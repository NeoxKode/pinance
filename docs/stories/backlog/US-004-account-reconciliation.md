# US-004: Account Reconciliation

**Story ID:** US-004
**Epic:** [EPIC-01: Account Management & Double-Entry Foundation](../../epics/epic-01-account-management.md)
**Created:** 2025-10-23
**Status:** 📋 Backlog (Ready for Sprint 6)
**Priority:** P0 (Critical - Core Feature)
**Story Points:** 8
**Assignee:** Unassigned
**Dependencies:** ✅ US-001 (Account Type Taxonomy) - Complete, ✅ US-002A (Journal Entry Foundation) - Complete, ✅ US-003 (Normal Balance Calculation) - Complete

---

## 📖 User Story

**As a** personal finance user
**I want** to reconcile my bank accounts against official statements
**So that** I can verify my records match the bank's records and catch any discrepancies or errors

---

## 📝 Description

### Context

Account reconciliation is a fundamental accounting practice where users compare their recorded transactions against official bank statements to ensure accuracy. This process:

- **Catches Errors**: Identifies duplicate entries, missing transactions, or data entry mistakes
- **Detects Fraud**: Spots unauthorized transactions or unusual activity
- **Ensures Accuracy**: Confirms the user's balance matches the bank's balance
- **Provides Peace of Mind**: Users know their financial records are correct

In double-entry accounting systems, reconciliation involves:
1. Starting with an **opening balance** (cleared balance from last reconciliation)
2. Adding/subtracting **new transactions** (marked as cleared during reconciliation)
3. Arriving at a **closing balance** that should match the bank statement

### Problem Statement

**Current Issues**:
1. ❌ No reconciliation status tracking (transactions can't be marked as cleared/pending)
2. ❌ No reconciliation history (can't see when accounts were last reconciled)
3. ❌ No statement date/balance tracking
4. ❌ No way to calculate discrepancies between user records and bank statements
5. ❌ No reconciliation workflow in UI
6. ❌ No reconciliation reports or audit trail

**User Pain Points**:
- "I don't know which transactions have cleared the bank"
- "I can't tell if my balance matches my bank statement"
- "I have to use a spreadsheet to reconcile my accounts"
- "I can't track reconciliation history"
- "I don't know when I last reconciled"

**Example Problem**:
```
User's Balance: $1,250.00
Bank Statement: $1,200.00
Discrepancy: $50.00 (unknown cause)

Without reconciliation:
- Can't identify which transactions are pending vs cleared
- Can't track down the $50.00 difference
- No audit trail of past reconciliations
```

### Proposed Solution

Add comprehensive reconciliation support:

1. **Transaction Reconciliation Status**
   - Add `reconciliation_status` field: `unreconciled`, `pending`, `cleared`
   - Add `reconciled_date` timestamp for audit trail
   - Add `statement_date` to associate with specific bank statement

2. **Account Reconciliation Tracking**
   - Track last reconciliation date per account
   - Store statement ending balance and date
   - Calculate and store discrepancies
   - Maintain reconciliation history

3. **Reconciliation Workflow**
   - Load unreconciled transactions for an account
   - Mark transactions as cleared against a statement
   - Calculate expected vs actual ending balance
   - Save reconciliation record with statement details

4. **Reconciliation Reports**
   - Show cleared vs uncleared transactions
   - Display reconciliation history
   - Highlight discrepancies that need investigation

**Example Solution**:
```python
# Start reconciliation
reconciliation = service.start_reconciliation(
    account_id=checking_account_id,
    statement_date="2025-10-31",
    statement_balance=Decimal("1200.00")
)

# Mark transactions as cleared
service.mark_cleared(transaction_id=101)
service.mark_cleared(transaction_id=102)
# ... mark all cleared transactions

# Calculate discrepancy
cleared_balance = service.calculate_cleared_balance(account_id)
# cleared_balance = $1,200.00

discrepancy = statement_balance - cleared_balance
# discrepancy = $0.00 ✅ Balanced!

# Complete reconciliation
service.complete_reconciliation(reconciliation_id)
```

---

## ✅ Acceptance Criteria

### Functional Requirements

#### AC1: Transaction Reconciliation Status
- [ ] **Given** a transaction exists
      **When** the transaction is created
      **Then** it should have `reconciliation_status='unreconciled'` by default

- [ ] **Given** a transaction is marked as cleared
      **When** the user confirms it matches the bank statement
      **Then** the transaction should have `reconciliation_status='cleared'` and `reconciled_date` set

- [ ] **Given** a transaction is cleared
      **When** viewing the transaction
      **Then** the cleared status should be visible with the reconciled date

#### AC2: Start Reconciliation Workflow
- [ ] **Given** an account with unreconciled transactions
      **When** the user starts reconciliation
      **Then** the system should prompt for statement date and ending balance

- [ ] **Given** a user starts reconciliation
      **When** they provide statement details
      **Then** the system should display all unreconciled transactions for that account

- [ ] **Given** reconciliation is in progress
      **When** viewing transactions
      **Then** unreconciled transactions should be clearly marked and filterable

#### AC3: Mark Transactions as Cleared
- [ ] **Given** unreconciled transactions are displayed
      **When** the user marks a transaction as cleared
      **Then** the transaction status should update to 'cleared'

- [ ] **Given** multiple transactions to reconcile
      **When** the user marks all matching transactions
      **Then** the system should calculate the running cleared balance

- [ ] **Given** a transaction is incorrectly marked as cleared
      **When** the user un-marks it
      **Then** the transaction should return to 'unreconciled' status

#### AC4: Calculate Reconciliation Discrepancy
- [ ] **Given** transactions are marked as cleared
      **When** the system calculates cleared balance
      **Then** it should sum all cleared transactions from the last reconciliation

- [ ] **Given** a cleared balance is calculated
      **When** compared to the statement balance
      **Then** the system should display any discrepancy (difference)

- [ ] **Given** a discrepancy exists
      **When** displayed to the user
      **Then** it should clearly indicate amount and direction (over/under)

#### AC5: Complete Reconciliation
- [ ] **Given** reconciliation is in progress
      **When** the user completes reconciliation
      **Then** a reconciliation record should be saved with statement details

- [ ] **Given** reconciliation is completed
      **When** saved
      **Then** the account's `last_reconciled_date` should be updated

- [ ] **Given** reconciliation is completed
      **When** viewing reconciliation history
      **Then** the reconciliation should appear with date, balance, and discrepancy

#### AC6: Reconciliation History
- [ ] **Given** an account has been reconciled multiple times
      **When** viewing reconciliation history
      **Then** all past reconciliations should be listed with dates and balances

- [ ] **Given** a past reconciliation record
      **When** selected
      **Then** the details should show which transactions were cleared in that reconciliation

### Non-Functional Requirements

- [ ] **Performance**: Load unreconciled transactions < 100ms for accounts with 1000+ transactions
- [ ] **Data Integrity**: Reconciliation records are immutable once completed
- [ ] **Usability**: Reconciliation workflow should be intuitive for non-accountants
- [ ] **Audit Trail**: All reconciliation actions should be logged
- [ ] **Concurrency**: Prevent concurrent reconciliations on the same account

### Definition of Done

- [ ] Code implemented following architecture patterns
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests verify reconciliation workflow end-to-end
- [ ] Code reviewed and approved by tech lead
- [ ] Documentation updated (user guide, architecture notes)
- [ ] No regressions in existing tests
- [ ] UI/UX reviewed and approved
- [ ] Manual testing completed with real-world scenarios
- [ ] Acceptance criteria verified by Product Owner

---

## 🔧 Technical Details

### Affected Components

- [x] **Data Layer**:
  - `finance_app/data/models.py` (Transaction model)
  - `finance_app/data/models.py` (NEW: Reconciliation model)
  - `finance_app/data/repositories/transaction_repository.py` (query methods)
  - `finance_app/data/repositories/reconciliation_repository.py` (NEW)

- [x] **Business Layer**:
  - `finance_app/business/reconciliation_service.py` (NEW)
  - `finance_app/business/account_service.py` (update with last_reconciled_date)

- [x] **Database**:
  - Migration: Add `reconciliation_status`, `reconciled_date`, `statement_date` to transactions
  - Migration: Create `reconciliations` table
  - Migration: Add `last_reconciled_date` to accounts

- [x] **UI Layer**:
  - `finance_app/ui/dialogs/reconciliation_dialog.py` (NEW)
  - `finance_app/ui/main_window.py` (add reconciliation menu/button)

- [x] **Tests**:
  - `finance_app/tests/unit/test_reconciliation_service.py` (NEW)
  - `finance_app/tests/integration/test_reconciliation_workflow.py` (NEW)

### Database Schema Changes

```sql
-- Migration 005: Add reconciliation support

-- 1. Add reconciliation fields to transactions table
ALTER TABLE transactions
ADD COLUMN reconciliation_status TEXT DEFAULT 'unreconciled'
    CHECK (reconciliation_status IN ('unreconciled', 'pending', 'cleared'));

ALTER TABLE transactions
ADD COLUMN reconciled_date TEXT;  -- ISO 8601 format

ALTER TABLE transactions
ADD COLUMN statement_date TEXT;  -- Which statement this was reconciled against

-- 2. Add last_reconciled_date to accounts table
ALTER TABLE accounts
ADD COLUMN last_reconciled_date TEXT;

-- 3. Create reconciliations table
CREATE TABLE IF NOT EXISTS reconciliations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    reconciliation_date TEXT NOT NULL,  -- When reconciliation was performed
    statement_date TEXT NOT NULL,       -- Date of bank statement
    statement_balance REAL NOT NULL,    -- Ending balance on statement
    cleared_balance REAL NOT NULL,      -- Calculated balance of cleared transactions
    discrepancy REAL NOT NULL,          -- Difference (can be 0.00 if balanced)
    transaction_count INTEGER NOT NULL, -- Number of transactions cleared
    notes TEXT,                         -- Optional notes about discrepancies
    created_at TEXT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

-- 4. Create indices for performance
CREATE INDEX idx_transactions_reconciliation
ON transactions(account_id, reconciliation_status);

CREATE INDEX idx_reconciliations_account
ON reconciliations(account_id, reconciliation_date DESC);
```

### Implementation Approach

#### Step 1: Data Models
```python
# finance_app/data/models.py

class ReconciliationStatus(str, Enum):
    """Transaction reconciliation status."""
    UNRECONCILED = 'unreconciled'  # Not yet reconciled
    PENDING = 'pending'            # In active reconciliation session
    CLEARED = 'cleared'            # Confirmed cleared on statement

@dataclass
class Transaction:
    """Transaction model with reconciliation support (US-004)."""
    # ... existing fields ...
    reconciliation_status: ReconciliationStatus = ReconciliationStatus.UNRECONCILED
    reconciled_date: Optional[str] = None      # Date marked as cleared
    statement_date: Optional[str] = None       # Which statement period

@dataclass
class Reconciliation:
    """
    Reconciliation record model (US-004).

    Represents a completed reconciliation session where transactions
    were matched against a bank statement.
    """
    id: Optional[int]
    account_id: int
    reconciliation_date: str         # When reconciliation was done
    statement_date: str              # Date of bank statement
    statement_balance: Decimal       # Bank's ending balance
    cleared_balance: Decimal         # Calculated from cleared transactions
    discrepancy: Decimal             # Difference (should be 0.00)
    transaction_count: int           # Number of transactions cleared
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    def is_balanced(self) -> bool:
        """Check if reconciliation is balanced (no discrepancy)."""
        return self.discrepancy == Decimal("0.00")
```

#### Step 2: Reconciliation Service
```python
# finance_app/business/reconciliation_service.py

class ReconciliationService:
    """Service for account reconciliation operations (US-004)."""

    def start_reconciliation(
        self,
        account_id: int,
        statement_date: str,
        statement_balance: Decimal
    ) -> dict:
        """
        Start a new reconciliation session.

        Returns dict with:
        - unreconciled_transactions: List of transactions to reconcile
        - opening_balance: Balance from last reconciliation
        - statement_balance: Target balance from statement
        """

    def get_unreconciled_transactions(
        self,
        account_id: int
    ) -> List[Transaction]:
        """Get all unreconciled transactions for an account."""

    def mark_transaction_cleared(
        self,
        transaction_id: int,
        statement_date: str
    ) -> Transaction:
        """Mark a transaction as cleared."""

    def unmark_transaction(
        self,
        transaction_id: int
    ) -> Transaction:
        """Unmark a transaction (return to unreconciled)."""

    def calculate_cleared_balance(
        self,
        account_id: int,
        up_to_date: Optional[str] = None
    ) -> Decimal:
        """Calculate balance of all cleared transactions."""

    def calculate_discrepancy(
        self,
        account_id: int,
        statement_balance: Decimal
    ) -> Decimal:
        """Calculate difference between statement and cleared balance."""

    def complete_reconciliation(
        self,
        account_id: int,
        statement_date: str,
        statement_balance: Decimal,
        notes: Optional[str] = None
    ) -> Reconciliation:
        """
        Complete reconciliation and save record.

        Validates that cleared balance matches statement balance
        (or user acknowledges discrepancy).
        """

    def get_reconciliation_history(
        self,
        account_id: int,
        limit: int = 10
    ) -> List[Reconciliation]:
        """Get past reconciliation records for an account."""
```

#### Step 3: Repository Methods
```python
# finance_app/data/repositories/transaction_repository.py

def get_by_reconciliation_status(
    self,
    account_id: int,
    status: ReconciliationStatus
) -> List[Transaction]:
    """Get transactions by reconciliation status."""

def mark_cleared(
    self,
    transaction_id: int,
    reconciled_date: str,
    statement_date: str
) -> Transaction:
    """Mark transaction as cleared."""

# finance_app/data/repositories/reconciliation_repository.py (NEW)

class ReconciliationRepository:
    """Repository for reconciliation records (US-004)."""

    def create(self, reconciliation: Reconciliation) -> Reconciliation:
        """Save a completed reconciliation record."""

    def get_by_account(
        self,
        account_id: int,
        limit: int = 10
    ) -> List[Reconciliation]:
        """Get reconciliation history for an account."""

    def get_last_reconciliation(
        self,
        account_id: int
    ) -> Optional[Reconciliation]:
        """Get the most recent reconciliation for an account."""
```

### API Changes

**New Service**: `ReconciliationService`
**New Repository**: `ReconciliationRepository`
**New Model**: `Reconciliation`
**New Enum**: `ReconciliationStatus`

**Updated Models**:
- `Transaction`: Added `reconciliation_status`, `reconciled_date`, `statement_date`
- `Account`: Added `last_reconciled_date`

---

## 🎨 Design

### UI/UX Mockups

**Reconciliation Dialog Flow:**

```
┌─────────────────────────────────────────────────────┐
│ Reconcile Account: Checking Account                │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Statement Details:                                  │
│ ┌──────────────────────┬──────────────────────┐   │
│ │ Statement Date:      │ [2025-10-31       ▼]│   │
│ │ Ending Balance:      │ [$1,200.00        ] │   │
│ └──────────────────────┴──────────────────────┘   │
│                                                     │
│ Transactions to Reconcile:                         │
│ ┌─────────────────────────────────────────────┐   │
│ │☐ 10/15  Walmart           -$45.23           │   │
│ │☑ 10/16  Paycheck         +$2,000.00         │   │
│ │☑ 10/18  Electric Bill     -$125.00          │   │
│ │☐ 10/25  Gas Station       -$35.00 (pending)│   │
│ │☑ 10/28  Rent Payment      -$1,200.00        │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ Summary:                                            │
│ ┌──────────────────────────────────────────────┐   │
│ │ Opening Balance:        $500.00              │   │
│ │ Cleared Transactions:  +$575.00              │   │
│ │ Cleared Balance:       $1,200.00             │   │
│ │                                              │   │
│ │ Statement Balance:     $1,200.00             │   │
│ │ Discrepancy:           $0.00 ✅              │   │
│ └──────────────────────────────────────────────┘   │
│                                                     │
│              [Cancel]  [Complete Reconciliation]   │
└─────────────────────────────────────────────────────┘
```

### User Flow

1. **Start Reconciliation**
   - User selects "Reconcile" from account menu
   - System prompts for statement date and ending balance
   - System loads unreconciled transactions

2. **Mark Transactions**
   - User checks off transactions that appear on bank statement
   - System updates cleared balance in real-time
   - System shows running discrepancy

3. **Review Discrepancy**
   - If balanced: System shows success message
   - If discrepancy: System highlights amount and prompts for investigation
   - User can add notes about discrepancies

4. **Complete Reconciliation**
   - User clicks "Complete Reconciliation"
   - System saves reconciliation record
   - System updates account's last_reconciled_date
   - System shows confirmation with summary

---

## 🧪 Test Plan

### Test Cases

#### Test Case 1: Mark Transaction as Cleared
- **Given:** An unreconciled transaction exists
- **When:** User marks it as cleared with statement date 2025-10-31
- **Then:** Transaction status should be 'cleared', reconciled_date and statement_date should be set
- **Test Data:** Transaction ID=100, Amount=-$45.00

#### Test Case 2: Calculate Cleared Balance
- **Given:** Account has 3 cleared transactions ($100, -$50, -$25)
- **When:** System calculates cleared balance
- **Then:** Cleared balance should be $25.00
- **Test Data:** Account ID=1, Opening Balance=$0.00

#### Test Case 3: Detect Discrepancy
- **Given:** Statement balance is $1,200.00, cleared balance is $1,150.00
- **When:** System calculates discrepancy
- **Then:** Discrepancy should be -$50.00 (user is $50 short)
- **Test Data:** Account ID=1

#### Test Case 4: Complete Balanced Reconciliation
- **Given:** Cleared balance matches statement balance
- **When:** User completes reconciliation
- **Then:** Reconciliation record should be created with discrepancy=$0.00
- **Test Data:** Statement Balance=$1,200.00, Cleared Balance=$1,200.00

#### Test Case 5: Unmark Transaction
- **Given:** A transaction is marked as cleared
- **When:** User un-marks it
- **Then:** Transaction status should return to 'unreconciled'
- **Test Data:** Transaction ID=100

#### Test Case 6: Reconciliation History
- **Given:** Account has 3 past reconciliations
- **When:** User views reconciliation history
- **Then:** All 3 reconciliations should be listed in reverse chronological order
- **Test Data:** Account ID=1

### Edge Cases
- [ ] Account with no transactions (should allow reconciliation with $0 balance)
- [ ] Account with only cleared transactions (should show "No transactions to reconcile")
- [ ] Large discrepancy (>$100) should show warning
- [ ] Reconciling with future date (should show warning)
- [ ] Concurrent reconciliation attempts (should be prevented)

### Error Scenarios
- [ ] Invalid statement date (e.g., before last reconciliation)
- [ ] Invalid statement balance (negative balance for asset account)
- [ ] Missing account (account_id doesn't exist)
- [ ] Completing reconciliation with large unacknowledged discrepancy

---

## 📊 Estimation

### Story Points Breakdown
- **Data Model Changes:** 1 point (add fields, create Reconciliation model)
- **Database Migration:** 1 point (migration script, indices)
- **Service Implementation:** 2 points (ReconciliationService with 8+ methods)
- **Repository Implementation:** 1 point (ReconciliationRepository)
- **UI Implementation:** 2 points (Reconciliation dialog with real-time updates)
- **Testing:** 1 point (unit + integration tests)
- **Total:** 8 points

### Time Estimate
- **Optimistic:** 12 hours (1.5 days)
- **Realistic:** 16 hours (2 days)
- **Pessimistic:** 24 hours (3 days)

### Complexity
- **Technical Complexity:** Medium-High (multi-step workflow, real-time calculations)
- **Business Complexity:** Medium (banking reconciliation logic)
- **Risk Level:** Medium (core financial feature, must be accurate)

---

## 🔗 Dependencies

### Blocked By
- ✅ [US-001: Account Type Taxonomy](../completed/US-001-account-type-taxonomy.md) - COMPLETE
- ✅ [US-002A: Journal Entry Foundation](../completed/US-002A-journal-entry-foundation.md) - COMPLETE
- ✅ [US-003: Normal Balance Calculation](../completed/US-003-normal-balance-calculation.md) - COMPLETE

### Blocks
- ⏳ US-005: Opening Balance Equity (needs reconciliation for opening balance handling)
- ⏳ Future: Reconciliation Reports (depends on reconciliation history)

### Related Stories
- 🔗 US-002B: Balanced Transaction Groups (reconciliation works with transaction groups)
- 🔗 US-002C: Split Transactions (split transactions can be reconciled)

---

## 🎯 Business Value

### User Impact
**Direct Impact**: High - Reconciliation is a core accounting feature
- ✅ Enables users to verify accuracy of their records
- ✅ Catches errors, fraud, and discrepancies
- ✅ Provides peace of mind and confidence in data
- ✅ Essential for serious personal finance management

**User Segments Impacted:**
- Budget-conscious individuals (50% of users) - High value
- Household financial managers (30% of users) - Critical value
- Freelancers/small business owners (15% of users) - Critical value
- Privacy-conscious users (5% of users) - High value

### Competitive Advantage
- ✅ Matches capabilities of commercial tools (Quicken, YNAB)
- ✅ Provides audit trail for reconciliation history
- ✅ Supports professional accounting workflows
- ✅ Differentiates from simple expense trackers

### Success Metrics
- **Adoption:** 60%+ of active users reconcile at least monthly
- **Accuracy:** 95%+ of reconciliations complete without discrepancies
- **Satisfaction:** NPS increase by 10+ points after feature release
- **Retention:** Users who reconcile have 2x retention rate

---

## 📝 Notes

### Technical Notes
- Reconciliation records are immutable once created (audit trail)
- Use optimistic locking to prevent concurrent reconciliations
- Consider background job to auto-suggest transactions for reconciliation
- Performance critical: Query optimization for large transaction sets

### Business Notes
- Many users don't understand reconciliation - need excellent UX and help text
- Consider "Quick Reconcile" mode for users who trust their data
- Future: Import bank statements (OFX/QFX) for automatic matching
- Future: Mobile app push notification reminders to reconcile

### Questions
- [ ] Should we support partial reconciliation (some transactions left unreconciled)? **Answer:** Yes, allow flexible workflow
- [ ] What happens if user deletes a cleared transaction? **Answer:** Mark reconciliation as "modified" and flag for review
- [ ] Should we support bulk mark/unmark? **Answer:** Yes, add for Sprint 7

### Risks
- **Risk 1:** Complex UI workflow may confuse non-accounting users
  - **Mitigation:** Simple, guided workflow with tooltips and help text
- **Risk 2:** Performance with 10,000+ transactions
  - **Mitigation:** Pagination, indices, and query optimization
- **Risk 3:** Users may not understand discrepancies
  - **Mitigation:** Clear error messages and help documentation

---

## 📚 References

### Accounting Concepts
- [Bank Reconciliation](https://www.accountingtools.com/articles/bank-reconciliation.html)
- [Reconciliation Best Practices](https://www.quickbooks.intuit.com/r/bookkeeping/bank-reconciliation/)

### Code References
- `finance_app/data/models.py:95` - Transaction model
- `finance_app/business/account_service.py` - Account service for last_reconciled_date

### Related Documents
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - System architecture
- [USER_GUIDE.md](../../USER_GUIDE.md) - User documentation (to be updated)

### External Resources
- [Quicken Reconciliation](https://www.quicken.com/support/reconciling-account) - Industry reference
- [YNAB Reconciliation](https://support.youneedabudget.com/t/m38x58/reconciling-accounts) - Alternative approach

---

**Created By:** Product Owner
**Last Updated:** 2025-10-23
**Story Status:** 📋 Ready for Sprint 6
**Estimated Delivery:** Sprint 6 (2 days)
