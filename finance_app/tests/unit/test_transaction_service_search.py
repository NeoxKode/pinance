"""
Unit tests for US-011: Basic Text Search.

Tests transaction search functionality in TransactionRepository and TransactionService.
Covers search_by_description() repository method and search_transactions() service method.

Test Coverage:
- TestTransactionRepositorySearch: 6 tests (repository layer)
- TestTransactionServiceSearch: 5 tests (service layer with business rules)

Total: 11 unit tests

Created: 2025-11-11
Story: US-011 - Basic Text Search (EPIC-002, Sprint 13)
"""
import pytest
import sqlite3
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
from finance_app.business.transaction_service import TransactionService
from finance_app.data.repositories.transaction_repository import TransactionRepository
from finance_app.data.models import Transaction
from finance_app.data.database import Database
from finance_app.utils.exceptions import DatabaseError


class TestTransactionRepositorySearch:
    """Unit tests for TransactionRepository.search_by_description()."""

    @pytest.fixture
    def mock_database(self):
        """Create mock database."""
        db = Mock(spec=Database)
        return db

    @pytest.fixture
    def repository(self, mock_database):
        """Create repository with mock database."""
        return TransactionRepository(mock_database)

    def test_search_by_description_basic(self, repository, mock_database):
        """Test basic search functionality returns matching transactions."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        # Mock database row
        mock_row = {
            'id': 1,
            'account_id': 5,
            'date': '2025-11-01',
            'description': 'Starbucks Coffee',
            'category': 'Dining Out',
            'amount': 5.50,
            'type': 'expense',
            'is_split': 0,
            'split_count': 0,
            'reconciliation_status': 'unreconciled',
            'reconciled_date': None,
            'statement_date': None,
            'is_opening_balance': 0
        }
        mock_cursor.fetchall.return_value = [mock_row]

        # Act
        results = repository.search_by_description("Starbucks")

        # Assert
        assert len(results) == 1
        assert results[0].description == "Starbucks Coffee"
        assert mock_cursor.execute.called
        # Verify LIKE query was used
        call_args = mock_cursor.execute.call_args[0]
        assert "LIKE" in call_args[0]
        assert "%Starbucks%" in call_args[1]

    def test_search_by_description_case_insensitive(self, repository, mock_database):
        """Test search is case-insensitive (SQLite LIKE default behavior)."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        mock_row = {
            'id': 1,
            'account_id': 5,
            'date': '2025-11-01',
            'description': 'Starbucks Coffee',
            'category': 'Dining Out',
            'amount': 5.50,
            'type': 'expense',
            'is_split': 0,
            'split_count': 0,
            'reconciliation_status': 'unreconciled',
            'reconciled_date': None,
            'statement_date': None,
            'is_opening_balance': 0
        }
        mock_cursor.fetchall.return_value = [mock_row]

        # Act
        results = repository.search_by_description("STARBUCKS")

        # Assert
        assert len(results) == 1
        # Verify uppercase keyword was used in query
        call_args = mock_cursor.execute.call_args[0]
        assert "%STARBUCKS%" in call_args[1]

    def test_search_by_description_with_account_filter(self, repository, mock_database):
        """Test search within specific account."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = []

        # Act
        repository.search_by_description("coffee", account_id=5)

        # Assert
        call_args = mock_cursor.execute.call_args[0]
        # Verify account_id filter in query
        assert "account_id = ?" in call_args[0]
        assert call_args[1] == ("%coffee%", 5)

    def test_search_by_description_no_results(self, repository, mock_database):
        """Test search with no matches returns empty list."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = []

        # Act
        results = repository.search_by_description("xyz123notfound")

        # Assert
        assert results == []
        assert len(results) == 0

    def test_search_by_description_partial_match(self, repository, mock_database):
        """Test partial substring matching works."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        mock_row = {
            'id': 1,
            'account_id': 5,
            'date': '2025-11-01',
            'description': 'Monthly Subscription Fee',
            'category': 'Services',
            'amount': 9.99,
            'type': 'expense',
            'is_split': 0,
            'split_count': 0,
            'reconciliation_status': 'unreconciled',
            'reconciled_date': None,
            'statement_date': None,
            'is_opening_balance': 0
        }
        mock_cursor.fetchall.return_value = [mock_row]

        # Act
        results = repository.search_by_description("subscr")

        # Assert
        assert len(results) == 1
        assert "Subscription" in results[0].description

    def test_search_by_description_database_error(self, repository, mock_database):
        """Test database error handling."""
        # Arrange
        mock_conn = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        # Raise sqlite3.Error so it gets caught and wrapped in DatabaseError
        mock_conn.cursor.side_effect = sqlite3.Error("Database connection failed")

        # Act & Assert
        with pytest.raises(DatabaseError, match="Failed to search transactions"):
            repository.search_by_description("test")


class TestTransactionServiceSearch:
    """Unit tests for TransactionService.search_transactions()."""

    @pytest.fixture
    def mock_database(self):
        """Create mock database."""
        db = Mock(spec=Database)
        return db

    @pytest.fixture
    def service(self, mock_database):
        """Create service with mock database."""
        return TransactionService(mock_database)

    def test_search_transactions_basic(self, service):
        """Test basic search functionality."""
        # Arrange
        mock_transaction = Transaction(
            id=1,
            account_id=5,
            date='2025-11-01',
            description='Starbucks Coffee',
            category='Dining Out',
            amount=Decimal('5.50'),
            type='expense'
        )

        with patch.object(service.transaction_repo, 'search_by_description') as mock_search:
            mock_search.return_value = [mock_transaction]

            # Act
            results = service.search_transactions("Starbucks")

            # Assert
            assert len(results) == 1
            assert results[0].description == "Starbucks Coffee"
            mock_search.assert_called_once_with("Starbucks", None)

    def test_search_transactions_empty_keyword(self, service):
        """Test empty keyword returns empty list (business rule)."""
        # Act
        results = service.search_transactions("")

        # Assert
        assert results == []
        assert len(results) == 0

    def test_search_transactions_whitespace_keyword(self, service):
        """Test whitespace-only keyword returns empty list."""
        # Act
        results = service.search_transactions("   ")

        # Assert
        assert results == []

    def test_search_transactions_trim_whitespace(self, service):
        """Test leading/trailing spaces are trimmed."""
        # Arrange
        mock_transaction = Transaction(
            id=1,
            account_id=5,
            date='2025-11-01',
            description='Coffee Shop',
            category='Dining Out',
            amount=Decimal('5.50'),
            type='expense'
        )

        with patch.object(service.transaction_repo, 'search_by_description') as mock_search:
            mock_search.return_value = [mock_transaction]

            # Act
            results = service.search_transactions("  coffee  ")

            # Assert
            assert len(results) == 1
            # Verify trimmed keyword was passed to repository
            mock_search.assert_called_once_with("coffee", None)

    def test_search_transactions_with_account_filter(self, service):
        """Test search within specific account."""
        # Arrange
        with patch.object(service.transaction_repo, 'search_by_description') as mock_search:
            mock_search.return_value = []

            # Act
            service.search_transactions("coffee", account_id=5)

            # Assert
            # Verify account_id was passed to repository
            mock_search.assert_called_once_with("coffee", 5)
