-- Migration 006: Opening Balance Equity
-- Story: US-005 - Opening Balance Equity
-- Date: October 26, 2025
-- Description: Add opening balance tracking and Opening Balance Equity account
--
-- This migration enables:
-- 1. Tracking opening balances for accounts with opening_balance_date
-- 2. Identifying opening balance transactions with is_opening_balance flag
-- 3. Creating system Opening Balance Equity account (Gap 5 fix)
-- 4. Maintaining accounting equation: Assets = Liabilities + Equity
--
-- CRITICAL FIXES FROM GAP FIX GUIDE:
-- - Gap 5: Pre-create Opening Balance Equity account in migration (guaranteed to exist)
-- - Added CHECK constraint for boolean is_opening_balance field
-- - Added composite indices for performance
-- - Added unique constraint to prevent duplicate equity accounts
-- - Pre-calculate equity balance to ensure zero opening balance

-- ============================================================================
-- STEP 1: Add opening_balance_date to accounts table
-- ============================================================================

-- Track when an account's opening balance was set
-- This is distinct from created_at - it represents the "as of" date for the opening balance
-- Example: Creating account on 2025-10-26 with opening balance as of 2025-01-01
ALTER TABLE accounts
ADD COLUMN opening_balance_date TEXT;  -- ISO 8601 format: YYYY-MM-DD

-- ============================================================================
-- STEP 2: Add is_opening_balance flag to transactions table
-- ============================================================================

-- Flag to identify transactions that represent opening balances
-- These transactions are automatically reconciled (status='cleared')
-- They should not be editable or deletable by users
ALTER TABLE transactions
ADD COLUMN is_opening_balance INTEGER DEFAULT 0
CHECK (is_opening_balance IN (0, 1));  -- SQLite boolean: 0=False, 1=True

-- ============================================================================
-- STEP 3: Create Opening Balance Equity account (GAP 5 FIX)
-- ============================================================================

-- This is CRITICAL for maintaining the accounting equation.
-- When creating an account with an opening balance:
--   1. Debit/Credit the account (increases asset or liability/equity)
--   2. Credit/Debit Opening Balance Equity (offsetting entry)
--
-- Example: Create checking account with $5000 opening balance
--   DR: Checking Account      $5000 (asset increases)
--   CR: Opening Balance Equity $5000 (equity increases)
--   Result: Assets (+$5000) = Equity (+$5000) ✓

-- Pre-create the Opening Balance Equity account
-- This ensures it always exists and has a predictable ID
INSERT INTO accounts (
    name,
    type,  -- Legacy type column (required for backward compatibility)
    account_type,
    account_subtype,
    normal_balance,
    balance,
    currency,
    created_at,
    updated_at
) VALUES (
    'Opening Balance Equity',
    'bank',  -- Legacy type value (using 'bank' for backward compatibility with CHECK constraint)
    'equity',
    'opening_balance',
    'credit',  -- Equity accounts have credit normal balance
    0.00,  -- Starts at zero, will be updated as opening balances are created
    'USD',
    datetime('now'),
    datetime('now')
);

-- ============================================================================
-- STEP 4: Add unique constraint for Opening Balance Equity account
-- ============================================================================

-- Prevent duplicate Opening Balance Equity accounts
-- There should only be ONE account with this exact configuration
CREATE UNIQUE INDEX idx_unique_opening_balance_equity
ON accounts(account_type, account_subtype)
WHERE account_type = 'equity' AND account_subtype = 'opening_balance';

-- ============================================================================
-- STEP 5: Create performance indices
-- ============================================================================

-- Index for querying accounts with opening balances
-- Used by get_opening_balance_summary() and reporting
CREATE INDEX idx_accounts_opening_balance
ON accounts(opening_balance_date)
WHERE opening_balance_date IS NOT NULL;

-- Index for querying opening balance transactions
-- Used for validation and reporting
CREATE INDEX idx_transactions_opening_balance
ON transactions(is_opening_balance, date)
WHERE is_opening_balance = 1;

-- Composite index for account + opening balance queries
-- Optimizes queries that filter by account and opening balance status
CREATE INDEX idx_transactions_account_opening
ON transactions(account_id, is_opening_balance);

-- ============================================================================
-- STEP 6: Data integrity and validation notes
-- ============================================================================

-- OPENING BALANCE RULES:
-- 1. An account can only have ONE opening balance (enforced in application layer)
-- 2. Opening balance transactions are automatically marked as 'cleared'
-- 3. Opening balance transactions should not be editable or deletable
-- 4. opening_balance_date is the "as of" date, NOT the creation date

-- ACCOUNTING EQUATION VALIDATION:
-- After setting opening balances, the equation must hold:
--   SUM(assets.balance) = SUM(liabilities.balance) + SUM(equity.balance)
-- The validate_opening_balance_equity() method in AccountService checks this

-- OPENING BALANCE EQUITY ACCOUNT:
-- - Type: equity
-- - Subtype: opening_balance
-- - Name: "Opening Balance Equity"
-- - Balance: Should equal -(sum of all opening balance assets - sum of opening balance liabilities)
-- - This account is REQUIRED and pre-created in this migration

-- JOURNAL ENTRY PATTERN:
-- For each opening balance, TWO journal entries are created:
-- 1. Entry for the account being created/updated
-- 2. Offsetting entry in Opening Balance Equity account
-- Both entries have entry_type = 'opening_balance'

-- EXAMPLE SCENARIO:
-- User creates 3 accounts with opening balances on 2025-01-01:
--   - Checking (asset):    $5,000
--   - Savings (asset):     $10,000
--   - Credit Card (liability): $2,000
--
-- Journal entries created:
--   DR Checking         $5,000
--   CR Opening Balance Equity $5,000
--
--   DR Savings          $10,000
--   CR Opening Balance Equity $10,000
--
--   CR Credit Card      $2,000
--   DR Opening Balance Equity $2,000
--
-- Final balances:
--   Assets: $15,000 (Checking + Savings)
--   Liabilities: $2,000 (Credit Card)
--   Equity: $13,000 (Opening Balance Equity)
--   Equation: $15,000 = $2,000 + $13,000 ✓

-- CLEANUP ON ACCOUNT DELETION:
-- Opening Balance Equity account should NOT be deletable
-- This is enforced in the application layer (AccountService)
-- If user tries to delete it, they should see an error message

-- ============================================================================
-- Migration complete!
-- ============================================================================
