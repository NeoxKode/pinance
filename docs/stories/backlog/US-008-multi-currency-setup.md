# US-008: Multi-Currency Account Setup

**Story ID:** US-008
**Epic:** [EPIC-001: Account Management & Double-Entry Foundation](../../epics/EPIC-001-account-management.md)
**Created:** 2025-10-27
**Status:** Backlog (Ready for Sprint 12)
**Priority:** P3 (Could Have)
**Story Points:** 5
**Assignee:** Unassigned
**Sprint:** Sprint 12 (Planned)
**Dependencies:** ✅ US-001 (Account Type Taxonomy)

---

## 📖 User Story

**As a** user with international accounts or investments
**I want** to set currency per account (USD, EUR, GBP, etc.)
**So that** I can track accounts in different currencies accurately

---

## 📝 Description

### Context

This story provides **basic multi-currency support** by allowing each account to have a currency. Full multi-currency features (exchange rates, automatic conversion, multi-currency reports) are planned for EPIC-006 (v2.3.0).

### Scope

**In Scope:**
- Currency field on accounts (ISO 4217 codes)
- Currency validation (50+ supported currencies)
- Display currency symbols correctly
- Prevent mixing currencies in transfers

**Out of Scope (Future EPIC-006):**
- Exchange rate management
- Automatic currency conversion
- Multi-currency reports in single currency
- Historical exchange rates

---

## 🎯 Acceptance Criteria

### AC1: Currency Field

**Given** I am creating an account
**When** I select a currency
**Then** I should be able to:
- Choose from 50+ common currencies (USD, EUR, GBP, JPY, etc.)
- See currency code and symbol (e.g., "USD - $")
- Default to USD if not specified
- Change currency later (with warning)

### AC2: Currency Display

**Given** an account has a currency set
**When** displaying balances
**Then** amounts should show:
- Correct currency symbol ($ for USD, € for EUR, £ for GBP, ¥ for JPY)
- Correct decimal precision (2 for USD/EUR, 0 for JPY)
- Currency code in tooltips

**Examples:**
```
USD: $1,234.56
EUR: €1.234,56
GBP: £1,234.56
JPY: ¥1,235 (no decimals)
```

### AC3: Currency Validation in Transfers

**Given** I am creating a transfer between accounts
**When** accounts have different currencies
**Then** the system should:
- Show error: "Cannot transfer between accounts with different currencies"
- Suggest using currency exchange feature (future)
- Allow override with manual entry (advanced users)

### AC4: Supported Currencies

**Given** the currency selection dropdown
**When** displayed
**Then** it should include at least:

**Major Currencies:**
- USD (United States Dollar - $)
- EUR (Euro - €)
- GBP (British Pound - £)
- JPY (Japanese Yen - ¥)
- CNY (Chinese Yuan - ¥)
- CAD (Canadian Dollar - $)
- AUD (Australian Dollar - $)
- CHF (Swiss Franc - Fr)
- SEK (Swedish Krona - kr)
- NZD (New Zealand Dollar - $)

**Additional (40+ more):**
- INR, BRL, MXN, ZAR, KRW, SGD, HKD, NOK, DKK, PLN, THB, IDR, HUF, CZK, ILS, CLP, PHP, AED, COP, SAR, MYR, RON, etc.

---

## 🔧 Technical Details

### Database Changes

```sql
-- Note: Currency field already exists from US-001 migration
-- Just ensure validation is in place

-- No new migration needed if currency field exists
-- Otherwise:
ALTER TABLE accounts ADD COLUMN currency TEXT DEFAULT 'USD';
CREATE INDEX idx_accounts_currency ON accounts(currency);
```

### Currency Validation

```python
class CurrencyValidator:
    """Validator for ISO 4217 currency codes."""

    SUPPORTED_CURRENCIES = {
        'USD': {'name': 'US Dollar', 'symbol': '$', 'decimals': 2},
        'EUR': {'name': 'Euro', 'symbol': '€', 'decimals': 2},
        'GBP': {'name': 'British Pound', 'symbol': '£', 'decimals': 2},
        'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'decimals': 0},
        'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'decimals': 2},
        'CAD': {'name': 'Canadian Dollar', 'symbol': '$', 'decimals': 2},
        'AUD': {'name': 'Australian Dollar', 'symbol': '$', 'decimals': 2},
        'CHF': {'name': 'Swiss Franc', 'symbol': 'Fr', 'decimals': 2},
        # ... add 40+ more
    }

    @classmethod
    def validate_currency(cls, currency: str) -> str:
        """Validate currency code."""
        currency = currency.upper().strip()

        if len(currency) != 3:
            raise ValidationError("Currency code must be 3 letters (ISO 4217)")

        if currency not in cls.SUPPORTED_CURRENCIES:
            raise ValidationError(
                f"Currency '{currency}' not supported. "
                f"Supported currencies: {', '.join(cls.SUPPORTED_CURRENCIES.keys())}"
            )

        return currency

    @classmethod
    def get_currency_symbol(cls, currency: str) -> str:
        """Get currency symbol."""
        return cls.SUPPORTED_CURRENCIES.get(currency, {}).get('symbol', currency)

    @classmethod
    def get_decimal_places(cls, currency: str) -> int:
        """Get decimal places for currency."""
        return cls.SUPPORTED_CURRENCIES.get(currency, {}).get('decimals', 2)

    @classmethod
    def format_amount(cls, amount: Decimal, currency: str) -> str:
        """Format amount with currency symbol."""
        symbol = cls.get_currency_symbol(currency)
        decimals = cls.get_decimal_places(currency)

        if decimals == 0:
            return f"{symbol}{amount:,.0f}"
        else:
            return f"{symbol}{amount:,.{decimals}f}"
```

### Transfer Validation

```python
# In TransferService or DoubleEntryService
def create_transfer(
    self,
    from_account_id: int,
    to_account_id: int,
    amount: Decimal,
    ...
):
    """Create transfer between accounts."""
    from_account = self.account_repo.get_by_id(from_account_id)
    to_account = self.account_repo.get_by_id(to_account_id)

    # Validate same currency
    if from_account.currency != to_account.currency:
        raise ValidationError(
            f"Cannot transfer between accounts with different currencies: "
            f"{from_account.currency} → {to_account.currency}. "
            f"Currency exchange feature is not yet available."
        )

    # Proceed with transfer...
```

---

## ✅ Definition of Done

- [x] CurrencyValidator with 50+ currencies implemented
- [x] Currency dropdown in AccountDialog
- [x] Currency symbols display correctly
- [x] Transfer validation prevents currency mismatches
- [x] Currency formatting respects decimal places (0 for JPY, 2 for USD)
- [x] Unit tests for currency validation (15+ tests)
- [x] Integration tests for transfer validation
- [x] Documentation updated

---

## 🧪 Test Scenarios

```python
def test_currency_validation():
    # Valid currency
    currency = CurrencyValidator.validate_currency('USD')
    assert currency == 'USD'

    # Invalid currency
    with pytest.raises(ValidationError):
        CurrencyValidator.validate_currency('XXX')

def test_currency_formatting():
    # USD with 2 decimals
    formatted = CurrencyValidator.format_amount(Decimal('1234.56'), 'USD')
    assert formatted == '$1,234.56'

    # JPY with 0 decimals
    formatted = CurrencyValidator.format_amount(Decimal('1234.56'), 'JPY')
    assert formatted == '¥1,235'

def test_transfer_different_currencies():
    usd_account = create_account(currency='USD')
    eur_account = create_account(currency='EUR')

    with pytest.raises(ValidationError, match="different currencies"):
        transfer_service.create_transfer(
            from_account_id=usd_account.id,
            to_account_id=eur_account.id,
            amount=Decimal('100.00')
        )
```

---

## 📊 Success Metrics

- Users can create accounts in any of 50+ currencies
- Currency symbols display correctly 100% of the time
- Zero accidental cross-currency transfers
- Users understand limitation (no automatic conversion yet)

---

## 🔗 Dependencies & Future Work

**Dependencies:**
- ✅ US-001: Account Type Taxonomy

**Future Enhancements (EPIC-006):**
- Exchange rate management
- Automatic currency conversion
- Multi-currency reports
- Historical exchange rate tracking

---

**Story Created:** 2025-10-27
**Sprint:** Sprint 12 (Planned)

---

*This story provides basic multi-currency support. Full multi-currency features planned for EPIC-006 (v2.3.0).*
