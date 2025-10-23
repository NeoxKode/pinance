#!/usr/bin/env python3
"""
Migrate existing account balances to opening balance journal entries.

This script creates OPENING journal entries for all accounts with non-zero balances,
ensuring that the journal is complete from day one.

Usage:
    python scripts/migrate_opening_balances.py [--dry-run] [--date YYYY-MM-DD]

Options:
    --dry-run       Preview what would be done without making changes
    --date          Date for opening entries (default: 2025-01-01)

Story: US-002B - Balanced Transaction Groups (Phase 1)
"""
import sys
import argparse
from pathlib import Path
from decimal import Decimal
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from finance_app.data.database import Database
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.business.double_entry_service import DoubleEntryService
from finance_app.data.models import EntryType
from finance_app.utils.logger import setup_logger

logger = setup_logger(__name__)


def migrate_opening_balances(
    dry_run: bool = False,
    opening_date: str = None
) -> tuple[int, int]:
    """
    Create opening balance journal entries for all accounts.

    This function:
    1. Gets all accounts with non-zero balances
    2. For each account, checks if OPENING entry already exists (idempotency)
    3. If not, creates OPENING journal entry using DoubleEntryService
    4. Logs progress and returns summary

    Args:
        dry_run: If True, only print what would be done (no database writes)
        opening_date: Date for opening entries (default: 2025-01-01)

    Returns:
        Tuple of (migrated_count, skipped_count)

    Raises:
        Exception: If migration fails
    """
    # Initialize database and services
    db = Database()
    account_repo = AccountRepository(db)
    journal_repo = JournalEntryRepository(db)
    double_entry_service = DoubleEntryService(db)

    # Default opening date if not provided
    if opening_date is None:
        opening_date = "2025-01-01"

    # Validate date format
    try:
        datetime.strptime(opening_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {opening_date}. Use YYYY-MM-DD")

    print(f"\n{'DRY RUN: ' if dry_run else ''}Migrating opening balances...")
    print(f"Opening balance date: {opening_date}\n")

    # Get all accounts
    accounts = account_repo.get_all()
    logger.info(f"Found {len(accounts)} total accounts")

    migrated_count = 0
    skipped_count = 0

    for account in accounts:
        # Skip accounts with zero balance
        if account.balance == Decimal("0"):
            print(f"  SKIP: {account.name} (zero balance)")
            skipped_count += 1
            continue

        # Check if OPENING entry already exists (idempotency)
        existing_entries = journal_repo.get_by_account(account.id)
        has_opening = any(
            entry.entry_type == EntryType.OPENING_BALANCE
            for entry in existing_entries
        )

        if has_opening:
            print(f"  SKIP: {account.name} (opening entry already exists)")
            logger.info(f"Account {account.id} ({account.name}) already has opening entry")
            skipped_count += 1
            continue

        # Log what we're about to do
        print(f"  {'WOULD CREATE' if dry_run else 'CREATING'}: {account.name} "
              f"opening balance = ${account.balance}")
        logger.info(
            f"{'Would create' if dry_run else 'Creating'} opening entry for "
            f"account {account.id} ({account.name}): balance={account.balance}"
        )

        if not dry_run:
            try:
                # CRITICAL: Reset account balance to zero BEFORE creating journal entry
                # The trigger will then add the journal entry amount, resulting in correct balance
                original_balance = account.balance

                # Reset balance to 0 using direct SQL
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE accounts SET balance = 0 WHERE id = ?",
                        (account.id,)
                    )
                    conn.commit()
                logger.info(f"Reset account {account.id} balance to 0 (was {original_balance})")

                # Create opening balance journal entry
                # The trigger will add this amount to the (now zero) account balance
                entry = double_entry_service.create_simple_transaction(
                    account_id=account.id,
                    amount=original_balance,  # Use original balance
                    date=opening_date,
                    description=f"Opening balance for {account.name}",
                    entry_type=EntryType.OPENING_BALANCE,
                    transaction_id=None,  # Opening balances don't link to transactions
                    reference_number="OPENING-BALANCE",
                    notes="Automatically created by opening balance migration"
                )
                print(f"    ✓ Created journal entry {entry.id} "
                      f"(debit={entry.debit_amount}, credit={entry.credit_amount})")
                logger.info(
                    f"Created opening entry {entry.id} for account {account.id}: "
                    f"debit={entry.debit_amount}, credit={entry.credit_amount}, "
                    f"balance_after={entry.balance_after}"
                )
                migrated_count += 1
            except Exception as e:
                print(f"    ✗ ERROR: {e}")
                logger.error(f"Failed to create opening entry for account {account.id}: {e}")
                # Continue with other accounts, don't stop entire migration
                skipped_count += 1
        else:
            # Dry run - just count it
            migrated_count += 1

    # Print summary
    print(f"\n{'DRY RUN ' if dry_run else ''}Summary:")
    print(f"  Accounts migrated: {migrated_count}")
    print(f"  Accounts skipped: {skipped_count}")
    print(f"  Total accounts: {len(accounts)}")

    if not dry_run and migrated_count > 0:
        print("\n✓ Migration complete!")
        print("Run: python scripts/validate_balances.py to verify")
    elif dry_run and migrated_count > 0:
        print("\nTo execute the migration, run without --dry-run flag:")
        print(f"  python scripts/migrate_opening_balances.py --date {opening_date}")

    logger.info(
        f"Migration {'would complete' if dry_run else 'completed'}: "
        f"migrated={migrated_count}, skipped={skipped_count}"
    )

    return migrated_count, skipped_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate existing account balances to opening balance journal entries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview migration (dry run)
  python scripts/migrate_opening_balances.py --dry-run

  # Run migration with default date (2025-01-01)
  python scripts/migrate_opening_balances.py

  # Run migration with custom date
  python scripts/migrate_opening_balances.py --date 2024-01-01

Rollback:
  If migration fails, restore from backup:
    cp finance.db.backup finance.db
        """
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be done without making changes"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Opening balance date in YYYY-MM-DD format (default: 2025-01-01)"
    )

    args = parser.parse_args()

    try:
        # Run migration
        migrated, skipped = migrate_opening_balances(
            dry_run=args.dry_run,
            opening_date=args.date
        )

        # Exit with success
        sys.exit(0)

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
