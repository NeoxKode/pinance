# Epic 1: Account Management & Double-Entry Foundation

**Epic ID:** epic-01
**Status:** 🟢 In Progress (16% complete)
**Priority:** P0 (Critical - Blocking)
**Estimated Effort:** 2-3 weeks (80-120 hours)
**Target Sprint:** Sprint 1-3
**Created:** October 22, 2025
**Started:** October 22, 2025
**Owner:** Development Team
**Progress:** 1/6 stories completed (8/50+ points)

---

## 📖 Epic Summary

Complete the foundational Account Management system to support professional double-entry accounting while maintaining a simple, intuitive user interface. This epic establishes the core data structures and business logic required for all other features in the Personal Finance Manager.

### Vision Statement

*"As a power user, I want a robust account management system that supports professional double-entry accounting behind the scenes, so I can track my finances with accuracy and confidence without needing accounting expertise."*

---

## 🎯 Business Goals

### Primary Goals
1. **Complete Feature #1** from PRD (Account Management) with all acceptance criteria met
2. **Establish double-entry foundation** for Feature #2 (Double-Entry Accounting System)
3. **Enable professional accounting accuracy** without adding complexity to the user experience
4. **Support multiple account types** (Assets, Liabilities, Equity, Income, Expenses)
5. **Prepare for reconciliation** (Feature #2 requirement)

### Success Metrics
- ✅ Users can create/edit/delete accounts in < 5 seconds
- ✅ Support for 50+ accounts without performance degradation
- ✅ 100% accounting accuracy (balance = sum of journal entries)
- ✅ Zero data loss during account operations
- ✅ All account operations properly validated and logged

---

## 📊 Current State vs Desired State

### Current State ✅ (What's Working)
- ✅ Basic CRUD operations (create, read, update, delete)
- ✅ Account repository with proper error handling
- ✅ Account service with validation layer
- ✅ Type-safe data models
- ✅ Logging and exception handling
- ✅ 4 basic account types: bank, cash, credit, investment
- ✅ Simple balance tracking
- ✅ Currency field (USD default)

### Gaps 🔴 (What's Missing)
- ❌ Double-entry account model (no journal entries)
- ❌ Account type hierarchy (Asset → Checking, Liability → Credit Card)
- ❌ Normal balance tracking (debit vs credit accounts)
- ❌ Reconciliation support (no reconciliation fields)
- ❌ Transaction count per account
- ❌ Account color-coding in UI
- ❌ Account status (active/inactive/archived)
- ❌ Opening balance equity handling
- ❌ Account number (for bank reconciliation)
- ❌ Multi-currency exchange rates
- ❌ Parent/child account hierarchy
- ❌ Balance validation against journal entries

### Desired End State 🎯
- ✅ **Complete double-entry account model** with journal entry foundation
- ✅ **5 primary account types** (Assets, Liabilities, Equity, Income, Expenses)
- ✅ **Subtypes for each category** (Checking, Savings, Credit Card, etc.)
- ✅ **Automatic normal balance** determination (debit/credit)
- ✅ **Reconciliation-ready** with status tracking
- ✅ **Opening balances** handled via Equity account
- ✅ **Account hierarchy** support (parent/child accounts)
- ✅ **Enhanced UI** with color-coding and transaction counts
- ✅ **Balance integrity** guaranteed by database constraints

---

## 👥 User Stories Overview

This epic contains **10 user stories** organized into 3 phases:

### Phase 1: Account Model & Double-Entry Foundation (Week 1)
- **US-001**: Account Type Taxonomy & Hierarchy
- **US-002**: Double-Entry Account Model
- **US-003**: Normal Balance Calculation
- **US-004**: Account Opening Balances

### Phase 2: Enhanced Account Features (Week 2)
- **US-005**: Account Reconciliation Support
- **US-006**: Account Status & Lifecycle
- **US-007**: Account Metadata & Organization
- **US-008**: Multi-Currency Account Setup

### Phase 3: UI & Integration (Week 3)
- **US-009**: Account Color Coding & Visual Indicators
- **US-010**: Account Balance Validation & Integrity

---

## 📝 User Stories (Detailed)

---

### **US-001: Account Type Taxonomy & Hierarchy** ✅ COMPLETED

**As a** power user
**I want** accounts organized by accounting type (Assets, Liabilities, Equity, Income, Expenses) with subtypes
**So that** I can use proper accounting categories while seeing familiar account names

**Priority:** P0 (Must Have - Blocking)
**Story Points:** 8
**Sprint:** Sprint 1
**Status:** ✅ Completed October 22, 2025
**Commit:** ba55779
**Story File:** [US-001](../stories/completed/US-001-account-type-taxonomy.md)

#### Acceptance Criteria

**Given** I am creating a new account
**When** I select account type
**Then** I should see 5 primary types:
- Assets (Checking, Savings, Cash, Investment, Other Asset)
- Liabilities (Credit Card, Loan, Mortgage, Line of Credit, Other Liability)
- Equity (Opening Balance, Retained Earnings)
- Income (Salary, Business Income, Interest, Dividends, Other Income)
- Expenses (Auto-created from categories)

**And** each primary type has relevant subtypes
**And** the subtype determines the account's normal balance (debit/credit)

**Given** I am viewing my accounts
**When** I look at the account list
**Then** accounts are grouped by primary type
**And** subtypes are shown as descriptive labels (e.g., "Checking Account" not "Asset")

#### Technical Notes

**Database Changes Required:**
```sql
-- Add new columns to accounts table
ALTER TABLE accounts ADD COLUMN account_type TEXT NOT NULL DEFAULT 'asset';
  -- Values: 'asset', 'liability', 'equity', 'income', 'expense'

ALTER TABLE accounts ADD COLUMN account_subtype TEXT NOT NULL DEFAULT 'checking';
  -- Values: 'checking', 'savings', 'cash', 'credit_card', 'loan', etc.

ALTER TABLE accounts ADD COLUMN normal_balance TEXT NOT NULL DEFAULT 'debit';
  -- Values: 'debit', 'credit'

ALTER TABLE accounts ADD COLUMN parent_account_id INTEGER;
  -- For hierarchical accounts (future)

-- Rename old 'type' column to 'legacy_type' for migration
ALTER TABLE accounts RENAME COLUMN type TO legacy_type;
```

**Model Changes:**
```python
@dataclass
class Account:
    # ... existing fields ...
    account_type: str  # 'asset', 'liability', 'equity', 'income', 'expense'
    account_subtype: str  # 'checking', 'savings', 'credit_card', etc.
    normal_balance: str  # 'debit' or 'credit'
    parent_account_id: Optional[int] = None
```

**Validation Rules:**
- account_type must be one of: asset, liability, equity, income, expense
- account_subtype must match account_type (e.g., 'checking' only valid for 'asset')
- normal_balance auto-calculated based on account_type:
  - Assets, Expenses → 'debit'
  - Liabilities, Equity, Income → 'credit'

**Data Migration:**
```python
# Migration script needed to convert old types to new taxonomy:
# 'bank' → account_type='asset', account_subtype='checking'
# 'cash' → account_type='asset', account_subtype='cash'
# 'credit' → account_type='liability', account_subtype='credit_card'
# 'investment' → account_type='asset', account_subtype='investment'
```

#### Definition of Done
- [ ] Database schema updated with migration script
- [ ] Account model includes new fields
- [ ] AccountValidator validates account_type and account_subtype combinations
- [ ] Data migration script tested with existing data
- [ ] All existing accounts successfully migrated
- [ ] Unit tests for account type validation (15+ test cases)
- [ ] Integration tests for account creation with new types
- [ ] Documentation updated with account type taxonomy

#### Dependencies
- None (foundational story)

#### Test Scenarios

**Test 1: Create asset account with checking subtype**
```python
account = account_service.create_account(
    name="My Checking",
    account_type="asset",
    account_subtype="checking"
)
assert account.normal_balance == "debit"
```

**Test 2: Create liability account with credit card subtype**
```python
account = account_service.create_account(
    name="Visa Card",
    account_type="liability",
    account_subtype="credit_card"
)
assert account.normal_balance == "credit"
```

**Test 3: Validation - invalid subtype for account type**
```python
with pytest.raises(ValidationError):
    account_service.create_account(
        name="Invalid",
        account_type="asset",
        account_subtype="credit_card"  # Invalid: credit_card only for liability
    )
```

---

### **US-002: Double-Entry Account Model**

**As a** developer
**I want** accounts to support double-entry accounting with journal entries
**So that** every transaction automatically creates balanced debit/credit records

**Priority:** P0 (Must Have - Blocking)
**Story Points:** 13
**Sprint:** Sprint 1

#### Acceptance Criteria

**Given** the double-entry system is enabled
**When** any account balance changes
**Then** a corresponding journal entry must be created
**And** the journal entry must have balanced debits and credits
**And** account balance must equal sum of all journal entries for that account

**Given** I query an account's balance
**When** I request the calculated balance
**Then** it should match the cached balance in the accounts table
**And** both should equal the sum of journal entry amounts

#### Technical Notes

**New Tables Required:**

```sql
-- Journal entries (double-entry ledger)
CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER,  -- Links to transactions table (nullable for non-transaction entries)
    account_id INTEGER NOT NULL,
    entry_date TEXT NOT NULL,  -- YYYY-MM-DD
    description TEXT NOT NULL,
    debit_amount REAL NOT NULL DEFAULT 0.0,
    credit_amount REAL NOT NULL DEFAULT 0.0,
    balance_after REAL NOT NULL,  -- Running balance after this entry
    entry_type TEXT NOT NULL,  -- 'transaction', 'opening_balance', 'adjustment', 'transfer'
    reference_number TEXT,  -- Check number, invoice number, etc.
    is_reconciled BOOLEAN DEFAULT 0,
    reconciliation_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE CASCADE,
    FOREIGN KEY (reconciliation_id) REFERENCES reconciliations (id)
);

CREATE INDEX idx_journal_account ON journal_entries(account_id);
CREATE INDEX idx_journal_date ON journal_entries(entry_date DESC);
CREATE INDEX idx_journal_transaction ON journal_entries(transaction_id);
CREATE INDEX idx_journal_reconciled ON journal_entries(is_reconciled);

-- Transaction groups (for multi-entry transactions like transfers)
CREATE TABLE transaction_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_date TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link journal entries to transaction groups
ALTER TABLE journal_entries ADD COLUMN group_id INTEGER;
ALTER TABLE journal_entries ADD FOREIGN KEY (group_id) REFERENCES transaction_groups(id);

-- Add constraint: debit and credit cannot both be non-zero
CREATE TRIGGER validate_journal_entry
BEFORE INSERT ON journal_entries
BEGIN
    SELECT CASE
        WHEN NEW.debit_amount > 0 AND NEW.credit_amount > 0 THEN
            RAISE(ABORT, 'Journal entry cannot have both debit and credit amounts')
        WHEN NEW.debit_amount = 0 AND NEW.credit_amount = 0 THEN
            RAISE(ABORT, 'Journal entry must have either debit or credit amount')
        WHEN NEW.debit_amount < 0 OR NEW.credit_amount < 0 THEN
            RAISE(ABORT, 'Debit and credit amounts must be non-negative')
    END;
END;
```

**New Models:**

```python
@dataclass
class JournalEntry:
    """Double-entry journal entry."""
    id: Optional[int]
    transaction_id: Optional[int]
    account_id: int
    entry_date: str  # YYYY-MM-DD
    description: str
    debit_amount: Decimal
    credit_amount: Decimal
    balance_after: Decimal
    entry_type: str  # 'transaction', 'opening_balance', 'adjustment', 'transfer'
    reference_number: Optional[str] = None
    is_reconciled: bool = False
    reconciliation_id: Optional[int] = None
    group_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate journal entry."""
        if self.debit_amount < 0 or self.credit_amount < 0:
            raise ValueError("Debit and credit amounts must be non-negative")
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValueError("Cannot have both debit and credit in same entry")
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValueError("Must have either debit or credit amount")

    @property
    def amount(self) -> Decimal:
        """Get the entry amount (positive for debit, negative for credit)."""
        return self.debit_amount - self.credit_amount

@dataclass
class TransactionGroup:
    """Group of related journal entries (for transfers, splits)."""
    id: Optional[int]
    group_date: str
    description: str
    created_at: Optional[datetime] = None

    def validate_balance(self, entries: List[JournalEntry]) -> bool:
        """Validate that entries in this group balance (debits = credits)."""
        total_debits = sum(e.debit_amount for e in entries)
        total_credits = sum(e.credit_amount for e in entries)
        return total_debits == total_credits
```

**Repository:**

```python
class JournalEntryRepository:
    """Repository for journal entry data access."""

    def create_entry(self, entry: JournalEntry) -> JournalEntry:
        """Create a journal entry and update account balance."""
        # Insert journal entry
        # Update account cached balance
        # Return created entry

    def create_balanced_entries(self, entries: List[JournalEntry],
                                group_id: Optional[int] = None) -> List[JournalEntry]:
        """
        Create multiple journal entries atomically.
        Validates that debits = credits before committing.
        """
        # Validate balance
        # Create all entries in transaction
        # Update affected account balances
        # Return created entries

    def get_account_balance(self, account_id: int) -> Decimal:
        """Calculate account balance from journal entries."""
        # SUM(debit_amount - credit_amount) for account

    def validate_account_balance(self, account_id: int) -> bool:
        """Validate cached balance matches calculated balance."""
        # Compare accounts.balance to SUM(journal_entries)
```

**Service Layer:**

```python
class DoubleEntryService:
    """Service for double-entry accounting operations."""

    def create_simple_transaction(
        self,
        account_id: int,
        amount: Decimal,
        description: str,
        date: str,
        transaction_type: str  # 'income' or 'expense'
    ) -> TransactionGroup:
        """
        Create a simple income/expense transaction.

        For income:
          Debit: Asset Account (increase)
          Credit: Income Account (increase income)

        For expense:
          Debit: Expense Account (increase expense)
          Credit: Asset Account (decrease)
        """

    def create_transfer(
        self,
        from_account_id: int,
        to_account_id: int,
        amount: Decimal,
        description: str,
        date: str,
        fee: Decimal = Decimal('0')
    ) -> TransactionGroup:
        """
        Create a transfer between accounts.

        Debit: Destination Account
        Credit: Source Account
        (If fee: Debit: Fee Expense, Credit: Source Account)
        """

    def validate_all_balances(self) -> Dict[int, bool]:
        """Validate all account balances match journal entries."""
```

#### Definition of Done
- [ ] journal_entries table created with constraints
- [ ] transaction_groups table created
- [ ] JournalEntry and TransactionGroup models implemented
- [ ] JournalEntryRepository with CRUD operations
- [ ] DoubleEntryService with basic transaction creation
- [ ] Database triggers for journal entry validation
- [ ] Balance calculation matches cached balance (100% accuracy)
- [ ] Unit tests for journal entry creation (20+ tests)
- [ ] Integration tests for balance validation
- [ ] Performance test: 10,000 journal entries < 500ms query time

#### Dependencies
- US-001 (Account Type Taxonomy) must be completed first

#### Test Scenarios

**Test 1: Create balanced journal entries**
```python
entries = [
    JournalEntry(account_id=1, debit_amount=100, credit_amount=0, ...),
    JournalEntry(account_id=2, debit_amount=0, credit_amount=100, ...)
]
group = double_entry_service.create_balanced_entries(entries)
assert group.validate_balance(entries) == True
```

**Test 2: Reject unbalanced entries**
```python
entries = [
    JournalEntry(account_id=1, debit_amount=100, credit_amount=0, ...),
    JournalEntry(account_id=2, debit_amount=0, credit_amount=50, ...)  # Unbalanced!
]
with pytest.raises(ValidationError):
    double_entry_service.create_balanced_entries(entries)
```

**Test 3: Account balance matches journal entries**
```python
# Create several journal entries
# Calculate balance from journal_entries table
# Compare to cached balance in accounts table
assert calculated_balance == cached_balance
```

---

### **US-003: Normal Balance Calculation**

**As a** system
**I want** to automatically determine if an account has a debit or credit normal balance
**So that** transactions are recorded correctly in double-entry accounting

**Priority:** P0 (Must Have)
**Story Points:** 3
**Sprint:** Sprint 1

#### Acceptance Criteria

**Given** an account of type "asset" or "expense"
**When** the account is created
**Then** normal_balance should be set to "debit"

**Given** an account of type "liability", "equity", or "income"
**When** the account is created
**Then** normal_balance should be set to "credit"

**Given** a journal entry increases an account
**When** the account has a debit normal balance
**Then** the entry should be a debit

**Given** a journal entry increases an account
**When** the account has a credit normal balance
**Then** the entry should be a credit

#### Technical Notes

**Helper Functions:**

```python
class AccountHelper:
    """Helper functions for account operations."""

    @staticmethod
    def get_normal_balance(account_type: str) -> str:
        """
        Get normal balance for account type.

        Accounting equation: Assets = Liabilities + Equity

        Debit accounts (left side):
          - Assets (increase with debits)
          - Expenses (increase with debits)

        Credit accounts (right side):
          - Liabilities (increase with credits)
          - Equity (increase with credits)
          - Income (increase with credits)
        """
        if account_type in ['asset', 'expense']:
            return 'debit'
        elif account_type in ['liability', 'equity', 'income']:
            return 'credit'
        else:
            raise ValueError(f"Invalid account type: {account_type}")

    @staticmethod
    def create_entry_for_increase(
        account: Account,
        amount: Decimal
    ) -> Tuple[Decimal, Decimal]:
        """
        Create debit/credit amounts to increase an account.
        Returns (debit_amount, credit_amount).
        """
        if account.normal_balance == 'debit':
            return (amount, Decimal('0'))
        else:
            return (Decimal('0'), amount)

    @staticmethod
    def create_entry_for_decrease(
        account: Account,
        amount: Decimal
    ) -> Tuple[Decimal, Decimal]:
        """
        Create debit/credit amounts to decrease an account.
        Returns (debit_amount, credit_amount).
        """
        if account.normal_balance == 'debit':
            return (Decimal('0'), amount)
        else:
            return (amount, Decimal('0'))
```

#### Definition of Done
- [ ] AccountHelper class with normal balance logic
- [ ] Auto-set normal_balance on account creation
- [ ] Validation prevents manual override of normal_balance
- [ ] Unit tests for all account type combinations (10+ tests)
- [ ] Documentation of debit/credit rules

#### Dependencies
- US-001 (Account Type Taxonomy)

---

### **US-004: Account Opening Balances**

**As a** new user migrating from another system
**I want** to set opening balances for my accounts
**So that** I can start tracking from my current financial position

**Priority:** P0 (Must Have)
**Story Points:** 5
**Sprint:** Sprint 1

#### Acceptance Criteria

**Given** I am creating a new account
**When** I specify an opening balance
**Then** an "Opening Balance Equity" account is automatically created (if doesn't exist)
**And** journal entries are created to record the opening balance
**And** the accounting equation remains balanced

**Given** I have set opening balances for all my accounts
**When** I view the "Opening Balance Equity" account
**Then** its balance should equal the negative sum of all opening balances
**And** this balances the accounting equation

#### Technical Notes

**Opening Balance Logic:**

For an asset account with opening balance of $1,000:
```
Debit:  Asset Account          $1,000
Credit: Opening Balance Equity $1,000
```

For a liability account with opening balance of $500:
```
Debit:  Opening Balance Equity $500
Credit: Liability Account      $500
```

**Equity Account Creation:**

```python
class AccountService:

    def ensure_opening_balance_equity_account(self) -> Account:
        """
        Ensure Opening Balance Equity account exists.
        Creates it if it doesn't exist.
        """
        # Check if exists
        equity_account = self.account_repo.get_by_name("Opening Balance Equity")

        if not equity_account:
            equity_account = self.create_account(
                name="Opening Balance Equity",
                account_type="equity",
                account_subtype="opening_balance",
                initial_balance="0.00"
            )

        return equity_account

    def set_opening_balance(
        self,
        account_id: int,
        opening_balance: Decimal,
        as_of_date: str
    ) -> TransactionGroup:
        """
        Set opening balance for an account.
        Creates balanced journal entries with Opening Balance Equity.
        """
        # Get account
        account = self.get_account(account_id)

        # Ensure Opening Balance Equity exists
        equity_account = self.ensure_opening_balance_equity_account()

        # Create balanced journal entries
        if account.normal_balance == 'debit':
            # Debit: Asset/Expense, Credit: Equity
            entries = [
                JournalEntry(
                    account_id=account.id,
                    debit_amount=opening_balance,
                    credit_amount=Decimal('0'),
                    entry_type='opening_balance',
                    ...
                ),
                JournalEntry(
                    account_id=equity_account.id,
                    debit_amount=Decimal('0'),
                    credit_amount=opening_balance,
                    entry_type='opening_balance',
                    ...
                )
            ]
        else:
            # Debit: Equity, Credit: Liability/Income
            entries = [
                JournalEntry(
                    account_id=equity_account.id,
                    debit_amount=opening_balance,
                    credit_amount=Decimal('0'),
                    entry_type='opening_balance',
                    ...
                ),
                JournalEntry(
                    account_id=account.id,
                    debit_amount=Decimal('0'),
                    credit_amount=opening_balance,
                    entry_type='opening_balance',
                    ...
                )
            ]

        return self.double_entry_service.create_balanced_entries(entries)
```

#### Definition of Done
- [ ] Opening Balance Equity account auto-created
- [ ] set_opening_balance() method implemented
- [ ] Journal entries created for opening balances
- [ ] Opening balances respect account normal balance
- [ ] Accounting equation validated after opening balances
- [ ] Unit tests for opening balance scenarios (8+ tests)
- [ ] Integration test: Set opening balances for 10 accounts, validate totals

#### Dependencies
- US-002 (Double-Entry Account Model)
- US-003 (Normal Balance Calculation)

---

### **US-005: Account Reconciliation Support**

**As a** user
**I want** to mark transactions as reconciled against my bank statement
**So that** I can ensure my records match the bank and catch errors

**Priority:** P1 (Should Have)
**Story Points:** 8
**Sprint:** Sprint 2

#### Acceptance Criteria

**Given** I am reconciling an account
**When** I mark journal entries as reconciled
**Then** they should be flagged as reconciled with a reconciliation date
**And** I cannot edit or delete reconciled entries without unreconciling first

**Given** I am viewing an account
**When** I look at the balance
**Then** I should see both:
  - Current balance (all entries)
  - Cleared balance (only reconciled entries)

**Given** I am reconciling to a bank statement
**When** the cleared balance matches the statement balance
**Then** the reconciliation is complete
**And** a reconciliation record is created

#### Technical Notes

**New Table:**

```sql
CREATE TABLE reconciliations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    reconciliation_date TEXT NOT NULL,
    statement_date TEXT NOT NULL,
    statement_balance REAL NOT NULL,
    cleared_balance REAL NOT NULL,
    difference REAL NOT NULL,
    is_balanced BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts (id)
);

-- Add account number field for reconciliation
ALTER TABLE accounts ADD COLUMN account_number TEXT;
ALTER TABLE accounts ADD COLUMN last_reconciled_date TEXT;
ALTER TABLE accounts ADD COLUMN last_reconciled_balance REAL;
```

**Model:**

```python
@dataclass
class Reconciliation:
    """Account reconciliation record."""
    id: Optional[int]
    account_id: int
    reconciliation_date: str
    statement_date: str
    statement_balance: Decimal
    cleared_balance: Decimal
    difference: Decimal
    is_balanced: bool
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    @property
    def is_complete(self) -> bool:
        """Check if reconciliation is complete (balanced)."""
        return abs(self.difference) < Decimal('0.01')  # Allow 1 cent difference
```

**Service Methods:**

```python
class ReconciliationService:

    def start_reconciliation(
        self,
        account_id: int,
        statement_date: str,
        statement_balance: Decimal
    ) -> Reconciliation:
        """Start a new reconciliation."""

    def mark_entry_reconciled(
        self,
        entry_id: int,
        reconciliation_id: int
    ) -> JournalEntry:
        """Mark a journal entry as reconciled."""

    def get_cleared_balance(self, account_id: int) -> Decimal:
        """Get balance of only reconciled entries."""

    def complete_reconciliation(
        self,
        reconciliation_id: int
    ) -> Reconciliation:
        """Complete and validate reconciliation."""
```

#### Definition of Done
- [ ] reconciliations table created
- [ ] Reconciliation model implemented
- [ ] ReconciliationService with reconciliation workflow
- [ ] Cannot edit/delete reconciled entries
- [ ] Cleared balance calculation works correctly
- [ ] Unit tests for reconciliation (12+ tests)
- [ ] Integration test: Complete reconciliation workflow

#### Dependencies
- US-002 (Double-Entry Account Model)

---

### **US-006: Account Status & Lifecycle**

**As a** user
**I want** to close or archive accounts I no longer use
**So that** my account list stays organized without losing historical data

**Priority:** P2 (Nice to Have)
**Story Points:** 3
**Sprint:** Sprint 2

#### Acceptance Criteria

**Given** I have an account I no longer use
**When** I archive the account
**Then** it should be hidden from the main account list
**And** all historical transactions remain accessible
**And** I cannot add new transactions to an archived account

**Given** I am viewing my accounts
**When** I choose to show archived accounts
**Then** all archived accounts should be visible with an "Archived" indicator

#### Technical Notes

**Database Changes:**

```sql
ALTER TABLE accounts ADD COLUMN status TEXT DEFAULT 'active';
  -- Values: 'active', 'inactive', 'archived', 'closed'

ALTER TABLE accounts ADD COLUMN closed_date TEXT;
ALTER TABLE accounts ADD COLUMN archived_date TEXT;
```

**Model Update:**

```python
@dataclass
class Account:
    # ... existing fields ...
    status: str = 'active'  # 'active', 'inactive', 'archived', 'closed'
    closed_date: Optional[str] = None
    archived_date: Optional[str] = None

    @property
    def is_active(self) -> bool:
        return self.status == 'active'

    @property
    def is_archived(self) -> bool:
        return self.status == 'archived'
```

**Service Methods:**

```python
class AccountService:

    def archive_account(self, account_id: int) -> Account:
        """Archive an account (hide from active list)."""

    def activate_account(self, account_id: int) -> Account:
        """Reactivate an archived account."""

    def close_account(self, account_id: int, closing_date: str) -> Account:
        """Permanently close an account (balance must be 0)."""

    def get_active_accounts(self) -> List[Account]:
        """Get only active accounts."""

    def get_all_accounts(self, include_archived: bool = False) -> List[Account]:
        """Get all accounts with optional archived filter."""
```

#### Definition of Done
- [ ] Account status field added
- [ ] Archive/activate methods implemented
- [ ] UI filters out archived accounts by default
- [ ] Cannot add transactions to archived accounts
- [ ] Unit tests for account lifecycle (8+ tests)

---

### **US-007: Account Metadata & Organization**

**As a** power user
**I want** to add notes, account numbers, and organize accounts
**So that** I can keep detailed records and stay organized

**Priority:** P2 (Nice to Have)
**Story Points:** 5
**Sprint:** Sprint 2

#### Acceptance Criteria

**Given** I am creating an account
**When** I add account metadata (account number, notes, institution)
**Then** it should be saved and displayed in the account details

**Given** I have many accounts
**When** I assign display order or favorites
**Then** accounts should be sorted accordingly in the UI

#### Technical Notes

**Database Changes:**

```sql
ALTER TABLE accounts ADD COLUMN account_number TEXT;
ALTER TABLE accounts ADD COLUMN institution_name TEXT;
ALTER TABLE accounts ADD COLUMN notes TEXT;
ALTER TABLE accounts ADD COLUMN is_favorite BOOLEAN DEFAULT 0;
ALTER TABLE accounts ADD COLUMN display_order INTEGER DEFAULT 0;
ALTER TABLE accounts ADD COLUMN color_hex TEXT DEFAULT '#3B82F6';
ALTER TABLE accounts ADD COLUMN icon TEXT;
```

**Model Update:**

```python
@dataclass
class Account:
    # ... existing fields ...
    account_number: Optional[str] = None
    institution_name: Optional[str] = None
    notes: Optional[str] = None
    is_favorite: bool = False
    display_order: int = 0
    color_hex: str = '#3B82F6'  # Default blue
    icon: Optional[str] = None
```

#### Definition of Done
- [ ] Metadata fields added to database and model
- [ ] UI displays account metadata
- [ ] Can mark accounts as favorites
- [ ] Accounts sortable by display_order
- [ ] Unit tests for metadata operations (6+ tests)

---

### **US-008: Multi-Currency Account Setup**

**As a** user with international accounts
**I want** to set currency per account
**So that** I can track accounts in different currencies

**Priority:** P3 (Could Have)
**Story Points:** 5
**Sprint:** Sprint 3

#### Acceptance Criteria

**Given** I am creating an account
**When** I select a currency (USD, EUR, GBP, etc.)
**Then** the account should store and display amounts in that currency

**Given** I have accounts in multiple currencies
**When** I view total net worth
**Then** I should see amounts in each currency separately
**Or** converted to my preferred currency (if exchange rates available)

#### Technical Notes

**Note:** Full multi-currency support with exchange rates is Feature #17 in PRD.
This story only ensures accounts CAN have different currencies.

**Validation:**

```python
class AccountValidator:

    SUPPORTED_CURRENCIES = [
        'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CNY', 'INR', 'CHF', 'SEK',
        # ... add more as needed
    ]

    def validate_currency(self, currency: str) -> str:
        """Validate currency code (ISO 4217)."""
        currency = currency.upper().strip()
        if len(currency) != 3:
            raise ValidationError("Currency code must be 3 letters")
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValidationError(f"Unsupported currency: {currency}")
        return currency
```

#### Definition of Done
- [ ] Currency validation supports 50+ currencies
- [ ] Account creation accepts currency parameter
- [ ] UI displays currency symbols correctly
- [ ] Cannot mix currencies in transfers (validation error)
- [ ] Unit tests for currency validation (10+ tests)

---

### **US-009: Account Color Coding & Visual Indicators**

**As a** user
**I want** accounts to have color-coded icons and visual indicators
**So that** I can quickly identify account types and status

**Priority:** P1 (Should Have)
**Story Points:** 5
**Sprint:** Sprint 2-3

#### Acceptance Criteria

**Given** I am viewing the account list
**When** I see accounts
**Then** each account should have:
  - Color-coded icon based on account type
  - Balance shown in color (positive=green, negative=red for assets)
  - Transaction count badge
  - Status indicator (active/archived/reconciled)

**Given** I am creating an account
**When** I select account type
**Then** a default color is assigned
**And** I can customize the color if desired

#### Technical Notes

**Default Colors by Type:**

```python
ACCOUNT_TYPE_COLORS = {
    'asset': {
        'checking': '#3B82F6',      # Blue
        'savings': '#10B981',        # Green
        'cash': '#8B5CF6',           # Purple
        'investment': '#F59E0B',     # Amber
    },
    'liability': {
        'credit_card': '#EF4444',    # Red
        'loan': '#F97316',           # Orange
        'mortgage': '#DC2626',       # Dark red
    },
    'equity': {
        'opening_balance': '#6B7280',  # Gray
    },
    'income': {
        'salary': '#10B981',         # Green
        'business_income': '#059669', # Dark green
    },
    'expense': {
        'default': '#DC2626',        # Red
    }
}
```

**Repository Method:**

```python
class AccountRepository:

    def get_account_summary(self, account_id: int) -> Dict:
        """
        Get account summary with transaction count.

        Returns:
            {
                'account': Account,
                'transaction_count': int,
                'last_transaction_date': str,
                'reconciled_count': int,
                'pending_count': int
            }
        """
```

**UI Component:**

```python
class AccountListItem(QWidget):
    """Custom widget for displaying account in list."""

    def __init__(self, account: Account, summary: Dict):
        # Display account icon with color
        # Show account name and balance
        # Show transaction count badge
        # Show status indicators
```

#### Definition of Done
- [ ] Color field added to accounts
- [ ] Default colors assigned by account type
- [ ] Account list shows color-coded icons
- [ ] Transaction count displayed per account
- [ ] Status indicators visible (archived, needs reconciliation)
- [ ] UI tests for account display
- [ ] Accessibility: colors meet contrast requirements

#### Dependencies
- US-007 (Account Metadata) for color_hex field

---

### **US-010: Account Balance Validation & Integrity**

**As a** system
**I want** to automatically validate account balances against journal entries
**So that** data integrity is maintained at all times

**Priority:** P0 (Must Have)
**Story Points:** 8
**Sprint:** Sprint 1-2

#### Acceptance Criteria

**Given** any account operation completes
**When** journal entries are created or modified
**Then** the account cached balance must equal the sum of journal entries
**And** if they don't match, raise a DataIntegrityError

**Given** the application starts up
**When** database is loaded
**Then** all account balances should be validated
**And** any discrepancies should be logged and optionally fixed

**Given** I run a balance validation report
**When** I request validation
**Then** I should see a report of all accounts showing:
  - Cached balance
  - Calculated balance (from journal entries)
  - Difference (if any)
  - Last validation timestamp

#### Technical Notes

**Validation Service:**

```python
class AccountBalanceValidator:
    """Service for validating account balance integrity."""

    def validate_account_balance(self, account_id: int) -> ValidationResult:
        """
        Validate single account balance.

        Returns:
            ValidationResult with status and details
        """
        account = self.account_repo.get_by_id(account_id)
        calculated_balance = self.journal_repo.get_account_balance(account_id)

        difference = account.balance - calculated_balance

        return ValidationResult(
            account_id=account_id,
            cached_balance=account.balance,
            calculated_balance=calculated_balance,
            difference=difference,
            is_valid=abs(difference) < Decimal('0.01'),  # Allow 1 cent rounding
            validated_at=datetime.now()
        )

    def validate_all_accounts(self) -> List[ValidationResult]:
        """Validate all account balances."""

    def fix_account_balance(self, account_id: int) -> Account:
        """Fix account balance to match journal entries."""

    def get_trial_balance(self) -> TrialBalance:
        """
        Generate trial balance report.

        Returns all accounts with debit and credit balances.
        Total debits must equal total credits.
        """

@dataclass
class ValidationResult:
    account_id: int
    cached_balance: Decimal
    calculated_balance: Decimal
    difference: Decimal
    is_valid: bool
    validated_at: datetime

@dataclass
class TrialBalance:
    report_date: str
    accounts: List[TrialBalanceEntry]
    total_debits: Decimal
    total_credits: Decimal
    is_balanced: bool

@dataclass
class TrialBalanceEntry:
    account_id: int
    account_name: str
    account_type: str
    debit_balance: Decimal
    credit_balance: Decimal
```

**Database Trigger for Auto-Validation:**

```sql
-- Trigger to update account balance when journal entry added
CREATE TRIGGER update_account_balance_on_journal_entry
AFTER INSERT ON journal_entries
BEGIN
    UPDATE accounts
    SET balance = balance + (NEW.debit_amount - NEW.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.account_id;
END;

-- Trigger to validate balance doesn't go negative for asset accounts
CREATE TRIGGER validate_asset_balance
AFTER UPDATE OF balance ON accounts
BEGIN
    SELECT CASE
        WHEN NEW.account_type = 'asset' AND NEW.balance < 0 THEN
            RAISE(ABORT, 'Asset account balance cannot be negative')
    END;
END;
```

**Scheduled Validation:**

```python
class BackgroundTasks:

    @schedule.every().day.at("02:00")
    def nightly_balance_validation():
        """Run balance validation every night."""
        validator = AccountBalanceValidator(db)
        results = validator.validate_all_accounts()

        # Log any discrepancies
        failed = [r for r in results if not r.is_valid]
        if failed:
            logger.error(f"Balance validation failed for {len(failed)} accounts")
            # Send notification to user
```

#### Definition of Done
- [ ] AccountBalanceValidator service implemented
- [ ] validate_account_balance() method works correctly
- [ ] validate_all_accounts() validates entire database
- [ ] fix_account_balance() can repair discrepancies
- [ ] get_trial_balance() generates accurate trial balance report
- [ ] Database triggers update balances automatically
- [ ] Validation runs on application startup
- [ ] Unit tests for validation logic (15+ tests)
- [ ] Integration test: Create 100 entries, validate all balances
- [ ] Performance: Validate 10,000 accounts in < 5 seconds

#### Dependencies
- US-002 (Double-Entry Account Model)

---

## 📊 Epic Metrics & Success Criteria

### Functional Metrics
- ✅ All 10 user stories completed with acceptance criteria met
- ✅ 100% of PRD Feature #1 requirements implemented
- ✅ Double-entry foundation ready for Feature #2
- ✅ Zero balance discrepancies (cached = calculated)
- ✅ Support for 50+ accounts without performance issues

### Technical Metrics
- ✅ Test coverage > 80% for account module
- ✅ All account operations < 100ms response time
- ✅ Zero data loss during account operations
- ✅ Database migrations tested and reversible
- ✅ All code reviewed and approved

### User Experience Metrics
- ✅ Account creation takes < 30 seconds
- ✅ Account list loads in < 200ms
- ✅ Color-coding improves account recognition (user testing)
- ✅ Reconciliation workflow is intuitive (user testing)

---

## 🔗 Dependencies

### Blocking Dependencies (Must Complete Before This Epic)
- None (this is the foundation)

### This Epic Blocks
- **Epic 2: Double-Entry Transactions** (requires US-002)
- **Epic 3: Asset Transfers** (requires US-002, US-003)
- **Epic 4: Account Reconciliation** (requires US-005)
- **Epic 5: Reports & Analytics** (requires US-010 trial balance)

---

## ⚠️ Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Data migration fails** | Medium | High | Comprehensive testing, backup before migration, rollback plan |
| **Balance discrepancies** | Medium | High | Automated validation, database constraints, extensive testing |
| **Performance with many accounts** | Low | Medium | Database indexing, pagination, performance testing |
| **User confusion with account types** | Medium | Low | Clear UI labels, tooltips, onboarding wizard |
| **Double-entry complexity** | Low | High | Hide complexity in service layer, simple UI |

---

## 📅 Timeline

### Sprint 1 (Week 1)
- **Days 1-2:** US-001 (Account Type Taxonomy)
- **Days 3-5:** US-002 (Double-Entry Model) - Part 1

### Sprint 2 (Week 2)
- **Days 1-2:** US-002 (Double-Entry Model) - Part 2
- **Day 3:** US-003 (Normal Balance)
- **Days 4-5:** US-004 (Opening Balances)

### Sprint 3 (Week 3)
- **Days 1-2:** US-010 (Balance Validation)
- **Days 3-4:** US-005 (Reconciliation Support)
- **Day 5:** US-009 (Color Coding & UI)

### Optional (Week 4)
- **Days 1-2:** US-006 (Account Status)
- **Days 2-3:** US-007 (Account Metadata)
- **Days 4-5:** US-008 (Multi-Currency) + Polish

---

## 🎯 Definition of Done (Epic Level)

This epic is considered DONE when:

- [ ] All 10 user stories completed and accepted
- [ ] All acceptance criteria met and tested
- [ ] Database schema updated with migrations
- [ ] All models, repositories, and services implemented
- [ ] Unit test coverage > 80%
- [ ] Integration tests passing
- [ ] Performance benchmarks met
- [ ] Code reviewed and approved
- [ ] Documentation updated (README, API docs, user guide)
- [ ] Manual testing completed
- [ ] No critical or high-priority bugs
- [ ] Demo to stakeholders completed and approved
- [ ] Architecture document updated

---

## 📚 Related Documentation

- [Product Requirements Document](../prd.md) - Feature #1 & Feature #2
- [Architecture Document](../ARCHITECTURE.md) - Will be updated with double-entry design
- [Database Schema](../database-schema.md) - Will be created
- [API Reference](../api-reference.md) - Will be updated

---

## 🔄 Epic Review & Retrospective

**To be completed after epic:**

### What Went Well
- TBD

### What Could Be Improved
- TBD

### Action Items for Next Epic
- TBD

---

**Epic Owner:** Development Team
**Product Owner:** Product Owner Agent
**Tech Lead:** Tech Lead Agent
**QA Lead:** TBD

**Epic Created:** October 22, 2025
**Epic Started:** TBD
**Epic Completed:** TBD

---

*This epic document is a living document and will be updated throughout development.*
