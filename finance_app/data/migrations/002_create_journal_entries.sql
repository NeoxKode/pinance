-- Migration: 002_create_journal_entries.sql
-- Description: Create journal entries table for double-entry accounting
-- Story: US-002A - Journal Entry Foundation
-- Date: 2025-10-22
-- Author: Tech Lead

-- ============================================================================
-- JOURNAL ENTRIES TABLE
-- ============================================================================

CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER,  -- Links to transactions table (nullable for non-transaction entries)
    group_id INTEGER,  -- Links to transaction_groups (US-002B) - nullable for single entries
    account_id INTEGER NOT NULL,
    entry_date TEXT NOT NULL,  -- YYYY-MM-DD
    description TEXT NOT NULL,
    debit_amount REAL NOT NULL DEFAULT 0.0,
    credit_amount REAL NOT NULL DEFAULT 0.0,
    balance_after REAL NOT NULL,  -- Running balance after this entry
    entry_type TEXT NOT NULL,  -- 'transaction', 'opening_balance', 'adjustment', 'transfer'
    reference_number TEXT,  -- Check number, invoice number, etc.
    is_reconciled BOOLEAN DEFAULT 0,
    reconciliation_id INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign keys
    FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE CASCADE
    -- Note: group_id foreign key will be added in US-002B when transaction_groups table is created
);

-- ============================================================================
-- INDICES FOR PERFORMANCE
-- ============================================================================

-- Single column indices
CREATE INDEX idx_journal_account ON journal_entries(account_id);
CREATE INDEX idx_journal_date ON journal_entries(entry_date DESC);
CREATE INDEX idx_journal_transaction ON journal_entries(transaction_id);
CREATE INDEX idx_journal_type ON journal_entries(entry_type);

-- Composite index for common query pattern (get entries by account, ordered by date)
CREATE INDEX idx_journal_account_date ON journal_entries(account_id, entry_date DESC);

-- Sparse index for reconciled entries only (more efficient)
CREATE INDEX idx_journal_reconciled ON journal_entries(is_reconciled) WHERE is_reconciled = 1;

-- ============================================================================
-- TRIGGER AUDIT TABLE (for debugging balance issues)
-- ============================================================================

CREATE TABLE trigger_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'
    record_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trigger_audit_timestamp ON trigger_audit(timestamp DESC);
CREATE INDEX idx_trigger_audit_trigger ON trigger_audit(trigger_name);

-- ============================================================================
-- VALIDATION TRIGGERS
-- ============================================================================

-- Trigger 1: Validate journal entry constraints before insert
CREATE TRIGGER validate_journal_entry_insert
BEFORE INSERT ON journal_entries
BEGIN
    -- Cannot have both debit and credit
    SELECT CASE
        WHEN NEW.debit_amount > 0 AND NEW.credit_amount > 0 THEN
            RAISE(ABORT, 'Journal entry cannot have both debit and credit amounts')
        WHEN NEW.debit_amount = 0 AND NEW.credit_amount = 0 THEN
            RAISE(ABORT, 'Journal entry must have either debit or credit amount')
        WHEN NEW.debit_amount < 0 OR NEW.credit_amount < 0 THEN
            RAISE(ABORT, 'Debit and credit amounts must be non-negative')
    END;
END;

-- Trigger 2: Validate journal entry constraints before update
CREATE TRIGGER validate_journal_entry_update
BEFORE UPDATE ON journal_entries
BEGIN
    -- Cannot have both debit and credit
    SELECT CASE
        WHEN NEW.debit_amount > 0 AND NEW.credit_amount > 0 THEN
            RAISE(ABORT, 'Journal entry cannot have both debit and credit amounts')
        WHEN NEW.debit_amount = 0 AND NEW.credit_amount = 0 THEN
            RAISE(ABORT, 'Journal entry must have either debit or credit amount')
        WHEN NEW.debit_amount < 0 OR NEW.credit_amount < 0 THEN
            RAISE(ABORT, 'Debit and credit amounts must be non-negative')
    END;
END;

-- Trigger 3: Prevent changing account_id (safety measure)
CREATE TRIGGER prevent_account_id_change
BEFORE UPDATE ON journal_entries
WHEN OLD.account_id != NEW.account_id
BEGIN
    SELECT RAISE(ABORT, 'Cannot change account_id of existing journal entry. Delete and recreate instead.');
END;

-- ============================================================================
-- BALANCE UPDATE TRIGGERS
-- ============================================================================

-- Trigger 4: Update account balance when journal entry inserted
CREATE TRIGGER update_account_balance_on_insert
AFTER INSERT ON journal_entries
BEGIN
    -- Update account balance
    UPDATE accounts
    SET balance = balance + (NEW.debit_amount - NEW.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.account_id;

    -- Audit log
    INSERT INTO trigger_audit (trigger_name, table_name, operation, record_id, new_value)
    VALUES ('update_account_balance_on_insert', 'journal_entries', 'INSERT',
            NEW.id, 'Amount: ' || (NEW.debit_amount - NEW.credit_amount));
END;

-- Trigger 5: Reverse account balance when journal entry deleted
CREATE TRIGGER update_account_balance_on_delete
AFTER DELETE ON journal_entries
BEGIN
    -- Reverse balance change
    UPDATE accounts
    SET balance = balance - (OLD.debit_amount - OLD.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.account_id;

    -- Audit log
    INSERT INTO trigger_audit (trigger_name, table_name, operation, record_id, old_value)
    VALUES ('update_account_balance_on_delete', 'journal_entries', 'DELETE',
            OLD.id, 'Amount: ' || (OLD.debit_amount - OLD.credit_amount));
END;

-- Trigger 6: Adjust account balance when journal entry amounts updated
-- Note: account_id changes are prevented by trigger above
CREATE TRIGGER update_account_balance_on_update
AFTER UPDATE ON journal_entries
WHEN OLD.debit_amount != NEW.debit_amount OR OLD.credit_amount != NEW.credit_amount
BEGIN
    -- Remove old amount, add new amount
    UPDATE accounts
    SET balance = balance - (OLD.debit_amount - OLD.credit_amount)
                         + (NEW.debit_amount - NEW.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.account_id;

    -- Audit log
    INSERT INTO trigger_audit (trigger_name, table_name, operation, record_id, old_value, new_value)
    VALUES ('update_account_balance_on_update', 'journal_entries', 'UPDATE',
            NEW.id,
            'Old: ' || (OLD.debit_amount - OLD.credit_amount),
            'New: ' || (NEW.debit_amount - NEW.credit_amount));
END;

-- ============================================================================
-- MIGRATION VERIFICATION
-- ============================================================================

-- Verify tables created
SELECT 'Migration 002: Journal entries table created' as status;
SELECT 'Migration 002: Trigger audit table created' as status;
SELECT 'Migration 002: 6 triggers created' as status;
SELECT 'Migration 002: 6 indices created' as status;

-- ============================================================================
-- ROLLBACK SCRIPT (for development/testing)
-- ============================================================================

-- To rollback this migration:
-- DROP TRIGGER IF EXISTS update_account_balance_on_update;
-- DROP TRIGGER IF EXISTS update_account_balance_on_delete;
-- DROP TRIGGER IF EXISTS update_account_balance_on_insert;
-- DROP TRIGGER IF EXISTS prevent_account_id_change;
-- DROP TRIGGER IF EXISTS validate_journal_entry_update;
-- DROP TRIGGER IF EXISTS validate_journal_entry_insert;
-- DROP INDEX IF EXISTS idx_trigger_audit_trigger;
-- DROP INDEX IF EXISTS idx_trigger_audit_timestamp;
-- DROP TABLE IF EXISTS trigger_audit;
-- DROP INDEX IF EXISTS idx_journal_reconciled;
-- DROP INDEX IF EXISTS idx_journal_account_date;
-- DROP INDEX IF EXISTS idx_journal_type;
-- DROP INDEX IF EXISTS idx_journal_transaction;
-- DROP INDEX IF EXISTS idx_journal_date;
-- DROP INDEX IF EXISTS idx_journal_account;
-- DROP TABLE IF EXISTS journal_entries;
