"""
Integration tests for journal entry database triggers.

These tests verify that SQLite triggers correctly:
- Update account balances on insert/update/delete
- Validate journal entry constraints
- Prevent invalid operations
- Maintain data integrity

Story: US-002A - Journal Entry Foundation
Author: Tech Lead
Date: 2025-10-22
"""

import pytest
from decimal import Decimal
from finance_app.data.models import JournalEntry, EntryType, Account, AccountType, AccountSubtype, NormalBalance
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.utils.exceptions import DatabaseError


class TestJournalEntryTriggers:
    """Test database triggers for journal entries."""

    @pytest.fixture
    def account_repo(self, test_db):
        """Create account repository."""
        return AccountRepository(test_db)

    @pytest.fixture
    def journal_repo(self, test_db):
        """Create journal entry repository."""
        return JournalEntryRepository(test_db)

    @pytest.fixture
    def checking_account(self, account_repo):
        """Create test checking account."""
        account = Account(
            id=None,
            name="Test Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        )
        return account_repo.create(account)

    # ========================================================================
    # INSERT TRIGGER TESTS
    # ========================================================================

    def test_trigger_updates_balance_on_insert_debit(self, journal_repo, account_repo, checking_account):
        """Test trigger updates account balance when debit journal entry inserted."""
        initial_balance = checking_account.balance

        # Create debit entry (increase asset account)
        entry = JournalEntry(
            id=None,
            transaction_id=None,
            group_id=None,
            account_id=checking_account.id,
            entry_date="2025-10-22",
            description="Deposit",
            debit_amount=Decimal("500.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1500.00"),  # Will be verified
            entry_type=EntryType.TRANSACTION
        )

        created_entry = journal_repo.create(entry)

        # Verify trigger updated balance
        updated_account = account_repo.get_by_id(checking_account.id)
        assert updated_account.balance == initial_balance + Decimal("500.00")
        assert updated_account.balance == Decimal("1500.00")

    def test_trigger_updates_balance_on_insert_credit(self, journal_repo, account_repo, checking_account):
        """Test trigger updates account balance when credit journal entry inserted."""
        initial_balance = checking_account.balance

        # Create credit entry (decrease asset account)
        entry = JournalEntry(
            id=None,
            transaction_id=None,
            group_id=None,
            account_id=checking_account.id,
            entry_date="2025-10-22",
            description="Withdrawal",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("200.00"),
            balance_after=Decimal("800.00"),
            entry_type=EntryType.TRANSACTION
        )

        journal_repo.create(entry)

        # Verify trigger updated balance
        updated_account = account_repo.get_by_id(checking_account.id)
        assert updated_account.balance == initial_balance - Decimal("200.00")
        assert updated_account.balance == Decimal("800.00")

    # ========================================================================
    # DELETE TRIGGER TESTS
    # ========================================================================

    def test_trigger_reverses_balance_on_delete(self, journal_repo, account_repo, checking_account):
        """Test trigger reverses balance when journal entry deleted."""
        # Create entry
        entry = JournalEntry(
            id=None,
            account_id=checking_account.id,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("300.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1300.00"),
            entry_type=EntryType.TRANSACTION
        )
        created = journal_repo.create(entry)

        # Verify balance increased
        account_after_insert = account_repo.get_by_id(checking_account.id)
        assert account_after_insert.balance == Decimal("1300.00")

        # Delete entry
        journal_repo.delete(created.id)

        # Verify balance reversed
        account_after_delete = account_repo.get_by_id(checking_account.id)
        assert account_after_delete.balance == Decimal("1000.00")  # Back to original

    # ========================================================================
    # UPDATE TRIGGER TESTS
    # ========================================================================

    def test_trigger_updates_balance_on_amount_change(self, journal_repo, account_repo, checking_account):
        """Test trigger adjusts balance when journal entry amount updated."""
        # Create entry
        entry = JournalEntry(
            id=None,
            account_id=checking_account.id,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )
        created = journal_repo.create(entry)

        # Verify initial balance
        account = account_repo.get_by_id(checking_account.id)
        assert account.balance == Decimal("1100.00")

        # Update entry amount
        created.debit_amount = Decimal("200.00")  # Changed from 100 to 200
        journal_repo.update(created)

        # Verify trigger adjusted balance correctly
        # Old: +100, New: +200, Diff: +100
        updated_account = account_repo.get_by_id(checking_account.id)
        assert updated_account.balance == Decimal("1200.00")

    def test_trigger_prevents_account_id_change(self, journal_repo, account_repo, checking_account):
        """Test trigger prevents changing account_id of existing entry."""
        # Create second account
        savings = Account(
            id=None,
            name="Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            balance=Decimal("500.00"),
            normal_balance=NormalBalance.DEBIT
        )
        savings_account = account_repo.create(savings)

        # Create entry
        entry = JournalEntry(
            id=None,
            account_id=checking_account.id,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )
        created = journal_repo.create(entry)

        # Try to change account_id
        created.account_id = savings_account.id

        with pytest.raises(DatabaseError, match="Cannot change account_id"):
            journal_repo.update(created)

    # ========================================================================
    # VALIDATION TRIGGER TESTS
    # ========================================================================

    def test_trigger_rejects_both_debit_and_credit(self, journal_repo, checking_account):
        """Test trigger rejects entry with both debit and credit amounts."""
        entry = JournalEntry(
            id=None,
            account_id=checking_account.id,
            entry_date="2025-10-22",
            description="Invalid",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("50.00"),  # ❌ INVALID!
            balance_after=Decimal("1050.00"),
            entry_type=EntryType.TRANSACTION
        )

        with pytest.raises(DatabaseError, match="cannot have both debit and credit"):
            journal_repo.create(entry)

    def test_trigger_rejects_zero_amounts(self, journal_repo, checking_account):
        """Test trigger rejects entry with zero debit and credit."""
        entry = JournalEntry(
            id=None,
            account_id=checking_account.id,
            entry_date="2025-10-22",
            description="Invalid",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("0"),  # ❌ INVALID!
            balance_after=Decimal("1000.00"),
            entry_type=EntryType.TRANSACTION
        )

        with pytest.raises(DatabaseError, match="must have either debit or credit"):
            journal_repo.create(entry)

    def test_trigger_rejects_negative_amounts(self, journal_repo, checking_account):
        """Test trigger rejects entry with negative amounts."""
        entry = JournalEntry(
            id=None,
            account_id=checking_account.id,
            entry_date="2025-10-22",
            description="Invalid",
            debit_amount=Decimal("-100.00"),  # ❌ INVALID!
            credit_amount=Decimal("0"),
            balance_after=Decimal("900.00"),
            entry_type=EntryType.TRANSACTION
        )

        with pytest.raises(DatabaseError, match="must be non-negative"):
            journal_repo.create(entry)

    # ========================================================================
    # TRANSACTION ROLLBACK TESTS
    # ========================================================================

    def test_trigger_rollback_on_error(self, journal_repo, account_repo, checking_account):
        """Test that failed journal entry doesn't corrupt balance."""
        initial_balance = checking_account.balance

        # Try to create invalid entry (both debit and credit)
        with pytest.raises(DatabaseError):
            entry = JournalEntry(
                id=None,
                account_id=checking_account.id,
                entry_date="2025-10-22",
                description="Invalid",
                debit_amount=Decimal("100.00"),
                credit_amount=Decimal("50.00"),  # Invalid
                balance_after=Decimal("1050.00"),
                entry_type=EntryType.TRANSACTION
            )
            journal_repo.create(entry)

        # Verify balance unchanged (transaction rolled back)
        account = account_repo.get_by_id(checking_account.id)
        assert account.balance == initial_balance
        assert account.balance == Decimal("1000.00")

    # ========================================================================
    # AUDIT LOG TESTS
    # ========================================================================

    def test_trigger_audit_log_on_insert(self, test_db, journal_repo, checking_account):
        """Test trigger creates audit log entry on insert."""
        # Create journal entry
        entry = JournalEntry(
            id=None,
            account_id=checking_account.id,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )
        journal_repo.create(entry)

        # Check audit log
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT trigger_name, operation
                FROM trigger_audit
                WHERE trigger_name = 'update_account_balance_on_insert'
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            audit = cursor.fetchone()

        assert audit is not None
        assert audit['trigger_name'] == 'update_account_balance_on_insert'
        assert audit['operation'] == 'INSERT'

    # ========================================================================
    # MULTIPLE ENTRIES TEST
    # ========================================================================

    def test_trigger_handles_multiple_entries_correctly(self, journal_repo, account_repo, checking_account):
        """Test triggers handle multiple consecutive operations correctly."""
        initial_balance = checking_account.balance

        # Create 5 entries
        entries = []
        for i in range(5):
            entry = JournalEntry(
                id=None,
                account_id=checking_account.id,
                entry_date="2025-10-22",
                description=f"Entry {i}",
                debit_amount=Decimal("50.00"),
                credit_amount=Decimal("0"),
                balance_after=Decimal("0"),  # Will be calculated
                entry_type=EntryType.TRANSACTION
            )
            created = journal_repo.create(entry)
            entries.append(created)

        # Verify final balance
        final_account = account_repo.get_by_id(checking_account.id)
        expected_balance = initial_balance + (Decimal("50.00") * 5)
        assert final_account.balance == expected_balance
        assert final_account.balance == Decimal("1250.00")

        # Delete middle entry
        journal_repo.delete(entries[2].id)

        # Verify balance adjusted
        account_after_delete = account_repo.get_by_id(checking_account.id)
        assert account_after_delete.balance == Decimal("1200.00")  # -50 from deletion
