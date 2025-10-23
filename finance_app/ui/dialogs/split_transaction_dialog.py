"""
Transaction Splits Dialog - Manage splits for a transaction.

Story: US-002C - Split Transactions (Day 4)

This dialog is opened from the main transaction dialog's split button
and allows users to split a transaction across multiple categories.
Follows HomeBank's UX pattern exactly.
"""
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Dict

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget, QComboBox, QLineEdit, QPushButton,
    QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDoubleValidator

from finance_app.data.database import Database
from finance_app.data.models import Category
from finance_app.data.repositories.category_repository import CategoryRepository
from finance_app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SplitTransactionDialog(QDialog):
    """
    Dialog for managing transaction splits (HomeBank pattern).

    Clean, minimal design matching HomeBank's split dialog exactly.
    """

    splits_saved = Signal(list)

    def __init__(
        self,
        database: Database,
        transaction_type: str = "expense",
        existing_splits: Optional[List[Dict]] = None,
        parent=None
    ):
        """Initialize splits dialog."""
        super().__init__(parent)
        self.db = database
        self.transaction_type = transaction_type
        self.existing_splits = existing_splits or []

        # Repository
        self.category_repo = CategoryRepository(database)

        # Load categories
        if transaction_type == "expense":
            self.categories = self.category_repo.get_all('expense')
        else:
            self.categories = self.category_repo.get_all('income')

        self.setup_ui()
        self.apply_styling()

        # Load existing splits only (HomeBank pattern - start clean)
        if self.existing_splits:
            self._load_existing_splits()

        logger.info(f"Split dialog opened: type={transaction_type}")

    def setup_ui(self) -> None:
        """Set up user interface (HomeBank-inspired clean design)."""
        self.setWindowTitle("Transaction splits")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(450)
        self.resize(750, 500)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Splits table (clean, minimal)
        self.splits_table = QTableWidget()
        self.splits_table.setColumnCount(4)
        self.splits_table.setHorizontalHeaderLabels([
            "#", "Category", "Memo", "Amount"
        ])
        self.splits_table.verticalHeader().setVisible(False)
        self.splits_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.splits_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.splits_table.setAlternatingRowColors(True)
        self.splits_table.setShowGrid(True)

        # Column sizing (HomeBank pattern)
        header = self.splits_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)    # #
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Category
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Memo
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # Amount
        self.splits_table.setColumnWidth(0, 40)
        self.splits_table.setColumnWidth(3, 180)

        main_layout.addWidget(self.splits_table)

        # Bottom add row (HomeBank pattern)
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)

        # Category
        bottom_row.addWidget(QLabel("Category:"))
        self.add_category = QComboBox()
        self.add_category.addItem("Category", None)
        for category in self.categories:
            self.add_category.addItem(category.name, category.id)
        bottom_row.addWidget(self.add_category, 2)

        # Memo
        bottom_row.addWidget(QLabel("Memo:"))
        self.add_memo = QLineEdit()
        self.add_memo.setPlaceholderText("Memo...")
        bottom_row.addWidget(self.add_memo, 2)

        # Amount with -/+ buttons
        expense_label = QLabel("Expense:" if self.transaction_type == "expense" else "Income:")
        bottom_row.addWidget(expense_label)

        self.add_amount = QLineEdit()
        self.add_amount.setPlaceholderText("0.00")
        self.add_amount.setFixedWidth(80)
        validator = QDoubleValidator(0.01, 999999.99, 2, self)
        self.add_amount.setValidator(validator)
        bottom_row.addWidget(self.add_amount)

        # Compact -/+ buttons
        minus_btn = QPushButton("−")
        minus_btn.setObjectName("compactButton")
        minus_btn.setFixedWidth(22)
        minus_btn.clicked.connect(lambda: self._adjust_add_amount(-1))
        bottom_row.addWidget(minus_btn)

        plus_btn = QPushButton("+")
        plus_btn.setObjectName("compactButton")
        plus_btn.setFixedWidth(22)
        plus_btn.clicked.connect(lambda: self._adjust_add_amount(1))
        bottom_row.addWidget(plus_btn)

        # Add button (blue)
        add_btn = QPushButton("+")
        add_btn.setObjectName("addButton")
        add_btn.setFixedWidth(28)
        add_btn.setToolTip("Add split")
        add_btn.clicked.connect(self._add_current_split)
        bottom_row.addWidget(add_btn)

        main_layout.addLayout(bottom_row)

        # Summary labels (HomeBank style - right aligned)
        summary_layout = QVBoxLayout()
        summary_layout.setSpacing(4)

        # Sum of splits
        sum_row = QHBoxLayout()
        sum_row.addStretch()
        sum_row.addWidget(QLabel("Sum of splits:"))
        self.sum_label = QLabel("₱ 0.00")
        self.sum_label.setObjectName("sumLabel")
        sum_row.addWidget(self.sum_label)
        summary_layout.addLayout(sum_row)

        main_layout.addLayout(summary_layout)

        # Status indicator
        self.status_label = QLabel("Add splits to create transaction")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(32)
        main_layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(90)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setObjectName("primaryButton")
        self.ok_btn.setDefault(True)
        self.ok_btn.setMinimumWidth(90)
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(self.ok_btn)

        main_layout.addLayout(button_layout)

        # Initialize
        self._update_sum_and_status()

    def _add_split_row(self) -> None:
        """Add a new split row to the table."""
        row = self.splits_table.rowCount()
        self.splits_table.insertRow(row)

        # # column
        num_item = QTableWidgetItem(str(row + 1))
        num_item.setFlags(num_item.flags() & ~Qt.ItemIsEditable)
        num_item.setTextAlignment(Qt.AlignCenter)
        self.splits_table.setItem(row, 0, num_item)

        # Category dropdown
        category_combo = QComboBox()
        category_combo.addItem("Select category...", None)
        for category in self.categories:
            category_combo.addItem(category.name, category.id)
        category_combo.currentIndexChanged.connect(self._update_sum_and_status)
        self.splits_table.setCellWidget(row, 1, category_combo)

        # Memo input
        memo_edit = QLineEdit()
        memo_edit.setPlaceholderText("Optional note...")
        self.splits_table.setCellWidget(row, 2, memo_edit)

        # Amount with delete button
        amount_widget = QWidget()
        amount_layout = QHBoxLayout(amount_widget)
        amount_layout.setContentsMargins(4, 2, 4, 2)
        amount_layout.setSpacing(4)

        amount_edit = QLineEdit()
        amount_edit.setPlaceholderText("0.00")
        amount_edit.setAlignment(Qt.AlignRight)
        validator = QDoubleValidator(0.01, 999999.99, 2, self)
        amount_edit.setValidator(validator)
        amount_edit.textChanged.connect(self._update_sum_and_status)
        amount_layout.addWidget(amount_edit, 1)

        # Delete button
        delete_btn = QPushButton("🗑")
        delete_btn.setObjectName("deleteButton")
        delete_btn.setToolTip("Delete")
        delete_btn.setFixedWidth(28)
        delete_btn.clicked.connect(lambda: self._delete_split_row(row))
        amount_layout.addWidget(delete_btn)

        self.splits_table.setCellWidget(row, 3, amount_widget)
        self._update_sum_and_status()

    def _add_current_split(self) -> None:
        """Add the current bottom row as a split."""
        category_id = self.add_category.currentData()
        if not category_id:
            QMessageBox.warning(self, "Missing Category", "Please select a category")
            return

        amount_text = self.add_amount.text().strip()
        if not amount_text:
            QMessageBox.warning(self, "Missing Amount", "Please enter an amount")
            return

        try:
            amount = Decimal(amount_text)
            if amount <= 0:
                raise ValueError()
        except (InvalidOperation, ValueError):
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid amount")
            return

        # Add split
        self._add_split_row()
        row = self.splits_table.rowCount() - 1

        # Set values
        category_combo = self.splits_table.cellWidget(row, 1)
        for i in range(category_combo.count()):
            if category_combo.itemData(i) == category_id:
                category_combo.setCurrentIndex(i)
                break

        memo_edit = self.splits_table.cellWidget(row, 2)
        memo_edit.setText(self.add_memo.text())

        amount_widget = self.splits_table.cellWidget(row, 3)
        amount_edit = amount_widget.layout().itemAt(0).widget()
        amount_edit.setText(amount_text)

        # Clear inputs
        self.add_category.setCurrentIndex(0)
        self.add_memo.clear()
        self.add_amount.clear()
        self.add_category.setFocus()

    def _delete_split_row(self, row: int) -> None:
        """Delete a split row."""
        if self.splits_table.rowCount() <= 2:
            QMessageBox.warning(
                self,
                "Minimum Splits",
                "Split transaction must have at least 2 splits."
            )
            return

        self.splits_table.removeRow(row)

        # Renumber
        for i in range(self.splits_table.rowCount()):
            num_item = self.splits_table.item(i, 0)
            if num_item:
                num_item.setText(str(i + 1))

        self._update_sum_and_status()

    def _adjust_add_amount(self, delta: int) -> None:
        """Adjust amount by delta."""
        try:
            current = Decimal(self.add_amount.text() or "0")
            new_value = max(Decimal("0"), current + Decimal(str(delta)))
            self.add_amount.setText(f"{new_value:.2f}")
        except (InvalidOperation, ValueError):
            pass

    def _update_sum_and_status(self) -> None:
        """Update sum and status."""
        total = Decimal("0")
        split_count = 0

        for row in range(self.splits_table.rowCount()):
            amount_widget = self.splits_table.cellWidget(row, 3)
            if amount_widget:
                amount_edit = amount_widget.layout().itemAt(0).widget()
                amount_text = amount_edit.text().strip()
                try:
                    if amount_text:
                        total += Decimal(amount_text)
                        split_count += 1
                except (InvalidOperation, ValueError):
                    pass

        # Update sum
        self.sum_label.setText(f"₱ {total:.2f}")

        # Update status
        if total == 0:
            self.status_label.setText("Add splits to create transaction")
            self.status_label.setProperty("state", "empty")
            self.ok_btn.setEnabled(False)
        elif split_count < 2:
            self.status_label.setText("Need at least 2 splits")
            self.status_label.setProperty("state", "warning")
            self.ok_btn.setEnabled(False)
        else:
            self.status_label.setText(f"Ready - {split_count} splits")
            self.status_label.setProperty("state", "ready")
            self.ok_btn.setEnabled(True)

        # Force style refresh
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _load_existing_splits(self) -> None:
        """Load existing splits."""
        for split_data in self.existing_splits:
            self._add_split_row()
            row = self.splits_table.rowCount() - 1

            category_combo = self.splits_table.cellWidget(row, 1)
            category_id = split_data.get('category_id')
            for i in range(category_combo.count()):
                if category_combo.itemData(i) == category_id:
                    category_combo.setCurrentIndex(i)
                    break

            memo_edit = self.splits_table.cellWidget(row, 2)
            memo_edit.setText(split_data.get('memo', ''))

            amount_widget = self.splits_table.cellWidget(row, 3)
            amount_edit = amount_widget.layout().itemAt(0).widget()
            amount_edit.setText(str(split_data.get('amount', '')))

    def _on_ok(self) -> None:
        """Validate and save."""
        splits = []
        for row in range(self.splits_table.rowCount()):
            category_combo = self.splits_table.cellWidget(row, 1)
            category_id = category_combo.currentData()

            if not category_id:
                QMessageBox.warning(
                    self,
                    "Missing Category",
                    f"Please select a category for split #{row + 1}"
                )
                return

            amount_widget = self.splits_table.cellWidget(row, 3)
            amount_edit = amount_widget.layout().itemAt(0).widget()
            amount_text = amount_edit.text().strip()

            if not amount_text:
                QMessageBox.warning(
                    self,
                    "Missing Amount",
                    f"Please enter an amount for split #{row + 1}"
                )
                return

            try:
                amount = Decimal(amount_text)
                if amount <= 0:
                    raise ValueError()
            except (InvalidOperation, ValueError):
                QMessageBox.warning(
                    self,
                    "Invalid Amount",
                    f"Invalid amount for split #{row + 1}"
                )
                return

            memo_edit = self.splits_table.cellWidget(row, 2)
            memo = memo_edit.text().strip() or None

            splits.append({
                'category_id': category_id,
                'amount': amount,
                'memo': memo,
                'split_order': row
            })

        if len(splits) < 2:
            QMessageBox.warning(
                self,
                "Minimum Splits",
                "Split transaction must have at least 2 splits"
            )
            return

        self.splits_saved.emit(splits)
        logger.info(f"Splits saved: {len(splits)} splits totaling ${sum(s['amount'] for s in splits):.2f}")
        self.accept()

    def get_splits(self) -> Optional[List[Dict]]:
        """Get splits data."""
        if self.result() != QDialog.Accepted:
            return None

        splits = []
        for row in range(self.splits_table.rowCount()):
            category_combo = self.splits_table.cellWidget(row, 1)
            category_id = category_combo.currentData()

            amount_widget = self.splits_table.cellWidget(row, 3)
            amount_edit = amount_widget.layout().itemAt(0).widget()
            amount_text = amount_edit.text().strip()

            memo_edit = self.splits_table.cellWidget(row, 2)
            memo = memo_edit.text().strip() or None

            if category_id and amount_text:
                try:
                    splits.append({
                        'category_id': category_id,
                        'amount': Decimal(amount_text),
                        'memo': memo,
                        'split_order': row
                    })
                except (InvalidOperation, ValueError):
                    pass

        return splits if splits else None

    def get_total_amount(self) -> Decimal:
        """Get total from splits."""
        total = Decimal("0")
        for row in range(self.splits_table.rowCount()):
            amount_widget = self.splits_table.cellWidget(row, 3)
            if amount_widget:
                amount_edit = amount_widget.layout().itemAt(0).widget()
                amount_text = amount_edit.text().strip()
                try:
                    if amount_text:
                        total += Decimal(amount_text)
                except (InvalidOperation, ValueError):
                    pass
        return total

    def apply_styling(self) -> None:
        """Apply clean styling (matching HomeBank better)."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }

            QLabel {
                color: #cccccc;
                font-size: 12px;
            }

            QLabel#sumLabel {
                color: #10B981;
                font-size: 14px;
                font-weight: bold;
            }

            QLabel#statusLabel {
                font-size: 12px;
                padding: 6px;
                border-radius: 3px;
            }

            QLabel#statusLabel[state="empty"] {
                color: #888888;
                background-color: transparent;
            }

            QLabel#statusLabel[state="warning"] {
                color: #F59E0B;
                background-color: #4d3a1a;
            }

            QLabel#statusLabel[state="ready"] {
                color: #10B981;
                background-color: #1a4d2e;
            }

            QLineEdit, QComboBox {
                padding: 4px 6px;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 2px;
                color: #ffffff;
                font-size: 12px;
                min-height: 20px;
            }

            QLineEdit:focus, QComboBox:focus {
                border-color: #0078d4;
            }

            QComboBox::drop-down {
                border: none;
                width: 18px;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 4px solid #ffffff;
            }

            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #ffffff;
                selection-background-color: #0078d4;
                border: 1px solid #555555;
            }

            QTableWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                gridline-color: #4a4a4a;
                border: 1px solid #555555;
                border-radius: 2px;
            }

            QTableWidget::item:selected {
                background-color: #0078d4;
            }

            QHeaderView::section {
                background-color: #2b2b2b;
                color: #cccccc;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #555555;
                border-right: 1px solid #4a4a4a;
                font-weight: bold;
                font-size: 11px;
            }

            QPushButton {
                padding: 6px 14px;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 2px;
                color: #ffffff;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #4a4a4a;
            }

            QPushButton:pressed {
                background-color: #2a2a2a;
            }

            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
            }

            QPushButton#primaryButton {
                background-color: #0078d4;
                border-color: #0078d4;
                font-weight: bold;
            }

            QPushButton#primaryButton:hover {
                background-color: #1084e0;
            }

            QPushButton#primaryButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
            }

            QPushButton#compactButton {
                padding: 4px;
                min-width: 22px;
                max-width: 22px;
                font-weight: bold;
            }

            QPushButton#addButton {
                padding: 4px;
                min-width: 28px;
                max-width: 28px;
                background-color: #0078d4;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton#addButton:hover {
                background-color: #1084e0;
            }

            QPushButton#deleteButton {
                padding: 4px;
                min-width: 28px;
                max-width: 28px;
                background-color: #5c2b2b;
                border-color: #7a3737;
            }

            QPushButton#deleteButton:hover {
                background-color: #7a3737;
            }
        """)
