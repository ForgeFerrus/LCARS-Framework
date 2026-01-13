# PCARS23 Components - компоненти 23-го століття
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from PyQt6.QtCore import Qt
from lcars.themes.lcars_palette import get_palette_by_name

class PCARS23Button(QWidget):
    def __init__(self, label='NAME', number='00-TOS', width=180, height=54, color='#FFE600', parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.bg = Block23(color, number, width, int(height*0.6), self)
        self.bg.move(0, 0)
        self.text_label = QLabel(label, self)
        self.text_label.setStyleSheet("color: #222; font-size: 18px; font-weight: bold; background: transparent;")
        self.text_label.setGeometry(0, int(height*0.6), width, int(height*0.4))
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.setStyleSheet("background: transparent;")

class PCARS23MiniButton(QWidget):
    def __init__(self, label='MINI', size=48, color='#FFE600', parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.bg = Block23(color, '', size, size, self)
        self.bg.move(0, 0)
        self.text_label = QLabel(label, self)
        self.text_label.setStyleSheet("color: #222; font-size: 14px; font-weight: bold; background: transparent;")
        self.text_label.setGeometry(0, int(size*0.55), size, int(size*0.4))
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.setStyleSheet("background: transparent;")

# === 23rd Century Custom Primitives ===
class Block23(QWidget):
    def __init__(self, color, text=None, width=80, height=40, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(width, height)
        self.text = text
    def paintEvent(self, a0):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(self.color))
        p.drawRect(0, 0, self.width(), self.height())
        if self.text:
            p.setPen(QColor("#000") if self.color.lower()!="#d80000" else QColor("#fff"))
            font = QFont("Eurostile", 18, QFont.Weight.Bold)
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
        # Draw left triangle
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(self.color1))
        points = [
            self.rect().topLeft(),
            self.rect().bottomLeft(),
            self.rect().topRight()
        ]
        p.drawPolygon(*points)
        # Draw right triangle
        p.setBrush(QColor(self.color2))
        points2 = [
            self.rect().bottomLeft(),
            self.rect().bottomRight(),
            self.rect().topRight()
        ]
        p.drawPolygon(*points2)

class Label23(QLabel):
    def __init__(self, text, color="#FF0000", size=22, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"color:{color};font-size:{size}px;font-family:'Eurostile','Arial';font-weight:bold;background:transparent;")
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

# === 23rd Century Panel ===
class PCARS23Panel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        pal = get_palette_by_name('23rd')
        self.setStyleSheet(f"background: {pal['background']};")
        self.setMinimumSize(1200, 800)
        
        # --- Верхні блоки ---
        self.blocks_top = []
        top_colors = ["#FFE600", "#FFE600", "#FFE600", "#319319", "#319319", "#FFE600", "#FFE600", "#FFE600", "#FFE600"]
        top_texts = ["756", "305", "353", "319", "319", "234", "234", "234", "234"]
        for i, (c, t) in enumerate(zip(top_colors, top_texts)):
            b = Block23(c, t, 60, 36, self)
            self.blocks_top.append(b)
            
        # --- Нижні блоки ---
        self.blocks_bottom = []
        bot_colors = ["#234", "#432", "#234", "#453", "#319", "#319", "#319", "#302"]
        bot_texts = ["234", "432", "234", "453", "319", "319", "319", "302"]
        for i, (c, t) in enumerate(zip(bot_colors, bot_texts)):
            b = Block23(c, t, 60, 36, self)
            self.blocks_bottom.append(b)
            
        # --- Червона лінія ---
        self.red_line = QWidget(self)
        self.red_line.setStyleSheet("background:#D80000;")
        self.red_line.setFixedHeight(6)
        
        # --- Підпис ---
        self.label_top = Label23("DISTRIBUTION RESERVE SUPPLIES", color="#D80000", size=22, parent=self)
        
        # --- Середні блоки ---
        self.mid_blocks = []
        mid_colors = ["#FFE600", "#FFE600", "#FFE600", "#FFE600", "#FFE600", "#FFE600", "#FFE600", "#FFE600"]
        mid_texts = ["234931", "45631", "998931", "734731", "0-0731", "76631", "676731", "45631"]
        for i, (c, t) in enumerate(zip(mid_colors, mid_texts)):
            b = Block23(c, t, 100, 40, self)
            self.mid_blocks.append(b)
            
        # --- Діагональна смуга ---
        self.diag_bar = DiagBar23("#FFE600", "#319319", 320, 40, self)
        
        # --- Нижній підпис ---
        self.label_bottom = Label23("OPERATIONAL PRIORITY ALLOCATIONS", color="#D80000", size=22, parent=self)
        
        # --- Layout ---
        self.resizeEvent(None)

    def resizeEvent(self, a0):
        w, h = self.width(), self.height()
        # Верхні блоки
        x0 = 80
        y0 = 40
        for i, b in enumerate(self.blocks_top):
            b.move(x0 + i*70, y0)
        # Нижні блоки
        yb = h - 80
        for i, b in enumerate(self.blocks_bottom):
            b.move(x0 + i*70, yb)
        # Червона лінія
        self.red_line.setGeometry(x0, y0+50, w-2*x0, 6)
        # Верхній підпис
        self.label_top.setGeometry(x0, y0+60, w-2*x0, 32)
        # Середні блоки
        ym = y0+120
        for i, b in enumerate(self.mid_blocks):
            b.move(x0 + i*110, ym)
        # Діагональна смуга
        self.diag_bar.move(x0+100, ym+60)
        # Нижній підпис
        self.label_bottom.setGeometry(x0, ym+120, w-2*x0, 32)

# === Фабрика компонентів 23-го століття ===
def get_23rd_components():
    return {
        'button23': lambda parent=None: PCARS23Button(parent=parent),
        'mini23': lambda parent=None: PCARS23MiniButton(parent=parent),
        'block23': lambda parent=None: Block23(color="#FFE600", text="23RD", width=80, height=40, parent=parent),
        'diagbar23': lambda parent=None: DiagBar23(color1="#FFE600", color2="#319319", width=160, height=40, parent=parent),
        'label23': lambda parent=None: Label23(text="23RD CENTURY", color="#FF0000", size=22, parent=parent),
        'panel23': lambda parent=None: PCARS23Panel(parent=parent),
    }
