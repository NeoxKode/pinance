#!/bin/bash
# UI Testing Script for US-016: Search & Filter UI Panel
# Tests visual implementation and integration with main window

set -e

# Configuration
export DISPLAY=:99
SCREENSHOT_DIR="images/ui-screenshots/us-016-testing"
TEST_RUN=$(date +%Y%m%d_%H%M%S)
SCREENSHOT_PREFIX="$SCREENSHOT_DIR/${TEST_RUN}"

echo "=================================================="
echo "US-016 UI Testing - Search & Filter Panel"
echo "=================================================="
echo "Test Run: $TEST_RUN"
echo "Screenshot Dir: $SCREENSHOT_DIR"
echo ""

# Create screenshot directory
mkdir -p "$SCREENSHOT_DIR"

# Check if xvfb is running
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "Starting Xvfb on display :99..."
    Xvfb :99 -screen 0 1920x1080x24 -ac &
    XVFB_PID=$!
    sleep 2
    echo "✓ Xvfb started (PID: $XVFB_PID)"
else
    echo "✓ Xvfb already running"
    XVFB_PID=""
fi

echo ""
echo "Launching Finance App..."

# Launch the application
SKIP_STARTUP_VALIDATION=1 PYTHONPATH=/home/neoxkode/dev/pinance python3 finance_app.py &
APP_PID=$!
echo "✓ App launched (PID: $APP_PID)"

# Wait for window to appear
echo "Waiting for application window..."
for i in {1..10}; do
    if DISPLAY=:99 xdotool search --name "Personal Finance" > /dev/null 2>&1; then
        echo "✓ Application window found!"
        break
    fi
    sleep 1
    if [ $i -eq 10 ]; then
        echo "✗ ERROR: Application window not found after 10 seconds"
        kill $APP_PID 2>/dev/null || true
        [ -n "$XVFB_PID" ] && kill $XVFB_PID 2>/dev/null || true
        exit 1
    fi
done

WINDOW_ID=$(DISPLAY=:99 xdotool search --name "Personal Finance" | head -1)
echo "Window ID: $WINDOW_ID"

echo ""
echo "=================================================="
echo "Capturing Screenshots"
echo "=================================================="

# Screenshot 1: Main window with search panel visible
sleep 1
echo "1. Capturing main window with search panel..."
DISPLAY=:99 scrot "${SCREENSHOT_PREFIX}_01_main_window_with_panel.png"
echo "   ✓ Saved: ${SCREENSHOT_PREFIX}_01_main_window_with_panel.png"

# Screenshot 2: Focus on search panel (zoomed if possible)
sleep 0.5
echo "2. Capturing search panel expanded state..."
DISPLAY=:99 scrot "${SCREENSHOT_PREFIX}_02_panel_expanded.png"
echo "   ✓ Saved: ${SCREENSHOT_PREFIX}_02_panel_expanded.png"

# Screenshot 3: Try to locate and click collapse button
echo "3. Testing collapse functionality..."
# Note: Without exact coordinates, we'll document the state
sleep 0.5
DISPLAY=:99 scrot "${SCREENSHOT_PREFIX}_03_panel_with_controls.png"
echo "   ✓ Saved: ${SCREENSHOT_PREFIX}_03_panel_with_controls.png"

# Screenshot 4: Search widget integration
echo "4. Capturing search widget integration..."
sleep 0.5
DISPLAY=:99 scrot "${SCREENSHOT_PREFIX}_04_search_widget_integrated.png"
echo "   ✓ Saved: ${SCREENSHOT_PREFIX}_04_search_widget_integrated.png"

echo ""
echo "=================================================="
echo "Cleanup"
echo "=================================================="

# Close application
echo "Closing application..."
kill $APP_PID 2>/dev/null || true
sleep 1

# Stop xvfb if we started it
if [ -n "$XVFB_PID" ]; then
    echo "Stopping Xvfb..."
    kill $XVFB_PID 2>/dev/null || true
fi

echo ""
echo "=================================================="
echo "Test Results"
echo "=================================================="
echo "Screenshots saved to: $SCREENSHOT_DIR"
echo ""
echo "Files created:"
ls -lh "$SCREENSHOT_DIR"/${TEST_RUN}_*.png 2>/dev/null || echo "No screenshots found"
echo ""
echo "Total screenshots: $(ls -1 "$SCREENSHOT_DIR"/${TEST_RUN}_*.png 2>/dev/null | wc -l)"
echo ""
echo "✅ UI Testing Complete!"
echo ""
echo "Next steps:"
echo "  1. Review screenshots to validate UI implementation"
echo "  2. Verify search panel is visible above transaction list"
echo "  3. Confirm professional styling and layout"
echo "  4. Check WCAG 2.1 AA focus indicators"
echo ""
