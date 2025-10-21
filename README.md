# Personal Finance Manager

A desktop application for managing personal finances, built with Python and PySide6 (Qt 6).

## Features

- ✅ Multiple account management (bank, cash, credit, investment)
- ✅ Transaction tracking with categories
- ✅ Income and expense categorization
- ✅ Balance summaries and calculations
- ✅ Clean, professional UI
- ✅ SQLite database with proper indices
- ✅ Comprehensive error handling
- ✅ Structured logging

## Architecture

This application follows a **layered architecture** with clear separation of concerns:

```
UI Layer (PySide6)
    ↓
Business Logic Layer (Services, Validators)
    ↓
Data Access Layer (Repositories)
    ↓
Database (SQLite)
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed documentation.

## Requirements

- Python 3.12+
- PySide6 6.10.0
- See [requirements.txt](requirements.txt) for full dependencies

## Installation

### 1. Clone or download the project

```bash
cd /path/to/finance
```

### 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# OR
.venv\Scripts\activate  # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Run the application

```bash
python main.py
```

Or use the compatibility symlink:

```bash
python finance_app.py
```

### Run tests

```bash
# All tests
pytest

# With coverage report
pytest --cov=finance_app --cov-report=html

# Unit tests only
pytest -m unit
```

### Run linters

```bash
# Format code
black finance_app/

# Check style
flake8 finance_app/

# Type checking
mypy finance_app/
```

## Project Structure

```
finance/
├── main.py                    # Application entry point
├── requirements.txt           # Dependencies
├── pytest.ini                 # Test configuration
├── README.md                  # This file
│
├── finance_app/              # Main package
│   ├── ui/                   # UI components
│   ├── business/             # Business logic
│   ├── data/                 # Data access
│   ├── utils/                # Utilities
│   └── tests/                # Test suite
│
├── docs/                     # Documentation
│   └── ARCHITECTURE.md       # Architecture docs
│
└── logs/                     # Application logs
    └── finance_app.log
```

## Development

### Epic and Story System

We use a structured epic and story system for feature development:

- **Product Owners:** Create epics and user stories in `docs/epics/` and `docs/stories/`
- **Developers:** Pick up stories from `docs/stories/backlog/`
- **Tracking:** Monitor progress in `docs/EPIC_STORY_INDEX.md`

**Quick Start:**
1. **PO:** Read [WORKFLOW_GUIDE.md](docs/WORKFLOW_GUIDE.md) - "Workflow for Product Owners"
2. **Developer:** Read [WORKFLOW_GUIDE.md](docs/WORKFLOW_GUIDE.md) - "Workflow for Developers"
3. **Example:** See [EPIC-001](docs/epics/EPIC-001-search-filter-transactions.md) and [STORY-001](docs/stories/backlog/STORY-001-basic-text-search.md)

### Adding a new feature

1. **Product Owner** creates an epic and breaks it into stories
2. **Developer** picks story from backlog
3. **Data Layer**: Add repository method if needed
4. **Business Layer**: Add service method with validation
5. **UI Layer**: Add UI component
6. **Tests**: Write tests for the new functionality
7. **Documentation**: Update docs
8. **Product Owner** reviews and accepts

### Code Quality Standards

- All code has type hints
- All public methods have docstrings
- Maximum function complexity: 10
- Test coverage target: >80%
- All inputs validated
- All errors handled and logged

## Database

The application uses SQLite with the following tables:

- **accounts**: Bank accounts, cash, credit cards, etc.
- **transactions**: Financial transactions
- **categories**: Income and expense categories

Database file: `finance.db`

## Logging

Logs are written to:
- `logs/finance_app.log` (rotating, 10MB max, 5 backups)
- Console (during development)

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Troubleshooting

### Import errors
Ensure you're in the project root and virtual environment is activated

### Database locked
Check for concurrent connections, restart application

### UI not updating
Verify that `load_data()` is called after modifications

## Roadmap

### Phase 1: Testing & Quality (Current)
- [x] Layered architecture
- [x] Type hints
- [x] Test infrastructure
- [ ] 80%+ test coverage
- [ ] CI/CD pipeline

### Phase 2: Performance
- [ ] Qt Model/View for tables
- [ ] Pagination for large datasets
- [ ] Query optimization
- [ ] Caching layer

### Phase 3: Features
- [ ] Search and filters
- [ ] Reporting and charts
- [ ] Recurring transactions
- [ ] Budget management
- [ ] Multi-currency support
- [ ] Import/Export (CSV, OFX)

### Phase 4: Production
- [ ] Database encryption
- [ ] User authentication
- [ ] Backup/restore
- [ ] Packaging for distribution
- [ ] Auto-updates

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Run linters before committing

## License

Private project - All rights reserved

## Version

**Current Version:** 2.0.0
**Architecture:** Layered (UI/Business/Data)
**Status:** Development

---

**Built with ❤️ using Python and PySide6**
