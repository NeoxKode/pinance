"""
Performance tests for journal entry system.

Tests the system with large volumes of journal entries to ensure:
- Insert performance
- Query performance
- Balance calculation performance
- Index effectiveness

Story: US-002A - Journal Entry Foundation
"""
import pytest
import time
from decimal import Decimal
from datetime import datetime, timedelta

from finance_app.data.database import Database
from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.business.transaction_service import TransactionService
from finance_app.business.double_entry_service import DoubleEntryService


class TestJournalPerformance:
    """Performance tests for journal entry system."""

    @pytest.fixture
    def account(self, test_db):
        """Create a test account."""
        account_repo = AccountRepository(test_db)
        account = Account(
            id=None,
            name="Performance Test Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT
        )
        return account_repo.create(account)

    def test_create_10k_journal_entries(self, test_db, account):
        """Test creating 10,000 journal entries."""
        transaction_service = TransactionService(test_db)
        journal_repo = JournalEntryRepository(test_db)

        num_entries = 10_000
        start_date = datetime(2025, 1, 1)

        print(f"\nCreating {num_entries:,} journal entries...")
        start_time = time.time()

        # Create entries
        for i in range(num_entries):
            # Alternate between income and expense
            is_income = i % 2 == 0
            amount = Decimal("100.00") if is_income else Decimal("50.00")
            trans_type = "income" if is_income else "expense"

            # Spread transactions over 365 days
            date = start_date + timedelta(days=i % 365)

            transaction_service.create_transaction(
                account_id=account.id,
                date=date.strftime("%Y-%m-%d"),
                description=f"Transaction {i+1}",
                category="Performance Test",
                amount=str(amount),
                trans_type=trans_type
            )

        end_time = time.time()
        elapsed = end_time - start_time

        # Verify count
        entries = journal_repo.get_by_account(account.id)
        assert len(entries) == num_entries

        # Performance metrics
        entries_per_second = num_entries / elapsed
        print(f"Created {num_entries:,} entries in {elapsed:.2f}s")
        print(f"Performance: {entries_per_second:.1f} entries/second")
        print(f"Average: {(elapsed/num_entries)*1000:.2f}ms per entry")

        # Performance assertion: should create at least 100 entries/second
        assert entries_per_second > 100, f"Too slow: {entries_per_second:.1f} entries/s"

    def test_query_performance_with_10k_entries(self, test_db, account):
        """Test query performance with 10,000 journal entries."""
        transaction_service = TransactionService(test_db)
        journal_repo = JournalEntryRepository(test_db)

        # Create 10k entries first
        num_entries = 10_000
        start_date = datetime(2025, 1, 1)

        print(f"\nSetting up {num_entries:,} entries for query testing...")
        for i in range(num_entries):
            is_income = i % 2 == 0
            amount = Decimal("100.00") if is_income else Decimal("50.00")
            trans_type = "income" if is_income else "expense"
            date = start_date + timedelta(days=i % 365)

            transaction_service.create_transaction(
                account_id=account.id,
                date=date.strftime("%Y-%m-%d"),
                description=f"Transaction {i+1}",
                category="Performance Test",
                amount=str(amount),
                trans_type=trans_type
            )

        # Test: Get all entries for account
        print("\nTest 1: Get all entries by account...")
        start_time = time.time()
        entries = journal_repo.get_by_account(account.id)
        elapsed = time.time() - start_time
        print(f"Retrieved {len(entries):,} entries in {elapsed*1000:.2f}ms")
        assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s"

        # Test: Get entries with limit
        print("\nTest 2: Get recent 100 entries...")
        start_time = time.time()
        recent_entries = journal_repo.get_by_account(account.id, limit=100)
        elapsed = time.time() - start_time
        print(f"Retrieved {len(recent_entries)} entries in {elapsed*1000:.2f}ms")
        assert len(recent_entries) == 100
        assert elapsed < 0.1, f"Too slow: {elapsed:.3f}s"

        # Test: Get entries by date range
        print("\nTest 3: Get entries for date range (30 days)...")
        start_date_str = "2025-01-01"
        end_date_str = "2025-01-30"
        start_time = time.time()
        range_entries = journal_repo.get_by_date_range(
            account.id, start_date_str, end_date_str
        )
        elapsed = time.time() - start_time
        print(f"Retrieved {len(range_entries)} entries in {elapsed*1000:.2f}ms")
        assert elapsed < 0.5, f"Too slow: {elapsed:.3f}s"

    def test_balance_calculation_performance_with_10k_entries(self, test_db, account):
        """Test balance calculation performance with 10,000 entries."""
        transaction_service = TransactionService(test_db)
        journal_repo = JournalEntryRepository(test_db)

        # Create 10k entries
        num_entries = 10_000
        start_date = datetime(2025, 1, 1)

        print(f"\nSetting up {num_entries:,} entries for balance calculation...")
        expected_balance = Decimal("0.00")
        for i in range(num_entries):
            is_income = i % 2 == 0
            amount = Decimal("100.00") if is_income else Decimal("50.00")
            trans_type = "income" if is_income else "expense"
            date = start_date + timedelta(days=i % 365)

            # Track expected balance
            if is_income:
                expected_balance += amount
            else:
                expected_balance -= amount

            transaction_service.create_transaction(
                account_id=account.id,
                date=date.strftime("%Y-%m-%d"),
                description=f"Transaction {i+1}",
                category="Performance Test",
                amount=str(amount),
                trans_type=trans_type
            )

        # Test: Calculate balance from journal
        print("\nCalculating balance from journal entries...")
        start_time = time.time()
        calculated_balance = journal_repo.get_account_balance(account.id)
        elapsed = time.time() - start_time

        print(f"Calculated balance in {elapsed*1000:.2f}ms")
        print(f"Balance: ${calculated_balance}")
        assert calculated_balance == expected_balance
        assert elapsed < 0.5, f"Too slow: {elapsed:.3f}s"

    def test_concurrent_transaction_performance(self, test_db, account):
        """Test performance under simulated concurrent load."""
        transaction_service = TransactionService(test_db)
        account_repo = AccountRepository(test_db)

        num_batches = 100
        batch_size = 100
        total_transactions = num_batches * batch_size

        print(f"\nCreating {total_transactions:,} transactions in {num_batches} batches...")
        start_time = time.time()

        for batch in range(num_batches):
            for i in range(batch_size):
                is_income = i % 2 == 0
                amount = Decimal("10.00")
                trans_type = "income" if is_income else "expense"
                date = datetime(2025, 1, 1) + timedelta(days=batch)

                transaction_service.create_transaction(
                    account_id=account.id,
                    date=date.strftime("%Y-%m-%d"),
                    description=f"Batch {batch} Transaction {i}",
                    category="Test",
                    amount=str(amount),
                    trans_type=trans_type
                )

        end_time = time.time()
        elapsed = end_time - start_time
        tps = total_transactions / elapsed

        print(f"Created {total_transactions:,} transactions in {elapsed:.2f}s")
        print(f"Throughput: {tps:.1f} transactions/second")

        # Verify final balance is correct
        final_account = account_repo.get_by_id(account.id)
        # 100 batches * 100 transactions * 50% income/expense * $10 = $0 net
        assert final_account.balance == Decimal("0.00")

        # Should handle at least 100 transactions per second
        assert tps > 100, f"Too slow: {tps:.1f} transactions/s"

    def test_index_effectiveness(self, test_db, account):
        """Test that database indices are effective."""
        transaction_service = TransactionService(test_db)
        journal_repo = JournalEntryRepository(test_db)

        # Create 5k entries
        num_entries = 5_000
        start_date = datetime(2025, 1, 1)

        print(f"\nSetting up {num_entries:,} entries for index testing...")
        for i in range(num_entries):
            is_income = i % 2 == 0
            amount = Decimal("100.00") if is_income else Decimal("50.00")
            trans_type = "income" if is_income else "expense"
            date = start_date + timedelta(days=i % 365)

            transaction_service.create_transaction(
                account_id=account.id,
                date=date.strftime("%Y-%m-%d"),
                description=f"Transaction {i+1}",
                category="Performance Test",
                amount=str(amount),
                trans_type=trans_type
            )

        # Test: Query by account_id (should use idx_je_account_date)
        print("\nTest: Query by account_id (indexed)...")
        start_time = time.time()
        entries = journal_repo.get_by_account(account.id, limit=1000)
        elapsed = time.time() - start_time
        print(f"Retrieved {len(entries)} entries in {elapsed*1000:.2f}ms")
        assert elapsed < 0.1, f"Index not effective: {elapsed:.3f}s"

        # Test: Query by transaction_id (should use idx_je_transaction)
        print("\nTest: Query by transaction_id (indexed)...")
        entries_list = journal_repo.get_by_account(account.id, limit=1)
        if entries_list:
            test_txn_id = entries_list[0].transaction_id
            start_time = time.time()
            entry = journal_repo.get_by_transaction(test_txn_id)
            elapsed = time.time() - start_time
            print(f"Retrieved entry by transaction_id in {elapsed*1000:.2f}ms")
            assert elapsed < 0.01, f"Index not effective: {elapsed:.3f}s"

        # Test: Query by date range (should use idx_je_date)
        print("\nTest: Query by date range (indexed)...")
        start_time = time.time()
        range_entries = journal_repo.get_by_date_range(account.id, "2025-01-01", "2025-01-31")
        elapsed = time.time() - start_time
        print(f"Retrieved {len(range_entries)} entries in {elapsed*1000:.2f}ms")
        assert elapsed < 0.1, f"Index not effective: {elapsed:.3f}s"

    def test_memory_usage_with_large_dataset(self, test_db, account):
        """Test that large datasets don't cause memory issues."""
        import sys
        transaction_service = TransactionService(test_db)
        journal_repo = JournalEntryRepository(test_db)

        num_entries = 5_000
        start_date = datetime(2025, 1, 1)

        print(f"\nCreating {num_entries:,} entries for memory test...")
        for i in range(num_entries):
            is_income = i % 2 == 0
            amount = Decimal("100.00") if is_income else Decimal("50.00")
            trans_type = "income" if is_income else "expense"
            date = start_date + timedelta(days=i % 365)

            transaction_service.create_transaction(
                account_id=account.id,
                date=date.strftime("%Y-%m-%d"),
                description=f"Transaction {i+1}",
                category="Performance Test",
                amount=str(amount),
                trans_type=trans_type
            )

        # Get entries and check memory usage
        print("\nRetrieving all entries...")
        entries = journal_repo.get_by_account(account.id)

        # Calculate approximate memory usage
        entry_size = sys.getsizeof(entries[0]) if entries else 0
        total_size_mb = (len(entries) * entry_size) / (1024 * 1024)

        print(f"Retrieved {len(entries):,} entries")
        print(f"Approximate memory usage: {total_size_mb:.2f} MB")

        # Should be reasonable memory usage (< 50 MB for 5k entries)
        assert total_size_mb < 50, f"Excessive memory usage: {total_size_mb:.2f} MB"
