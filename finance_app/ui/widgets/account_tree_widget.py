"""
Account Tree Widget for hierarchical account display.

US-006: Displays accounts in a tree structure with parent/child relationships.
"""
from typing import Optional, Dict
from decimal import Decimal

from PySide6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, QMessageBox, QMenu, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDropEvent, QDragMoveEvent, QIcon, QAction

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

        self.setup_ui()
        self.setup_drag_drop()
        self.connect_signals()

    def setup_ui(self):
        """Configure tree widget appearance and behavior."""
        # Column configuration
        self.setHeaderLabels(["Account", "Balance"])
        self.setColumnWidth(0, 300)
        self.setColumnWidth(1, 150)

        # Make columns user-resizable but maintain minimum sizes
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.Interactive)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)

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

        # Store account ID in item data
        item.setData(0, Qt.UserRole, account.id)

        # Format account name with icon
        if account.is_parent:
            # Parent account - folder icon
            account_name = f"📁 {account.name}"
        else:
            # Leaf account - different icons based on type
            icon = self._get_account_icon(account)
            account_name = f"{icon} {account.name}"

        item.setText(0, account_name)

        # Format balance
        if account.is_parent:
            # Calculate parent balance from children
            try:
                parent_balance = self.account_service.get_parent_account_balance_sql(account.id)
                balance_text = f"${parent_balance:,.2f}"
            except Exception as e:
                logger.warning(f"Failed to calculate parent balance for {account.name}: {e}")
                balance_text = "$0.00"

            # Bold font for parent accounts
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)
            item.setFont(1, font)

            # Gray color for parent balance
            item.setForeground(1, Qt.gray)
        else:
            # Leaf account - use actual balance
            balance_text = f"${account.balance:,.2f}"

        # Color code balance (red for negative, green for positive)
        if account.balance < 0 or (account.is_parent and "parent_balance" in locals() and parent_balance < 0):
            item.setForeground(1, Qt.red)
        elif account.balance > 0 or (account.is_parent and "parent_balance" in locals() and parent_balance > 0):
            item.setForeground(1, Qt.darkGreen)

        item.setText(1, balance_text)
        item.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)

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

    def _on_selection_changed(self):
        """Handle account selection."""
        selected_items = self.selectedItems()
        if selected_items:
            item = selected_items[0]
            account_id = item.data(0, Qt.UserRole)
            logger.debug(f"Account selected: ID={account_id}")
            self.account_selected.emit(account_id)

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
