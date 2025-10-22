"""
Business logic service for accounts.
"""
from decimal import Decimal
from typing import List, Optional

from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
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
        account_type: AccountType,
        account_subtype: AccountSubtype,
        initial_balance: str = "0.00",
        currency: str = "USD"
    ) -> Account:
        """
        Create a new account with validation.

        Args:
            name: Account name
            account_type: Primary account type (asset, liability, equity, income, expense)
            account_subtype: Account subtype (checking, savings, credit_card, etc.)
            initial_balance: Initial balance as string
            currency: Currency code (3 letters)

        Returns:
            Created account

        Raises:
            ValidationError: If validation fails
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

        # Create account object
        account = Account(
            id=None,
            name=validated_name,
            account_type=validated_type,
            account_subtype=validated_subtype,
            balance=validated_balance,
            normal_balance=normal_balance,
            currency=validated_currency
        )

        # Save account
        created_account = self.account_repo.create(account)
        logger.info(
            f"Account created: {created_account.name} "
            f"({created_account.account_type.value}/{created_account.account_subtype.value}, "
            f"ID: {created_account.id})"
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
