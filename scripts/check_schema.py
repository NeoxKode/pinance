#!/usr/bin/env python3
"""
Quick script to check journal_entries table schema.
"""
import sqlite3
import sys

db_path = "finance.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table schema
    cursor.execute("PRAGMA table_info(journal_entries)")
    columns = cursor.fetchall()

    print("journal_entries table schema:")
    print("-" * 60)
    for col in columns:
        col_id, name, col_type, not_null, default_val, pk = col
        print(f"  {name:20s} {col_type:15s} {'NOT NULL' if not_null else ''}")

    print("\n" + "=" * 60)
    print(f"Total columns: {len(columns)}")

    # Check specifically for updated_at
    has_updated_at = any(col[1] == 'updated_at' for col in columns)
    print(f"\nHas 'updated_at' column: {has_updated_at}")

    conn.close()

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
