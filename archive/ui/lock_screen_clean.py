"""
LCARS Lock Screen - ЗА ВАШИМ ДИЗАЙНОМ
Точно як на скріншоті з CorelDRAW
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFrame, QApplication, QLineEdit)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase

# Шлях до проекту
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Імпорти готових систем
from lcars.themes.lcars_palette import LCARSEra, get_era_palette
from lcars.ui.lock_screen import get_lcars_font_style, setup_lcars_font

# Шрифт вже готовий
LCARS_FONT_FAMILY = "Antonio"

def setup_lcars_font():
    """Використовуємо готову функцію"""
    # Імпортуємо готову функцію
    from lcars.ui.lock_screen import setup_lcars_font as original_setup
    return original_setup()

def get_lcars_font_style(size, weight="normal"):
    """Використовуємо готову функцію"""
    from lcars.ui.lock_screen import get_lcars_font_style as original_style
    return original_style(size, weight)

class LCARSButton(QPushButton):
    """LCARS кнопка з готовою палітрою"""
    
    def __init__(self, text, era=LCARSEra.LCARS_25TH, button_index=0, width=150, height=40):
        super().__init__(text)
        self.setFixedSize(width, height)
        
        # Використовуємо готову палітру
        colors = get_era_palette(era)
        color = colors['button_colors'][button_index % len(colors['button_colors'])]
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #000000;
                border: none;
                border-radius: 8px;
                {get_lcars_font_style(14, "normal")}
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #FF9900;
            }}
            QPushButton:pressed {{
                background-color: #CC5500;
            }}
        """)

class LCARSBar(QFrame):
    """LCARS бар з готовою палітрою"""
    
    def __init__(self, era=LCARSEra.LCARS_25TH, color_index=0, width=None, height=40):
        super().__init__()
        if width:
            self.setFixedSize(width, height)
        else:
            self.setFixedHeight(height)
            
        # Використовуємо готову палітру
        colors = get_era_palette(era)
        color = colors['button_colors'][color_index % len(colors['button_colors'])]
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                border-radius: 0px;
            }}
        """)

class PasswordField(QLineEdit):
    """Поле паролю із зірочками"""
    
    def __init__(self, era=LCARSEra.LCARS_25TH):
        super().__init__()
        self.setEchoMode(QLineEdit.EchoMode.Password)
        self.setFixedSize(200, 30)
        
        # Використовуємо готову палітру
        colors = get_era_palette(era)
        accent_color = colors['button_colors'][0]
        
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: #333333;
                color: #FFFFFF;
                border: 2px solid {accent_color};
                border-radius: 4px;
                {get_lcars_font_style(16, "normal")}
                padding: 4px 8px;
            }}
            QLineEdit:focus {{
                border: 2px solid #FF0000;
            }}
        """)
        self.setPlaceholderText("PASSWORD")

class LCARSLockScreen(QMainWindow):
    """Головний клас Lock Screen"""
    
    # Сигнали
    authentication_success = pyqtSignal()
    access_granted = pyqtSignal()
    
    def __init__(self, faction="federation", era="25th"):
        super().__init__()
        
        # Налаштування вікна
        self.setWindowTitle(f"LCARS - {faction.upper()} {era} Century")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
        
        # Параметри
        self.faction = faction
        self.era = era
        self.current_era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.current_era)  # Використовуємо готову палітру
        
        self.setup_interface()
        
    def setup_interface(self):
        """Створити інтерфейс"""
        self.central = QWidget()
        self.setCentralWidget(self.central)
        
        layout = QVBoxLayout(self.central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Верхні бари
        self.create_top_bars(layout)
        
        # Головний контент
        self.create_main_content(layout)
        
        # Нижні бари
        self.create_bottom_bars(layout)
        
    def create_top_bars(self, layout):
        """Створити верхні LCARS бари"""
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(20, 20, 20, 0)
        top_layout.setSpacing(8)
        
        # Перший бар
        bar1_layout = QHBoxLayout()
        bar1 = LCARSBar(self.colors['button_colors'][0], height=40)
        ship_label = QLabel("U.S.S. \"ODYSSEY\"")
        ship_label.setFixedWidth(250)
        ship_label.setStyleSheet("color: #FFCC99; font-size: 16px; font-weight: bold;")
        
        bar1_layout.addWidget(bar1, 1)
        bar1_layout.addWidget(ship_label)
        top_layout.addLayout(bar1_layout)
        
        # Другий бар
        bar2_layout = QHBoxLayout()
        bar2 = LCARSBar(self.colors['button_colors'][1], height=30)
        registry_label = QLabel("NCC-1071 ENTERPRISE-F")
        registry_label.setFixedWidth(250)
        registry_label.setStyleSheet("color: #FFCC99; font-size: 14px;")
        
        bar2_layout.addWidget(bar2, 1)
        bar2_layout.addWidget(registry_label)
        top_layout.addLayout(bar2_layout)
        
        layout.addWidget(top_container)
        
    def create_main_content(self, layout):
        """Створити головний контент"""
        main_container = QWidget()
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(20, 40, 20, 40)
        main_layout.setSpacing(20)
        
        # Ліві індикатори
        self.create_side_indicators(main_layout, "left")
        
        # Центральний контент
        self.create_center_content(main_layout)
        
        # Праві індикатори  
        self.create_side_indicators(main_layout, "right")
        
        layout.addWidget(main_container, 1)
        
    def create_side_indicators(self, layout, side):
        """Створити бокові індикатори"""
        container = QWidget()
        indicator_layout = QVBoxLayout(container)
        indicator_layout.setSpacing(12)
        
        count = 8 if side == "left" else 6
        for i in range(count):
            color_index = i if side == "left" else i + 5
            color = self.colors['button_colors'][color_index % len(self.colors['button_colors'])]
            indicator = LCARSBar(color, 20, 40)
            indicator_layout.addWidget(indicator)
            
        indicator_layout.addStretch()
        layout.addWidget(container)
        
    def create_center_content(self, layout):
        """Створити центральний контент"""
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setSpacing(40)
        
        # Емблема
        emblem = QLabel("◆")
        emblem.setStyleSheet("color: #FF6600; font-size: 100px;")
        emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(emblem)
        
        # Заголовок
        title = QLabel("THE LCARS COMPUTER NETWORK")
        title.setStyleSheet(f"""
            color: {self.colors['button_colors'][0]};
            {get_lcars_font_style(36, "normal")}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(title)
        
        # Підзаголовок
        subtitle = QLabel(f"{self.faction.upper()} {self.era} CENTURY - AUTHORIZED ACCESS ONLY")
        subtitle.setStyleSheet(f"""
            color: #FFCC99;
            {get_lcars_font_style(16, "normal")}
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(subtitle)
        
        center_layout.addSpacing(20)
        
        # Progress індикатор
        self.create_progress_indicator(center_layout)
        
        center_layout.addSpacing(20)
        
        # Кнопки
        self.create_buttons(center_layout)
        
        layout.addWidget(center_container, 1)
        
    def create_progress_indicator(self, layout):
        """Створити progress індикатор"""
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.setSpacing(8)
        
        for i in range(8):
            dot = QLabel("●")
            dot.setStyleSheet("color: #FF6600; font-size: 14px;")
            progress_layout.addWidget(dot)
        
        layout.addWidget(progress_container)
        
    def create_buttons(self, layout):
        """Створити кнопки управління"""
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(15)
        
        # Кнопка входу
        access_btn = LCARSButton("ACCESS DESKTOP", 
                                self.colors['button_colors'][0], 
                                width=350, height=60)
        access_btn.clicked.connect(self.grant_access)
        button_layout.addWidget(access_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Кнопка фракції
        faction_btn = LCARSButton(f"FACTION: {self.faction.upper()}", 
                                 self.colors['button_colors'][1], 
                                 width=300, height=45)
        button_layout.addWidget(faction_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Кнопка Alert
        alert_btn = LCARSButton("RED ALERT", 
                               self.colors['button_colors'][2], 
                               width=200, height=40)
        alert_btn.clicked.connect(self.show_alert)
        button_layout.addWidget(alert_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(button_container)
        
    def create_bottom_bars(self, layout):
        """Створити нижні бари"""
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(20, 0, 20, 20)
        bottom_layout.setSpacing(8)
        
        bar3 = LCARSBar(self.colors['button_colors'][2], height=30)
        bottom_layout.addWidget(bar3)
        
        bar4 = LCARSBar(self.colors['button_colors'][3], height=40)
        bottom_layout.addWidget(bar4)
        
        layout.addWidget(bottom_container)
        
    def grant_access(self):
        """Надати доступ"""
        self.authentication_success.emit()
        self.access_granted.emit()
        self.launch_desktop()
        
    def show_alert(self):
        """Показати попередження"""
        # Проста зміна кольору фону
        if self.styleSheet() == "QMainWindow { background-color: #000000; }":
            self.setStyleSheet("QMainWindow { background-color: #1a0000; }")
        else:
            self.setStyleSheet("QMainWindow { background-color: #000000; }")
        
    def launch_desktop(self):
        """Запустити робочий стіл"""
        if True:
            # Titanium Bridge Migration: import subprocess
            # Спроба запустити головний інтерфейс
            subprocess.Popen([sys.executable, "lcars_os.py"], cwd=project_root)
            self.close()
        if False: # Removed except block
            print(f"Desktop launch error: {e}")
            # Fallback - просто закрити
            self.close()


def main():
    """Головна функція"""
    app = QApplication(sys.argv)
    
    setup_lcars_font()
    
    lock_screen = LCARSLockScreen()
    lock_screen.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
