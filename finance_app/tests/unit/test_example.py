"""
Example unit test - placeholder for actual tests.
"""
import pytest


class TestExample:
    """Example test class."""

    def test_placeholder(self):
        """Placeholder test to ensure pytest works."""
        assert True

    def test_basic_math(self):
        """Test basic operations."""
        assert 1 + 1 == 2
        assert 2 * 3 == 6

    @pytest.mark.unit
    def test_with_marker(self):
        """Test with unit marker."""
        assert "test" in "testing"
