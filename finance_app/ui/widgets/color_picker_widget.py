"""
Color Picker Widget for account color customization.

US-009: Allows users to select custom colors for accounts with WCAG AA preview.
"""
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QColorDialog, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from finance_app.ui.styles import (
    AccountColors,
    get_default_color_for_account_type,
    is_wcag_aa_compliant
)


class ColorPickerWidget(QWidget):
    """
    Widget for selecting account colors with visual preview.

    Features:
    - Color preview box showing current color
    - Click to open color picker dialog
    - WCAG AA accessibility indicator
    - Quick color presets for common account types
    - Displays contrast ratio with white text

    Signals:
        color_changed(str): Emitted when color changes (hex color string)
    """

    color_changed = Signal(str)  # Emits hex color like "#2563EB"

    def __init__(self, initial_color: str = "#2563EB", parent=None):
        """
        Initialize color picker widget.

        Args:
            initial_color: Starting color as hex string
            parent: Parent widget
        """
        super().__init__(parent)
        self._current_color = initial_color
        self.setup_ui()

    def setup_ui(self):
        """Create the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main color preview and picker button
        preview_layout = QHBoxLayout()

        # Color preview box
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(50, 50)
        self.color_preview.setFrameShape(QFrame.Box)
        self.color_preview.setLineWidth(2)
        self.color_preview.setToolTip("Click 'Choose Color' to change")
        self._update_preview()
        preview_layout.addWidget(self.color_preview)

        # Color info and button
        info_layout = QVBoxLayout()

        # Current color label
        self.color_label = QLabel(self._current_color)
        self.color_label.setStyleSheet("font-family: monospace; font-weight: bold;")
        info_layout.addWidget(self.color_label)

        # WCAG AA indicator
        self.wcag_label = QLabel()
        self.wcag_label.setStyleSheet("font-size: 11px; color: #666;")
        self._update_wcag_indicator()
        info_layout.addWidget(self.wcag_label)

        # Choose color button
        self.choose_btn = QPushButton("Choose Color...")
        self.choose_btn.clicked.connect(self._open_color_dialog)
        info_layout.addWidget(self.choose_btn)

        preview_layout.addLayout(info_layout)
        preview_layout.addStretch()

        layout.addLayout(preview_layout)

        # Quick color presets
        presets_label = QLabel("Quick Presets:")
        presets_label.setStyleSheet("font-size: 11px; color: #666; margin-top: 8px;")
        layout.addWidget(presets_label)

        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(4)

        # Default account type colors
        preset_colors = [
            (AccountColors.ASSET, "Asset Blue"),
            (AccountColors.LIABILITY, "Liability Red"),
            (AccountColors.EQUITY, "Equity Purple"),
            (AccountColors.INCOME, "Income Amber"),
            (AccountColors.EXPENSE, "Expense Orange"),
        ]

        for color_hex, tooltip in preset_colors:
            btn = self._create_preset_button(color_hex, tooltip)
            presets_layout.addWidget(btn)

        presets_layout.addStretch()
        layout.addLayout(presets_layout)

        # Apply styling
        self.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }

            QPushButton:hover {
                background-color: #f5f5f5;
                border-color: #2196F3;
            }

            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)

    def _create_preset_button(self, color_hex: str, tooltip: str) -> QPushButton:
        """
        Create a preset color button.

        Args:
            color_hex: Color as hex string
            tooltip: Tooltip text

        Returns:
            QPushButton configured as preset
        """
        btn = QPushButton()
        btn.setFixedSize(32, 32)
        btn.setToolTip(f"{tooltip}\n{color_hex}")
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_hex};
                border: 2px solid #ddd;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid #2196F3;
            }}
        """)
        btn.clicked.connect(lambda: self.set_color(color_hex))
        return btn

    def _open_color_dialog(self):
        """Open Qt color picker dialog."""
        current_qcolor = QColor(self._current_color)

        # Open color dialog
        color = QColorDialog.getColor(
            current_qcolor,
            self,
            "Choose Account Color",
            QColorDialog.DontUseNativeDialog  # Use Qt dialog for consistency
        )

        if color.isValid():
            # Convert to hex string
            hex_color = color.name().upper()
            self.set_color(hex_color)

    def set_color(self, color_hex: str):
        """
        Set the current color.

        Args:
            color_hex: Color as hex string (e.g., "#2563EB")
        """
        # Validate color format
        try:
            QColor(color_hex)  # Will raise if invalid
            self._current_color = color_hex
            self._update_preview()
            self._update_wcag_indicator()
            self.color_label.setText(color_hex)
            self.color_changed.emit(color_hex)
        except:
            # Invalid color, ignore
            pass

    def get_color(self) -> str:
        """
        Get the current color.

        Returns:
            Current color as hex string
        """
        return self._current_color

    def _update_preview(self):
        """Update the color preview box."""
        self.color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {self._current_color};
                border: 2px solid #ddd;
                border-radius: 4px;
            }}
        """)

    def _update_wcag_indicator(self):
        """Update the WCAG AA accessibility indicator."""
        # Check WCAG AA compliance with white text
        is_compliant = is_wcag_aa_compliant(self._current_color, '#FFFFFF')

        if is_compliant:
            self.wcag_label.setText("✓ WCAG AA Compliant")
            self.wcag_label.setStyleSheet("font-size: 11px; color: #059669; font-weight: bold;")
        else:
            self.wcag_label.setText("⚠ Low contrast with white text")
            self.wcag_label.setStyleSheet("font-size: 11px; color: #DC2626; font-weight: bold;")
