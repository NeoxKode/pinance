"""
Account dialog for creating and editing accounts with double-entry support.

Implements US-001: Account Type Taxonomy & Hierarchy
"""
from decimal import Decimal
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Qt

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

        # Initial balance
        self.balance_edit = QLineEdit()
        self.balance_edit.setPlaceholderText("0.00")
        self.balance_edit.setText("0.00")
        form.addRow("Initial Balance:", self.balance_edit)

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

            QLineEdit, QComboBox {
                padding: 6px;
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                color: #ffffff;
                font-size: 13px;
                min-height: 24px;
            }

            QLineEdit:focus, QComboBox:focus {
                border-color: #0078d4;
                background-color: #404040;
            }

            QLineEdit::placeholder {
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
        Handle account type change - update subtype dropdown.

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

            # Validate required fields
            if not name:
                QMessageBox.warning(self, "Validation Error", "Account name is required")
                self.name_edit.setFocus()
                return

            if not account_type or not account_subtype:
                QMessageBox.warning(self, "Validation Error", "Please select account type and subtype")
                return

            # Create or update account
            if self.is_edit_mode:
                # Update existing account
                self.account_service.update_account(
                    account_id=self.account.id,
                    name=name,
                    account_type=account_type,
                    account_subtype=account_subtype,
                    currency=currency
                )
                logger.info(f"Account updated: {name}")
                QMessageBox.information(self, "Success", f"Account '{name}' updated successfully")
            else:
                # Create new account
                self.account_service.create_account(
                    name=name,
                    account_type=account_type,
                    account_subtype=account_subtype,
                    initial_balance=initial_balance,
                    currency=currency
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
