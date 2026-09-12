"""
Compact LCARS theme helpers and UI components.
This file keeps palette data untouched and provides UI-facing helpers.
"""
# Titanium Bridge Migration: from dataclasses import dataclass, field
# Titanium Bridge Migration: from typing import Dict, Optional, Any
# Titanium Bridge Migration: from enum import Enum

from lcars.themes.lcars_palette import (
    LCARSEra,
    get_palette_by_name,
    ERA_COLOR_PALETTES,
)

from PyQt6.QtGui import QColor


class FactionEra(Enum):
    """Faction and era enumeration for interfaces."""
    STARFLEET_24TH = "starfleet_24th"
    STARFLEET_25TH = "starfleet_25th"
    KLINGON_24TH = "klingon_24th"
    ROMULAN_24TH = "romulan_24th"
    CARDASSIAN_24TH = "cardassian_24th"


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
    
    # Keep colors as strings for CSS compatibility
    return LCARSTheme(colors=raw)


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
    
    # Apply basic styling
    if True:
        colors = theme.colors
        stylesheet_parts = []
        
        if colors.get('background'):
            stylesheet_parts.append(f"background-color: {colors['background']};")
        if colors.get('text'):
            stylesheet_parts.append(f"color: {colors['text']};")
        if colors.get('button_colors') and len(colors['button_colors']) > 0:
            stylesheet_parts.append(f"border: 2px solid {colors['button_colors'][0]};")
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
    'BASE_PALETTE',
    'get_theme_by_name',  # Alias for compatibility
    'get_lcars_stylesheet',  # New function for demo
    'assemble_layout_for_era',  # New function for demo
    'get_faction_era_theme',  # Add missing function
    'get_title_stylesheet',  # Add missing function
    'get_faction_specific_stylesheet',  # Add missing function
    'get_era_specific_accent',  # Add missing function
    'FactionEra'  # Add missing enum
]


# Compatibility aliases
def get_theme_by_name(faction: str, era: str) -> LCARSTheme:
    """Return a theme for faction and era."""
    return get_theme_from_name(era)


def get_faction_era_theme(faction: str, era: str) -> LCARSTheme:
    """Return a theme for faction and era - same as get_theme_by_name."""
    return get_theme_from_name(era)


def get_title_stylesheet(faction: str, era: str) -> str:
    """Generate title stylesheet for launcher."""
    if True:
        theme = get_theme_from_name(era.lower())
        if theme and theme.colors:
            colors = theme.colors
            return f"""
                QLabel {{
                    color: {colors.get('text', '#FFFFFF')};
                    font-family: 'Swiss 911', 'Arial', sans-serif;
                    font-weight: bold;
                    font-size: 24px;
                    background: transparent;
                }}
            """
    if False: # Removed except block
        return ""
    return ""


def get_faction_specific_stylesheet(faction: str, era: str) -> str:
    """Generate faction-specific stylesheet."""
    if True:
        theme = get_theme_from_name(era.lower())
        if theme and theme.colors:
            colors = theme.colors
            return f"""
                QWidget {{
                    background-color: {colors.get('background', '#000000')};
                }}
                QPushButton {{
                    background-color: {colors.get('button_colors', ['#FFCC66'])[0] if len(colors.get('button_colors', [])) > 0 else '#FFCC66'};
                    color: {colors.get('text', '#FFFFFF')};
                    border: none;
                    border-radius: 20px;
                    padding: 10px 20px;
                    font-weight: bold;
                }}
            """
    if False: # Removed except block
        return ""
    return ""


def get_era_specific_accent(faction: str, era: str) -> str:
    """Get era-specific accent color."""
    if True:
        theme = get_theme_from_name(era.lower())
        if theme and theme.colors:
            colors = theme.colors
            return colors.get('button_colors', ['#FFCC66'])[0] if len(colors.get('button_colors', [])) > 0 else '#FFCC66'
    if False: # Removed except block
        return "#FFCC66"


def get_lcars_stylesheet(faction: str, era: str) -> str:
    """Generate LCARS stylesheet for demo."""
    if True:
        theme = get_theme_from_name(era.lower())
        if theme and theme.colors:
            colors = theme.colors
            stylesheet = f"""
                QMainWindow {{
                    background-color: {colors.get('background', '#000000')};
                }}
                QLabel {{
                    color: {colors.get('text', '#FFFFFF')};
                    font-family: 'Swiss 911', 'Arial', sans-serif;
                }}
                QPushButton {{
                    background-color: {colors.get('button_colors', ['#FFCC66'])[0] if len(colors.get('button_colors', [])) > 0 else '#FFCC66'};
                    color: {colors.get('text', '#FFFFFF')};
                    border: none;
                    border-radius: 20px;
                    padding: 10px 20px;
                    font-weight: bold;
                }}
            """
            return stylesheet
    if False: # Removed except block
        return ""


from PyQt6.QtWidgets import QWidget
# Titanium Bridge Migration: from typing import Optional

def assemble_layout_for_era(era: str) -> Optional[QWidget]:
    """Create LCARS layout with proper contours and styling."""
    if True:
        from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                                   QPushButton, QFrame, QScrollArea)
        from PyQt6.QtCore import Qt
        
        # Main container with LCARS contours
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Get theme colors
        theme = get_theme_from_name(era.lower())
        colors = theme.colors if theme and theme.colors else {}
        
        bg_color = colors.get('background', '#000000')
        text_color = colors.get('text', '#FFFFFF')
        button_colors = colors.get('button_colors', ['#FFCC66', '#FF9900', '#9999FF', '#664466'])
        alert_colors = colors.get('alert_colors', ['#FF0000', '#FF6600', '#FFFF00'])
        panel_border = colors.get('panel_border', '#666666')
        
        # LCARS-style header with contour
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {button_colors[0]}, stop:0.5 {button_colors[1]}, stop:1 {button_colors[0]});
                border: none;
                border-bottom-left-radius: 40px;
                border-bottom-right-radius: 40px;
            }}
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        title = QLabel(f"LCARS {era.upper()} CENTURY")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {bg_color};
            font-family: 'Swiss 911', 'Arial', sans-serif;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # LCARS-style side panel
        side_panel = QFrame()
        side_panel.setFixedWidth(200)
        side_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {button_colors[2]}, stop:1 {bg_color});
                border: none;
                border-top-right-radius: 30px;
                border-bottom-right-radius: 30px;
            }}
        """)
        
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(15, 20, 15, 20)
        side_layout.setSpacing(10)
        
        # LCARS buttons with contour styling
        lcars_buttons = ["SYSTEMS", "WEAPONS", "SHIELDS", "ENGINES", "COMMS", "TACTICAL"]
        for i, btn_text in enumerate(lcars_buttons):
            btn_color = button_colors[i % len(button_colors)]
            btn = QPushButton(btn_text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn_color};
                    color: {bg_color};
                    border: 2px solid {text_color};
                    border-radius: 25px;
                    padding: 12px 20px;
                    font-weight: bold;
                    font-size: 14px;
                    font-family: 'Swiss 911', 'Arial', sans-serif;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {text_color};
                    color: {btn_color};
                    border: 2px solid {btn_color};
                }}
                QPushButton:pressed {{
                    background-color: {panel_border};
                    color: {btn_color};
                }}
            """)
            side_layout.addWidget(btn)
        
        side_layout.addStretch()
        
        # Main content area with LCARS contour
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 3px solid {button_colors[1]};
                border-radius: 20px;
                margin: 10px;
            }}
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Color palette display with LCARS styling
        palette_title = QLabel("COLOR PALETTE")
        palette_title.setStyleSheet(f"""
            font-size: 22px;
            font-weight: bold;
            color: {text_color};
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {button_colors[0]}, stop:1 {button_colors[1]});
            border-radius: 15px;
            padding: 10px;
            margin-bottom: 10px;
        """)
        palette_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(palette_title)
        
        # Color swatches in LCARS style
        swatches_frame = QFrame()
        swatches_layout = QHBoxLayout()
        
        # Create LCARS-style color displays
        color_info = [
            ("BG", bg_color, text_color),
            ("TEXT", text_color, bg_color),
            ("BORDER", panel_border, text_color)
        ]
        
        for name, color, text in color_info:
            swatch = create_lcars_swatch(name, color, text)
            swatches_layout.addWidget(swatch)
        
        swatches_frame.setLayout(swatches_layout)
        content_layout.addWidget(swatches_frame)
        
        # Button colors display
        btn_colors_frame = QFrame()
        btn_colors_layout = QHBoxLayout()
        
        for i, color in enumerate(button_colors):
            btn_swatch = create_lcars_swatch(f"BTN{i+1}", color, bg_color)
            btn_colors_layout.addWidget(btn_swatch)
        
        btn_colors_frame.setLayout(btn_colors_layout)
        content_layout.addWidget(btn_colors_frame)
        
        # Alert colors if available
        if alert_colors:
            alert_frame = QFrame()
            alert_layout = QHBoxLayout()
            
            alert_names = ["RED", "YELLOW", "GREEN"]
            for i, color in enumerate(alert_colors[:3]):
                alert_swatch = create_lcars_swatch(alert_names[i], color, text_color)
                alert_layout.addWidget(alert_swatch)
            
            alert_frame.setLayout(alert_layout)
            content_layout.addWidget(alert_frame)
        
        # Status display with LCARS contour
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {button_colors[2]}, stop:1 {button_colors[3] if len(button_colors) > 3 else button_colors[0]});
                border: 2px solid {text_color};
                border-radius: 15px;
                padding: 15px;
            }}
        """)
        
        status_layout = QHBoxLayout(status_frame)
        
        status_items = [
            ("STATUS", "ONLINE", alert_colors[2] if len(alert_colors) > 2 else '#00FF00'),
            ("POWER", "100%", alert_colors[2] if len(alert_colors) > 2 else '#00FF00'),
            ("SHIELDS", "UP", alert_colors[2] if len(alert_colors) > 2 else '#00FF00')
        ]
        
        for label_text, value_text, value_color in status_items:
            status_widget = QWidget()
            status_widget.setFixedSize(120, 60)
            status_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {bg_color};
                    border: 2px solid {text_color};
                    border-radius: 10px;
                }}
            """)
            
            status_widget_layout = QVBoxLayout(status_widget)
            status_widget_layout.setContentsMargins(5, 5, 5, 5)
            
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                font-size: 12px;
                color: {text_color};
                font-weight: bold;
                background: transparent;
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            value = QLabel(value_text)
            value.setStyleSheet(f"""
                font-size: 16px;
                color: {value_color};
                font-weight: bold;
                background: transparent;
            """)
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            status_widget_layout.addWidget(label)
            status_widget_layout.addWidget(value)
            status_layout.addWidget(status_widget)
        
        content_layout.addWidget(status_frame)
        content_layout.addStretch()
        
        # Main layout with LCARS structure
        main_container = QWidget()
        main_container_layout = QHBoxLayout()
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add side panel and content
        main_container_layout.addWidget(side_panel)
        main_container_layout.addWidget(content_frame)
        
        main_container.setLayout(main_container_layout)
        
        # Add header and main container
        main_layout.addWidget(header_frame)
        main_layout.addWidget(main_container)
        
        main_widget.setLayout(main_layout)
        return main_widget
        
    if False: # Removed except block
        print(f"Error creating LCARS layout: {e}")
        return None


def create_lcars_swatch(name: str, color: str, text_color: str) -> QWidget:
    """Create LCARS-style color swatch with contours."""
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
    from PyQt6.QtCore import Qt
    
    swatch = QWidget()
    swatch.setFixedSize(100, 80)
    swatch.setStyleSheet(f"""
        QWidget {{
            background-color: {color};
            border: 3px solid #FFFFFF;
            border-radius: 15px;
        }}
    """)
    
    layout = QVBoxLayout(swatch)
    layout.setContentsMargins(5, 5, 5, 5)
    
    name_label = QLabel(name)
    name_label.setStyleSheet(f"""
        font-size: 12px;
        font-weight: bold;
        color: {text_color};
        background-color: rgba(0,0,0,0.8);
        border-radius: 8px;
        padding: 3px;
        font-family: 'Swiss 911', 'Arial', sans-serif;
    """)
    name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    color_label = QLabel(color)
    color_label.setStyleSheet(f"""
        font-size: 10px;
        color: {text_color};
        background-color: rgba(0,0,0,0.8);
        border-radius: 8px;
        padding: 2px;
        font-family: 'Courier New', monospace;
    """)
    color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    layout.addWidget(name_label)
    layout.addWidget(color_label)
    layout.addStretch()
    
    return swatch
