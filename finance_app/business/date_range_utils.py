"""
Date range calculation utilities for transaction filtering.

US-012: Date Range Filter - Provides preset date ranges and custom range support.
This module contains pure date calculation logic with no dependencies, making it
easy to test and reuse across the application.

Created: 2025-11-16
Story: US-012 - Date Range Filter (EPIC-002, Sprint 14)
"""

from datetime import date, timedelta
from typing import Tuple


class DateRange:
    """
    Date range calculation utilities for transaction filtering.

    US-012: Provides 12 preset date ranges (Today, Yesterday, Last 7/30 Days,
    This/Last Month/Quarter/Year, All Time) plus support for custom ranges.

    All methods return (from_date, to_date) tuples for use in SQL queries.

    Design:
        - Static methods (no state, functional approach)
        - Pure functions (no side effects, deterministic for given date)
        - Type hints for safety
        - Handles edge cases (leap years, year boundaries, quarter wraps)

    Usage:
        >>> from_date, to_date = DateRange.get_last_month()
        >>> transactions = repo.filter_by_date_range(from_date, to_date)

        >>> from_date, to_date = DateRange.get_this_quarter()
        >>> # Returns (Jan 1, Today) if today is in Q1

    Performance:
        - All calculations < 1ms (pure Python date arithmetic)
        - No database queries, no I/O
        - Suitable for real-time filtering
    """

    @staticmethod
    def get_today() -> Tuple[date, date]:
        """
        Return today's date range.

        Returns:
            Tuple of (today, today) for single-day filtering

        Example:
            If today is 2025-11-16, returns (2025-11-16, 2025-11-16)
        """
        today = date.today()
        return (today, today)

    @staticmethod
    def get_yesterday() -> Tuple[date, date]:
        """
        Return yesterday's date range.

        Returns:
            Tuple of (yesterday, yesterday) for single-day filtering

        Example:
            If today is 2025-11-16, returns (2025-11-15, 2025-11-15)
        """
        yesterday = date.today() - timedelta(days=1)
        return (yesterday, yesterday)

    @staticmethod
    def get_last_n_days(n: int) -> Tuple[date, date]:
        """
        Return last N days including today.

        Args:
            n: Number of days to include (must be > 0)

        Returns:
            Tuple of (n days ago, today)

        Raises:
            ValueError: If n <= 0

        Example:
            If today is 2025-11-16 and n=7:
            Returns (2025-11-10, 2025-11-16) - 7 days total
        """
        if n <= 0:
            raise ValueError(f"Number of days must be positive, got {n}")

        today = date.today()
        start = today - timedelta(days=n - 1)
        return (start, today)

    @staticmethod
    def get_last_7_days() -> Tuple[date, date]:
        """
        Return last 7 days including today.

        Convenience method for common "Last Week" filter.

        Returns:
            Tuple of (7 days ago, today)
        """
        return DateRange.get_last_n_days(7)

    @staticmethod
    def get_last_30_days() -> Tuple[date, date]:
        """
        Return last 30 days including today.

        Convenience method for common "Last Month" filter (approximately).
        Note: This is 30 days, not a calendar month. Use get_last_month()
        for exact previous calendar month.

        Returns:
            Tuple of (30 days ago, today)
        """
        return DateRange.get_last_n_days(30)

    @staticmethod
    def get_this_month() -> Tuple[date, date]:
        """
        Return current month from day 1 to today.

        Returns:
            Tuple of (first day of current month, today)

        Example:
            If today is 2025-11-16:
            Returns (2025-11-01, 2025-11-16)
        """
        today = date.today()
        start = date(today.year, today.month, 1)
        return (start, today)

    @staticmethod
    def get_last_month() -> Tuple[date, date]:
        """
        Return entire previous calendar month.

        Returns:
            Tuple of (first day of previous month, last day of previous month)

        Example:
            If today is 2025-11-16:
            Returns (2025-10-01, 2025-10-31)

        Edge Cases:
            - If today is 2025-01-15: Returns (2024-12-01, 2024-12-31) - year wrap
            - If today is 2024-03-15: Returns (2024-02-01, 2024-02-29) - leap year
        """
        today = date.today()
        # Last day of previous month (go to first day of current month, then back 1 day)
        last_day_prev_month = date(today.year, today.month, 1) - timedelta(days=1)
        # First day of previous month
        first_day_prev_month = date(last_day_prev_month.year, last_day_prev_month.month, 1)
        return (first_day_prev_month, last_day_prev_month)

    @staticmethod
    def get_quarter(year: int, quarter: int) -> Tuple[date, date]:
        """
        Return date range for given quarter (1-4).

        Args:
            year: Year (e.g., 2025)
            quarter: Quarter number (1=Q1, 2=Q2, 3=Q3, 4=Q4)

        Returns:
            Tuple of (first day of quarter, last day of quarter)

        Raises:
            ValueError: If quarter not in 1-4

        Example:
            get_quarter(2025, 1) -> (2025-01-01, 2025-03-31)
            get_quarter(2025, 2) -> (2025-04-01, 2025-06-30)
            get_quarter(2025, 3) -> (2025-07-01, 2025-09-30)
            get_quarter(2025, 4) -> (2025-10-01, 2025-12-31)
        """
        if quarter not in (1, 2, 3, 4):
            raise ValueError(f"Quarter must be 1-4, got {quarter}")

        quarter_starts = {
            1: (year, 1, 1),
            2: (year, 4, 1),
            3: (year, 7, 1),
            4: (year, 10, 1)
        }
        quarter_ends = {
            1: (year, 3, 31),
            2: (year, 6, 30),
            3: (year, 9, 30),
            4: (year, 12, 31)
        }

        start = date(*quarter_starts[quarter])
        end = date(*quarter_ends[quarter])
        return (start, end)

    @staticmethod
    def get_this_quarter() -> Tuple[date, date]:
        """
        Return current quarter from quarter start to today.

        Returns:
            Tuple of (first day of current quarter, today)

        Example:
            If today is 2025-11-16 (Q4):
            Returns (2025-10-01, 2025-11-16)

            If today is 2025-02-15 (Q1):
            Returns (2025-01-01, 2025-02-15)
        """
        today = date.today()
        # Calculate current quarter (1-4)
        quarter = (today.month - 1) // 3 + 1
        start_date, _ = DateRange.get_quarter(today.year, quarter)
        return (start_date, today)

    @staticmethod
    def get_last_quarter() -> Tuple[date, date]:
        """
        Return entire previous quarter.

        Returns:
            Tuple of (first day of previous quarter, last day of previous quarter)

        Example:
            If today is 2025-11-16 (Q4):
            Returns (2025-07-01, 2025-09-30) - Q3

        Edge Case - Year Wrap:
            If today is 2025-01-15 (Q1):
            Returns (2024-10-01, 2024-12-31) - Q4 of previous year
        """
        today = date.today()
        current_quarter = (today.month - 1) // 3 + 1

        if current_quarter == 1:
            # Last quarter is Q4 of previous year
            return DateRange.get_quarter(today.year - 1, 4)
        else:
            # Last quarter is previous quarter of current year
            return DateRange.get_quarter(today.year, current_quarter - 1)

    @staticmethod
    def get_this_year() -> Tuple[date, date]:
        """
        Return current year from January 1 to today.

        Returns:
            Tuple of (first day of current year, today)

        Example:
            If today is 2025-11-16:
            Returns (2025-01-01, 2025-11-16)
        """
        today = date.today()
        start = date(today.year, 1, 1)
        return (start, today)

    @staticmethod
    def get_last_year() -> Tuple[date, date]:
        """
        Return entire previous calendar year.

        Returns:
            Tuple of (first day of previous year, last day of previous year)

        Example:
            If today is 2025-11-16:
            Returns (2024-01-01, 2024-12-31)
        """
        today = date.today()
        prev_year = today.year - 1
        return (date(prev_year, 1, 1), date(prev_year, 12, 31))

    @staticmethod
    def get_all_time() -> Tuple[date, date]:
        """
        Return maximum possible date range for "All Time" filter.

        Returns:
            Tuple of (very old date, far future date)

        Note:
            Uses date(1900, 1, 1) to date(2099, 12, 31) to cover
            reasonable transaction history without hitting date limits.

        Usage:
            Used when user selects "All Time" to show all transactions
            without date filtering. Repository layer should optimize this
            to skip the WHERE clause entirely.
        """
        return (date(1900, 1, 1), date(2099, 12, 31))

    @staticmethod
    def validate_custom_range(from_date: date, to_date: date) -> None:
        """
        Validate a custom date range.

        Args:
            from_date: Start date
            to_date: End date

        Raises:
            ValueError: If from_date > to_date

        Example:
            validate_custom_range(date(2025, 1, 1), date(2025, 12, 31))  # OK
            validate_custom_range(date(2025, 12, 31), date(2025, 1, 1))  # Raises
        """
        if from_date > to_date:
            raise ValueError(
                f"From date ({from_date}) must be <= To date ({to_date})"
            )
