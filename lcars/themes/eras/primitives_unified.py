#!/usr/bin/env python3
"""
Unified LCARS Primitives - Single source of truth for all geometric shapes
Used by all LCARS interfaces (22nd, 23rd, 24th, 25th centuries)
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt6.QtCore import QRectF, QPointF


class LCARSPrimitive(QWidget):
    """Base class for all LCARS primitives"""
    
    def __init__(self, color="#FFCC66", border_color="#000000", border=2, parent=None):
        super().__init__(parent)
        self.color = color if isinstance(color, QColor) else QColor(color)
        self.border_color = border_color if isinstance(border_color, QColor) else QColor(border_color)
        self.border_width = border
    
    def setup_painter(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.border_color, self.border_width))


class Rect(LCARSPRimitive):
    """Rectangle primitive"""
    
    def __init__(self, width=50, height=50, color="#FFCC66", border_color="#000000", border=2, parent=None):
        super().__init__(color, border_color, border, parent)
        self.setFixedSize(width, height)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        self.setup_painter(painter)
        painter.drawRect(self.rect())


class Square(LCARSPRimitive):
    """Square primitive"""
    
    def __init__(self, size=50, color="#FFCC66", border_color="#000000", border=2, parent=None):
        super().__init__(color, border_color, border, parent)
        self.setFixedSize(size, size)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        self.setup_painter(painter)
        painter.drawRect(self.rect())


class Circle(LCARSPRimitive):
    """Circle primitive"""
    
    def __init__(self, diameter=50, color="#FFCC66", border_color="#000000", border=2, parent=None):
        super().__init__(color, border_color, border, parent)
        self.setFixedSize(diameter, diameter)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        self.setup_painter(painter)
        
        # Calculate circle bounds
        size = min(self.width(), self.height())
        rect = QRectF(
            (self.width() - size) / 2,
            (self.height() - size) / 2,
            size,
            size
        )
        painter.drawEllipse(rect)


class RoundedRectangle(LCARSPRimitive):
    """Rounded rectangle primitive"""
    
    def __init__(self, width=100, height=50, radius=10, color="#FFCC66", border_color="#000000", border=2, parent=None):
        super().__init__(color, border_color, border, parent)
        self.radius = radius
        self.setFixedSize(width, height)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        self.setup_painter(painter)
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)


class Triangle(LCARSPRimitive):
    """Triangle primitive"""
    
    def __init__(self, width=50, height=50, color="#FFCC66", border_color="#000000", border=2, parent=None):
        super().__init__(color, border_color, border, parent)
        self.setFixedSize(width, height)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        self.setup_painter(painter)
        
        # Calculate triangle points
        points = QPolygonF([
            QPointF(self.width() / 2, 0),           # Top point
            QPointF(0, self.height()),              # Bottom left
            QPointF(self.width(), self.height())    # Bottom right
        ])
        painter.drawPolygon(points)


class Diamond(LCARSPRimitive):
    """Diamond primitive"""
    
    def __init__(self, width=50, height=50, color="#FFCC66", border_color="#000000", border=2, parent=None):
        super().__init__(color, border_color, border, parent)
        self.setFixedSize(width, height)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        self.setup_painter(painter)
        
        # Calculate diamond points
        points = QPolygonF([
            QPointF(self.width() / 2, 0),          # Top point
            QPointF(self.width(), self.height() / 2),  # Right point
            QPointF(self.width() / 2, self.height()),    # Bottom point
            QPointF(0, self.height() / 2)          # Left point
        ])
        painter.drawPolygon(points)


class Hexagon(LCARSPRimitive):
    """Hexagon primitive"""
    
    def __init__(self, width=60, height=60, color="#FFCC66", border_color="#000000", border=2, parent=None):
        super().__init__(color, border_color, border, parent)
        self.setFixedSize(width, height)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        self.setup_painter(painter)
        
        # Calculate hexagon points
        points = QPolygonF([
            QPointF(self.width() * 0.25, 0),
            QPointF(self.width() * 0.75, 0),
            QPointF(self.width(), self.height() * 0.5),
            QPointF(self.width() * 0.75, self.height()),
            QPointF(self.width() * 0.25, self.height()),
            QPointF(0, self.height() * 0.5)
        ])
        painter.drawPolygon(points)


class Trapezoid(LCARSPRimitive):
    """Trapezoid primitive"""
    
    def __init__(self, width=80, height=50, color="#FFCC66", border_color="#000000", border=2, parent=None):
        super().__init__(color, border_color, border, parent)
        self.setFixedSize(width, height)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        self.setup_painter(painter)
        
        # Calculate trapezoid points
        points = QPolygonF([
            QPointF(self.width() * 0.2, 0),
            QPointF(self.width() * 0.8, 0),
            QPointF(self.width(), self.height()),
            QPointF(0, self.height())
        ])
        painter.drawPolygon(points)


class Indicator(LCARSPRimitive):
    """Circular indicator with text"""
    
    def __init__(self, diameter=60, color="#FFE600", text="READY", parent=None):
        super().__init__(color, "#000000", 2, parent)
        self.text = text
        self.setFixedSize(diameter, diameter)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        self.setup_painter(painter)
        
        # Draw circle
        size = min(self.width(), self.height())
        rect = QRectF(
            (self.width() - size) / 2,
            (self.height() - size) / 2,
            size,
            size
        )
        painter.drawEllipse(rect)
        
        # Draw text
        painter.setPen(QColor("#000000"))
        from PyQt6.QtGui import QFont
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)


# Registry of all primitives
PRIMITIVES = {
    'Rect': Rect,
    'Square': Square,
    'Circle': Circle,
    'RoundedRectangle': RoundedRectangle,
    'Triangle': Triangle,
    'Diamond': Diamond,
    'Hexagon': Hexagon,
    'Trapezoid': Trapezoid,
    'Indicator': Indicator,
}


def get_primitive(primitive_name):
    """Get primitive class by name"""
    return PRIMITIVES.get(primitive_name, Rect)


def create_primitive(primitive_name, **kwargs):
    """Create primitive instance"""
    primitive_class = get_primitive(primitive_name)
    return primitive_class(**kwargs)
