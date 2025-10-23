#!/usr/bin/env python3
"""
Check current account balances vs journal.
"""
import sqlite3
from decimal import Decimal

db_path = "finance.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("CURRENT BALANCES")
print("=" * 80)

cursor.execute("""
    SELECT a.id, a.name, a.balance,
           COALESCE(SUM(j.debit_amount - j.credit_amount), 0) as journal_balance
    FROM accounts a
    LEFT JOIN journal_entries j ON a.id = j.account_id
    GROUP BY a.id, a.name, a.balance
    ORDER BY a.name
""")

rows = cursor.fetchall()

print(f"{'Account':<30} {'Account Balance':>15} {'Journal Balance':>15} {'Match':>8}")
print("-" * 80)

for row in rows:
    account_id, name, account_balance, journal_balance = row
    account_balance = Decimal(str(account_balance))
    journal_balance = Decimal(str(journal_balance))
    match = "✓" if account_balance == journal_balance else "✗"

    print(f"{name:<30} ${account_balance:>14} ${journal_balance:>14} {match:>8}")

print("\n" + "=" * 80)
print("JOURNAL ENTRIES")
print("=" * 80)

cursor.execute("""
    SELECT j.id, a.name, j.entry_date, j.description, j.debit_amount, j.credit_amount, j.balance_after
    FROM journal_entries j
    JOIN accounts a ON j.account_id = a.id
    ORDER BY j.id
""")

entries = cursor.fetchall()
print(f"{'ID':<5} {'Account':<20} {'Date':<12} {'Debit':>10} {'Credit':>10} {'Balance After':>15}")
print("-" * 80)

for entry in entries:
    entry_id, account, date, desc, debit, credit, balance_after = entry
    print(f"{entry_id:<5} {account:<20} {date:<12} ${debit:>9.2f} ${credit:>9.2f} ${balance_after:>14.2f}")

conn.close()
