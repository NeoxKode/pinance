# US-014: Amount Range Filter 💰

**Story ID:** US-014
**Epic:** [EPIC-002: Search and Filter Transactions](../../epics/EPIC-002-search-filter-transactions.md)
**Created:** 2025-11-11
**Status:** 📋 BACKLOG - Sprint 15 (Not Started)
**Priority:** P2 (Could Have - Nice to have for analysis)
**Story Points:** 4 (5-7 hours estimated)
**Sprint:** Sprint 15 (Week 5-6)
**Dependencies:** ✅ US-016 (Filter UI Panel)
**Related Stories:** US-011, US-012, US-013 (Other filters), US-015 (Combined Filters)

---

## 📖 User Story

**As a** user
**I want** to filter transactions by amount range
**So that** I can find large expenses (> $100) or small recurring charges (< $20)

---

## 📝 Description

Enables amount-based filtering for finding large purchases, subscription hunting, and expense analysis.

**Problem:** Cannot quickly find transactions by monetary value
**Solution:** Min/Max amount inputs with optional preset ranges

**Use Cases:**
1. Large Purchases: "Show transactions > $500"
2. Subscription Hunting: "Find small charges < $20"
3. Budget Analysis: "Purchases $50-$100"

---

## 🎯 Acceptance Criteria

### AC1: Amount Input Fields
- [ ] Min amount input (optional)
- [ ] Max amount input (optional)
- [ ] Accepts decimals: 19.99, 100.00
- [ ] Currency symbol ($) shown but not required
- [ ] Either min OR max OR both can be provided
- [ ] Validates: Min <= Max if both provided

### AC2: Filter Logic
- [ ] Min only: Shows transactions >= min
- [ ] Max only: Shows transactions <= max
- [ ] Both: Shows between min and max (inclusive)
- [ ] Handles positive and negative amounts
- [ ] Absolute value option: "Amounts $100+ (ignore +/-)"

### AC3: Preset Ranges (Nice to Have)
- [ ] Quick buttons:
  - "Small (< $20)"
  - "Medium ($20-$100)"
  - "Large (> $100)"
  - "Very Large (> $500)"

### AC4: Performance
- [ ] < 100ms filter time for 10,000 transactions
- [ ] Uses database index on `amount` column

---

## 🔧 Technical Implementation

### Backend

```python
# transaction_repository.py
def filter_by_amount_range(
    self,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    absolute: bool = False,
    account_id: Optional[int] = None
) -> List[Transaction]:
    """Filter by amount range."""
    conditions = []
    params = []

    if absolute:
        # Use absolute values
        if min_amount is not None:
            conditions.append("ABS(t.amount) >= ?")
            params.append(min_amount)
        if max_amount is not None:
            conditions.append("ABS(t.amount) <= ?")
            params.append(max_amount)
    else:
        # Use actual amounts (positive/negative)
        if min_amount is not None:
            conditions.append("t.amount >= ?")
            params.append(min_amount)
        if max_amount is not None:
            conditions.append("t.amount <= ?")
            params.append(max_amount)

    query = f"""
        SELECT t.* FROM transactions t
        WHERE {' AND '.join(conditions)}
    """
    # Add account filter if needed, execute...
```

### Frontend

```python
# search_panel_widget.py
def _setup_amount_filter(self):
    """Setup amount range inputs."""
    self.amount_min = QLineEdit()
    self.amount_min.setPlaceholderText("Min $")
    self.amount_min.textChanged.connect(self._on_amount_changed)

    self.amount_max = QLineEdit()
    self.amount_max.setPlaceholderText("Max $")
    self.amount_max.textChanged.connect(self._on_amount_changed)

    # Add preset buttons (optional)
    self.amount_presets = QWidget()
    preset_layout = QHBoxLayout(self.amount_presets)
    for label, min_val, max_val in [
        ("< $20", None, 20),
        ("$20-$100", 20, 100),
        ("> $100", 100, None),
        ("> $500", 500, None)
    ]:
        btn = QPushButton(label)
        btn.clicked.connect(lambda checked, mn=min_val, mx=max_val: self._apply_amount_preset(mn, mx))
        preset_layout.addWidget(btn)
```

### Database

```sql
-- Pre-EPIC Cleanup (Migration 011)
CREATE INDEX IF NOT EXISTS idx_transactions_amount
    ON transactions(amount);
```

---

## 🧪 Testing

**Unit Tests (10+):**
- Min only filtering
- Max only filtering
- Both min and max
- Absolute value mode
- Decimal handling
- Validation logic

**Integration Tests (4+):**
- End-to-end amount filtering
- Combined with other filters
- Preset button functionality
- Edge cases (negative amounts, zero)

---

## 📋 Task Breakdown for Development

This section provides a detailed, step-by-step implementation plan for developers.

### Phase 1: Database Preparation (Pre-Sprint - 5 minutes) ⚡ **TECH LEAD**

#### Task 1.1: Create Database Index on `amount` Column
**Assignee:** Tech Lead
**Estimate:** 5 minutes
**Files:** Direct SQL execution or migration script

**SQL:**
```sql
-- Run before Sprint 15 starts
CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount);

-- Verify index created
PRAGMA index_list('transactions');

-- Test query plan
EXPLAIN QUERY PLAN
SELECT * FROM transactions WHERE amount BETWEEN 50.00 AND 100.00;
-- Should show: SEARCH transactions USING INDEX idx_transactions_amount
```

**Acceptance:**
- [ ] Index `idx_transactions_amount` created
- [ ] PRAGMA shows index in list
- [ ] EXPLAIN QUERY PLAN confirms index usage for range queries
- [ ] Index creation time < 1 second for 10K+ transactions

**Testing:**
```python
def test_amount_index_exists():
    """Verify amount index exists."""
    cursor = db.execute("PRAGMA index_list('transactions')")
    indices = [row[1] for row in cursor.fetchall()]
    assert "idx_transactions_amount" in indices
```

---

### Phase 2: Backend - Repository Layer (Day 1 Morning - 2 hours) **BACKEND DEV**

#### Task 2.1: Add Amount Filtering Method to Repository
**Assignee:** Backend Developer
**Estimate:** 2 hours
**Files:** `finance_app/data/repositories/transaction_repository.py`

**New Method:**
```python
from decimal import Decimal

def filter_by_amount_range(
    self,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    absolute: bool = False,
    account_id: Optional[int] = None
) -> List[Transaction]:
    """
    Filter transactions by amount range.

    Args:
        min_amount: Minimum amount (inclusive), None = no lower bound
        max_amount: Maximum amount (inclusive), None = no upper bound
        absolute: If True, use absolute values (ignore sign)
        account_id: Optional account filter

    Returns:
        List of transactions within amount range, sorted by date DESC

    Examples:
        # Large purchases
        filter_by_amount_range(min_amount=Decimal("100"))

        # Small charges
        filter_by_amount_range(max_amount=Decimal("20"))

        # Mid-range
        filter_by_amount_range(min_amount=Decimal("20"), max_amount=Decimal("100"))

        # Absolute value (expenses OR income >= 100)
        filter_by_amount_range(min_amount=Decimal("100"), absolute=True)

    Performance:
        Uses idx_transactions_amount index for < 100ms with 10K transactions
    """
    if min_amount is None and max_amount is None:
        return []  # No range specified = no results

    conditions = []
    params = []

    if absolute:
        # Use absolute values (ignore sign)
        if min_amount is not None:
            conditions.append("ABS(t.amount) >= ?")
            params.append(float(min_amount))
        if max_amount is not None:
            conditions.append("ABS(t.amount) <= ?")
            params.append(float(max_amount))
    else:
        # Use actual amounts (preserves positive/negative)
        if min_amount is not None:
            conditions.append("t.amount >= ?")
            params.append(float(min_amount))
        if max_amount is not None:
            conditions.append("t.amount <= ?")
            params.append(float(max_amount))

    query = f"""
        SELECT t.* FROM transactions t
        WHERE {' AND '.join(conditions)}
    """

    if account_id:
        query += " AND (t.from_account_id = ? OR t.to_account_id = ?)"
        params.extend([account_id, account_id])

    query += " ORDER BY t.date DESC, t.id DESC"

    cursor = self.db.execute(query, params)
    rows = cursor.fetchall()
    return [self._row_to_transaction(row) for row in rows]
```

**Acceptance:**
- [ ] `filter_by_amount_range()` method added
- [ ] Supports min only, max only, or both
- [ ] Supports absolute value mode
- [ ] Account filter support (optional)
- [ ] Results sorted by date DESC
- [ ] Handles Decimal type correctly
- [ ] Uses database index (verified with EXPLAIN QUERY PLAN)
- [ ] Returns empty list if no range specified

**Testing:**
```python
def test_filter_by_amount_min_only(transaction_repo):
    """Test filtering with minimum amount only."""
    results = transaction_repo.filter_by_amount_range(min_amount=Decimal("100"))

    # Verify all results >= 100
    for txn in results:
        assert txn.amount >= Decimal("100")

def test_filter_by_amount_max_only(transaction_repo):
    """Test filtering with maximum amount only."""
    results = transaction_repo.filter_by_amount_range(max_amount=Decimal("20"))

    # Verify all results <= 20
    for txn in results:
        assert txn.amount <= Decimal("20")

def test_filter_by_amount_range_both(transaction_repo):
    """Test filtering with both min and max."""
    results = transaction_repo.filter_by_amount_range(
        min_amount=Decimal("20"),
        max_amount=Decimal("100")
    )

    # Verify all results in range
    for txn in results:
        assert Decimal("20") <= txn.amount <= Decimal("100")

def test_filter_by_amount_absolute_mode(transaction_repo):
    """Test absolute value filtering."""
    results = transaction_repo.filter_by_amount_range(
        min_amount=Decimal("100"),
        absolute=True
    )

    # Verify all results have absolute value >= 100
    for txn in results:
        assert abs(txn.amount) >= Decimal("100")
```

---

### Phase 3: Backend - Service Layer (Day 1 Afternoon - 1.5 hours) **BACKEND DEV**

#### Task 3.1: Add Amount Filtering to Transaction Service
**Assignee:** Backend Developer
**Estimate:** 1.5 hours
**Files:** `finance_app/business/transaction_service.py`

**New Method:**
```python
from decimal import Decimal, InvalidOperation

def filter_by_amount_range(
    self,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    absolute: bool = False,
    account_id: Optional[int] = None
) -> List[Transaction]:
    """
    Filter transactions by amount range with validation.

    Args:
        min_amount: Minimum amount (inclusive)
        max_amount: Maximum amount (inclusive)
        absolute: Use absolute values
        account_id: Optional account filter

    Returns:
        List of matching transactions

    Raises:
        ValueError: If validation fails (min > max, invalid amounts)
    """
    # Validate inputs
    if min_amount is not None and max_amount is not None:
        if min_amount > max_amount:
            raise ValueError(
                f"Min amount ({min_amount}) must be <= Max amount ({max_amount})"
            )

    # Validate at least one bound specified
    if min_amount is None and max_amount is None:
        return []  # No criteria = no results

    # Validate types
    if min_amount is not None and not isinstance(min_amount, Decimal):
        raise ValueError(f"min_amount must be Decimal, got {type(min_amount)}")

    if max_amount is not None and not isinstance(max_amount, Decimal):
        raise ValueError(f"max_amount must be Decimal, got {type(max_amount)}")

    return self.transaction_repository.filter_by_amount_range(
        min_amount=min_amount,
        max_amount=max_amount,
        absolute=absolute,
        account_id=account_id
    )

def parse_amount_string(self, amount_str: str) -> Optional[Decimal]:
    """
    Parse amount string to Decimal, handling currency symbols.

    Args:
        amount_str: Amount string (e.g., "$100", "50.99", "20")

    Returns:
        Decimal value or None if invalid

    Examples:
        "$100" -> Decimal("100")
        "50.99" -> Decimal("50.99")
        "invalid" -> None
    """
    if not amount_str or not amount_str.strip():
        return None

    # Remove common currency symbols and whitespace
    cleaned = amount_str.strip().replace('$', '').replace(',', '')

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None
```

**Acceptance:**
- [ ] `filter_by_amount_range()` method added with validation
- [ ] Validates min <= max
- [ ] Validates Decimal types
- [ ] Returns empty list if no criteria
- [ ] `parse_amount_string()` helper method added
- [ ] Handles currency symbols ($, commas)
- [ ] Type hints complete
- [ ] Docstrings complete

**Testing:**
```python
def test_filter_by_amount_validation_min_max(transaction_service):
    """Test validates min <= max."""
    with pytest.raises(ValueError, match="must be <="):
        transaction_service.filter_by_amount_range(
            min_amount=Decimal("100"),
            max_amount=Decimal("50")
        )

def test_filter_by_amount_no_criteria(transaction_service):
    """Test returns empty when no criteria."""
    results = transaction_service.filter_by_amount_range()
    assert results == []

def test_parse_amount_string_valid(transaction_service):
    """Test parsing valid amount strings."""
    assert transaction_service.parse_amount_string("$100") == Decimal("100")
    assert transaction_service.parse_amount_string("50.99") == Decimal("50.99")
    assert transaction_service.parse_amount_string("1,234.56") == Decimal("1234.56")

def test_parse_amount_string_invalid(transaction_service):
    """Test parsing invalid strings."""
    assert transaction_service.parse_amount_string("invalid") is None
    assert transaction_service.parse_amount_string("") is None
```

---

### Phase 4: Frontend - Amount Input Widget (Day 2 Morning - 2.5 hours) **FRONTEND DEV**

#### Task 4.1: Add Amount Filter Inputs to SearchPanelWidget
**Assignee:** Frontend Developer
**Estimate:** 2.5 hours
**Files:** `finance_app/ui/widgets/search_panel_widget.py`

**Changes:**
```python
from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QPushButton, QCheckBox
from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QDoubleValidator
from decimal import Decimal

class SearchPanelWidget(QWidget):
    # Add signal
    amount_filter_changed = Signal(object, object, bool)  # min, max, absolute

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_min_amount = None
        self.current_max_amount = None
        self.amount_absolute = False
        self.amount_timer = QTimer()
        self.amount_timer.setSingleShot(True)
        self.amount_timer.timeout.connect(self._emit_amount_filter)
        # ... existing code ...

    def _setup_filters_layout(self):
        # ... existing code ...

        # Row 3: Amount filter (replace placeholder)
        self.amount_label = QLabel("Amount:")
        self.filters_layout.addWidget(self.amount_label, 3, 0)

        # Amount inputs container
        amount_container = QWidget()
        amount_layout = QHBoxLayout(amount_container)
        amount_layout.setContentsMargins(0, 0, 0, 0)

        # Min amount input
        self.amount_min = QLineEdit()
        self.amount_min.setPlaceholderText("Min $")
        self.amount_min.setMaximumWidth(80)
        self.amount_min.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        self.amount_min.textChanged.connect(self._on_amount_input_changed)
        amount_layout.addWidget(self.amount_min)

        # Dash separator
        amount_layout.addWidget(QLabel("-"))

        # Max amount input
        self.amount_max = QLineEdit()
        self.amount_max.setPlaceholderText("Max $")
        self.amount_max.setMaximumWidth(80)
        self.amount_max.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        self.amount_max.textChanged.connect(self._on_amount_input_changed)
        amount_layout.addWidget(self.amount_max)

        # Absolute value checkbox
        self.amount_absolute_check = QCheckBox("Absolute")
        self.amount_absolute_check.setToolTip("Ignore +/- signs (use absolute values)")
        self.amount_absolute_check.stateChanged.connect(self._on_amount_input_changed)
        amount_layout.addWidget(self.amount_absolute_check)

        amount_layout.addStretch()

        self.filters_layout.addWidget(amount_container, 3, 1, 1, 2)

        # Row 4: Amount presets (optional quick filters)
        preset_container = QWidget()
        preset_layout = QHBoxLayout(preset_container)
        preset_layout.setContentsMargins(20, 0, 0, 0)

        preset_buttons = [
            ("< $20", None, "20"),
            ("$20-$100", "20", "100"),
            ("> $100", "100", None),
            ("> $500", "500", None),
        ]

        for label, min_val, max_val in preset_buttons:
            btn = QPushButton(label)
            btn.setMaximumWidth(80)
            btn.clicked.connect(
                lambda checked, mn=min_val, mx=max_val: self._apply_amount_preset(mn, mx)
            )
            preset_layout.addWidget(btn)

        preset_layout.addStretch()
        self.filters_layout.addWidget(preset_container, 4, 1, 1, 2)

    def _on_amount_input_changed(self):
        """Handle amount input change with debounce."""
        # Debounce: Wait 500ms after user stops typing
        self.amount_timer.stop()
        self.amount_timer.start(500)

    def _emit_amount_filter(self):
        """Emit amount filter signal after debounce."""
        # Parse inputs
        min_text = self.amount_min.text().strip()
        max_text = self.amount_max.text().strip()

        # Convert to Decimal
        min_amount = None
        max_amount = None

        if min_text:
            try:
                min_amount = Decimal(min_text.replace('$', '').replace(',', ''))
            except:
                pass  # Invalid input - ignore

        if max_text:
            try:
                max_amount = Decimal(max_text.replace('$', '').replace(',', ''))
            except:
                pass  # Invalid input - ignore

        # Get absolute checkbox state
        absolute = self.amount_absolute_check.isChecked()

        # Store current state
        self.current_min_amount = min_amount
        self.current_max_amount = max_amount
        self.amount_absolute = absolute

        # Emit signal
        self.amount_filter_changed.emit(min_amount, max_amount, absolute)
        self._update_filter_count()

    def _apply_amount_preset(self, min_val: Optional[str], max_val: Optional[str]):
        """Apply amount preset from button click."""
        # Set input values
        self.amount_min.setText(min_val if min_val else "")
        self.amount_max.setText(max_val if max_val else "")

        # Emit immediately (no debounce for preset buttons)
        self._emit_amount_filter()

    def has_amount_filter(self) -> bool:
        """Check if amount filter is active."""
        return self.current_min_amount is not None or self.current_max_amount is not None

    def clear_amount_filter(self):
        """Clear amount filter (called by Clear All)."""
        self.amount_min.clear()
        self.amount_max.clear()
        self.amount_absolute_check.setChecked(False)
        self.current_min_amount = None
        self.current_max_amount = None
        self.amount_absolute = False

    def _update_filter_count(self):
        """Update active filter count."""
        count = 0

        if self.text_search_widget and self.text_search_widget.has_text():
            count += 1

        if self.has_date_filter():
            count += 1

        if self.has_category_filter():
            count += 1

        if self.has_amount_filter():
            count += 1

        self.set_active_filter_count(count)

    def _on_clear_all_filters(self):
        """Handle Clear All Filters button."""
        # Clear text search
        if self.text_search_widget:
            self.text_search_widget.clear()

        # Clear date filter
        if hasattr(self, 'clear_date_filter'):
            self.clear_date_filter()

        # Clear category filter
        if hasattr(self, 'clear_category_filter'):
            self.clear_category_filter()

        # Clear amount filter
        self.clear_amount_filter()

        # Emit signal
        self.filters_cleared.emit()
```

**Acceptance:**
- [ ] Amount inputs replace placeholder in row 3
- [ ] Min and Max inputs with $ placeholders
- [ ] Decimal validation (2 decimal places)
- [ ] Absolute value checkbox
- [ ] Preset buttons in row 4 (< $20, $20-$100, > $100, > $500)
- [ ] Debounced input (500ms) to avoid excessive filtering
- [ ] Preset buttons apply immediately (no debounce)
- [ ] Emits `amount_filter_changed` signal with (min, max, absolute)
- [ ] has_amount_filter() returns True when filter active
- [ ] clear_amount_filter() clears inputs and state
- [ ] Filter count includes amount filter

**Testing:**
```python
def test_amount_filter_min_only(qtbot):
    """Test setting minimum amount."""
    panel = SearchPanelWidget()
    qtbot.addWidget(panel)

    # Set min amount
    panel.amount_min.setText("100")

    # Wait for debounce
    with qtbot.waitSignal(panel.amount_filter_changed, timeout=1000) as blocker:
        panel.amount_timer.timeout.emit()

    # Verify signal
    min_amt, max_amt, absolute = blocker.args
    assert min_amt == Decimal("100")
    assert max_amt is None

def test_amount_filter_preset_button(qtbot):
    """Test preset button click."""
    panel = SearchPanelWidget()
    qtbot.addWidget(panel)

    # Click "> $100" button
    with qtbot.waitSignal(panel.amount_filter_changed) as blocker:
        panel._apply_amount_preset("100", None)

    # Verify inputs set
    assert panel.amount_min.text() == "100"
    assert panel.amount_max.text() == ""

    # Verify signal
    min_amt, max_amt, absolute = blocker.args
    assert min_amt == Decimal("100")
```

---

### Phase 5: Main Window Integration (Day 2 Afternoon - 1 hour) **FRONTEND DEV**

#### Task 5.1: Connect Amount Filter to Transaction List
**Assignee:** Frontend Developer
**Estimate:** 1 hour
**Files:** `finance_app/ui/main_window.py`

**Changes:**
```python
def _setup_ui(self):
    # ... existing code ...

    # Connect amount filter signal
    self.search_panel.amount_filter_changed.connect(self._on_amount_filter_changed)

def _on_amount_filter_changed(self, min_amount, max_amount, absolute):
    """Handle amount filter change."""
    # Store current filter state
    self.current_min_amount = min_amount
    self.current_max_amount = max_amount
    self.current_amount_absolute = absolute

    # Reload transactions with filter
    self._reload_transactions()

def _reload_transactions(self):
    """Reload transaction list with all active filters."""
    # Get current account
    account_id = self.current_account_id if hasattr(self, 'current_account_id') else None

    # Start with all transactions
    transactions = self.transaction_service.get_all_transactions(account_id=account_id)

    # Apply date filter if active
    if hasattr(self, 'current_date_from') and self.current_date_from and self.current_date_to:
        transactions = [
            t for t in transactions
            if self.current_date_from <= t.date <= self.current_date_to
        ]

    # Apply category filter if active
    if hasattr(self, 'current_categories') and self.current_categories:
        transactions = [t for t in transactions if t.category in self.current_categories]

    # Apply amount filter if active
    if hasattr(self, 'current_min_amount') or hasattr(self, 'current_max_amount'):
        min_amt = getattr(self, 'current_min_amount', None)
        max_amt = getattr(self, 'current_max_amount', None)
        absolute = getattr(self, 'current_amount_absolute', False)

        if min_amt or max_amt:
            transactions = [
                t for t in transactions
                if self._amount_in_range(t.amount, min_amt, max_amt, absolute)
            ]

    # Apply text search filter if active
    if hasattr(self, 'current_search_text') and self.current_search_text:
        search_text = self.current_search_text.lower()
        transactions = [t for t in transactions if search_text in t.description.lower()]

    # Update transaction table
    self._update_transaction_table(transactions)

    # Update status bar
    self._update_status_bar(f"Showing {len(transactions)} transactions")

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
- [ ] amount_filter_changed signal connected
- [ ] _on_amount_filter_changed() stores filter state
- [ ] _reload_transactions() applies amount filter
- [ ] _amount_in_range() helper method for filtering
- [ ] Combines with date, category, and text filters (AND logic)
- [ ] Transaction table updates when amount filter changes
- [ ] Status bar shows filtered count

**Testing:**
```python
def test_main_window_amount_filter_integration(qtbot):
    """Test amount filter integration in main window."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Set amount range
    window.search_panel.amount_min.setText("100")
    window.search_panel._emit_amount_filter()

    # Verify transaction list filtered
    # (Requires test transactions setup)
```

---

### Phase 6: Testing (Day 3 - 2.5 hours) **BACKEND DEV + FRONTEND DEV**

#### Task 6.1: Write Unit Tests for Repository/Service
**Assignee:** Backend Developer
**Estimate:** 1.5 hours
**Files:** `finance_app/tests/unit/test_transaction_repository.py`, `test_transaction_service.py`

**Tests to Write (12 tests):**
```python
def test_filter_by_amount_min_only()
def test_filter_by_amount_max_only()
def test_filter_by_amount_both_min_max()
def test_filter_by_amount_absolute_mode()
def test_filter_by_amount_decimal_precision()
def test_filter_by_amount_negative_values()
def test_filter_by_amount_zero()
def test_filter_by_amount_validation_min_greater_max()
def test_filter_by_amount_no_criteria()
def test_parse_amount_string_valid()
def test_parse_amount_string_invalid()
def test_parse_amount_string_with_currency_symbols()
```

**Acceptance:**
- [ ] 12+ unit tests for repository and service
- [ ] Tests cover min only, max only, both
- [ ] Absolute value mode tests
- [ ] Decimal precision tests
- [ ] Validation tests
- [ ] Edge cases (negative, zero, no criteria)

---

#### Task 6.2: Write Integration Tests
**Assignee:** Backend Developer
**Estimate:** 45 minutes
**Files:** `finance_app/tests/integration/test_amount_filter_integration.py` (NEW)

**Tests to Write:**
```python
def test_amount_filter_integration_large_purchases()
def test_amount_filter_integration_small_charges()
def test_amount_filter_integration_mid_range()
def test_amount_filter_combined_with_date()
def test_amount_filter_combined_with_category()
def test_amount_filter_clear_all()
```

**Acceptance:**
- [ ] 6+ integration tests
- [ ] Full workflow tests (presets, custom range, combined filters)
- [ ] Clear All Filters test
- [ ] Multi-filter combination tests

---

#### Task 6.3: Write Performance Tests
**Assignee:** Backend Developer / Tech Lead
**Estimate:** 15 minutes
**Files:** `finance_app/tests/performance/test_amount_filter_performance.py` (NEW)

**Tests to Write:**
```python
def test_amount_filter_performance_10k_transactions()
def test_amount_filter_index_usage()
def test_amount_filter_absolute_mode_performance()
```

**Acceptance:**
- [ ] 3 performance tests
- [ ] < 100ms for 10,000 transactions
- [ ] EXPLAIN QUERY PLAN verifies index usage
- [ ] Absolute mode performance acceptable

---

### Phase 7: Documentation (Day 3 - 30 minutes) **FRONTEND DEV**

#### Task 7.1: Update User Guide
**Assignee:** Frontend Developer
**Estimate:** 30 minutes
**Files:** `docs/USER_GUIDE.md`

**Section to Add:**
```markdown
## Filtering Transactions by Amount

The amount filter allows you to find transactions by monetary value.

### Using Amount Filter

**Min/Max Inputs:**
1. Enter minimum amount in "Min $" field (e.g., "100")
2. Enter maximum amount in "Max $" field (e.g., "500")
3. Leave either field blank to filter one side only
4. Transaction list updates automatically after you stop typing (500ms delay)

**Absolute Value Mode:**
- Check "Absolute" to ignore +/- signs
- Useful for finding large amounts regardless of income/expense
- Example: Find all transactions with absolute value > $100

### Preset Buttons

Click preset buttons for quick filtering:
- **< $20**: Small charges (subscriptions, coffee, etc.)
- **$20-$100**: Mid-range purchases
- **> $100**: Large purchases
- **> $500**: Very large purchases

### Examples

**Find Large Purchases:**
- Click "> $100" preset button
- View all transactions over $100

**Subscription Hunting:**
- Click "< $20" preset button
- Review small recurring charges
- Identify unused subscriptions

**Budget Range Analysis:**
- Enter Min: "50", Max: "100"
- View purchases in $50-$100 range
- Analyze mid-range spending patterns

### Combining with Other Filters

Amount filter works with other filters:
- **Amount + Date:** "Large purchases last month" (> $100 + Last Month)
- **Amount + Category:** "Groceries over $100" (> $100 + Groceries)
- **Amount + Date + Category:** "Large dining expenses this month"

### Clearing Filter

- Clear Min/Max fields to remove amount filter
- Click "Clear All Filters" to reset all filters
```

**Acceptance:**
- [ ] User Guide section added
- [ ] Screenshots of amount inputs and preset buttons
- [ ] Examples of amount filter usage
- [ ] Explanation of absolute value mode
- [ ] Clear instructions for combining filters

---

### Summary: Task Assignments by Role

**Tech Lead (5 minutes):**
- Task 1.1: Create database index on amount

**Backend Developer (5-6 hours):**
- Task 2.1: Repository amount filtering method (2 hrs)
- Task 3.1: Service layer with validation + parsing (1.5 hrs)
- Task 6.1-6.3: Unit/integration/performance tests (2.5 hrs)

**Frontend Developer (4-5 hours):**
- Task 4.1: SearchPanelWidget amount inputs + presets (2.5 hrs)
- Task 5.1: Main window integration (1 hr)
- Task 7.1: User Guide documentation (0.5 hr)

**Tech Lead Review (1 hour):**
- Code review (all phases)
- Performance validation
- UX review (preset buttons, debouncing)

**Total Estimated Time:** 10-12 hours (matches 4 story points)

---

## 📋 Definition of Done

- [ ] Amount inputs working
- [ ] Preset buttons (optional)
- [ ] Database index on `amount`
- [ ] 10+ unit tests passing
- [ ] 4+ integration tests passing
- [ ] Performance < 100ms for 10K
- [ ] User Guide updated

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-16 (Task Breakdown Added - Ready for Development)
**Sprint:** Sprint 15 (Week 5-6)
**Status:** ✅ READY FOR SPRINT 15 (Task breakdown complete, all dependencies met)
