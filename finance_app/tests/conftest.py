"""
Pytest configuration and shared fixtures.
"""
import pytest
import sqlite3
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Provide a temporary database path."""
    return tmp_path / "test_finance.db"


@pytest.fixture
def db_connection(temp_db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """Provide a test database connection."""
    conn = sqlite3.connect(str(temp_db_path))
    yield conn
    conn.close()


@pytest.fixture
def sample_account() -> dict:
    """Provide sample account data."""
    return {
        'name': 'Test Checking',
        'type': 'bank',
        'balance': 1000.00,
        'currency': 'USD'
    }


@pytest.fixture
def sample_transaction() -> dict:
    """Provide sample transaction data."""
    return {
        'account_id': 1,
        'date': '2025-10-21',
        'description': 'Test Transaction',
        'category': 'Groceries',
        'amount': -50.00,
        'type': 'expense'
    }


@pytest.fixture
def sample_category() -> dict:
    """Provide sample category data."""
    return {
        'name': 'Test Category',
        'type': 'expense'
    }
