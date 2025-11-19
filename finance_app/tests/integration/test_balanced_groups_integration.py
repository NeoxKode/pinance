"""
Integration tests for balanced transaction groups.

Tests end-to-end group creation with real database.

Story: US-002B - Balanced Transaction Groups (Phase 2)
"""
import pytest
from decimal import Decimal

from finance_app.data.database import Database
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.data.repositories.transaction_group_repository import TransactionGroupRepository
from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance,
    JournalEntry, EntryType, TransactionGroup
)
from finance_app.utils.exceptions import ValidationError


class TestBalancedGroupsIntegration:
    """Integration tests for balanced transaction groups."""

    @pytest.fixture
    def test_accounts(self, test_db):
        """Create test accounts."""
        account_repo = AccountRepository(test_db)

        checking = account_repo.create(Account(
            id=None,
            name="Test Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        ))

        savings = account_repo.create(Account(
            id=None,
            name="Test Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            balance=Decimal("500.00"),
            normal_balance=NormalBalance.DEBIT
        ))

        return {"checking": checking, "savings": savings}

    def test_create_balanced_transfer(self, test_db, test_accounts):
        """
        Test creating a balanced transfer between two accounts.

        Transfer $200 from Checking to Savings.
        """
        journal_repo = JournalEntryRepository(test_db)
        checking = test_accounts["checking"]
        savings = test_accounts["savings"]

        # Create balanced group: Transfer $200 from checking to savings
        entries = [
            JournalEntry(
                id=None,
                account_id=checking.id,
                entry_date="2025-10-22",
                description="Transfer to savings",
                debit_amount=Decimal("0.00"),
                credit_amount=Decimal("200.00"),  # Decrease checking
                balance_after=Decimal("0.00"),  # Will be calculated
                entry_type=EntryType.TRANSFER
            ),
            JournalEntry(
                id=None,
                account_id=savings.id,
                entry_date="2025-10-22",
                description="Transfer from checking",
                debit_amount=Decimal("200.00"),  # Increase savings
                credit_amount=Decimal("0.00"),
                balance_after=Decimal("0.00"),  # Will be calculated
                entry_type=EntryType.TRANSFER
            )
        ]

        group, created_entries = journal_repo.create_balanced_group(
            entries,
            group_date="2025-10-22",
            description="Transfer: Checking → Savings",
            notes="Test transfer"
        )

        # Verify group
        assert group.id is not None
        assert group.total_debits == Decimal("200.00")
        assert group.total_credits == Decimal("200.00")
        assert group.is_balanced is True
        assert len(created_entries) == 2

        # Verify all entries have the same group_id
        assert all(e.group_id == group.id for e in created_entries)

        # Verify account balances updated
        account_repo = AccountRepository(test_db)
        updated_checking = account_repo.get_by_id(checking.id)
        updated_savings = account_repo.get_by_id(savings.id)

        assert updated_checking.balance == Decimal("800.00")  # 1000 - 200
        assert updated_savings.balance == Decimal("700.00")   # 500 + 200

    def test_unbalanced_group_rejected(self, test_db, test_accounts):
        """Unbalanced group (debits != credits) should raise ValidationError."""
        journal_repo = JournalEntryRepository(test_db)
        checking = test_accounts["checking"]
        savings = test_accounts["savings"]

        # Create UNBALANCED entries (debits != credits)
        entries = [
            JournalEntry(
                id=None,
                account_id=checking.id,
                entry_date="2025-10-22",
                description="Unbalanced",
                debit_amount=Decimal("0.00"),
                credit_amount=Decimal("300.00"),  # Credit 300
                balance_after=Decimal("0.00"),
                entry_type=EntryType.TRANSFER
            ),
            JournalEntry(
                id=None,
                account_id=savings.id,
                entry_date="2025-10-22",
                description="Unbalanced",
                debit_amount=Decimal("200.00"),  # Debit 200 (NOT BALANCED!)
                credit_amount=Decimal("0.00"),
                balance_after=Decimal("0.00"),
                entry_type=EntryType.TRANSFER
            )
        ]

        with pytest.raises(ValidationError, match="must be balanced"):
            journal_repo.create_balanced_group(
                entries,
                group_date="2025-10-22",
                description="Unbalanced transfer"
            )

        # Verify accounts unchanged
        account_repo = AccountRepository(test_db)
        checking_after = account_repo.get_by_id(checking.id)
        savings_after = account_repo.get_by_id(savings.id)

        assert checking_after.balance == Decimal("1000.00")  # Unchanged
        assert savings_after.balance == Decimal("500.00")    # Unchanged

    def test_single_entry_group_rejected(self, test_db, test_accounts):
        """Group with only 1 entry should raise ValidationError."""
        journal_repo = JournalEntryRepository(test_db)
        checking = test_accounts["checking"]

        entries = [
            JournalEntry(
                id=None,
                account_id=checking.id,
                entry_date="2025-10-22",
                description="Single entry",
                debit_amount=Decimal("100.00"),
                credit_amount=Decimal("0.00"),
                balance_after=Decimal("0.00"),
                entry_type=EntryType.TRANSFER
            )
        ]

        with pytest.raises(ValidationError, match="at least 2"):
            journal_repo.create_balanced_group(
                entries,
                group_date="2025-10-22",
                description="Single entry group"
            )

    def test_mismatched_dates_rejected(self, test_db, test_accounts):
        """Entries with different dates should raise ValidationError."""
        journal_repo = JournalEntryRepository(test_db)
        checking = test_accounts["checking"]
        savings = test_accounts["savings"]

        entries = [
            JournalEntry(
                id=None,
                account_id=checking.id,
                entry_date="2025-10-22",  # Date 1
                description="Entry 1",
                debit_amount=Decimal("0.00"),
                credit_amount=Decimal("100.00"),
                balance_after=Decimal("0.00"),
                entry_type=EntryType.TRANSFER
            ),
            JournalEntry(
                id=None,
                account_id=savings.id,
                entry_date="2025-10-23",  # Date 2 (DIFFERENT!)
                description="Entry 2",
                debit_amount=Decimal("100.00"),
                credit_amount=Decimal("0.00"),
                balance_after=Decimal("0.00"),
                entry_type=EntryType.TRANSFER
            )
        ]

        with pytest.raises(ValidationError, match="same date"):
            journal_repo.create_balanced_group(
                entries,
                group_date="2025-10-22",
                description="Mismatched dates"
            )

    def test_multi_entry_group(self, test_db, test_accounts):
        """
        Test creating a balanced group with more than 2 entries.

        Scenario: Split $300 from Checking into $200 to Savings and $100 to Cash.
        """
        # Add a cash account
        account_repo = AccountRepository(test_db)
        cash = account_repo.create(Account(
            id=None,
            name="Cash",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CASH,
            balance=Decimal("100.00"),
            normal_balance=NormalBalance.DEBIT
        ))

        journal_repo = JournalEntryRepository(test_db)
        checking = test_accounts["checking"]
        savings = test_accounts["savings"]

        # Create 3-entry balanced group
        entries = [
            JournalEntry(
                id=None,
                account_id=checking.id,
                entry_date="2025-10-22",
                description="Split withdrawal",
                debit_amount=Decimal("0.00"),
                credit_amount=Decimal("300.00"),  # Decrease checking by 300
                balance_after=Decimal("0.00"),
                entry_type=EntryType.TRANSFER
            ),
            JournalEntry(
                id=None,
                account_id=savings.id,
                entry_date="2025-10-22",
                description="Split deposit (part 1)",
                debit_amount=Decimal("200.00"),  # Increase savings by 200
                credit_amount=Decimal("0.00"),
                balance_after=Decimal("0.00"),
                entry_type=EntryType.TRANSFER
            ),
            JournalEntry(
                id=None,
                account_id=cash.id,
                entry_date="2025-10-22",
                description="Split deposit (part 2)",
                debit_amount=Decimal("100.00"),  # Increase cash by 100
                credit_amount=Decimal("0.00"),
                balance_after=Decimal("0.00"),
                entry_type=EntryType.TRANSFER
            )
        ]

        group, created_entries = journal_repo.create_balanced_group(
            entries,
            group_date="2025-10-22",
            description="Split transfer: Checking → Savings + Cash"
        )

        # Verify group
        assert group.total_debits == Decimal("300.00")
        assert group.total_credits == Decimal("300.00")
        assert len(created_entries) == 3

        # Verify balances
        checking_after = account_repo.get_by_id(checking.id)
        savings_after = account_repo.get_by_id(savings.id)
        cash_after = account_repo.get_by_id(cash.id)

        assert checking_after.balance == Decimal("700.00")  # 1000 - 300
        assert savings_after.balance == Decimal("700.00")   # 500 + 200
        assert cash_after.balance == Decimal("200.00")      # 100 + 100

    def test_transaction_group_repository_crud(self, test_db):
        """Test TransactionGroupRepository CRUD operations."""
        group_repo = TransactionGroupRepository(test_db)

        # Create
        group = group_repo.create(TransactionGroup(
            id=None,
            group_date="2025-10-22",
            description="Test group",
            notes="Test notes",
            total_debits=Decimal("500.00"),
            total_credits=Decimal("500.00")
        ))

        assert group.id is not None
        assert group.created_at is not None

        # Read
        retrieved = group_repo.get_by_id(group.id)
        assert retrieved.description == "Test group"
        assert retrieved.total_debits == Decimal("500.00")

        # Update
        retrieved.description = "Updated description"
        updated = group_repo.update(retrieved)
        assert updated.description == "Updated description"

        # Get all
        all_groups = group_repo.get_all()
        assert len(all_groups) >= 1

        # Delete
        group_repo.delete(group.id)
        deleted = group_repo.get_by_id(group.id)
        assert deleted is None

    def test_get_unbalanced_groups(self, test_db):
        """Test finding unbalanced groups (should be none in healthy system)."""
        group_repo = TransactionGroupRepository(test_db)

        # All groups should be balanced (validated on creation)
        unbalanced = group_repo.get_unbalanced_groups()
        assert len(unbalanced) == 0
