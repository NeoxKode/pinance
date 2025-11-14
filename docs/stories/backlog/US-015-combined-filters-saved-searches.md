# US-015: Combined Filters & Saved Searches 💾

**Story ID:** US-015
**Epic:** [EPIC-002: Search and Filter Transactions](../../epics/EPIC-002-search-filter-transactions.md)
**Created:** 2025-11-11
**Status:** 📋 BACKLOG - Sprint 15 (Not Started)
**Priority:** P2 (Could Have - Power user feature)
**Story Points:** 5 (Highest complexity in EPIC-002)
**Sprint:** Sprint 15 (Week 5-6) - May move to Sprint 16 if overloaded
**Dependencies:** ✅ US-011, US-012, US-013, US-014 (All individual filters), ✅ US-016 (Filter UI Panel)
**Related Stories:** All other EPIC-002 stories

---

## 📖 User Story

**As a** power user with complex analysis needs
**I want** to combine multiple filters and save them for reuse
**So that** I can quickly access common searches like "Monthly Groceries" without re-entering filters

---

## 📝 Description

This is the capstone story of EPIC-002, enabling filter combination and persistence. Allows users to create saved searches like "Monthly Groceries" = Groceries + This Month + > $20.

**Problem:** Repeatedly entering same filter combinations is tedious
**Solution:** Combined filter logic + database persistence for saved searches

**Use Cases:**
1. Budget Routine: Save "Monthly Groceries" = Groceries + This Month
2. Expense Review: Save "Large Expenses" = Amount > $100
3. Subscription Tracking: Save "Small Recurring" = Amount < $20 + This Month

---

## 🎯 Acceptance Criteria

### AC1: Combined Filter Logic
- [ ] Text + Date + Category + Amount work together
- [ ] Filters use AND logic: "Groceries AND Last Month AND > $50"
- [ ] All filters applied simultaneously
- [ ] Performance: < 300ms for 10,000 transactions with all filters

### AC2: Save Filter
- [ ] "Save Current Filters" button in filter panel
- [ ] Dialog prompts for name: "Monthly Groceries"
- [ ] Optional description field
- [ ] Saves all active filter values to database
- [ ] Saved filters appear in dropdown

### AC3: Load Filter
- [ ] "Saved Filters" dropdown shows all saved filters
- [ ] Selecting saved filter applies all values
- [ ] Tooltip shows filter details on hover

### AC4: Manage Saved Filters
- [ ] "Manage Saved Filters" button opens dialog
- [ ] List shows: Name, Description, Criteria, Last used
- [ ] Can edit, delete, or mark favorite (⭐)
- [ ] Favorites appear at top

### AC5: Database Persistence
- [ ] New table: `saved_filters`
- [ ] Stores filter criteria as JSON
- [ ] Tracks created/updated timestamps

---

## 🔧 Technical Implementation

### Backend

**New Table (Migration 012):**
```sql
CREATE TABLE saved_filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    filter_json TEXT NOT NULL,  -- {"text": "coffee", "date_from": "2025-01-01", ...}
    is_favorite BOOLEAN DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_saved_filters_favorite ON saved_filters(is_favorite);
```

**New Repository:** `saved_filter_repository.py`
```python
class SavedFilterRepository:
    """CRUD operations for saved filters."""

    def create_saved_filter(
        self,
        name: str,
        filter_criteria: dict,
        description: str = None
    ) -> int:
        """Save filter to database."""
        filter_json = json.dumps(filter_criteria)
        now = datetime.now().isoformat()

        query = """
            INSERT INTO saved_filters
            (name, description, filter_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.db.execute(query, [name, description, filter_json, now, now])
        return cursor.lastrowid

    def get_all_saved_filters(self) -> List[SavedFilter]:
        """Get all saved filters, favorites first."""
        query = """
            SELECT * FROM saved_filters
            ORDER BY is_favorite DESC, name ASC
        """
        # Execute and return...
```

**New Service:** `filter_service.py`
```python
class FilterService:
    """Manage combined filters and saved searches."""

    def apply_combined_filters(
        self,
        text: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        categories: Optional[List[str]] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """Apply multiple filters simultaneously (AND logic)."""
        # Build complex SQL query combining all filters
        # Use indexes for performance
        # Return combined results

    def save_current_filters(self, name: str, filter_state: dict) -> int:
        """Save current filter state."""
        return self.saved_filter_repo.create_saved_filter(name, filter_state)

    def load_saved_filter(self, filter_id: int) -> dict:
        """Load saved filter and return filter criteria."""
        saved_filter = self.saved_filter_repo.get_by_id(filter_id)
        return json.loads(saved_filter.filter_json)
```

### Frontend

**Save Filter Dialog:**
```python
class SaveFilterDialog(QDialog):
    """Dialog for saving current filter state."""

    def __init__(self, current_filters: dict, parent=None):
        # Input for filter name
        # Optional description field
        # Preview of filter criteria
        # Save/Cancel buttons
```

**Manage Filters Dialog:**
```python
class ManageFiltersDialog(QDialog):
    """Dialog for managing saved filters."""

    def __init__(self, parent=None):
        # Table showing all saved filters
        # Columns: Name, Description, Criteria, Last Used, Favorite
        # Edit/Delete/Favorite buttons
```

**SearchPanelWidget Updates:**
```python
def _add_saved_filters_ui(self):
    """Add saved filters dropdown and manage button."""
    self.saved_filters_combo = QComboBox()
    self.saved_filters_combo.currentIndexChanged.connect(self._on_load_saved_filter)

    self.save_button = QPushButton("Save Current Filters")
    self.save_button.clicked.connect(self._on_save_filters)

    self.manage_button = QPushButton("Manage...")
    self.manage_button.clicked.connect(self._on_manage_filters)
```

---

## 🧪 Testing

**Unit Tests (15+):**
- Combined filter logic (all combinations)
- Save filter functionality
- Load filter functionality
- JSON serialization/deserialization
- Favorite marking
- Edit/delete operations

**Integration Tests (5+):**
- End-to-end save and load
- Combined filters with real data
- Manage dialog CRUD operations
- Performance with all filters active
- Filter persistence across sessions

**Performance Test:**
```python
def test_combined_filters_performance():
    """Test all filters together on 10K transactions."""
    # Apply text + date + category + amount filters
    # Assert: < 300ms
```

---

## 📋 Definition of Done

- [ ] Combined filter logic working (AND logic)
- [ ] Save filter dialog implemented
- [ ] Load filter dropdown working
- [ ] Manage filters dialog complete
- [ ] Database table `saved_filters` created
- [ ] `SavedFilterRepository` implemented
- [ ] `FilterService` implemented
- [ ] 15+ unit tests passing
- [ ] 5+ integration tests passing
- [ ] Performance < 300ms with all filters
- [ ] User Guide chapter on saved searches complete

---

## 📊 Success Metrics

**Development:** 5 points (7-10 hours)
**User Adoption:** 40% of power users create saved filters
**Performance:** < 300ms for all filters combined

---

## 🔗 Related Documentation

- [EPIC-002: Search and Filter Transactions](../../epics/EPIC-002-search-filter-transactions.md)
- [US-011: Basic Text Search](./US-011-basic-text-search.md)
- [US-012: Date Range Filter](./US-012-date-range-filter.md)
- [US-013: Category Filter](./US-013-category-filter.md)
- [US-014: Amount Range Filter](./US-014-amount-range-filter.md)
- [US-016: Search & Filter UI Panel](./US-016-search-filter-ui-panel.md)

---

## 📝 Notes

**Why Highest Complexity (5 points):**
- Requires new database table and repository
- JSON serialization/deserialization
- Complex UI (2 new dialogs + dropdown)
- Combined filter query building
- Potential for scope creep (manage features)

**Risk Mitigation:**
- May move to Sprint 16 if Sprint 15 overloaded
- Can deliver MVP without "Manage" dialog (just save/load)
- Performance testing critical (300ms target with 4 filters)

**Out of Scope:**
- Filter sharing between users
- Filter export/import
- Advanced filter operators (OR, NOT)
- Search history tracking

---

**Created:** 2025-11-11
**Sprint:** Sprint 15 (Week 5-6) or Sprint 16
**Status:** 📋 BACKLOG
