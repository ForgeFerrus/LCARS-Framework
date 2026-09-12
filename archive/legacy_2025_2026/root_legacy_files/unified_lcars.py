"""
Unified LCARS System - Single Chain Boot Sequence
"""
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (QApplication, QDialog, QMainWindow, QWidget, 
                            QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                            QPushButton, QFrame, QProgressBar, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEventLoop
from PyQt6.QtGui import QFont, QColor, QPalette

# Import existing LCARS components
from lcars.themes.lcars_palette import (
    LCARSEra, get_theme, get_random_button_color,
    get_lcars_font_style, LCARSColorGenerator
)
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, ScanningBar
from lcars.modules.sound_manager import get_sound_manager

class UnifiedLCARSSystem(QDialog):
    """Single unified LCARS system with chained boot sequence"""
    
    def __init__(self):
        super().__init__()
        self.era = LCARSEra.LCARS_25TH
        self.faction = "FEDERATION"
        self.color_gen = LCARSColorGenerator(self.era)
        self.theme = get_theme(self.era)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(0, 0, QApplication.primaryScreen().size().width(), 
                        QApplication.primaryScreen().size().height())
        
        self.current_phase = "boot"
        # node_phase used by cycle_nodes() — initialize to a safe default
        self.node_phase = 0
        self.setup_ui()
        self.start_unified_sequence()
        
    def setup_ui(self):
        self.setStyleSheet("background-color: black;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main container
        self.container = QWidget()
        self.container.setFixedSize(1200, 700)
        layout.addWidget(self.container)
        
        # Center container
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(self.container)
        h_center.addStretch()
        layout.addLayout(h_center)
        
        # Stacked widget for different phases
        self.stack = QStackedWidget()
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.stack)
        
        # Phase 1: Boot Screen
        self.boot_widget = self.create_boot_screen()
        self.stack.addWidget(self.boot_widget)
        
        # Phase 2: Login Screen  
        self.login_widget = self.create_login_screen()
        self.stack.addWidget(self.login_widget)
        
        # Phase 3: Launcher Screen
        self.launcher_widget = self.create_launcher_screen()
        self.stack.addWidget(self.launcher_widget)
        
        # Phase 4: Desktop Screen
        self.desktop_widget = self.create_desktop_screen()
        self.stack.addWidget(self.desktop_widget)
        
    def create_boot_screen(self):
        """Create boot phase"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.boot_elb = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        self.boot_elb.setFixedSize(200, 70)
        header.addWidget(self.boot_elb)
        
        self.boot_title = QFrame()
        self.boot_title.setFixedHeight(70)
        self.boot_title.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
        title_layout = QHBoxLayout(self.boot_title)
        title_lbl = QLabel("◢ LCARS SYSTEM - INITIALIZATION")
        title_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(24, 'normal')}")
        title_layout.addWidget(title_lbl)
        header.addWidget(self.boot_title, 1)
        
        self.boot_cap = QFrame()
        self.boot_cap.setFixedSize(60, 70)
        self.boot_cap.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-right-radius: 35px; border-bottom-right-radius: 4px;")
        header.addWidget(self.boot_cap)
        layout.addLayout(header)
        
        # Main boot area
        main = QHBoxLayout()
        main.setSpacing(4)
        
        boot_sidebar = QFrame()
        boot_sidebar.setFixedWidth(200)
        boot_sidebar.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px; border-bottom-left-radius: 80px;")
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
        self.boot_footer.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-bottom-right-radius: 20px; border-top-right-radius: 4px;")
        layout.addWidget(self.boot_footer)
        
        return widget
        
    def create_login_screen(self):
        """Create login phase"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.login_elb = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        self.login_elb.setFixedSize(180, 60)
        header.addWidget(self.login_elb)
        
        self.login_title = QFrame()
        self.login_title.setFixedHeight(60)
        self.login_title.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
        title_layout = QHBoxLayout(self.login_title)
        title_layout.setContentsMargins(20, 0, 0, 0)
        title_lbl = QLabel("◢ AUTHORIZATION PROTOCOL // SECURE ACCESS")
        title_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'normal')}")
        title_layout.addWidget(title_lbl)
        header.addWidget(self.login_title, 1)
        
        self.login_cap = QFrame()
        self.login_cap.setFixedSize(40, 60)
        self.login_cap.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-right-radius: 20px; border-bottom-right-radius: 4px;")
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
        self.login_sidebar.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px; border-bottom-left-radius: 60px;")
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
        
        self.login_progress = ScanningBar(get_random_button_color(self.era), self)
        self.login_progress.setFixedHeight(25)
        content.addWidget(self.login_progress)
        
        content.addStretch()
        
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.login_btn = LCARSButton("AUTHORIZE", get_random_button_color(self.era), era=self.era, shape="rect", auto_cycle=True)
        self.login_btn.setFixedSize(180, 50)
        self.login_btn.clicked.connect(self.complete_login)
        btn_box.addWidget(self.login_btn)
        content.addLayout(btn_box)
        
        main.addLayout(content, 1)
        layout.addLayout(main, 1)
        
        # Footer
        self.login_footer = QFrame()
        self.login_footer.setFixedHeight(30)
        self.login_footer.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-bottom-right-radius: 15px; border-top-right-radius: 4px;")
        layout.addWidget(self.login_footer)
        
        return widget
        
    def create_launcher_screen(self):
        """Create launcher phase"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.launcher_elb = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        self.launcher_elb.setFixedSize(220, 80)
        header.addWidget(self.launcher_elb)
        
        self.launcher_title = QFrame()
        self.launcher_title.setFixedHeight(80)
        self.launcher_title.setStyleSheet("background-color: #99FFFF; border-radius: 4px;")
        title_layout = QHBoxLayout(self.launcher_title)
        title_layout.setContentsMargins(25, 0, 0, 0)
        title_lbl = QLabel("◢ SYSTEM ACCESS // TEMPORAL ALIGNMENT")
        title_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(24, 'normal')}")
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
        self.alert_btn = LCARSButton("RED ALERT", "#D80000", era=self.era, shape="rect", auto_cycle=False)
        self.alert_btn.setFixedSize(220, 60)
        sidebar.addWidget(self.alert_btn)
        
        main.addLayout(sidebar)
        
        # Content area
        content = QVBoxLayout()
        content.setContentsMargins(40, 20, 20, 20)
        content.setSpacing(20)
        
        # Stardate
        stardate = time.strftime("%Y.%m.%d")
        self.launcher_info = QLabel(f"STARDATE: {stardate} // {self.faction} SECTOR")
        self.launcher_info.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(28, 'normal')}")
        content.addWidget(self.launcher_info)
        
        # Faction selection
        faction_grid = QGridLayout()
        faction_grid.setSpacing(20)
        
        factions = [
            ("FEDERATION", "#4BBEBF"),
            ("KLINGON", "#D80000"),
            ("ROMULAN", "#006633"),
            ("CARDASSIAN", "#CC9966")
        ]
        
        for i, (faction, color) in enumerate(factions):
            btn = LCARSButton(faction, color, era=self.era, shape="rect", auto_cycle=True)
            btn.setFixedSize(250, 120)
            btn.clicked.connect(lambda checked, f=faction: self.select_faction(f))
            faction_grid.addWidget(btn, i // 2, i % 2)
        
        content.addLayout(faction_grid)
        
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
            btn = LCARSButton(display, get_random_button_color(era), era=era, shape="rect", auto_cycle=True)
            btn.setFixedSize(200, 60)
            btn.clicked.connect(lambda checked, e=era: self.select_era(e))
            era_grid.addWidget(btn, i // 3, i % 3)
        
        content.addLayout(era_grid)
        
        # Launch button
        launch_btn = LCARSButton("LAUNCH SYSTEM", "#00FF00", era=self.era, shape="rect", auto_cycle=False)
        launch_btn.setFixedSize(300, 60)
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
        
        # Start node animation
        self.node_timer = QTimer()
        self.node_timer.timeout.connect(self.cycle_nodes)
        self.node_timer.start(4000)
        
        return widget
        
    def create_desktop_screen(self):
        """Create desktop phase"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(4)
        
        desktop_elb = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        desktop_elb.setFixedSize(250, 80)
        header.addWidget(desktop_elb)
        
        title_panel = QFrame()
        title_panel.setFixedHeight(80)
        title_panel.setStyleSheet("background-color: #99FFFF; border-radius: 4px;")
        title_layout = QHBoxLayout(title_panel)
        title = QLabel(f"USS ENTERPRISE - {self.faction} {self.era.value}")
        title.setStyleSheet(f"color: black; {get_lcars_font_style(28, 'normal')}")
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
        
        controls = [
            ("DASHBOARD", get_random_button_color(self.era)),
            ("TACTICAL", "#D80000"),
            ("SCIENCE", get_random_button_color(self.era)),
            ("ENGINEERING", get_random_button_color(self.era)),
            ("COMMUNICATIONS", get_random_button_color(self.era))
        ]
        
        for control, color in controls:
            btn = LCARSButton(control, color, era=self.era, shape="rect", auto_cycle=True)
            btn.setFixedSize(250, 60)
            left_panel.addWidget(btn)
        
        left_panel.addStretch(1)
        
        bottom_elbow = LCARSElbow("bottom-left", era=self.era, auto_cycle=False)
        bottom_elbow.setFixedSize(250, 80)
        left_panel.addWidget(bottom_elbow)
        
        interface.addLayout(left_panel)
        
        # Center display
        center = QVBoxLayout()
        center.setContentsMargins(20, 20, 20, 20)
        center.setSpacing(15)
        
        # Main status
        status_panel = QFrame()
        status_panel.setFixedHeight(120)
        status_panel.setStyleSheet("background-color: #4BBEBF; border-radius: 4px;")
        status_layout = QVBoxLayout(status_panel)
        
        status_title = QLabel("MAIN SYSTEMS STATUS")
        status_title.setStyleSheet(f"color: black; {get_lcars_font_style(24, 'normal')}")
        status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_title)
        
        status_info = QLabel("ALL SYSTEMS OPERATIONAL - GREEN ALERT")
        status_info.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'normal')}")
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
            panel.setStyleSheet(f"background-color: {get_random_button_color(self.era)}; border-radius: 4px;")
            panel_layout = QVBoxLayout(panel)
            
            system_label = QLabel(system)
            system_label.setStyleSheet(f"color: black; {get_lcars_font_style(16, 'normal')}")
            system_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            panel_layout.addWidget(system_label)
            
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: black; {get_lcars_font_style(14, 'normal')}")
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
        
        left_status = LCARSElbow("bottom-left", era=self.era, auto_cycle=False)
        left_status.setFixedSize(300, 50)
        footer.addWidget(left_status)
        
        center_status = QFrame()
        center_status.setFixedHeight(50)
        center_status.setStyleSheet("background-color: #2A7193; border-radius: 4px;")
        center_layout = QHBoxLayout(center_status)
        status_text = QLabel(f"STARDATE: {int(time.time()) % 100000} - SYSTEM READY")
        status_text.setStyleSheet(f"color: #99FFFF; {get_lcars_font_style(16, 'normal')}")
        center_layout.addWidget(status_text)
        footer.addWidget(center_status, 1)
        
        right_status = QFrame()
        right_status.setFixedSize(150, 50)
        right_status.setStyleSheet("background-color: #9EA5BA; border-bottom-right-radius: 25px; border-top-right-radius: 4px;")
        footer.addWidget(right_status)
        
        layout.addLayout(footer)
        
        return widget
        
    def start_unified_sequence(self):
        """Start the unified boot sequence"""
        self.current_phase = "boot"
        self.stack.setCurrentIndex(0)  # Show boot screen
        self.start_boot_sequence()
        
    def start_boot_sequence(self):
        """Start boot phase"""
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
        
        self.boot_progress = 0
        self.boot_timer = QTimer()
        self.boot_timer.timeout.connect(self.update_boot)
        self.boot_timer.start(800)
        get_sound_manager().play("acknowledge")
        
    def update_boot(self):
        """Update boot progress"""
        if self.boot_progress < len(self.boot_steps):
            step_text = self.boot_steps[self.boot_progress]
            self.boot_step.setText(step_text)
            self.boot_log.setText(f"{self.boot_log.text()}\n> {step_text.split(':')[0]} :: ONLINE")
            get_sound_manager().play("click")
            
            # Update colors
            self.boot_elb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
            self.boot_title.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
            
            self.boot_progress += 1
        else:
            self.boot_timer.stop()
            get_sound_manager().play("ready")
            QTimer.singleShot(1500, self.transition_to_login)
            
    def transition_to_login(self):
        """Transition to login phase"""
        self.current_phase = "login"
        self.stack.setCurrentIndex(1)  # Show login screen
        QTimer.singleShot(2000, self.start_login)
        
    def start_login(self):
        """Start login phase"""
        self.login_status.setText("SCANNING BIOMETRICS... [MATCH CONFIRMED]")
        get_sound_manager().play("acknowledge")
        QTimer.singleShot(2000, self.transition_to_launcher)
        
    def complete_login(self):
        """Complete login manually"""
        self.login_status.setText("SCANNING BIOMETRICS... [MATCH CONFIRMED]")
        get_sound_manager().play("acknowledge")
        QTimer.singleShot(1500, self.transition_to_launcher)
        
    def transition_to_launcher(self):
        """Transition to launcher phase"""
        self.current_phase = "launcher"
        self.stack.setCurrentIndex(2)  # Show launcher screen
        get_sound_manager().play("ready")
        
    def select_faction(self, faction):
        """Handle faction selection"""
        get_sound_manager().play("acknowledge")
        self.faction = faction
        stardate = time.strftime("%Y.%m.%d")
        self.launcher_info.setText(f"STARDATE: {stardate} // {faction} SECTOR")
        
    def select_era(self, era):
        """Handle era selection"""
        get_sound_manager().play("acknowledge")
        self.era = era
        self.color_gen = LCARSColorGenerator(era)
        self.theme = get_theme(era)
        
    def cycle_nodes(self):
        """Animate launcher nodes"""
        if self.current_phase != "launcher":
            return
        palette = self.theme.get('palette', ["#4BBEBF", "#3366CC", "#FFCC33", "#CC6633"])
        for i, node in enumerate(reversed(self.launcher_nodes)):
            idx = (self.node_phase + i) % len(palette)
            node.setStyleSheet(f"background-color: {palette[idx]}; border-radius: 2px;")
        self.node_phase = (self.node_phase + 1) % len(palette)
        
    def launch_desktop(self):
        """Launch desktop phase"""
        get_sound_manager().play("ready")
        self.current_phase = "desktop"
        self.stack.setCurrentIndex(3)  # Show desktop screen
        
    def show(self):
        """Center and show"""
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)
        super().show()

def main():
    print("=== UNIFIED LCARS SYSTEM INITIALIZATION ===")
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Initialize sound manager
    sound_mgr = get_sound_manager()
    
    # Create and show unified system
    system = UnifiedLCARSSystem()
    system.show()
    
    print("=== LCARS SYSTEM FULLY OPERATIONAL ===")
    app.exec()

if __name__ == "__main__":
    main()
