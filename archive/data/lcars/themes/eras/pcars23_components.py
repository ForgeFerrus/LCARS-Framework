# PCARS23 Components - компоненти 23-го століття (TOS стиль)
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QTimer
from lcars.themes.palette import get_palette_by_name, get_random_button_color, LCARSEra

class PCARS23Button(QWidget):
    def __init__(self, label='NAME', number='00-TOS', width=180, height=54, color=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.label = label
        self.number = number
        
        # Динамічний колір з алгоритму
        self.dynamic_color = color or get_random_button_color(LCARSEra.PCARS_23RD)
        
        # Таймер для зміни кольору в часі
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_color)
        self.color_timer.start(3000)
        
        # TOS стиль - квадратна кнопка з легким скругленням
        self.bg = TOSButton23(self.dynamic_color, number, width, height, self)
        self.bg.move(0, 0)
        self.text_label = QLabel(label, self)
        self.text_label.setStyleSheet("color: #000; font-size: 16px; font-weight: bold; background: transparent;")
        self.text_label.setGeometry(0, int(height*0.7), width, int(height*0.3))
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.setStyleSheet("background: transparent;")
    
    def update_color(self):
        self.dynamic_color = get_random_button_color(LCARSEra.PCARS_23RD)
        self.bg.color = self.dynamic_color
        self.bg.update()

class PCARS23MiniButton(QWidget):
    def __init__(self, label='MINI', size=48, color=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.label = label
        
        # Динамічний колір з алгоритму
        self.dynamic_color = color or get_random_button_color(LCARSEra.PCARS_23RD)
        
        # Таймер для зміни кольору в часі
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_color)
        self.color_timer.start(3000)
        
        # TOS стиль - квадратна міні-кнопка з легким скругленням
        self.bg = TOSButton23(self.dynamic_color, '', size, size, self)
        self.bg.move(0, 0)
        self.text_label = QLabel(label, self)
        self.text_label.setStyleSheet("color: #000; font-size: 12px; font-weight: bold; background: transparent;")
        self.text_label.setGeometry(0, int(size*0.6), size, int(size*0.4))
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.setStyleSheet("background: transparent;")
    
    def update_color(self):
        self.dynamic_color = get_random_button_color(LCARSEra.PCARS_23RD)
        self.bg.color = self.dynamic_color
        self.bg.update()

# === TOS Primitives ===
class TOSButton23(QWidget):
    def __init__(self, color, text=None, width=80, height=40, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(width, height)
        self.text = text
    def paintEvent(self, a0):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor("#000"), 2))
        p.setBrush(QColor(self.color))
        # Квадратна кнопка TOS стилю з легким скругленням
        p.drawRoundedRect(2, 2, self.width()-4, self.height()-4, 5, 5)
        if self.text:
            p.setPen(QColor("#000"))
            font = QFont("Eurostile", 14, QFont.Weight.Bold)
            p.setFont(font)
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)

class CircleIndicator23(QWidget):
    def __init__(self, color, text=None, size=30, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(size, size)
        self.text = text
    def paintEvent(self, a0):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor("#000"), 2))
        p.setBrush(QColor(self.color))
        # Круглий індикатор TOS стилю
        radius = min(self.width(), self.height()) // 2 - 2
        center = self.rect().center()
        p.drawEllipse(center, radius, radius)
        if self.text:
            p.setPen(QColor("#000"))
            font = QFont("Eurostile", 12, QFont.Weight.Bold)
            p.setFont(font)
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)

class Block23(QWidget):
    def __init__(self, color, text=None, width=80, height=40, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(width, height)
        self.text = text
    def paintEvent(self, a0):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor("#000"), 2))
        p.setBrush(QColor(self.color))
        p.drawRect(2, 2, self.width()-4, self.height()-4)
        if self.text:
            p.setPen(QColor("#000"))
            font = QFont("Eurostile", 14, QFont.Weight.Bold)
            p.setFont(font)
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)

class DiagBar23(QWidget):
    def __init__(self, color1, color2, width=160, height=40, parent=None):
        super().__init__(parent)
        self.color1 = color1
        self.color2 = color2
        self.setFixedSize(width, height)
    def paintEvent(self, a0):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Лівий трикутник
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(self.color1))
        points = [
            self.rect().topLeft(),
            self.rect().bottomLeft(),
            self.rect().topRight()
        ]
        p.drawPolygon(*points)
        # Правий трикутник
        p.setBrush(QColor(self.color2))
        points = [
            self.rect().topRight(),
            self.rect().bottomRight(),
            self.rect().bottomLeft()
        ]
        p.drawPolygon(*points)

class Label23(QLabel):
    def __init__(self, text, color="#FF0000", size=22, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"color:{color};font-size:{size}px;font-family:'Eurostile','Arial';font-Weight.Normal;background:transparent;")
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

# === TOS Panel ===
class PCARS23Panel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        pal = get_palette_by_name('23rd')
        self.setStyleSheet(f"background: {pal.get('background', '#000000')};")
        self.setMinimumSize(1200, 800)
        
        # Створюємо компоненти
        self._create_components()
        # Встановлюємо позиції
        self.resizeEvent(None)
    
    def _create_components(self):
        # Верхні індикатори
        self.indicators_top = []
        top_colors = ["#FFE600", "#FFE600", "#FFE600", "#319319", "#319319", "#FFE600", "#FFE600", "#FFE600", "#FFE600"]
        top_texts = ["756", "305", "353", "319", "319", "234", "234", "234", "234"]
        for c, t in zip(top_colors, top_texts):
            self.indicators_top.append(CircleIndicator23(c, t, 25, self))
        
        # Червона лінія
        self.red_line = QWidget(self)
        self.red_line.setStyleSheet("background:#D80000;")
        
        # Верхні кнопки
        self.buttons_top = []
        button_colors = ["#FFE600", "#FFE600", "#FFE600", "#319319", "#319319", "#FFE600", "#FFE600", "#FFE600", "#FFE600"]
        button_texts = ["STD", "DAT", "MOD", "ANA", "VIS", "REP", "FIL", "DIR", "SRC"]
        for c, t in zip(button_colors, button_texts):
            self.buttons_top.append(TOSButton23(c, t, 50, 30, self))
        
        # Підписи
        self.label_top = Label23("DISTRIBUTION RESERVE SUPPLIES", color="#D80000", size=18, parent=self)
        self.label_bottom = Label23("OPERATIONAL PRIORITY ALLOCATIONS", color="#D80000", size=18, parent=self)
        
        # Середні кнопки
        self.mid_buttons = []
        mid_colors = ["#FFE600", "#FFE600", "#FFE600", "#FFE600", "#FFE600", "#FFE600", "#FFE600", "#FFE600"]
        mid_texts = ["234931", "45631", "998931", "734731", "0-0731", "76631", "676731", "45631"]
        for c, t in zip(mid_colors, mid_texts):
            self.mid_buttons.append(TOSButton23(c, t, 80, 35, self))
        
        # Діагональна смуга
        self.diag_bar = DiagBar23("#FFE600", "#319319", 280, 35, self)
        
        # Нижні індикатори
        self.indicators_bottom = []
        bot_colors = ["#234", "#432", "#234", "#453", "#319", "#319", "#319", "#302"]
        bot_texts = ["234", "432", "234", "453", "319", "319", "319", "302"]
        for c, t in zip(bot_colors, bot_texts):
            self.indicators_bottom.append(CircleIndicator23(c, t, 25, self))
    
    def resizeEvent(self, a0):
        # Базові позиції
        x_start = 50
        y_start = 50
        spacing = 35
        
        # Верхні індикатори
        for i, ind in enumerate(self.indicators_top):
            ind.move(x_start + i*spacing, y_start - 35)
        
        # Червона лінія
        self.red_line.setGeometry(x_start, y_start, 400, 4)
        
        # Верхні кнопки
        for i, btn in enumerate(self.buttons_top):
            btn.move(x_start + i*60, y_start + 15)
        
        # Верхній підпис
        self.label_top.move(x_start, y_start + 55)
        
        # Середні кнопки
        for i, btn in enumerate(self.mid_buttons):
            btn.move(x_start + i*90, y_start + 100)
        
        # Діагональна смуга
        self.diag_bar.move(x_start + 100, y_start + 150)
        
        # Нижній підпис
        self.label_bottom.move(x_start, y_start + 200)
        
        # Нижні індикатори
        for i, ind in enumerate(self.indicators_bottom):
            ind.move(x_start + i*spacing, y_start + 240)

# === Фабрика компонентів ===
def get_23rd_components():
    return {
        'button23': lambda parent=None: PCARS23Button(parent=parent),
        'mini23': lambda parent=None: PCARS23MiniButton(parent=parent),
        'block23': lambda parent=None: Block23(color="#FFE600", text="23RD", width=80, height=40, parent=parent),
        'diagbar23': lambda parent=None: DiagBar23(color1="#FFE600", color2="#319319", width=160, height=40, parent=parent),
        'label23': lambda parent=None: Label23(text="23RD CENTURY", color="#FF0000", size=22, parent=parent),
        'panel23': lambda parent=None: PCARS23Panel(parent=parent),
    }
