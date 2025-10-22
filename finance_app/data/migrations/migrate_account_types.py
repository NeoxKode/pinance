"""
Data migration script: Migrate legacy account types to new taxonomy.

This script converts old account types (bank, cash, credit, investment)
to the new double-entry accounting taxonomy (account_type + account_subtype).

User Story: US-001 - Account Type Taxonomy & Hierarchy
Date: October 22, 2025
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


# Mapping from legacy types to new account type system
LEGACY_TYPE_MAPPING: Dict[str, Tuple[str, str, str]] = {
    # legacy_type: (account_type, account_subtype, normal_balance)
    'bank': ('asset', 'checking', 'debit'),
    'cash': ('asset', 'cash', 'debit'),
    'credit': ('liability', 'credit_card', 'credit'),
    'investment': ('asset', 'investment', 'debit'),
}


class AccountTypeMigration:
    """Handle migration of account types to new taxonomy."""

    def __init__(self, db_path: str = "finance.db"):
        """
        Initialize migration.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)

    def check_migration_needed(self, conn: sqlite3.Connection) -> bool:
        """
        Check if migration is needed.

        Args:
            conn: Database connection

        Returns:
            True if migration is needed, False otherwise
        """
        cursor = conn.cursor()

        # Check if new columns exist
        cursor.execute("PRAGMA table_info(accounts)")
        columns = {row[1] for row in cursor.fetchall()}

        has_new_columns = all([
            'account_type' in columns,
            'account_subtype' in columns,
            'normal_balance' in columns
        ])

        if not has_new_columns:
            logger.info("Migration needed: New columns don't exist yet")
            return True

        # Check if any accounts have default values (not migrated)
        cursor.execute("""
            SELECT COUNT(*) FROM accounts
            WHERE account_type = 'asset'
              AND account_subtype = 'checking'
              AND normal_balance = 'debit'
              AND type IN ('bank', 'cash', 'credit', 'investment')
        """)

        count = cursor.fetchone()[0]
        if count > 0:
            logger.info(f"Migration needed: {count} accounts with default values")
            return True

        logger.info("Migration not needed: All accounts already migrated")
        return False

    def apply_schema_migration(self, conn: sqlite3.Connection) -> None:
        """
        Apply schema changes from SQL migration file.

        Args:
            conn: Database connection
        """
        logger.info("Applying schema migration...")

        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(accounts)")
        columns = {row[1] for row in cursor.fetchall()}

        # Add account_type column if it doesn't exist
        if 'account_type' not in columns:
            cursor.execute("""
                ALTER TABLE accounts
                ADD COLUMN account_type TEXT NOT NULL DEFAULT 'asset'
            """)
            logger.info("Added account_type column")

        # Add account_subtype column if it doesn't exist
        if 'account_subtype' not in columns:
            cursor.execute("""
                ALTER TABLE accounts
                ADD COLUMN account_subtype TEXT NOT NULL DEFAULT 'checking'
            """)
            logger.info("Added account_subtype column")

        # Add normal_balance column if it doesn't exist
        if 'normal_balance' not in columns:
            cursor.execute("""
                ALTER TABLE accounts
                ADD COLUMN normal_balance TEXT NOT NULL DEFAULT 'debit'
            """)
            logger.info("Added normal_balance column")

        # Add parent_account_id column if it doesn't exist
        if 'parent_account_id' not in columns:
            cursor.execute("""
                ALTER TABLE accounts
                ADD COLUMN parent_account_id INTEGER
            """)
            logger.info("Added parent_account_id column")

        # Add legacy_type column if it doesn't exist (preserve old type)
        if 'legacy_type' not in columns and 'type' in columns:
            cursor.execute("""
                ALTER TABLE accounts
                ADD COLUMN legacy_type TEXT
            """)
            # Copy old type to legacy_type
            cursor.execute("""
                UPDATE accounts
                SET legacy_type = type
            """)
            logger.info("Added legacy_type column and copied old type values")

        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_accounts_type
            ON accounts(account_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_accounts_subtype
            ON accounts(account_subtype)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_accounts_parent
            ON accounts(parent_account_id)
        """)

        conn.commit()
        logger.info("Schema migration completed")

    def migrate_account_data(self, conn: sqlite3.Connection) -> Dict[str, int]:
        """
        Migrate account data from legacy types to new taxonomy.

        Args:
            conn: Database connection

        Returns:
            Dictionary with migration statistics
        """
        logger.info("Migrating account data...")

        cursor = conn.cursor()

        # Get all accounts that need migration
        cursor.execute("""
            SELECT id, type FROM accounts
            WHERE type IS NOT NULL
        """)

        accounts = cursor.fetchall()
        stats = {
            'total': len(accounts),
            'migrated': 0,
            'skipped': 0,
            'errors': 0
        }

        for account_id, legacy_type in accounts:
            try:
                # Get mapping for this legacy type
                mapping = LEGACY_TYPE_MAPPING.get(legacy_type)

                if mapping:
                    account_type, account_subtype, normal_balance = mapping

                    # Update account with new values
                    cursor.execute("""
                        UPDATE accounts
                        SET account_type = ?,
                            account_subtype = ?,
                            normal_balance = ?
                        WHERE id = ?
                    """, (account_type, account_subtype, normal_balance, account_id))

                    stats['migrated'] += 1
                    logger.debug(
                        f"Migrated account {account_id}: {legacy_type} -> "
                        f"{account_type}/{account_subtype} ({normal_balance})"
                    )
                else:
                    logger.warning(f"No mapping for legacy type: {legacy_type}")
                    stats['skipped'] += 1

            except Exception as e:
                logger.error(f"Error migrating account {account_id}: {e}")
                stats['errors'] += 1

        conn.commit()

        logger.info(
            f"Data migration completed: {stats['migrated']} migrated, "
            f"{stats['skipped']} skipped, {stats['errors']} errors"
        )

        return stats

    def run_migration(self) -> Dict[str, int]:
        """
        Run complete migration process.

        Returns:
            Dictionary with migration statistics

        Raises:
            Exception: If migration fails
        """
        logger.info(f"Starting migration for database: {self.db_path}")

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row

        try:
            # Check if migration is needed
            if not self.check_migration_needed(conn):
                logger.info("Migration not needed - database already up to date")
                return {'total': 0, 'migrated': 0, 'skipped': 0, 'errors': 0}

            # Apply schema changes
            self.apply_schema_migration(conn)

            # Migrate data
            stats = self.migrate_account_data(conn)

            logger.info("Migration completed successfully")
            return stats

        except Exception as e:
            conn.rollback()
            logger.error(f"Migration failed: {e}")
            raise

        finally:
            conn.close()


def migrate_database(db_path: str = "finance.db") -> Dict[str, int]:
    """
    Convenience function to run migration.

    Args:
        db_path: Path to database file

    Returns:
        Migration statistics
    """
    migration = AccountTypeMigration(db_path)
    return migration.run_migration()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run migration
    try:
        stats = migrate_database()
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED")
        print("=" * 60)
        print(f"Total accounts: {stats['total']}")
        print(f"Migrated: {stats['migrated']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        print("=" * 60)

    except Exception as e:
        print(f"\nMIGRATION FAILED: {e}")
        exit(1)
