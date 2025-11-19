-- Migration 014: Saved Filters Table for US-015
-- Created: 2025-11-18
-- Purpose: Add saved_filters table for persisting user filter configurations
-- Epic: EPIC-002 - Search and Filter Transactions
-- Story: US-015 - Combined Filters & Saved Searches
-- Sprint: Sprint 16 (Final EPIC-002 story)

-- ==============================================================================
-- US-015: SAVED FILTERS PERSISTENCE
-- ==============================================================================
-- This migration creates the database foundation for US-015, which allows users
-- to save, load, and manage filter combinations.
--
-- IMPORTANT: Combined filter logic already exists in MainWindow._reload_filtered_transactions()
-- This table stores filter CONFIGURATIONS only, not the filtering logic itself.
--
-- Filter Criteria JSON Format (schema_version: 1):
-- {
--   "text_search": "coffee",           // Optional - US-011 text search keyword
--   "date_from": "2025-01-01",         // Optional - US-012 start date (ISO format)
--   "date_to": "2025-12-31",           // Optional - US-012 end date (ISO format)
--   "categories": ["Groceries", "Dining Out"],  // Optional - US-013 category list
--   "amount_min": "20.00",             // Optional - US-014 minimum amount (string)
--   "amount_max": "100.00",            // Optional - US-014 maximum amount (string)
--   "amount_absolute": true            // Optional - US-014 absolute value filter
-- }
-- ==============================================================================

BEGIN TRANSACTION;

-- ==============================================================================
-- TABLE: saved_filters
-- ==============================================================================
-- Stores user-created filter configurations for quick reuse.
-- Each saved filter captures the complete state of all active filters.

CREATE TABLE IF NOT EXISTS saved_filters (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Filter Identity
    name TEXT NOT NULL UNIQUE,  -- User-friendly name (e.g., "Coffee Purchases This Year")
    description TEXT,           -- Optional description of what this filter shows

    -- Filter Configuration (JSON)
    filter_json TEXT NOT NULL,  -- JSON string containing filter criteria
    schema_version INTEGER DEFAULT 1,  -- Schema version for future compatibility

    -- User Preferences
    is_favorite BOOLEAN DEFAULT 0,  -- Star/favorite flag for quick access

    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_used_at TEXT,  -- Track when filter was last loaded

    -- Constraints
    CHECK(length(name) > 0 AND length(name) <= 100),
    CHECK(length(filter_json) > 0),
    CHECK(schema_version >= 1)
);

-- ==============================================================================
-- INDEX 1: Favorite Filters (Quick Access)
-- ==============================================================================
-- Purpose: Optimize loading favorite filters (shown at top of dropdown)
-- Query Example: SELECT * FROM saved_filters WHERE is_favorite = 1 ORDER BY name
-- Expected Impact: Instant loading of favorite filters

CREATE INDEX IF NOT EXISTS idx_saved_filters_favorite
    ON saved_filters(is_favorite DESC, name ASC);

-- ==============================================================================
-- INDEX 2: Filter Name Search
-- ==============================================================================
-- Purpose: Fast lookups by filter name and alphabetical sorting
-- Query Example: SELECT * FROM saved_filters ORDER BY name
-- Expected Impact: Instant filter name searches and sorting

CREATE INDEX IF NOT EXISTS idx_saved_filters_name
    ON saved_filters(name);

-- ==============================================================================
-- INDEX 3: Recently Used Filters
-- ==============================================================================
-- Purpose: Optimize loading recently used filters
-- Query Example: SELECT * FROM saved_filters ORDER BY last_used_at DESC LIMIT 5
-- Expected Impact: Fast "recent filters" feature (future enhancement)

CREATE INDEX IF NOT EXISTS idx_saved_filters_last_used
    ON saved_filters(last_used_at DESC);

COMMIT;

-- ==============================================================================
-- SAMPLE DATA (Optional - for development/testing)
-- ==============================================================================
-- Uncomment to insert sample saved filters for testing:
--
-- INSERT INTO saved_filters (name, description, filter_json, is_favorite)
-- VALUES (
--     'Coffee Purchases',
--     'All coffee-related expenses',
--     '{"text_search": "coffee", "categories": ["Dining Out", "Groceries"]}',
--     1
-- );
--
-- INSERT INTO saved_filters (name, description, filter_json, is_favorite)
-- VALUES (
--     'Large Expenses This Month',
--     'Expenses over $100 in current month',
--     '{"date_from": "2025-11-01", "date_to": "2025-11-30", "amount_min": "100.00"}',
--     1
-- );
--
-- INSERT INTO saved_filters (name, description, filter_json)
-- VALUES (
--     'Grocery Shopping 2025',
--     'All grocery purchases in 2025',
--     '{"date_from": "2025-01-01", "date_to": "2025-12-31", "categories": ["Groceries"]}',
--     0
-- );
-- ==============================================================================

-- ==============================================================================
-- VERIFICATION QUERIES
-- ==============================================================================
-- After migration, verify table creation and indexes:
--
-- 1. Verify table exists:
--    SELECT name, sql FROM sqlite_master WHERE type='table' AND name='saved_filters';
--
-- 2. Verify indexes created:
--    SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='saved_filters';
--    Expected: idx_saved_filters_favorite, idx_saved_filters_name, idx_saved_filters_last_used
--
-- 3. Test UNIQUE constraint on name:
--    INSERT INTO saved_filters (name, filter_json) VALUES ('Test', '{}');
--    INSERT INTO saved_filters (name, filter_json) VALUES ('Test', '{}');  -- Should fail
--
-- 4. Test CHECK constraints:
--    INSERT INTO saved_filters (name, filter_json) VALUES ('', '{}');      -- Should fail (empty name)
--    INSERT INTO saved_filters (name, filter_json) VALUES ('Test', '');    -- Should fail (empty JSON)
--    INSERT INTO saved_filters (name, filter_json, schema_version)
--        VALUES ('Test2', '{}', 0);  -- Should fail (schema_version < 1)
-- ==============================================================================

-- ==============================================================================
-- SCHEMA VERSIONING NOTES
-- ==============================================================================
-- The schema_version field enables future filter criteria evolution:
--
-- Version 1 (Current):
-- - text_search: string
-- - date_from/date_to: ISO date strings
-- - categories: array of strings
-- - amount_min/amount_max: decimal strings
-- - amount_absolute: boolean
--
-- Future Versions (Examples):
-- Version 2: Add account_ids array for multi-account filtering
-- Version 3: Add payee filter
-- Version 4: Add tag filter
--
-- Migration Strategy:
-- - SavedFilterService checks schema_version when loading
-- - Upgrades old filters to current schema automatically
-- - Maintains backward compatibility with older filter formats
-- ==============================================================================

-- ==============================================================================
-- PERFORMANCE METRICS
-- ==============================================================================
-- Expected Performance (US-015 Acceptance Criteria):
-- - Load saved filter: < 50ms (single row SELECT by ID)
-- - List all filters: < 20ms (INDEX scan, typically < 100 filters)
-- - Save new filter: < 10ms (single row INSERT)
-- - Update filter: < 10ms (single row UPDATE)
-- - Delete filter: < 5ms (single row DELETE)
--
-- Storage Impact:
-- - Average filter size: ~200 bytes (name + description + JSON)
-- - 100 saved filters: ~20KB
-- - Negligible database size impact
-- ==============================================================================

-- ==============================================================================
-- INTEGRATION WITH EPIC-002
-- ==============================================================================
-- This table integrates with all EPIC-002 stories:
--
-- US-011 (Text Search):
--   - Saves: text_search keyword
--   - Loads: Applies to search input field
--
-- US-012 (Date Range Filter):
--   - Saves: date_from, date_to (ISO format: YYYY-MM-DD)
--   - Loads: Applies to date range dialog
--
-- US-013 (Category Filter):
--   - Saves: categories array
--   - Loads: Selects categories in checklist
--
-- US-014 (Amount Range Filter):
--   - Saves: amount_min, amount_max, amount_absolute
--   - Loads: Applies to amount range dialog
--
-- US-016 (Search Panel UI):
--   - Integrates: Saved filters dropdown in Row 5
--   - Displays: Filter name, favorite star, description tooltip
-- ==============================================================================

-- ==============================================================================
-- ROLLBACK INSTRUCTIONS
-- ==============================================================================
-- To rollback this migration:
-- BEGIN TRANSACTION;
-- DROP INDEX IF EXISTS idx_saved_filters_last_used;
-- DROP INDEX IF EXISTS idx_saved_filters_name;
-- DROP INDEX IF EXISTS idx_saved_filters_favorite;
-- DROP TABLE IF EXISTS saved_filters;
-- COMMIT;
-- ==============================================================================

-- Migration complete
-- Next steps: Create SavedFilter model, SavedFilterRepository, SavedFilterService
