"""
Account Tree Widget for hierarchical account display.

US-006: Displays accounts in a tree structure with parent/child relationships.
US-009: Enhanced with color-coded indicators and visual customization.
"""
from typing import Optional, Dict
from decimal import Decimal

from PySide6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, QMessageBox, QMenu, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QDropEvent, QDragMoveEvent, QIcon, QAction, QColor, QBrush, QPixmap, QPainter

from finance_app.business.account_service import AccountService
from finance_app.data.models import Account
from finance_app.utils.exceptions import ValidationError
from finance_app.utils.logger import setup_logger

logger = setup_logger(__name__)


class AccountTreeWidget(QTreeWidget):
    """
    Hierarchical tree view for accounts with parent/child relationships.

    Features:
    - Displays accounts in tree structure
    - Shows parent account balances (calculated)
    - Supports drag-and-drop reorganization
    - Expand/collapse functionality
    - Context menu for hierarchy operations

    Signals:
        account_selected(int): Emitted when an account is selected (account_id)
    """

    account_selected = Signal(int)  # Emits account_id

    def __init__(self, account_service: AccountService, parent=None):
        """
        Initialize account tree widget.

        Args:
            account_service: Service for account operations
            parent: Parent widget
        """
        super().__init__(parent)
        self.account_service = account_service
        self._expansion_state: Dict[int, bool] = {}  # Remember expanded state
        self._show_favorites_only = False  # US-009: Favorites filter
        self._search_query = ""  # US-007: Search filter

        self.setup_ui()
        self.setup_drag_drop()
        self.connect_signals()

    def setup_ui(self):
        """Configure tree widget appearance and behavior."""
        # Column configuration - US-009: Added Type column for visual context
        self.setHeaderLabels(["Account", "Type", "Balance", "Actions"])
        self.setColumnWidth(0, 280)  # Account name with color indicator
        self.setColumnWidth(1, 100)  # Account type
        self.setColumnWidth(2, 120)  # Balance
        self.setColumnWidth(3, 60)   # Actions (favorite star)

        # Make columns user-resizable but maintain minimum sizes
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.Interactive)  # Account
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        self.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Balance
        self.header().setSectionResizeMode(3, QHeaderView.Fixed)  # Actions (fixed width)

        # Tree behavior
        self.setIndentation(20)  # Indentation for child items
        self.setAnimated(True)  # Smooth expand/collapse
        self.setAlternatingRowColors(False)  # Keep clean white background like HomeBank
        self.setRootIsDecorated(True)  # Show expand/collapse indicators

        # Selection
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setSelectionBehavior(QTreeWidget.SelectRows)

        # Visual tweaks
        self.setUniformRowHeights(True)
        self.setExpandsOnDoubleClick(True)

        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        # Apply professional styling
        self._apply_styling()

        # Set tooltips for accessibility
        self.setToolTip(
            "Account Hierarchy Tree\n\n"
            "• Click account to view transactions\n"
            "• Double-click parent to expand/collapse\n"
            "• Right-click for more options\n"
            "• Drag-and-drop to reorganize accounts\n\n"
            "Keyboard:\n"
            "• Arrow keys to navigate\n"
            "• Left/Right to expand/collapse\n"
            "• Enter to edit selected account"
        )

        logger.debug("AccountTreeWidget UI configured")

    def _apply_styling(self):
        """Apply clean, minimal styling that respects system theme (light/dark mode)."""
        self.setStyleSheet("""
            QTreeWidget {
                border: 1px solid palette(mid);
                font-size: 13px;
                outline: none;
            }

            QTreeWidget::item {
                padding: 4px 2px;
                border: none;
            }

            QTreeWidget::item:hover {
                background-color: palette(midlight);
            }

            QTreeWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }

            /* Expand/collapse branch indicators */
            QTreeWidget::branch {
                background-color: transparent;
            }

            QTreeWidget::branch:hover {
                background: transparent;
            }

            /* Show arrow indicators for expandable items */
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border: none;
                background: transparent;
                image: none;
            }

            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border: none;
                background: transparent;
                image: none;
            }

            /* Header styling - respects theme */
            QHeaderView::section {
                background-color: palette(button);
                padding: 6px 4px;
                border: none;
                border-bottom: 1px solid palette(mid);
                border-right: 1px solid palette(midlight);
                font-weight: bold;
                font-size: 11px;
            }

            QHeaderView::section:last {
                border-right: none;
            }

            /* Minimal scrollbar - theme aware */
            QScrollBar:vertical {
                border: none;
                background-color: palette(base);
                width: 10px;
            }

            QScrollBar::handle:vertical {
                background-color: palette(mid);
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: palette(dark);
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar:horizontal {
                border: none;
                background-color: palette(base);
                height: 10px;
            }

            QScrollBar::handle:horizontal {
                background-color: palette(mid);
                min-width: 20px;
                border-radius: 5px;
            }

            QScrollBar::handle:horizontal:hover {
                background-color: palette(dark);
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)

    def setup_drag_drop(self):
        """Enable drag-and-drop for account reorganization."""
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.InternalMove)

        logger.debug("Drag-and-drop enabled for AccountTreeWidget")

    def connect_signals(self):
        """Connect internal signals."""
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.customContextMenuRequested.connect(self._show_context_menu)
        # US-007: Make favorite star clickable in column 3
        self.itemClicked.connect(self._on_item_clicked)
        self.itemExpanded.connect(self._on_item_expanded)
        self.itemCollapsed.connect(self._on_item_collapsed)

    def load_accounts(self, show_system_accounts: bool = True):
        """
        Load and display account hierarchy.

        Args:
            show_system_accounts: Whether to show system accounts
        """
        logger.info("Loading account hierarchy...")

        # Save current expansion state
        self._save_expansion_state()

        # Clear existing items
        self.clear()

        try:
            # Get all accounts
            accounts = self.account_service.get_all_accounts()

            # Filter system accounts if needed
            if not show_system_accounts:
                accounts = [acc for acc in accounts if not acc.name.startswith("Opening Balance Equity")]

            # US-007: Filter by search query if provided
            if self._search_query:
                search_results = self.account_service.account_repo.search_accounts(self._search_query)
                search_ids = {acc.id for acc in search_results}
                accounts = [acc for acc in accounts if acc.id in search_ids]
                logger.info(f"Search '{self._search_query}' matched {len(accounts)} accounts")

            # US-009: Filter by favorites if enabled
            if self._show_favorites_only:
                favorite_accounts = [acc for acc in accounts if acc.is_favorite]
                # Build tree with only favorites (tree builder will maintain hierarchy)
                account_tree = self.account_service.account_repo.build_account_tree(favorite_accounts)
                logger.info(f"Showing {len(favorite_accounts)} favorite accounts")
            else:
                # Build tree using repository's tree builder
                account_tree = self.account_service.account_repo.build_account_tree(accounts)

            # Add each root account and its descendants
            for root_account in account_tree:
                self._add_account_item(root_account, None)

            # Restore expansion state
            self._restore_expansion_state()

            # Expand all by default on first load
            if not self._expansion_state:
                self.expandAll()

            logger.info(f"Loaded {len(accounts)} accounts in hierarchy")

        except Exception as e:
            logger.error(f"Failed to load account hierarchy: {e}")
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load accounts:\n{str(e)}"
            )

    def set_favorites_filter(self, enabled: bool):
        """
        Toggle favorites-only filter.
        US-009: Show only favorite accounts when enabled.

        Args:
            enabled: True to show only favorites, False to show all
        """
        self._show_favorites_only = enabled
        self.load_accounts()
        logger.info(f"Favorites filter {'enabled' if enabled else 'disabled'}")

    def set_search_filter(self, query: str):
        """
        Set search filter for accounts.
        US-007: Filter accounts by name, account number, or institution name.

        Args:
            query: Search query string (searches name, account_number, institution_name)
        """
        self._search_query = query.strip()
        self.load_accounts()
        if self._search_query:
            logger.info(f"Search filter applied: '{self._search_query}'")
        else:
            logger.info("Search filter cleared")

    def _add_account_item(self, account: Account, parent_item: Optional[QTreeWidgetItem]):
        """
        Add account to tree recursively with its children.

        Args:
            account: Account to add
            parent_item: Parent tree item (None for root)
        """
        # Create tree item
        if parent_item is None:
            item = QTreeWidgetItem(self)
        else:
            item = QTreeWidgetItem(parent_item)

        # Store account ID and full account object in item data
        item.setData(0, Qt.UserRole, account.id)
        item.setData(0, Qt.UserRole + 1, account)  # Store full account for quick access

        # US-009: Create colored icon indicator
        color_icon = self._create_color_icon(account.color_hex)
        item.setIcon(0, color_icon)

        # Format account name with type icon
        if account.is_parent:
            # Parent account - folder icon
            account_name = f"📁 {account.name}"
        else:
            # Leaf account - different icons based on type
            icon = self._get_account_icon(account)
            account_name = f"{icon} {account.name}"

        item.setText(0, account_name)

        # US-009: Display account type in column 1
        account_type_display = account.account_subtype.value.replace('_', ' ').title()
        item.setText(1, account_type_display)
        item.setForeground(1, QColor("#666666"))  # Gray text for type

        # Format balance in column 2
        if account.is_parent:
            # Calculate parent balance from children
            try:
                parent_balance = self.account_service.get_parent_account_balance_sql(account.id)
                balance_text = f"${parent_balance:,.2f}"
            except Exception as e:
                logger.warning(f"Failed to calculate parent balance for {account.name}: {e}")
                balance_text = "$0.00"
                parent_balance = Decimal('0')

            # Bold font for parent accounts
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)
            item.setFont(1, font)
            item.setFont(2, font)

            # Gray color for parent balance
            item.setForeground(2, QColor("#666666"))
        else:
            # Leaf account - use actual balance
            balance_text = f"${account.balance:,.2f}"
            parent_balance = None

        # US-009: Color code balance using backend color logic
        balance_color = self._get_balance_color(account, parent_balance)
        if balance_color:
            item.setForeground(2, balance_color)

        item.setText(2, balance_text)
        item.setTextAlignment(2, Qt.AlignRight | Qt.AlignVCenter)

        # US-007/US-009: Add clickable favorite star in column 3
        if hasattr(account, 'is_favorite') and account.is_favorite:
            item.setText(3, "⭐")
            item.setToolTip(3, "Favorite Account (click to unfavorite)")
        else:
            item.setText(3, "☆")
            item.setToolTip(3, "Click to mark as favorite")

        item.setTextAlignment(3, Qt.AlignCenter)

        # Make star column more visually clickable
        item.setForeground(3, QColor("#FFB800"))  # Golden color for both states

        # Add helpful tooltip
        tooltip = self._create_account_tooltip(account, parent_balance if account.is_parent else None)
        item.setToolTip(0, tooltip)
        item.setToolTip(1, tooltip)

        # Add children recursively
        if hasattr(account, 'children'):
            for child in account.children:
                self._add_account_item(child, item)

    def _create_account_tooltip(self, account: Account, parent_balance: Optional[Decimal] = None) -> str:
        """
        Create helpful tooltip for account item.

        Args:
            account: Account object
            parent_balance: Calculated balance for parent accounts

        Returns:
            Formatted tooltip string
        """
        lines = []

        # Account name and type
        lines.append(f"📌 {account.name}")
        lines.append(f"Type: {account.account_type.value} - {account.account_subtype.value}")
        lines.append("")

        # Balance information
        if account.is_parent:
            lines.append(f"Balance: ${parent_balance:,.2f} (calculated)")
            lines.append("⚠️ Parent accounts cannot have direct transactions")
            lines.append("Balance is sum of all child accounts")
        else:
            lines.append(f"Balance: ${account.balance:,.2f}")
            lines.append(f"Normal Balance: {account.normal_balance}")

        lines.append("")

        # Hierarchy information
        if account.is_parent:
            child_count = len(getattr(account, 'children', []))
            lines.append(f"📁 Parent Account ({child_count} children)")
            lines.append(f"Hierarchy Level: {account.hierarchy_level}")
        else:
            if account.parent_account_id:
                lines.append(f"Child Account (Level {account.hierarchy_level})")
            else:
                lines.append("Top-Level Account")

        lines.append("")

        # Actions
        lines.append("💡 Actions:")
        if account.is_parent:
            lines.append("• Double-click to expand/collapse")
            lines.append("• Right-click for hierarchy options")
        else:
            lines.append("• Click to view transactions")
            lines.append("• Right-click to edit or move")
            lines.append("• Drag-and-drop to reorganize")

        return "\n".join(lines)

    def _get_account_icon(self, account: Account) -> str:
        """
        Get emoji icon for account based on type.

        Args:
            account: Account object

        Returns:
            Emoji string
        """
        # Map account subtypes to icons
        icon_map = {
            'checking': '🏦',
            'savings': '💰',
            'cash': '💵',
            'investment': '📈',
            'credit_card': '💳',
            'loan': '🏠',
            'mortgage': '🏡',
            'line_of_credit': '💳',
        }

        subtype_str = account.account_subtype.value if hasattr(account.account_subtype, 'value') else str(account.account_subtype)

        return icon_map.get(subtype_str, '📝')

    def _create_color_icon(self, color_hex: str) -> QIcon:
        """
        Create a colored circle icon for the account.

        US-009: Uses the account's custom color_hex field to create a visual indicator.
        Creates a small circular icon filled with the account's color.

        Args:
            color_hex: Hex color code (e.g., '#2563EB')

        Returns:
            QIcon with colored circle
        """
        # Create a 16x16 pixmap
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)

        # Draw a filled circle with the account color
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set the brush to the account color
        color = QColor(color_hex) if color_hex else QColor("#2563EB")
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)

        # Draw circle (slightly smaller than pixmap to avoid edge clipping)
        painter.drawEllipse(2, 2, 12, 12)
        painter.end()

        return QIcon(pixmap)

    def _get_balance_color(self, account: Account, parent_balance: Optional[Decimal] = None) -> Optional[QColor]:
        """
        Get the color for balance display based on account type and balance value.

        US-009: Uses backend color logic for consistent balance coloring.

        Args:
            account: Account object
            parent_balance: Calculated balance for parent accounts

        Returns:
            QColor for balance display, or None for default
        """
        from finance_app.data.models import AccountType

        balance = parent_balance if parent_balance is not None else account.balance

        if balance == 0:
            return QColor("#666666")  # Gray for zero balance

        # Asset accounts: positive = green, negative = red
        if account.account_type == AccountType.ASSET:
            return QColor("#059669") if balance > 0 else QColor("#DC2626")

        # Liability accounts: INVERTED - positive balance = owe money = red
        elif account.account_type == AccountType.LIABILITY:
            return QColor("#DC2626") if balance > 0 else QColor("#059669")

        # For other types (Equity, Income, Expense), use default coloring
        else:
            return QColor("#059669") if balance > 0 else QColor("#DC2626")

    def _on_selection_changed(self):
        """Handle account selection."""
        selected_items = self.selectedItems()
        if selected_items:
            item = selected_items[0]
            account_id = item.data(0, Qt.UserRole)
            logger.debug(f"Account selected: ID={account_id}")
            self.account_selected.emit(account_id)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Handle item clicks - toggle favorite when star column is clicked.
        US-007: Make favorite star clickable (AC4).

        Args:
            item: The clicked tree item
            column: The column that was clicked
        """
        # Column 3 is the Actions column with favorite star
        if column == 3:
            account_id = item.data(0, Qt.UserRole)
            if account_id:
                # Toggle favorite status
                self._toggle_favorite(account_id)
                logger.debug(f"Favorite star clicked for account ID={account_id}")

    def _save_expansion_state(self):
        """Save which items are expanded."""
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            account_id = item.data(0, Qt.UserRole)
            if account_id:
                self._expansion_state[account_id] = item.isExpanded()
            iterator += 1

    def _restore_expansion_state(self):
        """Restore expansion state after reload."""
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            account_id = item.data(0, Qt.UserRole)
            if account_id and account_id in self._expansion_state:
                item.setExpanded(self._expansion_state[account_id])
            iterator += 1

    def _on_item_expanded(self, item: QTreeWidgetItem):
        """Remember that item was expanded."""
        account_id = item.data(0, Qt.UserRole)
        if account_id:
            self._expansion_state[account_id] = True

    def _on_item_collapsed(self, item: QTreeWidgetItem):
        """Remember that item was collapsed."""
        account_id = item.data(0, Qt.UserRole)
        if account_id:
            self._expansion_state[account_id] = False

    def dragMoveEvent(self, event: QDragMoveEvent):
        """
        Handle drag move to provide visual feedback.

        Args:
            event: Drag move event
        """
        # Get target item
        target_item = self.itemAt(event.pos())

        if target_item:
            # Check if target is a parent account
            account_id = target_item.data(0, Qt.UserRole)
            try:
                account = self.account_service.get_account(account_id)

                # Only allow dropping on parent accounts
                if account and account.is_parent:
                    event.accept()
                else:
                    event.ignore()
            except:
                event.ignore()
        else:
            # Allow dropping on empty space (makes top-level)
            event.accept()

    def dropEvent(self, event: QDropEvent):
        """
        Handle drag-and-drop account reorganization.

        Args:
            event: Drop event
        """
        source_item = self.currentItem()
        if not source_item:
            event.ignore()
            return

        source_account_id = source_item.data(0, Qt.UserRole)
        target_item = self.itemAt(event.pos())

        try:
            if target_item:
                # Dropping on another account
                target_account_id = target_item.data(0, Qt.UserRole)
                target_account = self.account_service.get_account(target_account_id)

                # Validate: target must be parent account
                if not target_account.is_parent:
                    QMessageBox.warning(
                        self,
                        "Invalid Drop Target",
                        f"Can only drop on parent accounts.\n\n"
                        f"'{target_account.name}' is not a parent account."
                    )
                    event.ignore()
                    return

                # Move account
                logger.info(f"Moving account {source_account_id} to parent {target_account_id}")
                self.account_service.move_account(source_account_id, target_account_id)

            else:
                # Dropping on empty space - make top-level
                logger.info(f"Moving account {source_account_id} to top-level")
                self.account_service.move_account(source_account_id, None)

            # Reload tree
            self.load_accounts()
            event.accept()

            QMessageBox.information(
                self,
                "Account Moved",
                "Account hierarchy updated successfully!"
            )

        except ValidationError as e:
            logger.warning(f"Move validation failed: {e}")
            QMessageBox.warning(
                self,
                "Cannot Move Account",
                f"Failed to move account:\n\n{str(e)}"
            )
            event.ignore()

        except Exception as e:
            logger.error(f"Failed to move account: {e}")
            QMessageBox.critical(
                self,
                "Move Error",
                f"An error occurred:\n\n{str(e)}"
            )
            event.ignore()

    def _show_context_menu(self, position):
        """
        Show context menu for account operations.

        Args:
            position: Menu position
        """
        item = self.itemAt(position)
        if not item:
            return

        account_id = item.data(0, Qt.UserRole)
        try:
            account = self.account_service.get_account(account_id)
            if not account:
                return
        except:
            return

        menu = QMenu(self)

        # Edit Account
        edit_action = QAction("Edit Account", self)
        edit_action.triggered.connect(lambda: self._edit_account(account_id))
        menu.addAction(edit_action)

        # Set Opening Balance
        set_balance_action = QAction("Set Opening Balance...", self)
        set_balance_action.triggered.connect(lambda: self._set_opening_balance(account_id))
        menu.addAction(set_balance_action)

        # US-009: Toggle Favorite
        favorite_text = "⭐ Remove from Favorites" if account.is_favorite else "☆ Add to Favorites"
        toggle_favorite_action = QAction(favorite_text, self)
        toggle_favorite_action.triggered.connect(lambda: self._toggle_favorite(account_id))
        menu.addAction(toggle_favorite_action)

        menu.addSeparator()

        # US-009: Display order operations
        move_up_action = QAction("⬆ Move Up", self)
        move_up_action.triggered.connect(lambda: self._move_account_up(account_id))
        menu.addAction(move_up_action)

        move_down_action = QAction("⬇ Move Down", self)
        move_down_action.triggered.connect(lambda: self._move_account_down(account_id))
        menu.addAction(move_down_action)

        menu.addSeparator()

        # US-006: Hierarchy operations

        # Move to Parent
        move_action = QAction("Move to Parent...", self)
        move_action.triggered.connect(lambda: self._move_to_parent(account_id))
        menu.addAction(move_action)

        # Make Top-Level
        if account.parent_account_id is not None:
            top_level_action = QAction("Make Top-Level", self)
            top_level_action.triggered.connect(lambda: self._make_top_level(account_id))
            menu.addAction(top_level_action)

        # Convert to Parent Account
        if not account.is_parent:
            convert_action = QAction("Convert to Parent Account", self)
            convert_action.triggered.connect(lambda: self._convert_to_parent(account_id))
            menu.addAction(convert_action)

        menu.addSeparator()

        # Expand/Collapse
        if account.is_parent:
            expand_action = QAction("Expand All", self)
            expand_action.triggered.connect(lambda: item.setExpanded(True))
            menu.addAction(expand_action)

            collapse_action = QAction("Collapse All", self)
            collapse_action.triggered.connect(lambda: item.setExpanded(False))
            menu.addAction(collapse_action)

            menu.addSeparator()

        # Delete Account
        delete_action = QAction("Delete Account", self)
        delete_action.triggered.connect(lambda: self._delete_account(account_id))
        menu.addAction(delete_action)

        menu.exec_(self.viewport().mapToGlobal(position))

    def _edit_account(self, account_id: int):
        """Emit signal to edit account (handled by main window)."""
        # This will be connected by main window
        logger.info(f"Edit account requested: {account_id}")

    def _set_opening_balance(self, account_id: int):
        """Emit signal to set opening balance (handled by main window)."""
        logger.info(f"Set opening balance requested: {account_id}")

    def _move_to_parent(self, account_id: int):
        """Show dialog to move account to different parent."""
        # TODO: Implement move dialog
        QMessageBox.information(
            self,
            "Move Account",
            "Use drag-and-drop to move accounts, or this feature will be implemented soon!"
        )

    def _make_top_level(self, account_id: int):
        """Move account to top level (remove parent)."""
        try:
            account = self.account_service.get_account(account_id)
            confirm = QMessageBox.question(
                self,
                "Make Top-Level",
                f"Move '{account.name}' to top level?\n\n"
                f"This will remove it from its current parent.",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm == QMessageBox.Yes:
                self.account_service.move_account(account_id, None)
                self.load_accounts()

                QMessageBox.information(
                    self,
                    "Success",
                    f"'{account.name}' is now a top-level account."
                )

        except ValidationError as e:
            QMessageBox.warning(self, "Cannot Move", str(e))
        except Exception as e:
            logger.error(f"Failed to make top-level: {e}")
            QMessageBox.critical(self, "Error", str(e))

    def _convert_to_parent(self, account_id: int):
        """Convert regular account to parent account."""
        try:
            account = self.account_service.get_account(account_id)
            confirm = QMessageBox.question(
                self,
                "Convert to Parent Account",
                f"Convert '{account.name}' to a parent account?\n\n"
                f"Parent accounts:\n"
                f"• Cannot have direct transactions\n"
                f"• Show balance calculated from children\n"
                f"• Are used for grouping other accounts\n\n"
                f"This account must have no transactions to convert.",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm == QMessageBox.Yes:
                self.account_service.convert_to_parent_account(account_id)
                self.load_accounts()

                QMessageBox.information(
                    self,
                    "Success",
                    f"'{account.name}' is now a parent account!"
                )

        except ValidationError as e:
            QMessageBox.warning(self, "Cannot Convert", str(e))
        except Exception as e:
            logger.error(f"Failed to convert to parent: {e}")
            QMessageBox.critical(self, "Error", str(e))

    def _delete_account(self, account_id: int):
        """Delete account (handled by main window)."""
        logger.info(f"Delete account requested: {account_id}")

    def _move_account_up(self, account_id: int):
        """
        Move account up in display order (US-009).

        Args:
            account_id: Account to move up
        """
        try:
            account = self.account_service.get_account(account_id)
            if not account:
                return

            # Get all accounts at the same hierarchy level
            if account.parent_account_id:
                siblings = self.account_service.account_repo.get_child_accounts(account.parent_account_id)
            else:
                siblings = self.account_service.account_repo.get_root_accounts()

            # Find current position
            current_idx = next((i for i, acc in enumerate(siblings) if acc.id == account_id), None)
            if current_idx is None or current_idx == 0:
                return  # Already at top

            # Swap display_order with previous account
            prev_account = siblings[current_idx - 1]
            temp_order = account.display_order
            self.account_service.account_repo.update_display_order(account.id, prev_account.display_order)
            self.account_service.account_repo.update_display_order(prev_account.id, temp_order)

            # Reload tree
            self.load_accounts()
            logger.info(f"Moved account {account.name} up in display order")

        except Exception as e:
            logger.error(f"Failed to move account up: {e}")
            QMessageBox.critical(self, "Move Error", f"Failed to move account:\n{str(e)}")

    def _move_account_down(self, account_id: int):
        """
        Move account down in display order (US-009).

        Args:
            account_id: Account to move down
        """
        try:
            account = self.account_service.get_account(account_id)
            if not account:
                return

            # Get all accounts at the same hierarchy level
            if account.parent_account_id:
                siblings = self.account_service.account_repo.get_child_accounts(account.parent_account_id)
            else:
                siblings = self.account_service.account_repo.get_root_accounts()

            # Find current position
            current_idx = next((i for i, acc in enumerate(siblings) if acc.id == account_id), None)
            if current_idx is None or current_idx == len(siblings) - 1:
                return  # Already at bottom

            # Swap display_order with next account
            next_account = siblings[current_idx + 1]
            temp_order = account.display_order
            self.account_service.account_repo.update_display_order(account.id, next_account.display_order)
            self.account_service.account_repo.update_display_order(next_account.id, temp_order)

            # Reload tree
            self.load_accounts()
            logger.info(f"Moved account {account.name} down in display order")

        except Exception as e:
            logger.error(f"Failed to move account down: {e}")
            QMessageBox.critical(self, "Move Error", f"Failed to move account:\n{str(e)}")

    def _toggle_favorite(self, account_id: int):
        """
        Toggle favorite status for account (US-009).

        Args:
            account_id: Account to toggle favorite
        """
        try:
            account = self.account_service.get_account(account_id)
            if not account:
                return

            # Toggle favorite status
            updated_account = self.account_service.toggle_favorite(account_id)

            # Reload tree to update star indicator
            self.load_accounts()
            logger.info(f"Toggled favorite for account {account.name}: {account.is_favorite} → {updated_account.is_favorite}")

        except Exception as e:
            logger.error(f"Failed to toggle favorite: {e}")
            QMessageBox.critical(self, "Favorite Error", f"Failed to toggle favorite:\n{str(e)}")
