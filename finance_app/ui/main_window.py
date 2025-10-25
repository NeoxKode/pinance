"""
Main application window.
"""
from typing import Optional
from decimal import Decimal

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QSplitter, QMessageBox, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from finance_app.data.database import Database
from finance_app.data.models import AccountType, AccountSubtype, TransactionSplit
from finance_app.business.transaction_service import TransactionService
from finance_app.business.account_service import AccountService
from finance_app.business.double_entry_service import DoubleEntryService
from finance_app.business.split_transaction_service import SplitTransactionService
from finance_app.business.reconciliation_service import ReconciliationService
from finance_app.ui.dialogs.transaction_dialog import AddTransactionDialog
from finance_app.ui.dialogs.account_dialog import AccountDialog
from finance_app.ui.dialogs.transfer_dialog import TransferDialog
from finance_app.ui.dialogs.unified_transaction_dialog import UnifiedTransactionDialog
from finance_app.ui.dialogs.reconciliation_dialog import ReconciliationDialog
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
        self.double_entry_service = DoubleEntryService(database)
        self.split_service = SplitTransactionService(database)
        self.reconciliation_service = ReconciliationService(database)
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

        # Unified transaction dialog (HomeBank-style)
        add_trans_action = QAction("Add Transaction", self)
        add_trans_action.setShortcut("Ctrl+N")
        add_trans_action.triggered.connect(self.add_transaction_unified)
        edit_menu.addAction(add_trans_action)

        # Reconciliation dialog (US-004)
        reconcile_action = QAction("Reconcile Account...", self)
        reconcile_action.setShortcut("Ctrl+R")
        reconcile_action.triggered.connect(self.open_reconciliation_dialog)
        edit_menu.addAction(reconcile_action)

        edit_menu.addSeparator()

        # Legacy dialogs (kept for compatibility)
        add_trans_old_action = QAction("Add Transaction (Old)", self)
        add_trans_old_action.triggered.connect(self.add_transaction)
        edit_menu.addAction(add_trans_old_action)

        transfer_action = QAction("Transfer Money (Old)", self)
        transfer_action.setShortcut("Ctrl+Shift+T")
        transfer_action.triggered.connect(self.transfer_money)
        edit_menu.addAction(transfer_action)

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

        # Header with add button
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b>Accounts</b>"))
        header_layout.addStretch()

        add_account_btn = QPushButton("+ Add")
        add_account_btn.setToolTip("Add New Account")
        add_account_btn.clicked.connect(self.add_account)
        header_layout.addWidget(add_account_btn)

        layout.addLayout(header_layout)

        # Accounts table with 4 columns now
        self.account_table = QTableWidget()
        self.account_table.setColumnCount(4)
        self.account_table.setHorizontalHeaderLabels(["Account", "Type", "Subtype", "Balance"])
        self.account_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.account_table.itemSelectionChanged.connect(self.on_account_selected)
        self.account_table.setAlternatingRowColors(True)

        # Context menu for accounts
        self.account_table.setContextMenuPolicy(Qt.ActionsContextMenu)
        edit_action = QAction("Edit Account", self.account_table)
        edit_action.triggered.connect(self.edit_account)
        self.account_table.addAction(edit_action)

        delete_action = QAction("Delete Account", self.account_table)
        delete_action.triggered.connect(self.delete_account)
        self.account_table.addAction(delete_action)

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
        add_btn.setToolTip("Add transaction (Ctrl+N)")
        add_btn.clicked.connect(self.add_transaction_unified)
        control_layout.addWidget(add_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_transaction)
        control_layout.addWidget(delete_btn)

        layout.addLayout(control_layout)

        # Transaction table (US-004: Added Status column)
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(6)
        self.transaction_table.setHorizontalHeaderLabels([
            "Date", "Description", "Category", "Amount", "Type", "Status"
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
        """Load accounts into table with new type information."""
        try:
            accounts = self.account_service.get_all_accounts()
            self.account_table.setRowCount(len(accounts))

            # Account type icons/prefixes
            type_icons = {
                AccountType.ASSET: '💰',
                AccountType.LIABILITY: '💳',
                AccountType.EQUITY: '📊',
                AccountType.INCOME: '💵',
                AccountType.EXPENSE: '💸'
            }

            for i, account in enumerate(accounts):
                # Account name
                name_item = QTableWidgetItem(account.name)
                name_item.setData(Qt.UserRole, account.id)  # Store account ID
                self.account_table.setItem(i, 0, name_item)

                # Account type with icon (handle both enum and string)
                type_val = account.account_type.value if hasattr(account.account_type, 'value') else account.account_type
                # Convert string to enum for icon lookup
                try:
                    type_enum = AccountType(type_val) if isinstance(type_val, str) else account.account_type
                    type_icon = type_icons.get(type_enum, '')
                except (ValueError, KeyError):
                    type_icon = ''
                type_display = f"{type_icon} {type_val.capitalize()}"
                type_item = QTableWidgetItem(type_display)
                self.account_table.setItem(i, 1, type_item)

                # Account subtype (friendly name) - handle both enum and string
                subtype_val = account.account_subtype.value if hasattr(account.account_subtype, 'value') else account.account_subtype
                subtype_display = subtype_val.replace('_', ' ').title()
                subtype_item = QTableWidgetItem(subtype_display)
                self.account_table.setItem(i, 2, subtype_item)

                # Balance with color coding
                balance_item = QTableWidgetItem(f"${abs(account.balance):.2f}")

                # Color code based on account type and balance
                if account.account_type == AccountType.ASSET:
                    if account.balance >= 0:
                        balance_item.setForeground(Qt.darkGreen)
                    else:
                        balance_item.setForeground(Qt.red)
                elif account.account_type == AccountType.LIABILITY:
                    # For liabilities, show in red (money owed)
                    balance_item.setForeground(Qt.red)
                elif account.account_type == AccountType.INCOME:
                    balance_item.setForeground(Qt.darkGreen)
                elif account.account_type == AccountType.EXPENSE:
                    balance_item.setForeground(Qt.red)

                self.account_table.setItem(i, 3, balance_item)

            self.account_table.resizeColumnsToContents()

            # Update total balance
            total = self.account_service.get_total_balance()
            total_color = "green" if total >= 0 else "red"
            self.balance_label.setText(f"Total Balance: <span style='color: {total_color};'>${total:.2f}</span>")

        except FinanceAppError as e:
            logger.error(f"Failed to load accounts: {e}")
            raise

    def _load_transactions(self, account_id: Optional[int] = None) -> None:
        """
        Load transactions into table.

        US-004: Phase 6 - Task 4.37 - Added reconciliation status column
        """
        try:
            transactions = self.transaction_service.get_all_transactions(account_id)
            self.transaction_table.setRowCount(len(transactions))

            for i, trans in enumerate(transactions):
                # Date
                self.transaction_table.setItem(i, 0, QTableWidgetItem(trans.date))

                # Description
                self.transaction_table.setItem(i, 1, QTableWidgetItem(trans.description))

                # Category
                self.transaction_table.setItem(i, 2, QTableWidgetItem(trans.category))

                # Amount with color
                amount_item = QTableWidgetItem(f"${abs(trans.amount):.2f}")
                amount_item.setData(Qt.UserRole, trans.id)  # Store transaction ID
                if trans.is_expense:
                    amount_item.setForeground(Qt.red)
                else:
                    amount_item.setForeground(Qt.darkGreen)
                self.transaction_table.setItem(i, 3, amount_item)

                # Type
                self.transaction_table.setItem(i, 4, QTableWidgetItem(trans.type.capitalize()))

                # US-004: Reconciliation Status (Task 4.37)
                status_text = ""
                status_tooltip = ""

                # Get reconciliation status from transaction
                recon_status = trans.reconciliation_status
                if hasattr(recon_status, 'value'):
                    recon_status = recon_status.value

                if recon_status == 'cleared':
                    status_text = "✓ Reconciled"
                    status_tooltip = f"Reconciled on {trans.reconciled_date}" if trans.reconciled_date else "Reconciled"
                elif recon_status == 'pending':
                    status_text = "⏳ Pending"
                    status_tooltip = "Reconciliation in progress"
                else:
                    status_text = ""
                    status_tooltip = "Not reconciled"

                status_item = QTableWidgetItem(status_text)
                status_item.setToolTip(status_tooltip)
                if recon_status == 'cleared':
                    status_item.setForeground(Qt.darkGreen)
                elif recon_status == 'pending':
                    status_item.setForeground(Qt.darkYellow)
                self.transaction_table.setItem(i, 5, status_item)

            self.transaction_table.resizeColumnsToContents()

        except FinanceAppError as e:
            logger.error(f"Failed to load transactions: {e}")
            raise

    def on_account_selected(self) -> None:
        """Handle account selection."""
        selected_items = self.account_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            # Account ID is stored in the name column (column 0)
            name_item = self.account_table.item(row, 0)
            self.current_account_id = name_item.data(Qt.UserRole)
            self._load_transactions(self.current_account_id)
            account_name = name_item.text()
            self.statusBar().showMessage(f"Showing transactions for: {account_name}")

    def add_transaction(self) -> None:
        """Show dialog to add transaction (legacy)."""
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

    def add_transaction_unified(self) -> None:
        """Show unified transaction dialog (HomeBank-style with tabs)."""
        try:
            accounts = self.account_service.get_all_accounts()
            dialog = UnifiedTransactionDialog(self.db, accounts, self)

            if dialog.exec():
                data = dialog.get_transaction_data()
                if data:
                    if data['type'] == 'transfer':
                        # Handle transfer using double-entry service
                        group, entries = self.double_entry_service.create_transfer(
                            from_account_id=data['from_account_id'],
                            to_account_id=data['to_account_id'],
                            amount=Decimal(data['amount']),
                            date=data['date'],
                            description=data.get('description', 'Transfer'),
                            reference_number=data.get('reference'),
                            notes=data.get('memo')
                        )
                        self.load_data()
                        self.statusBar().showMessage(
                            f"Transfer of ${data['amount']} completed successfully"
                        )
                        logger.info(f"Transfer completed via unified dialog: group_id={group.id}")
                    else:
                        # Handle expense/income using transaction service
                        transaction = self.transaction_service.create_transaction(
                            account_id=data['account_id'],
                            date=data['date'],
                            description=data['description'],
                            category=data['category'],
                            amount=data['amount'],
                            trans_type=data['type']
                        )

                        # Check if splits exist
                        if data.get('splits'):
                            splits_data = data['splits']
                            logger.info(f"Creating split transaction with {len(splits_data)} splits")

                            # Convert split dictionaries to TransactionSplit objects
                            splits = []
                            for i, split_dict in enumerate(splits_data):
                                split = TransactionSplit(
                                    id=None,
                                    transaction_id=transaction.id,
                                    group_id=None,  # Will be assigned by service
                                    split_order=i,
                                    category_id=split_dict['category_id'],
                                    amount=Decimal(str(split_dict['amount'])),
                                    memo=split_dict.get('memo'),
                                    account_id=split_dict.get('account_id')
                                )
                                splits.append(split)

                            # Create splits via service
                            txn, created_splits, group = self.split_service.create_split_transaction(
                                transaction_id=transaction.id,
                                splits=splits
                            )

                            self.load_data()
                            self.statusBar().showMessage(
                                f"{data['type'].capitalize()} with {len(created_splits)} splits added successfully"
                            )
                            logger.info(
                                f"Split {data['type']} created: txn_id={txn.id}, "
                                f"splits={len(created_splits)}, group_id={group.id if group else None}"
                            )
                        else:
                            # Regular transaction without splits
                            self.load_data()
                            self.statusBar().showMessage(
                                f"{data['type'].capitalize()} added successfully"
                            )
                            logger.info(f"{data['type'].capitalize()} added via unified dialog")

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

    def add_account(self) -> None:
        """Show dialog to add a new account."""
        try:
            dialog = AccountDialog(self.account_service, parent=self)

            if dialog.exec():
                self.load_data()
                self.statusBar().showMessage("Account added successfully")
                logger.info("Account added via UI")

        except FinanceAppError as e:
            logger.error(f"Failed to add account: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add account: {e}")
        except Exception as e:
            import traceback
            logger.error(f"Unexpected error adding account: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            QMessageBox.critical(self, "Error", f"Unexpected error: {e}")

    def edit_account(self) -> None:
        """Show dialog to edit selected account."""
        selected_items = self.account_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an account to edit")
            return

        try:
            # Get account ID from first column
            row = selected_items[0].row()
            account_id = self.account_table.item(row, 0).data(Qt.UserRole)

            # Get account details
            account = self.account_service.get_account(account_id)
            if not account:
                QMessageBox.warning(self, "Error", "Account not found")
                return

            # Show edit dialog
            dialog = AccountDialog(self.account_service, account=account, parent=self)

            if dialog.exec():
                self.load_data()
                self.statusBar().showMessage("Account updated successfully")
                logger.info(f"Account edited via UI: {account_id}")

        except FinanceAppError as e:
            logger.error(f"Failed to edit account: {e}")
            QMessageBox.critical(self, "Error", f"Failed to edit account: {e}")
        except Exception as e:
            logger.error(f"Unexpected error editing account: {e}")
            QMessageBox.critical(self, "Error", f"Unexpected error: {e}")

    def delete_account(self) -> None:
        """Delete selected account."""
        selected_items = self.account_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an account to delete")
            return

        row = selected_items[0].row()
        account_name = self.account_table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete account '{account_name}'?\n\n"
            "This will also delete all associated transactions!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                account_id = self.account_table.item(row, 0).data(Qt.UserRole)
                self.account_service.delete_account(account_id)
                self.load_data()
                self.statusBar().showMessage(f"Account '{account_name}' deleted")
                logger.info(f"Account deleted via UI: {account_id}")

            except FinanceAppError as e:
                logger.error(f"Failed to delete account: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete account: {e}")
            except Exception as e:
                logger.error(f"Unexpected error deleting account: {e}")
                QMessageBox.critical(self, "Error", f"Unexpected error: {e}")

    def transfer_money(self) -> None:
        """Open transfer dialog and process transfer."""
        try:
            # Get all accounts for selection
            accounts = self.account_service.get_all_accounts()

            if len(accounts) < 2:
                QMessageBox.warning(
                    self,
                    "Insufficient Accounts",
                    "You need at least 2 accounts to make a transfer."
                )
                return

            # Open transfer dialog
            dialog = TransferDialog(self.db, accounts, self)

            if dialog.exec():
                transfer_data = dialog.get_transfer_data()

                if transfer_data:
                    # Execute transfer using double-entry service
                    group, entries = self.double_entry_service.create_transfer(
                        from_account_id=transfer_data['from_account_id'],
                        to_account_id=transfer_data['to_account_id'],
                        amount=transfer_data['amount'],
                        date=transfer_data['date'],
                        description=transfer_data['description'],
                        reference_number=transfer_data.get('reference_number'),
                        notes=transfer_data.get('notes')
                    )

                    # Refresh displays
                    self._load_accounts()
                    self._load_transactions()

                    # Show success message
                    self.statusBar().showMessage(
                        f"Transfer of ${transfer_data['amount']} completed successfully",
                        5000
                    )
                    logger.info(f"Transfer completed: group_id={group.id}")

        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            QMessageBox.critical(
                self,
                "Transfer Failed",
                f"Failed to complete transfer:\n{str(e)}"
            )

    def open_reconciliation_dialog(self) -> None:
        """
        Open reconciliation dialog for the selected account.

        US-004: Phase 6 - MainWindow Integration (Task 4.35)
        """
        try:
            # Get currently selected account
            selected_rows = self.account_table.selectedItems()
            if not selected_rows:
                QMessageBox.warning(
                    self,
                    "No Account Selected",
                    "Please select an account to reconcile."
                )
                return

            # Get account ID from selected row
            row = selected_rows[0].row()
            account_id_item = self.account_table.item(row, 0)
            if not account_id_item:
                logger.error("Could not get account ID from selected row")
                return

            # Get the account ID stored in the item's data
            account_id = account_id_item.data(Qt.UserRole)
            if not account_id:
                logger.error("Account ID not found in item data")
                return

            # Get account object
            account = self.account_service.get_account(account_id)
            if not account:
                QMessageBox.warning(
                    self,
                    "Account Not Found",
                    f"Account with ID {account_id} not found."
                )
                return

            # Open reconciliation dialog
            dialog = ReconciliationDialog(self.db, account, self)

            # Connect signal to refresh UI after reconciliation
            dialog.reconciliation_completed.connect(self._on_reconciliation_completed)

            # Show dialog
            if dialog.exec() == QDialog.Accepted:
                logger.info(f"Reconciliation dialog accepted for account: {account.name}")
            else:
                logger.info(f"Reconciliation dialog cancelled for account: {account.name}")

        except FinanceAppError as e:
            logger.error(f"Failed to open reconciliation dialog: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open reconciliation dialog:\n{str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error opening reconciliation dialog: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Unexpected error:\n{str(e)}"
            )

    def _on_reconciliation_completed(self, reconciliation_id: int) -> None:
        """
        Handle reconciliation completion.

        US-004: Phase 6 - Task 4.39 - Refresh transaction list after reconciliation

        Args:
            reconciliation_id: ID of the completed reconciliation
        """
        try:
            # Refresh all data to show updated reconciliation status
            self._load_accounts()
            self._load_transactions()

            # Show status message
            self.statusBar().showMessage(
                f"Reconciliation #{reconciliation_id} completed successfully",
                5000
            )

            logger.info(f"UI refreshed after reconciliation: {reconciliation_id}")

        except Exception as e:
            logger.error(f"Failed to refresh UI after reconciliation: {e}")

    def show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Personal Finance Manager",
            "Personal Finance Manager v2.0\n\n"
            "A simple personal finance application built with Python and PySide6.\n"
            "Inspired by HomeBank.\n\n"
            "Features:\n"
            "- Double-entry accounting system\n"
            "- Multiple account types (Assets, Liabilities, Equity, Income, Expense)\n"
            "- Transaction tracking\n"
            "- Category management\n"
            "- Balance summaries\n\n"
            "Built with ❤️ using PySide6"
        )
