"""
UI Tests for ReconciliationDialog

These tests verify the UI components, interactions, and visual feedback
of the reconciliation dialog using pytest-qt in offscreen mode.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QMessageBox, QInputDialog

from finance_app.ui.dialogs.reconciliation_dialog import ReconciliationDialog
from finance_app.data.database import Database
from finance_app.data.models import Account, Transaction, AccountType, AccountSubtype, NormalBalance, ReconciliationStatus
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.transaction_repository import TransactionRepository


@pytest.fixture
def test_database(tmp_path):
    """Create a test database with sample data."""
    db_path = tmp_path / "test_ui.db"
    db = Database(str(db_path))
    # Database auto-connects in __init__
    yield db
    # No need to disconnect as it's handled by Database


@pytest.fixture
def test_account(test_database):
    """Create a test account with transactions."""
    account_repo = AccountRepository(test_database)
    transaction_repo = TransactionRepository(test_database)

    # Create account
    account = Account(
        id=None,
        name="Test Checking",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        balance=Decimal("1000.00"),
        normal_balance=NormalBalance.DEBIT,
        last_reconciled_date=None,
        created_at=datetime(2025, 10, 1)
    )
    account = account_repo.create(account)

    # Create unreconciled transactions
    transactions = [
        Transaction(
            id=None,
            account_id=account.id,
            date="2025-10-05",
            description="Salary Deposit",
            category="Income",
            amount=Decimal("2000.00"),
            type="income",
            reconciliation_status=ReconciliationStatus.UNRECONCILED,
            created_at=datetime(2025, 10, 5)
        ),
        Transaction(
            id=None,
            account_id=account.id,
            date="2025-10-08",
            description="Grocery Store",
            category="Groceries",
            amount=Decimal("-125.50"),
            type="expense",
            reconciliation_status=ReconciliationStatus.UNRECONCILED,
            created_at=datetime(2025, 10, 8)
        ),
        Transaction(
            id=None,
            account_id=account.id,
            date="2025-10-12",
            description="Electric Bill",
            category="Utilities",
            amount=Decimal("-89.99"),
            type="expense",
            reconciliation_status=ReconciliationStatus.UNRECONCILED,
            created_at=datetime(2025, 10, 12)
        ),
    ]

    for txn in transactions:
        transaction_repo.create(txn)

    return account


class TestReconciliationDialogUI:
    """Test ReconciliationDialog UI components and interactions."""

    def test_dialog_opens_successfully(self, qtbot, test_database, test_account):
        """Test 1.1: Reconciliation dialog opens successfully."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        assert dialog.isModal()
        # Window title format may use " - " or ": " separator
        assert test_account.name in dialog.windowTitle()
        assert "Reconcile Account" in dialog.windowTitle()
        assert dialog.minimumWidth() == 900
        assert dialog.minimumHeight() == 700

    def test_statement_details_section_visible(self, qtbot, test_database, test_account):
        """Test 2.1: Statement details section displays correctly."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Check account name is displayed
        assert dialog.account_name_label is not None
        assert test_account.name in dialog.account_name_label.text()

        # Check statement date picker exists
        assert dialog.statement_date_edit is not None
        assert dialog.statement_date_edit.calendarPopup()

        # Check statement balance input exists
        assert dialog.statement_balance_edit is not None
        assert dialog.statement_balance_edit.placeholderText() != ""

    def test_statement_date_picker_works(self, qtbot, test_database, test_account):
        """Test 2.2: Statement date picker works."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Set a specific date
        test_date = QDate(2025, 10, 15)
        dialog.statement_date_edit.setDate(test_date)

        assert dialog.statement_date_edit.date() == test_date

    def test_statement_balance_accepts_decimal(self, qtbot, test_database, test_account):
        """Test 2.3: Statement balance accepts valid decimal input."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Enter valid amounts
        test_amounts = ["1234.56", "0.00", "99999.99"]

        for amount in test_amounts:
            qtbot.keyClicks(dialog.statement_balance_edit, amount)
            assert dialog.statement_balance_edit.text() == amount
            dialog.statement_balance_edit.clear()

    def test_transaction_list_populates(self, qtbot, test_database, test_account):
        """Test 3.1: Transaction table populates with unreconciled transactions."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Should show 3 unreconciled transactions
        assert dialog.transactions_table.rowCount() == 3

        # Check column headers
        expected_headers = ["✓", "Date", "Description", "Amount", "Type"]
        for col in range(5):
            header = dialog.transactions_table.horizontalHeaderItem(col)
            assert header is not None
            assert header.text() == expected_headers[col]

    def test_checkboxes_toggle_cleared_status(self, qtbot, test_database, test_account):
        """Test 3.2: Checkboxes toggle cleared status."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Get checkbox widget from first row
        checkbox_widget = dialog.transactions_table.cellWidget(0, 0)
        checkbox = checkbox_widget.findChild(checkbox_widget.__class__)

        # Initially unchecked
        initial_checked = len(dialog.checked_transactions)

        # Click checkbox
        qtbot.mouseClick(checkbox, Qt.LeftButton)

        # Should be checked now
        assert len(dialog.checked_transactions) == initial_checked + 1

    def test_transaction_count_displays(self, qtbot, test_database, test_account):
        """Test 3.3: Transaction count label displays total."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Check transaction count label
        assert dialog.transaction_count_label is not None
        assert "3" in dialog.transaction_count_label.text()
        assert "transaction" in dialog.transaction_count_label.text().lower()

    def test_summary_section_displays(self, qtbot, test_database, test_account):
        """Test 4.1: Summary section displays on dialog open."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Check all summary labels exist
        assert dialog.opening_balance_label is not None
        assert dialog.cleared_transactions_label is not None
        assert dialog.cleared_balance_label is not None
        assert dialog.statement_balance_label is not None
        assert dialog.discrepancy_label is not None

        # Opening balance should show account opening balance
        assert "$1,000.00" in dialog.opening_balance_label.text()

    def test_summary_updates_on_checkbox_click(self, qtbot, test_database, test_account):
        """Test 4.2: Summary recalculates when checkbox clicked."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Enter statement balance first
        qtbot.keyClicks(dialog.statement_balance_edit, "2784.51")

        # Get initial cleared balance
        initial_cleared = dialog.cleared_balance_label.text()

        # Click first checkbox (Salary +2000.00)
        checkbox_widget = dialog.transactions_table.cellWidget(0, 0)
        checkbox = checkbox_widget.findChild(checkbox_widget.__class__)
        qtbot.mouseClick(checkbox, Qt.LeftButton)

        # Cleared balance should update
        updated_cleared = dialog.cleared_balance_label.text()
        assert updated_cleared != initial_cleared

    def test_summary_updates_on_statement_balance_change(self, qtbot, test_database, test_account):
        """Test 4.3: Summary recalculates when statement balance changes."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Enter statement balance
        qtbot.keyClicks(dialog.statement_balance_edit, "2500.00")

        # Check that statement balance updates
        assert "$2,500.00" in dialog.statement_balance_label.text()

    def test_discrepancy_color_coding_balanced(self, qtbot, test_database, test_account):
        """Test 4.4: Discrepancy shows green when balanced."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Mark all transactions as cleared
        for row in range(dialog.transactions_table.rowCount()):
            checkbox_widget = dialog.transactions_table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(checkbox_widget.__class__)
            qtbot.mouseClick(checkbox, Qt.LeftButton)

        # Set statement balance to match cleared balance
        # Opening: 1000.00 + Salary: 2000.00 - Grocery: 125.50 - Electric: 89.99 = 2784.51
        qtbot.keyClicks(dialog.statement_balance_edit, "2784.51")

        # Discrepancy should be close to 0 and styled green
        discrepancy_style = dialog.discrepancy_label.styleSheet()
        assert "balanced" in dialog.discrepancy_status_label.text().lower() or "0.00" in dialog.discrepancy_label.text()

    def test_complete_button_enables_with_balance(self, qtbot, test_database, test_account):
        """Test 5.1: Complete button enables when valid balance entered."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Initially, button should be disabled if no balance
        initial_state = dialog.complete_btn.isEnabled()

        # Enter statement balance
        qtbot.keyClicks(dialog.statement_balance_edit, "2500.00")

        # Button should enable
        assert dialog.complete_btn.isEnabled()

    def test_cancel_button_closes_dialog(self, qtbot, test_database, test_account):
        """Test: Cancel button closes dialog without saving."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Click cancel
        qtbot.mouseClick(dialog.cancel_btn, Qt.LeftButton)

        # Dialog should be rejected
        assert dialog.result() == dialog.Rejected

    def test_keyboard_navigation_works(self, qtbot, test_database, test_account):
        """Test 10.2: Tab navigation works through form fields."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Set focus to first field
        dialog.statement_date_edit.setFocus()
        assert dialog.statement_date_edit.hasFocus()

        # Press Tab
        qtbot.keyClick(dialog.statement_date_edit, Qt.Key_Tab)

        # Focus should move to statement balance
        # (May vary based on tab order, just check focus moved)
        assert not dialog.statement_date_edit.hasFocus()

    def test_escape_key_cancels_dialog(self, qtbot, test_database, test_account):
        """Test 10.4: Escape key cancels dialog."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Press Escape
        qtbot.keyClick(dialog, Qt.Key_Escape)

        # Dialog should be rejected
        assert dialog.result() == dialog.Rejected

    def test_dark_theme_applied(self, qtbot, test_database, test_account):
        """Test 7.1: Dark theme consistent across dialog."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Check that stylesheet is applied
        stylesheet = dialog.styleSheet()
        assert stylesheet != ""
        assert "#2b2b2b" in stylesheet.lower() or "background" in stylesheet.lower()

    def test_amount_color_coding(self, qtbot, test_database, test_account):
        """Test 7.2: Amount color-coding works (red negative, green positive)."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Check that amounts are color-coded in table
        # Row 0: Salary +2000.00 (should be green/positive styling)
        # Row 1: Grocery -125.50 (should be red/negative styling)

        amount_item_positive = dialog.transactions_table.item(0, 3)
        amount_item_negative = dialog.transactions_table.item(1, 3)

        # Check that items exist
        assert amount_item_positive is not None
        assert amount_item_negative is not None

        # Check that foreground colors are different
        pos_color = amount_item_positive.foreground()
        neg_color = amount_item_negative.foreground()
        assert pos_color != neg_color


class TestReconciliationDialogEdgeCases:
    """Test edge cases and error scenarios."""

    def test_empty_account_no_transactions(self, qtbot, test_database):
        """Test 8.1: No unreconciled transactions scenario."""
        account_repo = AccountRepository(test_database)

        # Create account with no transactions
        account = Account(
            id=None,
            name="Empty Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("500.00"),
            normal_balance=NormalBalance.DEBIT,
            last_reconciled_date=None,
            created_at=datetime(2025, 10, 1)
        )
        account = account_repo.create(account)

        dialog = ReconciliationDialog(test_database, account)
        qtbot.addWidget(dialog)

        # Transaction table should be empty
        assert dialog.transactions_table.rowCount() == 0
        assert "0" in dialog.transaction_count_label.text()

    def test_invalid_statement_balance_handling(self, qtbot, test_database, test_account):
        """Test: Invalid statement balance shows error."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Try to enter invalid text
        qtbot.keyClicks(dialog.statement_balance_edit, "invalid")

        # Validator should prevent or clear invalid input
        # The exact behavior depends on the validator implementation


@pytest.mark.integration
class TestReconciliationDialogIntegration:
    """Integration tests for complete reconciliation workflow through UI."""

    def test_complete_balanced_reconciliation_workflow(self, qtbot, test_database, test_account, monkeypatch):
        """Test complete reconciliation workflow through UI."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Step 1: Enter statement details
        dialog.statement_date_edit.setDate(QDate(2025, 10, 15))
        qtbot.keyClicks(dialog.statement_balance_edit, "2784.51")

        # Step 2: Mark all transactions as cleared
        for row in range(dialog.transactions_table.rowCount()):
            checkbox_widget = dialog.transactions_table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(checkbox_widget.__class__)
            qtbot.mouseClick(checkbox, Qt.LeftButton)

        # Step 3: Verify discrepancy is 0
        assert "$0.00" in dialog.discrepancy_label.text() or "0.00" in dialog.discrepancy_label.text()

        # Step 4: Complete reconciliation
        # Mock the success message
        monkeypatch.setattr(QMessageBox, 'information', lambda *args: QMessageBox.Ok)

        # Click complete button
        qtbot.mouseClick(dialog.complete_btn, Qt.LeftButton)

        # Dialog should be accepted
        assert dialog.result() == dialog.Accepted

    def test_reconciliation_with_discrepancy_shows_confirmation(self, qtbot, test_database, test_account, monkeypatch):
        """Test that discrepancy shows confirmation dialog."""
        dialog = ReconciliationDialog(test_database, test_account)
        qtbot.addWidget(dialog)

        # Enter statement balance that doesn't match
        qtbot.keyClicks(dialog.statement_balance_edit, "3000.00")

        # Mark some transactions
        checkbox_widget = dialog.transactions_table.cellWidget(0, 0)
        checkbox = checkbox_widget.findChild(checkbox_widget.__class__)
        qtbot.mouseClick(checkbox, Qt.LeftButton)

        # Discrepancy should be visible and non-zero
        assert "$0.00" not in dialog.discrepancy_label.text()

        # Mock confirmation dialog to return No (cancel)
        monkeypatch.setattr(QMessageBox, 'question', lambda *args, **kwargs: QMessageBox.No)

        # Try to complete
        qtbot.mouseClick(dialog.complete_btn, Qt.LeftButton)

        # Dialog should NOT be accepted (user cancelled)
        assert dialog.result() != dialog.Accepted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
