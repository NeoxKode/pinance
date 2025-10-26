"""
Business logic service for accounts.
"""
from decimal import Decimal
from typing import List, Optional, Tuple

from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance,
    JournalEntry, EntryType, Transaction, ReconciliationStatus
)
from finance_app.data.database import Database
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.transaction_repository import TransactionRepository
from finance_app.business.validators import AccountValidator
from finance_app.business.double_entry_service import DoubleEntryService
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import ValidationError, NotFoundError

logger = setup_logger(__name__)


class AccountService:
    """Service for account business logic."""

    def __init__(self, database: Database):
        """
        Initialize service.

        Args:
            database: Database instance
        """
        self.db = database
        self.account_repo = AccountRepository(database)
        self.transaction_repo = TransactionRepository(database)
        self.validator = AccountValidator()
        self.double_entry_service = DoubleEntryService(database)

    def create_account(
        self,
        name: str,
        account_type: AccountType,
        account_subtype: AccountSubtype,
        initial_balance: str = "0.00",
        currency: str = "USD",
        parent_account_id: Optional[int] = None,
        is_parent: bool = False
    ) -> Account:
        """
        Create a new account with validation.

        US-006: Added hierarchy support with parent_account_id and is_parent parameters.

        Args:
            name: Account name
            account_type: Primary account type (asset, liability, equity, income, expense)
            account_subtype: Account subtype (checking, savings, credit_card, etc.)
            initial_balance: Initial balance as string
            currency: Currency code (3 letters)
            parent_account_id: Optional ID of parent account (US-006)
            is_parent: Whether this is a parent/header account (US-006)

        Returns:
            Created account

        Raises:
            ValidationError: If validation fails
            NotFoundError: If parent account doesn't exist
        """
        # Validate inputs
        validated_name = self.validator.validate_name(name)
        validated_type, validated_subtype = self.validator.validate_account_type_combination(
            account_type, account_subtype
        )
        validated_currency = self.validator.validate_currency(currency)

        # Get normal balance based on account type
        normal_balance = self.validator.get_normal_balance(account_type)

        # Parse and validate balance
        try:
            balance = Decimal(initial_balance)
            # Allow negative balance for credit-type accounts
            validated_balance = self.validator.validate_balance(
                balance, allow_negative=(normal_balance == NormalBalance.CREDIT)
            )
        except Exception as e:
            raise ValidationError(f"Invalid initial balance: {initial_balance}") from e

        # US-006: Validate hierarchy parameters
        if parent_account_id is not None:
            # Check that parent exists
            parent_account = self.account_repo.get_by_id(parent_account_id)
            if not parent_account:
                raise NotFoundError(f"Parent account with ID {parent_account_id} not found")

            # Validate parent is actually a parent account
            if not parent_account.is_parent:
                raise ValidationError(
                    f"Account {parent_account.name} (ID: {parent_account_id}) is not a parent account. "
                    "Only parent accounts can have children."
                )

            # Validate type compatibility (child must have same account_type as parent)
            if parent_account.account_type != account_type:
                raise ValidationError(
                    f"Child account type ({account_type.value}) must match "
                    f"parent account type ({parent_account.account_type.value})"
                )

            # Validate maximum depth (5 levels = 0-4)
            if parent_account.hierarchy_level >= 4:
                raise ValidationError(
                    f"Maximum hierarchy depth is 5 levels. "
                    f"Parent account is already at level {parent_account.hierarchy_level}."
                )

            # Check for circular reference (should be impossible for new accounts, but validate anyway)
            if self._would_create_cycle(None, parent_account_id):
                raise ValidationError("Creating this account would create a circular reference")

        # US-006: Validate is_parent flag
        if is_parent and initial_balance != "0.00":
            logger.warning(
                f"Parent account {name} created with non-zero initial balance. "
                "Parent accounts should have zero balance (calculated from children)."
            )

        # Create account object
        account = Account(
            id=None,
            name=validated_name,
            account_type=validated_type,
            account_subtype=validated_subtype,
            balance=validated_balance,
            normal_balance=normal_balance,
            currency=validated_currency,
            parent_account_id=parent_account_id,  # US-006
            is_parent=is_parent  # US-006
        )

        # Save account (repository will calculate hierarchy_path)
        created_account = self.account_repo.create(account)
        logger.info(
            f"Account created: {created_account.name} "
            f"({created_account.account_type.value}/{created_account.account_subtype.value}, "
            f"ID: {created_account.id}, "
            f"parent: {parent_account_id or 'none'}, "
            f"is_parent: {is_parent})"
        )

        return created_account

    def update_account(
        self,
        account_id: int,
        name: Optional[str] = None,
        account_type: Optional[AccountType] = None,
        account_subtype: Optional[AccountSubtype] = None,
        currency: Optional[str] = None
    ) -> Account:
        """
        Update account details.

        Args:
            account_id: Account ID
            name: New name (optional)
            account_type: New account type (optional)
            account_subtype: New account subtype (optional)
            currency: New currency (optional)

        Returns:
            Updated account

        Raises:
            NotFoundError: If account doesn't exist
            ValidationError: If validation fails
        """
        # Get existing account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account with ID {account_id} not found")

        # Update fields if provided
        if name is not None:
            account.name = self.validator.validate_name(name)

        # If type or subtype is updated, validate the combination
        if account_type is not None or account_subtype is not None:
            new_type = account_type if account_type is not None else account.account_type
            new_subtype = account_subtype if account_subtype is not None else account.account_subtype

            validated_type, validated_subtype = self.validator.validate_account_type_combination(
                new_type, new_subtype
            )

            account.account_type = validated_type
            account.account_subtype = validated_subtype

            # Update normal balance if type changed
            if account_type is not None:
                account.normal_balance = self.validator.get_normal_balance(validated_type)

        if currency is not None:
            account.currency = self.validator.validate_currency(currency)

        # Save updates
        updated_account = self.account_repo.update(account)
        logger.info(f"Account updated: {updated_account.name} (ID: {updated_account.id})")

        return updated_account

    def delete_account(self, account_id: int) -> bool:
        """
        Delete an account.

        Args:
            account_id: Account ID

        Returns:
            True if deleted

        Raises:
            NotFoundError: If account doesn't exist
        """
        deleted = self.account_repo.delete(account_id)
        if not deleted:
            raise NotFoundError(f"Account with ID {account_id} not found")

        logger.info(f"Account deleted: ID {account_id}")
        return deleted

    def get_account(self, account_id: int) -> Optional[Account]:
        """
        Get account by ID.

        Args:
            account_id: Account ID

        Returns:
            Account or None
        """
        return self.account_repo.get_by_id(account_id)

    def get_all_accounts(self) -> List[Account]:
        """
        Get all accounts.

        Returns:
            List of accounts
        """
        return self.account_repo.get_all()

    def get_total_balance(self) -> Decimal:
        """
        Get total balance across all accounts.

        Returns:
            Total balance
        """
        return self.account_repo.get_total_balance()

    def get_account_balance(self, account_id: int) -> Decimal:
        """
        Get balance for specific account.

        Args:
            account_id: Account ID

        Returns:
            Account balance

        Raises:
            NotFoundError: If account doesn't exist
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account with ID {account_id} not found")

        return account.balance

    # ========================================================================
    # Opening Balance Methods (US-005)
    # ========================================================================

    def ensure_opening_balance_equity_account(self) -> Account:
        """
        Ensure Opening Balance Equity account exists.

        This account is used to balance opening balance journal entries,
        maintaining the accounting equation: Assets = Liabilities + Equity

        Returns:
            Opening Balance Equity account

        Example:
            >>> equity = service.ensure_opening_balance_equity_account()
            >>> print(equity.name)
            'Opening Balance Equity'
            >>> print(equity.account_type)
            AccountType.EQUITY
        """
        # Try to find existing account
        all_accounts = self.account_repo.get_all()
        for account in all_accounts:
            if (account.name == "Opening Balance Equity" and
                account.account_type == AccountType.EQUITY):
                logger.debug("Found existing Opening Balance Equity account")
                return account

        # Create new Opening Balance Equity account
        equity_account = self.create_account(
            name="Opening Balance Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubtype.OPENING_BALANCE,
            initial_balance="0.00",
            currency="USD"
        )
        logger.info("Created Opening Balance Equity account")

        return equity_account

    def create_account_with_opening_balance(
        self,
        name: str,
        account_type: AccountType,
        account_subtype: AccountSubtype,
        opening_balance: Decimal,
        opening_date: str,
        currency: str = "USD",
        **kwargs
    ) -> Tuple[Account, Optional[JournalEntry]]:
        """
        Create a new account with an opening balance.

        This method:
        1. Creates the account (starting at balance = 0)
        2. Creates a journal entry for the opening balance using DoubleEntryService
        3. Creates offsetting entry in Opening Balance Equity account (maintains equation)
        4. Updates account with opening_balance_date

        Args:
            name: Account name
            account_type: Account type (ASSET, LIABILITY, EQUITY, INCOME, EXPENSE)
            account_subtype: Account subtype
            opening_balance: Opening balance amount (positive for normal balance increase)
            opening_date: Date of opening balance (YYYY-MM-DD)
            currency: Currency code (default: USD)
            **kwargs: Additional account fields

        Returns:
            Tuple of (created_account, journal_entry or None)

        Raises:
            ValidationError: If opening_balance is invalid or account creation fails

        Example:
            >>> account, entry = service.create_account_with_opening_balance(
            ...     name="Checking Account",
            ...     account_type=AccountType.ASSET,
            ...     account_subtype=AccountSubtype.CHECKING,
            ...     opening_balance=Decimal("1000.00"),
            ...     opening_date="2025-01-01"
            ... )
            >>> print(account.balance)  # After trigger updates
            1000.00
            >>> print(entry.entry_type)
            EntryType.OPENING_BALANCE
        """
        # Validate opening balance is not negative
        if opening_balance < 0:
            raise ValidationError(
                f"Opening balance must be non-negative, got {opening_balance}"
            )

        logger.info(
            f"Creating account '{name}' with opening balance {opening_balance} on {opening_date}"
        )

        # NOTE: Individual repository operations handle their own transactions
        # 1. Create account with zero initial balance
        # (Journal entry will update the balance via database trigger)
        account = self.create_account(
            name=name,
            account_type=account_type,
            account_subtype=account_subtype,
            initial_balance="0.00",  # Start at 0, journal entry updates it
            currency=currency
        )

        logger.debug(f"Created account {account.name} (ID={account.id})")

        # 2. Handle zero opening balance case
        if opening_balance == Decimal("0"):
            logger.info(f"Zero opening balance for {account.name}, skipping journal entry")
            # Still update opening_balance_date to indicate it was explicitly set
            account.opening_balance_date = opening_date
            self.account_repo.update(account)
            return account, None

        # 3. Ensure Opening Balance Equity account exists
        equity_account = self.ensure_opening_balance_equity_account()

        # 4. ✅ USE DoubleEntryService - Let it handle debit/credit logic
        account_entry = self.double_entry_service.create_simple_transaction(
            account_id=account.id,
            amount=opening_balance,
            date=opening_date,
            description=f"Opening balance for {name}",
            entry_type=EntryType.OPENING_BALANCE
        )

        logger.debug(
            f"Created opening balance journal entry for {account.name}: "
            f"debit={account_entry.debit_amount}, credit={account_entry.credit_amount}"
        )

        # 5. ✅ CREATE EQUITY OFFSET (GAP 3 FIX)
        # This maintains the accounting equation: Assets = Liabilities + Equity
        # Use OPPOSITE SIGN to create offsetting entry
        # Example: Asset +$1000 (debit) → Equity -$1000 creates credit of $1000
        equity_entry = self.double_entry_service.create_simple_transaction(
            account_id=equity_account.id,
            amount=-opening_balance,  # Opposite sign to balance the equation
            date=opening_date,
            description=f"Opening balance offset for {name}",
            entry_type=EntryType.OPENING_BALANCE
        )

        logger.debug(
            f"Created equity offset entry: "
            f"debit={equity_entry.debit_amount}, credit={equity_entry.credit_amount}"
        )

        # 6. Create transaction record with is_opening_balance flag
        # This allows filtering opening balance transactions in UI
        # Note: type must be 'income' or 'expense' per CHECK constraint
        # For opening balances, we use 'income' for all account types since it's a one-time setup
        transaction = Transaction(
            id=None,
            account_id=account.id,
            date=opening_date,
            description=f"Opening balance for {name}",
            category="Opening Balance",
            amount=opening_balance,
            type="income",  # Opening balances are classified as income for transaction records
            is_opening_balance=True,  # ← NEW FIELD from Migration 006
            reconciliation_status=ReconciliationStatus.CLEARED  # Opening balances are pre-cleared
        )
        created_transaction = self.transaction_repo.create(transaction)

        logger.debug(f"Created transaction record (ID={created_transaction.id})")

        # 7. Update account with opening_balance_date
        # CRITICAL: Refresh account from database FIRST to get trigger-updated balance
        # The journal entry triggers updated the balance in the database, but our
        # in-memory account object still has the old balance=0.00. If we update
        # without refreshing, we'll overwrite the trigger-updated balance!
        account = self.account_repo.get_by_id(account.id)
        account.opening_balance_date = opening_date
        updated_account = self.account_repo.update(account)

        # 8. Verify accounting equation still holds
        # This is a sanity check to catch any bugs
        try:
            self.validate_opening_balance_equity()
        except ValidationError as e:
            logger.error(f"Accounting equation violated: {e}")
            raise ValidationError(
                "Accounting equation violated after creating opening balance. "
                "This should not happen - please report this bug."
            ) from e

        logger.info(
            f"Account created with opening balance: {updated_account.name} "
            f"balance={updated_account.balance}, opening_date={opening_date}"
        )

        return updated_account, account_entry

    def set_account_opening_balance(
        self,
        account_id: int,
        opening_balance: Decimal,
        opening_date: str
    ) -> JournalEntry:
        """
        Set opening balance for an existing account.

        This method:
        1. Validates the account exists and has no existing opening balance
        2. Creates journal entry for the opening balance
        3. Creates offsetting entry in Opening Balance Equity
        4. Updates account with opening_balance_date

        Args:
            account_id: Existing account ID
            opening_balance: Opening balance amount
            opening_date: Date of opening balance (YYYY-MM-DD)

        Returns:
            Created journal entry

        Raises:
            NotFoundError: If account doesn't exist
            ValidationError: If account already has opening balance

        Example:
            >>> entry = service.set_account_opening_balance(
            ...     account_id=5,
            ...     opening_balance=Decimal("2500.00"),
            ...     opening_date="2025-01-01"
            ... )
        """
        # 1. Get account and validate it exists
        account = self.account_repo.get_by_id(account_id)
        if account is None:
            raise NotFoundError(f"Account {account_id} not found")

        # 2. Check if account already has an opening balance
        if hasattr(account, 'opening_balance_date') and account.opening_balance_date is not None:
            raise ValidationError(
                f"Account '{account.name}' already has opening balance set on "
                f"{account.opening_balance_date}. Cannot set opening balance twice."
            )

        # Validate opening balance
        if opening_balance < 0:
            raise ValidationError(
                f"Opening balance must be non-negative, got {opening_balance}"
            )

        logger.info(
            f"Setting opening balance for account '{account.name}': "
            f"{opening_balance} on {opening_date}"
        )

        # NOTE: Individual repository operations handle their own transactions
        # Handle zero opening balance
        if opening_balance == Decimal("0"):
            account.opening_balance_date = opening_date
            self.account_repo.update(account)
            logger.info(f"Set zero opening balance for {account.name}")
            return None

        # Ensure Opening Balance Equity account exists
        equity_account = self.ensure_opening_balance_equity_account()

        # Create journal entry for account
        account_entry = self.double_entry_service.create_simple_transaction(
            account_id=account_id,
            amount=opening_balance,
            date=opening_date,
            description=f"Opening balance for {account.name}",
            entry_type=EntryType.OPENING_BALANCE
        )

        # Create offsetting entry in equity
        # Use OPPOSITE SIGN to create offsetting entry
        equity_entry = self.double_entry_service.create_simple_transaction(
            account_id=equity_account.id,
            amount=-opening_balance,  # Opposite sign to balance the equation
            date=opening_date,
            description=f"Opening balance offset for {account.name}",
            entry_type=EntryType.OPENING_BALANCE
        )

        # Create transaction record
        # Note: type must be 'income' or 'expense' per CHECK constraint
        # For opening balances, we use 'income' for all account types since it's a one-time setup
        transaction = Transaction(
            id=None,
            account_id=account_id,
            date=opening_date,
            description=f"Opening balance for {account.name}",
            category="Opening Balance",
            amount=opening_balance,
            type="income",  # Opening balances are classified as income for transaction records
            is_opening_balance=True,
            reconciliation_status=ReconciliationStatus.CLEARED
        )
        self.transaction_repo.create(transaction)

        # Update account with opening balance date
        # CRITICAL: Refresh account from database FIRST to get trigger-updated balance
        account = self.account_repo.get_by_id(account_id)
        account.opening_balance_date = opening_date
        self.account_repo.update(account)

        # Validate accounting equation
        self.validate_opening_balance_equity()

        logger.info(
            f"Set opening balance for {account.name}: {opening_balance} on {opening_date}"
        )

        return account_entry

    def validate_opening_balance_equity(
        self,
        tolerance: Decimal = Decimal("0.01")
    ) -> bool:
        """
        Validate the accounting equation: Assets = Liabilities + Equity

        This method uses SQL aggregation for performance, rather than
        fetching all accounts and iterating in Python.

        Args:
            tolerance: Allowable difference (default: 1 cent)

        Returns:
            True if equation balances within tolerance

        Raises:
            ValidationError: If equation doesn't balance

        Example:
            >>> is_valid = service.validate_opening_balance_equity()
            >>> print(is_valid)
            True
        """
        # Use SQL aggregation to calculate totals by account type
        # This is much faster than fetching all accounts and iterating
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Get total for each account type with proper sign handling
            query = """
                SELECT
                    account_type,
                    SUM(balance) as total_balance
                FROM accounts
                WHERE account_type IN ('asset', 'liability', 'equity')
                GROUP BY account_type
            """
            cursor.execute(query)
            results = cursor.fetchall()

        # Build dictionary of balances by type
        balances = {
            'asset': Decimal("0.00"),
            'liability': Decimal("0.00"),
            'equity': Decimal("0.00")
        }

        for row in results:
            account_type = row[0]
            total_balance = Decimal(str(row[1]))
            balances[account_type] = total_balance

        # Calculate accounting equation: Assets = Liabilities + Equity
        # In standard accounting, liabilities and equity have credit normal balance
        # but our balances are stored as positive numbers
        left_side = balances['asset']  # Assets
        right_side = balances['liability'] + balances['equity']  # Liabilities + Equity

        difference = abs(left_side - right_side)

        logger.debug(
            f"Accounting equation check: "
            f"Assets={left_side}, "
            f"Liabilities={balances['liability']}, "
            f"Equity={balances['equity']}, "
            f"Difference={difference}"
        )

        if difference > tolerance:
            error_msg = (
                f"Accounting equation does not balance: "
                f"Assets ({left_side}) != Liabilities ({balances['liability']}) + "
                f"Equity ({balances['equity']}) "
                f"[Difference: {difference}, Tolerance: {tolerance}]"
            )
            logger.error(error_msg)
            raise ValidationError(error_msg)

        logger.debug(f"Accounting equation balanced (difference: {difference})")
        return True

    def get_opening_balance_summary(self) -> dict:
        """
        Get summary of all opening balances.

        Returns:
            Dictionary with:
            - total_accounts: Number of accounts with opening balances
            - total_amount: Sum of all opening balances
            - by_type: Breakdown by account type
            - accounts: List of accounts with opening balances

        Example:
            >>> summary = service.get_opening_balance_summary()
            >>> print(summary['total_accounts'])
            5
            >>> print(summary['total_amount'])
            Decimal('15250.00')
        """
        # Get all accounts
        all_accounts = self.account_repo.get_all()

        # Filter accounts with opening balance dates
        accounts_with_opening = [
            acc for acc in all_accounts
            if hasattr(acc, 'opening_balance_date') and acc.opening_balance_date is not None
        ]

        # Calculate totals
        total_amount = sum(
            acc.balance for acc in accounts_with_opening
        )

        # Group by account type
        by_type = {}
        for acc in accounts_with_opening:
            type_name = acc.account_type.value
            if type_name not in by_type:
                by_type[type_name] = {
                    'count': 0,
                    'total': Decimal("0.00"),
                    'accounts': []
                }

            by_type[type_name]['count'] += 1
            by_type[type_name]['total'] += acc.balance
            by_type[type_name]['accounts'].append({
                'id': acc.id,
                'name': acc.name,
                'balance': acc.balance,
                'opening_date': acc.opening_balance_date
            })

        return {
            'total_accounts': len(accounts_with_opening),
            'total_amount': total_amount,
            'by_type': by_type,
            'accounts': accounts_with_opening
        }

    # ========================================================================
    # US-006: Account Hierarchy Methods
    # ========================================================================

    def get_parent_account_balance(self, parent_id: int) -> Decimal:
        """
        Calculate parent account balance by summing all leaf descendant accounts (Python version).

        US-006: This is the Python implementation that loads accounts into memory.
        For better performance, use get_parent_account_balance_sql() in production.

        Args:
            parent_id: ID of the parent account

        Returns:
            Sum of all leaf descendant account balances

        Raises:
            NotFoundError: If parent account doesn't exist
        """
        # Get the parent account
        parent = self.account_repo.get_by_id(parent_id)
        if not parent:
            raise NotFoundError(f"Parent account with ID {parent_id} not found")

        # Get all descendants
        descendants = self.account_repo.get_descendant_accounts(parent_id)

        # Sum balances of leaf accounts only (is_parent=False)
        total = Decimal("0.00")
        for account in descendants:
            if not account.is_parent:  # Only leaf accounts contribute to balance
                total += account.balance

        logger.debug(
            f"Parent account {parent_id} balance calculated: {total} "
            f"(from {len([a for a in descendants if not a.is_parent])} leaf accounts)"
        )

        return total

    def get_parent_account_balance_sql(self, parent_id: int) -> Decimal:
        """
        Calculate parent account balance using SQL aggregation (10x faster).

        US-006: This is the optimized version for production use.
        Uses a single SQL query with hierarchy_path pattern matching.

        Args:
            parent_id: ID of the parent account

        Returns:
            Sum of all leaf descendant account balances

        Raises:
            NotFoundError: If parent account doesn't exist
        """
        # Get the parent account
        parent = self.account_repo.get_by_id(parent_id)
        if not parent:
            raise NotFoundError(f"Parent account with ID {parent_id} not found")

        if not parent.hierarchy_path:
            logger.warning(f"Parent account {parent_id} has no hierarchy_path set")
            return Decimal("0.00")

        # Use SQL aggregation for efficient calculation
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Query: Sum balance of all leaf descendants
            # hierarchy_path LIKE '/1/%' matches all descendants of account 1
            # is_parent = 0 ensures only leaf accounts are summed
            pattern = f"{parent.hierarchy_path}/%"

            cursor.execute("""
                SELECT SUM(balance)
                FROM accounts
                WHERE hierarchy_path LIKE ?
                  AND is_parent = 0
            """, (pattern,))

            result = cursor.fetchone()[0]
            total = Decimal(str(result)) if result else Decimal("0.00")

            logger.debug(f"Parent account {parent_id} balance (SQL): {total}")

            return total

    def _would_create_cycle(self, account_id: Optional[int], new_parent_id: int) -> bool:
        """
        Check if setting new_parent_id would create a circular reference.

        US-006: Walks up the parent chain to detect cycles.

        Args:
            account_id: ID of the account being moved (None for new accounts)
            new_parent_id: Proposed new parent ID

        Returns:
            True if cycle would be created, False otherwise
        """
        if account_id is None:
            # New account can't create a cycle
            return False

        if account_id == new_parent_id:
            # Account cannot be its own parent
            return True

        # Walk up the parent chain from new_parent_id
        # If we encounter account_id, we have a cycle
        current_id = new_parent_id
        visited = set()

        while current_id is not None:
            if current_id in visited:
                # Infinite loop detected in existing data
                logger.error(f"Circular reference detected in existing data starting from {current_id}")
                return True

            if current_id == account_id:
                # Found the account we're trying to move - this would create a cycle
                return True

            visited.add(current_id)

            # Get parent of current account
            current_account = self.account_repo.get_by_id(current_id)
            if not current_account:
                break

            current_id = current_account.parent_account_id

        return False

    def move_account(
        self,
        account_id: int,
        new_parent_id: Optional[int]
    ) -> Account:
        """
        Move an account to a new parent (or make it top-level).

        US-006: This operation updates the account's parent_account_id and recalculates
        hierarchy paths for the account and all its descendants.

        Args:
            account_id: ID of the account to move
            new_parent_id: ID of new parent account (None to make top-level)

        Returns:
            Updated account

        Raises:
            NotFoundError: If account or parent doesn't exist
            ValidationError: If move would violate hierarchy rules
        """
        # Get the account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account with ID {account_id} not found")

        # Validate new parent if provided
        if new_parent_id is not None:
            new_parent = self.account_repo.get_by_id(new_parent_id)
            if not new_parent:
                raise NotFoundError(f"Parent account with ID {new_parent_id} not found")

            # Validate parent is a parent account
            if not new_parent.is_parent:
                raise ValidationError(
                    f"Account {new_parent.name} (ID: {new_parent_id}) is not a parent account"
                )

            # Validate type compatibility
            if new_parent.account_type != account.account_type:
                raise ValidationError(
                    f"Cannot move account: type mismatch "
                    f"({account.account_type.value} != {new_parent.account_type.value})"
                )

            # Check for circular reference
            if self._would_create_cycle(account_id, new_parent_id):
                raise ValidationError(
                    "Cannot move account: would create circular reference"
                )

            # Validate maximum depth
            if new_parent.hierarchy_level >= 4:
                raise ValidationError(
                    f"Cannot move account: maximum depth exceeded "
                    f"(parent at level {new_parent.hierarchy_level})"
                )

        # Update parent_account_id
        account.parent_account_id = new_parent_id

        # Update account (repository will recalculate hierarchy paths)
        updated_account = self.account_repo.update(account)

        logger.info(
            f"Moved account {account.name} (ID: {account_id}) "
            f"to parent {new_parent_id or 'none'}"
        )

        return updated_account

    def convert_to_parent_account(self, account_id: int) -> Account:
        """
        Convert an account to a parent/header account.

        US-006: Sets is_parent=True and validates that the account has no transactions.
        Parent accounts cannot have direct transactions.

        Args:
            account_id: ID of the account to convert

        Returns:
            Updated account

        Raises:
            NotFoundError: If account doesn't exist
            ValidationError: If account has transactions
        """
        # Get the account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account with ID {account_id} not found")

        # Check if account already a parent
        if account.is_parent:
            logger.info(f"Account {account.name} is already a parent account")
            return account

        # Validate account has no transactions
        transactions = self.transaction_repo.get_all(account_id=account_id)
        if transactions:
            raise ValidationError(
                f"Cannot convert to parent account: {account.name} has {len(transactions)} transactions. "
                "Parent accounts cannot have direct transactions."
            )

        # Convert to parent
        account.is_parent = True

        # US-006 Gap Fix: Nested parents ARE allowed
        # Don't modify parent_account_id - preserve existing hierarchy

        # Update account
        updated_account = self.account_repo.update(account)

        logger.info(f"Converted account {account.name} (ID: {account_id}) to parent account")

        return updated_account

    def delete_account_with_children(
        self,
        account_id: int,
        force: bool = False
    ) -> bool:
        """
        Delete an account and optionally its children.

        US-006: If force=True, recursively deletes all descendants.
        If force=False, only deletes if account has no children.

        Args:
            account_id: ID of the account to delete
            force: If True, delete children recursively

        Returns:
            True if deleted

        Raises:
            NotFoundError: If account doesn't exist
            ValidationError: If account has children and force=False
        """
        # Get the account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account with ID {account_id} not found")

        # Get children
        children = self.account_repo.get_child_accounts(account_id)

        # Check if has children
        if children and not force:
            raise ValidationError(
                f"Cannot delete account {account.name}: has {len(children)} child accounts. "
                "Use force=True to delete all descendants."
            )

        # Delete children recursively if force=True
        if children and force:
            logger.info(f"Recursively deleting {len(children)} child accounts")
            for child in children:
                self.delete_account_with_children(child.id, force=True)

        # Delete the account
        success = self.account_repo.delete(account_id)

        logger.info(f"Deleted account {account.name} (ID: {account_id})")

        return success
