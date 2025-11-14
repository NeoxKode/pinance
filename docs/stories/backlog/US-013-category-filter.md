# US-013: Category Filter 🏷️

**Story ID:** US-013
**Epic:** [EPIC-002: Search and Filter Transactions](../../epics/EPIC-002-search-filter-transactions.md)
**Created:** 2025-11-11
**Status:** 📋 BACKLOG - Sprint 14 (Not Started)
**Priority:** P1 (Should Have - Core budgeting feature)
**Story Points:** 3 (4-5 hours estimated)
**Sprint:** Sprint 14 (Week 3-4)
**Dependencies:** ✅ US-016 (Filter UI Panel), ✅ Categories in transactions (EPIC-001)
**Related Stories:** US-011 (Text Search), US-012 (Date Filter), US-015 (Combined Filters)

---

## 📖 User Story

**As a** budget-conscious user
**I want** to filter transactions by category
**So that** I can see all expenses in categories like "Groceries" or "Entertainment"

---

## 📝 Description

This story enables category-based filtering for budget tracking and expense analysis. Users can select one or multiple categories to view related transactions.

**Problem:** Cannot analyze spending by category without manual scanning
**Solution:** Category dropdown filter with multi-select support

**Use Cases:**
1. Budget Review: "Show all Groceries spending this month"
2. Category Comparison: "Entertainment vs Dining Out"
3. Expense Analysis: "All Transportation costs"

---

## 🎯 Acceptance Criteria

### AC1: Category Dropdown
- [ ] Dropdown populated with all distinct categories from transactions
- [ ] "All Categories" option (clears filter)
- [ ] Categories sorted alphabetically
- [ ] Shows transaction count: "Groceries (45)"
- [ ] Selecting category immediately filters

### AC2: Multi-Select (Optional)
- [ ] Can select multiple categories (Ctrl+Click or checkboxes)
- [ ] Shows: "2 categories selected"
- [ ] Example: "Groceries + Dining Out" combined

### AC3: Performance
- [ ] < 100ms filter time for 10,000 transactions
- [ ] Uses database index on `category` column

---

## 🔧 Technical Implementation

### Backend

```python
# transaction_repository.py
def filter_by_categories(
    self,
    categories: List[str],
    account_id: Optional[int] = None
) -> List[Transaction]:
    """Filter by category list."""
    placeholders = ','.join('?' * len(categories))
    query = f"""
        SELECT t.* FROM transactions t
        WHERE t.category IN ({placeholders})
    """
    params = categories

    if account_id:
        query += " AND (t.from_account_id = ? OR t.to_account_id = ?)"
        params.extend([account_id, account_id])

    query += " ORDER BY t.date DESC"
    # Execute query...

def get_categories_with_counts(self) -> List[Tuple[str, int]]:
    """Get distinct categories with transaction counts."""
    query = """
        SELECT category, COUNT(*) as count
        FROM transactions
        GROUP BY category
        ORDER BY category ASC
    """
    # Execute and return...
```

### Frontend

```python
# search_panel_widget.py
def _setup_category_filter(self):
    """Setup category filter dropdown."""
    self.category_combo = QComboBox()
    self.category_combo.addItem("All Categories")

    # Populate with categories from database
    categories = self.transaction_service.get_categories_with_counts()
    for category, count in categories:
        self.category_combo.addItem(f"{category} ({count})")

    self.category_combo.currentTextChanged.connect(self._on_category_changed)
```

### Database

```sql
-- Pre-EPIC Cleanup (Migration 011)
CREATE INDEX IF NOT EXISTS idx_transactions_category
    ON transactions(category);
```

---

## 🧪 Testing

**Unit Tests (8+):**
- Category filtering logic
- Multi-select functionality
- Category list retrieval
- Count calculation

**Integration Tests (3+):**
- End-to-end category filtering
- Category + date filter combination
- Multi-category selection

---

## 📋 Definition of Done

- [ ] Category dropdown working
- [ ] Multi-select implemented (if time permits)
- [ ] Database index on `category`
- [ ] 8+ unit tests passing
- [ ] 3+ integration tests passing
- [ ] Performance < 100ms for 10K transactions
- [ ] User Guide updated

---

**Created:** 2025-11-11
**Sprint:** Sprint 14 (Week 3-4)
**Status:** 📋 BACKLOG
