"""
LCARS Central Command - 25th Century Style
Справжній 25th Century LCARS з віджетами, без нових вікон
"""

# Titanium Bridge Migration: import sys
import platform
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QGridLayout,
                           QTextEdit, QMessageBox, QStackedWidget, QFrame, QLineEdit)
from PyQt6.QtCore import Qt, QTimer, QProcess, QProcessEnvironment, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen

# Add project root
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import lcars.themes.lcars_palette as palette_module
from lcars.themes.lcars_palette import LCARSEra, get_era_palette

class LCARSButton(QPushButton):
    """Справжня LCARS кнопка 25th Century"""
    def __init__(self, text, color, text_color="black", parent=None):
        super().__init__(text, parent)
        self.color = color
        self.text_color = text_color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: none;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color)};
            }}
        """)
    
    def _lighten_color(self, color):
        """Зробити колір світлішим"""
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = min(255, r + 30)
            g = min(255, g + 30)
            b = min(255, b + 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
    
    def _darken_color(self, color):
        """Зробити колір темнішим"""
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = max(0, r - 30)
            g = max(0, g - 30)
            b = max(0, b - 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color

class LCARSPanel(QWidget):
    """LCARS панель з закругленими кутами"""
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border: none;
            }}
        """)
    
    def paintEvent(self, event):
        """Малюємо закруглені кути"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Закруглені кути
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 20, 20)

class SystemMonitorWidget(QWidget):
    """Віджет системного монітору"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("SYSTEM MONITOR")
        title.setStyleSheet("color: #37A6D1; font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Інформація
        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setMaximumHeight(120)
        self.info.setStyleSheet("""
            background-color: rgba(0,0,0,0.7);
            color: #37A6D1;
            border: none;
            font-family: 'Courier New';
            font-size: 10px;
            padding: 5px;
        """)
        layout.addWidget(self.info)
        
        # Оновлення
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.timer.start(2000)
        self.update_info()
    
    def update_info(self):
        """Оновити інформацію"""
        if True:
            import psutil
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:').percent
            
            info_text = f"""CPU Usage: {cpu}%
Memory: {memory}%
Disk: {disk}%
Platform: {platform.system()}
Python: {platform.python_version()}

Uptime: {datetime.now().strftime('%H:%M:%S')}"""
            
            self.info.setPlainText(info_text)
        if False: # Removed except block
            self.info.setPlainText(f"""Platform: {platform.system()}
Python: {platform.python_version()}

Time: {datetime.now().strftime('%H:%M:%S')}""")

class TelemetryWidget(QWidget):
    """Віджет телеметрії"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("TELEMETRY")
        title.setStyleSheet("color: #E7442A; font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Дані телеметрії
        self.telemetry = QTextEdit()
        self.telemetry.setReadOnly(True)
        self.telemetry.setMaximumHeight(100)
        self.telemetry.setStyleSheet("""
            background-color: rgba(0,0,0,0.7);
            color: #E7442A;
            border: none;
            font-family: 'Courier New';
            font-size: 10px;
            padding: 5px;
        """)
        layout.addWidget(self.telemetry)
        
        # Оновлення
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_telemetry)
        self.timer.start(1000)
        self.update_telemetry()
    
    def update_telemetry(self):
        """Оновити телеметрію"""
        telemetry_data = f"""STARDATE: {datetime.now().strftime('%Y.%m.%d')}
TIME: {datetime.now().strftime('%H:%M:%S')}
STATUS: OPERATIONAL
POWER: 100%
SHIELDS: 100%
WEAPONS: ONLINE
WARP: STANDBY

SYSTEMS: NOMINAL"""
        
        self.telemetry.setPlainText(telemetry_data)

class ConsoleWidget(QWidget):
    """Консоль віджет"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("CONSOLE")
        title.setStyleSheet("color: #9EA5BA; font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Консоль
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(150)
        self.console.setStyleSheet("""
            background-color: rgba(0,0,0,0.7);
            color: #9EA5BA;
            border: none;
            font-family: 'Courier New';
            font-size: 10px;
            padding: 5px;
        """)
        layout.addWidget(self.console)
        
        # Ввід команди
        input_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setStyleSheet("""
            background-color: rgba(0,0,0,0.7);
            color: #9EA5BA;
            border: 1px solid #9EA5BA;
            font-family: 'Courier New';
            font-size: 10px;
            padding: 3px;
        """)
        self.command_input.returnPressed.connect(self.execute_command)
        input_layout.addWidget(QLabel("CMD:"))
        input_layout.addWidget(self.command_input)
        layout.addLayout(input_layout)
        
        self.log_message("LCARS Console initialized")
    
    def execute_command(self):
        """Виконати команду"""
        command = self.command_input.text().strip()
        if command:
            self.log_message(f"> {command}")
            
            # Прості команди
            if command.lower() == "help":
                self.log_message("Available commands: help, status, clear, time")
            elif command.lower() == "status":
                self.log_message("All systems operational")
            elif command.lower() == "clear":
                self.console.clear()
            elif command.lower() == "time":
                self.log_message(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
            else:
                self.log_message(f"Unknown command: {command}")
            
            self.command_input.clear()
    
    def log_message(self, message):
        """Додати повідомлення до консолі"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{timestamp}] {message}")

class ApplicationsWidget(QWidget):
    """Віджет додатків"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.running_processes = {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("APPLICATIONS")
        title.setStyleSheet("color: #FF6753; font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Кнопки додатків
        apps_layout = QGridLayout()
        
        applications = [
            ("CONSTRUCTOR", "constructor.py", "#FF6753"),
            ("SYSTEM MONITOR", "system_monitor.py", "#37A6D1"),
            ("HEALTH CHECK", "health_check.py", "#1C3C55"),
            ("CONSOLE", "console.py", "#9EA5BA")
        ]
        
        for i, (name, file, color) in enumerate(applications):
            row = i // 2
            col = (i % 2) * 2
            
            # Кнопка запуску
            btn = LCARSButton(name, color)
            btn.clicked.connect(lambda checked, f=file, b=btn: self.toggle_app(f, b))
            apps_layout.addWidget(btn, row, col)
        
        layout.addLayout(apps_layout)
        
        # Статус запущених процесів
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        self.status.setMaximumHeight(80)
        self.status.setStyleSheet("""
            background-color: rgba(0,0,0,0.7);
            color: #FF6753;
            border: none;
            font-family: 'Courier New';
            font-size: 10px;
            padding: 5px;
        """)
        layout.addWidget(self.status)
    
    def toggle_app(self, filename, button):
        """Перемкнути додаток"""
        if filename in self.running_processes:
            process = self.running_processes[filename]
            if process.state() == QProcess.ProcessState.Running:
                process.terminate()
                button.setText(filename.split('.')[0].upper())
                self.log_message(f"Stopped {filename}")
        else:
            self.log_message(f"Launching {filename}...")
            process = QProcess(self)
            env = QProcessEnvironment.systemEnvironment()
            env.insert("PYTHONPATH", project_root)
            process.setProcessEnvironment(env)
            
            full_path = str(Path(project_root) / filename)
            process.start(sys.executable, [full_path])
            
            self.running_processes[filename] = process
            button.setText("STOP")
    
    def log_message(self, message):
        """Лог повідомлення"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status.append(f"[{timestamp}] {message}")

class LCARSCentralCommand(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Central Command - 25th Century")
        self.showFullScreen()
        
        # 25th Century палітра
        self.current_era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.current_era)
        
        # Справжній 25th Century стиль
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text']};
                font-family: 'Arial', sans-serif;
            }}
        """)
        
        # Головний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основний layout
        main_layout = QHBoxLayout(central_widget)
        
        # Ліва панель (системна інформація)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Центральна панель (консоль та телеметрія)
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 2)
        
        # Права панель (додатки)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        # Таймер оновлення
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        # ESC для виходу
        from PyQt6.QtGui import QShortcut, QKeySequence
        self.esc_shortcut = QShortcut(QKeySequence("ESC"), self)
        self.esc_shortcut.activated.connect(self.close)
    
    def create_left_panel(self):
        """Створити ліву панель"""
        panel = LCARSPanel(self.colors['button_colors'][0])
        layout = QVBoxLayout(panel)
        
        # Заголовок
        title = QLabel("◢ LCARS 25TH")
        title.setStyleSheet(f"""
            color: black;
            background-color: {self.colors['button_colors'][1]};
            font-size: 24px;
            font-weight: bold;
            padding: 15px;
            border: none;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Час
        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"""
            color: {self.colors['button_colors'][2]};
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
        """)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)
        
        # Системний монітор
        self.system_monitor = SystemMonitorWidget()
        layout.addWidget(self.system_monitor)
        
        layout.addStretch()
        return panel
    
    def create_center_panel(self):
        """Створити центральну панель"""
        panel = LCARSPanel(self.colors['button_colors'][3])
        layout = QVBoxLayout(panel)
        
        # Консоль
        self.console = ConsoleWidget()
        layout.addWidget(self.console)
        
        # Телеметрія
        self.telemetry = TelemetryWidget()
        layout.addWidget(self.telemetry)
        
        return panel
    
    def create_right_panel(self):
        """Створити праву панель"""
        panel = LCARSPanel(self.colors['button_colors'][4])
        layout = QVBoxLayout(panel)
        
        # Додатки
        self.applications = ApplicationsWidget(self)
        layout.addWidget(self.applications)
        
        # Кнопки епох
        era_group = QWidget()
        era_layout = QVBoxLayout(era_group)
        
        era_title = QLabel("ERA SELECTOR")
        era_title.setStyleSheet("color: #E7442A; font-weight: bold; font-size: 14px;")
        era_layout.addWidget(era_title)
        
        for era in LCARSEra:
            btn = LCARSButton(era.value, self.colors['button_colors'][5])
            btn.clicked.connect(lambda checked, e=era: self.change_era(e))
            era_layout.addWidget(btn)
        
        layout.addWidget(era_group)
        layout.addStretch()
        return panel
    
    def change_era(self, era):
        """Змінити епоху"""
        self.current_era = era
        self.colors = get_era_palette(era)
        
        # Оновити стиль
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text']};
                font-family: 'Arial', sans-serif;
            }}
        """)
        
        self.console.log_message(f"Switched to {era.value} era")
    
    def update_time(self):
        """Оновити час"""
        self.time_label.setText(datetime.now().strftime("STARDATE %Y.%m.%d\n%H:%M:%S"))

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = LCARSCentralCommand()
    window.show()
    
    print("🖖 LCARS Central Command - 25th Century launched!")
    print("🚀 All systems operational")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
