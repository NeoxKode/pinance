# Epic and Story Workflow Guide

**Version:** 1.0
**Last Updated:** 2025-10-21
**Purpose:** Guide for Product Owners and Developers

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Workflow for Product Owners](#workflow-for-product-owners)
4. [Workflow for Developers](#workflow-for-developers)
5. [Story Lifecycle](#story-lifecycle)
6. [Best Practices](#best-practices)
7. [Templates and Examples](#templates-and-examples)

---

## Overview

This document describes the workflow for managing epics and user stories in the Personal Finance Manager project. We use a simple, file-based system that integrates well with Git and enables clear tracking of features from conception to completion.

### Key Concepts

- **Epic:** A large feature or initiative that spans multiple user stories (e.g., "Search and Filter Transactions")
- **User Story:** A small, implementable piece of functionality from the user's perspective (e.g., "As a user, I want to search transactions by description")
- **Acceptance Criteria:** Specific, testable conditions that must be met for a story to be considered complete

### Naming Standards

**Epic Naming Convention:**
- Format: `EPIC-XXX-descriptive-name.md` (e.g., `EPIC-001-account-management.md`)
- Sequential numbering: EPIC-001, EPIC-002, EPIC-003, etc.
- Use three-digit numbers with leading zeros
- Descriptive kebab-case names

**Story Naming Convention:**
- Format: `US-XXX-descriptive-name.md` or `STORY-XXX-descriptive-name.md`
- US-XXX: Stories that are part of the original project scope
- STORY-XXX: Stories added later or from new epics
- Sequential numbering within each prefix

**Examples:**
```
docs/epics/EPIC-001-account-management.md
docs/epics/EPIC-002-search-filter-transactions.md
docs/stories/completed/US-001-account-type-taxonomy.md
docs/stories/backlog/STORY-001-basic-text-search.md
```

---

## Directory Structure

```
docs/
├── epics/                          # All epic definitions
│   ├── EPIC-001-search-filter.md
│   ├── EPIC-002-reporting.md
│   └── EPIC-003-budgets.md
│
├── stories/                        # All user stories
│   ├── backlog/                    # Stories ready to be worked on
│   │   ├── STORY-001-basic-search.md
│   │   ├── STORY-002-date-filter.md
│   │   └── STORY-003-category-filter.md
│   ├── in-progress/                # Stories currently being developed
│   │   └── STORY-004-amount-filter.md
│   └── completed/                  # Finished stories (archived)
│       └── STORY-000-example.md
│
└── templates/                      # Templates for creating new items
    ├── EPIC_TEMPLATE.md
    └── STORY_TEMPLATE.md
```

---

## Workflow for Product Owners

### 1. Creating a New Epic

**When to create an epic:**
- You have a large feature that will take 2+ weeks
- The feature can be broken down into multiple user stories
- Multiple developers may work on different parts

**Steps:**

1. **Copy the template**
   ```bash
   cp docs/templates/EPIC_TEMPLATE.md docs/epics/EPIC-XXX-name.md
   ```

2. **Fill in the epic details**
   - **Epic ID:** Sequential number (EPIC-001, EPIC-002, etc.)
   - **Overview:** What problem does this solve?
   - **Business Value:** Why is this important?
   - **Success Criteria:** How do we measure success?
   - **Scope:** What's in/out of scope?
   - **Timeline:** Rough estimates
   - **Stakeholders:** Who's involved?

3. **Break down into user stories**
   - List all the user stories needed to complete the epic
   - Estimate story count (aim for 3-8 stories per epic)
   - Link to story files (even if not yet created)

4. **Review with stakeholders**
   - Tech Lead: Technical feasibility
   - UX Designer: User experience
   - Development Team: Effort estimation

5. **Set priority and target release**
   - Critical, High, Medium, or Low
   - Target version or date

**Example:**
See [EPIC-001: Search and Filter Transactions](epics/EPIC-001-search-filter-transactions.md)

---

### 2. Creating User Stories

**When to create a story:**
- You've defined an epic and need to break it down
- You have a small, standalone feature request
- A developer needs clarity on requirements

**Steps:**

1. **Copy the template**
   ```bash
   cp docs/templates/STORY_TEMPLATE.md docs/stories/backlog/STORY-XXX-name.md
   ```

2. **Write the user story**
   - **Format:** "As a [user], I want [goal], so that [benefit]"
   - **Example:** "As a user, I want to search transactions by description, so that I can quickly find specific purchases"

3. **Define acceptance criteria**
   - Use "Given/When/Then" format
   - Be specific and testable
   - Include non-functional requirements (performance, security)

4. **Add technical context**
   - Work with Tech Lead to fill in technical details
   - List affected components
   - Identify dependencies

5. **Estimate story points**
   - Work with development team
   - Use fibonacci sequence (1, 2, 3, 5, 8, 13)
   - Consider complexity and risk

6. **Prioritize**
   - Set priority (Critical, High, Medium, Low)
   - Order backlog based on business value
   - Consider dependencies

**Example:**
See [STORY-001: Basic Text Search](stories/backlog/STORY-001-basic-text-search.md)

---

### 3. Managing the Backlog

**Weekly backlog grooming:**

1. **Review epic progress**
   - Update story counts in epics
   - Check if epics are on track
   - Adjust priorities as needed

2. **Refine upcoming stories**
   - Ensure stories in backlog are "Ready"
   - Verify acceptance criteria are clear
   - Confirm technical details with team

3. **Prioritize stories**
   - Order stories by business value
   - Consider dependencies
   - Balance new features vs tech debt

4. **Update roadmap**
   - Adjust target releases
   - Communicate changes to stakeholders

---

### 4. Story Acceptance

**When a developer marks a story as "Ready for Review":**

1. **Review implementation**
   - Run the application
   - Test all acceptance criteria
   - Check for edge cases

2. **Provide feedback**
   - Add comments to story file
   - Request changes if needed
   - Suggest improvements

3. **Accept or reject**
   - If all criteria met: Move to `completed/` and update epic
   - If issues found: Move back to `in-progress/` with feedback

4. **Update metrics**
   - Mark story as complete in epic
   - Update story points completed
   - Track velocity for planning

---

## Workflow for Developers

### 1. Picking Up a Story

**Choosing what to work on:**

1. **Check backlog**
   ```bash
   ls docs/stories/backlog/
   ```

2. **Select a story**
   - Choose highest priority story you're qualified for
   - Check dependencies are completed
   - Verify you understand requirements

3. **Assign yourself**
   - Update `Assignee` field in story file
   - Change `Status` to "In Progress"

4. **Move the file**
   ```bash
   git mv docs/stories/backlog/STORY-XXX.md docs/stories/in-progress/
   git commit -m "chore: Assign STORY-XXX to [your name]"
   ```

---

### 2. Implementing the Story

**Development workflow:**

1. **Create feature branch**
   ```bash
   git checkout -b feature/STORY-XXX-short-description
   ```

2. **Review technical details**
   - Read "Technical Details" section carefully
   - Review "Implementation Approach"
   - Check "Affected Components"
   - Ask questions if anything is unclear

3. **Follow the implementation checklist**
   - Check off items as you complete them
   - Update story file with progress

4. **Write code**
   - Follow the project coding standards
   - Add type hints to all functions
   - Write docstrings for public methods
   - Add logging for important operations
   - Handle errors properly

5. **Write tests**
   - Unit tests for business logic
   - Integration tests for layer interactions
   - Aim for >80% coverage
   - Test edge cases and error scenarios

6. **Update documentation**
   - Update docstrings
   - Update ARCHITECTURE.md if needed
   - Update QUICK_START.md with new features

7. **Commit regularly**
   ```bash
   git add .
   git commit -m "feat(STORY-XXX): Implement basic search functionality"
   ```

---

### 3. Testing Your Work

**Before requesting review:**

1. **Run all tests**
   ```bash
   pytest finance_app/tests/
   ```

2. **Check code coverage**
   ```bash
   pytest --cov=finance_app --cov-report=html
   ```

3. **Manual testing**
   - Test all acceptance criteria
   - Test edge cases
   - Test error scenarios
   - Test on different data sets

4. **Performance testing**
   - Check if performance criteria are met
   - Profile if needed
   - Optimize bottlenecks

5. **Update story file**
   - Check off all acceptance criteria
   - Add test results
   - Note any issues or deviations

---

### 4. Creating a Pull Request

**Ready for review:**

1. **Update story status**
   - Change `Status` to "Review"
   - Add activity log entry

2. **Create pull request**
   ```bash
   git push origin feature/STORY-XXX-short-description
   gh pr create --title "feat: [STORY-XXX] Story title" \
                --body "$(cat <<EOF
   ## Story
   [STORY-XXX: Story Title](link-to-story)

   ## Changes
   - Implemented [feature]
   - Added tests for [feature]
   - Updated documentation

   ## Testing
   - [ ] All tests passing
   - [ ] Manual testing completed
   - [ ] Performance criteria met

   ## Screenshots/Demo
   [Add screenshots or GIF here]

   ## Checklist
   - [ ] Code follows project standards
   - [ ] Tests written and passing
   - [ ] Documentation updated
   - [ ] Acceptance criteria met
   EOF
   )"
   ```

3. **Request review**
   - Assign to Tech Lead
   - Notify Product Owner for acceptance testing

---

### 5. Completing a Story

**After approval:**

1. **Merge pull request**
   ```bash
   gh pr merge --squash
   ```

2. **Update story**
   - Change `Status` to "Done"
   - Add completion date to activity log

3. **Move story file**
   ```bash
   git mv docs/stories/in-progress/STORY-XXX.md docs/stories/completed/
   git commit -m "chore: Complete STORY-XXX"
   ```

4. **Update epic**
   - Check off story in epic's story list
   - Update story counts
   - Update story points completed

5. **Deploy**
   - Deploy to staging for PO testing
   - After PO approval, deploy to production

---

## Story Lifecycle

```
┌─────────────┐
│   Backlog   │  PO creates story, defines requirements
└──────┬──────┘
       │
       │ Developer picks up story
       ↓
┌─────────────┐
│ In Progress │  Development, testing, documentation
└──────┬──────┘
       │
       │ PR created and approved
       ↓
┌─────────────┐
│   Review    │  Code review, PO acceptance testing
└──────┬──────┘
       │
       │ PO accepts, PR merged
       ↓
┌─────────────┐
│  Completed  │  Story archived, epic updated
└─────────────┘
```

### Story States

| State | Description | Location | Who Updates |
|-------|-------------|----------|-------------|
| **Backlog** | Ready to be worked on | `stories/backlog/` | Product Owner |
| **In Progress** | Currently being developed | `stories/in-progress/` | Developer |
| **Review** | Code review / Testing | `stories/in-progress/` | Developer |
| **Done** | Completed and deployed | `stories/completed/` | Developer |

---

## Best Practices

### For Product Owners

1. **Keep stories small**
   - Aim for 1-5 story points
   - Should be completable in 1-3 days
   - If larger, break down further

2. **Write clear acceptance criteria**
   - Use Given/When/Then format
   - Be specific and testable
   - Include success and error cases

3. **Prioritize ruthlessly**
   - Focus on business value
   - Consider dependencies
   - Balance new features with tech debt

4. **Groom backlog regularly**
   - Weekly review of upcoming stories
   - Ensure top stories are "Ready"
   - Remove or re-prioritize stale stories

5. **Be available for questions**
   - Developers need clarification
   - Quick answers unblock work
   - Better to clarify upfront

### For Developers

1. **Read the story thoroughly**
   - Understand the "why" not just "what"
   - Ask questions if unclear
   - Review technical details

2. **Update story as you work**
   - Check off checklist items
   - Note any deviations
   - Keep status current

3. **Write tests first (TDD)**
   - Write test for acceptance criteria
   - Implement until test passes
   - Refactor for quality

4. **Commit often**
   - Small, focused commits
   - Clear commit messages
   - Reference story ID

5. **Don't skip the checklist**
   - Tests, documentation, code review
   - All steps are important
   - Shortcuts create technical debt

### For Everyone

1. **Use templates**
   - Ensures consistency
   - Nothing is forgotten
   - Easy to find information

2. **Link everything**
   - Stories link to epics
   - Epics link to stories
   - Easy to navigate

3. **Keep files updated**
   - Don't let documentation get stale
   - Update as work progresses
   - Commit changes frequently

4. **Communicate**
   - Add comments to story files
   - Update status regularly
   - Flag blockers early

---

## Templates and Examples

### Quick Reference

| Template | Location | Use For |
|----------|----------|---------|
| **Epic Template** | `docs/templates/EPIC_TEMPLATE.md` | Creating new epics |
| **Story Template** | `docs/templates/STORY_TEMPLATE.md` | Creating new stories |
| **Example Epic** | `docs/epics/EPIC-001-search-filter-transactions.md` | Reference implementation |
| **Example Story** | `docs/stories/backlog/STORY-001-basic-text-search.md` | Reference implementation |

### Creating from Template

```bash
# Create a new epic
cp docs/templates/EPIC_TEMPLATE.md docs/epics/EPIC-XXX-name.md
# Edit the file and fill in details

# Create a new story
cp docs/templates/STORY_TEMPLATE.md docs/stories/backlog/STORY-XXX-name.md
# Edit the file and fill in details

# Commit
git add docs/
git commit -m "feat: Add EPIC-XXX and initial stories"
git push
```

---

## Tracking Progress

### Epic Progress

Track in the epic file:
```markdown
### Story Breakdown
Total Stories: 6
- Backlog: 3
- In Progress: 2
- Completed: 1

### Story Points
- Estimated: 21 points
- Completed: 3 points
- Remaining: 18 points
```

### Velocity Tracking

Track team velocity to improve estimates:
- **Sprint 1:** 15 points completed
- **Sprint 2:** 18 points completed
- **Sprint 3:** 20 points completed
- **Average:** 17.6 points per sprint

Use average velocity for future planning.

---

## Troubleshooting

### "I can't find a story to work on"
- Check `docs/stories/backlog/`
- Ask Product Owner to prioritize
- Look for stories marked "Ready"

### "Requirements are unclear"
- Add questions to story file
- Tag Product Owner in commit/PR
- Schedule quick sync meeting

### "Story is too large"
- Work with PO to break it down
- Create sub-tasks in story
- Split into multiple stories

### "Dependencies are blocking me"
- Update story with blocker info
- Move back to backlog
- Pick up a different story

---

## Summary

This workflow ensures:
- ✅ Clear requirements from Product Owner
- ✅ Structured development process
- ✅ Transparent progress tracking
- ✅ Quality deliverables
- ✅ Good collaboration between PO and developers

**Key Takeaways:**
1. Use templates for consistency
2. Update files as work progresses
3. Keep stories small and focused
4. Link epics and stories
5. Communicate frequently

---

**Questions or suggestions?** Update this document or discuss with the team!

**Last Updated:** 2025-10-21 by Tech Lead Agent
