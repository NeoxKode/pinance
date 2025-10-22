"""
Administrative tools for balance validation and reconciliation.

Story: US-002A - Journal Entry Foundation
"""
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from finance_app.data.database import Database
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.business.double_entry_service import DoubleEntryService
from finance_app.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class BalanceValidationResult:
    """Result of balance validation check."""
    account_id: int
    account_name: str
    account_balance: Decimal
    journal_balance: Decimal
    difference: Decimal
    is_valid: bool
    tolerance: Decimal = Decimal("0.01")


class AdminTools:
    """Administrative tools for system maintenance and validation."""

    def __init__(self, database: Database):
        """
        Initialize admin tools.

        Args:
            database: Database instance
        """
        self.db = database
        self.account_repo = AccountRepository(database)
        self.journal_repo = JournalEntryRepository(database)
        self.double_entry_service = DoubleEntryService(database)

    def validate_all_account_balances(
        self,
        tolerance: Decimal = Decimal("0.01")
    ) -> List[BalanceValidationResult]:
        """
        Validate all account balances against journal entries.

        Args:
            tolerance: Acceptable difference (default 0.01)

        Returns:
            List of validation results for all accounts
        """
        results = []
        accounts = self.account_repo.get_all()

        for account in accounts:
            result = self._validate_account_balance(account.id, tolerance)
            results.append(result)

            if not result.is_valid:
                logger.warning(
                    f"Balance mismatch for account {account.id} ({account.name}): "
                    f"account={result.account_balance}, journal={result.journal_balance}, "
                    f"diff={result.difference}"
                )

        return results

    def validate_account_balance(
        self,
        account_id: int,
        tolerance: Decimal = Decimal("0.01")
    ) -> BalanceValidationResult:
        """
        Validate a single account's balance.

        Args:
            account_id: Account ID to validate
            tolerance: Acceptable difference (default 0.01)

        Returns:
            Validation result
        """
        return self._validate_account_balance(account_id, tolerance)

    def _validate_account_balance(
        self,
        account_id: int,
        tolerance: Decimal
    ) -> BalanceValidationResult:
        """
        Internal method to validate account balance.

        Args:
            account_id: Account ID
            tolerance: Acceptable difference

        Returns:
            Validation result
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        account_balance = account.balance
        journal_balance = self.journal_repo.get_account_balance(account_id)
        difference = abs(account_balance - journal_balance)

        return BalanceValidationResult(
            account_id=account.id,
            account_name=account.name,
            account_balance=account_balance,
            journal_balance=journal_balance,
            difference=difference,
            is_valid=difference <= tolerance,
            tolerance=tolerance
        )

    def reconcile_account_balance(self, account_id: int) -> Tuple[Decimal, Decimal]:
        """
        Force reconcile an account's balance with journal entries.

        This updates the account table balance to match the journal calculation.
        Use with caution - this modifies data.

        Args:
            account_id: Account ID to reconcile

        Returns:
            Tuple of (old_balance, new_balance)
        """
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        old_balance = account.balance
        journal_balance = self.journal_repo.get_account_balance(account_id)

        # Update account balance to match journal
        difference = journal_balance - old_balance
        self.account_repo.update_balance(account_id, difference)

        logger.warning(
            f"Force reconciled account {account_id} ({account.name}): "
            f"{old_balance} -> {journal_balance}"
        )

        return (old_balance, journal_balance)

    def get_validation_summary(
        self,
        results: List[BalanceValidationResult]
    ) -> Dict[str, any]:
        """
        Generate summary statistics from validation results.

        Args:
            results: List of validation results

        Returns:
            Dictionary with summary statistics
        """
        total_accounts = len(results)
        valid_accounts = sum(1 for r in results if r.is_valid)
        invalid_accounts = total_accounts - valid_accounts

        total_difference = sum(r.difference for r in results)
        max_difference = max((r.difference for r in results), default=Decimal("0"))

        invalid_details = [
            {
                "account_id": r.account_id,
                "account_name": r.account_name,
                "account_balance": str(r.account_balance),
                "journal_balance": str(r.journal_balance),
                "difference": str(r.difference)
            }
            for r in results if not r.is_valid
        ]

        return {
            "total_accounts": total_accounts,
            "valid_accounts": valid_accounts,
            "invalid_accounts": invalid_accounts,
            "valid_percentage": (valid_accounts / total_accounts * 100) if total_accounts > 0 else 0,
            "total_difference": str(total_difference),
            "max_difference": str(max_difference),
            "invalid_details": invalid_details
        }

    def print_validation_report(
        self,
        results: List[BalanceValidationResult]
    ) -> None:
        """
        Print a formatted validation report.

        Args:
            results: List of validation results
        """
        summary = self.get_validation_summary(results)

        print("\n" + "=" * 70)
        print("ACCOUNT BALANCE VALIDATION REPORT")
        print("=" * 70)
        print(f"Total Accounts:    {summary['total_accounts']}")
        print(f"Valid:             {summary['valid_accounts']} ({summary['valid_percentage']:.1f}%)")
        print(f"Invalid:           {summary['invalid_accounts']}")
        print(f"Total Difference:  ${summary['total_difference']}")
        print(f"Max Difference:    ${summary['max_difference']}")
        print("=" * 70)

        if summary['invalid_accounts'] > 0:
            print("\nINVALID ACCOUNTS:")
            print("-" * 70)
            for detail in summary['invalid_details']:
                print(f"Account {detail['account_id']}: {detail['account_name']}")
                print(f"  Account Balance: ${detail['account_balance']}")
                print(f"  Journal Balance: ${detail['journal_balance']}")
                print(f"  Difference:      ${detail['difference']}")
                print("-" * 70)
        else:
            print("\n✓ All account balances are valid!\n")
