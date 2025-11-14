#!/bin/bash
#
# Automated UI Test for US-016: Search & Filter UI Panel
#
# This script tests the SearchPanelWidget implementation using Xvfb for
# headless GUI testing and captures screenshots at each step for visual
# validation.
#
# Usage:
#   chmod +x tests/ui/test_us016_search_panel.sh
#   ./tests/ui/test_us016_search_panel.sh
#
# Requirements:
#   - xvfb (X Virtual Frame Buffer)
#   - scrot (Screenshot utility)
#   - xdotool (X automation tool)
#
# Created: 2025-11-12
# Story: US-016 - Search & Filter UI Panel (EPIC-002, Sprint 13)
#

# Note: Don't use 'set -e' because xdotool may fail in Xvfb without breaking tests

# Colors for output (define first)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
export DISPLAY=:99
SCREENSHOT_DIR="images/ui-screenshots/us016-$(date +%Y%m%d_%H%M%S)"
TEST_NAME="US-016: Search Panel Widget"

# Use virtual environment Python if available
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
else
    PYTHON_CMD="python3"
fi

APP_CMD="$PYTHON_CMD finance_app.py"

# Create screenshot directory
mkdir -p "$SCREENSHOT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🧪 Testing: $TEST_NAME${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! command -v Xvfb &> /dev/null; then
    echo -e "${RED}✗ Xvfb not found. Install with: sudo apt-get install xvfb${NC}"
    exit 1
fi

if ! command -v scrot &> /dev/null; then
    echo -e "${RED}✗ scrot not found. Install with: sudo apt-get install scrot${NC}"
    exit 1
fi

if ! command -v xdotool &> /dev/null; then
    echo -e "${RED}✗ xdotool not found. Install with: sudo apt-get install xdotool${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All dependencies found${NC}"
echo ""

# Start Xvfb if not already running
if ! pgrep -f "Xvfb $DISPLAY" > /dev/null; then
    echo -e "${YELLOW}Starting Xvfb on display $DISPLAY...${NC}"
    Xvfb $DISPLAY -screen 0 1920x1080x24 &
    XVFB_PID=$!
    sleep 2
    echo -e "${GREEN}✓ Xvfb started (PID: $XVFB_PID)${NC}"
else
    echo -e "${GREEN}✓ Xvfb already running on $DISPLAY${NC}"
    XVFB_PID=""
fi
echo ""

# Launch application
echo -e "${YELLOW}Launching application...${NC}"
SKIP_STARTUP_VALIDATION=1 PYTHONPATH=/home/neoxkode/dev/pinance $APP_CMD &
APP_PID=$!
echo -e "${GREEN}✓ Application launched (PID: $APP_PID)${NC}"

# Wait for window to appear
echo -e "${YELLOW}Waiting for main window...${NC}"
sleep 3

# Find window
WINDOW_ID=$(DISPLAY=$DISPLAY xdotool search --name "Personal Finance" | head -1 || echo "")
if [ -z "$WINDOW_ID" ]; then
    echo -e "${RED}✗ Could not find application window${NC}"
    kill $APP_PID 2>/dev/null || true
    [ -n "$XVFB_PID" ] && kill $XVFB_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✓ Main window found (ID: $WINDOW_ID)${NC}"
echo ""

# Try to activate window (may fail in Xvfb without window manager - that's OK)
echo -e "${YELLOW}Attempting to activate window...${NC}"
if DISPLAY=$DISPLAY xdotool windowactivate $WINDOW_ID 2>/dev/null; then
    echo -e "${GREEN}✓ Window activated${NC}"
else
    echo -e "${YELLOW}⚠ Window activation failed (expected in Xvfb) - continuing anyway${NC}"
fi
sleep 1
echo ""

# ============================================================================
# TEST 1: Capture Main Window with Search Panel
# ============================================================================
echo -e "${BLUE}Test 1: Main Window with Search Panel${NC}"
DISPLAY=$DISPLAY scrot "$SCREENSHOT_DIR/01-main-window-with-panel.png"
echo -e "${GREEN}✓ Screenshot captured: 01-main-window-with-panel.png${NC}"
echo "  Expected: Search panel visible above transaction list"
echo "  Expected: Panel has header with '🔍 Search & Filters' title"
echo "  Expected: Collapse button visible ('▼ Collapse')"
echo "  Expected: Text search row with search box"
echo "  Expected: Date/Category/Amount placeholder rows visible"
echo "  Expected: Footer with 'Clear All Filters' button (disabled)"
echo ""

# ============================================================================
# TEST 2: Enter Search Text
# ============================================================================
echo -e "${BLUE}Test 2: Enter Search Text${NC}"
echo -e "${YELLOW}Clicking search box...${NC}"

# Try to click search box (approximate coordinates - may need adjustment)
# The search box should be in the first row of the search panel
# Assuming panel is at ~y=100, search box at ~y=130
DISPLAY=$DISPLAY xdotool mousemove 500 150 click 1
sleep 0.5

echo -e "${YELLOW}Typing search text...${NC}"
DISPLAY=$DISPLAY xdotool type "test search"
sleep 0.5

DISPLAY=$DISPLAY scrot "$SCREENSHOT_DIR/02-search-text-entered.png"
echo -e "${GREEN}✓ Screenshot captured: 02-search-text-entered.png${NC}"
echo "  Expected: Search text 'test search' visible in search box"
echo "  Expected: Filter count updated to '1 filter active'"
echo "  Expected: 'Clear All Filters' button enabled (red)"
echo ""

# ============================================================================
# TEST 3: Test Collapse Functionality
# ============================================================================
echo -e "${BLUE}Test 3: Collapse Panel${NC}"
echo -e "${YELLOW}Clicking collapse button...${NC}"

# Try to click collapse button (top-right of panel)
# Approximate coordinates - may need adjustment
DISPLAY=$DISPLAY xdotool mousemove 950 100 click 1
sleep 0.5

DISPLAY=$DISPLAY scrot "$SCREENSHOT_DIR/03-panel-collapsed.png"
echo -e "${GREEN}✓ Screenshot captured: 03-panel-collapsed.png${NC}"
echo "  Expected: Filters container hidden"
echo "  Expected: Footer hidden"
echo "  Expected: Collapse button text changed to '▶ Expand'"
echo "  Expected: Filter count visible in header '(1 filter active)'"
echo ""

# ============================================================================
# TEST 4: Test Expand Functionality
# ============================================================================
echo -e "${BLUE}Test 4: Expand Panel${NC}"
echo -e "${YELLOW}Clicking expand button...${NC}"

DISPLAY=$DISPLAY xdotool mousemove 950 100 click 1
sleep 0.5

DISPLAY=$DISPLAY scrot "$SCREENSHOT_DIR/04-panel-expanded.png"
echo -e "${GREEN}✓ Screenshot captured: 04-panel-expanded.png${NC}"
echo "  Expected: Filters container visible again"
echo "  Expected: Footer visible again"
echo "  Expected: Button text back to '▼ Collapse'"
echo "  Expected: Header filter count hidden"
echo ""

# ============================================================================
# TEST 5: Test Clear All Functionality
# ============================================================================
echo -e "${BLUE}Test 5: Clear All Filters${NC}"
echo -e "${YELLOW}Clicking 'Clear All Filters' button...${NC}"

# Clear All button should be in footer (left side)
# Approximate coordinates - may need adjustment
DISPLAY=$DISPLAY xdotool mousemove 150 200 click 1
sleep 0.5

DISPLAY=$DISPLAY scrot "$SCREENSHOT_DIR/05-filters-cleared.png"
echo -e "${GREEN}✓ Screenshot captured: 05-filters-cleared.png${NC}"
echo "  Expected: Search box cleared (empty)"
echo "  Expected: Filter count reset to 0"
echo "  Expected: 'Clear All Filters' button disabled (gray)"
echo "  Expected: Filter count label hidden in footer"
echo "  Expected: Transaction list reloaded (all transactions)"
echo ""

# ============================================================================
# TEST 6: Test Keyboard Navigation (Tab Order)
# ============================================================================
echo -e "${BLUE}Test 6: Keyboard Navigation${NC}"
echo -e "${YELLOW}Testing Tab key navigation...${NC}"

# Click search box first
DISPLAY=$DISPLAY xdotool mousemove 500 150 click 1
sleep 0.3

# Press Tab 3 times (search → clear → collapse)
DISPLAY=$DISPLAY xdotool key Tab
sleep 0.3
DISPLAY=$DISPLAY scrot "$SCREENSHOT_DIR/06a-tab-navigation-step1.png"

DISPLAY=$DISPLAY xdotool key Tab
sleep 0.3
DISPLAY=$DISPLAY scrot "$SCREENSHOT_DIR/06b-tab-navigation-step2.png"

DISPLAY=$DISPLAY xdotool key Tab
sleep 0.3
DISPLAY=$DISPLAY scrot "$SCREENSHOT_DIR/06c-tab-navigation-step3.png"

echo -e "${GREEN}✓ Screenshots captured: 06a/b/c-tab-navigation.png${NC}"
echo "  Expected: Visual focus indicators on each element"
echo "  Expected: Tab order: search box → clear button → collapse button"
echo ""

# ============================================================================
# TEST 7: Test Placeholder Labels
# ============================================================================
echo -e "${BLUE}Test 7: Placeholder Labels${NC}"
echo -e "${YELLOW}Verifying future filter placeholders...${NC}"

# Zoom in on filters area if possible (just take screenshot)
DISPLAY=$DISPLAY scrot "$SCREENSHOT_DIR/07-placeholder-labels.png"
echo -e "${GREEN}✓ Screenshot captured: 07-placeholder-labels.png${NC}"
echo "  Expected: '[Date filter - US-012]' placeholder visible"
echo "  Expected: '[Category filter - US-013]' placeholder visible"
echo "  Expected: '[Amount filter - US-014]' placeholder visible"
echo "  Expected: Placeholders are italic and gray"
echo ""

# ============================================================================
# TEST 8: Test Responsive Behavior (Window Resize)
# ============================================================================
echo -e "${BLUE}Test 8: Responsive Behavior${NC}"
echo -e "${YELLOW}Resizing window...${NC}"

# Get current window size
WINDOW_INFO=$(DISPLAY=$DISPLAY xdotool getwindowgeometry $WINDOW_ID)
echo "  Original window info: $WINDOW_INFO"

# Resize to smaller width
DISPLAY=$DISPLAY xdotool windowsize $WINDOW_ID 800 600
sleep 0.5
DISPLAY=$DISPLAY scrot "$SCREENSHOT_DIR/08a-window-small.png"
echo -e "${GREEN}✓ Screenshot captured: 08a-window-small.png (800x600)${NC}"

# Resize to larger width
DISPLAY=$DISPLAY xdotool windowsize $WINDOW_ID 1400 800
sleep 0.5
DISPLAY=$DISPLAY scrot "$SCREENSHOT_DIR/08b-window-large.png"
echo -e "${GREEN}✓ Screenshot captured: 08b-window-large.png (1400x800)${NC}"

echo "  Expected: Panel expands/contracts with window"
echo "  Expected: No overlap or truncation"
echo "  Expected: Grid layout maintains alignment"
echo ""

# ============================================================================
# Cleanup
# ============================================================================
echo -e "${YELLOW}Cleaning up...${NC}"

# Kill application
if kill -0 $APP_PID 2>/dev/null; then
    kill $APP_PID 2>/dev/null
    sleep 1
    # Force kill if still running
    kill -9 $APP_PID 2>/dev/null || true
fi
echo -e "${GREEN}✓ Application stopped${NC}"

# Kill Xvfb if we started it
if [ -n "$XVFB_PID" ] && kill -0 $XVFB_PID 2>/dev/null; then
    kill $XVFB_PID 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✓ Xvfb stopped${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ US-016 UI Test Complete${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Display results summary
echo -e "${BLUE}📸 Screenshots Summary:${NC}"
echo ""
ls -lh "$SCREENSHOT_DIR" | grep -v "^total" | awk '{printf "  %s  %s\n", $9, $5}'
echo ""

echo -e "${YELLOW}📁 Screenshots saved to:${NC}"
echo "  $SCREENSHOT_DIR"
echo ""

echo -e "${YELLOW}🔍 Review screenshots with:${NC}"
echo "  cd $SCREENSHOT_DIR"
echo "  eog *.png  # Or your preferred image viewer"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Visual Validation Checklist:${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Review each screenshot and verify:"
echo ""
echo "✓ 01: Main window has search panel above transaction list"
echo "✓ 02: Search text visible, filter count = 1, Clear All enabled"
echo "✓ 03: Panel collapsed, button = '▶ Expand', header shows count"
echo "✓ 04: Panel expanded again, footer shows count"
echo "✓ 05: Search cleared, count = 0, Clear All disabled"
echo "✓ 06a/b/c: Focus indicators visible on each Tab press"
echo "✓ 07: Placeholder labels visible for US-012, 013, 014"
echo "✓ 08a/b: Panel responds to window resize"
echo ""

echo -e "${GREEN}Done! Review screenshots to validate UI implementation.${NC}"
echo ""

exit 0
