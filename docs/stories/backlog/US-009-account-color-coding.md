# US-009: Account Color Coding & Visual Indicators

**Story ID:** US-009
**Epic:** [EPIC-001: Account Management & Double-Entry Foundation](../../epics/EPIC-001-account-management.md)
**Created:** 2025-10-27
**Updated:** 2025-10-27 (Product Owner refinement - comprehensive task breakdown added)
**Status:** Backlog (Ready for Sprint 10)
**Priority:** P1 (Should Have)
**Story Points:** 5 (13-14 hours estimated)
**Assignee:** Unassigned
**Sprint:** Sprint 10 (Planned)
**Dependencies:** ✅ US-001 (Account Type Taxonomy), ✅ US-006 (Account Hierarchy - tree widget integration)
**Blocks:** 📋 US-007 (Account Metadata - depends on Migration 010 fields)

---

## 📖 User Story

**As a** user
**I want** accounts to have color-coded icons and visual indicators
**So that** I can quickly identify account types, status, and important information at a glance

---

## 📝 Description

### Context from EPIC-001

This is the 10th story in EPIC-001 (Account Management & Double-Entry Foundation), completing Phase 3: Data Integrity & UX Polish. This story adds professional visual design to enhance user experience and account navigation.

**Completed Foundation (Sprints 1-9):**
- ✅ US-001: Account Type Taxonomy - Provides account types/subtypes for color mapping
- ✅ US-005: Opening Balance Equity - AccountDialog patterns to extend
- ✅ US-006: Account Hierarchy - Tree widget to enhance with visual indicators
- ✅ US-010: Balance Validation (Sprint 9) - Ensures data accuracy before UI polish

**Building Upon:**
- US-006 AccountTreeWidget patterns (drag-drop, display)
- US-005 AccountDialog patterns (form layout)
- Account repository patterns from all previous stories

### Problem Statement

Visual design significantly impacts usability. Color-coded accounts help users:
- Quickly identify account types (checking, savings, credit cards)
- See account status (active, needs reconciliation, archived)
- Recognize balances (positive/negative, approaching limits)
- Navigate large account lists efficiently

**Currently:**
- ❌ All accounts look the same
- ❌ No visual distinction between account types
- ❌ Hard to spot accounts needing attention
- ❌ No transaction count indicators
- ❌ Balances not visually emphasized

### Proposed Solution

Implement comprehensive visual design system:
- Color-coded icons by account type/subtype
- Status indicators (badges, icons)
- Transaction count display
- Balance color coding (green/red based on context)
- Customizable colors per account

---

## 🎯 Acceptance Criteria

### AC1: Default Color Scheme by Account Type

**Given** an account is created
**When** I select an account type/subtype
**Then** a default color should be automatically assigned:

- **Assets:**
  - Checking: Blue (#3B82F6)
  - Savings: Green (#10B981)
  - Cash: Purple (#8B5CF6)
  - Investment: Amber (#F59E0B)
- **Liabilities:**
  - Credit Card: Red (#EF4444)
  - Loan: Orange (#F97316)
  - Mortgage: Dark Red (#DC2626)
- **Equity:** Gray (#6B7280)
- **Income:** Green (#10B981)
- **Expenses:** Red (#DC2626)

### AC2: Account List Visual Design

**Given** I am viewing the account list
**When** accounts are displayed
**Then** each account should show:
- Color-coded icon (circle or account type icon)
- Account name (bold for emphasis)
- Account type label (e.g., "Checking Account")
- Current balance (color-coded: green if positive for assets, red if negative)
- Transaction count badge (e.g., "47 transactions")
- Status indicators (⚠️ needs reconciliation, 📁 archived)

### AC3: Balance Color Coding Logic

**Given** an account balance is displayed
**When** determining the color
**Then** the system should:

- **For Asset accounts (checking, savings, cash):**
  - Green if balance > $0
  - Red if balance < $0 (overdrawn)
  - Gray if balance = $0

- **For Liability accounts (credit cards, loans):**
  - Green if balance = $0 (paid off)
  - Orange if balance < credit limit (normal)
  - Red if balance >= credit limit (over limit)

- **For Investment accounts:**
  - Green if balance increased from opening
  - Red if balance decreased from opening
  - Gray if unchanged

### AC4: Transaction Count Display

**Given** an account has transactions
**When** displaying the account
**Then** show transaction count as:
- Badge with number (e.g., "47")
- Color-coded by activity level:
  - Green: 50+ transactions (active)
  - Blue: 10-49 transactions (moderate)
  - Gray: < 10 transactions (low activity)

### AC5: Custom Colors

**Given** I want to customize an account's color
**When** I edit the account
**Then** I should be able to:
- Click color picker
- Select from palette or enter hex code
- See live preview
- Reset to default color
- Save custom color

### AC6: Accessibility

**Given** users may have color vision deficiencies
**When** designing color schemes
**Then** ensure:
- Colors meet WCAG AA contrast requirements (4.5:1)
- Icons/text accompany all color indicators
- Patterns/shapes available for colorblind users
- High contrast mode supported

---

## 🔧 Technical Details

### Database Changes

```sql
-- Migration 010: Add color and display fields
ALTER TABLE accounts ADD COLUMN color_hex TEXT DEFAULT '#3B82F6';
ALTER TABLE accounts ADD COLUMN icon TEXT;
ALTER TABLE accounts ADD COLUMN display_order INTEGER DEFAULT 0;
ALTER TABLE accounts ADD COLUMN is_favorite BOOLEAN DEFAULT 0;

-- Note: These fields may overlap with US-007 if it's implemented first
```

### Implementation Approach

**Step 1: Define Color Scheme Constants (30 min)**
```python
# finance_app/ui/styles/account_colors.py
ACCOUNT_TYPE_COLORS = {
    'asset': {
        'checking': '#3B82F6',      # Blue
        'savings': '#10B981',        # Green
        'cash': '#8B5CF6',           # Purple
        'investment': '#F59E0B',     # Amber
    },
    'liability': {
        'credit_card': '#EF4444',    # Red
        'loan': '#F97316',           # Orange
        'mortgage': '#DC2626',       # Dark red
    },
    'equity': {
        'opening_balance': '#6B7280',  # Gray
    },
    'income': {
        'default': '#10B981',        # Green
    },
    'expense': {
        'default': '#DC2626',        # Red
    }
}

def get_default_color(account_type: str, account_subtype: str) -> str:
    """Get default color for account type/subtype."""
    return ACCOUNT_TYPE_COLORS.get(account_type, {}).get(
        account_subtype,
        '#3B82F6'  # Default blue
    )
```

**Step 2: Create Account Summary Repository Method (1 hour)**
```python
# In AccountRepository
def get_account_summary(self, account_id: int) -> Dict:
    """
    Get account summary with transaction count and stats.

    Returns:
        {
            'account': Account,
            'transaction_count': int,
            'last_transaction_date': str,
            'reconciled_count': int,
            'pending_count': int,
            'needs_reconciliation': bool
        }
    """
    query = """
        SELECT
            a.*,
            COUNT(je.id) as transaction_count,
            MAX(je.entry_date) as last_transaction_date,
            SUM(CASE WHEN je.is_reconciled = 1 THEN 1 ELSE 0 END) as reconciled_count,
            SUM(CASE WHEN je.is_reconciled = 0 THEN 1 ELSE 0 END) as pending_count
        FROM accounts a
        LEFT JOIN journal_entries je ON a.id = je.account_id
        WHERE a.id = ?
        GROUP BY a.id
    """
    # Execute and return summary dict
```

**Step 3: Create AccountListItem Widget (2 hours)**
```python
# finance_app/ui/widgets/account_list_item.py
class AccountListItem(QWidget):
    """Custom widget for displaying account in list with visual indicators."""

    def __init__(self, account: Account, summary: Dict, parent=None):
        super().__init__(parent)
        self.account = account
        self.summary = summary
        self.setup_ui()

    def setup_ui(self):
        """Create visual layout."""
        layout = QHBoxLayout(self)

        # Color indicator circle
        color_circle = self.create_color_circle(self.account.color_hex)
        layout.addWidget(color_circle)

        # Account info (name, type, balance)
        info_layout = QVBoxLayout()

        # Account name (bold)
        name_label = QLabel(f"<b>{self.account.name}</b>")
        info_layout.addWidget(name_label)

        # Account type label
        type_label = QLabel(self.get_account_type_label())
        type_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        info_layout.addWidget(type_label)

        layout.addLayout(info_layout)

        # Spacer
        layout.addStretch()

        # Transaction count badge
        count_badge = self.create_transaction_badge(
            self.summary['transaction_count']
        )
        layout.addWidget(count_badge)

        # Balance (color-coded)
        balance_label = self.create_balance_label(self.account.balance)
        layout.addWidget(balance_label)

        # Status indicators
        if self.summary['needs_reconciliation']:
            warning_icon = QLabel("⚠️")
            warning_icon.setToolTip("Needs reconciliation")
            layout.addWidget(warning_icon)

    def create_color_circle(self, color: str) -> QWidget:
        """Create colored circle indicator."""
        circle = QLabel()
        circle.setFixedSize(24, 24)
        circle.setStyleSheet(f"""
            background-color: {color};
            border-radius: 12px;
            border: 2px solid white;
        """)
        return circle

    def create_balance_label(self, balance: Decimal) -> QLabel:
        """Create balance label with color coding."""
        color = self.get_balance_color(balance)
        label = QLabel(f"${abs(balance):,.2f}")
        label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 16px;")
        return label

    def get_balance_color(self, balance: Decimal) -> str:
        """Determine balance color based on account type and value."""
        if self.account.account_type == 'asset':
            if balance > 0:
                return '#10B981'  # Green
            elif balance < 0:
                return '#EF4444'  # Red (overdrawn)
            else:
                return '#6B7280'  # Gray
        elif self.account.account_type == 'liability':
            if balance == 0:
                return '#10B981'  # Green (paid off)
            else:
                return '#F97316'  # Orange
        else:
            return '#1F2937'  # Dark gray (default)
```

**Step 4: Add Color Picker to AccountDialog (1 hour)**
```python
# In AccountDialog
def setup_color_picker(self):
    """Add color picker to account dialog."""
    color_layout = QHBoxLayout()

    color_label = QLabel("Color:")
    color_layout.addWidget(color_label)

    # Current color preview
    self.color_preview = QLabel()
    self.color_preview.setFixedSize(40, 40)
    self.update_color_preview(self.account.color_hex)
    color_layout.addWidget(self.color_preview)

    # Choose color button
    choose_btn = QPushButton("Choose Color...")
    choose_btn.clicked.connect(self.choose_color)
    color_layout.addWidget(choose_btn)

    # Reset to default button
    reset_btn = QPushButton("Reset to Default")
    reset_btn.clicked.connect(self.reset_color)
    color_layout.addWidget(reset_btn)

    self.layout.addRow(color_layout)

def choose_color(self):
    """Open color picker dialog."""
    color = QColorDialog.getColor(
        QColor(self.account.color_hex),
        self,
        "Choose Account Color"
    )

    if color.isValid():
        self.account.color_hex = color.name()
        self.update_color_preview(color.name())

def reset_color(self):
    """Reset to default color for account type."""
    default_color = get_default_color(
        self.account.account_type,
        self.account.account_subtype
    )
    self.account.color_hex = default_color
    self.update_color_preview(default_color)
```

---

## 📋 Task Breakdown for Development

This section provides a detailed, step-by-step implementation plan for developers.

### Phase 1: Database & Model (Day 1 - 2 hours)

#### Task 1.1: Create Database Migration (010)
**Estimate:** 45 minutes
**Files:** `finance_app/data/migrations/010_account_visual_fields.sql`

**Implementation:**
```sql
-- Migration 010: Account visual customization fields
-- Dependencies: Migration 007 (US-006 hierarchy fields)

-- Add visual customization fields
ALTER TABLE accounts ADD COLUMN color_hex TEXT DEFAULT '#3B82F6';
ALTER TABLE accounts ADD COLUMN icon TEXT;
ALTER TABLE accounts ADD COLUMN display_order INTEGER DEFAULT 0;
ALTER TABLE accounts ADD COLUMN is_favorite BOOLEAN DEFAULT 0;

-- Create indices for sorting and filtering
CREATE INDEX idx_accounts_favorite ON accounts(is_favorite);
CREATE INDEX idx_accounts_display_order ON accounts(display_order);
CREATE INDEX idx_accounts_color ON accounts(color_hex);

-- Set default display_order = id for existing accounts
UPDATE accounts SET display_order = id WHERE display_order = 0;
```

**Acceptance:**
- [ ] Migration file created and tested
- [ ] All 4 columns added successfully
- [ ] Indices created and verified
- [ ] Existing accounts have valid display_order
- [ ] Rollback tested

**Testing:**
```python
def test_migration_010():
    db = Database(":memory:")
    # Verify columns exist
    cursor = db.conn.cursor()
    result = cursor.execute("PRAGMA table_info(accounts)")
    columns = [row[1] for row in result.fetchall()]
    assert "color_hex" in columns
    assert "icon" in columns
    assert "display_order" in columns
    assert "is_favorite" in columns
```

---

#### Task 1.2: Update Account Model
**Estimate:** 45 minutes
**Files:** `finance_app/data/models.py`

**Implementation:**
1. Add 4 new fields to Account dataclass
2. Add validation (color_hex format, display_order non-negative)
3. Update docstrings
4. Add type hints

**New Fields:**
```python
@dataclass
class Account:
    # ... existing fields from US-001, US-006 ...

    # US-009: Visual customization (NEW)
    color_hex: str = '#3B82F6'  # Default blue
    icon: Optional[str] = None
    display_order: int = 0
    is_favorite: bool = False
```

**Acceptance:**
- [ ] Account model has 4 new fields with defaults
- [ ] Type hints complete
- [ ] Docstrings updated
- [ ] No breaking changes to existing code

**Testing:**
```python
def test_account_visual_fields():
    account = Account(
        id=1,
        name="Test",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        color_hex='#FF0000',
        is_favorite=True,
        display_order=5
    )
    assert account.color_hex == '#FF0000'
    assert account.is_favorite == True
```

---

#### Task 1.3: Update Database Integration
**Estimate:** 30 minutes
**Files:** `finance_app/data/database.py`

**Implementation:**
1. Add migration 010 to migration list
2. Update schema_version to 10
3. Run migration on app startup
4. Verify migration in logs

**Acceptance:**
- [ ] Migration 010 runs automatically
- [ ] Logs confirm successful migration
- [ ] Database version = 10

---

### Phase 2: Color Constants & Utilities (Day 1 - 1.5 hours)

#### Task 2.1: Create Color Scheme Module
**Estimate:** 1 hour
**Files:** `finance_app/ui/styles/account_colors.py` (NEW FILE)

**Implementation:**
Create new module with color constants and utility functions.

**Full Module:**
```python
"""
Account color scheme and visual styling utilities.

Defines default colors for account types and provides utility
functions for color manipulation and balance color logic.
"""

from decimal import Decimal
from typing import Optional

# Account type default colors (Tailwind CSS palette)
ACCOUNT_TYPE_COLORS = {
    'asset': {
        'checking': '#3B82F6',      # Blue
        'savings': '#10B981',        # Green
        'cash': '#8B5CF6',           # Purple
        'investment': '#F59E0B',     # Amber
    },
    'liability': {
        'credit_card': '#EF4444',    # Red
        'loan': '#F97316',           # Orange
        'mortgage': '#DC2626',       # Dark red
    },
    'equity': {
        'opening_balance': '#6B7280',  # Gray
    },
    'income': {
        'default': '#10B981',        # Green
    },
    'expense': {
        'default': '#DC2626',        # Red
    }
}

# Balance color coding
BALANCE_COLORS = {
    'positive': '#10B981',  # Green
    'negative': '#EF4444',  # Red
    'zero': '#6B7280',      # Gray
    'warning': '#F59E0B',   # Amber
}

def get_default_color(account_type: str, account_subtype: str) -> str:
    """
    Get default color for account type/subtype.

    Args:
        account_type: Account type (asset, liability, etc.)
        account_subtype: Account subtype (checking, savings, etc.)

    Returns:
        Hex color code

    Examples:
        >>> get_default_color('asset', 'checking')
        '#3B82F6'
        >>> get_default_color('liability', 'credit_card')
        '#EF4444'
    """
    return ACCOUNT_TYPE_COLORS.get(account_type, {}).get(
        account_subtype,
        '#3B82F6'  # Default blue if not found
    )

def get_balance_color(
    balance: Decimal,
    account_type: str,
    credit_limit: Optional[Decimal] = None
) -> str:
    """
    Get color for balance display based on account type and value.

    Args:
        balance: Current account balance
        account_type: Type of account
        credit_limit: Optional credit limit for liability accounts

    Returns:
        Hex color code

    Logic:
        Asset accounts (checking, savings, cash):
            - Green if balance > 0
            - Red if balance < 0 (overdrawn)
            - Gray if balance = 0

        Liability accounts (credit cards, loans):
            - Green if balance = 0 (paid off)
            - Orange if balance < credit limit (normal)
            - Red if balance >= credit limit (over limit)

        Other accounts:
            - Dark gray (neutral)
    """
    if account_type == 'asset':
        if balance > 0:
            return BALANCE_COLORS['positive']
        elif balance < 0:
            return BALANCE_COLORS['negative']
        else:
            return BALANCE_COLORS['zero']

    elif account_type == 'liability':
        if balance == 0:
            return BALANCE_COLORS['positive']  # Paid off
        elif credit_limit and balance >= credit_limit:
            return BALANCE_COLORS['negative']  # Over limit
        else:
            return BALANCE_COLORS['warning']   # Normal usage

    else:
        return '#1F2937'  # Dark gray for other types

def get_transaction_count_color(count: int) -> str:
    """
    Get color for transaction count badge.

    Args:
        count: Number of transactions

    Returns:
        Hex color code

    Color Coding:
        - Green: 50+ transactions (active account)
        - Blue: 10-49 transactions (moderate activity)
        - Gray: < 10 transactions (low activity)
    """
    if count >= 50:
        return '#10B981'  # Green (active)
    elif count >= 10:
        return '#3B82F6'  # Blue (moderate)
    else:
        return '#6B7280'  # Gray (low activity)
```

**Acceptance:**
- [ ] Module created with all constants
- [ ] get_default_color() implemented
- [ ] get_balance_color() implemented with all logic
- [ ] get_transaction_count_color() implemented
- [ ] Docstrings complete with examples
- [ ] Type hints correct

**Testing:**
```python
def test_get_default_color():
    assert get_default_color('asset', 'checking') == '#3B82F6'
    assert get_default_color('liability', 'credit_card') == '#EF4444'

def test_balance_color_asset_positive():
    color = get_balance_color(Decimal('1000'), 'asset')
    assert color == '#10B981'  # Green

def test_balance_color_asset_negative():
    color = get_balance_color(Decimal('-100'), 'asset')
    assert color == '#EF4444'  # Red (overdrawn)

def test_transaction_count_colors():
    assert get_transaction_count_color(100) == '#10B981'  # Green
    assert get_transaction_count_color(25) == '#3B82F6'   # Blue
    assert get_transaction_count_color(5) == '#6B7280'    # Gray
```

---

#### Task 2.2: Create __init__.py for styles module
**Estimate:** 15 minutes
**Files:** `finance_app/ui/styles/__init__.py` (NEW FILE)

**Implementation:**
```python
"""UI styles and theming."""

from .account_colors import (
    ACCOUNT_TYPE_COLORS,
    BALANCE_COLORS,
    get_default_color,
    get_balance_color,
    get_transaction_count_color
)

__all__ = [
    'ACCOUNT_TYPE_COLORS',
    'BALANCE_COLORS',
    'get_default_color',
    'get_balance_color',
    'get_transaction_count_color',
]
```

**Acceptance:**
- [ ] __init__.py created
- [ ] All functions exported
- [ ] Module importable

---

#### Task 2.3: Update AccountService.create_account() to Set Default Color
**Estimate:** 15 minutes
**Files:** `finance_app/business/account_service.py`

**Implementation:**
```python
from finance_app.ui.styles.account_colors import get_default_color

def create_account(
    self,
    name: str,
    account_type: AccountType,
    account_subtype: AccountSubtype,
    # ... existing params ...
    color_hex: Optional[str] = None  # NEW parameter
) -> Account:
    """Create new account with default color."""

    # ... existing validation ...

    # Set default color if not provided
    if not color_hex:
        color_hex = get_default_color(
            account_type.value,
            account_subtype.value
        )

    # ... rest of method ...
```

**Acceptance:**
- [ ] Default color assigned when creating account
- [ ] Custom color accepted if provided
- [ ] Color persisted to database

---

### Phase 3: Repository Layer (Day 1-2 - 2 hours)

#### Task 3.1: Add get_account_summary() Method
**Estimate:** 1.5 hours
**Files:** `finance_app/data/repositories/account_repository.py`

**Follow Pattern From:** US-006 repository methods, US-007 search methods

**New Method:**
```python
def get_account_summary(self, account_id: int) -> Dict[str, any]:
    """
    Get account summary with transaction statistics.

    Args:
        account_id: Account ID

    Returns:
        Dictionary with account and statistics:
        {
            'account': Account object,
            'transaction_count': int,
            'last_transaction_date': Optional[str],
            'reconciled_count': int,
            'pending_count': int,
            'needs_reconciliation': bool
        }
    """
    query = """
        SELECT
            a.id, a.name, a.account_type, a.account_subtype, a.balance,
            a.normal_balance, a.currency, a.parent_account_id,
            a.legacy_type, a.last_reconciled_date, a.opening_balance_date,
            a.is_parent, a.hierarchy_level, a.hierarchy_path,
            a.color_hex, a.icon, a.display_order, a.is_favorite,
            a.created_at, a.updated_at,
            COUNT(je.id) as transaction_count,
            MAX(je.entry_date) as last_transaction_date,
            SUM(CASE WHEN je.is_reconciled = 1 THEN 1 ELSE 0 END) as reconciled_count,
            SUM(CASE WHEN je.is_reconciled = 0 THEN 1 ELSE 0 END) as pending_count
        FROM accounts a
        LEFT JOIN journal_entries je ON a.id = je.account_id
        WHERE a.id = ?
        GROUP BY a.id
    """

    cursor = self.db.conn.cursor()
    cursor.execute(query, (account_id,))
    row = cursor.fetchone()

    if not row:
        raise ValueError(f"Account {account_id} not found")

    account = self._row_to_account(row)

    return {
        'account': account,
        'transaction_count': row['transaction_count'] or 0,
        'last_transaction_date': row['last_transaction_date'],
        'reconciled_count': row['reconciled_count'] or 0,
        'pending_count': row['pending_count'] or 0,
        'needs_reconciliation': (row['pending_count'] or 0) > 0
    }
```

**Acceptance:**
- [ ] Method implemented with explicit column selection
- [ ] Returns account with statistics
- [ ] Handles accounts with no transactions
- [ ] Single SQL query (efficient)
- [ ] Type hints correct

**Testing:**
```python
def test_get_account_summary_with_transactions():
    account = create_account(name="Test")
    create_transaction(account.id, amount=Decimal("100"))
    create_transaction(account.id, amount=Decimal("-50"))

    summary = account_repo.get_account_summary(account.id)
    assert summary['transaction_count'] == 2
    assert summary['account'].id == account.id

def test_get_account_summary_no_transactions():
    account = create_account(name="Empty")
    summary = account_repo.get_account_summary(account.id)
    assert summary['transaction_count'] == 0
    assert summary['needs_reconciliation'] == False
```

---

#### Task 3.2: Update _row_to_account() Helper
**Estimate:** 30 minutes
**Files:** `finance_app/data/repositories/account_repository.py`

**Implementation:**
Add mapping for 4 new visual fields in `_row_to_account()` method.

**Changes:**
```python
def _row_to_account(self, row: sqlite3.Row) -> Account:
    """Convert database row to Account object."""
    return Account(
        # ... existing fields ...

        # US-009: Visual customization fields (NEW)
        color_hex=row.get('color_hex', '#3B82F6'),
        icon=row.get('icon'),
        display_order=row.get('display_order', 0),
        is_favorite=bool(row.get('is_favorite', 0)),

        # ... timestamps ...
    )
```

**Acceptance:**
- [ ] All 4 visual fields mapped correctly
- [ ] Default values handled
- [ ] Boolean conversion for is_favorite
- [ ] No data loss during conversion

---

### Phase 4: UI Components (Day 2-3 - 4 hours)

#### Task 4.1: Create AccountListItem Widget
**Estimate:** 2 hours
**Files:** `finance_app/ui/widgets/account_list_item.py` (NEW FILE)

**Follow Pattern From:** US-006 AccountTreeWidget, PySide6 QWidget patterns

**Full Widget Implementation:**
```python
"""Custom widget for account list item with visual indicators."""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from decimal import Decimal
from typing import Dict, Optional

from finance_app.data.models import Account
from finance_app.ui.styles.account_colors import (
    get_balance_color,
    get_transaction_count_color
)

class AccountListItem(QWidget):
    """
    Custom widget displaying account with visual indicators.

    Visual Elements:
        - Color-coded circle (account color)
        - Account name (bold)
        - Account type label
        - Transaction count badge (color-coded)
        - Balance (color-coded)
        - Status icons (needs reconciliation, favorite)

    Signals:
        favorite_toggled: Emitted when favorite icon clicked
    """

    favorite_toggled = Signal(int, bool)  # account_id, is_favorite

    def __init__(
        self,
        account: Account,
        summary: Optional[Dict] = None,
        parent=None
    ):
        super().__init__(parent)
        self.account = account
        self.summary = summary or {}
        self.setup_ui()

    def setup_ui(self):
        """Create visual layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Color indicator circle
        color_circle = self.create_color_circle(self.account.color_hex)
        layout.addWidget(color_circle)

        # Account info (name + type)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        # Account name (bold)
        name_label = QLabel(f"<b>{self.account.name}</b>")
        name_label.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(name_label)

        # Account type label
        type_label = QLabel(self.get_account_type_label())
        type_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        info_layout.addWidget(type_label)

        layout.addLayout(info_layout)

        # Spacer
        layout.addStretch()

        # Transaction count badge
        if self.summary.get('transaction_count', 0) > 0:
            count_badge = self.create_transaction_badge(
                self.summary['transaction_count']
            )
            layout.addWidget(count_badge)

        # Balance (color-coded)
        balance_label = self.create_balance_label(self.account.balance)
        layout.addWidget(balance_label)

        # Favorite star (clickable)
        favorite_btn = self.create_favorite_button()
        layout.addWidget(favorite_btn)

        # Status indicators
        if self.summary.get('needs_reconciliation', False):
            warning_icon = QLabel("⚠️")
            warning_icon.setToolTip("Needs reconciliation")
            warning_icon.setStyleSheet("font-size: 16px;")
            layout.addWidget(warning_icon)

    def create_color_circle(self, color: str) -> QWidget:
        """Create colored circle indicator."""
        circle = QLabel()
        circle.setFixedSize(24, 24)
        circle.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 12px;
                border: 2px solid white;
            }}
        """)
        circle.setToolTip(f"Account color: {color}")
        return circle

    def create_balance_label(self, balance: Decimal) -> QLabel:
        """Create balance label with color coding."""
        balance_color = get_balance_color(
            balance,
            self.account.account_type
        )

        # Format balance
        formatted = f"${abs(balance):,.2f}"
        if balance < 0:
            formatted = f"-{formatted}"

        label = QLabel(formatted)
        label.setStyleSheet(f"""
            QLabel {{
                color: {balance_color};
                font-weight: bold;
                font-size: 16px;
            }}
        """)
        return label

    def create_transaction_badge(self, count: int) -> QLabel:
        """Create transaction count badge."""
        badge_color = get_transaction_count_color(count)

        label = QLabel(str(count))
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(40, 24)
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {badge_color};
                color: white;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                padding: 4px 8px;
            }}
        """)
        label.setToolTip(f"{count} transactions")
        return label

    def create_favorite_button(self) -> QPushButton:
        """Create favorite star button."""
        btn = QPushButton("⭐" if self.account.is_favorite else "☆")
        btn.setFixedSize(30, 30)
        btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #F3F4F6;
                border-radius: 15px;
            }
        """)
        btn.setToolTip(
            "Remove from favorites" if self.account.is_favorite
            else "Add to favorites"
        )
        btn.clicked.connect(self.on_favorite_clicked)
        return btn

    def on_favorite_clicked(self):
        """Handle favorite button click."""
        new_state = not self.account.is_favorite
        self.favorite_toggled.emit(self.account.id, new_state)

    def get_account_type_label(self) -> str:
        """Get human-readable account type label."""
        type_labels = {
            'asset': {
                'checking': 'Checking Account',
                'savings': 'Savings Account',
                'cash': 'Cash',
                'investment': 'Investment Account'
            },
            'liability': {
                'credit_card': 'Credit Card',
                'loan': 'Loan',
                'mortgage': 'Mortgage'
            },
            'equity': {
                'opening_balance': 'Opening Balance Equity'
            }
        }

        return type_labels.get(
            self.account.account_type, {}
        ).get(
            self.account.account_subtype,
            self.account.account_type.capitalize()
        )
```

**Acceptance:**
- [ ] Widget displays all visual elements
- [ ] Color circle shows account color
- [ ] Balance color-coded correctly
- [ ] Transaction count badge displayed
- [ ] Favorite star clickable
- [ ] Status icons shown when appropriate
- [ ] Tooltip information complete

**Testing:**
Manual UI testing with various account types and balances.

---

#### Task 4.2: Create __init__.py for widgets module
**Estimate:** 15 minutes
**Files:** `finance_app/ui/widgets/__init__.py`

**Implementation:**
```python
"""UI widgets and custom components."""

from .account_tree_widget import AccountTreeWidget  # US-006
from .account_list_item import AccountListItem      # US-009 (NEW)

__all__ = [
    'AccountTreeWidget',
    'AccountListItem',
]
```

**Acceptance:**
- [ ] __init__.py updated
- [ ] AccountListItem exported
- [ ] Module importable

---

#### Task 4.3: Add Color Picker to AccountDialog
**Estimate:** 1.5 hours
**Files:** `finance_app/ui/dialogs/account_dialog.py`

**Follow Pattern From:** US-005 AccountDialog form layout

**Implementation:**
Add color picker section to existing AccountDialog.

**New Methods:**
```python
from PySide6.QtWidgets import QColorDialog
from PySide6.QtGui import QColor
from finance_app.ui.styles.account_colors import get_default_color

class AccountDialog(QDialog):
    # ... existing code ...

    def setup_color_section(self):
        """Add color customization section to form."""
        # Color label + preview + buttons
        color_layout = QHBoxLayout()

        color_label = QLabel("Color:")
        color_layout.addWidget(color_label)

        # Current color preview
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(40, 40)
        self.color_preview.setStyleSheet(f"""
            QLabel {{
                background-color: {self.account.color_hex};
                border-radius: 20px;
                border: 2px solid #D1D5DB;
            }}
        """)
        color_layout.addWidget(self.color_preview)

        # Choose color button
        choose_btn = QPushButton("Choose Color...")
        choose_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(choose_btn)

        # Reset to default button
        reset_btn = QPushButton("Reset to Default")
        reset_btn.clicked.connect(self.reset_color)
        color_layout.addWidget(reset_btn)

        color_layout.addStretch()

        self.form_layout.addRow("Account Color:", color_layout)

        # Favorite checkbox
        self.favorite_checkbox = QCheckBox("Mark as favorite")
        self.favorite_checkbox.setChecked(self.account.is_favorite)
        self.form_layout.addRow("", self.favorite_checkbox)

    def choose_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(
            QColor(self.account.color_hex),
            self,
            "Choose Account Color"
        )

        if color.isValid():
            self.account.color_hex = color.name()
            self.update_color_preview(color.name())

    def update_color_preview(self, color: str):
        """Update color preview square."""
        self.color_preview.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 20px;
                border: 2px solid #D1D5DB;
            }}
        """)

    def reset_color(self):
        """Reset to default color for account type."""
        default_color = get_default_color(
            self.account_type_combo.currentData().value,
            self.account_subtype_combo.currentData().value
        )
        self.account.color_hex = default_color
        self.update_color_preview(default_color)

    def get_account_data(self) -> Account:
        """Get account data from form (override existing method)."""
        # ... existing code to get other fields ...

        # Add color and favorite
        account.color_hex = self.account.color_hex
        account.is_favorite = self.favorite_checkbox.isChecked()

        return account
```

**Acceptance:**
- [ ] Color picker section added to dialog
- [ ] Color preview updates when color changed
- [ ] Reset to default works correctly
- [ ] Favorite checkbox integrated
- [ ] Form data includes color and favorite

**Testing:**
Manual UI testing of color picker dialog.

---

#### Task 4.4: Update AccountTreeWidget to Use AccountListItem
**Estimate:** 30 minutes
**Files:** `finance_app/ui/widgets/account_tree_widget.py`

**Implementation:**
Replace simple text items with AccountListItem widgets in tree.

**Changes:**
```python
from finance_app.ui.widgets.account_list_item import AccountListItem

class AccountTreeWidget(QTreeWidget):
    # ... existing code ...

    def add_account_item(
        self,
        account: Account,
        parent_item: Optional[QTreeWidgetItem] = None
    ) -> QTreeWidgetItem:
        """Add account to tree with visual widget."""
        item = QTreeWidgetItem()

        if parent_item:
            parent_item.addChild(item)
        else:
            self.addTopLevelItem(item)

        # Get account summary for statistics
        summary = self.account_repo.get_account_summary(account.id)

        # Create and set custom widget
        widget = AccountListItem(account, summary)
        widget.favorite_toggled.connect(self.on_favorite_toggled)

        self.setItemWidget(item, 0, widget)
        item.setData(0, Qt.UserRole, account.id)

        return item

    def on_favorite_toggled(self, account_id: int, is_favorite: bool):
        """Handle favorite toggle from widget."""
        # Update account in database
        account = self.account_repo.get_by_id(account_id)
        account.is_favorite = is_favorite
        self.account_service.update_account(account)

        # Refresh display
        self.refresh()
```

**Acceptance:**
- [ ] AccountListItem widgets displayed in tree
- [ ] Visual indicators shown for all accounts
- [ ] Favorite toggle works
- [ ] Tree maintains hierarchy structure
- [ ] Drag-drop still functions

---

### Phase 5: Main Window Integration (Day 3 - 1 hour)

#### Task 5.1: Update MainWindow Account Display
**Estimate:** 1 hour
**Files:** `finance_app/ui/main_window.py`

**Implementation:**
Ensure MainWindow uses AccountTreeWidget with visual enhancements.

**Verification:**
- [ ] Account tree shows visual indicators
- [ ] Color coding visible for all accounts
- [ ] Transaction counts displayed
- [ ] Favorite toggle accessible
- [ ] Balance colors correct

---

### Phase 6: Testing (Day 3-4 - 2 hours)

#### Task 6.1: Write Unit Tests for Color Utilities
**Estimate:** 1 hour
**Files:** `finance_app/tests/unit/test_account_colors.py` (NEW FILE)

**Test Coverage:**
```python
import pytest
from decimal import Decimal
from finance_app.ui.styles.account_colors import (
    get_default_color,
    get_balance_color,
    get_transaction_count_color
)

class TestAccountColors:
    """Test color utility functions."""

    def test_get_default_color_asset_accounts(self):
        """Test default colors for asset account types."""
        assert get_default_color('asset', 'checking') == '#3B82F6'
        assert get_default_color('asset', 'savings') == '#10B981'
        assert get_default_color('asset', 'cash') == '#8B5CF6'
        assert get_default_color('asset', 'investment') == '#F59E0B'

    def test_get_default_color_liability_accounts(self):
        """Test default colors for liability account types."""
        assert get_default_color('liability', 'credit_card') == '#EF4444'
        assert get_default_color('liability', 'loan') == '#F97316'
        assert get_default_color('liability', 'mortgage') == '#DC2626'

    def test_get_default_color_unknown_type(self):
        """Test default color for unknown account type."""
        color = get_default_color('unknown', 'unknown')
        assert color == '#3B82F6'  # Default blue

    def test_balance_color_asset_positive(self):
        """Asset accounts with positive balance show green."""
        color = get_balance_color(Decimal('1000.00'), 'asset')
        assert color == '#10B981'  # Green

    def test_balance_color_asset_negative(self):
        """Asset accounts with negative balance show red (overdrawn)."""
        color = get_balance_color(Decimal('-50.00'), 'asset')
        assert color == '#EF4444'  # Red

    def test_balance_color_asset_zero(self):
        """Asset accounts with zero balance show gray."""
        color = get_balance_color(Decimal('0.00'), 'asset')
        assert color == '#6B7280'  # Gray

    def test_balance_color_liability_paid_off(self):
        """Liability accounts paid off (balance=0) show green."""
        color = get_balance_color(Decimal('0.00'), 'liability')
        assert color == '#10B981'  # Green

    def test_balance_color_liability_normal(self):
        """Liability accounts with normal balance show orange."""
        color = get_balance_color(Decimal('500.00'), 'liability')
        assert color == '#F59E0B'  # Orange/Amber

    def test_transaction_count_color_high_activity(self):
        """High transaction count (50+) shows green."""
        assert get_transaction_count_color(100) == '#10B981'
        assert get_transaction_count_color(50) == '#10B981'

    def test_transaction_count_color_moderate_activity(self):
        """Moderate transaction count (10-49) shows blue."""
        assert get_transaction_count_color(49) == '#3B82F6'
        assert get_transaction_count_color(10) == '#3B82F6'

    def test_transaction_count_color_low_activity(self):
        """Low transaction count (<10) shows gray."""
        assert get_transaction_count_color(9) == '#6B7280'
        assert get_transaction_count_color(0) == '#6B7280'
```

**Acceptance:**
- [ ] All color utility functions tested
- [ ] Edge cases covered (zero, negative, boundaries)
- [ ] Test coverage > 95% for account_colors.py

---

#### Task 6.2: Write Integration Tests
**Estimate:** 1 hour
**Files:** `finance_app/tests/integration/test_account_visual_integration.py` (NEW FILE)

**Test Scenarios:**
```python
def test_create_account_assigns_default_color(account_service):
    """Test account creation assigns correct default color."""
    account = account_service.create_account(
        name="Checking",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING
    )
    assert account.color_hex == '#3B82F6'  # Blue

def test_custom_color_persisted(account_service):
    """Test custom color is saved and loaded."""
    account = account_service.create_account(
        name="Savings",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.SAVINGS,
        color_hex='#FF00FF'  # Custom magenta
    )

    # Reload from database
    reloaded = account_service.get_account(account.id)
    assert reloaded.color_hex == '#FF00FF'

def test_favorite_toggle(account_service):
    """Test favorite status can be toggled."""
    account = account_service.create_account(name="Test")
    assert account.is_favorite == False

    account.is_favorite = True
    updated = account_service.update_account(account)
    assert updated.is_favorite == True

def test_get_account_summary_includes_stats(account_repo):
    """Test account summary includes transaction statistics."""
    account = create_account(name="Test")
    create_transaction(account.id, amount=Decimal("100"))
    create_transaction(account.id, amount=Decimal("-50"))

    summary = account_repo.get_account_summary(account.id)
    assert summary['transaction_count'] == 2
    assert summary['account'].color_hex is not None
```

**Acceptance:**
- [ ] Integration tests cover end-to-end workflows
- [ ] Database persistence verified
- [ ] Color assignment tested
- [ ] Favorite toggle tested

---

### Phase 7: Documentation (Day 4 - 1 hour)

#### Task 7.1: Update USER_GUIDE.md
**Estimate:** 30 minutes
**Files:** `docs/USER_GUIDE.md`

**New Section:**
```markdown
## Visual Account Customization

### Account Colors

Each account has a color-coded indicator for quick visual identification:

**Default Colors by Account Type:**
- **Checking:** Blue
- **Savings:** Green
- **Cash:** Purple
- **Credit Card:** Red
- **Loans:** Orange
- **Investments:** Amber

**Customizing Colors:**
1. Right-click account → Edit
2. Click "Choose Color..." button
3. Select color from palette or enter hex code
4. Click "Reset to Default" to restore default color

### Favorite Accounts

Mark frequently-used accounts as favorites:
- Click the ⭐ star icon next to account
- Favorites appear at top of account list
- Favorites persist across sessions

### Visual Indicators

Accounts display helpful visual information:
- **Balance Color:**
  - Green: Positive balance (asset accounts)
  - Red: Overdrawn (negative balance for assets)
  - Orange: Normal usage (liability accounts)

- **Transaction Count Badge:**
  - Shows number of transactions
  - Color indicates activity level (green = active, blue = moderate, gray = low)

- **Status Icons:**
  - ⚠️ Needs reconciliation
```

**Acceptance:**
- [ ] USER_GUIDE.md updated with visual customization section
- [ ] Screenshots added (optional)
- [ ] Clear instructions for customization

---

#### Task 7.2: Update ARCHITECTURE.md
**Estimate:** 30 minutes
**Files:** `docs/ARCHITECTURE.md`

**Updates:**
```markdown
### Visual Customization Fields (Migration 010)

Added in US-009 (Sprint 10):

**Database Fields:**
- `color_hex`: Hex color code for account (#RRGGBB format)
- `icon`: Optional icon identifier
- `display_order`: Integer for custom sorting
- `is_favorite`: Boolean favorite flag

**Color Scheme:**
- Defined in `finance_app/ui/styles/account_colors.py`
- Default colors assigned by account type/subtype
- Balance color logic based on account type and value
- Transaction count color coded by activity level

**UI Components:**
- `AccountListItem`: Custom widget with visual indicators
- `AccountTreeWidget`: Enhanced with visual widgets
- `AccountDialog`: Color picker integration
```

**Acceptance:**
- [ ] ARCHITECTURE.md updated with visual fields
- [ ] Migration 010 documented
- [ ] Color scheme module documented

---

## 📊 Task Summary

**Total Tasks:** 18 tasks across 7 phases
**Estimated Time:** 13-14 hours (5 story points)

| Phase | Tasks | Time | Description |
|-------|-------|------|-------------|
| Phase 1: Database & Model | 3 tasks | 2 hours | Migration 010, Account model updates |
| Phase 2: Color Constants & Utilities | 3 tasks | 1.5 hours | account_colors.py module, utility functions |
| Phase 3: Repository Layer | 2 tasks | 2 hours | get_account_summary(), _row_to_account() updates |
| Phase 4: UI Components | 4 tasks | 4 hours | AccountListItem widget, color picker, tree integration |
| Phase 5: Main Window Integration | 1 task | 1 hour | Display verification |
| Phase 6: Testing | 2 tasks | 2 hours | Unit tests (15+), integration tests (4+) |
| Phase 7: Documentation | 2 tasks | 1 hour | USER_GUIDE.md, ARCHITECTURE.md |

**Complexity:** Moderate (UI-heavy, follows established patterns from US-005 and US-006)

**Risk Areas:**
- UI performance with many accounts (mitigated by efficient widget rendering)
- Color accessibility (mitigated by WCAG AA compliance testing)
- Migration 010 critical for US-007 (ensure thorough testing before commit)

---

## 👥 Sprint 10 Task Assignments by Developer

**Team Structure:** Backend Developer, Frontend Developer, Tech Lead
**Sprint Duration:** 4 days (13.5 hours total)
**Coordination:** Daily standups + 3 handoff meetings

### Task Distribution Summary

| Developer | Tasks | Hours | Days | Critical Deliverables |
|-----------|-------|-------|------|------------------------|
| **Backend Developer** | 8 tasks | 5.5 hrs | Day 1-2 | Migration 010 (BLOCKS US-007), color module, repository |
| **Frontend Developer** | 5 tasks | 5 hrs | Day 2-3 | AccountListItem widget, color picker, tree integration |
| **Tech Lead** | 5 tasks | 3 hrs | Day 3-4 | Testing (15+ tests), accessibility, US-007 handoff |
| **TOTAL** | **18 tasks** | **13.5 hrs** | **4 days** | All 6 ACs complete, tests passing, docs updated |

---

### 👨‍💻 Backend Developer: 8 Tasks (5.5 hours, Day 1-2)

**Critical:** Migration 010 MUST be completed by end of Day 2 (blocks US-007 Sprint 11)

#### Day 1 Morning (2 hours) - Phase 1: Database & Model

**Task 1.1: Create Migration 010** ⚠️ CRITICAL
- **Time:** 45 minutes
- **Priority:** P0 (BLOCKS US-007)
- **Files:** `finance_app/data/migrations/010_account_visual_fields.sql`
- **Deliverables:**
  - 4 columns: color_hex, icon, display_order, is_favorite
  - 3 indices: favorite, display_order, color
  - UPDATE existing accounts: display_order = id
  - Rollback tested
- **Testing:** Verify columns exist, indices created
- **Handoff:** Notify team when committed to main

**Task 1.2: Update Account Model**
- **Time:** 45 minutes
- **Priority:** P0
- **Files:** `finance_app/data/models.py`
- **Deliverables:**
  - Add 4 visual fields to Account dataclass
  - Type hints + docstrings
  - Default values: color_hex='#3B82F6', display_order=0, is_favorite=False
- **Testing:** Test account creation with visual fields

**Task 1.3: Database Integration**
- **Time:** 30 minutes
- **Priority:** P0
- **Files:** `finance_app/data/database.py`
- **Deliverables:**
  - Add migration 010 to MIGRATIONS list
  - Update SCHEMA_VERSION = 10
  - Verify migration runs on startup

#### Day 1 Afternoon (1.5 hours) - Phase 2: Color Module

**Task 2.1: Create account_colors.py Module** ⭐ CORE MODULE
- **Time:** 1 hour
- **Priority:** P0
- **Files:** `finance_app/ui/styles/account_colors.py` (NEW - 140 lines)
- **Deliverables:**
  - ACCOUNT_TYPE_COLORS dict (8 account types)
  - BALANCE_COLORS dict
  - get_default_color() function
  - get_balance_color() function (asset/liability/investment logic)
  - get_transaction_count_color() function
- **Important:** Use '#059669' (dark green) for savings (WCAG AA compliance)
- **Testing:** 15+ unit tests (see Phase 6)

**Task 2.2: Create styles/__init__.py**
- **Time:** 15 minutes
- **Priority:** P0
- **Files:** `finance_app/ui/styles/__init__.py` (NEW)
- **Deliverables:** Export all color functions

**Task 2.3: Update AccountService**
- **Time:** 15 minutes
- **Priority:** P1
- **Files:** `finance_app/business/account_service.py`
- **Deliverables:**
  - Add color_hex parameter to create_account()
  - Call get_default_color() if not provided
  - Persist color to database

#### Day 2 Morning (2 hours) - Phase 3: Repository Layer

**Task 3.1: Add get_account_summary() Method** ⭐ KEY METHOD
- **Time:** 1.5 hours
- **Priority:** P0
- **Files:** `finance_app/data/repositories/account_repository.py`
- **Deliverables:**
  - Single SQL query with LEFT JOIN on journal_entries
  - Explicit column selection (NOT SELECT *)
  - Aggregates: transaction_count, reconciled_count, pending_count
  - Returns dict with account + statistics
- **Performance:** <10ms per account (test with 100 accounts)
- **Testing:** Test with/without transactions

**Task 3.2: Update _row_to_account() Helper**
- **Time:** 30 minutes
- **Priority:** P0
- **Files:** `finance_app/data/repositories/account_repository.py`
- **Deliverables:**
  - Map 4 visual fields in row conversion
  - Handle NULL values with defaults
  - Boolean conversion for is_favorite

#### Backend Handoff (End of Day 2)
- [ ] Migration 010 committed to main branch
- [ ] account_colors.py complete and importable
- [ ] get_account_summary() working
- [ ] Unit tests written for backend components
- [ ] Sample data available for Frontend testing

---

### 🎨 Frontend Developer: 5 Tasks (5 hours, Day 2-3)

**Prerequisites:** Backend Migration 010 + color module complete

#### Day 2 Afternoon (2.5 hours) - Phase 4: UI Components (Part 1)

**Task 4.1: Create AccountListItem Widget** ⭐ MAIN UI COMPONENT
- **Time:** 2 hours
- **Priority:** P0
- **Files:** `finance_app/ui/widgets/account_list_item.py` (NEW - 200+ lines)
- **Deliverables:**
  - QWidget with QHBoxLayout
  - Color circle (24x24 px) using account.color_hex
  - Account name (bold, 14px) + type label (gray, 11px)
  - Balance label (color-coded with get_balance_color())
  - Transaction count badge (color-coded by activity)
  - Favorite star button (clickable, emits signal)
  - Status icons (⚠️ needs reconciliation)
  - Tooltips for accessibility
- **Signals:** favorite_toggled = Signal(int, bool)
- **Testing:** Manual UI testing with various account types

**Task 4.2: Update widgets/__init__.py**
- **Time:** 15 minutes
- **Priority:** P0
- **Files:** `finance_app/ui/widgets/__init__.py`
- **Deliverables:** Export AccountListItem

**Task 4.3: Add Color Picker to AccountDialog** ⭐ USER FEATURE
- **Time:** 1.5 hours (starts Day 2, finishes Day 3)
- **Priority:** P0
- **Files:** `finance_app/ui/dialogs/account_dialog.py`
- **Deliverables:**
  - setup_color_section() method
  - Color preview (40x40 QLabel with border-radius)
  - "Choose Color..." button → QColorDialog
  - "Reset to Default" button (uses get_default_color())
  - "Mark as favorite" checkbox
  - Update get_account_data() to include color_hex + is_favorite
- **Testing:** Open dialog, select color, verify persistence

#### Day 3 Morning (1.5 hours) - Phase 4 & 5: Integration

**Task 4.4: Update AccountTreeWidget Integration**
- **Time:** 30 minutes
- **Priority:** P1
- **Files:** `finance_app/ui/widgets/account_tree_widget.py`
- **Deliverables:**
  - Replace simple items with AccountListItem widgets
  - Call get_account_summary() for each account
  - Connect favorite_toggled signal
  - Handle favorite toggle (update database, refresh)
  - Preserve drag-drop functionality
- **Testing:** Verify tree displays visual indicators

**Task 5.1: Verify MainWindow Display** (Phase 5)
- **Time:** 1 hour
- **Priority:** P1
- **Files:** `finance_app/ui/main_window.py`
- **Deliverables:**
  - Verify AccountTreeWidget shows visual indicators
  - Test with various account types (assets, liabilities)
  - Verify color coding visible
  - Test favorite toggle from main window
  - Performance check with 50+ accounts
- **Manual Testing:**
  - Create 50+ accounts
  - Verify load time <500ms
  - Test positive/negative balances (color-coded)
  - Click favorite stars (verify persistence)
  - Test color picker in create/edit dialogs

#### Frontend Handoff (End of Day 3)
- [ ] AccountListItem widget complete
- [ ] Color picker working in AccountDialog
- [ ] AccountTreeWidget displays visual indicators
- [ ] Manual testing completed (50+ accounts)
- [ ] Screenshots captured for documentation
- [ ] No UI glitches or layout issues

---

### 🔍 Tech Lead: 5 Tasks (3 hours, Day 3-4)

**Prerequisites:** Backend + Frontend implementation complete

#### Day 3 Afternoon (2 hours) - Phase 6: Testing

**Task 6.1: Unit Tests for Color Utilities** ⭐ CORE TESTING
- **Time:** 1 hour
- **Priority:** P0
- **Files:** `finance_app/tests/unit/test_account_colors.py` (NEW)
- **Deliverables:**
  - 15+ unit tests for account_colors.py
  - Test all color utility functions
  - Edge cases: zero, negative, unknown types
  - Test coverage >95% for account_colors.py
- **Test Suite:**
  ```
  test_get_default_color_asset_accounts()
  test_get_default_color_liability_accounts()
  test_get_default_color_unknown_type()
  test_balance_color_asset_positive()
  test_balance_color_asset_negative()
  test_balance_color_asset_zero()
  test_balance_color_liability_paid_off()
  test_balance_color_liability_normal()
  test_transaction_count_color_high_activity()
  test_transaction_count_color_moderate_activity()
  test_transaction_count_color_low_activity()
  ... (4 more tests)
  ```
- **Run:** `pytest finance_app/tests/unit/test_account_colors.py -v --cov`

**Task 6.2: Integration + Accessibility Tests** ⚠️ CRITICAL (AC6)
- **Time:** 1 hour
- **Priority:** P0 (AC6 requirement)
- **Files:** `finance_app/tests/integration/test_account_visual_integration.py` (NEW)
- **Deliverables:**
  - 4+ integration tests (create account, custom color, favorite toggle, account summary)
  - **NEW: Accessibility tests (WCAG AA contrast 4.5:1)**
  - Colorblind simulation test
  - Icons visible without color test
- **Test Suite:**
  ```python
  # Integration Tests
  test_create_account_assigns_default_color()
  test_custom_color_persisted()
  test_favorite_toggle()
  test_get_account_summary_includes_stats()

  # Accessibility Tests (NEW)
  test_color_contrast_wcag_aa()  # Test all colors meet 4.5:1 ratio
  test_colorblind_simulation()   # Protanopia/deuteranopia
  test_icons_visible_without_color()  # Text + icons present
  ```
- **Critical:** Verify dark green (#059669) for savings passes WCAG AA
- **Run:** `pytest finance_app/tests/integration/test_account_visual_integration.py -v`

#### Day 3 Late Afternoon (1 hour) - Phase 7: Documentation

**Task 7.1: Update USER_GUIDE.md**
- **Time:** 30 minutes
- **Priority:** P1
- **Files:** `docs/USER_GUIDE.md`
- **Deliverables:**
  - New section "Visual Account Customization" (~560 lines)
  - Subsections: Account Colors, Favorite Accounts, Visual Indicators
  - Step-by-step instructions for color customization
  - Screenshots (optional but recommended)
  - What/Why/How structure
- **Insert:** After "Organizing Accounts with Hierarchy" section

**Task 7.2: Update ARCHITECTURE.md**
- **Time:** 30 minutes
- **Priority:** P1
- **Files:** `docs/ARCHITECTURE.md`
- **Deliverables:**
  - New section "Visual Customization Fields (Migration 010)" (~370 lines)
  - Document 4 database fields + indices
  - Document account_colors.py module
  - Document UI components (AccountListItem, color picker)
  - Performance metrics
- **Insert:** In "Database Schema" section after US-006

#### Day 4 Morning (30 minutes) - Critical Handoff

**Task 6.3: Code Review**
- **Time:** 20 minutes
- **Priority:** P0
- **Checklist:**
  - [ ] Backend PR reviewed (migration, models, repository, service)
  - [ ] Frontend PR reviewed (widgets, dialogs, integration)
  - [ ] All tests passing (unit + integration + accessibility)
  - [ ] Code follows US-005/US-006 patterns
  - [ ] No regressions in existing features
  - [ ] Performance acceptable (<100ms rendering)

**Task 6.4: US-007 Handoff Verification** ⚠️ CRITICAL (BLOCKS SPRINT 11)
- **Time:** 10 minutes
- **Priority:** P0 (BLOCKS US-007)
- **US-007 Handoff Checklist:**
  - [ ] **Migration 010 committed** to main branch
  - [ ] **Fields verified present**: color_hex, icon, display_order, is_favorite
  - [ ] **Test Migration 011** (create dummy US-007 migration: account_number, institution_name, notes)
  - [ ] **Migration 011 test passes** with Migration 010 in place
  - [ ] **Documentation updated** showing field ownership:
    - Migration 010 (US-009): color_hex, icon, display_order, is_favorite
    - Migration 011 (US-007): account_number, institution_name, notes (ONLY)
  - [ ] **US-007 developer notified** fields available
- **Verification Script:**
  ```bash
  sqlite3 data/finance.db "PRAGMA table_info(accounts);" | grep -E "(color_hex|icon|display_order|is_favorite)"
  # Should show all 4 fields
  ```

#### Tech Lead Sprint Completion
- [ ] All 15+ unit tests passing
- [ ] All 4+ integration tests passing
- [ ] **Accessibility tests passing (WCAG AA)**
- [ ] USER_GUIDE.md + ARCHITECTURE.md updated
- [ ] Code review complete (backend + frontend)
- [ ] **US-007 handoff verified (Migration 010 → 011)**
- [ ] Sprint 10 demo prepared
- [ ] No regressions

---

## 📅 4-Day Sprint Timeline

### Day 1: Backend Foundation
**Morning (4 hours):**
- Backend: Task 1.1-1.3 (Database & Model) - 2 hours
- Backend: Task 2.1-2.3 (Color Module) - 1.5 hours
- Daily Standup: 15 minutes

**Afternoon (4 hours):**
- Backend: Task 3.1-3.2 (Repository Layer) - 2 hours
- Backend: Write backend unit tests - 1 hour
- Tech Lead: Review Migration 010 - 30 minutes

**End of Day 1 Deliverables:**
- [ ] Migration 010 complete (not yet committed)
- [ ] account_colors.py module complete
- [ ] Repository methods complete

---

### Day 2: Backend Finish + Frontend Start
**Morning (4 hours):**
- Backend: Finish Task 3.1-3.2 (if needed) - 1 hour
- Backend: Backend integration testing - 1 hour
- Frontend: Task 4.1 (AccountListItem widget) - 2 hours
- Daily Standup: 15 minutes

**Afternoon (4 hours):**
- Frontend: Task 4.2 (widgets/__init__.py) - 15 minutes
- Frontend: Task 4.3 (Color Picker) - Start (1.5 hours)
- Backend/Frontend: **Handoff Meeting** - 30 minutes
  - Backend demos: Migration, color module, get_account_summary()
  - Frontend asks API questions
  - Tech Lead verifies migration safety

**End of Day 2 Deliverables:**
- [ ] **Migration 010 committed to main** ⚠️ CRITICAL
- [ ] Backend PR submitted
- [ ] AccountListItem widget 80% complete
- [ ] Color picker integration started

---

### Day 3: Frontend Finish + Testing Start
**Morning (4 hours):**
- Frontend: Task 4.3 (Color Picker) - Finish (30 minutes)
- Frontend: Task 4.4 (AccountTreeWidget integration) - 30 minutes
- Frontend: Task 5.1 (MainWindow verification) - 1 hour
- Tech Lead: Task 6.1 (Unit tests) - 1 hour
- Daily Standup: 15 minutes
- All: Bug fixes from integration - 1 hour

**Afternoon (4 hours):**
- Tech Lead: Task 6.2 (Integration + Accessibility tests) - 1 hour
- Tech Lead: Task 7.1-7.2 (Documentation) - 1 hour
- Frontend/Tech Lead: **Handoff Meeting** - 30 minutes
  - Frontend demos: UI components, color picker, tree
  - Tech Lead reviews visual design
  - Identify manual testing scenarios
- All: Final integration testing - 1.5 hours

**End of Day 3 Deliverables:**
- [ ] Frontend PR submitted
- [ ] All UI components complete
- [ ] 15+ unit tests passing
- [ ] 4+ integration tests passing
- [ ] **Accessibility tests passing**

---

### Day 4: Polish + US-007 Handoff
**Morning (2 hours):**
- Tech Lead: Task 6.3 (Code review) - 20 minutes
- Tech Lead: Task 6.4 (US-007 handoff verification) - 10 minutes
- All: **Handoff Meeting** - 30 minutes
  - Tech Lead presents: Test results, documentation, US-007 status
  - Team reviews DoD checklist
  - Prepare sprint demo
- All: Final bug fixes - 1 hour

**Afternoon (1 hour):**
- Sprint 10 demo/review - 30 minutes
- Retrospective - 30 minutes
- **US-007 handoff to Sprint 11 team**

**End of Day 4 Deliverables:**
- [ ] All 18 tasks complete
- [ ] All 6 ACs met
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Code merged to main
- [ ] **Migration 010 committed (US-007 ready)**
- [ ] Sprint demo delivered
- [ ] **Grade: A expected**

---

## 🤝 Coordination & Handoffs

### Daily Standups (15 min, 9:00 AM)
**Day 1-4:** Each developer shares:
- Yesterday's progress
- Today's plan
- Blockers

### Handoff Meeting 1: Backend → Frontend (Day 2 Afternoon, 30 min)
**Agenda:**
- Backend demonstrates: Migration 010, account_colors.py, get_account_summary()
- Frontend asks questions about APIs
- Tech Lead reviews migration safety
- **Critical:** Confirm Migration 010 committed before Frontend proceeds

### Handoff Meeting 2: Frontend → Tech Lead (Day 3 Afternoon, 30 min)
**Agenda:**
- Frontend demonstrates: AccountListItem, color picker, tree integration
- Tech Lead reviews visual design
- Identify manual testing scenarios
- **Critical:** Capture screenshots for documentation

### Handoff Meeting 3: Tech Lead → Team (Day 4 Morning, 30 min)
**Agenda:**
- Tech Lead presents: Test results, documentation, US-007 handoff status
- Team reviews Definition of Done checklist
- Prepare sprint demo
- **Critical:** Verify US-007 handoff complete

---

## 🚨 Critical Success Factors

### P0: Must Have (Sprint Cannot Complete Without)
1. ✅ **Migration 010 committed by end of Day 2** - BLOCKS US-007 Sprint 11
2. ✅ **All 6 Acceptance Criteria met** - Story closure requirement
3. ✅ **All tests passing** - Quality gate (15+ unit, 4+ integration, accessibility)
4. ✅ **US-007 handoff verified** - Migration 010 → 011 sequence tested

### P1: Should Have (Important for Quality)
1. ✅ **Accessibility testing** - AC6 requirement (WCAG AA 4.5:1 contrast)
2. ✅ **Documentation complete** - USER_GUIDE.md + ARCHITECTURE.md
3. ✅ **Code review** - Pattern consistency with US-005/US-006
4. ✅ **Performance verified** - <100ms rendering for 100 accounts

### P2: Nice to Have (Optional Enhancements)
1. 💡 E2E GUI tests (Xvfb) - Recommended but not required
2. 💡 Performance benchmarks - Helps with scalability confidence
3. 💡 Color hex validation - Additional safety (QColorDialog already safe)

---

## ✅ Definition of Done

### Database & Model (Phase 1)
- [ ] Migration 010 created and tested
- [ ] 4 visual fields added to accounts table (color_hex, icon, display_order, is_favorite)
- [ ] Indices created for sorting/filtering
- [ ] Account model updated with 4 new fields
- [ ] Database version updated to 10

### Color Constants & Utilities (Phase 2)
- [ ] account_colors.py module created with all constants
- [ ] get_default_color() function implemented
- [ ] get_balance_color() function implemented (all account type logic)
- [ ] get_transaction_count_color() function implemented
- [ ] AccountService.create_account() sets default color

### Repository Layer (Phase 3)
- [ ] get_account_summary() method implemented
- [ ] Returns account with transaction statistics
- [ ] _row_to_account() updated for visual fields
- [ ] Explicit column selection (not SELECT *)
- [ ] NULL handling correct

### UI Components (Phase 4)
- [ ] AccountListItem widget created with all visual indicators
- [ ] Color circle, balance color, transaction badge implemented
- [ ] Favorite star toggle functional
- [ ] AccountDialog enhanced with color picker
- [ ] Color preview and reset to default functional
- [ ] AccountTreeWidget uses AccountListItem widgets

### Integration (Phase 5)
- [ ] MainWindow displays visual indicators
- [ ] Account tree shows colors, badges, favorites
- [ ] UI responsive and performant

### Testing (Phase 6)
- [ ] Unit tests for color utilities (15+ tests, >95% coverage)
- [ ] Integration tests for visual features (4+ tests)
- [ ] Default color assignment tested
- [ ] Custom color persistence tested
- [ ] Favorite toggle tested
- [ ] Manual UI testing completed

### Documentation (Phase 7)
- [ ] USER_GUIDE.md updated with visual customization section
- [ ] ARCHITECTURE.md updated with Migration 010 details
- [ ] Code comments comprehensive
- [ ] Screenshots added (optional)

### Quality Assurance
- [ ] All tests passing
- [ ] No regressions in existing features
- [ ] Code reviewed and approved
- [ ] Accessibility requirements met (WCAG AA contrast)
- [ ] Color scheme tested with colorblind simulation
- [ ] Performance acceptable (UI rendering < 100ms)

### US-007 Handoff (Critical!)
- [ ] **Migration 010 committed and documented**
- [ ] **Fields available for US-007 Migration 011**
- [ ] **display_order and is_favorite** fully functional
- [ ] **US-007 can proceed in Sprint 11**

---

## 🧪 Test Scenarios

### Test 1: Default Colors Assigned
```python
def test_default_color_assignment():
    account = account_service.create_account(
        name="Checking",
        account_type="asset",
        account_subtype="checking"
    )
    assert account.color_hex == '#3B82F6'  # Blue
```

### Test 2: Balance Color Logic - Asset Account
```python
def test_balance_color_asset_positive():
    account = create_test_account(type='asset', balance=Decimal('1000.00'))
    widget = AccountListItem(account, {})
    color = widget.get_balance_color(account.balance)
    assert color == '#10B981'  # Green for positive asset
```

### Test 3: Custom Color Persistence
```python
def test_custom_color_saved():
    account = account_service.create_account(name="Savings")
    account.color_hex = '#FF00FF'  # Custom magenta
    updated = account_service.update_account(account)
    assert updated.color_hex == '#FF00FF'
```

---

## 📊 Success Metrics

- Users can identify account types 50% faster
- Account list navigation improved (user testing)
- Color scheme passes accessibility audits
- Zero complaints about color contrast
- Transaction count visible and useful

---

## 🔗 Dependencies & Integration

### Depends On (Completed)
- ✅ **US-001:** Account Type Taxonomy
  - Provides account_type and account_subtype for color mapping
  - AccountType and AccountSubtype enums

- ✅ **US-005:** Opening Balance Equity
  - AccountDialog patterns to extend
  - QFormLayout structure to follow

- ✅ **US-006:** Account Hierarchy
  - AccountTreeWidget to enhance with visual widgets
  - Tree structure and drag-drop patterns
  - parent_account_id field integration

### Blocks (Critical!)
- 📋 **US-007:** Account Metadata & Organization (Sprint 11)
  - **US-007 Migration 011 depends on US-009 Migration 010**
  - Migration 010 adds: `display_order`, `is_favorite`, `color_hex`, `icon`
  - Migration 011 (US-007) ONLY adds: `account_number`, `institution_name`, `notes`
  - **If US-009 is skipped, US-007 Migration 011 will fail!**

### Integration Points

**With US-006 (Account Hierarchy):**
- AccountTreeWidget enhanced with AccountListItem widgets
- Visual indicators displayed in tree hierarchy
- Drag-drop functionality preserved
- Hierarchy + favorites + display_order work together

**With US-007 (Account Metadata):**
- Shared fields: `display_order`, `is_favorite`, `color_hex`
- Migration sequence: Migration 010 (US-009) → Migration 011 (US-007)
- US-007 AC7 specifies how display_order works per-hierarchy-level
- US-007 AC4 uses `is_favorite` for account organization

**With US-004 (Reconciliation):**
- Status indicators show reconciliation warnings
- Transaction count includes reconciled vs pending counts

---

## 🔮 Future Enhancements

**Potential Future Stories:**
- **US-009B:** Account icons (icon field currently added but not implemented)
- **US-009C:** Custom color themes (dark mode, colorblind-friendly palettes)
- **US-009D:** Advanced visual indicators (spending trends, budget warnings)
- **US-009E:** Bulk color operations (apply color to category of accounts)

**EPIC-002 Integration:**
- Search results could highlight account colors
- Filter by favorite status
- Sort by display_order in search results

---

## 📚 References

- [EPIC-001](../../epics/EPIC-001-account-management.md) - Parent epic
- [US-001 Account Types](../completed/US-001-account-type-taxonomy.md) - Account type taxonomy
- [US-005 AccountDialog](../completed/US-005-opening-balance-equity.md) - Dialog patterns
- [US-006 TreeWidget](../completed/US-006-account-hierarchy.md) - Tree widget patterns
- [US-007 Metadata](US-007-account-metadata.md) - Shared fields, migration dependency
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - System architecture
- [USER_GUIDE.md](../../USER_GUIDE.md) - End user documentation

---

**Story Created:** 2025-10-27
**Story Refined:** 2025-10-27 (Product Owner refinement - comprehensive task breakdown)
**Product Owner:** Product Owner Agent
**Sprint:** Sprint 10 (Planned)
**Estimated Delivery:** End of Sprint 10

---

*This story enhances UX with professional visual design and BLOCKS US-007 - Migration 010 is critical dependency for Sprint 11.*
