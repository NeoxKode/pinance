"""
Search Panel Widget for transaction filtering.

US-016: Search & Filter UI Panel - Foundation widget for all search and filter controls.
Provides a collapsible panel with organized filter rows for text search, date filters,
category filters, and amount filters. Designed for extensibility with future filter stories
(US-012, US-013, US-014).

Created: 2025-11-12
Story: US-016 - Search & Filter UI Panel (EPIC-002, Sprint 13)
"""

from datetime import date
from decimal import Decimal

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QComboBox, QDialog, QLineEdit, QCheckBox
)
from PySide6.QtCore import Signal, Qt, QTimer

from finance_app.business.date_range_utils import DateRange
from finance_app.ui.dialogs import DateRangeDialog


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
    date_filter_changed = Signal(object, object)      # from_date, to_date (US-012)
    category_filter_changed = Signal(list)            # Category names list (US-013)
    amount_filter_changed = Signal(object, object, bool)  # min_amount (Decimal), max_amount (Decimal), absolute (bool) (US-014)
    filters_cleared = Signal()                        # Clear all filters action
    saved_filter_selected = Signal(int)               # Saved filter ID selected for loading (US-015)
    save_current_filters_requested = Signal()         # User clicked "Save Current Filters" (US-015)
    manage_filters_requested = Signal()               # User clicked "Manage Filters" (US-015)

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

        # US-012: Date filter state
        self.current_date_from = None                 # Current from_date filter
        self.current_date_to = None                   # Current to_date filter

        # US-013: Category filter state
        self.current_categories = []                  # Current selected categories
        self.transaction_service = None               # Service for loading categories

        # US-014: Amount filter state
        self.current_amount_min = None                # Current min amount filter
        self.current_amount_max = None                # Current max amount filter
        self.current_amount_absolute = False          # Absolute value mode
        self.amount_debounce_timer = QTimer()         # Debounce timer for text input
        self.amount_debounce_timer.setSingleShot(True)
        self.amount_debounce_timer.setInterval(500)   # 500ms debounce
        self.amount_debounce_timer.timeout.connect(self._emit_amount_filter)

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

        # Row 1: Date filter (US-012 implementation)
        date_label = QLabel("Date:")
        date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.filters_layout.addWidget(date_label, 1, 0)

        # Date dropdown with presets
        self.date_combo = QComboBox()
        self.date_combo.setMinimumWidth(200)
        self.date_combo.setToolTip("Filter transactions by date range")
        self._populate_date_presets()
        self.date_combo.currentTextChanged.connect(self._on_date_preset_changed)
        self.filters_layout.addWidget(self.date_combo, 1, 1)

        # Row 2: Category filter (US-013 implementation)
        category_label = QLabel("Category:")
        category_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.filters_layout.addWidget(category_label, 2, 0)

        # Category dropdown
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(200)
        self.category_combo.setToolTip("Filter transactions by category")
        self.category_combo.addItem("All Categories")  # Default option
        self.category_combo.currentTextChanged.connect(self._on_category_changed)
        self.filters_layout.addWidget(self.category_combo, 2, 1)

        # Row 3: Amount filter (US-014 implementation)
        amount_label = QLabel("Amount:")
        amount_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.filters_layout.addWidget(amount_label, 3, 0)

        # Amount filter widget (inputs + absolute checkbox)
        amount_widget = self._create_amount_filter_widget()
        self.filters_layout.addWidget(amount_widget, 3, 1)

        # Row 4: Amount presets (US-014)
        presets_label = QLabel("")  # Empty label for alignment
        self.filters_layout.addWidget(presets_label, 4, 0)

        # Preset buttons
        presets_widget = self._create_amount_presets_widget()
        self.filters_layout.addWidget(presets_widget, 4, 1)

        # Row 5: Saved Filters (US-015)
        saved_label = QLabel("Saved:")
        saved_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.filters_layout.addWidget(saved_label, 5, 0)

        # Saved filters widget (dropdown + buttons)
        saved_widget = self._create_saved_filters_widget()
        self.filters_layout.addWidget(saved_widget, 5, 1)

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

    def _create_amount_filter_widget(self) -> QWidget:
        """
        Create amount filter input widget (US-014).

        Returns:
            QWidget containing min/max inputs and absolute checkbox

        Layout:
            [Min: $____] to [Max: $____] [✓ Absolute Value]
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Min amount input
        min_label = QLabel("Min:")
        layout.addWidget(min_label)

        self.amount_min_input = QLineEdit()
        self.amount_min_input.setPlaceholderText("$0.00")
        self.amount_min_input.setMaximumWidth(100)
        self.amount_min_input.setToolTip(
            "Minimum amount (e.g., 100, $50.99, 1,234.56)\n"
            "Leave empty for no minimum"
        )
        self.amount_min_input.textChanged.connect(self._on_amount_input_changed)
        layout.addWidget(self.amount_min_input)

        # "to" separator
        to_label = QLabel("to")
        layout.addWidget(to_label)

        # Max amount input
        max_label = QLabel("Max:")
        layout.addWidget(max_label)

        self.amount_max_input = QLineEdit()
        self.amount_max_input.setPlaceholderText("$999,999.99")
        self.amount_max_input.setMaximumWidth(100)
        self.amount_max_input.setToolTip(
            "Maximum amount (e.g., 500, $1,000.00)\n"
            "Leave empty for no maximum"
        )
        self.amount_max_input.textChanged.connect(self._on_amount_input_changed)
        layout.addWidget(self.amount_max_input)

        # Absolute value checkbox
        self.amount_absolute_checkbox = QCheckBox("Absolute Value")
        self.amount_absolute_checkbox.setToolTip(
            "Filter by absolute value (ignores +/- sign)\n"
            "Useful for finding 'any transaction over $100' regardless of income/expense"
        )
        self.amount_absolute_checkbox.stateChanged.connect(self._on_amount_absolute_changed)
        layout.addWidget(self.amount_absolute_checkbox)

        # Stretch to push everything left
        layout.addStretch()

        return widget

    def _create_amount_presets_widget(self) -> QWidget:
        """
        Create amount filter preset buttons (US-014).

        Returns:
            QWidget containing 4 preset buttons

        Buttons:
            - "< $20" (Small Charges)
            - "$20-$100" (Mid-range)
            - "> $100" (Large)
            - "> $500" (Very Large)
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Preset buttons
        self.preset_small_btn = QPushButton("< $20")
        self.preset_small_btn.setObjectName("amountPresetButton")
        self.preset_small_btn.setToolTip("Small charges (subscriptions, coffee)")
        self.preset_small_btn.setCursor(Qt.PointingHandCursor)
        self.preset_small_btn.clicked.connect(lambda: self._apply_amount_preset(None, Decimal("20"), True))
        layout.addWidget(self.preset_small_btn)

        self.preset_mid_btn = QPushButton("$20-$100")
        self.preset_mid_btn.setObjectName("amountPresetButton")
        self.preset_mid_btn.setToolTip("Mid-range purchases (groceries, gas)")
        self.preset_mid_btn.setCursor(Qt.PointingHandCursor)
        self.preset_mid_btn.clicked.connect(lambda: self._apply_amount_preset(Decimal("20"), Decimal("100"), True))
        layout.addWidget(self.preset_mid_btn)

        self.preset_large_btn = QPushButton("> $100")
        self.preset_large_btn.setObjectName("amountPresetButton")
        self.preset_large_btn.setToolTip("Large purchases (electronics, rent)")
        self.preset_large_btn.setCursor(Qt.PointingHandCursor)
        self.preset_large_btn.clicked.connect(lambda: self._apply_amount_preset(Decimal("100"), None, True))
        layout.addWidget(self.preset_large_btn)

        self.preset_very_large_btn = QPushButton("> $500")
        self.preset_very_large_btn.setObjectName("amountPresetButton")
        self.preset_very_large_btn.setToolTip("Very large purchases (furniture, appliances)")
        self.preset_very_large_btn.setCursor(Qt.PointingHandCursor)
        self.preset_very_large_btn.clicked.connect(lambda: self._apply_amount_preset(Decimal("500"), None, True))
        layout.addWidget(self.preset_very_large_btn)

        # Stretch to push buttons left
        layout.addStretch()

        return widget

    def _create_saved_filters_widget(self) -> QWidget:
        """
        Create saved filters widget (US-015).

        Returns:
            QWidget containing saved filters dropdown and action buttons

        Layout:
            [Dropdown: Select saved filter...] [💾 Save] [⚙️ Manage...]

        US-015: Allows users to:
        - Select and load saved filters from dropdown
        - Save current filter state
        - Manage existing saved filters
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Saved filters dropdown
        self.saved_filters_combo = QComboBox()
        self.saved_filters_combo.setMinimumWidth(250)
        self.saved_filters_combo.setToolTip("Load a saved filter combination")
        self.saved_filters_combo.addItem("-- Select saved filter --", None)  # Default placeholder
        self.saved_filters_combo.currentIndexChanged.connect(self._on_saved_filter_selected)
        layout.addWidget(self.saved_filters_combo)

        # Save button
        self.save_filter_btn = QPushButton("💾 Save")
        self.save_filter_btn.setObjectName("saveFilterButton")
        self.save_filter_btn.setToolTip("Save current filters for quick access later")
        self.save_filter_btn.setCursor(Qt.PointingHandCursor)
        self.save_filter_btn.clicked.connect(self._on_save_filter_clicked)
        layout.addWidget(self.save_filter_btn)

        # Manage button
        self.manage_filters_btn = QPushButton("⚙️ Manage...")
        self.manage_filters_btn.setToolTip("Edit, delete, or favorite saved filters")
        self.manage_filters_btn.setCursor(Qt.PointingHandCursor)
        self.manage_filters_btn.clicked.connect(self._on_manage_filters_clicked)
        layout.addWidget(self.manage_filters_btn)

        # Stretch to push buttons left
        layout.addStretch()

        return widget

    def _on_saved_filter_selected(self, index: int):
        """
        Handle saved filter selection from dropdown.

        Args:
            index: Selected index in combo box
        """
        if index <= 0:  # Skip placeholder item
            return

        # Get filter ID from item data
        filter_id = self.saved_filters_combo.itemData(index)
        if filter_id is not None:
            # Emit signal to load this filter
            self.saved_filter_selected.emit(filter_id)

    def _on_save_filter_clicked(self):
        """Handle Save Current Filters button click."""
        self.save_current_filters_requested.emit()

    def _on_manage_filters_clicked(self):
        """Handle Manage Filters button click."""
        self.manage_filters_requested.emit()

    def populate_saved_filters(self, saved_filters: list):
        """
        Populate the saved filters dropdown.

        Args:
            saved_filters: List of SavedFilter objects

        US-015: Called by MainWindow when filters are loaded from database.
        Favorites are shown first with a star icon.
        """
        # Store current selection to restore if possible
        current_id = self.saved_filters_combo.currentData()

        # Clear and repopulate
        self.saved_filters_combo.clear()
        self.saved_filters_combo.addItem("-- Select saved filter --", None)

        if not saved_filters:
            return

        # Sort: favorites first, then alphabetically
        sorted_filters = sorted(
            saved_filters,
            key=lambda f: (not f.is_favorite, f.name.lower())
        )

        for filter_obj in sorted_filters:
            # Add star for favorites
            display_name = f"⭐ {filter_obj.name}" if filter_obj.is_favorite else filter_obj.name

            # Add item with filter ID as data
            self.saved_filters_combo.addItem(display_name, filter_obj.id)

        # Restore selection if it still exists
        if current_id is not None:
            index = self.saved_filters_combo.findData(current_id)
            if index >= 0:
                self.saved_filters_combo.setCurrentIndex(index)

    def clear_saved_filter_selection(self):
        """Reset saved filter dropdown to placeholder."""
        self.saved_filters_combo.setCurrentIndex(0)

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

    def _populate_date_presets(self):
        """
        Populate date dropdown with preset options (US-012).

        Adds 12 preset date ranges plus "Custom Range..." option.
        Calculates current quarter and year for dynamic labels.
        """
        today = date.today()
        quarter = (today.month - 1) // 3 + 1

        self.date_combo.addItems([
            "All Time",
            "Today",
            "Yesterday",
            "Last 7 Days",
            "Last 30 Days",
            "This Month",
            "Last Month",
            f"This Quarter (Q{quarter})",
            "Last Quarter",
            f"This Year ({today.year})",
            f"Last Year ({today.year - 1})",
            "Custom Range..."
        ])

    def _on_date_preset_changed(self, text: str):
        """
        Handle date preset selection (US-012).

        Args:
            text: Selected preset text from dropdown

        Behavior:
            - "All Time": Clears date filter
            - "Custom Range...": Opens DateRangeDialog
            - Other presets: Calculate range and emit signal
        """
        if text == "Custom Range...":
            self._show_custom_date_dialog()
        elif text == "All Time":
            # Clear date filter
            self.current_date_from = None
            self.current_date_to = None
            self.date_filter_changed.emit(None, None)
            self._on_filter_changed()
        else:
            # Get date range from preset
            from_date, to_date = self._get_preset_range(text)
            if from_date and to_date:
                self.current_date_from = from_date
                self.current_date_to = to_date
                self.date_filter_changed.emit(from_date, to_date)
                self._on_filter_changed()

    def _get_preset_range(self, text: str) -> tuple:
        """
        Map preset dropdown text to date range (US-012).

        Args:
            text: Preset text from dropdown

        Returns:
            Tuple of (from_date, to_date) or (None, None) if unknown

        Note:
            Handles quarter/year presets that have dynamic text
            (e.g., "This Quarter (Q3)" -> extract "This Quarter")
        """
        # Map simple presets
        preset_map = {
            "Today": DateRange.get_today,
            "Yesterday": DateRange.get_yesterday,
            "Last 7 Days": DateRange.get_last_7_days,
            "Last 30 Days": DateRange.get_last_30_days,
            "This Month": DateRange.get_this_month,
            "Last Month": DateRange.get_last_month,
        }

        # Check simple presets first
        if text in preset_map:
            return preset_map[text]()

        # Handle dynamic presets (quarter/year with embedded info)
        if text.startswith("This Quarter"):
            return DateRange.get_this_quarter()
        elif text.startswith("Last Quarter"):
            return DateRange.get_last_quarter()
        elif text.startswith("This Year"):
            return DateRange.get_this_year()
        elif text.startswith("Last Year"):
            return DateRange.get_last_year()

        # Unknown preset
        return (None, None)

    def _show_custom_date_dialog(self):
        """
        Show custom date range picker dialog (US-012).

        Opens DateRangeDialog and updates combo box text with selected range
        if user clicks Apply.
        """
        dialog = DateRangeDialog(self)

        if dialog.exec() == QDialog.Accepted:
            from_date, to_date = dialog.get_date_range()

            # Store filter state
            self.current_date_from = from_date
            self.current_date_to = to_date

            # Update combo text to show selected range
            range_text = f"{from_date.strftime('%b %d')} - {to_date.strftime('%b %d, %Y')}"
            custom_index = self.date_combo.findText("Custom Range...", Qt.MatchStartsWith)

            if custom_index >= 0:
                # Replace "Custom Range..." with actual range
                self.date_combo.setItemText(custom_index, range_text)
                self.date_combo.setCurrentText(range_text)

            # Emit signal
            self.date_filter_changed.emit(from_date, to_date)
            self._on_filter_changed()
        else:
            # User cancelled - revert to "All Time"
            self.date_combo.setCurrentText("All Time")

    def has_date_filter(self) -> bool:
        """
        Check if date filter is currently active (US-012).

        Returns:
            True if date filter is set, False otherwise

        Note:
            Date filter is active if both from_date and to_date are set.
            "All Time" is not considered an active filter.
        """
        return self.current_date_from is not None and self.current_date_to is not None

    def clear_date_filter(self):
        """
        Clear date filter and reset to "All Time" (US-012).

        Called by _on_clear_all() when user clicks "Clear All Filters" button.
        """
        self.current_date_from = None
        self.current_date_to = None
        self.date_combo.setCurrentText("All Time")

        # Restore "Custom Range..." if it was replaced
        custom_index = self.date_combo.findText("Custom Range...", Qt.MatchStartsWith)
        if custom_index < 0:
            # Find any item that doesn't match a preset (custom range text)
            for i in range(self.date_combo.count()):
                item_text = self.date_combo.itemText(i)
                if "-" in item_text and "Days" not in item_text:  # Custom range format
                    self.date_combo.setItemText(i, "Custom Range...")
                    break

    def set_transaction_service(self, service):
        """
        Set transaction service for category dropdown population (US-013).

        Args:
            service: TransactionService instance

        Usage:
            >>> panel = SearchPanelWidget()
            >>> panel.set_transaction_service(transaction_service)
            >>> panel.populate_categories()
        """
        self.transaction_service = service

    def populate_categories(self, account_id=None):
        """
        Populate category dropdown with categories from database (US-013).

        Fetches distinct categories with transaction counts from the backend
        and populates the category combo box. Categories are sorted alphabetically
        with transaction counts displayed (e.g., "Groceries (45)").

        Args:
            account_id: Optional account ID to filter categories (only show
                        categories used in this account)

        Behavior:
            - Clears existing categories (except "All Categories")
            - Calls transaction_service.get_categories_with_counts()
            - Adds each category with count: "Category (count)"
            - Maintains current selection if possible

        Example:
            >>> panel.populate_categories()
            # Dropdown shows: "All Categories", "Dining Out (23)", "Groceries (45)"

            >>> panel.populate_categories(account_id=5)
            # Shows only categories from account 5
        """
        if not self.transaction_service:
            return

        # Store current selection
        current_text = self.category_combo.currentText()

        # Clear existing items (keep "All Categories")
        self.category_combo.clear()
        self.category_combo.addItem("All Categories")

        try:
            # Get categories with counts from backend
            categories = self.transaction_service.get_categories_with_counts(account_id=account_id)

            # Add categories with counts
            for category, count in categories:
                if category:  # Skip empty categories
                    display_text = f"{category} ({count})"
                    self.category_combo.addItem(display_text, category)  # Store category name in userData

        except Exception as e:
            # Log error but don't crash - dropdown will just show "All Categories"
            print(f"Error loading categories: {e}")

        # Restore selection if it still exists
        index = self.category_combo.findText(current_text)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)

    def _on_category_changed(self, text: str):
        """
        Handle category selection change (US-013).

        Args:
            text: Selected category text from dropdown

        Behavior:
            - "All Categories": Clears filter (emits empty list)
            - Other selection: Extracts category name and emits as list
            - Updates filter count
            - Emits category_filter_changed signal for MainWindow

        Signal Flow:
            SearchPanelWidget.category_filter_changed(List[str])
                ↓
            MainWindow._on_category_filter_changed(categories)
                ↓
            MainWindow._reload_filtered_transactions()
        """
        if text == "All Categories":
            # Clear filter
            self.current_categories = []
            self.category_filter_changed.emit([])
        else:
            # Extract category name from "Category (count)" format
            category_name = self.category_combo.currentData()
            if category_name:
                self.current_categories = [category_name]
                self.category_filter_changed.emit([category_name])
            else:
                # Fallback: parse from display text
                category_name = text.split(" (")[0] if " (" in text else text
                self.current_categories = [category_name]
                self.category_filter_changed.emit([category_name])

        # Update filter count
        self._on_filter_changed()

    def has_category_filter(self) -> bool:
        """
        Check if category filter is currently active (US-013).

        Returns:
            True if one or more categories are selected, False otherwise

        Note:
            "All Categories" is not considered an active filter.
        """
        return len(self.current_categories) > 0

    def clear_category_filter(self):
        """
        Clear category filter and reset to "All Categories" (US-013).

        Called by _on_clear_all() when user clicks "Clear All Filters" button.
        Also called by MainWindow when clearing filters programmatically.
        """
        self.current_categories = []
        self.category_combo.setCurrentText("All Categories")

    def _on_amount_input_changed(self):
        """
        Handle amount input text change (US-014).

        Implements 500ms debounce - waits for user to stop typing before
        parsing input and emitting filter signal. This prevents excessive
        filtering while user is typing.

        Debounce Strategy:
            - User types: Timer resets
            - User stops typing for 500ms: Timer fires, parse & emit
            - Invalid input: Ignore, wait for valid input
        """
        # Restart debounce timer (cancels previous timer if still running)
        self.amount_debounce_timer.stop()
        self.amount_debounce_timer.start()

    def _on_amount_absolute_changed(self, state):
        """
        Handle absolute value checkbox state change (US-014).

        Args:
            state: Qt.CheckState (Checked or Unchecked)

        Behavior:
            - Checkbox checked: Sets absolute mode to True
            - Checkbox unchecked: Sets absolute mode to False
            - Immediately re-emits filter signal (no debounce)
        """
        self.current_amount_absolute = (state == Qt.Checked)

        # Immediately apply (no debounce for checkbox)
        self._emit_amount_filter()

    def _emit_amount_filter(self):
        """
        Parse amount inputs and emit amount_filter_changed signal (US-014).

        Parses min/max input text using TransactionService.parse_amount_string()
        and emits signal with validated Decimal values.

        Validation Rules:
            - Empty inputs: Treated as None (no bound)
            - Invalid input: Ignored (treated as empty)
            - Min > Max: Validation handled by service layer

        Signal Emission:
            - Emits: (min_amount: Decimal|None, max_amount: Decimal|None, absolute: bool)
            - Updates filter count
        """
        if not self.transaction_service:
            return

        # Parse min amount
        min_text = self.amount_min_input.text().strip()
        if min_text:
            min_amount = self.transaction_service.parse_amount_string(min_text)
        else:
            min_amount = None

        # Parse max amount
        max_text = self.amount_max_input.text().strip()
        if max_text:
            max_amount = self.transaction_service.parse_amount_string(max_text)
        else:
            max_amount = None

        # Store current state
        self.current_amount_min = min_amount
        self.current_amount_max = max_amount

        # Emit signal
        self.amount_filter_changed.emit(min_amount, max_amount, self.current_amount_absolute)

        # Update filter count
        self._on_filter_changed()

    def _apply_amount_preset(self, min_amount, max_amount, absolute):
        """
        Apply amount filter preset (US-014).

        Args:
            min_amount: Minimum amount (Decimal or None)
            max_amount: Maximum amount (Decimal or None)
            absolute: Absolute value mode (bool)

        Behavior:
            - Updates input fields with preset values
            - Sets absolute checkbox state
            - Immediately applies filter (bypasses debounce)

        Presets:
            - "< $20": (None, 20, True)
            - "$20-$100": (20, 100, True)
            - "> $100": (100, None, True)
            - "> $500": (500, None, True)
        """
        # Update input fields
        if min_amount is not None:
            self.amount_min_input.setText(str(min_amount))
        else:
            self.amount_min_input.clear()

        if max_amount is not None:
            self.amount_max_input.setText(str(max_amount))
        else:
            self.amount_max_input.clear()

        # Update absolute checkbox
        self.amount_absolute_checkbox.setChecked(absolute)

        # Immediately apply (bypass debounce)
        self.current_amount_absolute = absolute
        self._emit_amount_filter()

    def has_amount_filter(self) -> bool:
        """
        Check if amount filter is currently active (US-014).

        Returns:
            True if min or max amount is set, False otherwise

        Note:
            Amount filter is active if either bound is set.
            Empty inputs are not considered active filters.
        """
        return self.current_amount_min is not None or self.current_amount_max is not None

    def clear_amount_filter(self):
        """
        Clear amount filter and reset inputs (US-014).

        Called by _on_clear_all() when user clicks "Clear All Filters" button.
        Also called by MainWindow when clearing filters programmatically.
        """
        self.current_amount_min = None
        self.current_amount_max = None
        self.current_amount_absolute = False
        self.amount_min_input.clear()
        self.amount_max_input.clear()
        self.amount_absolute_checkbox.setChecked(False)

    def apply_date_filter(self, from_date, to_date):
        """
        Apply date filter programmatically (US-015).

        Sets the date range and updates the UI to reflect the filter.
        Called when loading a saved filter.

        Args:
            from_date: Start date (datetime.date) or None
            to_date: End date (datetime.date) or None
        """
        self.current_date_from = from_date
        self.current_date_to = to_date

        if from_date and to_date:
            # Update combo box to show custom range
            date_str = f"{from_date.strftime('%b %d, %Y')} - {to_date.strftime('%b %d, %Y')}"
            self.date_combo.setCurrentText(date_str)
        else:
            self.date_combo.setCurrentText("All Time")

        # Emit signal
        self.date_filter_changed.emit(from_date, to_date)

    def apply_category_filter(self, categories):
        """
        Apply category filter programmatically (US-015).

        Sets the selected categories and updates the UI.
        Called when loading a saved filter.

        Args:
            categories: List of category names to filter by
        """
        self.current_categories = categories if categories else []

        if categories:
            # Update combo box to show category selection
            if len(categories) == 1:
                self.category_combo.setCurrentText(categories[0])
            else:
                # Multiple categories: show count
                self.category_combo.setCurrentText(f"{len(categories)} categories selected")
        else:
            self.category_combo.setCurrentText("All Categories")

        # Emit signal
        self.category_filter_changed.emit(self.current_categories)

    def apply_amount_filter(self, min_amount, max_amount, absolute=False):
        """
        Apply amount filter programmatically (US-015).

        Sets the amount range and absolute mode, updates UI.
        Called when loading a saved filter.

        Args:
            min_amount: Minimum amount (Decimal) or None
            max_amount: Maximum amount (Decimal) or None
            absolute: Whether to use absolute value mode (bool)
        """
        self.current_amount_min = min_amount
        self.current_amount_max = max_amount
        self.current_amount_absolute = absolute

        # Update input fields
        if min_amount is not None:
            self.amount_min_input.setText(str(min_amount))
        else:
            self.amount_min_input.clear()

        if max_amount is not None:
            self.amount_max_input.setText(str(max_amount))
        else:
            self.amount_max_input.clear()

        # Update checkbox
        self.amount_absolute_checkbox.setChecked(absolute)

        # Emit signal
        self.amount_filter_changed.emit(min_amount, max_amount, absolute)

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
        """
        count = 0

        # Count text search filter (US-011)
        if self.text_search_widget and self.text_search_widget.get_text():
            count += 1

        # US-012: Count date filter if set
        if self.has_date_filter():
            count += 1

        # US-013: Count category filter if selected
        if self.has_category_filter():
            count += 1

        # US-014: Count amount filter if min/max set
        if self.has_amount_filter():
            count += 1

        # Update display
        self.set_active_filter_count(count)

    def _on_clear_all(self):
        """
        Handle Clear All Filters button click.

        Clears all active filters by:
        1. Clearing text search widget (US-011)
        2. Clearing date filter (US-012)
        3. Clearing category filter (US-013)
        4. Clearing amount filter (US-014)
        5. Emitting filters_cleared signal for MainWindow to reload data
        6. Resetting filter count to 0

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

        # US-012: Clear date filter
        self.clear_date_filter()

        # US-013: Clear category filter
        self.clear_category_filter()

        # US-014: Clear amount filter
        self.clear_amount_filter()

        # Emit signal for MainWindow to reload data
        self.filters_cleared.emit()

        # Reset filter count
        self.set_active_filter_count(0)

    def _configure_tab_order(self):
        """
        Configure keyboard tab order for accessibility (US-016 Task F4 + US-012 + US-013).

        Tab Order:
            1. Search box (text_search_widget) - primary text filter
            2. Date dropdown (date_combo) - date filter (US-012)
            3. Category dropdown (category_combo) - category filter (US-013)
            4. Clear All button - reset action
            5. Collapse button - minimize action

        This ensures logical keyboard navigation where users can:
        - Tab into search box to start text filtering
        - Tab to date dropdown to change date range
        - Tab to category dropdown to filter by category
        - Tab to Clear All to reset all filters
        - Tab to Collapse to minimize panel

        Note: QWidget.setTabOrder() sets the order between two widgets.
        Call this after text_search_widget is set.
        """
        if not self.text_search_widget:
            # No search widget yet, tab order: date_combo → category_combo → clear_all → collapse
            self.setTabOrder(self.date_combo, self.category_combo)
            self.setTabOrder(self.category_combo, self.clear_all_button)
            self.setTabOrder(self.clear_all_button, self.collapse_button)
            return

        # Full tab order with all widgets
        # search_widget → date_combo → category_combo → clear_all_button → collapse_button
        self.setTabOrder(self.text_search_widget, self.date_combo)
        self.setTabOrder(self.date_combo, self.category_combo)
        self.setTabOrder(self.category_combo, self.clear_all_button)
        self.setTabOrder(self.clear_all_button, self.collapse_button)

    def _apply_styling(self):
        """
        Apply QSS styling to panel and child widgets.

        Styling includes:
        - Panel background and border (respects theme)
        - Header/Footer backgrounds (respects theme)
        - Button styles (collapse, clear all)
        - Label colors and fonts (respects theme)
        - Focus indicators for accessibility
        """
        self.setStyleSheet("""
            /* Panel container - respects system theme */
            SearchPanelWidget {
                background-color: palette(window);
                border: 1px solid palette(mid);
                border-radius: 4px;
            }

            /* Header frame */
            QFrame#headerFrame {
                background-color: palette(base);
                border-bottom: 1px solid palette(mid);
            }

            /* Filters container */
            QFrame#filtersContainer {
                background-color: palette(base);
            }

            /* Footer frame */
            QFrame#footerFrame {
                background-color: palette(window);
                border-top: 1px solid palette(mid);
            }

            /* Title label */
            QLabel#titleLabel {
                font-size: 14px;
                color: palette(text);
            }

            /* Filter count labels */
            QLabel#filterCountLabel {
                color: palette(dark);
                font-size: 12px;
            }

            /* Placeholder labels */
            QLabel#placeholderLabel {
                color: palette(dark);
                font-size: 13px;
                font-style: italic;
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
                background-color: palette(midlight);
            }

            QPushButton#collapseButton:pressed {
                background-color: palette(mid);
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
                background-color: palette(midlight);
                color: palette(mid);
            }

            QPushButton#clearAllButton:focus {
                border: 2px solid #2196F3;
                outline: 2px solid #93C5FD;
                outline-offset: 2px;
            }

            /* Amount preset buttons (US-014) */
            QPushButton#amountPresetButton {
                background-color: palette(button);
                color: palette(button-text);
                border: 1px solid palette(mid);
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
            }

            QPushButton#amountPresetButton:hover {
                background-color: #2196F3;
                color: white;
                border-color: #1976D2;
            }

            QPushButton#amountPresetButton:pressed {
                background-color: #1565C0;
            }

            QPushButton#amountPresetButton:focus {
                border: 2px solid #2196F3;
                outline: 1px solid #93C5FD;
            }
        """)
