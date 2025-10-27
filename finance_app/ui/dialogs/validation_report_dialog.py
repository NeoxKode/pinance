"""
Validation report dialog for displaying balance validation results (US-010).

Shows results of account balance validation with colored severity indicators.
"""

import logging
from decimal import Decimal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from typing import List

from finance_app.data.models import ValidationResult
from finance_app.business.account_balance_validator import AccountBalanceValidator


class ValidationReportDialog(QDialog):
    """
    Dialog showing balance validation results.

    Displays:
        - Summary (passed/failed count)
        - Table of validation results with colored severity
        - Actions: Close, Export CSV, Fix All

    Signals:
        accounts_fixed: Emitted when balances are repaired
    """

    accounts_fixed = Signal(int)  # Number of accounts fixed

    def __init__(
        self,
        results: List[ValidationResult],
        validator: AccountBalanceValidator,
        parent=None
    ):
        super().__init__(parent)
        self.results = results
        self.validator = validator
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
        self.setWindowTitle("Account Balance Validation Report")
        self.setMinimumSize(900, 600)

    def setup_ui(self):
        """Create UI components."""
        layout = QVBoxLayout(self)

        # Summary section
        summary_label = self._create_summary_label()
        layout.addWidget(summary_label)

        # Results table
        self.table = self._create_results_table()
        layout.addWidget(self.table)

        # Button section
        button_layout = self._create_button_layout()
        layout.addLayout(button_layout)

    def _create_summary_label(self) -> QLabel:
        """Create summary statistics label."""
        passed = sum(1 for r in self.results if r.is_valid)
        failed = len(self.results) - passed

        if failed == 0:
            text = f"✅ All {passed} accounts validated successfully!"
            color = "#10B981"  # Green
        else:
            text = (
                f"⚠️ Validation Results: {passed} passed, {failed} failed\n"
                f"Total discrepancy amount: ${sum(abs(r.difference) for r in self.results if not r.is_valid):.2f}"
            )
            color = "#EF4444"  # Red

        label = QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {color}22;
                color: {color};
                padding: 12px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        return label

    def _create_results_table(self) -> QTableWidget:
        """Create table of validation results."""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Account",
            "Cached Balance",
            "Calculated Balance",
            "Difference",
            "Status",
            "Severity"
        ])

        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Account name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        # Populate rows
        table.setRowCount(len(self.results))
        for i, result in enumerate(self.results):
            # Account name
            account_item = QTableWidgetItem(result.account_name)
            table.setItem(i, 0, account_item)

            # Cached balance
            cached_item = QTableWidgetItem(f"${result.cached_balance:,.2f}")
            cached_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(i, 1, cached_item)

            # Calculated balance
            calculated_item = QTableWidgetItem(f"${result.calculated_balance:,.2f}")
            calculated_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(i, 2, calculated_item)

            # Difference (color-coded)
            diff_item = QTableWidgetItem(f"${result.difference:+,.2f}")
            diff_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if abs(result.difference) >= Decimal('0.01'):
                diff_item.setForeground(QColor("#EF4444"))  # Red
                diff_item.setFont(QFont("", -1, QFont.Bold))
            table.setItem(i, 3, diff_item)

            # Status
            status_text = "✅ Valid" if result.is_valid else "❌ Invalid"
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignCenter)
            if not result.is_valid:
                status_item.setForeground(QColor("#EF4444"))
            table.setItem(i, 4, status_item)

            # Severity (color-coded badge)
            severity_item = QTableWidgetItem(result.severity)
            severity_item.setTextAlignment(Qt.AlignCenter)
            severity_item.setBackground(QColor(result.severity_color))
            severity_item.setForeground(QColor("#FFFFFF"))
            severity_item.setFont(QFont("", -1, QFont.Bold))
            table.setItem(i, 5, severity_item)

        # Styling
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)

        return table

    def _create_button_layout(self) -> QHBoxLayout:
        """Create button row."""
        layout = QHBoxLayout()

        # Export CSV button
        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.export_csv)
        layout.addWidget(export_btn)

        # Fix All button (only show if there are failures)
        failed_count = sum(1 for r in self.results if not r.is_valid)
        if failed_count > 0:
            fix_btn = QPushButton(f"Fix All ({failed_count} accounts)")
            fix_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F59E0B;
                    color: white;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #D97706;
                }
            """)
            fix_btn.clicked.connect(self.fix_all_discrepancies)
            layout.addWidget(fix_btn)

        layout.addStretch()

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        return layout

    def export_csv(self):
        """Export validation results to CSV file."""
        import csv

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Validation Report",
            "validation_report.csv",
            "CSV Files (*.csv)"
        )

        if filename:
            try:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([
                        "Account",
                        "Cached Balance",
                        "Calculated Balance",
                        "Difference",
                        "Status",
                        "Severity"
                    ])

                    for result in self.results:
                        writer.writerow([
                            result.account_name,
                            f"${result.cached_balance:.2f}",
                            f"${result.calculated_balance:.2f}",
                            f"${result.difference:.2f}",
                            "Valid" if result.is_valid else "Invalid",
                            result.severity
                        ])

                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Validation report exported to:\n{filename}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Error exporting CSV: {str(e)}"
                )

    def fix_all_discrepancies(self):
        """Fix all invalid account balances."""
        failed_results = [r for r in self.results if not r.is_valid]

        # Confirmation dialog
        response = QMessageBox.question(
            self,
            "Confirm Balance Repair",
            f"This will automatically fix {len(failed_results)} accounts by "
            f"recalculating balances from journal entries.\n\n"
            f"Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if response == QMessageBox.Yes:
            fixed_count = 0
            for result in failed_results:
                try:
                    self.validator.fix_account_balance(result.account_id)
                    fixed_count += 1
                except Exception as e:
                    self.logger.error(f"Error fixing account {result.account_id}: {e}")

            # Show success message
            QMessageBox.information(
                self,
                "Repair Complete",
                f"Successfully fixed {fixed_count}/{len(failed_results)} accounts."
            )

            # Emit signal
            self.accounts_fixed.emit(fixed_count)

            # Close dialog
            self.accept()
