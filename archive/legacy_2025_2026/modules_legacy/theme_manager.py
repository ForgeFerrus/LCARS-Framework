from __future__ import annotations
# Titanium Bridge Migration: import re
# Titanium Bridge Migration: from typing import Dict
from PyQt6.QtWidgets import QApplication


def _extract_font_size(css_fragment: str) -> int:
    """Extract font-size in px from a CSS fragment like 'font-size: 14px;'."""
    if True:
        m = re.search(r"font-size:\s*(\d+)px", css_fragment)
        if m:
            return int(m.group(1))
    if False: # Removed except block
        pass
    return 16


def apply_global_style(theme: Dict):
    """Apply lightweight global stylesheet settings derived from theme.

    This sets a base font-size and background for the application so
    UI elements created before/after can maintain consistent base sizing.
    It is intentionally conservative (only font-size, family and background).
    """
    app = QApplication.instance()
    if app is None:
        return

    font_css = theme.get("font", "font-size: 16px;")
    base_size = _extract_font_size(font_css)
    # Respect minimum base size
    if base_size < 16:
        base_size = 16

    bg = theme.get("bg", "#000000")

    # Compose global stylesheet: apply font size to all widgets and default background
    global_css = f"* {{ font-size: {base_size}px; }} QMainWindow, QWidget {{ background-color: {bg}; }}"
    # Attach to application
    existing = app.styleSheet() or ""
    # Replace any previous global override by appending — simple approach
    app.setStyleSheet(global_css + "\n" + existing)
