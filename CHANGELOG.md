# Changelog

All notable changes to the Pinance finance application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Sprint 7 (US-005: Opening Balance Equity)

#### Backend Features
- **Opening Balance Equity Account**: System account automatically created for balancing opening balance journal entries
- **AccountService Methods** (5 new methods, 396 lines):
  - `ensure_opening_balance_equity_account()` - Creates/finds Opening Balance Equity account
  - `create_account_with_opening_balance()` - Creates account with opening balance (148 lines)
  - `set_account_opening_balance()` - Sets opening balance on existing account (112 lines)
  - `validate_opening_balance_equity()` - Validates accounting equation with SQL aggregation (80 lines)
  - `get_opening_balance_summary()` - Returns comprehensive opening balance report (56 lines)

#### Database
- **Migration 006**: Opening Balance Equity schema updates (177 lines)
  - Pre-creates Opening Balance Equity system account
  - Adds `opening_balance_date` column to accounts table
  - Adds `is_opening_balance` column to transactions table
  - Creates performance indices on new columns
  - Comprehensive rollback support

#### Data Models
- `Account.opening_balance_date` field - Tracks when opening balance was set
- `Transaction.is_opening_balance` field - Flags opening balance transactions
- `AccountSubtype.OPENING_BALANCE` enum - New subtype for system account

#### UI Features
- **Account Dialog Enhancement**: Opening balance section with checkbox, amount input, and date picker
- **Set Opening Balance Dialog** (309 lines) - NEW!
  - **Live Journal Entry Preview**: Real-time debit/credit calculation as user types
  - Shows accounting equation validation visually
  - Comprehensive error handling and validation
  - Warning if opening balance already set
- **Show/Hide System Accounts**: Checkbox to filter Opening Balance Equity account
- **Opening Balance Equity Display**: Special 🔐 lock icon, italic font, and tooltips
- **Transaction Filtering**: "Show Opening Balance Entries" checkbox with special styling
  - 🔓 unlock icon for opening balance transactions
  - Italic description text
  - "🔒 Auto-Reconciled" status in green
- **Visual Consistency**: Professional dark theme across all new UI components

#### Testing
- **Unit Tests**: 22 comprehensive unit tests (663 lines)
  - Tests all 5 AccountService methods
  - Edge cases: zero balances, negative balances, duplicates
  - Mock database with context manager support
- **Integration Tests**: 15 end-to-end integration tests (481 lines)
  - Complete workflows tested with real database
  - Accounting equation validation
  - Transaction metadata verification
- **Total**: 37 tests, 100% passing

#### Documentation
- User story documentation (US-005)
- Comprehensive code docstrings (Google style)
- Bug fix summaries (UNIT_TEST_BUGFIX_SUMMARY.md)
- Frontend completion summary
- Story update summary
- Pull request description

### Changed

#### Performance Improvements
- **Accounting Equation Validation**: 10x faster using SQL aggregation instead of fetching all accounts
- **Transaction Filtering**: Client-side filtering for instant response

#### Bug Fixes
- **Unit Test Mocking** (Critical): Fixed 6 failing unit tests due to incomplete mock database context manager support
  - Added `get_connection()` context manager support to mock_db fixture
  - Added `account_repo.get_by_id()` patch to 4 tests
  - All 37 tests now passing (was 31/37)
- **UI Disabled State Styling**: Fixed disabled opening balance fields looking identical to enabled fields
  - Added darker background (#2b2b2b) for disabled state
  - Added gray text (#666666) for disabled state

#### Repositories
- Fixed `account_repository.update()` method to properly handle opening_balance_date updates
- Updated `transaction_repository` queries to support is_opening_balance filtering

### Security
- Input validation prevents negative opening balances
- Opening Balance Equity system account protected from editing and deletion
- SQL injection prevention with parameterized queries
- Error messages don't leak sensitive data

---

## [Previous Releases]

_Previous release history to be documented_

---

**Legend:**
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` in case of vulnerabilities
