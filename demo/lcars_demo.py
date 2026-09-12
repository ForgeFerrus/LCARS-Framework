"""
Автентична LCARS-система — демонстрація в стилі Star Trek

Файл містить прості допоміжні віджети й компоненти для демонстрації
палет проекту. Коментарі й docstring'и тут виконані українською для
зручності розробника.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
# Ensure repository root is on sys.path so the `lcars` package can be imported
repo_root = project_root.parent
sys.path.insert(0, str(repo_root))

from PyQt6.QtWidgets import (QApplication, QDialog, QMainWindow, QWidget, 
                            QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                            QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

# Import shared authentic palette constants when present
from lcars.themes.theme import FactionEra, get_faction_palette
from lcars.themes.lcars_palette import LCARSEra, get_theme, get_lcars_font_style, setup_lcars_font, get_random_button_color

# Register LCARS fonts (best-effort)
try:
    setup_lcars_font()
except (ImportError, OSError, FileNotFoundError):
    # Fonts are optional for the demo; ignore common filesystem/import errors
    pass

# Build a small LCARS_COLORS mapping from the default 25th-era theme so
# UI code that references LCARS_COLORS continues to work but colours
# originate from the project's palette algorithms (not hardcoded values).
try:
    _default_theme = get_theme(LCARSEra.LCARS_25TH)
    _p = _default_theme.get('palette', ['#4BBEBF'])
    LCARS_COLORS = {
        'primary_orange': _p[4] if len(_p) > 4 else _p[0],
        'primary_cyan': _p[0],
        'primary_blue': _p[1] if len(_p) > 1 else _p[0],
        'secondary_cyan': _p[2] if len(_p) > 2 else _p[0],
        'secondary_orange': _p[3] if len(_p) > 3 else _p[0],
        'secondary_blue': _p[1] if len(_p) > 1 else _p[0],
        'alert_red': _default_theme.get('alerts', ['#D80000'])[0],
        'alert_yellow': _default_theme.get('alerts', ['#FFBB00'])[1] if len(_default_theme.get('alerts', [])) > 1 else _default_theme.get('alerts', ['#FFBB00'])[0],
        'text_black': _default_theme.get('text', '#000000'),
        'text_white': _default_theme.get('text', '#FFFFFF'),
        'background_black': _default_theme.get('bg', '#000000'),
        'panel_gray': _p[0]
    }
except (AttributeError, TypeError, KeyError, IndexError, ImportError, RuntimeError):
    LCARS_COLORS = {
        "primary_orange": "#FF9900",
        "primary_cyan": "#00CC99",
        "primary_blue": "#3366CC",
        "secondary_cyan": "#99FFFF",
        "secondary_orange": "#FFCC33",
        "secondary_blue": "#4BBEBF",
        "alert_red": "#FF3333",
        "alert_yellow": "#FFFF00",
        "text_black": "#000000",
        "text_white": "#FFFFFF",
        "background_black": "#000000",
        "panel_gray": "#333333"
    }

# Пояснення: LCARS_COLORS — це локальний словник-резерв, який використовують
# допоміжні класи демонстрації нижче. Ми намагаємося наповнити його з теми;
# якщо тема недоступна — використовуємо дефолтні значення, щоб demo працював.

# Simple mapping from era display strings used in the demo to the LCARSEra enum
ERA_NAME_TO_ENUM = {
    "22nd": LCARSEra.COMS_22ND,
    "23rd": LCARSEra.PCARS_23RD,
    "23st": LCARSEra.PCARS_23ST,
    "24th": LCARSEra.LCARS_24TH,
    "24st": LCARSEra.LCARS_24ST,
    "25th": LCARSEra.LCARS_25TH,
    "29th": LCARSEra.TCARS_29TH,
}

class LCARSElbow(QFrame):
    """Кутовий елемент LCARS (elbow).

    Використовується для декоративних кутів інтерфейсу; радіуси бордерів
    підбираються залежно від орієнтації (tl/tr/bl/br).
    """
    def __init__(self, orientation="tl", color=None, size=(180, 70)):
        super().__init__()
        self.setFixedSize(size[0], size[1])
        
        if color is None:
            color = get_theme(LCARSEra.LCARS_25TH).get("primary_orange", "#FF9900")
        
        border_radius = ""
        if orientation == "tl":  # top-left
            border_radius = "border-top-left-radius: 50px; border-bottom-left-radius: 4px;"
        elif orientation == "tr":  # top-right  
            border_radius = "border-top-right-radius: 35px; border-bottom-right-radius: 4px;"
        elif orientation == "bl":  # bottom-left
            border_radius = "border-bottom-left-radius: 40px; border-top-left-radius: 6px;"
        elif orientation == "br":  # bottom-right
            border_radius = "border-bottom-right-radius: 40px; border-top-right-radius: 6px;"
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                {border_radius}
            }}
        """)

class LCARSButton(QPushButton):
    """Кнопка LCARS з типовим стилем (задається колір і текст).

    Віджету можна передати розмір і колір; стилі вписані в CSS через
    `setStyleSheet` для простоти демонстрації.
    """
    def __init__(self, text, color=LCARS_COLORS["primary_cyan"], size=(200, 50), text_color="#000000"):
        super().__init__(text)
        self.setFixedSize(size[0], size[1])
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: none;
                font-size: 16px;
                font-weight: bold;
                text-transform: uppercase;
                border-radius: 4px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: #FFFFFF;
                color: {color};
            }}
            QPushButton:pressed {{
                background-color: #666666;
                color: #FFFFFF;
            }}
        """)

class LCARSPanel(QFrame):
    """Панель LCARS з округленими кутами.

    Використовується як контейнер для заголовків і інформаційних панелей.
    """
    def __init__(self, color=LCARS_COLORS["secondary_blue"], height=70):
        super().__init__()
        self.setFixedHeight(height)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                border-radius: 4px;
            }}
        """)

class LCARSLabel(QLabel):
    """Напис LCARS з типовим шрифтом та стилем (великі літери, жирний)."""
    def __init__(self, text, color=LCARS_COLORS["text_white"], size=16, text_color=None):
        super().__init__(text)
        actual_color = text_color or color
        self.setStyleSheet(f"""
            QLabel {{
                color: {actual_color};
                font-size: {size}px;
                font-weight: bold;
                text-transform: uppercase;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)        

class LCARSDesktop(QMainWindow):
    """Authentic LCARS desktop interface"""
    def __init__(self, faction, era):
        super().__init__()
        self.faction = faction
        self.era = era
        
        self.setWindowTitle(f"LCARS Desktop - {faction} {era}")
        self.setGeometry(50, 50, 1600, 1000)
        self.setStyleSheet(f"background-color: {LCARS_COLORS['background_black']};")
        
        self.setup_ui()
        
    def setup_ui(self):
        # derive era enum for palette lookups
        era_enum = ERA_NAME_TO_ENUM.get(str(self.era).lower(), LCARSEra.LCARS_25TH)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)
        
        # === TOP HEADER ===
        header = QHBoxLayout()
        header.setSpacing(4)
        
        # Left elbow
        elbow_left = LCARSElbow("tl", get_random_button_color(era_enum), (250, 80))
        header.addWidget(elbow_left)
        
        # Title panel
        title_panel = LCARSPanel(get_random_button_color(era_enum), 80)
        title_layout = QHBoxLayout(title_panel)
        title = LCARSLabel(f"USS ENTERPRISE - {self.faction} {self.era} CONFIGURATION", size=32, text_color="#000000")
        title_layout.addWidget(title)
        header.addWidget(title_panel, 1)
        
        # Right cap
        right_cap = LCARSElbow("tr", get_random_button_color(era_enum), (80, 80))
        header.addWidget(right_cap)
        
        main_layout.addLayout(header)
        
        # === MAIN INTERFACE ===
        interface_layout = QHBoxLayout()
        interface_layout.setSpacing(4)
        
        # === LEFT CONTROL PANEL ===
        left_panel = QVBoxLayout()
        left_panel.setSpacing(4)
        
        # Main panel
        main_left = QFrame()
        main_left.setFixedWidth(250)
        main_left.setStyleSheet(f"background-color: {get_random_button_color(era_enum)}; border-bottom-left-radius: 100px; border-top-left-radius: 4px;")
        left_panel.addWidget(main_left, 1)
        
        # Control buttons
        controls = [
            ("DASHBOARD", get_random_button_color(era_enum)),
            ("TACTICAL", get_random_button_color(era_enum, None, 1)),
            ("SCIENCE", get_random_button_color(era_enum)),
            ("ENGINEERING", get_random_button_color(era_enum)),
            ("COMMUNICATIONS", get_random_button_color(era_enum)),
            ("COMPUTER", get_random_button_color(era_enum))
        ]
        
        for control, color in controls:
            btn = LCARSButton(control, color, (250, 60), "#000000")
            left_panel.addWidget(btn)
        
        left_panel.addStretch(1)
        
        # Bottom elbow
        bottom_elbow = LCARSElbow("bl", get_random_button_color(era_enum), (250, 80))
        left_panel.addWidget(bottom_elbow)
        
        interface_layout.addLayout(left_panel)
        
        # === CENTER DISPLAY AREA ===
        center_display = QVBoxLayout()
        center_display.setSpacing(20)
        center_display.setContentsMargins(20, 20, 20, 20)
        
        # Main status panel
        status_panel = LCARSPanel(get_random_button_color(era_enum), 100)
        status_layout = QHBoxLayout(status_panel)
        
        status_title = LCARSLabel("MAIN SYSTEMS STATUS", size=28, text_color="#FFFFFF")
        status_layout.addWidget(status_title)
        
        status_info = LCARSLabel("ALL SYSTEMS OPERATIONAL - GREEN ALERT", size=20, text_color="#FFFFFF")
        status_layout.addWidget(status_info)
        
        center_display.addWidget(status_panel)
        
        # Data display panels
        data_grid = QGridLayout()
        data_grid.setSpacing(15)
        
        data_panels = [
            ("SHIELDS", get_random_button_color(era_enum), "ONLINE - 100%"),
            ("WEAPONS", get_random_button_color(era_enum, None, 1), "STANDBY"),
            ("ENGINES", get_random_button_color(era_enum), "WARP 9.0 AVAILABLE"),
            ("SENSORS", get_random_button_color(era_enum), "LONG RANGE SCAN"),
            ("COMMUNICATIONS", get_random_button_color(era_enum), "SUBSPACE CHANNEL OPEN"),
            ("LIFE SUPPORT", get_random_button_color(era_enum), "OPTIMAL")
        ]
        
        for i, (title, color, status) in enumerate(data_panels):
            panel = QFrame()
            panel.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            panel.setFixedHeight(80)
            panel_layout = QVBoxLayout(panel)
            
            title_label = LCARSLabel(title, size=16, text_color="#000000")
            panel_layout.addWidget(title_label)
            
            status_label = LCARSLabel(status, size=14, text_color="#000000")
            panel_layout.addWidget(status_label)
            
            data_grid.addWidget(panel, i // 2, i % 2)
        
        center_display.addLayout(data_grid)
        center_display.addStretch()
        
        interface_layout.addLayout(center_display, 1)
        main_layout.addLayout(interface_layout)
        
        # === BOTTOM STATUS BAR ===
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(4)
        
        # Left status
        left_status = LCARSElbow("bl", get_random_button_color(era_enum), (300, 50))
        bottom_bar.addWidget(left_status)
        
        # Center status
        center_status = LCARSPanel(get_random_button_color(era_enum), 50)
        center_layout = QHBoxLayout(center_status)
        status_text = LCARSLabel(f"STARDATE: 58432.7 - {self.faction} {self.era} SYSTEM READY", size=18, text_color="#000000")
        center_layout.addWidget(status_text)
        bottom_bar.addWidget(center_status, 1)
        
        # Right status
        right_status = LCARSElbow("br", get_random_button_color(era_enum), (150, 50))
        bottom_bar.addWidget(right_status)
        
        main_layout.addLayout(bottom_bar)

def main():
    # Delegate to the unified demo launcher which implements
    # the full sequential initialization path. This keeps the
    # demo UI centralized and ensures palette/font algorithms
    # are used consistently.
    from demo import demo_launcher
    # Preserve any CLI args (support `--auto` for automatic demo)
    demo_launcher.main()

if __name__ == "__main__":
    main()
