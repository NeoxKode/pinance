"""
Repository for transaction group data access.

Story: US-002B - Balanced Transaction Groups (Phase 2)
"""
import sqlite3
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from finance_app.data.models import TransactionGroup
from finance_app.data.database import Database
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import DatabaseError, NotFoundError, ValidationError

logger = setup_logger(__name__)


class TransactionGroupRepository:
    """Repository for transaction group data access."""

    def __init__(self, database: Database):
        """
        Initialize repository.

        Args:
            database: Database instance
        """
        self.db = database

    def create(self, group: TransactionGroup) -> TransactionGroup:
        """
        Create a new transaction group.

        Args:
            group: TransactionGroup object (without ID)

        Returns:
            Created transaction group with ID

        Raises:
            DatabaseError: If creation fails
            ValidationError: If group is not balanced
        """
        # Validate balance before insert
        if group.total_debits != group.total_credits:
            raise ValidationError(
                f"Transaction group must be balanced: "
                f"debits ({group.total_debits}) != credits ({group.total_credits})"
            )

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO transaction_groups (
                        group_date, description, notes,
                        total_debits, total_credits, is_balanced
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    group.group_date,
                    group.description,
                    group.notes,
                    float(group.total_debits),
                    float(group.total_credits),
                    1 if group.is_balanced else 0
                ))

                group_id = cursor.lastrowid
                conn.commit()

                logger.info(f"Created transaction group {group_id}: {group.description}")

                # Fetch the created group to get timestamps
                return self.get_by_id(group_id)

        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to create transaction group (integrity error): {e}")
            raise ValidationError(f"Failed to create transaction group: {e}") from e
        except sqlite3.Error as e:
            logger.error(f"Failed to create transaction group: {e}")
            raise DatabaseError(f"Failed to create transaction group: {e}") from e

    def get_by_id(self, group_id: int) -> Optional[TransactionGroup]:
        """
        Get transaction group by ID.

        Args:
            group_id: Transaction group ID

        Returns:
            TransactionGroup object or None if not found

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, group_date, description, notes,
                           total_debits, total_credits, is_balanced,
                           created_at, updated_at
                    FROM transaction_groups
                    WHERE id = ?
                """, (group_id,))
                row = cursor.fetchone()
                return self._row_to_group(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch transaction group {group_id}: {e}")
            raise DatabaseError(f"Failed to fetch transaction group: {e}") from e

    def get_all(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[TransactionGroup]:
        """
        Get all transaction groups with optional date filtering.

        Args:
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            limit: Optional limit on number of results

        Returns:
            List of TransactionGroup objects ordered by date DESC

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Build query with optional filters
                query = """
                    SELECT id, group_date, description, notes,
                           total_debits, total_credits, is_balanced,
                           created_at, updated_at
                    FROM transaction_groups
                """
                params = []

                # Add date filters
                conditions = []
                if start_date:
                    conditions.append("group_date >= ?")
                    params.append(start_date)
                if end_date:
                    conditions.append("group_date <= ?")
                    params.append(end_date)

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                query += " ORDER BY group_date DESC, id DESC"

                if limit:
                    query += " LIMIT ?"
                    params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [self._row_to_group(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Failed to fetch transaction groups: {e}")
            raise DatabaseError(f"Failed to fetch transaction groups: {e}") from e

    def update(self, group: TransactionGroup) -> TransactionGroup:
        """
        Update an existing transaction group.

        Args:
            group: TransactionGroup object with ID

        Returns:
            Updated transaction group

        Raises:
            DatabaseError: If update fails
            NotFoundError: If group not found
            ValidationError: If group is not balanced
        """
        if group.id is None:
            raise ValueError("Transaction group ID is required for update")

        # Validate balance before update
        if group.total_debits != group.total_credits:
            raise ValidationError(
                f"Transaction group must be balanced: "
                f"debits ({group.total_debits}) != credits ({group.total_credits})"
            )

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE transaction_groups
                    SET group_date = ?,
                        description = ?,
                        notes = ?,
                        total_debits = ?,
                        total_credits = ?,
                        is_balanced = ?
                    WHERE id = ?
                """, (
                    group.group_date,
                    group.description,
                    group.notes,
                    float(group.total_debits),
                    float(group.total_credits),
                    1 if group.is_balanced else 0,
                    group.id
                ))

                if cursor.rowcount == 0:
                    raise NotFoundError(f"Transaction group {group.id} not found")

                conn.commit()
                logger.info(f"Updated transaction group {group.id}")

                return self.get_by_id(group.id)

        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to update transaction group (integrity error): {e}")
            raise ValidationError(f"Failed to update transaction group: {e}") from e
        except sqlite3.Error as e:
            logger.error(f"Failed to update transaction group {group.id}: {e}")
            raise DatabaseError(f"Failed to update transaction group: {e}") from e

    def delete(self, group_id: int) -> None:
        """
        Delete a transaction group.

        Note: This will also set group_id to NULL for all associated journal entries
        (assuming ON DELETE SET NULL foreign key, or handle programmatically).

        Args:
            group_id: Transaction group ID to delete

        Raises:
            DatabaseError: If deletion fails
            NotFoundError: If group not found
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # First, unlink journal entries from this group
                cursor.execute("""
                    UPDATE journal_entries
                    SET group_id = NULL
                    WHERE group_id = ?
                """, (group_id,))

                # Then delete the group
                cursor.execute("DELETE FROM transaction_groups WHERE id = ?", (group_id,))

                if cursor.rowcount == 0:
                    raise NotFoundError(f"Transaction group {group_id} not found")

                conn.commit()
                logger.info(f"Deleted transaction group {group_id}")

        except sqlite3.Error as e:
            logger.error(f"Failed to delete transaction group {group_id}: {e}")
            raise DatabaseError(f"Failed to delete transaction group: {e}") from e

    def get_unbalanced_groups(self) -> List[TransactionGroup]:
        """
        Get all unbalanced transaction groups (should be none in a healthy system).

        Returns:
            List of unbalanced TransactionGroup objects

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, group_date, description, notes,
                           total_debits, total_credits, is_balanced,
                           created_at, updated_at
                    FROM transaction_groups
                    WHERE is_balanced = 0 OR total_debits != total_credits
                    ORDER BY group_date DESC
                """)
                rows = cursor.fetchall()
                return [self._row_to_group(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Failed to fetch unbalanced groups: {e}")
            raise DatabaseError(f"Failed to fetch unbalanced groups: {e}") from e

    def _row_to_group(self, row) -> TransactionGroup:
        """
        Convert database row to TransactionGroup object.

        Args:
            row: Database row

        Returns:
            TransactionGroup object
        """
        return TransactionGroup(
            id=row[0],
            group_date=row[1],
            description=row[2],
            notes=row[3],
            total_debits=Decimal(str(row[4])),
            total_credits=Decimal(str(row[5])),
            is_balanced=bool(row[6]),
            created_at=datetime.fromisoformat(row[7]) if row[7] else None,
            updated_at=datetime.fromisoformat(row[8]) if row[8] else None
        )
