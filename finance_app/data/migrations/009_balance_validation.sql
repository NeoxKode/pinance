-- Migration 009: Account Balance Validation & Integrity (US-010)
-- Dependencies: Migration 002 (journal_entries table), Migration 001 (accounts table)
--
-- This migration implements automatic balance validation and integrity checks
-- for double-entry accounting. It creates database triggers to automatically
-- update account balances when journal entries are created, updated, or deleted.
--
-- Business Rules:
--   BR-001: Account balance = SUM(debit_amount - credit_amount) for all journal entries
--   BR-002: Triggers update accounts.balance automatically
--   BR-003: Validation log maintains audit trail of all validations

-- ============================================================================
-- PART 1: Database Triggers for Automatic Balance Updates
-- ============================================================================

-- Trigger 1: Update account balance when journal entry inserted
--
-- When a new journal entry is created, this trigger automatically updates
-- the corresponding account's balance by adding (debit - credit).
--
-- Example: If account has $1000 and journal entry adds $500 debit:
--   New balance = $1000 + ($500 - $0) = $1500
CREATE TRIGGER IF NOT EXISTS update_account_balance_on_insert
AFTER INSERT ON journal_entries
FOR EACH ROW
BEGIN
    UPDATE accounts
    SET balance = balance + (NEW.debit_amount - NEW.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.account_id;
END;

-- Trigger 2: Update account balance when journal entry updated
--
-- When a journal entry is modified, this trigger:
--   1. Reverts the old balance impact (subtract old debit-credit)
--   2. Applies the new balance impact (add new debit-credit)
--   3. Handles account_id changes (move balance between accounts)
--
-- Example: Changing $500 debit to $600 debit:
--   Balance = Balance - ($500 - $0) + ($600 - $0) = Balance + $100
CREATE TRIGGER IF NOT EXISTS update_account_balance_on_update
AFTER UPDATE ON journal_entries
FOR EACH ROW
WHEN OLD.debit_amount != NEW.debit_amount
   OR OLD.credit_amount != NEW.credit_amount
   OR OLD.account_id != NEW.account_id
BEGIN
    -- Revert old balance from old account
    UPDATE accounts
    SET balance = balance - (OLD.debit_amount - OLD.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.account_id;

    -- Apply new balance to new account
    UPDATE accounts
    SET balance = balance + (NEW.debit_amount - NEW.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.account_id;
END;

-- Trigger 3: Update account balance when journal entry deleted
--
-- When a journal entry is deleted, this trigger reverts its impact on
-- the account balance by subtracting (debit - credit).
--
-- Example: Deleting $500 debit entry from account with $1500:
--   New balance = $1500 - ($500 - $0) = $1000
CREATE TRIGGER IF NOT EXISTS update_account_balance_on_delete
AFTER DELETE ON journal_entries
FOR EACH ROW
BEGIN
    UPDATE accounts
    SET balance = balance - (OLD.debit_amount - OLD.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.account_id;
END;

-- ============================================================================
-- PART 2: Balance Validation Log Table (Audit Trail)
-- ============================================================================

-- Table to store validation history for audit trail and reporting.
-- Each row represents one validation check of one account.
--
-- Use Cases:
--   - Track validation history over time
--   - Identify recurring balance issues
--   - Audit trail for compliance
--   - Detect data corruption patterns
CREATE TABLE IF NOT EXISTS balance_validation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    cached_balance REAL NOT NULL,           -- Balance stored in accounts.balance
    calculated_balance REAL NOT NULL,       -- Balance calculated from journal entries
    difference REAL NOT NULL,               -- cached - calculated
    was_repaired BOOLEAN DEFAULT 0,         -- True if fix_account_balance() was called
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE SET NULL
);

-- Index 1: Lookup validation history for specific account
-- Allows efficient queries like: "Show validation history for Checking account"
CREATE INDEX IF NOT EXISTS idx_validation_log_account
ON balance_validation_log(account_id, validated_at DESC);

-- Index 2: Find all repair operations
-- Allows efficient queries like: "Show all accounts that were auto-repaired"
CREATE INDEX IF NOT EXISTS idx_validation_log_repaired
ON balance_validation_log(was_repaired, validated_at DESC);

-- ============================================================================
-- PART 3: Trigger Status Verification View (Testing Aid)
-- ============================================================================

-- View to easily check which triggers are installed.
-- Useful for:
--   - Migration verification
--   - Debugging trigger issues
--   - Testing trigger installation
--
-- Usage:
--   SELECT * FROM trigger_status;
CREATE VIEW IF NOT EXISTS trigger_status AS
SELECT
    name,
    sql
FROM sqlite_master
WHERE type = 'trigger'
  AND name LIKE 'update_account_balance%'
ORDER BY name;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verification Queries (for testing):
--
-- 1. Check triggers installed:
--    SELECT COUNT(*) FROM trigger_status;  -- Should return 3
--
-- 2. Check validation log table:
--    SELECT COUNT(*) FROM balance_validation_log;  -- Should return 0 (empty)
--
-- 3. Test trigger (insert journal entry and check account balance updated)
--
-- 4. Check indices:
--    SELECT name FROM sqlite_master
--    WHERE type='index' AND tbl_name='balance_validation_log';
--
-- Rollback Script (if needed):
--    DROP TRIGGER IF EXISTS update_account_balance_on_insert;
--    DROP TRIGGER IF EXISTS update_account_balance_on_update;
--    DROP TRIGGER IF EXISTS update_account_balance_on_delete;
--    DROP VIEW IF EXISTS trigger_status;
--    DROP TABLE IF EXISTS balance_validation_log;
