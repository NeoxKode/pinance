# Epic 3: Reporting and Charts

**Epic ID:** EPIC-003
**Status:** 📋 PLANNED (Sprint 17 Start)
**Priority:** P1 (High - Business Value)
**Estimated Effort:** 4-5 sprints (8-10 weeks, ~80-100 hours total)
**Target Sprints:** Sprint 17-21
**Created:** November 19, 2025
**Updated:** November 19, 2025
**Owner:** Product Owner
**Progress:** 0/7 stories completed (0/35 story points = 0%)
**Sprint 17:** 🎬 KICKOFF - Planning Phase

---

## 📖 Epic Summary

Transform transaction data into actionable financial insights through visual reports and interactive charts. Enable users to understand spending patterns, track budgets, analyze trends, and make data-driven financial decisions. Build upon EPIC-002's search/filter foundation to deliver comprehensive reporting capabilities that answer key financial questions at a glance.

### Vision Statement

*"As a user managing my finances, I want to see visual reports and charts that show where my money goes, how my spending trends over time, and whether I'm meeting my financial goals, so I can make informed decisions and improve my financial health without manual calculations or spreadsheets."*

---

## 🎯 Business Goals

### Primary Goals

1. **Enable Financial Insights** - Transform raw transaction data into meaningful information
2. **Support Decision Making** - Help users identify spending problems and opportunities
3. **Increase User Engagement** - Keep users returning to check reports and track progress
4. **Differentiate from Competitors** - Offer compelling visualizations that users can't get elsewhere
5. **Prepare for Budget Features** - Foundation for EPIC-004 (Budget Management)
6. **Drive User Retention** - Reports become a "must-have" feature that prevents churn

### Success Metrics

- ✅ 70% of users view at least one report within first week of release
- ✅ Report generation: < 500ms for 10,000 transactions
- ✅ Chart rendering: < 200ms for all chart types
- ✅ NPS score increase: +15 points after EPIC-003 (compound with EPIC-002)
- ✅ Feature usage: 50%+ users view reports weekly, 30%+ view daily
- ✅ User satisfaction: "Very satisfied" with reporting in post-release survey
- ✅ Export usage: 20%+ users export reports (indicates business/serious use)

### Business Value (RICE Score)

- **Reach:** 100% of active users (everyone wants to see spending analysis)
- **Impact:** VERY HIGH (3.5/3) - Key differentiator, drives retention
- **Confidence:** 90% - Tech stack supports charting (Qt Charts available)
- **Effort:** 35 story points

**RICE Score:** (100% × 3.5 × 90%) / 35 = **9.0** (Excellent - High Priority)

---

## 📊 Current State vs Desired State

### Current State ✅ (What's Working)

From completed EPIC-001 and EPIC-002:

- ✅ EPIC-001 complete (12/12 stories, 73 points, Account Management)
- ✅ EPIC-002 complete (6/6 stories, 21 points, Search & Filter)
- ✅ Transaction data captured with categories, dates, amounts
- ✅ Account balances calculated and displayed
- ✅ Search and filter system operational (< 50ms performance)
- ✅ Account hierarchy with parent/child relationships
- ✅ Reconciliation system tracking cleared transactions
- ✅ Double-entry accounting ensures data integrity
- ✅ Database indexed for fast queries
- ✅ Clean professional UI (Grade A/A+ across all stories)

### Gaps 🔴 (What's Missing - EPIC-003 Will Solve)

- ❌ **No visual reports** - Data is in tables, no charts or graphs
- ❌ **No spending analysis** - Cannot see "where money goes" at a glance
- ❌ **No trend analysis** - Cannot see spending patterns over time
- ❌ **No category breakdown** - Cannot visualize spending by category
- ❌ **No income vs expense** - No high-level financial health view
- ❌ **No net worth tracking** - Cannot see asset/liability trends
- ❌ **No export capabilities** - Cannot save reports for taxes, advisors
- ❌ **No dashboard** - No single view of key financial metrics
- ❌ **No date comparison** - Cannot compare "this month vs last month"
- ❌ **No custom reports** - Limited to pre-built views

### Desired End State 🎯 (After EPIC-003 Complete)

- ✅ **Interactive Dashboard** - Key metrics at a glance (income, expenses, savings rate)
- ✅ **Spending by Category** - Pie/donut chart showing category breakdown
- ✅ **Spending Trends** - Line chart showing expenses over time (daily/weekly/monthly)
- ✅ **Income vs Expense** - Bar chart comparing income and expenses by period
- ✅ **Account Balances Over Time** - Line chart showing balance trends
- ✅ **Net Worth Tracking** - Assets minus liabilities over time
- ✅ **Category Drill-Down** - Click category to see transactions
- ✅ **Custom Date Ranges** - All reports support flexible date filters
- ✅ **Export Reports** - PDF and CSV export for all reports
- ✅ **Print Reports** - Printer-friendly layouts
- ✅ **Saved Report Views** - Save custom date ranges and filters

**User Impact:** Users gain complete visibility into financial health, identify spending problems 10x faster, and can answer questions like "Where does my money go?" in < 5 seconds instead of hours of manual analysis.

---

## 📈 Sprint Breakdown

### Sprint 17 (7 points) - Foundation - Weeks 1-2 🎬 **KICKOFF**

**Goal:** Establish reporting infrastructure and deliver first visual report

**Stories:**
- **US-017: Reporting Infrastructure & Dashboard Layout** (4 pts) - Report framework + dashboard shell
- **US-018: Spending by Category Report (Pie Chart)** (3 pts) - First visual report

**Success Criteria:**
- Dashboard layout with placeholder report widgets
- Working pie chart showing spending by category
- Report date range selector working
- Performance: < 200ms chart rendering

**Velocity:** 7 points (slightly above EPIC-002 avg of 4.5 pts/sprint, within EPIC-001 avg of 6.08 pts/sprint)

**Deliverables:**
- Report infrastructure (ReportService, ChartWidget base classes)
- Dashboard window with layout
- Spending by category pie chart
- 15+ unit tests
- 5+ integration tests
- User Guide section on reports
- CHANGELOG.md Sprint 17 entry

---

### Sprint 18 (6 points) - Trend Analysis - Weeks 3-4

**Goal:** Enable time-based spending analysis

**Stories:**
- **US-019: Spending Trends Over Time (Line Chart)** (3 pts) - Daily/weekly/monthly spending
- **US-020: Income vs Expense Comparison (Bar Chart)** (3 pts) - Side-by-side comparison

**Success Criteria:**
- Line chart showing spending trends (selectable granularity)
- Bar chart comparing income vs expenses by period
- Drill-down to transactions from chart click
- Performance: < 300ms for complex aggregations

**Velocity:** 6 points (matches EPIC-001 average)

**Deliverables:**
- Line chart component with zoom/pan
- Bar chart component with tooltips
- Chart interaction (click to drill down)
- 15+ unit tests
- 5+ integration tests
- User Guide sections for each report

---

### Sprint 19 (7 points) - Account Analysis - Weeks 5-6

**Goal:** Track account balances and net worth

**Stories:**
- **US-021: Account Balances Over Time (Line Chart)** (4 pts) - Multi-line chart with account selection
- **US-022: Net Worth Tracking Report** (3 pts) - Assets vs Liabilities trend

**Success Criteria:**
- Multi-line chart showing multiple account balances
- Net worth calculation and trend visualization
- Account selector (choose which accounts to display)
- Historical balance snapshots calculated correctly

**Velocity:** 7 points

**Deliverables:**
- Multi-line chart component
- Net worth calculation service
- Account selection UI
- 15+ unit tests
- 5+ integration tests
- User Guide sections

---

### Sprint 20 (8 points) - Advanced Features - Weeks 7-8

**Goal:** Export, drill-down, and custom report features

**Stories:**
- **US-023: Report Export (PDF & CSV)** (3 pts) - Export all reports
- **US-024: Interactive Report Drill-Down** (3 pts) - Click chart to see transactions
- **US-025: Custom Report Date Ranges & Filters** (2 pts) - Flexible report configuration

**Success Criteria:**
- PDF export with charts rendered as images
- CSV export with underlying data
- Click any chart element to filter transactions
- Custom date ranges work across all reports
- Saved report configurations persist

**Velocity:** 8 points (stretch sprint)

**Deliverables:**
- PDF generation service
- CSV export functionality
- Chart click handlers
- Report configuration dialog
- 15+ unit tests
- 5+ integration tests

---

### Sprint 21 (7 points) - Polish & Performance - Weeks 9-10 ⚡ **FINAL**

**Goal:** Dashboard integration, performance optimization, final polish

**Stories:**
- **US-026: Financial Dashboard (Summary View)** (4 pts) - All reports on one page
- **US-027: Report Performance Optimization** (3 pts) - Caching, async loading

**Success Criteria:**
- Dashboard shows 5+ key metrics and mini-charts
- All reports load in < 500ms for 10K transactions
- Responsive layout (resize dashboard widgets)
- Report caching reduces subsequent loads to < 50ms

**Velocity:** 7 points

**Deliverables:**
- Complete dashboard with all reports
- Performance optimizations (caching, indexing)
- Responsive layouts
- 15+ performance tests
- Complete User Guide chapter
- Release notes

---

### EPIC-003 Totals

**Total Story Points:** 35 points
**Total Sprints:** 5 (10 weeks)
**Expected Completion:** Sprint 21 (Week 10)
**Average Velocity:** 7 points/sprint (vs. EPIC-002 avg of 4.5 pts/sprint, EPIC-001 avg of 6.08 pts/sprint)

---

## 👥 User Stories Overview

This epic contains **7 user stories** organized in 5 phases:

### Phase 1: Foundation (Sprint 17) - 7 points 🎬

- 📋 **US-017**: Reporting Infrastructure & Dashboard Layout (4 pts) - P0 Must Have
- 📋 **US-018**: Spending by Category Report (3 pts) - P0 Must Have

### Phase 2: Trend Analysis (Sprint 18) - 6 points

- 📋 **US-019**: Spending Trends Over Time (3 pts) - P0 Must Have
- 📋 **US-020**: Income vs Expense Comparison (3 pts) - P0 Must Have

### Phase 3: Account Analysis (Sprint 19) - 7 points

- 📋 **US-021**: Account Balances Over Time (4 pts) - P1 Should Have
- 📋 **US-022**: Net Worth Tracking Report (3 pts) - P1 Should Have

### Phase 4: Advanced Features (Sprint 20) - 8 points

- 📋 **US-023**: Report Export (PDF & CSV) (3 pts) - P2 Could Have
- 📋 **US-024**: Interactive Report Drill-Down (3 pts) - P1 Should Have
- 📋 **US-025**: Custom Report Date Ranges (2 pts) - P2 Could Have

### Phase 5: Polish & Performance (Sprint 21) - 7 points

- 📋 **US-026**: Financial Dashboard (4 pts) - P0 Must Have
- 📋 **US-027**: Report Performance Optimization (3 pts) - P1 Should Have

---

## 📝 User Stories (Detailed)

---

### **US-017: Reporting Infrastructure & Dashboard Layout** 🏗️ **FOUNDATION**

**As a** developer building reporting features
**I want** a reusable reporting infrastructure with base classes and common components
**So that** all reports follow consistent patterns and share common functionality

**Priority:** P0 (Must Have) - **Foundation for all other reports**
**Story Points:** 4
**Sprint:** Sprint 17 (Week 1-2)

**Acceptance Criteria:**

**AC1: Report Service Infrastructure**
- [ ] `ReportService` base class with common report operations
- [ ] Methods: `generate_report()`, `get_date_range_data()`, `aggregate_by_period()`
- [ ] Support for daily, weekly, monthly, quarterly, yearly aggregations
- [ ] Handles timezone and date boundary edge cases

**AC2: Chart Widget Base Classes**
- [ ] `BaseChartWidget` abstract class (inherits from QWidget)
- [ ] `PieChartWidget`, `LineChartWidget`, `BarChartWidget` implementations
- [ ] Common features: legend, tooltips, title, loading state
- [ ] Responsive sizing (adapts to container)
- [ ] Qt Charts integration (if available) or matplotlib fallback

**AC3: Dashboard Layout**
- [ ] New "Reports" menu item in main window menu bar
- [ ] Dashboard window with grid layout (2x3 or 3x2)
- [ ] Placeholder cards for 6 reports (empty state initially)
- [ ] Date range selector at top (global for all reports)
- [ ] "Refresh All" button to reload all reports

**AC4: Common UI Components**
- [ ] Date range selector widget (reuse from US-012)
- [ ] Loading spinner for async report generation
- [ ] Error state display ("Unable to generate report")
- [ ] Empty state display ("No data for selected period")

**Technical Notes:**
- Use Qt Charts (PySide6.QtCharts) if available, else matplotlib + FigureCanvas
- Create `finance_app/business/report_service.py` base class
- Create `finance_app/ui/widgets/chart_widgets.py` module
- Create `finance_app/ui/windows/dashboard_window.py`

**Dependencies:**
- ✅ EPIC-001 complete (transaction data available)
- ✅ EPIC-002 complete (search/filter infrastructure)
- ✅ Qt6 Charts library (check if installed, add to requirements if needed)

**Definition of Done:**
- [ ] ReportService base class with 5+ methods
- [ ] 3 chart widget base classes (Pie, Line, Bar)
- [ ] Dashboard window with grid layout
- [ ] Date range selector integrated
- [ ] 15+ unit tests (services + widgets)
- [ ] 3+ integration tests
- [ ] User Guide section on accessing dashboard
- [ ] CHANGELOG.md entry

---

### **US-018: Spending by Category Report (Pie Chart)** 🥧 **QUICK WIN**

**As a** user tracking my spending
**I want** to see a pie chart showing my spending breakdown by category
**So that** I can quickly identify which categories consume most of my budget

**Priority:** P0 (Must Have) - **Most requested report feature**
**Story Points:** 3
**Sprint:** Sprint 17 (Week 1-2)

**Acceptance Criteria:**

**AC1: Pie Chart Display**
- [ ] Pie chart showing spending by category for selected date range
- [ ] Each slice represents a category (color-coded)
- [ ] Shows percentage and dollar amount for each slice
- [ ] Legend lists all categories with colors and amounts
- [ ] Top 10 categories shown, rest grouped as "Other" if > 10 categories

**AC2: Chart Interactions**
- [ ] Hover over slice shows tooltip: "Groceries: $1,234.56 (23.4%)"
- [ ] Click slice to highlight (visual feedback)
- [ ] Double-click slice opens transactions filtered by that category (drill-down)
- [ ] Legend item click toggles category visibility

**AC3: Configuration Options**
- [ ] Toggle: "Include income" (default: expenses only)
- [ ] Toggle: "Absolute values" (show $500 credit and $500 debit as same)
- [ ] Date range selector (uses US-012 date range logic)
- [ ] Account filter: "All accounts" or specific accounts

**AC4: Empty States**
- [ ] "No expenses in selected period" if no data
- [ ] "All categories hidden" if user hides all via legend
- [ ] Shows message with actionable suggestion

**Technical Notes:**
- Use `PieChartWidget` from US-017
- SQL: `SELECT category, SUM(amount) FROM transactions WHERE amount < 0 GROUP BY category`
- Handle negative amounts (expenses) vs positive (income)
- Color palette: Use app theme colors + auto-generated palette

**Dependencies:**
- ✅ US-017 (Chart infrastructure)
- ✅ Categories in transactions (EPIC-001)
- ✅ Date range filtering (US-012)

**Use Cases:**
1. **Budget Review:** "Where did my money go this month?"
2. **Category Analysis:** "Is dining out consuming too much budget?"
3. **Spending Awareness:** "Visualize my largest expense categories"

**Definition of Done:**
- [ ] Pie chart displays category breakdown
- [ ] Hover tooltips working
- [ ] Double-click drill-down to transactions
- [ ] Configuration toggles functional
- [ ] 10+ unit tests (service + widget)
- [ ] 5+ integration tests
- [ ] User Guide section with screenshot
- [ ] Performance: < 200ms for 10K transactions

---

### **US-019: Spending Trends Over Time (Line Chart)** 📈

**As a** user
**I want** to see a line chart showing my spending trends over time
**So that** I can identify patterns, seasonal changes, and spending spikes

**Priority:** P0 (Must Have) - **Core trend analysis**
**Story Points:** 3
**Sprint:** Sprint 18 (Week 3-4)

**Acceptance Criteria:**

**AC1: Line Chart Display**
- [ ] Line chart showing total spending over time
- [ ] X-axis: Date (daily, weekly, or monthly granularity)
- [ ] Y-axis: Amount ($)
- [ ] Smooth line connecting data points
- [ ] Data points marked (circles or dots)

**AC2: Granularity Selector**
- [ ] Dropdown: "Daily", "Weekly", "Monthly", "Quarterly"
- [ ] Chart updates when granularity changes
- [ ] Smart defaults based on date range:
  - < 31 days: Daily
  - 31-90 days: Weekly
  - 90+ days: Monthly

**AC3: Multi-Line Support**
- [ ] Toggle: "Compare categories" - shows multiple lines (one per category)
- [ ] Toggle: "Income vs Expense" - two lines (income + expense)
- [ ] Legend shows all lines with color coding
- [ ] Can toggle line visibility via legend

**AC4: Chart Interactions**
- [ ] Hover shows tooltip: "Jan 15, 2025: $234.56"
- [ ] Click data point highlights (visual feedback)
- [ ] Double-click data point shows transactions for that period
- [ ] Zoom: Scroll wheel or pinch to zoom X-axis
- [ ] Pan: Click-drag to pan left/right

**Technical Notes:**
- Use `LineChartWidget` from US-017
- Aggregate by period: `GROUP BY strftime('%Y-%m-%d', date)` for daily
- Handle missing data (gaps) - show as zero or skip point?
- Chart library: Qt Charts QLineSeries or matplotlib

**Dependencies:**
- ✅ US-017 (Chart infrastructure)
- ✅ Transaction date data (EPIC-001)

**Definition of Done:**
- [ ] Line chart with spending trends
- [ ] Granularity selector working
- [ ] Multi-line comparison working
- [ ] Zoom and pan functional
- [ ] 10+ unit tests
- [ ] 5+ integration tests
- [ ] User Guide section

---

### **US-020: Income vs Expense Comparison (Bar Chart)** 📊

**As a** user
**I want** to see a bar chart comparing my income and expenses side-by-side
**So that** I can see if I'm spending more than I earn and by how much

**Priority:** P0 (Must Have) - **Financial health indicator**
**Story Points:** 3
**Sprint:** Sprint 18 (Week 3-4)

**Acceptance Criteria:**

**AC1: Bar Chart Display**
- [ ] Grouped bar chart: Income (green) vs Expenses (red)
- [ ] X-axis: Time periods (same granularity as US-019)
- [ ] Y-axis: Amount ($)
- [ ] Each period has two bars side-by-side
- [ ] Net savings line overlaid (Income - Expenses)

**AC2: Summary Statistics**
- [ ] Text summary above chart:
  - "Total Income: $X"
  - "Total Expenses: $Y"
  - "Net Savings: $Z" (green if positive, red if negative)
  - "Savings Rate: N%" (Net / Income * 100)

**AC3: Chart Interactions**
- [ ] Hover shows detailed tooltip: "Jan 2025: Income $3,200, Expenses $2,100, Net +$1,100"
- [ ] Click bar highlights period
- [ ] Double-click bar shows transactions for that period and type (income or expense)

**AC4: Configuration**
- [ ] Toggle: "Show net savings line" (default: on)
- [ ] Toggle: "Stack subcategories" (shows stacked bars with category breakdown)
- [ ] Granularity selector (daily/weekly/monthly)

**Technical Notes:**
- Use `BarChartWidget` from US-017
- Income: `SUM(amount) WHERE amount > 0`
- Expenses: `SUM(ABS(amount)) WHERE amount < 0`
- Net: Income - Expenses
- Savings Rate: (Net / Income) * 100

**Dependencies:**
- ✅ US-017 (Chart infrastructure)

**Definition of Done:**
- [ ] Bar chart with income vs expense
- [ ] Summary statistics displayed
- [ ] Net savings line overlaid
- [ ] Interactive tooltips and drill-down
- [ ] 10+ unit tests
- [ ] 5+ integration tests
- [ ] User Guide section

---

### **US-021: Account Balances Over Time (Line Chart)** 💰

**As a** user managing multiple accounts
**I want** to see how my account balances change over time
**So that** I can track growth, identify cash flow issues, and monitor savings goals

**Priority:** P1 (Should Have) - **Important for multi-account users**
**Story Points:** 4
**Sprint:** Sprint 19 (Week 5-6)

**Acceptance Criteria:**

**AC1: Multi-Line Chart**
- [ ] Line chart with one line per selected account
- [ ] Each line shows account balance over time
- [ ] Legend shows account names with color coding
- [ ] Supports 1-10 accounts simultaneously

**AC2: Account Selection**
- [ ] Account multi-select dropdown (checkboxes)
- [ ] "Select All" / "Deselect All" buttons
- [ ] Account hierarchy support (select parent includes children)
- [ ] Selected accounts persist across sessions

**AC3: Balance Calculation**
- [ ] Historical balance calculated for each date point
- [ ] Considers all transactions up to that date
- [ ] Opening balance factored in correctly
- [ ] Handles transfers between selected accounts

**AC4: Chart Features**
- [ ] Hover tooltip: "Checking Account - Jan 15: $2,345.67"
- [ ] Click line to highlight that account
- [ ] Toggle account visibility via legend click
- [ ] Zoom and pan (like US-019)

**Technical Notes:**
- Calculate balance at each point: `SELECT SUM(amount) WHERE date <= ?`
- Performance: Cache balance snapshots daily to avoid recalculating
- Create `BalanceSnapshotService` for efficient historical balance queries

**Dependencies:**
- ✅ US-017 (Chart infrastructure)
- ✅ Account balance calculation (EPIC-001)

**Definition of Done:**
- [ ] Multi-line chart with account balances
- [ ] Account selector with hierarchy support
- [ ] Historical balance calculation accurate
- [ ] 12+ unit tests
- [ ] 5+ integration tests
- [ ] User Guide section

---

### **US-022: Net Worth Tracking Report** 💎

**As a** user
**I want** to see my net worth (assets - liabilities) over time
**So that** I can track my overall financial health and progress toward wealth goals

**Priority:** P1 (Should Have) - **High-level financial health metric**
**Story Points:** 3
**Sprint:** Sprint 19 (Week 5-6)

**Acceptance Criteria:**

**AC1: Net Worth Calculation**
- [ ] Net Worth = Sum(Asset accounts) - Sum(Liability accounts)
- [ ] Asset accounts: Checking, Savings, Investment
- [ ] Liability accounts: Credit Card, Loan
- [ ] Excludes: Income, Expense, Equity accounts

**AC2: Net Worth Chart**
- [ ] Line chart showing net worth over time
- [ ] Stacked area chart (optional): Assets (green) and Liabilities (red)
- [ ] Shows total net worth prominently at top
- [ ] Shows change: "Net worth increased by $X (+Y%) this month"

**AC3: Account Type Breakdown**
- [ ] Table below chart:
  - Row 1: Total Assets: $X (List: Checking $Y, Savings $Z, ...)
  - Row 2: Total Liabilities: $X (List: Credit Card $Y, Loan $Z, ...)
  - Row 3: Net Worth: $X
- [ ] Expandable rows to see individual accounts

**AC4: Milestone Markers**
- [ ] Visual markers on chart for milestones:
  - First $10K net worth
  - First $50K net worth
  - First $100K net worth
- [ ] User can add custom milestones

**Technical Notes:**
- Reuse balance calculation from US-021
- Account type mapping: Assets (normal_balance = 'Dr'), Liabilities (normal_balance = 'Cr')
- Cache daily snapshots for performance

**Dependencies:**
- ✅ US-017 (Chart infrastructure)
- ✅ US-021 (Balance calculation service)
- ✅ Account types (EPIC-001)

**Definition of Done:**
- [ ] Net worth chart with trend
- [ ] Account breakdown table
- [ ] Milestone markers
- [ ] 10+ unit tests
- [ ] 5+ integration tests
- [ ] User Guide section

---

### **US-023: Report Export (PDF & CSV)** 📄

**As a** user
**I want** to export reports to PDF and CSV formats
**So that** I can share them with tax advisors, save for records, or import into other tools

**Priority:** P2 (Could Have) - **Business/power user feature**
**Story Points:** 3
**Sprint:** Sprint 20 (Week 7-8)

**Acceptance Criteria:**

**AC1: PDF Export**
- [ ] "Export to PDF" button on each report
- [ ] PDF includes:
  - Report title and date range
  - Chart rendered as high-quality image
  - Summary statistics (text)
  - Generated date/time
  - App branding (optional)
- [ ] File name: "SpendingByCategory_2025-01-01_to_2025-01-31.pdf"

**AC2: CSV Export**
- [ ] "Export to CSV" button on each report
- [ ] CSV contains underlying data (not chart image)
- [ ] Example (Spending by Category):
  ```
  Category,Amount,Percentage
  Groceries,1234.56,23.4%
  Dining Out,567.89,10.8%
  ...
  ```
- [ ] Respects current filters and date range

**AC3: Export Dialog**
- [ ] File save dialog with default location (Documents/FinanceReports/)
- [ ] Format selector: PDF or CSV
- [ ] Option: "Include all data" vs "Current view only"
- [ ] Success notification: "Report saved to [path]"

**AC4: Batch Export**
- [ ] "Export All Reports" button on dashboard
- [ ] Exports all visible reports to a single folder
- [ ] Generates ZIP file with all PDFs and CSVs

**Technical Notes:**
- PDF: Use ReportLab or Qt QPrinter for PDF generation
- CSV: Use Python csv module
- Chart to image: QPixmap.save() or matplotlib savefig()

**Dependencies:**
- ✅ All report types (US-018 through US-022)

**Definition of Done:**
- [ ] PDF export working for all report types
- [ ] CSV export with accurate data
- [ ] Batch export functionality
- [ ] 8+ unit tests
- [ ] 3+ integration tests
- [ ] User Guide section on exporting

---

### **US-024: Interactive Report Drill-Down** 🔍

**As a** user viewing a report
**I want** to click on any chart element to see the underlying transactions
**So that** I can investigate specific data points and verify report accuracy

**Priority:** P1 (Should Have) - **Critical for trust and investigation**
**Story Points:** 3
**Sprint:** Sprint 20 (Week 7-8)

**Acceptance Criteria:**

**AC1: Chart Click Handler**
- [ ] Clicking any chart element opens transaction list
- [ ] Pie chart: Click slice shows transactions for that category
- [ ] Line chart: Click point shows transactions for that date/period
- [ ] Bar chart: Click bar shows transactions for that period and type (income/expense)

**AC2: Transaction Filter Dialog**
- [ ] Dialog title: "Transactions: [Category/Period]"
- [ ] Shows filtered transaction list (reuses main transaction list component)
- [ ] Date range highlighted (e.g., "Jan 1-31, 2025")
- [ ] Applied filters clearly displayed
- [ ] Can export filtered transactions to CSV

**AC3: Breadcrumb Navigation**
- [ ] Shows navigation path: "Reports > Spending by Category > Groceries"
- [ ] Can click breadcrumb to go back to report
- [ ] "Back to Report" button in transaction view

**AC4: Context Preservation**
- [ ] Report state preserved when drilling down (date range, filters)
- [ ] Returning to report shows same view as before drill-down
- [ ] Can drill down multiple levels (report > category > individual transaction)

**Technical Notes:**
- Emit Qt signals from chart widgets: `chart_element_clicked(category, date_range)`
- Main window listens to signals and shows filtered transaction view
- Reuse existing transaction list widget (EPIC-001)
- Use navigation stack for back button

**Dependencies:**
- ✅ All chart widgets (US-017, US-018, US-019, US-020)
- ✅ Transaction list widget (EPIC-001)
- ✅ Search/filter infrastructure (EPIC-002)

**Definition of Done:**
- [ ] Click handlers on all chart types
- [ ] Transaction filter dialog working
- [ ] Breadcrumb navigation implemented
- [ ] Context preserved on back navigation
- [ ] 10+ unit tests
- [ ] 5+ integration tests
- [ ] User Guide section

---

### **US-025: Custom Report Date Ranges & Filters** ⚙️

**As a** power user
**I want** to customize reports with flexible date ranges and filters
**So that** I can create reports for specific needs (e.g., "Q4 2024 business expenses")

**Priority:** P2 (Could Have) - **Power user feature**
**Story Points:** 2
**Sprint:** Sprint 20 (Week 7-8)

**Acceptance Criteria:**

**AC1: Global Date Range Selector**
- [ ] Date range selector at top of dashboard (already in US-017)
- [ ] All reports update when date range changes
- [ ] Presets: Same as US-012 (Today, Last 7/30 days, This Month, etc.)
- [ ] Custom range picker

**AC2: Report-Specific Filters**
- [ ] Each report has "Filter" button
- [ ] Filter dialog specific to report type:
  - Spending by Category: Account filter, include/exclude categories
  - Spending Trends: Category filter, account filter
  - Income vs Expense: Account filter, category filter
- [ ] Applied filters shown as chips ("Checking Account", "Groceries", "x" to remove)

**AC3: Save Report Configuration**
- [ ] "Save Report View" button
- [ ] Saves: Date range, filters, chart settings
- [ ] Saved views appear in dropdown: "My Saved Reports"
- [ ] Can rename, delete saved views

**AC4: Report Configuration Persistence**
- [ ] Last used date range persists across sessions
- [ ] Saved report configurations stored in database
- [ ] "Reset to Default" button clears all customizations

**Technical Notes:**
- Reuse saved filter infrastructure from US-015 (EPIC-002)
- Store report configurations in `saved_filters` table (expand schema)
- Emit signals when filters change, reports listen and refresh

**Dependencies:**
- ✅ US-017 (Dashboard date range selector)
- ✅ US-015 (Saved filter infrastructure from EPIC-002)
- ✅ All report types

**Definition of Done:**
- [ ] Global date range selector working
- [ ] Report-specific filter dialogs
- [ ] Save/load report configurations
- [ ] Persistence across sessions
- [ ] 8+ unit tests
- [ ] 3+ integration tests
- [ ] User Guide section

---

### **US-026: Financial Dashboard (Summary View)** 📊 **MILESTONE**

**As a** user
**I want** a financial dashboard that shows all key metrics and reports in one view
**So that** I can understand my financial health at a glance without navigating multiple pages

**Priority:** P0 (Must Have) - **Epic completion milestone**
**Story Points:** 4
**Sprint:** Sprint 21 (Week 9-10)

**Acceptance Criteria:**

**AC1: Dashboard Layout**
- [ ] Grid layout with 6 report widgets:
  - Row 1: Spending by Category (US-018), Spending Trends (US-019)
  - Row 2: Income vs Expense (US-020), Account Balances (US-021)
  - Row 3: Net Worth (US-022), Key Metrics Card
- [ ] Responsive: Adapts to window size (1-3 columns based on width)
- [ ] Each widget can be expanded to full view

**AC2: Key Metrics Card**
- [ ] Summary statistics card showing:
  - Current Month Income: $X
  - Current Month Expenses: $Y
  - Net Savings: $Z (green if positive, red if negative)
  - Savings Rate: N%
  - Total Net Worth: $X
  - Net Worth Change: +/- $Y (+/- N% vs last month)
- [ ] Large, readable numbers with visual indicators (↑↓)

**AC3: Quick Actions**
- [ ] "Add Transaction" quick button (opens transaction dialog)
- [ ] "View All Transactions" button
- [ ] "Export All Reports" button (US-023)
- [ ] Date range selector (global for all reports)

**AC4: Dashboard Customization**
- [ ] Drag-and-drop to rearrange widgets
- [ ] Hide/show individual widgets (gear icon)
- [ ] Widget size options: Small, Medium, Large
- [ ] Configuration saved per user

**Technical Notes:**
- Use QGridLayout or QSplitter for responsive layout
- Each widget is independent (can be developed/tested separately)
- Dashboard controller coordinates date range changes across all widgets

**Dependencies:**
- ✅ US-017 (Dashboard foundation)
- ✅ US-018, US-019, US-020, US-021, US-022 (All report types)

**Definition of Done:**
- [ ] Dashboard with all 6 widgets
- [ ] Key metrics card with summary stats
- [ ] Quick actions functional
- [ ] Drag-and-drop customization
- [ ] 12+ unit tests
- [ ] 5+ integration tests
- [ ] User Guide chapter on dashboard
- [ ] Demo-ready showcase

---

### **US-027: Report Performance Optimization** ⚡

**As a** user with thousands of transactions
**I want** reports to load quickly without lag
**So that** I can work efficiently without waiting for slow report generation

**Priority:** P1 (Should Have) - **Performance is critical**
**Story Points:** 3
**Sprint:** Sprint 21 (Week 9-10)

**Acceptance Criteria:**

**AC1: Performance Targets**
- [ ] Report generation: < 500ms for 10,000 transactions
- [ ] Chart rendering: < 200ms for all chart types
- [ ] Dashboard load (all reports): < 2 seconds
- [ ] Subsequent loads (cached): < 50ms

**AC2: Caching Strategy**
- [ ] Cache report data for 5 minutes (configurable)
- [ ] Cache invalidated when:
  - New transaction added/edited/deleted
  - Date range changed
  - Account reconciled
- [ ] Cache keys include date range + filters

**AC3: Async Loading**
- [ ] Reports load asynchronously (non-blocking UI)
- [ ] Loading spinner shown while generating
- [ ] Dashboard loads reports in parallel (6 async requests)
- [ ] User can interact with loaded reports while others load

**AC4: Database Optimization**
- [ ] Add indexes for common report queries:
  - `CREATE INDEX idx_transactions_category_date ON transactions(category, date)`
  - `CREATE INDEX idx_transactions_amount_date ON transactions(amount, date)`
- [ ] Use EXPLAIN QUERY PLAN to verify index usage
- [ ] Aggregate queries optimized (GROUP BY on indexed columns)

**AC5: Data Aggregation**
- [ ] Pre-aggregate common queries:
  - Daily spending totals stored in cache
  - Category totals updated on transaction save
- [ ] Background task updates aggregations (async)

**Technical Notes:**
- Use QThreadPool for async report generation
- Implement simple in-memory cache (dict with TTL)
- Consider SQLite connection pooling for parallel queries
- Profile slow queries with EXPLAIN QUERY PLAN

**Dependencies:**
- ✅ All report types (US-018 through US-026)

**Definition of Done:**
- [ ] All performance targets met
- [ ] Caching implemented and tested
- [ ] Async loading working
- [ ] Database indexes added
- [ ] 15+ performance tests (various data sizes)
- [ ] Profiling results documented
- [ ] User Guide performance tips section

---

## 🏗️ Technical Implementation

### Architecture Changes

**New Components:**
```
finance_app/
├── business/
│   ├── report_service.py           # NEW - Base report service
│   ├── spending_report_service.py  # NEW - Spending reports
│   ├── balance_report_service.py   # NEW - Balance/net worth reports
│   └── report_cache.py             # NEW - Report caching layer
│
├── data/repositories/
│   ├── report_repository.py        # NEW - Report data queries
│   └── balance_snapshot_repository.py # NEW - Historical balances
│
└── ui/
    ├── windows/
    │   └── dashboard_window.py     # NEW - Main dashboard window
    └── widgets/
        ├── chart_widgets.py        # NEW - Base chart widgets
        ├── pie_chart_widget.py     # NEW - Pie chart
        ├── line_chart_widget.py    # NEW - Line chart
        ├── bar_chart_widget.py     # NEW - Bar chart
        └── metrics_card_widget.py  # NEW - Key metrics display
```

**Estimated New Code:**
- Python: ~2,500 lines (services + repositories + widgets)
- SQL: ~100 lines (aggregation queries + indexes)
- Tests: ~1,500 lines (100+ new tests)

---

### Database Changes

**New Tables:**
```sql
-- Migration 015: Balance Snapshots (for performance)
CREATE TABLE balance_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    snapshot_date TEXT NOT NULL,  -- Daily snapshot
    balance REAL NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    UNIQUE(account_id, snapshot_date)
);

CREATE INDEX idx_balance_snapshots_account_date
    ON balance_snapshots(account_id, snapshot_date);

-- Migration 016: Report Configurations (extends saved_filters)
-- Reuses saved_filters table from US-015, add schema version
ALTER TABLE saved_filters ADD COLUMN schema_version INTEGER DEFAULT 1;
```

**New Indexes:**
```sql
-- For report performance
CREATE INDEX idx_transactions_category_date
    ON transactions(category, date);

CREATE INDEX idx_transactions_amount_date
    ON transactions(amount, date);

CREATE INDEX idx_transactions_account_date
    ON transactions(account_id, date);
```

**Estimated Migration Time:** 45 minutes (indexes) + 15 minutes (snapshots table) = 60 minutes

---

### Performance Targets

| Operation | Target | Test With |
|-----------|--------|-----------|
| Single Report Generation | < 500ms | 10K transactions |
| Chart Rendering | < 200ms | All chart types |
| Dashboard Load (6 reports) | < 2 seconds | 10K transactions |
| Cached Report Load | < 50ms | Second access |
| Balance Snapshot Query | < 100ms | 10K transactions |
| Export to PDF | < 3 seconds | Full report |
| Export to CSV | < 1 second | 10K rows |

**Performance Optimization Strategies:**
- Database indexes on all filtered/grouped columns
- In-memory caching with 5-minute TTL
- Async report generation (parallel loading)
- Pre-aggregated daily snapshots
- Lazy loading (load chart data only when widget visible)

---

## 🧪 Testing Strategy

### Test Coverage Goals

**Unit Tests:** 80+ tests
- `ReportService`: 15 tests (aggregation, date ranges)
- `SpendingReportService`: 12 tests (category breakdown)
- `BalanceReportService`: 10 tests (historical balances)
- Chart Widgets: 25 tests (rendering, interactions)
- Export Services: 8 tests (PDF/CSV generation)
- Performance Tests: 10+ tests (various data sizes)

**Integration Tests:** 30+ tests
- Report generation end-to-end: 10 tests
- Chart interaction scenarios: 8 tests
- Export workflows: 5 tests
- Dashboard integration: 7 tests

**Performance Tests:** 15+ tests
- Each report type with 1K, 10K, 50K transactions
- Dashboard load time with all reports
- Cache effectiveness tests

**Total New Tests:** 125+ tests

---

## 📊 Success Metrics & KPIs

### User Adoption Metrics

**Week 1 After Release:**
- Target: 70% of active users view at least one report
- Measure: Analytics event "report_viewed"

**Month 1 After Release:**
- Target: 50%+ view reports weekly
- Target: 30%+ view reports daily
- Target: 40%+ use dashboard as default view
- Target: 20%+ export reports (indicates serious/business use)

### User Satisfaction Metrics

**Net Promoter Score:**
- Baseline (Post-EPIC-002): ~50
- Target (Post-EPIC-003): +15 points = 65
- Measure: In-app survey 2 weeks after release

**Feature Satisfaction:**
- Survey: "How satisfied are you with the reporting features?"
- Target: 85%+ "Satisfied" or "Very Satisfied"

**Time to Insight:**
- Survey: "How quickly can you understand your financial situation?"
- Target: 80%+ say "Very quickly" or "Instantly"

### Performance Metrics

**Report Load Times:**
- P50: < 200ms
- P95: < 500ms
- P99: < 2 seconds

**Feature Stability:**
- Zero critical bugs in first month
- < 1 medium bug per week
- User-reported issues resolved within 24 hours

---

## 🚧 Risks and Mitigations

### Technical Risks

**Risk 1: Chart Library Performance**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Evaluate Qt Charts vs matplotlib early (Sprint 17 Day 1)
  - Performance test with 10K+ data points
  - Fallback to matplotlib if Qt Charts insufficient
  - Consider chart.js via web view as alternative

**Risk 2: PDF Generation Quality**
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:**
  - Test ReportLab early in Sprint 20
  - Ensure charts render as high-DPI images
  - Provide "Print to PDF" fallback (browser print)

**Risk 3: Historical Balance Calculation Complexity**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Design balance snapshot strategy in Sprint 17
  - Create comprehensive test suite (20+ tests)
  - Validate against manual calculations
  - Consider nightly background task to update snapshots

### Schedule Risks

**Risk 4: Sprint 20 Overloaded (8 points)**
- **Probability:** Medium
- **Impact:** Low
- **Mitigation:**
  - Monitor Sprint 18-19 velocity
  - US-025 (2 pts) can move to Sprint 21 if needed
  - US-023 (export) is independent, can be developed in parallel

**Risk 5: Chart Widget Development Slower Than Expected**
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:**
  - US-017 allocates 4 points for infrastructure
  - Spike task in Sprint 17 Day 1 to validate approach
  - Reuse examples from Qt Charts documentation

### User Adoption Risks

**Risk 6: Users Don't Discover Dashboard**
- **Probability:** Low
- **Impact:** High
- **Mitigation:**
  - Prominent "Reports" menu item in main window
  - Keyboard shortcut (Ctrl+R / Cmd+R)
  - First-launch tutorial highlighting dashboard
  - Release notes emphasize reporting features

**Risk 7: Reports Don't Match User Expectations**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Show mockups to users in Sprint 17 planning
  - Iterative feedback after each sprint
  - User testing session after Sprint 19
  - Flexible configuration options (US-025)

---

## 📋 Pre-EPIC Checklist

**Must Complete Before Sprint 17 Kickoff:**

**Tech Lead Tasks (4-6 hours):**
- [ ] Evaluate chart libraries (Qt Charts vs matplotlib vs chart.js)
  - Estimated: 2 hours ⚡
- [ ] Create spike task: Render simple pie chart with sample data
  - Estimated: 1 hour ⚡
- [ ] Design balance snapshot schema and update strategy
  - Estimated: 2 hours
- [ ] Review database indexes needed for report queries
  - Estimated: 1 hour

**Product Owner Tasks (6-8 hours):**
- [ ] Create detailed US-017 and US-018 story documents ✅ DONE IN THIS EPIC
- [ ] Design dashboard layout mockups (sketch or wireframe)
  - Estimated: 2 hours
- [ ] Create Sprint 17 kickoff document
  - Estimated: 2 hours
- [ ] Update EPIC_STORY_INDEX.md with EPIC-003
  - Estimated: 30 minutes ⚡
- [ ] Write Sprint 17 kickoff announcement
  - Estimated: 30 minutes ⚡
- [ ] Gather user feedback on report priorities
  - Estimated: 2 hours

**Total Estimated Time:** 10-14 hours (Tech: 4-6 hrs, PO: 6-8 hrs)
**Deadline:** Before Sprint 17 Day 1 (target: this week)

---

## 🎯 Definition of Done (EPIC-003 Complete)

### Epic-Level Acceptance

- [ ] All 7 user stories completed (35 story points)
- [ ] All acceptance criteria met for each story
- [ ] 125+ tests written and passing (unit + integration + performance)
- [ ] Code reviewed and merged to main branch
- [ ] Database migrations applied and tested (Migrations 015-016)
- [ ] User Guide updated with complete Reporting chapter
- [ ] Product Owner sign-off (acceptance testing complete)
- [ ] Demo to stakeholders completed
- [ ] Performance targets met (< 500ms reports, < 2s dashboard)
- [ ] No critical or high-priority bugs open

### Release Criteria

- [ ] All EPIC-003 code merged to `main`
- [ ] Version bumped to v2.1.0 (or v2.2.0 if EPIC-002 was v2.1.0)
- [ ] Release notes written with screenshots
- [ ] User-facing documentation published
- [ ] Performance validated on production-like data (10K+ transactions)
- [ ] No regressions in EPIC-001 or EPIC-002 features
- [ ] Export features tested (PDF and CSV)
- [ ] Chart rendering tested on multiple screen sizes
- [ ] Backup/rollback plan documented

---

## 📅 Timeline and Milestones

### Sprint 17 (Weeks 1-2) - Foundation

**Milestone 1: Reporting Infrastructure Complete**
- **Date:** End of Sprint 17
- **Deliverables:**
  - US-017: Infrastructure ✅
  - US-018: Spending by Category ✅
  - Chart framework operational
  - First visual report delivered
  - 20+ tests passing
- **Demo:** Pie chart showing spending breakdown

---

### Sprint 18 (Weeks 3-4) - Trend Analysis

**Milestone 2: Trend Reports Delivered**
- **Date:** End of Sprint 18
- **Deliverables:**
  - US-019: Spending Trends ✅
  - US-020: Income vs Expense ✅
  - 35+ total tests passing
- **Demo:** Line and bar charts with time-based analysis

---

### Sprint 19 (Weeks 5-6) - Account Analysis

**Milestone 3: Balance Reports Delivered**
- **Date:** End of Sprint 19
- **Deliverables:**
  - US-021: Account Balances ✅
  - US-022: Net Worth ✅
  - 50+ total tests passing
- **Demo:** Multi-account balance tracking, net worth trend

---

### Sprint 20 (Weeks 7-8) - Advanced Features

**Milestone 4: Export and Drill-Down Complete**
- **Date:** End of Sprint 20
- **Deliverables:**
  - US-023: Export ✅
  - US-024: Drill-Down ✅
  - US-025: Custom Filters ✅
  - 70+ total tests passing
- **Demo:** Export reports to PDF/CSV, interactive drill-down

---

### Sprint 21 (Weeks 9-10) - Dashboard & Polish

**Milestone 5: EPIC-003 Complete** 🎉
- **Date:** End of Sprint 21
- **Deliverables:**
  - US-026: Dashboard ✅
  - US-027: Performance ✅
  - 125+ total tests passing
  - Complete User Guide chapter
  - Release notes with screenshots
- **Demo:** Full dashboard showcase, performance benchmarks

---

## 👥 Stakeholders and Responsibilities

### Product Owner
- **Name:** Product Owner
- **Responsibilities:**
  - Define user stories and acceptance criteria
  - Prioritize backlog and adjust sprint plans
  - Accept/reject completed work
  - Gather user feedback on reports and charts
  - Create dashboard mockups and wireframes

### Tech Lead
- **Name:** Tech Lead
- **Responsibilities:**
  - Architecture design (chart library selection, caching strategy)
  - Code review and quality assurance
  - Performance optimization and profiling
  - Technical risk mitigation
  - Balance calculation and snapshot design

### Development Team
- **Composition:** Full Stack Team
- **Responsibilities:**
  - Implement stories (backend + frontend)
  - Write tests (unit + integration + performance)
  - Fix bugs and issues
  - Maintain code quality
  - Develop chart widgets and report services

### QA/Testing
- **Responsibilities:**
  - Acceptance testing for each report
  - Visual testing (chart rendering, layouts)
  - Performance testing (10K+ transactions)
  - Export testing (PDF/CSV quality)
  - Regression testing (EPIC-001/002 features)

---

## 📚 References

### Related Documents

**Product & Planning:**
- [Product Requirements Document](../prd.md)
- [EPIC-001: Account Management](EPIC-001-account-management.md)
- [EPIC-002: Search and Filter Transactions](EPIC-002-search-filter-transactions.md)
- [EPIC_STORY_INDEX.md](../EPIC_STORY_INDEX.md)

**Technical:**
- [Architecture Documentation](../ARCHITECTURE.md)
- [User Guide](../USER_GUIDE.md)
- [Qt Charts Documentation](https://doc.qt.io/qt-6/qtcharts-index.html)

**Templates:**
- [Epic Template](../templates/EPIC_TEMPLATE.md)
- [Story Template](../templates/STORY_TEMPLATE.md)

### External Resources

**Design Inspiration:**
- Mint.com reports and charts
- YNAB reports dashboard
- Personal Capital net worth tracker
- GnuCash balance reports

**Technical References:**
- Qt Charts Examples: https://doc.qt.io/qt-6/qtcharts-examples.html
- Matplotlib with Qt: https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html
- ReportLab PDF: https://www.reportlab.com/docs/reportlab-userguide.pdf
- Chart Design Best Practices: https://datavizcatalogue.com/

---

## 📝 Notes

### Discussion Points

**Q1: Which chart library should we use?**
- **Options:** Qt Charts (native), matplotlib (Python), chart.js (web view)
- **Decision:** Evaluate in Sprint 17 spike task (2 hours)
- **Criteria:** Performance, ease of use, interactivity, licensing
- **Recommendation:** Qt Charts if sufficient, matplotlib as fallback

**Q2: Should we pre-calculate balance snapshots or calculate on-demand?**
- **Decision:** Hybrid approach
- **Rationale:** On-demand for recent data (< 30 days), snapshots for historical (> 30 days)
- **Implementation:** Nightly background task updates snapshots

**Q3: Should dashboard be default view on app start?**
- **Decision:** Make it configurable (user preference)
- **Default:** Transaction list (current behavior)
- **Setting:** "Show dashboard on startup" checkbox in preferences

---

### Decisions Made

- **2025-11-19:** Epic created with 7 stories, 35 points, 5 sprints
- **2025-11-19:** Priority set to High (P1) for v2.1.0 release
- **2025-11-19:** Chart library evaluation required before Sprint 17
- **2025-11-19:** Balance snapshot strategy approved (hybrid on-demand/cached)

---

### Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-11-19 | Epic created | Product Owner |
| 2025-11-19 | 7 user stories defined with detailed acceptance criteria | Product Owner |
| 2025-11-19 | 5-sprint plan (Sprints 17-21) finalized | Product Owner |
| 2025-11-19 | Pre-EPIC checklist created | Product Owner + Tech Lead |

---

**Last Updated:** 2025-11-19
**Next Review:** Sprint 17 Planning Meeting (US-017, US-018)
**EPIC Status:** 📋 **PLANNED** - 0/7 stories complete (0% done)

---

## 🚀 Let's Build Amazing Reporting Features!

This epic will transform the Personal Finance Manager from a transaction management tool into a comprehensive financial insights platform. With visual reports, interactive charts, and a powerful dashboard, users will gain deep understanding of their financial health and make data-driven decisions with confidence.

**Expected Impact:**
- 80% of users can answer "Where does my money go?" in < 5 seconds
- +15 points NPS increase (compound with EPIC-002)
- 70% user adoption of reporting features
- Foundation for EPIC-004 (Budget Management)
- Key differentiator vs competitors

**Let's make financial insights beautiful and actionable!** 🎯📊
