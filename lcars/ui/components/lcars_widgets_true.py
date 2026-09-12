# ◤ LCARS AUTHENTIC WIDGETS — v2.0 // TRUE STAR TREK STYLE
# ─────────────────────────────────────────────────────────────────────
# Справжні LCARS компоненти: БЕЗ контурів, з default.py функціями
# ─────────────────────────────────────────────────────────────────────

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QPushButton, QLabel, QFrame, QWidget, QVBoxLayout, 
                           QHBoxLayout, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Використовуємо справжні функції з default.py
if True:
    from lcars.base.default import Palette, SystemTheme, SystemScale
    # Створюємо локальні асоціації для сумісності
    DefaultPalette = Palette
    randomButtonColor = SystemTheme.RandomButtonColor
    contrastColor = SystemTheme.ContrastColor
    fontStyle = SystemTheme.FontStyle
    defaultRadius = 30
    systemScale = SystemScale
    LCARS_AVAILABLE = True
if False: # Removed except block
    # Fallback якщо default.py не доступний
    LCARS_AVAILABLE = False

class LCARSButton(QPushButton):
    """Справжня LCARS кнопка: БЕЗ контурів, з default.py функціями"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        # Використовуємо randomButtonColor з default.py
        self.color = randomButtonColor("buttons")
        self._apply_style()
        
    def _apply_style(self):
        # LCARS: НІЯКИХ контурів, з fontStyle та contrastColor з default.py
        text_color = contrastColor(self.color)
        radius = int(defaultRadius * systemScale)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: {text_color};
                border: none;
                border-radius: {radius}px;
                padding: 8px 16px;
                {fontStyle(12, 'bold')}
                min-height: {int(36 * systemScale)}px;
                min-width: {int(80 * systemScale)}px;
            }}
            QPushButton:hover {{
                background-color: #88BBEE;
            }}
            QPushButton:pressed {{
                background-color: #4477AA;
            }}
        """)

class LCARSLabel(QLabel):
    """Справжня LCARS мітка: БЕЗ контурів, з default.py функціями"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        # Використовуємо randomButtonColor з default.py
        self.color = randomButtonColor("buttons")
        self._apply_style()
        
    def _apply_style(self):
        # LCARS: НІЯКИХ контурів, з fontStyle та contrastColor з default.py
        text_color = contrastColor(self.color)
        
        self.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                background-color: {self.color};
                border: none;
                padding: 5px;
                {fontStyle(14, 'normal')}
            }}
        """)

class LCARSElbow(QFrame):
    """Справжній LCARS elbow: БЕЗ контурів, з default.py функціями"""
    
    def __init__(self, corner='top-left', parent=None):
        super().__init__(parent)
        self.corner = corner
        # Використовуємо randomButtonColor з default.py
        self.color = randomButtonColor("buttons")
        self.setFixedSize(180, 50)
        self._apply_style()
        
    def _apply_style(self):
        # LCARS: НІЯКИХ контурів, з defaultRadius та systemScale
        radius = int(defaultRadius * systemScale)
        border_radius = f"{radius * 2}px" if 'left' in self.corner else f"{radius}px"
        
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
                border: none;
                border-{radius_side}-{radius_corner}-radius: {border_radius};
                border-radius: {border_radius};
            }}
        """)

class LCARSBridge(QFrame):
    """Справжній LCARS bridge: БЕЗ контурів, з default.py функціями"""
    
    def __init__(self, height=8, parent=None):
        super().__init__(parent)
        # Використовуємо randomButtonColor з default.py
        self.color = randomButtonColor("buttons")
        self.setFixedHeight(int(height * systemScale))
        self._apply_style()
        
    def _apply_style(self):
        # LCARS: НІЯКИХ контурів, з defaultRadius та systemScale
        radius = int(defaultRadius * systemScale)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border: none;
                border-radius: {radius}px;
            }}
        """)

class LCARSPanel(QFrame):
    """Справжня LCARS панель: БЕЗ контурів, з default.py функціями"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Використовуємо DefaultPalette.Background з default.py
        self._apply_style()
        
    def _apply_style(self):
        # LCARS: НІЯКИХ контурів, з DefaultPalette.Background та defaultRadius
        radius = int(defaultRadius * systemScale)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {DefaultPalette.Background};
                border: none;
                border-radius: {radius}px;
                padding: 15px;
            }}
        """)
