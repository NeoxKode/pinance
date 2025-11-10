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
    def validate_amount(amount_str: str, currency: str = 'USD') -> Decimal:
        """
        Validate and convert amount string to Decimal with currency-aware precision.

        US-008: Multi-Currency Support - Now validates decimal places based on currency.

        Args:
            amount_str: Amount as string
            currency: ISO 4217 currency code (default: USD)

        Returns:
            Amount as Decimal

        Raises:
            ValidationError: If amount is invalid or exceeds currency precision

        Examples:
            >>> TransactionValidator.validate_amount('1234.56', 'USD')
            Decimal('1234.56')
            >>> TransactionValidator.validate_amount('1234.56', 'JPY')
            ValidationError: JPY cannot have more than 0 decimal places
        """
        try:
            amount = Decimal(amount_str.strip())
        except (InvalidOperation, ValueError, AttributeError) as e:
            raise ValidationError(f"Invalid amount format: {amount_str}") from e

        if amount == 0:
            raise ValidationError("Amount cannot be zero")

        if abs(amount) > Decimal("999999999.99"):
            raise ValidationError("Amount exceeds maximum allowed value")

        # US-008: Currency-aware decimal validation
        # Get decimal precision for the currency (0 for JPY/KRW, 2 for USD/EUR, etc.)
        decimals = AccountValidator.get_decimal_places(currency)

        if amount.as_tuple().exponent < -decimals:
            raise ValidationError(
                f"{currency} cannot have more than {decimals} decimal place{'s' if decimals != 1 else ''}. "
                f"Got: {amount_str}"
            )

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

    # US-008: Multi-Currency Support (Sprint 12)
    # Supported ISO 4217 currency codes with metadata
    SUPPORTED_CURRENCIES = {
        'AED': {'name': 'UAE Dirham', 'symbol': 'د.إ', 'decimals': 2},
        'ARS': {'name': 'Argentine Peso', 'symbol': '$', 'decimals': 2},
        'AUD': {'name': 'Australian Dollar', 'symbol': '$', 'decimals': 2},
        'BDT': {'name': 'Bangladeshi Taka', 'symbol': '৳', 'decimals': 2},
        'BRL': {'name': 'Brazilian Real', 'symbol': 'R$', 'decimals': 2},
        'CAD': {'name': 'Canadian Dollar', 'symbol': '$', 'decimals': 2},
        'CHF': {'name': 'Swiss Franc', 'symbol': 'Fr', 'decimals': 2},
        'CLP': {'name': 'Chilean Peso', 'symbol': '$', 'decimals': 0},
        'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'decimals': 2},
        'COP': {'name': 'Colombian Peso', 'symbol': '$', 'decimals': 2},
        'CZK': {'name': 'Czech Koruna', 'symbol': 'Kč', 'decimals': 2},
        'DKK': {'name': 'Danish Krone', 'symbol': 'kr', 'decimals': 2},
        'EGP': {'name': 'Egyptian Pound', 'symbol': '£', 'decimals': 2},
        'EUR': {'name': 'Euro', 'symbol': '€', 'decimals': 2},
        'GBP': {'name': 'British Pound', 'symbol': '£', 'decimals': 2},
        'HKD': {'name': 'Hong Kong Dollar', 'symbol': '$', 'decimals': 2},
        'HUF': {'name': 'Hungarian Forint', 'symbol': 'Ft', 'decimals': 2},
        'IDR': {'name': 'Indonesian Rupiah', 'symbol': 'Rp', 'decimals': 2},
        'ILS': {'name': 'Israeli Shekel', 'symbol': '₪', 'decimals': 2},
        'INR': {'name': 'Indian Rupee', 'symbol': '₹', 'decimals': 2},
        'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'decimals': 0},
        'KRW': {'name': 'South Korean Won', 'symbol': '₩', 'decimals': 0},
        'MXN': {'name': 'Mexican Peso', 'symbol': '$', 'decimals': 2},
        'MYR': {'name': 'Malaysian Ringgit', 'symbol': 'RM', 'decimals': 2},
        'NGN': {'name': 'Nigerian Naira', 'symbol': '₦', 'decimals': 2},
        'NOK': {'name': 'Norwegian Krone', 'symbol': 'kr', 'decimals': 2},
        'NZD': {'name': 'New Zealand Dollar', 'symbol': '$', 'decimals': 2},
        'PHP': {'name': 'Philippine Peso', 'symbol': '₱', 'decimals': 2},
        'PKR': {'name': 'Pakistani Rupee', 'symbol': '₨', 'decimals': 2},
        'PLN': {'name': 'Polish Zloty', 'symbol': 'zł', 'decimals': 2},
        'RON': {'name': 'Romanian Leu', 'symbol': 'lei', 'decimals': 2},
        'RUB': {'name': 'Russian Ruble', 'symbol': '₽', 'decimals': 2},
        'SAR': {'name': 'Saudi Riyal', 'symbol': '﷼', 'decimals': 2},
        'SEK': {'name': 'Swedish Krona', 'symbol': 'kr', 'decimals': 2},
        'SGD': {'name': 'Singapore Dollar', 'symbol': '$', 'decimals': 2},
        'THB': {'name': 'Thai Baht', 'symbol': '฿', 'decimals': 2},
        'TRY': {'name': 'Turkish Lira', 'symbol': '₺', 'decimals': 2},
        'TWD': {'name': 'Taiwan Dollar', 'symbol': 'NT$', 'decimals': 2},
        'UAH': {'name': 'Ukrainian Hryvnia', 'symbol': '₴', 'decimals': 2},
        'USD': {'name': 'US Dollar', 'symbol': '$', 'decimals': 2},
        'VND': {'name': 'Vietnamese Dong', 'symbol': '₫', 'decimals': 0},
        'ZAR': {'name': 'South African Rand', 'symbol': 'R', 'decimals': 2},
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

    @classmethod
    def validate_currency(cls, currency: str) -> str:
        """
        Validate currency code against ISO 4217 supported currencies.

        US-008: Multi-Currency Support

        Args:
            currency: Currency code (e.g., 'USD', 'EUR', 'JPY')

        Returns:
            Normalized currency code (uppercase, stripped)

        Raises:
            ValidationError: If currency invalid or unsupported

        Examples:
            >>> AccountValidator.validate_currency('usd')
            'USD'
            >>> AccountValidator.validate_currency('XXX')
            ValidationError: Currency 'XXX' not supported
        """
        if not currency:
            raise ValidationError("Currency code is required")

        currency = currency.upper().strip()

        if len(currency) != 3:
            raise ValidationError(
                f"Currency code must be 3 letters (ISO 4217). Got: '{currency}'"
            )

        if not currency.isalpha():
            raise ValidationError(
                f"Currency code must contain only letters. Got: '{currency}'"
            )

        if currency not in cls.SUPPORTED_CURRENCIES:
            supported = ', '.join(sorted(cls.SUPPORTED_CURRENCIES.keys()))
            raise ValidationError(
                f"Currency '{currency}' not supported. "
                f"Supported currencies: {supported}"
            )

        return currency

    @classmethod
    def get_currency_symbol(cls, currency: str) -> str:
        """
        Get currency symbol for display.

        US-008: Multi-Currency Support

        Args:
            currency: ISO 4217 currency code

        Returns:
            Currency symbol (e.g., '$', '€', '¥')

        Examples:
            >>> AccountValidator.get_currency_symbol('USD')
            '$'
            >>> AccountValidator.get_currency_symbol('EUR')
            '€'
        """
        return cls.SUPPORTED_CURRENCIES.get(currency, {}).get(
            'symbol', currency
        )

    @classmethod
    def get_decimal_places(cls, currency: str) -> int:
        """
        Get number of decimal places for currency.

        US-008: Multi-Currency Support

        Args:
            currency: ISO 4217 currency code

        Returns:
            Number of decimal places (0 for JPY/KRW/CLP/VND, 2 for most others)

        Examples:
            >>> AccountValidator.get_decimal_places('USD')
            2
            >>> AccountValidator.get_decimal_places('JPY')
            0
        """
        return cls.SUPPORTED_CURRENCIES.get(currency, {}).get(
            'decimals', 2
        )

    @classmethod
    def format_amount(cls, amount: Decimal, currency: str) -> str:
        """
        Format amount with currency symbol and correct decimal places.

        US-008: Multi-Currency Support

        Args:
            amount: Amount to format
            currency: ISO 4217 currency code

        Returns:
            Formatted string (e.g., '$1,234.56', '¥1,235')

        Examples:
            >>> AccountValidator.format_amount(Decimal('1234.56'), 'USD')
            '$1,234.56'
            >>> AccountValidator.format_amount(Decimal('1234.56'), 'JPY')
            '¥1,235'
        """
        symbol = cls.get_currency_symbol(currency)
        decimals = cls.get_decimal_places(currency)

        if decimals == 0:
            # Round to integer for zero-decimal currencies
            return f"{symbol}{amount:,.0f}"
        else:
            return f"{symbol}{amount:,.{decimals}f}"

    @classmethod
    def get_currency_info(cls, currency: str) -> dict:
        """
        Get complete currency information.

        US-008: Multi-Currency Support

        Args:
            currency: ISO 4217 currency code

        Returns:
            Dict with name, symbol, decimals

        Example:
            >>> AccountValidator.get_currency_info('USD')
            {'name': 'US Dollar', 'symbol': '$', 'decimals': 2}
        """
        return cls.SUPPORTED_CURRENCIES.get(currency, {
            'name': currency,
            'symbol': currency,
            'decimals': 2
        })


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
