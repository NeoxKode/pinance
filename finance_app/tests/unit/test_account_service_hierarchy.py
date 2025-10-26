"""
Unit tests for AccountService hierarchy methods.

Story: US-006 - Account Hierarchy (Parent/Child Accounts)

Test Coverage:
- create_account() with hierarchy parameters (6 tests)
- get_parent_account_balance() method (3 tests)
- get_parent_account_balance_sql() method (3 tests)
- _would_create_cycle() method (4 tests)
- move_account() method (6 tests)
- convert_to_parent_account() method (4 tests)
- delete_account_with_children() method (5 tests)

Total: 31 tests (exceeds 20+ target)
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch, call
from typing import Optional

from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance, Transaction
)
from finance_app.business.account_service import AccountService
from finance_app.data.database import Database
from finance_app.utils.exceptions import ValidationError, NotFoundError


class TestCreateAccountWithHierarchy:
    """Test create_account() with hierarchy parameters."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return AccountService(mock_db)

    def test_create_child_account_with_valid_parent(self, service):
        """Test creating child account with valid parent."""
        # Mock parent account
        parent_account = Account(
            id=1,
            name="Test Bank Accounts",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            is_parent=True,
            hierarchy_level=0,
            hierarchy_path="/1"
        )

        # Mock created child account
        child_account = Account(
            id=2,
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT,
            parent_account_id=1,
            is_parent=False,
            hierarchy_level=1,
            hierarchy_path="/1/2"
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=parent_account), \
             patch.object(service, '_would_create_cycle', return_value=False), \
             patch.object(service.account_repo, 'create', return_value=child_account):

            result = service.create_account(
                name="Checking Account",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                initial_balance="1000.00",
                parent_account_id=1
            )

            assert result.name == "Checking Account"
            assert result.parent_account_id == 1
            assert result.hierarchy_level == 1

    def test_create_parent_account_is_parent_true(self, service):
        """Test creating parent account with is_parent=True."""
        parent_account = Account(
            id=1,
            name="Test Bank Accounts",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            is_parent=True,
            hierarchy_level=0,
            hierarchy_path="/1"
        )

        with patch.object(service.account_repo, 'create', return_value=parent_account):
            result = service.create_account(
                name="Test Bank Accounts",
                account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING,
                initial_balance="0.00",
                is_parent=True
            )

            assert result.is_parent is True
            assert result.balance == Decimal("0.00")

    def test_raises_error_if_parent_does_not_exist(self, service):
        """Test that NotFoundError is raised if parent account doesn't exist."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Parent account with ID 999 not found"):
                service.create_account(
                    name="Checking Account",
                    account_type=AccountType.ASSET,
                    account_subtype=AccountSubtype.CHECKING,
                    initial_balance="0.00",
                    parent_account_id=999
                )

    def test_raises_error_if_parent_is_not_parent_account(self, service):
        """Test that ValidationError is raised if parent is not a parent account."""
        # Mock non-parent account
        non_parent_account = Account(
            id=1,
            name="Regular Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT,
            is_parent=False
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=non_parent_account):
            with pytest.raises(ValidationError, match="is not a parent account"):
                service.create_account(
                    name="Child Account",
                    account_type=AccountType.ASSET,
                    account_subtype=AccountSubtype.CHECKING,
                    initial_balance="0.00",
                    parent_account_id=1
                )

    def test_raises_error_if_type_mismatch_with_parent(self, service):
        """Test that ValidationError is raised if child type doesn't match parent."""
        # Mock parent account (ASSET type)
        parent_account = Account(
            id=1,
            name="Test Bank Accounts",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            is_parent=True,
            hierarchy_level=0
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=parent_account):
            with pytest.raises(ValidationError, match="must match parent account type"):
                service.create_account(
                    name="Credit Card",
                    account_type=AccountType.LIABILITY,  # Mismatch!
                    account_subtype=AccountSubtype.CREDIT_CARD,
                    initial_balance="0.00",
                    parent_account_id=1
                )

    def test_raises_error_if_maximum_depth_exceeded(self, service):
        """Test that ValidationError is raised if maximum depth (5 levels) exceeded."""
        # Mock parent at level 4 (maximum)
        deep_parent = Account(
            id=5,
            name="Level 4 Parent",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            is_parent=True,
            hierarchy_level=4  # At maximum depth
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=deep_parent):
            with pytest.raises(ValidationError, match="Maximum hierarchy depth is 5 levels"):
                service.create_account(
                    name="Too Deep",
                    account_type=AccountType.ASSET,
                    account_subtype=AccountSubtype.CHECKING,
                    initial_balance="0.00",
                    parent_account_id=5
                )


class TestGetParentAccountBalance:
    """Test get_parent_account_balance() method (Python version)."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return AccountService(mock_db)

    def test_calculates_balance_from_leaf_descendants(self, service):
        """Test that balance is calculated from leaf (non-parent) descendants only."""
        parent = Account(
            id=1,
            name="Bank Accounts",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            is_parent=True
        )

        # Child 1: Leaf account with balance
        child1 = Account(
            id=2,
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("1000.00"),
            normal_balance=NormalBalance.DEBIT,
            is_parent=False,
            parent_account_id=1
        )

        # Child 2: Leaf account with balance
        child2 = Account(
            id=3,
            name="Savings",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            balance=Decimal("5000.00"),
            normal_balance=NormalBalance.DEBIT,
            is_parent=False,
            parent_account_id=1
        )

        # Child 3: Parent account (should be ignored)
        child3 = Account(
            id=4,
            name="Sub Category",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            is_parent=True,
            parent_account_id=1
        )

        descendants = [child1, child2, child3]

        with patch.object(service.account_repo, 'get_by_id', return_value=parent), \
             patch.object(service.account_repo, 'get_descendant_accounts', return_value=descendants):

            balance = service.get_parent_account_balance(1)

            # Should only sum child1 (1000) + child2 (5000) = 6000
            # child3 is parent, so excluded
            assert balance == Decimal("6000.00")

    def test_returns_zero_if_no_leaf_descendants(self, service):
        """Test that zero is returned if parent has no leaf descendants."""
        parent = Account(
            id=1,
            name="Bank Accounts",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            is_parent=True
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=parent), \
             patch.object(service.account_repo, 'get_descendant_accounts', return_value=[]):

            balance = service.get_parent_account_balance(1)

            assert balance == Decimal("0.00")

    def test_raises_not_found_error_if_parent_not_exists(self, service):
        """Test that NotFoundError is raised if parent account doesn't exist."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Parent account with ID 999 not found"):
                service.get_parent_account_balance(999)


class TestGetParentAccountBalanceSQL:
    """Test get_parent_account_balance_sql() method (optimized SQL version)."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database with connection support."""
        mock = Mock(spec=Database)
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock.get_connection.return_value.__exit__ = Mock(return_value=False)
        return mock, mock_cursor

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        db, _ = mock_db
        return AccountService(db)

    def test_calculates_balance_using_sql_aggregation(self, service, mock_db):
        """Test that balance is calculated using SQL SUM aggregation."""
        _, mock_cursor = mock_db

        parent = Account(
            id=1,
            name="Bank Accounts",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            is_parent=True,
            hierarchy_path="/1"
        )

        # Mock SQL result: total of all leaf descendants
        mock_cursor.fetchone.return_value = (6000.00,)

        with patch.object(service.account_repo, 'get_by_id', return_value=parent):
            balance = service.get_parent_account_balance_sql(1)

            assert balance == Decimal("6000.00")

            # Verify SQL query used pattern matching and is_parent = 0 filter
            executed_query = mock_cursor.execute.call_args[0][0]
            assert 'SUM(balance)' in executed_query
            assert 'hierarchy_path LIKE ?' in executed_query
            assert 'is_parent = 0' in executed_query

    def test_returns_zero_if_no_leaf_descendants_sql(self, service, mock_db):
        """Test that zero is returned if SQL query returns NULL."""
        _, mock_cursor = mock_db

        parent = Account(
            id=1,
            name="Empty Parent",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            balance=Decimal("0.00"),
            normal_balance=NormalBalance.DEBIT,
            is_parent=True,
            hierarchy_path="/1"
        )

        # Mock SQL result: NULL (no descendants)
        mock_cursor.fetchone.return_value = (None,)

        with patch.object(service.account_repo, 'get_by_id', return_value=parent):
            balance = service.get_parent_account_balance_sql(1)

            assert balance == Decimal("0.00")

    def test_raises_not_found_error_if_parent_not_exists_sql(self, service, mock_db):
        """Test that NotFoundError is raised if parent account doesn't exist."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Parent account with ID 999 not found"):
                service.get_parent_account_balance_sql(999)


class TestWouldCreateCycle:
    """Test _would_create_cycle() method for circular reference detection."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return AccountService(mock_db)

    def test_detects_direct_cycle(self, service):
        """Test detection of direct cycle (A -> B, then B -> A)."""
        # Account 2 currently has parent=None
        # Account 1 currently has parent=2
        # Trying to make 2's parent = 1 would create cycle: 1 -> 2 -> 1

        account1 = Account(
            id=1, name="A", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
            normal_balance=NormalBalance.DEBIT, parent_account_id=None
        )

        account2 = Account(
            id=2, name="B", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
            normal_balance=NormalBalance.DEBIT, parent_account_id=1  # 2 -> 1
        )

        # Mock: First call gets account1 (new_parent), second call gets account2 (parent of account1)
        def get_by_id_side_effect(account_id):
            if account_id == 1:
                return account1
            elif account_id == 2:
                return account2
            return None

        with patch.object(service.account_repo, 'get_by_id', side_effect=get_by_id_side_effect):
            # Try to move account 1 to have parent 2: would create 1->2->1 (via 2's parent being 1)
            result = service._would_create_cycle(account_id=1, new_parent_id=2)

            assert result is True

    def test_detects_indirect_cycle(self, service):
        """Test detection of indirect cycle (A -> B -> C -> A)."""
        # Current chain: 1 -> 2, 2 -> 3, 3 -> None
        # Trying to make 3 -> parent 1 would create: 1 -> 2 -> 3 -> 1
        account1 = Account(id=1, name="A", account_type=AccountType.ASSET,
                          account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
                          normal_balance=NormalBalance.DEBIT, parent_account_id=2)
        account2 = Account(id=2, name="B", account_type=AccountType.ASSET,
                          account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
                          normal_balance=NormalBalance.DEBIT, parent_account_id=3)
        account3 = Account(id=3, name="C", account_type=AccountType.ASSET,
                          account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
                          normal_balance=NormalBalance.DEBIT, parent_account_id=None)

        def get_by_id_side_effect(account_id):
            accounts = {1: account1, 2: account2, 3: account3}
            return accounts.get(account_id)

        # Trying to make 3 -> parent 1 would create cycle
        # Walk: start at 1 (new_parent) -> parent is 2 -> parent is 3 -> that's the account we're moving! Cycle!
        with patch.object(service.account_repo, 'get_by_id', side_effect=get_by_id_side_effect):
            result = service._would_create_cycle(account_id=3, new_parent_id=1)

            assert result is True

    def test_no_cycle_with_valid_parent(self, service):
        """Test that no cycle is detected for valid parent chain."""
        # Chain: 2 -> 1 -> None
        account1 = Account(id=1, name="A", account_type=AccountType.ASSET,
                          account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
                          normal_balance=NormalBalance.DEBIT, parent_account_id=None)
        account2 = Account(id=2, name="B", account_type=AccountType.ASSET,
                          account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
                          normal_balance=NormalBalance.DEBIT, parent_account_id=1)

        # Account 3 setting parent to 2 is valid: 3 -> 2 -> 1 -> None
        with patch.object(service.account_repo, 'get_by_id', side_effect=[account2, account1]):
            result = service._would_create_cycle(account_id=3, new_parent_id=2)

            assert result is False

    def test_account_cannot_be_own_parent(self, service):
        """Test that account cannot be its own parent."""
        result = service._would_create_cycle(account_id=1, new_parent_id=1)

        assert result is True


class TestMoveAccount:
    """Test move_account() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return AccountService(mock_db)

    def test_move_account_to_new_parent(self, service):
        """Test moving account to a new parent."""
        # Account to move
        account = Account(
            id=3, name="Child", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
            normal_balance=NormalBalance.DEBIT, parent_account_id=None
        )

        # New parent
        new_parent = Account(
            id=1, name="Parent", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
            normal_balance=NormalBalance.DEBIT, is_parent=True, hierarchy_level=0
        )

        # Updated account after move
        updated_account = Account(
            id=3, name="Child", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
            normal_balance=NormalBalance.DEBIT, parent_account_id=1, hierarchy_level=1
        )

        with patch.object(service.account_repo, 'get_by_id', side_effect=[account, new_parent]), \
             patch.object(service, '_would_create_cycle', return_value=False), \
             patch.object(service.account_repo, 'update', return_value=updated_account):

            result = service.move_account(account_id=3, new_parent_id=1)

            assert result.parent_account_id == 1
            assert result.hierarchy_level == 1

    def test_move_account_to_top_level(self, service):
        """Test moving account to top-level (parent_id = None)."""
        # Account currently under a parent
        account = Account(
            id=3, name="Child", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
            normal_balance=NormalBalance.DEBIT, parent_account_id=1, hierarchy_level=1
        )

        # Updated account after move to top-level
        updated_account = Account(
            id=3, name="Child", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
            normal_balance=NormalBalance.DEBIT, parent_account_id=None, hierarchy_level=0
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=account), \
             patch.object(service.account_repo, 'update', return_value=updated_account):

            result = service.move_account(account_id=3, new_parent_id=None)

            assert result.parent_account_id is None
            assert result.hierarchy_level == 0

    def test_raises_error_if_account_not_found(self, service):
        """Test that NotFoundError is raised if account doesn't exist."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Account with ID 999 not found"):
                service.move_account(account_id=999, new_parent_id=1)

    def test_raises_error_if_new_parent_not_parent_account(self, service):
        """Test that ValidationError is raised if new parent is not a parent account."""
        account = Account(
            id=3, name="Child", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
            normal_balance=NormalBalance.DEBIT
        )

        # Not a parent account
        non_parent = Account(
            id=1, name="Regular", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("500"),
            normal_balance=NormalBalance.DEBIT, is_parent=False
        )

        with patch.object(service.account_repo, 'get_by_id', side_effect=[account, non_parent]):
            with pytest.raises(ValidationError, match="is not a parent account"):
                service.move_account(account_id=3, new_parent_id=1)

    def test_raises_error_if_circular_reference(self, service):
        """Test that ValidationError is raised if move would create circular reference."""
        account = Account(
            id=3, name="Child", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
            normal_balance=NormalBalance.DEBIT
        )

        new_parent = Account(
            id=1, name="Parent", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
            normal_balance=NormalBalance.DEBIT, is_parent=True, hierarchy_level=0
        )

        with patch.object(service.account_repo, 'get_by_id', side_effect=[account, new_parent]), \
             patch.object(service, '_would_create_cycle', return_value=True):

            with pytest.raises(ValidationError, match="would create circular reference"):
                service.move_account(account_id=3, new_parent_id=1)

    def test_raises_error_if_type_mismatch(self, service):
        """Test that ValidationError is raised if account type doesn't match parent."""
        account = Account(
            id=3, name="Asset Account", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
            normal_balance=NormalBalance.DEBIT
        )

        # Different type parent
        liability_parent = Account(
            id=1, name="Liability Parent", account_type=AccountType.LIABILITY,
            account_subtype=AccountSubtype.CREDIT_CARD, balance=Decimal("0"),
            normal_balance=NormalBalance.CREDIT, is_parent=True, hierarchy_level=0
        )

        with patch.object(service.account_repo, 'get_by_id', side_effect=[account, liability_parent]):
            with pytest.raises(ValidationError, match="type mismatch"):
                service.move_account(account_id=3, new_parent_id=1)


class TestConvertToParentAccount:
    """Test convert_to_parent_account() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return AccountService(mock_db)

    def test_converts_account_to_parent(self, service):
        """Test successful conversion of account to parent."""
        account = Account(
            id=1, name="Regular Account", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
            normal_balance=NormalBalance.DEBIT, is_parent=False
        )

        parent_account = Account(
            id=1, name="Regular Account", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
            normal_balance=NormalBalance.DEBIT, is_parent=True
        )

        # Mock get_all method with account_id parameter
        with patch.object(service.account_repo, 'get_by_id', return_value=account), \
             patch.object(service.transaction_repo, 'get_all', return_value=[]) as mock_get_all, \
             patch.object(service.account_repo, 'update', return_value=parent_account):

            result = service.convert_to_parent_account(account_id=1)

            assert result.is_parent is True
            mock_get_all.assert_called_once_with(account_id=1)

    def test_raises_error_if_account_not_found(self, service):
        """Test that NotFoundError is raised if account doesn't exist."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Account with ID 999 not found"):
                service.convert_to_parent_account(account_id=999)

    def test_raises_error_if_account_has_transactions(self, service):
        """Test that ValidationError is raised if account has transactions."""
        account = Account(
            id=1, name="Account With Transactions", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
            normal_balance=NormalBalance.DEBIT, is_parent=False
        )

        # Mock transactions with correct Transaction model signature
        transactions = [
            Transaction(
                id=1, account_id=1, date="2025-01-01", description="Transaction 1",
                category="Groceries", amount=Decimal("1000"), type="income"
            ),
            Transaction(
                id=2, account_id=1, date="2025-01-02", description="Transaction 2",
                category="Entertainment", amount=Decimal("-500"), type="expense"
            )
        ]

        # Mock get_all method with account_id parameter
        with patch.object(service.account_repo, 'get_by_id', return_value=account), \
             patch.object(service.transaction_repo, 'get_all', return_value=transactions):
            with pytest.raises(ValidationError, match="has 2 transactions"):
                service.convert_to_parent_account(account_id=1)

    def test_returns_same_account_if_already_parent(self, service):
        """Test that account is returned unchanged if already a parent."""
        parent_account = Account(
            id=1, name="Already Parent", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
            normal_balance=NormalBalance.DEBIT, is_parent=True
        )

        # Create mock for update method
        mock_update = Mock()

        with patch.object(service.account_repo, 'get_by_id', return_value=parent_account), \
             patch.object(service.account_repo, 'update', mock_update):
            result = service.convert_to_parent_account(account_id=1)

            assert result.is_parent is True
            # Verify update was NOT called since account already parent
            mock_update.assert_not_called()


class TestDeleteAccountWithChildren:
    """Test delete_account_with_children() method."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock database."""
        return AccountService(mock_db)

    def test_prevents_delete_when_has_children_without_force(self, service):
        """Test that delete is prevented when account has children (force=False)."""
        parent = Account(
            id=1, name="Parent", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
            normal_balance=NormalBalance.DEBIT, is_parent=True
        )

        child = Account(
            id=2, name="Child", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
            normal_balance=NormalBalance.DEBIT, parent_account_id=1
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=parent), \
             patch.object(service.account_repo, 'get_child_accounts', return_value=[child]):

            with pytest.raises(ValidationError, match="has 1 child accounts"):
                service.delete_account_with_children(account_id=1, force=False)

    def test_cascade_delete_with_force_true(self, service):
        """Test that cascade delete works when force=True."""
        parent = Account(
            id=1, name="Parent", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
            normal_balance=NormalBalance.DEBIT, is_parent=True
        )

        child1 = Account(
            id=2, name="Child 1", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
            normal_balance=NormalBalance.DEBIT, parent_account_id=1
        )

        child2 = Account(
            id=3, name="Child 2", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS, balance=Decimal("5000"),
            normal_balance=NormalBalance.DEBIT, parent_account_id=1
        )

        # Setup mock calls
        call_count = [0]

        def get_by_id_side_effect(account_id):
            if account_id == 1:
                return parent
            elif account_id == 2:
                return child1
            elif account_id == 3:
                return child2
            return None

        def get_child_accounts_side_effect(account_id):
            if account_id == 1 and call_count[0] == 0:
                call_count[0] += 1
                return [child1, child2]
            return []

        with patch.object(service.account_repo, 'get_by_id', side_effect=get_by_id_side_effect), \
             patch.object(service.account_repo, 'get_child_accounts', side_effect=get_child_accounts_side_effect), \
             patch.object(service.account_repo, 'delete', return_value=True):

            result = service.delete_account_with_children(account_id=1, force=True)

            assert result is True
            # Verify delete was called 3 times (2 children + 1 parent)
            assert service.account_repo.delete.call_count == 3

    def test_deletes_account_without_children(self, service):
        """Test that account without children is deleted normally."""
        account = Account(
            id=1, name="Leaf Account", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
            normal_balance=NormalBalance.DEBIT, is_parent=False
        )

        with patch.object(service.account_repo, 'get_by_id', return_value=account), \
             patch.object(service.account_repo, 'get_child_accounts', return_value=[]), \
             patch.object(service.account_repo, 'delete', return_value=True):

            result = service.delete_account_with_children(account_id=1, force=False)

            assert result is True
            service.account_repo.delete.assert_called_once_with(1)

    def test_raises_error_if_account_not_found(self, service):
        """Test that NotFoundError is raised if account doesn't exist."""
        with patch.object(service.account_repo, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError, match="Account with ID 999 not found"):
                service.delete_account_with_children(account_id=999, force=False)

    def test_recursive_deletion_of_nested_hierarchy(self, service):
        """Test recursive deletion of deeply nested hierarchy."""
        # Level 0
        grandparent = Account(id=1, name="Grandparent", account_type=AccountType.ASSET,
                             account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
                             normal_balance=NormalBalance.DEBIT, is_parent=True)

        # Level 1
        parent = Account(id=2, name="Parent", account_type=AccountType.ASSET,
                        account_subtype=AccountSubtype.CHECKING, balance=Decimal("0"),
                        normal_balance=NormalBalance.DEBIT, is_parent=True, parent_account_id=1)

        # Level 2
        child = Account(id=3, name="Child", account_type=AccountType.ASSET,
                       account_subtype=AccountSubtype.CHECKING, balance=Decimal("1000"),
                       normal_balance=NormalBalance.DEBIT, is_parent=False, parent_account_id=2)

        call_tracker = {'get_children_calls': 0}

        def get_by_id_side_effect(account_id):
            accounts = {1: grandparent, 2: parent, 3: child}
            return accounts.get(account_id)

        def get_child_accounts_side_effect(account_id):
            call_tracker['get_children_calls'] += 1
            if account_id == 1 and call_tracker['get_children_calls'] == 1:
                return [parent]
            elif account_id == 2 and call_tracker['get_children_calls'] == 2:
                return [child]
            return []

        with patch.object(service.account_repo, 'get_by_id', side_effect=get_by_id_side_effect), \
             patch.object(service.account_repo, 'get_child_accounts', side_effect=get_child_accounts_side_effect), \
             patch.object(service.account_repo, 'delete', return_value=True):

            result = service.delete_account_with_children(account_id=1, force=True)

            assert result is True
            # Should delete: grandparent, parent, child (3 total)
            assert service.account_repo.delete.call_count == 3
