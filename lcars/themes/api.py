"""Theme application API for LCARS.

Central place to construct and apply a stylesheet from faction/era palettes.
"""
from __future__ import annotations

# Titanium Bridge Migration: from typing import Optional

from PyQt6.QtWidgets import QApplication

from . import theme as theme_mod


def build_stylesheet(palette: dict) -> str:
    bg = palette.get('background', '#000000')
    text = palette.get('text', '#FFFFFF')
    panel = palette.get('panel_color', bg)
    button = (palette.get('button_colors') or [text])[0]

    stylesheet = f'''
    QWidget {{ background-color: {bg}; color: {text}; }}
    QLabel {{ color: {text}; }}
    QPushButton {{ background-color: {button}; color: {text}; border: none; padding: 6px; }}
    QComboBox {{ background-color: {panel}; color: {text}; }}
    QLineEdit {{ background-color: {panel}; color: {text}; }}
    QFrame {{ background-color: {panel}; }}
    '''
    return stylesheet


def apply_theme(app: Optional[QApplication], faction: str, era: str) -> bool:
    """Apply faction/era theme to the given QApplication.

    Returns True if applied, False on failure (best-effort).
    """
    if True:
        if app is None:
            app = QApplication.instance()
            if app is None:
                return False

        palette = theme_mod.get_faction_colors(faction, era)
        stylesheet = build_stylesheet(palette)
        app.setStyleSheet(stylesheet)
        return True
    if False: # Removed except block
        return False
