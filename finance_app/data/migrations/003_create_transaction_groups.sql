-- Migration: 003_create_transaction_groups.sql
-- Description: Create transaction_groups table for balanced multi-entry transactions
-- Story: US-002B - Balanced Transaction Groups (Phase 2)
-- Date: 2025-10-22
-- Author: Backend Developer

-- ============================================================================
-- TRANSACTION GROUPS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS transaction_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_date TEXT NOT NULL,  -- YYYY-MM-DD format
    description TEXT NOT NULL,
    notes TEXT,
    total_debits REAL NOT NULL DEFAULT 0.0,  -- Sum of all debit amounts
    total_credits REAL NOT NULL DEFAULT 0.0,  -- Sum of all credit amounts
    is_balanced BOOLEAN NOT NULL DEFAULT 1,  -- Must be balanced (debits = credits)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraint: Ensure balanced entries (debits must equal credits)
    CHECK (total_debits = total_credits)
);

-- ============================================================================
-- INDICES FOR PERFORMANCE
-- ============================================================================

-- Index for querying by date
CREATE INDEX idx_transaction_group_date ON transaction_groups(group_date DESC);

-- Index for finding unbalanced groups (should be rare/none)
CREATE INDEX idx_transaction_group_balanced ON transaction_groups(is_balanced) WHERE is_balanced = 0;

-- ============================================================================
-- ADD FOREIGN KEY TO JOURNAL_ENTRIES
-- ============================================================================

-- Note: The group_id column already exists in journal_entries table (created in 002)
-- We just need to add the foreign key constraint

-- SQLite doesn't support ALTER TABLE ADD CONSTRAINT, so we need to verify the FK
-- The FK will be enforced programmatically in the repository layer

-- ============================================================================
-- VALIDATION TRIGGERS
-- ============================================================================

-- Trigger 1: Validate group balance before insert
CREATE TRIGGER validate_transaction_group_balance_insert
BEFORE INSERT ON transaction_groups
BEGIN
    SELECT CASE
        WHEN NEW.total_debits != NEW.total_credits THEN
            RAISE(ABORT, 'Transaction group must be balanced: debits must equal credits')
        WHEN NEW.total_debits < 0 OR NEW.total_credits < 0 THEN
            RAISE(ABORT, 'Total debits and credits must be non-negative')
    END;
END;

-- Trigger 2: Validate group balance before update
CREATE TRIGGER validate_transaction_group_balance_update
BEFORE UPDATE ON transaction_groups
BEGIN
    SELECT CASE
        WHEN NEW.total_debits != NEW.total_credits THEN
            RAISE(ABORT, 'Transaction group must be balanced: debits must equal credits')
        WHEN NEW.total_debits < 0 OR NEW.total_credits < 0 THEN
            RAISE(ABORT, 'Total debits and credits must be non-negative')
    END;
END;

-- Trigger 3: Automatically set updated_at timestamp
CREATE TRIGGER update_transaction_group_timestamp
AFTER UPDATE ON transaction_groups
BEGIN
    UPDATE transaction_groups
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- ============================================================================
-- MIGRATION VERIFICATION
-- ============================================================================

-- Verify table created
SELECT 'Migration 003: Transaction groups table created' as status;
SELECT 'Migration 003: 3 triggers created' as status;
SELECT 'Migration 003: 2 indices created' as status;

-- ============================================================================
-- ROLLBACK SCRIPT (for development/testing)
-- ============================================================================

-- To rollback this migration:
-- DROP TRIGGER IF EXISTS update_transaction_group_timestamp;
-- DROP TRIGGER IF EXISTS validate_transaction_group_balance_update;
-- DROP TRIGGER IF EXISTS validate_transaction_group_balance_insert;
-- DROP INDEX IF EXISTS idx_transaction_group_balanced;
-- DROP INDEX IF EXISTS idx_transaction_group_date;
-- DROP TABLE IF EXISTS transaction_groups;
