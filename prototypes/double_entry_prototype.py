#!/usr/bin/env python3
"""
Double-Entry Accounting Prototype
Time-boxed: 8 hours
Goal: Validate double-entry approach before full implementation

Run with: python prototypes/double_entry_prototype.py
"""

import sqlite3
import os
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional


@dataclass
class JournalEntryPrototype:
    """Minimal journal entry for prototype."""
    id: Optional[int]
    account_id: int
    entry_date: str
    description: str
    debit_amount: Decimal
    credit_amount: Decimal
    balance_after: Optional[Decimal] = None
    entry_type: str = 'transaction'

    @property
    def amount(self) -> Decimal:
        """Net amount (debit - credit)."""
        return self.debit_amount - self.credit_amount

    def validate(self):
        """Validate entry."""
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValueError("Cannot have both debit and credit")
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValueError("Must have either debit or credit")
        if self.debit_amount < 0 or self.credit_amount < 0:
            raise ValueError("Amounts cannot be negative")


class DoubleEntryPrototype:
    """Prototype double-entry system."""

    def __init__(self, db_path: str = "prototype.db"):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        """Create prototype tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    balance REAL DEFAULT 0.0
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS journal_entries_prototype (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    entry_date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    debit_amount REAL NOT NULL DEFAULT 0.0,
                    credit_amount REAL NOT NULL DEFAULT 0.0,
                    balance_after REAL,
                    entry_type TEXT DEFAULT 'transaction',
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            """)

            # Create trigger
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS update_balance_prototype
                AFTER INSERT ON journal_entries_prototype
                BEGIN
                    UPDATE accounts
                    SET balance = balance + (NEW.debit_amount - NEW.credit_amount)
                    WHERE id = NEW.account_id;
                END
            """)

            conn.commit()

    def create_account(self, name: str, initial_balance: float = 0.0) -> int:
        """Create a test account."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO accounts (name, balance) VALUES (?, ?)",
                (name, initial_balance)
            )
            return cursor.lastrowid

    def create_entry(self, entry: JournalEntryPrototype) -> JournalEntryPrototype:
        """Create a journal entry."""
        entry.validate()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO journal_entries_prototype
                (account_id, entry_date, description, debit_amount, credit_amount, entry_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                entry.account_id,
                entry.entry_date,
                entry.description,
                float(entry.debit_amount),
                float(entry.credit_amount),
                entry.entry_type
            ))
            entry.id = cursor.lastrowid
            conn.commit()

        return entry

    def create_balanced_transaction(self, entries: List[JournalEntryPrototype]):
        """Create multiple balanced entries atomically."""
        # Validate balance
        total_debits = sum(e.debit_amount for e in entries)
        total_credits = sum(e.credit_amount for e in entries)

        if abs(total_debits - total_credits) > Decimal('0.01'):
            raise ValueError(
                f"Unbalanced transaction: "
                f"Debits={total_debits}, Credits={total_credits}"
            )

        # Create all entries in transaction
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("BEGIN TRANSACTION")
            try:
                for entry in entries:
                    entry.validate()
                    conn.execute("""
                        INSERT INTO journal_entries_prototype
                        (account_id, entry_date, description, debit_amount, credit_amount)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        entry.account_id,
                        entry.entry_date,
                        entry.description,
                        float(entry.debit_amount),
                        float(entry.credit_amount)
                    ))
                conn.commit()
                print(f"✅ Created balanced transaction with {len(entries)} entries")
            except Exception as e:
                conn.rollback()
                print(f"❌ Transaction failed: {e}")
                raise

    def get_account_balance(self, account_id: int) -> Decimal:
        """Get account balance from table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT balance FROM accounts WHERE id = ?",
                (account_id,)
            )
            row = cursor.fetchone()
            return Decimal(str(row[0])) if row else Decimal('0')

    def calculate_balance_from_entries(self, account_id: int) -> Decimal:
        """Calculate balance from journal entries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT SUM(debit_amount - credit_amount)
                FROM journal_entries_prototype
                WHERE account_id = ?
            """, (account_id,))
            row = cursor.fetchone()
            return Decimal(str(row[0])) if row and row[0] else Decimal('0')

    def validate_balance(self, account_id: int) -> dict:
        """Validate cached balance matches calculated balance."""
        cached = self.get_account_balance(account_id)
        calculated = self.calculate_balance_from_entries(account_id)
        difference = abs(cached - calculated)

        return {
            'account_id': account_id,
            'cached_balance': cached,
            'calculated_balance': calculated,
            'difference': difference,
            'is_valid': difference < Decimal('0.01')
        }

    def get_trial_balance(self) -> dict:
        """Get trial balance (total debits and credits)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT
                    SUM(debit_amount) as total_debits,
                    SUM(credit_amount) as total_credits
                FROM journal_entries_prototype
            """)
            row = cursor.fetchone()

            total_debits = Decimal(str(row[0])) if row[0] else Decimal('0')
            total_credits = Decimal(str(row[1])) if row[1] else Decimal('0')
            difference = abs(total_debits - total_credits)

            return {
                'total_debits': total_debits,
                'total_credits': total_credits,
                'difference': difference,
                'is_balanced': difference < Decimal('0.01')
            }


def run_prototype_tests():
    """Run prototype validation tests."""
    print("=" * 60)
    print("DOUBLE-ENTRY ACCOUNTING PROTOTYPE")
    print("=" * 60)

    proto = DoubleEntryPrototype()

    # Test 1: Create accounts
    print("\n📝 Test 1: Creating test accounts...")
    checking_id = proto.create_account("Checking", 0.0)
    income_id = proto.create_account("Salary Income", 0.0)
    expense_id = proto.create_account("Groceries Expense", 0.0)
    print(f"✅ Created accounts: Checking={checking_id}, Income={income_id}, Expense={expense_id}")

    # Test 2: Income transaction (Salary deposit)
    print("\n📝 Test 2: Creating income transaction (Salary $5,000)...")
    income_entries = [
        JournalEntryPrototype(
            id=None,
            account_id=checking_id,
            entry_date="2025-10-22",
            description="Salary deposit",
            debit_amount=Decimal("5000.00"),  # Debit checking (increase asset)
            credit_amount=Decimal("0")
        ),
        JournalEntryPrototype(
            id=None,
            account_id=income_id,
            entry_date="2025-10-22",
            description="Salary deposit",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("5000.00")  # Credit income (increase income)
        )
    ]
    proto.create_balanced_transaction(income_entries)

    # Validate balances
    checking_balance = proto.get_account_balance(checking_id)
    print(f"   Checking balance: ${checking_balance}")
    assert checking_balance == Decimal("5000.00"), "Checking should have $5,000"

    # Test 3: Expense transaction (Groceries)
    print("\n📝 Test 3: Creating expense transaction (Groceries $150)...")
    expense_entries = [
        JournalEntryPrototype(
            id=None,
            account_id=expense_id,
            entry_date="2025-10-22",
            description="Grocery shopping",
            debit_amount=Decimal("150.00"),  # Debit expense (increase expense)
            credit_amount=Decimal("0")
        ),
        JournalEntryPrototype(
            id=None,
            account_id=checking_id,
            entry_date="2025-10-22",
            description="Grocery shopping",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("150.00")  # Credit checking (decrease asset)
        )
    ]
    proto.create_balanced_transaction(expense_entries)

    # Validate balances
    checking_balance = proto.get_account_balance(checking_id)
    expense_balance = proto.get_account_balance(expense_id)
    print(f"   Checking balance: ${checking_balance}")
    print(f"   Expense balance: ${expense_balance}")
    assert checking_balance == Decimal("4850.00"), "Checking should have $4,850"
    assert expense_balance == Decimal("150.00"), "Expense should have $150"

    # Test 4: Balance validation
    print("\n📝 Test 4: Validating account balances...")
    for account_id in [checking_id, income_id, expense_id]:
        result = proto.validate_balance(account_id)
        status = "✅" if result['is_valid'] else "❌"
        print(f"   {status} Account {account_id}: "
              f"Cached={result['cached_balance']}, "
              f"Calculated={result['calculated_balance']}, "
              f"Diff={result['difference']}")
        assert result['is_valid'], f"Balance validation failed for account {account_id}"

    # Test 5: Trial balance
    print("\n📝 Test 5: Checking trial balance...")
    trial_balance = proto.get_trial_balance()
    print(f"   Total Debits:  ${trial_balance['total_debits']}")
    print(f"   Total Credits: ${trial_balance['total_credits']}")
    print(f"   Difference:    ${trial_balance['difference']}")
    status = "✅ BALANCED" if trial_balance['is_balanced'] else "❌ UNBALANCED"
    print(f"   Status: {status}")
    assert trial_balance['is_balanced'], "Trial balance should be balanced"

    # Test 6: Unbalanced transaction (should fail)
    print("\n📝 Test 6: Testing unbalanced transaction rejection...")
    unbalanced_entries = [
        JournalEntryPrototype(
            id=None,
            account_id=checking_id,
            entry_date="2025-10-22",
            description="Unbalanced",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0")
        ),
        JournalEntryPrototype(
            id=None,
            account_id=expense_id,
            entry_date="2025-10-22",
            description="Unbalanced",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("50.00")  # Only $50 credit (unbalanced!)
        )
    ]
    try:
        proto.create_balanced_transaction(unbalanced_entries)
        print("   ❌ FAIL: Should have rejected unbalanced transaction")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"   ✅ Correctly rejected: {e}")

    # Test 7: Performance test
    print("\n📝 Test 7: Performance testing with 1,000 entries...")
    import time

    test_account_id = proto.create_account("Performance Test", 0.0)
    start_time = time.time()

    for i in range(1000):
        entry = JournalEntryPrototype(
            id=None,
            account_id=test_account_id,
            entry_date="2025-10-22",
            description=f"Entry {i}",
            debit_amount=Decimal("10.00"),
            credit_amount=Decimal("0")
        )
        proto.create_entry(entry)

    elapsed = time.time() - start_time
    avg_time = (elapsed / 1000) * 1000  # Convert to ms
    print(f"   Created 1,000 entries in {elapsed:.2f}s ({avg_time:.2f}ms per entry)")

    # Query performance
    start_time = time.time()
    balance = proto.calculate_balance_from_entries(test_account_id)
    query_time = (time.time() - start_time) * 1000  # Convert to ms
    print(f"   Balance query took {query_time:.2f}ms")
    print(f"   Final balance: ${balance}")

    assert balance == Decimal("10000.00"), "Should have $10,000"
    assert query_time < 500, f"Query too slow: {query_time}ms"

    print("\n" + "=" * 60)
    print("✅ ALL PROTOTYPE TESTS PASSED")
    print("=" * 60)
    print("\n📊 RECOMMENDATION: Proceed with full implementation")
    print("   - Double-entry logic works correctly")
    print("   - Balance validation is accurate")
    print("   - Performance is acceptable")
    print("   - Database triggers work as expected")
    print("\n📝 Next Steps:")
    print("   1. Document results in docs/spikes/SPIKE-001-RESULTS.md")
    print("   2. Start US-001: Account Type Taxonomy")
    print("   3. Proceed with Epic 1 implementation")


if __name__ == "__main__":
    # Clean up old prototype database
    if os.path.exists("prototype.db"):
        os.remove("prototype.db")
        print("🗑️  Cleaned up old prototype.db\n")

    try:
        run_prototype_tests()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("\n📊 RECOMMENDATION: NO-GO - Fix issues and re-run")
        exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print("\n📊 RECOMMENDATION: NO-GO - Investigate and redesign")
        exit(1)
