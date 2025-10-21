# Personal Finance App Development Reference
## Project: HomeBank-like Application

---

## Table of Contents
1. [Research & Analysis](#research--analysis)
2. [Technology Selection](#technology-selection)
3. [HomeBank Technical Details](#homebank-technical-details)
4. [Our Implementation](#our-implementation)
5. [Development Setup](#development-setup)
6. [Code Structure](#code-structure)
7. [Next Steps](#next-steps)

---

## Research & Analysis

### Initial Questions
- **Does C have GUI libraries?** Yes, several including GTK, Qt, Win32 API, wxWidgets, IUP, FLTK
- **Does Python have GUI libraries?** Yes, many including Tkinter, PyQt/PySide, Kivy, wxPython, and web-based options like Streamlit

### HomeBank Analysis
HomeBank is a mature personal finance application available at https://www.gethomebank.org/en/index.php

**Key Features:**
- Multiple account management
- Transaction tracking
- Budget management
- Scheduled transactions
- Financial reports and charts
- Import/Export (CSV, OFX, QFX)
- Multi-currency support
- Cross-platform (Linux, Windows, macOS, FreeBSD)

---

## Technology Selection

### Options Evaluated

#### Easiest to Start
1. **Python + Tkinter** - Built-in, simple
2. **Python + PyQt/PySide** - Professional, powerful ✅ **SELECTED**
3. **Python + Kivy** - Modern, mobile-friendly
4. **JavaScript + Electron** - Web technologies

#### Medium Difficulty
1. **C# + .NET MAUI/WPF** - Good Windows support
2. **Java + JavaFX** - Very cross-platform

#### Traditional/Powerful
1. **C + GTK+3** - What HomeBank uses
2. **C++ + Qt** - Professional grade

#### Modern Systems Language
1. **Rust + GTK-rs** - Memory-safe alternative

### Final Decision: Python + PySide6

**Reasons:**
- Best balance of power and ease of learning
- Professional-looking UIs similar to HomeBank
- Excellent documentation and community support
- Cross-platform by default
- Rich ecosystem of libraries (SQLite, CSV parsing, charting)
- Rapid development and iteration
- Qt framework is industry-proven

---

## HomeBank Technical Details

### Core Technology Stack
- **Language:** C
- **GUI Framework:** GTK+ 3.x (migrated from GTK 2 at version 5.0)
- **Build System:** GNU Autotools (autoconf, automake)
- **Version Control:** Bazaar (bzr) on Launchpad

### Dependencies
- **GLib 2** - Core data structures and utilities
- **LibRSVG** - SVG icon support
- **Cairo** - 2D graphics
- **LibOFX** - OFX/QFX file import
- **LibSoup** - Network operations
- **Pango** - Text rendering
- **HarfBuzz** - Text shaping
- **intltool** - Internationalization

### Architecture
- **Design Pattern:** Monolithic single-binary
- **Data Storage:** XML-based format (.xhb files)
- **License:** GPL-2.0 or later
- **Development History:** 27+ years (started 1995 on Amiga)

### File Structure
```
src/
  ui-account.c      # Account management
  ui-archive.c      # Scheduled transactions
  [other modules]   # Modular C files
configure.ac        # Autoconf configuration
Makefile.am         # Automake rules
```

---

## Our Implementation

### Technology Stack
- **Language:** Python 3
- **GUI Framework:** PySide6 (Qt for Python)
- **Database:** SQLite3 (built into Python)
- **Data Format:** SQLite database file (.db)

### Architecture Decisions

#### Database Schema
```sql
-- Accounts: Store bank accounts, credit cards, etc.
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    balance REAL DEFAULT 0,
    currency TEXT DEFAULT 'USD'
)

-- Transactions: All financial transactions
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER,
    date TEXT NOT NULL,
    description TEXT,
    category TEXT,
    amount REAL NOT NULL,
    type TEXT NOT NULL,  -- 'income' or 'expense'
    FOREIGN KEY (account_id) REFERENCES accounts(id)
)

-- Categories: Organize transactions
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL  -- 'income' or 'expense'
)
```

#### Application Structure
```
FinanceApp (QMainWindow)
  ├── Menu Bar (File, Edit, View, Help)
  ├── Toolbar (Quick actions)
  ├── Main Content (QSplitter)
  │   ├── Left Panel: Accounts List
  │   │   ├── Account Table
  │   │   └── Balance Summary
  │   └── Right Panel: Transactions
  │       ├── Control Buttons
  │       └── Transaction Table
  └── Status Bar

Database (Class)
  ├── create_tables()
  ├── get_accounts()
  ├── get_transactions()
  ├── add_transaction()
  ├── delete_transaction()
  └── get_balance_summary()

AddTransactionDialog (QDialog)
  ├── Account Selection
  ├── Date Picker
  ├── Description Input
  ├── Type Selection (Income/Expense)
  ├── Category Selection
  └── Amount Input
```

### Key Features Implemented (v1.0)
✅ Multi-account management
✅ Transaction creation with categories
✅ Transaction deletion
✅ Automatic balance calculation
✅ Color-coded amounts (red=expense, green=income)
✅ Account filtering of transactions
✅ Sample data for testing
✅ Menu bar structure
✅ Dialog-based transaction entry

---

## Development Setup

### Installation

```bash
# Install PySide6
pip install PySide6

# Optional: Install additional libraries for future features
pip install matplotlib      # For charts
pip install pandas          # For data manipulation
pip install openpyxl        # For Excel export
```

### Running the Application

```bash
python finance_app.py
```

### Project Structure
```
personal-finance-app/
├── finance_app.py          # Main application file
├── finance.db              # SQLite database (auto-created)
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
└── docs/
    ├── reference.md       # This file
    └── prd.md            # Product Requirements Document
```

---

## Code Structure

### Main Classes

#### 1. Database Class
**Purpose:** Handle all database operations

**Key Methods:**
- `__init__(db_name)` - Initialize database connection
- `create_tables()` - Set up database schema
- `get_accounts()` - Retrieve all accounts
- `get_transactions(account_id)` - Get transactions (optionally filtered)
- `add_transaction(...)` - Insert new transaction and update balance
- `delete_transaction(...)` - Remove transaction and update balance
- `get_categories(type)` - Get income or expense categories
- `get_balance_summary()` - Calculate total balance across all accounts

#### 2. FinanceApp Class (QMainWindow)
**Purpose:** Main application window and UI coordination

**Key Methods:**
- `setup_ui()` - Create the user interface
- `create_menu_bar()` - Set up File/Edit/View/Help menus
- `load_data()` - Refresh accounts and transactions from database
- `load_transactions(account_id)` - Display transactions in table
- `on_account_selected()` - Handle account selection event
- `add_transaction()` - Show dialog and process new transaction
- `delete_transaction()` - Remove selected transaction with confirmation

#### 3. AddTransactionDialog Class (QDialog)
**Purpose:** Dialog for entering new transactions

**Key Methods:**
- `setup_ui()` - Create form layout
- `on_type_changed(text)` - Update categories when type changes
- `update_categories(type)` - Load appropriate categories
- `get_data()` - Validate and return transaction data

### UI Components

#### Main Window Layout
```
QMainWindow
└── QHBoxLayout (central widget)
    └── QSplitter (horizontal)
        ├── Left Panel (QWidget)
        │   ├── Label: "Accounts"
        │   ├── QTableWidget (accounts)
        │   └── QLabel (balance summary)
        └── Right Panel (QWidget)
            ├── Controls (QHBoxLayout)
            │   ├── Label: "Transactions"
            │   ├── Stretch
            │   ├── Add Button
            │   └── Delete Button
            └── QTableWidget (transactions)
```

---

## Next Steps

### Phase 1: Core Features Enhancement
- [ ] Add account creation/editing
- [ ] Add category management (CRUD)
- [ ] Implement search and filtering
- [ ] Add date range filtering
- [ ] Improve transaction editing (double-click to edit)

### Phase 2: Import/Export
- [ ] CSV import functionality
- [ ] CSV export functionality
- [ ] OFX/QFX import (using ofxparse library)
- [ ] Export to Excel (using openpyxl)
- [ ] Backup and restore database

### Phase 3: Reports & Visualization
- [ ] Balance over time chart (matplotlib)
- [ ] Spending by category pie chart
- [ ] Income vs Expense comparison
- [ ] Monthly/yearly summary reports
- [ ] Budget vs Actual comparison

### Phase 4: Advanced Features
- [ ] Recurring transactions (scheduled)
- [ ] Budget planning and tracking
- [ ] Multi-currency support with exchange rates
- [ ] Split transactions
- [ ] Tags/labels for transactions
- [ ] Attachments (receipts, documents)

### Phase 5: Polish & Distribution
- [ ] Custom themes and styling
- [ ] Keyboard shortcuts
- [ ] Undo/Redo functionality
- [ ] Data validation improvements
- [ ] Performance optimization for large datasets
- [ ] Package as standalone executable (PyInstaller)
- [ ] Create installer for Windows/Mac/Linux

---

## Libraries to Add

### For Charts & Reports
```bash
pip install matplotlib      # Basic charting
pip install plotly          # Interactive charts
pip install seaborn         # Statistical visualizations
```

### For Data Processing
```bash
pip install pandas          # Data manipulation
pip install numpy           # Numerical operations
```

### For Import/Export
```bash
pip install openpyxl        # Excel files
pip install ofxparse        # OFX/QFX files
pip install python-dateutil # Date parsing
```

### For Packaging
```bash
pip install pyinstaller     # Create executables
```

---

## Learning Resources

### PySide6/Qt Documentation
- Official PySide6 Docs: https://doc.qt.io/qtforpython-6/
- Qt Examples: https://doc.qt.io/qt-6/qtexamples.html
- Qt Widgets: https://doc.qt.io/qt-6/qtwidgets-index.html

### Python SQLite
- Python sqlite3 Module: https://docs.python.org/3/library/sqlite3.html
- SQLite Tutorial: https://www.sqlitetutorial.net/

### Personal Finance App Design
- HomeBank: https://www.gethomebank.org/
- GnuCash: https://gnucash.org/
- Money Manager Ex: https://www.moneymanagerex.org/

---

## Development Tips

### Best Practices
1. **Database Transactions:** Use BEGIN/COMMIT for multi-step operations
2. **Error Handling:** Add try/except blocks around database operations
3. **Input Validation:** Always validate amounts, dates before saving
4. **User Feedback:** Use status bar messages for operation feedback
5. **Data Backup:** Implement automatic backup before destructive operations

### Performance Considerations
- Use database indexes for frequently queried columns (date, account_id)
- Paginate transaction lists for accounts with thousands of transactions
- Cache balance calculations when appropriate
- Use QThreads for heavy operations (import, reports)

### UI/UX Improvements
- Add keyboard shortcuts (Ctrl+N for new transaction, etc.)
- Implement right-click context menus
- Add tooltips for better user guidance
- Support drag-and-drop for CSV import
- Remember window size and position

---

## Troubleshooting

### Common Issues

**Issue:** "No module named 'PySide6'"
```bash
Solution: pip install PySide6
```

**Issue:** Database locked errors
```bash
Solution: Ensure only one instance of the app is running
```

**Issue:** Transactions not showing
```bash
Solution: Check account_id foreign key constraint
```

---

## Version History

### v1.0 (Current)
- Initial release
- Basic account and transaction management
- SQLite database
- Add/Delete transactions
- Sample data

### Planned Versions
- **v1.1:** Category management, search/filtering
- **v1.2:** Import/Export (CSV)
- **v1.3:** Basic reports and charts
- **v2.0:** Recurring transactions, budgets
- **v2.1:** Multi-currency support
- **v3.0:** Advanced reports, data analytics

---

## Contributing Ideas

If expanding this as an open-source project:

1. **Code Style:** Follow PEP 8 Python style guide
2. **Documentation:** Document all functions and classes
3. **Testing:** Add unit tests for database operations
4. **Internationalization:** Use Qt's translation system
5. **Accessibility:** Ensure keyboard navigation works throughout

---

## Contact & Resources

- Project inspired by: HomeBank (https://www.gethomebank.org)
- Built with: Python 3 + PySide6 (Qt for Python)
- Database: SQLite3
- License: (To be determined - consider GPL-2.0 like HomeBank)

---

**Last Updated:** October 21, 2025
**Version:** 1.0
**Status:** Active Development