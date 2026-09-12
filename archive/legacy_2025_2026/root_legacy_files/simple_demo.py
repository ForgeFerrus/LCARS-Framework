import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import random
from datetime import datetime

# Додати шлях до проєкту
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

try:
    from lcars.themes.lcars_palette import get_random_button_color, LCARSEra, get_era_palette, get_random_button_color
    from lcars.themes.theme import FactionEra, get_faction_palette
    print('LCARS modules imported successfully')
except ImportError as e:
    print(f'Cannot import LCARS modules: {e}')
    sys.exit(1)

class LCARSDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_palette = None
        self.current_faction = None
        self.edit_mode = False
        self.setup_ui()
        self.update_system_console()
        
    def setup_ui(self):
        self.setWindowTitle('LCARS Theme Demo')
        self.resize(1000, 600)  # Зменшений розмір
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
        
        # Консоль зверху
        console_frame = QFrame()
        console_layout = QVBoxLayout(console_frame)
        
        console_label = QLabel('LCARS SYSTEM CONSOLE')
        console_label.setStyleSheet('''
            QLabel {
                color: #FF6B6B;
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }
        ''')
        console_layout.addWidget(console_label)
        
        self.console_display = QTextEdit()
        self.console_display.setReadOnly(True)
        self.console_display.setMaximumHeight(120)  # Зменшена висота консолі
        console_layout.addWidget(self.console_display)
        
        main_layout.addWidget(console_frame)
        
        # Основний контент
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        
        # Ліва панель - кнопки фракцій
        left_panel = QWidget()
        left_panel.setFixedWidth(250)  # Зменшена ширина
        left_layout = QVBoxLayout(left_panel)
        
        # Привітання
        welcome_label = QLabel('LCARS')
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet('''
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                background-color: #2F3749;
                border-radius: 10px;
                margin: 10px;
            }
        ''')
        left_layout.addWidget(welcome_label)
        
        # Індивідуальні привітання для кожної фракції
        self.faction_welcome = QLabel('Select a faction to begin')
        self.faction_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.faction_welcome.setStyleSheet('''
            QLabel {
                color: #CCCCCC;
                font-size: 16px;
                padding: 10px;
                margin: 5px;
            }
        ''')
        left_layout.addWidget(self.faction_welcome)
        
        # Кнопки фракцій
        factions = [
            ('STARFLEET', 'starfleet', 'Welcome to Starfleet Command'),
            ('KLINGON', 'klingon', 'Honor and glory to the Empire!'),
            ('ROMULAN', 'romulan', 'Tal Shiar welcomes you'),
            ('CARDASSIAN', 'cardassian', 'Order and discipline prevail')
        ]
        
        for name, faction, greeting in factions:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, f=faction, g=greeting: self.select_faction(f, g))
            left_layout.addWidget(btn)
            self.animate_button(btn)
        
        # Кнопки управління
        control_layout = QHBoxLayout()
        
        self.mode_btn = QPushButton('MODE')
        self.mode_btn.clicked.connect(self.toggle_mode)
        control_layout.addWidget(self.mode_btn)
        
        self.back_btn = QPushButton('BACK')
        self.back_btn.clicked.connect(self.go_back)
        control_layout.addWidget(self.back_btn)
        
        left_layout.addLayout(control_layout)
        left_layout.addStretch()
        content_layout.addWidget(left_panel)
        
        # Права панель - демонстрація палітри
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Опис палітри
        self.palette_display = QTextEdit()
        self.palette_display.setReadOnly(True)
        self.palette_display.setMaximumHeight(150)  # Зменшена висота
        self.palette_display.setPlainText("LCARS THEME DEMO\n\nSelect a faction to see its color palette\n\nEach faction has unique colors:\n• STARFLEET - Federation colors\n• KLINGON - Warrior colors\n• ROMULAN - Intelligence colors\n• CARDASSIAN - Military colors")
        right_layout.addWidget(self.palette_display)
        
        # Кольорові квадратики
        self.colors_layout = QHBoxLayout()
        right_layout.addLayout(self.colors_layout)
        
        right_layout.addStretch()
        content_layout.addWidget(right_panel)
        
    def update_system_console(self):
        # Оновити системну консоль з повною інформацією
        current_time = datetime.now()
        date_str = current_time.strftime("%Y.%m.%d")
        time_str = current_time.strftime("%H:%M:%S")
        
        # Генеруємо зоряну дату
        star_date = f"{current_time.year - 1900}.{current_time.timetuple().tm_yday:03d}"
        
        console_text = f"═══════════════════════════════════════\n"
        console_text += f"    LCARS SYSTEM CONSOLE v1.0\n"
        console_text += f"═══════════════════════════════════════\n\n"
        console_text += f"SYSTEM STATUS: ONLINE\n"
        console_text += f"DATE: {date_str}\n"
        console_text += f"TIME: {time_str}\n"
        console_text += f"STAR DATE: {star_date}\n"
        console_text += f"LOCATION: EARTH SPACE DOCK\n"
        console_text += f"USER: LCARS DEMO OPERATOR\n"
        console_text += f"SECURITY LEVEL: ALPHA\n\n"
        
        if self.current_faction:
            console_text += f"ACTIVE FACTION: {self.current_faction.upper()}\n"
            console_text += f"THEME MODE: {'EDIT MODE' if self.edit_mode else 'DISPLAY MODE'}\n"
        else:
            console_text += "ACTIVE FACTION: NONE\n"
            console_text += "THEME MODE: DISPLAY MODE\n"
        
        console_text += f"\nSYSTEM MODULES:\n"
        console_text += f"• LCARS INTERFACE: ACTIVE\n"
        console_text += f"• COLOR PALETTE SYSTEM: {'LOADED' if self.current_palette else 'STANDBY'}\n"
        console_text += f"• FACTION DATABASE: ONLINE\n"
        console_text += f"• ANIMATION ENGINE: RUNNING\n"
        console_text += f"• EDIT MODE: {'ENABLED' if self.edit_mode else 'DISABLED'}\n\n"
        
        console_text += f"AVAILABLE COMMANDS:\n"
        console_text += f"• Select faction to load theme\n"
        console_text += f"• MODE - Toggle edit mode\n"
        console_text += f"• BACK - Return to welcome\n\n"
        
        console_text += f"🖖 LIVE LONG AND PROSPER\n"
        console_text += f"═══════════════════════════════════════"
        
        self.console_display.setPlainText(console_text)
        
    def toggle_mode(self):
        self.edit_mode = not self.edit_mode
        mode_text = "EDIT MODE ENABLED" if self.edit_mode else "DISPLAY MODE"
        self.update_system_console()
        print(f"Mode changed: {mode_text}")
        
    def go_back(self):
        self.current_faction = None
        self.current_palette = None
        self.edit_mode = False
        self.faction_welcome.setText('Select a faction to begin')
        
        # Очистити палітру
        self.palette_display.setPlainText("LCARS THEME DEMO\n\nSelect a faction to see its color palette\n\nEach faction has unique colors:\n• STARFLEET - Federation colors\n• KLINGON - Warrior colors\n• ROMULAN - Intelligence colors\n• CARDASSIAN - Military colors")
        
        # Очистити кольорові квадратики
        for i in reversed(range(self.colors_layout.count())):
            item = self.colors_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        
        self.update_system_console()
        print("Returned to welcome screen")
        
    def select_faction(self, faction, greeting):
        # Вибрати фракцію та показати її палітру
        self.faction_welcome.setText(greeting)
        self.current_faction = faction
        
        try:
            if faction == 'starfleet':
                self.current_palette = get_era_palette(LCARSEra.LCARS_25TH)
            elif faction == 'klingon':
                self.current_palette = get_faction_palette(FactionEra.KLINGON_25TH)
            elif faction == 'romulan':
                self.current_palette = get_faction_palette(FactionEra.ROMULAN_25TH)
            elif faction == 'cardassian':
                self.current_palette = get_faction_palette(FactionEra.CARDASSIAN_25TH)
            
            self.show_palette()
            print(f'Selected faction: {faction.upper()}')
        except Exception as e:
            print(f'Error loading faction palette: {e}')
    
    def show_palette(self):
        if not self.current_palette:
            return
            
        # Показати опис палітри
        palette_text = f"{self.current_palette.get('name', 'LCARS Palette')}\\n\\n"
        palette_text += f"Background: {self.current_palette['background']}\\n"
        palette_text += f"Text: {self.current_palette['text']}\\n\\n"
        palette_text += "Button Colors:\\n"
        for i, color in enumerate(self.current_palette['button_colors'][:8]):  # Показати перші 8 кольорів
            palette_text += f"  {i+1}. {color}\\n"
        
        self.palette_display.setPlainText(palette_text)
        
        # Створити кольорові квадратики
        # Очистити існуючі квадратики
        for i in reversed(range(self.colors_layout.count())):
            item = self.colors_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        
        # Додати нові квадратики
        for i, color in enumerate(self.current_palette['button_colors'][:8]):
            square = QLabel()
            square.setFixedSize(70, 70)  # Збільшений розмір
            square.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    border: 2px solid #FFFFFF;
                    border-radius: 8px;
                }}
            """)
            self.colors_layout.addWidget(square)
        
    def animate_button(self, button):
        from PyQt6.QtCore import QTimer
        import random
        
        timer = QTimer()
        timer.setInterval(2000 + random.randint(0, 2000))
        
        def change_color():
            try:
                color = get_random_button_color(LCARSEra.LCARS_25TH)
                button.setStyleSheet(f'''
                    QPushButton {{
                        background-color: {color};
                        color: #000000;
                        font-weight: bold;
                        padding: 10px;
                        border-radius: 6px;
                        border: 2px solid #FFFFFF;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background-color: #FFFFFF;
                        color: {color};
                    }}
                ''')
            except Exception as e:
                print(f'Animation error: {e}')
        
        timer.timeout.connect(change_color)
        timer.start()
        change_color()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('LCARS Demo')
    
    demo = LCARSDemo()
    demo.show()
    
    print('🎨 LCARS Theme Demo Started')
    print('🖖 Simple menu with welcome message')
    
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
