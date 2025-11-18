"""
Unit tests for US-013: Category Filter.

Tests category filtering functionality in TransactionRepository and TransactionService.
Covers get_categories_with_counts() and filter_by_categories() methods.

Test Coverage:
- TestTransactionRepositoryCategoryFilter: 7 tests (repository layer)
- TestTransactionServiceCategoryFilter: 6 tests (service layer with validation)

Total: 13 unit tests

Created: 2025-11-17
Story: US-013 - Category Filter (EPIC-002, Sprint 14)
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


class TestTransactionRepositoryCategoryFilter:
    """Unit tests for TransactionRepository category filter methods."""

    @pytest.fixture
    def mock_database(self):
        """Create mock database."""
        db = Mock(spec=Database)
        return db

    @pytest.fixture
    def repository(self, mock_database):
        """Create repository with mock database."""
        return TransactionRepository(mock_database)

    def test_get_categories_with_counts_all_accounts(self, repository, mock_database):
        """Test getting categories with counts from all accounts."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        # Mock category counts
        mock_rows = [
            {'category': 'Dining Out', 'count': 45},
            {'category': 'Groceries', 'count': 123},
            {'category': 'Transportation', 'count': 67}
        ]
        mock_cursor.fetchall.return_value = mock_rows

        # Act
        results = repository.get_categories_with_counts()

        # Assert
        assert len(results) == 3
        assert results[0] == ('Dining Out', 45)
        assert results[1] == ('Groceries', 123)
        assert results[2] == ('Transportation', 67)
        assert mock_cursor.execute.called
        # Verify query has GROUP BY and ORDER BY
        call_args = mock_cursor.execute.call_args[0]
        assert "GROUP BY category" in call_args[0]
        assert "ORDER BY category ASC" in call_args[0]

    def test_get_categories_with_counts_single_account(self, repository, mock_database):
        """Test getting categories with counts from specific account."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        mock_rows = [
            {'category': 'Groceries', 'count': 23}
        ]
        mock_cursor.fetchall.return_value = mock_rows

        # Act
        results = repository.get_categories_with_counts(account_id=5)

        # Assert
        assert len(results) == 1
        assert results[0] == ('Groceries', 23)
        # Verify account filter was applied
        call_args = mock_cursor.execute.call_args[0]
        assert "WHERE account_id = ?" in call_args[0]
        assert call_args[1] == (5,)

    def test_get_categories_with_counts_empty_result(self, repository, mock_database):
        """Test getting categories when no transactions exist."""
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
        results = repository.get_categories_with_counts()

        # Assert
        assert results == []

    def test_filter_by_categories_single_category(self, repository, mock_database):
        """Test filtering by single category."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        # Mock transaction row
        mock_row = {
            'id': 1,
            'account_id': 5,
            'date': '2025-11-01',
            'description': 'Whole Foods',
            'category': 'Groceries',
            'amount': 45.50,
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
        results = repository.filter_by_categories(['Groceries'])

        # Assert
        assert len(results) == 1
        assert results[0].category == 'Groceries'
        assert mock_cursor.execute.called
        # Verify IN clause was used
        call_args = mock_cursor.execute.call_args[0]
        assert "category IN (?)" in call_args[0]
        assert call_args[1] == ['Groceries']

    def test_filter_by_categories_multiple_categories(self, repository, mock_database):
        """Test filtering by multiple categories."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        mock_rows = [
            {
                'id': 1,
                'account_id': 5,
                'date': '2025-11-01',
                'description': 'Whole Foods',
                'category': 'Groceries',
                'amount': 45.50,
                'type': 'expense',
                'is_split': 0,
                'split_count': 0,
                'reconciliation_status': 'unreconciled',
                'reconciled_date': None,
                'statement_date': None,
                'is_opening_balance': 0
            },
            {
                'id': 2,
                'account_id': 5,
                'date': '2025-11-01',
                'description': 'Restaurant',
                'category': 'Dining Out',
                'amount': 35.00,
                'type': 'expense',
                'is_split': 0,
                'split_count': 0,
                'reconciliation_status': 'unreconciled',
                'reconciled_date': None,
                'statement_date': None,
                'is_opening_balance': 0
            }
        ]
        mock_cursor.fetchall.return_value = mock_rows

        # Act
        results = repository.filter_by_categories(['Groceries', 'Dining Out'])

        # Assert
        assert len(results) == 2
        assert results[0].category == 'Groceries'
        assert results[1].category == 'Dining Out'
        # Verify IN clause with multiple placeholders
        call_args = mock_cursor.execute.call_args[0]
        assert "category IN (?,?)" in call_args[0]
        assert call_args[1] == ['Groceries', 'Dining Out']

    def test_filter_by_categories_empty_list(self, repository, mock_database):
        """Test filtering with empty category list returns empty."""
        # Act
        results = repository.filter_by_categories([])

        # Assert
        assert results == []
        # Verify no database call was made
        assert not mock_database.get_connection.called

    def test_filter_by_categories_with_account_id(self, repository, mock_database):
        """Test filtering by categories with account filter."""
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
        results = repository.filter_by_categories(['Groceries'], account_id=5)

        # Assert
        assert results == []
        # Verify both category and account filters applied
        call_args = mock_cursor.execute.call_args[0]
        assert "category IN (?)" in call_args[0]
        assert "account_id = ?" in call_args[0]
        assert call_args[1] == ['Groceries', 5]


class TestTransactionServiceCategoryFilter:
    """Unit tests for TransactionService category filter methods."""

    @pytest.fixture
    def mock_database(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_database):
        """Create service with mock database."""
        return TransactionService(mock_database)

    def test_get_categories_with_counts_delegates_to_repository(self, service):
        """Test service delegates to repository correctly."""
        # Arrange
        expected_categories = [('Groceries', 45), ('Dining Out', 23)]
        service.transaction_repo.get_categories_with_counts = Mock(return_value=expected_categories)

        # Act
        results = service.get_categories_with_counts()

        # Assert
        assert results == expected_categories
        service.transaction_repo.get_categories_with_counts.assert_called_once_with(account_id=None)

    def test_get_categories_with_counts_with_account_id(self, service):
        """Test service passes account_id to repository."""
        # Arrange
        service.transaction_repo.get_categories_with_counts = Mock(return_value=[])

        # Act
        service.get_categories_with_counts(account_id=5)

        # Assert
        service.transaction_repo.get_categories_with_counts.assert_called_once_with(account_id=5)

    def test_filter_by_categories_valid_list(self, service):
        """Test service filters with valid category list."""
        # Arrange
        mock_transaction = Transaction(
            id=1,
            account_id=5,
            date='2025-11-01',
            description='Test',
            category='Groceries',
            amount=Decimal('45.50'),
            type='expense'
        )
        service.transaction_repo.filter_by_categories = Mock(return_value=[mock_transaction])

        # Act
        results = service.filter_by_categories(['Groceries'])

        # Assert
        assert len(results) == 1
        assert results[0].category == 'Groceries'
        service.transaction_repo.filter_by_categories.assert_called_once_with(
            categories=['Groceries'],
            account_id=None
        )

    def test_filter_by_categories_none_raises_error(self, service):
        """Test service raises ValueError when categories is None."""
        # Act & Assert
        with pytest.raises(ValueError, match="Categories cannot be None"):
            service.filter_by_categories(None)

    def test_filter_by_categories_invalid_type_raises_error(self, service):
        """Test service raises ValueError when categories is not a list."""
        # Act & Assert
        with pytest.raises(ValueError, match="Categories must be a list"):
            service.filter_by_categories("Groceries")

        with pytest.raises(ValueError, match="Categories must be a list"):
            service.filter_by_categories(123)

    def test_filter_by_categories_sanitizes_whitespace(self, service):
        """Test service filters out empty and whitespace-only strings."""
        # Arrange
        service.transaction_repo.filter_by_categories = Mock(return_value=[])

        # Act - input has empty strings and whitespace
        service.filter_by_categories(['Groceries', '', '  ', 'Dining Out', '   \t  '])

        # Assert - only valid categories passed to repository
        service.transaction_repo.filter_by_categories.assert_called_once_with(
            categories=['Groceries', 'Dining Out'],
            account_id=None
        )

    def test_filter_by_categories_empty_after_sanitization(self, service):
        """Test service returns empty list when all categories are invalid."""
        # Arrange - Mock the repository method
        service.transaction_repo.filter_by_categories = Mock()

        # Act - all empty/whitespace strings
        results = service.filter_by_categories(['', '  ', '\t'])

        # Assert
        assert results == []
        # Repository should not be called
        service.transaction_repo.filter_by_categories.assert_not_called()
