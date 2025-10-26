"""
Repository for account data access.
"""
import sqlite3
from decimal import Decimal
from typing import List, Optional

from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
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
                    SELECT id, name, account_type, account_subtype, balance,
                           normal_balance, currency, parent_account_id,
                           legacy_type, last_reconciled_date, opening_balance_date
                    FROM accounts
                    ORDER BY account_type, name
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
                    SELECT id, name, account_type, account_subtype, balance,
                           normal_balance, currency, parent_account_id,
                           legacy_type, last_reconciled_date, opening_balance_date
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
                # Map new account type to legacy type for backward compatibility
                legacy_type_map = {
                    'checking': 'bank',
                    'savings': 'bank',
                    'cash': 'cash',
                    'investment': 'investment',
                    'credit_card': 'credit',
                    'loan': 'credit',
                    'mortgage': 'credit',
                    'line_of_credit': 'credit',
                }

                # Handle both enum and string values
                subtype_val = account.account_subtype.value if hasattr(account.account_subtype, 'value') else account.account_subtype
                type_val = account.account_type.value if hasattr(account.account_type, 'value') else account.account_type
                normal_bal_val = account.normal_balance.value if hasattr(account.normal_balance, 'value') else account.normal_balance

                legacy_type = legacy_type_map.get(subtype_val, 'bank')

                cursor.execute("""
                    INSERT INTO accounts (
                        name, type, account_type, account_subtype, balance,
                        normal_balance, currency, parent_account_id, legacy_type
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    account.name,
                    legacy_type,  # Old type column for backward compatibility
                    type_val,
                    subtype_val,
                    float(account.balance),
                    normal_bal_val,
                    account.currency,
                    account.parent_account_id,
                    legacy_type  # Also store in legacy_type
                ))
                account.id = cursor.lastrowid
                logger.info(
                    f"Created account: {account.name} "
                    f"({type_val}/{subtype_val}, "
                    f"ID: {account.id})"
                )
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

                # Map new account type to legacy type for backward compatibility
                legacy_type_map = {
                    'checking': 'bank',
                    'savings': 'bank',
                    'cash': 'cash',
                    'investment': 'investment',
                    'credit_card': 'credit',
                    'loan': 'credit',
                    'mortgage': 'credit',
                    'line_of_credit': 'credit',
                }

                # Handle both enum and string values
                subtype_val = account.account_subtype.value if hasattr(account.account_subtype, 'value') else account.account_subtype
                type_val = account.account_type.value if hasattr(account.account_type, 'value') else account.account_type
                normal_bal_val = account.normal_balance.value if hasattr(account.normal_balance, 'value') else account.normal_balance

                legacy_type = legacy_type_map.get(subtype_val, 'bank')

                cursor.execute("""
                    UPDATE accounts
                    SET name = ?,
                        type = ?,
                        account_type = ?,
                        account_subtype = ?,
                        balance = ?,
                        normal_balance = ?,
                        currency = ?,
                        parent_account_id = ?,
                        last_reconciled_date = ?,
                        opening_balance_date = ?
                    WHERE id = ?
                """, (
                    account.name,
                    legacy_type,  # Update legacy type for backward compatibility
                    type_val,
                    subtype_val,
                    float(account.balance),
                    normal_bal_val,
                    account.currency,
                    account.parent_account_id,
                    account.last_reconciled_date,  # US-004
                    account.opening_balance_date,  # US-005
                    account.id
                ))

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
            account_type=row['account_type'],
            account_subtype=row['account_subtype'],
            balance=Decimal(str(row['balance'])),
            normal_balance=row['normal_balance'],
            currency=row['currency'],
            parent_account_id=row['parent_account_id'],
            legacy_type=row['legacy_type'] if 'legacy_type' in row.keys() else None,
            last_reconciled_date=row['last_reconciled_date'] if 'last_reconciled_date' in row.keys() else None,  # US-004
            opening_balance_date=row['opening_balance_date'] if 'opening_balance_date' in row.keys() else None,  # US-005
            created_at=None,  # Not in current schema
            updated_at=None   # Not in current schema
        )
