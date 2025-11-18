"""
Main application window.
"""
from typing import Optional
from decimal import Decimal

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QSplitter, QMessageBox, QDialog, QCheckBox,
    QHeaderView, QLineEdit
)
from finance_app.ui.widgets import AccountTreeWidget, TransactionSearchWidget, SearchPanelWidget
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
from finance_app.ui.dialogs.set_opening_balance_dialog import SetOpeningBalanceDialog
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

        # US-012: Date filter state
        self.current_date_from = None
        self.current_date_to = None
        self.current_search_keyword = None  # Track text search state

        # US-013: Category filter state
        self.current_categories = []  # Track selected categories for filtering

        self.setup_ui()
        self.load_data()

        logger.info("Main window initialized")

    def setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("Personal Finance Manager")
        self.setGeometry(100, 100, 1000, 600)

        # ISSUE-007 FIX: Add clear keyboard focus indicators (WCAG accessibility)
        self.setStyleSheet("""
            /* Keyboard focus indicators for buttons */
            QPushButton:focus {
                border: 2px solid #3B82F6;
                outline: 2px solid #93C5FD;
                outline-offset: 2px;
            }

            /* Keyboard focus indicators for table widgets */
            QTableWidget:focus {
                border: 2px solid #3B82F6;
            }

            /* Keyboard focus indicators for tree widgets */
            QTreeWidget:focus, QTreeView:focus {
                border: 2px solid #3B82F6;
            }

            /* Keyboard focus indicators for checkboxes */
            QCheckBox:focus {
                outline: 2px solid #3B82F6;
                outline-offset: 2px;
            }

            /* Keyboard focus indicators for menu items */
            QMenu::item:focus {
                background-color: #DBEAFE;
                color: #1E40AF;
            }
        """)

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

        # US-006: Increased left panel size to show Balance column (300px Account + 150px Balance = 450px minimum)
        splitter.setSizes([500, 500])
        main_layout.addWidget(splitter)

        # Status bar
        self.statusBar().showMessage("Ready")

    def _create_menu_bar(self) -> None:
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        # TODO: Implement New/Open File when multi-database support is added
        # new_action = QAction("New File", self)
        # new_action.triggered.connect(self.new_file)
        # file_menu.addAction(new_action)
        #
        # open_action = QAction("Open File", self)
        # open_action.triggered.connect(self.open_file)
        # file_menu.addAction(open_action)
        #
        # file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        # Transaction operations
        add_trans_action = QAction("Add Transaction...", self)
        add_trans_action.setShortcut("Ctrl+N")
        add_trans_action.setToolTip("Create a new transaction")
        add_trans_action.triggered.connect(self.add_transaction_unified)
        edit_menu.addAction(add_trans_action)

        delete_trans_action = QAction("Delete Transaction", self)
        delete_trans_action.setShortcut("Ctrl+D")
        delete_trans_action.setToolTip("Delete the selected transaction")
        delete_trans_action.triggered.connect(self.delete_transaction)
        edit_menu.addAction(delete_trans_action)

        edit_menu.addSeparator()

        # US-011: Search operations
        search_account_action = QAction("Search in Account...", self)
        search_account_action.setShortcut("Ctrl+F")
        search_account_action.setToolTip("Search transactions in current account")
        search_account_action.triggered.connect(self._focus_search_in_account)
        edit_menu.addAction(search_account_action)

        search_all_action = QAction("Search All Accounts...", self)
        search_all_action.setShortcut("Ctrl+Shift+F")
        search_all_action.setToolTip("Search transactions across all accounts")
        search_all_action.triggered.connect(self._focus_search_all_accounts)
        edit_menu.addAction(search_all_action)

        edit_menu.addSeparator()

        # Account operations
        new_account_action = QAction("New Account...", self)
        new_account_action.setShortcut("Ctrl+Shift+N")
        new_account_action.setToolTip("Create a new account")
        new_account_action.triggered.connect(self.add_account)
        edit_menu.addAction(new_account_action)

        reconcile_action = QAction("Reconcile Account...", self)
        reconcile_action.setShortcut("Ctrl+R")
        reconcile_action.setToolTip("Reconcile the selected account")
        reconcile_action.triggered.connect(self.open_reconciliation_dialog)
        edit_menu.addAction(reconcile_action)

        # Legacy dialogs removed - unified transaction dialog is sufficient
        # Previous items: Add Transaction (Old), Transfer Money (Old)
        # Users can use the unified "Add Transaction" dialog for all transaction types

        # TODO: BUG-FIX-009 - Add View menu back in EPIC-003 when Reports are implemented
        # View menu removed because it was empty after Bug #8 fix
        # See docs/technical-reviews/FINAL_COMPREHENSIVE_UI_REVIEW.md - Bug #9
        # view_menu = menubar.addMenu("View")
        # reports_action = QAction("Reports", self)
        # view_menu.addAction(reports_action)

        # Tools menu (US-010)
        tools_menu = menubar.addMenu("Tools")

        # Validate All Accounts action
        validate_action = QAction("Validate Account Balances...", self)
        validate_action.setShortcut("Ctrl+Shift+V")
        validate_action.setToolTip("Validate all account balances against journal entries")
        validate_action.triggered.connect(self.validate_all_accounts)
        tools_menu.addAction(validate_action)

        # Trial Balance action
        trial_balance_action = QAction("Trial Balance Report...", self)
        trial_balance_action.setShortcut("Ctrl+T")
        trial_balance_action.setToolTip("Generate trial balance report")
        trial_balance_action.triggered.connect(self.show_trial_balance)
        tools_menu.addAction(trial_balance_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.setShortcut("F1")
        shortcuts_action.setToolTip("Show keyboard shortcuts reference")
        shortcuts_action.triggered.connect(self.show_keyboard_shortcuts)
        help_menu.addAction(shortcuts_action)

        help_menu.addSeparator()

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

        # US-005: Show/Hide System Accounts toggle
        self.show_system_accounts_checkbox = QCheckBox("Show System Accounts")
        self.show_system_accounts_checkbox.setToolTip("Show/hide system accounts like Opening Balance Equity")
        self.show_system_accounts_checkbox.setChecked(True)  # Show by default
        self.show_system_accounts_checkbox.stateChanged.connect(self._load_accounts)
        header_layout.addWidget(self.show_system_accounts_checkbox)

        # US-009: Show Favorites Only toggle
        self.show_favorites_only_checkbox = QCheckBox("⭐ Favorites Only")
        self.show_favorites_only_checkbox.setToolTip("Show only favorite accounts")
        self.show_favorites_only_checkbox.setChecked(False)  # Show all by default
        self.show_favorites_only_checkbox.stateChanged.connect(self._on_favorites_filter_changed)
        header_layout.addWidget(self.show_favorites_only_checkbox)

        add_account_btn = QPushButton("+ Add")
        add_account_btn.setToolTip("Add New Account")
        add_account_btn.clicked.connect(self.add_account)
        header_layout.addWidget(add_account_btn)

        layout.addLayout(header_layout)

        # US-007: Multi-field search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)

        self.account_search_box = QLineEdit()
        self.account_search_box.setPlaceholderText("Search by name, account number, or institution...")
        self.account_search_box.setToolTip(
            "Search accounts by:\n"
            "• Account name\n"
            "• Account number\n"
            "• Institution name"
        )
        self.account_search_box.setClearButtonEnabled(True)
        self.account_search_box.textChanged.connect(self._on_account_search_changed)
        search_layout.addWidget(self.account_search_box)

        layout.addLayout(search_layout)

        # US-006: Replace table with hierarchical tree widget
        self.account_tree = AccountTreeWidget(self.account_service)
        self.account_tree.account_selected.connect(self.on_account_selected)

        # BUG-FIX: Connect edit, delete, and opening balance signals
        self.account_tree.account_edit_requested.connect(self.edit_account)
        self.account_tree.account_delete_requested.connect(self.delete_account)
        self.account_tree.opening_balance_requested.connect(self.set_opening_balance)

        layout.addWidget(self.account_tree)

        # Summary
        self.balance_label = QLabel("Total Balance: $0.00")
        self.balance_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.balance_label)

        return panel

    def _create_transaction_panel(self) -> QWidget:
        """Create right panel with transactions."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # US-016: Create search/filter panel (foundation for all filters)
        self.search_panel = SearchPanelWidget()
        self.search_panel.filters_cleared.connect(self._on_filters_cleared)
        layout.addWidget(self.search_panel)  # Panel above transaction list

        # US-011: Create search widget and integrate into panel
        self.transaction_search = TransactionSearchWidget()
        self.search_panel.set_text_search_widget(self.transaction_search)
        self.transaction_search.search_changed.connect(self._on_search_changed)

        # US-012: Connect date filter signal
        self.search_panel.date_filter_changed.connect(self._on_date_filter_changed)

        # US-013: Set transaction service and connect category filter signal
        self.search_panel.set_transaction_service(self.transaction_service)
        self.search_panel.category_filter_changed.connect(self._on_category_filter_changed)

        # Transaction controls
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("<b>Transactions</b>"))

        control_layout.addStretch()

        # US-005: Filter toggle for opening balance transactions
        self.show_opening_balance_checkbox = QCheckBox("Show Opening Balance Entries")
        self.show_opening_balance_checkbox.setChecked(True)  # Show by default
        self.show_opening_balance_checkbox.setToolTip("Toggle visibility of opening balance transactions")
        self.show_opening_balance_checkbox.stateChanged.connect(self._on_opening_balance_filter_toggle)
        control_layout.addWidget(self.show_opening_balance_checkbox)

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

        # BUG-006 FIX: Configure column widths and resize behavior
        header = self.transaction_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Description (takes remaining space)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(3, QHeaderView.Fixed)             # Amount (fixed width)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status

        # Set minimum width for Amount column to prevent truncation
        self.transaction_table.setColumnWidth(3, 100)  # Amount column

        # ISSUE-002 FIX: Enable tooltips for table items
        self.transaction_table.setMouseTracking(True)

        # TODO: Add double-click to edit when UnifiedTransactionDialog supports editing
        # See docs/technical-reviews/FINAL_UI_UX_REVIEW.md - Bug #5
        # self.transaction_table.itemDoubleClicked.connect(self.edit_transaction)

        layout.addWidget(self.transaction_table)

        return panel

    def load_data(self) -> None:
        """Load all data from database."""
        try:
            self._load_accounts()
            self._load_transactions()

            # US-013: Populate category dropdown with categories from database
            self.search_panel.populate_categories(account_id=self.current_account_id)
        except FinanceAppError as e:
            logger.error(f"Failed to load data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")

    def _load_accounts(self) -> None:
        """
        Load accounts into hierarchical tree widget.

        US-006: Updated to use AccountTreeWidget for hierarchy display.
        """
        try:
            # US-005: Filter system accounts based on checkbox
            show_system = self.show_system_accounts_checkbox.isChecked()

            # US-006: Load accounts into tree widget
            self.account_tree.load_accounts(show_system_accounts=show_system)

            # Update total balance
            total = self.account_service.get_total_balance()
            total_color = "green" if total >= 0 else "red"
            self.balance_label.setText(f"Total Balance: <span style='color: {total_color};'>${total:.2f}</span>")

        except FinanceAppError as e:
            logger.error(f"Failed to load accounts: {e}")
            raise

    def _on_favorites_filter_changed(self):
        """
        Handle favorites filter checkbox change.
        US-009: Toggle favorites-only view in account tree.
        """
        is_checked = self.show_favorites_only_checkbox.isChecked()
        self.account_tree.set_favorites_filter(is_checked)
        logger.info(f"Favorites filter {'enabled' if is_checked else 'disabled'}")

    def _on_account_search_changed(self, text: str):
        """
        Handle account search box text changes.
        US-007: Multi-field search across name, account number, and institution name.

        Args:
            text: Current search query
        """
        # Update tree with search filter
        self.account_tree.set_search_filter(text)
        logger.debug(f"Account search query: '{text}'")

    def _load_transactions(self, account_id: Optional[int] = None) -> None:
        """
        Load transactions into table.

        US-004: Phase 6 - Task 4.37 - Added reconciliation status column
        US-005: Added filtering and special styling for opening balance transactions
        US-011: Refactored to use _display_transactions() helper method
        """
        try:
            all_transactions = self.transaction_service.get_all_transactions(account_id)

            # US-005: Filter opening balance transactions if checkbox is unchecked
            show_opening_balance = self.show_opening_balance_checkbox.isChecked()
            if show_opening_balance:
                transactions = all_transactions
            else:
                transactions = [t for t in all_transactions if not t.is_opening_balance]

            # US-011: Use helper method to display transactions
            self._display_transactions(transactions)

        except FinanceAppError as e:
            logger.error(f"Failed to load transactions: {e}")
            raise

    def on_account_selected(self, account_id: int = None) -> None:
        """
        Handle account selection.

        US-006: Updated to receive account_id directly from tree widget signal.

        Args:
            account_id: Selected account ID (from tree widget signal)
        """
        if account_id is None:
            # Fallback for backward compatibility
            return

        self.current_account_id = account_id
        self._load_transactions(self.current_account_id)

        # US-013: Repopulate category dropdown for selected account
        self.search_panel.populate_categories(account_id=account_id)

        # Get account name for status bar
        try:
            account = self.account_service.get_account(account_id)
            if account:
                self.statusBar().showMessage(f"Showing transactions for: {account.name}")
        except Exception as e:
            logger.warning(f"Failed to get account name: {e}")

    def _on_opening_balance_filter_toggle(self, state: int) -> None:
        """
        Handle opening balance filter toggle (US-005).

        Args:
            state: Checkbox state (Qt.Checked or Qt.Unchecked)
        """
        # Reload transactions with current filter state
        self._reload_filtered_transactions()

    def _on_date_filter_changed(self, from_date, to_date) -> None:
        """
        Handle date filter change (US-012).

        Stores the date filter state and reloads transactions with all active filters.

        Args:
            from_date: Start date (None if filter cleared)
            to_date: End date (None if filter cleared)
        """
        # Store date filter state
        self.current_date_from = from_date
        self.current_date_to = to_date

        # Reload transactions with combined filters
        self._reload_filtered_transactions()

        # Update status bar
        if from_date and to_date:
            self.statusBar().showMessage(
                f"Filtered by date: {from_date.strftime('%b %d, %Y')} - {to_date.strftime('%b %d, %Y')}",
                3000
            )
        else:
            self.statusBar().showMessage("Date filter cleared", 2000)

    def _on_category_filter_changed(self, categories: list) -> None:
        """
        Handle category filter change (US-013).

        Stores the selected categories and reloads transactions with all active filters.

        Args:
            categories: List of selected category names (empty list if filter cleared)
        """
        # Store category filter state
        self.current_categories = categories if categories else []

        # Reload transactions with combined filters
        self._reload_filtered_transactions()

        # Update status bar
        if categories:
            if len(categories) == 1:
                self.statusBar().showMessage(f"Filtered by category: {categories[0]}", 3000)
            else:
                self.statusBar().showMessage(
                    f"Filtered by {len(categories)} categories: {', '.join(categories[:2])}{'...' if len(categories) > 2 else ''}",
                    3000
                )
        else:
            self.statusBar().showMessage("Category filter cleared", 2000)

    def _on_search_changed(self, keyword: str) -> None:
        """
        Handle transaction search text change (US-011 + US-012).

        Stores the search keyword and reloads transactions with all active filters.

        Args:
            keyword: Search keyword (already trimmed by widget)
        """
        # Store search keyword state
        self.current_search_keyword = keyword if keyword else None

        # Reload transactions with combined filters
        self._reload_filtered_transactions()

        # Update status bar with result count
        if keyword:
            account_msg = "in this account" if self.current_account_id else "in all accounts"
            self.statusBar().showMessage(f"Searching for '{keyword}' {account_msg}", 2000)
        else:
            self.statusBar().showMessage("Text search cleared", 2000)

    def _on_filters_cleared(self) -> None:
        """
        Handle Clear All Filters action (US-016).

        Called when user clicks "Clear All Filters" button in SearchPanelWidget.
        Clears all filter state and reloads all transactions for the current account.

        Signal Flow:
            SearchPanelWidget.filters_cleared
                ↓
            MainWindow._on_filters_cleared() ← THIS METHOD
                ↓
            Clear filter state + _load_transactions(current_account_id)
        """
        try:
            # Clear all filter state (US-012, US-013)
            self.current_date_from = None
            self.current_date_to = None
            self.current_categories = []
            self.current_search_keyword = None

            # Reload transactions with no filters
            self._load_transactions(self.current_account_id)

            # Update status bar
            self.statusBar().showMessage("All filters cleared", 2000)

            logger.info("All filters cleared via Clear All button")

        except FinanceAppError as e:
            logger.error(f"Failed to clear filters: {e}")
            QMessageBox.warning(self, "Filter Error", f"Failed to clear filters: {e}")

    def _reload_filtered_transactions(self) -> None:
        """
        Reload transactions with ALL active filters applied.

        US-011 + US-012 + US-013: Combines date, category, text search, and opening balance filters.
        Applies filters in order: date (backend) → category (Python) → text (Python) → opening balance (Python)

        Filter Combination Strategy:
            1. Date Filter (if active): Use backend transaction_service.filter_by_date_range()
            2. No Date Filter: Use transaction_service.get_all_transactions()
            3. Category Filter (if active): Post-filter results in Python (US-013)
            4. Text Search (if active): Post-filter results in Python
            5. Opening Balance Toggle: Post-filter to exclude opening balance transactions

        Called by:
            - _on_date_filter_changed() (US-012)
            - _on_category_filter_changed() (US-013)
            - _on_search_changed() (US-011)
            - _on_opening_balance_filter_toggle()

        Note:
            This method combines all active filters without clearing any state.
            To clear filters, use _on_filters_cleared() instead.
        """
        try:
            account_id = self.current_account_id

            # Step 1: Apply date filter if active (backend filtering)
            if self.current_date_from and self.current_date_to:
                transactions = self.transaction_service.filter_by_date_range(
                    from_date=self.current_date_from,
                    to_date=self.current_date_to,
                    account_id=account_id
                )
                logger.debug(
                    f"Applied date filter: {self.current_date_from} to {self.current_date_to}, "
                    f"got {len(transactions)} transactions"
                )
            else:
                # No date filter - get all transactions
                transactions = self.transaction_service.get_all_transactions(account_id)
                logger.debug(f"No date filter - loaded {len(transactions)} transactions")

            # Step 2: Apply category filter (post-filter in Python) (US-013)
            if self.current_categories:
                before_count = len(transactions)
                transactions = [
                    t for t in transactions
                    if t.category in self.current_categories
                ]
                logger.debug(
                    f"Applied category filter {self.current_categories}: {before_count} → {len(transactions)} transactions"
                )

            # Step 3: Apply text search filter (post-filter in Python)
            if self.current_search_keyword:
                keyword = self.current_search_keyword.lower()
                before_count = len(transactions)
                transactions = [
                    t for t in transactions
                    if keyword in t.description.lower()
                ]
                logger.debug(
                    f"Applied text search filter '{keyword}': {before_count} → {len(transactions)} transactions"
                )

            # Step 4: Apply opening balance filter (post-filter in Python)
            show_opening_balance = self.show_opening_balance_checkbox.isChecked()
            if not show_opening_balance:
                before_count = len(transactions)
                transactions = [
                    t for t in transactions
                    if not t.is_opening_balance
                ]
                logger.debug(
                    f"Applied opening balance filter: {before_count} → {len(transactions)} transactions"
                )

            # Step 5: Display filtered results
            self._display_transactions(transactions)

            # Log final result
            filter_summary = []
            if self.current_date_from and self.current_date_to:
                filter_summary.append(f"date: {self.current_date_from} to {self.current_date_to}")
            if self.current_categories:
                categories_str = ', '.join(self.current_categories[:2])
                if len(self.current_categories) > 2:
                    categories_str += f"... (+{len(self.current_categories) - 2} more)"
                filter_summary.append(f"categories: {categories_str}")
            if self.current_search_keyword:
                filter_summary.append(f"text: '{self.current_search_keyword}'")
            if not show_opening_balance:
                filter_summary.append("hide opening balance")

            if filter_summary:
                logger.info(
                    f"Reloaded {len(transactions)} transactions with filters: {', '.join(filter_summary)}"
                )
            else:
                logger.info(f"Reloaded {len(transactions)} transactions (no filters active)")

        except FinanceAppError as e:
            logger.error(f"Failed to reload filtered transactions: {e}")
            QMessageBox.warning(
                self,
                "Filter Error",
                f"Failed to apply filters:\n\n{e}"
            )

    def _focus_search_in_account(self) -> None:
        """
        Focus search widget for current account (Ctrl+F).

        US-011: Keyboard shortcut handler for searching within the currently
        selected account.
        """
        # Focus search widget and select all text for easy replacement
        self.transaction_search.set_focus()

        # Update status bar to indicate search scope
        if self.current_account_id:
            try:
                account = self.account_service.get_account(self.current_account_id)
                if account:
                    self.statusBar().showMessage(f"Search in: {account.name}", 2000)
            except Exception as e:
                logger.warning(f"Failed to get account name: {e}")
        else:
            self.statusBar().showMessage("Search in: All accounts", 2000)

    def _focus_search_all_accounts(self) -> None:
        """
        Focus search widget and clear account filter (Ctrl+Shift+F).

        US-011: Keyboard shortcut handler for searching across all accounts.
        This temporarily clears the account filter to enable global search.
        """
        # Clear current account selection to search all accounts
        self.current_account_id = None

        # Clear account tree selection to reflect "all accounts" state
        self.account_tree.clearSelection()

        # Focus search widget
        self.transaction_search.set_focus()

        # Update status bar
        self.statusBar().showMessage("Search in: All accounts", 2000)

    def _display_transactions(self, transactions: list) -> None:
        """
        Display transactions in table (extracted from _load_transactions for reuse).

        US-011: Helper method to display transactions from search results
        or regular load operations.

        Args:
            transactions: List of Transaction objects to display
        """
        self.transaction_table.setRowCount(len(transactions))

        for i, trans in enumerate(transactions):
            # US-005: Check if this is an opening balance transaction
            is_opening_balance = trans.is_opening_balance

            # Date
            date_text = trans.date
            if is_opening_balance:
                date_text = f"🔓 {date_text}"  # Opening balance icon
            date_item = QTableWidgetItem(date_text)
            if is_opening_balance:
                date_item.setToolTip("Opening balance transaction - automatically created")
            self.transaction_table.setItem(i, 0, date_item)

            # Description
            desc_item = QTableWidgetItem(trans.description)
            if is_opening_balance:
                # Make opening balance description italic
                font = desc_item.font()
                font.setItalic(True)
                desc_item.setFont(font)
            # ISSUE-002 FIX: Add tooltip showing full description text
            desc_item.setToolTip(trans.description)
            self.transaction_table.setItem(i, 1, desc_item)

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
            # US-005: Show "Auto-Reconciled" for opening balance transactions
            status_text = ""
            status_tooltip = ""
            recon_status = None

            if is_opening_balance:
                # Opening balance transactions are auto-reconciled
                status_text = "🔒 Auto-Reconciled"
                status_tooltip = "Opening balance transactions are automatically reconciled"
            else:
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
            if is_opening_balance or (recon_status and recon_status == 'cleared'):
                status_item.setForeground(Qt.darkGreen)
            elif recon_status and recon_status == 'pending':
                status_item.setForeground(Qt.darkYellow)
            self.transaction_table.setItem(i, 5, status_item)

        self.transaction_table.resizeColumnsToContents()

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

    # TODO: Implement edit_transaction when UnifiedTransactionDialog supports editing
    # See docs/technical-reviews/FINAL_UI_UX_REVIEW.md - Bug #5
    # Current workaround: Delete and recreate transaction
    #
    # def edit_transaction(self) -> None:
    #     """Edit selected transaction - NOT YET IMPLEMENTED."""
    #     pass

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

    def edit_account(self, account_id: int = None) -> None:
        """
        Show dialog to edit selected account.

        Args:
            account_id: ID of account to edit. If None, uses current selection.

        US-006: Updated to use current_account_id from tree widget selection.
        BUG-FIX-001: Now accepts account_id from signal.
        """
        # BUG-FIX-001: Use provided account_id or fall back to current selection
        if account_id is None:
            account_id = self.current_account_id

        if not account_id:
            QMessageBox.warning(self, "No Selection", "Please select an account to edit")
            return

        try:

            # Get account details
            account = self.account_service.get_account(account_id)
            if not account:
                QMessageBox.warning(self, "Error", "Account not found")
                return

            # US-005: Prevent editing Opening Balance Equity account
            if (account.account_type == AccountType.EQUITY and
                account.account_subtype == AccountSubtype.OPENING_BALANCE):
                QMessageBox.warning(
                    self,
                    "System Account",
                    "The Opening Balance Equity account is a system account and cannot be edited.\n\n"
                    "This account is automatically managed to maintain the accounting equation."
                )
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

    def delete_account(self, account_id: int = None) -> None:
        """
        Delete selected account.

        Args:
            account_id: ID of account to delete. If None, uses current selection.

        US-006: Updated to use current_account_id from tree widget selection.
        BUG-FIX-002: Now accepts account_id from signal.
        """
        # BUG-FIX-002: Use provided account_id or fall back to current selection
        if account_id is None:
            account_id = self.current_account_id

        if not account_id:
            QMessageBox.warning(self, "No Selection", "Please select an account to delete")
            return

        try:
            # US-005: Prevent deleting Opening Balance Equity account
            account = self.account_service.get_account(account_id)
            if account and (account.account_type == AccountType.EQUITY and
                           account.account_subtype == AccountSubtype.OPENING_BALANCE):
                QMessageBox.warning(
                    self,
                    "System Account",
                    "The Opening Balance Equity account is a system account and cannot be deleted.\n\n"
                    "This account is required to maintain the accounting equation."
                )
                return

            account_name = account.name if account else "Unknown"

            # BUG-FIX-010: Check transaction count and show detailed warning
            transaction_count = self.account_service.get_transaction_count(account_id)

            # Build warning message based on transaction count
            if transaction_count > 0:
                message = (
                    f"Are you SURE you want to delete account '{account_name}'?\n\n"
                    f"⚠️ This account has {transaction_count} transaction(s).\n\n"
                    f"Deleting this account will PERMANENTLY DELETE:\n"
                    f"  • {transaction_count} transaction(s)\n"
                    f"  • All associated journal entries\n"
                    f"  • All reconciliation history\n\n"
                    f"This action CANNOT be undone!"
                )
                icon = QMessageBox.Warning
            else:
                message = f"Are you sure you want to delete account '{account_name}'?\n\nThis account has no transactions."
                icon = QMessageBox.Question

            msg_box = QMessageBox(icon, "Confirm Delete", message, parent=self)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            reply = msg_box.exec()

            if reply == QMessageBox.Yes:
                self.account_service.delete_account(account_id)
                self.load_data()
                if transaction_count > 0:
                    self.statusBar().showMessage(
                        f"Account '{account_name}' deleted (with {transaction_count} transactions)"
                    )
                else:
                    self.statusBar().showMessage(f"Account '{account_name}' deleted")
                logger.info(f"Account deleted via UI: {account_id} ({transaction_count} transactions)")

        except FinanceAppError as e:
            logger.error(f"Failed to delete account: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete account: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deleting account: {e}")
            QMessageBox.critical(self, "Error", f"Unexpected error: {e}")

    def set_opening_balance(self, account_id: int = None) -> None:
        """
        Open dialog to set opening balance for selected account (US-005).

        Args:
            account_id: ID of account. If None, uses current selection.

        US-006: Updated to use current_account_id from tree widget selection.
        BUG-FIX-003: Now accepts account_id from signal.
        """
        # BUG-FIX-003: Use provided account_id or fall back to current selection
        if account_id is None:
            account_id = self.current_account_id

        if not account_id:
            QMessageBox.warning(self, "No Selection", "Please select an account to set opening balance")
            return

        try:
            # Get the account
            account = self.account_service.get_account(account_id)
            if not account:
                QMessageBox.warning(self, "Error", "Account not found")
                return

            # Open set opening balance dialog
            dialog = SetOpeningBalanceDialog(account, self.account_service, self)
            if dialog.exec() == QDialog.Accepted:
                # Reload data to show updated balance
                self.load_data()
                self.statusBar().showMessage(f"Opening balance set for '{account.name}'")
                logger.info(f"Opening balance set via UI for account: {account_id}")

        except FinanceAppError as e:
            logger.error(f"Failed to set opening balance: {e}")
            QMessageBox.critical(self, "Error", f"Failed to set opening balance: {e}")
        except Exception as e:
            logger.error(f"Unexpected error setting opening balance: {e}")
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
        US-006: Updated to use current_account_id from tree widget selection.
        """
        try:
            # Get currently selected account
            if not self.current_account_id:
                QMessageBox.warning(
                    self,
                    "No Account Selected",
                    "Please select an account to reconcile."
                )
                return

            account_id = self.current_account_id

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

    def validate_all_accounts(self) -> None:
        """Run balance validation on all accounts (US-010)."""
        from finance_app.business.account_balance_validator import AccountBalanceValidator
        from finance_app.data.repositories.account_repository import AccountRepository
        from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
        from finance_app.ui.dialogs.validation_report_dialog import ValidationReportDialog
        from PySide6.QtWidgets import QProgressDialog

        try:
            # Create repositories
            account_repo = AccountRepository(self.db)
            journal_repo = JournalEntryRepository(self.db)

            # Create validator
            validator = AccountBalanceValidator(
                self.db,
                account_repo,
                journal_repo
            )

            # Show progress dialog
            progress = QProgressDialog("Validating account balances...", None, 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            # Run validation
            results = validator.validate_all_accounts()

            progress.close()

            # Show results dialog
            dialog = ValidationReportDialog(results, validator, self)
            dialog.accounts_fixed.connect(self.refresh_all)
            dialog.exec()

        except Exception as e:
            logger.error(f"Failed to validate accounts: {e}")
            QMessageBox.critical(self, "Error", f"Failed to validate accounts: {e}")

    def show_trial_balance(self) -> None:
        """Show trial balance report (US-010)."""
        from finance_app.business.account_balance_validator import AccountBalanceValidator
        from finance_app.data.repositories.account_repository import AccountRepository
        from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
        from finance_app.ui.dialogs.trial_balance_dialog import TrialBalanceDialog

        try:
            # Create repositories
            account_repo = AccountRepository(self.db)
            journal_repo = JournalEntryRepository(self.db)

            # Create validator
            validator = AccountBalanceValidator(
                self.db,
                account_repo,
                journal_repo
            )

            # Generate trial balance
            trial_balance = validator.get_trial_balance()

            # Show dialog
            dialog = TrialBalanceDialog(trial_balance, self)
            dialog.exec()

        except Exception as e:
            logger.error(f"Failed to generate trial balance: {e}")
            QMessageBox.critical(self, "Error", f"Failed to generate trial balance: {e}")

    def refresh_all(self) -> None:
        """Refresh all data displays after validation fixes (US-010)."""
        try:
            self._load_accounts()
            self._load_transactions()
            self.statusBar().showMessage("Data refreshed after balance repair", 3000)
            logger.info("UI refreshed after balance validation fixes")
        except Exception as e:
            logger.error(f"Failed to refresh UI: {e}")

    def show_keyboard_shortcuts(self) -> None:
        """Show keyboard shortcuts reference dialog."""
        shortcuts_text = """
<h2>Keyboard Shortcuts</h2>

<h3>Transaction Operations</h3>
<table cellpadding="5" cellspacing="0" border="0">
<tr><td><b>Ctrl+N</b></td><td>Add Transaction</td></tr>
<tr><td><b>Ctrl+D</b></td><td>Delete Transaction</td></tr>
<tr><td><b>Ctrl+F</b></td><td>Search in Account</td></tr>
<tr><td><b>Ctrl+Shift+F</b></td><td>Search All Accounts</td></tr>
</table>

<h3>Account Operations</h3>
<table cellpadding="5" cellspacing="0" border="0">
<tr><td><b>Ctrl+Shift+N</b></td><td>New Account</td></tr>
<tr><td><b>Ctrl+R</b></td><td>Reconcile Account</td></tr>
</table>

<h3>Tools & Validation</h3>
<table cellpadding="5" cellspacing="0" border="0">
<tr><td><b>Ctrl+Shift+V</b></td><td>Validate Account Balances</td></tr>
<tr><td><b>Ctrl+T</b></td><td>Trial Balance Report</td></tr>
</table>

<h3>Help</h3>
<table cellpadding="5" cellspacing="0" border="0">
<tr><td><b>F1</b></td><td>Keyboard Shortcuts (this dialog)</td></tr>
</table>

<h3>General</h3>
<table cellpadding="5" cellspacing="0" border="0">
<tr><td><b>Alt+F</b></td><td>Open File menu</td></tr>
<tr><td><b>Alt+E</b></td><td>Open Edit menu</td></tr>
<tr><td><b>Alt+T</b></td><td>Open Tools menu</td></tr>
<tr><td><b>Alt+H</b></td><td>Open Help menu</td></tr>
</table>
"""

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Keyboard Shortcuts")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(shortcuts_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

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
