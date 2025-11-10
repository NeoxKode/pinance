# Sprint 12: US-008 Multi-Currency Setup - Task Assignments & Developer Plan

**Sprint:** Sprint 12
**Story:** US-008 - Multi-Currency Account Setup
**Duration:** 2 days (8 hours total)
**Created:** November 10, 2025
**Status:** 🟢 READY FOR ASSIGNMENT

---

## 📊 Task Summary by Role

| Role | Tasks | Hours | Complexity | Dependencies |
|------|-------|-------|------------|--------------|
| **Backend Developer** | 9 tasks | 4.5h | Low-Medium | Database foundation |
| **Frontend Developer** | 5 tasks | 2.5h | Low | Backend API complete |
| **Tech Lead** | 4 tasks | 1h | Low | Review & validation |

**Total:** 18 tasks, 8 hours

---

## 🎯 Critical Path Analysis

### Day 1 (5 hours)
**Focus:** Backend Foundation + Frontend Start
1. Backend: CurrencyValidator + Repository (2.5h)
2. Backend: Service Layer (1.5h)
3. Frontend: AccountDialog Currency Dropdown (1h)

### Day 2 (3 hours)
**Focus:** UI Completion + Testing + Review
1. Frontend: Currency Display (1h)
2. Backend: Transfer Validation (0.5h)
3. Testing + Review (1.5h)

---

## 👨‍💻 Backend Developer Tasks (9 tasks, 4.5 hours)

### Phase 1: Currency Validation (Day 1 AM - 1.5 hours)

#### Task B1.1: Create CurrencyValidator Class ⭐ CRITICAL
**Assigned:** Backend Developer
**Estimate:** 1 hour
**Dependencies:** None (can start immediately)
**Priority:** P0 (MUST complete Day 1)
**Files:** `finance_app/business/validators.py`

**Implementation:**
```python
class CurrencyValidator:
    """Validator for ISO 4217 currency codes."""

    # Full currency database (50+ currencies)
    SUPPORTED_CURRENCIES = {
        # Major Currencies
        'USD': {'name': 'US Dollar', 'symbol': '$', 'decimals': 2, 'locale': 'en_US'},
        'EUR': {'name': 'Euro', 'symbol': '€', 'decimals': 2, 'locale': 'de_DE'},
        'GBP': {'name': 'British Pound', 'symbol': '£', 'decimals': 2, 'locale': 'en_GB'},
        'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'decimals': 0, 'locale': 'ja_JP'},
        'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'decimals': 2, 'locale': 'zh_CN'},
        'CAD': {'name': 'Canadian Dollar', 'symbol': '$', 'decimals': 2, 'locale': 'en_CA'},
        'AUD': {'name': 'Australian Dollar', 'symbol': '$', 'decimals': 2, 'locale': 'en_AU'},
        'CHF': {'name': 'Swiss Franc', 'symbol': 'Fr', 'decimals': 2, 'locale': 'de_CH'},
        'SEK': {'name': 'Swedish Krona', 'symbol': 'kr', 'decimals': 2, 'locale': 'sv_SE'},
        'NZD': {'name': 'New Zealand Dollar', 'symbol': '$', 'decimals': 2, 'locale': 'en_NZ'},

        # Asian Currencies
        'INR': {'name': 'Indian Rupee', 'symbol': '₹', 'decimals': 2, 'locale': 'en_IN'},
        'KRW': {'name': 'South Korean Won', 'symbol': '₩', 'decimals': 0, 'locale': 'ko_KR'},
        'SGD': {'name': 'Singapore Dollar', 'symbol': '$', 'decimals': 2, 'locale': 'en_SG'},
        'HKD': {'name': 'Hong Kong Dollar', 'symbol': '$', 'decimals': 2, 'locale': 'zh_HK'},
        'THB': {'name': 'Thai Baht', 'symbol': '฿', 'decimals': 2, 'locale': 'th_TH'},
        'IDR': {'name': 'Indonesian Rupiah', 'symbol': 'Rp', 'decimals': 0, 'locale': 'id_ID'},
        'MYR': {'name': 'Malaysian Ringgit', 'symbol': 'RM', 'decimals': 2, 'locale': 'ms_MY'},
        'PHP': {'name': 'Philippine Peso', 'symbol': '₱', 'decimals': 2, 'locale': 'en_PH'},

        # European Currencies
        'NOK': {'name': 'Norwegian Krone', 'symbol': 'kr', 'decimals': 2, 'locale': 'no_NO'},
        'DKK': {'name': 'Danish Krone', 'symbol': 'kr', 'decimals': 2, 'locale': 'da_DK'},
        'PLN': {'name': 'Polish Zloty', 'symbol': 'zł', 'decimals': 2, 'locale': 'pl_PL'},
        'HUF': {'name': 'Hungarian Forint', 'symbol': 'Ft', 'decimals': 0, 'locale': 'hu_HU'},
        'CZK': {'name': 'Czech Koruna', 'symbol': 'Kč', 'decimals': 2, 'locale': 'cs_CZ'},
        'RON': {'name': 'Romanian Leu', 'symbol': 'lei', 'decimals': 2, 'locale': 'ro_RO'},

        # Americas
        'BRL': {'name': 'Brazilian Real', 'symbol': 'R$', 'decimals': 2, 'locale': 'pt_BR'},
        'MXN': {'name': 'Mexican Peso', 'symbol': '$', 'decimals': 2, 'locale': 'es_MX'},
        'CLP': {'name': 'Chilean Peso', 'symbol': '$', 'decimals': 0, 'locale': 'es_CL'},
        'COP': {'name': 'Colombian Peso', 'symbol': '$', 'decimals': 0, 'locale': 'es_CO'},
        'ARS': {'name': 'Argentine Peso', 'symbol': '$', 'decimals': 2, 'locale': 'es_AR'},

        # Middle East & Africa
        'ZAR': {'name': 'South African Rand', 'symbol': 'R', 'decimals': 2, 'locale': 'en_ZA'},
        'AED': {'name': 'UAE Dirham', 'symbol': 'د.إ', 'decimals': 2, 'locale': 'ar_AE'},
        'SAR': {'name': 'Saudi Riyal', 'symbol': 'ر.س', 'decimals': 2, 'locale': 'ar_SA'},
        'ILS': {'name': 'Israeli Shekel', 'symbol': '₪', 'decimals': 2, 'locale': 'he_IL'},
        'TRY': {'name': 'Turkish Lira', 'symbol': '₺', 'decimals': 2, 'locale': 'tr_TR'},
        'EGP': {'name': 'Egyptian Pound', 'symbol': 'E£', 'decimals': 2, 'locale': 'ar_EG'},

        # Oceania & Others
        'NZD': {'name': 'New Zealand Dollar', 'symbol': '$', 'decimals': 2, 'locale': 'en_NZ'},
        'RUB': {'name': 'Russian Ruble', 'symbol': '₽', 'decimals': 2, 'locale': 'ru_RU'},
        'VND': {'name': 'Vietnamese Dong', 'symbol': '₫', 'decimals': 0, 'locale': 'vi_VN'},
        'TWD': {'name': 'Taiwan Dollar', 'symbol': 'NT$', 'decimals': 0, 'locale': 'zh_TW'},
    }

    @classmethod
    def validate_currency(cls, currency: str) -> str:
        """
        Validate currency code.

        Args:
            currency: ISO 4217 currency code (e.g., 'USD', 'EUR')

        Returns:
            Validated currency code (uppercase)

        Raises:
            ValidationError: If currency is invalid
        """
        if not currency:
            return 'USD'  # Default to USD

        currency = currency.upper().strip()

        # Length check
        if len(currency) != 3:
            raise ValidationError(
                "Currency code must be 3 letters (ISO 4217 standard)"
            )

        # Alphabetic check
        if not currency.isalpha():
            raise ValidationError(
                "Currency code must contain only letters"
            )

        # Supported check
        if currency not in cls.SUPPORTED_CURRENCIES:
            supported_list = ', '.join(sorted(cls.SUPPORTED_CURRENCIES.keys())[:10])
            raise ValidationError(
                f"Currency '{currency}' not supported. "
                f"Supported currencies include: {supported_list}... "
                f"(total: {len(cls.SUPPORTED_CURRENCIES)} currencies)"
            )

        return currency

    @classmethod
    def get_currency_symbol(cls, currency: str) -> str:
        """Get currency symbol for display."""
        currency_info = cls.SUPPORTED_CURRENCIES.get(currency, {})
        return currency_info.get('symbol', currency)

    @classmethod
    def get_decimal_places(cls, currency: str) -> int:
        """Get decimal places for currency (0 for JPY, KRW; 2 for USD, EUR)."""
        currency_info = cls.SUPPORTED_CURRENCIES.get(currency, {})
        return currency_info.get('decimals', 2)

    @classmethod
    def get_currency_name(cls, currency: str) -> str:
        """Get full currency name."""
        currency_info = cls.SUPPORTED_CURRENCIES.get(currency, {})
        return currency_info.get('name', currency)

    @classmethod
    def format_amount(cls, amount: Decimal, currency: str) -> str:
        """
        Format amount with currency symbol.

        Args:
            amount: Decimal amount
            currency: Currency code

        Returns:
            Formatted string (e.g., "$1,234.56", "¥1,235")
        """
        symbol = cls.get_currency_symbol(currency)
        decimals = cls.get_decimal_places(currency)

        # Round to correct decimal places
        if decimals == 0:
            amount = amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            return f"{symbol}{amount:,.0f}"
        else:
            return f"{symbol}{amount:,.{decimals}f}"

    @classmethod
    def get_all_currencies(cls) -> List[Dict[str, str]]:
        """
        Get list of all supported currencies for dropdown.

        Returns:
            List of dicts with keys: code, name, symbol
        """
        currencies = []
        for code, info in sorted(cls.SUPPORTED_CURRENCIES.items()):
            currencies.append({
                'code': code,
                'name': info['name'],
                'symbol': info['symbol'],
                'display': f"{code} - {info['symbol']} ({info['name']})"
            })
        return currencies
```

**Acceptance Criteria:**
- [ ] CurrencyValidator class created in validators.py
- [ ] 40+ currencies defined in SUPPORTED_CURRENCIES
- [ ] validate_currency() method with length, alpha, supported checks
- [ ] get_currency_symbol() returns correct symbols (€, £, ¥, etc.)
- [ ] get_decimal_places() returns 0 for JPY/KRW, 2 for others
- [ ] format_amount() formats with correct decimals and symbol
- [ ] get_all_currencies() returns list for dropdown population

**Testing:**
```python
def test_currency_validator():
    # Valid currencies
    assert CurrencyValidator.validate_currency('USD') == 'USD'
    assert CurrencyValidator.validate_currency('usd') == 'USD'  # Case insensitive
    assert CurrencyValidator.validate_currency('EUR') == 'EUR'

    # Invalid currencies
    with pytest.raises(ValidationError, match="3 letters"):
        CurrencyValidator.validate_currency('US')

    with pytest.raises(ValidationError, match="not supported"):
        CurrencyValidator.validate_currency('XXX')

    # Formatting
    assert CurrencyValidator.format_amount(Decimal('1234.56'), 'USD') == '$1,234.56'
    assert CurrencyValidator.format_amount(Decimal('1234.56'), 'JPY') == '¥1,235'
    assert CurrencyValidator.format_amount(Decimal('1234.56'), 'EUR') == '€1,234.56'
```

---

#### Task B1.2: Update Account Model with Currency Property
**Assigned:** Backend Developer
**Estimate:** 30 minutes
**Dependencies:** Task B1.1 (CurrencyValidator)
**Priority:** P0 (MUST complete Day 1)
**Files:** `finance_app/data/models.py`

**Implementation:**
```python
@dataclass
class Account:
    # ... existing fields ...

    # US-008: Currency field (already exists from US-001, just activate)
    currency: str = 'USD'  # ISO 4217 code

    # ... existing properties ...

    @property
    def currency_symbol(self) -> str:
        """Get currency symbol for display."""
        from finance_app.business.validators import CurrencyValidator
        return CurrencyValidator.get_currency_symbol(self.currency)

    @property
    def decimal_places(self) -> int:
        """Get decimal places for currency."""
        from finance_app.business.validators import CurrencyValidator
        return CurrencyValidator.get_decimal_places(self.currency)

    def format_balance(self) -> str:
        """Format balance with currency symbol."""
        from finance_app.business.validators import CurrencyValidator
        return CurrencyValidator.format_amount(self.balance, self.currency)
```

**Acceptance Criteria:**
- [ ] Account model has currency field (str, default 'USD')
- [ ] currency_symbol property added
- [ ] decimal_places property added
- [ ] format_balance() method added
- [ ] Docstrings updated

---

### Phase 2: Service Layer (Day 1 PM - 1.5 hours)

#### Task B2.1: Add Currency Validation to AccountService
**Assigned:** Backend Developer
**Estimate:** 45 minutes
**Dependencies:** Task B1.1 (CurrencyValidator)
**Priority:** P0 (blocks frontend)
**Files:** `finance_app/business/account_service.py`

**Implementation:**
```python
class AccountService:
    """Account service with currency validation."""

    def create_account(
        self,
        name: str,
        account_type: AccountType,
        account_subtype: AccountSubtype,
        currency: str = 'USD',  # NEW parameter
        ...
    ) -> Account:
        """Create account with currency validation."""
        # Validate currency (AC1)
        currency = CurrencyValidator.validate_currency(currency)

        # ... existing validation ...

        account = Account(
            name=name,
            account_type=account_type,
            account_subtype=account_subtype,
            currency=currency,  # Set validated currency
            ...
        )

        return self.account_repo.create(account)

    def update_currency(
        self,
        account_id: int,
        new_currency: str
    ) -> Account:
        """
        Update account currency (with warning).

        Args:
            account_id: Account to update
            new_currency: New currency code

        Returns:
            Updated account

        Raises:
            ValidationError: If currency invalid or account has transactions
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account {account_id} not found")

        # Validate new currency
        new_currency = CurrencyValidator.validate_currency(new_currency)

        # Warning: Check if account has transactions
        # (Changing currency on accounts with transactions can cause issues)
        transaction_count = self.transaction_repo.count_by_account(account_id)
        if transaction_count > 0:
            raise ValidationError(
                f"Cannot change currency on account with {transaction_count} transactions. "
                f"This would invalidate existing transaction amounts."
            )

        # Update currency
        account.currency = new_currency
        return self.account_repo.update(account)

    def get_supported_currencies(self) -> List[Dict[str, str]]:
        """Get list of supported currencies for UI dropdown."""
        return CurrencyValidator.get_all_currencies()
```

**Acceptance Criteria:**
- [ ] create_account() accepts currency parameter
- [ ] Currency validated via CurrencyValidator.validate_currency()
- [ ] update_currency() method added
- [ ] update_currency() blocks if account has transactions
- [ ] get_supported_currencies() returns list for dropdown
- [ ] Error messages are clear and actionable

---

#### Task B2.2: Add Transfer Currency Validation
**Assigned:** Backend Developer
**Estimate:** 45 minutes
**Dependencies:** Task B2.1 (AccountService)
**Priority:** P0 (AC3 requirement)
**Files:** `finance_app/business/double_entry_service.py`

**Implementation:**
```python
class DoubleEntryService:
    """Double-entry service with currency validation."""

    def create_transfer(
        self,
        from_account_id: int,
        to_account_id: int,
        amount: Decimal,
        date: str,
        description: str = "Transfer"
    ) -> TransactionGroup:
        """
        Create transfer between accounts (AC3: validate same currency).

        Raises:
            ValidationError: If accounts have different currencies
        """
        # Get accounts
        from_account = self.account_repo.get_by_id(from_account_id)
        to_account = self.account_repo.get_by_id(to_account_id)

        if not from_account or not to_account:
            raise NotFoundError("One or both accounts not found")

        # AC3: Validate same currency
        if from_account.currency != to_account.currency:
            raise ValidationError(
                f"Cannot transfer between accounts with different currencies: "
                f"{from_account.currency} → {to_account.currency}. "
                f"\n\nTo transfer between different currencies, you need to:\n"
                f"1. Use a currency exchange service (future feature), or\n"
                f"2. Manually record as separate transactions in each account"
            )

        # Proceed with transfer (existing logic)
        # ... create journal entries ...

        return transaction_group
```

**Acceptance Criteria:**
- [ ] create_transfer() validates currencies match
- [ ] Error message explains why transfer blocked (AC3)
- [ ] Error message suggests alternatives
- [ ] Same-currency transfers work without issues
- [ ] Unit tests cover currency mismatch scenario

---

### Phase 3: Testing (Day 2 AM - 1.5 hours)

#### Task B3.1: Write Unit Tests for CurrencyValidator
**Assigned:** Backend Developer
**Estimate:** 45 minutes
**Dependencies:** Task B1.1 (CurrencyValidator)
**Priority:** P0 (must have tests)
**Files:** `finance_app/tests/unit/test_currency_validator.py` (NEW)

**Test Coverage (15+ tests):**
- `test_validate_currency_valid_codes()` - USD, EUR, GBP, JPY
- `test_validate_currency_case_insensitive()` - 'usd' → 'USD'
- `test_validate_currency_invalid_length()` - 'US', 'USDD'
- `test_validate_currency_non_alpha()` - 'U$D', '123'
- `test_validate_currency_unsupported()` - 'XXX', 'ZZZ'
- `test_get_currency_symbol()` - $, €, £, ¥
- `test_get_decimal_places()` - 0 for JPY, 2 for USD
- `test_format_amount_usd()` - $1,234.56
- `test_format_amount_jpy()` - ¥1,235 (no decimals)
- `test_format_amount_eur()` - €1,234.56
- `test_get_all_currencies()` - Returns 40+ currencies
- `test_currency_symbols_unique()` - Verify no duplicates
- `test_currency_codes_iso_4217()` - All codes are 3 letters

**Acceptance:**
- [ ] 15+ unit tests written
- [ ] All tests passing
- [ ] 95%+ coverage of CurrencyValidator

---

#### Task B3.2: Write Integration Tests for Currency Validation
**Assigned:** Backend Developer
**Estimate:** 45 minutes
**Dependencies:** Task B2.2 (Transfer validation)
**Priority:** P0 (must have tests)
**Files:** `finance_app/tests/integration/test_currency_integration.py` (NEW)

**Test Scenarios (8+ tests):**
- `test_create_account_with_currency()` - Create USD, EUR, JPY accounts
- `test_create_account_defaults_to_usd()` - No currency specified
- `test_update_currency_on_empty_account()` - Allowed
- `test_update_currency_with_transactions()` - Blocked
- `test_transfer_same_currency()` - USD → USD (success)
- `test_transfer_different_currency()` - USD → EUR (error)
- `test_balance_display_with_currency()` - Format correctly
- `test_supported_currencies_list()` - 40+ currencies available

**Acceptance:**
- [ ] 8+ integration tests written
- [ ] All tests passing
- [ ] End-to-end workflows validated

---

## 🎨 Frontend Developer Tasks (5 tasks, 2.5 hours)

### Phase 4: UI Implementation (Day 1-2 - 2.5 hours)

#### Task F4.1: Add Currency Dropdown to AccountDialog ⭐ HIGH PRIORITY
**Assigned:** Frontend Developer
**Estimate:** 1 hour
**Dependencies:** Task B2.1 (get_supported_currencies service method)
**Priority:** P0 (AC1 core feature)
**Files:** `finance_app/ui/dialogs/account_dialog.py`

**Implementation:**
```python
class AccountDialog(QDialog):
    """Account dialog with currency selection."""

    def setup_ui(self):
        layout = QFormLayout()

        # ... existing fields ...

        # US-008: Currency Dropdown (AC1)
        self.currency_combo = QComboBox()
        self.currency_combo.setEditable(False)
        self._populate_currencies()
        layout.addRow("Currency:", self.currency_combo)

    def _populate_currencies(self):
        """Load supported currencies from service."""
        currencies = self.account_service.get_supported_currencies()

        # Populate dropdown
        for currency in currencies:
            # Display: "USD - $ (US Dollar)"
            display_text = currency['display']
            currency_code = currency['code']

            self.currency_combo.addItem(display_text, currency_code)

        # Set default to USD
        usd_index = self.currency_combo.findData('USD')
        if usd_index >= 0:
            self.currency_combo.setCurrentIndex(usd_index)

    def set_account(self, account: Account):
        """Populate form with existing account data."""
        # ... existing fields ...

        # Set currency
        currency_index = self.currency_combo.findData(account.currency)
        if currency_index >= 0:
            self.currency_combo.setCurrentIndex(currency_index)

    def get_account_data(self) -> dict:
        """Collect form data."""
        data = {
            "name": self.name_edit.text().strip(),
            # ... existing fields ...
            "currency": self.currency_combo.currentData(),  # Get currency code
        }
        return data
```

**UI Layout:**
```
[Account Name      ] (existing)
[Account Type  ▼]   (existing)
[Currency      ▼]   (NEW - US-008)
  └─ "USD - $ (US Dollar)"
  └─ "EUR - € (Euro)"
  └─ "GBP - £ (British Pound)"
  └─ "JPY - ¥ (Japanese Yen)"
  └─ ... (40+ more)
[Color Picker      ] (existing US-009)
[Parent Account ▼] (existing US-006)
...
```

**Acceptance Criteria:**
- [ ] Currency dropdown added to AccountDialog
- [ ] Dropdown shows "CODE - SYMBOL (Name)" format
- [ ] 40+ currencies available
- [ ] Defaults to USD for new accounts
- [ ] Loads existing currency when editing
- [ ] Currency saved correctly via account_service

---

#### Task F4.2: Display Currency Symbol in Account Tree
**Assigned:** Frontend Developer
**Estimate:** 45 minutes
**Dependencies:** Task B1.2 (Account.format_balance method)
**Priority:** P0 (AC2 core feature)
**Files:** `finance_app/ui/widgets/account_tree_widget.py`

**Implementation:**
```python
class AccountTreeWidget(QTreeWidget):
    """Account tree with currency-aware balance display."""

    def _populate_tree_item(self, item: QTreeWidgetItem, account: Account):
        """Populate tree item with account data."""
        # Column 0: Favorite (existing)
        # Column 1: Account name (existing)
        item.setText(1, account.name)

        # Column 2: Type (existing)

        # Column 3: Balance with currency symbol (AC2)
        balance_formatted = account.format_balance()  # "$1,234.56", "¥1,235"
        item.setText(3, balance_formatted)
        item.setToolTip(3, f"{account.currency} balance")

        # Right-align balance for better readability
        item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
```

**Acceptance Criteria:**
- [ ] Balance column shows currency symbol (AC2)
- [ ] USD shows $1,234.56
- [ ] EUR shows €1,234.56
- [ ] JPY shows ¥1,235 (no decimals)
- [ ] Tooltip shows currency code
- [ ] Right-aligned for readability

---

#### Task F4.3: Add Currency Warning to Transfer Dialog
**Assigned:** Frontend Developer
**Estimate:** 30 minutes
**Dependencies:** Task B2.2 (Transfer validation)
**Priority:** P1 (AC3 error handling)
**Files:** `finance_app/ui/dialogs/transfer_dialog.py`

**Implementation:**
```python
class TransferDialog(QDialog):
    """Transfer dialog with currency validation."""

    def validate_transfer(self) -> bool:
        """Validate transfer before submission."""
        # Get selected accounts
        from_account_id = self.from_account_combo.currentData()
        to_account_id = self.to_account_combo.currentData()

        from_account = self.account_repo.get_by_id(from_account_id)
        to_account = self.account_repo.get_by_id(to_account_id)

        # AC3: Check currency mismatch
        if from_account.currency != to_account.currency:
            QMessageBox.warning(
                self,
                "Currency Mismatch",
                f"Cannot transfer between accounts with different currencies:\n\n"
                f"From: {from_account.name} ({from_account.currency})\n"
                f"To: {to_account.name} ({to_account.currency})\n\n"
                f"To transfer between different currencies:\n"
                f"• Use a currency exchange service (future feature), or\n"
                f"• Manually record as separate transactions in each account"
            )
            return False

        return True

    def accept(self):
        """Submit transfer after validation."""
        if not self.validate_transfer():
            return  # Block transfer

        # Proceed with transfer (existing logic)
        super().accept()
```

**Acceptance Criteria:**
- [ ] Transfer dialog checks currency before submit
- [ ] Error dialog shows clear message (AC3)
- [ ] Error explains why transfer blocked
- [ ] Error suggests alternatives
- [ ] Same-currency transfers work without warning

---

#### Task F4.4: Display Currency in Account Details View
**Assigned:** Frontend Developer
**Estimate:** 15 minutes
**Dependencies:** Task F4.2 (Balance display)
**Priority:** P2 (nice to have)
**Files:** `finance_app/ui/main_window.py` or account details panel

**Implementation:**
```python
def show_account_details(self, account: Account):
    """Show account details with currency."""
    details_html = f"""
    <h3>{account.name}</h3>
    <table>
        <tr><td><b>Type:</b></td><td>{account.account_type}</td></tr>
        <tr><td><b>Currency:</b></td><td>{account.currency} ({account.currency_symbol})</td></tr>
        <tr><td><b>Balance:</b></td><td>{account.format_balance()}</td></tr>
        <tr><td><b>Account Number:</b></td><td>{account.account_number or 'N/A'}</td></tr>
        ...
    </table>
    """
    self.details_text.setHtml(details_html)
```

**Acceptance Criteria:**
- [ ] Account details show currency code and symbol
- [ ] Balance formatted with currency
- [ ] Clear and readable layout

---

## 🔧 Tech Lead Tasks (4 tasks, 1 hour)

### Phase 5: Code Review & Validation (Day 2 PM - 1 hour)

#### Task TL5.1: Code Review Backend (Critical)
**Assigned:** Tech Lead
**Estimate:** 20 minutes
**Dependencies:** All backend tasks complete
**Priority:** P0 (quality gate)
**Files:** All backend files

**Review Checklist:**
- [ ] CurrencyValidator has 40+ currencies
- [ ] Currency validation in create_account() and update_currency()
- [ ] Transfer validation blocks currency mismatches (AC3)
- [ ] Error messages are clear and helpful
- [ ] 15+ unit tests passing
- [ ] 8+ integration tests passing
- [ ] No hardcoded currency assumptions (e.g., "$" symbol)

---

#### Task TL5.2: Code Review Frontend (Critical)
**Assigned:** Tech Lead
**Estimate:** 20 minutes
**Dependencies:** All frontend tasks complete
**Priority:** P0 (quality gate)
**Files:** All UI files

**Review Checklist:**
- [ ] Currency dropdown shows CODE - SYMBOL (Name) format
- [ ] 40+ currencies available in dropdown
- [ ] Balance displays with correct currency symbol (AC2)
- [ ] JPY/KRW show 0 decimals
- [ ] Transfer dialog blocks currency mismatches (AC3)
- [ ] Error messages match backend wording

---

#### Task TL5.3: Manual Testing - Edge Cases
**Assigned:** Tech Lead
**Estimate:** 15 minutes
**Dependencies:** Task TL5.1, TL5.2
**Priority:** P0 (catch edge cases)
**Files:** N/A (manual testing)

**Test Scenarios:**
1. **Create accounts in different currencies** - USD, EUR, JPY
2. **Transfer same currency** - USD → USD (should work)
3. **Transfer different currency** - USD → EUR (should block)
4. **Display JPY balance** - Verify 0 decimals (¥1,235 not ¥1,234.56)
5. **Change currency on empty account** - Should work
6. **Change currency with transactions** - Should block

**Acceptance:** All edge cases handled gracefully

---

#### Task TL5.4: Documentation Update
**Assigned:** Tech Lead
**Estimate:** 5 minutes
**Dependencies:** Task TL5.3
**Priority:** P1 (nice to have)
**Files:** `docs/USER_GUIDE.md`, `docs/ARCHITECTURE.md`

**Updates:**
- Add "Currency Support" section to USER_GUIDE.md
- Document 40+ supported currencies
- Explain transfer currency validation
- Update ARCHITECTURE.md with CurrencyValidator

---

## 📅 Sprint Schedule (2 Days, 8 Hours)

### Day 1: Backend + Frontend Start (5 hours)

| Time | Task | Assigned | Duration | Status |
|------|------|----------|----------|--------|
| **AM** | | | | |
| 9:00 | Sprint Planning Meeting | All | 30m | 📋 |
| 9:30 | Task B1.1: CurrencyValidator | Backend | 1h | ⏳ |
| 10:30 | Task B1.2: Account Model | Backend | 30m | ⏳ |
| 11:00 | Task B2.1: AccountService | Backend | 45m | ⏳ |
| 11:45 | Daily Standup | All | 15m | 📋 |
| **PM** | | | | |
| 13:00 | Task B2.2: Transfer Validation | Backend | 45m | ⏳ |
| 13:45 | Task F4.1: Currency Dropdown | Frontend | 1h | ⏳ |
| 14:45 | Buffer / Integration | Both | 1h | - |
| 15:45 | Daily Standup | All | 15m | 📋 |

**Deliverables:** Backend complete ✅, Frontend 50% complete

---

### Day 2: Testing + Review (3 hours)

| Time | Task | Assigned | Duration | Status |
|------|------|----------|----------|--------|
| **AM** | | | | |
| 9:00 | Daily Standup | All | 15m | 📋 |
| 9:15 | Task F4.2: Currency Display | Frontend | 45m | ⏳ |
| 10:00 | Task F4.3: Transfer Warning | Frontend | 30m | ⏳ |
| 10:30 | Task B3.1: Unit Tests | Backend | 45m | ⏳ |
| 11:15 | Task B3.2: Integration Tests | Backend | 45m | ⏳ |
| **PM** | | | | |
| 13:00 | Task TL5.1: Backend Review | Tech Lead | 20m | ⏳ |
| 13:20 | Task TL5.2: Frontend Review | Tech Lead | 20m | ⏳ |
| 13:40 | Task TL5.3: Manual Testing | Tech Lead | 15m | ⏳ |
| 13:55 | Bug Fixes (if needed) | All | 30m | ⏳ |
| 14:25 | Task TL5.4: Documentation | Tech Lead | 5m | ⏳ |
| 14:30 | Sprint Demo | All | 30m | 📋 |

**Deliverables:** All tasks complete ✅, tested, demoed

---

## 🔄 Dependencies & Blockers

### Critical Dependencies

**Backend → Frontend:**
- Frontend CANNOT start Currency Dropdown (Task F4.1) until Backend completes get_supported_currencies() (Task B2.1)
- Frontend CANNOT test Transfer Warning (Task F4.3) until Backend completes Transfer Validation (Task B2.2)

**Solution:** Backend works Day 1 AM+PM, Frontend starts Day 1 PM

---

## ⚠️ Risk Mitigation

### High-Risk Tasks

| Task | Risk | Mitigation |
|------|------|------------|
| **B1.1: CurrencyValidator** | Missing currencies | Start with 10 major, add 30+ more incrementally |
| **F4.2: Currency Display** | JPY/KRW decimal issues | Test early with format_amount() method |
| **B2.2: Transfer Validation** | Edge cases (multi-leg) | Focus on simple transfers, defer complex scenarios |

### De-Scope Options (if time runs short)

1. **Currency change validation** - Can allow changes even with transactions (with warning)
2. **Currency in account details** - Can defer to Sprint 13
3. **Documentation** - Can be follow-up PR

---

## ✅ Definition of Done (Checklist)

### Backend (9 tasks)
- [ ] CurrencyValidator with 40+ currencies
- [ ] Account model currency_symbol, decimal_places properties
- [ ] AccountService currency validation
- [ ] AccountService update_currency() method
- [ ] Transfer currency validation (AC3)
- [ ] 15+ unit tests passing
- [ ] 8+ integration tests passing
- [ ] Code review passed
- [ ] No regressions

### Frontend (5 tasks)
- [ ] Currency dropdown in AccountDialog (AC1)
- [ ] Balance displays with currency symbol (AC2)
- [ ] Transfer dialog blocks currency mismatches (AC3)
- [ ] JPY/KRW show 0 decimals
- [ ] Manual testing complete

### Quality (All)
- [ ] All 4 ACs demonstrated working
- [ ] Zero critical bugs
- [ ] 23+ tests passing (15 unit + 8 integration)
- [ ] Code quality 5/5
- [ ] Sprint demo completed

---

## 🎯 Success Metrics

**Development:**
- [ ] 18 tasks completed
- [ ] 8 hours actual ≈ 8 hours estimated (100% accuracy)
- [ ] All 4 ACs complete
- [ ] 23+ tests passing

**Quality:**
- [ ] Zero critical issues
- [ ] Currency symbols display correctly 100% of time
- [ ] Transfer validation works 100% of time
- [ ] Tech lead approved

**Business:**
- [ ] Users can create accounts in 40+ currencies
- [ ] Zero accidental cross-currency transfers
- [ ] Clear error messages
- [ ] Ready for beta testing

---

## 📚 Reference Documentation

**Backend Developers:**
- ISO 4217 currency codes standard
- Python Decimal formatting
- US-001 Account model

**Frontend Developers:**
- QComboBox documentation (currency dropdown)
- Qt number formatting
- US-007 AccountDialog patterns

**Tech Lead:**
- US-008 full story (all 4 ACs)
- Sprint 11 tech review (quality standards)

---

**Sprint 12 Task Assignments Complete!** ✅
**Ready for sprint planning meeting and developer assignments.** 🚀

---

*Task Assignment Document v1.0*
*Created: November 10, 2025*
*Sprint: Sprint 12*
*Story: US-008 - Multi-Currency Account Setup*
