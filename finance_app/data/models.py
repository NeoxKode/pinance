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
    """Transaction model with split transaction support (US-002C)."""
    id: Optional[int]
    account_id: int
    date: str  # YYYY-MM-DD format
    description: str
    category: str
    amount: Decimal
    type: str  # 'income' or 'expense'
    is_split: bool = False  # True if transaction has splits
    split_count: int = 0  # Number of splits (0 if not split)
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
    """Category model with optional account linkage (US-002C Option A)."""
    id: Optional[int]
    name: str
    type: str  # 'income' or 'expense'
    account_id: Optional[int] = None  # Links category to account for journal entries
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


@dataclass
class TransactionSplit:
    """
    Transaction split model for splitting a single transaction across multiple categories.

    Represents a single split within a transaction. For example, in a $100 Walmart
    transaction split into Groceries ($70) and Household ($30), each would be a
    TransactionSplit.

    Story: US-002C - Split Transactions (Day 1)

    Key Design Decisions:
    - Split amounts are ALWAYS positive (sign comes from parent transaction type)
    - Each split links to a category (which links to an account via account_id)
    - Splits are ordered for display consistency
    - Optional memo for per-split notes
    """
    id: Optional[int]
    transaction_id: int
    group_id: int  # Links to transaction_groups for double-entry
    split_order: int
    category_id: int
    amount: Decimal
    memo: Optional[str] = None
    account_id: Optional[int] = None  # For multi-account splits (future)
    split_type: str = 'manual'  # 'manual', 'paycheck', 'shopping', 'bill'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate split data and ensure types are correct."""
        # Convert to Decimal if needed
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))

        # Validation: Split amount must be positive
        if self.amount <= 0:
            raise ValueError(f"Split amount must be positive, got {self.amount}")

        # Validation: Split order must be non-negative
        if self.split_order < 0:
            raise ValueError(f"Split order must be non-negative, got {self.split_order}")

        # Validation: Split type must be valid
        valid_types = {'manual', 'paycheck', 'shopping', 'bill'}
        if self.split_type not in valid_types:
            raise ValueError(f"Split type must be one of {valid_types}, got {self.split_type}")

        # Trim memo if provided
        if self.memo:
            self.memo = self.memo.strip()[:500]  # Limit memo length

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"TransactionSplit(id={self.id}, amount={self.amount}, category={self.category_id})"


@dataclass
class SplitTransaction:
    """
    Split transaction model containing parent transaction and all child splits.

    Represents a complete split transaction with validation that splits balance
    to the transaction amount.

    Example:
        Transaction: Walmart purchase -$127.50
        Splits:
            - Groceries: $85.00
            - Household: $32.50
            - Personal Care: $10.00
            Total: $127.50 ✓ Balanced

    Story: US-002C - Split Transactions (Day 1)
    """
    transaction: Transaction
    splits: list  # List[TransactionSplit]

    def __post_init__(self):
        """Validate split transaction."""
        # Validation: Must have at least 2 splits
        if len(self.splits) < 2:
            raise ValueError(
                f"Split transaction must have at least 2 splits, got {len(self.splits)}"
            )

        # Validation: All splits must belong to this transaction
        for split in self.splits:
            if split.transaction_id != self.transaction.id:
                raise ValueError(
                    f"Split {split.id} belongs to transaction {split.transaction_id}, "
                    f"not {self.transaction.id}"
                )

    @property
    def total_splits(self) -> Decimal:
        """Calculate total of all splits."""
        return sum(split.amount for split in self.splits)

    @property
    def is_balanced(self) -> bool:
        """
        Check if splits equal transaction amount.

        Uses 1-cent tolerance for floating point comparison.
        """
        return abs(self.total_splits - abs(self.transaction.amount)) < Decimal('0.01')

    @property
    def balance_difference(self) -> Decimal:
        """
        Get difference between transaction and splits.

        Useful for error messages:
        - Positive: Need to add more splits
        - Negative: Total splits exceed transaction amount
        - Zero: Balanced ✓
        """
        return abs(self.transaction.amount) - self.total_splits

    @property
    def split_count(self) -> int:
        """Get number of splits."""
        return len(self.splits)

    def validate_balance(self) -> bool:
        """
        Validate that splits balance to transaction amount.

        Returns:
            True if balanced (within 1-cent tolerance)

        Raises:
            ValueError: If splits don't balance with detailed error message
        """
        if not self.is_balanced:
            raise ValueError(
                f"Splits total ${self.total_splits} doesn't match transaction "
                f"amount ${abs(self.transaction.amount)} "
                f"(difference: ${abs(self.balance_difference)})"
            )
        return True

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "✓ Balanced" if self.is_balanced else f"⚠ Off by ${self.balance_difference}"
        return (
            f"SplitTransaction(id={self.transaction.id}, "
            f"amount={self.transaction.amount}, "
            f"splits={self.split_count}, "
            f"{status})"
        )


@dataclass
class PaycheckSplit:
    """
    Template model for paycheck split transactions.

    Represents a paycheck with gross pay and various deductions, automatically
    calculating net pay. This is the most common use case for split transactions.

    Example:
        Gross Pay: $5,000.00
        - Federal Tax: $750.00
        - State Tax: $250.00
        - Social Security: $310.00
        - Medicare: $72.50
        - 401(k): $500.00
        - Health Insurance: $200.00
        = Net Pay: $2,917.50

    Story: US-002C - Split Transactions (Day 1)
    """
    gross_pay: Decimal
    federal_tax: Decimal
    state_tax: Decimal
    social_security: Decimal
    medicare: Decimal
    retirement_401k: Decimal
    health_insurance: Decimal
    other_deductions: Optional[list] = None  # List[Tuple[str, Decimal]]

    def __post_init__(self):
        """Validate paycheck data and ensure types are correct."""
        # Convert all to Decimal
        fields = [
            'gross_pay', 'federal_tax', 'state_tax',
            'social_security', 'medicare', 'retirement_401k', 'health_insurance'
        ]

        for field in fields:
            value = getattr(self, field)
            if not isinstance(value, Decimal):
                setattr(self, field, Decimal(str(value)))

        # Validation: Gross pay must be positive
        if self.gross_pay <= 0:
            raise ValueError(f"Gross pay must be positive, got {self.gross_pay}")

        # Validation: Deductions must be non-negative
        deductions = [
            ('federal_tax', self.federal_tax),
            ('state_tax', self.state_tax),
            ('social_security', self.social_security),
            ('medicare', self.medicare),
            ('retirement_401k', self.retirement_401k),
            ('health_insurance', self.health_insurance),
        ]

        for name, value in deductions:
            if value < 0:
                raise ValueError(f"{name} must be non-negative, got {value}")

        # Validation: Total deductions cannot exceed gross pay
        if self.total_deductions > self.gross_pay:
            raise ValueError(
                f"Total deductions ${self.total_deductions} exceed "
                f"gross pay ${self.gross_pay}"
            )

        # Convert other_deductions to Decimal
        if self.other_deductions:
            self.other_deductions = [
                (name, Decimal(str(amt)) if not isinstance(amt, Decimal) else amt)
                for name, amt in self.other_deductions
            ]

    @property
    def total_deductions(self) -> Decimal:
        """Calculate total deductions."""
        total = (
            self.federal_tax +
            self.state_tax +
            self.social_security +
            self.medicare +
            self.retirement_401k +
            self.health_insurance
        )

        if self.other_deductions:
            total += sum(amt for _, amt in self.other_deductions)

        return total

    @property
    def net_pay(self) -> Decimal:
        """Calculate net pay (gross - all deductions)."""
        return self.gross_pay - self.total_deductions

    @property
    def deduction_count(self) -> int:
        """Get number of deductions."""
        base_count = 6  # Standard deductions
        other_count = len(self.other_deductions) if self.other_deductions else 0
        return base_count + other_count

    @property
    def effective_tax_rate(self) -> Decimal:
        """Calculate effective tax rate (total taxes / gross pay)."""
        total_taxes = self.federal_tax + self.state_tax + self.social_security + self.medicare
        if self.gross_pay == 0:
            return Decimal('0')
        return (total_taxes / self.gross_pay) * 100

    def to_splits(self) -> list:
        """
        Convert paycheck to list of split dictionaries.

        Returns:
            List of dicts with 'category_id', 'amount', 'memo' keys
            Note: category_id will need to be mapped by the service layer
        """
        splits = []

        # Income split (gross pay)
        splits.append({
            'category': 'Salary',
            'amount': self.gross_pay,
            'memo': 'Gross Pay'
        })

        # Deduction splits
        if self.federal_tax > 0:
            splits.append({
                'category': 'Federal Tax',
                'amount': self.federal_tax,
                'memo': 'Federal Income Tax'
            })

        if self.state_tax > 0:
            splits.append({
                'category': 'State Tax',
                'amount': self.state_tax,
                'memo': 'State Income Tax'
            })

        if self.social_security > 0:
            splits.append({
                'category': 'Social Security Tax',
                'amount': self.social_security,
                'memo': 'Social Security (FICA)'
            })

        if self.medicare > 0:
            splits.append({
                'category': 'Medicare Tax',
                'amount': self.medicare,
                'memo': 'Medicare Tax'
            })

        if self.retirement_401k > 0:
            splits.append({
                'category': '401(k) Contribution',
                'amount': self.retirement_401k,
                'memo': '401(k) Retirement Contribution'
            })

        if self.health_insurance > 0:
            splits.append({
                'category': 'Health Insurance',
                'amount': self.health_insurance,
                'memo': 'Health Insurance Premium'
            })

        # Other deductions
        if self.other_deductions:
            for name, amount in self.other_deductions:
                if amount > 0:
                    splits.append({
                        'category': name,
                        'amount': amount,
                        'memo': f'Other Deduction: {name}'
                    })

        return splits

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"PaycheckSplit(gross=${self.gross_pay}, "
            f"deductions=${self.total_deductions}, "
            f"net=${self.net_pay})"
        )
