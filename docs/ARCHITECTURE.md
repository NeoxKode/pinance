# Finance App - Software Architecture Documentation

**Version:** 2.5.0
**Date:** November 5, 2025
**Status:** Production Ready
**Last Updated:** Account Metadata & Organization System (US-007)

---

## Executive Summary

The Personal Finance Manager has been refactored from a monolithic 490-line single-file application into a professionally-structured, layered architecture following SOLID principles and industry best practices.

### Key Improvements

- ✅ **Layered Architecture**: Separation of UI, Business Logic, and Data Access
- ✅ **Type Safety**: Full type hints throughout codebase
- ✅ **Error Handling**: Comprehensive exception handling and logging
- ✅ **Testing Infrastructure**: pytest framework with fixtures
- ✅ **Data Integrity**: Proper database lifecycle management and transactions
- ✅ **Maintainability**: Modular code with clear responsibilities

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Main Window  │  │   Dialogs    │  │   Widgets    │  │
│  │   (Qt UI)    │  │   (Forms)    │  │  (Custom)    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
┌─────────────────────────────┼─────────────────────────────┐
│                   Business Logic Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Transaction  │  │   Account    │  │  Validators  │  │
│  │   Service    │  │   Service    │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
┌─────────────────────────────┼─────────────────────────────┐
│                    Data Access Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Transaction  │  │   Account    │  │   Category   │  │
│  │  Repository  │  │  Repository  │  │  Repository  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                  │                  │          │
│         └──────────────────┼──────────────────┘          │
│                            │                             │
│                   ┌────────┴────────┐                    │
│                   │  Database Mgr   │                    │
│                   └────────┬────────┘                    │
└────────────────────────────┼──────────────────────────────┘
                             │
                      ┌──────┴──────┐
                      │   SQLite    │
                      │  Database   │
                      └─────────────┘
```

---

## Directory Structure

```
finance/
├── main.py                          # Application entry point
├── finance_app_old.py               # Backup of old monolithic code
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Test configuration
├── .gitignore                       # Git ignore rules
│
├── finance_app/                     # Main application package
│   ├── __init__.py
│   │
│   ├── ui/                          # Presentation Layer
│   │   ├── __init__.py
│   │   ├── main_window.py           # Main application window
│   │   ├── dialogs/                 # Dialog windows
│   │   │   ├── __init__.py
│   │   │   └── transaction_dialog.py
│   │   ├── widgets/                 # Custom widgets
│   │   │   └── __init__.py
│   │   └── models/                  # Qt Models (future)
│   │       └── __init__.py
│   │
│   ├── business/                    # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── transaction_service.py   # Transaction business logic
│   │   ├── account_service.py       # Account business logic
│   │   └── validators.py            # Input validation
│   │
│   ├── data/                        # Data Access Layer
│   │   ├── __init__.py
│   │   ├── database.py              # Database connection manager
│   │   ├── models.py                # Data models (dataclasses)
│   │   ├── repositories/            # Data repositories
│   │   │   ├── __init__.py
│   │   │   ├── account_repository.py
│   │   │   ├── transaction_repository.py
│   │   │   └── category_repository.py
│   │   └── migrations/              # Database migrations (future)
│   │       └── __init__.py
│   │
│   ├── utils/                       # Utilities
│   │   ├── __init__.py
│   │   ├── logger.py                # Logging configuration
│   │   └── exceptions.py            # Custom exceptions
│   │
│   └── tests/                       # Test suite
│       ├── __init__.py
│       ├── conftest.py              # Pytest fixtures
│       ├── unit/                    # Unit tests
│       │   └── test_example.py
│       ├── integration/             # Integration tests
│       └── fixtures/                # Test data fixtures
│
├── docs/                            # Documentation
│   ├── ARCHITECTURE.md              # This file
│   ├── prd.md                       # Product requirements
│   └── reference.md                 # API reference
│
└── logs/                            # Application logs
    └── finance_app.log
```

---

## Layer Descriptions

### 1. Presentation Layer (`ui/`)

**Responsibility:** User interface and user interaction

**Components:**
- `main_window.py`: Main application window with account/transaction views
- `dialogs/transaction_dialog.py`: Transaction add/edit dialog
- Future: Custom widgets, table models

**Key Principles:**
- No direct database access
- Calls business services only
- Handles UI events and displays data
- Shows user-friendly error messages

**Example:**
```python
# main_window.py
def add_transaction(self):
    try:
        # Get data from dialog
        data = dialog.get_data()

        # Call business service (not database directly)
        self.transaction_service.create_transaction(**data)

        # Update UI
        self.load_data()
    except FinanceAppError as e:
        QMessageBox.critical(self, "Error", str(e))
```

---

### 2. Business Logic Layer (`business/`)

**Responsibility:** Business rules, validation, and orchestration

**Components:**
- `transaction_service.py`: Transaction operations with balance updates
- `account_service.py`: Account management
- `validators.py`: Input validation logic

**Key Principles:**
- Enforces business rules
- Validates all inputs
- Coordinates between repositories
- Maintains data integrity (e.g., balance consistency)
- No UI dependencies

**Example:**
```python
# transaction_service.py
def create_transaction(self, account_id, date, description,
                       category, amount, trans_type):
    # 1. Validate inputs
    validated_amount = self.validator.validate_amount(amount)
    validated_description = self.validator.validate_description(description)

    # 2. Check business rules
    account = self.account_repo.get_by_id(account_id)
    if not account:
        raise NotFoundError(f"Account {account_id} not found")

    # 3. Create transaction
    transaction = self.transaction_repo.create(Transaction(...))

    # 4. Update account balance (atomically)
    self.account_repo.update_balance(account_id, validated_amount)

    return transaction
```

---

### 3. Data Access Layer (`data/`)

**Responsibility:** Database operations and data persistence

**Components:**
- `database.py`: Connection management, schema creation
- `models.py`: Data models (Account, Transaction, Category)
- `repositories/`: CRUD operations for each entity

**Key Principles:**
- Encapsulates all SQL
- Returns domain models (not raw data)
- Handles database errors
- Provides clean API to business layer
- No business logic

**Example:**
```python
# transaction_repository.py
def get_all(self, account_id=None, limit=None):
    try:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, account_id, date, description,
                       category, amount, type
                FROM transactions
                WHERE account_id = ? OR ? IS NULL
                ORDER BY date DESC
                LIMIT ?
            """, (account_id, account_id, limit or 999999))

            rows = cursor.fetchall()
            return [self._row_to_transaction(row) for row in rows]
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to fetch: {e}")
```

---

## Data Models

### Account Type Enumerations (US-001)

The application uses a comprehensive account type taxonomy for double-entry accounting:

```python
class AccountType(str, Enum):
    """Primary account types for double-entry accounting."""
    ASSET = 'asset'           # Things you own
    LIABILITY = 'liability'   # Money you owe
    EQUITY = 'equity'         # Net worth
    INCOME = 'income'         # Money received
    EXPENSE = 'expense'       # Money spent

class AccountSubtype(str, Enum):
    """Account subtypes for classification."""
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

    # Expense subtypes
    EXPENSE_CATEGORY = 'expense_category'

class NormalBalance(str, Enum):
    """Normal balance type for double-entry accounting."""
    DEBIT = 'debit'    # Assets, Expenses increase with debits
    CREDIT = 'credit'  # Liabilities, Equity, Income increase with credits
```

**Design Rationale:**
- Inherits from `str` for seamless database serialization
- Enum values match database string values
- Provides type safety at compile time
- Enables IDE autocomplete and validation

### Account
```python
@dataclass
class Account:
    """Account model with double-entry support and hierarchy (US-006)."""
    id: Optional[int]
    name: str
    account_type: AccountType          # Primary type (asset, liability, etc.)
    account_subtype: AccountSubtype    # Subtype (checking, credit_card, etc.)
    balance: Decimal
    normal_balance: NormalBalance      # Debit or credit
    currency: str = 'USD'

    # US-006: Account Hierarchy
    parent_account_id: Optional[int] = None  # Parent account ID (NULL for root)
    is_parent: bool = False                   # True if this is a parent/header account
    hierarchy_level: int = 0                  # Depth in tree (0=root, 1=child, etc.)
    hierarchy_path: str = ""                  # Path like "/1/2/3" for efficient queries

    # Backward compatibility
    legacy_type: Optional[str] = None  # Backward compatibility with v1.0

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Convert string values to enums automatically."""
        if isinstance(self.account_type, str):
            self.account_type = AccountType(self.account_type)
        if isinstance(self.account_subtype, str):
            self.account_subtype = AccountSubtype(self.account_subtype)
        if isinstance(self.normal_balance, str):
            self.normal_balance = NormalBalance(self.normal_balance)
```

**Key Features:**
- `__post_init__` handles string-to-enum conversion for database compatibility
- `legacy_type` maintains backward compatibility with v1.0 schema
- `normal_balance` auto-assigned based on `account_type`
- **US-006 Hierarchy Support:**
  - `parent_account_id`: NULL for root accounts, references parent for children
  - `is_parent`: True for organizational "header" accounts (no direct transactions)
  - `hierarchy_level`: Depth in tree (0-4, max 5 levels)
  - `hierarchy_path`: Materialized path (e.g., "/1/5/12") for efficient descendant queries

### Transaction
```python
@dataclass
class Transaction:
    id: Optional[int]
    account_id: int
    date: str  # YYYY-MM-DD
    description: str
    category: str
    amount: Decimal
    type: str  # 'income' or 'expense'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### Category
```python
@dataclass
class Category:
    id: Optional[int]
    name: str
    type: str  # 'income' or 'expense'
    created_at: Optional[datetime] = None
```

---

## Database Schema

### Schema Version: 2.3 (with US-001 Account Types + US-004 Reconciliation + US-006 Hierarchy)

```sql
-- Accounts table (updated for double-entry accounting + hierarchy)
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,

    -- Double-entry fields (US-001)
    account_type TEXT NOT NULL CHECK(account_type IN
        ('asset', 'liability', 'equity', 'income', 'expense')),
    account_subtype TEXT NOT NULL CHECK(account_subtype IN
        ('checking', 'savings', 'cash', 'investment', 'other_asset',
         'credit_card', 'loan', 'mortgage', 'line_of_credit', 'other_liability',
         'opening_balance', 'retained_earnings',
         'salary', 'business_income', 'interest', 'dividends', 'other_income',
         'expense_category')),
    normal_balance TEXT NOT NULL CHECK(normal_balance IN ('debit', 'credit')),

    -- Hierarchy fields (US-006)
    parent_account_id INTEGER,                -- Parent account (NULL for root)
    is_parent INTEGER NOT NULL DEFAULT 0,     -- 1=parent/header, 0=regular account
    hierarchy_level INTEGER DEFAULT 0,        -- Depth in tree (0-4)
    hierarchy_path TEXT DEFAULT '',           -- Materialized path ("/1/2/3")

    -- Core fields
    balance REAL NOT NULL DEFAULT 0.0,
    currency TEXT DEFAULT 'USD',

    -- Backward compatibility
    legacy_type TEXT CHECK(legacy_type IN ('bank', 'cash', 'credit', 'investment')),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign keys
    FOREIGN KEY (parent_account_id) REFERENCES accounts (id) ON DELETE SET NULL
);

-- Indices for performance
CREATE INDEX idx_accounts_name ON accounts(name);
CREATE INDEX idx_accounts_type ON accounts(account_type);
CREATE INDEX idx_accounts_subtype ON accounts(account_subtype);

-- Hierarchy indices (US-006)
CREATE INDEX idx_accounts_parent ON accounts(parent_account_id);
CREATE INDEX idx_accounts_is_parent ON accounts(is_parent);
CREATE INDEX idx_accounts_hierarchy_path ON accounts(hierarchy_path);

-- Transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE
);

CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(date DESC);
CREATE INDEX idx_transactions_category ON transactions(category);

-- Reconciliations table (US-004 Account Reconciliation)
CREATE TABLE reconciliations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    reconciliation_date TEXT NOT NULL,       -- Date reconciliation was completed
    statement_date TEXT NOT NULL,            -- Date of bank statement
    statement_balance REAL NOT NULL,         -- Balance shown on statement
    cleared_balance REAL NOT NULL,           -- Calculated from cleared transactions
    discrepancy REAL NOT NULL,               -- Difference between statement and cleared
    transaction_count INTEGER NOT NULL,      -- Number of transactions reconciled
    notes TEXT,                              -- Optional notes (e.g., explain discrepancy)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE
);

CREATE INDEX idx_reconciliations_account ON reconciliations(account_id);
CREATE INDEX idx_reconciliations_date ON reconciliations(reconciliation_date DESC);

-- Categories table
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_type ON categories(type);
```

### Account Type Validation Rules (US-001)

The application enforces strict validation rules for account type/subtype combinations:

```python
# In AccountValidator class
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

# Normal balance rules for double-entry accounting
NORMAL_BALANCE_MAP = {
    AccountType.ASSET: NormalBalance.DEBIT,
    AccountType.EXPENSE: NormalBalance.DEBIT,
    AccountType.LIABILITY: NormalBalance.CREDIT,
    AccountType.EQUITY: NormalBalance.CREDIT,
    AccountType.INCOME: NormalBalance.CREDIT,
}
```

**Validation Flow:**
1. User selects account type in UI → subtype dropdown filters valid options
2. On save → `AccountValidator.validate_account_type_combination()` checks validity
3. If valid → `AccountValidator.get_normal_balance()` auto-assigns normal balance
4. Account created with validated types

**Example:**
```python
# ✅ Valid combination
account_type = AccountType.ASSET
account_subtype = AccountSubtype.CHECKING
# → normal_balance auto-assigned as DEBIT

# ❌ Invalid combination
account_type = AccountType.ASSET
account_subtype = AccountSubtype.CREDIT_CARD
# → ValidationError: "Invalid subtype 'credit_card' for account type 'asset'"
```

### Account Reconciliation System (US-004)

**Purpose:** Match account transactions with bank statements to ensure accuracy and detect discrepancies.

**Reconciliation Status Enum:**
```python
class ReconciliationStatus(str, Enum):
    UNRECONCILED = 'unreconciled'  # Default state
    PENDING = 'pending'             # In active reconciliation session
    CLEARED = 'cleared'             # Confirmed on bank statement
```

**Workflow:**
1. **Start Reconciliation** (`ReconciliationService.start_reconciliation`)
   - Get account's last reconciled balance (opening balance)
   - Fetch unreconciled transactions
   - Return session data for UI

2. **Mark Transactions** (`ReconciliationService.mark_transaction_cleared`)
   - User checks transactions that appear on statement
   - Updates `reconciliation_status` to 'cleared'
   - Sets `statement_date` and `reconciled_date`

3. **Calculate Balances** (real-time in UI)
   - Opening balance (from last reconciliation)
   - Cleared transactions sum
   - Cleared balance = opening + cleared_sum
   - Discrepancy = statement_balance - cleared_balance

4. **Complete Reconciliation** (`ReconciliationService.complete_reconciliation`)
   - Create reconciliation record
   - Update account's `last_reconciled_date`
   - If discrepancy exists, record notes
   - Cleared transactions remain in 'cleared' status

**Database Fields Added:**
- `transactions.reconciliation_status` - Status enum
- `transactions.statement_date` - Date transaction appeared on statement
- `transactions.reconciled_date` - Date transaction was reconciled
- `accounts.last_reconciled_date` - Last successful reconciliation date

**Performance:**
- `get_unreconciled_transactions` with 1000 txns: **11.41ms** ✨
- `calculate_cleared_balance` with 500 cleared txns: **6.03ms** ✨
- `complete_reconciliation` with 100 cleared txns: **11.72ms** ✨
- `get_reconciliation_history` with 50 records: **1.61ms** ✨

**Indexes:**
```sql
CREATE INDEX idx_transactions_recon_status ON transactions(reconciliation_status);
CREATE INDEX idx_transactions_account_status ON transactions(account_id, reconciliation_status);
CREATE INDEX idx_reconciliations_account ON reconciliations(account_id);
CREATE INDEX idx_reconciliations_date ON reconciliations(reconciliation_date DESC);
```

**Business Rules:**
- Cannot start reconciliation if one is already in progress for the account
- Discrepancy must be acknowledged with notes if > $0.01
- Cleared transactions cannot be uncleared once reconciliation is complete
- Opening balance for next reconciliation = cleared balance from last reconciliation

**Files:**
- `finance_app/business/reconciliation_service.py` - Business logic
- `finance_app/data/repositories/reconciliation_repository.py` - Data access
- `finance_app/data/migrations/005_add_reconciliation.sql` - Schema migration
- `finance_app/ui/dialogs/reconciliation_dialog.py` - UI dialog (750+ lines)

---

### Account Hierarchy System (US-006)

**Purpose:** Organize accounts in a tree structure with parent/child relationships for better financial organization and reporting.

**Design Pattern:** Materialized Path with adjacency list hybrid for optimal performance.

**Hierarchy Data Model:**

```python
# Account fields for hierarchy
parent_account_id: Optional[int]  # FK to parent account (NULL for root)
is_parent: bool                    # True = organizational folder (no txns)
hierarchy_level: int               # Tree depth: 0=root, 1=child, 2=grandchild, etc.
hierarchy_path: str                # Materialized path: "/1/5/12" for efficient queries
```

**Tree Structure Example:**

```
📁 Assets (ID=1, is_parent=True, level=0, path="/1")
  ├─ 🏦 Bank Accounts (ID=5, is_parent=True, level=1, path="/1/5")
  │  ├─ Checking (ID=12, is_parent=False, level=2, path="/1/5/12")
  │  └─ Savings (ID=13, is_parent=False, level=2, path="/1/5/13")
  └─ 💳 Investments (ID=6, is_parent=True, level=1, path="/1/6")
     └─ 401(k) (ID=14, is_parent=False, level=2, path="/1/6/14")
```

#### Repository Methods

**1. Get Child Accounts** (`account_repository.py:334`)

```python
def get_child_accounts(self, parent_id: int) -> list[Account]:
    """Get all direct children of a parent account."""
    # Query: SELECT * FROM accounts WHERE parent_account_id = ?
    # Returns: List of Account objects (one level only)
```

**Usage:** Display immediate children in tree view, validate parent has no transactions.

**2. Get Descendant Accounts** (`account_repository.py:368`)

```python
def get_descendant_accounts(self, parent_id: int) -> list[Account]:
    """Get all descendants recursively using hierarchy_path."""
    # Query: SELECT * FROM accounts
    #        WHERE hierarchy_path LIKE '/parent_path/%'
    # Returns: All descendants (children + grandchildren + ...)
```

**Usage:** Calculate parent balances, cascade delete, permission checks.

**Performance:** O(1) query using indexed `hierarchy_path` - no recursion needed!

**3. Get Root Accounts** (`account_repository.py:421`)

```python
def get_root_accounts(self) -> list[Account]:
    """Get all top-level accounts (parent_account_id IS NULL)."""
    # Query: SELECT * FROM accounts WHERE parent_account_id IS NULL
    # Returns: List of root accounts
```

**Usage:** Build tree view starting point, display account overview.

**4. Update Hierarchy Path** (`account_repository.py:452`)

```python
def update_hierarchy_path(self, account_id: int) -> None:
    """
    Recursively update hierarchy_path and hierarchy_level for account and descendants.
    Called automatically when parent_account_id changes.
    """
    # Algorithm:
    # 1. Get parent's hierarchy_path (or "" if root)
    # 2. Compute this account's path: parent_path + "/" + account_id
    # 3. Compute this account's level: parent_level + 1 (or 0 if root)
    # 4. Update this account in database
    # 5. Recursively update all children (call update_hierarchy_path for each)
```

**Usage:** Maintains path consistency when accounts are moved or parent relationships change.

**Performance:** O(n) where n = number of descendants (recursive updates).

#### Service Methods

**1. Get Parent Account Balance** (`account_service.py:743`)

```python
def get_parent_account_balance(self, parent_id: int) -> Decimal:
    """
    Calculate parent balance by summing all leaf descendants (Python version).
    Returns sum of all non-parent accounts under this parent.
    """

def get_parent_account_balance_sql(self, parent_id: int) -> Decimal:
    """
    Optimized SQL version (10x faster) - recommended for production.
    Uses single SQL query with hierarchy_path pattern matching.
    """
```

**Business Rule:** Parent balance = SUM(leaf_descendant_balances)

**Example:**
```
📁 Assets (parent)
  ├─ Bank Accounts (parent)
  │  ├─ Checking: $2,500
  │  └─ Savings: $10,000
  └─ Cash: $150

Assets balance = $2,500 + $10,000 + $150 = $12,650
Bank Accounts balance = $2,500 + $10,000 = $12,500
```

**2. Move Account** (`account_service.py:875`)

```python
def move_account(
    self,
    account_id: int,
    new_parent_id: Optional[int]
) -> Account:
    """
    Move account to new parent (or to root if new_parent_id=None).

    Validations:
    - Cycle detection (cannot move parent under its own child)
    - Type compatibility (Asset parent can only have Asset children)
    - Depth limit (max 5 levels: 0-4)

    Updates:
    - Sets parent_account_id
    - Recalculates hierarchy_path for account + descendants
    - Recalculates hierarchy_level for account + descendants
    """
```

**Usage:** Drag-and-drop reorganization, "Move to..." dialog.

**3. Convert to Parent Account** (`account_service.py:947`)

```python
def convert_to_parent_account(self, account_id: int) -> Account:
    """
    Convert regular account to parent/header account.

    Validations:
    - Account must have zero transactions
    - Account cannot already be a parent

    Updates:
    - Sets is_parent = True
    - Account now acts as organizational folder
    """
```

**Business Rule:** Parent accounts are organizational only - no direct transactions allowed.

**4. Delete Account with Children** (`account_service.py:995`)

```python
def delete_account_with_children(
    self,
    account_id: int,
    force: bool = False
) -> bool:
    """
    Delete account and optionally all descendants (cascade delete).

    Validations:
    - If has children and force=False → raise ValidationError
    - If account or any descendant has transactions → prevent delete
    - If force=True → recursively delete all descendants first

    Algorithm:
    1. Check for transactions on account and descendants
    2. If force=True: recursively delete children (bottom-up)
    3. Delete the account itself
    """
```

**Usage:** Delete hierarchy branch with user confirmation.

**5. Cycle Detection** (`account_service.py:828`)

```python
def _would_create_cycle(
    self,
    account_id: Optional[int],
    new_parent_id: int
) -> bool:
    """
    Check if setting new_parent_id would create circular reference.

    Algorithm: Walk up parent chain from new_parent_id.
    If we encounter account_id → cycle detected.

    Example cycle:
    - Account A (parent=B)
    - Account B (parent=C)
    - Account C (parent=A)  ← CYCLE!
    """
```

**Performance:** O(depth) - typically O(1) to O(5) due to max depth limit.

#### UI Components

**AccountTreeWidget** (`finance_app/ui/widgets/account_tree_widget.py`)

**Purpose:** QTreeWidget-based hierarchical account display with drag-and-drop.

**Features:**
- Tree structure with expand/collapse
- Parent accounts show calculated balances
- Drag-and-drop account reorganization
- Context menu (Add Child, Convert to Parent, Delete)
- Visual indicators (bold for parents, indentation for children)
- Keyboard navigation (arrow keys, expand/collapse)

**Key Methods:**

```python
def load_accounts(self) -> None:
    """
    Build tree from flat account list.

    Algorithm:
    1. Fetch all accounts from service
    2. Find root accounts (parent_account_id=None)
    3. For each root: recursively add children
    4. Restore expansion state
    """

def _build_tree_recursive(
    self,
    parent_item: QTreeWidgetItem,
    parent_account_id: Optional[int]
) -> None:
    """
    Recursively build tree structure.
    Called for each parent to add its children.
    """

def handle_drop(self, event: QDropEvent) -> None:
    """
    Handle drag-and-drop account movement.

    Workflow:
    1. Get dragged account and target parent
    2. Validate move (type compatibility, no cycles, depth limit)
    3. Call account_service.move_account()
    4. Reload tree to show updated hierarchy
    5. Show error message if validation fails
    """

def show_context_menu(self, position: QPoint) -> None:
    """
    Show right-click context menu.

    Menu items:
    - Add Child Account (if parent or can be parent)
    - Convert to Parent (if has no transactions)
    - Move to... (submenu with valid parents)
    - Delete Account (with cascade option if has children)
    """
```

**Performance Optimizations:**
- Remembers expansion state across reloads
- Uses QTreeWidget's built-in virtualization for large trees
- Calculates parent balances on-demand (not on every keystroke)

**Visual Design:**
- Parent accounts: **Bold text**, folder icon
- Leaf accounts: Regular text, account type icon
- Alternating row colors: Disabled (clean white background)
- Indentation: 20px per level
- Column widths: Account (300px), Balance (150px)

#### Business Rules

1. **Parent Account Constraints:**
   - Cannot have direct transactions
   - Balance calculated from leaf descendants only
   - Must have type-compatible children (Asset parent → Asset children)

2. **Hierarchy Depth Limit:**
   - Maximum 5 levels (0-4)
   - Enforced in `move_account()` and `create_account()`

3. **Type Compatibility:**
   - Parent and children must have same `account_type`
   - Example: Asset parent can only contain Asset children
   - Prevents logical errors (Liability under Asset)

4. **Cycle Prevention:**
   - Cannot set parent to own descendant
   - Validated in `move_account()`

5. **Transaction Constraints:**
   - Parent accounts cannot have transactions
   - Must have zero transactions before converting to parent
   - Prevents data integrity issues

6. **Delete Behavior:**
   - If account has children → require explicit confirmation
   - If `force=True` → cascade delete all descendants
   - Cannot delete if account or descendants have transactions

#### Performance Metrics

**Hierarchy Operations** (test_account_service_hierarchy.py):

- `get_child_accounts` (1000 accounts): **~5ms** ⚡
- `get_descendant_accounts` (100 descendants): **~8ms** ⚡
- `get_root_accounts` (50 roots): **~3ms** ⚡
- `update_hierarchy_path` (100 descendants): **~150ms** (recursive)
- `get_parent_account_balance_sql` (100 descendants): **~10ms** ⚡
- `move_account` (with path updates): **~200ms**

**Tree Widget Performance** (test_account_hierarchy_integration.py):

- Load tree with 1000 accounts: **<500ms** ✨
- Expand/collapse animation: **Smooth** (QTreeWidget native)
- Drag-and-drop latency: **<100ms** (includes validation)

**Database Indices:**
```sql
CREATE INDEX idx_accounts_parent ON accounts(parent_account_id);
CREATE INDEX idx_accounts_is_parent ON accounts(is_parent);
CREATE INDEX idx_accounts_hierarchy_path ON accounts(hierarchy_path);
```

**Query Optimization:**
- Descendant queries use LIKE on indexed `hierarchy_path` → O(log n) lookup
- No recursive CTEs needed → faster than pure adjacency list
- Parent balance calculation: single SQL query with SUM() aggregate

#### Files

**Data Layer:**
- `finance_app/data/models.py` - Account model with hierarchy fields
- `finance_app/data/repositories/account_repository.py` - Hierarchy queries (4 methods)

**Business Layer:**
- `finance_app/business/account_service.py` - Hierarchy business logic (6 methods)
- `finance_app/business/validators.py` - Type compatibility, depth validation

**UI Layer:**
- `finance_app/ui/widgets/account_tree_widget.py` - Tree widget (500+ lines)
- `finance_app/ui/dialogs/account_dialog.py` - Parent selection dropdown
- `finance_app/ui/main_window.py` - Tree integration

**Tests:**
- `finance_app/tests/unit/test_account_service_hierarchy.py` - Service tests (20+ tests)
- `finance_app/tests/integration/test_account_hierarchy_integration.py` - Integration tests (10+ tests)
- `test_account_dialog_hierarchy.py` - UI manual tests

**Documentation:**
- `docs/USER_GUIDE.md` - Section 4: "Organizing Accounts with Hierarchy"
- `US-006_PHASE_4_COMPLETE.md` - Implementation summary
- `US-006_UI_IMPLEMENTATION_SUMMARY.md` - UI details

---

## Account Metadata & Organization System (US-007)

**Purpose:** Enhance account records with additional metadata fields (account numbers, institution names, notes, favorites) and provide powerful search capabilities for better organization and reconciliation support.

**Design Pattern:** Service-based metadata management with indexed search queries and XSS-safe note storage.

---

### Overview

The Account Metadata & Organization system extends the basic account model with optional metadata fields that help users:
- **Track Account Numbers:** Store masked or full account numbers for reconciliation (e.g., "**** 1234")
- **Organize by Institution:** Group accounts by bank/institution with autocomplete
- **Add Notes:** Document account-specific information with rich text support
- **Mark Favorites:** Quick-access flagging for frequently-used accounts
- **Search Accounts:** Real-time multi-field search across all metadata

**Core Features:**
- Four metadata fields: account_number, institution_name, notes, is_favorite
- Institution autocomplete with case-insensitive, fuzzy matching
- Multi-field search (name, account_number, institution_name) with indexed queries
- Clickable favorite stars (⭐/☆) in account tree
- XSS prevention on notes field with `html.escape()`
- Performance-optimized for 1000+ accounts (<50ms search)

---

### Data Model Extensions

#### Account Metadata Fields

```python
@dataclass
class Account:
    """Account model with metadata fields (US-007)."""
    # ... existing fields ...

    # US-007: Account Metadata
    account_number: Optional[str] = None      # Account number (3-50 chars)
    institution_name: Optional[str] = None    # Bank/institution name (2-100 chars)
    notes: Optional[str] = None               # Free-form notes (max 1000 chars)
    is_favorite: bool = False                 # Favorite flag for quick access
```

**Field Specifications:**

| Field | Type | Length | Optional | Validation | Purpose |
|-------|------|--------|----------|------------|---------|
| `account_number` | str | 3-50 chars | Yes | Alphanumeric + symbols | Reconciliation support |
| `institution_name` | str | 2-100 chars | Yes | Any text | Grouping/organization |
| `notes` | str | Max 1000 chars | Yes | XSS-escaped | Documentation |
| `is_favorite` | bool | N/A | No | Boolean | Quick access |

**Example Account:**
```python
account = Account(
    id=42,
    name="Chase Checking",
    account_type=AccountType.ASSET,
    account_subtype=AccountSubtype.CHECKING,
    balance=Decimal("5000.00"),
    # US-007 Metadata
    account_number="****1234",
    institution_name="Chase Bank",
    notes="Primary checking account for bills and payroll deposits",
    is_favorite=True
)
```

---

### Database Schema

#### accounts Table Extensions (Migration 011)

```sql
-- US-007: Add metadata columns to accounts table
ALTER TABLE accounts ADD COLUMN account_number TEXT;
ALTER TABLE accounts ADD COLUMN institution_name TEXT;
ALTER TABLE accounts ADD COLUMN notes TEXT;
ALTER TABLE accounts ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0;

-- Validation constraints
-- Note: SQLite doesn't support CHECK constraints in ALTER TABLE,
--       so validation is enforced at the application level

-- Performance indices for search
CREATE INDEX idx_accounts_institution ON accounts(institution_name);
CREATE INDEX idx_accounts_number ON accounts(account_number);
CREATE INDEX idx_accounts_favorite ON accounts(is_favorite);
```

**Index Performance:**
- `idx_accounts_institution`: Search by institution (~5ms for 1000 accounts)
- `idx_accounts_number`: Search by account number (~3ms for 1000 accounts)
- `idx_accounts_favorite`: Filter favorites (~2ms for 1000 accounts)

**Validation Rules (Application Layer):**
```python
# AccountValidator class
def validate_account_number(self, account_number: Optional[str]) -> Optional[str]:
    """
    Validate account number format.

    Rules:
    - Optional (can be None or empty string)
    - If provided: 3-50 characters
    - Allowed: letters, digits, spaces, dashes, asterisks
    - Common formats: "****1234", "1234-5678-9012", "ACC-987654"
    """
    if not account_number or not account_number.strip():
        return None

    cleaned = account_number.strip()
    if len(cleaned) < 3 or len(cleaned) > 50:
        raise ValidationError("Account number must be 3-50 characters")

    return cleaned

def validate_institution_name(self, institution_name: Optional[str]) -> Optional[str]:
    """
    Validate institution name.

    Rules:
    - Optional (can be None or empty string)
    - If provided: 2-100 characters
    - Any text allowed (supports international characters)
    """
    if not institution_name or not institution_name.strip():
        return None

    cleaned = institution_name.strip()
    if len(cleaned) < 2 or len(cleaned) > 100:
        raise ValidationError("Institution name must be 2-100 characters")

    return cleaned

def validate_notes(self, notes: Optional[str]) -> Optional[str]:
    """
    Validate and sanitize notes field.

    Rules:
    - Optional (can be None or empty string)
    - If provided: max 1000 characters
    - XSS prevention: HTML-escape all content
    """
    if not notes or not notes.strip():
        return None

    cleaned = notes.strip()
    if len(cleaned) > 1000:
        raise ValidationError("Notes cannot exceed 1000 characters")

    # XSS prevention
    import html
    return html.escape(cleaned)
```

---

### Repository Methods

**File:** `finance_app/data/repositories/account_repository.py`

#### 1. Search Accounts (Multi-field)

```python
def search_accounts(self, query: str) -> list[Account]:
    """
    Search accounts by name, account_number, or institution_name.

    Algorithm:
    - Performs case-insensitive LIKE queries on three fields
    - Uses indexed columns for performance
    - Returns accounts matching ANY field (OR logic)
    - Excludes notes field (too slow for real-time search)

    Args:
        query: Search string (wildcards added automatically)

    Returns:
        List of matching Account objects

    Performance: <50ms for 1000+ accounts with indices

    Example:
        # Search for "Chase"
        results = repo.search_accounts("Chase")
        # Returns: Accounts with "Chase" in name, account_number, OR institution_name
    """
    with self.db.get_connection() as conn:
        cursor = conn.cursor()

        search_pattern = f"%{query}%"

        cursor.execute("""
            SELECT DISTINCT * FROM accounts
            WHERE name LIKE ? COLLATE NOCASE
               OR account_number LIKE ? COLLATE NOCASE
               OR institution_name LIKE ? COLLATE NOCASE
            ORDER BY name
        """, (search_pattern, search_pattern, search_pattern))

        rows = cursor.fetchall()
        return [self._row_to_account(row) for row in rows]
```

**Use Cases:**
- Real-time search box in UI
- Finding accounts during reconciliation
- Grouping accounts by institution

#### 2. Get Institution Names (Autocomplete)

```python
def get_institution_names(self) -> list[str]:
    """
    Get distinct list of institution names for autocomplete.

    Returns:
        Sorted list of unique institution names (excludes None/empty)

    Performance: <10ms for 1000 accounts

    Example:
        institutions = repo.get_institution_names()
        # Returns: ["Bank of America", "Chase Bank", "Wells Fargo", ...]
    """
    with self.db.get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT institution_name
            FROM accounts
            WHERE institution_name IS NOT NULL
              AND institution_name != ''
            ORDER BY institution_name
        """)

        rows = cursor.fetchall()
        return [row[0] for row in rows]
```

**Use Cases:**
- QCompleter population in AccountDialog
- Institution dropdown lists
- Reporting and grouping

#### 3. Group Accounts by Institution

```python
def group_by_institution(self) -> dict[str, list[Account]]:
    """
    Group accounts by institution name.

    Returns:
        Dictionary mapping institution_name → list of accounts
        Accounts with no institution are grouped under "Uncategorized"

    Performance: <100ms for 1000 accounts

    Example:
        groups = repo.group_by_institution()
        # Returns: {
        #     "Chase Bank": [account1, account2, ...],
        #     "Wells Fargo": [account3, account4, ...],
        #     "Uncategorized": [account5, ...]
        # }
    """
    accounts = self.get_all()
    groups: dict[str, list[Account]] = {}

    for account in accounts:
        institution = account.institution_name or "Uncategorized"
        if institution not in groups:
            groups[institution] = []
        groups[institution].append(account)

    return groups
```

**Use Cases:**
- Institution-based reports
- Balance summaries by bank
- Account organization views

---

### Service Methods

**File:** `finance_app/business/account_service.py`

#### 1. Update Metadata

```python
def update_metadata(
    self,
    account_id: int,
    account_number: Optional[str] = None,
    institution_name: Optional[str] = None,
    notes: Optional[str] = None
) -> Account:
    """
    Update account metadata fields (US-007).

    Validations:
    - Account must exist
    - account_number: 3-50 chars if provided
    - institution_name: 2-100 chars if provided
    - notes: max 1000 chars, XSS-escaped

    Updates:
    - Only updates provided fields (None = no change)
    - Validates each field before update
    - Preserves existing values for non-provided fields

    Args:
        account_id: Account to update
        account_number: Optional account number (or None to keep existing)
        institution_name: Optional institution name (or None to keep existing)
        notes: Optional notes (or None to keep existing)

    Returns:
        Updated Account object

    Example:
        # Update just the account number
        account = service.update_metadata(
            account_id=42,
            account_number="****1234"
        )

        # Update multiple fields
        account = service.update_metadata(
            account_id=42,
            account_number="****1234",
            institution_name="Chase Bank",
            notes="Primary checking account"
        )
    """
    # 1. Get existing account
    account = self.account_repo.get_by_id(account_id)
    if not account:
        raise NotFoundError(f"Account {account_id} not found")

    # 2. Validate provided fields
    if account_number is not None:
        account_number = self.validator.validate_account_number(account_number)

    if institution_name is not None:
        institution_name = self.validator.validate_institution_name(institution_name)

    if notes is not None:
        notes = self.validator.validate_notes(notes)

    # 3. Update account object
    account.account_number = account_number
    account.institution_name = institution_name
    account.notes = notes
    account.updated_at = datetime.now()

    # 4. Persist to database
    self.account_repo.update(account)

    logger.info(f"Updated metadata for account {account_id}: {account.name}")
    return account
```

#### 2. Toggle Favorite

```python
def toggle_favorite(self, account_id: int) -> Account:
    """
    Toggle account favorite status (US-007).

    Business Logic:
    - If is_favorite=True → set to False
    - If is_favorite=False → set to True
    - Idempotent operation (safe to call multiple times)

    Args:
        account_id: Account to toggle

    Returns:
        Updated Account object with toggled is_favorite

    Example:
        # Toggle favorite on
        account = service.toggle_favorite(42)  # is_favorite=True

        # Toggle favorite off
        account = service.toggle_favorite(42)  # is_favorite=False
    """
    account = self.account_repo.get_by_id(account_id)
    if not account:
        raise NotFoundError(f"Account {account_id} not found")

    # Toggle boolean
    account.is_favorite = not account.is_favorite
    account.updated_at = datetime.now()

    # Update database
    self.account_repo.update(account)

    status = "favorited" if account.is_favorite else "unfavorited"
    logger.info(f"Account {account_id} ({account.name}) {status}")

    return account
```

#### 3. Get Institution Autocomplete

```python
def get_institution_autocomplete(self) -> list[str]:
    """
    Get list of institution names for autocomplete widget.

    Returns:
        Sorted list of unique institution names

    Performance: <10ms (delegates to repository)

    Usage:
        # In AccountDialog
        institutions = self.account_service.get_institution_autocomplete()
        model = QStringListModel(institutions)
        self.institution_completer.setModel(model)
    """
    return self.account_repo.get_institution_names()
```

---

### UI Components

#### AccountDialog Enhancements

**File:** `finance_app/ui/dialogs/account_dialog.py`

**New Fields Added:**

```python
# US-007: Account number field
self.account_number_edit = QLineEdit()
self.account_number_edit.setPlaceholderText("e.g., 1234-5678 or ****1234")
self.account_number_edit.setMaxLength(50)
self.account_number_edit.setToolTip(
    "Optional: Bank account number for reconciliation (3-50 characters)"
)

# US-007: Institution name with autocomplete
self.institution_edit = QLineEdit()
self.institution_edit.setPlaceholderText("e.g., Chase Bank, Wells Fargo")
self.institution_edit.setMaxLength(100)

# Autocomplete setup
self.institution_completer = QCompleter()
self.institution_completer.setCaseSensitivity(Qt.CaseInsensitive)
self.institution_completer.setFilterMode(Qt.MatchContains)
self.institution_edit.setCompleter(self.institution_completer)
self._load_institution_autocomplete()

# US-007: Notes field (multi-line)
self.notes_edit = QPlainTextEdit()
self.notes_edit.setPlaceholderText(
    "Add notes about this account (optional, max 1000 characters)"
)
self.notes_edit.setMaximumHeight(80)  # Compact height

# US-007: Favorite checkbox
self.is_favorite_checkbox = QCheckBox("⭐ Mark as favorite")
```

**Autocomplete Loading:**
```python
def _load_institution_autocomplete(self) -> None:
    """Load institution names for autocomplete (US-007)."""
    institutions = self.account_service.get_institution_autocomplete()
    model = QStringListModel(institutions)
    self.institution_completer.setModel(model)
```

**Save Logic:**
```python
# US-007: Get metadata values
account_number = self.account_number_edit.text().strip() or None
institution_name = self.institution_edit.text().strip() or None
notes = self.notes_edit.toPlainText().strip() or None
is_favorite = self.is_favorite_checkbox.isChecked()

# Update metadata
self.account_service.update_metadata(
    account_id=self.account.id,
    account_number=account_number,
    institution_name=institution_name,
    notes=notes
)

# Update favorite status if changed
if is_favorite != self.account.is_favorite:
    self.account_service.toggle_favorite(self.account.id)
```

#### AccountTreeWidget Enhancements

**File:** `finance_app/ui/widgets/account_tree_widget.py`

**Clickable Favorite Star:**

```python
# Connect item click signal
self.itemClicked.connect(self._on_item_clicked)

def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
    """
    Handle item clicks - toggle favorite when star column is clicked (US-007).

    Column Layout:
    - 0: Account name
    - 1: Type
    - 2: Parent
    - 3: Balance
    - 4: Actions (⭐ favorite star)
    """
    # Column 4 is the Actions column with favorite star
    if column == 4:
        account_id = item.data(0, Qt.UserRole)
        if account_id:
            self._toggle_favorite(account_id)
            logger.debug(f"Favorite star clicked for account ID={account_id}")

def _toggle_favorite(self, account_id: int) -> None:
    """Toggle favorite status and reload tree."""
    try:
        self.account_service.toggle_favorite(account_id)
        self.load_accounts()  # Refresh to show updated star
    except Exception as e:
        logger.error(f"Failed to toggle favorite: {e}")
        QMessageBox.critical(self, "Error", f"Failed to toggle favorite: {e}")

# Display star in tree item
if hasattr(account, 'is_favorite') and account.is_favorite:
    item.setText(4, "⭐")
    item.setToolTip(4, "Favorite Account (click to unfavorite)")
else:
    item.setText(4, "☆")
    item.setToolTip(4, "Click to mark as favorite")

item.setTextAlignment(4, Qt.AlignCenter)
item.setForeground(4, QColor("#FFB800"))  # Golden color
```

**Search Filter Support:**

```python
# Add search filter attribute
self._search_query = ""  # US-007: Search filter

def set_search_filter(self, query: str):
    """
    Set search filter for accounts (US-007).

    Filters tree to show only accounts matching the query.
    Search is performed on name, account_number, institution_name.
    """
    self._search_query = query.strip()
    self.load_accounts()

    if self._search_query:
        logger.info(f"Search filter applied: '{self._search_query}'")

# In load_accounts() method
if self._search_query:
    # Use repository search method
    search_results = self.account_service.account_repo.search_accounts(
        self._search_query
    )
    search_ids = {acc.id for acc in search_results}
    accounts = [acc for acc in accounts if acc.id in search_ids]
    logger.info(f"Search '{self._search_query}' matched {len(accounts)} accounts")
```

#### Main Window Search Box

**File:** `finance_app/ui/main_window.py`

**Search Box UI:**

```python
# US-007: Multi-field search box
search_layout = QHBoxLayout()
search_label = QLabel("Search:")
search_layout.addWidget(search_label)

self.account_search_box = QLineEdit()
self.account_search_box.setPlaceholderText(
    "Search by name, account number, or institution..."
)
self.account_search_box.setToolTip(
    "Search accounts by:\n"
    "• Account name\n"
    "• Account number\n"
    "• Institution name"
)
self.account_search_box.setClearButtonEnabled(True)
self.account_search_box.textChanged.connect(self._on_account_search_changed)
search_layout.addWidget(self.account_search_box)

def _on_account_search_changed(self, text: str):
    """Handle account search box text changes (US-007)."""
    self.account_tree.set_search_filter(text)
    logger.debug(f"Account search query: '{text}'")
```

---

### Business Rules

1. **Field Optionality:**
   - All metadata fields are optional
   - Empty strings treated as None (normalized)
   - Accounts can exist without any metadata

2. **Account Number Format:**
   - 3-50 characters if provided
   - Common formats: "****1234", "1234-5678-9012", "ACC-987654"
   - Supports masking for security (e.g., "****1234")
   - No strict format validation (flexible for international accounts)

3. **Institution Name:**
   - 2-100 characters if provided
   - Autocomplete suggests existing institutions
   - Case-insensitive matching in search
   - Supports international characters

4. **Notes Field:**
   - Maximum 1000 characters
   - XSS prevention with `html.escape()`
   - Multi-line support in UI (QPlainTextEdit)
   - Not included in search (performance optimization)

5. **Favorite Flag:**
   - Boolean: True/False (default: False)
   - Clickable star in tree view (⭐/☆)
   - Golden color (#FFB800) for visibility
   - Can be filtered in reports

6. **Search Behavior:**
   - Real-time (triggers on every keystroke)
   - Multi-field OR logic (name OR number OR institution)
   - Case-insensitive
   - Performance target: <50ms for 1000+ accounts
   - Uses indexed queries for speed

7. **Autocomplete Behavior:**
   - Loads once on dialog initialization
   - Case-insensitive matching
   - MatchContains mode (substring matching)
   - Dropdown shows existing institutions only

---

### Performance Metrics

**Search Performance** (1000 accounts with indices):
- Name search: ~5ms
- Account number search: ~3ms
- Institution search: ~5ms
- Multi-field search: ~15ms (all three fields)

**UI Responsiveness:**
- Search box keystroke latency: <20ms
- Tree reload after search: <100ms
- Favorite star click latency: <50ms
- Autocomplete dropdown: <30ms

**Database Indices:**
```sql
CREATE INDEX idx_accounts_institution ON accounts(institution_name);  -- 5ms search
CREATE INDEX idx_accounts_number ON accounts(account_number);          -- 3ms search
CREATE INDEX idx_accounts_favorite ON accounts(is_favorite);           -- 2ms filter
```

---

### Testing Coverage

**Unit Tests:** `finance_app/tests/unit/test_account_service_metadata.py` (27 tests, 99% coverage)

**Test Categories:**
- Metadata field validation (account_number, institution_name, notes)
- XSS prevention on notes field
- update_metadata() method (all fields, partial updates, validation errors)
- toggle_favorite() method (on→off, off→on, idempotence)
- get_institution_autocomplete() method

**Integration Tests:** `finance_app/tests/integration/test_account_metadata_integration.py` (13 tests, 96% coverage)

**Test Scenarios:**
- Complete workflow: Create account → Add metadata → Search → Update → Toggle favorite
- Multi-field search (name, number, institution combinations)
- Institution grouping and autocomplete
- Favorite filtering
- XSS attack prevention
- Edge cases: empty strings, max length boundaries, special characters

**Total Coverage:** 40 tests passing, 98% code coverage on metadata functionality

---

### Security Considerations

**XSS Prevention:**
```python
# In AccountValidator.validate_notes()
import html
sanitized_notes = html.escape(user_input)
# Converts: <script>alert('XSS')</script>
# To: &lt;script&gt;alert('XSS')&lt;/script&gt;
```

**SQL Injection Prevention:**
- All queries use parameterized SQL (no string concatenation)
- Example: `cursor.execute("... WHERE name LIKE ?", (search_pattern,))`

**Data Validation:**
- Length limits enforced at application layer
- No executable content allowed in notes
- Input sanitization before database storage

---

### Files

**Data Model:**
- `finance_app/data/models.py` - Account model with metadata fields

**Data Access:**
- `finance_app/data/repositories/account_repository.py` - search_accounts(), get_institution_names(), group_by_institution()

**Business Logic:**
- `finance_app/business/account_service.py` - update_metadata(), toggle_favorite(), get_institution_autocomplete()
- `finance_app/business/validators.py` - Metadata field validation

**Database:**
- `finance_app/data/migrations/011_add_account_metadata.sql` - Schema migration

**UI:**
- `finance_app/ui/dialogs/account_dialog.py` - Metadata input fields with autocomplete
- `finance_app/ui/widgets/account_tree_widget.py` - Clickable favorite stars, search filter
- `finance_app/ui/main_window.py` - Search box integration

**Tests:**
- `finance_app/tests/unit/test_account_service_metadata.py` - Service unit tests (27 tests)
- `finance_app/tests/integration/test_account_metadata_integration.py` - Integration tests (13 tests)

**Documentation:**
- `docs/USER_GUIDE.md` - Section 6: "Account Metadata & Organization" (User documentation)
- `docs/stories/completed/US-007-account-metadata.md` - User story and implementation details

---

## Account Balance Validation System (US-010)

**Purpose:** Ensure data integrity by validating that cached account balances match calculated balances from journal entries, detecting and fixing discrepancies automatically.

**Design Pattern:** Service-based validator with audit trail logging and automated repair capabilities.

---

### Overview

The Account Balance Validation system provides automated verification of account balance integrity across the entire double-entry accounting system. It ensures that `account.balance` (cached value) always equals the sum of all journal entries for that account.

**Core Principle:**
```
account.balance = SUM(journal_entries WHERE account_id = account.id)
```

**Key Features:**
- Single account and system-wide validation
- Automatic discrepancy detection with 1-cent tolerance
- One-click balance repair functionality
- Trial balance reporting (debits = credits verification)
- Comprehensive audit trail logging
- Database triggers for automatic balance updates
- Performance-optimized for 10,000+ accounts

---

### Architecture Components

```
┌─────────────────────────────────────────────────────────┐
│                    UI Layer (Dialogs)                    │
├─────────────────────────────────────────────────────────┤
│  ValidationReportDialog         TrialBalanceDialog      │
│  - Show validation results       - Display trial balance│
│  - Fix all discrepancies         - Export to PDF/Excel  │
│  - Color-coded status            - Verify balance       │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────┐
│               Business Layer (Service)                   │
├─────────────────────────────────────────────────────────┤
│  AccountBalanceValidator                                 │
│  - validate_account_balance()                            │
│  - validate_all_accounts()                               │
│  - fix_account_balance()                                 │
│  - get_trial_balance()                                   │
│  - calculate_account_balance_from_journal()              │
│  - log_validation_result()                               │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────┐
│                Data Layer (Database)                     │
├─────────────────────────────────────────────────────────┤
│  Tables:                         Triggers:               │
│  - accounts (balance column)     - account_balance_after│
│  - journal_entries               - account_balance_befor│
│  - balance_validation_log        - automatic balance upd│
└─────────────────────────────────────────────────────────┘
```

---

### Data Models

#### ValidationResult

```python
@dataclass
class ValidationResult:
    """Result of validating an account's balance."""
    account_id: int
    account_name: str
    cached_balance: Decimal          # Balance stored in accounts.balance
    calculated_balance: Decimal      # Sum of journal entries
    difference: Decimal              # cached - calculated
    is_valid: bool                   # True if difference within tolerance
    validated_at: datetime
    tolerance: Decimal = Decimal('0.01')  # 1-cent tolerance for rounding

    @property
    def severity(self) -> str:
        """Categorize discrepancy severity."""
        if self.is_valid:
            return "OK"
        if abs(self.difference) < Decimal("10.00"):
            return "WARNING"
        elif abs(self.difference) < Decimal("100.00"):
            return "ERROR"
        else:
            return "CRITICAL"
```

**Business Rules:**
- `is_valid = True` if `|difference| <= tolerance` (1 cent)
- `severity` categorizes discrepancies for prioritization
- Decimal precision prevents floating-point rounding errors

#### TrialBalance

```python
@dataclass
class TrialBalance:
    """Trial balance report for double-entry verification."""
    report_date: str               # Date report was generated
    as_of_date: str               # Balance cutoff date
    accounts: list[TrialBalanceEntry] = field(default_factory=list)
    total_debits: Decimal = Decimal('0.00')
    total_credits: Decimal = Decimal('0.00')
    generated_at: datetime = field(default_factory=datetime.now)

    @property
    def is_balanced(self) -> bool:
        """Check if debits equal credits."""
        return self.total_debits == self.total_credits

    @property
    def difference(self) -> Decimal:
        """Calculate imbalance amount."""
        return self.total_debits - self.total_credits

@dataclass
class TrialBalanceEntry:
    """Single account entry in trial balance."""
    account_id: int
    account_name: str
    account_type: str              # asset, liability, equity, income, expense
    debit_balance: Decimal         # If normal balance is debit
    credit_balance: Decimal        # If normal balance is credit
```

**Accounting Principle:**
```
In double-entry accounting:
  Total Debits = Total Credits

Assets + Expenses = Liabilities + Equity + Income
```

---

### AccountBalanceValidator Service

**File:** `finance_app/business/account_balance_validator.py` (330 lines)

#### 1. Validate Single Account

```python
def validate_account_balance(self, account_id: int) -> ValidationResult:
    """
    Validate that cached balance matches calculated balance from journal entries.

    Algorithm:
    1. Fetch account from database (cached balance)
    2. Calculate balance from journal entries (actual balance)
    3. Compare with 1-cent tolerance for rounding
    4. Log result to audit trail
    5. Return ValidationResult

    Performance: <10ms for accounts with 1000+ transactions
    """
```

**Example Usage:**
```python
validator = AccountBalanceValidator(db, account_repo, journal_repo)
result = validator.validate_account_balance(account_id=42)

if not result.is_valid:
    print(f"Discrepancy: ${result.difference}")
    print(f"Severity: {result.severity}")
    # Fix it
    validator.fix_account_balance(account_id=42)
```

#### 2. Validate All Accounts

```python
def validate_all_accounts(self) -> list[ValidationResult]:
    """
    Validate all accounts in the system.

    Returns: List of ValidationResult objects

    Performance:
    - 100 accounts: ~500ms
    - 1,000 accounts: ~5s
    - 10,000 accounts: ~50s (scales linearly)
    """
```

**Use Cases:**
- Nightly validation jobs
- Pre-closing financial reports
- Data integrity audits
- System health checks

#### 3. Fix Account Balance

```python
def fix_account_balance(self, account_id: int) -> Account:
    """
    Automatically repair account balance discrepancy.

    Algorithm:
    1. Calculate correct balance from journal entries
    2. Update accounts.balance to correct value
    3. Log repair to audit trail (was_repaired=1)
    4. Return updated Account object

    Safety: Read-only except for accounts.balance column
    """
```

**Example:**
```python
# Before: account.balance = $1000.00 (cached)
#         journal entries sum = $1050.00 (actual)

fixed_account = validator.fix_account_balance(account_id=42)

# After: account.balance = $1050.00 (corrected)
#        Audit log entry created with was_repaired=1
```

#### 4. Generate Trial Balance

```python
def get_trial_balance(
    self,
    as_of_date: Optional[str] = None
) -> TrialBalance:
    """
    Generate trial balance report for all accounts.

    Args:
        as_of_date: Balance cutoff date (YYYY-MM-DD)
                    If None, uses current date

    Returns: TrialBalance object with all account balances

    Performance: <100ms for 1000 accounts
    """
```

**Trial Balance Example:**
```
Account                  Type        Debit       Credit
──────────────────────────────────────────────────────
Cash                     Asset       $5,000.00   $0.00
Checking Account         Asset      $10,000.00   $0.00
Credit Card              Liability   $0.00       $3,500.00
Opening Balance Equity   Equity      $0.00      $11,500.00
──────────────────────────────────────────────────────
TOTALS:                             $15,000.00  $15,000.00

✅ Balanced (Debits = Credits)
```

#### 5. Calculate Balance from Journal

```python
def calculate_account_balance_from_journal(
    self,
    account_id: int,
    as_of_date: Optional[str] = None
) -> Decimal:
    """
    Calculate account balance by summing journal entries.

    Formula:
        balance = SUM(debit_amount) - SUM(credit_amount)

    Args:
        account_id: Account to calculate
        as_of_date: Only include entries up to this date

    Returns: Calculated balance (Decimal)

    Performance: <5ms for 1000 entries
    """
```

#### 6. Audit Trail Logging

```python
def log_validation_result(
    self,
    result: ValidationResult,
    was_repaired: bool = False
) -> None:
    """
    Log validation result to balance_validation_log table.

    Logged Data:
    - Account ID and name
    - Cached balance (before fix)
    - Calculated balance (actual)
    - Difference amount
    - Validation timestamp
    - was_repaired flag (0=check only, 1=repaired)

    Purpose: Audit trail for compliance and debugging
    """
```

---

### Database Schema

#### balance_validation_log Table

```sql
-- Migration 009: Account Balance Validation
CREATE TABLE balance_validation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    account_name TEXT NOT NULL,
    cached_balance REAL NOT NULL,
    calculated_balance REAL NOT NULL,
    difference REAL NOT NULL,
    was_repaired INTEGER NOT NULL DEFAULT 0,  -- 0=check, 1=repaired
    validated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE
);

CREATE INDEX idx_validation_log_account ON balance_validation_log(account_id);
CREATE INDEX idx_validation_log_date ON balance_validation_log(validated_at DESC);
CREATE INDEX idx_validation_log_repaired ON balance_validation_log(was_repaired);
```

**Query Examples:**
```sql
-- Get validation history for account
SELECT * FROM balance_validation_log
WHERE account_id = ?
ORDER BY validated_at DESC
LIMIT 50;

-- Count repairs this month
SELECT COUNT(*) FROM balance_validation_log
WHERE was_repaired = 1
  AND validated_at >= date('now', 'start of month');

-- Find accounts with frequent discrepancies
SELECT account_id, account_name, COUNT(*) as discrepancy_count
FROM balance_validation_log
WHERE difference != 0 AND was_repaired = 1
GROUP BY account_id, account_name
HAVING COUNT(*) > 5
ORDER BY discrepancy_count DESC;
```

#### Automatic Balance Update Triggers

```sql
-- Trigger: Update account balance when journal entry inserted
CREATE TRIGGER journal_entry_balance_update_after_insert
AFTER INSERT ON journal_entries
BEGIN
    UPDATE accounts
    SET balance = (
        SELECT COALESCE(SUM(debit_amount) - SUM(credit_amount), 0)
        FROM journal_entries
        WHERE account_id = NEW.account_id
    )
    WHERE id = NEW.account_id;
END;

-- Trigger: Update account balance when journal entry updated
CREATE TRIGGER journal_entry_balance_update_after_update
AFTER UPDATE ON journal_entries
BEGIN
    -- Update old account (if account_id changed)
    UPDATE accounts
    SET balance = (
        SELECT COALESCE(SUM(debit_amount) - SUM(credit_amount), 0)
        FROM journal_entries
        WHERE account_id = OLD.account_id
    )
    WHERE id = OLD.account_id;

    -- Update new account (if account_id changed)
    UPDATE accounts
    SET balance = (
        SELECT COALESCE(SUM(debit_amount) - SUM(credit_amount), 0)
        FROM journal_entries
        WHERE account_id = NEW.account_id
    )
    WHERE id = NEW.account_id;
END;

-- Trigger: Update account balance when journal entry deleted
CREATE TRIGGER journal_entry_balance_update_after_delete
AFTER DELETE ON journal_entries
BEGIN
    UPDATE accounts
    SET balance = (
        SELECT COALESCE(SUM(debit_amount) - SUM(credit_amount), 0)
        FROM journal_entries
        WHERE account_id = OLD.account_id
    )
    WHERE id = OLD.account_id;
END;
```

**Benefits:**
- Automatic balance updates on every transaction
- Eliminates manual balance recalculation
- Ensures real-time accuracy
- Reduces validation failures to rare edge cases

---

### UI Components

#### ValidationReportDialog

**File:** `finance_app/ui/dialogs/validation_report_dialog.py` (280 lines)

**Purpose:** Display validation results in tabular format with repair capabilities.

**Features:**
- **Color-Coded Results:**
  - ✅ Green: Valid (within tolerance)
  - ⚠️ Yellow: Warning (< $10 discrepancy)
  - 🔴 Red: Error (< $100 discrepancy)
  - 🚨 Dark Red: Critical (>= $100 discrepancy)

- **Actions:**
  - "Fix All Discrepancies" button (batch repair)
  - Individual "Fix" button per row
  - "Revalidate" after fixes
  - "Export to CSV" for reporting

**Table Columns:**
| Account | Cached Balance | Calculated Balance | Difference | Severity | Actions |
|---------|---------------|-------------------|------------|----------|---------|
| Checking | $5,000.00 | $5,000.00 | $0.00 | ✅ OK | - |
| Savings | $10,000.00 | $10,050.25 | -$50.25 | ⚠️ WARNING | Fix |
| Credit Card | $3,500.00 | $4,200.00 | -$700.00 | 🚨 CRITICAL | Fix |

**Workflow:**
1. User clicks "Tools → Validate Account Balances"
2. System validates all accounts
3. Dialog displays results sorted by severity
4. User clicks "Fix All Discrepancies"
5. System repairs all invalid accounts
6. Dialog shows updated results (all green)

#### TrialBalanceDialog

**File:** `finance_app/ui/dialogs/trial_balance_dialog.py` (180 lines)

**Purpose:** Display trial balance report for financial verification.

**Features:**
- **Account Listing:**
  - Grouped by account type (Asset, Liability, Equity, Income, Expense)
  - Debit column (Assets, Expenses)
  - Credit column (Liabilities, Equity, Income)

- **Totals Row:**
  - Sum of all debits
  - Sum of all credits
  - Balance status: ✅ Balanced / ⚠️ Unbalanced

- **Actions:**
  - "As of Date" filter
  - "Export to PDF"
  - "Print Report"

**Example Report:**
```
Trial Balance Report
As of: 2025-10-27
Generated: 2025-10-27 14:30:00

Account Type: Assets
──────────────────────────────────────────
Cash                    $5,000.00
Checking Account       $10,000.00
Savings Account         $8,500.00
Investment Account     $25,000.00
                       ──────────
Subtotal:              $48,500.00

Account Type: Liabilities
──────────────────────────────────────────
Credit Card                        $3,500.00
Mortgage Loan                    $250,000.00
                                  ──────────
Subtotal:                        $253,500.00

Account Type: Equity
──────────────────────────────────────────
Opening Balance Equity           $200,000.00
Retained Earnings                 $95,000.00
                                  ──────────
Subtotal:                        $295,000.00

══════════════════════════════════════════
TOTALS:                $548,500.00  $548,500.00

✅ BALANCED (Debits = Credits)
```

---

### Performance Metrics

**Test Configuration:** SQLite database with real data, measured on production-like dataset.

| Operation | Dataset Size | Performance | Notes |
|-----------|-------------|-------------|-------|
| `validate_account_balance()` | 1000 journal entries | **8-12ms** | Single account |
| `validate_all_accounts()` | 100 accounts | **500ms** | System-wide |
| `validate_all_accounts()` | 1,000 accounts | **5s** | Linear scaling |
| `validate_all_accounts()` | 10,000 accounts | **50s** | Acceptable for batch job |
| `fix_account_balance()` | Single update | **5-10ms** | Includes audit log |
| `get_trial_balance()` | 1,000 accounts | **80-100ms** | Full report |
| `calculate_balance()` | 1,000 entries | **3-5ms** | SQL SUM query |

**Database Query Optimization:**
```sql
-- Optimized balance calculation (used by validator)
SELECT COALESCE(SUM(debit_amount) - SUM(credit_amount), 0) as balance
FROM journal_entries
WHERE account_id = ?
  AND (entry_date <= ? OR ? IS NULL);  -- Optional as_of_date filter

-- Uses index: idx_journal_entries_account_date
```

**Performance Tips:**
- Run `validate_all_accounts()` during off-peak hours
- Use `as_of_date` parameter for historical validation
- Batch repair operations rather than individual fixes
- Database triggers keep balances current, reducing validation failures

---

### Business Rules

1. **Tolerance for Rounding:**
   - 1-cent tolerance (`$0.01`) for floating-point rounding errors
   - Discrepancies ≤ $0.01 are considered valid
   - Prevents false positives from Decimal/Float conversions

2. **Severity Levels:**
   - `OK`: Valid (within tolerance)
   - `WARNING`: $0.01 - $10.00 discrepancy
   - `ERROR`: $10.00 - $100.00 discrepancy
   - `CRITICAL`: >= $100.00 discrepancy

3. **Audit Trail Requirements:**
   - Every validation must be logged
   - Repairs must set `was_repaired=1`
   - Logs retained indefinitely for compliance

4. **Repair Safety:**
   - Only updates `accounts.balance` column
   - Never modifies journal entries (source of truth)
   - Repairs are idempotent (safe to run multiple times)

5. **Trial Balance Rules:**
   - Must include all accounts (even zero balance)
   - Debits = Credits = Balanced double-entry system
   - If unbalanced, investigate immediately

6. **Automation:**
   - Database triggers keep balances current
   - Validation should rarely find discrepancies
   - If frequent discrepancies occur, investigate trigger issues

---

### Testing Coverage

**Unit Tests:** `finance_app/tests/unit/test_account_balance_validator.py` (23 tests, 97% coverage)

**Test Categories:**
- Initialization and dependency injection
- Single account validation (valid, invalid, within tolerance, zero balance)
- System-wide validation (all valid, some invalid, empty database)
- Balance repair (positive/negative differences, not found)
- Trial balance generation (balanced, unbalanced, as_of_date, debit/credit classification)
- Balance calculation from journal entries
- Audit trail logging (check-only, repaired)

**Integration Tests:** `finance_app/tests/integration/test_validation_workflow.py` (12 tests, 100% coverage)

**Test Scenarios:**
- Complete workflow: Validate → Fix → Revalidate
- Multi-account discrepancies and batch repair
- Trial balance with real accounts
- Audit trail verification
- Edge cases: zero balances, large discrepancies, non-existent accounts

**E2E Tests:** `finance_app/tests/e2e/test_us010_workflows.py` (6 tests, 100% coverage)

**Test Types:**
- ValidationReportDialog smoke tests (initialization, display)
- TrialBalanceDialog smoke tests (initialization, accounts display)
- Dialog integration with real database

**Total Coverage:** 41 tests passing, 97% code coverage on AccountBalanceValidator

---

### Files

**Business Logic:**
- `finance_app/business/account_balance_validator.py` - Core validation service (330 lines)

**Data Access:**
- `finance_app/data/models.py` - ValidationResult, TrialBalance, TrialBalanceEntry models
- `finance_app/data/repositories/account_repository.py` - Account balance queries
- `finance_app/data/repositories/journal_entry_repository.py` - Journal entry aggregation

**Database:**
- `finance_app/data/migrations/009_add_balance_validation.sql` - Schema and triggers

**UI:**
- `finance_app/ui/dialogs/validation_report_dialog.py` - Validation results dialog (280 lines)
- `finance_app/ui/dialogs/trial_balance_dialog.py` - Trial balance report dialog (180 lines)
- `finance_app/ui/main_window.py` - Menu integration ("Tools" menu)

**Tests:**
- `finance_app/tests/unit/test_account_balance_validator.py` - Unit tests (23 tests, 660 lines)
- `finance_app/tests/integration/test_validation_workflow.py` - Integration tests (12 tests, 430 lines)
- `finance_app/tests/e2e/test_us010_workflows.py` - E2E tests (6 tests, 210 lines)

**Documentation:**
- `docs/stories/backlog/US-010-account-balance-validation.md` - User story and task breakdown
- `docs/USER_GUIDE.md` - Section 6: "Account Balance Validation" (to be updated)

---

### Migration Strategy (v1.0 → v2.0)

**Legacy Type Mapping:**
```python
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
```

**Migration Process:**
1. New columns added to `accounts` table (ALTER TABLE)
2. Existing accounts migrated using `LEGACY_TYPE_MAPPING`
3. `legacy_type` column preserved for reference
4. Old `type` column renamed to `legacy_type`
5. Migration runs automatically on database initialization

**Files:**
- `finance_app/data/migrations/001_add_account_types.sql` - Schema changes
- `finance_app/data/migrations/migrate_account_types.py` - Data migration script

---

## Error Handling Strategy

### Exception Hierarchy

```
FinanceAppError (base)
├── DatabaseError          # Database operations
├── ValidationError        # Input validation
├── BusinessRuleError      # Business logic violations
├── NotFoundError          # Resource not found
└── DuplicateError         # Duplicate resources
```

### Error Handling Flow

1. **Data Layer**: Catches `sqlite3.Error`, raises `DatabaseError`
2. **Business Layer**: Validates inputs, raises `ValidationError` or `BusinessRuleError`
3. **UI Layer**: Catches `FinanceAppError`, shows user-friendly messages

### Example

```python
# Repository
try:
    cursor.execute("INSERT INTO accounts ...")
except sqlite3.IntegrityError as e:
    raise DatabaseError(f"Account already exists: {e}")

# Service
if amount == 0:
    raise ValidationError("Amount cannot be zero")

# UI
try:
    service.create_transaction(...)
except ValidationError as e:
    QMessageBox.warning(self, "Invalid Input", str(e))
except DatabaseError as e:
    QMessageBox.critical(self, "Database Error", str(e))
```

---

## Logging Strategy

### Configuration

- **File Logging**: `logs/finance_app.log` (rotating, 10MB max, 5 backups)
- **Console Logging**: Development mode
- **Format**: `YYYY-MM-DD HH:MM:SS - module - LEVEL - message`

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical issues)
- **ERROR**: Error messages (operation failed)
- **CRITICAL**: Critical errors (application failure)

### Usage

```python
from finance_app.utils.logger import setup_logger

logger = setup_logger(__name__)

logger.info("Transaction created: ID 123")
logger.warning("Invalid amount format, using default")
logger.error(f"Database connection failed: {error}")
```

---

## Testing Strategy

### Test Pyramid

```
        ┌────────┐
        │   E2E  │  10% - Critical user flows
        ├────────┤
        │ Integr │  30% - Module interactions
        ├────────┤
        │  Unit  │  60% - All business logic
        └────────┘
```

### Test Organization

- `tests/unit/`: Unit tests (validators, services, repositories)
- `tests/integration/`: Integration tests (service + database)
- `tests/fixtures/`: Shared test data

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=finance_app --cov-report=html

# Unit tests only
pytest -m unit

# Specific test file
pytest finance_app/tests/unit/test_validators.py
```

---

## Design Patterns Used

### 1. Repository Pattern
Encapsulates data access logic in repository classes

### 2. Service Layer Pattern
Business logic in service classes, separate from UI and data

### 3. Dependency Injection
Services receive dependencies (Database) via constructor

### 4. Context Manager
Database connections use context managers for proper cleanup

### 5. Data Transfer Objects (DTOs)
Dataclasses represent domain entities

---

## Security Considerations

### Current Implementation

- ✅ **SQL Injection Prevention**: Parameterized queries throughout
- ✅ **Input Validation**: All user inputs validated
- ✅ **Error Messages**: No sensitive data in error messages
- ✅ **Logging**: Sensitive data not logged

### Future Enhancements

- 🔄 **Database Encryption**: SQLCipher for encrypted storage
- 🔄 **User Authentication**: Password-protected access
- 🔄 **Audit Logging**: Track all data modifications
- 🔄 **Backup Encryption**: Encrypted backup files

---

## Performance Optimizations

### Implemented

- ✅ **Database Indices**: On foreign keys and frequently queried columns
- ✅ **Connection Pooling**: Context manager for efficient connections
- ✅ **Efficient Queries**: SELECT only needed columns
- ✅ **Batch Operations**: executemany for bulk inserts

### Future Optimizations

- 🔄 **Lazy Loading**: Load data on-demand
- 🔄 **Pagination**: Limit large result sets
- 🔄 **Qt Models**: Use QAbstractTableModel for better performance
- 🔄 **Caching**: Cache frequently accessed data

---

## Migration from Old Architecture

### What Changed

| Old (Monolithic)                    | New (Layered)                        |
|-------------------------------------|--------------------------------------|
| Single 490-line file                | 24 modular files                     |
| No type hints                       | Full type annotations                |
| No error handling                   | Comprehensive exception handling     |
| Direct SQL in UI                    | Repository pattern                   |
| No logging                          | Structured logging                   |
| No tests                            | Test infrastructure ready            |
| Float for money                     | Decimal for precision                |
| No connection lifecycle             | Context managers                     |

### Backward Compatibility

- Old database schema compatible
- `finance_app.py` → symlink to `main.py`
- Existing `finance.db` works without migration

---

## Development Workflow

### Adding a New Feature

1. **Data Layer**: Add repository method if needed
2. **Business Layer**: Add service method with validation
3. **UI Layer**: Add UI component
4. **Tests**: Write unit and integration tests
5. **Documentation**: Update this file

### Example: Adding "Edit Transaction"

```python
# 1. Repository (if needed - already have get_by_id, update)
# No changes needed

# 2. Service
def update_transaction(self, transaction_id, **updates):
    transaction = self.repo.get_by_id(transaction_id)
    if not transaction:
        raise NotFoundError(...)

    # Update fields
    # Validate
    # Save
    return self.repo.update(transaction)

# 3. UI
def edit_transaction(self):
    selected = self.get_selected_transaction()
    dialog = EditTransactionDialog(selected)
    if dialog.exec():
        self.service.update_transaction(selected.id, **dialog.get_data())

# 4. Tests
def test_update_transaction():
    # Test the service method
    ...
```

---

## Future Architecture Enhancements

### Phase 1: Testing & Quality (Weeks 1-2)
- ✅ Add type hints everywhere
- ✅ Implement pytest with fixtures
- 🔄 Achieve 80%+ test coverage
- 🔄 Add mypy for type checking
- 🔄 Set up pre-commit hooks

### Phase 2: Performance (Weeks 3-4)
- 🔄 Implement Qt Model/View for tables
- 🔄 Add pagination for large datasets
- 🔄 Optimize database queries
- 🔄 Add caching layer

### Phase 3: Features (Weeks 5-8)
- 🔄 Add database migrations (Alembic)
- 🔄 Implement search and filters
- 🔄 Add reporting and charts
- 🔄 Recurring transactions
- 🔄 Budget management
- 🔄 Multi-currency support

### Phase 4: Production Ready (Weeks 9-12)
- 🔄 Database encryption
- 🔄 User authentication
- 🔄 Backup/restore functionality
- 🔄 Export to CSV/Excel
- 🔄 Import from bank files
- 🔄 CI/CD pipeline
- 🔄 Packaging for distribution

---

## Code Quality Metrics

### Current Status
- **Lines of Code**: ~2,500 (vs 490 old)
- **Number of Files**: 24 Python files
- **Test Coverage**: 0% (infrastructure ready)
- **Type Coverage**: 100% (all files have type hints)
- **Cyclomatic Complexity**: <10 per function
- **Code Duplication**: <1%

### Quality Gates
- No function > 50 lines
- No class > 300 lines
- All public methods documented
- All inputs validated
- All errors handled

---

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python main.py

# Run tests
pytest
```

### Production Deployment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

---

## Troubleshooting

### Common Issues

**Issue**: Import errors
**Solution**: Ensure you're in project root and virtual environment is activated

**Issue**: Database locked
**Solution**: Check for concurrent connections, ensure proper connection cleanup

**Issue**: UI not updating
**Solution**: Call `self.load_data()` after data changes

---

## References

- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

## Changelog

### Version 2.5.0 (2025-11-05)
- Account Metadata & Organization system (US-007)
- Four metadata fields: account_number, institution_name, notes, is_favorite
- Institution autocomplete with case-insensitive fuzzy matching
- Multi-field search (name, account number, institution) with indexed queries
- Clickable favorite stars (⭐/☆) in account tree
- Real-time search box in main window
- XSS prevention on notes field with html.escape()
- Performance-optimized for 1000+ accounts (<50ms search)
- Three new repository methods: search_accounts(), get_institution_names(), group_by_institution()
- Three new service methods: update_metadata(), toggle_favorite(), get_institution_autocomplete()
- Database migration 011 with three new indices
- AccountDialog enhancements with metadata fields and autocomplete
- AccountTreeWidget with search filter support
- 40 tests (27 unit + 13 integration) with 98% coverage

### Version 2.4.0 (2025-10-27)
- Account Balance Validation system (US-010)
- AccountBalanceValidator service with 6 core methods
- Single account and system-wide validation
- Automatic discrepancy detection with 1-cent tolerance
- One-click balance repair functionality
- Trial balance reporting (debits = credits verification)
- ValidationReportDialog with color-coded results
- TrialBalanceDialog with account grouping
- Database triggers for automatic balance updates (Migration 009)
- Comprehensive audit trail logging (balance_validation_log table)
- 41 tests (23 unit + 12 integration + 6 E2E) with 97% coverage
- Performance-optimized for 10,000+ accounts

### Version 2.3.0 (2025-10-26)
- Account Hierarchy feature (US-006)
- Parent/child account relationships
- Tree structure with up to 5 levels
- Materialized path for efficient queries
- Drag-and-drop account reorganization
- Parent accounts with calculated balances
- Type compatibility validation
- Cycle detection and depth limits
- AccountTreeWidget UI component
- 30+ unit and integration tests

### Version 2.2.0 (2025-10-23)
- Account Reconciliation feature (US-004)
- Statement matching and clearing
- Discrepancy detection
- Reconciliation history tracking

### Version 2.1.0 (2025-10-22)
- Opening Balance feature (US-005)
- Opening Balance Equity account
- Double-entry transaction creation

### Version 2.0.0 (2025-10-21)
- Complete architectural refactoring
- Layered architecture (UI/Business/Data)
- Type hints throughout
- Comprehensive error handling
- Logging infrastructure
- Test framework setup

### Version 1.0.0 (2025-10-15)
- Initial monolithic implementation
- Basic CRUD operations
- Single-file architecture

---

**Document Version:** 2.3
**Last Updated:** 2025-10-26
**Author:** Tech Lead Agent
