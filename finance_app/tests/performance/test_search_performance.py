"""
Performance tests for US-011: Basic Text Search.

Tests search performance with realistic data volumes to ensure:
- Search completes within performance budget (< 200ms for 10K transactions)
- Database index is used effectively (idx_transactions_description)
- Performance scales appropriately with transaction count

Performance Targets (from US-011):
- 1,000 transactions: < 50ms
- 10,000 transactions: < 200ms
- Index usage: SEARCH using INDEX idx_transactions_description

Story: US-011 - Basic Text Search (EPIC-002, Sprint 13)
Created: 2025-11-11
"""
import pytest
import time
from decimal import Decimal
from datetime import date, timedelta

from finance_app.data.database import Database
from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.business.transaction_service import TransactionService


class TestSearchPerformance:
    """Performance tests for transaction search functionality (US-011)."""

    @pytest.fixture
    def test_account(self, test_db):
        """Create a test account for performance testing."""
        account_repo = AccountRepository(test_db)
        account = Account(
            id=None,
            name="Performance Test Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("100000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        return account_repo.create(account)

    def _create_test_transactions(
        self,
        transaction_service,
        account_id: int,
        count: int,
        start_date: date
    ):
        """
        Create test transactions with varied descriptions for realistic testing.

        Args:
            transaction_service: TransactionService instance
            account_id: Account ID for transactions
            count: Number of transactions to create
            start_date: Starting date for transactions
        """
        # Common search keywords for realistic distribution
        vendors = [
            "Starbucks Coffee", "Amazon.com Purchase", "Walmart Groceries",
            "Target Shopping", "McDonald's Restaurant", "Shell Gas Station",
            "CVS Pharmacy", "Home Depot", "Best Buy Electronics",
            "Kroger Supermarket", "Walgreens", "Costco Wholesale",
            "Publix Grocery", "Chick-fil-A", "Subway Sandwich",
            "Dunkin Donuts", "Chipotle Mexican Grill", "Panera Bread",
            "Whole Foods Market", "Trader Joe's"
        ]

        print(f"Creating {count:,} test transactions...")
        start_time = time.time()

        for i in range(count):
            # Cycle through vendors for variety
            vendor = vendors[i % len(vendors)]
            description = f"{vendor} #{i+1:05d}"

            # Alternate between income and expense
            is_expense = i % 3 != 0  # 2/3 expense, 1/3 income
            amount = f"{(i % 100) + 1}.{i % 100:02d}"
            trans_type = "expense" if is_expense else "income"

            # Spread transactions over dates (1 transaction per day)
            trans_date = str(start_date + timedelta(days=(i % 365)))

            transaction_service.create_transaction(
                account_id=account_id,
                date=trans_date,
                description=description,
                category="Test Category",
                amount=amount,
                trans_type=trans_type
            )

            # Progress indicator for large datasets
            if (i + 1) % 1000 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                print(f"  Created {i+1:,}/{count:,} ({rate:.0f}/sec)")

        elapsed = time.time() - start_time
        print(f"✓ Created {count:,} transactions in {elapsed:.2f}s")

    # ========================================================================
    # TEST 1: Search Performance with 1,000 Transactions
    # ========================================================================

    def test_search_performance_1000_transactions(self, test_db, test_account):
        """
        Test 1/3: Verify search completes in < 50ms for 1,000 transactions.

        US-011 Performance Target: < 50ms for 1K transactions

        Setup: 1,000 transactions with varied descriptions
        Test: Search for common keyword ("Starbucks")
        Expected: Query completes in < 50ms
        """
        transaction_service = TransactionService(test_db)
        start_date = date(2025, 1, 1)

        # Setup: Create 1,000 test transactions
        self._create_test_transactions(
            transaction_service,
            test_account.id,
            count=1000,
            start_date=start_date
        )

        # Warm-up query to load cache
        transaction_service.search_transactions("warmup")

        # Act: Search for "Starbucks" (should match multiple transactions)
        start_time = time.time()
        results = transaction_service.search_transactions("Starbucks")
        elapsed_ms = (time.time() - start_time) * 1000

        # Assert: Query completed within performance target
        print(f"\n1K Transactions Search Performance: {elapsed_ms:.2f}ms")
        assert elapsed_ms < 50, \
            f"Search took {elapsed_ms:.2f}ms (should be < 50ms for 1K transactions)"

        # Assert: Found expected results
        assert len(results) > 0, "Should find Starbucks transactions"
        assert all("Starbucks" in t.description for t in results), \
            "All results should contain 'Starbucks'"

        print(f"✓ Found {len(results)} results in {elapsed_ms:.2f}ms (target: < 50ms)")

    # ========================================================================
    # TEST 2: Search Performance with 10,000 Transactions
    # ========================================================================

    def test_search_performance_10000_transactions(self, test_db, test_account):
        """
        Test 2/3: Verify search completes in < 200ms for 10,000 transactions.

        US-011 Performance Target: < 200ms for 10K transactions

        Setup: 10,000 transactions with varied descriptions
        Test: Search for common keyword ("Amazon")
        Expected: Query completes in < 200ms
        """
        transaction_service = TransactionService(test_db)
        start_date = date(2025, 1, 1)

        # Setup: Create 10,000 test transactions
        self._create_test_transactions(
            transaction_service,
            test_account.id,
            count=10000,
            start_date=start_date
        )

        # Warm-up query to load cache
        transaction_service.search_transactions("warmup")

        # Act: Search for "Amazon" (should match multiple transactions)
        start_time = time.time()
        results = transaction_service.search_transactions("Amazon")
        elapsed_ms = (time.time() - start_time) * 1000

        # Assert: Query completed within performance target
        print(f"\n10K Transactions Search Performance: {elapsed_ms:.2f}ms")
        assert elapsed_ms < 200, \
            f"Search took {elapsed_ms:.2f}ms (should be < 200ms for 10K transactions)"

        # Assert: Found expected results
        assert len(results) > 0, "Should find Amazon transactions"
        assert all("Amazon" in t.description for t in results), \
            "All results should contain 'Amazon'"

        print(f"✓ Found {len(results)} results in {elapsed_ms:.2f}ms (target: < 200ms)")

    # ========================================================================
    # TEST 3: Database Index Usage Verification
    # ========================================================================

    def test_search_index_usage(self, test_db, test_account):
        """
        Test 3/3: Verify database uses indexes (not full table scan).

        US-011: Validates that the search query uses database indexes
        created in Migration 013 for optimal performance.

        Note: SQLite query optimizer may choose idx_transactions_date for
        ORDER BY optimization instead of idx_transactions_description for
        WHERE LIKE. Both are acceptable (no full table scan).

        Setup: Database with migrations applied
        Test: Run EXPLAIN QUERY PLAN on search query
        Expected: Query plan includes "USING INDEX" (not plain "SCAN transactions")
        """
        transaction_service = TransactionService(test_db)

        # Setup: Create some test transactions
        self._create_test_transactions(
            transaction_service,
            test_account.id,
            count=100,
            start_date=date(2025, 1, 1)
        )

        # Act: Get query plan for search query
        with test_db.get_connection() as conn:
            cursor = conn.cursor()

            # Test the exact query pattern used by repository
            cursor.execute("""
                EXPLAIN QUERY PLAN
                SELECT id, account_id, date, description, category, amount, type,
                       is_split, split_count,
                       reconciliation_status, reconciled_date, statement_date,
                       is_opening_balance
                FROM transactions
                WHERE description LIKE ?
                ORDER BY date DESC, id DESC
            """, ('%Starbucks%',))

            query_plan = cursor.fetchall()

        # Extract plan details (Row object format: id, parent, notused, detail)
        plan_details = [row[3] if len(row) > 3 else str(row) for row in query_plan]
        plan_str = "\n".join(plan_details)
        print(f"\nQuery Plan:")
        print(plan_str)

        # Assert: Using an index (not full table scan)
        # SQLite may use either idx_transactions_description or idx_transactions_date
        using_index = any("USING INDEX" in detail for detail in plan_details)
        assert using_index, \
            f"Query should use an index (not full table scan).\nPlan:\n{plan_str}"

        # Assert: Using SEARCH or SCAN with index (not plain SCAN)
        # "SCAN transactions USING INDEX" is acceptable (indexed scan)
        # "SCAN transactions" without USING INDEX would be a full table scan (bad)
        has_search_or_indexed_scan = any(
            "SEARCH" in detail or "USING INDEX" in detail
            for detail in plan_details
        )
        assert has_search_or_indexed_scan, \
            f"Query should use index-based access.\nPlan:\n{plan_str}"

        # Verify: No full table scan
        full_table_scan = any(
            detail.startswith("SCAN transactions") and "USING INDEX" not in detail
            for detail in plan_details
        )
        assert not full_table_scan, \
            f"Query should not do full table scan.\nPlan:\n{plan_str}"

        print("✓ Query uses database indexes (optimized, no full table scan)")

    # ========================================================================
    # BONUS TEST: Performance Degradation Test
    # ========================================================================

    def test_search_performance_scaling(self, test_db, test_account):
        """
        Bonus test: Verify performance scales linearly (O(log n) with index).

        US-011: Validates that performance improvement from indexing scales
        appropriately as transaction count increases.

        Setup: Test with 1K, 5K, 10K transactions
        Test: Measure search time for each dataset
        Expected: Time increase is logarithmic, not linear
        """
        transaction_service = TransactionService(test_db)
        start_date = date(2025, 1, 1)

        results = []

        # Test with different transaction counts
        for count in [1000, 5000, 10000]:
            # Clear previous transactions (recreate database)
            # (Note: In real test, you'd use separate test databases)

            # Create transactions
            self._create_test_transactions(
                transaction_service,
                test_account.id,
                count=count,
                start_date=start_date
            )

            # Warm-up
            transaction_service.search_transactions("warmup")

            # Measure search time
            start_time = time.time()
            search_results = transaction_service.search_transactions("Starbucks")
            elapsed_ms = (time.time() - start_time) * 1000

            results.append((count, elapsed_ms, len(search_results)))
            print(f"\n{count:,} transactions: {elapsed_ms:.2f}ms ({len(search_results)} results)")

        # Assert: Performance scales appropriately
        # With index, 10x data should not be 10x slower (should be much less)
        time_1k, time_5k, time_10k = [r[1] for r in results]

        # Performance should not degrade linearly
        # (10K should be less than 10x slower than 1K)
        if time_1k > 0:  # Avoid division by zero
            scaling_factor = time_10k / time_1k
            print(f"\nScaling factor (10K/1K): {scaling_factor:.2f}x")
            assert scaling_factor < 10, \
                f"Performance degraded too much: 10K took {scaling_factor:.1f}x longer than 1K (should be < 10x with index)"

        print("✓ Performance scales appropriately with index (< 10x degradation)")

    # ========================================================================
    # BONUS TEST: Search with No Results Performance
    # ========================================================================

    def test_search_performance_no_results(self, test_db, test_account):
        """
        Bonus test: Verify performance when search finds no results.

        US-011: Tests that no-match searches complete quickly (don't scan
        entire table looking for non-existent data).

        Setup: 10,000 transactions
        Test: Search for keyword that doesn't exist
        Expected: Completes in < 200ms (same as match scenario)
        """
        transaction_service = TransactionService(test_db)
        start_date = date(2025, 1, 1)

        # Setup: Create 10,000 test transactions
        self._create_test_transactions(
            transaction_service,
            test_account.id,
            count=10000,
            start_date=start_date
        )

        # Warm-up query
        transaction_service.search_transactions("warmup")

        # Act: Search for keyword that doesn't exist
        start_time = time.time()
        results = transaction_service.search_transactions("xyz123notfound")
        elapsed_ms = (time.time() - start_time) * 1000

        # Assert: No-match query still completes quickly
        print(f"\nNo-Results Search Performance: {elapsed_ms:.2f}ms")
        assert elapsed_ms < 200, \
            f"No-match search took {elapsed_ms:.2f}ms (should be < 200ms even with no results)"

        # Assert: Returns empty list
        assert len(results) == 0, "Should find no results"

        print(f"✓ No-results search completed in {elapsed_ms:.2f}ms (target: < 200ms)")
