# US-002B: Balanced Transaction Groups (Double-Entry Phase 2)

**Story ID:** US-002B
**Epic:** [EPIC-001 - Account Management & Double-Entry Foundation](../../epics/epic-01-account-management.md)
**Status:** 📋 Backlog
**Priority:** P0 (Must Have - Blocking)
**Story Points:** 8
**Sprint:** Sprint 3
**Assignee:** TBD
**Created:** October 22, 2025
**Related Stories:** US-002A (Journal Entry Foundation) - DEPENDENCY

---

## 📖 User Story

**As a** finance app user
**I want** my existing account balances to have journal entries AND support transfers between accounts
**So that** my journal is complete from day one and I can track money movement accurately

**Technical Implementation:** This story builds on US-002A to:
1. Migrate existing account balances to opening balance journal entries
2. Enable balanced multi-entry transactions (transfers)
3. Provide validation tools to ensure data integrity

---

## 🎯 Business Value

- **Complete Journal History:** Existing accounts get opening balance entries for full audit trail
- **Account Transfers:** Enable moving money between accounts with perfect accuracy
- **Accounting Balance:** Guarantee debits always equal credits
- **Financial Integrity:** Prevent unbalanced books through validation
- **Data Migration Safety:** Automated migration with validation tools

**Scope:** This story (Phase 2) migrates existing balances to journal entries and adds transaction groups for balanced multi-entry capabilities on top of the foundation built in US-002A.

---

## 📝 Story Refinement Notes

**Refinement Date:** October 22, 2025
**Reviewed By:** Tech Lead

### Changes Made During Refinement:
1. **ADDED:** AC1 - Opening Balance Migration (CRITICAL - was missing)
2. **REMOVED:** AC4 - Split Transactions (deferred to US-002C)
3. **UPDATED:** Story points from 5 to 8 (added 16 hours for migration work)
4. **UPDATED:** User story to include opening balance migration
5. **ADDED:** Opening balance migration technical implementation section
6. **ADDED:** 9 new tasks for migration work (Phase 1)
7. **UPDATED:** Definition of Done with migration criteria
8. **ADDED:** Migration test scenarios

### Rationale:
- **Opening balance migration is ESSENTIAL** for Sprint 3 because without it, journal entries don't exist for existing account balances, making the journal incomplete
- **Split transactions add complexity** and should be deferred to keep this story focused on core foundation
- **Story points increased** to reflect additional scope (migration = 2 points, transfer UI = 2 points)

### Deferred to Future Stories:
- **US-002C:** Split Transactions (paycheck splits, bill splits)
- **US-007:** Advanced Transfer UI (may be combined with Phase 4 if needed)

---

## ✅ Acceptance Criteria

### AC1: Opening Balance Migration (CRITICAL)
**Given** I have existing accounts with non-zero balances (from US-001)
**When** I run the opening balance migration script
**Then** a journal entry is created for each account's current balance
**And** the entry type is OPENING
**And** the entry date is the account creation date (or migration date if unknown)
**And** for Asset accounts with positive balance: debit journal entry
**And** for Liability accounts with positive balance: credit journal entry
**And** after migration, `scripts/validate_balances.py` shows all accounts VALID
**And** the journal balance matches the account table balance for every account

### AC2: Transaction Groups
**Given** I have the journal entry foundation (US-002A complete)
**When** I create a transfer between two accounts
**Then** a transaction group is created linking the journal entries
**And** the group has a date and description
**And** all entries in the group share the same group_id

### AC3: Balanced Multi-Entry Transactions
**Given** I create a transaction with multiple journal entries
**When** the entries are saved
**Then** the sum of all debits must equal the sum of all credits
**And** if unbalanced, the transaction must be rejected with clear error message
**And** no partial data is saved (transaction rollback)

### AC4: Account Transfers
**Given** I want to transfer $500 from Checking to Savings
**When** I initiate the transfer
**Then** two journal entries are created:
  - Debit: Savings +$500 (increase asset)
  - Credit: Checking -$500 (decrease asset)
**And** both entries are in the same transaction group
**And** checking balance decreases by $500
**And** savings balance increases by $500
**And** total debits = total credits = $500

### AC5: User Experience (Transfer UI)
**Given** I use the transfer feature in the UI
**When** I complete a transfer
**Then** I see confirmation "Transfer successful"
**And** both account balances update immediately
**And** the transfer appears in both account transaction lists
**And** the UI does NOT expose journal entry complexity (user-friendly)

---

## 🔧 Technical Implementation

### Opening Balance Migration

**Migration Script:** `scripts/migrate_opening_balances.py`

```python
#!/usr/bin/env python3
"""
Migrate existing account balances to opening balance journal entries.

Usage:
    python scripts/migrate_opening_balances.py [--dry-run] [--date YYYY-MM-DD]

This script creates OPENING journal entries for all accounts with non-zero balances.
"""
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from finance_app.data.database import Database
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.business.double_entry_service import DoubleEntryService
from finance_app.data.models import EntryType

def migrate_opening_balances(dry_run: bool = False, opening_date: str = None):
    """
    Create opening balance journal entries for all accounts.

    Args:
        dry_run: If True, only print what would be done
        opening_date: Date for opening entries (default: today)
    """
    db = Database()
    account_repo = AccountRepository(db)
    double_entry_service = DoubleEntryService(db)

    if opening_date is None:
        opening_date = datetime.now().strftime("%Y-%m-%d")

    print(f"\n{'DRY RUN: ' if dry_run else ''}Migrating opening balances...")
    print(f"Opening balance date: {opening_date}\n")

    accounts = account_repo.get_all()
    migrated_count = 0
    skipped_count = 0

    for account in accounts:
        if account.balance == Decimal("0"):
            print(f"  SKIP: {account.name} (zero balance)")
            skipped_count += 1
            continue

        print(f"  {'WOULD CREATE' if dry_run else 'CREATING'}: {account.name} "
              f"opening balance = ${account.balance}")

        if not dry_run:
            # Create opening balance journal entry
            entry = double_entry_service.create_simple_transaction(
                account_id=account.id,
                amount=abs(account.balance),
                date=opening_date,
                description=f"Opening balance for {account.name}",
                entry_type=EntryType.OPENING,
                transaction_id=None,  # Opening balances don't link to transactions
                reference_number="OPENING-BALANCE",
                notes="Automatically created by opening balance migration"
            )
            print(f"    ✓ Created journal entry {entry.id}")
            migrated_count += 1
        else:
            migrated_count += 1

    print(f"\n{'DRY RUN ' if dry_run else ''}Summary:")
    print(f"  Accounts migrated: {migrated_count}")
    print(f"  Accounts skipped: {skipped_count}")
    print(f"  Total accounts: {len(accounts)}")

    if not dry_run:
        print("\n✓ Migration complete!")
        print("Run: python scripts/validate_balances.py to verify")

    return migrated_count, skipped_count

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrate opening balances")
    parser.add_argument("--dry-run", action="store_true",
                       help="Print what would be done without making changes")
    parser.add_argument("--date", type=str,
                       help="Opening balance date (default: today)")

    args = parser.parse_args()

    migrate_opening_balances(dry_run=args.dry_run, opening_date=args.date)
```

**Validation After Migration:**
```bash
# Verify all accounts balanced
python scripts/validate_balances.py

# Expected output:
# ✓ All accounts valid (100%)
```

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

### Test 3: Opening Balance Migration
```python
def test_migrate_opening_balances(account_repo, journal_repo, double_entry_service):
    """Test creating opening balance journal entries."""
    # Create accounts with balances
    checking = create_account(name="Checking", balance=Decimal("1000.00"))
    savings = create_account(name="Savings", balance=Decimal("5000.00"))
    zero_account = create_account(name="Zero", balance=Decimal("0"))

    # Run migration
    from scripts.migrate_opening_balances import migrate_opening_balances
    migrated, skipped = migrate_opening_balances(
        dry_run=False,
        opening_date="2025-01-01"
    )

    assert migrated == 2  # Checking and Savings
    assert skipped == 1   # Zero account

    # Verify journal entries created
    checking_entries = journal_repo.get_by_account(checking.id)
    assert len(checking_entries) == 1
    assert checking_entries[0].entry_type == EntryType.OPENING
    assert checking_entries[0].debit_amount == Decimal("1000.00")

    # Verify balances match
    from finance_app.utils.admin_tools import AdminTools
    admin = AdminTools(db)
    results = admin.validate_all_account_balances()
    assert all(r.is_valid for r in results)
```

---

## 📋 Tasks Breakdown

### Phase 1: Opening Balance Migration (Days 1-3, 16 hours)
- [ ] **Task 2B.1:** Create opening balance migration script (`scripts/migrate_opening_balances.py`) (3 hours)
- [ ] **Task 2B.2:** Add --dry-run flag for safe testing (1 hour)
- [ ] **Task 2B.3:** Write unit tests for migration script (3 hours)
- [ ] **Task 2B.4:** Integration test: Migrate real data and validate (2 hours)
- [ ] **Task 2B.5:** Run migration on production data (with backup) (1 hour)
- [ ] **Task 2B.6:** Validate all accounts with `scripts/validate_balances.py` (1 hour)
- [ ] **Task 2B.7:** Document migration process in story (1 hour)
- [ ] **Task 2B.8:** Add rollback instructions if needed (1 hour)
- [ ] **Task 2B.9:** Handle edge cases (negative balances, equity accounts) (3 hours)

**Day 3 Checkpoint:** All accounts have opening balance journal entries, validation passes 100%

### Phase 2: Transaction Groups (Days 4-5, 12 hours)
- [ ] **Task 2B.10:** Create transaction_groups table migration (1 hour)
- [ ] **Task 2B.11:** Create TransactionGroup model with balance validation (2 hours)
- [ ] **Task 2B.12:** Create TransactionGroupRepository (2 hours)
- [ ] **Task 2B.13:** Enhance JournalEntryRepository with create_balanced_group() (3 hours)
- [ ] **Task 2B.14:** Write unit tests for TransactionGroup model (2 hours)
- [ ] **Task 2B.15:** Write integration tests for balanced groups (2 hours)

### Phase 3: Transfer Service (Days 6-7, 12 hours)
- [ ] **Task 2B.16:** Add create_transfer() to DoubleEntryService (3 hours)
- [ ] **Task 2B.17:** Add validation (same account, negative amount) (1 hour)
- [ ] **Task 2B.18:** Write unit tests for transfer service (3 hours)
- [ ] **Task 2B.19:** Write integration tests for transfers (3 hours)
- [ ] **Task 2B.20:** Test edge cases (zero balance accounts, large transfers) (2 hours)

### Phase 4: Transfer UI (Day 8, 8 hours - OPTIONAL)
- [ ] **Task 2B.21:** Create TransferDialog UI component (3 hours)
- [ ] **Task 2B.22:** Add account selection dropdowns (2 hours)
- [ ] **Task 2B.23:** Add "Transfer" button to main window (1 hour)
- [ ] **Task 2B.24:** Manual UI testing (2 hours)

**Total Estimated Time:** 48 hours (6 days implementation + 2 days buffer = 8 story points)

**Note:** Phase 4 (Transfer UI) can be deferred to US-007 if time is tight. Core backend work (Phases 1-3) is 40 hours = 5 points.

---

## 🔗 Dependencies

### Blocked By
- US-002A (Journal Entry Foundation) - MUST be completed first
  - Requires: JournalEntry model, JournalEntryRepository, DoubleEntryService
  - Requires: EntryType.OPENING enum value
  - Requires: Database triggers for balance updates

### Blocks
- US-002C (Split Transactions) - deferred advanced feature
- US-006 (Account Hierarchy) - may use transfer logic
- Future transfer UI features

### Notes
- Opening balance migration (previously US-004) is now included in this story
- Split transactions deferred to US-002C to keep this story focused

---

## ✅ Definition of Done

### Phase 1: Opening Balance Migration
- [ ] `scripts/migrate_opening_balances.py` created and tested
- [ ] --dry-run flag works correctly
- [ ] Migration creates OPENING journal entries for all non-zero accounts
- [ ] `scripts/validate_balances.py` shows 100% valid after migration
- [ ] Migration unit tests passing (5+ tests)
- [ ] Migration integration test passing
- [ ] Edge cases handled (negative balances, equity accounts)
- [ ] Rollback instructions documented

### Phase 2: Transaction Groups
- [ ] transaction_groups table created with migration
- [ ] TransactionGroup model implemented with balance validation
- [ ] TransactionGroupRepository CRUD operations complete
- [ ] JournalEntryRepository.create_balanced_group() working
- [ ] Unit tests passing (10+ tests for groups)
- [ ] Integration tests passing (5+ tests for balanced groups)
- [ ] Atomicity verified (rollback on failure)

### Phase 3: Transfer Service
- [ ] DoubleEntryService.create_transfer() working
- [ ] Transfer validation rejects unbalanced entries
- [ ] Transfer validation rejects same-account transfers
- [ ] Unit tests passing (8+ tests for transfers)
- [ ] Integration tests passing (5+ tests for transfers)
- [ ] Edge cases tested (zero balance, large amounts)

### Phase 4: Transfer UI (OPTIONAL)
- [ ] TransferDialog UI component created
- [ ] "Transfer" button added to main window
- [ ] Manual testing: Transfer between accounts successful
- [ ] UI shows success confirmation

### Overall
- [ ] All tests passing (30+ total tests)
- [ ] Code reviewed and approved by tech lead
- [ ] Documentation complete with examples
- [ ] Performance: Transfers complete < 100ms
- [ ] Zero regression in existing functionality

---

## 📚 References

- [Epic 01: Account Management](../../epics/epic-01-account-management.md)
- [US-002A: Journal Entry Foundation](US-002A-journal-entry-foundation.md) - Prerequisite
- [PRD: Feature #2 - Double-Entry Accounting](../../prd.md#2-double-entry-accounting-system)
- [Double-Entry Bookkeeping](https://en.wikipedia.org/wiki/Double-entry_bookkeeping)

---

**Story Created:** October 22, 2025
**Last Refined:** October 22, 2025 (Tech Lead review - added opening balance migration)
**Dependencies:** US-002A must be completed first
**Estimated Start:** Sprint 3 (after US-002A completion)
**Story Points:** 8 (6 days implementation + 2 days buffer)
**Critical Path:** Opening balance migration → Transaction groups → Transfers → UI
