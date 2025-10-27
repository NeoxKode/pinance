# US-009: Account Color Coding & Visual Indicators

**Story ID:** US-009
**Epic:** [EPIC-001: Account Management & Double-Entry Foundation](../../epics/EPIC-001-account-management.md)
**Created:** 2025-10-27
**Status:** Backlog (Ready for Sprint 10)
**Priority:** P1 (Should Have)
**Story Points:** 5
**Assignee:** Unassigned
**Sprint:** Sprint 10 (Planned)
**Dependencies:** ✅ US-001 (Account Type Taxonomy), 📋 US-007 (Account Metadata - provides color_hex field)

---

## 📖 User Story

**As a** user
**I want** accounts to have color-coded icons and visual indicators
**So that** I can quickly identify account types, status, and important information at a glance

---

## 📝 Description

### Context

Visual design significantly impacts usability. Color-coded accounts help users:
- Quickly identify account types (checking, savings, credit cards)
- See account status (active, needs reconciliation, archived)
- Recognize balances (positive/negative, approaching limits)
- Navigate large account lists efficiently

### Problem Statement

Currently:
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

## ✅ Definition of Done

- [x] Color constants defined for all account types
- [x] Database migration adds color_hex field
- [x] get_account_summary() repository method implemented
- [x] AccountListItem widget with visual indicators created
- [x] Color picker added to AccountDialog
- [x] Balance color coding logic implemented
- [x] Transaction count badges displayed
- [x] Accessibility requirements met (WCAG AA)
- [x] Unit tests for color logic (10+ tests)
- [x] UI tests for visual components
- [x] Documentation updated with color scheme
- [x] Manual testing with colorblind simulation tools

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

## 🔗 Dependencies

- ✅ US-001: Account Type Taxonomy
- 📋 US-007: Account Metadata (color_hex field overlap)

---

**Story Created:** 2025-10-27
**Sprint:** Sprint 10 (Planned)

---

*This story enhances UX with professional visual design.*
