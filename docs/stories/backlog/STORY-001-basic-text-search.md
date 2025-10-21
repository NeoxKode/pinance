# User Story: Basic Text Search for Transactions

**Story ID:** STORY-001
**Epic:** [EPIC-001: Search and Filter Transactions](../../epics/EPIC-001-search-filter-transactions.md)
**Created:** 2025-10-21
**Status:** Backlog
**Priority:** High
**Story Points:** 3
**Assignee:** [Unassigned]

---

## User Story

**As a** user managing my finances
**I want** to search transactions by description text
**So that** I can quickly find specific transactions without scrolling through hundreds of entries

---

## Description

### Context
Users currently must manually scroll through all transactions to find a specific transaction. With hundreds or thousands of transactions, this becomes time-consuming and frustrating. A simple text search will dramatically improve the user experience.

### Problem Statement
Without search functionality, finding a specific transaction (e.g., "Starbucks purchase from last month") requires manually scrolling and reading through potentially hundreds of entries.

### Proposed Solution
Add a search input field in the transaction view that filters transactions in real-time as the user types. The search should match against transaction descriptions (case-insensitive) and update the table immediately.

---

## Acceptance Criteria

### Functional Requirements
- [ ] Given I'm on the main window with transactions visible, when I type text in the search box, then only transactions containing that text in the description are displayed
- [ ] Given I've entered search text, when I clear the search box, then all transactions are displayed again
- [ ] Given I'm searching for "coffee", when transactions contain "Coffee", "COFFEE", or "coffee", then all variants are found (case-insensitive)
- [ ] Given the search box is empty, when I start typing, then results update in real-time (no need to press Enter)
- [ ] Given no transactions match my search, when I search for non-existent text, then an empty table is shown with a "No results found" message

### Non-Functional Requirements
- [ ] Performance: Search results appear in <100ms for up to 1,000 transactions
- [ ] Performance: Search results appear in <500ms for up to 10,000 transactions
- [ ] Security: Search input is sanitized to prevent SQL injection
- [ ] Usability: Search box is prominently placed and clearly labeled
- [ ] Accessibility: Search box is keyboard accessible (Tab navigation)

### Definition of Done
- [ ] Code implemented and follows coding standards
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests written and passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Manual testing completed
- [ ] Acceptance criteria verified by PO
- [ ] Performance benchmarks met
- [ ] No critical bugs

---

## Technical Details

### Affected Components
- [ ] UI Layer: `finance_app/ui/main_window.py`
- [ ] Business Layer: `finance_app/business/transaction_service.py`
- [ ] Data Layer: `finance_app/data/repositories/transaction_repository.py`
- [ ] Database: Add index on `transactions.description`
- [ ] Tests: `finance_app/tests/unit/test_transaction_search.py`

### Implementation Approach
```
1. Add database index for faster search:
   CREATE INDEX idx_transactions_description
   ON transactions(description COLLATE NOCASE);

2. Add repository method:
   TransactionRepository.search_by_description(search_text: str)
   - Use SQL LIKE with wildcards: WHERE description LIKE '%text%'
   - Case-insensitive search: COLLATE NOCASE

3. Add service method:
   TransactionService.search_transactions(search_text: str)
   - Validate input (strip, sanitize)
   - Call repository method
   - Return filtered transactions

4. Add UI components:
   - QLineEdit for search input
   - Connect textChanged signal to search handler
   - Update table with filtered results

5. Add tests:
   - Unit tests for repository search
   - Unit tests for service validation
   - Integration tests for full search flow
```

### API Changes
```python
# finance_app/data/repositories/transaction_repository.py
class TransactionRepository:
    def search_by_description(
        self,
        search_text: str,
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Search transactions by description.

        Args:
            search_text: Text to search for (case-insensitive)
            account_id: Optional account filter

        Returns:
            List of matching transactions
        """
        pass

# finance_app/business/transaction_service.py
class TransactionService:
    def search_transactions(
        self,
        search_text: str,
        account_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Search transactions with validation.

        Args:
            search_text: Text to search for
            account_id: Optional account filter

        Returns:
            List of matching transactions

        Raises:
            ValidationError: If search text is invalid
        """
        pass
```

### Database Changes
```sql
-- Add index for faster search
CREATE INDEX IF NOT EXISTS idx_transactions_description_search
ON transactions(description COLLATE NOCASE);

-- Test query performance
EXPLAIN QUERY PLAN
SELECT * FROM transactions
WHERE description LIKE '%coffee%' COLLATE NOCASE
ORDER BY date DESC;
```

---

## Design

### UI/UX Mockups
```
┌─────────────────────────────────────────────────────────┐
│  Transactions                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 🔍 Search transactions...                     [X]│  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Date       Description         Category    Amount     │
│  ──────────────────────────────────────────────────── │
│  2025-10-20 Starbucks Coffee   Food        -$5.50     │
│  2025-10-18 Coffee Bean        Food        -$4.25     │
│  2025-10-15 Morning Coffee     Food        -$3.75     │
│                                                         │
│  3 results found for "coffee"                          │
└─────────────────────────────────────────────────────────┘
```

### User Flow
```
1. User navigates to main window with transactions
2. User sees search box above transaction table
3. User clicks in search box (or presses Ctrl+F)
4. User types "coffee"
5. Table updates in real-time showing only matching transactions
6. User sees "3 results found for 'coffee'" at bottom
7. User clears search (X button or Backspace)
8. All transactions displayed again
```

---

## Test Plan

### Test Cases

#### Test Case 1: Basic Search
- **Given:** Transaction table has 100 transactions
- **When:** User types "Starbucks" in search box
- **Then:** Only transactions with "Starbucks" in description are shown
- **Test Data:** 5 Starbucks transactions, 95 other transactions

#### Test Case 2: Case Insensitive Search
- **Given:** Transaction with "COFFEE", "Coffee", and "coffee"
- **When:** User types "coffee"
- **Then:** All three transactions are displayed
- **Test Data:** 3 transactions with different capitalizations

#### Test Case 3: Partial Match
- **Given:** Transaction "Starbucks Coffee Shop"
- **When:** User types "Coffee"
- **Then:** Transaction is displayed
- **Test Data:** Transaction with multi-word description

#### Test Case 4: No Results
- **Given:** No transactions contain "xyz"
- **When:** User types "xyz"
- **Then:** Empty table with "No results found" message
- **Test Data:** 100 transactions, none matching "xyz"

#### Test Case 5: Clear Search
- **Given:** User has search active with results filtered
- **When:** User clicks [X] button or clears text
- **Then:** All transactions displayed again
- **Test Data:** Filtered view with 5 results out of 100

### Edge Cases
- [ ] Search with special characters (!@#$%)
- [ ] Search with very long text (200+ characters)
- [ ] Search with numbers (amounts vs descriptions)
- [ ] Search with empty string
- [ ] Search with only whitespace
- [ ] Search with SQL injection attempts

### Error Scenarios
- [ ] Database connection lost during search
- [ ] Invalid search input (malformed SQL)
- [ ] Extremely large result set (10,000+ matches)

---

## Dependencies

### Blocked By
- None (can start immediately)

### Blocks
- [STORY-005: Combined filters](STORY-005-combined-filters.md) - Needs basic search working first

### Related Stories
- [STORY-002: Date range filter](STORY-002-date-range-filter.md)
- [STORY-003: Category filter](STORY-003-category-filter.md)

---

## Estimation

### Story Points Breakdown
- **Development:** 2 points
  - Repository method: 0.5 points
  - Service method: 0.5 points
  - UI components: 1 point
- **Testing:** 0.5 points
- **Code Review:** 0.25 points
- **Documentation:** 0.25 points
- **Total:** 3 points

### Time Estimate
- **Optimistic:** 4 hours
- **Realistic:** 6 hours
- **Pessimistic:** 8 hours

### Complexity
- **Technical Complexity:** Low (straightforward LIKE query)
- **Business Complexity:** Low (simple search logic)
- **Risk Level:** Low (minimal risk)

---

## Implementation Checklist

### Development
- [ ] Branch created: `feature/STORY-001-basic-text-search`
- [ ] Database index added (`idx_transactions_description_search`)
- [ ] Repository method implemented (`search_by_description`)
- [ ] Service method implemented (`search_transactions`)
- [ ] Input validation added
- [ ] UI search box added to main window
- [ ] Signal/slot connected (textChanged → search handler)
- [ ] Results display updated in real-time
- [ ] "No results" message added
- [ ] Clear search button added
- [ ] Error handling added
- [ ] Logging added
- [ ] Type hints added
- [ ] Docstrings added

### Testing
- [ ] Unit test: Repository search method
- [ ] Unit test: Service validation
- [ ] Unit test: Case-insensitive search
- [ ] Unit test: Partial match search
- [ ] Unit test: Special characters
- [ ] Integration test: Full search flow
- [ ] Performance test: 1,000 transactions
- [ ] Performance test: 10,000 transactions
- [ ] Manual testing: UI interaction
- [ ] Manual testing: Real-time updates
- [ ] All tests passing locally

### Code Review
- [ ] Self-review completed
- [ ] PR created: "feat: Add basic text search for transactions (STORY-001)"
- [ ] PR description includes demo GIF/video
- [ ] Code review requested from tech lead
- [ ] Feedback addressed
- [ ] PR approved

### Documentation
- [ ] Code comments added
- [ ] Docstrings added to all methods
- [ ] ARCHITECTURE.md updated (if needed)
- [ ] QUICK_START.md updated with search feature
- [ ] CHANGELOG updated

### Deployment
- [ ] Merged to main
- [ ] Deployed to staging
- [ ] Smoke tests passed on staging
- [ ] PO acceptance obtained
- [ ] Ready for production

---

## Notes

### Technical Notes
- SQLite's `LIKE` operator with `COLLATE NOCASE` provides case-insensitive search
- For better performance with large datasets, consider full-text search (FTS5) in future
- Current implementation uses simple substring match; fuzzy search can be added in v2.2

### Business Notes
- User research shows 60% of users would use search if available
- Competitors (Mint, YNAB) all have search functionality
- This is table stakes for modern finance apps

### Questions
- [x] Should search be real-time or require Enter key? **Answer: Real-time for better UX**
- [x] Should we search other fields (category, amount)? **Answer: No, description only for now**
- [x] Should we highlight matched text? **Answer: Nice-to-have, v2.2**

### Risks
- **Performance with large datasets:** Mitigated by database index
- **UI responsiveness:** Mitigated by debouncing (search after 300ms pause)

---

## Activity Log

### Comments
| Date | Author | Comment |
|------|--------|---------|
| 2025-10-21 | Tech Lead | Story created from epic breakdown |

### Status Changes
| Date | From | To | Author |
|------|------|-----|--------|
| 2025-10-21 | - | Backlog | Tech Lead |

### Time Tracking
| Date | Developer | Hours | Activity |
|------|-----------|-------|----------|
| - | - | - | Not started |

---

## Demo

### Demo Script
1. Show transaction list with 50+ transactions
2. Type "coffee" in search box
3. Show real-time filtering as typing
4. Show "5 results found" message
5. Clear search and show all transactions again
6. Search for non-existent term, show empty state
7. Show performance: search 1,000 transactions instantly

### Demo Date
[To be scheduled after implementation]

### Demo Feedback
[To be collected after demo]

---

## References

### Code References
- `finance_app/ui/main_window.py:315` - Transaction table widget
- `finance_app/data/repositories/transaction_repository.py:50` - get_all method (reference)

### Related Documents
- [EPIC-001: Search and Filter Transactions](../../epics/EPIC-001-search-filter-transactions.md)
- [Architecture Documentation](../../ARCHITECTURE.md)
- [Technical Design](../../TECHNICAL_DESIGN.md)

### External Resources
- [SQLite LIKE operator documentation](https://www.sqlite.org/lang_expr.html#like)
- [Qt QLineEdit signals documentation](https://doc.qt.io/qt-6/qlineedit.html#signals)
- [UX patterns for search interfaces](https://www.nngroup.com/articles/search-interface/)

---

**Created By:** Tech Lead Agent
**Last Updated:** 2025-10-21
**Reviewed By:** [Pending]
