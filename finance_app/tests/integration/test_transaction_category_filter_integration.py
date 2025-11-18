"""
Integration tests for US-013: Category Filter.

These tests verify the complete category filtering workflow from TransactionService
through TransactionRepository to the database, ensuring all layers work together
correctly with real database operations.

Test Coverage:
- End-to-end category filtering functionality
- Category counts calculation with real data
- Single and multiple category filtering
- Account filtering integration
- Result sorting by date DESC
- Empty categories handling

Story: US-013 - Category Filter (EPIC-002, Sprint 14)
Created: 2025-11-17
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta

from finance_app.data.database import Database
from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.business.transaction_service import TransactionService


class TestCategoryFilterIntegration:
    """Integration tests for category filtering functionality (US-013)."""

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
    def diverse_transactions(self, transaction_service, checking_account, credit_card_account):
        """Create diverse transactions across multiple categories for testing."""
        today = date.today()
        transactions = []

        # Groceries category (checking account)
        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=10)),
            description="Whole Foods Market",
            category="Groceries",
            amount="85.50",
            trans_type="expense"
        ))

        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=5)),
            description="Trader Joe's",
            category="Groceries",
            amount="67.30",
            trans_type="expense"
        ))

        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=2)),
            description="Safeway",
            category="Groceries",
            amount="42.15",
            trans_type="expense"
        ))

        # Dining Out category (credit card account)
        transactions.append(transaction_service.create_transaction(
            account_id=credit_card_account.id,
            date=str(today - timedelta(days=8)),
            description="Starbucks Coffee",
            category="Dining Out",
            amount="5.50",
            trans_type="expense"
        ))

        transactions.append(transaction_service.create_transaction(
            account_id=credit_card_account.id,
            date=str(today - timedelta(days=4)),
            description="Italian Restaurant",
            category="Dining Out",
            amount="75.00",
            trans_type="expense"
        ))

        # Transportation category (checking account)
        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=7)),
            description="Gas Station",
            category="Transportation",
            amount="45.00",
            trans_type="expense"
        ))

        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=3)),
            description="Uber Ride",
            category="Transportation",
            amount="18.50",
            trans_type="expense"
        ))

        # Entertainment category (credit card account)
        transactions.append(transaction_service.create_transaction(
            account_id=credit_card_account.id,
            date=str(today - timedelta(days=6)),
            description="Movie Theater",
            category="Entertainment",
            amount="25.00",
            trans_type="expense"
        ))

        # Income category (checking account)
        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=1)),
            description="Monthly Salary",
            category="Income",
            amount="3000.00",
            trans_type="income"
        ))

        return transactions

    # ========================================================================
    # Test 1: Get Categories with Counts (All Accounts)
    # ========================================================================

    def test_get_categories_with_counts_all_accounts(
        self,
        transaction_service,
        diverse_transactions
    ):
        """
        Test getting all categories with counts from all accounts.

        Expected:
        - Dining Out: 2
        - Entertainment: 1
        - Groceries: 3
        - Income: 1
        - Transportation: 2
        """
        # Act
        categories = transaction_service.get_categories_with_counts()

        # Assert
        assert len(categories) == 5
        # Verify alphabetical sorting
        category_names = [cat[0] for cat in categories]
        assert category_names == sorted(category_names)

        # Verify counts
        category_dict = dict(categories)
        assert category_dict['Groceries'] == 3
        assert category_dict['Dining Out'] == 2
        assert category_dict['Transportation'] == 2
        assert category_dict['Entertainment'] == 1
        assert category_dict['Income'] == 1

    # ========================================================================
    # Test 2: Get Categories with Counts (Single Account Filter)
    # ========================================================================

    def test_get_categories_with_counts_single_account(
        self,
        transaction_service,
        checking_account,
        diverse_transactions
    ):
        """
        Test getting categories with counts from specific account only.

        Checking account categories:
        - Groceries: 3
        - Transportation: 2
        - Income: 1
        """
        # Act
        categories = transaction_service.get_categories_with_counts(
            account_id=checking_account.id
        )

        # Assert
        category_dict = dict(categories)
        assert len(category_dict) == 3
        assert category_dict['Groceries'] == 3
        assert category_dict['Transportation'] == 2
        assert category_dict['Income'] == 1
        # Credit card categories should not appear
        assert 'Dining Out' not in category_dict
        assert 'Entertainment' not in category_dict

    # ========================================================================
    # Test 3: Filter by Single Category
    # ========================================================================

    def test_filter_by_single_category(
        self,
        transaction_service,
        diverse_transactions
    ):
        """
        Test filtering transactions by single category (Groceries).

        Expected: 3 Groceries transactions, sorted by date DESC
        """
        # Act
        results = transaction_service.filter_by_categories(['Groceries'])

        # Assert
        assert len(results) == 3
        # All results should be Groceries category
        for txn in results:
            assert txn.category == 'Groceries'

        # Verify sorted by date DESC
        dates = [txn.date for txn in results]
        assert dates == sorted(dates, reverse=True)

        # Verify transactions
        descriptions = [txn.description for txn in results]
        assert 'Safeway' in descriptions
        assert 'Trader Joe\'s' in descriptions
        assert 'Whole Foods Market' in descriptions

    # ========================================================================
    # Test 4: Filter by Multiple Categories
    # ========================================================================

    def test_filter_by_multiple_categories(
        self,
        transaction_service,
        diverse_transactions
    ):
        """
        Test filtering transactions by multiple categories (Groceries + Transportation).

        Expected: 5 transactions (3 Groceries + 2 Transportation)
        """
        # Act
        results = transaction_service.filter_by_categories(
            ['Groceries', 'Transportation']
        )

        # Assert
        assert len(results) == 5

        # All results should be in selected categories
        for txn in results:
            assert txn.category in ['Groceries', 'Transportation']

        # Count by category
        groceries_count = sum(1 for txn in results if txn.category == 'Groceries')
        transportation_count = sum(1 for txn in results if txn.category == 'Transportation')
        assert groceries_count == 3
        assert transportation_count == 2

        # Verify sorted by date DESC
        dates = [txn.date for txn in results]
        assert dates == sorted(dates, reverse=True)

    # ========================================================================
    # Test 5: Filter by Category with Account Filter
    # ========================================================================

    def test_filter_by_category_with_account_filter(
        self,
        transaction_service,
        credit_card_account,
        diverse_transactions
    ):
        """
        Test filtering by category within specific account.

        Credit card account should only have:
        - Dining Out: 2
        - Entertainment: 1
        """
        # Act
        results = transaction_service.filter_by_categories(
            ['Dining Out'],
            account_id=credit_card_account.id
        )

        # Assert
        assert len(results) == 2
        # All results should be Dining Out and from credit card account
        for txn in results:
            assert txn.category == 'Dining Out'
            assert txn.account_id == credit_card_account.id

        # Verify descriptions
        descriptions = [txn.description for txn in results]
        assert 'Starbucks Coffee' in descriptions
        assert 'Italian Restaurant' in descriptions

    # ========================================================================
    # Test 6: Filter by Empty Category List
    # ========================================================================

    def test_filter_by_empty_category_list(
        self,
        transaction_service,
        diverse_transactions
    ):
        """
        Test filtering with empty category list returns no results.

        Expected: Empty list (no transactions)
        """
        # Act
        results = transaction_service.filter_by_categories([])

        # Assert
        assert results == []

    # ========================================================================
    # Test 7: Filter by Non-Existent Category
    # ========================================================================

    def test_filter_by_nonexistent_category(
        self,
        transaction_service,
        diverse_transactions
    ):
        """
        Test filtering by category that doesn't exist returns no results.

        Expected: Empty list (no transactions match 'NonExistent')
        """
        # Act
        results = transaction_service.filter_by_categories(['NonExistent'])

        # Assert
        assert results == []

    # ========================================================================
    # Test 8: Performance - Filter 100+ Transactions
    # ========================================================================

    def test_category_filter_performance_many_transactions(
        self,
        transaction_service,
        checking_account
    ):
        """
        Test category filtering performance with 100+ transactions.

        Expected: Filter completes in < 100ms (performance requirement)
        """
        import time

        # Create 100 transactions across 5 categories
        today = date.today()
        categories = ['Groceries', 'Dining Out', 'Transportation', 'Entertainment', 'Utilities']

        for i in range(100):
            transaction_service.create_transaction(
                account_id=checking_account.id,
                date=str(today - timedelta(days=i)),
                description=f"Transaction {i}",
                category=categories[i % 5],
                amount=str(10.00 + (i * 0.50)),
                trans_type="expense"
            )

        # Measure filter performance
        start_time = time.time()
        results = transaction_service.filter_by_categories(['Groceries', 'Dining Out'])
        end_time = time.time()

        elapsed_ms = (end_time - start_time) * 1000

        # Assert
        assert len(results) == 40  # 20 Groceries + 20 Dining Out
        assert elapsed_ms < 100  # Performance requirement: < 100ms
        print(f"Filter time: {elapsed_ms:.2f}ms")
