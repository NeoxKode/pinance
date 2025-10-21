# SPIKE-001: Double-Entry Accounting Prototype

**Spike ID:** SPIKE-001
**Type:** Technical Validation
**Status:** 📋 Ready
**Time-Box:** 1 day (8 hours)
**Sprint:** Pre-Sprint 1
**Owner:** Development Team
**Created:** October 22, 2025

---

## 🎯 Spike Goal

**Validate that our double-entry accounting approach works correctly before committing 2-3 weeks to full implementation.**

### Success Criteria
- ✅ Can create journal entries that balance (debits = credits)
- ✅ Account balances update correctly from journal entries
- ✅ Balance calculation matches cached balance
- ✅ Database triggers work as expected
- ✅ Performance is acceptable (< 100ms for basic operations)

### Fail Criteria
- ❌ Cannot maintain balanced entries
- ❌ Balance calculations don't match
- ❌ Performance is too slow (> 500ms)
- ❌ Database design is fundamentally flawed

---

## 📋 Spike Tasks

### Hour 1-2: Database Schema Prototype
**Goal:** Create minimal journal_entries table and triggers

**Tasks:**
1. Create `journal_entries_prototype` table
2. Create balance update trigger
3. Insert sample journal entries manually
4. Verify triggers update account balance correctly

**Deliverable:** Working database schema with triggers

---

### Hour 3-4: Python Model & Repository
**Goal:** Create basic Python classes to interact with journal entries

**Tasks:**
1. Create `JournalEntry` dataclass
2. Create basic `JournalEntryRepository`
3. Write `create()` and `get_by_account()` methods
4. Test creating entries programmatically

**Deliverable:** Python code that can create journal entries

---

### Hour 5-6: Accounting Logic Validation
**Goal:** Prove the accounting equation works

**Tasks:**
1. Create sample accounts (Checking, Income, Expense)
2. Create balanced transaction (Income → Checking)
3. Create balanced transaction (Checking → Expense)
4. Verify all balances are correct
5. Calculate trial balance (total debits = total credits)

**Deliverable:** Proof that accounting logic works

---

### Hour 7-8: Performance Testing & Decision
**Goal:** Test with realistic data volume

**Tasks:**
1. Create 1,000 journal entries
2. Query account balance from entries
3. Measure query performance
4. Test balance validation with 1,000 entries
5. Document findings and make go/no-go decision

**Deliverable:** Performance metrics and recommendation

---

## 🔧 Prototype Code

### Database Schema (Minimal)

```sql
-- File: prototypes/double_entry_prototype.sql

-- Minimal journal entries table
CREATE TABLE journal_entries_prototype (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    entry_date TEXT NOT NULL,
    description TEXT NOT NULL,
    debit_amount REAL NOT NULL DEFAULT 0.0,
    credit_amount REAL NOT NULL DEFAULT 0.0,
    balance_after REAL,
    entry_type TEXT DEFAULT 'transaction',
    FOREIGN KEY (account_id) REFERENCES accounts (id)
);

-- Trigger to update account balance
CREATE TRIGGER update_balance_prototype
AFTER INSERT ON journal_entries_prototype
BEGIN
    UPDATE accounts
    SET balance = balance + (NEW.debit_amount - NEW.credit_amount)
    WHERE id = NEW.account_id;
END;

-- Validation trigger
CREATE TRIGGER validate_entry_prototype
BEFORE INSERT ON journal_entries_prototype
BEGIN
    SELECT CASE
        WHEN NEW.debit_amount > 0 AND NEW.credit_amount > 0 THEN
            RAISE(ABORT, 'Cannot have both debit and credit')
        WHEN NEW.debit_amount = 0 AND NEW.credit_amount = 0 THEN
            RAISE(ABORT, 'Must have debit or credit')
    END;
END;
```

### Python Prototype Code

```python
# File: prototypes/double_entry_prototype.py
"""
Prototype for double-entry accounting system.
Time-boxed: 8 hours
"""

import sqlite3
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from datetime import datetime


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
            account_id=checking_id,
            entry_date="2025-10-22",
            description="Unbalanced",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0")
        ),
        JournalEntryPrototype(
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


if __name__ == "__main__":
    import os
    # Clean up old prototype database
    if os.path.exists("prototype.db"):
        os.remove("prototype.db")

    run_prototype_tests()
```

---

## 📊 Expected Results

### Successful Prototype Should Show:

1. **Functional Requirements:**
   - ✅ Can create balanced journal entries
   - ✅ Account balances update automatically via triggers
   - ✅ Cached balance matches calculated balance (100% accuracy)
   - ✅ Trial balance is balanced (total debits = total credits)
   - ✅ Unbalanced transactions are rejected

2. **Performance Requirements:**
   - ✅ Single entry creation: < 10ms
   - ✅ Balance query with 1,000 entries: < 100ms
   - ✅ Batch create 1,000 entries: < 5 seconds

3. **Data Integrity:**
   - ✅ No balance discrepancies
   - ✅ Database triggers prevent invalid entries
   - ✅ Atomic transactions work correctly

---

## 🎯 Decision Points

After completing the prototype, decide:

### ✅ GO - Proceed with Full Implementation
**If:**
- All tests pass
- Performance is acceptable
- No fundamental design flaws discovered
- Team confidence is high

**Next Steps:**
1. Start US-001 (Account Type Taxonomy)
2. Proceed with Epic 1 implementation
3. Use prototype code as reference

### ❌ NO-GO - Redesign Approach
**If:**
- Tests fail
- Performance is too slow
- Design flaws discovered
- Complexity is too high

**Next Steps:**
1. Document issues found
2. Research alternative approaches
3. Redesign database schema
4. Run another spike

### ⚠️ MAYBE - More Investigation Needed
**If:**
- Some tests fail but fixable
- Performance borderline
- Minor design issues

**Next Steps:**
1. Extend spike by 4 hours
2. Fix identified issues
3. Re-run tests
4. Make final decision

---

## 📋 Spike Deliverables

1. **prototype.db** - Working SQLite database with sample data
2. **double_entry_prototype.py** - Python prototype code
3. **SPIKE-001-RESULTS.md** - Results document with:
   - Test results (pass/fail)
   - Performance metrics
   - Issues discovered
   - Recommendation (GO/NO-GO/MAYBE)
   - Lessons learned

---

## ⏱️ Time Tracking

| Task | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| Database schema | 2h | | |
| Python models | 2h | | |
| Accounting logic | 2h | | |
| Performance testing | 2h | | |
| **Total** | **8h** | | |

---

## 📝 Notes

- Keep code simple - this is a prototype, not production
- Focus on proving concepts, not perfection
- Document all findings, especially failures
- Be honest about what works and what doesn't
- Time-box strictly - don't exceed 8 hours

---

**Spike Created:** October 22, 2025
**Spike Started:** TBD
**Spike Completed:** TBD
**Recommendation:** TBD
