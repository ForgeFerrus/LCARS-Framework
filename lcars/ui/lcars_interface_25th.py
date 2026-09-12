"""
LCARS 25th Century Interface - Чистий послідовний інтерфейс
Стартове меню → Вибір фракції → Вибір ери → Демонстрація палітри
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                           QVBoxLayout, QHBoxLayout, QGridLayout,
                           QLabel, QPushButton)
from PyQt6.QtCore import Qt

# Додаємо шлях до проєкту
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lcars.themes.lcars_palette import LCARSEra, get_era_palette
from lcars.themes.theme import FactionEra, get_faction_palette


class LCARS25thInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_palette = None
        self.current_faction = None
        self.current_era = None
        self.screen_mode = "start"  # start -> faction -> era -> demo
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('LCARS 25th Century Interface')
        # Повноекранний режим без віндовських елементів
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        
        # Базовий стиль LCARS 25th Century
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
                color: #FFFFFF;
            }
            QWidget {
                background-color: #000000;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Arial', sans-serif;
            }
            QPushButton {
                background-color: #FFCC66;
                color: #000000;
                font-weight: bold;
                border: none;
                border-radius: 0px;
                font-family: 'Arial', sans-serif;
            }
            QPushButton:hover {
                background-color: #FFFFFF;
                color: #000000;
            }
        """)
        
        # Основний контейнер
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(50, 50, 50, 50)
        self.main_layout.setSpacing(30)
        
        # Показуємо стартовий екран
        self.show_start_screen()
    
    def show_start_screen(self):
        """Початковий екран LCARS 25th Century"""
        self.clear_screen()
        
        # Заголовок
        title = QLabel("LCARS FRAMEWORK")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 72px;
            font-weight: bold;
            color: #FFFFFF;
            margin: 50px;
        """)
        
        subtitle = QLabel("25th CENTURY INTERFACE")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 36px;
            color: #FFCC66;
            margin: 20px;
        """)
        
        # Кнопки управління
        button_layout = QHBoxLayout()
        
        start_btn = QPushButton("START DEMONSTRATION")
        start_btn.clicked.connect(self.show_faction_menu)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFCC66;
                font-size: 24px;
                padding: 30px 60px;
                margin: 20px;
            }
        """)
        
        exit_btn = QPushButton("EXIT")
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6666;
                font-size: 24px;
                padding: 30px 60px;
                margin: 20px;
            }
        """)
        
        button_layout.addWidget(start_btn)
        button_layout.addWidget(exit_btn)
        
        self.main_layout.addWidget(title)
        self.main_layout.addWidget(subtitle)
        self.main_layout.addStretch()
        self.main_layout.addLayout(button_layout)
        self.main_layout.addStretch()
    
    def show_faction_menu(self):
        """Меню вибору фракцій"""
        self.clear_screen()
        self.screen_mode = "faction"
        
        title = QLabel("SELECT FACTION")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #FFFFFF;
            margin: 30px;
        """)
        
        # Фракції
        factions_layout = QVBoxLayout()
        factions = [
            ("STARFLEET", "Federation of United Planets"),
            ("KLINGON EMPIRE", "Honor and Glory"),
            ("ROMULAN REPUBLIC", "Intelligence and Strategy"),
            ("CARDASSIAN UNION", "Order and Discipline")
        ]
        
        for faction_name, description in factions:
            faction_btn = QPushButton(f"{faction_name}\n{description}")
            faction_btn.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    padding: 25px;
                    margin: 10px;
                    text-align: left;
                }
            """)
            faction_key = faction_name.split()[0].lower()
            faction_btn.clicked.connect(lambda checked, f=faction_key: self.select_faction(f))
            factions_layout.addWidget(faction_btn)
        
        # Кнопка назад
        back_btn = QPushButton("BACK TO START")
        back_btn.clicked.connect(self.show_start_screen)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                font-size: 18px;
                padding: 15px;
            }
        """)
        
        self.main_layout.addWidget(title)
        self.main_layout.addLayout(factions_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(back_btn)
    
    def select_faction(self, faction):
        """Вибір фракції та перехід до вибору ери"""
        self.current_faction = faction
        print(f"Selected faction: {faction}")
        self.show_era_menu()
    
    def show_era_menu(self):
        """Меню вибору ери для вибраної фракції"""
        self.clear_screen()
        self.screen_mode = "era"
        
        title = QLabel(f"{self.current_faction.upper()} ERAS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #FFFFFF;
            margin: 30px;
        """)
        
        subtitle = QLabel("Select Historical Period")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 24px;
            color: #FFCC66;
            margin: 20px;
        """)
        
        # Ери залежно від фракції
        eras_layout = QVBoxLayout()
        
        if self.current_faction == 'starfleet':
            eras = [
                ("22nd Century", "Enterprise NX-01 Era", LCARSEra.COMS_22ND),
                ("23rd Century", "Original Series Era", LCARSEra.PCARS_23RD),
                ("24th Century", "Next Generation Era", LCARSEra.LCARS_24TH),
                ("25th Century", "Modern Era", LCARSEra.LCARS_25TH)
            ]
        else:
            era_map = {
                'klingon': [
                    ("22nd Century", "Early Empire", FactionEra.KLINGON_22ND),
                    ("23rd Century", "Classical Period", FactionEra.KLINGON_23RD),
                    ("24th Century", "Federation Alliance", FactionEra.KLINGON_24TH),
                    ("25th Century", "Modern Empire", FactionEra.KLINGON_25TH)
                ],
                'romulan': [
                    ("22nd Century", "Isolationist Period", FactionEra.ROMULAN_22ND),
                    ("23rd Century", "Cold War Era", FactionEra.ROMULAN_23RD),
                    ("24th Century", "Imperial Era", FactionEra.ROMULAN_24TH),
                    ("25th Century", "Republic Era", FactionEra.ROMULAN_25TH)
                ],
                'cardassian': [
                    ("22nd Century", "Pre-Union", FactionEra.CARDASSIAN_22ND),
                    ("23rd Century", "Early Union", FactionEra.CARDASSIAN_23RD),
                    ("24th Century", "Military State", FactionEra.CARDASSIAN_24TH),
                    ("25th Century", "Democratic Union", FactionEra.CARDASSIAN_25TH)
                ]
            }
            eras = era_map.get(self.current_faction, [])
        
        for era_name, description, era_enum in eras:
            era_btn = QPushButton(f"{era_name}\n{description}")
            era_btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    padding: 20px;
                    margin: 8px;
                    text-align: left;
                }
            """)
            era_btn.clicked.connect(lambda checked, e=era_enum: self.select_era(e))
            eras_layout.addWidget(era_btn)
        
        # Кнопка назад
        back_btn = QPushButton("BACK TO FACTIONS")
        back_btn.clicked.connect(self.show_faction_menu)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                font-size: 18px;
                padding: 15px;
            }
        """)
        
        self.main_layout.addWidget(title)
        self.main_layout.addWidget(subtitle)
        self.main_layout.addLayout(eras_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(back_btn)
    
    def select_era(self, era):
        """Вибір ери та показ демонстрації палітри"""
        self.current_era = era
        print(f"Selected era: {era}")
        self.show_palette_demo()
    
    def show_palette_demo(self):
        """Демонстрація палітри для вибраної фракції та ери"""
        self.clear_screen()
        self.screen_mode = "demo"
        
        # Завантаження палітри
        if True:
            if self.current_faction == 'starfleet':
                self.current_palette = get_era_palette(self.current_era)
            else:
                self.current_palette = get_faction_palette(self.current_era)
        if False: # Removed except block
            print(f"Error loading palette: {e}")
            self.current_palette = get_era_palette(LCARSEra.LCARS_25TH)
        
        # Заголовок
        title = QLabel(f"{self.current_faction.upper()} - {self.current_era.name}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 42px;
            font-weight: bold;
            color: {self.current_palette.get('button_colors', ['#FFFFFF'])[0]};
            margin: 30px;
        """)
        
        # Інформація про палітру
        info_text = f"""
FACTION: {self.current_faction.upper()}
ERA: {self.current_era.name}
COLORS: {len(self.current_palette.get('button_colors', []))} variations
BACKGROUND: {self.current_palette.get('background', '#000000')}
TEXT: {self.current_palette.get('text', '#FFFFFF')}
        """
        
        info_label = QLabel(info_text)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            font-size: 18px;
            padding: 20px;
            background-color: #111111;
        """)
        
        # Кольорові квадратики
        colors_layout = QGridLayout()
        colors = self.current_palette.get('button_colors', [])
        
        for i, color in enumerate(colors[:12]):  # Максимум 12 кольорів
            color_btn = QPushButton(color)
            color_btn.setFixedSize(120, 80)
            color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: #000000;
                    font-size: 14px;
                    font-weight: bold;
                }}
            """)
            colors_layout.addWidget(color_btn, i // 4, i % 4)
        
        # Кнопки управління
        controls_layout = QHBoxLayout()
        
        back_btn = QPushButton("BACK TO ERAS")
        back_btn.clicked.connect(self.show_era_menu)
        
        new_faction_btn = QPushButton("NEW FACTION")
        new_faction_btn.clicked.connect(self.show_faction_menu)
        
        start_btn = QPushButton("START MENU")
        start_btn.clicked.connect(self.show_start_screen)
        
        for btn in [back_btn, new_faction_btn, start_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    font-size: 16px;
                    padding: 15px;
                    margin: 5px;
                }
            """)
            controls_layout.addWidget(btn)
        
        self.main_layout.addWidget(title)
        self.main_layout.addWidget(info_label)
        self.main_layout.addLayout(colors_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(controls_layout)
        
        # Застосовуємо кольорову тему
        self.apply_palette_theme()
    
    def apply_palette_theme(self):
        """Застосування теми з поточної палітри"""
        if not self.current_palette:
            return
        
        primary_color = self.current_palette.get('button_colors', ['#FFCC66'])[0]
        background = self.current_palette.get('background', '#000000')
        text_color = self.current_palette.get('text', '#FFFFFF')
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {background};
                color: {text_color};
            }}
            QWidget {{
                background-color: {background};
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
                font-family: 'Arial', sans-serif;
            }}
            QPushButton {{
                background-color: {primary_color};
                color: #000000;
                font-weight: bold;
                border: none;
                border-radius: 0px;
                font-family: 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: #FFFFFF;
                color: #000000;
            }}
        """)
    
    def clear_screen(self):
        """Очищення екрану"""
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    subchild = child.layout().takeAt(0)
                    if subchild.widget():
                        subchild.widget().deleteLater()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('LCARS 25th Century Interface')
    
    interface = LCARS25thInterface()
    interface.show()
    
    print('🚀 LCARS 25th Century Interface Started')
    print('📋 Sequential workflow: Start → Faction → Era → Palette Demo')
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
