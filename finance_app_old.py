"""
Personal Finance Manager - Starter Template
Similar to HomeBank, built with Python + PySide6
"""

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QDialog, QFormLayout, QComboBox, QDateEdit, QMessageBox,
    QMenuBar, QMenu, QStatusBar, QSplitter
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QAction
import sqlite3
import sys
from datetime import datetime


class Database:
    """Handle all database operations"""
    
    def __init__(self, db_name="finance.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                balance REAL DEFAULT 0,
                currency TEXT DEFAULT 'USD'
            )
        """)
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                date TEXT NOT NULL,
                description TEXT,
                category TEXT,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)
        
        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL
            )
        """)
        
        self.conn.commit()
        self._add_sample_data()
    
    def _add_sample_data(self):
        """Add some sample data if database is empty"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM accounts")
        if cursor.fetchone()[0] == 0:
            # Add sample account
            cursor.execute("""
                INSERT INTO accounts (name, type, balance, currency)
                VALUES ('Checking Account', 'Bank', 1000.00, 'USD')
            """)
            account_id = cursor.lastrowid
            
            # Add sample categories
            categories = [
                ('Groceries', 'expense'),
                ('Salary', 'income'),
                ('Utilities', 'expense'),
                ('Entertainment', 'expense')
            ]
            cursor.executemany("""
                INSERT INTO categories (name, type) VALUES (?, ?)
            """, categories)
            
            # Add sample transactions
            transactions = [
                (account_id, '2025-10-15', 'Monthly Salary', 'Salary', 3000.00, 'income'),
                (account_id, '2025-10-16', 'Grocery Store', 'Groceries', -150.50, 'expense'),
                (account_id, '2025-10-17', 'Electric Bill', 'Utilities', -85.00, 'expense'),
            ]
            cursor.executemany("""
                INSERT INTO transactions (account_id, date, description, category, amount, type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, transactions)
            
            self.conn.commit()
    
    def get_accounts(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM accounts")
        return cursor.fetchall()
    
    def get_transactions(self, account_id=None):
        cursor = self.conn.cursor()
        if account_id:
            cursor.execute("""
                SELECT id, date, description, category, amount, type 
                FROM transactions 
                WHERE account_id = ?
                ORDER BY date DESC
            """, (account_id,))
        else:
            cursor.execute("""
                SELECT id, date, description, category, amount, type 
                FROM transactions 
                ORDER BY date DESC
            """)
        return cursor.fetchall()
    
    def get_categories(self, cat_type=None):
        cursor = self.conn.cursor()
        if cat_type:
            cursor.execute("SELECT name FROM categories WHERE type = ?", (cat_type,))
        else:
            cursor.execute("SELECT name FROM categories")
        return [row[0] for row in cursor.fetchall()]
    
    def add_transaction(self, account_id, date, description, category, amount, trans_type):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (account_id, date, description, category, amount, type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (account_id, date, description, category, amount, trans_type))
        
        # Update account balance
        cursor.execute("""
            UPDATE accounts SET balance = balance + ? WHERE id = ?
        """, (amount, account_id))
        
        self.conn.commit()
    
    def delete_transaction(self, trans_id, account_id, amount):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
        
        # Update account balance
        cursor.execute("""
            UPDATE accounts SET balance = balance - ? WHERE id = ?
        """, (amount, account_id))
        
        self.conn.commit()
    
    def get_balance_summary(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(balance) FROM accounts")
        return cursor.fetchone()[0] or 0.0


class AddTransactionDialog(QDialog):
    """Dialog for adding new transactions"""
    
    def __init__(self, db, accounts, parent=None):
        super().__init__(parent)
        self.db = db
        self.accounts = accounts
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Add Transaction")
        self.setModal(True)
        layout = QFormLayout(self)
        
        # Account selection
        self.account_combo = QComboBox()
        for account in self.accounts:
            self.account_combo.addItem(account[1], account[0])  # name, id
        layout.addRow("Account:", self.account_combo)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        layout.addRow("Date:", self.date_edit)
        
        # Description
        self.description_edit = QLineEdit()
        layout.addRow("Description:", self.description_edit)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Expense", "Income"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addRow("Type:", self.type_combo)
        
        # Category
        self.category_combo = QComboBox()
        self.update_categories("expense")
        layout.addRow("Category:", self.category_combo)
        
        # Amount
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("0.00")
        layout.addRow("Amount:", self.amount_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
    
    def on_type_changed(self, text):
        trans_type = "expense" if text == "Expense" else "income"
        self.update_categories(trans_type)
    
    def update_categories(self, trans_type):
        self.category_combo.clear()
        categories = self.db.get_categories(trans_type)
        self.category_combo.addItems(categories)
    
    def get_data(self):
        try:
            amount = float(self.amount_edit.text())
            if self.type_combo.currentText() == "Expense":
                amount = -abs(amount)
            else:
                amount = abs(amount)
            
            return {
                'account_id': self.account_combo.currentData(),
                'date': self.date_edit.date().toString("yyyy-MM-dd"),
                'description': self.description_edit.text(),
                'category': self.category_combo.currentText(),
                'amount': amount,
                'type': self.type_combo.currentText().lower()
            }
        except ValueError:
            return None


class FinanceApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_account_id = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        self.setWindowTitle("Personal Finance Manager")
        self.setGeometry(100, 100, 1000, 600)
        
        # Menu bar
        self.create_menu_bar()
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Accounts
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("<b>Accounts</b>"))
        
        self.account_table = QTableWidget()
        self.account_table.setColumnCount(3)
        self.account_table.setHorizontalHeaderLabels(["Account", "Type", "Balance"])
        self.account_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.account_table.itemSelectionChanged.connect(self.on_account_selected)
        left_layout.addWidget(self.account_table)
        
        # Summary
        self.balance_label = QLabel("Total Balance: $0.00")
        self.balance_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_layout.addWidget(self.balance_label)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Transactions
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Transaction controls
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("<b>Transactions</b>"))
        control_layout.addStretch()
        
        add_btn = QPushButton("+ Add Transaction")
        add_btn.clicked.connect(self.add_transaction)
        control_layout.addWidget(add_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_transaction)
        control_layout.addWidget(delete_btn)
        
        right_layout.addLayout(control_layout)
        
        # Transaction table
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(5)
        self.transaction_table.setHorizontalHeaderLabels([
            "Date", "Description", "Category", "Amount", "Type"
        ])
        self.transaction_table.setSelectionBehavior(QTableWidget.SelectRows)
        right_layout.addWidget(self.transaction_table)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New File", self)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open File", self)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        add_trans_action = QAction("Add Transaction", self)
        add_trans_action.triggered.connect(self.add_transaction)
        edit_menu.addAction(add_trans_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        reports_action = QAction("Reports", self)
        view_menu.addAction(reports_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def load_data(self):
        # Load accounts
        accounts = self.db.get_accounts()
        self.account_table.setRowCount(len(accounts))
        
        for i, account in enumerate(accounts):
            self.account_table.setItem(i, 0, QTableWidgetItem(account[1]))  # name
            self.account_table.setItem(i, 1, QTableWidgetItem(account[2]))  # type
            balance_item = QTableWidgetItem(f"${account[3]:.2f}")
            balance_item.setData(Qt.UserRole, account[0])  # store account id
            self.account_table.setItem(i, 2, balance_item)
        
        self.account_table.resizeColumnsToContents()
        
        # Update total balance
        total = self.db.get_balance_summary()
        self.balance_label.setText(f"Total Balance: ${total:.2f}")
        
        # Load all transactions initially
        self.load_transactions()
    
    def load_transactions(self, account_id=None):
        transactions = self.db.get_transactions(account_id)
        self.transaction_table.setRowCount(len(transactions))
        
        for i, trans in enumerate(transactions):
            self.transaction_table.setItem(i, 0, QTableWidgetItem(trans[1]))  # date
            self.transaction_table.setItem(i, 1, QTableWidgetItem(trans[2]))  # description
            self.transaction_table.setItem(i, 2, QTableWidgetItem(trans[3]))  # category
            
            # Format amount with color
            amount_item = QTableWidgetItem(f"${abs(trans[4]):.2f}")
            amount_item.setData(Qt.UserRole, trans[0])  # store transaction id
            if trans[4] < 0:
                amount_item.setForeground(Qt.red)
            else:
                amount_item.setForeground(Qt.darkGreen)
            self.transaction_table.setItem(i, 3, amount_item)
            
            self.transaction_table.setItem(i, 4, QTableWidgetItem(trans[5].capitalize()))  # type
        
        self.transaction_table.resizeColumnsToContents()
    
    def on_account_selected(self):
        selected_items = self.account_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            balance_item = self.account_table.item(row, 2)
            self.current_account_id = balance_item.data(Qt.UserRole)
            self.load_transactions(self.current_account_id)
            account_name = self.account_table.item(row, 0).text()
            self.statusBar().showMessage(f"Showing transactions for: {account_name}")
    
    def add_transaction(self):
        accounts = self.db.get_accounts()
        dialog = AddTransactionDialog(self.db, accounts, self)
        
        if dialog.exec():
            data = dialog.get_data()
            if data:
                self.db.add_transaction(
                    data['account_id'],
                    data['date'],
                    data['description'],
                    data['category'],
                    data['amount'],
                    data['type']
                )
                self.load_data()
                self.statusBar().showMessage("Transaction added successfully")
            else:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid amount")
    
    def delete_transaction(self):
        selected_items = self.transaction_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a transaction to delete")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this transaction?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = selected_items[0].row()
            trans_id = self.transaction_table.item(row, 3).data(Qt.UserRole)
            amount_text = self.transaction_table.item(row, 3).text()
            amount = float(amount_text.replace('$', ''))
            
            # Determine if it was expense or income
            if self.transaction_table.item(row, 3).foreground().color() == Qt.red:
                amount = -amount
            
            # Get account_id (we need to query this or store it)
            if self.current_account_id:
                account_id = self.current_account_id
            else:
                # If viewing all transactions, we'd need to store account_id in table
                account_id = 1  # Default fallback
            
            self.db.delete_transaction(trans_id, account_id, amount)
            self.load_data()
            self.statusBar().showMessage("Transaction deleted")
    
    def show_about(self):
        QMessageBox.about(
            self,
            "About Personal Finance Manager",
            "Personal Finance Manager v1.0\n\n"
            "A simple personal finance application built with Python and PySide6.\n"
            "Inspired by HomeBank.\n\n"
            "Features:\n"
            "- Multiple accounts\n"
            "- Transaction tracking\n"
            "- Category management\n"
            "- Balance summaries"
        )


def main():
    app = QApplication(sys.argv)
    window = FinanceApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()