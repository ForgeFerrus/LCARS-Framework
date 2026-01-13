"""
Simple PCARS22 Panel - direct implementation
"""

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtCore import Qt, QTimer
from lcars.themes.lcars_palette import get_palette_by_name, LCARSEra, get_random_button_color
from lcars.themes.primitives import Rect, Circle, Square
import random


class PCARS22Screen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #000;")
        self.panel_rect = Rect(1, 1, color="#000000", border_color="#222", border=2, parent=self)
        self.inner_margin_left = 48
        self.inner_margin_right = 24
        self.inner_margin_top = 24
        self.inner_margin_bottom = 24
        self.screen_rect = Rect(1, 1, color="#222", border_color="#666", border=2, parent=self)
        self.vert_label = PCARSText("SCREEN", font="JEFFE", size=18, color="#000000", vertical=True, parent=self)
        # Додаємо одну міні-кнопку зліва внизу
        self.mini = PCARS22MiniButton(label='MIN', parent=self)
        # Додаємо велике коло з індикатором справа вгорі
        self.big_circle_right = Circle(diameter=40, color="#000000", border_color="#222", border=2, parent=self)
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


class PCARS22Panel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get palette
        self.palette = get_palette_by_name("22nd")
        self.setStyleSheet(f"background: {self.palette.get('background', '#000000')};")
        self.setMinimumSize(900, 600)
        
        # Create mini buttons from components
        self.mini_buttons = [
            PCARS22MiniButton(label="STD", size=80, color_index=0, parent=self),
            PCARS22MiniButton(label="DAT", size=80, color_index=1, parent=self),
            PCARS22MiniButton(label="MOD", size=80, color_index=2, parent=self),
        ]
        for btn in self.mini_buttons:
            btn.show()
        
        # Create real indicator
        self.indicator = PCARS22Indicator(size=40, parent=self)
        self.indicator.show()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Panel occupies the entire widget area
        panel_x = 0
        panel_y = 0
        panel_w = self.width()
        panel_h = self.height()
        
        # Panel itself - чорна
        painter.fillRect(panel_x, panel_y, panel_w, panel_h, QColor('#000000'))
        
        # Inner frame - сірий
        margin = 60
        inner_x = panel_x + margin
        inner_y = panel_y + margin
        inner_w = panel_w - 2*margin
        inner_h = panel_h - 2*margin
        
        painter.fillRect(inner_x, inner_y, inner_w, inner_h, QColor('#666666'))
        
        # Black rectangle inside - відсунута вліво
        inner_margin = 20
        black_x = inner_x + inner_margin + 50  # відсунута вліво
        black_y = inner_y + inner_margin
        black_w = inner_w - 2*inner_margin - 50  # менша ширина
        black_h = inner_h - 2*inner_margin
        
        painter.fillRect(black_x, black_y, black_w, black_h, QColor('#000000'))
        
        # Circle - сірий, в самий кут
        circle_x = panel_x + 30
        circle_y = panel_y + 30
        painter.setBrush(QBrush(QColor('#666666')))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(circle_x, circle_y, 60, 60)
        
        painter.end()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position mini buttons
        btn_size = 80
        btn_spacing = 20
        bottom_margin = 80
        
        for i, btn in enumerate(self.mini_buttons):
            btn_y = self.height() - bottom_margin - (i+1)*(btn_size + btn_spacing)
            btn.setGeometry(30, btn_y, btn_size, btn_size)
        
        # Position indicator inside circle
        self.indicator.move(30 + 20, 30 + 20)

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

class PCARS22Button(QWidget):
    """Композиція примітивів: Rect (фон), Rect (бар), Square (квадрат), Circle (круг), QLabel (номер, підпис)"""
    
    def __init__(self, number='00-0000', label='NAME', width=200, height=64, color=None, bar_color=None, border_color=None, border=1, parent=None):
        super().__init__(parent)
        
        # Отримуємо палітру для 22-го століття
        palette = get_palette_by_name("22nd")
        
        # Встановлюємо кольори за замовчуванням з палітри
        if color:
            self._color = QColor(color)
        else:
            # Беремо перший колір з button_colors
            button_colors = palette.get('button_colors', ['#269EEE'])
            self._color = QColor(button_colors[0])
        self._bar_color = QColor(bar_color or '#5C5C5C')
        self._border_color = QColor(border_color or palette.get('panel_border', '#444444'))
        
        self._era = LCARSEra.COMS_22ND
        self.setFixedSize(width, height)
        
        self._border = border
        self._width = width
        self._height = height
        self._number = number
        self._label = label
        
        bar_h = int(height * 0.28)
        square_size = int(height * 0.38)
        circle_d = int(square_size * 0.62)
        
        # Фон
        self.bg = Rect(width, height-bar_h, color=self._color, border_color=self._border_color, border=border, parent=self)
        self.bg.move(0, 0)
        
        # Бар
        self.bar = Rect(width, bar_h, color=self._bar_color, border_color=self._border_color, border=border, parent=self)
        self.bar.move(0, height-bar_h)
        
        # Квадрат
        self.square = Square(size=square_size, color=self._bar_color, border_color=self._border_color, border=border, parent=self)
        self.square.move(width - square_size - border, border)
        
        # Круг
        self.circle = Circle(diameter=circle_d, color=QColor('#FFFFFF'), border_color=self._bar_color, border=border, parent=self.square)
        self.circle.move((square_size-circle_d)//2, (square_size-circle_d)//2)
        
        # Номер
        self.number_label = QLabel(number, self)
        font_num = QFont('Arial', max(12, int((height-bar_h)*0.32)), QFont.Weight.Normal)
        self.number_label.setFont(font_num)
        self.number_label.setStyleSheet("color: #111;")
        self.number_label.setGeometry(0, int((height-bar_h)*0.18), width, int((height-bar_h)*0.32))
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        
        # Підпис
        self.text_label = QLabel(label, self)
        font_label = QFont('Arial', max(10, int(bar_h*0.5)), QFont.Weight.Normal)
        self.text_label.setFont(font_label)
        self.text_label.setStyleSheet("color: #111;")
        self.text_label.setGeometry(0, height-bar_h, width, bar_h)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        
        self.setStyleSheet("background: transparent;")
        
        # Таймер для зміни кольору
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._change_color)
        self._timer.start(5000)

    def _change_color(self):
        # Проста зміна кольору без залежності від імпортів
        colors = ['#269EEE', '#FFE600', '#5C5C5C', '#27F8FF', '#018D76']
        new_color = QColor(random.choice(colors))
        self.bg.color = new_color
        self._color = new_color
        self.bg.update()

    def mouseDoubleClickEvent(self, event):
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Змінити підпис", "Новий підпис:", text=self.text_label.text())
        if ok and text:
            self.text_label.setText(text)
            self._label = text

# === 22nd Century Custom Primitives ===
import math
class Radar22(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(420, 420)
        self.setMaximumSize(600, 600)
        self.angle_sector = (30, 90)  # degrees
        self.rings = 5
        self.segments = 12
        self.highlight_color = QColor("#FFE600")
        self.bg_color = QColor("#222")
        self.grid_color = QColor("#888")
        self.arc_color = QColor("#FFE600")
        
    def paintEvent(self, a0):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        r = min(w, h)//2 - 10
        cx, cy = w//2, h//2
        
        # background
        p.setBrush(self.bg_color)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(cx-r, cy-r, 2*r, 2*r)
        
        # grid
        p.setPen(QPen(self.grid_color, 1))
        for i in range(1, self.rings+1):
            p.drawEllipse(cx-i*r//self.rings, cy-i*r//self.rings, 2*i*r//self.rings, 2*i*r//self.rings)
        for i in range(self.segments):
            angle = i * 360 // self.segments
            x = cx + r * math.cos(math.radians(angle))
            y = cy - r * math.sin(math.radians(angle))
            p.drawLine(cx, cy, int(x), int(y))

class VerticalScale22(QWidget):
    def __init__(self, label="SCALE", parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 300)
        self.label = label
        self.value = 75
    def paintEvent(self, a0):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Background
        p.fillRect(10, 10, 60, 280, QColor("#222"))
        # Scale marks
        p.setPen(QPen(QColor("#FFE600"), 2))
        for i in range(0, 11):
            y = 30 + i * 25
            p.drawLine(15, y, 55, y)
        # Current value
        y = int(30 + (10 - self.value) * 2.5)
        p.fillRect(15, y, 40, 5, QColor("#FF0000"))

class LogBlock22(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 200)
        self.entries = [
            "SYSTEM STARTUP COMPLETE",
            "MAIN POWER ONLINE",
            "SENSORS ACTIVE",
            "COMM SYSTEMS READY"
        ]
    def paintEvent(self, a0):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Background
        p.fillRect(0, 0, self.width(), self.height(), QColor("#111"))
        # Border
        p.setPen(QPen(QColor("#FFE600"), 2))
        p.drawRect(1, 1, self.width()-2, self.height()-2)
        # Text
        p.setPen(QColor("#FFE600"))
        font = QFont("Courier", 10)
        p.setFont(font)
        for i, entry in enumerate(self.entries):
            p.drawText(10, 20 + i*20, entry)

# === Фабрика компонентів для Constructor ===
def _create_panel(parent):
    """Create PCARS22Panel to avoid circular import"""
    from lcars.themes.eras.PCARSPanel import PCARS22Panel
    return PCARS22Panel(parent=parent)

def get_base_components():
    return {
        'button': lambda parent=None: PCARS22Button(
            number='01-000',
            label='NAME',
            color=get_random_button_color(LCARSEra.PCARS_22ND),
            bar_color='#CCCCCC',
            border_color='#222',
            parent=parent
        ),
        'panel': lambda parent=None: _create_panel(parent),
        'screen': lambda parent=None: PCARS22Screen(parent=parent),
        'mini': lambda parent=None: PCARS22MiniButton(label='MIN', parent=parent),
        'indicator': lambda parent=None: PCARS22Indicator(parent=parent),
        'radar22': lambda parent=None: Radar22(parent=parent),
        'scale22': lambda parent=None: VerticalScale22(parent=parent),
        'log22': lambda parent=None: LogBlock22(parent=parent),
    }
