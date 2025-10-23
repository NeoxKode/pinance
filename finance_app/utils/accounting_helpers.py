"""
Accounting helper functions for normal balance calculations.

This module provides utilities for determining and validating normal balances
based on account types, following double-entry accounting principles:

- Assets & Expenses: Debit normal balance (increases with debits)
- Liabilities, Equity & Income: Credit normal balance (increases with credits)

These functions are used throughout the application to ensure correct
journal entry creation and accounting accuracy.
"""

from finance_app.data.models import AccountType, NormalBalance
from finance_app.utils.exceptions import ValidationError


def get_normal_balance(account_type: AccountType) -> NormalBalance:
    """
    Determine the normal balance side for an account type.

    In double-entry accounting, each account type has a "normal balance" side:
    - Assets & Expenses naturally increase with debits (debit normal balance)
    - Liabilities, Equity & Income naturally increase with credits (credit normal balance)

    Args:
        account_type: The account type to check

    Returns:
        NormalBalance.DEBIT for assets/expenses, NormalBalance.CREDIT for others

    Example:
        >>> get_normal_balance(AccountType.ASSET)
        NormalBalance.DEBIT
        >>> get_normal_balance(AccountType.LIABILITY)
        NormalBalance.CREDIT
    """
    if account_type in (AccountType.ASSET, AccountType.EXPENSE):
        return NormalBalance.DEBIT
    else:  # LIABILITY, EQUITY, INCOME
        return NormalBalance.CREDIT


def validate_normal_balance(
    account_type: AccountType,
    normal_balance: NormalBalance
) -> None:
    """
    Validate that a normal balance matches its account type.

    Raises an error if the normal balance doesn't match the expected value
    for the given account type.

    Args:
        account_type: The account type
        normal_balance: The normal balance to validate

    Raises:
        ValidationError: If normal balance doesn't match account type

    Example:
        >>> validate_normal_balance(AccountType.ASSET, NormalBalance.DEBIT)
        # No error - correct
        >>> validate_normal_balance(AccountType.ASSET, NormalBalance.CREDIT)
        # Raises ValidationError - assets must have debit normal balance
    """
    expected = get_normal_balance(account_type)
    if normal_balance != expected:
        raise ValidationError(
            f"{account_type.value.capitalize()} accounts must have "
            f"{expected.value} normal balance, got {normal_balance.value}"
        )


def is_debit_account(normal_balance: NormalBalance) -> bool:
    """
    Check if an account has debit normal balance.

    Args:
        normal_balance: The normal balance to check

    Returns:
        True if debit normal balance, False otherwise

    Example:
        >>> is_debit_account(NormalBalance.DEBIT)
        True
        >>> is_debit_account(NormalBalance.CREDIT)
        False
    """
    return normal_balance == NormalBalance.DEBIT


def is_credit_account(normal_balance: NormalBalance) -> bool:
    """
    Check if an account has credit normal balance.

    Args:
        normal_balance: The normal balance to check

    Returns:
        True if credit normal balance, False otherwise

    Example:
        >>> is_credit_account(NormalBalance.CREDIT)
        True
        >>> is_credit_account(NormalBalance.DEBIT)
        False
    """
    return normal_balance == NormalBalance.CREDIT


def increases_with_debit(normal_balance: NormalBalance) -> bool:
    """
    Check if an account increases with debit entries.

    Accounts with debit normal balance (assets, expenses) increase with debits.
    Accounts with credit normal balance (liabilities, equity, income) decrease with debits.

    Args:
        normal_balance: The normal balance to check

    Returns:
        True if account increases with debits, False otherwise

    Example:
        >>> increases_with_debit(NormalBalance.DEBIT)
        True  # Assets and expenses increase with debits
        >>> increases_with_debit(NormalBalance.CREDIT)
        False  # Liabilities, equity, income decrease with debits
    """
    return normal_balance == NormalBalance.DEBIT


def increases_with_credit(normal_balance: NormalBalance) -> bool:
    """
    Check if an account increases with credit entries.

    Accounts with credit normal balance (liabilities, equity, income) increase with credits.
    Accounts with debit normal balance (assets, expenses) decrease with credits.

    Args:
        normal_balance: The normal balance to check

    Returns:
        True if account increases with credits, False otherwise

    Example:
        >>> increases_with_credit(NormalBalance.CREDIT)
        True  # Liabilities, equity, income increase with credits
        >>> increases_with_credit(NormalBalance.DEBIT)
        False  # Assets and expenses decrease with credits
    """
    return normal_balance == NormalBalance.CREDIT
