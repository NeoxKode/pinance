"""
Integration tests for Account Hierarchy workflow.

Story: US-006 - Account Hierarchy (Parent/Child Accounts)

Test Coverage:
- Create parent account and add children (2 tests)
- Move account between parents (2 tests)
- Calculate parent balance with multiple levels (2 tests)
- Delete parent cascade (2 tests)
- Convert account to parent (1 test)
- Validate hierarchy constraints (2 tests)
- Test hierarchy path updates (2 tests)
- Test nested parent accounts (2 tests)

Total: 15 integration tests
"""
import pytest
from decimal import Decimal

from finance_app.data.database import Database
from finance_app.data.models import (
    Account, AccountType, AccountSubtype, NormalBalance
)
from finance_app.business.account_service import AccountService
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.utils.exceptions import ValidationError, NotFoundError


class TestCreateParentAndChildren:
    """Integration tests for creating parent accounts and adding children."""

    def test_create_parent_account_and_add_children(self, test_db):
        """Test creating parent account and adding child accounts."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create parent account
        parent = service.create_account(
            name="Bank Accounts",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="0.00",
            is_parent=True
        )

        assert parent.is_parent is True
        assert parent.hierarchy_level == 0
        assert parent.hierarchy_path == f"/{parent.id}"

        # Add child account
        child1 = service.create_account(
            name="Checking Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="1000.00",
            parent_account_id=parent.id
        )

        # Verify child account
        assert child1.parent_account_id == parent.id
        assert child1.hierarchy_level == 1
        assert child1.hierarchy_path == f"/{parent.id}/{child1.id}"

        # Add second child
        child2 = service.create_account(
            name="Savings Account",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS,
            initial_balance="5000.00",
            parent_account_id=parent.id
        )

        # Verify second child
        assert child2.parent_account_id == parent.id
        assert child2.hierarchy_level == 1

        # Verify repository methods
        children = account_repo.get_child_accounts(parent.id)
        assert len(children) == 2
        assert any(c.id == child1.id for c in children)
        assert any(c.id == child2.id for c in children)

    def test_create_nested_parent_hierarchy(self, test_db):
        """Test creating nested parent hierarchy (parent -> parent -> child)."""
        service = AccountService(test_db)

        # Level 0: Top parent
        level0 = service.create_account(
            name="Assets",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="0.00",
            is_parent=True
        )

        # Level 1: Nested parent
        level1 = service.create_account(
            name="Bank Accounts",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="0.00",
            parent_account_id=level0.id,
            is_parent=True
        )

        assert level1.hierarchy_level == 1
        assert level1.parent_account_id == level0.id

        # Level 2: Leaf account
        level2 = service.create_account(
            name="Checking",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING,
            initial_balance="2000.00",
            parent_account_id=level1.id
        )

        assert level2.hierarchy_level == 2
        assert level2.hierarchy_path == f"/{level0.id}/{level1.id}/{level2.id}"


class TestMoveAccountBetweenParents:
    """Integration tests for moving accounts between parents."""

    def test_move_account_to_different_parent(self, test_db):
        """Test moving account from one parent to another."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create two parent accounts
        parent1 = service.create_account(
            name="Bank A", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        parent2 = service.create_account(
            name="Bank B", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        # Create child under parent1
        child = service.create_account(
            name="Checking", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="1000.00",
            parent_account_id=parent1.id
        )

        assert child.parent_account_id == parent1.id

        # Move child to parent2
        moved_child = service.move_account(child.id, parent2.id)

        assert moved_child.parent_account_id == parent2.id
        assert moved_child.hierarchy_path.startswith(f"/{parent2.id}/")

        # Verify parent1 has no children
        parent1_children = account_repo.get_child_accounts(parent1.id)
        assert len(parent1_children) == 0

        # Verify parent2 has the child
        parent2_children = account_repo.get_child_accounts(parent2.id)
        assert len(parent2_children) == 1
        assert parent2_children[0].id == child.id

    def test_move_account_to_top_level(self, test_db):
        """Test moving account from parent to top-level."""
        service = AccountService(test_db)

        # Create parent and child
        parent = service.create_account(
            name="Bank Accounts", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        child = service.create_account(
            name="Checking", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="1000.00",
            parent_account_id=parent.id
        )

        assert child.hierarchy_level == 1

        # Move to top-level
        moved_child = service.move_account(child.id, None)

        assert moved_child.parent_account_id is None
        assert moved_child.hierarchy_level == 0
        assert moved_child.hierarchy_path == f"/{moved_child.id}"


class TestCalculateParentBalance:
    """Integration tests for calculating parent account balance."""

    def test_calculate_parent_balance_from_children(self, test_db):
        """Test that parent balance is calculated from child accounts."""
        service = AccountService(test_db)

        # Create parent
        parent = service.create_account(
            name="Bank Accounts", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        # Create children with balances
        child1 = service.create_account(
            name="Checking", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="1000.00",
            parent_account_id=parent.id
        )

        child2 = service.create_account(
            name="Savings", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS, initial_balance="5000.00",
            parent_account_id=parent.id
        )

        # Calculate parent balance (Python version)
        balance = service.get_parent_account_balance(parent.id)
        assert balance == Decimal("6000.00")  # 1000 + 5000

        # Calculate parent balance (SQL version)
        balance_sql = service.get_parent_account_balance_sql(parent.id)
        assert balance_sql == Decimal("6000.00")

    def test_calculate_nested_parent_balance(self, test_db):
        """Test calculating balance for nested parent hierarchy."""
        service = AccountService(test_db)

        # Level 0: Grandparent
        grandparent = service.create_account(
            name="All Bank Accounts", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        # Level 1: Parent (nested)
        parent = service.create_account(
            name="Checking Accounts", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00",
            parent_account_id=grandparent.id, is_parent=True
        )

        # Level 2: Leaf accounts
        child1 = service.create_account(
            name="Personal Checking", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="2000.00",
            parent_account_id=parent.id
        )

        child2 = service.create_account(
            name="Business Checking", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="8000.00",
            parent_account_id=parent.id
        )

        # Parent balance should be sum of children
        parent_balance = service.get_parent_account_balance_sql(parent.id)
        assert parent_balance == Decimal("10000.00")

        # Grandparent balance should also be sum of all descendants
        grandparent_balance = service.get_parent_account_balance_sql(grandparent.id)
        assert grandparent_balance == Decimal("10000.00")


class TestDeleteParentCascade:
    """Integration tests for deleting parent accounts with children."""

    def test_prevent_delete_parent_with_children_without_force(self, test_db):
        """Test that deleting parent with children fails without force."""
        service = AccountService(test_db)

        # Create parent and child
        parent = service.create_account(
            name="Bank Accounts", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        child = service.create_account(
            name="Checking", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="1000.00",
            parent_account_id=parent.id
        )

        # Try to delete parent without force
        with pytest.raises(ValidationError, match="has 1 child accounts"):
            service.delete_account_with_children(parent.id, force=False)

    def test_cascade_delete_parent_with_force(self, test_db):
        """Test cascade delete of parent and all children with force=True."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create parent with multiple children
        parent = service.create_account(
            name="Bank Accounts", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        child1 = service.create_account(
            name="Checking", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="1000.00",
            parent_account_id=parent.id
        )

        child2 = service.create_account(
            name="Savings", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS, initial_balance="5000.00",
            parent_account_id=parent.id
        )

        # Delete with force
        result = service.delete_account_with_children(parent.id, force=True)
        assert result is True

        # Verify all accounts deleted
        assert account_repo.get_by_id(parent.id) is None
        assert account_repo.get_by_id(child1.id) is None
        assert account_repo.get_by_id(child2.id) is None


class TestConvertToParent:
    """Integration tests for converting regular accounts to parent accounts."""

    def test_convert_account_to_parent_and_add_children(self, test_db):
        """Test converting regular account to parent and adding children."""
        service = AccountService(test_db)

        # Create regular account with zero balance
        account = service.create_account(
            name="Bank Accounts", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00"
        )

        assert account.is_parent is False

        # Convert to parent
        converted = service.convert_to_parent_account(account.id)
        assert converted.is_parent is True

        # Now add children
        child = service.create_account(
            name="Checking", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="1000.00",
            parent_account_id=converted.id
        )

        assert child.parent_account_id == converted.id


class TestHierarchyConstraints:
    """Integration tests for hierarchy validation constraints."""

    def test_cannot_create_circular_reference(self, test_db):
        """Test that circular references are prevented."""
        service = AccountService(test_db)

        # Create parent and child
        parent = service.create_account(
            name="Parent", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        child = service.create_account(
            name="Child", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00",
            parent_account_id=parent.id, is_parent=True
        )

        # Try to move parent under child (would create cycle)
        with pytest.raises(ValidationError, match="circular reference"):
            service.move_account(parent.id, child.id)

    def test_cannot_exceed_maximum_depth(self, test_db):
        """Test that maximum hierarchy depth (5 levels) is enforced."""
        service = AccountService(test_db)

        # Create 5 levels (0, 1, 2, 3, 4)
        level0 = service.create_account(
            name="Level 0", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        level1 = service.create_account(
            name="Level 1", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00",
            parent_account_id=level0.id, is_parent=True
        )

        level2 = service.create_account(
            name="Level 2", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00",
            parent_account_id=level1.id, is_parent=True
        )

        level3 = service.create_account(
            name="Level 3", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00",
            parent_account_id=level2.id, is_parent=True
        )

        level4 = service.create_account(
            name="Level 4", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00",
            parent_account_id=level3.id, is_parent=True
        )

        assert level4.hierarchy_level == 4

        # Try to add level 5 (should fail)
        with pytest.raises(ValidationError, match="Maximum hierarchy depth"):
            service.create_account(
                name="Level 5", account_type=AccountType.ASSET,
                account_subtype=AccountSubtype.CHECKING, initial_balance="0.00",
                parent_account_id=level4.id
            )


class TestHierarchyPathUpdates:
    """Integration tests for hierarchy path updates."""

    def test_hierarchy_paths_update_when_moving_account(self, test_db):
        """Test that hierarchy paths are updated correctly when moving accounts."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create parent1 with child and grandchild
        parent1 = service.create_account(
            name="Parent 1", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        child = service.create_account(
            name="Child", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00",
            parent_account_id=parent1.id, is_parent=True
        )

        grandchild = service.create_account(
            name="Grandchild", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="1000.00",
            parent_account_id=child.id
        )

        # Verify initial paths
        assert grandchild.hierarchy_path == f"/{parent1.id}/{child.id}/{grandchild.id}"

        # Create parent2
        parent2 = service.create_account(
            name="Parent 2", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        # Move child (and its descendants) to parent2
        service.move_account(child.id, parent2.id)

        # Verify paths updated
        updated_child = account_repo.get_by_id(child.id)
        updated_grandchild = account_repo.get_by_id(grandchild.id)

        assert updated_child.hierarchy_path == f"/{parent2.id}/{child.id}"
        assert updated_grandchild.hierarchy_path == f"/{parent2.id}/{child.id}/{grandchild.id}"

    def test_get_descendant_accounts_returns_all_levels(self, test_db):
        """Test that get_descendant_accounts returns all nested descendants."""
        service = AccountService(test_db)
        account_repo = AccountRepository(test_db)

        # Create hierarchy: parent -> child -> grandchild
        parent = service.create_account(
            name="Parent", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        child = service.create_account(
            name="Child", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00",
            parent_account_id=parent.id, is_parent=True
        )

        grandchild1 = service.create_account(
            name="Grandchild 1", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="1000.00",
            parent_account_id=child.id
        )

        grandchild2 = service.create_account(
            name="Grandchild 2", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.SAVINGS, initial_balance="2000.00",
            parent_account_id=child.id
        )

        # Get all descendants of parent
        descendants = account_repo.get_descendant_accounts(parent.id)

        # Should return child + both grandchildren (3 total)
        assert len(descendants) == 3
        descendant_ids = [d.id for d in descendants]
        assert child.id in descendant_ids
        assert grandchild1.id in descendant_ids
        assert grandchild2.id in descendant_ids


class TestNestedParentAccounts:
    """Integration tests for nested parent accounts."""

    def test_nested_parents_allowed(self, test_db):
        """Test that nested parent accounts are allowed."""
        service = AccountService(test_db)

        # Create parent that is itself under another parent
        grandparent = service.create_account(
            name="Assets", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        # Create parent under grandparent
        parent = service.create_account(
            name="Bank Accounts", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00",
            parent_account_id=grandparent.id, is_parent=True
        )

        assert parent.is_parent is True
        assert parent.parent_account_id == grandparent.id

    def test_type_compatibility_enforced_across_hierarchy(self, test_db):
        """Test that type compatibility is enforced for all hierarchy levels."""
        service = AccountService(test_db)

        # Create ASSET parent
        asset_parent = service.create_account(
            name="Assets", account_type=AccountType.ASSET,
            account_subtype=AccountSubtype.CHECKING, initial_balance="0.00", is_parent=True
        )

        # Cannot add LIABILITY child to ASSET parent
        with pytest.raises(ValidationError, match="must match parent account type"):
            service.create_account(
                name="Credit Card", account_type=AccountType.LIABILITY,
                account_subtype=AccountSubtype.CREDIT_CARD, initial_balance="0.00",
                parent_account_id=asset_parent.id
            )
