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
                           legacy_type, last_reconciled_date, opening_balance_date,
                           is_parent, hierarchy_level, hierarchy_path
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
                           legacy_type, last_reconciled_date, opening_balance_date,
                           is_parent, hierarchy_level, hierarchy_path
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
                        normal_balance, currency, parent_account_id, legacy_type,
                        is_parent, hierarchy_level
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    account.name,
                    legacy_type,  # Old type column for backward compatibility
                    type_val,
                    subtype_val,
                    float(account.balance),
                    normal_bal_val,
                    account.currency,
                    account.parent_account_id,
                    legacy_type,  # Also store in legacy_type
                    1 if account.is_parent else 0,  # US-006: Hierarchy support
                    account.hierarchy_level  # US-006: Hierarchy support
                ))
                account.id = cursor.lastrowid

                # US-006: Update hierarchy_path after creation
                # This builds the path based on parent_account_id
                conn.commit()  # Commit insert first so update_hierarchy_path can read it

            # Update hierarchy path outside the connection context
            # to avoid nested transaction issues
            self.update_hierarchy_path(account.id)

            logger.info(
                f"Created account: {account.name} "
                f"({type_val}/{subtype_val}, "
                f"ID: {account.id}, "
                f"parent: {account.parent_account_id or 'none'})"
            )
            return self.get_by_id(account.id)  # Return fresh copy with hierarchy_path set
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
            # US-006: Get old account to check if parent changed
            old_account = self.get_by_id(account.id)
            if not old_account:
                raise NotFoundError(f"Account with ID {account.id} not found")

            parent_changed = old_account.parent_account_id != account.parent_account_id

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
                        is_parent = ?,
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
                    1 if account.is_parent else 0,  # US-006
                    account.last_reconciled_date,  # US-004
                    account.opening_balance_date,  # US-005
                    account.id
                ))

                if cursor.rowcount == 0:
                    raise NotFoundError(f"Account with ID {account.id} not found")

                conn.commit()

            # US-006: Update hierarchy path if parent changed
            if parent_changed:
                logger.debug(f"Parent changed for account {account.id}, updating hierarchy paths")
                self.update_hierarchy_path(account.id)

            logger.info(f"Updated account: {account.name} (ID: {account.id})")
            return self.get_by_id(account.id)  # Return fresh copy with updated hierarchy
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

    # ========================================================================
    # US-006: Hierarchy Query Methods
    # ========================================================================

    def get_child_accounts(self, parent_id: int) -> list[Account]:
        """
        Get all direct children of a parent account.

        US-006: Account hierarchy support.

        Args:
            parent_id: ID of the parent account

        Returns:
            List of child Account objects (direct children only)

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM accounts
                    WHERE parent_account_id = ?
                    ORDER BY name
                """, (parent_id,))

                rows = cursor.fetchall()
                accounts = [self._row_to_account(row) for row in rows]

                logger.debug(f"Retrieved {len(accounts)} child accounts for parent {parent_id}")
                return accounts

        except sqlite3.Error as e:
            logger.error(f"Failed to get child accounts for parent {parent_id}: {e}")
            raise DatabaseError(f"Failed to get child accounts: {e}") from e

    def get_descendant_accounts(self, parent_id: int) -> list[Account]:
        """
        Get all descendants of a parent account (recursive).

        US-006: Uses hierarchy_path for efficient recursive query.
        This includes children, grandchildren, great-grandchildren, etc.

        Args:
            parent_id: ID of the parent account

        Returns:
            List of all descendant Account objects

        Raises:
            NotFoundError: If parent account not found
            DatabaseError: If query fails
        """
        try:
            # First get the parent account to retrieve its hierarchy_path
            parent = self.get_by_id(parent_id)
            if not parent:
                raise NotFoundError(f"Parent account with ID {parent_id} not found")

            if not parent.hierarchy_path:
                # Parent has no path set yet, return empty list
                logger.debug(f"Parent account {parent_id} has no hierarchy_path set")
                return []

            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Use hierarchy_path LIKE pattern for efficient descendant query
                # Pattern: "/1/5/%" matches "/1/5/12", "/1/5/12/20", etc.
                pattern = f"{parent.hierarchy_path}/%"

                cursor.execute("""
                    SELECT * FROM accounts
                    WHERE hierarchy_path LIKE ?
                    ORDER BY hierarchy_path
                """, (pattern,))

                rows = cursor.fetchall()
                accounts = [self._row_to_account(row) for row in rows]

                logger.debug(f"Retrieved {len(accounts)} descendant accounts for parent {parent_id}")
                return accounts

        except NotFoundError:
            raise
        except sqlite3.Error as e:
            logger.error(f"Failed to get descendant accounts for parent {parent_id}: {e}")
            raise DatabaseError(f"Failed to get descendant accounts: {e}") from e

    def get_root_accounts(self) -> list[Account]:
        """
        Get all top-level accounts (accounts with no parent).

        US-006: Account hierarchy support.

        Returns:
            List of root Account objects

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM accounts
                    WHERE parent_account_id IS NULL
                    ORDER BY account_type, name
                """)

                rows = cursor.fetchall()
                accounts = [self._row_to_account(row) for row in rows]

                logger.debug(f"Retrieved {len(accounts)} root accounts")
                return accounts

        except sqlite3.Error as e:
            logger.error(f"Failed to get root accounts: {e}")
            raise DatabaseError(f"Failed to get root accounts: {e}") from e

    def update_hierarchy_path(self, account_id: int) -> None:
        """
        Update hierarchy_path and hierarchy_level for an account and all its descendants.

        US-006: This method should be called whenever an account's parent_account_id changes.
        It recursively updates the hierarchy path for the account and all its children.

        Hierarchy path format: "/parent_id/.../account_id"
        Example: account with id=12, parent=5, grandparent=1 -> "/1/5/12"

        Args:
            account_id: ID of the account to update

        Raises:
            NotFoundError: If account not found
            DatabaseError: If update fails
        """
        try:
            account = self.get_by_id(account_id)
            if not account:
                raise NotFoundError(f"Account with ID {account_id} not found")

            # Build hierarchy path by walking up the parent chain
            path_parts = [str(account.id)]
            current = account

            while current.parent_account_id:
                parent = self.get_by_id(current.parent_account_id)
                if not parent:
                    logger.warning(f"Parent account {current.parent_account_id} not found for account {current.id}")
                    break
                path_parts.insert(0, str(parent.id))
                current = parent

            # Build path: "/1/5/12"
            new_path = "/" + "/".join(path_parts)
            new_level = len(path_parts) - 1

            # Update this account's hierarchy fields
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE accounts
                    SET hierarchy_path = ?,
                        hierarchy_level = ?
                    WHERE id = ?
                """, (new_path, new_level, account_id))

                if cursor.rowcount == 0:
                    raise NotFoundError(f"Account with ID {account_id} not found")

                logger.debug(f"Updated hierarchy for account {account_id}: path={new_path}, level={new_level}")

            # Recursively update all children
            children = self.get_child_accounts(account_id)
            for child in children:
                self.update_hierarchy_path(child.id)

        except NotFoundError:
            raise
        except sqlite3.Error as e:
            logger.error(f"Failed to update hierarchy path for account {account_id}: {e}")
            raise DatabaseError(f"Failed to update hierarchy path: {e}") from e

    def build_account_tree(self, accounts: list[Account] = None) -> list[Account]:
        """
        Build a hierarchical tree structure from a flat list of accounts.

        US-006: This method organizes accounts into a tree structure where each
        parent account has a 'children' attribute containing its child accounts.
        The tree is built by organizing accounts by their parent_account_id relationships.

        Args:
            accounts: Optional list of accounts. If None, retrieves all accounts.

        Returns:
            List of root-level Account objects with children attached.
            Each account will have a temporary 'children' attribute added.

        Example:
            ```python
            tree = repo.build_account_tree()
            for root in tree:
                print(f"{root.name}")
                for child in getattr(root, 'children', []):
                    print(f"  - {child.name}")
            ```

        Raises:
            DatabaseError: If query fails
        """
        try:
            # Get all accounts if not provided
            if accounts is None:
                accounts = self.get_all()

            # Create a dictionary mapping account ID to account object
            account_map = {account.id: account for account in accounts}

            # Add a temporary 'children' list to each account
            for account in accounts:
                # Use setattr to add a temporary attribute
                setattr(account, 'children', [])

            # Build parent-child relationships
            root_accounts = []
            for account in accounts:
                if account.parent_account_id is None:
                    # This is a root account
                    root_accounts.append(account)
                else:
                    # This is a child account
                    parent = account_map.get(account.parent_account_id)
                    if parent:
                        # Add this account to its parent's children list
                        getattr(parent, 'children', []).append(account)
                    else:
                        # Orphaned account (parent not found) - treat as root
                        logger.warning(
                            f"Account {account.id} ({account.name}) has parent_account_id "
                            f"{account.parent_account_id} but parent not found. Treating as root."
                        )
                        root_accounts.append(account)

            # Sort root accounts by type and name
            root_accounts.sort(key=lambda a: (a.account_type.value, a.name))

            # Recursively sort children
            def sort_children_recursively(account):
                """Recursively sort children of an account by name."""
                children = getattr(account, 'children', [])
                children.sort(key=lambda a: a.name)
                for child in children:
                    sort_children_recursively(child)

            for root in root_accounts:
                sort_children_recursively(root)

            logger.debug(f"Built account tree with {len(root_accounts)} root accounts")
            return root_accounts

        except Exception as e:
            logger.error(f"Failed to build account tree: {e}")
            raise DatabaseError(f"Failed to build account tree: {e}") from e

    @staticmethod
    def _row_to_account(row: sqlite3.Row) -> Account:
        """
        Convert database row to Account object.

        US-006: Added hierarchy field mapping.

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
            # US-006: Hierarchy fields
            is_parent=bool(row['is_parent']) if 'is_parent' in row.keys() else False,
            hierarchy_level=row['hierarchy_level'] if 'hierarchy_level' in row.keys() else 0,
            hierarchy_path=row['hierarchy_path'] if 'hierarchy_path' in row.keys() else None,
            # US-004: Reconciliation
            last_reconciled_date=row['last_reconciled_date'] if 'last_reconciled_date' in row.keys() else None,
            # US-005: Opening balance
            opening_balance_date=row['opening_balance_date'] if 'opening_balance_date' in row.keys() else None,
            created_at=None,  # Not in current schema
            updated_at=None   # Not in current schema
        )
