# Computer Control MCP Integration with BMAD Agents

**Version:** 1.0.0
**Date:** October 25, 2025
**Status:** Active

## Overview

The Personal Finance Manager project has integrated the **computer-use Model Context Protocol (MCP)** server with the BMAD Agent framework, enabling automated UI testing, E2E validation, and performance monitoring through computer control capabilities.

## What is the Computer-Use MCP?

The computer-use MCP server allows AI agents to control your computer through:
- **Mouse control**: Click, move, drag UI elements
- **Keyboard input**: Type text, send shortcuts
- **Screen capture**: Take screenshots for validation
- **Screen reading**: Read and verify screen content

## Installation Status

✅ **Installed**: The computer-use MCP server has been configured in Claude Code

**Configuration:**
- **Server name**: `computer-use`
- **Transport**: stdio (local process)
- **Command**: `npx -y computer-use-mcp`
- **Config file**: `/root/.claude.json`

## Integrated Agents

### 1. Frontend-Dev Agent (UI/UX Developer)

**Role:** UI testing, visual validation, accessibility testing

**MCP Capabilities:**
- Launch and interact with the PySide6 application
- Test UI components (buttons, forms, dialogs)
- Validate visual appearance and layout
- Test keyboard navigation and accessibility
- Capture screenshots for documentation

**Commands:**
- `*test-ui` - Run automated UI tests using MCP
- `*implement-ui` - Implement and test UI components
- `*accessibility` - Test accessibility with keyboard/screen reader

**Usage Example:**
```
User: "Test the transaction dialog UI"

Frontend-Dev Agent will:
1. Launch the finance application
2. Click "Add Transaction" button
3. Fill in form fields
4. Test validation messages
5. Capture screenshots
6. Verify visual appearance
```

### 2. Tech-Lead Agent (Technical Lead)

**Role:** E2E testing, performance validation, CI/CD automation

**MCP Capabilities:**
- Run complete end-to-end test workflows
- Measure performance during real usage
- Visual regression testing
- Security testing through UI
- CI/CD pipeline validation

**Commands:**
- `*e2e` - Run automated end-to-end tests
- `*test` - Design and execute test strategy
- `*optimize` - Performance testing and profiling
- `*security` - Security testing including UI-based attacks

**Usage Example:**
```
User: "Run E2E tests for the transaction workflow"

Tech-Lead Agent will:
1. Launch application
2. Execute complete transaction flow
3. Verify data persistence
4. Check account balance updates
5. Measure performance metrics
6. Generate test report with screenshots
```

## MCP Capabilities Matrix

| Capability | Frontend-Dev | Tech-Lead | Use Cases |
|------------|--------------|-----------|-----------|
| Mouse Control | ✅ | ✅ | Click buttons, select items, drag elements |
| Keyboard Input | ✅ | ✅ | Type text, keyboard shortcuts, tab navigation |
| Screenshot | ✅ | ✅ | Visual validation, documentation, regression testing |
| Screen Reading | ✅ | ✅ | Verify text, validate data, accessibility testing |

## Use Cases

### Frontend Development & Testing

**1. UI Component Testing**
```
Scenario: Test Transaction Dialog
- Launch app via MCP
- Click "Add Transaction"
- Fill form fields:
  * Description
  * Amount
  * Category
- Submit form
- Verify transaction appears
- Screenshot result
```

**2. Visual Validation**
```
Scenario: Validate Layout Changes
- Launch app
- Navigate to each screen
- Capture screenshots
- Compare with baseline images
- Flag visual regressions
```

**3. Accessibility Testing**
```
Scenario: Test Keyboard Navigation
- Launch app
- Tab through all focusable elements
- Verify focus indicators visible
- Test keyboard shortcuts (Ctrl+N, etc.)
- Verify screen reader labels
```

### Quality Assurance & Testing

**1. End-to-End Workflows**
```
Scenario: Complete Account Reconciliation
- Open reconciliation dialog
- Enter statement balance
- Mark transactions as cleared
- Calculate difference
- Complete reconciliation
- Verify account status
- Check audit trail
Performance: Measure total time
```

**2. Performance Validation**
```
Scenario: Measure Transaction Performance
- Add 100 transactions via MCP
- Measure each operation time
- Verify < 100ms per transaction
- Monitor UI responsiveness
- Generate performance report
```

**3. Regression Testing**
```
Scenario: Nightly Regression Suite
- Run all critical user paths
- Capture screenshots at each step
- Compare with baseline
- Flag any failures or changes
- Generate comprehensive report
```

### Security Testing

**1. Input Validation**
```
Scenario: Test SQL Injection Protection
- Attempt SQL injection in forms
- Try special characters
- Test field length limits
- Verify error handling
- Check no data leakage
```

**2. UI Security**
```
Scenario: Permission Boundaries
- Test unauthorized actions
- Verify error messages
- Check data access controls
- Test session handling
```

## Safety & Best Practices

### Safety Mode

**🔒 Supervised Mode (Default)**
- All MCP actions require human monitoring
- User can see and stop any action
- Recommended for development and testing
- Never use for production environments

### Best Practices

**1. Test Environment**
- ✅ Use test database (finance_test.db)
- ✅ Run in isolated environment
- ✅ Use test data only
- ❌ Never test on production data

**2. Test Design**
- ✅ Make tests independent
- ✅ Clean up after each test
- ✅ Add explicit waits for UI elements
- ✅ Handle async operations properly
- ❌ Don't make tests depend on each other

**3. Performance**
- ✅ Run tests in parallel when possible
- ✅ Use database snapshots
- ✅ Measure and track execution time
- ✅ Optimize slow tests

**4. Reliability**
- ✅ Retry flaky operations
- ✅ Log all MCP actions
- ✅ Capture screenshots on failure
- ✅ Add clear error messages

**5. Security**
- ✅ Monitor all computer control actions
- ✅ Use sandboxed environments
- ✅ Validate all inputs
- ❌ Never run destructive tests on production

## Integration with CI/CD

### Automated Testing Pipeline

```
┌─────────────────┐
│   Git Commit    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Pre-commit     │ ← Unit tests only (fast)
│  Hooks          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Pull Request   │ ← Unit + Integration tests
│  Validation     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Nightly Build  │ ← Full E2E suite with MCP
│                 │   Performance testing
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Release        │ ← Extended E2E tests
│  Candidate      │   Visual regression
│                 │   Security testing
└─────────────────┘
```

### GitHub Actions Example

```yaml
name: E2E Tests with MCP

on:
  schedule:
    - cron: '0 2 * * *'  # Run nightly at 2 AM

jobs:
  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Setup Node.js for MCP
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm install -g computer-use-mcp

      - name: Setup virtual display
        run: |
          sudo apt-get install -y xvfb
          Xvfb :99 -screen 0 1920x1080x24 &
          export DISPLAY=:99

      - name: Run E2E tests
        run: |
          pytest tests/e2e/ --mcp-enabled --screenshots

      - name: Upload screenshots
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-screenshots
          path: tests/screenshots/

      - name: Generate report
        run: |
          python scripts/generate_test_report.py
```

## Quick Start Guide

### For Frontend Developers

**Test a UI Component:**
```bash
# 1. Activate frontend-dev agent
/frontend-dev

# 2. Request UI testing
*test-ui
# Agent will ask what to test, respond: "Test the transaction dialog"

# 3. Agent will:
# - Launch the app
# - Navigate to the dialog
# - Interact with UI elements
# - Capture screenshots
# - Report results
```

### For Tech Leads

**Run E2E Tests:**
```bash
# 1. Activate tech-lead agent
/tech-lead

# 2. Request E2E testing
*e2e
# Agent will ask what workflow to test

# 3. Agent will:
# - Execute complete workflow
# - Measure performance
# - Generate report
# - Provide recommendations
```

## Troubleshooting

### MCP Server Not Connecting

**Issue:** `computer-use: ✗ Failed to connect`

**Solutions:**
1. Verify Node.js is installed: `node --version`
2. Restart Claude Code
3. Check MCP server manually: `npx -y computer-use-mcp`
4. Review logs in `/root/.npm/_logs/`

### Tests Failing

**Common Issues:**
1. **Application not launching**: Check Python environment
2. **UI elements not found**: Add explicit waits
3. **Screenshots blank**: Verify display settings
4. **Timeouts**: Increase wait times for slow operations

### Performance Issues

**If tests run slowly:**
1. Run tests in parallel
2. Use database snapshots
3. Optimize test data setup
4. Cache application startup

## Examples

### Example 1: Testing Transaction Creation

```python
# Pseudocode for MCP-based test
def test_create_transaction():
    # Launch app
    mcp.launch("python finance_app.py")
    mcp.wait_for_window("Personal Finance Manager")

    # Open dialog
    mcp.click_button("Add Transaction")
    mcp.wait_for_dialog("Add Transaction")

    # Fill form
    mcp.type_in_field("description", "Grocery Shopping")
    mcp.select_dropdown("category", "Groceries")
    mcp.type_in_field("amount", "75.50")

    # Submit
    mcp.click_button("Save")

    # Verify
    screenshot = mcp.screenshot()
    assert mcp.text_visible_on_screen("Grocery Shopping")
    assert mcp.text_visible_on_screen("$75.50")

    return screenshot
```

### Example 2: Performance Testing

```python
# Measure transaction performance
def test_transaction_performance():
    results = []

    for i in range(100):
        start = time.time()

        # Add transaction via MCP
        mcp.click_button("Add Transaction")
        mcp.fill_transaction_form(f"Test {i}", "50.00")
        mcp.click_button("Save")

        elapsed = time.time() - start
        results.append(elapsed)

    # Analyze results
    avg_time = sum(results) / len(results)
    max_time = max(results)

    assert avg_time < 0.1, f"Average time {avg_time}s exceeds 100ms"
    assert max_time < 0.5, f"Max time {max_time}s exceeds 500ms"
```

### Example 3: Visual Regression Testing

```python
# Compare screenshots
def test_visual_regression():
    # Take screenshots of all screens
    screens = {
        "main": mcp.screenshot_main_window(),
        "transaction_dialog": mcp.screenshot_dialog("Add Transaction"),
        "reconciliation": mcp.screenshot_dialog("Reconciliation"),
    }

    # Compare with baseline
    for screen_name, screenshot in screens.items():
        baseline = load_baseline(screen_name)
        diff = compare_images(baseline, screenshot)

        assert diff < 0.01, f"{screen_name} has visual changes: {diff}%"
```

## Resources

### Documentation
- [BMAD Agent Framework](./bmad-setup-guide.md)
- [Testing Strategy](./ARCHITECTURE.md#testing-strategy)
- [Frontend Development](../.bmad/frontend-dev.md)
- [Technical Leadership](../.bmad/tech-lead.md)

### External Links
- [Computer Use MCP GitHub](https://github.com/domdomegg/computer-use-mcp)
- [Model Context Protocol](https://anthropic.com/news/model-context-protocol)
- [Claude Code MCP Guide](https://docs.claude.com/en/docs/claude-code/mcp)

## Support

### Getting Help

**For MCP Issues:**
1. Check this documentation
2. Review MCP server logs
3. Test MCP server independently
4. Consult Claude Code docs

**For Test Issues:**
1. Review test logs and screenshots
2. Reproduce manually
3. Check test environment setup
4. Consult tech-lead agent

**For Integration Issues:**
1. Verify agent configuration
2. Check MCP server status
3. Review agent documentation
4. Test with simple scenarios first

## Changelog

### Version 1.0.0 (October 25, 2025)
- Initial integration of computer-use MCP
- Added MCP capabilities to frontend-dev agent
- Added MCP capabilities to tech-lead agent
- Created comprehensive documentation
- Defined safety guidelines and best practices

---

**Last Updated:** October 25, 2025
**Maintained By:** Tech Lead
**Status:** Active & Production-Ready
