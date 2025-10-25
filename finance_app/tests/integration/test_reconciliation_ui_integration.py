"""
Integration tests for US-004 Account Reconciliation UI workflow.

Tests the full reconciliation workflow from MainWindow through ReconciliationDialog
to ReconciliationService and back to UI refresh.

Story: US-004 - Phase 6 - UI Integration Testing
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from finance_app.data.database import Database
from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance, Transaction
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.transaction_repository import TransactionRepository
from finance_app.business.reconciliation_service import ReconciliationService


class TestReconciliationUIIntegration:
    """Integration tests for reconciliation UI workflow."""

    @pytest.fixture
    def db(self, tmp_path):
        """Create a test database."""
        db_path = tmp_path / "test_reconciliation_ui.db"
        db = Database(str(db_path))
        yield db
        db.close()

    @pytest.fixture
    def account_repo(self, db):
        """Create account repository."""
        return AccountRepository(db)

    @pytest.fixture
    def transaction_repo(self, db):
        """Create transaction repository."""
        return TransactionRepository(db)

    @pytest.fixture
    def reconciliation_service(self, db):
        """Create reconciliation service."""
        return ReconciliationService(db)

    @pytest.fixture
    def checking_account(self, account_repo):
        """Create a checking account for testing."""
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

    def test_reconciliation_workflow_with_transactions(
        self,
        db,
        checking_account,
        transaction_repo,
        reconciliation_service
    ):
        """
        Test complete reconciliation workflow.

        This test simulates:
        1. User selects account in MainWindow
        2. User opens ReconciliationDialog
        3. Dialog loads unreconciled transactions
        4. User checks transactions as cleared
        5. User enters statement balance
        6. User completes reconciliation
        7. UI refreshes to show reconciliation status
        """
        # Setup: Create test transactions
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        txn1 = Transaction(
            id=None,
            account_id=checking_account.id,
            date=yesterday,
            description="Grocery Store",
            category="Food",
            amount=Decimal("-50.00"),
            type="expense"
        )
        txn1 = transaction_repo.create(txn1)

        txn2 = Transaction(
            id=None,
            account_id=checking_account.id,
            date=today,
            description="Salary Deposit",
            category="Income",
            amount=Decimal("2000.00"),
            type="income"
        )
        txn2 = transaction_repo.create(txn2)

        txn3 = Transaction(
            id=None,
            account_id=checking_account.id,
            date=today,
            description="Electric Bill",
            category="Utilities",
            amount=Decimal("-100.00"),
            type="expense"
        )
        txn3 = transaction_repo.create(txn3)

        # Step 1: Start reconciliation (simulates dialog open)
        session = reconciliation_service.start_reconciliation(
            account_id=checking_account.id,
            statement_date=today,
            statement_balance=Decimal("0.00")  # Will be updated
        )

        assert session is not None
        assert session['account_id'] == checking_account.id
        # Opening balance is 0 for first reconciliation (no previous reconciliation)
        assert session['opening_balance'] == Decimal("0.00")

        # Step 2: Get unreconciled transactions (simulates dialog load)
        unreconciled = reconciliation_service.get_unreconciled_transactions(
            checking_account.id
        )

        assert len(unreconciled) == 3
        assert all(txn.reconciliation_status.value == 'unreconciled' for txn in unreconciled)

        # Step 3: Mark transactions as cleared (simulates user checking boxes)
        # User checks txn1 and txn2, but not txn3 (not on statement yet)
        reconciliation_service.mark_transaction_cleared(
            transaction_id=txn1.id,
            statement_date=today
        )
        reconciliation_service.mark_transaction_cleared(
            transaction_id=txn2.id,
            statement_date=today
        )

        # Verify transactions are marked as cleared
        txn1_updated = transaction_repo.get_by_id(txn1.id)
        assert txn1_updated.reconciliation_status.value == 'cleared'
        assert txn1_updated.statement_date == today

        # Step 4: Calculate cleared balance
        cleared_balance = reconciliation_service.calculate_cleared_balance(
            checking_account.id
        )
        # Opening: 0.00 (first reconciliation)
        # Cleared: -50.00 (txn1) + 2000.00 (txn2) = 1950.00
        # Expected cleared balance: 0.00 + 1950.00 = 1950.00
        assert cleared_balance == Decimal("1950.00")

        # Step 5: Complete reconciliation
        statement_balance = Decimal("1950.00")  # Matches cleared balance
        reconciliation = reconciliation_service.complete_reconciliation(
            account_id=checking_account.id,
            statement_date=today,
            statement_balance=statement_balance,
            notes=None
        )

        assert reconciliation.id is not None
        assert reconciliation.account_id == checking_account.id
        assert reconciliation.statement_balance == statement_balance
        assert reconciliation.transaction_count == 2  # txn1 and txn2
        assert reconciliation.discrepancy == Decimal("0.00")

        # Step 6: Verify transactions status (cleared ones remain cleared)
        txn1_final = transaction_repo.get_by_id(txn1.id)
        txn2_final = transaction_repo.get_by_id(txn2.id)
        txn3_final = transaction_repo.get_by_id(txn3.id)

        assert txn1_final.reconciliation_status.value == 'cleared'
        assert txn1_final.reconciled_date == today  # Set when marked cleared
        assert txn2_final.reconciliation_status.value == 'cleared'
        assert txn2_final.reconciled_date == today
        assert txn3_final.reconciliation_status.value == 'unreconciled'  # Not cleared

        # Step 7: Verify account last_reconciled_date is updated
        from finance_app.data.repositories.account_repository import AccountRepository
        account_repo = AccountRepository(db)
        account_updated = account_repo.get_by_id(checking_account.id)
        assert account_updated.last_reconciled_date == today

        # Step 8: Verify unreconciled transactions after reconciliation
        unreconciled_after = reconciliation_service.get_unreconciled_transactions(
            checking_account.id
        )
        assert len(unreconciled_after) == 1
        assert unreconciled_after[0].id == txn3.id

    def test_reconciliation_with_discrepancy(
        self,
        db,
        checking_account,
        transaction_repo,
        reconciliation_service
    ):
        """
        Test reconciliation workflow with discrepancy.

        Simulates user accepting reconciliation even when there's a discrepancy
        and providing notes to explain it.
        """
        today = datetime.now().strftime('%Y-%m-%d')

        # Create a single transaction
        txn = Transaction(
            id=None,
            account_id=checking_account.id,
            date=today,
            description="Test Transaction",
            category="Test",
            amount=Decimal("-25.00"),
            type="expense"
        )
        txn = transaction_repo.create(txn)

        # Start reconciliation
        session = reconciliation_service.start_reconciliation(
            account_id=checking_account.id,
            statement_date=today,
            statement_balance=Decimal("0.00")
        )

        # Mark transaction as cleared
        reconciliation_service.mark_transaction_cleared(
            transaction_id=txn.id,
            statement_date=today
        )

        # Complete with statement balance that doesn't match
        # Opening: 0.00 (first reconciliation), Cleared: -25.00, Expected: -25.00
        # But statement shows: -20.00 (discrepancy of +5.00)
        statement_balance = Decimal("-20.00")
        reconciliation = reconciliation_service.complete_reconciliation(
            account_id=checking_account.id,
            statement_date=today,
            statement_balance=statement_balance,
            notes="Bank fee of $5.00 not yet recorded"
        )

        assert reconciliation.discrepancy == Decimal("5.00")  # Positive discrepancy
        assert reconciliation.notes == "Bank fee of $5.00 not yet recorded"

        # Verify transaction is still cleared despite discrepancy
        txn_final = transaction_repo.get_by_id(txn.id)
        assert txn_final.reconciliation_status.value == 'cleared'

    def test_reconciliation_history(
        self,
        db,
        checking_account,
        transaction_repo,
        reconciliation_service
    ):
        """Test reconciliation history retrieval."""
        today = datetime.now().strftime('%Y-%m-%d')

        # Create and reconcile a transaction
        txn = Transaction(
            id=None,
            account_id=checking_account.id,
            date=today,
            description="Test Transaction",
            category="Test",
            amount=Decimal("100.00"),
            type="income"
        )
        txn = transaction_repo.create(txn)

        # Start and complete reconciliation
        reconciliation_service.start_reconciliation(
            account_id=checking_account.id,
            statement_date=today,
            statement_balance=Decimal("100.00")
        )

        reconciliation_service.mark_transaction_cleared(
            transaction_id=txn.id,
            statement_date=today
        )

        reconciliation = reconciliation_service.complete_reconciliation(
            account_id=checking_account.id,
            statement_date=today,
            statement_balance=Decimal("100.00"),
            notes=None
        )

        # Get reconciliation history
        history = reconciliation_service.get_reconciliation_history(
            account_id=checking_account.id,
            limit=10
        )

        assert len(history) == 1
        assert history[0].id == reconciliation.id
        assert history[0].account_id == checking_account.id
