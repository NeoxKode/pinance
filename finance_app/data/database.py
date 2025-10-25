"""
Database connection and schema management.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import DatabaseError

logger = setup_logger(__name__)


def _apply_account_type_migration(conn: sqlite3.Connection) -> None:
    """
    Apply account type migration if needed.

    This adds the double-entry accounting fields to existing databases.

    Args:
        conn: Database connection
    """
    cursor = conn.cursor()

    # Check if migration is needed
    cursor.execute("PRAGMA table_info(accounts)")
    columns = {row[1] for row in cursor.fetchall()}

    if 'account_type' not in columns:
        logger.info("Applying account type migration...")

        # Add new columns
        cursor.execute("""
            ALTER TABLE accounts
            ADD COLUMN account_type TEXT NOT NULL DEFAULT 'asset'
        """)
        cursor.execute("""
            ALTER TABLE accounts
            ADD COLUMN account_subtype TEXT NOT NULL DEFAULT 'checking'
        """)
        cursor.execute("""
            ALTER TABLE accounts
            ADD COLUMN normal_balance TEXT NOT NULL DEFAULT 'debit'
        """)
        cursor.execute("""
            ALTER TABLE accounts
            ADD COLUMN parent_account_id INTEGER
        """)
        cursor.execute("""
            ALTER TABLE accounts
            ADD COLUMN legacy_type TEXT
        """)

        # Preserve old type column
        if 'type' in columns:
            cursor.execute("UPDATE accounts SET legacy_type = type")

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

        # Migrate existing data
        legacy_type_mapping = {
            'bank': ('asset', 'checking', 'debit'),
            'cash': ('asset', 'cash', 'debit'),
            'credit': ('liability', 'credit_card', 'credit'),
            'investment': ('asset', 'investment', 'debit'),
        }

        for legacy_type, (acc_type, acc_subtype, normal_bal) in legacy_type_mapping.items():
            cursor.execute("""
                UPDATE accounts
                SET account_type = ?,
                    account_subtype = ?,
                    normal_balance = ?
                WHERE legacy_type = ? OR type = ?
            """, (acc_type, acc_subtype, normal_bal, legacy_type, legacy_type))

        conn.commit()
        logger.info("Account type migration completed")


def _apply_journal_entries_migration(conn: sqlite3.Connection) -> None:
    """
    Apply journal entries migration (002_create_journal_entries.sql).

    This creates the journal_entries table for double-entry accounting.
    Story: US-002A - Journal Entry Foundation

    Args:
        conn: Database connection
    """
    cursor = conn.cursor()

    # Check if migration is needed
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='journal_entries'
    """)

    if cursor.fetchone() is None:
        logger.info("Applying journal entries migration (002)...")

        # Read and execute migration file
        migration_path = Path(__file__).parent / "migrations" / "002_create_journal_entries.sql"

        if not migration_path.exists():
            logger.warning(f"Migration file not found: {migration_path}")
            return

        with open(migration_path, 'r') as f:
            migration_sql = f.read()

        # Execute migration (split on semicolons but keep transaction together)
        cursor.executescript(migration_sql)

        conn.commit()
        logger.info("Journal entries migration (002) completed")

        # Verify migration
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('journal_entries', 'trigger_audit')
        """)
        tables = [row[0] for row in cursor.fetchall()]

        if 'journal_entries' in tables and 'trigger_audit' in tables:
            logger.info("Migration verification: ✓ Tables created")
        else:
            logger.error(f"Migration verification failed. Tables found: {tables}")

        # Verify triggers
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='trigger' AND tbl_name='journal_entries'
        """)
        triggers = [row[0] for row in cursor.fetchall()]

        if len(triggers) == 6:
            logger.info(f"Migration verification: ✓ All 6 triggers created")
        else:
            logger.warning(f"Migration verification: Found {len(triggers)}/6 triggers: {triggers}")
    else:
        logger.debug("Journal entries table already exists, skipping migration")


def _apply_transaction_groups_migration(conn: sqlite3.Connection) -> None:
    """
    Apply transaction groups migration (003_create_transaction_groups.sql).

    This creates the transaction_groups table for balanced multi-entry transactions.
    Story: US-002B - Balanced Transaction Groups (Phase 2)

    Args:
        conn: Database connection
    """
    cursor = conn.cursor()

    # Check if migration is needed
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='transaction_groups'
    """)

    if cursor.fetchone() is None:
        logger.info("Applying transaction groups migration (003)...")

        # Read and execute migration file
        migration_path = Path(__file__).parent / "migrations" / "003_create_transaction_groups.sql"

        if not migration_path.exists():
            logger.warning(f"Migration file not found: {migration_path}")
            return

        with open(migration_path, 'r') as f:
            migration_sql = f.read()

        # Execute migration (split on semicolons but keep transaction together)
        cursor.executescript(migration_sql)

        conn.commit()
        logger.info("Transaction groups migration (003) completed")

        # Verify migration
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='transaction_groups'
        """)
        if cursor.fetchone():
            logger.info("Migration verification: ✓ transaction_groups table created")
        else:
            logger.error("Migration verification failed: transaction_groups table not found")

        # Verify triggers
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='trigger' AND tbl_name='transaction_groups'
        """)
        triggers = [row[0] for row in cursor.fetchall()]

        if len(triggers) == 3:
            logger.info(f"Migration verification: ✓ All 3 triggers created")
        else:
            logger.warning(f"Migration verification: Found {len(triggers)}/3 triggers: {triggers}")
    else:
        logger.debug("Transaction groups table already exists, skipping migration")


def _apply_split_transactions_migration(conn: sqlite3.Connection) -> None:
    """
    Apply split transactions migration (004_create_split_transactions.sql).

    This creates the transaction_splits table and adds split tracking to transactions.
    Story: US-002C - Split Transactions (Day 1)

    Args:
        conn: Database connection
    """
    cursor = conn.cursor()

    # Check if migration is needed
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='transaction_splits'
    """)

    if cursor.fetchone() is None:
        logger.info("Applying split transactions migration (004)...")

        # Read and execute migration file
        migration_path = Path(__file__).parent / "migrations" / "004_create_split_transactions.sql"

        if not migration_path.exists():
            logger.warning(f"Migration file not found: {migration_path}")
            return

        with open(migration_path, 'r') as f:
            migration_sql = f.read()

        # Execute migration (split on semicolons but keep transaction together)
        cursor.executescript(migration_sql)

        conn.commit()
        logger.info("Split transactions migration (004) completed")

        # Verify migration
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='transaction_splits'
        """)
        if cursor.fetchone():
            logger.info("Migration verification: ✓ transaction_splits table created")
        else:
            logger.error("Migration verification failed: transaction_splits table not found")

        # Verify indices
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND tbl_name='transaction_splits'
        """)
        indices = [row[0] for row in cursor.fetchall()]

        if len(indices) >= 4:
            logger.info(f"Migration verification: ✓ Split transaction indices created")
        else:
            logger.warning(f"Migration verification: Found {len(indices)}/4 indices: {indices}")
    else:
        logger.debug("Transaction splits table already exists, skipping migration")


def _apply_reconciliation_migration(conn: sqlite3.Connection) -> None:
    """
    Apply reconciliation migration (005_create_reconciliation.sql).

    This creates the reconciliations table and adds reconciliation fields to transactions/accounts.
    Story: US-004 - Account Reconciliation (Day 1)

    Args:
        conn: Database connection
    """
    cursor = conn.cursor()

    # Check if migration is needed
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='reconciliations'
    """)

    if cursor.fetchone() is None:
        logger.info("Applying reconciliation migration (005)...")

        # Read and execute migration file
        migration_path = Path(__file__).parent / "migrations" / "005_create_reconciliation.sql"

        if not migration_path.exists():
            logger.warning(f"Migration file not found: {migration_path}")
            return

        with open(migration_path, 'r') as f:
            migration_sql = f.read()

        # Execute migration (split on semicolons but keep transaction together)
        cursor.executescript(migration_sql)

        conn.commit()
        logger.info("Reconciliation migration (005) completed")

        # Verify migration
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='reconciliations'
        """)
        if cursor.fetchone():
            logger.info("Migration verification: ✓ reconciliations table created")
        else:
            logger.error("Migration verification failed: reconciliations table not found")

        # Verify reconciliation_status column in transactions
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'reconciliation_status' in columns:
            logger.info("Migration verification: ✓ reconciliation_status column added to transactions")
        else:
            logger.error("Migration verification failed: reconciliation_status column not found in transactions")

        # Verify indices
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name IN ('idx_transactions_reconciliation', 'idx_reconciliations_account')
        """)
        indices = [row[0] for row in cursor.fetchall()]

        if len(indices) >= 2:
            logger.info(f"Migration verification: ✓ Reconciliation indices created")
        else:
            logger.warning(f"Migration verification: Found {len(indices)}/2 indices: {indices}")
    else:
        logger.debug("Reconciliations table already exists, skipping migration")


class Database:
    """
    Database manager with connection pooling and lifecycle management.

    Usage:
        db = Database("finance.db")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts")
    """

    def __init__(self, db_path: str = "finance.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None
        self._ensure_database_exists()
        logger.info(f"Database initialized at {self.db_path}")

    def _ensure_database_exists(self) -> None:
        """Ensure database file and directory exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        is_new_database = not self.db_path.exists()

        if is_new_database:
            logger.info(f"Creating new database at {self.db_path}")
            self._create_schema()
        else:
            # Apply migrations for existing database
            self._apply_migrations()

    def _create_schema(self) -> None:
        """Create database schema."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Enable foreign keys
                cursor.execute("PRAGMA foreign_keys = ON")

                # Accounts table (with double-entry accounting fields)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        type TEXT NOT NULL CHECK(type IN ('bank', 'cash', 'credit', 'investment')),
                        balance REAL NOT NULL DEFAULT 0.0,
                        currency TEXT DEFAULT 'USD',
                        account_type TEXT NOT NULL DEFAULT 'asset',
                        account_subtype TEXT NOT NULL DEFAULT 'checking',
                        normal_balance TEXT NOT NULL DEFAULT 'debit',
                        parent_account_id INTEGER,
                        legacy_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create indices on accounts
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_accounts_name
                    ON accounts(name)
                """)
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

                # Transactions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        account_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        description TEXT NOT NULL,
                        category TEXT NOT NULL,
                        amount REAL NOT NULL,
                        type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE
                    )
                """)

                # Create indices on transactions
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_transactions_account
                    ON transactions(account_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_transactions_date
                    ON transactions(date DESC)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_transactions_category
                    ON transactions(category)
                """)

                # Categories table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create index on category type
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_categories_type
                    ON categories(type)
                """)

                # Trigger to update updated_at timestamp
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS update_accounts_timestamp
                    AFTER UPDATE ON accounts
                    BEGIN
                        UPDATE accounts SET updated_at = CURRENT_TIMESTAMP
                        WHERE id = NEW.id;
                    END
                """)

                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS update_transactions_timestamp
                    AFTER UPDATE ON transactions
                    BEGIN
                        UPDATE transactions SET updated_at = CURRENT_TIMESTAMP
                        WHERE id = NEW.id;
                    END
                """)

                conn.commit()
                logger.info("Database schema created successfully")

                # Apply journal entries migration for new databases
                _apply_journal_entries_migration(conn)

                # Apply transaction groups migration for new databases
                _apply_transaction_groups_migration(conn)

                # Apply split transactions migration for new databases
                _apply_split_transactions_migration(conn)

                # Apply reconciliation migration for new databases
                _apply_reconciliation_migration(conn)

                # Add sample data if empty
                self._add_sample_data(conn)

        except sqlite3.Error as e:
            logger.error(f"Failed to create database schema: {e}")
            raise DatabaseError(f"Schema creation failed: {e}") from e

    def _apply_migrations(self) -> None:
        """Apply database migrations for existing databases."""
        try:
            with self.get_connection() as conn:
                _apply_account_type_migration(conn)
                _apply_journal_entries_migration(conn)
                _apply_transaction_groups_migration(conn)
                _apply_split_transactions_migration(conn)
                _apply_reconciliation_migration(conn)
                logger.info("All migrations applied successfully")
        except Exception as e:
            logger.error(f"Failed to apply migrations: {e}")
            # Don't raise - allow app to continue with what we have

    def _add_sample_data(self, conn: sqlite3.Connection) -> None:
        """Add sample data if database is empty."""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM accounts")
            if cursor.fetchone()[0] == 0:
                logger.info("Adding sample data to empty database")

                # Add sample account
                cursor.execute("""
                    INSERT INTO accounts (name, type, balance, currency)
                    VALUES ('Checking Account', 'bank', 1000.00, 'USD')
                """)
                account_id = cursor.lastrowid

                # Add sample categories
                categories = [
                    ('Groceries', 'expense'),
                    ('Salary', 'income'),
                    ('Utilities', 'expense'),
                    ('Entertainment', 'expense'),
                    ('Transportation', 'expense'),
                    ('Freelance', 'income'),
                ]
                cursor.executemany("""
                    INSERT INTO categories (name, type) VALUES (?, ?)
                """, categories)

                # Add sample transactions
                transactions = [
                    (account_id, '2025-10-15', 'Monthly Salary', 'Salary', 3000.00, 'income'),
                    (account_id, '2025-10-16', 'Grocery Store', 'Groceries', -150.50, 'expense'),
                    (account_id, '2025-10-17', 'Electric Bill', 'Utilities', -85.00, 'expense'),
                    (account_id, '2025-10-18', 'Gas Station', 'Transportation', -45.00, 'expense'),
                ]
                cursor.executemany("""
                    INSERT INTO transactions (account_id, date, description, category, amount, type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, transactions)

                conn.commit()
                logger.info("Sample data added successfully")

        except sqlite3.Error as e:
            logger.warning(f"Failed to add sample data: {e}")
            # Don't raise - sample data is optional

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Get a database connection context manager.

        Yields:
            SQLite connection object

        Raises:
            DatabaseError: If connection fails
        """
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # Enable column access by name
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise DatabaseError(f"Database operation failed: {e}") from e
        finally:
            if conn:
                conn.close()

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
