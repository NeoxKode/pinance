"""
Account balance validation service (US-010).

Validates that cached account balances match calculated balances from
journal entries. Provides trial balance reports and integrity checks.

Story: US-010 - Account Balance Validation & Integrity
"""

import logging
from decimal import Decimal
from datetime import datetime
from typing import List, Optional

from finance_app.data.database import Database
from finance_app.data.repositories.account_repository import AccountRepository
from finance_app.data.repositories.journal_entry_repository import JournalEntryRepository
from finance_app.data.models import (
    Account,
    ValidationResult,
    TrialBalance,
    TrialBalanceEntry,
    AccountType
)
from finance_app.utils.exceptions import NotFoundError


class AccountBalanceValidator:
    """
    Service for validating account balance integrity.

    Ensures cached balances (accounts.balance) match calculated balances
    from journal entries. Provides validation reports and repair tools.

    Core Responsibilities:
        - Validate single account balance
        - Validate all account balances
        - Fix discrepancies (recalculate from journal entries)
        - Generate trial balance reports
        - Log validation history for auditing

    Usage:
        validator = AccountBalanceValidator(db, account_repo, journal_repo)

        # Validate single account
        result = validator.validate_account_balance(account_id=123)
        if not result.is_valid:
            print(f"Discrepancy: ${result.difference}")

        # Validate all accounts
        results = validator.validate_all_accounts()
        failed = [r for r in results if not r.is_valid]

        # Fix discrepancy
        if failed:
            for result in failed:
                validator.fix_account_balance(result.account_id)

        # Generate trial balance
        trial_balance = validator.get_trial_balance()
        print(trial_balance)  # Formatted table output
    """

    def __init__(
        self,
        db: Database,
        account_repo: AccountRepository,
        journal_repo: JournalEntryRepository
    ):
        """
        Initialize validator with dependencies.

        Args:
            db: Database instance for transactions
            account_repo: Repository for account operations
            journal_repo: Repository for journal entry operations
        """
        self.db = db
        self.account_repo = account_repo
        self.journal_repo = journal_repo
        self.logger = logging.getLogger(__name__)
        self.tolerance = Decimal('0.01')  # 1 cent tolerance for rounding

    def validate_account_balance(self, account_id: int) -> ValidationResult:
        """
        Validate single account balance against journal entries.

        Compares cached balance (accounts.balance) to calculated balance
        (SUM of journal entries). Returns validation result with details.

        Args:
            account_id: ID of account to validate

        Returns:
            ValidationResult with comparison details

        Raises:
            NotFoundError: If account doesn't exist

        Business Logic:
            1. Get account from repository
            2. Calculate balance from journal entries
            3. Compare cached vs calculated
            4. Mark as valid if difference < tolerance ($0.01)
            5. Log validation result

        Example:
            >>> result = validator.validate_account_balance(123)
            >>> print(f"Valid: {result.is_valid}, Diff: ${result.difference}")
            Valid: True, Diff: $0.00
        """
        # 1. Get account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account {account_id} not found")

        # 2. Calculate balance from journal entries
        calculated_balance = self.calculate_account_balance_from_journal(account_id)

        # 3. Compare cached vs calculated
        cached_balance = account.balance
        difference = cached_balance - calculated_balance
        is_valid = abs(difference) < self.tolerance

        # 4. Create validation result
        result = ValidationResult(
            account_id=account.id,
            account_name=account.name,
            cached_balance=cached_balance,
            calculated_balance=calculated_balance,
            difference=difference,
            is_valid=is_valid,
            validated_at=datetime.now(),
            tolerance=self.tolerance
        )

        # 5. Log result
        if not is_valid:
            self.logger.warning(
                f"Balance mismatch in account '{account.name}' (ID {account.id}): "
                f"cached=${cached_balance:.2f}, calculated=${calculated_balance:.2f}, "
                f"difference=${difference:.2f} ({result.severity})"
            )
        else:
            self.logger.debug(
                f"Account '{account.name}' (ID {account.id}) validated successfully"
            )

        # 6. Log to database (optional - for audit trail)
        self.log_validation_result(result, was_repaired=False)

        return result

    def validate_all_accounts(self) -> List[ValidationResult]:
        """
        Validate all account balances in the system.

        Iterates through all accounts and validates each balance against
        journal entries. Returns list of validation results.

        Returns:
            List of ValidationResult, one per account

        Performance:
            Target: < 5 seconds for 10,000 accounts
            Optimization: Uses single SQL query per account

        Example:
            >>> results = validator.validate_all_accounts()
            >>> failed = [r for r in results if not r.is_valid]
            >>> print(f"{len(failed)} accounts have discrepancies")
        """
        accounts = self.account_repo.get_all()
        results = []

        self.logger.info(f"Validating {len(accounts)} accounts...")
        start_time = datetime.now()

        for account in accounts:
            try:
                result = self.validate_account_balance(account.id)
                results.append(result)
            except Exception as e:
                self.logger.error(
                    f"Error validating account {account.id} '{account.name}': {e}"
                )
                # Continue with next account

        # Log summary
        passed = sum(1 for r in results if r.is_valid)
        failed = len(results) - passed
        elapsed = (datetime.now() - start_time).total_seconds()

        if failed > 0:
            self.logger.error(
                f"Validation complete: {passed}/{len(results)} passed, "
                f"{failed} FAILED in {elapsed:.2f}s"
            )
        else:
            self.logger.info(
                f"✅ Validation complete: {passed}/{len(results)} passed "
                f"in {elapsed:.2f}s"
            )

        return results

    def fix_account_balance(self, account_id: int) -> Account:
        """
        Fix account balance to match journal entries.

        Recalculates balance from journal entries and updates cached value
        in accounts table. Creates audit trail entry.

        Args:
            account_id: Account to fix

        Returns:
            Updated Account object with corrected balance

        Raises:
            NotFoundError: If account doesn't exist

        Business Logic:
            1. Get account from repository
            2. Calculate correct balance from journal entries
            3. Update accounts.balance to match calculated value
            4. Log correction with old/new values
            5. Return updated account

        Example:
            >>> # Account has cached=$1000, calculated=$1050
            >>> fixed = validator.fix_account_balance(account_id=123)
            >>> assert fixed.balance == Decimal("1050.00")
        """
        # 1. Get account
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError(f"Account {account_id} not found")

        # 2. Calculate correct balance
        calculated_balance = self.calculate_account_balance_from_journal(account_id)

        old_balance = account.balance
        difference = calculated_balance - old_balance

        # 3. Update account balance directly via SQL (bypass triggers)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE accounts
                SET balance = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (float(calculated_balance), account_id)
            )
            conn.commit()

        # Update account object
        account.balance = calculated_balance

        # 4. Log correction
        self.logger.info(
            f"Fixed balance for account '{account.name}' (ID {account.id}): "
            f"old=${old_balance:.2f}, new=${calculated_balance:.2f}, "
            f"correction=${difference:+.2f}"
        )

        # Log to database
        result = ValidationResult(
            account_id=account.id,
            account_name=account.name,
            cached_balance=old_balance,
            calculated_balance=calculated_balance,
            difference=difference,
            is_valid=True,  # Now valid after fix
            validated_at=datetime.now()
        )
        self.log_validation_result(result, was_repaired=True)

        return account

    def get_trial_balance(
        self,
        as_of_date: Optional[str] = None
    ) -> TrialBalance:
        """
        Generate trial balance report.

        Lists all accounts with debit/credit balances and verifies
        accounting equation: Total Debits = Total Credits.

        Args:
            as_of_date: Date for historical trial balance (YYYY-MM-DD)
                       If None, uses current date

        Returns:
            TrialBalance object with all accounts and totals

        Business Rules:
            - Debit normal balance accounts (Assets, Expenses):
              Show positive balances in debit column
            - Credit normal balance accounts (Liabilities, Equity, Income):
              Show positive balances in credit column
            - Total debits should equal total credits (accounting equation)

        Example:
            >>> tb = validator.get_trial_balance()
            >>> print(tb)
            TRIAL BALANCE - 2025-10-27
            ...
            Status: ✅ BALANCED
        """
        today = datetime.now().strftime('%Y-%m-%d')
        as_of = as_of_date or today

        # Create trial balance report
        trial_balance = TrialBalance(
            report_date=today,
            as_of_date=as_of
        )

        # Get all accounts
        accounts = self.account_repo.get_all()

        self.logger.info(f"Generating trial balance for {len(accounts)} accounts as of {as_of}")

        for account in accounts:
            # Calculate balance from journal entries (use cached balance for speed)
            balance = account.balance

            # Determine if account has debit or credit normal balance
            # Assets and Expenses = Debit normal balance
            # Liabilities, Equity, Income = Credit normal balance
            debit_balance = Decimal('0.00')
            credit_balance = Decimal('0.00')

            if account.account_type in (AccountType.ASSET, AccountType.EXPENSE):
                # Debit normal balance accounts
                if balance > 0:
                    debit_balance = balance
                else:
                    credit_balance = abs(balance)
            else:
                # Credit normal balance accounts (Liability, Equity, Income)
                if balance > 0:
                    credit_balance = balance
                else:
                    debit_balance = abs(balance)

            # Create entry
            entry = TrialBalanceEntry(
                account_id=account.id,
                account_name=account.name,
                account_type=account.account_type.value,
                debit_balance=debit_balance,
                credit_balance=credit_balance
            )

            trial_balance.add_entry(entry)

        # Log result
        if trial_balance.is_balanced:
            self.logger.info(
                f"✅ Trial balance is BALANCED: "
                f"Debits=${trial_balance.total_debits:.2f}, "
                f"Credits=${trial_balance.total_credits:.2f}"
            )
        else:
            self.logger.error(
                f"❌ Trial balance UNBALANCED: "
                f"Debits=${trial_balance.total_debits:.2f}, "
                f"Credits=${trial_balance.total_credits:.2f}, "
                f"Difference=${trial_balance.difference:.2f}"
            )

        return trial_balance

    def calculate_account_balance_from_journal(self, account_id: int) -> Decimal:
        """
        Calculate account balance from journal entries.

        Sums all journal entries for the account:
        Balance = SUM(debit_amount - credit_amount)

        Args:
            account_id: Account to calculate balance for

        Returns:
            Calculated balance as Decimal

        Note:
            This is the "source of truth" - journal entries are immutable
            and represent the actual financial history.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            result = cursor.execute(
                """
                SELECT SUM(debit_amount - credit_amount) as balance
                FROM journal_entries
                WHERE account_id = ?
                """,
                (account_id,)
            ).fetchone()

            balance = result['balance'] if result['balance'] is not None else 0.0
            return Decimal(str(balance))

    def log_validation_result(
        self,
        result: ValidationResult,
        was_repaired: bool = False
    ):
        """
        Log validation result to database for audit trail.

        Args:
            result: ValidationResult to log
            was_repaired: True if balance was automatically fixed
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO balance_validation_log (
                    account_id,
                    cached_balance,
                    calculated_balance,
                    difference,
                    was_repaired,
                    validated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    result.account_id,
                    float(result.cached_balance),
                    float(result.calculated_balance),
                    float(result.difference),
                    1 if was_repaired else 0,
                    result.validated_at.isoformat()
                )
            )
            conn.commit()
