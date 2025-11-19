"""
Unit tests for JournalEntryRepository.

Story: US-002A - Journal Entry Foundation
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch, call
import sqlite3

from finance_app.data.models import JournalEntry, EntryType, Account, AccountType, AccountSubtype, NormalBalance
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.data.database import Database
from finance_app.utils.exceptions import DatabaseError, NotFoundError


class TestJournalEntryRepositoryCreate:
    """Test repository create() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return JournalEntryRepository(mock_db)

    def test_create_calculates_balance_before_insert(self, repository, mock_db):
        """Test that create() calculates balance_after before inserting."""
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock account balance query
        mock_cursor.fetchone.side_effect = [
            [1000.00],  # Current account balance
            # Return None for get_by_id (will be tested separately)
        ]
        mock_cursor.lastrowid = 123

        # Create entry
        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("0"),  # Will be calculated
            entry_type=EntryType.TRANSACTION
        )

        # Mock get_by_id to return the entry
        with patch.object(repository, 'get_by_id') as mock_get:
            mock_get.return_value = entry
            result = repository.create(entry)

        # Verify BEGIN IMMEDIATE was called
        mock_conn.execute.assert_called_once_with("BEGIN IMMEDIATE TRANSACTION")

        # Verify balance query was made
        assert mock_cursor.execute.call_count >= 2
        balance_query = mock_cursor.execute.call_args_list[0][0][0]
        assert "SELECT balance FROM accounts WHERE id = ?" in balance_query

    def test_create_uses_begin_immediate(self, repository, mock_db):
        """Test that create() uses BEGIN IMMEDIATE for transaction isolation."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.fetchone.return_value = [1000.00]
        mock_cursor.lastrowid = 1

        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )

        with patch.object(repository, 'get_by_id'):
            repository.create(entry)

        # Verify BEGIN IMMEDIATE was called
        mock_conn.execute.assert_called_once_with("BEGIN IMMEDIATE TRANSACTION")

    def test_create_raises_not_found_for_invalid_account(self, repository, mock_db):
        """Test that create() raises NotFoundError for non-existent account."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock account not found
        mock_cursor.fetchone.return_value = None

        entry = JournalEntry(
            id=None,
            account_id=999,  # Non-existent account
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )

        with pytest.raises(NotFoundError, match="Account 999 not found"):
            repository.create(entry)

    def test_create_handles_database_error(self, repository, mock_db):
        """Test that create() handles database errors properly."""
        mock_conn = MagicMock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Simulate database error
        mock_conn.execute.side_effect = sqlite3.Error("Database error")

        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )

        with pytest.raises(DatabaseError, match="Failed to create journal entry"):
            repository.create(entry)


class TestJournalEntryRepositoryGetByAccount:
    """Test repository get_by_account() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return JournalEntryRepository(mock_db)

    def test_get_by_account_without_filters(self, repository, mock_db):
        """Test get_by_account() without date filters."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock query results
        mock_cursor.fetchall.return_value = []

        entries = repository.get_by_account(account_id=1)

        # Verify query was made with only account_id filter
        query = mock_cursor.execute.call_args[0][0]
        params = mock_cursor.execute.call_args[0][1]

        assert "WHERE account_id = ?" in query
        assert params[0] == 1
        assert "AND entry_date >=" not in query
        assert "ORDER BY entry_date DESC" in query

    def test_get_by_account_with_start_date(self, repository, mock_db):
        """Test get_by_account() with start_date filter."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.fetchall.return_value = []

        entries = repository.get_by_account(
            account_id=1,
            start_date="2025-10-01"
        )

        # Verify start_date filter was added
        query = mock_cursor.execute.call_args[0][0]
        params = mock_cursor.execute.call_args[0][1]

        assert "AND entry_date >= ?" in query
        assert "2025-10-01" in params

    def test_get_by_account_with_end_date(self, repository, mock_db):
        """Test get_by_account() with end_date filter."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.fetchall.return_value = []

        entries = repository.get_by_account(
            account_id=1,
            end_date="2025-10-31"
        )

        # Verify end_date filter was added
        query = mock_cursor.execute.call_args[0][0]
        params = mock_cursor.execute.call_args[0][1]

        assert "AND entry_date <= ?" in query
        assert "2025-10-31" in params

    def test_get_by_account_with_limit(self, repository, mock_db):
        """Test get_by_account() with limit parameter."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.fetchall.return_value = []

        entries = repository.get_by_account(account_id=1, limit=10)

        # Verify LIMIT clause was added
        query = mock_cursor.execute.call_args[0][0]
        params = mock_cursor.execute.call_args[0][1]

        assert "LIMIT ?" in query
        assert 10 in params


class TestJournalEntryRepositoryGetAccountBalance:
    """Test repository get_account_balance() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return JournalEntryRepository(mock_db)

    def test_get_account_balance_without_date(self, repository, mock_db):
        """Test get_account_balance() without as_of_date."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock balance result
        mock_cursor.fetchone.return_value = [1500.50]

        balance = repository.get_account_balance(account_id=1)

        # Verify query
        query = mock_cursor.execute.call_args[0][0]
        assert "SUM(debit_amount - credit_amount)" in query
        assert "WHERE account_id = ?" in query
        assert "AND entry_date <=" not in query

        # Verify result
        assert balance == Decimal("1500.50")

    # Note: test_get_account_balance_with_date was removed because the as_of_date
    # parameter was removed when get_account_balance was simplified for US-010.
    # The date-filtered balance calculation is now done elsewhere.

    def test_get_account_balance_returns_zero_for_no_entries(self, repository, mock_db):
        """Test get_account_balance() returns zero when no entries exist."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock NULL result (no entries)
        mock_cursor.fetchone.return_value = [None]

        balance = repository.get_account_balance(account_id=1)

        assert balance == Decimal("0")


class TestJournalEntryRepositoryUpdate:
    """Test repository update() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return JournalEntryRepository(mock_db)

    def test_update_raises_error_for_no_id(self, repository):
        """Test that update() raises ValueError when entry has no ID."""
        entry = JournalEntry(
            id=None,  # No ID!
            account_id=1,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )

        with pytest.raises(ValueError, match="Journal entry ID is required"):
            repository.update(entry)

    def test_update_includes_account_id_in_query(self, repository, mock_db):
        """Test that update() includes account_id to trigger validation."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock existing entry data
        mock_cursor.fetchone.side_effect = [
            [1, "2025-10-22"],  # Old entry
            [500.00],  # Balance calculation
            [1000.00],  # Current account balance
        ]
        mock_cursor.rowcount = 1

        entry = JournalEntry(
            id=123,
            account_id=1,
            entry_date="2025-10-22",
            description="Updated",
            debit_amount=Decimal("200.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1200.00"),
            entry_type=EntryType.TRANSACTION
        )

        with patch.object(repository, 'get_by_id'):
            repository.update(entry)

        # Verify UPDATE query includes account_id
        update_calls = [call for call in mock_cursor.execute.call_args_list
                       if 'UPDATE journal_entries' in str(call)]
        assert len(update_calls) > 0

        update_query = update_calls[0][0][0]
        assert "SET account_id = ?" in update_query

    def test_update_raises_not_found_for_invalid_id(self, repository, mock_db):
        """Test that update() raises NotFoundError for non-existent entry."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock entry not found
        mock_cursor.fetchone.return_value = None

        entry = JournalEntry(
            id=999,
            account_id=1,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )

        with pytest.raises(NotFoundError, match="Journal entry 999 not found"):
            repository.update(entry)


class TestJournalEntryRepositoryDelete:
    """Test repository delete() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return JournalEntryRepository(mock_db)

    def test_delete_removes_entry(self, repository, mock_db):
        """Test that delete() removes the entry."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.rowcount = 1

        repository.delete(entry_id=123)

        # Verify DELETE query was executed
        query = mock_cursor.execute.call_args[0][0]
        params = mock_cursor.execute.call_args[0][1]

        assert "DELETE FROM journal_entries WHERE id = ?" in query
        assert params == (123,)

    def test_delete_uses_begin_immediate(self, repository, mock_db):
        """Test that delete() uses BEGIN IMMEDIATE."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.rowcount = 1

        repository.delete(entry_id=123)

        # Verify BEGIN IMMEDIATE was called
        mock_conn.execute.assert_called_once_with("BEGIN IMMEDIATE TRANSACTION")

    def test_delete_raises_not_found_for_invalid_id(self, repository, mock_db):
        """Test that delete() raises NotFoundError for non-existent entry."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock no rows affected
        mock_cursor.rowcount = 0

        with pytest.raises(NotFoundError, match="Journal entry 999 not found"):
            repository.delete(entry_id=999)


class TestJournalEntryRepositoryRowConversion:
    """Test _row_to_entry() helper method."""

    @pytest.fixture
    def repository(self):
        """Create repository."""
        return JournalEntryRepository(Mock(spec=Database))

    def test_row_to_entry_converts_all_fields(self, repository):
        """Test that _row_to_entry() converts all fields correctly."""
        row = [
            123,  # id
            456,  # transaction_id
            789,  # group_id
            1,    # account_id
            "2025-10-22",  # entry_date
            "Test entry",  # description
            100.00,  # debit_amount
            0.00,    # credit_amount
            1100.00,  # balance_after
            'transaction',  # entry_type
            "CHK-001",  # reference_number
            1,  # is_reconciled
            999,  # reconciliation_id
            "Test notes",  # notes
            "2025-10-22T10:30:00",  # created_at
            "2025-10-22T11:45:00"   # updated_at
        ]

        entry = repository._row_to_entry(row)

        assert entry.id == 123
        assert entry.transaction_id == 456
        assert entry.group_id == 789
        assert entry.account_id == 1
        assert entry.entry_date == "2025-10-22"
        assert entry.description == "Test entry"
        assert entry.debit_amount == Decimal("100.00")
        assert entry.credit_amount == Decimal("0.00")
        assert entry.balance_after == Decimal("1100.00")
        assert entry.entry_type == EntryType.TRANSACTION
        assert entry.reference_number == "CHK-001"
        assert entry.is_reconciled is True
        assert entry.reconciliation_id == 999
        assert entry.notes == "Test notes"

    def test_row_to_entry_handles_none_values(self, repository):
        """Test that _row_to_entry() handles None values correctly."""
        row = [
            1,    # id
            None, # transaction_id
            None, # group_id
            1,    # account_id
            "2025-10-22",
            "Test",
            50.00,
            0.00,
            1050.00,
            'transaction',
            None,  # reference_number
            0,     # is_reconciled
            None,  # reconciliation_id
            None,  # notes
            None,  # created_at
            None   # updated_at
        ]

        entry = repository._row_to_entry(row)

        assert entry.transaction_id is None
        assert entry.group_id is None
        assert entry.reference_number is None
        assert entry.is_reconciled is False
        assert entry.reconciliation_id is None
        assert entry.notes is None
        assert entry.created_at is None
        assert entry.updated_at is None
