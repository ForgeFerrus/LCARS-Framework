"""
LCARS UI Launcher - Faction and Era Selection Dialog
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import datetime
from typing import Optional, Sequence
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QStackedLayout, QWidget, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from lcars.themes.palette import ( LCARSColorGenerator,
    LCARSEra, get_lcars_font_style,
    get_random_button_color, get_alert_color, get_era_palette, FactionEra
)
# Default factions and eras
DEFAULT_FACTIONS = ["Federation", "Klingon", "Romulan", "Cardassian"]
DEFAULT_ERAS = ["22nd", "23rd", "23st", "24th", "24st", "25th", "29th"]

class FactionDialog(QDialog):
    """Unified LCARS System with Boot -> Login -> Launcher -> Desktop sequence"""
    
    def __init__(self, factions: Sequence[str], eras: Sequence[str], parent=None):
        super().__init__(parent)
        self.era_enum = LCARSEra.LCARS_25TH
        self.color_gen = LCARSColorGenerator(self.era_enum)
        self.factions = factions
        self.eras = eras
        self.current_faction = None
        
        self.selected_faction = factions[0]
        self.selected_era = eras[0]
        self.alert_mode = False
        self._bar_index = 0
        self.current_phase = "boot"
        self.boot_progress = 0
        self.node_phase = 0  # Add missing attribute
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black; color: white;")
        self.resize(1200, 800)
        self.setWindowTitle("LCARS System Access")
        print(f"Window setup complete, size: {self.size()}")

        # Center window on screen
        from PyQt6.QtGui import QScreen
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)
            print(f"Window centered at: ({x}, {y})")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setFixedSize(1200, 800)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(4)
        
        # Stacked widget for different phases
        self.stack = QStackedWidget()
        c_layout.addWidget(self.stack)
        
        # Create all phases
        self.create_boot_phase()
        self.create_login_phase()
        self.create_launcher_phase()
        self.create_desktop_phase()
        
        main_layout.addWidget(container)
        
        # Start boot sequence
        QTimer.singleShot(500, self.start_boot_sequence)
        
    def create_boot_phase(self):
        """Create boot sequence phase"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.boot_elb = QFrame()
        self.boot_elb.setFixedSize(200, 70)
        self.boot_elb.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(0)}; border-top-left-radius: 50px; border-bottom-left-radius: 4px;")
        header.addWidget(self.boot_elb)
        
        self.boot_title = QFrame()
        self.boot_title.setFixedHeight(70)
        self.boot_title.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(1)}; border-radius: 4px; color: black;")
        title_layout = QHBoxLayout(self.boot_title)
        title_lbl = QLabel("◢ LCARS SYSTEM - INITIALIZATION")
        title_lbl.setStyleSheet(get_lcars_font_style(24, 'normal'))
        title_layout.addWidget(title_lbl)
        header.addWidget(self.boot_title, 1)
        
        self.boot_cap = QFrame()
        self.boot_cap.setFixedSize(60, 70)
        self.boot_cap.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(2)}; border-top-right-radius: 35px; border-bottom-right-radius: 4px;")
        header.addWidget(self.boot_cap)
        layout.addLayout(header)
        
        # Main boot area
        main = QHBoxLayout()
        main.setSpacing(4)
        
        boot_sidebar = QFrame()
        boot_sidebar.setFixedWidth(200)
        boot_sidebar.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(3)}; border-radius: 4px; border-bottom-left-radius: 80px;")
        main.addWidget(boot_sidebar)
        
        boot_content = QVBoxLayout()
        boot_content.setContentsMargins(20, 10, 10, 10)
        
        self.boot_step = QLabel("INITIALIZING...")
        self.boot_step.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(24, 'normal')}")
        boot_content.addWidget(self.boot_step)
        
        self.boot_log = QLabel("> BOOT_MODE: NOMINAL")
        self.boot_log.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(16, 'normal')}")
        self.boot_log.setWordWrap(True)
        boot_content.addWidget(self.boot_log)
        boot_content.addStretch()
        
        main.addLayout(boot_content, 1)
        layout.addLayout(main, 1)
        
        # Footer
        self.boot_footer = QFrame()
        self.boot_footer.setFixedHeight(40)
        self.boot_footer.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(4)}; border-bottom-right-radius: 20px; border-top-right-radius: 4px;")
        layout.addWidget(self.boot_footer)
        
        self.stack.addWidget(widget)
        
    def create_login_phase(self):
        """Create login phase"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.login_elb = QFrame()
        self.login_elb.setFixedSize(180, 60)
        self.login_elb.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(5)}; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
        header.addWidget(self.login_elb)
        
        self.login_title = QFrame()
        self.login_title.setFixedHeight(60)
        self.login_title.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(6)}; border-radius: 4px; color: black;")
        title_layout = QHBoxLayout(self.login_title)
        title_layout.setContentsMargins(20, 0, 0, 0)
        title_lbl = QLabel("◢ AUTHORIZATION PROTOCOL // SECURE ACCESS")
        title_lbl.setStyleSheet(get_lcars_font_style(18, 'normal'))
        title_layout.addWidget(title_lbl)
        header.addWidget(self.login_title, 1)
        
        self.login_cap = QFrame()
        self.login_cap.setFixedSize(40, 60)
        self.login_cap.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(7)}; border-top-right-radius: 20px; border-bottom-right-radius: 4px;")
        header.addWidget(self.login_cap)
        layout.addLayout(header)
        
        # Main login area
        main = QHBoxLayout()
        main.setSpacing(10)
        
        # Sidebar
        sidebar = QVBoxLayout()
        sidebar.setSpacing(4)
        self.login_sidebar = QFrame()
        self.login_sidebar.setFixedSize(180, 200)
        self.login_sidebar.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(8)}; border-radius: 4px; border-bottom-left-radius: 60px;")
        sidebar.addWidget(self.login_sidebar)
        sidebar.addStretch()
        main.addLayout(sidebar)
        
        # Content
        content = QVBoxLayout()
        content.setContentsMargins(30, 20, 30, 20)
        content.setSpacing(15)
        
        self.login_status = QLabel("PROTOCOL :: IDENTIFYING NEURAL PATTERN...")
        self.login_status.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(18, 'normal')}")
        content.addWidget(self.login_status)
        
        # Simple progress bar
        progress_frame = QFrame()
        progress_frame.setFixedHeight(25)
        progress_frame.setStyleSheet("background-color: #222; border-radius: 2px;")
        progress_layout = QHBoxLayout(progress_frame)
        self.login_progress = QFrame()
        self.login_progress.setStyleSheet("background-color: #4BBEBF; border-radius: 2px;")
        self.login_progress.setFixedWidth(50)
        progress_layout.addWidget(self.login_progress)
        progress_layout.addStretch()
        content.addWidget(progress_frame)
        
        content.addStretch()
        
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.login_btn = QPushButton("AUTHORIZE")
        self.login_btn.setFixedSize(180, 50)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #3366CC;
                color: white;
                border: none;
                border-radius: 4px;
                {get_lcars_font_style(16, 'bold')}
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: white;
                color: #3366CC;
            }}
        """)
        self.login_btn.clicked.connect(self.complete_login)
        btn_box.addWidget(self.login_btn)
        content.addLayout(btn_box)
        
        main.addLayout(content, 1)
        layout.addLayout(main, 1)
        
        # Footer
        self.login_footer = QFrame()
        self.login_footer.setFixedHeight(30)
        self.login_footer.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(9)}; border-bottom-right-radius: 15px; border-top-right-radius: 4px;")
        layout.addWidget(self.login_footer)
        
        self.stack.addWidget(widget)
        
    def create_launcher_phase(self):
        """Create launcher phase - using existing launcher code"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Use existing launcher structure but simplified
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.launcher_elb = QFrame()
        self.launcher_elb.setFixedSize(220, 80)
        self.launcher_elb.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(10)}; border-top-left-radius: 50px; border-bottom-left-radius: 4px;")
        header.addWidget(self.launcher_elb)
        
        self.launcher_title = QFrame()
        self.launcher_title.setFixedHeight(80)
        self.launcher_title.setStyleSheet("background-color: #99FFFF; border-radius: 4px; color: black;")
        title_layout = QHBoxLayout(self.launcher_title)
        title_layout.setContentsMargins(25, 0, 0, 0)
        title_lbl = QLabel("◢ SYSTEM ACCESS // TEMPORAL ALIGNMENT")
        title_lbl.setStyleSheet(get_lcars_font_style(24, 'normal'))
        title_layout.addWidget(title_lbl)
        header.addWidget(self.launcher_title, 1)
        
        self.launcher_cap = QFrame()
        self.launcher_cap.setFixedSize(80, 80)
        self.launcher_cap.setStyleSheet("background-color: #9EA5BA; border-top-right-radius: 40px; border-bottom-right-radius: 4px;")
        header.addWidget(self.launcher_cap)
        layout.addLayout(header)
        
        # Main launcher area
        main = QHBoxLayout()
        main.setSpacing(6)
        
        # Sidebar
        sidebar = QVBoxLayout()
        sidebar.setSpacing(6)
        
        self.launcher_sidebar = QFrame()
        self.launcher_sidebar.setFixedSize(220, 400)
        self.launcher_sidebar.setStyleSheet("background-color: #2A7193; border-radius: 4px; border-bottom-left-radius: 100px;")
        sidebar.addWidget(self.launcher_sidebar)
        
        sidebar.addStretch()
        
        # Animated nodes
        self.launcher_nodes = []
        for _ in range(6):
            n = QFrame()
            n.setFixedSize(220, 20)
            n.setStyleSheet("background-color: #4BBEBF; border-radius: 2px;")
            sidebar.addWidget(n)
            self.launcher_nodes.append(n)
            
        # RED ALERT Button
        self.alert_btn = QPushButton("RED ALERT")
        self.alert_btn.setFixedSize(220, 60)
        self.alert_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #D80000;
                color: white;
                border: none;
                border-radius: 4px;
                {get_lcars_font_style(16, 'bold')}
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: white;
                color: #D80000;
            }}
        """)
        sidebar.addWidget(self.alert_btn)
        
        main.addLayout(sidebar)
        
        # Content area
        content = QVBoxLayout()
        content.setContentsMargins(40, 20, 20, 20)
        content.setSpacing(20)
        
        # Stardate
        stardate = datetime.datetime.now().strftime("%Y.%m.%d")
        self.launcher_info = QLabel(f"STARDATE: {stardate} // TEMPORAL ALIGNMENT")
        self.launcher_info.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(28, 'normal')}")
        content.addWidget(self.launcher_info)
        
        # Era selection
        era_label = QLabel("SELECT TEMPORAL PERIOD")
        era_label.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(20, 'normal')}")
        era_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.addWidget(era_label)
        
        era_grid = QGridLayout()
        era_grid.setSpacing(15)
        
        eras = [
            ("22ND", LCARSEra.COMS_22ND),
            ("23RD", LCARSEra.PCARS_23RD),
            ("24TH", LCARSEra.LCARS_24TH),
            ("25TH", LCARSEra.LCARS_25TH),
            ("29TH", LCARSEra.TCARS_29TH)
        ]
        
        for i, (display, era) in enumerate(eras):
            btn = QPushButton(display)
            btn.setFixedSize(200, 60)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {get_random_button_color(era)};
                    color: black;
                    border: none;
                    border-radius: 4px;
                    {get_lcars_font_style(16, 'bold')}
                    text-transform: uppercase;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {get_random_button_color(era)};
                }}
            """)
            btn.clicked.connect(lambda checked, e=era: self.select_era(e))
            era_grid.addWidget(btn, i // 3, i % 3)
        
        content.addLayout(era_grid)
        
        # Launch button
        launch_btn = QPushButton("LAUNCH SYSTEM")
        launch_btn.setFixedSize(300, 60)
        launch_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #00FF00;
                color: black;
                border: none;
                border-radius: 4px;
                {get_lcars_font_style(18, 'bold')}
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: white;
                color: #00FF00;
            }}
        """)
        launch_btn.clicked.connect(self.launch_desktop)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(launch_btn)
        btn_layout.addStretch()
        content.addLayout(btn_layout)
        
        content.addStretch()
        
        main.addLayout(content, 1)
        layout.addLayout(main)
        
        # Footer
        self.launcher_footer = QFrame()
        self.launcher_footer.setFixedHeight(40)
        self.launcher_footer.setStyleSheet("background-color: #2A7193; border-bottom-right-radius: 20px; border-top-right-radius: 4px;")
        layout.addWidget(self.launcher_footer)
        
        self.stack.addWidget(widget)
        
        # Start node animation
        self.node_timer = QTimer()
        self.node_timer.timeout.connect(self.cycle_nodes)
        self.node_timer.start(4000)
        
    def create_desktop_phase(self):
        """Create desktop phase"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(4)
        
        desktop_elb = QFrame()
        desktop_elb.setFixedSize(250, 80)
        desktop_elb.setStyleSheet("background-color: #4BBEBF; border-top-left-radius: 50px; border-bottom-left-radius: 4px;")
        header.addWidget(desktop_elb)
        
        title_panel = QFrame()
        title_panel.setFixedHeight(80)
        title_panel.setStyleSheet("background-color: #99FFFF; border-radius: 4px; color: black;")
        title_layout = QHBoxLayout(title_panel)
        title = QLabel(f"USS ENTERPRISE - {self.selected_faction} {self.selected_era}")
        title.setStyleSheet(get_lcars_font_style(28, 'normal'))
        title_layout.addWidget(title)
        header.addWidget(title_panel, 1)
        
        right_cap = QFrame()
        right_cap.setFixedSize(100, 80)
        right_cap.setStyleSheet("background-color: #9EA5BA; border-top-right-radius: 40px; border-bottom-right-radius: 4px;")
        header.addWidget(right_cap)
        
        layout.addLayout(header)
        
        # Main interface
        interface = QHBoxLayout()
        interface.setSpacing(6)
        
        # Left control panel
        left_panel = QVBoxLayout()
        left_panel.setSpacing(6)
        
        main_left = QFrame()
        main_left.setFixedWidth(250)
        main_left.setStyleSheet("background-color: #2A7193; border-radius: 4px; border-bottom-left-radius: 100px;")
        left_panel.addWidget(main_left, 1)
        
        controls = ["DASHBOARD", "TACTICAL", "SCIENCE", "ENGINEERING", "COMMUNICATIONS"]
        
        for control in controls:
            btn = QPushButton(control)
            btn.setFixedSize(250, 60)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {get_random_button_color(self.era_enum)};
                    color: black;
                    border: none;
                    border-radius: 4px;
                    {get_lcars_font_style(16, 'bold')}
                    text-transform: uppercase;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {get_random_button_color(self.era_enum)};
                }}
            """)
            left_panel.addWidget(btn)
        
        left_panel.addStretch(1)
        
        bottom_elbow = QFrame()
        bottom_elbow.setFixedSize(250, 80)
        bottom_elbow.setStyleSheet("background-color: #4BBEBF; border-bottom-left-radius: 40px; border-top-left-radius: 6px;")
        left_panel.addWidget(bottom_elbow)
        
        interface.addLayout(left_panel)
        
        # Center display
        center = QVBoxLayout()
        center.setContentsMargins(20, 20, 20, 20)
        center.setSpacing(15)
        
        # Main status
        status_panel = QFrame()
        status_panel.setFixedHeight(120)
        status_panel.setStyleSheet("background-color: #4BBEBF; border-radius: 4px; color: black;")
        status_layout = QVBoxLayout(status_panel)
        
        status_title = QLabel("MAIN SYSTEMS STATUS")
        status_title.setStyleSheet(get_lcars_font_style(24, 'normal'))
        status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_title)
        
        status_info = QLabel("ALL SYSTEMS OPERATIONAL - GREEN ALERT")
        status_info.setStyleSheet(get_lcars_font_style(18, 'normal'))
        status_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_info)
        
        center.addWidget(status_panel)
        
        # System panels
        systems_grid = QGridLayout()
        systems_grid.setSpacing(15)
        
        systems = [
            ("SHIELDS", "ONLINE - 100%"),
            ("WEAPONS", "STANDBY"),
            ("ENGINES", "WARP 9.0"),
            ("SENSORS", "LONG RANGE"),
            ("COMM", "SUBSPACE OPEN"),
            ("LIFE SUPPORT", "OPTIMAL")
        ]
        
        for i, (system, status) in enumerate(systems):
            panel = QFrame()
            panel.setFixedSize(200, 80)
            panel.setStyleSheet(f"background-color: {get_random_button_color(self.era_enum)}; border-radius: 4px; color: black;")
            panel_layout = QVBoxLayout(panel)
            
            system_label = QLabel(system)
            system_label.setStyleSheet(get_lcars_font_style(16, 'normal'))
            system_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            panel_layout.addWidget(system_label)
            
            status_label = QLabel(status)
            status_label.setStyleSheet(get_lcars_font_style(14, 'normal'))
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            panel_layout.addWidget(status_label)
            
            systems_grid.addWidget(panel, i // 2, i % 2)
        
        center.addLayout(systems_grid)
        center.addStretch()
        
        interface.addLayout(center, 1)
        layout.addLayout(interface)
        
        # Footer
        footer = QHBoxLayout()
        footer.setSpacing(4)
        
        left_status = QFrame()
        left_status.setFixedSize(300, 50)
        left_status.setStyleSheet("background-color: #4BBEBF; border-bottom-left-radius: 25px; border-top-left-radius: 6px;")
        footer.addWidget(left_status)
        
        center_status = QFrame()
        center_status.setFixedHeight(50)
        center_status.setStyleSheet("background-color: #2A7193; border-radius: 4px; color: #99FFFF;")
        center_layout = QHBoxLayout(center_status)
        import time
        status_text = QLabel(f"STARDATE: {int(time.time()) % 100000} - SYSTEM READY")
        status_text.setStyleSheet(get_lcars_font_style(16, 'normal'))
        center_layout.addWidget(status_text)
        footer.addWidget(center_status, 1)
        
        right_status = QFrame()
        right_status.setFixedSize(150, 50)
        right_status.setStyleSheet("background-color: #9EA5BA; border-bottom-right-radius: 25px; border-top-right-radius: 6px;")
        footer.addWidget(right_status)
        
        layout.addLayout(footer)
        
        self.stack.addWidget(widget)
        
    def start_boot_sequence(self):
        """Start the unified boot sequence"""
        self.current_phase = "boot"
        self.stack.setCurrentIndex(0)  # Show boot screen
        
        self.boot_steps = [
            "◤ ISOLINEAR CORE: INITIALIZING...",
            "◤ NEXUS DATA HUB: CONNECTING...", 
            "◤ NEURAL PROCESSOR: CALIBRATING...",
            "◤ SUBSPACE COMMUNICATIONS: ESTABLISHING LINK...",
            "◤ TACTICAL SYSTEMS: LOADING...",
            "◤ SHIELD GENERATORS: POWERING UP...",
            "◤ WARP CORE: IGNITION SEQUENCE...",
            "◤ LIFE SUPPORT: ONLINE",
            "◤ LCARS INTERFACE: READY"
        ]
        
        self.boot_timer = QTimer()
        self.boot_timer.timeout.connect(self.update_boot)
        self.boot_timer.start(800)
        
        # Play sound
        try:
            from lcars.modules.sound_manager import get_sound_manager
            get_sound_manager().play("acknowledge")
        except:
            pass
            
    def update_boot(self):
        """Update boot progress"""
        if self.boot_progress < len(self.boot_steps):
            step_text = self.boot_steps[self.boot_progress]
            self.boot_step.setText(step_text)
            self.boot_log.setText(f"{self.boot_log.text()}\n> {step_text.split(':')[0]} :: ONLINE")
            
            # Update colors
            self.boot_elb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-left-radius: 50px; border-bottom-left-radius: 4px;")
            self.boot_title.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
            
            # Play sound
            try:
                from lcars.modules.sound_manager import get_sound_manager
                get_sound_manager().play("click")
            except:
                pass
            
            self.boot_progress += 1
        else:
            self.boot_timer.stop()
            try:
                from lcars.modules.sound_manager import get_sound_manager
                get_sound_manager().play("ready")
            except:
                pass
            QTimer.singleShot(1500, self.transition_to_login)
            
    def transition_to_login(self):
        """Transition to login phase"""
        self.current_phase = "login"
        self.stack.setCurrentIndex(1)  # Show login screen
        QTimer.singleShot(2000, self.start_login)
        
    def start_login(self):
        """Start login phase"""
        self.login_status.setText("SCANNING BIOMETRICS... [MATCH CONFIRMED]")
        # Animate progress bar
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.animate_login_progress)
        self.progress_timer.start(100)
        self.progress_width = 50
        
        try:
            from lcars.modules.sound_manager import get_sound_manager
            get_sound_manager().play("acknowledge")
        except:
            pass
        QTimer.singleShot(2000, self.transition_to_launcher)
        
    def animate_login_progress(self):
        """Animate login progress bar"""
        self.progress_width += 5
        if self.progress_width > 200:
            self.progress_width = 50
        self.login_progress.setFixedWidth(self.progress_width)
        
    def complete_login(self):
        """Complete login manually"""
        self.login_status.setText("SCANNING BIOMETRICS... [MATCH CONFIRMED]")
        try:
            from lcars.modules.sound_manager import get_sound_manager
            get_sound_manager().play("acknowledge")
        except:
            pass
        QTimer.singleShot(1500, self.transition_to_launcher)
        
    def transition_to_launcher(self):
        """Transition to launcher phase"""
        self.current_phase = "launcher"
        self.stack.setCurrentIndex(2)  # Show launcher screen
        try:
            from lcars.modules.sound_manager import get_sound_manager
            get_sound_manager().play("ready")
        except:
            pass
        
    def select_faction(self, faction):
        """Handle faction selection"""
        try:
            from lcars.modules.sound_manager import get_sound_manager
            get_sound_manager().play("acknowledge")
        except:
            pass
        self.selected_faction = faction
        stardate = datetime.datetime.now().strftime("%Y.%m.%d")
        self.launcher_info.setText(f"STARDATE: {stardate} // {faction} SECTOR")
        
    def select_era(self, era):
        """Handle era selection - змінює палітру інтерфейсу"""
        try:
            from lcars.modules.sound_manager import get_sound_manager
            get_sound_manager().play("acknowledge")
        except:
            pass
        self.selected_era = era.value if hasattr(era, 'value') else str(era)
        self.era_enum = era
        self.color_gen = LCARSColorGenerator(era)
        
        # Оновити палітру всіх елементів
        self._update_ui_palette()
        
    def _update_ui_palette(self):
        """Оновити кольори UI відповідно до епохи"""
        palette = get_era_palette(self.era_enum)
        
        # Оновити launcher sidebar
        self.launcher_sidebar.setStyleSheet(f"background-color: {palette['button_colors'][0]}; border-radius: 4px; border-bottom-left-radius: 100px;")
        
        # Оновити footer
        self.launcher_footer.setStyleSheet(f"background-color: {palette['button_colors'][0]}; border-bottom-right-radius: 20px; border-top-right-radius: 4px;")
        
        # Оновити info label
        self.launcher_info.setStyleSheet(f"color: {palette['button_colors'][1]}; {get_lcars_font_style(28, 'normal')}")
        self.launcher_info.setText(f"STARDATE: {datetime.datetime.now().strftime('%Y.%m.%d')} // ERA: {self.selected_era.upper()}")
        
    def cycle_nodes(self):
        """Animate launcher nodes"""
        if self.current_phase != "launcher":
            return
        colors = ["#4BBEBF", "#3366CC", "#FFCC33", "#CC6633"]
        for i, node in enumerate(reversed(self.launcher_nodes)):
            idx = (self.node_phase + i) % len(colors)
            node.setStyleSheet(f"background-color: {colors[idx]}; border-radius: 2px;")
        self.node_phase = (self.node_phase + 1) % len(colors)
        
    def launch_desktop(self):
        """Launch desktop phase"""
        try:
            from lcars.modules.sound_manager import get_sound_manager
            get_sound_manager().play("ready")
        except:
            pass
        self.current_phase = "desktop"
        self.stack.setCurrentIndex(3)  # Show desktop screen
        
    # Keep existing methods for compatibility
    def selection(self):
        """Return current selection for compatibility"""
        return (self.selected_faction, self.selected_era, 0)

        # --- NAVIGATION BAR (FIXED AT BOTTOM) ---
        nav = QHBoxLayout()
        nav.setContentsMargins(188, 5, 8, 5) 
        nav.setSpacing(15)

        self.back_btn = QPushButton("RETURN")
        self.back_btn.setFixedSize(220, 56) 
        self.back_btn.setStyleSheet(self._get_btn_style("#FF9900", size=20))
        self.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.back_btn.setVisible(False)
        self.stack.currentChanged.connect(lambda idx: self.back_btn.setVisible(idx > 0))
        nav.addWidget(self.back_btn)
        
        c_layout.addLayout(nav)
 
        # --- FOOTER ---
        self.footer_fr = QFrame()
        self.footer_fr.setFixedHeight(48)
        self.footer_fr.setStyleSheet(f"""
            background-color: {self.color_gen.get_color_at_index(4)}; 
            border-bottom-right-radius: 40px; 
            border-top-right-radius: 4px;
            margin-left: 188px;
        """)
        c_layout.addWidget(self.footer_fr)

        # Center on screen
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(container)
        h_center.addStretch()
        main_layout.addLayout(h_center)

        # Disable all timers for stability
        # self.color_timer = QTimer(self)
        # self.color_timer.timeout.connect(self._cycle_atmosphere_colors)
        # self.color_timer.start(5000)

        # Disable problematic timer
        # self.running_timer = QTimer(self)
        # self.running_timer.timeout.connect(self._cycle_running_bars)
        # self.running_timer.start(400)

        # Don't show full screen for modal dialog
        # self.showFullScreen()

    def _get_btn_style(self, color, size=24):
        """Clean, professional LCARS Brick Style"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: black;
                border: none;
                border-radius: 4px;
                {get_lcars_font_style(size, 'normal')}
                text-align: right;
                padding-right: 15px;
                text-transform: uppercase;
            }}
            QPushButton:hover {{ 
                background-color: white; 
                color: black;
            }}
            QPushButton:pressed {{ 
                background-color: #666666; 
            }}
        """
      
    def _select_faction(self, faction):
        self.selected_faction = faction
        f_map = {"Klingon": FactionEra.KLINGON, "Romulan": FactionEra.ROMULAN, "Cardassian": FactionEra.CARDASSIAN, "Federation": None}
        self.current_faction = f_map.get(faction)
        self.color_gen = LCARSColorGenerator(self.era_enum, self.current_faction)
        
        # Immediate UI Update - DISABLED
        # self._cycle_atmosphere_colors()

        # Dim others
        for btn in self.faction_btns.values():
            if btn.text() == faction.upper():
                btn.setStyleSheet(self._get_btn_style("#00CC00", size=26)) 
            else:
                btn.setStyleSheet(self._get_btn_style("#222222", size=26))
        
        QTimer.singleShot(300, lambda: self.stack.setCurrentIndex(1))

    def _select_era(self, era):
        self.selected_era = era
        era_map = {"22nd": LCARSEra.COMS_22ND, "23rd": LCARSEra.PCARS_23RD, "23st": LCARSEra.PCARS_23ST, "24th": LCARSEra.LCARS_24TH, "24st": LCARSEra.LCARS_24ST, "25th": LCARSEra.LCARS_25TH, "29th": LCARSEra.TCARS_29TH}
        self.era_enum = era_map.get(era, LCARSEra.LCARS_24TH)

        for btn in self.era_btns.values():
            if btn.text() == era.upper():
                btn.setStyleSheet(self._get_btn_style("#00CC00", size=22))
            else:
                btn.setStyleSheet(self._get_btn_style("#222222", size=22))
        
        # Auto-accept after a short delay for smoothness
        QTimer.singleShot(300, self._on_ok)

    def _on_ok(self):
        try:
            from lcars.system.alert import alert_system
            alert_level = int(alert_system.level)
        except:
            alert_level = 0
        self._selection = (self.selected_faction, self.selected_era, alert_level)
        print(f"Selection made: {self._selection}")
        self.accept()

    def selection(self) -> Optional[tuple]:
        return self._selection

def main():
    """Main launcher function"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Dark theme
    from PyQt6.QtGui import QColor
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(0, 0, 0))
    palette.setColor(palette.ColorRole.WindowText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    print("Starting LCARS Launcher...")
    
    try:
        launcher = FactionDialog(DEFAULT_FACTIONS, DEFAULT_ERAS)
        launcher.show()
        
        if launcher.exec() == QDialog.DialogCode.Accepted:
            selection = launcher.selection()
            if selection:
                faction, era, alert_level = selection
                print(f"Launching: {faction} {era} (Alert: {alert_level})")
                
                # Launch appropriate desktop
                if era == "22nd":
                    from desktop_22nd import PCARS22Desktop
                    desktop = PCARS22Desktop()
                    desktop.show()
                    sys.exit(app.exec())
                else:
                    print(f"Desktop for {era} not implemented yet")
        else:
            print("Launcher cancelled")
            
    except Exception as e:
        print(f"Error in launcher: {e}")
        import traceback
        traceback.print_exc()
    
    sys.exit(0)

if __name__ == "__main__":
    main()
