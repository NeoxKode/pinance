"""
Validation utilities for business logic.
"""
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Optional

from finance_app.utils.exceptions import ValidationError


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
    """Validator for account data."""

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

    @staticmethod
    def validate_account_type(account_type: str) -> str:
        """
        Validate account type.

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
