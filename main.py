"""
Personal Finance Manager - Main Entry Point
"""
import sys
import logging
from PySide6.QtWidgets import QApplication, QMessageBox

from finance_app.data.database import Database
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.ui.main_window import MainWindow
from finance_app.utils.logger import setup_logger

logger = setup_logger(__name__)


def startup_validation(db, account_repo, journal_repo):
    """
    Run balance validation on app startup (US-010).

    Validates all account balances and alerts user if discrepancies found.
    Offers automatic repair option.
    """
    from finance_app.business.account_balance_validator import AccountBalanceValidator

    logger.info("Running startup balance validation...")

    # Create validator
    validator = AccountBalanceValidator(db, account_repo, journal_repo)

    # Run validation
    results = validator.validate_all_accounts()

    # Check for failures
    failed = [r for r in results if not r.is_valid]

    if failed:
        logger.warning(f"Found {len(failed)} accounts with balance discrepancies")

        # Show warning dialog
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Balance Validation Warning")
        msg_box.setText(
            f"Found {len(failed)} accounts with incorrect balances.\n\n"
            f"Total discrepancy: ${sum(abs(r.difference) for r in failed):.2f}"
        )
        msg_box.setInformativeText("Would you like to automatically repair them?")
        msg_box.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Ignore
        )
        msg_box.setDefaultButton(QMessageBox.No)

        # Add "View Details" button
        details_btn = msg_box.addButton("View Details", QMessageBox.ActionRole)

        response = msg_box.exec()

        if msg_box.clickedButton() == details_btn:
            # Show validation report dialog
            from finance_app.ui.dialogs.validation_report_dialog import ValidationReportDialog
            dialog = ValidationReportDialog(results, validator)
            dialog.exec()
        elif response == QMessageBox.Yes:
            # Auto-repair all discrepancies
            logger.info("Auto-repairing balance discrepancies...")
            fixed_count = 0
            for result in failed:
                try:
                    validator.fix_account_balance(result.account_id)
                    logger.info(f"Fixed account {result.account_name}")
                    fixed_count += 1
                except Exception as e:
                    logger.error(f"Error fixing account {result.account_id}: {e}")

            logger.info(f"Repaired {fixed_count}/{len(failed)} balance discrepancies")
            QMessageBox.information(
                None,
                "Repair Complete",
                f"Successfully repaired {fixed_count} accounts."
            )
    else:
        logger.info("✅ All account balances validated successfully")


def main():
    """Application entry point."""
    try:
        logger.info("Starting Personal Finance Manager")

        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Personal Finance Manager")
        app.setOrganizationName("FinanceApp")

        # Initialize database
        db = Database("finance.db")

        # Initialize repositories for startup validation (US-010)
        account_repo = AccountRepository(db)
        journal_repo = JournalEntryRepository(db)

        # Run startup balance validation (US-010)
        # Skip if SKIP_STARTUP_VALIDATION env var is set (for testing)
        import os
        if not os.environ.get('SKIP_STARTUP_VALIDATION'):
            startup_validation(db, account_repo, journal_repo)

        # Create and show main window
        window = MainWindow(db)
        window.show()

        logger.info("Application started successfully")

        # Run event loop
        sys.exit(app.exec())

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
