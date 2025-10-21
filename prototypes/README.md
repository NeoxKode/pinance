# Prototypes

This directory contains time-boxed prototypes for validating technical approaches.

## SPIKE-001: Double-Entry Accounting Prototype

**File:** `double_entry_prototype.py`
**Time-box:** 8 hours
**Status:** Ready to run

### Quick Start

```bash
cd /home/neoxkode/dev/finance
python prototypes/double_entry_prototype.py
```

### What It Tests

1. ✅ Journal entry creation
2. ✅ Balanced transactions (debits = credits)
3. ✅ Account balance updates via triggers
4. ✅ Balance validation (cached vs calculated)
5. ✅ Trial balance
6. ✅ Unbalanced transaction rejection
7. ✅ Performance with 1,000 entries

### Expected Output

```
==================================================
DOUBLE-ENTRY ACCOUNTING PROTOTYPE
==================================================

📝 Test 1: Creating test accounts...
✅ Created accounts: Checking=1, Income=2, Expense=3

📝 Test 2: Creating income transaction (Salary $5,000)...
✅ Created balanced transaction with 2 entries
   Checking balance: $5000.00

...

==================================================
✅ ALL PROTOTYPE TESTS PASSED
==================================================

📊 RECOMMENDATION: Proceed with full implementation
```

### Success Criteria

- All 7 tests pass ✅
- Performance < 100ms for queries ✅
- No fundamental design flaws ✅

### Next Steps

After running:
1. Document results in `docs/spikes/SPIKE-001-RESULTS.md`
2. Make GO/NO-GO decision
3. If GO: Start US-001 (Account Type Taxonomy)

---

*Created: October 22, 2025*
