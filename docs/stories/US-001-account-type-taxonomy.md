# US-001: Account Type Taxonomy & Hierarchy

**Story ID:** US-001
**Epic:** [EPIC-001 - Account Management & Double-Entry Foundation](../epics/epic-01-account-management.md)
**Status:** 📋 Ready for Development
**Priority:** P0 (Must Have - Blocking)
**Story Points:** 8
**Sprint:** Sprint 1
**Assignee:** TBD
**Created:** October 22, 2025

---

## 📖 User Story

**As a** power user
**I want** accounts organized by accounting type (Assets, Liabilities, Equity, Income, Expenses) with subtypes
**So that** I can use proper accounting categories while seeing familiar account names

---

## 🎯 Business Value

- Establishes foundation for professional double-entry accounting
- Enables accurate financial reporting (Balance Sheet, P&L)
- Supports both personal finance and small business use cases
- Maintains user-friendly interface while using proper accounting taxonomy

---

## ✅ Acceptance Criteria

### AC1: Account Type Selection
**Given** I am creating a new account
**When** I select account type
**Then** I should see 5 primary types:
- **Assets** (Checking, Savings, Cash, Investment, Other Asset)
- **Liabilities** (Credit Card, Loan, Mortgage, Line of Credit, Other Liability)
- **Equity** (Opening Balance, Retained Earnings)
- **Income** (Salary, Business Income, Interest, Dividends, Other Income)
- **Expenses** (Auto-created from categories)

**And** each primary type has relevant subtypes
**And** the subtype determines the account's normal balance (debit/credit)

### AC2: Account Grouping
**Given** I am viewing my accounts
**When** I look at the account list
**Then** accounts are grouped by primary type
**And** subtypes are shown as descriptive labels (e.g., "Checking Account" not "Asset")

### AC3: Normal Balance Auto-Assignment
**Given** I create an account with type "asset" and subtype "checking"
**When** the account is saved
**Then** normal_balance should be automatically set to "debit"

**Given** I create an account with type "liability" and subtype "credit_card"
**When** the account is saved
**Then** normal_balance should be automatically set to "credit"

### AC4: Validation Rules
**Given** I am creating an account
**When** I select an invalid subtype for the account type
**Then** I should receive a validation error
**And** the account should not be created

**Example:** Cannot create account_type="asset" with account_subtype="credit_card"

---

## 🔧 Technical Implementation

### Database Changes

```sql
-- Migration: Add double-entry account type fields
-- File: migrations/001_add_account_types.sql

-- Step 1: Add new columns
ALTER TABLE accounts ADD COLUMN account_type TEXT NOT NULL DEFAULT 'asset';
  -- Values: 'asset', 'liability', 'equity', 'income', 'expense'

ALTER TABLE accounts ADD COLUMN account_subtype TEXT NOT NULL DEFAULT 'checking';
  -- Values: 'checking', 'savings', 'cash', 'credit_card', 'loan', etc.

ALTER TABLE accounts ADD COLUMN normal_balance TEXT NOT NULL DEFAULT 'debit';
  -- Values: 'debit', 'credit'

ALTER TABLE accounts ADD COLUMN parent_account_id INTEGER;
  -- For hierarchical accounts (future use)

-- Step 2: Create constraints
CREATE INDEX idx_accounts_type ON accounts(account_type);
CREATE INDEX idx_accounts_subtype ON accounts(account_subtype);

-- Step 3: Rename old 'type' column for backward compatibility
ALTER TABLE accounts RENAME COLUMN type TO legacy_type;

-- Step 4: Add foreign key for parent accounts (future)
-- Foreign key will be added when needed
```

### Data Migration

```python
# Migration script: migrate_account_types.py

LEGACY_TYPE_MAPPING = {
    'bank': {
        'account_type': 'asset',
        'account_subtype': 'checking',
        'normal_balance': 'debit'
    },
    'cash': {
        'account_type': 'asset',
        'account_subtype': 'cash',
        'normal_balance': 'debit'
    },
    'credit': {
        'account_type': 'liability',
        'account_subtype': 'credit_card',
        'normal_balance': 'credit'
    },
    'investment': {
        'account_type': 'asset',
        'account_subtype': 'investment',
        'normal_balance': 'debit'
    }
}

def migrate_existing_accounts(db: Database):
    """Migrate existing accounts to new type system."""
    accounts = db.execute("SELECT id, legacy_type FROM accounts")

    for account in accounts:
        mapping = LEGACY_TYPE_MAPPING.get(account['legacy_type'])
        if mapping:
            db.execute("""
                UPDATE accounts
                SET account_type = ?,
                    account_subtype = ?,
                    normal_balance = ?
                WHERE id = ?
            """, (
                mapping['account_type'],
                mapping['account_subtype'],
                mapping['normal_balance'],
                account['id']
            ))
```

### Model Changes

```python
# File: finance_app/data/models.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from datetime import datetime


class AccountType(str, Enum):
    """Primary account types."""
    ASSET = 'asset'
    LIABILITY = 'liability'
    EQUITY = 'equity'
    INCOME = 'income'
    EXPENSE = 'expense'


class AccountSubtype(str, Enum):
    """Account subtypes."""
    # Asset subtypes
    CHECKING = 'checking'
    SAVINGS = 'savings'
    CASH = 'cash'
    INVESTMENT = 'investment'
    OTHER_ASSET = 'other_asset'

    # Liability subtypes
    CREDIT_CARD = 'credit_card'
    LOAN = 'loan'
    MORTGAGE = 'mortgage'
    LINE_OF_CREDIT = 'line_of_credit'
    OTHER_LIABILITY = 'other_liability'

    # Equity subtypes
    OPENING_BALANCE = 'opening_balance'
    RETAINED_EARNINGS = 'retained_earnings'

    # Income subtypes
    SALARY = 'salary'
    BUSINESS_INCOME = 'business_income'
    INTEREST = 'interest'
    DIVIDENDS = 'dividends'
    OTHER_INCOME = 'other_income'

    # Expense subtypes (typically use category names)
    EXPENSE_CATEGORY = 'expense_category'


class NormalBalance(str, Enum):
    """Normal balance type."""
    DEBIT = 'debit'
    CREDIT = 'credit'


@dataclass
class Account:
    """Account model with double-entry support."""
    id: Optional[int]
    name: str
    account_type: AccountType
    account_subtype: AccountSubtype
    balance: Decimal
    normal_balance: NormalBalance
    currency: str = 'USD'
    parent_account_id: Optional[int] = None
    legacy_type: Optional[str] = None  # For migration
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Ensure balance is Decimal and types are enums."""
        if not isinstance(self.balance, Decimal):
            self.balance = Decimal(str(self.balance))

        if isinstance(self.account_type, str):
            self.account_type = AccountType(self.account_type)

        if isinstance(self.account_subtype, str):
            self.account_subtype = AccountSubtype(self.account_subtype)

        if isinstance(self.normal_balance, str):
            self.normal_balance = NormalBalance(self.normal_balance)
```

### Validation Logic

```python
# File: finance_app/business/validators.py

class AccountValidator:
    """Validator for account operations."""

    # Valid subtype combinations
    VALID_SUBTYPES = {
        AccountType.ASSET: [
            AccountSubtype.CHECKING,
            AccountSubtype.SAVINGS,
            AccountSubtype.CASH,
            AccountSubtype.INVESTMENT,
            AccountSubtype.OTHER_ASSET,
        ],
        AccountType.LIABILITY: [
            AccountSubtype.CREDIT_CARD,
            AccountSubtype.LOAN,
            AccountSubtype.MORTGAGE,
            AccountSubtype.LINE_OF_CREDIT,
            AccountSubtype.OTHER_LIABILITY,
        ],
        AccountType.EQUITY: [
            AccountSubtype.OPENING_BALANCE,
            AccountSubtype.RETAINED_EARNINGS,
        ],
        AccountType.INCOME: [
            AccountSubtype.SALARY,
            AccountSubtype.BUSINESS_INCOME,
            AccountSubtype.INTEREST,
            AccountSubtype.DIVIDENDS,
            AccountSubtype.OTHER_INCOME,
        ],
        AccountType.EXPENSE: [
            AccountSubtype.EXPENSE_CATEGORY,
        ],
    }

    # Normal balance by account type
    NORMAL_BALANCE_MAP = {
        AccountType.ASSET: NormalBalance.DEBIT,
        AccountType.EXPENSE: NormalBalance.DEBIT,
        AccountType.LIABILITY: NormalBalance.CREDIT,
        AccountType.EQUITY: NormalBalance.CREDIT,
        AccountType.INCOME: NormalBalance.CREDIT,
    }

    def validate_account_type_combination(
        self,
        account_type: AccountType,
        account_subtype: AccountSubtype
    ) -> tuple[AccountType, AccountSubtype]:
        """
        Validate account type and subtype combination.

        Args:
            account_type: Primary account type
            account_subtype: Account subtype

        Returns:
            Validated (account_type, account_subtype) tuple

        Raises:
            ValidationError: If combination is invalid
        """
        if account_subtype not in self.VALID_SUBTYPES.get(account_type, []):
            valid_subtypes = ', '.join(
                [s.value for s in self.VALID_SUBTYPES[account_type]]
            )
            raise ValidationError(
                f"Invalid subtype '{account_subtype.value}' for account type "
                f"'{account_type.value}'. Valid subtypes: {valid_subtypes}"
            )

        return account_type, account_subtype

    def get_normal_balance(self, account_type: AccountType) -> NormalBalance:
        """
        Get normal balance for account type.

        Args:
            account_type: Account type

        Returns:
            Normal balance (debit or credit)
        """
        return self.NORMAL_BALANCE_MAP[account_type]
```

### Service Layer Changes

```python
# File: finance_app/business/account_service.py

class AccountService:
    """Service for account business logic."""

    def create_account(
        self,
        name: str,
        account_type: AccountType,
        account_subtype: AccountSubtype,
        initial_balance: str = "0.00",
        currency: str = "USD"
    ) -> Account:
        """
        Create a new account with validation.

        Args:
            name: Account name
            account_type: Primary account type
            account_subtype: Account subtype
            initial_balance: Initial balance as string
            currency: Currency code

        Returns:
            Created account

        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        validated_name = self.validator.validate_name(name)
        validated_type, validated_subtype = self.validator.validate_account_type_combination(
            account_type, account_subtype
        )
        validated_currency = self.validator.validate_currency(currency)

        # Get normal balance
        normal_balance = self.validator.get_normal_balance(account_type)

        # Parse balance
        try:
            balance = Decimal(initial_balance)
            validated_balance = self.validator.validate_balance(
                balance, allow_negative=(normal_balance == NormalBalance.CREDIT)
            )
        except Exception as e:
            raise ValidationError(f"Invalid initial balance: {initial_balance}") from e

        # Create account object
        account = Account(
            id=None,
            name=validated_name,
            account_type=validated_type,
            account_subtype=validated_subtype,
            balance=validated_balance,
            normal_balance=normal_balance,
            currency=validated_currency
        )

        # Save account
        created_account = self.account_repo.create(account)
        logger.info(
            f"Account created: {created_account.name} "
            f"({created_account.account_type.value}/{created_account.account_subtype.value})"
        )

        return created_account
```

---

## 🧪 Test Scenarios

### Test 1: Create Asset Account
```python
def test_create_asset_checking_account(account_service):
    """Test creating a checking account (asset)."""
    account = account_service.create_account(
        name="My Checking",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        initial_balance="1000.00"
    )

    assert account.id is not None
    assert account.name == "My Checking"
    assert account.account_type == AccountType.ASSET
    assert account.account_subtype == AccountSubtype.CHECKING
    assert account.normal_balance == NormalBalance.DEBIT
    assert account.balance == Decimal("1000.00")
```

### Test 2: Create Liability Account
```python
def test_create_liability_credit_card_account(account_service):
    """Test creating a credit card account (liability)."""
    account = account_service.create_account(
        name="Visa Card",
        account_type=AccountType.LIABILITY,
        account_subtype=AccountSubtype.CREDIT_CARD,
        initial_balance="0.00"
    )

    assert account.account_type == AccountType.LIABILITY
    assert account.account_subtype == AccountSubtype.CREDIT_CARD
    assert account.normal_balance == NormalBalance.CREDIT
```

### Test 3: Invalid Subtype Validation
```python
def test_invalid_subtype_combination(account_service):
    """Test that invalid subtype for account type raises error."""
    with pytest.raises(ValidationError) as exc_info:
        account_service.create_account(
            name="Invalid Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CREDIT_CARD  # Invalid for assets
        )

    assert "Invalid subtype" in str(exc_info.value)
```

### Test 4: Normal Balance Auto-Assignment
```python
@pytest.mark.parametrize("account_type,expected_normal_balance", [
    (AccountType.ASSET, NormalBalance.DEBIT),
    (AccountType.EXPENSE, NormalBalance.DEBIT),
    (AccountType.LIABILITY, NormalBalance.CREDIT),
    (AccountType.EQUITY, NormalBalance.CREDIT),
    (AccountType.INCOME, NormalBalance.CREDIT),
])
def test_normal_balance_assignment(account_service, account_type, expected_normal_balance):
    """Test normal balance is correctly assigned for each account type."""
    # Get valid subtype for this account type
    valid_subtypes = AccountValidator.VALID_SUBTYPES[account_type]
    subtype = valid_subtypes[0]

    account = account_service.create_account(
        name=f"Test {account_type.value}",
        account_type=account_type,
        account_subtype=subtype
    )

    assert account.normal_balance == expected_normal_balance
```

### Test 5: Data Migration
```python
def test_migrate_legacy_accounts(db):
    """Test migration from legacy account types."""
    # Create legacy account
    db.execute("""
        INSERT INTO accounts (name, type, balance)
        VALUES ('Old Checking', 'bank', 500.00)
    """)

    # Run migration
    migrate_existing_accounts(db)

    # Verify migration
    account = db.execute("""
        SELECT account_type, account_subtype, normal_balance
        FROM accounts
        WHERE name = 'Old Checking'
    """).fetchone()

    assert account['account_type'] == 'asset'
    assert account['account_subtype'] == 'checking'
    assert account['normal_balance'] == 'debit'
```

---

## 📋 Tasks Breakdown

- [ ] **Task 1.1:** Create database migration script (2 hours)
  - Add new columns to accounts table
  - Create indexes
  - Rename legacy_type column

- [ ] **Task 1.2:** Create data migration script (2 hours)
  - Map old types to new taxonomy
  - Test migration with sample data
  - Create rollback script

- [ ] **Task 1.3:** Update data models (3 hours)
  - Add AccountType, AccountSubtype, NormalBalance enums
  - Update Account dataclass
  - Add validation in __post_init__

- [ ] **Task 1.4:** Update validators (3 hours)
  - Add VALID_SUBTYPES mapping
  - Add NORMAL_BALANCE_MAP
  - Implement validate_account_type_combination()
  - Implement get_normal_balance()

- [ ] **Task 1.5:** Update AccountService (2 hours)
  - Modify create_account() to use new types
  - Auto-assign normal_balance
  - Update all method signatures

- [ ] **Task 1.6:** Update AccountRepository (2 hours)
  - Handle new enum types in _row_to_account()
  - Update CREATE/UPDATE queries
  - Add conversion logic

- [ ] **Task 1.7:** Write unit tests (4 hours)
  - Test all account type combinations
  - Test validation errors
  - Test normal balance assignment
  - Test migration script

- [ ] **Task 1.8:** Update UI (optional for this story) (4 hours)
  - Update account creation dialog
  - Add account type dropdown
  - Add subtype dropdown (filtered by type)
  - Update account list grouping

- [ ] **Task 1.9:** Documentation (1 hour)
  - Update architecture document
  - Document account type taxonomy
  - Add examples to README

**Total Estimated Time:** 23 hours (approx. 3 days)

---

## 🔗 Dependencies

### Blocked By
- None (foundational story)

### Blocks
- US-002 (Double-Entry Account Model) - needs account types
- US-003 (Normal Balance Calculation) - needs normal_balance field
- All other stories in Epic 1

---

## ✅ Definition of Done

- [ ] Database migration script created and tested
- [ ] Data migration script successfully migrates existing accounts
- [ ] Account model updated with new fields and enums
- [ ] AccountValidator validates type/subtype combinations
- [ ] Normal balance auto-assigned on account creation
- [ ] AccountService uses new account type system
- [ ] All unit tests passing (15+ tests)
- [ ] Integration test: Create account of each type/subtype
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Manual testing completed
- [ ] No regressions in existing functionality

---

## 📚 References

- [Epic 01: Account Management](../epics/epic-01-account-management.md)
- [PRD: Feature #1 - Account Management](../prd.md#1-account-management)
- [PRD: Feature #2 - Double-Entry Accounting](../prd.md#2-double-entry-accounting-system)
- [Architecture: Data Models](../ARCHITECTURE.md#data-models)

---

## 📝 Notes

- This story establishes the foundation for double-entry accounting
- Keep UI simple: Users see "Checking Account" not "Asset/Checking"
- Legacy accounts will be migrated automatically
- Parent/child account hierarchy is planned but not implemented yet

---

**Story Created:** October 22, 2025
**Story Started:** TBD
**Story Completed:** TBD
**Story Accepted:** TBD
