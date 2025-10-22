"""
Unit tests for JournalEntry model.

Story: US-002A - Journal Entry Foundation
"""
import pytest
from decimal import Decimal
from datetime import datetime

from finance_app.data.models import JournalEntry, EntryType


class TestJournalEntryValidation:
    """Test JournalEntry validation logic."""

    def test_creates_valid_debit_entry(self):
        """Test creating valid debit entry."""
        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Test debit",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )

        assert entry.debit_amount == Decimal("100.00")
        assert entry.credit_amount == Decimal("0")
        assert entry.is_debit is True
        assert entry.is_credit is False
        assert entry.amount == Decimal("100.00")

    def test_creates_valid_credit_entry(self):
        """Test creating valid credit entry."""
        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Test credit",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("50.00"),
            balance_after=Decimal("950.00"),
            entry_type=EntryType.TRANSACTION
        )

        assert entry.debit_amount == Decimal("0")
        assert entry.credit_amount == Decimal("50.00")
        assert entry.is_debit is False
        assert entry.is_credit is True
        assert entry.amount == Decimal("-50.00")

    def test_rejects_both_debit_and_credit(self):
        """Test validation rejects entry with both debit and credit."""
        with pytest.raises(ValueError, match="cannot have both debit and credit"):
            JournalEntry(
                id=None,
                account_id=1,
                entry_date="2025-10-22",
                description="Invalid",
                debit_amount=Decimal("100.00"),
                credit_amount=Decimal("50.00"),  # ❌ INVALID
                balance_after=Decimal("1050.00"),
                entry_type=EntryType.TRANSACTION
            )

    def test_rejects_zero_amounts(self):
        """Test validation rejects entry with both amounts zero."""
        with pytest.raises(ValueError, match="must have either debit or credit"):
            JournalEntry(
                id=None,
                account_id=1,
                entry_date="2025-10-22",
                description="Invalid",
                debit_amount=Decimal("0"),
                credit_amount=Decimal("0"),  # ❌ INVALID
                balance_after=Decimal("1000.00"),
                entry_type=EntryType.TRANSACTION
            )

    def test_rejects_negative_debit(self):
        """Test validation rejects negative debit amount."""
        with pytest.raises(ValueError, match="must be non-negative"):
            JournalEntry(
                id=None,
                account_id=1,
                entry_date="2025-10-22",
                description="Invalid",
                debit_amount=Decimal("-100.00"),  # ❌ INVALID
                credit_amount=Decimal("0"),
                balance_after=Decimal("900.00"),
                entry_type=EntryType.TRANSACTION
            )

    def test_rejects_negative_credit(self):
        """Test validation rejects negative credit amount."""
        with pytest.raises(ValueError, match="must be non-negative"):
            JournalEntry(
                id=None,
                account_id=1,
                entry_date="2025-10-22",
                description="Invalid",
                debit_amount=Decimal("0"),
                credit_amount=Decimal("-50.00"),  # ❌ INVALID
                balance_after=Decimal("950.00"),
                entry_type=EntryType.TRANSACTION
            )


class TestJournalEntryTypeConversions:
    """Test type conversions in __post_init__."""

    def test_converts_float_to_decimal(self):
        """Test that float amounts are converted to Decimal."""
        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=100.50,  # Float
            credit_amount=0,
            balance_after=1100.50,
            entry_type=EntryType.TRANSACTION
        )

        assert isinstance(entry.debit_amount, Decimal)
        assert isinstance(entry.credit_amount, Decimal)
        assert isinstance(entry.balance_after, Decimal)
        assert entry.debit_amount == Decimal("100.50")

    def test_converts_string_to_entry_type_enum(self):
        """Test that string entry_type is converted to enum."""
        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type='transaction'  # String instead of enum
        )

        assert isinstance(entry.entry_type, EntryType)
        assert entry.entry_type == EntryType.TRANSACTION


class TestJournalEntryHelperProperties:
    """Test helper properties on JournalEntry."""

    def test_amount_property_for_debit(self):
        """Test amount property returns positive for debit."""
        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )

        assert entry.amount == Decimal("100.00")

    def test_amount_property_for_credit(self):
        """Test amount property returns negative for credit."""
        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("50.00"),
            balance_after=Decimal("950.00"),
            entry_type=EntryType.TRANSACTION
        )

        assert entry.amount == Decimal("-50.00")

    def test_is_debit_property(self):
        """Test is_debit property."""
        debit_entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Debit",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )

        credit_entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Credit",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("50.00"),
            balance_after=Decimal("950.00"),
            entry_type=EntryType.TRANSACTION
        )

        assert debit_entry.is_debit is True
        assert credit_entry.is_debit is False

    def test_is_credit_property(self):
        """Test is_credit property."""
        debit_entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Debit",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
        )

        credit_entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Credit",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("50.00"),
            balance_after=Decimal("950.00"),
            entry_type=EntryType.TRANSACTION
        )

        assert debit_entry.is_credit is False
        assert credit_entry.is_credit is True


class TestEntryType:
    """Test EntryType enum."""

    def test_entry_type_values(self):
        """Test all EntryType enum values."""
        assert EntryType.TRANSACTION.value == 'transaction'
        assert EntryType.OPENING_BALANCE.value == 'opening_balance'
        assert EntryType.ADJUSTMENT.value == 'adjustment'
        assert EntryType.TRANSFER.value == 'transfer'

    def test_entry_type_from_string(self):
        """Test creating EntryType from string."""
        assert EntryType('transaction') == EntryType.TRANSACTION
        assert EntryType('opening_balance') == EntryType.OPENING_BALANCE
        assert EntryType('adjustment') == EntryType.ADJUSTMENT
        assert EntryType('transfer') == EntryType.TRANSFER


class TestJournalEntryEdgeCases:
    """Test edge cases for JournalEntry."""

    def test_handles_optional_fields(self):
        """Test that optional fields can be None."""
        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Test",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION
            # All optional fields omitted
        )

        assert entry.id is None
        assert entry.transaction_id is None
        assert entry.group_id is None
        assert entry.reference_number is None
        assert entry.is_reconciled is False
        assert entry.reconciliation_id is None
        assert entry.notes is None
        assert entry.created_at is None
        assert entry.updated_at is None

    def test_handles_large_amounts(self):
        """Test handling of large decimal amounts."""
        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Large amount",
            debit_amount=Decimal("9999999.99"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("10000999.99"),
            entry_type=EntryType.TRANSACTION
        )

        assert entry.debit_amount == Decimal("9999999.99")
        assert entry.amount == Decimal("9999999.99")

    def test_handles_precise_decimal_amounts(self):
        """Test handling of precise decimal amounts (more than 2 places)."""
        entry = JournalEntry(
            id=None,
            account_id=1,
            entry_date="2025-10-22",
            description="Precise amount",
            debit_amount=Decimal("100.12345"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.12345"),
            entry_type=EntryType.TRANSACTION
        )

        assert entry.debit_amount == Decimal("100.12345")

    def test_with_all_optional_fields_populated(self):
        """Test entry with all optional fields populated."""
        entry = JournalEntry(
            id=123,
            transaction_id=456,
            group_id=789,
            account_id=1,
            entry_date="2025-10-22",
            description="Full entry",
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
            balance_after=Decimal("1100.00"),
            entry_type=EntryType.TRANSACTION,
            reference_number="CHK-001",
            is_reconciled=True,
            reconciliation_id=999,
            notes="Test notes",
            created_at=datetime(2025, 10, 22, 10, 30),
            updated_at=datetime(2025, 10, 22, 11, 45)
        )

        assert entry.id == 123
        assert entry.transaction_id == 456
        assert entry.group_id == 789
        assert entry.reference_number == "CHK-001"
        assert entry.is_reconciled is True
        assert entry.reconciliation_id == 999
        assert entry.notes == "Test notes"
        assert entry.created_at == datetime(2025, 10, 22, 10, 30)
        assert entry.updated_at == datetime(2025, 10, 22, 11, 45)
