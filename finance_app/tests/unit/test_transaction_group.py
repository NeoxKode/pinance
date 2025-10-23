"""
Unit tests for TransactionGroup model and create_balanced_group.

Story: US-002B - Balanced Transaction Groups (Phase 2)
"""
import pytest
from decimal import Decimal
from datetime import datetime

from finance_app.data.models import TransactionGroup, JournalEntry, EntryType


class TestTransactionGroupModel:
    """Test TransactionGroup model validation."""

    def test_create_valid_balanced_group(self):
        """Valid balanced group should be created successfully."""
        group = TransactionGroup(
            id=None,
            group_date="2025-10-22",
            description="Test transfer",
            total_debits=Decimal("500.00"),
            total_credits=Decimal("500.00"),
            notes="Test notes"
        )

        assert group.is_balanced is True
        assert group.total_amount == Decimal("500.00")
        assert group.entry_count == 2

    def test_unbalanced_group_raises_error(self):
        """Unbalanced group (debits != credits) should raise ValueError."""
        with pytest.raises(ValueError, match="must be balanced"):
            TransactionGroup(
                id=None,
                group_date="2025-10-22",
                description="Unbalanced",
                total_debits=Decimal("500.00"),
                total_credits=Decimal("400.00")  # Not balanced!
            )

    def test_negative_debits_raises_error(self):
        """Negative total_debits should raise ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            TransactionGroup(
                id=None,
                group_date="2025-10-22",
                description="Negative debits",
                total_debits=Decimal("-500.00"),
                total_credits=Decimal("-500.00")
            )

    def test_negative_credits_raises_error(self):
        """Negative total_credits should raise ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            TransactionGroup(
                id=None,
                group_date="2025-10-22",
                description="Negative credits",
                total_debits=Decimal("500.00"),
                total_credits=Decimal("-500.00")
            )

    def test_automatic_decimal_conversion(self):
        """String and float amounts should be converted to Decimal."""
        group = TransactionGroup(
            id=None,
            group_date="2025-10-22",
            description="Test",
            total_debits="100.50",  # String
            total_credits=100.50    # Float
        )

        assert isinstance(group.total_debits, Decimal)
        assert isinstance(group.total_credits, Decimal)
        assert group.total_debits == Decimal("100.50")
        assert group.total_credits == Decimal("100.50")

    def test_zero_amount_balanced_group(self):
        """Zero-amount balanced group should be valid."""
        group = TransactionGroup(
            id=None,
            group_date="2025-10-22",
            description="Zero amount",
            total_debits=Decimal("0.00"),
            total_credits=Decimal("0.00")
        )

        assert group.is_balanced is True
        assert group.total_amount == Decimal("0.00")

    def test_validate_balance_method(self):
        """validate_balance() should return True for balanced group."""
        group = TransactionGroup(
            id=None,
            group_date="2025-10-22",
            description="Test",
            total_debits=Decimal("1000.00"),
            total_credits=Decimal("1000.00")
        )

        assert group.validate_balance() is True

    def test_large_amounts(self):
        """Large amounts should be handled correctly."""
        large_amount = Decimal("999999999.99")
        group = TransactionGroup(
            id=None,
            group_date="2025-10-22",
            description="Large transfer",
            total_debits=large_amount,
            total_credits=large_amount
        )

        assert group.is_balanced is True
        assert group.total_amount == large_amount

    def test_precision_maintained(self):
        """Decimal precision should be maintained."""
        amount = Decimal("123.456789")
        group = TransactionGroup(
            id=None,
            group_date="2025-10-22",
            description="Precision test",
            total_debits=amount,
            total_credits=amount
        )

        assert group.total_debits == amount
        assert group.total_credits == amount

    def test_with_timestamps(self):
        """Group with timestamps should be created correctly."""
        now = datetime.now()
        group = TransactionGroup(
            id=1,
            group_date="2025-10-22",
            description="With timestamps",
            total_debits=Decimal("100.00"),
            total_credits=Decimal("100.00"),
            created_at=now,
            updated_at=now
        )

        assert group.created_at == now
        assert group.updated_at == now


class TestJournalEntryValidation:
    """Test journal entry validation for balanced groups."""

    def test_valid_journal_entry(self):
        """Valid journal entry should be created."""
        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Test entry",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0.00"),
            balance_after=Decimal("100.00"),
            entry_type=EntryType.TRANSFER
        )

        assert entry.is_debit is True
        assert entry.is_credit is False
        assert entry.amount == Decimal("100.00")

    def test_journal_entry_both_debit_and_credit_raises_error(self):
        """Entry with both debit and credit should raise ValueError."""
        with pytest.raises(ValueError, match="cannot have both"):
            JournalEntry(
                id=None,
                account_id=1,
                entry_date="2025-10-22",
                description="Invalid",
                debit_amount=Decimal("100.00"),  # Both set!
                credit_amount=Decimal("100.00"),  # Both set!
                balance_after=Decimal("0.00"),
                entry_type=EntryType.TRANSFER
            )

    def test_journal_entry_no_amount_raises_error(self):
        """Entry with no debit or credit should raise ValueError."""
        with pytest.raises(ValueError, match="must have either"):
            JournalEntry(
                id=None,
                account_id=1,
                entry_date="2025-10-22",
                description="Invalid",
                debit_amount=Decimal("0.00"),  # Both zero!
                credit_amount=Decimal("0.00"),  # Both zero!
                balance_after=Decimal("0.00"),
                entry_type=EntryType.TRANSFER
            )

    def test_journal_entry_negative_amount_raises_error(self):
        """Entry with negative amount should raise ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            JournalEntry(
                id=None,
                account_id=1,
                entry_date="2025-10-22",
                description="Invalid",
                debit_amount=Decimal("-100.00"),  # Negative!
                credit_amount=Decimal("0.00"),
                balance_after=Decimal("0.00"),
                entry_type=EntryType.TRANSFER
            )

    def test_journal_entry_credit_amount(self):
        """Credit entry should have negative amount."""
        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Credit entry",
            debit_amount=Decimal("0.00"),
            credit_amount=Decimal("100.00"),
            balance_after=Decimal("0.00"),
            entry_type=EntryType.TRANSFER
        )

        assert entry.is_credit is True
        assert entry.is_debit is False
        assert entry.amount == Decimal("-100.00")

    def test_journal_entry_with_group_id(self):
        """Entry with group_id should be created."""
        entry = JournalEntry(
            id=1,
            account_id=1,
            entry_date="2025-10-22",
            description="Grouped entry",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0.00"),
            balance_after=Decimal("100.00"),
            entry_type=EntryType.TRANSFER,
            group_id=5  # Part of a group
        )

        assert entry.group_id == 5
