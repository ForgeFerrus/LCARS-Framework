"""
LCARS Theme Demo - Простий 25th Century інтерфейс
Вибір фракції і демонстрація всіх епох на одному екрані
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                           QVBoxLayout, QHBoxLayout, QGridLayout,
                           QLabel, QPushButton, QScrollArea)
from PyQt6.QtCore import Qt

# Додаємо шлях до проєкту
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lcars.themes.lcars_palette import LCARSEra, get_era_palette
from lcars.themes.theme import FactionEra, get_faction_palette


class LCARSDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_faction = "starfleet"
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('LCARS 25th Century Palette Demo')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        
        # Стиль 25 століття
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #000000, stop: 0.5 #001122, stop: 1 #000000);
                color: #FFFFFF;
            }
            QWidget {
                background-color: transparent;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
                font-weight: bold;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #FFCC66, stop: 1 #CC9933);
                color: #000000;
                font-weight: bold;
                border: 2px solid #FFCC66;
                border-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                padding: 8px 16px;
                margin: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #FFFFFF, stop: 1 #CCCCCC);
                border-color: #FFFFFF;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("◆ LCARS 25TH CENTURY PALETTE DEMONSTRATION ◆")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 36px;
            color: #66CCFF;
            margin: 20px;
            border: 3px solid #66CCFF;
            border-radius: 15px;
            padding: 20px;
            background: rgba(102, 204, 255, 0.1);
        """)
        main_layout.addWidget(title)
        
        # Кнопки вибору фракції
        faction_layout = QHBoxLayout()
        factions = [
            ("STARFLEET", "starfleet", "#6699FF"),
            ("KLINGON", "klingon", "#CC3333"), 
            ("ROMULAN", "romulan", "#33CC33"),
            ("CARDASSIAN", "cardassian", "#CC9933")
        ]
        
        for name, key, color in factions:
            btn = QPushButton(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {color}, stop: 1 rgba(0,0,0,0.7));
                    font-size: 18px;
                    padding: 15px 30px;
                    border: 3px solid {color};
                    border-radius: 10px;
                    min-height: 40px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #FFFFFF, stop: 1 {color});
                }}
            """)
            btn.clicked.connect(lambda checked, f=key: self.select_faction(f))
            faction_layout.addWidget(btn)
        
        main_layout.addLayout(faction_layout)
        
        # Кнопка виходу
        exit_btn = QPushButton("✕ EXIT")
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #FF6666, stop: 1 #CC3333);
                font-size: 16px;
                padding: 10px 20px;
                border: 2px solid #FF6666;
                border-radius: 8px;
                max-width: 100px;
            }
        """)
        exit_layout = QHBoxLayout()
        exit_layout.addStretch()
        exit_layout.addWidget(exit_btn)
        main_layout.addLayout(exit_layout)
        
        # Scroll area для палітр
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.palettes_layout = QVBoxLayout(scroll_widget)
        self.palettes_layout.setSpacing(15)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        # Показуємо палітри за замовчуванням
        self.show_palettes()
    
    def select_faction(self, faction):
        """Вибір фракції та показ її палітр"""
        self.current_faction = faction
        print(f"Selected faction: {faction}")
        self.show_palettes()
    
    def show_palettes(self):
        """Показ всіх палітр вибраної фракції"""
        # Очищуємо попередні палітри
        while self.palettes_layout.count():
            child = self.palettes_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        faction_names = {
            'starfleet': 'UNITED FEDERATION OF PLANETS',
            'klingon': 'KLINGON EMPIRE',
            'romulan': 'ROMULAN REPUBLIC', 
            'cardassian': 'CARDASSIAN UNION'
        }
        
        # Заголовок фракції
        faction_title = QLabel(f"◊ {faction_names.get(self.current_faction, 'UNKNOWN')} ERAS ◊")
        faction_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        faction_title.setStyleSheet("""
            font-size: 28px;
            color: #FFCC66;
            margin: 15px;
            font-weight: bold;
        """)
        self.palettes_layout.addWidget(faction_title)
        
        # Отримуємо ери для фракції
        if self.current_faction == 'starfleet':
            eras = [
                ("22nd Century - Enterprise NX-01 Era", LCARSEra.COMS_22ND),
                ("23rd Century - Original Series Era", LCARSEra.PCARS_23RD), 
                ("24th Century - Next Generation Era", LCARSEra.LCARS_24TH),
                ("25th Century - Modern Era", LCARSEra.LCARS_25TH)
            ]
        else:
            era_map = {
                'klingon': [
                    ("22nd Century - Early Empire", FactionEra.KLINGON_22ND),
                    ("23rd Century - Classical Period", FactionEra.KLINGON_23RD),
                    ("24th Century - Federation Alliance", FactionEra.KLINGON_24TH),
                    ("25th Century - Modern Empire", FactionEra.KLINGON_25TH)
                ],
                'romulan': [
                    ("22nd Century - Isolationist Period", FactionEra.ROMULAN_22ND),
                    ("23rd Century - Cold War Era", FactionEra.ROMULAN_23RD),
                    ("24th Century - Imperial Era", FactionEra.ROMULAN_24TH),
                    ("25th Century - Republic Era", FactionEra.ROMULAN_25TH)
                ],
                'cardassian': [
                    ("22nd Century - Pre-Union", FactionEra.CARDASSIAN_22ND),
                    ("23rd Century - Early Union", FactionEra.CARDASSIAN_23RD),
                    ("24th Century - Military State", FactionEra.CARDASSIAN_24TH),
                    ("25th Century - Democratic Union", FactionEra.CARDASSIAN_25TH)
                ]
            }
            eras = era_map.get(self.current_faction, [])
        
        # Показуємо кожну еру з її палітрою
        for era_name, era_enum in eras:
            self.create_era_section(era_name, era_enum)
    
    def create_era_section(self, era_name, era_enum):
        """Створення секції для ери з її палітрою"""
        # Отримуємо палітру
        if True:
            if self.current_faction == 'starfleet':
                palette = get_era_palette(era_enum)
            else:
                palette = get_faction_palette(era_enum)
        if False: # Removed except block
            print(f"Error loading palette for {era_name}: {e}")
            palette = get_era_palette(LCARSEra.LCARS_25TH)
        
        primary_color = palette.get('button_colors', ['#FFCC66'])[0]
        
        # Заголовок ери
        era_label = QLabel(f"⚡ {era_name}")
        era_label.setStyleSheet(f"""
            font-size: 20px;
            color: {primary_color};
            margin: 10px 0px;
            font-weight: bold;
            border: 2px solid {primary_color};
            border-radius: 8px;
            padding: 10px;
            background: rgba({int(primary_color[1:3], 16)}, {int(primary_color[3:5], 16)}, {int(primary_color[5:7], 16)}, 0.1);
        """)
        self.palettes_layout.addWidget(era_label)
        
        # Інформація про палітру
        info_text = f"Colors: {len(palette.get('button_colors', []))} • Background: {palette.get('background', '#000000')} • Text: {palette.get('text', '#FFFFFF')}"
        info_label = QLabel(info_text)
        info_label.setStyleSheet(f"""
            font-size: 14px;
            color: {primary_color};
            margin: 5px 20px;
        """)
        self.palettes_layout.addWidget(info_label)
        
        # Кольорові квадратики
        colors_widget = QWidget()
        colors_layout = QGridLayout(colors_widget)
        colors_layout.setSpacing(8)
        
        colors = palette.get('button_colors', [])
        for i, color in enumerate(colors[:12]):  # Максимум 12 кольорів на еру
            color_btn = QPushButton(color)
            color_btn.setFixedSize(120, 60)
            color_btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {color}, stop: 1 rgba(0,0,0,0.3));
                    color: #000000;
                    font-size: 10px;
                    font-weight: bold;
                    border: 2px solid {color};
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #FFFFFF, stop: 1 {color});
                }}
            """)
            colors_layout.addWidget(color_btn, i // 6, i % 6)
        
        self.palettes_layout.addWidget(colors_widget)
        
        # Розділювач
        separator = QLabel("─" * 80)
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator.setStyleSheet("color: #333333; margin: 10px;")
        self.palettes_layout.addWidget(separator)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('LCARS 25th Century Demo')
    
    demo = LCARSDemo()
    demo.show()
    
    print('🚀 LCARS 25th Century Palette Demo')
    print('📋 Simple interface: Select faction → View all era palettes')
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
