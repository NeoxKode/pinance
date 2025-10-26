"""
Set Opening Balance Dialog for existing accounts.

Implements US-005: Opening Balance Equity (frontend)
"""
from decimal import Decimal, InvalidOperation
import decimal
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox, QDateEdit,
    QGroupBox, QTextEdit
)
from PySide6.QtCore import Qt, QDate

from finance_app.data.models import Account, NormalBalance
from finance_app.business.account_service import AccountService
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import ValidationError, NotFoundError

logger = setup_logger(__name__)


class SetOpeningBalanceDialog(QDialog):
    """
    Dialog for setting opening balance on an existing account.

    Features:
    - Set opening balance amount
    - Set opening balance date
    - Validation to prevent setting twice
    - Clear success/error feedback
    - Accounting equation validation
    """

    def __init__(self, account: Account, account_service: AccountService, parent=None):
        """
        Initialize set opening balance dialog.

        Args:
            account: Account to set opening balance for
            account_service: Account service instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.account = account
        self.account_service = account_service

        self.setup_ui()
        self.apply_styling()

    def setup_ui(self) -> None:
        """Create the dialog UI."""
        self.setWindowTitle("Set Opening Balance")
        self.setModal(True)
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel(f"<h3>Set Opening Balance</h3>")
        layout.addWidget(header_label)

        # Account info
        account_info = QLabel(
            f"<b>Account:</b> {self.account.name}<br>"
            f"<b>Type:</b> {self.account.account_type.value.title()}<br>"
            f"<b>Current Balance:</b> ${self.account.balance:.2f}"
        )
        account_info.setStyleSheet("padding: 10px; background-color: #3c3c3c; border-radius: 4px; margin-bottom: 10px;")
        layout.addWidget(account_info)

        # Check if already has opening balance
        if self.account.opening_balance_date:
            warning_label = QLabel(
                f"⚠️ <b>Warning:</b> This account already has an opening balance set on {self.account.opening_balance_date}.<br>"
                "Setting a new opening balance is not allowed."
            )
            warning_label.setStyleSheet("color: #FF9800; padding: 10px; background-color: #3c3c3c; border-radius: 4px;")
            warning_label.setWordWrap(True)
            layout.addWidget(warning_label)

            # Only show Close button
            button_layout = QHBoxLayout()
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.reject)
            button_layout.addStretch()
            button_layout.addWidget(close_btn)
            layout.addLayout(button_layout)
            return

        # Help text
        help_text = QLabel(
            "Set an opening balance for this account if you're migrating from another system. "
            "This will create a journal entry offset by the Opening Balance Equity account."
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #888888; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(help_text)

        # Form layout
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(12)

        # Opening balance amount
        self.opening_balance_edit = QLineEdit()
        self.opening_balance_edit.setPlaceholderText("Enter opening balance (e.g., 1000.00)")
        self.opening_balance_edit.setText("0.00")
        form.addRow("Opening Balance:*", self.opening_balance_edit)

        # Opening balance date
        self.opening_date_edit = QDateEdit()
        self.opening_date_edit.setDate(QDate.currentDate())
        self.opening_date_edit.setCalendarPopup(True)
        self.opening_date_edit.setDisplayFormat("MMM dd, yyyy")
        form.addRow("Opening Date:*", self.opening_date_edit)

        layout.addLayout(form)

        # Required fields note
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: #888888; font-size: 11px; margin-top: 5px;")
        layout.addWidget(note_label)

        # Journal entry preview section
        preview_group = QGroupBox("Journal Entry Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(140)
        self.preview_text.setPlainText("Enter an opening balance to see journal entry preview...")
        preview_layout.addWidget(self.preview_text)

        layout.addWidget(preview_group)

        # Validation info
        validation_info = QLabel(
            "💡 <b>Note:</b> The accounting equation (Assets = Liabilities + Equity) will be validated automatically."
        )
        validation_info.setWordWrap(True)
        validation_info.setStyleSheet("color: #888888; font-size: 11px; margin-top: 10px; margin-bottom: 10px;")
        layout.addWidget(validation_info)

        # Connect signals for live preview
        self.opening_balance_edit.textChanged.connect(self._update_preview)
        self.opening_date_edit.dateChanged.connect(self._update_preview)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Set Opening Balance")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self._on_save)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

        # Set focus to opening balance field
        self.opening_balance_edit.setFocus()
        self.opening_balance_edit.selectAll()

    def apply_styling(self) -> None:
        """Apply QSS styling to match the main theme."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }

            QLabel {
                color: #ffffff;
            }

            QLineEdit, QDateEdit {
                padding: 8px;
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
                min-width: 100px;
            }

            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #666666;
            }

            QPushButton:pressed {
                background-color: #2a2a2a;
            }

            QPushButton:default {
                background-color: #0078d4;
                border-color: #0078d4;
            }

            QPushButton:default:hover {
                background-color: #0086f0;
            }

            QPushButton:default:pressed {
                background-color: #006cc1;
            }

            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }

            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 3px;
                color: #d4d4d4;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 8px;
            }
        """)

    def _update_preview(self) -> None:
        """Update the journal entry preview based on current inputs."""
        try:
            # Parse opening balance
            amount_text = self.opening_balance_edit.text().strip()
            if not amount_text:
                self.preview_text.setPlainText("Enter an opening balance to see journal entry preview...")
                return

            amount = Decimal(amount_text)
            if amount <= 0:
                self.preview_text.setPlainText("⚠️ Opening balance must be greater than zero.")
                return

            # Get opening date
            opening_date = self.opening_date_edit.date().toPython()

            # Determine debit/credit based on account normal balance
            account_debit = Decimal("0.00")
            account_credit = Decimal("0.00")
            equity_debit = Decimal("0.00")
            equity_credit = Decimal("0.00")

            if self.account.normal_balance == NormalBalance.DEBIT:
                # Asset/Expense: Debit account, Credit equity
                account_debit = amount
                equity_credit = amount
            else:
                # Liability/Equity/Income: Credit account, Debit equity
                account_credit = amount
                equity_debit = amount

            # Build preview text
            preview = f"Date: {opening_date.strftime('%B %d, %Y')}\n"
            preview += f"Description: Opening balance for {self.account.name}\n\n"
            preview += "Journal Entries:\n"
            preview += "─" * 50 + "\n"

            if account_debit > 0:
                preview += f"  Debit:  {self.account.name:<30} ${account_debit:>12,.2f}\n"
            else:
                preview += f"  Credit: {self.account.name:<30} ${account_credit:>12,.2f}\n"

            if equity_credit > 0:
                preview += f"  Credit: Opening Balance Equity{' ':<13} ${equity_credit:>12,.2f}\n"
            else:
                preview += f"  Debit:  Opening Balance Equity{' ':<13} ${equity_debit:>12,.2f}\n"

            preview += "─" * 50 + "\n"
            preview += f"  Total:  {' ':<30} ${amount:>12,.2f}\n\n"
            preview += "✓ Journal entries will be balanced (Debits = Credits)"

            self.preview_text.setPlainText(preview)

        except (InvalidOperation, ValueError):
            self.preview_text.setPlainText("⚠️ Please enter a valid numeric amount.")

    def _on_save(self) -> None:
        """Validate and save the opening balance."""
        try:
            # Get values
            opening_balance_str = self.opening_balance_edit.text().strip()
            opening_date = self.opening_date_edit.date().toString("yyyy-MM-dd")

            # Validate opening balance
            if not opening_balance_str:
                QMessageBox.warning(self, "Validation Error", "Opening balance amount is required")
                self.opening_balance_edit.setFocus()
                return

            try:
                opening_balance = Decimal(opening_balance_str)
                if opening_balance < 0:
                    QMessageBox.warning(
                        self,
                        "Validation Error",
                        "Opening balance cannot be negative"
                    )
                    self.opening_balance_edit.setFocus()
                    return
            except (ValueError, InvalidOperation):
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Please enter a valid opening balance amount"
                )
                self.opening_balance_edit.setFocus()
                return

            # Confirm action
            reply = QMessageBox.question(
                self,
                "Confirm Opening Balance",
                f"Set opening balance of ${opening_balance:.2f} for account '{self.account.name}' "
                f"as of {self.opening_date_edit.date().toString('MMM dd, yyyy')}?\n\n"
                "This will create journal entries and cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return

            # Set opening balance via service
            journal_entry = self.account_service.set_account_opening_balance(
                account_id=self.account.id,
                opening_balance=opening_balance,
                opening_date=opening_date
            )

            logger.info(
                f"Opening balance set for account {self.account.name}: "
                f"${opening_balance:.2f} as of {opening_date}"
            )

            # Success message
            QMessageBox.information(
                self,
                "Success",
                f"Opening balance of ${opening_balance:.2f} has been set successfully!\n\n"
                f"Journal entries have been created and the accounting equation has been validated."
            )

            self.accept()

        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            QMessageBox.warning(self, "Validation Error", str(e))
        except NotFoundError as e:
            logger.error(f"Account not found: {e}")
            QMessageBox.critical(self, "Error", str(e))
        except Exception as e:
            logger.error(f"Error setting opening balance: {e}")
            QMessageBox.critical(self, "Error", f"Failed to set opening balance: {e}")
