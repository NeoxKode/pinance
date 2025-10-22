-- Migration: Add double-entry account type fields
-- File: 001_add_account_types.sql
-- User Story: US-001 - Account Type Taxonomy & Hierarchy
-- Date: October 22, 2025

-- ============================================================
-- STEP 1: Add new columns for double-entry accounting
-- ============================================================

-- Add account_type column (asset, liability, equity, income, expense)
ALTER TABLE accounts ADD COLUMN account_type TEXT NOT NULL DEFAULT 'asset';

-- Add account_subtype column (checking, savings, credit_card, loan, etc.)
ALTER TABLE accounts ADD COLUMN account_subtype TEXT NOT NULL DEFAULT 'checking';

-- Add normal_balance column (debit or credit)
ALTER TABLE accounts ADD COLUMN normal_balance TEXT NOT NULL DEFAULT 'debit';

-- Add parent_account_id for hierarchical accounts (future use)
ALTER TABLE accounts ADD COLUMN parent_account_id INTEGER;

-- ============================================================
-- STEP 2: Create constraints
-- ============================================================

-- Check constraint for account_type
-- Note: SQLite doesn't support ALTER TABLE ADD CONSTRAINT, so this is documentation
-- The constraint will be enforced in application code
-- Valid values: 'asset', 'liability', 'equity', 'income', 'expense'

-- Check constraint for normal_balance
-- Valid values: 'debit', 'credit'

-- ============================================================
-- STEP 3: Create indexes for performance
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(account_type);
CREATE INDEX IF NOT EXISTS idx_accounts_subtype ON accounts(account_subtype);
CREATE INDEX IF NOT EXISTS idx_accounts_parent ON accounts(parent_account_id);

-- ============================================================
-- STEP 4: Rename legacy 'type' column for backward compatibility
-- ============================================================

-- SQLite doesn't support ALTER TABLE RENAME COLUMN directly in older versions
-- We'll handle this in the Python migration script
-- The old 'type' column will be preserved as 'legacy_type'

-- ============================================================
-- STEP 5: Add foreign key for parent accounts (future)
-- ============================================================

-- Foreign key constraint for hierarchical accounts
-- This will be used when we implement parent/child account relationships
-- FOREIGN KEY (parent_account_id) REFERENCES accounts(id) ON DELETE SET NULL

-- ============================================================
-- MIGRATION NOTES
-- ============================================================

-- This migration adds the foundational columns for double-entry accounting
-- without modifying existing data. The data migration (mapping old types
-- to new account_type/account_subtype) will be handled separately in
-- Python migration script: migrate_account_types.py

-- Backward compatibility:
-- - Old 'type' column preserved as 'legacy_type'
-- - Existing accounts will have default values until data migration runs
-- - Application code must handle both old and new account type systems

-- Rollback strategy:
-- To rollback this migration:
-- 1. Remove the new columns
-- 2. Restore the old 'type' column from 'legacy_type'
-- 3. Drop the new indexes
