"""
Business logic service for accounts.
"""
from decimal import Decimal
from typing import List, Optional

from finance_app.data.models import Account
from finance_app.data.database import Database
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.business.validators import AccountValidator
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
        self.validator = AccountValidator()

    def create_account(
        self,
        name: str,
        account_type: str,
        initial_balance: str = "0.00",
        currency: str = "USD"
    ) -> Account:
        """
        Create a new account with validation.

        Args:
            name: Account name
            account_type: Account type (bank, cash, credit, investment)
            initial_balance: Initial balance as string
            currency: Currency code (3 letters)

        Returns:
            Created account

        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        validated_name = self.validator.validate_name(name)
        validated_type = self.validator.validate_account_type(account_type)
        validated_currency = self.validator.validate_currency(currency)

        # Parse and validate balance
        try:
            balance = Decimal(initial_balance)
            validated_balance = self.validator.validate_balance(balance, allow_negative=True)
        except Exception as e:
            raise ValidationError(f"Invalid initial balance: {initial_balance}") from e

        # Create account object
        account = Account(
            id=None,
            name=validated_name,
            type=validated_type,
            balance=validated_balance,
            currency=validated_currency
        )

        # Save account
        created_account = self.account_repo.create(account)
        logger.info(f"Account created: {created_account.name} (ID: {created_account.id})")

        return created_account

    def update_account(
        self,
        account_id: int,
        name: Optional[str] = None,
        account_type: Optional[str] = None,
        currency: Optional[str] = None
    ) -> Account:
        """
        Update account details.

        Args:
            account_id: Account ID
            name: New name (optional)
            account_type: New type (optional)
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

        if account_type is not None:
            account.type = self.validator.validate_account_type(account_type)

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
