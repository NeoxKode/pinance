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
    QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox, QDateEdit, QCheckBox,
    QPlainTextEdit, QCompleter
)
from PySide6.QtCore import Qt, QDate, QStringListModel

from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
from finance_app.business.account_service import AccountService
from finance_app.business.validators import AccountValidator
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import ValidationError
# US-009: Color picker widget and color utilities
from finance_app.ui.widgets.color_picker_widget import ColorPickerWidget
from finance_app.ui.styles import get_default_color_for_account_type

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

        # US-008: Currency dropdown with search/filter
        self.currency_combo = QComboBox()
        self.currency_combo.setEditable(True)  # Enables search/filter
        self.currency_combo.setInsertPolicy(QComboBox.NoInsert)  # Prevent adding new items
        self.currency_combo.currentIndexChanged.connect(self._on_currency_changed)
        self._populate_currencies()
        form.addRow("Currency:", self.currency_combo)

        # US-009: Account color picker
        self.color_picker = ColorPickerWidget()
        self.color_picker.color_changed.connect(self._on_color_changed)
        form.addRow("Account Color:", self.color_picker)

        # US-007: Account metadata fields
        # Account number
        self.account_number_edit = QLineEdit()
        self.account_number_edit.setPlaceholderText("e.g., 1234-5678 or ****1234")
        self.account_number_edit.setMaxLength(50)
        self.account_number_edit.setToolTip("Optional: Bank account number for reconciliation (3-50 characters)")
        form.addRow("Account Number:", self.account_number_edit)

        # Institution name with autocomplete
        self.institution_edit = QLineEdit()
        self.institution_edit.setPlaceholderText("e.g., Chase Bank, Wells Fargo")
        self.institution_edit.setMaxLength(100)
        self.institution_edit.setToolTip("Optional: Financial institution name")

        # Setup autocomplete for institution
        self.institution_completer = QCompleter()
        self.institution_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.institution_completer.setFilterMode(Qt.MatchContains)
        self.institution_edit.setCompleter(self.institution_completer)

        # Load institution autocomplete data
        self._load_institution_autocomplete()

        form.addRow("Institution Name:", self.institution_edit)

        # Notes (multi-line)
        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setPlaceholderText("Add notes about this account (optional, max 1000 characters)")
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setToolTip("Optional: Free-form notes (max 1000 characters)")
        form.addRow("Notes:", self.notes_edit)

        # Favorite checkbox
        self.is_favorite_checkbox = QCheckBox("⭐ Mark as favorite")
        self.is_favorite_checkbox.setToolTip("Favorite accounts appear at the top of the list")
        form.addRow("", self.is_favorite_checkbox)

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

        # US-009: Set default color for account type (only for new accounts)
        if not self.is_edit_mode:
            default_color = get_default_color_for_account_type(account_type)
            self.color_picker.set_color(default_color)

    def _on_color_changed(self, color_hex: str) -> None:
        """
        Handle color picker change.
        US-009: Store selected color for account creation/update.

        Args:
            color_hex: Selected color as hex string
        """
        # Color is stored in the widget, will be retrieved during save
        logger.debug(f"Account color changed to: {color_hex}")

    def _populate_currencies(self) -> None:
        """
        Populate currency dropdown with supported currencies.
        US-008: Popular currencies first, then separator, then all others alphabetically.
        """
        currencies = AccountValidator.SUPPORTED_CURRENCIES

        # Popular currencies first
        popular = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY']
        for code in popular:
            if code in currencies:
                info = currencies[code]
                display = f"{code} - {info['symbol']} ({info['name']})"
                self.currency_combo.addItem(display, code)

        # Add separator
        self.currency_combo.insertSeparator(len(popular))

        # Add all other currencies alphabetically
        other_currencies = sorted([c for c in currencies.keys() if c not in popular])
        for code in other_currencies:
            info = currencies[code]
            display = f"{code} - {info['symbol']} ({info['name']})"
            self.currency_combo.addItem(display, code)

        # Set default to USD
        usd_index = self.currency_combo.findData('USD')
        if usd_index >= 0:
            self.currency_combo.setCurrentIndex(usd_index)

        # Add helpful tooltip
        self.currency_combo.setToolTip(
            "Select account currency (ISO 4217 standard).\n\n"
            "Type to search currencies.\n"
            "Popular currencies are listed first.\n\n"
            "Note: Currency cannot be changed if account has transactions.\n"
            "Zero-decimal currencies (JPY, KRW, CLP, VND) do not allow cents."
        )

        logger.debug(f"Populated {len(currencies)} currencies in dropdown")

    def _on_currency_changed(self, index: int) -> None:
        """
        Handle currency selection change.
        US-008: Validate currency changes for existing accounts.

        Args:
            index: Selected index in currency combo box
        """
        if not self.is_edit_mode:
            return  # No validation needed for new accounts

        if index < 0:
            return  # Invalid index

        # Get new currency
        new_currency = self.currency_combo.currentData()
        if not new_currency:
            return

        # Get old currency
        old_currency = self.account.currency if self.account else 'USD'

        if new_currency == old_currency:
            return  # No change

        # US-008: Check if currency change is allowed
        try:
            # Check transaction count
            trans_count = self.account_service.get_transaction_count(self.account.id)

            if trans_count > 0:
                # Show warning and revert
                QMessageBox.warning(
                    self,
                    "Currency Change Not Allowed",
                    f"Cannot change currency for '{self.account.name}'.\n\n"
                    f"This account has {trans_count} transaction(s).\n"
                    f"Currency changes are only allowed for accounts with no transactions.\n\n"
                    f"To change currency:\n"
                    f"1. Create a new account with the desired currency\n"
                    f"2. Transfer transactions to the new account\n"
                    f"3. Delete this account"
                )
                # Revert to original currency
                old_index = self.currency_combo.findData(old_currency)
                if old_index >= 0:
                    self.currency_combo.blockSignals(True)
                    self.currency_combo.setCurrentIndex(old_index)
                    self.currency_combo.blockSignals(False)
                return

            # Check parent/child currency consistency
            if self.account.parent_account_id:
                parent = self.account_service.get_account(self.account.parent_account_id)
                if parent and parent.currency != new_currency:
                    QMessageBox.warning(
                        self,
                        "Currency Mismatch",
                        f"Cannot change currency to {new_currency}.\n\n"
                        f"This account's parent '{parent.name}' uses {parent.currency}.\n"
                        f"Child accounts must match their parent's currency."
                    )
                    # Revert to original currency
                    old_index = self.currency_combo.findData(old_currency)
                    if old_index >= 0:
                        self.currency_combo.blockSignals(True)
                        self.currency_combo.setCurrentIndex(old_index)
                        self.currency_combo.blockSignals(False)
                    return

            # Check if account has children with different currencies
            if self.account.is_parent:
                children = self.account_service.account_repo.get_child_accounts(self.account.id)
                mismatched = [c for c in children if c.currency != new_currency]
                if mismatched:
                    names = ', '.join([c.name for c in mismatched[:3]])  # Show first 3
                    if len(mismatched) > 3:
                        names += f", and {len(mismatched) - 3} more"

                    QMessageBox.warning(
                        self,
                        "Currency Mismatch",
                        f"Cannot change currency to {new_currency}.\n\n"
                        f"Child accounts have different currencies: {names}\n\n"
                        f"Change child account currencies first."
                    )
                    # Revert to original currency
                    old_index = self.currency_combo.findData(old_currency)
                    if old_index >= 0:
                        self.currency_combo.blockSignals(True)
                        self.currency_combo.setCurrentIndex(old_index)
                        self.currency_combo.blockSignals(False)
                    return

            # Currency change is valid
            logger.info(f"Currency change allowed: {old_currency} → {new_currency}")

        except Exception as e:
            logger.error(f"Error validating currency change: {e}")
            QMessageBox.warning(
                self,
                "Validation Error",
                f"Could not validate currency change: {e}"
            )
            # Revert to original currency
            old_index = self.currency_combo.findData(old_currency)
            if old_index >= 0:
                self.currency_combo.blockSignals(True)
                self.currency_combo.setCurrentIndex(old_index)
                self.currency_combo.blockSignals(False)

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

    def _load_institution_autocomplete(self) -> None:
        """
        Load institution names for autocomplete.
        US-007: Populate autocomplete with existing institution names.
        """
        try:
            # Get institution autocomplete suggestions from service
            institutions = self.account_service.get_institution_autocomplete("")

            # Create string list model for completer
            model = QStringListModel(institutions)
            self.institution_completer.setModel(model)

            logger.debug(f"Loaded {len(institutions)} institutions for autocomplete")

        except Exception as e:
            logger.warning(f"Failed to load institution autocomplete: {e}")

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

        # US-009: Set account color
        if hasattr(self.account, 'color_hex') and self.account.color_hex:
            self.color_picker.set_color(self.account.color_hex)
        else:
            # Fallback to default color for account type
            default_color = get_default_color_for_account_type(self.account.account_type)
            self.color_picker.set_color(default_color)

        # US-006: Set parent account
        if self.account.parent_account_id:
            parent_index = self.parent_combo.findData(self.account.parent_account_id)
            if parent_index >= 0:
                self.parent_combo.setCurrentIndex(parent_index)

        # US-006: Set is_parent checkbox
        self.is_parent_checkbox.setChecked(self.account.is_parent)

        self.balance_edit.setText(f"{self.account.balance:.2f}")

        # US-008: Set currency in combo box
        currency_index = self.currency_combo.findData(self.account.currency)
        if currency_index >= 0:
            self.currency_combo.setCurrentIndex(currency_index)
        else:
            # Fallback to USD if currency not found
            logger.warning(f"Currency '{self.account.currency}' not found in dropdown, defaulting to USD")
            usd_index = self.currency_combo.findData('USD')
            if usd_index >= 0:
                self.currency_combo.setCurrentIndex(usd_index)

        # US-007: Set metadata fields
        if hasattr(self.account, 'account_number') and self.account.account_number:
            self.account_number_edit.setText(self.account.account_number)

        if hasattr(self.account, 'institution_name') and self.account.institution_name:
            self.institution_edit.setText(self.account.institution_name)

        if hasattr(self.account, 'notes') and self.account.notes:
            self.notes_edit.setPlainText(self.account.notes)

        if hasattr(self.account, 'is_favorite'):
            self.is_favorite_checkbox.setChecked(self.account.is_favorite)

    def _on_save(self) -> None:
        """Validate and save the account."""
        try:
            # Get values
            name = self.name_edit.text().strip()
            account_type = self.type_combo.currentData()
            account_subtype = self.subtype_combo.currentData()
            initial_balance = self.balance_edit.text().strip()
            currency = self.currency_combo.currentData()  # US-008: Get from combo box

            # US-005: Opening balance fields
            use_opening_balance = self.use_opening_balance_checkbox.isChecked()
            opening_balance_str = self.opening_balance_edit.text().strip() if use_opening_balance else None
            opening_date = self.opening_date_edit.date().toString("yyyy-MM-dd") if use_opening_balance else None

            # US-006: Parent account and is_parent fields
            parent_account_id = self.parent_combo.currentData()
            is_parent = self.is_parent_checkbox.isChecked()

            # US-007: Metadata fields
            account_number = self.account_number_edit.text().strip() or None
            institution_name = self.institution_edit.text().strip() or None
            notes = self.notes_edit.toPlainText().strip() or None
            is_favorite = self.is_favorite_checkbox.isChecked()

            # US-007: Validate metadata fields
            if account_number and len(account_number) < 3:
                QMessageBox.warning(self, "Validation Error", "Account number must be at least 3 characters")
                self.account_number_edit.setFocus()
                return

            if institution_name and len(institution_name) > 100:
                QMessageBox.warning(self, "Validation Error", "Institution name cannot exceed 100 characters")
                self.institution_edit.setFocus()
                return

            if notes and len(notes) > 1000:
                QMessageBox.warning(self, "Validation Error", "Notes cannot exceed 1000 characters")
                self.notes_edit.setFocus()
                return

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

            # US-009: Get selected color
            color_hex = self.color_picker.get_color()

            # Create or update account
            if self.is_edit_mode:
                # Update existing account - make separate service calls for different features

                # 1. Update basic account fields
                self.account_service.update_account(
                    account_id=self.account.id,
                    name=name,
                    account_type=account_type,
                    account_subtype=account_subtype,
                    currency=currency
                )

                # 2. US-006: Update parent if changed
                if parent_account_id != self.account.parent_account_id:
                    self.account_service.move_account(
                        account_id=self.account.id,
                        new_parent_id=parent_account_id
                    )

                # 3. US-006: Update is_parent if changed
                if is_parent and not self.account.is_parent:
                    self.account_service.convert_to_parent_account(self.account.id)

                # 4. US-009: Update color if changed
                if color_hex != getattr(self.account, 'color_hex', None):
                    self.account_service.update_color(
                        account_id=self.account.id,
                        color_hex=color_hex
                    )

                # 5. US-007: Update metadata fields
                self.account_service.update_metadata(
                    account_id=self.account.id,
                    account_number=account_number,
                    institution_name=institution_name,
                    notes=notes
                )

                # 6. US-009: Update favorite status if changed
                current_favorite = getattr(self.account, 'is_favorite', False)
                if is_favorite != current_favorite:
                    self.account_service.toggle_favorite(self.account.id)

                logger.info(f"Account updated: {name}, color={color_hex}, metadata fields included")
                QMessageBox.information(self, "Success", f"Account '{name}' updated successfully")
            else:
                # US-005: Create account with or without opening balance
                if use_opening_balance and opening_balance_str:
                    # Create account with opening balance (US-005)
                    opening_balance = Decimal(opening_balance_str)
                    # US-006: Include parent_account_id and is_parent
                    # US-009: Include color_hex
                    created_account, journal_entry = self.account_service.create_account_with_opening_balance(
                        name=name,
                        account_type=account_type,
                        account_subtype=account_subtype,
                        opening_balance=opening_balance,
                        opening_date=opening_date,
                        currency=currency,
                        parent_account_id=parent_account_id,
                        is_parent=is_parent,
                        color_hex=color_hex
                    )
                    logger.info(f"Account created with opening balance: {name}, balance={opening_balance}, date={opening_date}, color={color_hex}")
                else:
                    # Create account without opening balance (original flow)
                    # US-006: Include parent_account_id and is_parent
                    # US-009: Include color_hex
                    created_account = self.account_service.create_account(
                        name=name,
                        account_type=account_type,
                        account_subtype=account_subtype,
                        initial_balance=initial_balance,
                        currency=currency,
                        parent_account_id=parent_account_id,
                        is_parent=is_parent,
                        color_hex=color_hex
                    )
                    logger.info(f"Account created: {name}, color={color_hex}")

                # US-007: Add metadata to newly created account
                if account_number or institution_name or notes:
                    self.account_service.update_metadata(
                        account_id=created_account.id,
                        account_number=account_number,
                        institution_name=institution_name,
                        notes=notes
                    )

                # US-009: Set favorite status if checked
                if is_favorite:
                    self.account_service.toggle_favorite(created_account.id)

                # Show success message
                if use_opening_balance and opening_balance_str:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Account '{name}' created successfully with opening balance of ${opening_balance:.2f}"
                    )
                else:
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
                'currency': self.currency_combo.currentData()  # US-008: Get from combo box
            }
        return None
