# US-002B: Balanced Transaction Groups (Double-Entry Phase 2)

**Story ID:** US-002B
**Epic:** [EPIC-001 - Account Management & Double-Entry Foundation](../../epics/epic-01-account-management.md)
**Status:** 📋 Backlog
**Priority:** P0 (Must Have - Blocking)
**Story Points:** 5
**Sprint:** Sprint 2 or 3
**Assignee:** TBD
**Created:** October 22, 2025
**Related Stories:** US-002A (Journal Entry Foundation) - DEPENDENCY

---

## 📖 User Story

**As a** power user managing transfers between accounts
**I want** transfers to be automatically balanced (debit one account, credit another)
**So that** my books always balance and I can track money movement accurately

**Technical Implementation:** This story builds on US-002A to enable multi-entry balanced transactions, including transfers, split transactions, and complex journal entries.

---

## 🎯 Business Value

- **Account Transfers:** Enable moving money between accounts with perfect accuracy
- **Split Transactions:** Support transactions affecting multiple accounts
- **Accounting Balance:** Guarantee debits always equal credits
- **Financial Integrity:** Prevent unbalanced books through validation
- **Advanced Workflows:** Foundation for paycheck splits, bill payments, etc.

**Scope:** This story (Phase 2) adds transaction groups and balanced multi-entry capabilities on top of the foundation built in US-002A.

---

## ✅ Acceptance Criteria

### AC1: Transaction Groups
**Given** I have the journal entry foundation (US-002A complete)
**When** I create a transfer between two accounts
**Then** a transaction group is created linking the journal entries
**And** the group has a date and description
**And** all entries in the group share the same group_id

### AC2: Balanced Multi-Entry Transactions
**Given** I create a transaction with multiple journal entries
**When** the entries are saved
**Then** the sum of all debits must equal the sum of all credits
**And** if unbalanced, the transaction must be rejected with clear error message
**And** no partial data is saved (transaction rollback)

### AC3: Account Transfers
**Given** I want to transfer $500 from Checking to Savings
**When** I initiate the transfer
**Then** two journal entries are created:
  - Debit: Savings +$500 (increase asset)
  - Credit: Checking -$500 (decrease asset)
**And** both entries are in the same transaction group
**And** checking balance decreases by $500
**And** savings balance increases by $500
**And** total debits = total credits = $500

### AC4: Split Transactions (Advanced)
**Given** I receive a $5000 paycheck
**When** I split it into multiple accounts (e.g., 70% Checking, 20% Savings, 10% Investment)
**Then** multiple journal entries are created in one balanced group:
  - Credit: Income -$5000
  - Debit: Checking +$3500
  - Debit: Savings +$1000
  - Debit: Investment +$500
**And** all entries balance (total debits = total credits = $5000)

### AC5: User Experience
**Given** I use the transfer feature in the UI
**When** I complete a transfer
**Then** I see confirmation "Transfer successful"
**And** both account balances update immediately
**And** the transfer appears in both account transaction lists
**And** the UI does NOT expose journal entry complexity (user-friendly)

---

## 🔧 Technical Implementation

### New Database Table

```sql
-- Migration: 003_create_transaction_groups.sql

CREATE TABLE transaction_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_date TEXT NOT NULL,
    description TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT
);

CREATE INDEX idx_transaction_groups_date ON transaction_groups(group_date DESC);

-- Add foreign key constraint to journal_entries (if not already present)
-- ALTER TABLE journal_entries ADD COLUMN group_id INTEGER REFERENCES transaction_groups(id);
```

### New Data Model

```python
# File: finance_app/data/models.py

@dataclass
class TransactionGroup:
    """Group of related journal entries (for transfers, splits)."""
    id: Optional[int]
    group_date: str
    description: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None

    def validate_balance(self, entries: List[JournalEntry]) -> bool:
        """
        Validate that entries in this group balance (debits = credits).

        Args:
            entries: List of journal entries in this group

        Returns:
            True if balanced, False otherwise
        """
        total_debits = sum(e.debit_amount for e in entries)
        total_credits = sum(e.credit_amount for e in entries)
        difference = abs(total_debits - total_credits)

        # Allow for tiny rounding differences (1 cent)
        return difference < Decimal('0.01')

    def get_total_debits(self, entries: List[JournalEntry]) -> Decimal:
        """Get total debit amount."""
        return sum(e.debit_amount for e in entries)

    def get_total_credits(self, entries: List[JournalEntry]) -> Decimal:
        """Get total credit amount."""
        return sum(e.credit_amount for e in entries)
```

### Enhanced Repository

```python
# File: finance_app/data/repositories/journal_entry_repository.py

def create_balanced_group(
    self,
    entries: List[JournalEntry],
    group: TransactionGroup
) -> tuple[TransactionGroup, List[JournalEntry]]:
    """
    Create a group of balanced journal entries atomically.

    Args:
        entries: List of journal entries
        group: Transaction group

    Returns:
        Tuple of (created_group, created_entries)

    Raises:
        ValidationError: If entries are not balanced
        DatabaseError: If creation fails
    """
    # Validate balance
    if not group.validate_balance(entries):
        total_debits = group.get_total_debits(entries)
        total_credits = group.get_total_credits(entries)
        raise ValidationError(
            f"Journal entries not balanced: "
            f"Debits={total_debits}, Credits={total_credits}"
        )

    try:
        with self.db.get_connection() as conn:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            try:
                # Create transaction group
                cursor.execute("""
                    INSERT INTO transaction_groups (group_date, description, notes)
                    VALUES (?, ?, ?)
                """, (group.group_date, group.description, group.notes))
                group.id = cursor.lastrowid

                # Create all journal entries
                created_entries = []
                for entry in entries:
                    entry.group_id = group.id
                    created_entry = self.create(entry)
                    created_entries.append(created_entry)

                conn.commit()
                return group, created_entries

            except Exception as e:
                conn.rollback()
                raise

    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to create journal entry group: {e}") from e
```

### Enhanced Service Layer

```python
# File: finance_app/business/double_entry_service.py

def create_transfer(
    self,
    from_account: Account,
    to_account: Account,
    amount: Decimal,
    description: str,
    date: str,
    reference_number: Optional[str] = None
) -> tuple[TransactionGroup, List[JournalEntry]]:
    """
    Create a transfer between two accounts.

    Args:
        from_account: Source account (will be credited/decreased)
        to_account: Destination account (will be debited/increased)
        amount: Transfer amount (positive)
        description: Transfer description
        date: Transfer date (YYYY-MM-DD)
        reference_number: Optional reference

    Returns:
        Tuple of (transaction_group, journal_entries)

    Raises:
        ValidationError: If amount is invalid or accounts are same
    """
    if amount <= 0:
        raise ValidationError("Transfer amount must be positive")

    if from_account.id == to_account.id:
        raise ValidationError("Cannot transfer to the same account")

    # Create transaction group
    group = TransactionGroup(
        id=None,
        group_date=date,
        description=description
    )

    # Create entries
    entries = [
        # Decrease source account
        self._create_transfer_entry(
            from_account, amount, description, date,
            is_increase=False, reference_number=reference_number
        ),
        # Increase destination account
        self._create_transfer_entry(
            to_account, amount, description, date,
            is_increase=True, reference_number=reference_number
        )
    ]

    # Create balanced group atomically
    return self.journal_repo.create_balanced_group(entries, group)
```

---

## 🧪 Test Scenarios

### Test 1: Simple Transfer
```python
def test_create_transfer(double_entry_service, checking_account, savings_account):
    """Test transferring money between accounts."""
    initial_checking = checking_account.balance
    initial_savings = savings_account.balance

    group, entries = double_entry_service.create_transfer(
        from_account=checking_account,
        to_account=savings_account,
        amount=Decimal("500.00"),
        description="Transfer to savings",
        date="2025-10-22"
    )

    assert group.id is not None
    assert len(entries) == 2

    # Verify balances changed
    checking_updated = account_repo.get_by_id(checking_account.id)
    savings_updated = account_repo.get_by_id(savings_account.id)

    assert checking_updated.balance == initial_checking - Decimal("500.00")
    assert savings_updated.balance == initial_savings + Decimal("500.00")
```

### Test 2: Reject Unbalanced Group
```python
def test_reject_unbalanced_group(journal_repo):
    """Test that unbalanced entries are rejected."""
    group = TransactionGroup(
        id=None,
        group_date="2025-10-22",
        description="Unbalanced"
    )

    entries = [
        JournalEntry(debit_amount=Decimal("100"), credit_amount=Decimal("0"), ...),
        JournalEntry(debit_amount=Decimal("0"), credit_amount=Decimal("50"), ...)
    ]

    with pytest.raises(ValidationError, match="not balanced"):
        journal_repo.create_balanced_group(entries, group)
```

### Test 3: Split Transaction
```python
def test_split_transaction(double_entry_service, income_account, checking_account,
                          savings_account, investment_account):
    """Test splitting income across multiple accounts."""
    group = TransactionGroup(
        group_date="2025-10-22",
        description="Paycheck split"
    )

    entries = [
        # Credit income
        JournalEntry(
            account_id=income_account.id,
            debit_amount=Decimal("0"),
            credit_amount=Decimal("5000.00"),
            ...
        ),
        # Debit checking (70%)
        JournalEntry(
            account_id=checking_account.id,
            debit_amount=Decimal("3500.00"),
            credit_amount=Decimal("0"),
            ...
        ),
        # Debit savings (20%)
        JournalEntry(
            account_id=savings_account.id,
            debit_amount=Decimal("1000.00"),
            credit_amount=Decimal("0"),
            ...
        ),
        # Debit investment (10%)
        JournalEntry(
            account_id=investment_account.id,
            debit_amount=Decimal("500.00"),
            credit_amount=Decimal("0"),
            ...
        )
    ]

    created_group, created_entries = journal_repo.create_balanced_group(entries, group)

    assert created_group.id is not None
    assert len(created_entries) == 4
    assert group.validate_balance(created_entries) is True
```

---

## 📋 Tasks Breakdown

- [ ] **Task 2B.1:** Create transaction_groups table migration (1 hour)
- [ ] **Task 2B.2:** Create TransactionGroup model (1 hour)
- [ ] **Task 2B.3:** Create TransactionGroupRepository (2 hours)
- [ ] **Task 2B.4:** Enhance JournalEntryRepository with create_balanced_group() (3 hours)
- [ ] **Task 2B.5:** Add transfer functionality to DoubleEntryService (3 hours)
- [ ] **Task 2B.6:** Write unit tests for TransactionGroup (2 hours)
- [ ] **Task 2B.7:** Write integration tests for balanced groups (3 hours)
- [ ] **Task 2B.8:** Write integration tests for transfers (3 hours)
- [ ] **Task 2B.9:** Add UI for transfers (optional - may be separate story) (4 hours)
- [ ] **Task 2B.10:** Documentation and examples (2 hours)

**Total Estimated Time:** 24 hours (approx. 3 days = 5 story points)

**Note:** If UI for transfers is complex, consider splitting into US-007 (Transfer UI)

---

## 🔗 Dependencies

### Blocked By
- US-002A (Journal Entry Foundation) - MUST be completed first

### Blocks
- US-004 (Opening Balances) - needs transfer capability
- US-006 (Account Hierarchy) - may use transfer logic
- Future transfer UI features

---

## ✅ Definition of Done

- [ ] transaction_groups table created with migration
- [ ] TransactionGroup model implemented with balance validation
- [ ] TransactionGroupRepository CRUD operations complete
- [ ] JournalEntryRepository.create_balanced_group() working
- [ ] DoubleEntryService.create_transfer() working
- [ ] All unit tests passing (10+ tests)
- [ ] Integration tests passing (5+ tests)
- [ ] Transfer validation rejects unbalanced entries
- [ ] Atomicity verified (rollback on failure)
- [ ] Code reviewed and approved by tech lead
- [ ] Documentation complete with transfer examples
- [ ] Manual testing: Transfer between accounts successful

---

## 📚 References

- [Epic 01: Account Management](../../epics/epic-01-account-management.md)
- [US-002A: Journal Entry Foundation](US-002A-journal-entry-foundation.md) - Prerequisite
- [PRD: Feature #2 - Double-Entry Accounting](../../prd.md#2-double-entry-accounting-system)
- [Double-Entry Bookkeeping](https://en.wikipedia.org/wiki/Double-entry_bookkeeping)

---

**Story Created:** October 22, 2025
**Dependencies:** US-002A must be completed first
**Estimated Start:** Sprint 2 or 3 (after US-002A)
