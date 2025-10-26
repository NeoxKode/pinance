"""
Repository for reconciliation data access.

Story: US-004 - Account Reconciliation (Day 1)
"""
import sqlite3
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from finance_app.data.models import Reconciliation
from finance_app.data.database import Database
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import DatabaseError, NotFoundError, ValidationError

logger = setup_logger(__name__)


class ReconciliationRepository:
    """
    Repository for reconciliation data access.

    Provides CRUD operations for reconciliation records with immutability enforcement.

    Key Methods:
    - create(): Save completed reconciliation
    - get_by_id(): Fetch single reconciliation
    - get_by_account(): Get reconciliation history for account
    - get_last_reconciliation(): Get most recent reconciliation
    - get_pending_reconciliation(): Check for active reconciliation (concurrency)

    Critical Fix from Tech Review:
    - Added get_pending_reconciliation() for concurrency prevention
    """

    def __init__(self, database: Database):
        """
        Initialize repository.

        Args:
            database: Database instance
        """
        self.db = database

    def create(self, reconciliation: Reconciliation) -> Reconciliation:
        """
        Create a new reconciliation record.

        Reconciliation records are IMMUTABLE once created (audit trail).

        Args:
            reconciliation: Reconciliation object (without ID)

        Returns:
            Created reconciliation with ID and timestamp

        Raises:
            DatabaseError: If creation fails
            ValidationError: If reconciliation data is invalid
        """
        # Validation
        if reconciliation.transaction_count < 0:
            raise ValidationError("Transaction count cannot be negative")

        if not reconciliation.reconciliation_date:
            raise ValidationError("Reconciliation date is required")

        if not reconciliation.statement_date:
            raise ValidationError("Statement date is required")

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Get current timestamp for created_at
                current_timestamp = datetime.now().isoformat()

                cursor.execute("""
                    INSERT INTO reconciliations (
                        account_id, reconciliation_date, statement_date,
                        statement_balance, cleared_balance, discrepancy,
                        transaction_count, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    reconciliation.account_id,
                    reconciliation.reconciliation_date,
                    reconciliation.statement_date,
                    float(reconciliation.statement_balance),
                    float(reconciliation.cleared_balance),
                    float(reconciliation.discrepancy),
                    reconciliation.transaction_count,
                    reconciliation.notes,
                    current_timestamp
                ))

                reconciliation_id = cursor.lastrowid
                conn.commit()

                logger.info(
                    f"Created reconciliation {reconciliation_id} for account {reconciliation.account_id}: "
                    f"statement=${reconciliation.statement_balance}, "
                    f"cleared=${reconciliation.cleared_balance}, "
                    f"discrepancy=${reconciliation.discrepancy}"
                )

                # Fetch the created reconciliation to get all fields
                return self.get_by_id(reconciliation_id)

        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to create reconciliation (integrity error): {e}")
            raise ValidationError(f"Failed to create reconciliation: {e}") from e
        except sqlite3.Error as e:
            logger.error(f"Failed to create reconciliation: {e}")
            raise DatabaseError(f"Failed to create reconciliation: {e}") from e

    def get_by_id(self, reconciliation_id: int) -> Optional[Reconciliation]:
        """
        Get reconciliation by ID.

        Args:
            reconciliation_id: Reconciliation ID

        Returns:
            Reconciliation object or None if not found

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, account_id, reconciliation_date, statement_date,
                           statement_balance, cleared_balance, discrepancy,
                           transaction_count, notes, created_at
                    FROM reconciliations
                    WHERE id = ?
                """, (reconciliation_id,))

                row = cursor.fetchone()
                return self._row_to_reconciliation(row) if row else None

        except sqlite3.Error as e:
            logger.error(f"Failed to fetch reconciliation {reconciliation_id}: {e}")
            raise DatabaseError(f"Failed to fetch reconciliation: {e}") from e

    def get_by_account(
        self,
        account_id: int,
        limit: Optional[int] = None
    ) -> List[Reconciliation]:
        """
        Get reconciliation history for an account.

        Returns reconciliations ordered by reconciliation_date DESC (most recent first).

        Args:
            account_id: Account ID
            limit: Optional limit on number of results (default: all)

        Returns:
            List of Reconciliation objects (newest first)

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Build query with optional limit
                query = """
                    SELECT id, account_id, reconciliation_date, statement_date,
                           statement_balance, cleared_balance, discrepancy,
                           transaction_count, notes, created_at
                    FROM reconciliations
                    WHERE account_id = ?
                    ORDER BY reconciliation_date DESC, statement_date DESC, id DESC
                """

                params = [account_id]

                if limit is not None:
                    query += " LIMIT ?"
                    params.append(limit)

                cursor.execute(query, params)

                rows = cursor.fetchall()
                return [self._row_to_reconciliation(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Failed to fetch reconciliations for account {account_id}: {e}")
            raise DatabaseError(f"Failed to fetch reconciliations: {e}") from e

    def get_last_reconciliation(self, account_id: int) -> Optional[Reconciliation]:
        """
        Get the most recent reconciliation for an account.

        Useful for calculating opening balance for next reconciliation.

        Args:
            account_id: Account ID

        Returns:
            Most recent Reconciliation or None if never reconciled

        Raises:
            DatabaseError: If query fails
        """
        reconciliations = self.get_by_account(account_id, limit=1)
        return reconciliations[0] if reconciliations else None

    def get_pending_reconciliation(self, account_id: int) -> bool:
        """
        Check if account has a pending/active reconciliation.

        CRITICAL FIX from Tech Review:
        This prevents concurrent reconciliations on the same account.
        A reconciliation is "pending" if there are transactions with status='pending'.

        Args:
            account_id: Account ID

        Returns:
            True if reconciliation is in progress, False otherwise

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Check for any transactions with reconciliation_status='pending'
                cursor.execute("""
                    SELECT COUNT(*) as pending_count
                    FROM transactions
                    WHERE account_id = ? AND reconciliation_status = 'pending'
                """, (account_id,))

                row = cursor.fetchone()
                pending_count = row[0] if row else 0

                has_pending = pending_count > 0

                if has_pending:
                    logger.warning(
                        f"Account {account_id} has {pending_count} pending transactions "
                        f"(reconciliation already in progress)"
                    )

                return has_pending

        except sqlite3.Error as e:
            logger.error(f"Failed to check pending reconciliation for account {account_id}: {e}")
            raise DatabaseError(f"Failed to check pending reconciliation: {e}") from e

    def _row_to_reconciliation(self, row: sqlite3.Row) -> Reconciliation:
        """
        Convert database row to Reconciliation object.

        Args:
            row: SQLite row object

        Returns:
            Reconciliation object
        """
        return Reconciliation(
            id=row[0],
            account_id=row[1],
            reconciliation_date=row[2],
            statement_date=row[3],
            statement_balance=Decimal(str(row[4])),
            cleared_balance=Decimal(str(row[5])),
            discrepancy=Decimal(str(row[6])),
            transaction_count=row[7],
            notes=row[8],
            created_at=row[9]
        )
