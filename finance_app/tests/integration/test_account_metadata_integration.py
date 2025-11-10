"""
Integration tests for Account Metadata & Organization workflow.

Story: US-007 - Account Metadata & Organization
Sprint: 11

Test Coverage:
- Create accounts with metadata fields (2 tests)
- Update account metadata end-to-end (2 tests)
- Search accounts by multiple fields (3 tests)
- Institution autocomplete workflow (2 tests)
- Group accounts by institution (2 tests)
- Metadata field validation (2 tests)

Total: 13 integration tests
"""
import pytest
from decimal import Decimal

from finance_app.data.database import Database
from finance_app.data.models import (
    Account, AccountType, AccountSubtype
)
from finance_app.business.account_service import AccountService
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.utils.exceptions import ValidationError, NotFoundError


class TestCreateAccountsWithMetadata:
    """Integration tests for creating accounts with US-007 metadata fields."""

    def test_create_account_with_full_metadata(self, test_db):
        """Test creating account with all metadata fields populated."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create account with full metadata
        account = service.create_account(
            name="Chase Premier Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="5000.00"
        )

        # Update with metadata (using update_metadata service method)
        updated_account = service.update_metadata(
            account_id=account.id,
            account_number="1234-5678-9012",
            institution_name="Chase Bank",
            notes="Primary checking account for household expenses"
        )

        # Verify metadata persisted to database
        retrieved = account_repo.get_by_id(account.id)
        assert retrieved.account_number == "1234-5678-9012"
        assert retrieved.institution_name == "Chase Bank"
        assert "Primary checking account" in retrieved.notes
        assert retrieved.balance == Decimal("5000.00")

    def test_create_multiple_accounts_at_same_institution(self, test_db):
        """Test creating multiple accounts at the same institution."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create checking account at Chase
        checking = service.create_account(
            name="Chase Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="1000.00"
        )
        service.update_metadata(
            account_id=checking.id,
            account_number="1111-2222",
            institution_name="Chase Bank"
        )

        # Create savings account at Chase
        savings = service.create_account(
            name="Chase Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            initial_balance="5000.00"
        )
        service.update_metadata(
            account_id=savings.id,
            account_number="3333-4444",
            institution_name="Chase Bank"
        )

        # Create account at different institution
        wells = service.create_account(
            name="Wells Fargo Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="2000.00"
        )
        service.update_metadata(
            account_id=wells.id,
            account_number="5555-6666",
            institution_name="Wells Fargo"
        )

        # Verify all accounts persisted (includes Opening Balance Equity created by system)
        all_accounts = account_repo.get_all()
        assert len(all_accounts) == 4  # 3 created + 1 Opening Balance Equity

        # Verify institution names distinct
        institutions = account_repo.get_institution_names()
        assert len(institutions) == 2
        assert "Chase Bank" in institutions
        assert "Wells Fargo" in institutions


class TestUpdateAccountMetadata:
    """Integration tests for updating account metadata end-to-end."""

    def test_update_metadata_fields_incrementally(self, test_db):
        """Test updating metadata fields one at a time."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create basic account
        account = service.create_account(
            name="New Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="0.00"
        )

        # Update account number only
        service.update_metadata(account_id=account.id, account_number="1234-5678")
        retrieved = account_repo.get_by_id(account.id)
        assert retrieved.account_number == "1234-5678"
        assert retrieved.institution_name is None

        # Update institution name only
        service.update_metadata(account_id=account.id, institution_name="Chase Bank")
        retrieved = account_repo.get_by_id(account.id)
        assert retrieved.account_number == "1234-5678"  # Preserved
        assert retrieved.institution_name == "Chase Bank"

        # Update notes only
        service.update_metadata(account_id=account.id, notes="Emergency fund account")
        retrieved = account_repo.get_by_id(account.id)
        assert retrieved.account_number == "1234-5678"  # Preserved
        assert retrieved.institution_name == "Chase Bank"  # Preserved
        assert "Emergency fund" in retrieved.notes

    def test_update_metadata_with_validation_errors(self, test_db):
        """Test metadata validation catches errors during update."""
        service = AccountService(test_db)

        # Create account
        account = service.create_account(
            name="Test Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="0.00"
        )

        # Test account number too short (< 3 chars)
        with pytest.raises(ValueError, match="at least 3 characters"):
            service.update_metadata(account_id=account.id, account_number="12")

        # Test account number too long (> 50 chars)
        with pytest.raises(ValueError, match="cannot exceed 50 characters"):
            service.update_metadata(account_id=account.id, account_number="A" * 51)

        # Test institution name too long (> 100 chars)
        with pytest.raises(ValueError, match="cannot exceed 100 characters"):
            service.update_metadata(account_id=account.id, institution_name="B" * 101)

        # Test notes too long (> 1000 chars)
        with pytest.raises(ValueError, match="cannot exceed 1000 characters"):
            service.update_metadata(account_id=account.id, notes="C" * 1001)


class TestSearchAccountsByMetadata:
    """Integration tests for multi-field search functionality."""

    def test_search_by_account_name(self, test_db):
        """Test searching accounts by name."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create accounts
        chase = service.create_account(
            name="Chase Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="1000.00"
        )
        wells = service.create_account(
            name="Wells Fargo Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            initial_balance="5000.00"
        )

        # Search by name
        results = account_repo.search_accounts("Chase")
        assert len(results) == 1
        assert results[0].name == "Chase Checking"

    def test_search_by_account_number(self, test_db):
        """Test searching accounts by account number."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create account with account number
        account = service.create_account(
            name="My Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="1000.00"
        )
        service.update_metadata(
            account_id=account.id,
            account_number="1234-5678-9012"
        )

        # Search by partial account number
        results = account_repo.search_accounts("5678")
        assert len(results) == 1
        assert results[0].account_number == "1234-5678-9012"

    def test_search_by_institution_name(self, test_db):
        """Test searching accounts by institution name."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create accounts at different institutions
        chase1 = service.create_account(
            name="Chase Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="1000.00"
        )
        service.update_metadata(account_id=chase1.id, institution_name="Chase Bank")

        chase2 = service.create_account(
            name="Chase Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            initial_balance="5000.00"
        )
        service.update_metadata(account_id=chase2.id, institution_name="Chase Bank")

        wells = service.create_account(
            name="Wells Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="2000.00"
        )
        service.update_metadata(account_id=wells.id, institution_name="Wells Fargo")

        # Search by institution
        results = account_repo.search_accounts("Chase")
        assert len(results) == 2
        assert all("Chase" in r.institution_name for r in results)


class TestInstitutionAutocomplete:
    """Integration tests for institution autocomplete workflow."""

    def test_autocomplete_returns_matching_institutions(self, test_db):
        """Test autocomplete returns matching institution names."""
        service = AccountService(test_db)

        # Create accounts at different institutions
        acc1 = service.create_account(
            name="Account 1", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00"
        )
        service.update_metadata(account_id=acc1.id, institution_name="Chase Bank")

        acc2 = service.create_account(
            name="Account 2", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00"
        )
        service.update_metadata(account_id=acc2.id, institution_name="Charles Schwab")

        acc3 = service.create_account(
            name="Account 3", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00"
        )
        service.update_metadata(account_id=acc3.id, institution_name="Wells Fargo")

        # Test autocomplete with "Ch" prefix
        results = service.get_institution_autocomplete("Ch")
        assert len(results) == 2
        assert "Chase Bank" in results
        assert "Charles Schwab" in results
        assert "Wells Fargo" not in results

    def test_autocomplete_case_insensitive(self, test_db):
        """Test autocomplete is case-insensitive."""
        service = AccountService(test_db)

        # Create account
        acc = service.create_account(
            name="Account", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00"
        )
        service.update_metadata(account_id=acc.id, institution_name="Bank of America")

        # Test lowercase search
        results = service.get_institution_autocomplete("bank")
        assert len(results) == 1
        assert "Bank of America" in results

        # Test uppercase search
        results = service.get_institution_autocomplete("BANK")
        assert len(results) == 1
        assert "Bank of America" in results


class TestGroupByInstitution:
    """Integration tests for grouping accounts by institution."""

    def test_group_accounts_by_institution(self, test_db):
        """Test grouping accounts by institution name."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create accounts at different institutions
        chase1 = service.create_account(
            name="Chase Checking", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="1000.00"
        )
        service.update_metadata(account_id=chase1.id, institution_name="Chase Bank")

        chase2 = service.create_account(
            name="Chase Savings", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS, initial_balance="5000.00"
        )
        service.update_metadata(account_id=chase2.id, institution_name="Chase Bank")

        wells = service.create_account(
            name="Wells Checking", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="2000.00"
        )
        service.update_metadata(account_id=wells.id, institution_name="Wells Fargo")

        # Group by institution
        groups = account_repo.group_by_institution()

        # Verify grouping
        assert "Chase Bank" in groups
        assert "Wells Fargo" in groups
        assert len(groups["Chase Bank"]) == 2
        assert len(groups["Wells Fargo"]) == 1

        # Verify account details
        chase_accounts = groups["Chase Bank"]
        chase_names = [acc.name for acc in chase_accounts]
        assert "Chase Checking" in chase_names
        assert "Chase Savings" in chase_names

    def test_group_excludes_accounts_without_institution(self, test_db):
        """Test grouping excludes accounts without institution name."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create account with institution
        with_inst = service.create_account(
            name="Chase Checking", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="1000.00"
        )
        service.update_metadata(account_id=with_inst.id, institution_name="Chase Bank")

        # Create account without institution
        without_inst = service.create_account(
            name="Cash", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CASH, initial_balance="100.00"
        )

        # Group by institution
        groups = account_repo.group_by_institution()

        # Verify only Chase Bank group exists
        assert "Chase Bank" in groups
        assert len(groups) == 1  # Only one group
        assert groups["Chase Bank"][0].name == "Chase Checking"


class TestMetadataFieldValidation:
    """Integration tests for metadata field validation in full workflow."""

    def test_xss_prevention_in_notes_field(self, test_db):
        """Test XSS attack is prevented in notes field."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create account
        account = service.create_account(
            name="Test Account", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00"
        )

        # Attempt XSS in notes
        malicious_notes = "<script>alert('XSS')</script>"
        service.update_metadata(account_id=account.id, notes=malicious_notes)

        # Verify notes are HTML-escaped
        retrieved = account_repo.get_by_id(account.id)
        assert "<script>" not in retrieved.notes or "&lt;script&gt;" in retrieved.notes

    def test_account_number_format_validation(self, test_db):
        """Test account number format validation."""
        service = AccountService(test_db)

        # Create account
        account = service.create_account(
            name="Test Account", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00"
        )

        # Valid formats should pass
        valid_formats = [
            "1234-5678-9012",
            "123456789012",
            "****1234",
            "ACCT-1234-5678",
            "1234 5678 9012"
        ]

        for valid_format in valid_formats:
            service.update_metadata(account_id=account.id, account_number=valid_format)
            # Should not raise exception

        # Invalid format should fail (contains special chars not allowed)
        with pytest.raises(ValueError, match="Invalid account number format"):
            service.update_metadata(account_id=account.id, account_number="1234@#$%")
