"""
Repository for account data access.
"""
import sqlite3
from decimal import Decimal
from typing import List, Optional

from finance_app.data.models import Account
from finance_app.data.database import Database
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import DatabaseError, NotFoundError

logger = setup_logger(__name__)


class AccountRepository:
    """Repository for account data access."""

    def __init__(self, database: Database):
        """
        Initialize repository.

        Args:
            database: Database instance
        """
        self.db = database

    def get_all(self) -> List[Account]:
        """
        Get all accounts.

        Returns:
            List of Account objects

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, type, balance, currency, created_at, updated_at
                    FROM accounts
                    ORDER BY name
                """)
                rows = cursor.fetchall()
                return [self._row_to_account(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch accounts: {e}")
            raise DatabaseError(f"Failed to fetch accounts: {e}") from e

    def get_by_id(self, account_id: int) -> Optional[Account]:
        """
        Get account by ID.

        Args:
            account_id: Account ID

        Returns:
            Account object or None if not found

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, type, balance, currency, created_at, updated_at
                    FROM accounts
                    WHERE id = ?
                """, (account_id,))
                row = cursor.fetchone()
                return self._row_to_account(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch account {account_id}: {e}")
            raise DatabaseError(f"Failed to fetch account: {e}") from e

    def create(self, account: Account) -> Account:
        """
        Create a new account.

        Args:
            account: Account object (without ID)

        Returns:
            Created account with ID

        Raises:
            DatabaseError: If creation fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO accounts (name, type, balance, currency)
                    VALUES (?, ?, ?, ?)
                """, (account.name, account.type, float(account.balance), account.currency))
                account.id = cursor.lastrowid
                logger.info(f"Created account: {account.name} (ID: {account.id})")
                return account
        except sqlite3.IntegrityError as e:
            logger.error(f"Account with name '{account.name}' already exists")
            raise DatabaseError(f"Account already exists: {e}") from e
        except sqlite3.Error as e:
            logger.error(f"Failed to create account: {e}")
            raise DatabaseError(f"Failed to create account: {e}") from e

    def update(self, account: Account) -> Account:
        """
        Update an existing account.

        Args:
            account: Account object with ID

        Returns:
            Updated account

        Raises:
            NotFoundError: If account doesn't exist
            DatabaseError: If update fails
        """
        if not account.id:
            raise ValueError("Account ID is required for update")

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE accounts
                    SET name = ?, type = ?, balance = ?, currency = ?
                    WHERE id = ?
                """, (account.name, account.type, float(account.balance),
                      account.currency, account.id))

                if cursor.rowcount == 0:
                    raise NotFoundError(f"Account with ID {account.id} not found")

                logger.info(f"Updated account: {account.name} (ID: {account.id})")
                return account
        except sqlite3.Error as e:
            logger.error(f"Failed to update account {account.id}: {e}")
            raise DatabaseError(f"Failed to update account: {e}") from e

    def delete(self, account_id: int) -> bool:
        """
        Delete an account.

        Args:
            account_id: Account ID

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseError: If deletion fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Deleted account ID: {account_id}")
                return deleted
        except sqlite3.Error as e:
            logger.error(f"Failed to delete account {account_id}: {e}")
            raise DatabaseError(f"Failed to delete account: {e}") from e

    def get_total_balance(self) -> Decimal:
        """
        Get total balance across all accounts.

        Returns:
            Total balance as Decimal

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(balance) FROM accounts")
                result = cursor.fetchone()[0]
                return Decimal(str(result)) if result else Decimal('0.0')
        except sqlite3.Error as e:
            logger.error(f"Failed to calculate total balance: {e}")
            raise DatabaseError(f"Failed to calculate total balance: {e}") from e

    def update_balance(self, account_id: int, amount: Decimal) -> None:
        """
        Update account balance by adding an amount.

        Args:
            account_id: Account ID
            amount: Amount to add (can be negative)

        Raises:
            NotFoundError: If account doesn't exist
            DatabaseError: If update fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE accounts
                    SET balance = balance + ?
                    WHERE id = ?
                """, (float(amount), account_id))

                if cursor.rowcount == 0:
                    raise NotFoundError(f"Account with ID {account_id} not found")

                logger.debug(f"Updated balance for account {account_id} by {amount}")
        except sqlite3.Error as e:
            logger.error(f"Failed to update balance for account {account_id}: {e}")
            raise DatabaseError(f"Failed to update balance: {e}") from e

    @staticmethod
    def _row_to_account(row: sqlite3.Row) -> Account:
        """
        Convert database row to Account object.

        Args:
            row: Database row

        Returns:
            Account object
        """
        return Account(
            id=row['id'],
            name=row['name'],
            type=row['type'],
            balance=Decimal(str(row['balance'])),
            currency=row['currency'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
