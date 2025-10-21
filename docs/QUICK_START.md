# Quick Start Guide

## For Developers New to the Project

### 1. Setup (5 minutes)

```bash
# Clone/navigate to project
cd /path/to/finance

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

### 3. Understanding the Architecture (5 minutes)

```
User Interface (UI Layer)
    ↓ calls
Business Services (Business Layer)
    ↓ calls  
Data Repositories (Data Layer)
    ↓ queries
SQLite Database
```

#### Want to add a new feature?

**Example: Add "Edit Transaction" button**

1. **UI** (`ui/main_window.py`): Add button and dialog
2. **Business** (`business/transaction_service.py`): Add `update_transaction()` method
3. **Data** (already have `update()` in repository)
4. **Done!**

### 4. Common Tasks

#### Add a Transaction (UI)
```python
# UI calls service
self.transaction_service.create_transaction(
    account_id=1,
    date="2025-10-21",
    description="Groceries",
    category="Food",
    amount="50.00",
    trans_type="expense"
)
```

#### Query Transactions (Code)
```python
from finance_app.data.database import Database
from finance_app.business.transaction_service import TransactionService

db = Database("finance.db")
service = TransactionService(db)

# Get all transactions
transactions = service.get_all_transactions()

# Filter by account
transactions = service.get_all_transactions(account_id=1)

# By date range
transactions = service.get_transactions_by_date_range(
    "2025-10-01", 
    "2025-10-31"
)
```

### 5. File Locations Quick Reference

| What you want to do | File to edit |
|---------------------|--------------|
| Change UI layout | `ui/main_window.py` |
| Add dialog | `ui/dialogs/` |
| Add business logic | `business/transaction_service.py` or `business/account_service.py` |
| Add validation | `business/validators.py` |
| Change database queries | `data/repositories/` |
| Add custom exception | `utils/exceptions.py` |
| Configure logging | `utils/logger.py` |

### 6. Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=finance_app

# Run specific test
pytest finance_app/tests/unit/test_validators.py

# Run only unit tests
pytest -m unit
```

### 7. Code Style

```bash
# Format code
black finance_app/

# Check types
mypy finance_app/

# Lint
flake8 finance_app/
```

### 8. Getting Help

- Read `docs/ARCHITECTURE.md` for detailed architecture
- Check `docs/REFACTORING_SUMMARY.md` for what changed
- Look at existing code for patterns
- All public methods have docstrings

### 9. Making Changes

1. Create a branch
2. Write code following existing patterns
3. Add tests
4. Run `pytest` to verify
5. Format with `black`
6. Update docs if needed
7. Commit and push

### 10. Debugging

#### App won't start
```bash
# Check Python version
python3 --version  # Should be 3.12+

# Check virtual environment
which python  # Should show .venv/bin/python

# Check imports
python -c "import finance_app"
```

#### Database issues
```bash
# Check database file
ls -lh finance.db

# Remove and recreate (CAUTION: deletes data)
rm finance.db
python main.py  # Will create new DB with sample data
```

#### Import errors
```bash
# Ensure you're in project root
pwd  # Should show /path/to/finance

# Activate virtual environment
source .venv/bin/activate
```

---

## Architecture at a Glance

```
finance/
├── main.py              # ← START HERE: Application entry point
├── finance_app/
│   ├── ui/              # ← User Interface (Qt widgets)
│   │   ├── main_window.py
│   │   └── dialogs/
│   ├── business/        # ← Business Logic (services, validation)
│   │   ├── transaction_service.py
│   │   ├── account_service.py
│   │   └── validators.py
│   └── data/            # ← Data Access (database, repositories)
│       ├── database.py
│       ├── models.py
│       └── repositories/
└── docs/                # ← Documentation
    └── ARCHITECTURE.md  # Read this for details
```

---

## Key Principles

1. **UI calls Business, Business calls Data** - Never skip layers
2. **All inputs validated** - Use validators before database
3. **Type hints everywhere** - Help your IDE help you
4. **Handle all errors** - Try-catch with logging
5. **Test your code** - Write tests for new features

---

**Ready to code?** Start with `main.py` and explore from there!

For detailed information, see `docs/ARCHITECTURE.md`
