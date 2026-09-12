# -*- coding: utf-8 -*-
"""
LCARS Faction & Era Selection Screen
Вибір фракції та епохи для автентичного досвіду
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFrame, QGridLayout, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QFontDatabase

# Додаємо шлях до проекту
if True:
    project_root = str(Path(__file__).parent.parent.parent)
if False: # Removed except block
    project_root = os.path.abspath(os.path.join(os.getcwd()))
    
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.themes.lcars_palette import LCARSEra, get_era_palette

# Підключення LCARS шрифтів
font_path = os.path.join(project_root, "resources", "fonts", "lcars.ttf")
LCARS_FONT_FAMILY = "Antonio"

def setup_lcars_font():
    """Setup LCARS font"""
    global LCARS_FONT_FAMILY
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                LCARS_FONT_FAMILY = font_families[0]
                return True
    
    fallback_fonts = ["Antonio", "Bank Gothic", "Eurostile", "Oswald"]
    available_fonts = QFontDatabase.families()
    for font in fallback_fonts:
        if font in available_fonts:
            LCARS_FONT_FAMILY = font
            return True
    return False

def get_selector_font_style(size, weight="normal"):
    """Стиль шрифту для selector"""
    weight_map = {"normal": "500", "bold": "700", "light": "300"}
    return f"""
        font-family: '{LCARS_FONT_FAMILY}', 'Antonio', 'Bank Gothic', sans-serif;
        font-size: {size}px;
        font-weight: {weight_map.get(weight, "500")};
        letter-spacing: 2px;
        text-transform: uppercase;
    """


class FactionInfo:
    """Інформація про фракції"""
    FACTIONS = {
        'federation': {
            'name': 'United Federation of Planets',
            'era': LCARSEra.LCARS_25TH,
            'description': 'Peace • Exploration • Unity',
            'color': '#FF6600',
            'emblem': '◆',
            'established': '2161'
        },
        'klingon': {
            'name': 'Klingon Empire',
            'era': LCARSEra.PCARS_23RD,
            'description': 'Honor • Strength • Victory',
            'color': '#CC0000',
            'emblem': '◄►',
            'established': '900'
        },
        'romulan': {
            'name': 'Romulan Star Empire',
            'era': LCARSEra.LCARS_24TH,
            'description': 'Logic • Secrecy • Power',
            'color': '#009900',
            'emblem': '♦',
            'established': '387'
        }
    }


class FactionButton(QPushButton):
    """Кнопка вибору фракції з автентичним стилем"""
    
    def __init__(self, faction_key, faction_data):
        super().__init__()
        self.faction_key = faction_key
        self.faction_data = faction_data
        
        self.setFixedSize(350, 120)
        self.setup_style()
        
    def setup_style(self):
        """Налаштування стилю кнопки"""
        faction = self.faction_data
        
        # Отримуємо кольори з палітри ери
        era_colors = get_era_palette(faction['era'])
        primary_color = era_colors['button_colors'][0]
        
        font_style = get_selector_font_style(18, "bold")
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {primary_color};
                color: #000000;
                border: 3px solid {faction['color']};
                border-radius: 15px;
                {font_style}
                text-align: center;
                padding: 15px;
            }}
            QPushButton:hover {{
                background-color: {faction['color']};
                color: #FFFFFF;
                border: 3px solid #FFFFFF;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #000000;
                color: {faction['color']};
                border: 3px solid {faction['color']};
            }}
        """)
        
        # Текст кнопки
        button_text = f"{faction['emblem']}\n{faction['name']}\n{faction['description']}"
        self.setText(button_text)


class LCARSFactionSelector(QMainWindow):
    """Екран вибору фракції та ери"""
    
    faction_selected = pyqtSignal(str, dict)  # faction_key, faction_data
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS OS - Faction Selection")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        # Стилізація
        self.setStyleSheet("QMainWindow { background-color: #0a0a0a; }")
        
        self.setup_selector_interface()
        self.showFullScreen()
    
    def setup_selector_interface(self):
        """Налаштування інтерфейсу селектора"""
        self.central = QWidget()
        self.setCentralWidget(self.central)
        
        layout = QVBoxLayout(self.central)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(40)
        
        # Заголовок
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.setSpacing(20)
        
        main_title = QLabel("FACTION SELECTION PROTOCOL")
        main_title_style = get_selector_font_style(56, "bold")
        main_title.setStyleSheet(f"""
            color: #FF6600;
            {main_title_style}
            background: transparent;
        """)
        main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(main_title)
        
        subtitle = QLabel("SELECT YOUR ALLEGIANCE TO PROCEED WITH AUTHENTICATION")
        subtitle_style = get_selector_font_style(24, "normal")
        subtitle.setStyleSheet(f"""
            color: #FFCC99;
            {subtitle_style}
            background: transparent;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_container)
        
        # Фракції
        factions_container = QWidget()
        factions_layout = QHBoxLayout(factions_container)
        factions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        factions_layout.setSpacing(60)
        
        for faction_key, faction_data in FactionInfo.FACTIONS.items():
            faction_group = QWidget()
            faction_group_layout = QVBoxLayout(faction_group)
            faction_group_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            faction_group_layout.setSpacing(20)
            
            # Кнопка фракції
            faction_button = FactionButton(faction_key, faction_data)
            faction_button.clicked.connect(
                lambda checked, fk=faction_key, fd=faction_data: self.select_faction(fk, fd)
            )
            faction_group_layout.addWidget(faction_button)
            
            # Додаткова інформація
            era_info = QLabel(f"ERA: {faction_data['era'].value}")
            era_style = get_selector_font_style(14, "normal")
            era_info.setStyleSheet(f"""
                color: {faction_data['color']};
                {era_style}
                background: transparent;
            """)
            era_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            faction_group_layout.addWidget(era_info)
            
            established_info = QLabel(f"ESTABLISHED: {faction_data['established']}")
            established_style = get_selector_font_style(12, "light")
            established_info.setStyleSheet(f"""
                color: #CCCCCC;
                {established_style}
                background: transparent;
            """)
            established_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            faction_group_layout.addWidget(established_info)
            
            factions_layout.addWidget(faction_group)
        
        layout.addWidget(factions_container, 1)
        
        # Нижня інформація
        footer_info = QLabel("EACH FACTION PROVIDES AN AUTHENTIC INTERFACE EXPERIENCE")
        footer_style = get_selector_font_style(16, "normal")
        footer_info.setStyleSheet(f"""
            color: #666666;
            {footer_style}
            background: transparent;
            padding: 20px;
        """)
        footer_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_info)
        
        # Індикатори стану
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.setSpacing(15)
        
        for i in range(12):
            indicator = QLabel("●")
            indicator.setStyleSheet("color: #333333; font-size: 12px; background: transparent;")
            status_layout.addWidget(indicator)
        
        layout.addWidget(status_container)
    
    def select_faction(self, faction_key, faction_data):
        """Обробити вибір фракції"""
        print(f"🎯 Faction selected: {faction_data['name']} ({faction_data['era'].value})")
        
        # Анімація вибору (простий ефект)
        self.setStyleSheet("QMainWindow { background-color: #001100; }")
        QTimer.singleShot(300, lambda: self.setStyleSheet("QMainWindow { background-color: #0a0a0a; }"))
        
        # Затримка для візуального ефекту
        QTimer.singleShot(800, lambda: self.emit_selection(faction_key, faction_data))
    
    def emit_selection(self, faction_key, faction_data):
        """Емітувати сигнал вибору"""
        print(f"🚀 Proceeding to {faction_data['name']} lock screen")
        self.faction_selected.emit(faction_key, faction_data)


def main():
    """Test faction selector"""
    app = QApplication(sys.argv)
    setup_lcars_font()
    
    selector = LCARSFactionSelector()
    selector.faction_selected.connect(
        lambda fk, fd: print(f"Selected: {fd['name']} - {fd['era'].value}")
    )
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
