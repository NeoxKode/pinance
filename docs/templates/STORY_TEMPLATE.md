# User Story: [Story Title]

**Story ID:** STORY-XXX
**Epic:** [EPIC-XXX: Epic Name](../epics/EPIC-XXX.md)
**Created:** YYYY-MM-DD
**Status:** [Backlog | Ready | In Progress | Review | Testing | Done]
**Priority:** [Critical | High | Medium | Low]
**Story Points:** [X points]
**Assignee:** [Developer Name]

---

## User Story

**As a** [type of user]
**I want** [goal/desire]
**So that** [benefit/value]

---

## Description

### Context
[Provide background and context for this story]

### Problem Statement
[What problem are we solving?]

### Proposed Solution
[Brief overview of the solution]

---

## Acceptance Criteria

### Functional Requirements
- [ ] Given [context], when [action], then [expected result]
- [ ] Given [context], when [action], then [expected result]
- [ ] Given [context], when [action], then [expected result]

### Non-Functional Requirements
- [ ] Performance: [Specific performance requirement]
- [ ] Security: [Security considerations]
- [ ] Accessibility: [Accessibility requirements]
- [ ] Usability: [UX/UI requirements]

### Definition of Done
- [ ] Code implemented and follows coding standards
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests written and passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Manual testing completed
- [ ] Acceptance criteria verified by PO
- [ ] Deployed to staging environment
- [ ] No critical bugs

---

## Technical Details

### Affected Components
- [ ] UI Layer: [Specific files]
- [ ] Business Layer: [Specific files]
- [ ] Data Layer: [Specific files]
- [ ] Database: [Schema changes]
- [ ] Tests: [New test files]

### Implementation Approach
```
[Brief technical approach or pseudocode]

Example:
1. Create new service method in TransactionService
2. Add validation in TransactionValidator
3. Create repository method in TransactionRepository
4. Update UI component to call new service
5. Add tests for all layers
```

### API Changes
```python
# New methods/classes to be added
class NewService:
    def new_method(self, param: Type) -> ReturnType:
        """Method description."""
        pass
```

### Database Changes
```sql
-- Schema changes if any
ALTER TABLE table_name ADD COLUMN new_column TYPE;
CREATE INDEX idx_name ON table_name(column);
```

---

## Design

### UI/UX Mockups
[Link to Figma/design files or embed screenshots]

### User Flow
```
1. User navigates to [screen]
2. User clicks [button]
3. System displays [result]
4. User confirms [action]
5. System updates [data]
```

### Wireframes
[Attach or link to wireframes]

---

## Test Plan

### Test Cases

#### Test Case 1: [Scenario Name]
- **Given:** [Initial state]
- **When:** [Action performed]
- **Then:** [Expected outcome]
- **Test Data:** [Specific test data]

#### Test Case 2: [Scenario Name]
- **Given:** [Initial state]
- **When:** [Action performed]
- **Then:** [Expected outcome]
- **Test Data:** [Specific test data]

### Edge Cases
- [ ] [Edge case 1]
- [ ] [Edge case 2]
- [ ] [Edge case 3]

### Error Scenarios
- [ ] [Error scenario 1]
- [ ] [Error scenario 2]

---

## Dependencies

### Blocked By
- [ ] [STORY-XXX: Dependency story](STORY-XXX.md)
- [ ] [External dependency]

### Blocks
- [ ] [STORY-XXX: Story that depends on this](STORY-XXX.md)

### Related Stories
- [STORY-XXX: Related story](STORY-XXX.md)
- [STORY-XXX: Related story](STORY-XXX.md)

---

## Estimation

### Story Points Breakdown
- **Development:** X points
- **Testing:** X points
- **Code Review:** X points
- **Documentation:** X points
- **Total:** X points

### Time Estimate
- **Optimistic:** X hours
- **Realistic:** X hours
- **Pessimistic:** X hours

### Complexity
- **Technical Complexity:** [Low | Medium | High]
- **Business Complexity:** [Low | Medium | High]
- **Risk Level:** [Low | Medium | High]

---

## Implementation Checklist

### Development
- [ ] Branch created from `main`: `feature/STORY-XXX-description`
- [ ] Data layer implementation
- [ ] Business layer implementation
- [ ] UI layer implementation
- [ ] Error handling added
- [ ] Logging added
- [ ] Type hints added
- [ ] Docstrings added

### Testing
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Manual testing completed
- [ ] Edge cases tested
- [ ] Error scenarios tested
- [ ] All tests passing locally

### Code Review
- [ ] Self-review completed
- [ ] PR created with description
- [ ] Code review requested
- [ ] Feedback addressed
- [ ] PR approved

### Documentation
- [ ] Code comments added
- [ ] API documentation updated
- [ ] User documentation updated
- [ ] CHANGELOG updated

### Deployment
- [ ] Merged to main
- [ ] Deployed to staging
- [ ] Smoke tests passed
- [ ] PO acceptance obtained
- [ ] Deployed to production (if applicable)

---

## Notes

### Technical Notes
[Any technical considerations, alternatives considered, or implementation notes]

### Business Notes
[Business context, market research, user feedback]

### Questions
- [ ] [Question 1 - Status: Open/Answered]
- [ ] [Question 2 - Status: Open/Answered]

### Risks
- [Risk 1 and mitigation plan]
- [Risk 2 and mitigation plan]

---

## Activity Log

### Comments
| Date | Author | Comment |
|------|--------|---------|
| YYYY-MM-DD | [Name] | [Comment] |

### Status Changes
| Date | From | To | Author |
|------|------|-----|--------|
| YYYY-MM-DD | Backlog | In Progress | [Name] |
| YYYY-MM-DD | In Progress | Review | [Name] |
| YYYY-MM-DD | Review | Done | [Name] |

### Time Tracking
| Date | Developer | Hours | Activity |
|------|-----------|-------|----------|
| YYYY-MM-DD | [Name] | X | Development |
| YYYY-MM-DD | [Name] | X | Testing |

---

## Demo

### Demo Script
1. [Step 1 to demonstrate]
2. [Step 2 to demonstrate]
3. [Step 3 to demonstrate]

### Demo Date
[Date of demo to stakeholders]

### Demo Feedback
[Feedback received during demo]

---

## References

### Code References
- `file_path:line_number` - [Description]
- `file_path:line_number` - [Description]

### Related Documents
- [Architecture Documentation](../ARCHITECTURE.md)
- [Technical Design](../TECHNICAL_DESIGN.md)

### External Resources
- [Link to relevant documentation]
- [Link to research or examples]

---

**Created By:** [Author Name]
**Last Updated:** YYYY-MM-DD
**Reviewed By:** [Reviewer Name] on YYYY-MM-DD
