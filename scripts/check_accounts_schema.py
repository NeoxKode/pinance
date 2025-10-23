#!/usr/bin/env python3
"""
Check accounts table schema.
"""
import sqlite3

db_path = "finance.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("ACCOUNTS TABLE SCHEMA")
print("=" * 70)

# Get PRAGMA info
cursor.execute("PRAGMA table_info(accounts)")
columns = cursor.fetchall()

for col in columns:
    col_id, name, col_type, not_null, default_val, pk = col
    print(f"  {name:20s} {col_type:15s} {'NOT NULL' if not_null else ''} {f'DEFAULT {default_val}' if default_val else ''}")

print(f"\nTotal columns: {len(columns)}")

# Check for updated_at
has_updated_at = any(col[1] == 'updated_at' for col in columns)
print(f"\nHas 'updated_at' column: {has_updated_at}")

# Get CREATE TABLE statement
print("\n" + "=" * 70)
print("CREATE TABLE STATEMENT")
print("=" * 70)
cursor.execute("""
    SELECT sql FROM sqlite_master
    WHERE type='table' AND name='accounts'
""")
create_sql = cursor.fetchone()
if create_sql:
    print(create_sql[0])

conn.close()
