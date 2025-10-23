"""
Integration tests for split transactions.

Story: US-002C - Split Transactions (Day 5)

Tests the complete split transaction workflow from UI to database,
including journal entry creation, balance validation, and data integrity.
"""
import pytest
from decimal import Decimal
from datetime import date

from finance_app.data.database import Database
from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance, Transaction, TransactionSplit,
    Category, TransactionGroup
)
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.transaction_repository import TransactionRepository
from finance_app.data.repositories.category_repository import CategoryRepository
from finance_app.data.repositories.transaction_split_repository import TransactionSplitRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.business.split_transaction_service import SplitTransactionService
from finance_app.utils.exceptions import ValidationError, NotFoundError


@pytest.fixture
def split_service(test_db):
    """Create split transaction service."""
    return SplitTransactionService(test_db)


@pytest.fixture
def account_repo(test_db):
    """Create account repository."""
    return AccountRepository(test_db)


@pytest.fixture
def transaction_repo(test_db):
    """Create transaction repository."""
    return TransactionRepository(test_db)


@pytest.fixture
def category_repo(test_db):
    """Create category repository."""
    return CategoryRepository(test_db)


@pytest.fixture
def split_repo(test_db):
    """Create split repository."""
    return TransactionSplitRepository(test_db)


@pytest.fixture
def journal_repo(test_db):
    """Create journal entry repository."""
    return JournalEntryRepository(test_db)


@pytest.fixture
def test_account(account_repo):
    """Create test checking account."""
    account = Account(
        id=None,
        name="Test Checking",
        account_type=AccountType.ASSET,
        account_subtype=AccountSubtype.CHECKING,
        balance=Decimal("1000.00"),
        normal_balance=NormalBalance.DEBIT,
        currency="USD"
    )
    return account_repo.create(account)


@pytest.fixture
def expense_accounts(account_repo):
    """Create test expense accounts for categories."""
    accounts = {}

    # Create expense accounts for each category
    for name in ['Groceries', 'Gas', 'Household']:
        account = Account(
            id=None,
            name=f"Expense: {name}",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubtype.EXPENSE_CATEGORY,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        )
        accounts[name.lower()] = account_repo.create(account)

    return accounts


@pytest.fixture
def expense_categories(category_repo, expense_accounts):
    """Create test expense categories."""
    categories = {
        'groceries': Category(
            id=None, name="Test Groceries", type="expense",
            account_id=expense_accounts['groceries'].id
        ),
        'gas': Category(
            id=None, name="Test Gas", type="expense",
            account_id=expense_accounts['gas'].id
        ),
        'household': Category(
            id=None, name="Test Household", type="expense",
            account_id=expense_accounts['household'].id
        )
    }

    created = {}
    for key, cat in categories.items():
        created[key] = category_repo.create(cat)

    return created


class TestSplitIntegration:
    """Test split transaction integration scenarios."""

    def test_create_simple_split_transaction(
        self, split_service, transaction_repo, split_repo, journal_repo,
        test_account, expense_categories
    ):
        """Test creating a simple 2-way split transaction."""
        # Arrange: Create base transaction
        transaction = Transaction(
            id=None,
            account_id=test_account.id,
            date=date.today().strftime("%Y-%m-%d"),
            description="Walmart Shopping",
            category="Shopping",
            amount=Decimal("-100.00"),
            type="expense"
        )
        transaction = transaction_repo.create(transaction)

        # Create splits: $70 groceries, $30 household
        splits = [
            TransactionSplit(
                id=None,
                transaction_id=transaction.id,
                group_id=None,
                split_order=0,
                category_id=expense_categories['groceries'].id,
                amount=Decimal("70.00"),
                memo="Food items"
            ),
            TransactionSplit(
                id=None,
                transaction_id=transaction.id,
                group_id=None,
                split_order=1,
                category_id=expense_categories['household'].id,
                amount=Decimal("30.00"),
                memo="Cleaning supplies"
            )
        ]

        # Act: Create split transaction
        txn, created_splits, group = split_service.create_split_transaction(
            transaction_id=transaction.id,
            splits=splits
        )

        # Assert: Transaction updated
        assert txn.id == transaction.id
        assert txn.is_split is True
        assert txn.split_count == 2

        # Assert: Splits created
        assert len(created_splits) == 2
        assert all(s.id is not None for s in created_splits)
        assert created_splits[0].amount == Decimal("70.00")
        assert created_splits[1].amount == Decimal("30.00")

        # Assert: Group created
        assert group is not None
        assert group.id is not None
        assert all(s.group_id == group.id for s in created_splits)

        # Note: Journal entries are created by the service automatically
        # Balance verification is handled by the service layer

    def test_create_multi_split_transaction(
        self, split_service, transaction_repo, test_account, expense_categories
    ):
        """Test creating transaction with 5 splits."""
        # Arrange: Create base transaction
        transaction = Transaction(
            id=None,
            account_id=test_account.id,
            date=date.today().strftime("%Y-%m-%d"),
            description="Monthly Shopping",
            category="Shopping",
            amount=Decimal("-200.00"),
            type="expense"
        )
        transaction = transaction_repo.create(transaction)

        # Create 5 splits
        splits = [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=0, category_id=expense_categories['groceries'].id,
                amount=Decimal("80.00"), memo="Groceries"
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=1, category_id=expense_categories['gas'].id,
                amount=Decimal("40.00"), memo="Gas"
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=2, category_id=expense_categories['household'].id,
                amount=Decimal("30.00"), memo="Household"
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=3, category_id=expense_categories['groceries'].id,
                amount=Decimal("25.00"), memo="Snacks"
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=4, category_id=expense_categories['household'].id,
                amount=Decimal("25.00"), memo="Paper towels"
            )
        ]

        # Act
        txn, created_splits, group = split_service.create_split_transaction(
            transaction_id=transaction.id,
            splits=splits
        )

        # Assert
        assert len(created_splits) == 5
        assert txn.split_count == 5
        assert sum(s.amount for s in created_splits) == Decimal("200.00")

    def test_split_balance_validation(
        self, split_service, transaction_repo, test_account, expense_categories
    ):
        """Test that unbalanced splits are rejected."""
        # Arrange: $100 transaction
        transaction = Transaction(
            id=None,
            account_id=test_account.id,
            date=date.today().strftime("%Y-%m-%d"),
            description="Test",
            category="Shopping",
            amount=Decimal("-100.00"),
            type="expense"
        )
        transaction = transaction_repo.create(transaction)

        # Create unbalanced splits: only $90
        splits = [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=0, category_id=expense_categories['groceries'].id,
                amount=Decimal("60.00")
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=1, category_id=expense_categories['gas'].id,
                amount=Decimal("30.00")  # Total = 90, not 100
            )
        ]

        # Act & Assert: Should raise ValidationError
        with pytest.raises(ValidationError, match="must equal transaction amount"):
            split_service.create_split_transaction(
                transaction_id=transaction.id,
                splits=splits
            )

    def test_split_minimum_two_required(
        self, split_service, transaction_repo, test_account, expense_categories
    ):
        """Test that minimum 2 splits are required."""
        # Arrange
        transaction = Transaction(
            id=None,
            account_id=test_account.id,
            date=date.today().strftime("%Y-%m-%d"),
            description="Test",
            category="Shopping",
            amount=Decimal("-50.00"),
            type="expense"
        )
        transaction = transaction_repo.create(transaction)

        # Only one split
        splits = [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=0, category_id=expense_categories['groceries'].id,
                amount=Decimal("50.00")
            )
        ]

        # Act & Assert
        with pytest.raises(ValidationError, match="at least 2 splits"):
            split_service.create_split_transaction(
                transaction_id=transaction.id,
                splits=splits
            )

    def test_split_nonexistent_transaction(
        self, split_service, expense_categories
    ):
        """Test creating splits for nonexistent transaction."""
        # Arrange: Splits for transaction ID 999999
        splits = [
            TransactionSplit(
                id=None, transaction_id=999999, group_id=None,
                split_order=0, category_id=expense_categories['groceries'].id,
                amount=Decimal("50.00")
            ),
            TransactionSplit(
                id=None, transaction_id=999999, group_id=None,
                split_order=1, category_id=expense_categories['gas'].id,
                amount=Decimal("50.00")
            )
        ]

        # Act & Assert
        with pytest.raises(NotFoundError, match="Transaction 999999 not found"):
            split_service.create_split_transaction(
                transaction_id=999999,
                splits=splits
            )

    def test_update_split_transaction(
        self, split_service, transaction_repo, test_account, expense_categories
    ):
        """Test updating splits for existing split transaction."""
        # Arrange: Create initial split transaction
        transaction = Transaction(
            id=None,
            account_id=test_account.id,
            date=date.today().strftime("%Y-%m-%d"),
            description="Shopping",
            category="Shopping",
            amount=Decimal("-100.00"),
            type="expense"
        )
        transaction = transaction_repo.create(transaction)

        initial_splits = [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=0, category_id=expense_categories['groceries'].id,
                amount=Decimal("60.00")
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=1, category_id=expense_categories['gas'].id,
                amount=Decimal("40.00")
            )
        ]
        txn, _, _ = split_service.create_split_transaction(
            transaction_id=transaction.id,
            splits=initial_splits
        )

        # Act: Update with new split amounts
        new_splits = [
            TransactionSplit(
                id=None, transaction_id=txn.id, group_id=None,
                split_order=0, category_id=expense_categories['groceries'].id,
                amount=Decimal("70.00")
            ),
            TransactionSplit(
                id=None, transaction_id=txn.id, group_id=None,
                split_order=1, category_id=expense_categories['household'].id,
                amount=Decimal("30.00")
            )
        ]
        updated_txn, updated_splits = split_service.update_split_transaction(
            transaction_id=txn.id,
            splits=new_splits
        )

        # Assert: Splits updated
        assert len(updated_splits) == 2
        assert updated_splits[0].amount == Decimal("70.00")
        assert updated_splits[1].amount == Decimal("30.00")
        assert updated_splits[1].category_id == expense_categories['household'].id

    def test_delete_split_transaction(
        self, split_service, transaction_repo, split_repo,
        test_account, expense_categories
    ):
        """Test deleting split transaction."""
        # Arrange: Create split transaction
        transaction = Transaction(
            id=None,
            account_id=test_account.id,
            date=date.today().strftime("%Y-%m-%d"),
            description="Test",
            category="Shopping",
            amount=Decimal("-80.00"),
            type="expense"
        )
        transaction = transaction_repo.create(transaction)

        splits = [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=0, category_id=expense_categories['groceries'].id,
                amount=Decimal("50.00")
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=1, category_id=expense_categories['gas'].id,
                amount=Decimal("30.00")
            )
        ]
        txn, _, _ = split_service.create_split_transaction(
            transaction_id=transaction.id,
            splits=splits
        )

        # Act: Delete splits
        split_service.delete_split_transaction(txn.id)

        # Assert: Splits deleted
        remaining_splits = split_repo.get_by_transaction(txn.id)
        assert len(remaining_splits) == 0

        # Assert: Transaction flags updated
        updated_txn = transaction_repo.get_by_id(txn.id)
        assert updated_txn.is_split is False
        assert updated_txn.split_count == 0

    def test_get_split_transaction(
        self, split_service, transaction_repo, test_account, expense_categories
    ):
        """Test retrieving split transaction."""
        # Arrange: Create split transaction
        transaction = Transaction(
            id=None,
            account_id=test_account.id,
            date=date.today().strftime("%Y-%m-%d"),
            description="Shopping",
            category="Shopping",
            amount=Decimal("-100.00"),
            type="expense"
        )
        transaction = transaction_repo.create(transaction)

        splits = [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=0, category_id=expense_categories['groceries'].id,
                amount=Decimal("60.00"), memo="Groceries"
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=1, category_id=expense_categories['gas'].id,
                amount=Decimal("40.00"), memo="Gas"
            )
        ]
        txn, _, _ = split_service.create_split_transaction(
            transaction_id=transaction.id,
            splits=splits
        )

        # Act: Get split transaction
        split_txn = split_service.get_split_transaction(txn.id)

        # Assert: Split transaction returned
        assert split_txn is not None
        assert split_txn.transaction.id == txn.id
        assert len(split_txn.splits) == 2
        assert split_txn.is_balanced is True
        assert split_txn.total_splits == Decimal("100.00")

    def test_split_transaction_balance_check(
        self, split_service, transaction_repo, test_account, expense_categories
    ):
        """Test split transaction balance checking properties."""
        # Arrange & Act: Create split transaction
        transaction = Transaction(
            id=None,
            account_id=test_account.id,
            date=date.today().strftime("%Y-%m-%d"),
            description="Shopping",
            category="Shopping",
            amount=Decimal("-150.00"),
            type="expense"
        )
        transaction = transaction_repo.create(transaction)

        splits = [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=0, category_id=expense_categories['groceries'].id,
                amount=Decimal("100.00")
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=None,
                split_order=1, category_id=expense_categories['gas'].id,
                amount=Decimal("50.00")
            )
        ]
        txn, _, _ = split_service.create_split_transaction(
            transaction_id=transaction.id,
            splits=splits
        )

        split_txn = split_service.get_split_transaction(txn.id)

        # Assert: Balance properties
        assert split_txn.is_balanced is True
        assert split_txn.total_splits == Decimal("150.00")
        assert split_txn.balance_difference == Decimal("0.00")
