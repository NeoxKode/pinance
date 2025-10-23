-- Migration 004: Create Split Transactions
-- Story: US-002C - Split Transactions
-- Date: October 23, 2025
-- Description: Add split transaction support with category-account linkage (Option A)
--
-- This migration enables:
-- 1. Splitting transactions across multiple categories (paychecks, shopping)
-- 2. Linking categories to accounts for proper journal entry creation
-- 3. Tracking split metadata (type, order, memo)
--
-- CRITICAL: This uses Option A (add account_id to categories) as recommended
-- by Tech Lead for cleaner architecture and better data integrity.

-- ============================================================================
-- STEP 1: Add split tracking to transactions table
-- ============================================================================

-- Add is_split flag to mark transactions that have splits
ALTER TABLE transactions ADD COLUMN is_split BOOLEAN DEFAULT 0;

-- Add split_count to quickly show number of splits
ALTER TABLE transactions ADD COLUMN split_count INTEGER DEFAULT 0;

-- ============================================================================
-- STEP 2: Create transaction_splits table
-- ============================================================================

CREATE TABLE transaction_splits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Links to parent transaction
    transaction_id INTEGER NOT NULL,

    -- Links to transaction group for double-entry (from US-002B)
    group_id INTEGER NOT NULL,

    -- Order of this split in the list (for display)
    split_order INTEGER NOT NULL DEFAULT 0,

    -- Category for this split (required)
    category_id INTEGER NOT NULL,

    -- Amount for this split (always positive, sign comes from transaction type)
    amount REAL NOT NULL CHECK (amount > 0),

    -- Optional memo for this specific split
    memo TEXT,

    -- Optional: For future account-to-account splits
    account_id INTEGER,

    -- Split type for analytics and templates
    -- Values: 'manual', 'paycheck', 'shopping', 'bill'
    split_type TEXT DEFAULT 'manual',

    -- Audit timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraints with CASCADE for data integrity
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES transaction_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- ============================================================================
-- STEP 3: Create performance indices
-- ============================================================================

-- Index for querying splits by transaction (most common query)
CREATE INDEX idx_splits_transaction ON transaction_splits(transaction_id);

-- Index for querying splits by group (for journal entry lookups)
CREATE INDEX idx_splits_group ON transaction_splits(group_id);

-- Index for category-based queries (spending reports)
CREATE INDEX idx_splits_category ON transaction_splits(category_id);

-- Index for split type filtering (template analytics)
CREATE INDEX idx_splits_type ON transaction_splits(split_type);

-- ============================================================================
-- STEP 4: Add category-account linkage (Option A)
-- ============================================================================

-- Add account_id column to categories
-- This links each category to its corresponding account for journal entries
-- Example: "Groceries" category → "Groceries Expense" account
ALTER TABLE categories ADD COLUMN account_id INTEGER;

-- Add foreign key constraint (note: SQLite doesn't support ALTER TABLE ADD CONSTRAINT
-- so this is a documentation comment for the schema)
-- FOREIGN KEY (account_id) REFERENCES accounts(id)

-- ============================================================================
-- STEP 5: Create trigger for updated_at timestamp
-- ============================================================================

CREATE TRIGGER update_split_timestamp
AFTER UPDATE ON transaction_splits
FOR EACH ROW
BEGIN
    UPDATE transaction_splits
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- ============================================================================
-- MIGRATION NOTES
-- ============================================================================

-- After running this migration, you MUST:
--
-- 1. Run the data migration script to link existing categories to accounts:
--    python scripts/migrate_category_accounts.py
--
-- 2. Verify the migration:
--    python scripts/check_schema.py
--
-- 3. Test split creation:
--    python -m pytest finance_app/tests/unit/test_transaction_split.py
--
-- Expected Performance:
--   - 2 splits  = 4 journal entries → ~20ms
--   - 5 splits  = 10 journal entries → ~50ms
--   - 10 splits = 20 journal entries → ~100ms (target)
--   - 20 splits = 40 journal entries → ~200ms (acceptable)
--
-- Database Size Impact:
--   - Minimal: ~100 bytes per split
--   - Indices: ~500 bytes per 100 splits
--
-- ============================================================================
-- ROLLBACK INSTRUCTIONS
-- ============================================================================

-- If you need to rollback this migration:
--
-- 1. Drop indices:
--    DROP INDEX IF EXISTS idx_splits_transaction;
--    DROP INDEX IF EXISTS idx_splits_group;
--    DROP INDEX IF EXISTS idx_splits_category;
--    DROP INDEX IF EXISTS idx_splits_type;
--
-- 2. Drop trigger:
--    DROP TRIGGER IF EXISTS update_split_timestamp;
--
-- 3. Drop table:
--    DROP TABLE IF EXISTS transaction_splits;
--
-- 4. Remove columns from transactions (SQLite limitation: need to recreate table):
--    -- Create backup, recreate table without new columns, restore data
--
-- 5. Remove account_id from categories (same limitation as above)
--
-- NOTE: Always backup database before migration!

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
