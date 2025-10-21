-- File: prototypes/double_entry_prototype.sql
-- Double-Entry Accounting Prototype Schema
-- SPIKE-001: Database schema for validating double-entry bookkeeping

-- ============================================================
-- PROTOTYPE TABLES
-- ============================================================

-- Minimal accounts table for testing
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    balance REAL DEFAULT 0.0
);

-- Minimal journal entries table
CREATE TABLE IF NOT EXISTS journal_entries_prototype (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    entry_date TEXT NOT NULL,
    description TEXT NOT NULL,
    debit_amount REAL NOT NULL DEFAULT 0.0,
    credit_amount REAL NOT NULL DEFAULT 0.0,
    balance_after REAL,
    entry_type TEXT DEFAULT 'transaction',
    FOREIGN KEY (account_id) REFERENCES accounts (id)
);

-- ============================================================
-- TRIGGERS
-- ============================================================

-- Trigger to automatically update account balance
-- This validates that the cached balance approach works
CREATE TRIGGER IF NOT EXISTS update_balance_prototype
AFTER INSERT ON journal_entries_prototype
BEGIN
    UPDATE accounts
    SET balance = balance + (NEW.debit_amount - NEW.credit_amount)
    WHERE id = NEW.account_id;
END;

-- Validation trigger to prevent invalid entries
CREATE TRIGGER IF NOT EXISTS validate_entry_prototype
BEFORE INSERT ON journal_entries_prototype
BEGIN
    SELECT CASE
        WHEN NEW.debit_amount > 0 AND NEW.credit_amount > 0 THEN
            RAISE(ABORT, 'Cannot have both debit and credit')
        WHEN NEW.debit_amount = 0 AND NEW.credit_amount = 0 THEN
            RAISE(ABORT, 'Must have debit or credit')
        WHEN NEW.debit_amount < 0 OR NEW.credit_amount < 0 THEN
            RAISE(ABORT, 'Amounts cannot be negative')
    END;
END;

-- ============================================================
-- INDEXES (for performance testing)
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_journal_entries_account
ON journal_entries_prototype(account_id);

CREATE INDEX IF NOT EXISTS idx_journal_entries_date
ON journal_entries_prototype(entry_date);

-- ============================================================
-- TEST QUERIES
-- ============================================================

-- Calculate account balance from entries
-- SELECT account_id, SUM(debit_amount - credit_amount) as calculated_balance
-- FROM journal_entries_prototype
-- GROUP BY account_id;

-- Get trial balance (should be balanced)
-- SELECT
--     SUM(debit_amount) as total_debits,
--     SUM(credit_amount) as total_credits,
--     SUM(debit_amount) - SUM(credit_amount) as difference
-- FROM journal_entries_prototype;

-- Validate cached balance vs calculated balance
-- SELECT
--     a.id,
--     a.name,
--     a.balance as cached_balance,
--     COALESCE(SUM(j.debit_amount - j.credit_amount), 0) as calculated_balance,
--     ABS(a.balance - COALESCE(SUM(j.debit_amount - j.credit_amount), 0)) as difference
-- FROM accounts a
-- LEFT JOIN journal_entries_prototype j ON a.id = j.account_id
-- GROUP BY a.id, a.name, a.balance;
