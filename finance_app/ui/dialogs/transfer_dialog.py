"""
Dialog for transferring money between accounts.

This dialog allows users to transfer funds from one account to another,
creating balanced journal entries in the double-entry accounting system.

Story: US-002B - Balanced Transaction Groups (Phase 4)
"""
from typing import List, Optional, Dict
from decimal import Decimal, InvalidOperation

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QComboBox, QDateEdit,
    QLineEdit, QPushButton, QLabel, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QDoubleValidator

from finance_app.data.models import Account
from finance_app.data.database import Database
from finance_app.utils.logger import setup_logger

logger = setup_logger(__name__)


class TransferDialog(QDialog):
    """
    Dialog for transferring money between accounts.

    This implements the UI for Phase 4 of US-002B, allowing users to:
    - Select source and destination accounts
    - Enter transfer amount
    - Add optional notes
    - See real-time validation feedback
    """

    def __init__(self, database: Database, accounts: List[Account], parent=None):
        """
        Initialize transfer dialog.

        Args:
            database: Database instance
            accounts: List of available accounts
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = database
        self.accounts = accounts
        self.setup_ui()
        self.apply_styling()

        logger.info("Transfer dialog initialized")

    def setup_ui(self) -> None:
        """Set up user interface with clean, intuitive layout."""
        self.setWindowTitle("Transfer Money")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)

        # Header with icon and description
        header_layout = QVBoxLayout()
        title_label = QLabel("💸 Transfer Money")
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)

        description_label = QLabel(
            "Transfer funds between your accounts. "
            "This creates balanced journal entries automatically."
        )
        description_label.setWordWrap(True)
        description_label.setObjectName("descriptionLabel")
        header_layout.addWidget(description_label)

        main_layout.addLayout(header_layout)

        # Form layout for input fields
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # From Account (Source)
        self.from_account_combo = QComboBox()
        self.from_account_combo.setObjectName("accountCombo")
        for account in self.accounts:
            # Format: "Checking ($1,000.00)"
            balance_str = f"${account.balance:,.2f}"
            subtype = account.account_subtype.value if hasattr(account.account_subtype, 'value') else account.account_subtype
            subtype_display = subtype.replace('_', ' ').title()
            display_text = f"{account.name} ({subtype_display}) - {balance_str}"
            self.from_account_combo.addItem(display_text, account.id)

        self.from_account_combo.currentIndexChanged.connect(self._on_account_changed)
        form.addRow("From Account:*", self.from_account_combo)

        # To Account (Destination)
        self.to_account_combo = QComboBox()
        self.to_account_combo.setObjectName("accountCombo")
        for account in self.accounts:
            balance_str = f"${account.balance:,.2f}"
            subtype = account.account_subtype.value if hasattr(account.account_subtype, 'value') else account.account_subtype
            subtype_display = subtype.replace('_', ' ').title()
            display_text = f"{account.name} ({subtype_display}) - {balance_str}"
            self.to_account_combo.addItem(display_text, account.id)

        # Set different default to avoid same-account selection
        if len(self.accounts) > 1:
            self.to_account_combo.setCurrentIndex(1)

        self.to_account_combo.currentIndexChanged.connect(self._on_account_changed)
        form.addRow("To Account:*", self.to_account_combo)

        # Amount input with validation
        amount_layout = QHBoxLayout()
        amount_layout.setSpacing(4)

        dollar_label = QLabel("$")
        dollar_label.setObjectName("currencyLabel")
        amount_layout.addWidget(dollar_label)

        self.amount_edit = QLineEdit()
        self.amount_edit.setObjectName("amountInput")
        self.amount_edit.setPlaceholderText("0.00")

        # Validator: only positive decimal numbers
        validator = QDoubleValidator(0.01, 999999999.99, 2, self)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.amount_edit.setValidator(validator)
        self.amount_edit.textChanged.connect(self._on_amount_changed)

        amount_layout.addWidget(self.amount_edit)
        amount_layout.addStretch()

        form.addRow("Amount:*", amount_layout)

        # Date picker
        self.date_edit = QDateEdit()
        self.date_edit.setObjectName("dateInput")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("MMMM dd, yyyy")
        form.addRow("Date:", self.date_edit)

        # Description (optional)
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("e.g., Monthly savings transfer")
        self.description_edit.setObjectName("descriptionInput")
        form.addRow("Description:", self.description_edit)

        # Reference number (optional)
        self.reference_edit = QLineEdit()
        self.reference_edit.setPlaceholderText("Optional reference number")
        self.reference_edit.setObjectName("referenceInput")
        form.addRow("Reference:", self.reference_edit)

        # Notes (optional)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Add any additional notes...")
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setObjectName("notesInput")
        form.addRow("Notes:", self.notes_edit)

        main_layout.addLayout(form)

        # Validation feedback label
        self.feedback_label = QLabel()
        self.feedback_label.setObjectName("feedbackLabel")
        self.feedback_label.setWordWrap(True)
        self.feedback_label.hide()  # Hidden until validation error
        main_layout.addWidget(self.feedback_label)

        # Required fields note
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        main_layout.addWidget(note_label)

        # Preview section
        preview_layout = QVBoxLayout()
        preview_label = QLabel("Transfer Preview:")
        preview_label.setObjectName("previewLabel")
        preview_layout.addWidget(preview_label)

        self.preview_text = QLabel("Select accounts and enter amount to see preview")
        self.preview_text.setObjectName("previewText")
        self.preview_text.setWordWrap(True)
        preview_layout.addWidget(self.preview_text)

        main_layout.addLayout(preview_layout)

        # Spacer
        main_layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.transfer_btn = QPushButton("💸 Transfer Money")
        self.transfer_btn.setObjectName("primaryButton")
        self.transfer_btn.setDefault(True)
        self.transfer_btn.clicked.connect(self._on_transfer_clicked)
        self.transfer_btn.setEnabled(False)  # Disabled until valid input
        button_layout.addWidget(self.transfer_btn)

        main_layout.addLayout(button_layout)

        # Set focus to amount field
        self.amount_edit.setFocus()

        # Initial validation
        self._validate_and_update_preview()

    def apply_styling(self) -> None:
        """Apply beautiful QSS styling for modern UI."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }

            QLabel#titleLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1976D2;
                padding: 8px 0;
            }

            QLabel#descriptionLabel {
                color: #666;
                font-size: 13px;
                padding-bottom: 8px;
            }

            QLabel#previewLabel {
                font-weight: bold;
                color: #333;
                padding: 8px 0 4px 0;
            }

            QLabel#previewText {
                background-color: #E3F2FD;
                border-left: 4px solid #2196F3;
                padding: 12px;
                border-radius: 4px;
                color: #333;
            }

            QLabel#currencyLabel {
                font-size: 16px;
                font-weight: bold;
                color: #666;
                padding-right: 4px;
            }

            QLabel#feedbackLabel {
                background-color: #FFEBEE;
                border-left: 4px solid #F44336;
                padding: 8px 12px;
                border-radius: 4px;
                color: #C62828;
            }

            QComboBox#accountCombo,
            QLineEdit#amountInput,
            QLineEdit#descriptionInput,
            QLineEdit#referenceInput,
            QDateEdit#dateInput,
            QTextEdit#notesInput {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
                min-height: 20px;
            }

            QComboBox#accountCombo:focus,
            QLineEdit#amountInput:focus,
            QLineEdit#descriptionInput:focus,
            QLineEdit#referenceInput:focus,
            QDateEdit#dateInput:focus,
            QTextEdit#notesInput:focus {
                border-color: #2196F3;
                background-color: #FAFAFA;
            }

            QLineEdit#amountInput {
                font-size: 16px;
                font-weight: 500;
                min-width: 150px;
            }

            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                min-width: 100px;
            }

            QPushButton#cancelButton {
                background-color: white;
                border: 2px solid #e0e0e0;
                color: #666;
            }

            QPushButton#cancelButton:hover {
                background-color: #f5f5f5;
                border-color: #bdbdbd;
            }

            QPushButton#primaryButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
            }

            QPushButton#primaryButton:hover {
                background-color: #1976D2;
            }

            QPushButton#primaryButton:pressed {
                background-color: #0D47A1;
            }

            QPushButton#primaryButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }

            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }

            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)

    def _on_account_changed(self) -> None:
        """Handle account selection change."""
        self._validate_and_update_preview()

    def _on_amount_changed(self, text: str) -> None:
        """Handle amount input change."""
        self._validate_and_update_preview()

    def _validate_and_update_preview(self) -> None:
        """
        Validate inputs and update preview text.

        This provides immediate feedback to the user about:
        - Same account selection
        - Invalid amount
        - Transfer preview with balances
        """
        # Get current selections
        from_account_id = self.from_account_combo.currentData()
        to_account_id = self.to_account_combo.currentData()
        amount_text = self.amount_edit.text().strip()

        # Reset feedback
        self.feedback_label.hide()
        is_valid = True
        error_message = ""

        # Validate: Different accounts
        if from_account_id == to_account_id:
            is_valid = False
            error_message = "⚠️ Source and destination accounts must be different"
            self.feedback_label.setText(error_message)
            self.feedback_label.show()

        # Validate: Amount
        try:
            if amount_text:
                amount = Decimal(amount_text)
                if amount <= 0:
                    is_valid = False
                    error_message = "⚠️ Amount must be greater than zero"
                    self.feedback_label.setText(error_message)
                    self.feedback_label.show()
            else:
                is_valid = False  # Amount required
        except (InvalidOperation, ValueError):
            is_valid = False
            if amount_text:  # Only show error if user typed something invalid
                error_message = "⚠️ Please enter a valid amount"
                self.feedback_label.setText(error_message)
                self.feedback_label.show()

        # Enable/disable transfer button
        self.transfer_btn.setEnabled(is_valid and bool(amount_text))

        # Update preview
        if is_valid and amount_text:
            self._update_preview(from_account_id, to_account_id, Decimal(amount_text))
        else:
            self.preview_text.setText("Select accounts and enter amount to see preview")

    def _update_preview(self, from_id: int, to_id: int, amount: Decimal) -> None:
        """
        Update transfer preview with account balances.

        Args:
            from_id: Source account ID
            to_id: Destination account ID
            amount: Transfer amount
        """
        from_account = next((a for a in self.accounts if a.id == from_id), None)
        to_account = next((a for a in self.accounts if a.id == to_id), None)

        if not from_account or not to_account:
            return

        # Calculate new balances
        from_new_balance = from_account.balance - amount
        to_new_balance = to_account.balance + amount

        # Format preview text
        preview_html = f"""
        <p><b>Transfer ${amount:,.2f}</b></p>
        <p style='margin-top: 8px;'>
        <b style='color: #F44336;'>From:</b> {from_account.name}<br/>
        Current: ${from_account.balance:,.2f} →
        <b>New: ${from_new_balance:,.2f}</b>
        </p>
        <p style='margin-top: 4px;'>
        <b style='color: #4CAF50;'>To:</b> {to_account.name}<br/>
        Current: ${to_account.balance:,.2f} →
        <b>New: ${to_new_balance:,.2f}</b>
        </p>
        """

        self.preview_text.setText(preview_html)

    def _on_transfer_clicked(self) -> None:
        """Handle transfer button click with final validation."""
        # Final validation before accepting
        from_account_id = self.from_account_combo.currentData()
        to_account_id = self.to_account_combo.currentData()
        amount_text = self.amount_edit.text().strip()

        # Validate accounts
        if from_account_id == to_account_id:
            QMessageBox.warning(
                self,
                "Invalid Transfer",
                "Cannot transfer to the same account.\n\n"
                "Please select different source and destination accounts."
            )
            return

        # Validate amount
        try:
            amount = Decimal(amount_text)
            if amount <= 0:
                QMessageBox.warning(
                    self,
                    "Invalid Amount",
                    "Transfer amount must be greater than zero."
                )
                self.amount_edit.setFocus()
                return
        except (InvalidOperation, ValueError):
            QMessageBox.warning(
                self,
                "Invalid Amount",
                "Please enter a valid amount.\n\n"
                "Example: 500.00"
            )
            self.amount_edit.setFocus()
            return

        # Confirmation dialog with summary
        from_account = next((a for a in self.accounts if a.id == from_account_id), None)
        to_account = next((a for a in self.accounts if a.id == to_account_id), None)

        if not from_account or not to_account:
            QMessageBox.critical(self, "Error", "Selected account not found")
            return

        confirm_msg = (
            f"Transfer ${amount:,.2f} from {from_account.name} to {to_account.name}?\n\n"
            f"{from_account.name}: ${from_account.balance:,.2f} → ${from_account.balance - amount:,.2f}\n"
            f"{to_account.name}: ${to_account.balance:,.2f} → ${to_account.balance + amount:,.2f}"
        )

        reply = QMessageBox.question(
            self,
            "Confirm Transfer",
            confirm_msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            logger.info(f"Transfer confirmed: ${amount} from account {from_account_id} to {to_account_id}")
            self.accept()
        else:
            logger.info("Transfer cancelled by user")

    def get_transfer_data(self) -> Optional[Dict]:
        """
        Get transfer data for backend processing.

        Returns:
            Dictionary with transfer data or None if dialog was cancelled

        Format:
            {
                'from_account_id': int,
                'to_account_id': int,
                'amount': Decimal,
                'date': str (YYYY-MM-DD),
                'description': str,
                'reference_number': Optional[str],
                'notes': Optional[str]
            }
        """
        if self.result() != QDialog.Accepted:
            return None

        try:
            # Get description or generate default
            description = self.description_edit.text().strip()
            if not description:
                from_account = next(
                    (a for a in self.accounts if a.id == self.from_account_combo.currentData()),
                    None
                )
                to_account = next(
                    (a for a in self.accounts if a.id == self.to_account_combo.currentData()),
                    None
                )
                if from_account and to_account:
                    description = f"Transfer from {from_account.name} to {to_account.name}"
                else:
                    description = "Account transfer"

            return {
                'from_account_id': self.from_account_combo.currentData(),
                'to_account_id': self.to_account_combo.currentData(),
                'amount': Decimal(self.amount_edit.text().strip()),
                'date': self.date_edit.date().toString("yyyy-MM-dd"),
                'description': description,
                'reference_number': self.reference_edit.text().strip() or None,
                'notes': self.notes_edit.toPlainText().strip() or None
            }
        except Exception as e:
            logger.error(f"Failed to get transfer data: {e}")
            return None
