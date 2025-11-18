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

## 📋 Task Breakdown for Development

This section provides a detailed, step-by-step implementation plan for developers. US-015 is the most complex story in EPIC-002 at 5 story points.

### Phase 1: Database & Model Foundation (Day 1 Morning - 2 hours) **BACKEND DEV**

#### Task 1.1: Create Database Migration (012)
**Assignee:** Backend Developer / Tech Lead
**Estimate:** 1 hour
**Files:** `finance_app/data/migrations/012_saved_filters.sql` (NEW)

**Migration SQL:**
```sql
-- Migration 012: Add saved_filters table for filter persistence

CREATE TABLE IF NOT EXISTS saved_filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    filter_json TEXT NOT NULL,  -- JSON: {"text": "coffee", "date_from": "2025-01-01", ...}
    is_favorite BOOLEAN DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_used_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_saved_filters_favorite
    ON saved_filters(is_favorite DESC, name ASC);

CREATE INDEX IF NOT EXISTS idx_saved_filters_name
    ON saved_filters(name);
```

**Acceptance:**
- [ ] Migration file created
- [ ] `saved_filters` table created with 7 columns
- [ ] 2 indexes created (favorite, name)
- [ ] Migration tested on development database
- [ ] Rollback script documented

**Testing:**
```python
def test_migration_012_creates_saved_filters_table():
    """Test migration 012 creates saved_filters table."""
    # Apply migration
    # Check table exists
    cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saved_filters'")
    assert cursor.fetchone() is not None

    # Check indexes exist
    cursor = db.execute("PRAGMA index_list('saved_filters')")
    indices = [row[1] for row in cursor.fetchall()]
    assert 'idx_saved_filters_favorite' in indices
    assert 'idx_saved_filters_name' in indices
```

---

#### Task 1.2: Create SavedFilter Model
**Assignee:** Backend Developer
**Estimate:** 30 minutes
**Files:** `finance_app/data/models.py`

**Model Definition:**
```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import json


@dataclass
class SavedFilter:
    """Saved filter configuration."""

    id: Optional[int]
    name: str
    filter_json: str  # JSON string
    description: Optional[str] = None
    is_favorite: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    @property
    def filter_criteria(self) -> dict:
        """Parse filter JSON to dict."""
        return json.loads(self.filter_json)

    @classmethod
    def from_dict(cls, data: dict) -> 'SavedFilter':
        """Create SavedFilter from filter criteria dict."""
        return cls(
            id=None,
            name=data['name'],
            description=data.get('description'),
            filter_json=json.dumps(data['criteria']),
            is_favorite=data.get('is_favorite', False)
        )
```

**Acceptance:**
- [ ] SavedFilter model added to models.py
- [ ] filter_criteria property for JSON parsing
- [ ] from_dict() class method for creation
- [ ] Type hints complete
- [ ] Docstrings complete

---

### Phase 2: Backend - Repository Layer (Day 1 Afternoon - 2.5 hours) **BACKEND DEV**

#### Task 2.1: Create SavedFilterRepository
**Assignee:** Backend Developer
**Estimate:** 2.5 hours
**Files:** `finance_app/data/repositories/saved_filter_repository.py` (NEW)

**Full Repository Implementation:**
```python
from typing import List, Optional
from datetime import datetime
import json
from finance_app.data.models import SavedFilter


class SavedFilterRepository:
    """Repository for saved filter CRUD operations."""

    def __init__(self, db):
        self.db = db

    def create(self, saved_filter: SavedFilter) -> SavedFilter:
        """Create new saved filter."""
        now = datetime.now().isoformat()

        query = """
            INSERT INTO saved_filters
            (name, description, filter_json, is_favorite, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = [
            saved_filter.name,
            saved_filter.description,
            saved_filter.filter_json,
            saved_filter.is_favorite,
            now,
            now
        ]

        cursor = self.db.execute(query, params)
        saved_filter.id = cursor.lastrowid
        saved_filter.created_at = now
        saved_filter.updated_at = now
        return saved_filter

    def get_by_id(self, filter_id: int) -> Optional[SavedFilter]:
        """Get saved filter by ID."""
        query = "SELECT * FROM saved_filters WHERE id = ?"
        cursor = self.db.execute(query, [filter_id])
        row = cursor.fetchone()
        return self._row_to_saved_filter(row) if row else None

    def get_by_name(self, name: str) -> Optional[SavedFilter]:
        """Get saved filter by name."""
        query = "SELECT * FROM saved_filters WHERE name = ?"
        cursor = self.db.execute(query, [name])
        row = cursor.fetchone()
        return self._row_to_saved_filter(row) if row else None

    def get_all(self) -> List[SavedFilter]:
        """Get all saved filters, favorites first."""
        query = """
            SELECT * FROM saved_filters
            ORDER BY is_favorite DESC, name ASC
        """
        cursor = self.db.execute(query)
        rows = cursor.fetchall()
        return [self._row_to_saved_filter(row) for row in rows]

    def update(self, saved_filter: SavedFilter) -> SavedFilter:
        """Update existing saved filter."""
        now = datetime.now().isoformat()

        query = """
            UPDATE saved_filters
            SET name = ?, description = ?, filter_json = ?,
                is_favorite = ?, updated_at = ?
            WHERE id = ?
        """
        params = [
            saved_filter.name,
            saved_filter.description,
            saved_filter.filter_json,
            saved_filter.is_favorite,
            now,
            saved_filter.id
        ]

        self.db.execute(query, params)
        saved_filter.updated_at = now
        return saved_filter

    def delete(self, filter_id: int) -> bool:
        """Delete saved filter."""
        query = "DELETE FROM saved_filters WHERE id = ?"
        cursor = self.db.execute(query, [filter_id])
        return cursor.rowcount > 0

    def mark_as_used(self, filter_id: int):
        """Update last_used_at timestamp."""
        now = datetime.now().isoformat()
        query = "UPDATE saved_filters SET last_used_at = ? WHERE id = ?"
        self.db.execute(query, [now, filter_id])

    def toggle_favorite(self, filter_id: int) -> bool:
        """Toggle favorite status."""
        query = """
            UPDATE saved_filters
            SET is_favorite = NOT is_favorite, updated_at = ?
            WHERE id = ?
        """
        now = datetime.now().isoformat()
        self.db.execute(query, [now, filter_id])

        # Return new favorite status
        saved_filter = self.get_by_id(filter_id)
        return saved_filter.is_favorite if saved_filter else False

    def _row_to_saved_filter(self, row) -> SavedFilter:
        """Convert database row to SavedFilter model."""
        return SavedFilter(
            id=row[0],
            name=row[1],
            description=row[2],
            filter_json=row[3],
            is_favorite=bool(row[4]),
            created_at=row[5],
            updated_at=row[6],
            last_used_at=row[7] if len(row) > 7 else None
        )
```

**Acceptance:**
- [ ] SavedFilterRepository class created
- [ ] CRUD methods: create, get_by_id, get_by_name, get_all, update, delete
- [ ] mark_as_used() method for tracking usage
- [ ] toggle_favorite() method
- [ ] _row_to_saved_filter() mapper
- [ ] Error handling for unique constraint (name)
- [ ] Type hints complete
- [ ] Docstrings complete

**Testing:**
```python
def test_saved_filter_repository_create(saved_filter_repo):
    """Test creating saved filter."""
    saved_filter = SavedFilter(
        id=None,
        name="Monthly Groceries",
        description="Groceries from this month",
        filter_json='{"categories": ["Groceries"], "date_preset": "this_month"}'
    )

    created = saved_filter_repo.create(saved_filter)
    assert created.id is not None
    assert created.created_at is not None

def test_saved_filter_repository_get_all_favorites_first(saved_filter_repo):
    """Test get_all returns favorites first."""
    # Create normal filter
    # Create favorite filter
    all_filters = saved_filter_repo.get_all()
    assert all_filters[0].is_favorite == True
```

---

### Phase 3: Backend - Service Layer (Day 2 Morning - 2.5 hours) **BACKEND DEV**

#### Task 3.1: Create FilterService for Combined Filters
**Assignee:** Backend Developer
**Estimate:** 2.5 hours
**Files:** `finance_app/business/filter_service.py` (NEW)

**Service Implementation:**
```python
from typing import List, Optional, Dict
from decimal import Decimal
from datetime import date
from finance_app.data.models import Transaction, SavedFilter
from finance_app.data.repositories.saved_filter_repository import SavedFilterRepository
from finance_app.business.transaction_service import TransactionService
import json


class FilterService:
    """Service for managing combined filters and saved searches."""

    def __init__(self, saved_filter_repo: SavedFilterRepository, transaction_service: TransactionService):
        self.saved_filter_repo = saved_filter_repo
        self.transaction_service = transaction_service

    def apply_combined_filters(
        self,
        text: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        categories: Optional[List[str]] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        amount_absolute: bool = False,
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Apply multiple filters simultaneously using AND logic.

        All filters are combined: a transaction must match ALL active filters to appear.

        Performance:
            Target: < 300ms for 10,000 transactions with all filters active
        """
        # Start with all transactions
        transactions = self.transaction_service.get_all_transactions(account_id=account_id)

        # Apply text filter
        if text:
            text_lower = text.lower()
            transactions = [t for t in transactions if text_lower in t.description.lower()]

        # Apply date filter
        if date_from and date_to:
            transactions = [t for t in transactions if date_from <= t.date <= date_to]

        # Apply category filter
        if categories:
            transactions = [t for t in transactions if t.category in categories]

        # Apply amount filter
        if min_amount is not None or max_amount is not None:
            transactions = [
                t for t in transactions
                if self._amount_in_range(t.amount, min_amount, max_amount, amount_absolute)
            ]

        return transactions

    def save_filter(
        self,
        name: str,
        filter_criteria: Dict,
        description: Optional[str] = None
    ) -> SavedFilter:
        """
        Save current filter state.

        Args:
            name: Filter name (must be unique)
            filter_criteria: Dict of filter values
            description: Optional description

        Returns:
            Created SavedFilter

        Raises:
            ValueError: If name already exists
        """
        # Check if name exists
        existing = self.saved_filter_repo.get_by_name(name)
        if existing:
            raise ValueError(f"Filter name '{name}' already exists")

        # Create SavedFilter
        saved_filter = SavedFilter(
            id=None,
            name=name,
            description=description,
            filter_json=json.dumps(filter_criteria)
        )

        return self.saved_filter_repo.create(saved_filter)

    def load_filter(self, filter_id: int) -> Dict:
        """
        Load saved filter and return criteria.

        Args:
            filter_id: Saved filter ID

        Returns:
            Filter criteria dict

        Raises:
            ValueError: If filter not found
        """
        saved_filter = self.saved_filter_repo.get_by_id(filter_id)
        if not saved_filter:
            raise ValueError(f"Saved filter {filter_id} not found")

        # Mark as used
        self.saved_filter_repo.mark_as_used(filter_id)

        return saved_filter.filter_criteria

    def get_all_saved_filters(self) -> List[SavedFilter]:
        """Get all saved filters, favorites first."""
        return self.saved_filter_repo.get_all()

    def update_saved_filter(
        self,
        filter_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        filter_criteria: Optional[Dict] = None
    ) -> SavedFilter:
        """Update saved filter."""
        saved_filter = self.saved_filter_repo.get_by_id(filter_id)
        if not saved_filter:
            raise ValueError(f"Saved filter {filter_id} not found")

        if name:
            saved_filter.name = name
        if description is not None:
            saved_filter.description = description
        if filter_criteria:
            saved_filter.filter_json = json.dumps(filter_criteria)

        return self.saved_filter_repo.update(saved_filter)

    def delete_saved_filter(self, filter_id: int) -> bool:
        """Delete saved filter."""
        return self.saved_filter_repo.delete(filter_id)

    def toggle_favorite(self, filter_id: int) -> bool:
        """Toggle favorite status, return new status."""
        return self.saved_filter_repo.toggle_favorite(filter_id)

    def _amount_in_range(
        self,
        amount: Decimal,
        min_amount: Optional[Decimal],
        max_amount: Optional[Decimal],
        absolute: bool
    ) -> bool:
        """Check if amount is in range."""
        check_amount = abs(amount) if absolute else amount

        if min_amount and check_amount < min_amount:
            return False

        if max_amount and check_amount > max_amount:
            return False

        return True
```

**Acceptance:**
- [ ] FilterService class created
- [ ] apply_combined_filters() with ALL filter parameters
- [ ] save_filter() with duplicate name validation
- [ ] load_filter() with mark_as_used
- [ ] get_all_saved_filters()
- [ ] update_saved_filter()
- [ ] delete_saved_filter()
- [ ] toggle_favorite()
- [ ] Type hints complete
- [ ] Docstrings complete

**Testing:**
```python
def test_apply_combined_filters_all_active(filter_service):
    """Test combined filters with all filters active."""
    results = filter_service.apply_combined_filters(
        text="coffee",
        date_from=date(2025, 1, 1),
        date_to=date(2025, 1, 31),
        categories=["Dining Out"],
        min_amount=Decimal("5"),
        max_amount=Decimal("20")
    )

    # Verify all filters applied
    for txn in results:
        assert "coffee" in txn.description.lower()
        assert date(2025, 1, 1) <= txn.date <= date(2025, 1, 31)
        assert txn.category == "Dining Out"
        assert Decimal("5") <= txn.amount <= Decimal("20")

def test_save_filter_duplicate_name(filter_service):
    """Test save filter rejects duplicate name."""
    filter_service.save_filter("Test Filter", {"text": "test"})

    with pytest.raises(ValueError, match="already exists"):
        filter_service.save_filter("Test Filter", {"text": "test2"})
```

---

### Phase 4: Frontend - Save Filter Dialog (Day 2 Afternoon - 2 hours) **FRONTEND DEV**

#### Task 4.1: Create SaveFilterDialog
**Assignee:** Frontend Developer
**Estimate:** 2 hours
**Files:** `finance_app/ui/dialogs/save_filter_dialog.py` (NEW)

**Dialog Implementation:**
```python
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QTextEdit, QLabel, QPushButton, QMessageBox
)
from typing import Dict


class SaveFilterDialog(QDialog):
    """Dialog for saving current filter state."""

    def __init__(self, current_filters: Dict, parent=None):
        super().__init__(parent)
        self.current_filters = current_filters
        self.setWindowTitle("Save Filter")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Filter name input
        layout.addWidget(QLabel("Filter Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Monthly Groceries")
        layout.addWidget(self.name_input)

        # Description input (optional)
        layout.addWidget(QLabel("Description (optional):"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("e.g., Groceries from this month")
        self.description_input.setMaximumHeight(60)
        layout.addWidget(self.description_input)

        # Filter preview
        layout.addWidget(QLabel("Filter Criteria:"))
        preview_text = self._build_filter_preview()
        preview_label = QLabel(preview_text)
        preview_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        preview_label.setWordWrap(True)
        layout.addWidget(preview_label)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._validate_and_save)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def _build_filter_preview(self) -> str:
        """Build human-readable filter preview."""
        criteria = []

        if self.current_filters.get('text'):
            criteria.append(f"Text: \"{self.current_filters['text']}\"")

        if self.current_filters.get('date_preset'):
            criteria.append(f"Date: {self.current_filters['date_preset']}")
        elif self.current_filters.get('date_from') and self.current_filters.get('date_to'):
            criteria.append(f"Date: {self.current_filters['date_from']} to {self.current_filters['date_to']}")

        if self.current_filters.get('categories'):
            cats = ", ".join(self.current_filters['categories'])
            criteria.append(f"Categories: {cats}")

        if self.current_filters.get('min_amount') or self.current_filters.get('max_amount'):
            min_amt = self.current_filters.get('min_amount', '')
            max_amt = self.current_filters.get('max_amount', '')
            if min_amt and max_amt:
                criteria.append(f"Amount: ${min_amt} - ${max_amt}")
            elif min_amt:
                criteria.append(f"Amount: >= ${min_amt}")
            elif max_amt:
                criteria.append(f"Amount: <= ${max_amt}")

        return "\n".join(criteria) if criteria else "No filters active"

    def _validate_and_save(self):
        """Validate and accept dialog."""
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Invalid Input", "Filter name cannot be empty.")
            return

        self.accept()

    def get_filter_data(self) -> Dict:
        """Return filter data for saving."""
        return {
            'name': self.name_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'criteria': self.current_filters
        }
```

**Acceptance:**
- [ ] SaveFilterDialog class created
- [ ] Name input (required)
- [ ] Description input (optional)
- [ ] Filter criteria preview (human-readable)
- [ ] Validation: name not empty
- [ ] get_filter_data() returns dict
- [ ] Cancel/Save buttons

**Testing:**
```python
def test_save_filter_dialog_validation(qtbot):
    """Test dialog validates name."""
    dialog = SaveFilterDialog({})
    qtbot.addWidget(dialog)

    # Empty name should show warning
    dialog._validate_and_save()
    # Should not accept (dialog still open)
```

---

#### Task 4.2: Create ManageFiltersDialog
**Assignee:** Frontend Developer
**Estimate:** 2 hours (included in Phase 5)
**Files:** `finance_app/ui/dialogs/manage_filters_dialog.py` (NEW)

This will be implemented in Phase 5.

---

### Phase 5: Frontend - Manage Filters Dialog (Day 3 Morning - 2.5 hours) **FRONTEND DEV**

#### Task 5.1: Create ManageFiltersDialog
**Assignee:** Frontend Developer
**Estimate:** 2.5 hours
**Files:** `finance_app/ui/dialogs/manage_filters_dialog.py` (NEW)

**Dialog Implementation:**
```python
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from typing import List
from finance_app.data.models import SavedFilter


class ManageFiltersDialog(QDialog):
    """Dialog for managing saved filters."""

    filter_deleted = Signal(int)  # filter_id
    filter_edited = Signal(int)  # filter_id
    filter_favorited = Signal(int)  # filter_id

    def __init__(self, saved_filters: List[SavedFilter], parent=None):
        super().__init__(parent)
        self.saved_filters = saved_filters
        self.setWindowTitle("Manage Saved Filters")
        self.setMinimumSize(700, 400)
        self._setup_ui()
        self._populate_table()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Description", "Criteria", "Last Used", "Favorite", "Actions"
        ])

        # Resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Name
        header.setSectionResizeMode(1, QHeaderView.Stretch)     # Description
        header.setSectionResizeMode(2, QHeaderView.Stretch)     # Criteria
        header.setSectionResizeMode(3, QHeaderView.Interactive)  # Last Used
        header.setSectionResizeMode(4, QHeaderView.Fixed)        # Favorite
        header.setSectionResizeMode(5, QHeaderView.Fixed)        # Actions

        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 150)

        layout.addWidget(self.table)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

    def _populate_table(self):
        """Populate table with saved filters."""
        self.table.setRowCount(len(self.saved_filters))

        for row, saved_filter in enumerate(self.saved_filters):
            # Name
            self.table.setItem(row, 0, QTableWidgetItem(saved_filter.name))

            # Description
            desc = saved_filter.description or ""
            self.table.setItem(row, 1, QTableWidgetItem(desc))

            # Criteria (summary)
            criteria_summary = self._build_criteria_summary(saved_filter)
            self.table.setItem(row, 2, QTableWidgetItem(criteria_summary))

            # Last Used
            last_used = saved_filter.last_used_at or "Never"
            if last_used != "Never":
                last_used = last_used[:10]  # Show date only
            self.table.setItem(row, 3, QTableWidgetItem(last_used))

            # Favorite
            fav_text = "⭐" if saved_filter.is_favorite else ""
            fav_item = QTableWidgetItem(fav_text)
            fav_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, fav_item)

            # Actions (buttons)
            actions_widget = self._create_action_buttons(saved_filter)
            self.table.setCellWidget(row, 5, actions_widget)

    def _build_criteria_summary(self, saved_filter: SavedFilter) -> str:
        """Build short criteria summary."""
        criteria = saved_filter.filter_criteria
        parts = []

        if criteria.get('text'):
            parts.append(f"Text: {criteria['text']}")
        if criteria.get('date_preset'):
            parts.append(f"Date: {criteria['date_preset']}")
        if criteria.get('categories'):
            parts.append(f"Cat: {', '.join(criteria['categories'][:2])}")
        if criteria.get('min_amount') or criteria.get('max_amount'):
            parts.append("Amount filter")

        return " | ".join(parts) if parts else "No filters"

    def _create_action_buttons(self, saved_filter: SavedFilter) -> QWidget:
        """Create action buttons for row."""
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)

        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setMaximumWidth(60)
        edit_btn.clicked.connect(lambda: self._on_edit(saved_filter))
        layout.addWidget(edit_btn)

        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setMaximumWidth(60)
        delete_btn.clicked.connect(lambda: self._on_delete(saved_filter))
        layout.addWidget(delete_btn)

        # Favorite button
        fav_btn = QPushButton("⭐" if not saved_filter.is_favorite else "☆")
        fav_btn.setMaximumWidth(30)
        fav_btn.clicked.connect(lambda: self._on_toggle_favorite(saved_filter))
        layout.addWidget(fav_btn)

        return widget

    def _on_edit(self, saved_filter: SavedFilter):
        """Handle edit button click."""
        # TODO: Open edit dialog
        self.filter_edited.emit(saved_filter.id)
        # For now, just emit signal

    def _on_delete(self, saved_filter: SavedFilter):
        """Handle delete button click."""
        reply = QMessageBox.question(
            self,
            "Delete Filter",
            f"Are you sure you want to delete '{saved_filter.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.filter_deleted.emit(saved_filter.id)
            # Remove from list and refresh table
            self.saved_filters = [f for f in self.saved_filters if f.id != saved_filter.id]
            self._populate_table()

    def _on_toggle_favorite(self, saved_filter: SavedFilter):
        """Handle favorite toggle."""
        self.filter_favorited.emit(saved_filter.id)
        # Toggle and refresh
        saved_filter.is_favorite = not saved_filter.is_favorite
        self._populate_table()
```

**Acceptance:**
- [ ] ManageFiltersDialog class created
- [ ] Table with 6 columns
- [ ] Displays all saved filters
- [ ] Edit button (emits signal)
- [ ] Delete button with confirmation
- [ ] Favorite toggle button (⭐/☆)
- [ ] Criteria summary displayed
- [ ] Last used date displayed

---

### Phase 6: Frontend - SearchPanelWidget Integration (Day 3 Afternoon - 2 hours) **FRONTEND DEV**

#### Task 6.1: Add Saved Filters UI to SearchPanelWidget
**Assignee:** Frontend Developer
**Estimate:** 2 hours
**Files:** `finance_app/ui/widgets/search_panel_widget.py`

**Changes:**
```python
from PySide6.QtWidgets import QComboBox, QPushButton
from PySide6.QtCore import Signal
from finance_app.ui.dialogs import SaveFilterDialog, ManageFiltersDialog

class SearchPanelWidget(QWidget):
    # Add signals
    save_filter_requested = Signal(dict)  # filter_data
    load_filter_requested = Signal(int)  # filter_id
    manage_filters_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_service = None  # Will be set by main window
        # ... existing code ...

    def _setup_filters_layout(self):
        # ... existing filter rows ...

        # Row 5: Saved Filters
        saved_label = QLabel("Saved Filters:")
        self.filters_layout.addWidget(saved_label, 5, 0)

        # Saved filters dropdown
        self.saved_filters_combo = QComboBox()
        self.saved_filters_combo.addItem("-- Select Saved Filter --")
        self.saved_filters_combo.currentIndexChanged.connect(self._on_load_saved_filter)
        self.filters_layout.addWidget(self.saved_filters_combo, 5, 1)

        # Save/Manage buttons
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.save_filters_btn = QPushButton("Save Current")
        self.save_filters_btn.clicked.connect(self._on_save_filters)
        buttons_layout.addWidget(self.save_filters_btn)

        self.manage_filters_btn = QPushButton("Manage...")
        self.manage_filters_btn.clicked.connect(self._on_manage_filters)
        buttons_layout.addWidget(self.manage_filters_btn)

        buttons_layout.addStretch()
        self.filters_layout.addWidget(buttons_container, 5, 2)

    def set_filter_service(self, service):
        """Set filter service and load saved filters."""
        self.filter_service = service
        self._refresh_saved_filters()

    def _refresh_saved_filters(self):
        """Refresh saved filters dropdown."""
        if not self.filter_service:
            return

        self.saved_filters_combo.clear()
        self.saved_filters_combo.addItem("-- Select Saved Filter --")

        saved_filters = self.filter_service.get_all_saved_filters()
        for saved_filter in saved_filters:
            display_name = f"⭐ {saved_filter.name}" if saved_filter.is_favorite else saved_filter.name
            self.saved_filters_combo.addItem(display_name, saved_filter.id)

    def _on_save_filters(self):
        """Handle Save Current Filters button."""
        # Collect current filter state
        current_filters = self._get_current_filter_state()

        if not any(current_filters.values()):
            QMessageBox.information(
                self,
                "No Filters Active",
                "There are no filters currently active to save."
            )
            return

        # Open save dialog
        dialog = SaveFilterDialog(current_filters, self)
        if dialog.exec() == QDialog.Accepted:
            filter_data = dialog.get_filter_data()
            self.save_filter_requested.emit(filter_data)

    def _on_load_saved_filter(self, index):
        """Handle saved filter selection."""
        if index == 0:
            return  # "-- Select Saved Filter --" option

        filter_id = self.saved_filters_combo.itemData(index)
        if filter_id:
            self.load_filter_requested.emit(filter_id)

    def _on_manage_filters(self):
        """Handle Manage Filters button."""
        self.manage_filters_requested.emit()

    def _get_current_filter_state(self) -> dict:
        """Collect current filter state into dict."""
        state = {}

        # Text search
        if self.text_search_widget and self.text_search_widget.has_text():
            state['text'] = self.text_search_widget.get_text()

        # Date filter
        if self.has_date_filter():
            if self.current_from_date and self.current_to_date:
                state['date_from'] = self.current_from_date.isoformat()
                state['date_to'] = self.current_to_date.isoformat()

        # Category filter
        if self.has_category_filter():
            state['categories'] = self.selected_categories

        # Amount filter
        if self.has_amount_filter():
            if self.current_min_amount:
                state['min_amount'] = str(self.current_min_amount)
            if self.current_max_amount:
                state['max_amount'] = str(self.current_max_amount)
            if self.amount_absolute:
                state['amount_absolute'] = True

        return state

    def apply_filter_state(self, filter_criteria: dict):
        """Apply saved filter state to UI."""
        # Clear all filters first
        self._on_clear_all_filters()

        # Apply text filter
        if filter_criteria.get('text'):
            self.text_search_widget.set_text(filter_criteria['text'])

        # Apply date filter
        if filter_criteria.get('date_from') and filter_criteria.get('date_to'):
            from_date = date.fromisoformat(filter_criteria['date_from'])
            to_date = date.fromisoformat(filter_criteria['date_to'])
            # Apply dates...

        # Apply category filter
        if filter_criteria.get('categories'):
            # Set category selection...
            pass

        # Apply amount filter
        if filter_criteria.get('min_amount'):
            self.amount_min.setText(filter_criteria['min_amount'])
        if filter_criteria.get('max_amount'):
            self.amount_max.setText(filter_criteria['max_amount'])
```

**Acceptance:**
- [ ] Saved filters dropdown in row 5
- [ ] "Save Current" button
- [ ] "Manage..." button
- [ ] _get_current_filter_state() collects all filter values
- [ ] apply_filter_state() applies saved filter to UI
- [ ] _refresh_saved_filters() populates dropdown
- [ ] Favorites shown with ⭐ prefix
- [ ] Signals emitted for save/load/manage

---

### Phase 7: Main Window Integration (Day 4 Morning - 1.5 hours) **FRONTEND DEV**

#### Task 7.1: Integrate FilterService in Main Window
**Assignee:** Frontend Developer
**Estimate:** 1.5 hours
**Files:** `finance_app/ui/main_window.py`

**Changes:**
```python
from finance_app.business.filter_service import FilterService
from finance_app.data.repositories.saved_filter_repository import SavedFilterRepository
from finance_app.ui.dialogs import ManageFiltersDialog

def _setup_services(self):
    # ... existing services ...

    # Create filter service
    self.saved_filter_repo = SavedFilterRepository(self.db)
    self.filter_service = FilterService(self.saved_filter_repo, self.transaction_service)

def _setup_ui(self):
    # ... existing code ...

    # Set filter service on search panel
    self.search_panel.set_filter_service(self.filter_service)

    # Connect saved filter signals
    self.search_panel.save_filter_requested.connect(self._on_save_filter)
    self.search_panel.load_filter_requested.connect(self._on_load_filter)
    self.search_panel.manage_filters_requested.connect(self._on_manage_filters)

def _on_save_filter(self, filter_data):
    """Handle save filter request."""
    try:
        saved_filter = self.filter_service.save_filter(
            name=filter_data['name'],
            filter_criteria=filter_data['criteria'],
            description=filter_data['description']
        )

        QMessageBox.information(
            self,
            "Filter Saved",
            f"Filter '{saved_filter.name}' saved successfully."
        )

        # Refresh dropdown
        self.search_panel._refresh_saved_filters()

    except ValueError as e:
        QMessageBox.warning(self, "Save Failed", str(e))

def _on_load_filter(self, filter_id):
    """Handle load filter request."""
    try:
        filter_criteria = self.filter_service.load_filter(filter_id)
        self.search_panel.apply_filter_state(filter_criteria)

        QMessageBox.information(
            self,
            "Filter Loaded",
            "Saved filter applied successfully."
        )

    except ValueError as e:
        QMessageBox.warning(self, "Load Failed", str(e))

def _on_manage_filters(self):
    """Handle manage filters request."""
    saved_filters = self.filter_service.get_all_saved_filters()

    dialog = ManageFiltersDialog(saved_filters, self)

    # Connect signals
    dialog.filter_deleted.connect(self._on_filter_deleted)
    dialog.filter_favorited.connect(self._on_filter_favorited)

    dialog.exec()

    # Refresh dropdown after managing
    self.search_panel._refresh_saved_filters()

def _on_filter_deleted(self, filter_id):
    """Handle filter deletion."""
    self.filter_service.delete_saved_filter(filter_id)

def _on_filter_favorited(self, filter_id):
    """Handle favorite toggle."""
    self.filter_service.toggle_favorite(filter_id)
```

**Acceptance:**
- [ ] FilterService instantiated in main window
- [ ] Set on search panel
- [ ] save_filter_requested signal connected
- [ ] load_filter_requested signal connected
- [ ] manage_filters_requested signal connected
- [ ] Success/error messages displayed
- [ ] Dropdown refreshed after save/delete

---

### Phase 8: Testing (Day 4 Afternoon + Day 5 Morning - 4 hours) **BACKEND DEV + FRONTEND DEV**

#### Task 8.1: Write Unit Tests for Repository/Service
**Assignee:** Backend Developer
**Estimate:** 2 hours
**Files:** `finance_app/tests/unit/test_saved_filter_repository.py` (NEW), `test_filter_service.py` (NEW)

**Tests to Write (20+ tests):**
```python
# SavedFilterRepository tests (10 tests)
def test_create_saved_filter()
def test_get_by_id()
def test_get_by_name()
def test_get_all_favorites_first()
def test_update_saved_filter()
def test_delete_saved_filter()
def test_mark_as_used()
def test_toggle_favorite()
def test_unique_name_constraint()
def test_json_roundtrip()

# FilterService tests (10 tests)
def test_apply_combined_filters_all_active()
def test_apply_combined_filters_text_only()
def test_apply_combined_filters_date_only()
def test_save_filter()
def test_save_filter_duplicate_name()
def test_load_filter()
def test_load_filter_not_found()
def test_update_saved_filter()
def test_delete_saved_filter()
def test_toggle_favorite()
```

**Acceptance:**
- [ ] 20+ unit tests for repository and service
- [ ] All CRUD operations tested
- [ ] Combined filter logic tested
- [ ] JSON serialization tested
- [ ] Error cases tested

---

#### Task 8.2: Write Integration Tests
**Assignee:** Backend Developer
**Estimate:** 1.5 hours
**Files:** `finance_app/tests/integration/test_combined_filters_integration.py` (NEW)

**Tests to Write:**
```python
def test_combined_filters_integration_all_filters()
def test_save_and_load_filter_integration()
def test_manage_filters_crud_integration()
def test_favorite_filters_sort_order()
def test_filter_persistence_across_sessions()
```

**Acceptance:**
- [ ] 5+ integration tests
- [ ] Full workflow tests
- [ ] Database persistence verified
- [ ] UI interaction tested (if applicable)

---

#### Task 8.3: Write Performance Tests
**Assignee:** Backend Developer / Tech Lead
**Estimate:** 30 minutes
**Files:** `finance_app/tests/performance/test_combined_filters_performance.py` (NEW)

**Tests to Write:**
```python
def test_combined_filters_performance_all_active():
    """Test all filters active on 10K transactions."""
    # Apply all 4 filters
    # Assert: < 300ms

def test_saved_filter_load_performance():
    """Test loading saved filter."""
    # Assert: < 50ms
```

**Acceptance:**
- [ ] Combined filter performance < 300ms for 10K transactions
- [ ] Load saved filter < 50ms

---

### Phase 9: Documentation (Day 5 Afternoon - 1 hour) **FRONTEND DEV + TECH LEAD**

#### Task 9.1: Update User Guide
**Assignee:** Frontend Developer
**Estimate:** 45 minutes
**Files:** `docs/USER_GUIDE.md`

**Section to Add:**
```markdown
## Saved Filters and Combined Searches

### Combining Multiple Filters

All filters work together using AND logic. A transaction must match ALL active filters to appear in results.

**Example: "Large Groceries Last Month"**
1. Select "Last Month" from Date filter
2. Select "Groceries" from Category filter
3. Enter "100" in Amount Min field
4. Results show: Groceries AND Last Month AND Amount >= $100

### Saving Filters

**To save current filters:**
1. Apply your desired filters
2. Click "Save Current" button
3. Enter a name (e.g., "Monthly Groceries")
4. Optionally add description
5. Click "Save"

**Filter appears in "Saved Filters" dropdown for quick access.**

### Loading Saved Filters

1. Click "Saved Filters" dropdown
2. Select your saved filter
3. All filters apply automatically
4. Favorite filters appear with ⭐

### Managing Saved Filters

Click "Manage..." to:
- View all saved filters
- Edit filter names/descriptions
- Delete unused filters
- Mark favorites (⭐) for quick access
- See when filters were last used

### Examples

**Monthly Budget Routine:**
- Save "Monthly Groceries" = Groceries + This Month
- Save "Monthly Dining" = Dining Out + This Month
- Save "Monthly Transportation" = Transportation + This Month
- Quick access to each category each month

**Expense Review:**
- Save "Large Expenses" = Amount > $500
- Save "Small Recurring" = Amount < $20
- Quick identification of unusual charges
```

**Acceptance:**
- [ ] User Guide section added
- [ ] Screenshots of save/load/manage dialogs
- [ ] Examples of combined filters
- [ ] Clear workflow instructions

---

#### Task 9.2: Update Architecture Documentation
**Assignee:** Tech Lead
**Estimate:** 15 minutes
**Files:** `docs/ARCHITECTURE.md`

**Section to Add:**
```markdown
### Filter System Architecture

**Components:**
- `FilterService`: Combined filter logic and saved filter management
- `SavedFilterRepository`: CRUD for saved filters
- `SavedFilter` model: Filter persistence
- Database table: `saved_filters` with JSON storage

**Filter Combination Logic:**
- All filters use AND logic
- Applied in sequence: text → date → category → amount
- Performance target: < 300ms for 10K transactions

**Saved Filters:**
- Stored as JSON in database
- Favorites-first sorting
- Last-used tracking
```

**Acceptance:**
- [ ] Architecture docs updated
- [ ] Component diagram (optional)
- [ ] Performance notes documented

---

### Summary: Task Assignments by Role

**Tech Lead (1 hour):**
- Task 1.1: Database migration review and creation (shared with Backend)
- Task 9.2: Architecture documentation

**Backend Developer (9-10 hours):**
- Task 1.1-1.2: Database migration + Model (1.5 hrs)
- Task 2.1: SavedFilterRepository (2.5 hrs)
- Task 3.1: FilterService (2.5 hrs)
- Task 8.1-8.3: Unit/integration/performance tests (4 hrs)

**Frontend Developer (8-9 hours):**
- Task 4.1: SaveFilterDialog (2 hrs)
- Task 5.1: ManageFiltersDialog (2.5 hrs)
- Task 6.1: SearchPanelWidget integration (2 hrs)
- Task 7.1: Main window integration (1.5 hrs)
- Task 9.1: User Guide documentation (0.75 hr)

**Tech Lead Review (1 hour):**
- Code review (all phases)
- Performance validation
- UX review

**Total Estimated Time:** 18-20 hours (matches 5 story points)

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-16 (Task Breakdown Added - Ready for Development)
**Sprint:** Sprint 15 (Week 5-6) or Sprint 16 (if Sprint 15 overloaded)
**Status:** ✅ READY FOR SPRINT 15/16 (Task breakdown complete, depends on US-012, 013, 014 completion)
