#!/usr/bin/env python3
"""
Standalone test script for DateRangeDialog.

US-012: Phase 1 - Test DateRangeDialog independently before integration.

Usage:
    python test_date_range_dialog.py
"""

import sys
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel

from finance_app.ui.dialogs import DateRangeDialog


class TestWindow(QWidget):
    """Simple test window to launch DateRangeDialog."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DateRangeDialog Test")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("<h2>DateRangeDialog Test</h2>")
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Click the button below to open the DateRangeDialog.\n"
            "Test validation by entering invalid ranges (from > to)."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Result label
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-weight: bold; color: green;")
        layout.addWidget(self.result_label)

        # Test button
        test_btn = QPushButton("Open Date Range Dialog")
        test_btn.clicked.connect(self.test_dialog)
        layout.addWidget(test_btn)

    def test_dialog(self):
        """Open DateRangeDialog and display result."""
        dialog = DateRangeDialog(self)

        if dialog.exec():
            from_date, to_date = dialog.get_date_range()
            self.result_label.setText(
                f"✓ Selected: {from_date.strftime('%b %d, %Y')} to {to_date.strftime('%b %d, %Y')}\n"
                f"  Days: {(to_date - from_date).days + 1}"
            )
            print(f"✓ Date range selected: {from_date} to {to_date}")
        else:
            self.result_label.setText("✗ Dialog cancelled")
            print("✗ Dialog cancelled")


def main():
    """Run test application."""
    app = QApplication(sys.argv)

    window = TestWindow()
    window.show()

    print("=" * 60)
    print("DateRangeDialog Test Started")
    print("=" * 60)
    print("\nTest Cases:")
    print("1. Open dialog - default dates should be 1 month ago to today")
    print("2. Click Apply - should accept and close")
    print("3. Set from_date > to_date - should show error message")
    print("4. Click Cancel - should close without selection")
    print("5. Press Enter - should trigger Apply button")
    print("6. Press Escape - should cancel dialog")
    print("\n" + "=" * 60)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
