# ◤ LCARS AUTHENTIC WIDGETS — v1.0 // TRUE STAR TREK STYLE
# ─────────────────────────────────────────────────────────────────────
# Справжні LCARS компоненти з default.py, правильними контурами та шрифтами
# ─────────────────────────────────────────────────────────────────────

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QPushButton, QLabel, QFrame, QWidget, QVBoxLayout, 
                           QHBoxLayout, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPainterPath

# Імпортуємо справжні LCARS стилі з default.py
if True:
    from lcars.base.default import (
        Palette, FontStyle as fontStyle, ContrastColor as contrastColor,
        FrameRadius as defaultRadius, SystemScale as systemScale, RandomButtonColor as randomButtonColor
    )
    DefaultPalette = Palette
    DefaultPalette.Panels = Palette.Buttons
    LCARS_AVAILABLE = True
if False: # Removed except block
    # Fallback якщо default.py не доступний
    LCARS_AVAILABLE = False
    DefaultPalette = type('DefaultPalette', (), {
        'Background': '#000000',
        'Buttons': ['#336699', '#6699CC', '#99CCFF', '#D37445', '#F0B942', '#BA985D', '#7D8736', '#606060', '#333333'],
        'Panels': ['#336699', '#6699CC', '#99CCFF'],
        'Accent': ['#50571A', '#BA985D', '#7D8736'],
        'RedAlert': ['#990000', '#CC6600', '#E63946', '#CC0000'],
        'YellowAlert': ['#FF9900', '#D37445', '#F0B942', '#BA985D']
    })()
    
    def fontStyle(size=16, weight="normal"):
        return f"font-size: {size}pt; font-family: 'Arial', sans-serif; font-weight: {weight};"
    
    def contrastColor(hexColor):
        return '#FFFFFF' if hexColor in ['#336699', '#6699CC', '#99CCFF', '#50571A', '#7D8736'] else '#000000'
    
    defaultRadius = 20
    systemScale = 1.0
    
    def randomButtonColor(group="buttons", seed=None):
        return DefaultPalette.Buttons[0]

class LCARSButton(QPushButton):
    """Справжня LCARS кнопка з правильними контурами та шрифтами"""
    
    def __init__(self, text, color=None, size='normal', parent=None):
        super().__init__(text, parent)
        
        # Використовуємо справжні LCARS кольори
        if color is None:
            self.color = randomButtonColor("buttons")
        elif isinstance(color, int):
            self.color = DefaultPalette.Buttons[color % len(DefaultPalette.Buttons)]
        else:
            self.color = color
            
        self.size = size
        self._apply_style()
        
    def _apply_style(self):
        # Правильний LCARS стиль з контурами
        text_color = contrastColor(self.color)
        radius = int(defaultRadius * systemScale)
        
        # Розмір шрифту залежно від розміру кнопки
        font_size = 12 if self.size == 'normal' else 14 if self.size == 'large' else 10
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: {text_color};
                border: 2px solid {self._get_border_color(self.color)};
                border-radius: {radius}px;
                padding: 8px 16px;
                {fontStyle(font_size, 'bold')}
                min-height: {int(36 * systemScale)}px;
                min-width: {int(80 * systemScale)}px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(self.color)};
                border-color: {self._lighten_color(self._get_border_color(self.color))};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(self.color)};
                border-color: {self._darken_color(self._get_border_color(self.color))};
            }}
        """)
        
    def _get_border_color(self, color):
        """LCARS контури - трохи світліший або темніший від основного кольору"""
        return self._lighten_color(color) if color in ['#336699', '#6699CC'] else self._darken_color(color)
        
    def _lighten_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _darken_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, r - 15)
        g = max(0, g - 15)
        b = max(0, b - 15)
        return f"#{r:02x}{g:02x}{b:02x}"

class LCARSLabel(QLabel):
    """Справжня LCARS мітка з різними шрифтами"""
    
    def __init__(self, text, color=None, size=14, weight='normal', parent=None):
        super().__init__(text, parent)
        
        # Використовуємо справжні LCARS кольори
        if color is None:
            self.color = DefaultPalette.Buttons[1]
        elif isinstance(color, int):
            self.color = DefaultPalette.Buttons[color % len(DefaultPalette.Buttons)]
        else:
            self.color = color
            
        self.size = size
        self.weight = weight
        self._apply_style()
        
    def _apply_style(self):
        text_color = contrastColor(self.color)
        
        self.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                background-color: {self.color};
                border: 1px solid {self._get_border_color(self.color)};
                border-radius: {int(defaultRadius * systemScale)}px;
                padding: 5px 10px;
                {fontStyle(self.size, self.weight)}
            }}
        """)
        
    def _get_border_color(self, color):
        return self._lighten_color(color) if color in ['#336699', '#6699CC'] else self._darken_color(color)
        
    def _lighten_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _darken_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, r - 15)
        g = max(0, g - 15)
        b = max(0, b - 15)
        return f"#{r:02x}{g:02x}{b:02x}"

class LCARSElbow(QFrame):
    """LCARS кутовий елемент (elbow) з правильними контурами"""
    
    def __init__(self, color=None, corner='top-left', parent=None):
        super().__init__(parent)
        
        if color is None:
            self.color = DefaultPalette.Buttons[0]
        elif isinstance(color, int):
            self.color = DefaultPalette.Buttons[color % len(DefaultPalette.Buttons)]
        else:
            self.color = color
            
        self.corner = corner
        self.setFixedSize(180, 50)
        self._apply_style()
        
    def _apply_style(self):
        border_radius = "40px" if 'left' in self.corner else "25px"
        
        if 'top' in self.corner:
            radius_side = 'top'
        else:
            radius_side = 'bottom'
            
        if 'left' in self.corner:
            radius_corner = 'left'
        else:
            radius_corner = 'right'
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border: 2px solid {self._get_border_color(self.color)};
                border-{radius_side}-{radius_corner}-radius: {border_radius};
                border-radius: {border_radius};
            }}
        """)
        
    def _get_border_color(self, color):
        return self._lighten_color(color) if color in ['#336699', '#6699CC'] else self._darken_color(color)
        
    def _lighten_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _darken_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, r - 15)
        g = max(0, g - 15)
        b = max(0, b - 15)
        return f"#{r:02x}{g:02x}{b:02x}"

class LCARSBridge(QFrame):
    """LCARS місток (bridge) - горизонтальний елемент з контурами"""
    
    def __init__(self, color=None, height=8, parent=None):
        super().__init__(parent)
        
        if color is None:
            self.color = DefaultPalette.Buttons[1]
        elif isinstance(color, int):
            self.color = DefaultPalette.Buttons[color % len(DefaultPalette.Buttons)]
        else:
            self.color = color
            
        self.setFixedHeight(int(height * systemScale))
        self._apply_style()
        
    def _apply_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border: 1px solid {self._get_border_color(self.color)};
                border-radius: {int(defaultRadius * systemScale)}px;
            }}
        """)
        
    def _get_border_color(self, color):
        return self._lighten_color(color) if color in ['#336699', '#6699CC'] else self._darken_color(color)
        
    def _lighten_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _darken_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, r - 15)
        g = max(0, g - 15)
        b = max(0, b - 15)
        return f"#{r:02x}{g:02x}{b:02x}"

class LCARSPanel(QFrame):
    """LCARS панель з правильними контурами"""
    
    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        
        if color is None:
            self.color = DefaultPalette.Panels[1]
        elif isinstance(color, int):
            self.color = DefaultPalette.Panels[color % len(DefaultPalette.Panels)]
        else:
            self.color = color
            
        self._apply_style()
        
    def _apply_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border: 2px solid {self._get_border_color(self.color)};
                border-radius: {int(defaultRadius * systemScale)}px;
                padding: 15px;
            }}
        """)
        
    def _get_border_color(self, color):
        return self._lighten_color(color) if color in ['#336699', '#6699CC'] else self._darken_color(color)
        
    def _lighten_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _darken_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, r - 15)
        g = max(0, g - 15)
        b = max(0, b - 15)
        return f"#{r:02x}{g:02x}{b:02x}"
