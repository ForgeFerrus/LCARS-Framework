import sys
import os
import json
import subprocess
import random
import traceback
from pathlib import Path
from datetime import datetime

# Strictly import dependencies - No try/except as requested
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QGridLayout,
    QTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QFont

# Project imports
# Ensure project root is on sys.path so `lcars` package imports work when
# running this file directly.
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.system.paths import get_project_root, get_config_dir
from lcars.themes.palette import (
    LCARSEra, get_era_palette, get_random_button_color,
    get_lcars_font_style, setup_lcars_font
)

# STRICT imports of project widgets (will error if missing, as requested)
# File manager import stays strict; StartMenu may be optional so provide a fallback
from lcars.ui.widgets.file_manager import FileManagerWidget
try:
    from lcars.ui.start_menu import StartMenu
except Exception as e:
    logger.exception("Unhandled exception in %s", __file__)
    raise

    logger.exception("Unhandled exception in %s: %s", __file__, e)
    raise

    # Provide a minimal fallback StartMenu so the desktop can start
    class StartMenu(QWidget):
        launchRequested = pyqtSignal(str)
        def __init__(self, parent=None):
            super().__init__(parent)
            lay = QVBoxLayout(self)
            btn = QPushButton("LAUNCH: SAMPLE MODULE")
            btn.clicked.connect(lambda: self.launchRequested.emit('file_manager'))
            lay.addWidget(btn)
            lay.addStretch()

class LCARSButton(QPushButton):
    """Dynamic LCARS Button with hover effects and era-aware color."""
    def __init__(self, text, era: LCARSEra = LCARSEra.LCARS_25TH, parent=None):
        super().__init__(text, parent)
        self.era = era
        self.default_color = get_random_button_color(self.era)

        self.setFixedHeight(48)
        # Use LCARS font helper for consistent typography (normal weight)
        font_style = get_lcars_font_style(14, 'normal')
        self._set_style(self.default_color, font_style)

    def _set_style(self, color, font_style=''):
        text_color = "#000000"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: none;
                border-radius: 20px;
                padding-left: 20px;
                text-align: left;
                {font_style}
            }}
            QPushButton:hover {{
                background-color: #FFFFFF;
                color: {color};
            }}
            QPushButton:pressed {{
                background-color: #FFCC00;
                color: #000000;
            }}
        """)

class SettingsPanel(QWidget):
    """Minimal embedded Settings panel used by the desktop when no global
    settings widget is available in the repo. Keeps settings local and small.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        h = QLabel("◢ SETTINGS")
        h.setStyleSheet("color: #FF9900; font-size: 16pt;")
        layout.addWidget(h)
        info = QLabel("Basic runtime settings are managed in config files.\nUse the Config Manager for advanced edits.")
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()


class LogsViewer(QWidget):
    """Simple logs viewer that opens the project's main log file if present."""
    def __init__(self, log_path=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        h = QLabel("◢ SYSTEM LOGS")
        h.setStyleSheet("color: #CC9999; font-size: 14pt;")
        layout.addWidget(h)
        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)
        layout.addWidget(self.viewer, 1)
        self._load_log(log_path)

    def _load_log(self, path=None):
        if path is None:
            path = Path(os.getcwd()) / 'logs' / 'lcars_framework.log'
        try:
            if path.exists():
                self.viewer.setPlainText(path.read_text(encoding='utf-8'))
            else:
                self.viewer.setPlainText('No log file found at: ' + str(path))
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            self.viewer.setPlainText(f'Error reading log: {e}')

class LCARSDesktop(QMainWindow):
    """
    Main LCARS Desktop Shell.
    Redesigned to have seamless frames and direct error reporting.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS COMMAND INTERFACE")
        self.setGeometry(0, 0, 1920, 1080)
        
        # Frameless and Fullscreen
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.setStyleSheet("QMainWindow { background-color: #000000; }")

        # Theme
        self.current_era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.current_era)
        setup_lcars_font()
        # Unified font styles for consistent typography across UI
        # Use 'normal' weight for uniform look; sizes can vary but style string same
        self.font_style_title = get_lcars_font_style(24, 'normal')
        self.font_style_button = get_lcars_font_style(14, 'normal')
        self.font_style_small = get_lcars_font_style(12, 'normal')
        
        # Core State
        self.workspace_widgets = {}
        # Buttons whose colors should rotate over time
        self.dynamic_buttons = []
        
        # Build UI
        self._init_ui()
        
        # Clock
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_tick)
        self.timer.start(1000)  # Update every second
    def _init_ui(self):
        # Main Container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Use a grid to simulate the specialized LCARS layout "hugging" the content
        # Row 0: Top Bar
        # Row 1: Main Content
        # Row 2: Bottom Bar
        # Col 0: Left Sidebar
        # Col 1: Content
        
        self.layout = QGridLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)

        # --- LEFT SIDEBAR (The "Elbow" vertical part) ---
        self.left_sidebar = QFrame()
        self.left_sidebar.setFixedWidth(100)
        self.left_sidebar_color = self.colors['button_colors'][0]
        self.left_sidebar.setStyleSheet(f"""
            background-color: {self.left_sidebar_color};
            border-top-left-radius: 60px;
            border-bottom-left-radius: 60px;
        """)
        
        # Content inside sidebar (Stardate, etc)
        sb_layout = QVBoxLayout(self.left_sidebar)
        sb_layout.setContentsMargins(5, 30, 5, 20)
        
        # Example deco text vertical
        self.date_label = QLabel("2402")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.date_label.setStyleSheet("color: #000; font-weight: bold; font-size: 16pt;")
        sb_layout.addWidget(self.date_label)
        sb_layout.addStretch()
        
        self.layout.addWidget(self.left_sidebar, 0, 0, 3, 1) # Spans 3 rows

        # --- TOP HEADER ---
        self.top_header = QFrame()
        self.top_header.setFixedHeight(48)
        self.top_header.setStyleSheet(f"""
            background-color: {self.colors['button_colors'][1]};
            border-top-right-radius: 35px; 
            margin-left: -10px; /* Overlap to look seamless */
        """)
        
        th_layout = QHBoxLayout(self.top_header)
        th_layout.setContentsMargins(20, 0, 10, 0)
        
        title = QLabel("◢ LCARS PRIMARY COMMAND")
        title_style = get_lcars_font_style(24, 'normal')
        title.setStyleSheet(f"color: #000; {title_style}")
        th_layout.addWidget(title)
        th_layout.addStretch()
        
        self.clock_label = QLabel("00:00:00")
        self.clock_label.setStyleSheet(f"color: #000; {get_lcars_font_style(18, 'normal')}")
        th_layout.addWidget(self.clock_label)
        
        self.layout.addWidget(self.top_header, 0, 1)

        # --- MAIN CONTENT AREA ---
        self.content_stack = QStackedWidget()
        self.layout.addWidget(self.content_stack, 1, 1)
        
        # 1. Welcome screen (shown on startup) and Mission Hub
        self.welcome_screen = self.create_welcome_screen()
        self.content_stack.addWidget(self.welcome_screen)
        self.mission_hub = self.create_mission_hub()
        self.content_stack.addWidget(self.mission_hub)
        # start on welcome, then switch to mission hub shortly after
        self.content_stack.setCurrentWidget(self.welcome_screen)
        QTimer.singleShot(1500, lambda: self.content_stack.setCurrentWidget(self.mission_hub))
        
        # 2. Workspace items will be added here

        # --- BOTTOM FOOTER ---
        self.bottom_footer = QFrame()
        self.bottom_footer.setFixedHeight(40)
        self.bottom_footer.setStyleSheet(f"""
            background-color: {self.colors['button_colors'][2]};
            border-bottom-right-radius: 25px;
            margin-left: -10px;
        """)
        
        bf_layout = QHBoxLayout(self.bottom_footer)
        bf_layout.setContentsMargins(12, 4, 12, 4)


        footer_label = QLabel("LCARS Framework v25.2 - All Systems Nominal")
        footer_label.setStyleSheet(f"color: #000; {get_lcars_font_style(12, 'normal')}")
        bf_layout.addWidget(footer_label)
        bf_layout.addStretch()
        self.clock_label_footer = QLabel("00:00:00")
        self.clock_label_footer.setStyleSheet(f"color: #000; {get_lcars_font_style(12, 'normal')}")
        bf_layout.addWidget(self.clock_label_footer)
        
    
    def create_welcome_screen(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(40, 80, 40, 40)
        title = QLabel("WELCOME TO LCARS")
        title.setStyleSheet(f"color: {self.colors['button_colors'][1]}; {self.font_style_title}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        subtitle = QLabel("Primary Command Interface")
        subtitle.setStyleSheet(f"color: {self.colors['button_colors'][3]}; {self.font_style_small}")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(subtitle)

        lay.addStretch()
        return w

    def create_mission_hub(self):
        hub = QWidget()
        # Main layout for hub
        lay = QHBoxLayout(hub)
        lay.setContentsMargins(40, 40, 40, 40)
        
        # Left Column Buttons
        col1 = QVBoxLayout()
        col1.setSpacing(20)
        
        # Header
        h1 = QLabel("PRIMARY FUNCTIONS")
        h1.setStyleSheet("color: #FF9900; font-size: 20pt; border-bottom: 3px solid #FF9900; margin-bottom: 10px;")
        col1.addWidget(h1)

        btns = [
            ("START MENU", "start_menu"),
            ("FILE MANAGER", "file_manager"),
            ("SETTINGS", "settings"),
            ("OCUD", "ocud"),
            ("LOGS", "logs")
        ]
        
        for text, cmd in btns:
            # Create button with unified font style and dynamic color
            btn = LCARSButton(text)
            c = get_random_button_color(self.current_era)
            btn._set_style(c, self.font_style_button)
            self.dynamic_buttons.append(btn)

            if cmd == "start_menu":
                btn.clicked.connect(self.open_start_menu)
            else:
                btn.clicked.connect(lambda _, c=cmd: self.handle_command(c))

            col1.addWidget(btn)
        lay.addLayout(col1, 1)
        
        # Right Column Buttons
        col2 = QVBoxLayout()
        col2.setSpacing(20)
        
        h2 = QLabel("SCIENTIFIC MODULES")
        h2.setStyleSheet("color: #CC99CC; font-size: 20pt; border-bottom: 3px solid #CC99CC; margin-bottom: 10px;")
        col2.addWidget(h2)
        
        btns2 = [
            ("GEANT4 SIMULATION", "geant4"),
            ("CORTEX AI", "cortex"),
            ("DATA ANALYSIS", "data"),
            ("SENSORS", "sensors"),
            ("TERMINAL", "terminal")
        ]
        
        for text, cmd in btns2:
            btn = LCARSButton(text)
            c = get_random_button_color(self.current_era)
            btn._set_style(c, self.font_style_button)
            # track for periodic color rotation
            self.dynamic_buttons.append(btn)
            btn.clicked.connect(lambda _, c=cmd: self.handle_command(c))
            col2.addWidget(btn)

        col2.addStretch()

        sys_row = QHBoxLayout()
        exit_btn = QPushButton("SHUTDOWN SYSTEM")
        exit_btn.setFixedHeight(50)
        exit_btn.setStyleSheet(f"background-color: #CC0000; color: #000; border-radius: 15px; {self.font_style_button}")
        exit_btn.clicked.connect(self.close)
        sys_row.addWidget(exit_btn)
        
        col2.addLayout(sys_row)
        
        lay.addLayout(col2, 1)
        
        return hub

    def handle_command(self, cmd):
        print(f"Command: {cmd}")
        
        if cmd == "file_manager":
            self.open_app("FILE MANAGER", FileManagerWidget(start_path=get_project_root()))
        elif cmd == "terminal":
            # No try/except, let it crash if missing
            from lcars.ui.widgets.terminal import LCARSTerminalWidget
            self.open_app("TERMINAL", LCARSTerminalWidget())
        elif cmd == "geant4":
            # Try to embed the Geant4 panel; fall back to an error view if it fails
            try:
                from programs.geant_project import GeantProjectWidget
                gpw = GeantProjectWidget(geant_root=get_project_root(), parent=self)
                self.open_app("GEANT4", gpw)
            except Exception as e:
                logger.exception("Unhandled exception in %s", __file__)
                raise

                tb = traceback.format_exc()
                lbl = QLabel(f"GEANT4 PANEL FAILED TO LOAD:\n{str(e)}\n\n{tb}")
                lbl.setStyleSheet("color: #FFF; font-size: 12pt;")
                lbl.setWordWrap(True)
                self.open_app("GEANT4 (ERROR)", lbl)
        elif cmd == "settings":
            self.open_app("SETTINGS", SettingsPanel(parent=self))
        elif cmd == "logs":
            self.open_app("LOGS", LogsViewer(parent=self))
        elif cmd == "cortex":
            from lcars.widgets.dashboard import AIAgentWidget
            self.open_app("CORTEX AI", AIAgentWidget())
        elif cmd == "data":
            from lcars.widgets.dashboard_widgets import ConsoleWidget
            self.open_app("DATA ANALYSIS", ConsoleWidget())
        elif cmd == "sensors":
            from lcars.widgets.dashboard_widgets import
import logging
logger = logging.getLogger(__name__)

 SystemMonitorWidget
            self.open_app("SENSORS", SystemMonitorWidget())
        else:
            # Fallback for unconnected buttons
            lbl = QLabel(f"MODULE {cmd.upper()} NOT INSTALLED")
            lbl.setStyleSheet("color: #F00; font-size: 24pt;")
            self.open_app(cmd.upper(), lbl)

    def open_app(self, title, widget):
        """Helper to open a widget in the stack space with a return button."""
        container = QWidget()
        vbox = QVBoxLayout(container)
        
        # Header
        head = QLabel(title)
        header_color = self.colors.get('header_color', self.colors.get('button_colors', ["#FFF"])[0])
        head.setStyleSheet(f"color: {header_color}; font-size: 22pt; margin-bottom: 10px;")
        vbox.addWidget(head)
        
        # The App
        vbox.addWidget(widget, 1)
        
        # Return Button
        ret_btn = QPushButton("RETURN TO MISSION HUB")
        ret_btn.setFixedHeight(50)
        ret_btn.setStyleSheet(f"""
            background-color: {self.colors['button_colors'][0]}; 
            color: #000; 
            border-radius: 15px;
            font-size: 14pt;
            font-weight: bold;
        """)
        # CRITICAL: Return logic
        ret_btn.clicked.connect(self.go_home)
        
        vbox.addWidget(ret_btn)
        
        self.content_stack.addWidget(container)
        self.content_stack.setCurrentWidget(container)

    def go_home(self):
        self.content_stack.setCurrentWidget(self.mission_hub)

    def open_start_menu(self):
        # Using the start menu class
        menu = StartMenu(parent=self)
        menu.launchRequested.connect(self.handle_command)
        self.open_app("START MENU", menu)

    def toggle_mod_mode(self):
        self.mod_mode = not getattr(self, 'mod_mode', False)
        print(f"Mod Mode: {self.mod_mode}")
        # Visual hint: slightly change top header color when in mod mode
        if self.mod_mode:
            self.top_header.setStyleSheet(f"background-color: {self.colors['button_colors'][3]}; border-top-right-radius: 35px; margin-left: -10px;")
        else:
            self.top_header.setStyleSheet(f"background-color: {self.colors['button_colors'][1]}; border-top-right-radius: 35px; margin-left: -10px;")

    def toggle_red_alert(self):
        self.red_alert = not getattr(self, 'red_alert', False)
        if self.red_alert:
            # start flashing via a timer
            if not hasattr(self, '_alert_timer'):
                self._alert_timer = QTimer(self)
                self._alert_state = False
                def _flash():
                    self._alert_state = not self._alert_state
                    c = '#FF0000' if self._alert_state else self.colors['button_colors'][2]
                    self.top_header.setStyleSheet(f"background-color: {c}; border-top-right-radius: 35px; margin-left: -10px;")
                self._alert_timer.timeout.connect(_flash)
            self._alert_timer.start(500)
        else:
            if hasattr(self, '_alert_timer'):
                self._alert_timer.stop()
            # restore header
            self.top_header.setStyleSheet(f"background-color: {self.colors['button_colors'][1]}; border-top-right-radius: 35px; margin-left: -10px;")

    def update_tick(self):
        now = datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S"))
        # Update random numbers in UI if we had them
def main():
    app = QApplication(sys.argv)
    
    # Global stylesheet tweak for scrollbars to look more sci-fi
    app.setStyleSheet("""
        QScrollBar:vertical {
            border: none;
            background: #000;
            width: 15px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #F90;
            min-height: 20px;
            border-radius: 7px;
        }
    """)
    
    desktop = LCARSDesktop()
    desktop.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
