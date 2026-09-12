"""Compatibility wrapper exposing a LockScreen and font helpers.

This module adapts older imports (`lcars.ui.lock_screen`) to the
current implementation in `lcars.modules.lock_screen` and
font helpers in `lcars.themes.lcars_palette`.
"""
from lcars.modules.lock_screen import LCARSLoginScreen
from lcars.themes.lcars_palette import setup_lcars_font, get_lcars_font_style


# Backwards-compatible names expected by older imports
LCARSLockScreen = LCARSLoginScreen

__all__ = ["LCARSLockScreen", "setup_lcars_font", "get_lcars_font_style"]
