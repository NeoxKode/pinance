#!/usr/bin/env python3
"""
Add updated_at column to accounts table.

This column is referenced by triggers but was missing from the schema.
"""
import sqlite3
import sys

db_path = "finance.db"

def add_updated_at_column():
    """Add updated_at column to accounts table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Checking if updated_at column exists...")
        cursor.execute("PRAGMA table_info(accounts)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'updated_at' in column_names:
            print("✓ Column already exists, no action needed")
            return True

        print("Adding updated_at column to accounts table...")
        # SQLite doesn't allow CURRENT_TIMESTAMP as default in ALTER TABLE
        # So we add the column without a default, then update it
        cursor.execute("""
            ALTER TABLE accounts
            ADD COLUMN updated_at TIMESTAMP
        """)

        # Initialize updated_at for all existing rows
        cursor.execute("""
            UPDATE accounts
            SET updated_at = datetime('now')
        """)

        conn.commit()
        print(f"✓ Added updated_at column and initialized {cursor.rowcount} existing rows")

        # Verify
        cursor.execute("PRAGMA table_info(accounts)")
        columns = cursor.fetchall()
        has_updated_at = any(col[1] == 'updated_at' for col in columns)

        if has_updated_at:
            print("✓ Verification successful")
            return True
        else:
            print("✗ Verification failed")
            return False

    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = add_updated_at_column()
    sys.exit(0 if success else 1)
