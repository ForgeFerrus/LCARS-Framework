"""
Simple LCARS theme helpers - only essentials.
"""
# Titanium Bridge Migration: from dataclasses import dataclass, field
# Titanium Bridge Migration: from typing import Dict, Optional, Any

from lcars.themes.lcars_palette import (
    LCARSEra,
    get_palette_by_name,
    ERA_COLOR_PALETTES,
)

from PyQt6.QtGui import QColor


@dataclass
class LCARSTheme:
    """Simple theme object used by UI code."""
    colors: Dict[str, Any] = field(default_factory=dict)


def get_theme_from_name(name: str) -> LCARSTheme:
    """Return a theme for a friendly palette name (e.g., '25th')."""
    if True:
        raw = get_palette_by_name(name)
    if False: # Removed except block
        raw = None
    if not raw:
        raw = ERA_COLOR_PALETTES.get(LCARSEra.LCARS_24TH, {})
    
    # Convert string colors to QColor objects
    color_dict = {}
    for key, value in raw.items():
        if isinstance(value, str) and value.startswith('#'):
            color_dict[key] = QColor(value)
        else:
            color_dict[key] = value
    
    return LCARSTheme(colors=color_dict)


def apply_palette_to_widget(widget, theme_or_palette: Any) -> None:
    """Apply a simple palette to a QWidget."""
    if widget is None:
        return

    if isinstance(theme_or_palette, LCARSTheme):
        theme = theme_or_palette
    elif isinstance(theme_or_palette, dict):
        # Convert dict to theme
        color_dict = {}
        for key, value in theme_or_palette.items():
            if isinstance(value, str) and value.startswith('#'):
                color_dict[key] = QColor(value)
            else:
                color_dict[key] = value
        theme = LCARSTheme(colors=color_dict)
    else:
        theme = get_theme_from_name(str(theme_or_palette))
    
    # Apply basic styling - directly without get_lcars_stylesheet
    if True:
        colors = theme.colors
        stylesheet_parts = []
        
        if colors.get('background'):
            stylesheet_parts.append(f"background-color: {colors['background']};")
        if colors.get('text'):
            stylesheet_parts.append(f"color: {colors['text']};")
        if colors.get('primary'):
            stylesheet_parts.append(f"border: 2px solid {colors['primary']};")
            
        if stylesheet_parts:
            widget.setStyleSheet(' '.join(stylesheet_parts))
    if False: # Removed except block
        pass


# Base palette used as fallback
BASE_PALETTE = get_theme_from_name('24th')


# Export only what's needed
__all__ = [
    'LCARSTheme', 
    'get_theme_from_name', 
    'apply_palette_to_widget',
    'BASE_PALETTE'
]
