"""
Klingon Interface Components
Aggressive, angular, high-contrast aesthetics for the Klingon Empire.
"""

from PyQt6.QtWidgets import QWidget, QPushButton, QFrame
from PyQt6.QtCore import Qt, QPoint, QPointF
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QBrush

from lcars.themes.palette import get_lcars_font_style, get_theme

# --- CONSTANTS ---
KLINGON_RED = "#CC0000"
KLINGON_RED_DARK = "#660000"
KLINGON_ORANGE = "#FF9900"
KLINGON_GOLD = "#D4AF37"  # Sometimes used for text
KLINGON_BLACK = "#110000"
# Use a font that looks sharp? "Impact" or system default bold.
KLINGON_FONT = "Impact"


class KlingonFrame(QFrame):
    """Base Klingon container"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {KLINGON_BLACK};
                border: 2px solid {KLINGON_RED};
                color: {KLINGON_ORANGE};
            }}
        """)


class KlingonButton(QPushButton):
    """
    Klingon Button: Sharp spikes/blades shape.
    Usually triangular or trapezoidal components.
    """

    def __init__(self, text, parent=None, color=KLINGON_RED):
        super().__init__(text, parent)
        self.color_base = color
        self.setMinimumHeight(60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        is_pressed = self.isDown()
        is_hover = self.underMouse()

        bg_color = QColor(self.color_base)
        if is_pressed:
            bg_color = bg_color.lighter(150)
        elif is_hover:
            bg_color = bg_color.lighter(120)

        w = self.width()
        h = self.height()

        # Shape: Bat'leth curve style or simple jagged geometry
        # Let's do a blade-like shape pointing right or blocky
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(w - 20, 0)
        path.lineTo(w, h / 2)  # Point
        path.lineTo(w - 20, h)
        path.lineTo(0, h)
        # Indent at start
        path.lineTo(10, h / 2)
        path.lineTo(0, 0)
        path.closeSubpath()

        # Fill
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(KLINGON_BLACK), 2))
        painter.drawPath(path)

        # Text
        painter.setPen(QColor(KLINGON_BLACK))
        font_style = get_lcars_font_style(14, "normal")
        # Extract family and size from style string if needed, or just set font
        painter.setFont(QFont("Arial Narrow", 14)) # fallback
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


class KlingonHeader(QWidget):
    """Bold Red/Black Header"""

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.setMinimumHeight(60)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Background
        painter.fillRect(self.rect(), QColor(KLINGON_RED_DARK))

        # Triangles at bottom?
        painter.setBrush(QColor(KLINGON_RED))
        painter.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        path.moveTo(0, self.height())
        path.lineTo(self.width(), self.height())
        path.lineTo(self.width(), self.height() - 10)
        path.lineTo(0, self.height() - 10)
        painter.drawPath(path)

        # Text
        painter.setPen(QColor(KLINGON_ORANGE))
        font = QFont(KLINGON_FONT, 28, QFont.Weight.Normal)
        painter.setFont(font)
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            "  " + self.text,
        )


class KlingonDisplay(QFrame):
    """Geometric Star/Target display common in Klingon UI (Authorization Contours)"""

    def __init__(self, text="TARGET", parent=None):
        super().__init__(parent)
        self.text = text
        self.setMinimumHeight(150)
        self.setStyleSheet(f"background-color: {KLINGON_BLACK};")

    def _draw_star(self, painter, x, y, size, color):
        """Aggressive 4-pointed star for Klingon tactical."""
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        points = [
            QPointF(x, y - size),
            QPointF(x + size*0.2, y - size*0.2),
            QPointF(x + size, y),
            QPointF(x + size*0.2, y + size*0.2),
            QPointF(x, y + size),
            QPointF(x - size*0.2, y + size*0.2),
            QPointF(x - size, y),
            QPointF(x - size*0.2, y - size*0.2)
        ]
        painter.drawPolygon(points)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = QPoint(self.width() // 2, self.height() // 2)
        radius = min(self.width(), self.height()) // 2 - 20

        # Replace circles with Starburst geometry
        self._draw_star(painter, center.x(), center.y(), radius, KLINGON_RED)
        self._draw_star(painter, center.x(), center.y(), radius * 0.6, KLINGON_ORANGE)

        # Crosshairs (Now with gaps for the star)
        painter.setPen(QPen(QColor(KLINGON_ORANGE), 1))
        painter.drawLine(center.x() - radius - 10, center.y(), center.x() - radius/2, center.y())
        painter.drawLine(center.x() + radius/2, center.y(), center.x() + radius + 10, center.y())
        painter.drawLine(center.x(), center.y() - radius - 10, center.x(), center.y() - radius/2)
        painter.drawLine(center.x(), center.y() + radius/2, center.x(), center.y() + radius + 10)

        # Text
        painter.setPen(QColor(KLINGON_ORANGE))
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            self.text,
        )
