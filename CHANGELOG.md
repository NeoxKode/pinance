# Changelog

All notable changes to the Pinance finance application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Sprint 17 (EPIC-003 Kickoff: Reporting & Charts) 🎬

#### Epic Planning (November 19, 2025)
- **EPIC-003: Reporting and Charts** - NEW EPIC! (7 stories, 35 points, 5 sprints)
  - Complete epic document with vision, goals, and success metrics
  - User stories: US-017 through US-027 (infrastructure, charts, dashboard)
  - Target release: v2.1.0
  - Expected impact: +15 NPS, 70%+ user adoption of reports
  - RICE Score: 9.0 (Excellent - High Priority)
- **Sprint 17 Planning** (2 weeks, 7 story points):
  - US-017: Reporting Infrastructure & Dashboard Layout (4 pts) - Foundation
  - US-018: Spending by Category Report - Pie Chart (3 pts) - First visual report
  - Sprint goal: Build reporting foundation and deliver first visual report
  - Sprint kickoff document created with 10-day detailed schedule
- **Documentation Updates**:
  - EPIC_STORY_INDEX.md updated (3 epics, 25 stories, 150 total points)
  - 7 new stories added to backlog (US-017 through US-023)
  - Sprint 17 kickoff document (10-day schedule, tasks, risks)
  - Updated roadmap: v2.1.0 now includes EPIC-002 + EPIC-003

#### Planned Features (Sprint 17 - Next Up)
- **Reporting Infrastructure** (US-017):
  - `ReportService` base class for all reports
  - Chart widget base classes (Pie, Line, Bar)
  - Dashboard window with grid layout (2×3 widgets)
  - Global date range selector for all reports
  - Common UI components (loading, error, empty states)
- **Spending by Category Report** (US-018):
  - Interactive pie chart showing category breakdown
  - Hover tooltips with percentages and amounts
  - Double-click drill-down to transactions
  - Configuration: Include income, absolute values
  - Top 10 categories, rest grouped as "Other"

#### Upcoming Sprints (EPIC-003 Roadmap)
- **Sprint 18** (Trend Analysis):
  - US-019: Spending Trends Over Time - Line Chart (3 pts)
  - US-020: Income vs Expense Comparison - Bar Chart (3 pts)
- **Sprint 19** (Account Analysis):
  - US-021: Account Balances Over Time - Multi-line Chart (4 pts)
  - US-022: Net Worth Tracking Report (3 pts)
- **Sprint 20** (Advanced Features):
  - US-023: Report Export - PDF & CSV (3 pts)
  - US-024: Interactive Report Drill-Down (3 pts)
  - US-025: Custom Report Date Ranges & Filters (2 pts)
- **Sprint 21** (Dashboard & Polish):
  - US-026: Financial Dashboard - Summary View (4 pts)
  - US-027: Report Performance Optimization (3 pts)

#### Architecture Changes (Planned)
- **New Components**:
  - `finance_app/business/report_service.py` - Base report service
  - `finance_app/business/spending_report_service.py` - Spending reports
  - `finance_app/data/repositories/report_repository.py` - Report queries
  - `finance_app/ui/widgets/chart_widgets.py` - Chart base classes
  - `finance_app/ui/windows/dashboard_window.py` - Main dashboard
- **Estimated Code**: ~2,500 lines Python + ~100 lines SQL + ~1,500 lines tests
- **New Database Tables** (Future sprints):
  - `balance_snapshots` (Migration 015) - Historical balance cache
  - Report configurations (extends `saved_filters` from US-015)

#### Success Metrics (EPIC-003 Targets)
- Report generation: < 500ms for 10K transactions
- Chart rendering: < 200ms for all chart types
- Dashboard load: < 2 seconds (6 reports)
- User adoption: 70%+ view reports within first week
- NPS increase: +15 points (compound with EPIC-002)
- Export usage: 20%+ users export reports

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

### Added - Sprint 15 (US-014: Amount Range Filter)

#### Backend Features
- **TransactionRepository.filter_by_amount_range()** method (83 lines):
  - SQL-based filtering with BETWEEN and comparison operators
  - Supports min_amount, max_amount, and absolute value modes
  - Uses idx_transactions_amount index for performance
  - Handles all 4 filtering modes:
    - Both min and max: `BETWEEN min_amount AND max_amount`
    - Min only: `>= min_amount`
    - Max only: `<= max_amount`
    - Absolute mode: `ABS(amount) BETWEEN/>=/<= threshold`
  - Supports optional account_id filtering
  - Returns List[Transaction] in date DESC order
- **TransactionService.filter_by_amount_range()** method (68 lines):
  - High-level service interface for amount filtering
  - Input validation: min_amount <= max_amount (raises ValueError if violated)
  - Type validation: ensures Decimal types
  - Comprehensive error handling with FinanceAppError
  - Debug logging for troubleshooting
  - Delegates to repository layer

#### UI Features
- **SearchPanelWidget Amount Filter** (~311 lines):
  - Min/max amount input fields with placeholders ("$0.00", "$999,999.99")
  - Absolute value checkbox with tooltip explanation
  - 4 preset buttons for common scenarios:
    - **< $20** - Small charges (subscriptions, coffee, small purchases)
    - **$20 - $100** - Mid-range expenses (groceries, utilities, gas)
    - **> $100** - Large purchases (rent, electronics, major expenses)
    - **> $500** - Very large transactions (rent, bonuses, big purchases)
  - 500ms debounce timer on text input (prevents excessive filtering)
  - Signal emission: `amount_filter_changed.emit(min_amount, max_amount, absolute)`
  - Filter state tracking: `current_amount_min`, `current_amount_max`, `current_amount_absolute`
  - Helper methods: `has_amount_filter()`, `clear_amount_filter()`
  - Integration with filter count badge
  - Clear All Filters button support
  - Tab order keyboard navigation
- **MainWindow Amount Filter Integration** (~115 lines):
  - State tracking: `current_amount_min`, `current_amount_max`, `current_amount_absolute`
  - Signal handler: `_on_amount_filter_changed(min_amount, max_amount, absolute)`
  - Multi-stage filter pipeline (now 5 stages):
    1. Date filter (SQL backend)
    2. **Amount filter (SQL backend with set intersection)** - NEW!
    3. Category filter (Python post-filter)
    4. Text search filter (Python post-filter)
    5. Opening balance filter (Python post-filter)
  - Status bar feedback: "Filtered by amount: $100 - $500" or ">= $50 (absolute)"
  - Smart AND logic: intersects amount results with date results
  - Filter state clearing in `_on_filters_cleared()`

#### Testing
- **Backend Unit Tests**: 14 comprehensive tests (100% passing in 0.05s)
  - Repository filter_by_amount_range() (min only, max only, both, absolute mode, account filter)
  - Service filter_by_amount_range() (delegation, validation, min > max error, type checking)
  - Edge cases: zero amounts, negative amounts, Decimal precision
- **Integration Tests**: 8 complete workflow tests (100% passing in 2.47s)
  - Filter by min amount only (>= $50)
  - Filter by max amount only (<= $100)
  - Filter by range ($50 - $200)
  - Filter by absolute value (|amount| >= $100 catches both income and expenses)
  - Filter with account_id restriction
  - Combined filters (date + amount)
  - Empty results (no transactions in range)
  - **Performance test**: 1,000+ transactions < 100ms ✅ (meets performance target)
- **Total Tests**: 22/22 passing (100% pass rate)

#### Documentation
- **USER_GUIDE.md** (+520 lines, Section 7.4):
  - "Amount Range Filter (US-014)" comprehensive guide
  - How to filter by amount range (4-step guide)
  - Preset button explanations with use cases:
    - < $20: Subscription hunting, recurring charges
    - $20-$100: Groceries, utilities, gas
    - > $100: Rent, electronics, major expenses
    - > $500: Large transactions, bonuses
  - Custom amount ranges (min only, max only, both)
  - Absolute value mode (when to use / not use)
  - Amount filter input formats (basic, with symbols, with commas)
  - Combining amount filter with other filters (7 examples)
  - Tips and best practices (7 tips)
  - 5 detailed examples (subscription hunt, large purchase review, budget variance, etc.)
  - FAQ section (16 questions answered)
- **US-014 Story Document**: Complete Definition of Done, task breakdown with actual times
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
