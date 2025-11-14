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
**Sprint:** Sprint 15 (Week 5-6)
**Status:** 📋 BACKLOG
