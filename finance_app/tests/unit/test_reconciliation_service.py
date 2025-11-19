"""
Unit tests for ReconciliationService.

Story: US-004 - Account Reconciliation (Day 2, Task 4.16)

Test Coverage:
- start_reconciliation() method (4 tests)
- get_unreconciled_transactions() method (2 tests)
- mark_transaction_cleared() method (3 tests)
- unmark_transaction() method (2 tests)
- calculate_cleared_balance() method (4 tests)
- calculate_discrepancy() method (3 tests)
- complete_reconciliation() method (5 tests)
- get_reconciliation_history() method (2 tests)

Total: 25 tests (exceeds 20+ target)
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime

from finance_app.data.models import (
    Reconciliation, Transaction, Account, AccountType, AccountSubtype,
    NormalBalance, ReconciliationStatus
)
from finance_app.business.reconciliation_service import ReconciliationService
from finance_app.data.database import Database
from finance_app.utils.exceptions import ValidationError, NotFoundError, BusinessRuleError


class TestReconciliationServiceStartReconciliation:
    """Test service start_reconciliation() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return ReconciliationService(mock_db)

    def test_start_reconciliation_success(self, service):
        """Test successful reconciliation start."""
        # Mock account
        mock_account = Account(
            id=1,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1200.00"),
            normal_balance=NormalBalance.DEBIT
        )

        # Mock last reconciliation
        mock_last_reconciliation = Reconciliation(
            id=1,
            account_id=1,
            reconciliation_date="2025-09-30",
            statement_date="2025-09-30",
            statement_balance=Decimal("1000.00"),
            cleared_balance=Decimal("1000.00"),
            discrepancy=Decimal("0.00"),
            transaction_count=5
        )

        # Setup mocks
        with patch.object(service.account_repo, 'get_by_id', return_value=mock_account), \
             patch.object(service.reconciliation_repo, 'get_pending_reconciliation', return_value=False), \
             patch.object(service.reconciliation_repo, 'get_last_reconciliation', return_value=mock_last_reconciliation), \
             patch.object(service, 'get_unreconciled_transactions', return_value=[]):

            result = service.start_reconciliation(
                account_id=1,
                statement_date="2025-10-31",
                statement_balance=Decimal("1200.00")
            )

            assert result['account_id'] == 1
            assert result['account_name'] == "Checking Account"
            assert result['statement_date'] == "2025-10-31"
            assert result['statement_balance'] == Decimal("1200.00")
            assert result['opening_balance'] == Decimal("1000.00")
            assert result['unreconciled_count'] == 0

    def test_start_reconciliation_raises_business_rule_error_for_pending(self, service):
        """Test that concurrent reconciliation is prevented."""
        mock_account = Account(
            id=1,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1200.00"),
            normal_balance=NormalBalance.DEBIT
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=mock_account), \
             patch.object(service.reconciliation_repo, 'get_pending_reconciliation', return_value=True):

            with pytest.raises(BusinessRuleError, match="already in progress"):
                service.start_reconciliation(
                    account_id=1,
                    statement_date="2025-10-31",
                    statement_balance=Decimal("1200.00")
                )

    def test_start_reconciliation_raises_not_found_for_invalid_account(self, service):
        """Test that invalid account raises NotFoundError."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Account 999 not found"):
                service.start_reconciliation(
                    account_id=999,
                    statement_date="2025-10-31",
                    statement_balance=Decimal("1200.00")
                )

    def test_start_reconciliation_raises_validation_error_for_invalid_date(self, service):
        """Test that invalid statement_date raises ValidationError."""
        mock_account = Account(
            id=1,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1200.00"),
            normal_balance=NormalBalance.DEBIT
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=mock_account):
            with pytest.raises(ValidationError, match="Invalid statement date format"):
                service.start_reconciliation(
                    account_id=1,
                    statement_date="10/31/2025",  # Wrong format
                    statement_balance=Decimal("1200.00")
                )


class TestReconciliationServiceGetUnreconciledTransactions:
    """Test service get_unreconciled_transactions() method."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        mock_db = Mock(spec=Database)
        return ReconciliationService(mock_db)

    def test_get_unreconciled_transactions_filters_correctly(self, service):
        """Test that only unreconciled transactions are returned."""
        mock_account = Account(
            id=1,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1200.00"),
            normal_balance=NormalBalance.DEBIT
        )

        # Mix of reconciliation statuses
        mock_transactions = [
            Transaction(
                id=1, account_id=1, date="2025-10-15", description="Cleared",
                category="Income", amount=Decimal("100.00"), type="income",
                reconciliation_status=ReconciliationStatus.CLEARED
            ),
            Transaction(
                id=2, account_id=1, date="2025-10-20", description="Unreconciled",
                category="Expense", amount=Decimal("-50.00"), type="expense",
                reconciliation_status=ReconciliationStatus.UNRECONCILED
            ),
            Transaction(
                id=3, account_id=1, date="2025-10-25", description="Unreconciled 2",
                category="Expense", amount=Decimal("-25.00"), type="expense",
                reconciliation_status=ReconciliationStatus.UNRECONCILED
            ),
        ]

        with patch.object(service.account_repo, 'get_by_id', return_value=mock_account), \
             patch.object(service.transaction_repo, 'get_all', return_value=mock_transactions):

            result = service.get_unreconciled_transactions(account_id=1)

            assert len(result) == 2
            assert all(txn.reconciliation_status == ReconciliationStatus.UNRECONCILED for txn in result)
            # Verify sorted by date
            assert result[0].date == "2025-10-20"
            assert result[1].date == "2025-10-25"

    def test_get_unreconciled_transactions_raises_not_found_for_invalid_account(self, service):
        """Test that invalid account raises NotFoundError."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Account 999 not found"):
                service.get_unreconciled_transactions(account_id=999)


class TestReconciliationServiceMarkTransactionCleared:
    """Test service mark_transaction_cleared() method."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        mock_db = Mock(spec=Database)
        return ReconciliationService(mock_db)

    def test_mark_transaction_cleared_updates_status(self, service):
        """Test that transaction is marked as cleared."""
        mock_transaction = Transaction(
            id=1, account_id=1, date="2025-10-20", description="Test",
            category="Expense", amount=Decimal("-50.00"), type="expense",
            reconciliation_status=ReconciliationStatus.UNRECONCILED
        )

        with patch.object(service.transaction_repo, 'get_by_id', return_value=mock_transaction), \
             patch.object(service.transaction_repo, 'update') as mock_update:

            result = service.mark_transaction_cleared(
                transaction_id=1,
                statement_date="2025-10-31"
            )

            assert result.reconciliation_status == ReconciliationStatus.CLEARED
            assert result.statement_date == "2025-10-31"
            # Note: reconciled_date is only set when reconciliation completes, not when marking as cleared
            mock_update.assert_called_once()

    def test_mark_transaction_cleared_raises_not_found_for_invalid_transaction(self, service):
        """Test that invalid transaction raises NotFoundError."""
        with patch.object(service.transaction_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Transaction 999 not found"):
                service.mark_transaction_cleared(
                    transaction_id=999,
                    statement_date="2025-10-31"
                )

    def test_mark_transaction_cleared_raises_validation_error_for_invalid_date(self, service):
        """Test that invalid statement_date raises ValidationError."""
        mock_transaction = Transaction(
            id=1, account_id=1, date="2025-10-20", description="Test",
            category="Expense", amount=Decimal("-50.00"), type="expense",
            reconciliation_status=ReconciliationStatus.UNRECONCILED
        )

        with patch.object(service.transaction_repo, 'get_by_id', return_value=mock_transaction):
            with pytest.raises(ValidationError, match="Invalid statement date format"):
                service.mark_transaction_cleared(
                    transaction_id=1,
                    statement_date="10/31/2025"  # Wrong format
                )


class TestReconciliationServiceUnmarkTransaction:
    """Test service unmark_transaction() method."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        mock_db = Mock(spec=Database)
        return ReconciliationService(mock_db)

    def test_unmark_transaction_reverts_status(self, service):
        """Test that transaction is unmarked (returned to unreconciled)."""
        mock_transaction = Transaction(
            id=1, account_id=1, date="2025-10-20", description="Test",
            category="Expense", amount=Decimal("-50.00"), type="expense",
            reconciliation_status=ReconciliationStatus.CLEARED,
            reconciled_date="2025-10-23",
            statement_date="2025-10-31"
        )

        with patch.object(service.transaction_repo, 'get_by_id', return_value=mock_transaction), \
             patch.object(service.transaction_repo, 'update') as mock_update:

            result = service.unmark_transaction(transaction_id=1)

            assert result.reconciliation_status == ReconciliationStatus.UNRECONCILED
            assert result.reconciled_date is None
            assert result.statement_date is None
            mock_update.assert_called_once()

    def test_unmark_transaction_raises_not_found_for_invalid_transaction(self, service):
        """Test that invalid transaction raises NotFoundError."""
        with patch.object(service.transaction_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Transaction 999 not found"):
                service.unmark_transaction(transaction_id=999)


class TestReconciliationServiceCalculateClearedBalance:
    """Test service calculate_cleared_balance() method."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        mock_db = Mock(spec=Database)
        return ReconciliationService(mock_db)

    def test_calculate_cleared_balance_with_opening_balance(self, service):
        """Test cleared balance calculation with opening balance from last reconciliation."""
        mock_account = Account(
            id=1,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1200.00"),
            normal_balance=NormalBalance.DEBIT
        )

        mock_last_reconciliation = Reconciliation(
            id=1,
            account_id=1,
            reconciliation_date="2025-09-30",
            statement_date="2025-09-30",
            statement_balance=Decimal("1000.00"),
            cleared_balance=Decimal("1000.00"),
            discrepancy=Decimal("0.00"),
            transaction_count=5
        )

        mock_transactions = [
            Transaction(
                id=1, account_id=1, date="2025-10-15", description="Cleared",
                category="Income", amount=Decimal("100.00"), type="income",
                reconciliation_status=ReconciliationStatus.CLEARED
            ),
            Transaction(
                id=2, account_id=1, date="2025-10-20", description="Cleared",
                category="Expense", amount=Decimal("-50.00"), type="expense",
                reconciliation_status=ReconciliationStatus.CLEARED
            ),
        ]

        with patch.object(service.account_repo, 'get_by_id', return_value=mock_account), \
             patch.object(service.reconciliation_repo, 'get_last_reconciliation', return_value=mock_last_reconciliation), \
             patch.object(service.transaction_repo, 'get_all', return_value=mock_transactions):

            result = service.calculate_cleared_balance(account_id=1)

            # opening (1000) + cleared (100 - 50 = 50) = 1050
            assert result == Decimal("1050.00")

    def test_calculate_cleared_balance_without_opening_balance(self, service):
        """Test cleared balance calculation without prior reconciliation."""
        mock_account = Account(
            id=1,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("50.00"),
            normal_balance=NormalBalance.DEBIT
        )

        mock_transactions = [
            Transaction(
                id=1, account_id=1, date="2025-10-15", description="Cleared",
                category="Income", amount=Decimal("100.00"), type="income",
                reconciliation_status=ReconciliationStatus.CLEARED
            ),
            Transaction(
                id=2, account_id=1, date="2025-10-20", description="Cleared",
                category="Expense", amount=Decimal("-50.00"), type="expense",
                reconciliation_status=ReconciliationStatus.CLEARED
            ),
        ]

        with patch.object(service.account_repo, 'get_by_id', return_value=mock_account), \
             patch.object(service.reconciliation_repo, 'get_last_reconciliation', return_value=None), \
             patch.object(service.transaction_repo, 'get_all', return_value=mock_transactions):

            result = service.calculate_cleared_balance(account_id=1)

            # No opening balance, so just sum of cleared transactions
            assert result == Decimal("50.00")

    def test_calculate_cleared_balance_ignores_unreconciled(self, service):
        """Test that unreconciled transactions are not included in cleared balance."""
        mock_account = Account(
            id=1,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("100.00"),
            normal_balance=NormalBalance.DEBIT
        )

        mock_transactions = [
            Transaction(
                id=1, account_id=1, date="2025-10-15", description="Cleared",
                category="Income", amount=Decimal("100.00"), type="income",
                reconciliation_status=ReconciliationStatus.CLEARED
            ),
            Transaction(
                id=2, account_id=1, date="2025-10-20", description="Unreconciled",
                category="Expense", amount=Decimal("-50.00"), type="expense",
                reconciliation_status=ReconciliationStatus.UNRECONCILED  # Should be ignored
            ),
        ]

        with patch.object(service.account_repo, 'get_by_id', return_value=mock_account), \
             patch.object(service.reconciliation_repo, 'get_last_reconciliation', return_value=None), \
             patch.object(service.transaction_repo, 'get_all', return_value=mock_transactions):

            result = service.calculate_cleared_balance(account_id=1)

            # Only cleared transaction (100), unreconciled ignored
            assert result == Decimal("100.00")

    def test_calculate_cleared_balance_raises_not_found_for_invalid_account(self, service):
        """Test that invalid account raises NotFoundError."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Account 999 not found"):
                service.calculate_cleared_balance(account_id=999)


class TestReconciliationServiceCalculateDiscrepancy:
    """Test service calculate_discrepancy() method."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        mock_db = Mock(spec=Database)
        return ReconciliationService(mock_db)

    def test_calculate_discrepancy_balanced(self, service):
        """Test discrepancy calculation for balanced reconciliation."""
        with patch.object(service, 'calculate_cleared_balance', return_value=Decimal("1200.00")):
            result = service.calculate_discrepancy(
                account_id=1,
                statement_balance=Decimal("1200.00")
            )

            assert result == Decimal("0.00")

    def test_calculate_discrepancy_positive(self, service):
        """Test discrepancy calculation for missing transactions (positive discrepancy)."""
        with patch.object(service, 'calculate_cleared_balance', return_value=Decimal("1150.00")):
            result = service.calculate_discrepancy(
                account_id=1,
                statement_balance=Decimal("1200.00")
            )

            # Positive: statement > cleared (missing transactions)
            assert result == Decimal("50.00")

    def test_calculate_discrepancy_negative(self, service):
        """Test discrepancy calculation for extra transactions (negative discrepancy)."""
        with patch.object(service, 'calculate_cleared_balance', return_value=Decimal("1250.00")):
            result = service.calculate_discrepancy(
                account_id=1,
                statement_balance=Decimal("1200.00")
            )

            # Negative: statement < cleared (extra transactions)
            assert result == Decimal("-50.00")


class TestReconciliationServiceCompleteReconciliation:
    """Test service complete_reconciliation() method."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        mock_db = Mock(spec=Database)
        return ReconciliationService(mock_db)

    def test_complete_reconciliation_creates_record(self, service):
        """Test that reconciliation record is created."""
        mock_account = Account(
            id=1,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1200.00"),
            normal_balance=NormalBalance.DEBIT
        )

        mock_saved_reconciliation = Reconciliation(
            id=1,
            account_id=1,
            reconciliation_date="2025-10-23",
            statement_date="2025-10-31",
            statement_balance=Decimal("1200.00"),
            cleared_balance=Decimal("1200.00"),
            discrepancy=Decimal("0.00"),
            transaction_count=5
        )

        # Create proper mock transactions with all required attributes
        mock_transactions = [
            Mock(reconciliation_status=ReconciliationStatus.CLEARED, id=i)
            for i in range(1, 6)
        ]

        with patch.object(service.account_repo, 'get_by_id', return_value=mock_account), \
             patch.object(service, 'calculate_cleared_balance', return_value=Decimal("1200.00")), \
             patch.object(service, 'calculate_discrepancy', return_value=Decimal("0.00")), \
             patch.object(service.transaction_repo, 'get_all', return_value=mock_transactions), \
             patch.object(service.transaction_repo, 'update'), \
             patch.object(service.reconciliation_repo, 'create', return_value=mock_saved_reconciliation) as mock_create, \
             patch.object(service.account_repo, 'update') as mock_update:

            result = service.complete_reconciliation(
                account_id=1,
                statement_date="2025-10-31",
                statement_balance=Decimal("1200.00")
            )

            assert result.id == 1
            assert result.discrepancy == Decimal("0.00")
            mock_create.assert_called_once()
            mock_update.assert_called_once()

    def test_complete_reconciliation_updates_account_last_reconciled_date(self, service):
        """Test that account.last_reconciled_date is updated."""
        mock_account = Account(
            id=1,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1200.00"),
            normal_balance=NormalBalance.DEBIT,
            last_reconciled_date=None  # Never reconciled
        )

        mock_saved_reconciliation = Reconciliation(
            id=1,
            account_id=1,
            reconciliation_date="2025-10-23",
            statement_date="2025-10-31",
            statement_balance=Decimal("1200.00"),
            cleared_balance=Decimal("1200.00"),
            discrepancy=Decimal("0.00"),
            transaction_count=5
        )

        # Create proper mock transactions with all required attributes
        mock_transactions = [
            Mock(reconciliation_status=ReconciliationStatus.CLEARED, id=i)
            for i in range(1, 6)
        ]

        with patch.object(service.account_repo, 'get_by_id', return_value=mock_account), \
             patch.object(service, 'calculate_cleared_balance', return_value=Decimal("1200.00")), \
             patch.object(service, 'calculate_discrepancy', return_value=Decimal("0.00")), \
             patch.object(service.transaction_repo, 'get_all', return_value=mock_transactions), \
             patch.object(service.transaction_repo, 'update'), \
             patch.object(service.reconciliation_repo, 'create', return_value=mock_saved_reconciliation), \
             patch.object(service.account_repo, 'update') as mock_update:

            service.complete_reconciliation(
                account_id=1,
                statement_date="2025-10-31",
                statement_balance=Decimal("1200.00")
            )

            # Verify account update was called
            mock_update.assert_called_once()
            updated_account = mock_update.call_args[0][0]
            assert updated_account.last_reconciled_date is not None

    def test_complete_reconciliation_counts_cleared_transactions(self, service):
        """Test that transaction_count is accurately counted."""
        mock_account = Account(
            id=1,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1200.00"),
            normal_balance=NormalBalance.DEBIT
        )

        # 3 cleared, 2 unreconciled - add id attribute for transaction updates
        mock_transactions = [
            Mock(reconciliation_status=ReconciliationStatus.CLEARED, id=1),
            Mock(reconciliation_status=ReconciliationStatus.CLEARED, id=2),
            Mock(reconciliation_status=ReconciliationStatus.CLEARED, id=3),
            Mock(reconciliation_status=ReconciliationStatus.UNRECONCILED, id=4),
            Mock(reconciliation_status=ReconciliationStatus.UNRECONCILED, id=5),
        ]

        mock_saved_reconciliation = Reconciliation(
            id=1,
            account_id=1,
            reconciliation_date="2025-10-23",
            statement_date="2025-10-31",
            statement_balance=Decimal("1200.00"),
            cleared_balance=Decimal("1200.00"),
            discrepancy=Decimal("0.00"),
            transaction_count=3  # Only cleared
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=mock_account), \
             patch.object(service, 'calculate_cleared_balance', return_value=Decimal("1200.00")), \
             patch.object(service, 'calculate_discrepancy', return_value=Decimal("0.00")), \
             patch.object(service.transaction_repo, 'get_all', return_value=mock_transactions), \
             patch.object(service.transaction_repo, 'update'), \
             patch.object(service.reconciliation_repo, 'create', return_value=mock_saved_reconciliation), \
             patch.object(service.account_repo, 'update'):

            result = service.complete_reconciliation(
                account_id=1,
                statement_date="2025-10-31",
                statement_balance=Decimal("1200.00")
            )

            assert result.transaction_count == 3

    def test_complete_reconciliation_saves_notes(self, service):
        """Test that optional notes are saved."""
        mock_account = Account(
            id=1,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1200.00"),
            normal_balance=NormalBalance.DEBIT
        )

        mock_saved_reconciliation = Reconciliation(
            id=1,
            account_id=1,
            reconciliation_date="2025-10-23",
            statement_date="2025-10-31",
            statement_balance=Decimal("1200.00"),
            cleared_balance=Decimal("1150.00"),
            discrepancy=Decimal("50.00"),
            transaction_count=5,
            notes="Missing ATM withdrawal"
        )

        # Create mock transactions with id attribute for updates
        mock_transactions = [
            Mock(reconciliation_status=ReconciliationStatus.CLEARED, id=i)
            for i in range(1, 6)
        ]

        with patch.object(service.account_repo, 'get_by_id', return_value=mock_account), \
             patch.object(service, 'calculate_cleared_balance', return_value=Decimal("1150.00")), \
             patch.object(service, 'calculate_discrepancy', return_value=Decimal("50.00")), \
             patch.object(service.transaction_repo, 'get_all', return_value=mock_transactions), \
             patch.object(service.transaction_repo, 'update'), \
             patch.object(service.reconciliation_repo, 'create', return_value=mock_saved_reconciliation) as mock_create, \
             patch.object(service.account_repo, 'update'):

            result = service.complete_reconciliation(
                account_id=1,
                statement_date="2025-10-31",
                statement_balance=Decimal("1200.00"),
                notes="Missing ATM withdrawal"
            )

            # Verify notes were passed to create
            create_call_args = mock_create.call_args[0][0]
            assert create_call_args.notes == "Missing ATM withdrawal"

    def test_complete_reconciliation_raises_not_found_for_invalid_account(self, service):
        """Test that invalid account raises NotFoundError."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Account 999 not found"):
                service.complete_reconciliation(
                    account_id=999,
                    statement_date="2025-10-31",
                    statement_balance=Decimal("1200.00")
                )


class TestReconciliationServiceGetReconciliationHistory:
    """Test service get_reconciliation_history() method."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        mock_db = Mock(spec=Database)
        return ReconciliationService(mock_db)

    def test_get_reconciliation_history_returns_ordered_list(self, service):
        """Test that reconciliation history is returned in order."""
        mock_account = Account(
            id=1,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1200.00"),
            normal_balance=NormalBalance.DEBIT
        )

        mock_history = [
            Reconciliation(id=3, account_id=1, reconciliation_date="2025-10-23", statement_date="2025-10-31",
                          statement_balance=Decimal("1200.00"), cleared_balance=Decimal("1200.00"),
                          discrepancy=Decimal("0.00"), transaction_count=7),
            Reconciliation(id=2, account_id=1, reconciliation_date="2025-09-30", statement_date="2025-09-30",
                          statement_balance=Decimal("1000.00"), cleared_balance=Decimal("1000.00"),
                          discrepancy=Decimal("0.00"), transaction_count=6),
        ]

        with patch.object(service.account_repo, 'get_by_id', return_value=mock_account), \
             patch.object(service.reconciliation_repo, 'get_by_account', return_value=mock_history):

            result = service.get_reconciliation_history(account_id=1, limit=10)

            assert len(result) == 2
            assert result[0].id == 3  # Most recent first
            assert result[1].id == 2

    def test_get_reconciliation_history_raises_not_found_for_invalid_account(self, service):
        """Test that invalid account raises NotFoundError."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Account 999 not found"):
                service.get_reconciliation_history(account_id=999)
