# ◤ LCARS BOOT SCREEN :: Autonomous Titanium Component
# Самодостатній boot screen без зовнішніх залежностей
# ПРОТОКОЛ: Titanium v44.20 // CamelCase // Zero-External-Deps

# Titanium Bridge Migration: import sys
import random
# Titanium Bridge Migration: from enum import Enum

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal


# ◤ INTERNAL PALETTE SYSTEM (No External Dependencies)
class LCARSEra(Enum):
    PCARS_22ND = "22nd Century"
    PCARS_23RD = "23rd Century"
    LCARS_24TH = "24th Century"
    LCARS_25TH = "25th Century"
    TCARS_29TH = "29th Century"


# ◤ TITANIUM COLOR MATRIX
TITANIUM_COLORS = {
    "Scientific": ["#FFCC00", "#CC9900", "#FFAA00"],
    "Command": ["#CC6666", "#FF6666", "#AA4444"],
    "Medical": ["#6699CC", "#99CCFF", "#4477AA"],
    "Engineering": ["#CC99CC", "#CC66CC", "#9966CC"],
    "Navigation": ["#99CCFF", "#6699CC", "#4477AA"],
    "Alert": ["#CC0000", "#FF0000", "#990000"],
    "System": ["#3366CC", "#6699FF", "#99CCFF"],
}

LCARS_COLORS = [
    "#FFCC66", "#CC99CC", "#99CCFF", "#FF9966",
    "#66CC99", "#CC6666", "#FFCC00", "#3366CC"
]

FACTION_DATA = {
    "federation": {"Name": "UFP", "Description": "Peace • Exploration • Unity", "Emblem": "🔵"},
    "klingon": {"Name": "Klingon", "Description": "Honor • Strength • Victory", "Emblem": "🔺"},
    "romulan": {"Name": "Romulan", "Description": "Logic • Secrecy • Power", "Emblem": "🟩"},
    "cardassian": {"Name": "Cardassian", "Description": "Order • Discipline • State", "Emblem": "🔶"},
}


def GetRandomColor():
    return random.choice(LCARS_COLORS)


def GetLcarsFontStyle(Size, Weight="normal"):
    return f"font-family: 'LCARS', 'Arial', sans-serif; font-size: {Size}px; font-weight: {Weight};"


class FactionLaunchButton(QPushButton):
    def __init__(self, FactionKey, FactionData):
        super().__init__()
        self.FactionKey = FactionKey
        self.FactionData = FactionData
        self.setFixedSize(220, 60)
        self.SetupStyle()

    def SetupStyle(self):
        Color = GetRandomColor()
        FontStyle = GetLcarsFontStyle(18, "normal")
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Color};
                color: #000000;
                border: none;
                border-radius: 8px;
                {FontStyle}
                text-align: center;
                padding: 12px 16px;
            }}
            QPushButton:hover {{
                background-color: {GetRandomColor()};
                color: #000000;
                border: none;
            }}
            QPushButton:pressed {{
                background-color: {GetRandomColor()};
                color: #000000;
                border: none;
            }}
        """)
        self.setText(self.FactionData["Name"])


class LCARSBootScreen(QMainWindow):
    """Один боот скрін: boot -> faction -> era -> loading -> lock screen"""
    
    faction_selected = pyqtSignal(str, dict)  # Сигнал вибору фракції
    era_selected = pyqtSignal(str, str)  # Сигнал вибору епохи (faction, era)
    system_ready = pyqtSignal(str, str)  # Сигнал готовності системи
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS - Initializing System")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.boot_stage = 0
        self.current_state = "booting"  # booting -> faction_select -> era_select -> loading -> ready
        self.selected_faction = None
        self.selected_faction_data = None
        
        self.boot_messages = [
            "INITIALIZING LCARS OPERATING SYSTEM...",
            "LOADING CORE SUBSYSTEMS...", 
            "ESTABLISHING NETWORK PROTOCOLS...",
            "LOADING FACTION DATABASES...",
            "SYSTEM READY FOR FACTION SELECTION"
        ]
        
        # ЗАВЖДИ ЧОРНИЙ ФОН!
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
        
        self.setup_boot_interface()
        
        # Boot animation timer
        self.boot_timer = QTimer()
        self.boot_timer.timeout.connect(self.advance_boot)
        self.boot_timer.start(1200)
    
    def setup_boot_interface(self):
        """Налаштування інтерфейсу boot screen"""
        self.central = QWidget()
        self.setCentralWidget(self.central)
        
        layout = QVBoxLayout(self.central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Мінімальний top spacer - ПІДНЯТИ ВИЩЕ!
        layout.addSpacing(100)
        
        # Center content
        self.center_container = QWidget()
        self.center_layout = QVBoxLayout(self.center_container)
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.setSpacing(20)  # Менше spacing
        
        # LCARS Logo/Emblem з системними кольорами
        emblem = QLabel("🔵")
        emblem.setStyleSheet(f"""
            color: {GetRandomColor()};
            font-size: 180px;
            font-weight: 400;
            background: transparent;
        """)
        emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(emblem)
        
        # System title
        title = QLabel("LCARS OPERATING SYSTEM")
        title_style = GetLcarsFontStyle(48, "normal")
        title.setStyleSheet(f"""
            color: {GetRandomColor()};
            {title_style}
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(title)
        
        # Version info
        version = QLabel("VERSION 25.1.2026 - MULTI-FACTION SUPPORT")
        version_style = GetLcarsFontStyle(18, "normal")
        version.setStyleSheet(f"""
            color: {GetRandomColor()};
            {version_style}
            background: transparent;
        """)
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(version)
        
        self.center_layout.addSpacing(20)  # Менше spacing щоб підняти кнопки
        
        # Boot progress message
        self.boot_message = QLabel(self.boot_messages[0])
        message_style = GetLcarsFontStyle(20, "normal")
        self.boot_message.setStyleSheet(f"""
            color: {GetRandomColor()};
            {message_style}
            background: transparent;
        """)
        self.boot_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(self.boot_message)
        
        # Progress indicator
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.setSpacing(8)
        
        self.progress_dots = []
        for i in range(8):
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {GetRandomColor()}; font-size: 16px; background: transparent;")
            progress_layout.addWidget(dot)
            self.progress_dots.append(dot)
        
        self.center_layout.addWidget(progress_container)
        
        layout.addWidget(self.center_container, 2)
        
        # Bottom info
        footer = QLabel("")
        footer_style = GetLcarsFontStyle(14, "light")
        footer.setStyleSheet(f"""
            color: {GetRandomColor()};
            {footer_style}
            background: transparent;
            padding: 20px;
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
    
    def advance_boot(self):
        """Просування boot sequence"""
        if self.current_state != "booting":
            return
            
        # Оновити progress dots
        if self.boot_stage < len(self.progress_dots):
            self.progress_dots[self.boot_stage].setStyleSheet(
                f"color: {GetRandomColor()}; font-size: 16px; background: transparent;"
            )
        
        self.boot_stage += 1
        
        if self.boot_stage < len(self.boot_messages):
            self.boot_message.setText(self.boot_messages[self.boot_stage])
        elif self.boot_stage == len(self.boot_messages):
            # ЗУПИНКА НА ВИБІР ФРАКЦІЇ - як ви просили!
            self.boot_timer.stop()
            self.current_state = "faction_select"
            self.show_faction_selection()
    
    def show_faction_selection(self):
        """Показати кнопки вибору фракцій"""
        # Змінити повідомлення
        self.boot_message.setText("SYSTEM READY - SELECT YOUR FACTION")
        self.boot_message.setStyleSheet(f"""
            color: {GetRandomColor()};
            {GetLcarsFontStyle(22, "normal")}
            background: transparent;
        """)
        
        # Додати кнопки фракцій
        faction_container = QWidget()
        faction_layout = QHBoxLayout(faction_container)
        faction_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        faction_layout.setSpacing(25)  # Менше spacing між кнопками
        
        for faction_key, faction_data in FACTION_DATA.items():
            faction_button = FactionLaunchButton(faction_key, faction_data)
            faction_button.clicked.connect(
                lambda checked, fk=faction_key, fd=faction_data: self.select_faction(fk, fd)
            )
            faction_layout.addWidget(faction_button)
        
        self.center_layout.addSpacing(15)
        self.center_layout.addWidget(faction_container)
        
        # КНОПКИ НАЗАД І МОД!
        controls_container = QWidget()
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.setSpacing(20)
        
        # Кнопка повернення
        back_button = QPushButton("← RETURN TO BOOT")
        back_button.setFixedSize(200, 35)
        back_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {GetRandomColor()};
                color: #000000;
                border: none;
                border-radius: 6px;
                {GetLcarsFontStyle(12, "normal")}
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: {GetRandomColor()};
                border: none;
            }}
        """)
        back_button.clicked.connect(self.return_to_boot)
        controls_layout.addWidget(back_button)
        
        # Кнопка моду
        mod_button = QPushButton("MODE")
        mod_button.setFixedSize(200, 35)
        mod_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {GetRandomColor()};
                color: #000000;
                border: none;
                border-radius: 6px;
                {GetLcarsFontStyle(12, "normal")}
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: {GetRandomColor()};
                border: none;
            }}
        """)
        mod_button.clicked.connect(self.enter_dev_mode)
        controls_layout.addWidget(mod_button)
        
        self.center_layout.addSpacing(20)
        self.center_layout.addWidget(controls_container)
    
    def select_faction(self, faction_key, faction_data):
        """Обробити вибір фракції - перейти до вибору епохи"""
        print(f"◤ FACTION SELECTED: {faction_data['Name']}")
        
        self.selected_faction = faction_key
        self.selected_faction_data = faction_data
        self.current_state = "era_select"
        
        # НЕ змінюємо фон як просив користувач!
        
        # Перейти до вибору епохи
        QTimer.singleShot(300, self.show_era_selection)
    
    def show_era_selection(self):
        """Показати вибір епохи для обраної фракції"""
        self.boot_message.setText(f"SELECT {self.selected_faction_data['Name'].upper()} ERA")
        
        # Очистити кнопки фракцій
        for i in reversed(range(self.center_layout.count())):
            item = self.center_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'layout') and widget.layout():
                    # Перевіряємо чи це контейнер з кнопками
                    layout = widget.layout()
                    if layout.count() > 1:  # Контейнер з кнопками
                        widget.deleteLater()
        
        # Додати кнопки епох
        eras = [LCARSEra.LCARS_24TH, LCARSEra.LCARS_25TH, LCARSEra.PCARS_23RD, LCARSEra.TCARS_29TH]
        era_container = QWidget()
        era_layout = QHBoxLayout(era_container)
        era_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        era_layout.setSpacing(30)
        
        for era in eras:
            era_color = GetRandomColor()
            era_btn = QPushButton(era.value)
            era_btn.setFixedSize(200, 60)
            era_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {era_color};
                    color: #000000;
                    border: none;
                    border-radius: 8px;
                    {GetLcarsFontStyle(14, "normal")}
                }}
                QPushButton:hover {{
                    background-color: {GetRandomColor()};
                    border: none;
                }}
            """)
            era_btn.clicked.connect(lambda checked, e=era: self.select_era(e))
            era_layout.addWidget(era_btn)
        
        self.center_layout.addWidget(era_container)
    
    def select_era(self, era):
        """Обробити вибір епохи - завантажити автентичний інтерфейс"""
        print(f"🕰️ Era selected: {self.selected_faction} - {era.value}")
        
        self.current_state = "loading"
        
        # Показати завантаження автентичного інтерфейсу
        self.boot_message.setText(f"LOADING {self.selected_faction.upper()} {era.value} INTERFACE...")
        
        # Анімація завантаження
        self.setStyleSheet(f"QMainWindow {{ background-color: {GetRandomColor()}22; }}")
        
        # Завершити через 2 секунди
        QTimer.singleShot(2000, lambda: self.system_ready.emit(self.selected_faction, era.value))

    def return_to_boot(self):
        """Повернення до boot sequence"""
        self.current_state = "booting"
        self.boot_stage = 0
        
        # Очистити всі кнопки
        for i in reversed(range(self.center_layout.count())):
            item = self.center_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QPushButton):
                    widget.deleteLater()
        
        # Перезапустити boot
        self.boot_message.setText(self.boot_messages[0])
        self.boot_timer.start(1200)
    
    def enter_dev_mode(self):
        """Увійти в режим розробника"""
        print("🔧 Entering development mode...")
        self.close()
        # Тут можна запустити dev інтерфейс


def main():
    """Просто тест UI компонента"""
    app = QApplication(sys.argv)
    
    boot_screen = LCARSBootScreen()
    boot_screen.faction_selected.connect(
        lambda fk, fd: print(f"◤ SELECTED: {fd['Name']}")
    )
    boot_screen.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
