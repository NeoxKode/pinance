# Technical Design Document - Personal Finance Manager

**Version:** 2.0.0
**Date:** October 21, 2025
**Status:** Design Phase
**Tech Lead:** AI Agent

---

## 1. Executive Summary

This document outlines the technical design for the Personal Finance Manager application following the completion of the architectural refactoring (v2.0). It provides detailed design decisions, patterns, and future enhancement plans.

---

## 2. System Overview

### 2.1 Purpose
Personal Finance Manager is a desktop application for tracking personal finances, managing multiple accounts, categorizing transactions, and generating financial reports.

### 2.2 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **UI Framework** | PySide6 | 6.10.0 | Cross-platform Qt-based UI |
| **Language** | Python | 3.12+ | Application logic |
| **Database** | SQLite | 3.x | Local data persistence |
| **Testing** | pytest | 8.3.4 | Unit and integration testing |
| **Type Checking** | mypy | 1.14.0 | Static type analysis |
| **Code Quality** | black, flake8 | Latest | Code formatting and linting |

### 2.3 Architecture Style
**Layered Architecture** with clear separation of concerns:
- **Presentation Layer** (UI)
- **Business Logic Layer** (Services)
- **Data Access Layer** (Repositories)
- **Persistence Layer** (Database)

---

## 3. Detailed Design

### 3.1 Data Layer Design

#### 3.1.1 Database Schema Design

**Design Decisions:**
1. **SQLite Choice:** Local-first, no server required, embedded database
2. **Normalized Schema:** 3NF to prevent data duplication
3. **Indices:** Strategic indices on foreign keys and query columns
4. **Constraints:** CHECK constraints for data integrity
5. **Audit Fields:** created_at, updated_at for tracking

**Schema Evolution Strategy:**
- Use Alembic for migrations (future)
- Version database schema
- Backward compatibility for 1 version
- Migration testing before deployment

#### 3.1.2 Repository Pattern

**Design Principles:**
```python
class BaseRepository(ABC):
    """Abstract base for all repositories."""

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all entities."""
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        """Create new entity."""
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """Update existing entity."""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        pass
```

**Benefits:**
- Testable (can mock repositories)
- Swappable (can change database)
- Consistent API across entities
- Encapsulates SQL queries

#### 3.1.3 Data Models

**Design Decision: Dataclasses**
- Immutable by default
- Type-safe
- Auto-generated __init__, __repr__
- Easy serialization
- Less boilerplate

**Example:**
```python
@dataclass
class Transaction:
    id: Optional[int]
    account_id: int
    date: str
    description: str
    category: str
    amount: Decimal  # NOT float!
    type: str

    def __post_init__(self):
        # Ensure Decimal type
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))
```

**Money Handling:**
- Use `Decimal` (not `float`) for precision
- Store as REAL in SQLite (limitation)
- Convert to Decimal immediately on read
- Never perform math on floats

---

### 3.2 Business Layer Design

#### 3.2.1 Service Layer Pattern

**Design Principles:**
- Services orchestrate business logic
- Services use repositories, not direct DB
- Services enforce business rules
- Services validate all inputs
- Services handle transactions

**Service Responsibilities:**
```python
class TransactionService:
    def create_transaction(self, ...):
        # 1. Validate inputs (validators)
        # 2. Check business rules (account exists)
        # 3. Create transaction (repository)
        # 4. Update balance (atomic)
        # 5. Log operation
        # 6. Return result or raise exception
```

**Transaction Management:**
```python
# Atomic operations
try:
    transaction = repo.create(trans)
    account_repo.update_balance(account_id, amount)
    # Both succeed or both rollback
except Exception:
    # Rollback handled by context manager
    raise BusinessRuleError("...")
```

#### 3.2.2 Validation Strategy

**Design Principles:**
- Validate early (at entry points)
- Fail fast with clear messages
- Use type hints for structure validation
- Use validators for business rules
- Never trust user input

**Validation Layers:**
1. **Type Validation:** Type hints + mypy
2. **Format Validation:** Validators (regex, range checks)
3. **Business Validation:** Services (account exists, etc.)
4. **Database Validation:** Constraints (foreign keys, unique)

**Example Validator:**
```python
class TransactionValidator:
    @staticmethod
    def validate_amount(amount_str: str) -> Decimal:
        # 1. Type conversion
        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            raise ValidationError("Invalid amount")

        # 2. Business rules
        if amount == 0:
            raise ValidationError("Amount cannot be zero")

        # 3. Range check
        if abs(amount) > Decimal("999999999.99"):
            raise ValidationError("Amount too large")

        # 4. Precision check
        if amount.as_tuple().exponent < -2:
            raise ValidationError("Max 2 decimal places")

        return amount
```

---

### 3.3 Presentation Layer Design

#### 3.3.1 Qt Architecture

**Design Pattern: Model-View-Controller (MVC)**

**Current Implementation:**
- **View:** QTableWidget (simple, not optimal)
- **Controller:** MainWindow methods
- **Model:** Implicit (service calls)

**Planned Improvement:**
- **View:** QTableView (better performance)
- **Controller:** Same
- **Model:** Custom QAbstractTableModel

**Benefits of QAbstractTableModel:**
```python
class TransactionTableModel(QAbstractTableModel):
    """Model for transaction table."""

    def __init__(self, transactions: List[Transaction]):
        super().__init__()
        self._transactions = transactions

    def rowCount(self, parent=QModelIndex()):
        return len(self._transactions)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            trans = self._transactions[index.row()]
            return self._format_cell(trans, index.column())

    def update_data(self, transactions: List[Transaction]):
        # Efficient incremental updates
        self.beginResetModel()
        self._transactions = transactions
        self.endResetModel()
```

**Benefits:**
- Only visible rows rendered
- Efficient updates (no full rebuild)
- Sorting/filtering built-in
- Less memory usage

#### 3.3.2 Signal-Slot Design

**Design Principles:**
- Use signals for decoupling
- No direct method calls between widgets
- Use typed signals (PySide6)
- Connect in __init__ or setup method

**Example:**
```python
class TransactionDialog(QDialog):
    # Define typed signal
    transaction_saved = Signal(Transaction)

    def accept(self):
        transaction = self.create_transaction()
        # Emit signal instead of calling parent method
        self.transaction_saved.emit(transaction)
        super().accept()


class MainWindow(QMainWindow):
    def show_add_dialog(self):
        dialog = TransactionDialog()
        # Connect signal
        dialog.transaction_saved.connect(self.on_transaction_saved)
        dialog.exec()

    def on_transaction_saved(self, transaction: Transaction):
        # Handle new transaction
        self.refresh_data()
```

#### 3.3.3 Error Handling in UI

**Design Strategy:**
```python
def add_transaction(self):
    try:
        # Business operation
        self.service.create_transaction(...)

        # Success feedback
        self.statusBar().showMessage("Transaction added")
        self.load_data()

    except ValidationError as e:
        # User input error (warning)
        QMessageBox.warning(self, "Invalid Input", str(e))
        logger.warning(f"Validation error: {e}")

    except BusinessRuleError as e:
        # Business rule violation (warning)
        QMessageBox.warning(self, "Cannot Complete", str(e))
        logger.error(f"Business rule error: {e}")

    except DatabaseError as e:
        # Database error (critical)
        QMessageBox.critical(self, "Database Error", str(e))
        logger.error(f"Database error: {e}", exc_info=True)

    except Exception as e:
        # Unexpected error (critical)
        QMessageBox.critical(self, "Error", f"Unexpected error: {e}")
        logger.critical(f"Unexpected error: {e}", exc_info=True)
```

**Error Display Guidelines:**
- **Warning:** Yellow icon, user can fix (validation errors)
- **Critical:** Red icon, system error (database errors)
- **Information:** Blue icon, FYI only
- Always log errors (even validation)
- Show user-friendly messages (not stack traces)

---

### 3.4 Error Handling Design

#### 3.4.1 Exception Hierarchy

```
FinanceAppError (base)
├── DatabaseError         # Data layer errors
│   ├── ConnectionError
│   └── QueryError
├── ValidationError       # Input validation errors
├── BusinessRuleError     # Business logic violations
├── NotFoundError         # Resource not found
└── DuplicateError        # Duplicate resources
```

#### 3.4.2 Error Propagation

**Flow:**
```
UI Layer
  → Catches all FinanceAppError
  → Shows user-friendly dialog
  → Logs error

Business Layer
  → Validates inputs (raises ValidationError)
  → Checks business rules (raises BusinessRuleError)
  → Catches DatabaseError, may re-raise as BusinessRuleError

Data Layer
  → Catches sqlite3.Error
  → Raises DatabaseError with context
```

---

### 3.5 Logging Design

#### 3.5.1 Logging Strategy

**Log Levels:**
- **DEBUG:** Detailed diagnostic (e.g., "Query: SELECT * FROM ...")
- **INFO:** General info (e.g., "Transaction created: ID 123")
- **WARNING:** Recoverable issues (e.g., "Invalid input, using default")
- **ERROR:** Operation failed (e.g., "Failed to save transaction")
- **CRITICAL:** System failure (e.g., "Database connection lost")

**What to Log:**
```python
# ✅ DO LOG
logger.info(f"Transaction created: {transaction.id}")
logger.warning(f"Invalid amount format: {amount_str}")
logger.error(f"Database query failed: {error}")

# ❌ DON'T LOG
logger.info(f"Password: {password}")  # Sensitive data
logger.debug(f"User data: {user.__dict__}")  # May contain sensitive info
```

#### 3.5.2 Log Rotation

**Configuration:**
```python
RotatingFileHandler(
    filename='logs/finance_app.log',
    maxBytes=10_485_760,  # 10MB
    backupCount=5          # Keep 5 old logs
)
```

**Result:**
```
logs/
├── finance_app.log          # Current log
├── finance_app.log.1        # Previous log
├── finance_app.log.2        # 2 logs ago
├── finance_app.log.3        # 3 logs ago
├── finance_app.log.4        # 4 logs ago
└── finance_app.log.5        # 5 logs ago (oldest)
```

---

### 3.6 Testing Design

#### 3.6.1 Test Pyramid

```
      ┌────────────┐
      │    E2E     │  ~10% - Full user workflows
      │   (Few)    │
      ├────────────┤
      │Integration │  ~30% - Layer interactions
      │   (Some)   │
      ├────────────┤
      │    Unit    │  ~60% - Individual functions
      │   (Many)   │
      └────────────┘
```

#### 3.6.2 Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_validators.py
│   ├── test_services.py
│   └── test_repositories.py
├── integration/             # Integration tests
│   ├── test_database.py
│   └── test_service_integration.py
├── ui/                      # UI tests (future)
│   └── test_dialogs.py
└── fixtures/                # Test data
    ├── sample_accounts.json
    └── sample_transactions.json
```

#### 3.6.3 Testing Strategies

**Unit Tests:**
```python
def test_validate_amount():
    """Test amount validation."""
    validator = TransactionValidator()

    # Valid amount
    result = validator.validate_amount("123.45")
    assert result == Decimal("123.45")

    # Invalid: zero
    with pytest.raises(ValidationError, match="cannot be zero"):
        validator.validate_amount("0.00")

    # Invalid: too many decimals
    with pytest.raises(ValidationError, match="2 decimal places"):
        validator.validate_amount("123.456")
```

**Integration Tests:**
```python
def test_create_transaction_updates_balance(db_connection):
    """Test transaction creation updates account balance."""
    # Arrange
    db = Database(":memory:")
    service = TransactionService(db)
    account_repo = AccountRepository(db)

    account = account_repo.create(Account(
        id=None,
        name="Test",
        type="bank",
        balance=Decimal("1000.00")
    ))

    # Act
    service.create_transaction(
        account_id=account.id,
        date="2025-10-21",
        description="Test",
        category="Food",
        amount="-50.00",
        trans_type="expense"
    )

    # Assert
    updated_account = account_repo.get_by_id(account.id)
    assert updated_account.balance == Decimal("950.00")
```

**Fixtures:**
```python
@pytest.fixture
def sample_account() -> Account:
    """Provide a sample account."""
    return Account(
        id=1,
        name="Test Account",
        type="bank",
        balance=Decimal("1000.00"),
        currency="USD"
    )

@pytest.fixture
def mock_repository(mocker):
    """Mock repository for service tests."""
    repo = mocker.Mock(spec=TransactionRepository)
    repo.create.return_value = Transaction(
        id=1,
        account_id=1,
        date="2025-10-21",
        description="Test",
        category="Food",
        amount=Decimal("-50.00"),
        type="expense"
    )
    return repo
```

---

## 4. Design Patterns

### 4.1 Patterns Used

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Repository** | `data/repositories/` | Encapsulate data access |
| **Service Layer** | `business/` | Business logic abstraction |
| **Dependency Injection** | Services receive DB | Testability, decoupling |
| **Factory** | Model creation | Consistent object creation |
| **Context Manager** | Database connections | Resource management |
| **Observer** | Qt Signals/Slots | Decoupled communication |
| **Strategy** | Validators | Swappable validation rules |
| **DTO** | Dataclass models | Data transfer objects |

### 4.2 Pattern Details

#### 4.2.1 Repository Pattern

**Intent:** Separate data access logic from business logic

**Implementation:**
```python
class TransactionRepository:
    def __init__(self, database: Database):
        self.db = database  # Dependency injection

    def get_all(self, account_id=None) -> List[Transaction]:
        # SQL encapsulated here
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ...")
            return [self._row_to_model(row) for row in cursor.fetchall()]
```

**Benefits:**
- Business logic doesn't know about SQL
- Can swap database (SQLite → PostgreSQL)
- Easy to mock for testing
- Consistent API

#### 4.2.2 Service Layer Pattern

**Intent:** Centralize business logic

**Implementation:**
```python
class TransactionService:
    def __init__(self, database: Database):
        self.trans_repo = TransactionRepository(database)
        self.account_repo = AccountRepository(database)
        self.validator = TransactionValidator()

    def create_transaction(self, ...):
        # Orchestrates:
        # 1. Validation
        # 2. Business rules
        # 3. Multiple repository calls
        # 4. Transaction management
```

**Benefits:**
- Single place for business logic
- Testable without UI
- Reusable across UI components
- Can add caching, logging, etc.

---

## 5. Performance Design

### 5.1 Database Performance

**Current Optimizations:**
- Indices on foreign keys
- Indices on frequent queries (date, category)
- Parameterized queries (prepared statements)
- Connection pooling via context managers

**Planned Optimizations:**
```sql
-- Covering index for transaction list
CREATE INDEX idx_trans_account_date
ON transactions(account_id, date DESC, id DESC);

-- Index for category filtering
CREATE INDEX idx_trans_category_date
ON transactions(category, date DESC);
```

### 5.2 UI Performance

**Current Issues:**
- Full table rebuild on every update
- All data loaded at once
- QTableWidget (inefficient for large datasets)

**Planned Improvements:**
1. **QAbstractTableModel**
   - Lazy loading (only visible rows)
   - Incremental updates
   - Memory efficient

2. **Pagination**
   ```python
   def get_transactions_paginated(
       self,
       page: int = 1,
       per_page: int = 100
   ) -> Tuple[List[Transaction], int]:
       offset = (page - 1) * per_page
       transactions = self.repo.get_all(limit=per_page, offset=offset)
       total = self.repo.count()
       return transactions, total
   ```

3. **Virtual Scrolling**
   - Only render visible rows
   - Reuse row widgets
   - Smooth scrolling

### 5.3 Caching Strategy

**Planned Cache Design:**
```python
class CachedAccountRepository:
    def __init__(self, repo: AccountRepository):
        self._repo = repo
        self._cache: Dict[int, Account] = {}
        self._cache_time: Dict[int, float] = {}
        self._ttl = 300  # 5 minutes

    def get_by_id(self, account_id: int) -> Optional[Account]:
        if self._is_cached(account_id):
            return self._cache[account_id]

        account = self._repo.get_by_id(account_id)
        if account:
            self._cache[account_id] = account
            self._cache_time[account_id] = time.time()

        return account

    def invalidate(self, account_id: int):
        self._cache.pop(account_id, None)
        self._cache_time.pop(account_id, None)
```

**Cache Invalidation:**
- On create/update/delete
- After timeout (TTL)
- On user request (refresh button)

---

## 6. Security Design

### 6.1 Current Security

✅ **Implemented:**
- SQL injection prevention (parameterized queries)
- Input validation (all user inputs)
- Error messages don't expose internals
- Logging doesn't include sensitive data

### 6.2 Planned Security Enhancements

#### 6.2.1 Database Encryption

**Technology:** SQLCipher
```python
from pysqlcipher3 import dbapi2 as sqlite3

conn = sqlite3.connect("finance.db")
conn.execute(f"PRAGMA key = '{encryption_key}'")
```

**Key Management:**
```python
# Derive key from user password
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    return kdf.derive(password.encode())
```

#### 6.2.2 User Authentication

**Design:**
```python
@dataclass
class User:
    id: int
    username: str
    password_hash: str  # bcrypt
    salt: bytes
    created_at: datetime

class AuthService:
    def authenticate(self, username: str, password: str) -> bool:
        user = self.user_repo.get_by_username(username)
        if not user:
            return False

        # Verify password
        password_hash = bcrypt.hashpw(
            password.encode(),
            user.salt
        )
        return password_hash == user.password_hash
```

#### 6.2.3 Audit Logging

**Design:**
```python
@dataclass
class AuditLog:
    id: int
    user_id: int
    action: str  # 'CREATE', 'UPDATE', 'DELETE'
    entity_type: str  # 'transaction', 'account'
    entity_id: int
    changes: str  # JSON of changes
    timestamp: datetime

class AuditService:
    def log_action(
        self,
        user_id: int,
        action: str,
        entity_type: str,
        entity_id: int,
        changes: dict
    ):
        log = AuditLog(
            id=None,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=json.dumps(changes),
            timestamp=datetime.now()
        )
        self.audit_repo.create(log)
```

---

## 7. Future Enhancements

### 7.1 Short-term (1-2 months)

#### 7.1.1 Search and Filters
```python
class TransactionFilter:
    account_id: Optional[int] = None
    category: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    description_search: Optional[str] = None

class TransactionService:
    def search(self, filter: TransactionFilter) -> List[Transaction]:
        return self.repo.search(filter)
```

#### 7.1.2 Reporting System
```python
@dataclass
class IncomeExpenseReport:
    period: str  # "2025-10"
    total_income: Decimal
    total_expense: Decimal
    net: Decimal
    by_category: Dict[str, Decimal]

class ReportService:
    def generate_income_expense(
        self,
        start_date: str,
        end_date: str
    ) -> IncomeExpenseReport:
        transactions = self.trans_service.get_by_date_range(
            start_date,
            end_date
        )
        # Calculate report
        return report
```

#### 7.1.3 Charts and Visualization
```python
# Using matplotlib
class ChartService:
    def create_spending_chart(
        self,
        transactions: List[Transaction]
    ) -> Figure:
        fig, ax = plt.subplots()
        # Create pie chart of expenses by category
        categories = {}
        for t in transactions:
            if t.is_expense:
                categories[t.category] = categories.get(t.category, 0) + abs(t.amount)

        ax.pie(categories.values(), labels=categories.keys())
        return fig
```

### 7.2 Medium-term (3-6 months)

#### 7.2.1 Recurring Transactions
```python
@dataclass
class RecurringTransaction:
    id: int
    template: Transaction
    frequency: str  # 'daily', 'weekly', 'monthly', 'yearly'
    next_date: str
    end_date: Optional[str]
    active: bool

class RecurringService:
    def process_recurring(self, date: str):
        """Create transactions for due recurring items."""
        recurring = self.recurring_repo.get_due(date)
        for r in recurring:
            # Create transaction
            self.trans_service.create_transaction(...)
            # Update next_date
            r.next_date = self.calculate_next_date(r)
            self.recurring_repo.update(r)
```

#### 7.2.2 Budget Management
```python
@dataclass
class Budget:
    id: int
    category: str
    amount: Decimal
    period: str  # 'monthly', 'yearly'
    start_date: str
    alert_threshold: Decimal  # 0.8 = 80%

class BudgetService:
    def check_budgets(self, date: str):
        """Check if any budgets are close to limit."""
        budgets = self.budget_repo.get_active()
        for budget in budgets:
            spent = self.trans_service.get_category_total(
                budget.category,
                budget.start_date,
                date
            )
            if spent >= budget.amount * budget.alert_threshold:
                self.alert_service.send_budget_alert(budget, spent)
```

#### 7.2.3 Multi-Currency Support
```python
@dataclass
class ExchangeRate:
    from_currency: str
    to_currency: str
    rate: Decimal
    date: str

class CurrencyService:
    def convert(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        date: str
    ) -> Decimal:
        if from_currency == to_currency:
            return amount

        rate = self.rate_repo.get_rate(from_currency, to_currency, date)
        return amount * rate
```

### 7.3 Long-term (6-12 months)

#### 7.3.1 Cloud Sync
```python
class SyncService:
    def sync_to_cloud(self):
        """Sync local data to cloud."""
        # 1. Get local changes since last sync
        changes = self.get_local_changes()

        # 2. Upload to cloud
        response = self.cloud_client.upload(changes)

        # 3. Download cloud changes
        cloud_changes = response.get_changes()

        # 4. Merge changes
        self.merge_changes(cloud_changes)

        # 5. Update sync timestamp
        self.update_last_sync()
```

#### 7.3.2 Import/Export
```python
class ImportExportService:
    def export_to_csv(self, filepath: str):
        """Export all data to CSV."""
        with open(filepath, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Account', 'Category', 'Amount', 'Description'])

            for trans in self.trans_service.get_all():
                writer.writerow([
                    trans.date,
                    self.account_service.get(trans.account_id).name,
                    trans.category,
                    trans.amount,
                    trans.description
                ])

    def import_from_ofx(self, filepath: str):
        """Import transactions from OFX file."""
        from ofxparse import OfxParser

        with open(filepath) as f:
            ofx = OfxParser.parse(f)

        for account in ofx.accounts:
            for trans in account.statement.transactions:
                self.trans_service.create_transaction(
                    account_id=self.find_matching_account(account),
                    date=trans.date.strftime('%Y-%m-%d'),
                    description=trans.memo,
                    category=self.categorize_transaction(trans),
                    amount=str(trans.amount),
                    trans_type='income' if trans.amount > 0 else 'expense'
                )
```

---

## 8. Deployment Design

### 8.1 Packaging

**Technology:** PyInstaller
```bash
pyinstaller --name="Finance Manager" \
            --windowed \
            --onefile \
            --add-data "finance_app:finance_app" \
            main.py
```

### 8.2 Auto-Update

**Design:**
```python
class UpdateService:
    def check_for_updates(self) -> Optional[str]:
        """Check if new version available."""
        current_version = __version__
        latest_version = self.fetch_latest_version()

        if self.is_newer(latest_version, current_version):
            return latest_version
        return None

    def download_update(self, version: str):
        """Download update installer."""
        url = f"https://releases.example.com/v{version}/installer.exe"
        self.download_file(url, "update.exe")

    def install_update(self):
        """Install downloaded update."""
        subprocess.Popen(["update.exe", "/SILENT"])
        sys.exit(0)
```

---

## 9. Decision Log

| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| 2025-10-21 | Use Layered Architecture | Separation of concerns, maintainability | High - Affects all code |
| 2025-10-21 | Use SQLite | Local-first, no server needed | Medium - Limits multi-user |
| 2025-10-21 | Use Decimal for money | Precision critical for finance | High - Data integrity |
| 2025-10-21 | Use Repository Pattern | Testability, abstraction | High - Code organization |
| 2025-10-21 | Use PySide6 over PyQt6 | LGPL license | Low - Similar API |
| 2025-10-21 | Type hints everywhere | Catch bugs early, IDE support | Medium - Development speed |

---

## 10. Open Questions

1. **Multi-user support:** How to handle concurrent access?
   - Current: Single-user (local database)
   - Options: File locking, server-client, web app

2. **Cloud sync:** Which cloud provider?
   - Options: Custom server, Dropbox API, Google Drive API
   - Considerations: Privacy, cost, complexity

3. **Mobile app:** Native or web-based?
   - Options: React Native, Flutter, Progressive Web App
   - Considerations: Development cost, features, performance

4. **Scalability:** What if users have 100k+ transactions?
   - Current: All data loaded into memory
   - Options: Pagination, virtual scrolling, archiving

---

## 11. Conclusion

This technical design document provides a comprehensive blueprint for the Personal Finance Manager application. The architecture is solid, extensible, and production-ready. Future enhancements can be implemented incrementally without major refactoring.

**Next Steps:**
1. Implement remaining tests (target 80% coverage)
2. Add search and filter functionality
3. Implement reporting system
4. Create charts and visualizations
5. Plan for production deployment

---

**Document Version:** 1.0
**Last Updated:** 2025-10-21
**Status:** Final
**Author:** Tech Lead Agent
