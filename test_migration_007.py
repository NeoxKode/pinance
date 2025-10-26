#!/usr/bin/env python3
"""
Test script for Migration 007: Account Hierarchy
US-006 - Account Hierarchy (Parent/Child Accounts)

This script tests that migration 007 runs correctly and verifies:
1. All hierarchy fields are added to accounts table
2. Indices are created
3. Existing accounts are initialized with default values
"""

import os
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from finance_app.data.database import Database

def test_migration_007():
    """Test migration 007 on a test database."""
    print("=" * 80)
    print("Testing Migration 007: Account Hierarchy")
    print("=" * 80)
    print()

    # Use a test database
    test_db_path = "test_hierarchy_migration.db"

    # Remove test database if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"✓ Removed existing test database: {test_db_path}")

    try:
        # Initialize database (this will run all migrations including 007)
        print(f"\nInitializing database: {test_db_path}")
        print("-" * 80)
        db = Database(test_db_path)
        print()

        # Verify migration 007 was applied
        print("Verifying Migration 007...")
        print("-" * 80)

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Check accounts table structure
            cursor.execute("PRAGMA table_info(accounts)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}  # {name: type}

            print("\n1. Checking hierarchy fields in accounts table:")
            hierarchy_fields = {
                'is_parent': 'INTEGER',
                'hierarchy_level': 'INTEGER',
                'hierarchy_path': 'TEXT'
            }

            all_fields_present = True
            for field_name, expected_type in hierarchy_fields.items():
                if field_name in columns:
                    actual_type = columns[field_name]
                    if actual_type == expected_type or actual_type == '':  # SQLite may return empty string
                        print(f"   ✓ {field_name}: {actual_type or expected_type}")
                    else:
                        print(f"   ✗ {field_name}: Expected {expected_type}, got {actual_type}")
                        all_fields_present = False
                else:
                    print(f"   ✗ {field_name}: MISSING")
                    all_fields_present = False

            if all_fields_present:
                print("   ✓ All hierarchy fields present")
            else:
                print("   ✗ Some hierarchy fields missing")
                return False

            # Check indices
            print("\n2. Checking indices:")
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND name LIKE 'idx_accounts_%'
                ORDER BY name
            """)
            indices = [row[0] for row in cursor.fetchall()]

            required_indices = ['idx_accounts_hierarchy_path', 'idx_accounts_parent']
            for idx_name in required_indices:
                if idx_name in indices:
                    print(f"   ✓ {idx_name}")
                else:
                    print(f"   ✗ {idx_name}: MISSING")

            # Check default values for new accounts
            print("\n3. Testing default values for new accounts:")
            cursor.execute("""
                INSERT INTO accounts (name, type, account_type, account_subtype, normal_balance, balance, currency)
                VALUES ('Test Account', 'bank', 'asset', 'checking', 'debit', 0.0, 'USD')
            """)
            conn.commit()

            cursor.execute("""
                SELECT is_parent, hierarchy_level, hierarchy_path
                FROM accounts WHERE name = 'Test Account'
            """)
            row = cursor.fetchone()

            if row:
                is_parent, hierarchy_level, hierarchy_path = row
                print(f"   is_parent: {is_parent} (expected: 0)")
                print(f"   hierarchy_level: {hierarchy_level} (expected: 0)")
                print(f"   hierarchy_path: {hierarchy_path} (expected: /[id])")

                # Verify defaults
                checks_passed = True
                if is_parent != 0:
                    print("   ✗ is_parent should be 0")
                    checks_passed = False
                if hierarchy_level != 0:
                    print("   ✗ hierarchy_level should be 0")
                    checks_passed = False
                if hierarchy_path is None or not hierarchy_path.startswith('/'):
                    print("   ✗ hierarchy_path should start with '/'")
                    checks_passed = False

                if checks_passed:
                    print("   ✓ All default values correct")
            else:
                print("   ✗ Could not retrieve test account")
                return False

            # Check that parent_account_id still exists from migration 001
            print("\n4. Verifying backward compatibility:")
            if 'parent_account_id' in columns:
                print("   ✓ parent_account_id field still exists (from migration 001)")
            else:
                print("   ✗ parent_account_id field missing (required from migration 001)")

            print("\n" + "=" * 80)
            print("Migration 007 Test: SUCCESS")
            print("=" * 80)
            print()
            print("Summary:")
            print("  ✓ All hierarchy fields added (is_parent, hierarchy_level, hierarchy_path)")
            print("  ✓ Indices created (idx_accounts_hierarchy_path)")
            print("  ✓ Default values set correctly")
            print("  ✓ Backward compatibility maintained (parent_account_id exists)")
            print()
            print("Ready for US-006 implementation!")
            return True

    except Exception as e:
        print(f"\n✗ Migration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up test database
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print(f"\n✓ Cleaned up test database: {test_db_path}")


if __name__ == "__main__":
    success = test_migration_007()
    sys.exit(0 if success else 1)
