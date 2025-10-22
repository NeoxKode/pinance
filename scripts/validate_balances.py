#!/usr/bin/env python3
"""
CLI script to validate account balances against journal entries.

Usage:
    python scripts/validate_balances.py [--reconcile] [--account-id ID]

Options:
    --reconcile       Force reconcile invalid accounts (use with caution)
    --account-id ID   Validate only a specific account

Story: US-002A - Journal Entry Foundation
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from finance_app.data.database import Database
from finance_app.utils.admin_tools import AdminTools


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate account balances against journal entries"
    )
    parser.add_argument(
        "--reconcile",
        action="store_true",
        help="Force reconcile invalid accounts (updates account table)"
    )
    parser.add_argument(
        "--account-id",
        type=int,
        help="Validate only a specific account ID"
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.01,
        help="Acceptable difference tolerance (default: 0.01)"
    )

    args = parser.parse_args()

    # Initialize database and admin tools
    db = Database()
    admin_tools = AdminTools(db)

    try:
        if args.account_id:
            # Validate single account
            print(f"\nValidating account {args.account_id}...")
            from decimal import Decimal
            result = admin_tools.validate_account_balance(
                account_id=args.account_id,
                tolerance=Decimal(str(args.tolerance))
            )

            print("\n" + "=" * 70)
            print(f"Account {result.account_id}: {result.account_name}")
            print("=" * 70)
            print(f"Account Balance: ${result.account_balance}")
            print(f"Journal Balance: ${result.journal_balance}")
            print(f"Difference:      ${result.difference}")
            print(f"Status:          {'✓ VALID' if result.is_valid else '✗ INVALID'}")
            print("=" * 70)

            if not result.is_valid and args.reconcile:
                print("\nReconciling account...")
                old_balance, new_balance = admin_tools.reconcile_account_balance(
                    account_id=args.account_id
                )
                print(f"✓ Reconciled: ${old_balance} → ${new_balance}")

            sys.exit(0 if result.is_valid else 1)

        else:
            # Validate all accounts
            print("\nValidating all accounts...")
            from decimal import Decimal
            results = admin_tools.validate_all_account_balances(
                tolerance=Decimal(str(args.tolerance))
            )

            # Print report
            admin_tools.print_validation_report(results)

            # Reconcile if requested
            if args.reconcile:
                invalid_results = [r for r in results if not r.is_valid]
                if invalid_results:
                    print(f"\nReconciling {len(invalid_results)} invalid accounts...")
                    for result in invalid_results:
                        old_balance, new_balance = admin_tools.reconcile_account_balance(
                            result.account_id
                        )
                        print(
                            f"  Account {result.account_id} ({result.account_name}): "
                            f"${old_balance} → ${new_balance}"
                        )
                    print("\n✓ Reconciliation complete")

            # Exit with error code if any invalid accounts found
            summary = admin_tools.get_validation_summary(results)
            sys.exit(0 if summary["invalid_accounts"] == 0 else 1)

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
