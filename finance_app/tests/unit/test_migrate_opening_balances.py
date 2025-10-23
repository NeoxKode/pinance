"""
Unit tests for opening balance migration.

Story: US-002B - Balanced Transaction Groups (Phase 1)
"""
import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance,
    JournalEntry, EntryType
)


class TestMigrateOpeningBalances:
    """Test opening balance migration logic."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for migration."""
        with patch('scripts.migrate_opening_balances.Database') as mock_db, \
             patch('scripts.migrate_opening_balances.AccountRepository') as mock_account_repo, \
             patch('scripts.migrate_opening_balances.JournalEntryRepository') as mock_journal_repo, \
             patch('scripts.migrate_opening_balances.DoubleEntryService') as mock_service:

            # Configure mocks
            account_repo_instance = Mock()
            journal_repo_instance = Mock()
            service_instance = Mock()

            mock_account_repo.return_value = account_repo_instance
            mock_journal_repo.return_value = journal_repo_instance
            mock_service.return_value = service_instance

            yield {
                'account_repo': account_repo_instance,
                'journal_repo': journal_repo_instance,
                'service': service_instance
            }

    def test_migrate_account_with_positive_balance(self, mock_dependencies):
        """Positive balance → creates journal entry with correct amount."""
        from scripts.migrate_opening_balances import migrate_opening_balances

        # Arrange
        account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )

        mock_dependencies['account_repo'].get_all.return_value = [account]
        mock_dependencies['journal_repo'].get_by_account.return_value = []  # No existing entries

        mock_entry = JournalEntry(
            id=1,
            account_id=1,
            entry_date="2025-01-01",
            description="Opening balance for Checking",
            debit_amount=Decimal("1000.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1000.00"),
            entry_type=EntryType.OPENING_BALANCE
        )
        mock_dependencies['service'].create_simple_transaction.return_value = mock_entry

        # Act
        migrated, skipped = migrate_opening_balances(dry_run=False, opening_date="2025-01-01")

        # Assert
        assert migrated == 1
        assert skipped == 0
        mock_dependencies['service'].create_simple_transaction.assert_called_once()

        # Verify call arguments
        call_args = mock_dependencies['service'].create_simple_transaction.call_args
        assert call_args[1]['account_id'] == 1
        assert call_args[1]['amount'] == Decimal("1000.00")
        assert call_args[1]['entry_type'] == EntryType.OPENING_BALANCE

    def test_migrate_account_with_negative_balance(self, mock_dependencies):
        """Negative balance (liability) → creates journal entry with negative amount."""
        from scripts.migrate_opening_balances import migrate_opening_balances

        # Arrange
        account = Account(
            id=2,
            name="Credit Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            balance=Decimal("-500.00"),  # Negative balance (owe money)
            normal_balance=NormalBalance.CREDIT
        )

        mock_dependencies['account_repo'].get_all.return_value = [account]
        mock_dependencies['journal_repo'].get_by_account.return_value = []

        mock_entry = JournalEntry(
            id=2,
            account_id=2,
            entry_date="2025-01-01",
            description="Opening balance for Credit Card",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("500.00"),  # Credit for liability
            balance_after=Decimal("-500.00"),
            entry_type=EntryType.OPENING_BALANCE
        )
        mock_dependencies['service'].create_simple_transaction.return_value = mock_entry

        # Act
        migrated, skipped = migrate_opening_balances(dry_run=False, opening_date="2025-01-01")

        # Assert
        assert migrated == 1
        assert skipped == 0

        # Verify negative amount passed to service (service handles debit/credit)
        call_args = mock_dependencies['service'].create_simple_transaction.call_args
        assert call_args[1]['amount'] == Decimal("-500.00")

    def test_migrate_account_with_zero_balance_skips(self, mock_dependencies):
        """Zero balance → skip, no entry created."""
        from scripts.migrate_opening_balances import migrate_opening_balances

        # Arrange
        account = Account(
            id=3,
            name="Empty Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            balance=Decimal("0.00"),  # Zero balance
            normal_balance=NormalBalance.DEBIT
        )

        mock_dependencies['account_repo'].get_all.return_value = [account]

        # Act
        migrated, skipped = migrate_opening_balances(dry_run=False, opening_date="2025-01-01")

        # Assert
        assert migrated == 0
        assert skipped == 1
        mock_dependencies['service'].create_simple_transaction.assert_not_called()

    def test_dry_run_does_not_modify_database(self, mock_dependencies):
        """Dry-run flag → no database writes."""
        from scripts.migrate_opening_balances import migrate_opening_balances

        # Arrange
        account = Account(
            id=4,
            name="Test Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("500.00"),
            normal_balance=NormalBalance.DEBIT
        )

        mock_dependencies['account_repo'].get_all.return_value = [account]
        mock_dependencies['journal_repo'].get_by_account.return_value = []

        # Act
        migrated, skipped = migrate_opening_balances(dry_run=True, opening_date="2025-01-01")

        # Assert
        assert migrated == 1  # Would have migrated
        assert skipped == 0
        # Verify NO database write calls made
        mock_dependencies['service'].create_simple_transaction.assert_not_called()

    def test_migration_idempotent_no_duplicates(self, mock_dependencies):
        """Running twice → no duplicate entries (idempotency)."""
        from scripts.migrate_opening_balances import migrate_opening_balances

        # Arrange
        account = Account(
            id=5,
            name="Already Migrated",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1500.00"),
            normal_balance=NormalBalance.DEBIT
        )

        # Mock existing OPENING entry
        existing_entry = JournalEntry(
            id=100,
            account_id=5,
            entry_date="2025-01-01",
            description="Opening balance",
            debit_amount=Decimal("1500.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1500.00"),
            entry_type=EntryType.OPENING_BALANCE  # Already has opening entry
        )

        mock_dependencies['account_repo'].get_all.return_value = [account]
        mock_dependencies['journal_repo'].get_by_account.return_value = [existing_entry]

        # Act
        migrated, skipped = migrate_opening_balances(dry_run=False, opening_date="2025-01-01")

        # Assert
        assert migrated == 0  # Should skip
        assert skipped == 1
        mock_dependencies['service'].create_simple_transaction.assert_not_called()

    def test_migrate_multiple_accounts(self, mock_dependencies):
        """Multiple accounts → all migrated correctly."""
        from scripts.migrate_opening_balances import migrate_opening_balances

        # Arrange
        accounts = [
            Account(
                id=1, name="Checking",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                balance=Decimal("1000.00"),
                normal_balance=NormalBalance.DEBIT
            ),
            Account(
                id=2, name="Savings",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.SAVINGS,
                balance=Decimal("5000.00"),
                normal_balance=NormalBalance.DEBIT
            ),
            Account(
                id=3, name="Zero Account",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CASH,
                balance=Decimal("0.00"),  # Should skip
                normal_balance=NormalBalance.DEBIT
            ),
        ]

        mock_dependencies['account_repo'].get_all.return_value = accounts
        mock_dependencies['journal_repo'].get_by_account.return_value = []

        mock_dependencies['service'].create_simple_transaction.side_effect = [
            JournalEntry(
                id=1, account_id=1, entry_date="2025-01-01",
                description="Opening", debit_amount=Decimal("1000"), credit_amount=Decimal("0"),
                balance_after=Decimal("1000"), entry_type=EntryType.OPENING_BALANCE
            ),
            JournalEntry(
                id=2, account_id=2, entry_date="2025-01-01",
                description="Opening", debit_amount=Decimal("5000"), credit_amount=Decimal("0"),
                balance_after=Decimal("5000"), entry_type=EntryType.OPENING_BALANCE
            ),
        ]

        # Act
        migrated, skipped = migrate_opening_balances(dry_run=False, opening_date="2025-01-01")

        # Assert
        assert migrated == 2  # Checking and Savings
        assert skipped == 1   # Zero account skipped
        assert mock_dependencies['service'].create_simple_transaction.call_count == 2

    def test_migrate_with_custom_date(self, mock_dependencies):
        """Custom date parameter → used in journal entries."""
        from scripts.migrate_opening_balances import migrate_opening_balances

        # Arrange
        account = Account(
            id=6,
            name="Test",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("100.00"),
            normal_balance=NormalBalance.DEBIT
        )

        mock_dependencies['account_repo'].get_all.return_value = [account]
        mock_dependencies['journal_repo'].get_by_account.return_value = []

        mock_entry = JournalEntry(
            id=6, account_id=6, entry_date="2024-06-15",
            description="Opening", debit_amount=Decimal("100"), credit_amount=Decimal("0"),
            balance_after=Decimal("100"), entry_type=EntryType.OPENING_BALANCE
        )
        mock_dependencies['service'].create_simple_transaction.return_value = mock_entry

        # Act
        migrated, skipped = migrate_opening_balances(dry_run=False, opening_date="2024-06-15")

        # Assert
        assert migrated == 1
        call_args = mock_dependencies['service'].create_simple_transaction.call_args
        assert call_args[1]['date'] == "2024-06-15"

    def test_migrate_error_handling_continues(self, mock_dependencies):
        """Error on one account → continues with others."""
        from scripts.migrate_opening_balances import migrate_opening_balances

        # Arrange
        accounts = [
            Account(
                id=1, name="Good Account",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                balance=Decimal("100.00"),
                normal_balance=NormalBalance.DEBIT
            ),
            Account(
                id=2, name="Bad Account",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.SAVINGS,
                balance=Decimal("200.00"),
                normal_balance=NormalBalance.DEBIT
            ),
        ]

        mock_dependencies['account_repo'].get_all.return_value = accounts
        mock_dependencies['journal_repo'].get_by_account.return_value = []

        # First call succeeds, second call fails
        mock_dependencies['service'].create_simple_transaction.side_effect = [
            JournalEntry(
                id=1, account_id=1, entry_date="2025-01-01",
                description="Opening", debit_amount=Decimal("100"), credit_amount=Decimal("0"),
                balance_after=Decimal("100"), entry_type=EntryType.OPENING_BALANCE
            ),
            Exception("Database error"),  # Simulate error
        ]

        # Act
        migrated, skipped = migrate_opening_balances(dry_run=False, opening_date="2025-01-01")

        # Assert
        assert migrated == 1  # First account migrated
        assert skipped == 1   # Second account skipped due to error
