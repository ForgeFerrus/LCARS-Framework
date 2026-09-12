# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: import subprocess
import random
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from datetime import datetime

# Strictly import dependencies - No try/except as requested
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QGridLayout,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QColor, QFont

# Project imports
from lcars.system.paths import get_project_root, get_config_dir
from lcars.themes.lcars_palette import (
    LCARSEra, get_era_palette, get_random_button_color,
    get_lcars_font_style, setup_lcars_font
)

# STRICT imports of project widgets (will error if missing, as requested)
from lcars.ui.widgets.file_manager import FileManagerWidget
from lcars.ui.start_menu import StartMenu
# If these don't exist in path, it will crash, which is what the user wants ("Why checks remain!")

class LCARSButton(QPushButton):
    """Dynamic LCARS Button with hover effects."""
    def __init__(self, text, color_func=None, parent=None):
        super().__init__(text, parent)
        self.color_func = color_func
        self.default_color = get_random_button_color(LCARSEra.LCARS_25TH)
        if self.color_func:
            self.default_color = self.color_func()
        
        self.setFixedHeight(60)
        self.setFont(QFont("Haettenschweiler", 18))  # Fallback font
        self._set_style(self.default_color)

    def _set_style(self, color):
        # Dynamic style with hover reaction
        text_color = "#000000"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: none;
                border-radius: 20px;
                padding-left: 20px;
                text-align: left;
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
        
        # Core State
        self.workspace_widgets = {}
        
        # Build UI
        self._init_ui()
        
        # Clock
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_tick)
        self.timer.start(1000)

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
        self.left_sidebar.setFixedWidth(140)
        self.left_sidebar_color = self.colors['button_colors'][0]
        self.left_sidebar.setStyleSheet(f"""
            background-color: {self.left_sidebar_color};
            border-top-left-radius: 60px;
            border-bottom-left-radius: 60px;
        """)
        
        # Content inside sidebar (Stardate, etc)
        sb_layout = QVBoxLayout(self.left_sidebar)
        sb_layout.setContentsMargins(5, 60, 5, 40)
        
        # Example deco text vertical
        self.date_label = QLabel("2402")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.date_label.setStyleSheet("color: #000; font-weight: bold; font-size: 16pt;")
        sb_layout.addWidget(self.date_label)
        sb_layout.addStretch()
        
        self.layout.addWidget(self.left_sidebar, 0, 0, 3, 1) # Spans 3 rows

        # --- TOP HEADER ---
        self.top_header = QFrame()
        self.top_header.setFixedHeight(70)
        self.top_header.setStyleSheet(f"""
            background-color: {self.colors['button_colors'][1]};
            border-top-right-radius: 35px; 
            margin-left: -10px; /* Overlap to look seamless */
        """)
        
        th_layout = QHBoxLayout(self.top_header)
        th_layout.setContentsMargins(30, 0, 20, 0)
        
        title = QLabel("USS ODYSSEY // SYSTEM CONTROL")
        title.setStyleSheet("color: #000; font-size: 24pt; font-weight: bold;")
        th_layout.addWidget(title)
        th_layout.addStretch()
        
        self.clock_label = QLabel("00:00:00")
        self.clock_label.setStyleSheet("color: #000; font-size: 24pt; font-weight: bold;")
        th_layout.addWidget(self.clock_label)
        
        self.layout.addWidget(self.top_header, 0, 1)

        # --- MAIN CONTENT AREA ---
        self.content_stack = QStackedWidget()
        self.layout.addWidget(self.content_stack, 1, 1)
        
        # 1. Mission Hub (Home)
        self.mission_hub = self.create_mission_hub()
        self.content_stack.addWidget(self.mission_hub)
        
        # 2. Workspace items will be added here

        # --- BOTTOM FOOTER ---
        self.bottom_footer = QFrame()
        self.bottom_footer.setFixedHeight(50)
        self.bottom_footer.setStyleSheet(f"""
            background-color: {self.colors['button_colors'][2]};
            border-bottom-right-radius: 25px;
            margin-left: -10px;
        """)
        
        bf_layout = QHBoxLayout(self.bottom_footer)
        bf_layout.setContentsMargins(30, 0, 20, 0)
        
        status = QLabel("SYSTEMS NORMAL")
        status.setStyleSheet("color: #000; font-weight: bold; font-size: 14pt;")
        bf_layout.addWidget(status)
        bf_layout.addStretch()
        
        self.layout.addWidget(self.bottom_footer, 2, 1)

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
            # Random color for each button
            btn = LCARSButton(text) 
            # Force color to be random now
            c = get_random_button_color(self.current_era)
            btn._set_style(c)
            
            if cmd == "start_menu":
                btn.clicked.connect(self.open_start_menu)
            else:
                btn.clicked.connect(lambda _, c=cmd: self.handle_command(c))
            col1.addWidget(btn)
        
        col1.addStretch()
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
            btn._set_style(c)
            btn.clicked.connect(lambda _, c=cmd: self.handle_command(c))
            col2.addWidget(btn)

        col2.addStretch()
        
        # System buttons row
        sys_row = QHBoxLayout()
        exit_btn = QPushButton("SHUTDOWN SYSTEM")
        exit_btn.setFixedHeight(50)
        exit_btn.setStyleSheet("background-color: #CC0000; color: #000; border-radius: 15px; font-weight: bold; font-size: 14pt;")
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
            # Just a placeholder for now, but no silent fail
            lbl = QLabel("GEANT4 INTERFACE LOADING...")
            lbl.setStyleSheet("color: #FFF; font-size: 20pt;")
            self.open_app("GEANT4", lbl)
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
        head.setStyleSheet(f"color: {self.colors['header_color']}; font-size: 22pt; margin-bottom: 10px;")
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
