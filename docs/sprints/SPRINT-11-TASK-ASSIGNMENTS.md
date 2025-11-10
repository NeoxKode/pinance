# Sprint 11: US-007 Task Assignments & Developer Plan

**Sprint:** Sprint 11
**Story:** US-007 - Account Metadata & Organization
**Duration:** 3 days (13 hours total)
**Created:** November 4, 2025
**Status:** 🟢 READY FOR ASSIGNMENT

---

## 📊 Task Summary by Role

| Role | Tasks | Hours | Complexity | Dependencies |
|------|-------|-------|------------|--------------|
| **Backend Developer** | 12 tasks | 7.5h | Medium | Database foundation |
| **Frontend Developer** | 8 tasks | 4h | Medium-High | Backend API complete |
| **Tech Lead** | 6 tasks | 1.5h | Low-Medium | Review & support |

**Total:** 26 tasks, 13 hours

---

## 🎯 Critical Path Analysis

### Day 1 (5 hours)
**Focus:** Backend Foundation
1. Backend: Database + Models (2h)
2. Backend: Repository Layer (3h)
- Frontend can start UI planning/mockups in parallel

### Day 2 (5 hours)
**Focus:** Service Layer + UI Start
1. Backend: Service Layer (1.5h)
2. Frontend: AccountDialog (1.5h)
3. Both: Integration begins (2h)

### Day 3 (3 hours)
**Focus:** UI Completion + Testing
1. Frontend: Favorites + Drag-drop (1.5h)
2. Backend: Integration tests (1h)
3. Tech Lead: Code review + documentation (0.5h)

---

## 👨‍💻 Backend Developer Tasks (12 tasks, 7.5 hours)

### Phase 1: Database & Models (Day 1 AM - 2 hours)

#### Task B1.1: Create Migration 011 ⭐ CRITICAL
**Assigned:** Backend Developer
**Estimate:** 45 minutes
**Dependencies:** None (can start immediately)
**Priority:** P0 (MUST complete Day 1)
**Files:** `finance_app/data/migrations/011_account_metadata.sql`

**Implementation:**
```sql
-- Migration 011: Account metadata (account numbers, institutions, notes)
-- Dependencies: Migration 010 (US-009) MUST be applied first

-- Add metadata fields (US-007 specific)
ALTER TABLE accounts ADD COLUMN account_number TEXT;
ALTER TABLE accounts ADD COLUMN institution_name TEXT;
ALTER TABLE accounts ADD COLUMN notes TEXT;

-- Create indices for search and filtering
CREATE INDEX IF NOT EXISTS idx_accounts_institution ON accounts(institution_name);
CREATE INDEX IF NOT EXISTS idx_accounts_number ON accounts(account_number);

-- Note: is_favorite, display_order, color_hex, icon already exist from Migration 010
```

**Acceptance Criteria:**
- [ ] Migration file created with correct SQL
- [ ] Indices added for institution_name and account_number
- [ ] Test migration on dev database (verify columns exist)
- [ ] Rollback tested and documented
- [ ] No conflicts with Migration 010

**Testing:**
```python
def test_migration_011_creates_columns():
    db = Database(":memory:")
    cursor = db.conn.cursor()
    result = cursor.execute("PRAGMA table_info(accounts)")
    columns = [row[1] for row in result.fetchall()]

    assert "account_number" in columns
    assert "institution_name" in columns
    assert "notes" in columns
```

---

#### Task B1.2: Update Account Model
**Assigned:** Backend Developer
**Estimate:** 45 minutes
**Dependencies:** Task B1.1 (migration spec)
**Priority:** P0 (MUST complete Day 1)
**Files:** `finance_app/data/models.py`

**Implementation:**
```python
@dataclass
class Account:
    # ... existing fields ...

    # US-007: Metadata fields
    account_number: Optional[str] = None
    institution_name: Optional[str] = None
    notes: Optional[str] = None
    is_favorite: bool = False  # From US-009, now used by US-007
    display_order: int = 0     # From US-009, now used by US-007

    @property
    def truncated_notes(self) -> str:
        """Return first 100 characters of notes with ellipsis if truncated."""
        if not self.notes:
            return ""
        return self.notes[:100] + "..." if len(self.notes) > 100 else self.notes
```

**Acceptance Criteria:**
- [ ] Account dataclass has 5 fields (3 new + 2 from US-009)
- [ ] Type hints complete (Optional[str], bool, int)
- [ ] Default values set correctly
- [ ] `truncated_notes` property implemented
- [ ] Docstrings updated

**Testing:**
```python
def test_account_metadata_fields():
    account = Account(
        id=1, name="Test", account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
        normal_balance=NormalBalance.DEBIT,
        account_number="1234-5678",
        institution_name="Chase Bank",
        notes="Emergency fund - DO NOT TOUCH!",
        is_favorite=True,
        display_order=5
    )

    assert account.account_number == "1234-5678"
    assert account.institution_name == "Chase Bank"
    assert account.is_favorite is True
    assert account.display_order == 5
    assert account.truncated_notes == account.notes
```

---

#### Task B1.3: Update Database Integration
**Assigned:** Backend Developer
**Estimate:** 30 minutes
**Dependencies:** Task B1.1 (migration file)
**Priority:** P0 (MUST complete Day 1)
**Files:** `finance_app/data/database.py`

**Implementation:**
```python
MIGRATIONS = [
    # ... existing migrations ...
    "010_account_visual_metadata.sql",  # US-009
    "011_account_metadata.sql",          # US-007 (THIS STORY)
]

CURRENT_SCHEMA_VERSION = 11  # Update from 10
```

**Acceptance Criteria:**
- [ ] Migration 011 added to MIGRATIONS list
- [ ] CURRENT_SCHEMA_VERSION = 11
- [ ] Migration runs on app startup
- [ ] Logs confirm successful migration
- [ ] Error handling for migration failure

---

### Phase 2: Repository Layer (Day 1 PM - 3 hours)

#### Task B2.1: Implement Core Repository Methods ⭐ HIGH PRIORITY
**Assigned:** Backend Developer
**Estimate:** 2 hours
**Dependencies:** Task B1.2 (Account model updated)
**Priority:** P0 (blocks frontend)
**Files:** `finance_app/data/repositories/account_repository.py`

**Methods to Implement (7 total):**

**1. `get_all_sorted()` - Core sorting logic**
```python
def get_all_sorted(self, include_archived: bool = False) -> List[Account]:
    """
    Get all accounts sorted by favorites, display_order, then name.

    Sort order:
    1. is_favorite DESC (favorites first)
    2. display_order ASC (custom order)
    3. name ASC (alphabetical)
    """
    query = """
        SELECT * FROM accounts
        WHERE (is_archived = 0 OR ?)
        ORDER BY is_favorite DESC, display_order ASC, name ASC
    """
    cursor = self.db.conn.cursor()
    cursor.execute(query, (include_archived,))
    return [self._row_to_account(row) for row in cursor.fetchall()]
```

**2. `get_favorites()` - Filter favorites only**
```python
def get_favorites(self) -> List[Account]:
    """Get only favorite accounts."""
    query = """
        SELECT * FROM accounts
        WHERE is_favorite = 1
        ORDER BY display_order ASC, name ASC
    """
    cursor = self.db.conn.cursor()
    cursor.execute(query)
    return [self._row_to_account(row) for row in cursor.fetchall()]
```

**3. `search_accounts()` - Multi-field search (AC6)**
```python
def search_accounts(self, query: str) -> List[Account]:
    """
    Search accounts by name, account_number, or institution_name.

    Note: Excludes notes field for performance (per AC6).
    Future: Add FTS5 full-text search for notes.
    """
    search_pattern = f"%{query}%"
    sql = """
        SELECT * FROM accounts
        WHERE name LIKE ?
           OR account_number LIKE ?
           OR institution_name LIKE ?
        ORDER BY is_favorite DESC, name ASC
    """
    cursor = self.db.conn.cursor()
    cursor.execute(sql, (search_pattern, search_pattern, search_pattern))
    return [self._row_to_account(row) for row in cursor.fetchall()]
```

**4. `get_institution_names()` - For autocomplete (AC2)**
```python
def get_institution_names(self) -> List[str]:
    """Get distinct institution names for autocomplete dropdown."""
    query = """
        SELECT DISTINCT institution_name
        FROM accounts
        WHERE institution_name IS NOT NULL AND institution_name != ''
        ORDER BY institution_name ASC
    """
    cursor = self.db.conn.cursor()
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]
```

**5. `group_by_institution()` - For reports**
```python
def group_by_institution(self) -> Dict[str, List[Account]]:
    """Group accounts by institution name."""
    accounts = self.get_all()
    groups = {}
    for account in accounts:
        institution = account.institution_name or "No Institution"
        if institution not in groups:
            groups[institution] = []
        groups[institution].append(account)
    return groups
```

**6. `update_display_order()` - Already exists from US-009! ✅**
```python
# REUSE from US-009 - No new code needed!
def update_display_order(self, account_id: int, display_order: int) -> Account:
    """Update account display order (implemented in US-009)."""
    # Already implemented - just verify it works
    pass
```

**7. `reset_display_order()` - Reset to default**
```python
def reset_display_order(self) -> None:
    """Reset all display orders to default (alphabetical by id)."""
    query = "UPDATE accounts SET display_order = id"
    cursor = self.db.conn.cursor()
    cursor.execute(query)
    self.db.conn.commit()
```

**Acceptance Criteria:**
- [ ] All 7 methods implemented (6 new + 1 reuse from US-009)
- [ ] SQL queries use indices (performance)
- [ ] NULL values handled gracefully
- [ ] Type hints complete
- [ ] Docstrings with examples

**Testing:**
```python
def test_get_all_sorted_favorites_first():
    repo = AccountRepository(db)

    # Create accounts
    regular = repo.create(Account(name="Regular", is_favorite=False, display_order=1))
    favorite = repo.create(Account(name="Favorite", is_favorite=True, display_order=2))

    # Get sorted
    accounts = repo.get_all_sorted()

    # Favorites first, regardless of display_order
    assert accounts[0].id == favorite.id
    assert accounts[1].id == regular.id


def test_search_accounts_by_number():
    repo = AccountRepository(db)

    # Create account with number
    account = repo.create(Account(
        name="Chase Checking",
        account_number="1234-5678"
    ))

    # Search by number
    results = repo.search_accounts("1234")
    assert len(results) == 1
    assert results[0].id == account.id


def test_get_institution_names_for_autocomplete():
    repo = AccountRepository(db)

    # Create accounts at different institutions
    repo.create(Account(name="Checking", institution_name="Chase Bank"))
    repo.create(Account(name="Savings", institution_name="Chase Bank"))
    repo.create(Account(name="Credit Card", institution_name="Wells Fargo"))

    # Get institution names
    institutions = repo.get_institution_names()

    # Should return distinct, sorted names
    assert len(institutions) == 2
    assert "Chase Bank" in institutions
    assert "Wells Fargo" in institutions
```

---

#### Task B2.2: Update `_row_to_account()` Helper
**Assigned:** Backend Developer
**Estimate:** 30 minutes
**Dependencies:** Task B1.2 (Account model)
**Priority:** P0 (required for all repository methods)
**Files:** `finance_app/data/repositories/account_repository.py`

**Implementation:**
```python
def _row_to_account(self, row: sqlite3.Row) -> Account:
    """Convert database row to Account object."""
    return Account(
        id=row["id"],
        name=row["name"],
        account_type=AccountType(row["account_type"]),
        account_subtype=AccountSubtype(row["account_subtype"]),
        # ... existing fields ...

        # US-007: Metadata fields (handle NULL)
        account_number=row["account_number"] if row["account_number"] else None,
        institution_name=row["institution_name"] if row["institution_name"] else None,
        notes=row["notes"] if row["notes"] else None,
        is_favorite=bool(row["is_favorite"]) if row["is_favorite"] else False,
        display_order=int(row["display_order"]) if row["display_order"] else 0,
    )
```

**Acceptance Criteria:**
- [ ] All 5 metadata fields mapped
- [ ] NULL values return None or default
- [ ] Type conversions correct (str, bool, int)
- [ ] No data loss

---

#### Task B2.3: Update `_account_to_row()` Helper
**Assigned:** Backend Developer
**Estimate:** 30 minutes
**Dependencies:** Task B2.2
**Priority:** P0 (required for INSERT/UPDATE)
**Files:** `finance_app/data/repositories/account_repository.py`

**Implementation:**
```python
def _account_to_row(self, account: Account) -> Dict[str, Any]:
    """Convert Account object to database row dict."""
    return {
        "id": account.id,
        "name": account.name,
        # ... existing fields ...

        # US-007: Metadata fields
        "account_number": account.account_number,
        "institution_name": account.institution_name,
        "notes": account.notes,
        "is_favorite": 1 if account.is_favorite else 0,
        "display_order": account.display_order,
    }
```

**Acceptance Criteria:**
- [ ] All metadata fields included in dict
- [ ] Boolean converted to int (is_favorite)
- [ ] INSERT/UPDATE operations include new fields
- [ ] Test with NULL values

---

### Phase 3: Service Layer (Day 2 AM - 1.5 hours)

#### Task B3.1: Add Business Logic Methods
**Assigned:** Backend Developer
**Estimate:** 1 hour
**Dependencies:** Task B2.1 (repository methods)
**Priority:** P0 (blocks frontend integration)
**Files:** `finance_app/business/account_service.py`

**Methods to Implement:**

**1. `update_metadata()` - Update account metadata (NEW)**
```python
def update_metadata(
    self,
    account_id: int,
    account_number: Optional[str] = None,
    institution_name: Optional[str] = None,
    notes: Optional[str] = None
) -> Account:
    """
    Update account metadata fields.

    Args:
        account_id: Account to update
        account_number: Bank account number (3-50 chars if provided)
        institution_name: Financial institution name
        notes: Free-form notes (max 1000 chars)

    Returns:
        Updated Account object

    Raises:
        ValidationError: If validation fails
        NotFoundError: If account doesn't exist
    """
    # Validate
    account = self.account_repo.get_by_id(account_id)
    if not account:
        raise NotFoundError(f"Account {account_id} not found")

    # Validate account_number (AC1)
    if account_number:
        account_number = account_number.strip()
        if len(account_number) < 3 or len(account_number) > 50:
            raise ValidationError("Account number must be 3-50 characters")
        # Alphanumeric + separators only
        import re
        if not re.match(r'^[A-Za-z0-9\s\.\-]+$', account_number):
            raise ValidationError("Invalid account number format")

    # Validate notes (AC3)
    if notes and len(notes) > 1000:
        raise ValidationError("Notes cannot exceed 1000 characters")

    # Sanitize notes (XSS prevention)
    if notes:
        import html
        notes = html.escape(notes)

    # Update fields
    account.account_number = account_number
    account.institution_name = institution_name
    account.notes = notes

    # Save
    return self.account_repo.update(account)
```

**2. `get_institution_autocomplete()` - Autocomplete logic (NEW)**
```python
def get_institution_autocomplete(self, partial: str) -> List[str]:
    """
    Get institution name suggestions for autocomplete.

    Args:
        partial: Partial institution name entered by user

    Returns:
        List of matching institution names (sorted)

    Example:
        >>> service.get_institution_autocomplete("Cha")
        ["Chase Bank", "Charles Schwab"]
    """
    all_institutions = self.account_repo.get_institution_names()

    # Filter by partial match (case-insensitive)
    partial_lower = partial.lower()
    matches = [
        inst for inst in all_institutions
        if partial_lower in inst.lower()
    ]

    return sorted(matches)
```

**3. `toggle_favorite()` - Already exists from US-009! ✅**
```python
# REUSE from US-009 - No new code needed!
def toggle_favorite(self, account_id: int) -> Account:
    """Toggle favorite status (implemented in US-009)."""
    return self.account_repo.toggle_favorite(account_id)
```

**4. `reorder_accounts()` - Already exists from US-009! ✅**
```python
# REUSE from US-009 - No new code needed!
def reorder_accounts(self, order_pairs: List[Tuple[int, int]]) -> List[Account]:
    """Reorder accounts (implemented in US-009)."""
    # Validate non-negative display_order
    for account_id, display_order in order_pairs:
        if display_order < 0:
            raise ValidationError("Display order must be non-negative")
        self.account_repo.update_display_order(account_id, display_order)

    return [self.account_repo.get_by_id(aid) for aid, _ in order_pairs]
```

**Acceptance Criteria:**
- [ ] `update_metadata()` implemented with validation
- [ ] `get_institution_autocomplete()` implemented
- [ ] `toggle_favorite()` verified working (from US-009)
- [ ] `reorder_accounts()` verified working (from US-009)
- [ ] Input validation for account_number (3-50 chars, alphanumeric + separators)
- [ ] Notes sanitization (HTML escape for XSS prevention)
- [ ] Error handling with meaningful messages

**Testing:**
```python
def test_update_metadata_validates_account_number():
    service = AccountService(db)
    account = service.create_account("Test", AccountType.ASSET, AccountSubtype.CHECKING)

    # Valid account number
    updated = service.update_metadata(account.id, account_number="1234-5678")
    assert updated.account_number == "1234-5678"

    # Invalid: too short
    with pytest.raises(ValidationError, match="must be 3-50 characters"):
        service.update_metadata(account.id, account_number="12")

    # Invalid: bad format
    with pytest.raises(ValidationError, match="Invalid account number format"):
        service.update_metadata(account.id, account_number="1234@#$%")


def test_get_institution_autocomplete():
    service = AccountService(db)

    # Create accounts
    service.create_account("Checking", AccountType.ASSET, AccountSubtype.CHECKING,
                          institution_name="Chase Bank")
    service.create_account("Savings", AccountType.ASSET, AccountSubtype.SAVINGS,
                          institution_name="Charles Schwab")
    service.create_account("Credit", AccountType.LIABILITY, AccountSubtype.CREDIT_CARD,
                          institution_name="Wells Fargo")

    # Search "Cha" should return Chase and Charles
    results = service.get_institution_autocomplete("Cha")
    assert len(results) == 2
    assert "Chase Bank" in results
    assert "Charles Schwab" in results
    assert "Wells Fargo" not in results


def test_notes_sanitization_prevents_xss():
    service = AccountService(db)
    account = service.create_account("Test", AccountType.ASSET, AccountSubtype.CHECKING)

    # Attempt XSS injection
    malicious_notes = "<script>alert('XSS')</script>"

    updated = service.update_metadata(account.id, notes=malicious_notes)

    # Should be HTML escaped
    assert "<script>" not in updated.notes
    assert "&lt;script&gt;" in updated.notes
```

---

#### Task B3.2: Update `create_account()` Method
**Assigned:** Backend Developer
**Estimate:** 30 minutes
**Dependencies:** Task B3.1
**Priority:** P1 (nice to have for Day 2)
**Files:** `finance_app/business/account_service.py`

**Implementation:**
```python
def create_account(
    self,
    name: str,
    account_type: AccountType,
    account_subtype: AccountSubtype,
    # ... existing parameters ...

    # US-007: New optional parameters
    account_number: Optional[str] = None,
    institution_name: Optional[str] = None,
    notes: Optional[str] = None,
    is_favorite: bool = False,
    display_order: Optional[int] = None
) -> Account:
    """
    Create a new account with optional metadata.

    US-007: Added metadata parameters for account organization.
    """
    # ... existing validation ...

    # Set default display_order if not provided
    if display_order is None:
        max_order = self.account_repo.get_max_display_order()
        display_order = max_order + 1 if max_order else 0

    # Validate metadata (reuse update_metadata validation logic)
    if account_number:
        # Same validation as update_metadata
        pass

    # Create account with metadata
    account = Account(
        name=name,
        account_type=account_type,
        # ... existing fields ...
        account_number=account_number,
        institution_name=institution_name,
        notes=notes,
        is_favorite=is_favorite,
        display_order=display_order
    )

    return self.account_repo.create(account)
```

**Acceptance Criteria:**
- [ ] `create_account()` accepts 5 new metadata parameters
- [ ] Default display_order = max + 1
- [ ] Metadata saved correctly
- [ ] Validation applied

---

### Phase 5: Integration Testing (Day 3 AM - 1 hour)

#### Task B5.1: Write Unit Tests
**Assigned:** Backend Developer
**Estimate:** 30 minutes
**Dependencies:** All backend tasks complete
**Priority:** P0 (must have tests)
**Files:** `finance_app/tests/unit/test_us007_metadata.py`

**Test Coverage:**
- `test_update_metadata_validates_account_number()` (AC1)
- `test_update_metadata_validates_notes_length()` (AC3)
- `test_notes_sanitization_prevents_xss()` (AC3)
- `test_get_institution_autocomplete()` (AC2)
- `test_get_all_sorted_favorites_first()` (AC4)
- `test_search_accounts_multi_field()` (AC6)
- `test_toggle_favorite()` (AC4 - verify US-009 method)
- `test_reorder_accounts()` (AC5 - verify US-009 method)

**Target:** 10+ unit tests, 80%+ coverage

---

#### Task B5.2: Write Integration Tests
**Assigned:** Backend Developer
**Estimate:** 30 minutes
**Dependencies:** Task B5.1
**Priority:** P0 (must have tests)
**Files:** `finance_app/tests/integration/test_us007_integration.py`

**Test Scenarios:**
- Create account with metadata → save → reload → verify all fields persist (AC1, AC2, AC3)
- Search accounts by account_number → verify results (AC6)
- Search accounts by institution_name → verify results (AC6)
- Toggle favorite → verify favorites sort to top (AC4)
- Reorder accounts → verify display_order persists (AC5)
- Group accounts by institution → verify grouping (AC2)
- Hierarchy integration: favorites within hierarchy level (AC7)

**Target:** 5+ integration tests covering critical workflows

---

## 🎨 Frontend Developer Tasks (8 tasks, 4 hours)

### Phase 4: UI Implementation (Day 2 PM - 2.5 hours)

#### Task F4.1: Update AccountDialog with Metadata Fields ⭐ CRITICAL
**Assigned:** Frontend Developer
**Estimate:** 1.5 hours
**Dependencies:** Task B3.1 (service methods ready)
**Priority:** P0 (core UI feature)
**Files:** `finance_app/ui/dialogs/account_dialog.py`

**Follow US-005 AccountDialog patterns**

**Implementation:**

**1. Add Form Fields (Layout)**
```python
class AccountDialog(QDialog):
    def setup_ui(self):
        layout = QFormLayout()

        # Existing fields
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        # ...

        # US-007: NEW FIELDS

        # Account Number (AC1)
        self.account_number_edit = QLineEdit()
        self.account_number_edit.setPlaceholderText("e.g., 1234-5678-9012")
        self.account_number_edit.setMaxLength(50)
        layout.addRow("Account Number (optional):", self.account_number_edit)

        # Institution Name with Autocomplete (AC2)
        self.institution_edit = QLineEdit()
        self.institution_completer = QCompleter()
        self.institution_edit.setCompleter(self.institution_completer)
        self.institution_edit.setPlaceholderText("e.g., Chase Bank")
        layout.addRow("Institution:", self.institution_edit)

        # Notes (AC3)
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.setPlaceholderText("Add notes about this account...")
        layout.addRow("Notes (optional):", self.notes_edit)

        # Favorite Checkbox (AC4)
        self.favorite_checkbox = QCheckBox("Mark as Favorite ⭐")
        layout.addRow("", self.favorite_checkbox)
```

**2. Populate Autocomplete**
```python
def __init__(self, account_service: AccountService, ...):
    super().__init__(parent)
    self.account_service = account_service

    # Load institution names for autocomplete
    self._populate_institution_autocomplete()

def _populate_institution_autocomplete(self):
    """Load existing institution names for autocomplete."""
    institutions = self.account_service.get_institution_autocomplete("")

    # Create completer model
    model = QStringListModel(institutions)
    self.institution_completer.setModel(model)
    self.institution_completer.setCaseSensitivity(Qt.CaseInsensitive)
    self.institution_completer.setFilterMode(Qt.MatchContains)
```

**3. Load Data (Edit Mode)**
```python
def set_account(self, account: Account):
    """Populate form with existing account data."""
    self.name_edit.setText(account.name)
    # ... existing fields ...

    # US-007: Load metadata
    if account.account_number:
        self.account_number_edit.setText(account.account_number)
    if account.institution_name:
        self.institution_edit.setText(account.institution_name)
    if account.notes:
        self.notes_edit.setPlainText(account.notes)
    self.favorite_checkbox.setChecked(account.is_favorite)
```

**4. Save Data**
```python
def get_account_data(self) -> dict:
    """Collect form data for save."""
    data = {
        "name": self.name_edit.text().strip(),
        # ... existing fields ...

        # US-007: Metadata fields
        "account_number": self.account_number_edit.text().strip() or None,
        "institution_name": self.institution_edit.text().strip() or None,
        "notes": self.notes_edit.toPlainText().strip() or None,
        "is_favorite": self.favorite_checkbox.isChecked(),
    }
    return data
```

**5. Validation**
```python
def validate(self) -> bool:
    """Validate form inputs before save."""
    # ... existing validation ...

    # US-007: Validate account number (AC1)
    account_number = self.account_number_edit.text().strip()
    if account_number:
        if len(account_number) < 3 or len(account_number) > 50:
            QMessageBox.warning(self, "Validation Error",
                              "Account number must be 3-50 characters")
            return False

    # US-007: Validate notes length (AC3)
    notes = self.notes_edit.toPlainText()
    if len(notes) > 1000:
        QMessageBox.warning(self, "Validation Error",
                          f"Notes too long ({len(notes)}/1000 characters)")
        return False

    return True
```

**Acceptance Criteria:**
- [ ] Account number field added (QLineEdit, 50 char max)
- [ ] Institution field added with autocomplete (QCompleter)
- [ ] Notes field added (QTextEdit, multi-line)
- [ ] Favorite checkbox added with star icon
- [ ] Fields populate when editing existing account
- [ ] Validation prevents invalid account number
- [ ] Notes length validated (≤ 1000 chars)
- [ ] Save includes all metadata fields
- [ ] Dialog size adjusted for new fields

**Testing:**
Manual testing:
1. Create new account → fill metadata → save → verify saved
2. Edit existing account → metadata loads → edit → save → verify updated
3. Test autocomplete → start typing "Cha" → see suggestions
4. Test notes multi-line → press Enter → line break preserved
5. Test validation → enter 2-char account number → see error
6. Test validation → enter 1001-char notes → see error

---

#### Task F4.2: Add Favorite Icon to Account Tree ⭐ HIGH PRIORITY
**Assigned:** Frontend Developer
**Estimate:** 45 minutes
**Dependencies:** Task B3.1 (toggle_favorite service method)
**Priority:** P0 (AC4 core feature)
**Files:** `finance_app/ui/widgets/account_tree_widget.py`

**Follow US-009 color icon patterns**

**Implementation:**

**1. Add Favorite Column to Tree**
```python
class AccountTreeWidget(QTreeWidget):
    def setup_ui(self):
        # Update column count (add favorite column)
        self.setColumnCount(6)  # Was 5, now 6

        # Set headers
        self.setHeaderLabels([
            "⭐",           # NEW: Favorite column
            "Account",
            "Type",
            "Parent",
            "Balance",
            "Actions"
        ])

        # Set column widths
        self.setColumnWidth(0, 30)   # Favorite icon (narrow)
        self.setColumnWidth(1, 200)  # Account name
        # ...
```

**2. Populate Favorite Icon**
```python
def _populate_tree_item(self, item: QTreeWidgetItem, account: Account):
    """Populate tree item with account data."""
    # Column 0: Favorite icon (clickable)
    if account.is_favorite:
        item.setIcon(0, QIcon.fromTheme("starred"))  # Gold star ⭐
        item.setToolTip(0, "Click to unfavorite")
    else:
        item.setIcon(0, QIcon.fromTheme("non-starred"))  # Empty star ☆
        item.setToolTip(0, "Click to mark as favorite")

    # Make favorite column clickable
    item.setFlags(item.flags() | Qt.ItemIsEditable)

    # Column 1: Account name (with color dot from US-009)
    color_icon = self._create_color_icon(account.color_hex)
    item.setIcon(1, color_icon)
    item.setText(1, account.name)

    # ... other columns ...
```

**3. Handle Favorite Toggle Click**
```python
def mousePressEvent(self, event: QMouseEvent):
    """Handle mouse clicks on tree items."""
    item = self.itemAt(event.pos())
    if not item:
        return super().mousePressEvent(event)

    # Get clicked column
    column = self.columnAt(event.x())

    # Column 0 = Favorite toggle
    if column == 0:
        account_id = item.data(0, Qt.UserRole)
        self._toggle_favorite(account_id)
        event.accept()
        return

    super().mousePressEvent(event)

def _toggle_favorite(self, account_id: int):
    """Toggle favorite status and refresh display."""
    try:
        # Call service
        updated_account = self.account_service.toggle_favorite(account_id)

        # Refresh tree (will re-sort favorites to top)
        self.load_accounts()

        # Optional: Show brief feedback
        # self.show_status_message(f"{'Added to' if updated_account.is_favorite else 'Removed from'} favorites")

    except Exception as e:
        QMessageBox.warning(self, "Error", f"Failed to toggle favorite: {e}")
```

**4. Ensure Favorites Sort to Top (AC4)**
```python
def load_accounts(self):
    """Load accounts from database (sorted by favorites)."""
    # Get accounts sorted (favorites first - from repository)
    accounts = self.account_repo.get_all_sorted()  # Uses ORDER BY is_favorite DESC

    # Clear tree
    self.clear()

    # Populate tree
    for account in accounts:
        self._add_account_to_tree(account)
```

**Acceptance Criteria:**
- [ ] Favorite column added to tree (⭐ header)
- [ ] Gold star ⭐ shows for favorites
- [ ] Empty star ☆ shows for non-favorites
- [ ] Click star to toggle favorite status
- [ ] Tree re-sorts after toggle (favorites to top)
- [ ] Tooltip shows "Click to favorite/unfavorite"
- [ ] Integration with US-009 color dots (both visible)

**Testing:**
Manual testing:
1. Click empty star ☆ → becomes gold star ⭐
2. Click gold star ⭐ → becomes empty star ☆
3. Mark account as favorite → verify sorts to top of tree
4. Unfavorite account → verify moves down in tree
5. Verify star icon and color dot both visible

---

#### Task F4.3: Implement Drag-and-Drop Reordering (AC5)
**Assigned:** Frontend Developer
**Estimate:** 45 minutes
**Dependencies:** Task B3.1 (reorder_accounts service method)
**Priority:** P1 (important, can simplify if time short)
**Files:** `finance_app/ui/widgets/account_tree_widget.py`

**Follow US-006 drag-drop patterns**

**Implementation:**

**1. Enable Drag-Drop**
```python
class AccountTreeWidget(QTreeWidget):
    def __init__(self, ...):
        super().__init__(parent)

        # Enable drag-drop (US-006 pattern)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
```

**2. Handle Drop Event**
```python
def dropEvent(self, event: QDropEvent):
    """Handle account reordering via drag-drop."""
    # Get dropped item
    source_item = self.currentItem()
    if not source_item:
        return super().dropEvent(event)

    # Get drop target
    target_item = self.itemAt(event.pos())
    if not target_item:
        return super().dropEvent(event)

    # Get account IDs
    source_account_id = source_item.data(0, Qt.UserRole)
    target_account_id = target_item.data(0, Qt.UserRole)

    # Get source and target accounts
    source_account = self.account_repo.get_by_id(source_account_id)
    target_account = self.account_repo.get_by_id(target_account_id)

    # AC7: Only allow reorder within same hierarchy level
    if source_account.parent_account_id != target_account.parent_account_id:
        QMessageBox.warning(self, "Cannot Reorder",
                          "Can only reorder accounts within the same level")
        return

    # Calculate new display_order values
    # Get all siblings sorted by current display_order
    siblings = self._get_siblings(source_account)

    # Reorder: remove source, insert at target position
    siblings.remove(source_account)
    target_index = siblings.index(target_account)
    siblings.insert(target_index, source_account)

    # Update display_order for all siblings
    order_pairs = [(acc.id, idx) for idx, acc in enumerate(siblings)]

    try:
        # Call service to update display_order
        self.account_service.reorder_accounts(order_pairs)

        # Reload tree
        self.load_accounts()

    except Exception as e:
        QMessageBox.warning(self, "Error", f"Failed to reorder: {e}")

def _get_siblings(self, account: Account) -> List[Account]:
    """Get all sibling accounts (same parent, sorted by display_order)."""
    all_accounts = self.account_repo.get_all_sorted()
    return [
        acc for acc in all_accounts
        if acc.parent_account_id == account.parent_account_id
    ]
```

**3. Visual Feedback During Drag**
```python
def dragMoveEvent(self, event: QDragMoveEvent):
    """Provide visual feedback during drag."""
    target_item = self.itemAt(event.pos())

    if target_item:
        # Highlight drop target
        self.setCurrentItem(target_item)
        event.accept()
    else:
        event.ignore()
```

**Acceptance Criteria:**
- [ ] Accounts can be dragged and dropped
- [ ] Visual feedback during drag (highlight target)
- [ ] Reordering only within same hierarchy level (AC7)
- [ ] Error message if trying to drag across levels
- [ ] Display order persists after reload
- [ ] Tree refreshes automatically after reorder

**Testing:**
Manual testing:
1. Drag account A above account B → verify order changes
2. Reload app → verify order persists
3. Try to drag child into different parent → see error message
4. Drag favorite account → verify favorites stay at top
5. Drag multiple times → verify stable ordering

**Note:** If time runs short, can simplify to "up/down" buttons instead of drag-drop.

---

### Phase 5: Search & Filter (Day 3 AM - 1 hour)

#### Task F5.1: Add Search Box Integration (AC6)
**Assigned:** Frontend Developer
**Estimate:** 1 hour
**Dependencies:** Task B2.1 (search_accounts repository method)
**Priority:** P0 (AC6 core feature)
**Files:** `finance_app/ui/main_window.py`

**Implementation:**

**1. Add Search Box to Main Window**
```python
class MainWindow(QMainWindow):
    def setup_ui(self):
        # ... existing UI ...

        # US-007: Add search box
        search_layout = QHBoxLayout()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search accounts (name, number, institution)...")
        self.search_edit.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self.search_edit)

        self.clear_search_btn = QPushButton("Clear")
        self.clear_search_btn.clicked.connect(self._clear_search)
        search_layout.addWidget(self.clear_search_btn)

        # Add to main layout
        main_layout.insertLayout(0, search_layout)  # At top
```

**2. Implement Search Logic**
```python
def _on_search_text_changed(self, text: str):
    """Handle search text changes (debounced)."""
    # Debounce: wait 300ms after last keystroke
    if hasattr(self, '_search_timer'):
        self._search_timer.stop()

    self._search_timer = QTimer()
    self._search_timer.setSingleShot(True)
    self._search_timer.timeout.connect(lambda: self._perform_search(text))
    self._search_timer.start(300)  # 300ms debounce

def _perform_search(self, query: str):
    """Execute search and update account tree."""
    if not query or len(query.strip()) < 2:
        # Empty or too short - show all accounts
        self._show_all_accounts()
        return

    # Search accounts (AC6: name, number, institution)
    try:
        results = self.account_repo.search_accounts(query)

        # Update tree with results
        self.account_tree.clear()
        for account in results:
            self.account_tree._add_account_to_tree(account)

        # Show result count
        self.statusBar().showMessage(f"Found {len(results)} account(s)", 3000)

    except Exception as e:
        QMessageBox.warning(self, "Search Error", f"Search failed: {e}")

def _clear_search(self):
    """Clear search and show all accounts."""
    self.search_edit.clear()
    self._show_all_accounts()

def _show_all_accounts(self):
    """Show all accounts (clear search filter)."""
    self.account_tree.load_accounts()
```

**3. Optional: Highlight Search Matches**
```python
def _highlight_search_matches(self, item: QTreeWidgetItem, query: str):
    """Highlight matching text in search results (optional)."""
    account_name = item.text(1)

    # Simple highlighting: bold matching text
    if query.lower() in account_name.lower():
        font = item.font(1)
        font.setBold(True)
        item.setFont(1, font)
```

**Acceptance Criteria:**
- [ ] Search box added to main window (top)
- [ ] Search updates as user types (debounced 300ms)
- [ ] Searches name, account_number, institution_name (AC6)
- [ ] Results display in account tree
- [ ] Result count shown in status bar
- [ ] Clear button resets to full list
- [ ] Search is case-insensitive
- [ ] Performance: < 50ms for 100 accounts (AC6 requirement)

**Testing:**
Manual testing:
1. Type "chase" → see only Chase accounts
2. Type "1234" → see accounts with "1234" in account_number
3. Type "ba" → see accounts with "bank" in institution_name
4. Clear search → see all accounts again
5. Performance: Create 100 test accounts → search → verify fast

---

## 🔧 Tech Lead Tasks (6 tasks, 1.5 hours)

### Phase 0: Pre-Sprint Prep (Before Day 1 - 30 minutes)

#### Task TL0.1: Review AC7 with Developers
**Assigned:** Tech Lead
**Estimate:** 30 minutes
**Dependencies:** None
**Priority:** P0 (MUST complete before sprint starts)
**Files:** None (meeting/discussion)

**Agenda:**
1. **Review AC7 Spec:** Hierarchy + display_order interaction
   - Explain "per-level" ordering concept
   - Clarify drag-drop constraints (siblings only)
   - Discuss edge cases (favoriting parent, etc.)

2. **Review US-006 Patterns:** Show drag-drop implementation
   - `AccountTreeWidget.dropEvent()` from US-006
   - Parent-child constraint checking
   - Visual feedback patterns

3. **Clarify Questions:**
   - What happens when you favorite a parent account?
   - Can you drag a parent below its children? (No)
   - How do favorites interact with hierarchy? (Within each level)

**Deliverable:** Clear understanding of AC7 constraints

---

### Phase 6: Code Review & Documentation (Day 3 PM - 1 hour)

#### Task TL6.1: Code Review Backend (Critical)
**Assigned:** Tech Lead
**Estimate:** 30 minutes
**Dependencies:** All backend tasks complete
**Priority:** P0 (quality gate)
**Files:** All backend files

**Review Checklist:**
- [ ] **Migration 011:** Correct SQL, indices added, no conflicts with Migration 010
- [ ] **Repository Methods:** All 7 methods implemented, SQL optimized, NULL handling
- [ ] **Service Methods:** Validation correct, error handling, XSS prevention in notes
- [ ] **Tests:** 80%+ coverage, integration tests cover AC7
- [ ] **Performance:** search_accounts() < 50ms (AC6 requirement)

**Focus Areas:**
1. **Security:** Notes field HTML escaping (XSS prevention)
2. **Performance:** Search query with 3 fields (check EXPLAIN QUERY PLAN)
3. **AC7:** Hierarchy integration tests (favorites within levels)

---

#### Task TL6.2: Code Review Frontend (Critical)
**Assigned:** Tech Lead
**Estimate:** 30 minutes
**Dependencies:** All frontend tasks complete
**Priority:** P0 (quality gate)
**Files:** All UI files

**Review Checklist:**
- [ ] **AccountDialog:** All 5 fields added, validation works, autocomplete functional
- [ ] **Favorite Toggle:** Click star to toggle, tree re-sorts, integration with US-009 color dots
- [ ] **Drag-Drop:** Reordering works, hierarchy constraints enforced (AC7), visual feedback
- [ ] **Search:** Multi-field search, debounced, performance < 50ms

**Focus Areas:**
1. **UX:** Drag-drop feels smooth, visual feedback clear
2. **AC7:** Cannot drag across hierarchy levels (error message shown)
3. **Integration:** Favorites + color dots both visible (US-009 integration)

---

#### Task TL6.3: Manual Testing (AC7 Edge Cases)
**Assigned:** Tech Lead
**Estimate:** 20 minutes
**Dependencies:** Task TL6.1, TL6.2 (code reviews pass)
**Priority:** P0 (catch edge cases)
**Files:** N/A (manual testing)

**Test Scenarios:**
1. **Favorite Parent Account:** Mark parent as favorite → verify stays in hierarchy (not extracted to top)
2. **Favorite Child Account:** Mark child as favorite → verify sorts before non-favorite siblings
3. **Drag Child to Different Parent:** Try to drag → verify error message
4. **Drag Parent Below Child:** Try to drag → verify prevented
5. **Reorder Favorites:** Drag favorite account A above favorite account B → verify works
6. **Search with Hierarchy:** Search for account → verify hierarchy preserved in results

**Acceptance:** All edge cases handled gracefully, no crashes

---

#### Task TL6.4: Performance Validation
**Assigned:** Tech Lead
**Estimate:** 10 minutes
**Dependencies:** Task TL6.3
**Priority:** P0 (AC6 requirement)
**Files:** N/A (performance testing)

**Performance Tests:**
1. **Create 100 Test Accounts:**
   ```python
   for i in range(100):
       account_service.create_account(
           name=f"Account {i}",
           account_type=AccountType.ASSET,
           account_subtype=AccountSubtype.CHECKING,
           account_number=f"{i:04d}",
           institution_name=random.choice(["Chase", "Wells Fargo", "BofA"])
       )
   ```

2. **Test Search Performance:**
   ```python
   import time

   start = time.time()
   results = account_repo.search_accounts("Chase")
   elapsed = (time.time() - start) * 1000  # Convert to ms

   assert elapsed < 50, f"Search took {elapsed:.2f}ms (should be < 50ms)"
   ```

3. **Test Sort Performance:**
   ```python
   start = time.time()
   accounts = account_repo.get_all_sorted()
   elapsed = (time.time() - start) * 1000

   assert elapsed < 100, f"Sort took {elapsed:.2f}ms (should be < 100ms)"
   ```

**Acceptance:** All performance requirements met (< 50ms search per AC6)

---

#### Task TL6.5: Update Documentation
**Assigned:** Tech Lead
**Estimate:** 10 minutes
**Dependencies:** Task TL6.4 (all tests pass)
**Priority:** P1 (nice to have)
**Files:** `docs/ARCHITECTURE.md`, Sprint completion summary

**Updates:**
1. **Architecture Doc:** Add US-007 metadata fields to Account model diagram
2. **Repository Methods:** List new methods in repository section
3. **Service Methods:** List new methods in service section

**Can be done async if needed**

---

## 📅 Sprint Schedule (3 Days, 13 Hours)

### Day 1: Backend Foundation (5 hours)

| Time | Task | Assigned | Duration | Status |
|------|------|----------|----------|--------|
| **AM** | | | | |
| 9:00 | Sprint Planning Meeting | All | 1h | 📋 |
| 10:00 | Task B1.1: Migration 011 | Backend | 45m | ⏳ |
| 10:45 | Task B1.2: Account Model | Backend | 45m | ⏳ |
| 11:30 | Task B1.3: Database Integration | Backend | 30m | ⏳ |
| **PM** | | | | |
| 13:00 | Task B2.1: Repository Methods | Backend | 2h | ⏳ |
| 15:00 | Task B2.2: _row_to_account() | Backend | 30m | ⏳ |
| 15:30 | Task B2.3: _account_to_row() | Backend | 30m | ⏳ |
| 16:00 | Daily Standup | All | 15m | 📋 |
| 16:15 | Buffer / Overflow | - | 45m | - |

**Deliverables:** Database + Repository layer complete ✅

---

### Day 2: Service + UI (5 hours)

| Time | Task | Assigned | Duration | Status |
|------|------|----------|----------|--------|
| **AM** | | | | |
| 9:00 | Daily Standup | All | 15m | 📋 |
| 9:15 | Task B3.1: Service Methods | Backend | 1h | ⏳ |
| 10:15 | Task B3.2: update create_account() | Backend | 30m | ⏳ |
| 10:45 | Task F4.1: AccountDialog | Frontend | 1.5h | ⏳ |
| **PM** | | | | |
| 13:00 | Task F4.1: AccountDialog (cont.) | Frontend | 30m | ⏳ |
| 13:30 | Task F4.2: Favorite Icon | Frontend | 45m | ⏳ |
| 14:15 | Integration Testing (backend + UI) | Both | 1h | ⏳ |
| 15:15 | Daily Standup | All | 15m | 📋 |
| 15:30 | Task F4.3: Drag-Drop | Frontend | 45m | ⏳ |
| 16:15 | Buffer / Overflow | - | 45m | - |

**Deliverables:** Service layer + AccountDialog + Favorites complete ✅

---

### Day 3: Testing + Polish (3 hours)

| Time | Task | Assigned | Duration | Status |
|------|------|----------|----------|--------|
| **AM** | | | | |
| 9:00 | Daily Standup | All | 15m | 📋 |
| 9:15 | Task F5.1: Search Integration | Frontend | 1h | ⏳ |
| 10:15 | Task B5.1: Unit Tests | Backend | 30m | ⏳ |
| 10:45 | Task B5.2: Integration Tests | Backend | 30m | ⏳ |
| 11:15 | Task TL6.1: Backend Code Review | Tech Lead | 30m | ⏳ |
| 11:45 | Task TL6.2: Frontend Code Review | Tech Lead | 30m | ⏳ |
| **PM** | | | | |
| 13:00 | Task TL6.3: Manual Testing (AC7) | Tech Lead | 20m | ⏳ |
| 13:20 | Task TL6.4: Performance Validation | Tech Lead | 10m | ⏳ |
| 13:30 | Bug Fixes / Polish | All | 1h | ⏳ |
| 14:30 | Demo Preparation | All | 30m | 📋 |
| 15:00 | Sprint Demo to Stakeholders | All | 1h | 📋 |
| 16:00 | Sprint Retrospective | All | 30m | 📋 |

**Deliverables:** All ACs complete, tested, demoed ✅

---

## 🔄 Dependencies & Blockers

### Critical Dependencies

**Backend → Frontend:**
- Frontend CANNOT start AccountDialog (Task F4.1) until Backend completes service methods (Task B3.1)
- Frontend CANNOT start Favorite toggle (Task F4.2) until Backend completes toggle_favorite verification
- Frontend CANNOT start Search (Task F5.1) until Backend completes search_accounts method (Task B2.1)

**Solution:** Backend works Day 1 + Day 2 AM, Frontend starts Day 2 (parallel on UI mockups Day 1)

**Tech Lead → All:**
- Code reviews (Tasks TL6.1, TL6.2) MUST complete before considering sprint done
- AC7 review (Task TL0.1) MUST complete before Day 1 starts

---

## ⚠️ Risk Mitigation

### High-Risk Tasks

| Task | Risk | Mitigation |
|------|------|------------|
| **F4.3: Drag-Drop** | Complex, AC7 constraints | Can simplify to up/down buttons if time short |
| **B2.1: Search** | Performance < 50ms | Indices added, can optimize query if needed |
| **F4.1: AccountDialog** | Many fields, autocomplete | Follow US-005 patterns, QCompleter is proven |
| **TL6.3: AC7 Testing** | Edge cases, hierarchy | Extra time on Day 3 PM, can extend if needed |

### De-Scope Options (if time runs short)

1. **E2E Tests (stretch goal):** Manual testing sufficient for Sprint 11
2. **User Documentation (stretch goal):** Can be follow-up task
3. **Drag-Drop Edge Cases:** Simplify to basic reordering, polish in Sprint 12
4. **Search Highlighting:** Optional visual enhancement, not in AC6

---

## ✅ Definition of Done (Checklist)

### Backend (12 tasks)
- [ ] Migration 011 created and tested
- [ ] Account model updated with 5 fields
- [ ] Database integration updated (version 11)
- [ ] 7 repository methods implemented
- [ ] _row_to_account() updated
- [ ] _account_to_row() updated
- [ ] 4 service methods implemented (2 new + 2 verified from US-009)
- [ ] create_account() updated with metadata params
- [ ] 10+ unit tests passing
- [ ] 5+ integration tests passing
- [ ] Code review passed (tech lead)
- [ ] Performance validated (< 50ms search)

### Frontend (8 tasks)
- [ ] AccountDialog updated with 5 fields
- [ ] Institution autocomplete working
- [ ] Favorite icon toggle working
- [ ] Drag-and-drop reordering working
- [ ] Search box integrated
- [ ] Manual testing complete (all ACs)
- [ ] Code review passed (tech lead)
- [ ] AC7 edge cases tested (hierarchy constraints)

### Quality (All)
- [ ] All 7 ACs demonstrated working
- [ ] Zero critical bugs
- [ ] Performance requirements met (AC6: < 50ms)
- [ ] Integration with US-004, US-006, US-009 validated
- [ ] Sprint demo completed
- [ ] US-007 status updated to COMPLETE
- [ ] Sprint completion summary created

---

## 📞 Daily Standup Questions

**Each Developer Answers:**
1. **Yesterday:** What did I complete?
2. **Today:** What am I working on?
3. **Blockers:** Any issues preventing progress?
4. **On Track?:** Am I on track for my time estimate?

**Product Owner Checks:**
- Are we on track for 13 hours total?
- Any scope changes needed?
- Any blockers to remove?

**Tech Lead Checks:**
- Any technical risks emerging?
- Any integration issues between backend/frontend?
- Any AC7 questions coming up?

---

## 🎯 Success Metrics

**Development:**
- [ ] 26 tasks completed (or de-scoped with approval)
- [ ] 13 hours actual ≈ 13 hours estimated (100% accuracy)
- [ ] All 7 ACs complete
- [ ] 23+ tests passing

**Quality:**
- [ ] Zero critical issues
- [ ] Performance < 50ms (AC6)
- [ ] Code quality 5/5 (maintain Sprint 10 standard)
- [ ] Tech lead approved

**Business:**
- [ ] Demo successful (stakeholders satisfied)
- [ ] EPIC-001 at 92% (10/12 → 11/12 stories)
- [ ] Ready for beta testing
- [ ] User feedback collection plan ready

---

## 📚 Reference Documentation

**Backend Developers:**
- Migration 010 spec (shows which fields already exist)
- US-009 service methods (toggle_favorite, reorder_accounts)
- Repository pattern from US-001 through US-006

**Frontend Developers:**
- US-005 AccountDialog patterns (form layout, validation)
- US-006 drag-drop patterns (dropEvent, hierarchy constraints)
- US-009 color icon patterns (QIcon, QPainter)
- Qt QCompleter documentation (for autocomplete)

**Tech Lead:**
- US-007 full story (all 7 ACs)
- AC7 spec (hierarchy integration)
- Sprint 10 tech review (quality standards)

---

**Sprint 11 Task Assignments Complete!** ✅
**Ready for sprint planning meeting and developer assignments.** 🚀

---

*Task Assignment Document v1.0*
*Created: November 4, 2025*
*Sprint: Sprint 11*
*Story: US-007 - Account Metadata & Organization*
