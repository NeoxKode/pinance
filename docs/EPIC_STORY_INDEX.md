# Epic and Story Index

**Last Updated:** 2025-10-21
**Project:** Personal Finance Manager v2.0

---

## Quick Stats

| Metric | Count |
|--------|-------|
| **Total Epics** | 1 |
| **Total Stories** | 1 |
| **Stories in Backlog** | 1 |
| **Stories in Progress** | 0 |
| **Stories Completed** | 0 |
| **Total Story Points** | 3 |
| **Points Completed** | 0 |

---

## Epics Overview

### Active Epics

| ID | Epic | Priority | Status | Stories | Points | Target Release |
|----|------|----------|--------|---------|--------|----------------|
| [EPIC-001](epics/EPIC-001-search-filter-transactions.md) | Search and Filter Transactions | High | Ready | 1/6 | 3/21 | v2.1.0 |

### Planned Epics (Not Yet Created)

| ID | Epic | Priority | Target Release |
|----|------|----------|----------------|
| EPIC-002 | Reporting and Charts | High | v2.1.0 |
| EPIC-003 | Budget Management | Medium | v2.2.0 |
| EPIC-004 | Recurring Transactions | Medium | v2.2.0 |
| EPIC-005 | Multi-Currency Support | Low | v2.3.0 |
| EPIC-006 | Import/Export | Medium | v2.2.0 |
| EPIC-007 | Cloud Backup | Low | v2.3.0 |

---

## Stories by Status

### 📋 Backlog (1)

| ID | Story | Epic | Priority | Points | Assignee |
|----|-------|------|----------|--------|----------|
| [STORY-001](stories/backlog/STORY-001-basic-text-search.md) | Basic Text Search | EPIC-001 | High | 3 | Unassigned |

### 🚧 In Progress (0)

| ID | Story | Epic | Priority | Points | Assignee | Started |
|----|-------|------|----------|--------|----------|---------|
| - | - | - | - | - | - | - |

### ✅ Completed (0)

| ID | Story | Epic | Points | Completed | Developer |
|----|-------|------|--------|-----------|-----------|
| - | - | - | - | - | - |

---

## Stories by Epic

### EPIC-001: Search and Filter Transactions (1/6 stories)

| ID | Story | Status | Points | Assignee |
|----|-------|--------|--------|----------|
| [STORY-001](stories/backlog/STORY-001-basic-text-search.md) | Basic Text Search | Backlog | 3 | Unassigned |
| STORY-002 | Date Range Filter | Not Created | 3 | - |
| STORY-003 | Category Filter | Not Created | 3 | - |
| STORY-004 | Amount Range Filter | Not Created | 4 | - |
| STORY-005 | Combined Filters | Not Created | 5 | - |
| STORY-006 | Filter UI Panel | Not Created | 3 | - |

**Progress:** 0% (0/21 points completed)

---

## Roadmap

### v2.1.0 (Target: Q4 2025)

**Focus:** Search, Filters, and Reporting

- [ ] EPIC-001: Search and Filter Transactions (21 pts)
- [ ] EPIC-002: Reporting and Charts (TBD)
- **Total:** ~40-50 story points

### v2.2.0 (Target: Q1 2026)

**Focus:** Advanced Features

- [ ] EPIC-003: Budget Management (TBD)
- [ ] EPIC-004: Recurring Transactions (TBD)
- [ ] EPIC-006: Import/Export (TBD)
- **Total:** ~60-80 story points

### v2.3.0 (Target: Q2 2026)

**Focus:** Cloud and Mobile

- [ ] EPIC-005: Multi-Currency Support (TBD)
- [ ] EPIC-007: Cloud Backup (TBD)
- [ ] EPIC-008: Mobile App (TBD)
- **Total:** ~80-100 story points

---

## Velocity Tracking

### Sprint History

| Sprint | Dates | Planned | Completed | Velocity |
|--------|-------|---------|-----------|----------|
| Sprint 1 | TBD | TBD | TBD | TBD |

**Average Velocity:** TBD (need 3+ sprints)

---

## Priority Distribution

```
Critical: 0 stories (0%)
High:     1 story  (100%)
Medium:   0 stories (0%)
Low:      0 stories (0%)
```

---

## Story Points Distribution

| Range | Count | Percentage |
|-------|-------|------------|
| 1-2 points | 0 | 0% |
| 3-5 points | 1 | 100% |
| 8+ points | 0 | 0% |

**Average:** 3.0 points per story

---

## Developer Assignments

| Developer | Active Stories | Total Points |
|-----------|----------------|--------------|
| Unassigned | 1 | 3 |

---

## Recent Activity

| Date | Activity | Story/Epic |
|------|----------|------------|
| 2025-10-21 | Created EPIC-001 | Search and Filter Transactions |
| 2025-10-21 | Created STORY-001 | Basic Text Search |

---

## Blockers and Risks

### Current Blockers
- None

### Risks
- **Resource availability:** Need developers to pick up stories
- **Technical complexity:** Search performance needs validation

---

## How to Use This Index

### For Product Owners
1. Review epic progress regularly
2. Create new stories as needed
3. Update priorities based on business needs
4. Track velocity for future planning

### For Developers
1. Check "Backlog" section for available work
2. Pick highest priority story you can work on
3. Update this index when you change story status
4. Report blockers in "Blockers and Risks" section

### For Tech Leads
1. Review story distribution and assignments
2. Ensure stories have technical details filled in
3. Monitor velocity for capacity planning
4. Help resolve blockers

---

## Maintenance

### Update Frequency
- **Daily:** Update in-progress stories
- **Weekly:** Update backlog priorities
- **Sprint End:** Update velocity and completed stories

### Who Updates
- Product Owner: Epic status, priorities, new stories
- Developers: Story status, assignments, progress
- Tech Lead: Technical details, velocity, blockers

---

## Templates and Resources

- [Epic Template](templates/EPIC_TEMPLATE.md)
- [Story Template](templates/STORY_TEMPLATE.md)
- [Workflow Guide](WORKFLOW_GUIDE.md)
- [Example Epic](epics/EPIC-001-search-filter-transactions.md)
- [Example Story](stories/backlog/STORY-001-basic-text-search.md)

---

## Commands for Quick Updates

### Create new story
```bash
cp docs/templates/STORY_TEMPLATE.md docs/stories/backlog/STORY-XXX-name.md
# Edit file, then:
git add docs/stories/backlog/STORY-XXX-name.md
git commit -m "feat: Add STORY-XXX [story name]"
```

### Move story to in-progress
```bash
git mv docs/stories/backlog/STORY-XXX.md docs/stories/in-progress/
git commit -m "chore: Start work on STORY-XXX"
```

### Complete story
```bash
git mv docs/stories/in-progress/STORY-XXX.md docs/stories/completed/
git commit -m "chore: Complete STORY-XXX"
```

---

**Maintained by:** Product Owner and Development Team
**Format:** Markdown
**Sync:** Update after any story/epic changes
