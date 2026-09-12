"""
LCARS Launcher - справжній LCARS інтерфейс запуску системи
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from typing import Dict, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QLineEdit, QComboBox, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

# Додавання шляху до проекту
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.themes.lcars_palette import (
    LCARSEra, get_era_palette, get_random_button_color,
    get_lcars_font_style, setup_lcars_font
)


class LCARSButton(QPushButton):
    """LCARS кнопка для лаунчера"""
    
    def __init__(self, text, color=None, shape="rect", parent=None):
        super().__init__(text, parent)
        self.shape = shape
        
        # ДИНАМІЧНИЙ КОЛІОР - буде змінюватися
        self.dynamic_color = None
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_color)
        self.color_timer.start(2000)  # Зміна кольору кожні 2 секунди
        
        # Початковий колір
        self.update_color()
        
        # Розміри
        if shape == "wide":
            self.setFixedWidth(200)
            self.setFixedHeight(50)
        elif shape == "tall":
            self.setFixedWidth(100)
            self.setFixedHeight(150)
        else:
            self.setFixedSize(150, 50)
        
        # ДИНАМІЧНИЙ СТИЛЬ LCARS
        self.apply_lcars_style()

    def update_color(self):
        """Оновлення кольору кнопки"""
        self.dynamic_color = get_random_button_color(LCARSEra.LCARS_25TH)
        self.apply_lcars_style()

    def apply_lcars_style(self):
        """Застосування динамічного LCARS стилю"""
        font_style = get_lcars_font_style(12, 'bold')
        
        if self.shape == "tall":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.dynamic_color};
                    color: #000000;
                    border: none;
                    border-top-left-radius: 30px;
                    border-bottom-left-radius: 30px;
                    {font_style}
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: #FFFFFF;
                    color: {self.dynamic_color};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.dynamic_color};
                    color: #000000;
                    border: none;
                    border-radius: 20px;
                    {font_style}
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: #FFFFFF;
                    color: {self.dynamic_color};
                }}
            """)


class LCARSLauncher(QMainWindow):
    """Справжній LCARS лаунчер з повноцінним інтерфейсом"""
    
    # Сигнали для переходів між екранами
    login_success = pyqtSignal()
    desktop_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS SYSTEM LAUNCHER")
        self.setGeometry(0, 0, 1920, 1080)
        
        # Безрамковий повноекранний режим
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        # ІНІЦІАЛІЗАЦІЯ СИСТЕМИ
        self.initialize_system()
        
        # Таймер для годинника
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()
        
        # Підключення сигналів
        self.login_success.connect(self.show_desktop)
        self.desktop_requested.connect(self.launch_desktop)
    
    def initialize_system(self):
        """Повна ініціалізація LCARS системи"""
        # Ініціалізація тем
        self.setup_theme_system()
        
        # Ініціалізація шрифтів
        self.setup_font_system()
        
        # Створення UI
        self.setup_ui()
    
    def setup_theme_system(self):
        """Налаштування системи тем"""
        # Базова палітра 25th ери
        self.base_palette = get_era_palette("25th")
        
        # Система динамічних кольорів
        self.dynamic_colors = {}
        self.generate_dynamic_colors()
    
    def setup_font_system(self):
        """Налаштування системи шрифтів"""
        if True:
            setup_lcars_font()
            self.font_system_ready = True
        if False: # Removed except block
            self.font_system_ready = False
            # Fallback на системні шрифти
            QFont.setFontSubstitutions(["Arial", "Swiss 721 BT"])
    
    def generate_dynamic_colors(self):
        """Генерація динамічних кольорів без присвоєння"""
        # Використовуємо рандомний алгоритм для кожного елемента
        self.dynamic_colors = {
            'primary': get_random_button_color(LCARSEra.LCARS_25TH),
            'secondary': get_random_button_color(LCARSEra.LCARS_25TH),
            'accent': get_random_button_color(LCARSEra.LCARS_25TH),
            'warning': get_random_button_color(LCARSEra.LCARS_25TH),
            'success': get_random_button_color(LCARSEra.LCARS_25TH)
        }
    
    def setup_ui(self):
        """Створення LCARS інтерфейсу лаунчера"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: #000000;")
        
        # Основний layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Стек для різних екранів
        self.stack = QStackedWidget()
        
        # Екран вибору фракції
        self.faction_screen = self.create_faction_screen()
        self.stack.addWidget(self.faction_screen)
        
        # Екран входу
        self.login_screen = self.create_login_screen()
        self.stack.addWidget(self.login_screen)
        
        # Екран блокування
        self.lock_screen = self.create_lock_screen()
        self.stack.addWidget(self.lock_screen)
        
        main_layout.addWidget(self.stack)
        
        # Показуємо початковий екран
        self.stack.setCurrentWidget(self.faction_screen)
    
    def create_faction_screen(self):
        """Екран вибору фракції та епохи"""
        screen = QWidget()
        screen.setStyleSheet("background-color: #000000;")
        
        layout = QVBoxLayout(screen)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Верхня кутова панель
        top_panel = self.create_launcher_top_panel("◢ LCARS SYSTEM LAUNCHER")
        layout.addWidget(top_panel)
        
        # Центральна область
        center_layout = QHBoxLayout()
        center_layout.setContentsMargins(50, 50, 50, 50)
        center_layout.setSpacing(30)
        
        # Ліва панель - вибір фракції
        left_panel = self.create_faction_panel()
        center_layout.addWidget(left_panel)
        
        # Центральна панель - вибір епохи
        center_panel = self.create_era_panel()
        center_layout.addWidget(center_panel)
        
        # Права панель - кнопка запуску
        right_panel = self.create_launch_panel()
        center_layout.addWidget(right_panel)
        
        layout.addLayout(center_layout)
        
        # Нижня панель
        bottom_panel = self.create_launcher_bottom_panel()
        layout.addWidget(bottom_panel)
        
        return screen
    
    def create_login_screen(self):
        """Екран входу в систему"""
        screen = QWidget()
        screen.setStyleSheet("background-color: #000000;")
        
        layout = QVBoxLayout(screen)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Верхня панель
        top_panel = self.create_launcher_top_panel("◢ SYSTEM AUTHENTICATION")
        layout.addWidget(top_panel)
        
        # Центральна область входу
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(100, 50, 100, 50)
        center_layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("◢ ENTER CREDENTIALS")
        title_style = get_lcars_font_style(32, 'bold')
        title.setStyleSheet(f"""
            color: {get_random_button_color(LCARSEra.LCARS_25TH)};
            {title_style}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(title)
        
        # Поля входу
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Username
        username_label = QLabel("◢ USERNAME:")
        username_style = get_lcars_font_style(16, 'bold')
        username_label.setStyleSheet(f"""
            color: {get_random_button_color(LCARSEra.LCARS_25TH)};
            {username_style}
        """)
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setFixedHeight(40)
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {get_random_button_color(LCARSEra.LCARS_25TH)};
                color: #000000;
                border: 2px solid {get_random_button_color(LCARSEra.LCARS_25TH)};
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        self.username_input.setPlaceholderText("COMMANDER")
        form_layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("◢ PASSWORD:")
        password_label.setStyleSheet(f"""
            color: {get_random_button_color(LCARSEra.LCARS_25TH)};
            {username_style}
        """)
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setFixedHeight(40)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {get_random_button_color(LCARSEra.LCARS_25TH)};
                color: #000000;
                border: 2px solid {get_random_button_color(LCARSEra.LCARS_25TH)};
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        self.password_input.setPlaceholderText("••••••••")
        form_layout.addWidget(self.password_input)
        
        center_layout.addLayout(form_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        login_btn = LCARSButton("◢ LOGIN", get_random_button_color(LCARSEra.LCARS_25TH), "wide")
        login_btn.clicked.connect(self.authenticate)
        button_layout.addWidget(login_btn)
        
        back_btn = LCARSButton("◄ BACK", get_random_button_color(LCARSEra.LCARS_25TH), "wide")
        back_btn.clicked.connect(self.go_to_faction)
        button_layout.addWidget(back_btn)
        
        center_layout.addLayout(button_layout)
        center_layout.addStretch()
        
        layout.addWidget(center_widget)
        
        # Нижня панель
        bottom_panel = self.create_launcher_bottom_panel()
        layout.addWidget(bottom_panel)
        
        return screen
    
    def create_lock_screen(self):
        """Екран блокування"""
        screen = QWidget()
        screen.setStyleSheet("background-color: #000000;")
        
        layout = QVBoxLayout(screen)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Верхня панель
        top_panel = self.create_launcher_top_panel("◢ SYSTEM LOCKED")
        layout.addWidget(top_panel)
        
        # Центральна область
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(100, 50, 100, 50)
        center_layout.setSpacing(30)
        
        # Заголовок
        title = QLabel("◢ SYSTEM LOCKED")
        title_style = get_lcars_font_style(36, 'bold')
        title.setStyleSheet(f"""
            color: {get_random_button_color(LCARSEra.LCARS_25TH)};
            {title_style}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(title)
        
        # Час
        self.lock_time_label = QLabel("00:00:00")
        time_style = get_lcars_font_style(48, 'bold')
        self.lock_time_label.setStyleSheet(f"""
            color: {get_random_button_color(LCARSEra.LCARS_25TH)};
            {time_style}
        """)
        self.lock_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.lock_time_label)
        
        # Дата
        self.lock_date_label = QLabel("STARDATE 2402.123")
        date_style = get_lcars_font_style(18, 'bold')
        self.lock_date_label.setStyleSheet(f"""
            color: {get_random_button_color(LCARSEra.LCARS_25TH)};
            {date_style}
        """)
        self.lock_date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.lock_date_label)
        
        # Кнопка розблокування
        unlock_btn = LCARSButton("◢ UNLOCK", get_random_button_color(LCARSEra.LCARS_25TH), "wide")
        unlock_btn.clicked.connect(self.go_to_login)
        center_layout.addWidget(unlock_btn)
        
        center_layout.addStretch()
        
        layout.addWidget(center_widget)
        
        # Нижня панель
        bottom_panel = self.create_launcher_bottom_panel()
        layout.addWidget(bottom_panel)
        
        return screen
    
    def create_launcher_top_panel(self, title_text):
        """Верхня панель лаунчера"""
        panel = QWidget()
        panel.setFixedHeight(100)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Лівий кутовий елемент
        left_color = get_random_button_color(LCARSEra.LCARS_25TH)
        left_corner = QFrame()
        left_corner.setFixedSize(300, 100)
        left_corner.setStyleSheet(f"""
            QFrame {{
                background-color: {left_color};
                border-top-left-radius: 50px;
                border-bottom-left-radius: 30px;
            }}
        """)
        layout.addWidget(left_corner)
        
        # Центральна область заголовка
        title_area = QWidget()
        title_layout = QHBoxLayout(title_area)
        title_layout.setContentsMargins(30, 0, 30, 0)
        
        title = QLabel(title_text)
        title_style = get_lcars_font_style(28, 'bold')
        title.setStyleSheet(f"""
            color: {get_random_button_color(LCARSEra.LCARS_25TH)};
            {title_style}
        """)
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        # Годинник
        self.launcher_clock = QLabel("00:00:00")
        clock_style = get_lcars_font_style(20, 'bold')
        self.launcher_clock.setStyleSheet(f"""
            color: {get_random_button_color(LCARSEra.LCARS_25TH)};
            {clock_style}
        """)
        title_layout.addWidget(self.launcher_clock)
        
        layout.addWidget(title_area, 1)
        
        # Правий кутовий елемент
        right_color = get_random_button_color(LCARSEra.LCARS_25TH)
        right_corner = QFrame()
        right_corner.setFixedSize(250, 100)
        right_corner.setStyleSheet(f"""
            QFrame {{
                background-color: {right_color};
                border-top-right-radius: 50px;
                border-bottom-right-radius: 30px;
            }}
        """)
        layout.addWidget(right_corner)
        
        return panel
    
    def create_faction_panel(self):
        """Панель вибору фракції"""
        panel = QFrame()
        panel.setFixedWidth(350)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {get_random_button_color(LCARSEra.LCARS_25TH)};
                border-radius: 20px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("◢ FACTION")
        title_style = get_lcars_font_style(20, 'bold')
        title.setStyleSheet(f"""
            color: #000000;
            {title_style}
        """)
        layout.addWidget(title)
        
        # Кнопки фракцій
        factions = ["FEDERATION", "KLINGON", "ROMULAN", "BORG"]
        self.faction_buttons = []
        
        for faction in factions:
            color = get_random_button_color(LCARSEra.LCARS_25TH)
            btn = LCARSButton(faction, color, "rect")
            btn.clicked.connect(lambda checked, f=faction: self.select_faction(f))
            layout.addWidget(btn)
            self.faction_buttons.append(btn)
        
        layout.addStretch()
        return panel
    
    def create_era_panel(self):
        """Панель вибору епохи"""
        panel = QFrame()
        panel.setFixedWidth(350)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {get_random_button_color(LCARSEra.LCARS_25TH)};
                border-radius: 20px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("◢ ERA")
        title_style = get_lcars_font_style(20, 'bold')
        title.setStyleSheet(f"""
            color: #000000;
            {title_style}
        """)
        layout.addWidget(title)
        
        # Кнопки епох
        eras = ["22nd CENTURY", "23rd CENTURY", "24th CENTURY", "25th CENTURY"]
        self.era_buttons = []
        
        for era in eras:
            color = get_random_button_color(LCARSEra.LCARS_25TH)
            btn = LCARSButton(era, color, "rect")
            btn.clicked.connect(lambda checked, e=era: self.select_era(e))
            layout.addWidget(btn)
            self.era_buttons.append(btn)
        
        layout.addStretch()
        return panel
    
    def create_launch_panel(self):
        """Панель запуску"""
        panel = QFrame()
        panel.setFixedWidth(300)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {get_random_button_color(LCARSEra.LCARS_25TH)};
                border-radius: 20px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        title = QLabel("◢ LAUNCH")
        title_style = get_lcars_font_style(20, 'bold')
        title.setStyleSheet(f"""
            color: #000000;
            {title_style}
        """)
        layout.addWidget(title)
        
        # Вибрані параметри
        self.selected_faction_label = QLabel("Faction: None")
        self.selected_era_label = QLabel("Era: None")
        
        param_style = get_lcars_font_style(14, 'bold')
        for label in [self.selected_faction_label, self.selected_era_label]:
            label.setStyleSheet(f"""
                color: #000000;
                {param_style}
            """)
        
        layout.addWidget(self.selected_faction_label)
        layout.addWidget(self.selected_era_label)
        
        layout.addStretch()
        
        # Кнопка запуску
        self.launch_btn = LCARSButton("◢ LAUNCH", get_random_button_color(LCARSEra.LCARS_25TH), "tall")
        self.launch_btn.clicked.connect(self.proceed_to_login)
        layout.addWidget(self.launch_btn)
        
        return panel
    
    def create_launcher_bottom_panel(self):
        """Нижня панель лаунчера"""
        panel = QWidget()
        panel.setFixedHeight(80)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Лівий кутовий елемент
        left_color = get_random_button_color(LCARSEra.LCARS_25TH)
        left_corner = QFrame()
        left_corner.setFixedSize(300, 80)
        left_corner.setStyleSheet(f"""
            QFrame {{
                background-color: {left_color};
                border-bottom-left-radius: 40px;
                border-top-left-radius: 20px;
            }}
        """)
        layout.addWidget(left_corner)
        
        # Центральна область статусу
        status_area = QWidget()
        status_layout = QHBoxLayout(status_area)
        status_layout.setContentsMargins(30, 0, 30, 0)
        
        status = QLabel("◢ LAUNCHER READY // SELECT CONFIGURATION")
        status_style = get_lcars_font_style(16, 'bold')
        status.setStyleSheet(f"""
            color: {get_random_button_color(LCARSEra.LCARS_25TH)};
            {status_style}
        """)
        status_layout.addWidget(status)
        
        status_layout.addStretch()
        
        # Інформація
        info = QLabel("LCARS v25.2.2026")
        info_style = get_lcars_font_style(14, 'normal')
        info.setStyleSheet(f"""
            color: {get_random_button_color(LCARSEra.LCARS_25TH)};
            {info_style}
        """)
        status_layout.addWidget(info)
        
        layout.addWidget(status_area, 1)
        
        # Правий кутовий елемент
        right_color = get_random_button_color(LCARSEra.LCARS_25TH)
        right_corner = QFrame()
        right_corner.setFixedSize(250, 80)
        right_corner.setStyleSheet(f"""
            QFrame {{
                background-color: {right_color};
                border-bottom-right-radius: 40px;
                border-top-right-radius: 20px;
            }}
        """)
        layout.addWidget(right_corner)
        
        return panel
    
    def select_faction(self, faction):
        """Вибір фракції"""
        self.selected_faction = faction
        self.selected_faction_label.setText(f"Faction: {faction}")
        
        # Оновлення стилів кнопок
        for btn in self.faction_buttons:
            if btn.text() == faction:
                btn.setStyleSheet(btn.styleSheet().replace("background-color:", "background-color: #00FF00;"))
            else:
                btn.setStyleSheet(btn.styleSheet().replace("#00FF00", btn.dynamic_color))
    
    def select_era(self, era):
        """Вибір епохи"""
        self.selected_era = era
        self.selected_era_label.setText(f"Era: {era}")
        
        # Оновлення стилів кнопок
        for btn in self.era_buttons:
            if btn.text() == era:
                btn.setStyleSheet(btn.styleSheet().replace("background-color:", "background-color: #00FF00;"))
            else:
                btn.setStyleSheet(btn.styleSheet().replace("#00FF00", btn.dynamic_color))
    
    def proceed_to_login(self):
        """Перехід до екрану входу"""
        if hasattr(self, 'selected_faction') and hasattr(self, 'selected_era'):
            self.stack.setCurrentWidget(self.login_screen)
    
    def authenticate(self):
        """Автентифікація"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        # Проста автентифікація (в реальності тут буде перевірка)
        if username and password:
            self.login_success.emit()
        else:
            # Показати помилку
            self.password_input.setStyleSheet(self.password_input.styleSheet().replace(
                "border: 2px solid", "border: 2px solid #FF0000"
            ))
    
    def show_desktop(self):
        """Показати десктоп"""
        self.desktop_requested.emit()
    
    def launch_desktop(self):
        """Запуск десктопу"""
        if True:
            from lcars.ui.desktop import LCARSDesktop
            self.desktop = LCARSDesktop()
            self.desktop.show()
            self.close()
        if False: # Removed except block
            print(f"Failed to launch desktop: {e}")
    
    def go_to_faction(self):
        """Повернення до вибору фракції"""
        self.stack.setCurrentWidget(self.faction_screen)
    
    def go_to_login(self):
        """Перехід до екрану входу"""
        self.stack.setCurrentWidget(self.login_screen)
    
    def update_clock(self):
        """Оновлення годинника"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        
        if hasattr(self, 'launcher_clock'):
            self.launcher_clock.setText(time_str)
        
        if hasattr(self, 'lock_time_label'):
            self.lock_time_label.setText(time_str)
        
        # Зіркова дата
        year_offset = now.year - 2026
        day_of_year = now.timetuple().tm_yday
        fraction = day_of_year / 365.25
        stardate = f"STARDATE {2400 + year_offset + fraction:.3f}"
        
        if hasattr(self, 'lock_date_label'):
            self.lock_date_label.setText(stardate)


def main():
    """Запуск LCARS лаунчера"""
    app = QApplication(sys.argv)
    
    # Темна тема
    app.setStyleSheet("""
        QMainWindow {
            background-color: #000000;
        }
        QWidget {
            background-color: #000000;
            color: #FFFFFF;
        }
    """)
    
    # Створення лаунчера
    launcher = LCARSLauncher()
    
    # Показуємо вікно
    launcher.show()
    
    # Виводимо інформацію для дебагу
    print("LCARS Launcher started successfully")
    print(f"Window visible: {launcher.isVisible()}")
    print(f"Window geometry: {launcher.geometry()}")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
