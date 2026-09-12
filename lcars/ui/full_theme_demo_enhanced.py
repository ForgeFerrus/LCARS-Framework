"""
LCARS Theme Demo - Покращений 25th Century інтерфейс
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


class LCARSDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_palette = None
        self.current_faction = None
        self.current_era = None
        self.screen_mode = "start"  # start -> faction -> era -> demo
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('LCARS Theme Demo - 25th Century Enhanced')
        # Повноекранний режим без віндовських елементів
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        
        # Покращений стиль LCARS 25th Century з градієнтами та анімацією
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
                font-family: 'Orbitron', 'Arial', sans-serif;
                text-shadow: 0px 0px 10px #66CCFF;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #FFCC66, stop: 1 #CC9933);
                color: #000000;
                font-weight: bold;
                border: 2px solid #FFCC66;
                border-radius: 8px;
                font-family: 'Orbitron', 'Arial', sans-serif;
                font-size: 16px;
                text-shadow: 1px 1px 2px #000000;
                box-shadow: 0px 0px 15px #FFCC66;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #FFFFFF, stop: 1 #CCCCCC);
                color: #000000;
                border-color: #FFFFFF;
                box-shadow: 0px 0px 20px #FFFFFF;
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #CCCCCC, stop: 1 #999999);
                transform: translate(2px, 2px);
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
        """Покращений початковий екран з анімацією"""
        self.clear_screen()
        
        # Анімований заголовок
        title = QLabel("LCARS FRAMEWORK")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 84px;
            font-weight: bold;
            color: #FFFFFF;
            margin: 50px;
            text-shadow: 0px 0px 20px #66CCFF;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba(102, 204, 255, 0.1), 
                stop: 0.5 rgba(102, 204, 255, 0.3),
                stop: 1 rgba(102, 204, 255, 0.1));
            border-radius: 15px;
            padding: 30px;
        """)
        
        subtitle = QLabel("◊ 25TH CENTURY ENHANCED INTERFACE ◊")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 28px;
            color: #FFCC66;
            margin: 20px;
            text-shadow: 0px 0px 15px #FFCC66;
        """)
        
        # Статус лінія
        status = QLabel("STARDATE 2406.015 • SYSTEMS ONLINE • READY FOR DEMONSTRATION")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setStyleSheet("""
            font-size: 16px;
            color: #66FF66;
            margin: 10px;
            text-shadow: 0px 0px 10px #66FF66;
        """)
        
        # Покращені кнопки
        button_layout = QHBoxLayout()
        
        start_btn = QPushButton("▶ INITIATE DEMONSTRATION")
        start_btn.clicked.connect(self.show_faction_menu)
        start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #66FF66, stop: 1 #339933);
                font-size: 24px;
                padding: 25px 50px;
                margin: 20px;
                border-color: #66FF66;
                box-shadow: 0px 0px 25px #66FF66;
            }
            QPushButton:hover {
                box-shadow: 0px 0px 35px #66FF66;
            }
        """)
        
        exit_btn = QPushButton("✕ TERMINATE SESSION")
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #FF6666, stop: 1 #CC3333);
                font-size: 24px;
                padding: 25px 50px;
                margin: 20px;
                border-color: #FF6666;
                box-shadow: 0px 0px 25px #FF6666;
            }
            QPushButton:hover {
                box-shadow: 0px 0px 35px #FF6666;
            }
        """)
        
        button_layout.addWidget(start_btn)
        button_layout.addWidget(exit_btn)
        
        self.main_layout.addWidget(title)
        self.main_layout.addWidget(subtitle)
        self.main_layout.addWidget(status)
        self.main_layout.addStretch()
        self.main_layout.addLayout(button_layout)
        self.main_layout.addStretch()
    
    def show_faction_menu(self):
        """Покращене меню фракцій з іконками"""
        self.clear_screen()
        self.screen_mode = "faction"
        
        title = QLabel("◆ FACTION SELECTION PROTOCOL ◆")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #FFFFFF;
            margin: 30px;
            text-shadow: 0px 0px 20px #66CCFF;
        """)
        
        subtitle = QLabel("Choose your allegiance to access historical archives")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 20px;
            color: #CCCCCC;
            margin: 15px;
        """)
        
        # Фракції з покращеним дизайном
        factions_layout = QVBoxLayout()
        factions = [
            ("⭐ UNITED FEDERATION OF PLANETS", "Federation of United Planets", "starfleet", "#6699FF"),
            ("⚔️ KLINGON EMPIRE", "Honor and Glory", "klingon", "#CC3333"),
            ("🛡️ ROMULAN REPUBLIC", "Intelligence and Strategy", "romulan", "#33CC33"),
            ("🏛️ CARDASSIAN UNION", "Order and Discipline", "cardassian", "#CC9933")
        ]
        
        for faction_name, description, faction_key, color in factions:
            faction_btn = QPushButton(f"{faction_name}\n{description}")
            faction_btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 20px;
                    padding: 30px;
                    margin: 15px;
                    text-align: left;
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 {color}, stop: 1 rgba(0,0,0,0.7));
                    border-color: {color};
                    box-shadow: 0px 0px 15px {color};
                    min-height: 60px;
                }}
                QPushButton:hover {{
                    box-shadow: 0px 0px 25px {color};
                    transform: scale(1.02);
                }}
            """)
            faction_btn.clicked.connect(lambda checked, f=faction_key: self.select_faction(f))
            factions_layout.addWidget(faction_btn)
        
        # Кнопка назад
        back_btn = QPushButton("◀ RETURN TO START")
        back_btn.clicked.connect(self.show_start_screen)
        back_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #666666, stop: 1 #333333);
                font-size: 18px;
                padding: 15px;
                border-color: #666666;
                box-shadow: 0px 0px 10px #666666;
            }
        """)
        
        self.main_layout.addWidget(title)
        self.main_layout.addWidget(subtitle)
        self.main_layout.addLayout(factions_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(back_btn)
    
    def select_faction(self, faction):
        """Вибір фракції з анімацією"""
        self.current_faction = faction
        print(f"✓ Selected faction: {faction.upper()}")
        self.show_era_menu()
    
    def show_era_menu(self):
        """Покращене меню ер з детальною інформацією"""
        self.clear_screen()
        self.screen_mode = "era"
        
        faction_names = {
            'starfleet': 'UNITED FEDERATION OF PLANETS',
            'klingon': 'KLINGON EMPIRE', 
            'romulan': 'ROMULAN REPUBLIC',
            'cardassian': 'CARDASSIAN UNION'
        }
        
        title = QLabel(f"◆ {faction_names.get(self.current_faction, 'UNKNOWN')} ◆")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 42px;
            font-weight: bold;
            color: #FFFFFF;
            margin: 30px;
            text-shadow: 0px 0px 20px #66CCFF;
        """)
        
        subtitle = QLabel("◊ HISTORICAL PERIOD SELECTION ◊")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 24px;
            color: #FFCC66;
            margin: 20px;
            text-shadow: 0px 0px 15px #FFCC66;
        """)
        
        # Ери з детальною інформацією
        eras_layout = QVBoxLayout()
        
        if self.current_faction == 'starfleet':
            eras = [
                ("22nd Century", "Enterprise NX-01 Era • Pre-Federation", LCARSEra.COMS_22ND, "#FF9966"),
                ("23rd Century", "Original Series Era • Kirk's Enterprise", LCARSEra.PCARS_23RD, "#FFCC66"),
                ("24th Century", "Next Generation Era • Picard's Enterprise", LCARSEra.LCARS_24TH, "#66CCFF"),
                ("25th Century", "Modern Era • Advanced Technology", LCARSEra.LCARS_25TH, "#99FF99")
            ]
        else:
            era_map = {
                'klingon': [
                    ("22nd Century", "Early Empire • Honor Code Formation", FactionEra.KLINGON_22ND, "#CC6666"),
                    ("23rd Century", "Classical Period • Warrior Tradition", FactionEra.KLINGON_23RD, "#CC3333"),
                    ("24th Century", "Federation Alliance • Modern Empire", FactionEra.KLINGON_24TH, "#FF6666"),
                    ("25th Century", "Contemporary Era • Galactic Power", FactionEra.KLINGON_25TH, "#FF9999")
                ],
                'romulan': [
                    ("22nd Century", "Isolationist Period • Earth-Romulan War", FactionEra.ROMULAN_22ND, "#66CC66"),
                    ("23rd Century", "Cold War Era • Neutral Zone", FactionEra.ROMULAN_23RD, "#33CC33"),
                    ("24th Century", "Imperial Era • Star Empire", FactionEra.ROMULAN_24TH, "#99FF66"),
                    ("25th Century", "Republic Era • New Government", FactionEra.ROMULAN_25TH, "#CCFF99")
                ],
                'cardassian': [
                    ("22nd Century", "Pre-Union • Tribal Period", FactionEra.CARDASSIAN_22ND, "#CC9966"),
                    ("23rd Century", "Early Union • Expansion", FactionEra.CARDASSIAN_23RD, "#CC9933"),
                    ("24th Century", "Military State • Dominion War", FactionEra.CARDASSIAN_24TH, "#FFCC33"),
                    ("25th Century", "Democratic Union • Reconstruction", FactionEra.CARDASSIAN_25TH, "#FFDD66")
                ]
            }
            eras = era_map.get(self.current_faction, [])
        
        for era_name, description, era_enum, color in eras:
            era_btn = QPushButton(f"⚡ {era_name}\n{description}")
            era_btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 18px;
                    padding: 25px;
                    margin: 12px;
                    text-align: left;
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 {color}, stop: 1 rgba(0,0,0,0.8));
                    border-color: {color};
                    box-shadow: 0px 0px 15px {color};
                    min-height: 50px;
                }}
                QPushButton:hover {{
                    box-shadow: 0px 0px 25px {color};
                    transform: scale(1.02);
                }}
            """)
            era_btn.clicked.connect(lambda checked, e=era_enum: self.select_era(e))
            eras_layout.addWidget(era_btn)
        
        # Кнопка назад
        back_btn = QPushButton("◀ BACK TO FACTIONS")
        back_btn.clicked.connect(self.show_faction_menu)
        back_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #666666, stop: 1 #333333);
                font-size: 18px;
                padding: 15px;
                border-color: #666666;
                box-shadow: 0px 0px 10px #666666;
            }
        """)
        
        self.main_layout.addWidget(title)
        self.main_layout.addWidget(subtitle)
        self.main_layout.addLayout(eras_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(back_btn)
    
    def select_era(self, era):
        """Вибір ери з завантаженням палітри"""
        self.current_era = era
        print(f"✓ Selected era: {era.name}")
        self.show_palette_demo()
    
    def show_palette_demo(self):
        """Покращена демонстрація палітри з детальним аналізом"""
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
        
        # Анімований заголовок з інформацією
        title = QLabel(f"◆ {self.current_faction.upper()} - {self.current_era.name} ◆")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        primary_color = self.current_palette.get('button_colors', ['#FFFFFF'])[0]
        title.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            color: {primary_color};
            margin: 25px;
            text-shadow: 0px 0px 20px {primary_color};
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 rgba({hex(int(primary_color[1:3], 16))[2:]}, {hex(int(primary_color[3:5], 16))[2:]}, {hex(int(primary_color[5:7], 16))[2:]}, 0.2),
                stop: 0.5 rgba({hex(int(primary_color[1:3], 16))[2:]}, {hex(int(primary_color[3:5], 16))[2:]}, {hex(int(primary_color[5:7], 16))[2:]}, 0.4),
                stop: 1 rgba({hex(int(primary_color[1:3], 16))[2:]}, {hex(int(primary_color[3:5], 16))[2:]}, {hex(int(primary_color[5:7], 16))[2:]}, 0.2));
            border-radius: 12px;
            padding: 20px;
        """)
        
        # Детальна інформація про палітру
        info_text = f"""
◊ FACTION: {self.current_faction.upper()}
◊ ERA: {self.current_era.name} 
◊ PALETTE VARIANTS: {len(self.current_palette.get('button_colors', []))} colors
◊ PRIMARY BACKGROUND: {self.current_palette.get('background', '#000000')}
◊ TEXT COLOR: {self.current_palette.get('text', '#FFFFFF')}
◊ INTERFACE STATUS: FULLY OPERATIONAL
        """
        
        info_label = QLabel(info_text.strip())
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet(f"""
            font-size: 16px;
            padding: 25px;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(17, 17, 17, 0.9), stop: 1 rgba(34, 34, 34, 0.9));
            border: 2px solid {primary_color};
            border-radius: 10px;
            margin: 15px;
            text-shadow: 0px 0px 8px {primary_color};
        """)
        
        # Інтерактивні кольорові квадратики
        colors_layout = QGridLayout()
        colors = self.current_palette.get('button_colors', [])
        
        for i, color in enumerate(colors[:16]):  # Максимум 16 кольорів
            color_btn = QPushButton(f"COLOR {i+1:02d}\n{color}")
            color_btn.setFixedSize(140, 100)
            color_btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {color}, stop: 1 rgba(0,0,0,0.3));
                    color: #000000;
                    font-size: 12px;
                    font-weight: bold;
                    border: 3px solid {color};
                    border-radius: 12px;
                    margin: 8px;
                    text-shadow: 1px 1px 3px #FFFFFF;
                    box-shadow: 0px 0px 15px {color};
                }}
                QPushButton:hover {{
                    box-shadow: 0px 0px 25px {color};
                    transform: scale(1.1);
                }}
            """)
            colors_layout.addWidget(color_btn, i // 4, i % 4)
        
        # Покращені кнопки навігації
        controls_layout = QHBoxLayout()
        
        control_buttons = [
            ("◀ BACK TO ERAS", self.show_era_menu, "#666666"),
            ("🔄 NEW FACTION", self.show_faction_menu, "#9966CC"),
            ("🏠 START MENU", self.show_start_screen, "#66CC99")
        ]
        
        for text, callback, color in control_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {color}, stop: 1 rgba(0,0,0,0.7));
                    font-size: 16px;
                    padding: 18px;
                    margin: 8px;
                    border-color: {color};
                    box-shadow: 0px 0px 12px {color};
                }}
                QPushButton:hover {{
                    box-shadow: 0px 0px 20px {color};
                }}
            """)
            controls_layout.addWidget(btn)
        
        self.main_layout.addWidget(title)
        self.main_layout.addWidget(info_label)
        self.main_layout.addLayout(colors_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(controls_layout)
        
        # Застосовуємо покращену тему
        self.apply_enhanced_theme()
    
    def apply_enhanced_theme(self):
        """Застосування покращеної теми з градієнтами"""
        if not self.current_palette:
            return
        
        primary_color = self.current_palette.get('button_colors', ['#FFCC66'])[0]
        background = self.current_palette.get('background', '#000000')
        text_color = self.current_palette.get('text', '#FFFFFF')
        
        # Покращений стиль з анімацією та ефектами
        enhanced_style = f"""
            QMainWindow {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {background}, 
                    stop: 0.3 rgba({int(primary_color[1:3], 16)}, {int(primary_color[3:5], 16)}, {int(primary_color[5:7], 16)}, 0.1),
                    stop: 0.7 rgba({int(primary_color[1:3], 16)}, {int(primary_color[3:5], 16)}, {int(primary_color[5:7], 16)}, 0.1),
                    stop: 1 {background});
                color: {text_color};
            }}
            QWidget {{
                background-color: transparent;
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
                font-family: 'Orbitron', 'Arial', sans-serif;
                text-shadow: 0px 0px 12px {primary_color};
            }}
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {primary_color}, stop: 1 rgba(0,0,0,0.8));
                color: #000000;
                font-weight: bold;
                border: 3px solid {primary_color};
                border-radius: 12px;
                font-family: 'Orbitron', 'Arial', sans-serif;
                text-shadow: 1px 1px 3px #FFFFFF;
                box-shadow: 0px 0px 18px {primary_color};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #FFFFFF, stop: 1 rgba(204, 204, 204, 0.9));
                border-color: #FFFFFF;
                box-shadow: 0px 0px 25px #FFFFFF;
                transform: scale(1.05);
            }}
        """
        
        self.setStyleSheet(enhanced_style)
    
    def clear_screen(self):
        """Очищення екрану з анімацією"""
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
    app.setApplicationName('LCARS Theme Demo - Enhanced')
    
    demo = LCARSDemo()
    demo.show()
    
    print('🚀 Enhanced LCARS Theme Demo Started')
    print('✨ Features: Gradients, Shadows, Animations, Enhanced UI')
    print('📋 Workflow: Start → Faction → Era → Enhanced Palette Demo')
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
