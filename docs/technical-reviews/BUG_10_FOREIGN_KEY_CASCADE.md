# Bug #10: Account Deletion Fails with FOREIGN KEY Constraint

**Date:** November 10, 2025
**Severity:** 🚨 **CRITICAL (P0)** - Blocks account deletion
**Status:** ✅ **ROOT CAUSE IDENTIFIED**

---

## User Report

```
2025-11-10 20:11:34 - finance_app.ui.widgets.account_tree_widget - INFO - Delete account requested: 5
2025-11-10 20:11:38 - finance_app.data.database - ERROR - Database operation failed: FOREIGN KEY constraint failed
2025-11-10 20:11:38 - finance_app.ui.main_window - ERROR - Failed to delete account: Database operation failed: FOREIGN KEY constraint failed
```

User tried to delete account (ID 5) and got FOREIGN KEY constraint error.

---

## Root Cause Analysis

### The Problem

The `transactions` and `transaction_splits` tables have foreign key constraints referencing `accounts(id)` but **WITHOUT ON DELETE CASCADE**.

When you try to delete an account that has transactions, SQLite prevents the deletion because it would orphan the transaction records.

### Database Schema Analysis

**Tables with account_id foreign keys:**

1. ✅ **journal_entries** - `ON DELETE CASCADE` (GOOD)
   ```sql
   FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE
   ```

2. ✅ **reconciliations** - `ON DELETE CASCADE` (GOOD)
   ```sql
   FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
   ```

3. ✅ **balance_validation_log** - `ON DELETE SET NULL` (GOOD - logs should preserve history)
   ```sql
   FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE SET NULL
   ```

4. ❌ **transactions** - **NO CASCADE** (PROBLEM!)
   ```sql
   FOREIGN KEY (account_id) REFERENCES accounts (id)
   ```

5. ❌ **transaction_splits** - **NO CASCADE** (PROBLEM!)
   ```sql
   FOREIGN KEY (account_id) REFERENCES accounts(id)
   ```

### Why It Fails

1. User right-clicks account → "Delete Account"
2. Confirmation dialog → User clicks "Yes"
3. `account_service.delete_account(5)` is called
4. Repository executes: `DELETE FROM accounts WHERE id = 5`
5. SQLite checks foreign key constraints:
   - ❌ Found transaction records with `account_id = 5`
   - ❌ No CASCADE defined
   - ❌ Would orphan transaction records
6. **SQLite raises: FOREIGN KEY constraint failed**

---

## Why This Wasn't Caught Earlier

### Tests Were Incomplete

Looking at existing delete tests:
```python
# Most tests delete accounts with NO transactions
account = create_test_account()
service.delete_account(account.id)  # ✅ Works (no transactions)
```

**Missing test case:**
```python
# This test doesn't exist!
account = create_test_account()
create_test_transaction(account.id)  # Add transaction
service.delete_account(account.id)  # ❌ FAILS with FK error
```

### Migration Gap

The original `transactions` table was created BEFORE we established CASCADE DELETE policies in later migrations (like 002_create_journal_entries.sql which DOES have CASCADE).

---

## Solution Options

### Option 1: Fix Schema with Migration (PROPER but RISKY)

Create migration to add CASCADE DELETE to foreign keys.

**Pros:**
- Proper database design
- Consistent with other tables
- Automatic cleanup

**Cons:**
- SQLite doesn't support `ALTER TABLE` for foreign keys
- Must recreate entire `transactions` and `transaction_splits` tables
- Risky data migration
- Could corrupt data if not careful

**Implementation:**
```sql
-- Migration: 013_fix_cascade_delete.sql

-- 1. Create new transactions table WITH CASCADE
CREATE TABLE transactions_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    -- ... all other columns ...
    FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE
);

-- 2. Copy data
INSERT INTO transactions_new SELECT * FROM transactions;

-- 3. Drop old table
DROP TABLE transactions;

-- 4. Rename new table
ALTER TABLE transactions_new RENAME TO transactions;

-- 5. Recreate indexes
-- ... recreate all indexes ...

-- Repeat for transaction_splits
```

**Risk Assessment:** MEDIUM-HIGH
- If anything goes wrong, could lose all transaction data
- Complex migration with many steps
- Need comprehensive rollback plan

### Option 2: Manual Cleanup in delete_account() (SAFE and QUICK)

Modify `delete_account()` method to manually delete related records first.

**Pros:**
- Safe - no schema changes
- Quick to implement (15 minutes)
- Easy to test
- Easy to rollback
- No risk to existing data

**Cons:**
- Not "proper" database design
- Cleanup logic in application layer instead of database layer
- Must maintain manually

**Implementation:**
```python
def delete_account(self, account_id: int) -> bool:
    """Delete account and all related data."""
    try:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Step 1: Delete related transactions (will cascade to splits)
            cursor.execute("DELETE FROM transactions WHERE account_id = ?", (account_id,))
            deleted_txns = cursor.rowcount

            # Step 2: Delete journal entries (should have CASCADE, but be explicit)
            cursor.execute("DELETE FROM journal_entries WHERE account_id = ?", (account_id,))
            deleted_entries = cursor.rowcount

            # Step 3: Delete reconciliations (should have CASCADE, but be explicit)
            cursor.execute("DELETE FROM reconciliations WHERE account_id = ?", (account_id,))
            deleted_recons = cursor.rowcount

            # Step 4: Now safe to delete account
            cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            deleted = cursor.rowcount > 0

            if deleted:
                logger.info(
                    f"Deleted account ID {account_id} with {deleted_txns} transactions, "
                    f"{deleted_entries} journal entries, {deleted_recons} reconciliations"
                )

            return deleted

    except sqlite3.Error as e:
        logger.error(f"Failed to delete account {account_id}: {e}")
        raise DatabaseError(f"Failed to delete account: {e}") from e
```

**Risk Assessment:** LOW
- No schema changes
- Explicit control over deletion order
- Can add logging/auditing
- Easy to test

### Option 3: Check Before Delete (USER-FRIENDLY)

Check if account has transactions and warn user before deleting.

**Pros:**
- Gives user control
- Prevents accidental data loss
- Can offer export/backup before deletion

**Cons:**
- More clicks for user
- Still need Option 2 to actually delete

**Implementation:**
```python
def delete_account(self, account_id: int):
    """Delete account with user confirmation if has transactions."""
    # Check if has transactions
    txn_count = self.get_transaction_count(account_id)

    if txn_count > 0:
        reply = QMessageBox.warning(
            self,
            "Account Has Transactions",
            f"This account has {txn_count} transactions.\n\n"
            f"Deleting the account will PERMANENTLY DELETE all transactions!\n\n"
            f"Are you SURE you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

    # Proceed with deletion (using Option 2)
    self.account_service.delete_account(account_id)
```

---

## Recommended Solution

**IMPLEMENT: Option 2 + Option 3**

1. **Fix `account_repository.delete()` to manually delete related records** (Option 2)
   - Safe, quick, low-risk
   - No schema changes required
   - Can implement immediately

2. **Enhance UI confirmation dialog** (Option 3)
   - Show transaction count to user
   - Make consequences clear
   - Give user explicit warning

3. **DEFER: Schema fix (Option 1) to Sprint 13**
   - Proper long-term solution
   - Requires careful planning
   - Need comprehensive testing
   - Can be done when we have time for thorough QA

---

## Implementation Plan

### Immediate Fix (15 minutes)

1. ✅ Modify `account_repository.delete()` method
2. ✅ Add explicit DELETE statements for related records
3. ✅ Add logging for deleted records
4. ✅ Test deletion with transactions

### Short-Term Enhancement (20 minutes)

5. ✅ Modify UI `delete_account()` method
6. ✅ Add transaction count check
7. ✅ Enhance warning message
8. ✅ Test UI workflow

### Testing (20 minutes)

9. ✅ Add test: `test_delete_account_with_transactions()`
10. ✅ Add test: `test_delete_account_with_splits()`
11. ✅ Add test: `test_delete_account_with_reconciliations()`
12. ✅ Manual test: Delete account with real data

### Documentation (10 minutes)

13. ✅ Update this bug report with fix details
14. ✅ Add TODO for schema fix in Sprint 13
15. ✅ Document in CHANGELOG

**Total Time:** ~65 minutes

---

## Expected Behavior After Fix

### User Action: Delete Account with 5 Transactions

**Step 1:** Right-click account → "Delete Account"

**Step 2:** Warning dialog:
```
This account has 5 transactions.

Deleting the account will PERMANENTLY DELETE all transactions!

Are you SURE you want to continue?

[No] [Yes]
```

**Step 3:** User clicks "Yes"

**Step 4:** Backend deletes in order:
1. 5 transactions deleted
2. 10 journal entries deleted (2 per transaction)
3. 0 reconciliations deleted
4. Account deleted

**Step 5:** Success message: "Account 'Checking' deleted"

**Step 6:** UI refreshes, account gone from tree

---

## Test Cases to Add

```python
def test_delete_account_with_transactions(self):
    """Test deleting account that has transactions."""
    account = self.service.create_account("Test", AccountType.ASSET)
    # Create 3 transactions
    for i in range(3):
        txn = self.transaction_service.create_transaction(
            account.id, date.today(), f"Transaction {i}", 100.0, TransactionType.INCOME
        )

    # Should delete account AND all 3 transactions
    self.service.delete_account(account.id)

    # Verify account deleted
    assert self.service.get_account(account.id) is None

    # Verify transactions deleted
    txns = self.transaction_service.get_transactions_by_account(account.id)
    assert len(txns) == 0

    # Verify journal entries deleted
    entries = self.journal_service.get_entries_by_account(account.id)
    assert len(entries) == 0


def test_delete_account_with_reconciliations(self):
    """Test deleting account that has reconciliation history."""
    account = self.service.create_account("Test", AccountType.ASSET)

    # Create reconciliation
    recon = self.reconciliation_service.start_reconciliation(
        account.id, date.today(), 1000.0
    )

    # Should delete account AND reconciliation
    self.service.delete_account(account.id)

    # Verify both deleted
    assert self.service.get_account(account.id) is None
    assert self.reconciliation_service.get_reconciliation(recon.id) is None


def test_delete_account_preserves_validation_log(self):
    """Test that validation logs are preserved (SET NULL behavior)."""
    account = self.service.create_account("Test", AccountType.ASSET)

    # Create validation log entry
    self.validation_service.validate_account(account.id)

    # Delete account
    self.service.delete_account(account.id)

    # Validation log should still exist with account_id = NULL
    logs = self.validation_service.get_validation_logs()
    assert len(logs) > 0
    assert logs[0].account_id is None  # SET NULL behavior
```

---

## Status

**Current:** ✅ ROOT CAUSE IDENTIFIED
**Next:** Implement Option 2 + Option 3
**Timeline:** 65 minutes to complete fix + tests
**Priority:** CRITICAL - Blocking users from deleting accounts

---

**Tech Lead Sign-off:** Ready to implement fix

**Date:** November 10, 2025
