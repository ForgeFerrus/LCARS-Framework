"""
LCARS Theme Demo - Повна версія з усіма фракціями та епохами
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import random
# Titanium Bridge Migration: from datetime import datetime

# Додати шлях до проєкту
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

if True:
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    from lcars.themes.lcars_palette import get_random_button_color, LCARSEra, get_era_palette
    from lcars.themes.theme import FactionEra, get_faction_palette, get_faction_eras
    print('LCARS modules imported successfully')
if False: # Removed except block
    print(f'Cannot import LCARS modules: {e}')
    sys.exit(1)

class LCARSDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_palette = None
        self.current_faction = None
        self.current_era = None
        self.edit_mode = False
        self.button_timers = {}
        self.faction_eras_widgets = {}
        
        self.setup_ui()
        self.update_system_console()
        
    def setup_ui(self):
        self.setWindowTitle('LCARS Theme Demo - Full Version')
        self.showMaximized()
        self.setWindowFlags(Qt.WindowType.Window)
        
        # Встановити чорний фон
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QWidget {
                background-color: #000000;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                color: #000000;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: 2px solid #FF6B6B;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New', monospace;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Основний контент
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        
        # Ліва панель - вибір фракції та епох
        left_panel = QWidget()
        left_panel.setFixedWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        # Заголовок фракцій
        faction_label = QLabel('SELECT FACTION')
        faction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        faction_label.setStyleSheet('''
            QLabel {
                color: #FF6B6B;
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                background-color: rgba(255, 107, 107, 0.1);
                border-radius: 10px;
                border: 2px solid #FF6B6B;
                margin-bottom: 10px;
            }
        ''')
        left_layout.addWidget(faction_label)
        
        # Кнопки фракцій
        factions = [
            ('STARFLEET', 'starfleet', 'Welcome to Starfleet Command'),
            ('KLINGON EMPIRE', 'klingon', 'Honor and glory to the Empire!'),
            ('ROMULAN STAR EMPIRE', 'romulan', 'Tal Shiar welcomes you'),
            ('CARDASSIAN UNION', 'cardassian', 'Order and discipline prevail')
        ]
        
        for name, faction, greeting in factions:
            btn = QPushButton(name)
            btn.setMinimumHeight(50)
            btn.clicked.connect(lambda checked, f=faction, g=greeting: self.select_faction(f, g))
            left_layout.addWidget(btn)
            self.animate_button(btn)
        
        # Кнопки епох - початково приховані
        self.eras_frame = QFrame()
        self.eras_frame.setVisible(False)
        self.eras_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #FF6B6B;
                border-radius: 8px;
                padding: 8px;
                background-color: rgba(255, 107, 107, 0.05);
                margin: 10px 0;
            }
        """)
        self.eras_layout = QVBoxLayout(self.eras_frame)
        self.eras_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.eras_label = QLabel("--- ERAS ---")
        self.eras_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.eras_label.setStyleSheet('''
            QLabel {
                color: #FF6B6B;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
        ''')
        self.eras_layout.addWidget(self.eras_label)
        
        self.era_buttons = []
        left_layout.addWidget(self.eras_frame)
        
        left_layout.addStretch()
        
        # Кнопки управління - вниз
        control_layout = QHBoxLayout()
        
        self.mode_btn = QPushButton('MODE')
        self.mode_btn.setMinimumHeight(40)
        self.mode_btn.clicked.connect(self.toggle_mode)
        control_layout.addWidget(self.mode_btn)
        
        self.back_btn = QPushButton('BACK')
        self.back_btn.setMinimumHeight(40)
        self.back_btn.clicked.connect(self.go_back)
        control_layout.addWidget(self.back_btn)
        
        left_layout.addLayout(control_layout)
        content_layout.addWidget(left_panel)
        
        # Права панель - демонстрація
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Заголовок демо
        welcome_label = QLabel('LCARS THEME DEMO')
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet('''
            QLabel {
                color: #FF6B6B;
                font-size: 32px;
                font-weight: bold;
                padding: 20px;
                background-color: rgba(255, 107, 107, 0.1);
                border-radius: 15px;
                margin: 15px;
                border: 3px solid #FF6B6B;
            }
        ''')
        right_layout.addWidget(welcome_label)
        
        # Інформація про фракцію
        self.faction_welcome = QLabel('Select a faction to begin')
        self.faction_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.faction_welcome.setStyleSheet('''
            QLabel {
                color: #FFFFFF;
                font-size: 20px;
                padding: 15px;
                margin: 10px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: 2px solid #CCCCCC;
            }
        ''')
        right_layout.addWidget(self.faction_welcome)
        
        # Інформація про епоху
        self.era_info = QLabel('')
        self.era_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.era_info.setStyleSheet('''
            QLabel {
                color: #CCCCCC;
                font-size: 16px;
                padding: 10px;
                margin: 5px;
                background-color: rgba(204, 204, 204, 0.1);
                border-radius: 8px;
                border: 1px solid #888888;
            }
        ''')
        right_layout.addWidget(self.era_info)
        
        # Опис палітри
        self.palette_display = QTextEdit()
        self.palette_display.setReadOnly(True)
        self.palette_display.setMaximumHeight(150)
        self.palette_display.setPlainText("LCARS THEME DEMO\n\nSelect a faction to see its color palette\n\nEach faction has unique colors:\n• STARFLEET - Federation colors\n• KLINGON EMPIRE - Warrior colors\n• ROMULAN STAR EMPIRE - Intelligence colors\n• CARDASSIAN UNION - Military colors")
        right_layout.addWidget(self.palette_display)
        
        # Кольорові квадратики
        self.colors_layout = QVBoxLayout()
        self.colors_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addLayout(self.colors_layout)
        
        right_layout.addStretch()
        content_layout.addWidget(right_panel)
        
    def select_faction(self, faction, greeting):
        # Вибрати фракцію та показати її епохи
        self.faction_welcome.setText(greeting)
        self.current_faction = faction
        self.current_era = None
        
        # Отримати список ер для фракції
        eras = get_faction_eras(faction)
        
        if faction == 'starfleet':
            self.eras_label.setText("--- STARFLEET ERAS ---")
            # Starfleet використовує LCARSEra
            starfleet_eras = [
                ("22nd Century", LCARSEra.COMS_22ND, "Enterprise NX-01 era"),
                ("23rd Century", LCARSEra.PCARS_23RD, "Captain Kirk era"),
                ("23rd Alternative", LCARSEra.PCARS_23ST, "Motion Pictures era"),
                ("24th Century", LCARSEra.LCARS_24TH, "TNG/DS9/VOY era"),
                ("24th Sovereign", LCARSEra.LCARS_24ST, "Enterprise-E era"),
                ("25th Century", LCARSEra.LCARS_25TH, "Picard era"),
                ("29th Century", LCARSEra.TCARS_29TH, "Future era")
            ]
            self.update_era_buttons(starfleet_eras, is_starfleet=True)
        else:
            # Інші фракції використовують FactionEra
            faction_names = {
                'klingon': 'KLINGON EMPIRE',
                'romulan': 'ROMULAN STAR EMPIRE', 
                'cardassian': 'CARDASSIAN UNION'
            }
            self.eras_label.setText(f"--- {faction_names.get(faction, faction.upper())} ERAS ---")
            
            # Створити список епох для фракції
            faction_eras = []
            for era in eras:
                # Знайти відповідний FactionEra
                for faction_era in FactionEra:
                    if faction_era.value == f"{faction}_{era}":
                        # Створити читабельну назву
                        era_display = era.upper().replace('ND', 'nd').replace('RD', 'rd').replace('ST', 'st').replace('TH', 'th')
                        faction_eras.append((f"{era_display} Century", faction_era, f"{faction_names.get(faction, faction.upper())} {era_display} era"))
                        break
            
            self.update_era_buttons(faction_eras, is_starfleet=False)
        
        self.eras_frame.setVisible(True)
        print(f'Selected faction: {faction.upper()}, available eras: {len(eras)}')
        
    def update_era_buttons(self, eras, is_starfleet=True):
        # Очистити існуючі кнопки епох
        for btn in self.era_buttons:
            btn.deleteLater()
        self.era_buttons.clear()
        
        # Створити нові кнопки епох
        for display_name, era, description in eras:
            btn = QPushButton(display_name)
            btn.setMinimumHeight(40)
            btn.setToolTip(description)
            
            if is_starfleet:
                btn.clicked.connect(lambda checked, e=era: self.select_starfleet_era(e))
            else:
                btn.clicked.connect(lambda checked, e=era: self.select_faction_era(e))
            
            self.eras_layout.addWidget(btn)
            self.era_buttons.append(btn)
            self.animate_button(btn)
    
    def select_starfleet_era(self, era):
        # Вибрати еру Starfleet
        self.current_era = era
        if True:
            self.current_palette = get_era_palette(era)
            self.apply_theme_to_interface()
            self.show_palette()
            self.update_era_info(era.name.replace('_', ' ').title())
            print(f'Selected Starfleet era: {era.name}')
        if False: # Removed except block
            print(f'Error loading Starfleet era: {e}')
    
    def select_faction_era(self, era):
        # Вибрати еру іншої фракції
        self.current_era = era
        if True:
            self.current_palette = get_faction_palette(era)
            self.apply_theme_to_interface()
            self.show_palette()
            self.update_era_info(era.value.replace('_', ' ').title())
            print(f'Selected {self.current_faction.upper()} era: {era.name}')
        if False: # Removed except block
            print(f'Error loading faction era: {e}')
    
    def update_era_info(self, era_name):
        # Оновити інформацію про епоху
        faction_names = {
            'starfleet': 'STARFLEET',
            'klingon': 'KLINGON EMPIRE',
            'romulan': 'ROMULAN STAR EMPIRE', 
            'cardassian': 'CARDASSIAN UNION'
        }
        
        faction_name = faction_names.get(self.current_faction, self.current_faction.upper())
        self.era_info.setText(f"{faction_name} - {era_name}")
    
    def apply_theme_to_interface(self):
        # Застосувати тему до всього інтерфейсу
        if not self.current_palette:
            return
        
        palette = self.current_palette
        
        # Отримати кольори з палітри
        bg_color = palette.get('background', '#000000')
        text_color = palette.get('text', '#FFFFFF')
        button_colors = palette.get('button_colors', [])
        border_color = button_colors[0] if button_colors else '#FF6B6B'
        
        # Застосувати стилі до вікна
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg_color};
            }}
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New', monospace;
            }}
            QFrame {{
                border: 2px solid {border_color};
                border-radius: 8px;
                background-color: rgba(255, 107, 107, 0.1);
            }}
        """)
        
        # Оновити всі кнопки з кольорами теми
        self.update_all_button_colors()
        
        print(f"Theme applied: {self.current_faction.upper()} {self.current_era.name if self.current_era else 'Unknown'}")
        
        # Оновити консоль
        self.update_system_console()
    
    def update_all_button_colors(self):
        # Оновити кольори всіх кнопок
        if not self.current_palette:
            return
            
        button_colors = self.current_palette.get('button_colors', [])
        if not button_colors:
            return
        
        # Оновити кнопки фракцій та епох
        for button in self.findChildren(QPushButton):
            if button.text() in ['STARFLEET', 'KLINGON EMPIRE', 'ROMULAN STAR EMPIRE', 'CARDASSIAN UNION', 'MODE', 'BACK'] or \
               any(century in button.text() for century in ['22nd', '23rd', '23rd Alternative', '24th', '24th Sovereign', '25th', '29th']):
                color = random.choice(button_colors)
                button.setStyleSheet(f'''
                    QPushButton {{
                        background-color: {color};
                        color: #000000;
                        font-weight: bold;
                        padding: 10px;
                        border-radius: 6px;
                        border: 2px solid #000000;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background-color: #000000;
                        color: {color};
                    }}
                ''')
    
    def show_palette(self):
        if not self.current_palette:
            return
            
        # Показати опис палітри
        faction_names = {
            'starfleet': 'STARFLEET',
            'klingon': 'KLINGON EMPIRE',
            'romulan': 'ROMULAN STAR EMPIRE', 
            'cardassian': 'CARDASSIAN UNION'
        }
        
        faction_name = faction_names.get(self.current_faction, self.current_faction.upper())
        era_name = self.current_era.name if self.current_era else 'Unknown'
        
        palette_text = f"{faction_name} - {era_name}\\n\\n"
        palette_text += f"Background: {self.current_palette['background']}\\n"
        palette_text += f"Text: {self.current_palette['text']}\\n\\n"
        palette_text += "Button Colors:\\n"
        for i, color in enumerate(self.current_palette['button_colors']):
            palette_text += f"  {i+1:2d}. {color}\\n"
        
        if 'alert_colors' in self.current_palette:
            palette_text += "\\nAlert Colors:\\n"
            for i, color in enumerate(self.current_palette['alert_colors']):
                palette_text += f"  {i+1:2d}. {color}\\n"
        
        self.palette_display.setPlainText(palette_text)
        
        # Очистити попередні квадратики
        for i in reversed(range(self.colors_layout.count())):
            item = self.colors_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        
        # Всі кольори палітри
        all_colors = []
        for color in self.current_palette['button_colors']:
            if color.lower() not in ['#000000', '#ffffff', 'black', 'white']:
                all_colors.append(color)
        
        # Динамічний розмір квадратиків
        if len(all_colors) <= 4:
            square_size = 200
        elif len(all_colors) <= 8:
            square_size = 160
        else:
            square_size = 120
        
        colors_per_row = (len(all_colors) + 1) // 2
        
        # Створити сітку
        self.current_squares = []
        
        for row in range(2):
            row_layout = QHBoxLayout()
            row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            for col in range(colors_per_row):
                index = row * colors_per_row + col
                if index < len(all_colors):
                    color = all_colors[index]
                    
                    square = QLabel()
                    square.setFixedSize(square_size, square_size)
                    square.setStyleSheet(f"""
                        QLabel {{
                            background-color: {color};
                            border: 2px solid #000000;
                            border-radius: 12px;
                        }}
                    """)
                    square.setToolTip(color)
                    row_layout.addWidget(square)
                    self.current_squares.append(square)
            
            row_layout.addStretch()
            self.colors_layout.addLayout(row_layout)
        
        self.update()
        self.adjustSize()
    
    def toggle_mode(self):
        self.edit_mode = not self.edit_mode
        mode_text = "EDIT MODE ENABLED" if self.edit_mode else "DISPLAY MODE"
        
        if self.edit_mode:
            self.mode_btn.setStyleSheet('''
                QPushButton {
                    background-color: #FF6B6B;
                    color: #000000;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 6px;
                    border: 2px solid #000000;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #000000;
                    color: #FF6B6B;
                }
            ''')
            self.faction_welcome.setText("EDIT MODE - Interface editing enabled")
        else:
            if self.current_palette:
                color = random.choice(self.current_palette['button_colors'])
            else:
                color = get_random_button_color(LCARSEra.LCARS_25TH)
            
            self.mode_btn.setStyleSheet(f'''
                QPushButton {{
                    background-color: {color};
                    color: #000000;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 6px;
                    border: 2px solid #000000;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: #000000;
                    color: {color};
                }}
            ''')
            
            # Повернути привітання фракції
            if self.current_faction:
                greetings = {
                    'starfleet': 'Welcome to Starfleet Command',
                    'klingon': 'Honor and glory to the Empire!',
                    'romulan': 'Tal Shiar welcomes you',
                    'cardassian': 'Order and discipline prevail'
                }
                self.faction_welcome.setText(greetings.get(self.current_faction, 'Select a faction to begin'))
            else:
                self.faction_welcome.setText('Select a faction to begin')
        
        self.update_system_console()
        print(f"Mode changed: {mode_text}")
    
    def go_back(self):
        self.current_faction = None
        self.current_era = None
        self.current_palette = None
        self.edit_mode = False
        
        self.faction_welcome.setText('Select a faction to begin')
        self.era_info.setText('')
        self.eras_frame.setVisible(False)
        
        # Очистити палітру
        self.palette_display.setPlainText("LCARS THEME DEMO\n\nSelect a faction to see its color palette\n\nEach faction has unique colors:\n• STARFLEET - Federation colors\n• KLINGON EMPIRE - Warrior colors\n• ROMULAN STAR EMPIRE - Intelligence colors\n• CARDASSIAN UNION - Military colors")
        
        # Очистити кольорові квадратики
        for i in reversed(range(self.colors_layout.count())):
            item = self.colors_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        
        # Повернути початковий стиль
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QWidget {
                background-color: #000000;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                color: #000000;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: 2px solid #FF6B6B;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New', monospace;
            }
        """)
        
        self.update_system_console()
        print("Returned to welcome screen")
    
    def update_system_console(self):
        current_time = datetime.now()
        date_str = current_time.strftime("%Y.%m.%d")
        time_str = current_time.strftime("%H:%M:%S")
        star_date = f"{current_time.year - 1900}.{current_time.timetuple().tm_yday:03d}"
        
        console_text = f"═══════════════════════════════════════\n"
        console_text += f"    LCARS SYSTEM CONSOLE v2.0\n"
        console_text += f"═══════════════════════════════════════\n\n"
        console_text += f"🖖 LIVE LONG AND PROSPER\n"
        console_text += f"SYSTEM STATUS: ONLINE\n"
        console_text += f"DATE: {date_str}\n"
        console_text += f"TIME: {time_str}\n"
        console_text += f"STAR DATE: {star_date}\n"
        console_text += f"LOCATION: EARTH SPACE DOCK\n"
        console_text += f"USER: LCARS DEMO OPERATOR\n"
        console_text += f"SECURITY LEVEL: ALPHA\n\n"
        
        if self.current_faction:
            console_text += f"ACTIVE FACTION: {self.current_faction.upper()}\n"
            if self.current_era:
                console_text += f"ACTIVE ERA: {self.current_era.name}\n"
            console_text += f"THEME MODE: {'EDIT MODE' if self.edit_mode else 'DISPLAY MODE'}\n"
            console_text += f"PALETTE STATUS: LOADED\n"
        else:
            console_text += "ACTIVE FACTION: NONE\n"
            console_text += "ACTIVE ERA: NONE\n"
            console_text += "THEME MODE: DISPLAY MODE\n"
            console_text += "PALETTE STATUS: STANDBY\n"
        
        console_text += f"\nSYSTEM MODULES:\n"
        console_text += f"• LCARS INTERFACE: ACTIVE\n"
        console_text += f"• COLOR PALETTE SYSTEM: {'LOADED' if self.current_palette else 'STANDBY'}\n"
        console_text += f"• FACTION DATABASE: ONLINE\n"
        console_text += f"• ANIMATION ENGINE: RUNNING\n"
        console_text += f"• EDIT MODE: {'ENABLED' if self.edit_mode else 'DISABLED'}\n\n"
        
        console_text += f"AVAILABLE FACTIONS:\n"
        console_text += f"• STARFLEET (7 eras)\n"
        console_text += f"• KLINGON EMPIRE (4 eras)\n"
        console_text += f"• ROMULAN STAR EMPIRE (6 eras)\n"
        console_text += f"• CARDASSIAN UNION (5 eras)\n\n"
        
        console_text += f"AVAILABLE COMMANDS:\n"
        console_text += f"• Select faction → Select era → Apply theme\n"
        console_text += f"• MODE - Toggle edit mode\n"
        console_text += f"• BACK - Return to welcome\n\n"
        console_text += f"═══════════════════════════════════════"
        
        # Оновити консоль якщо існує
        if hasattr(self, 'console_display'):
            self.console_display.setPlainText(console_text)
    
    def animate_button(self, button):
        timer = QTimer()
        timer.setInterval(2000 + random.randint(0, 2000))
        
        def change_color():
            if True:
                if self.current_palette and self.current_palette.get('button_colors'):
                    color = random.choice(self.current_palette['button_colors'])
                else:
                    color = get_random_button_color(LCARSEra.LCARS_25TH)
                
                button.setStyleSheet(f'''
                    QPushButton {{
                        background-color: {color};
                        color: #000000;
                        font-weight: bold;
                        padding: 10px;
                        border-radius: 6px;
                        border: 2px solid #000000;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background-color: #000000;
                        color: {color};
                    }}
                ''')
            if False: # Removed except block
                print(f'Animation error: {e}')
        
        timer.timeout.connect(change_color)
        timer.start()
        self.button_timers[id(button)] = timer
        change_color()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('LCARS Full Theme Demo')
    
    demo = LCARSDemo()
    demo.show()
    
    print('🎨 LCARS Full Theme Demo Started')
    print('🖖 All factions with unique eras and palettes')
    print('📊 Total: 4 factions, 22 eras, 22 unique palettes')
    
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
