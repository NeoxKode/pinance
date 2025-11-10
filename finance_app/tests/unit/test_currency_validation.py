"""
Unit tests for US-008: Multi-Currency Validation.

Tests currency validation, formatting, and currency-aware amount validation.
Covers AccountValidator and TransactionValidator currency methods.

Test Coverage:
- TestCurrencyValidation: 11 tests (currency code validation)
- TestCurrencyFormatting: 7 tests (display formatting with symbols)
- TestCurrencyAwareAmountValidation: 5 tests (decimal precision per currency)

Total: 23 unit tests

Created: 2025-11-10
Story: US-008 - Multi-Currency Account Setup
"""
import pytest
from decimal import Decimal
from finance_app.business.validators import AccountValidator, TransactionValidator
from finance_app.utils.exceptions import ValidationError


class TestCurrencyValidation:
    """Unit tests for currency validation (AC4)."""

    def test_validate_currency_valid_uppercase(self):
        """Test valid currency code (uppercase)."""
        currency = AccountValidator.validate_currency('USD')
        assert currency == 'USD'

    def test_validate_currency_valid_lowercase(self):
        """Test valid currency code (converts to uppercase)."""
        currency = AccountValidator.validate_currency('usd')
        assert currency == 'USD'

    def test_validate_currency_with_whitespace(self):
        """Test currency code with whitespace (strips)."""
        currency = AccountValidator.validate_currency(' EUR ')
        assert currency == 'EUR'

    def test_validate_currency_invalid_too_short(self):
        """Test invalid currency (too short)."""
        with pytest.raises(ValidationError, match="3 letters"):
            AccountValidator.validate_currency('US')

    def test_validate_currency_invalid_too_long(self):
        """Test invalid currency (too long)."""
        with pytest.raises(ValidationError, match="3 letters"):
            AccountValidator.validate_currency('USDA')

    def test_validate_currency_invalid_unsupported(self):
        """Test unsupported currency code."""
        with pytest.raises(ValidationError, match="not supported"):
            AccountValidator.validate_currency('XXX')

    def test_validate_currency_invalid_numbers(self):
        """Test currency code with numbers."""
        with pytest.raises(ValidationError, match="only letters"):
            AccountValidator.validate_currency('U5D')

    def test_validate_currency_invalid_special_chars(self):
        """Test currency code with special characters."""
        with pytest.raises(ValidationError, match="only letters"):
            AccountValidator.validate_currency('U$D')

    def test_validate_currency_empty_string(self):
        """Test empty currency string."""
        with pytest.raises(ValidationError, match="required"):
            AccountValidator.validate_currency('')

    def test_validate_currency_none(self):
        """Test None currency."""
        with pytest.raises(ValidationError, match="required"):
            AccountValidator.validate_currency(None)

    def test_all_42_currencies_valid(self):
        """Test all 42 supported currencies validate correctly."""
        expected_count = 42
        actual_count = len(AccountValidator.SUPPORTED_CURRENCIES)
        assert actual_count == expected_count, f"Expected {expected_count} currencies, got {actual_count}"

        for code in AccountValidator.SUPPORTED_CURRENCIES.keys():
            result = AccountValidator.validate_currency(code)
            assert result == code, f"Currency {code} did not validate correctly"


class TestCurrencyFormatting:
    """Unit tests for currency formatting (AC2)."""

    def test_format_amount_usd_two_decimals(self):
        """Test USD formatting with 2 decimals."""
        formatted = AccountValidator.format_amount(Decimal('1234.56'), 'USD')
        assert formatted == '$1,234.56'

    def test_format_amount_eur_two_decimals(self):
        """Test EUR formatting with 2 decimals."""
        formatted = AccountValidator.format_amount(Decimal('1234.56'), 'EUR')
        assert formatted == '€1,234.56'

    def test_format_amount_jpy_zero_decimals(self):
        """Test JPY formatting with 0 decimals (rounds)."""
        formatted = AccountValidator.format_amount(Decimal('1234.56'), 'JPY')
        assert formatted == '¥1,235'

    def test_format_amount_krw_zero_decimals(self):
        """Test KRW formatting with 0 decimals."""
        formatted = AccountValidator.format_amount(Decimal('5000.00'), 'KRW')
        assert formatted == '₩5,000'

    def test_get_currency_symbol(self):
        """Test currency symbol retrieval."""
        assert AccountValidator.get_currency_symbol('USD') == '$'
        assert AccountValidator.get_currency_symbol('EUR') == '€'
        assert AccountValidator.get_currency_symbol('GBP') == '£'
        assert AccountValidator.get_currency_symbol('JPY') == '¥'

    def test_get_decimal_places(self):
        """Test decimal places for different currencies."""
        assert AccountValidator.get_decimal_places('USD') == 2
        assert AccountValidator.get_decimal_places('EUR') == 2
        assert AccountValidator.get_decimal_places('JPY') == 0
        assert AccountValidator.get_decimal_places('KRW') == 0
        assert AccountValidator.get_decimal_places('CLP') == 0
        assert AccountValidator.get_decimal_places('VND') == 0

    def test_get_currency_info(self):
        """Test currency info retrieval."""
        info = AccountValidator.get_currency_info('USD')
        assert info['name'] == 'US Dollar'
        assert info['symbol'] == '$'
        assert info['decimals'] == 2

        # Test another currency
        info_jpy = AccountValidator.get_currency_info('JPY')
        assert info_jpy['name'] == 'Japanese Yen'
        assert info_jpy['symbol'] == '¥'
        assert info_jpy['decimals'] == 0


class TestCurrencyAwareAmountValidation:
    """Unit tests for currency-aware amount validation."""

    def test_validate_amount_usd_valid_two_decimals(self):
        """Test USD amount with 2 decimals (valid)."""
        amount = TransactionValidator.validate_amount('1234.56', 'USD')
        assert amount == Decimal('1234.56')

    def test_validate_amount_usd_invalid_three_decimals(self):
        """Test USD amount with 3 decimals (invalid)."""
        with pytest.raises(ValidationError, match="more than 2 decimal places"):
            TransactionValidator.validate_amount('1234.567', 'USD')

    def test_validate_amount_jpy_valid_zero_decimals(self):
        """Test JPY amount with 0 decimals (valid)."""
        amount = TransactionValidator.validate_amount('1235', 'JPY')
        assert amount == Decimal('1235')

    def test_validate_amount_jpy_invalid_one_decimal(self):
        """Test JPY amount with 1 decimal (invalid)."""
        with pytest.raises(ValidationError, match="more than 0 decimal places"):
            TransactionValidator.validate_amount('1234.5', 'JPY')

    def test_validate_amount_default_currency_usd(self):
        """Test amount validation defaults to USD."""
        amount = TransactionValidator.validate_amount('100.50')
        assert amount == Decimal('100.50')

        # Should reject 3 decimals (USD default)
        with pytest.raises(ValidationError, match="more than 2 decimal places"):
            TransactionValidator.validate_amount('100.505')


# Additional edge case tests
class TestCurrencyEdgeCases:
    """Additional edge case tests for currency handling."""

    def test_format_amount_negative_values(self):
        """Test formatting negative amounts."""
        formatted = AccountValidator.format_amount(Decimal('-1234.56'), 'USD')
        assert formatted == '$-1,234.56'

    def test_format_amount_zero(self):
        """Test formatting zero amount."""
        formatted_usd = AccountValidator.format_amount(Decimal('0.00'), 'USD')
        assert formatted_usd == '$0.00'

        formatted_jpy = AccountValidator.format_amount(Decimal('0'), 'JPY')
        assert formatted_jpy == '¥0'

    def test_format_amount_large_numbers(self):
        """Test formatting very large amounts."""
        formatted = AccountValidator.format_amount(Decimal('1234567.89'), 'USD')
        assert formatted == '$1,234,567.89'

    def test_all_zero_decimal_currencies(self):
        """Test all zero-decimal currencies are handled correctly."""
        zero_decimal_currencies = ['JPY', 'KRW', 'CLP', 'VND']

        for currency in zero_decimal_currencies:
            decimals = AccountValidator.get_decimal_places(currency)
            assert decimals == 0, f"{currency} should have 0 decimals"

            # Test formatting
            formatted = AccountValidator.format_amount(Decimal('1000.99'), currency)
            assert '.' not in formatted, f"{currency} should not show decimals"

    def test_currency_info_for_all_currencies(self):
        """Test currency info available for all supported currencies."""
        for code in AccountValidator.SUPPORTED_CURRENCIES.keys():
            info = AccountValidator.get_currency_info(code)

            assert 'name' in info, f"Missing name for {code}"
            assert 'symbol' in info, f"Missing symbol for {code}"
            assert 'decimals' in info, f"Missing decimals for {code}"

            assert isinstance(info['name'], str)
            assert isinstance(info['symbol'], str)
            assert isinstance(info['decimals'], int)
            assert info['decimals'] in [0, 2], f"{code} has invalid decimals: {info['decimals']}"
