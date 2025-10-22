# US-002A: Journal Entry Foundation (Double-Entry Phase 1)

**Story ID:** US-002A
**Epic:** [EPIC-001 - Account Management & Double-Entry Foundation](../../epics/epic-01-account-management.md)
**Status:** ✅ Ready for Sprint 2 (Tech Lead Approved)
**Priority:** P0 (Must Have - Blocking)
**Story Points:** 8
**Sprint:** Sprint 2
**Assignee:** Backend Developer (Primary), Frontend Developer (Support Day 8-9)
**Created:** October 22, 2025
**Updated:** October 22, 2025 (Tech Lead Review Complete)
**Tech Lead Review:** ✅ Approved with corrections applied
**Related Stories:** US-002B (Balanced Transaction Groups)

---

## 📖 User Story

**As a** power user tracking my finances
**I want** every transaction to be recorded with professional double-entry accuracy
**So that** I can trust my financial reports and account balances are always correct

**Technical Implementation:** This story establishes the journal entry foundation that enables double-entry accounting behind the scenes, without adding complexity to the user interface.

---

## 🎯 Business Value

- **Professional Accuracy:** Maintains accounting integrity behind the scenes
- **Audit Trail:** Every balance change is traceable through journal entries
- **Foundation for Features:** Enables transfers, reconciliation, and accounting reports (US-002B)
- **Data Integrity:** Prevents data corruption through automatic validation
- **User Trust:** Users can trust their financial data is always accurate

**Scope:** This story (Phase 1) focuses on the backend foundation - database tables, models, and single-entry journal creation. Multi-entry balanced transactions and transfers are in US-002B (Phase 2).

---

## ✅ Acceptance Criteria

### AC1: Journal Entry Creation (Backend)
**Given** any account balance changes
**When** the change occurs (single transaction or adjustment)
**Then** a corresponding journal entry must be created
**And** the journal entry must have either debit OR credit amount (not both)
**And** the entry must update the account's cached balance
**And** the database triggers must handle the balance update automatically

**Note:** Multi-entry balanced transactions (transfers) are in US-002B.

### AC2: Balance Integrity (Backend)
**Given** an account exists with journal entries
**When** I query the account balance
**Then** the cached balance in accounts table must equal the sum of journal entries
**And** calculated_balance = SUM(debit_amount - credit_amount) for that account
**And** validation function confirms balance within 1 cent tolerance

### AC3: Running Balance (Backend)
**Given** journal entries are ordered by date
**When** I query journal entries for an account
**Then** each entry shows the running balance_after amount
**And** the final entry's balance_after equals the current account balance

### AC4: Database Constraints (Backend)
**Given** I attempt to create an invalid journal entry
**When** the entry violates rules (negative amount, both debit and credit, zero amount)
**Then** the database trigger must reject it with clear error
**And** no partial data is saved (transaction rollback)

### AC5: User Experience (Frontend)
**Given** I create a new transaction in the UI
**When** I save it
**Then** I should NOT see any double-entry complexity (technical details hidden)
**And** the transaction should appear in my account immediately
**And** the account balance should update correctly
**And** the UI should feel exactly the same as before (no regression)

**Note:** This ensures the technical foundation doesn't disrupt the user experience.

---

## 🔧 Technical Implementation

**⚠️ TECH LEAD NOTE:** This story (US-002A) focuses ONLY on single-entry journal foundation. TransactionGroup and balanced multi-entry transactions are deferred to US-002B.

**Migration File:** `/finance_app/data/migrations/002_create_journal_entries.sql`
**Integration Tests:** `/finance_app/tests/integration/test_journal_triggers.py`

### New Database Tables

```sql
-- Migration: 002_create_journal_entries.sql
-- Full migration file available at: finance_app/data/migrations/002_create_journal_entries.sql

-- Journal entries (double-entry ledger)
CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER,  -- Links to transactions table (nullable for non-transaction entries)
    group_id INTEGER,  -- Links to transaction_groups for multi-entry transactions
    account_id INTEGER NOT NULL,
    entry_date TEXT NOT NULL,  -- YYYY-MM-DD
    description TEXT NOT NULL,
    debit_amount REAL NOT NULL DEFAULT 0.0,
    credit_amount REAL NOT NULL DEFAULT 0.0,
    balance_after REAL NOT NULL,  -- Running balance after this entry
    entry_type TEXT NOT NULL,  -- 'transaction', 'opening_balance', 'adjustment', 'transfer'
    reference_number TEXT,  -- Check number, invoice number, etc.
    is_reconciled BOOLEAN DEFAULT 0,
    reconciliation_id INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES transaction_groups (id) ON DELETE CASCADE,
    FOREIGN KEY (reconciliation_id) REFERENCES reconciliations (id)
);

CREATE INDEX idx_journal_account ON journal_entries(account_id);
CREATE INDEX idx_journal_date ON journal_entries(entry_date DESC);
CREATE INDEX idx_journal_transaction ON journal_entries(transaction_id);
CREATE INDEX idx_journal_group ON journal_entries(group_id);
CREATE INDEX idx_journal_reconciled ON journal_entries(is_reconciled);
CREATE INDEX idx_journal_type ON journal_entries(entry_type);

-- Trigger: Validate journal entry constraints
CREATE TRIGGER validate_journal_entry
BEFORE INSERT ON journal_entries
BEGIN
    -- Cannot have both debit and credit
    SELECT CASE
        WHEN NEW.debit_amount > 0 AND NEW.credit_amount > 0 THEN
            RAISE(ABORT, 'Journal entry cannot have both debit and credit amounts')
        WHEN NEW.debit_amount = 0 AND NEW.credit_amount = 0 THEN
            RAISE(ABORT, 'Journal entry must have either debit or credit amount')
        WHEN NEW.debit_amount < 0 OR NEW.credit_amount < 0 THEN
            RAISE(ABORT, 'Debit and credit amounts must be non-negative')
    END;
END;

-- Trigger: Update account balance when journal entry added
CREATE TRIGGER update_account_balance_on_insert
AFTER INSERT ON journal_entries
BEGIN
    UPDATE accounts
    SET balance = balance + (NEW.debit_amount - NEW.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.account_id;
END;

-- Trigger: Reverse account balance when journal entry deleted
CREATE TRIGGER update_account_balance_on_delete
AFTER DELETE ON journal_entries
BEGIN
    UPDATE accounts
    SET balance = balance - (OLD.debit_amount - OLD.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.account_id;
END;

-- Trigger: Adjust account balance when journal entry updated
CREATE TRIGGER update_account_balance_on_update
AFTER UPDATE ON journal_entries
BEGIN
    UPDATE accounts
    SET balance = balance - (OLD.debit_amount - OLD.credit_amount) + (NEW.debit_amount - NEW.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.account_id;
END;
```

### New Data Models

```python
# File: finance_app/data/models.py

from enum import Enum

class EntryType(str, Enum):
    """Journal entry types."""
    TRANSACTION = 'transaction'
    OPENING_BALANCE = 'opening_balance'
    ADJUSTMENT = 'adjustment'
    TRANSFER = 'transfer'
    CLOSING = 'closing'


@dataclass
class JournalEntry:
    """Double-entry journal entry."""
    id: Optional[int]
    transaction_id: Optional[int]
    group_id: Optional[int]
    account_id: int
    entry_date: str  # YYYY-MM-DD
    description: str
    debit_amount: Decimal
    credit_amount: Decimal
    balance_after: Decimal
    entry_type: EntryType
    reference_number: Optional[str] = None
    is_reconciled: bool = False
    reconciliation_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate journal entry."""
        # Convert to Decimal
        if not isinstance(self.debit_amount, Decimal):
            self.debit_amount = Decimal(str(self.debit_amount))
        if not isinstance(self.credit_amount, Decimal):
            self.credit_amount = Decimal(str(self.credit_amount))
        if not isinstance(self.balance_after, Decimal):
            self.balance_after = Decimal(str(self.balance_after))

        # Convert to enum
        if isinstance(self.entry_type, str):
            self.entry_type = EntryType(self.entry_type)

        # Validate amounts
        if self.debit_amount < 0 or self.credit_amount < 0:
            raise ValueError("Debit and credit amounts must be non-negative")
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValueError("Cannot have both debit and credit in same entry")
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValueError("Must have either debit or credit amount")

    @property
    def amount(self) -> Decimal:
        """Get the entry amount (positive for debit, negative for credit)."""
        return self.debit_amount - self.credit_amount

    @property
    def is_debit(self) -> bool:
        """Check if this is a debit entry."""
        return self.debit_amount > 0

    @property
    def is_credit(self) -> bool:
        """Check if this is a credit entry."""
        return self.credit_amount > 0


**⚠️ TECH LEAD NOTE:** TransactionGroup model is NOT in US-002A scope. Moved to US-002B.
```

### Repository Layer

```python
# File: finance_app/data/repositories/journal_entry_repository.py

class JournalEntryRepository:
    """Repository for journal entry data access."""

    def __init__(self, database: Database):
        self.db = database

    def create(self, entry: JournalEntry) -> JournalEntry:
        """
        Create a single journal entry.

        Args:
            entry: JournalEntry to create

        Returns:
            Created journal entry with ID

        Raises:
            DatabaseError: If creation fails
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO journal_entries (
                        transaction_id, group_id, account_id, entry_date,
                        description, debit_amount, credit_amount, balance_after,
                        entry_type, reference_number, notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.transaction_id,
                    entry.group_id,
                    entry.account_id,
                    entry.entry_date,
                    entry.description,
                    float(entry.debit_amount),
                    float(entry.credit_amount),
                    float(entry.balance_after),
                    entry.entry_type.value,
                    entry.reference_number,
                    entry.notes
                ))
                entry.id = cursor.lastrowid
                logger.info(f"Created journal entry: {entry.id} for account {entry.account_id}")
                return entry
        except sqlite3.Error as e:
            logger.error(f"Failed to create journal entry: {e}")
            raise DatabaseError(f"Failed to create journal entry: {e}") from e

    # ⚠️ TECH LEAD NOTE: create_balanced_group() is US-002B scope, not US-002A
    # Deferred to US-002B: Balanced Transaction Groups

    def get_by_account(
        self,
        account_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_reconciled: bool = True
    ) -> List[JournalEntry]:
        """Get journal entries for an account."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                query = """
                    SELECT id, transaction_id, group_id, account_id, entry_date,
                           description, debit_amount, credit_amount, balance_after,
                           entry_type, reference_number, is_reconciled,
                           reconciliation_id, notes, created_at, updated_at
                    FROM journal_entries
                    WHERE account_id = ?
                """
                params = [account_id]

                if start_date:
                    query += " AND entry_date >= ?"
                    params.append(start_date)

                if end_date:
                    query += " AND entry_date <= ?"
                    params.append(end_date)

                if not include_reconciled:
                    query += " AND is_reconciled = 0"

                query += " ORDER BY entry_date ASC, id ASC"

                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [self._row_to_journal_entry(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Failed to fetch journal entries: {e}")
            raise DatabaseError(f"Failed to fetch journal entries: {e}") from e

    def get_account_balance(self, account_id: int) -> Decimal:
        """
        Calculate account balance from journal entries.

        Args:
            account_id: Account ID

        Returns:
            Calculated balance
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT SUM(debit_amount - credit_amount)
                    FROM journal_entries
                    WHERE account_id = ?
                """, (account_id,))
                result = cursor.fetchone()[0]
                return Decimal(str(result)) if result else Decimal('0.0')

        except sqlite3.Error as e:
            logger.error(f"Failed to calculate account balance: {e}")
            raise DatabaseError(f"Failed to calculate account balance: {e}") from e

    @staticmethod
    def _row_to_journal_entry(row: sqlite3.Row) -> JournalEntry:
        """Convert database row to JournalEntry object."""
        return JournalEntry(
            id=row['id'],
            transaction_id=row['transaction_id'],
            group_id=row['group_id'],
            account_id=row['account_id'],
            entry_date=row['entry_date'],
            description=row['description'],
            debit_amount=Decimal(str(row['debit_amount'])),
            credit_amount=Decimal(str(row['credit_amount'])),
            balance_after=Decimal(str(row['balance_after'])),
            entry_type=EntryType(row['entry_type']),
            reference_number=row['reference_number'],
            is_reconciled=bool(row['is_reconciled']),
            reconciliation_id=row['reconciliation_id'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
```

### Service Layer

```python
# File: finance_app/business/double_entry_service.py

class DoubleEntryService:
    """Service for double-entry accounting operations."""

    def __init__(self, database: Database):
        self.db = database
        self.journal_repo = JournalEntryRepository(database)
        self.account_repo = AccountRepository(database)

    def create_simple_transaction(
        self,
        account: Account,
        amount: Decimal,
        description: str,
        date: str,
        is_increase: bool,
        entry_type: EntryType = EntryType.TRANSACTION,
        reference_number: Optional[str] = None
    ) -> JournalEntry:
        """
        Create a simple single-entry journal entry.

        For now, this creates only the account-side entry.
        The offsetting entry (to Income/Expense) will be created
        when we implement full transaction management.

        Args:
            account: Account to affect
            amount: Transaction amount (positive)
            description: Entry description
            date: Entry date (YYYY-MM-DD)
            is_increase: True to increase account, False to decrease
            entry_type: Type of entry
            reference_number: Optional reference

        Returns:
            Created journal entry
        """
        if amount <= 0:
            raise ValidationError("Amount must be positive")

        # Determine debit/credit based on normal balance and direction
        if is_increase:
            # Increase account
            if account.normal_balance == NormalBalance.DEBIT:
                debit_amount = amount
                credit_amount = Decimal('0')
            else:
                debit_amount = Decimal('0')
                credit_amount = amount
        else:
            # Decrease account
            if account.normal_balance == NormalBalance.DEBIT:
                debit_amount = Decimal('0')
                credit_amount = amount
            else:
                debit_amount = amount
                credit_amount = Decimal('0')

        # Create journal entry
        entry = JournalEntry(
            id=None,
            transaction_id=None,
            group_id=None,
            account_id=account.id,
            entry_date=date,
            description=description,
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            balance_after=Decimal('0'),  # Will be calculated by repository
            entry_type=entry_type,
            reference_number=reference_number
        )

        return self.journal_repo.create(entry)

    def validate_account_balance(self, account_id: int) -> dict:
        """
        Validate account balance matches journal entries.

        Args:
            account_id: Account ID

        Returns:
            Dict with validation results
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account {account_id} not found")

        calculated_balance = self.journal_repo.get_account_balance(account_id)
        cached_balance = account.balance

        difference = abs(cached_balance - calculated_balance)
        is_valid = difference < Decimal('0.01')  # Allow 1 cent rounding

        return {
            'account_id': account_id,
            'account_name': account.name,
            'cached_balance': cached_balance,
            'calculated_balance': calculated_balance,
            'difference': difference,
            'is_valid': is_valid
        }
```

---

## 🧪 Test Scenarios

### Test 1: Create Journal Entry
```python
def test_create_journal_entry(journal_repo, test_account):
    """Test creating a single journal entry."""
    entry = JournalEntry(
        id=None,
        account_id=test_account.id,
        entry_date="2025-10-22",
        description="Test entry",
        debit_amount=Decimal("100.00"),
        credit_amount=Decimal("0"),
        balance_after=Decimal("100.00"),
        entry_type=EntryType.TRANSACTION
    )

    created = journal_repo.create(entry)

    assert created.id is not None
    assert created.debit_amount == Decimal("100.00")
    assert created.credit_amount == Decimal("0")
```

### Test 2: Balanced Transaction Group
```python
def test_create_balanced_transaction_group(journal_repo, checking_account, income_account):
    """Test creating balanced journal entries (income transaction)."""
    group = TransactionGroup(
        id=None,
        group_date="2025-10-22",
        description="Salary deposit"
    )

    entries = [
        JournalEntry(  # Debit: Checking (increase asset)
            account_id=checking_account.id,
            entry_date="2025-10-22",
            description="Salary deposit",
            debit_amount=Decimal("5000.00"),
            credit_amount=Decimal("0"),
            entry_type=EntryType.TRANSACTION
        ),
        JournalEntry(  # Credit: Income (increase income)
            account_id=income_account.id,
            entry_date="2025-10-22",
            description="Salary deposit",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("5000.00"),
            entry_type=EntryType.TRANSACTION
        )
    ]

    created_group, created_entries = journal_repo.create_balanced_group(entries, group)

    assert created_group.id is not None
    assert len(created_entries) == 2
    assert all(e.id is not None for e in created_entries)
    assert all(e.group_id == created_group.id for e in created_entries)
```

### Test 3: Reject Unbalanced Entries
```python
def test_reject_unbalanced_entries(journal_repo, checking_account, expense_account):
    """Test that unbalanced entries are rejected."""
    group = TransactionGroup(
        id=None,
        group_date="2025-10-22",
        description="Unbalanced transaction"
    )

    entries = [
        JournalEntry(
            account_id=checking_account.id,
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            ...
        ),
        JournalEntry(
            account_id=expense_account.id,
            debit_amount=Decimal("0"),
            credit_amount=Decimal("50.00"),  # Unbalanced!
            ...
        )
    ]

    with pytest.raises(ValidationError) as exc_info:
        journal_repo.create_balanced_group(entries, group)

    assert "not balanced" in str(exc_info.value).lower()
```

### Test 4: Balance Validation
```python
def test_account_balance_validation(double_entry_service, test_account):
    """Test that cached balance matches calculated balance."""
    # Create several journal entries
    for i in range(5):
        double_entry_service.create_simple_transaction(
            account=test_account,
            amount=Decimal("100.00"),
            description=f"Entry {i}",
            date="2025-10-22",
            is_increase=True
        )

    # Validate balance
    result = double_entry_service.validate_account_balance(test_account.id)

    assert result['is_valid'] is True
    assert result['cached_balance'] == result['calculated_balance']
    assert result['difference'] < Decimal('0.01')
```

### Test 5: Running Balance
```python
def test_running_balance_calculation(journal_repo, test_account):
    """Test that balance_after is correctly calculated for each entry."""
    entries = journal_repo.get_by_account(test_account.id)

    # Verify running balance
    for i, entry in enumerate(entries):
        if i == 0:
            expected_balance = entry.amount
        else:
            expected_balance = entries[i-1].balance_after + entry.amount

        assert entry.balance_after == expected_balance
```

---

## 📋 Tasks Breakdown (US-002A: Phase 1 Only)

- [ ] **Task 2A.1:** Create journal_entries table migration (2 hours)
- [ ] **Task 2A.2:** Create database triggers for balance updates (2 hours)
- [ ] **Task 2A.3:** Create JournalEntry model with validation (2 hours)
- [ ] **Task 2A.4:** Create JournalEntryRepository (basic CRUD) (4 hours)
- [ ] **Task 2A.5:** Create DoubleEntryService (single-entry operations) (3 hours)
- [ ] **Task 2A.6:** Update TransactionService to create journal entries (3 hours)
- [ ] **Task 2A.7:** Write unit tests for JournalEntry model (2 hours)
- [ ] **Task 2A.8:** Write unit tests for repository (3 hours)
- [ ] **Task 2A.9:** Write integration tests for single-entry flow (3 hours)
- [ ] **Task 2A.10:** Add balance validation functionality (2 hours)
- [ ] **Task 2A.11:** Performance testing with 10k+ entries (2 hours)
- [ ] **Task 2A.12:** Documentation and examples (2 hours)

**Total Estimated Time:** 30 hours (approx. 4 days = 8 story points)

**Deferred to US-002B:**
- Transaction groups table
- TransactionGroup model
- Balanced multi-entry transactions
- Transfer functionality

---

## 🔗 Dependencies

### Blocked By
- ✅ US-001 (Account Type Taxonomy) - COMPLETED - provides account types and normal_balance

### Blocks
- US-002B (Balanced Transaction Groups) - needs journal entry foundation from this story
- US-003 (Normal Balance Calculation) - needs journal entry logic
- US-004 (Opening Balances) - needs journal entries
- US-005 (Account Reconciliation) - needs journal entry tracking

---

## ✅ Definition of Done

### Database & Schema
- [ ] journal_entries table created with migration script
- [ ] trigger_audit table created (for debugging)
- [ ] Database triggers working correctly (insert/update/delete balance updates)
- [ ] Composite index added (account_id, entry_date)
- [ ] Migration rollback script tested
- [ ] Foreign key constraints enforced

### Code Implementation
- [ ] JournalEntry model implemented with validation
- [ ] EntryType enum implemented
- [ ] JournalEntryRepository CRUD operations complete
- [ ] balance_after calculated correctly (before insert)
- [ ] Transaction isolation implemented (BEGIN IMMEDIATE)
- [ ] DoubleEntryService single-entry operations working
- [ ] TransactionService updated to create journal entries
- [ ] Balance validation function working correctly
- [ ] Decimal arithmetic handled correctly (no float precision errors)

### Testing
- [ ] All unit tests passing (15+ tests for models/repository)
- [ ] Integration tests passing (12+ tests for triggers)
- [ ] Trigger integration tests passing (test_journal_triggers.py)
- [ ] Backward compatibility verified (old transactions still work)
- [ ] Race condition testing (concurrent inserts)
- [ ] Rollback testing (failed operations don't corrupt data)
- [ ] Performance test: Query 10,000 journal entries in < 500ms ✅
- [ ] Performance test: Balance calculation from 10k entries < 100ms ✅

### Quality & Review
- [ ] No regression in existing transaction creation UI
- [ ] Code reviewed and approved by tech lead
- [ ] All code review feedback addressed
- [ ] Logging added for debugging
- [ ] Error handling robust and clear
- [ ] No technical debt added

### Documentation
- [ ] ARCHITECTURE.md updated with journal entry system
- [ ] Trigger behavior documented
- [ ] Migration notes added
- [ ] Code examples provided
- [ ] Manual testing: Create transaction and verify journal entry created

### Tech Lead Sign-Off
- [ ] Database design approved
- [ ] Code quality meets standards
- [ ] Test coverage adequate
- [ ] Performance benchmarks met
- [ ] Ready for production

---

## 📚 References

- [Epic 01: Account Management](../epics/epic-01-account-management.md)
- [PRD: Feature #2 - Double-Entry Accounting](../prd.md#2-double-entry-accounting-system)
- [Accounting Equation](https://en.wikipedia.org/wiki/Accounting_equation)
- [Double-Entry Bookkeeping](https://en.wikipedia.org/wiki/Double-entry_bookkeeping)

---

**Story Created:** October 22, 2025
**Story Started:** TBD
**Story Completed:** TBD
