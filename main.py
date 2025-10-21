"""
Personal Finance Manager - Main Entry Point
"""
import sys
from PySide6.QtWidgets import QApplication

from finance_app.data.database import Database
from finance_app.ui.main_window import MainWindow
from finance_app.utils.logger import setup_logger

logger = setup_logger(__name__)


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
