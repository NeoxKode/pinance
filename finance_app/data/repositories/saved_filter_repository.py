"""
Repository for saved filter data access.

US-015: Combined Filters & Saved Searches (Sprint 16)
"""
import sqlite3
import json
from typing import List, Optional
from datetime import datetime

from finance_app.data.models import SavedFilter
from finance_app.data.database import Database
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import DatabaseError, NotFoundError

logger = setup_logger(__name__)


class SavedFilterRepository:
    """
    Repository for saved filter data access.

    US-015: Handles CRUD operations for saved filter persistence.

    This repository manages saved filter configurations only. It does NOT
    implement combined filtering logic (that exists in MainWindow).

    Methods:
        - create(): Save new filter configuration
        - get_by_id(): Load filter by ID
        - get_by_name(): Load filter by name
        - get_all(): List all saved filters
        - get_favorites(): List favorite filters only
        - update(): Update existing filter
        - delete(): Remove filter
        - mark_as_used(): Update last_used_at timestamp
        - toggle_favorite(): Toggle is_favorite flag
    """

    def __init__(self, database: Database):
        """
        Initialize repository.

        Args:
            database: Database instance
        """
        self.db = database

    def create(self, saved_filter: SavedFilter) -> SavedFilter:
        """
        Create a new saved filter.

        Args:
            saved_filter: SavedFilter object (without ID)

        Returns:
            Created SavedFilter with assigned ID and timestamps

        Raises:
            DatabaseError: If creation fails (e.g., duplicate name)

        Example:
            >>> filter_criteria = {"text_search": "coffee"}
            >>> saved_filter = SavedFilter(name="Coffee", filter_criteria=filter_criteria)
            >>> created = repo.create(saved_filter)
            >>> print(created.id)  # Auto-assigned ID
            1
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Serialize filter_criteria to JSON
                filter_json = json.dumps(saved_filter.filter_criteria)

                cursor.execute("""
                    INSERT INTO saved_filters (
                        name, description, filter_json, schema_version, is_favorite
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    saved_filter.name,
                    saved_filter.description,
                    filter_json,
                    saved_filter.schema_version,
                    1 if saved_filter.is_favorite else 0
                ))

                saved_filter.id = cursor.lastrowid

                # Fetch timestamps set by database
                cursor.execute("""
                    SELECT created_at, updated_at
                    FROM saved_filters
                    WHERE id = ?
                """, (saved_filter.id,))

                row = cursor.fetchone()
                saved_filter.created_at = datetime.fromisoformat(row[0])
                saved_filter.updated_at = datetime.fromisoformat(row[1])

                logger.info(
                    f"Created saved filter: '{saved_filter.name}' "
                    f"(ID: {saved_filter.id}, filters: {saved_filter.filter_count})"
                )

                return saved_filter

        except sqlite3.IntegrityError as e:
            error_msg = f"Filter with name '{saved_filter.name}' already exists"
            logger.error(error_msg)
            raise DatabaseError(error_msg) from e

        except sqlite3.Error as e:
            logger.error(f"Failed to create saved filter: {e}")
            raise DatabaseError(f"Failed to create saved filter: {e}") from e

    def get_by_id(self, filter_id: int) -> Optional[SavedFilter]:
        """
        Get saved filter by ID.

        Args:
            filter_id: Filter ID

        Returns:
            SavedFilter object or None if not found

        Raises:
            DatabaseError: If query fails

        Example:
            >>> saved_filter = repo.get_by_id(1)
            >>> if saved_filter:
            ...     print(saved_filter.name)
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, description, filter_json, schema_version,
                           is_favorite, created_at, updated_at, last_used_at
                    FROM saved_filters
                    WHERE id = ?
                """, (filter_id,))

                row = cursor.fetchone()
                return self._row_to_saved_filter(row) if row else None

        except sqlite3.Error as e:
            logger.error(f"Failed to fetch saved filter {filter_id}: {e}")
            raise DatabaseError(f"Failed to fetch saved filter: {e}") from e

    def get_by_name(self, name: str) -> Optional[SavedFilter]:
        """
        Get saved filter by name.

        Args:
            name: Filter name (case-sensitive)

        Returns:
            SavedFilter object or None if not found

        Raises:
            DatabaseError: If query fails

        Example:
            >>> saved_filter = repo.get_by_name("Coffee Purchases")
            >>> if saved_filter:
            ...     print(saved_filter.get_summary())
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, description, filter_json, schema_version,
                           is_favorite, created_at, updated_at, last_used_at
                    FROM saved_filters
                    WHERE name = ?
                """, (name,))

                row = cursor.fetchone()
                return self._row_to_saved_filter(row) if row else None

        except sqlite3.Error as e:
            logger.error(f"Failed to fetch saved filter '{name}': {e}")
            raise DatabaseError(f"Failed to fetch saved filter: {e}") from e

    def get_all(self, order_by: str = 'name') -> List[SavedFilter]:
        """
        Get all saved filters.

        Args:
            order_by: Sort order ('name', 'created_at', 'last_used_at')
                     Default: 'name' (alphabetical)

        Returns:
            List of SavedFilter objects (may be empty)

        Raises:
            DatabaseError: If query fails

        Example:
            >>> all_filters = repo.get_all()
            >>> for f in all_filters:
            ...     print(f"{f.name}: {f.get_summary()}")
        """
        valid_orders = {
            'name': 'name ASC',
            'created_at': 'created_at DESC',
            'last_used_at': 'last_used_at DESC NULLS LAST'
        }

        if order_by not in valid_orders:
            raise ValueError(f"Invalid order_by: {order_by}. Must be one of {list(valid_orders.keys())}")

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT id, name, description, filter_json, schema_version,
                           is_favorite, created_at, updated_at, last_used_at
                    FROM saved_filters
                    ORDER BY {valid_orders[order_by]}
                """)

                rows = cursor.fetchall()
                filters = [self._row_to_saved_filter(row) for row in rows]

                logger.debug(f"Fetched {len(filters)} saved filters (order_by={order_by})")
                return filters

        except sqlite3.Error as e:
            logger.error(f"Failed to fetch all saved filters: {e}")
            raise DatabaseError(f"Failed to fetch saved filters: {e}") from e

    def get_favorites(self) -> List[SavedFilter]:
        """
        Get only favorite filters, sorted by name.

        Returns:
            List of favorite SavedFilter objects (may be empty)

        Raises:
            DatabaseError: If query fails

        Example:
            >>> favorites = repo.get_favorites()
            >>> print(f"You have {len(favorites)} favorite filters")
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, description, filter_json, schema_version,
                           is_favorite, created_at, updated_at, last_used_at
                    FROM saved_filters
                    WHERE is_favorite = 1
                    ORDER BY name ASC
                """)

                rows = cursor.fetchall()
                filters = [self._row_to_saved_filter(row) for row in rows]

                logger.debug(f"Fetched {len(filters)} favorite filters")
                return filters

        except sqlite3.Error as e:
            logger.error(f"Failed to fetch favorite filters: {e}")
            raise DatabaseError(f"Failed to fetch favorite filters: {e}") from e

    def update(self, saved_filter: SavedFilter) -> SavedFilter:
        """
        Update an existing saved filter.

        Args:
            saved_filter: SavedFilter object with ID

        Returns:
            Updated SavedFilter with new updated_at timestamp

        Raises:
            NotFoundError: If filter ID doesn't exist
            DatabaseError: If update fails

        Example:
            >>> saved_filter = repo.get_by_id(1)
            >>> saved_filter.description = "Updated description"
            >>> saved_filter.filter_criteria["amount_min"] = "10.00"
            >>> updated = repo.update(saved_filter)
        """
        if not saved_filter.id:
            raise ValueError("Cannot update saved filter without ID")

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Check if filter exists
                cursor.execute("SELECT id FROM saved_filters WHERE id = ?", (saved_filter.id,))
                if not cursor.fetchone():
                    raise NotFoundError(f"Saved filter {saved_filter.id} not found")

                # Serialize filter_criteria to JSON
                filter_json = json.dumps(saved_filter.filter_criteria)

                cursor.execute("""
                    UPDATE saved_filters
                    SET name = ?,
                        description = ?,
                        filter_json = ?,
                        schema_version = ?,
                        is_favorite = ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (
                    saved_filter.name,
                    saved_filter.description,
                    filter_json,
                    saved_filter.schema_version,
                    1 if saved_filter.is_favorite else 0,
                    saved_filter.id
                ))

                # Fetch new updated_at timestamp
                cursor.execute("SELECT updated_at FROM saved_filters WHERE id = ?", (saved_filter.id,))
                row = cursor.fetchone()
                saved_filter.updated_at = datetime.fromisoformat(row[0])

                logger.info(f"Updated saved filter: '{saved_filter.name}' (ID: {saved_filter.id})")

                return saved_filter

        except NotFoundError:
            raise

        except sqlite3.IntegrityError as e:
            error_msg = f"Filter with name '{saved_filter.name}' already exists"
            logger.error(error_msg)
            raise DatabaseError(error_msg) from e

        except sqlite3.Error as e:
            logger.error(f"Failed to update saved filter {saved_filter.id}: {e}")
            raise DatabaseError(f"Failed to update saved filter: {e}") from e

    def delete(self, filter_id: int) -> bool:
        """
        Delete a saved filter.

        Args:
            filter_id: Filter ID to delete

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseError: If deletion fails

        Example:
            >>> if repo.delete(1):
            ...     print("Filter deleted successfully")
            ... else:
            ...     print("Filter not found")
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM saved_filters WHERE id = ?", (filter_id,))

                deleted = cursor.rowcount > 0

                if deleted:
                    logger.info(f"Deleted saved filter ID: {filter_id}")
                else:
                    logger.warning(f"Attempted to delete non-existent filter ID: {filter_id}")

                return deleted

        except sqlite3.Error as e:
            logger.error(f"Failed to delete saved filter {filter_id}: {e}")
            raise DatabaseError(f"Failed to delete saved filter: {e}") from e

    def mark_as_used(self, filter_id: int) -> bool:
        """
        Mark filter as recently used by updating last_used_at timestamp.

        Args:
            filter_id: Filter ID

        Returns:
            True if updated, False if filter not found

        Raises:
            DatabaseError: If update fails

        Example:
            >>> repo.mark_as_used(1)  # Called when user loads this filter
            True
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE saved_filters
                    SET last_used_at = datetime('now')
                    WHERE id = ?
                """, (filter_id,))

                updated = cursor.rowcount > 0

                if updated:
                    logger.debug(f"Marked filter {filter_id} as used")
                else:
                    logger.warning(f"Attempted to mark non-existent filter {filter_id} as used")

                return updated

        except sqlite3.Error as e:
            logger.error(f"Failed to mark filter {filter_id} as used: {e}")
            raise DatabaseError(f"Failed to mark filter as used: {e}") from e

    def toggle_favorite(self, filter_id: int) -> bool:
        """
        Toggle is_favorite flag for a filter.

        Args:
            filter_id: Filter ID

        Returns:
            New favorite status (True = favorite, False = not favorite)

        Raises:
            NotFoundError: If filter not found
            DatabaseError: If update fails

        Example:
            >>> new_status = repo.toggle_favorite(1)
            >>> if new_status:
            ...     print("Filter is now a favorite ⭐")
            ... else:
            ...     print("Filter removed from favorites")
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Get current favorite status
                cursor.execute("SELECT is_favorite FROM saved_filters WHERE id = ?", (filter_id,))
                row = cursor.fetchone()

                if not row:
                    raise NotFoundError(f"Saved filter {filter_id} not found")

                current_favorite = bool(row[0])
                new_favorite = not current_favorite

                # Toggle favorite status
                cursor.execute("""
                    UPDATE saved_filters
                    SET is_favorite = ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (1 if new_favorite else 0, filter_id))

                logger.info(
                    f"Toggled favorite for filter {filter_id}: "
                    f"{current_favorite} → {new_favorite}"
                )

                return new_favorite

        except NotFoundError:
            raise

        except sqlite3.Error as e:
            logger.error(f"Failed to toggle favorite for filter {filter_id}: {e}")
            raise DatabaseError(f"Failed to toggle favorite: {e}") from e

    def _row_to_saved_filter(self, row: tuple) -> SavedFilter:
        """
        Convert database row to SavedFilter object.

        Args:
            row: Database row tuple

        Returns:
            SavedFilter object

        Raises:
            json.JSONDecodeError: If filter_json is invalid
        """
        return SavedFilter(
            id=row[0],
            name=row[1],
            description=row[2],
            filter_criteria=json.loads(row[3]),  # Deserialize JSON
            schema_version=row[4],
            is_favorite=bool(row[5]),
            created_at=datetime.fromisoformat(row[6]) if row[6] else None,
            updated_at=datetime.fromisoformat(row[7]) if row[7] else None,
            last_used_at=datetime.fromisoformat(row[8]) if row[8] else None
        )
