"""
Integration tests for transfer functionality.

Tests end-to-end transfers with real database.

Story: US-002B - Balanced Transaction Groups (Phase 3)
"""
import pytest
from decimal import Decimal

from finance_app.data.database import Database
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.business.double_entry_service import DoubleEntryService
from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance
)
from finance_app.utils.exceptions import ValidationError, NotFoundError


class TestTransferIntegration:
    """Integration tests for account transfers."""

    @pytest.fixture
    def test_db(self):
        """Create test database."""
        db = Database(":memory:")
        yield db
        db.close()

    @pytest.fixture
    def test_accounts(self, test_db):
        """Create test accounts."""
        account_repo = AccountRepository(test_db)

        checking = account_repo.create(Account(
            id=None,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT
        ))

        savings = account_repo.create(Account(
            id=None,
            name="Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            balance=Decimal("500.00"),
            normal_balance=NormalBalance.DEBIT
        ))

        cash = account_repo.create(Account(
            id=None,
            name="Cash",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CASH,
            balance=Decimal("200.00"),
            normal_balance=NormalBalance.DEBIT
        ))

        return {"checking": checking, "savings": savings, "cash": cash}

    def test_simple_transfer(self, test_db, test_accounts):
        """
        Test simple transfer: $300 from Checking to Savings.

        Expected:
        - Checking: 1000 - 300 = 700
        - Savings: 500 + 300 = 800
        """
        service = DoubleEntryService(test_db)
        checking = test_accounts["checking"]
        savings = test_accounts["savings"]

        # Execute transfer
        group, entries = service.create_transfer(
            from_account_id=checking.id,
            to_account_id=savings.id,
            amount=Decimal("300.00"),
            date="2025-10-22",
            description="Monthly savings transfer"
        )

        # Verify group
        assert group.id is not None
        assert group.is_balanced is True
        assert group.total_debits == Decimal("300.00")
        assert group.total_credits == Decimal("300.00")

        # Verify entries
        assert len(entries) == 2
        assert all(e.group_id == group.id for e in entries)
        assert all(e.entry_type.value == "transfer" for e in entries)

        # Verify balances
        account_repo = AccountRepository(test_db)
        checking_after = account_repo.get_by_id(checking.id)
        savings_after = account_repo.get_by_id(savings.id)

        assert checking_after.balance == Decimal("700.00")  # 1000 - 300
        assert savings_after.balance == Decimal("800.00")   # 500 + 300

    def test_multiple_transfers_sequential(self, test_db, test_accounts):
        """Test multiple sequential transfers."""
        service = DoubleEntryService(test_db)
        checking = test_accounts["checking"]
        savings = test_accounts["savings"]
        cash = test_accounts["cash"]

        # Transfer 1: Checking → Savings ($200)
        service.create_transfer(
            from_account_id=checking.id,
            to_account_id=savings.id,
            amount=Decimal("200.00"),
            date="2025-10-22",
            description="Transfer 1"
        )

        # Transfer 2: Checking → Cash ($100)
        service.create_transfer(
            from_account_id=checking.id,
            to_account_id=cash.id,
            amount=Decimal("100.00"),
            date="2025-10-22",
            description="Transfer 2"
        )

        # Transfer 3: Savings → Cash ($50)
        service.create_transfer(
            from_account_id=savings.id,
            to_account_id=cash.id,
            amount=Decimal("50.00"),
            date="2025-10-22",
            description="Transfer 3"
        )

        # Verify final balances
        account_repo = AccountRepository(test_db)
        checking_final = account_repo.get_by_id(checking.id)
        savings_final = account_repo.get_by_id(savings.id)
        cash_final = account_repo.get_by_id(cash.id)

        assert checking_final.balance == Decimal("700.00")  # 1000 - 200 - 100
        assert savings_final.balance == Decimal("650.00")   # 500 + 200 - 50
        assert cash_final.balance == Decimal("350.00")      # 200 + 100 + 50

    def test_transfer_with_insufficient_funds_allowed(self, test_db, test_accounts):
        """
        Test transfer that creates negative balance (overdraft).

        Note: We don't prevent negative balances at the transfer level.
        Business logic can add that validation if needed.
        """
        service = DoubleEntryService(test_db)
        checking = test_accounts["checking"]
        savings = test_accounts["savings"]

        # Transfer more than available balance
        group, entries = service.create_transfer(
            from_account_id=checking.id,
            to_account_id=savings.id,
            amount=Decimal("1500.00"),  # More than $1000 balance
            date="2025-10-22",
            description="Overdraft transfer"
        )

        # Transfer should succeed (overdraft allowed)
        assert group.is_balanced is True

        # Verify balances
        account_repo = AccountRepository(test_db)
        checking_after = account_repo.get_by_id(checking.id)
        savings_after = account_repo.get_by_id(savings.id)

        assert checking_after.balance == Decimal("-500.00")  # 1000 - 1500 = -500
        assert savings_after.balance == Decimal("2000.00")   # 500 + 1500

    def test_negative_amount_rejected(self, test_db, test_accounts):
        """Transfer with negative amount should raise ValidationError."""
        service = DoubleEntryService(test_db)

        with pytest.raises(ValidationError, match="must be positive"):
            service.create_transfer(
                from_account_id=test_accounts["checking"].id,
                to_account_id=test_accounts["savings"].id,
                amount=Decimal("-100.00"),
                date="2025-10-22",
                description="Invalid"
            )

        # Verify no changes
        account_repo = AccountRepository(test_db)
        checking = account_repo.get_by_id(test_accounts["checking"].id)
        assert checking.balance == Decimal("1000.00")  # Unchanged

    def test_same_account_rejected(self, test_db, test_accounts):
        """Transfer to same account should raise ValidationError."""
        service = DoubleEntryService(test_db)

        with pytest.raises(ValidationError, match="same account"):
            service.create_transfer(
                from_account_id=test_accounts["checking"].id,
                to_account_id=test_accounts["checking"].id,  # Same!
                amount=Decimal("100.00"),
                date="2025-10-22",
                description="Invalid"
            )

    def test_nonexistent_account_rejected(self, test_db, test_accounts):
        """Transfer to/from nonexistent account should raise NotFoundError."""
        service = DoubleEntryService(test_db)

        # Nonexistent source account
        with pytest.raises(NotFoundError, match="Source account"):
            service.create_transfer(
                from_account_id=999,  # Doesn't exist
                to_account_id=test_accounts["checking"].id,
                amount=Decimal("100.00"),
                date="2025-10-22",
                description="Invalid"
            )

        # Nonexistent destination account
        with pytest.raises(NotFoundError, match="Destination account"):
            service.create_transfer(
                from_account_id=test_accounts["checking"].id,
                to_account_id=999,  # Doesn't exist
                amount=Decimal("100.00"),
                date="2025-10-22",
                description="Invalid"
            )

    def test_transfer_with_reference_and_notes(self, test_db, test_accounts):
        """Transfer with reference number and notes should store them."""
        service = DoubleEntryService(test_db)

        group, entries = service.create_transfer(
            from_account_id=test_accounts["checking"].id,
            to_account_id=test_accounts["savings"].id,
            amount=Decimal("100.00"),
            date="2025-10-22",
            description="Test transfer",
            reference_number="REF-12345",
            notes="Monthly automatic transfer"
        )

        # Verify reference and notes
        assert all(e.reference_number == "REF-12345" for e in entries)
        assert group.notes == "Monthly automatic transfer"

    def test_transfer_journal_entries_queryable(self, test_db, test_accounts):
        """Transfer journal entries should be queryable."""
        service = DoubleEntryService(test_db)
        checking = test_accounts["checking"]

        # Create transfer
        service.create_transfer(
            from_account_id=checking.id,
            to_account_id=test_accounts["savings"].id,
            amount=Decimal("100.00"),
            date="2025-10-22",
            description="Test transfer"
        )

        # Query journal entries for checking account
        entries = service.get_journal_entries(checking.id)

        assert len(entries) >= 1
        transfer_entry = entries[0]
        assert transfer_entry.entry_type.value == "transfer"
        assert transfer_entry.credit_amount == Decimal("100.00")

    def test_decimal_precision_maintained(self, test_db, test_accounts):
        """Transfer should maintain Decimal precision."""
        service = DoubleEntryService(test_db)

        precise_amount = Decimal("123.456789")
        group, entries = service.create_transfer(
            from_account_id=test_accounts["checking"].id,
            to_account_id=test_accounts["savings"].id,
            amount=precise_amount,
            date="2025-10-22",
            description="Precision test"
        )

        # Verify precision maintained
        account_repo = AccountRepository(test_db)
        checking = account_repo.get_by_id(test_accounts["checking"].id)
        savings = account_repo.get_by_id(test_accounts["savings"].id)

        assert checking.balance == Decimal("1000.00") - precise_amount
        assert savings.balance == Decimal("500.00") + precise_amount

    def test_bidirectional_transfer(self, test_db, test_accounts):
        """Test transferring back and forth between accounts."""
        service = DoubleEntryService(test_db)
        checking = test_accounts["checking"]
        savings = test_accounts["savings"]

        # Transfer Checking → Savings
        service.create_transfer(
            from_account_id=checking.id,
            to_account_id=savings.id,
            amount=Decimal("200.00"),
            date="2025-10-22",
            description="Forward transfer"
        )

        # Transfer Savings → Checking (reverse)
        service.create_transfer(
            from_account_id=savings.id,
            to_account_id=checking.id,
            amount=Decimal("150.00"),
            date="2025-10-23",
            description="Reverse transfer"
        )

        # Verify final balances
        account_repo = AccountRepository(test_db)
        checking_final = account_repo.get_by_id(checking.id)
        savings_final = account_repo.get_by_id(savings.id)

        assert checking_final.balance == Decimal("950.00")  # 1000 - 200 + 150
        assert savings_final.balance == Decimal("550.00")   # 500 + 200 - 150
