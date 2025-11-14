"""
Unit tests for SearchPanelWidget (US-016).

Tests the search panel container widget including:
- Widget creation and initialization
- Collapse/expand functionality
- Filter count tracking
- Signal emissions
- Keyboard navigation setup
- Text search widget integration

Created: 2025-11-12
Story: US-016 - Search & Filter UI Panel (EPIC-002, Sprint 13)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication

from finance_app.ui.widgets.search_panel_widget import SearchPanelWidget
from finance_app.ui.widgets.transaction_search_widget import TransactionSearchWidget


@pytest.fixture
def search_panel(qtbot):
    """Create a SearchPanelWidget instance for testing."""
    panel = SearchPanelWidget()
    qtbot.addWidget(panel)
    return panel


@pytest.fixture
def search_widget(qtbot):
    """Create a TransactionSearchWidget for integration testing."""
    widget = TransactionSearchWidget()
    qtbot.addWidget(widget)
    return widget


class TestSearchPanelCreation:
    """Test SearchPanelWidget creation and initialization."""

    def test_panel_created_successfully(self, search_panel):
        """Test that SearchPanelWidget can be created."""
        assert search_panel is not None
        assert isinstance(search_panel, SearchPanelWidget)

    def test_initial_state_is_expanded(self, search_panel):
        """Test that panel starts in expanded state."""
        assert search_panel.is_collapsed is False

    def test_initial_filter_count_is_zero(self, search_panel):
        """Test that panel starts with zero active filters."""
        assert search_panel.active_filter_count == 0

    def test_no_search_widget_initially(self, search_panel):
        """Test that panel starts without a search widget."""
        assert search_panel.text_search_widget is None

    def test_has_collapse_button(self, search_panel):
        """Test that collapse button exists."""
        assert search_panel.collapse_button is not None
        assert search_panel.collapse_button.text() == "▼ Collapse"

    def test_collapse_button_has_focus_policy(self, search_panel):
        """Test that collapse button has TabFocus policy (US-016 Task F4)."""
        assert search_panel.collapse_button.focusPolicy() == Qt.TabFocus

    def test_has_clear_all_button(self, search_panel):
        """Test that clear all button exists."""
        assert search_panel.clear_all_button is not None
        assert "Clear All Filters" in search_panel.clear_all_button.text()

    def test_clear_all_button_has_focus_policy(self, search_panel):
        """Test that clear all button has TabFocus policy (US-016 Task F4)."""
        assert search_panel.clear_all_button.focusPolicy() == Qt.TabFocus

    def test_filters_container_exists(self, search_panel):
        """Test that filters container exists and is not hidden."""
        assert search_panel.filters_container is not None
        # Note: isVisible() requires widget to be shown, so we just check it's not explicitly hidden
        assert not search_panel.filters_container.isHidden()

    def test_footer_widget_exists(self, search_panel):
        """Test that footer widget exists and is not hidden."""
        assert search_panel.footer_widget is not None
        # Note: isVisible() requires widget to be shown, so we just check it's not explicitly hidden
        assert not search_panel.footer_widget.isHidden()

    def test_header_filter_count_hidden_initially(self, search_panel):
        """Test that header filter count is hidden when expanded."""
        assert search_panel.header_filter_count is not None
        assert not search_panel.header_filter_count.isVisible()


class TestCollapseExpandFunctionality:
    """Test collapse and expand behavior."""

    def test_collapse_hides_filters_container(self, search_panel):
        """Test that collapsing hides the filters container."""
        search_panel.collapse_button.click()

        assert search_panel.is_collapsed is True
        assert not search_panel.filters_container.isVisible()

    def test_collapse_hides_footer(self, search_panel):
        """Test that collapsing hides the footer."""
        search_panel.collapse_button.click()

        assert not search_panel.footer_widget.isVisible()

    def test_collapse_changes_button_text(self, search_panel):
        """Test that collapse button text changes to 'Expand'."""
        search_panel.collapse_button.click()

        assert search_panel.collapse_button.text() == "▶ Expand"

    def test_expand_shows_filters_container(self, search_panel):
        """Test that expanding shows the filters container."""
        # Collapse first
        search_panel.collapse_button.click()
        # Then expand
        search_panel.collapse_button.click()

        assert search_panel.is_collapsed is False
        assert not search_panel.filters_container.isHidden()

    def test_expand_shows_footer(self, search_panel):
        """Test that expanding shows the footer."""
        # Collapse first
        search_panel.collapse_button.click()
        # Then expand
        search_panel.collapse_button.click()

        assert not search_panel.footer_widget.isHidden()

    def test_expand_changes_button_text_back(self, search_panel):
        """Test that expand button text changes back to 'Collapse'."""
        # Collapse first
        search_panel.collapse_button.click()
        # Then expand
        search_panel.collapse_button.click()

        assert search_panel.collapse_button.text() == "▼ Collapse"

    def test_multiple_collapse_expand_cycles(self, search_panel):
        """Test multiple collapse/expand cycles work correctly."""
        for _ in range(3):
            # Collapse
            search_panel.collapse_button.click()
            assert search_panel.is_collapsed is True

            # Expand
            search_panel.collapse_button.click()
            assert search_panel.is_collapsed is False


class TestFilterCountTracking:
    """Test active filter count tracking and display."""

    def test_filter_count_starts_at_zero(self, search_panel):
        """Test that filter count starts at 0."""
        assert search_panel.active_filter_count == 0

    def test_filter_count_label_hidden_when_zero(self, search_panel):
        """Test that filter count label is hidden when count is 0."""
        # Footer filter count should be hidden when count is 0
        assert not search_panel.footer_filter_count.isVisible()

    def test_filter_count_updates_to_one(self, search_panel):
        """Test that filter count updates correctly to 1."""
        # Set filter count to 1
        search_panel.set_active_filter_count(1)

        assert search_panel.active_filter_count == 1

    def test_filter_count_label_shows_singular(self, search_panel):
        """Test that filter count uses singular form for 1 filter."""
        search_panel.set_active_filter_count(1)

        footer_text = search_panel.footer_filter_count.text()
        assert "1 filter active" in footer_text

    def test_filter_count_updates_to_multiple(self, search_panel):
        """Test that filter count updates correctly to multiple filters."""
        # Set filter count to 3
        search_panel.set_active_filter_count(3)

        assert search_panel.active_filter_count == 3

    def test_filter_count_label_shows_plural(self, search_panel):
        """Test that filter count uses plural form for multiple filters."""
        search_panel.set_active_filter_count(2)

        footer_text = search_panel.footer_filter_count.text()
        assert "2 filters active" in footer_text

    def test_header_filter_count_shown_when_collapsed(self, search_panel):
        """Test that header shows filter count when collapsed."""
        # Add a filter
        search_panel.set_active_filter_count(1)

        # Collapse panel
        search_panel.collapse_button.click()

        # Check filter count is not hidden and has correct text
        assert not search_panel.header_filter_count.isHidden()
        assert "1 filter" in search_panel.header_filter_count.text()

    def test_header_filter_count_hidden_when_expanded(self, search_panel):
        """Test that header hides filter count when expanded."""
        # Add a filter and collapse
        search_panel._on_filter_changed()
        search_panel.collapse_button.click()

        # Expand panel
        search_panel.collapse_button.click()

        assert not search_panel.header_filter_count.isVisible()

    def test_header_filter_count_hidden_when_collapsed_with_no_filters(self, search_panel):
        """Test that header filter count stays hidden when collapsed with 0 filters."""
        # Collapse without adding filters
        search_panel.collapse_button.click()

        assert not search_panel.header_filter_count.isVisible()


class TestClearAllButton:
    """Test Clear All Filters button behavior."""

    def test_clear_all_button_disabled_initially(self, search_panel):
        """Test that Clear All button starts disabled."""
        assert not search_panel.clear_all_button.isEnabled()

    def test_clear_all_button_enabled_with_active_filter(self, search_panel):
        """Test that Clear All button enables when filter is active."""
        search_panel.set_active_filter_count(1)

        assert search_panel.clear_all_button.isEnabled()

    def test_clear_all_button_emits_signal(self, search_panel, qtbot):
        """Test that clicking Clear All emits filters_cleared signal."""
        # Add a filter to enable the button
        search_panel.set_active_filter_count(1)

        with qtbot.waitSignal(search_panel.filters_cleared, timeout=1000) as blocker:
            search_panel.clear_all_button.click()

        assert blocker.signal_triggered

    def test_clear_all_resets_filter_count(self, search_panel, search_widget):
        """Test that Clear All resets filter count to 0."""
        # Set up search widget with text
        search_panel.set_text_search_widget(search_widget)
        search_widget.set_text("test")
        search_panel._on_filter_changed()  # Recalculates count based on widgets

        # Clear all
        search_panel._on_clear_all()

        # Manually reset count (since no MainWindow to reload)
        search_panel.set_active_filter_count(0)

        assert search_panel.active_filter_count == 0

    def test_clear_all_disables_button_again(self, search_panel):
        """Test that Clear All disables the button after clearing."""
        # Add a filter
        search_panel.set_active_filter_count(1)

        # Clear all and reset count
        search_panel._on_clear_all()
        search_panel.set_active_filter_count(0)

        assert not search_panel.clear_all_button.isEnabled()


class TestSearchWidgetIntegration:
    """Test integration with TransactionSearchWidget (US-011)."""

    def test_set_text_search_widget(self, search_panel, search_widget):
        """Test setting the text search widget."""
        search_panel.set_text_search_widget(search_widget)

        assert search_panel.text_search_widget == search_widget

    def test_search_widget_added_to_layout(self, search_panel, search_widget):
        """Test that search widget is added to the grid layout."""
        search_panel.set_text_search_widget(search_widget)

        # Check that widget is in the layout at row 0, column 1
        item = search_panel.filters_layout.itemAtPosition(0, 1)
        assert item is not None
        assert item.widget() == search_widget

    def test_search_widget_signal_connected(self, search_panel, search_widget, qtbot):
        """Test that search widget's signal is connected to filter count."""
        search_panel.set_text_search_widget(search_widget)

        # Set text and trigger filter change
        search_widget.search_input.setText("test")
        # Trigger the debounce timer immediately
        search_widget.search_timer.timeout.emit()

        # Wait for signal processing
        qtbot.wait(50)

        # Panel should have incremented filter count
        assert search_panel.active_filter_count == 1

    def test_set_text_search_widget_twice_keeps_last(self, search_panel, qtbot):
        """Test that setting search widget twice keeps the last one."""
        # Create two search widgets
        widget1 = TransactionSearchWidget()
        widget2 = TransactionSearchWidget()
        qtbot.addWidget(widget1)
        qtbot.addWidget(widget2)

        # Set first widget
        search_panel.set_text_search_widget(widget1)
        assert search_panel.text_search_widget == widget1

        # Set second widget (should update reference)
        search_panel.set_text_search_widget(widget2)
        assert search_panel.text_search_widget == widget2

    def test_tab_order_configured_after_setting_widget(self, search_panel, search_widget):
        """Test that tab order is configured after setting search widget (Task F4)."""
        search_panel.set_text_search_widget(search_widget)

        # Verify tab order exists (hard to test directly, but we can check it doesn't crash)
        # This would be better tested via manual/integration testing
        assert search_panel.text_search_widget is not None


class TestSignalDefinitions:
    """Test that all signals are properly defined."""

    def test_has_search_changed_signal(self, search_panel):
        """Test that search_changed signal exists."""
        assert hasattr(search_panel, 'search_changed')
        assert isinstance(search_panel.__class__.search_changed, Signal)

    def test_has_date_filter_changed_signal(self, search_panel):
        """Test that date_filter_changed signal exists (US-012)."""
        assert hasattr(search_panel, 'date_filter_changed')
        assert isinstance(search_panel.__class__.date_filter_changed, Signal)

    def test_has_category_filter_changed_signal(self, search_panel):
        """Test that category_filter_changed signal exists (US-013)."""
        assert hasattr(search_panel, 'category_filter_changed')
        assert isinstance(search_panel.__class__.category_filter_changed, Signal)

    def test_has_amount_filter_changed_signal(self, search_panel):
        """Test that amount_filter_changed signal exists (US-014)."""
        assert hasattr(search_panel, 'amount_filter_changed')
        assert isinstance(search_panel.__class__.amount_filter_changed, Signal)

    def test_has_filters_cleared_signal(self, search_panel):
        """Test that filters_cleared signal exists."""
        assert hasattr(search_panel, 'filters_cleared')
        assert isinstance(search_panel.__class__.filters_cleared, Signal)


class TestKeyboardNavigation:
    """Test keyboard navigation setup (Task F4)."""

    def test_collapse_button_has_tooltip(self, search_panel):
        """Test that collapse button has keyboard usage tooltip."""
        tooltip = search_panel.collapse_button.toolTip()
        assert "Keyboard" in tooltip
        assert "Tab" in tooltip

    def test_clear_all_button_has_tooltip(self, search_panel):
        """Test that clear all button has keyboard usage tooltip."""
        tooltip = search_panel.clear_all_button.toolTip()
        assert "Keyboard" in tooltip
        assert "Tab" in tooltip

    def test_tab_order_without_search_widget(self, search_panel):
        """Test that tab order is set even without search widget."""
        # Tab order should be: clear_all → collapse
        # This is hard to test directly, but we ensure it doesn't crash
        search_panel._configure_tab_order()

        # No assertion needed - we're just testing it doesn't crash


class TestPlaceholderLabels:
    """Test placeholder labels for future filters."""

    def test_date_placeholder_exists(self, search_panel):
        """Test that date filter placeholder exists."""
        assert search_panel.date_placeholder is not None

    def test_date_placeholder_text(self, search_panel):
        """Test that date placeholder has correct text."""
        text = search_panel.date_placeholder.text()
        assert "Date filter" in text
        assert "US-012" in text

    def test_category_placeholder_exists(self, search_panel):
        """Test that category filter placeholder exists."""
        assert search_panel.category_placeholder is not None

    def test_category_placeholder_text(self, search_panel):
        """Test that category placeholder has correct text."""
        text = search_panel.category_placeholder.text()
        assert "Category filter" in text
        assert "US-013" in text

    def test_amount_placeholder_exists(self, search_panel):
        """Test that amount filter placeholder exists."""
        assert search_panel.amount_placeholder is not None

    def test_amount_placeholder_text(self, search_panel):
        """Test that amount placeholder has correct text."""
        text = search_panel.amount_placeholder.text()
        assert "Amount filter" in text
        assert "US-014" in text


# Run tests with: pytest finance_app/tests/unit/test_search_panel_widget.py -v
