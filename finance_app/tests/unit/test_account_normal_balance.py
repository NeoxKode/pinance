"""
Unit tests for Account model normal balance behavior (US-003).

Tests auto-calculation and validation of normal balances in Account model.
"""

import pytest
from decimal import Decimal
from finance_app.data.models import (
    Account,
    AccountType,
    AccountSubtype,
    NormalBalance,
)
from finance_app.utils.exceptions import ValidationError


class TestAccountAutoCalculation:
    """Test automatic normal balance calculation when creating accounts."""

    def test_asset_account_auto_calculates_debit(self):
        """Asset account without normal_balance should auto-calculate as DEBIT."""
        account = Account(
            id=None,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=None  # Not provided
        )

        assert account.normal_balance == NormalBalance.DEBIT

    def test_expense_account_auto_calculates_debit(self):
        """Expense account without normal_balance should auto-calculate as DEBIT."""
        account = Account(
            id=None,
            name="Groceries",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubtype.EXPENSE_CATEGORY,
            balance=Decimal("0.00"),
            normal_balance=None  # Not provided
        )

        assert account.normal_balance == NormalBalance.DEBIT

    def test_liability_account_auto_calculates_credit(self):
        """Liability account without normal_balance should auto-calculate as CREDIT."""
        account = Account(
            id=None,
            name="Credit Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            balance=Decimal("500.00"),
            normal_balance=None  # Not provided
        )

        assert account.normal_balance == NormalBalance.CREDIT

    def test_equity_account_auto_calculates_credit(self):
        """Equity account without normal_balance should auto-calculate as CREDIT."""
        account = Account(
            id=None,
            name="Opening Balance Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubtype.OPENING_BALANCE,
            balance=Decimal("0.00"),
            normal_balance=None  # Not provided
        )

        assert account.normal_balance == NormalBalance.CREDIT

    def test_income_account_auto_calculates_credit(self):
        """Income account without normal_balance should auto-calculate as CREDIT."""
        account = Account(
            id=None,
            name="Salary",
            account_type=AccountType.INCOME,
            account_subtype=AccountSubtype.SALARY,
            balance=Decimal("0.00"),
            normal_balance=None  # Not provided
        )

        assert account.normal_balance == NormalBalance.CREDIT

    @pytest.mark.parametrize("account_type,expected_balance", [
        (AccountType.ASSET, NormalBalance.DEBIT),
        (AccountType.EXPENSE, NormalBalance.DEBIT),
        (AccountType.LIABILITY, NormalBalance.CREDIT),
        (AccountType.EQUITY, NormalBalance.CREDIT),
        (AccountType.INCOME, NormalBalance.CREDIT),
    ])
    def test_auto_calculation_all_types_parametrized(self, account_type, expected_balance):
        """Test auto-calculation for all account types."""
        account = Account(
            id=None,
            name="Test Account",
            account_type=account_type,
            account_subtype=AccountSubtype.OTHER_ASSET,  # Generic subtype
            balance=Decimal("0.00"),
            normal_balance=None
        )

        assert account.normal_balance == expected_balance


class TestAccountValidation:
    """Test normal balance validation when explicitly provided."""

    def test_asset_with_correct_debit_passes_validation(self):
        """Asset with explicit DEBIT normal balance should not raise error."""
        account = Account(
            id=None,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT  # Explicitly provided
        )

        # Should not raise, just verify it's set correctly
        assert account.normal_balance == NormalBalance.DEBIT

    def test_asset_with_incorrect_credit_raises_error(self):
        """Asset with explicit CREDIT normal balance should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Account(
                id=None,
                name="Checking",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                balance=Decimal("1000.00"),
                normal_balance=NormalBalance.CREDIT  # WRONG!
            )

        assert "Asset accounts must have debit normal balance" in str(exc_info.value)

    def test_expense_with_incorrect_credit_raises_error(self):
        """Expense with explicit CREDIT normal balance should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Account(
                id=None,
                name="Groceries",
                account_type=AccountType.EXPENSE,
                account_subtype=AccountSubtype.EXPENSE_CATEGORY,
                balance=Decimal("0.00"),
                normal_balance=NormalBalance.CREDIT  # WRONG!
            )

        assert "Expense accounts must have debit normal balance" in str(exc_info.value)

    def test_liability_with_incorrect_debit_raises_error(self):
        """Liability with explicit DEBIT normal balance should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Account(
                id=None,
                name="Credit Card",
                account_type=AccountType.LIABILITY,
                account_subtype=AccountSubtype.CREDIT_CARD,
                balance=Decimal("500.00"),
                normal_balance=NormalBalance.DEBIT  # WRONG!
            )

        assert "Liability accounts must have credit normal balance" in str(exc_info.value)

    def test_equity_with_incorrect_debit_raises_error(self):
        """Equity with explicit DEBIT normal balance should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Account(
                id=None,
                name="Opening Balance",
                account_type=AccountType.EQUITY,
                account_subtype=AccountSubtype.OPENING_BALANCE,
                balance=Decimal("0.00"),
                normal_balance=NormalBalance.DEBIT  # WRONG!
            )

        assert "Equity accounts must have credit normal balance" in str(exc_info.value)

    def test_income_with_incorrect_debit_raises_error(self):
        """Income with explicit DEBIT normal balance should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Account(
                id=None,
                name="Salary",
                account_type=AccountType.INCOME,
                account_subtype=AccountSubtype.SALARY,
                balance=Decimal("0.00"),
                normal_balance=NormalBalance.DEBIT  # WRONG!
            )

        assert "Income accounts must have credit normal balance" in str(exc_info.value)

    def test_string_normal_balance_converted_and_validated(self):
        """String normal balance should be converted to enum and validated."""
        account = Account(
            id=None,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance="debit"  # String instead of enum
        )

        assert account.normal_balance == NormalBalance.DEBIT
        assert isinstance(account.normal_balance, NormalBalance)

    def test_string_wrong_normal_balance_raises_error(self):
        """String wrong normal balance should raise ValidationError."""
        with pytest.raises(ValidationError):
            Account(
                id=None,
                name="Checking",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                balance=Decimal("1000.00"),
                normal_balance="credit"  # WRONG as string
            )


class TestAccountInstanceMethods:
    """Test Account instance helper methods."""

    def test_is_debit_account_for_asset(self):
        """Asset account should return True for is_debit_account()."""
        account = Account(
            id=None,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00")
        )

        assert account.is_debit_account() is True

    def test_is_debit_account_for_liability(self):
        """Liability account should return False for is_debit_account()."""
        account = Account(
            id=None,
            name="Credit Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            balance=Decimal("500.00")
        )

        assert account.is_debit_account() is False

    def test_increases_with_debit_for_asset(self):
        """Asset account should increase with debits."""
        account = Account(
            id=None,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00")
        )

        assert account.increases_with_debit() is True
        assert account.increases_with_credit() is False

    def test_increases_with_credit_for_liability(self):
        """Liability account should increase with credits."""
        account = Account(
            id=None,
            name="Credit Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            balance=Decimal("500.00")
        )

        assert account.increases_with_credit() is True
        assert account.increases_with_debit() is False

    def test_increases_with_debit_for_expense(self):
        """Expense account should increase with debits."""
        account = Account(
            id=None,
            name="Groceries",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubtype.EXPENSE_CATEGORY,
            balance=Decimal("0.00")
        )

        assert account.increases_with_debit() is True
        assert account.increases_with_credit() is False

    def test_increases_with_credit_for_income(self):
        """Income account should increase with credits."""
        account = Account(
            id=None,
            name="Salary",
            account_type=AccountType.INCOME,
            account_subtype=AccountSubtype.SALARY,
            balance=Decimal("0.00")
        )

        assert account.increases_with_credit() is True
        assert account.increases_with_debit() is False

    @pytest.mark.parametrize("account_type,should_increase_debit", [
        (AccountType.ASSET, True),
        (AccountType.EXPENSE, True),
        (AccountType.LIABILITY, False),
        (AccountType.EQUITY, False),
        (AccountType.INCOME, False),
    ])
    def test_increases_with_debit_parametrized(self, account_type, should_increase_debit):
        """Test increases_with_debit for all account types."""
        account = Account(
            id=None,
            name="Test Account",
            account_type=account_type,
            account_subtype=AccountSubtype.OTHER_ASSET,
            balance=Decimal("0.00")
        )

        assert account.increases_with_debit() == should_increase_debit
        assert account.increases_with_credit() == (not should_increase_debit)


class TestBackwardCompatibility:
    """Test that existing code with explicit normal_balance still works."""

    def test_existing_code_with_explicit_normal_balance_works(self):
        """Existing code that provides normal_balance should still work."""
        account = Account(
            id=1,
            name="Legacy Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT  # Explicit like old code
        )

        assert account.normal_balance == NormalBalance.DEBIT
        assert account.is_debit_account() is True

    def test_can_still_provide_explicit_values_for_all_types(self):
        """Can still explicitly provide correct normal balance values."""
        accounts = [
            Account(
                id=1,
                name="Checking",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                balance=Decimal("1000.00"),
                normal_balance=NormalBalance.DEBIT
            ),
            Account(
                id=2,
                name="Credit Card",
                account_type=AccountType.LIABILITY,
                account_subtype=AccountSubtype.CREDIT_CARD,
                balance=Decimal("500.00"),
                normal_balance=NormalBalance.CREDIT
            ),
        ]

        assert accounts[0].normal_balance == NormalBalance.DEBIT
        assert accounts[1].normal_balance == NormalBalance.CREDIT


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_account_with_string_account_type_and_auto_balance(self):
        """Account with string account_type should auto-calculate normal balance."""
        account = Account(
            id=None,
            name="Test",
            account_type="asset",  # String instead of enum
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=None
        )

        assert account.account_type == AccountType.ASSET
        assert account.normal_balance == NormalBalance.DEBIT

    def test_zero_balance_account_still_gets_normal_balance(self):
        """Account with zero balance should still have normal balance."""
        account = Account(
            id=None,
            name="New Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=None
        )

        assert account.normal_balance == NormalBalance.DEBIT

    def test_negative_balance_account_still_gets_normal_balance(self):
        """Account with negative balance should still have normal balance."""
        account = Account(
            id=None,
            name="Overdraft Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("-100.00"),
            normal_balance=None
        )

        assert account.normal_balance == NormalBalance.DEBIT
