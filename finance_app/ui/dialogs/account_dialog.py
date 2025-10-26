"""
Account dialog for creating and editing accounts with double-entry support.

Implements US-001: Account Type Taxonomy & Hierarchy
Implements US-005: Opening Balance Equity (frontend)
"""
from decimal import Decimal, InvalidOperation
import decimal
from typing import Optional
from datetime import date

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox, QDateEdit, QCheckBox
)
from PySide6.QtCore import Qt, QDate

from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
from finance_app.business.account_service import AccountService
from finance_app.business.validators import AccountValidator
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import ValidationError

logger = setup_logger(__name__)


class AccountDialog(QDialog):
    """
    Dialog for creating and editing accounts.

    Features:
    - Account type selection (Asset, Liability, Equity, Income, Expense)
    - Dynamic subtype dropdown (filtered by selected type)
    - Automatic normal balance assignment
    - Input validation
    - User-friendly labels and help text
    """

    # Account type display names and descriptions
    ACCOUNT_TYPE_INFO = {
        AccountType.ASSET: {
            'display': '💰 Asset',
            'description': 'Things you own (checking, savings, cash, investments)',
            'icon': '💰'
        },
        AccountType.LIABILITY: {
            'display': '💳 Liability',
            'description': 'Money you owe (credit cards, loans, mortgages)',
            'icon': '💳'
        },
        AccountType.EQUITY: {
            'display': '📊 Equity',
            'description': 'Your net worth (opening balance, retained earnings)',
            'icon': '📊'
        },
        AccountType.INCOME: {
            'display': '💵 Income',
            'description': 'Money you receive (salary, business income, interest)',
            'icon': '💵'
        },
        AccountType.EXPENSE: {
            'display': '💸 Expense',
            'description': 'Money you spend (tied to categories)',
            'icon': '💸'
        }
    }

    # Account subtype display names
    ACCOUNT_SUBTYPE_INFO = {
        AccountSubtype.CHECKING: {'display': 'Checking Account', 'icon': '🏦'},
        AccountSubtype.SAVINGS: {'display': 'Savings Account', 'icon': '🏦'},
        AccountSubtype.CASH: {'display': 'Cash', 'icon': '💵'},
        AccountSubtype.INVESTMENT: {'display': 'Investment Account', 'icon': '📈'},
        AccountSubtype.OTHER_ASSET: {'display': 'Other Asset', 'icon': '💰'},

        AccountSubtype.CREDIT_CARD: {'display': 'Credit Card', 'icon': '💳'},
        AccountSubtype.LOAN: {'display': 'Loan', 'icon': '💳'},
        AccountSubtype.MORTGAGE: {'display': 'Mortgage', 'icon': '🏠'},
        AccountSubtype.LINE_OF_CREDIT: {'display': 'Line of Credit', 'icon': '💳'},
        AccountSubtype.OTHER_LIABILITY: {'display': 'Other Liability', 'icon': '💳'},

        AccountSubtype.OPENING_BALANCE: {'display': 'Opening Balance Equity', 'icon': '📊'},
        AccountSubtype.RETAINED_EARNINGS: {'display': 'Retained Earnings', 'icon': '📊'},

        AccountSubtype.SALARY: {'display': 'Salary/Wages', 'icon': '💵'},
        AccountSubtype.BUSINESS_INCOME: {'display': 'Business Income', 'icon': '💼'},
        AccountSubtype.INTEREST: {'display': 'Interest Income', 'icon': '💰'},
        AccountSubtype.DIVIDENDS: {'display': 'Dividends', 'icon': '📈'},
        AccountSubtype.OTHER_INCOME: {'display': 'Other Income', 'icon': '💵'},

        AccountSubtype.EXPENSE_CATEGORY: {'display': 'Expense Category', 'icon': '💸'},
    }

    def __init__(self, account_service: AccountService, account: Optional[Account] = None, parent=None):
        """
        Initialize account dialog.

        Args:
            account_service: Account service instance
            account: Existing account to edit (None for new account)
            parent: Parent widget
        """
        super().__init__(parent)
        self.account_service = account_service
        self.validator = AccountValidator()
        self.account = account
        self.is_edit_mode = account is not None

        self.setup_ui()
        self.apply_styling()

        if self.is_edit_mode:
            self.populate_fields()

    def setup_ui(self) -> None:
        """Create the dialog UI."""
        title = "Edit Account" if self.is_edit_mode else "Add New Account"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Form layout - clean and simple like Transaction dialog
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        # Account name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter account name (e.g., 'Chase Checking')")
        form.addRow("Account Name:", self.name_edit)

        # Account type
        self.type_combo = QComboBox()
        for account_type in AccountType:
            info = self.ACCOUNT_TYPE_INFO[account_type]
            self.type_combo.addItem(info['display'], account_type)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        form.addRow("Account Type:", self.type_combo)

        # Account subtype (will be populated based on type)
        self.subtype_combo = QComboBox()
        form.addRow("Account Subtype:", self.subtype_combo)

        # US-006: Parent account selection
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("(None - Top Level)", None)
        form.addRow("Parent Account:", self.parent_combo)

        # US-006: Make this a parent account checkbox
        self.is_parent_checkbox = QCheckBox("Make this a parent account")
        self.is_parent_checkbox.setToolTip(
            "Parent accounts are used for grouping other accounts.\n"
            "They cannot have direct transactions and their balance\n"
            "is calculated from their child accounts."
        )
        form.addRow("", self.is_parent_checkbox)

        # Initial balance (legacy field - still shown for backwards compatibility)
        self.balance_edit = QLineEdit()
        self.balance_edit.setPlaceholderText("0.00")
        self.balance_edit.setText("0.00")
        self.balance_edit.setToolTip("Legacy field - not recommended. Use Opening Balance instead for proper accounting.")
        form.addRow("Initial Balance (legacy):", self.balance_edit)

        # US-005: Opening Balance Section
        opening_balance_label = QLabel("<b>Opening Balance (Recommended)</b>")
        opening_balance_label.setStyleSheet("margin-top: 10px;")
        layout.addWidget(opening_balance_label)

        opening_help = QLabel(
            "Use this for proper double-entry accounting when migrating from another system. "
            "This creates journal entries and maintains the accounting equation."
        )
        opening_help.setWordWrap(True)
        opening_help.setStyleSheet("color: #888888; font-size: 11px; margin-bottom: 5px;")
        layout.addWidget(opening_help)

        # Opening balance checkbox
        self.use_opening_balance_checkbox = QCheckBox("Set opening balance for this account")
        self.use_opening_balance_checkbox.stateChanged.connect(self._on_opening_balance_toggle)
        form.addRow("", self.use_opening_balance_checkbox)

        # Opening balance amount
        self.opening_balance_edit = QLineEdit()
        self.opening_balance_edit.setPlaceholderText("Enter opening balance (e.g., 1000.00)")
        self.opening_balance_edit.setEnabled(False)
        form.addRow("Opening Balance:", self.opening_balance_edit)

        # Opening balance date
        self.opening_date_edit = QDateEdit()
        self.opening_date_edit.setDate(QDate.currentDate())
        self.opening_date_edit.setCalendarPopup(True)
        self.opening_date_edit.setDisplayFormat("MMM dd, yyyy")
        self.opening_date_edit.setEnabled(False)
        form.addRow("Opening Date:", self.opening_date_edit)

        # Currency (hidden for now since it's disabled)
        self.currency_edit = QLineEdit()
        self.currency_edit.setText("USD")
        self.currency_edit.setMaxLength(3)
        self.currency_edit.setVisible(False)  # Hide instead of disable

        layout.addLayout(form)

        # Buttons - same layout as Transaction dialog
        button_layout = QHBoxLayout()

        save_text = "Save" if self.is_edit_mode else "Save"
        self.save_btn = QPushButton(save_text)
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self._on_save)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Initialize subtype dropdown with first type
        self._on_type_changed(0)

        # Set focus to name field
        self.name_edit.setFocus()

    def apply_styling(self) -> None:
        """Apply QSS styling to the dialog - matching Transaction dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }

            QLabel {
                color: #ffffff;
                font-size: 13px;
            }

            QLineEdit, QComboBox, QDateEdit {
                padding: 6px;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                color: #ffffff;
                font-size: 13px;
                min-height: 24px;
            }

            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #0078d4;
                background-color: #404040;
            }

            QLineEdit:disabled, QComboBox:disabled, QDateEdit:disabled {
                background-color: #2b2b2b;
                border-color: #3a3a3a;
                color: #666666;
            }

            QLineEdit::placeholder {
                color: #888888;
            }

            QCheckBox {
                color: #ffffff;
                spacing: 5px;
            }

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #3c3c3c;
            }

            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
            }

            QCheckBox::indicator:hover {
                border-color: #0078d4;
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

            QDateEdit:disabled::down-arrow {
                border-top-color: #666666;
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
        """)

    def _on_type_changed(self, index: int) -> None:
        """
        Handle account type change - update subtype dropdown and parent account dropdown.

        Args:
            index: Selected index in type combo box
        """
        account_type = self.type_combo.currentData()

        # Get valid subtypes for this account type
        valid_subtypes = self.validator.VALID_SUBTYPES.get(account_type, [])

        # Clear and repopulate subtype combo
        self.subtype_combo.clear()
        for subtype in valid_subtypes:
            info = self.ACCOUNT_SUBTYPE_INFO[subtype]
            display = f"{info['icon']} {info['display']}"
            self.subtype_combo.addItem(display, subtype)

        # US-006: Populate parent account dropdown with compatible parent accounts
        self._populate_parent_accounts(account_type)

    def _populate_parent_accounts(self, account_type: AccountType) -> None:
        """
        Populate parent account dropdown with compatible parent accounts.
        US-006: Only show parent accounts of the same type.

        Args:
            account_type: The selected account type
        """
        # Clear and add default option
        self.parent_combo.clear()
        self.parent_combo.addItem("(None - Top Level)", None)

        try:
            # Get all accounts
            all_accounts = self.account_service.get_all_accounts()

            # Filter to parent accounts of matching type
            parent_accounts = [
                acc for acc in all_accounts
                if acc.is_parent and acc.account_type == account_type
            ]

            # Exclude current account if editing (can't be parent of self)
            if self.is_edit_mode and self.account:
                parent_accounts = [acc for acc in parent_accounts if acc.id != self.account.id]

            # Add to dropdown
            for parent_acc in parent_accounts:
                self.parent_combo.addItem(f"📁 {parent_acc.name}", parent_acc.id)

            logger.debug(f"Populated {len(parent_accounts)} parent accounts for type {account_type}")

        except Exception as e:
            logger.warning(f"Failed to load parent accounts: {e}")

    def _on_opening_balance_toggle(self, state: int) -> None:
        """
        Handle opening balance checkbox toggle.

        Args:
            state: Checkbox state (Qt.CheckState.Checked or Qt.CheckState.Unchecked)
        """
        # In PySide6, state is Qt.CheckState enum, value 2 = Checked
        is_checked = (state == Qt.CheckState.Checked) or (state == 2)

        self.opening_balance_edit.setEnabled(is_checked)
        self.opening_date_edit.setEnabled(is_checked)

        # If enabled, set focus to opening balance field
        if is_checked:
            self.opening_balance_edit.setFocus()
            if not self.opening_balance_edit.text():
                self.opening_balance_edit.setText("0.00")

    def populate_fields(self) -> None:
        """Populate fields when editing an existing account."""
        if not self.account:
            return

        self.name_edit.setText(self.account.name)

        # Set account type
        type_index = self.type_combo.findData(self.account.account_type)
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)

        # Set account subtype (after type is set to populate subtypes)
        subtype_index = self.subtype_combo.findData(self.account.account_subtype)
        if subtype_index >= 0:
            self.subtype_combo.setCurrentIndex(subtype_index)

        # US-006: Set parent account
        if self.account.parent_account_id:
            parent_index = self.parent_combo.findData(self.account.parent_account_id)
            if parent_index >= 0:
                self.parent_combo.setCurrentIndex(parent_index)

        # US-006: Set is_parent checkbox
        self.is_parent_checkbox.setChecked(self.account.is_parent)

        self.balance_edit.setText(f"{self.account.balance:.2f}")
        self.currency_edit.setText(self.account.currency)

    def _on_save(self) -> None:
        """Validate and save the account."""
        try:
            # Get values
            name = self.name_edit.text().strip()
            account_type = self.type_combo.currentData()
            account_subtype = self.subtype_combo.currentData()
            initial_balance = self.balance_edit.text().strip()
            currency = self.currency_edit.text().strip()

            # US-005: Opening balance fields
            use_opening_balance = self.use_opening_balance_checkbox.isChecked()
            opening_balance_str = self.opening_balance_edit.text().strip() if use_opening_balance else None
            opening_date = self.opening_date_edit.date().toString("yyyy-MM-dd") if use_opening_balance else None

            # US-006: Parent account and is_parent fields
            parent_account_id = self.parent_combo.currentData()
            is_parent = self.is_parent_checkbox.isChecked()

            # Validate required fields
            if not name:
                QMessageBox.warning(self, "Validation Error", "Account name is required")
                self.name_edit.setFocus()
                return

            if not account_type or not account_subtype:
                QMessageBox.warning(self, "Validation Error", "Please select account type and subtype")
                return

            # US-006: Validate parent account rules
            if is_parent and parent_account_id:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "An account cannot be a parent account and also have a parent.\n"
                    "Please uncheck 'Make this a parent account' or select '(None - Top Level)' as parent."
                )
                return

            if is_parent and use_opening_balance:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Parent accounts cannot have opening balances.\n"
                    "Their balance is calculated from child accounts.\n"
                    "Please uncheck 'Make this a parent account' or disable opening balance."
                )
                return

            # Validate opening balance if checkbox is checked
            if use_opening_balance:
                if not opening_balance_str:
                    QMessageBox.warning(self, "Validation Error", "Opening balance amount is required")
                    self.opening_balance_edit.setFocus()
                    return

                try:
                    opening_balance = Decimal(opening_balance_str)
                    if opening_balance < 0:
                        QMessageBox.warning(self, "Validation Error", "Opening balance cannot be negative")
                        self.opening_balance_edit.setFocus()
                        return
                except (ValueError, decimal.InvalidOperation):
                    QMessageBox.warning(self, "Validation Error", "Please enter a valid opening balance amount")
                    self.opening_balance_edit.setFocus()
                    return

            # Create or update account
            if self.is_edit_mode:
                # Update existing account
                # US-006: Include parent_account_id in update
                self.account_service.update_account(
                    account_id=self.account.id,
                    name=name,
                    account_type=account_type,
                    account_subtype=account_subtype,
                    currency=currency,
                    parent_account_id=parent_account_id
                )
                logger.info(f"Account updated: {name}")
                QMessageBox.information(self, "Success", f"Account '{name}' updated successfully")
            else:
                # US-005: Create account with or without opening balance
                if use_opening_balance and opening_balance_str:
                    # Create account with opening balance (US-005)
                    opening_balance = Decimal(opening_balance_str)
                    # US-006: Include parent_account_id and is_parent
                    account, journal_entry = self.account_service.create_account_with_opening_balance(
                        name=name,
                        account_type=account_type,
                        account_subtype=account_subtype,
                        opening_balance=opening_balance,
                        opening_date=opening_date,
                        currency=currency,
                        parent_account_id=parent_account_id,
                        is_parent=is_parent
                    )
                    logger.info(f"Account created with opening balance: {name}, balance={opening_balance}, date={opening_date}")
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Account '{name}' created successfully with opening balance of ${opening_balance:.2f}"
                    )
                else:
                    # Create account without opening balance (original flow)
                    # US-006: Include parent_account_id and is_parent
                    self.account_service.create_account(
                        name=name,
                        account_type=account_type,
                        account_subtype=account_subtype,
                        initial_balance=initial_balance,
                        currency=currency,
                        parent_account_id=parent_account_id,
                        is_parent=is_parent
                    )
                    logger.info(f"Account created: {name}")
                    QMessageBox.information(self, "Success", f"Account '{name}' created successfully")

            self.accept()

        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception as e:
            logger.error(f"Error saving account: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save account: {e}")

    def get_account_data(self) -> Optional[dict]:
        """
        Get account data from dialog (if accepted).

        Returns:
            Dictionary with account data, or None if cancelled
        """
        if self.result() == QDialog.Accepted:
            return {
                'name': self.name_edit.text().strip(),
                'account_type': self.type_combo.currentData(),
                'account_subtype': self.subtype_combo.currentData(),
                'initial_balance': self.balance_edit.text().strip(),
                'currency': self.currency_edit.text().strip()
            }
        return None
