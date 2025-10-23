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


class EntryType(str, Enum):
    """Journal entry types."""
    TRANSACTION = 'transaction'  # Regular transaction entry
    OPENING_BALANCE = 'opening_balance'  # Opening balance entry
    ADJUSTMENT = 'adjustment'  # Manual adjustment
    TRANSFER = 'transfer'  # Transfer between accounts


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


@dataclass
class JournalEntry:
    """
    Journal entry model for double-entry accounting.

    Each journal entry represents one side of a transaction (debit OR credit).
    Story: US-002A - Journal Entry Foundation
    """
    id: Optional[int]
    account_id: int
    entry_date: str  # YYYY-MM-DD format
    description: str
    debit_amount: Decimal
    credit_amount: Decimal
    balance_after: Decimal  # Running balance after this entry
    entry_type: EntryType
    transaction_id: Optional[int] = None  # Links to transactions table
    group_id: Optional[int] = None  # Links to transaction_groups (US-002B)
    reference_number: Optional[str] = None  # Check number, invoice number, etc.
    is_reconciled: bool = False
    reconciliation_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate journal entry and ensure types are correct."""
        # Convert to Decimal if needed
        if not isinstance(self.debit_amount, Decimal):
            self.debit_amount = Decimal(str(self.debit_amount))
        if not isinstance(self.credit_amount, Decimal):
            self.credit_amount = Decimal(str(self.credit_amount))
        if not isinstance(self.balance_after, Decimal):
            self.balance_after = Decimal(str(self.balance_after))

        # Convert string to enum if needed
        if isinstance(self.entry_type, str):
            self.entry_type = EntryType(self.entry_type)

        # Validation: Cannot have both debit and credit
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValueError("Journal entry cannot have both debit and credit amounts")

        # Validation: Must have either debit or credit
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValueError("Journal entry must have either debit or credit amount")

        # Validation: Amounts must be non-negative
        if self.debit_amount < 0 or self.credit_amount < 0:
            raise ValueError("Debit and credit amounts must be non-negative")

    @property
    def amount(self) -> Decimal:
        """Get the amount (positive for debit, negative for credit)."""
        return self.debit_amount - self.credit_amount

    @property
    def is_debit(self) -> bool:
        """Check if this is a debit entry."""
        return self.debit_amount > 0

    @property
    def is_credit(self) -> bool:
        """Check if this is a credit entry."""
        return self.credit_amount > 0


@dataclass
class TransactionGroup:
    """
    Transaction group model for balanced multi-entry transactions.

    Groups multiple journal entries together ensuring debits equal credits.
    Used for transfers and other multi-entry transactions.

    Story: US-002B - Balanced Transaction Groups (Phase 2)
    """
    id: Optional[int]
    group_date: str  # YYYY-MM-DD format
    description: str
    total_debits: Decimal
    total_credits: Decimal
    is_balanced: bool = True
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate transaction group and ensure types are correct."""
        # Convert to Decimal if needed
        if not isinstance(self.total_debits, Decimal):
            self.total_debits = Decimal(str(self.total_debits))
        if not isinstance(self.total_credits, Decimal):
            self.total_credits = Decimal(str(self.total_credits))

        # Validation: Total debits and credits must be non-negative
        if self.total_debits < 0:
            raise ValueError("Total debits must be non-negative")
        if self.total_credits < 0:
            raise ValueError("Total credits must be non-negative")

        # Validation: Group must be balanced (debits = credits)
        if self.total_debits != self.total_credits:
            raise ValueError(
                f"Transaction group must be balanced: "
                f"debits ({self.total_debits}) must equal credits ({self.total_credits})"
            )

        # Set is_balanced based on validation
        self.is_balanced = (self.total_debits == self.total_credits)

    @property
    def total_amount(self) -> Decimal:
        """Get the total amount (debits or credits, they should be equal)."""
        return self.total_debits

    @property
    def entry_count(self) -> int:
        """
        Get the expected minimum number of entries (at least 2 for balanced group).
        Note: Actual count must be determined by querying journal_entries.
        """
        return 2  # Minimum for a balanced transaction

    def validate_balance(self) -> bool:
        """Validate that the group is balanced."""
        return self.total_debits == self.total_credits
