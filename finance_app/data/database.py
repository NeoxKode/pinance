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
        if not self.db_path.exists():
            logger.info(f"Creating new database at {self.db_path}")
            self._create_schema()

    def _create_schema(self) -> None:
        """Create database schema."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Enable foreign keys
                cursor.execute("PRAGMA foreign_keys = ON")

                # Accounts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        type TEXT NOT NULL CHECK(type IN ('bank', 'cash', 'credit', 'investment')),
                        balance REAL NOT NULL DEFAULT 0.0,
                        currency TEXT DEFAULT 'USD',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create index on account name
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_accounts_name
                    ON accounts(name)
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

                # Add sample data if empty
                self._add_sample_data(conn)

        except sqlite3.Error as e:
            logger.error(f"Failed to create database schema: {e}")
            raise DatabaseError(f"Schema creation failed: {e}") from e

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
