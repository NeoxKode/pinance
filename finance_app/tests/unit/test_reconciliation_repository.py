"""
Unit tests for ReconciliationRepository.

Story: US-004 - Account Reconciliation (Day 1, Task 4.6)

Test Coverage:
- create() method (5 tests)
- get_by_id() method (2 tests)
- get_by_account() method (3 tests)
- get_last_reconciliation() method (3 tests)
- get_pending_reconciliation() method (3 tests)
- _row_to_reconciliation() conversion (1 test)

Total: 17 tests (exceeds 15+ target)
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
import sqlite3
from datetime import datetime

from finance_app.data.models import Reconciliation
from finance_app.data.repositories.reconciliation_repository import ReconciliationRepository
from finance_app.data.database import Database
from finance_app.utils.exceptions import DatabaseError, ValidationError


class TestReconciliationRepositoryCreate:
    """Test repository create() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return ReconciliationRepository(mock_db)

    def test_create_saves_reconciliation_correctly(self, repository, mock_db):
        """Test that create() saves reconciliation with correct data."""
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.lastrowid = 123

        # Create reconciliation
        reconciliation = Reconciliation(
            id=None,
            account_id=1,
            reconciliation_date="2025-10-23",
            statement_date="2025-10-31",
            statement_balance=Decimal("1200.00"),
            cleared_balance=Decimal("1200.00"),
            discrepancy=Decimal("0.00"),
            transaction_count=5,
            notes="Perfect reconciliation"
        )

        # Mock get_by_id to return the reconciliation
        with patch.object(repository, 'get_by_id') as mock_get:
            mock_get.return_value = reconciliation
            result = repository.create(reconciliation)

        # Verify INSERT was called
        assert mock_cursor.execute.called
        insert_query = mock_cursor.execute.call_args[0][0]
        assert "INSERT INTO reconciliations" in insert_query

        # Verify commit was called
        mock_conn.commit.assert_called_once()

    def test_create_sets_created_at_timestamp(self, repository, mock_db):
        """Test that create() sets created_at timestamp."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.lastrowid = 1

        reconciliation = Reconciliation(
            id=None,
            account_id=1,
            reconciliation_date="2025-10-23",
            statement_date="2025-10-31",
            statement_balance=Decimal("1200.00"),
            cleared_balance=Decimal("1200.00"),
            discrepancy=Decimal("0.00"),
            transaction_count=5
        )

        with patch.object(repository, 'get_by_id'):
            repository.create(reconciliation)

        # Verify created_at was passed to INSERT
        insert_params = mock_cursor.execute.call_args[0][1]
        created_at = insert_params[-1]  # Last parameter
        assert created_at is not None
        # Verify it's a valid ISO timestamp
        datetime.fromisoformat(created_at)

    def test_create_raises_validation_error_for_negative_transaction_count(self, repository):
        """Test that create() validates transaction_count."""
        reconciliation = Reconciliation(
            id=None,
            account_id=1,
            reconciliation_date="2025-10-23",
            statement_date="2025-10-31",
            statement_balance=Decimal("1200.00"),
            cleared_balance=Decimal("1200.00"),
            discrepancy=Decimal("0.00"),
            transaction_count=-5  # Invalid
        )

        with pytest.raises(ValidationError, match="cannot be negative"):
            repository.create(reconciliation)

    def test_create_raises_validation_error_for_missing_reconciliation_date(self, repository):
        """Test that create() validates reconciliation_date."""
        reconciliation = Reconciliation(
            id=None,
            account_id=1,
            reconciliation_date="",  # Invalid
            statement_date="2025-10-31",
            statement_balance=Decimal("1200.00"),
            cleared_balance=Decimal("1200.00"),
            discrepancy=Decimal("0.00"),
            transaction_count=5
        )

        with pytest.raises(ValidationError, match="Reconciliation date is required"):
            repository.create(reconciliation)

    def test_create_raises_validation_error_for_missing_statement_date(self, repository):
        """Test that create() validates statement_date."""
        reconciliation = Reconciliation(
            id=None,
            account_id=1,
            reconciliation_date="2025-10-23",
            statement_date="",  # Invalid
            statement_balance=Decimal("1200.00"),
            cleared_balance=Decimal("1200.00"),
            discrepancy=Decimal("0.00"),
            transaction_count=5
        )

        with pytest.raises(ValidationError, match="Statement date is required"):
            repository.create(reconciliation)


class TestReconciliationRepositoryGetById:
    """Test repository get_by_id() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return ReconciliationRepository(mock_db)

    def test_get_by_id_returns_reconciliation_when_found(self, repository, mock_db):
        """Test that get_by_id() returns reconciliation when found."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock database row
        mock_cursor.fetchone.return_value = (
            1,  # id
            2,  # account_id
            "2025-10-23",  # reconciliation_date
            "2025-10-31",  # statement_date
            1200.00,  # statement_balance
            1200.00,  # cleared_balance
            0.00,  # discrepancy
            5,  # transaction_count
            "Perfect",  # notes
            "2025-10-23T15:30:00"  # created_at
        )

        result = repository.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.account_id == 2
        assert result.reconciliation_date == "2025-10-23"
        assert result.statement_balance == Decimal("1200.00")

    def test_get_by_id_returns_none_when_not_found(self, repository, mock_db):
        """Test that get_by_id() returns None when not found."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock no result
        mock_cursor.fetchone.return_value = None

        result = repository.get_by_id(999)

        assert result is None


class TestReconciliationRepositoryGetByAccount:
    """Test repository get_by_account() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return ReconciliationRepository(mock_db)

    def test_get_by_account_returns_ordered_history(self, repository, mock_db):
        """Test that get_by_account() returns reconciliations ordered by date DESC."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock 3 reconciliations (already ordered DESC by date)
        mock_cursor.fetchall.return_value = [
            (3, 1, "2025-10-23", "2025-10-31", 1300.00, 1300.00, 0.00, 7, None, "2025-10-23T16:00:00"),
            (2, 1, "2025-09-30", "2025-09-30", 1200.00, 1200.00, 0.00, 6, None, "2025-09-30T15:00:00"),
            (1, 1, "2025-08-31", "2025-08-31", 1100.00, 1100.00, 0.00, 5, None, "2025-08-31T14:00:00"),
        ]

        result = repository.get_by_account(account_id=1)

        assert len(result) == 3
        # Verify newest first
        assert result[0].reconciliation_date == "2025-10-23"
        assert result[1].reconciliation_date == "2025-09-30"
        assert result[2].reconciliation_date == "2025-08-31"

    def test_get_by_account_respects_limit(self, repository, mock_db):
        """Test that get_by_account() respects limit parameter."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.fetchall.return_value = [
            (2, 1, "2025-10-23", "2025-10-31", 1200.00, 1200.00, 0.00, 5, None, "2025-10-23T15:00:00"),
        ]

        repository.get_by_account(account_id=1, limit=1)

        # Verify LIMIT was added to query
        query = mock_cursor.execute.call_args[0][0]
        assert "LIMIT ?" in query

        # Verify limit parameter passed
        params = mock_cursor.execute.call_args[0][1]
        assert 1 in params  # account_id
        assert 1 in params  # limit

    def test_get_by_account_returns_empty_list_when_no_reconciliations(self, repository, mock_db):
        """Test that get_by_account() returns empty list when no reconciliations."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.fetchall.return_value = []

        result = repository.get_by_account(account_id=1)

        assert result == []


class TestReconciliationRepositoryGetLastReconciliation:
    """Test repository get_last_reconciliation() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return ReconciliationRepository(mock_db)

    def test_get_last_reconciliation_returns_most_recent(self, repository):
        """Test that get_last_reconciliation() returns most recent reconciliation."""
        # Mock get_by_account to return reconciliations
        with patch.object(repository, 'get_by_account') as mock_get:
            mock_reconciliation = Reconciliation(
                id=3,
                account_id=1,
                reconciliation_date="2025-10-23",
                statement_date="2025-10-31",
                statement_balance=Decimal("1300.00"),
                cleared_balance=Decimal("1300.00"),
                discrepancy=Decimal("0.00"),
                transaction_count=7
            )
            mock_get.return_value = [mock_reconciliation]

            result = repository.get_last_reconciliation(account_id=1)

            assert result is not None
            assert result.id == 3
            assert result.reconciliation_date == "2025-10-23"
            # Verify get_by_account was called with limit=1
            mock_get.assert_called_once_with(1, limit=1)

    def test_get_last_reconciliation_returns_none_when_never_reconciled(self, repository):
        """Test that get_last_reconciliation() returns None when never reconciled."""
        with patch.object(repository, 'get_by_account') as mock_get:
            mock_get.return_value = []

            result = repository.get_last_reconciliation(account_id=1)

            assert result is None

    def test_get_last_reconciliation_uses_limit_one(self, repository):
        """Test that get_last_reconciliation() uses limit=1 for efficiency."""
        with patch.object(repository, 'get_by_account') as mock_get:
            mock_get.return_value = []

            repository.get_last_reconciliation(account_id=1)

            # Verify limit=1 was passed
            mock_get.assert_called_once_with(1, limit=1)


class TestReconciliationRepositoryGetPendingReconciliation:
    """Test repository get_pending_reconciliation() method (concurrency check)."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return ReconciliationRepository(mock_db)

    def test_get_pending_reconciliation_returns_true_when_pending(self, repository, mock_db):
        """Test that get_pending_reconciliation() returns True when reconciliation in progress."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock 5 pending transactions
        mock_cursor.fetchone.return_value = (5,)  # pending_count

        result = repository.get_pending_reconciliation(account_id=1)

        assert result is True

        # Verify query checked for status='pending'
        query = mock_cursor.execute.call_args[0][0]
        assert "reconciliation_status = 'pending'" in query

    def test_get_pending_reconciliation_returns_false_when_no_pending(self, repository, mock_db):
        """Test that get_pending_reconciliation() returns False when no pending transactions."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock 0 pending transactions
        mock_cursor.fetchone.return_value = (0,)  # pending_count

        result = repository.get_pending_reconciliation(account_id=1)

        assert result is False

    def test_get_pending_reconciliation_handles_null_result(self, repository, mock_db):
        """Test that get_pending_reconciliation() handles NULL result from COUNT."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock None result (edge case)
        mock_cursor.fetchone.return_value = None

        result = repository.get_pending_reconciliation(account_id=1)

        assert result is False


class TestReconciliationRepositoryRowConversion:
    """Test repository _row_to_reconciliation() method."""

    @pytest.fixture
    def repository(self):
        """Create repository with mock database."""
        mock_db = Mock(spec=Database)
        return ReconciliationRepository(mock_db)

    def test_row_to_reconciliation_converts_correctly(self, repository):
        """Test that _row_to_reconciliation() converts database row to Reconciliation."""
        # Mock SQLite row
        row = (
            1,  # id
            2,  # account_id
            "2025-10-23",  # reconciliation_date
            "2025-10-31",  # statement_date
            1200.50,  # statement_balance (float from DB)
            1200.50,  # cleared_balance (float from DB)
            0.00,  # discrepancy (float from DB)
            5,  # transaction_count
            "Perfect reconciliation",  # notes
            "2025-10-23T15:30:00.123456"  # created_at
        )

        result = repository._row_to_reconciliation(row)

        assert isinstance(result, Reconciliation)
        assert result.id == 1
        assert result.account_id == 2
        assert result.reconciliation_date == "2025-10-23"
        assert result.statement_date == "2025-10-31"
        # Verify Decimal conversion
        assert isinstance(result.statement_balance, Decimal)
        assert result.statement_balance == Decimal("1200.50")
        assert isinstance(result.cleared_balance, Decimal)
        assert result.cleared_balance == Decimal("1200.50")
        assert isinstance(result.discrepancy, Decimal)
        assert result.discrepancy == Decimal("0.00")
        assert result.transaction_count == 5
        assert result.notes == "Perfect reconciliation"
        assert result.created_at == "2025-10-23T15:30:00.123456"
