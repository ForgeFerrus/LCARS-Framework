#!/usr/bin/env python3
"""
LCARS Programs Launcher
Центральний запускач всіх програм LCARS
"""

import subprocess
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QTextEdit, QGroupBox,
    QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon

# Add project root to path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.theme.palette import LCARSEra, FactionEra, get_theme as get_era_palette, get_lcars_font_style

class ProgramsLauncher(QMainWindow):
    """Центральний запускач програм LCARS"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS PROGRAMS")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply LCARS styling
        self.setup_lcars_style()
        self.setup_ui()
        
        # Define available programs
        self.setup_programs()
        
    def setup_lcars_style(self):
        """Застосувати LCARS стилі"""
        theme = get_era_palette(LCARSEra.LCARS_25TH)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme.get('background', '#000000')};
                color: {theme.get('text', '#FF9900')};
                font-family: "Swiss 911 BT", "Arial", sans-serif;
            }}
            QListWidget {{
                background-color: {theme.get('panel', '#1a1a1a')};
                border: 2px solid {theme.get('accent', '#FF9900')};
                color: {theme.get('text', '#FFFFFF')};
                padding: 10px;
                font-size: 14px;
            }}
            QTextEdit {{
                background-color: {theme.get('panel', '#1a1a1a')};
                border: 2px solid {theme.get('accent', '#FF9900')};
                color: {theme.get('text', '#FFFFFF')};
                font-family: "Consolas", monospace;
            }}
            QPushButton {{
                background-color: {theme.get('button', '#666666')};
                color: {theme.get('text', '#FFFFFF')};
                border: 2px solid {theme.get('accent', '#FF9900')};
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {theme.get('accent', '#FF9900')};
                color: {theme.get('background', '#000000')};
            }}
            QPushButton:disabled {{
                background-color: {theme.get('disabled', '#333333')};
                color: {theme.get('text_secondary', '#888888')};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme.get('accent', '#FF9900')};
                margin-top: 15px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                font-size: 16px;
            }}
        """)
        
    def setup_ui(self):
        """Налаштувати інтерфейс"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_group = QGroupBox("LCARS ENTERPRISE SYSTEMS")
        header_layout = QVBoxLayout(header_group)
        
        header_label = QLabel("SELECT PROGRAM TO LAUNCH")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF9900;")
        header_layout.addWidget(header_label)
        
        main_layout.addWidget(header_group)
        
        # Content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Programs list
        left_panel = self.create_programs_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Program info and controls
        right_panel = self.create_info_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 800])
        main_layout.addWidget(splitter)
        
        # Status bar
        status_group = QGroupBox("SYSTEM STATUS")
        status_layout = QHBoxLayout(status_group)
        
        self.status_label = QLabel("All systems operational")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.time_label = QLabel()
        status_layout.addWidget(self.time_label)
        
        main_layout.addWidget(status_group)
        
        # Setup timer for time display
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()
        
    def create_programs_panel(self):
        """Створити панель програм"""
        panel = QGroupBox("AVAILABLE PROGRAMS")
        layout = QVBoxLayout(panel)
        
        # Programs list
        self.programs_list = QListWidget()
        self.programs_list.itemSelectionChanged.connect(self.on_program_selected)
        layout.addWidget(self.programs_list)
        
        return panel
        
    def create_info_panel(self):
        """Створити інформаційну панель"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Program info
        info_group = QGroupBox("PROGRAM INFORMATION")
        info_layout = QVBoxLayout(info_group)
        
        self.program_info = QTextEdit()
        self.program_info.setReadOnly(True)
        self.program_info.setMaximumHeight(200)
        info_layout.addWidget(self.program_info)
        
        layout.addWidget(info_group)
        
        # Launch controls
        controls_group = QGroupBox("LAUNCH CONTROLS")
        controls_layout = QVBoxLayout(controls_group)
        
        self.launch_btn = QPushButton("LAUNCH PROGRAM")
        self.launch_btn.clicked.connect(self.launch_program)
        self.launch_btn.setEnabled(False)
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #00CC00;
                font-size: 16px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #00FF00;
            }
        """)
        controls_layout.addWidget(self.launch_btn)
        
        layout.addWidget(controls_group)
        
        # Quick actions
        actions_group = QGroupBox("QUICK ACTIONS")
        actions_layout = QHBoxLayout(actions_group)
        
        self.refresh_btn = QPushButton("REFRESH")
        self.refresh_btn.clicked.connect(self.refresh_programs)
        actions_layout.addWidget(self.refresh_btn)
        
        self.settings_btn = QPushButton("SETTINGS")
        self.settings_btn.clicked.connect(self.open_settings)
        actions_layout.addWidget(self.settings_btn)
        
        self.help_btn = QPushButton("HELP")
        self.help_btn.clicked.connect(self.show_help)
        actions_layout.addWidget(self.help_btn)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        return panel
        
    def setup_programs(self):
        """Налаштувати список програм"""
        self.programs = {
            "English Learning": {
                "file": "english_learning/app.py",
                "description": "25th Century English Learning Kiosk with Tenses, Vocabulary and Tests",
                "category": "Education",
                "icon": "📚",
                "dependencies": ["PyQt6", "PyQt6-WebEngine", "sqlite3"],
                "status": "Ready"
            },
            "Geant4 Control": {
                "file": "geant4/launcher.py",
                "module": "lcars.programs.geant4.launcher",
                "function": "run",
                "description": "Geant4 симуляції та управління науковими розрахунками",
                "category": "Science",
                "icon": "🧪",
                "dependencies": ["PyQt6", "numpy", "matplotlib"],
                "status": "Ready"
            },
            "File Manager": {
                "file": "file_manager.py", 
                "description": "Базовий файловий менеджер для роботи з документами та проектами",
                "category": "System",
                "icon": "🗂️",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Total Commander": {
                "file": "total_commander.py", 
                "description": "Повноцінний двопанельний менеджер файлів. Наступник застарілої системи.",
                "category": "System",
                "icon": "📁",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "AI Assistant": {
                "file": "Copilot.py",
                "description": "LCARS Copilot - AI Development Assistant with 25th Era styling",
                "category": "Development",
                "icon": "🤖",
                "dependencies": ["PyQt6", "sqlite3"],
                "status": "Ready"
            },
            "Network Browser": {
                "file": "network_browser.py",
                "description": "Простий текстовий веб-браузер для базових сторінок",
                "category": "Network",
                "icon": "🌐",
                "dependencies": ["PyQt6", "requests"],
                "status": "Ready"
            },
            "LCARS Web Browser": {
                "file": "lcars_web_browser.py",
                "description": "Повноцінний веб-браузер з підтримкою сучасних сайтів та Star Trek закладками",
                "category": "Network",
                "icon": "🚀",
                "dependencies": ["PyQt6", "PyQt6-WebEngine"],
                "status": "Ready"
            },
            "UI Designer": {
                "file": "../lcars/ui/tools/ui_designer.py",
                "description": "Конструктор LCARS інтерфейсів та компонентів",
                "category": "Development",
                "icon": "🎨",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "System Monitor": {
                "file": "../lcars/ui/views/monitor.py",
                "description": "Монітор системних ресурсів та проектів",
                "category": "System",
                "icon": "📊",
                "dependencies": ["PyQt6", "psutil"],
                "status": "Ready"
            },
            "LCARS Terminal": {
                "file": "../lcars/ui/terminal.py",
                "description": "Термінал для виконання команд та скриптів",
                "category": "System",
                "icon": "💻",
                "dependencies": ["PyQt6"],
                "status": "Issues"
            },
            "Console Monitor": {
                "file": "../simple_monitor.py",
                "description": "Текстовий монітор системних ресурсів",
                "category": "System",
                "icon": "📈",
                "dependencies": ["psutil"],
                "status": "Ready"
            },
            "Notes": {
                "file": "notebook.py",
                "description": "Простий блокнот для збереження нотаток",
                "category": "Utility",
                "icon": "📝",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Logger": {
                "file": "logger_app.py",
                "description": "Записник/журнали системних подій",
                "category": "Utility",
                "icon": "📓",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "SMS Client": {
                "file": "sms_client.py",
                "description": "Клієнт для внутрішніх SMS-чатів",
                "category": "Communication",
                "icon": "💬",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Email Client": {
                "file": "email_client.py",
                "description": "Програма для внутрішньої пошти",
                "category": "Communication",
                "icon": "✉️",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Phone": {
                "file": "phone.py",
                "description": "Телефон / VoIP клієнт",
                "category": "Communication",
                "icon": "📞",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Messenger (Facebook)": {
                "file": "messenger_facebook.py",
                "description": "Підхід Фейсбук-подібних чатів",
                "category": "Communication",
                "icon": "📘",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Messenger (Telegram)": {
                "file": "messenger_telegram.py",
                "description": "Telegram-подібний месенджер",
                "category": "Communication",
                "icon": "📲",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Messenger (Viber)": {
                "file": "messenger_viber.py",
                "description": "Viber-подібний чат",
                "category": "Communication",
                "icon": "💜",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Messenger (WhatsApp)": {
                "file": "messenger_whatsapp.py",
                "description": "WhatsApp-подібний чат",
                "category": "Communication",
                "icon": "🟢",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Network Apps": {
                "file": "network_apps.py",
                "description": "Колекція мережевих програм",
                "category": "Network",
                "icon": "🕸️",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "GPS": {
                "file": "gps.py",
                "description": "Модуль GPS позиціювання",
                "category": "Navigation",
                "icon": "📡",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Maps": {
                "file": "maps.py",
                "description": "Переглядач зіркових карт",
                "category": "Navigation",
                "icon": "🗺️",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Weather": {
                "file": "weather.py",
                "description": "Астро-погода",
                "category": "Navigation",
                "icon": "☁️",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Astro Nav": {
                "file": "astro_nav.py",
                "description": "Астронвігація та зоряне картографування",
                "category": "Navigation",
                "icon": "🌌",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Laboratory": {
                "file": "lab_manager.py",
                "description": "Управління лабораторією",
                "category": "Utility",
                "icon": "⚗️",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Physical Modules": {
                "file": "physical_modules.py",
                "description": "Інтерфейс фізичних модулів",
                "category": "Utility",
                "icon": "🔧",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Wi-Fi Scanner": {
                "file": "wifi_scanner.py",
                "description": "Сканер беспроводних мереж",
                "category": "Network",
                "icon": "📶",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            },
            "Cortex Agent": {
                "file": "cortex_agent.py",
                "description": "Віджет AI-агента Cortex",
                "category": "Utility",
                "icon": "🤖",
                "dependencies": ["PyQt6"],
                "status": "Ready"
            }
        }
        
        self.refresh_programs()
        
    def refresh_programs(self):
        """Оновити список програм"""
        self.programs_list.clear()
        
        for name, info in self.programs.items():
            status_icon = "✅" if info["status"] == "Ready" else "⚠️"
            item_text = f"{status_icon} {info['icon']} {name}"
            
            item = self.programs_list.addItem(item_text)
            # Get the actual item and set data
            item_widget = self.programs_list.item(self.programs_list.count() - 1)
            item_widget.setData(Qt.ItemDataRole.UserRole, info)
            
    def on_program_selected(self):
        """Обробити вибір програми"""
        current_item = self.programs_list.currentItem()
        if not current_item:
            return
            
        program = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Update program info
        info_text = f"PROGRAM: {program['icon']} {current_item.text().split(' ', 2)[-1]}\n\n"
        info_text += f"Category: {program['category']}\n"
        info_text += f"Status: {program['status']}\n"
        info_text += f"Dependencies: {', '.join(program['dependencies'])}\n\n"
        info_text += f"Description:\n{program['description']}"
        
        self.program_info.setText(info_text)
        
        # Enable launch button
        self.launch_btn.setEnabled(program['status'] == "Ready")
        
    def launch_program(self):
        """Запустити обрану програму"""
        current_item = self.programs_list.currentItem()
        if not current_item:
            return
            
        program = current_item.data(Qt.ItemDataRole.UserRole)
        program_file = program['file']
        program_name = current_item.text().split(' ', 2)[-1]
        
        try:
            self.status_label.setText(f"Launching {program_name}...")
            
            # Check if program has module import
            if 'module' in program and 'function' in program:
                # Import module and call function
                module_path = program['module']
                function_name = program['function']
                
                # Dynamic import
                parts = module_path.split('.')
                module = __import__(parts[0])
                for part in parts[1:]:
                    module = getattr(module, part)
                
                # Call the function
                launch_func = getattr(module, function_name)
                launch_func()
                
            else:
                # Launch as separate process
                cmd = [sys.executable, str(Path(__file__).parent / program_file)]
                subprocess.Popen(cmd, cwd=str(Path(__file__).parent))
            
            self.status_label.setText(f"{program_name} launched successfully")
            QMessageBox.information(self, "Launch Success", f"{program_name} has been launched")
            
        except Exception as e:
            self.status_label.setText(f"Failed to launch {program_name}")
            QMessageBox.critical(self, "Launch Error", f"Failed to launch {program_name}:\n{str(e)}")
            
    def open_settings(self):
        """Відкрити налаштування"""
        QMessageBox.information(self, "Settings", "Settings panel would open here")
        
    def show_help(self):
        """Показати довідку"""
        help_text = """
LCARS Programs Launcher Help

This launcher provides access to all LCARS applications:

• Science Programs - Geant4 simulations and calculations
• System Programs - File management, monitoring, terminal
• Tools - AI assistant, UI designer
• Network Programs - Web browser and network tools

To launch a program:
1. Select it from the list
2. Click "LAUNCH PROGRAM"

For issues with programs, check dependencies and system requirements.
        """
        QMessageBox.information(self, "Help", help_text)
        
    def update_time(self):
        """Оновити час"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"Stardate: {current_time}")


def run_programs_launcher():
    """Запустити запускач програм"""
    app = QApplication(sys.argv)
    # Note: setup_lcars_font not available in palette.py, using default
    window = ProgramsLauncher()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_programs_launcher())

