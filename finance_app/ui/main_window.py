"""
Main application window.
"""
from typing import Optional
from decimal import Decimal

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QSplitter, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from finance_app.data.database import Database
from finance_app.business.transaction_service import TransactionService
from finance_app.business.account_service import AccountService
from finance_app.ui.dialogs.transaction_dialog import AddTransactionDialog
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import FinanceAppError

logger = setup_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, database: Database):
        """
        Initialize main window.

        Args:
            database: Database instance
        """
        super().__init__()
        self.db = database
        self.transaction_service = TransactionService(database)
        self.account_service = AccountService(database)
        self.current_account_id: Optional[int] = None

        self.setup_ui()
        self.load_data()

        logger.info("Main window initialized")

    def setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("Personal Finance Manager")
        self.setGeometry(100, 100, 1000, 600)

        # Menu bar
        self._create_menu_bar()

        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Accounts
        splitter.addWidget(self._create_account_panel())

        # Right panel - Transactions
        splitter.addWidget(self._create_transaction_panel())

        splitter.setSizes([300, 700])
        main_layout.addWidget(splitter)

        # Status bar
        self.statusBar().showMessage("Ready")

    def _create_menu_bar(self) -> None:
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New File", self)
        file_menu.addAction(new_action)

        open_action = QAction("Open File", self)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        add_trans_action = QAction("Add Transaction", self)
        add_trans_action.triggered.connect(self.add_transaction)
        edit_menu.addAction(add_trans_action)

        # View menu
        view_menu = menubar.addMenu("View")
        reports_action = QAction("Reports", self)
        view_menu.addAction(reports_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _create_account_panel(self) -> QWidget:
        """Create left panel with accounts."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("<b>Accounts</b>"))

        self.account_table = QTableWidget()
        self.account_table.setColumnCount(3)
        self.account_table.setHorizontalHeaderLabels(["Account", "Type", "Balance"])
        self.account_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.account_table.itemSelectionChanged.connect(self.on_account_selected)
        layout.addWidget(self.account_table)

        # Summary
        self.balance_label = QLabel("Total Balance: $0.00")
        self.balance_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.balance_label)

        return panel

    def _create_transaction_panel(self) -> QWidget:
        """Create right panel with transactions."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Transaction controls
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("<b>Transactions</b>"))
        control_layout.addStretch()

        add_btn = QPushButton("+ Add Transaction")
        add_btn.clicked.connect(self.add_transaction)
        control_layout.addWidget(add_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_transaction)
        control_layout.addWidget(delete_btn)

        layout.addLayout(control_layout)

        # Transaction table
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(5)
        self.transaction_table.setHorizontalHeaderLabels([
            "Date", "Description", "Category", "Amount", "Type"
        ])
        self.transaction_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.transaction_table)

        return panel

    def load_data(self) -> None:
        """Load all data from database."""
        try:
            self._load_accounts()
            self._load_transactions()
        except FinanceAppError as e:
            logger.error(f"Failed to load data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")

    def _load_accounts(self) -> None:
        """Load accounts into table."""
        try:
            accounts = self.account_service.get_all_accounts()
            self.account_table.setRowCount(len(accounts))

            for i, account in enumerate(accounts):
                self.account_table.setItem(i, 0, QTableWidgetItem(account.name))
                self.account_table.setItem(i, 1, QTableWidgetItem(account.type.capitalize()))

                balance_item = QTableWidgetItem(f"${account.balance:.2f}")
                balance_item.setData(Qt.UserRole, account.id)  # Store account ID
                self.account_table.setItem(i, 2, balance_item)

            self.account_table.resizeColumnsToContents()

            # Update total balance
            total = self.account_service.get_total_balance()
            self.balance_label.setText(f"Total Balance: ${total:.2f}")

        except FinanceAppError as e:
            logger.error(f"Failed to load accounts: {e}")
            raise

    def _load_transactions(self, account_id: Optional[int] = None) -> None:
        """Load transactions into table."""
        try:
            transactions = self.transaction_service.get_all_transactions(account_id)
            self.transaction_table.setRowCount(len(transactions))

            for i, trans in enumerate(transactions):
                self.transaction_table.setItem(i, 0, QTableWidgetItem(trans.date))
                self.transaction_table.setItem(i, 1, QTableWidgetItem(trans.description))
                self.transaction_table.setItem(i, 2, QTableWidgetItem(trans.category))

                # Format amount with color
                amount_item = QTableWidgetItem(f"${abs(trans.amount):.2f}")
                amount_item.setData(Qt.UserRole, trans.id)  # Store transaction ID
                if trans.is_expense:
                    amount_item.setForeground(Qt.red)
                else:
                    amount_item.setForeground(Qt.darkGreen)
                self.transaction_table.setItem(i, 3, amount_item)

                self.transaction_table.setItem(i, 4, QTableWidgetItem(trans.type.capitalize()))

            self.transaction_table.resizeColumnsToContents()

        except FinanceAppError as e:
            logger.error(f"Failed to load transactions: {e}")
            raise

    def on_account_selected(self) -> None:
        """Handle account selection."""
        selected_items = self.account_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            balance_item = self.account_table.item(row, 2)
            self.current_account_id = balance_item.data(Qt.UserRole)
            self._load_transactions(self.current_account_id)
            account_name = self.account_table.item(row, 0).text()
            self.statusBar().showMessage(f"Showing transactions for: {account_name}")

    def add_transaction(self) -> None:
        """Show dialog to add transaction."""
        try:
            accounts = self.account_service.get_all_accounts()
            dialog = AddTransactionDialog(self.db, accounts, self)

            if dialog.exec():
                data = dialog.get_data()
                if data:
                    self.transaction_service.create_transaction(
                        account_id=data['account_id'],
                        date=data['date'],
                        description=data['description'],
                        category=data['category'],
                        amount=data['amount'],
                        trans_type=data['type']
                    )
                    self.load_data()
                    self.statusBar().showMessage("Transaction added successfully")
                    logger.info("Transaction added via UI")

        except FinanceAppError as e:
            logger.error(f"Failed to add transaction: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add transaction: {e}")
        except Exception as e:
            logger.error(f"Unexpected error adding transaction: {e}")
            QMessageBox.critical(self, "Error", f"Unexpected error: {e}")

    def delete_transaction(self) -> None:
        """Delete selected transaction."""
        selected_items = self.transaction_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a transaction to delete")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this transaction?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                row = selected_items[0].row()
                trans_id = self.transaction_table.item(row, 3).data(Qt.UserRole)

                self.transaction_service.delete_transaction(trans_id)
                self.load_data()
                self.statusBar().showMessage("Transaction deleted")
                logger.info(f"Transaction deleted via UI: {trans_id}")

            except FinanceAppError as e:
                logger.error(f"Failed to delete transaction: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete transaction: {e}")
            except Exception as e:
                logger.error(f"Unexpected error deleting transaction: {e}")
                QMessageBox.critical(self, "Error", f"Unexpected error: {e}")

    def show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Personal Finance Manager",
            "Personal Finance Manager v1.0\n\n"
            "A simple personal finance application built with Python and PySide6.\n"
            "Inspired by HomeBank.\n\n"
            "Features:\n"
            "- Multiple accounts\n"
            "- Transaction tracking\n"
            "- Category management\n"
            "- Balance summaries"
        )
