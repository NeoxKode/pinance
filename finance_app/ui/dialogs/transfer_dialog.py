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
from finance_app.business.validators import AccountValidator  # US-008: Currency validation
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
        """Set up user interface with clean, intuitive layout inspired by HomeBank."""
        self.setWindowTitle("Transfer Money")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.resize(450, 400)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Form layout for input fields - HomeBank style
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # From Account (Source)
        self.from_account_combo = QComboBox()
        self.from_account_combo.setObjectName("accountCombo")
        self._populate_from_accounts()
        self.from_account_combo.currentIndexChanged.connect(self._on_from_account_changed)
        form.addRow("From Account:*", self.from_account_combo)

        # To Account (Destination) - will be filtered by source currency
        self.to_account_combo = QComboBox()
        self.to_account_combo.setObjectName("accountCombo")
        self.to_account_combo.currentIndexChanged.connect(self._on_account_changed)
        form.addRow("To Account:*", self.to_account_combo)

        # US-008: Currency info label
        self.currency_info_label = QLabel()
        self.currency_info_label.setObjectName("currencyInfoLabel")
        self.currency_info_label.setWordWrap(True)
        self.currency_info_label.hide()  # Hidden until account selected
        form.addRow("", self.currency_info_label)

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

        # Validation feedback label (compact)
        self.feedback_label = QLabel()
        self.feedback_label.setObjectName("feedbackLabel")
        self.feedback_label.setWordWrap(True)
        self.feedback_label.hide()  # Hidden until validation error
        main_layout.addWidget(self.feedback_label)

        # Preview section (compact, HomeBank-inspired)
        self.preview_text = QLabel("Select accounts and enter amount")
        self.preview_text.setObjectName("previewText")
        self.preview_text.setWordWrap(True)
        self.preview_text.setMinimumHeight(60)
        main_layout.addWidget(self.preview_text)

        # Spacer
        main_layout.addStretch()

        # Button layout - HomeBank style
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("cancelButton")
        close_btn.clicked.connect(self.reject)
        close_btn.setMinimumWidth(100)
        button_layout.addWidget(close_btn)

        button_layout.addStretch()

        self.transfer_btn = QPushButton("Transfer")
        self.transfer_btn.setObjectName("primaryButton")
        self.transfer_btn.setDefault(True)
        self.transfer_btn.clicked.connect(self._on_transfer_clicked)
        self.transfer_btn.setEnabled(False)  # Disabled until valid input
        self.transfer_btn.setMinimumWidth(100)
        button_layout.addWidget(self.transfer_btn)

        main_layout.addLayout(button_layout)

        # Set focus to amount field
        self.amount_edit.setFocus()

        # Initial validation
        self._validate_and_update_preview()

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

            QLabel#previewText {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                padding: 8px;
                border-radius: 3px;
                color: #b0b0b0;
                font-size: 12px;
            }

            QLabel#currencyLabel {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                padding-right: 4px;
            }

            QLabel#feedbackLabel {
                background-color: #4a2828;
                border-left: 3px solid #d32f2f;
                padding: 8px 12px;
                border-radius: 3px;
                color: #ff6b6b;
            }

            QLabel#currencyInfoLabel {
                color: #88bbff;
                font-size: 11px;
                padding: 4px;
                font-style: italic;
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

            QPushButton#primaryButton:disabled {
                background-color: #555555;
                border-color: #555555;
                color: #888888;
            }
        """)

    def _populate_from_accounts(self) -> None:
        """
        Populate from account dropdown with all accounts.
        US-008: Show currency in display format.
        """
        self.from_account_combo.clear()
        for account in self.accounts:
            # US-008: Format with currency symbol
            symbol = AccountValidator.get_currency_symbol(account.currency)
            balance_str = AccountValidator.format_amount(account.balance, account.currency)

            subtype = account.account_subtype.value if hasattr(account.account_subtype, 'value') else account.account_subtype
            subtype_display = subtype.replace('_', ' ').title()
            display_text = f"{account.name} ({account.currency}) - {balance_str}"
            self.from_account_combo.addItem(display_text, account.id)

        # Trigger initial population of to_account_combo
        if self.accounts:
            self._populate_to_accounts()

    def _populate_to_accounts(self) -> None:
        """
        Populate to account dropdown filtered by from account currency.
        US-008: Only show accounts with matching currency.
        """
        self.to_account_combo.clear()

        from_account_id = self.from_account_combo.currentData()
        if not from_account_id:
            return

        # Get from account
        from_account = next((a for a in self.accounts if a.id == from_account_id), None)
        if not from_account:
            return

        from_currency = from_account.currency

        # Filter accounts by matching currency (excluding from account)
        compatible_accounts = [
            acc for acc in self.accounts
            if acc.currency == from_currency and acc.id != from_account_id
        ]

        # Populate dropdown
        for account in compatible_accounts:
            symbol = AccountValidator.get_currency_symbol(account.currency)
            balance_str = AccountValidator.format_amount(account.balance, account.currency)

            subtype = account.account_subtype.value if hasattr(account.account_subtype, 'value') else account.account_subtype
            subtype_display = subtype.replace('_', ' ').title()
            display_text = f"{account.name} ({account.currency}) - {balance_str}"
            self.to_account_combo.addItem(display_text, account.id)

        # Update currency info label
        self._update_currency_info(from_currency, len(compatible_accounts))

    def _update_currency_info(self, currency: str, count: int) -> None:
        """
        Update currency compatibility info label.
        US-008: Show how many compatible accounts are available.

        Args:
            currency: Currency code
            count: Number of compatible accounts
        """
        if count == 0:
            self.currency_info_label.setText(
                f"ℹ️ No other accounts with {currency} currency available for transfer"
            )
            self.currency_info_label.setStyleSheet("color: #ffaa66;")  # Warning color
        elif count == 1:
            self.currency_info_label.setText(
                f"ℹ️ Showing 1 account with {currency} currency"
            )
            self.currency_info_label.setStyleSheet("color: #88bbff;")  # Info color
        else:
            self.currency_info_label.setText(
                f"ℹ️ Showing {count} accounts with {currency} currency"
            )
            self.currency_info_label.setStyleSheet("color: #88bbff;")  # Info color

        self.currency_info_label.show()

    def _on_from_account_changed(self, index: int) -> None:
        """
        Handle from account selection change.
        US-008: Re-populate to account list with currency filtering.

        Args:
            index: Selected index
        """
        self._populate_to_accounts()
        self._validate_and_update_preview()

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
        US-008: Use currency-aware formatting.

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

        # US-008: Format with currency symbols
        currency = from_account.currency
        amount_str = AccountValidator.format_amount(amount, currency)
        from_balance_str = AccountValidator.format_amount(from_account.balance, currency)
        from_new_str = AccountValidator.format_amount(from_new_balance, currency)
        to_balance_str = AccountValidator.format_amount(to_account.balance, currency)
        to_new_str = AccountValidator.format_amount(to_new_balance, currency)

        # Format preview text - compact HomeBank style with currency
        preview_text = (
            f"Transfer {amount_str}\n"
            f"From: {from_account.name} ({from_balance_str} → {from_new_str})\n"
            f"To: {to_account.name} ({to_balance_str} → {to_new_str})"
        )

        self.preview_text.setText(preview_text)

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

        # US-008: Format with currency symbols
        currency = from_account.currency
        amount_str = AccountValidator.format_amount(amount, currency)
        from_balance_str = AccountValidator.format_amount(from_account.balance, currency)
        from_new_str = AccountValidator.format_amount(from_account.balance - amount, currency)
        to_balance_str = AccountValidator.format_amount(to_account.balance, currency)
        to_new_str = AccountValidator.format_amount(to_account.balance + amount, currency)

        confirm_msg = (
            f"Transfer {amount_str} from {from_account.name} to {to_account.name}?\n\n"
            f"{from_account.name}: {from_balance_str} → {from_new_str}\n"
            f"{to_account.name}: {to_balance_str} → {to_new_str}"
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
