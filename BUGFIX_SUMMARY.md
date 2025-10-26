# US-005 Bug Fixes

## Issues Reported

### Issue 1: Opening balance field appears disabled even when checkbox is checked
**Screenshot:** `/home/neoxkode/dev/pinance/images/Pasted image (17).png`

**Root Cause:** Missing QSS styling for:
- `QDateEdit` widget
- `:disabled` state for input fields
- `QCheckBox` styling

**Fix:** Added comprehensive styling in `account_dialog.py:210-294`:
- Added `QDateEdit` to the base styling (matches QLineEdit and QComboBox)
- Added `:disabled` state styling with darker background (#2b2b2b), darker border (#3a3a3a), and grayed text (#666666)
- Added `QCheckBox` styling with blue checked indicator
- Added `QDateEdit` dropdown arrow styling with disabled state

**Result:** Disabled fields now have a visually distinct appearance (darker/grayed) compared to enabled fields (normal #3c3c3c background).

### Issue 2: Error when setting opening balance on existing account
**Screenshot:** `/home/neoxkode/dev/pinance/images/Pasted image (18).png`
**Error:** `AccountService object has no attribute 'get_account_by_id'`

**Root Cause:** Incorrect method name in `main_window.py:704`
- Used: `account = self.account_service.get_account_by_id(account_id)`
- Correct: `account = self.account_service.get_account(account_id)`

**Fix:** Changed method call in `main_window.py:704` from `get_account_by_id()` to `get_account()`

**Result:** Set Opening Balance dialog now works correctly for existing accounts.

## Additional Improvements

### Clarified "Initial Balance" vs "Opening Balance"
**User Question:** Are these two fields the same?

**Answer:** NO - they are different:
- **Initial Balance (legacy):** Simple balance field, does NOT create journal entries, not recommended
- **Opening Balance (recommended):** Proper double-entry accounting with journal entries, validates equation

**Enhancement:** Updated labels and help text in `account_dialog.py:146-164`:
- Changed label to "Initial Balance (legacy):"
- Added tooltip: "Legacy field - not recommended. Use Opening Balance instead for proper accounting."
- Changed opening balance label to "Opening Balance (Recommended)"
- Enhanced help text to explain it creates journal entries and maintains the accounting equation

## Files Modified

1. `finance_app/ui/dialogs/account_dialog.py`
   - Lines 150-151: Updated Initial Balance label and tooltip
   - Lines 154-164: Enhanced Opening Balance section with clearer labels
   - Lines 210-294: Added comprehensive QSS styling for QDateEdit, disabled states, and QCheckBox

2. `finance_app/ui/main_window.py`
   - Line 704: Fixed method name from `get_account_by_id()` to `get_account()`

## Testing

Both bugs have been fixed. To verify:

1. **Test Opening Balance Field:**
   - Open Account Dialog
   - Notice "Initial Balance (legacy)" is grayed/darker
   - Check "Set opening balance for this account"
   - Opening Balance and Opening Date fields should now appear with normal background (#3c3c3c)
   - Uncheck - fields should appear darker/grayed again

2. **Test Set Opening Balance on Existing Account:**
   - Right-click on any existing account
   - Select "Set Opening Balance..."
   - Dialog should open without errors
   - Fill in amount and date
   - Click "Set Opening Balance" - should work successfully

## Status

✅ Both bugs fixed
✅ Additional clarifications added
✅ Code ready for testing
