"""
Complete LCARS System with Full Boot Sequence
"""
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (QApplication, QDialog, QMainWindow, QWidget, 
                            QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                            QPushButton, QFrame, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QPalette

from lcars.themes.lcars_palette import LCARSEra, get_theme, get_era_palette

class LCARSThemeManager:
    def __init__(self):
        self.current_era = LCARSEra.LCARS_25TH
        self.current_faction = None
        self.theme = get_theme(self.current_era)
        
    def set_era(self, era):
        # Accept either enum member or string key like 'LCARS_25TH'
        try:
            if isinstance(era, str):
                era_enum = LCARSEra[era]
            elif isinstance(era, LCARSEra):
                era_enum = era
            else:
                era_enum = None
        except Exception:
            era_enum = None

        if era_enum:
            self.current_era = era_enum
            self.theme = get_theme(self.current_era)
            
    def get_color(self, element):
        return self.theme.get(element, "#FFFFFF")
        
    def apply_faction_theme(self, faction):
        faction_overrides = {
            "KLINGON": {"primary": "#8B0000", "warning": "#FF4500"},
            "ROMULAN": {"primary": "#4B0082", "accent": "#DDA0DD"},
            "CARDASSIAN": {"primary": "#8B4513", "secondary": "#D2691E"}
        }
        if faction in faction_overrides:
            self.theme.update(faction_overrides[faction])

class LCARSBootScreen(QDialog):
    """Authentic LCARS boot sequence"""
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(0, 0, QApplication.primaryScreen().size().width(), 
                        QApplication.primaryScreen().size().height())
        
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
        
        self.current_step = 0
        self.setup_ui()
        self.start_boot_sequence()
        
    def setup_ui(self):
        self.setStyleSheet(f"background-color: {self.theme_manager.get_color('background')};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(100, 100, 100, 100)
        
        # Main boot display
        self.main_display = QFrame()
        self.main_display.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme_manager.get_color('primary')};
                border-radius: 10px;
                border: 2px solid {self.theme_manager.get_color('accent')};
            }}
        """)
        self.main_display.setFixedHeight(400)
        
        display_layout = QVBoxLayout(self.main_display)
        display_layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("LCARS SYSTEM BOOT")
        title.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('text_primary')};
                font-size: 36px;
                font-weight: bold;
                text-transform: uppercase;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display_layout.addWidget(title)
        
        display_layout.addStretch()
        
        # Boot status
        self.boot_status = QLabel("INITIALIZING...")
        self.boot_status.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('text_primary')};
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        self.boot_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display_layout.addWidget(self.boot_status)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {self.theme_manager.get_color('accent')};
                border-radius: 5px;
                text-align: center;
                color: {self.theme_manager.get_color('text_primary')};
                background-color: {self.theme_manager.get_color('primary')};
            }}
            QProgressBar::chunk {{
                background-color: {self.theme_manager.get_color('success')};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.setRange(0, len(self.boot_steps))
        self.progress_bar.setValue(0)
        display_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.main_display, 1)
        
        # System status panel
        status_panel = QFrame()
        status_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme_manager.get_color('secondary')};
                border-radius: 5px;
                border: 1px solid {self.theme_manager.get_color('accent')};
            }}
        """)
        status_panel.setFixedHeight(100)
        
        status_layout = QHBoxLayout(status_panel)
        
        self.system_status = QLabel("SYSTEM STATUS: INITIALIZING")
        self.system_status.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('text_primary')};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        status_layout.addWidget(self.system_status)
        
        layout.addWidget(status_panel)
        
    def start_boot_sequence(self):
        self.boot_timer = QTimer()
        self.boot_timer.timeout.connect(self.update_boot)
        self.boot_timer.start(800)
        
    def update_boot(self):
        if self.current_step < len(self.boot_steps):
            step_text = self.boot_steps[self.current_step]
            self.boot_status.setText(step_text)
            self.progress_bar.setValue(self.current_step + 1)
            
            # Update system status
            if self.current_step < len(self.boot_steps) - 1:
                self.system_status.setText(f"SYSTEM STATUS: {step_text.split(':')[0]}")
            else:
                self.system_status.setText("SYSTEM STATUS: READY")
                
            self.current_step += 1
        else:
            self.boot_timer.stop()
            QTimer.singleShot(1000, self.boot_complete)
            
    def boot_complete(self):
        self.accept()

class LCARSLoginScreen(QDialog):
    """LCARS system login"""
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(200, 200, 800, 600)
        
        # Center on screen
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)
            
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet(f"background-color: {self.theme_manager.get_color('background')};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Login panel
        login_panel = QFrame()
        login_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme_manager.get_color('primary')};
                border-radius: 10px;
                border: 2px solid {self.theme_manager.get_color('accent')};
            }}
        """)
        
        panel_layout = QVBoxLayout(login_panel)
        panel_layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("STARFLEET AUTHENTICATION")
        title.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('text_primary')};
                font-size: 28px;
                font-weight: bold;
                text-transform: uppercase;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(title)
        
        panel_layout.addStretch()
        
        # Login fields
        username_label = QLabel("OFFICER ID:")
        username_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('text_primary')};
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        panel_layout.addWidget(username_label)
        
        # Auto-login for demo
        self.login_status = QLabel("AUTHENTICATING OFFICER...")
        self.login_status.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('text_primary')};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        self.login_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(self.login_status)
        
        panel_layout.addStretch()
        
        layout.addWidget(login_panel)
        
        # Auto-login after delay
        QTimer.singleShot(2000, self.auto_login)
        
    def auto_login(self):
        self.login_status.setText("ACCESS GRANTED - WELCOME, COMMANDER")
        QTimer.singleShot(1500, self.accept)

class LCARSLauncher(QDialog):
    """Main launcher with faction/era selection"""
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(100, 100, 1200, 800)
        
        # Center on screen
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)
        
        self.selected_faction = "FEDERATION"
        self.selected_era = "LCARS_25TH"
        self._selection = None
        
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet(f"background-color: {self.theme_manager.get_color('background')};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Header
        header = QHBoxLayout()
        
        elbow_left = self.create_elbow("tl", 200, 70)
        header.addWidget(elbow_left)
        
        title_panel = self.create_panel(self.theme_manager.get_color('secondary'), 70)
        title_layout = QHBoxLayout(title_panel)
        title = QLabel("CONFIGURATION SELECTION")
        title.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('text_primary')};
                font-size: 24px;
                font-weight: bold;
                text-transform: uppercase;
            }}
        """)
        title_layout.addWidget(title)
        header.addWidget(title_panel, 1)
        
        right_cap = self.create_elbow("tr", 60, 70)
        header.addWidget(right_cap)
        
        layout.addLayout(header)
        
        # Main content
        content = QHBoxLayout()
        
        # Sidebar
        sidebar = QVBoxLayout()
        
        main_sidebar = QFrame()
        main_sidebar.setFixedWidth(200)
        main_sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme_manager.get_color('secondary')};
                border-bottom-left-radius: 80px;
                border-top-left-radius: 4px;
            }}
        """)
        sidebar.addWidget(main_sidebar, 1)
        
        # Status buttons
        for i in range(6):
            btn = QPushButton(f"NODE {i+1:02d}")
            btn.setFixedSize(200, 40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme_manager.get_color('accent')};
                    color: {self.theme_manager.get_color('text_primary')};
                    border: none;
                    font-size: 14px;
                    font-weight: bold;
                }}
            """)
            sidebar.addWidget(btn)
        
        sidebar.addStretch(1)
        
        bottom_elbow = self.create_elbow("bl", 200, 60)
        sidebar.addWidget(bottom_elbow)
        
        content.addLayout(sidebar)
        
        # Selection area
        center = QVBoxLayout()
        center.setContentsMargins(40, 20, 40, 20)
        
        # Era selection
        era_label = QLabel("SELECT TEMPORAL ERA")
        era_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('secondary')};
                font-size: 20px;
                font-weight: bold;
                text-transform: uppercase;
            }}
        """)
        era_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addWidget(era_label)
        
        era_grid = QGridLayout()
        era_grid.setSpacing(20)
        
        eras = [
            ("COMS 22ND", "COMS_22ND"),
            ("PCARS 23RD", "PCARS_23RD"), 
            ("LCARS 24TH", "LCARS_24TH"),
            ("LCARS 25TH", "LCARS_25TH"),
            ("TCARS 29TH", "TCARS_29TH")
        ]
        
        for i, (display_name, era_key) in enumerate(eras):
            btn = QPushButton(display_name)
            btn.setFixedSize(200, 80)
            # map era key to enum and theme
            try:
                era_enum = LCARSEra[era_key]
                era_theme = get_theme(era_enum)
                bg_color = era_theme.get('palette', [era_theme.get('accent')])[0]
                text_color = era_theme.get('text', '#FFFFFF')
            except Exception:
                bg_color = '#444444'
                text_color = '#FFFFFF'

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: none;
                    font-size: 14px;
                    font-weight: bold;
                    text-transform: uppercase;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: #FFFFFF;
                    color: {bg_color};
                }}
            """)
            btn.clicked.connect(lambda checked, e=era_key: self.select_era(e))
            era_grid.addWidget(btn, i // 3, i % 2)
        
        center.addLayout(era_grid)
        
        # Faction selection
        faction_label = QLabel("SELECT FACTION ALIGNMENT")
        faction_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('secondary')};
                font-size: 20px;
                font-weight: bold;
                text-transform: uppercase;
            }}
        """)
        faction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addWidget(faction_label)
        
        faction_layout = QHBoxLayout()
        
        factions = [
            ("FEDERATION", "#4169E1"),
            ("KLINGON", "#8B0000"),
            ("ROMULAN", "#4B0082"),
            ("CARDASSIAN", "#8B4513")
        ]
        
        for faction, color in factions:
            btn = QPushButton(faction)
            btn.setFixedSize(150, 80)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: #FFFFFF;
                    border: none;
                    font-size: 14px;
                    font-weight: bold;
                    text-transform: uppercase;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: #FFFFFF;
                    color: {color};
                }}
            """)
            btn.clicked.connect(lambda checked, f=faction: self.select_faction(f))
            faction_layout.addWidget(btn)
        
        center.addLayout(faction_layout)
        center.addStretch()
        
        content.addLayout(center, 1)
        layout.addLayout(content)
        
        # Launch button
        launch_btn = QPushButton("LAUNCH SYSTEM")
        launch_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_manager.get_color('success')};
                color: {self.theme_manager.get_color('text_primary')};
                border: none;
                font-size: 18px;
                font-weight: bold;
                text-transform: uppercase;
                padding: 15px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #FFFFFF;
                color: {self.theme_manager.get_color('success')};
            }}
        """)
        launch_btn.clicked.connect(self.launch_system)
        layout.addWidget(launch_btn)
        
    def create_elbow(self, orientation, width, height):
        elbow = QFrame()
        elbow.setFixedSize(width, height)
        
        border_radius = ""
        if orientation == "tl":
            border_radius = "border-top-left-radius: 50px; border-bottom-left-radius: 4px;"
        elif orientation == "tr":
            border_radius = "border-top-right-radius: 35px; border-bottom-right-radius: 4px;"
        elif orientation == "bl":
            border_radius = "border-bottom-left-radius: 40px; border-top-left-radius: 6px;"
            
        elbow.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme_manager.get_color('primary')};
                border: none;
                {border_radius}
            }}
        """)
        return elbow
        
    def create_panel(self, color, height):
        panel = QFrame()
        panel.setFixedHeight(height)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                border-radius: 4px;
            }}
        """)
        return panel
        
    def select_era(self, era):
        self.selected_era = era
        self.theme_manager.set_era(era)
        
    def select_faction(self, faction):
        self.selected_faction = faction
        self.theme_manager.apply_faction_theme(faction)
        
    def launch_system(self):
        self._selection = (self.selected_faction, self.selected_era, 0)
        self.accept()
        
    def get_selection(self):
        return self._selection

class LCARSDesktop(QMainWindow):
    """Main desktop interface"""
    def __init__(self, theme_manager, faction, era):
        super().__init__()
        self.theme_manager = theme_manager
        self.faction = faction
        self.era = era
        
        self.setWindowTitle(f"LCARS Desktop - {faction} {era}")
        self.setGeometry(50, 50, 1600, 1000)
        self.setStyleSheet(f"background-color: {self.theme_manager.get_color('background')};")
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Header
        header = QHBoxLayout()
        
        elbow_left = self.create_elbow("tl", 250, 80)
        header.addWidget(elbow_left)
        
        title_panel = self.create_panel(self.theme_manager.get_color('secondary'), 80)
        title_layout = QHBoxLayout(title_panel)
        title = QLabel(f"USS ENTERPRISE - {self.faction} {self.era}")
        title.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('text_primary')};
                font-size: 28px;
                font-weight: bold;
                text-transform: uppercase;
            }}
        """)
        title_layout.addWidget(title)
        header.addWidget(title_panel, 1)
        
        right_cap = self.create_elbow("tr", 80, 80)
        header.addWidget(right_cap)
        
        layout.addLayout(header)
        
        # Main interface
        interface = QHBoxLayout()
        
        # Left control panel
        left_panel = QVBoxLayout()
        
        main_left = QFrame()
        main_left.setFixedWidth(250)
        main_left.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme_manager.get_color('secondary')};
                border-bottom-left-radius: 100px;
                border-top-left-radius: 4px;
            }}
        """)
        left_panel.addWidget(main_left, 1)
        
        controls = [
            ("DASHBOARD", self.theme_manager.get_color('accent')),
            ("TACTICAL", self.theme_manager.get_color('alert')),
            ("SCIENCE", self.theme_manager.get_color('primary')),
            ("ENGINEERING", self.theme_manager.get_color('warning')),
            ("COMMUNICATIONS", self.theme_manager.get_color('success'))
        ]
        
        for control, color in controls:
            btn = QPushButton(control)
            btn.setFixedSize(250, 60)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {self.theme_manager.get_color('text_primary')};
                    border: none;
                    font-size: 14px;
                    font-weight: bold;
                    text-transform: uppercase;
                }}
            """)
            left_panel.addWidget(btn)
        
        left_panel.addStretch(1)
        
        bottom_elbow = self.create_elbow("bl", 250, 80)
        left_panel.addWidget(bottom_elbow)
        
        interface.addLayout(left_panel)
        
        # Center display
        center = QVBoxLayout()
        center.setContentsMargins(20, 20, 20, 20)
        
        # Main status
        status_panel = self.create_panel(self.theme_manager.get_color('primary'), 120)
        status_layout = QVBoxLayout(status_panel)
        
        status_title = QLabel("MAIN SYSTEMS STATUS")
        status_title.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('text_primary')};
                font-size: 24px;
                font-weight: bold;
                text-transform: uppercase;
            }}
        """)
        status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_title)
        
        status_info = QLabel("ALL SYSTEMS OPERATIONAL - GREEN ALERT")
        status_info.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('text_primary')};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
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
            panel = self.create_panel(self.theme_manager.get_color('accent'), 80)
            panel_layout = QVBoxLayout(panel)
            
            system_label = QLabel(system)
            system_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.theme_manager.get_color('text_primary')};
                    font-size: 16px;
                    font-weight: bold;
                }}
            """)
            system_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            panel_layout.addWidget(system_label)
            
            status_label = QLabel(status)
            status_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.theme_manager.get_color('text_primary')};
                    font-size: 14px;
                    font-weight: bold;
                }}
            """)
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            panel_layout.addWidget(status_label)
            
            systems_grid.addWidget(panel, i // 2, i % 2)
        
        center.addLayout(systems_grid)
        center.addStretch()
        
        interface.addLayout(center, 1)
        layout.addLayout(interface)
        
        # Bottom status bar
        bottom = QHBoxLayout()
        
        left_status = self.create_elbow("bl", 300, 50)
        bottom.addWidget(left_status)
        
        center_status = self.create_panel(self.theme_manager.get_color('secondary'), 50)
        center_layout = QHBoxLayout(center_status)
        status_text = QLabel(f"STARDATE: {int(time.time()) % 100000} - SYSTEM READY")
        status_text.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_manager.get_color('text_primary')};
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        center_layout.addWidget(status_text)
        bottom.addWidget(center_status, 1)
        
        right_status = self.create_elbow("br", 150, 50)
        bottom.addWidget(right_status)
        
        layout.addLayout(bottom)
        
    def create_elbow(self, orientation, width, height):
        elbow = QFrame()
        elbow.setFixedSize(width, height)
        
        border_radius = ""
        if orientation == "tl":
            border_radius = "border-top-left-radius: 50px; border-bottom-left-radius: 4px;"
        elif orientation == "tr":
            border_radius = "border-top-right-radius: 35px; border-bottom-right-radius: 4px;"
        elif orientation == "bl":
            border_radius = "border-bottom-left-radius: 40px; border-top-left-radius: 6px;"
        elif orientation == "br":
            border_radius = "border-bottom-right-radius: 40px; border-top-right-radius: 6px;"
            
        elbow.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme_manager.get_color('primary')};
                border: none;
                {border_radius}
            }}
        """)
        return elbow
        
    def create_panel(self, color, height):
        panel = QFrame()
        panel.setFixedHeight(height)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                border-radius: 4px;
            }}
        """)
        return panel

def main():
    print("=== COMPLETE LCARS SYSTEM INITIALIZATION ===")
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Initialize theme manager
    theme_manager = LCARSThemeManager()

    # Step 1: Boot sequence
    print("Step 1: System Boot...")
    boot_screen = LCARSBootScreen(theme_manager)
    boot_screen.show()

    if boot_screen.exec() == QDialog.DialogCode.Accepted:
        print("Boot complete")

        # Step 2: Login
        print("Step 2: Authentication...")
        login_screen = LCARSLoginScreen(theme_manager)
        login_screen.show()

        if login_screen.exec() == QDialog.DialogCode.Accepted:
            print("Authentication successful")

            # Step 3: Configuration selection
            print("Step 3: Configuration Selection...")
            launcher = LCARSLauncher(theme_manager)
            launcher.show()

            if launcher.exec() == QDialog.DialogCode.Accepted:
                selection = launcher.get_selection()
                if selection:
                    faction, era, _ = selection
                    print(f"Configuration selected: {faction} {era}")

                    # Step 4: Main desktop
                    print("Step 4: Launching Main Desktop...")
                    desktop = LCARSDesktop(theme_manager, faction, era)
                    desktop.show()

                    print("=== LCARS SYSTEM FULLY OPERATIONAL ===")
                    app.exec()
            else:
                print("Configuration cancelled")
        else:
            print("Authentication failed")
    else:
        print("Boot failed")

if __name__ == "__main__":
    main()
