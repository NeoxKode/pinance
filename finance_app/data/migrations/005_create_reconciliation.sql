-- Migration 005: Create Account Reconciliation
-- Story: US-004 - Account Reconciliation
-- Date: October 23, 2025
-- Description: Add reconciliation support to track cleared transactions and reconciliation history
--
-- This migration enables:
-- 1. Tracking transaction reconciliation status (unreconciled, pending, cleared)
-- 2. Recording when transactions were reconciled against bank statements
-- 3. Maintaining reconciliation history with statement balances and discrepancies
-- 4. Tracking last reconciliation date per account
--
-- CRITICAL FIXES FROM TECH REVIEW:
-- - Added CHECK constraint for reconciliation_status enum values
-- - Added composite indices for performance (< 100ms for 1000+ transactions)
-- - Added concurrency prevention via reconciliation_status tracking

-- ============================================================================
-- STEP 1: Add reconciliation fields to transactions table
-- ============================================================================

-- Add reconciliation_status to track cleared/uncleared state
-- Default is 'unreconciled' for all existing and new transactions
ALTER TABLE transactions
ADD COLUMN reconciliation_status TEXT DEFAULT 'unreconciled'
CHECK (reconciliation_status IN ('unreconciled', 'pending', 'cleared'));

-- Add reconciled_date to track when transaction was marked as cleared
-- This provides audit trail for when reconciliation occurred
ALTER TABLE transactions
ADD COLUMN reconciled_date TEXT;  -- ISO 8601 format: YYYY-MM-DD

-- Add statement_date to link transaction to specific bank statement
-- Helps identify which statement this transaction appeared on
ALTER TABLE transactions
ADD COLUMN statement_date TEXT;  -- ISO 8601 format: YYYY-MM-DD

-- ============================================================================
-- STEP 2: Add last_reconciled_date to accounts table
-- ============================================================================

-- Track when account was last reconciled
-- Used to calculate opening balance for next reconciliation
ALTER TABLE accounts
ADD COLUMN last_reconciled_date TEXT;  -- ISO 8601 format: YYYY-MM-DD

-- ============================================================================
-- STEP 3: Create reconciliations table
-- ============================================================================

CREATE TABLE reconciliations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Account being reconciled
    account_id INTEGER NOT NULL,

    -- When reconciliation was performed
    reconciliation_date TEXT NOT NULL,  -- ISO 8601: YYYY-MM-DD

    -- Bank statement details
    statement_date TEXT NOT NULL,       -- Date of bank statement
    statement_balance REAL NOT NULL,    -- Ending balance on statement

    -- Calculated balances
    cleared_balance REAL NOT NULL,      -- Sum of all cleared transactions
    discrepancy REAL NOT NULL,          -- Difference: statement - cleared

    -- Metadata
    transaction_count INTEGER NOT NULL, -- Number of transactions cleared
    notes TEXT,                         -- Optional notes about discrepancy

    -- Audit trail
    created_at TEXT NOT NULL,           -- Timestamp when reconciliation was saved

    -- Foreign key constraints
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

-- ============================================================================
-- STEP 4: Create performance indices
-- ============================================================================

-- Index for querying unreconciled transactions by account
-- Critical for loading reconciliation dialog (< 100ms requirement)
CREATE INDEX idx_transactions_reconciliation
ON transactions(account_id, reconciliation_status);

-- Index for reconciliation history queries
-- Optimizes "get last 10 reconciliations" query
CREATE INDEX idx_reconciliations_account
ON reconciliations(account_id, reconciliation_date DESC);

-- ============================================================================
-- STEP 5: Data integrity notes
-- ============================================================================

-- IMMUTABLE RECONCILIATIONS:
-- Once a reconciliation record is created, it should NOT be modified.
-- This provides an audit trail of all reconciliation attempts.
-- If user needs to re-reconcile, create a NEW reconciliation record.

-- CONCURRENCY PREVENTION:
-- The application layer (ReconciliationService) checks for pending reconciliations
-- by querying transactions with reconciliation_status='pending'
-- Only one reconciliation can be "in progress" per account at a time.

-- BALANCE VALIDATION:
-- discrepancy = statement_balance - cleared_balance
-- discrepancy should be 0.00 for perfect reconciliation
-- Non-zero discrepancy indicates:
--   - Positive: Missing transactions (need to add to app)
--   - Negative: Extra transactions (need to remove from app or bank error)

-- CLEANUP ON ACCOUNT DELETION:
-- ON DELETE CASCADE ensures reconciliation history is removed when account is deleted
-- This maintains referential integrity

-- ============================================================================
-- Migration complete!
-- ============================================================================
