# PCARS22 Components - recreated based on existing structure
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QTimer
from lcars.themes.eras.primitives import Rect, Square, Circle
from lcars.themes.lcars_palette import get_palette_by_name, get_random_button_color, LCARSEra
import random

class PCARS22MiniButton(QPushButton):
    def __init__(self, label='MIN', size=50, color_index=0, parent=None):
        super().__init__(parent)
        
        # Отримуємо палітру для 22-го століття
        self.palette = get_palette_by_name("22nd")
        
        # Отримуємо колір з палітри кнопок
        button_colors = self.palette.get('button_colors', ['#269EEE'])
        self._color = QColor(button_colors[color_index % len(button_colors)])
        self.setFixedSize(size, size)
        
        # Створюємо квадратну кнопку
        self.square = Square(
            size=size, 
            color=self._color,
            border_color=QColor(self.palette.get('panel_border', '#444444')),
            border=1,
            parent=self
        )
        self.square.move(0, 0)
        
        # Налаштування тексту
        self.text_label = QLabel(label, self)
        font = QFont('Arial', max(8, int(size*0.2)))
        self.text_label.setFont(font)
        self.text_label.setStyleSheet(f"color: #000000; background: transparent;")
        self.text_label.setGeometry(0, int(size*0.62), size, int(size*0.32))
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.text_label.setWordWrap(True)
        
        # Таймер для зміни кольору
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._change_color)
        self._timer.start(5000)
    
    def _change_color(self):
        """Змінити колір кнопки"""
        button_colors = self.palette.get('button_colors', ['#269EEE'])
        new_color = QColor(button_colors[random.randint(0, len(button_colors)-1)])
        self._color = new_color
        self.square.color = new_color
        self.square.update()

class PCARS22Indicator(QWidget):
    def __init__(self, size=50, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        # Центрований круг без контурів
        self.circle = Circle(diameter=size-4, color="#FFF", border_color="#FFF", border=0, parent=self)
        self.circle.move(2, 2)  # Центрування
        
class PCARSText(QLabel):
    def __init__(self, text, font="JEFFE", size=18, color="#000000", vertical=False, parent=None):
        super().__init__(text, parent)
        self._vertical = vertical
        self.setFont(QFont(font, size, QFont.Weight.Bold))
        self.setStyleSheet(f"color: {color}; background: transparent;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
