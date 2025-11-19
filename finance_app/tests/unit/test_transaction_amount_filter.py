"""
Unit tests for US-014: Amount Range Filter.

Tests amount filtering functionality in TransactionRepository and TransactionService.
Covers filter_by_amount_range() and parse_amount_string() methods.

Test Coverage:
- TestTransactionRepositoryAmountFilter: 7 tests (repository layer)
- TestTransactionServiceAmountFilter: 7 tests (service layer with validation)

Total: 14 unit tests

Created: 2025-11-18
Story: US-014 - Amount Range Filter (EPIC-002, Sprint 15)
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


class TestTransactionRepositoryAmountFilter:
    """Unit tests for TransactionRepository amount filter methods."""

    @pytest.fixture
    def mock_database(self):
        """Create mock database."""
        db = Mock(spec=Database)
        return db

    @pytest.fixture
    def repository(self, mock_database):
        """Create repository with mock database."""
        return TransactionRepository(mock_database)

    def test_filter_by_amount_min_only(self, repository, mock_database):
        """Test filtering with minimum amount only."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        # Mock transaction row with amount >= 100
        mock_row = {
            'id': 1,
            'account_id': 5,
            'date': '2025-11-01',
            'description': 'Large purchase',
            'category': 'Electronics',
            'amount': 150.00,
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
        results = repository.filter_by_amount_range(min_amount=Decimal("100"))

        # Assert
        assert len(results) == 1
        assert results[0].amount == Decimal("150.00")
        assert mock_cursor.execute.called
        # Verify query uses >= condition
        call_args = mock_cursor.execute.call_args[0]
        assert "amount >= ?" in call_args[0]
        assert call_args[1] == [100.0]

    def test_filter_by_amount_max_only(self, repository, mock_database):
        """Test filtering with maximum amount only."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        mock_row = {
            'id': 2,
            'account_id': 5,
            'date': '2025-11-01',
            'description': 'Small purchase',
            'category': 'Groceries',
            'amount': 15.00,
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
        results = repository.filter_by_amount_range(max_amount=Decimal("20"))

        # Assert
        assert len(results) == 1
        assert results[0].amount == Decimal("15.00")
        # Verify query uses <= condition
        call_args = mock_cursor.execute.call_args[0]
        assert "amount <= ?" in call_args[0]
        assert call_args[1] == [20.0]

    def test_filter_by_amount_both_min_max(self, repository, mock_database):
        """Test filtering with both min and max amounts."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        mock_row = {
            'id': 3,
            'account_id': 5,
            'date': '2025-11-01',
            'description': 'Mid-range purchase',
            'category': 'Dining Out',
            'amount': 50.00,
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
        results = repository.filter_by_amount_range(
            min_amount=Decimal("20"),
            max_amount=Decimal("100")
        )

        # Assert
        assert len(results) == 1
        assert results[0].amount == Decimal("50.00")
        # Verify query uses both >= and <= conditions
        call_args = mock_cursor.execute.call_args[0]
        assert "amount >= ?" in call_args[0]
        assert "amount <= ?" in call_args[0]
        assert "AND" in call_args[0]
        assert call_args[1] == [20.0, 100.0]

    def test_filter_by_amount_absolute_mode(self, repository, mock_database):
        """Test filtering with absolute value mode."""
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
        repository.filter_by_amount_range(
            min_amount=Decimal("100"),
            absolute=True
        )

        # Assert
        assert mock_cursor.execute.called
        # Verify query uses ABS() function
        call_args = mock_cursor.execute.call_args[0]
        assert "ABS(amount) >= ?" in call_args[0]
        assert call_args[1] == [100.0]

    def test_filter_by_amount_boundary_min_equals_max(self, repository, mock_database):
        """Test filtering when min equals max (exact amount match)."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_context.__exit__.return_value = None
        mock_database.get_connection.return_value = mock_context
        mock_conn.cursor.return_value = mock_cursor

        mock_row = {
            'id': 4,
            'account_id': 5,
            'date': '2025-11-01',
            'description': 'Exact amount',
            'category': 'Subscription',
            'amount': 100.00,
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
        results = repository.filter_by_amount_range(
            min_amount=Decimal("100.00"),
            max_amount=Decimal("100.00")
        )

        # Assert
        assert len(results) == 1
        assert results[0].amount == Decimal("100.00")
        # Verify both conditions present
        call_args = mock_cursor.execute.call_args[0]
        assert call_args[1] == [100.0, 100.0]

    def test_filter_by_amount_boundary_very_large_amounts(self, repository, mock_database):
        """Test filtering with very large amounts (999999.99)."""
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
        repository.filter_by_amount_range(
            min_amount=Decimal("999999.00"),
            max_amount=Decimal("999999.99")
        )

        # Assert
        assert mock_cursor.execute.called
        call_args = mock_cursor.execute.call_args[0]
        # Verify large amounts are handled correctly
        assert call_args[1] == [999999.00, 999999.99]

    def test_filter_by_amount_no_criteria(self, repository, mock_database):
        """Test filtering with no criteria returns empty list."""
        # Act
        results = repository.filter_by_amount_range()

        # Assert
        assert results == []
        # Verify no database call was made
        assert not mock_database.get_connection.called


class TestTransactionServiceAmountFilter:
    """Unit tests for TransactionService amount filter methods."""

    @pytest.fixture
    def mock_database(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_database):
        """Create service with mock database."""
        return TransactionService(mock_database)

    def test_filter_by_amount_validation_min_greater_max(self, service):
        """Test service raises ValueError when min > max."""
        # Act & Assert
        with pytest.raises(ValueError, match="must be <="):
            service.filter_by_amount_range(
                min_amount=Decimal("100"),
                max_amount=Decimal("50")
            )

    def test_filter_by_amount_no_criteria(self, service):
        """Test service returns empty list when no criteria specified."""
        # Act
        results = service.filter_by_amount_range()

        # Assert
        assert results == []

    def test_filter_by_amount_invalid_type_min_amount(self, service):
        """Test service raises ValueError when min_amount is not Decimal."""
        # Act & Assert
        with pytest.raises(ValueError, match="min_amount must be Decimal"):
            service.filter_by_amount_range(min_amount=100)  # int, not Decimal

        with pytest.raises(ValueError, match="min_amount must be Decimal"):
            service.filter_by_amount_range(min_amount="100")  # str, not Decimal

    def test_filter_by_amount_invalid_type_max_amount(self, service):
        """Test service raises ValueError when max_amount is not Decimal."""
        # Act & Assert
        with pytest.raises(ValueError, match="max_amount must be Decimal"):
            service.filter_by_amount_range(max_amount=50.0)  # float, not Decimal

    def test_parse_amount_string_valid(self, service):
        """Test parsing valid amount strings."""
        # Test basic amount
        assert service.parse_amount_string("100") == Decimal("100")

        # Test decimal amount
        assert service.parse_amount_string("50.99") == Decimal("50.99")

        # Test with dollar sign
        assert service.parse_amount_string("$100") == Decimal("100")

        # Test with thousands separator
        assert service.parse_amount_string("1,234.56") == Decimal("1234.56")

        # Test with whitespace
        assert service.parse_amount_string("  100.00  ") == Decimal("100.00")

        # Test negative amount
        assert service.parse_amount_string("-50.25") == Decimal("-50.25")

    def test_parse_amount_string_invalid(self, service):
        """Test parsing invalid strings returns None."""
        # Empty string
        assert service.parse_amount_string("") is None

        # Whitespace only
        assert service.parse_amount_string("   ") is None

        # Invalid format
        assert service.parse_amount_string("invalid") is None

        # Multiple decimals
        assert service.parse_amount_string("100.50.25") is None

    def test_parse_amount_string_with_currency_symbols(self, service):
        """Test parsing strings with various currency symbols."""
        # Dollar sign
        assert service.parse_amount_string("$100.00") == Decimal("100.00")

        # Pound sign
        assert service.parse_amount_string("£50.50") == Decimal("50.50")

        # Euro sign
        assert service.parse_amount_string("€75.25") == Decimal("75.25")

        # Combined with comma
        assert service.parse_amount_string("$1,234.56") == Decimal("1234.56")
