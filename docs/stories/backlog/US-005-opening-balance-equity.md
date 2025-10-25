# US-005: Opening Balance Equity

**Story ID:** US-005
**Epic:** [EPIC-01: Account Management & Double-Entry Foundation](../../epics/epic-01-account-management.md)
**Created:** 2025-10-25
**Status:** 📋 Backlog (Ready for Sprint 7)
**Priority:** P0 (Critical - Accounting Foundation)
**Story Points:** 5
**Assignee:** Unassigned
**Sprint:** Sprint 7 (planned)
**Dependencies:** ✅ US-001 (Account Type Taxonomy), ✅ US-002A (Journal Entry Foundation), ✅ US-003 (Normal Balance Calculation)

---

## 📖 User Story

**As a** new user migrating from another financial system
**I want** to set opening balances for my accounts when first setting up the application
**So that** I can start tracking from my current financial position without manual journal entries

---

## 📝 Description

### Context

When users first set up a personal finance application, they already have existing accounts with current balances:
- Checking account: $2,500
- Savings account: $10,000
- Credit card: -$850
- Investment account: $25,000

In double-entry accounting, every transaction must be balanced (debits = credits). When creating accounts with initial balances, the system needs a special **Opening Balance Equity** account to balance the equation.

### The Accounting Principle

The fundamental accounting equation:
```
Assets - Liabilities = Equity
```

When a user adds opening balances, the system creates balanced journal entries using Opening Balance Equity as the offsetting account:

**Example 1: Asset Account (Checking) with $2,500 opening balance**
```
Debit:  Checking Account        $2,500  (increases asset)
Credit: Opening Balance Equity  $2,500  (increases equity)
```

**Example 2: Liability Account (Credit Card) with $850 balance**
```
Debit:  Opening Balance Equity  $850    (decreases equity)
Credit: Credit Card             $850    (increases liability)
```

After all opening balances are entered:
- **Assets:** $37,500 (Checking + Savings + Investment)
- **Liabilities:** $850 (Credit Card)
- **Opening Balance Equity:** $36,650 (Assets - Liabilities)
- **✅ Accounting Equation Balanced:** $37,500 - $850 = $36,650

### Problem Statement

**Current Issues**:
1. ❌ No automated Opening Balance Equity account creation
2. ❌ Users must manually create offsetting journal entries (complex, error-prone)
3. ❌ No validation that opening balance entries are balanced
4. ❌ No easy way to set initial account balances
5. ❌ Accounting equation can be unbalanced during setup
6. ❌ No way to track which transactions are opening balance entries

**User Pain Points**:
- "I don't know how to enter my starting balances correctly"
- "The system won't let me create an account without a $0 balance"
- "I manually created journal entries but my books don't balance"
- "I don't understand what 'Opening Balance Equity' means"

**Example Problem**:
```
User creates Checking account with $2,500 balance
- Account shows $2,500 ✅
- But accounting equation is broken: Assets = $2,500, Equity = $0 ❌
- No offsetting entry was created
- Books don't balance
```

### Proposed Solution

Add comprehensive Opening Balance Equity support:

1. **Auto-Create Equity Account**
   - System automatically creates "Opening Balance Equity" account (if not exists)
   - Type: Equity, Subtype: OPENING_BALANCE
   - Hidden from user by default (internal accounting account)

2. **Set Opening Balance Method**
   - New `AccountService.set_opening_balance()` method
   - Creates balanced journal entry automatically
   - Uses correct debit/credit based on account type
   - Validates accounting equation

3. **UI Enhancement**
   - Add "Opening Balance" field to account creation dialog
   - Add "Set Opening Balance" option to existing accounts
   - Display warning if books aren't balanced
   - Show Opening Balance Equity balance for transparency

4. **Opening Balance Transaction Metadata**
   - Mark transactions as opening balance entries
   - Allow filtering/hiding opening balance transactions
   - Include in reconciliation but clearly identified

**Example Solution**:
```python
# User creates checking account with opening balance
account_service.create_account_with_opening_balance(
    name="My Checking",
    account_type=AccountType.ASSET,
    account_subtype=AccountSubtype.CHECKING,
    opening_balance=Decimal("2500.00"),
    opening_date="2025-01-01"
)

# System automatically:
# 1. Creates "Opening Balance Equity" account (if not exists)
# 2. Creates balanced journal entry:
#    - Debit: My Checking $2,500
#    - Credit: Opening Balance Equity $2,500
# 3. Updates both account balances
# 4. Marks transaction as opening balance entry
# 5. Accounting equation remains balanced ✅
```

---

## ✅ Acceptance Criteria

### Functional Requirements

#### AC1: Opening Balance Equity Account Creation
- [ ] **Given** the system starts with no Opening Balance Equity account
      **When** the first account with opening balance is created
      **Then** the system automatically creates an "Opening Balance Equity" account
      **And** the account has type=EQUITY, subtype=OPENING_BALANCE
      **And** the account initial balance is $0.00

- [ ] **Given** an Opening Balance Equity account already exists
      **When** another account with opening balance is created
      **Then** the system reuses the existing Opening Balance Equity account
      **And** does not create a duplicate

- [ ] **Given** the Opening Balance Equity account
      **When** viewed in the UI
      **Then** it should be clearly labeled as a system account
      **And** should show the cumulative balance from all opening entries

#### AC2: Set Opening Balance for New Accounts
- [ ] **Given** I am creating a new asset account (e.g., Checking)
      **When** I specify an opening balance of $2,500
      **Then** a balanced journal entry is created:
      - Debit: Asset Account $2,500
      - Credit: Opening Balance Equity $2,500
      **And** the asset account balance = $2,500
      **And** the Opening Balance Equity balance increases by $2,500

- [ ] **Given** I am creating a new liability account (e.g., Credit Card)
      **When** I specify an opening balance of $850
      **Then** a balanced journal entry is created:
      - Debit: Opening Balance Equity $850
      - Credit: Liability Account $850
      **And** the liability account balance = $850
      **And** the Opening Balance Equity balance decreases by $850

- [ ] **Given** I am creating a new account
      **When** I leave the opening balance blank or $0
      **Then** no Opening Balance Equity entry is created
      **And** the account is created with $0 balance

#### AC3: Set Opening Balance for Existing Accounts
- [ ] **Given** I have an existing account with $0 balance
      **When** I set an opening balance of $1,000 via "Set Opening Balance" action
      **Then** a balanced journal entry is created
      **And** the entry is dated with the opening date I specify
      **And** the account balance updates to $1,000

- [ ] **Given** I have an existing account with existing transactions
      **When** I try to set an opening balance
      **Then** the system should warn me that this will affect historical balances
      **And** require confirmation before proceeding
      **And** the opening balance entry is dated before all existing transactions

#### AC4: Accounting Equation Validation
- [ ] **Given** multiple accounts with opening balances
      **When** all opening balances are entered
      **Then** the accounting equation must balance:
      - Total Assets - Total Liabilities = Opening Balance Equity

- [ ] **Given** the user views account summary
      **When** opening balances exist
      **Then** display accounting equation with values:
      - Assets: $X
      - Liabilities: $Y
      - Equity (Opening Balance): $Z
      - Status: ✅ Balanced or ❌ Unbalanced

#### AC5: Opening Balance Transaction Metadata
- [ ] **Given** an opening balance journal entry
      **When** viewing the transaction
      **Then** it should be marked with `is_opening_balance=True`
      **And** the description should include "Opening Balance"
      **And** the transaction date should match the specified opening date

- [ ] **Given** the transaction list
      **When** filtering transactions
      **Then** users can filter to show/hide opening balance entries
      **And** opening balance entries are visually distinguished (e.g., icon, color)

#### AC6: UI Enhancements
- [ ] **Given** the account creation dialog
      **When** opened
      **Then** it includes an "Opening Balance" field with:
      - Decimal input (optional)
      - Date picker for "Opening Date" (defaults to today)
      - Help text explaining opening balances

- [ ] **Given** an existing account detail view
      **When** the account has $0 balance and no transactions
      **Then** display a "Set Opening Balance" button
      **And** clicking it opens a dialog to set opening balance

- [ ] **Given** the accounts list view
      **When** displaying accounts
      **Then** the Opening Balance Equity account should:
      - Be hidden by default (or in separate "System Accounts" section)
      - Be viewable via "Show System Accounts" toggle
      - Clearly labeled as "Opening Balance Equity (System)"

### Non-Functional Requirements

#### Performance
- [ ] **Performance:** Opening balance entry creation completes in < 100ms
- [ ] **Performance:** Opening Balance Equity account creation < 50ms
- [ ] **Performance:** Accounting equation validation < 50ms for 100 accounts

#### Data Integrity
- [ ] **Data Integrity:** All opening balance entries are atomic transactions (rollback on error)
- [ ] **Data Integrity:** Opening Balance Equity account cannot be deleted if opening balance entries exist
- [ ] **Data Integrity:** Opening balance transactions cannot be manually edited (system-managed)

#### Usability
- [ ] **Usability:** User guide includes step-by-step instructions for setting up opening balances
- [ ] **Usability:** Error messages clearly explain accounting equation violations
- [ ] **Usability:** In-app help text explains "Opening Balance Equity" concept

#### Security
- [ ] **Security:** Validate that opening balance amounts are reasonable (< $1 billion per account)
- [ ] **Security:** Prevent duplicate opening balance entries for same account
- [ ] **Security:** Validate opening date is not in future

### Definition of Done
- [ ] All functional and non-functional requirements met
- [ ] Code implemented with full type hints and docstrings
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests for complete opening balance workflow
- [ ] Performance tests verify speed requirements
- [ ] Database migration for any schema changes
- [ ] User guide updated with "Setting Up Opening Balances" section
- [ ] Architecture documentation updated
- [ ] Code reviewed and approved by Tech Lead
- [ ] Manual testing completed with real-world scenarios
- [ ] PO acceptance obtained
- [ ] No regressions in existing tests

---

## 🔧 Technical Details

### Affected Components

#### Data Layer
- [ ] `finance_app/data/models.py`
  - Add `is_opening_balance: bool` field to Transaction model
  - Add `opening_date: Optional[date]` field to Account model

- [ ] `finance_app/data/migrations/006_opening_balance_equity.sql`
  - Add `is_opening_balance BOOLEAN DEFAULT 0` to transactions table
  - Add `opening_date DATE` to accounts table
  - Create Opening Balance Equity account if not exists

- [ ] `finance_app/data/repositories/account_repository.py`
  - Add `get_by_name(name: str)` method (if not exists)
  - Add `get_opening_balance_equity_account()` method

#### Business Layer
- [ ] `finance_app/business/account_service.py`
  - Add `ensure_opening_balance_equity_account()` method
  - Add `set_opening_balance()` method
  - Add `create_account_with_opening_balance()` method
  - Add `validate_accounting_equation()` method
  - Add `get_accounting_equation_status()` method

- [ ] `finance_app/business/transaction_service.py`
  - Update `create_transaction()` to accept `is_opening_balance` flag
  - Add `create_opening_balance_entry()` method

#### UI Layer
- [ ] `finance_app/ui/dialogs/account_dialog.py`
  - Add "Opening Balance" field (QLineEdit with currency validation)
  - Add "Opening Date" field (QDateEdit)
  - Add help text and info icon

- [ ] `finance_app/ui/dialogs/set_opening_balance_dialog.py` (NEW)
  - New dialog for setting opening balance on existing accounts
  - Shows current balance, proposed opening balance
  - Shows journal entry preview
  - Requires confirmation

- [ ] `finance_app/ui/main_window.py`
  - Add "Set Opening Balance" action to account context menu
  - Add accounting equation summary to dashboard (optional)
  - Add "Show System Accounts" toggle

#### Tests
- [ ] `finance_app/tests/unit/test_account_service_opening_balance.py` (NEW)
  - Test ensure_opening_balance_equity_account()
  - Test set_opening_balance() for all account types
  - Test accounting equation validation
  - Test error cases (duplicate entries, invalid amounts)

- [ ] `finance_app/tests/integration/test_opening_balance_workflow.py` (NEW)
  - Test complete workflow: create accounts with opening balances
  - Test accounting equation remains balanced
  - Test UI interactions

- [ ] `finance_app/tests/unit/test_transaction_opening_balance.py` (NEW)
  - Test opening balance transaction creation
  - Test is_opening_balance flag propagation

### Implementation Approach

**Phase 1: Data Layer (1 hour)**
```python
# 1. Add migration 006_opening_balance_equity.sql
ALTER TABLE transactions ADD COLUMN is_opening_balance BOOLEAN DEFAULT 0;
ALTER TABLE accounts ADD COLUMN opening_date DATE;

# 2. Update Transaction model
@dataclass
class Transaction:
    # ... existing fields ...
    is_opening_balance: bool = False

# 3. Update Account model
@dataclass
class Account:
    # ... existing fields ...
    opening_date: Optional[date] = None
```

**Phase 2: Business Layer (3 hours)**
```python
# AccountService methods

def ensure_opening_balance_equity_account(self) -> Account:
    """
    Ensure Opening Balance Equity account exists.
    Creates it if it doesn't exist.

    Returns:
        The Opening Balance Equity account
    """
    equity_account = self.account_repo.get_by_name("Opening Balance Equity")

    if not equity_account:
        equity_account = self.create_account(
            name="Opening Balance Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubtype.OPENING_BALANCE,
            balance=Decimal("0.00")
        )

    return equity_account


def set_opening_balance(
    self,
    account_id: int,
    opening_balance: Decimal,
    opening_date: date
) -> Transaction:
    """
    Set opening balance for an account.
    Creates balanced journal entry with Opening Balance Equity.

    Args:
        account_id: Account to set opening balance for
        opening_balance: Initial balance amount
        opening_date: Date of opening balance

    Returns:
        The created opening balance transaction

    Raises:
        ValueError: If account already has opening balance
        ValueError: If opening_date is in future
    """
    # Get account
    account = self.get_account(account_id)

    # Validation
    if opening_date > date.today():
        raise ValueError("Opening date cannot be in future")

    # Check for existing opening balance
    existing_opening = self.transaction_repo.get_opening_balance_for_account(account_id)
    if existing_opening:
        raise ValueError(f"Account already has opening balance: {existing_opening.id}")

    # Ensure Opening Balance Equity exists
    equity_account = self.ensure_opening_balance_equity_account()

    # Create balanced journal entry
    from finance_app.utils.accounting_helpers import get_normal_balance

    if account.normal_balance == NormalBalance.DEBIT:
        # Asset/Expense: Debit account, Credit equity
        debit_account = account
        credit_account = equity_account
    else:
        # Liability/Equity/Income: Debit equity, Credit account
        debit_account = equity_account
        credit_account = account

    # Create transaction group
    transaction = self.transaction_service.create_opening_balance_entry(
        debit_account=debit_account,
        credit_account=credit_account,
        amount=abs(opening_balance),
        opening_date=opening_date,
        description=f"Opening Balance - {account.name}"
    )

    # Update account opening_date
    account.opening_date = opening_date
    self.account_repo.update(account)

    return transaction


def create_account_with_opening_balance(
    self,
    name: str,
    account_type: AccountType,
    account_subtype: AccountSubtype,
    opening_balance: Decimal,
    opening_date: date,
    **kwargs
) -> Tuple[Account, Optional[Transaction]]:
    """
    Create account with opening balance in one operation.

    Returns:
        Tuple of (created_account, opening_balance_transaction or None)
    """
    # Create account with $0 balance
    account = self.create_account(
        name=name,
        account_type=account_type,
        account_subtype=account_subtype,
        balance=Decimal("0.00"),
        **kwargs
    )

    # Set opening balance if non-zero
    opening_transaction = None
    if opening_balance != Decimal("0.00"):
        opening_transaction = self.set_opening_balance(
            account_id=account.id,
            opening_balance=opening_balance,
            opening_date=opening_date
        )

        # Update account balance
        account.balance = opening_balance
        account = self.account_repo.update(account)

    return account, opening_transaction


def validate_accounting_equation(self) -> Tuple[bool, Dict]:
    """
    Validate that accounting equation is balanced.

    Returns:
        Tuple of (is_balanced, equation_dict)

    Example:
        {
            "total_assets": Decimal("10000.00"),
            "total_liabilities": Decimal("2000.00"),
            "total_equity": Decimal("8000.00"),
            "is_balanced": True,
            "discrepancy": Decimal("0.00")
        }
    """
    accounts = self.account_repo.get_all()

    total_assets = sum(
        acc.balance for acc in accounts
        if acc.account_type == AccountType.ASSET
    )
    total_liabilities = sum(
        acc.balance for acc in accounts
        if acc.account_type == AccountType.LIABILITY
    )
    total_equity = sum(
        acc.balance for acc in accounts
        if acc.account_type == AccountType.EQUITY
    )

    # Accounting equation: Assets = Liabilities + Equity
    discrepancy = total_assets - (total_liabilities + total_equity)
    is_balanced = abs(discrepancy) < Decimal("0.01")

    return is_balanced, {
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        "is_balanced": is_balanced,
        "discrepancy": discrepancy
    }
```

**Phase 3: UI Layer (2 hours)**
```python
# Add to AccountDialog
class AccountDialog(QDialog):
    def __init__(self, ...):
        # ... existing fields ...

        # Opening Balance section
        opening_group = QGroupBox("Initial Balance (Optional)")
        opening_layout = QFormLayout()

        self.opening_balance_edit = QLineEdit()
        self.opening_balance_edit.setPlaceholderText("0.00")
        # Add currency validator

        self.opening_date_edit = QDateEdit()
        self.opening_date_edit.setDate(QDate.currentDate())
        self.opening_date_edit.setCalendarPopup(True)

        info_label = QLabel(
            "💡 Opening balance creates a balanced journal entry "
            "with Opening Balance Equity account."
        )
        info_label.setWordWrap(True)

        opening_layout.addRow("Opening Balance:", self.opening_balance_edit)
        opening_layout.addRow("Opening Date:", self.opening_date_edit)
        opening_layout.addRow(info_label)

        opening_group.setLayout(opening_layout)
        main_layout.addWidget(opening_group)
```

**Phase 4: Tests (2 hours)**
- 15+ unit tests for AccountService opening balance methods
- 10+ integration tests for complete workflow
- 5+ UI tests for dialog interactions

### Database Changes

**Migration 006: Opening Balance Equity Support**
```sql
-- Add opening balance tracking to transactions
ALTER TABLE transactions ADD COLUMN is_opening_balance BOOLEAN DEFAULT 0;

-- Add opening date to accounts
ALTER TABLE accounts ADD COLUMN opening_date DATE;

-- Create index for filtering opening balance transactions
CREATE INDEX idx_transactions_opening_balance
ON transactions(is_opening_balance)
WHERE is_opening_balance = 1;

-- Create Opening Balance Equity account if not exists
INSERT INTO accounts (
    name,
    account_type,
    account_subtype,
    balance,
    normal_balance,
    created_at
)
SELECT
    'Opening Balance Equity',
    'equity',
    'opening_balance',
    0.00,
    'credit',
    CURRENT_TIMESTAMP
WHERE NOT EXISTS (
    SELECT 1 FROM accounts
    WHERE name = 'Opening Balance Equity'
);
```

---

## 🎨 Design

### UI/UX Mockups

**Account Creation Dialog with Opening Balance:**
```
┌─────────────────────────────────────────────┐
│ Create New Account                    [X]   │
├─────────────────────────────────────────────┤
│                                             │
│ Account Name: [My Checking Account______]  │
│                                             │
│ Account Type:  [Asset ▼]                   │
│ Account Subtype: [Checking ▼]              │
│                                             │
│ ┌─ Initial Balance (Optional) ──────────┐  │
│ │                                        │  │
│ │ Opening Balance: [$2,500.00_______]   │  │
│ │ Opening Date:    [01/01/2025 📅]      │  │
│ │                                        │  │
│ │ 💡 Opening balance creates a balanced │  │
│ │    journal entry with Opening Balance │  │
│ │    Equity account.                    │  │
│ └────────────────────────────────────────┘  │
│                                             │
│           [Cancel]  [Create Account]        │
└─────────────────────────────────────────────┘
```

**Set Opening Balance Dialog (for existing accounts):**
```
┌─────────────────────────────────────────────┐
│ Set Opening Balance - My Checking     [X]   │
├─────────────────────────────────────────────┤
│                                             │
│ Current Balance: $0.00                      │
│                                             │
│ Opening Balance: [$2,500.00_______]        │
│ Opening Date:    [01/01/2025 📅]           │
│                                             │
│ ┌─ Journal Entry Preview ──────────────┐   │
│ │ Date: 01/01/2025                     │   │
│ │ Description: Opening Balance - My... │   │
│ │                                      │   │
│ │ Debit:  My Checking        $2,500.00│   │
│ │ Credit: Opening Balance Eq $2,500.00│   │
│ │                            ─────────  │   │
│ │ Total:                     $2,500.00│   │
│ └──────────────────────────────────────┘   │
│                                             │
│ ⚠️ This will create a transaction dated    │
│    01/01/2025. Ensure this date is before  │
│    any existing transactions.               │
│                                             │
│           [Cancel]  [Set Opening Balance]   │
└─────────────────────────────────────────────┘
```

**Dashboard: Accounting Equation Summary (optional feature):**
```
┌─────────────────────────────────────────────┐
│ Accounting Summary                          │
├─────────────────────────────────────────────┤
│                                             │
│ Assets:        $37,500.00                   │
│ Liabilities:   -$850.00                     │
│ ────────────────────────────                │
│ Net Worth:     $36,650.00                   │
│                                             │
│ Equity (Opening Balance):  $36,650.00       │
│                                             │
│ Status: ✅ Balanced                         │
└─────────────────────────────────────────────┘
```

### User Flow

**Flow 1: Create Account with Opening Balance**
```
1. User clicks "Add Account" button
2. Account creation dialog opens
3. User fills in:
   - Name: "My Checking"
   - Type: Asset
   - Subtype: Checking
   - Opening Balance: $2,500
   - Opening Date: 01/01/2025
4. User clicks "Create Account"
5. System:
   a. Creates "My Checking" account with $0 balance
   b. Creates/gets "Opening Balance Equity" account
   c. Creates journal entry:
      - Debit: My Checking $2,500
      - Credit: Opening Balance Equity $2,500
      - Marked as is_opening_balance=True
      - Dated 01/01/2025
   d. Updates account balance to $2,500
6. Success message: "Account created with opening balance"
7. Dialog closes
8. Account appears in list with $2,500 balance
```

**Flow 2: Set Opening Balance on Existing Account**
```
1. User right-clicks existing account (balance = $0)
2. Context menu shows "Set Opening Balance"
3. User clicks "Set Opening Balance"
4. Dialog opens showing:
   - Current balance
   - Opening balance field
   - Opening date field
   - Journal entry preview
5. User enters opening balance and date
6. Preview updates showing journal entry
7. User clicks "Set Opening Balance"
8. System creates opening balance entry
9. Account balance updates
10. Success message displayed
```

---

## 🧪 Test Plan

### Test Cases

#### Test Case 1: Auto-Create Opening Balance Equity Account
- **Given:** No Opening Balance Equity account exists
- **When:** User creates first account with opening balance of $1,000
- **Then:**
  - Opening Balance Equity account is automatically created
  - It has type=EQUITY, subtype=OPENING_BALANCE
  - Initial balance is $0 (before transaction)
  - After transaction, balance is $1,000
- **Test Data:** Asset account, opening balance $1,000

#### Test Case 2: Asset Account Opening Balance
- **Given:** Opening Balance Equity account exists
- **When:** User creates Asset account with opening balance $2,500
- **Then:**
  - Journal entry created: Debit Asset $2,500, Credit Equity $2,500
  - Asset account balance = $2,500
  - Opening Balance Equity increases by $2,500
  - Transaction marked with is_opening_balance=True
- **Test Data:** Checking account, $2,500, date 2025-01-01

#### Test Case 3: Liability Account Opening Balance
- **Given:** Opening Balance Equity account exists with balance $2,500
- **When:** User creates Liability account with opening balance $850
- **Then:**
  - Journal entry created: Debit Equity $850, Credit Liability $850
  - Liability account balance = $850
  - Opening Balance Equity decreases to $1,650 ($2,500 - $850)
  - Accounting equation remains balanced
- **Test Data:** Credit card, $850, date 2025-01-01

#### Test Case 4: Multiple Accounts - Accounting Equation Validation
- **Given:** Clean system
- **When:** User creates multiple accounts with opening balances:
  - Checking (Asset): $2,500
  - Savings (Asset): $10,000
  - Credit Card (Liability): $850
  - Investment (Asset): $25,000
- **Then:**
  - Total Assets = $37,500
  - Total Liabilities = $850
  - Opening Balance Equity = $36,650
  - Accounting equation validates: $37,500 - $850 = $36,650 ✅
- **Test Data:** Multiple accounts as listed

#### Test Case 5: Zero Opening Balance (No Transaction)
- **Given:** System with Opening Balance Equity account
- **When:** User creates account with opening balance = $0 or blank
- **Then:**
  - Account is created with $0 balance
  - NO journal entry is created
  - NO transaction with Opening Balance Equity
  - Account has opening_date = None
- **Test Data:** Checking account, $0 opening balance

#### Test Case 6: Set Opening Balance on Existing Account
- **Given:** Existing account "Old Savings" with $0 balance, no transactions
- **When:** User sets opening balance of $5,000 dated 2025-01-01
- **Then:**
  - Opening balance journal entry created
  - Entry dated 2025-01-01
  - Account balance updates to $5,000
  - Account opening_date = 2025-01-01
- **Test Data:** Existing account, $5,000, 2025-01-01

#### Test Case 7: Opening Balance with Existing Transactions (Warning)
- **Given:** Account has existing transactions dated 2025-02-01 and later
- **When:** User tries to set opening balance dated 2025-03-01 (after transactions)
- **Then:**
  - System displays warning: "Opening date must be before existing transactions"
  - Does not create opening balance entry
  - Suggests earliest valid date (before first transaction)
- **Test Data:** Account with transactions, invalid opening date

#### Test Case 8: Duplicate Opening Balance Prevention
- **Given:** Account already has an opening balance entry
- **When:** User tries to set opening balance again
- **Then:**
  - System displays error: "Account already has opening balance"
  - Does not create duplicate entry
  - Suggests editing or deleting existing opening balance
- **Test Data:** Account with existing opening balance

#### Test Case 9: Future Opening Date Validation
- **Given:** User creating account
- **When:** User enters opening date in future (e.g., 2026-01-01)
- **Then:**
  - System displays error: "Opening date cannot be in future"
  - Does not create account/opening balance
  - Field validation highlights error
- **Test Data:** Account with opening_date > today

#### Test Case 10: Opening Balance Transaction Filtering
- **Given:** System has multiple transactions including opening balance entries
- **When:** User applies filter "Hide Opening Balance Entries"
- **Then:**
  - Transaction list excludes all transactions with is_opening_balance=True
  - Regular transactions still displayed
  - Filter state persists across sessions
- **Test Data:** Mixed transactions, some with is_opening_balance=True

### Edge Cases
- [ ] Very large opening balance ($1 million+) - should work but validate
- [ ] Negative opening balance for assets (unusual but valid)
- [ ] Creating 100+ accounts with opening balances (performance test)
- [ ] Opening balance exactly $0.00 vs empty/null (both treated as no opening balance)
- [ ] Opening Balance Equity account manually deleted (system recreates)
- [ ] Opening balance entry manually deleted (accounting equation broken - detect and warn)
- [ ] Account created programmatically via API/import (opening balance support)

### Error Scenarios
- [ ] Database connection lost during opening balance creation (rollback)
- [ ] Invalid opening balance amount (non-numeric, too many decimals)
- [ ] Opening date in invalid format
- [ ] Opening Balance Equity account corrupted/wrong type
- [ ] Concurrent opening balance creation for same account (race condition)

---

## 📊 Dependencies

### Blocked By
- ✅ US-001: Account Type Taxonomy (Complete) - Need account types and subtypes
- ✅ US-002A: Journal Entry Foundation (Complete) - Need transaction/journal entry creation
- ✅ US-003: Normal Balance Calculation (Complete) - Need normal balance logic for debit/credit

### Blocks
- None - This is a standalone feature

### Related Stories
- US-006: Account Hierarchy (may need opening balances for parent accounts)
- Future: Data Import feature (will use opening balance functionality)
- Future: Account Migration tool (will use opening balance functionality)

---

## 📏 Estimation

### Story Points Breakdown
- **Development:** 3 points
  - Data layer: 0.5 points (migration, model updates)
  - Business layer: 1.5 points (5 new methods, validation logic)
  - UI layer: 1 point (dialog updates, new dialog)
- **Testing:** 1.5 points
  - Unit tests: 0.75 points (15 tests)
  - Integration tests: 0.5 points (10 tests)
  - Manual testing: 0.25 points
- **Documentation:** 0.5 points
  - User guide: 0.25 points
  - Architecture docs: 0.25 points
- **Total:** 5 points

### Time Estimate
- **Optimistic:** 6 hours (everything works first try)
- **Realistic:** 8-10 hours (normal development with debugging)
- **Pessimistic:** 12 hours (complex edge cases, extensive testing)

### Complexity
- **Technical Complexity:** Medium
  - Need to understand accounting principles (debit/credit for different account types)
  - Atomic transaction creation important
  - Accounting equation validation logic
- **Business Complexity:** Medium-High
  - Accounting concepts may be unfamiliar to some developers
  - Critical to get debit/credit correct for each account type
  - Opening Balance Equity concept needs clear explanation
- **Risk Level:** Medium
  - High impact if accounting equation breaks
  - Must maintain data integrity
  - Existing accounts should not be affected

---

## 📋 Implementation Checklist

### Development
- [ ] Branch created from `main`: `feature/US-005-opening-balance-equity`
- [ ] Database migration 006 created and tested
- [ ] Transaction model updated with `is_opening_balance` field
- [ ] Account model updated with `opening_date` field
- [ ] AccountRepository `get_by_name()` method implemented
- [ ] AccountService `ensure_opening_balance_equity_account()` implemented
- [ ] AccountService `set_opening_balance()` implemented
- [ ] AccountService `create_account_with_opening_balance()` implemented
- [ ] AccountService `validate_accounting_equation()` implemented
- [ ] TransactionService `create_opening_balance_entry()` implemented
- [ ] AccountDialog updated with opening balance fields
- [ ] SetOpeningBalanceDialog created
- [ ] MainWindow context menu action added
- [ ] Error handling for all edge cases
- [ ] Logging added for opening balance operations
- [ ] Type hints added to all new methods
- [ ] Docstrings added with examples

### Testing
- [ ] Unit tests for ensure_opening_balance_equity_account() (3 tests)
- [ ] Unit tests for set_opening_balance() (8 tests)
- [ ] Unit tests for create_account_with_opening_balance() (5 tests)
- [ ] Unit tests for validate_accounting_equation() (4 tests)
- [ ] Integration tests for complete opening balance workflow (10 tests)
- [ ] UI tests for dialog interactions (optional)
- [ ] Manual testing with real-world scenario
- [ ] Edge cases tested (large amounts, negative amounts, etc.)
- [ ] Error scenarios tested (duplicate entries, invalid dates)
- [ ] All tests passing locally (>80% coverage target)

### Code Review
- [ ] Self-review completed
- [ ] PR created with detailed description
- [ ] Code review requested from Tech Lead
- [ ] Feedback addressed
- [ ] PR approved

### Documentation
- [ ] Code comments added for complex logic
- [ ] User guide updated with "Setting Up Opening Balances" section
- [ ] Architecture documentation updated
- [ ] CHANGELOG updated
- [ ] Demo script created for PO review

### Deployment
- [ ] Merged to main
- [ ] Database migration applied to staging
- [ ] Smoke tests passed on staging
- [ ] PO acceptance obtained
- [ ] Deployed to production (if applicable)

---

## 📝 Notes

### Technical Notes

**Why Opening Balance Equity?**

In double-entry accounting, the Opening Balance Equity account serves as a "balancing" account when setting up initial balances. It represents the cumulative effect of all starting balances and ensures the accounting equation (Assets = Liabilities + Equity) remains balanced.

Think of it as "where did the money come from?" for your starting balances. When you start tracking finances, you don't have historical transactions, so Opening Balance Equity represents your net worth at the start.

**Alternative Considered: Individual Equity Accounts**

We could create separate equity accounts for each opening balance, but this adds complexity and doesn't follow standard accounting practice. Opening Balance Equity is a standard QuickBooks/accounting concept.

**Opening Balance vs Regular Transaction**

Opening balance entries are special because:
1. They always involve Opening Balance Equity as offsetting account
2. They should be dated at account setup (historical date)
3. They cannot be edited manually (system-managed)
4. They can be filtered out of reports for clarity

### Business Notes

**User Education**

Many personal finance users don't understand "Opening Balance Equity" - it sounds technical. The UI should:
- Use friendly language: "Initial Balance" in UI
- Provide tooltip: "Creates a starting balance for your account"
- Link to help: "Learn more about opening balances"
- Show only when relevant (hide Opening Balance Equity account by default)

**Migration from Other Systems**

Users coming from Mint, YNAB, or other apps will need to set opening balances to match their current state. The user guide should include:
- "Migrating from Another App" section
- Step-by-step instructions
- Example: "If your checking account has $2,500 today, set opening balance to $2,500 with today's date"

### Questions
- [x] **Q1:** Should Opening Balance Equity account be visible in account list by default?
  - **Answer:** No, hide by default. Show in "System Accounts" section if user enables it.

- [x] **Q2:** Can users edit/delete opening balance transactions?
  - **Answer:** No, they are system-managed. Users can delete and recreate if needed.

- [x] **Q3:** What if user wants to change opening balance later?
  - **Answer:** Provide "Edit Opening Balance" action that deletes old entry and creates new one.

- [ ] **Q4:** Should we support opening balances for split transactions?
  - **Status:** Discuss with PO - probably not needed for MVP

### Risks
1. **Risk:** Users might not understand Opening Balance Equity concept
   - **Mitigation:** Clear UI labels, help text, user guide section

2. **Risk:** Incorrect debit/credit for some account type might break accounting equation
   - **Mitigation:** Comprehensive unit tests for all account types, validation in code

3. **Risk:** Users might try to edit/delete Opening Balance Equity account
   - **Mitigation:** Add validation preventing deletion if opening balance entries exist

---

## 📺 Demo

### Demo Script

**Scenario:** New user setting up accounts for the first time

1. **Open account creation dialog**
   - Show empty account list
   - Click "Add Account" button

2. **Create Checking account with opening balance**
   - Name: "My Checking"
   - Type: Asset → Checking
   - Opening Balance: $2,500
   - Opening Date: January 1, 2025
   - Click "Create Account"
   - **Result:** Account created, balance shows $2,500

3. **Show Opening Balance Equity account**
   - Enable "Show System Accounts" toggle
   - **Point out:** Opening Balance Equity account automatically created
   - Balance: $2,500 (offsetting the checking account)

4. **Create Credit Card account with opening balance**
   - Name: "Visa Card"
   - Type: Liability → Credit Card
   - Opening Balance: $850
   - Opening Date: January 1, 2025
   - Click "Create Account"
   - **Result:** Credit card created with $850 balance

5. **Show accounting equation summary**
   - Assets: $2,500
   - Liabilities: $850
   - Equity (Opening Balance): $1,650
   - Status: ✅ Balanced

6. **Show transaction list**
   - Two opening balance entries visible
   - Marked with special icon
   - Can be filtered out

7. **Demonstrate "Set Opening Balance" on existing account**
   - Create new Savings account with $0 balance
   - Right-click → "Set Opening Balance"
   - Enter $10,000, date January 1
   - Show journal entry preview
   - Confirm
   - Balance updates to $10,000

### Demo Data Setup

```python
# Create demo accounts with opening balances
accounts = [
    {
        "name": "My Checking",
        "type": AccountType.ASSET,
        "subtype": AccountSubtype.CHECKING,
        "opening_balance": Decimal("2500.00"),
        "opening_date": date(2025, 1, 1)
    },
    {
        "name": "Visa Card",
        "type": AccountType.LIABILITY,
        "subtype": AccountSubtype.CREDIT_CARD,
        "opening_balance": Decimal("850.00"),
        "opening_date": date(2025, 1, 1)
    },
    {
        "name": "Investment Account",
        "type": AccountType.ASSET,
        "subtype": AccountSubtype.INVESTMENT,
        "opening_balance": Decimal("25000.00"),
        "opening_date": date(2025, 1, 1)
    }
]

# Expected Opening Balance Equity: $26,650 ($27,500 - $850)
```

### Demo Acceptance Criteria
- [ ] All accounts created successfully
- [ ] Opening Balance Equity account auto-created
- [ ] All balances display correctly
- [ ] Accounting equation is balanced
- [ ] Journal entries are correct (debit/credit)
- [ ] UI is intuitive and clear
- [ ] Help text and tooltips are helpful

---

## 🔗 References

### Code References
- `finance_app/data/models.py:45-120` - Account and Transaction models
- `finance_app/business/account_service.py` - Account business logic
- `finance_app/utils/accounting_helpers.py` - Normal balance helpers
- `finance_app/tests/unit/test_account_service.py` - Existing account service tests

### Related Documents
- [Epic-01: Account Management](../../epics/epic-01-account-management.md)
- [US-001: Account Type Taxonomy](../completed/US-001-account-type-taxonomy.md)
- [US-003: Normal Balance Calculation](../completed/US-003-normal-balance-calculation.md)
- [Architecture Documentation](../../ARCHITECTURE.md)

### External Resources
- [QuickBooks: Opening Balance Equity Explained](https://quickbooks.intuit.com/learn-support/en-us/help-article/opening-balances/opening-balance-equity-account/L2hVUgVWD_US_en_US)
- [Double-Entry Accounting Basics](https://www.accountingtools.com/articles/what-is-double-entry-accounting.html)
- [Accounting Equation](https://www.investopedia.com/terms/a/accounting-equation.asp)

---

**Created By:** Product Owner Agent
**Last Updated:** October 25, 2025 (Sprint 7 Planning)
**Epic:** epic-01 - Account Management & Double-Entry Foundation
**Target Sprint:** Sprint 7
**Estimated Duration:** 1-2 days (8-10 hours)
