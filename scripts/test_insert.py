#!/usr/bin/env python3
"""
Test inserting into journal_entries to diagnose the error.
"""
import sqlite3
from decimal import Decimal

db_path = "finance.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if we have an account to test with
    cursor.execute("SELECT id, name, balance FROM accounts LIMIT 1")
    account = cursor.fetchone()
    if not account:
        print("No accounts found in database")
        exit(1)

    account_id, account_name, current_balance = account
    print(f"Testing with account: {account_name} (ID: {account_id}, Balance: {current_balance})")

    # Try a simple insert
    print("\nAttempting INSERT...")
    cursor.execute("""
        INSERT INTO journal_entries (
            transaction_id, group_id, account_id, entry_date,
            description, debit_amount, credit_amount, balance_after,
            entry_type, reference_number, is_reconciled,
            reconciliation_id, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        None,  # transaction_id
        None,  # group_id
        account_id,  # account_id
        "2025-01-01",  # entry_date
        "Test entry",  # description
        100.0,  # debit_amount
        0.0,  # credit_amount
        current_balance + 100.0,  # balance_after
        "opening_balance",  # entry_type
        "TEST-001",  # reference_number
        0,  # is_reconciled
        None,  # reconciliation_id
        "Test note"  # notes
    ))

    entry_id = cursor.lastrowid
    print(f"✓ INSERT successful! Entry ID: {entry_id}")

    # Now try to SELECT it back with timestamps
    print("\nAttempting SELECT with timestamps...")
    cursor.execute("""
        SELECT id, transaction_id, group_id, account_id, entry_date,
               description, debit_amount, credit_amount, balance_after,
               entry_type, reference_number, is_reconciled,
               reconciliation_id, notes, created_at, updated_at
        FROM journal_entries
        WHERE id = ?
    """, (entry_id,))

    row = cursor.fetchone()
    if row:
        print(f"✓ SELECT successful!")
        print(f"  created_at: {row[14]}")
        print(f"  updated_at: {row[15]}")
    else:
        print("✗ SELECT returned no data")

    # Rollback the test
    conn.rollback()
    print("\n✓ Test rolled back (no changes saved)")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
