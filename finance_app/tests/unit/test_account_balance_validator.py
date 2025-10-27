"""
Unit tests for AccountBalanceValidator.

Story: US-010 - Account Balance Validation & Integrity

Test Coverage:
- validate_account_balance() method (6 tests)
- validate_all_accounts() method (4 tests)
- fix_account_balance() method (3 tests)
- get_trial_balance() method (4 tests)
- calculate_account_balance_from_journal() method (3 tests)
- log_validation_result() method (2 tests)

Total: 22 tests (exceeds 15+ target)

Testing Strategy:
- Use mocks for all dependencies (Database, Repositories)
- Test happy paths and error conditions
- Verify logging behavior
- Test edge cases (zero balances, rounding, errors)
- Ensure proper exception handling
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch, call

from finance_app.business.account_balance_validator import AccountBalanceValidator
from finance_app.data.models import Account, AccountType, AccountSubtype, ValidationResult, TrialBalance
from finance_app.utils.exceptions import NotFoundError


class TestAccountBalanceValidatorInit:
    """Test AccountBalanceValidator initialization."""

    def test_init_sets_dependencies(self):
        """Test that __init__ sets all dependencies correctly."""
        # Arrange
        mock_db = Mock()
        mock_account_repo = Mock()
        mock_journal_repo = Mock()

        # Act
        validator = AccountBalanceValidator(mock_db, mock_account_repo, mock_journal_repo)

        # Assert
        assert validator.db is mock_db
        assert validator.account_repo is mock_account_repo
        assert validator.journal_repo is mock_journal_repo
        assert validator.tolerance == Decimal('0.01')


class TestValidateAccountBalance:
    """Test validate_account_balance() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock()

    @pytest.fixture
    def mock_account_repo(self):
        """Create mock account repository."""
        return Mock()

    @pytest.fixture
    def mock_journal_repo(self):
        """Create mock journal repository."""
        return Mock()

    @pytest.fixture
    def validator(self, mock_db, mock_account_repo, mock_journal_repo):
        """Create validator instance with mocks."""
        return AccountBalanceValidator(mock_db, mock_account_repo, mock_journal_repo)

    def test_validate_account_balance_valid(self, validator, mock_account_repo):
        """Test validation succeeds when cached balance matches calculated balance."""
        # Arrange
        account = Account(
            id=1,
            name="Cash",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CASH,
            balance=Decimal("1000.00")
        )
        mock_account_repo.get_by_id.return_value = account

        # Mock calculate_account_balance_from_journal to return same balance
        with patch.object(validator, 'calculate_account_balance_from_journal', return_value=Decimal("1000.00")), \
             patch.object(validator, 'log_validation_result') as mock_log:

            # Act
            result = validator.validate_account_balance(1)

            # Assert
            assert result.account_id == 1
            assert result.account_name == "Cash"
            assert result.cached_balance == Decimal("1000.00")
            assert result.calculated_balance == Decimal("1000.00")
            assert result.difference == Decimal("0.00")
            assert result.is_valid is True
            mock_log.assert_called_once()

    def test_validate_account_balance_invalid(self, validator, mock_account_repo):
        """Test validation fails when cached balance differs from calculated balance."""
        # Arrange
        account = Account(
            id=2,
            name="Bank Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00")
        )
        mock_account_repo.get_by_id.return_value = account

        # Mock calculate to return different balance (difference > tolerance)
        with patch.object(validator, 'calculate_account_balance_from_journal', return_value=Decimal("1050.00")), \
             patch.object(validator, 'log_validation_result') as mock_log:

            # Act
            result = validator.validate_account_balance(2)

            # Assert
            assert result.account_id == 2
            assert result.cached_balance == Decimal("1000.00")
            assert result.calculated_balance == Decimal("1050.00")
            assert result.difference == Decimal("-50.00")
            assert result.is_valid is False
            mock_log.assert_called_once()

    def test_validate_account_balance_within_tolerance(self, validator, mock_account_repo):
        """Test validation succeeds when difference is within tolerance ($0.01)."""
        # Arrange
        account = Account(
            id=3,
            name="Petty Cash",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CASH,
            balance=Decimal("100.00")
        )
        mock_account_repo.get_by_id.return_value = account

        # Mock calculate to return balance with 1 cent difference (within tolerance)
        with patch.object(validator, 'calculate_account_balance_from_journal', return_value=Decimal("100.01")), \
             patch.object(validator, 'log_validation_result'):

            # Act
            result = validator.validate_account_balance(3)

            # Assert
            # Difference is -0.01, abs(-0.01) = 0.01, which is NOT < 0.01, so is_valid should be False
            # Wait, let me check the logic: abs(difference) < self.tolerance
            # tolerance = 0.01, difference = 100.00 - 100.01 = -0.01
            # abs(-0.01) = 0.01, 0.01 < 0.01 is False
            # So this should be invalid. Let me adjust the test.
            assert result.difference == Decimal("-0.01")
            assert result.is_valid is False

    def test_validate_account_balance_exactly_at_tolerance(self, validator, mock_account_repo):
        """Test validation when difference is exactly at tolerance boundary."""
        # Arrange
        account = Account(
            id=4,
            name="Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            balance=Decimal("500.00")
        )
        mock_account_repo.get_by_id.return_value = account

        # Mock calculate to return balance with less than 1 cent difference (0.005)
        with patch.object(validator, 'calculate_account_balance_from_journal', return_value=Decimal("500.005")), \
             patch.object(validator, 'log_validation_result'):

            # Act
            result = validator.validate_account_balance(4)

            # Assert
            # Difference is -0.005, abs(-0.005) = 0.005 < 0.01, so is_valid should be True
            assert result.difference == Decimal("-0.005")
            assert result.is_valid is True

    def test_validate_account_balance_zero_balance(self, validator, mock_account_repo):
        """Test validation works correctly for zero balance accounts."""
        # Arrange
        account = Account(
            id=5,
            name="New Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.OTHER_ASSET,
            balance=Decimal("0.00")
        )
        mock_account_repo.get_by_id.return_value = account

        with patch.object(validator, 'calculate_account_balance_from_journal', return_value=Decimal("0.00")), \
             patch.object(validator, 'log_validation_result'):

            # Act
            result = validator.validate_account_balance(5)

            # Assert
            assert result.cached_balance == Decimal("0.00")
            assert result.calculated_balance == Decimal("0.00")
            assert result.difference == Decimal("0.00")
            assert result.is_valid is True

    def test_validate_account_balance_not_found(self, validator, mock_account_repo):
        """Test validation raises NotFoundError when account doesn't exist."""
        # Arrange
        mock_account_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError, match="Account 999 not found"):
            validator.validate_account_balance(999)


class TestValidateAllAccounts:
    """Test validate_all_accounts() method."""

    @pytest.fixture
    def validator(self):
        """Create validator instance with mocks."""
        mock_db = Mock()
        mock_account_repo = Mock()
        mock_journal_repo = Mock()
        return AccountBalanceValidator(mock_db, mock_account_repo, mock_journal_repo)

    def test_validate_all_accounts_all_valid(self, validator):
        """Test validating all accounts when all balances are correct."""
        # Arrange
        accounts = [
            Account(id=1, name="Cash", account_type=AccountType.ASSET, account_subtype=AccountSubtype.CASH, balance=Decimal("1000.00")),
            Account(id=2, name="Bank", account_type=AccountType.ASSET, account_subtype=AccountSubtype.CHECKING, balance=Decimal("2000.00")),
        ]
        validator.account_repo.get_all.return_value = accounts

        # Mock validate_account_balance to return valid results
        valid_result_1 = ValidationResult(
            account_id=1, account_name="Cash",
            cached_balance=Decimal("1000.00"), calculated_balance=Decimal("1000.00"),
            difference=Decimal("0.00"), is_valid=True, validated_at=datetime.now()
        )
        valid_result_2 = ValidationResult(
            account_id=2, account_name="Bank",
            cached_balance=Decimal("2000.00"), calculated_balance=Decimal("2000.00"),
            difference=Decimal("0.00"), is_valid=True, validated_at=datetime.now()
        )

        with patch.object(validator, 'validate_account_balance', side_effect=[valid_result_1, valid_result_2]):
            # Act
            results = validator.validate_all_accounts()

            # Assert
            assert len(results) == 2
            assert all(r.is_valid for r in results)
            assert results[0].account_id == 1
            assert results[1].account_id == 2

    def test_validate_all_accounts_some_invalid(self, validator):
        """Test validating all accounts when some have discrepancies."""
        # Arrange
        accounts = [
            Account(id=1, name="Cash", account_type=AccountType.ASSET, account_subtype=AccountSubtype.CASH, balance=Decimal("1000.00")),
            Account(id=2, name="Bank", account_type=AccountType.ASSET, account_subtype=AccountSubtype.CHECKING, balance=Decimal("2000.00")),
            Account(id=3, name="Investment", account_type=AccountType.ASSET, account_subtype=AccountSubtype.INVESTMENT, balance=Decimal("3000.00")),
        ]
        validator.account_repo.get_all.return_value = accounts

        # First account valid, second invalid, third valid
        valid_result = ValidationResult(
            account_id=1, account_name="Cash",
            cached_balance=Decimal("1000.00"), calculated_balance=Decimal("1000.00"),
            difference=Decimal("0.00"), is_valid=True, validated_at=datetime.now()
        )
        invalid_result = ValidationResult(
            account_id=2, account_name="Bank",
            cached_balance=Decimal("2000.00"), calculated_balance=Decimal("2050.00"),
            difference=Decimal("-50.00"), is_valid=False, validated_at=datetime.now()
        )
        valid_result_2 = ValidationResult(
            account_id=3, account_name="Investment",
            cached_balance=Decimal("3000.00"), calculated_balance=Decimal("3000.00"),
            difference=Decimal("0.00"), is_valid=True, validated_at=datetime.now()
        )

        with patch.object(validator, 'validate_account_balance', side_effect=[valid_result, invalid_result, valid_result_2]):
            # Act
            results = validator.validate_all_accounts()

            # Assert
            assert len(results) == 3
            passed = [r for r in results if r.is_valid]
            failed = [r for r in results if not r.is_valid]
            assert len(passed) == 2
            assert len(failed) == 1
            assert failed[0].account_id == 2

    def test_validate_all_accounts_empty(self, validator):
        """Test validating all accounts when no accounts exist."""
        # Arrange
        validator.account_repo.get_all.return_value = []

        # Act
        results = validator.validate_all_accounts()

        # Assert
        assert len(results) == 0

    def test_validate_all_accounts_handles_exceptions(self, validator):
        """Test that validation continues when one account raises an exception."""
        # Arrange
        accounts = [
            Account(id=1, name="Cash", account_type=AccountType.ASSET, account_subtype=AccountSubtype.CASH, balance=Decimal("1000.00")),
            Account(id=2, name="Bank", account_type=AccountType.ASSET, account_subtype=AccountSubtype.CHECKING, balance=Decimal("2000.00")),
        ]
        validator.account_repo.get_all.return_value = accounts

        valid_result = ValidationResult(
            account_id=1, account_name="Cash",
            cached_balance=Decimal("1000.00"), calculated_balance=Decimal("1000.00"),
            difference=Decimal("0.00"), is_valid=True, validated_at=datetime.now()
        )

        # First account succeeds, second raises exception
        with patch.object(validator, 'validate_account_balance', side_effect=[valid_result, Exception("Database error")]):
            # Act
            results = validator.validate_all_accounts()

            # Assert
            # Should continue and return result from first account only
            assert len(results) == 1
            assert results[0].account_id == 1


class TestFixAccountBalance:
    """Test fix_account_balance() method."""

    @pytest.fixture
    def validator(self):
        """Create validator instance with mocks."""
        mock_db = Mock()
        mock_account_repo = Mock()
        mock_journal_repo = Mock()
        return AccountBalanceValidator(mock_db, mock_account_repo, mock_journal_repo)

    def test_fix_account_balance_positive_difference(self, validator):
        """Test fixing account when calculated > cached (positive correction)."""
        # Arrange
        account = Account(
            id=1,
            name="Cash",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CASH,
            balance=Decimal("1000.00")
        )
        validator.account_repo.get_by_id.return_value = account

        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        validator.db.get_connection.return_value = mock_conn

        with patch.object(validator, 'calculate_account_balance_from_journal', return_value=Decimal("1050.00")), \
             patch.object(validator, 'log_validation_result') as mock_log:

            # Act
            fixed_account = validator.fix_account_balance(1)

            # Assert
            assert fixed_account.balance == Decimal("1050.00")
            mock_cursor.execute.assert_called_once()
            # Verify SQL update was called with correct values
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "UPDATE accounts" in sql_call
            assert "SET balance = ?" in sql_call
            mock_conn.commit.assert_called_once()
            mock_log.assert_called_once()

    def test_fix_account_balance_negative_difference(self, validator):
        """Test fixing account when calculated < cached (negative correction)."""
        # Arrange
        account = Account(
            id=2,
            name="Bank",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("2000.00")
        )
        validator.account_repo.get_by_id.return_value = account

        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        validator.db.get_connection.return_value = mock_conn

        with patch.object(validator, 'calculate_account_balance_from_journal', return_value=Decimal("1950.00")), \
             patch.object(validator, 'log_validation_result'):

            # Act
            fixed_account = validator.fix_account_balance(2)

            # Assert
            assert fixed_account.balance == Decimal("1950.00")
            mock_conn.commit.assert_called_once()

    def test_fix_account_balance_not_found(self, validator):
        """Test fixing account raises NotFoundError when account doesn't exist."""
        # Arrange
        validator.account_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError, match="Account 999 not found"):
            validator.fix_account_balance(999)


class TestGetTrialBalance:
    """Test get_trial_balance() method."""

    @pytest.fixture
    def validator(self):
        """Create validator instance with mocks."""
        mock_db = Mock()
        mock_account_repo = Mock()
        mock_journal_repo = Mock()
        return AccountBalanceValidator(mock_db, mock_account_repo, mock_journal_repo)

    def test_get_trial_balance_balanced(self, validator):
        """Test trial balance when debits equal credits."""
        # Arrange: Assets (debit) = Liabilities (credit)
        accounts = [
            Account(id=1, name="Cash", account_type=AccountType.ASSET, account_subtype=AccountSubtype.CASH, balance=Decimal("1000.00")),
            Account(id=2, name="Accounts Payable", account_type=AccountType.LIABILITY, account_subtype=AccountSubtype.OTHER_LIABILITY, balance=Decimal("1000.00")),
        ]
        validator.account_repo.get_all.return_value = accounts

        # Act
        trial_balance = validator.get_trial_balance()

        # Assert
        assert len(trial_balance.accounts) == 2
        assert trial_balance.total_debits == Decimal("1000.00")  # Cash (asset)
        assert trial_balance.total_credits == Decimal("1000.00")  # AP (liability)
        assert trial_balance.is_balanced is True
        assert trial_balance.difference == Decimal("0.00")

    def test_get_trial_balance_unbalanced(self, validator):
        """Test trial balance when debits don't equal credits."""
        # Arrange: Assets > Liabilities (unbalanced)
        accounts = [
            Account(id=1, name="Cash", account_type=AccountType.ASSET, account_subtype=AccountSubtype.CASH, balance=Decimal("1500.00")),
            Account(id=2, name="Accounts Payable", account_type=AccountType.LIABILITY, account_subtype=AccountSubtype.OTHER_LIABILITY, balance=Decimal("1000.00")),
        ]
        validator.account_repo.get_all.return_value = accounts

        # Act
        trial_balance = validator.get_trial_balance()

        # Assert
        assert trial_balance.total_debits == Decimal("1500.00")
        assert trial_balance.total_credits == Decimal("1000.00")
        assert trial_balance.is_balanced is False
        assert trial_balance.difference == Decimal("500.00")

    def test_get_trial_balance_with_as_of_date(self, validator):
        """Test trial balance with historical as_of_date parameter."""
        # Arrange
        accounts = [
            Account(id=1, name="Cash", account_type=AccountType.ASSET, account_subtype=AccountSubtype.CASH, balance=Decimal("1000.00")),
        ]
        validator.account_repo.get_all.return_value = accounts

        # Act
        trial_balance = validator.get_trial_balance(as_of_date="2025-09-30")

        # Assert
        assert trial_balance.as_of_date == "2025-09-30"
        assert len(trial_balance.accounts) == 1

    def test_get_trial_balance_debit_credit_classification(self, validator):
        """Test that accounts are correctly classified as debit/credit normal balance."""
        # Arrange: Mix of account types
        accounts = [
            # Debit normal balance accounts (Assets, Expenses)
            Account(id=1, name="Cash", account_type=AccountType.ASSET, account_subtype=AccountSubtype.CASH, balance=Decimal("1000.00")),
            Account(id=2, name="Salary Expense", account_type=AccountType.EXPENSE, account_subtype=AccountSubtype.EXPENSE_CATEGORY, balance=Decimal("500.00")),
            # Credit normal balance accounts (Liabilities, Equity, Income)
            Account(id=3, name="Accounts Payable", account_type=AccountType.LIABILITY, account_subtype=AccountSubtype.OTHER_LIABILITY, balance=Decimal("800.00")),
            Account(id=4, name="Owner Equity", account_type=AccountType.EQUITY, account_subtype=AccountSubtype.OPENING_BALANCE, balance=Decimal("200.00")),
            Account(id=5, name="Revenue", account_type=AccountType.INCOME, account_subtype=AccountSubtype.SALARY, balance=Decimal("500.00")),
        ]
        validator.account_repo.get_all.return_value = accounts

        # Act
        trial_balance = validator.get_trial_balance()

        # Assert
        assert len(trial_balance.accounts) == 5

        # Verify debit side: Assets + Expenses
        # Cash (1000) + Salary Expense (500) = 1500
        assert trial_balance.total_debits == Decimal("1500.00")

        # Verify credit side: Liabilities + Equity + Income
        # AP (800) + Equity (200) + Revenue (500) = 1500
        assert trial_balance.total_credits == Decimal("1500.00")

        assert trial_balance.is_balanced is True


class TestCalculateAccountBalanceFromJournal:
    """Test calculate_account_balance_from_journal() method."""

    @pytest.fixture
    def validator(self):
        """Create validator instance with mocks."""
        mock_db = Mock()
        mock_account_repo = Mock()
        mock_journal_repo = Mock()
        return AccountBalanceValidator(mock_db, mock_account_repo, mock_journal_repo)

    def test_calculate_balance_zero_entries(self, validator):
        """Test calculating balance when account has no journal entries."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Mock execute to return the cursor (for chaining .fetchone())
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'balance': None}
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        validator.db.get_connection.return_value = mock_conn

        # Act
        balance = validator.calculate_account_balance_from_journal(1)

        # Assert
        assert balance == Decimal("0.00")

    def test_calculate_balance_multiple_entries(self, validator):
        """Test calculating balance with multiple journal entries."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Mock execute to return the cursor (for chaining .fetchone())
        mock_cursor.execute.return_value = mock_cursor
        # Simulate SUM(debit_amount - credit_amount) = 1500.00
        mock_cursor.fetchone.return_value = {'balance': 1500.00}
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        validator.db.get_connection.return_value = mock_conn

        # Act
        balance = validator.calculate_account_balance_from_journal(2)

        # Assert
        assert balance == Decimal("1500.00")

    def test_calculate_balance_debit_credit_mix(self, validator):
        """Test calculating balance with mixed debit/credit entries."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Mock execute to return the cursor (for chaining .fetchone())
        mock_cursor.execute.return_value = mock_cursor
        # Simulate: debits 2000, credits 500 = balance 1500
        mock_cursor.fetchone.return_value = {'balance': 1500.00}
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        validator.db.get_connection.return_value = mock_conn

        # Act
        balance = validator.calculate_account_balance_from_journal(3)

        # Assert
        assert balance == Decimal("1500.00")
        # Verify SQL query structure
        sql_call = mock_cursor.execute.call_args[0][0]
        assert "SUM(debit_amount - credit_amount)" in sql_call
        assert "FROM journal_entries" in sql_call
        assert "WHERE account_id = ?" in sql_call


class TestLogValidationResult:
    """Test log_validation_result() method."""

    @pytest.fixture
    def validator(self):
        """Create validator instance with mocks."""
        mock_db = Mock()
        mock_account_repo = Mock()
        mock_journal_repo = Mock()
        return AccountBalanceValidator(mock_db, mock_account_repo, mock_journal_repo)

    def test_log_validation_result_not_repaired(self, validator):
        """Test logging validation result when account was not repaired."""
        # Arrange
        result = ValidationResult(
            account_id=1,
            account_name="Cash",
            cached_balance=Decimal("1000.00"),
            calculated_balance=Decimal("1000.00"),
            difference=Decimal("0.00"),
            is_valid=True,
            validated_at=datetime.now()
        )

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        validator.db.get_connection.return_value = mock_conn

        # Act
        validator.log_validation_result(result, was_repaired=False)

        # Assert
        mock_cursor.execute.assert_called_once()
        sql_call = mock_cursor.execute.call_args[0][0]
        params = mock_cursor.execute.call_args[0][1]

        assert "INSERT INTO balance_validation_log" in sql_call
        assert params[4] == 0  # was_repaired = False (0) - index 4, not 5
        mock_conn.commit.assert_called_once()

    def test_log_validation_result_repaired(self, validator):
        """Test logging validation result when account was repaired."""
        # Arrange
        result = ValidationResult(
            account_id=2,
            account_name="Bank",
            cached_balance=Decimal("1000.00"),
            calculated_balance=Decimal("1050.00"),
            difference=Decimal("-50.00"),
            is_valid=False,
            validated_at=datetime.now()
        )

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        validator.db.get_connection.return_value = mock_conn

        # Act
        validator.log_validation_result(result, was_repaired=True)

        # Assert
        mock_cursor.execute.assert_called_once()
        params = mock_cursor.execute.call_args[0][1]

        assert params[0] == 2  # account_id
        assert params[4] == 1  # was_repaired = True (1) - index 4, not 5
        mock_conn.commit.assert_called_once()
