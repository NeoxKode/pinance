"""
UI Styles Package - Color system and visual styling.

Story: US-009 - Account Color Coding & Visual Indicators
Sprint: 10

This package provides:
- account_colors: Color constants, validation, and WCAG AA compliance utilities
- (Future) Additional style modules as needed
"""

from finance_app.ui.styles.account_colors import (
    # Color Constants
    AccountColors,

    # Color Mapping Functions
    get_default_color_for_account_type,
    get_default_color_for_subtype,

    # Validation Functions
    is_valid_hex_color,
    hex_to_rgb,
    rgb_to_hex,

    # Accessibility Functions
    calculate_relative_luminance,
    calculate_contrast_ratio,
    is_wcag_aa_compliant,
    suggest_text_color,

    # Balance Color Logic
    get_balance_color,

    # Color Utilities
    lighten_color,
    darken_color,
    get_hover_color,
    validate_and_fix_color,
)

__all__ = [
    # Color Constants
    'AccountColors',

    # Color Mapping
    'get_default_color_for_account_type',
    'get_default_color_for_subtype',

    # Validation
    'is_valid_hex_color',
    'hex_to_rgb',
    'rgb_to_hex',

    # Accessibility
    'calculate_relative_luminance',
    'calculate_contrast_ratio',
    'is_wcag_aa_compliant',
    'suggest_text_color',

    # Balance Colors
    'get_balance_color',

    # Utilities
    'lighten_color',
    'darken_color',
    'get_hover_color',
    'validate_and_fix_color',
]
