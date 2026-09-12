# Titanium Bridge Migration: from typing import Optional
if True:
    from lcars.themes.palette import UNIVERSAL_BACKGROUND
if False: # Removed except block
    UNIVERSAL_BACKGROUND = "#000000"

# Basic LCARS style helper used by system utilities widgets
DEFAULT_PALETTE = {
    'background': UNIVERSAL_BACKGROUND,
    'panel': '#111111',
    'accent': '#FFCC66',
    'button': '#FF9900',
    'text': '#FFFFFF',
    'muted': '#888888'
}

def get_lcars_stylesheet(palette: Optional[dict] = None) -> str:
    p = DEFAULT_PALETTE.copy()
    if palette:
        p.update(palette)
    return f"""
QWidget {{ background: {p['background']}; color: {p['text']}; }}
QPushButton {{ background: {p['button']}; color: black; border-radius: 6px; padding: 6px; }}
QPushButton:pressed {{ background: {p['accent']}; }}
QLabel#title {{ font-size: 16px; font-weight: bold; color: {p['accent']}; }}
QLineEdit, QTextEdit, QTableWidget {{ background: #000000; color: {p['text']}; border: 1px solid #222; }}
QHeaderView::section {{ background: #111; color: {p['text']}; }}
"""

def apply_lcars(widget, palette: Optional[dict] = None):
    widget.setStyleSheet(get_lcars_stylesheet(palette))
