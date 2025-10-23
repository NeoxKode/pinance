"""
Unit tests for accounting_helpers module (US-003).

Tests the helper functions for normal balance determination and validation.
"""

import pytest
from finance_app.data.models import AccountType, NormalBalance
from finance_app.utils.accounting_helpers import (
    get_normal_balance,
    validate_normal_balance,
    is_debit_account,
    is_credit_account,
    increases_with_debit,
    increases_with_credit,
)
from finance_app.utils.exceptions import ValidationError


class TestGetNormalBalance:
    """Test get_normal_balance() function."""

    def test_asset_has_debit_normal_balance(self):
        """Asset accounts should have debit normal balance."""
        result = get_normal_balance(AccountType.ASSET)
        assert result == NormalBalance.DEBIT

    def test_expense_has_debit_normal_balance(self):
        """Expense accounts should have debit normal balance."""
        result = get_normal_balance(AccountType.EXPENSE)
        assert result == NormalBalance.DEBIT

    def test_liability_has_credit_normal_balance(self):
        """Liability accounts should have credit normal balance."""
        result = get_normal_balance(AccountType.LIABILITY)
        assert result == NormalBalance.CREDIT

    def test_equity_has_credit_normal_balance(self):
        """Equity accounts should have credit normal balance."""
        result = get_normal_balance(AccountType.EQUITY)
        assert result == NormalBalance.CREDIT

    def test_income_has_credit_normal_balance(self):
        """Income accounts should have credit normal balance."""
        result = get_normal_balance(AccountType.INCOME)
        assert result == NormalBalance.CREDIT

    @pytest.mark.parametrize("account_type,expected", [
        (AccountType.ASSET, NormalBalance.DEBIT),
        (AccountType.EXPENSE, NormalBalance.DEBIT),
        (AccountType.LIABILITY, NormalBalance.CREDIT),
        (AccountType.EQUITY, NormalBalance.CREDIT),
        (AccountType.INCOME, NormalBalance.CREDIT),
    ])
    def test_all_account_types_parametrized(self, account_type, expected):
        """Test all account types with parametrized test."""
        result = get_normal_balance(account_type)
        assert result == expected


class TestValidateNormalBalance:
    """Test validate_normal_balance() function."""

    def test_asset_with_debit_is_valid(self):
        """Asset with debit normal balance should not raise error."""
        # Should not raise
        validate_normal_balance(AccountType.ASSET, NormalBalance.DEBIT)

    def test_asset_with_credit_raises_error(self):
        """Asset with credit normal balance should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_normal_balance(AccountType.ASSET, NormalBalance.CREDIT)

        assert "Asset accounts must have debit normal balance" in str(exc_info.value)

    def test_expense_with_debit_is_valid(self):
        """Expense with debit normal balance should not raise error."""
        # Should not raise
        validate_normal_balance(AccountType.EXPENSE, NormalBalance.DEBIT)

    def test_expense_with_credit_raises_error(self):
        """Expense with credit normal balance should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_normal_balance(AccountType.EXPENSE, NormalBalance.CREDIT)

        assert "Expense accounts must have debit normal balance" in str(exc_info.value)

    def test_liability_with_credit_is_valid(self):
        """Liability with credit normal balance should not raise error."""
        # Should not raise
        validate_normal_balance(AccountType.LIABILITY, NormalBalance.CREDIT)

    def test_liability_with_debit_raises_error(self):
        """Liability with debit normal balance should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_normal_balance(AccountType.LIABILITY, NormalBalance.DEBIT)

        assert "Liability accounts must have credit normal balance" in str(exc_info.value)

    def test_equity_with_credit_is_valid(self):
        """Equity with credit normal balance should not raise error."""
        # Should not raise
        validate_normal_balance(AccountType.EQUITY, NormalBalance.CREDIT)

    def test_equity_with_debit_raises_error(self):
        """Equity with debit normal balance should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_normal_balance(AccountType.EQUITY, NormalBalance.DEBIT)

        assert "Equity accounts must have credit normal balance" in str(exc_info.value)

    def test_income_with_credit_is_valid(self):
        """Income with credit normal balance should not raise error."""
        # Should not raise
        validate_normal_balance(AccountType.INCOME, NormalBalance.CREDIT)

    def test_income_with_debit_raises_error(self):
        """Income with debit normal balance should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_normal_balance(AccountType.INCOME, NormalBalance.DEBIT)

        assert "Income accounts must have credit normal balance" in str(exc_info.value)

    @pytest.mark.parametrize("account_type,valid_balance", [
        (AccountType.ASSET, NormalBalance.DEBIT),
        (AccountType.EXPENSE, NormalBalance.DEBIT),
        (AccountType.LIABILITY, NormalBalance.CREDIT),
        (AccountType.EQUITY, NormalBalance.CREDIT),
        (AccountType.INCOME, NormalBalance.CREDIT),
    ])
    def test_valid_combinations_parametrized(self, account_type, valid_balance):
        """Test all valid account type + normal balance combinations."""
        # Should not raise
        validate_normal_balance(account_type, valid_balance)

    @pytest.mark.parametrize("account_type,invalid_balance", [
        (AccountType.ASSET, NormalBalance.CREDIT),
        (AccountType.EXPENSE, NormalBalance.CREDIT),
        (AccountType.LIABILITY, NormalBalance.DEBIT),
        (AccountType.EQUITY, NormalBalance.DEBIT),
        (AccountType.INCOME, NormalBalance.DEBIT),
    ])
    def test_invalid_combinations_parametrized(self, account_type, invalid_balance):
        """Test all invalid account type + normal balance combinations."""
        with pytest.raises(ValidationError):
            validate_normal_balance(account_type, invalid_balance)


class TestIsDebitAccount:
    """Test is_debit_account() function."""

    def test_debit_returns_true(self):
        """Debit normal balance should return True."""
        result = is_debit_account(NormalBalance.DEBIT)
        assert result is True

    def test_credit_returns_false(self):
        """Credit normal balance should return False."""
        result = is_debit_account(NormalBalance.CREDIT)
        assert result is False


class TestIsCreditAccount:
    """Test is_credit_account() function."""

    def test_credit_returns_true(self):
        """Credit normal balance should return True."""
        result = is_credit_account(NormalBalance.CREDIT)
        assert result is True

    def test_debit_returns_false(self):
        """Debit normal balance should return False."""
        result = is_credit_account(NormalBalance.DEBIT)
        assert result is False


class TestIncreasesWithDebit:
    """Test increases_with_debit() function."""

    def test_debit_account_increases_with_debit(self):
        """Debit normal balance accounts increase with debits."""
        result = increases_with_debit(NormalBalance.DEBIT)
        assert result is True

    def test_credit_account_does_not_increase_with_debit(self):
        """Credit normal balance accounts do not increase with debits."""
        result = increases_with_debit(NormalBalance.CREDIT)
        assert result is False


class TestIncreasesWithCredit:
    """Test increases_with_credit() function."""

    def test_credit_account_increases_with_credit(self):
        """Credit normal balance accounts increase with credits."""
        result = increases_with_credit(NormalBalance.CREDIT)
        assert result is True

    def test_debit_account_does_not_increase_with_credit(self):
        """Debit normal balance accounts do not increase with credits."""
        result = increases_with_credit(NormalBalance.DEBIT)
        assert result is False


class TestHelperFunctionConsistency:
    """Test that helper functions are consistent with each other."""

    def test_is_debit_and_is_credit_are_opposites(self):
        """is_debit_account and is_credit_account should be opposites."""
        assert is_debit_account(NormalBalance.DEBIT) is True
        assert is_credit_account(NormalBalance.DEBIT) is False

        assert is_debit_account(NormalBalance.CREDIT) is False
        assert is_credit_account(NormalBalance.CREDIT) is True

    def test_increases_with_debit_and_credit_are_opposites(self):
        """increases_with_debit and increases_with_credit should be opposites."""
        assert increases_with_debit(NormalBalance.DEBIT) is True
        assert increases_with_credit(NormalBalance.DEBIT) is False

        assert increases_with_debit(NormalBalance.CREDIT) is False
        assert increases_with_credit(NormalBalance.CREDIT) is True

    def test_is_debit_equals_increases_with_debit(self):
        """is_debit_account should equal increases_with_debit."""
        for balance in [NormalBalance.DEBIT, NormalBalance.CREDIT]:
            assert is_debit_account(balance) == increases_with_debit(balance)

    def test_is_credit_equals_increases_with_credit(self):
        """is_credit_account should equal increases_with_credit."""
        for balance in [NormalBalance.DEBIT, NormalBalance.CREDIT]:
            assert is_credit_account(balance) == increases_with_credit(balance)
