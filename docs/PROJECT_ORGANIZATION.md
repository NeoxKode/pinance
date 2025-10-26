# Project Organization Guide

**Last Updated:** October 26, 2025
**Status:** Current and Maintained

This document describes the organization of documentation and artifacts in the Personal Finance Manager project.

---

## 📁 Root Directory Structure

The root directory contains only essential project files:

```
pinance/
├── CHANGELOG.md              # Project changelog (all sprints)
├── README.md                 # Project overview and setup
├── main.py                   # Application entry point
├── finance_app.py           # Symlink to main.py
├── requirements.txt         # Python dependencies
├── pytest.ini              # Test configuration
├── .gitignore              # Git ignore rules
├── finance_app/            # Main application code
├── docs/                   # All documentation (see below)
└── scripts/                # Utility scripts
```

**Philosophy:** Keep the root directory clean with only essential configuration and entry points. All documentation lives in `docs/`.

---

## 📚 Documentation Structure

All project documentation is organized in the `docs/` folder:

### Core Documentation

**Location:** `docs/`

| File | Purpose |
|------|---------|
| `ARCHITECTURE.md` | System architecture and design decisions |
| `USER_GUIDE.md` | End-user documentation (780+ lines) |
| `GETTING-STARTED.md` | Developer setup guide |
| `QUICK_START.md` | Quick start for developers |
| `TECHNICAL_DESIGN.md` | Technical design specifications |
| `WORKFLOW_GUIDE.md` | Development workflow and processes |
| `PROJECT-STATUS.md` | Current project status |
| `REFACTORING_SUMMARY.md` | Historical refactoring documentation |
| `INDEX.md` | Documentation index |
| `EPIC_STORY_INDEX.md` | Epic and story index |
| `MCP_INTEGRATION.md` | MCP integration documentation |

### Epics

**Location:** `docs/epics/`

Contains epic definitions describing major feature areas:
- `epic-01-account-management.md` - Account Management & Double-Entry Foundation
- Additional epics as project grows

**Purpose:** High-level feature planning and requirements definition.

### Stories

**Location:** `docs/stories/`

Organized into three folders:

#### 1. Backlog (`docs/stories/backlog/`)
- Stories ready to be worked on
- Prioritized by Product Owner
- Includes detailed acceptance criteria

#### 2. In Progress (`docs/stories/in-progress/`)
- Stories currently being developed
- Moved here when development starts
- Updated with progress notes

#### 3. Completed (`docs/stories/completed/`)
- Finished and accepted stories
- Includes Product Owner acceptance
- Serves as historical reference

**Current Completed Stories:**
1. US-001: Account Type Taxonomy
2. US-002A: Journal Entry Foundation
3. US-002B: Balanced Transaction Groups
4. US-002C: Split Transactions
5. US-003: Normal Balance Calculation
6. US-004: Account Reconciliation
7. US-005: Opening Balance Equity ⭐

### Sprints

**Location:** `docs/sprints/`

Sprint-specific documentation and retrospectives:

| File Pattern | Purpose |
|--------------|---------|
| `SPRINT-XX-PLAN.md` | Sprint planning documents |
| `SPRINT-XX-COMPLETION-SUMMARY.md` | Sprint completion reports |
| `SPRINT-XX-RETROSPECTIVE.md` | Sprint retrospectives |
| `SPRINT-XX-USXXX-*.md` | Story-specific sprint artifacts |
| `PRODUCT-OWNER-SUMMARY.md` | PO summaries across sprints |

**Sprint 7 (Latest) Artifacts:**
- `SPRINT-07-PLANNING-MEETING.md` - Sprint kickoff
- `SPRINT-07-US005-FINAL-COMPLETION.md` - US-005 completion summary
- `SPRINT-07-BUGFIX-SUMMARY.md` - Bug fixes applied
- `SPRINT-07-UNIT-TEST-BUGFIX.md` - Test mocking fixes

### Testing

**Location:** `docs/testing/`

Test reports and verification documents:

**US-004 (Reconciliation):**
- `RECONCILIATION_MANUAL_TEST_CHECKLIST.md`
- `US-004-ACCEPTANCE-CRITERIA-VERIFICATION.md`
- `US-004-FINAL-INTEGRATION-VERIFICATION.md`
- `US-004-MANUAL-UI-TESTING-CHECKLIST.md`

**US-005 (Opening Balance):**
- `US-005-MANUAL-TEST-REPORT.md` - 6 test cases, 100% passing

**Purpose:** Comprehensive test documentation for manual verification, acceptance testing, and quality assurance.

### Tech Reviews

**Location:** `docs/tech-reviews/`

Technical reviews and analysis documents:

**US-005 Reviews:**
- `US-005-TECH-LEAD-REVIEW.md` - Tech Lead code review (4.9/5.0)
- `US-005-GAP-ANALYSIS.md` - Gap analysis vs. US-002B
- `US-005-IMPLEMENTATION-GUIDE.md` - Implementation guidance

**Purpose:** Technical oversight, code reviews, and implementation guidance.

### Templates

**Location:** `docs/templates/`

Reusable templates for creating new artifacts:
- Story templates
- Epic templates
- Sprint planning templates

**Purpose:** Consistency and standardization across documentation.

### Archive

**Location:** `docs/archive/`

Historical documentation that's no longer actively used but preserved for context:
- `BUGFIXES.md` - Early bugfixes (Oct 22)
- `COMPLETION_REPORT.md` - Initial refactoring report (Oct 21)
- `EPIC_STORY_SYSTEM_SUMMARY.md` - Epic/story system setup (Oct 21)
- `RUN-PROTOTYPE.md` - Early prototype documentation

**Philosophy:** Don't delete historical context; archive it for future reference.

---

## 🎯 US-005 Documentation Map

For the recently completed US-005 Opening Balance Equity, here's where to find all artifacts:

### Story Documentation
- **Main Story:** `docs/stories/completed/US-005-opening-balance-equity.md` (104KB)
  - Complete story with Product Owner acceptance
  - All acceptance criteria verified
  - Quality metrics and final status

### Sprint Documentation
- **Final Completion:** `docs/sprints/SPRINT-07-US005-FINAL-COMPLETION.md`
  - Comprehensive 630-line completion summary
  - All deliverables documented
  - Innovations and achievements
- **Sprint Planning:** `docs/sprints/SPRINT-07-PLANNING-MEETING.md`
- **Bug Fixes:** `docs/sprints/SPRINT-07-BUGFIX-SUMMARY.md`
- **Unit Test Fixes:** `docs/sprints/SPRINT-07-UNIT-TEST-BUGFIX.md`

### Testing Documentation
- **Manual Testing:** `docs/testing/US-005-MANUAL-TEST-REPORT.md`
  - 6 test cases, 100% passing
  - Visual verification with screenshots
  - Bug fix verification

### Technical Reviews
- **Tech Lead Review:** `docs/tech-reviews/US-005-TECH-LEAD-REVIEW.md` (4.9/5.0)
- **Gap Analysis:** `docs/tech-reviews/US-005-GAP-ANALYSIS.md`
- **Implementation Guide:** `docs/tech-reviews/US-005-IMPLEMENTATION-GUIDE.md`

### Pull Request
- **PR Description:** `docs/stories/completed/US-005-PR-DESCRIPTION.md`
  - Comprehensive implementation summary
  - Features delivered
  - Review checklist

### User Documentation
- **User Guide Section:** `docs/USER_GUIDE.md` (lines 800-1580)
  - "Setting Up Opening Balances" (780 lines)
  - Step-by-step instructions
  - FAQ and troubleshooting

---

## 📊 Documentation by Purpose

### For Future Developers

**Where to start:**
1. `docs/GETTING-STARTED.md` - Developer setup
2. `docs/ARCHITECTURE.md` - System architecture
3. `docs/WORKFLOW_GUIDE.md` - Development workflow
4. `docs/EPIC_STORY_INDEX.md` - Feature overview

**Implementing a new story:**
1. Review epic in `docs/epics/`
2. Check story in `docs/stories/backlog/`
3. Review similar completed stories in `docs/stories/completed/`
4. Follow patterns from previous sprints in `docs/sprints/`

**Understanding existing features:**
1. Check completed stories in `docs/stories/completed/`
2. Review test documentation in `docs/testing/`
3. Read tech reviews in `docs/tech-reviews/`
4. Check sprint completion summaries in `docs/sprints/`

### For Product Owners

**Planning:**
- `docs/epics/` - Epic definitions
- `docs/stories/backlog/` - Available stories
- `docs/sprints/SPRINT-XX-PLAN.md` - Sprint planning documents

**Review and Acceptance:**
- `docs/stories/completed/` - Completed stories with PO acceptance
- `docs/sprints/SPRINT-XX-COMPLETION-SUMMARY.md` - Sprint completions
- `docs/testing/` - Test verification reports

**Status Tracking:**
- `docs/PROJECT-STATUS.md` - Current project status
- `docs/EPIC_STORY_INDEX.md` - Story progress index

### For End Users

**User Documentation:**
- `docs/USER_GUIDE.md` - Comprehensive user guide
- `docs/QUICK_START.md` - Quick start guide
- `docs/GETTING-STARTED.md` - Setup instructions

### For Technical Reviewers

**Code Review:**
- `docs/tech-reviews/` - Technical review documents
- `docs/ARCHITECTURE.md` - Architecture and design patterns
- `docs/TECHNICAL_DESIGN.md` - Technical specifications

**Quality Assurance:**
- `docs/testing/` - Test reports and verification
- `docs/sprints/SPRINT-XX-BUGFIX-*.md` - Bug fix documentation

---

## 🔄 Maintenance Guidelines

### When Creating New Documentation

1. **Choose the right location:**
   - Story documentation → `docs/stories/`
   - Sprint artifacts → `docs/sprints/`
   - Test reports → `docs/testing/`
   - Tech reviews → `docs/tech-reviews/`
   - General docs → `docs/`

2. **Use clear naming conventions:**
   - Stories: `US-XXX-story-name.md`
   - Sprints: `SPRINT-XX-description.md`
   - Testing: `US-XXX-test-type.md`

3. **Update indexes:**
   - Add to `docs/EPIC_STORY_INDEX.md`
   - Update `docs/INDEX.md` if needed
   - Update this file (`PROJECT_ORGANIZATION.md`)

### When Completing a Sprint

1. Move active stories from `in-progress/` to `completed/`
2. Create `SPRINT-XX-COMPLETION-SUMMARY.md` in `docs/sprints/`
3. Move test reports to `docs/testing/`
4. Archive interim documents to `docs/archive/` if not needed
5. Update `CHANGELOG.md` in root
6. Update project status documents

### When Archiving Documentation

**Archive when:**
- Documentation is outdated but historically valuable
- Documentation has been superseded by newer versions
- Documentation is no longer actively referenced

**Don't archive:**
- Completed story documentation (goes in `completed/`)
- Test reports (keep in `testing/`)
- Current sprint documentation
- User-facing documentation

**How to archive:**
1. Move to `docs/archive/`
2. Add brief note at top explaining why archived
3. Update indexes to point to newer versions

---

## 📈 Benefits of This Organization

### Clarity
- Clear separation of concerns
- Easy to find relevant documentation
- Consistent structure across sprints

### Maintainability
- Historical context preserved
- Easy to update and extend
- Clear patterns for new documentation

### Collaboration
- Product Owners know where to find stories
- Developers know where to find technical docs
- Testers know where to find test documentation

### Traceability
- Complete audit trail for each feature
- Easy to track sprint progress
- Clear acceptance criteria and verification

---

## 🚀 Quick Reference

**I want to...**

- **Start a new story** → Check `docs/stories/backlog/` and `docs/epics/`
- **Review completed work** → Check `docs/stories/completed/` and `docs/sprints/`
- **Learn the architecture** → Read `docs/ARCHITECTURE.md`
- **Set up the project** → Follow `docs/GETTING-STARTED.md`
- **Test a feature** → Check `docs/testing/` and `docs/USER_GUIDE.md`
- **Review code quality** → Check `docs/tech-reviews/`
- **Track sprint progress** → Check `docs/sprints/` and `docs/PROJECT-STATUS.md`
- **Find old documentation** → Check `docs/archive/`

---

**Maintained by:** Development Team
**Review Frequency:** Updated at end of each sprint
**Next Review:** End of Sprint 8

---

*This organization structure ensures all project artifacts are properly preserved, organized, and accessible for future development, maintenance, and reference.*
