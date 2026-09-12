from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QSize, QRectF
from PyQt6.QtGui import QPainter, QPixmap, QIcon
from PyQt6.QtSvg import QSvgRenderer

class SVGButton(QPushButton):
    def __init__(self, svg_path, parent=None):
        super().__init__(parent)
        self.svg_path = svg_path
        self.renderer = QSvgRenderer(svg_path)
        
        print(f"SVG loaded: {self.renderer.isValid()}")
        print(f"SVG size: {self.renderer.defaultSize().width()}x{self.renderer.defaultSize().height()}")
        print(f"SVG viewBox: {self.renderer.viewBox()}")
        
        # Створюємо QPixmap з правильним розміром
        pixmap = QPixmap(120, 80)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Малюємо SVG на QPixmap з масштабуванням
        painter = QPainter(pixmap)
        # Масштабуємо великий SVG до нашого розміру
        target_rect = QRectF(0, 0, 120, 80)
        self.renderer.render(painter, target_rect)
        painter.end()
        
        print(f"Pixmap created: {not pixmap.isNull()}")
        
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(120, 80))
        
        self.setFixedSize(120, 80)
        self.setStyleSheet("background: transparent; border: none;")
        
    def paintEvent(self, event):
        super().paintEvent(event)
