"""
Business logic service for transactions.

Updated for US-002A: Now creates journal entries for double-entry accounting.
Updated for US-012: Added date range filtering with preset support.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional

from finance_app.data.models import Transaction, EntryType
from finance_app.business.date_range_utils import DateRange
from finance_app.data.database import Database
from finance_app.data.repositories.transaction_repository import TransactionRepository
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.business.validators import TransactionValidator
from finance_app.business.double_entry_service import DoubleEntryService
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
        self.double_entry_service = DoubleEntryService(database)  # US-002A

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

        # US-006: Validate parent accounts cannot have transactions
        if account.is_parent:
            raise ValidationError(
                f"Cannot create transaction for parent account '{account.name}'. "
                "Parent/header accounts cannot have direct transactions. "
                "Post transactions to child accounts instead."
            )

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

        # US-002A: Create journal entry for double-entry accounting
        # This will automatically update the account balance via database triggers
        try:
            journal_entry = self.double_entry_service.create_simple_transaction(
                account_id=account_id,
                amount=validated_amount,
                date=validated_date,
                description=validated_description,
                entry_type=EntryType.TRANSACTION,
                transaction_id=created_transaction.id,
                reference_number=None,
                notes=f"Category: {validated_category}"
            )
            logger.info(
                f"Transaction created with journal entry: txn={created_transaction.id}, "
                f"journal={journal_entry.id}, amount={validated_amount}"
            )
        except Exception as e:
            # Rollback transaction if journal entry creation fails
            self.transaction_repo.delete(created_transaction.id)
            logger.error(f"Failed to create journal entry, transaction rolled back: {e}")
            raise BusinessRuleError(f"Failed to create journal entry: {e}") from e

        return created_transaction

    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Delete a transaction and revert balance.

        US-002A: Journal entries are automatically deleted via CASCADE,
        and the database triggers automatically revert the balance.

        Args:
            transaction_id: Transaction ID

        Returns:
            True if deleted

        Raises:
            NotFoundError: If transaction doesn't exist
        """
        # Get transaction to verify it exists
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction with ID {transaction_id} not found")

        # Delete transaction
        # US-002A: This will CASCADE delete the journal entry,
        # which will trigger the balance update automatically
        deleted = self.transaction_repo.delete(transaction_id)

        if deleted:
            logger.info(
                f"Transaction deleted (journal entry cascade deleted, "
                f"balance auto-reverted): {transaction_id}"
            )

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

    def search_transactions(
        self,
        keyword: str,
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Search transactions by description keyword.

        US-011: Basic Text Search - Enables users to find transactions quickly
        by searching for keywords in descriptions.

        Args:
            keyword: Search keyword (will be trimmed, empty returns empty list)
            account_id: Optional account ID filter

        Returns:
            List of matching transactions, empty list if no matches or empty keyword

        Business Rules:
            - Empty/whitespace keyword returns empty list (not all transactions)
            - Keyword trimmed for consistency
            - Minimum length: 1 character (after trim)
            - Case-insensitive search

        Examples:
            >>> service.search_transactions("Starbucks")
            [Transaction(...), ...]

            >>> service.search_transactions("  ")  # Empty after trim
            []

        Raises:
            DatabaseError: If database query fails
        """
        # Trim and validate keyword
        keyword_trimmed = keyword.strip()

        # Business rule: Empty keyword returns empty list (not all transactions)
        if not keyword_trimmed:
            logger.debug("Empty search keyword, returning empty list")
            return []

        # Call repository method
        logger.info(f"Searching transactions for keyword: '{keyword_trimmed}' (account_id: {account_id})")
        return self.transaction_repo.search_by_description(keyword_trimmed, account_id)

    def filter_by_date_range(
        self,
        from_date: date,
        to_date: date,
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Filter transactions by date range using date objects.

        US-012: Date Range Filter - Service layer method with validation.
        Accepts date objects for type safety and validates the range before
        delegating to repository.

        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)
            account_id: Optional account ID filter

        Returns:
            List of Transaction objects within date range, sorted by date DESC

        Raises:
            ValueError: If from_date > to_date

        Business Rules:
            - from_date must be <= to_date
            - Both dates are inclusive
            - Results sorted by date DESC, then id DESC

        Examples:
            >>> from datetime import date
            >>> service.filter_by_date_range(date(2025, 1, 1), date(2025, 12, 31))
            [Transaction(...), ...]

            >>> service.filter_by_date_range(date(2025, 3, 1), date(2025, 2, 1))
            ValueError: From date (2025-03-01) must be <= To date (2025-02-01)
        """
        # Validate date range
        DateRange.validate_custom_range(from_date, to_date)

        # Call repository method
        logger.info(f"Filtering transactions from {from_date} to {to_date} (account_id: {account_id})")
        return self.transaction_repo.filter_by_date_range(from_date, to_date, account_id)

    def filter_by_preset(
        self,
        preset: str,
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Filter transactions by preset date range.

        US-012: Date Range Filter - Provides convenient preset filtering
        (Today, Yesterday, Last 7/30 Days, This/Last Month/Quarter/Year, All Time).

        Args:
            preset: Preset name (case-insensitive). Options:
                - "today", "yesterday"
                - "last_7_days", "last_30_days"
                - "this_month", "last_month"
                - "this_quarter", "last_quarter"
                - "this_year", "last_year"
                - "all_time"
            account_id: Optional account ID filter

        Returns:
            List of Transaction objects for the preset range

        Raises:
            ValueError: If preset name is invalid

        Examples:
            >>> service.filter_by_preset("last_month")
            [Transaction(...), ...]

            >>> service.filter_by_preset("this_quarter", account_id=1)
            [Transaction(...), ...]

            >>> service.filter_by_preset("invalid_preset")
            ValueError: Invalid preset: invalid_preset
        """
        # Normalize preset name
        preset_lower = preset.lower().strip()

        # Map presets to DateRange methods
        preset_methods = {
            "today": DateRange.get_today,
            "yesterday": DateRange.get_yesterday,
            "last_7_days": DateRange.get_last_7_days,
            "last_30_days": DateRange.get_last_30_days,
            "this_month": DateRange.get_this_month,
            "last_month": DateRange.get_last_month,
            "this_quarter": DateRange.get_this_quarter,
            "last_quarter": DateRange.get_last_quarter,
            "this_year": DateRange.get_this_year,
            "last_year": DateRange.get_last_year,
            "all_time": DateRange.get_all_time,
        }

        # Validate preset
        if preset_lower not in preset_methods:
            valid_presets = ", ".join(sorted(preset_methods.keys()))
            raise ValueError(
                f"Invalid preset: {preset}. Valid options: {valid_presets}"
            )

        # Get date range from preset
        from_date, to_date = preset_methods[preset_lower]()

        # Call filter_by_date_range (reuse validation logic)
        logger.info(f"Filtering transactions by preset '{preset_lower}': {from_date} to {to_date}")
        return self.filter_by_date_range(from_date, to_date, account_id)

    def get_categories_with_counts(self, account_id: Optional[int] = None) -> List[tuple]:
        """
        Get all categories with transaction counts.

        US-013: Category Filter - Provides category list for filter dropdown
        with transaction counts for each category.

        Args:
            account_id: Optional account filter (only count transactions in this account)

        Returns:
            List of (category, count) tuples sorted alphabetically by category name
            Example: [('Dining Out', 45), ('Groceries', 123), ('Transportation', 67)]

        Raises:
            No exceptions raised (wraps repository exceptions)

        Examples:
            >>> service.get_categories_with_counts()
            [('Dining Out', 45), ('Groceries', 123), ('Transportation', 67)]

            >>> service.get_categories_with_counts(account_id=5)
            [('Groceries', 23), ('Transportation', 12)]
        """
        logger.debug(f"Getting categories with counts (account_id={account_id})")
        return self.transaction_repo.get_categories_with_counts(account_id=account_id)

    def filter_by_categories(
        self,
        categories: List[str],
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Filter transactions by category list with validation.

        US-013: Category Filter - Enables filtering transactions by one or more
        category names with input validation and sanitization.

        Args:
            categories: List of category names to filter
            account_id: Optional account ID filter

        Returns:
            List of matching transactions, sorted by date DESC

        Raises:
            ValueError: If categories is None or not a list

        Examples:
            >>> service.filter_by_categories(['Groceries'])
            [Transaction(...), Transaction(...)]

            >>> service.filter_by_categories(['Groceries', 'Dining Out'])
            [Transaction(...), Transaction(...), ...]

            >>> service.filter_by_categories([], account_id=5)
            []  # Empty list returns no results

            >>> service.filter_by_categories(None)
            ValueError: Categories cannot be None
        """
        # Validation
        if categories is None:
            logger.error("Attempted to filter by categories with None value")
            raise ValueError("Categories cannot be None")

        if not isinstance(categories, list):
            logger.error(f"Invalid categories type: {type(categories)}")
            raise ValueError(f"Categories must be a list, got {type(categories).__name__}")

        # Sanitization: Filter out empty/whitespace-only strings
        sanitized_categories = [cat.strip() for cat in categories if cat and isinstance(cat, str) and cat.strip()]

        if not sanitized_categories:
            logger.debug("No valid categories after sanitization, returning empty list")
            return []  # No valid categories = no results

        logger.info(f"Filtering transactions by {len(sanitized_categories)} categories: {sanitized_categories[:3]}{'...' if len(sanitized_categories) > 3 else ''}")

        return self.transaction_repo.filter_by_categories(
            categories=sanitized_categories,
            account_id=account_id
        )

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
