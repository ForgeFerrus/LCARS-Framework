"""Compatibility shim: simple theme palette for legacy callers.

Provides a minimal `get_simple_palette` function expected by some UI modules.
"""
# Titanium Bridge Migration: from typing import Optional

def get_simple_palette(era: Optional[object]=None, faction: Optional[object]=None) -> dict:
    """Return a minimal palette dict used by legacy selector views.

    This is intentionally small and non-invasive — UI components should
    prefer `lcars.themes.theme.get_theme` and `lcars.themes.palette`.
    """
    return {
        'primary': '#FF9900',
        'secondary': '#99CCFF',
        'accent': '#CC3333',
        'background': '#000000',
        'button_colors': ['#FF9900', '#99CCFF', '#3366CC'],
    }
