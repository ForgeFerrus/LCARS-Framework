#!/usr/bin/env python3
"""
FULL LCARS DESKTOP - Complete Working System
Повноцінний десктоп з усім функціоналом на вашому фреймворку
"""
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QGridLayout, QSplitter, QTextEdit,
    QProgressBar, QScrollArea, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QDateTime
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter

class SystemMonitor(QThread):
    """Поток для моніторингу системи"""
    update_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        while self.running:
            # Симуляція системних даних
            import random
            data = {
                'cpu': random.randint(20, 80),
                'memory': random.randint(30, 70),
                'power': random.randint(60, 100),
                'shields': random.randint(0, 150),
                'weapons': random.randint(0, 100),
                'hull': random.randint(80, 100),
                'torpedoes': random.randint(10, 50)
            }
            self.update_signal.emit(data)
            self.msleep(1000)

class FullLCARSDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS DESKTOP - FULL SYSTEM")
        self.setGeometry(50, 50, 1600, 1000)
        
        # LCARS кольори
        self.lcars_orange = "#FF9900"
        self.lcars_purple = "#CC99CC"
        self.lcars_red = "#CC6666"
        self.lcars_blue = "#6699CC"
        self.lcars_green = "#66CC66"
        self.lcars_black = "#000000"
        self.lcars_gray = "#333333"
        
        # Стани систем
        self.weapons_online = False
        self.shields_raised = False
        self.cloak_engaged = False
        self.red_alert = False
        
        # Встановлюємо стиль
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.lcars_black};
            }}
            QFrame {{
                background-color: {self.lcars_black};
                border: 2px solid {self.lcars_orange};
                border-radius: 10px;
            }}
            QPushButton {{
                background-color: {self.lcars_gray};
                color: {self.lcars_orange};
                border: 2px solid {self.lcars_orange};
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.lcars_orange};
                color: {self.lcars_black};
            }}
            QPushButton:pressed {{
                background-color: {self.lcars_red};
            }}
            QLabel {{
                color: {self.lcars_orange};
                background-color: transparent;
                font-weight: bold;
            }}
            QProgressBar {{
                border: 2px solid {self.lcars_orange};
                border-radius: 5px;
                text-align: center;
                color: {self.lcars_orange};
                background-color: {self.lcars_gray};
            }}
            QProgressBar::chunk {{
                background-color: {self.lcars_orange};
                border-radius: 3px;
            }}
            QTextEdit {{
                background-color: {self.lcars_gray};
                color: {self.lcars_orange};
                border: 2px solid {self.lcars_orange};
                border-radius: 5px;
                font-family: 'Courier New';
            }}
            QTabWidget::pane {{
                border: 2px solid {self.lcars_orange};
                background-color: {self.lcars_black};
            }}
            QTabBar::tab {{
                background-color: {self.lcars_gray};
                color: {self.lcars_orange};
                border: 2px solid {self.lcars_orange};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {self.lcars_orange};
                color: {self.lcars_black};
            }}
        """)
        
        self.setup_ui()
        self.setup_system_monitor()
        self.setup_timer()
        
    def setup_ui(self):
        """Створення інтерфейсу"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Головний layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Верхня панель
        top_panel = self.create_top_panel()
        main_layout.addWidget(top_panel)
        
        # Основна область
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Ліва панель - системи
        systems_panel = self.create_systems_panel()
        content_splitter.addWidget(systems_panel)
        
        # Центральна панель - робоча область
        work_panel = self.create_work_panel()
        content_splitter.addWidget(work_panel)
        
        # Права панель - статус
        status_panel = self.create_status_panel()
        content_splitter.addWidget(status_panel)
        
        content_splitter.setSizes([400, 800, 400])
        main_layout.addWidget(content_splitter)
        
        # Нижня панель управління
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
    def create_top_panel(self):
        """Верхня панель"""
        panel = QFrame()
        panel.setFixedHeight(80)
        layout = QHBoxLayout(panel)
        
        # Логотип LCARS
        logo = QLabel("◤ LCARS DESKTOP")
        logo.setStyleSheet(f"""
            QLabel {{
                color: {self.lcars_orange};
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        layout.addWidget(logo)
        
        # Час
        self.time_label = QLabel("00:00:00")
        self.time_label.setStyleSheet(f"""
            QLabel {{
                color: {self.lcars_green};
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        layout.addWidget(self.time_label)
        
        # Статус системи
        self.system_status = QLabel("SYSTEM: ONLINE")
        self.system_status.setStyleSheet(f"""
            QLabel {{
                color: {self.lcars_green};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        layout.addWidget(self.system_status)
        
        layout.addStretch()
        
        return panel
        
    def create_systems_panel(self):
        """Панель систем"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Заголовок
        title = QLabel("🚀 SYSTEMS CONTROL")
        title.setStyleSheet(f"color: {self.lcars_orange}; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Системні кнопки
        systems = [
            ("🔫 WEAPONS", "weapons", self.toggle_weapons),
            ("🛡️ SHIELDS", "shields", self.toggle_shields),
            ("👻 CLOAK", "cloak", self.toggle_cloak),
            ("🚨 RED ALERT", "alert", self.toggle_red_alert),
            ("📡 COMMUNICATIONS", "comms", self.open_comms),
            ("🔧 ENGINEERING", "eng", self.open_engineering),
            ("🧬 MEDICAL", "med", self.open_medical),
            ("📚 LIBRARY", "lib", self.open_library)
        ]
        
        for name, key, func in systems:
            btn = QPushButton(name)
            btn.clicked.connect(func)
            btn.setMinimumHeight(40)
            layout.addWidget(btn)
            
        layout.addStretch()
        return panel
        
    def create_work_panel(self):
        """Робоча панель"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Таби
        tabs = QTabWidget()
        
        # Таб тактики
        tactical_tab = QWidget()
        tactical_layout = QVBoxLayout(tactical_tab)
        
        tactical_label = QLabel("🎯 TACTICAL DISPLAY")
        tactical_label.setStyleSheet(f"color: {self.lcars_orange}; font-size: 18px; font-weight: bold;")
        tactical_layout.addWidget(tactical_label)
        
        # Радарний дисплей
        radar_frame = QFrame()
        radar_frame.setFixedSize(400, 400)
        radar_layout = QVBoxLayout(radar_frame)
        
        self.radar_display = QLabel()
        self.radar_display.setFixedSize(380, 380)
        self.radar_display.setStyleSheet(f"""
            QLabel {{
                background-color: {self.lcars_gray};
                border: 2px solid {self.lcars_green};
                border-radius: 190px;
            }}
        """)
        radar_layout.addWidget(self.radar_display)
        
        tactical_layout.addWidget(radar_frame)
        
        # Кнопки тактики
        tactical_buttons = QHBoxLayout()
        
        scan_btn = QPushButton("🔍 SCAN")
        scan_btn.clicked.connect(self.scan_systems)
        tactical_buttons.addWidget(scan_btn)
        
        combat_btn = QPushButton("⚔️ COMBAT")
        combat_btn.clicked.connect(self.engage_combat)
        tactical_buttons.addWidget(combat_btn)
        
        tactical_layout.addLayout(tactical_buttons)
        tactical_layout.addStretch()
        
        tabs.addTab(tactical_tab, "Tactical")
        
        # Таб логів
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        log_label = QLabel("📋 SYSTEM LOGS")
        log_label.setStyleSheet(f"color: {self.lcars_orange}; font-size: 18px; font-weight: bold;")
        log_layout.addWidget(log_label)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(300)
        log_layout.addWidget(self.log_display)
        
        tabs.addTab(log_tab, "Logs")
        
        # Таб налаштувань
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        settings_label = QLabel("⚙️ SYSTEM SETTINGS")
        settings_label.setStyleSheet(f"color: {self.lcars_orange}; font-size: 18px; font-weight: bold;")
        settings_layout.addWidget(settings_label)
        
        # Налаштування
        settings_grid = QGridLayout()
        
        settings_labels = ["Power Level", "Shield Strength", "Weapon Status", "Cloak Device"]
        for i, label in enumerate(settings_labels):
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {self.lcars_orange};")
            settings_grid.addWidget(lbl, i, 0)
            
            progress = QProgressBar()
            progress.setValue(75)
            settings_grid.addWidget(progress, i, 1)
            
        settings_layout.addLayout(settings_grid)
        settings_layout.addStretch()
        
        tabs.addTab(settings_tab, "Settings")
        
        layout.addWidget(tabs)
        return panel
        
    def create_status_panel(self):
        """Панель статусу"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Заголовок
        title = QLabel("📊 SYSTEM STATUS")
        title.setStyleSheet(f"color: {self.lcars_orange}; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Індикатори систем
        self.status_indicators = {}
        
        indicators = [
            ("CPU", "cpu"),
            ("MEMORY", "memory"),
            ("POWER", "power"),
            ("SHIELDS", "shields"),
            ("WEAPONS", "weapons"),
            ("HULL", "hull"),
            ("TORPEDOES", "torpedoes")
        ]
        
        for name, key in indicators:
            frame = QFrame()
            frame_layout = QVBoxLayout(frame)
            
            label = QLabel(f"{name}:")
            label.setStyleSheet(f"color: {self.lcars_orange}; font-size: 12px;")
            frame_layout.addWidget(label)
            
            progress = QProgressBar()
            progress.setValue(50)
            self.status_indicators[key] = progress
            frame_layout.addWidget(progress)
            
            layout.addWidget(frame)
            
        layout.addStretch()
        return panel
        
    def create_control_panel(self):
        """Панель управління"""
        panel = QFrame()
        panel.setFixedHeight(100)
        layout = QHBoxLayout(panel)
        
        # Кнопки управління
        controls = [
            ("🚀 LAUNCH", self.launch_system),
            ("🔄 RESTART", self.restart_system),
            ("💾 SAVE", self.save_state),
            ("📁 FILES", self.open_files),
            ("🔍 SEARCH", self.search_system),
            ("🚪 EXIT", self.close)
        ]
        
        for name, func in controls:
            btn = QPushButton(name)
            btn.clicked.connect(func)
            btn.setMinimumWidth(120)
            btn.setMinimumHeight(50)
            layout.addWidget(btn)
            
        layout.addStretch()
        return panel
        
    def setup_system_monitor(self):
        """Налаштування моніторингу системи"""
        self.monitor = SystemMonitor()
        self.monitor.update_signal.connect(self.update_system_status)
        self.monitor.start()
        
    def setup_timer(self):
        """Налаштування таймера"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
    def update_time(self):
        """Оновлення часу"""
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.time_label.setText(current_time)
        
    def update_system_status(self, data):
        """Оновлення статусу систем"""
        for key, value in data.items():
            if key in self.status_indicators:
                self.status_indicators[key].setValue(value)
                
    def log_message(self, message):
        """Додавання повідомлення до логу"""
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.log_display.append(f"[{timestamp}] {message}")
        
    # ==============================================================================
    # ФУНКЦІЇ СИСТЕМИ
    # ==============================================================================
    
    def toggle_weapons(self):
        """Перемкнути зброю"""
        self.weapons_online = not self.weapons_online
        status = "ONLINE" if self.weapons_online else "OFFLINE"
        self.log_message(f"Weapons system {status}")
        
    def toggle_shields(self):
        """Перемкнути щити"""
        if self.cloak_engaged:
            self.log_message("Cannot raise shields with cloak engaged!")
            return
            
        self.shields_raised = not self.shields_raised
        status = "RAISED" if self.shields_raised else "LOWERED"
        self.log_message(f"Shields {status}")
        
    def toggle_cloak(self):
        """Перемкнути маскування"""
        if self.shields_raised:
            self.log_message("Cannot engage cloak with shields up!")
            return
            
        self.cloak_engaged = not self.cloak_engaged
        status = "ENGAGED" if self.cloak_engaged else "DISENGAGED"
        self.log_message(f"Cloaking device {status}")
        
    def toggle_red_alert(self):
        """Перемкнути червону тривогу"""
        self.red_alert = not self.red_alert
        status = "ACTIVATED" if self.red_alert else "DEACTIVATED"
        self.log_message(f"Red alert {status}")
        
        if self.red_alert:
            self.system_status.setText("SYSTEM: RED ALERT")
            self.system_status.setStyleSheet(f"color: {self.lcars_red}; font-size: 16px; font-weight: bold;")
        else:
            self.system_status.setText("SYSTEM: ONLINE")
            self.system_status.setStyleSheet(f"color: {self.lcars_green}; font-size: 16px; font-weight: bold;")
            
    def open_comms(self):
        """Відкрити комунікації"""
        self.log_message("Opening communications panel...")
        
    def open_engineering(self):
        """Відкрити інженерію"""
        self.log_message("Accessing engineering systems...")
        
    def open_medical(self):
        """Відкрити медичний"""
        self.log_message("Opening medical bay...")
        
    def open_library(self):
        """Відкрити бібліотеку"""
        self.log_message("Accessing library database...")
        
    def scan_systems(self):
        """Сканування систем"""
        self.log_message("Initiating deep space scan...")
        
    def engage_combat(self):
        """Бойовий режим"""
        self.log_message("Engaging combat mode...")
        self.weapons_online = True
        self.toggle_shields()
        
    def launch_system(self):
        """Запуск системи"""
        self.log_message("Launching LCARS systems...")
        
    def restart_system(self):
        """Перезапуск системи"""
        self.log_message("Restarting system...")
        
    def save_state(self):
        """Збереження стану"""
        self.log_message("Saving system state...")
        
    def open_files(self):
        """Відкрити файли"""
        self.log_message("Opening file manager...")
        
    def search_system(self):
        """Пошук системи"""
        self.log_message("Initiating system search...")
        
    def closeEvent(self, event):
        """Закриття програми"""
        self.monitor.running = False
        self.monitor.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Темна тема
    app.setStyle("Fusion")
    dark_palette = app.palette()
    dark_palette.setColor(dark_palette.ColorRole.Window, QColor(0, 0, 0))
    dark_palette.setColor(dark_palette.ColorRole.WindowText, QColor(255, 153, 0))
    app.setPalette(dark_palette)
    
    desktop = FullLCARSDesktop()
    desktop.show()
    
    print("🚀 Full LCARS Desktop Started")
    print("📊 All systems operational")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
