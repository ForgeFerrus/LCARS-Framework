"""
LCARS Central Command - 25th Century Standalone
Modern launcher for LCARS applications (Star Trek: Picard Style)
"""

import sys
import platform
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QGridLayout,
                           QGroupBox, QTextEdit, QMessageBox, QFrame, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, QProcess, QProcessEnvironment, QPropertyAnimation, QEasingCurve, QObject, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen, QPainterPath

# Add project root correctly
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import lcars.themes.palette as palette_module
from lcars.themes.lcars_palette import LCARSEra, get_era_palette


class SessionManager:
        def __init__(self): pass
        def get_current_user(self): return "Captain"
        def get_role(self): return "Commander"

try:
    from lcars.core.process_supervisor import ProcessSupervisor
except ImportError:
    class ProcessSupervisor(QObject):
        processOutput = pyqtSignal(str, str)
        processFinished = pyqtSignal(str)
        
        def __init__(self, project_root=None, parent=None): 
            super().__init__(parent)
            self.processes = []
            self.project_root = project_root
        def start_process(self, name, cmd): 
            import subprocess
            return subprocess.Popen(cmd)
        def get_running(self): 
            return []
        def list_processes(self):
            return []
        def terminate_all(self): 
            pass

try:
    from lcars.modules.lock_screen import LCARSLoginScreen
except ImportError:
    LCARSLoginScreen = None

class LCARSButton(QPushButton):
    """Refined 25th Century LCARS Button - Pill Shape"""
    def __init__(self, text, color, text_color="black", parent=None):
        super().__init__(text, parent)
        self._color = QColor(color)
        self._text_color = text_color
        self.setFixedHeight(45)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("border: none; background-color: transparent;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Determine Color State
        bg = self._color
        if self.isDown():
            bg = bg.darker(130)
        elif self.underMouse():
            bg = bg.lighter(120)
            
        rect = self.rect()
        path = QPainterPath()
        
        # Pill Shape (Picard Style - Fully Rounded Ends)
        radius = rect.height() / 2
        path.addRoundedRect(0, 0, rect.width(), rect.height(), radius, radius)
        
        painter.setBrush(bg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        
        # Text
        painter.setPen(QColor(self._text_color))
        # Use simple bold font, standard across modern LCARS
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Align left if wide, center if small
        if self.width() > 120:
             # Add left padding for text in wide buttons
             painter.drawText(rect.adjusted(20, 0, 0, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text())
        else:
             painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class LCARSDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS System Command")
        self.showFullScreen()
        
        # STRICTLY 25th Century Theme
        self.current_era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.current_era)
        self.bg_color = self.colors['background']
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.bg_color};
                color: #FFFFFF;
            }}
            QWidget {{
                background-color: transparent;
                color: #FFFFFF;
                border: none;
            }}
            QTextEdit {{
                background-color: rgba(20, 20, 30, 0.8);
                color: {self.colors['button_colors'][3]};
                border: none;
                font-family: 'Consolas';
                font-size: 14px;
                border-radius: 10px;
                padding: 10px;
            }}
            QScrollBar:vertical {{
                background: #000;
                width: 10px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.colors['button_colors'][0]};
                border-radius: 5px;
            }}
        """)
        
        # Process tracking
        self.running_processes = {}
        self.app_buttons = {}

        self.applications_data = [
            {'name': 'КОНСТРУКТОР', 'file': 'constructor.py', 'desc': 'Редактор Інтерфейсу'},
            {'name': 'WORKSTATION', 'file': 'lcars/ui/geant4_workstation.py', 'desc': 'Ядерна Симуляція G4'},
            {'name': 'LCARS 24TH', 'file': 'lcars/ui/LCARS_24th.py', 'desc': 'Класичний Режим'},
            {'name': 'СИСТЕМА', 'file': 'lcars/ui/system_monitor.py', 'desc': 'Моніторинг Ресурсів'},
            {'name': 'АНАЛІЗАТОР', 'file': 'lcars/ui/health_check.py', 'desc': 'Сканування Цілісності'}
        ]

        # Session
        self.session_manager = SessionManager()
        self.supervisor = ProcessSupervisor(project_root=project_root, parent=self)
        self.supervisor.processOutput.connect(lambda name, data: self.log_message(f"[{name}] {data}"))
        self.supervisor.processFinished.connect(lambda name: self.log_message(f"Процес {name} завершено"))
        
        # Main stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Create screens
        self.create_main_screen()
        
        # Start with main screen directly
        self.stack.setCurrentWidget(self.main_screen)
        
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)
        
        # Shortcuts
        from PyQt6.QtGui import QShortcut, QKeySequence
        self.esc_shortcut = QShortcut(QKeySequence("ESC"), self)
        self.esc_shortcut.activated.connect(self.close)
    
    def create_main_screen(self):
        """Create the main launcher screen with 25th Century Layout"""
        self.main_screen = QWidget()
        
        # Use a grid layout for the whole screen
        layout = QGridLayout(self.main_screen)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # --- LEFT SIDEBAR (Navigation/Header) ---
        sidebar = QFrame()
        sidebar.setFixedWidth(320)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Decorative Elbow Top (Picard Style - Angular)
        elbow_top = QFrame()
        elbow_top.setFixedHeight(120)
        elbow_top.setStyleSheet(f"""
            background-color: {self.colors['button_colors'][0]};
            border-top-left-radius: 60px;
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 60px; 
            margin-bottom: 10px;
        """)
        sidebar_layout.addWidget(elbow_top)
        
        # Title in Sidebar
        title_label = QLabel("СИСТЕМНА\nКОМАНДА")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        title_label.setStyleSheet(f"""
            color: {self.colors['button_colors'][0]}; 
            font-size: 36px; 
            font-weight: bold; 
            font-family: Impact, Arial Black;
            letter-spacing: 2px;
        """)
        sidebar_layout.addWidget(title_label)
        
        sidebar_layout.addSpacing(30)
        
        # Menu Buttons
        menu_items = [
            ("ГОЛОВНА", "#FF9900"),
            ("БІБЛІОТЕКА", "#CC6600"),
            ("НАЛАШТУВАННЯ", "#99CCFF"),
            ("ДІАГНОСТИКА", "#FFCC00")
        ]

        for text, col in menu_items:
            btn = LCARSButton(text, col, "#000")
            sidebar_layout.addWidget(btn)
            
        sidebar_layout.addStretch()
        
        # Exit Button at bottom
        exit_btn = LCARSButton("ВИХІД", "#CC0000", "#FFF")
        exit_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(exit_btn)
        
        # Add sidebar to main grid (Rows 0-2, Col 0)
        layout.addWidget(sidebar, 0, 0, 3, 1)
        
        # --- TOP HEADER BAR ---
        header_bar = QFrame()
        header_bar.setFixedHeight(50)
        header_bar.setStyleSheet(f"""
            background-color: {self.colors['button_colors'][1]};
            border-radius: 25px;
            margin-left: 20px;
        """)
        header_layout = QHBoxLayout(header_bar)
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: black; font-size: 18px; font-weight: bold; border: none;")
        header_layout.addWidget(self.time_label)
        header_layout.addStretch()
        
        user_label = QLabel(f"АВТОРИЗАЦІЯ: {platform.node()}")
        user_label.setStyleSheet("color: black; font-size: 18px; font-weight: bold; border: none;")
        header_layout.addWidget(user_label)
        
        layout.addWidget(header_bar, 0, 1)

        # --- CENTRAL APP GRID ---
        apps_container = QWidget()
        apps_layout = QGridLayout(apps_container)
        apps_layout.setSpacing(25)
        
        row, col = 0, 0
        for app in self.applications_data:
            # Card for App
            app_card = QFrame()
            app_card.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(0, 0, 0, 0.4);
                    border: 2px solid {self.colors['button_colors'][2]};
                    border-radius: 20px;
                }}
            """)
            card_layout = QVBoxLayout(app_card)
            
            # App Header
            app_name = QLabel(app['name'])
            app_name.setStyleSheet(f"color: {self.colors['button_colors'][2]}; font-weight: bold; font-size: 18px; font-family: Impact;")
            card_layout.addWidget(app_name)
            
            # Description
            app_desc = QLabel(app['desc'])
            app_desc.setStyleSheet("color: #DDD; font-size: 13px; font-family: Arial;")
            app_desc.setWordWrap(True)
            card_layout.addWidget(app_desc)
            
            card_layout.addStretch()
            
            # Action Button
            launch_btn = LCARSButton("ЗАПУСК", self.colors['button_colors'][3], "#000")
            launch_btn.clicked.connect(lambda checked, f=app['file']: self.launch_application(f))
            card_layout.addWidget(launch_btn)
            
            self.app_buttons[app['file']] = launch_btn
            
            apps_layout.addWidget(app_card, row, col)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        layout.addWidget(apps_container, 1, 1)
        
        # --- BOTTOM MONITOR PANEL ---
        monitor_panel = QWidget()
        mon_layout = QHBoxLayout(monitor_panel)
        mon_layout.setContentsMargins(20,0,0,0)
        
        # Process Log
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setPlaceholderText("ОЧІКУВАННЯ ПОДІЙ...")
        mon_layout.addWidget(self.log_display, stretch=2)
        
        # Process List
        self.process_list = QTextEdit()
        self.process_list.setReadOnly(True)
        self.process_list.setPlaceholderText("ФОНОВІ ЗАВДАННЯ...")
        mon_layout.addWidget(self.process_list, stretch=1)
        
        # Control Buttons
        ctrl_panel = QVBoxLayout()
        stop_all_btn = LCARSButton("СТОП", "#FF9900", "#000")
        stop_all_btn.clicked.connect(self.stop_all_applications)
        ctrl_panel.addWidget(stop_all_btn)
        
        mon_layout.addLayout(ctrl_panel)
        
        layout.addWidget(monitor_panel, 2, 1)

        self.stack.addWidget(self.main_screen)

    def show_lock_screen(self):
        """Display lock/login screen and set session locked"""
        try:
            self.lock_screen = LCARSLoginScreen(parent=self)
            self.lock_screen.login_successful.connect(self.on_unlock)
            self.lock_screen.showFullScreen()
            self.session_manager.lock()
            self.log_message("БЛОКУВАННЯ")
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            self.log_message(f"ПОМИЛКА: {e}")

    def on_unlock(self):
        try:
            if hasattr(self, 'lock_screen') and self.lock_screen:
                self.lock_screen.close()
                self.lock_screen = None
            self.session_manager.unlock()
            self.log_message("ДОСТУП ДОЗВОЛЕНО")
            self.stack.setCurrentWidget(self.main_screen)
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            self.log_message(f"Unlock Error: {e}")

    def launch_application(self, filename):
        """Launch or stop an application using ProcessSupervisor"""
        if self.supervisor.is_running(filename):
            self.supervisor.stop_process(filename)
            self.log_message(f"ПРИПИНЕНО: {filename}")
            if filename in self.app_buttons:
                self.app_buttons[filename].setText("ЗАПУСК")
            return

        self.log_message(f"ІНІЦІАЛІЗАЦІЯ: {filename}...")
        full_path = str(Path(project_root) / filename)
        
        # Special handling for internal launch vs external process
        success = self.supervisor.start_process(filename, full_path)
            
        if success:
            if filename in self.app_buttons:
                self.app_buttons[filename].setText("АКТИВНИЙ")
        else:
            self.log_message(f"ЗБІЙ: {filename}")
    
    def handle_output(self, filename):
        """Handle process output"""
        process = self.running_processes.get(filename)
        if process:
            data = process.readAllStandardOutput().data().decode('utf-8', errors='ignore').strip()
            if data:
                self.log_message(f"[{filename}] {data}")
    
    def stop_all_applications(self):
        """Stop all running applications"""
        self.supervisor.stop_all()
        self.log_message("СИСТЕМА СКИДАНА")

        for filename in self.app_buttons:
            self.app_buttons[filename].setText("ЗАПУСК")
    
    def update_status(self):
        """Update status displays"""
        term = "25C"
        self.time_label.setText(f"SD {datetime.now().strftime('%y%m.%d %H:%M')}")

        # Update process list
        running = []
        for name in self.supervisor.list_processes():
            if self.supervisor.is_running(name):
                running.append(name.split('/')[-1])

        if running:
            self.process_list.setPlainText("\n".join(running))
        else:
            self.process_list.setPlainText("НЕМАЄ ЗАДАЧ")
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"{timestamp} > {message}")
        lines = self.log_display.toPlainText().split('\n')
        if len(lines) > 50:
            self.log_display.setPlainText('\n'.join(lines[-50:]))

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = LCARSDashboard()
    window.show()
    
    print("🖖 25th Century LCARS Standalone Initialized")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
