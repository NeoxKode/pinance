"""
Business logic service for account reconciliation.

Story: US-004 - Account Reconciliation (Day 2)

This service handles:
- Starting reconciliation sessions
- Marking transactions as cleared/uncleared
- Calculating balances and discrepancies
- Completing reconciliations
- Retrieving reconciliation history
"""
from decimal import Decimal
from typing import List, Dict, Optional
from datetime import datetime, date

from finance_app.data.models import (
    Reconciliation, Transaction, Account, ReconciliationStatus
)
from finance_app.data.database import Database
from finance_app.data.repositories.reconciliation_repository import ReconciliationRepository
from finance_app.data.repositories.transaction_repository import TransactionRepository
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import ValidationError, NotFoundError, BusinessRuleError

logger = setup_logger(__name__)


class ReconciliationService:
    """
    Service for account reconciliation operations.

    This service handles the complete reconciliation workflow:
    1. Start reconciliation (check for pending, get opening balance)
    2. Get unreconciled transactions
    3. Mark/unmark transactions as cleared
    4. Calculate cleared balance and discrepancy
    5. Complete reconciliation (save record, update account)
    6. Get reconciliation history

    Critical Fix from Tech Review:
    - Concurrency prevention via pending reconciliation check
    """

    def __init__(self, database: Database):
        """
        Initialize service with database and repositories.

        Args:
            database: Database instance
        """
        self.db = database
        self.reconciliation_repo = ReconciliationRepository(database)
        self.transaction_repo = TransactionRepository(database)
        self.account_repo = AccountRepository(database)

    def start_reconciliation(
        self,
        account_id: int,
        statement_date: str,
        statement_balance: Decimal
    ) -> Dict:
        """
        Start a reconciliation session for an account.

        CRITICAL FIX from Tech Review:
        This checks for pending reconciliations to prevent concurrent reconciliations.

        Args:
            account_id: Account ID to reconcile
            statement_date: Date of bank statement (ISO 8601: YYYY-MM-DD)
            statement_balance: Ending balance on bank statement

        Returns:
            Dictionary with reconciliation session info:
            {
                'account_id': int,
                'account_name': str,
                'statement_date': str,
                'statement_balance': Decimal,
                'opening_balance': Decimal,
                'unreconciled_count': int,
                'last_reconciliation_date': Optional[str]
            }

        Raises:
            NotFoundError: If account doesn't exist
            ValidationError: If statement_date or statement_balance invalid
            BusinessRuleError: If reconciliation already in progress
        """
        # Validate account exists
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account {account_id} not found")

        # Validate statement_date
        if not statement_date:
            raise ValidationError("Statement date is required")

        try:
            # Verify date format
            datetime.strptime(statement_date, '%Y-%m-%d')
        except ValueError:
            raise ValidationError(f"Invalid statement date format: {statement_date} (expected YYYY-MM-DD)")

        # Validate statement_balance
        if not isinstance(statement_balance, Decimal):
            try:
                statement_balance = Decimal(str(statement_balance))
            except:
                raise ValidationError(f"Invalid statement balance: {statement_balance}")

        # CRITICAL: Check for pending reconciliation (concurrency prevention)
        has_pending = self.reconciliation_repo.get_pending_reconciliation(account_id)
        if has_pending:
            raise BusinessRuleError(
                f"Reconciliation already in progress for account '{account.name}'. "
                f"Please complete or cancel the current reconciliation before starting a new one."
            )

        # Get last reconciliation to determine opening balance
        last_reconciliation = self.reconciliation_repo.get_last_reconciliation(account_id)
        opening_balance = last_reconciliation.cleared_balance if last_reconciliation else Decimal('0.00')

        # Get count of unreconciled transactions
        unreconciled_transactions = self.get_unreconciled_transactions(account_id)
        unreconciled_count = len(unreconciled_transactions)

        logger.info(
            f"Started reconciliation for account {account_id} ({account.name}): "
            f"statement_date={statement_date}, statement_balance={statement_balance}, "
            f"opening_balance={opening_balance}, unreconciled_count={unreconciled_count}"
        )

        return {
            'account_id': account_id,
            'account_name': account.name,
            'statement_date': statement_date,
            'statement_balance': statement_balance,
            'opening_balance': opening_balance,
            'unreconciled_count': unreconciled_count,
            'last_reconciliation_date': account.last_reconciled_date
        }

    def get_unreconciled_transactions(self, account_id: int) -> List[Transaction]:
        """
        Get all unreconciled transactions for an account.

        Returns transactions with reconciliation_status='unreconciled',
        ordered by date ascending (oldest first).

        Args:
            account_id: Account ID

        Returns:
            List of unreconciled Transaction objects (oldest first)

        Raises:
            NotFoundError: If account doesn't exist
        """
        # Validate account exists
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account {account_id} not found")

        # Query transactions with reconciliation_status='unreconciled'
        # Note: TransactionRepository.get_all() accepts account_id parameter
        all_transactions = self.transaction_repo.get_all(account_id=account_id)

        # Filter for unreconciled only
        unreconciled = [
            txn for txn in all_transactions
            if txn.reconciliation_status == ReconciliationStatus.UNRECONCILED
        ]

        # Sort by date ascending (oldest first)
        unreconciled.sort(key=lambda t: t.date)

        logger.debug(f"Found {len(unreconciled)} unreconciled transactions for account {account_id}")

        return unreconciled

    def mark_transaction_cleared(
        self,
        transaction_id: int,
        statement_date: str
    ) -> Transaction:
        """
        Mark a transaction as cleared (reconciled).

        Updates:
        - reconciliation_status = 'cleared'
        - reconciled_date = current date
        - statement_date = provided statement date

        Args:
            transaction_id: Transaction ID to mark as cleared
            statement_date: Date of bank statement (ISO 8601: YYYY-MM-DD)

        Returns:
            Updated Transaction object

        Raises:
            NotFoundError: If transaction doesn't exist
            ValidationError: If statement_date invalid
        """
        # Validate transaction exists
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction {transaction_id} not found")

        # Validate statement_date
        if not statement_date:
            raise ValidationError("Statement date is required")

        try:
            datetime.strptime(statement_date, '%Y-%m-%d')
        except ValueError:
            raise ValidationError(f"Invalid statement date format: {statement_date}")

        # Update transaction reconciliation fields
        transaction.reconciliation_status = ReconciliationStatus.CLEARED
        transaction.reconciled_date = datetime.now().strftime('%Y-%m-%d')
        transaction.statement_date = statement_date

        # Save to database
        self.transaction_repo.update(transaction)

        logger.info(
            f"Marked transaction {transaction_id} as cleared: "
            f"statement_date={statement_date}, amount={transaction.amount}"
        )

        return transaction

    def unmark_transaction(self, transaction_id: int) -> Transaction:
        """
        Unmark a transaction (return to unreconciled status).

        Updates:
        - reconciliation_status = 'unreconciled'
        - reconciled_date = None
        - statement_date = None

        Args:
            transaction_id: Transaction ID to unmark

        Returns:
            Updated Transaction object

        Raises:
            NotFoundError: If transaction doesn't exist
        """
        # Validate transaction exists
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction {transaction_id} not found")

        # Update transaction reconciliation fields
        transaction.reconciliation_status = ReconciliationStatus.UNRECONCILED
        transaction.reconciled_date = None
        transaction.statement_date = None

        # Save to database
        self.transaction_repo.update(transaction)

        logger.info(f"Unmarked transaction {transaction_id} (returned to unreconciled)")

        return transaction

    def calculate_cleared_balance(self, account_id: int) -> Decimal:
        """
        Calculate the cleared balance for an account.

        Cleared balance = opening_balance + sum(cleared transactions)

        Args:
            account_id: Account ID

        Returns:
            Decimal cleared balance

        Raises:
            NotFoundError: If account doesn't exist
        """
        # Validate account exists
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account {account_id} not found")

        # Get opening balance from last reconciliation
        last_reconciliation = self.reconciliation_repo.get_last_reconciliation(account_id)
        opening_balance = last_reconciliation.cleared_balance if last_reconciliation else Decimal('0.00')

        # Get all transactions for account
        all_transactions = self.transaction_repo.get_all(account_id=account_id)

        # Sum only cleared transactions
        cleared_sum = Decimal('0.00')
        for txn in all_transactions:
            if txn.reconciliation_status == ReconciliationStatus.CLEARED:
                cleared_sum += txn.amount

        cleared_balance = opening_balance + cleared_sum

        logger.debug(
            f"Calculated cleared balance for account {account_id}: "
            f"opening={opening_balance}, cleared_sum={cleared_sum}, "
            f"cleared_balance={cleared_balance}"
        )

        return cleared_balance

    def calculate_discrepancy(
        self,
        account_id: int,
        statement_balance: Decimal
    ) -> Decimal:
        """
        Calculate discrepancy between statement balance and cleared balance.

        discrepancy = statement_balance - cleared_balance

        Interpretation:
        - Positive discrepancy: Missing transactions in app (need to add)
        - Negative discrepancy: Extra transactions in app (remove or bank error)
        - Zero discrepancy: Perfect reconciliation ✓

        Args:
            account_id: Account ID
            statement_balance: Ending balance from bank statement

        Returns:
            Decimal discrepancy amount

        Raises:
            NotFoundError: If account doesn't exist
        """
        cleared_balance = self.calculate_cleared_balance(account_id)
        discrepancy = statement_balance - cleared_balance

        logger.debug(
            f"Calculated discrepancy for account {account_id}: "
            f"statement={statement_balance}, cleared={cleared_balance}, "
            f"discrepancy={discrepancy}"
        )

        return discrepancy

    def complete_reconciliation(
        self,
        account_id: int,
        statement_date: str,
        statement_balance: Decimal,
        notes: Optional[str] = None
    ) -> Reconciliation:
        """
        Complete reconciliation and save the record.

        This method:
        1. Calculates cleared balance and discrepancy
        2. Counts cleared transactions
        3. Creates reconciliation record
        4. Updates account.last_reconciled_date
        5. Returns saved reconciliation

        Args:
            account_id: Account ID
            statement_date: Date of bank statement
            statement_balance: Ending balance on statement
            notes: Optional notes (explain discrepancy if exists)

        Returns:
            Created Reconciliation object

        Raises:
            NotFoundError: If account doesn't exist
            ValidationError: If data invalid
        """
        # Validate account exists
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account {account_id} not found")

        # Calculate balances
        cleared_balance = self.calculate_cleared_balance(account_id)
        discrepancy = self.calculate_discrepancy(account_id, statement_balance)

        # Count cleared transactions
        all_transactions = self.transaction_repo.get_all(account_id=account_id)
        cleared_count = sum(
            1 for txn in all_transactions
            if txn.reconciliation_status == ReconciliationStatus.CLEARED
        )

        # Get current date for reconciliation_date
        reconciliation_date = datetime.now().strftime('%Y-%m-%d')

        # Create reconciliation record
        reconciliation = Reconciliation(
            id=None,
            account_id=account_id,
            reconciliation_date=reconciliation_date,
            statement_date=statement_date,
            statement_balance=statement_balance,
            cleared_balance=cleared_balance,
            discrepancy=discrepancy,
            transaction_count=cleared_count,
            notes=notes
        )

        # Save reconciliation
        saved_reconciliation = self.reconciliation_repo.create(reconciliation)

        # Update account last_reconciled_date
        account.last_reconciled_date = reconciliation_date
        self.account_repo.update(account)

        # Log completion
        status = "BALANCED" if abs(discrepancy) < Decimal('0.01') else f"DISCREPANCY: ${discrepancy}"
        logger.info(
            f"Completed reconciliation {saved_reconciliation.id} for account {account_id} ({account.name}): "
            f"{status}, {cleared_count} transactions cleared"
        )

        return saved_reconciliation

    def get_reconciliation_history(
        self,
        account_id: int,
        limit: Optional[int] = 10
    ) -> List[Reconciliation]:
        """
        Get reconciliation history for an account.

        Returns reconciliations ordered by date DESC (newest first).

        Args:
            account_id: Account ID
            limit: Maximum number of reconciliations to return (default: 10)

        Returns:
            List of Reconciliation objects (newest first)

        Raises:
            NotFoundError: If account doesn't exist
        """
        # Validate account exists
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account {account_id} not found")

        # Get reconciliation history
        history = self.reconciliation_repo.get_by_account(account_id, limit=limit)

        logger.debug(f"Retrieved {len(history)} reconciliations for account {account_id}")

        return history

