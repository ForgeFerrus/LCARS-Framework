from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QLabel
from lcars.themes.eras.pcars22_primitives import Rect, Circle, PCARSText
from lcars.themes.lcars_palette import LCARSEra, get_palette_by_name, get_random_button_color

class PCARS23Button(QWidget):
    def __init__(self, number='23-0000', label='NAME', width=200, height=64, parent=None):
        super().__init__(parent)
        pal = get_palette_by_name('23rd')
        self.setFixedSize(width, height)
        bar_h = int(height * 0.28)
        square_size = int(height * 0.38)
        circle_d = int(square_size * 0.62)
        # Фон
        self.bg = Rect(width, height-bar_h, color=get_random_button_color(LCARSEra.PCARS_23RD), border_color=pal['panel_border'], border=2, parent=self)
        self.bg.move(0, 0)
        # Бар
        self.bar = Rect(width, bar_h, color=pal['panel_border'], border_color=pal['panel_border'], border=2, parent=self)
        self.bar.move(0, height-bar_h)
        # Квадрат
        self.square = Rect(width=square_size, height=square_size, color=pal['panel_border'], border_color=pal['panel_border'], border=2, parent=self)
        self.square.move(width - square_size - 2, 2)
        # Круг
        self.circle = Circle(diameter=circle_d, color=pal['text'], border_color=pal['panel_border'], border=2, parent=self.square)
        self.circle.move((square_size-circle_d)//2, (square_size-circle_d)//2)
        # Номер
        self.number_label = QLabel(number, self)
        font_num = QFont('Arial', max(12, int((height-bar_h)*0.32)), QFont.Weight.Normal)
        self.number_label.setFont(font_num)
        self.number_label.setStyleSheet(f"color: {pal['background']};")
        self.number_label.setGeometry(0, int((height-bar_h)*0.18), width, int((height-bar_h)*0.32))
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        # Підпис
        self.text_label = QLabel(label, self)
        font_label = QFont('Arial', max(10, int(bar_h*0.5)), QFont.Weight.Normal)
        self.text_label.setFont(font_label)
        self.text_label.setStyleSheet(f"color: {pal['background']};")
        self.text_label.setGeometry(0, height-bar_h, width, bar_h)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.setStyleSheet("background: transparent;")
        self.show()
