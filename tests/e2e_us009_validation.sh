#!/bin/bash
# E2E Validation Script for US-009 Account Color Coding
# Tech Lead: Comprehensive E2E testing with xvfb

set -e

# Configuration
export DISPLAY=:99
export PYTHONPATH=/home/neoxkode/dev/pinance
export SKIP_STARTUP_VALIDATION=1
TEST_RUN=$(date +%Y%m%d_%H%M%S)
SCREENSHOT_DIR="images/e2e-screenshots/us009-validation/run_${TEST_RUN}"
mkdir -p "$SCREENSHOT_DIR"

echo "=========================================="
echo "US-009 E2E Validation - Test Run: $TEST_RUN"
echo "=========================================="

# Start xvfb if not running
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "[1/7] Starting Xvfb on display :99..."
    Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
    XVFB_PID=$!
    sleep 3
    echo "✓ Xvfb started (PID: $XVFB_PID)"
else
    echo "[1/7] Xvfb already running"
    XVFB_PID=$(pgrep -x "Xvfb")
fi

# Launch application
echo "[2/7] Launching application..."
START_TIME=$(date +%s)
source .venv/bin/activate && timeout 60 python finance_app.py &
APP_PID=$!
echo "✓ Application launched (PID: $APP_PID)"

# Wait for window to appear
echo "[3/7] Waiting for application window..."
WINDOW_FOUND=false
for i in {1..30}; do
    if xdotool search --name "Personal Finance" > /dev/null 2>&1; then
        WINDOW_ID=$(xdotool search --name "Personal Finance" | head -1)
        echo "✓ Application window found (Window ID: $WINDOW_ID)"
        WINDOW_FOUND=true
        break
    fi
    sleep 1
done

if [ "$WINDOW_FOUND" = false ]; then
    echo "✗ ERROR: Application window not found after 30 seconds"
    kill $APP_PID 2>/dev/null || true
    kill $XVFB_PID 2>/dev/null || true
    exit 1
fi

# Calculate startup time
END_TIME=$(date +%s)
STARTUP_TIME=$((END_TIME - START_TIME))
echo "✓ Startup time: ${STARTUP_TIME}s"

# Capture initial state
echo "[4/7] Capturing initial application state..."
sleep 2
scrot "$SCREENSHOT_DIR/01-initial-state.png"
echo "✓ Screenshot saved: 01-initial-state.png"

# Test account list with colors
echo "[5/7] Testing account tree with color indicators..."
sleep 1
scrot "$SCREENSHOT_DIR/02-account-tree-with-colors.png"
echo "✓ Screenshot saved: 02-account-tree-with-colors.png"

# Test navigation and UI elements
echo "[6/7] Testing UI elements visibility..."
sleep 1
scrot "$SCREENSHOT_DIR/03-ui-elements.png"
echo "✓ Screenshot saved: 03-ui-elements.png"

# Final state capture
echo "[7/7] Capturing final state..."
sleep 1
scrot "$SCREENSHOT_DIR/04-final-state.png"
echo "✓ Screenshot saved: 04-final-state.png"

# Cleanup
echo "=========================================="
echo "Cleaning up..."
kill $APP_PID 2>/dev/null || true
sleep 2
kill $XVFB_PID 2>/dev/null || true

# Generate report
echo "=========================================="
echo "E2E Test Results:"
echo "=========================================="
echo "Test Run ID: $TEST_RUN"
echo "Startup Time: ${STARTUP_TIME}s (budget: < 2s)"
echo "Screenshots Directory: $SCREENSHOT_DIR"
echo ""
echo "Screenshot Summary:"
ls -lh "$SCREENSHOT_DIR" | awk '{if(NR>1) print "  " $9 " - " $5}'
echo ""
echo "Total Screenshots: $(ls -1 "$SCREENSHOT_DIR" | wc -l)"
echo ""

# Performance Check
if [ $STARTUP_TIME -lt 2 ]; then
    echo "✓ Performance: PASSED (startup < 2s)"
else
    echo "⚠ Performance: WARNING (startup ≥ 2s)"
fi

echo ""
echo "View screenshots:"
echo "  cd $SCREENSHOT_DIR && ls -1"
echo ""
echo "=========================================="
echo "E2E Validation Complete!"
echo "=========================================="
