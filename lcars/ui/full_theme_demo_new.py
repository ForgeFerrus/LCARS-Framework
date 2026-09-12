"""
LCARS Theme Demo - Повноцінний інтерфейс з індивідуальними епохами
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QFrame, QLabel
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import random

# Додати шлях до проєкту
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.themes.lcars_palette import ERA_COLOR_PALETTES, LCARSEra, get_era_palette, get_random_button_color, get_alert_color
from lcars.themes.theme import FactionEra, get_faction_palette

class LCARSDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.button_timers = {}
        self.faction_eras_widgets = {}
        self.current_palette = None
        self.color_squares = []
        
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("LCARS Theme Demo")
        self.resize(1400, 800)
        self.setWindowFlags(Qt.WindowType.Window)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        
        # Привітання зверху
        welcome_label = QLabel("🖖 WELCOME TO LCARS THEME DEMO")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                background-color: #2F3749;
                border-radius: 10px;
                margin: 10px;
            }
        """)
        main_layout.addWidget(welcome_label)
        
        # Основний контент
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        
        # Ліва панель - фракції
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Кнопки фракцій
        factions = [
            ("STARFLEET", "starfleet"),
            ("KLINGON", "klingon"), 
            ("ROMULAN", "romulan"),
            ("CARDASSIAN", "cardassian")
        ]
        
        for name, faction in factions:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, f=faction: self.select_faction(f))
            left_layout.addWidget(btn)
            self.animate_button(btn)
        
        # Епохи для кожної фракції (спочатку приховані)
        for faction_key in ["starfleet", "klingon", "romulan", "cardassian"]:
            era_widget = QWidget()
            era_layout = QVBoxLayout(era_widget)
            era_widget.hide()
            
            if faction_key == "starfleet":
                eras = [
                    ("22nd", LCARSEra.COMS_22ND),
                    ("23rd", LCARSEra.PCARS_23RD),
                    ("24th", LCARSEra.LCARS_24TH),
                    ("25th", LCARSEra.LCARS_25TH),
                    ("29th", LCARSEra.TCARS_29TH)
                ]
            else:
                if faction_key == "klingon":
                    eras = [("24th", FactionEra.KLINGON_24TH)]
                elif faction_key == "romulan":
                    eras = [("24th", FactionEra.ROMULAN_24TH)]
                elif faction_key == "cardassian":
                    eras = [("24th", FactionEra.CARDASSIAN_24TH)]
                else:
                    eras = []
            
            for name, era in eras:
                btn = QPushButton(f"{name} Century")
                btn.clicked.connect(lambda checked, e=era: self.select_era(e))
                era_layout.addWidget(btn)
                self.animate_button(btn)
            
            left_layout.addWidget(era_widget)
            self.faction_eras_widgets[faction_key] = era_widget
        
        # Кнопка виходу
        exit_btn = QPushButton("EXIT")
        exit_btn.clicked.connect(self.close)
        left_layout.addWidget(exit_btn)
        
        left_layout.addStretch()
        content_layout.addWidget(left_panel)
        
        # Права панель - демонстрація
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Демонстрація кольорів
        self.color_display = QTextEdit()
        self.color_display.setReadOnly(True)
        self.color_display.setMaximumHeight(200)
        right_layout.addWidget(self.color_display)
        
        # Кольорові квадратики
        self.color_squares_layout = QHBoxLayout()
        right_layout.addLayout(self.color_squares_layout)
        
        # Консоль внизу
        console_frame = QFrame()
        console_layout = QVBoxLayout(console_frame)
        console_layout.addWidget(QLabel("LCARS CONSOLE"))
        
        self.console_display = QTextEdit()
        self.console_display.setReadOnly(True)
        self.console_display.setMaximumHeight(120)
        console_layout.addWidget(self.console_display)
        
        right_layout.addWidget(console_frame)
        
        content_layout.addWidget(right_panel)
        
    def select_faction(self, faction):
        if True:
            # Приховати всі епохи
            for key, widget in self.faction_eras_widgets.items():
                widget.hide()
            
            # Показати епохи для обраної фракції
            if faction in self.faction_eras_widgets:
                self.faction_eras_widgets[faction].show()
            
            self.update_console(f"Selected faction: {faction.upper()}\n\nShowing available eras for {faction}")
        if False: # Removed except block
            print(f"Error selecting faction {faction}: {e}")
            
    def select_era(self, era):
        if True:
            if hasattr(era, 'name'):
                # LCARSEra
                palette = get_era_palette(era)
                self.show_palette(palette)
                self.update_console(f"Selected era: {era.name}")
            else:
                # FactionEra
                palette = get_faction_palette(era)
                self.show_palette(palette)
                self.update_console(f"Selected era: {era.name}")
        if False: # Removed except block
            print(f"Error selecting era {era}: {e}")
            
    def show_palette(self, palette):
        # Показати палітру
        color_text = "LCARS PALETTE\n\n"
        color_text += f"Background: {palette['background']}\n"
        color_text += f"Text: {palette['text']}\n\n"
        color_text += "Button Colors:\n"
        for i, color in enumerate(palette['button_colors']):
            color_text += f"  {i+1}. {color}\n"
        color_text += "\nAlert Colors:\n"
        for i, color in enumerate(palette['alert_colors']):
            color_text += f"  {i+1}. {color}\n"
            
        self.color_display.setPlainText(color_text)
        
        # Створити кольорові квадратики
        for square in self.color_squares:
            square.deleteLater()
        self.color_squares.clear()
        
        for i, color in enumerate(palette['button_colors']):
            square = QLabel(str(i+1))
            square.setFixedSize(80, 80)
            square.setAlignment(Qt.AlignmentFlag.AlignCenter)
            square.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: {palette['background']};
                    font-weight: bold;
                    font-size: 24px;
                    border-radius: 12px;
                    border: 3px solid {palette['text']};
                }}
            """)
            
            self.color_squares.append(square)
            self.color_squares_layout.addWidget(square)
        
    def animate_button(self, button):
        timer = QTimer()
        timer.setInterval(2000 + random.randint(0, 2000))
        
        def change_color():
            color = get_random_button_color(LCARSEra.LCARS_25TH)
            button.setStyleSheet(f"""
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
            """)
        
        timer.timeout.connect(change_color)
        timer.start()
        self.button_timers[id(button)] = timer
        change_color()
        
    def update_console(self, message=""):
        console_text = "LCARS SYSTEM STATUS\n\n"
        console_text += ">> SYSTEM ONLINE\n"
        console_text += ">> THEME SELECTOR ACTIVE\n"
        console_text += ">> ALL SYSTEMS NOMINAL\n\n"
        
        if message:
            console_text += f">> {message}\n\n"
        
        console_text += "Select a faction to see its eras\n"
        console_text += "Click on an era to see its palette\n"
        console_text += "🖖 Live long and prosper!"
        
        self.console_display.setPlainText(console_text)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LCARS Demo")
    
    demo = LCARSDemo()
    demo.show()
    
    print("🎨 LCARS Theme Demo Started")
    print("🖖 Full interface with individual eras")
    print("🚀 All buttons animated with LCARS colors")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
