"""
Dialog for adding/editing transactions.
"""
from typing import List, Optional, Dict

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QComboBox, QDateEdit,
    QLineEdit, QPushButton
)
from PySide6.QtCore import QDate

from finance_app.data.models import Account
from finance_app.data.database import Database
from finance_app.data.repositories.category_repository import CategoryRepository
from finance_app.utils.logger import setup_logger

logger = setup_logger(__name__)


class AddTransactionDialog(QDialog):
    """Dialog for adding new transactions."""

    def __init__(self, database: Database, accounts: List[Account], parent=None):
        """
        Initialize dialog.

        Args:
            database: Database instance
            accounts: List of accounts
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = database
        self.accounts = accounts
        self.category_repo = CategoryRepository(database)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up user interface."""
        self.setWindowTitle("Add Transaction")
        self.setModal(True)
        layout = QFormLayout(self)

        # Account selection
        self.account_combo = QComboBox()
        for account in self.accounts:
            self.account_combo.addItem(f"{account.name} ({account.type})", account.id)
        layout.addRow("Account:", self.account_combo)

        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        layout.addRow("Date:", self.date_edit)

        # Description
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Enter description...")
        layout.addRow("Description:", self.description_edit)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Expense", "Income"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addRow("Type:", self.type_combo)

        # Category
        self.category_combo = QComboBox()
        self.update_categories("expense")
        layout.addRow("Category:", self.category_combo)

        # Amount
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("0.00")
        layout.addRow("Amount:", self.amount_edit)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def on_type_changed(self, text: str) -> None:
        """Handle type change."""
        trans_type = "expense" if text == "Expense" else "income"
        self.update_categories(trans_type)

    def update_categories(self, trans_type: str) -> None:
        """Update category dropdown."""
        self.category_combo.clear()
        categories = self.category_repo.get_names(trans_type)
        self.category_combo.addItems(categories)

    def get_data(self) -> Optional[Dict]:
        """
        Get form data.

        Returns:
            Dictionary with form data or None if invalid
        """
        try:
            return {
                'account_id': self.account_combo.currentData(),
                'date': self.date_edit.date().toString("yyyy-MM-dd"),
                'description': self.description_edit.text().strip(),
                'category': self.category_combo.currentText(),
                'amount': self.amount_edit.text().strip(),
                'type': self.type_combo.currentText().lower()
            }
        except Exception as e:
            logger.error(f"Failed to get dialog data: {e}")
            return None
