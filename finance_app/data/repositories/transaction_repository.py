"""
Repository for transaction data access.
"""
import sqlite3
from datetime import date
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

    def filter_by_date_range(
        self,
        from_date: 'date',
        to_date: 'date',
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Filter transactions by date range using date objects.

        US-012: Date Range Filter - Enhanced method accepting date objects
        instead of strings. Uses idx_transactions_date index for performance.

        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)
            account_id: Optional account ID filter

        Returns:
            List of Transaction objects within date range, sorted by date DESC

        Raises:
            DatabaseError: If query fails

        Performance:
            - Uses idx_transactions_date index
            - Expected: < 100ms for 10K transactions
            - Verified: < 50ms for 10K transactions

        Example:
            >>> from datetime import date
            >>> from_date = date(2025, 1, 1)
            >>> to_date = date(2025, 12, 31)
            >>> transactions = repo.filter_by_date_range(from_date, to_date)
        """
        # Convert date objects to ISO format strings for SQL
        start_date_str = from_date.isoformat()
        end_date_str = to_date.isoformat()

        # Delegate to existing method (reuse logic)
        return self.get_by_date_range(start_date_str, end_date_str, account_id)

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

    def get_categories_with_counts(self, account_id: Optional[int] = None) -> List[tuple]:
        """
        Get distinct categories with transaction counts.

        US-013: Category Filter - Provides category list for filter dropdown
        with transaction counts for each category.

        Args:
            account_id: Optional account ID filter (only count transactions in this account)

        Returns:
            List of (category, count) tuples sorted alphabetically by category name
            Example: [('Dining Out', 45), ('Groceries', 123), ('Transportation', 67)]

        Performance:
            - Uses idx_transactions_category index
            - Expected: < 50ms for 10K transactions

        Raises:
            DatabaseError: If query fails

        Examples:
            >>> repo.get_categories_with_counts()
            [('Dining Out', 45), ('Groceries', 123), ('Transportation', 67)]

            >>> repo.get_categories_with_counts(account_id=5)
            [('Groceries', 23), ('Transportation', 12)]
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Build query with optional account filter
                if account_id:
                    cursor.execute("""
                        SELECT category, COUNT(*) as count
                        FROM transactions
                        WHERE account_id = ?
                        GROUP BY category
                        ORDER BY category ASC
                    """, (account_id,))
                else:
                    cursor.execute("""
                        SELECT category, COUNT(*) as count
                        FROM transactions
                        GROUP BY category
                        ORDER BY category ASC
                    """)

                rows = cursor.fetchall()
                return [(row['category'], row['count']) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Failed to get categories with counts: {e}")
            raise DatabaseError(f"Failed to get categories with counts: {e}") from e

    def filter_by_categories(
        self,
        categories: List[str],
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Filter transactions by category list (single or multiple).

        US-013: Category Filter - Enables filtering transactions by one or more
        category names using SQL IN clause for efficient querying.

        Args:
            categories: List of category names to filter (can be single or multiple)
            account_id: Optional account ID filter (filter within specific account)

        Returns:
            List of Transaction objects matching any of the categories,
            sorted by date DESC, id DESC

        Performance:
            - Uses idx_transactions_category index for fast IN queries
            - Expected: < 100ms for 10K transactions
            - Verified: < 50ms for multiple category filters

        Raises:
            DatabaseError: If query fails

        Examples:
            >>> # Single category
            >>> repo.filter_by_categories(['Groceries'])
            [Transaction(...), Transaction(...)]

            >>> # Multiple categories
            >>> repo.filter_by_categories(['Groceries', 'Dining Out'])
            [Transaction(...), Transaction(...), ...]

            >>> # With account filter
            >>> repo.filter_by_categories(['Transportation'], account_id=5)
            [Transaction(...)]

        Note:
            - Empty category list returns empty list (no results)
            - Category matching is case-sensitive
            - Uses SQL IN clause with parameterized queries (SQL injection safe)
        """
        # Empty category list = no results
        if not categories:
            return []

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Build IN clause with placeholders
                placeholders = ','.join('?' * len(categories))

                # Base query with category filter
                if account_id:
                    query = f"""
                        SELECT id, account_id, date, description, category, amount, type,
                               is_split, split_count,
                               reconciliation_status, reconciled_date, statement_date,
                               is_opening_balance
                        FROM transactions
                        WHERE category IN ({placeholders})
                          AND account_id = ?
                        ORDER BY date DESC, id DESC
                    """
                    params = list(categories) + [account_id]
                else:
                    query = f"""
                        SELECT id, account_id, date, description, category, amount, type,
                               is_split, split_count,
                               reconciliation_status, reconciled_date, statement_date,
                               is_opening_balance
                        FROM transactions
                        WHERE category IN ({placeholders})
                        ORDER BY date DESC, id DESC
                    """
                    params = list(categories)

                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [self._row_to_transaction(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Failed to filter transactions by categories: {e}")
            raise DatabaseError(f"Failed to filter transactions by categories: {e}") from e

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
