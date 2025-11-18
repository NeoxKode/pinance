# Changelog

All notable changes to the Pinance finance application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Sprint 14 (US-012: Date Range Filter)

#### Backend Features
- **DateRange Utility Class** (14 static methods, 380 lines):
  - `get_today()`, `get_yesterday()` - Basic date helpers
  - `get_last_n_days()` - Flexible N-day range calculation
  - `get_this_month()`, `get_last_month()` - Month boundary handling
  - `get_this_quarter()`, `get_last_quarter()` - Fiscal quarter support (Q1-Q4)
  - `get_this_year()`, `get_last_year()` - Calendar year ranges
  - `validate_custom_range()` - Business rule validation (from_date ≤ to_date)
  - Complete type hints and comprehensive docstrings
- **TransactionRepository.filter_by_date_range()** method:
  - SQL-based filtering using BETWEEN clause with database index
  - Supports optional account_id filtering
  - Excludes opening balance transactions by default
  - Returns List[Transaction] in date DESC order
- **TransactionService.filter_by_date_range()** method:
  - High-level service interface for date filtering
  - Integrates with transaction repository
  - Comprehensive error handling with FinanceAppError

#### UI Features
- **DateRangeDialog** (305 lines) - NEW!
  - Custom date picker modal with calendar popups
  - Smart defaults: 1 month ago to today
  - Real-time validation (from_date ≤ to_date)
  - Clear error messages with visual feedback
  - Keyboard shortcuts (Enter = Apply, Escape = Cancel)
  - Professional dark theme styling
- **SearchPanelWidget Date Filter** (8 major enhancements, ~400 lines):
  - Date range dropdown with 12 preset options:
    - All Time, Today, Yesterday
    - Last 7 Days, Last 30 Days
    - This Month, Last Month
    - This Quarter (dynamic Q1-Q4), Last Quarter
    - This Year (dynamic year), Last Year (dynamic year)
    - Custom Range (opens DateRangeDialog)
  - Real-time custom range display (e.g., "Jan 15 - Feb 28, 2025")
  - Signal emission: `date_filter_changed.emit(from_date, to_date)`
  - Filter state tracking: `current_date_from`, `current_date_to`
  - Clear All button integration
  - Active filter count badge update
- **MainWindow Combined Filtering** (90 lines):
  - `_reload_filtered_transactions()` method - Multi-stage filter pipeline:
    1. Date filter (SQL backend via TransactionService)
    2. Text search filter (Python post-filter)
    3. Opening balance filter (Python post-filter)
  - Smart AND logic combining all active filters
  - Filter state management: tracks date, text, and opening balance state
  - Real-time status bar feedback (e.g., "Filtered by date: Jan 01 - Jan 31")
  - Comprehensive debug logging for filter operations

#### Testing
- **Backend Unit Tests**: 31 comprehensive tests (100% passing)
  - DateRange utility methods (14 test cases)
  - Repository filter_by_date_range() edge cases
  - Service layer error handling
  - All tests execute in < 100ms
- **Integration Tests**: 5 complete workflow tests
  - Date filter only (backend filtering)
  - Text search only (Python filtering)
  - Combined date + text search (US-012 primary use case)
  - Opening balance filter
  - All filters combined (ultimate test)
- **Performance**: < 50ms average (exceeds < 100ms target by 50%)

#### Documentation
- **USER_GUIDE.md** (+467 lines, new Section 7):
  - "Finding and Filtering Transactions" comprehensive guide
  - 12 date preset examples with screenshots
  - Custom date range picker instructions
  - 5 common filter combination patterns
  - Keyboard shortcuts reference table
  - Troubleshooting guide (9 Q&As)
  - Tips and best practices
- **US-012 Story Document**: Complete task breakdown, acceptance criteria, and Definition of Done
- **Code Documentation**: All methods have comprehensive docstrings (Google style)

### Added - Sprint 14 (US-013: Category Filter)

#### Backend Features
- **TransactionRepository.get_categories_with_counts()** method (145 lines):
  - Retrieves all unique categories from transactions with count aggregation
  - SQL GROUP BY with COUNT() aggregation
  - Alphabetically sorted results
  - Supports optional account_id filtering
  - Returns List[Tuple[str, int]] (category, count) pairs
  - Uses idx_transactions_category index for performance
- **TransactionRepository.filter_by_categories()** method:
  - SQL IN clause filtering for category list
  - Parameterized queries for security
  - Handles empty category list gracefully (returns empty list)
  - Supports optional account_id filtering
  - Returns List[Transaction] in date DESC order
- **TransactionService Category Methods** (83 lines):
  - `get_categories_with_counts()` - Service wrapper with business logic
  - `filter_by_categories()` - Input validation and sanitization:
    - Validates categories is a list (raises ValueError if not)
    - Strips whitespace from category names
    - Filters out empty strings
    - Comprehensive logging for debugging

#### UI Features
- **SearchPanelWidget Category Filter** (~128 lines):
  - Category dropdown populated dynamically from database
  - "All Categories" default option (no filter active)
  - Category count display: "Groceries (23)", "Dining Out (45)"
  - Alphabetically sorted category list for easy navigation
  - Signal emission: `category_filter_changed.emit(categories)`
  - Filter state tracking: `current_categories` list
  - Helper methods: `has_category_filter()`, `clear_category_filter()`
  - `populate_categories()` method for dynamic category loading
  - Integration with filter count badge
  - Clear All Filters button support
  - Tab order keyboard navigation
- **MainWindow Category Filter Integration** (~58 lines):
  - State tracking: `current_categories` list
  - Signal handler: `_on_category_filter_changed(categories)`
  - Multi-stage filter pipeline (now 4 stages):
    1. Date filter (SQL backend)
    2. **Category filter (Python post-filter)** - NEW!
    3. Text search filter (Python post-filter)
    4. Opening balance filter (Python post-filter)
  - Status bar feedback: "Filtered by category: Groceries"
  - Category refresh on account change and data load
  - Service injection: `set_transaction_service()` for category population
  - Filter state clearing in `_on_filters_cleared()`

#### Testing
- **Backend Unit Tests**: 14 comprehensive tests (100% passing in 0.07s)
  - Repository get_categories_with_counts() (all accounts, single account, empty)
  - Repository filter_by_categories() (single, multiple, empty list, account filter)
  - Service get_categories_with_counts() (delegation, account passthrough)
  - Service filter_by_categories() (validation, None check, type check, sanitization)
- **Integration Tests**: 8 complete workflow tests (100% passing in 2.89s)
  - Get categories with counts from all accounts (verified 5 categories)
  - Get categories with counts from single account filter
  - Filter by single category (3 Groceries transactions)
  - Filter by multiple categories (5 transactions total)
  - Filter by category with account filter (credit card only)
  - Filter by empty category list (returns empty)
  - Filter by non-existent category (returns empty)
  - **Performance test**: 100+ transactions < 50ms ✅ (exceeds < 100ms target)
- **Total Tests**: 22/22 passing (100% pass rate)

#### Documentation
- **USER_GUIDE.md** (+300 lines, Section 7.3):
  - "Category Filter (US-013)" comprehensive guide
  - How to filter by category (4-step guide)
  - Understanding categories (what/where/counts)
  - 5 common use cases with examples:
    - Monthly budget review (Groceries this month)
    - Category comparison (Entertainment vs Dining Out)
    - Quarterly expense analysis (Transportation for taxes)
    - Vendor + category tracking (Starbucks in Dining Out)
    - Income verification (Salary deposits this year)
  - Combining category with other filters (7 examples)
  - Tips and best practices (5 tips)
  - Category filter examples with results
  - FAQ section (9 questions answered)
- **US-013 Story Document**: Complete Definition of Done, implementation summaries
- **Filter Panel Layout**: Updated diagram to show category dropdown
- **Filter Combinations**: Updated with 7 category-based examples
- **Code Documentation**: All methods have comprehensive docstrings (Google style)

### Changed - Sprint 14

#### Filter Architecture
- **MainWindow._on_search_changed()**: Now calls `_reload_filtered_transactions()` for unified filter handling
- **MainWindow._reload_filtered_transactions()**: Enhanced with 4-stage filter pipeline:
  1. Date filter (SQL backend)
  2. Category filter (Python post-filter) - NEW in US-013
  3. Text search filter (Python post-filter)
  4. Opening balance filter (Python post-filter)
- **SearchPanelWidget Signals**:
  - Date: Changed from `Signal(object)` to `Signal(object, object)` for date tuple
  - Category: Added `Signal(list)` for category list - NEW in US-013
- **Filter Combination Strategy**: Established pattern - SQL backend first, then Python post-filters
- **Tab Order**: Updated keyboard navigation to include date_combo and category_combo
- **Filter Count Logic**: Now tracks 4 filter types (text, date, category, opening balance)

#### Performance Improvements
- **Date Filtering**: SQL BETWEEN with idx_transactions_date index (< 50ms for 10,000+ transactions)
- **Category Filtering**: Python post-filter with idx_transactions_category index (< 50ms for 100+ transactions) - NEW in US-013
- **Combined Filters**: Sequential filtering reduces result set at each stage
- **No UI Blocking**: All filter operations complete in < 100ms (responsive UX)

---

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
