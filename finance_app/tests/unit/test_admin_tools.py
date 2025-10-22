"""
Unit tests for AdminTools.

Story: US-002A - Journal Entry Foundation
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
from finance_app.utils.admin_tools import AdminTools, BalanceValidationResult
from finance_app.data.database import Database


class TestBalanceValidationResult:
    """Test BalanceValidationResult dataclass."""

    def test_result_with_valid_balance(self):
        """Test result when balances match."""
        result = BalanceValidationResult(
            account_id=1,
            account_name="Checking",
            account_balance=Decimal("1000.00"),
            journal_balance=Decimal("1000.00"),
            difference=Decimal("0"),
            is_valid=True
        )

        assert result.account_id == 1
        assert result.account_name == "Checking"
        assert result.is_valid is True
        assert result.difference == Decimal("0")

    def test_result_with_invalid_balance(self):
        """Test result when balances don't match."""
        result = BalanceValidationResult(
            account_id=2,
            account_name="Savings",
            account_balance=Decimal("500.00"),
            journal_balance=Decimal("450.00"),
            difference=Decimal("50.00"),
            is_valid=False
        )

        assert result.account_id == 2
        assert result.is_valid is False
        assert result.difference == Decimal("50.00")


class TestAdminToolsValidateAccountBalance:
    """Test validate_account_balance method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def admin_tools(self, mock_db):
        """Create admin tools with mocked dependencies."""
        with patch('finance_app.utils.admin_tools.AccountRepository'), \
             patch('finance_app.utils.admin_tools.JournalEntryRepository'), \
             patch('finance_app.utils.admin_tools.DoubleEntryService'):
            return AdminTools(mock_db)

    def test_validate_matching_balance(self, admin_tools):
        """Test validation when balances match."""
        mock_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        admin_tools.account_repo.get_by_id = Mock(return_value=mock_account)
        admin_tools.journal_repo.get_account_balance = Mock(return_value=Decimal("1000.00"))

        result = admin_tools.validate_account_balance(account_id=1)

        assert result.is_valid is True
        assert result.difference == Decimal("0")
        assert result.account_balance == Decimal("1000.00")
        assert result.journal_balance == Decimal("1000.00")

    def test_validate_mismatched_balance(self, admin_tools):
        """Test validation when balances don't match."""
        mock_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        admin_tools.account_repo.get_by_id = Mock(return_value=mock_account)
        admin_tools.journal_repo.get_account_balance = Mock(return_value=Decimal("950.00"))

        result = admin_tools.validate_account_balance(account_id=1)

        assert result.is_valid is False
        assert result.difference == Decimal("50.00")
        assert result.account_balance == Decimal("1000.00")
        assert result.journal_balance == Decimal("950.00")

    def test_validate_within_tolerance(self, admin_tools):
        """Test validation when difference is within tolerance."""
        mock_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        admin_tools.account_repo.get_by_id = Mock(return_value=mock_account)
        # 0.005 difference (< 0.01 tolerance)
        admin_tools.journal_repo.get_account_balance = Mock(return_value=Decimal("1000.005"))

        result = admin_tools.validate_account_balance(account_id=1, tolerance=Decimal("0.01"))

        assert result.is_valid is True
        assert result.difference == Decimal("0.005")

    def test_validate_outside_tolerance(self, admin_tools):
        """Test validation when difference exceeds tolerance."""
        mock_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        admin_tools.account_repo.get_by_id = Mock(return_value=mock_account)
        # 5.00 difference (> 0.01 tolerance)
        admin_tools.journal_repo.get_account_balance = Mock(return_value=Decimal("1005.00"))

        result = admin_tools.validate_account_balance(account_id=1, tolerance=Decimal("0.01"))

        assert result.is_valid is False
        assert result.difference == Decimal("5.00")

    def test_validate_nonexistent_account_raises_error(self, admin_tools):
        """Test that validating non-existent account raises ValueError."""
        admin_tools.account_repo.get_by_id = Mock(return_value=None)

        with pytest.raises(ValueError, match="Account 999 not found"):
            admin_tools.validate_account_balance(account_id=999)


class TestAdminToolsValidateAllAccountBalances:
    """Test validate_all_account_balances method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def admin_tools(self, mock_db):
        """Create admin tools with mocked dependencies."""
        with patch('finance_app.utils.admin_tools.AccountRepository'), \
             patch('finance_app.utils.admin_tools.JournalEntryRepository'), \
             patch('finance_app.utils.admin_tools.DoubleEntryService'):
            return AdminTools(mock_db)

    def test_validate_all_with_all_valid(self, admin_tools):
        """Test validate all when all accounts are valid."""
        mock_accounts = [
            Account(
                id=1, name="Checking", account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                balance=Decimal("1000.00"), normal_balance=NormalBalance.DEBIT
            ),
            Account(
                id=2, name="Savings", account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.SAVINGS,
                balance=Decimal("5000.00"), normal_balance=NormalBalance.DEBIT
            )
        ]
        admin_tools.account_repo.get_all = Mock(return_value=mock_accounts)
        admin_tools.account_repo.get_by_id = Mock(side_effect=lambda id: mock_accounts[id - 1])
        admin_tools.journal_repo.get_account_balance = Mock(
            side_effect=lambda id: mock_accounts[id - 1].balance
        )

        results = admin_tools.validate_all_account_balances()

        assert len(results) == 2
        assert all(r.is_valid for r in results)

    def test_validate_all_with_some_invalid(self, admin_tools):
        """Test validate all when some accounts are invalid."""
        mock_accounts = [
            Account(
                id=1, name="Checking", account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                balance=Decimal("1000.00"), normal_balance=NormalBalance.DEBIT
            ),
            Account(
                id=2, name="Savings", account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.SAVINGS,
                balance=Decimal("5000.00"), normal_balance=NormalBalance.DEBIT
            )
        ]
        admin_tools.account_repo.get_all = Mock(return_value=mock_accounts)
        admin_tools.account_repo.get_by_id = Mock(side_effect=lambda id: mock_accounts[id - 1])
        # First account matches, second doesn't
        admin_tools.journal_repo.get_account_balance = Mock(
            side_effect=lambda id: Decimal("1000.00") if id == 1 else Decimal("4950.00")
        )

        results = admin_tools.validate_all_account_balances()

        assert len(results) == 2
        assert results[0].is_valid is True
        assert results[1].is_valid is False
        assert results[1].difference == Decimal("50.00")


class TestAdminToolsReconcileAccountBalance:
    """Test reconcile_account_balance method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def admin_tools(self, mock_db):
        """Create admin tools with mocked dependencies."""
        with patch('finance_app.utils.admin_tools.AccountRepository'), \
             patch('finance_app.utils.admin_tools.JournalEntryRepository'), \
             patch('finance_app.utils.admin_tools.DoubleEntryService'):
            return AdminTools(mock_db)

    def test_reconcile_updates_balance(self, admin_tools):
        """Test that reconcile updates account balance to match journal."""
        mock_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        admin_tools.account_repo.get_by_id = Mock(return_value=mock_account)
        admin_tools.journal_repo.get_account_balance = Mock(return_value=Decimal("950.00"))
        admin_tools.account_repo.update_balance = Mock()

        old_balance, new_balance = admin_tools.reconcile_account_balance(account_id=1)

        assert old_balance == Decimal("1000.00")
        assert new_balance == Decimal("950.00")
        # Should update by difference: 950 - 1000 = -50
        admin_tools.account_repo.update_balance.assert_called_once_with(1, Decimal("-50.00"))

    def test_reconcile_nonexistent_account_raises_error(self, admin_tools):
        """Test that reconciling non-existent account raises ValueError."""
        admin_tools.account_repo.get_by_id = Mock(return_value=None)

        with pytest.raises(ValueError, match="Account 999 not found"):
            admin_tools.reconcile_account_balance(account_id=999)


class TestAdminToolsGetValidationSummary:
    """Test get_validation_summary method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def admin_tools(self, mock_db):
        """Create admin tools with mocked dependencies."""
        with patch('finance_app.utils.admin_tools.AccountRepository'), \
             patch('finance_app.utils.admin_tools.JournalEntryRepository'), \
             patch('finance_app.utils.admin_tools.DoubleEntryService'):
            return AdminTools(mock_db)

    def test_summary_all_valid(self, admin_tools):
        """Test summary when all accounts are valid."""
        results = [
            BalanceValidationResult(
                account_id=1, account_name="Checking",
                account_balance=Decimal("1000.00"), journal_balance=Decimal("1000.00"),
                difference=Decimal("0"), is_valid=True
            ),
            BalanceValidationResult(
                account_id=2, account_name="Savings",
                account_balance=Decimal("5000.00"), journal_balance=Decimal("5000.00"),
                difference=Decimal("0"), is_valid=True
            )
        ]

        summary = admin_tools.get_validation_summary(results)

        assert summary["total_accounts"] == 2
        assert summary["valid_accounts"] == 2
        assert summary["invalid_accounts"] == 0
        assert summary["valid_percentage"] == 100.0
        assert summary["total_difference"] == "0"
        assert summary["max_difference"] == "0"
        assert len(summary["invalid_details"]) == 0

    def test_summary_some_invalid(self, admin_tools):
        """Test summary when some accounts are invalid."""
        results = [
            BalanceValidationResult(
                account_id=1, account_name="Checking",
                account_balance=Decimal("1000.00"), journal_balance=Decimal("1000.00"),
                difference=Decimal("0"), is_valid=True
            ),
            BalanceValidationResult(
                account_id=2, account_name="Savings",
                account_balance=Decimal("5000.00"), journal_balance=Decimal("4950.00"),
                difference=Decimal("50.00"), is_valid=False
            )
        ]

        summary = admin_tools.get_validation_summary(results)

        assert summary["total_accounts"] == 2
        assert summary["valid_accounts"] == 1
        assert summary["invalid_accounts"] == 1
        assert summary["valid_percentage"] == 50.0
        assert summary["total_difference"] == "50.00"
        assert summary["max_difference"] == "50.00"
        assert len(summary["invalid_details"]) == 1
        assert summary["invalid_details"][0]["account_id"] == 2
