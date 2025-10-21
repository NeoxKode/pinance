"""
Data models for the finance application.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Account:
    """Account model."""
    id: Optional[int]
    name: str
    type: str  # 'bank', 'cash', 'credit', 'investment'
    balance: Decimal
    currency: str = 'USD'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Ensure balance is Decimal."""
        if not isinstance(self.balance, Decimal):
            self.balance = Decimal(str(self.balance))


@dataclass
class Transaction:
    """Transaction model."""
    id: Optional[int]
    account_id: int
    date: str  # YYYY-MM-DD format
    description: str
    category: str
    amount: Decimal
    type: str  # 'income' or 'expense'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Ensure amount is Decimal."""
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))

    @property
    def is_expense(self) -> bool:
        """Check if transaction is an expense."""
        return self.type == 'expense' or self.amount < 0

    @property
    def is_income(self) -> bool:
        """Check if transaction is income."""
        return self.type == 'income' or self.amount > 0


@dataclass
class Category:
    """Category model."""
    id: Optional[int]
    name: str
    type: str  # 'income' or 'expense'
    created_at: Optional[datetime] = None

    def __str__(self) -> str:
        return self.name
