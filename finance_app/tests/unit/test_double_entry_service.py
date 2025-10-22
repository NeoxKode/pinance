"""
Unit tests for DoubleEntryService.

Story: US-002A - Journal Entry Foundation
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from finance_app.data.models import (
    JournalEntry, EntryType, Account, AccountType, AccountSubtype, NormalBalance
)
from finance_app.business.double_entry_service import DoubleEntryService
from finance_app.data.database import Database
from finance_app.utils.exceptions import ValidationError, NotFoundError


class TestDoubleEntryServiceDebitCreditLogic:
    """Test debit/credit calculation logic."""

    @pytest.fixture
    def service(self):
        """Create service with mock database."""
        return DoubleEntryService(Mock(spec=Database))

    def test_asset_account_positive_amount_is_debit(self, service):
        """Test positive amount to asset account creates debit."""
        debit, credit = service._calculate_debit_credit(
            Decimal("100.00"),
            NormalBalance.DEBIT
        )

        assert debit == Decimal("100.00")
        assert credit == Decimal("0")

    def test_asset_account_negative_amount_is_credit(self, service):
        """Test negative amount to asset account creates credit."""
        debit, credit = service._calculate_debit_credit(
            Decimal("-50.00"),
            NormalBalance.DEBIT
        )

        assert debit == Decimal("0")
        assert credit == Decimal("50.00")

    def test_liability_account_positive_amount_is_credit(self, service):
        """Test positive amount to liability account creates credit."""
        debit, credit = service._calculate_debit_credit(
            Decimal("200.00"),
            NormalBalance.CREDIT
        )

        assert debit == Decimal("0")
        assert credit == Decimal("200.00")

    def test_liability_account_negative_amount_is_debit(self, service):
        """Test negative amount to liability account creates debit."""
        debit, credit = service._calculate_debit_credit(
            Decimal("-75.00"),
            NormalBalance.CREDIT
        )

        assert debit == Decimal("75.00")
        assert credit == Decimal("0")


class TestDoubleEntryServiceCreateSimpleTransaction:
    """Test create_simple_transaction() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service."""
        with patch('finance_app.business.double_entry_service.JournalEntryRepository'), \
             patch('finance_app.business.double_entry_service.AccountRepository'):
            return DoubleEntryService(mock_db)

    def test_create_transaction_for_asset_account_deposit(self, service):
        """Test creating transaction for asset account (deposit = debit)."""
        # Mock account
        mock_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        service.account_repo.get_by_id = Mock(return_value=mock_account)

        # Mock journal entry creation
        mock_entry = JournalEntry(
            id=123,
            account_id=1,
            entry_date="2025-10-22",
            description="Deposit",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )
        service.journal_repo.create = Mock(return_value=mock_entry)

        # Create transaction
        result = service.create_simple_transaction(
            account_id=1,
            amount=Decimal("100.00"),  # Positive = debit for asset
            date="2025-10-22",
            description="Deposit"
        )

        # Verify journal repo was called with debit entry
        call_args = service.journal_repo.create.call_args[0][0]
        assert call_args.debit_amount == Decimal("100.00")
        assert call_args.credit_amount == Decimal("0")
        assert result.id == 123

    def test_create_transaction_for_asset_account_withdrawal(self, service):
        """Test creating transaction for asset account (withdrawal = credit)."""
        mock_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        service.account_repo.get_by_id = Mock(return_value=mock_account)

        mock_entry = JournalEntry(
            id=124,
            account_id=1,
            entry_date="2025-10-22",
            description="Withdrawal",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("50.00"),
            balance_after=Decimal("950.00"),
            entry_type=EntryType.TRANSACTION
        )
        service.journal_repo.create = Mock(return_value=mock_entry)

        result = service.create_simple_transaction(
            account_id=1,
            amount=Decimal("-50.00"),  # Negative = credit for asset
            date="2025-10-22",
            description="Withdrawal"
        )

        # Verify journal repo was called with credit entry
        call_args = service.journal_repo.create.call_args[0][0]
        assert call_args.debit_amount == Decimal("0")
        assert call_args.credit_amount == Decimal("50.00")

    def test_create_transaction_for_liability_account_increase(self, service):
        """Test creating transaction for liability account (increase = credit)."""
        mock_account = Account(
            id=2,
            name="Credit Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            balance=Decimal("500.00"),
            normal_balance=NormalBalance.CREDIT
        )
        service.account_repo.get_by_id = Mock(return_value=mock_account)

        mock_entry = JournalEntry(
            id=125,
            account_id=2,
            entry_date="2025-10-22",
            description="Credit card charge",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("75.00"),
            balance_after=Decimal("575.00"),
            entry_type=EntryType.TRANSACTION
        )
        service.journal_repo.create = Mock(return_value=mock_entry)

        result = service.create_simple_transaction(
            account_id=2,
            amount=Decimal("75.00"),  # Positive = credit for liability
            date="2025-10-22",
            description="Credit card charge"
        )

        # Verify journal repo was called with credit entry
        call_args = service.journal_repo.create.call_args[0][0]
        assert call_args.debit_amount == Decimal("0")
        assert call_args.credit_amount == Decimal("75.00")

    def test_create_transaction_for_liability_account_payment(self, service):
        """Test creating transaction for liability account (payment = debit)."""
        mock_account = Account(
            id=2,
            name="Credit Card",
            account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD,
            balance=Decimal("500.00"),
            normal_balance=NormalBalance.CREDIT
        )
        service.account_repo.get_by_id = Mock(return_value=mock_account)

        mock_entry = JournalEntry(
            id=126,
            account_id=2,
            entry_date="2025-10-22",
            description="Payment",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("400.00"),
            entry_type=EntryType.TRANSACTION
        )
        service.journal_repo.create = Mock(return_value=mock_entry)

        result = service.create_simple_transaction(
            account_id=2,
            amount=Decimal("-100.00"),  # Negative = debit for liability
            date="2025-10-22",
            description="Payment"
        )

        # Verify journal repo was called with debit entry
        call_args = service.journal_repo.create.call_args[0][0]
        assert call_args.debit_amount == Decimal("100.00")
        assert call_args.credit_amount == Decimal("0")

    def test_create_transaction_raises_error_for_zero_amount(self, service):
        """Test that zero amount raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be zero"):
            service.create_simple_transaction(
                account_id=1,
                amount=Decimal("0"),
                date="2025-10-22",
                description="Invalid"
            )

    def test_create_transaction_raises_error_for_invalid_account(self, service):
        """Test that invalid account ID raises NotFoundError."""
        service.account_repo.get_by_id = Mock(return_value=None)

        with pytest.raises(NotFoundError, match="Account 999 not found"):
            service.create_simple_transaction(
                account_id=999,
                amount=Decimal("100.00"),
                date="2025-10-22",
                description="Test"
            )


class TestDoubleEntryServiceValidateAccountBalance:
    """Test validate_account_balance() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service."""
        with patch('finance_app.business.double_entry_service.JournalEntryRepository'), \
             patch('finance_app.business.double_entry_service.AccountRepository'):
            return DoubleEntryService(mock_db)

    def test_validate_balance_passes_when_balances_match(self, service):
        """Test validation passes when balances match."""
        mock_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        service.account_repo.get_by_id = Mock(return_value=mock_account)
        service.journal_repo.get_account_balance = Mock(return_value=Decimal("1000.00"))

        result = service.validate_account_balance(account_id=1)

        assert result is True

    def test_validate_balance_passes_within_tolerance(self, service):
        """Test validation passes when difference is within tolerance."""
        mock_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        service.account_repo.get_by_id = Mock(return_value=mock_account)
        # 0.005 difference (< 0.01 tolerance)
        service.journal_repo.get_account_balance = Mock(return_value=Decimal("1000.005"))

        result = service.validate_account_balance(account_id=1)

        assert result is True

    def test_validate_balance_fails_outside_tolerance(self, service):
        """Test validation fails when difference exceeds tolerance."""
        mock_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        service.account_repo.get_by_id = Mock(return_value=mock_account)
        # 5.00 difference (> 0.01 tolerance)
        service.journal_repo.get_account_balance = Mock(return_value=Decimal("1005.00"))

        with pytest.raises(ValidationError, match="Balance mismatch"):
            service.validate_account_balance(account_id=1)

    def test_validate_balance_raises_error_for_invalid_account(self, service):
        """Test that invalid account raises NotFoundError."""
        service.account_repo.get_by_id = Mock(return_value=None)

        with pytest.raises(NotFoundError, match="Account 999 not found"):
            service.validate_account_balance(account_id=999)


class TestDoubleEntryServiceGetAccountBalance:
    """Test get_account_balance() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service."""
        with patch('finance_app.business.double_entry_service.JournalEntryRepository'), \
             patch('finance_app.business.double_entry_service.AccountRepository'):
            return DoubleEntryService(mock_db)

    def test_get_balance_returns_journal_balance(self, service):
        """Test get_account_balance returns balance from journal."""
        mock_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        service.account_repo.get_by_id = Mock(return_value=mock_account)
        service.journal_repo.get_account_balance = Mock(return_value=Decimal("1234.56"))

        balance = service.get_account_balance(account_id=1)

        assert balance == Decimal("1234.56")
        service.journal_repo.get_account_balance.assert_called_once_with(1, None)

    def test_get_balance_with_date(self, service):
        """Test get_account_balance with as_of_date parameter."""
        mock_account = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        service.account_repo.get_by_id = Mock(return_value=mock_account)
        service.journal_repo.get_account_balance = Mock(return_value=Decimal("900.00"))

        balance = service.get_account_balance(account_id=1, as_of_date="2025-10-15")

        assert balance == Decimal("900.00")
        service.journal_repo.get_account_balance.assert_called_once_with(1, "2025-10-15")

    def test_get_balance_raises_error_for_invalid_account(self, service):
        """Test that invalid account raises NotFoundError."""
        service.account_repo.get_by_id = Mock(return_value=None)

        with pytest.raises(NotFoundError, match="Account 999 not found"):
            service.get_account_balance(account_id=999)
