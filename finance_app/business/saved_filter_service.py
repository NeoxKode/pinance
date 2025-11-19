"""
Business logic service for saved filters.

US-015: Combined Filters & Saved Searches (Sprint 16)
"""
from typing import List, Optional, Dict
from datetime import datetime

from finance_app.data.models import SavedFilter
from finance_app.data.database import Database
from finance_app.data.repositories.saved_filter_repository import SavedFilterRepository
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import ValidationError, NotFoundError, DatabaseError

logger = setup_logger(__name__)


class SavedFilterService:
    """
    Service for saved filter business logic (CRUD only).

    US-015: Handles saved filter persistence and management.

    IMPORTANT: This service does NOT implement combined filtering logic.
    Combined filtering already exists in MainWindow._reload_filtered_transactions()
    (5-stage pipeline: Date → Amount → Category → Text → Opening Balance).

    This service focuses exclusively on saved filter CRUD operations:
    - Creating/saving filter configurations
    - Loading/retrieving saved filters
    - Updating existing filters
    - Deleting filters
    - Managing favorites
    - Tracking usage

    Methods:
        - save_filter(): Create new saved filter with validation
        - load_filter(): Load filter by ID and mark as used
        - get_all_filters(): List all saved filters
        - get_favorite_filters(): List favorite filters only
        - update_filter(): Update existing filter
        - delete_filter(): Remove filter
        - toggle_favorite(): Toggle favorite status
        - rename_filter(): Rename existing filter
        - validate_filter_criteria(): Validate filter criteria structure
    """

    def __init__(self, database: Database):
        """
        Initialize service.

        Args:
            database: Database instance
        """
        self.db = database
        self.repo = SavedFilterRepository(database)
        self.logger = logger

    def save_filter(
        self,
        name: str,
        filter_criteria: Dict,
        description: Optional[str] = None,
        is_favorite: bool = False
    ) -> SavedFilter:
        """
        Create and save a new filter configuration.

        Args:
            name: User-friendly filter name (1-100 characters)
            filter_criteria: Dictionary of filter settings (see SavedFilter model for format)
            description: Optional description of what this filter shows
            is_favorite: Whether to mark as favorite immediately

        Returns:
            Created SavedFilter object

        Raises:
            ValidationError: If validation fails (invalid name, duplicate name, invalid criteria)
            DatabaseError: If database operation fails

        Example:
            >>> filter_criteria = {
            ...     "text_search": "coffee",
            ...     "date_from": "2025-01-01",
            ...     "date_to": "2025-12-31",
            ...     "categories": ["Groceries", "Dining Out"]
            ... }
            >>> saved_filter = service.save_filter(
            ...     name="Coffee Purchases 2025",
            ...     filter_criteria=filter_criteria,
            ...     description="All coffee-related expenses this year",
            ...     is_favorite=True
            ... )
        """
        # Validate name
        name = name.strip()
        if not name:
            raise ValidationError("Filter name cannot be empty")

        if len(name) > 100:
            raise ValidationError("Filter name cannot exceed 100 characters")

        # Check for duplicate name
        existing = self.repo.get_by_name(name)
        if existing:
            raise ValidationError(f"Filter with name '{name}' already exists")

        # Validate filter criteria
        self.validate_filter_criteria(filter_criteria)

        # Strip description
        if description:
            description = description.strip()
            if len(description) == 0:
                description = None

        # Create SavedFilter object
        saved_filter = SavedFilter(
            name=name,
            filter_criteria=filter_criteria,
            description=description,
            is_favorite=is_favorite
        )

        # Save to database
        try:
            created = self.repo.create(saved_filter)
            self.logger.info(
                f"Saved new filter: '{created.name}' "
                f"({created.filter_count} active filters)"
            )
            return created

        except DatabaseError as e:
            # Re-raise with more context
            raise ValidationError(f"Failed to save filter: {e}") from e

    def load_filter(self, filter_id: int) -> SavedFilter:
        """
        Load a saved filter by ID and mark it as used.

        This method:
        1. Retrieves the filter from database
        2. Updates last_used_at timestamp
        3. Returns the filter configuration

        Args:
            filter_id: ID of saved filter to load

        Returns:
            SavedFilter object

        Raises:
            NotFoundError: If filter doesn't exist
            DatabaseError: If database operation fails

        Example:
            >>> saved_filter = service.load_filter(1)
            >>> # Apply filter criteria to UI
            >>> criteria = saved_filter.filter_criteria
            >>> if "text_search" in criteria:
            ...     search_widget.setText(criteria["text_search"])
            >>> if "date_from" in criteria:
            ...     date_from_widget.setDate(criteria["date_from"])
        """
        # Get filter from database
        saved_filter = self.repo.get_by_id(filter_id)

        if not saved_filter:
            raise NotFoundError(f"Saved filter {filter_id} not found")

        # Mark as used (updates last_used_at)
        try:
            self.repo.mark_as_used(filter_id)
        except DatabaseError as e:
            # Log warning but don't fail the load operation
            self.logger.warning(f"Failed to update last_used_at for filter {filter_id}: {e}")

        self.logger.info(f"Loaded filter: '{saved_filter.name}' (ID: {filter_id})")

        return saved_filter

    def get_all_filters(self, order_by: str = 'name') -> List[SavedFilter]:
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
            >>> all_filters = service.get_all_filters()
            >>> for f in all_filters:
            ...     print(f"{f.name}: {f.get_summary()}")
        """
        try:
            return self.repo.get_all(order_by=order_by)
        except ValueError as e:
            raise ValidationError(str(e)) from e

    def get_favorite_filters(self) -> List[SavedFilter]:
        """
        Get only favorite filters, sorted by name.

        Returns:
            List of favorite SavedFilter objects (may be empty)

        Raises:
            DatabaseError: If query fails

        Example:
            >>> favorites = service.get_favorite_filters()
            >>> # Show favorites at top of dropdown
            >>> for f in favorites:
            ...     dropdown.addItem(f"⭐ {f.name}")
        """
        return self.repo.get_favorites()

    def update_filter(
        self,
        filter_id: int,
        name: Optional[str] = None,
        filter_criteria: Optional[Dict] = None,
        description: Optional[str] = None,
        is_favorite: Optional[bool] = None
    ) -> SavedFilter:
        """
        Update an existing saved filter.

        Args:
            filter_id: ID of filter to update
            name: New name (optional, None = keep current)
            filter_criteria: New filter criteria (optional, None = keep current)
            description: New description (optional, None = keep current)
            is_favorite: New favorite status (optional, None = keep current)

        Returns:
            Updated SavedFilter object

        Raises:
            NotFoundError: If filter doesn't exist
            ValidationError: If validation fails
            DatabaseError: If update fails

        Example:
            >>> # Update filter name and description only
            >>> updated = service.update_filter(
            ...     filter_id=1,
            ...     name="Coffee Purchases - Updated",
            ...     description="Updated description"
            ... )
        """
        # Get existing filter
        existing = self.repo.get_by_id(filter_id)
        if not existing:
            raise NotFoundError(f"Saved filter {filter_id} not found")

        # Update fields (keep existing if None)
        if name is not None:
            name = name.strip()
            if not name:
                raise ValidationError("Filter name cannot be empty")
            if len(name) > 100:
                raise ValidationError("Filter name cannot exceed 100 characters")

            # Check for duplicate name (but allow same name if it's the current filter)
            duplicate = self.repo.get_by_name(name)
            if duplicate and duplicate.id != filter_id:
                raise ValidationError(f"Filter with name '{name}' already exists")

            existing.name = name

        if filter_criteria is not None:
            self.validate_filter_criteria(filter_criteria)
            existing.filter_criteria = filter_criteria

        if description is not None:
            description = description.strip()
            existing.description = description if len(description) > 0 else None

        if is_favorite is not None:
            existing.is_favorite = is_favorite

        # Save changes
        try:
            updated = self.repo.update(existing)
            self.logger.info(f"Updated filter: '{updated.name}' (ID: {filter_id})")
            return updated

        except DatabaseError as e:
            raise ValidationError(f"Failed to update filter: {e}") from e

    def delete_filter(self, filter_id: int) -> bool:
        """
        Delete a saved filter.

        Args:
            filter_id: ID of filter to delete

        Returns:
            True if deleted successfully

        Raises:
            NotFoundError: If filter doesn't exist
            DatabaseError: If deletion fails

        Example:
            >>> if service.delete_filter(1):
            ...     print("Filter deleted successfully")
        """
        # Check if filter exists first
        existing = self.repo.get_by_id(filter_id)
        if not existing:
            raise NotFoundError(f"Saved filter {filter_id} not found")

        # Delete from database
        deleted = self.repo.delete(filter_id)

        if deleted:
            self.logger.info(f"Deleted filter: '{existing.name}' (ID: {filter_id})")

        return deleted

    def toggle_favorite(self, filter_id: int) -> bool:
        """
        Toggle favorite status for a filter.

        Args:
            filter_id: ID of filter to toggle

        Returns:
            New favorite status (True = favorite, False = not favorite)

        Raises:
            NotFoundError: If filter doesn't exist
            DatabaseError: If update fails

        Example:
            >>> new_status = service.toggle_favorite(1)
            >>> if new_status:
            ...     star_icon.show()
            ... else:
            ...     star_icon.hide()
        """
        return self.repo.toggle_favorite(filter_id)

    def rename_filter(self, filter_id: int, new_name: str) -> SavedFilter:
        """
        Rename an existing filter (convenience method).

        Args:
            filter_id: ID of filter to rename
            new_name: New filter name

        Returns:
            Updated SavedFilter object

        Raises:
            NotFoundError: If filter doesn't exist
            ValidationError: If validation fails
            DatabaseError: If update fails

        Example:
            >>> renamed = service.rename_filter(1, "New Filter Name")
        """
        return self.update_filter(filter_id=filter_id, name=new_name)

    def validate_filter_criteria(self, filter_criteria: Dict) -> None:
        """
        Validate filter criteria structure and values.

        Validates:
        - Must be a dictionary
        - Known keys only (text_search, date_from, date_to, categories, amount_min, amount_max, amount_absolute)
        - Value types match expected format
        - Date strings are valid ISO format
        - Amount strings can be parsed as Decimal
        - Categories is a list of strings

        Args:
            filter_criteria: Dictionary to validate

        Raises:
            ValidationError: If validation fails

        Example:
            >>> criteria = {"text_search": "coffee", "categories": ["Groceries"]}
            >>> service.validate_filter_criteria(criteria)  # No error = valid
        """
        if not isinstance(filter_criteria, dict):
            raise ValidationError("Filter criteria must be a dictionary")

        # Define valid keys and their expected types
        valid_keys = {
            'text_search': str,
            'date_from': str,
            'date_to': str,
            'categories': list,
            'amount_min': str,
            'amount_max': str,
            'amount_absolute': bool
        }

        # Check for unknown keys
        unknown_keys = set(filter_criteria.keys()) - set(valid_keys.keys())
        if unknown_keys:
            raise ValidationError(f"Unknown filter criteria keys: {unknown_keys}")

        # Validate each present key
        for key, value in filter_criteria.items():
            expected_type = valid_keys[key]

            # Check type
            if not isinstance(value, expected_type):
                raise ValidationError(
                    f"Filter criteria '{key}' must be {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )

            # Additional validation for specific fields
            if key in ('date_from', 'date_to'):
                # Validate ISO date format (YYYY-MM-DD)
                try:
                    datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    raise ValidationError(
                        f"Filter criteria '{key}' must be ISO date format (YYYY-MM-DD), "
                        f"got '{value}'"
                    )

            elif key in ('amount_min', 'amount_max'):
                # Validate decimal string
                from decimal import Decimal, InvalidOperation
                try:
                    Decimal(value)
                except InvalidOperation:
                    raise ValidationError(
                        f"Filter criteria '{key}' must be a valid decimal string, "
                        f"got '{value}'"
                    )

            elif key == 'categories':
                # Validate list of strings
                if not all(isinstance(cat, str) for cat in value):
                    raise ValidationError(
                        f"Filter criteria 'categories' must be a list of strings"
                    )

                if len(value) == 0:
                    raise ValidationError(
                        f"Filter criteria 'categories' cannot be empty list"
                    )

        # At least one filter criteria must be present
        if len(filter_criteria) == 0:
            raise ValidationError("Filter criteria cannot be empty")

        self.logger.debug(f"Validated filter criteria: {len(filter_criteria)} fields")
