-- Migration 011: Account metadata indices
-- Supports: US-007 (Sprint 11) - Account Metadata & Organization
-- Dependencies: Migration 010 (US-009 visual metadata - MUST be applied first)
-- Tech Lead Review: Pending
-- Backend Developer: TBD
-- Created: 2025-11-04 (Sprint 11 Day 1)

-- ============================================================================
-- IMPORTANT: FIELD CREATION STRATEGY
-- ============================================================================
--
-- Migration 010 (US-009) already created ALL fields needed for US-007:
--   ✅ account_number TEXT
--   ✅ institution_name TEXT
--   ✅ notes TEXT
--   ✅ icon TEXT
--   ✅ tags TEXT
--   ✅ display_order INTEGER (shared with US-009)
--   ✅ is_favorite BOOLEAN (shared with US-009)
--
-- This "forward-looking" migration strategy prevents Migration 011 from
-- attempting duplicate ALTER TABLE commands which would fail.
--
-- Migration 011 ONLY adds search performance indices for US-007 fields.
--
-- ============================================================================

-- ============================================================================
-- US-007 INDICES FOR SEARCH PERFORMANCE
-- ============================================================================

-- Index for institution name search (AC2, AC6)
-- Enables fast autocomplete and search by institution
CREATE INDEX IF NOT EXISTS idx_accounts_institution ON accounts(institution_name);
-- Performance target: <50ms for 1000+ accounts searching by institution

-- Index for account number search (AC1, AC6)
-- Enables fast search by account number for reconciliation workflows
CREATE INDEX IF NOT EXISTS idx_accounts_number ON accounts(account_number);
-- Performance target: <50ms for 1000+ accounts searching by account number

-- ============================================================================
-- MIGRATION VERIFICATION
-- ============================================================================

-- Verify all required fields exist (should already exist from Migration 010)
-- This is a safety check - if any fail, Migration 010 was not applied correctly

-- Check account_number column exists
-- SELECT COUNT(*) FROM pragma_table_info('accounts') WHERE name = 'account_number';
-- Expected: 1

-- Check institution_name column exists
-- SELECT COUNT(*) FROM pragma_table_info('accounts') WHERE name = 'institution_name';
-- Expected: 1

-- Check notes column exists
-- SELECT COUNT(*) FROM pragma_table_info('accounts') WHERE name = 'notes';
-- Expected: 1

-- Check display_order column exists (shared with US-009)
-- SELECT COUNT(*) FROM pragma_table_info('accounts') WHERE name = 'display_order';
-- Expected: 1

-- Check is_favorite column exists (shared with US-009)
-- SELECT COUNT(*) FROM pragma_table_info('accounts') WHERE name = 'is_favorite';
-- Expected: 1

-- Verify indices created
-- SELECT name FROM sqlite_master WHERE type='index' AND name IN ('idx_accounts_institution', 'idx_accounts_number');
-- Expected: 2 rows

-- ============================================================================
-- ROLLBACK NOTES
-- ============================================================================

-- To rollback this migration:
-- DROP INDEX IF EXISTS idx_accounts_institution;
-- DROP INDEX IF EXISTS idx_accounts_number;
--
-- ❌ DO NOT drop columns - they are shared with Migration 010 (US-009)
-- Dropping columns would break US-009 functionality (color coding, favorites)

-- ============================================================================
-- MIGRATION METADATA
-- ============================================================================

-- Migration 011 Status:
-- - Adds: 2 indices (institution, account_number)
-- - Modifies: 0 columns (all exist from Migration 010)
-- - Dependencies: Migration 010 MUST be applied first
-- - Safe to apply: Yes (IF NOT EXISTS prevents errors)
-- - Safe to rollback: Yes (only drops indices)

-- ============================================================================
-- TECH LEAD REVIEW CHECKLIST
-- ============================================================================

-- [ ] Verified Migration 010 applied first (columns exist)
-- [ ] 2 indices created (institution, account_number)
-- [ ] No duplicate ALTER TABLE commands
-- [ ] IF NOT EXISTS used for safety
-- [ ] Comments explain forward-looking strategy
-- [ ] Rollback instructions clear
-- [ ] No syntax errors
-- [ ] SQLite compatible
-- [ ] Ready for Sprint 11 Day 1 completion

-- ============================================================================
-- END OF MIGRATION 011
-- ============================================================================
