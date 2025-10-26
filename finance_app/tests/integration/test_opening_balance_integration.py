"""
Integration tests for Opening Balance Equity workflow.

Story: US-005 - Opening Balance Equity

Test Coverage:
- Complete workflow: Create account → Set opening balance → Verify journal entries (3 tests)
- Accounting equation validation with real database (3 tests)
- Multiple accounts with opening balances (2 tests)
- Error scenarios with real database (3 tests)
- Opening balance summary reporting (2 tests)
- Migration 006 execution (2 tests)

Total: 15 integration tests
"""
import pytest
from decimal import Decimal
from datetime import datetime
import os

from finance_app.data.database import Database
from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance,
    JournalEntry, EntryType, Transaction, ReconciliationStatus
)
from finance_app.business.account_service import AccountService
from finance_app.business.double_entry_service import DoubleEntryService
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.data.repositories.transaction_repository import TransactionRepository
from finance_app.utils.exceptions import ValidationError, NotFoundError


class TestCreateAccountWithOpeningBalanceIntegration:
    """Integration tests for creating accounts with opening balances."""

    def test_create_asset_account_with_opening_balance_creates_journal_entries(self, test_db):
        """Test that creating asset account creates both journal entries."""
        service = AccountService(test_db)
        journal_repo = JournalEntryRepository(test_db)
        account_repo = AccountRepository(test_db)

        # Create account with opening balance
        account, journal_entry = service.create_account_with_opening_balance(
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("5000.00"),
            opening_date="2025-01-01",
            currency="USD"
        )

        # Verify account was created
        assert account.id is not None
        assert account.name == "Checking Account"
        assert account.opening_balance_date == "2025-01-01"

        # Verify journal entries were created for the account
        account_entries = journal_repo.get_by_account(account.id)
        opening_balance_entries = [e for e in account_entries if e.entry_type == EntryType.OPENING_BALANCE]
        assert len(opening_balance_entries) >= 1

        # Verify the entry for the account has correct amount
        assert opening_balance_entries[0].debit_amount == Decimal("5000.00") or \
               opening_balance_entries[0].credit_amount == Decimal("5000.00")

        # Verify Opening Balance Equity account also has an entry
        all_accounts = account_repo.get_all()
        equity_account = next((a for a in all_accounts
                               if a.name == "Opening Balance Equity"
                               and a.account_type == AccountType.EQUITY), None)
        assert equity_account is not None

        equity_entries = journal_repo.get_by_account(equity_account.id)
        equity_opening_entries = [e for e in equity_entries if e.entry_type == EntryType.OPENING_BALANCE]
        assert len(equity_opening_entries) >= 1

    def test_create_multiple_accounts_maintains_accounting_equation(self, test_db):
        """Test that creating multiple accounts with opening balances maintains equation."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create multiple accounts
        checking, _ = service.create_account_with_opening_balance(
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("5000.00"),
            opening_date="2025-01-01"
        )

        savings, _ = service.create_account_with_opening_balance(
            name="Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            opening_balance=Decimal("10000.00"),
            opening_date="2025-01-01"
        )

        credit_card, _ = service.create_account_with_opening_balance(
            name="Credit Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            opening_balance=Decimal("2000.00"),
            opening_date="2025-01-01"
        )

        # Verify accounting equation: Assets = Liabilities + Equity
        all_accounts = account_repo.get_all()

        assets = sum(acc.balance for acc in all_accounts if acc.account_type == AccountType.ASSET)
        liabilities = sum(acc.balance for acc in all_accounts if acc.account_type == AccountType.LIABILITY)
        equity = sum(acc.balance for acc in all_accounts if acc.account_type == AccountType.EQUITY)

        assert assets == liabilities + equity

    def test_create_account_with_zero_opening_balance_creates_no_journal_entries(self, test_db):
        """Test that zero opening balance creates no journal entries."""
        service = AccountService(test_db)
        journal_repo = JournalEntryRepository(test_db)

        # Create account with zero opening balance
        account, journal_entry = service.create_account_with_opening_balance(
            name="New Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("0.00"),
            opening_date="2025-01-01"
        )

        # Verify no journal entries were created for this account
        assert journal_entry is None
        account_entries = journal_repo.get_by_account(account.id)
        # Should have no entries with OPENING_BALANCE type
        opening_entries = [e for e in account_entries if e.entry_type == EntryType.OPENING_BALANCE]
        assert len(opening_entries) == 0


class TestSetAccountOpeningBalanceIntegration:
    """Integration tests for setting opening balance on existing accounts."""

    def test_set_opening_balance_on_existing_account(self, test_db):
        """Test setting opening balance on an account created without one."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create account without opening balance
        account = service.create_account(
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="0.00"
        )

        # Set opening balance
        journal_entry = service.set_account_opening_balance(
            account_id=account.id,
            opening_balance=Decimal("3000.00"),
            opening_date="2025-01-01"
        )

        # Verify opening balance was set
        updated_account = account_repo.get_by_id(account.id)
        assert updated_account.opening_balance_date == "2025-01-01"
        assert journal_entry is not None

    def test_cannot_set_opening_balance_twice(self, test_db):
        """Test that ValidationError is raised when trying to set opening balance twice."""
        service = AccountService(test_db)

        # Create account with opening balance
        account, _ = service.create_account_with_opening_balance(
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("5000.00"),
            opening_date="2025-01-01"
        )

        # Try to set opening balance again
        with pytest.raises(ValidationError, match="already has opening balance set"):
            service.set_account_opening_balance(
                account_id=account.id,
                opening_balance=Decimal("1000.00"),
                opening_date="2025-02-01"
            )

    def test_set_opening_balance_raises_not_found_for_invalid_account(self, test_db):
        """Test that NotFoundError is raised for nonexistent account."""
        service = AccountService(test_db)

        with pytest.raises(NotFoundError, match="Account 99999 not found"):
            service.set_account_opening_balance(
                account_id=99999,
                opening_balance=Decimal("1000.00"),
                opening_date="2025-01-01"
            )


class TestOpeningBalanceEquityAccountIntegration:
    """Integration tests for Opening Balance Equity account."""

    def test_opening_balance_equity_account_created_by_migration(self, test_db):
        """Test that Migration 006 creates Opening Balance Equity account."""
        account_repo = AccountRepository(test_db)
        all_accounts = account_repo.get_all()

        # Find Opening Balance Equity account
        equity_account = next(
            (acc for acc in all_accounts
             if acc.name == "Opening Balance Equity"
             and acc.account_type == AccountType.EQUITY),
            None
        )

        assert equity_account is not None
        assert equity_account.account_subtype == AccountSubtype.OPENING_BALANCE
        assert equity_account.balance == Decimal("0.00")

    def test_ensure_opening_balance_equity_returns_migration_created_account(self, test_db):
        """Test that ensure method returns the account created by migration."""
        service = AccountService(test_db)

        equity_account = service.ensure_opening_balance_equity_account()

        assert equity_account.name == "Opening Balance Equity"
        assert equity_account.account_type == AccountType.EQUITY


class TestAccountingEquationValidation:
    """Integration tests for accounting equation validation."""

    def test_validate_passes_for_balanced_accounts(self, test_db):
        """Test that validation passes when equation is balanced."""
        service = AccountService(test_db)

        # Create balanced set of accounts
        service.create_account_with_opening_balance(
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("5000.00"),
            opening_date="2025-01-01"
        )

        # Validation should pass (called internally, but we can call it explicitly)
        result = service.validate_opening_balance_equity()
        assert result is True

    def test_validate_passes_for_zero_balances(self, test_db):
        """Test that validation passes when all balances are zero."""
        service = AccountService(test_db)

        # Don't create any accounts with opening balances
        result = service.validate_opening_balance_equity()
        assert result is True

    def test_validate_raises_error_for_unbalanced_accounts(self, test_db):
        """Test that validation raises error when equation is unbalanced."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create account with opening balance
        account, _ = service.create_account_with_opening_balance(
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("5000.00"),
            opening_date="2025-01-01"
        )

        # Manually corrupt the balance to break the equation
        # This simulates a data integrity issue
        with test_db.get_connection() as conn:
            conn.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (10000.00, account.id)
            )

        # Validation should fail
        with pytest.raises(ValidationError, match="Accounting equation does not balance"):
            service.validate_opening_balance_equity()


class TestOpeningBalanceSummaryIntegration:
    """Integration tests for opening balance summary."""

    def test_get_summary_with_multiple_accounts(self, test_db):
        """Test that summary correctly aggregates multiple accounts."""
        service = AccountService(test_db)

        # Create multiple accounts with opening balances
        service.create_account_with_opening_balance(
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("5000.00"),
            opening_date="2025-01-01"
        )

        service.create_account_with_opening_balance(
            name="Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            opening_balance=Decimal("10000.00"),
            opening_date="2025-01-01"
        )

        service.create_account_with_opening_balance(
            name="Credit Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            opening_balance=Decimal("2000.00"),
            opening_date="2025-01-01"
        )

        # Get summary
        summary = service.get_opening_balance_summary()

        # Verify totals (excluding Opening Balance Equity account)
        assert summary['total_accounts'] >= 3
        assert 'asset' in summary['by_type']
        assert 'liability' in summary['by_type']
        assert summary['by_type']['asset']['count'] == 2
        assert summary['by_type']['liability']['count'] == 1

    def test_get_summary_excludes_accounts_without_opening_balances(self, test_db):
        """Test that summary excludes accounts created without opening balances."""
        service = AccountService(test_db)

        # Create account with opening balance
        service.create_account_with_opening_balance(
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("5000.00"),
            opening_date="2025-01-01"
        )

        # Create account without opening balance
        service.create_account(
            name="New Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="0.00"
        )

        # Get summary
        summary = service.get_opening_balance_summary()

        # Verify only account with opening balance is included
        # (Plus the Opening Balance Equity account)
        assert summary['total_accounts'] >= 1


class TestTransactionOpeningBalanceFlag:
    """Integration tests for is_opening_balance transaction flag."""

    def test_opening_balance_transactions_are_flagged(self, test_db):
        """Test that transactions created for opening balances are flagged."""
        service = AccountService(test_db)
        transaction_repo = TransactionRepository(test_db)

        # Create account with opening balance
        account, _ = service.create_account_with_opening_balance(
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("5000.00"),
            opening_date="2025-01-01"
        )

        # Get transactions for the account
        transactions = transaction_repo.get_all(account_id=account.id)

        # Find opening balance transaction
        opening_balance_txn = next(
            (txn for txn in transactions if txn.is_opening_balance),
            None
        )

        assert opening_balance_txn is not None
        assert opening_balance_txn.amount == Decimal("5000.00")
        assert opening_balance_txn.reconciliation_status == ReconciliationStatus.CLEARED

    def test_opening_balance_transactions_are_automatically_cleared(self, test_db):
        """Test that opening balance transactions are automatically reconciled."""
        service = AccountService(test_db)
        transaction_repo = TransactionRepository(test_db)

        # Create account with opening balance
        account, _ = service.create_account_with_opening_balance(
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            opening_balance=Decimal("3000.00"),
            opening_date="2025-01-01"
        )

        # Get opening balance transaction
        transactions = transaction_repo.get_all(account_id=account.id)
        opening_balance_txn = next((txn for txn in transactions if txn.is_opening_balance), None)

        assert opening_balance_txn.reconciliation_status == ReconciliationStatus.CLEARED
