"""
Business logic service for double-entry accounting.

Story: US-002A - Journal Entry Foundation
"""
from decimal import Decimal
from typing import Tuple, Optional
from datetime import datetime

from finance_app.data.models import (
    JournalEntry, EntryType, Account, AccountType, NormalBalance
)
from finance_app.data.database import Database
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import ValidationError, NotFoundError

logger = setup_logger(__name__)


class DoubleEntryService:
    """
    Service for double-entry accounting operations.

    This service handles the creation of journal entries and ensures
    proper debit/credit logic based on account types.
    """

    def __init__(self, database: Database):
        """
        Initialize service.

        Args:
            database: Database instance
        """
        self.db = database
        self.journal_repo = JournalEntryRepository(database)
        self.account_repo = AccountRepository(database)

    def create_simple_transaction(
        self,
        account_id: int,
        amount: Decimal,
        date: str,
        description: str,
        entry_type: EntryType = EntryType.TRANSACTION,
        transaction_id: Optional[int] = None,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None
    ) -> JournalEntry:
        """
        Create a simple single-entry journal transaction.

        This determines whether the entry should be a debit or credit based on:
        1. The account's normal balance (debit or credit)
        2. Whether the amount increases or decreases the account

        Debit/Credit Logic:
        - Asset/Expense accounts (normal balance = DEBIT):
          - Positive amount → Debit (increases account)
          - Negative amount → Credit (decreases account)

        - Liability/Equity/Income accounts (normal balance = CREDIT):
          - Positive amount → Credit (increases account)
          - Negative amount → Debit (decreases account)

        Args:
            account_id: Account to post to
            amount: Transaction amount (positive = increase, negative = decrease)
            date: Transaction date (YYYY-MM-DD)
            description: Entry description
            entry_type: Type of entry (default: TRANSACTION)
            transaction_id: Optional link to transactions table
            reference_number: Optional reference (check number, invoice, etc.)
            notes: Optional notes

        Returns:
            Created journal entry

        Raises:
            NotFoundError: If account doesn't exist
            ValidationError: If amount is zero or invalid

        Example:
            # Deposit $100 to checking (asset account):
            # Positive amount to asset = DEBIT
            service.create_simple_transaction(
                account_id=1,
                amount=Decimal("100.00"),  # Debit checking
                date="2025-10-22",
                description="Deposit"
            )

            # Pay $50 expense from checking (asset account):
            # Negative amount to asset = CREDIT
            service.create_simple_transaction(
                account_id=1,
                amount=Decimal("-50.00"),  # Credit checking
                date="2025-10-22",
                description="Expense payment"
            )
        """
        # Validate amount
        if amount == Decimal("0"):
            raise ValidationError("Transaction amount cannot be zero")

        # Get account to determine normal balance
        account = self.account_repo.get_by_id(account_id)
        if account is None:
            raise NotFoundError(f"Account {account_id} not found")

        # Determine debit/credit based on normal balance and amount sign
        debit_amount, credit_amount = self._calculate_debit_credit(
            amount, account.normal_balance
        )

        logger.info(
            f"Creating journal entry for account {account_id} ({account.name}): "
            f"amount={amount}, debit={debit_amount}, credit={credit_amount}"
        )

        # Create journal entry
        entry = JournalEntry(
            id=None,
            transaction_id=transaction_id,
            group_id=None,  # Single entries don't have groups (US-002B)
            account_id=account_id,
            entry_date=date,
            description=description,
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            balance_after=Decimal("0"),  # Will be calculated by repository
            entry_type=entry_type,
            reference_number=reference_number,
            notes=notes
        )

        # Repository will calculate balance_after and triggers will update account balance
        created_entry = self.journal_repo.create(entry)

        logger.info(
            f"Journal entry created: ID={created_entry.id}, "
            f"balance_after={created_entry.balance_after}"
        )

        return created_entry

    def _calculate_debit_credit(
        self,
        amount: Decimal,
        normal_balance: NormalBalance
    ) -> Tuple[Decimal, Decimal]:
        """
        Calculate debit and credit amounts based on amount sign and normal balance.

        Args:
            amount: Signed amount (positive = increase, negative = decrease)
            normal_balance: Account's normal balance type

        Returns:
            Tuple of (debit_amount, credit_amount)

        Logic:
            DEBIT normal balance (Asset, Expense):
              - Positive amount → DEBIT (increase)
              - Negative amount → CREDIT (decrease)

            CREDIT normal balance (Liability, Equity, Income):
              - Positive amount → CREDIT (increase)
              - Negative amount → DEBIT (decrease)
        """
        abs_amount = abs(amount)

        if normal_balance == NormalBalance.DEBIT:
            # Asset/Expense accounts: increase with debit, decrease with credit
            if amount > 0:
                return (abs_amount, Decimal("0"))  # Debit
            else:
                return (Decimal("0"), abs_amount)  # Credit
        else:
            # Liability/Equity/Income: increase with credit, decrease with debit
            if amount > 0:
                return (Decimal("0"), abs_amount)  # Credit
            else:
                return (abs_amount, Decimal("0"))  # Debit

    def validate_account_balance(
        self,
        account_id: int,
        tolerance: Decimal = Decimal("0.01")
    ) -> bool:
        """
        Validate that account's cached balance matches journal entry sum.

        This is a reconciliation check to ensure data integrity.

        Args:
            account_id: Account to validate
            tolerance: Allowable difference (default: 1 cent)

        Returns:
            True if balance is correct within tolerance

        Raises:
            NotFoundError: If account doesn't exist
            ValidationError: If balance doesn't match
        """
        # Get account
        account = self.account_repo.get_by_id(account_id)
        if account is None:
            raise NotFoundError(f"Account {account_id} not found")

        # Get calculated balance from journal entries
        calculated_balance = self.journal_repo.get_account_balance(account_id)

        # Compare with cached balance
        difference = abs(account.balance - calculated_balance)

        if difference > tolerance:
            error_msg = (
                f"Balance mismatch for account {account_id} ({account.name}): "
                f"cached={account.balance}, calculated={calculated_balance}, "
                f"difference={difference}"
            )
            logger.error(error_msg)
            raise ValidationError(error_msg)

        logger.debug(
            f"Balance validated for account {account_id}: "
            f"{account.balance} (difference: {difference})"
        )

        return True

    def get_account_balance(
        self,
        account_id: int,
        as_of_date: Optional[str] = None
    ) -> Decimal:
        """
        Get account balance from journal entries.

        This is the authoritative balance calculation.

        Args:
            account_id: Account ID
            as_of_date: Optional date to get balance as of (YYYY-MM-DD)

        Returns:
            Account balance

        Raises:
            NotFoundError: If account doesn't exist
        """
        # Verify account exists
        account = self.account_repo.get_by_id(account_id)
        if account is None:
            raise NotFoundError(f"Account {account_id} not found")

        return self.journal_repo.get_account_balance(account_id, as_of_date)

    def get_journal_entries(
        self,
        account_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list[JournalEntry]:
        """
        Get journal entries for an account.

        Args:
            account_id: Account ID
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            limit: Optional limit on number of results

        Returns:
            List of journal entries ordered by date DESC

        Raises:
            NotFoundError: If account doesn't exist
        """
        # Verify account exists
        account = self.account_repo.get_by_id(account_id)
        if account is None:
            raise NotFoundError(f"Account {account_id} not found")

        return self.journal_repo.get_by_account(
            account_id, start_date, end_date, limit
        )
