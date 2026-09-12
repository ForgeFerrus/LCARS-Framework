# -*- coding: utf-8 -*-
"""
LCARS Boot/Loading Screen з інтегрованим Faction Selection
Чистий boot screen що використовує систему тем
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFrame, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

# Додаємо шлях до проекту
if True:
    project_root = str(Path(__file__).parent.parent.parent)
if False: # Removed except block
    project_root = os.path.abspath(os.path.join(os.getcwd()))
    
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Імпорт системи тем
from lcars.themes.lcars_palette import LCARSEra, get_era_palette

# Використовуємо системні функції
if True:
    from lcars.ui.lock_screen import get_lcars_font_style, setup_lcars_font
if False: # Removed except block
    # Fallback якщо lock_screen недоступний
    def get_lcars_font_style(size, weight="normal"):
        weight_map = {"normal": "500", "bold": "700", "light": "300"}
        return f"""
            font-family: 'Antonio', 'Bank Gothic', 'Eurostile', sans-serif;
            font-size: {size}px;
            font-weight: {weight_map.get(weight, "500")};
            letter-spacing: 2px;
            text-transform: uppercase;
        """
    
    def setup_lcars_font():
        print("⚠️ Using basic font setup")
        return True


class FactionInfo:
    """Інформація про фракції - тільки базові дані, кольори з палітри"""
    FACTIONS = {
        'federation': {
            'name': 'United Federation of Planets',
            'era': LCARSEra.LCARS_25TH,
            'description': 'Peace • Exploration • Unity',
            'emblem': '◆'
        },
        'klingon': {
            'name': 'Klingon Empire', 
            'era': LCARSEra.PCARS_23RD,
            'description': 'Honor • Strength • Victory',
            'emblem': '◄►'
        },
        'romulan': {
            'name': 'Romulan Star Empire',
            'era': LCARSEra.LCARS_24TH,
            'description': 'Logic • Secrecy • Power', 
            'emblem': '♦'
        }
    }


class FactionLaunchButton(QPushButton):
    """Кнопка запуску фракції - використовує кольори з системи тем"""
    
    def __init__(self, faction_key, faction_data):
        super().__init__()
        self.faction_key = faction_key
        self.faction_data = faction_data
        
        self.setFixedSize(280, 80)
        self.setup_style()
        
    def setup_style(self):
        """Налаштування стилю з використанням палітри ери"""
        faction = self.faction_data
        
        # Отримуємо кольори з палітри ери замість хардкоджених
        era_colors = get_era_palette(faction['era'])
        primary_color = era_colors['button_colors'][0]
        accent_color = era_colors['button_colors'][1] if len(era_colors['button_colors']) > 1 else primary_color
        
        font_style = get_lcars_font_style(16, "bold")
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {primary_color};
                color: #000000;
                border: 2px solid {accent_color};
                border-radius: 12px;
                {font_style}
                text-align: center;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {accent_color};
                color: #000000;
                border: 2px solid #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: {primary_color};
                color: #FFFFFF;
            }}
        """)
        
        button_text = f"{faction['emblem']} {faction['name']}"
        self.setText(button_text)


class LCARSBootScreen(QMainWindow):
    """Boot screen з інтегрованим faction selection"""
    
    faction_selected = pyqtSignal(str, dict)  # Сигнал вибору фракції
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS OS - Initializing System")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.boot_stage = 0
        self.boot_messages = [
            "INITIALIZING LCARS OPERATING SYSTEM...",
            "LOADING CORE SUBSYSTEMS...", 
            "ESTABLISHING NETWORK PROTOCOLS...",
            "LOADING FACTION DATABASES...",
            "PREPARING USER INTERFACE...",
            "SYSTEM READY FOR FACTION SELECTION"
        ]
        
        # Стандартні кольори з палітри
        self.default_colors = get_era_palette(LCARSEra.LCARS_25TH)
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
        
        self.setup_boot_interface()
        
        # Boot animation timer
        self.boot_timer = QTimer()
        self.boot_timer.timeout.connect(self.advance_boot)
        self.boot_timer.start(1200)  # 1.2 секунди на стадію
        
        self.showFullScreen()
    
    def setup_boot_interface(self):
        """Налаштування інтерфейсу boot screen"""
        self.central = QWidget()
        self.setCentralWidget(self.central)
        
        layout = QVBoxLayout(self.central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top spacer
        layout.addStretch(1)
        
        # Center content
        self.center_container = QWidget()
        self.center_layout = QVBoxLayout(self.center_container)
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.setSpacing(40)
        
        # LCARS Logo/Emblem з системними кольорами
        emblem = QLabel("◆")
        emblem.setStyleSheet(f"""
            color: {self.default_colors['button_colors'][0]};
            font-size: 180px;
            font-weight: bold;
            background: transparent;
        """)
        emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(emblem)
        
        # System title
        title = QLabel("LCARS OPERATING SYSTEM")
        title_style = get_lcars_font_style(48, "bold")
        title.setStyleSheet(f"""
            color: {self.default_colors['text']['primary']};
            {title_style}
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(title)
        
        # Version info
        version = QLabel("VERSION 25.1.2026 - MULTI-FACTION SUPPORT")
        version_style = get_lcars_font_style(16, "normal")
        version.setStyleSheet(f"""
            color: {self.default_colors['text']['secondary']};
            {version_style}
            background: transparent;
        """)
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(version)
        
        self.center_layout.addSpacing(50)
        
        # Boot progress message
        self.boot_message = QLabel(self.boot_messages[0])
        message_style = get_lcars_font_style(24, "normal")
        self.boot_message.setStyleSheet(f"""
            color: {self.default_colors['button_colors'][2]};
            {message_style}
            background: transparent;
        """)
        self.boot_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(self.boot_message)
        
        # Progress indicator
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.setSpacing(8)
        
        self.progress_dots = []
        for i in range(8):
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {self.default_colors['button_colors'][0]}; font-size: 16px; background: transparent;")
            progress_layout.addWidget(dot)
            self.progress_dots.append(dot)
        
        self.center_layout.addWidget(progress_container)
        
        layout.addWidget(self.center_container, 2)
        
        # Bottom info
        footer = QLabel("UNITED FEDERATION OF PLANETS • KLINGON EMPIRE • ROMULAN STAR EMPIRE")
        footer_style = get_lcars_font_style(14, "light")
        footer.setStyleSheet(f"""
            color: {self.default_colors['text']['tertiary']};
            {footer_style}
            background: transparent;
            padding: 20px;
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
    
    def advance_boot(self):
        """Просування boot sequence"""
        # Оновити progress dots
        if self.boot_stage < len(self.progress_dots):
            self.progress_dots[self.boot_stage].setStyleSheet(
                f"color: {self.default_colors['button_colors'][2]}; font-size: 16px; background: transparent;"
            )
        
        self.boot_stage += 1
        
        if self.boot_stage < len(self.boot_messages):
            self.boot_message.setText(self.boot_messages[self.boot_stage])
        else:
            # Boot completed
            self.boot_timer.stop()
            self.show_faction_selection()
    
    def show_faction_selection(self):
        """Показати кнопки вибору фракцій"""
        # Змінити повідомлення
        self.boot_message.setText("SYSTEM READY - SELECT YOUR FACTION")
        self.boot_message.setStyleSheet(f"""
            color: {self.default_colors['status']['success']};
            {get_lcars_font_style(24, "bold")}
            background: transparent;
        """)
        
        # Додати кнопки фракцій
        faction_container = QWidget()
        faction_layout = QHBoxLayout(faction_container)
        faction_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        faction_layout.setSpacing(40)
        
        for faction_key, faction_data in FactionInfo.FACTIONS.items():
            faction_button = FactionLaunchButton(faction_key, faction_data)
            faction_button.clicked.connect(
                lambda checked, fk=faction_key, fd=faction_data: self.select_faction(fk, fd)
            )
            faction_layout.addWidget(faction_button)
        
        self.center_layout.addSpacing(30)
        self.center_layout.addWidget(faction_container)
    
    def select_faction(self, faction_key, faction_data):
        """Обробити вибір фракції"""
        print(f"🎯 Faction selected: {faction_data['name']} ({faction_data['era'].value})")
        
        # Візуальний ефект з кольорами ери
        era_colors = get_era_palette(faction_data['era'])
        effect_color = era_colors['button_colors'][0] + "33"  # 20% opacity
        
        self.setStyleSheet(f"QMainWindow {{ background-color: {effect_color}; }}")
        QTimer.singleShot(300, lambda: self.setStyleSheet("QMainWindow { background-color: #000000; }"))
        
        # Емітувати сигнал вибору фракції
        QTimer.singleShot(600, lambda: self.faction_selected.emit(faction_key, faction_data))


def main():
    """Test boot screen with integrated faction selection"""
    app = QApplication(sys.argv)
    setup_lcars_font()
    
    boot_screen = LCARSBootScreen()
    boot_screen.faction_selected.connect(
        lambda fk, fd: print(f"✅ Selected: {fd['name']} - {fd['era'].value}")
    )
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
