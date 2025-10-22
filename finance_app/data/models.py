"""
Data models for the finance application.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class AccountType(str, Enum):
    """Primary account types for double-entry accounting."""
    ASSET = 'asset'
    LIABILITY = 'liability'
    EQUITY = 'equity'
    INCOME = 'income'
    EXPENSE = 'expense'


class AccountSubtype(str, Enum):
    """Account subtypes for classification."""
    # Asset subtypes
    CHECKING = 'checking'
    SAVINGS = 'savings'
    CASH = 'cash'
    INVESTMENT = 'investment'
    OTHER_ASSET = 'other_asset'

    # Liability subtypes
    CREDIT_CARD = 'credit_card'
    LOAN = 'loan'
    MORTGAGE = 'mortgage'
    LINE_OF_CREDIT = 'line_of_credit'
    OTHER_LIABILITY = 'other_liability'

    # Equity subtypes
    OPENING_BALANCE = 'opening_balance'
    RETAINED_EARNINGS = 'retained_earnings'

    # Income subtypes
    SALARY = 'salary'
    BUSINESS_INCOME = 'business_income'
    INTEREST = 'interest'
    DIVIDENDS = 'dividends'
    OTHER_INCOME = 'other_income'

    # Expense subtypes (typically use category names)
    EXPENSE_CATEGORY = 'expense_category'


class NormalBalance(str, Enum):
    """Normal balance type for double-entry accounting."""
    DEBIT = 'debit'
    CREDIT = 'credit'


@dataclass
class Account:
    """Account model with double-entry support."""
    id: Optional[int]
    name: str
    account_type: AccountType
    account_subtype: AccountSubtype
    balance: Decimal
    normal_balance: NormalBalance
    currency: str = 'USD'
    parent_account_id: Optional[int] = None
    legacy_type: Optional[str] = None  # For migration compatibility
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Ensure balance is Decimal and types are enums."""
        if not isinstance(self.balance, Decimal):
            self.balance = Decimal(str(self.balance))

        if isinstance(self.account_type, str):
            self.account_type = AccountType(self.account_type)

        if isinstance(self.account_subtype, str):
            self.account_subtype = AccountSubtype(self.account_subtype)

        if isinstance(self.normal_balance, str):
            self.normal_balance = NormalBalance(self.normal_balance)


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
