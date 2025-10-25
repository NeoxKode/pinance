#!/usr/bin/env python3
"""
Setup Demo Data for Account Reconciliation Feature Demo

This script creates a demo checking account with realistic transactions
for demonstrating the reconciliation feature to the Product Owner.

Usage:
    python3 setup_reconciliation_demo_data.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from finance_app.data.database import Database
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.transaction_repository import TransactionRepository
from finance_app.data.models import Account, Transaction, AccountType, NormalBalance, ReconciliationStatus
from decimal import Decimal
from datetime import datetime


def setup_demo_data(db_path: str = "finance.db"):
    """
    Create demo data for reconciliation demonstration.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        dict with account_id and transaction count
    """

    print("=" * 60)
    print("Account Reconciliation - Demo Data Setup")
    print("=" * 60)
    print()

    # Connect to database
    db = Database(db_path)
    db.connect()
    print(f"✅ Connected to database: {db_path}")

    account_repo = AccountRepository(db)
    transaction_repo = TransactionRepository(db)

    # Check if demo account already exists
    all_accounts = account_repo.get_all()
    demo_account_exists = any(acc.name == "Demo Checking Account" for acc in all_accounts)

    if demo_account_exists:
        print("\n⚠️  Demo account already exists!")
        response = input("Do you want to delete it and recreate? (y/n): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled.")
            db.disconnect()
            return None

        # Find and delete existing demo account
        for acc in all_accounts:
            if acc.name == "Demo Checking Account":
                # Delete transactions first
                transactions = transaction_repo.get_by_account(acc.id)
                for txn in transactions:
                    transaction_repo.delete(txn.id)
                # Delete account
                account_repo.delete(acc.id)
                print(f"🗑️  Deleted existing demo account (ID: {acc.id})")

    # Create Demo Account
    print("\n📁 Creating Demo Checking Account...")
    demo_account = Account(
        id=None,
        name="Demo Checking Account",
        account_type=AccountType.ASSET_CHECKING,
        normal_balance=NormalBalance.DEBIT,
        opening_balance=Decimal("1000.00"),
        created_at=datetime.fromisoformat("2025-10-01T00:00:00"),
        last_reconciled_date=None
    )

    created_account = account_repo.create(demo_account)
    account_id = created_account.id

    print(f"✅ Created account: '{created_account.name}' (ID: {account_id})")
    print(f"   Opening Balance: ${created_account.opening_balance}")
    print(f"   Account Type: {created_account.account_type.value}")

    # Create Transactions
    print("\n💳 Creating Demo Transactions...")

    transactions_data = [
        # Date, Description, Amount, Category
        ("2025-10-02T10:00:00", "Grocery Store", "-52.34", "Should Clear"),
        ("2025-10-03T15:30:00", "Gas Station", "-45.00", "Should Clear"),
        ("2025-10-05T09:00:00", "Salary Deposit", "2000.00", "Should Clear"),
        ("2025-10-08T12:00:00", "Electric Bill", "-125.00", "Should Clear"),
        ("2025-10-10T08:00:00", "Coffee Shop", "-8.50", "Should Clear"),
        ("2025-10-12T20:00:00", "Online Shopping", "-89.99", "Should Clear"),
        ("2025-10-13T18:00:00", "ATM Withdrawal", "-60.00", "Should Clear"),
        ("2025-10-14T19:30:00", "Restaurant", "-67.45", "Should Clear"),
        ("2025-10-15T23:59:00", "Bank Interest", "2.35", "Should Clear"),
        ("2025-10-16T11:00:00", "Grocery Store", "-42.91", "Pending (After Statement)"),
        ("2025-10-18T09:00:00", "Paycheck", "2000.00", "Pending (After Statement)"),
    ]

    created_transactions = []
    for date_str, description, amount_str, note in transactions_data:
        transaction = Transaction(
            id=None,
            account_id=account_id,
            transaction_date=date_str.split('T')[0],
            description=description,
            amount=Decimal(amount_str),
            category_id=None,  # No category for demo
            reconciliation_status=ReconciliationStatus.UNRECONCILED,
            reconciled_date=None,
            statement_date=None,
            created_at=datetime.fromisoformat(date_str)
        )

        created_txn = transaction_repo.create(transaction)
        created_transactions.append(created_txn)

        # Format amount with color
        amount_val = Decimal(amount_str)
        amount_display = f"${abs(amount_val):>8.2f}"
        if amount_val >= 0:
            amount_display = f"+{amount_display}"
        else:
            amount_display = f"-{amount_display}"

        print(f"   ✓ {date_str.split('T')[0]} | {description:<20} | {amount_display} | {note}")

    # Calculate expected balances
    print("\n" + "=" * 60)
    print("📊 Demo Data Summary")
    print("=" * 60)

    # Transactions to clear (Oct 1-15)
    cleared_txns = [txn for txn in created_transactions if txn.transaction_date <= "2025-10-15"]
    cleared_sum = sum(txn.amount for txn in cleared_txns)
    cleared_balance = Decimal("1000.00") + cleared_sum

    # All transactions
    all_sum = sum(txn.amount for txn in created_transactions)
    current_balance = Decimal("1000.00") + all_sum

    print(f"\nAccount ID: {account_id}")
    print(f"Account Name: Demo Checking Account")
    print(f"\nTransactions Created: {len(created_transactions)}")
    print(f"  - Should Clear (Oct 1-15): {len(cleared_txns)}")
    print(f"  - Pending (After Oct 15): {len(created_transactions) - len(cleared_txns)}")

    print(f"\n💰 Balance Information:")
    print(f"  Opening Balance (Oct 1):      ${Decimal('1000.00'):>10.2f}")
    print(f"  Statement Balance (Oct 15):   ${cleared_balance:>10.2f} ⭐ Use this for demo!")
    print(f"  Current Balance (Oct 18):     ${current_balance:>10.2f}")

    print(f"\n📅 Reconciliation Details for Demo:")
    print(f"  Statement Period: October 1-15, 2025")
    print(f"  Statement Date: 2025-10-15")
    print(f"  Statement Balance: ${cleared_balance:.2f}")
    print(f"  Transactions to Mark: {len(cleared_txns)}")
    print(f"  Expected Discrepancy After Marking All: $0.00 ✅")

    print(f"\n" + "=" * 60)
    print("✅ Demo Data Setup Complete!")
    print("=" * 60)
    print(f"\n🎬 Ready for Product Owner Demo!")
    print(f"\n📋 Next Steps:")
    print(f"   1. Launch the application: python3 -m finance_app.main")
    print(f"   2. Select 'Demo Checking Account'")
    print(f"   3. Click Edit → Reconcile Account (or Ctrl+R)")
    print(f"   4. Enter Statement Date: October 15, 2025")
    print(f"   5. Enter Statement Balance: ${cleared_balance:.2f}")
    print(f"   6. Check the first 9 transactions (Oct 2-15)")
    print(f"   7. Complete reconciliation when discrepancy = $0.00")
    print(f"\n📄 See docs/demos/RECONCILIATION_PO_DEMO.md for full demo script")
    print()

    db.disconnect()

    return {
        "account_id": account_id,
        "transaction_count": len(created_transactions),
        "statement_balance": float(cleared_balance),
        "success": True
    }


def main():
    """Main entry point for the script."""

    # Default database path
    db_path = project_root / "finance.db"

    # Allow custom database path as argument
    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])

    print(f"\nUsing database: {db_path}")
    print()

    if not db_path.exists():
        print(f"⚠️  Database not found at: {db_path}")
        response = input("Create new database? (y/n): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled.")
            return

    result = setup_demo_data(str(db_path))

    if result and result["success"]:
        print("\n✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Script failed or was cancelled.")
        sys.exit(1)


if __name__ == "__main__":
    main()
