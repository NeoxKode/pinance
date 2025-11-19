"""
Integration tests for opening balance migration.

Tests end-to-end migration with real database.

Story: US-002B - Balanced Transaction Groups (Phase 1)
"""
import pytest
from decimal import Decimal
import sys
from pathlib import Path

# Add scripts to path for importing
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.migrate_opening_balances import migrate_opening_balances
from finance_app.data.database import Database
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance, EntryType
)
from finance_app.utils.admin_tools import AdminTools


class TestMigrationIntegration:
    """Integration tests for opening balance migration."""

    @pytest.fixture
    def populated_db(self, test_db):
        """Create database with sample accounts (no journal entries)."""
        account_repo = AccountRepository(test_db)

        # Create test accounts with various balances
        accounts = [
            Account(
                id=None,
                name="Test Checking",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                balance=Decimal("1000.00"),
                normal_balance=NormalBalance.DEBIT
            ),
            Account(
                id=None,
                name="Test Savings",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.SAVINGS,
                balance=Decimal("5000.00"),
                normal_balance=NormalBalance.DEBIT
            ),
            Account(
                id=None,
                name="Credit Card",
                account_type=AccountType.LIABILITY,
                account_subtype=AccountSubtype.CREDIT_CARD,
                balance=Decimal("-500.00"),  # Negative (owe money)
                normal_balance=NormalBalance.CREDIT
            ),
            Account(
                id=None,
                name="Zero Balance",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CASH,
                balance=Decimal("0.00"),
                normal_balance=NormalBalance.DEBIT
            ),
        ]

        for account in accounts:
            account_repo.create(account)

        return test_db

    def test_migrate_all_accounts_and_validate(self, populated_db, monkeypatch):
        """
        End-to-end migration test.

        1. Create test accounts with balances
        2. Run migration
        3. Verify journal entries created
        4. Run validate_balances
        5. Assert 100% valid
        """
        # Patch Database constructor to use our test database
        def mock_database(*args, **kwargs):
            return populated_db

        monkeypatch.setattr('scripts.migrate_opening_balances.Database', mock_database)

        # Get account and journal repos
        account_repo = AccountRepository(populated_db)
        journal_repo = JournalEntryRepository(populated_db)

        # Verify initial state: accounts have balances but no journal entries
        # Note: Database auto-creates Opening Balance Equity account, so we have 5 accounts
        accounts = account_repo.get_all()
        # Filter out the auto-created Opening Balance Equity for testing purposes
        test_accounts = [a for a in accounts if a.account_subtype != AccountSubtype.OPENING_BALANCE]
        assert len(test_accounts) == 4

        for account in test_accounts:
            entries = journal_repo.get_by_account(account.id)
            assert len(entries) == 0, f"Account {account.name} should have no entries before migration"

        # Run migration
        migrated, skipped = migrate_opening_balances(
            dry_run=False,
            opening_date="2025-01-01"
        )

        # Verify migration results (Opening Balance Equity has 0 balance, so +1 skipped)
        assert migrated == 3, "Should migrate 3 accounts with non-zero balances"
        assert skipped == 2, "Should skip 2 accounts with zero balance (Zero Balance + Opening Balance Equity)"

        # Verify journal entries created
        for account in test_accounts:
            entries = journal_repo.get_by_account(account.id)

            if account.balance == Decimal("0"):
                # Zero balance account should have no entries
                assert len(entries) == 0, f"Zero balance account should have no entries"
            else:
                # Non-zero accounts should have 1 OPENING entry
                assert len(entries) == 1, f"Account {account.name} should have 1 journal entry"

                entry = entries[0]
                assert entry.entry_type == EntryType.OPENING_BALANCE
                assert entry.entry_date == "2025-01-01"
                assert entry.reference_number == "OPENING-BALANCE"

                # Verify debit/credit logic
                if account.normal_balance == NormalBalance.DEBIT:
                    # Asset account with positive balance → debit
                    if account.balance > 0:
                        assert entry.debit_amount == abs(account.balance)
                        assert entry.credit_amount == Decimal("0")
                    else:
                        # Negative balance on asset → credit
                        assert entry.debit_amount == Decimal("0")
                        assert entry.credit_amount == abs(account.balance)
                else:
                    # Liability/Credit account with negative balance → credit
                    if account.balance < 0:
                        assert entry.credit_amount == abs(account.balance)
                        assert entry.debit_amount == Decimal("0")

        # Validate all account balances match journal
        admin_tools = AdminTools(populated_db)
        results = admin_tools.validate_all_account_balances()

        # All non-zero accounts should validate
        for result in results:
            if result.account_balance != Decimal("0"):
                assert result.is_valid, (
                    f"Account {result.account_name} should validate: "
                    f"account_balance={result.account_balance}, "
                    f"journal_balance={result.journal_balance}"
                )

    def test_migration_idempotency(self, populated_db, monkeypatch):
        """Running migration twice should not create duplicate entries."""
        # Patch Database constructor
        def mock_database(*args, **kwargs):
            return populated_db

        monkeypatch.setattr('scripts.migrate_opening_balances.Database', mock_database)

        account_repo = AccountRepository(populated_db)
        journal_repo = JournalEntryRepository(populated_db)

        # Run migration first time
        migrated1, skipped1 = migrate_opening_balances(
            dry_run=False,
            opening_date="2025-01-01"
        )

        assert migrated1 == 3
        assert skipped1 == 2  # Zero Balance + Opening Balance Equity

        # Count entries after first migration
        accounts = account_repo.get_all()
        entry_counts_before = {}
        for account in accounts:
            entries = journal_repo.get_by_account(account.id)
            entry_counts_before[account.id] = len(entries)

        # Run migration second time
        migrated2, skipped2 = migrate_opening_balances(
            dry_run=False,
            opening_date="2025-01-01"
        )

        # Should skip all accounts (already have opening entries)
        assert migrated2 == 0, "Second migration should not create new entries"
        assert skipped2 == 5, "Second migration should skip all accounts (4 test + 1 Opening Balance Equity)"

        # Verify entry counts unchanged
        for account in accounts:
            entries = journal_repo.get_by_account(account.id)
            assert len(entries) == entry_counts_before[account.id], (
                f"Account {account.name} should have same number of entries"
            )

    def test_migration_with_mixed_account_types(self, test_db, monkeypatch):
        """Test migration with various account types (asset, liability, equity)."""
        # Patch Database constructor
        def mock_database(*args, **kwargs):
            return test_db

        monkeypatch.setattr('scripts.migrate_opening_balances.Database', mock_database)

        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)

        # Create accounts of different types
        accounts_data = [
            # Asset account (normal balance: DEBIT)
            {
                "name": "Cash",
                "type": AccountType.ASSET,
                "subtype": AccountSubtype.CASH,
                "balance": Decimal("500.00"),
                "normal": NormalBalance.DEBIT,
                "expected_debit": Decimal("500.00"),
                "expected_credit": Decimal("0")
            },
            # Liability account (normal balance: CREDIT)
            {
                "name": "Loan",
                "type": AccountType.LIABILITY,
                "subtype": AccountSubtype.LOAN,
                "balance": Decimal("-1000.00"),  # Negative (owe)
                "normal": NormalBalance.CREDIT,
                "expected_debit": Decimal("0"),
                "expected_credit": Decimal("1000.00")
            },
            # Equity account (normal balance: CREDIT)
            # Note: Use RETAINED_EARNINGS instead of OPENING_BALANCE to avoid conflict
            # with auto-created Opening Balance Equity account
            {
                "name": "Retained Earnings",
                "type": AccountType.EQUITY,
                "subtype": AccountSubtype.RETAINED_EARNINGS,
                "balance": Decimal("2000.00"),  # Positive equity
                "normal": NormalBalance.CREDIT,
                "expected_debit": Decimal("0"),
                "expected_credit": Decimal("2000.00")
            },
        ]

        created_accounts = []
        for data in accounts_data:
            account = Account(
                id=None,
                name=data["name"],
                account_type=data["type"],
                account_subtype=data["subtype"],
                balance=data["balance"],
                normal_balance=data["normal"]
            )
            created = account_repo.create(account)
            created_accounts.append((created, data))

        # Run migration
        migrated, skipped = migrate_opening_balances(
            dry_run=False,
            opening_date="2025-01-01"
        )

        assert migrated == 3
        assert skipped == 1  # Auto-created Opening Balance Equity with 0 balance

        # Verify each account's journal entry
        for account, expected in created_accounts:
            entries = journal_repo.get_by_account(account.id)
            assert len(entries) == 1

            entry = entries[0]
            assert entry.entry_type == EntryType.OPENING_BALANCE

            # Verify correct debit/credit amounts
            assert entry.debit_amount == expected["expected_debit"], (
                f"Account {account.name} debit mismatch: "
                f"expected {expected['expected_debit']}, got {entry.debit_amount}"
            )
            assert entry.credit_amount == expected["expected_credit"], (
                f"Account {account.name} credit mismatch: "
                f"expected {expected['expected_credit']}, got {entry.credit_amount}"
            )
