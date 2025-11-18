"""
Custom Date Range Picker Dialog.

US-012: Date Range Filter - Allows users to select custom date ranges
for filtering transactions. Provides calendar popups and validates that
from_date <= to_date.

Created: 2025-11-17
Story: US-012 - Date Range Filter (EPIC-002, Sprint 14)
"""

from datetime import date, timedelta
from typing import Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QDateEdit, QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QKeySequence, QShortcut

from finance_app.business.date_range_utils import DateRange


class DateRangeDialog(QDialog):
    """
    Custom date range picker dialog.

    US-012: Allows users to select a custom date range for filtering transactions.
    Provides calendar popups for easy date selection and validates that the
    from_date is not greater than the to_date.

    Features:
        - Calendar popups for both From and To dates
        - Smart defaults (from = 1 month ago, to = today)
        - Validation prevents invalid ranges (from > to)
        - Enter key triggers Apply
        - Escape key triggers Cancel
        - Clear error messages for validation failures

    Usage:
        >>> dialog = DateRangeDialog(parent)
        >>> if dialog.exec() == QDialog.Accepted:
        >>>     from_date, to_date = dialog.get_date_range()
        >>>     print(f"Selected: {from_date} to {to_date}")

    Design:
        - Width: 400px minimum
        - Height: Auto (based on content)
        - Modal: Yes (blocks parent window)
        - Focus: From date field
    """

    def __init__(self, parent=None):
        """
        Initialize custom date range dialog.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        self._setup_ui()
        self._apply_styling()
        self._connect_shortcuts()

    def _setup_ui(self):
        """
        Create the dialog user interface.

        Layout:
            1. Title label
            2. Form with From/To date pickers
            3. Help text
            4. Button row (Cancel, Apply)
        """
        self.setWindowTitle("Select Date Range")
        self.setModal(True)
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("<h3>Select Custom Date Range</h3>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Form layout for date pickers
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form_layout.setSpacing(12)

        # From date picker
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setDisplayFormat("MMM dd, yyyy")
        self.from_date_edit.setMinimumWidth(200)

        # Set default to 1 month ago
        default_from = date.today() - timedelta(days=30)
        self.from_date_edit.setDate(QDate(default_from.year, default_from.month, default_from.day))

        form_layout.addRow("<b>From Date:</b>", self.from_date_edit)

        # To date picker
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setDisplayFormat("MMM dd, yyyy")
        self.to_date_edit.setMinimumWidth(200)

        # Set default to today
        today = date.today()
        self.to_date_edit.setDate(QDate(today.year, today.month, today.day))

        form_layout.addRow("<b>To Date:</b>", self.to_date_edit)

        layout.addLayout(form_layout)

        # Help text
        help_label = QLabel(
            "<i>Select the start and end dates for filtering transactions.<br>"
            "Both dates are inclusive in the filter results.</i>"
        )
        help_label.setAlignment(Qt.AlignCenter)
        help_label.setWordWrap(True)
        help_label.setObjectName("helpLabel")
        layout.addWidget(help_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setObjectName("primaryButton")
        self.apply_btn.setMinimumWidth(100)
        self.apply_btn.setDefault(True)  # Enter key triggers this
        self.apply_btn.clicked.connect(self._validate_and_accept)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.apply_btn)

        layout.addLayout(button_layout)

        # Set focus to from_date field
        self.from_date_edit.setFocus()

    def _apply_styling(self):
        """
        Apply QSS styling to dialog.

        Styling includes:
        - Clean white background
        - Blue primary button
        - Subtle borders on date pickers
        - Proper spacing and padding
        """
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }

            QLabel#helpLabel {
                color: #666;
                font-size: 12px;
                padding: 8px;
            }

            QDateEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                font-size: 13px;
                background-color: white;
            }

            QDateEdit:focus {
                border-color: #2196F3;
            }

            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #e0e0e0;
            }

            QDateEdit::down-arrow {
                image: none;
                border: none;
            }

            QPushButton {
                padding: 8px 16px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }

            QPushButton:hover {
                background-color: #f5f5f5;
            }

            QPushButton:pressed {
                background-color: #e0e0e0;
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

            QPushButton#primaryButton:focus {
                border: 2px solid #0D47A1;
                outline: 2px solid #93C5FD;
                outline-offset: 2px;
            }
        """)

    def _connect_shortcuts(self):
        """
        Connect keyboard shortcuts.

        Shortcuts:
            - Enter: Apply (handled by default button)
            - Escape: Cancel (built-in QDialog behavior)
        """
        # Escape key closes dialog (built-in)
        # Enter key handled by setDefault(True) on apply_btn
        pass

    def _validate_and_accept(self):
        """
        Validate date range and accept dialog.

        Validates that from_date <= to_date using backend validation.
        Shows error message if validation fails.

        Validation Rules:
            - from_date must be <= to_date
            - Uses DateRange.validate_custom_range() from backend
        """
        # Get dates from pickers
        from_date = self.from_date_edit.date().toPython()
        to_date = self.to_date_edit.date().toPython()

        # Validate using backend utility
        try:
            DateRange.validate_custom_range(from_date, to_date)
        except ValueError as e:
            # Show error message
            QMessageBox.warning(
                self,
                "Invalid Date Range",
                f"The date range is invalid:\n\n{str(e)}\n\n"
                "Please ensure the 'From' date is not after the 'To' date."
            )

            # Focus the from_date field for correction
            self.from_date_edit.setFocus()
            self.from_date_edit.selectAll()
            return

        # Validation passed - accept dialog
        self.accept()

    def get_date_range(self) -> Tuple[date, date]:
        """
        Get selected date range.

        Returns:
            Tuple of (from_date, to_date) as Python date objects

        Usage:
            >>> if dialog.exec() == QDialog.Accepted:
            >>>     from_date, to_date = dialog.get_date_range()

        Note:
            Should only be called after dialog.exec() returns QDialog.Accepted.
            Both dates are guaranteed to be valid (from_date <= to_date) due
            to validation in _validate_and_accept().
        """
        return (
            self.from_date_edit.date().toPython(),
            self.to_date_edit.date().toPython()
        )
