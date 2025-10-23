#!/usr/bin/env python3
"""
Verify transaction_groups table was created successfully.
"""
import sqlite3

db_path = "finance.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("TRANSACTION_GROUPS TABLE SCHEMA")
print("=" * 70)

# Get table schema
cursor.execute("PRAGMA table_info(transaction_groups)")
columns = cursor.fetchall()

for col in columns:
    col_id, name, col_type, not_null, default_val, pk = col
    print(f"  {name:20s} {col_type:15s} {'NOT NULL' if not_null else ''}")

print(f"\nTotal columns: {len(columns)}")

# Get triggers
print("\n" + "=" * 70)
print("TRIGGERS ON transaction_groups")
print("=" * 70)

cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='trigger' AND tbl_name='transaction_groups'
""")
triggers = cursor.fetchall()

for trigger in triggers:
    print(f"  - {trigger[0]}")

print(f"\nTotal triggers: {len(triggers)}")

# Get indices
print("\n" + "=" * 70)
print("INDICES ON transaction_groups")
print("=" * 70)

cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='index' AND tbl_name='transaction_groups'
""")
indices = cursor.fetchall()

for index in indices:
    print(f"  - {index[0]}")

print(f"\nTotal indices: {len(indices)}")

conn.close()

print("\n✓ Verification complete!")
