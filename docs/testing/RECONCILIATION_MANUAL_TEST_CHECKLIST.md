# Reconciliation Feature - Manual Testing Checklist

**Feature:** US-004 Account Reconciliation
**Test Date:** 2025-10-25
**Tester:** _____________
**Status:** ⏳ In Progress

---

## Pre-Test Setup

- [ ] Application launched successfully
- [ ] Database contains at least one account with transactions
- [ ] Test account has mix of reconciled and unreconciled transactions

---

## Test Cases

### 1. Dialog Opening & Access
- [ ] **Test 1.1:** Reconciliation dialog opens from Edit menu
  - **Steps:** Click Edit → Reconcile Account... (or press Ctrl+R)
  - **Expected:** Dialog opens if account is selected
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 1.2:** Warning shown if no account selected
  - **Steps:** Deselect all accounts, then click Edit → Reconcile Account...
  - **Expected:** Warning message "Please select an account to reconcile"
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

### 2. Statement Details Section
- [ ] **Test 2.1:** Statement details section displays correctly
  - **Steps:** Open reconciliation dialog
  - **Expected:** Account name shown, statement date picker visible, balance input visible
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 2.2:** Statement date picker works
  - **Steps:** Click on statement date field, select a date from calendar
  - **Expected:** Date updates, calendar popup works smoothly
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 2.3:** Statement balance accepts valid decimal input
  - **Steps:** Enter various amounts: 1234.56, 0.00, 99999.99
  - **Expected:** All valid decimal amounts accepted
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

### 3. Transaction List
- [ ] **Test 3.1:** Transaction table populates with unreconciled transactions
  - **Steps:** Open dialog, observe transaction list
  - **Expected:** Only unreconciled transactions shown, sorted by date
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 3.2:** Checkboxes toggle cleared status
  - **Steps:** Click checkbox for a transaction
  - **Expected:** Checkbox toggles on/off smoothly
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 3.3:** Transaction count label displays total
  - **Steps:** Observe transaction count label
  - **Expected:** Shows "X transactions to reconcile"
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

### 4. Summary Section & Real-time Calculations
- [ ] **Test 4.1:** Summary section displays on dialog open
  - **Steps:** Open dialog, observe summary section
  - **Expected:** Opening Balance, Cleared Transactions, Cleared Balance, Statement Balance, Discrepancy all visible
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 4.2:** Summary recalculates when checkbox clicked
  - **Steps:** Check/uncheck a transaction, watch summary update
  - **Expected:** Cleared Transactions and Cleared Balance update immediately
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 4.3:** Summary recalculates when statement balance changes
  - **Steps:** Change statement balance input, watch discrepancy update
  - **Expected:** Discrepancy recalculates immediately
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 4.4:** Discrepancy color-coding works (green/yellow/red)
  - **Steps:**
    - Create balanced reconciliation (discrepancy = $0.00) → should be GREEN
    - Create positive discrepancy (statement > cleared) → should be YELLOW/ORANGE
    - Create negative discrepancy (statement < cleared) → should be RED
  - **Expected:** Colors match discrepancy type with helpful status messages
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

### 5. Complete Reconciliation
- [ ] **Test 5.1:** "Complete Reconciliation" button enables/disables correctly
  - **Steps:**
    - Open dialog with no statement balance → button should be disabled
    - Enter statement balance → button should enable
  - **Expected:** Button only enabled when valid balance entered
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 5.2:** Confirmation dialog shown on discrepancy
  - **Steps:** Create reconciliation with discrepancy > $0.01, click Complete
  - **Expected:** Confirmation dialog asks if you want to proceed with discrepancy
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 5.3:** Notes field dialog appears for discrepancy
  - **Steps:** Confirm proceeding with discrepancy
  - **Expected:** Multi-line text input dialog for notes appears
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 5.4:** Notes field saves with reconciliation
  - **Steps:** Enter notes, complete reconciliation
  - **Expected:** Reconciliation saved with notes
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 5.5:** Success message displayed after completion
  - **Steps:** Complete a balanced reconciliation
  - **Expected:** Success message with reconciliation details shown
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

### 6. Post-Reconciliation Updates
- [ ] **Test 6.1:** Transaction list shows cleared status after reconciliation
  - **Steps:** Complete reconciliation, close dialog, view transaction list
  - **Expected:** "✓ Reconciled" shown in Status column for cleared transactions (green color)
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 6.2:** Account shows last_reconciled_date (if visible in UI)
  - **Steps:** Complete reconciliation, check account details
  - **Expected:** Last reconciled date updated
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

### 7. Theme & Styling
- [ ] **Test 7.1:** Dark theme consistent across all dialog elements
  - **Steps:** Review entire dialog appearance
  - **Expected:** All elements match app's dark theme (#2b2b2b background)
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 7.2:** Amount color-coding works (red negative, green positive)
  - **Steps:** Observe transaction amounts in table
  - **Expected:** Negative amounts red, positive amounts green
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

### 8. Edge Cases
- [ ] **Test 8.1:** No unreconciled transactions scenario
  - **Steps:** Reconcile all transactions, open dialog again
  - **Expected:** Message shown "No transactions to reconcile" or empty table
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 8.2:** All transactions already cleared scenario
  - **Steps:** Mark all as cleared, complete reconciliation
  - **Expected:** Works correctly with all checkboxes checked
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 8.3:** Future statement date warning
  - **Steps:** Enter a statement date in the future
  - **Expected:** Warning shown or date highlighted
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

### 9. Error Handling
- [ ] **Test 9.1:** Concurrent reconciliation prevention
  - **Steps:** (Complex - requires opening same account in two windows)
  - **Expected:** Error message if reconciliation already in progress
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

### 10. Keyboard Shortcuts
- [ ] **Test 10.1:** Ctrl+R keyboard shortcut opens dialog
  - **Steps:** Press Ctrl+R with account selected
  - **Expected:** Dialog opens
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 10.2:** Tab navigation works through form fields
  - **Steps:** Press Tab repeatedly to move through fields
  - **Expected:** Focus moves logically through date, balance, buttons
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 10.3:** Enter key submits form when on Complete button
  - **Steps:** Tab to Complete button, press Enter
  - **Expected:** Reconciliation completes
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

- [ ] **Test 10.4:** Escape key cancels dialog
  - **Steps:** Press Escape key
  - **Expected:** Dialog closes without saving
  - **Result:** ⬜ Pass ⬜ Fail
  - **Notes:** _____________

---

## Summary

**Total Tests:** 33
**Passed:** _____
**Failed:** _____
**Pass Rate:** _____%

---

## Issues Found

| # | Test | Severity | Description | Steps to Reproduce |
|---|------|----------|-------------|-------------------|
| 1 |      |          |             |                   |
| 2 |      |          |             |                   |
| 3 |      |          |             |                   |

---

## Overall Assessment

- [ ] Feature is ready for production
- [ ] Feature needs minor fixes
- [ ] Feature needs major fixes

**Comments:**
___________________________________________
___________________________________________
___________________________________________

**Tester Signature:** _______________ **Date:** ___________
