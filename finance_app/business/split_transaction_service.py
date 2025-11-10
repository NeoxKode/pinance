"""
Business logic service for split transactions.

Story: US-002C - Split Transactions (Day 3)

This service handles creating and managing split transactions where a single
transaction is divided across multiple categories with proper balance validation.
"""
from decimal import Decimal
from typing import List, Tuple, Optional
from datetime import datetime

from finance_app.data.models import (
    TransactionSplit, SplitTransaction, PaycheckSplit, Transaction,
    TransactionGroup, JournalEntry, Category
)
from finance_app.data.database import Database
from finance_app.data.repositories.transaction_split_repository import TransactionSplitRepository
from finance_app.data.repositories.transaction_repository import TransactionRepository
from finance_app.data.repositories.transaction_group_repository import TransactionGroupRepository
from finance_app.data.repositories.category_repository import CategoryRepository
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.business.double_entry_service import DoubleEntryService
from finance_app.utils.logger import setup_logger
from finance_app.utils.exceptions import ValidationError, NotFoundError, DatabaseError

logger = setup_logger(__name__)


class SplitTransactionService:
    """
    Service for split transaction operations.

    Handles creation and management of split transactions with:
    - Balance validation (splits must equal transaction amount)
    - Integration with double-entry accounting
    - Template methods for common scenarios (paychecks, shopping)
    - Atomic operations for data integrity
    """

    def __init__(self, database: Database):
        """
        Initialize service.

        Args:
            database: Database instance
        """
        self.db = database
        self.split_repo = TransactionSplitRepository(database)
        self.transaction_repo = TransactionRepository(database)
        self.group_repo = TransactionGroupRepository(database)
        self.category_repo = CategoryRepository(database)
        self.account_repo = AccountRepository(database)
        self.double_entry_service = DoubleEntryService(database)

    def create_split_transaction(
        self,
        transaction_id: int,
        splits: List[TransactionSplit],
        create_journal_entries: bool = True
    ) -> Tuple[Transaction, List[TransactionSplit], Optional[TransactionGroup]]:
        """
        Create a split transaction with balance validation.

        This method:
        1. Validates that splits balance with transaction amount
        2. Creates splits atomically via repository
        3. Optionally creates journal entries for double-entry accounting
        4. Links all entries in a balanced transaction group

        Args:
            transaction_id: ID of transaction to split
            splits: List of TransactionSplit objects (minimum 2)
            create_journal_entries: Whether to create journal entries (default: True)

        Returns:
            Tuple of (Transaction, List[TransactionSplit], Optional[TransactionGroup])

        Raises:
            ValidationError: If splits don't balance or are invalid
            NotFoundError: If transaction or categories don't exist
            DatabaseError: If creation fails

        Example:
            # Split a $100 transaction into groceries ($70) and gas ($30)
            splits = [
                TransactionSplit(
                    id=None, transaction_id=1, group_id=1, split_order=0,
                    category_id=2, amount=Decimal('70.00'), memo="Groceries"
                ),
                TransactionSplit(
                    id=None, transaction_id=1, group_id=1, split_order=1,
                    category_id=3, amount=Decimal('30.00'), memo="Gas"
                )
            ]
            txn, splits, group = service.create_split_transaction(
                transaction_id=1,
                splits=splits
            )
        """
        # Get transaction
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction {transaction_id} not found")

        # Validate minimum splits
        if len(splits) < 2:
            raise ValidationError(
                f"Split transaction must have at least 2 splits, got {len(splits)}"
            )

        # Calculate total split amount
        total_splits = sum(split.amount for split in splits)
        transaction_amount = abs(transaction.amount)

        # Validate balance (within 1 cent tolerance)
        if abs(total_splits - transaction_amount) >= Decimal('0.01'):
            raise ValidationError(
                f"Split amounts must equal transaction amount. "
                f"Transaction: {transaction_amount}, Splits: {total_splits}, "
                f"Difference: {abs(total_splits - transaction_amount)}"
            )

        # US-008: Validate all accounts use same currency
        transaction_account = self.account_repo.get_by_id(transaction.account_id)
        if not transaction_account:
            raise NotFoundError(f"Transaction account {transaction.account_id} not found")

        transaction_currency = transaction_account.currency

        for i, split in enumerate(splits):
            category = self.category_repo.get_by_id(split.category_id)
            if not category:
                raise NotFoundError(f"Category {split.category_id} not found for split {i+1}")

            if not category.account_id:
                raise ValidationError(
                    f"Category '{category.name}' (ID={category.id}) does not have "
                    f"a linked account. Run category-account migration first."
                )

            split_account = self.account_repo.get_by_id(category.account_id)
            if not split_account:
                raise NotFoundError(
                    f"Account {category.account_id} linked to category '{category.name}' not found"
                )

            if split_account.currency != transaction_currency:
                raise ValidationError(
                    f"Cannot create split transaction with different currencies. "
                    f"Transaction account '{transaction_account.name}' uses {transaction_currency}, "
                    f"but split {i+1} category '{category.name}' is linked to account "
                    f"'{split_account.name}' which uses {split_account.currency}. "
                    f"All accounts in a split transaction must use the same currency."
                )

        logger.info(
            f"Creating split transaction for txn {transaction_id} "
            f"with {len(splits)} splits totaling {total_splits}"
        )

        # Create or get transaction group (always needed for splits)
        # Check if splits already have a group_id
        if splits[0].group_id is not None:
            group = self.group_repo.get_by_id(splits[0].group_id)
        else:
            # Create new group
            group = TransactionGroup(
                id=None,
                group_date=transaction.date,
                description=f"Split: {transaction.description}",
                total_debits=Decimal('0'),
                total_credits=Decimal('0'),
                is_balanced=False
            )
            group = self.group_repo.create(group)

            # Update splits with group_id
            for split in splits:
                split.group_id = group.id

        # Create splits atomically
        created_splits = self.split_repo.create_splits(transaction_id, splits)

        # Create journal entries if requested
        if create_journal_entries and group:
            journal_entries = self._create_journal_entries_for_splits(
                transaction, created_splits, group
            )
            logger.info(
                f"Created {len(journal_entries)} journal entries for split transaction"
            )

        # Refresh transaction to get updated is_split and split_count
        updated_transaction = self.transaction_repo.get_by_id(transaction_id)

        logger.info(
            f"Split transaction created successfully: "
            f"txn={transaction_id}, splits={len(created_splits)}, "
            f"group={group.id if group else None}"
        )

        return updated_transaction, created_splits, group

    def create_paycheck_split(
        self,
        account_id: int,
        date: str,
        description: str,
        paycheck: PaycheckSplit,
        category_mapping: dict,
        create_journal_entries: bool = True
    ) -> Tuple[Transaction, List[TransactionSplit], Optional[TransactionGroup]]:
        """
        Create a paycheck split transaction from template.

        This is a convenience method for the common paycheck scenario where
        gross pay is split into various deductions and net pay.

        Args:
            account_id: Account to credit with net pay (e.g., checking account)
            date: Transaction date (YYYY-MM-DD)
            description: Transaction description
            paycheck: PaycheckSplit template with all amounts
            category_mapping: Dict mapping deduction types to category IDs
                Expected keys: 'gross_pay', 'federal_tax', 'state_tax',
                              'social_security', 'medicare', 'retirement_401k',
                              'health_insurance', 'other_deductions'
            create_journal_entries: Whether to create journal entries

        Returns:
            Tuple of (Transaction, List[TransactionSplit], Optional[TransactionGroup])

        Raises:
            ValidationError: If paycheck template is invalid or categories missing
            NotFoundError: If account or categories don't exist

        Example:
            paycheck = PaycheckSplit(
                gross_pay=Decimal('5000.00'),
                federal_tax=Decimal('750.00'),
                state_tax=Decimal('250.00'),
                social_security=Decimal('310.00'),
                medicare=Decimal('72.50'),
                retirement_401k=Decimal('500.00'),
                health_insurance=Decimal('200.00')
            )

            category_mapping = {
                'gross_pay': 1,     # Income category
                'federal_tax': 2,   # Tax expense
                'state_tax': 3,     # Tax expense
                # ... etc
            }

            txn, splits, group = service.create_paycheck_split(
                account_id=1,
                date='2025-10-23',
                description='October paycheck',
                paycheck=paycheck,
                category_mapping=category_mapping
            )
        """
        # Validate paycheck
        if not paycheck.is_valid:
            raise ValidationError(
                f"Invalid paycheck: gross_pay ({paycheck.gross_pay}) != "
                f"net_pay ({paycheck.net_pay}) + deductions ({paycheck.total_deductions})"
            )

        # Validate category mapping
        required_keys = [
            'gross_pay', 'federal_tax', 'state_tax',
            'social_security', 'medicare', 'retirement_401k', 'health_insurance'
        ]
        for key in required_keys:
            if key not in category_mapping:
                raise ValidationError(f"Missing category mapping for: {key}")

        logger.info(
            f"Creating paycheck split: gross=${paycheck.gross_pay}, "
            f"net=${paycheck.net_pay}, deductions=${paycheck.total_deductions}"
        )

        # Create main transaction for net pay
        transaction = Transaction(
            id=None,
            account_id=account_id,
            date=date,
            description=description,
            category='Income',  # Will be overridden by splits
            amount=paycheck.net_pay,  # Net amount credited to account
            type='income'
        )
        transaction = self.transaction_repo.create(transaction)

        # Create transaction group (always needed for splits)
        group = TransactionGroup(
            id=None,
            group_date=date,
            description=f"Paycheck: {description}",
            total_debits=Decimal('0'),
            total_credits=Decimal('0'),
            is_balanced=False
        )
        group = self.group_repo.create(group)

        # Build splits list
        splits = []
        split_order = 0

        # Gross pay (income)
        splits.append(TransactionSplit(
            id=None,
            transaction_id=transaction.id,
            group_id=group.id,
            split_order=split_order,
            category_id=category_mapping['gross_pay'],
            amount=paycheck.gross_pay,
            memo="Gross pay",
            split_type='paycheck'
        ))
        split_order += 1

        # Deductions
        deduction_splits = [
            ('federal_tax', paycheck.federal_tax, "Federal tax"),
            ('state_tax', paycheck.state_tax, "State tax"),
            ('social_security', paycheck.social_security, "Social Security"),
            ('medicare', paycheck.medicare, "Medicare"),
            ('retirement_401k', paycheck.retirement_401k, "401(k)"),
            ('health_insurance', paycheck.health_insurance, "Health insurance"),
        ]

        for key, amount, memo in deduction_splits:
            if amount > 0:
                splits.append(TransactionSplit(
                    id=None,
                    transaction_id=transaction.id,
                    group_id=group.id,
                    split_order=split_order,
                    category_id=category_mapping[key],
                    amount=amount,
                    memo=memo,
                    split_type='paycheck'
                ))
                split_order += 1

        # Other deductions
        if paycheck.other_deductions:
            if 'other_deductions' not in category_mapping:
                raise ValidationError("Missing category mapping for: other_deductions")

            for i, (name, amount) in enumerate(paycheck.other_deductions):
                splits.append(TransactionSplit(
                    id=None,
                    transaction_id=transaction.id,
                    group_id=group.id,
                    split_order=split_order,
                    category_id=category_mapping['other_deductions'],
                    amount=amount,
                    memo=f"Other: {name}",
                    split_type='paycheck'
                ))
                split_order += 1

        # Create splits (this will validate balance)
        created_splits = self.split_repo.create_splits(transaction.id, splits)

        # Create journal entries if requested
        if create_journal_entries and group:
            journal_entries = self._create_journal_entries_for_splits(
                transaction, created_splits, group
            )
            logger.info(
                f"Created {len(journal_entries)} journal entries for paycheck split"
            )

        # Refresh transaction to get updated is_split and split_count
        updated_transaction = self.transaction_repo.get_by_id(transaction.id)

        logger.info(
            f"Paycheck split created: txn={transaction.id}, "
            f"splits={len(created_splits)}, effective_rate={paycheck.effective_tax_rate:.2f}%"
        )

        return updated_transaction, created_splits, group

    def update_split_transaction(
        self,
        transaction_id: int,
        splits: List[TransactionSplit]
    ) -> Tuple[Transaction, List[TransactionSplit]]:
        """
        Update splits for an existing split transaction.

        This method:
        1. Validates new splits balance with transaction
        2. Deletes old splits
        3. Creates new splits atomically
        4. Updates journal entries if they exist

        Args:
            transaction_id: Transaction ID
            splits: New list of splits

        Returns:
            Tuple of (Transaction, List[TransactionSplit])

        Raises:
            ValidationError: If splits don't balance
            NotFoundError: If transaction doesn't exist
        """
        # Get transaction
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction {transaction_id} not found")

        # Validate balance
        total_splits = sum(split.amount for split in splits)
        transaction_amount = abs(transaction.amount)

        if abs(total_splits - transaction_amount) >= Decimal('0.01'):
            raise ValidationError(
                f"Split amounts must equal transaction amount. "
                f"Transaction: {transaction_amount}, Splits: {total_splits}"
            )

        logger.info(f"Updating splits for transaction {transaction_id}")

        # Delete old splits
        deleted_count = self.split_repo.delete_all_for_transaction(transaction_id)
        logger.info(f"Deleted {deleted_count} old splits")

        # Create or get transaction group (always needed for splits)
        # Check if splits already have a group_id
        if splits[0].group_id is not None:
            group = self.group_repo.get_by_id(splits[0].group_id)
        else:
            # Create new group
            group = TransactionGroup(
                id=None,
                group_date=transaction.date,
                description=f"Split: {transaction.description}",
                total_debits=Decimal('0'),
                total_credits=Decimal('0'),
                is_balanced=False
            )
            group = self.group_repo.create(group)

            # Update splits with group_id
            for split in splits:
                split.group_id = group.id

        # Create new splits
        created_splits = self.split_repo.create_splits(transaction_id, splits)

        # Refresh transaction
        updated_transaction = self.transaction_repo.get_by_id(transaction_id)

        logger.info(
            f"Splits updated: txn={transaction_id}, "
            f"old_count={deleted_count}, new_count={len(created_splits)}"
        )

        return updated_transaction, created_splits

    def delete_split_transaction(
        self,
        transaction_id: int,
        delete_journal_entries: bool = True
    ) -> int:
        """
        Delete all splits for a transaction.

        Args:
            transaction_id: Transaction ID
            delete_journal_entries: Whether to delete associated journal entries

        Returns:
            Number of splits deleted

        Raises:
            NotFoundError: If transaction doesn't exist
        """
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction {transaction_id} not found")

        if not transaction.is_split:
            logger.warning(f"Transaction {transaction_id} is not a split transaction")
            return 0

        logger.info(f"Deleting split transaction {transaction_id}")

        # Delete splits (this updates transaction flags automatically)
        deleted_count = self.split_repo.delete_all_for_transaction(transaction_id)

        # TODO: Delete journal entries if requested
        # This would require getting the group_id from splits before deletion

        logger.info(f"Deleted {deleted_count} splits from transaction {transaction_id}")

        return deleted_count

    def get_split_transaction(
        self,
        transaction_id: int
    ) -> Optional[SplitTransaction]:
        """
        Get a complete split transaction with validation.

        Args:
            transaction_id: Transaction ID

        Returns:
            SplitTransaction object or None if not found

        Raises:
            NotFoundError: If transaction doesn't exist
        """
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction {transaction_id} not found")

        if not transaction.is_split:
            return None

        splits = self.split_repo.get_by_transaction(transaction_id)
        if not splits:
            return None

        return SplitTransaction(transaction=transaction, splits=splits)

    def _create_journal_entries_for_splits(
        self,
        transaction: Transaction,
        splits: List[TransactionSplit],
        group: TransactionGroup
    ) -> List[JournalEntry]:
        """
        Create journal entries for split transaction.

        For each split, creates a journal entry posting to the category's
        linked account.

        Args:
            transaction: The transaction
            splits: List of splits
            group: Transaction group

        Returns:
            List of created journal entries

        Raises:
            ValidationError: If categories don't have linked accounts
        """
        journal_entries = []

        for split in splits:
            # Get category to find linked account
            category = self.category_repo.get_by_id(split.category_id)
            if not category:
                raise NotFoundError(f"Category {split.category_id} not found")

            if not category.account_id:
                raise ValidationError(
                    f"Category '{category.name}' (ID={category.id}) does not have "
                    f"a linked account. Run category-account migration first."
                )

            # Create journal entry for this split
            # Amount sign: expense/asset increases are debits (positive)
            #             income/liability increases are credits (negative)
            entry_amount = split.amount
            if category.type == 'income':
                entry_amount = -split.amount  # Income is a credit

            entry = self.double_entry_service.create_simple_transaction(
                account_id=category.account_id,
                amount=entry_amount,
                date=transaction.date,
                description=f"{transaction.description} - {split.memo or category.name}",
                transaction_id=transaction.id,
                notes=f"Split {split.split_order + 1} of {len(splits)}"
            )

            journal_entries.append(entry)

        return journal_entries
