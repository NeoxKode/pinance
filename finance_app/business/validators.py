"""
Validation utilities for business logic.
"""
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Optional, Tuple

from finance_app.utils.exceptions import ValidationError
from finance_app.data.models import AccountType, AccountSubtype, NormalBalance


class TransactionValidator:
    """Validator for transaction data."""

    @staticmethod
    def validate_amount(amount_str: str) -> Decimal:
        """
        Validate and convert amount string to Decimal.

        Args:
            amount_str: Amount as string

        Returns:
            Amount as Decimal

        Raises:
            ValidationError: If amount is invalid
        """
        try:
            amount = Decimal(amount_str.strip())
        except (InvalidOperation, ValueError, AttributeError) as e:
            raise ValidationError(f"Invalid amount format: {amount_str}") from e

        if amount == 0:
            raise ValidationError("Amount cannot be zero")

        if abs(amount) > Decimal("999999999.99"):
            raise ValidationError("Amount exceeds maximum allowed value")

        # Ensure 2 decimal places max
        if amount.as_tuple().exponent < -2:
            raise ValidationError("Amount cannot have more than 2 decimal places")

        return amount

    @staticmethod
    def validate_description(description: str, max_length: int = 200) -> str:
        """
        Validate transaction description.

        Args:
            description: Description text
            max_length: Maximum allowed length

        Returns:
            Cleaned description

        Raises:
            ValidationError: If description is invalid
        """
        if not description or not description.strip():
            raise ValidationError("Description is required")

        cleaned = description.strip()

        if len(cleaned) > max_length:
            raise ValidationError(f"Description exceeds maximum length of {max_length} characters")

        return cleaned

    @staticmethod
    def validate_date(date_str: str) -> str:
        """
        Validate date format (YYYY-MM-DD).

        Args:
            date_str: Date string

        Returns:
            Validated date string

        Raises:
            ValidationError: If date format is invalid
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError as e:
            raise ValidationError(f"Invalid date format. Expected YYYY-MM-DD, got: {date_str}") from e

    @staticmethod
    def validate_category(category: str) -> str:
        """
        Validate category name.

        Args:
            category: Category name

        Returns:
            Validated category

        Raises:
            ValidationError: If category is invalid
        """
        if not category or not category.strip():
            raise ValidationError("Category is required")

        return category.strip()

    @staticmethod
    def validate_transaction_type(trans_type: str) -> str:
        """
        Validate transaction type.

        Args:
            trans_type: Transaction type

        Returns:
            Validated type ('income' or 'expense')

        Raises:
            ValidationError: If type is invalid
        """
        normalized = trans_type.lower().strip()
        if normalized not in ('income', 'expense'):
            raise ValidationError(f"Invalid transaction type: {trans_type}. Must be 'income' or 'expense'")
        return normalized


class AccountValidator:
    """Validator for account data with double-entry support."""

    # Valid subtype combinations for each account type
    VALID_SUBTYPES = {
        AccountType.ASSET: [
            AccountSubtype.CHECKING,
            AccountSubtype.SAVINGS,
            AccountSubtype.CASH,
            AccountSubtype.INVESTMENT,
            AccountSubtype.OTHER_ASSET,
        ],
        AccountType.LIABILITY: [
            AccountSubtype.CREDIT_CARD,
            AccountSubtype.LOAN,
            AccountSubtype.MORTGAGE,
            AccountSubtype.LINE_OF_CREDIT,
            AccountSubtype.OTHER_LIABILITY,
        ],
        AccountType.EQUITY: [
            AccountSubtype.OPENING_BALANCE,
            AccountSubtype.RETAINED_EARNINGS,
        ],
        AccountType.INCOME: [
            AccountSubtype.SALARY,
            AccountSubtype.BUSINESS_INCOME,
            AccountSubtype.INTEREST,
            AccountSubtype.DIVIDENDS,
            AccountSubtype.OTHER_INCOME,
        ],
        AccountType.EXPENSE: [
            AccountSubtype.EXPENSE_CATEGORY,
        ],
    }

    # Normal balance by account type (double-entry accounting rules)
    NORMAL_BALANCE_MAP = {
        AccountType.ASSET: NormalBalance.DEBIT,
        AccountType.EXPENSE: NormalBalance.DEBIT,
        AccountType.LIABILITY: NormalBalance.CREDIT,
        AccountType.EQUITY: NormalBalance.CREDIT,
        AccountType.INCOME: NormalBalance.CREDIT,
    }

    @staticmethod
    def validate_name(name: str, max_length: int = 100) -> str:
        """
        Validate account name.

        Args:
            name: Account name
            max_length: Maximum allowed length

        Returns:
            Cleaned name

        Raises:
            ValidationError: If name is invalid
        """
        if not name or not name.strip():
            raise ValidationError("Account name is required")

        cleaned = name.strip()

        if len(cleaned) > max_length:
            raise ValidationError(f"Account name exceeds maximum length of {max_length} characters")

        return cleaned

    @classmethod
    def validate_account_type_combination(
        cls,
        account_type: AccountType,
        account_subtype: AccountSubtype
    ) -> Tuple[AccountType, AccountSubtype]:
        """
        Validate account type and subtype combination.

        Args:
            account_type: Primary account type
            account_subtype: Account subtype

        Returns:
            Validated (account_type, account_subtype) tuple

        Raises:
            ValidationError: If combination is invalid
        """
        # Convert string to enum if needed
        if isinstance(account_type, str):
            try:
                account_type = AccountType(account_type)
            except ValueError:
                raise ValidationError(
                    f"Invalid account type: {account_type}. "
                    f"Valid types: {', '.join([t.value for t in AccountType])}"
                )

        if isinstance(account_subtype, str):
            try:
                account_subtype = AccountSubtype(account_subtype)
            except ValueError:
                raise ValidationError(
                    f"Invalid account subtype: {account_subtype}. "
                    f"Valid subtypes: {', '.join([s.value for s in AccountSubtype])}"
                )

        # Validate combination
        if account_subtype not in cls.VALID_SUBTYPES.get(account_type, []):
            valid_subtypes = ', '.join(
                [s.value for s in cls.VALID_SUBTYPES[account_type]]
            )
            raise ValidationError(
                f"Invalid subtype '{account_subtype.value}' for account type "
                f"'{account_type.value}'. Valid subtypes: {valid_subtypes}"
            )

        return account_type, account_subtype

    @classmethod
    def get_normal_balance(cls, account_type: AccountType) -> NormalBalance:
        """
        Get normal balance for account type.

        Args:
            account_type: Account type

        Returns:
            Normal balance (debit or credit)

        Raises:
            ValidationError: If account type is invalid
        """
        if isinstance(account_type, str):
            try:
                account_type = AccountType(account_type)
            except ValueError:
                raise ValidationError(f"Invalid account type: {account_type}")

        return cls.NORMAL_BALANCE_MAP[account_type]

    @staticmethod
    def validate_account_type(account_type: str) -> str:
        """
        Validate legacy account type (for backward compatibility).

        Args:
            account_type: Account type

        Returns:
            Validated type

        Raises:
            ValidationError: If type is invalid
        """
        valid_types = ('bank', 'cash', 'credit', 'investment')
        normalized = account_type.lower().strip()

        if normalized not in valid_types:
            raise ValidationError(
                f"Invalid account type: {account_type}. Must be one of: {', '.join(valid_types)}"
            )

        return normalized

    @staticmethod
    def validate_balance(balance: Decimal, allow_negative: bool = False) -> Decimal:
        """
        Validate account balance.

        Args:
            balance: Balance amount
            allow_negative: Whether negative balances are allowed

        Returns:
            Validated balance

        Raises:
            ValidationError: If balance is invalid
        """
        if not allow_negative and balance < 0:
            raise ValidationError("Account balance cannot be negative")

        if abs(balance) > Decimal("999999999.99"):
            raise ValidationError("Balance exceeds maximum allowed value")

        return balance

    @staticmethod
    def validate_currency(currency: str) -> str:
        """
        Validate currency code.

        Args:
            currency: Currency code (3 letters)

        Returns:
            Validated currency code

        Raises:
            ValidationError: If currency is invalid
        """
        cleaned = currency.upper().strip()

        if len(cleaned) != 3:
            raise ValidationError("Currency code must be 3 characters (e.g., USD, EUR, GBP)")

        if not cleaned.isalpha():
            raise ValidationError("Currency code must contain only letters")

        return cleaned


class CategoryValidator:
    """Validator for category data."""

    @staticmethod
    def validate_name(name: str, max_length: int = 50) -> str:
        """
        Validate category name.

        Args:
            name: Category name
            max_length: Maximum allowed length

        Returns:
            Cleaned name

        Raises:
            ValidationError: If name is invalid
        """
        if not name or not name.strip():
            raise ValidationError("Category name is required")

        cleaned = name.strip()

        if len(cleaned) > max_length:
            raise ValidationError(f"Category name exceeds maximum length of {max_length} characters")

        return cleaned

    @staticmethod
    def validate_type(category_type: str) -> str:
        """
        Validate category type.

        Args:
            category_type: Category type

        Returns:
            Validated type ('income' or 'expense')

        Raises:
            ValidationError: If type is invalid
        """
        normalized = category_type.lower().strip()
        if normalized not in ('income', 'expense'):
            raise ValidationError(
                f"Invalid category type: {category_type}. Must be 'income' or 'expense'"
            )
        return normalized
