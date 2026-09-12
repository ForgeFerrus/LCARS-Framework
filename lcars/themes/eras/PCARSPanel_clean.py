"""
Simple PCARS22 Panel - direct implementation
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtCore import Qt
from lcars.themes.lcars_palette import get_palette_by_name
from lcars.themes.eras.primitives import Rect, Circle, Square
from lcars.themes.eras.pcars22_components import PCARS22Indicator, PCARS22MiniButton, PCARSText


class PCARS22Screen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #000;")
        self.panel_rect = Rect(1, 1, color="#1A1A1A", border_color="#222", border=2, parent=self)
        self.inner_margin_left = 48
        self.inner_margin_right = 24
        self.inner_margin_top = 24
        self.inner_margin_bottom = 24
        self.screen_rect = Rect(1, 1, color="#222", border_color="#666", border=2, parent=self)
        self.vert_label = PCARSText("SCREEN", font="JEFFE", size=18, color="#FFFFFF", vertical=True, parent=self)
        # Додаємо одну міні-кнопку зліва внизу
        self.mini = PCARS22MiniButton(label='MIN', parent=self)
        # Додаємо велике коло з індикатором справа вгорі
        self.big_circle_right = Circle(diameter=40, color="#1A1A1A", border_color="#222", border=2, parent=self)
        self.indicator_right = PCARS22Indicator(size=20, parent=self.big_circle_right)
        self.panel_rect.show()
        self.screen_rect.show()
        self.vert_label.show()
        self.mini.show()
        self.big_circle_right.show()
        self.indicator_right.show()
        self.resizeEvent(None)
        
    def resizeEvent(self, a0):
        w, h = self.width(), self.height()
        self.panel_rect.setGeometry(0, 0, w, h)
        screen_x = self.inner_margin_left
        screen_y = self.inner_margin_top
        screen_w = max(40, w - self.inner_margin_left - self.inner_margin_right)
        screen_h = max(40, h - self.inner_margin_top - self.inner_margin_bottom)
        self.screen_rect.setGeometry(screen_x, screen_y, screen_w, screen_h)
        self.vert_label.setGeometry(0, 0, self.inner_margin_left, h)
        # Розміщення міні-кнопки зліва внизу
        btn_size = 56
        self.mini.setGeometry(10, h - btn_size - 10, btn_size, btn_size)
        # Велике коло з індикатором справа вгорі
        self.big_circle_right.setGeometry(w-60, 10, 40, 40)
        self.indicator_right.setGeometry(10, 20, 20, 20)
