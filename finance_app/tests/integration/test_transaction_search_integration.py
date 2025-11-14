"""
Integration tests for US-011: Basic Text Search.

These tests verify the complete search workflow from TransactionService
through TransactionRepository to the database, ensuring all layers work
together correctly.

Test Coverage:
- End-to-end search functionality
- Account filtering integration
- Result sorting by date DESC
- Empty keyword business rule
- No results scenario

Story: US-011 - Basic Text Search (EPIC-002, Sprint 13)
Created: 2025-11-11
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta

from finance_app.data.database import Database
from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.business.transaction_service import TransactionService


class TestTransactionSearchIntegration:
    """Integration tests for transaction search functionality (US-011)."""

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
    def savings_account(self, account_repo):
        """Create test savings account."""
        account = Account(
            id=None,
            name="Test Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            balance=Decimal("5000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        return account_repo.create(account)

    @pytest.fixture
    def sample_transactions(self, transaction_service, checking_account, savings_account):
        """Create sample transactions for testing search."""
        today = date.today()
        transactions = []

        # Checking account transactions
        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=5)),
            description="Starbucks Coffee",
            category="Dining Out",
            amount="5.50",
            trans_type="expense"
        ))

        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=3)),
            description="Amazon Prime Subscription",
            category="Services",
            amount="14.99",
            trans_type="expense"
        ))

        transactions.append(transaction_service.create_transaction(
            account_id=checking_account.id,
            date=str(today - timedelta(days=1)),
            description="Monthly Salary",
            category="Income",
            amount="3000.00",
            trans_type="income"
        ))

        # Savings account transactions
        transactions.append(transaction_service.create_transaction(
            account_id=savings_account.id,
            date=str(today - timedelta(days=2)),
            description="Amazon Gift Card",
            category="Gifts",
            amount="50.00",
            trans_type="income"
        ))

        transactions.append(transaction_service.create_transaction(
            account_id=savings_account.id,
            date=str(today),
            description="Grocery Store Purchase",
            category="Groceries",
            amount="85.32",
            trans_type="expense"
        ))

        return transactions

    # ========================================================================
    # TEST 1: End-to-End Search Integration
    # ========================================================================

    def test_search_integration_end_to_end(
        self, transaction_service, sample_transactions
    ):
        """
        Test 1/5: Verify complete search workflow from service to database.

        US-011: Validates that search_transactions() correctly flows through
        all layers (service → repository → database) and returns matching results.

        Setup: 5 transactions with various descriptions
        Test: Search for "Amazon" keyword
        Expected: 2 transactions match (Amazon Prime, Amazon Gift Card)
        """
        # Act: Search for "Amazon" (case-insensitive)
        results = transaction_service.search_transactions("Amazon")

        # Assert: Found both Amazon transactions
        assert len(results) == 2, "Should find 2 transactions with 'Amazon'"

        descriptions = [t.description for t in results]
        assert any("Amazon Prime" in d for d in descriptions), \
            "Should find 'Amazon Prime Subscription'"
        assert any("Amazon Gift Card" in d for d in descriptions), \
            "Should find 'Amazon Gift Card'"

        # Assert: All results contain keyword (case-insensitive)
        for transaction in results:
            assert "amazon" in transaction.description.lower(), \
                f"Result '{transaction.description}' should contain 'Amazon'"

    # ========================================================================
    # TEST 2: Search with Account Filter
    # ========================================================================

    def test_search_integration_with_account_filter(
        self, transaction_service, checking_account, savings_account, sample_transactions
    ):
        """
        Test 2/5: Verify search correctly filters by account.

        US-011: Tests that account_id parameter properly restricts search
        results to transactions within the specified account only.

        Setup: 5 transactions across 2 accounts
        Test: Search for "Amazon" in checking account only
        Expected: 1 transaction (Amazon Prime in checking), not Gift Card (savings)
        """
        # Act: Search for "Amazon" in checking account only
        results = transaction_service.search_transactions(
            "Amazon",
            account_id=checking_account.id
        )

        # Assert: Found only checking account transaction
        assert len(results) == 1, \
            "Should find only 1 'Amazon' transaction in checking account"

        # Assert: Result is from checking account
        assert results[0].account_id == checking_account.id, \
            "Result should be from checking account"
        assert "Amazon Prime" in results[0].description, \
            "Should find 'Amazon Prime Subscription'"

        # Verify: Savings account Amazon transaction not included
        assert all(t.account_id == checking_account.id for t in results), \
            "All results should be from checking account"

    # ========================================================================
    # TEST 3: Result Sorting by Date DESC
    # ========================================================================

    def test_search_integration_sorting(
        self, transaction_service, sample_transactions
    ):
        """
        Test 3/5: Verify search results are sorted by date DESC (newest first).

        US-011: Validates that repository correctly orders results by date
        descending, ensuring users see most recent transactions first.

        Setup: 5 transactions with different dates
        Test: Search without keyword filter (all transactions)
        Expected: Results ordered from newest to oldest by date
        """
        # Act: Search for common term to get multiple results
        results = transaction_service.search_transactions("a")  # Matches multiple

        # Assert: At least 3 results for meaningful sorting test
        assert len(results) >= 3, "Should have multiple results for sorting test"

        # Assert: Results are sorted by date DESC (newest first)
        dates = [t.date for t in results]
        assert dates == sorted(dates, reverse=True), \
            f"Results should be sorted by date DESC (newest first): {dates}"

        # Additional check: First result should be most recent
        assert results[0].date == max(dates), \
            "First result should be the most recent transaction"

    # ========================================================================
    # TEST 4: Empty Keyword Behavior
    # ========================================================================

    def test_search_integration_empty_keyword(
        self, transaction_service, sample_transactions
    ):
        """
        Test 4/5: Verify empty keyword returns empty list (business rule).

        US-011: Tests business rule that empty or whitespace-only keywords
        return empty list rather than all transactions (for clarity).

        Setup: 5 transactions exist
        Test: Search with empty string and whitespace-only string
        Expected: Empty list returned (not all transactions)
        """
        # Act: Search with empty keyword
        results_empty = transaction_service.search_transactions("")

        # Assert: Returns empty list
        assert results_empty == [], \
            "Empty keyword should return empty list (business rule)"
        assert len(results_empty) == 0, \
            "Empty keyword should not return all transactions"

        # Act: Search with whitespace-only keyword
        results_whitespace = transaction_service.search_transactions("   ")

        # Assert: Whitespace-only also returns empty list
        assert results_whitespace == [], \
            "Whitespace-only keyword should return empty list"

        # Verify: Service layer trims and validates (not repository)
        # This confirms business rule is in service layer as designed
        assert isinstance(results_empty, list), "Should return list type"
        assert isinstance(results_whitespace, list), "Should return list type"

    # ========================================================================
    # TEST 5: No Results Scenario
    # ========================================================================

    def test_search_integration_no_results(
        self, transaction_service, sample_transactions
    ):
        """
        Test 5/5: Verify search with no matches returns empty list gracefully.

        US-011: Tests that search handles no-match scenario cleanly without
        exceptions, returning an empty list.

        Setup: 5 transactions with known descriptions
        Test: Search for keyword that doesn't exist
        Expected: Empty list, no exceptions raised
        """
        # Act: Search for keyword that doesn't match any transaction
        results = transaction_service.search_transactions("xyz123notfound")

        # Assert: Returns empty list (not None, not exception)
        assert results == [], \
            "No-match search should return empty list"
        assert len(results) == 0, \
            "Should have zero results for non-existent keyword"

        # Assert: Return type is list (not None)
        assert isinstance(results, list), \
            "Should return list type even with no results"

        # Verify: No exceptions raised
        # (If we got here, no exception was raised - test passes)

    # ========================================================================
    # BONUS TEST: Case-Insensitive Search
    # ========================================================================

    def test_search_integration_case_insensitive(
        self, transaction_service, sample_transactions
    ):
        """
        Bonus test: Verify search is case-insensitive (SQLite LIKE behavior).

        US-011: Confirms that search works regardless of case, making it
        user-friendly and intuitive.

        Setup: Transactions with mixed case descriptions
        Test: Search with different case variations
        Expected: All case variations return same results
        """
        # Act: Search with different case variations
        results_lower = transaction_service.search_transactions("amazon")
        results_upper = transaction_service.search_transactions("AMAZON")
        results_mixed = transaction_service.search_transactions("AmAzOn")

        # Assert: All return same number of results
        assert len(results_lower) == len(results_upper) == len(results_mixed), \
            "Case should not affect search results"

        assert len(results_lower) == 2, \
            "Should find 2 'Amazon' transactions regardless of case"

        # Assert: Results are identical
        lower_ids = {t.id for t in results_lower}
        upper_ids = {t.id for t in results_upper}
        mixed_ids = {t.id for t in results_mixed}

        assert lower_ids == upper_ids == mixed_ids, \
            "All case variations should return same transactions"

    # ========================================================================
    # BONUS TEST: Partial Substring Matching
    # ========================================================================

    def test_search_integration_partial_match(
        self, transaction_service, sample_transactions
    ):
        """
        Bonus test: Verify partial substring matching works correctly.

        US-011: Validates that search uses LIKE '%keyword%' pattern,
        matching substrings anywhere in description.

        Setup: Transactions with multi-word descriptions
        Test: Search with partial words
        Expected: Matches transactions containing the substring
        """
        # Act: Search for partial word "Star" (should match "Starbucks")
        results_star = transaction_service.search_transactions("Star")

        # Assert: Found Starbucks transaction
        assert len(results_star) == 1, "Should find 'Starbucks Coffee'"
        assert "Starbucks" in results_star[0].description

        # Act: Search for partial word "bucks" (middle of word)
        results_bucks = transaction_service.search_transactions("bucks")

        # Assert: Also found Starbucks (substring match)
        assert len(results_bucks) == 1, "Should find 'Starbucks Coffee'"
        assert "Starbucks" in results_bucks[0].description

        # Act: Search for "Coffee" (end of description)
        results_coffee = transaction_service.search_transactions("Coffee")

        # Assert: Found Starbucks transaction
        assert len(results_coffee) == 1, "Should find 'Starbucks Coffee'"
        assert "Coffee" in results_coffee[0].description
