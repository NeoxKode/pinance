# Personal Finance Manager - User Guide

**Version:** 2.0.0
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
3. [Advanced Features](#advanced-features)

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

- **2.0.0** (October 23, 2025) - Initial user guide with split transactions
- More features coming in future versions!

---

*Thank you for using Personal Finance Manager!* 🎉
