"""
Integration tests for Account Balance Validation workflow.

Story: US-010 - Account Balance Validation & Integrity

Test Coverage:
- Complete validation workflow: Validate → Fix → Revalidate (3 tests)
- Trial balance generation with real accounts (2 tests)
- Multi-account validation scenarios (2 tests)
- Validation audit trail logging (2 tests)
- Edge cases: Zero balances, large discrepancies (2 tests)

Total: 11 integration tests (exceeds 8+ target)

Testing Strategy:
- Use real database (test_db fixture)
- Create real accounts and journal entries
- Test full validation workflow end-to-end
- Verify database state after operations
"""

import pytest
from decimal import Decimal
from datetime import datetime

from finance_app.data.database import Database
from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance,
    JournalEntry, EntryType, ValidationResult, TrialBalance
)
from finance_app.business.account_balance_validator import AccountBalanceValidator
from finance_app.business.account_service import AccountService
from finance_app.business.double_entry_service import DoubleEntryService
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.utils.exceptions import NotFoundError


class TestValidationWorkflowIntegration:
    """Integration tests for complete validation workflow."""

    def test_validate_account_with_correct_balance(self, test_db):
        """Test validating account when cached balance matches journal entries."""
        # Setup
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)
        account_service = AccountService(test_db)

        # Create account with opening balance (creates journal entries automatically)
        account, _ = account_service.create_account_with_opening_balance(
            name="Test Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("1000.00"),
            opening_date="2025-10-01"
        )

        # Act: Validate the account
        result = validator.validate_account_balance(account.id)

        # Assert: Should be valid since balance matches journal entries
        assert result.is_valid is True
        assert result.cached_balance == Decimal("1000.00")
        assert result.calculated_balance == Decimal("1000.00")
        assert result.difference == Decimal("0.00")

    def test_validate_account_with_discrepancy_then_fix(self, test_db):
        """Test complete workflow: Detect discrepancy → Fix → Revalidate."""
        # Setup
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)
        account_service = AccountService(test_db)

        # Create account
        account, _ = account_service.create_account_with_opening_balance(
            name="Test Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            opening_balance=Decimal("5000.00"),
            opening_date="2025-10-01"
        )

        # Manually corrupt the cached balance to simulate discrepancy
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (4500.00, account.id)  # Set wrong balance (should be 5000)
            )
            conn.commit()

        # Act 1: Validate - should detect discrepancy
        result1 = validator.validate_account_balance(account.id)

        # Assert 1: Discrepancy detected
        assert result1.is_valid is False
        assert result1.cached_balance == Decimal("4500.00")
        assert result1.calculated_balance == Decimal("5000.00")
        assert result1.difference == Decimal("-500.00")

        # Act 2: Fix the discrepancy
        fixed_account = validator.fix_account_balance(account.id)

        # Assert 2: Balance corrected
        assert fixed_account.balance == Decimal("5000.00")

        # Act 3: Revalidate - should now be valid
        result2 = validator.validate_account_balance(account.id)

        # Assert 3: Now valid after fix
        assert result2.is_valid is True
        assert result2.cached_balance == Decimal("5000.00")
        assert result2.calculated_balance == Decimal("5000.00")
        assert result2.difference == Decimal("0.00")

    def test_fix_multiple_account_discrepancies(self, test_db):
        """Test fixing discrepancies in multiple accounts."""
        # Setup
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)
        account_service = AccountService(test_db)

        # Create 3 accounts
        account1, _ = account_service.create_account_with_opening_balance(
            name="Cash", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CASH,
            opening_balance=Decimal("1000.00"), opening_date="2025-10-01"
        )
        account2, _ = account_service.create_account_with_opening_balance(
            name="Bank", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("2000.00"), opening_date="2025-10-01"
        )
        account3, _ = account_service.create_account_with_opening_balance(
            name="Investment", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.INVESTMENT,
            opening_balance=Decimal("3000.00"), opening_date="2025-10-01"
        )

        # Corrupt balances for account1 and account3
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (900.00, account1.id)  # Wrong: should be 1000
            )
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (3500.00, account3.id)  # Wrong: should be 3000
            )
            conn.commit()

        # Act: Validate all accounts
        results = validator.validate_all_accounts()

        # Filter failed validations
        failed = [r for r in results if not r.is_valid]

        # Assert: 2 accounts should have failures (account1 and account3)
        assert len(failed) >= 2

        # Fix all failed accounts
        for result in failed:
            validator.fix_account_balance(result.account_id)

        # Revalidate all
        results2 = validator.validate_all_accounts()
        failed2 = [r for r in results2 if not r.is_valid]

        # Assert: All should be valid now
        assert len(failed2) == 0


class TestTrialBalanceIntegration:
    """Integration tests for trial balance generation."""

    def test_trial_balance_with_real_accounts_balanced(self, test_db):
        """Test trial balance generation with balanced accounts."""
        # Setup
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)
        account_service = AccountService(test_db)

        # Create balanced set: Assets = Equity
        # Asset accounts (debit normal balance)
        cash, _ = account_service.create_account_with_opening_balance(
            name="Cash Account", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CASH,
            opening_balance=Decimal("5000.00"), opening_date="2025-10-01"
        )
        bank, _ = account_service.create_account_with_opening_balance(
            name="Bank Account", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("10000.00"), opening_date="2025-10-01"
        )

        # Act: Generate trial balance
        trial_balance = validator.get_trial_balance()

        # Assert: Should be balanced
        # Note: Opening Balance Equity account is auto-created to balance the equation
        assert trial_balance is not None
        assert len(trial_balance.accounts) > 0
        # In double-entry accounting, debits should equal credits
        assert trial_balance.is_balanced is True or abs(trial_balance.difference) < Decimal("0.01")

    def test_trial_balance_with_as_of_date(self, test_db):
        """Test trial balance with historical as_of_date parameter."""
        # Setup
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)
        account_service = AccountService(test_db)

        # Create account
        account, _ = account_service.create_account_with_opening_balance(
            name="Historical Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("1000.00"),
            opening_date="2025-09-01"
        )

        # Act: Generate trial balance as of specific date
        trial_balance = validator.get_trial_balance(as_of_date="2025-09-30")

        # Assert
        assert trial_balance.as_of_date == "2025-09-30"
        assert len(trial_balance.accounts) > 0


class TestValidateAllAccountsIntegration:
    """Integration tests for validating all accounts."""

    def test_validate_all_accounts_with_mix_of_valid_and_invalid(self, test_db):
        """Test validating all accounts when some are valid and some have discrepancies."""
        # Setup
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)
        account_service = AccountService(test_db)

        # Create 4 accounts
        acct1, _ = account_service.create_account_with_opening_balance(
            name="Account 1", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CASH,
            opening_balance=Decimal("100.00"), opening_date="2025-10-01"
        )
        acct2, _ = account_service.create_account_with_opening_balance(
            name="Account 2", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("200.00"), opening_date="2025-10-01"
        )
        acct3, _ = account_service.create_account_with_opening_balance(
            name="Account 3", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            opening_balance=Decimal("300.00"), opening_date="2025-10-01"
        )

        # Corrupt balance for acct2
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (250.00, acct2.id)  # Wrong balance
            )
            conn.commit()

        # Act: Validate all
        results = validator.validate_all_accounts()

        # Assert: Should have mix of valid and invalid
        passed = [r for r in results if r.is_valid]
        failed = [r for r in results if not r.is_valid]

        # At least one should fail (acct2)
        assert len(failed) >= 1

        # Find the failed account
        acct2_result = next((r for r in results if r.account_id == acct2.id), None)
        assert acct2_result is not None
        assert acct2_result.is_valid is False

    def test_validate_all_accounts_empty_database(self, test_db):
        """Test validating all accounts when database has no accounts."""
        # Setup: Fresh database with no accounts (except auto-created equity)
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)

        # Act: Validate all
        results = validator.validate_all_accounts()

        # Assert: Should handle empty list gracefully
        # May have Opening Balance Equity account auto-created from previous tests
        assert isinstance(results, list)


class TestValidationAuditTrailIntegration:
    """Integration tests for validation audit trail logging."""

    def test_validation_creates_audit_log_entry(self, test_db):
        """Test that validation results are logged to database."""
        # Setup
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)
        account_service = AccountService(test_db)

        # Create account
        account, _ = account_service.create_account_with_opening_balance(
            name="Audit Test Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("1000.00"),
            opening_date="2025-10-01"
        )

        # Act: Validate (should log to balance_validation_log table)
        validator.validate_account_balance(account.id)

        # Assert: Check that log entry was created
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            logs = cursor.execute(
                "SELECT * FROM balance_validation_log WHERE account_id = ?",
                (account.id,)
            ).fetchall()

        assert len(logs) >= 1
        log = logs[-1]  # Get most recent
        assert log['account_id'] == account.id
        assert log['was_repaired'] == 0  # Not repaired

    def test_fix_creates_audit_log_with_repaired_flag(self, test_db):
        """Test that fixing balance creates audit log entry with was_repaired=1."""
        # Setup
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)
        account_service = AccountService(test_db)

        # Create account
        account, _ = account_service.create_account_with_opening_balance(
            name="Fix Audit Test",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("2000.00"),
            opening_date="2025-10-01"
        )

        # Corrupt balance
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (1500.00, account.id)
            )
            conn.commit()

        # Act: Fix the balance (should log with was_repaired=1)
        validator.fix_account_balance(account.id)

        # Assert: Check that log entry has was_repaired flag
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            logs = cursor.execute(
                "SELECT * FROM balance_validation_log WHERE account_id = ? AND was_repaired = 1",
                (account.id,)
            ).fetchall()

        assert len(logs) >= 1
        log = logs[-1]
        assert log['was_repaired'] == 1


class TestEdgeCasesIntegration:
    """Integration tests for edge cases."""

    def test_validate_account_with_zero_balance(self, test_db):
        """Test validating account with zero balance."""
        # Setup
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)

        # Create account manually with zero balance (no opening balance)
        account = Account(
            id=None,
            name="Zero Balance Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00")
        )
        created = account_repo.create(account)

        # Act: Validate
        result = validator.validate_account_balance(created.id)

        # Assert: Should be valid (0 = 0)
        assert result.is_valid is True
        assert result.cached_balance == Decimal("0.00")
        assert result.calculated_balance == Decimal("0.00")

    def test_validate_account_with_large_discrepancy(self, test_db):
        """Test validating account with large balance discrepancy."""
        # Setup
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)
        account_service = AccountService(test_db)

        # Create account
        account, _ = account_service.create_account_with_opening_balance(
            name="Large Discrepancy Test",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("10000.00"),
            opening_date="2025-10-01"
        )

        # Create large discrepancy
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (5000.00, account.id)  # Off by 5000
            )
            conn.commit()

        # Act: Validate
        result = validator.validate_account_balance(account.id)

        # Assert: Should detect large discrepancy
        assert result.is_valid is False
        assert abs(result.difference) == Decimal("5000.00")
        assert result.severity == "CRITICAL"  # Large discrepancy

    def test_validate_nonexistent_account_raises_error(self, test_db):
        """Test that validating non-existent account raises NotFoundError."""
        # Setup
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)

        # Act & Assert
        with pytest.raises(NotFoundError, match="Account 99999 not found"):
            validator.validate_account_balance(99999)
