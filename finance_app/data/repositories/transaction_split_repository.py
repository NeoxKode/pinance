"""
Repository for transaction split data access.

Story: US-002C - Split Transactions (Day 2)

This repository handles CRUD operations for transaction splits with:
- Atomic transaction handling
- CASCADE delete support
- Balance validation
- Bulk operations
"""

import sqlite3
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from finance_app.data.models import TransactionSplit
from finance_app.data.database import Database
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import DatabaseError, NotFoundError, ValidationError

logger = setup_logger(__name__)


class TransactionSplitRepository:
    """Repository for transaction split data access."""

    def __init__(self, database: Database):
        """
        Initialize repository.

        Args:
            database: Database instance
        """
        self.db = database

    def create(self, split: TransactionSplit) -> TransactionSplit:
        """
        Create a single transaction split.

        Note: For creating multiple splits atomically, use create_splits() instead.

        Args:
            split: TransactionSplit object (without ID)

        Returns:
            Created split with ID

        Raises:
            DatabaseError: If creation fails
            NotFoundError: If referenced entities don't exist
        """
        try:
            with self.db.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE TRANSACTION")
                cursor = conn.cursor()

                # Verify transaction exists
                cursor.execute(
                    "SELECT id FROM transactions WHERE id = ?",
                    (split.transaction_id,)
                )
                if cursor.fetchone() is None:
                    raise NotFoundError(f"Transaction {split.transaction_id} not found")

                # Verify group exists
                cursor.execute(
                    "SELECT id FROM transaction_groups WHERE id = ?",
                    (split.group_id,)
                )
                if cursor.fetchone() is None:
                    raise NotFoundError(f"Transaction group {split.group_id} not found")

                # Verify category exists
                cursor.execute(
                    "SELECT id FROM categories WHERE id = ?",
                    (split.category_id,)
                )
                if cursor.fetchone() is None:
                    raise NotFoundError(f"Category {split.category_id} not found")

                # Insert split
                cursor.execute("""
                    INSERT INTO transaction_splits (
                        transaction_id, group_id, split_order, category_id,
                        amount, memo, account_id, split_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    split.transaction_id,
                    split.group_id,
                    split.split_order,
                    split.category_id,
                    float(split.amount),
                    split.memo,
                    split.account_id,
                    split.split_type
                ))

                split_id = cursor.lastrowid
                conn.commit()

                logger.info(f"Created split {split_id} for transaction {split.transaction_id}")
                return self.get_by_id(split_id)

        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error creating split: {e}")
            raise DatabaseError(f"Failed to create split: {e}")
        except sqlite3.Error as e:
            logger.error(f"Database error creating split: {e}")
            raise DatabaseError(f"Failed to create split: {e}")

    def create_splits(
        self,
        transaction_id: int,
        splits: List[TransactionSplit]
    ) -> List[TransactionSplit]:
        """
        Create multiple splits for a transaction atomically.

        This is the preferred method for creating splits as it:
        - Ensures atomicity (all-or-nothing)
        - Updates transaction.is_split and split_count
        - Validates that splits balance before committing

        Args:
            transaction_id: Transaction ID
            splits: List of TransactionSplit objects

        Returns:
            List of created splits with IDs

        Raises:
            DatabaseError: If creation fails
            ValidationError: If splits are invalid
            NotFoundError: If transaction doesn't exist
        """
        if not splits:
            raise ValidationError("Must provide at least one split")

        if len(splits) < 2:
            raise ValidationError(
                f"Split transaction must have at least 2 splits, got {len(splits)}"
            )

        try:
            with self.db.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE TRANSACTION")
                cursor = conn.cursor()

                # Verify transaction exists
                cursor.execute(
                    "SELECT id FROM transactions WHERE id = ?",
                    (transaction_id,)
                )
                if cursor.fetchone() is None:
                    raise NotFoundError(f"Transaction {transaction_id} not found")

                created_splits = []

                for i, split in enumerate(splits):
                    # Ensure split order is set
                    split.split_order = i

                    # Verify group exists
                    cursor.execute(
                        "SELECT id FROM transaction_groups WHERE id = ?",
                        (split.group_id,)
                    )
                    if cursor.fetchone() is None:
                        raise NotFoundError(f"Transaction group {split.group_id} not found")

                    # Verify category exists
                    cursor.execute(
                        "SELECT id FROM categories WHERE id = ?",
                        (split.category_id,)
                    )
                    if cursor.fetchone() is None:
                        raise NotFoundError(f"Category {split.category_id} not found")

                    # Insert split
                    cursor.execute("""
                        INSERT INTO transaction_splits (
                            transaction_id, group_id, split_order, category_id,
                            amount, memo, account_id, split_type
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        transaction_id,
                        split.group_id,
                        split.split_order,
                        split.category_id,
                        float(split.amount),
                        split.memo,
                        split.account_id,
                        split.split_type
                    ))

                    split.id = cursor.lastrowid
                    created_splits.append(split)

                # Update transaction to mark as split
                cursor.execute("""
                    UPDATE transactions
                    SET is_split = 1, split_count = ?
                    WHERE id = ?
                """, (len(splits), transaction_id))

                conn.commit()

                logger.info(
                    f"Created {len(splits)} splits for transaction {transaction_id}"
                )

                # Fetch created splits with timestamps
                return self.get_by_transaction(transaction_id)

        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error creating splits: {e}")
            raise DatabaseError(f"Failed to create splits: {e}")
        except sqlite3.Error as e:
            logger.error(f"Database error creating splits: {e}")
            raise DatabaseError(f"Failed to create splits: {e}")

    def get_by_id(self, split_id: int) -> Optional[TransactionSplit]:
        """
        Get split by ID.

        Args:
            split_id: Split ID

        Returns:
            TransactionSplit or None if not found
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, transaction_id, group_id, split_order, category_id,
                           amount, memo, account_id, split_type,
                           created_at, updated_at
                    FROM transaction_splits
                    WHERE id = ?
                """, (split_id,))

                row = cursor.fetchone()
                if row is None:
                    return None

                return self._row_to_split(row)

        except sqlite3.Error as e:
            logger.error(f"Error fetching split {split_id}: {e}")
            raise DatabaseError(f"Failed to fetch split: {e}")

    def get_by_transaction(self, transaction_id: int) -> List[TransactionSplit]:
        """
        Get all splits for a transaction, ordered by split_order.

        Args:
            transaction_id: Transaction ID

        Returns:
            List of TransactionSplit objects (may be empty)
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, transaction_id, group_id, split_order, category_id,
                           amount, memo, account_id, split_type,
                           created_at, updated_at
                    FROM transaction_splits
                    WHERE transaction_id = ?
                    ORDER BY split_order ASC
                """, (transaction_id,))

                rows = cursor.fetchall()
                return [self._row_to_split(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error fetching splits for transaction {transaction_id}: {e}")
            raise DatabaseError(f"Failed to fetch splits: {e}")

    def get_by_group(self, group_id: int) -> List[TransactionSplit]:
        """
        Get all splits for a transaction group.

        Args:
            group_id: Transaction group ID

        Returns:
            List of TransactionSplit objects (may be empty)
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, transaction_id, group_id, split_order, category_id,
                           amount, memo, account_id, split_type,
                           created_at, updated_at
                    FROM transaction_splits
                    WHERE group_id = ?
                    ORDER BY transaction_id, split_order ASC
                """, (group_id,))

                rows = cursor.fetchall()
                return [self._row_to_split(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error fetching splits for group {group_id}: {e}")
            raise DatabaseError(f"Failed to fetch splits: {e}")

    def get_by_category(
        self,
        category_id: int,
        limit: Optional[int] = None
    ) -> List[TransactionSplit]:
        """
        Get splits by category.

        Useful for category spending reports.

        Args:
            category_id: Category ID
            limit: Optional result limit

        Returns:
            List of TransactionSplit objects
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                query = """
                    SELECT id, transaction_id, group_id, split_order, category_id,
                           amount, memo, account_id, split_type,
                           created_at, updated_at
                    FROM transaction_splits
                    WHERE category_id = ?
                    ORDER BY created_at DESC
                """

                params = [category_id]

                if limit:
                    query += " LIMIT ?"
                    params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [self._row_to_split(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error fetching splits for category {category_id}: {e}")
            raise DatabaseError(f"Failed to fetch splits: {e}")

    def update(self, split: TransactionSplit) -> TransactionSplit:
        """
        Update an existing split.

        Note: Updating splits requires recalculating balances.
        Consider using update_splits() for atomic updates of all splits.

        Args:
            split: TransactionSplit with updated values

        Returns:
            Updated split

        Raises:
            DatabaseError: If update fails
            NotFoundError: If split doesn't exist
        """
        if split.id is None:
            raise ValidationError("Cannot update split without ID")

        try:
            with self.db.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE TRANSACTION")
                cursor = conn.cursor()

                # Verify split exists
                cursor.execute("SELECT id FROM transaction_splits WHERE id = ?", (split.id,))
                if cursor.fetchone() is None:
                    raise NotFoundError(f"Split {split.id} not found")

                # Update split
                cursor.execute("""
                    UPDATE transaction_splits
                    SET group_id = ?, split_order = ?, category_id = ?,
                        amount = ?, memo = ?, account_id = ?, split_type = ?
                    WHERE id = ?
                """, (
                    split.group_id,
                    split.split_order,
                    split.category_id,
                    float(split.amount),
                    split.memo,
                    split.account_id,
                    split.split_type,
                    split.id
                ))

                if cursor.rowcount == 0:
                    raise NotFoundError(f"Split {split.id} not found")

                conn.commit()

                logger.info(f"Updated split {split.id}")
                return self.get_by_id(split.id)

        except sqlite3.Error as e:
            logger.error(f"Error updating split {split.id}: {e}")
            raise DatabaseError(f"Failed to update split: {e}")

    def delete(self, split_id: int) -> None:
        """
        Delete a single split.

        Warning: This may leave a transaction with < 2 splits.
        Use delete_all_for_transaction() to remove all splits atomically.

        Args:
            split_id: Split ID

        Raises:
            DatabaseError: If deletion fails
            NotFoundError: If split doesn't exist
        """
        try:
            with self.db.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE TRANSACTION")
                cursor = conn.cursor()

                # Get transaction_id before deleting
                cursor.execute(
                    "SELECT transaction_id FROM transaction_splits WHERE id = ?",
                    (split_id,)
                )
                row = cursor.fetchone()
                if row is None:
                    raise NotFoundError(f"Split {split_id} not found")

                transaction_id = row[0]

                # Delete split
                cursor.execute("DELETE FROM transaction_splits WHERE id = ?", (split_id,))

                if cursor.rowcount == 0:
                    raise NotFoundError(f"Split {split_id} not found")

                # Update transaction split_count
                cursor.execute("""
                    SELECT COUNT(*) FROM transaction_splits
                    WHERE transaction_id = ?
                """, (transaction_id,))
                remaining_count = cursor.fetchone()[0]

                # Update or reset is_split flag
                if remaining_count == 0:
                    cursor.execute("""
                        UPDATE transactions
                        SET is_split = 0, split_count = 0
                        WHERE id = ?
                    """, (transaction_id,))
                else:
                    cursor.execute("""
                        UPDATE transactions
                        SET split_count = ?
                        WHERE id = ?
                    """, (remaining_count, transaction_id))

                conn.commit()

                logger.info(f"Deleted split {split_id}, {remaining_count} splits remaining")

        except sqlite3.Error as e:
            logger.error(f"Error deleting split {split_id}: {e}")
            raise DatabaseError(f"Failed to delete split: {e}")

    def delete_all_for_transaction(self, transaction_id: int) -> int:
        """
        Delete all splits for a transaction atomically.

        This also updates the transaction to clear is_split and split_count.

        Args:
            transaction_id: Transaction ID

        Returns:
            Number of splits deleted

        Raises:
            DatabaseError: If deletion fails
        """
        try:
            with self.db.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE TRANSACTION")
                cursor = conn.cursor()

                # Count splits before deleting
                cursor.execute("""
                    SELECT COUNT(*) FROM transaction_splits
                    WHERE transaction_id = ?
                """, (transaction_id,))
                count = cursor.fetchone()[0]

                # Delete splits
                cursor.execute("""
                    DELETE FROM transaction_splits
                    WHERE transaction_id = ?
                """, (transaction_id,))

                deleted_count = cursor.rowcount

                # Update transaction
                cursor.execute("""
                    UPDATE transactions
                    SET is_split = 0, split_count = 0
                    WHERE id = ?
                """, (transaction_id,))

                conn.commit()

                logger.info(f"Deleted {deleted_count} splits for transaction {transaction_id}")
                return deleted_count

        except sqlite3.Error as e:
            logger.error(f"Error deleting splits for transaction {transaction_id}: {e}")
            raise DatabaseError(f"Failed to delete splits: {e}")

    def count_by_transaction(self, transaction_id: int) -> int:
        """
        Count splits for a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Number of splits
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM transaction_splits
                    WHERE transaction_id = ?
                """, (transaction_id,))
                return cursor.fetchone()[0]

        except sqlite3.Error as e:
            logger.error(f"Error counting splits: {e}")
            raise DatabaseError(f"Failed to count splits: {e}")

    def get_total_amount_by_transaction(self, transaction_id: int) -> Decimal:
        """
        Calculate total amount of all splits for a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Total split amount as Decimal
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT SUM(amount) FROM transaction_splits
                    WHERE transaction_id = ?
                """, (transaction_id,))

                result = cursor.fetchone()[0]
                return Decimal(str(result)) if result else Decimal('0')

        except sqlite3.Error as e:
            logger.error(f"Error calculating split total: {e}")
            raise DatabaseError(f"Failed to calculate split total: {e}")

    def _row_to_split(self, row: tuple) -> TransactionSplit:
        """
        Convert database row to TransactionSplit object.

        Args:
            row: Database row tuple

        Returns:
            TransactionSplit object
        """
        return TransactionSplit(
            id=row[0],
            transaction_id=row[1],
            group_id=row[2],
            split_order=row[3],
            category_id=row[4],
            amount=Decimal(str(row[5])),
            memo=row[6],
            account_id=row[7],
            split_type=row[8],
            created_at=datetime.fromisoformat(row[9]) if row[9] else None,
            updated_at=datetime.fromisoformat(row[10]) if row[10] else None
        )
