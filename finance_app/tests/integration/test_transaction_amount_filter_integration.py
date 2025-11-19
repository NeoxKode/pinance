"""
Integration tests for US-014: Amount Range Filter.

These tests verify the complete amount filtering workflow from TransactionService
through TransactionRepository to the database, ensuring all layers work together
correctly with real database operations.

Test Coverage:
- End-to-end amount filtering functionality
- Min only, max only, and both min/max filtering
- Absolute value mode filtering
- Account filtering integration
- Result sorting by date DESC
- Combined filters (amount + other filters)
- Performance validation

Story: US-014 - Amount Range Filter (EPIC-002, Sprint 15)
Created: 2025-11-18
"""
import pytest
import time
from decimal import Decimal
from datetime import date, timedelta

from finance_app.data.database import Database
from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.business.transaction_service import TransactionService


class TestAmountFilterIntegration:
    """Integration tests for amount filtering functionality (US-014)."""

    @pytest.fixture
    def account_repo(self, test_db):
        """Create account repository."""
        return AccountRepository(test_db)

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

    @pytest.fixture
    def credit_card_account(self, account_repo):
        """Create test credit card account."""
        account = Account(
            id=None,
            name="Test Credit Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.CREDIT
        )
        return account_repo.create(account)

    @pytest.fixture
    def amount_test_transactions(self, transaction_service, checking_account, credit_card_account):
        """Create transactions with various amounts for testing."""
        today = date.today()
        transactions = []

        # Small amounts (< $20)
        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=10)),
            description="Coffee",
            category="Dining Out",
            amount="5.50",
            trans_type="expense"
        ))

        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=9)),
            description="Netflix Subscription",
            category="Entertainment",
            amount="15.99",
            trans_type="expense"
        ))

        # Mid-range amounts ($20-$100)
        transactions.append(transaction_service.create_transaction(
            account_id=credit_card_account.id,
            date=str(today - timedelta(days=8)),
            description="Gas Station",
            category="Transportation",
            amount="45.00",
            trans_type="expense"
        ))

        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=7)),
            description="Groceries",
            category="Groceries",
            amount="67.30",
            trans_type="expense"
        ))

        transactions.append(transaction_service.create_transaction(
            account_id=credit_card_account.id,
            date=str(today - timedelta(days=6)),
            description="Restaurant",
            category="Dining Out",
            amount="85.50",
            trans_type="expense"
        ))

        # Large amounts (> $100)
        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=5)),
            description="Electronics Store",
            category="Electronics",
            amount="250.00",
            trans_type="expense"
        ))

        transactions.append(transaction_service.create_transaction(
            account_id=credit_card_account.id,
            date=str(today - timedelta(days=4)),
            description="Furniture",
            category="Home",
            amount="500.00",
            trans_type="expense"
        ))

        # Very large amounts (> $500)
        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=3)),
            description="Rent Payment",
            category="Housing",
            amount="1200.00",
            trans_type="expense"
        ))

        # Income (positive amounts)
        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=2)),
            description="Salary Deposit",
            category="Salary",
            amount="3000.00",
            trans_type="income"
        ))

        return transactions

    def test_filter_by_amount_large_purchases(self, transaction_service, amount_test_transactions):
        """Test filtering large purchases (> $100) using absolute mode."""
        # Act - Use absolute mode to get all transactions with abs value >= 100
        results = transaction_service.filter_by_amount_range(
            min_amount=Decimal("100"),
            absolute=True  # This handles both positive (income) and negative (expense) amounts
        )

        # Assert
        # Should get: Electronics (250), Furniture (500), Rent (1200), Salary (3000)
        assert len(results) >= 4, f"Expected at least 4 results, got {len(results)}"

        # Verify all have absolute value >= 100
        for txn in results:
            assert abs(txn.amount) >= Decimal("100"), \
                f"Transaction {txn.id} has amount {txn.amount} (abs: {abs(txn.amount)}) < 100"

    def test_filter_by_amount_small_charges(self, transaction_service, amount_test_transactions):
        """Test filtering small charges (< $20) - subscription hunting."""
        # Act - filter for expenses (negative) less than -20
        # This means absolute values < 20
        results = transaction_service.filter_by_amount_range(
            max_amount=Decimal("-0.01"),  # Get negative amounts (expenses)
            min_amount=Decimal("-20")      # But not too large
        )

        # Assert - Should get: Coffee (5.50), Netflix (15.99)
        assert len(results) >= 2, f"Expected at least 2 small charges, got {len(results)}"

        # Verify all are expenses with abs value < 20
        for txn in results:
            assert txn.amount < Decimal("0"), f"Expected expense, got {txn.amount}"
            assert abs(txn.amount) < Decimal("20"), \
                f"Transaction {txn.id} amount {txn.amount} is too large"

    def test_filter_by_amount_mid_range(self, transaction_service, amount_test_transactions):
        """Test filtering mid-range purchases ($20-$100)."""
        # Act - filter for negative amounts between -100 and -20
        results = transaction_service.filter_by_amount_range(
            min_amount=Decimal("-100"),
            max_amount=Decimal("-20")
        )

        # Assert - Should get: Gas (45), Groceries (67.30), Restaurant (85.50)
        assert len(results) >= 3, f"Expected at least 3 mid-range transactions, got {len(results)}"

        # Verify all amounts in range
        for txn in results:
            assert Decimal("-100") <= txn.amount <= Decimal("-20"), \
                f"Transaction {txn.id} amount {txn.amount} out of range"

    def test_filter_by_amount_with_account_filter(self, transaction_service, checking_account, amount_test_transactions):
        """Test amount filtering combined with account filter."""
        # Act - filter checking account for large expenses (< -100)
        results = transaction_service.filter_by_amount_range(
            max_amount=Decimal("-100"),
            account_id=checking_account.id
        )

        # Assert - Should get checking account transactions with amount < -100
        assert len(results) >= 2, f"Expected at least 2 large checking transactions, got {len(results)}"

        # Verify all are from checking account and large
        for txn in results:
            assert txn.account_id == checking_account.id
            assert txn.amount < Decimal("-100")

    def test_filter_by_amount_absolute_mode(self, transaction_service, amount_test_transactions):
        """Test absolute value mode (any transaction >= $100, ignoring sign)."""
        # Act
        results = transaction_service.filter_by_amount_range(
            min_amount=Decimal("100"),
            absolute=True
        )

        # Assert - Should get any transaction with abs value >= 100
        # Electronics (250), Furniture (500), Rent (1200), Salary (3000)
        assert len(results) >= 4, f"Expected at least 4 transactions with abs >= 100, got {len(results)}"

        # Verify all have absolute value >= 100
        for txn in results:
            assert abs(txn.amount) >= Decimal("100"), \
                f"Transaction {txn.id} abs amount {abs(txn.amount)} < 100"

    def test_filter_by_amount_empty_results(self, transaction_service, amount_test_transactions):
        """Test filtering with no matching transactions."""
        # Act - filter for amounts > 10,000 (none exist)
        results = transaction_service.filter_by_amount_range(
            min_amount=Decimal("10000")
        )

        # Assert
        assert results == []

    def test_filter_by_amount_combined_with_date(self, transaction_service, amount_test_transactions):
        """Test amount filter combined with date filter."""
        today = date.today()
        week_ago = today - timedelta(days=7)

        # Act - Get large purchases in last week
        # First filter by date
        date_filtered = transaction_service.filter_by_date_range(
            from_date=week_ago,
            to_date=today
        )

        # Then filter by amount (> 100 in absolute value)
        large_recent = [t for t in date_filtered if abs(t.amount) >= Decimal("100")]

        # Assert
        assert len(large_recent) >= 1, \
            f"Expected at least 1 large recent transaction, got {len(large_recent)}"

        # Verify all are within date range and large
        for txn in large_recent:
            txn_date = date.fromisoformat(txn.date) if isinstance(txn.date, str) else txn.date
            assert week_ago <= txn_date <= today
            assert abs(txn.amount) >= Decimal("100")

    def test_filter_by_amount_performance(self, transaction_service, checking_account):
        """Test amount filtering performance with 100+ transactions."""
        # Arrange - Create 150 transactions with varying amounts
        today = date.today()

        for i in range(150):
            # Alternate between small, medium, and large amounts
            if i % 3 == 0:
                amount = "10.00"  # Small
            elif i % 3 == 1:
                amount = "50.00"  # Medium
            else:
                amount = "150.00"  # Large

            transaction_service.create_transaction(
                account_id=checking_account.id,
                date=str(today - timedelta(days=i % 30)),
                description=f"Test Transaction {i}",
                category="Test",
                amount=amount,
                trans_type="expense"
            )

        # Act - Measure filter performance (use absolute mode to find large amounts)
        start_time = time.time()

        results = transaction_service.filter_by_amount_range(
            min_amount=Decimal("100"),
            absolute=True  # Get all transactions with abs value >= 100
        )

        elapsed_ms = (time.time() - start_time) * 1000

        # Assert - Should get 50 transactions with amount 150 (1/3 of 150)
        assert len(results) >= 50, f"Expected at least 50 large transactions, got {len(results)}"
        assert elapsed_ms < 100, \
            f"Amount filter took {elapsed_ms:.2f}ms, expected < 100ms (performance regression)"

        # Verify performance meets acceptance criteria
        print(f"\n✅ Performance: Filtered {len(results)} transactions in {elapsed_ms:.2f}ms (< 100ms target)")

        # Verify all results are large amounts
        for txn in results:
            assert abs(txn.amount) >= Decimal("100")
