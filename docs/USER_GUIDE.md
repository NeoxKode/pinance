# Personal Finance Manager - User Guide

**Version:** 2.1.0
**Last Updated:** October 23, 2025
**Status:** ✅ Complete

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Split Transactions](#split-transactions)
   - [What are Split Transactions?](#what-are-split-transactions)
   - [When to Use Split Transactions](#when-to-use-split-transactions)
   - [How to Create a Split Transaction](#how-to-create-a-split-transaction)
   - [Editing Split Transactions](#editing-split-transactions)
   - [Tips and Best Practices](#tips-and-best-practices)
   - [Troubleshooting](#troubleshooting)
3. [Account Reconciliation](#account-reconciliation)
   - [What is Account Reconciliation?](#what-is-account-reconciliation)
   - [Why Reconcile Your Accounts?](#why-reconcile-your-accounts)
   - [When to Reconcile](#when-to-reconcile)
   - [How to Reconcile Your Account](#how-to-reconcile-your-account)
   - [Understanding Reconciliation Concepts](#understanding-reconciliation-concepts)
   - [Handling Discrepancies](#handling-discrepancies)
   - [Reconciliation Tips & Best Practices](#reconciliation-tips--best-practices)
   - [Troubleshooting Reconciliation](#troubleshooting-reconciliation)
   - [Frequently Asked Questions](#frequently-asked-questions)
4. [Advanced Features](#advanced-features)

---

## Introduction

Welcome to the Personal Finance Manager User Guide! This guide will help you make the most of the application's features to track and manage your personal finances effectively.

This guide is organized by feature, with detailed instructions and examples for each.

---

## Split Transactions

### What are Split Transactions?

Split transactions allow you to divide a single transaction across multiple spending categories. This is useful when a single purchase or payment covers multiple types of expenses.

**Example Scenarios:**

1. **Grocery Shopping**
   - Total: $150.00
   - Splits:
     - $100.00 → Groceries (Food)
     - $30.00 → Household Items (Cleaning supplies)
     - $20.00 → Personal Care (Toiletries)

2. **Paycheck Deposit**
   - Total: $3,000.00
   - Splits:
     - $2,400.00 → Salary (Regular pay)
     - $400.00 → Bonus (Performance bonus)
     - $200.00 → Reimbursement (Travel expenses)

3. **Walmart Shopping**
   - Total: $85.50
   - Splits:
     - $45.00 → Groceries
     - $25.00 → Electronics (USB cable)
     - $15.50 → Clothing (Socks)

### When to Use Split Transactions

Use split transactions when:

✅ **You should split when:**
- A single receipt covers multiple expense categories
- You want detailed spending analysis by category
- You need to track specific subcategories within a transaction
- You're categorizing a paycheck with multiple income sources

❌ **You probably don't need to split when:**
- All items belong to the same category (e.g., all groceries)
- The transaction is simple and single-purpose
- You don't need detailed category tracking for that purchase

### How to Create a Split Transaction

#### Step 1: Open the Transaction Dialog

1. Click the **"Add Transaction"** button in the main window
2. Or: Right-click on the transaction list and select **"Add Transaction"**

#### Step 2: Enter Basic Transaction Information

Fill in the basic transaction details:

- **Account**: Select the account (e.g., "Checking Account")
- **Date**: Choose the transaction date
- **Amount**: Enter the **total transaction amount**
- **Description**: Add a description (e.g., "Walmart Shopping")
- **Category**: Select a general category (will be overridden by splits)

**Important**: Enter the total transaction amount here. You'll divide it into splits in the next step.

#### Step 3: Click the "Split" Button

1. Look for the **"Split"** button in the transaction dialog
2. Click it to open the **Split Transaction Dialog**

#### Step 4: Add Your Splits

The Split Transaction Dialog uses a **sum-driven approach** (like HomeBank):

**How it works:**
1. **Start with an empty splits table**
2. **Add splits one by one** - the "Sum" updates automatically
3. **The total grows as you add splits** - no pre-filled target
4. **The sum should equal your transaction amount when done**

**To add a split:**

1. **Click the "+" (Add) button** to create a new split row
2. **Fill in the split details:**
   - **Category**: Select the category (e.g., "Groceries")
   - **Memo**: Optional note for this split (e.g., "Food items")
   - **Amount**: Enter the amount for this category (e.g., "100.00")
3. **Watch the "Sum" update** at the bottom of the dialog
4. **Repeat** until you've added all splits
5. **Verify the sum equals your transaction amount**

**Example:**

```
Transaction Amount: $150.00

Split 1:
  Category: Groceries
  Memo: Food items
  Amount: $100.00

  Sum of splits: ₱100.00

Split 2:
  Category: Household
  Memo: Cleaning supplies
  Amount: $30.00

  Sum of splits: ₱130.00

Split 3:
  Category: Personal Care
  Memo: Toiletries
  Amount: $20.00

  Sum of splits: ₱150.00  ✅ Matches transaction amount!
```

#### Step 5: Verify and Save

1. **Check the "Sum of splits" indicator** at the bottom
   - It should display: `Sum of splits: ₱150.00`
2. **Verify the sum matches your transaction amount exactly**
3. If the amounts match, click **"OK"** to save
4. If they don't match, adjust your split amounts

**What happens when you save:**
- ✅ The transaction is marked as a split transaction
- ✅ Each split is saved with its category and amount
- ✅ Journal entries are created for proper accounting
- ✅ The transaction appears in your transaction list

### Editing Split Transactions

#### How to Edit Existing Splits

1. **Find the split transaction** in your transaction list
   - Split transactions are marked with a special indicator
2. **Double-click the transaction** to open it
3. **Click the "Split" button** to open the splits
4. **Modify your splits:**
   - Add new splits with the "+" button
   - Remove splits with the "-" button
   - Edit existing split amounts and categories
5. **Verify the sum still matches** the transaction amount
6. **Click "OK"** to save changes

**Important**: When editing splits, you must ensure the sum of splits still equals the transaction amount.

#### How to Remove Splits (Convert to Regular Transaction)

To convert a split transaction back to a regular transaction:

1. **Open the split transaction**
2. **Click the "Split" button**
3. **Remove all splits** using the "-" button
4. **Save the transaction**
5. The transaction will become a regular (non-split) transaction

### Tips and Best Practices

#### ✅ Best Practices

1. **Use Meaningful Memos**
   - Good: "Food items" (clear and specific)
   - Bad: "Stuff" (too vague)

2. **Keep Categories Consistent**
   - Use the same category names for similar items
   - This makes reports and analysis more accurate

3. **Verify Amounts Before Saving**
   - Always check the "Sum of splits" matches the transaction amount
   - Double-check your math to avoid errors

4. **Split at the Right Level**
   - Don't over-split (too many tiny categories)
   - Don't under-split (losing useful detail)
   - Find a balance that works for your tracking needs

5. **Use Splits for Paychecks**
   - Split gross pay into salary, bonus, reimbursements, etc.
   - This gives you detailed income tracking

#### 💡 Pro Tips

**Tip 1: Quick Split Entry**
- Have your receipt ready when entering splits
- Enter all amounts first, then add memos
- This speeds up data entry

**Tip 2: Common Split Templates**
- For recurring split transactions (like paychecks), write down the split structure
- Keep a note of common split patterns for reference
- Future versions will support split templates!

**Tip 3: Category Setup**
- Set up your categories before creating splits
- Link categories to accounts for proper journal entries
- Use Settings → Categories to manage your categories

**Tip 4: Handling Partial Amounts**
- If you don't know exact split amounts, estimate and add a "Misc" split for the remainder
- You can always edit the split later when you have exact amounts

### Troubleshooting

#### Error: "Splits must equal transaction amount"

**Problem**: The sum of your splits doesn't match the transaction amount.

**Solutions**:
1. **Check your math**: Add up the split amounts manually
2. **Look for decimal errors**: Make sure amounts are entered correctly (e.g., 20.00 not 2.00)
3. **Count all splits**: Make sure you haven't missed any categories
4. **Use a calculator**: Verify the total on paper or calculator

**Example**:
```
Transaction: $100.00
Split 1: $60.00
Split 2: $30.00
Split 3: $5.00

Sum: $95.00 ❌ ERROR - Missing $5.00!
```

**Fix**: Adjust Split 3 to $10.00 or add another split for the remaining $5.00

#### Error: "At least 2 splits required"

**Problem**: You're trying to create a split transaction with only 1 split.

**Solutions**:
1. **Add another split**: Split transactions need at least 2 categories
2. **Or don't split**: If you only have one category, don't use a split transaction

#### Error: "Category does not have a linked account"

**Problem**: The category you selected isn't properly set up for split transactions.

**Solutions**:
1. **Go to Settings → Categories**
2. **Select the category** and link it to an account
3. **Save the category settings**
4. **Return to the split transaction** and try again

If you're not sure which account to link, ask your system administrator or check the documentation.

#### Split Button Not Working

**Problem**: Clicking the "Split" button doesn't open the dialog.

**Solutions**:
1. **Make sure you've entered the transaction amount** - The amount is required first
2. **Check for error messages** - There might be a validation error
3. **Try saving the base transaction first** - Then edit it to add splits
4. **Restart the application** - If the button is completely unresponsive

#### Split Dialog Won't Save

**Problem**: Clicking "OK" doesn't save the splits.

**Solutions**:
1. **Check the sum** - Make sure it matches the transaction amount exactly
2. **Verify all splits have categories** - Empty category fields will prevent saving
3. **Check for negative amounts** - All split amounts must be positive
4. **Look for error messages** - The dialog will show validation errors

#### Lost Split Data

**Problem**: Your splits disappeared after editing.

**Solutions**:
1. **Check if you saved** - Did you click "OK" or "Cancel"?
2. **Look for the transaction** - Make sure you're looking at the right transaction
3. **Check the database** - Splits are stored permanently unless deleted
4. **Restore from backup** - If you have database backups, you can restore

**Prevention**: Always click "OK" to save changes, not "Cancel"!

---

## Account Reconciliation

### What is Account Reconciliation?

**Account reconciliation** is the process of matching your account transactions in the app with your bank or credit card statement to ensure accuracy and detect discrepancies.

Think of it as "balancing your checkbook" - you're verifying that what the app shows matches what your bank says you have.

**Real-World Analogy:**
Imagine you track your piggy bank with pen and paper. Reconciliation is when you:
1. Count the actual cash in the piggy bank ($52.35)
2. Check your written record ($52.35)
3. Verify they match ✓
4. Mark that date as "reconciled"

If they don't match, you know something's wrong - maybe you forgot to write down a transaction, or wrote the wrong amount.

### Why Reconcile Your Accounts?

Reconciling your accounts regularly provides these important benefits:

#### ✅ **1. Catch Errors Early**
- Find data entry mistakes (typed $50 instead of $500)
- Detect missing transactions (forgot to record ATM withdrawal)
- Identify duplicate transactions (entered same transaction twice)

#### ✅ **2. Detect Fraudulent Activity**
- Spot unauthorized charges on your credit card
- Identify suspicious withdrawals from your bank account
- Catch merchant errors (charged twice for same purchase)

#### ✅ **3. Maintain Accurate Records**
- Ensure your app balance matches your actual bank balance
- Keep your financial data trustworthy
- Make better financial decisions with accurate data

#### ✅ **4. Peace of Mind**
- Know your finances are under control
- Sleep better knowing everything is accounted for
- Reduce financial stress and uncertainty

### When to Reconcile

**Best Practice: Reconcile Monthly**

Reconcile your accounts once per month when you receive your bank or credit card statement:

- **Checking Account**: Monthly (when statement arrives)
- **Savings Account**: Monthly or quarterly
- **Credit Card**: Monthly (after statement closing date)
- **Cash Account**: Weekly or monthly (more frequent due to cash transactions)

**Recommended Schedule:**

| Account Type | Frequency | Trigger |
|-------------|-----------|---------|
| Checking | Monthly | Bank statement received |
| Savings | Monthly | Bank statement received |
| Credit Card | Monthly | Statement closing date |
| Cash | Weekly | End of week |
| Investment | Quarterly | Quarterly statement |

**Pro Tip**: Set up calendar reminders for reconciliation day!

### How to Reconcile Your Account

Follow these step-by-step instructions to reconcile your account:

#### **Step 1: Gather Your Bank Statement**

Before starting, you'll need:

- 📄 Your latest bank or credit card statement (paper or online)
- 💻 The Personal Finance Manager app open
- ☕ A few minutes of quiet time

**What to look for on your statement:**
- **Statement Date**: The closing date (e.g., "October 15, 2025")
- **Ending Balance**: The final balance on the statement (e.g., "$1,245.67")
- **Transaction List**: All transactions during the statement period

#### **Step 2: Open the Reconciliation Dialog**

There are two ways to open the reconciliation dialog:

**Method 1: Using the Menu**
1. **Select your account** in the accounts list on the left
2. Click **Edit → Reconcile Account...** from the menu bar
3. The reconciliation dialog will open

**Method 2: Using Keyboard Shortcut**
1. **Select your account** in the accounts list
2. Press **Ctrl+R** on your keyboard
3. The reconciliation dialog will open instantly

![Screenshot: Reconciliation Menu](screenshots/reconciliation-menu.png)
*Figure 1: Opening reconciliation from the Edit menu*

#### **Step 3: Enter Statement Details**

The reconciliation dialog will appear with several sections. Start by entering your statement details:

1. **Statement Date**: Click the calendar icon and select your statement's ending date
   - Example: October 15, 2025

2. **Statement Balance**: Enter the ending balance from your bank statement
   - Example: $1,245.67
   - **Important**: Enter the exact amount shown on your statement

3. **Opening Balance** (read-only): This shows your last reconciled balance
   - For first-time reconciliation, this will be $0.00
   - For subsequent reconciliations, this shows the previous statement balance

![Screenshot: Statement Details Section](screenshots/statement-details.png)
*Figure 2: Entering statement date and balance*

#### **Step 4: Mark Cleared Transactions**

Now you'll match your transactions with those on your bank statement:

The dialog shows a table with all **unreconciled transactions** for this account:

| ✓ | Date | Description | Amount | Type |
|---|------|-------------|--------|------|
| ☐ | Oct 2 | Grocery Store | -$52.34 | Expense |
| ☐ | Oct 5 | Salary Deposit | +$2,000.00 | Income |
| ☐ | Oct 8 | Electric Bill | -$125.00 | Expense |
| ☐ | Oct 12 | ATM Withdrawal | -$60.00 | Expense |
| ☐ | Oct 15 | Gas Station | -$45.50 | Expense |

**How to mark transactions:**

1. **Look at your bank statement** and find the first transaction
2. **Find the matching transaction** in the dialog's table
3. **Click the checkbox** (✓) next to that transaction
4. **Repeat** for each transaction on your statement

**Pro Tip**: Work chronologically from oldest to newest transaction. Check them off one by one as you verify them against your statement.

**What to verify:**
- ✅ Date matches (or is close - some banks delay posting)
- ✅ Amount matches exactly
- ✅ Description is recognizable (might differ slightly)

![Screenshot: Transaction List with Checkboxes](screenshots/transaction-checkboxes.png)
*Figure 3: Marking transactions as cleared*

#### **Step 5: Watch the Summary Update**

As you check transactions, the **Summary section** at the bottom updates automatically:

```
┌─────────────────────────────────────────────────┐
│ RECONCILIATION SUMMARY                          │
├─────────────────────────────────────────────────┤
│ Opening Balance:           $1,000.00            │
│ + Cleared Transactions:    +$245.67             │
│ = Cleared Balance:         $1,245.67  ✓         │
│                                                  │
│ Statement Balance:         $1,245.67            │
│ Discrepancy:               $0.00     ✓ Balanced │
└─────────────────────────────────────────────────┘
```

**Understanding the summary:**

- **Opening Balance**: Starting point (from last reconciliation)
- **+ Cleared Transactions**: Sum of transactions you checked
- **= Cleared Balance**: Opening + Cleared (calculated)
- **Statement Balance**: What your bank statement says
- **Discrepancy**: Difference between Cleared Balance and Statement Balance

**Goal**: Get the discrepancy to $0.00 (balanced)!

#### **Step 6: Handle the Discrepancy**

The discrepancy indicator will change color based on the difference:

##### 🟢 **GREEN - Perfectly Balanced ($0.00)**

```
Discrepancy: $0.00  ✓ Balanced
```

**Meaning**: Your cleared transactions match your statement balance exactly! 🎉

**What to do**: Click "Complete Reconciliation" to finish!

##### 🟡 **YELLOW - Minor Discrepancy ($0.01 - $10.00)**

```
Discrepancy: $2.50  ⚠ Minor difference
```

**Meaning**: Small difference, possibly due to:
- Bank fees you haven't recorded yet
- Interest you haven't recorded yet
- Rounding differences
- Small transaction you missed

**What to do**:
1. Check for small bank fees or interest on your statement
2. Look for missing small transactions
3. If you can't find the difference, add a note explaining it
4. Click "Complete Reconciliation" to proceed

##### 🔴 **RED - Major Discrepancy (> $10.00)**

```
Discrepancy: $125.00  ❌ Significant difference
```

**Meaning**: Large difference that needs investigation.

**What to do**:
1. **Don't complete yet!** Find the problem first
2. **Common causes:**
   - Missing transaction (forgot to record something)
   - Wrong amount entered (typo)
   - Duplicate transaction (entered twice)
   - Transaction on statement you didn't know about
3. **See "Handling Discrepancies" section below** for detailed troubleshooting

#### **Step 7: Add Notes (If Discrepancy Exists)**

If you have a discrepancy and know why, add an explanation in the **Notes** field:

**Good note examples:**
- "Bank fee of $5.00 not yet recorded - will add after reconciliation"
- "Interest of $2.35 earned this month - will record separately"
- "ATM fee of $3.00 I wasn't aware of"

**Why add notes?**
- Helps you remember why there was a discrepancy
- Useful for future reference
- Good documentation practice

![Screenshot: Notes Field](screenshots/notes-field.png)
*Figure 4: Adding notes to explain discrepancy*

#### **Step 8: Complete the Reconciliation**

When you're ready to finish:

1. **Click the "Complete Reconciliation" button**

2. **If there's a discrepancy**, a confirmation dialog will appear:
   ```
   ⚠ There is a discrepancy of $5.00.

   Are you sure you want to complete this reconciliation?

   [No] [Yes]
   ```

   - Click **"No"** to go back and investigate further
   - Click **"Yes"** to complete despite the discrepancy

3. **Success!** You'll see a confirmation message:
   ```
   ✓ Reconciliation #47 completed successfully
   ```

4. The dialog will close and return you to the main window

#### **Step 9: Verify the Results**

After reconciliation, check that everything updated correctly:

**In the Transactions List:**
- ✓ Cleared transactions now show a **"Cleared"** status indicator
- ✓ Or a checkmark (✓) appears in the status column
- ✓ Reconciled date is displayed

**In the Account Details:**
- ✓ "Last Reconciled" field shows today's date (or statement date)
- ✓ Account balance remains accurate

**Status Bar:**
- ✓ Success message visible: "Reconciliation #47 completed successfully"

![Screenshot: After Reconciliation](screenshots/after-reconciliation.png)
*Figure 5: Transaction list showing cleared status*

### Understanding Reconciliation Concepts

To become a reconciliation pro, let's clarify some key concepts:

#### **Opening Balance**

The **opening balance** is your starting point for this reconciliation - it's the ending balance from your last reconciliation.

**Examples:**

**First Reconciliation Ever:**
```
Opening Balance: $0.00

(You're starting from the beginning, so there's no previous reconciliation)
```

**Subsequent Reconciliation:**
```
Last month's statement balance: $1,000.00
Opening Balance (this reconciliation): $1,000.00

(This reconciliation starts where the last one ended)
```

**Why it matters:** The opening balance ensures continuity between reconciliations.

#### **Cleared Transactions**

A transaction is **"cleared"** when it appears on your bank statement and you've verified it.

**Transaction Lifecycle:**

1. **Unreconciled** (initial state)
   - You entered the transaction in the app
   - It hasn't been reconciled yet
   - Status: "Unreconciled"

2. **Cleared** (checked during reconciliation)
   - You found it on your bank statement
   - You checked the ✓ checkbox
   - Status: "Cleared"

3. **After Reconciliation Complete**
   - Transaction remains "Cleared" permanently
   - Shows reconciled date
   - Won't appear in future reconciliations

**Visual Example:**

```
Before Reconciliation:
┌────────────────────────────────────────┐
│ Oct 2 | Grocery Store | -$52.34 | 🔲   │ Unreconciled
│ Oct 5 | Salary       | +$2000   | 🔲   │ Unreconciled
└────────────────────────────────────────┘

During Reconciliation (checked):
┌────────────────────────────────────────┐
│ Oct 2 | Grocery Store | -$52.34 | ✅   │ Clearing...
│ Oct 5 | Salary       | +$2000   | ✅   │ Clearing...
└────────────────────────────────────────┘

After Reconciliation Complete:
┌────────────────────────────────────────┐
│ Oct 2 | Grocery Store | -$52.34 | ✓    │ Cleared (Oct 15)
│ Oct 5 | Salary       | +$2000   | ✓    │ Cleared (Oct 15)
└────────────────────────────────────────┘
```

#### **Cleared Balance**

The **cleared balance** is calculated as:

```
Cleared Balance = Opening Balance + Sum of Cleared Transactions
```

**Example:**

```
Opening Balance:        $1,000.00

Cleared Transactions:
  + Salary              +$2,000.00
  - Grocery Store       -$52.34
  - Electric Bill       -$125.00
  - ATM Withdrawal      -$60.00
  - Gas Station         -$45.50
                        ──────────
  Sum of Cleared:       +$1,717.16

Cleared Balance:        $1,000.00 + $1,717.16 = $2,717.16
```

**This should match your statement balance!**

#### **Statement Balance**

The **statement balance** is the ending balance shown on your bank or credit card statement.

**Where to find it:**
- Printed on the front page of paper statements
- Shown in online banking as "Statement Balance" or "Ending Balance"
- Listed at the bottom of the transaction list on the statement

**Example statement:**

```
═══════════════════════════════════════════════════
  ABC BANK - Monthly Statement
═══════════════════════════════════════════════════

  Account: Checking ***1234
  Statement Period: Sep 16 - Oct 15, 2025

  Previous Balance:     $1,000.00
  Deposits:             $2,000.00
  Withdrawals:          $282.84

  ENDING BALANCE:       $2,717.16  ← This is your Statement Balance!

═══════════════════════════════════════════════════
```

#### **Discrepancy**

The **discrepancy** is the difference between your cleared balance and the statement balance:

```
Discrepancy = Statement Balance - Cleared Balance
```

**What different discrepancies mean:**

| Discrepancy | Meaning | Likely Cause |
|------------|---------|--------------|
| **$0.00** | ✓ Perfect match! | Everything reconciled correctly |
| **Positive** (e.g., +$50) | Your cleared balance is too low | Missing income or fewer expenses than expected |
| **Negative** (e.g., -$50) | Your cleared balance is too high | Missing expense or fewer deposits than expected |

**Example Scenarios:**

**Scenario A: Balanced ($0.00)**
```
Statement Balance:  $1,500.00
Cleared Balance:    $1,500.00
Discrepancy:        $0.00  ✓ Balanced!
```

**Scenario B: Positive Discrepancy (+$50.00)**
```
Statement Balance:  $1,550.00
Cleared Balance:    $1,500.00
Discrepancy:        +$50.00

Possible causes:
  - You forgot to check a $50 deposit
  - You forgot to check a $50 expense (double-check!)
  - Bank interest of $50 you didn't record
```

**Scenario C: Negative Discrepancy (-$50.00)**
```
Statement Balance:  $1,450.00
Cleared Balance:    $1,500.00
Discrepancy:        -$50.00

Possible causes:
  - You checked a transaction that's not on the statement yet
  - You entered a wrong amount ($50 too high)
  - Bank fee of $50 you didn't record
```

### Handling Discrepancies

Found a discrepancy? Don't panic! Follow this systematic troubleshooting process:

#### **Step 1: Double-Check Your Math**

Before investigating complex issues, verify the basics:

1. **Re-enter the statement balance** in the dialog
   - Maybe you typed $1,245.67 instead of $1,254.67
   - Check the statement carefully

2. **Recount your cleared transactions**
   - Uncheck all transactions
   - Start over, checking them one by one
   - Be methodical

3. **Verify opening balance**
   - Is this your first reconciliation? Should be $0.00
   - Is this a subsequent reconciliation? Should match last statement's ending balance

#### **Step 2: Look for Missing Transactions**

**Positive discrepancy?** (Statement balance is higher)

You're probably missing transactions you haven't checked yet:

1. **Check for unchecked deposits**
   - Did you forget to check a paycheck?
   - Any interest earnings not checked?

2. **Look for transactions at the end of the statement**
   - Transactions near the statement closing date are easy to miss
   - Check the last page of your statement

**Negative discrepancy?** (Statement balance is lower)

You might be missing expenses:

1. **Check for unchecked expenses**
   - Did you forget to check a bill payment?
   - Any automatic withdrawals?

2. **Look for bank fees or charges**
   - Monthly maintenance fees
   - ATM fees
   - Overdraft charges
   - Foreign transaction fees

#### **Step 3: Look for Wrong Amounts**

Typos happen! Check your transaction amounts:

1. **Compare each transaction amount carefully**
   - Did you enter $500 instead of $50?
   - Did you enter $123.45 instead of $132.45?

2. **Common errors:**
   - Missing or extra zero (10 vs 100)
   - Decimal in wrong place (12.34 vs 123.4)
   - Transposed numbers (123 vs 132)

**Pro Tip**: If your discrepancy is a round number (like $100 or $50), it's often a missing transaction of that exact amount.

#### **Step 4: Look for Duplicate Transactions**

Did you accidentally enter the same transaction twice?

1. **Sort transactions by amount** (if possible)
2. **Look for identical transactions** on the same day
3. **Check for similar descriptions**

**Example:**
```
Oct 12 | Grocery Store | -$52.34  ← Original
Oct 12 | Grocery       | -$52.34  ← Duplicate! (slightly different description)
```

If you find a duplicate, **don't check it** during reconciliation. Delete it after reconciliation completes.

#### **Step 5: Check for Pending Transactions**

Some transactions might not appear on your statement yet:

**Transactions that might still be pending:**
- Checks you wrote recently (not cashed yet)
- Debit card transactions from the last day or two
- Automatic payments scheduled near statement closing
- Weekend transactions (posted on Monday)

**What to do:**
- **Don't check** transactions that aren't on your statement yet
- They'll appear on next month's statement
- They'll reconcile during your next reconciliation

#### **Step 6: Check for Bank Errors**

Rarely, but sometimes, banks make mistakes:

**Look for:**
- Duplicate charges from merchants
- Incorrect amounts posted by the bank
- Transactions you don't recognize (possible fraud!)
- Missing deposits that should have cleared

**If you find a bank error:**
1. **Contact your bank immediately**
2. **Provide transaction details**
3. **Ask them to investigate and correct**
4. **Wait for correction before completing reconciliation**

#### **Step 7: When You Can't Find the Difference**

If you've tried everything and still can't find the discrepancy:

**For small discrepancies (<$5.00):**
1. **Add a note** explaining you couldn't find the difference
2. **Complete the reconciliation anyway**
3. **Make a correcting entry** to account for the difference
4. **Example note:** "Unable to locate $2.35 discrepancy after thorough review. Marking complete."

**For large discrepancies (>$10.00):**
1. **Don't complete yet!** The issue is too significant
2. **Cancel and investigate further** outside the reconciliation dialog
3. **Check your transaction history** carefully
4. **Consider asking for help** or waiting until you have more information
5. **Try again later** when you've figured out the issue

**Last Resort:**
- **Re-enter transactions** from your statement into a spreadsheet
- **Calculate manually** what the balance should be
- **Compare with your app** to find the discrepancy source

### Reconciliation Tips & Best Practices

Follow these tips to make reconciliation easier and more effective:

#### ✅ **Tip 1: Reconcile Regularly**

**Best Practice:** Reconcile monthly when your statement arrives.

**Why it matters:**
- Easier to remember recent transactions
- Fewer transactions to review (less overwhelming)
- Catch errors while they're fresh
- Maintain accurate financial records

**Set a reminder:** Add "Reconcile Accounts" to your calendar on the same day each month.

#### ✅ **Tip 2: Record Transactions Promptly**

**Best Practice:** Enter transactions into the app as soon as they happen.

**How:**
- Keep receipts and enter them daily or weekly
- Use your bank's mobile app to cross-reference
- Set aside 10 minutes each weekend to catch up

**Why it matters:**
- You won't forget transactions
- Reconciliation becomes easier (everything is already entered)
- You'll spot fraudulent charges faster

#### ✅ **Tip 3: Keep Your Statements Organized**

**Best Practice:** Save all bank statements (paper or digital).

**How to organize:**
- **Paper statements:** File in a binder by month/year
- **Digital statements:** Save PDFs in a folder: `Bank Statements/2025/`
- **Name files clearly:** `2025-10-Checking-Statement.pdf`

**Why it matters:**
- Easy to reference during reconciliation
- Needed for tax purposes
- Helpful if you need to dispute a charge

#### ✅ **Tip 4: Work in a Quiet Environment**

**Best Practice:** Reconcile when you have 15-30 minutes of uninterrupted time.

**Why it matters:**
- Reconciliation requires concentration
- Interruptions lead to errors and missed transactions
- You'll be more thorough and accurate

**Create the right environment:**
- 🔇 Turn off notifications
- ☕ Get a beverage
- 🎵 Put on focus music (optional)
- 📝 Have paper and pen nearby for notes

#### ✅ **Tip 5: Check Transactions in Order**

**Best Practice:** Check transactions from oldest to newest, one at a time.

**Why it matters:**
- Methodical approach reduces errors
- You won't accidentally skip transactions
- Easier to track your progress

**How to do it:**
1. Start with the first transaction on your statement
2. Find it in the app's reconciliation dialog
3. Check the ✓ checkbox
4. Move to the next transaction on the statement
5. Repeat until all transactions are checked

#### ✅ **Tip 6: Use the Notes Field**

**Best Practice:** Always add notes when there's a discrepancy.

**Good note examples:**
- "Bank fee of $15.00 for overdraft - will add after reconciliation"
- "Interest earned: $3.25 - not yet recorded"
- "ATM fee of $2.50 I wasn't aware of"
- "Check #1234 not yet cashed, will appear next month"

**Why it matters:**
- Helps you remember what happened
- Useful when reviewing reconciliation history
- Documents decisions for future reference

#### ✅ **Tip 7: Don't Force a Balanced Reconciliation**

**Warning:** Never adjust transactions just to make the reconciliation balance!

**Why this is bad:**
- You're hiding errors instead of fixing them
- Your records become inaccurate
- You'll have bigger problems later

**Instead:**
- Take the time to find the real discrepancy
- Add a note if you can't find it
- Complete with a small discrepancy if necessary
- But never fudge the numbers!

#### ✅ **Tip 8: Reconcile All Accounts**

**Best Practice:** Reconcile ALL accounts, not just your main checking.

**Accounts to reconcile:**
- ✓ Checking accounts
- ✓ Savings accounts
- ✓ Credit cards
- ✓ Cash accounts
- ✓ Investment accounts (quarterly)

**Why it matters:**
- Every account can have errors
- Credit card fraud is common
- Complete financial picture requires all accounts reconciled

#### ✅ **Tip 9: Review Reconciliation History**

**Best Practice:** Periodically review past reconciliations.

**What to look for:**
- Frequent discrepancies? (might indicate a recurring problem)
- Common types of errors? (work on preventing them)
- Trends in your balance over time

**Where to find it:** (if available in the app)
- View → Reconciliation History
- Or in the Account Details panel

### Troubleshooting Reconciliation

#### Problem: "No Account Selected" Warning

**Symptom:** You click Reconcile but get a warning: "Please select an account to reconcile."

**Solution:**
1. Look at the accounts list on the left side of the main window
2. Click on an account to select it (it should highlight)
3. Try opening the reconciliation dialog again (Edit → Reconcile or Ctrl+R)

#### Problem: Reconciliation Dialog is Empty

**Symptom:** Dialog opens but shows "No unreconciled transactions."

**Possible Causes & Solutions:**

**Cause 1: All transactions are already reconciled**
- This account has been fully reconciled recently
- No new transactions since last reconciliation
- **Solution:** Add new transactions first, then reconcile

**Cause 2: This is a brand new account with no transactions**
- **Solution:** Add some transactions to the account, then reconcile

**Cause 3: All transactions are marked as "Cleared" from a previous incomplete reconciliation**
- **Solution:** Contact support or check database (technical issue)

#### Problem: Can't Find a Transaction

**Symptom:** Your statement shows a transaction that doesn't appear in the reconciliation dialog.

**Possible Causes & Solutions:**

**Cause 1: Transaction not entered in the app yet**
- **Solution:** Cancel reconciliation, add the missing transaction, then try again

**Cause 2: Transaction entered in a different account**
- **Solution:** Check other accounts, move transaction if needed

**Cause 3: Transaction already reconciled (shouldn't appear again)**
- Check if transaction is already marked "Cleared" in transaction list
- **Solution:** This is normal - already reconciled transactions don't appear

**Cause 4: Transaction date outside the reconciliation period**
- **Solution:** Check the date range on your statement

#### Problem: Discrepancy Won't Go to Zero

**Symptom:** No matter what you do, you can't get the discrepancy to $0.00.

**Solutions (in order):**

1. **Double-check the statement balance** you entered
2. **Recount all checked transactions** (uncheck all, start over)
3. **Look for a missing transaction** on the statement
4. **Look for a wrong amount** in your transactions
5. **Check for bank fees** or interest you haven't recorded
6. **See "Handling Discrepancies" section** above for detailed troubleshooting

#### Problem: Complete Button is Disabled

**Symptom:** The "Complete Reconciliation" button is grayed out and can't be clicked.

**Possible Causes & Solutions:**

**Cause 1: Statement balance is empty**
- **Solution:** Enter your statement balance in the "Statement Balance" field

**Cause 2: Statement date is not selected**
- **Solution:** Pick a date using the calendar picker

**Cause 3: Invalid statement balance (not a number)**
- **Solution:** Make sure you entered a valid decimal number (e.g., 1234.56)

#### Problem: Reconciliation Fails with Error

**Symptom:** You click "Complete" but get an error message.

**Common error messages and solutions:**

**"A reconciliation is already in progress for this account"**
- **Cause:** You (or another user) already started a reconciliation
- **Solution:** Cancel or complete the other reconciliation first, then try again

**"Unable to save reconciliation"**
- **Cause:** Database error or permission issue
- **Solution:** Check that the database file is writable, restart the app, try again

**"Invalid statement date"**
- **Cause:** Date is too far in the past or future
- **Solution:** Check that you selected a reasonable date (within last 2 years)

#### Problem: Dialog Closes but Nothing Happened

**Symptom:** You clicked "Complete" but the reconciliation didn't save.

**Possible Causes & Solutions:**

**Cause 1: You clicked "Cancel" instead of "Complete"**
- **Solution:** Open the dialog again and click "Complete Reconciliation"

**Cause 2: Dialog showed an error message you missed**
- **Solution:** Try again and watch carefully for error messages

**Cause 3: Database issue**
- **Solution:** Check application logs, restart app, try again

### Frequently Asked Questions

#### Q: How often should I reconcile my accounts?

**A:** Monthly is recommended for most accounts (checking, savings, credit cards). Reconcile when you receive your monthly statement. For cash accounts, weekly is better due to frequent transactions.

#### Q: What if I have a discrepancy?

**A:** Small discrepancies (<$5) are usually due to bank fees, interest, or minor errors. Add a note explaining the discrepancy and complete the reconciliation. For larger discrepancies (>$10), investigate thoroughly before completing. See the "Handling Discrepancies" section for detailed troubleshooting steps.

#### Q: Can I reconcile multiple times per month?

**A:** Yes! You can reconcile as often as you like. Some people reconcile weekly to stay on top of their finances. Just use your current balance as the "statement balance" for mid-month reconciliations.

#### Q: What if I made a mistake during reconciliation?

**A:** If you haven't completed yet, just uncheck the wrong transactions and fix them. If you already completed, you can run a new reconciliation to correct it. The next reconciliation will use the completed reconciliation's ending balance as its opening balance.

#### Q: Do I need to reconcile if I check my bank balance online every day?

**A:** Yes! Even if you check online banking daily, reconciliation is important for:
- Catching data entry errors in your app
- Verifying every transaction matches
- Maintaining proper financial records
- Detecting fraudulent charges you might miss

#### Q: What happens to cleared transactions after reconciliation?

**A:** Cleared transactions remain in your transaction list permanently, but they're marked with a "Cleared" status and reconciliation date. They won't appear in future reconciliations since they've already been verified.

#### Q: Can I undo a reconciliation?

**A:** Not currently. Once completed, a reconciliation is permanent. However, you can run a new reconciliation to correct any issues. Future versions may support reconciliation reversal.

#### Q: What if my bank statement doesn't have an ending balance?

**A:** Some online statements just show transactions. In this case:
1. Log into online banking
2. Find the "Balance" or "Available Balance" as of the statement date
3. Use that as your statement balance

Or:
1. Calculate manually: Previous balance + deposits - withdrawals = ending balance
2. Use that calculated balance

#### Q: Should I reconcile my credit card accounts?

**A:** Absolutely! Credit cards are even more important to reconcile because:
- Credit card fraud is very common
- Merchants can make billing errors
- You need to verify every charge
- Helps you track credit card spending accurately

Reconcile your credit card monthly when the statement arrives (usually ~30 days after closing).

#### Q: What if a check I wrote hasn't cleared yet?

**A:** Don't check that transaction during reconciliation. It's not on your statement yet because the payee hasn't cashed the check. It will appear on next month's statement, and you'll reconcile it then. The transaction remains "Unreconciled" until the check clears.

#### Q: Can I reconcile if I'm missing some transaction receipts?

**A:** Yes, but it's harder. Use your bank statement to verify transactions even if you don't have receipts. The statement is your source of truth during reconciliation. However, it's best practice to keep all receipts for future reference.

#### Q: What's the difference between "Cleared" and "Reconciled"?

**A:** In this app, they mean the same thing:
- **"Cleared"** = verified on bank statement during reconciliation
- **"Reconciled"** = same thing, just different terminology

Both mean: "This transaction has been matched with the bank statement and verified as accurate."

#### Q: How long should I keep reconciliation records?

**A:** Keep reconciliation records for at least **7 years** for tax purposes. Bank statements should also be kept for 7 years. Digital copies are fine - you don't need to keep paper statements if you have PDFs.

#### Q: What if I haven't reconciled in over a year?

**A:** Don't panic! You can still reconcile:

**Option 1: Start fresh (recommended)**
1. Get your most recent bank statement
2. Enter any missing transactions from that statement
3. Reconcile using that statement as your starting point
4. Opening balance will be $0.00 (or your first statement's opening balance)

**Option 2: Catch up (more work)**
1. Gather all statements from the last year
2. Reconcile them one by one, starting with the oldest
3. This ensures all transactions are verified

**Option 1 is faster and gets you back on track quickly.**

---

## Advanced Features

### Split Transaction Templates (Coming Soon)

Future versions will include split templates for recurring split transactions:

- **Paycheck Template**: Pre-defined splits for your paycheck
- **Shopping Templates**: Common shopping split patterns
- **Custom Templates**: Create your own reusable split structures

### Split Transaction Reports (Coming Soon)

Planned reporting features:

- **Split Category Analysis**: See how much you're spending per split category
- **Split Trends**: Track split patterns over time
- **Category Comparison**: Compare actual vs. budgeted amounts by split category

### Budget Integration (Coming Soon)

Split transactions will integrate with budgets:

- **Budget by Split Category**: Set budgets for individual split categories
- **Split Alerts**: Get notified when split categories exceed budget
- **Split Forecasting**: Predict future spending based on split patterns

---

## Need Help?

If you encounter issues not covered in this guide:

1. **Check the GitHub Issues**: [https://github.com/anthropics/claude-code/issues](https://github.com/anthropics/claude-code/issues)
2. **Contact Support**: Report bugs or request features via GitHub
3. **Community Forum**: Connect with other users (coming soon)

---

## Glossary

**Split Transaction**: A transaction divided across multiple categories with individual amounts.

**Split**: An individual line item within a split transaction, with its own category and amount.

**Sum of Splits**: The total of all split amounts, which must equal the transaction amount.

**Category**: A classification for expenses or income (e.g., "Groceries", "Salary").

**Memo**: An optional note or comment for a split or transaction.

**Journal Entry**: An accounting record created for each split to maintain double-entry bookkeeping.

**HomeBank Pattern**: A sum-driven approach where splits are added individually and the sum builds up (vs. pre-entering a target).

---

**Version History:**

- **2.1.0** (October 23, 2025) - Added Account Reconciliation feature guide (US-004)
- **2.0.0** (October 23, 2025) - Initial user guide with split transactions
- More features coming in future versions!

---

*Thank you for using Personal Finance Manager!* 🎉
