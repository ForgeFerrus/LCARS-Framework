"""
LCARS Generic Widgets
Reusable text components, buttons, and containers for the LCARS framework.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QSize, QRect, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen

class AnimatedButton(QPushButton):
    """Standard animated color-changing LCARS button"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._color = QColor("#000000")
        
    @pyqtProperty(QColor)
    def color(self):
        return self._color
        
    @color.setter
    def color(self, color):
        self._color = color
        self.setStyleSheet(f"background-color: {color.name()}; border: none; border-radius: 15px; color: black; font-weight: bold;")
        
    def set_color(self, color):
        self.color = color
        
    def animate_to_color(self, target_color, duration=1000):
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setDuration(duration)
        self.animation.setStartValue(self._color)
        self.animation.setEndValue(QColor(target_color))
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()

class LcarsTile(QFrame):
    """Advanced Tile Widget for Applications with Title and Description"""
    clicked = pyqtSignal(bool)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._color = QColor("#37A6D1")
        
        # Internal Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)
        self.layout.setSpacing(5)
        
        # Decorator line (Technical detail)
        self.line = QFrame()
        self.line.setFixedHeight(4)
        self.line.setStyleSheet("background-color: rgba(0,0,0, 0.3); border-radius: 2px;")
        self.layout.addWidget(self.line)
        
        self.title_label = QLabel()
        self.title_label.setStyleSheet("background: transparent; border: none; color: black; font-weight: 900; font-size: 18px; font-family: 'Swis721 BT'; text-transform: uppercase;")
        
        self.desc_label = QLabel()
        self.desc_label.setStyleSheet("background: transparent; border: none; color: black; font-weight: normal; font-size: 12px; font-family: 'Swis721 BT';")
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.desc_label)
        
        # Technical footer number
        self.number_label = QLabel(str(id(self))[-4:]) 
        self.number_label.setStyleSheet("color: rgba(0,0,0, 0.5); font-size: 10px; font-weight: bold; font-family: 'Swis721 BT';")
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.number_label)
        
        self.setText(text)
        
    def setText(self, text):
        if "\n" in text:
            parts = text.split("\n", 1)
            self.title_label.setText(parts[0])
            self.desc_label.setText(parts[1])
        else:
            self.title_label.setText(text)
            self.desc_label.setText("")
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(True)
            
    @pyqtProperty(QColor)
    def color(self):
        return self._color
        
    @color.setter
    def color(self, color):
        self._color = color
        self.setStyleSheet(f"""
            LcarsTile {{
                background-color: {color.name()};
                border-radius: 20px;
                border-bottom-right-radius: 0px; 
            }}
            QLabel {{
                color: black;
                background: transparent;
            }}
        """)
        
    def set_color(self, color):
        self.color = color


class LcarsElbow(QWidget):
    """Iconic LCARS L-bend (Elbow) connector - 25th Century Style"""
    def __init__(self, color="#37A6D1", direction="top-left", size=(150, 80), parent=None):
        super().__init__(parent)
        self.color = color
        self.direction = direction
        self.setFixedSize(QSize(*size))

    def set_color(self, color):
        """Update color and repaint"""
        self.color = color
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.color))
        p.setPen(Qt.PenStyle.NoPen)
        
        w, h = self.width(), self.height()
        bar_height = 40  # Standard bar height
        curve_radius = 40
        
        path = QPainterPath()
        
        if self.direction == "top-left":
            # Horizontal top bar part
            path.moveTo(w, 0)
            path.lineTo(curve_radius + 20, 0)
            # Outer curve
            path.cubicTo(curve_radius, 0, 0, 0, 0, curve_radius)
            # Vertical down part
            path.lineTo(0, h)
            path.lineTo(bar_height, h) 
            path.lineTo(bar_height, curve_radius + 20)
            # Inner curve
            path.cubicTo(bar_height, bar_height, bar_height, bar_height, w, bar_height)
            
        p.drawPath(path)

class LcarsFrame(QFrame):
    """Custom LCARS styled container with header elbow"""
    def __init__(self, title, color="#37A6D1", parent=None):
        super().__init__(parent)
        self.title = title.upper()
        self.color = color
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 45, 10, 10)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        w, h = rect.width(), rect.height()
        
        # Header bar
        p.setBrush(QColor(self.color))
        p.setPen(Qt.PenStyle.NoPen)
        
        # Elbow
        thickness = 30
        path = QPainterPath()
        path.moveTo(thickness + 10, 0)
        path.lineTo(w - 20, 0)
        path.arcTo(w - 20, 0, 20, 20, 90, -90)
        path.lineTo(w, thickness)
        path.lineTo(thickness, thickness)
        path.arcTo(0, 0, thickness*2, thickness*2, 90, 90)
        path.lineTo(0, h)
        path.lineTo(10, h)
        path.lineTo(10, thickness)
        path.arcTo(10, thickness, 2, 2, 180, -90)
        path.lineTo(thickness + 10, thickness)
        path.closeSubpath()
        
        p.drawPath(path)
        
        # Title text
        p.setPen(QPen(QColor("#000000"), 2))
        font = QFont("Swis721 BT", 12, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(QRect(thickness + 20, 5, w - thickness - 40, thickness - 10), 
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.title)

