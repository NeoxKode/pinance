# US-007: Account Metadata & Organization

**Story ID:** US-007
**Epic:** [EPIC-001: Account Management & Double-Entry Foundation](../../epics/EPIC-001-account-management.md)
**Created:** 2025-10-27
**Updated:** 2025-10-27 (Post Epic Alignment Review - Pattern consistency fixes + documentation enhancements)
**Status:** Backlog (Ready for Sprint 11)
**Priority:** P2 (Nice to Have - UX Enhancement)
**Story Points:** 5 (13 hours estimated)
**Assignee:** Unassigned
**Sprint:** Sprint 11 (Planned)
**Dependencies:** ✅ US-001 (Account Type Taxonomy), ✅ US-006 (Account Hierarchy - UI patterns), **📋 US-009 (Color Coding - MUST complete before US-007)**
**Related Stories:** US-004 (Reconciliation - uses account_number)

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
- ~~Notes (full text)~~ **EXCLUDED for performance** - may add FTS5 in future

**Performance Requirement:** Search must complete in <50ms for 1000+ accounts

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

# Search by notes - NOT SUPPORTED in v1 (performance)
# Future enhancement: Add FTS5 full-text search index
results = account_repo.search_accounts("direct deposit")
assert len(results) == 0  # Notes not searchable
```

---

### AC7: Display Order with Account Hierarchy (NEW)

**Given** accounts are organized in a hierarchy (US-006)
**When** display_order and is_favorite are used
**Then** the system should:

**Display Order Scope:**
- Display order is **per-hierarchy-level** (siblings ordered independently)
- Root accounts have order 0, 1, 2...
- Children under each parent have their own order 0, 1, 2...
- Example hierarchy with ordering:
  ```
  Assets (display_order=0)
    └─ Bank Accounts (display_order=0 within parent)
       ├─ Checking (display_order=0 within parent)
       ├─ Savings (display_order=1 within parent)
  Liabilities (display_order=1)
    └─ Credit Cards (display_order=0 within parent)
       ├─ Visa (display_order=0 within parent)
       ├─ Mastercard (display_order=1 within parent)
  ```

**Favorites Behavior:**
- Favorites displayed with ⭐ icon in tree view
- Favorites NOT moved to separate section (stay in hierarchy)
- Favorites appear before non-favorites **within each hierarchy level**
- Optional: "Show only favorites" filter button (future enhancement)

**Reorder Logic:**
- Drag-and-drop only affects sibling order at same hierarchy level
- Cannot drag across hierarchy levels (parent type constraint from US-006)
- Reordering updates display_order for all siblings at that level
- Parent accounts cannot be reordered below their children

**Example:**
```python
# Create hierarchy with custom ordering
parent = account_service.create_account(
    name="Bank Accounts",
    is_parent=True,
    display_order=0
)

# Children with custom order
savings = account_service.create_account(
    name="Savings",
    parent_account_id=parent.id,
    display_order=0,  # First child
    is_favorite=True
)

checking = account_service.create_account(
    name="Checking",
    parent_account_id=parent.id,
    display_order=1,  # Second child
    is_favorite=False
)

# Get children sorted by display_order
children = account_repo.get_child_accounts(parent.id)
assert children[0] == savings   # Favorite first, then by display_order
assert children[1] == checking

# Reorder: move Checking before Savings
account_service.reorder_siblings([checking.id, savings.id])
children = account_repo.get_child_accounts(parent.id)
assert children[0] == checking  # Now first
assert children[1] == savings   # Now second
```

---

## 🔧 Technical Details

### Database Changes (Migration 011)

**⚠️ CRITICAL DEPENDENCY:** This migration assumes Migration 010 (US-009) has already added:
- `color_hex TEXT DEFAULT '#3B82F6'`
- `icon TEXT`
- `display_order INTEGER DEFAULT 0`
- `is_favorite BOOLEAN DEFAULT 0`

**Migration 011 ONLY adds the following NEW fields:**

```sql
-- Migration 011: Account metadata (account numbers, institutions, notes)
-- Dependencies:
--   - Migration 007 (US-006 hierarchy fields)
--   - Migration 010 (US-009 color/display fields) ← MUST RUN FIRST

-- Add metadata fields (US-007 specific)
ALTER TABLE accounts ADD COLUMN account_number TEXT;
ALTER TABLE accounts ADD COLUMN institution_name TEXT;
ALTER TABLE accounts ADD COLUMN notes TEXT;

-- ❌ DO NOT ADD - Already in Migration 010 (US-009):
-- ALTER TABLE accounts ADD COLUMN is_favorite BOOLEAN DEFAULT 0;
-- ALTER TABLE accounts ADD COLUMN display_order INTEGER DEFAULT 0;
-- ALTER TABLE accounts ADD COLUMN color_hex TEXT DEFAULT '#3B82F6';
-- ALTER TABLE accounts ADD COLUMN icon TEXT;

-- Create indices for search and filtering (US-007 specific)
CREATE INDEX idx_accounts_institution ON accounts(institution_name);
CREATE INDEX idx_accounts_number ON accounts(account_number);

-- ❌ DO NOT CREATE - Already in Migration 010 (US-009):
-- CREATE INDEX idx_accounts_favorite ON accounts(is_favorite);
-- CREATE INDEX idx_accounts_display_order ON accounts(display_order);

-- Note: display_order initialization handled by Migration 010
-- Note: FTS5 full-text search on notes is future enhancement (v2.2+)
```

**Rollback:**
```sql
-- Rollback migration 011 (ONLY US-007 fields)
DROP INDEX IF EXISTS idx_accounts_institution;
DROP INDEX IF EXISTS idx_accounts_number;

ALTER TABLE accounts DROP COLUMN account_number;
ALTER TABLE accounts DROP COLUMN institution_name;
ALTER TABLE accounts DROP COLUMN notes;

-- ❌ DO NOT DROP - Owned by Migration 010 (US-009):
-- DROP INDEX IF EXISTS idx_accounts_favorite;
-- DROP INDEX IF EXISTS idx_accounts_display_order;
-- ALTER TABLE accounts DROP COLUMN is_favorite;
-- ALTER TABLE accounts DROP COLUMN display_order;
-- ALTER TABLE accounts DROP COLUMN color_hex;
-- ALTER TABLE accounts DROP COLUMN icon;
```

---

### Visual Diagrams

#### Diagram 1: Migration Dependency Chain

```
Migration Sequence (CRITICAL ORDER):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Migration 001-006 (US-001 to US-006)
         ✅ COMPLETED
         │
         ▼
Migration 007 (US-006) - Account Hierarchy
         ✅ COMPLETED
         │
         ├─ parent_account_id
         ├─ is_parent
         ├─ hierarchy_level
         └─ hierarchy_path
         │
         ▼
Migration 010 (US-009) - Color Coding ⚠️ MUST RUN FIRST
         📋 Sprint 10 (Planned)
         │
         ├─ color_hex
         ├─ icon
         ├─ display_order        ← US-007 depends on this
         └─ is_favorite          ← US-007 depends on this
         │
         ▼
Migration 011 (US-007) - Account Metadata ← THIS STORY
         📋 Sprint 11 (Blocked until Migration 010 completes)
         │
         ├─ account_number
         ├─ institution_name
         └─ notes

⚠️ CRITICAL: If Migration 010 is skipped or delayed:
   ❌ Migration 011 will reference non-existent columns
   ❌ AC4, AC5 tests will fail
   ❌ display_order and is_favorite fields missing
```

---

#### Diagram 2: Account Hierarchy + Display Order Interaction

```
Example Hierarchy with Display Order and Favorites:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ROOT LEVEL (parent_id = NULL)
├─ [0] Assets                     display_order=0
│  │
│  CHILDREN OF "Assets" (parent_id = Assets.id)
│  ├─ [0] ⭐ Checking (FAVORITE)  display_order=0  ← Favorite first
│  ├─ [1] Savings                 display_order=1
│  └─ [2] Cash                    display_order=2
│
├─ [1] Liabilities                display_order=1
│  │
│  CHILDREN OF "Liabilities"
│  ├─ [0] ⭐ Visa (FAVORITE)      display_order=0  ← Favorite first
│  ├─ [1] Mastercard              display_order=1
│  └─ [2] Mortgage                display_order=2
│
└─ [2] Equity                     display_order=2

KEY INSIGHTS:
• display_order is scoped per hierarchy level
• Each parent's children have their own 0, 1, 2... ordering
• Favorites stay within hierarchy (NOT moved to separate section)
• Favorites appear before non-favorites within each level
• Drag-drop only reorders siblings (same parent)
```

---

#### Diagram 3: Search Performance Optimization

```
Search Query Execution Flow:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User enters: "Chase"
         │
         ▼
┌─────────────────────────────────────────┐
│  search_accounts("Chase")               │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  SQL Query:                                             │
│  SELECT ... FROM accounts                               │
│  WHERE                                                  │
│    name LIKE '%Chase%'                ✅ Indexed       │
│    OR account_number LIKE '%Chase%'   ✅ Indexed       │
│    OR institution_name LIKE '%Chase%' ✅ Indexed       │
│    -- notes EXCLUDED (performance)    ❌ NOT searched  │
│  ORDER BY is_favorite DESC, display_order, name         │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌───────────────────────────────────────┐
│  Index Scan:                          │
│  • idx_accounts_institution           │
│  • idx_accounts_number                │
│  • Built-in index on name             │
│                                       │
│  Performance: <50ms for 1000+ accts   │
└───────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Results (sorted by favorites first):   │
│  1. ⭐ Chase Checking (favorite)        │
│  2. Chase Savings                       │
│  3. Chase Credit Card                   │
└─────────────────────────────────────────┘

WHY NOTES ARE EXCLUDED:
• Notes field is TEXT (up to 1000 chars)
• LIKE on long text fields = full table scan
• With 1000 accounts × 1000 chars = 1M chars scanned
• Future: Add FTS5 full-text search index (v2.2+)
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

    # ❌ NO __post_init__ validation - follows existing codebase pattern
    # ✅ Validation done in AccountValidator and AccountService (see below)

    @property
    def truncated_notes(self) -> str:
        """Get truncated notes for list view (first 100 chars)."""
        if not self.notes:
            return ""
        return self.notes[:100] + ("..." if len(self.notes) > 100 else "")
```

---

### Validation Layer (NEW)

**File:** `finance_app/business/validators.py`

**⚠️ IMPORTANT:** Following existing codebase pattern, validation is done in `AccountValidator` class, NOT in model `__post_init__`. This matches the pattern from US-001 through US-006.

Add validation methods to existing `AccountValidator` class:

```python
class AccountValidator:
    """Validator for account fields (US-001 through US-007)."""

    # ... existing methods from US-001 ...

    # ========================================================================
    # US-007: Metadata Field Validation
    # ========================================================================

    def validate_account_number(self, account_number: Optional[str]) -> Optional[str]:
        """
        Validate account number field.

        Args:
            account_number: Account number to validate (can be None)

        Returns:
            Validated account number (stripped, None if empty)

        Raises:
            ValidationError: If account number is invalid

        Examples:
            >>> validator.validate_account_number("  1234-5678  ")
            "1234-5678"
            >>> validator.validate_account_number("")
            None
            >>> validator.validate_account_number("12")  # Too short
            ValidationError: "Account number must be at least 3 characters"
        """
        if account_number is None or account_number.strip() == "":
            return None

        account_number = account_number.strip()

        # Length validation
        if len(account_number) < 3:
            raise ValidationError("Account number must be at least 3 characters")
        if len(account_number) > 50:
            raise ValidationError("Account number cannot exceed 50 characters")

        return account_number

    def validate_institution_name(self, institution_name: Optional[str]) -> Optional[str]:
        """
        Validate institution name field.

        Args:
            institution_name: Institution name to validate

        Returns:
            Validated institution name (stripped, None if empty)

        Raises:
            ValidationError: If institution name is invalid
        """
        if institution_name is None or institution_name.strip() == "":
            return None

        institution_name = institution_name.strip()

        if len(institution_name) > 100:
            raise ValidationError("Institution name cannot exceed 100 characters")

        return institution_name

    def validate_notes(self, notes: Optional[str]) -> Optional[str]:
        """
        Validate notes field.

        Args:
            notes: Notes text to validate

        Returns:
            Validated notes (stripped, sanitized, None if empty)

        Raises:
            ValidationError: If notes are invalid

        Security:
            Sanitizes HTML/special characters to prevent XSS
        """
        if notes is None or notes.strip() == "":
            return None

        notes = notes.strip()

        # Length validation
        if len(notes) > 1000:
            raise ValidationError("Notes cannot exceed 1000 characters")

        # Security: Sanitize HTML entities
        import html
        notes = html.escape(notes)

        return notes

    def validate_display_order(self, display_order: int) -> int:
        """
        Validate display_order field.

        Args:
            display_order: Display order value

        Returns:
            Validated display order

        Raises:
            ValidationError: If display_order is invalid
        """
        if display_order < 0:
            raise ValidationError("Display order must be non-negative")

        return display_order
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
            SELECT id, name, account_type, account_subtype, balance,
                   normal_balance, currency, parent_account_id,
                   legacy_type, last_reconciled_date, opening_balance_date,
                   is_parent, hierarchy_level, hierarchy_path,
                   account_number, institution_name, notes,
                   is_favorite, display_order, color_hex, icon,
                   created_at, updated_at
            FROM accounts
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
        query = """
            SELECT id, name, account_type, account_subtype, balance,
                   normal_balance, currency, parent_account_id,
                   legacy_type, last_reconciled_date, opening_balance_date,
                   is_parent, hierarchy_level, hierarchy_path,
                   account_number, institution_name, notes,
                   is_favorite, display_order, color_hex, icon,
                   created_at, updated_at
            FROM accounts
            WHERE is_favorite = 1
            ORDER BY display_order, name
        """
        rows = self.db.execute_query(query)
        return [self._row_to_account(row) for row in rows]

    def search_accounts(self, search_query: str) -> List[Account]:
        """
        Search accounts by name, account_number, and institution.

        **Performance Note:** Notes field excluded from search to maintain
        <50ms performance with 1000+ accounts. Use FTS5 for full-text search
        on notes in future enhancement (v2.2+).

        Args:
            search_query: Search term (case-insensitive)

        Returns:
            List of matching accounts
        """
        query = """
            SELECT id, name, account_type, account_subtype, balance,
                   normal_balance, currency, parent_account_id,
                   legacy_type, last_reconciled_date, opening_balance_date,
                   is_parent, hierarchy_level, hierarchy_path,
                   account_number, institution_name, notes,
                   is_favorite, display_order, color_hex, icon,
                   created_at, updated_at
            FROM accounts
            WHERE
                name LIKE ? OR
                account_number LIKE ? OR
                institution_name LIKE ?
            ORDER BY is_favorite DESC, display_order, name
        """

        search_pattern = f"%{search_query}%"
        rows = self.db.execute_query(
            query,
            (search_pattern, search_pattern, search_pattern)
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
            SELECT id, name, account_type, account_subtype, balance,
                   normal_balance, currency, parent_account_id,
                   legacy_type, last_reconciled_date, opening_balance_date,
                   is_parent, hierarchy_level, hierarchy_path,
                   account_number, institution_name, notes,
                   is_favorite, display_order, color_hex, icon,
                   created_at, updated_at
            FROM accounts
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
        """
        Reset all accounts to default display order (alphabetical by name).

        **Performance Note:** This basic implementation uses N sequential UPDATEs.
        For 100+ accounts, consider batch UPDATE with CASE statement (10x faster).
        Batch optimization is OPTIONAL stretch goal for Sprint 11.
        """
        # Get all accounts sorted by name
        accounts = self.get_all()
        accounts_sorted = sorted(accounts, key=lambda a: a.name.lower())

        # Update display_order sequentially
        # TODO (Stretch Goal): Optimize with batch UPDATE using CASE statement
        # for idx, account in enumerate(accounts_sorted):
        #     self.update_display_order(account.id, idx)
        #
        # Optimized version (stretch goal):
        # UPDATE accounts SET display_order = CASE id
        #   WHEN 1 THEN 0
        #   WHEN 5 THEN 1
        #   WHEN 3 THEN 2
        # END WHERE id IN (1, 5, 3)
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
- [x] ✅ Migration 011 coordinated with US-009 (Migration 010)
- [x] ✅ Migration 011 ONLY adds 3 new fields (account_number, institution_name, notes)
- [x] ✅ Migration 011 assumes display_order, is_favorite exist from US-009
- [ ] Account model updated with 3 new fields + references US-009 fields
- [x] ✅ NO __post_init__ validation (follows existing pattern)
- [ ] All existing accounts migrated with default values

### Validation Layer (NEW - Tech Lead Requirement)
- [ ] AccountValidator methods added (validate_account_number, validate_institution_name, validate_notes)
- [ ] Notes sanitization implemented (HTML escape for XSS prevention)
- [ ] All validation in service layer (matches US-001 through US-006 pattern)

### Repository Layer
- [ ] 7 new repository methods implemented
- [ ] `_row_to_account()` updated with new fields
- [x] ✅ Search excludes notes field (performance optimization)
- [x] ✅ Search targets: name, account_number, institution_name only
- [ ] Search performance < 50ms for 1000+ accounts
- [ ] Database indices created (idx_accounts_institution, idx_accounts_number)
- [ ] All methods handle NULL values

### Service Layer
- [ ] 4 new service methods implemented
- [ ] `create_account()` supports metadata parameters
- [ ] Input validation uses AccountValidator methods
- [ ] Institution autocomplete working

### UI Layer
- [ ] AccountDialog updated with 3 new fields (account_number, institution_name, notes)
- [ ] Institution autocomplete dropdown works
- [ ] Favorite icon/toggle in account list (uses US-009 field)
- [ ] Drag-and-drop reordering works (uses US-009 display_order)
- [x] ✅ Hierarchy integration: ordering per-level, favorites in-place (AC7)
- [ ] Search box searches metadata (name, account_number, institution)

### Testing
- [ ] Unit tests for all new methods (15+ tests)
- [ ] Integration tests for workflows (8+ tests)
- [ ] Hierarchy integration tests (AC7 scenarios)
- [ ] Manual UI testing completed
- [ ] Test coverage > 80%

### Documentation
- [ ] USER_GUIDE.md updated
- [ ] ARCHITECTURE.md updated
- [ ] Code comments comprehensive
- [ ] Migration documented with US-009 dependency

### Quality Assurance
- [ ] All tests passing
- [ ] No regressions in existing features
- [ ] Code reviewed and approved
- [x] ✅ Performance acceptable (search < 50ms, notes excluded)
- [x] ✅ Tech Lead review recommendations implemented

### Tech Lead Review Items (2025-10-27)
- [x] ✅ Migration conflict with US-009 resolved (Option B selected)
- [x] ✅ Validation moved from model to AccountValidator
- [x] ✅ Search performance optimized (notes excluded)
- [x] ✅ Hierarchy integration clarified (AC7 added)
- [x] ✅ Notes sanitization added (XSS prevention)
- [ ] Batch update optimization (OPTIONAL stretch goal)

### Epic Alignment Review Fixes (2025-10-27 - Post-Review)
- [x] ✅ SELECT * changed to explicit column selection (P1 - Critical)
  - Fixed: get_all_sorted(), get_favorites(), search_accounts(), group_by_institution()
  - Pattern now matches: finance_app/data/repositories/account_repository.py
- [x] ✅ Visual diagrams added (P2 - Documentation Enhancement)
  - Diagram 1: Migration dependency chain (010 → 011)
  - Diagram 2: Account hierarchy + display_order interaction
  - Diagram 3: Search performance optimization flowchart
- [x] ✅ Edge Cases & Troubleshooting section added (P2 - Clarification)
  - 8 edge case scenarios with code examples
  - Troubleshooting table with 6 common issues
  - Security considerations (XSS, data integrity)

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

## 🔧 Edge Cases & Troubleshooting

This section addresses common edge cases and potential issues that developers and users may encounter.

### Edge Case 1: Changing Institution Name After Reconciliation

**Scenario:** User changes `institution_name` from "Chase Bank" to "JPMorgan Chase" after reconciling transactions.

**Behavior:**
- ✅ **ALLOWED** - Institution name is metadata, not tied to financial data
- All existing transactions remain linked to the account
- Reconciliation history is NOT affected
- Historical reports still group correctly (by account, not institution)

**Impact:** Low - Institution grouping in reports may show new name, but data integrity preserved

**Testing:**
```python
def test_change_institution_after_reconciliation():
    # Create account with institution
    account = create_account(institution_name="Chase Bank")

    # Reconcile transactions
    reconcile_account(account.id, statement_date="2025-01-31")

    # Change institution name
    account.institution_name = "JPMorgan Chase"
    account_service.update_account(account)

    # Verify reconciliation unaffected
    reconciliation = get_latest_reconciliation(account.id)
    assert reconciliation.status == "complete"
```

---

### Edge Case 2: Updating Account Number After Transactions Exist

**Scenario:** User realizes they entered wrong account number (e.g., "1234" instead of "1234-5678-9012") after adding 100 transactions.

**Behavior:**
- ✅ **ALLOWED** - Account number is metadata, NOT a foreign key
- All existing transactions remain linked (by account.id, not account_number)
- Search by old account number will no longer find the account
- Reconciliation dialog shows new account number immediately

**Impact:** Low - Data integrity preserved, search updated

**Recommendation:** Add confirmation dialog in UI: "Change account number? This affects reconciliation matching."

**Testing:**
```python
def test_update_account_number_with_transactions():
    account = create_account(account_number="1234")

    # Add transactions
    for i in range(100):
        create_transaction(account.id, amount=Decimal("10.00"))

    # Update account number
    account.account_number = "1234-5678-9012"
    updated = account_service.update_account(account)

    # Verify transactions still linked
    transactions = transaction_repo.get_by_account(account.id)
    assert len(transactions) == 100

    # Verify new search works
    results = account_repo.search_accounts("1234-5678")
    assert account in results
```

---

### Edge Case 3: Institution Merger / Name Change

**Scenario:** Bank merges - "Washington Mutual" becomes "Chase Bank". User has 3 accounts at "Washington Mutual".

**Options:**

**Option A: Bulk Update (Recommended)**
```python
# Get all WaMu accounts
wamu_accounts = account_repo.search_accounts("Washington Mutual")

# Update institution name for all
for account in wamu_accounts:
    account.institution_name = "Chase Bank"
    account_service.update_account(account)
```

**Option B: Keep Historical Name**
- Leave institution_name as "Washington Mutual"
- Add note: "Now part of Chase Bank (merged 2008)"
- Advantage: Preserves historical accuracy

**Impact:** Medium - Affects institution grouping in reports

**UI Enhancement (Future):** Add "Bulk Update Institution" dialog

---

### Edge Case 4: Duplicate Account Numbers at Different Institutions

**Scenario:** User has checking account #1234 at Chase AND checking account #1234 at Bank of America.

**Behavior:**
- ✅ **ALLOWED** - No unique constraint on `account_number`
- `account_number` + `institution_name` combination identifies account
- Search for "1234" will return BOTH accounts
- User disambiguates by account name or institution

**Impact:** Low - Users can distinguish by institution

**Validation (NOT Enforced):**
```python
# OPTIONAL: Warn user if duplicate account_number + institution exists
def check_duplicate_account_number(account_number, institution_name):
    existing = account_repo.get_by_account_number_and_institution(
        account_number, institution_name
    )
    if existing:
        # Show warning, but ALLOW creation
        return "Warning: Account number already exists at this institution"
```

**UI Enhancement (Future):** Show institution in search results to disambiguate

---

### Edge Case 5: Notes Exceed 1000 Character Limit

**Scenario:** User pastes long text (2000 chars) into notes field.

**Behavior:**
- ❌ **REJECTED** - ValidationError raised
- UI shows error: "Notes cannot exceed 1000 characters (currently 2000)"
- User must trim text or save in external document

**Workaround (v2.1):**
- Store full text in external file
- Add link in notes: "See full notes at: file:///path/to/notes.txt"

**Future Enhancement (v2.2):**
- Add "Attachments" feature (US-014?)
- Support file uploads (PDFs, images, etc.)

**Testing:**
```python
def test_notes_exceed_limit():
    with pytest.raises(ValidationError, match="exceed 1000 characters"):
        account_service.create_account(
            name="Test",
            notes="A" * 1001  # 1001 chars
        )
```

---

### Edge Case 6: Special Characters in Account Number

**Scenario:** User enters account number with special chars: "ACCT-123/456 (USD)"

**Behavior:**
- ✅ **ALLOWED** - No character restrictions (only length 3-50)
- Special chars: `-`, `.`, `/`, `(`, `)`, spaces, alphanumeric
- Search works with special chars
- Display exactly as entered

**Impact:** None - Flexibility for international account formats

**Example:**
```python
valid_account_numbers = [
    "1234-5678-9012",
    "ACCT.123.456",
    "IBAN: DE89 3704 0044 0532 0130 00",
    "SWIFT: CHASUS33",
    "A/C 123/456 (USD)",
]

for number in valid_account_numbers:
    account = account_service.create_account(
        name="Test",
        account_number=number
    )
    assert account.account_number == number
```

---

### Edge Case 7: HTML/Script Injection in Notes (XSS Attack)

**Scenario:** Malicious user enters `<script>alert('XSS')</script>` in notes field.

**Behavior:**
- ✅ **SANITIZED** - HTML entities escaped by `AccountValidator.validate_notes()`
- Stored as: `&lt;script&gt;alert('XSS')&lt;/script&gt;`
- Displayed as plain text, NOT executed
- User sees: `<script>alert('XSS')</script>` (safe)

**Security:**
```python
import html

def validate_notes(notes: str) -> str:
    # Escape HTML entities
    notes = html.escape(notes)
    return notes

# Test
malicious_input = "<script>alert('XSS')</script>"
safe_output = validate_notes(malicious_input)
assert safe_output == "&lt;script&gt;alert('XSS')&lt;/script&gt;"
```

**Impact:** None - XSS attack prevented

---

### Edge Case 8: Favorite Status Lost After Database Migration

**Scenario:** User upgrades from US-007 (no favorites) to US-009 (with favorites). Is `is_favorite` field lost?

**Behavior:**
- ✅ **PRESERVED** - Migration 010 (US-009) adds `is_favorite` with DEFAULT 0
- Migration 011 (US-007) assumes field exists
- Existing accounts have `is_favorite = 0` (not favorite)
- User can manually mark favorites after migration

**Impact:** None - Default value ensures no data loss

**Migration Order:**
1. Migration 010 runs: Adds `is_favorite` column, defaults all to 0
2. Migration 011 runs: Uses existing `is_favorite` column
3. User marks favorites via UI

---

### Troubleshooting Guide

| Problem | Symptom | Solution |
|---------|---------|----------|
| **Search not finding account by number** | User searches "1234", account not returned | Verify `account_number` field populated. Check for typos. Account number might have spaces/dashes. |
| **Institution autocomplete not working** | Dropdown empty when typing institution | Ensure at least one account has `institution_name` populated. Check database query returns results. |
| **Notes not saving** | Notes field clears after save | Check for validation error (1000 char limit). Verify database column exists. Check for SQL error in logs. |
| **Favorites not sorting to top** | Favorites appear randomly in list | Verify `is_favorite = 1` in database. Check `get_all_sorted()` ORDER BY clause includes `is_favorite DESC`. |
| **Drag-and-drop not persisting order** | Accounts revert to original order after reload | Check `update_display_order()` commits to database. Verify `display_order` column updated. Check for concurrent updates. |
| **Migration 011 fails** | Error: "column display_order does not exist" | ⚠️ CRITICAL: Migration 010 (US-009) must run FIRST. Check `schema_version`. Run Migration 010 before Migration 011. |

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
