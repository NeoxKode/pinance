"""
Search Panel Widget for transaction filtering.

US-016: Search & Filter UI Panel - Foundation widget for all search and filter controls.
Provides a collapsible panel with organized filter rows for text search, date filters,
category filters, and amount filters. Designed for extensibility with future filter stories
(US-012, US-013, US-014).

Created: 2025-11-12
Story: US-016 - Search & Filter UI Panel (EPIC-002, Sprint 13)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Signal, Qt


class SearchPanelWidget(QWidget):
    """
    Container widget for transaction search and filter controls.

    US-016: Provides organized UI for all filter types with collapsible panel,
    active filter count display, and "Clear All" functionality. Designed for
    extensibility - future filter widgets integrate via setter methods.

    Features:
        - Collapsible panel (expand/collapse to save space)
        - Active filter count indicator ("2 filters active")
        - "Clear All Filters" button
        - Grid layout for clean label-widget alignment
        - Pre-defined rows for all future filters (US-012, 013, 014)
        - Signal-driven architecture for loose coupling

    Signals:
        search_changed(str): Emitted when text search changes (from US-011 widget)
        date_filter_changed(object): Emitted when date range changes (US-012)
        category_filter_changed(str): Emitted when category changes (US-013)
        amount_filter_changed(float, float): Emitted when amount range changes (US-014)
        filters_cleared(): Emitted when user clicks "Clear All Filters"

    Usage:
        >>> panel = SearchPanelWidget()
        >>> panel.set_text_search_widget(transaction_search_widget)  # US-011
        >>> panel.filters_cleared.connect(on_clear_all_handler)
        >>> panel.set_active_filter_count(2)  # Update count when filters change

    Design:
        - Width: Expands to fill parent container
        - Height: Adjusts based on collapsed state (~120px expanded, ~40px collapsed)
        - Background: Light gray (#f9f9f9) with border
        - Responsive: Works with window resize

    Architecture:
        ┌─────────────────────────────────────────────────────────┐
        │ [🔍 Search & Filters]  (2 active)  [▼ Collapse] ← Header│
        ├─────────────────────────────────────────────────────────┤
        │ Text:     [TransactionSearchWidget]        [X]          │ Row 0
        │ Date:     [Date filter - US-012]                        │ Row 1
        │ Category: [Category filter - US-013]                    │ Row 2
        │ Amount:   [Amount filter - US-014]                      │ Row 3
        ├─────────────────────────────────────────────────────────┤
        │ [Clear All Filters]                   2 filters active  │ Footer
        └─────────────────────────────────────────────────────────┘
    """

    # Signals for filter changes
    search_changed = Signal(str)                      # Text search keyword
    date_filter_changed = Signal(object)              # Date range object (US-012)
    category_filter_changed = Signal(str)             # Category name (US-013)
    amount_filter_changed = Signal(float, float)      # Min, max amount (US-014)
    filters_cleared = Signal()                        # Clear all filters action

    def __init__(self, parent=None):
        """
        Initialize search panel widget.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        # State variables
        self.is_collapsed = False                     # Panel expansion state
        self.active_filter_count = 0                  # Number of active filters
        self.text_search_widget = None                # US-011 widget reference

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """
        Create the widget user interface.

        Builds three-part layout:
        1. Header (title, filter count, collapse button)
        2. Filters container (grid layout with filter rows)
        3. Footer (Clear All button, filter count)
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self.header_widget = self._create_header()
        main_layout.addWidget(self.header_widget)

        # Filters container (collapsible)
        self.filters_container = self._create_filters_container()
        main_layout.addWidget(self.filters_container)

        # Footer
        self.footer_widget = self._create_footer()
        main_layout.addWidget(self.footer_widget)

        # Apply styling
        self._apply_styling()

    def _create_header(self) -> QFrame:
        """
        Create panel header with title, filter count, and collapse button.

        Returns:
            QFrame containing header layout
        """
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFrameShape(QFrame.StyledPanel)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Title label with icon
        title_label = QLabel("🔍 <b>Search & Filters</b>")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)

        # Filter count label (visible in collapsed mode)
        self.header_filter_count = QLabel("")
        self.header_filter_count.setObjectName("filterCountLabel")
        self.header_filter_count.hide()  # Hidden by default (shown when collapsed)
        layout.addWidget(self.header_filter_count)

        # Stretch to push collapse button to right
        layout.addStretch()

        # Collapse/Expand button
        self.collapse_button = QPushButton("▼ Collapse")
        self.collapse_button.setObjectName("collapseButton")
        self.collapse_button.setCursor(Qt.PointingHandCursor)
        self.collapse_button.setToolTip(
            "Collapse filter panel to save space\n"
            "Keyboard: Tab to focus, Enter to activate"
        )
        self.collapse_button.clicked.connect(self._toggle_collapse)

        # US-016 Task F4: Set explicit focus policy for keyboard navigation
        self.collapse_button.setFocusPolicy(Qt.TabFocus)

        layout.addWidget(self.collapse_button)

        return header

    def _create_filters_container(self) -> QFrame:
        """
        Create filters container with grid layout for all filter rows.

        Grid Layout:
            Column 0: Labels (fixed width)
            Column 1: Filter widgets (stretch)

        Rows:
            Row 0: Text search (US-011 integration)
            Row 1: Date filter (US-012 placeholder)
            Row 2: Category filter (US-013 placeholder)
            Row 3: Amount filter (US-014 placeholder)

        Returns:
            QFrame containing filters grid layout
        """
        container = QFrame()
        container.setObjectName("filtersContainer")
        container.setFrameShape(QFrame.StyledPanel)

        # Grid layout for clean alignment
        self.filters_layout = QGridLayout(container)
        self.filters_layout.setContentsMargins(12, 12, 12, 12)
        self.filters_layout.setHorizontalSpacing(12)
        self.filters_layout.setVerticalSpacing(10)
        self.filters_layout.setColumnStretch(0, 0)  # Labels: fixed width
        self.filters_layout.setColumnStretch(1, 1)  # Widgets: stretch

        # Row 0: Text search (US-011 integration)
        text_label = QLabel("Text:")
        text_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.filters_layout.addWidget(text_label, 0, 0)
        # US-011 widget will be added here via set_text_search_widget()

        # Row 1: Date filter (US-012 placeholder)
        date_label = QLabel("Date:")
        date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.filters_layout.addWidget(date_label, 1, 0)

        self.date_placeholder = QLabel("<i>[Date filter - US-012]</i>")
        self.date_placeholder.setObjectName("placeholderLabel")
        self.date_placeholder.setToolTip("Date range filter will be added in Sprint 14 (US-012)")
        self.filters_layout.addWidget(self.date_placeholder, 1, 1)

        # Row 2: Category filter (US-013 placeholder)
        category_label = QLabel("Category:")
        category_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.filters_layout.addWidget(category_label, 2, 0)

        self.category_placeholder = QLabel("<i>[Category filter - US-013]</i>")
        self.category_placeholder.setObjectName("placeholderLabel")
        self.category_placeholder.setToolTip("Category filter will be added in Sprint 14 (US-013)")
        self.filters_layout.addWidget(self.category_placeholder, 2, 1)

        # Row 3: Amount filter (US-014 placeholder)
        amount_label = QLabel("Amount:")
        amount_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.filters_layout.addWidget(amount_label, 3, 0)

        self.amount_placeholder = QLabel("<i>[Amount filter - US-014]</i>")
        self.amount_placeholder.setObjectName("placeholderLabel")
        self.amount_placeholder.setToolTip("Amount range filter will be added in Sprint 15 (US-014)")
        self.filters_layout.addWidget(self.amount_placeholder, 3, 1)

        return container

    def _create_footer(self) -> QFrame:
        """
        Create panel footer with Clear All button and active filter count.

        Returns:
            QFrame containing footer layout
        """
        footer = QFrame()
        footer.setObjectName("footerFrame")
        footer.setFrameShape(QFrame.StyledPanel)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Clear All Filters button
        self.clear_all_button = QPushButton("Clear All Filters")
        self.clear_all_button.setObjectName("clearAllButton")
        self.clear_all_button.setCursor(Qt.PointingHandCursor)
        self.clear_all_button.setToolTip(
            "Clear all active filters and show all transactions\n"
            "Keyboard: Tab to focus, Enter to activate"
        )
        self.clear_all_button.setEnabled(False)  # Disabled when no filters active
        self.clear_all_button.clicked.connect(self._on_clear_all)

        # US-016 Task F4: Set explicit focus policy for keyboard navigation
        self.clear_all_button.setFocusPolicy(Qt.TabFocus)

        layout.addWidget(self.clear_all_button)

        # Stretch to push filter count to right
        layout.addStretch()

        # Active filter count label
        self.footer_filter_count = QLabel("")
        self.footer_filter_count.setObjectName("filterCountLabel")
        self.footer_filter_count.hide()  # Hidden when count is 0
        layout.addWidget(self.footer_filter_count)

        return footer

    def _toggle_collapse(self):
        """
        Toggle panel collapsed/expanded state.

        Collapsed State:
            - Hides filters container and footer
            - Shows filter count in header (if > 0)
            - Changes button text to "▶ Expand"

        Expanded State:
            - Shows filters container and footer
            - Hides filter count in header
            - Changes button text to "▼ Collapse"
        """
        self.is_collapsed = not self.is_collapsed

        if self.is_collapsed:
            # Collapse: Hide filters and footer
            self.filters_container.hide()
            self.footer_widget.hide()

            # Update button
            self.collapse_button.setText("▶ Expand")
            self.collapse_button.setToolTip("Expand filter panel")

            # Show filter count in header (if active filters exist)
            if self.active_filter_count > 0:
                self.header_filter_count.show()
        else:
            # Expand: Show filters and footer
            self.filters_container.show()
            self.footer_widget.show()

            # Update button
            self.collapse_button.setText("▼ Collapse")
            self.collapse_button.setToolTip("Collapse filter panel to save space")

            # Hide filter count in header
            self.header_filter_count.hide()

    def set_text_search_widget(self, widget):
        """
        Set text search widget (US-011 integration).

        Adds the TransactionSearchWidget to the grid layout at Row 0, Column 1.
        Connects the widget's search_changed signal to internal handler for
        filter count updates.

        Args:
            widget: TransactionSearchWidget instance from US-011

        Usage:
            >>> panel = SearchPanelWidget()
            >>> search_widget = TransactionSearchWidget()
            >>> panel.set_text_search_widget(search_widget)
        """
        # Store reference
        self.text_search_widget = widget

        # Add to grid layout (Row 0, Column 1)
        self.filters_layout.addWidget(widget, 0, 1)

        # Connect signal for filter count updates
        widget.search_changed.connect(self._on_filter_changed)

        # US-016 Task F4: Configure tab order after search widget is added
        self._configure_tab_order()

    def set_active_filter_count(self, count: int):
        """
        Update active filter count display.

        Updates both header and footer labels with current filter count.
        Handles singular/plural ("1 filter" vs "2 filters").
        Shows/hides labels based on count (hidden when 0).
        Enables/disables "Clear All" button based on count.

        Args:
            count: Number of active filters (0 or more)

        State Changes:
            - count == 0: Hides labels, disables Clear All button
            - count == 1: Shows "1 filter active" (singular)
            - count >= 2: Shows "N filters active" (plural)
        """
        self.active_filter_count = count

        if count == 0:
            # No filters: Hide labels, disable button
            self.header_filter_count.hide()
            self.footer_filter_count.hide()
            self.clear_all_button.setEnabled(False)
        else:
            # Format text (singular/plural)
            filter_text = "1 filter active" if count == 1 else f"{count} filters active"

            # Update labels
            self.header_filter_count.setText(f"({filter_text})")
            self.footer_filter_count.setText(filter_text)

            # Show/hide based on collapsed state
            if self.is_collapsed:
                self.header_filter_count.show()
                self.footer_filter_count.hide()  # Footer hidden when collapsed
            else:
                self.header_filter_count.hide()  # Header count hidden when expanded
                self.footer_filter_count.show()

            # Enable Clear All button
            self.clear_all_button.setEnabled(True)

    def _on_filter_changed(self):
        """
        Handle filter change from any filter widget.

        Called when a filter value changes (e.g., text search keyword entered).
        Counts active filters and updates the display.

        Active Filter Rules:
            - Text search: Active if search text is not empty
            - Date filter: Active if date range is set (US-012)
            - Category filter: Active if category is selected (US-013)
            - Amount filter: Active if min or max is set (US-014)

        Note: Currently only handles text search (US-011). Future stories
        (US-012, 013, 014) will add additional filter count logic.
        """
        count = 0

        # Count text search filter (US-011)
        if self.text_search_widget and self.text_search_widget.get_text():
            count += 1

        # TODO: US-012 - Count date filter if set
        # TODO: US-013 - Count category filter if selected
        # TODO: US-014 - Count amount filter if min/max set

        # Update display
        self.set_active_filter_count(count)

    def _on_clear_all(self):
        """
        Handle Clear All Filters button click.

        Clears all active filters by:
        1. Clearing text search widget (US-011)
        2. Emitting filters_cleared signal for MainWindow to reload data
        3. Resetting filter count to 0

        Signal Flow:
            SearchPanelWidget.filters_cleared
                ↓
            MainWindow._on_filters_cleared()
                ↓
            Reload all transactions (no filters)
        """
        # Clear text search widget (US-011)
        if self.text_search_widget:
            self.text_search_widget.clear()

        # TODO: US-012 - Clear date filter
        # TODO: US-013 - Clear category filter
        # TODO: US-014 - Clear amount filter

        # Emit signal for MainWindow to reload data
        self.filters_cleared.emit()

        # Reset filter count
        self.set_active_filter_count(0)

    def _configure_tab_order(self):
        """
        Configure keyboard tab order for accessibility (US-016 Task F4).

        Tab Order:
            1. Search box (text_search_widget) - primary interaction
            2. Clear All button - secondary action
            3. Collapse button - tertiary action

        This ensures logical keyboard navigation where users can:
        - Tab into search box to start filtering
        - Tab to Clear All to reset filters
        - Tab to Collapse to minimize panel

        Note: QWidget.setTabOrder() sets the order between two widgets.
        Call this after text_search_widget is set.
        """
        if not self.text_search_widget:
            # No search widget yet, tab order is just: Clear All → Collapse
            self.setTabOrder(self.clear_all_button, self.collapse_button)
            return

        # Search widget has its own internal focus chain (QLineEdit inside)
        # We need to link from search widget to our buttons

        # Tab order: search_widget → clear_all_button → collapse_button
        self.setTabOrder(self.text_search_widget, self.clear_all_button)
        self.setTabOrder(self.clear_all_button, self.collapse_button)

    def _apply_styling(self):
        """
        Apply QSS styling to panel and child widgets.

        Styling includes:
        - Panel background and border
        - Header/Footer backgrounds
        - Button styles (collapse, clear all)
        - Label colors and fonts
        - Focus indicators for accessibility
        """
        self.setStyleSheet("""
            /* Panel container */
            SearchPanelWidget {
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }

            /* Header frame */
            QFrame#headerFrame {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
            }

            /* Filters container */
            QFrame#filtersContainer {
                background-color: white;
            }

            /* Footer frame */
            QFrame#footerFrame {
                background-color: #fafafa;
                border-top: 1px solid #e0e0e0;
            }

            /* Title label */
            QLabel#titleLabel {
                font-size: 14px;
                color: #333;
            }

            /* Filter count labels */
            QLabel#filterCountLabel {
                color: #666;
                font-size: 12px;
            }

            /* Placeholder labels */
            QLabel#placeholderLabel {
                color: #999;
                font-size: 12px;
            }

            /* Collapse button */
            QPushButton#collapseButton {
                border: none;
                background-color: transparent;
                color: #2196F3;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
            }

            QPushButton#collapseButton:hover {
                background-color: #E3F2FD;
            }

            QPushButton#collapseButton:pressed {
                background-color: #BBDEFB;
            }

            QPushButton#collapseButton:focus {
                border: 2px solid #2196F3;
                outline: 2px solid #93C5FD;
                outline-offset: 2px;
            }

            /* Clear All button */
            QPushButton#clearAllButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton#clearAllButton:hover {
                background-color: #d32f2f;
            }

            QPushButton#clearAllButton:pressed {
                background-color: #b71c1c;
            }

            QPushButton#clearAllButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }

            QPushButton#clearAllButton:focus {
                border: 2px solid #2196F3;
                outline: 2px solid #93C5FD;
                outline-offset: 2px;
            }
        """)
