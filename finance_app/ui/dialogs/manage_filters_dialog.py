"""
Manage Filters Dialog for US-015.

Allows users to view, edit, delete, and manage saved filters.

US-015: Combined Filters & Saved Searches (Sprint 16, Phase 5)
Created: 2025-11-18
"""

from typing import List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QHeaderView, QAbstractItemView, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from finance_app.data.models import SavedFilter


class ManageFiltersDialog(QDialog):
    """
    Dialog for managing saved filters.

    US-015: Provides table view of all saved filters with CRUD operations:
    - View all filters (name, description, filter count, last used, favorite)
    - Edit filter name/description
    - Delete filters
    - Toggle favorite status
    - Shows filter details on selection

    Signals:
        filter_deleted(int): Emitted when filter is deleted (filter_id)
        filter_updated(int): Emitted when filter is updated (filter_id)
        filter_favorited(int, bool): Emitted when favorite toggled (filter_id, is_favorite)

    Example:
        >>> dialog = ManageFiltersDialog(saved_filters)
        >>> dialog.filter_deleted.connect(lambda id: print(f"Deleted: {id}"))
        >>> dialog.exec()
    """

    # Signals for filter management
    filter_deleted = Signal(int)  # filter_id
    filter_updated = Signal(int)  # filter_id
    filter_favorited = Signal(int, bool)  # filter_id, is_favorite

    def __init__(self, saved_filters: List[SavedFilter], parent=None):
        """
        Initialize manage filters dialog.

        Args:
            saved_filters: List of SavedFilter objects to display
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        self.saved_filters = saved_filters
        self.selected_filter = None

        self.setWindowTitle("Manage Saved Filters")
        self.setModal(True)
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)

        self._setup_ui()
        self._populate_table()
        self._apply_styling()

    def _setup_ui(self):
        """Create the dialog user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header_label = QLabel("⚙️ Manage Saved Filters")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        main_layout.addWidget(header_label)

        # Subtitle
        subtitle = QLabel(f"{len(self.saved_filters)} saved filter(s)")
        subtitle.setStyleSheet("color: #666; margin-bottom: 8px;")
        main_layout.addWidget(subtitle)

        # Filters table
        self.filters_table = QTableWidget()
        self.filters_table.setColumnCount(6)
        self.filters_table.setHorizontalHeaderLabels([
            "⭐", "Name", "Description", "Filters", "Last Used", "Actions"
        ])

        # Table settings
        self.filters_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.filters_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.filters_table.setAlternatingRowColors(True)
        self.filters_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.filters_table.verticalHeader().setVisible(False)

        # Column widths
        header = self.filters_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Favorite
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Description
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Filters
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Last Used
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Actions

        # Connect selection signal
        self.filters_table.itemSelectionChanged.connect(self._on_selection_changed)

        main_layout.addWidget(self.filters_table)

        # Filter details panel
        self.details_label = QLabel("<i>Select a filter to view details</i>")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet(
            "background-color: #f9f9f9; "
            "padding: 12px; "
            "border: 1px solid #e0e0e0; "
            "border-radius: 4px; "
            "min-height: 60px;"
        )
        main_layout.addWidget(self.details_label)

        # Action buttons at bottom
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setToolTip("Reload filters from database")
        refresh_btn.clicked.connect(self._on_refresh_clicked)
        button_layout.addWidget(refresh_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setObjectName("primaryButton")
        close_btn.setDefault(True)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

    def _apply_styling(self):
        """Apply QSS styling to dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }

            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                gridline-color: #f0f0f0;
            }

            QTableWidget::item {
                padding: 6px;
            }

            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: black;
            }

            QTableWidget::item:hover {
                background-color: #F5F5F5;
            }

            QHeaderView::section {
                background-color: #fafafa;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-weight: bold;
            }

            QPushButton {
                padding: 6px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                min-width: 80px;
            }

            QPushButton:hover {
                background-color: #f5f5f5;
            }

            QPushButton#primaryButton {
                background-color: #2196F3;
                color: white;
                border: none;
                font-weight: bold;
            }

            QPushButton#primaryButton:hover {
                background-color: #1976D2;
            }

            QPushButton#deleteButton {
                background-color: #F44336;
                color: white;
                border: none;
            }

            QPushButton#deleteButton:hover {
                background-color: #D32F2F;
            }

            QPushButton#favoriteButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
                min-width: 30px;
                padding: 2px;
            }

            QPushButton#favoriteButton:hover {
                background-color: #FFF9C4;
            }
        """)

    def _populate_table(self):
        """Populate table with saved filters."""
        self.filters_table.setRowCount(0)

        # Sort filters: favorites first, then by name
        sorted_filters = sorted(
            self.saved_filters,
            key=lambda f: (not f.is_favorite, f.name.lower())
        )

        for filter_obj in sorted_filters:
            self._add_filter_row(filter_obj)

    def _add_filter_row(self, filter_obj: SavedFilter):
        """
        Add a filter row to the table.

        Args:
            filter_obj: SavedFilter object to add
        """
        row = self.filters_table.rowCount()
        self.filters_table.insertRow(row)

        # Column 0: Favorite button
        favorite_btn = QPushButton("⭐" if filter_obj.is_favorite else "☆")
        favorite_btn.setObjectName("favoriteButton")
        favorite_btn.setToolTip("Toggle favorite status")
        favorite_btn.setCursor(Qt.PointingHandCursor)
        favorite_btn.clicked.connect(
            lambda checked, fid=filter_obj.id: self._on_favorite_clicked(fid)
        )
        self.filters_table.setCellWidget(row, 0, favorite_btn)

        # Column 1: Name
        name_item = QTableWidgetItem(filter_obj.name)
        name_item.setData(Qt.UserRole, filter_obj.id)  # Store filter ID
        if filter_obj.is_favorite:
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
        self.filters_table.setItem(row, 1, name_item)

        # Column 2: Description
        description = filter_obj.description or "<i>No description</i>"
        desc_item = QTableWidgetItem(description)
        desc_item.setForeground(Qt.gray if not filter_obj.description else Qt.black)
        self.filters_table.setItem(row, 2, desc_item)

        # Column 3: Filter count
        filter_count = filter_obj.filter_count
        count_item = QTableWidgetItem(f"{filter_count} filter{'s' if filter_count != 1 else ''}")
        count_item.setTextAlignment(Qt.AlignCenter)
        self.filters_table.setItem(row, 3, count_item)

        # Column 4: Last used
        if filter_obj.last_used_at:
            last_used = filter_obj.last_used_at.strftime("%b %d, %Y %I:%M %p")
        else:
            last_used = "Never"
        last_used_item = QTableWidgetItem(last_used)
        last_used_item.setTextAlignment(Qt.AlignCenter)
        if not filter_obj.last_used_at:
            last_used_item.setForeground(Qt.gray)
        self.filters_table.setItem(row, 4, last_used_item)

        # Column 5: Actions (Edit/Delete buttons)
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(4, 2, 4, 2)
        actions_layout.setSpacing(4)

        # Edit button
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setToolTip("Edit filter name and description")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(
            lambda checked, fid=filter_obj.id: self._on_edit_clicked(fid)
        )
        actions_layout.addWidget(edit_btn)

        # Delete button
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setObjectName("deleteButton")
        delete_btn.setToolTip("Delete this saved filter")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(
            lambda checked, fid=filter_obj.id: self._on_delete_clicked(fid)
        )
        actions_layout.addWidget(delete_btn)

        self.filters_table.setCellWidget(row, 5, actions_widget)

    def _on_selection_changed(self):
        """Handle filter selection change - show details."""
        selected_items = self.filters_table.selectedItems()
        if not selected_items:
            self.details_label.setText("<i>Select a filter to view details</i>")
            self.selected_filter = None
            return

        # Get selected filter ID
        row = selected_items[0].row()
        filter_id = self.filters_table.item(row, 1).data(Qt.UserRole)

        # Find filter object
        filter_obj = next((f for f in self.saved_filters if f.id == filter_id), None)
        if not filter_obj:
            return

        self.selected_filter = filter_obj

        # Build details text
        details = f"<b>{filter_obj.name}</b><br>"
        if filter_obj.description:
            details += f"<i>{filter_obj.description}</i><br><br>"
        else:
            details += "<br>"

        details += f"<b>Filter Criteria:</b><br>{filter_obj.get_summary()}<br><br>"

        details += f"<b>Created:</b> {filter_obj.created_at.strftime('%b %d, %Y %I:%M %p')}<br>"
        details += f"<b>Updated:</b> {filter_obj.updated_at.strftime('%b %d, %Y %I:%M %p')}<br>"

        if filter_obj.last_used_at:
            details += f"<b>Last Used:</b> {filter_obj.last_used_at.strftime('%b %d, %Y %I:%M %p')}"
        else:
            details += f"<b>Last Used:</b> Never"

        self.details_label.setText(details)

    def _on_favorite_clicked(self, filter_id: int):
        """
        Handle favorite button click.

        Args:
            filter_id: ID of filter to toggle favorite
        """
        # Find filter
        filter_obj = next((f for f in self.saved_filters if f.id == filter_id), None)
        if not filter_obj:
            return

        # Toggle favorite status
        new_status = not filter_obj.is_favorite
        filter_obj.is_favorite = new_status

        # Emit signal
        self.filter_favorited.emit(filter_id, new_status)

        # Refresh table to re-sort
        self._populate_table()

    def _on_edit_clicked(self, filter_id: int):
        """
        Handle edit button click.

        Args:
            filter_id: ID of filter to edit
        """
        # Find filter
        filter_obj = next((f for f in self.saved_filters if f.id == filter_id), None)
        if not filter_obj:
            return

        # Prompt for new name
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Filter",
            "Enter new name:",
            text=filter_obj.name
        )

        if ok and new_name.strip():
            filter_obj.name = new_name.strip()

            # Prompt for new description
            new_desc, ok = QInputDialog.getMultiLineText(
                self,
                "Edit Description",
                "Enter description (optional):",
                text=filter_obj.description or ""
            )

            if ok:
                filter_obj.description = new_desc.strip() or None

                # Emit signal
                self.filter_updated.emit(filter_id)

                # Refresh table
                self._populate_table()

    def _on_delete_clicked(self, filter_id: int):
        """
        Handle delete button click.

        Args:
            filter_id: ID of filter to delete
        """
        # Find filter
        filter_obj = next((f for f in self.saved_filters if f.id == filter_id), None)
        if not filter_obj:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the filter '{filter_obj.name}'?\n\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Remove from list
            self.saved_filters = [f for f in self.saved_filters if f.id != filter_id]

            # Emit signal
            self.filter_deleted.emit(filter_id)

            # Refresh table
            self._populate_table()

            # Clear details if deleted filter was selected
            if self.selected_filter and self.selected_filter.id == filter_id:
                self.details_label.setText("<i>Select a filter to view details</i>")
                self.selected_filter = None

    def _on_refresh_clicked(self):
        """Handle refresh button click - signal to reload filters."""
        # This would typically reload from the database
        # For now, just refresh the table display
        self._populate_table()

    def update_filters(self, saved_filters: List[SavedFilter]):
        """
        Update the filters list and refresh display.

        Args:
            saved_filters: New list of SavedFilter objects
        """
        self.saved_filters = saved_filters
        self._populate_table()
        self.details_label.setText("<i>Select a filter to view details</i>")
        self.selected_filter = None
