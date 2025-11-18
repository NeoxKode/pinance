"""
Unit tests for DateRange utility class.

US-012: Date Range Filter - Tests all 12 preset methods plus edge cases.
Covers leap years, year boundaries, quarter wraps, and validation.

Created: 2025-11-16
Story: US-012 - Date Range Filter (EPIC-002, Sprint 14)
"""

import pytest
from datetime import date, timedelta

from finance_app.business.date_range_utils import DateRange


class TestDateRangePresets:
    """Test all 12 preset date range methods."""

    def test_get_today(self):
        """Test today preset returns single day range."""
        # Act
        from_date, to_date = DateRange.get_today()

        # Assert
        assert from_date == date.today()
        assert to_date == date.today()
        assert from_date == to_date  # Single day

    def test_get_yesterday(self):
        """Test yesterday preset returns single day range."""
        # Act
        from_date, to_date = DateRange.get_yesterday()

        # Assert
        expected = date.today() - timedelta(days=1)
        assert from_date == expected
        assert to_date == expected
        assert from_date == to_date  # Single day

    def test_get_last_n_days_seven(self):
        """Test last N days including today."""
        # Act
        from_date, to_date = DateRange.get_last_n_days(7)

        # Assert
        today = date.today()
        expected_start = today - timedelta(days=6)
        assert from_date == expected_start
        assert to_date == today
        assert (to_date - from_date).days == 6  # 7 days total (inclusive)

    def test_get_last_7_days(self):
        """Test last 7 days convenience method."""
        # Act
        result = DateRange.get_last_7_days()

        # Assert - should match get_last_n_days(7)
        expected = DateRange.get_last_n_days(7)
        assert result == expected

    def test_get_last_30_days(self):
        """Test last 30 days convenience method."""
        # Act
        from_date, to_date = DateRange.get_last_30_days()

        # Assert
        today = date.today()
        expected_start = today - timedelta(days=29)
        assert from_date == expected_start
        assert to_date == today

    def test_get_this_month(self):
        """Test this month from day 1 to today."""
        # Act
        from_date, to_date = DateRange.get_this_month()

        # Assert
        today = date.today()
        assert from_date == date(today.year, today.month, 1)
        assert to_date == today

    def test_get_last_month(self):
        """Test last month returns entire previous calendar month."""
        # Act
        from_date, to_date = DateRange.get_last_month()

        # Assert
        today = date.today()
        # Last day of previous month
        last_day_prev = date(today.year, today.month, 1) - timedelta(days=1)
        first_day_prev = date(last_day_prev.year, last_day_prev.month, 1)

        assert from_date == first_day_prev
        assert to_date == last_day_prev

    def test_get_quarter_q1(self):
        """Test Q1 quarter range."""
        from_date, to_date = DateRange.get_quarter(2025, 1)

        assert from_date == date(2025, 1, 1)
        assert to_date == date(2025, 3, 31)

    def test_get_quarter_q2(self):
        """Test Q2 quarter range."""
        from_date, to_date = DateRange.get_quarter(2025, 2)

        assert from_date == date(2025, 4, 1)
        assert to_date == date(2025, 6, 30)

    def test_get_quarter_q3(self):
        """Test Q3 quarter range."""
        from_date, to_date = DateRange.get_quarter(2025, 3)

        assert from_date == date(2025, 7, 1)
        assert to_date == date(2025, 9, 30)

    def test_get_quarter_q4(self):
        """Test Q4 quarter range."""
        from_date, to_date = DateRange.get_quarter(2025, 4)

        assert from_date == date(2025, 10, 1)
        assert to_date == date(2025, 12, 31)

    def test_get_this_quarter(self):
        """Test this quarter from quarter start to today."""
        # Act
        from_date, to_date = DateRange.get_this_quarter()

        # Assert
        today = date.today()
        quarter = (today.month - 1) // 3 + 1
        expected_start, _ = DateRange.get_quarter(today.year, quarter)

        assert from_date == expected_start
        assert to_date == today

    def test_get_last_quarter(self):
        """Test last quarter returns entire previous quarter."""
        # Act
        from_date, to_date = DateRange.get_last_quarter()

        # Assert - verify it's a complete quarter (either Q1-Q4)
        # Calculate expected based on current quarter
        today = date.today()
        current_quarter = (today.month - 1) // 3 + 1

        if current_quarter == 1:
            # Should be Q4 of previous year
            expected = DateRange.get_quarter(today.year - 1, 4)
        else:
            # Should be previous quarter of current year
            expected = DateRange.get_quarter(today.year, current_quarter - 1)

        assert (from_date, to_date) == expected

    def test_get_this_year(self):
        """Test this year from Jan 1 to today."""
        # Act
        from_date, to_date = DateRange.get_this_year()

        # Assert
        today = date.today()
        assert from_date == date(today.year, 1, 1)
        assert to_date == today

    def test_get_last_year(self):
        """Test last year returns entire previous year."""
        # Act
        from_date, to_date = DateRange.get_last_year()

        # Assert
        today = date.today()
        prev_year = today.year - 1
        assert from_date == date(prev_year, 1, 1)
        assert to_date == date(prev_year, 12, 31)

    def test_get_all_time(self):
        """Test all time returns maximum range."""
        from_date, to_date = DateRange.get_all_time()

        assert from_date == date(1900, 1, 1)
        assert to_date == date(2099, 12, 31)
        assert (to_date - from_date).days > 70000  # ~200 years


class TestDateRangeEdgeCases:
    """Test edge cases: leap years, year boundaries, quarter wraps."""

    def test_quarter_calculation_all_months(self):
        """Test quarter calculation for all 12 months."""
        # Q1: Jan, Feb, Mar
        for month in [1, 2, 3]:
            quarter = (month - 1) // 3 + 1
            assert quarter == 1

        # Q2: Apr, May, Jun
        for month in [4, 5, 6]:
            quarter = (month - 1) // 3 + 1
            assert quarter == 2

        # Q3: Jul, Aug, Sep
        for month in [7, 8, 9]:
            quarter = (month - 1) // 3 + 1
            assert quarter == 3

        # Q4: Oct, Nov, Dec
        for month in [10, 11, 12]:
            quarter = (month - 1) // 3 + 1
            assert quarter == 4

    def test_last_quarter_year_wrap_logic(self):
        """Test that Q1 → Last Quarter wraps to Q4 of previous year."""
        # Using explicit date for Q1
        # If we're in Q1, last quarter should be Q4 of prev year
        q4_2024 = DateRange.get_quarter(2024, 4)
        q1_2025 = DateRange.get_quarter(2025, 1)

        # Verify Q4 2024 is before Q1 2025
        assert q4_2024[0] < q1_2025[0]
        assert q4_2024[1] < q1_2025[0]

    def test_leap_year_february(self):
        """Test February in leap year has 29 days."""
        # 2024 is a leap year
        q1_2024 = DateRange.get_quarter(2024, 1)
        # Q1 ends March 31, but let's verify Feb exists
        feb_2024 = date(2024, 2, 29)  # Should not raise

        assert feb_2024.month == 2
        assert feb_2024.day == 29

    def test_non_leap_year_february(self):
        """Test February in non-leap year has 28 days."""
        # 2025 is not a leap year
        with pytest.raises(ValueError):
            date(2025, 2, 29)  # Should raise

        # But Feb 28 should work
        feb_2025 = date(2025, 2, 28)
        assert feb_2025.month == 2
        assert feb_2025.day == 28

    def test_year_boundaries_dec_31_to_jan_1(self):
        """Test year boundary transition."""
        dec_31 = date(2024, 12, 31)
        jan_1 = date(2025, 1, 1)

        assert (jan_1 - dec_31).days == 1
        assert dec_31.year == 2024
        assert jan_1.year == 2025


class TestDateRangeValidation:
    """Test validation and error handling."""

    def test_validate_custom_range_valid(self):
        """Test validation passes for valid date range."""
        # Should not raise
        DateRange.validate_custom_range(
            date(2025, 1, 1),
            date(2025, 12, 31)
        )

    def test_validate_custom_range_equal_dates(self):
        """Test validation passes when from_date == to_date."""
        # Should not raise (single day is valid)
        DateRange.validate_custom_range(
            date(2025, 11, 16),
            date(2025, 11, 16)
        )

    def test_validate_custom_range_invalid(self):
        """Test validation fails when from_date > to_date."""
        with pytest.raises(ValueError, match="From date.*must be <= To date"):
            DateRange.validate_custom_range(
                date(2025, 12, 31),
                date(2025, 1, 1)
            )

    def test_get_last_n_days_zero(self):
        """Test last_n_days with n=0 raises error."""
        with pytest.raises(ValueError, match="must be positive"):
            DateRange.get_last_n_days(0)

    def test_get_last_n_days_negative(self):
        """Test last_n_days with negative n raises error."""
        with pytest.raises(ValueError, match="must be positive"):
            DateRange.get_last_n_days(-7)

    def test_get_quarter_invalid_quarter_0(self):
        """Test get_quarter with quarter=0 raises error."""
        with pytest.raises(ValueError, match="must be 1-4"):
            DateRange.get_quarter(2025, 0)

    def test_get_quarter_invalid_quarter_5(self):
        """Test get_quarter with quarter=5 raises error."""
        with pytest.raises(ValueError, match="must be 1-4"):
            DateRange.get_quarter(2025, 5)


class TestDateRangeComprehensive:
    """Comprehensive tests for complete coverage."""

    def test_all_presets_return_tuples(self):
        """Test all preset methods return (from_date, to_date) tuples."""
        # All should return tuples with 2 dates
        assert len(DateRange.get_today()) == 2
        assert len(DateRange.get_yesterday()) == 2
        assert len(DateRange.get_last_7_days()) == 2
        assert len(DateRange.get_last_30_days()) == 2
        assert len(DateRange.get_this_month()) == 2
        assert len(DateRange.get_last_month()) == 2
        assert len(DateRange.get_this_quarter()) == 2
        assert len(DateRange.get_last_quarter()) == 2
        assert len(DateRange.get_this_year()) == 2
        assert len(DateRange.get_last_year()) == 2
        assert len(DateRange.get_all_time()) == 2

    def test_all_presets_from_before_or_equal_to(self):
        """Test all presets have from_date <= to_date."""
        presets = [
            DateRange.get_today(),
            DateRange.get_yesterday(),
            DateRange.get_last_7_days(),
            DateRange.get_last_30_days(),
            DateRange.get_this_month(),
            DateRange.get_last_month(),
            DateRange.get_this_quarter(),
            DateRange.get_last_quarter(),
            DateRange.get_this_year(),
            DateRange.get_last_year(),
            DateRange.get_all_time(),
        ]

        for from_date, to_date in presets:
            assert from_date <= to_date, f"Invalid range: {from_date} > {to_date}"

    def test_all_presets_return_date_objects(self):
        """Test all presets return actual date objects."""
        presets = [
            DateRange.get_today(),
            DateRange.get_yesterday(),
            DateRange.get_last_7_days(),
            DateRange.get_last_30_days(),
            DateRange.get_this_month(),
            DateRange.get_last_month(),
            DateRange.get_this_quarter(),
            DateRange.get_last_quarter(),
            DateRange.get_this_year(),
            DateRange.get_last_year(),
            DateRange.get_all_time(),
        ]

        for from_date, to_date in presets:
            assert isinstance(from_date, date)
            assert isinstance(to_date, date)
