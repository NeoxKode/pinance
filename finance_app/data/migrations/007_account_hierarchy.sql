-- Migration 007: Account Hierarchy Support
-- Story: US-006 - Account Hierarchy (Parent/Child Accounts)
-- Date: October 26, 2025
-- Description: Add hierarchy support for organizing accounts in parent/child relationships
--
-- This migration enables:
-- 1. Marking accounts as parent/header accounts (is_parent flag)
-- 2. Tracking hierarchy depth (hierarchy_level for validation)
-- 3. Efficient hierarchy queries with materialized path (hierarchy_path)
-- 4. Nested parent support up to 5 levels deep (industry standard)
--
-- CRITICAL DESIGN DECISIONS (from Gap Analysis):
-- - Nested parents ARE allowed (QuickBooks/Xero/GnuCash standard)
-- - Maximum depth: 5 levels (enforced in application layer)
-- - Materialized path pattern for O(log n) descendant queries
-- - parent_account_id field already exists from migration 001 ✅
-- - idx_accounts_parent index already exists from migration 001 ✅

-- ============================================================================
-- STEP 1: Add is_parent column
-- ============================================================================

-- Flag to identify parent/header accounts (accounts that contain other accounts)
-- Parent accounts:
--   - Cannot have direct transactions (enforced in application layer)
--   - Balance = sum of all leaf descendant accounts
--   - Display with folder icon in UI
--   - Can have parents themselves (nested parents allowed)
ALTER TABLE accounts
ADD COLUMN is_parent INTEGER DEFAULT 0
CHECK (is_parent IN (0, 1));  -- SQLite boolean: 0=False, 1=True

-- ============================================================================
-- STEP 2: Add hierarchy_level column
-- ============================================================================

-- Tracks depth in hierarchy tree (0-indexed)
-- Level 0 = top-level (no parent)
-- Level 1 = child of top-level
-- Level 2 = grandchild
-- Level 3 = great-grandchild
-- Level 4 = great-great-grandchild (maximum depth)
--
-- Maximum depth of 5 levels (0-4) enforced in application layer
-- This prevents over-complicated hierarchies and maintains UI usability
ALTER TABLE accounts
ADD COLUMN hierarchy_level INTEGER DEFAULT 0;

-- ============================================================================
-- STEP 3: Add hierarchy_path column (Materialized Path Pattern)
-- ============================================================================

-- Stores the complete path from root to this account
-- Format: "/parent_id/grandparent_id/.../account_id"
-- Examples:
--   - Top-level account (id=1): "/1"
--   - Child account (id=5, parent=1): "/1/5"
--   - Grandchild (id=12, parent=5, grandparent=1): "/1/5/12"
--
-- Benefits of materialized path:
-- 1. O(log n) descendant queries using LIKE '/1/%'
-- 2. No recursive CTEs needed (simpler queries)
-- 3. Easy to understand and debug
-- 4. Efficient with proper indexing
--
-- This pattern is proven 10x faster than loading all accounts into memory
-- (Reference: US-005 SQL optimization findings)
ALTER TABLE accounts
ADD COLUMN hierarchy_path TEXT;

-- ============================================================================
-- STEP 4: Create performance index on hierarchy_path
-- ============================================================================

-- Index for efficient descendant queries
-- Enables fast queries like: WHERE hierarchy_path LIKE '/1/%'
-- This query pattern returns all descendants of account 1
CREATE INDEX IF NOT EXISTS idx_accounts_hierarchy_path
ON accounts(hierarchy_path);

-- Note: idx_accounts_parent already exists from migration 001 ✅
-- This index supports: WHERE parent_account_id = ?

-- ============================================================================
-- STEP 5: Initialize hierarchy fields for existing accounts
-- ============================================================================

-- Set hierarchy_level to 0 for all existing accounts (they're all top-level)
UPDATE accounts
SET hierarchy_level = 0
WHERE hierarchy_level IS NULL;

-- Set hierarchy_path to '/[id]' for all existing accounts
-- This represents top-level accounts with no parent
UPDATE accounts
SET hierarchy_path = '/' || id
WHERE hierarchy_path IS NULL;

-- ============================================================================
-- STEP 6: Data integrity and validation notes
-- ============================================================================

-- HIERARCHY VALIDATION RULES (enforced in application layer):
-- 1. Maximum depth: 5 levels (hierarchy_level 0-4)
-- 2. No circular references (account cannot be its own ancestor)
-- 3. Child account type must match parent account type
-- 4. Parent accounts cannot have direct transactions
-- 5. Cannot delete parent account with children (unless force=True)

-- NESTED PARENTS ALLOWED (Gap Fix #2):
-- - Industry standard: QuickBooks, Xero, GnuCash allow nested parents
-- - Example: Assets → Current Assets → Bank Accounts → Checking
-- - Maximum depth validation provides sufficient protection
-- - Circular reference detection prevents cycles

-- MATERIALIZED PATH MAINTENANCE:
-- - hierarchy_path must be updated when:
--   1. Account parent_account_id changes (move operation)
--   2. Parent account is moved (all descendants must update)
-- - Use update_hierarchy_path() in repository layer
-- - Wrap multi-account updates in database transaction

-- EFFICIENT QUERIES:
-- 1. Get direct children:
--    SELECT * FROM accounts WHERE parent_account_id = ?
--
-- 2. Get all descendants (recursive):
--    SELECT * FROM accounts WHERE hierarchy_path LIKE '/1/%'
--
-- 3. Get parent balance (sum of leaf descendants):
--    SELECT SUM(balance) FROM accounts
--    WHERE hierarchy_path LIKE '/1/%' AND is_parent = 0

-- PERFORMANCE REQUIREMENTS:
-- - Load 1000 accounts in hierarchy: < 500ms
-- - Parent balance calculation (50 children): < 100ms
-- - Move account in hierarchy: < 200ms
-- - SQL aggregation is 10x faster than Python loops (US-005 findings)

-- EXAMPLE HIERARCHY:
-- id=1: Assets (is_parent=1, hierarchy_level=0, hierarchy_path='/1')
--   id=2: Bank Accounts (is_parent=1, hierarchy_level=1, hierarchy_path='/1/2')
--     id=5: Checking (is_parent=0, hierarchy_level=2, hierarchy_path='/1/2/5')
--     id=6: Savings (is_parent=0, hierarchy_level=2, hierarchy_path='/1/2/6')
--   id=3: Investments (is_parent=1, hierarchy_level=1, hierarchy_path='/1/3')
--     id=7: Brokerage (is_parent=0, hierarchy_level=2, hierarchy_path='/1/3/7')

-- ACCOUNTING EQUATION PRESERVATION:
-- - Hierarchy does NOT affect the accounting equation
-- - Parent balances are calculated, not stored
-- - Only leaf accounts have actual transactions
-- - Equation still holds: Assets = Liabilities + Equity

-- BACKWARD COMPATIBILITY:
-- - Existing accounts remain functional (all become top-level)
-- - parent_account_id field exists from migration 001 (not used until now)
-- - UI will be updated to display hierarchy (tree view)
-- - Legacy flat list view can still work by ignoring parent_account_id

-- ROLLBACK STRATEGY:
-- To rollback this migration:
-- 1. DROP INDEX idx_accounts_hierarchy_path
-- 2. ALTER TABLE accounts DROP COLUMN hierarchy_path
-- 3. ALTER TABLE accounts DROP COLUMN hierarchy_level
-- 4. ALTER TABLE accounts DROP COLUMN is_parent
-- 5. Existing parent_account_id values will remain (harmless)

-- ============================================================================
-- Migration complete!
-- ============================================================================
-- Next steps:
-- 1. Update Account model with new fields (Task 1.2)
-- 2. Implement hierarchy query methods in repository (Task 2.1)
-- 3. Add parent balance calculation in service layer (Task 3.2)
-- 4. Create AccountTreeWidget for UI (Task 4.1)
