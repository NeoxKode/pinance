"""
Unit tests for TransactionSplitRepository.

Story: US-002C - Split Transactions (Day 2)

Tests cover:
- CRUD operations (create, create_splits, update, delete)
- Query methods (get_by_id, get_by_transaction, get_by_group, get_by_category)
- Helper methods (count, total amount)
- Atomic transactions
- Foreign key validation
- Error handling (NotFoundError, DatabaseError, ValidationError)
- Edge cases and boundary conditions

Total: 20+ comprehensive tests
"""

import pytest
from decimal import Decimal
from datetime import datetime

from finance_app.data.repositories.transaction_split_repository import TransactionSplitRepository
from finance_app.data.repositories.transaction_repository import TransactionRepository
from finance_app.data.repositories.transaction_group_repository import TransactionGroupRepository
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.category_repository import CategoryRepository
from finance_app.data.models import (
    TransactionSplit, Transaction, TransactionGroup, Account, Category,
    AccountType, AccountSubtype, NormalBalance
)
from finance_app.utils.exceptions import NotFoundError, ValidationError, DatabaseError


class TestTransactionSplitRepositoryCreate:
    """Tests for creating transaction splits."""

    def test_create_single_split(self, test_db):
        """Should create a single split with all required fields."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create dependencies
        account = Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        )
        account = account_repo.create(account)

        category = Category(
            id=None, name="Test Category", type="expense", account_id=account.id
        )
        category = category_repo.create(category)

        group = TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Test Group",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        )
        group = group_repo.create(group)

        transaction = Transaction(
            id=None,
            account_id=account.id,
            amount=Decimal('-100.00'),
            description="Split Transaction",
            date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name,
            type="expense"
        )
        transaction = txn_repo.create(transaction)

        # Create split
        split = TransactionSplit(
            id=None,
            transaction_id=transaction.id,
            group_id=group.id,
            split_order=0,
            category_id=category.id,
            amount=Decimal('100.00'),
            memo="First split",
            account_id=account.id,
            split_type='manual'
        )

        result = split_repo.create(split)

        # Verify
        assert result.id is not None
        assert result.transaction_id == transaction.id
        assert result.group_id == group.id
        assert result.category_id == category.id
        assert result.amount == Decimal('100.00')
        assert result.memo == "First split"
        assert result.split_type == 'manual'
        assert result.created_at is not None

    def test_create_splits_atomic(self, test_db):
        """Should create multiple splits atomically."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create dependencies
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category1 = category_repo.create(Category(
            id=None, name="Test Category 1", type="expense", account_id=account.id
        ))
        category2 = category_repo.create(Category(
            id=None, name="Test Category 2", type="expense", account_id=account.id
        ))

        group = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Shopping",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        transaction = txn_repo.create(Transaction(
            id=None,
            account_id=account.id,
            amount=Decimal('-100.00'),
            description="Shopping Trip",
            date=datetime.now().strftime('%Y-%m-%d'),
            category=category1.name,
            type="expense"
        ))

        # Create splits
        splits = [
            TransactionSplit(
                id=None,
                transaction_id=transaction.id,
                group_id=group.id,
                split_order=0,
                category_id=category1.id,
                amount=Decimal('70.00'),
                memo="Groceries",
                split_type='manual'
            ),
            TransactionSplit(
                id=None,
                transaction_id=transaction.id,
                group_id=group.id,
                split_order=1,
                category_id=category2.id,
                amount=Decimal('30.00'),
                memo="Gas",
                split_type='manual'
            )
        ]

        result = split_repo.create_splits(transaction.id, splits)

        # Verify
        assert len(result) == 2
        assert all(s.id is not None for s in result)
        assert result[0].split_order == 0
        assert result[1].split_order == 1
        assert result[0].amount == Decimal('70.00')
        assert result[1].amount == Decimal('30.00')

        # Verify transaction updated
        updated_txn = txn_repo.get_by_id(transaction.id)
        assert updated_txn.is_split is True
        assert updated_txn.split_count == 2

    def test_create_splits_minimum_two_required(self, test_db):
        """Should reject creating splits with less than 2 splits."""
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Setup minimal data
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category = category_repo.create(Category(
            id=None, name="Test", type="expense", account_id=account.id
        ))

        transaction = txn_repo.create(Transaction(
            id=None,
            account_id=account.id,
            amount=Decimal('-100.00'),
            description="Test",
            date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name,
            type="expense"
        ))

        # Try to create with only 1 split
        splits = [
            TransactionSplit(
                id=None,
                transaction_id=transaction.id,
                group_id=1,
                split_order=0,
                category_id=category.id,
                amount=Decimal('100.00'),
                split_type='manual'
            )
        ]

        with pytest.raises(ValidationError, match="at least 2 splits"):
            split_repo.create_splits(transaction.id, splits)

    def test_create_split_invalid_transaction_id(self, test_db):
        """Should reject split with non-existent transaction."""
        split_repo = TransactionSplitRepository(test_db)

        split = TransactionSplit(
            id=None,
            transaction_id=99999,
            group_id=1,
            split_order=0,
            category_id=1,
            amount=Decimal('100.00'),
            split_type='manual'
        )

        with pytest.raises(NotFoundError, match="Transaction 99999 not found"):
            split_repo.create(split)

    def test_create_split_invalid_group_id(self, test_db):
        """Should reject split with non-existent group."""
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create dependencies
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category = category_repo.create(Category(
            id=None, name="Test", type="expense", account_id=account.id
        ))

        transaction = txn_repo.create(Transaction(
            id=None,
            account_id=account.id,
            amount=Decimal('-100.00'),
            description="Test",
            date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name,
            type="expense"
        ))

        split = TransactionSplit(
            id=None,
            transaction_id=transaction.id,
            group_id=99999,
            split_order=0,
            category_id=category.id,
            amount=Decimal('100.00'),
            split_type='manual'
        )

        with pytest.raises(NotFoundError, match="Transaction group 99999 not found"):
            split_repo.create(split)

    def test_create_split_invalid_category_id(self, test_db):
        """Should reject split with non-existent category."""
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create dependencies
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category = category_repo.create(Category(
            id=None, name="Test", type="expense", account_id=account.id
        ))

        group = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Test",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        transaction = txn_repo.create(Transaction(
            id=None,
            account_id=account.id,
            amount=Decimal('-100.00'),
            description="Test",
            date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name,
            type="expense"
        ))

        split = TransactionSplit(
            id=None,
            transaction_id=transaction.id,
            group_id=group.id,
            split_order=0,
            category_id=99999,
            amount=Decimal('100.00'),
            split_type='manual'
        )

        with pytest.raises(NotFoundError, match="Category 99999 not found"):
            split_repo.create(split)


class TestTransactionSplitRepositoryQuery:
    """Tests for querying transaction splits."""

    def test_get_by_id(self, test_db):
        """Should retrieve split by ID."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create test data
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category = category_repo.create(Category(
            id=None, name="Test", type="expense", account_id=account.id
        ))

        group = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Test",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        transaction = txn_repo.create(Transaction(
            id=None,
            account_id=account.id,
            amount=Decimal('-100.00'),
            description="Test",
            date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name,
            type="expense"
        ))

        split = split_repo.create(TransactionSplit(
            id=None,
            transaction_id=transaction.id,
            group_id=group.id,
            split_order=0,
            category_id=category.id,
            amount=Decimal('100.00'),
            memo="Test split",
            split_type='manual'
        ))

        # Query
        result = split_repo.get_by_id(split.id)

        # Verify
        assert result is not None
        assert result.id == split.id
        assert result.transaction_id == transaction.id
        assert result.amount == Decimal('100.00')
        assert result.memo == "Test split"

    def test_get_by_id_not_found(self, test_db):
        """Should return None for non-existent split."""
        split_repo = TransactionSplitRepository(test_db)
        result = split_repo.get_by_id(99999)
        assert result is None

    def test_get_by_transaction(self, test_db):
        """Should retrieve all splits for a transaction ordered by split_order."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create test data
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category1 = category_repo.create(Category(
            id=None, name="Cat1", type="expense", account_id=account.id
        ))
        category2 = category_repo.create(Category(
            id=None, name="Cat2", type="expense", account_id=account.id
        ))
        category3 = category_repo.create(Category(
            id=None, name="Cat3", type="expense", account_id=account.id
        ))

        group = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Test",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        transaction = txn_repo.create(Transaction(
            id=None,
            account_id=account.id,
            amount=Decimal('-150.00'),
            description="Test",
            date=datetime.now().strftime('%Y-%m-%d'),
            category=category1.name,
            type="expense"
        ))

        # Create splits in non-sequential order
        splits = [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=0, category_id=category1.id, amount=Decimal('50.00'),
                memo="Third", split_type='manual'
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=1, category_id=category2.id, amount=Decimal('60.00'),
                memo="First", split_type='manual'
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=2, category_id=category3.id, amount=Decimal('40.00'),
                memo="Second", split_type='manual'
            )
        ]

        split_repo.create_splits(transaction.id, splits)

        # Query
        result = split_repo.get_by_transaction(transaction.id)

        # Verify ordering
        assert len(result) == 3
        assert result[0].split_order == 0
        assert result[1].split_order == 1
        assert result[2].split_order == 2
        assert result[0].memo == "Third"
        assert result[1].memo == "First"
        assert result[2].memo == "Second"

    def test_get_by_transaction_empty(self, test_db):
        """Should return empty list for transaction with no splits."""
        split_repo = TransactionSplitRepository(test_db)
        result = split_repo.get_by_transaction(99999)
        assert result == []

    def test_get_by_group(self, test_db):
        """Should retrieve all splits for a transaction group."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create test data
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category = category_repo.create(Category(
            id=None, name="Test", type="expense", account_id=account.id
        ))

        group1 = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Group 1",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))
        group2 = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Group 2",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        txn1 = txn_repo.create(Transaction(
            id=None, account_id=account.id, amount=Decimal('-100.00'),
            description="Txn 1", date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name, type="expense"
        ))

        txn2 = txn_repo.create(Transaction(
            id=None, account_id=account.id, amount=Decimal('-50.00'),
            description="Txn 2", date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name, type="expense"
        ))

        # Create splits for group1
        split_repo.create_splits(txn1.id, [
            TransactionSplit(
                id=None, transaction_id=txn1.id, group_id=group1.id,
                split_order=0, category_id=category.id, amount=Decimal('60.00'),
                split_type='manual'
            ),
            TransactionSplit(
                id=None, transaction_id=txn1.id, group_id=group1.id,
                split_order=1, category_id=category.id, amount=Decimal('40.00'),
                split_type='manual'
            )
        ])

        split_repo.create_splits(txn2.id, [
            TransactionSplit(
                id=None, transaction_id=txn2.id, group_id=group1.id,
                split_order=0, category_id=category.id, amount=Decimal('30.00'),
                split_type='manual'
            ),
            TransactionSplit(
                id=None, transaction_id=txn2.id, group_id=group1.id,
                split_order=1, category_id=category.id, amount=Decimal('20.00'),
                split_type='manual'
            )
        ])

        # Create splits for group2
        txn3 = txn_repo.create(Transaction(
            id=None, account_id=account.id, amount=Decimal('-75.00'),
            description="Txn 3", date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name, type="expense"
        ))

        split_repo.create_splits(txn3.id, [
            TransactionSplit(
                id=None, transaction_id=txn3.id, group_id=group2.id,
                split_order=0, category_id=category.id, amount=Decimal('50.00'),
                split_type='manual'
            ),
            TransactionSplit(
                id=None, transaction_id=txn3.id, group_id=group2.id,
                split_order=1, category_id=category.id, amount=Decimal('25.00'),
                split_type='manual'
            )
        ])

        # Query group1
        result = split_repo.get_by_group(group1.id)

        # Verify
        assert len(result) == 4
        assert all(s.group_id == group1.id for s in result)

    def test_get_by_category(self, test_db):
        """Should retrieve splits by category."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create test data
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        groceries = category_repo.create(Category(
            id=None, name="Test Groceries", type="expense", account_id=account.id
        ))
        gas = category_repo.create(Category(
            id=None, name="Test Gas", type="expense", account_id=account.id
        ))

        group = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Test",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        # Create multiple transactions with splits
        for i in range(3):
            txn = txn_repo.create(Transaction(
                id=None, account_id=account.id, amount=Decimal('-100.00'),
                description=f"Txn {i}", date=datetime.now().strftime('%Y-%m-%d'),
                category=groceries.name, type="expense"
            ))

            split_repo.create_splits(txn.id, [
                TransactionSplit(
                    id=None, transaction_id=txn.id, group_id=group.id,
                    split_order=0, category_id=groceries.id, amount=Decimal('70.00'),
                    split_type='manual'
                ),
                TransactionSplit(
                    id=None, transaction_id=txn.id, group_id=group.id,
                    split_order=1, category_id=gas.id, amount=Decimal('30.00'),
                    split_type='manual'
                )
            ])

        # Query groceries category
        result = split_repo.get_by_category(groceries.id)

        # Verify
        assert len(result) == 3
        assert all(s.category_id == groceries.id for s in result)
        assert all(s.amount == Decimal('70.00') for s in result)

    def test_get_by_category_with_limit(self, test_db):
        """Should respect limit parameter when querying by category."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create test data
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category = category_repo.create(Category(
            id=None, name="Test", type="expense", account_id=account.id
        ))

        group = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Test",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        # Create 5 transactions
        for i in range(5):
            txn = txn_repo.create(Transaction(
                id=None, account_id=account.id, amount=Decimal('-100.00'),
                description=f"Txn {i}", date=datetime.now().strftime('%Y-%m-%d'),
                category=category.name, type="expense"
            ))

            split_repo.create_splits(txn.id, [
                TransactionSplit(
                    id=None, transaction_id=txn.id, group_id=group.id,
                    split_order=0, category_id=category.id, amount=Decimal('60.00'),
                    split_type='manual'
                ),
                TransactionSplit(
                    id=None, transaction_id=txn.id, group_id=group.id,
                    split_order=1, category_id=category.id, amount=Decimal('40.00'),
                    split_type='manual'
                )
            ])

        # Query with limit
        result = split_repo.get_by_category(category.id, limit=3)

        # Verify
        assert len(result) == 3


class TestTransactionSplitRepositoryUpdate:
    """Tests for updating transaction splits."""

    def test_update_split(self, test_db):
        """Should update existing split."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create test data
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category1 = category_repo.create(Category(
            id=None, name="Original", type="expense", account_id=account.id
        ))
        category2 = category_repo.create(Category(
            id=None, name="Updated", type="expense", account_id=account.id
        ))

        group = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Test",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        transaction = txn_repo.create(Transaction(
            id=None, account_id=account.id, amount=Decimal('-100.00'),
            description="Test", date=datetime.now().strftime('%Y-%m-%d'),
            category=category1.name, type="expense"
        ))

        split = split_repo.create(TransactionSplit(
            id=None, transaction_id=transaction.id, group_id=group.id,
            split_order=0, category_id=category1.id, amount=Decimal('100.00'),
            memo="Original", split_type='manual'
        ))

        # Update split
        split.category_id = category2.id
        split.amount = Decimal('75.00')
        split.memo = "Updated"

        result = split_repo.update(split)

        # Verify
        assert result.id == split.id
        assert result.category_id == category2.id
        assert result.amount == Decimal('75.00')
        assert result.memo == "Updated"

    def test_update_split_without_id(self, test_db):
        """Should reject update without split ID."""
        split_repo = TransactionSplitRepository(test_db)

        split = TransactionSplit(
            id=None,
            transaction_id=1,
            group_id=1,
            split_order=0,
            category_id=1,
            amount=Decimal('100.00'),
            split_type='manual'
        )

        with pytest.raises(ValidationError, match="Cannot update split without ID"):
            split_repo.update(split)

    def test_update_nonexistent_split(self, test_db):
        """Should reject update of non-existent split."""
        split_repo = TransactionSplitRepository(test_db)

        split = TransactionSplit(
            id=99999,
            transaction_id=1,
            group_id=1,
            split_order=0,
            category_id=1,
            amount=Decimal('100.00'),
            split_type='manual'
        )

        with pytest.raises(NotFoundError, match="Split 99999 not found"):
            split_repo.update(split)


class TestTransactionSplitRepositoryDelete:
    """Tests for deleting transaction splits."""

    def test_delete_single_split(self, test_db):
        """Should delete a single split and update transaction."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create test data
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category = category_repo.create(Category(
            id=None, name="Test", type="expense", account_id=account.id
        ))

        group = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Test",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        transaction = txn_repo.create(Transaction(
            id=None, account_id=account.id, amount=Decimal('-150.00'),
            description="Test", date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name, type="expense"
        ))

        # Create 3 splits
        splits = split_repo.create_splits(transaction.id, [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=0, category_id=category.id, amount=Decimal('50.00'),
                split_type='manual'
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=1, category_id=category.id, amount=Decimal('60.00'),
                split_type='manual'
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=2, category_id=category.id, amount=Decimal('40.00'),
                split_type='manual'
            )
        ])

        # Delete one split
        split_repo.delete(splits[1].id)

        # Verify
        remaining = split_repo.get_by_transaction(transaction.id)
        assert len(remaining) == 2

        # Verify transaction updated
        txn = txn_repo.get_by_id(transaction.id)
        assert txn.split_count == 2
        assert txn.is_split is True

    def test_delete_last_splits_clears_flag(self, test_db):
        """Should clear is_split flag when all splits deleted."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create test data
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category = category_repo.create(Category(
            id=None, name="Test", type="expense", account_id=account.id
        ))

        group = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Test",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        transaction = txn_repo.create(Transaction(
            id=None, account_id=account.id, amount=Decimal('-100.00'),
            description="Test", date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name, type="expense"
        ))

        splits = split_repo.create_splits(transaction.id, [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=0, category_id=category.id, amount=Decimal('60.00'),
                split_type='manual'
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=1, category_id=category.id, amount=Decimal('40.00'),
                split_type='manual'
            )
        ])

        # Delete all splits individually
        split_repo.delete(splits[0].id)
        split_repo.delete(splits[1].id)

        # Verify transaction cleared
        txn = txn_repo.get_by_id(transaction.id)
        assert txn.is_split is False
        assert txn.split_count == 0

    def test_delete_nonexistent_split(self, test_db):
        """Should raise NotFoundError for non-existent split."""
        split_repo = TransactionSplitRepository(test_db)

        with pytest.raises(NotFoundError, match="Split 99999 not found"):
            split_repo.delete(99999)

    def test_delete_all_for_transaction(self, test_db):
        """Should delete all splits for a transaction atomically."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create test data
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category = category_repo.create(Category(
            id=None, name="Test", type="expense", account_id=account.id
        ))

        group = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Test",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        transaction = txn_repo.create(Transaction(
            id=None, account_id=account.id, amount=Decimal('-100.00'),
            description="Test", date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name, type="expense"
        ))

        # Create splits
        split_repo.create_splits(transaction.id, [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=0, category_id=category.id, amount=Decimal('60.00'),
                split_type='manual'
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=1, category_id=category.id, amount=Decimal('40.00'),
                split_type='manual'
            )
        ])

        # Delete all
        deleted_count = split_repo.delete_all_for_transaction(transaction.id)

        # Verify
        assert deleted_count == 2

        remaining = split_repo.get_by_transaction(transaction.id)
        assert len(remaining) == 0

        txn = txn_repo.get_by_id(transaction.id)
        assert txn.is_split is False
        assert txn.split_count == 0


class TestTransactionSplitRepositoryHelpers:
    """Tests for helper methods."""

    def test_count_by_transaction(self, test_db):
        """Should count splits for a transaction."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create test data
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category = category_repo.create(Category(
            id=None, name="Test", type="expense", account_id=account.id
        ))

        group = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Test",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        transaction = txn_repo.create(Transaction(
            id=None, account_id=account.id, amount=Decimal('-100.00'),
            description="Test", date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name, type="expense"
        ))

        # Create splits
        split_repo.create_splits(transaction.id, [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=0, category_id=category.id, amount=Decimal('60.00'),
                split_type='manual'
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=1, category_id=category.id, amount=Decimal('40.00'),
                split_type='manual'
            )
        ])

        # Count
        count = split_repo.count_by_transaction(transaction.id)
        assert count == 2

    def test_count_by_transaction_zero(self, test_db):
        """Should return 0 for transaction with no splits."""
        split_repo = TransactionSplitRepository(test_db)
        count = split_repo.count_by_transaction(99999)
        assert count == 0

    def test_get_total_amount_by_transaction(self, test_db):
        """Should calculate total amount of splits."""
        # Setup
        split_repo = TransactionSplitRepository(test_db)
        txn_repo = TransactionRepository(test_db)
        group_repo = TransactionGroupRepository(test_db)
        account_repo = AccountRepository(test_db)
        category_repo = CategoryRepository(test_db)

        # Create test data
        account = account_repo.create(Account(
            id=None, name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal('1000.00'),
            normal_balance=NormalBalance.DEBIT,
            currency="USD"
        ))

        category = category_repo.create(Category(
            id=None, name="Test", type="expense", account_id=account.id
        ))

        group = group_repo.create(TransactionGroup(
            id=None,
            group_date=datetime.now().strftime('%Y-%m-%d'),
            description="Test",
            total_debits=Decimal('0'),
            total_credits=Decimal('0')
        ))

        transaction = txn_repo.create(Transaction(
            id=None, account_id=account.id, amount=Decimal('-153.50'),
            description="Test", date=datetime.now().strftime('%Y-%m-%d'),
            category=category.name, type="expense"
        ))

        # Create splits with specific amounts
        split_repo.create_splits(transaction.id, [
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=0, category_id=category.id, amount=Decimal('73.25'),
                split_type='manual'
            ),
            TransactionSplit(
                id=None, transaction_id=transaction.id, group_id=group.id,
                split_order=1, category_id=category.id, amount=Decimal('80.25'),
                split_type='manual'
            )
        ])

        # Calculate total
        total = split_repo.get_total_amount_by_transaction(transaction.id)
        assert total == Decimal('153.50')

    def test_get_total_amount_zero(self, test_db):
        """Should return 0 for transaction with no splits."""
        split_repo = TransactionSplitRepository(test_db)
        total = split_repo.get_total_amount_by_transaction(99999)
        assert total == Decimal('0')
