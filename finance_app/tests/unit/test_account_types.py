"""
Unit tests for US-001: Account Type Taxonomy & Hierarchy

This test suite validates all acceptance criteria for the account type taxonomy feature.
"""

import pytest
from decimal import Decimal

from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
from finance_app.business.validators import AccountValidator
from finance_app.utils.exceptions import ValidationError


class TestAccountTypeEnums:
    """Test account type enumerations."""

    def test_account_type_values(self):
        """Test AccountType enum has correct values."""
        assert AccountType.ASSET.value == 'asset'
        assert AccountType.LIABILITY.value == 'liability'
        assert AccountType.EQUITY.value == 'equity'
        assert AccountType.INCOME.value == 'income'
        assert AccountType.EXPENSE.value == 'expense'

    def test_account_subtype_asset_values(self):
        """Test AccountSubtype enum has correct asset subtypes."""
        assert AccountSubtype.CHECKING.value == 'checking'
        assert AccountSubtype.SAVINGS.value == 'savings'
        assert AccountSubtype.CASH.value == 'cash'
        assert AccountSubtype.INVESTMENT.value == 'investment'
        assert AccountSubtype.OTHER_ASSET.value == 'other_asset'

    def test_account_subtype_liability_values(self):
        """Test AccountSubtype enum has correct liability subtypes."""
        assert AccountSubtype.CREDIT_CARD.value == 'credit_card'
        assert AccountSubtype.LOAN.value == 'loan'
        assert AccountSubtype.MORTGAGE.value == 'mortgage'
        assert AccountSubtype.LINE_OF_CREDIT.value == 'line_of_credit'
        assert AccountSubtype.OTHER_LIABILITY.value == 'other_liability'

    def test_account_subtype_equity_values(self):
        """Test AccountSubtype enum has correct equity subtypes."""
        assert AccountSubtype.OPENING_BALANCE.value == 'opening_balance'
        assert AccountSubtype.RETAINED_EARNINGS.value == 'retained_earnings'

    def test_account_subtype_income_values(self):
        """Test AccountSubtype enum has correct income subtypes."""
        assert AccountSubtype.SALARY.value == 'salary'
        assert AccountSubtype.BUSINESS_INCOME.value == 'business_income'
        assert AccountSubtype.INTEREST.value == 'interest'
        assert AccountSubtype.DIVIDENDS.value == 'dividends'
        assert AccountSubtype.OTHER_INCOME.value == 'other_income'

    def test_normal_balance_values(self):
        """Test NormalBalance enum has correct values."""
        assert NormalBalance.DEBIT.value == 'debit'
        assert NormalBalance.CREDIT.value == 'credit'


class TestAccountModel:
    """Test Account model with new type system."""

    def test_create_asset_account(self):
        """AC1: Test creating asset account with checking subtype."""
        account = Account(
            id=None,
            name="My Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        )

        assert account.name == "My Checking"
        assert account.account_type == AccountType.ASSET
        assert account.account_subtype == AccountSubtype.CHECKING
        assert account.normal_balance == NormalBalance.DEBIT
        assert account.balance == Decimal("1000.00")

    def test_create_liability_account(self):
        """AC1: Test creating liability account with credit card subtype."""
        account = Account(
            id=None,
            name="Visa Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.CREDIT,
            currency="USD"
        )

        assert account.account_type == AccountType.LIABILITY
        assert account.account_subtype == AccountSubtype.CREDIT_CARD
        assert account.normal_balance == NormalBalance.CREDIT

    def test_account_post_init_converts_strings(self):
        """Test Account __post_init__ converts string to enum."""
        account = Account(
            id=1,
            name="Test",
            account_type='asset',  # String
            account_subtype='checking',  # String
            balance=Decimal("100"),
            normal_balance='debit',  # String
        )

        assert isinstance(account.account_type, AccountType)
        assert isinstance(account.account_subtype, AccountSubtype)
        assert isinstance(account.normal_balance, NormalBalance)
        assert account.account_type == AccountType.ASSET


class TestAccountValidator:
    """Test account validation logic."""

    def test_validate_account_type_combination_asset_checking(self):
        """AC1, AC4: Test valid asset/checking combination."""
        validator = AccountValidator()

        acc_type, acc_subtype = validator.validate_account_type_combination(
            AccountType.ASSET,
            AccountSubtype.CHECKING
        )

        assert acc_type == AccountType.ASSET
        assert acc_subtype == AccountSubtype.CHECKING

    def test_validate_account_type_combination_liability_credit_card(self):
        """AC1, AC4: Test valid liability/credit_card combination."""
        validator = AccountValidator()

        acc_type, acc_subtype = validator.validate_account_type_combination(
            AccountType.LIABILITY,
            AccountSubtype.CREDIT_CARD
        )

        assert acc_type == AccountType.LIABILITY
        assert acc_subtype == AccountSubtype.CREDIT_CARD

    def test_invalid_subtype_for_asset(self):
        """AC4: Test that credit_card subtype is invalid for asset type."""
        validator = AccountValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_account_type_combination(
                AccountType.ASSET,
                AccountSubtype.CREDIT_CARD  # Invalid for assets
            )

        assert "Invalid subtype 'credit_card' for account type 'asset'" in str(exc_info.value)

    def test_invalid_subtype_for_liability(self):
        """AC4: Test that checking subtype is invalid for liability type."""
        validator = AccountValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_account_type_combination(
                AccountType.LIABILITY,
                AccountSubtype.CHECKING  # Invalid for liabilities
            )

        assert "Invalid subtype 'checking' for account type 'liability'" in str(exc_info.value)

    def test_get_normal_balance_asset(self):
        """AC3: Test normal balance auto-assignment for asset."""
        validator = AccountValidator()

        normal_balance = validator.get_normal_balance(AccountType.ASSET)

        assert normal_balance == NormalBalance.DEBIT

    def test_get_normal_balance_liability(self):
        """AC3: Test normal balance auto-assignment for liability."""
        validator = AccountValidator()

        normal_balance = validator.get_normal_balance(AccountType.LIABILITY)

        assert normal_balance == NormalBalance.CREDIT

    def test_get_normal_balance_equity(self):
        """AC3: Test normal balance auto-assignment for equity."""
        validator = AccountValidator()

        normal_balance = validator.get_normal_balance(AccountType.EQUITY)

        assert normal_balance == NormalBalance.CREDIT

    def test_get_normal_balance_income(self):
        """AC3: Test normal balance auto-assignment for income."""
        validator = AccountValidator()

        normal_balance = validator.get_normal_balance(AccountType.INCOME)

        assert normal_balance == NormalBalance.CREDIT

    def test_get_normal_balance_expense(self):
        """AC3: Test normal balance auto-assignment for expense."""
        validator = AccountValidator()

        normal_balance = validator.get_normal_balance(AccountType.EXPENSE)

        assert normal_balance == NormalBalance.DEBIT

    @pytest.mark.parametrize("account_type,expected_normal_balance", [
        (AccountType.ASSET, NormalBalance.DEBIT),
        (AccountType.EXPENSE, NormalBalance.DEBIT),
        (AccountType.LIABILITY, NormalBalance.CREDIT),
        (AccountType.EQUITY, NormalBalance.CREDIT),
        (AccountType.INCOME, NormalBalance.CREDIT),
    ])
    def test_normal_balance_for_all_types(self, account_type, expected_normal_balance):
        """AC3: Test normal balance assignment for all account types."""
        validator = AccountValidator()

        normal_balance = validator.get_normal_balance(account_type)

        assert normal_balance == expected_normal_balance

    def test_valid_subtypes_for_all_types(self):
        """AC1: Test that all account types have valid subtypes defined."""
        validator = AccountValidator()

        # Asset subtypes
        assert AccountSubtype.CHECKING in validator.VALID_SUBTYPES[AccountType.ASSET]
        assert AccountSubtype.SAVINGS in validator.VALID_SUBTYPES[AccountType.ASSET]
        assert AccountSubtype.CASH in validator.VALID_SUBTYPES[AccountType.ASSET]
        assert AccountSubtype.INVESTMENT in validator.VALID_SUBTYPES[AccountType.ASSET]
        assert AccountSubtype.OTHER_ASSET in validator.VALID_SUBTYPES[AccountType.ASSET]

        # Liability subtypes
        assert AccountSubtype.CREDIT_CARD in validator.VALID_SUBTYPES[AccountType.LIABILITY]
        assert AccountSubtype.LOAN in validator.VALID_SUBTYPES[AccountType.LIABILITY]
        assert AccountSubtype.MORTGAGE in validator.VALID_SUBTYPES[AccountType.LIABILITY]
        assert AccountSubtype.LINE_OF_CREDIT in validator.VALID_SUBTYPES[AccountType.LIABILITY]
        assert AccountSubtype.OTHER_LIABILITY in validator.VALID_SUBTYPES[AccountType.LIABILITY]

        # Equity subtypes
        assert AccountSubtype.OPENING_BALANCE in validator.VALID_SUBTYPES[AccountType.EQUITY]
        assert AccountSubtype.RETAINED_EARNINGS in validator.VALID_SUBTYPES[AccountType.EQUITY]

        # Income subtypes
        assert AccountSubtype.SALARY in validator.VALID_SUBTYPES[AccountType.INCOME]
        assert AccountSubtype.BUSINESS_INCOME in validator.VALID_SUBTYPES[AccountType.INCOME]
        assert AccountSubtype.INTEREST in validator.VALID_SUBTYPES[AccountType.INCOME]
        assert AccountSubtype.DIVIDENDS in validator.VALID_SUBTYPES[AccountType.INCOME]
        assert AccountSubtype.OTHER_INCOME in validator.VALID_SUBTYPES[AccountType.INCOME]

        # Expense subtypes
        assert AccountSubtype.EXPENSE_CATEGORY in validator.VALID_SUBTYPES[AccountType.EXPENSE]

    def test_string_to_enum_conversion(self):
        """Test validator converts strings to enums properly."""
        validator = AccountValidator()

        acc_type, acc_subtype = validator.validate_account_type_combination(
            'asset',  # String
            'checking'  # String
        )

        assert isinstance(acc_type, AccountType)
        assert isinstance(acc_subtype, AccountSubtype)
        assert acc_type == AccountType.ASSET
        assert acc_subtype == AccountSubtype.CHECKING

    def test_invalid_string_account_type(self):
        """Test validator rejects invalid account type string."""
        validator = AccountValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_account_type_combination(
                'invalid_type',
                'checking'
            )

        assert "Invalid account type: invalid_type" in str(exc_info.value)

    def test_invalid_string_account_subtype(self):
        """Test validator rejects invalid account subtype string."""
        validator = AccountValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_account_type_combination(
                'asset',
                'invalid_subtype'
            )

        assert "Invalid account subtype: invalid_subtype" in str(exc_info.value)


class TestNormalBalanceMapping:
    """Test the normal balance mapping is correct."""

    def test_normal_balance_map_completeness(self):
        """Test that all account types have a normal balance mapping."""
        validator = AccountValidator()

        for account_type in AccountType:
            assert account_type in validator.NORMAL_BALANCE_MAP

    def test_debit_normal_balances(self):
        """Test assets and expenses have debit normal balance."""
        validator = AccountValidator()

        assert validator.NORMAL_BALANCE_MAP[AccountType.ASSET] == NormalBalance.DEBIT
        assert validator.NORMAL_BALANCE_MAP[AccountType.EXPENSE] == NormalBalance.DEBIT

    def test_credit_normal_balances(self):
        """Test liabilities, equity, and income have credit normal balance."""
        validator = AccountValidator()

        assert validator.NORMAL_BALANCE_MAP[AccountType.LIABILITY] == NormalBalance.CREDIT
        assert validator.NORMAL_BALANCE_MAP[AccountType.EQUITY] == NormalBalance.CREDIT
        assert validator.NORMAL_BALANCE_MAP[AccountType.INCOME] == NormalBalance.CREDIT


class TestValidSubtypesMapping:
    """Test the valid subtypes mapping is correct."""

    def test_all_account_types_have_subtypes(self):
        """Test that all account types have valid subtypes defined."""
        validator = AccountValidator()

        for account_type in AccountType:
            assert account_type in validator.VALID_SUBTYPES
            assert len(validator.VALID_SUBTYPES[account_type]) > 0

    def test_asset_subtypes_count(self):
        """Test asset type has 5 subtypes."""
        validator = AccountValidator()

        assert len(validator.VALID_SUBTYPES[AccountType.ASSET]) == 5

    def test_liability_subtypes_count(self):
        """Test liability type has 5 subtypes."""
        validator = AccountValidator()

        assert len(validator.VALID_SUBTYPES[AccountType.LIABILITY]) == 5

    def test_equity_subtypes_count(self):
        """Test equity type has 2 subtypes."""
        validator = AccountValidator()

        assert len(validator.VALID_SUBTYPES[AccountType.EQUITY]) == 2

    def test_income_subtypes_count(self):
        """Test income type has 5 subtypes."""
        validator = AccountValidator()

        assert len(validator.VALID_SUBTYPES[AccountType.INCOME]) == 5

    def test_expense_subtypes_count(self):
        """Test expense type has 1 subtype."""
        validator = AccountValidator()

        assert len(validator.VALID_SUBTYPES[AccountType.EXPENSE]) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
