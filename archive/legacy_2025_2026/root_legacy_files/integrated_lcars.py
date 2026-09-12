"""
Integrated LCARS System using existing palette and component architecture
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
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEventLoop
from PyQt6.QtGui import QFont, QColor, QPalette

# Import existing LCARS components
from lcars.themes.lcars_palette import (
    LCARSEra, get_theme, get_random_button_color,
    get_lcars_font_style, LCARSColorGenerator
)
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, ScanningBar
from lcars.modules.sound_manager import get_sound_manager

class IntegratedBootView(QWidget):
    """Authentic LCARS Boot Sequence using existing architecture"""
    finished = pyqtSignal()
    
    def __init__(self, era=LCARSEra.LCARS_25TH):
        super().__init__()
        self.era = era
        self.color_gen = LCARSColorGenerator(era)
        self.progress = 0
        
        self.steps = [
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
        
        self.setup_ui()
        self.start_boot_sequence()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Main container with LCARS styling
        container = QWidget()
        container.setFixedSize(1000, 600)
        c_lay = QVBoxLayout(container)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(4)
        
        # --- HEADER ---
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.h_elb = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        self.h_elb.setFixedSize(200, 70)
        header.addWidget(self.h_elb)
        
        self.title_fr = QFrame()
        self.title_fr.setFixedHeight(70)
        self.title_fr.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
        tl_lay = QHBoxLayout(self.title_fr)
        lbl = QLabel("◢ LCARS SYSTEM - INITIALIZATION")
        lbl.setStyleSheet(f"color: black; {get_lcars_font_style(24, 'normal')}")
        tl_lay.addWidget(lbl)
        header.addWidget(self.title_fr, 1)
        
        self.h_cap = QFrame()
        self.h_cap.setFixedSize(60, 70)
        self.h_cap.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-right-radius: 35px; border-bottom-right-radius: 4px;")
        header.addWidget(self.h_cap)
        c_lay.addLayout(header)

        # --- MID ---
        mid = QHBoxLayout()
        mid.setSpacing(4)
        
        self.sb = QFrame()
        self.sb.setFixedWidth(200)
        self.sb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px; border-bottom-left-radius: 80px;")
        mid.addWidget(self.sb)
        
        term = QVBoxLayout()
        term.setContentsMargins(20, 10, 10, 10)
        self.step_lbl = QLabel("INITIALIZING...")
        self.step_lbl.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(24, 'normal')}")
        term.addWidget(self.step_lbl)
        
        self.log = QLabel("> BOOT_MODE: NOMINAL")
        self.log.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(16, 'normal')}")
        self.log.setWordWrap(True)
        term.addWidget(self.log)
        term.addStretch()
        
        mid.addLayout(term, 1)
        c_lay.addLayout(mid, 1)

        # --- FOOTER ---
        self.footer = QFrame()
        self.footer.setFixedHeight(40)
        self.footer.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-bottom-right-radius: 20px; border-top-right-radius: 4px;")
        c_lay.addWidget(self.footer)

        # Centering
        self.layout.addStretch()
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(container)
        h_center.addStretch()
        self.layout.addLayout(h_center)
        self.layout.addStretch()
        
    def start_boot_sequence(self):
        self.boot_timer = QTimer()
        self.boot_timer.timeout.connect(self.update_boot)
        self.boot_timer.start(800)
        get_sound_manager().play("acknowledge")
        
    def update_boot(self):
        self.progress += 1
        
        if self.progress < len(self.steps):
            step_text = self.steps[self.progress]
            self.step_lbl.setText(step_text)
            self.log.setText(f"{self.log.text()}\n> {step_text.split(':')[0]} :: ONLINE")
            get_sound_manager().play("click")
            
            # Subtly shift atmospheric colors (LCARS Panel Flicker)
            self.h_elb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
            self.title_fr.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
        else:
            self.boot_timer.stop()
            get_sound_manager().play("ready")
            QTimer.singleShot(1000, self.boot_complete)
            
    def boot_complete(self):
        self.finished.emit()

class IntegratedLoginView(QWidget):
    """LCARS Login using existing architecture"""
    finished = pyqtSignal()
    
    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__()
        self.era = era
        self.faction = faction
        self.color_gen = LCARSColorGenerator(era)
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Main container
        container = QWidget()
        container.setFixedSize(800, 500)
        container.setStyleSheet("background: black;")
        c_lay = QVBoxLayout(container)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(4)
        
        # --- HEADER ---
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.h_elb = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        self.h_elb.setFixedSize(180, 60)
        header.addWidget(self.h_elb)
        
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(60)
        self.title_bar.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
        tb_lay = QHBoxLayout(self.title_bar)
        tb_lay.setContentsMargins(20, 0, 0, 0)
        hdr_txt = QLabel("◢ AUTHORIZATION PROTOCOL // SECURE ACCESS")
        hdr_txt.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'normal')}")
        tb_lay.addWidget(hdr_txt)
        header.addWidget(self.title_bar, 1)
        
        self.h_cap = QFrame()
        self.h_cap.setFixedSize(40, 60)
        self.h_cap.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-right-radius: 20px; border-bottom-right-radius: 4px;")
        header.addWidget(self.h_cap)
        c_lay.addLayout(header)

        # --- MID AREA ---
        mid = QHBoxLayout()
        mid.setSpacing(10)
        
        # Left Sidebar
        sidebar = QVBoxLayout()
        sidebar.setSpacing(4)
        self.sb_block = QFrame()
        self.sb_block.setFixedSize(180, 200)
        self.sb_block.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px; border-bottom-left-radius: 60px;")
        sidebar.addWidget(self.sb_block)
        sidebar.addStretch()
        mid.addLayout(sidebar)
        
        # Main content area
        content = QVBoxLayout()
        content.setContentsMargins(30, 20, 30, 20)
        content.setSpacing(15)
        
        self.status_lbl = QLabel("PROTOCOL :: IDENTIFYING NEURAL PATTERN...")
        self.status_lbl.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(18, 'normal')}")
        content.addWidget(self.status_lbl)
        
        self.progress_bar = ScanningBar(get_random_button_color(self.era), self)
        self.progress_bar.setFixedHeight(25)
        content.addWidget(self.progress_bar)
        
        content.addStretch()
        
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.auth_btn = LCARSButton("AUTHORIZE", get_random_button_color(self.era), era=self.era, shape="rect", auto_cycle=True)
        self.auth_btn.setFixedSize(180, 50)
        self.auth_btn.clicked.connect(self.start_auth)
        btn_box.addWidget(self.auth_btn)
        content.addLayout(btn_box)
        
        mid.addLayout(content, 1)
        c_lay.addLayout(mid, 1)

        # --- FOOTER ---
        self.footer = QFrame()
        self.footer.setFixedHeight(30)
        self.footer.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-bottom-right-radius: 15px; border-top-right-radius: 4px;")
        c_lay.addWidget(self.footer)

        # Centering
        self.layout.addStretch()
        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(container)
        h_box.addStretch()
        self.layout.addLayout(h_box)
        self.layout.addStretch()
        
        # Auto-login for demo
        QTimer.singleShot(2000, self.start_auth)
        
    def start_auth(self):
        get_sound_manager().play("acknowledge")
        self.status_lbl.setText("SCANNING BIOMETRICS... [MATCH CONFIRMED]")
        QTimer.singleShot(2000, self.finish_auth)
        
    def finish_auth(self):
        get_sound_manager().play("ready")
        self.finished.emit()

class IntegratedLauncherView(QWidget):
    """Integrated launcher using existing LCARS architecture"""
    selected = pyqtSignal(str, str)
    
    def __init__(self, era=LCARSEra.LCARS_25TH):
        super().__init__()
        self.era = era
        self.faction = "FEDERATION"
        self.color_gen = LCARSColorGenerator(era)
        self.theme = get_theme(era)
        self.node_phase = 0
        self.setup_ui()
        
        # Node Shifting Algorithm
        self.node_timer = QTimer()
        self.node_timer.timeout.connect(self._cycle_nodes)
        self.node_timer.start(4000)
        
    def _cycle_nodes(self):
        if not self.isVisible(): return
        palette = self.theme.get('palette', ["#4BBEBF", "#3366CC", "#FFCC33", "#CC6633"])
        for i, node in enumerate(reversed(self.nodes)):
            idx = (self.node_phase + i) % len(palette)
            node.setStyleSheet(f"background-color: {palette[idx]}; border-radius: 2px;")
        self.node_phase = (self.node_phase + 1) % len(palette)
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Main container
        container = QFrame()
        container.setFixedSize(1200, 800)
        container.setStyleSheet("background: black;")
        self.layout.addWidget(container)
        
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(4, 4, 4, 4)
        c_layout.setSpacing(6)
        
        # --- HEADER ---
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.h_elb = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        self.h_elb.setFixedSize(220, 80)
        header.addWidget(self.h_elb)
        
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(80)
        self.title_bar.setStyleSheet("background-color: #99FFFF; border-radius: 4px;")
        tb_lay = QHBoxLayout(self.title_bar)
        tb_lay.setContentsMargins(25, 0, 0, 0)
        hdr_txt = QLabel("◢ SYSTEM ACCESS // TEMPORAL ALIGNMENT")
        hdr_txt.setStyleSheet(f"color: black; {get_lcars_font_style(24, 'normal')}")
        tb_lay.addWidget(hdr_txt)
        header.addWidget(self.title_bar, 1)
        
        self.h_cap = QFrame()
        self.h_cap.setFixedSize(80, 80)
        self.h_cap.setStyleSheet("background-color: #9EA5BA; border-top-right-radius: 40px; border-bottom-right-radius: 4px;")
        header.addWidget(self.h_cap)
        c_layout.addLayout(header)

        # --- MAIN CONTENT ---
        main = QHBoxLayout()
        main.setSpacing(6)
        
        # Sidebar
        sidebar = QVBoxLayout()
        sidebar.setSpacing(6)
        
        self.sb_main = QFrame()
        self.sb_main.setFixedSize(220, 400)
        self.sb_main.setStyleSheet("background-color: #2A7193; border-radius: 4px; border-bottom-left-radius: 100px;")
        sidebar.addWidget(self.sb_main)
        
        sidebar.addStretch()
        
        # Animated Nodes
        self.nodes = []
        for _ in range(6):
            n = QFrame()
            n.setFixedSize(220, 20)
            n.setStyleSheet("background-color: #4BBEBF; border-radius: 2px;")
            sidebar.addWidget(n)
            self.nodes.append(n)
            
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
        self.info_lbl = QLabel(f"STARDATE: {stardate} // {self.faction} SECTOR")
        self.info_lbl.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(28, 'normal')}")
        content.addWidget(self.info_lbl)
        
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
            btn.clicked.connect(lambda checked, f=faction: self._on_faction_selected(f))
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
            btn.clicked.connect(lambda checked, e=era: self._on_era_selected(e))
            era_grid.addWidget(btn, i // 3, i % 3)
        
        content.addLayout(era_grid)
        content.addStretch()
        
        main.addLayout(content, 1)
        c_layout.addLayout(main)
        
        # --- FOOTER ---
        self.footer = QFrame()
        self.footer.setFixedHeight(40)
        self.footer.setStyleSheet("background-color: #2A7193; border-bottom-right-radius: 20px; border-top-right-radius: 4px;")
        c_layout.addWidget(self.footer)
        
    def _on_faction_selected(self, faction):
        get_sound_manager().play("acknowledge")
        self.faction = faction
        stardate = time.strftime("%Y.%m.%d")
        self.info_lbl.setText(f"STARDATE: {stardate} // {faction} SECTOR")
        
    def _on_era_selected(self, era):
        get_sound_manager().play("acknowledge")
        self.selected.emit(self.faction, era.value)

class IntegratedDesktop(QMainWindow):
    """Main desktop using existing LCARS architecture"""
    def __init__(self, era=LCARSEra.LCARS_25TH, faction="FEDERATION"):
        super().__init__()
        self.era = era
        self.faction = faction
        self.theme = get_theme(era)
        self.color_gen = LCARSColorGenerator(era)
        
        self.setWindowTitle(f"LCARS Desktop - {faction} {era.value}")
        self.setGeometry(50, 50, 1600, 1000)
        self.setStyleSheet("background-color: black;")
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # --- HEADER ---
        header = QHBoxLayout()
        header.setSpacing(4)
        
        elbow_left = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        elbow_left.setFixedSize(250, 80)
        header.addWidget(elbow_left)
        
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
        
        # --- MAIN INTERFACE ---
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
        
        # --- FOOTER ---
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

def main():
    print("=== INTEGRATED LCARS SYSTEM INITIALIZATION ===")
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Initialize sound manager
    sound_mgr = get_sound_manager()
    
    # Step 1: Boot sequence
    print("Step 1: System Boot...")
    boot_view = IntegratedBootView()
    boot_view.show()
    
    # Wait for boot to complete
    boot_loop = QEventLoop()
    boot_view.finished.connect(boot_loop.quit)
    boot_loop.exec()
    
    print("Boot complete")
    
    # Step 2: Login
    print("Step 2: Authentication...")
    login_view = IntegratedLoginView()
    login_view.show()
    
    # Wait for login to complete
    login_loop = QEventLoop()
    login_view.finished.connect(login_loop.quit)
    login_loop.exec()
    
    print("Authentication successful")
    
    # Step 3: Launcher
    print("Step 3: Configuration Selection...")
    launcher = IntegratedLauncherView()
    launcher.show()
    
    # Wait for selection
    launcher_loop = QEventLoop()
    launcher.selected.connect(launcher_loop.quit)
    launcher_loop.exec()
    
    print("Configuration selected")
    
    # Step 4: Main desktop
    print("Step 4: Launching Main Desktop...")
    desktop = IntegratedDesktop()
    desktop.show()
    
    print("=== LCARS SYSTEM FULLY OPERATIONAL ===")
    app.exec()

if __name__ == "__main__":
    main()
