import sys
import os
import psutil
import time
import subprocess
import random
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QTabWidget, 
                           QTextEdit, QListWidget, QProgressBar, QGridLayout,
                           QGroupBox, QFrame, QMessageBox, QStackedWidget,
                           QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QProcess, QSize, QRectF
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor, QPainter, QPainterPath, QBrush, QPen

# Додавання шляху до проекту
current_file = Path(__file__).resolve()
project_root = current_file.parents[1]  # Виправлено - parents[1] замість parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    
from lcars.themes.lcars_palette import get_random_button_color, LCARSEra, get_era_palette
from lcars.themes.theme import FactionEra, get_faction_palette

class LCARSDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_palette = None
        self.current_faction = None
        self.edit_mode = False
        self.console_display = QTextEdit()
        self.console_display.setReadOnly(True)
        self.console_display.setMaximumHeight(200)  # Зменшена висота
        self.console_display.setPlainText("LCARS THEME DEMO\n\nSelect a faction to see its color palette\n\nEach faction has unique colors:\n• STARFLEET - Federation colors\n• KLINGON - Warrior colors\n• ROMULAN - Intelligence colors\n• CARDASSIAN - Military colors")
        self.setup_ui()
        self.update_system_console()
        
    def setup_ui(self):
        self.setWindowTitle('LCARS Theme Demo')
        self.showMaximized()  # Повноекранний режим!
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
        left_layout.addStretch()
        content_layout.addWidget(left_panel)
        
        # Права панель - демонстрація палітри
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Привітання - центроване з великим шрифтом
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
        
        # Індивідуальні привітання для кожної фракції
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
        
        # Опис палітри
        self.palette_display = QTextEdit()
        self.palette_display.setReadOnly(True)
        self.palette_display.setMaximumHeight(150)  # Зменшена висота
        self.palette_display.setPlainText("LCARS THEME DEMO\n\nSelect a faction to see its color palette\n\nEach faction has unique colors:\n• STARFLEET - Federation colors\n• KLINGON - Warrior colors\n• ROMULAN - Intelligence colors\n• CARDASSIAN - Military colors")
        right_layout.addWidget(self.palette_display)
        
        # Кольорові квадратики - динамічний контейнер
        self.colors_container = QWidget()
        self.colors_container_layout = QVBoxLayout(self.colors_container)
        self.colors_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.colors_container)
        
        self.colors_layout = QVBoxLayout()
        self.colors_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.colors_container_layout.addLayout(self.colors_layout)
        
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
        console_text += f"═══════════════════════════════════════"
        
        self.console_display.setPlainText(console_text)
        
    def toggle_mode(self):
        self.edit_mode = not self.edit_mode
        mode_text = "EDIT MODE ENABLED" if self.edit_mode else "DISPLAY MODE"
        
        if self.edit_mode:
            # РЕЖИМ РЕДАГУВАННЯ - дозволити взаємодію з квадратиками
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
            
            # Зробити квадратики інтерактивними
            self.make_squares_interactive()
            
            # Показати повідомлення про редагування
            self.faction_welcome.setText("EDIT MODE - Click colors to modify")
            
        else:
            # РЕЖИМ ДИСПЛЕЮ - тільки перегляд
            # Повернути колір з поточної палітри
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
            
            # Повернути квадратики до звичайного стану
            self.make_squares_normal()
            
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
    
    def make_squares_interactive(self):
        # Зробити квадратики інтерактивними в режимі редагування
        if hasattr(self, 'current_squares'):
            for square in self.current_squares:
                square.setCursor(Qt.CursorShape.PointingHandCursor)
                square.setStyleSheet(square.styleSheet() + """
                    QLabel:hover {
                        border: 3px solid #FF6B6B;
                        transform: scale(1.05);
                    }
                """)
    
    def make_squares_normal(self):
        # Повернути квадратики до звичайного стану
        if hasattr(self, 'current_squares'):
            for square in self.current_squares:
                square.setCursor(Qt.CursorShape.ArrowCursor)
                # Прибрати hover ефекти
        
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
            
            # Оновити кольори всіх кнопок відразу!
            self.update_all_button_colors()
            # Показати кольорові квадратики
            self.show_palette()
            print(f'Selected faction: {faction.upper()}')
        except Exception as e:
            print(f'Error loading faction palette: {e}')
    
    def update_all_button_colors(self):
        # Оновити кольори всіх кнопок відразу при виборі фракції
        if not self.current_palette:
            return
            
        # Знайти всі кнопки фракцій та управління
        for button in self.findChildren(QPushButton):
            if button.text() in ['STARFLEET', 'KLINGON', 'ROMULAN', 'CARDASSIAN', 'MODE', 'BACK']:
                color = random.choice(self.current_palette['button_colors'])
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
        palette_text = f"{self.current_palette.get('name', 'LCARS Palette')}\\n\\n"
        palette_text += f"Background: {self.current_palette['background']}\\n"
        palette_text += f"Text: {self.current_palette['text']}\\n\\n"
        palette_text += "Button Colors:\\n"
        for i, color in enumerate(self.current_palette['button_colors']):
            palette_text += f"  {i+1:2d}. {color}\\n"
        
        self.palette_display.setPlainText(palette_text)
        
        # Повністю очистити контейнер перед створенням нових квадратиків
        # Видаляємо всі віджети з контейнера
        for i in reversed(range(self.colors_layout.count())):
            item = self.colors_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                else:
                    # Видаляємо layout
                    item.setParent(None)
        
        # Всі кольори палітри (без алерт)
        all_colors = []
        
        # Додати кнопкові кольори
        for color in self.current_palette['button_colors']:
            if color.lower() not in ['#000000', '#ffffff', 'black', 'white']:
                all_colors.append(color)
        
        # Динамічний розмір квадратиків залежно від кількості
        if len(all_colors) <= 4:
            square_size = 200
        elif len(all_colors) <= 8:
            square_size = 160
        else:
            square_size = 120
        
        colors_per_row = (len(all_colors) + 1) // 2  # Половина в кожному рядку
        
        # Створити сітку 2 рядки
        self.current_squares = []  # Зберегти квадратики для взаємодії
        
        for row in range(2):
            row_layout = QHBoxLayout()
            row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            for col in range(colors_per_row):
                index = row * colors_per_row + col
                if index < len(all_colors):
                    color = all_colors[index]
                    
                    # Динамічний квадратик кольору
                    square = QLabel()
                    square.setFixedSize(square_size, square_size)
                    square.setStyleSheet(f"""
                        QLabel {{
                            background-color: {color};
                            border: 2px solid #000000;
                            border-radius: 12px;
                        }}
                    """)
                    row_layout.addWidget(square)
                    self.current_squares.append(square)
            
            row_layout.addStretch()
            self.colors_layout.addLayout(row_layout)
        
        # Якщо в режимі редагування, зробити квадратики інтерактивними
        if self.edit_mode:
            self.make_squares_interactive()
        
        # Оновити контейнер щоб він адаптувався
        self.colors_container.update()
        self.colors_container.adjustSize()
        # Оновити все вікно
        self.update()
        self.adjustSize()
        
    def animate_button(self, button):
        from PyQt6.QtCore import QTimer
        import random
        
        timer = QTimer()
        timer.setInterval(2000 + random.randint(0, 2000))
        
        def change_color():
            try:
                # Завжди використовуємо кольори з поточної палітри якщо є
                if self.current_palette and self.current_faction:
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
            except Exception as e:
                print(f'Animation error: {e}')
        
        timer.timeout.connect(change_color)
        timer.start()
        # Зберегти таймер для кнопки
        if hasattr(self, 'button_timers'):
            self.button_timers[id(button)] = timer
        else:
            self.button_timers = {id(button): timer}
        
        # Одразу змінити колір
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
