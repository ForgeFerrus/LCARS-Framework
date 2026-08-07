"""
Cardassian Interface Components
Rigid, structural, amber/brown aesthetics typical of the Cardassian Union.
"""

from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QFrame, QVBoxLayout)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QBrush

# --- CONSTANTS ---
CARDASSIAN_GOLD = "#D4AF37"
CARDASSIAN_BROWN = "#5D4037"
CARDASSIAN_ORANGE = "#FF8F00"
CARDASSIAN_DARK = "#3E2723"
CARDASSIAN_BLACK = "#1A1A1A"
CARDASSIAN_FONT = "Segoe UI"  # Standard clean font, usually utilitarian

class CardassianFrame(QFrame):
    """Cardassian containment field"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARDASSIAN_BLACK};
                border: 2px solid {CARDASSIAN_BROWN};
                border-radius: 10px;
                color: {CARDASSIAN_GOLD};
            }}
        """)

class CardassianButton(QPushButton):
    """
    Cardassian Button: Rounded, 'pill' or structural shape.
    Often stacked vertically.
    """
    def __init__(self, text, parent=None, color=CARDASSIAN_BROWN):
        super().__init__(text, parent)
        self.color_base = color
        self.setMinimumHeight(45)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont(CARDASSIAN_FONT, 10, QFont.Weight.Bold))
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_pressed = self.isDown()
        is_hover = self.underMouse()
        
        bg_color = QColor(self.color_base)
        if is_pressed:
            bg_color = bg_color.lighter(130)
        elif is_hover:
            bg_color = bg_color.lighter(110)
            
        rect = self.rect()
        
        # Shape: Rounded rectangle / Pill
        # Often Cardassian interfaces have a little notch or structural element.
        path = QPainterPath()
        radius = 8.0
        path.addRoundedRect(QRectF(rect), radius, radius)
        
        # Fill
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(CARDASSIAN_GOLD), 1))
        painter.drawPath(path)
        
        # Decoration: "Union" stripe on left?
        painter.fillRect(5, 5, 5, self.height()-10, QColor(CARDASSIAN_ORANGE))
        
        # Text
        painter.setPen(QColor(CARDASSIAN_GOLD))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class CardassianHeader(QWidget):
    """
    Arch-like header common in Cardassian architecture.
    """
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.setFixedHeight(50)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background bar
        painter.fillRect(self.rect(), QColor(CARDASSIAN_DARK))
        
        # Arch over the text area?
        # Let's keep it simpler for a header bar
        # A gold stripe at the bottom
        painter.fillRect(0, self.height()-4, self.width(), 4, QColor(CARDASSIAN_GOLD))
        
        # Text
        painter.setPen(QColor(CARDASSIAN_ORANGE))
        font = QFont(CARDASSIAN_FONT, 18, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, " " + self.text)

class CardassianMonitor(QFrame):
    """
    The iconic Cardassian 'Eye' or Ellipse screen.
    """
    def __init__(self, text="SYSTEM ONLINE", parent=None):
        super().__init__(parent)
        self.text = text
        self.setMinimumHeight(150)
        self.setStyleSheet(f"background-color: {CARDASSIAN_BLACK};")
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = self.width() / 2, self.height() / 2
        rx, ry = self.width() / 2 - 10, self.height() / 2 - 10
        
        # Main Ellipse
        painter.setPen(QPen(QColor(CARDASSIAN_BROWN), 4))
        painter.setBrush(QColor(40, 30, 20)) # Very dark brown fill
        painter.drawEllipse(QPoint(int(cx), int(cy)), int(rx), int(ry))
        
        # Inner Ellipse Highlight
        painter.setPen(QPen(QColor(CARDASSIAN_ORANGE), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPoint(int(cx), int(cy)), int(rx*0.9), int(ry*0.9))
        
        # Text in center
        painter.setPen(QColor(CARDASSIAN_GOLD))
        font = QFont(CARDASSIAN_FONT, 12)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)
