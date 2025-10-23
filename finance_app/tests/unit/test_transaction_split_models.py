"""
Unit tests for split transaction models.

Story: US-002C - Split Transactions (Day 1)
Tests: TransactionSplit, SplitTransaction, PaycheckSplit

Test Coverage:
- Model validation
- Balance checking
- Edge cases
- Error handling
"""

import pytest
from decimal import Decimal
from datetime import datetime
from finance_app.data.models import (
    Transaction,
    TransactionSplit,
    SplitTransaction,
    PaycheckSplit
)


class TestTransactionSplit:
    """Test TransactionSplit model validation."""

    def test_create_valid_split(self):
        """Should create valid transaction split."""
        split = TransactionSplit(
            id=None,
            transaction_id=1,
            group_id=1,
            split_order=0,
            category_id=1,
            amount=Decimal('50.00'),
            memo="Test split"
        )

        assert split.transaction_id == 1
        assert split.group_id == 1
        assert split.category_id == 1
        assert split.amount == Decimal('50.00')
        assert split.memo == "Test split"
        assert split.split_type == 'manual'  # Default

    def test_amount_converted_to_decimal(self):
        """Should convert amount to Decimal automatically."""
        split = TransactionSplit(
            id=None,
            transaction_id=1,
            group_id=1,
            split_order=0,
            category_id=1,
            amount=50.00  # Float
        )

        assert isinstance(split.amount, Decimal)
        assert split.amount == Decimal('50.00')

    def test_reject_zero_amount(self):
        """Should reject split with zero amount."""
        with pytest.raises(ValueError, match="must be positive"):
            TransactionSplit(
                id=None,
                transaction_id=1,
                group_id=1,
                split_order=0,
                category_id=1,
                amount=Decimal('0')
            )

    def test_reject_negative_amount(self):
        """Should reject split with negative amount."""
        with pytest.raises(ValueError, match="must be positive"):
            TransactionSplit(
                id=None,
                transaction_id=1,
                group_id=1,
                split_order=0,
                category_id=1,
                amount=Decimal('-50.00')
            )

    def test_reject_negative_split_order(self):
        """Should reject negative split order."""
        with pytest.raises(ValueError, match="must be non-negative"):
            TransactionSplit(
                id=None,
                transaction_id=1,
                group_id=1,
                split_order=-1,
                category_id=1,
                amount=Decimal('50.00')
            )

    def test_reject_invalid_split_type(self):
        """Should reject invalid split type."""
        with pytest.raises(ValueError, match="must be one of"):
            TransactionSplit(
                id=None,
                transaction_id=1,
                group_id=1,
                split_order=0,
                category_id=1,
                amount=Decimal('50.00'),
                split_type='invalid'
            )

    def test_valid_split_types(self):
        """Should accept all valid split types."""
        valid_types = ['manual', 'paycheck', 'shopping', 'bill']

        for split_type in valid_types:
            split = TransactionSplit(
                id=None,
                transaction_id=1,
                group_id=1,
                split_order=0,
                category_id=1,
                amount=Decimal('50.00'),
                split_type=split_type
            )
            assert split.split_type == split_type

    def test_memo_truncated_to_500_chars(self):
        """Should truncate memo to 500 characters."""
        long_memo = "A" * 600
        split = TransactionSplit(
            id=None,
            transaction_id=1,
            group_id=1,
            split_order=0,
            category_id=1,
            amount=Decimal('50.00'),
            memo=long_memo
        )

        assert len(split.memo) == 500

    def test_memo_stripped(self):
        """Should strip whitespace from memo."""
        split = TransactionSplit(
            id=None,
            transaction_id=1,
            group_id=1,
            split_order=0,
            category_id=1,
            amount=Decimal('50.00'),
            memo="  Test memo  "
        )

        assert split.memo == "Test memo"

    def test_repr_string(self):
        """Should have readable string representation."""
        split = TransactionSplit(
            id=42,
            transaction_id=1,
            group_id=1,
            split_order=0,
            category_id=5,
            amount=Decimal('75.50')
        )

        repr_str = repr(split)
        assert "TransactionSplit" in repr_str
        assert "42" in repr_str
        assert "75.50" in repr_str
        assert "5" in repr_str


class TestSplitTransaction:
    """Test SplitTransaction model with balance checking."""

    def create_test_transaction(self, amount=Decimal('-100.00')):
        """Helper to create test transaction."""
        return Transaction(
            id=1,
            account_id=1,
            date="2025-10-23",
            description="Test transaction",
            category="Test",
            amount=amount,
            type='expense'
        )

    def create_test_split(self, transaction_id, amount, order=0):
        """Helper to create test split."""
        return TransactionSplit(
            id=None,
            transaction_id=transaction_id,
            group_id=1,
            split_order=order,
            category_id=1,
            amount=amount
        )

    def test_create_balanced_split_transaction(self):
        """Should create balanced split transaction."""
        transaction = self.create_test_transaction(Decimal('-100.00'))
        splits = [
            self.create_test_split(1, Decimal('70.00'), 0),
            self.create_test_split(1, Decimal('30.00'), 1)
        ]

        split_txn = SplitTransaction(transaction=transaction, splits=splits)

        assert split_txn.split_count == 2
        assert split_txn.total_splits == Decimal('100.00')
        assert split_txn.is_balanced is True
        assert split_txn.balance_difference == Decimal('0')

    def test_reject_single_split(self):
        """Should reject transaction with only one split."""
        transaction = self.create_test_transaction()
        splits = [self.create_test_split(1, Decimal('100.00'))]

        with pytest.raises(ValueError, match="at least 2 splits"):
            SplitTransaction(transaction=transaction, splits=splits)

    def test_reject_empty_splits(self):
        """Should reject transaction with no splits."""
        transaction = self.create_test_transaction()
        splits = []

        with pytest.raises(ValueError, match="at least 2 splits"):
            SplitTransaction(transaction=transaction, splits=splits)

    def test_reject_mismatched_transaction_id(self):
        """Should reject splits belonging to different transaction."""
        transaction = self.create_test_transaction()
        splits = [
            self.create_test_split(1, Decimal('70.00')),
            TransactionSplit(
                id=None,
                transaction_id=999,  # Different transaction
                group_id=1,
                split_order=1,
                category_id=1,
                amount=Decimal('30.00')
            )
        ]

        with pytest.raises(ValueError, match="belongs to transaction"):
            SplitTransaction(transaction=transaction, splits=splits)

    def test_detect_unbalanced_over(self):
        """Should detect when splits exceed transaction amount."""
        transaction = self.create_test_transaction(Decimal('-100.00'))
        splits = [
            self.create_test_split(1, Decimal('70.00')),
            self.create_test_split(1, Decimal('40.00'), 1)  # Total: 110
        ]

        split_txn = SplitTransaction(transaction=transaction, splits=splits)

        assert split_txn.is_balanced is False
        assert split_txn.balance_difference == Decimal('-10.00')  # Over by 10

    def test_detect_unbalanced_under(self):
        """Should detect when splits are less than transaction amount."""
        transaction = self.create_test_transaction(Decimal('-100.00'))
        splits = [
            self.create_test_split(1, Decimal('60.00')),
            self.create_test_split(1, Decimal('30.00'), 1)  # Total: 90
        ]

        split_txn = SplitTransaction(transaction=transaction, splits=splits)

        assert split_txn.is_balanced is False
        assert split_txn.balance_difference == Decimal('10.00')  # Under by 10

    def test_balance_within_one_cent_tolerance(self):
        """Should accept splits balanced within 1 cent."""
        transaction = self.create_test_transaction(Decimal('-100.00'))
        splits = [
            self.create_test_split(1, Decimal('99.995')),  # Rounds to 100.00
            self.create_test_split(1, Decimal('0.005'), 1)
        ]

        split_txn = SplitTransaction(transaction=transaction, splits=splits)

        # Should be balanced within tolerance
        assert abs(split_txn.balance_difference) < Decimal('0.01')

    def test_validate_balance_raises_error(self):
        """Should raise error when validating unbalanced splits."""
        transaction = self.create_test_transaction(Decimal('-100.00'))
        splits = [
            self.create_test_split(1, Decimal('60.00')),
            self.create_test_split(1, Decimal('30.00'), 1)
        ]

        split_txn = SplitTransaction(transaction=transaction, splits=splits)

        with pytest.raises(ValueError, match="doesn't match"):
            split_txn.validate_balance()

    def test_validate_balance_returns_true_when_balanced(self):
        """Should return True when validating balanced splits."""
        transaction = self.create_test_transaction(Decimal('-100.00'))
        splits = [
            self.create_test_split(1, Decimal('70.00')),
            self.create_test_split(1, Decimal('30.00'), 1)
        ]

        split_txn = SplitTransaction(transaction=transaction, splits=splits)

        assert split_txn.validate_balance() is True

    def test_multiple_splits_balanced(self):
        """Should handle multiple splits correctly."""
        transaction = self.create_test_transaction(Decimal('-127.50'))
        splits = [
            self.create_test_split(1, Decimal('85.00'), 0),
            self.create_test_split(1, Decimal('32.50'), 1),
            self.create_test_split(1, Decimal('10.00'), 2)
        ]

        split_txn = SplitTransaction(transaction=transaction, splits=splits)

        assert split_txn.split_count == 3
        assert split_txn.total_splits == Decimal('127.50')
        assert split_txn.is_balanced is True

    def test_repr_string_balanced(self):
        """Should show balanced status in repr."""
        transaction = self.create_test_transaction(Decimal('-100.00'))
        splits = [
            self.create_test_split(1, Decimal('70.00')),
            self.create_test_split(1, Decimal('30.00'), 1)
        ]

        split_txn = SplitTransaction(transaction=transaction, splits=splits)
        repr_str = repr(split_txn)

        assert "SplitTransaction" in repr_str
        assert "✓ Balanced" in repr_str
        assert "splits=2" in repr_str

    def test_repr_string_unbalanced(self):
        """Should show difference in repr when unbalanced."""
        transaction = self.create_test_transaction(Decimal('-100.00'))
        splits = [
            self.create_test_split(1, Decimal('60.00')),
            self.create_test_split(1, Decimal('30.00'), 1)
        ]

        split_txn = SplitTransaction(transaction=transaction, splits=splits)
        repr_str = repr(split_txn)

        assert "⚠ Off by" in repr_str


class TestPaycheckSplit:
    """Test PaycheckSplit template model."""

    def test_create_valid_paycheck(self):
        """Should create valid paycheck split."""
        paycheck = PaycheckSplit(
            gross_pay=Decimal('5000.00'),
            federal_tax=Decimal('750.00'),
            state_tax=Decimal('250.00'),
            social_security=Decimal('310.00'),
            medicare=Decimal('72.50'),
            retirement_401k=Decimal('500.00'),
            health_insurance=Decimal('200.00')
        )

        assert paycheck.gross_pay == Decimal('5000.00')
        assert paycheck.federal_tax == Decimal('750.00')
        assert paycheck.net_pay == Decimal('2917.50')

    def test_amounts_converted_to_decimal(self):
        """Should convert all amounts to Decimal."""
        paycheck = PaycheckSplit(
            gross_pay=5000.00,  # Float
            federal_tax=750.00,
            state_tax=250.00,
            social_security=310.00,
            medicare=72.50,
            retirement_401k=500.00,
            health_insurance=200.00
        )

        assert isinstance(paycheck.gross_pay, Decimal)
        assert isinstance(paycheck.federal_tax, Decimal)
        assert isinstance(paycheck.net_pay, Decimal)

    def test_reject_zero_gross_pay(self):
        """Should reject paycheck with zero gross pay."""
        with pytest.raises(ValueError, match="must be positive"):
            PaycheckSplit(
                gross_pay=Decimal('0'),
                federal_tax=Decimal('0'),
                state_tax=Decimal('0'),
                social_security=Decimal('0'),
                medicare=Decimal('0'),
                retirement_401k=Decimal('0'),
                health_insurance=Decimal('0')
            )

    def test_reject_negative_gross_pay(self):
        """Should reject negative gross pay."""
        with pytest.raises(ValueError, match="must be positive"):
            PaycheckSplit(
                gross_pay=Decimal('-5000.00'),
                federal_tax=Decimal('0'),
                state_tax=Decimal('0'),
                social_security=Decimal('0'),
                medicare=Decimal('0'),
                retirement_401k=Decimal('0'),
                health_insurance=Decimal('0')
            )

    def test_reject_negative_deductions(self):
        """Should reject negative deductions."""
        with pytest.raises(ValueError, match="must be non-negative"):
            PaycheckSplit(
                gross_pay=Decimal('5000.00'),
                federal_tax=Decimal('-750.00'),  # Negative
                state_tax=Decimal('250.00'),
                social_security=Decimal('310.00'),
                medicare=Decimal('72.50'),
                retirement_401k=Decimal('500.00'),
                health_insurance=Decimal('200.00')
            )

    def test_reject_deductions_exceeding_gross_pay(self):
        """Should reject deductions that exceed gross pay."""
        with pytest.raises(ValueError, match="exceed gross pay"):
            PaycheckSplit(
                gross_pay=Decimal('1000.00'),
                federal_tax=Decimal('500.00'),
                state_tax=Decimal('300.00'),
                social_security=Decimal('310.00'),
                medicare=Decimal('100.00'),
                retirement_401k=Decimal('100.00'),
                health_insurance=Decimal('100.00')  # Total: 1410 > 1000
            )

    def test_calculate_total_deductions(self):
        """Should calculate total deductions correctly."""
        paycheck = PaycheckSplit(
            gross_pay=Decimal('5000.00'),
            federal_tax=Decimal('750.00'),
            state_tax=Decimal('250.00'),
            social_security=Decimal('310.00'),
            medicare=Decimal('72.50'),
            retirement_401k=Decimal('500.00'),
            health_insurance=Decimal('200.00')
        )

        expected_total = Decimal('2082.50')
        assert paycheck.total_deductions == expected_total

    def test_calculate_net_pay(self):
        """Should calculate net pay correctly (gross - deductions)."""
        paycheck = PaycheckSplit(
            gross_pay=Decimal('5000.00'),
            federal_tax=Decimal('750.00'),
            state_tax=Decimal('250.00'),
            social_security=Decimal('310.00'),
            medicare=Decimal('72.50'),
            retirement_401k=Decimal('500.00'),
            health_insurance=Decimal('200.00')
        )

        expected_net = Decimal('5000.00') - Decimal('2082.50')
        assert paycheck.net_pay == expected_net
        assert paycheck.net_pay == Decimal('2917.50')

    def test_other_deductions(self):
        """Should handle other deductions."""
        paycheck = PaycheckSplit(
            gross_pay=Decimal('5000.00'),
            federal_tax=Decimal('750.00'),
            state_tax=Decimal('250.00'),
            social_security=Decimal('310.00'),
            medicare=Decimal('72.50'),
            retirement_401k=Decimal('500.00'),
            health_insurance=Decimal('200.00'),
            other_deductions=[
                ('HSA', Decimal('100.00')),
                ('Union Dues', Decimal('50.00'))
            ]
        )

        # Total deductions: 2082.50 + 100 + 50 = 2232.50
        assert paycheck.total_deductions == Decimal('2232.50')
        assert paycheck.net_pay == Decimal('2767.50')

    def test_deduction_count(self):
        """Should count deductions correctly."""
        paycheck = PaycheckSplit(
            gross_pay=Decimal('5000.00'),
            federal_tax=Decimal('750.00'),
            state_tax=Decimal('250.00'),
            social_security=Decimal('310.00'),
            medicare=Decimal('72.50'),
            retirement_401k=Decimal('500.00'),
            health_insurance=Decimal('200.00')
        )

        assert paycheck.deduction_count == 6  # Standard deductions

    def test_deduction_count_with_other(self):
        """Should count other deductions."""
        paycheck = PaycheckSplit(
            gross_pay=Decimal('5000.00'),
            federal_tax=Decimal('750.00'),
            state_tax=Decimal('250.00'),
            social_security=Decimal('310.00'),
            medicare=Decimal('72.50'),
            retirement_401k=Decimal('500.00'),
            health_insurance=Decimal('200.00'),
            other_deductions=[
                ('HSA', Decimal('100.00')),
                ('Union Dues', Decimal('50.00'))
            ]
        )

        assert paycheck.deduction_count == 8  # 6 + 2 other

    def test_calculate_effective_tax_rate(self):
        """Should calculate effective tax rate correctly."""
        paycheck = PaycheckSplit(
            gross_pay=Decimal('5000.00'),
            federal_tax=Decimal('750.00'),
            state_tax=Decimal('250.00'),
            social_security=Decimal('310.00'),
            medicare=Decimal('72.50'),
            retirement_401k=Decimal('500.00'),
            health_insurance=Decimal('200.00')
        )

        # Total taxes: 750 + 250 + 310 + 72.50 = 1382.50
        # Rate: 1382.50 / 5000 * 100 = 27.65%
        expected_rate = Decimal('27.65')
        assert paycheck.effective_tax_rate == expected_rate

    def test_to_splits_basic(self):
        """Should convert paycheck to splits list."""
        paycheck = PaycheckSplit(
            gross_pay=Decimal('5000.00'),
            federal_tax=Decimal('750.00'),
            state_tax=Decimal('250.00'),
            social_security=Decimal('310.00'),
            medicare=Decimal('72.50'),
            retirement_401k=Decimal('500.00'),
            health_insurance=Decimal('200.00')
        )

        splits = paycheck.to_splits()

        assert len(splits) == 7  # 1 income + 6 deductions
        assert splits[0]['category'] == 'Salary'
        assert splits[0]['amount'] == Decimal('5000.00')
        assert splits[1]['category'] == 'Federal Tax'
        assert splits[1]['amount'] == Decimal('750.00')

    def test_to_splits_skips_zero_deductions(self):
        """Should skip zero deductions in splits."""
        paycheck = PaycheckSplit(
            gross_pay=Decimal('5000.00'),
            federal_tax=Decimal('750.00'),
            state_tax=Decimal('0'),  # Zero
            social_security=Decimal('310.00'),
            medicare=Decimal('72.50'),
            retirement_401k=Decimal('0'),  # Zero
            health_insurance=Decimal('200.00')
        )

        splits = paycheck.to_splits()

        # Should have 1 income + 4 non-zero deductions = 5
        assert len(splits) == 5
        category_names = [s['category'] for s in splits]
        assert 'State Tax' not in category_names
        assert '401(k) Contribution' not in category_names

    def test_to_splits_includes_other_deductions(self):
        """Should include other deductions in splits."""
        paycheck = PaycheckSplit(
            gross_pay=Decimal('5000.00'),
            federal_tax=Decimal('750.00'),
            state_tax=Decimal('250.00'),
            social_security=Decimal('310.00'),
            medicare=Decimal('72.50'),
            retirement_401k=Decimal('500.00'),
            health_insurance=Decimal('200.00'),
            other_deductions=[
                ('HSA', Decimal('100.00')),
                ('Union Dues', Decimal('50.00'))
            ]
        )

        splits = paycheck.to_splits()

        assert len(splits) == 9  # 1 income + 6 standard + 2 other
        category_names = [s['category'] for s in splits]
        assert 'HSA' in category_names
        assert 'Union Dues' in category_names

    def test_repr_string(self):
        """Should have readable string representation."""
        paycheck = PaycheckSplit(
            gross_pay=Decimal('5000.00'),
            federal_tax=Decimal('750.00'),
            state_tax=Decimal('250.00'),
            social_security=Decimal('310.00'),
            medicare=Decimal('72.50'),
            retirement_401k=Decimal('500.00'),
            health_insurance=Decimal('200.00')
        )

        repr_str = repr(paycheck)
        assert "PaycheckSplit" in repr_str
        assert "5000" in repr_str
        assert "2917.50" in repr_str  # Net pay
