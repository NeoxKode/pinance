# Sprint 2: Developer Assignments & Technical Guidance

**Sprint:** Sprint 2
**Story:** US-002A - Journal Entry Foundation
**Duration:** 2 weeks (Oct 23 - Nov 5, 2025)
**Tech Lead:** Tech Lead Agent

---

## 👥 Developer Assignments

### **Backend Developer: PRIMARY OWNER** (30 hours, 100% allocation)

**Developer:** [TBD - Assign Backend Developer]
**Story Points:** 8
**Estimated Hours:** 30 hours over 10 days
**Responsibility:** End-to-end ownership of US-002A implementation

**Skills Required:**
- ✅ Advanced Python (dataclasses, enums, Decimal arithmetic)
- ✅ Advanced SQLite (triggers, transactions, indices)
- ✅ Intermediate pytest (fixtures, mocking, parameterized tests)
- ✅ Database design (schema, constraints, migrations)

---

### **Frontend Developer: SUPPORT ROLE** (3 hours, 10% allocation)

**Developer:** [TBD - Assign Frontend Developer]
**Story Points:** 0 (support only)
**Estimated Hours:** 3 hours on Day 8-9
**Responsibility:** UI regression testing and verification

**Skills Required:**
- ✅ Basic PySide6/Qt (manual testing)
- ✅ Basic integration testing

---

## 📅 Day-by-Day Task Assignment

### **Days 1-2 (Oct 23-24): Database Foundation**

**Backend Developer Tasks:**
- [ ] **Task 2A.1:** Run migration `002_create_journal_entries.sql` (1 hour)
  - Verify journal_entries table created
  - Verify trigger_audit table created
  - Test migration rollback script

- [ ] **Task 2A.2:** Test database triggers (3 hours)
  - Write trigger integration tests (use `/finance_app/tests/integration/test_journal_triggers.py` as template)
  - Verify all 6 triggers fire correctly
  - Test validation triggers reject invalid data
  - Test balance update triggers

**Deliverables:**
- ✅ Migration runs successfully
- ✅ All triggers working
- ✅ 12+ trigger tests passing

**Tech Lead Review:** End of Day 2 (30 min review)

---

### **Days 3-4 (Oct 25-26): Models & Repository**

**Backend Developer Tasks:**
- [ ] **Task 2A.3:** Create JournalEntry model (2 hours)
  - File: `finance_app/data/models.py`
  - Add `EntryType` enum
  - Add `JournalEntry` dataclass
  - Implement `__post_init__` validation
  - Add helper properties (`amount`, `is_debit`, `is_credit`)

- [ ] **Task 2A.4:** Create JournalEntryRepository (4 hours)
  - File: `finance_app/data/repositories/journal_entry_repository.py`
  - Implement `create()` with balance_after calculation
  - Implement `get_by_account()` with date filtering
  - Implement `get_account_balance()` (SUM from journal)
  - Implement `update()` and `delete()`
  - **CRITICAL:** Use `BEGIN IMMEDIATE` for transaction isolation

- [ ] **Task 2A.7:** Write unit tests for model (2 hours)
  - File: `finance_app/tests/unit/test_journal_entry_model.py`
  - Test validation (both debit/credit, zero amounts, negative)
  - Test enum conversions
  - Test helper properties

- [ ] **Task 2A.8:** Write unit tests for repository (3 hours)
  - File: `finance_app/tests/unit/test_journal_entry_repository.py`
  - Test CRUD operations
  - Test date filtering
  - Test balance calculation
  - Mock database connections

**Deliverables:**
- ✅ JournalEntry model complete with validation
- ✅ JournalEntryRepository complete with all methods
- ✅ 10+ model tests passing
- ✅ 15+ repository tests passing

**Tech Lead Review:** End of Day 4 (1 hour code review)

---

### **Day 5 (Oct 27): Service Layer**

**Backend Developer Tasks:**
- [ ] **Task 2A.5:** Create DoubleEntryService (3 hours)
  - File: `finance_app/business/double_entry_service.py`
  - Implement `create_simple_transaction()`
  - Implement `validate_account_balance()`
  - Add proper debit/credit logic based on normal_balance
  - Write service layer tests

**Deliverables:**
- ✅ DoubleEntryService complete
- ✅ 8+ service tests passing
- ✅ Debit/credit logic correct for all account types

**Tech Lead Review:** End of Day 5 (30 min review)

---

### **Days 6-7 (Oct 28-29): Integration & Performance**

**Backend Developer Tasks:**
- [ ] **Task 2A.6:** Update TransactionService (3 hours)
  - File: `finance_app/business/transaction_service.py`
  - Integrate DoubleEntryService
  - Create journal entry when transaction created
  - Handle errors gracefully (rollback on failure)
  - **CRITICAL:** Maintain backward compatibility

- [ ] **Task 2A.9:** Write integration tests (3 hours)
  - File: `finance_app/tests/integration/test_double_entry_integration.py`
  - Test transaction → journal entry flow
  - Test balance integrity
  - Test error handling

- [ ] **Task 2A.10:** Add balance validation (2 hours)
  - Implement reconciliation check
  - Add admin function to validate all accounts
  - Test with realistic data

- [ ] **Task 2A.11:** Performance testing (2 hours)
  - Create 10,000 journal entries
  - Benchmark query performance (target: < 500ms)
  - Benchmark balance calculation (target: < 100ms)
  - Document results

**Deliverables:**
- ✅ TransactionService integrated with journal entries
- ✅ 5+ integration tests passing
- ✅ Performance benchmarks met and documented
- ✅ Balance validation working

**Tech Lead Review:** End of Day 7 (30 min review)

---

### **Day 8 (Oct 30): UI Testing & Verification**

**Backend Developer Tasks:**
- [ ] Manual testing with UI
- [ ] Fix any integration issues
- [ ] Prepare for code review

**Frontend Developer Tasks:** 👈 **JOIN HERE**
- [ ] **Manual UI Regression Testing (2 hours)**
  - Launch application
  - Create new transaction via UI
  - Verify transaction appears correctly
  - Verify account balance updates
  - Test with different account types
  - Test edge cases (large amounts, special characters)

- [ ] **Report Issues (1 hour)**
  - Document any UI bugs or regressions
  - Work with backend dev to resolve
  - Retest after fixes

**Deliverables:**
- ✅ UI regression test report
- ✅ All UI functionality working
- ✅ No user-visible changes (double-entry is invisible)

**Tech Lead Review:** End of Day 8 (1 hour joint review with both devs)

---

### **Day 9 (Nov 1): Code Review & Polish**

**Backend Developer Tasks:**
- [ ] Address tech lead code review feedback
- [ ] Refactor based on feedback
- [ ] Add missing tests (if any)
- [ ] Code cleanup

**Frontend Developer Tasks:**
- [ ] Final UI verification
- [ ] Retest after backend changes

**Tech Lead:** **FULL CODE REVIEW** (2-3 hours)
- Review all code against checklist
- Check architecture compliance
- Verify test coverage
- Check documentation
- Security review

**Deliverables:**
- ✅ All code review feedback addressed
- ✅ Code approved by tech lead
- ✅ Ready for merge

---

### **Day 10 (Nov 3): Documentation & Demo**

**Backend Developer Tasks:**
- [ ] **Task 2A.12:** Write documentation (2 hours)
  - Update ARCHITECTURE.md with journal entry system
  - Add examples and usage patterns
  - Document trigger behavior
  - Add migration notes

- [ ] Prepare sprint demo
- [ ] Update tracking documents

**Deliverables:**
- ✅ Documentation complete
- ✅ Sprint demo ready
- ✅ Story moved to completed

---

## 🔧 Technical Guidance for Backend Developer

### **Critical Implementation Notes**

#### 1. **Calculate balance_after BEFORE insert**

```python
# ✅ CORRECT
def create(self, entry: JournalEntry) -> JournalEntry:
    with self.db.get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE TRANSACTION")  # Get write lock
        cursor = conn.cursor()

        # Get current balance BEFORE inserting
        cursor.execute("SELECT balance FROM accounts WHERE id = ?", (entry.account_id,))
        current_balance = Decimal(str(cursor.fetchone()[0]))

        # Calculate what balance will be AFTER this entry
        entry.balance_after = current_balance + entry.amount

        # Now insert with calculated balance_after
        cursor.execute("INSERT INTO journal_entries (...) VALUES (...)")
        conn.commit()
```

#### 2. **Use BEGIN IMMEDIATE for write lock**

```python
# ✅ CORRECT - Prevents race conditions
conn.execute("BEGIN IMMEDIATE TRANSACTION")

# ❌ WRONG - Race condition possible
conn.execute("BEGIN TRANSACTION")  # Default is DEFERRED
```

#### 3. **Handle Decimal precision**

```python
# ✅ CORRECT - Convert floats to Decimal via string
balance = Decimal(str(row['balance']))

# ❌ WRONG - Direct float to Decimal loses precision
balance = Decimal(row['balance'])  # 0.1 + 0.2 != 0.3
```

#### 4. **Test triggers explicitly**

```python
# Use integration tests from test_journal_triggers.py
# These test actual database triggers, not mocks!
```

---

### **Common Pitfalls to Avoid**

❌ **Don't:** Create journal entry without calculating balance_after first
✅ **Do:** Calculate balance_after from current account balance before insert

❌ **Don't:** Use default BEGIN TRANSACTION (deferred lock)
✅ **Do:** Use BEGIN IMMEDIATE TRANSACTION for write operations

❌ **Don't:** Test triggers with mocks
✅ **Do:** Use integration tests with real database

❌ **Don't:** Forget to test rollback scenarios
✅ **Do:** Test that failed operations don't corrupt balances

❌ **Don't:** Skip performance testing until the end
✅ **Do:** Test with 10k entries on Day 7

---

## 📞 Communication & Escalation

### **Daily Standup (10am)**
- What did you do yesterday?
- What will you do today?
- Any blockers?

### **When to Escalate to Tech Lead**

**Immediate Escalation (< 1 hour):**
- Trigger not firing correctly
- Balance mismatch between cached and calculated
- Migration fails
- Critical bug found

**Same Day Escalation (< 4 hours):**
- Unsure about debit/credit logic
- Test failing and can't figure out why
- Performance benchmark not meeting targets

**Next Day Escalation:**
- Code design question
- Refactoring advice needed
- Test strategy clarification

### **Tech Lead Availability**

- **Daily:** Available for quick questions (Slack/chat)
- **Scheduled Reviews:** End of Day 2, 4, 5, 7, 8
- **Code Review:** Day 9 (2-3 hours dedicated)
- **Emergency:** Anytime for critical blockers

---

## ✅ Success Criteria

### **For Backend Developer**

**Must Have:**
- [ ] All 12 tasks completed
- [ ] All tests passing (40+ tests total)
- [ ] Performance benchmarks met
- [ ] Code reviewed and approved
- [ ] No regressions

**Nice to Have:**
- [ ] Test coverage > 90% for new code
- [ ] Zero tech debt added
- [ ] Documentation with examples

### **For Frontend Developer**

**Must Have:**
- [ ] UI regression test completed
- [ ] Test report submitted
- [ ] No UI bugs found (or all fixed)

**Nice to Have:**
- [ ] Suggestions for future UI improvements
- [ ] Additional test scenarios identified

---

## 🎓 Learning Outcomes

**By end of Sprint 2, developers will have learned:**

### Backend Developer
- ✅ SQLite trigger programming
- ✅ Database transaction isolation
- ✅ Double-entry accounting principles
- ✅ Decimal arithmetic in Python
- ✅ Integration testing with databases
- ✅ Performance optimization techniques

### Frontend Developer
- ✅ Backend integration testing
- ✅ Double-entry accounting basics
- ✅ Regression testing methodology

---

## 📊 Progress Tracking

**Backend Developer:** Update task checkboxes daily
**Tech Lead:** Review progress in daily standup
**Product Owner:** Check status in sprint dashboard

---

**Prepared By:** Tech Lead Agent
**Date:** October 22, 2025
**Sprint:** Sprint 2
**Status:** Ready for Developer Assignment

---

**Next Actions:**
1. Assign Backend Developer to US-002A
2. Assign Frontend Developer to support (Day 8-9)
3. Schedule kickoff meeting (Oct 23)
4. Begin Day 1 tasks!
