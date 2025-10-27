"""
E2E tests for US-010 Account Balance Validation dialogs.

Story: US-010 - Account Balance Validation & Integrity

Test Coverage:
- ValidationReportDialog smoke tests (2 tests)
- TrialBalanceDialog smoke tests (2 tests)
- Dialog integration with main window (2 tests)

Total: 6 E2E tests

Testing Strategy:
- Use pytest-qt for Qt widget testing
- Focus on smoke tests (dialog initialization, basic functionality)
- Verify dialogs don't crash and display correctly
- Test signal/slot connections
"""

import pytest
from decimal import Decimal
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from finance_app.data.models import ValidationResult, TrialBalance, TrialBalanceEntry, AccountType
from finance_app.ui.dialogs.validation_report_dialog import ValidationReportDialog
from finance_app.ui.dialogs.trial_balance_dialog import TrialBalanceDialog
from finance_app.business.account_balance_validator import AccountBalanceValidator
from finance_app.business.account_service import AccountService
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository


class TestValidationReportDialogE2E:
    """E2E tests for ValidationReportDialog."""

    def test_validation_report_dialog_initializes_successfully(self, qtbot, test_db):
        """Test that ValidationReportDialog can be created and displayed."""
        # Setup: Create test validation results
        results = [
            ValidationResult(
                account_id=1,
                account_name="Test Account",
                cached_balance=Decimal("1000.00"),
                calculated_balance=Decimal("1000.00"),
                difference=Decimal("0.00"),
                is_valid=True,
                validated_at=datetime.now()
            )
        ]

        # Create validator
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)

        # Act: Create dialog
        dialog = ValidationReportDialog(results, validator)
        qtbot.addWidget(dialog)

        # Assert: Dialog created without crashing
        assert dialog is not None
        assert dialog.windowTitle() == "Account Balance Validation Report"
        assert dialog.table is not None

    def test_validation_report_dialog_displays_discrepancies(self, qtbot, test_db):
        """Test that dialog correctly displays accounts with discrepancies."""
        # Setup: Create mix of valid and invalid results
        results = [
            ValidationResult(
                account_id=1, account_name="Valid Account",
                cached_balance=Decimal("1000.00"), calculated_balance=Decimal("1000.00"),
                difference=Decimal("0.00"), is_valid=True, validated_at=datetime.now()
            ),
            ValidationResult(
                account_id=2, account_name="Invalid Account",
                cached_balance=Decimal("2000.00"), calculated_balance=Decimal("2050.00"),
                difference=Decimal("-50.00"), is_valid=False, validated_at=datetime.now()
            )
        ]

        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)

        # Act: Create dialog
        dialog = ValidationReportDialog(results, validator)
        qtbot.addWidget(dialog)

        # Assert: Table should have 2 rows
        assert dialog.table.rowCount() == 2

        # Assert: "Fix All Discrepancies" button should be visible
        fix_button = dialog.findChild(QPushButton, "")
        # Button text check
        buttons = dialog.findChildren(QPushButton)
        fix_buttons = [b for b in buttons if "Fix" in b.text()]
        assert len(fix_buttons) > 0


class TestTrialBalanceDialogE2E:
    """E2E tests for TrialBalanceDialog."""

    def test_trial_balance_dialog_initializes_successfully(self, qtbot):
        """Test that TrialBalanceDialog can be created and displayed."""
        # Setup: Create test trial balance
        trial_balance = TrialBalance(
            report_date="2025-10-27",
            as_of_date="2025-10-27"
        )
        trial_balance.add_entry(TrialBalanceEntry(
            account_id=1,
            account_name="Cash",
            account_type="asset",
            debit_balance=Decimal("1000.00"),
            credit_balance=Decimal("0.00")
        ))

        # Act: Create dialog
        dialog = TrialBalanceDialog(trial_balance)
        qtbot.addWidget(dialog)

        # Assert: Dialog created without crashing
        assert dialog is not None
        assert "Trial Balance" in dialog.windowTitle()
        assert dialog.table is not None

    def test_trial_balance_dialog_displays_accounts(self, qtbot):
        """Test that dialog correctly displays trial balance accounts."""
        # Setup: Create trial balance with multiple accounts
        trial_balance = TrialBalance(
            report_date="2025-10-27",
            as_of_date="2025-10-27"
        )
        trial_balance.add_entry(TrialBalanceEntry(
            account_id=1, account_name="Cash", account_type="asset",
            debit_balance=Decimal("1000.00"), credit_balance=Decimal("0.00")
        ))
        trial_balance.add_entry(TrialBalanceEntry(
            account_id=2, account_name="Accounts Payable", account_type="liability",
            debit_balance=Decimal("0.00"), credit_balance=Decimal("1000.00")
        ))

        # Act: Create dialog
        dialog = TrialBalanceDialog(trial_balance)
        qtbot.addWidget(dialog)

        # Assert: Table should have 2 data rows (totals displayed separately in UI)
        assert dialog.table.rowCount() == 2  # 2 accounts

        # Assert: Totals should be displayed
        assert trial_balance.total_debits == Decimal("1000.00")
        assert trial_balance.total_credits == Decimal("1000.00")


class TestValidationDialogsIntegrationE2E:
    """E2E tests for dialog integration with validation workflow."""

    def test_validation_report_with_real_database(self, qtbot, test_db):
        """Test ValidationReportDialog with real database and validator."""
        # Setup: Create real account with opening balance
        account_service = AccountService(test_db)
        account, _ = account_service.create_account_with_opening_balance(
            name="E2E Test Account",
            account_type=AccountType.ASSET,
            account_subtype="checking",
            opening_balance=Decimal("5000.00"),
            opening_date="2025-10-01"
        )

        # Validate the account
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)
        results = validator.validate_all_accounts()

        # Act: Create dialog with real results
        dialog = ValidationReportDialog(results, validator)
        qtbot.addWidget(dialog)

        # Assert: Dialog displays results from real database
        assert dialog.table.rowCount() > 0

    def test_trial_balance_with_real_database(self, qtbot, test_db):
        """Test TrialBalanceDialog with real database."""
        # Setup: Create real accounts
        account_service = AccountService(test_db)
        account_service.create_account_with_opening_balance(
            name="E2E Cash",
            account_type=AccountType.ASSET,
            account_subtype="cash",
            opening_balance=Decimal("1000.00"),
            opening_date="2025-10-01"
        )

        # Generate real trial balance
        account_repo = AccountRepository(test_db)
        journal_repo = JournalEntryRepository(test_db)
        validator = AccountBalanceValidator(test_db, account_repo, journal_repo)
        trial_balance = validator.get_trial_balance()

        # Act: Create dialog with real trial balance
        dialog = TrialBalanceDialog(trial_balance)
        qtbot.addWidget(dialog)

        # Assert: Dialog displays real data
        assert dialog.table.rowCount() > 0
        assert trial_balance.total_debits > Decimal("0.00") or trial_balance.total_credits > Decimal("0.00")
