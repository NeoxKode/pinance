# Sprint 17 Kickoff - EPIC-003 Begins! 🎬

**Sprint:** Sprint 17
**Duration:** 2 weeks (Weeks 1-2 of EPIC-003)
**Dates:** November 19, 2025 - December 3, 2025
**Epic:** [EPIC-003: Reporting and Charts](../epics/EPIC-003-reporting-and-charts.md)
**Status:** 🎬 **KICKOFF** - Sprint Planning Complete
**Team:** Full Stack Team
**Sprint Goal:** Build reporting foundation and deliver first visual report

---

## 🎯 Sprint Goal

**Primary Goal:** Establish the reporting infrastructure and deliver the first visual report to users.

**Success Criteria:**
- ✅ Reporting framework operational (services, widgets, dashboard layout)
- ✅ Spending by Category pie chart working
- ✅ Dashboard accessible from main window
- ✅ Date range selector functional
- ✅ 20+ tests passing
- ✅ User Guide section on accessing reports

---

## 📊 Sprint Metrics

| Metric | Value |
|--------|-------|
| **Story Points Committed** | 7 points |
| **Stories in Sprint** | 2 (US-017, US-018) |
| **Team Velocity (Target)** | 7 pts (based on EPIC-001 avg: 6.08 pts/sprint) |
| **Team Capacity** | 80 hours (2 weeks × 40 hours) |
| **Estimated Hours** | ~28-35 hours (7 pts × 4-5 hrs/pt) |
| **Buffer** | 45-52 hours (56-65% capacity utilization) |

---

## 📝 Sprint Backlog

### Story 1: US-017 - Reporting Infrastructure & Dashboard Layout 🏗️

**Priority:** P0 (Must Have - Foundation)
**Story Points:** 4
**Assignee:** Full Stack Team
**Estimated Hours:** 16-20 hours

**User Story:**
> As a developer building reporting features, I want a reusable reporting infrastructure with base classes and common components, so that all reports follow consistent patterns and share common functionality.

**Acceptance Criteria Summary:**
- [ ] `ReportService` base class with common operations
- [ ] Chart widget base classes (Pie, Line, Bar)
- [ ] Dashboard window with grid layout
- [ ] Date range selector at top (global for all reports)
- [ ] Common UI components (loading spinner, error/empty states)

**Tasks Breakdown:**

**Backend Tasks (8-10 hours):**
1. Create `finance_app/business/report_service.py` - Base report service (3 hours)
   - `generate_report()` method
   - `get_date_range_data()` method
   - `aggregate_by_period()` method (daily, weekly, monthly, quarterly, yearly)
   - Handle timezone and date boundary edge cases

2. Create `finance_app/data/repositories/report_repository.py` - Report queries (3 hours)
   - Query builder for aggregations
   - Date range filtering
   - Category grouping
   - Account filtering

3. Write backend unit tests (2-4 hours)
   - 10+ tests for ReportService
   - 5+ tests for ReportRepository

**Frontend Tasks (8-10 hours):**
4. Create `finance_app/ui/widgets/chart_widgets.py` - Base chart widgets (4 hours)
   - `BaseChartWidget` abstract class
   - `PieChartWidget` implementation (uses Qt Charts or matplotlib)
   - `LineChartWidget` stub (will be used in US-019)
   - `BarChartWidget` stub (will be used in US-020)
   - Common features: legend, tooltips, title, loading state

5. Create `finance_app/ui/windows/dashboard_window.py` - Dashboard (3 hours)
   - QMainWindow with grid layout (2×3 or 3×2)
   - Date range selector at top
   - "Refresh All" button
   - Placeholder cards for 6 reports

6. Write frontend unit tests (1-2 hours)
   - 5+ tests for chart widgets
   - 3+ tests for dashboard window

**Dependencies:**
- ✅ EPIC-001 complete (transaction data)
- ✅ EPIC-002 complete (date range selector from US-012)
- ⏳ Qt Charts library (check if installed, spike task Day 1)

**Story Link:** [US-017 Documentation](../stories/backlog/US-017-reporting-infrastructure.md)

---

### Story 2: US-018 - Spending by Category Report (Pie Chart) 🥧

**Priority:** P0 (Must Have - Quick Win)
**Story Points:** 3
**Assignee:** Full Stack Team
**Estimated Hours:** 12-15 hours

**User Story:**
> As a user tracking my spending, I want to see a pie chart showing my spending breakdown by category, so that I can quickly identify which categories consume most of my budget.

**Acceptance Criteria Summary:**
- [ ] Pie chart showing spending by category
- [ ] Each slice color-coded with percentage and dollar amount
- [ ] Hover tooltip: "Groceries: $1,234.56 (23.4%)"
- [ ] Double-click slice opens transactions filtered by category
- [ ] Configuration: Include income toggle, absolute values toggle
- [ ] Top 10 categories, rest grouped as "Other"

**Tasks Breakdown:**

**Backend Tasks (5-7 hours):**
1. Create `SpendingReportService` class (3 hours)
   - `get_spending_by_category(date_from, date_to)` method
   - SQL: `SELECT category, SUM(amount) FROM transactions WHERE amount < 0 GROUP BY category`
   - Handle negative amounts (expenses) vs positive (income)
   - Sort by amount descending

2. Write backend unit tests (2-4 hours)
   - 8+ tests for SpendingReportService
   - Test with various date ranges
   - Test with income/expense filtering
   - Test empty data scenarios

**Frontend Tasks (7-8 hours):**
3. Implement `SpendingByCategoryWidget` (4 hours)
   - Extends `PieChartWidget` from US-017
   - Fetch data from `SpendingReportService`
   - Render pie chart with categories
   - Color palette assignment
   - Legend display

4. Add configuration options (2 hours)
   - "Include income" checkbox
   - "Absolute values" checkbox
   - Account filter dropdown (optional for Sprint 17)

5. Implement chart interactions (2 hours)
   - Hover tooltips
   - Double-click drill-down to transactions
   - Emit signal: `category_clicked(category_name)`
   - MainWindow listens and filters transaction list

6. Write frontend unit tests (1-2 hours)
   - 5+ tests for SpendingByCategoryWidget
   - Test rendering with sample data
   - Test empty state
   - Test configuration toggles

**Integration (in US-017):**
7. Add widget to dashboard grid (already done in US-017)
8. Connect date range selector to widget refresh

**Dependencies:**
- ✅ US-017 (Chart infrastructure - must complete first)
- ✅ Categories in transactions (EPIC-001)
- ✅ Date range filtering (US-012)

**Story Link:** [US-018 Documentation](../stories/backlog/US-018-spending-by-category-report.md)

---

## 📅 Sprint Schedule

### Week 1 (Days 1-5)

**Day 1 (Mon, Nov 19) - Sprint Planning & Spike**
- Morning: Sprint planning meeting (2 hours)
- Spike task: Evaluate Qt Charts vs matplotlib (2 hours)
  - Install Qt Charts: `pip install PySide6-QtCharts` (if not already installed)
  - Create simple pie chart proof-of-concept
  - Decide on chart library for sprint
- Afternoon: Start US-017 backend (ReportService base class)

**Day 2 (Tue, Nov 20) - US-017 Backend**
- Complete ReportService implementation
- Create ReportRepository
- Write backend unit tests (10+ tests)
- Target: Backend foundation complete

**Day 3 (Wed, Nov 21) - US-017 Frontend**
- Create BaseChartWidget and PieChartWidget
- Create dashboard window with grid layout
- Integrate date range selector
- Target: Chart framework operational

**Day 4 (Thu, Nov 22) - Complete US-017**
- Write frontend unit tests (5+ tests)
- Test dashboard layout and date range selector
- Code review and fixes
- **US-017 COMPLETE ✅** (4 points)

**Day 5 (Fri, Nov 23) - Start US-018 Backend**
- Create SpendingReportService
- Implement `get_spending_by_category()` method
- Write backend unit tests (8+ tests)
- Target: Backend complete for US-018

---

### Week 2 (Days 6-10)

**Day 6 (Mon, Nov 26) - US-018 Frontend**
- Implement SpendingByCategoryWidget
- Render pie chart with sample data
- Add color palette and legend

**Day 7 (Tue, Nov 27) - US-018 Configuration**
- Add configuration checkboxes (include income, absolute values)
- Implement chart hover tooltips
- Connect to dashboard grid

**Day 8 (Wed, Nov 28) - US-018 Interactions**
- Implement double-click drill-down to transactions
- Connect signals to MainWindow
- Test transaction filtering integration

**Day 9 (Thu, Nov 29) - Testing & Polish**
- Write frontend unit tests for US-018 (5+ tests)
- Integration testing (end-to-end scenarios)
- Fix bugs and polish UI
- **US-018 COMPLETE ✅** (3 points)

**Day 10 (Fri, Nov 30) - Sprint Review & Retrospective**
- Morning: Sprint demo (1 hour)
  - Demo dashboard with spending by category report
  - Show drill-down to transactions
  - Performance metrics
- Afternoon: Sprint retrospective (1 hour)
- Update documentation (User Guide, CHANGELOG)
- Sprint 17 COMPLETE! 🎉

---

## 🧪 Testing Strategy

### Unit Tests Target: 20+ tests

**Backend (15 tests):**
- ReportService: 10 tests
  - `generate_report()` with various date ranges
  - `aggregate_by_period()` for daily/weekly/monthly
  - Edge cases (empty data, timezone boundaries)
- SpendingReportService: 5 tests
  - `get_spending_by_category()` with sample data
  - Income vs expense filtering
  - Empty data handling

**Frontend (5+ tests):**
- BaseChartWidget: 2 tests (rendering, loading state)
- PieChartWidget: 3 tests (data rendering, tooltips, empty state)
- Dashboard window: 2 tests (layout, date range selector)
- SpendingByCategoryWidget: 3 tests (rendering, configuration, interactions)

### Integration Tests: 5+ tests
- End-to-end: Generate report → Render chart → Drill down to transactions
- Date range change updates chart
- Configuration toggles update chart
- Empty data scenarios
- Large data sets (1,000+ transactions)

### Performance Tests: 2+ tests
- Report generation < 500ms for 10K transactions
- Chart rendering < 200ms

---

## 📚 Documentation Tasks

### User Guide Updates
- [ ] New chapter: "7. Reports and Charts"
- [ ] Section 7.1: Accessing the Dashboard
- [ ] Section 7.2: Understanding Reports
- [ ] Section 7.3: Spending by Category Report
- [ ] Screenshots of dashboard and pie chart
- [ ] Estimated: 2 hours

### CHANGELOG.md Update
- [ ] Sprint 17 section
- [ ] US-017 and US-018 entries
- [ ] Breaking changes (if any)
- [ ] Estimated: 30 minutes

### Architecture Documentation
- [ ] Update ARCHITECTURE.md with reporting components
- [ ] Add section on ReportService and chart widgets
- [ ] Diagram of reporting architecture
- [ ] Estimated: 1 hour

---

## ⚠️ Risks and Mitigations

### Risk 1: Qt Charts Performance or Availability
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Spike task on Day 1 to evaluate library
  - If Qt Charts insufficient, fallback to matplotlib
  - Budget 2 hours for library evaluation
- **Status:** 🔍 To be evaluated Day 1

### Risk 2: Chart Rendering Complexity
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:**
  - Use Qt Charts examples as starting point
  - Keep first chart simple (pie chart is easiest)
  - Defer advanced features to future sprints
- **Status:** ⚠️ Monitor during implementation

### Risk 3: Integration with Existing UI
- **Probability:** Low
- **Impact:** Low
- **Mitigation:**
  - Dashboard is separate window, minimal impact on existing UI
  - Reuse date range selector from US-012
  - Test on multiple screen sizes
- **Status:** ✅ Low risk

---

## 🎯 Definition of Done

**Story-Level DoD (US-017, US-018):**
- [ ] All acceptance criteria met
- [ ] Code written and committed
- [ ] Unit tests written and passing (20+ total)
- [ ] Integration tests written and passing (5+ total)
- [ ] Code reviewed by Tech Lead
- [ ] No critical or high-priority bugs
- [ ] Performance targets met (< 500ms, < 200ms)
- [ ] User Guide updated

**Sprint-Level DoD:**
- [ ] Both stories (US-017, US-018) complete
- [ ] 7 story points delivered
- [ ] All tests passing (25+ total)
- [ ] Dashboard accessible from main window
- [ ] Spending by category report functional
- [ ] Demo completed and approved by Product Owner
- [ ] CHANGELOG.md updated
- [ ] No regressions in EPIC-001/002 features

---

## 📊 Success Metrics

### Sprint Completion
- **Target:** 7/7 story points completed
- **Measure:** US-017 ✅ + US-018 ✅

### Code Quality
- **Target:** 80%+ test coverage on new code
- **Measure:** pytest-cov report
- **Target:** Zero critical bugs
- **Measure:** Bug tracker

### Performance
- **Target:** Report generation < 500ms for 10K transactions
- **Measure:** Performance test results
- **Target:** Chart rendering < 200ms
- **Measure:** Profiling with 1K+ data points

### User Satisfaction (Post-Sprint Survey)
- **Question:** "Are you excited about the new reporting features?"
- **Target:** 80%+ respond "Yes" or "Very excited"

---

## 👥 Team and Responsibilities

### Full Stack Team
**Members:** Full Stack Development Team
**Responsibilities:**
- Implement US-017 (Infrastructure)
- Implement US-018 (Category Report)
- Write tests (unit + integration)
- Code reviews
- Documentation updates

### Product Owner
**Responsibilities:**
- Clarify requirements as needed
- Accept/reject completed stories
- Sprint demo preparation
- Gather user feedback

### Tech Lead
**Responsibilities:**
- Chart library spike task (Day 1)
- Architecture guidance
- Code review for US-017 and US-018
- Performance validation

---

## 📋 Pre-Sprint Checklist ✅

**Before Sprint Starts (Day 1 Morning):**
- [x] EPIC-003 created and documented ✅
- [x] US-017 and US-018 stories detailed ✅
- [x] Sprint 17 kickoff document created ✅
- [x] EPIC_STORY_INDEX.md updated ✅
- [ ] Team briefed on sprint goal (Day 1 morning)
- [ ] Chart library evaluation spike planned (Day 1 afternoon)
- [ ] Development environment ready (Qt Charts dependency)

**All Prerequisites Met:** 80% complete (4/5 tasks)

---

## 🚀 Sprint Kickoff Agenda

**Date:** November 19, 2025 (Day 1 Morning)
**Duration:** 2 hours
**Location:** Team Meeting Room

**Agenda:**

1. **Welcome and Sprint Overview** (15 min)
   - Celebrate EPIC-002 completion! 🎉
   - Introduce EPIC-003: Reporting and Charts
   - Sprint 17 goal and deliverables

2. **EPIC-003 Walkthrough** (30 min)
   - Review epic vision and business value
   - Overview of all 7 stories (35 points, 5 sprints)
   - Focus on Sprint 17: US-017 + US-018

3. **Story Deep Dive** (45 min)
   - US-017: Reporting Infrastructure (4 pts)
     - Acceptance criteria review
     - Task breakdown
     - Technical approach
   - US-018: Spending by Category (3 pts)
     - Acceptance criteria review
     - Task breakdown
     - Chart design discussion

4. **Sprint Planning** (20 min)
   - Review sprint schedule (10-day plan)
   - Identify dependencies and blockers
   - Assign initial tasks
   - Q&A

5. **Spike Task Planning** (10 min)
   - Chart library evaluation (Qt Charts vs matplotlib)
   - Success criteria for spike
   - Time-box: 2 hours

**Action Items:**
- Team: Complete spike task by Day 1 EOD
- Tech Lead: Provide chart library recommendation
- Product Owner: Prepare dashboard mockups for reference

---

## 📝 Sprint Retrospective (End of Sprint)

**Questions to Answer:**

### What Went Well?
- (To be filled after sprint)

### What Could Be Improved?
- (To be filled after sprint)

### Action Items for Next Sprint
- (To be filled after sprint)

### Velocity Analysis
- **Planned:** 7 story points
- **Completed:** ___ story points
- **Velocity:** ___ pts/sprint
- **Comparison to EPIC-001 avg (6.08 pts/sprint):** ___
- **Comparison to EPIC-002 avg (4.5 pts/sprint):** ___

---

## 🎬 Let's Build Amazing Reports!

Sprint 17 marks the beginning of EPIC-003, where we'll transform transaction data into beautiful, actionable insights. This sprint focuses on laying a solid foundation with reusable infrastructure and delivering our first visual report.

**Key Milestones:**
- ✅ EPIC-003 planned and documented
- 🎬 Sprint 17 kickoff (US-017 + US-018)
- 🎯 First visual report delivered (Pie Chart)
- 🏗️ Reporting framework operational

**Expected Impact:**
- Users gain visual insight into spending patterns
- Foundation for 6+ more report types
- Step toward comprehensive financial dashboard
- Path to v2.1.0 release

**Let's make Sprint 17 a success!** 🚀📊

---

**Document Status:** ✅ Complete - Ready for Sprint Kickoff
**Last Updated:** November 19, 2025
**Next Update:** Sprint 17 Retrospective (December 3, 2025)
