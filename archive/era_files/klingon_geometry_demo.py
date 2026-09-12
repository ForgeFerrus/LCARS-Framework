"""
Klingon LCARS-style Trapezoid Button
Authentic Klingon interface elements with proper geometry
"""

from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient, QBrush, QFont, QPainterPath
import math

class TrapezoidButton(QPushButton):
    """Authentic Klingon LCARS-style trapezoid button"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(200, 60)
        self.setStyleSheet("background: transparent; border: none;")
        
    def paintEvent(self, event):
        """Draw trapezoid button with Klingon styling"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create trapezoid path
        path = QPainterPath()
        width = self.width()
        height = self.height()
        
        # Klingon-style trapezoid with angled sides
        path.moveTo(10, height)  # Bottom left
        path.lineTo(width - 10, height)  # Bottom right
        path.lineTo(width - 5, 5)  # Top right (angled)
        path.lineTo(5, 5)  # Top left (angled)
        path.closeSubpath()
        
        # Gradient fill
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor(255, 69, 0))  # Orange-red
        gradient.setColorAt(0.5, QColor(139, 0, 0))  # Dark red
        gradient.setColorAt(1, QColor(255, 140, 0))  # Orange
        
        painter.fillPath(path, QBrush(gradient))
        
        # Border styling
        pen = QPen(QColor(255, 215, 0))  # Gold border
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # Inner border for depth
        inner_pen = QPen(QColor(255, 255, 255))  # White inner
        inner_pen.setWidth(1)
        painter.setPen(inner_pen)
        
        # Draw inner trapezoid
        inner_path = QPainterPath()
        inner_path.moveTo(15, height - 5)
        inner_path.lineTo(width - 15, height - 5)
        inner_path.lineTo(width - 8, 10)
        inner_path.lineTo(8, 10)
        inner_path.closeSubpath()
        painter.drawPath(inner_path)
        
        # Text
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class HexagonalPanel(QWidget):
    """Hexagonal panel for Klingon interface"""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setFixedSize(300, 200)
        
    def paintEvent(self, event):
        """Draw hexagonal panel"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        
        # Create hexagon path
        path = QPainterPath()
        hex_size = min(width, height) * 0.4
        
        for i in range(6):
            angle = i * 60 * math.pi / 180
            x = center_x + hex_size * math.cos(angle)
            y = center_y + hex_size * math.sin(angle)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        
        path.closeSubpath()
        
        # Fill with gradient
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor(139, 0, 0, 180))  # Dark red with transparency
        gradient.setColorAt(1, QColor(255, 69, 0, 120))  # Orange-red with transparency
        
        painter.fillPath(path, QBrush(gradient))
        
        # Border
        pen = QPen(QColor(255, 215, 0))  # Gold
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # Title text
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = QFont("Arial", 14, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(10, 30, self.title)

class DiagonalDisplay(QWidget):
    """Diagonal display panel with angled corners"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 250)
        
    def paintEvent(self, event):
        """Draw diagonal display panel"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Create diagonal rectangle path
        path = QPainterPath()
        path.moveTo(20, height)  # Bottom left
        path.lineTo(width, height - 20)  # Bottom right (angled up)
        path.lineTo(width - 20, 0)  # Top right (angled left)
        path.lineTo(0, 20)  # Top left (angled down)
        path.closeSubpath()
        
        # Background gradient
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor(0, 0, 0))  # Black
        gradient.setColorAt(0.7, QColor(139, 0, 0))  # Dark red
        gradient.setColorAt(1, QColor(255, 69, 0))  # Orange-red
        
        painter.fillPath(path, QBrush(gradient))
        
        # Multi-layered borders for LCARS effect
        # Outer border (gold)
        pen = QPen(QColor(255, 215, 0))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # Middle border (white)
        pen.setColor(QColor(255, 255, 255))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Inner path
        inner_path = QPainterPath()
        inner_path.moveTo(25, height - 5)
        inner_path.lineTo(width - 5, height - 25)
        inner_path.lineTo(width - 25, 5)
        inner_path.lineTo(5, 25)
        inner_path.closeSubpath()
        painter.drawPath(inner_path)

class KlingonGeometryWidget(QWidget):
    """Main widget demonstrating authentic Klingon geometry"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI with authentic Klingon elements"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title hexagonal panel
        title_panel = HexagonalPanel("KLINGON COMMAND")
        layout.addWidget(title_panel)
        
        # Trapezoid buttons row
        button_row = QHBoxLayout()
        
        btn1 = TrapezoidButton("TACTICAL")
        btn2 = TrapezoidButton("WEAPONS")
        btn3 = TrapezoidButton("SHIELDS")
        btn4 = TrapezoidButton("ENGINEERING")
        
        button_row.addWidget(btn1)
        button_row.addWidget(btn2)
        button_row.addWidget(btn3)
        button_row.addWidget(btn4)
        
        layout.addLayout(button_row)
        
        # Diagonal display
        display = DiagonalDisplay()
        layout.addWidget(display)
        
        # More trapezoid buttons
        control_row = QHBoxLayout()
        
        btn5 = TrapezoidButton("COMMUNICATIONS")
        btn6 = TrapezoidButton("SENSORS")
        btn7 = TrapezoidButton("NAVIGATION")
        
        control_row.addWidget(btn5)
        control_row.addWidget(btn6)
        control_row.addWidget(btn7)
        
        layout.addLayout(control_row)
        
        self.setLayout(layout)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Set dark theme
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QMainWindow {
            background-color: #000000;
        }
    """)
    
    widget = KlingonGeometryWidget()
    widget.setWindowTitle("Authentic Klingon LCARS Geometry")
    widget.resize(800, 600)
    widget.show()
    
    sys.exit(app.exec())
