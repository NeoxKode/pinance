# Sprint 4 Kickoff - Split Transactions

**Sprint ID:** Sprint 4
**Duration:** October 23-28, 2025 (5 days)
**Story:** US-002C - Split Transactions
**Story Points:** 8
**Team:** Development Team
**Sprint Goal:** Implement split transaction functionality to enable complex multi-category transactions

---

## 🎯 Sprint Goal

Enable users to split a single transaction across multiple categories (e.g., paychecks, shopping receipts) while maintaining double-entry accounting integrity established in Sprint 3.

---

## 📊 Sprint 3 Recap - Context for Sprint 4

### What We Accomplished in Sprint 3

**Story:** US-002B - Balanced Transaction Groups
**Result:** ✅ **EXCEPTIONAL DELIVERY**

- **Tech Lead Grade:** A+ (97/100)
- **Product Owner Decision:** ACCEPTED - EXCEPTIONAL DELIVERY
- **Delivery:** 34 hours (29% under estimate), 50 tests (67% over target)
- **Status:** 1 sprint ahead of roadmap

**Key Deliverables That Enable Sprint 4:**

1. **Transaction Groups** (`transaction_groups` table)
   - Mechanism for linking related journal entries
   - Foundation for multi-entry transactions

2. **Double-Entry Service** (`DoubleEntryService`)
   - `create_balanced_group()` method for balanced multi-entry transactions
   - Automatic balance validation
   - Journal entry creation patterns

3. **Unified Transaction Dialog** (UnifiedTransactionDialog)
   - Professional UI with dark theme
   - HomeBank-inspired design
   - Patterns for amount input, validation, styling

4. **Opening Balance Migration**
   - Successfully migrated 4 accounts ($23,450.50)
   - Established patterns for data migration
   - Validation tools created

**Files You'll Build Upon:**

```
finance_app/
├── business/
│   └── double_entry_service.py          ← Use create_balanced_group()
├── data/
│   ├── models.py                         ← Add split models here
│   └── repositories/
│       ├── journal_entry_repository.py   ← Reference for patterns
│       └── transaction_group_repository.py
└── ui/
    └── dialogs/
        └── unified_transaction_dialog.py ← Reference for UI patterns
```

---

## 📚 Story Assignment: US-002C

### Story Overview

**User Story:**
> As a finance app user, I want to split a single transaction across multiple categories, so that I can accurately track complex transactions like paychecks and shopping trips.

**Business Value:**
- **High Impact:** 80%+ users have split transactions
- **Frequency:** 20-30% of all transactions need splits
- **Top Use Cases:**
  - Paychecks (gross pay - deductions = net pay)
  - Shopping receipts (multiple categories in one trip)
  - Bills with multiple line items
  - Income with processing fees

### Technical Scope

**New Components:**
1. **Database:** `transaction_splits` table
2. **Models:** `TransactionSplit`, `SplitTransaction`, `PaycheckSplit`
3. **Repository:** `TransactionSplitRepository`
4. **Service:** `SplitTransactionService`
5. **UI:** `SplitTransactionDialog`

**Integration Points:**
- Extends `DoubleEntryService.create_balanced_group()`
- Links to existing `transaction_groups` table
- Uses `JournalEntry` and `JournalEntryRepository`
- Follows patterns from `UnifiedTransactionDialog`

---

## 🚨 Critical Prerequisites (Day 1 Decision Required)

### Issue #1: Category-Account Linkage

**Problem:** Categories need to link to accounts for journal entry creation.

**Current State:**
- Categories have: `id`, `name`, `type` (income/expense)
- Categories do NOT have: `account_id`

**Impact:**
- Split transactions create journal entries for each category
- Each journal entry needs: debit account + credit account
- Service layer currently assumes `category.account_id` exists

**Two Options:**

#### Option A: Add account_id to Categories (RECOMMENDED)

**Pros:**
- Clean architecture
- Explicit relationships
- Better data integrity
- Easier to understand

**Cons:**
- Requires migration of existing categories
- Need to create/link accounts for all categories

**Implementation:**
```sql
ALTER TABLE categories ADD COLUMN account_id INTEGER;
-- Then link each category to an account:
-- "Groceries" → "Groceries Expense" account
-- "Salary" → "Salary Income" account
```

#### Option B: Auto-Create Accounts from Categories

**Pros:**
- No migration needed
- Simpler for users (fewer concepts)
- Works with existing data

**Cons:**
- Account proliferation (many auto-created accounts)
- Less control over chart of accounts
- Harder to customize account names

**Implementation:**
```python
def _get_or_create_category_account(self, category: Category) -> Account:
    account_name = f"{category.name} {'Expense' if category.type == 'expense' else 'Income'}"
    existing = self.account_repo.get_by_name(account_name)
    if existing:
        return existing
    # Auto-create
    return self.account_repo.create(...)
```

**DECISION NEEDED:** Team must choose on Day 1 morning standup.

**Tech Lead Recommendation:** Option A (cleaner architecture, better for long-term maintainability)

---

## 📋 5-Day Implementation Plan

### Day 1: Foundation & Schema (8 hours)
**Owner:** Backend Developer
**Deliverables:**
- [ ] Database migration script created
- [ ] `transaction_splits` table created with constraints
- [ ] Split data models implemented
- [ ] Migration tested on local DB

**Key Tasks:**
1. Morning standup: Decide category-account linkage approach
2. Create `004_create_split_transactions.sql` migration
3. Implement `TransactionSplit`, `SplitTransaction`, `PaycheckSplit` in `models.py`
4. Run migration, verify with `scripts/check_schema.py`

---

### Day 2: Repository Layer (8 hours)
**Owner:** Backend Developer
**Deliverables:**
- [ ] `TransactionSplitRepository` implemented
- [ ] Unit tests written (15+ tests)
- [ ] 100% repository test coverage

**Key Tasks:**
1. Create `transaction_split_repository.py`
2. Implement CRUD operations (create, read, update, delete)
3. Ensure atomic transactions for split creation
4. Write comprehensive unit tests

---

### Day 3: Service Layer (8 hours)
**Owner:** Backend Developer
**Deliverables:**
- [ ] `SplitTransactionService` implemented
- [ ] Integration with `DoubleEntryService`
- [ ] Unit tests written (10+ tests)
- [ ] 85%+ coverage for service layer

**Key Tasks:**
1. Create `split_transaction_service.py`
2. Implement `create_split_transaction()` with validation
3. Implement `create_paycheck_split()` template
4. Integrate with `DoubleEntryService.create_balanced_group()`
5. Write unit tests

---

### Day 4: UI Implementation (8 hours)
**Owner:** Frontend Developer
**Deliverables:**
- [ ] `SplitTransactionDialog` implemented
- [ ] Templates (paycheck, shopping) working
- [ ] Real-time balance validation
- [ ] Dark theme applied

**Key Tasks:**
1. Create `split_transaction_dialog.py`
2. Build split table UI (category, amount, memo columns)
3. Implement balance indicator (green/yellow/red)
4. Add template buttons (paycheck, shopping)
5. Apply dark theme (reference UnifiedTransactionDialog)

---

### Day 5: Integration & Testing (8 hours)
**Owner:** Full Team
**Deliverables:**
- [ ] UI integrated into MainWindow
- [ ] Integration tests written (10+ tests)
- [ ] End-to-end testing complete
- [ ] Code review requested

**Key Tasks:**
1. Integrate dialog into MainWindow menu
2. Write integration tests (end-to-end workflows)
3. Performance testing (< 100ms for 10 splits)
4. Full test suite run (unit + integration)
5. Code cleanup and documentation
6. Request tech lead code review

---

## 🎯 Success Criteria

### Functional Requirements
- [ ] All 6 acceptance criteria met (AC1-AC6)
- [ ] Balance validation working at UI, service, and DB levels
- [ ] Paycheck template working end-to-end
- [ ] Shopping template working
- [ ] Delete cascade working correctly

### Technical Requirements
- [ ] Test coverage > 80% for all new code
- [ ] All tests passing (unit + integration + existing)
- [ ] No pylint errors or warnings
- [ ] Type hints on all public methods
- [ ] Performance: 10 splits < 100ms

### Code Quality
- [ ] Tech lead approval obtained
- [ ] No code smells or anti-patterns
- [ ] Proper error handling throughout
- [ ] Comprehensive docstrings
- [ ] Architecture compliance verified

---

## 📚 Required Reading

**CRITICAL:** Review these before starting implementation:

1. **[US-002C Story Document](../stories/backlog/US-002C-split-transactions.md)**
   - Full story with acceptance criteria
   - Complete technical implementation details
   - Test plan (30+ tests)

2. **[US-002C Technical Review](../stories/backlog/US-002C-TECH-REVIEW.md)**
   - Grade: A (92/100) - APPROVED WITH CONDITIONS
   - Critical issues and recommendations
   - Performance analysis
   - Day-by-day implementation guide

3. **[US-002B: Balanced Transaction Groups](../stories/completed/US-002B-balanced-transaction-groups.md)**
   - Foundation for split transactions
   - `create_balanced_group()` pattern
   - UnifiedTransactionDialog UI patterns
   - Opening balance migration lessons

4. **[US-002A: Journal Entry Foundation](../stories/completed/US-002A-journal-entry-foundation.md)**
   - Double-entry basics
   - Balance validation patterns
   - Decimal usage best practices

---

## 🔗 Key Code References

### 1. DoubleEntryService Pattern

**File:** `finance_app/business/double_entry_service.py`

```python
# This is how you'll create journal entries for splits:
created_group, created_entries = self.double_entry_service.create_balanced_group(
    entries=journal_entries,  # List of JournalEntry objects
    group=group                # TransactionGroup object
)
# Automatically validates that debits = credits
```

**Why Important:** Each split creates 2 journal entries (debit + credit). You'll call this once with all entries for the split transaction.

---

### 2. UnifiedTransactionDialog Pattern

**File:** `finance_app/ui/dialogs/unified_transaction_dialog.py` (lines 1-591)

**Key Patterns to Reuse:**

1. **Dark Theme Styling:**
```python
self.setStyleSheet("""
    QDialog {
        background-color: #2b2b2b;
        color: white;
    }
    QLineEdit, QComboBox {
        background-color: #3c3c3c;
        color: white;
        border: 1px solid #555;
    }
""")
```

2. **Amount Input with +/- Buttons:**
```python
minus_btn.setFixedWidth(15)  # User requested 15px
plus_btn.setFixedWidth(15)
amount_layout.addWidget(self.expense_amount, 1)  # Stretch factor
```

3. **Validation Pattern:**
```python
validator = QDoubleValidator(0.01, 999999.99, 2, self)
self.amount_edit.setValidator(validator)
```

---

### 3. Atomic Transaction Pattern

**File:** `finance_app/data/repositories/journal_entry_repository.py`

```python
with self.db.get_connection() as conn:
    cursor = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION")

        # Multiple operations here

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise DatabaseError(f"Failed: {e}")
```

**Why Important:** Split creation involves multiple database operations that must succeed or fail together.

---

## 🆘 Getting Help

### Questions & Resources

**Architecture Questions:**
- See: `docs/ARCHITECTURE.md`
- Reference: Sprint 3 tech review (`SPRINT-03-TECH-LEAD-REVIEW.md`)

**Database Questions:**
- Reference: US-002A for journal entry patterns
- Reference: US-002B Phase 1 for migration patterns

**UI Questions:**
- Reference: UnifiedTransactionDialog
- Color scheme: Dark theme (#2b2b2b background)

### Escalation Path

**Blockers?** Escalate immediately if:
1. Category-account linkage decision not clear
2. Balance validation not working as expected
3. Performance targets not being met (>100ms)
4. `create_balanced_group()` integration issues
5. UI integration problems with MainWindow

**Tag:** Tech Lead for immediate support

---

## 📊 Sprint Metrics to Track

Track these daily in standup:

1. **Progress:**
   - Tasks completed vs. planned
   - Tests written (target: 30+)
   - Test coverage percentage

2. **Quality:**
   - Test pass rate
   - Pylint score
   - Code review feedback

3. **Performance:**
   - Split creation time (target: < 100ms for 10 splits)
   - Database query count per split

4. **Blockers:**
   - Any blockers or dependencies
   - Technical decisions pending

---

## 🎉 Sprint 3 Lessons Learned

**What Went Well:**
1. ✅ Incremental approach (4 phases) worked great
2. ✅ Early validation scripts caught issues
3. ✅ UI iteration led to professional result
4. ✅ Strong test coverage prevented regressions

**Apply to Sprint 4:**
1. 🎯 Day 1: Get schema and models right (foundation matters)
2. 🎯 Test early and often (don't wait until Day 5)
3. 🎯 Reference UnifiedTransactionDialog patterns (don't reinvent)
4. 🎯 Ask questions early (tech lead available)

---

## 🚀 Let's Build Something Great!

Sprint 3 delivered exceptional results. Sprint 4 is well-planned, technically sound, and builds on proven patterns. You have:

- ✅ Clear 5-day plan
- ✅ Complete technical specs
- ✅ Reference implementations
- ✅ Strong foundation from Sprint 3
- ✅ Tech lead support

**Confidence Level:** HIGH - This sprint is well-positioned for success.

---

**Sprint Start:** October 23, 2025
**Sprint End:** October 28, 2025
**Daily Standup:** 9:00 AM
**Code Review:** Day 5 EOD

**Let's ship US-002C! 🚀**

---

**Created:** October 23, 2025
**Sprint Lead:** Tech Lead
**Story Owner:** Product Owner
**Development Team:** Backend + Frontend Developers
