"""
Trial balance dialog for displaying accounting integrity report (US-010).
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from decimal import Decimal

from finance_app.data.models import TrialBalance


class TrialBalanceDialog(QDialog):
    """
    Dialog displaying trial balance report.

    Shows:
        - Report date and status
        - Table of accounts with debit/credit balances
        - Total debits and total credits
        - Balance status (balanced or unbalanced)
    """

    def __init__(self, trial_balance: TrialBalance, parent=None):
        super().__init__(parent)
        self.trial_balance = trial_balance
        self.setup_ui()
        self.setWindowTitle("Trial Balance Report")
        self.setMinimumSize(800, 600)

    def setup_ui(self):
        """Create UI components."""
        layout = QVBoxLayout(self)

        # Header section
        header_label = self._create_header_label()
        layout.addWidget(header_label)

        # Trial balance table
        self.table = self._create_trial_balance_table()
        layout.addWidget(self.table)

        # Totals section
        totals_widget = self._create_totals_section()
        layout.addWidget(totals_widget)

        # Button section
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        export_btn = QPushButton("Export PDF")
        export_btn.clicked.connect(self.export_pdf)
        button_layout.addWidget(export_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _create_header_label(self) -> QLabel:
        """Create header with report date and status."""
        status = "✅ BALANCED" if self.trial_balance.is_balanced else "❌ UNBALANCED"
        text = (
            f"TRIAL BALANCE\n"
            f"Report Date: {self.trial_balance.report_date}\n"
            f"As of: {self.trial_balance.as_of_date}\n"
            f"Status: {status}"
        )

        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: white;
                padding: 16px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        return label

    def _create_trial_balance_table(self) -> QTableWidget:
        """Create table of accounts with debit/credit columns."""
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Account", "Debit", "Credit"])

        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 150)

        # Populate rows
        table.setRowCount(len(self.trial_balance.accounts))
        for i, entry in enumerate(self.trial_balance.accounts):
            # Account name
            account_item = QTableWidgetItem(entry.account_name)
            table.setItem(i, 0, account_item)

            # Debit balance
            debit_text = f"${entry.debit_balance:,.2f}" if entry.debit_balance else ""
            debit_item = QTableWidgetItem(debit_text)
            debit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if entry.debit_balance:
                debit_item.setForeground(QColor("#10B981"))  # Green
            table.setItem(i, 1, debit_item)

            # Credit balance
            credit_text = f"${entry.credit_balance:,.2f}" if entry.credit_balance else ""
            credit_item = QTableWidgetItem(credit_text)
            credit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if entry.credit_balance:
                credit_item.setForeground(QColor("#3B82F6"))  # Blue
            table.setItem(i, 2, credit_item)

        table.setAlternatingRowColors(True)
        return table

    def _create_totals_section(self) -> QLabel:
        """Create totals row with status."""
        totals_text = (
            f"Total Debits: ${self.trial_balance.total_debits:,.2f}    "
            f"Total Credits: ${self.trial_balance.total_credits:,.2f}    "
            f"Difference: ${abs(self.trial_balance.difference):,.2f}"
        )

        status_color = "#10B981" if self.trial_balance.is_balanced else "#EF4444"

        label = QLabel(totals_text)
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {status_color}22;
                color: {status_color};
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }}
        """)
        return label

    def export_pdf(self):
        """Export trial balance to PDF."""
        # TODO: Implement PDF export (P2 priority)
        QMessageBox.information(
            self,
            "Feature Coming Soon",
            "PDF export will be available in a future update."
        )
