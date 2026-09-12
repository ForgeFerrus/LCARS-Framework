from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPixmap, QIcon
from PyQt6.QtSvg import QSvgRenderer

class SVGInterface(QWidget):
    def __init__(self, svg_path, parent=None):
        super().__init__(parent)
        self.svg_path = svg_path
        self.renderer = QSvgRenderer(svg_path)
        
        self.setFixedSize(800, 600)
        self.setStyleSheet("background: transparent; border: none;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Малюємо SVG прямо на віджеті
        target_rect = QRectF(0, 0, 800, 600)
        self.renderer.render(painter, target_rect)
        
        painter.end()
