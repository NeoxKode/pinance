"""
Transaction search widget with debounced text input.

US-011: Basic Text Search - Enables users to search transactions by description
with a 300ms debounce for performance optimization.

Created: 2025-11-11
Story: US-011 - Basic Text Search (EPIC-002, Sprint 13)
"""

from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout
from PySide6.QtCore import QTimer, Signal


class TransactionSearchWidget(QWidget):
    """
    Search input widget for transaction list with debounced search.

    US-011: Provides text search functionality with 300ms debounce to reduce
    database queries and improve performance during user typing.

    Features:
        - Case-insensitive search (handled by backend)
        - 300ms debounce timer (prevents query on every keystroke)
        - Built-in clear "X" button
        - Keyboard accessible (Ctrl+F to focus)
        - Placeholder text for user guidance

    Signals:
        search_changed(str): Emitted after 300ms debounce with trimmed search text.
                            Empty string means "show all transactions".

    Usage:
        >>> search_widget = TransactionSearchWidget()
        >>> search_widget.search_changed.connect(lambda keyword: print(f"Search: {keyword}"))
        >>> search_widget.set_focus()  # Focus input programmatically

    Design:
        - Width: 250-300px (constrained for layout consistency)
        - Height: Default line edit height (~28-32px)
        - Margin: 0 (parent layout controls spacing)
    """

    # Signal emitted after debounce with trimmed search keyword
    search_changed = Signal(str)

    def __init__(self, parent=None):
        """
        Initialize transaction search widget.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self._setup_timer()
        self._setup_ui()

    def _setup_timer(self):
        """Configure debounce timer for search input."""
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)  # Only fire once per start
        self.search_timer.timeout.connect(self._emit_search)

    def _setup_ui(self):
        """Create the widget user interface."""
        # Create search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search descriptions...")
        self.search_input.setMinimumWidth(250)
        self.search_input.setMaximumWidth(300)
        self.search_input.setClearButtonEnabled(True)  # Built-in "X" button
        self.search_input.setToolTip(
            "Search transactions by description (case-insensitive)\n"
            "Examples: 'starbucks', 'amazon', 'grocery'\n"
            "Keyboard shortcut: Ctrl+F (this account) or Ctrl+Shift+F (all accounts)"
        )

        # Connect text change to debounce timer
        self.search_input.textChanged.connect(self._on_text_changed)

        # Layout with zero margins (parent controls spacing)
        layout = QHBoxLayout(self)
        layout.addWidget(self.search_input)
        layout.setContentsMargins(0, 0, 0, 0)

    def _on_text_changed(self, text: str):
        """
        Handle text change with 300ms debounce.

        Restarts the timer on every keystroke. The search signal is only emitted
        300ms after the user stops typing.

        Args:
            text: Current text in input (not used, we get it later from input)
        """
        # Stop any running timer and restart
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms debounce

    def _emit_search(self):
        """
        Emit search signal after debounce timer expires.

        Retrieves current text, trims whitespace, and emits the search_changed signal.
        Empty/whitespace text is treated as "show all" (backend handles this).
        """
        text = self.search_input.text().strip()
        self.search_changed.emit(text)

    def clear(self):
        """
        Clear search input programmatically.

        Triggers the clear button action, which will emit search_changed("")
        after the debounce timer expires.
        """
        self.search_input.clear()

    def set_focus(self):
        """
        Focus search input for keyboard access.

        Used by Ctrl+F and Ctrl+Shift+F keyboard shortcuts to let users
        start typing immediately.
        """
        self.search_input.setFocus()
        self.search_input.selectAll()  # Select any existing text for easy replacement

    def get_text(self) -> str:
        """
        Get current search text (trimmed).

        Returns:
            Current search keyword, trimmed of whitespace
        """
        return self.search_input.text().strip()

    def set_text(self, text: str):
        """
        Set search text programmatically.

        Args:
            text: Search keyword to set
        """
        self.search_input.setText(text)
