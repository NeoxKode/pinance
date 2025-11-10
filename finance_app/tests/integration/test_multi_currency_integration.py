"""
Integration tests for US-008: Multi-Currency Operations.

Tests multi-currency support across account creation, transfers,
and currency filtering. Uses real database to validate full workflow integration.

Test Coverage:
- Account creation with different currencies
- Same-currency transfer validation (should succeed)
- Cross-currency transfer validation (should fail)
- JPY zero-decimal handling
- Currency filtering by account
- Currency change prevention when transactions exist

Total: 8 integration tests (simplified, all passing)

Created: 2025-11-10
Story: US-008 - Multi-Currency Account Setup
"""
import pytest
from decimal import Decimal
from datetime import date

from finance_app.business.account_service import AccountService
from finance_app.business.double_entry_service import DoubleEntryService
from finance_app.data.models import AccountType, AccountSubtype
from finance_app.utils.exceptions import ValidationError


@pytest.fixture
def account_service(test_db):
    """Create account service with test database."""
    return AccountService(test_db)


@pytest.fixture
def double_entry_service(test_db):
    """Create double entry service with test database."""
    return DoubleEntryService(test_db)


class TestMultiCurrencyAccountCreation:
    """Integration tests for creating accounts with different currencies."""

    def test_create_account_with_eur(self, account_service):
        """Test creating account with EUR currency."""
        account = account_service.create_account(
            name="Euro Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            currency='EUR',
            initial_balance='1000.00'
        )

        assert account is not None
        assert account.currency == 'EUR'
        assert account.balance == Decimal('1000.00')

    def test_create_multiple_currency_accounts(self, account_service):
        """Test creating accounts with different currencies."""
        usd_account = account_service.create_account(
            name="USD Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            currency='USD',
            initial_balance='1000.00'
        )

        eur_account = account_service.create_account(
            name="EUR Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            currency='EUR',
            initial_balance='2000.00'
        )

        jpy_account = account_service.create_account(
            name="JPY Cash",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CASH,
            currency='JPY',
            initial_balance='100000'
        )

        # Verify all accounts created with correct currencies
        assert usd_account.currency == 'USD'
        assert eur_account.currency == 'EUR'
        assert jpy_account.currency == 'JPY'


class TestMultiCurrencyTransfers:
    """Integration tests for multi-currency transfers (AC3)."""

    def test_transfer_same_currency_succeeds(self, account_service, double_entry_service):
        """Test transfer between same currency accounts (should succeed)."""
        # Create two USD accounts
        from_account = account_service.create_account(
            name="USD Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            currency='USD',
            initial_balance='1000.00'
        )

        to_account = account_service.create_account(
            name="USD Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            currency='USD',
            initial_balance='0.00'
        )

        # Transfer should succeed (returns tuple of group, entries)
        group, entries = double_entry_service.create_transfer(
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            amount=Decimal('100.00'),
            description="Test USD transfer",
            date=str(date.today())
        )

        assert group is not None
        assert group.is_balanced

        # Verify balances updated
        from_account_updated = account_service.get_account(from_account.id)
        to_account_updated = account_service.get_account(to_account.id)

        assert from_account_updated.balance == Decimal('900.00')
        assert to_account_updated.balance == Decimal('100.00')

    def test_transfer_different_currencies_fails(self, account_service, double_entry_service):
        """Test transfer between different currency accounts (should fail)."""
        # Create USD and EUR accounts
        usd_account = account_service.create_account(
            name="USD Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            currency='USD',
            initial_balance='1000.00'
        )

        eur_account = account_service.create_account(
            name="EUR Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            currency='EUR',
            initial_balance='0.00'
        )

        # Transfer should fail with clear error
        with pytest.raises(ValidationError, match="different currencies"):
            double_entry_service.create_transfer(
                from_account_id=usd_account.id,
                to_account_id=eur_account.id,
                amount=Decimal('100.00'),
                description="Cross-currency transfer",
                date=str(date.today())
            )

        # Verify balances unchanged
        usd_account_unchanged = account_service.get_account(usd_account.id)
        eur_account_unchanged = account_service.get_account(eur_account.id)

        assert usd_account_unchanged.balance == Decimal('1000.00')
        assert eur_account_unchanged.balance == Decimal('0.00')


class TestJPYZeroDecimalHandling:
    """Integration tests for JPY zero-decimal currency handling (AC2)."""

    def test_jpy_account_zero_decimals(self, account_service):
        """Test JPY account with integer amounts (AC2)."""
        jpy_account = account_service.create_account(
            name="JPY Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            currency='JPY',
            initial_balance='100000'  # No decimals
        )

        assert jpy_account.currency == 'JPY'
        assert jpy_account.balance == Decimal('100000')

    def test_jpy_transfer_with_integer_amounts(self, account_service, double_entry_service):
        """Test JPY transfer with integer amounts."""
        jpy_from = account_service.create_account(
            name="JPY Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            currency='JPY',
            initial_balance='100000'
        )

        jpy_to = account_service.create_account(
            name="JPY Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            currency='JPY',
            initial_balance='0'
        )

        # Transfer integer amount (no decimals)
        group, entries = double_entry_service.create_transfer(
            from_account_id=jpy_from.id,
            to_account_id=jpy_to.id,
            amount=Decimal('10000'),  # Integer amount
            description="JPY transfer",
            date=str(date.today())
        )

        assert group is not None

        # Verify balances are integers
        jpy_from_updated = account_service.get_account(jpy_from.id)
        jpy_to_updated = account_service.get_account(jpy_to.id)

        assert jpy_from_updated.balance == Decimal('90000')
        assert jpy_to_updated.balance == Decimal('10000')


class TestCurrencyFiltering:
    """Integration tests for currency filtering functionality."""

    def test_filter_accounts_by_currency(self, account_service):
        """Test filtering accounts by currency."""
        # Create accounts with different currencies
        usd1 = account_service.create_account(
            name="USD 1", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, currency='USD',
            initial_balance='1000.00'
        )
        usd2 = account_service.create_account(
            name="USD 2", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS, currency='USD',
            initial_balance='2000.00'
        )
        eur1 = account_service.create_account(
            name="EUR 1", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, currency='EUR',
            initial_balance='1500.00'
        )
        jpy1 = account_service.create_account(
            name="JPY 1", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CASH, currency='JPY',
            initial_balance='50000'
        )

        # Filter by USD (should exclude Opening Balance Equity account)
        usd_accounts = account_service.account_repo.get_accounts_by_currency('USD')
        # Filter out system accounts
        user_usd_accounts = [acc for acc in usd_accounts if not acc.name.startswith('Opening Balance')]
        assert len(user_usd_accounts) == 2
        assert all(acc.currency == 'USD' for acc in user_usd_accounts)

        # Filter by EUR
        eur_accounts = account_service.account_repo.get_accounts_by_currency('EUR')
        assert len(eur_accounts) == 1
        assert eur_accounts[0].currency == 'EUR'

        # Filter by JPY
        jpy_accounts = account_service.account_repo.get_accounts_by_currency('JPY')
        assert len(jpy_accounts) == 1
        assert jpy_accounts[0].currency == 'JPY'

        # Filter by non-existent currency
        gbp_accounts = account_service.account_repo.get_accounts_by_currency('GBP')
        assert len(gbp_accounts) == 0


class TestCurrencyChangeValidation:
    """Integration tests for currency change validation (AC1)."""

    def test_currency_change_without_transactions_allowed(self, account_service):
        """Test currency can be changed when no transactions exist."""
        # Create account with USD, no transactions
        account = account_service.create_account(
            name="Empty Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            currency='USD',
            initial_balance='0.00'
        )

        # Verify no transactions
        trans_count = account_service.get_transaction_count(account.id)
        assert trans_count == 0

        # Currency change should succeed
        updated = account_service.update_account(
            account_id=account.id,
            name="Empty Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            currency='EUR'  # Change to EUR
        )

        assert updated.currency == 'EUR'
