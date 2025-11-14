# US-012: Date Range Filter 📅

**Story ID:** US-012
**Epic:** [EPIC-002: Search and Filter Transactions](../../epics/EPIC-002-search-filter-transactions.md)
**Created:** 2025-11-11
**Updated:** 2025-11-11 (Created)
**Status:** 📋 BACKLOG - Sprint 14 (Not Started)
**Priority:** P0 (Must Have - Essential for budgeting)
**Story Points:** 3 (4-5 hours estimated)
**Assignee:** Backend Dev ⏳ PENDING, Frontend Dev ⏳ PENDING, QA ⏳ PENDING
**Sprint:** Sprint 14 (Week 3-4)
**Dependencies:** ✅ US-016 (Filter UI Panel), ⏳ Database index on `date` (pre-EPIC cleanup)
**Related Stories:** US-011 (Text Search), US-013 (Category Filter), US-015 (Combined Filters)
**Progress:** Backend: 0% | Frontend: 0% | Tests: 0% | Docs: 0% | **Overall: 0%**

---

## 📖 User Story

**As a** user tracking spending over time
**I want** to filter transactions by date range (preset or custom)
**So that** I can analyze spending for specific periods like "Last Month" or "Q1 2025"

---

## 📝 Description

### Context from EPIC-002

This is the third story in EPIC-002 (Search and Filter Transactions), part of Phase 2: Core Filters (Sprint 14). This story enables users to filter transactions by date using both preset ranges (Last Month, This Quarter) and custom date ranges.

**Completed Foundation (Sprint 13):**
- ✅ US-011: Basic Text Search (text filtering operational)
- ✅ US-016: Search & Filter UI Panel (filter panel framework ready)

**Building Upon:**
- Filter panel architecture from US-016
- Search service patterns from US-011
- Date handling from EPIC-001 transaction model

### Problem Statement

Users need to analyze spending over specific time periods but currently must manually scroll and visually scan transaction dates:

- ❌ **Budget Analysis**: Cannot easily view "last month's spending" for budget review
- ❌ **Tax Preparation**: Must manually find Q1 transactions for tax filing
- ❌ **Spending Trends**: Cannot compare "this month vs last month" easily
- ❌ **Time-Specific Review**: Searching for a specific week's transactions requires scrolling
- ❌ **Report Generation**: Cannot filter to specific date ranges for reporting

**Real-World Scenarios:**
1. **Monthly Budget Review:** User wants to see all transactions from last month to compare against budget
2. **Tax Season:** User needs Q1 2025 transactions for tax preparation
3. **Vacation Analysis:** User wants to see spending during vacation week (specific custom range)
4. **Quarterly Reports:** Business user needs This Quarter transactions for quarterly review
5. **Historical Analysis:** User wants to compare This Year vs Last Year spending

**User Impact:**
- **Current state**: Manual scrolling through chronological list, visual date scanning
- **With date filter**: One-click access to any time period + custom range flexibility
- **Time savings**: ~90% reduction in time to find period-specific transactions

### Proposed Solution

Implement date range filtering with preset ranges and custom date picker:

**Core Features:**
- **Preset Ranges**: 11 common ranges (Today, Yesterday, Last 7 Days, This Month, Last Month, This/Last Quarter, This/Last Year, All Time)
- **Custom Range**: Date picker dialog for arbitrary From/To dates
- **Quick Access**: Dropdown in filter panel for easy selection
- **Database Performance**: Use indexed date queries for < 100ms filtering

**UI Design:**
```
┌─────────────────────────────────────────────────────────┐
│ Date:    [Last Month ▼]          [From] [To]            │
└─────────────────────────────────────────────────────────┘

Dropdown options:
- All Time
- Today
- Yesterday
- Last 7 Days
- Last 30 Days
- This Month
- Last Month
- This Quarter (Q4 2025)
- Last Quarter (Q3 2025)
- This Year (2025)
- Last Year (2024)
- Custom Range... → Opens date picker dialog
```

**Integration Points:**
- **US-016**: Date filter integrates into row 1 of SearchPanelWidget
- **US-015**: Date filter combines with text, category, amount filters

---

## 🎯 Acceptance Criteria

### AC1: Preset Date Ranges

**Given** I am viewing the filter panel
**When** I click the Date dropdown
**Then** I should see these preset options:
- [ ] "All Time" (no filter - default)
- [ ] "Today" (transactions from today)
- [ ] "Yesterday" (transactions from yesterday)
- [ ] "Last 7 Days" (last 7 calendar days including today)
- [ ] "Last 30 Days" (last 30 calendar days including today)
- [ ] "This Month" (first day of current month through today)
- [ ] "Last Month" (entire previous calendar month)
- [ ] "This Quarter" (first day of current quarter through today) - Q1/Q2/Q3/Q4
- [ ] "Last Quarter" (entire previous quarter)
- [ ] "This Year" (Jan 1 of current year through today)
- [ ] "Last Year" (Jan 1 through Dec 31 of previous year)
- [ ] "Custom Range..." (opens date picker dialog)

**And when** I select a preset range
**Then** the transaction list should:
- [ ] Immediately filter to show only transactions within that date range
- [ ] Update the active filter count in the filter panel footer
- [ ] Preserve other active filters (text search, category, amount)

**Example:**
```python
# Today's date: Nov 11, 2025

# "Last Month" = Oct 1, 2025 - Oct 31, 2025
# "This Quarter" = Oct 1, 2025 (Q4 start) - Nov 11, 2025 (today)
# "Last 7 Days" = Nov 5, 2025 - Nov 11, 2025
```

### AC2: Custom Date Range

**Given** I select "Custom Range..." from the Date dropdown
**When** the date picker dialog opens
**Then** I should see:
- [ ] Dialog title: "Select Date Range"
- [ ] "From Date" picker (required field)
- [ ] "To Date" picker (optional field, defaults to today if empty)
- [ ] "Apply" button to apply the filter
- [ ] "Cancel" button to close without applying

**And when** I select dates and click "Apply"
**Then** the system should:
- [ ] Validate: From Date <= To Date
- [ ] Show error if From Date > To Date
- [ ] Apply the custom date range filter
- [ ] Update dropdown to show: "Jan 1 - Mar 31" (selected range)
- [ ] Close the dialog

**Example:**
```
┌──────────────────────────────────┐
│ Select Date Range           [X]  │
├──────────────────────────────────┤
│ From: [📅 Jan 1, 2025     ]     │
│ To:   [📅 Mar 31, 2025    ]     │
│                                  │
│           [Cancel] [Apply]       │
└──────────────────────────────────┘
```

### AC3: Quarter Calculation

**Given** today's date falls within a specific quarter
**When** I select "This Quarter" or "Last Quarter"
**Then** the system should calculate quarters correctly:
- [ ] Q1 = January 1 - March 31
- [ ] Q2 = April 1 - June 30
- [ ] Q3 = July 1 - September 30
- [ ] Q4 = October 1 - December 31

**Test Cases:**
```python
# Today: Feb 15, 2025
assert "This Quarter" == (date(2025, 1, 1), date(2025, 2, 15))  # Q1
assert "Last Quarter" == (date(2024, 10, 1), date(2024, 12, 31))  # Q4 2024

# Today: Nov 11, 2025
assert "This Quarter" == (date(2025, 10, 1), date(2025, 11, 11))  # Q4
assert "Last Quarter" == (date(2025, 7, 1), date(2025, 9, 30))  # Q3
```

### AC4: Performance Requirements

**Given** I have 10,000 transactions in the database
**When** I apply any date filter
**Then** the system should:
- [ ] Complete filtering in < 100ms (target performance)
- [ ] Use database index on `date` column
- [ ] Show results sorted by date DESC (newest first)

**Performance Test:**
```python
def test_date_filter_performance_10k():
    # Setup: Create 10,000 test transactions
    start = time.time()
    results = transaction_service.filter_by_date_range(
        from_date=date(2025, 1, 1),
        to_date=date(2025, 12, 31)
    )
    duration = (time.time() - start) * 1000  # ms
    assert duration < 100, f"Filter took {duration}ms, expected < 100ms"
```

### AC5: Filter Combination

**Given** I have other filters active (text search, category)
**When** I apply a date filter
**Then** the system should:
- [ ] Combine date filter with existing filters using AND logic
- [ ] Example: "Groceries" AND "Last Month" shows only grocery transactions from last month
- [ ] Update active filter count (if date filter is new, count increases)
- [ ] Preserve existing filter state when date filter changes

---

## 🔧 Technical Implementation

### Backend Implementation

#### 1. Date Range Calculation Utility

**New file:** `finance_app/business/date_utils.py`

```python
from datetime import date, timedelta
from typing import Tuple

class DateRange:
    """Date range calculation utilities."""

    @staticmethod
    def get_today() -> Tuple[date, date]:
        """Return today's date range."""
        today = date.today()
        return (today, today)

    @staticmethod
    def get_yesterday() -> Tuple[date, date]:
        """Return yesterday's date range."""
        yesterday = date.today() - timedelta(days=1)
        return (yesterday, yesterday)

    @staticmethod
    def get_last_n_days(n: int) -> Tuple[date, date]:
        """Return last N days including today."""
        today = date.today()
        start = today - timedelta(days=n-1)
        return (start, today)

    @staticmethod
    def get_this_month() -> Tuple[date, date]:
        """Return current month from day 1 to today."""
        today = date.today()
        start = date(today.year, today.month, 1)
        return (start, today)

    @staticmethod
    def get_last_month() -> Tuple[date, date]:
        """Return entire previous calendar month."""
        today = date.today()
        # Last day of previous month
        last_day_prev_month = date(today.year, today.month, 1) - timedelta(days=1)
        # First day of previous month
        first_day_prev_month = date(last_day_prev_month.year, last_day_prev_month.month, 1)
        return (first_day_prev_month, last_day_prev_month)

    @staticmethod
    def get_quarter(year: int, quarter: int) -> Tuple[date, date]:
        """Return date range for given quarter (1-4)."""
        quarter_starts = {
            1: (year, 1, 1),
            2: (year, 4, 1),
            3: (year, 7, 1),
            4: (year, 10, 1)
        }
        quarter_ends = {
            1: (year, 3, 31),
            2: (year, 6, 30),
            3: (year, 9, 30),
            4: (year, 12, 31)
        }
        start = date(*quarter_starts[quarter])
        end = date(*quarter_ends[quarter])
        return (start, end)

    @staticmethod
    def get_this_quarter() -> Tuple[date, date]:
        """Return current quarter from quarter start to today."""
        today = date.today()
        quarter = (today.month - 1) // 3 + 1
        start_date, _ = DateRange.get_quarter(today.year, quarter)
        return (start_date, today)

    @staticmethod
    def get_last_quarter() -> Tuple[date, date]:
        """Return entire previous quarter."""
        today = date.today()
        current_quarter = (today.month - 1) // 3 + 1

        if current_quarter == 1:
            # Last quarter is Q4 of previous year
            return DateRange.get_quarter(today.year - 1, 4)
        else:
            return DateRange.get_quarter(today.year, current_quarter - 1)
```

#### 2. Repository Layer

Update `transaction_repository.py`:

```python
def filter_by_date_range(
    self,
    from_date: date,
    to_date: date,
    account_id: Optional[int] = None
) -> List[Transaction]:
    """
    Filter transactions by date range.

    Args:
        from_date: Start date (inclusive)
        to_date: End date (inclusive)
        account_id: Optional account filter

    Returns:
        List of transactions within date range, sorted by date DESC
    """
    query = """
        SELECT t.* FROM transactions t
        WHERE t.date BETWEEN ? AND ?
    """
    params = [from_date.isoformat(), to_date.isoformat()]

    if account_id:
        query += " AND (t.from_account_id = ? OR t.to_account_id = ?)"
        params.extend([account_id, account_id])

    query += " ORDER BY t.date DESC, t.id DESC"

    cursor = self.db.execute(query, params)
    rows = cursor.fetchall()
    return [self._row_to_transaction(row) for row in rows]
```

#### 3. Service Layer

Update `transaction_service.py`:

```python
from finance_app.business.date_utils import DateRange

def filter_by_date_range(
    self,
    from_date: date,
    to_date: date,
    account_id: Optional[int] = None
) -> List[Transaction]:
    """Filter transactions by date range."""
    # Validate date range
    if from_date > to_date:
        raise ValueError(f"From date ({from_date}) must be <= To date ({to_date})")

    return self.transaction_repository.filter_by_date_range(
        from_date=from_date,
        to_date=to_date,
        account_id=account_id
    )

def filter_by_preset(
    self,
    preset: str,
    account_id: Optional[int] = None
) -> List[Transaction]:
    """Filter by preset date range (e.g., 'last_month', 'this_quarter')."""
    preset_map = {
        'today': DateRange.get_today,
        'yesterday': DateRange.get_yesterday,
        'last_7_days': lambda: DateRange.get_last_n_days(7),
        'last_30_days': lambda: DateRange.get_last_n_days(30),
        'this_month': DateRange.get_this_month,
        'last_month': DateRange.get_last_month,
        'this_quarter': DateRange.get_this_quarter,
        'last_quarter': DateRange.get_last_quarter,
        'this_year': lambda: (date(date.today().year, 1, 1), date.today()),
        'last_year': lambda: (date(date.today().year - 1, 1, 1), date(date.today().year - 1, 12, 31)),
    }

    if preset not in preset_map:
        raise ValueError(f"Unknown preset: {preset}")

    from_date, to_date = preset_map[preset]()
    return self.filter_by_date_range(from_date, to_date, account_id)
```

### Frontend Implementation

#### 1. Date Filter Widget

Update `SearchPanelWidget` in `search_panel_widget.py`:

```python
from PySide6.QtWidgets import QComboBox, QPushButton, QDialog, QDateEdit

class SearchPanelWidget(QWidget):
    date_filter_changed = Signal(object, object)  # from_date, to_date

    def _setup_date_filter(self):
        """Setup date filter dropdown (US-012)."""
        self.date_combo = QComboBox()
        self.date_combo.addItems([
            "All Time",
            "Today",
            "Yesterday",
            "Last 7 Days",
            "Last 30 Days",
            "This Month",
            "Last Month",
            f"This Quarter (Q{self._get_current_quarter()})",
            "Last Quarter",
            f"This Year ({date.today().year})",
            f"Last Year ({date.today().year - 1})",
            "Custom Range..."
        ])
        self.date_combo.currentTextChanged.connect(self._on_date_preset_changed)
        self.filters_layout.addWidget(self.date_combo, 1, 1)

    def _on_date_preset_changed(self, text: str):
        """Handle date preset selection."""
        if text == "Custom Range...":
            self._show_custom_date_dialog()
        elif text == "All Time":
            self.date_filter_changed.emit(None, None)  # Clear filter
        else:
            # Map preset to date range and emit signal
            from_date, to_date = self._get_preset_range(text)
            self.date_filter_changed.emit(from_date, to_date)

    def _show_custom_date_dialog(self):
        """Show custom date range picker dialog."""
        dialog = DateRangeDialog(self)
        if dialog.exec() == QDialog.Accepted:
            from_date, to_date = dialog.get_date_range()
            self.date_filter_changed.emit(from_date, to_date)
            # Update combo text to show selected range
            self.date_combo.setItemText(
                self.date_combo.currentIndex(),
                f"{from_date.strftime('%b %d')} - {to_date.strftime('%b %d')}"
            )
```

#### 2. Custom Date Range Dialog

**New file:** `finance_app/ui/dialogs/date_range_dialog.py`

```python
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDateEdit, QPushButton, QLabel
from PySide6.QtCore import QDate
from datetime import date

class DateRangeDialog(QDialog):
    """Custom date range picker dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date Range")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # From date picker
        layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate())
        self.from_date.setCalendarPopup(True)
        layout.addWidget(self.from_date)

        # To date picker
        layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        layout.addWidget(self.to_date)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._validate_and_accept)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(apply_btn)
        layout.addLayout(button_layout)

    def _validate_and_accept(self):
        """Validate date range and accept dialog."""
        from_date = self.from_date.date().toPython()
        to_date = self.to_date.date().toPython()

        if from_date > to_date:
            QMessageBox.warning(
                self,
                "Invalid Date Range",
                "From date must be before or equal to To date."
            )
            return

        self.accept()

    def get_date_range(self) -> tuple[date, date]:
        """Return selected date range."""
        return (
            self.from_date.date().toPython(),
            self.to_date.date().toPython()
        )
```

### Database Changes

**Pre-EPIC Cleanup (Migration 011):**
```sql
-- Create index for date range filtering
CREATE INDEX IF NOT EXISTS idx_transactions_date
    ON transactions(date);

-- Verify index effectiveness:
-- EXPLAIN QUERY PLAN
-- SELECT * FROM transactions WHERE date BETWEEN '2025-01-01' AND '2025-12-31';
-- Should show: USING INDEX idx_transactions_date
```

---

## 🧪 Testing Requirements

### Unit Tests (8+ tests)

```python
def test_date_range_today():
    """Test today's date range."""
    from_date, to_date = DateRange.get_today()
    assert from_date == date.today()
    assert to_date == date.today()

def test_date_range_last_month():
    """Test last month calculation."""
    from_date, to_date = DateRange.get_last_month()
    assert from_date.day == 1
    assert to_date == date(from_date.year, from_date.month, monthrange(from_date.year, from_date.month)[1])

def test_date_range_this_quarter():
    """Test current quarter calculation."""
    from_date, to_date = DateRange.get_this_quarter()
    assert to_date == date.today()
    # Verify quarter start
    quarter = (from_date.month - 1) // 3 + 1
    expected_start_month = (quarter - 1) * 3 + 1
    assert from_date.month == expected_start_month

def test_filter_by_date_range():
    """Test date range filtering."""
    results = service.filter_by_date_range(
        from_date=date(2025, 1, 1),
        to_date=date(2025, 1, 31)
    )
    for txn in results:
        assert date(2025, 1, 1) <= txn.date <= date(2025, 1, 31)

def test_filter_invalid_range():
    """Test validation for invalid date range."""
    with pytest.raises(ValueError):
        service.filter_by_date_range(
            from_date=date(2025, 12, 31),
            to_date=date(2025, 1, 1)
        )
```

### Integration Tests (3+ tests)

```python
def test_date_filter_integration():
    """Test end-to-end date filtering."""
    # Setup: Create transactions across multiple months
    # Test: Filter by "Last Month"
    # Assert: Only last month's transactions returned

def test_date_filter_with_account():
    """Test date filter combined with account filter."""
    # Test filtering specific account within date range

def test_custom_date_range_integration():
    """Test custom date range selection."""
    # Test arbitrary date range filtering
```

### Performance Tests (1 test)

```python
def test_date_filter_performance():
    """Test date filter performance with 10K transactions."""
    # Setup: Create 10,000 transactions across 2 years
    start = time.time()
    results = service.filter_by_date_range(
        from_date=date(2025, 1, 1),
        to_date=date(2025, 12, 31)
    )
    duration = (time.time() - start) * 1000
    assert duration < 100, f"Filter took {duration}ms, expected < 100ms"
```

---

## 📋 Definition of Done

### Code Complete
- [ ] `DateRange` utility class implemented
- [ ] Repository `filter_by_date_range()` method
- [ ] Service `filter_by_date_range()` and `filter_by_preset()` methods
- [ ] Date filter dropdown in SearchPanelWidget
- [ ] Custom date range dialog implemented
- [ ] Database index on `date` column created
- [ ] Code reviewed and approved

### Testing Complete
- [ ] 8+ unit tests passing (date calculations + filtering)
- [ ] 3+ integration tests passing
- [ ] 1 performance test passing (< 100ms for 10K)
- [ ] Manual UI testing (dropdowns, dialog, date picker)
- [ ] All existing tests still passing

### Documentation
- [ ] User Guide: "Filtering by Date Range" section
- [ ] Screenshot of date dropdown with presets
- [ ] Screenshot of custom date range dialog
- [ ] Code docstrings complete
- [ ] Quarter calculation documented

### Demo Ready
- [ ] Can demonstrate preset ranges (Last Month, This Quarter)
- [ ] Can demonstrate custom date picker
- [ ] Performance is responsive (< 100ms)
- [ ] Filter combines with US-011 text search

---

## 📊 Success Metrics

**Development:** 3 points (4-5 hours)
**User Adoption:** 70% of users use date filter within first month
**Performance:** < 100ms for 10,000 transactions

---

## 🔗 Related Documentation

- [EPIC-002: Search and Filter Transactions](../../epics/EPIC-002-search-filter-transactions.md)
- [US-011: Basic Text Search](./US-011-basic-text-search.md)
- [US-016: Search & Filter UI Panel](./US-016-search-filter-ui-panel.md)
- [US-013: Category Filter](./US-013-category-filter.md)

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Sprint:** Sprint 14 (Week 3-4)
**Status:** 📋 BACKLOG
