from PyQt6.QtWidgets import QPushButton, QWidget, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer, Qt
from lcars.themes.lcars_palette import (
    get_random_button_color, get_text_color, LCARSEra, get_era_palette
)
import random

# Каркаси кнопок для всіх епох Федерації з різними формами

class Starfleet22ndButton(QPushButton):
    """Кнопка 22-го століття (COMS) - прямокутна з гострими кутами"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.apply_22nd_theme()
        
    def apply_22nd_theme(self):
        # 22nd - Enterprise NX-01: прямокутна з гострими кутами як на реальному скріншоті
        bg_color = "#1E3A8A"  # темно-синій
        text_color = "#FFFFFF"  # білий текст
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid #4C4C7A;
                border-radius: 0px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
                font-family: 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: #2C4B9E;
            }}
            QPushButton:pressed {{
                background-color: #3B5DB8;
            }}
        """)

class Starfleet23rdButton(QWidget):
    """Кнопка 23-го століття (PCARS) - кругла форма"""
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.apply_23rd_theme()
        
    def apply_23rd_theme(self):
        # 23rd - TOS: кругла червона кнопка
        palette = get_era_palette(LCARSEra.PCARS_23RD)
        bg_color = palette['button_colors'][1]  # #FF0000 - червоний
        
        self.setFixedSize(120, 120)
        
        # Кругла кнопка
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: 3px solid #D3A200;
                border-radius: 60px;
            }}
        """)
        
        # Текст
        self.text_label = QLabel(self.text, self)
        self.text_label.setGeometry(10, 45, 100, 30)
        self.text_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
                background: transparent;
            }
        """)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

class Starfleet24thButton(QWidget):
    """Кнопка 24-го століття (LCARS TNG) - класична LCARS форма"""
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.apply_24th_theme()
        
    def apply_24th_theme(self):
        # 24th - TNG: класична LCARS з заокругленими кутами
        palette = get_era_palette(LCARSEra.LCARS_24TH)
        bg_color = palette['button_colors'][0]  # #FFCC66 - помаранчевий
        
        self.setFixedSize(180, 50)
        
        # Класична LCARS форма
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: 2px solid #664466;
                border-radius: 25px;
            }}
        """)
        
        # Текст
        self.text_label = QLabel(self.text, self)
        self.text_label.setGeometry(10, 10, 160, 30)
        self.text_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 14px;
                font-weight: bold;
                text-transform: uppercase;
                background: transparent;
                letter-spacing: 2px;
            }
        """)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

class Starfleet24stButton(QPushButton):
    """Кнопка 24-го століття (LCARS Sovereign)"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.apply_24st_theme()
    
    def apply_24st_theme(self):
        # 24st - Sovereign: темно-синій колір
        palette = get_era_palette(LCARSEra.LCARS_24ST)
        bg_color = palette['button_colors'][3]  # #CCDDFF - світло-синій
        text_color = "#000000"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
        """)

class Starfleet25thButton(QPushButton):
    """Кнопка 25-го століття (LCARS Titan)"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.apply_25th_theme()
    
    def apply_25th_theme(self):
        # Використовуємо перший колір з палітри 25th - темно-сірий
        palette = get_era_palette(LCARSEra.LCARS_25TH)
        bg_color = palette['button_colors'][0]  # #2F3749 - темно-сірий
        text_color = "#FFFFFF"  # Білий текст
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 17px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
        """)

class Starfleet29thButton(QPushButton):
    """Кнопка 29-го століття (TCARS)"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.apply_29th_theme()
    
    def apply_29th_theme(self):
        # Використовуємо перший колір з палітри 29th - блакитний
        palette = get_era_palette(LCARSEra.TCARS_29TH)
        bg_color = palette['button_colors'][0]  # #31C9F4 - блакитний
        text_color = "#000000"  # Чорний текст
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 18px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
        """)

# Універсальна кнопка з вибором епохи
class StarfleetButton(QPushButton):
    """Універсальна кнопка Федерації"""
    def __init__(self, text, era="24th", parent=None):
        super().__init__(text, parent)
        self.era = era
        self.apply_era_theme()
    
    def apply_era_theme(self):
        # Алгоритм вибору епохи
        era_map = {
            "22nd": LCARSEra.COMS_22ND,
            "23rd": LCARSEra.PCARS_23RD,
            "23st": LCARSEra.PCARS_23ST,
            "24th": LCARSEra.LCARS_24TH,
            "24st": LCARSEra.LCARS_24ST,
            "25th": LCARSEra.LCARS_25TH,
            "29th": LCARSEra.TCARS_29TH
        }
        
        lcars_era = era_map.get(self.era, LCARSEra.LCARS_24TH)
        bg_color = get_random_button_color(lcars_era)
        text_color = get_text_color()
        
        # Розмір шрифту залежно від епохи
        font_sizes = {"22nd": 14, "23rd": 15, "23st": 15, "24th": 16, "24st": 16, "25th": 17, "29th": 18}
        font_size = font_sizes.get(self.era, 16)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: {font_size}px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
        """)

# Фабричні функції
def create_22nd_button(text, parent=None):
    return Starfleet22ndButton(text, parent)

def create_23rd_button(text, parent=None):
    return Starfleet23rdButton(text, parent)

def create_24th_button(text, parent=None):
    return Starfleet24thButton(text, parent)

def create_25th_button(text, parent=None):
    return Starfleet25thButton(text, parent)

def create_29th_button(text, parent=None):
    return Starfleet29thButton(text, parent)

def create_starfleet_button(text, era="24th", parent=None):
    return StarfleetButton(text, era, parent)

# Демо - просто запустіть файл
if __name__ == "__main__":
    # Titanium Bridge Migration: import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
    
    app = QApplication(sys.argv)
    
    class DemoWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Starfleet Buttons Demo")
            self.setGeometry(100, 100, 1000, 700)
            
            widget = QWidget()
            self.setCentralWidget(widget)
            layout = QVBoxLayout(widget)
            
            # Заголовок
            title = QLabel("STARFLEET ERA BUTTONS")
            title.setStyleSheet("color: #FFCC66; font-size: 24px; font-weight: bold; padding: 20px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Кнопки кожної епохи
            eras = [
                ("22nd Century", create_22nd_button),
                ("23rd Century", create_23rd_button),
                ("24th Century", create_24th_button),
                ("25th Century", create_25th_button),
                ("29th Century", create_29th_button)
            ]
            
            for era_name, create_func in eras:
                label = QLabel(era_name)
                label.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold;")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(label)
                
                btn_layout = QHBoxLayout()
                btn1 = create_func("ENTERPRISE")
                btn2 = create_func("STARFLEET")
                btn3 = create_func("FEDERATION")
                
                btn_layout.addWidget(btn1)
                btn_layout.addWidget(btn2)
                btn_layout.addWidget(btn3)
                layout.addLayout(btn_layout)
            
            # Універсальні кнопки
            label = QLabel("Universal Buttons")
            label.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            
            uni_layout = QHBoxLayout()
            uni1 = create_starfleet_button("TNG", "24th")
            uni2 = create_starfleet_button("VOY", "25th")
            uni3 = create_starfleet_button("TOS", "23rd")
            
            uni_layout.addWidget(uni1)
            uni_layout.addWidget(uni2)
            uni_layout.addWidget(uni3)
            layout.addLayout(uni_layout)
            
            widget.setStyleSheet("background-color: #000022;")
    
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec())
