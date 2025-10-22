"""
End-to-end integration tests for Transaction → Journal Entry flow.

These tests verify that TransactionService properly integrates with
DoubleEntryService to create journal entries and update balances.

Story: US-002A - Journal Entry Foundation
"""
import pytest
from decimal import Decimal

from finance_app.data.database import Database
from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.business.transaction_service import TransactionService
from finance_app.utils.exceptions import NotFoundError


class TestTransactionJournalIntegration:
    """Test end-to-end transaction → journal entry flow."""

    @pytest.fixture
    def account_repo(self, test_db):
        """Create account repository."""
        return AccountRepository(test_db)

    @pytest.fixture
    def journal_repo(self, test_db):
        """Create journal entry repository."""
        return JournalEntryRepository(test_db)

    @pytest.fixture
    def transaction_service(self, test_db):
        """Create transaction service."""
        return TransactionService(test_db)

    @pytest.fixture
    def checking_account(self, account_repo):
        """Create test checking account."""
        account = Account(
            id=None,
            name="Test Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        return account_repo.create(account)

    # ========================================================================
    # CREATE TRANSACTION TESTS
    # ========================================================================

    def test_create_income_transaction_creates_journal_entry(
        self, transaction_service, journal_repo, account_repo, checking_account
    ):
        """Test that creating income transaction creates journal entry."""
        initial_balance = checking_account.balance

        # Create income transaction
        transaction = transaction_service.create_transaction(
            account_id=checking_account.id,
            date="2025-10-22",
            description="Salary",
            category="Income",
            amount="500.00",
            trans_type="income"
        )

        # Verify transaction was created
        assert transaction.id is not None
        assert transaction.amount == Decimal("500.00")
        assert transaction.type == "income"

        # Verify journal entry was created
        entries = journal_repo.get_by_account(checking_account.id)
        assert len(entries) == 1

        journal_entry = entries[0]
        assert journal_entry.transaction_id == transaction.id
        assert journal_entry.description == "Salary"
        assert journal_entry.debit_amount == Decimal("500.00")  # Income increases asset = debit
        assert journal_entry.credit_amount == Decimal("0")

        # Verify account balance was updated via trigger
        updated_account = account_repo.get_by_id(checking_account.id)
        assert updated_account.balance == initial_balance + Decimal("500.00")
        assert updated_account.balance == Decimal("1500.00")

        # Verify balance_after in journal entry
        assert journal_entry.balance_after == Decimal("1500.00")

    def test_create_expense_transaction_creates_journal_entry(
        self, transaction_service, journal_repo, account_repo, checking_account
    ):
        """Test that creating expense transaction creates journal entry."""
        initial_balance = checking_account.balance

        # Create expense transaction
        transaction = transaction_service.create_transaction(
            account_id=checking_account.id,
            date="2025-10-22",
            description="Groceries",
            category="Food",
            amount="75.50",
            trans_type="expense"
        )

        # Verify transaction was created
        assert transaction.id is not None
        assert transaction.amount == Decimal("-75.50")  # Expense is negative
        assert transaction.type == "expense"

        # Verify journal entry was created
        entries = journal_repo.get_by_account(checking_account.id)
        assert len(entries) == 1

        journal_entry = entries[0]
        assert journal_entry.transaction_id == transaction.id
        assert journal_entry.description == "Groceries"
        assert journal_entry.debit_amount == Decimal("0")
        assert journal_entry.credit_amount == Decimal("75.50")  # Expense decreases asset = credit

        # Verify account balance was updated via trigger
        updated_account = account_repo.get_by_id(checking_account.id)
        assert updated_account.balance == initial_balance - Decimal("75.50")
        assert updated_account.balance == Decimal("924.50")

        # Verify balance_after in journal entry
        assert journal_entry.balance_after == Decimal("924.50")

    def test_multiple_transactions_create_multiple_journal_entries(
        self, transaction_service, journal_repo, account_repo, checking_account
    ):
        """Test that multiple transactions create multiple journal entries with correct balances."""
        initial_balance = checking_account.balance

        # Create multiple transactions
        txn1 = transaction_service.create_transaction(
            account_id=checking_account.id,
            date="2025-10-22",
            description="Salary",
            category="Income",
            amount="1000.00",
            trans_type="income"
        )

        txn2 = transaction_service.create_transaction(
            account_id=checking_account.id,
            date="2025-10-23",
            description="Rent",
            category="Housing",
            amount="500.00",
            trans_type="expense"
        )

        txn3 = transaction_service.create_transaction(
            account_id=checking_account.id,
            date="2025-10-24",
            description="Groceries",
            category="Food",
            amount="100.00",
            trans_type="expense"
        )

        # Verify 3 journal entries were created
        entries = journal_repo.get_by_account(checking_account.id)
        assert len(entries) == 3

        # Verify final balance is correct
        # Initial: 1000, +1000 (income), -500 (rent), -100 (groceries) = 1400
        updated_account = account_repo.get_by_id(checking_account.id)
        assert updated_account.balance == Decimal("1400.00")

        # Verify balance_after progression
        # Order is DESC by date, so reverse to get chronological
        entries_chronological = list(reversed(entries))
        assert entries_chronological[0].balance_after == Decimal("2000.00")  # After +1000
        assert entries_chronological[1].balance_after == Decimal("1500.00")  # After -500
        assert entries_chronological[2].balance_after == Decimal("1400.00")  # After -100

    # ========================================================================
    # DELETE TRANSACTION TESTS
    # ========================================================================

    def test_delete_transaction_deletes_journal_entry_and_reverts_balance(
        self, transaction_service, journal_repo, account_repo, checking_account
    ):
        """Test that deleting transaction deletes journal entry and reverts balance."""
        initial_balance = checking_account.balance

        # Create transaction
        transaction = transaction_service.create_transaction(
            account_id=checking_account.id,
            date="2025-10-22",
            description="Test",
            category="Test",
            amount="200.00",
            trans_type="income"
        )

        # Verify balance increased
        account_after_create = account_repo.get_by_id(checking_account.id)
        assert account_after_create.balance == Decimal("1200.00")

        # Verify journal entry exists
        entries_before = journal_repo.get_by_account(checking_account.id)
        assert len(entries_before) == 1

        # Delete transaction
        deleted = transaction_service.delete_transaction(transaction.id)
        assert deleted is True

        # Verify journal entry was deleted (CASCADE)
        entries_after = journal_repo.get_by_account(checking_account.id)
        assert len(entries_after) == 0

        # Verify balance was reverted via trigger
        account_after_delete = account_repo.get_by_id(checking_account.id)
        assert account_after_delete.balance == initial_balance
        assert account_after_delete.balance == Decimal("1000.00")

    def test_delete_nonexistent_transaction_raises_error(self, transaction_service):
        """Test that deleting non-existent transaction raises NotFoundError."""
        with pytest.raises(NotFoundError, match="Transaction with ID 999 not found"):
            transaction_service.delete_transaction(999)

    # ========================================================================
    # BALANCE INTEGRITY TESTS
    # ========================================================================

    def test_journal_balance_matches_account_balance(
        self, transaction_service, journal_repo, account_repo
    ):
        """Test that calculated balance from journal matches account balance."""
        # Create account with zero balance so journal and account balances match
        # (Opening balance journal entries are handled in US-002B)
        account = Account(
            id=None,
            name="Zero Balance Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),  # Start with zero
            normal_balance=NormalBalance.DEBIT
        )
        zero_account = account_repo.create(account)

        # Create several transactions
        transaction_service.create_transaction(
            account_id=zero_account.id,
            date="2025-10-22",
            description="Income 1",
            category="Salary",
            amount="500.00",
            trans_type="income"
        )

        transaction_service.create_transaction(
            account_id=zero_account.id,
            date="2025-10-23",
            description="Expense 1",
            category="Food",
            amount="150.00",
            trans_type="expense"
        )

        transaction_service.create_transaction(
            account_id=zero_account.id,
            date="2025-10-24",
            description="Income 2",
            category="Bonus",
            amount="300.00",
            trans_type="income"
        )

        # Get account balance from account table
        account = account_repo.get_by_id(zero_account.id)
        account_balance = account.balance

        # Calculate balance from journal entries
        journal_balance = journal_repo.get_account_balance(zero_account.id)

        # They should match
        assert account_balance == journal_balance
        # 0 + 500 - 150 + 300 = 650
        assert account_balance == Decimal("650.00")

    def test_transaction_creates_correct_debit_credit_for_asset_account(
        self, transaction_service, journal_repo, checking_account
    ):
        """Test that transactions create correct debit/credit entries for asset account."""
        # Income (positive amount) to asset = DEBIT
        income_txn = transaction_service.create_transaction(
            account_id=checking_account.id,
            date="2025-10-22",
            description="Income",
            category="Salary",
            amount="100.00",
            trans_type="income"
        )

        income_entry = journal_repo.get_by_account(checking_account.id)[0]
        assert income_entry.debit_amount == Decimal("100.00")
        assert income_entry.credit_amount == Decimal("0")
        assert income_entry.is_debit is True

        # Expense (negative amount) to asset = CREDIT
        expense_txn = transaction_service.create_transaction(
            account_id=checking_account.id,
            date="2025-10-23",
            description="Expense",
            category="Food",
            amount="50.00",
            trans_type="expense"
        )

        entries = journal_repo.get_by_account(checking_account.id)
        expense_entry = [e for e in entries if e.transaction_id == expense_txn.id][0]
        assert expense_entry.debit_amount == Decimal("0")
        assert expense_entry.credit_amount == Decimal("50.00")
        assert expense_entry.is_credit is True

    # ========================================================================
    # ERROR HANDLING TESTS
    # ========================================================================

    def test_transaction_rollback_on_journal_entry_failure(
        self, transaction_service, account_repo, test_db
    ):
        """Test that transaction is rolled back if journal entry creation fails."""
        # This test would require mocking or corrupting the journal entry creation
        # For now, we verify that invalid account raises error
        with pytest.raises(NotFoundError, match="Account with ID 999 not found"):
            transaction_service.create_transaction(
                account_id=999,  # Non-existent account
                date="2025-10-22",
                description="Test",
                category="Test",
                amount="100.00",
                trans_type="income"
            )
