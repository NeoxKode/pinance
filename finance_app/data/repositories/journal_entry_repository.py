"""
Repository for journal entry data access.
Story: US-002A - Journal Entry Foundation
Story: US-002B - Balanced Transaction Groups (create_balanced_group method)
"""
import sqlite3
from decimal import Decimal
from typing import List, Optional, Tuple
from datetime import datetime

from finance_app.data.models import JournalEntry, EntryType, TransactionGroup
from finance_app.data.database import Database
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import DatabaseError, NotFoundError, ValidationError

logger = setup_logger(__name__)


class JournalEntryRepository:
    """Repository for journal entry data access."""

    def __init__(self, database: Database):
        """
        Initialize repository.

        Args:
            database: Database instance
        """
        self.db = database

    def create(self, entry: JournalEntry) -> JournalEntry:
        """
        Create a new journal entry.

        CRITICAL: This method calculates balance_after BEFORE inserting the entry.
        The triggers will then update the account balance automatically.

        Args:
            entry: JournalEntry object (without ID)

        Returns:
            Created journal entry with ID and calculated balance_after

        Raises:
            DatabaseError: If creation fails
        """
        try:
            with self.db.get_connection() as conn:
                # ⚠️ TECH LEAD NOTE: Use BEGIN IMMEDIATE to prevent race conditions
                conn.execute("BEGIN IMMEDIATE TRANSACTION")
                cursor = conn.cursor()

                # Calculate balance_after BEFORE insert
                cursor.execute(
                    "SELECT balance FROM accounts WHERE id = ?",
                    (entry.account_id,)
                )
                row = cursor.fetchone()
                if row is None:
                    raise NotFoundError(f"Account {entry.account_id} not found")

                # Convert to Decimal via string to avoid precision loss
                current_balance = Decimal(str(row[0]))

                # Calculate what balance will be AFTER this entry
                amount_change = entry.debit_amount - entry.credit_amount
                entry.balance_after = current_balance + amount_change

                # Now insert with calculated balance_after
                cursor.execute("""
                    INSERT INTO journal_entries (
                        transaction_id, group_id, account_id, entry_date,
                        description, debit_amount, credit_amount, balance_after,
                        entry_type, reference_number, is_reconciled,
                        reconciliation_id, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.transaction_id,
                    entry.group_id,
                    entry.account_id,
                    entry.entry_date,
                    entry.description,
                    float(entry.debit_amount),
                    float(entry.credit_amount),
                    float(entry.balance_after),
                    entry.entry_type.value,
                    entry.reference_number,
                    1 if entry.is_reconciled else 0,
                    entry.reconciliation_id,
                    entry.notes
                ))

                entry_id = cursor.lastrowid
                conn.commit()

                # Fetch the created entry to get timestamps
                return self.get_by_id(entry_id)

        except sqlite3.Error as e:
            logger.error(f"Failed to create journal entry: {e}")
            raise DatabaseError(f"Failed to create journal entry: {e}") from e

    def get_by_id(self, entry_id: int) -> Optional[JournalEntry]:
        """
        Get journal entry by ID.

        Args:
            entry_id: Journal entry ID

        Returns:
            JournalEntry object or None if not found

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, transaction_id, group_id, account_id, entry_date,
                           description, debit_amount, credit_amount, balance_after,
                           entry_type, reference_number, is_reconciled,
                           reconciliation_id, notes, created_at, updated_at
                    FROM journal_entries
                    WHERE id = ?
                """, (entry_id,))
                row = cursor.fetchone()
                return self._row_to_entry(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch journal entry {entry_id}: {e}")
            raise DatabaseError(f"Failed to fetch journal entry: {e}") from e

    def get_by_account(
        self,
        account_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[JournalEntry]:
        """
        Get journal entries for an account with optional date filtering.

        Args:
            account_id: Account ID
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            limit: Optional limit on number of results

        Returns:
            List of JournalEntry objects ordered by date DESC

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Build query with optional filters
                query = """
                    SELECT id, transaction_id, group_id, account_id, entry_date,
                           description, debit_amount, credit_amount, balance_after,
                           entry_type, reference_number, is_reconciled,
                           reconciliation_id, notes, created_at, updated_at
                    FROM journal_entries
                    WHERE account_id = ?
                """
                params = [account_id]

                if start_date:
                    query += " AND entry_date >= ?"
                    params.append(start_date)

                if end_date:
                    query += " AND entry_date <= ?"
                    params.append(end_date)

                query += " ORDER BY entry_date DESC, id DESC"

                if limit:
                    query += " LIMIT ?"
                    params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [self._row_to_entry(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Failed to fetch journal entries for account {account_id}: {e}")
            raise DatabaseError(f"Failed to fetch journal entries: {e}") from e

    def get_account_balance(self, account_id: int, as_of_date: Optional[str] = None) -> Decimal:
        """
        Calculate account balance from journal entries.

        This is the authoritative balance calculation from the journal.
        The cached balance in accounts table should match this.

        Args:
            account_id: Account ID
            as_of_date: Optional date to calculate balance as of (YYYY-MM-DD)

        Returns:
            Account balance as Decimal

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                if as_of_date:
                    cursor.execute("""
                        SELECT SUM(debit_amount - credit_amount)
                        FROM journal_entries
                        WHERE account_id = ? AND entry_date <= ?
                    """, (account_id, as_of_date))
                else:
                    cursor.execute("""
                        SELECT SUM(debit_amount - credit_amount)
                        FROM journal_entries
                        WHERE account_id = ?
                    """, (account_id,))

                result = cursor.fetchone()[0]
                return Decimal(str(result)) if result is not None else Decimal("0")

        except sqlite3.Error as e:
            logger.error(f"Failed to calculate balance for account {account_id}: {e}")
            raise DatabaseError(f"Failed to calculate balance: {e}") from e

    def update(self, entry: JournalEntry) -> JournalEntry:
        """
        Update an existing journal entry.

        ⚠️ WARNING: Updating journal entries can affect account balances.
        The triggers will automatically adjust the account balance.

        Args:
            entry: JournalEntry object with ID

        Returns:
            Updated journal entry

        Raises:
            DatabaseError: If update fails
            NotFoundError: If entry not found
        """
        if entry.id is None:
            raise ValueError("Journal entry ID is required for update")

        try:
            with self.db.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE TRANSACTION")
                cursor = conn.cursor()

                # Recalculate balance_after if amounts changed
                # Get the account balance before this entry
                cursor.execute("""
                    SELECT account_id, entry_date
                    FROM journal_entries
                    WHERE id = ?
                """, (entry.id,))
                old_row = cursor.fetchone()
                if old_row is None:
                    raise NotFoundError(f"Journal entry {entry.id} not found")

                # Calculate balance up to (but not including) this entry
                cursor.execute("""
                    SELECT SUM(debit_amount - credit_amount)
                    FROM journal_entries
                    WHERE account_id = ? AND (
                        entry_date < ? OR (entry_date = ? AND id < ?)
                    )
                """, (entry.account_id, entry.entry_date, entry.entry_date, entry.id))

                balance_before = cursor.fetchone()[0]
                balance_before = Decimal(str(balance_before)) if balance_before else Decimal("0")

                # Add current account's base balance (from account table before any journal entries)
                cursor.execute("SELECT balance FROM accounts WHERE id = ?", (entry.account_id,))
                current_balance = Decimal(str(cursor.fetchone()[0]))

                # Recalculate balance_after
                amount_change = entry.debit_amount - entry.credit_amount
                entry.balance_after = balance_before + amount_change

                # Update the entry (account_id included for trigger to catch changes)
                cursor.execute("""
                    UPDATE journal_entries
                    SET account_id = ?,
                        entry_date = ?,
                        description = ?,
                        debit_amount = ?,
                        credit_amount = ?,
                        balance_after = ?,
                        reference_number = ?,
                        is_reconciled = ?,
                        reconciliation_id = ?,
                        notes = ?
                    WHERE id = ?
                """, (
                    entry.account_id,
                    entry.entry_date,
                    entry.description,
                    float(entry.debit_amount),
                    float(entry.credit_amount),
                    float(entry.balance_after),
                    entry.reference_number,
                    1 if entry.is_reconciled else 0,
                    entry.reconciliation_id,
                    entry.notes,
                    entry.id
                ))

                if cursor.rowcount == 0:
                    raise NotFoundError(f"Journal entry {entry.id} not found")

                conn.commit()

                # Return updated entry
                return self.get_by_id(entry.id)

        except sqlite3.Error as e:
            logger.error(f"Failed to update journal entry {entry.id}: {e}")
            raise DatabaseError(f"Failed to update journal entry: {e}") from e

    def delete(self, entry_id: int) -> None:
        """
        Delete a journal entry.

        ⚠️ WARNING: Deleting journal entries affects account balances.
        The triggers will automatically reverse the balance change.

        Args:
            entry_id: Journal entry ID to delete

        Raises:
            DatabaseError: If deletion fails
            NotFoundError: If entry not found
        """
        try:
            with self.db.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE TRANSACTION")
                cursor = conn.cursor()

                cursor.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))

                if cursor.rowcount == 0:
                    raise NotFoundError(f"Journal entry {entry_id} not found")

                conn.commit()
                logger.info(f"Deleted journal entry {entry_id}")

        except sqlite3.Error as e:
            logger.error(f"Failed to delete journal entry {entry_id}: {e}")
            raise DatabaseError(f"Failed to delete journal entry: {e}") from e

    def create_balanced_group(
        self,
        entries: List[JournalEntry],
        group_date: str,
        description: str,
        notes: Optional[str] = None
    ) -> Tuple[TransactionGroup, List[JournalEntry]]:
        """
        Create a balanced group of journal entries atomically.

        This method ensures that:
        1. All entries are created together in a single transaction
        2. The sum of debits equals the sum of credits (balanced)
        3. All entries are linked to the same transaction group
        4. If any validation fails, entire operation rolls back

        Story: US-002B - Balanced Transaction Groups (Phase 2)

        Args:
            entries: List of JournalEntry objects (without IDs or group_id)
            group_date: Date for the transaction group (YYYY-MM-DD)
            description: Description for the transaction group
            notes: Optional notes for the transaction group

        Returns:
            Tuple of (TransactionGroup, List[JournalEntry]) - created group and entries

        Raises:
            ValidationError: If entries are not balanced or invalid
            DatabaseError: If creation fails

        Example:
            # Transfer $500 from Checking (ID=1) to Savings (ID=2)
            entries = [
                JournalEntry(
                    account_id=1,  # Checking
                    entry_date="2025-10-22",
                    description="Transfer to savings",
                    debit_amount=Decimal("0"),
                    credit_amount=Decimal("500"),  # Decrease asset
                    balance_after=Decimal("0"),  # Will be calculated
                    entry_type=EntryType.TRANSFER
                ),
                JournalEntry(
                    account_id=2,  # Savings
                    entry_date="2025-10-22",
                    description="Transfer from checking",
                    debit_amount=Decimal("500"),  # Increase asset
                    credit_amount=Decimal("0"),
                    balance_after=Decimal("0"),  # Will be calculated
                    entry_type=EntryType.TRANSFER
                )
            ]
            group, created_entries = repo.create_balanced_group(
                entries, "2025-10-22", "Transfer between accounts"
            )
        """
        # Validation: Must have at least 2 entries
        if len(entries) < 2:
            raise ValidationError(
                "Balanced group must have at least 2 journal entries"
            )

        # Validation: Calculate totals
        total_debits = sum(entry.debit_amount for entry in entries)
        total_credits = sum(entry.credit_amount for entry in entries)

        # Validation: Must be balanced
        if total_debits != total_credits:
            raise ValidationError(
                f"Journal entries must be balanced: "
                f"total debits ({total_debits}) != total credits ({total_credits})"
            )

        # Validation: All entries must have the same date
        if not all(entry.entry_date == entries[0].entry_date for entry in entries):
            raise ValidationError(
                "All journal entries in a group must have the same date"
            )

        try:
            from finance_app.data.repositories.transaction_group_repository import TransactionGroupRepository

            with self.db.get_connection() as conn:
                # Use IMMEDIATE transaction to prevent race conditions
                conn.execute("BEGIN IMMEDIATE TRANSACTION")
                cursor = conn.cursor()

                # Step 1: Create the transaction group
                group_repo = TransactionGroupRepository(self.db)
                group = TransactionGroup(
                    id=None,
                    group_date=group_date,
                    description=description,
                    notes=notes,
                    total_debits=total_debits,
                    total_credits=total_credits,
                    is_balanced=True
                )

                # Insert group (bypassing repo to stay in same transaction)
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
                logger.info(
                    f"Created transaction group {group_id}: {description} "
                    f"(debits={total_debits}, credits={total_credits})"
                )

                # Step 2: Create all journal entries with the group_id
                created_entries = []
                for entry in entries:
                    # Set the group_id
                    entry.group_id = group_id

                    # Calculate balance_after for this entry
                    cursor.execute(
                        "SELECT balance FROM accounts WHERE id = ?",
                        (entry.account_id,)
                    )
                    row = cursor.fetchone()
                    if row is None:
                        raise NotFoundError(f"Account {entry.account_id} not found")

                    current_balance = Decimal(str(row[0]))
                    amount_change = entry.debit_amount - entry.credit_amount
                    entry.balance_after = current_balance + amount_change

                    # Insert journal entry
                    cursor.execute("""
                        INSERT INTO journal_entries (
                            transaction_id, group_id, account_id, entry_date,
                            description, debit_amount, credit_amount, balance_after,
                            entry_type, reference_number, is_reconciled,
                            reconciliation_id, notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entry.transaction_id,
                        entry.group_id,
                        entry.account_id,
                        entry.entry_date,
                        entry.description,
                        float(entry.debit_amount),
                        float(entry.credit_amount),
                        float(entry.balance_after),
                        entry.entry_type.value,
                        entry.reference_number,
                        1 if entry.is_reconciled else 0,
                        entry.reconciliation_id,
                        entry.notes
                    ))

                    entry.id = cursor.lastrowid
                    logger.info(
                        f"Created journal entry {entry.id} for account {entry.account_id} "
                        f"in group {group_id}: debit={entry.debit_amount}, "
                        f"credit={entry.credit_amount}"
                    )

                    created_entries.append(entry.id)

                # Commit the transaction
                conn.commit()

                # Fetch the created entries after commit (so they're visible)
                created_entries = [self.get_by_id(entry_id) for entry_id in created_entries]

                # Fetch the created group with timestamps
                group.id = group_id
                cursor.execute("""
                    SELECT created_at, updated_at
                    FROM transaction_groups
                    WHERE id = ?
                """, (group_id,))
                row = cursor.fetchone()
                if row:
                    group.created_at = datetime.fromisoformat(row[0]) if row[0] else None
                    group.updated_at = datetime.fromisoformat(row[1]) if row[1] else None

                logger.info(
                    f"Successfully created balanced group {group_id} with "
                    f"{len(created_entries)} journal entries"
                )

                return group, created_entries

        except ValidationError:
            # Re-raise validation errors
            raise
        except sqlite3.Error as e:
            logger.error(f"Failed to create balanced group: {e}")
            raise DatabaseError(f"Failed to create balanced group: {e}") from e

    def get_account_balance(self, account_id: int) -> Decimal:
        """
        Get calculated balance for an account from journal entries.

        Calculates balance by summing all journal entries:
        Balance = SUM(debit_amount - credit_amount)

        This is used for balance validation (US-010) to verify that
        cached account balances match the journal entry totals.

        Args:
            account_id: Account ID to calculate balance for

        Returns:
            Calculated balance as Decimal

        Example:
            >>> balance = journal_repo.get_account_balance(123)
            >>> print(f"Account balance: ${balance:.2f}")
            Account balance: $5432.10

        Story: US-010 - Account Balance Validation & Integrity
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT SUM(debit_amount - credit_amount) as balance
                    FROM journal_entries
                    WHERE account_id = ?
                """, (account_id,))

                row = cursor.fetchone()
                balance = row[0] if row and row[0] is not None else 0.0

                return Decimal(str(balance))

        except sqlite3.Error as e:
            logger.error(f"Failed to calculate balance for account {account_id}: {e}")
            raise DatabaseError(f"Failed to calculate balance: {e}") from e

    def _row_to_entry(self, row) -> JournalEntry:
        """
        Convert database row to JournalEntry object.

        Args:
            row: Database row

        Returns:
            JournalEntry object
        """
        return JournalEntry(
            id=row[0],
            transaction_id=row[1],
            group_id=row[2],
            account_id=row[3],
            entry_date=row[4],
            description=row[5],
            debit_amount=Decimal(str(row[6])),
            credit_amount=Decimal(str(row[7])),
            balance_after=Decimal(str(row[8])),
            entry_type=EntryType(row[9]),
            reference_number=row[10],
            is_reconciled=bool(row[11]),
            reconciliation_id=row[12],
            notes=row[13],
            created_at=datetime.fromisoformat(row[14]) if row[14] else None,
            updated_at=datetime.fromisoformat(row[15]) if row[15] else None
        )
