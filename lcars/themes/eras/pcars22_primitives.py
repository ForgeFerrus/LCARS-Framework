# PCARS22 Primitives - базові графічні примітиви для 22-го століття
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt

class Rect(QWidget):
    """Прямокутник"""
    def __init__(self, x=0, y=0, width=100, height=50, color="#000000", border_color="#FFFFFF", border=1, parent=None):
        super().__init__(parent)
        self.setGeometry(x, y, width, height)
        self.color = QColor(color)
        self.border_color = QColor(border_color)
        self.border = border
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(self.border_color, self.border))
        painter.setBrush(QColor(self.color))
        painter.drawRect(0, 0, self.width(), self.height())
        painter.end()

class Square(QWidget):
    """Квадрат"""
    def __init__(self, size=50, color="#000000", border_color="#FFFFFF", border=1, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.color = QColor(color)
        self.border_color = QColor(border_color)
        self.border = border
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(self.border_color, self.border))
        painter.setBrush(QColor(self.color))
        painter.drawRect(0, 0, self.width(), self.height())
        painter.end()

class Circle(QWidget):
    """Коло"""
    def __init__(self, diameter=50, color="#000000", border_color="#FFFFFF", border=1, parent=None):
        super().__init__(parent)
        self.setFixedSize(diameter, diameter)
        self.color = QColor(color)
        self.border_color = QColor(border_color)
        self.border = border
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(self.border_color, self.border))
        painter.setBrush(QColor(self.color))
        painter.drawEllipse(0, 0, self.width(), self.height())
        painter.end()