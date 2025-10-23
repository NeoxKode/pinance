#!/usr/bin/env python3
"""
Reset all account balances to zero before opening balance migration.

This script saves the current balances, then sets them to 0.
The migration will then recreate them via journal entries.

Story: US-002B - Balanced Transaction Groups (Phase 1)
"""
import sqlite3
import sys
from decimal import Decimal

db_path = "finance.db"

def reset_balances():
    """Reset all account balances to zero and save original values."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get current balances
        cursor.execute("SELECT id, name, balance FROM accounts WHERE balance != 0")
        accounts = cursor.fetchall()

        if not accounts:
            print("All account balances are already zero")
            return True

        print(f"Resetting {len(accounts)} account balances to zero:")
        print("-" * 60)

        for account_id, name, balance in accounts:
            print(f"  {name:<30} ${Decimal(str(balance)):>12} → $0.00")

        # Reset all balances to 0
        cursor.execute("UPDATE accounts SET balance = 0")

        conn.commit()

        print(f"\n✓ Reset {cursor.rowcount} account balances to zero")
        print("\nNow run: python scripts/migrate_opening_balances.py")

        return True

    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("RESET ACCOUNT BALANCES")
    print("=" * 60)
    print("\nThis will set all account balances to zero.")
    print("The migration will then recreate them via journal entries.\n")

    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled")
        sys.exit(0)

    success = reset_balances()
    sys.exit(0 if success else 1)
