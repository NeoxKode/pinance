# Sprint 11 Kickoff: Account Metadata & Organization

**Sprint:** Sprint 11
**Epic:** [EPIC-001: Account Management & Double-Entry Foundation](../epics/EPIC-001-account-management.md)
**Story:** [US-007 - Account Metadata & Organization](../stories/backlog/US-007-account-metadata.md)
**Duration:** 3 days (estimated)
**Status:** 🟢 **READY TO START**
**Created:** 2025-11-04

---

## 📊 Sprint Overview

### Sprint Goal
Implement comprehensive account metadata and organization features to enhance power user experience with account numbers, institution tracking, notes, favorites, and custom sorting.

### Sprint Deliverables
1. Migration 011 (minimal - 3 new fields only)
2. Repository methods for metadata queries (7 methods)
3. Service layer metadata management (4 methods)
4. AccountDialog enhancements (3 new form fields)
5. Favorite icon toggle UI
6. Drag-and-drop account reordering
7. Search across metadata fields
8. Institution name autocomplete
9. Unit tests + integration tests
10. User documentation

---

## 🎯 Story Summary: US-007

### User Story
**As a** power user managing multiple financial accounts
**I want** to add metadata (account numbers, institution names, notes) and organize accounts with custom ordering and favorites
**So that** I can keep detailed records, stay organized, quickly access important accounts, and customize my account management workflow

### Story Points
- **Estimated:** 5 points (13 hours)
- **Based On:** US-009 accuracy (13h estimate = 13h actual)
- **Confidence:** High (similar scope to US-009)

### Priority
**P2** (Nice to Have - UX Enhancement)
*But highly valuable for power users*

---

## ✅ Dependencies Status

### Prerequisites (All Met) ✅
- ✅ **US-001:** Account Type Taxonomy (provides account model)
- ✅ **US-004:** Account Reconciliation (will use account_number field)
- ✅ **US-005:** Opening Balance Equity (UI dialog patterns to follow)
- ✅ **US-006:** Account Hierarchy (tree widget + drag-drop patterns)
- ✅ **US-009:** Color Coding ⭐ **JUST COMPLETED** (Migration 010 fields exist)
- ✅ **US-010:** Balance Validation (ensures data integrity)

### Critical Dependency: Migration 010 ✅
**Status:** ✅ COMPLETE (Sprint 10)

**What Migration 010 Provides:**
- ✅ `is_favorite` BOOLEAN (used by AC4)
- ✅ `display_order` INTEGER (used by AC5)
- ✅ `color_hex` TEXT (shared with US-009)
- ✅ `icon` TEXT (future use)
- ✅ `notes` TEXT (will be used by AC3)
- ✅ `account_number` TEXT (will be used by AC1)
- ✅ `institution_name` TEXT (will be used by AC2)
- ✅ 3 indices: `idx_accounts_favorite`, `idx_accounts_display_order`, `idx_accounts_color`

**⚠️ IMPORTANT:** Migration 010 was forward-looking and **already created all US-007 fields!**
This means **Migration 011 is OPTIONAL** and only needed for additional indices.

---

## 🎨 Acceptance Criteria

### AC1: Account Number Field ✅
- Accept alphanumeric with separators (`-`, `.`, spaces)
- Validate length (3-50 characters if provided)
- Optional field
- Display in account details
- Searchable
- Show in reconciliation dialog (US-004 integration)

**Field Status:** ✅ Column exists in Migration 010
**Work Needed:** UI form field, validation, search integration

---

### AC2: Institution Name with Autocomplete ✅
- Autocomplete dropdown with previous institutions
- Free-text entry for new institutions
- Standardize common variations
- Optional field
- Enable grouping by institution
- Searchable

**Field Status:** ✅ Column exists in Migration 010
**Work Needed:** Autocomplete widget, grouping methods, search integration

---

### AC3: Notes Field ✅
- Multi-line text (up to 1000 characters)
- Preserve line breaks
- Display full notes in details dialog
- Show first 100 chars in list view
- Searchable
- Optional field

**Field Status:** ✅ Column exists in Migration 010
**Work Needed:** Multi-line text widget, truncation logic, search integration

---

### AC4: Favorite Accounts ✅
- Star ⭐ icon next to account name
- Favorites at top of list
- "Show only favorites" filter toggle
- Click to toggle favorite status
- Persist across sessions
- Support multiple favorites

**Field Status:** ✅ `is_favorite` column exists in Migration 010
**Work Needed:** Star icon widget, sorting logic, filter toggle

---

### AC5: Custom Account Ordering ✅
- Drag-and-drop reordering in account tree
- Persist order across sessions
- Work within hierarchy levels
- Visual feedback during drag
- "Reset to default" option

**Field Status:** ✅ `display_order` column exists in Migration 010
**Work Needed:** Drag-drop handling, update methods, reset function

---

## 🔧 Technical Design

### Migration 011 (OPTIONAL)

Since Migration 010 already created all required fields, Migration 011 is **optional**.

**If Created, It Should Only Add:**
```sql
-- Migration 011: Additional indices for US-007 (OPTIONAL)
-- Dependencies: Migration 010 (REQUIRED)

-- Add indices for search optimization
CREATE INDEX IF NOT EXISTS idx_accounts_institution ON accounts(institution_name);
CREATE INDEX IF NOT EXISTS idx_accounts_number ON accounts(account_number);

-- Note: is_favorite and display_order indices already exist from Migration 010
```

**Alternative Approach:**
Skip Migration 011 entirely since:
- All fields already exist in Migration 010
- Current indices may be sufficient
- Can add indices later if performance issues arise

**Tech Lead Decision:** Create minimal Migration 011 for completeness and future-proofing

---

### Repository Layer (7 New Methods)

**File:** `finance_app/data/repositories/account_repository.py`

**Methods to Implement:**

1. **`get_all_sorted()`** - Sort by favorites + display_order
```python
def get_all_sorted(self, include_archived: bool = False) -> List[Account]:
    """Get all accounts sorted by favorite, then display_order, then name."""
    query = """
        SELECT * FROM accounts
        WHERE (is_archived = 0 OR ?)
        ORDER BY is_favorite DESC, display_order ASC, name ASC
    """
```

2. **`get_favorites()`** - Filter favorites only
```python
def get_favorites(self) -> List[Account]:
    """Get only favorite accounts."""
    query = "SELECT * FROM accounts WHERE is_favorite = 1 ORDER BY name"
```

3. **`search_accounts()`** - Search across metadata
```python
def search_accounts(self, query: str) -> List[Account]:
    """Search accounts by name, number, or institution."""
    search_query = """
        SELECT * FROM accounts
        WHERE name LIKE ?
           OR account_number LIKE ?
           OR institution_name LIKE ?
        ORDER BY is_favorite DESC, name ASC
    """
```

4. **`get_institution_names()`** - For autocomplete
```python
def get_institution_names(self) -> List[str]:
    """Get distinct institution names for autocomplete."""
    query = """
        SELECT DISTINCT institution_name
        FROM accounts
        WHERE institution_name IS NOT NULL
        ORDER BY institution_name
    """
```

5. **`group_by_institution()`** - For reports
```python
def group_by_institution(self) -> Dict[str, List[Account]]:
    """Group accounts by institution name."""
    # Returns {institution_name: [accounts]}
```

6. **`update_display_order()`** - For drag-drop
```python
def update_display_order(self, account_id: int, display_order: int) -> Account:
    """Update display order for custom sorting."""
```

7. **`reset_display_order()`** - Reset to default
```python
def reset_display_order(self) -> None:
    """Reset all display orders to default (alphabetical)."""
    query = "UPDATE accounts SET display_order = id"
```

---

### Service Layer (4 New Methods)

**File:** `finance_app/business/account_service.py`

**Methods to Implement:**

1. **`update_metadata()`** - Update account metadata
```python
def update_metadata(
    self,
    account_id: int,
    account_number: Optional[str] = None,
    institution_name: Optional[str] = None,
    notes: Optional[str] = None
) -> Account:
    """Update account metadata fields with validation."""
```

2. **`toggle_favorite()`** - Already implemented in US-009! ✅
```python
def toggle_favorite(self, account_id: int) -> Account:
    """Toggle favorite status (ALREADY EXISTS from US-009)."""
```

3. **`get_institution_autocomplete()`** - Institution suggestions
```python
def get_institution_autocomplete(self, partial: str) -> List[str]:
    """Get institution name suggestions for autocomplete."""
```

4. **`reorder_accounts()`** - Already implemented in US-009! ✅
```python
def reorder_accounts(self, order_pairs: List[Tuple[int, int]]) -> List[Account]:
    """Reorder accounts (ALREADY EXISTS from US-009)."""
```

---

### UI Layer

#### 1. AccountDialog Enhancements
**File:** `finance_app/ui/dialogs/account_dialog.py`

**Add 3 New Form Fields:**
```python
# Account Number field
self.account_number_edit = QLineEdit()
self.account_number_edit.setPlaceholderText("e.g., 1234-5678-9012")
self.account_number_edit.setMaxLength(50)

# Institution Name field (with autocomplete)
self.institution_edit = QLineEdit()
self.institution_completer = QCompleter(institution_names)
self.institution_edit.setCompleter(self.institution_completer)

# Notes field (multi-line)
self.notes_edit = QTextEdit()
self.notes_edit.setMaximumHeight(100)
self.notes_edit.setPlaceholderText("Add notes about this account...")
```

#### 2. Favorite Icon Toggle
**File:** `finance_app/ui/widgets/account_tree_widget.py`

**Add Favorite Star Icon:**
```python
def _create_favorite_icon(self, is_favorite: bool) -> QIcon:
    """Create star icon for favorite accounts."""
    if is_favorite:
        return QIcon.fromTheme("starred")  # Gold star ⭐
    else:
        return QIcon.fromTheme("non-starred")  # Empty star ☆
```

#### 3. Drag-and-Drop Reordering
**File:** `finance_app/ui/widgets/account_tree_widget.py`

**Enable Drag-Drop:**
```python
# Enable drag-drop in tree widget
self.setDragEnabled(True)
self.setAcceptDrops(True)
self.setDragDropMode(QAbstractItemView.InternalMove)

def dropEvent(self, event):
    """Handle account reordering."""
    # Get dropped item new position
    # Calculate new display_order values
    # Call account_service.reorder_accounts()
    # Refresh tree
```

---

### Validation Layer

**File:** `finance_app/business/validators.py`

**Add Validation Methods:**

```python
def validate_account_number(self, account_number: str) -> str:
    """
    Validate account number format.

    Rules:
    - 3-50 characters
    - Alphanumeric + separators (-, ., space)
    - Trim whitespace
    """
    if not account_number:
        return None

    cleaned = account_number.strip()

    if len(cleaned) < 3 or len(cleaned) > 50:
        raise ValidationError("Account number must be 3-50 characters")

    # Allow alphanumeric + common separators
    import re
    if not re.match(r'^[A-Za-z0-9\s\.\-]+$', cleaned):
        raise ValidationError("Invalid account number format")

    return cleaned


def validate_institution_name(self, institution_name: str) -> str:
    """
    Validate and standardize institution name.

    Rules:
    - 2-100 characters
    - Standardize common variations
    """
    if not institution_name:
        return None

    cleaned = institution_name.strip()

    if len(cleaned) < 2 or len(cleaned) > 100:
        raise ValidationError("Institution name must be 2-100 characters")

    # Standardize common bank names
    standardizations = {
        "chase bank": "Chase",
        "wells fargo bank": "Wells Fargo",
        "bank of america": "Bank of America",
        # Add more as needed
    }

    return standardizations.get(cleaned.lower(), cleaned)


def validate_notes(self, notes: str) -> str:
    """
    Validate and sanitize notes.

    Rules:
    - Max 1000 characters
    - HTML escape for XSS prevention
    - Preserve line breaks
    """
    if not notes:
        return None

    if len(notes) > 1000:
        raise ValidationError("Notes cannot exceed 1000 characters")

    # HTML escape for security (prevent XSS)
    import html
    sanitized = html.escape(notes)

    return sanitized
```

---

## 📅 Sprint Schedule (3 Days)

### Day 1: Backend Foundation (5 hours)
**Morning (3 hours):**
- ✅ Review Sprint 11 kickoff
- ✅ Review US-007 story and acceptance criteria
- Create Migration 011 (minimal, indices only)
- Test migration on dev database

**Afternoon (2 hours):**
- Implement validation methods (validate_account_number, validate_institution_name, validate_notes)
- Add unit tests for validation
- Code review validation layer

**Deliverables:**
- Migration 011 complete and tested
- Validation methods complete with tests

---

### Day 2: Repository & Service Layers (5 hours)
**Morning (3 hours):**
- Implement 7 repository methods
- Update `_row_to_account()` to include metadata fields
- Write unit tests for repository methods
- Test search performance (< 100ms for 100 accounts)

**Afternoon (2 hours):**
- Implement service layer methods (update_metadata, get_institution_autocomplete)
- Leverage existing toggle_favorite and reorder_accounts from US-009
- Write unit tests for service methods
- Integration tests for metadata persistence

**Deliverables:**
- All repository methods complete with tests
- All service methods complete with tests
- Search performance validated

---

### Day 3: UI & Integration (3 hours)
**Morning (2 hours):**
- Enhance AccountDialog with 3 new form fields
- Implement institution autocomplete
- Add favorite star icon toggle
- Wire up save/load logic

**Afternoon (1 hour):**
- Implement drag-and-drop reordering
- Add "Show only favorites" filter toggle
- UI testing with real data
- Visual polish

**Deliverables:**
- AccountDialog enhanced and functional
- Favorite toggle working
- Drag-drop reordering working
- All UI interactions smooth

---

### Stretch Goals (if time permits)
- Visual regression tests with xvfb
- User documentation section in USER_GUIDE.md
- Performance monitoring for search queries
- Institution name standardization improvements

---

## 🧪 Testing Strategy

### Unit Tests (Estimated: 18 tests)

**Validation Tests (3 tests):**
- `test_validate_account_number_valid()`
- `test_validate_institution_name_standardization()`
- `test_validate_notes_sanitization()`

**Repository Tests (7 tests):**
- `test_get_all_sorted_favorites_first()`
- `test_search_accounts_by_number()`
- `test_get_institution_names_autocomplete()`
- `test_group_by_institution()`
- `test_update_display_order()`
- `test_reset_display_order()`
- `test_get_favorites_only()`

**Service Tests (5 tests):**
- `test_update_metadata_validation()`
- `test_get_institution_autocomplete()`
- `test_toggle_favorite_persists()` (reuse US-009 test)
- `test_reorder_accounts_persists()` (reuse US-009 test)
- `test_update_metadata_xss_prevention()`

**UI Tests (3 tests):**
- `test_account_dialog_metadata_fields()`
- `test_favorite_toggle_ui()`
- `test_drag_drop_reordering()`

---

### Integration Tests (Estimated: 5 tests)

**File:** `finance_app/tests/integration/test_us007_metadata_integration.py`

**Tests:**
1. `test_metadata_persists_across_app_restart()`
2. `test_search_finds_account_by_metadata()`
3. `test_favorite_sorting_persists()`
4. `test_custom_order_persists_after_drag_drop()`
5. `test_institution_autocomplete_end_to_end()`

---

### E2E Tests (Optional)

**Script:** `tests/e2e_us007_validation.sh`

**Scenarios:**
1. Create account with full metadata
2. Toggle favorite status
3. Drag-drop to reorder
4. Search by account number
5. Filter favorites only
6. Institution autocomplete

---

## 🎯 Acceptance Criteria Checklist

### AC1: Account Number Field
- [ ] Field in AccountDialog
- [ ] Validation (3-50 chars, alphanumeric + separators)
- [ ] Display in account details
- [ ] Searchable via search_accounts()
- [ ] Shows in reconciliation dialog

### AC2: Institution Name with Autocomplete
- [ ] Field in AccountDialog with QCompleter
- [ ] Autocomplete suggests previous institutions
- [ ] Standardization working (e.g., "Chase Bank" → "Chase")
- [ ] Group by institution method working
- [ ] Searchable

### AC3: Notes Field
- [ ] Multi-line QTextEdit in AccountDialog
- [ ] 1000 character limit enforced
- [ ] Line breaks preserved
- [ ] Truncated display in list view (100 chars)
- [ ] Full display in details dialog
- [ ] XSS sanitization working

### AC4: Favorite Accounts
- [ ] Star icon toggle in account tree
- [ ] Favorites sort to top
- [ ] "Show only favorites" filter works
- [ ] Persists across sessions
- [ ] Multiple favorites supported

### AC5: Custom Account Ordering
- [ ] Drag-drop enabled in account tree
- [ ] Visual feedback during drag
- [ ] Order persists across sessions
- [ ] Works within hierarchy levels
- [ ] "Reset to default" option available

### AC6: Search Across Metadata
- [ ] Search by account name
- [ ] Search by account number
- [ ] Search by institution name
- [ ] Search excludes notes (performance)
- [ ] Results sorted (favorites first)

### AC7: Hierarchy Integration
- [ ] Favorites sort within their level
- [ ] Custom order works per-level
- [ ] Parent-child relationships preserved
- [ ] Drag-drop respects hierarchy

---

## 🚧 Risk Assessment

### Low Risk ✅
- **Migration 011:** Minimal (only 2 indices, optional)
- **Database fields:** Already exist from Migration 010
- **Service methods:** Leverage existing US-009 methods

### Medium Risk 🟡
- **Autocomplete widget:** First time implementing autocomplete
- **Drag-drop reordering:** UI complexity, need to handle edge cases
- **Search performance:** Must test with 100+ accounts

### Mitigation Strategies
1. **Autocomplete:** Use Qt's QCompleter (well-documented, proven)
2. **Drag-drop:** Reuse US-006 hierarchy drag-drop patterns
3. **Performance:** Create test database with 100 accounts for benchmarking

---

## 📊 Success Metrics

### Development Metrics
- **Estimation Accuracy:** Target 100% (13h estimate = 13h actual)
- **Test Pass Rate:** Target 100% (23/23 tests passing)
- **Code Quality:** Target 5/5 stars (match US-009)
- **Performance:** Search < 100ms, autocomplete < 50ms

### User Metrics (Post-Release)
- **Adoption:** 60%+ users add account numbers (within 1 month)
- **Engagement:** 40%+ users mark favorites
- **Customization:** 30%+ users customize order

---

## 📚 Reference Materials

### Code Patterns to Follow
- **Validation:** US-001 AccountValidator patterns
- **Repository:** US-006 hierarchy repository patterns
- **Service:** US-009 color service patterns
- **UI Dialogs:** US-005 AccountDialog patterns
- **Drag-Drop:** US-006 tree widget drag-drop

### Documentation to Review
- [US-007 Full Story](../stories/backlog/US-007-account-metadata.md)
- [EPIC-001 Overview](../epics/EPIC-001-account-management.md)
- [US-006 Hierarchy Implementation](../stories/completed/US-006-account-hierarchy.md)
- [US-009 Color System](../stories/backlog/US-009-account-color-coding.md)

### External Resources
- [Qt QCompleter Documentation](https://doc.qt.io/qt-6/qcompleter.html)
- [Qt Drag and Drop](https://doc.qt.io/qt-6/dnd.html)
- [SQLite Full-Text Search](https://www.sqlite.org/fts5.html) (future enhancement)

---

## 🎓 Lessons from Sprint 10 (US-009)

### What Worked Well ✅
1. **Forward-looking migration design** - Migration 010 created US-007 fields
2. **Accurate estimation** - 13h estimate = 13h actual
3. **WCAG compliance** - Accessibility built-in from start
4. **Comprehensive testing** - 100% unit test coverage
5. **E2E framework** - xvfb testing established

### Apply to Sprint 11
1. **Reuse Migration 010 fields** - No schema changes needed!
2. **Follow 13-hour timeline** - Similar scope, similar estimate
3. **Accessibility** - Keyboard nav for favorites, drag-drop
4. **100% test coverage** - Continue high testing standards
5. **E2E validation** - Reuse xvfb framework for US-007

---

## 🔗 Integration Points

### US-004 (Account Reconciliation)
- **Integration:** Display `account_number` in reconciliation dialog
- **File:** `finance_app/ui/dialogs/reconciliation_dialog.py`
- **Change:** Add account number label next to account name

### US-006 (Account Hierarchy)
- **Integration:** Drag-drop respects parent-child relationships
- **File:** `finance_app/ui/widgets/account_tree_widget.py`
- **Change:** Reorder within same parent only

### US-009 (Color Coding)
- **Integration:** Favorite star + color dot both visible
- **File:** `finance_app/ui/widgets/account_tree_widget.py`
- **Change:** Icon composition (color dot + favorite star)

---

## ✅ Definition of Done

### Code Complete
- [ ] All repository methods implemented and tested
- [ ] All service methods implemented and tested
- [ ] All UI components functional
- [ ] Migration 011 created (optional) and tested
- [ ] No linting errors
- [ ] Type hints throughout

### Testing Complete
- [ ] 18 unit tests passing
- [ ] 5 integration tests passing
- [ ] E2E validation successful (optional)
- [ ] Performance benchmarks met (search < 100ms)
- [ ] Manual testing on dev database

### Documentation Complete
- [ ] Code docstrings added
- [ ] Sprint completion summary created
- [ ] US-007 status updated to COMPLETE
- [ ] EPIC-001 progress updated to 92%
- [ ] User documentation section added (stretch goal)

### Review & Approval
- [ ] Code review by tech lead
- [ ] Product owner acceptance
- [ ] All acceptance criteria verified
- [ ] No critical issues found

---

## 🚀 Ready to Start!

**Sprint 11 is ready to begin:**
- ✅ All dependencies met (US-009 complete)
- ✅ Migration 010 provides all required fields
- ✅ Task breakdown is comprehensive
- ✅ Estimation is based on proven accuracy (US-009)
- ✅ Testing strategy is defined
- ✅ Success metrics are clear

**Let's build an amazing metadata and organization system!** 🎉

---

**Next Steps:**
1. Assign developers to Sprint 11
2. Set up dev environment
3. Create Migration 011 (Day 1 AM)
4. Begin validation layer implementation (Day 1 PM)

**Estimated Completion:** 3 days from start
**Target Sprint End:** Sprint 11 Day 3

---

*Sprint 11 Kickoff - Created 2025-11-04*
*EPIC-001 Progress: 83% → 92% (after US-007)*
*Final Sprint 12: US-008 (Multi-Currency)*

**🎯 Onward to 92% EPIC-001 completion!**
