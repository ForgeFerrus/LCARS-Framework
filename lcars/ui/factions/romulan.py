"""
Romulan Interface Components
Authentic Romulan Star Empire styling for LCARS Framework.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QBrush, QLinearGradient

# --- CONSTANTS ---
ROMULAN_FONT = "Impact" # Or "Arial Black" as a fallback for blocky look
ROMULAN_GREEN_DARK = "#003300"
ROMULAN_GREEN_MID = "#006633"
ROMULAN_GREEN_LIGHT = "#33CC66"
ROMULAN_TEAL = "#008080"
ROMULAN_GREY = "#2F4F4F" 
ROMULAN_TEXT_COLOR = "#99FF99"

class RomulanFrame(QFrame):
    """
    Base container with Romulan-styled borders (angular, no rounded corners).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ROMULAN_GREEN_DARK};
                border: 2px solid {ROMULAN_GREEN_MID};
                color: {ROMULAN_TEXT_COLOR};
            }}
        """)

class RomulanHeader(QWidget):
    """
    Top header bar with the Romulan emblem shape (Trapezoidal feel).
    """
    def __init__(self, title="IMPERIAL ACCESS", parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.title = title
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Background: Dark Green Gradient
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(ROMULAN_GREEN_MID))
        gradient.setColorAt(1, QColor(ROMULAN_GREEN_DARK))
        
        # Complex Shape
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(width, 0)
        path.lineTo(width, height)
        path.lineTo(width - 40, height) # Notch right
        path.lineTo(width - 60, height - 20) # Angle up
        path.lineTo(60, height - 20) # Flat mid
        path.lineTo(40, height) # Angle down
        path.lineTo(0, height)
        path.closeSubpath()
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        
        # Text
        painter.setPen(QColor(ROMULAN_TEXT_COLOR))
        font = QFont(ROMULAN_FONT, 24, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop, self.title)

class RomulanButton(QPushButton):
    """
    Hexagonal/Angled button.
    """
    def __init__(self, text, parent=None, color=ROMULAN_GREEN_MID):
        super().__init__(text, parent)
        self.color_base = color
        self.setMinimumHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_pressed = self.isDown()
        is_hover = self.underMouse()
        
        # Color Logic
        bg_color = QColor(self.color_base)
        if is_pressed:
            bg_color = bg_color.lighter(150)
        elif is_hover:
            bg_color = bg_color.lighter(120)
            
        width = self.width()
        height = self.height()
        offset = 15 # Angle depth
        
        # Shape: Cut corners (Octagon-ish / Hex-ish)
        path = QPainterPath()
        path.moveTo(offset, 0)
        path.lineTo(width, 0)
        path.lineTo(width, height - offset)
        path.lineTo(width - offset, height)
        path.lineTo(0, height)
        path.lineTo(0, offset)
        path.closeSubpath()
        
        # Draw Fill
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(ROMULAN_TEXT_COLOR), 1))
        painter.drawPath(path)
        
        # Draw Text
        painter.setPen(QColor("black") if is_pressed else QColor(ROMULAN_TEXT_COLOR))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class RomulanDisplay(QFrame):
    """
    Line graph / status display area.
    """
    def __init__(self, text="STATUS", parent=None):
        super().__init__(parent)
        self.text = text
        self.setMinimumHeight(120)
        self.setStyleSheet("background-color: black; border: 1px solid #336633;")
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QColor(ROMULAN_GREEN_LIGHT))
        font = QFont("Consolas", 10)
        painter.setFont(font)
        
        # Grid lines
        painter.setPen(QPen(QColor(ROMULAN_GREEN_DARK), 1, Qt.PenStyle.DotLine))
        for i in range(0, self.width(), 20):
            painter.drawLine(i, 0, i, self.height())
        for i in range(0, self.height(), 20):
            painter.drawLine(0, i, self.width(), i)
            
        # Random data line
        painter.setPen(QPen(QColor(ROMULAN_GREEN_LIGHT), 2))
        path = QPainterPath()
        path.moveTo(0, self.height()/2)
        import random
        for i in range(0, self.width(), 10):
            path.lineTo(i, self.height()/2 + random.randint(-40, 40))
        painter.drawPath(path)
        
        # Label
        painter.setPen(QColor(ROMULAN_TEXT_COLOR))
        painter.drawText(10, 20, self.text)
