"""
Unit tests for US-009 Account Color Coding & Visual Indicators.

Tests cover:
- Color validation and WCAG AA compliance
- Repository methods (update_color, toggle_favorite, update_display_order)
- Service methods (color update, favorite toggle, reorder)
- Default color assignment
- Error handling and edge cases

Sprint: 10
Story: US-009
"""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from finance_app.data.models import Account, AccountType, AccountSubtype, NormalBalance
from finance_app.business.account_service import AccountService
from finance_app.ui.styles import (
    AccountColors,
    get_default_color_for_account_type,
    is_valid_hex_color,
    is_wcag_aa_compliant,
    validate_and_fix_color
)
from finance_app.utils.exceptions import ValidationError, NotFoundError


class TestColorValidation:
    """Test color validation functions."""

    def test_valid_hex_color_formats(self):
        """Test valid hex color format validation."""
        assert is_valid_hex_color('#2563EB') is True
        assert is_valid_hex_color('#DC2626') is True
        assert is_valid_hex_color('#6D28D9') is True
        assert is_valid_hex_color('#B45309') is True
        assert is_valid_hex_color('#C2410C') is True
        assert is_valid_hex_color('#000000') is True
        assert is_valid_hex_color('#FFFFFF') is True

    def test_invalid_hex_color_formats(self):
        """Test invalid hex color format validation."""
        assert is_valid_hex_color('') is False
        assert is_valid_hex_color('invalid') is False
        assert is_valid_hex_color('2563EB') is False  # Missing #
        assert is_valid_hex_color('#2563E') is False  # Too short
        assert is_valid_hex_color('#2563EBF') is False  # Too long
        assert is_valid_hex_color('#GGGGGG') is False  # Invalid hex chars
        assert is_valid_hex_color(None) is False

    def test_wcag_aa_compliant_colors(self):
        """Test WCAG AA compliance check for account type colors."""
        # All default colors should pass WCAG AA (≥4.5:1 with white)
        assert is_wcag_aa_compliant(AccountColors.ASSET, '#FFFFFF') is True  # 5.17:1
        assert is_wcag_aa_compliant(AccountColors.LIABILITY, '#FFFFFF') is True  # 4.83:1
        assert is_wcag_aa_compliant(AccountColors.EQUITY, '#FFFFFF') is True  # 5.87:1
        assert is_wcag_aa_compliant(AccountColors.INCOME, '#FFFFFF') is True  # 5.02:1
        assert is_wcag_aa_compliant(AccountColors.EXPENSE, '#FFFFFF') is True  # 5.18:1

    def test_wcag_aa_failing_colors(self):
        """Test colors that fail WCAG AA compliance."""
        # Light colors fail with white text
        assert is_wcag_aa_compliant('#FFFF00', '#FFFFFF') is False  # Yellow
        assert is_wcag_aa_compliant('#00FFFF', '#FFFFFF') is False  # Cyan
        assert is_wcag_aa_compliant('#FF00FF', '#FFFFFF') is False  # Magenta

    def test_validate_and_fix_color(self):
        """Test color validation with fallback."""
        # Valid colors pass through
        assert validate_and_fix_color('#2563EB') == '#2563EB'

        # Invalid colors return fallback
        assert validate_and_fix_color('invalid', fallback='#DC2626') == '#DC2626'
        assert validate_and_fix_color('', fallback='#6D28D9') == '#6D28D9'
        assert validate_and_fix_color(None, fallback='#B45309') == '#B45309'

    def test_default_color_for_account_type(self):
        """Test default color assignment by account type."""
        assert get_default_color_for_account_type(AccountType.ASSET) == AccountColors.ASSET
        assert get_default_color_for_account_type(AccountType.LIABILITY) == AccountColors.LIABILITY
        assert get_default_color_for_account_type(AccountType.EQUITY) == AccountColors.EQUITY
        assert get_default_color_for_account_type(AccountType.INCOME) == AccountColors.INCOME
        assert get_default_color_for_account_type(AccountType.EXPENSE) == AccountColors.EXPENSE


class TestAccountServiceColorMethods:
    """Test AccountService US-009 methods."""

    @pytest.fixture
    def mock_service(self):
        """Create AccountService with mocked dependencies."""
        mock_db = MagicMock()
        service = AccountService(mock_db)
        service.account_repo = MagicMock()
        return service

    def test_update_color_valid(self, mock_service):
        """Test update_color with valid WCAG AA color."""
        mock_account = Account(
            id=1,
            name="Test Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('100.00'),
            normal_balance=NormalBalance.DEBIT,
            color_hex='#2563EB'
        )
        mock_service.account_repo.update_color.return_value = mock_account

        result = mock_service.update_color(1, '#2563EB')

        assert result.color_hex == '#2563EB'
        mock_service.account_repo.update_color.assert_called_once_with(1, '#2563EB')

    def test_update_color_invalid_format(self, mock_service):
        """Test update_color rejects invalid color format."""
        with pytest.raises(ValidationError, match="Invalid color format"):
            mock_service.update_color(1, 'invalid')

        with pytest.raises(ValidationError, match="Invalid color format"):
            mock_service.update_color(1, '2563EB')  # Missing #

    def test_update_color_wcag_warning(self, mock_service, caplog):
        """Test update_color warns for non-compliant colors but allows them."""
        mock_account = Account(
            id=1,
            name="Test Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('100.00'),
            normal_balance=NormalBalance.DEBIT,
            color_hex='#FFFF00'
        )
        mock_service.account_repo.update_color.return_value = mock_account

        # Should succeed but log warning
        result = mock_service.update_color(1, '#FFFF00', validate_wcag=True)

        assert result.color_hex == '#FFFF00'
        assert "does not meet WCAG AA" in caplog.text

    def test_toggle_favorite(self, mock_service):
        """Test toggle_favorite changes favorite status."""
        mock_account = Account(
            id=1,
            name="Test Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('100.00'),
            normal_balance=NormalBalance.DEBIT,
            is_favorite=True  # After toggle
        )
        mock_service.account_repo.toggle_favorite.return_value = mock_account

        result = mock_service.toggle_favorite(1)

        assert result.is_favorite is True
        mock_service.account_repo.toggle_favorite.assert_called_once_with(1)

    def test_reorder_accounts_valid(self, mock_service):
        """Test reorder_accounts with valid display orders."""
        mock_accounts = [
            Account(
                id=1, name="Account 1", account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING, balance=Decimal('100.00'),
                normal_balance=NormalBalance.DEBIT, display_order=10
            ),
            Account(
                id=2, name="Account 2", account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.SAVINGS, balance=Decimal('200.00'),
                normal_balance=NormalBalance.DEBIT, display_order=20
            )
        ]

        mock_service.account_repo.update_display_order.side_effect = mock_accounts

        result = mock_service.reorder_accounts([(1, 10), (2, 20)])

        assert len(result) == 2
        assert result[0].display_order == 10
        assert result[1].display_order == 20

    def test_reorder_accounts_negative_order(self, mock_service):
        """Test reorder_accounts rejects negative display_order."""
        with pytest.raises(ValidationError, match="Display order must be non-negative"):
            mock_service.reorder_accounts([(1, -5)])

    def test_create_account_default_color(self, mock_service):
        """Test create_account assigns default color based on account type."""
        # Mock the account_repo.create to return account with default color
        def mock_create(account):
            account.id = 1
            return account

        mock_service.account_repo.create.side_effect = mock_create
        mock_service.account_repo.get_by_id.return_value = Account(
            id=1,
            name="Test Account",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            balance=Decimal('0.00'),
            normal_balance=NormalBalance.CREDIT,
            color_hex=AccountColors.LIABILITY  # Default liability color
        )

        result = mock_service.create_account(
            name="Test Account",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD
        )

        # Should use default LIABILITY color (#DC2626 Red-600)
        assert result.color_hex == AccountColors.LIABILITY

    def test_create_account_custom_color(self, mock_service):
        """Test create_account accepts custom color and validates it."""
        def mock_create(account):
            account.id=1
            return account

        mock_service.account_repo.create.side_effect = mock_create
        mock_service.account_repo.get_by_id.return_value = Account(
            id=1,
            name="Test Account",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubtype.EXPENSE_CATEGORY,
            balance=Decimal('0.00'),
            normal_balance=NormalBalance.DEBIT,
            color_hex='#10B981'  # Custom emerald green
        )

        result = mock_service.create_account(
            name="Test Account",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubtype.EXPENSE_CATEGORY,
            color_hex='#10B981'
        )

        # Should use custom color
        assert result.color_hex == '#10B981'


# Run tests with: pytest finance_app/tests/unit/test_us009_color_system.py -v
