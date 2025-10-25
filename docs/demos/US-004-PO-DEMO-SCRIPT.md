# US-004 Account Reconciliation - Product Owner Demo Script

**Story:** US-004 - Account Reconciliation
**Phase:** Phase 7 - Final Testing & Documentation
**Task:** 4.47 - Prepare PO Demo
**Date:** October 23, 2025
**Presenter:** ___________________________
**Duration:** 15-20 minutes

---

## Demo Overview

This demo showcases the new Account Reconciliation feature, allowing users to match their account transactions with bank statements to ensure accuracy and detect discrepancies.

**Demo Objectives:**
1. Show the complete reconciliation workflow from start to finish
2. Demonstrate balanced reconciliation (no discrepancy)
3. Demonstrate reconciliation with discrepancy handling
4. Highlight key UX features and visual feedback
5. Show how reconciliation status appears in the transaction list

---

## Pre-Demo Setup

### Environment Setup

**Before the demo begins:**

1. **Clean Database** (or use test database with prepared data)
   ```bash
   cp finance.db finance.db.backup
   # Use demo database: finance_demo.db
   ```

2. **Prepare Demo Account**
   - **Account Name:** "Demo Checking Account"
   - **Account Type:** Checking (Asset)
   - **Opening Balance:** $1,000.00
   - **Currency:** USD

3. **Add Demo Transactions** (see Test Data section below)
   - 10 transactions total
   - Mix of income and expenses
   - Date range: October 1-15, 2025
   - All transactions "Unreconciled" initially

4. **Prepare Fake Bank Statement** (printed or on screen)
   - Statement Date: October 15, 2025
   - Statement Balance: $1,850.00 (for balanced scenario)
   - Lists 8 of the 10 transactions (2 pending)

5. **Application Running**
   - App launched and ready
   - Demo account visible in accounts list
   - Transactions visible in transaction list

### Screenshot Preparation

**Optional: Take these screenshots for documentation:**
- [ ] Main window with demo account selected
- [ ] Edit menu showing "Reconcile Account" option
- [ ] Reconciliation dialog - empty state
- [ ] Reconciliation dialog - with transactions checked
- [ ] Discrepancy indicator - Green (balanced)
- [ ] Discrepancy indicator - Yellow/Red (discrepancy)
- [ ] After reconciliation - transaction list with cleared status

---

## Demo Test Data

### Demo Account Setup

**Account Details:**
```
Name: Demo Checking Account
Type: Checking (Asset)
Subtype: Checking
Balance: $2,000.00 (calculated from transactions)
Currency: USD
Last Reconciled: Never (before first reconciliation)
```

### Transaction List (10 transactions)

**October 2025 Transactions:**

| Date | Description | Category | Amount | Type | Should Clear? |
|------|-------------|----------|--------|------|--------------|
| Oct 1 | Opening Balance Adjustment | Adjustment | +$1,000.00 | Income | ✓ Yes |
| Oct 2 | Grocery Store | Food | -$52.34 | Expense | ✓ Yes |
| Oct 3 | Gas Station | Transportation | -$45.50 | Expense | ✓ Yes |
| Oct 5 | Salary Deposit | Salary | +$2,000.00 | Income | ✓ Yes |
| Oct 7 | Electric Bill | Utilities | -$125.00 | Expense | ✓ Yes |
| Oct 10 | Coffee Shop | Dining | -$15.75 | Expense | ✓ Yes |
| Oct 12 | ATM Withdrawal | Cash | -$60.00 | Expense | ✓ Yes |
| Oct 14 | Online Shopping | Shopping | -$89.99 | Expense | ✓ Yes |
| Oct 15 | Restaurant | Dining | -$42.42 | Expense | ✗ No (pending) |
| Oct 15 | Check #1234 | Check | -$500.00 | Expense | ✗ No (pending) |

**Calculated Balances:**
- **Total of all transactions:** +$2,069.00
- **Total of transactions to clear (8):** +$2,611.42
- **Opening balance:** $1,000.00
- **Expected cleared balance:** $1,000.00 + ($2,069.00 - $542.42 pending) = **$2,526.58**

Wait, let me recalculate to ensure we have a balanced scenario:

**Cleared Transactions (8 transactions):**
```
+ $1,000.00  (Opening Balance Adjustment)
+ $2,000.00  (Salary Deposit)
- $52.34     (Grocery Store)
- $45.50     (Gas Station)
- $125.00    (Electric Bill)
- $15.75     (Coffee Shop)
- $60.00     (ATM Withdrawal)
- $89.99     (Online Shopping)
────────────
= +$2,611.42 (sum of cleared transactions)
```

**For a balanced reconciliation:**
```
Opening Balance: $0.00 (first reconciliation)
+ Cleared Transactions: $2,611.42
= Cleared Balance: $2,611.42
Statement Balance: $2,611.42
Discrepancy: $0.00 ✓
```

**Pending Transactions (2 transactions - won't clear):**
```
- $42.42     (Restaurant - just posted)
- $500.00    (Check #1234 - not cashed yet)
```

### Bank Statement (Mock)

```
═══════════════════════════════════════════════════════════
              DEMO BANK - Monthly Statement
═══════════════════════════════════════════════════════════

Account: Demo Checking Account ***1234
Statement Period: October 1-15, 2025

───────────────────────────────────────────────────────────

Previous Balance (Sep 30):               $0.00

DEPOSITS AND CREDITS:
  Oct 1    Opening Balance Adjustment    +$1,000.00
  Oct 5    Salary Deposit                +$2,000.00
                                          ──────────
  Total Deposits:                         $3,000.00

WITHDRAWALS AND DEBITS:
  Oct 2    Grocery Store                 -$52.34
  Oct 3    Gas Station                   -$45.50
  Oct 7    Electric Bill                 -$125.00
  Oct 10   Coffee Shop                   -$15.75
  Oct 12   ATM Withdrawal                -$60.00
  Oct 14   Online Shopping               -$89.99
                                          ──────────
  Total Withdrawals:                      -$388.58

ENDING BALANCE (Oct 15):                  $2,611.42

───────────────────────────────────────────────────────────
Note: Check #1234 ($500.00) has not cleared yet.
Note: Restaurant charge ($42.42) posted after statement close.
═══════════════════════════════════════════════════════════
```

---

## Demo Script

### Introduction (1 minute)

**Presenter says:**

> "Good morning/afternoon everyone! Today I'm excited to demo our new **Account Reconciliation** feature, which is story US-004. This feature allows users to match their transactions in the app with their bank statements to ensure accuracy and catch errors or fraud."

> "Reconciliation is a core accounting practice - think of it as 'balancing your checkbook' in the digital age. Let's see how easy we've made this process!"

**Show:** Main window with demo account selected

---

### Part 1: Opening the Reconciliation Dialog (2 minutes)

**Presenter says:**

> "Let's start by reconciling our Demo Checking Account. I'll show you two ways to open the reconciliation dialog."

**Demo Step 1: Menu Access**

1. **Select** the "Demo Checking Account" in the accounts list
2. **Click** Edit → Reconcile Account... from the menu
3. **Dialog opens**

**Presenter says:**

> "As you can see, the dialog opens with a clear title showing which account we're reconciling."

**Close dialog**

**Demo Step 2: Keyboard Shortcut**

1. **Press** Ctrl+R
2. **Dialog opens instantly**

**Presenter says:**

> "For power users, we have a keyboard shortcut: Ctrl+R. Much faster!"

**Show:** Dialog is now open for the demo

---

### Part 2: Statement Details Section (2 minutes)

**Presenter says:**

> "The reconciliation dialog has three main sections. Let's start with **Statement Details** at the top."

**Point to Statement Details section**

**Demo Step 3: Enter Statement Date**

1. **Click** on the Statement Date calendar icon
2. **Select** October 15, 2025
3. **Date appears** in the field

**Presenter says:**

> "First, I'll enter the statement date from my bank statement - October 15th."

**Demo Step 4: Enter Statement Balance**

1. **Click** in the Statement Balance field
2. **Type:** 2611.42
3. **Tab** to next field

**Presenter says:**

> "Next, I'll enter the ending balance from my bank statement: $2,611.42."

**Point to Opening Balance (read-only)**

**Presenter says:**

> "Notice the **Opening Balance** field shows $0.00. That's because this is our first reconciliation for this account. In future reconciliations, this would show the previous statement's ending balance."

---

### Part 3: Transaction List & Marking Cleared (3 minutes)

**Presenter says:**

> "Now for the main event - matching transactions! The middle section shows all **unreconciled transactions** for this account."

**Point to transaction table**

**Demo Step 5: Mark Transactions as Cleared**

**Presenter says:**

> "I'll go through my bank statement and check off each transaction that appears on it. Let me work chronologically..."

**Check transactions one by one while narrating:**

1. ✓ **Check** "Opening Balance Adjustment ($1,000.00)" - "This appears on the statement..."
2. ✓ **Check** "Grocery Store (-$52.34)" - "Yes, this one too..."
3. ✓ **Check** "Gas Station (-$45.50)" - "Yep..."
4. ✓ **Check** "Salary Deposit ($2,000.00)" - "My paycheck came through..."
5. ✓ **Check** "Electric Bill (-$125.00)" - "Electric bill paid..."
6. ✓ **Check** "Coffee Shop (-$15.75)" - "Coffee, of course..."
7. ✓ **Check** "ATM Withdrawal (-$60.00)" - "ATM cash..."
8. ✓ **Check** "Online Shopping (-$89.99)" - "And my online order..."

**Leave unchecked:**
- ☐ "Restaurant (-$42.42)" - "This one isn't on the statement yet - posted after closing"
- ☐ "Check #1234 (-$500.00)" - "And this check hasn't been cashed yet"

**Presenter says:**

> "Notice I'm **not checking** these last two transactions. The restaurant charge posted after the statement date, and the check hasn't been cashed yet. They'll appear on next month's statement."

---

### Part 4: Summary & Discrepancy Indicator (3 minutes)

**Presenter says:**

> "Now let's look at the **Summary section** at the bottom. This is where the magic happens!"

**Point to Summary section**

**Show the summary values:**

```
Opening Balance:        $0.00
+ Cleared Transactions: +$2,611.42
= Cleared Balance:      $2,611.42

Statement Balance:      $2,611.42
Discrepancy:            $0.00  ✓ Balanced
```

**Presenter says:**

> "The app automatically calculates:
> - **Opening Balance**: $0 (first reconciliation)
> - **Cleared Transactions**: The sum of all transactions I checked: +$2,611.42
> - **Cleared Balance**: Opening + Cleared = $2,611.42
> - **Statement Balance**: What I entered from the bank: $2,611.42
> - **Discrepancy**: The difference: $0.00"

**Point to green discrepancy indicator**

**Presenter says:**

> "See this **green** indicator? That means we're perfectly balanced! Everything matches. This is what we want to see."

**Presenter asks:**

> "But what if there's a discrepancy? Let me show you..."

---

### Part 5: Demonstrating Discrepancy Handling (3 minutes)

**Demo Step 6: Create a Discrepancy (uncheck one transaction)**

1. **Uncheck** one transaction (e.g., "Coffee Shop (-$15.75)")
2. **Watch** summary update

**New summary:**

```
Cleared Balance:        $2,627.17  (was $2,611.42 + $15.75)
Statement Balance:      $2,611.42
Discrepancy:            -$15.75  ⚠ Difference
```

**Presenter says:**

> "Uh oh! Now we have a discrepancy of -$15.75. The app is showing me in **yellow** that there's a small difference."

**Point to yellow/orange discrepancy indicator**

**Presenter says:**

> "This could mean:
> - I forgot to check a transaction
> - There's a bank fee I haven't recorded
> - I made a data entry error"

**Demo Step 7: Add a Note**

1. **Click** in the Notes field
2. **Type:** "Missing coffee shop transaction - forgot to check it"
3. **Show** the note

**Presenter says:**

> "I can add a **note** explaining the discrepancy. This helps me remember what happened when I review my reconciliation history later."

**Demo Step 8: Fix the Discrepancy**

1. **Re-check** "Coffee Shop" transaction
2. **Watch** summary update back to $0.00 discrepancy
3. **Green indicator** returns

**Presenter says:**

> "Ah, there we go! I found the issue - I forgot to check the coffee shop transaction. Now we're balanced again."

**Clear the notes field**

---

### Part 6: Completing the Reconciliation (2 minutes)

**Presenter says:**

> "Now that everything is balanced, let's complete the reconciliation."

**Demo Step 9: Complete Reconciliation**

1. **Click** "Complete Reconciliation" button
2. **Success message** appears (if dialog shows it)
3. **Dialog closes**

**Presenter says:**

> "The reconciliation is complete! Let me show you what changed..."

---

### Part 7: Viewing Reconciliation Results (2 minutes)

**Show:** Main window with transaction list

**Presenter says:**

> "Look at the transaction list now. Notice the **'Reconciliation Status'** column?"

**Point to status column**

**Show cleared transactions:**
- ✓ "Opening Balance Adjustment" - **Cleared** (Oct 15)
- ✓ "Grocery Store" - **Cleared** (Oct 15)
- ✓ "Salary Deposit" - **Cleared** (Oct 15)
- (etc... all 8 cleared transactions)

**Show unreconciled transactions:**
- ☐ "Restaurant" - **Unreconciled**
- ☐ "Check #1234" - **Unreconciled**

**Presenter says:**

> "The transactions I checked are now marked as **'Cleared'** with the reconciliation date. The two transactions I didn't check remain **'Unreconciled'** - they'll be reconciled next month when they appear on the next statement."

**Point to Account Details (if visible)**

**Presenter says:**

> "And in the account details, we can see the **'Last Reconciled'** field now shows October 15, 2025."

**Show status bar (if visible)**

**Presenter says:**

> "The status bar shows a success message: 'Reconciliation #1 completed successfully.'"

---

### Part 8: Demonstrating Discrepancy Workflow (Optional - 3 minutes)

**Presenter says:**

> "Let me quickly demonstrate what happens if we complete a reconciliation **with a discrepancy**."

**Demo Step 10: Start Another Reconciliation (Optional)**

1. **Add** a new transaction: "Bank Fee" -$5.00 (not reconciled)
2. **Open** reconciliation dialog again (Ctrl+R)
3. **Enter** statement date: October 16, 2025
4. **Enter** statement balance: Same as before (intentionally create discrepancy)
5. **Don't check** the new "Bank Fee" transaction
6. **Show** red discrepancy: $5.00

**Presenter says:**

> "Now we have a larger discrepancy - $5.00. The indicator turned **red** because it's more significant."

**Demo Step 11: Complete with Discrepancy**

1. **Add note:** "Bank fee of $5.00 not yet recorded - will add after reconciliation"
2. **Click** "Complete Reconciliation"
3. **Confirmation dialog** appears: "There is a discrepancy of $5.00. Are you sure?"
4. **Click** "Yes" to confirm

**Presenter says:**

> "The app asks for confirmation before completing with a discrepancy. This prevents accidental completion when there might be an error. I can click 'Yes' to proceed or 'No' to go back and investigate."

**Click "No" to cancel (don't actually complete)**

**Presenter says:**

> "For this demo, I'll cancel and not actually complete this one."

---

### Conclusion & Q&A (2 minutes)

**Presenter says:**

> "So to recap, the Account Reconciliation feature provides:
>
> ✅ **Easy-to-use dialog** with clear sections
> ✅ **Automatic calculations** - no manual math needed
> ✅ **Color-coded discrepancy indicators** - green, yellow, red
> ✅ **Notes field** for documenting discrepancies
> ✅ **Confirmation prompts** for discrepancies
> ✅ **Clear reconciliation status** in transaction list
> ✅ **Keyboard shortcuts** for efficiency (Ctrl+R)
>
> This feature helps users:
> - Catch errors early
> - Detect fraudulent activity
> - Maintain accurate financial records
> - Gain peace of mind about their finances"

**Presenter says:**

> "Any questions about the reconciliation feature?"

**[Q&A session]**

---

## Demo Tips & Best Practices

### Presentation Tips

**Do:**
- ✅ Speak slowly and clearly
- ✅ Explain each step as you perform it
- ✅ Point to UI elements as you discuss them
- ✅ Emphasize the color coding (green/yellow/red)
- ✅ Show both success and error scenarios
- ✅ Pause for questions throughout

**Don't:**
- ❌ Rush through the demo
- ❌ Assume everyone understands accounting terms
- ❌ Skip the explanation of discrepancy colors
- ❌ Forget to show the end result (cleared status)
- ❌ Use technical jargon without explanation

### Common Questions & Answers

**Q: Can users undo a reconciliation?**
A: Not currently. Once completed, a reconciliation is permanent. However, users can run a new reconciliation to correct any issues. Future versions may support reconciliation reversal.

**Q: What happens if users complete with a large discrepancy?**
A: The app shows a confirmation dialog asking "Are you sure?" Users can choose to go back and investigate or proceed with the discrepancy. The discrepancy is recorded in the reconciliation record.

**Q: Can users reconcile multiple accounts at once?**
A: No, reconciliation is done one account at a time. This ensures accuracy and prevents confusion.

**Q: How often should users reconcile?**
A: We recommend monthly reconciliation when bank statements arrive. Some users may prefer weekly for cash accounts with frequent transactions.

**Q: Does this work with credit card accounts?**
A: Yes! The reconciliation feature works with all account types: checking, savings, credit cards, and cash.

**Q: What if a transaction is missing from the app?**
A: Users should cancel the reconciliation, add the missing transaction to the app, then start a new reconciliation.

**Q: Can users see reconciliation history?**
A: This feature is planned for a future release. Currently, users can see which transactions are cleared and when, but a dedicated reconciliation history view is not yet available.

---

## Post-Demo Cleanup

**After the demo:**

1. **Restore original database** (if using demo database)
   ```bash
   mv finance.db.backup finance.db
   ```

2. **Delete demo account and transactions** (if keeping database)

3. **Save screenshots** to documentation folder
   - `docs/screenshots/reconciliation/`

4. **Collect feedback** from attendees
   - Note any questions asked
   - Record suggestions for improvements
   - Document any bugs discovered

---

## Demo Variations

### Variation A: Quick Demo (5 minutes)

**For time-constrained demos:**
1. Show opening dialog (1 min)
2. Mark 3-4 transactions as cleared (1 min)
3. Show green balanced indicator (1 min)
4. Complete reconciliation (1 min)
5. Show cleared status in transaction list (1 min)

### Variation B: Deep Dive Demo (30 minutes)

**For technical stakeholders:**
- Include detailed explanation of reconciliation concepts (opening balance, cleared balance, etc.)
- Show reconciliation history (if available)
- Demonstrate edge cases (empty transaction list, all transactions cleared)
- Discuss performance (tested with 1000+ transactions)
- Show error handling (concurrent reconciliation, validation errors)
- Review code quality and test coverage

### Variation C: User-Focused Demo (15 minutes)

**For end users:**
- Focus on "Why reconcile?" benefits
- Show real-world example with actual bank statement
- Emphasize ease of use and visual feedback
- Demonstrate troubleshooting common discrepancies
- Provide tips for monthly reconciliation workflow

---

## Appendix: Demo Database Script

**Optional: Script to create demo database with test data**

```sql
-- Create demo account
INSERT INTO accounts (name, account_type, account_subtype, balance, normal_balance, currency)
VALUES ('Demo Checking Account', 'ASSET', 'CHECKING', 2000.00, 'DEBIT', 'USD');

-- Get account ID (assume it's 1 for this example)
-- In practice, retrieve the last inserted ID

-- Create demo transactions
INSERT INTO transactions (account_id, date, description, category, amount, type, reconciliation_status)
VALUES
  (1, '2025-10-01', 'Opening Balance Adjustment', 'Adjustment', 1000.00, 'income', 'unreconciled'),
  (1, '2025-10-02', 'Grocery Store', 'Food', -52.34, 'expense', 'unreconciled'),
  (1, '2025-10-03', 'Gas Station', 'Transportation', -45.50, 'expense', 'unreconciled'),
  (1, '2025-10-05', 'Salary Deposit', 'Salary', 2000.00, 'income', 'unreconciled'),
  (1, '2025-10-07', 'Electric Bill', 'Utilities', -125.00, 'expense', 'unreconciled'),
  (1, '2025-10-10', 'Coffee Shop', 'Dining', -15.75, 'expense', 'unreconciled'),
  (1, '2025-10-12', 'ATM Withdrawal', 'Cash', -60.00, 'expense', 'unreconciled'),
  (1, '2025-10-14', 'Online Shopping', 'Shopping', -89.99, 'expense', 'unreconciled'),
  (1, '2025-10-15', 'Restaurant', 'Dining', -42.42, 'expense', 'unreconciled'),
  (1, '2025-10-15', 'Check #1234', 'Check', -500.00, 'expense', 'unreconciled');
```

---

## Appendix: Mock Bank Statement (Printable)

**For physical demo:**

Print this statement and use it during the demo to show matching transactions:

```
═══════════════════════════════════════════════════════════════════════════
                          DEMO BANK
                     Your Trusted Financial Partner
═══════════════════════════════════════════════════════════════════════════

ACCOUNT STATEMENT

Account Holder: Demo User
Account Number: ****1234
Account Type: Checking
Statement Period: October 1-15, 2025
Statement Date: October 15, 2025

───────────────────────────────────────────────────────────────────────────

ACCOUNT SUMMARY

Previous Balance (September 30, 2025):                           $0.00

Deposits and Other Credits:                                  $3,000.00
Withdrawals and Other Debits:                                 -$388.58

ENDING BALANCE (October 15, 2025):                           $2,611.42

───────────────────────────────────────────────────────────────────────────

TRANSACTION DETAILS

Date       Description                                    Amount
───────────────────────────────────────────────────────────────────────────

DEPOSITS AND CREDITS:
Oct 1      Opening Balance Adjustment                  +$1,000.00
Oct 5      Direct Deposit - SALARY                     +$2,000.00
                                                        ──────────
           Total Deposits:                             +$3,000.00

WITHDRAWALS AND DEBITS:
Oct 2      Debit Card - GROCERY STORE                     -$52.34
Oct 3      Debit Card - GAS STATION                       -$45.50
Oct 7      Online Payment - ELECTRIC COMPANY             -$125.00
Oct 10     Debit Card - COFFEE SHOP                       -$15.75
Oct 12     ATM Withdrawal - MAIN ST BRANCH                -$60.00
Oct 14     Debit Card - ONLINE RETAILER                   -$89.99
                                                        ──────────
           Total Withdrawals:                            -$388.58

───────────────────────────────────────────────────────────────────────────

PENDING TRANSACTIONS (Not included in ending balance):

Oct 15     Debit Card - RESTAURANT                        -$42.42
Oct 15     Check #1234 (Not yet cashed)                  -$500.00

───────────────────────────────────────────────────────────────────────────

IMPORTANT NOTICES:
- Your account is in good standing
- No fees charged this statement period
- Next statement date: November 15, 2025

For questions, contact us at: 1-800-DEMO-BANK
Online banking: www.demobank.com

═══════════════════════════════════════════════════════════════════════════
                        End of Statement
═══════════════════════════════════════════════════════════════════════════
```

---

**Demo Script Version:** 1.0
**Last Updated:** October 23, 2025
**Story:** US-004 Account Reconciliation
**Prepared By:** Frontend Developer
