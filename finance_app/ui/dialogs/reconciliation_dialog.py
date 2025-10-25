"""
Reconciliation dialog for matching transactions with bank statements.

Story: US-004 - Account Reconciliation (Phase 5 - Day 4)

This dialog provides a complete interface for reconciling account transactions
against bank statements, inspired by HomeBank's reconciliation workflow.
"""
from decimal import Decimal, InvalidOperation
from typing import List, Optional
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QDateEdit, QPushButton, QLabel, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QDoubleValidator

from finance_app.data.database import Database
from finance_app.data.models import Account, Transaction, ReconciliationStatus
from finance_app.business.reconciliation_service import ReconciliationService
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import NotFoundError, ValidationError, BusinessRuleError

logger = setup_logger(__name__)


class ReconciliationDialog(QDialog):
    """
    Dialog for reconciling account transactions with bank statements.

    Features:
    - Statement date and balance input
    - Transaction list with clear/unclear checkboxes
    - Real-time balance calculations
    - Discrepancy tracking and color-coding
    - Notes field for explaining discrepancies
    """

    # Signal emitted when reconciliation is completed successfully
    reconciliation_completed = Signal(int)  # reconciliation_id

    def __init__(self, database: Database, account: Account, parent=None):
        """
        Initialize reconciliation dialog.

        Args:
            database: Database instance
            account: Account to reconcile
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = database
        self.account = account
        self.service = ReconciliationService(database)

        # Track reconciliation session data
        self.session_data = None
        self.transactions = []
        self.checked_transactions = set()  # Transaction IDs that are checked

        # Initialize UI
        self.setup_ui()
        self.apply_styling()
        self.load_reconciliation_data()

        logger.info(f"ReconciliationDialog initialized for account: {account.name}")

    def setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle(f"Reconcile Account - {self.account.name}")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.resize(900, 700)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Header with account name
        header_label = QLabel(f"<h2>Reconcile: {self.account.name}</h2>")
        header_label.setObjectName("dialogHeader")
        main_layout.addWidget(header_label)

        # Statement Details Section
        statement_group = self._create_statement_section()
        main_layout.addWidget(statement_group)

        # Transaction List Section
        transactions_group = self._create_transactions_section()
        main_layout.addWidget(transactions_group, stretch=1)

        # Summary Section
        summary_group = self._create_summary_section()
        main_layout.addWidget(summary_group)

        # Action Buttons
        button_layout = self._create_button_layout()
        main_layout.addLayout(button_layout)

    def _create_statement_section(self) -> QGroupBox:
        """
        Create the statement details input section.

        Task 4.27: Statement details section with HomeBank-inspired layout
        """
        group = QGroupBox("Statement Details")
        group.setObjectName("statementGroup")

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(8)

        # Account name (read-only display)
        account_label = QLabel(self.account.name)
        account_label.setObjectName("accountNameLabel")
        form_layout.addRow("Account:", account_label)

        # Statement date picker
        self.statement_date_edit = QDateEdit()
        self.statement_date_edit.setDate(QDate.currentDate())
        self.statement_date_edit.setCalendarPopup(True)
        self.statement_date_edit.setDisplayFormat("MMM dd, yyyy")
        self.statement_date_edit.setMinimumWidth(150)
        form_layout.addRow("Statement Date:", self.statement_date_edit)

        # Statement balance input
        balance_layout = QHBoxLayout()
        balance_layout.setSpacing(4)

        currency_label = QLabel("$")
        currency_label.setObjectName("currencySymbol")
        balance_layout.addWidget(currency_label)

        self.statement_balance_edit = QLineEdit()
        self.statement_balance_edit.setPlaceholderText("0.00")

        # Validator for decimal input (2 decimal places)
        validator = QDoubleValidator(0.0, 999999999.99, 2, self)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.statement_balance_edit.setValidator(validator)
        self.statement_balance_edit.setMinimumWidth(150)

        # Connect to recalculate summary when balance changes
        self.statement_balance_edit.textChanged.connect(self._update_summary)

        balance_layout.addWidget(self.statement_balance_edit)
        balance_layout.addStretch()

        balance_widget = QWidget()
        balance_widget.setLayout(balance_layout)
        form_layout.addRow("Statement Balance:", balance_widget)

        group.setLayout(form_layout)
        return group

    def _create_transactions_section(self) -> QGroupBox:
        """
        Create the transactions list table section.

        Task 4.28: Transaction list with checkboxes for cleared/uncleared
        """
        group = QGroupBox("Unreconciled Transactions")
        group.setObjectName("transactionsGroup")

        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Info label
        info_label = QLabel("Check transactions that appear on your statement:")
        info_label.setObjectName("infoLabel")
        layout.addWidget(info_label)

        # Create table widget
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels([
            "✓", "Date", "Description", "Amount", "Status"
        ])

        # Set column widths
        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Checkbox column
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Date column
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Description (stretches)
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Amount column
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Status column

        self.transactions_table.setColumnWidth(0, 40)   # Checkbox
        self.transactions_table.setColumnWidth(1, 100)  # Date
        self.transactions_table.setColumnWidth(3, 120)  # Amount
        self.transactions_table.setColumnWidth(4, 100)  # Status

        # Table settings
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transactions_table.setSelectionMode(QTableWidget.SingleSelection)
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.verticalHeader().setVisible(False)
        self.transactions_table.setShowGrid(False)

        layout.addWidget(self.transactions_table)

        # Transaction count label
        self.transaction_count_label = QLabel("0 transactions")
        self.transaction_count_label.setObjectName("countLabel")
        layout.addWidget(self.transaction_count_label)

        group.setLayout(layout)
        return group

    def _create_summary_section(self) -> QGroupBox:
        """
        Create the reconciliation summary section.

        Task 4.29: Summary section with real-time calculations
        """
        group = QGroupBox("Reconciliation Summary")
        group.setObjectName("summaryGroup")

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(6)

        # Opening Balance
        self.opening_balance_label = QLabel("$0.00")
        self.opening_balance_label.setObjectName("summaryValue")
        form_layout.addRow("Opening Balance:", self.opening_balance_label)

        # Cleared Transactions
        self.cleared_transactions_label = QLabel("$0.00")
        self.cleared_transactions_label.setObjectName("summaryValue")
        form_layout.addRow("Cleared Transactions:", self.cleared_transactions_label)

        # Cleared Balance
        self.cleared_balance_label = QLabel("$0.00")
        self.cleared_balance_label.setObjectName("summaryValue")
        form_layout.addRow("Cleared Balance:", self.cleared_balance_label)

        # Statement Balance
        self.statement_balance_label = QLabel("$0.00")
        self.statement_balance_label.setObjectName("summaryValue")
        form_layout.addRow("Statement Balance:", self.statement_balance_label)

        # Separator line
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setObjectName("separator")
        form_layout.addRow("", separator)

        # Discrepancy (color-coded)
        self.discrepancy_label = QLabel("$0.00")
        self.discrepancy_label.setObjectName("discrepancyValue")
        self.discrepancy_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        discrepancy_row = QWidget()
        discrepancy_layout = QHBoxLayout(discrepancy_row)
        discrepancy_layout.setContentsMargins(0, 0, 0, 0)
        discrepancy_layout.addWidget(self.discrepancy_label)
        form_layout.addRow("Discrepancy:", discrepancy_row)

        # Discrepancy explanation
        self.discrepancy_status_label = QLabel("")
        self.discrepancy_status_label.setObjectName("discrepancyStatus")
        self.discrepancy_status_label.setWordWrap(True)
        form_layout.addRow("", self.discrepancy_status_label)

        group.setLayout(form_layout)
        return group

    def _create_button_layout(self) -> QHBoxLayout:
        """
        Create the action button layout.

        Task 4.31: Action buttons with validation
        """
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumWidth(100)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()

        # Complete Reconciliation button
        self.complete_btn = QPushButton("Complete Reconciliation")
        self.complete_btn.setObjectName("primaryButton")
        self.complete_btn.setMinimumWidth(180)
        self.complete_btn.clicked.connect(self._on_complete_reconciliation)
        self.complete_btn.setEnabled(False)  # Disabled until valid
        button_layout.addWidget(self.complete_btn)

        return button_layout

    def load_reconciliation_data(self) -> None:
        """
        Load reconciliation data from the service.

        This method:
        1. Starts the reconciliation session
        2. Gets unreconciled transactions
        3. Populates the table
        4. Initializes the summary
        """
        try:
            # Get current statement balance (if any) to prefill
            statement_balance = Decimal("0.00")

            # Start reconciliation session
            self.session_data = self.service.start_reconciliation(
                account_id=self.account.id,
                statement_date=datetime.now().strftime('%Y-%m-%d'),
                statement_balance=statement_balance
            )

            # Get unreconciled transactions
            self.transactions = self.service.get_unreconciled_transactions(self.account.id)

            # Populate table
            self._populate_transactions_table()

            # Update summary with opening balance
            self._update_summary()

            logger.info(
                f"Loaded reconciliation data: {len(self.transactions)} unreconciled transactions, "
                f"opening balance: ${self.session_data['opening_balance']}"
            )

        except BusinessRuleError as e:
            # Concurrent reconciliation in progress
            QMessageBox.warning(
                self,
                "Reconciliation In Progress",
                str(e)
            )
            self.reject()
        except Exception as e:
            logger.error(f"Failed to load reconciliation data: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load reconciliation data: {str(e)}"
            )
            self.reject()

    def _populate_transactions_table(self) -> None:
        """Populate the transactions table with unreconciled transactions."""
        self.transactions_table.setRowCount(len(self.transactions))

        for row, transaction in enumerate(self.transactions):
            # Column 0: Checkbox
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignCenter)

            checkbox = QCheckBox()
            checkbox.setProperty("transaction_id", transaction.id)
            checkbox.stateChanged.connect(lambda state, txn_id=transaction.id: self._on_checkbox_changed(state, txn_id))
            checkbox_layout.addWidget(checkbox)

            self.transactions_table.setCellWidget(row, 0, checkbox_widget)

            # Column 1: Date
            date_item = QTableWidgetItem(transaction.date)
            date_item.setTextAlignment(Qt.AlignCenter)
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.transactions_table.setItem(row, 1, date_item)

            # Column 2: Description
            desc_item = QTableWidgetItem(transaction.description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.transactions_table.setItem(row, 2, desc_item)

            # Column 3: Amount (formatted, right-aligned, color-coded)
            amount = transaction.amount
            amount_text = f"${abs(amount):,.2f}"
            if amount < 0:
                amount_text = f"-{amount_text}"

            amount_item = QTableWidgetItem(amount_text)
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)

            # Color-code amount (red for negative, green for positive)
            if amount < 0:
                amount_item.setForeground(Qt.GlobalColor.red)
            else:
                amount_item.setForeground(Qt.GlobalColor.green)

            self.transactions_table.setItem(row, 3, amount_item)

            # Column 4: Status badge
            status = transaction.reconciliation_status.value if hasattr(transaction.reconciliation_status, 'value') else transaction.reconciliation_status
            status_item = QTableWidgetItem(status.title())
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.transactions_table.setItem(row, 4, status_item)

        # Update count label
        count = len(self.transactions)
        self.transaction_count_label.setText(
            f"{count} transaction{'s' if count != 1 else ''}"
        )

    def _on_checkbox_changed(self, state: int, transaction_id: int) -> None:
        """
        Handle checkbox state change.

        Args:
            state: Qt.CheckState value (0=unchecked, 2=checked)
            transaction_id: ID of the transaction
        """
        if state == Qt.Checked:
            self.checked_transactions.add(transaction_id)
            logger.debug(f"Transaction {transaction_id} marked as cleared")
        else:
            self.checked_transactions.discard(transaction_id)
            logger.debug(f"Transaction {transaction_id} unmarked")

        # Recalculate summary
        self._update_summary()

    def _update_summary(self) -> None:
        """
        Update the reconciliation summary section with real-time calculations.

        Task 4.30: Real-time balance calculations with color-coding
        """
        try:
            # Get opening balance from session data
            opening_balance = Decimal(str(self.session_data['opening_balance']))

            # Calculate sum of checked (cleared) transactions
            cleared_sum = Decimal("0.00")
            for transaction in self.transactions:
                if transaction.id in self.checked_transactions:
                    cleared_sum += transaction.amount

            # Calculate cleared balance
            cleared_balance = opening_balance + cleared_sum

            # Get statement balance from input
            statement_balance_text = self.statement_balance_edit.text().strip()
            if statement_balance_text:
                try:
                    statement_balance = Decimal(statement_balance_text)
                except (InvalidOperation, ValueError):
                    statement_balance = Decimal("0.00")
            else:
                statement_balance = Decimal("0.00")

            # Calculate discrepancy
            discrepancy = statement_balance - cleared_balance

            # Update labels
            self.opening_balance_label.setText(f"${opening_balance:,.2f}")
            self.cleared_transactions_label.setText(
                f"${cleared_sum:+,.2f}" if cleared_sum != 0 else "$0.00"
            )
            self.cleared_balance_label.setText(f"${cleared_balance:,.2f}")
            self.statement_balance_label.setText(f"${statement_balance:,.2f}")
            self.discrepancy_label.setText(f"${abs(discrepancy):,.2f}")

            # Color-code discrepancy and update status message
            if abs(discrepancy) < Decimal("0.01"):
                # Balanced! (green)
                self.discrepancy_label.setStyleSheet("""
                    QLabel {
                        color: #4CAF50;
                        font-weight: bold;
                        font-size: 16px;
                    }
                """)
                self.discrepancy_status_label.setText("✓ Accounts are balanced!")
                self.discrepancy_status_label.setStyleSheet("color: #4CAF50;")
                self.complete_btn.setEnabled(True)

            elif discrepancy > 0:
                # Positive discrepancy - missing transactions (yellow/warning)
                self.discrepancy_label.setStyleSheet("""
                    QLabel {
                        color: #FF9800;
                        font-weight: bold;
                        font-size: 16px;
                    }
                """)
                self.discrepancy_status_label.setText(
                    f"⚠ Statement balance is ${discrepancy:,.2f} higher. "
                    "Check for missing transactions in your records."
                )
                self.discrepancy_status_label.setStyleSheet("color: #FF9800;")
                self.complete_btn.setEnabled(True)  # Allow with confirmation

            else:
                # Negative discrepancy - extra transactions (red/error)
                self.discrepancy_label.setStyleSheet("""
                    QLabel {
                        color: #F44336;
                        font-weight: bold;
                        font-size: 16px;
                    }
                """)
                self.discrepancy_status_label.setText(
                    f"⚠ Statement balance is ${abs(discrepancy):,.2f} lower. "
                    "Check for uncleared transactions or errors."
                )
                self.discrepancy_status_label.setStyleSheet("color: #F44336;")
                self.complete_btn.setEnabled(True)  # Allow with confirmation

            logger.debug(
                f"Summary updated: opening={opening_balance}, cleared={cleared_sum}, "
                f"cleared_balance={cleared_balance}, statement={statement_balance}, "
                f"discrepancy={discrepancy}"
            )

        except Exception as e:
            logger.error(f"Error updating summary: {e}")

    def _on_complete_reconciliation(self) -> None:
        """
        Handle complete reconciliation button click.

        This method:
        1. Validates input
        2. Confirms discrepancy if exists
        3. Marks transactions as cleared
        4. Completes reconciliation via service
        5. Emits success signal
        """
        try:
            # Validate statement balance
            statement_balance_text = self.statement_balance_edit.text().strip()
            if not statement_balance_text:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Please enter the statement balance."
                )
                self.statement_balance_edit.setFocus()
                return

            try:
                statement_balance = Decimal(statement_balance_text)
            except (InvalidOperation, ValueError):
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Please enter a valid statement balance."
                )
                self.statement_balance_edit.setFocus()
                return

            # Get statement date
            statement_date = self.statement_date_edit.date().toString("yyyy-MM-dd")

            # Calculate current discrepancy
            opening_balance = Decimal(str(self.session_data['opening_balance']))
            cleared_sum = sum(
                txn.amount for txn in self.transactions
                if txn.id in self.checked_transactions
            )
            cleared_balance = opening_balance + cleared_sum
            discrepancy = statement_balance - cleared_balance

            # If discrepancy exists, ask for confirmation and notes
            notes = None
            if abs(discrepancy) >= Decimal("0.01"):
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Discrepancy Detected")
                msg.setText(
                    f"<b>There is a discrepancy of ${abs(discrepancy):,.2f}</b><br><br>"
                    f"Cleared Balance: ${cleared_balance:,.2f}<br>"
                    f"Statement Balance: ${statement_balance:,.2f}<br><br>"
                    "Do you want to proceed with this reconciliation?"
                )
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg.setDefaultButton(QMessageBox.No)

                if msg.exec() != QMessageBox.Yes:
                    return

                # Ask for notes to explain discrepancy
                from PySide6.QtWidgets import QInputDialog
                notes, ok = QInputDialog.getMultiLineText(
                    self,
                    "Reconciliation Notes",
                    "Please provide a note explaining the discrepancy:",
                    f"Discrepancy of ${discrepancy:,.2f} - "
                )

                if not ok:
                    return

            # Mark all checked transactions as cleared
            for transaction in self.transactions:
                if transaction.id in self.checked_transactions:
                    self.service.mark_transaction_cleared(
                        transaction_id=transaction.id,
                        statement_date=statement_date
                    )

            # Complete reconciliation
            reconciliation = self.service.complete_reconciliation(
                account_id=self.account.id,
                statement_date=statement_date,
                statement_balance=statement_balance,
                notes=notes
            )

            # Show success message
            QMessageBox.information(
                self,
                "Reconciliation Complete",
                f"<b>Account reconciled successfully!</b><br><br>"
                f"Reconciliation ID: {reconciliation.id}<br>"
                f"Transactions cleared: {reconciliation.transaction_count}<br>"
                f"Discrepancy: ${abs(reconciliation.discrepancy):,.2f}"
            )

            # Emit signal and close
            self.reconciliation_completed.emit(reconciliation.id)
            self.accept()

            logger.info(
                f"Reconciliation completed: ID={reconciliation.id}, "
                f"cleared={reconciliation.transaction_count}, "
                f"discrepancy=${reconciliation.discrepancy}"
            )

        except ValidationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except BusinessRuleError as e:
            QMessageBox.warning(self, "Business Rule Error", str(e))
        except Exception as e:
            logger.error(f"Failed to complete reconciliation: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to complete reconciliation: {str(e)}"
            )

    def apply_styling(self) -> None:
        """
        Apply QSS styling to match application dark theme.

        Task 4.32: Dark theme styling matching UnifiedTransactionDialog
        """
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }

            QLabel {
                color: #ffffff;
                font-size: 13px;
            }

            QLabel#dialogHeader {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding: 8px 0;
            }

            QLabel#accountNameLabel {
                color: #0078d4;
                font-weight: bold;
                font-size: 14px;
            }

            QLabel#currencySymbol {
                color: #b0b0b0;
                font-weight: bold;
                font-size: 14px;
                padding-right: 4px;
            }

            QLabel#infoLabel {
                color: #b0b0b0;
                font-size: 12px;
                font-style: italic;
                padding: 4px 0;
            }

            QLabel#countLabel {
                color: #888888;
                font-size: 12px;
                padding: 4px 0;
            }

            QLabel#summaryValue {
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
            }

            QLabel#discrepancyValue {
                font-weight: bold;
                font-size: 16px;
                padding: 4px 8px;
                border-radius: 3px;
            }

            QLabel#discrepancyStatus {
                font-size: 12px;
                padding: 4px 0;
            }

            QLabel#separator {
                background-color: #555555;
                margin: 4px 0;
            }

            QLineEdit, QDateEdit {
                padding: 6px;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                color: #ffffff;
                font-size: 13px;
                min-height: 24px;
            }

            QLineEdit:focus, QDateEdit:focus {
                border-color: #0078d4;
                background-color: #404040;
            }

            QLineEdit::placeholder {
                color: #888888;
            }

            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #2b2b2b;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                color: #ffffff;
            }

            QGroupBox#statementGroup, QGroupBox#summaryGroup {
                background-color: #333333;
            }

            QTableWidget {
                background-color: #2b2b2b;
                alternate-background-color: #323232;
                border: 1px solid #555555;
                border-radius: 3px;
                gridline-color: #3c3c3c;
            }

            QTableWidget::item {
                padding: 6px;
                color: #ffffff;
            }

            QTableWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }

            QTableWidget::item:hover {
                background-color: #3c3c3c;
            }

            QHeaderView::section {
                background-color: #3c3c3c;
                color: #b0b0b0;
                padding: 6px;
                border: none;
                border-bottom: 2px solid #555555;
                font-weight: bold;
                font-size: 12px;
            }

            QHeaderView::section:hover {
                background-color: #404040;
            }

            QCheckBox {
                spacing: 8px;
                color: #ffffff;
            }

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #555555;
                border-radius: 3px;
                background-color: #3c3c3c;
            }

            QCheckBox::indicator:hover {
                border-color: #0078d4;
                background-color: #404040;
            }

            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
                image: url(none);
            }

            QCheckBox::indicator:checked:after {
                content: "✓";
                color: white;
            }

            QPushButton {
                padding: 8px 16px;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                color: #ffffff;
                font-size: 13px;
                min-height: 28px;
            }

            QPushButton:hover {
                background-color: #404040;
                border-color: #666666;
            }

            QPushButton:pressed {
                background-color: #353535;
            }

            QPushButton:disabled {
                background-color: #2b2b2b;
                color: #666666;
                border-color: #444444;
            }

            QPushButton#primaryButton {
                background-color: #0078d4;
                border: none;
                color: #ffffff;
                font-weight: bold;
            }

            QPushButton#primaryButton:hover {
                background-color: #1084d8;
            }

            QPushButton#primaryButton:pressed {
                background-color: #006cbe;
            }

            QPushButton#primaryButton:disabled {
                background-color: #3c3c3c;
                color: #666666;
            }
        """)
