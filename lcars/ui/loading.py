"""
LCARS Boot Screen з Faction Selection
Чистий UI компонент - отримує готові дані, показує інтерфейс
"""
 
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
 
# Шлях до проекту
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
 
# Імпорти тем
from lcars.themes.lcars_palette import LCARSEra, get_faction_random_color
from lcars.themes.theme import FactionEra
from lcars.ui.lock_screen import get_lcars_font_style

# Дані фракцій
FACTIONS = {
    'federation': {
        'name': 'UFP',
        'era': FactionEra.STARFLEET_25TH,
        'description': 'Peace • Exploration • Unity',
    },
    'klingon': {
        'name': 'Klingon', 
        'era': FactionEra.KLINGON_25TH,
        'description': 'Honor • Strength • Victory',
    },
    'romulan': {
        'name': 'Romulan',
        'era': FactionEra.ROMULAN_25TH,
        'description': 'Logic • Secrecy • Power',
    },
    'cardassian': {
        'name': 'Cardassian',
        'era': FactionEra.CARDASSIAN_25TH,
        'description': 'Order • Discipline • State',
    }
}

class FactionButton(QPushButton):
    """Кнопка фракції з анімацією"""
 
    def __init__(self, faction_key, faction_data):
        super().__init__()
        self.faction_data = faction_data
        self.setFixedSize(200, 60)
        self.setText(faction_data['name'])
        self.setup_style()
 
        # Анімація кольору
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.setup_style)
        self.color_timer.start(2000)
 
    def setup_style(self):
        color = get_faction_random_color(self.faction_data['era'])
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #000000;
                border: none;
                border-radius: 8px;
                {get_lcars_font_style(28, "normal")}
                padding: 12px 16px;
            }}
            QPushButton:hover {{
                background-color: {get_faction_random_color(self.faction_data['era'])};
            }}
        """)

class LCARSBoot(QMainWindow):
    """Головний клас Boot Screen"""
 
    system_ready = pyqtSignal(str, str)  # faction, era
 
    def __init__(self):
        super().__init__()
        
        # Налаштування вікна
        self.setWindowTitle("LCARS System")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
        
        # Змінні стану
        self.boot_stage = 0
        self.selected_faction = None
        self.selected_era = None
        
        # Boot повідомлення
        self.boot_messages = [
            "INITIALIZING LCARS OPERATING SYSTEM...",
            "LOADING CORE SUBSYSTEMS...", 
            "ESTABLISHING NETWORK PROTOCOLS...",
            "LOADING FACTION DATABASES...",
            "SYSTEM READY FOR FACTION SELECTION"
        ]
        
        self.setup_interface()
        self.start_boot_sequence()
        
    def setup_interface(self):
        """Створити інтерфейс"""
        self.central = QWidget()
        self.setCentralWidget(self.central)
 
        layout = QVBoxLayout(self.central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addSpacing(100)
 
        # Центральний контент
        self.center_container = QWidget()
        self.center_layout = QVBoxLayout(self.center_container)
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.setSpacing(20)
 
        # Logo
        emblem = QLabel("🔵")
        emblem.setStyleSheet("color: #5588CC; font-size: 180px; background: transparent;")
        emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(emblem)
 
        # Заголовок
        title = QLabel("LCARS OPERATING SYSTEM")
        title.setStyleSheet(f"""
            color: #9EA5BA;
            {get_lcars_font_style(68, "normal")}
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(title)
 
        # Версія
        version = QLabel("VERSION 25.1.2026 - MULTI-FACTION SUPPORT")
        version.setStyleSheet(f"""
            color: #37A6D1;
            {get_lcars_font_style(22, "normal")}
            background: transparent;
        """)
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(version)
 
        self.center_layout.addSpacing(20)
 
        # Boot повідомлення
        self.boot_message = QLabel(self.boot_messages[0])
        self.boot_message.setStyleSheet(f"""
            color: #6D748C;
            {get_lcars_font_style(22, "normal")}
            background: transparent;
        """)
        self.boot_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(self.boot_message)
 
        # Progress індикатор
        self.setup_progress_indicator()
 
        layout.addWidget(self.center_container, 2)
        layout.addWidget(QLabel(""), 0)  # Footer spacer
        
    def setup_progress_indicator(self):
        """Створити progress індикатор"""
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.setSpacing(8)
 
        self.progress_colors = [
            "#37A6D1", "#2E8BC0", "#246B9E", "#1B4F7A",
            "#123757", "#1B4F7A", "#246B9E", "#2E8BC0"
        ]
 
        self.progress_dots = []
        for i in range(8):
            dot = QLabel("●")
            dot.setStyleSheet("color: #333333; font-size: 16px; background: transparent;")
            progress_layout.addWidget(dot)
            self.progress_dots.append(dot)
 
        self.center_layout.addWidget(progress_container)
        
    def start_boot_sequence(self):
        """Запустити boot послідовність"""
        self.boot_timer = QTimer()
        self.boot_timer.timeout.connect(self.advance_boot)
        self.boot_timer.start(1200)
 
    def advance_boot(self):
        """Просування boot послідовності"""
        # Оновити progress
        if self.boot_stage < len(self.progress_dots):
            if self.boot_stage > 0:
                self.progress_dots[self.boot_stage - 1].setStyleSheet(
                    "color: #333333; font-size: 16px; background: transparent;"
                )
            
            color_index = self.boot_stage % len(self.progress_colors)
            self.progress_dots[self.boot_stage].setStyleSheet(
                f"color: {self.progress_colors[color_index]}; font-size: 16px; background: transparent;"
            )
 
        self.boot_stage += 1
 
        # Оновити повідомлення
        if self.boot_stage < len(self.boot_messages):
            self.boot_message.setText(self.boot_messages[self.boot_stage])
        elif self.boot_stage == len(self.boot_messages):
            self.boot_timer.stop()
            self.show_faction_selection()
 
    def show_faction_selection(self):
        """Показати вибір фракцій"""
        self.boot_message.setText("SYSTEM READY - SELECT YOUR FACTION")
        self.boot_message.setStyleSheet(f"""
            color: #4BBEBF;
            {get_lcars_font_style(28, "normal")}
            background: transparent;
        """)

        # Кнопки фракцій
        faction_container = QWidget()
        faction_layout = QHBoxLayout(faction_container)
        faction_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        faction_layout.setSpacing(25)

        for faction_key, faction_data in FACTIONS.items():
            faction_button = FactionButton(faction_key, faction_data)
            faction_button.clicked.connect(
                lambda checked, fk=faction_key, fd=faction_data: self.select_faction(fk, fd)
            )
            faction_layout.addWidget(faction_button)

        self.center_layout.addSpacing(15)
        self.center_layout.addWidget(faction_container)

    def select_faction(self, faction_key, faction_data):
        """Вибрати фракцію"""
        self.selected_faction = faction_key
        
        # Federation прямо до 25th century
        if faction_key == 'federation':
            self.launch_era(faction_key, "25th")
        else:
            self.show_era_selection(faction_key, faction_data)
 
    def show_era_selection(self, faction_key, faction_data):
        """Показати вибір епохи"""
        self.boot_message.setText(f"SELECT {faction_data['name'].upper()} ERA")
 
        # Очистити кнопки фракцій
        self.clear_buttons()
        
        # Отримати доступні епохи
        from lcars.ui.era_factory import get_available_eras, get_era_description
        available_eras = get_available_eras(faction_key)
        
        # Кнопки епох
        era_container = QWidget()
        era_layout = QHBoxLayout(era_container)
        era_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        era_layout.setSpacing(30)
        
        for era in available_eras:
            era_btn = QPushButton(f"{era} CENTURY")
            era_btn.setFixedSize(200, 60)
            era_btn.setToolTip(get_era_description(faction_key, era))
            
            # Стиль кнопки
            era_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFCC66;
                    color: #000000;
                    border: none;
                    border-radius: 8px;
                    {get_lcars_font_style(18, "normal")}
                }}
                QPushButton:hover {{
                    background-color: #FF9900;
                }}
            """)
            
            era_btn.clicked.connect(lambda checked, e=era: self.launch_era(faction_key, e))
            era_layout.addWidget(era_btn)
 
        self.center_layout.addWidget(era_container)
        
    def clear_buttons(self):
        """Очистити кнопки"""
        for i in reversed(range(self.center_layout.count())):
            item = self.center_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    # Only call layout() if widget is not None
                    layout = getattr(widget, 'layout', None)
                    if callable(layout) and layout() is not None:
                        widget.deleteLater()
                    elif isinstance(widget, QPushButton):
                        widget.deleteLater()
 
    def launch_era(self, faction, era):
        """Запустити епоху"""
        self.selected_era = era
        
        self.boot_message.setText(f"STARTING {era} CENTURY INTERFACE...")
        
        QTimer.singleShot(1000, lambda: self.launch_era_interface(faction, era))
    
    def launch_era_interface(self, faction, era):
        """Запустити інтерфейс епохи"""
        if True:
            if faction == "federation":
                if era == "22nd":
                    from lcars.ui.factions.federation.era_22nd.login_screen import main as login_22nd
                    self.hide()
                    login_22nd()
                elif era == "24th":
                    from lcars.ui.factions.federation.era_24th.login_screen import main as login_24th
                    self.hide()
                    login_24th()
                elif era == "25th":
                    from lcars.ui.lock_screen import LCARSLockScreen
                    self.lock_screen = LCARSLockScreen(faction, era)
                    self.lock_screen.access_granted.connect(self.launch_desktop)
                    self.lock_screen.show()
                    self.hide()
                elif era == "29th":
                    from lcars.ui.factions.federation.era_29th.login_screen import main as login_29th
                    self.hide()
                    login_29th()
            else:
                # Інші фракції - 25th century
                from lcars.ui.lock_screen import LCARSLockScreen
                self.lock_screen = LCARSLockScreen(faction, "25th")
                self.lock_screen.access_granted.connect(self.launch_desktop)
                self.lock_screen.show()
                self.hide()
                
        if False: # Removed except block
            self.boot_message.setText(f"ERROR: {e}")
    
    def launch_desktop(self):
        """Запустити робочий стіл"""
        if True:
            if self.selected_faction == "federation" and self.selected_era == "22nd":
                from lcars.ui.factions.federation.era_22nd.desktop import NX01Desktop
                self.desktop = NX01Desktop()
            else:
                from lcars.ui.desktop import LCARSDesktop
                self.desktop = LCARSDesktop()
            
            self.desktop.show()
            
            if hasattr(self, 'lock_screen'):
                self.lock_screen.close()
                
        if False: # Removed except block
            print(f"Desktop error: {e}")

# Alias
LCARSBootScreen = LCARSBoot

def main():
    app = QApplication(sys.argv)
    
    from lcars.ui.lock_screen import setup_lcars_font
    setup_lcars_font()
    
    boot_screen = LCARSBoot()
    boot_screen.show()
    
    sys.exit(app.exec())
 
if __name__ == "__main__":
    main()
