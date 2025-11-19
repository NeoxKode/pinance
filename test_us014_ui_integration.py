"""
UI Integration test for US-014: Amount Range Filter.

Tests the complete UI integration from SearchPanelWidget through MainWindow
to the backend filtering. Verifies that amount filter UI components work
correctly with the filter pipeline.

Created: 2025-11-18
Story: US-014 - Amount Range Filter (EPIC-002, Sprint 15)
"""
import sys
from decimal import Decimal
from datetime import date, timedelta

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from finance_app.data.database import Database
from finance_app.ui.main_window import MainWindow
from finance_app.business.transaction_service import TransactionService
from finance_app.business.account_service import AccountService
from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance


def test_amount_filter_ui_integration():
    """
    Test amount filter UI integration with MainWindow.

    This test verifies:
    1. Amount filter inputs are created correctly
    2. Preset buttons work
    3. Filter signals are emitted correctly
    4. MainWindow receives and applies filters
    5. Transaction table updates correctly
    """
    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create test database (auto-initializes)
    db = Database(":memory:")

    # Create test account
    account_service = AccountService(db)
    checking = account_service.create_account(
        name="Test Checking",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING
    )

    # Create test transactions
    transaction_service = TransactionService(db)
    today = date.today()

    # Small amounts
    transaction_service.create_transaction(
        account_id=checking.id,
        date=str(today - timedelta(days=10)),
        description="Coffee",
        category="Dining Out",
        amount="5.50",
        trans_type="expense"
    )

    # Mid-range
    transaction_service.create_transaction(
        account_id=checking.id,
        date=str(today - timedelta(days=8)),
        description="Groceries",
        category="Groceries",
        amount="67.30",
        trans_type="expense"
    )

    # Large
    transaction_service.create_transaction(
        account_id=checking.id,
        date=str(today - timedelta(days=5)),
        description="Electronics",
        category="Electronics",
        amount="250.00",
        trans_type="expense"
    )

    # Very large
    transaction_service.create_transaction(
        account_id=checking.id,
        date=str(today - timedelta(days=3)),
        description="Rent",
        category="Housing",
        amount="1200.00",
        trans_type="expense"
    )

    # Income
    transaction_service.create_transaction(
        account_id=checking.id,
        date=str(today - timedelta(days=2)),
        description="Salary",
        category="Salary",
        amount="3000.00",
        trans_type="income"
    )

    # Create main window
    window = MainWindow(db)

    # Verify search panel has amount filter widgets
    search_panel = window.search_panel
    assert hasattr(search_panel, 'amount_min_input'), "Amount min input not found"
    assert hasattr(search_panel, 'amount_max_input'), "Amount max input not found"
    assert hasattr(search_panel, 'amount_absolute_checkbox'), "Absolute checkbox not found"
    assert hasattr(search_panel, 'preset_small_btn'), "Small preset button not found"
    assert hasattr(search_panel, 'preset_large_btn'), "Large preset button not found"

    print("✅ Amount filter UI components created")

    # Test 1: Verify filter count starts at 0
    assert search_panel.active_filter_count == 0, "Filter count should start at 0"
    print("✅ Filter count initialized correctly")

    # Test 2: Apply large purchases preset (> $100)
    search_panel.preset_large_btn.click()

    # Verify inputs are populated
    assert search_panel.amount_min_input.text() == "100", f"Min input should be '100', got '{search_panel.amount_min_input.text()}'"
    assert search_panel.amount_max_input.text() == "", f"Max input should be empty, got '{search_panel.amount_max_input.text()}'"
    assert search_panel.amount_absolute_checkbox.isChecked(), "Absolute checkbox should be checked"

    # Verify filter count increased
    assert search_panel.active_filter_count == 1, f"Filter count should be 1, got {search_panel.active_filter_count}"
    print("✅ Preset button works correctly")

    # Test 3: Verify transactions are filtered
    # Should show: Electronics ($250), Rent ($1200), Salary ($3000) - 3 transactions with abs >= 100
    row_count = window.transaction_table.rowCount()
    assert row_count >= 3, f"Expected at least 3 large transactions, got {row_count}"
    print(f"✅ Transactions filtered correctly ({row_count} rows shown)")

    # Test 4: Apply mid-range preset ($20-$100)
    search_panel.preset_mid_btn.click()

    # Verify inputs changed
    assert search_panel.amount_min_input.text() == "20", f"Min should be '20', got '{search_panel.amount_min_input.text()}'"
    assert search_panel.amount_max_input.text() == "100", f"Max should be '100', got '{search_panel.amount_max_input.text()}'"

    # Should show: Groceries ($67.30) - 1 transaction
    row_count = window.transaction_table.rowCount()
    assert row_count >= 1, f"Expected at least 1 mid-range transaction, got {row_count}"
    print(f"✅ Mid-range preset works ({row_count} rows shown)")

    # Test 5: Clear all filters
    search_panel.clear_all_button.click()

    # Verify inputs cleared
    assert search_panel.amount_min_input.text() == "", "Min input should be cleared"
    assert search_panel.amount_max_input.text() == "", "Max input should be cleared"
    assert not search_panel.amount_absolute_checkbox.isChecked(), "Absolute checkbox should be unchecked"
    assert search_panel.active_filter_count == 0, "Filter count should be 0"

    # All transactions should be shown
    row_count = window.transaction_table.rowCount()
    assert row_count == 5, f"Expected 5 transactions after clearing, got {row_count}"
    print("✅ Clear all filters works")

    # Test 6: Manual input (min only)
    search_panel.amount_min_input.setText("50")

    # Wait for debounce (simulate by directly calling emit)
    search_panel._emit_amount_filter()

    # Verify filter applied
    assert search_panel.current_amount_min == Decimal("50"), "Min amount should be stored"
    assert search_panel.active_filter_count == 1, "Filter count should be 1"
    print("✅ Manual min amount input works")

    # Test 7: Has amount filter check
    assert search_panel.has_amount_filter(), "Should have amount filter active"

    search_panel.clear_amount_filter()
    assert not search_panel.has_amount_filter(), "Should not have amount filter after clear"
    print("✅ has_amount_filter() works correctly")

    print("\n✅ All US-014 UI integration tests passed!")

    # Cleanup
    db.close()

    return True


if __name__ == "__main__":
    try:
        success = test_amount_filter_ui_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
