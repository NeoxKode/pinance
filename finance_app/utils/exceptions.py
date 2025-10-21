"""
Custom exceptions for the finance application.
"""


class FinanceAppError(Exception):
    """Base exception for all application errors."""
    pass


class DatabaseError(FinanceAppError):
    """Database operation errors."""
    pass


class ValidationError(FinanceAppError):
    """Data validation errors."""
    pass


class BusinessRuleError(FinanceAppError):
    """Business logic rule violations."""
    pass


class NotFoundError(FinanceAppError):
    """Resource not found errors."""
    pass


class DuplicateError(FinanceAppError):
    """Duplicate resource errors."""
    pass
