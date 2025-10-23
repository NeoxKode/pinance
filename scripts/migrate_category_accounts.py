#!/usr/bin/env python3
"""
Data Migration: Link Categories to Accounts (Option A)

Story: US-002C - Split Transactions (Day 1)
Date: October 23, 2025

This script implements Option A of the category-account linkage strategy:
- For each existing category, create a corresponding account
- Link the category to its account via account_id
- Follow double-entry accounting conventions

Example:
  "Groceries" (expense category) → "Groceries Expense" (expense account)
  "Salary" (income category) → "Salary Income" (income account)
"""

import sqlite3
from decimal import Decimal
import sys

# Account type mappings
CATEGORY_TO_ACCOUNT_TYPE = {
    'expense': 'expense',
    'income': 'income'
}

CATEGORY_TO_ACCOUNT_SUBTYPE = {
    'expense': 'expense_category',
    'income': 'salary'  # Default, will be customized per category
}

CATEGORY_TO_NORMAL_BALANCE = {
    'expense': 'debit',  # Expenses increase with debits
    'income': 'credit'   # Income increases with credits
}

def get_or_create_account_for_category(cursor, category_id, category_name, category_type):
    """
    Get or create an account for a category.

    Args:
        cursor: Database cursor
        category_id: Category ID
        category_name: Category name
        category_type: 'income' or 'expense'

    Returns:
        account_id: ID of the account (existing or newly created)
    """
    # Determine account name
    if category_type == 'expense':
        account_name = f"{category_name} Expense"
    else:
        account_name = f"{category_name} Income"

    # Check if account already exists
    cursor.execute("""
        SELECT id FROM accounts WHERE name = ?
    """, (account_name,))
    existing = cursor.fetchone()

    if existing:
        print(f"  ✓ Found existing account: {account_name} (ID: {existing[0]})")
        return existing[0]

    # Create new account
    account_type = CATEGORY_TO_ACCOUNT_TYPE[category_type]
    account_subtype = CATEGORY_TO_ACCOUNT_SUBTYPE[category_type]
    normal_balance = CATEGORY_TO_NORMAL_BALANCE[category_type]

    cursor.execute("""
        INSERT INTO accounts (
            name, type, account_type, account_subtype, balance, normal_balance, currency
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        account_name,
        category_type,  # Legacy 'type' column (required NOT NULL)
        account_type,
        account_subtype,
        0.0,  # Starting balance
        normal_balance,
        'USD'
    ))

    account_id = cursor.lastrowid
    print(f"  ✓ Created new account: {account_name} (ID: {account_id})")
    return account_id


def migrate_categories_to_accounts(db_path='finance.db'):
    """
    Main migration function.

    For each category:
    1. Get or create corresponding account
    2. Link category to account via account_id column
    """
    print("=" * 70)
    print("CATEGORY-ACCOUNT LINKAGE MIGRATION (Option A)")
    print("=" * 70)
    print(f"\nDatabase: {db_path}")
    print("Strategy: Create accounts for categories and link via account_id")
    print()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Get all categories that don't have account_id set
        cursor.execute("""
            SELECT id, name, type, account_id
            FROM categories
            ORDER BY type, name
        """)
        categories = cursor.fetchall()

        if not categories:
            print("No categories found.")
            return

        print(f"Found {len(categories)} categories to process")
        print("-" * 70)

        migrated = 0
        skipped = 0
        created_accounts = []

        for cat_id, cat_name, cat_type, account_id in categories:
            print(f"\n[{cat_id}] {cat_name} ({cat_type})")

            # Skip if already linked
            if account_id is not None:
                print(f"  ⊙ Already linked to account_id={account_id}, skipping")
                skipped += 1
                continue

            # Get or create account
            new_account_id = get_or_create_account_for_category(
                cursor, cat_id, cat_name, cat_type
            )

            # Link category to account
            cursor.execute("""
                UPDATE categories
                SET account_id = ?
                WHERE id = ?
            """, (new_account_id, cat_id))

            print(f"  ✓ Linked category to account_id={new_account_id}")
            migrated += 1
            created_accounts.append((cat_name, new_account_id))

        # Commit transaction
        conn.commit()

        # Summary
        print("\n" + "=" * 70)
        print("MIGRATION SUMMARY")
        print("=" * 70)
        print(f"Categories processed: {len(categories)}")
        print(f"  - Migrated: {migrated}")
        print(f"  - Skipped (already linked): {skipped}")
        print(f"  - Accounts created: {len(created_accounts)}")

        if created_accounts:
            print("\nCreated Accounts:")
            for name, acc_id in created_accounts:
                print(f"  - {name}: account_id={acc_id}")

        # Verification
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)

        cursor.execute("""
            SELECT
                c.id, c.name, c.type, c.account_id, a.name as account_name
            FROM categories c
            LEFT JOIN accounts a ON c.account_id = a.id
            ORDER BY c.type, c.name
        """)
        results = cursor.fetchall()

        all_linked = True
        for cat_id, cat_name, cat_type, acc_id, acc_name in results:
            if acc_id is None:
                print(f"✗ [{cat_id}] {cat_name} - NOT LINKED")
                all_linked = False
            else:
                print(f"✓ [{cat_id}] {cat_name} → [{acc_id}] {acc_name}")

        print("\n" + "=" * 70)
        if all_linked:
            print("✓ MIGRATION SUCCESSFUL - All categories linked!")
        else:
            print("⚠ MIGRATION INCOMPLETE - Some categories not linked")
        print("=" * 70)

    except Exception as e:
        conn.rollback()
        print(f"\n✗ ERROR: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    import sys

    db_path = sys.argv[1] if len(sys.argv) > 1 else 'finance.db'
    migrate_categories_to_accounts(db_path)
