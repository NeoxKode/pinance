# US-007: Account Metadata & Organization

**Story ID:** US-007
**Epic:** [EPIC-001: Account Management & Double-Entry Foundation](../../epics/EPIC-001-account-management.md)
**Created:** 2025-10-27
**Status:** Backlog (Ready for Sprint 11)
**Priority:** P2 (Nice to Have)
**Story Points:** 5
**Assignee:** Unassigned
**Sprint:** Sprint 11 (Planned)
**Dependencies:** ✅ US-001 (Account Type Taxonomy)

---

## 📖 User Story

**As a** power user
**I want** to add notes, account numbers, and organize accounts with custom metadata
**So that** I can keep detailed records, stay organized, and customize my account management workflow

---

## 📝 Description

### Problem Statement

Users need to:
- Track bank account numbers for reconciliation
- Add notes about account purpose or restrictions
- Mark favorite accounts for quick access
- Reorder accounts for personal organization
- Track which financial institution holds each account

### Proposed Solution

Add metadata fields to accounts:
- `account_number`: Bank/institution account number
- `institution_name`: Bank or financial institution
- `notes`: Free-form text notes
- `is_favorite`: Star/favorite accounts
- `display_order`: Custom sort order
- `color_hex`: Custom color (may overlap with US-009)
- `icon`: Custom icon name

---

## 🎯 Acceptance Criteria

### AC1: Account Number Field

**Given** I am creating/editing an account
**When** I enter an account number
**Then** it should:
- Accept alphanumeric characters (e.g., "1234-5678-90")
- Be optional (not all accounts have numbers)
- Display in account details view
- Be searchable

### AC2: Institution Name

**Given** I am creating/editing an account
**When** I enter an institution name
**Then** it should:
- Support autocomplete from previously entered institutions
- Group accounts by institution in reports
- Be optional

### AC3: Notes Field

**Given** I want to add notes to an account
**When** I enter notes
**Then** they should:
- Support multi-line text (up to 1000 characters)
- Display in account details
- Be searchable

### AC4: Favorite Accounts

**Given** I have many accounts
**When** I mark an account as favorite
**Then** it should:
- Display star/heart icon
- Appear at top of account list
- Be filterable ("Show only favorites")

### AC5: Custom Display Order

**Given** I want to customize account order
**When** I drag-and-drop accounts or set display_order
**Then** accounts should:
- Sort by display_order (ascending)
- Remember custom order across sessions
- Allow reset to default order (by type, then name)

---

## 🔧 Technical Details

### Database Changes

```sql
-- Migration 011: Account metadata fields
ALTER TABLE accounts ADD COLUMN account_number TEXT;
ALTER TABLE accounts ADD COLUMN institution_name TEXT;
ALTER TABLE accounts ADD COLUMN notes TEXT;
ALTER TABLE accounts ADD COLUMN is_favorite BOOLEAN DEFAULT 0;
ALTER TABLE accounts ADD COLUMN display_order INTEGER DEFAULT 0;
ALTER TABLE accounts ADD COLUMN color_hex TEXT DEFAULT '#3B82F6';
ALTER TABLE accounts ADD COLUMN icon TEXT;

CREATE INDEX idx_accounts_institution ON accounts(institution_name);
CREATE INDEX idx_accounts_favorite ON accounts(is_favorite);
CREATE INDEX idx_accounts_display_order ON accounts(display_order);
```

### Model Update

```python
@dataclass
class Account:
    # ... existing fields ...
    account_number: Optional[str] = None
    institution_name: Optional[str] = None
    notes: Optional[str] = None
    is_favorite: bool = False
    display_order: int = 0
    color_hex: str = '#3B82F6'
    icon: Optional[str] = None
```

### Implementation

1. **Add fields to AccountDialog** (2 hours)
2. **Update AccountRepository** with search/filter methods (1 hour)
3. **Add account grouping by institution** in UI (1 hour)
4. **Implement drag-and-drop reordering** (1 hour)
5. **Add favorites filter toggle** (30 min)

---

## ✅ Definition of Done

- [x] Database migration adds metadata fields
- [x] Account model updated
- [x] AccountDialog includes all new fields
- [x] Autocomplete for institution names
- [x] Favorite toggle in UI
- [x] Drag-and-drop reordering works
- [x] Search includes metadata fields
- [x] Unit tests (8+ tests)
- [x] Documentation updated

---

## 🧪 Test Scenarios

```python
def test_account_metadata_saved():
    account = account_service.create_account(
        name="Checking",
        account_number="1234-5678",
        institution_name="Chase Bank",
        notes="Primary checking account",
        is_favorite=True,
        display_order=1
    )
    assert account.account_number == "1234-5678"
    assert account.is_favorite == True
```

---

**Story Created:** 2025-10-27
**Sprint:** Sprint 11 (Planned)
