from PyQt6.QtWidgets import QWidget, QPushButton, QLabel
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF, QFont
from PyQt6.QtCore import Qt, QPointF

# =========================
# BASE LCARS PRIMITIVE
# =========================

class LcarsPrimitive(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = "#FF9900"

    def setColor(self, color: str):
        self.color = color
        self.update()

# =========================
# GEOMETRIC PRIMITIVES
# =========================

class Rect(LcarsPrimitive):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(0, 0, self.width(), self.height())

class Square(Rect):
    def __init__(self, size=40, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

class Circle(LcarsPrimitive):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, self.width(), self.height())

class Triangle(LcarsPrimitive):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.color))
        points = [
            QPointF(self.width() / 2, 0),
            QPointF(self.width(), self.height()),
            QPointF(0, self.height())
        ]
        p.drawPolygon(QPolygonF(points))

class Trapezoid(LcarsPrimitive):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.color))
        w, h = self.width(), self.height()
        o = w * 0.25
        points = [
            QPointF(o, 0),
            QPointF(w - o, 0),
            QPointF(w, h),
            QPointF(0, h)
        ]
        p.drawPolygon(QPolygonF(points))

class Line(LcarsPrimitive):
    def __init__(self, orientation="h", parent=None):
        super().__init__(parent)
        self.orientation = orientation

    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(QPen(QColor(self.color), 4))
        if self.orientation == "h":
            p.drawLine(0, self.height() // 2, self.width(), self.height() // 2)
        else:
            p.drawLine(self.width() // 2, 0, self.width() // 2, self.height())

# =========================
# TEXT / FUNCTIONAL
# =========================

class LCARSLabel(QLabel):
    def __init__(self, text="LABEL", parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.setStyleSheet("color: black; background: transparent;")

    def setColor(self, color):
        self.setStyleSheet(f"color: {color}; background: transparent;")

class LCARSButton(QPushButton):
    def __init__(self, text="DATA", parent=None):
        super().__init__(text, parent)
        self.color = "#FF9900"
        self._apply_style()

    def setColor(self, color):
        self.color = color
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: black;
                border-radius: 14px;
                font-weight: bold;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: white;
            }}
        """)

# =========================
# LCARS PANELS / DISPLAYS
# =========================

class Panel(Rect):
    pass

class Display(Rect):
    pass

class Indicator(Rect):
    pass

# =========================
# UNIVERSAL FACTORY
# =========================

def get_universal_primitives():
    return {
        # Geometry
        "Rect": lambda parent=None: Rect(parent),
        "Square": lambda parent=None: Square(parent=parent),
        "Circle": lambda parent=None: Circle(parent),
        "Triangle": lambda parent=None: Triangle(parent),
        "Trapezoid": lambda parent=None: Trapezoid(parent),

        # Functional
        "Button": lambda parent=None: LCARSButton("DATA", parent),
        "Label": lambda parent=None: LCARSLabel("TEXT", parent),
        "Panel": lambda parent=None: Panel(parent),
        "Display": lambda parent=None: Display(parent),
        "Indicator": lambda parent=None: Indicator(parent),
    }
