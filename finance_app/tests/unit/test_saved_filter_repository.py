"""
Unit tests for SavedFilterRepository.

Story: US-015 - Combined Filters & Saved Searches (Sprint 16, Task 8.1)

Test Coverage:
- create() method (3 tests)
- get_by_id() method (2 tests)
- get_by_name() method (2 tests)
- get_all() method (2 tests)
- get_favorites() method (2 tests)
- update() method (3 tests)
- delete() method (2 tests)
- mark_as_used() method (2 tests)
- toggle_favorite() method (2 tests)
- _row_to_saved_filter() conversion (1 test)

Total: 21 tests (exceeds 8+ target)
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
import sqlite3
from datetime import datetime

from finance_app.data.models import SavedFilter
from finance_app.data.repositories.saved_filter_repository import SavedFilterRepository
from finance_app.data.database import Database
from finance_app.utils.exceptions import DatabaseError, NotFoundError


class TestSavedFilterRepositoryCreate:
    """Test repository create() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return SavedFilterRepository(mock_db)

    def test_create_saves_filter_correctly(self, repository, mock_db):
        """Test that create() saves filter with correct data."""
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.lastrowid = 1
        mock_cursor.fetchone.return_value = (
            '2025-11-18 12:00:00',  # created_at
            '2025-11-18 12:00:00'   # updated_at
        )

        # Create filter
        filter_criteria = {'text_search': 'coffee', 'categories': ['Groceries']}
        saved_filter = SavedFilter(
            name='Coffee Purchases',
            filter_criteria=filter_criteria,
            description='All coffee purchases',
            is_favorite=True
        )

        result = repository.create(saved_filter)

        # Verify INSERT was called
        assert mock_cursor.execute.called
        insert_query = mock_cursor.execute.call_args_list[0][0][0]
        assert "INSERT INTO saved_filters" in insert_query

        # Verify ID was set
        assert result.id == 1

        # Verify timestamps were set
        assert result.created_at is not None
        assert result.updated_at is not None

    def test_create_serializes_filter_criteria_to_json(self, repository, mock_db):
        """Test that create() serializes filter_criteria as JSON."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.lastrowid = 1
        mock_cursor.fetchone.return_value = (
            '2025-11-18 12:00:00',
            '2025-11-18 12:00:00'
        )

        filter_criteria = {
            'text_search': 'coffee',
            'date_from': '2025-01-01',
            'categories': ['Groceries', 'Dining Out']
        }
        saved_filter = SavedFilter(name='Test', filter_criteria=filter_criteria)

        repository.create(saved_filter)

        # Get the parameters passed to execute
        params = mock_cursor.execute.call_args_list[0][0][1]

        # Verify filter_json parameter is a JSON string
        import json
        filter_json = params[2]  # Third parameter is filter_json
        assert isinstance(filter_json, str)

        # Verify JSON can be parsed back
        parsed = json.loads(filter_json)
        assert parsed == filter_criteria

    def test_create_raises_error_on_duplicate_name(self, repository, mock_db):
        """Test that create() raises DatabaseError on duplicate filter name."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Simulate UNIQUE constraint violation
        mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")

        filter_criteria = {'text_search': 'coffee'}
        saved_filter = SavedFilter(name='Duplicate', filter_criteria=filter_criteria)

        with pytest.raises(DatabaseError) as exc_info:
            repository.create(saved_filter)

        assert "already exists" in str(exc_info.value)


class TestSavedFilterRepositoryGetById:
    """Test repository get_by_id() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return SavedFilterRepository(mock_db)

    def test_get_by_id_returns_filter_when_found(self, repository, mock_db):
        """Test that get_by_id() returns SavedFilter when filter exists."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock database row
        mock_cursor.fetchone.return_value = (
            1,  # id
            'Coffee Purchases',  # name
            'All coffee purchases',  # description
            '{"text_search": "coffee"}',  # filter_json
            1,  # schema_version
            1,  # is_favorite
            '2025-11-18 12:00:00',  # created_at
            '2025-11-18 12:00:00',  # updated_at
            None  # last_used_at
        )

        result = repository.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.name == 'Coffee Purchases'
        assert result.filter_criteria == {'text_search': 'coffee'}
        assert result.is_favorite is True

    def test_get_by_id_returns_none_when_not_found(self, repository, mock_db):
        """Test that get_by_id() returns None when filter doesn't exist."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.fetchone.return_value = None

        result = repository.get_by_id(999)

        assert result is None


class TestSavedFilterRepositoryGetByName:
    """Test repository get_by_name() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return SavedFilterRepository(mock_db)

    def test_get_by_name_returns_filter_when_found(self, repository, mock_db):
        """Test that get_by_name() returns SavedFilter when name matches."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.fetchone.return_value = (
            1, 'Coffee Purchases', 'Desc', '{"text_search": "coffee"}',
            1, 1, '2025-11-18 12:00:00', '2025-11-18 12:00:00', None
        )

        result = repository.get_by_name('Coffee Purchases')

        assert result is not None
        assert result.name == 'Coffee Purchases'

        # Verify WHERE clause used name parameter
        query = mock_cursor.execute.call_args[0][0]
        assert "WHERE name = ?" in query

    def test_get_by_name_returns_none_when_not_found(self, repository, mock_db):
        """Test that get_by_name() returns None when name doesn't match."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.fetchone.return_value = None

        result = repository.get_by_name('Nonexistent Filter')

        assert result is None


class TestSavedFilterRepositoryGetAll:
    """Test repository get_all() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return SavedFilterRepository(mock_db)

    def test_get_all_returns_all_filters(self, repository, mock_db):
        """Test that get_all() returns list of all saved filters."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock 3 filters
        mock_cursor.fetchall.return_value = [
            (1, 'Filter A', None, '{"text_search": "a"}', 1, 0, '2025-11-18', '2025-11-18', None),
            (2, 'Filter B', None, '{"text_search": "b"}', 1, 1, '2025-11-18', '2025-11-18', None),
            (3, 'Filter C', None, '{"text_search": "c"}', 1, 0, '2025-11-18', '2025-11-18', None),
        ]

        result = repository.get_all()

        assert len(result) == 3
        assert all(isinstance(f, SavedFilter) for f in result)
        assert result[0].name == 'Filter A'
        assert result[1].name == 'Filter B'
        assert result[2].name == 'Filter C'

    def test_get_all_supports_different_sort_orders(self, repository, mock_db):
        """Test that get_all() supports order_by parameter."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.fetchall.return_value = []

        # Test name sorting (default)
        repository.get_all(order_by='name')
        query = mock_cursor.execute.call_args[0][0]
        assert "ORDER BY name ASC" in query

        # Test created_at sorting
        repository.get_all(order_by='created_at')
        query = mock_cursor.execute.call_args[0][0]
        assert "ORDER BY created_at DESC" in query

        # Test last_used_at sorting
        repository.get_all(order_by='last_used_at')
        query = mock_cursor.execute.call_args[0][0]
        assert "ORDER BY last_used_at DESC" in query


class TestSavedFilterRepositoryGetFavorites:
    """Test repository get_favorites() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return SavedFilterRepository(mock_db)

    def test_get_favorites_returns_only_favorite_filters(self, repository, mock_db):
        """Test that get_favorites() filters for is_favorite = 1."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock 2 favorite filters
        mock_cursor.fetchall.return_value = [
            (1, 'Fav 1', None, '{}', 1, 1, '2025-11-18', '2025-11-18', None),
            (2, 'Fav 2', None, '{}', 1, 1, '2025-11-18', '2025-11-18', None),
        ]

        result = repository.get_favorites()

        assert len(result) == 2
        assert all(f.is_favorite for f in result)

        # Verify WHERE clause filters for is_favorite
        query = mock_cursor.execute.call_args[0][0]
        assert "WHERE is_favorite = 1" in query

    def test_get_favorites_returns_empty_list_when_none(self, repository, mock_db):
        """Test that get_favorites() returns empty list when no favorites."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.fetchall.return_value = []

        result = repository.get_favorites()

        assert result == []


class TestSavedFilterRepositoryUpdate:
    """Test repository update() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return SavedFilterRepository(mock_db)

    def test_update_modifies_existing_filter(self, repository, mock_db):
        """Test that update() modifies existing filter correctly."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock filter exists check
        mock_cursor.fetchone.side_effect = [
            (1,),  # First call: filter exists
            ('2025-11-18 13:00:00',)  # Second call: new updated_at
        ]

        filter_criteria = {'text_search': 'updated'}
        saved_filter = SavedFilter(
            id=1,
            name='Updated Name',
            filter_criteria=filter_criteria,
            description='Updated description'
        )

        result = repository.update(saved_filter)

        # Verify UPDATE was called
        update_query = mock_cursor.execute.call_args_list[1][0][0]
        assert "UPDATE saved_filters" in update_query
        assert "WHERE id = ?" in update_query

        # Verify updated_at was refreshed
        assert result.updated_at is not None

    def test_update_raises_error_when_filter_not_found(self, repository, mock_db):
        """Test that update() raises NotFoundError when filter doesn't exist."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock filter doesn't exist
        mock_cursor.fetchone.return_value = None

        saved_filter = SavedFilter(
            id=999,
            name='Nonexistent',
            filter_criteria={}
        )

        with pytest.raises(NotFoundError) as exc_info:
            repository.update(saved_filter)

        assert "not found" in str(exc_info.value)

    def test_update_raises_error_without_id(self, repository, mock_db):
        """Test that update() raises ValueError when filter has no ID."""
        saved_filter = SavedFilter(
            name='No ID',
            filter_criteria={}
        )

        with pytest.raises(ValueError) as exc_info:
            repository.update(saved_filter)

        assert "without ID" in str(exc_info.value)


class TestSavedFilterRepositoryDelete:
    """Test repository delete() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return SavedFilterRepository(mock_db)

    def test_delete_removes_filter_when_exists(self, repository, mock_db):
        """Test that delete() removes filter and returns True."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock successful delete (1 row affected)
        mock_cursor.rowcount = 1

        result = repository.delete(1)

        assert result is True

        # Verify DELETE was called
        query = mock_cursor.execute.call_args[0][0]
        assert "DELETE FROM saved_filters" in query
        assert "WHERE id = ?" in query

    def test_delete_returns_false_when_not_found(self, repository, mock_db):
        """Test that delete() returns False when filter doesn't exist."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock no rows affected
        mock_cursor.rowcount = 0

        result = repository.delete(999)

        assert result is False


class TestSavedFilterRepositoryMarkAsUsed:
    """Test repository mark_as_used() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return SavedFilterRepository(mock_db)

    def test_mark_as_used_updates_last_used_at(self, repository, mock_db):
        """Test that mark_as_used() updates last_used_at timestamp."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.rowcount = 1

        result = repository.mark_as_used(1)

        assert result is True

        # Verify UPDATE sets last_used_at
        query = mock_cursor.execute.call_args[0][0]
        assert "UPDATE saved_filters" in query
        assert "SET last_used_at = datetime('now')" in query
        assert "WHERE id = ?" in query

    def test_mark_as_used_returns_false_when_not_found(self, repository, mock_db):
        """Test that mark_as_used() returns False when filter doesn't exist."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        mock_cursor.rowcount = 0

        result = repository.mark_as_used(999)

        assert result is False


class TestSavedFilterRepositoryToggleFavorite:
    """Test repository toggle_favorite() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return SavedFilterRepository(mock_db)

    def test_toggle_favorite_flips_from_true_to_false(self, repository, mock_db):
        """Test that toggle_favorite() changes True → False."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock current favorite status = True
        mock_cursor.fetchone.return_value = (1,)

        result = repository.toggle_favorite(1)

        assert result is False  # Toggled to False

        # Verify UPDATE sets is_favorite = 0
        update_query = mock_cursor.execute.call_args_list[1][0][0]
        params = mock_cursor.execute.call_args_list[1][0][1]
        assert "UPDATE saved_filters" in update_query
        assert params[0] == 0  # New value is 0 (False)

    def test_toggle_favorite_raises_error_when_not_found(self, repository, mock_db):
        """Test that toggle_favorite() raises NotFoundError when filter doesn't exist."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_conn

        # Mock filter not found
        mock_cursor.fetchone.return_value = None

        with pytest.raises(NotFoundError) as exc_info:
            repository.toggle_favorite(999)

        assert "not found" in str(exc_info.value)


class TestSavedFilterRepositoryRowConversion:
    """Test repository _row_to_saved_filter() conversion."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return SavedFilterRepository(mock_db)

    def test_row_to_saved_filter_converts_correctly(self, repository):
        """Test that _row_to_saved_filter() converts database row to SavedFilter."""
        row = (
            1,  # id
            'Coffee Purchases',  # name
            'All coffee purchases',  # description
            '{"text_search": "coffee", "categories": ["Groceries"]}',  # filter_json
            1,  # schema_version
            1,  # is_favorite
            '2025-11-18 12:00:00',  # created_at
            '2025-11-18 13:00:00',  # updated_at
            '2025-11-18 14:00:00'   # last_used_at
        )

        result = repository._row_to_saved_filter(row)

        assert isinstance(result, SavedFilter)
        assert result.id == 1
        assert result.name == 'Coffee Purchases'
        assert result.description == 'All coffee purchases'
        assert result.filter_criteria == {'text_search': 'coffee', 'categories': ['Groceries']}
        assert result.schema_version == 1
        assert result.is_favorite is True
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)
        assert isinstance(result.last_used_at, datetime)
