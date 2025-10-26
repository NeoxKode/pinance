"""
Unit tests for AccountService opening balance methods.

Story: US-005 - Opening Balance Equity

Test Coverage:
- ensure_opening_balance_equity_account() method (3 tests)
- create_account_with_opening_balance() method (6 tests)
- set_account_opening_balance() method (5 tests)
- validate_opening_balance_equity() method (4 tests)
- get_opening_balance_summary() method (4 tests)

Total: 22 tests (exceeds 20+ target)
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime

from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance,
    JournalEntry, EntryType, Transaction, ReconciliationStatus
)
from finance_app.business.account_service import AccountService
from finance_app.data.database import Database
from finance_app.utils.exceptions import ValidationError, NotFoundError


class TestEnsureOpeningBalanceEquityAccount:
    """Test ensure_opening_balance_equity_account() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return AccountService(mock_db)

    def test_returns_existing_equity_account(self, service):
        """Test that existing Opening Balance Equity account is returned."""
        # Mock existing equity account
        equity_account = Account(
            id=999,
            name="Opening Balance Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubtype.OPENING_BALANCE,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.CREDIT
        )

        other_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )

        with patch.object(service.account_repo, 'get_all', return_value=[other_account, equity_account]):
            result = service.ensure_opening_balance_equity_account()

            assert result.id == 999
            assert result.name == "Opening Balance Equity"
            assert result.account_type == AccountType.EQUITY

    def test_creates_new_equity_account_if_not_exists(self, service):
        """Test that new Opening Balance Equity account is created if it doesn't exist."""
        other_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )

        new_equity_account = Account(
            id=999,
            name="Opening Balance Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubtype.OPENING_BALANCE,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.CREDIT
        )

        with patch.object(service.account_repo, 'get_all', return_value=[other_account]), \
             patch.object(service, 'create_account', return_value=new_equity_account):

            result = service.ensure_opening_balance_equity_account()

            assert result.name == "Opening Balance Equity"
            assert result.account_type == AccountType.EQUITY
            service.create_account.assert_called_once_with(
                name="Opening Balance Equity",
                account_type=AccountType.EQUITY,
                account_subtype=AccountSubtype.OPENING_BALANCE,
                initial_balance="0.00",
                currency="USD"
            )

    def test_returns_same_account_when_called_multiple_times(self, service):
        """Test that calling method multiple times returns the same account."""
        equity_account = Account(
            id=999,
            name="Opening Balance Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubtype.OPENING_BALANCE,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.CREDIT
        )

        with patch.object(service.account_repo, 'get_all', return_value=[equity_account]):
            result1 = service.ensure_opening_balance_equity_account()
            result2 = service.ensure_opening_balance_equity_account()

            assert result1.id == result2.id == 999


class TestCreateAccountWithOpeningBalance:
    """Test create_account_with_opening_balance() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database with transaction and connection support."""
        mock = MagicMock()

        # Mock transaction context manager
        mock_transaction = MagicMock()
        mock_transaction.__enter__ = Mock()
        mock_transaction.__exit__ = Mock(return_value=False)
        mock.transaction.return_value = mock_transaction

        # Mock get_connection context manager (needed for validate_opening_balance_equity)
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []  # Default empty result
        mock_connection.cursor.return_value = mock_cursor

        mock_connection_cm = MagicMock()
        mock_connection_cm.__enter__ = Mock(return_value=mock_connection)
        mock_connection_cm.__exit__ = Mock(return_value=None)
        mock.get_connection.return_value = mock_connection_cm

        return mock

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return AccountService(mock_db)

    def test_create_account_with_zero_opening_balance(self, service):
        """Test creating account with zero opening balance (no journal entries)."""
        new_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            opening_balance_date=None
        )

        with patch.object(service, 'create_account', return_value=new_account), \
             patch.object(service.account_repo, 'update', return_value=new_account) as mock_update:

            result, journal_entry = service.create_account_with_opening_balance(
                name="Checking",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                opening_balance=Decimal("0.00"),
                opening_date="2025-01-01"
            )

            assert result.name == "Checking"
            assert journal_entry is None
            # Verify opening_balance_date was set
            mock_update.assert_called_once()
            updated_account = mock_update.call_args[0][0]
            assert updated_account.opening_balance_date == "2025-01-01"

    def test_create_asset_account_with_opening_balance(self, service):
        """Test creating asset account with positive opening balance."""
        new_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT
        )

        equity_account = Account(
            id=999,
            name="Opening Balance Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubtype.OPENING_BALANCE,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.CREDIT
        )

        account_journal = JournalEntry(
            id=1,
            account_id=1,
            entry_date="2025-01-01",
            description="Opening balance for Checking",
            debit_amount=Decimal("5000.00"),
            credit_amount=Decimal("0.00"),
            balance_after=Decimal("5000.00"),
            entry_type=EntryType.OPENING_BALANCE
        )

        equity_journal = JournalEntry(
            id=2,
            account_id=999,
            entry_date="2025-01-01",
            description="Opening balance offset for Checking",
            debit_amount=Decimal("0.00"),
            credit_amount=Decimal("5000.00"),
            balance_after=Decimal("5000.00"),
            entry_type=EntryType.OPENING_BALANCE
        )

        with patch.object(service, 'create_account', return_value=new_account), \
             patch.object(service, 'ensure_opening_balance_equity_account', return_value=equity_account), \
             patch.object(service.double_entry_service, 'create_simple_transaction', side_effect=[account_journal, equity_journal]), \
             patch.object(service.transaction_repo, 'create'), \
             patch.object(service.account_repo, 'get_by_id', return_value=new_account), \
             patch.object(service.account_repo, 'update', return_value=new_account), \
             patch.object(service, 'validate_opening_balance_equity'):

            result, journal_entry = service.create_account_with_opening_balance(
                name="Checking",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                opening_balance=Decimal("5000.00"),
                opening_date="2025-01-01"
            )

            assert result.name == "Checking"
            assert journal_entry.id == 1
            # Verify DoubleEntryService was called for both entries
            assert service.double_entry_service.create_simple_transaction.call_count == 2

    def test_create_liability_account_with_opening_balance(self, service):
        """Test creating liability account with opening balance."""
        new_account = Account(
            id=2,
            name="Credit Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.CREDIT
        )

        equity_account = Account(
            id=999,
            name="Opening Balance Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubtype.OPENING_BALANCE,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.CREDIT
        )

        with patch.object(service, 'create_account', return_value=new_account), \
             patch.object(service, 'ensure_opening_balance_equity_account', return_value=equity_account), \
             patch.object(service.double_entry_service, 'create_simple_transaction'), \
             patch.object(service.transaction_repo, 'create'), \
             patch.object(service.account_repo, 'get_by_id', return_value=new_account), \
             patch.object(service.account_repo, 'update', return_value=new_account), \
             patch.object(service, 'validate_opening_balance_equity'):

            result, journal_entry = service.create_account_with_opening_balance(
                name="Credit Card",
                account_type=AccountType.LIABILITY,
                account_subtype=AccountSubtype.CREDIT_CARD,
                opening_balance=Decimal("2000.00"),
                opening_date="2025-01-01"
            )

            assert result.name == "Credit Card"

    def test_raises_validation_error_for_negative_opening_balance(self, service):
        """Test that negative opening balance raises ValidationError."""
        with pytest.raises(ValidationError, match="Opening balance must be non-negative"):
            service.create_account_with_opening_balance(
                name="Checking",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                opening_balance=Decimal("-100.00"),
                opening_date="2025-01-01"
            )

    def test_creates_transaction_with_is_opening_balance_flag(self, service):
        """Test that transaction is created with is_opening_balance=True."""
        new_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT
        )

        equity_account = Account(
            id=999,
            name="Opening Balance Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubtype.OPENING_BALANCE,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.CREDIT
        )

        with patch.object(service, 'create_account', return_value=new_account), \
             patch.object(service, 'ensure_opening_balance_equity_account', return_value=equity_account), \
             patch.object(service.double_entry_service, 'create_simple_transaction'), \
             patch.object(service.transaction_repo, 'create') as mock_create_txn, \
             patch.object(service.account_repo, 'get_by_id', return_value=new_account), \
             patch.object(service.account_repo, 'update', return_value=new_account), \
             patch.object(service, 'validate_opening_balance_equity'):

            service.create_account_with_opening_balance(
                name="Checking",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                opening_balance=Decimal("1000.00"),
                opening_date="2025-01-01"
            )

            # Verify transaction was created with is_opening_balance=True
            mock_create_txn.assert_called_once()
            created_transaction = mock_create_txn.call_args[0][0]
            assert created_transaction.is_opening_balance is True
            assert created_transaction.reconciliation_status == ReconciliationStatus.CLEARED

    def test_validates_accounting_equation_after_creation(self, service):
        """Test that accounting equation is validated after creating opening balance."""
        new_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT
        )

        equity_account = Account(
            id=999,
            name="Opening Balance Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubtype.OPENING_BALANCE,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.CREDIT
        )

        with patch.object(service, 'create_account', return_value=new_account), \
             patch.object(service, 'ensure_opening_balance_equity_account', return_value=equity_account), \
             patch.object(service.double_entry_service, 'create_simple_transaction'), \
             patch.object(service.transaction_repo, 'create'), \
             patch.object(service.account_repo, 'get_by_id', return_value=new_account), \
             patch.object(service.account_repo, 'update', return_value=new_account), \
             patch.object(service, 'validate_opening_balance_equity') as mock_validate:

            service.create_account_with_opening_balance(
                name="Checking",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                opening_balance=Decimal("1000.00"),
                opening_date="2025-01-01"
            )

            # Verify validation was called
            mock_validate.assert_called_once()


class TestSetAccountOpeningBalance:
    """Test set_account_opening_balance() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database with transaction support."""
        mock = Mock(spec=Database)
        mock.transaction = MagicMock()
        mock.transaction.return_value.__enter__ = Mock()
        mock.transaction.return_value.__exit__ = Mock(return_value=False)
        return mock

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return AccountService(mock_db)

    def test_set_opening_balance_for_existing_account(self, service):
        """Test setting opening balance for an existing account."""
        existing_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            opening_balance_date=None
        )

        equity_account = Account(
            id=999,
            name="Opening Balance Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubtype.OPENING_BALANCE,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.CREDIT
        )

        journal_entry = JournalEntry(
            id=1,
            account_id=1,
            entry_date="2025-01-01",
            description="Opening balance for Checking",
            debit_amount=Decimal("3000.00"),
            credit_amount=Decimal("0.00"),
            balance_after=Decimal("3000.00"),
            entry_type=EntryType.OPENING_BALANCE
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=existing_account), \
             patch.object(service, 'ensure_opening_balance_equity_account', return_value=equity_account), \
             patch.object(service.double_entry_service, 'create_simple_transaction', return_value=journal_entry), \
             patch.object(service.transaction_repo, 'create'), \
             patch.object(service.account_repo, 'update'), \
             patch.object(service, 'validate_opening_balance_equity'):

            result = service.set_account_opening_balance(
                account_id=1,
                opening_balance=Decimal("3000.00"),
                opening_date="2025-01-01"
            )

            assert result.id == 1

    def test_raises_not_found_error_for_nonexistent_account(self, service):
        """Test that NotFoundError is raised for nonexistent account."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Account 999 not found"):
                service.set_account_opening_balance(
                    account_id=999,
                    opening_balance=Decimal("1000.00"),
                    opening_date="2025-01-01"
                )

    def test_raises_validation_error_if_opening_balance_already_set(self, service):
        """Test that ValidationError is raised if opening balance already set."""
        existing_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("5000.00"),
            normal_balance=NormalBalance.DEBIT,
            opening_balance_date="2025-01-01"  # Already set
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=existing_account):
            with pytest.raises(ValidationError, match="already has opening balance set"):
                service.set_account_opening_balance(
                    account_id=1,
                    opening_balance=Decimal("1000.00"),
                    opening_date="2025-01-01"
                )

    def test_raises_validation_error_for_negative_opening_balance(self, service):
        """Test that negative opening balance raises ValidationError."""
        existing_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            opening_balance_date=None
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=existing_account):
            with pytest.raises(ValidationError, match="Opening balance must be non-negative"):
                service.set_account_opening_balance(
                    account_id=1,
                    opening_balance=Decimal("-100.00"),
                    opening_date="2025-01-01"
                )

    def test_handles_zero_opening_balance_without_journal_entries(self, service):
        """Test that zero opening balance sets date but creates no journal entries."""
        existing_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            opening_balance_date=None
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=existing_account), \
             patch.object(service.account_repo, 'update') as mock_update:

            result = service.set_account_opening_balance(
                account_id=1,
                opening_balance=Decimal("0.00"),
                opening_date="2025-01-01"
            )

            assert result is None
            # Verify opening_balance_date was set
            mock_update.assert_called_once()
            updated_account = mock_update.call_args[0][0]
            assert updated_account.opening_balance_date == "2025-01-01"


class TestValidateOpeningBalanceEquity:
    """Test validate_opening_balance_equity() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database with connection support."""
        mock = Mock(spec=Database)
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock.get_connection.return_value.__exit__ = Mock(return_value=False)
        return mock, mock_cursor

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        db, _ = mock_db
        return AccountService(db)

    def test_validates_balanced_equation(self, service, mock_db):
        """Test that balanced equation passes validation."""
        _, mock_cursor = mock_db

        # Mock SQL results: Assets=$15000, Liabilities=$2000, Equity=$13000
        mock_cursor.fetchall.return_value = [
            ('asset', 15000.00),
            ('liability', 2000.00),
            ('equity', 13000.00)
        ]

        result = service.validate_opening_balance_equity()

        assert result is True

    def test_validates_zero_balances(self, service, mock_db):
        """Test that zero balances pass validation."""
        _, mock_cursor = mock_db

        # Mock SQL results: All zeros
        mock_cursor.fetchall.return_value = [
            ('asset', 0.00),
            ('liability', 0.00),
            ('equity', 0.00)
        ]

        result = service.validate_opening_balance_equity()

        assert result is True

    def test_raises_validation_error_for_unbalanced_equation(self, service, mock_db):
        """Test that unbalanced equation raises ValidationError."""
        _, mock_cursor = mock_db

        # Mock SQL results: Assets=$15000, Liabilities=$2000, Equity=$10000 (off by $3000)
        mock_cursor.fetchall.return_value = [
            ('asset', 15000.00),
            ('liability', 2000.00),
            ('equity', 10000.00)
        ]

        with pytest.raises(ValidationError, match="Accounting equation does not balance"):
            service.validate_opening_balance_equity()

    def test_uses_sql_aggregation_for_performance(self, service, mock_db):
        """Test that method uses SQL aggregation instead of fetching all accounts."""
        db, mock_cursor = mock_db

        mock_cursor.fetchall.return_value = [
            ('asset', 5000.00),
            ('liability', 1000.00),
            ('equity', 4000.00)
        ]

        service.validate_opening_balance_equity()

        # Verify SQL query used GROUP BY aggregation
        executed_query = mock_cursor.execute.call_args[0][0]
        assert 'GROUP BY' in executed_query
        assert 'SUM(balance)' in executed_query


class TestGetOpeningBalanceSummary:
    """Test get_opening_balance_summary() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return AccountService(mock_db)

    def test_returns_summary_for_accounts_with_opening_balances(self, service):
        """Test that summary includes only accounts with opening balances."""
        account1 = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("5000.00"),
            normal_balance=NormalBalance.DEBIT,
            opening_balance_date="2025-01-01"
        )

        account2 = Account(
            id=2,
            name="Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            balance=Decimal("10000.00"),
            normal_balance=NormalBalance.DEBIT,
            opening_balance_date="2025-01-01"
        )

        account3 = Account(
            id=3,
            name="New Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            opening_balance_date=None  # No opening balance
        )

        with patch.object(service.account_repo, 'get_all', return_value=[account1, account2, account3]):
            summary = service.get_opening_balance_summary()

            assert summary['total_accounts'] == 2
            assert summary['total_amount'] == Decimal("15000.00")
            assert len(summary['accounts']) == 2

    def test_returns_empty_summary_when_no_opening_balances(self, service):
        """Test that empty summary is returned when no accounts have opening balances."""
        account1 = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT,
            opening_balance_date=None
        )

        with patch.object(service.account_repo, 'get_all', return_value=[account1]):
            summary = service.get_opening_balance_summary()

            assert summary['total_accounts'] == 0
            assert summary['total_amount'] == Decimal("0.00")
            assert summary['by_type'] == {}

    def test_groups_accounts_by_type(self, service):
        """Test that accounts are grouped by account type."""
        asset_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("5000.00"),
            normal_balance=NormalBalance.DEBIT,
            opening_balance_date="2025-01-01"
        )

        liability_account = Account(
            id=2,
            name="Credit Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            balance=Decimal("2000.00"),
            normal_balance=NormalBalance.CREDIT,
            opening_balance_date="2025-01-01"
        )

        with patch.object(service.account_repo, 'get_all', return_value=[asset_account, liability_account]):
            summary = service.get_opening_balance_summary()

            assert 'asset' in summary['by_type']
            assert 'liability' in summary['by_type']
            assert summary['by_type']['asset']['count'] == 1
            assert summary['by_type']['liability']['count'] == 1
            assert summary['by_type']['asset']['total'] == Decimal("5000.00")
            assert summary['by_type']['liability']['total'] == Decimal("2000.00")

    def test_includes_account_details_in_summary(self, service):
        """Test that account details are included in summary."""
        account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("5000.00"),
            normal_balance=NormalBalance.DEBIT,
            opening_balance_date="2025-01-01"
        )

        with patch.object(service.account_repo, 'get_all', return_value=[account]):
            summary = service.get_opening_balance_summary()

            asset_accounts = summary['by_type']['asset']['accounts']
            assert len(asset_accounts) == 1
            assert asset_accounts[0]['id'] == 1
            assert asset_accounts[0]['name'] == "Checking"
            assert asset_accounts[0]['balance'] == Decimal("5000.00")
            assert asset_accounts[0]['opening_date'] == "2025-01-01"
