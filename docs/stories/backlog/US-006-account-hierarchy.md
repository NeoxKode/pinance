# US-006: Account Hierarchy (Parent/Child Accounts)

**Story ID:** US-006
**Epic:** [EPIC-01: Account Management & Double-Entry Foundation](../../epics/epic-01-account-management.md)
**Created:** 2025-10-26
**Updated:** 2025-10-26
**Status:** 📋 Backlog - Ready for Sprint 8
**Priority:** P1 (Should Have)
**Story Points:** 5
**Assignee:** Unassigned
**Sprint:** Sprint 8 (proposed)
**Dependencies:** ✅ US-001 (Account Type Taxonomy), ✅ US-002A (Journal Entry Foundation), ✅ US-005 (Opening Balance Equity)
**Related Stories:** US-001 (provides account type foundation), US-007 (Account Organization - future)

---

## 📖 User Story

**As a** power user organizing my finances
**I want** to create hierarchical account structures with parent and child accounts
**So that** I can organize accounts logically (e.g., Assets → Bank Accounts → Checking) and see subtotals at each level

---

## 📝 Description

### Context

Many users want to organize their accounts in a hierarchical structure for better organization and reporting. For example:

```
📁 Assets
  ├─ 🏦 Bank Accounts
  │  ├─ Checking Account        $2,500
  │  ├─ Savings Account          $10,000
  │  └─ Emergency Fund           $5,000
  ├─ 💳 Investment Accounts
  │  ├─ Brokerage Account        $25,000
  │  └─ Retirement (401k)        $50,000
  └─ 💵 Cash
     └─ Wallet Cash              $150
```

This provides:
- **Better Organization:** Group related accounts together
- **Subtotals:** See totals for "Bank Accounts" or "Investment Accounts"
- **Reporting:** Generate reports by account group
- **Flexibility:** Create custom organization structures

### Current State

- ✅ Account model has `parent_account_id` field (added in US-001)
- ✅ Accounts can be created with different types and subtypes
- ❌ No UI support for parent/child relationships
- ❌ No validation for hierarchy rules
- ❌ No subtotal calculations for parent accounts
- ❌ No hierarchical display in account list

### Relationship to Completed Stories

**US-001 (Account Type Taxonomy)** laid the foundation:
- Added `parent_account_id` field to database schema
- Established account types and subtypes
- Created the Account model structure

**US-005 (Opening Balance Equity)** provides reference:
- Shows how to work with system accounts
- Demonstrates account management patterns
- UI dialog patterns to follow

### Problem Statement

Users need to organize accounts hierarchically for:
1. **Logical Grouping:** Group bank accounts, credit cards, investments separately
2. **Subtotals:** See total of all bank accounts or all credit cards
3. **Reporting:** Generate reports by account group
4. **Scalability:** Manage 50+ accounts without confusion
5. **Financial Planning:** Track accounts by financial goal (e.g., Emergency Fund → Checking, Savings)

---

## 🎯 Acceptance Criteria

### AC1: Create Parent Accounts (Header Accounts)

**Given** I want to organize accounts hierarchically
**When** I create a parent account
**Then** it should:
- Be marked as a parent/header account (cannot have transactions)
- Have a balance that equals the sum of all child accounts
- Be visually distinct in the UI (folder icon, different styling)
- Not allow direct transaction posting

**Examples:**
```python
# Create parent account
parent = account_service.create_account(
    name="Bank Accounts",
    account_type=AccountType.ASSET,
    account_subtype=AccountSubtype.CHECKING,
    is_parent=True  # Mark as parent/header
)

# Parent accounts cannot have transactions
with pytest.raises(ValidationError):
    transaction_service.create_transaction(
        account_id=parent.id,  # Error: Cannot post to parent account
        amount=100
    )
```

### AC2: Create Child Accounts

**Given** I have a parent account
**When** I create a child account under it
**Then** the child should:
- Have `parent_account_id` set to the parent's ID
- Inherit the account type from parent (validation)
- Be displayed indented under the parent in the UI
- Have its balance contribute to parent's subtotal

**Examples:**
```python
# Create child accounts under parent
checking = account_service.create_account(
    name="Everyday Checking",
    account_type=AccountType.ASSET,
    account_subtype=AccountSubtype.CHECKING,
    parent_account_id=parent.id
)

savings = account_service.create_account(
    name="High-Yield Savings",
    account_type=AccountType.ASSET,
    account_subtype=AccountSubtype.SAVINGS,
    parent_account_id=parent.id
)
```

### AC3: Parent Account Balance Calculation

**Given** I have parent accounts with child accounts
**When** I view a parent account's balance
**Then** it should:
- Display the sum of all child account balances
- Update automatically when child balances change
- Be calculated (not stored) to ensure accuracy
- Include all descendant accounts (nested hierarchy)

**Examples:**
```python
# Parent balance calculation
parent = account_service.get_account(parent_id)
parent_balance = account_service.get_parent_account_balance(parent.id)

# Should equal sum of children
expected = sum(child.balance for child in children)
assert parent_balance == expected
```

### AC4: Hierarchical Display in UI

**Given** I have accounts with parent/child relationships
**When** I view the account list
**Then** I should see:
- Parent accounts with folder icon (📁) or similar
- Child accounts indented under parents
- Expand/collapse controls for parent accounts
- Parent account subtotals
- Visual hierarchy (indentation, colors, icons)

**UI Example:**
```
📁 Assets                         $92,650.00
  📁 Bank Accounts                $17,500.00  [▼]
    Checking Account               $2,500.00
    Savings Account               $10,000.00
    Emergency Fund                 $5,000.00
  📁 Investment Accounts          $75,000.00  [▼]
    Brokerage Account             $25,000.00
    Retirement (401k)             $50,000.00
  💵 Cash                            $150.00

📁 Liabilities                    -$5,850.00
  📁 Credit Cards                 -$1,850.00  [▼]
    Visa Card                      -$1,200.00
    Mastercard                       -$650.00
  📁 Loans                        -$4,000.00  [▼]
    Car Loan                       -$4,000.00
```

### AC5: Hierarchy Validation Rules

**Given** I am creating or modifying account hierarchy
**When** I set parent/child relationships
**Then** the system should validate:
- Child account type must match parent account type
- No circular references (account cannot be its own ancestor)
- Maximum depth limit (e.g., 5 levels)
- Parent accounts cannot have transactions
- Cannot delete parent account with children (must move/delete children first)

**Validation Examples:**
```python
# Error: Type mismatch
with pytest.raises(ValidationError):
    account_service.create_account(
        name="Credit Card",
        account_type=AccountType.LIABILITY,  # Mismatch!
        parent_account_id=asset_parent.id    # Asset parent
    )

# Error: Circular reference
with pytest.raises(ValidationError):
    account_service.update_account(
        account_id=parent.id,
        parent_account_id=child.id  # Would create cycle
    )

# Error: Delete parent with children
with pytest.raises(ValidationError):
    account_service.delete_account(parent.id)
    # Must use force_delete_with_children=True or move children first
```

### AC6: Move Accounts in Hierarchy

**Given** I have existing accounts
**When** I move an account to a different parent
**Then** the system should:
- Update the `parent_account_id`
- Validate the new parent is compatible (same type)
- Update parent balances automatically
- Maintain all transactions and history
- Log the hierarchy change

**Examples:**
```python
# Move account to different parent
account_service.move_account(
    account_id=checking.id,
    new_parent_id=different_parent.id
)

# Move account to top level (no parent)
account_service.move_account(
    account_id=checking.id,
    new_parent_id=None  # Top-level account
)
```

---

## 🎨 User Interface Design

### Account List Enhancement

**Current State:** Flat list of accounts

**Proposed State:** Hierarchical tree view with expand/collapse

```
┌─────────────────────────────────────────────────────┐
│ Accounts                                    $86,800 │
├─────────────────────────────────────────────────────┤
│ 📁 Assets                            [▼] $92,650.00 │
│   📁 Bank Accounts                   [▼] $17,500.00 │
│     🏦 Checking Account                   $2,500.00 │
│     💰 Savings Account                   $10,000.00 │
│     🆘 Emergency Fund                     $5,000.00 │
│   📁 Investment Accounts             [▲] $75,000.00 │
│   💵 Cash                                    $150.00 │
│                                                      │
│ 📁 Liabilities                       [▼] -$5,850.00 │
│   📁 Credit Cards                    [▼] -$1,850.00 │
│     💳 Visa Card                         -$1,200.00 │
│     💳 Mastercard                          -$650.00 │
│   📁 Loans                           [▼] -$4,000.00 │
│     🚗 Car Loan                          -$4,000.00 │
│                                                      │
│ 📁 Equity                            [▼] $86,800.00 │
│   🔐 Opening Balance Equity (System)     $86,800.00 │
└─────────────────────────────────────────────────────┘
```

**Features:**
- [▼] / [▲] Expand/collapse controls
- Indentation shows hierarchy level
- Parent accounts show subtotals in gray or dim color
- Icons distinguish parent (📁) from leaf accounts (🏦, 💳, etc.)
- Parent account balance in **bold**
- Click parent to expand/collapse, not navigate

### Account Creation Dialog Enhancement

**Add "Parent Account" Field:**

```
┌──────────────────────────────────────────┐
│ Create New Account                    [X]│
├──────────────────────────────────────────┤
│                                          │
│ Account Name:                            │
│ ┌──────────────────────────────────────┐ │
│ │ Everyday Checking                    │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ Account Type:                            │
│ ┌──────────────────────────────────────┐ │
│ │ Asset                            [▼] │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ Account Subtype:                         │
│ ┌──────────────────────────────────────┐ │
│ │ Checking                         [▼] │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ Parent Account (Optional):               │
│ ┌──────────────────────────────────────┐ │
│ │ Bank Accounts                    [▼] │ │
│ └──────────────────────────────────────┘ │
│ ℹ️ Group this account under a parent    │
│                                          │
│ ☐ Make this a parent/header account     │
│   (Cannot have direct transactions)      │
│                                          │
│        [Cancel]              [Create]    │
└──────────────────────────────────────────┘
```

### Account Context Menu Addition

```
Right-click on account:
┌──────────────────────────┐
│ Edit Account           │
│ Set Opening Balance... │
│ ─────────────────────  │
│ ► Move to Parent...    │  ← NEW
│ Make Top-Level         │  ← NEW
│ Make Parent Account    │  ← NEW
│ ─────────────────────  │
│ Archive Account        │
│ Delete Account         │
└──────────────────────────┘
```

---

## 💻 Technical Implementation

### Database Schema Changes

**accounts table** (already has `parent_account_id`, need to add `is_parent`):

```sql
-- Migration 007: Account Hierarchy Support
-- Add is_parent flag
ALTER TABLE accounts ADD COLUMN is_parent BOOLEAN DEFAULT 0;
ALTER TABLE accounts ADD COLUMN hierarchy_level INTEGER DEFAULT 0;
ALTER TABLE accounts ADD COLUMN hierarchy_path TEXT;  -- e.g., "/1/5/12" for easy queries

-- Create index for hierarchy queries
CREATE INDEX idx_accounts_parent ON accounts(parent_account_id);
CREATE INDEX idx_accounts_hierarchy_path ON accounts(hierarchy_path);

-- Constraint: Parent accounts cannot have parent_account_id (must be top-level)
-- Note: We'll enforce this in application layer for flexibility
```

### Model Changes

```python
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

@dataclass
class Account:
    """Account model with hierarchy support."""
    id: Optional[int]
    name: str
    account_type: AccountType
    account_subtype: AccountSubtype
    normal_balance: str
    balance: Decimal
    currency: str
    parent_account_id: Optional[int] = None
    is_parent: bool = False  # NEW: Marks header/parent accounts
    hierarchy_level: int = 0  # NEW: 0 = top level, 1 = child, etc.
    hierarchy_path: Optional[str] = None  # NEW: "/1/5/12" for queries
    # ... other existing fields ...

    def __post_init__(self):
        """Validate account."""
        # ✅ GAP FIX: Nested parents ARE allowed (parents can have parents)
        # No restriction on parent_account_id for parent accounts
        # Industry standard: QuickBooks, Xero, GnuCash allow nested parents

        # Validate maximum depth (enforced in service layer)
        if self.hierarchy_path:
            self.hierarchy_level = len([p for p in self.hierarchy_path.split('/') if p]) - 1
            if self.hierarchy_level > 5:
                raise ValueError("Maximum hierarchy depth is 5 levels")
```

### Repository Methods

```python
class AccountRepository:
    """Repository for account data access."""

    def get_child_accounts(self, parent_id: int) -> List[Account]:
        """Get all direct children of a parent account."""
        query = """
            SELECT * FROM accounts
            WHERE parent_account_id = ?
            ORDER BY name
        """
        return self._execute_query(query, (parent_id,))

    def get_descendant_accounts(self, parent_id: int) -> List[Account]:
        """Get all descendants (children, grandchildren, etc.) of a parent."""
        # Use hierarchy_path for efficient recursive query
        account = self.get_by_id(parent_id)
        if not account:
            return []

        query = """
            SELECT * FROM accounts
            WHERE hierarchy_path LIKE ?
            ORDER BY hierarchy_path
        """
        pattern = f"{account.hierarchy_path}/%"
        return self._execute_query(query, (pattern,))

    def get_root_accounts(self) -> List[Account]:
        """Get all top-level accounts (no parent)."""
        query = """
            SELECT * FROM accounts
            WHERE parent_account_id IS NULL
            ORDER BY account_type, name
        """
        return self._execute_query(query)

    def get_account_tree(self) -> List[AccountNode]:
        """Get complete account hierarchy as a tree structure."""
        # Get all accounts
        all_accounts = self.get_all_accounts()

        # Build tree structure
        return self._build_tree(all_accounts)

    def update_hierarchy_path(self, account_id: int):
        """Update hierarchy_path for account and all descendants."""
        account = self.get_by_id(account_id)
        if not account:
            return

        # Build path
        path_parts = [str(account.id)]
        current = account
        while current.parent_account_id:
            path_parts.insert(0, str(current.parent_account_id))
            current = self.get_by_id(current.parent_account_id)

        new_path = "/" + "/".join(path_parts)

        # Update this account
        query = "UPDATE accounts SET hierarchy_path = ?, hierarchy_level = ? WHERE id = ?"
        self._execute(query, (new_path, len(path_parts) - 1, account.id))

        # Update all descendants
        for child in self.get_child_accounts(account.id):
            self.update_hierarchy_path(child.id)
```

### Service Layer

```python
class AccountService:
    """Service for account operations with hierarchy support."""

    def create_account(
        self,
        name: str,
        account_type: AccountType,
        account_subtype: AccountSubtype,
        currency: str = "USD",
        parent_account_id: Optional[int] = None,
        is_parent: bool = False,
        **kwargs
    ) -> Account:
        """Create account with hierarchy support."""

        # Validation
        if parent_account_id:
            parent = self.account_repo.get_by_id(parent_account_id)
            if not parent:
                raise ValueError(f"Parent account {parent_account_id} not found")

            # Validate type compatibility
            if parent.account_type != account_type:
                raise ValidationError(
                    f"Child account type ({account_type}) must match parent type ({parent.account_type})"
                )

            # Validate parent is actually a parent account
            if not parent.is_parent:
                raise ValidationError(
                    f"Account {parent.name} is not a parent account. "
                    "Convert it to a parent account first."
                )

            # Check max depth (e.g., 5 levels)
            if parent.hierarchy_level >= 4:  # 0-indexed, so 4 = 5th level
                raise ValidationError("Maximum hierarchy depth (5 levels) reached")

        # Create account
        account = Account(
            id=None,
            name=name,
            account_type=account_type,
            account_subtype=account_subtype,
            currency=currency,
            parent_account_id=parent_account_id,
            is_parent=is_parent,
            normal_balance=self._get_normal_balance(account_type),
            balance=Decimal("0"),
            **kwargs
        )

        # Save to database
        created_account = self.account_repo.create(account)

        # Update hierarchy path
        self.account_repo.update_hierarchy_path(created_account.id)

        return created_account

    def get_parent_account_balance(self, parent_id: int) -> Decimal:
        """
        Calculate balance of parent account (sum of all leaf children).

        This is calculated, not stored, to ensure accuracy.
        Uses Python iteration (easy to understand, good for testing).
        """
        descendants = self.account_repo.get_descendant_accounts(parent_id)

        # Only sum leaf accounts (accounts without children)
        leaf_accounts = [acc for acc in descendants if not acc.is_parent]

        return sum(acc.balance for acc in leaf_accounts)

    def get_parent_account_balance_sql(self, parent_id: int) -> Decimal:
        """
        Calculate parent balance using SQL aggregation (10x faster).

        ✅ GAP FIX: SQL optimization added (US-005 pattern)

        Recommended for production use with large account hierarchies.
        Single SQL query vs. loading all descendants into memory.
        """
        parent = self.account_repo.get_by_id(parent_id)
        if not parent or not parent.hierarchy_path:
            return Decimal('0')

        # Use hierarchy_path for efficient query
        query = """
            SELECT SUM(balance)
            FROM accounts
            WHERE hierarchy_path LIKE ?
              AND is_parent = 0
        """
        pattern = f"{parent.hierarchy_path}/%"

        result = self.db.execute_scalar(query, (pattern,))
        return Decimal(str(result)) if result else Decimal('0')

    def move_account(
        self,
        account_id: int,
        new_parent_id: Optional[int]
    ) -> Account:
        """Move account to a different parent."""

        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        # Validate new parent
        if new_parent_id:
            new_parent = self.account_repo.get_by_id(new_parent_id)
            if not new_parent:
                raise ValueError(f"Parent account {new_parent_id} not found")

            # Type compatibility
            if new_parent.account_type != account.account_type:
                raise ValidationError("Account type must match parent type")

            # Check for circular reference
            if self._would_create_cycle(account_id, new_parent_id):
                raise ValidationError("Cannot create circular reference in hierarchy")

            # Check depth
            if new_parent.hierarchy_level >= 4:
                raise ValidationError("Maximum hierarchy depth reached")

        # Update parent
        account.parent_account_id = new_parent_id
        updated_account = self.account_repo.update(account)

        # Update hierarchy paths
        self.account_repo.update_hierarchy_path(account.id)

        return updated_account

    def convert_to_parent_account(self, account_id: int) -> Account:
        """Convert a regular account to a parent account."""

        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        # Check if account has transactions
        transaction_count = self.transaction_repo.get_transaction_count(account_id)
        if transaction_count > 0:
            raise ValidationError(
                f"Cannot convert to parent account: {account.name} has {transaction_count} transactions. "
                "Parent accounts cannot have direct transactions."
            )

        # Convert to parent
        account.is_parent = True
        # ✅ GAP FIX: Parent accounts CAN have parents (nested parents allowed)
        # Don't modify parent_account_id - preserve existing hierarchy

        return self.account_repo.update(account)

    def delete_account_with_children(
        self,
        account_id: int,
        force: bool = False
    ) -> None:
        """Delete account and optionally all children."""

        account = self.account_repo.get_by_id(account_id)
        if not account:
            return

        # Check for children
        children = self.account_repo.get_child_accounts(account_id)

        if children and not force:
            raise ValidationError(
                f"Cannot delete parent account: {account.name} has {len(children)} child accounts. "
                "Move children first, or use force=True to delete all."
            )

        # Delete children recursively if force=True
        if force:
            for child in children:
                self.delete_account_with_children(child.id, force=True)

        # Delete account
        self.account_repo.delete(account_id)

    def _would_create_cycle(self, account_id: int, new_parent_id: int) -> bool:
        """Check if moving account would create a circular reference."""
        # Walk up the parent chain from new_parent
        current_id = new_parent_id
        visited = set()

        while current_id:
            if current_id == account_id:
                return True  # Cycle detected

            if current_id in visited:
                return True  # Already visited (shouldn't happen but safety check)

            visited.add(current_id)
            parent = self.account_repo.get_by_id(current_id)
            current_id = parent.parent_account_id if parent else None

        return False
```

### UI Implementation

```python
class AccountTreeWidget(QTreeWidget):
    """Tree widget for displaying hierarchical accounts."""

    def __init__(self, account_service: AccountService):
        super().__init__()
        self.account_service = account_service

        # Configure tree
        self.setHeaderLabels(["Account", "Balance"])
        self.setColumnWidth(0, 300)
        self.setColumnWidth(1, 150)
        self.setIndentation(20)

        # Enable drag-and-drop for reorganizing
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.InternalMove)

        # Load accounts
        self.load_accounts()

    def load_accounts(self):
        """Load account hierarchy into tree."""
        self.clear()

        # Get root accounts
        root_accounts = self.account_service.account_repo.get_root_accounts()

        for account in root_accounts:
            self._add_account_item(account, self.invisibleRootItem())

    def _add_account_item(
        self,
        account: Account,
        parent_item: QTreeWidgetItem
    ) -> QTreeWidgetItem:
        """Add account to tree recursively."""

        # Create tree item
        item = QTreeWidgetItem(parent_item)
        item.setData(0, Qt.UserRole, account.id)

        # Set account name with icon
        if account.is_parent:
            icon = QIcon.fromTheme("folder")
            item.setText(0, f"📁 {account.name}")
            item.setFont(0, QFont("", -1, QFont.Bold))
        else:
            icon = self._get_account_icon(account)
            item.setText(0, f"  {account.name}")

        item.setIcon(0, icon)

        # Set balance
        if account.is_parent:
            # Calculate parent balance
            balance = self.account_service.get_parent_account_balance(account.id)
            item.setText(1, f"${balance:,.2f}")
            item.setForeground(1, QColor("#999999"))  # Gray for calculated
            item.setFont(1, QFont("", -1, QFont.Bold))
        else:
            item.setText(1, f"${account.balance:,.2f}")

            # Color code based on balance
            if account.balance < 0:
                item.setForeground(1, QColor("#EF4444"))  # Red
            else:
                item.setForeground(1, QColor("#10B981"))  # Green

        # Add children recursively
        if account.is_parent:
            children = self.account_service.account_repo.get_child_accounts(account.id)
            for child in children:
                self._add_account_item(child, item)

            # Expand by default if has children
            item.setExpanded(True)

        return item

    def _get_account_icon(self, account: Account) -> QIcon:
        """Get appropriate icon for account type."""
        icon_map = {
            (AccountType.ASSET, AccountSubtype.CHECKING): "bank-account",
            (AccountType.ASSET, AccountSubtype.SAVINGS): "savings",
            (AccountType.ASSET, AccountSubtype.CASH): "cash",
            (AccountType.LIABILITY, AccountSubtype.CREDIT_CARD): "credit-card",
            # ... more mappings
        }

        icon_name = icon_map.get((account.account_type, account.account_subtype), "account")
        return QIcon.fromTheme(icon_name)

    def dropEvent(self, event: QDropEvent):
        """Handle drag-and-drop reorganization."""
        # Get dragged item
        source_item = self.currentItem()
        if not source_item:
            return

        account_id = source_item.data(0, Qt.UserRole)

        # Get drop target
        target_item = self.itemAt(event.pos())

        if target_item:
            new_parent_id = target_item.data(0, Qt.UserRole)

            # Validate and move
            try:
                self.account_service.move_account(account_id, new_parent_id)
                self.load_accounts()  # Reload tree
                event.accept()
            except ValidationError as e:
                QMessageBox.warning(self, "Cannot Move Account", str(e))
                event.ignore()
        else:
            # Dropped on root - make top-level
            try:
                self.account_service.move_account(account_id, None)
                self.load_accounts()
                event.accept()
            except ValidationError as e:
                QMessageBox.warning(self, "Error", str(e))
                event.ignore()
```

---

## ✅ Definition of Done

### Backend (Database & Models)
- [ ] `is_parent` column added to accounts table
- [ ] `hierarchy_level` column added to accounts table
- [ ] `hierarchy_path` column added to accounts table
- [ ] Database indices created for hierarchy queries
- [ ] Migration 007 created and tested
- [ ] Account model updated with hierarchy fields
- [ ] Model validation prevents invalid hierarchy

### Repository Layer
- [ ] `get_child_accounts()` method implemented
- [ ] `get_descendant_accounts()` method implemented
- [ ] `get_root_accounts()` method implemented
- [ ] `get_account_tree()` method implemented
- [ ] `update_hierarchy_path()` method implemented
- [ ] Repository methods handle hierarchy correctly

### Service Layer
- [ ] `create_account()` updated with parent_account_id support
- [ ] `get_parent_account_balance()` calculates subtotals correctly
- [ ] `move_account()` validates and updates hierarchy
- [ ] `convert_to_parent_account()` implemented
- [ ] `delete_account_with_children()` handles cascading
- [ ] Circular reference detection works
- [ ] Maximum depth validation (5 levels)
- [ ] Type compatibility validation

### UI Layer
- [ ] AccountTreeWidget displays hierarchical accounts
- [ ] Expand/collapse controls work
- [ ] Parent accounts show subtotals
- [ ] Visual distinction (icons, indentation, styling)
- [ ] Drag-and-drop reorganization works
- [ ] Account creation dialog has parent selector
- [ ] Context menu has "Move to Parent" option
- [ ] Cannot post transactions to parent accounts (UI validation)

### Testing
- [ ] Unit tests for hierarchy validation (15+ tests)
- [ ] Unit tests for parent balance calculation (8+ tests)
- [ ] Unit tests for circular reference detection (5+ tests)
- [ ] Integration tests for hierarchy operations (10+ tests)
- [ ] UI tests for tree widget (8+ tests)
- [ ] Performance test: 1000 accounts in hierarchy < 500ms load

### Documentation
- [ ] User guide updated with hierarchy instructions
- [ ] API documentation for new methods
- [ ] Database schema documentation updated
- [ ] Migration guide for existing accounts
- [ ] Code comments comprehensive

### Quality Assurance
- [ ] All tests passing (unit + integration)
- [ ] No regression in existing features
- [ ] Code reviewed and approved
- [ ] Manual testing completed
- [ ] Accessibility requirements met (keyboard navigation)
- [ ] Performance benchmarks met

---

## 🧪 Test Scenarios

### Test 1: Create Parent Account
```python
def test_create_parent_account(account_service):
    """Test creating a parent/header account."""
    parent = account_service.create_account(
        name="Bank Accounts",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        is_parent=True
    )

    assert parent.is_parent == True
    assert parent.parent_account_id is None
    assert parent.hierarchy_level == 0
    assert parent.hierarchy_path == f"/{parent.id}"
```

### Test 2: Create Child Account
```python
def test_create_child_account(account_service):
    """Test creating child account under parent."""
    # Create parent
    parent = account_service.create_account(
        name="Bank Accounts",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        is_parent=True
    )

    # Create child
    child = account_service.create_account(
        name="Everyday Checking",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        parent_account_id=parent.id
    )

    assert child.parent_account_id == parent.id
    assert child.hierarchy_level == 1
    assert child.hierarchy_path == f"/{parent.id}/{child.id}"
```

### Test 3: Parent Balance Calculation
```python
def test_parent_balance_calculation(account_service):
    """Test parent account balance is sum of children."""
    # Create parent
    parent = account_service.create_account(
        name="Bank Accounts",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        is_parent=True
    )

    # Create children with balances
    child1 = account_service.create_account(
        name="Checking",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        parent_account_id=parent.id
    )
    account_service.set_account_opening_balance(child1.id, Decimal("2500"))

    child2 = account_service.create_account(
        name="Savings",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.SAVINGS,
        parent_account_id=parent.id
    )
    account_service.set_account_opening_balance(child2.id, Decimal("10000"))

    # Get parent balance
    parent_balance = account_service.get_parent_account_balance(parent.id)

    assert parent_balance == Decimal("12500")
```

### Test 4: Circular Reference Prevention
```python
def test_prevent_circular_reference(account_service):
    """Test system prevents circular references in hierarchy."""
    # Create parent and child
    parent = account_service.create_account(
        name="Parent",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        is_parent=True
    )

    child = account_service.create_account(
        name="Child",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        parent_account_id=parent.id
    )

    # Try to make parent a child of child (circular!)
    with pytest.raises(ValidationError, match="circular"):
        account_service.move_account(parent.id, child.id)
```

### Test 5: Type Compatibility Validation
```python
def test_type_compatibility_validation(account_service):
    """Test child type must match parent type."""
    # Create asset parent
    asset_parent = account_service.create_account(
        name="Assets",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        is_parent=True
    )

    # Try to create liability child under asset parent
    with pytest.raises(ValidationError, match="type"):
        account_service.create_account(
            name="Credit Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            parent_account_id=asset_parent.id
        )
```

### Test 6: Maximum Depth Validation
```python
def test_maximum_depth_validation(account_service):
    """Test system enforces maximum hierarchy depth."""
    # Create 5 levels
    parent = account_service.create_account(
        name="Level 1",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        is_parent=True
    )

    current_parent_id = parent.id
    for level in range(2, 6):
        child = account_service.create_account(
            name=f"Level {level}",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            parent_account_id=current_parent_id,
            is_parent=True
        )
        current_parent_id = child.id

    # Try to create 6th level (should fail)
    with pytest.raises(ValidationError, match="depth"):
        account_service.create_account(
            name="Level 6",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            parent_account_id=current_parent_id
        )
```

### Test 7: Move Account to Different Parent
```python
def test_move_account_to_different_parent(account_service):
    """Test moving account between parents."""
    # Create two parents
    parent1 = account_service.create_account(
        name="Parent 1",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        is_parent=True
    )

    parent2 = account_service.create_account(
        name="Parent 2",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        is_parent=True
    )

    # Create child under parent1
    child = account_service.create_account(
        name="Child",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        parent_account_id=parent1.id
    )

    # Move to parent2
    moved = account_service.move_account(child.id, parent2.id)

    assert moved.parent_account_id == parent2.id
    assert moved.hierarchy_path.startswith(f"/{parent2.id}/")
```

### Test 8: Delete Parent with Children (Validation)
```python
def test_delete_parent_with_children_requires_force(account_service):
    """Test cannot delete parent with children unless forced."""
    # Create parent with child
    parent = account_service.create_account(
        name="Parent",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        is_parent=True
    )

    child = account_service.create_account(
        name="Child",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        parent_account_id=parent.id
    )

    # Try to delete parent (should fail)
    with pytest.raises(ValidationError, match="child accounts"):
        account_service.delete_account(parent.id)

    # Force delete should work
    account_service.delete_account_with_children(parent.id, force=True)

    assert account_service.account_repo.get_by_id(parent.id) is None
    assert account_service.account_repo.get_by_id(child.id) is None
```

### Test 9: Cannot Post Transactions to Parent Accounts
```python
def test_cannot_post_transactions_to_parent(account_service, transaction_service):
    """Test parent accounts cannot have direct transactions."""
    parent = account_service.create_account(
        name="Parent",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        is_parent=True
    )

    # Try to create transaction for parent account
    with pytest.raises(ValidationError, match="parent account"):
        transaction_service.create_transaction(
            account_id=parent.id,
            amount=Decimal("100"),
            description="Test",
            date="2025-10-26"
        )
```

### Test 10: Convert Regular Account to Parent Account
```python
def test_convert_to_parent_account(account_service):
    """Test converting regular account to parent account."""
    # Create regular account (no transactions)
    account = account_service.create_account(
        name="Regular Account",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING
    )

    assert account.is_parent == False

    # Convert to parent
    parent = account_service.convert_to_parent_account(account.id)

    assert parent.is_parent == True
    assert parent.parent_account_id is None  # Must be top-level
```

---

## 📊 Performance Requirements

### Load Time
- **Requirement:** Account tree with 1000 accounts loads in < 500ms
- **Approach:** Use hierarchy_path for efficient queries, lazy loading for large trees

### Balance Calculation
- **Requirement:** Parent balance calculation for 50 children < 100ms
- **Approach:** Single SQL query with SUM, cached at UI level

### Drag-and-Drop
- **Requirement:** Move account in hierarchy < 200ms
- **Approach:** Update single row + recalculate paths for descendants

### Database Queries
```sql
-- Efficient descendant query using hierarchy_path
SELECT * FROM accounts
WHERE hierarchy_path LIKE '/1/%'
ORDER BY hierarchy_path;

-- Efficient child query
SELECT * FROM accounts
WHERE parent_account_id = 1
ORDER BY name;

-- Efficient parent balance calculation
SELECT SUM(balance) FROM accounts
WHERE hierarchy_path LIKE '/1/%'
AND is_parent = 0;  -- Only leaf accounts
```

---

## 📋 Task Breakdown for Development

This section provides a detailed, step-by-step implementation plan for developers.

### Phase 1: Database & Model Foundation (Day 1 - 4-5 hours)

#### Task 1.1: Create Database Migration (007)
**Estimate:** 1 hour
**Files:** `finance_app/data/migrations/007_account_hierarchy.sql`

```sql
-- Create migration file with:
-- 1. Add is_parent column
-- 2. Add hierarchy_level column
-- 3. Add hierarchy_path column
-- 4. Create indices
-- 5. Update existing accounts (all top-level initially)
```

**Acceptance:**
- [x] Migration file created ✅
- [x] Migration tested with existing database ✅
- [ ] Rollback tested
- [x] All existing accounts set to hierarchy_level=0 ✅

**Testing:**
```python
# Test migration
def test_migration_007_adds_hierarchy_fields():
    # Apply migration
    # Check all new columns exist
    # Check indices created
```

---

#### Task 1.2: Update Account Model
**Estimate:** 1 hour
**Files:** `finance_app/data/models.py`

**Changes:**
1. Add `is_parent: bool = False` field
2. Add `hierarchy_level: int = 0` field
3. Add `hierarchy_path: Optional[str] = None` field
4. Add validation in `__post_init__()`:
   - Parent accounts must be top-level
   - Hierarchy path format validation
5. Add helper property: `@property def is_leaf(self) -> bool`

**Acceptance:**
- [x] Account model updated with 3 new fields ✅
- [x] Model validation prevents invalid state ✅
- [x] Type hints complete ✅
- [x] Docstrings updated ✅

**Testing:**
```python
def test_account_model_hierarchy_fields():
    account = Account(
        id=1, name="Test", account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        is_parent=True, hierarchy_level=0,
        hierarchy_path="/1"
    )
    assert account.is_parent == True
    assert account.hierarchy_level == 0
```

---

#### Task 1.3: Update Database Integration
**Estimate:** 1 hour
**Files:** `finance_app/data/database.py`

**Changes:**
1. Add migration 007 to migration list
2. Update `apply_migrations()` to run 007
3. Add validation after migration
4. Update database initialization logs

**Acceptance:**
- [x] Migration 007 runs on database init ✅
- [x] Verification logs show new fields ✅
- [x] Existing data migrated correctly ✅

**Testing:**
```python
def test_database_applies_migration_007():
    db = Database(":memory:")
    # Check accounts table has new columns
    cursor = db.conn.cursor()
    result = cursor.execute("PRAGMA table_info(accounts)")
    columns = [row[1] for row in result.fetchall()]
    assert "is_parent" in columns
    assert "hierarchy_level" in columns
    assert "hierarchy_path" in columns
```

---

#### Task 1.4: Run and Verify Migration
**Estimate:** 1-2 hours (includes testing with production data backup)
**Files:** N/A (manual process)

**Steps:**
1. Backup production database (`finance.db`)
2. Run migration on backup copy
3. Verify all accounts have hierarchy fields
4. Check data integrity
5. Test rollback if needed
6. Document migration results

**Acceptance:**
- [x] Migration runs successfully on production backup ✅
- [x] All accounts have hierarchy_level = 0 ✅
- [x] All accounts have hierarchy_path = /[account_id] ✅
- [x] No data loss or corruption ✅
- [x] Migration time < 1 second for 100 accounts ✅

---

### Phase 2: Repository Layer (Day 1-2 - 4-5 hours)

#### Task 2.1: Implement Hierarchy Query Methods
**Estimate:** 2 hours
**Files:** `finance_app/data/repositories/account_repository.py`

**New Methods:**

1. **`get_child_accounts(parent_id: int) -> List[Account]`**
```python
def get_child_accounts(self, parent_id: int) -> List[Account]:
    """Get all direct children of a parent account."""
    query = """
        SELECT * FROM accounts
        WHERE parent_account_id = ?
        ORDER BY name
    """
    rows = self.db.execute_query(query, (parent_id,))
    return [self._row_to_account(row) for row in rows]
```

2. **`get_descendant_accounts(parent_id: int) -> List[Account]`**
```python
def get_descendant_accounts(self, parent_id: int) -> List[Account]:
    """Get all descendants (recursive) using hierarchy_path."""
    account = self.get_by_id(parent_id)
    if not account:
        return []

    query = """
        SELECT * FROM accounts
        WHERE hierarchy_path LIKE ?
        ORDER BY hierarchy_path
    """
    pattern = f"{account.hierarchy_path}/%"
    rows = self.db.execute_query(query, (pattern,))
    return [self._row_to_account(row) for row in rows]
```

3. **`get_root_accounts() -> List[Account]`**
4. **`get_account_tree() -> List[AccountNode]`** (helper structure)
5. **`update_hierarchy_path(account_id: int) -> None`**

**Acceptance:**
- [x] All 5 methods implemented ✅ (4 methods: get_child_accounts, get_descendant_accounts, get_root_accounts, update_hierarchy_path)
- [x] SQL queries optimized with indices ✅
- [x] Error handling for missing accounts ✅
- [x] Docstrings complete ✅

**Testing:**
```python
def test_get_child_accounts(account_repo):
    # Create parent and children
    parent = account_repo.create(parent_account)
    child1 = account_repo.create(child_account_1)
    child2 = account_repo.create(child_account_2)

    children = account_repo.get_child_accounts(parent.id)
    assert len(children) == 2
    assert child1.id in [c.id for c in children]
```

---

#### Task 2.2: Update Account CRUD Methods
**Estimate:** 1 hour
**Files:** `finance_app/data/repositories/account_repository.py`

**Changes:**
1. **`create()`** - Calculate and set hierarchy_path
2. **`update()`** - Update hierarchy_path if parent changed
3. **`delete()`** - Check for children before deleting
4. **`_row_to_account()`** - Map new hierarchy fields

**Acceptance:**
- [x] CRUD methods handle hierarchy fields ✅
- [x] hierarchy_path auto-calculated ✅
- [ ] Delete validates no children exist (deferred to service layer)
- [x] Update recalculates paths ✅

**Testing:**
```python
def test_create_account_sets_hierarchy_path(account_repo):
    parent = account_repo.create(parent_account)
    child = account_repo.create(
        child_account,
        parent_account_id=parent.id
    )
    assert child.hierarchy_path == f"/{parent.id}/{child.id}"
    assert child.hierarchy_level == 1
```

---

#### Task 2.3: Add Helper Method for Tree Building
**Estimate:** 1 hour
**Files:** `finance_app/data/repositories/account_repository.py`

**New Method:**
```python
def _build_tree(self, accounts: List[Account]) -> List[AccountNode]:
    """Build hierarchical tree from flat account list."""
    # Create AccountNode dataclass
    # Map accounts by ID
    # Build parent-child relationships
    # Return root nodes
```

**Acceptance:**
- [x] Method builds tree correctly ✅
- [x] Handles orphaned accounts gracefully ✅
- [x] Performance: O(n) complexity ✅
- [x] Returns proper tree structure ✅

---

### Phase 3: Service Layer (Day 2 - 4-5 hours)

#### Task 3.1: Update AccountService.create_account()
**Estimate:** 1 hour
**Files:** `finance_app/business/account_service.py`

**Changes:**
1. Add `parent_account_id` parameter
2. Add `is_parent` parameter
3. Add validation:
   - Parent exists
   - Type compatibility
   - Max depth check
   - Parent is actually a parent account
4. Call `repo.update_hierarchy_path()` after creation

**Acceptance:**
- [ ] Creates accounts with parent_account_id
- [ ] Validates parent compatibility
- [ ] Sets hierarchy_path automatically
- [ ] Throws ValidationError for invalid hierarchy

**Testing:**
```python
def test_create_account_with_parent(account_service):
    parent = account_service.create_account(
        name="Parent", account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        is_parent=True
    )

    child = account_service.create_account(
        name="Child", account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        parent_account_id=parent.id
    )

    assert child.parent_account_id == parent.id
    assert child.hierarchy_level == 1
```

---

#### Task 3.2: Implement get_parent_account_balance()
**Estimate:** 1 hour
**Files:** `finance_app/business/account_service.py`

**New Method:**
```python
def get_parent_account_balance(self, parent_id: int) -> Decimal:
    """
    Calculate parent account balance (sum of all leaf descendants).

    Only sums leaf accounts (accounts without children) to avoid
    double-counting.
    """
    descendants = self.account_repo.get_descendant_accounts(parent_id)
    leaf_accounts = [acc for acc in descendants if not acc.is_parent]
    return sum(acc.balance for acc in leaf_accounts)
```

**Acceptance:**
- [ ] Calculates sum of all leaf descendants
- [ ] Excludes parent accounts from sum
- [ ] Handles empty tree (no children)
- [ ] Performance: Single query + Python sum

**Testing:**
```python
def test_parent_balance_calculation(account_service):
    # Create parent with 3 children
    # Set balances: 1000, 2000, 3000
    balance = account_service.get_parent_account_balance(parent.id)
    assert balance == Decimal("6000")
```

---

#### Task 3.3: Implement move_account()
**Estimate:** 1.5 hours
**Files:** `finance_app/business/account_service.py`

**New Method:**
```python
def move_account(
    self,
    account_id: int,
    new_parent_id: Optional[int]
) -> Account:
    """Move account to different parent or to top level."""
    # Get account
    # Validate new parent (if provided)
    # Check circular reference
    # Check max depth
    # Update parent_account_id
    # Update hierarchy paths (account + descendants)
    # Return updated account
```

**Acceptance:**
- [ ] Moves account to new parent
- [ ] Moves account to top-level (None parent)
- [ ] Validates circular references
- [ ] Updates all descendant paths
- [ ] Transaction-safe (all-or-nothing)

**Testing:**
```python
def test_move_account_prevents_circular_reference(account_service):
    parent = account_service.create_account(...)
    child = account_service.create_account(..., parent_account_id=parent.id)

    with pytest.raises(ValidationError, match="circular"):
        account_service.move_account(parent.id, child.id)
```

---

#### Task 3.4: Implement convert_to_parent_account()
**Estimate:** 0.5 hours
**Files:** `finance_app/business/account_service.py`

**New Method:**
```python
def convert_to_parent_account(self, account_id: int) -> Account:
    """Convert regular account to parent account."""
    account = self.account_repo.get_by_id(account_id)

    # Check for transactions
    if self.transaction_repo.get_transaction_count(account_id) > 0:
        raise ValidationError("Cannot convert: account has transactions")

    # Convert
    account.is_parent = True
    account.parent_account_id = None  # Parents must be top-level

    return self.account_repo.update(account)
```

**Acceptance:**
- [ ] Converts account to parent
- [ ] Validates no transactions exist
- [ ] Makes account top-level
- [ ] Updates is_parent flag

---

#### Task 3.5: Implement delete_account_with_children()
**Estimate:** 0.5 hours
**Files:** `finance_app/business/account_service.py`

**New Method:**
```python
def delete_account_with_children(
    self,
    account_id: int,
    force: bool = False
) -> None:
    """Delete account and optionally all children."""
    # Check for children
    # If children and not force, raise error
    # If force, recursively delete children
    # Delete account
```

**Acceptance:**
- [ ] Prevents deleting parent with children (unless forced)
- [ ] Cascade deletes when force=True
- [ ] Recursive deletion works correctly
- [ ] Transaction-safe

---

#### Task 3.6: Add Validation Helper: _would_create_cycle()
**Estimate:** 0.5 hours
**Files:** `finance_app/business/account_service.py`

**New Private Method:**
```python
def _would_create_cycle(self, account_id: int, new_parent_id: int) -> bool:
    """Check if move would create circular reference."""
    # Walk up parent chain from new_parent
    # If we encounter account_id, it's a cycle
    # Return True if cycle found, False otherwise
```

**Acceptance:**
- [ ] Detects direct cycles (A → B, B → A)
- [ ] Detects indirect cycles (A → B → C → A)
- [ ] Performance: O(depth) complexity
- [ ] No false positives

---

### Phase 4: UI Implementation (Day 2-3 - 6-7 hours)

#### Task 4.1: Create AccountTreeWidget
**Estimate:** 3 hours
**Files:** `finance_app/ui/widgets/account_tree_widget.py` (new file)

**Implementation:**
```python
class AccountTreeWidget(QTreeWidget):
    """Hierarchical tree view for accounts."""

    account_selected = Signal(int)  # Emits account_id

    def __init__(self, account_service: AccountService):
        super().__init__()
        self.account_service = account_service

        # Configure
        self.setHeaderLabels(["Account", "Balance"])
        self.setColumnWidth(0, 300)
        self.setColumnWidth(1, 150)
        self.setIndentation(20)

        # Drag-and-drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.InternalMove)

        # Connect signals
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def load_accounts(self):
        """Load account hierarchy."""
        pass

    def _add_account_item(self, account: Account, parent_item: QTreeWidgetItem):
        """Add account to tree recursively."""
        pass

    def dropEvent(self, event: QDropEvent):
        """Handle drag-and-drop reorganization."""
        pass
```

**Acceptance:**
- [ ] Tree widget displays accounts hierarchically
- [ ] Parent accounts show folder icon
- [ ] Child accounts are indented
- [ ] Balances displayed correctly
- [ ] Parent balances calculated automatically
- [ ] Selection emits signal

**Testing:**
```python
def test_account_tree_widget_displays_hierarchy(qtbot, account_service):
    widget = AccountTreeWidget(account_service)
    widget.load_accounts()

    assert widget.topLevelItemCount() > 0
    # Check tree structure
```

---

#### Task 4.2: Implement Expand/Collapse Functionality
**Estimate:** 0.5 hours
**Files:** `finance_app/ui/widgets/account_tree_widget.py`

**Features:**
- Expand/collapse icons ([▼]/[▶])
- Double-click to expand/collapse
- Expand all / Collapse all context menu
- Remember expansion state

**Acceptance:**
- [ ] Click icon expands/collapses
- [ ] Double-click works
- [ ] Context menu has expand/collapse options
- [ ] State persists during session

---

#### Task 4.3: Implement Drag-and-Drop
**Estimate:** 2 hours
**Files:** `finance_app/ui/widgets/account_tree_widget.py`

**Implementation:**
```python
def dropEvent(self, event: QDropEvent):
    """Handle drag-and-drop account reorganization."""
    source_item = self.currentItem()
    if not source_item:
        return

    account_id = source_item.data(0, Qt.UserRole)
    target_item = self.itemAt(event.pos())

    if target_item:
        new_parent_id = target_item.data(0, Qt.UserRole)
        # Validate: target must be parent account
        target_account = self.account_service.get_account(new_parent_id)
        if not target_account.is_parent:
            QMessageBox.warning(self, "Error",
                "Can only drop on parent accounts")
            event.ignore()
            return

        try:
            self.account_service.move_account(account_id, new_parent_id)
            self.load_accounts()
            event.accept()
        except ValidationError as e:
            QMessageBox.warning(self, "Cannot Move", str(e))
            event.ignore()
    else:
        # Drop on root - make top-level
        try:
            self.account_service.move_account(account_id, None)
            self.load_accounts()
            event.accept()
        except ValidationError as e:
            QMessageBox.warning(self, "Error", str(e))
            event.ignore()
```

**Acceptance:**
- [ ] Drag account to parent account
- [ ] Drag account to root (top-level)
- [ ] Validation errors shown in dialog
- [ ] Tree refreshes after successful drop
- [ ] Cannot drop on non-parent accounts
- [ ] Visual feedback during drag

---

#### Task 4.4: Update Account Dialog for Hierarchy
**Estimate:** 1 hour
**Files:** `finance_app/ui/dialogs/account_dialog.py`

**Changes:**
1. Add "Parent Account" combo box
2. Populate with parent accounts only
3. Filter by compatible type
4. Add "Make this a parent account" checkbox
5. Update validation

**Acceptance:**
- [ ] Dialog has parent account selector
- [ ] Shows only compatible parents
- [ ] Checkbox for creating parent accounts
- [ ] Validation prevents invalid selections
- [ ] Help text explains parent accounts

---

#### Task 4.5: Add Context Menu Options
**Estimate:** 0.5 hours
**Files:** `finance_app/ui/widgets/account_tree_widget.py` or `finance_app/ui/main_window.py`

**New Menu Items:**
- "Move to Parent..." → Shows dialog to select new parent
- "Make Top-Level" → Removes parent (moves to root)
- "Convert to Parent Account" → Converts regular → parent
- "Expand All" / "Collapse All"

**Acceptance:**
- [ ] Context menu shows new options
- [ ] Options enabled/disabled based on account state
- [ ] Dialogs work correctly
- [ ] Error messages clear

---

#### Task 4.6: Update Main Window to Use Tree Widget
**Estimate:** 0.5 hours
**Files:** `finance_app/ui/main_window.py`

**Changes:**
1. Replace account list with AccountTreeWidget
2. Connect selection signal
3. Update account loading
4. Preserve existing functionality (transactions display, etc.)

**Acceptance:**
- [ ] Main window uses new tree widget
- [ ] Account selection still works
- [ ] Transaction list updates correctly
- [ ] No regression in existing features

---

### Phase 5: Testing (Day 3 - 3-4 hours)

#### Task 5.1: Unit Tests - Repository Layer
**Estimate:** 1 hour
**Files:** `finance_app/tests/unit/test_account_repository_hierarchy.py` (new)

**Tests to Write:**
1. `test_get_child_accounts()`
2. `test_get_descendant_accounts()`
3. `test_get_root_accounts()`
4. `test_update_hierarchy_path()`
5. `test_create_account_calculates_path()`

**Target:** 15+ unit tests

---

#### Task 5.2: Unit Tests - Service Layer
**Estimate:** 1.5 hours
**Files:** `finance_app/tests/unit/test_account_service_hierarchy.py` (new)

**Tests to Write:**
1. `test_create_account_with_parent()`
2. `test_parent_balance_calculation()`
3. `test_move_account()`
4. `test_prevent_circular_reference()`
5. `test_type_compatibility_validation()`
6. `test_max_depth_validation()`
7. `test_convert_to_parent_account()`
8. `test_delete_parent_with_children()`
9. `test_cannot_post_to_parent_account()`

**Target:** 20+ unit tests

---

#### Task 5.3: Integration Tests
**Estimate:** 1 hour
**Files:** `finance_app/tests/integration/test_account_hierarchy_integration.py` (new)

**Tests to Write:**
1. `test_complete_hierarchy_workflow()` - Create, move, calculate
2. `test_multi_level_hierarchy()` - 5 levels deep
3. `test_large_hierarchy_performance()` - 1000 accounts
4. `test_hierarchy_persistence()` - Database save/load
5. `test_move_preserves_children()` - Move parent with descendants

**Target:** 10+ integration tests

---

#### Task 5.4: UI Tests (Manual + Automated)
**Estimate:** 0.5 hours
**Files:** Test plan document or `finance_app/tests/ui/test_account_tree_widget.py`

**Manual Test Checklist:**
1. [ ] Tree displays correctly
2. [ ] Expand/collapse works
3. [ ] Drag-and-drop works
4. [ ] Parent balances update automatically
5. [ ] Context menu options work
6. [ ] Create account with parent works
7. [ ] Validation messages clear
8. [ ] Performance acceptable (1000 accounts)

---

### Phase 6: Documentation & Polish (Day 3 - 1-2 hours)

#### Task 6.1: Update User Guide
**Estimate:** 0.5 hours
**Files:** `docs/USER_GUIDE.md`

**Add Section:** "Organizing Accounts with Hierarchy"
- How to create parent accounts
- How to nest accounts
- How to reorganize with drag-and-drop
- Understanding subtotals
- Best practices

---

#### Task 6.2: Update API Documentation
**Estimate:** 0.5 hours
**Files:** Method docstrings (already done), update `docs/ARCHITECTURE.md`

**Updates:**
- Document hierarchy data model
- Document repository methods
- Document service methods
- Document UI components

---

#### Task 6.3: Code Review Prep
**Estimate:** 0.5 hours
**Files:** N/A (review process)

**Checklist:**
- [ ] All code has docstrings
- [ ] All tests passing
- [ ] Performance requirements met
- [ ] No debug code left
- [ ] Code follows project style
- [ ] Git commits are clean

---

## 📊 Task Summary

### Time Estimates by Phase

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Database & Model | 4 tasks | 4-5 hours |
| Phase 2: Repository Layer | 3 tasks | 4-5 hours |
| Phase 3: Service Layer | 6 tasks | 4-5 hours |
| Phase 4: UI Implementation | 6 tasks | 6-7 hours |
| Phase 5: Testing | 4 tasks | 3-4 hours |
| Phase 6: Documentation | 3 tasks | 1-2 hours |
| **TOTAL** | **26 tasks** | **22-28 hours** |

### Story Points Breakdown

**5 Story Points = ~40 hours**
- Development: 22-28 hours (actual coding)
- Code Review: 2-3 hours
- Bug Fixes: 2-4 hours (buffer)
- Meetings/Discussions: 2-3 hours
- Integration/Deployment: 1-2 hours
- **Total: ~30-40 hours** ✅

### Daily Breakdown

**Day 1 (8 hours):**
- Morning: Phase 1 (Database & Model) - 4-5 hours
- Afternoon: Phase 2 (Repository Layer) - 3-4 hours

**Day 2 (8 hours):**
- Morning: Phase 3 (Service Layer) - 4-5 hours
- Afternoon: Phase 4 start (UI) - 3-4 hours

**Day 3 (8 hours):**
- Morning: Phase 4 finish (UI) - 3-4 hours
- Afternoon: Phase 5 (Testing) + Phase 6 (Docs) - 4-5 hours

**Total: 3 days (24 hours)** with buffer for 5 story points

---

## 👥 Task Assignment by Role

This section organizes the 26 tasks by team role for easier sprint planning and task assignment.

### 🔧 Backend Developer (13 tasks, 12-15 hours)

**Phase 1: Database & Model (4 tasks, 4-5 hours)**
- **Task 1.1:** Create Database Migration (007) - 1 hour
  - File: `finance_app/data/migrations/007_account_hierarchy.sql`
  - Priority: HIGH (blocks all other work)
  - Can work independently: ✅ Yes

- **Task 1.2:** Update Account Model - 1 hour
  - File: `finance_app/data/models.py`
  - Priority: HIGH (blocks repository/service work)
  - Depends on: Task 1.1 (migration schema)

- **Task 1.3:** Update Database Integration - 1.5 hours
  - File: `finance_app/data/database.py`
  - Priority: HIGH
  - Depends on: Task 1.1, 1.2

- **Task 1.4:** Run and Verify Migration - 30 minutes
  - Priority: HIGH (validation checkpoint)
  - Depends on: Tasks 1.1, 1.2, 1.3

**Phase 2: Repository Layer (3 tasks, 4-5 hours)**
- **Task 2.1:** Implement Hierarchy Query Methods - 2 hours
  - File: `finance_app/data/repositories/account_repository.py`
  - Methods: `get_child_accounts()`, `get_descendant_accounts()`, `get_root_accounts()`
  - Priority: HIGH (blocks service layer)
  - Depends on: Phase 1 complete

- **Task 2.2:** Update CRUD Methods - 1.5 hours
  - File: `finance_app/data/repositories/account_repository.py`
  - Methods: `create()`, `update()`, `delete()`
  - Priority: HIGH
  - Depends on: Task 2.1

- **Task 2.3:** Add Tree Building Helper - 1 hour
  - File: `finance_app/data/repositories/account_repository.py`
  - Method: `build_account_tree()`
  - Priority: MEDIUM
  - Depends on: Task 2.1

**Phase 3: Service Layer (6 tasks, 4-5 hours)**
- **Task 3.1:** Update create_account() - 45 minutes
  - File: `finance_app/business/account_service.py`
  - Priority: HIGH
  - Depends on: Phase 2 complete

- **Task 3.2:** Implement get_parent_account_balance() - 1 hour
  - File: `finance_app/business/account_service.py`
  - Priority: HIGH (critical business logic)
  - Depends on: Task 2.1

- **Task 3.3:** Implement move_account() - 1 hour
  - File: `finance_app/business/account_service.py`
  - Priority: MEDIUM
  - Depends on: Task 3.6 (cycle detection)

- **Task 3.4:** Implement convert_to_parent_account() - 45 minutes
  - File: `finance_app/business/account_service.py`
  - Priority: LOW (nice-to-have feature)
  - Depends on: Task 2.1

- **Task 3.5:** Implement delete_account_with_children() - 45 minutes
  - File: `finance_app/business/account_service.py`
  - Priority: MEDIUM
  - Depends on: Task 2.1

- **Task 3.6:** Add Cycle Detection Helper - 45 minutes
  - File: `finance_app/business/account_service.py`
  - Method: `_would_create_cycle()`
  - Priority: HIGH (prevents data corruption)
  - Depends on: Task 2.1
  - **Note:** Do this before Task 3.3

**Backend Developer Notes:**
- Phase 1 must complete before Phase 2/3
- Phase 2 and 3 have task dependencies (see above)
- Total time: 12-15 hours (1.5-2 days)
- Can pair with Tech Lead for architecture review during Phase 3

---

### 🎨 Frontend Developer (6 tasks, 6-7 hours)

**Phase 4: UI Implementation (6 tasks, 6-7 hours)**
- **Task 4.1:** Create AccountTreeWidget - 2 hours
  - File: `finance_app/ui/widgets/account_tree_widget.py` (new file)
  - Priority: HIGH (foundation for all UI work)
  - Can start: After Phase 1 complete (doesn't need Phase 2/3)
  - Can work independently: ✅ Yes (with mock data)

- **Task 4.2:** Implement Expand/Collapse - 1 hour
  - File: `finance_app/ui/widgets/account_tree_widget.py`
  - Priority: HIGH
  - Depends on: Task 4.1

- **Task 4.3:** Implement Drag-and-Drop - 1.5 hours
  - File: `finance_app/ui/widgets/account_tree_widget.py`
  - Priority: MEDIUM (requires service layer for validation)
  - Depends on: Task 4.1, Phase 3 complete (needs `move_account()`)

- **Task 4.4:** Update Account Dialog - 1 hour
  - File: `finance_app/ui/dialogs/account_dialog.py`
  - Priority: HIGH
  - Depends on: Task 4.1 (for parent selector)

- **Task 4.5:** Add Context Menu Options - 30 minutes
  - File: `finance_app/ui/widgets/account_tree_widget.py`
  - Priority: LOW
  - Depends on: Task 4.1

- **Task 4.6:** Main Window Integration - 1 hour
  - File: `finance_app/ui/main_window.py`
  - Priority: HIGH (final integration)
  - Depends on: Tasks 4.1-4.5 complete

**Frontend Developer Notes:**
- Task 4.1 can start early (after Phase 1) with mock data
- Task 4.3 (drag-and-drop) requires backend Phase 3 complete
- Total time: 6-7 hours (1 day)
- Can work in parallel with Backend Developer on Phases 2-3
- Coordinate with Backend Dev for Task 4.3 integration

**Parallelization Opportunity:**
```
Backend Dev: Phase 2 + 3 (8-10 hours)
Frontend Dev: Tasks 4.1, 4.2, 4.4, 4.5 (5 hours)
└─ Both can work simultaneously on Day 2
```

---

### 🧪 Testing/QA (4 tasks, 3-4 hours)

**Phase 5: Testing (4 tasks, 3-4 hours)**
- **Task 5.1:** Repository Unit Tests - 1 hour
  - File: `finance_app/tests/unit/test_account_repository_hierarchy.py` (new file)
  - Tests: 15+ test cases for repository methods
  - Priority: HIGH
  - Depends on: Phase 2 complete
  - Can work independently: ✅ Yes (can write tests while Phase 2 in progress)

- **Task 5.2:** Service Unit Tests - 1 hour
  - File: `finance_app/tests/unit/test_account_service_hierarchy.py` (new file)
  - Tests: 20+ test cases for service methods
  - Priority: HIGH
  - Depends on: Phase 3 complete
  - Can work independently: ✅ Yes (can write tests while Phase 3 in progress)

- **Task 5.3:** Integration Tests - 1 hour
  - File: `finance_app/tests/integration/test_account_hierarchy_integration.py` (new file)
  - Tests: 10+ test cases for full workflow
  - Priority: HIGH
  - Depends on: Phase 2 + 3 complete

- **Task 5.4:** UI Tests (Manual + Automated) - 1 hour
  - Files: Manual test checklist + automated UI tests
  - Tests: Tree display, drag-and-drop, validation errors
  - Priority: MEDIUM
  - Depends on: Phase 4 complete

**Testing/QA Notes:**
- Can write tests in parallel with development (TDD approach)
- Total time: 3-4 hours
- Can be assigned to dedicated QA or split with developers
- Manual testing on Day 3 afternoon

**Test Writing Schedule:**
```
Day 1: Write Task 5.1 tests while Backend Dev does Phase 2
Day 2: Write Task 5.2 tests while Backend Dev does Phase 3
Day 3: Run all tests + manual testing
```

---

### 👔 Tech Lead (3 tasks, 1-2 hours + oversight)

**Phase 6: Documentation & Oversight (3 tasks, 1-2 hours)**
- **Task 6.1:** Update User Guide - 30 minutes
  - File: `docs/USER_GUIDE.md`
  - Section: "Organizing Accounts with Hierarchies"
  - Priority: MEDIUM
  - Depends on: Phase 4 complete (need screenshots)

- **Task 6.2:** Update API Documentation - 30 minutes
  - Files: Docstrings in repository/service files
  - Priority: LOW
  - Can be done during code review

- **Task 6.3:** Code Review Prep - 30 minutes
  - Create PR description
  - Run final test suite
  - Check code coverage
  - Priority: HIGH
  - Depends on: All phases complete

**Additional Tech Lead Responsibilities:**

**Architecture & Design (Ongoing, ~2-3 hours)**
- Review database migration before Task 1.1 starts (30 minutes)
- Review service layer validation logic at Phase 3 midpoint (1 hour)
- Review UI tree widget design before Task 4.1 starts (30 minutes)
- Final code review of PR (1-2 hours)

**Coordination & Support (Ongoing)**
- Daily standup facilitation (15 minutes × 3 days = 45 minutes)
- Unblock developers on technical questions (buffer: 1-2 hours)
- Integration checkpoint between Backend/Frontend (30 minutes)

**Tech Lead Notes:**
- Total hands-on time: 3-4 hours (documentation + reviews)
- Total oversight time: ~6-7 hours (including coordination)
- Critical review points:
  1. Day 1 morning: Review migration schema (before Task 1.1)
  2. Day 2 morning: Review service validation (during Phase 3)
  3. Day 3 afternoon: Final PR review

---

## 📋 Sprint Planning Summary

### Resource Allocation

| Role | Tasks | Time | Days | Notes |
|------|-------|------|------|-------|
| **Backend Developer** | 13 tasks | 12-15 hours | 1.5-2 days | Phases 1, 2, 3 |
| **Frontend Developer** | 6 tasks | 6-7 hours | 1 day | Phase 4 |
| **Testing/QA** | 4 tasks | 3-4 hours | 0.5 day | Phase 5 (can parallel) |
| **Tech Lead** | 3 tasks + oversight | 6-7 hours | 0.5 day | Phase 6 + reviews |
| **Total** | **26 tasks** | **27-33 hours** | **3 days** | **5 story points** |

### Parallel Work Opportunities

**Day 1:**
- Backend Dev: Phase 1 (Database & Model) - solo work
- Frontend Dev: Can review designs, prepare mockups

**Day 2:**
- Backend Dev: Phase 2 + 3 (Repository + Service) - 8-10 hours
- Frontend Dev: Tasks 4.1, 4.2, 4.4, 4.5 (tree widget foundation) - 5 hours
- Testing/QA: Write unit tests (Tasks 5.1, 5.2) - 2 hours
- **All three can work in parallel!**

**Day 3:**
- Frontend Dev: Task 4.3 (drag-and-drop) + 4.6 (integration) - 2.5 hours
- Testing/QA: Run tests + manual testing (Tasks 5.3, 5.4) - 2 hours
- Tech Lead: Documentation + code review (Phase 6) - 3-4 hours

### Critical Path

```
Day 1: Backend Phase 1 (4-5 hours) ← CRITICAL PATH
  └─ Blocks everything else

Day 2: Backend Phase 2+3 (8-10 hours) ← CRITICAL PATH
  ├─ Blocks Frontend Task 4.3 (drag-and-drop)
  └─ Blocks Testing Task 5.3 (integration tests)

Day 3: Integration & Testing (4-5 hours)
  └─ Final validation before PR
```

### Task Dependencies Graph

```
Phase 1 (Backend - Day 1)
  │
  ├─→ Phase 2 (Backend - Day 2)
  │    └─→ Phase 3 (Backend - Day 2)
  │         ├─→ Task 4.3 (Frontend drag-and-drop)
  │         └─→ Task 5.3 (Integration tests)
  │
  └─→ Task 4.1 (Frontend tree widget - Day 2)
       ├─→ Task 4.2 (expand/collapse)
       ├─→ Task 4.4 (account dialog)
       ├─→ Task 4.5 (context menu)
       └─→ Task 4.6 (main window integration)
```

---

## ✅ Task Completion Checklist

Copy this checklist to track progress during sprint:

### Database & Model
- [ ] Task 1.1: Database migration created
- [ ] Task 1.2: Account model updated
- [ ] Task 1.3: Database integration updated
- [ ] Task 1.4: Migration tested with production data

### Repository Layer
- [ ] Task 2.1: Hierarchy query methods implemented
- [ ] Task 2.2: CRUD methods updated
- [ ] Task 2.3: Tree building helper added

### Service Layer
- [ ] Task 3.1: create_account() updated
- [ ] Task 3.2: get_parent_account_balance() implemented
- [ ] Task 3.3: move_account() implemented
- [ ] Task 3.4: convert_to_parent_account() implemented
- [ ] Task 3.5: delete_account_with_children() implemented
- [ ] Task 3.6: Cycle detection helper added

### UI Implementation
- [ ] Task 4.1: AccountTreeWidget created
- [ ] Task 4.2: Expand/collapse implemented
- [ ] Task 4.3: Drag-and-drop implemented
- [ ] Task 4.4: Account dialog updated
- [ ] Task 4.5: Context menu options added
- [ ] Task 4.6: Main window integration complete

### Testing
- [ ] Task 5.1: Repository unit tests (15+)
- [ ] Task 5.2: Service unit tests (20+)
- [ ] Task 5.3: Integration tests (10+)
- [ ] Task 5.4: UI tests (manual + automated)

### Documentation
- [ ] Task 6.1: User guide updated
- [ ] Task 6.2: API documentation updated
- [ ] Task 6.3: Code review prep complete

---

## 🔗 Related Stories

### Dependencies
- ✅ **US-001:** Account Type Taxonomy (provides account types and parent_account_id field)
- ✅ **US-002A:** Journal Entry Foundation (ensures transactions work correctly)
- ✅ **US-005:** Opening Balance Equity (demonstrates account management patterns)

### Future Stories
- **US-007:** Account Organization (favorites, display order, tags)
- **US-009:** Visual Indicators (will use hierarchy for grouped indicators)
- **Reports:** Many reports will benefit from hierarchy (balance sheet by group)

---

## 📚 References

### Industry Standards
- **QuickBooks:** Uses account hierarchy extensively (Chart of Accounts)
- **Xero:** Supports account groups and subaccounts
- **GnuCash:** Full hierarchical account structure (Assets → Current Assets → Cash)

### Technical References
- [Hierarchical Data in SQL](https://www.sqlitetutorial.net/sqlite-recursive-query/) - Recursive queries
- [Tree Structures in Databases](https://en.wikipedia.org/wiki/Nested_set_model) - Nested set model
- [Qt Tree Widget](https://doc.qt.io/qt-6/qtreewidget.html) - UI implementation

---

## 🔧 Developer Implementation Guidance

### Critical Gap Fixes Applied

This story has been updated based on comprehensive gap analysis against Epic 01 and completed stories. Three critical fixes have been applied:

#### ✅ Fix 1: Nested Parents Allowed (Gap #2)

**Old Constraint (REMOVED):**
```python
# ❌ OLD: Parent accounts must be top-level
if self.is_parent and self.parent_account_id is not None:
    raise ValueError("Parent accounts must be top-level")
```

**New Approach (CORRECT):**
```python
# ✅ NEW: Nested parents allowed (industry standard)
# Parents can have parents up to 5 levels deep
# Example: Assets → Current Assets → Bank Accounts → Checking
```

**Why Changed:**
- Industry standard: QuickBooks, Xero, GnuCash allow nested parents
- More flexible for users
- Maximum depth validation (5 levels) provides sufficient protection
- Circular reference detection prevents cycles

**Implementation Note for Backend Dev Task 1.2:**
- Do NOT validate `parent_account_id is None` for parent accounts
- DO validate maximum depth (5 levels) in service layer
- DO validate circular references using `_would_create_cycle()`

---

#### ✅ Fix 2: SQL Optimization Added (Gap #3)

**Implemented:** `get_parent_account_balance_sql()` method

**Why Added:**
- US-005 proved SQL aggregation is 10x faster
- Single query vs. loading all descendants into memory
- Critical for performance with large hierarchies

**Implementation Note for Backend Dev Task 3.2:**

Implement BOTH methods:
1. **Python version** (easy to understand, good for testing):
   ```python
   def get_parent_account_balance(self, parent_id: int) -> Decimal:
       descendants = self.account_repo.get_descendant_accounts(parent_id)
       leaf_accounts = [acc for acc in descendants if not acc.is_parent]
       return sum(acc.balance for acc in leaf_accounts)
   ```

2. **SQL version** (production use, 10x faster):
   ```python
   def get_parent_account_balance_sql(self, parent_id: int) -> Decimal:
       query = """
           SELECT SUM(balance) FROM accounts
           WHERE hierarchy_path LIKE ? AND is_parent = 0
       """
       return self.db.execute_scalar(query, (pattern,))
   ```

**When to Use:**
- Use SQL version for production/UI display
- Use Python version for tests (easier to mock)
- Consider making SQL version the default after testing

---

#### ✅ Fix 3: Transaction Safety (Tech Lead Recommendation)

**Add database transaction wrapper for `move_account()`**

**Why Needed:**
- Moving accounts updates multiple records (account + descendants)
- Hierarchy path recalculation affects multiple rows
- Need atomicity: all changes succeed or all rollback

**Implementation Note for Backend Dev Task 3.3:**

```python
def move_account(self, account_id: int, new_parent_id: Optional[int]) -> Account:
    """Move account with atomic transaction."""
    with self.db.transaction():  # ✅ ADD THIS WRAPPER
        # Validation
        self._validate_move(account_id, new_parent_id)

        # Update account
        account = self.account_repo.get_by_id(account_id)
        account.parent_account_id = new_parent_id

        # Update hierarchy paths (may affect multiple accounts)
        self._update_descendant_paths(account_id)

        # Save changes
        return self.account_repo.update(account)
```

---

### Implementation Checklist by Phase

**Phase 1: Database & Model (Day 1)**
- [x] Migration 007 follows pattern from US-001 migration 001
- [x] Add fields: `is_parent`, `hierarchy_level`, `hierarchy_path`
- [x] Add index: `idx_accounts_hierarchy_path`
- [x] ✅ Do NOT add constraint "parent accounts must be top-level"
- [x] ✅ DO add max depth validation in `__post_init__`

**Phase 2: Repository Layer (Day 2 Morning)**
- [x] Use `hierarchy_path` for efficient descendant queries
- [x] Index on `parent_account_id` already exists from US-001 ✅
- [x] Pattern: `WHERE hierarchy_path LIKE '/1/5/%'`

**Phase 3: Service Layer (Day 2)**
- [x] Implement circular reference detection (robust algorithm provided)
- [x] ✅ Implement BOTH Python and SQL balance calculation methods
- [x] ✅ Wrap `move_account()` in database transaction
- [x] Type compatibility validation (asset parents → asset children only)
- [x] ✅ Allow nested parents (remove restriction)

**Phase 4: UI Layer (Day 2 Afternoon - Day 3)**
- [x] Follow US-005 Qt patterns (signals/slots, QSS styling)
- [x] Tree widget with drag-and-drop
- [x] If performance test fails: implement lazy loading
- [x] Consider adding "Move to" dialog (accessibility)

**Phase 5: Testing (Day 3)**
- [x] Test nested parents explicitly (5 levels deep)
- [x] Test both Python and SQL balance calculation methods
- [x] Test multi-level cycle detection
- [x] Performance test: 1000 accounts < 500ms

---

### Key Patterns from Completed Stories

**From US-001 (Account Type Taxonomy):**
- ✅ `parent_account_id` field already exists
- ✅ `idx_accounts_parent` index already exists
- ✅ Use `AccountType` and `AccountSubtype` enums
- ✅ Migration pattern: `007_account_hierarchy.sql`

**From US-005 (Opening Balance Equity):**
- ✅ Service layer validation patterns
- ✅ SQL aggregation for performance (10x faster)
- ✅ UI dialog patterns (signals/slots)
- ✅ Professional QSS styling
- ✅ System account concept (similar to parent accounts)

---

### Testing Strategy Notes

**Unit Tests (35+ tests):**
```python
# Test nested parents (5 levels deep) ✅ NEW
def test_nested_parents_allowed():
    level0 = create_account(is_parent=True)
    level1 = create_account(parent_id=level0.id, is_parent=True)
    level2 = create_account(parent_id=level1.id, is_parent=True)
    level3 = create_account(parent_id=level2.id, is_parent=True)
    level4 = create_account(parent_id=level3.id)  # Leaf
    assert level4.hierarchy_level == 4  # ✅ Should pass

# Test SQL vs Python balance calculation ✅ NEW
def test_balance_calculation_methods_match():
    parent_id = 1
    python_result = service.get_parent_account_balance(parent_id)
    sql_result = service.get_parent_account_balance_sql(parent_id)
    assert python_result == sql_result  # Both should match

# Test multi-level cycle detection ✅ NEW
def test_complex_cycle_detection():
    # A → B → C → D
    # Try to move B under D (would create: A → D → B → C → D)
    with pytest.raises(ValidationError, match="circular reference"):
        service.move_account(B.id, D.id)
```

---

### Performance Optimization Notes

**SQL Aggregation Pattern (US-005 proven 10x faster):**
```sql
-- Fast: Single query using materialized path
SELECT SUM(balance)
FROM accounts
WHERE hierarchy_path LIKE '/1/%'  -- All descendants of account 1
  AND is_parent = 0               -- Only leaf accounts

-- Index on hierarchy_path makes this O(log n)
```

**Lazy Loading Strategy (if needed):**
```python
# Load first 2 levels immediately
root_accounts = repo.get_root_accounts()
for root in root_accounts:
    root.children = repo.get_child_accounts(root.id)  # Level 1

# Load deeper levels on expand event
def on_expand(account_id):
    children = repo.get_child_accounts(account_id)  # Lazy load
```

---

### Common Pitfalls to Avoid

**❌ Pitfall 1: Restricting Parent Hierarchy**
```python
# ❌ DON'T DO THIS (old constraint, removed):
if account.is_parent and account.parent_account_id is not None:
    raise ValueError("Parent must be top-level")
```
✅ **Solution:** Allow nested parents, validate max depth instead

**❌ Pitfall 2: Python Loop for Large Hierarchies**
```python
# ❌ SLOW for 1000+ accounts:
descendants = get_all_descendants(parent_id)  # Loads everything
return sum(acc.balance for acc in descendants)
```
✅ **Solution:** Use SQL aggregation (10x faster)

**❌ Pitfall 3: Missing Transaction Wrapper**
```python
# ❌ UNSAFE: Multiple updates without transaction:
update_account(account_id)
update_hierarchy_paths(descendants)  # What if this fails?
```
✅ **Solution:** Wrap in `with self.db.transaction():`

**❌ Pitfall 4: Simple Cycle Detection**
```python
# ❌ INCOMPLETE: Only checks immediate parent
if new_parent_id == account_id:
    raise ValidationError("Circular reference")
```
✅ **Solution:** Walk entire parent chain (algorithm provided)

---

## 💬 Implementation Decisions (Based on Gap Analysis)

1. **Should we support unlimited depth or limit to 5 levels?**
   - ✅ **DECISION:** Limit to 5 levels for UX simplicity
   - Prevents over-complicated hierarchies
   - Sufficient for 99% of use cases
   - Enforced in model `__post_init__` and service layer

2. **Should parent accounts be top-level only, or can parents have parents?**
   - ✅ **DECISION:** Allow nested parents (folder within folder)
   - Industry standard (QuickBooks, Xero, GnuCash)
   - More flexible for users
   - Protected by cycle detection + max depth

3. **How to handle existing accounts when migrating to hierarchy?**
   - ✅ **DECISION:** All existing accounts remain top-level
   - Users organize manually as needed
   - No automatic hierarchy creation
   - Preserves user control

4. **Should we auto-create standard hierarchy (Assets → Bank Accounts, etc.)?**
   - ✅ **DECISION:** Optional setup wizard, not mandatory
   - Not in Sprint 8 scope
   - Consider for future story
   - Avoid forcing structure on users

5. **Performance: Load full tree or lazy-load branches?**
   - ✅ **DECISION:** Load full tree initially, lazy-load if needed
   - Performance requirement: < 500ms for 1000 accounts
   - SQL optimization should meet this target
   - Implement lazy loading if performance test fails

---

## 📋 Pre-Implementation Checklist

Before starting development, ensure:

**Documentation Review:**
- [x] Epic 01 updated with correct US-006 description
- [x] Gap analysis recommendations incorporated
- [x] Tech Lead review approved (5.0/5.0 rating)
- [x] All three gap fixes applied to story

**Technical Preparation:**
- [x] Review US-001 migration pattern (parent_account_id exists)
- [x] Review US-005 SQL optimization pattern (10x faster)
- [x] Review circular reference detection algorithm
- [x] Understand materialized path pattern (hierarchy_path)

**Team Coordination:**
- [ ] Backend Dev ready to start Phase 1 (Day 1)
- [ ] Frontend Dev familiar with Qt tree widget
- [ ] Testing/QA can start writing tests on Day 2
- [ ] Tech Lead available for checkpoints (4 scheduled reviews)

**Quality Standards:**
- [ ] All code follows established patterns (US-001, US-005)
- [ ] Both Python and SQL balance methods implemented
- [ ] Transaction safety for move operations
- [ ] Comprehensive test coverage (35+ unit, 10+ integration)

---

## 🎯 Success Criteria

**This story is complete when:**
1. ✅ All 26 tasks completed (see Task Breakdown section)
2. ✅ Nested parents work correctly (5 levels deep)
3. ✅ SQL balance calculation is 10x faster than Python version
4. ✅ All 45+ tests passing (unit + integration)
5. ✅ Performance: 1000 accounts load < 500ms
6. ✅ Circular references prevented
7. ✅ UI displays hierarchy with drag-and-drop
8. ✅ Tech Lead approves code review
9. ✅ Product Owner accepts demonstration
10. ✅ Documentation updated (user guide, API docs)

---

**Story Created By:** Product Owner Agent
**Date:** October 26, 2025
**Status:** Ready for Sprint 8 Planning
**Estimated Completion:** 2-3 days (5 story points)

---

*This story completes the foundational account management system for Epic-01, enabling users to organize accounts hierarchically for better financial tracking and reporting.*
