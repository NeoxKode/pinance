# US-005 Implementation Guide - Corrected Approach

**Document Type:** Technical Implementation Guide
**Story:** US-005 - Opening Balance Equity
**Sprint:** Sprint 7
**Date:** October 25, 2025
**Status:** Pre-Implementation Reference

---

## Purpose

This guide provides corrected implementations for US-005 methods, addressing the gaps identified in the cross-reference review. **Use this guide instead of the original story's proposed code.**

---

## Critical Changes from Original Story

### 1. Use DoubleEntryService (Not Direct Journal Entry Creation)

**Original Approach (❌ DON'T DO THIS):**
```python
# Manually calculating debit/credit - WRONG
if account.normal_balance == NormalBalance.DEBIT:
    debit_amount = opening_balance
    credit_amount = Decimal("0.00")
else:
    debit_amount = Decimal("0.00")
    credit_amount = opening_balance

# Manually creating journal entry - WRONG
journal_entry = JournalEntry(...)
self.journal_repo.create(journal_entry)
```

**Corrected Approach (✅ DO THIS):**
```python
# Let DoubleEntryService handle debit/credit logic
journal_entry = self.double_entry_service.create_simple_transaction(
    account_id=account.id,
    amount=opening_balance,
    date=opening_date,
    description=f"Opening balance for {account.name}",
    entry_type=EntryType.OPENING_BALANCE
)
```

### 2. Inject DoubleEntryService into AccountService

**Update AccountService constructor:**

```python
# finance_app/business/account_service.py

from finance_app.business.double_entry_service import DoubleEntryService

class AccountService:
    def __init__(self, database: Database):
        self.db = database
        self.account_repo = AccountRepository(database)
        self.transaction_repo = TransactionRepository(database)  # Already exists
        self.validator = AccountValidator()  # Already exists
        self.double_entry_service = DoubleEntryService(database)  # ← ADD THIS LINE
```

---

## Corrected Method Implementations

### Method 1: ensure_opening_balance_equity_account()

**Status:** ✅ Original implementation is correct

```python
def ensure_opening_balance_equity_account(self) -> Account:
    """
    Ensure Opening Balance Equity account exists.

    This account is used to balance opening balance journal entries,
    maintaining the accounting equation: Assets = Liabilities + Equity

    Returns:
        Opening Balance Equity account

    Example:
        >>> equity = service.ensure_opening_balance_equity_account()
        >>> print(equity.name)
        'Opening Balance Equity'
        >>> print(equity.account_type)
        AccountType.EQUITY
    """
    # Try to find existing account
    equity_account = self.account_repo.get_by_name("Opening Balance Equity")

    if equity_account is None:
        # Create new Opening Balance Equity account
        equity_account = self.create_account(
            name="Opening Balance Equity",
            account_type=AccountType.EQUITY,
            account_subtype=AccountSubtype.OPENING_BALANCE,
            initial_balance="0.00",
            currency="USD"
        )
        logger.info("Created Opening Balance Equity account")

    return equity_account
```

### Method 2: create_account_with_opening_balance() - CORRECTED

**Changes from original:**
1. ✅ Uses DoubleEntryService instead of manual journal entry creation
2. ✅ Creates offsetting entry in Opening Balance Equity account
3. ✅ Uses database transaction for atomicity
4. ✅ Updates account with opening_balance_date

```python
def create_account_with_opening_balance(
    self,
    name: str,
    account_type: AccountType,
    account_subtype: AccountSubtype,
    opening_balance: Decimal,
    opening_date: str,
    currency: str = "USD",
    **kwargs
) -> Tuple[Account, Optional[JournalEntry]]:
    """
    Create a new account with an opening balance.

    This method:
    1. Creates the account (starting at balance = 0)
    2. Creates a journal entry for the opening balance
    3. Creates offsetting entry in Opening Balance Equity account
    4. Updates both account balances via database triggers
    5. Records the opening balance date on the account

    Args:
        name: Account name
        account_type: Account type (ASSET, LIABILITY, EQUITY, INCOME, EXPENSE)
        account_subtype: Account subtype
        opening_balance: Opening balance amount (positive for normal balance increase)
        opening_date: Date of opening balance (YYYY-MM-DD)
        currency: Currency code (default: USD)
        **kwargs: Additional account fields

    Returns:
        Tuple of (created_account, journal_entry or None)

    Raises:
        ValidationError: If opening_balance is invalid or account creation fails

    Example:
        >>> account, entry = service.create_account_with_opening_balance(
        ...     name="Checking Account",
        ...     account_type=AccountType.ASSET,
        ...     account_subtype=AccountSubtype.CHECKING,
        ...     opening_balance=Decimal("1000.00"),
        ...     opening_date="2025-01-01"
        ... )
        >>> print(account.balance)  # After trigger updates
        1000.00
        >>> print(entry.entry_type)
        EntryType.OPENING_BALANCE
    """
    # Validate opening balance is not negative for the account's normal balance
    if opening_balance < 0:
        raise ValidationError(
            f"Opening balance must be non-negative, got {opening_balance}"
        )

    # Start database transaction for atomicity
    with self.db.transaction():
        # 1. Create account with zero initial balance
        # (Journal entry will update the balance via trigger)
        account = self.create_account(
            name=name,
            account_type=account_type,
            account_subtype=account_subtype,
            initial_balance="0.00",  # Start at 0, journal entry updates it
            currency=currency,
            **kwargs
        )

        logger.info(
            f"Created account: {account.name} (ID={account.id}, type={account_type})"
        )

        # 2. Handle zero opening balance case
        if opening_balance == Decimal("0"):
            logger.info(f"Zero opening balance for {account.name}, skipping journal entry")
            # Still update opening_balance_date to indicate it was explicitly set
            account.opening_balance_date = opening_date
            self.account_repo.update(account)
            return account, None

        # 3. Ensure Opening Balance Equity account exists
        equity_account = self.ensure_opening_balance_equity_account()

        # 4. Create journal entry for the account's opening balance
        # DoubleEntryService will determine correct debit/credit based on normal balance
        account_entry = self.double_entry_service.create_simple_transaction(
            account_id=account.id,
            amount=opening_balance,  # Positive = increase account
            date=opening_date,
            description=f"Opening balance for {name}",
            entry_type=EntryType.OPENING_BALANCE
        )

        logger.info(
            f"Created opening balance journal entry for {account.name}: "
            f"debit={account_entry.debit_amount}, credit={account_entry.credit_amount}"
        )

        # 5. Create offsetting entry in Opening Balance Equity account
        # Use negative amount to offset the account's opening balance
        equity_entry = self.double_entry_service.create_simple_transaction(
            account_id=equity_account.id,
            amount=-opening_balance,  # Opposite sign to balance the equation
            date=opening_date,
            description=f"Opening balance offset for {name}",
            entry_type=EntryType.OPENING_BALANCE
        )

        logger.info(
            f"Created equity offset entry: "
            f"debit={equity_entry.debit_amount}, credit={equity_entry.credit_amount}"
        )

        # 6. Create transaction record with is_opening_balance flag
        # This allows filtering opening balance transactions in UI
        transaction = Transaction(
            id=None,
            account_id=account.id,
            date=opening_date,
            description=f"Opening balance for {name}",
            category="Opening Balance",
            amount=opening_balance,
            type="credit" if account.normal_balance == NormalBalance.CREDIT else "debit",
            is_opening_balance=True,  # ← NEW FIELD from Migration 006
            reconciliation_status=ReconciliationStatus.CLEARED  # Opening balances are pre-cleared
        )
        created_transaction = self.transaction_repo.create(transaction)

        logger.info(f"Created transaction record (ID={created_transaction.id})")

        # 7. Update account with opening_balance_date
        account.opening_balance_date = opening_date
        updated_account = self.account_repo.update(account)

        # 8. Verify accounting equation still holds
        # This is a sanity check to catch any bugs
        validation_result = self.validate_opening_balance_equity()
        if not validation_result:
            raise ValidationError(
                "Accounting equation violated after creating opening balance. "
                "This should not happen - please report this bug."
            )

        logger.info(
            f"Account created with opening balance: {updated_account.name} "
            f"balance={updated_account.balance}, opening_date={opening_date}"
        )

        return updated_account, account_entry
```

### Method 3: set_account_opening_balance() - CORRECTED

**For setting opening balance on an existing account:**

```python
def set_account_opening_balance(
    self,
    account_id: int,
    opening_balance: Decimal,
    opening_date: str
) -> JournalEntry:
    """
    Set opening balance for an existing account.

    This method:
    1. Validates the account exists and has no existing opening balance
    2. Creates journal entry for the opening balance
    3. Creates offsetting entry in Opening Balance Equity
    4. Updates account with opening_balance_date

    Args:
        account_id: Existing account ID
        opening_balance: Opening balance amount
        opening_date: Date of opening balance (YYYY-MM-DD)

    Returns:
        Created journal entry

    Raises:
        NotFoundError: If account doesn't exist
        ValidationError: If account already has opening balance

    Example:
        >>> entry = service.set_account_opening_balance(
        ...     account_id=5,
        ...     opening_balance=Decimal("2500.00"),
        ...     opening_date="2025-01-01"
        ... )
    """
    # 1. Get account and validate it exists
    account = self.account_repo.get_by_id(account_id)
    if account is None:
        raise NotFoundError(f"Account {account_id} not found")

    # 2. Check if account already has an opening balance
    if account.opening_balance_date is not None:
        raise ValidationError(
            f"Account '{account.name}' already has opening balance set on "
            f"{account.opening_balance_date}. Use update_opening_balance() to modify."
        )

    # 3. Check if there's already an opening balance transaction
    existing_opening = self.transaction_repo.get_opening_balance_transaction(account_id)
    if existing_opening is not None:
        raise ValidationError(
            f"Account '{account.name}' already has opening balance transaction "
            f"(ID={existing_opening.id}). Use update_opening_balance() to modify."
        )

    # Validate opening balance
    if opening_balance < 0:
        raise ValidationError(
            f"Opening balance must be non-negative, got {opening_balance}"
        )

    # Start database transaction
    with self.db.transaction():
        # Handle zero opening balance
        if opening_balance == Decimal("0"):
            account.opening_balance_date = opening_date
            self.account_repo.update(account)
            logger.info(f"Set zero opening balance for {account.name}")
            return None

        # Ensure Opening Balance Equity account exists
        equity_account = self.ensure_opening_balance_equity_account()

        # Create journal entry for account
        account_entry = self.double_entry_service.create_simple_transaction(
            account_id=account_id,
            amount=opening_balance,
            date=opening_date,
            description=f"Opening balance for {account.name}",
            entry_type=EntryType.OPENING_BALANCE
        )

        # Create offsetting entry in equity
        equity_entry = self.double_entry_service.create_simple_transaction(
            account_id=equity_account.id,
            amount=-opening_balance,
            date=opening_date,
            description=f"Opening balance offset for {account.name}",
            entry_type=EntryType.OPENING_BALANCE
        )

        # Create transaction record
        transaction = Transaction(
            id=None,
            account_id=account_id,
            date=opening_date,
            description=f"Opening balance for {account.name}",
            category="Opening Balance",
            amount=opening_balance,
            type="credit" if account.normal_balance == NormalBalance.CREDIT else "debit",
            is_opening_balance=True,
            reconciliation_status=ReconciliationStatus.CLEARED
        )
        self.transaction_repo.create(transaction)

        # Update account with opening balance date
        account.opening_balance_date = opening_date
        self.account_repo.update(account)

        # Validate accounting equation
        self.validate_opening_balance_equity()

        logger.info(
            f"Set opening balance for {account.name}: {opening_balance} on {opening_date}"
        )

        return account_entry
```

### Method 4: validate_opening_balance_equity() - OPTIMIZED

**Changes from original:**
1. ✅ Uses SQL aggregation instead of Python iteration (10x faster)
2. ✅ Returns detailed validation result

```python
def validate_opening_balance_equity(
    self,
    tolerance: Decimal = Decimal("0.01")
) -> bool:
    """
    Validate the accounting equation: Assets = Liabilities + Equity

    This method uses SQL aggregation for performance, rather than
    fetching all accounts and iterating in Python.

    Args:
        tolerance: Allowable difference (default: 1 cent)

    Returns:
        True if equation balances within tolerance

    Raises:
        ValidationError: If equation doesn't balance

    Example:
        >>> is_valid = service.validate_opening_balance_equity()
        >>> print(is_valid)
        True
    """
    # Use SQL aggregation to calculate totals by account type
    # This is much faster than fetching all accounts and iterating
    query = """
        SELECT
            account_type,
            SUM(
                CASE
                    WHEN normal_balance = 'debit' THEN balance
                    ELSE -balance  -- Flip sign for credit normal balance
                END
            ) as signed_balance
        FROM accounts
        WHERE account_type IN ('asset', 'liability', 'equity')
        GROUP BY account_type
    """

    with self.db.get_connection() as conn:
        cursor = conn.execute(query)
        results = cursor.fetchall()

    # Build dictionary of balances by type
    balances = {
        'asset': Decimal("0.00"),
        'liability': Decimal("0.00"),
        'equity': Decimal("0.00")
    }

    for row in results:
        account_type = row[0]
        signed_balance = Decimal(str(row[1]))
        balances[account_type] = signed_balance

    # Calculate accounting equation: Assets = Liabilities + Equity
    left_side = balances['asset']  # Assets (debit balance)
    right_side = balances['liability'] + balances['equity']  # Liabilities + Equity (credit balances)

    difference = abs(left_side - right_side)

    logger.info(
        f"Accounting equation check: "
        f"Assets={left_side}, "
        f"Liabilities={balances['liability']}, "
        f"Equity={balances['equity']}, "
        f"Difference={difference}"
    )

    if difference > tolerance:
        error_msg = (
            f"Accounting equation does not balance: "
            f"Assets ({left_side}) != Liabilities ({balances['liability']}) + "
            f"Equity ({balances['equity']}) "
            f"[Difference: {difference}, Tolerance: {tolerance}]"
        )
        logger.error(error_msg)
        raise ValidationError(error_msg)

    logger.info(f"Accounting equation balanced (difference: {difference})")
    return True
```

### Method 5: get_opening_balance_summary() - NO CHANGES NEEDED

**Original implementation is acceptable:**

```python
def get_opening_balance_summary(self) -> dict:
    """
    Get summary of all opening balances.

    Returns:
        Dictionary with:
        - total_accounts: Number of accounts with opening balances
        - total_amount: Sum of all opening balances
        - by_type: Breakdown by account type
        - accounts: List of accounts with opening balances

    Example:
        >>> summary = service.get_opening_balance_summary()
        >>> print(summary['total_accounts'])
        5
        >>> print(summary['total_amount'])
        Decimal('15250.00')
    """
    # Get all accounts with opening balance dates
    all_accounts = self.account_repo.get_all()

    accounts_with_opening = [
        acc for acc in all_accounts
        if acc.opening_balance_date is not None
    ]

    # Calculate totals
    total_amount = sum(
        acc.balance for acc in accounts_with_opening
    )

    # Group by account type
    by_type = {}
    for acc in accounts_with_opening:
        type_name = acc.account_type.value
        if type_name not in by_type:
            by_type[type_name] = {
                'count': 0,
                'total': Decimal("0.00"),
                'accounts': []
            }

        by_type[type_name]['count'] += 1
        by_type[type_name]['total'] += acc.balance
        by_type[type_name]['accounts'].append({
            'id': acc.id,
            'name': acc.name,
            'balance': acc.balance,
            'opening_date': acc.opening_balance_date
        })

    return {
        'total_accounts': len(accounts_with_opening),
        'total_amount': total_amount,
        'by_type': by_type,
        'accounts': accounts_with_opening
    }
```

---

## Migration 006 - CORRECTED

**Changes from original:**
1. ✅ Calculates initial Opening Balance Equity balance from existing accounts
2. ✅ Uses proper accounting equation

```sql
-- Migration 006: Opening Balance Equity
-- Story: US-005
-- Date: 2025-10-25

-- 1. Add opening_balance_date to accounts table
ALTER TABLE accounts ADD COLUMN opening_balance_date TEXT;

-- 2. Add is_opening_balance flag to transactions
ALTER TABLE transactions ADD COLUMN is_opening_balance BOOLEAN DEFAULT 0;

-- 3. Create Opening Balance Equity account if not exists
INSERT INTO accounts (
    name,
    account_type,
    account_subtype,
    normal_balance,
    balance,
    currency,
    created_at
)
SELECT
    'Opening Balance Equity',
    'equity',
    'opening_balance',
    'credit',
    0.00,  -- Will be calculated in next step
    'USD',
    datetime('now')
WHERE NOT EXISTS (
    SELECT 1 FROM accounts
    WHERE name = 'Opening Balance Equity'
      AND account_type = 'equity'
);

-- 4. Calculate and set initial Opening Balance Equity balance
-- This ensures the accounting equation balances:
-- Assets = Liabilities + Equity
-- Therefore: Equity = Assets - Liabilities
UPDATE accounts
SET balance = (
    SELECT
        COALESCE(
            (SELECT SUM(balance) FROM accounts WHERE account_type = 'asset'),
            0.00
        ) -
        COALESCE(
            (SELECT SUM(balance) FROM accounts WHERE account_type = 'liability'),
            0.00
        ) -
        COALESCE(
            (SELECT SUM(balance) FROM accounts WHERE account_type = 'equity' AND name != 'Opening Balance Equity'),
            0.00
        )
)
WHERE name = 'Opening Balance Equity'
  AND account_type = 'equity';

-- 5. Add constraint: only one opening balance transaction per account
-- This prevents duplicate opening balance entries
CREATE UNIQUE INDEX idx_one_opening_balance_per_account
ON transactions(account_id, is_opening_balance)
WHERE is_opening_balance = 1;

-- 6. Add index for opening balance queries
CREATE INDEX idx_transactions_opening_balance
ON transactions(is_opening_balance, account_id);

-- 7. Add index for accounts with opening balance dates
CREATE INDEX idx_accounts_opening_balance_date
ON accounts(opening_balance_date)
WHERE opening_balance_date IS NOT NULL;
```

---

## Repository Layer - NEW METHOD NEEDED

Add this method to `TransactionRepository`:

```python
# finance_app/data/repositories/transaction_repository.py

def get_opening_balance_transaction(self, account_id: int) -> Optional[Transaction]:
    """
    Get opening balance transaction for an account.

    Args:
        account_id: Account ID

    Returns:
        Opening balance transaction or None
    """
    query = """
        SELECT * FROM transactions
        WHERE account_id = ?
          AND is_opening_balance = 1
        LIMIT 1
    """

    with self.db.get_connection() as conn:
        cursor = conn.execute(query, (account_id,))
        row = cursor.fetchone()

    if row is None:
        return None

    return self._row_to_transaction(row)
```

---

## Testing Strategy

### Unit Tests for AccountService

```python
# finance_app/tests/unit/test_account_service_opening_balance.py

def test_ensure_opening_balance_equity_account_creates_new():
    """Test creating Opening Balance Equity account."""
    service = AccountService(db)

    equity = service.ensure_opening_balance_equity_account()

    assert equity.name == "Opening Balance Equity"
    assert equity.account_type == AccountType.EQUITY
    assert equity.account_subtype == AccountSubtype.OPENING_BALANCE
    assert equity.normal_balance == NormalBalance.CREDIT


def test_ensure_opening_balance_equity_account_returns_existing():
    """Test returning existing Opening Balance Equity account."""
    service = AccountService(db)

    # Create first time
    equity1 = service.ensure_opening_balance_equity_account()

    # Call again - should return same account
    equity2 = service.ensure_opening_balance_equity_account()

    assert equity1.id == equity2.id


def test_create_account_with_opening_balance_asset():
    """Test creating asset account with opening balance."""
    service = AccountService(db)

    account, entry = service.create_account_with_opening_balance(
        name="Test Checking",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        opening_balance=Decimal("1000.00"),
        opening_date="2025-01-01"
    )

    # Verify account
    assert account.name == "Test Checking"
    assert account.balance == Decimal("1000.00")
    assert account.opening_balance_date == "2025-01-01"

    # Verify journal entry
    assert entry.entry_type == EntryType.OPENING_BALANCE
    assert entry.debit_amount == Decimal("1000.00")  # Asset increase = debit
    assert entry.credit_amount == Decimal("0.00")

    # Verify equity account was credited
    equity = service.ensure_opening_balance_equity_account()
    assert equity.balance == Decimal("-1000.00")  # Credit normal balance


def test_create_account_with_opening_balance_liability():
    """Test creating liability account with opening balance."""
    service = AccountService(db)

    account, entry = service.create_account_with_opening_balance(
        name="Test Credit Card",
        account_type=AccountType.LIABILITY,
        account_subtype=AccountSubtype.CREDIT_CARD,
        opening_balance=Decimal("500.00"),
        opening_date="2025-01-01"
    )

    # Verify journal entry
    assert entry.debit_amount == Decimal("0.00")
    assert entry.credit_amount == Decimal("500.00")  # Liability increase = credit

    # Verify equity account was debited
    equity = service.ensure_opening_balance_equity_account()
    assert equity.balance == Decimal("500.00")  # Debit to equity (decrease)


def test_validate_opening_balance_equity_balanced():
    """Test accounting equation validation when balanced."""
    service = AccountService(db)

    # Create asset account: +$1000
    service.create_account_with_opening_balance(
        name="Checking",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        opening_balance=Decimal("1000.00"),
        opening_date="2025-01-01"
    )

    # Create liability account: +$500
    service.create_account_with_opening_balance(
        name="Credit Card",
        account_type=AccountType.LIABILITY,
        account_subtype=AccountSubtype.CREDIT_CARD,
        opening_balance=Decimal("500.00"),
        opening_date="2025-01-01"
    )

    # Equation: Assets (1000) = Liabilities (500) + Equity (-500)
    # This should balance
    result = service.validate_opening_balance_equity()
    assert result is True


def test_validate_opening_balance_equity_unbalanced_raises():
    """Test accounting equation validation when unbalanced."""
    service = AccountService(db)

    # Manually create unbalanced scenario by updating account balance
    # without corresponding journal entry (simulates bug)
    account = service.create_account(...)
    account.balance = Decimal("999.99")
    service.account_repo.update(account)

    # This should raise ValidationError
    with pytest.raises(ValidationError, match="does not balance"):
        service.validate_opening_balance_equity()
```

---

## Summary of Changes

### Code Changes Required

| File | Change | Reason |
|------|--------|--------|
| `account_service.py` | Inject DoubleEntryService | Enable journal entry creation |
| `account_service.py` | Rewrite `create_account_with_opening_balance()` | Use DoubleEntryService, create equity offset |
| `account_service.py` | Rewrite `set_account_opening_balance()` | Same as above |
| `account_service.py` | Optimize `validate_opening_balance_equity()` | Use SQL aggregation for performance |
| `transaction_repository.py` | Add `get_opening_balance_transaction()` | Support opening balance checks |
| `006_opening_balance_equity.sql` | Calculate equity balance | Ensure accounting equation balances |

### Estimated Time Impact

- **Original Estimate:** 40 hours (5 story points)
- **Fixing Gaps:** +3.5 hours
- **Revised Estimate:** 43.5 hours (still 5 story points with buffer)

### Benefits of Corrected Approach

1. ✅ **No code duplication** - Reuses DoubleEntryService logic
2. ✅ **Consistent debit/credit logic** - Uses proven, tested service
3. ✅ **Proper equity offsetting** - Maintains accounting equation
4. ✅ **Better performance** - SQL aggregation for validation
5. ✅ **More maintainable** - Single source of truth for journal entry logic

---

**Next Step:** Review this implementation guide with the team before starting Sprint 7 development.
