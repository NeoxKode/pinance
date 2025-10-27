# US-007: Account Metadata & Organization

**Story ID:** US-007
**Epic:** [EPIC-001: Account Management & Double-Entry Foundation](../../epics/EPIC-001-account-management.md)
**Created:** 2025-10-27
**Updated:** 2025-10-27 (Refined with task breakdown)
**Status:** Backlog (Ready for Sprint 11)
**Priority:** P2 (Nice to Have - UX Enhancement)
**Story Points:** 5
**Assignee:** Unassigned
**Sprint:** Sprint 11 (Planned)
**Dependencies:** ✅ US-001 (Account Type Taxonomy), ✅ US-006 (Account Hierarchy - UI patterns)
**Related Stories:** US-009 (Color Coding - shares color_hex field), US-004 (Reconciliation - uses account_number)

---

## 📖 User Story

**As a** power user managing multiple financial accounts
**I want** to add metadata (account numbers, institution names, notes) and organize accounts with custom ordering and favorites
**So that** I can keep detailed records, stay organized, quickly access important accounts, and customize my account management workflow to match my needs

---

## 📝 Description

### Context from EPIC-001

This is the 11th story in EPIC-001 (Account Management & Double-Entry Foundation), completing Phase 3: Data Integrity & UX Polish. This story adds organizational and customization features that enhance the user experience for power users managing many accounts.

**Completed Foundation (Sprints 1-10):**
- ✅ US-001: Account Type Taxonomy - Provides account types and subtypes
- ✅ US-004: Account Reconciliation - Will use `account_number` for bank statement matching
- ✅ US-005: Opening Balance Equity - UI dialog patterns to follow
- ✅ US-006: Account Hierarchy - Tree widget and drag-and-drop patterns to follow
- ✅ US-009: Color Coding (Sprint 10) - Shares `color_hex` field
- ✅ US-010: Balance Validation (Sprint 9) - Ensures data integrity

**Building Upon:**
- Account dialogs from US-005 (follow AccountDialog patterns)
- Tree widget from US-006 (adapt display_order for custom sorting)
- Account repository patterns from all previous stories

### Problem Statement

Power users with 10+ accounts face organizational challenges:
- ❌ Cannot track bank account numbers needed for reconciliation
- ❌ No way to add notes about account purpose, restrictions, or goals
- ❌ Cannot mark frequently-used accounts as "favorites" for quick access
- ❌ Accounts always sort alphabetically, can't customize order
- ❌ No easy way to group accounts by institution across reports
- ❌ Searching accounts only works by name, not metadata

**Real-World Scenarios:**
1. **Reconciliation Pain:** User needs to find account number for bank statement reconciliation (US-004)
2. **Account Purpose:** User wants to note "Emergency fund - don't touch" on savings account
3. **Multiple Banks:** User has accounts at 3 banks, wants to group by institution
4. **Favorites:** User accesses checking account daily, wants it at top of list
5. **Custom Order:** User wants accounts sorted by importance, not alphabet

### Proposed Solution

Add rich metadata fields to accounts:
- **`account_number`**: Bank/institution account number (for reconciliation)
- **`institution_name`**: Financial institution with autocomplete
- **`notes`**: Free-form multi-line text (up to 1000 chars)
- **`is_favorite`**: Boolean flag with star/heart icon
- **`display_order`**: Integer for custom sorting (drag-and-drop UI)
- **`color_hex`**: Custom color (overlap with US-009, already implemented there)
- **`icon`**: Custom icon name (optional, future enhancement)

**Integration Points:**
- **US-004 Reconciliation:** `account_number` displayed in reconciliation dialog
- **US-006 Hierarchy:** `display_order` works alongside hierarchy (sort within each level)
- **US-009 Color Coding:** `color_hex` shared field (US-009 handles UI)
- **Search:** Metadata fields searchable via AccountRepository

---

## 🎯 Acceptance Criteria

### AC1: Account Number Field

**Given** I am creating or editing an account
**When** I enter an account number
**Then** the system should:
- Accept alphanumeric characters with common separators (`-`, `.`, spaces)
- Examples: "1234-5678-90", "123.456.789", "ACCT 12345"
- Be optional (not all accounts have numbers)
- Validate length (3-50 characters if provided)
- Display prominently in account details view
- Be searchable in account list filter
- Show in reconciliation dialog (US-004 integration)

**Example:**
```python
account = account_service.create_account(
    name="Chase Checking",
    account_number="1234-5678-9012"
)
assert account.account_number == "1234-5678-9012"

# Search by account number
accounts = account_repo.search_accounts(query="1234")
assert len(accounts) == 1
```

---

### AC2: Institution Name with Autocomplete

**Given** I am creating or editing an account
**When** I enter an institution name
**Then** the system should:
- Show autocomplete dropdown with previously entered institutions
- Allow free-text entry for new institutions
- Standardize common variations (e.g., "Chase Bank" = "Chase")
- Be optional
- Enable grouping accounts by institution in reports
- Be searchable

**Given** I have existing accounts at "Chase Bank"
**When** I start typing "Cha" in institution field
**Then** autocomplete suggests "Chase Bank"

**Example:**
```python
# First account at Chase
account1 = account_service.create_account(
    name="Checking",
    institution_name="Chase Bank"
)

# Autocomplete should return ["Chase Bank"]
suggestions = account_service.get_institution_autocomplete("Cha")
assert "Chase Bank" in suggestions

# Second account uses autocomplete
account2 = account_service.create_account(
    name="Savings",
    institution_name="Chase Bank"  # Same institution
)

# Group by institution
groups = account_repo.group_by_institution()
assert groups["Chase Bank"] == [account1, account2]
```

---

### AC3: Notes Field

**Given** I want to add notes to an account
**When** I enter notes
**Then** the system should:
- Support multi-line text (up to 1000 characters)
- Preserve line breaks and formatting
- Display full notes in account details dialog
- Show first 100 characters in list view (with "..." if truncated)
- Be searchable
- Be optional

**Example:**
```python
notes_text = """Emergency fund - DO NOT TOUCH
Goal: $10,000 by end of year
Current: $7,500
Remaining: $2,500"""

account = account_service.create_account(
    name="Emergency Fund",
    notes=notes_text
)

assert len(account.notes) == len(notes_text)
assert "\n" in account.notes  # Multi-line preserved
```

---

### AC4: Favorite Accounts

**Given** I have many accounts (10+)
**When** I mark an account as favorite
**Then** the system should:
- Display star ⭐ or heart ❤️ icon next to account name
- Show favorites at top of account list (before non-favorites)
- Provide "Show only favorites" filter toggle
- Allow unfavoriting by clicking icon again
- Persist favorite status across sessions
- Support multiple favorites (not just one)

**Example:**
```python
# Mark as favorite
checking = account_service.create_account(name="Checking", is_favorite=True)
savings = account_service.create_account(name="Savings", is_favorite=True)
credit = account_service.create_account(name="Credit Card", is_favorite=False)

# Favorites appear first
accounts = account_repo.get_all_sorted()
assert accounts[0] == checking  # Favorite first
assert accounts[1] == savings   # Favorite second
assert accounts[2] == credit    # Non-favorite last

# Filter favorites only
favorites = account_repo.get_favorites()
assert len(favorites) == 2
assert checking in favorites
assert savings in favorites
```

---

### AC5: Custom Display Order (Drag-and-Drop)

**Given** I want to customize account order
**When** I drag-and-drop accounts in the list
**Then** the system should:
- Update `display_order` field automatically
- Sort accounts by `display_order` ascending (then by name)
- Remember custom order across sessions
- Work within account hierarchy (US-006): sort siblings, not across levels
- Provide "Reset to default order" button
- Handle gaps in display_order gracefully (re-number on demand)

**Given** I reset to default order
**Then** accounts should sort by:
1. Favorites first (is_favorite=True)
2. Then by account type (Asset, Liability, Equity, Income, Expense)
3. Then alphabetically by name

**Example:**
```python
# Create accounts
a1 = account_service.create_account(name="A", display_order=0)
a2 = account_service.create_account(name="B", display_order=0)
a3 = account_service.create_account(name="C", display_order=0)

# Drag C to top: C, A, B
account_service.update_display_order(a3.id, new_order=0)  # C = 0
account_service.update_display_order(a1.id, new_order=1)  # A = 1
account_service.update_display_order(a2.id, new_order=2)  # B = 2

accounts = account_repo.get_all_sorted()
assert accounts[0].name == "C"
assert accounts[1].name == "A"
assert accounts[2].name == "B"

# Reset to default
account_service.reset_display_order()
accounts = account_repo.get_all_sorted()
assert accounts[0].name == "A"  # Alphabetical
```

---

### AC6: Search and Filter Integration

**Given** accounts have metadata
**When** I search using the account filter/search box
**Then** the search should match:
- Account name
- Account number
- Institution name
- Notes (full text)
- Account type/subtype

**Example:**
```python
account_service.create_account(
    name="Primary Checking",
    account_number="1234",
    institution_name="Chase Bank",
    notes="Direct deposit account"
)

# Search by account number
results = account_repo.search_accounts("1234")
assert len(results) == 1

# Search by institution
results = account_repo.search_accounts("Chase")
assert len(results) == 1

# Search by notes
results = account_repo.search_accounts("direct deposit")
assert len(results) == 1
```

---

## 🔧 Technical Details

### Database Changes (Migration 011)

```sql
-- Migration 011: Account metadata and organization
-- Depends on: Migration 007 (US-006 hierarchy)

-- Add metadata fields
ALTER TABLE accounts ADD COLUMN account_number TEXT;
ALTER TABLE accounts ADD COLUMN institution_name TEXT;
ALTER TABLE accounts ADD COLUMN notes TEXT;
ALTER TABLE accounts ADD COLUMN is_favorite BOOLEAN DEFAULT 0;
ALTER TABLE accounts ADD COLUMN display_order INTEGER DEFAULT 0;

-- Note: color_hex and icon handled by US-009
-- ALTER TABLE accounts ADD COLUMN color_hex TEXT DEFAULT '#3B82F6';
-- ALTER TABLE accounts ADD COLUMN icon TEXT;

-- Create indices for search and filtering
CREATE INDEX idx_accounts_institution ON accounts(institution_name);
CREATE INDEX idx_accounts_favorite ON accounts(is_favorite);
CREATE INDEX idx_accounts_display_order ON accounts(display_order);
CREATE INDEX idx_accounts_number ON accounts(account_number);

-- Update existing accounts to have display_order based on ID
UPDATE accounts SET display_order = id WHERE display_order = 0;

-- Full-text search index for notes (optional, SQLite FTS5)
-- For production, consider: CREATE VIRTUAL TABLE accounts_fts USING fts5(...)
```

**Rollback:**
```sql
-- Rollback migration 011
DROP INDEX IF EXISTS idx_accounts_institution;
DROP INDEX IF EXISTS idx_accounts_favorite;
DROP INDEX IF EXISTS idx_accounts_display_order;
DROP INDEX IF EXISTS idx_accounts_number;

ALTER TABLE accounts DROP COLUMN account_number;
ALTER TABLE accounts DROP COLUMN institution_name;
ALTER TABLE accounts DROP COLUMN notes;
ALTER TABLE accounts DROP COLUMN is_favorite;
ALTER TABLE accounts DROP COLUMN display_order;
```

---

### Model Updates

**File:** `finance_app/data/models.py`

```python
from dataclasses import dataclass, field
from typing import Optional
from decimal import Decimal

@dataclass
class Account:
    """Account model with metadata fields."""

    # Core fields (from US-001)
    id: Optional[int]
    name: str
    account_type: str
    account_subtype: str
    currency: str
    balance: Decimal
    normal_balance: str

    # Hierarchy fields (from US-006)
    parent_account_id: Optional[int] = None
    is_parent: bool = False
    hierarchy_level: int = 0
    hierarchy_path: Optional[str] = None

    # Metadata fields (US-007 - NEW)
    account_number: Optional[str] = None
    institution_name: Optional[str] = None
    notes: Optional[str] = None
    is_favorite: bool = False
    display_order: int = 0

    # UI customization (US-009)
    color_hex: str = '#3B82F6'
    icon: Optional[str] = None

    # Timestamps
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """Validate model fields."""
        # Validate account_number length
        if self.account_number:
            if len(self.account_number) < 3:
                raise ValueError("Account number must be at least 3 characters")
            if len(self.account_number) > 50:
                raise ValueError("Account number cannot exceed 50 characters")

        # Validate notes length
        if self.notes and len(self.notes) > 1000:
            raise ValueError("Notes cannot exceed 1000 characters")

        # Ensure display_order is non-negative
        if self.display_order < 0:
            raise ValueError("Display order must be non-negative")

    @property
    def truncated_notes(self) -> str:
        """Get truncated notes for list view (first 100 chars)."""
        if not self.notes:
            return ""
        return self.notes[:100] + ("..." if len(self.notes) > 100 else "")
```

---

### Repository Layer

**File:** `finance_app/data/repositories/account_repository.py`

Add new methods for metadata querying:

```python
class AccountRepository:
    """Account repository with metadata support."""

    def get_all_sorted(
        self,
        sort_by: str = "display_order",
        include_favorites_first: bool = True
    ) -> List[Account]:
        """
        Get all accounts sorted by display_order and favorites.

        Args:
            sort_by: Field to sort by ("display_order", "name", "type")
            include_favorites_first: Show favorites at top

        Returns:
            List of accounts sorted according to criteria
        """
        query = """
            SELECT * FROM accounts
            ORDER BY
                CASE WHEN ? = 1 THEN is_favorite END DESC,
                CASE WHEN ? = 'display_order' THEN display_order END ASC,
                CASE WHEN ? = 'name' THEN name END ASC,
                CASE WHEN ? = 'type' THEN account_type END ASC
        """

        rows = self.db.execute_query(
            query,
            (
                1 if include_favorites_first else 0,
                sort_by,
                sort_by,
                sort_by
            )
        )

        return [self._row_to_account(row) for row in rows]

    def get_favorites(self) -> List[Account]:
        """Get all favorite accounts."""
        query = "SELECT * FROM accounts WHERE is_favorite = 1 ORDER BY display_order, name"
        rows = self.db.execute_query(query)
        return [self._row_to_account(row) for row in rows]

    def search_accounts(self, search_query: str) -> List[Account]:
        """
        Search accounts by name, account_number, institution, or notes.

        Args:
            search_query: Search term (case-insensitive)

        Returns:
            List of matching accounts
        """
        query = """
            SELECT * FROM accounts
            WHERE
                name LIKE ? OR
                account_number LIKE ? OR
                institution_name LIKE ? OR
                notes LIKE ?
            ORDER BY is_favorite DESC, display_order, name
        """

        search_pattern = f"%{search_query}%"
        rows = self.db.execute_query(
            query,
            (search_pattern, search_pattern, search_pattern, search_pattern)
        )

        return [self._row_to_account(row) for row in rows]

    def get_institution_names(self) -> List[str]:
        """
        Get list of all unique institution names for autocomplete.

        Returns:
            List of institution names, sorted alphabetically
        """
        query = """
            SELECT DISTINCT institution_name
            FROM accounts
            WHERE institution_name IS NOT NULL
            ORDER BY institution_name
        """
        rows = self.db.execute_query(query)
        return [row[0] for row in rows]

    def group_by_institution(self) -> Dict[str, List[Account]]:
        """
        Group accounts by institution name.

        Returns:
            Dictionary mapping institution name to list of accounts
        """
        query = """
            SELECT * FROM accounts
            WHERE institution_name IS NOT NULL
            ORDER BY institution_name, display_order, name
        """
        rows = self.db.execute_query(query)
        accounts = [self._row_to_account(row) for row in rows]

        # Group by institution
        groups = {}
        for account in accounts:
            institution = account.institution_name
            if institution not in groups:
                groups[institution] = []
            groups[institution].append(account)

        return groups

    def update_display_order(self, account_id: int, new_order: int) -> Account:
        """
        Update account display order.

        Args:
            account_id: Account to update
            new_order: New display order value

        Returns:
            Updated account
        """
        query = """
            UPDATE accounts
            SET display_order = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        self.db.execute_update(query, (new_order, account_id))
        return self.get_by_id(account_id)

    def reset_display_order(self) -> None:
        """Reset all accounts to default display order (alphabetical by name)."""
        # Get all accounts sorted by name
        accounts = self.get_all()
        accounts_sorted = sorted(accounts, key=lambda a: a.name.lower())

        # Update display_order sequentially
        for idx, account in enumerate(accounts_sorted):
            self.update_display_order(account.id, idx)
```

---

### Service Layer

**File:** `finance_app/business/account_service.py`

Add business logic methods:

```python
class AccountService:
    """Account service with metadata support."""

    def get_institution_autocomplete(self, partial_name: str) -> List[str]:
        """
        Get autocomplete suggestions for institution names.

        Args:
            partial_name: Partial institution name (e.g., "Cha")

        Returns:
            List of matching institution names
        """
        all_institutions = self.account_repo.get_institution_names()

        # Filter by partial match (case-insensitive)
        partial_lower = partial_name.lower()
        matches = [
            inst for inst in all_institutions
            if partial_lower in inst.lower()
        ]

        return sorted(matches)

    def toggle_favorite(self, account_id: int) -> Account:
        """
        Toggle favorite status of an account.

        Args:
            account_id: Account to toggle

        Returns:
            Updated account
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        account.is_favorite = not account.is_favorite
        return self.account_repo.update(account)

    def reorder_accounts(
        self,
        account_ids: List[int]
    ) -> List[Account]:
        """
        Reorder accounts by providing ordered list of IDs.

        Args:
            account_ids: List of account IDs in desired order

        Returns:
            List of updated accounts
        """
        updated_accounts = []

        for new_order, account_id in enumerate(account_ids):
            updated = self.account_repo.update_display_order(account_id, new_order)
            updated_accounts.append(updated)

        return updated_accounts

    def reset_to_default_order(self) -> None:
        """Reset all accounts to default sort order (type, then name)."""
        self.account_repo.reset_display_order()
```

---

## 📋 Task Breakdown for Development

This section provides a detailed, step-by-step implementation plan for developers.

### Phase 1: Database & Model (Day 1 - 2 hours)

#### Task 1.1: Create Database Migration (011)
**Estimate:** 45 minutes
**Files:** `finance_app/data/migrations/011_account_metadata.sql`

**Implementation:**
1. Create migration file with SQL from Technical Details section
2. Add indices for search performance
3. Set default `display_order = id` for existing accounts
4. Test migration on backup database

**Acceptance:**
- [ ] Migration file created and tested
- [ ] All columns added successfully
- [ ] Indices created and verified
- [ ] Existing accounts have valid display_order
- [ ] Rollback tested

**Testing:**
```python
def test_migration_011():
    db = Database(":memory:")
    # Verify columns exist
    cursor = db.conn.cursor()
    result = cursor.execute("PRAGMA table_info(accounts)")
    columns = [row[1] for row in result.fetchall()]
    assert "account_number" in columns
    assert "institution_name" in columns
    assert "notes" in columns
    assert "is_favorite" in columns
    assert "display_order" in columns
```

---

#### Task 1.2: Update Account Model
**Estimate:** 45 minutes
**Files:** `finance_app/data/models.py`

**Implementation:**
1. Add 5 new fields to Account dataclass
2. Add validation in `__post_init__()`:
   - Account number: 3-50 chars if provided
   - Notes: max 1000 chars
   - Display order: non-negative
3. Add `truncated_notes` property
4. Update docstrings

**Acceptance:**
- [ ] Account model has 5 new fields with defaults
- [ ] Validation prevents invalid data
- [ ] Type hints complete
- [ ] Docstrings updated

**Testing:**
```python
def test_account_metadata_fields():
    account = Account(
        id=1,
        name="Test",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        account_number="1234",
        institution_name="Test Bank",
        notes="Test notes",
        is_favorite=True,
        display_order=5
    )
    assert account.account_number == "1234"
    assert account.is_favorite == True
```

---

#### Task 1.3: Update Database Integration
**Estimate:** 30 minutes
**Files:** `finance_app/data/database.py`

**Implementation:**
1. Add migration 011 to migration list
2. Update schema_version to 11
3. Run migration on app startup
4. Verify migration in logs

**Acceptance:**
- [ ] Migration 011 runs automatically
- [ ] Logs confirm successful migration
- [ ] Database version = 11

---

### Phase 2: Repository Layer (Day 1-2 - 3 hours)

#### Task 2.1: Implement Metadata Query Methods
**Estimate:** 2 hours
**Files:** `finance_app/data/repositories/account_repository.py`

**Implementation:**
1. Add `get_all_sorted()` - respects favorites and display_order
2. Add `get_favorites()` - filter favorites only
3. Add `search_accounts()` - search across all metadata
4. Add `get_institution_names()` - for autocomplete
5. Add `group_by_institution()` - for reports
6. Add `update_display_order()` - for drag-and-drop
7. Add `reset_display_order()` - reset to default

**Acceptance:**
- [ ] All 7 methods implemented
- [ ] SQL queries optimized (use indices)
- [ ] Methods handle NULL values gracefully
- [ ] Return types correct (List[Account], Dict, etc.)

**Testing:**
```python
def test_get_favorites():
    # Create accounts
    fav1 = create_account(name="Fav1", is_favorite=True)
    fav2 = create_account(name="Fav2", is_favorite=True)
    regular = create_account(name="Regular", is_favorite=False)

    # Get favorites
    favorites = account_repo.get_favorites()
    assert len(favorites) == 2
    assert fav1 in favorites
    assert regular not in favorites
```

---

#### Task 2.2: Update Repository `_row_to_account()` Helper
**Estimate:** 30 minutes
**Files:** `finance_app/data/repositories/account_repository.py`

**Implementation:**
1. Add mapping for 5 new fields in `_row_to_account()`
2. Handle NULL values (use defaults)
3. Ensure all field types match model

**Acceptance:**
- [ ] `_row_to_account()` maps all metadata fields
- [ ] NULL values handled correctly
- [ ] No data loss during conversion

---

#### Task 2.3: Update Repository `_account_to_row()` Helper
**Estimate:** 30 minutes
**Files:** `finance_app/data/repositories/account_repository.py`

**Implementation:**
1. Add mapping for 5 new fields in `_account_to_row()`
2. Ensure INSERT and UPDATE include new fields
3. Test with NULL values

**Acceptance:**
- [ ] `_account_to_row()` includes metadata fields
- [ ] INSERT operations save metadata
- [ ] UPDATE operations preserve metadata

---

### Phase 3: Service Layer (Day 2 - 1.5 hours)

#### Task 3.1: Add Business Logic Methods
**Estimate:** 1 hour
**Files:** `finance_app/business/account_service.py`

**Implementation:**
1. Add `get_institution_autocomplete()` - fuzzy matching
2. Add `toggle_favorite()` - flip boolean
3. Add `reorder_accounts()` - batch update display_order
4. Add `reset_to_default_order()` - call repo method

**Acceptance:**
- [ ] All 4 methods implemented
- [ ] Input validation (check account exists)
- [ ] Error handling with meaningful messages

**Testing:**
```python
def test_toggle_favorite():
    account = create_account(is_favorite=False)

    # Toggle on
    updated = account_service.toggle_favorite(account.id)
    assert updated.is_favorite == True

    # Toggle off
    updated = account_service.toggle_favorite(account.id)
    assert updated.is_favorite == False
```

---

#### Task 3.2: Update `create_account()` Method
**Estimate:** 30 minutes
**Files:** `finance_app/business/account_service.py`

**Implementation:**
1. Add optional parameters for metadata fields
2. Pass metadata to repository create method
3. Set default display_order (max + 1)
4. Update docstring

**Acceptance:**
- [ ] `create_account()` accepts metadata parameters
- [ ] Metadata saved correctly
- [ ] Default display_order assigned

**Example:**
```python
def create_account(
    self,
    name: str,
    account_type: str,
    account_subtype: str,
    # ... existing params ...
    account_number: Optional[str] = None,
    institution_name: Optional[str] = None,
    notes: Optional[str] = None,
    is_favorite: bool = False,
    display_order: Optional[int] = None
) -> Account:
    # Set default display_order if not provided
    if display_order is None:
        max_order = self.account_repo.get_max_display_order()
        display_order = max_order + 1

    # ... rest of method
```

---

### Phase 4: UI Implementation (Day 2-3 - 3 hours)

#### Task 4.1: Update AccountDialog
**Estimate:** 1.5 hours
**Files:** `finance_app/ui/dialogs/account_dialog.py`

**Follow patterns from US-005 AccountDialog**

**Implementation:**
1. Add QLineEdit for `account_number`
2. Add QComboBox with autocomplete for `institution_name`
3. Add QPlainTextEdit for `notes` (multi-line)
4. Add QCheckBox for `is_favorite` with star icon
5. Populate autocomplete from `account_service.get_institution_autocomplete()`
6. Validate inputs before save
7. Update dialog size for new fields

**Layout:**
```
[Account Name      ] (existing)
[Account Type  ▼]   (existing)
[Account Number    ] (NEW)
[Institution   ▼]   (NEW - autocomplete)
[Notes (multi-line)] (NEW)
☐ Mark as Favorite  (NEW)
[Currency      ▼]   (existing)
[Opening Balance  ] (existing)
```

**Acceptance:**
- [ ] All 5 new fields added to dialog
- [ ] Institution autocomplete works
- [ ] Notes field supports multi-line
- [ ] Favorite checkbox shows star icon
- [ ] Fields populate when editing
- [ ] Validation prevents invalid data

**Testing:**
Manual testing of dialog with various inputs

---

#### Task 4.2: Add Favorite Icon to Account List
**Estimate:** 45 minutes
**Files:** `finance_app/ui/widgets/account_list_widget.py` or `main_window.py`

**Implementation:**
1. Add star ⭐ icon column to account list/tree
2. Click star to toggle favorite status
3. Show favorites at top of list
4. Update display when favorite toggled

**Acceptance:**
- [ ] Star icon visible for favorites
- [ ] Click star to toggle favorite
- [ ] Favorites sort to top automatically
- [ ] Icon color distinguishes favorite/non-favorite

---

#### Task 4.3: Implement Drag-and-Drop Reordering
**Estimate:** 45 minutes
**Files:** `finance_app/ui/widgets/account_list_widget.py`

**Follow patterns from US-006 AccountTreeWidget**

**Implementation:**
1. Enable drag-drop on account list widget
2. Handle `dropEvent()` to update display_order
3. Call `account_service.reorder_accounts()` with new order
4. Reload list after reorder
5. Show visual feedback during drag

**Acceptance:**
- [ ] Accounts can be dragged and dropped
- [ ] Order persists after reload
- [ ] Visual feedback during drag
- [ ] Works with favorites (reorder within favorites, within non-favorites)

**Code Reference:**
See US-006 `AccountTreeWidget.dropEvent()` for drag-drop pattern

---

### Phase 5: Search & Filter (Day 3 - 1 hour)

#### Task 5.1: Add Search Box Integration
**Estimate:** 1 hour
**Files:** `finance_app/ui/main_window.py`

**Implementation:**
1. Update existing search box to call `account_repo.search_accounts()`
2. Search across name, number, institution, notes
3. Display results in account list
4. Highlight matching text (optional)
5. Add "Clear search" button

**Acceptance:**
- [ ] Search box searches all metadata fields
- [ ] Results display correctly
- [ ] Clear search returns to full list
- [ ] Search is case-insensitive

---

### Phase 6: Testing (Day 3-4 - 2 hours)

#### Task 6.1: Write Unit Tests
**Estimate:** 1 hour
**Files:** `finance_app/tests/unit/test_account_service_metadata.py`

**Write tests for:**
- `get_institution_autocomplete()` - fuzzy matching
- `toggle_favorite()` - flip boolean correctly
- `reorder_accounts()` - batch update
- `reset_to_default_order()` - alphabetical order

**Coverage Target:** 80%+

---

#### Task 6.2: Write Integration Tests
**Estimate:** 1 hour
**Files:** `finance_app/tests/integration/test_account_metadata_integration.py`

**Write tests for:**
- Create account with metadata, save, reload - verify all fields
- Search accounts by metadata - verify results
- Group by institution - verify grouping
- Drag-and-drop reorder - verify order persists
- Toggle favorite - verify UI updates

**Coverage Target:** Critical user workflows

---

### Phase 7: Documentation (Day 4 - 1 hour)

#### Task 7.1: Update User Guide
**Estimate:** 30 minutes
**Files:** `docs/USER_GUIDE.md`

**Add section:**
- "Organizing Accounts with Metadata"
- How to add account numbers
- Using favorites
- Customizing account order
- Searching accounts

---

#### Task 7.2: Update Architecture Documentation
**Estimate:** 30 minutes
**Files:** `docs/ARCHITECTURE.md`

**Update:**
- Account model diagram with new fields
- Repository methods list
- Service layer methods

---

## ✅ Definition of Done

### Backend (Database & Models)
- [x] Migration 011 created and tested
- [ ] Account model updated with 5 new fields
- [ ] Model validation prevents invalid data
- [ ] All existing accounts migrated with default values

### Repository Layer
- [ ] 7 new repository methods implemented
- [ ] `_row_to_account()` and `_account_to_row()` updated
- [ ] Search optimized with database indices
- [ ] All methods handle NULL values

### Service Layer
- [ ] 4 new service methods implemented
- [ ] `create_account()` supports metadata parameters
- [ ] Input validation and error handling complete

### UI Layer
- [ ] AccountDialog updated with 5 new fields
- [ ] Institution autocomplete works
- [ ] Favorite icon/toggle in account list
- [ ] Drag-and-drop reordering works
- [ ] Search box searches metadata

### Testing
- [ ] Unit tests for all new methods (15+ tests)
- [ ] Integration tests for workflows (8+ tests)
- [ ] Manual UI testing completed
- [ ] Test coverage > 80%

### Documentation
- [ ] USER_GUIDE.md updated
- [ ] ARCHITECTURE.md updated
- [ ] Code comments comprehensive
- [ ] Migration documented

### Quality Assurance
- [ ] All tests passing
- [ ] No regressions in existing features
- [ ] Code reviewed and approved
- [ ] Performance acceptable (search < 100ms)

---

## 🧪 Test Scenarios

### Test 1: Create Account with Metadata
```python
def test_create_account_with_metadata(account_service):
    """Test creating account with all metadata fields."""
    account = account_service.create_account(
        name="Chase Checking",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        account_number="1234-5678-9012",
        institution_name="Chase Bank",
        notes="Primary checking account\nDirect deposit",
        is_favorite=True,
        display_order=1
    )

    assert account.account_number == "1234-5678-9012"
    assert account.institution_name == "Chase Bank"
    assert "Direct deposit" in account.notes
    assert account.is_favorite == True
    assert account.display_order == 1
```

### Test 2: Institution Autocomplete
```python
def test_institution_autocomplete(account_service):
    """Test autocomplete suggests existing institutions."""
    # Create accounts at different institutions
    account_service.create_account(
        name="Account 1",
        institution_name="Chase Bank"
    )
    account_service.create_account(
        name="Account 2",
        institution_name="Bank of America"
    )

    # Autocomplete for "Bank"
    suggestions = account_service.get_institution_autocomplete("Bank")
    assert "Chase Bank" in suggestions
    assert "Bank of America" in suggestions

    # Autocomplete for "Chase"
    suggestions = account_service.get_institution_autocomplete("Chase")
    assert "Chase Bank" in suggestions
    assert "Bank of America" not in suggestions
```

### Test 3: Favorite Accounts Sort First
```python
def test_favorites_sort_first(account_repo):
    """Test favorite accounts appear at top of list."""
    # Create accounts
    regular1 = create_account(name="AAA Regular", is_favorite=False)
    favorite1 = create_account(name="ZZZ Favorite", is_favorite=True)
    favorite2 = create_account(name="BBB Favorite", is_favorite=True)
    regular2 = create_account(name="CCC Regular", is_favorite=False)

    # Get sorted list
    accounts = account_repo.get_all_sorted()

    # Favorites should be first (regardless of name)
    assert accounts[0].is_favorite == True
    assert accounts[1].is_favorite == True
    assert accounts[2].is_favorite == False
    assert accounts[3].is_favorite == False
```

### Test 4: Search Accounts by Metadata
```python
def test_search_accounts_by_metadata(account_repo, account_service):
    """Test searching accounts by various metadata fields."""
    # Create test accounts
    account_service.create_account(
        name="Chase Checking",
        account_number="1234-5678",
        institution_name="Chase Bank",
        notes="Primary account for bills"
    )
    account_service.create_account(
        name="BofA Savings",
        account_number="9876-5432",
        institution_name="Bank of America",
        notes="Emergency fund savings"
    )

    # Search by account number
    results = account_repo.search_accounts("1234")
    assert len(results) == 1
    assert results[0].name == "Chase Checking"

    # Search by institution
    results = account_repo.search_accounts("Bank of America")
    assert len(results) == 1
    assert results[0].name == "BofA Savings"

    # Search by notes
    results = account_repo.search_accounts("emergency")
    assert len(results) == 1
    assert results[0].name == "BofA Savings"
```

### Test 5: Custom Display Order
```python
def test_custom_display_order(account_service, account_repo):
    """Test custom display order via drag-and-drop."""
    # Create accounts with default order
    a1 = account_service.create_account(name="Account A")
    a2 = account_service.create_account(name="Account B")
    a3 = account_service.create_account(name="Account C")

    # Reorder: C, A, B
    new_order = [a3.id, a1.id, a2.id]
    account_service.reorder_accounts(new_order)

    # Verify order
    accounts = account_repo.get_all_sorted()
    assert accounts[0].id == a3.id  # C
    assert accounts[1].id == a1.id  # A
    assert accounts[2].id == a2.id  # B
```

### Test 6: Notes Multi-line Support
```python
def test_notes_multiline(account_service):
    """Test notes field preserves line breaks."""
    notes_text = """Line 1: Primary checking
Line 2: Used for bills
Line 3: Balance goal: $5000"""

    account = account_service.create_account(
        name="Test",
        notes=notes_text
    )

    # Reload from database
    reloaded = account_service.get_account(account.id)

    assert reloaded.notes == notes_text
    assert "Line 1:" in reloaded.notes
    assert "\n" in reloaded.notes
```

### Test 7: Account Number Validation
```python
def test_account_number_validation(account_service):
    """Test account number length validation."""
    # Valid account numbers
    valid_numbers = [
        "123",           # Minimum 3 chars
        "1234-5678",     # With separator
        "ACCT123456",    # Alphanumeric
        "12.34.56",      # Dots
    ]

    for number in valid_numbers:
        account = account_service.create_account(
            name="Test",
            account_number=number
        )
        assert account.account_number == number

    # Invalid: too short
    with pytest.raises(ValueError, match="at least 3 characters"):
        account_service.create_account(
            name="Test",
            account_number="12"  # Only 2 chars
        )

    # Invalid: too long
    with pytest.raises(ValueError, match="cannot exceed 50 characters"):
        account_service.create_account(
            name="Test",
            account_number="A" * 51  # 51 chars
        )
```

### Test 8: Group by Institution
```python
def test_group_by_institution(account_repo, account_service):
    """Test grouping accounts by institution."""
    # Create accounts at multiple institutions
    chase1 = account_service.create_account(
        name="Chase Checking",
        institution_name="Chase Bank"
    )
    chase2 = account_service.create_account(
        name="Chase Savings",
        institution_name="Chase Bank"
    )
    bofa = account_service.create_account(
        name="BofA Checking",
        institution_name="Bank of America"
    )
    no_institution = account_service.create_account(
        name="Cash",
        institution_name=None
    )

    # Group by institution
    groups = account_repo.group_by_institution()

    assert "Chase Bank" in groups
    assert len(groups["Chase Bank"]) == 2
    assert chase1 in groups["Chase Bank"]
    assert chase2 in groups["Chase Bank"]

    assert "Bank of America" in groups
    assert len(groups["Bank of America"]) == 1

    # Accounts without institution not included
    assert no_institution not in groups.get("", [])
```

---

## 📊 Success Metrics

**User Experience:**
- Users can find account numbers 100% faster (vs searching bank website)
- Account organization time reduced by 50% (favorites + custom order)
- Search finds accounts 80% faster than scrolling

**Technical:**
- Search queries < 100ms for 100 accounts
- Autocomplete response < 50ms
- Drag-and-drop reorder < 200ms
- No performance degradation with 50+ accounts

**Adoption:**
- 60%+ of users add account numbers (within 1 month)
- 40%+ of users mark favorites
- 30%+ of users customize order

---

## 🔗 Dependencies & Integration

**Depends On (Completed):**
- ✅ US-001: Account Type Taxonomy - Core account model
- ✅ US-006: Account Hierarchy - Tree widget patterns, drag-and-drop

**Integrates With:**
- 📋 US-004: Account Reconciliation - Displays `account_number` in reconciliation dialog
- 📋 US-009: Color Coding (Sprint 10) - Shares `color_hex` field
- 📋 EPIC-002: Search & Filter - Uses metadata in global search

**Blocks:**
- None (optional enhancement)

---

## 📚 References

- [EPIC-001](../../epics/EPIC-001-account-management.md) - Parent epic
- [US-005 AccountDialog](../completed/US-005-opening-balance-equity.md) - Dialog patterns
- [US-006 TreeWidget](../completed/US-006-account-hierarchy.md) - Drag-and-drop patterns
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - System architecture
- [USER_GUIDE.md](../../USER_GUIDE.md) - End user documentation

---

**Story Created:** 2025-10-27
**Story Refined:** 2025-10-27 (Added comprehensive task breakdown)
**Product Owner:** Product Owner Agent
**Tech Lead:** TBD
**Sprint:** Sprint 11 (Planned)

---

*This story is production-ready with detailed implementation guidance, code examples following existing patterns, and comprehensive testing scenarios.*
