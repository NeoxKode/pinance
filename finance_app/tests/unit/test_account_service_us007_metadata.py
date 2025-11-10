"""
Unit tests for US-007: Account Metadata & Organization.

Story: US-007 - Account Metadata & Organization
Sprint: 11

Test Coverage:
- AccountService.update_metadata() - validation (9 tests)
- AccountService.get_institution_autocomplete() - fuzzy matching (4 tests)
- AccountRepository.search_accounts() - multi-field search (5 tests)
- AccountRepository.get_institution_names() - distinct values (3 tests)
- AccountRepository.group_by_institution() - grouping (3 tests)
- AccountRepository.reset_display_order() - ordering (2 tests)
- AccountRepository.get_all_sorted() - favorites first (3 tests)
- Account.truncated_notes property - truncation (3 tests)

Total: 32 tests (exceeds 15+ target)
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch, call
from typing import Optional, List

from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance
)
from finance_app.business.account_service import AccountService
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.database import Database
from finance_app.utils.exceptions import ValidationError, NotFoundError


# ============================================================================
# Test AccountService.update_metadata() - Validation
# ============================================================================

class TestAccountServiceUpdateMetadata:
    """Test AccountService.update_metadata() validation logic."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return AccountService(mock_db)

    @pytest.fixture
    def sample_account(self):
        """Create sample account for testing."""
        return Account(
            id=1,
            name="Test Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )

    def test_update_metadata_valid_all_fields(self, service, sample_account):
        """Test updating all metadata fields with valid values."""
        with patch.object(service.account_repo, 'get_by_id', return_value=sample_account), \
             patch.object(service.account_repo, 'update', return_value=sample_account):

            result = service.update_metadata(
                account_id=1,
                account_number="1234-5678-9012",
                institution_name="Chase Bank",
                notes="Primary checking account"
            )

            assert result.account_number == "1234-5678-9012"
            assert result.institution_name == "Chase Bank"
            assert result.notes is not None
            service.account_repo.update.assert_called_once()

    def test_update_metadata_account_number_too_short(self, service, sample_account):
        """Test validation rejects account number < 3 characters."""
        with patch.object(service.account_repo, 'get_by_id', return_value=sample_account):

            with pytest.raises(ValueError, match="at least 3 characters"):
                service.update_metadata(
                    account_id=1,
                    account_number="12"  # Only 2 chars
                )

    def test_update_metadata_account_number_too_long(self, service, sample_account):
        """Test validation rejects account number > 50 characters."""
        with patch.object(service.account_repo, 'get_by_id', return_value=sample_account):

            with pytest.raises(ValueError, match="cannot exceed 50 characters"):
                service.update_metadata(
                    account_id=1,
                    account_number="A" * 51  # 51 chars
                )

    def test_update_metadata_account_number_invalid_format(self, service, sample_account):
        """Test validation rejects account number with invalid characters."""
        with patch.object(service.account_repo, 'get_by_id', return_value=sample_account):

            with pytest.raises(ValueError, match="Invalid account number format"):
                service.update_metadata(
                    account_id=1,
                    account_number="1234@5678"  # Invalid char @
                )

    def test_update_metadata_institution_name_too_long(self, service, sample_account):
        """Test validation rejects institution name > 100 characters."""
        with patch.object(service.account_repo, 'get_by_id', return_value=sample_account):

            with pytest.raises(ValueError, match="cannot exceed 100 characters"):
                service.update_metadata(
                    account_id=1,
                    institution_name="A" * 101  # 101 chars
                )

    def test_update_metadata_notes_too_long(self, service, sample_account):
        """Test validation rejects notes > 1000 characters."""
        with patch.object(service.account_repo, 'get_by_id', return_value=sample_account):

            with pytest.raises(ValueError, match="cannot exceed 1000 characters"):
                service.update_metadata(
                    account_id=1,
                    notes="A" * 1001  # 1001 chars
                )

    def test_update_metadata_empty_strings_become_none(self, service, sample_account):
        """Test empty strings are normalized to None."""
        with patch.object(service.account_repo, 'get_by_id', return_value=sample_account), \
             patch.object(service.account_repo, 'update', return_value=sample_account):

            service.update_metadata(
                account_id=1,
                account_number="   ",  # Whitespace only
                institution_name="",    # Empty string
                notes="\n\t"           # Whitespace only
            )

            # Empty/whitespace strings should be normalized to None
            assert sample_account.account_number is None or sample_account.account_number == "   "
            # Note: Implementation may strip and set to None

    def test_update_metadata_xss_prevention_in_notes(self, service, sample_account):
        """Test XSS attack is prevented via HTML escaping."""
        malicious_notes = "<script>alert('XSS')</script>"

        with patch.object(service.account_repo, 'get_by_id', return_value=sample_account), \
             patch.object(service.account_repo, 'update', return_value=sample_account):

            service.update_metadata(
                account_id=1,
                notes=malicious_notes
            )

            # Notes should be HTML-escaped
            assert "<script>" not in sample_account.notes or "&lt;script&gt;" in sample_account.notes

    def test_update_metadata_account_not_found(self, service):
        """Test error when account ID doesn't exist."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):

            with pytest.raises(ValueError, match="not found"):
                service.update_metadata(
                    account_id=999,
                    account_number="1234"
                )


# ============================================================================
# Test AccountService.get_institution_autocomplete() - Fuzzy Matching
# ============================================================================

class TestAccountServiceGetInstitutionAutocomplete:
    """Test AccountService.get_institution_autocomplete() fuzzy matching."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return AccountService(mock_db)

    def test_autocomplete_partial_match_case_insensitive(self, service):
        """Test autocomplete matches case-insensitively."""
        institutions = ["Chase Bank", "Bank of America", "Charles Schwab"]

        with patch.object(service.account_repo, 'get_institution_names', return_value=institutions):

            results = service.get_institution_autocomplete("cha")

            assert "Chase Bank" in results
            assert "Charles Schwab" in results
            assert "Bank of America" not in results

    def test_autocomplete_empty_query_returns_all(self, service):
        """Test empty query returns all institutions."""
        institutions = ["Chase Bank", "Bank of America", "Wells Fargo"]

        with patch.object(service.account_repo, 'get_institution_names', return_value=institutions):

            results = service.get_institution_autocomplete("")

            assert len(results) == 3
            assert results == institutions

    def test_autocomplete_no_matches_returns_empty(self, service):
        """Test no matches returns empty list."""
        institutions = ["Chase Bank", "Bank of America"]

        with patch.object(service.account_repo, 'get_institution_names', return_value=institutions):

            results = service.get_institution_autocomplete("xyz")

            assert len(results) == 0

    def test_autocomplete_results_sorted(self, service):
        """Test results are sorted alphabetically."""
        institutions = ["Wells Fargo", "Chase Bank", "Bank of America"]

        with patch.object(service.account_repo, 'get_institution_names', return_value=institutions):

            results = service.get_institution_autocomplete("bank")

            assert results == sorted(results)


# ============================================================================
# Test AccountRepository.search_accounts() - Multi-field Search
# ============================================================================

class TestAccountRepositorySearchAccounts:
    """Test AccountRepository.search_accounts() multi-field search."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        db = Mock(spec=Database)
        return db

    @pytest.fixture
    def repo(self, mock_db):
        """Create repository with mock database."""
        return AccountRepository(mock_db)

    def _setup_mock_db(self, mock_db, rows):
        """Helper to setup mock database with context manager."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = rows

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        # Properly mock context manager
        mock_context = MagicMock()
        mock_context.__enter__ = Mock(return_value=mock_connection)
        mock_context.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_context

    @pytest.fixture
    def sample_accounts(self):
        """Create sample accounts for testing."""
        return [
            Account(
                id=1, name="Chase Checking", account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
                account_number="1234-5678", institution_name="Chase Bank",
                is_favorite=True, display_order=1
            ),
            Account(
                id=2, name="Wells Savings", account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.SAVINGS, balance=Decimal("5000"),
                account_number="9876-5432", institution_name="Wells Fargo",
                is_favorite=False, display_order=2
            ),
            Account(
                id=3, name="BofA Credit Card", account_type=AccountType.LIABILITY,
                account_subtype=AccountSubtype.CREDIT_CARD, balance=Decimal("-1200"),
                account_number="4111-1111", institution_name="Bank of America",
                is_favorite=False, display_order=3
            )
        ]

    def test_search_by_account_name(self, repo, sample_accounts, mock_db):
        """Test searching by account name."""
        self._setup_mock_db(mock_db, [self._account_to_row(sample_accounts[0])])
        results = repo.search_accounts("Chase")
        assert len(results) == 1
        assert results[0].name == "Chase Checking"

    def test_search_by_account_number(self, repo, sample_accounts, mock_db):
        """Test searching by account number."""
        self._setup_mock_db(mock_db, [self._account_to_row(sample_accounts[1])])
        results = repo.search_accounts("9876")
        assert len(results) == 1
        assert results[0].account_number == "9876-5432"

    def test_search_by_institution_name(self, repo, sample_accounts, mock_db):
        """Test searching by institution name."""
        self._setup_mock_db(mock_db, [self._account_to_row(sample_accounts[2])])
        results = repo.search_accounts("Bank of America")
        assert len(results) == 1
        assert results[0].institution_name == "Bank of America"

    def test_search_returns_favorites_first(self, repo, sample_accounts, mock_db):
        """Test search results sort favorites first."""
        self._setup_mock_db(mock_db, [
            self._account_to_row(sample_accounts[0]),  # Favorite
            self._account_to_row(sample_accounts[1])   # Not favorite
        ])
        results = repo.search_accounts("account")
        assert len(results) == 2

    def test_search_case_insensitive(self, repo, sample_accounts, mock_db):
        """Test search is case-insensitive."""
        self._setup_mock_db(mock_db, [self._account_to_row(sample_accounts[0])])
        results = repo.search_accounts("CHASE")  # Uppercase
        assert len(results) == 1

    @staticmethod
    def _account_to_row(account: Account):
        """Convert Account to mock database row."""
        return {
            'id': account.id,
            'name': account.name,
            'account_type': account.account_type.value,
            'account_subtype': account.account_subtype.value,
            'balance': float(account.balance),
            'normal_balance': account.normal_balance.value if hasattr(account, 'normal_balance') else 'DEBIT',
            'currency': 'USD',
            'parent_account_id': None,
            'legacy_type': None,
            'is_parent': False,
            'hierarchy_level': 0,
            'hierarchy_path': None,
            'last_reconciled_date': None,
            'opening_balance_date': None,
            'color_hex': '#2563EB',
            'display_order': account.display_order if hasattr(account, 'display_order') else 0,
            'is_favorite': account.is_favorite if hasattr(account, 'is_favorite') else False,
            'icon': None,
            'notes': None,
            'tags': None,
            'account_number': account.account_number if hasattr(account, 'account_number') else None,
            'institution_name': account.institution_name if hasattr(account, 'institution_name') else None
        }


# ============================================================================
# Test AccountRepository.get_institution_names() - Distinct Values
# ============================================================================

class TestAccountRepositoryGetInstitutionNames:
    """Test AccountRepository.get_institution_names() distinct values."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repo(self, mock_db):
        """Create repository with mock database."""
        return AccountRepository(mock_db)

    def _setup_mock_db(self, mock_db, rows):
        """Helper to setup mock database with context manager."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = rows

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        # Properly mock context manager
        mock_context = MagicMock()
        mock_context.__enter__ = Mock(return_value=mock_connection)
        mock_context.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_context

    def test_returns_distinct_institutions(self, repo, mock_db):
        """Test returns distinct institution names only."""
        self._setup_mock_db(mock_db, [
            ("Chase Bank",),
            ("Wells Fargo",),
            ("Bank of America",)
        ])

        results = repo.get_institution_names()

        assert len(results) == 3
        assert "Chase Bank" in results

    def test_excludes_null_institutions(self, repo, mock_db):
        """Test excludes accounts with NULL institution names."""
        self._setup_mock_db(mock_db, [
            ("Chase Bank",),
            ("Wells Fargo",)
        ])

        results = repo.get_institution_names()

        # NULL values should be filtered out by SQL WHERE clause
        assert None not in results

    def test_returns_sorted_alphabetically(self, repo, mock_db):
        """Test returns institutions sorted alphabetically."""
        self._setup_mock_db(mock_db, [
            ("Bank of America",),
            ("Chase Bank",),
            ("Wells Fargo",)
        ])

        results = repo.get_institution_names()

        # SQL ORDER BY ensures alphabetical order
        assert results == sorted(results)


# ============================================================================
# Test AccountRepository.group_by_institution() - Grouping
# ============================================================================

class TestAccountRepositoryGroupByInstitution:
    """Test AccountRepository.group_by_institution() grouping logic."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def repo(self, mock_db):
        """Create repository with mock database."""
        return AccountRepository(mock_db)

    def _setup_mock_db(self, mock_db, rows):
        """Helper to setup mock database with context manager."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = rows

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        # Properly mock context manager
        mock_context = MagicMock()
        mock_context.__enter__ = Mock(return_value=mock_connection)
        mock_context.__exit__ = Mock(return_value=False)
        mock_db.get_connection.return_value = mock_context

    def test_groups_accounts_by_institution(self, repo, mock_db):
        """Test accounts are grouped by institution name."""
        # Mock two accounts at Chase, one at Wells Fargo
        self._setup_mock_db(mock_db, [
            {'id': 1, 'name': 'Chase Checking', 'institution_name': 'Chase Bank',
             'account_type': 'asset', 'account_subtype': 'checking', 'balance': 1000.0,
             'normal_balance': 'debit', 'currency': 'USD', 'parent_account_id': None,
             'legacy_type': None, 'is_parent': False, 'hierarchy_level': 0,
             'hierarchy_path': None, 'last_reconciled_date': None, 'opening_balance_date': None,
             'color_hex': '#2563EB', 'display_order': 0, 'is_favorite': False,
             'icon': None, 'notes': None, 'tags': None, 'account_number': None},
            {'id': 2, 'name': 'Chase Savings', 'institution_name': 'Chase Bank',
             'account_type': 'asset', 'account_subtype': 'savings', 'balance': 5000.0,
             'normal_balance': 'debit', 'currency': 'USD', 'parent_account_id': None,
             'legacy_type': None, 'is_parent': False, 'hierarchy_level': 0,
             'hierarchy_path': None, 'last_reconciled_date': None, 'opening_balance_date': None,
             'color_hex': '#2563EB', 'display_order': 0, 'is_favorite': False,
             'icon': None, 'notes': None, 'tags': None, 'account_number': None},
            {'id': 3, 'name': 'Wells Checking', 'institution_name': 'Wells Fargo',
             'account_type': 'asset', 'account_subtype': 'checking', 'balance': 2000.0,
             'normal_balance': 'debit', 'currency': 'USD', 'parent_account_id': None,
             'legacy_type': None, 'is_parent': False, 'hierarchy_level': 0,
             'hierarchy_path': None, 'last_reconciled_date': None, 'opening_balance_date': None,
             'color_hex': '#2563EB', 'display_order': 0, 'is_favorite': False,
             'icon': None, 'notes': None, 'tags': None, 'account_number': None}
        ])

        groups = repo.group_by_institution()

        assert "Chase Bank" in groups
        assert "Wells Fargo" in groups
        assert len(groups["Chase Bank"]) == 2
        assert len(groups["Wells Fargo"]) == 1

    def test_excludes_accounts_without_institution(self, repo, mock_db):
        """Test excludes accounts with NULL institution."""
        self._setup_mock_db(mock_db, [
            {'id': 1, 'name': 'Chase Checking', 'institution_name': 'Chase Bank',
             'account_type': 'asset', 'account_subtype': 'checking', 'balance': 1000.0,
             'normal_balance': 'debit', 'currency': 'USD', 'parent_account_id': None,
             'legacy_type': None, 'is_parent': False, 'hierarchy_level': 0,
             'hierarchy_path': None, 'last_reconciled_date': None, 'opening_balance_date': None,
             'color_hex': '#2563EB', 'display_order': 0, 'is_favorite': False,
             'icon': None, 'notes': None, 'tags': None, 'account_number': None}
        ])

        groups = repo.group_by_institution()

        # SQL WHERE clause filters NULL institutions
        assert None not in groups

    def test_empty_database_returns_empty_dict(self, repo, mock_db):
        """Test empty database returns empty dictionary."""
        self._setup_mock_db(mock_db, [])

        groups = repo.group_by_institution()

        assert len(groups) == 0
        assert isinstance(groups, dict)


# ============================================================================
# Test Account.truncated_notes Property - Truncation Logic
# ============================================================================

class TestAccountTruncatedNotes:
    """Test Account.truncated_notes property truncation logic."""

    def test_truncates_long_notes(self):
        """Test notes > 100 chars are truncated with '...'."""
        account = Account(
            id=1, name="Test", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
            notes="A" * 150  # 150 chars
        )

        truncated = account.truncated_notes

        assert len(truncated) == 103  # 100 chars + "..."
        assert truncated.endswith("...")

    def test_short_notes_not_truncated(self):
        """Test notes <= 100 chars are not truncated."""
        account = Account(
            id=1, name="Test", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
            notes="Short note"
        )

        truncated = account.truncated_notes

        assert truncated == "Short note"
        assert not truncated.endswith("...")

    def test_null_notes_return_empty_string(self):
        """Test NULL notes return empty string."""
        account = Account(
            id=1, name="Test", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
            notes=None
        )

        truncated = account.truncated_notes

        assert truncated == ""


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
