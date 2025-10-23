"""
Unified transaction dialog with tabs for Expense/Income/Transfer.

Inspired by HomeBank's excellent UX design.
"""
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Dict
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QWidget, QComboBox, QLineEdit, QDateEdit, QTextEdit, QPushButton,
    QLabel, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QDoubleValidator

from finance_app.data.database import Database
from finance_app.data.models import Account
from finance_app.data.repositories.category_repository import CategoryRepository
from finance_app.utils.logger import setup_logger

logger = setup_logger(__name__)


class UnifiedTransactionDialog(QDialog):
    """
    Unified transaction dialog with tabs for Expense/Income/Transfer.

    Inspired by HomeBank's design - one dialog handles all transaction types.
    """

    def __init__(self, database: Database, accounts: List[Account], parent=None):
        """
        Initialize unified transaction dialog.

        Args:
            database: Database instance
            accounts: List of available accounts
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = database
        self.accounts = accounts
        self.category_repo = CategoryRepository(database)
        self.transaction_type = "expense"  # Default to expense tab

        self.setup_ui()
        self.apply_styling()

        logger.info("Unified transaction dialog initialized")

    def setup_ui(self) -> None:
        """Set up user interface with HomeBank-inspired tabbed layout."""
        self.setWindowTitle("Add transaction")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.resize(450, 500)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Tab widget for Expense/Income/Transfer
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("transactionTabs")

        # Create tabs
        self.expense_tab = self._create_expense_tab()
        self.income_tab = self._create_income_tab()
        self.transfer_tab = self._create_transfer_tab()

        self.tab_widget.addTab(self.expense_tab, "Expense")
        self.tab_widget.addTab(self.income_tab, "Income")
        self.tab_widget.addTab(self.transfer_tab, "Transfer")

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        main_layout.addWidget(self.tab_widget)

        # Spacer
        main_layout.addStretch()

        # Button layout - HomeBank style
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        close_btn.setMinimumWidth(100)
        button_layout.addWidget(close_btn)

        button_layout.addStretch()

        # "Add & Keep" button - adds transaction and keeps dialog open
        self.add_keep_btn = QPushButton("Add && Keep")
        self.add_keep_btn.clicked.connect(self._on_add_and_keep)
        self.add_keep_btn.setMinimumWidth(100)
        button_layout.addWidget(self.add_keep_btn)

        # "Add" button - adds transaction and closes dialog
        self.add_btn = QPushButton("Add")
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.setDefault(True)
        self.add_btn.clicked.connect(self.accept)
        self.add_btn.setMinimumWidth(100)
        button_layout.addWidget(self.add_btn)

        main_layout.addLayout(button_layout)

    def _create_expense_tab(self) -> QWidget:
        """Create Expense tab content."""
        widget = QWidget()
        form = QFormLayout(widget)
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Date
        self.expense_date = QDateEdit()
        self.expense_date.setDate(QDate.currentDate())
        self.expense_date.setCalendarPopup(True)
        self.expense_date.setDisplayFormat("ddd MM/dd/yyyy")
        form.addRow("Date:", self.expense_date)

        # Amount - HomeBank style: input expands, buttons compact
        amount_layout = QHBoxLayout()
        amount_layout.setSpacing(4)
        self.expense_amount = QLineEdit()
        self.expense_amount.setPlaceholderText("0.00")
        validator = QDoubleValidator(0.01, 999999999.99, 2, self)
        self.expense_amount.setValidator(validator)
        amount_layout.addWidget(self.expense_amount, 1)  # Stretch factor 1 - takes most space

        # Compact adjustment buttons like HomeBank
        minus_btn = QPushButton("−")
        minus_btn.setFixedSize(32, 28)
        minus_btn.clicked.connect(lambda: self._adjust_amount(self.expense_amount, -1))
        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(32, 28)
        plus_btn.clicked.connect(lambda: self._adjust_amount(self.expense_amount, 1))
        amount_layout.addWidget(minus_btn, 0)  # No stretch
        amount_layout.addWidget(plus_btn, 0)  # No stretch

        form.addRow("Amount:", amount_layout)

        # Account
        self.expense_account = QComboBox()
        for account in self.accounts:
            subtype = account.account_subtype.value if hasattr(account.account_subtype, 'value') else account.account_subtype
            subtype_display = subtype.replace('_', ' ').title()
            display_text = f"{account.name} ({subtype_display})"
            self.expense_account.addItem(display_text, account.id)
        form.addRow("Account:", self.expense_account)

        # Number (reference/check number)
        self.expense_number = QLineEdit()
        self.expense_number.setPlaceholderText("Check number, reference...")
        form.addRow("Number:", self.expense_number)

        # Payee
        self.expense_payee = QLineEdit()
        self.expense_payee.setPlaceholderText("Who you paid")
        form.addRow("Payee:", self.expense_payee)

        # Category
        self.expense_category = QComboBox()
        expense_categories = self.category_repo.get_names("expense")
        self.expense_category.addItems(expense_categories)
        form.addRow("Category:", self.expense_category)

        # Memo
        self.expense_memo = QTextEdit()
        self.expense_memo.setPlaceholderText("Notes...")
        self.expense_memo.setMaximumHeight(60)
        form.addRow("Memo:", self.expense_memo)

        return widget

    def _create_income_tab(self) -> QWidget:
        """Create Income tab content."""
        widget = QWidget()
        form = QFormLayout(widget)
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Date
        self.income_date = QDateEdit()
        self.income_date.setDate(QDate.currentDate())
        self.income_date.setCalendarPopup(True)
        self.income_date.setDisplayFormat("ddd MM/dd/yyyy")
        form.addRow("Date:", self.income_date)

        # Amount - HomeBank style: input expands, buttons compact
        amount_layout = QHBoxLayout()
        amount_layout.setSpacing(4)
        self.income_amount = QLineEdit()
        self.income_amount.setPlaceholderText("0.00")
        validator = QDoubleValidator(0.01, 999999999.99, 2, self)
        self.income_amount.setValidator(validator)
        amount_layout.addWidget(self.income_amount, 1)  # Stretch factor 1

        minus_btn = QPushButton("−")
        minus_btn.setFixedSize(32, 28)
        minus_btn.clicked.connect(lambda: self._adjust_amount(self.income_amount, -1))
        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(32, 28)
        plus_btn.clicked.connect(lambda: self._adjust_amount(self.income_amount, 1))
        amount_layout.addWidget(minus_btn, 0)
        amount_layout.addWidget(plus_btn, 0)

        form.addRow("Amount:", amount_layout)

        # Account
        self.income_account = QComboBox()
        for account in self.accounts:
            subtype = account.account_subtype.value if hasattr(account.account_subtype, 'value') else account.account_subtype
            subtype_display = subtype.replace('_', ' ').title()
            display_text = f"{account.name} ({subtype_display})"
            self.income_account.addItem(display_text, account.id)
        form.addRow("Account:", self.income_account)

        # Number
        self.income_number = QLineEdit()
        self.income_number.setPlaceholderText("Reference number...")
        form.addRow("Number:", self.income_number)

        # Payer
        self.income_payer = QLineEdit()
        self.income_payer.setPlaceholderText("Who paid you")
        form.addRow("Payer:", self.income_payer)

        # Category
        self.income_category = QComboBox()
        income_categories = self.category_repo.get_names("income")
        self.income_category.addItems(income_categories)
        form.addRow("Category:", self.income_category)

        # Memo
        self.income_memo = QTextEdit()
        self.income_memo.setPlaceholderText("Notes...")
        self.income_memo.setMaximumHeight(60)
        form.addRow("Memo:", self.income_memo)

        return widget

    def _create_transfer_tab(self) -> QWidget:
        """Create Transfer tab content."""
        widget = QWidget()
        form = QFormLayout(widget)
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Date
        self.transfer_date = QDateEdit()
        self.transfer_date.setDate(QDate.currentDate())
        self.transfer_date.setCalendarPopup(True)
        self.transfer_date.setDisplayFormat("ddd MM/dd/yyyy")
        form.addRow("Date:", self.transfer_date)

        # Amount - HomeBank style: input expands, buttons compact
        amount_layout = QHBoxLayout()
        amount_layout.setSpacing(4)
        self.transfer_amount = QLineEdit()
        self.transfer_amount.setPlaceholderText("0.00")
        validator = QDoubleValidator(0.01, 999999999.99, 2, self)
        self.transfer_amount.setValidator(validator)
        amount_layout.addWidget(self.transfer_amount, 1)  # Stretch factor 1

        minus_btn = QPushButton("−")
        minus_btn.setFixedSize(32, 28)
        minus_btn.clicked.connect(lambda: self._adjust_amount(self.transfer_amount, -1))
        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(32, 28)
        plus_btn.clicked.connect(lambda: self._adjust_amount(self.transfer_amount, 1))
        amount_layout.addWidget(minus_btn, 0)
        amount_layout.addWidget(plus_btn, 0)

        form.addRow("Amount:", amount_layout)

        # From Account
        self.transfer_from = QComboBox()
        for account in self.accounts:
            subtype = account.account_subtype.value if hasattr(account.account_subtype, 'value') else account.account_subtype
            subtype_display = subtype.replace('_', ' ').title()
            display_text = f"{account.name} ({subtype_display})"
            self.transfer_from.addItem(display_text, account.id)
        form.addRow("From Account:", self.transfer_from)

        # To Account
        self.transfer_to = QComboBox()
        for account in self.accounts:
            subtype = account.account_subtype.value if hasattr(account.account_subtype, 'value') else account.account_subtype
            subtype_display = subtype.replace('_', ' ').title()
            display_text = f"{account.name} ({subtype_display})"
            self.transfer_to.addItem(display_text, account.id)
        # Set different default to avoid same-account selection
        if len(self.accounts) > 1:
            self.transfer_to.setCurrentIndex(1)
        form.addRow("To Account:", self.transfer_to)

        # Number
        self.transfer_number = QLineEdit()
        self.transfer_number.setPlaceholderText("Reference number...")
        form.addRow("Number:", self.transfer_number)

        # Memo
        self.transfer_memo = QTextEdit()
        self.transfer_memo.setPlaceholderText("Notes...")
        self.transfer_memo.setMaximumHeight(60)
        form.addRow("Memo:", self.transfer_memo)

        return widget

    def _adjust_amount(self, line_edit: QLineEdit, delta: int) -> None:
        """
        Adjust amount by +/- 1 (like HomeBank).

        Args:
            line_edit: The amount QLineEdit widget
            delta: +1 or -1
        """
        try:
            current = Decimal(line_edit.text() or "0")
            new_amount = max(Decimal("0"), current + Decimal(delta))
            line_edit.setText(f"{new_amount:.2f}")
        except (InvalidOperation, ValueError):
            line_edit.setText("0.00")

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab change."""
        if index == 0:
            self.transaction_type = "expense"
        elif index == 1:
            self.transaction_type = "income"
        elif index == 2:
            self.transaction_type = "transfer"
        logger.debug(f"Transaction type changed to: {self.transaction_type}")

    def _on_add_and_keep(self) -> None:
        """Add transaction and keep dialog open for next entry."""
        if self._validate_and_save():
            # Clear form fields but keep dialog open
            self._clear_current_tab()
            QMessageBox.information(
                self,
                "Transaction Added",
                "Transaction added successfully. You can add another."
            )

    def _validate_and_save(self) -> bool:
        """
        Validate current tab data and signal success.

        Returns:
            True if valid, False otherwise
        """
        # Basic validation
        current_tab = self.tab_widget.currentIndex()

        if current_tab == 0:  # Expense
            if not self.expense_amount.text().strip():
                QMessageBox.warning(self, "Invalid Amount", "Please enter an amount")
                return False
        elif current_tab == 1:  # Income
            if not self.income_amount.text().strip():
                QMessageBox.warning(self, "Invalid Amount", "Please enter an amount")
                return False
        elif current_tab == 2:  # Transfer
            if not self.transfer_amount.text().strip():
                QMessageBox.warning(self, "Invalid Amount", "Please enter an amount")
                return False
            # Check same account
            if self.transfer_from.currentData() == self.transfer_to.currentData():
                QMessageBox.warning(
                    self,
                    "Invalid Transfer",
                    "Source and destination accounts must be different"
                )
                return False

        return True

    def _clear_current_tab(self) -> None:
        """Clear form fields in current tab."""
        current_tab = self.tab_widget.currentIndex()

        if current_tab == 0:  # Expense
            self.expense_amount.clear()
            self.expense_number.clear()
            self.expense_payee.clear()
            self.expense_memo.clear()
        elif current_tab == 1:  # Income
            self.income_amount.clear()
            self.income_number.clear()
            self.income_payer.clear()
            self.income_memo.clear()
        elif current_tab == 2:  # Transfer
            self.transfer_amount.clear()
            self.transfer_number.clear()
            self.transfer_memo.clear()

    def get_transaction_data(self) -> Optional[Dict]:
        """
        Get transaction data based on current tab.

        Returns:
            Dictionary with transaction data or None if cancelled
        """
        if self.result() != QDialog.Accepted:
            return None

        current_tab = self.tab_widget.currentIndex()

        if current_tab == 0:  # Expense
            return {
                'type': 'expense',
                'account_id': self.expense_account.currentData(),
                'date': self.expense_date.date().toString("yyyy-MM-dd"),
                'amount': self.expense_amount.text().strip(),
                'category': self.expense_category.currentText(),
                'description': self.expense_payee.text().strip() or "Expense",
                'payee': self.expense_payee.text().strip(),
                'reference': self.expense_number.text().strip(),
                'memo': self.expense_memo.toPlainText().strip()
            }
        elif current_tab == 1:  # Income
            return {
                'type': 'income',
                'account_id': self.income_account.currentData(),
                'date': self.income_date.date().toString("yyyy-MM-dd"),
                'amount': self.income_amount.text().strip(),
                'category': self.income_category.currentText(),
                'description': self.income_payer.text().strip() or "Income",
                'payer': self.income_payer.text().strip(),
                'reference': self.income_number.text().strip(),
                'memo': self.income_memo.toPlainText().strip()
            }
        elif current_tab == 2:  # Transfer
            return {
                'type': 'transfer',
                'from_account_id': self.transfer_from.currentData(),
                'to_account_id': self.transfer_to.currentData(),
                'date': self.transfer_date.date().toString("yyyy-MM-dd"),
                'amount': self.transfer_amount.text().strip(),
                'description': "Transfer",
                'reference': self.transfer_number.text().strip(),
                'memo': self.transfer_memo.toPlainText().strip()
            }

        return None

    def apply_styling(self) -> None:
        """Apply QSS styling to match application dark theme."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }

            QLabel {
                color: #ffffff;
                font-size: 13px;
            }

            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                padding: 6px;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                color: #ffffff;
                font-size: 13px;
                min-height: 24px;
            }

            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border-color: #0078d4;
                background-color: #404040;
            }

            QLineEdit::placeholder, QTextEdit::placeholder {
                color: #888888;
            }

            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
                border-radius: 3px;
            }

            QTabBar::tab {
                background-color: #3c3c3c;
                color: #b0b0b0;
                padding: 8px 20px;
                border: 1px solid #555555;
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                margin-right: 2px;
            }

            QTabBar::tab:selected {
                background-color: #2b2b2b;
                color: #ffffff;
                border-bottom-color: #2b2b2b;
            }

            QTabBar::tab:hover {
                background-color: #4a4a4a;
            }

            QComboBox::drop-down {
                border: none;
                width: 20px;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #ffffff;
                width: 0;
                height: 0;
            }

            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #ffffff;
                selection-background-color: #0078d4;
                border: 1px solid #555555;
            }

            QDateEdit::drop-down {
                border: none;
                width: 20px;
            }

            QDateEdit::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #ffffff;
                width: 0;
                height: 0;
            }

            QPushButton {
                padding: 8px 24px;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                color: #ffffff;
                font-size: 13px;
                min-width: 80px;
            }

            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #666666;
            }

            QPushButton:pressed {
                background-color: #2a2a2a;
            }

            QPushButton#primaryButton {
                background-color: #0078d4;
                border-color: #0078d4;
                font-weight: bold;
            }

            QPushButton#primaryButton:hover {
                background-color: #1084e0;
            }

            QPushButton#primaryButton:pressed {
                background-color: #006cc1;
            }
        """)
