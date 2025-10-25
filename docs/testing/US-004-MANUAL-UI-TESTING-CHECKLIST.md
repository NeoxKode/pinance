# US-004 Account Reconciliation - Manual UI Testing Checklist

**Story:** US-004 - Account Reconciliation
**Phase:** Phase 7 - Final Testing & Documentation
**Task:** 4.45 - Complete manual UI testing checklist
**Date:** October 23, 2025
**Tester:** _________________________
**Test Environment:** Development / Staging / Production (circle one)

---

## Overview

This checklist validates the complete UI/UX for the Account Reconciliation feature (US-004). Each test case should be executed and marked as **PASS**, **FAIL**, or **N/A**.

**Testing Prerequisites:**
- ✅ Application builds and runs without errors
- ✅ Test database with sample accounts and transactions available
- ✅ At least one account with 5+ unreconciled transactions
- ✅ Backend tests passing (41/41 reconciliation tests)

---

## Test Environment Setup

### Setup Instructions

1. **Start the application:**
   ```bash
   source .venv/bin/activate
   python main.py
   ```

2. **Prepare test data:**
   - Create or select a checking account
   - Add at least 10 transactions (mix of income and expenses)
   - Ensure transactions have various dates
   - Note the current account balance

3. **Required test scenarios:**
   - Scenario A: Balanced reconciliation (no discrepancy)
   - Scenario B: Reconciliation with discrepancy
   - Scenario C: Empty account (no unreconciled transactions)
   - Scenario D: Large dataset (50+ transactions)

---

## Test Cases

### Section 1: Dialog Access & Opening (3 tests)

#### TC-001: Open Reconciliation Dialog from Menu
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Launch application
  2. Select an account from the accounts list
  3. Click **Edit → Reconcile Account...** from menu bar
  4. Dialog should open
- **Expected Results:**
  - Dialog opens with title "Reconcile Account - [Account Name]"
  - Dialog is modal (blocks main window interaction)
  - Dialog size: minimum 800x600, initial 900x700
  - Account name appears in dialog header
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-002: Keyboard Shortcut (Ctrl+R)
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Select an account
  2. Press **Ctrl+R** keyboard shortcut
  3. Dialog should open
- **Expected Results:**
  - Dialog opens immediately
  - Same dialog as menu access
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-003: No Account Selected Warning
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Deselect all accounts (click on empty space)
  2. Click **Edit → Reconcile Account...** or press Ctrl+R
- **Expected Results:**
  - Warning dialog appears: "No Account Selected"
  - Message: "Please select an account to reconcile."
  - Reconciliation dialog does NOT open
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

---

### Section 2: Statement Details Section (4 tests)

#### TC-004: Statement Date Picker
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Open reconciliation dialog
  2. Locate "Statement Date" field
  3. Click date picker calendar icon
  4. Select a date (e.g., today's date)
- **Expected Results:**
  - Calendar popup appears
  - Date selection works
  - Date format displays as "MMM dd, yyyy" (e.g., "Oct 23, 2025")
  - Date field defaults to today's date
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-005: Statement Balance Input - Valid
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Open reconciliation dialog
  2. Enter a valid amount in "Statement Balance" field (e.g., "1234.56")
  3. Tab to next field or click elsewhere
- **Expected Results:**
  - Accepts decimal numbers (up to 2 decimal places)
  - No error messages
  - Summary section recalculates
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-006: Statement Balance Input - Invalid
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Try entering invalid inputs:
     - Letters: "abc"
     - Special characters: "$$$"
     - Multiple decimals: "12.34.56"
- **Expected Results:**
  - Input validator prevents invalid characters
  - Only numbers and one decimal point accepted
  - Field shows validation error styling (red border)
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-007: Opening Balance Display
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Open reconciliation dialog for an account
  2. Check "Opening Balance" field (read-only)
- **Expected Results:**
  - Shows $0.00 for first reconciliation
  - Shows last reconciliation's statement balance for subsequent reconciliations
  - Field is read-only (grayed out)
  - Label is clear: "Opening Balance:"
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

---

### Section 3: Transaction List (5 tests)

#### TC-008: Transaction Table Populates
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Open reconciliation dialog for account with transactions
  2. Observe transaction table
- **Expected Results:**
  - Table shows all unreconciled transactions
  - Columns visible: [✓] | Date | Description | Amount | Type
  - Transactions sorted by date (oldest first)
  - Amount formatting: positive for income (green), negative for expenses (red)
  - Alternating row colors for readability
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-009: Checkboxes Toggle Cleared Status
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Click checkbox for a transaction
  2. Observe state change
  3. Uncheck the same transaction
  4. Check multiple transactions
- **Expected Results:**
  - Checkbox toggles on/off smoothly
  - Checked row highlights or changes appearance
  - Summary section updates immediately
  - Cleared Balance recalculates
  - Discrepancy updates
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-010: Empty Transaction List
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Open dialog for account with NO unreconciled transactions
  2. Observe transaction table
- **Expected Results:**
  - Table shows message: "No unreconciled transactions"
  - OR table is empty with clear indication
  - Complete button behavior (should be disabled or show warning)
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-011: Transaction List Scrolling (Large Dataset)
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Open dialog for account with 50+ transactions
  2. Scroll through transaction list
- **Expected Results:**
  - Table scrolls smoothly
  - All transactions visible when scrolling
  - Header row stays fixed at top
  - Performance is acceptable (no lag)
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-012: Transaction Details Accuracy
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Compare transaction details in dialog with main window transaction list
  2. Verify date, description, amount match
- **Expected Results:**
  - All transaction details accurate
  - Date format consistent
  - Amount values match
  - No missing or duplicate transactions
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

---

### Section 4: Summary Section & Calculations (5 tests)

#### TC-013: Summary Recalculates on Every Change
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Check a transaction → observe summary update
  2. Uncheck transaction → observe summary update
  3. Change statement balance → observe summary update
- **Expected Results:**
  - **Opening Balance:** Remains constant (from last reconciliation)
  - **+ Cleared Transactions:** Updates when transactions checked/unchecked
  - **= Cleared Balance:** Opening + Cleared Transactions
  - **Statement Balance:** Updates when user changes input
  - **Discrepancy:** Statement Balance - Cleared Balance
  - All calculations instant (< 100ms)
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-014: Discrepancy Color Coding - GREEN (Balanced)
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Check transactions until Cleared Balance matches Statement Balance
  2. Observe discrepancy field
- **Expected Results:**
  - Discrepancy shows "$0.00"
  - Background color: **GREEN** (#4CAF50 or similar)
  - Text: "✓ Balanced" or "Perfect match!"
  - Visual indication of success
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-015: Discrepancy Color Coding - YELLOW (Minor)
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Create small discrepancy ($0.01 - $10.00)
  2. Observe discrepancy field
- **Expected Results:**
  - Discrepancy shows amount (e.g., "$5.23")
  - Background color: **YELLOW** (#FF9800 or similar)
  - Warning icon or text
  - Notes field becomes prominent (for explanation)
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-016: Discrepancy Color Coding - RED (Major)
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Create large discrepancy (> $10.00)
  2. Observe discrepancy field
- **Expected Results:**
  - Discrepancy shows amount (e.g., "$125.00")
  - Background color: **RED** (#F44336 or similar)
  - Error icon or strong warning
  - Notes field required or emphasized
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-017: Calculation Accuracy
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Manually calculate expected values using calculator
  2. Compare with dialog calculations
  3. Test with:
     - Positive amounts only
     - Negative amounts only
     - Mix of positive and negative
     - Large numbers (> $100,000)
     - Small decimals ($0.01)
- **Expected Results:**
  - All calculations accurate to 2 decimal places
  - No rounding errors
  - Handles negative amounts correctly (expenses)
  - Large numbers display properly
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

---

### Section 5: Complete Button & Validation (4 tests)

#### TC-018: Complete Button - Enabled State
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Observe "Complete Reconciliation" button state in different scenarios:
     - No transactions checked
     - Some transactions checked
     - All transactions checked
     - Statement balance empty vs filled
- **Expected Results:**
  - Button ENABLED when:
    - Statement balance has valid value
    - At least one transaction is checked (optional requirement)
  - Button DISABLED when:
    - Statement balance is empty or invalid
    - No statement date selected
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-019: Confirmation Dialog - No Discrepancy
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Balance the reconciliation (discrepancy = $0.00)
  2. Click "Complete Reconciliation"
- **Expected Results:**
  - No confirmation dialog (proceeds immediately)
  - OR simple confirmation: "Complete reconciliation?"
  - Reconciliation completes successfully
  - Success message appears
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-020: Confirmation Dialog - With Discrepancy
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Create discrepancy (e.g., $10.50)
  2. Click "Complete Reconciliation"
- **Expected Results:**
  - Confirmation dialog appears
  - Message: "There is a discrepancy of $10.50. Are you sure you want to complete?"
  - Shows "Yes" and "No" buttons
  - "No" cancels and returns to dialog
  - "Yes" proceeds with reconciliation
  - Notes field content saved with reconciliation
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-021: Notes Field Saves with Reconciliation
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Create discrepancy
  2. Enter notes: "Bank fee of $5.00 not yet recorded"
  3. Complete reconciliation
  4. Check reconciliation history (if available)
- **Expected Results:**
  - Notes field is multi-line text area
  - Accepts long text (100+ characters)
  - Notes saved with reconciliation record
  - Notes visible in reconciliation history
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

---

### Section 6: UI Refresh & Status Display (3 tests)

#### TC-022: Transaction List Shows Cleared Status
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Complete a reconciliation
  2. Return to main window
  3. View transaction list for that account
- **Expected Results:**
  - Transaction list has "Reconciliation Status" or "✓" column
  - Cleared transactions show: "Cleared" or "✓" indicator
  - Cleared date displayed (statement date or reconciliation date)
  - Status icon/text clearly visible
  - Unreconciled transactions show: "Unreconciled" or empty
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-023: Account Info Shows Last Reconciled Date
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Complete a reconciliation
  2. Check account details panel
  3. Look for "Last Reconciled" field
- **Expected Results:**
  - Account details show: "Last Reconciled: Oct 23, 2025"
  - Date matches reconciliation statement date
  - Date format consistent with app style
  - Shows "Never" or "--" if not yet reconciled
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-024: Status Bar Success Message
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Complete reconciliation successfully
  2. Observe main window status bar
- **Expected Results:**
  - Status message appears: "Reconciliation #[ID] completed successfully"
  - Message visible for 3-5 seconds
  - Message uses success styling (green icon/text)
  - Message auto-disappears after timeout
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

---

### Section 7: Dark Theme & Styling (2 tests)

#### TC-025: Dark Theme Consistency
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Enable dark theme (if application supports it)
  2. Open reconciliation dialog
  3. Inspect all UI elements
- **Expected Results:**
  - All dialog elements use dark theme colors
  - Text readable (good contrast)
  - Buttons styled consistently
  - Table rows alternate colors appropriately
  - Green/Yellow/Red discrepancy colors still visible
  - No white "flashes" or inconsistent backgrounds
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-026: Visual Polish & Professional Appearance
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Review overall dialog appearance
  2. Check spacing, alignment, fonts, colors
- **Expected Results:**
  - Consistent padding and margins (8-16px)
  - Aligned labels and inputs
  - Professional font choices and sizes
  - Color scheme consistent with app branding
  - No overlapping elements
  - No truncated text
  - Icons (if any) consistent style
  - Buttons clearly distinguishable (primary vs secondary)
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

---

### Section 8: Edge Cases & Error Handling (5 tests)

#### TC-027: Edge Case - No Unreconciled Transactions
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Open dialog for fully reconciled account (no unreconciled transactions)
- **Expected Results:**
  - Dialog opens with empty transaction table
  - Message: "No unreconciled transactions" or similar
  - Complete button disabled or shows informative message
  - No errors or crashes
  - Cancel button works to close dialog
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-028: Edge Case - All Transactions Cleared
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Open dialog with transactions
  2. Check ALL transactions
  3. Enter statement balance matching total
  4. Complete reconciliation
- **Expected Results:**
  - All checkboxes checked
  - Cleared Balance = sum of all transactions
  - Reconciliation completes successfully
  - Next reconciliation shows no unreconciled transactions
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-029: Edge Case - Future Statement Date
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Select statement date in the future (e.g., 30 days from today)
  2. Try to complete reconciliation
- **Expected Results:**
  - EITHER: Warning message appears: "Statement date is in the future. Continue?"
  - OR: Validation prevents future dates
  - If allowed, reconciliation completes with future date saved
  - No crashes or data corruption
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-030: Error Handling - Concurrent Reconciliation
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. (If possible) Open two reconciliation dialogs for same account
  2. OR Start reconciliation, and simulate backend error for concurrent reconciliation
- **Expected Results:**
  - Error message: "A reconciliation is already in progress for this account"
  - OR: Second dialog prevents opening
  - Error message is clear and helpful
  - User can cancel and retry
  - No data corruption
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-031: Cancel Button & Dialog Close
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Open dialog, make changes (check transactions, enter balance)
  2. Click "Cancel" button
  3. OR click X button on window
  4. Reopen dialog
- **Expected Results:**
  - Confirmation prompt: "Discard changes?" (if changes made)
  - OR: Dialog closes immediately (if no changes)
  - No data saved when cancelled
  - Reopening dialog shows fresh state (no saved checkboxes)
  - No memory leaks or hanging processes
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

---

### Section 9: Keyboard Shortcuts & Accessibility (3 tests)

#### TC-032: Keyboard Shortcuts Work
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Open dialog
  2. Try keyboard shortcuts:
     - **Tab**: Navigate between fields
     - **Space**: Toggle transaction checkboxes (when focused)
     - **Enter**: Complete reconciliation (when Complete button focused)
     - **Esc**: Cancel/close dialog
- **Expected Results:**
  - Tab order logical (top to bottom, left to right)
  - Space toggles checkboxes
  - Enter triggers Complete button
  - Esc closes dialog
  - Keyboard navigation feels natural
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-033: Focus Indicators Visible
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Use Tab to navigate through dialog
  2. Observe focus indicators on each element
- **Expected Results:**
  - Blue outline or border shows focused element
  - Focus indicator visible on all interactive elements
  - Focus indicator meets WCAG contrast requirements
  - No "invisible focus" (always know where you are)
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

#### TC-034: Screen Reader Compatibility (if applicable)
- [ ] **PASS** | **FAIL** | **N/A**
- **Steps:**
  1. Enable screen reader (e.g., NVDA, JAWS, VoiceOver)
  2. Navigate dialog with screen reader
- **Expected Results:**
  - All labels read correctly
  - Button purposes clear
  - Form fields announce labels
  - Table structure navigable
  - Error messages announced
  - Summary values read correctly
- **Actual Results:** _______________________________________
- **Notes:** _____________________________________________

---

## Test Summary

**Total Test Cases:** 34
**Passed:** _____ / 34
**Failed:** _____ / 34
**N/A:** _____ / 34

**Pass Rate:** _____%

---

## Defects Found

| ID | Test Case | Severity | Description | Status |
|----|-----------|----------|-------------|--------|
| DEF-001 | TC-___ | Critical / Major / Minor | _________________ | Open / Fixed / Closed |
| DEF-002 | TC-___ | Critical / Major / Minor | _________________ | Open / Fixed / Closed |
| DEF-003 | TC-___ | Critical / Major / Minor | _________________ | Open / Fixed / Closed |

**Severity Definitions:**
- **Critical:** Blocks feature usage, data loss, crashes
- **Major:** Important functionality broken, workaround exists
- **Minor:** Cosmetic issues, minor inconvenience

---

## Recommendations

### Must Fix Before Release
- [ ] List critical/major defects here
- [ ] _____________________________________________
- [ ] _____________________________________________

### Nice to Have (Future Improvements)
- [ ] List minor issues or enhancements here
- [ ] _____________________________________________
- [ ] _____________________________________________

### Performance Notes
- Average dialog open time: ______ ms
- Average calculation update time: ______ ms
- Acceptable performance with ______ transactions

---

## Sign-off

**Tester Name:** _________________________
**Test Date:** _________________________
**Signature:** _________________________

**Reviewed By:** _________________________
**Review Date:** _________________________

---

## Appendix: Test Data

### Test Account Details
- **Account Name:** _________________________
- **Account Type:** Checking / Savings / Credit Card
- **Opening Balance:** $_________
- **Number of Transactions:** _____
- **Date Range:** _________ to _________

### Test Reconciliation Scenarios

**Scenario A: Balanced Reconciliation**
- Opening Balance: $500.00
- 5 transactions checked (total: $250.00)
- Statement Balance: $750.00
- Expected Discrepancy: $0.00 ✓

**Scenario B: Discrepancy Reconciliation**
- Opening Balance: $500.00
- 3 transactions checked (total: $100.00)
- Statement Balance: $595.00 (missing $5 bank fee)
- Expected Discrepancy: $5.00
- Notes: "Bank fee of $5.00 not yet recorded"

---

**Document Version:** 1.0
**Last Updated:** October 23, 2025
**Story:** US-004 Account Reconciliation
**Phase:** Phase 7 - Final Testing
