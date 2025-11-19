"""
Save Filter Dialog for US-015.

Allows users to save current filter state with a name and optional description.

US-015: Combined Filters & Saved Searches (Sprint 16, Phase 4)
Created: 2025-11-18
"""

from typing import Dict, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QLabel, QPushButton, QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class SaveFilterDialog(QDialog):
    """
    Dialog for saving current filter state.

    US-015: Prompts user for filter name and optional description,
    shows preview of filter criteria, and emits signal when saved.

    Signals:
        filter_saved(dict): Emitted when filter is saved
                           dict contains: name, description, filter_criteria, is_favorite

    Example:
        >>> current_filters = {
        ...     "text_search": "coffee",
        ...     "date_from": "2025-01-01",
        ...     "categories": ["Groceries"]
        ... }
        >>> dialog = SaveFilterDialog(current_filters)
        >>> dialog.filter_saved.connect(lambda data: print(f"Saved: {data['name']}"))
        >>> if dialog.exec():
        ...     print("Filter saved successfully")
    """

    # Signal emitted when filter is saved
    filter_saved = Signal(dict)  # {name, description, filter_criteria, is_favorite}

    def __init__(self, current_filters: Dict, parent=None):
        """
        Initialize save filter dialog.

        Args:
            current_filters: Dictionary of active filter criteria
                            Format: {"text_search": str, "date_from": str, ...}
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        self.current_filters = current_filters
        self.filter_name = ""
        self.filter_description = ""
        self.is_favorite = False

        self.setWindowTitle("Save Filter")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)

        self._setup_ui()
        self._apply_styling()

        # Set focus to name input
        self.name_input.setFocus()

    def _setup_ui(self):
        """Create the dialog user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header_label = QLabel("💾 Save Current Filters")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        main_layout.addWidget(header_label)

        # Subtitle
        subtitle = QLabel("Save this filter combination for quick access later")
        subtitle.setStyleSheet("color: #666; margin-bottom: 8px;")
        main_layout.addWidget(subtitle)

        # Input form
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setVerticalSpacing(12)

        # Filter name (required)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Monthly Groceries")
        self.name_input.setMaxLength(100)
        self.name_input.textChanged.connect(self._on_name_changed)
        form_layout.addRow("Filter Name:*", self.name_input)

        # Description (optional)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("e.g., All grocery purchases from this month")
        self.description_input.setMaximumHeight(60)
        self.description_input.setTabChangesFocus(True)  # Tab to next field
        form_layout.addRow("Description:", self.description_input)

        # Favorite checkbox
        self.favorite_checkbox = QCheckBox("⭐ Mark as favorite (shows at top of list)")
        form_layout.addRow("", self.favorite_checkbox)

        main_layout.addLayout(form_layout)

        # Filter preview
        preview_group = QGroupBox("Filter Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_label = QLabel(self._build_filter_preview())
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet(
            "background-color: #f9f9f9; "
            "padding: 12px; "
            "border: 1px solid #e0e0e0; "
            "border-radius: 4px;"
        )
        preview_layout.addWidget(self.preview_label)

        main_layout.addWidget(preview_group)

        # Spacer to push buttons to bottom
        main_layout.addStretch()

        # Required field note
        note_label = QLabel("* Required field")
        note_label.setStyleSheet("color: #666; font-size: 11px;")
        main_layout.addWidget(note_label)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # Save button
        self.save_btn = QPushButton("💾 Save Filter")
        self.save_btn.setObjectName("primaryButton")
        self.save_btn.setDefault(True)
        self.save_btn.setEnabled(False)  # Disabled until name is entered
        self.save_btn.clicked.connect(self._on_save_clicked)
        button_layout.addWidget(self.save_btn)

        main_layout.addLayout(button_layout)

    def _apply_styling(self):
        """Apply QSS styling to dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }

            QLineEdit, QTextEdit {
                padding: 6px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                font-size: 13px;
            }

            QLineEdit:focus, QTextEdit:focus {
                border-color: #2196F3;
            }

            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }

            QPushButton {
                padding: 8px 16px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                min-width: 100px;
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

            QPushButton#primaryButton:pressed {
                background-color: #0D47A1;
            }

            QPushButton#primaryButton:disabled {
                background-color: #BBDEFB;
                color: #E3F2FD;
            }

            QCheckBox {
                spacing: 6px;
            }

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #e0e0e0;
                border-radius: 3px;
            }

            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
            }

            QCheckBox::indicator:checked:after {
                content: "✓";
                color: white;
            }
        """)

    def _build_filter_preview(self) -> str:
        """
        Build human-readable preview of filter criteria.

        Returns:
            Formatted string describing active filters

        Example:
            "Text: 'coffee'\nDate: Jan 1, 2025 to Dec 31, 2025\nCategories: Groceries, Dining Out"
        """
        if not self.current_filters:
            return "<i>No filters active</i>"

        lines = []

        # Text search
        if "text_search" in self.current_filters and self.current_filters["text_search"]:
            text = self.current_filters["text_search"]
            lines.append(f"<b>Text:</b> '{text}'")

        # Date range
        date_from = self.current_filters.get("date_from")
        date_to = self.current_filters.get("date_to")
        if date_from or date_to:
            date_str = ""
            if date_from and date_to:
                date_str = f"{date_from} to {date_to}"
            elif date_from:
                date_str = f"from {date_from}"
            elif date_to:
                date_str = f"until {date_to}"
            lines.append(f"<b>Date:</b> {date_str}")

        # Categories
        categories = self.current_filters.get("categories", [])
        if categories:
            if len(categories) == 1:
                lines.append(f"<b>Category:</b> {categories[0]}")
            else:
                cat_list = ", ".join(categories[:3])
                if len(categories) > 3:
                    cat_list += f" (+{len(categories) - 3} more)"
                lines.append(f"<b>Categories:</b> {cat_list}")

        # Amount range
        amount_min = self.current_filters.get("amount_min")
        amount_max = self.current_filters.get("amount_max")
        amount_absolute = self.current_filters.get("amount_absolute", False)

        if amount_min is not None or amount_max is not None:
            amount_str = ""
            if amount_min is not None and amount_max is not None:
                amount_str = f"${amount_min} to ${amount_max}"
            elif amount_min is not None:
                amount_str = f"≥ ${amount_min}"
            elif amount_max is not None:
                amount_str = f"≤ ${amount_max}"

            if amount_absolute:
                amount_str += " (absolute value)"

            lines.append(f"<b>Amount:</b> {amount_str}")

        if not lines:
            return "<i>No filters active</i>"

        # Join with HTML line breaks
        return "<br>".join(lines)

    def _on_name_changed(self, text: str):
        """
        Handle name input change.

        Enables/disables save button based on whether name is entered.

        Args:
            text: Current text in name input
        """
        has_name = bool(text.strip())
        self.save_btn.setEnabled(has_name)

        # Update button text to show validation
        if has_name:
            self.save_btn.setText("💾 Save Filter")
        else:
            self.save_btn.setText("💾 Save Filter (name required)")

    def _on_save_clicked(self):
        """
        Handle save button click.

        Validates input, prepares data dictionary, and emits filter_saved signal.
        """
        # Get and validate name
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            return

        # Get description (optional)
        description = self.description_input.toPlainText().strip()
        if not description:
            description = None

        # Get favorite status
        is_favorite = self.favorite_checkbox.isChecked()

        # Prepare filter data
        filter_data = {
            "name": name,
            "description": description,
            "filter_criteria": self.current_filters.copy(),  # Copy to avoid mutations
            "is_favorite": is_favorite
        }

        # Emit signal with filter data
        self.filter_saved.emit(filter_data)

        # Accept dialog (closes with success)
        self.accept()

    def get_filter_data(self) -> Optional[Dict]:
        """
        Get the filter data if dialog was accepted.

        Returns:
            Dictionary with filter data or None if cancelled

        Example:
            >>> dialog = SaveFilterDialog(filters)
            >>> if dialog.exec():
            ...     data = dialog.get_filter_data()
            ...     print(f"Name: {data['name']}")
        """
        if self.result() == QDialog.Accepted:
            return {
                "name": self.name_input.text().strip(),
                "description": self.description_input.toPlainText().strip() or None,
                "filter_criteria": self.current_filters.copy(),
                "is_favorite": self.favorite_checkbox.isChecked()
            }
        return None
