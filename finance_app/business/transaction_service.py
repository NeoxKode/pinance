"""
Business logic service for transactions.
"""
from decimal import Decimal
from typing import List, Optional

from finance_app.data.models import Transaction
from finance_app.data.database import Database
from finance_app.data.repositories.transaction_repository import TransactionRepository
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.business.validators import TransactionValidator
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import ValidationError, BusinessRuleError, NotFoundError

logger = setup_logger(__name__)


class TransactionService:
    """Service for transaction business logic."""

    def __init__(self, database: Database):
        """
        Initialize service.

        Args:
            database: Database instance
        """
        self.db = database
        self.transaction_repo = TransactionRepository(database)
        self.account_repo = AccountRepository(database)
        self.validator = TransactionValidator()

    def create_transaction(
        self,
        account_id: int,
        date: str,
        description: str,
        category: str,
        amount: str,
        trans_type: str
    ) -> Transaction:
        """
        Create a new transaction with validation and balance update.

        Args:
            account_id: Account ID
            date: Transaction date (YYYY-MM-DD)
            description: Transaction description
            category: Transaction category
            amount: Amount as string
            trans_type: Transaction type ('income' or 'expense')

        Returns:
            Created transaction

        Raises:
            ValidationError: If validation fails
            BusinessRuleError: If business rules are violated
            NotFoundError: If account doesn't exist
        """
        # Validate account exists
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account with ID {account_id} not found")

        # Validate inputs
        validated_amount = self.validator.validate_amount(amount)
        validated_description = self.validator.validate_description(description)
        validated_date = self.validator.validate_date(date)
        validated_category = self.validator.validate_category(category)
        validated_type = self.validator.validate_transaction_type(trans_type)

        # Ensure amount sign matches type
        if validated_type == 'expense' and validated_amount > 0:
            validated_amount = -validated_amount
        elif validated_type == 'income' and validated_amount < 0:
            validated_amount = abs(validated_amount)

        # Create transaction object
        transaction = Transaction(
            id=None,
            account_id=account_id,
            date=validated_date,
            description=validated_description,
            category=validated_category,
            amount=validated_amount,
            type=validated_type
        )

        # Save transaction
        created_transaction = self.transaction_repo.create(transaction)

        # Update account balance
        try:
            self.account_repo.update_balance(account_id, validated_amount)
            logger.info(
                f"Transaction created and balance updated: {created_transaction.id} "
                f"({validated_amount} for account {account_id})"
            )
        except Exception as e:
            # Rollback transaction if balance update fails
            self.transaction_repo.delete(created_transaction.id)
            logger.error(f"Failed to update balance, transaction rolled back: {e}")
            raise BusinessRuleError(f"Failed to update account balance: {e}") from e

        return created_transaction

    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Delete a transaction and revert balance.

        Args:
            transaction_id: Transaction ID

        Returns:
            True if deleted

        Raises:
            NotFoundError: If transaction doesn't exist
            BusinessRuleError: If balance update fails
        """
        # Get transaction to revert balance
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction with ID {transaction_id} not found")

        # Delete transaction
        deleted = self.transaction_repo.delete(transaction_id)

        if deleted:
            # Revert balance (subtract the transaction amount)
            try:
                self.account_repo.update_balance(transaction.account_id, -transaction.amount)
                logger.info(f"Transaction deleted and balance reverted: {transaction_id}")
            except Exception as e:
                logger.error(f"Failed to revert balance after deletion: {e}")
                # Note: Transaction is already deleted, this is a data inconsistency issue
                raise BusinessRuleError(
                    f"Transaction deleted but failed to revert balance: {e}"
                ) from e

        return deleted

    def get_all_transactions(
        self,
        account_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """
        Get all transactions, optionally filtered.

        Args:
            account_id: Filter by account ID
            limit: Maximum number of transactions

        Returns:
            List of transactions
        """
        return self.transaction_repo.get_all(account_id, limit)

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """
        Get transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction or None
        """
        return self.transaction_repo.get_by_id(transaction_id)

    def get_transactions_by_category(
        self,
        category: str,
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Get transactions by category.

        Args:
            category: Category name
            account_id: Optional account filter

        Returns:
            List of transactions
        """
        return self.transaction_repo.get_by_category(category, account_id)

    def get_transactions_by_date_range(
        self,
        start_date: str,
        end_date: str,
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Get transactions in date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            account_id: Optional account filter

        Returns:
            List of transactions
        """
        # Validate dates
        self.validator.validate_date(start_date)
        self.validator.validate_date(end_date)

        return self.transaction_repo.get_by_date_range(start_date, end_date, account_id)

    def calculate_total(
        self,
        transactions: List[Transaction],
        trans_type: Optional[str] = None
    ) -> Decimal:
        """
        Calculate total amount from transactions.

        Args:
            transactions: List of transactions
            trans_type: Filter by type ('income' or 'expense')

        Returns:
            Total amount
        """
        if trans_type:
            filtered = [t for t in transactions if t.type == trans_type]
        else:
            filtered = transactions

        return sum((t.amount for t in filtered), Decimal('0.0'))
