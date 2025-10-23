#!/usr/bin/env python3
"""
Check database schema in detail including triggers and defaults.
"""
import sqlite3

db_path = "finance.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("JOURNAL_ENTRIES TABLE FULL SCHEMA")
print("=" * 70)

# Get the CREATE TABLE statement
cursor.execute("""
    SELECT sql FROM sqlite_master
    WHERE type='table' AND name='journal_entries'
""")
create_sql = cursor.fetchone()
if create_sql:
    print(create_sql[0])
else:
    print("Table not found!")

print("\n" + "=" * 70)
print("TRIGGERS ON journal_entries")
print("=" * 70)

# Get all triggers
cursor.execute("""
    SELECT name, sql FROM sqlite_master
    WHERE type='trigger' AND tbl_name='journal_entries'
""")
triggers = cursor.fetchall()
for name, sql in triggers:
    print(f"\n{name}:")
    print(sql)

conn.close()
