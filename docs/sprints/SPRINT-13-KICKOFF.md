# Sprint 13 Kickoff: Search & Filter Foundation

**Sprint:** Sprint 13
**Epic:** [EPIC-002: Search and Filter Transactions](../epics/EPIC-002-search-filter-transactions.md)
**Stories:**
- [US-011: Basic Text Search](../stories/backlog/US-011-basic-text-search.md)
- [US-016: Search & Filter UI Panel](../stories/backlog/US-016-search-filter-ui-panel.md)
**Duration:** 2 weeks (estimated)
**Status:** 🟢 **READY TO START**
**Created:** 2025-11-11

---

## 📊 Sprint Overview

### Sprint Goal
**Implement foundational search and filter capabilities** for transactions, enabling users to quickly find specific transactions via text search and establishing the UI framework for all future filter features.

### Sprint Deliverables
1. **Database Migration 011** - Search indexes on `transactions` table
2. **Backend (US-011):**
   - `TransactionRepository.search_by_description()` method
   - `TransactionService.search_transactions()` method
   - Unit tests (10+) + integration tests (3+)
3. **Frontend (US-011):**
   - `TransactionSearchWidget` component
   - Main window integration
   - Keyboard shortcut (Ctrl+F)
4. **Frontend (US-016):**
   - `SearchPanelWidget` component (collapsible filter panel)
   - Integration with main window
   - Active filter count and "Clear All" functionality
5. **Tests:**
   - US-011: 10+ unit, 3+ integration, 3+ performance tests
   - US-016: 5+ unit, 3+ integration tests
6. **Documentation:**
   - User Guide: "Searching Transactions" section
   - User Guide: "Using the Filter Panel" section

---

## 🎯 Story Summaries

### US-011: Basic Text Search ⭐ QUICK WIN

**User Story:**
**As a** user managing many transactions
**I want** to search transactions by description using text input
**So that** I can quickly find specific purchases like "Starbucks" or "Amazon" without scrolling

**Story Points:** 3 (4-5 hours estimated)
**Priority:** P0 (Must Have - Highest user request)

**Key Acceptance Criteria:**
- Search box in transaction panel header with placeholder "Search descriptions..."
- Case-insensitive search with live updates (300ms debounce)
- Clear "X" button to reset search
- Keyboard shortcut: Ctrl+F / Cmd+F focuses search box
- Performance: < 50ms for 1,000 transactions, < 200ms for 10,000
- "No results" message when no matches found

**Why Quick Win:**
- 80% of users requested this feature
- Fastest to implement (3 points)
- Immediate value (no dependencies)
- Low technical risk (simple SQL LIKE query)

---

### US-016: Search & Filter UI Panel 🎨 FOUNDATION

**User Story:**
**As a** user
**I want** a dedicated search/filter panel in the transaction view
**So that** I can easily access and understand all available filter options in one organized location

**Story Points:** 3 (4-5 hours estimated)
**Priority:** P0 (Must Have - Required for all filters)

**Key Acceptance Criteria:**
- Filter panel appears above transaction list with header "🔍 Search & Filters"
- Collapsible (expand/collapse button to save space)
- Contains rows for: Text search, Date filter, Category filter, Amount filter
- Active filter count indicator ("X filters active")
- "Clear All Filters" button
- Keyboard accessible (Tab navigation)
- Professional design matching app aesthetic

**Why Foundation:**
- Creates UI structure for all future filter stories
- Establishes widget pattern for US-012, 013, 014, 015
- Enables parallel development (US-011 integrates immediately)
- Ensures UX consistency across all filters

---

## ✅ Dependencies Status

### Prerequisites (All Met) ✅
- ✅ **EPIC-001:** Account Management & Double-Entry Foundation (12/12 stories complete)
- ✅ **US-001:** Account Type Taxonomy (provides transaction data model)
- ✅ **US-006:** Account Hierarchy (widget pattern reference for US-016)
- ✅ **Main Window:** Dual-pane layout with transaction list (ready for integration)

### Sprint 13 Stories Can Run in Parallel ✅
- **US-011** (Backend + basic UI) and **US-016** (Filter panel framework) have minimal dependencies
- US-011 can be developed first, then integrated into US-016's panel
- OR: US-016 can be built with placeholders, then US-011 search widget drops in

---

## 🔧 Technical Design

### Database Changes

#### Migration 011: Search Indexes

```sql
-- Enable fast text search on transaction descriptions
CREATE INDEX IF NOT EXISTS idx_transactions_description
    ON transactions(description);

-- Optional: Additional indexes for future filters
CREATE INDEX IF NOT EXISTS idx_transactions_date
    ON transactions(date);

CREATE INDEX IF NOT EXISTS idx_transactions_category
    ON transactions(category);

CREATE INDEX IF NOT EXISTS idx_transactions_amount
    ON transactions(amount);
```

**Performance Target:**
- `LIKE '%keyword%'` queries should use `idx_transactions_description`
- Expected: < 100ms for 10,000 transactions

---

### Backend Architecture (US-011)

#### Repository Layer (`transaction_repository.py`)

```python
def search_by_description(
    self,
    keyword: str,
    account_id: Optional[int] = None
) -> List[Transaction]:
    """
    Search transactions by description (case-insensitive).

    Args:
        keyword: Search term
        account_id: Optional account filter

    Returns:
        List of matching transactions, sorted by date DESC
    """
    query = """
        SELECT t.* FROM transactions t
        WHERE t.description LIKE ?
    """
    params = [f"%{keyword}%"]

    if account_id:
        query += " AND (t.from_account_id = ? OR t.to_account_id = ?)"
        params.extend([account_id, account_id])

    query += " ORDER BY t.date DESC, t.id DESC"

    cursor = self.db.execute(query, params)
    rows = cursor.fetchall()
    return [self._row_to_transaction(row) for row in rows]
```

#### Service Layer (`transaction_service.py`)

```python
def search_transactions(
    self,
    keyword: str,
    account_id: Optional[int] = None
) -> List[Transaction]:
    """Search transactions by description keyword."""
    keyword = keyword.strip()
    if not keyword:
        return []  # Empty search returns no results

    return self.transaction_repository.search_by_description(
        keyword=keyword,
        account_id=account_id
    )
```

---

### Frontend Architecture (US-011)

#### TransactionSearchWidget (`transaction_search_widget.py`)

**New file:** `finance_app/ui/widgets/transaction_search_widget.py`

```python
from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout
from PySide6.QtCore import QTimer, Signal

class TransactionSearchWidget(QWidget):
    """Search input widget for transaction list."""

    search_changed = Signal(str)  # Emitted after 300ms debounce

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._emit_search)

        # Create search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search descriptions...")
        self.search_input.setMinimumWidth(250)
        self.search_input.setMaximumWidth(300)
        self.search_input.setClearButtonEnabled(True)  # "X" button
        self.search_input.textChanged.connect(self._on_text_changed)

        # Layout
        layout = QHBoxLayout(self)
        layout.addWidget(self.search_input)
        layout.setContentsMargins(0, 0, 0, 0)

    def _on_text_changed(self, text: str):
        """Debounce search (300ms)."""
        self.search_timer.stop()
        self.search_timer.start(300)

    def _emit_search(self):
        """Emit search signal after debounce."""
        text = self.search_input.text().strip()
        self.search_changed.emit(text)
```

**Integration in `main_window.py`:**
```python
# Add search widget to transaction panel
self.transaction_search = TransactionSearchWidget()
self.transaction_search.search_changed.connect(self._on_search_changed)
transaction_header_layout.addWidget(self.transaction_search)

# Add Ctrl+F shortcut
search_action = QAction("Find Transaction", self)
search_action.setShortcut(QKeySequence.Find)
search_action.triggered.connect(self.transaction_search.set_focus)
self.addAction(search_action)
```

---

### Frontend Architecture (US-016)

#### SearchPanelWidget (`search_panel_widget.py`)

**New file:** `finance_app/ui/widgets/search_panel_widget.py`

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout
from PySide6.QtCore import Signal

class SearchPanelWidget(QWidget):
    """Filter panel container for all search/filter controls."""

    filters_cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_collapsed = False
        self.active_filter_count = 0
        self._setup_ui()

    def _setup_ui(self):
        """Setup collapsible filter panel UI."""
        # Header with collapse button
        # Filter controls grid (text, date, category, amount rows)
        # Footer with "Clear All" button and filter count
        pass

    def set_text_search_widget(self, widget):
        """Integrate US-011 search widget into filter panel."""
        self.text_search_widget = widget
        self.filters_layout.addWidget(widget, 0, 1)
        widget.search_changed.connect(self._on_filter_changed)
```

**Integration in `main_window.py`:**
```python
# Create filter panel
self.search_panel = SearchPanelWidget()
self.search_panel.filters_cleared.connect(self._on_filters_cleared)

# Integrate US-011 search widget into panel
self.transaction_search = TransactionSearchWidget()
self.search_panel.set_text_search_widget(self.transaction_search)

# Add to transaction panel layout
transaction_layout = QVBoxLayout()
transaction_layout.addWidget(self.search_panel)  # Panel at top
transaction_layout.addWidget(self.transaction_table)  # List below
```

---

## 📋 Task Breakdown

### Phase 1: Database & Backend (US-011) - 2-3 hours

**Tasks:**
1. ✅ Create Migration 011 with search indexes
2. ✅ Add `search_by_description()` to `TransactionRepository`
3. ✅ Add `search_transactions()` to `TransactionService`
4. ✅ Write 10+ unit tests (service + repository)
5. ✅ Write 3+ integration tests
6. ✅ Write 3+ performance tests (< 200ms for 10K)

---

### Phase 2: Frontend Search Widget (US-011) - 2 hours

**Tasks:**
1. ✅ Create `TransactionSearchWidget` class
2. ✅ Implement debounced search (300ms)
3. ✅ Add clear "X" button functionality
4. ✅ Integrate into main window transaction panel
5. ✅ Add Ctrl+F keyboard shortcut
6. ✅ Connect to backend search service
7. ✅ Show "No results" message when needed

---

### Phase 3: Filter Panel UI (US-016) - 2-3 hours

**Tasks:**
1. ✅ Create `SearchPanelWidget` class
2. ✅ Implement collapsible header
3. ✅ Create filter controls grid layout
4. ✅ Add placeholder rows for future filters
5. ✅ Add active filter count display
6. ✅ Add "Clear All Filters" button
7. ✅ Integrate US-011 search widget
8. ✅ Add keyboard navigation (Tab order)

---

### Phase 4: Integration & Testing - 2 hours

**Tasks:**
1. ✅ Integrate filter panel into main window
2. ✅ Test US-011 end-to-end (search workflow)
3. ✅ Test US-016 UI (collapse, clear, filter count)
4. ✅ Run all unit + integration tests
5. ✅ Performance testing with 10K+ transactions
6. ✅ Manual UI testing (keyboard nav, responsive layout)

---

### Phase 5: Documentation - 1 hour

**Tasks:**
1. ✅ Update User Guide: "Searching Transactions" section
2. ✅ Update User Guide: "Using the Filter Panel" section
3. ✅ Add screenshots of search UI
4. ✅ Document Ctrl+F shortcut
5. ✅ Update Architecture docs if needed

---

## 🧪 Testing Strategy

### US-011: Basic Text Search

**Unit Tests (10+):**
- `test_search_transactions_basic()` - Basic search functionality
- `test_search_case_insensitive()` - Case insensitivity
- `test_search_partial_match()` - Substring matching
- `test_search_empty_keyword()` - Empty keyword returns empty list
- `test_search_whitespace_keyword()` - Whitespace-only returns empty
- `test_search_no_results()` - No matches returns empty list
- `test_search_with_account_filter()` - Search within specific account
- `test_search_repository_method()` - Repository method works
- `test_search_service_method()` - Service method validates input
- `test_search_trim_whitespace()` - Leading/trailing spaces trimmed

**Integration Tests (3+):**
- `test_search_integration_end_to_end()` - Full search workflow
- `test_search_integration_with_account_filter()` - Filtered search
- `test_search_integration_sorting()` - Results sorted by date DESC

**Performance Tests (3+):**
- `test_search_performance_1000_transactions()` - < 50ms
- `test_search_performance_10000_transactions()` - < 200ms
- `test_search_index_usage()` - EXPLAIN QUERY PLAN shows index

---

### US-016: Search & Filter UI Panel

**Unit Tests (5+):**
- `test_search_panel_created()` - Panel created with correct structure
- `test_collapse_expand_toggle()` - Collapse/expand works
- `test_active_filter_count_zero()` - Count display for 0 filters
- `test_active_filter_count_multiple()` - Count display for 3 filters
- `test_clear_all_button_emits_signal()` - Clear All emits signal

**Integration Tests (3+):**
- `test_search_panel_integration_with_main_window()` - Panel in main window
- `test_search_panel_clear_all_reloads()` - Clear All reloads transactions
- `test_search_panel_keyboard_navigation()` - Tab order works

**Manual UI Tests:**
- Panel layout and styling
- Collapse/expand animations
- Keyboard navigation
- Responsive layout (narrow/wide windows)

---

## 🎯 Success Criteria

### Sprint Success = Both Stories Complete

**US-011 Complete When:**
- [ ] Search box visible in transaction panel
- [ ] Typing in search box filters transaction list
- [ ] Clear "X" button resets search
- [ ] Ctrl+F focuses search box
- [ ] Performance targets met (< 200ms for 10K)
- [ ] 10+ unit tests passing
- [ ] 3+ integration tests passing
- [ ] User Guide updated with screenshots

**US-016 Complete When:**
- [ ] Filter panel visible above transaction list
- [ ] Collapse/expand works smoothly
- [ ] Active filter count displays correctly
- [ ] "Clear All Filters" button works
- [ ] US-011 search widget integrated into panel
- [ ] 5+ unit tests passing
- [ ] 3+ integration tests passing
- [ ] User Guide updated with screenshots

**Sprint 13 Complete When:**
- [ ] Both US-011 and US-016 are complete
- [ ] All tests passing (25+ total tests)
- [ ] User Guide documentation complete
- [ ] Demo-ready for stakeholder review
- [ ] No critical or high-priority bugs

---

## 📊 Velocity Tracking

**Sprint 13 Planned Velocity:** 6 points (2 stories × 3 points each)

**Historical Velocity (EPIC-001):**
- Average: 6.08 points/sprint (over 12 sprints)
- Range: 3-8 points per sprint

**Sprint 13 Target:**
- 6 points (matches historical average) ✅
- Both stories have clear scope and acceptance criteria ✅
- Minimal dependencies (can run in parallel) ✅
- **Confidence:** HIGH - Sprint 13 is achievable

---

## ⚠️ Risks & Mitigations

### Risk 1: Performance Degradation with Large Datasets
**Impact:** High
**Probability:** Low
**Mitigation:**
- Database indexes already planned in Migration 011
- Performance tests validate < 200ms target
- If issues: Consider FTS5 (SQLite full-text search)

### Risk 2: UI/UX Complexity for Filter Panel
**Impact:** Medium
**Probability:** Low
**Mitigation:**
- US-016 has clear mockups and widget patterns
- Reference US-006 (AccountTreeWidget) for patterns
- Manual UI testing built into Definition of Done

### Risk 3: Scope Creep - Advanced Search Features
**Impact:** Medium
**Probability:** Medium
**Mitigation:**
- Stories have clear "Out of Scope" sections
- Advanced features deferred to US-012, 013, 014, 015
- Focus on "Quick Win" and "Foundation" goals only

---

## 📝 Notes

### Development Order (Recommended)

**Option A: Sequential (Backend First)**
1. Day 1-2: US-011 Backend (Migration, Repository, Service, Tests)
2. Day 3: US-011 Frontend (Search widget, integration, Ctrl+F)
3. Day 4-5: US-016 (Filter panel, integration, tests)

**Option B: Parallel (Team of 2+)**
1. Developer 1: US-011 (Backend + Frontend) - Days 1-3
2. Developer 2: US-016 (Filter panel framework) - Days 1-3
3. Day 4: Integration (US-011 widget drops into US-016 panel)
4. Day 5: Testing + Documentation

**Recommended:** Option A for single developer, Option B for team

---

### Pre-Sprint Cleanup (Optional)

Before Sprint 13 starts, consider addressing:
1. ✅ Bug #9: Remove empty View menu (5 minutes) - DONE
2. ⏳ Fix ~20 test failures in EPIC-001 tests (6-8 hours) - OPTIONAL
3. ⏳ Review and address Tech Lead Review findings

**Note:** Pre-sprint cleanup is OPTIONAL. Sprint 13 can start immediately with current codebase.

---

### Integration with Future Stories

**US-012 (Date Range Filter) will add:**
- Date dropdown widget to US-016 panel row 1
- Date filter backend methods
- Integration with US-016 filter count

**US-013 (Category Filter) will add:**
- Category dropdown widget to US-016 panel row 2
- Category filter backend methods
- Integration with US-016 filter count

**US-014, US-015 follow same pattern**
- Each story adds widgets to existing US-016 panel rows
- US-016 provides the framework, future stories just plug in

---

## 🔗 Related Documentation

- [EPIC-002: Search and Filter Transactions](../epics/EPIC-002-search-filter-transactions.md)
- [US-011: Basic Text Search](../stories/backlog/US-011-basic-text-search.md)
- [US-016: Search & Filter UI Panel](../stories/backlog/US-016-search-filter-ui-panel.md)
- [EPIC-002 Tech Lead Review](../technical-reviews/EPIC-002-TECH-LEAD-COMPREHENSIVE-REVIEW.md)
- [EPIC-002 Quality Review](../technical-reviews/EPIC-002-QUALITY-REVIEW.md)
- [EPIC_STORY_INDEX.md](../EPIC_STORY_INDEX.md)

---

**Created:** 2025-11-11
**Sprint Duration:** 2 weeks (estimated 8-10 development hours)
**Status:** 🟢 READY TO START
**Next Action:** Assign stories to developers and begin Sprint 13!
