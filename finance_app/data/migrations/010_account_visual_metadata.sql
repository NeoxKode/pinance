-- Migration 010: Account visual customization & metadata fields
-- Supports: US-009 (Sprint 10) + US-007 (Sprint 11)
-- Dependencies: Migration 009 (US-010 balance validation)
-- Tech Lead Review: 2025-10-27
-- Backend Developer: backend-dev
-- Created: 2025-10-27 (Sprint 10 Day 1)

-- ============================================================================
-- US-009 FIELDS (ACTIVE in Sprint 10) ✅
-- ============================================================================

-- Visual customization fields for account color coding and organization
ALTER TABLE accounts ADD COLUMN color_hex TEXT DEFAULT '#2563EB';
-- ^ Default Blue-600 color (WCAG AA compliant: 5.14:1 contrast), validated as #RRGGBB format in Account model

ALTER TABLE accounts ADD COLUMN display_order INTEGER DEFAULT 0;
-- ^ Custom sort order for account list (0 = default alphabetical)

ALTER TABLE accounts ADD COLUMN is_favorite BOOLEAN DEFAULT 0;
-- ^ Mark accounts as favorites for quick access (0 = not favorite, 1 = favorite)

-- ============================================================================
-- US-007 FIELDS (INACTIVE until Sprint 11) 💤
-- ============================================================================

-- Metadata fields pre-created to prevent Migration 011 duplicate column errors
-- These fields will remain NULL/unused until US-007 activates them in Sprint 11

ALTER TABLE accounts ADD COLUMN icon TEXT;
-- ^ Optional icon name/emoji for visual identification (e.g., "💰", "credit-card")

ALTER TABLE accounts ADD COLUMN notes TEXT;
-- ^ Free-form notes about the account (e.g., "Primary checking", "Emergency fund")

ALTER TABLE accounts ADD COLUMN tags TEXT;
-- ^ JSON array of tags for flexible categorization (e.g., '["personal", "tax-deductible"]')

ALTER TABLE accounts ADD COLUMN account_number TEXT;
-- ^ Account number for reconciliation (e.g., "****1234")

ALTER TABLE accounts ADD COLUMN institution_name TEXT;
-- ^ Financial institution name (e.g., "Chase", "Wells Fargo")

-- ============================================================================
-- INDICES FOR PERFORMANCE
-- ============================================================================

-- Index for favorite accounts filter (used in US-009 account list)
CREATE INDEX idx_accounts_favorite ON accounts(is_favorite);

-- Index for custom sort order (used in US-009 account list ordering)
CREATE INDEX idx_accounts_display_order ON accounts(display_order);

-- Index for color-based filtering/grouping (potential future feature)
CREATE INDEX idx_accounts_color ON accounts(color_hex);

-- ============================================================================
-- DEFAULT VALUES FOR EXISTING ACCOUNTS
-- ============================================================================

-- Set display_order = id for existing accounts to maintain current order
-- New accounts will use display_order = 0 (alphabetical) unless user customizes
UPDATE accounts SET display_order = id WHERE display_order = 0;

-- ============================================================================
-- MIGRATION METADATA
-- ============================================================================

-- Schema migrations table is updated automatically by database.py apply_migration()
-- Migration 010 will be marked as applied with timestamp

-- ============================================================================
-- ROLLBACK NOTES (SQLite Limitations)
-- ============================================================================

-- SQLite does not support DROP COLUMN in all versions
-- To rollback this migration:
-- 1. Create new accounts table without these columns
-- 2. Copy data from old table (excluding new columns)
-- 3. Drop old table
-- 4. Rename new table
-- See: docs/migrations/rollback-010.sql (if needed)

-- ============================================================================
-- TECH LEAD REVIEW CHECKLIST
-- ============================================================================

-- [ ] All 8 columns added (3 US-009, 5 US-007)
-- [ ] 3 indices created
-- [ ] display_order defaulted for existing accounts
-- [ ] No syntax errors
-- [ ] SQLite compatible
-- [ ] Comments explain US-009 vs US-007 fields
-- [ ] Ready for commit Day 2 4:00 PM

-- ============================================================================
-- END OF MIGRATION 010
-- ============================================================================
