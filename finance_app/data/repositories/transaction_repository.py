"""
Repository for transaction data access.
"""
import sqlite3
from decimal import Decimal
from typing import List, Optional

from finance_app.data.models import Transaction
from finance_app.data.database import Database
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import DatabaseError, NotFoundError

logger = setup_logger(__name__)


class TransactionRepository:
    """Repository for transaction data access."""

    def __init__(self, database: Database):
        """
        Initialize repository.

        Args:
            database: Database instance
        """
        self.db = database

    def get_all(self, account_id: Optional[int] = None, limit: Optional[int] = None) -> List[Transaction]:
        """
        Get transactions, optionally filtered by account.

        Args:
            account_id: Filter by account ID (optional)
            limit: Maximum number of transactions to return (optional)

        Returns:
            List of Transaction objects

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                if account_id:
                    query = """
                        SELECT id, account_id, date, description, category, amount, type,
                               is_split, split_count,
                               reconciliation_status, reconciled_date, statement_date,
                               is_opening_balance
                        FROM transactions
                        WHERE account_id = ?
                        ORDER BY date DESC, id DESC
                    """
                    params = (account_id,)
                else:
                    query = """
                        SELECT id, account_id, date, description, category, amount, type,
                               is_split, split_count,
                               reconciliation_status, reconciled_date, statement_date,
                               is_opening_balance
                        FROM transactions
                        ORDER BY date DESC, id DESC
                    """
                    params = ()

                if limit:
                    query += f" LIMIT {limit}"

                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [self._row_to_transaction(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch transactions: {e}")
            raise DatabaseError(f"Failed to fetch transactions: {e}") from e

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """
        Get transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction object or None if not found

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, account_id, date, description, category, amount, type,
                           is_split, split_count,
                           reconciliation_status, reconciled_date, statement_date,
                           is_opening_balance
                    FROM transactions
                    WHERE id = ?
                """, (transaction_id,))
                row = cursor.fetchone()
                return self._row_to_transaction(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch transaction {transaction_id}: {e}")
            raise DatabaseError(f"Failed to fetch transaction: {e}") from e

    def create(self, transaction: Transaction) -> Transaction:
        """
        Create a new transaction.

        Args:
            transaction: Transaction object (without ID)

        Returns:
            Created transaction with ID

        Raises:
            DatabaseError: If creation fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO transactions (
                        account_id, date, description, category, amount, type,
                        reconciliation_status, is_opening_balance
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction.account_id,
                    transaction.date,
                    transaction.description,
                    transaction.category,
                    float(transaction.amount),
                    transaction.type,
                    transaction.reconciliation_status.value if hasattr(transaction.reconciliation_status, 'value') else transaction.reconciliation_status,
                    1 if transaction.is_opening_balance else 0
                ))
                transaction.id = cursor.lastrowid
                logger.info(f"Created transaction: {transaction.description} (ID: {transaction.id})")
                return transaction
        except sqlite3.Error as e:
            logger.error(f"Failed to create transaction: {e}")
            raise DatabaseError(f"Failed to create transaction: {e}") from e

    def update(self, transaction: Transaction) -> Transaction:
        """
        Update an existing transaction.

        US-004: Now includes reconciliation fields

        Args:
            transaction: Transaction object with ID

        Returns:
            Updated transaction

        Raises:
            NotFoundError: If transaction doesn't exist
            DatabaseError: If update fails
        """
        if not transaction.id:
            raise ValueError("Transaction ID is required for update")

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE transactions
                    SET account_id = ?, date = ?, description = ?, category = ?,
                        amount = ?, type = ?,
                        reconciliation_status = ?, reconciled_date = ?, statement_date = ?
                    WHERE id = ?
                """, (transaction.account_id, transaction.date, transaction.description,
                      transaction.category, float(transaction.amount), transaction.type,
                      transaction.reconciliation_status.value,  # US-004: reconciliation fields
                      transaction.reconciled_date,
                      transaction.statement_date,
                      transaction.id))

                if cursor.rowcount == 0:
                    raise NotFoundError(f"Transaction with ID {transaction.id} not found")

                logger.info(f"Updated transaction: {transaction.description} (ID: {transaction.id})")
                return transaction
        except sqlite3.Error as e:
            logger.error(f"Failed to update transaction {transaction.id}: {e}")
            raise DatabaseError(f"Failed to update transaction: {e}") from e

    def delete(self, transaction_id: int) -> bool:
        """
        Delete a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseError: If deletion fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Deleted transaction ID: {transaction_id}")
                return deleted
        except sqlite3.Error as e:
            logger.error(f"Failed to delete transaction {transaction_id}: {e}")
            raise DatabaseError(f"Failed to delete transaction: {e}") from e

    def get_by_category(self, category: str, account_id: Optional[int] = None) -> List[Transaction]:
        """
        Get transactions by category.

        Args:
            category: Category name
            account_id: Filter by account ID (optional)

        Returns:
            List of transactions

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                if account_id:
                    cursor.execute("""
                        SELECT id, account_id, date, description, category, amount, type,
                               is_split, split_count,
                               reconciliation_status, reconciled_date, statement_date,
                               is_opening_balance
                        FROM transactions
                        WHERE category = ? AND account_id = ?
                        ORDER BY date DESC
                    """, (category, account_id))
                else:
                    cursor.execute("""
                        SELECT id, account_id, date, description, category, amount, type,
                               is_split, split_count,
                               reconciliation_status, reconciled_date, statement_date,
                               is_opening_balance
                        FROM transactions
                        WHERE category = ?
                        ORDER BY date DESC
                    """, (category,))

                rows = cursor.fetchall()
                return [self._row_to_transaction(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch transactions by category: {e}")
            raise DatabaseError(f"Failed to fetch transactions by category: {e}") from e

    def get_by_date_range(
        self,
        start_date: str,
        end_date: str,
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Get transactions within a date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            account_id: Filter by account ID (optional)

        Returns:
            List of transactions

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                if account_id:
                    cursor.execute("""
                        SELECT id, account_id, date, description, category, amount, type,
                               is_split, split_count,
                               reconciliation_status, reconciled_date, statement_date,
                               is_opening_balance
                        FROM transactions
                        WHERE date BETWEEN ? AND ? AND account_id = ?
                        ORDER BY date DESC
                    """, (start_date, end_date, account_id))
                else:
                    cursor.execute("""
                        SELECT id, account_id, date, description, category, amount, type,
                               is_split, split_count,
                               reconciliation_status, reconciled_date, statement_date,
                               is_opening_balance
                        FROM transactions
                        WHERE date BETWEEN ? AND ?
                        ORDER BY date DESC
                    """, (start_date, end_date))

                rows = cursor.fetchall()
                return [self._row_to_transaction(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch transactions by date range: {e}")
            raise DatabaseError(f"Failed to fetch transactions by date range: {e}") from e

    def search_by_description(
        self,
        keyword: str,
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Search transactions by description keyword (case-insensitive).

        US-011: Basic Text Search - Enables users to find transactions by searching
        for keywords in transaction descriptions.

        Args:
            keyword: Search term (case-insensitive substring match)
            account_id: Optional account ID to filter (search within account only)

        Returns:
            List of matching Transaction objects, sorted by date DESC, id DESC

        Performance:
            - Uses idx_transactions_description for fast LIKE queries
            - Expected: < 50ms for 1K transactions, < 200ms for 10K transactions

        Examples:
            >>> repo.search_by_description("Starbucks")
            [Transaction(...), Transaction(...)]

            >>> repo.search_by_description("coffee", account_id=5)
            [Transaction(...)]

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Build query with optional account filter
                if account_id:
                    cursor.execute("""
                        SELECT id, account_id, date, description, category, amount, type,
                               is_split, split_count,
                               reconciliation_status, reconciled_date, statement_date,
                               is_opening_balance
                        FROM transactions
                        WHERE description LIKE ? AND account_id = ?
                        ORDER BY date DESC, id DESC
                    """, (f'%{keyword}%', account_id))
                else:
                    cursor.execute("""
                        SELECT id, account_id, date, description, category, amount, type,
                               is_split, split_count,
                               reconciliation_status, reconciled_date, statement_date,
                               is_opening_balance
                        FROM transactions
                        WHERE description LIKE ?
                        ORDER BY date DESC, id DESC
                    """, (f'%{keyword}%',))

                rows = cursor.fetchall()
                return [self._row_to_transaction(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Failed to search transactions by description: {e}")
            raise DatabaseError(f"Failed to search transactions by description: {e}") from e

    @staticmethod
    def _row_to_transaction(row: sqlite3.Row) -> Transaction:
        """
        Convert database row to Transaction object.

        US-004: Now includes reconciliation fields

        Args:
            row: Database row

        Returns:
            Transaction object
        """
        return Transaction(
            id=row['id'],
            account_id=row['account_id'],
            date=row['date'],
            description=row['description'],
            category=row['category'],
            amount=Decimal(str(row['amount'])),
            type=row['type'],
            is_split=bool(row['is_split']) if 'is_split' in row.keys() else False,
            split_count=row['split_count'] if 'split_count' in row.keys() else 0,
            # US-004: Reconciliation fields
            reconciliation_status=row['reconciliation_status'] if 'reconciliation_status' in row.keys() else 'unreconciled',
            reconciled_date=row['reconciled_date'] if 'reconciled_date' in row.keys() else None,
            statement_date=row['statement_date'] if 'statement_date' in row.keys() else None,
            # US-005: Opening balance flag
            is_opening_balance=bool(row['is_opening_balance']) if 'is_opening_balance' in row.keys() else False,
            created_at=None,  # Not in current schema
            updated_at=None   # Not in current schema
        )
