"""
Repository for category data access.
"""
import sqlite3
from typing import List, Optional

from finance_app.data.models import Category
from finance_app.data.database import Database
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import DatabaseError, NotFoundError

logger = setup_logger(__name__)


class CategoryRepository:
    """Repository for category data access."""

    def __init__(self, database: Database):
        """
        Initialize repository.

        Args:
            database: Database instance
        """
        self.db = database

    def get_all(self, category_type: Optional[str] = None) -> List[Category]:
        """
        Get all categories, optionally filtered by type.

        Args:
            category_type: Filter by type ('income' or 'expense')

        Returns:
            List of Category objects

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                if category_type:
                    cursor.execute("""
                        SELECT id, name, type
                        FROM categories
                        WHERE type = ?
                        ORDER BY name
                    """, (category_type,))
                else:
                    cursor.execute("""
                        SELECT id, name, type
                        FROM categories
                        ORDER BY name
                    """)

                rows = cursor.fetchall()
                return [self._row_to_category(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch categories: {e}")
            raise DatabaseError(f"Failed to fetch categories: {e}") from e

    def get_names(self, category_type: Optional[str] = None) -> List[str]:
        """
        Get category names only.

        Args:
            category_type: Filter by type ('income' or 'expense')

        Returns:
            List of category names

        Raises:
            DatabaseError: If query fails
        """
        categories = self.get_all(category_type)
        return [cat.name for cat in categories]

    def get_by_id(self, category_id: int) -> Optional[Category]:
        """
        Get category by ID.

        Args:
            category_id: Category ID

        Returns:
            Category object or None if not found

        Raises:
            DatabaseError: If query fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, type
                    FROM categories
                    WHERE id = ?
                """, (category_id,))
                row = cursor.fetchone()
                return self._row_to_category(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch category {category_id}: {e}")
            raise DatabaseError(f"Failed to fetch category: {e}") from e

    def create(self, category: Category) -> Category:
        """
        Create a new category.

        Args:
            category: Category object (without ID)

        Returns:
            Created category with ID

        Raises:
            DatabaseError: If creation fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO categories (name, type)
                    VALUES (?, ?)
                """, (category.name, category.type))
                category.id = cursor.lastrowid
                logger.info(f"Created category: {category.name} (ID: {category.id})")
                return category
        except sqlite3.IntegrityError as e:
            logger.error(f"Category with name '{category.name}' already exists")
            raise DatabaseError(f"Category already exists: {e}") from e
        except sqlite3.Error as e:
            logger.error(f"Failed to create category: {e}")
            raise DatabaseError(f"Failed to create category: {e}") from e

    def delete(self, category_id: int) -> bool:
        """
        Delete a category.

        Args:
            category_id: Category ID

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseError: If deletion fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Deleted category ID: {category_id}")
                return deleted
        except sqlite3.Error as e:
            logger.error(f"Failed to delete category {category_id}: {e}")
            raise DatabaseError(f"Failed to delete category: {e}") from e

    @staticmethod
    def _row_to_category(row: sqlite3.Row) -> Category:
        """
        Convert database row to Category object.

        Args:
            row: Database row

        Returns:
            Category object
        """
        return Category(
            id=row['id'],
            name=row['name'],
            type=row['type'],
            created_at=None  # Not in current schema
        )
