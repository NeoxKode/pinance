"""
Integration tests for account reconciliation workflow.

Story: US-004 - Account Reconciliation (Day 3)

These tests verify end-to-end reconciliation workflows including:
- Balanced reconciliation (discrepancy = $0)
- Reconciliation with discrepancy
- Mark/unmark transaction workflows
- Concurrent reconciliation prevention
- Reconciliation history tracking
- Account last_reconciled_date updates
- Edge cases (empty accounts, all cleared, etc.)
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from finance_app.data.database import Database
from finance_app.data.models import (
    Account, Transaction, ReconciliationStatus, AccountType, AccountSubtype, NormalBalance
)
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.transaction_repository import TransactionRepository
from finance_app.data.repositories.reconciliation_repository import ReconciliationRepository
from finance_app.business.reconciliation_service import ReconciliationService
from finance_app.utils.exceptions import NotFoundError, ValidationError, BusinessRuleError


@pytest.fixture
def account_repo(test_db):
    """Create AccountRepository with test database."""
    return AccountRepository(test_db)


@pytest.fixture
def transaction_repo(test_db):
    """Create TransactionRepository with test database."""
    return TransactionRepository(test_db)


@pytest.fixture
def reconciliation_repo(test_db):
    """Create ReconciliationRepository with test database."""
    return ReconciliationRepository(test_db)


@pytest.fixture
def service(test_db):
    """Create ReconciliationService with test database."""
    return ReconciliationService(test_db)


@pytest.fixture
def test_account(account_repo):
    """Create a test checking account."""
    account = Account(
        id=None,
        name="Test Checking",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        normal_balance=NormalBalance.DEBIT,
        balance=Decimal("0.00"),
        last_reconciled_date=None
    )
    return account_repo.create(account)


@pytest.fixture
def test_transactions(test_account, transaction_repo):
    """Create test transactions for reconciliation."""
    transactions = []

    # Transaction 1: Paycheck (3 days ago)
    txn1 = Transaction(
        id=None,
        account_id=test_account.id,
        date=(datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
        description="Paycheck",
        amount=Decimal("2000.00"),
        category="Income",
        type="expense",
        reconciliation_status=ReconciliationStatus.UNRECONCILED
    )
    transactions.append(transaction_repo.create(txn1))

    # Transaction 2: Rent payment (2 days ago)
    txn2 = Transaction(
        id=None,
        account_id=test_account.id,
        date=(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
        description="Rent Payment",
        amount=Decimal("-1200.00"),
        category="Housing",
        type="expense",
        reconciliation_status=ReconciliationStatus.UNRECONCILED
    )
    transactions.append(transaction_repo.create(txn2))

    # Transaction 3: Grocery store (1 day ago)
    txn3 = Transaction(
        id=None,
        account_id=test_account.id,
        date=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
        description="Grocery Store",
        amount=Decimal("-125.50"),
        category="Food",
        type="expense",
        reconciliation_status=ReconciliationStatus.UNRECONCILED
    )
    transactions.append(transaction_repo.create(txn3))

    # Transaction 4: Gas station (today)
    txn4 = Transaction(
        id=None,
        account_id=test_account.id,
        date=datetime.now().strftime('%Y-%m-%d'),
        description="Gas Station",
        amount=Decimal("-45.00"),
        category="Transportation",
        type="expense",
        reconciliation_status=ReconciliationStatus.UNRECONCILED
    )
    transactions.append(transaction_repo.create(txn4))

    return transactions


class TestBalancedReconciliation:
    """Test reconciliation that balances perfectly (discrepancy = $0)."""

    def test_complete_balanced_reconciliation_workflow(
        self, service, test_account, test_transactions, transaction_repo, account_repo
    ):
        """
        Test complete workflow: start → mark all → calculate → complete.

        Verifies:
        - Start reconciliation returns correct info
        - All transactions can be marked as cleared
        - Cleared balance calculation is correct
        - Discrepancy is $0.00
        - Reconciliation record is saved
        - Account last_reconciled_date is updated
        """
        statement_date = datetime.now().strftime('%Y-%m-%d')
        expected_balance = sum(txn.amount for txn in test_transactions)  # $629.50

        # Step 1: Start reconciliation
        session = service.start_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date,
            statement_balance=expected_balance
        )

        assert session['account_id'] == test_account.id
        assert session['account_name'] == "Test Checking"
        assert session['statement_date'] == statement_date
        assert session['statement_balance'] == expected_balance
        assert session['opening_balance'] == Decimal('0.00')  # First reconciliation
        assert session['unreconciled_count'] == 4
        assert session['last_reconciliation_date'] is None

        # Step 2: Mark all transactions as cleared
        for txn in test_transactions:
            updated_txn = service.mark_transaction_cleared(
                transaction_id=txn.id,
                statement_date=statement_date
            )
            assert updated_txn.reconciliation_status == ReconciliationStatus.CLEARED
            assert updated_txn.reconciled_date is not None
            assert updated_txn.statement_date == statement_date

        # Step 3: Calculate cleared balance
        cleared_balance = service.calculate_cleared_balance(test_account.id)
        assert cleared_balance == expected_balance

        # Step 4: Calculate discrepancy
        discrepancy = service.calculate_discrepancy(test_account.id, expected_balance)
        assert discrepancy == Decimal('0.00')  # Perfect balance!

        # Step 5: Complete reconciliation
        reconciliation = service.complete_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date,
            statement_balance=expected_balance,
            notes=None
        )

        assert reconciliation.id is not None
        assert reconciliation.account_id == test_account.id
        assert reconciliation.statement_date == statement_date
        assert reconciliation.statement_balance == expected_balance
        assert reconciliation.cleared_balance == expected_balance
        assert reconciliation.discrepancy == Decimal('0.00')
        assert reconciliation.transaction_count == 4
        assert reconciliation.notes is None
        assert reconciliation.is_balanced() is True

        # Step 6: Verify account last_reconciled_date updated
        updated_account = account_repo.get_by_id(test_account.id)
        assert updated_account.last_reconciled_date is not None
        assert updated_account.last_reconciled_date == reconciliation.reconciliation_date


class TestReconciliationWithDiscrepancy:
    """Test reconciliation with discrepancy (cleared balance ≠ statement balance)."""

    def test_reconciliation_with_positive_discrepancy(
        self, service, test_account, test_transactions
    ):
        """
        Test reconciliation where statement balance > cleared balance.

        This happens when bank shows transactions that user hasn't recorded yet.
        """
        statement_date = datetime.now().strftime('%Y-%m-%d')

        # Mark only 2 transactions as cleared (leave 2 unreconciled)
        service.mark_transaction_cleared(test_transactions[0].id, statement_date)
        service.mark_transaction_cleared(test_transactions[1].id, statement_date)

        # Cleared balance: $2000 - $1200 = $800
        cleared_balance = service.calculate_cleared_balance(test_account.id)
        assert cleared_balance == Decimal('800.00')

        # Statement balance is higher (bank has cleared a transaction we haven't recorded)
        statement_balance = Decimal('850.00')
        discrepancy = service.calculate_discrepancy(test_account.id, statement_balance)

        assert discrepancy == Decimal('50.00')  # Positive: missing $50 in our records

        # Complete reconciliation with notes explaining discrepancy
        reconciliation = service.complete_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date,
            statement_balance=statement_balance,
            notes="Bank processed interest payment of $50 not yet recorded"
        )

        assert reconciliation.discrepancy == Decimal('50.00')
        assert reconciliation.notes == "Bank processed interest payment of $50 not yet recorded"
        assert reconciliation.is_balanced() is False

    def test_reconciliation_with_negative_discrepancy(
        self, service, test_account, test_transactions
    ):
        """
        Test reconciliation where cleared balance > statement balance.

        This happens when user recorded transactions that bank hasn't cleared yet.
        """
        statement_date = datetime.now().strftime('%Y-%m-%d')

        # Mark 3 transactions as cleared
        service.mark_transaction_cleared(test_transactions[0].id, statement_date)
        service.mark_transaction_cleared(test_transactions[1].id, statement_date)
        service.mark_transaction_cleared(test_transactions[2].id, statement_date)

        # Cleared balance: $2000 - $1200 - $125.50 = $674.50
        cleared_balance = service.calculate_cleared_balance(test_account.id)
        assert cleared_balance == Decimal('674.50')

        # Statement balance is lower (check hasn't cleared yet)
        statement_balance = Decimal('625.00')
        discrepancy = service.calculate_discrepancy(test_account.id, statement_balance)

        assert discrepancy == Decimal('-49.50')  # Negative: we have $49.50 extra in records

        # Complete reconciliation with notes
        reconciliation = service.complete_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date,
            statement_balance=statement_balance,
            notes="Grocery store check pending, not yet cleared by bank"
        )

        assert reconciliation.discrepancy == Decimal('-49.50')
        assert reconciliation.is_balanced() is False


class TestMarkUnmarkWorkflow:
    """Test marking and unmarking transactions during reconciliation."""

    def test_mark_then_unmark_then_remark_transaction(
        self, service, test_account, test_transactions
    ):
        """
        Test that transactions can be marked, unmarked, and re-marked correctly.

        This simulates user making a mistake and correcting it.
        """
        statement_date = datetime.now().strftime('%Y-%m-%d')
        txn = test_transactions[0]

        # Initial state: unreconciled
        assert txn.reconciliation_status == ReconciliationStatus.UNRECONCILED
        assert txn.reconciled_date is None
        assert txn.statement_date is None

        # Mark as cleared
        cleared_txn = service.mark_transaction_cleared(txn.id, statement_date)
        assert cleared_txn.reconciliation_status == ReconciliationStatus.CLEARED
        assert cleared_txn.reconciled_date is not None
        assert cleared_txn.statement_date == statement_date

        # Unmark (user made a mistake)
        uncleared_txn = service.unmark_transaction(txn.id)
        assert uncleared_txn.reconciliation_status == ReconciliationStatus.UNRECONCILED
        assert uncleared_txn.reconciled_date is None
        assert uncleared_txn.statement_date is None

        # Re-mark as cleared (user corrects mistake)
        recleared_txn = service.mark_transaction_cleared(txn.id, statement_date)
        assert recleared_txn.reconciliation_status == ReconciliationStatus.CLEARED
        assert recleared_txn.reconciled_date is not None
        assert recleared_txn.statement_date == statement_date

    def test_cleared_balance_updates_with_mark_unmark(
        self, service, test_account, test_transactions
    ):
        """Test that cleared balance recalculates correctly after mark/unmark."""
        statement_date = datetime.now().strftime('%Y-%m-%d')

        # Initial cleared balance: $0 (no transactions cleared)
        assert service.calculate_cleared_balance(test_account.id) == Decimal('0.00')

        # Mark first transaction ($2000)
        service.mark_transaction_cleared(test_transactions[0].id, statement_date)
        assert service.calculate_cleared_balance(test_account.id) == Decimal('2000.00')

        # Mark second transaction (-$1200)
        service.mark_transaction_cleared(test_transactions[1].id, statement_date)
        assert service.calculate_cleared_balance(test_account.id) == Decimal('800.00')

        # Unmark first transaction
        service.unmark_transaction(test_transactions[0].id)
        assert service.calculate_cleared_balance(test_account.id) == Decimal('-1200.00')

        # Unmark second transaction
        service.unmark_transaction(test_transactions[1].id)
        assert service.calculate_cleared_balance(test_account.id) == Decimal('0.00')


class TestConcurrentReconciliationPrevention:
    """Test that concurrent reconciliations are prevented."""

    def test_cannot_start_second_reconciliation_while_one_pending(
        self, service, test_account, transaction_repo
    ):
        """
        Test that starting a second reconciliation fails when one is in progress.

        Critical fix from tech review: prevents concurrency issues.
        """
        statement_date = datetime.now().strftime('%Y-%m-%d')

        # Create a transaction with pending status (simulates active reconciliation)
        pending_txn = Transaction(
            id=None,
            account_id=test_account.id,
            date=statement_date,
            description="Pending Transaction",
            amount=Decimal("-50.00"),
            category="Test",
            type="expense",
            reconciliation_status=ReconciliationStatus.PENDING
        )
        transaction_repo.create(pending_txn)

        # Attempt to start reconciliation should fail
        with pytest.raises(BusinessRuleError) as exc_info:
            service.start_reconciliation(
                account_id=test_account.id,
                statement_date=statement_date,
                statement_balance=Decimal('1000.00')
            )

        assert "already in progress" in str(exc_info.value)
        assert "Test Checking" in str(exc_info.value)


class TestReconciliationHistory:
    """Test reconciliation history tracking."""

    def test_multiple_reconciliations_create_history(
        self, service, test_account, test_transactions
    ):
        """
        Test that multiple reconciliations create searchable history.

        Verifies:
        - Each reconciliation is saved separately
        - History is ordered by date DESC (newest first)
        - All reconciliation details are preserved
        """
        # First reconciliation (3 days ago)
        statement_date_1 = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        service.mark_transaction_cleared(test_transactions[0].id, statement_date_1)
        reconciliation_1 = service.complete_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date_1,
            statement_balance=Decimal('2000.00'),
            notes="First reconciliation"
        )

        # Unmark transaction for second reconciliation
        service.unmark_transaction(test_transactions[0].id)

        # Second reconciliation (2 days ago)
        statement_date_2 = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        service.mark_transaction_cleared(test_transactions[0].id, statement_date_2)
        service.mark_transaction_cleared(test_transactions[1].id, statement_date_2)
        reconciliation_2 = service.complete_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date_2,
            statement_balance=Decimal('800.00'),
            notes="Second reconciliation"
        )

        # Unmark transactions for third reconciliation
        service.unmark_transaction(test_transactions[0].id)
        service.unmark_transaction(test_transactions[1].id)

        # Third reconciliation (today)
        statement_date_3 = datetime.now().strftime('%Y-%m-%d')
        for txn in test_transactions:
            service.mark_transaction_cleared(txn.id, statement_date_3)
        reconciliation_3 = service.complete_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date_3,
            statement_balance=Decimal('629.50'),
            notes="Third reconciliation"
        )

        # Get reconciliation history
        history = service.get_reconciliation_history(test_account.id, limit=10)

        assert len(history) == 3
        # Verify order (newest first)
        assert history[0].id == reconciliation_3.id
        assert history[1].id == reconciliation_2.id
        assert history[2].id == reconciliation_1.id

        # Verify details preserved
        assert history[2].statement_balance == Decimal('2000.00')
        assert history[1].statement_balance == Decimal('800.00')
        assert history[0].statement_balance == Decimal('629.50')

        assert history[2].notes == "First reconciliation"
        assert history[1].notes == "Second reconciliation"
        assert history[0].notes == "Third reconciliation"

    def test_get_history_with_limit(self, service, test_account, test_transactions):
        """Test that history limit works correctly."""
        # Create 5 reconciliations
        for i in range(5):
            statement_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            service.mark_transaction_cleared(test_transactions[0].id, statement_date)
            service.complete_reconciliation(
                account_id=test_account.id,
                statement_date=statement_date,
                statement_balance=Decimal('2000.00'),
                notes=f"Reconciliation {i+1}"
            )
            service.unmark_transaction(test_transactions[0].id)

        # Get only 3 most recent
        history = service.get_reconciliation_history(test_account.id, limit=3)
        assert len(history) == 3
        assert history[0].notes == "Reconciliation 1"  # Most recent
        assert history[1].notes == "Reconciliation 2"
        assert history[2].notes == "Reconciliation 3"


class TestAccountLastReconciledDateUpdate:
    """Test that account last_reconciled_date is updated correctly."""

    def test_account_last_reconciled_date_updates_on_completion(
        self, service, test_account, test_transactions, account_repo
    ):
        """
        Test that completing reconciliation updates account.last_reconciled_date.
        """
        # Initial state: never reconciled
        assert test_account.last_reconciled_date is None

        # Complete first reconciliation
        statement_date = datetime.now().strftime('%Y-%m-%d')
        service.mark_transaction_cleared(test_transactions[0].id, statement_date)
        reconciliation = service.complete_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date,
            statement_balance=Decimal('2000.00')
        )

        # Verify account updated
        updated_account = account_repo.get_by_id(test_account.id)
        assert updated_account.last_reconciled_date is not None
        assert updated_account.last_reconciled_date == reconciliation.reconciliation_date


class TestEdgeCases:
    """Test edge cases and unusual scenarios."""

    def test_reconciliation_with_no_transactions(
        self, service, test_account
    ):
        """
        Test reconciliation of account with no transactions.

        Should allow reconciliation with $0 balance.
        """
        statement_date = datetime.now().strftime('%Y-%m-%d')
        statement_balance = Decimal('0.00')

        # Start reconciliation
        session = service.start_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date,
            statement_balance=statement_balance
        )

        assert session['unreconciled_count'] == 0
        assert session['opening_balance'] == Decimal('0.00')

        # Calculate balances
        cleared_balance = service.calculate_cleared_balance(test_account.id)
        assert cleared_balance == Decimal('0.00')

        discrepancy = service.calculate_discrepancy(test_account.id, statement_balance)
        assert discrepancy == Decimal('0.00')

        # Complete reconciliation
        reconciliation = service.complete_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date,
            statement_balance=statement_balance
        )

        assert reconciliation.transaction_count == 0
        assert reconciliation.is_balanced() is True

    def test_reconciliation_with_all_transactions_already_cleared(
        self, service, test_account, test_transactions
    ):
        """
        Test reconciliation when all transactions are already cleared.

        Should show no unreconciled transactions.
        """
        statement_date = datetime.now().strftime('%Y-%m-%d')

        # Mark all transactions as cleared
        for txn in test_transactions:
            service.mark_transaction_cleared(txn.id, statement_date)

        # Get unreconciled transactions
        unreconciled = service.get_unreconciled_transactions(test_account.id)
        assert len(unreconciled) == 0

        # Start reconciliation (should show 0 unreconciled)
        session = service.start_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date,
            statement_balance=Decimal('629.50')
        )

        assert session['unreconciled_count'] == 0

    def test_opening_balance_from_previous_reconciliation(
        self, service, test_account, test_transactions
    ):
        """
        Test that second reconciliation uses first reconciliation's cleared balance as opening.
        """
        # First reconciliation: clear 2 transactions
        statement_date_1 = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        service.mark_transaction_cleared(test_transactions[0].id, statement_date_1)
        service.mark_transaction_cleared(test_transactions[1].id, statement_date_1)

        reconciliation_1 = service.complete_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date_1,
            statement_balance=Decimal('800.00')
        )

        # Second reconciliation: opening balance should be $800
        statement_date_2 = datetime.now().strftime('%Y-%m-%d')
        session = service.start_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date_2,
            statement_balance=Decimal('600.00')
        )

        assert session['opening_balance'] == Decimal('800.00')
        assert session['unreconciled_count'] == 2  # Transactions 3 and 4

        # Clear remaining transactions
        service.mark_transaction_cleared(test_transactions[2].id, statement_date_2)
        service.mark_transaction_cleared(test_transactions[3].id, statement_date_2)

        # Cleared balance = opening ($800) + new cleared (-$125.50 - $45) = $629.50
        cleared_balance = service.calculate_cleared_balance(test_account.id)
        assert cleared_balance == Decimal('629.50')

    def test_large_transaction_count(
        self, service, test_account, transaction_repo
    ):
        """
        Test reconciliation with 100+ transactions.

        Verifies performance and correct counting.
        """
        # Create 100 transactions
        statement_date = datetime.now().strftime('%Y-%m-%d')
        for i in range(100):
            txn = Transaction(
                id=None,
                account_id=test_account.id,
                date=statement_date,
                description=f"Transaction {i+1}",
                amount=Decimal('10.00'),
                category="Test",
                type="expense",
                reconciliation_status=ReconciliationStatus.UNRECONCILED
            )
            created_txn = transaction_repo.create(txn)
            service.mark_transaction_cleared(created_txn.id, statement_date)

        # Complete reconciliation
        reconciliation = service.complete_reconciliation(
            account_id=test_account.id,
            statement_date=statement_date,
            statement_balance=Decimal('1000.00')
        )

        assert reconciliation.transaction_count == 100
        assert reconciliation.cleared_balance == Decimal('1000.00')
