"""
LCARS Central Command - Working Version
Simple launcher for all LCARS applications
"""

import sys
import platform
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QGridLayout,
                           QGroupBox, QTextEdit, QMessageBox, QFrame, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, QProcess, QProcessEnvironment, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen

# Add project root
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import lcars.themes.lcars_palette as palette_module
from lcars.themes.lcars_palette import LCARSEra, get_era_palette
from lcars.ui.faction_selector import FactionSelector
from lcars.ui.LCARS_24th import LCARS24thCentury
from lcars.ui.start_menu import StartMenu
from lcars.core.session_manager import SessionManager
from lcars.core.process_supervisor import ProcessSupervisor
from lcars.modules.lock_screen import LCARSLoginScreen

class LCARSButton(QPushButton):
    """Справжня LCARS кнопка з закругленими кутами та анімацією"""
    def __init__(self, text, color, text_color="black", parent=None):
        super().__init__(text, parent)
        self._color = QColor(color)
        self._text_color = text_color
        self._hover_color = self._lighten_color(color)
        self._pressed_color = self._darken_color(color)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: none;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 15px;
                border-radius: 8px;
            }}
        """)
        
    def _lighten_color(self, color):
        """Зробити колір світлішим"""
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = min(255, r + 40)
            g = min(255, g + 40)
            b = min(255, b + 40)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
    
    def _darken_color(self, color):
        """Зробити колір темнішим"""
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = max(0, r - 40)
            g = max(0, g - 40)
            b = max(0, b - 40)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
    
    def enterEvent(self, event):
        """Анімація при наведенні"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._hover_color};
                color: {self._text_color};
                border: none;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 15px;
                border-radius: 8px;
            }}
        """)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Повернення до початкового кольору"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color.name()};
                color: {self._text_color};
                border: none;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 15px;
                border-radius: 8px;
            }}
        """)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Анімація при натисканні"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._pressed_color};
                color: {self._text_color};
                border: none;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 15px;
                border-radius: 8px;
            }}
        """)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Повернення до hover кольору"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._hover_color};
                color: {self._text_color};
                border: none;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 15px;
                border-radius: 8px;
            }}
        """)
        super().mouseReleaseEvent(event)

class LCARSCentralCommand(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Central Command")
        self.showFullScreen()
        
        # Use 25th century theme
        self.current_era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.current_era)
        
        # ЗАСТОСОВУЄМО СПРАВЖНІЙ 25TH CENTURY СТИЛЬ!
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #000000;
                color: #FFFFFF;
            }}
            QWidget {{
                background-color: #000000;
                color: #FFFFFF;
                border: none;
            }}
            QLabel {{
                color: #FFFFFF;
                background-color: transparent;
                border: none;
            }}
            QPushButton {{
                background-color: #2F3749;
                color: #FFFFFF;
                border: none;
                font-weight: bold;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: #52596E;
            }}
            QTextEdit {{
                background-color: rgba(0,0,0,0.8);
                color: #37A6D1;
                border: 1px solid #2F3749;
                font-family: 'Courier New';
            }}
        """)
        
        # Process tracking
        self.running_processes = {}
        self.app_buttons = {}

        # Session and Process supervision
        self.session_manager = SessionManager()
        self.supervisor = ProcessSupervisor(project_root=project_root, parent=self)
        self.supervisor.processOutput.connect(lambda name, data: self.log_message(f"[{name}] {data}"))
        self.supervisor.processFinished.connect(lambda name: self.log_message(f"Process {name} finished"))
        
        # Main stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Create screens
        self.create_start_menu()
        self.create_main_screen()
        self.create_faction_screen()
        
        # Start with start menu
        self.stack.setCurrentWidget(self.start_menu) ("""PROTOTYPE: Start Menu is the default full-screen view""")
        
        # Setup timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)
        
        # Setup shortcuts
        from PyQt6.QtGui import QShortcut, QKeySequence
        self.esc_shortcut = QShortcut(QKeySequence("ESC"), self)
        self.esc_shortcut.activated.connect(self.close)
    
    def create_main_screen(self):
        """Create the main launcher screen"""
        self.main_screen = QWidget()
        layout = QVBoxLayout(self.main_screen)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("◢ LCARS 25TH CENTRAL COMMAND")
        title.setStyleSheet(f"""
            color: #000000; 
            background-color: #37A6D1; 
            font-size: 28px; 
            font-weight: bold; 
            padding: 15px 25px;
            border: none;
        """)
        header.addWidget(title)
        header.addStretch()
        
        # Era buttons
        self.era_buttons = []
        for era in LCARSEra:
            era_btn = LCARSButton(era.value, "#E7442A", "#000000")
            era_btn.clicked.connect(lambda checked, e=era: self.change_era(e))
            era_btn.setCheckable(True)
            if era == self.current_era:
                era_btn.setChecked(True)
            header.addWidget(era_btn)
            self.era_buttons.append(era_btn)
        
        # Кнопка виходу
        exit_btn = LCARSButton("EXIT", "#FF6753", "#000000")
        exit_btn.clicked.connect(self.close)
        header.addWidget(exit_btn)
        
        layout.addLayout(header)
        
        # Time display
        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"color: #9EA5BA; font-size: 18px; font-weight: bold;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)
        
        # Applications grid - без рамок!
        apps_container = QWidget()
        apps_container.setStyleSheet(f"background-color: transparent;")
        apps_layout = QGridLayout(apps_container)
        
        # Applications data
        self.applications_data = [
            {'name': 'LCARS Constructor', 'file': 'constructor.py', 'desc': 'Interface Editor'},
            {'name': 'Geant4 Workstation', 'file': 'lcars/ui/geant4_workstation.py', 'desc': 'Nuclear Simulation'},
            {'name': 'LCARS 24th Century', 'file': 'lcars/ui/LCARS_24th.py', 'desc': 'Authentic Interface'},
            {'name': 'System Monitor', 'file': 'lcars/ui/system_monitor.py', 'desc': 'System Diagnostics'},
            {'name': 'Health Check', 'file': 'lcars/ui/health_check.py', 'desc': 'System Scan'}
        ]
        
        # Create app buttons
        for i, app in enumerate(self.applications_data):
            row = i // 2
            col = (i % 2) * 2
            
            # App info
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            
            name_label = QLabel(app['name'])
            name_label.setStyleSheet(f"color: #FF6753; font-weight: bold; font-size: 14px;")
            info_layout.addWidget(name_label)
            
            desc_label = QLabel(app['desc'])
            desc_label.setStyleSheet(f"color: #9EA5BA; font-size: 11px;")
            info_layout.addWidget(desc_label)
            
            apps_layout.addWidget(info_widget, row, col)
            
            # Launch button - LCARS стиль з анімацією
            launch_btn = LCARSButton("LAUNCH", "#37A6D1", "#000000")
            launch_btn.clicked.connect(lambda checked, f=app['file']: self.launch_application(f))
            apps_layout.addWidget(launch_btn, row, col + 1)
            
            self.app_buttons[app['file']] = launch_btn
        
        layout.addWidget(apps_container)
        
        # Status panel - без рамок!
        status_container = QWidget()
        status_container.setStyleSheet(f"background-color: transparent;")
        status_layout = QVBoxLayout(status_container)
        
        # System info
        self.system_info = QLabel(f"Platform: {platform.system()}\nPython: {platform.python_version()}")
        self.system_info.setStyleSheet(f"""
            color: {self.colors['button_colors'][2]}; 
            font-family: 'Courier New'; 
            font-size: 10px; 
            padding: 10px;
        """)
        status_layout.addWidget(self.system_info)
        
        # Process list - без рамок
        self.process_list = QTextEdit()
        self.process_list.setReadOnly(True)
        self.process_list.setMaximumHeight(100)
        self.process_list.setStyleSheet(f"""
            background-color: rgba(0,0,0,0.7); 
            color: {self.colors['alert_colors'][0]}; 
            font-family: 'Courier New'; 
            font-size: 10px; 
            border: none;
            padding: 5px;
        """)
        status_layout.addWidget(QLabel("RUNNING PROCESSES"))
        status_layout.addWidget(self.process_list)
        
        # Log display - без рамок
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(150)
        self.log_display.setStyleSheet(f"""
            background-color: rgba(0,0,0,0.7); 
            color: {self.colors['button_colors'][2]}; 
            font-family: 'Courier New'; 
            font-size: 10px; 
            border: none;
            padding: 5px;
        """)
        status_layout.addWidget(QLabel("SYSTEM LOGS"))
        status_layout.addWidget(self.log_display)
        
        layout.addWidget(status_container)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        stop_all_btn = LCARSButton("STOP ALL", "#FF6753", "#000000")
        stop_all_btn.clicked.connect(self.stop_all_applications)
        controls_layout.addWidget(stop_all_btn)
        
        exit_btn = LCARSButton("EXIT", "#FF6753", "#000000")
        exit_btn.clicked.connect(self.close)
        controls_layout.addWidget(exit_btn)
        
        layout.addLayout(controls_layout)
        
        self.stack.addWidget(self.main_screen)
    
    def create_start_menu(self):
        """Create the full-screen Start Menu (prototype)"""
        self.start_menu = StartMenu(applications=[
            {'name': 'LCARS Constructor', 'file': 'constructor.py'},
            {'name': 'Geant4 Workstation', 'file': 'lcars/ui/geant4_workstation.py'},
            {'name': 'System Monitor', 'file': 'lcars/ui/system_monitor.py'},
            {'name': 'Health Check', 'file': 'lcars/ui/health_check.py'},
        ])
        # Connect signals
        self.start_menu.launchRequested.connect(self.launch_application)
        self.start_menu.exitRequested.connect(self.close)
        self.start_menu.settingsRequested.connect(lambda: self.log_message('Settings requested (prototype)'))
        self.start_menu.lockRequested.connect(self.show_lock_screen)
        self.stack.addWidget(self.start_menu)

    def create_faction_screen(self):
        """Create the faction selector screen"""
        self.faction_screen = FactionSelector()
        self.faction_screen.factionSelected.connect(self.start_interface)
        self.stack.addWidget(self.faction_screen)
    
    def restore_selector(self):
        """Відновити головний екран"""
        self.stack.setCurrentWidget(self.main_screen)

    def show_lock_screen(self):
        """Display lock/login screen and set session locked"""
        try:
            self.lock_screen = LCARSLoginScreen(parent=self)
            self.lock_screen.login_successful.connect(self.on_unlock)
            self.lock_screen.showFullScreen()
            self.session_manager.lock()
            self.log_message("System locked")
        except Exception as e:
            self.log_message(f"Failed to show lock screen: {e}")

    def on_unlock(self):
        """Called when login is successful"""
        try:
            if hasattr(self, 'lock_screen') and self.lock_screen:
                self.lock_screen.close()
                self.lock_screen = None
            self.session_manager.unlock()
            self.log_message("System unlocked")
            # Return to main screen after unlock
            self.stack.setCurrentWidget(self.main_screen)
        except Exception as e:
            self.log_message(f"Unlock handler error: {e}")

    def change_era(self, era):
        """Змінити епоху та оновити палітру"""
        self.current_era = era
        self.colors = get_era_palette(era)
        
        # Оновити стиль всіх кнопок епох
        for i, btn in enumerate(self.era_buttons):
            new_color = self.colors['button_colors'][i % len(self.colors['button_colors'])]
            btn.setStyleSheet(f"""
                background-color: {new_color}; 
                color: black; 
                font-weight: bold; 
                padding: 10px 15px;
                border: none;
                margin: 2px;
            """)
            btn.setChecked(btn.text() == era.value)
        
        # Оновити головний заголовок
        title = self.findChild(QLabel, "title")
        if title:
            title.setStyleSheet(f"""
                color: black; 
                background-color: {self.colors['button_colors'][0]}; 
                font-size: 28px; 
                font-weight: bold; 
                padding: 15px 25px;
                border: none;
            """)
        
        self.log_message(f"Switched to {era.value} era")
    
    def start_interface(self, faction_id):
        """Start faction-specific interface"""
        if faction_id == "federation":
            self.interface = LCARS24thCentury(None, selector=self)
            
            # Setup return functionality
            def return_to_selector():
                self.stack.setCurrentWidget(self.main_screen)
                if hasattr(self, 'interface') and self.interface:
                    self.stack.removeWidget(self.interface)
                    self.interface = None
            
            self.interface.return_to_selector = return_to_selector
            self.stack.addWidget(self.interface)
            self.stack.setCurrentWidget(self.interface)
        else:
            # For other factions, return to main screen
            self.stack.setCurrentWidget(self.main_screen)
    
    def launch_application(self, filename):
        """Launch or stop an application using ProcessSupervisor"""
        # If already running, stop it
        if self.supervisor.is_running(filename):
            self.supervisor.stop_process(filename)
            self.log_message(f"Stopped {filename}")
            if filename in self.app_buttons:
                self.app_buttons[filename].setText("LAUNCH")
            return

        self.log_message(f"Launching {filename}...")
        full_path = str(Path(project_root) / filename)
        success = self.supervisor.start_process(filename, full_path)
        if success:
            if filename in self.app_buttons:
                self.app_buttons[filename].setText("STOP")
        else:
            self.log_message(f"Failed to launch {filename}")
    
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
        self.log_message("Stopped all processes")

        # Reset button texts
        for filename in self.app_buttons:
            self.app_buttons[filename].setText("LAUNCH")
    
    def update_status(self):
        """Update status displays"""
        # Update time
        self.time_label.setText(datetime.now().strftime("STARDATE %Y.%m.%d - %H:%M:%S"))

        # Update process list from supervisor
        running = []
        for name in self.supervisor.list_processes():
            if self.supervisor.is_running(name):
                running.append(name.split('/')[-1])

        if running:
            self.process_list.setPlainText("\n".join(running))
        else:
            self.process_list.setPlainText("No active processes")
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")
        
        # Keep log size manageable
        lines = self.log_display.toPlainText().split('\n')
        if len(lines) > 50:
            self.log_display.setPlainText('\n'.join(lines[-50:]))

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = LCARSCentralCommand()
    window.show()
    
    print("🖖 LCARS Central Command launched!")
    print("🚀 All systems operational")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
