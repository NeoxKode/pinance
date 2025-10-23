"""
Unit tests for transfer service.

Story: US-002B - Balanced Transaction Groups (Phase 3)
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock

from finance_app.business.double_entry_service import DoubleEntryService
from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance,
    JournalEntry, EntryType, TransactionGroup
)
from finance_app.utils.exceptions import ValidationError, NotFoundError


class TestTransferService:
    """Test transfer creation and validation."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock()

    @pytest.fixture
    def mock_accounts(self):
        """Create mock accounts."""
        checking = Account(
            id=1,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        )
        savings = Account(
            id=2,
            name="Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            balance=Decimal("500.00"),
            normal_balance=NormalBalance.DEBIT
        )
        return {"checking": checking, "savings": savings}

    @pytest.fixture
    def service(self, mock_db, mock_accounts):
        """Create service with mocked dependencies."""
        service = DoubleEntryService(mock_db)

        # Mock account repository
        service.account_repo = Mock()
        service.account_repo.get_by_id = Mock(side_effect=lambda id: {
            1: mock_accounts["checking"],
            2: mock_accounts["savings"]
        }.get(id))

        # Mock journal repository
        service.journal_repo = Mock()

        return service

    def test_valid_transfer_creates_balanced_group(self, service, mock_accounts):
        """Valid transfer should create balanced group with 2 entries."""
        # Setup mock
        mock_group = TransactionGroup(
            id=1,
            group_date="2025-10-22",
            description="Transfer: Checking → Savings",
            total_debits=Decimal("500.00"),
            total_credits=Decimal("500.00")
        )
        mock_entries = [Mock(), Mock()]
        service.journal_repo.create_balanced_group = Mock(
            return_value=(mock_group, mock_entries)
        )

        # Execute
        group, entries = service.create_transfer(
            from_account_id=1,
            to_account_id=2,
            amount=Decimal("500.00"),
            date="2025-10-22",
            description="Monthly savings"
        )

        # Verify
        assert group.id == 1
        assert len(entries) == 2
        service.journal_repo.create_balanced_group.assert_called_once()

        # Verify entries structure
        call_args = service.journal_repo.create_balanced_group.call_args
        entries_arg = call_args[1]['entries']
        assert len(entries_arg) == 2

        # First entry: credit from_account (decrease)
        assert entries_arg[0].account_id == 1
        assert entries_arg[0].credit_amount == Decimal("500.00")
        assert entries_arg[0].debit_amount == Decimal("0.00")
        assert entries_arg[0].entry_type == EntryType.TRANSFER

        # Second entry: debit to_account (increase)
        assert entries_arg[1].account_id == 2
        assert entries_arg[1].debit_amount == Decimal("500.00")
        assert entries_arg[1].credit_amount == Decimal("0.00")
        assert entries_arg[1].entry_type == EntryType.TRANSFER

    def test_negative_amount_raises_validation_error(self, service):
        """Transfer with negative amount should raise ValidationError."""
        with pytest.raises(ValidationError, match="must be positive"):
            service.create_transfer(
                from_account_id=1,
                to_account_id=2,
                amount=Decimal("-500.00"),
                date="2025-10-22",
                description="Invalid transfer"
            )

    def test_zero_amount_raises_validation_error(self, service):
        """Transfer with zero amount should raise ValidationError."""
        with pytest.raises(ValidationError, match="must be positive"):
            service.create_transfer(
                from_account_id=1,
                to_account_id=2,
                amount=Decimal("0.00"),
                date="2025-10-22",
                description="Invalid transfer"
            )

    def test_same_account_raises_validation_error(self, service):
        """Transfer to same account should raise ValidationError."""
        with pytest.raises(ValidationError, match="same account"):
            service.create_transfer(
                from_account_id=1,
                to_account_id=1,  # Same as from_account!
                amount=Decimal("500.00"),
                date="2025-10-22",
                description="Invalid transfer"
            )

    def test_nonexistent_source_account_raises_not_found(self, service):
        """Transfer from nonexistent account should raise NotFoundError."""
        service.account_repo.get_by_id = Mock(return_value=None)

        with pytest.raises(NotFoundError, match="Source account 999 not found"):
            service.create_transfer(
                from_account_id=999,
                to_account_id=2,
                amount=Decimal("500.00"),
                date="2025-10-22",
                description="Invalid transfer"
            )

    def test_nonexistent_destination_account_raises_not_found(self, service, mock_accounts):
        """Transfer to nonexistent account should raise NotFoundError."""
        def get_by_id_side_effect(id):
            if id == 1:
                return mock_accounts["checking"]
            return None

        service.account_repo.get_by_id = Mock(side_effect=get_by_id_side_effect)

        with pytest.raises(NotFoundError, match="Destination account 999 not found"):
            service.create_transfer(
                from_account_id=1,
                to_account_id=999,
                amount=Decimal("500.00"),
                date="2025-10-22",
                description="Invalid transfer"
            )

    def test_transfer_with_reference_number(self, service):
        """Transfer with reference number should pass it to entries."""
        mock_group = TransactionGroup(
            id=1,
            group_date="2025-10-22",
            description="Transfer",
            total_debits=Decimal("100.00"),
            total_credits=Decimal("100.00")
        )
        service.journal_repo.create_balanced_group = Mock(
            return_value=(mock_group, [Mock(), Mock()])
        )

        service.create_transfer(
            from_account_id=1,
            to_account_id=2,
            amount=Decimal("100.00"),
            date="2025-10-22",
            description="Test transfer",
            reference_number="TXN-12345"
        )

        # Verify reference number passed to entries
        call_args = service.journal_repo.create_balanced_group.call_args
        entries_arg = call_args[1]['entries']
        assert all(e.reference_number == "TXN-12345" for e in entries_arg)

    def test_transfer_with_notes(self, service):
        """Transfer with notes should pass them to group and entries."""
        mock_group = TransactionGroup(
            id=1,
            group_date="2025-10-22",
            description="Transfer",
            total_debits=Decimal("100.00"),
            total_credits=Decimal("100.00")
        )
        service.journal_repo.create_balanced_group = Mock(
            return_value=(mock_group, [Mock(), Mock()])
        )

        service.create_transfer(
            from_account_id=1,
            to_account_id=2,
            amount=Decimal("100.00"),
            date="2025-10-22",
            description="Test transfer",
            notes="Test notes"
        )

        # Verify notes passed
        call_args = service.journal_repo.create_balanced_group.call_args
        assert call_args[1]['notes'] == "Test notes"

        entries_arg = call_args[1]['entries']
        assert all(e.notes == "Test notes" for e in entries_arg)

    def test_large_transfer_amount(self, service):
        """Transfer with large amount should work correctly."""
        large_amount = Decimal("999999999.99")
        mock_group = TransactionGroup(
            id=1,
            group_date="2025-10-22",
            description="Transfer",
            total_debits=large_amount,
            total_credits=large_amount
        )
        service.journal_repo.create_balanced_group = Mock(
            return_value=(mock_group, [Mock(), Mock()])
        )

        group, _ = service.create_transfer(
            from_account_id=1,
            to_account_id=2,
            amount=large_amount,
            date="2025-10-22",
            description="Large transfer"
        )

        assert group.total_debits == large_amount
        assert group.total_credits == large_amount

    def test_transfer_maintains_decimal_precision(self, service):
        """Transfer should maintain Decimal precision."""
        precise_amount = Decimal("123.456789")
        mock_group = TransactionGroup(
            id=1,
            group_date="2025-10-22",
            description="Transfer",
            total_debits=precise_amount,
            total_credits=precise_amount
        )
        service.journal_repo.create_balanced_group = Mock(
            return_value=(mock_group, [Mock(), Mock()])
        )

        service.create_transfer(
            from_account_id=1,
            to_account_id=2,
            amount=precise_amount,
            date="2025-10-22",
            description="Precision test"
        )

        # Verify precise amounts
        call_args = service.journal_repo.create_balanced_group.call_args
        entries_arg = call_args[1]['entries']
        assert entries_arg[0].credit_amount == precise_amount
        assert entries_arg[1].debit_amount == precise_amount
