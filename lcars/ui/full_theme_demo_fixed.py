"""
LCARS Theme Demo - Повнофункціональна демонстрація з динамічним інтерфейсом
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QFrame, QMessageBox
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
    
    from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_random_button_color, get_palette_by_name
    from lcars.themes.theme import FactionEra, get_faction_palette
    print('LCARS modules imported successfully')
if False: # Removed except block
    print(f'Cannot import LCARS modules: {e}')
    sys.exit(1)

class LCARSDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_palette = None
        self.current_faction = None
        self.edit_mode = False
        self.button_timers = {}
        self.setup_ui()
        # Встановлюємо дефолтну тему
        self.select_faction('starfleet', 'Welcome to Starfleet Command')
        
    def setup_ui(self):
        self.setWindowTitle('LCARS Theme Demo - Fixed')
        self.showMaximized()
        self.setWindowFlags(Qt.WindowType.Window)
        
        # Початкова тема - чорний фон
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
        
        # Головний layout з системними кнопками зверху
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Системні кнопки на початку
        system_frame = QFrame()
        system_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #FF6B6B;
                border-radius: 8px;
                padding: 8px;
                background-color: rgba(255, 107, 107, 0.1);
            }
        """)
        system_layout = QHBoxLayout(system_frame)
        
        # Системні кнопки
        system_buttons = [
            ("🖖 SYSTEM", self.open_system_info),
            ("🎨 THEMES", self.open_theme_manager),
            ("⚙️ SETTINGS", self.open_settings),
            ("💾 SAVE", self.save_current_theme),
            ("🔄 RESET", self.reset_interface)
        ]
        
        for name, callback in system_buttons:
            btn = QPushButton(name)
            btn.setMinimumHeight(40)
            btn.clicked.connect(callback)
            system_layout.addWidget(btn)
            self.animate_button(btn)
        
        main_layout.addWidget(system_frame)
        
        # Основний контент
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        
        # Ліва панель - відсунута вбік, кнопки наверх
        left_panel = QWidget()
        left_panel.setFixedWidth(300)  # Компактна збоку
        left_layout = QVBoxLayout(left_panel)
        
        # Кнопки фракцій - наверх!
        factions = [
            ('STARFLEET', 'starfleet', 'Welcome to Starfleet Command'),
            ('KLINGON', 'klingon', 'Honor and glory to the Empire!'),
            ('ROMULAN', 'romulan', 'Tal Shiar welcomes you'),
            ('CARDASSIAN', 'cardassian', 'Order and discipline prevail')
        ]
        
        for name, faction, greeting in factions:
            btn = QPushButton(name)
            btn.setMinimumHeight(50)  # Кнопки наверх
            btn.clicked.connect(lambda checked, f=faction, g=greeting: self.select_faction(f, g))
            left_layout.addWidget(btn)
            self.animate_button(btn)
        
        # Кнопки управління - теж наверх
        bottom_control_layout = QHBoxLayout()
        
        self.mode_btn = QPushButton('MODE')
        self.mode_btn.setMinimumHeight(50)
        self.mode_btn.clicked.connect(self.toggle_mode)
        bottom_control_layout.addWidget(self.mode_btn)
        
        self.back_btn = QPushButton('BACK')
        self.back_btn.setMinimumHeight(40)
        self.back_btn.clicked.connect(self.go_back)
        bottom_control_layout.addWidget(self.back_btn)
        
        left_layout.addLayout(bottom_control_layout)
        
        # Вільне місце для майбутніх кнопок
        left_layout.addStretch()
        
        content_layout.addWidget(left_panel)
        
        # Центральна панель - основний дисплей
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        
        # Головний дисплей
        self.main_display = QTextEdit()
        self.main_display.setMinimumHeight(400)
        self.main_display.setPlainText("""
╔═══════════════════════════════════════════════════════╗
║                    LCARS FRAMEWORK                   ║
║                    Version 2.0.1                     ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  System Status: Online                               ║
║  Database: Connected                                 ║
║  Security: Active                                    ║
║                                                       ║
║  Select a faction to begin theme demonstration.      ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
        """)
        center_layout.addWidget(self.main_display)
        
        # Консоль
        console_frame = QFrame()
        console_layout = QVBoxLayout(console_frame)
        
        console_label = QLabel("System Console:")
        console_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        console_layout.addWidget(console_label)
        
        self.console = QTextEdit()
        self.console.setMaximumHeight(150)
        self.console.setPlainText("LCARS Demo initialized successfully.\nSelect faction to load theme.")
        console_layout.addWidget(self.console)
        
        center_layout.addWidget(console_frame)
        
        content_layout.addWidget(center_widget, 2)
        
        # Права панель - статус та налаштування
        right_panel = QWidget()
        right_panel.setFixedWidth(250)
        right_layout = QVBoxLayout(right_panel)
        
        # Статус панель
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        
        status_title = QLabel("SYSTEM STATUS")
        status_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        status_layout.addWidget(status_title)
        
        self.status_labels = []
        status_items = [
            "🟢 Core Systems: Online",
            "🟢 Theme Engine: Active",
            "🟡 Debug Mode: Standby",
            "🟢 Interface: Responsive"
        ]
        
        for item in status_items:
            label = QLabel(item)
            self.status_labels.append(label)
            status_layout.addWidget(label)
        
        right_layout.addWidget(status_frame)
        
        # Кнопки ери LCARS
        era_frame = QFrame()
        era_layout = QVBoxLayout(era_frame)
        
        era_title = QLabel("LCARS ERAS")
        era_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        era_layout.addWidget(era_title)
        
        era_buttons = [
            ("22nd Century", LCARSEra.COMS_22ND),
            ("23rd Century", LCARSEra.PCARS_23RD),
            ("24th Century", LCARSEra.LCARS_24TH),
            ("25th Century", LCARSEra.LCARS_25TH),
        ]
        
        for name, era in era_buttons:
            btn = QPushButton(name)
            btn.setMinimumHeight(35)
            btn.clicked.connect(lambda checked, e=era: self.select_era(e))
            era_layout.addWidget(btn)
            self.animate_button(btn)
        
        right_layout.addWidget(era_frame)
        right_layout.addStretch()
        
        content_layout.addWidget(right_panel)
        
        # Таймер для оновлення статусу
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)  # Кожні 2 секунди
        
    def animate_button(self, button):
        """Анімація кнопки при hover"""
        if True:
            # Створюємо унікальний таймер для кожної кнопки
            button_id = id(button)
            if button_id not in self.button_timers:
                self.button_timers[button_id] = QTimer()
                
            timer = self.button_timers[button_id]
            timer.timeout.connect(lambda: self.cycle_button_color(button))
            timer.start(1500)  # Зміна кольору кожні 1.5 секунди
        if False: # Removed except block
            print(f"Button animation error: {e}")
    
    def cycle_button_color(self, button):
        """Цикл кольорів для кнопки"""
        if True:
            if hasattr(self, 'current_palette') and self.current_palette:
                color = get_random_button_color(LCARSEra.LCARS_24TH)
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: #000000;
                        border: none;
                        border-radius: 8px;
                        font-weight: bold;
                        padding: 5px;
                    }}
                    QPushButton:hover {{
                        background-color: #FFFFFF;
                        color: #000000;
                    }}
                """)
        if False: # Removed except block
            print(f"Color cycle error: {e}")
    
    def select_faction(self, faction, greeting):
        """Вибір фракції та застосування теми"""
        if True:
            print(f"Selecting faction: {faction}")
            self.current_faction = faction
            
            # Отримання палітри фракції
            if True:
                palette = get_faction_palette(FactionEra(faction))
                self.current_palette = palette
                self.console.append(f"✅ Faction {faction.upper()} theme loaded successfully")
                print(f"Palette loaded: {list(palette.keys())}")
            if False: # Removed except block
                print(f"Faction palette error: {e}")
                # Fallback на LCARS палітру
                palette = get_era_palette(LCARSEra.LCARS_24TH)
                self.current_palette = palette
                self.console.append(f"⚠️ Using fallback LCARS theme for {faction}")
            
            # Оновлюємо головний дисплей
            self.main_display.setPlainText(f"""
╔═══════════════════════════════════════════════════════╗
║                  {faction.upper()} INTERFACE                 ║
║                    Status: Active                     ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  {greeting}             ║
║                                                       ║
║  Current Theme: {faction.upper()}                              ║
║  Era: 24th Century                                   ║
║  Mode: Standard Operation                            ║
║                                                       ║
║  All systems operational.                            ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
            """)
            
            self.apply_theme()
            
        if False: # Removed except block
            print(f"Faction selection error: {e}")
            self.console.append(f"❌ Error loading {faction} theme: {e}")
    
    def select_era(self, era):
        """Вибір ери LCARS"""
        if True:
            print(f"Selecting era: {era}")
            palette = get_era_palette(era)
            self.current_palette = palette
            self.console.append(f"✅ LCARS {era.value} era theme loaded")
            self.apply_theme()
            
            # Оновлюємо дисплей з інформацією про еру
            self.main_display.setPlainText(f"""
╔═══════════════════════════════════════════════════════╗
║                  LCARS {era.value.upper()} ERA                   ║
║                    Theme Active                       ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  Era: {era.value} Century                                   ║
║  Style: LCARS Interface                              ║
║  Colors: {len(palette.get('button_colors', []))} variations                    ║
║                                                       ║
║  Historical Context:                                 ║
║  {self.get_era_description(era)}
║                                                       ║
╚═══════════════════════════════════════════════════════╝
            """)
            
        if False: # Removed except block
            print(f"Era selection error: {e}")
            self.console.append(f"❌ Error loading era {era}: {e}")
    
    def get_era_description(self, era):
        """Опис ери"""
        descriptions = {
            LCARSEra.COMS_22ND: "Enterprise NX-01 Computer System",
            LCARSEra.PCARS_23RD: "Original Series Pre-LCARS",
            LCARSEra.LCARS_24TH: "Next Generation Standard",
            LCARSEra.LCARS_25TH: "Modern Starfleet Interface"
        }
        return descriptions.get(era, "Unknown era interface")
    
    def apply_theme(self):
        """Застосування поточної теми"""
        if True:
            if not self.current_palette:
                print("No palette to apply")
                return
            
            # Безпечний доступ до палітри
            background = self.current_palette.get('background', '#000000')
            text = self.current_palette.get('text', '#FFFFFF')
            panel_border = self.current_palette.get('panel_border', '#FF6B6B')
            button_colors = self.current_palette.get('button_colors', ['#FF6B6B'])
            
            primary_color = button_colors[0] if button_colors else '#FF6B6B'
            secondary_color = button_colors[1] if len(button_colors) > 1 else primary_color
            
            style = f"""
            QMainWindow {{
                background-color: {background};
            }}
            QWidget {{
                background-color: {background};
                color: {text};
            }}
            QLabel {{
                color: {text};
            }}
            QPushButton {{
                background-color: {primary_color};
                color: {background};
                border: none;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px;
                margin: 2px;
            }}
            QPushButton:hover {{
                background-color: {secondary_color};
            }}
            QTextEdit {{
                background-color: {background};
                color: {text};
                border: 2px solid {panel_border};
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New', monospace;
            }}
            QFrame {{
                border: 2px solid {panel_border};
                border-radius: 8px;
                padding: 5px;
                background-color: rgba{self.hex_to_rgba(panel_border, 0.1)};
            }}
            """
            
            self.setStyleSheet(style)
            print(f"Theme applied successfully with colors: {list(self.current_palette.keys())}")
            
        if False: # Removed except block
            print(f"Theme application error: {e}")
            self.console.append(f"❌ Theme application error: {e}")
    
    def hex_to_rgba(self, hex_color, alpha):
        """Конвертування HEX в RGBA"""
        if True:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f"({r}, {g}, {b}, {alpha})"
        if False: # Removed except block
            return "(255, 107, 107, 0.1)"
    
    def update_status(self):
        """Оновлення статусних індикаторів"""
        if True:
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Оновлюємо статуси випадково
            if random.random() < 0.3:  # 30% шанс зміни
                statuses = ["🟢 Online", "🟡 Standby", "🔴 Alert", "🔵 Processing"]
                for label in self.status_labels:
                    if random.random() < 0.2:  # 20% шанс для кожного
                        original_text = label.text().split(': ')[0]
                        new_status = random.choice(statuses)
                        label.setText(f"{original_text}: {new_status}")
            
        if False: # Removed except block
            print(f"Status update error: {e}")
    
    # Системні функції
    def open_system_info(self):
        self.console.append("🖖 System Information accessed")
        self.main_display.setPlainText("System Information Panel - Under Development")
    
    def open_theme_manager(self):
        self.console.append("🎨 Theme Manager opened")
        self.main_display.setPlainText("Theme Management Interface - Under Development")
    
    def open_settings(self):
        self.console.append("⚙️ Settings panel accessed")
        self.main_display.setPlainText("Settings Configuration - Under Development")
    
    def save_current_theme(self):
        if self.current_palette:
            self.console.append(f"💾 Theme saved: {self.current_faction or 'current'}")
        else:
            self.console.append("❌ No theme to save")
    
    def reset_interface(self):
        self.console.append("🔄 Interface reset")
        self.main_display.setPlainText("Interface Reset Complete")
        # Reset to default
        self.select_faction('starfleet', 'Interface reset to default')
    
    def toggle_mode(self):
        self.edit_mode = not self.edit_mode
        mode_text = "EDIT" if self.edit_mode else "VIEW"
        self.mode_btn.setText(f"MODE: {mode_text}")
        self.console.append(f"🔄 Switched to {mode_text} mode")
    
    def go_back(self):
        self.console.append("⬅️ Navigation: Back")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = LCARSDemo()
    demo.show()
    sys.exit(app.exec())
