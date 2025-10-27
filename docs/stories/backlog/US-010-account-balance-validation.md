# US-010: Account Balance Validation & Integrity

**Story ID:** US-010
**Epic:** [EPIC-001: Account Management & Double-Entry Foundation](../../epics/EPIC-001-account-management.md)
**Created:** 2025-10-27
**Status:** Backlog (Ready for Sprint 9)
**Priority:** P0 (Must Have - Critical)
**Story Points:** 8
**Assignee:** Unassigned
**Sprint:** Sprint 9 (Planned)
**Dependencies:** ✅ US-002A (Journal Entry Foundation), ✅ US-002B (Balanced Transaction Groups)

---

## 📖 User Story

**As a** system
**I want** to automatically validate account balances against journal entries
**So that** data integrity is maintained at all times and users can trust their financial data

---

## 📝 Description

### Context

In a double-entry accounting system, account balances MUST equal the sum of their journal entries at all times. Any discrepancy indicates data corruption, programming errors, or manual database manipulation.

This story implements:
1. **Real-time validation** during account operations
2. **Startup validation** when the application loads
3. **Manual validation** via balance validation reports
4. **Automatic repair** of minor discrepancies
5. **Trial balance generation** for accounting integrity

### Problem Statement

Currently:
- ❌ No automatic validation of cached vs calculated balances
- ❌ Potential for data corruption to go undetected
- ❌ No trial balance report
- ❌ No way to verify accounting equation (Assets = Liabilities + Equity)
- ❌ Users can't verify data integrity

This creates risks:
- Silent data corruption
- Inaccurate financial reports
- Loss of user trust
- Difficulty debugging balance issues

### Proposed Solution

Implement **AccountBalanceValidator** service that:
- Validates cached balance = SUM(journal entries) for each account
- Runs validation on app startup
- Provides manual validation tools
- Generates trial balance reports
- Allows 1-cent tolerance for floating-point rounding
- Logs all discrepancies
- Optional automatic repair

---

## 🎯 Acceptance Criteria

### AC1: Single Account Validation

**Given** any account in the system
**When** I validate the account balance
**Then** the validator should:
- Calculate balance from journal entries (SUM of debits - credits)
- Compare to cached balance in accounts table
- Return validation result with details
- Allow 1-cent tolerance for rounding errors
- Mark as VALID if difference < $0.01
- Mark as INVALID if difference >= $0.01

**Example:**
```python
result = validator.validate_account_balance(account_id=123)
assert result.is_valid == True
assert abs(result.difference) < Decimal('0.01')
```

### AC2: All Accounts Validation

**Given** the database contains multiple accounts
**When** I run validate_all_accounts()
**Then** the validator should:
- Validate every account in the system
- Return list of validation results
- Log any discrepancies found
- Complete in < 5 seconds for 10,000 accounts
- Provide summary statistics

**Example:**
```python
results = validator.validate_all_accounts()
failed = [r for r in results if not r.is_valid]
assert len(failed) == 0  # No discrepancies
```

### AC3: Startup Validation

**Given** the application is starting up
**When** the database is loaded
**Then** the system should:
- Automatically validate all account balances
- Log validation summary to console/log file
- Show warning to user if discrepancies found
- Provide option to auto-fix discrepancies
- Continue loading even if validation finds issues

**Example:**
```
[INFO] Validating 47 accounts...
[INFO] Validation complete: 47/47 passed
[SUCCESS] All account balances valid
```

### AC4: Trial Balance Report

**Given** I want to verify accounting integrity
**When** I request a trial balance report
**Then** the system should:
- List all accounts with their balances
- Separate into debit and credit columns
- Calculate total debits
- Calculate total credits
- Verify total debits = total credits
- Flag if unbalanced (error condition)
- Export to CSV/PDF

**Example Trial Balance:**
```
TRIAL BALANCE - October 27, 2025

Account                    | Debit      | Credit
--------------------------------------------------
Checking Account          | $5,000.00  |
Savings Account           | $10,000.00 |
Credit Card               |            | $1,500.00
Opening Balance Equity    |            | $13,500.00
--------------------------------------------------
TOTALS                    | $15,000.00 | $15,000.00

Status: ✅ BALANCED
```

### AC5: Discrepancy Repair

**Given** a validation detects a discrepancy
**When** I run fix_account_balance()
**Then** the system should:
- Recalculate balance from journal entries
- Update accounts.balance to match calculated value
- Log the correction with old/new values
- Create audit trail entry
- Return updated account

**Example:**
```python
# Before: Cached=$1000.00, Calculated=$1000.50
fixed_account = validator.fix_account_balance(account_id=123)
# After: Cached=$1000.50 (matches calculated)
```

### AC6: Database Triggers for Auto-Update

**Given** journal entries are added/modified/deleted
**When** any journal entry operation occurs
**Then** database triggers should:
- Automatically update account.balance
- Maintain balance accuracy
- Prevent manual balance modification
- Update updated_at timestamp

---

## 🔧 Technical Details

### Affected Components

**New Files:**
- `finance_app/business/account_balance_validator.py` - Validation service
- `finance_app/data/models/validation_result.py` - Validation result model
- `finance_app/data/models/trial_balance.py` - Trial balance models
- `finance_app/tests/integration/test_balance_validation.py` - Integration tests
- `finance_app/tests/unit/test_account_balance_validator.py` - Unit tests

**Modified Files:**
- `finance_app/main.py` - Add startup validation
- `finance_app/ui/main_window.py` - Add validation menu item
- `finance_app/ui/dialogs/validation_report_dialog.py` - NEW validation report UI
- `docs/ARCHITECTURE.md` - Document validation system
- `docs/USER_GUIDE.md` - Add validation instructions

### Database Changes

```sql
-- Migration 009: Balance validation triggers

-- Trigger to update account balance when journal entry added
CREATE TRIGGER update_account_balance_on_insert
AFTER INSERT ON journal_entries
BEGIN
    UPDATE accounts
    SET balance = balance + (NEW.debit_amount - NEW.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.account_id;
END;

-- Trigger to update account balance when journal entry updated
CREATE TRIGGER update_account_balance_on_update
AFTER UPDATE ON journal_entries
BEGIN
    UPDATE accounts
    SET balance = balance - (OLD.debit_amount - OLD.credit_amount)
                          + (NEW.debit_amount - NEW.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.account_id;
END;

-- Trigger to update account balance when journal entry deleted
CREATE TRIGGER update_account_balance_on_delete
AFTER DELETE ON journal_entries
BEGIN
    UPDATE accounts
    SET balance = balance - (OLD.debit_amount - OLD.credit_amount),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.account_id;
END;

-- Add validation log table (optional - for audit trail)
CREATE TABLE balance_validation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    cached_balance REAL NOT NULL,
    calculated_balance REAL NOT NULL,
    difference REAL NOT NULL,
    was_repaired BOOLEAN DEFAULT 0,
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

### Implementation Approach

**Step 1: Create Models (1 hour)**
```python
@dataclass
class ValidationResult:
    """Result of validating a single account."""
    account_id: int
    account_name: str
    cached_balance: Decimal
    calculated_balance: Decimal
    difference: Decimal
    is_valid: bool
    validated_at: datetime

    @property
    def severity(self) -> str:
        """Get severity level based on difference."""
        if abs(self.difference) < Decimal('0.01'):
            return 'OK'
        elif abs(self.difference) < Decimal('1.00'):
            return 'MINOR'
        elif abs(self.difference) < Decimal('100.00'):
            return 'MODERATE'
        else:
            return 'CRITICAL'

@dataclass
class TrialBalance:
    """Trial balance report."""
    report_date: str
    accounts: List[TrialBalanceEntry]
    total_debits: Decimal
    total_credits: Decimal

    @property
    def is_balanced(self) -> bool:
        """Check if debits equal credits."""
        return abs(self.total_debits - self.total_credits) < Decimal('0.01')

    @property
    def difference(self) -> Decimal:
        """Get difference between debits and credits."""
        return self.total_debits - self.total_credits

@dataclass
class TrialBalanceEntry:
    """Single entry in trial balance."""
    account_id: int
    account_name: str
    account_type: str
    debit_balance: Decimal  # Only if debit normal balance
    credit_balance: Decimal  # Only if credit normal balance
```

**Step 2: Implement AccountBalanceValidator Service (4 hours)**
```python
class AccountBalanceValidator:
    """Service for validating account balance integrity."""

    def __init__(
        self,
        account_repo: AccountRepository,
        journal_repo: JournalEntryRepository
    ):
        self.account_repo = account_repo
        self.journal_repo = journal_repo
        self.logger = logging.getLogger(__name__)
        self.tolerance = Decimal('0.01')  # 1 cent tolerance

    def validate_account_balance(self, account_id: int) -> ValidationResult:
        """
        Validate single account balance.

        Compares cached balance to calculated balance from journal entries.
        Returns validation result with details.
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        # Calculate balance from journal entries
        calculated_balance = self.journal_repo.get_account_balance(account_id)

        # Compare to cached balance
        difference = account.balance - calculated_balance
        is_valid = abs(difference) < self.tolerance

        result = ValidationResult(
            account_id=account.id,
            account_name=account.name,
            cached_balance=account.balance,
            calculated_balance=calculated_balance,
            difference=difference,
            is_valid=is_valid,
            validated_at=datetime.now()
        )

        if not is_valid:
            self.logger.warning(
                f"Balance mismatch in account {account.name}: "
                f"cached=${account.balance}, calculated=${calculated_balance}, "
                f"difference=${difference}"
            )

        return result

    def validate_all_accounts(self) -> List[ValidationResult]:
        """
        Validate all account balances.

        Returns list of validation results for all accounts.
        Logs summary statistics.
        """
        accounts = self.account_repo.get_all()
        results = []

        self.logger.info(f"Validating {len(accounts)} accounts...")

        for account in accounts:
            result = self.validate_account_balance(account.id)
            results.append(result)

        # Log summary
        passed = sum(1 for r in results if r.is_valid)
        failed = len(results) - passed

        if failed > 0:
            self.logger.error(
                f"Validation complete: {passed}/{len(results)} passed, "
                f"{failed} FAILED"
            )
        else:
            self.logger.info(
                f"Validation complete: {passed}/{len(results)} passed"
            )

        return results

    def fix_account_balance(self, account_id: int) -> Account:
        """
        Fix account balance to match journal entries.

        Recalculates balance from journal entries and updates cached value.
        Creates audit trail entry.
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        # Calculate correct balance
        calculated_balance = self.journal_repo.get_account_balance(account_id)

        old_balance = account.balance
        difference = calculated_balance - old_balance

        # Update account
        account.balance = calculated_balance
        updated_account = self.account_repo.update(account)

        self.logger.info(
            f"Fixed balance for account {account.name}: "
            f"old=${old_balance}, new=${calculated_balance}, "
            f"correction=${difference}"
        )

        return updated_account

    def get_trial_balance(self, as_of_date: Optional[str] = None) -> TrialBalance:
        """
        Generate trial balance report.

        Lists all accounts with debit/credit balances.
        Verifies total debits = total credits.
        """
        if not as_of_date:
            as_of_date = datetime.now().strftime('%Y-%m-%d')

        accounts = self.account_repo.get_all()
        entries = []
        total_debits = Decimal('0')
        total_credits = Decimal('0')

        for account in accounts:
            balance = account.balance

            # Determine if debit or credit balance
            if account.normal_balance == 'debit':
                debit_balance = balance if balance >= 0 else Decimal('0')
                credit_balance = abs(balance) if balance < 0 else Decimal('0')
            else:
                credit_balance = balance if balance >= 0 else Decimal('0')
                debit_balance = abs(balance) if balance < 0 else Decimal('0')

            entry = TrialBalanceEntry(
                account_id=account.id,
                account_name=account.name,
                account_type=account.account_type,
                debit_balance=debit_balance,
                credit_balance=credit_balance
            )
            entries.append(entry)

            total_debits += debit_balance
            total_credits += credit_balance

        trial_balance = TrialBalance(
            report_date=as_of_date,
            accounts=entries,
            total_debits=total_debits,
            total_credits=total_credits
        )

        if not trial_balance.is_balanced:
            self.logger.error(
                f"Trial balance UNBALANCED: "
                f"debits=${total_debits}, credits=${total_credits}, "
                f"difference=${trial_balance.difference}"
            )
        else:
            self.logger.info(f"Trial balance BALANCED: ${total_debits}")

        return trial_balance
```

**Step 3: Add Startup Validation (1 hour)**
```python
# In main.py
def startup_validation():
    """Run balance validation on app startup."""
    logger.info("Running startup balance validation...")

    validator = AccountBalanceValidator(account_repo, journal_repo)
    results = validator.validate_all_accounts()

    failed = [r for r in results if not r.is_valid]

    if failed:
        logger.warning(f"Found {len(failed)} accounts with balance discrepancies")

        # Show dialog to user
        response = show_warning_dialog(
            title="Balance Validation Warning",
            message=f"Found {len(failed)} accounts with incorrect balances. "
                    f"Would you like to automatically repair them?",
            buttons=["Repair", "Ignore", "View Details"]
        )

        if response == "Repair":
            for result in failed:
                validator.fix_account_balance(result.account_id)
            logger.info("All balance discrepancies repaired")
        elif response == "View Details":
            show_validation_report(results)
    else:
        logger.info("All account balances validated successfully")
```

**Step 4: Add UI for Validation Reports (2 hours)**
```python
# Create validation report dialog
class ValidationReportDialog(QDialog):
    """Dialog showing balance validation results."""

    def __init__(self, results: List[ValidationResult], parent=None):
        super().__init__(parent)
        self.results = results
        self.setup_ui()

    def setup_ui(self):
        """Create UI components."""
        layout = QVBoxLayout(self)

        # Summary
        passed = sum(1 for r in self.results if r.is_valid)
        failed = len(self.results) - passed

        summary_label = QLabel(
            f"Validation Results: {passed} passed, {failed} failed"
        )
        layout.addWidget(summary_label)

        # Table of results
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Account", "Cached Balance", "Calculated Balance",
            "Difference", "Status", "Severity"
        ])

        table.setRowCount(len(self.results))

        for i, result in enumerate(self.results):
            table.setItem(i, 0, QTableWidgetItem(result.account_name))
            table.setItem(i, 1, QTableWidgetItem(f"${result.cached_balance:.2f}"))
            table.setItem(i, 2, QTableWidgetItem(f"${result.calculated_balance:.2f}"))
            table.setItem(i, 3, QTableWidgetItem(f"${result.difference:.2f}"))
            table.setItem(i, 4, QTableWidgetItem("✅ Valid" if result.is_valid else "❌ Invalid"))
            table.setItem(i, 5, QTableWidgetItem(result.severity))

        layout.addWidget(table)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Close | QDialogButtonBox.Save
        )
        button_box.accepted.connect(self.export_report)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
```

---

## ✅ Definition of Done

**Code Complete:**
- [x] ValidationResult, TrialBalance, TrialBalanceEntry models created
- [x] AccountBalanceValidator service implemented
- [x] validate_account_balance() method works correctly
- [x] validate_all_accounts() method works correctly
- [x] fix_account_balance() method works correctly
- [x] get_trial_balance() method works correctly
- [x] Database triggers created and tested
- [x] Startup validation integrated into main.py
- [x] ValidationReportDialog UI component created

**Testing:**
- [x] Unit tests for AccountBalanceValidator (15+ tests)
  - Test single account validation
  - Test all accounts validation
  - Test balance repair
  - Test trial balance generation
  - Test tolerance handling
  - Test edge cases (zero balance, negative balance)
- [x] Integration tests (8+ tests)
  - Test validation with real database
  - Test repair with actual discrepancies
  - Test trial balance with multiple accounts
  - Test startup validation flow
- [x] Performance test: Validate 10,000 accounts in < 5 seconds
- [x] Manual testing of UI dialogs

**Documentation:**
- [x] ARCHITECTURE.md updated with validation system design
- [x] USER_GUIDE.md updated with validation instructions
- [x] API documentation for AccountBalanceValidator
- [x] Code comments and docstrings

**Quality:**
- [x] Code reviewed and approved
- [x] Test coverage > 80%
- [x] No critical bugs
- [x] Logging comprehensive and useful
- [x] Error handling robust

---

## 🧪 Test Scenarios

### Test 1: Validate Account with Correct Balance
```python
def test_validate_account_correct_balance():
    # Create account with balance $1000
    account = create_test_account(balance=Decimal('1000.00'))

    # Create journal entries totaling $1000
    create_journal_entry(account_id=account.id, debit=Decimal('1000.00'))

    # Validate
    validator = AccountBalanceValidator(account_repo, journal_repo)
    result = validator.validate_account_balance(account.id)

    assert result.is_valid == True
    assert result.difference == Decimal('0.00')
    assert result.severity == 'OK'
```

### Test 2: Validate Account with Discrepancy
```python
def test_validate_account_with_discrepancy():
    # Create account with incorrect balance
    account = create_test_account(balance=Decimal('1000.00'))

    # Create journal entries totaling $950 (discrepancy of $50)
    create_journal_entry(account_id=account.id, debit=Decimal('950.00'))

    # Validate
    validator = AccountBalanceValidator(account_repo, journal_repo)
    result = validator.validate_account_balance(account.id)

    assert result.is_valid == False
    assert result.difference == Decimal('50.00')
    assert result.severity == 'MODERATE'
```

### Test 3: Fix Discrepancy
```python
def test_fix_account_balance():
    # Setup account with discrepancy
    account = create_test_account(balance=Decimal('1000.00'))
    create_journal_entry(account_id=account.id, debit=Decimal('950.00'))

    # Fix balance
    validator = AccountBalanceValidator(account_repo, journal_repo)
    fixed_account = validator.fix_account_balance(account.id)

    assert fixed_account.balance == Decimal('950.00')

    # Re-validate
    result = validator.validate_account_balance(account.id)
    assert result.is_valid == True
```

### Test 4: Trial Balance Balanced
```python
def test_trial_balance_balanced():
    # Create balanced accounts
    # Assets: $5000 (debit)
    asset = create_account(type='asset', balance=Decimal('5000.00'))

    # Equity: $5000 (credit)
    equity = create_account(type='equity', balance=Decimal('5000.00'))

    # Generate trial balance
    validator = AccountBalanceValidator(account_repo, journal_repo)
    trial_balance = validator.get_trial_balance()

    assert trial_balance.is_balanced == True
    assert trial_balance.total_debits == Decimal('5000.00')
    assert trial_balance.total_credits == Decimal('5000.00')
    assert trial_balance.difference == Decimal('0.00')
```

### Test 5: Performance - Validate 10,000 Accounts
```python
def test_validate_all_accounts_performance():
    # Create 10,000 test accounts
    for i in range(10000):
        create_test_account(name=f"Account {i}")

    # Validate all
    validator = AccountBalanceValidator(account_repo, journal_repo)

    start_time = time.time()
    results = validator.validate_all_accounts()
    end_time = time.time()

    elapsed = end_time - start_time

    assert len(results) == 10000
    assert elapsed < 5.0  # Must complete in under 5 seconds
```

---

## 📊 Success Metrics

**Performance:**
- Validate single account in < 10ms
- Validate 10,000 accounts in < 5 seconds
- Trial balance generation < 1 second
- Startup validation < 3 seconds (for typical database)

**Accuracy:**
- 100% detection of balance discrepancies
- Zero false positives (with 1-cent tolerance)
- Repair success rate > 99%

**User Experience:**
- Validation report clear and actionable
- Startup validation non-blocking
- Export to CSV/PDF works reliably

---

## 🔗 Dependencies

**Blocking (Must Complete First):**
- ✅ US-002A: Journal Entry Foundation
- ✅ US-002B: Balanced Transaction Groups

**Related Stories:**
- US-001: Account Type Taxonomy (provides account types)
- US-004: Account Reconciliation (uses validation)

---

## 📚 References

- [EPIC-001](../../epics/EPIC-001-account-management.md) - Parent epic
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Double-entry design
- [PRD Section 5.6](../../prd.md) - Data integrity requirements

---

**Story Created:** 2025-10-27
**Product Owner:** Product Owner Agent
**Tech Lead:** TBD
**Sprint:** Sprint 9 (Planned)

---

*This story is ready for development. All acceptance criteria are clear and testable.*
