"""
Geant4 Startup Views - Classic 25th Century Standard
Clean, functional, and authentic LCARS architecture.
"""
import random
# Titanium Bridge Migration: import datetime
import logging

logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, 
    QGridLayout, QStackedWidget, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor

from lcars.base.interface import LCARSButton, ScanningBar
from lcars.modules.sound_manager import get_sound_manager

class BootView(QWidget):
    """Authentic LCARS Boot Sequence using ColorGenerator logic."""
    finished = pyqtSignal()
    # Emitted when the user has completed selection: (faction_name, era_name)
    selection_made = pyqtSignal(str, str)

    def __init__(self, era=LCARSEra.LCARS_25TH):
        super().__init__()
        self.era = era
        from lcars.themes.lcars_palette import LCARSColorGenerator
        self.color_gen = LCARSColorGenerator(era)
        self.progress = 0
        
        self.steps = [
            "SCANNING CORE BUFFER...",
            "INITIALIZING NEURAL NETS...",
            "CALIBRATING OPTICAL DATA...",
            "ESTABLISHING SECURE PROTOCOLS...",
            "READY FOR INTERFACE.",
            "SELECT FACTION ALIGNMENT...",
            "SELECT TEMPORAL PERIOD...",
            "ACCESS GRANTED. WELCOME ABOARD."
        ]
        
        self.setup_ui()
        # Clear log at start; do NOT auto-start boot sequence.
        # Boot must be explicitly started via `start_boot()` to avoid
        # accidental automatic login flows during launcher initialization.
        self.log.setText("")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_boot)

    def start_boot(self):
        """Begin the timed boot sequence. Call explicitly when user confirms."""
        if not self.timer.isActive():
            self.timer.start(40)
            if True:
                get_sound_manager().play("acknowledge")
            if False: # Removed except block
                pass

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        container = QWidget()
        container.setFixedSize(900, 500)
        c_lay = QVBoxLayout(container)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(4)
        
        # --- HEADER ---
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.h_elb = QFrame()
        self.h_elb.setFixedSize(180, 60)
        self.h_elb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
        header.addWidget(self.h_elb)
        
        self.title_fr = QFrame()
        self.title_fr.setFixedHeight(60)
        self.title_fr.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
        tl_lay = QHBoxLayout(self.title_fr)
        lbl = QLabel("◢ LCARS SYSTEM - INITIALIZATION")
        lbl.setStyleSheet(f"color: black; {get_lcars_font_style(20, 'normal')}")
        tl_lay.addWidget(lbl)
        header.addWidget(self.title_fr, 1)
        
        self.h_cap = QFrame()
        self.h_cap.setFixedSize(40, 60)
        self.h_cap.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-right-radius: 30px; border-bottom-right-radius: 4px;")
        header.addWidget(self.h_cap)
        c_lay.addLayout(header)

        # --- MID ---
        mid = QHBoxLayout()
        mid.setSpacing(4)
        
        self.sb = QFrame()
        self.sb.setFixedWidth(180)
        self.sb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px; border-bottom-left-radius: 60px;")
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
        
        # Add faction buttons directly in setup - CENTERED
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)
        
        self.faction_buttons = []
        for i, (faction, faction_era) in enumerate([
            ("FEDERATION", FactionEra.STARFLEET_25TH),  # Federation - LCARS
            ("KLINGON", FactionEra.KLINGON),  # Klingon - own system
            ("ROMULAN", FactionEra.ROMULAN),  # Romulan - own system
            ("CARDASSIAN", FactionEra.CARDASSIAN)   # Cardassian - own system
        ]):
            # Get simple faction palette
            palette = get_simple_palette(faction_era)
            color = palette['primary']
            btn = QPushButton(faction)
            btn.setFixedSize(160, 70)  # Larger, more square
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    {get_lcars_font_style(16, 'normal')}
                    text-transform: uppercase;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {color};
                }}
            """)
            btn.clicked.connect(lambda checked, f=faction, fe=faction_era: self.select_faction_with_era(f, fe))
            btn.show()  # Show immediately
            button_layout.addWidget(btn)
            self.faction_buttons.append(btn)
        
        button_layout.addStretch()  # Center the buttons
        term.addWidget(button_container)
        
        # Hide container initially, show after boot
        self.button_container = button_container
        self.button_container.hide()
        
        term.addStretch()
        
        mid.addLayout(term, 1)
        c_lay.addLayout(mid, 1)

        # --- FOOTER ---
        self.footer = QFrame()
        self.footer.setFixedHeight(30)
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

    def update_boot(self):
        self.progress += 1
        
        if self.progress % 10 == 0:
            step_idx = min(self.progress // 20, len(self.steps)-1)
            current_step = self.steps[step_idx]
            self.step_lbl.setText(current_step)
            self.log.setText(f"{self.log.text()}\n0x{random.randint(1000, 9999):X} :: DATA_LINK_STABLE")
            get_sound_manager().play("click")
            
            # Subtly shift atmospheric colors (LCARS Panel Flicker)
            self.h_elb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
            self.title_fr.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
            
            # ENABLED: Show selection buttons after boot
            # if step_idx == 5 and not hasattr(self, 'faction_shown'):  # "SELECT FACTION ALIGNMENT..."
            #     self.show_faction_buttons()
            #     self.faction_shown = True
            
            # if step_idx == 6 and not hasattr(self, 'era_shown'):  # "SELECT TEMPORAL PERIOD..."
            #     self.show_era_buttons()
            #     self.era_shown = True

        if self.progress >= 100:
            self.timer.stop()
            get_sound_manager().play("ready")
            # Show complete boot sequence - no selection buttons
            self.show_complete_boot()
            
    def show_complete_boot(self):
        """Show complete boot sequence output"""
        self.step_lbl.setText("SYSTEM READY")
        
        # Add date and stardate
        current_date = datetime.datetime.now().strftime("%Y.%m.%d")
        stardate = f"Stardate: {random.randint(40000, 50000)}.{random.randint(1, 9)}"
        
        # Add complete boot messages to log
        boot_messages = [
            f"STARDATE: {stardate}",
            f"DATE: {current_date}",
            "",
            "// LCARS COMMAND :: NEXUS INTERFACE //",
            "=====================================",
            "AUTHENTICATING NEURAL PATHWAYS... [OK]",
            "SYNCHRONIZING CORE SUBSYSTEMS... [OK]",
            "ESTABLISHING TITAN-ERA PROTOCOL... [OK]",
            "",
            "◤ ISOLINEAR CORE: ACTIVE",
            "◤ NEXUS DATA HUB: ONLINE",
            "◤ KERNEL: ALL SYSTEMS NOMINAL",
            "◤ COORDINATOR: BOOT SEQUENCE INITIATED",
            "◤ COORDINATOR: BOOT SEQUENCE COMPLETED"
        ]
        
        full_log = "\n".join(boot_messages)
        self.log.setText(full_log)
        
        # Show selection buttons immediately after boot completes
        self.show_faction_selection()
            
    def show_faction_selection(self):
        """Show faction selection - SIMPLE"""
        logger.debug("show_faction_selection called")
        self.step_lbl.setText("SELECT FACTION")
        
        # Hide log
        self.log.hide()
        
        # Show button container
        self.button_container.show()
        
        self.selected_faction = None
        
    def show_era_selection(self):
        """Show era selection - REPLACE IN SAME CONTAINER"""
        self.step_lbl.setText("SELECT TEMPORAL PERIOD")
        
        # Hide faction buttons first
        for btn in self.faction_buttons:
            btn.hide()
        
        # Clear existing buttons from container
        button_layout = self.button_container.layout()
        while button_layout.count():
            item = button_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add era buttons to same container with proper palettes
        eras = [
            ("22ND", FactionEra.STARFLEET_22ND),
            ("23RD", FactionEra.STARFLEET_23RD),
            ("23ST", FactionEra.STARFLEET_23ST),
            ("24TH", FactionEra.STARFLEET_24TH),
            ("24ST", FactionEra.STARFLEET_24ST),
            ("25TH", FactionEra.STARFLEET_25TH),
            ("29TH", FactionEra.STARFLEET_29TH)
        ]
        
        self.era_buttons = []
        for era_name, era_enum in eras:
            # Get proper era palette
            palette = get_faction_palette(era_enum)
            color = palette.get('button_colors', ['#4BBEBF'])[0]
            
            btn = QPushButton(era_name)
            btn.setFixedSize(140, 60)  # Larger, more square
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: black;
                    border: none;
                    border-radius: 2px;
                    font-size: 14px;
                    font-weight: normal;
                    text-transform: uppercase;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {color};
                }}
            """)
            btn.clicked.connect(lambda checked, e=era_name, en=era_enum: self.select_era_with_enum(e, en))
            button_layout.addWidget(btn)
            self.era_buttons.append(btn)
        button_layout.addStretch()
        self.selected_era = None
        
    # REMOVED: Duplicate show_greeting method - using the new one below
        
    def select_faction_with_era(self, faction, faction_era):
        """Handle faction selection with era"""
        self.selected_faction = faction
        self.faction_era = faction_era
        get_sound_manager().play("acknowledge")
        
        # Show era selection after faction
        QTimer.singleShot(500, self.show_era_selection)
        
    def select_era_with_enum(self, era_name, era_enum):
        """Handle era selection with proper enum"""
        self.selected_era = era_name
        self.era_enum = era_enum
        get_sound_manager().play("acknowledge")
        
        # Show greeting after selection
        QTimer.singleShot(500, self.show_greeting)
        
    def select_era_simple(self, era):
        """Handle era selection - SIMPLE"""
        self.selected_era = era
        get_sound_manager().play("acknowledge")
        
        # Show greeting after selection
        QTimer.singleShot(500, self.show_greeting)
        
    def select_era(self, era_enum, display_name):
        """Handle era selection"""
        self.selected_era = display_name
        get_sound_manager().play("acknowledge")
        
        # Show greeting after selection
        QTimer.singleShot(500, self.show_greeting)
        
    def show_greeting(self):
        """Show greeting step"""
        self.step_lbl.setText("ACCESS GRANTED")
        
        # Hide era buttons first
        for btn in self.era_buttons:
            btn.hide()
        
        # Clear container and add greeting
        button_layout = self.button_container.layout()
        while button_layout.count():
            item = button_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        greeting_label = QLabel(f"Welcome to {self.selected_faction} Systems - {self.selected_era} Era")
        greeting_label.setStyleSheet(f"color: #4BBEBF; {get_lcars_font_style(24, 'normal')}")
        greeting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(greeting_label)
        
        # Show login after greeting
        QTimer.singleShot(2000, self.show_login)
        
    def show_login(self):
        """Show login screen with password simulation"""
        self.step_lbl.setText("AUTHENTICATION REQUIRED")
        
        # Clear container and add login
        button_layout = self.button_container.layout()
        while button_layout.count():
            item = button_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Login prompt
        login_label = QLabel(f"{self.selected_faction} USER AUTHENTICATION")
        login_label.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(20, 'normal')}")
        login_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(login_label)
        
        # Password field
        self.password_label = QLabel("ENTER PASSWORD: ")
        self.password_label.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(16, 'normal')}")
        button_layout.addWidget(self.password_label)
        
        self.password_stars = QLabel("")
        self.password_stars.setStyleSheet(f"color: #4BBEBF; {get_lcars_font_style(18, 'normal')}")
        button_layout.addWidget(self.password_stars)
        
        # Start password animation
        self.password_progress = 0
        self.password_timer = QTimer(self)
        self.password_timer.timeout.connect(self.animate_password)
        self.password_timer.start(300)
        
    def animate_password(self):
        """Animate password entry with stars"""
        self.password_progress += 1
        stars = "*" * self.password_progress
        self.password_stars.setText(stars)
        get_sound_manager().play("click")
        
        if self.password_progress >= 10:
            self.password_timer.stop()
            get_sound_manager().play("ready")
            QTimer.singleShot(1000, self.launch_desktop)
        
    def launch_desktop(self):
        """Launch desktop with selected configuration"""
        logger.debug("BootView.launch_desktop called with faction=%s, era=%s", self.selected_faction, self.selected_era)
        if hasattr(self, 'selection_made'):
            logger.debug("Emitting selection_made signal")
            self.selection_made.emit(self.selected_faction or "UNKNOWN", self.selected_era or "UNKNOWN")
        else:
            # For compatibility with existing system
            if True:
                logger.debug("Calling parent().parent().launch_desktop(...)")
                self.parent().parent().launch_desktop(self.selected_faction, self.selected_era)
            if False: # Removed except block
                logger.exception("Unhandled exception while calling parent launch_desktop")
                raise
        
    def show_selection_buttons(self):
        """Show faction and era selection buttons after boot"""
        # Change title to show current selection phase
        self.step_lbl.setText("SELECT FACTION")
        
        # Get the terminal layout (the layout that contains the log)
        terminal_layout = self.log.parent().layout()
        
        # Add faction selection AFTER the existing log
        faction_label = QLabel("SELECT FACTION:")
        faction_label.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(20, 'normal')}")
        terminal_layout.addWidget(faction_label)
        
        faction_grid = QGridLayout()
        faction_grid.setSpacing(15)
        
        factions = [
            ("FEDERATION", "#4BBEBF"),
            ("KLINGON", "#D80000"), 
            ("ROMULAN", "#006633"),
            ("CARDASSIAN", "#CC9966")
        ]
        
        self.faction_buttons = []
        for i, (faction, color) in enumerate(factions):
            btn = QPushButton(faction)
            btn.setFixedSize(200, 80)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    {get_lcars_font_style(18, 'normal')}
                    text-transform: uppercase;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {color};
                }}
            """)
            btn.clicked.connect(lambda checked, f=faction: self.select_faction(f))
            faction_grid.addWidget(btn, i // 2, i % 2)
            self.faction_buttons.append(btn)
        
        terminal_layout.addLayout(faction_grid)
        
        # Store selections
        self.selected_faction = None
        self.selected_era = None
        self.faction_label = faction_label
        self.faction_grid = faction_grid
        self.era_label = None
        self.era_grid = None
        
        # Hide faction buttons
        for btn in self.faction_buttons:
            btn.hide()
        self.faction_label.hide()
        
        # Show era selection
        self.step_lbl.setText("SELECT TEMPORAL PERIOD")
        
        era_label = QLabel("SELECT TEMPORAL PERIOD:")
        era_label.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(20, 'normal')}")
        self.era_label = era_label
        
        terminal_layout = self.log.parent().layout()
        terminal_layout.addWidget(era_label)
        
        era_grid = QGridLayout()
        era_grid.setSpacing(10)
        
        eras = [
            ("22ND", LCARSEra.COMS_22ND),
            ("23RD", LCARSEra.PCARS_23RD),
            ("23ST", LCARSEra.PCARS_23ST),
            ("24TH", LCARSEra.LCARS_24TH),
            ("24ST", LCARSEra.LCARS_24ST),
            ("25TH", LCARSEra.LCARS_25TH),
            ("29TH", LCARSEra.TCARS_29TH)
        ]
        
        self.era_buttons = []
        for i, (display, era_enum) in enumerate(eras):
            btn = QPushButton(display)
            btn.setFixedSize(150, 60)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {get_random_button_color(era_enum)};
                    color: black;
                    border: none;
                    border-radius: 4px;
                    {get_lcars_font_style(16, 'normal')}
                    text-transform: uppercase;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {get_random_button_color(era_enum)};
                }}
            """)
            btn.clicked.connect(lambda checked, e=era_enum, d=display: self.select_era(e, d))
            era_grid.addWidget(btn, i // 3, i % 3)
            self.era_buttons.append(btn)
        
        self.era_grid = era_grid
        terminal_layout.addLayout(era_grid)
        
    def select_era(self, era_enum, display_name):
        """Handle era selection and show greeting"""
        self.selected_era = display_name
        get_sound_manager().play("acknowledge")
        
        # Hide era buttons
        for btn in self.era_buttons:
            btn.hide()
        self.era_label.hide()
        
        # Show greeting
        self.step_lbl.setText("ACCESS GRANTED")
        
        greeting_label = QLabel(f"Welcome to {self.selected_faction} Systems - {self.selected_era} Era")
        greeting_label.setStyleSheet(f"color: #4BBEBF; {get_lcars_font_style(24, 'normal')}")
        terminal_layout = self.log.parent().layout()
        terminal_layout.addWidget(greeting_label)
        
        # Auto-launch desktop after 2 seconds
        QTimer.singleShot(2000, self.launch_desktop)
        
    def launch_desktop(self):
        """Launch desktop with selected configuration"""
        if hasattr(self, 'selection_made'):
            self.selection_made.emit(self.selected_faction, self.selected_era)
        else:
            # For compatibility with existing system
            self.parent().parent().launch_desktop(self.selected_faction, self.selected_era)

class IntegratedLauncherView(QWidget):
    """Authentic LCARS Launcher aligned with user-provided reference."""
    selected = pyqtSignal(str, str)
    alert_triggered = pyqtSignal()
    bios_requested = pyqtSignal()

    def __init__(self, era=LCARSEra.LCARS_25TH):
        super().__init__()
        from lcars.themes.lcars_palette import LCARSColorGenerator
        self.era = era
        self.faction = "FEDERATION"
        self.color_gen = LCARSColorGenerator(era)
        self.theme = get_theme(era)
        self.node_phase = 0
        self.setup_ui()
        
        # Node Shifting Algorithm (Sequential "Alive" movement)
        self.node_timer = QTimer(self)
        self.node_timer.timeout.connect(self._cycle_nodes)
        self.node_timer.start(4000) # Slower, rhythmic shifting

    def _cycle_nodes(self):
        if not self.isVisible(): return
        palette = self.theme.get('palette', ["#4BBEBF", "#3366CC", "#FFCC33", "#CC6633"])
        for i, node in enumerate(reversed(self.nodes)):
            idx = (self.node_phase + i) % len(palette)
            node.setStyleSheet(f"background-color: {palette[idx]}; border-radius: 2px;")
        self.node_phase = (self.node_phase + 1) % len(palette)

    def setup_ui(self):
        """Create dynamic launcher interface"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Main container with LCARS styling
        container = QFrame()
        container.setStyleSheet("background-color: black; border: 2px solid #4BBEBF;")
        self.layout.addWidget(container)
        
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(15)
        
        # Header with stardate
        self.header = QFrame()
        self.header.setFixedHeight(60)
        self.header.setStyleSheet("background-color: #4BBEBF; border-radius: 4px;")
        h_layout = QHBoxLayout(self.header)
        
        stardate = datetime.datetime.now().strftime("%Y.%m.%d")
        self.info_lbl = QLabel(f"STARDATE: {stardate} // FEDERATION SECTOR")
        self.info_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(24, 'normal')}")
        h_layout.addWidget(self.info_lbl)
        c_layout.addWidget(self.header)
        
        # Dynamic faction grid
        self.faction_container = QFrame()
        self.faction_container.setStyleSheet("background-color: #111111; border-radius: 4px;")
        grid_layout = QGridLayout(self.faction_container)
        grid_layout.setSpacing(20)
        
        self.faction_buttons = {}
        factions = ["FEDERATION", "KLINGON", "ROMULAN", "CARDASSIAN"]
        colors = ["#4BBEBF", "#FF6B6B", "#FFD700", "#8B4513"]
        
        for i, (faction, color) in enumerate(zip(factions, colors)):
            btn = QPushButton(faction)
            btn.setFixedSize(250, 150)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: 2px solid {color};
                    border-radius: 8px;
                    {get_lcars_font_style(20, 'normal')};
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {color};
                    border: 2px solid white;
                }}
            """)
            btn.clicked.connect(lambda checked, f=faction: self._on_faction_selected(f))
            grid_layout.addWidget(btn, i // 2, i % 2)
            self.faction_buttons[faction] = btn
        
        c_layout.addWidget(self.faction_container)
        
        # Status bar with animation
        self.status_bar = QFrame()
        self.status_bar.setFixedHeight(40)
        self.status_bar.setStyleSheet("background-color: #2A7193; border-radius: 4px;")
        status_layout = QHBoxLayout(self.status_bar)
        
        self.status_lbl = QLabel("SYSTEM READY // AWAITING COMMAND")
        self.status_lbl.setStyleSheet(f"color: #99FFFF; {get_lcars_font_style(16, 'normal')}")
        status_layout.addWidget(self.status_lbl)
        status_layout.addStretch()
        
        # Animated indicators
        self.indicators = []
        for i in range(5):
            indicator = QFrame()
            indicator.setFixedSize(30, 20)
            indicator.setStyleSheet(f"background-color: #4BBEBF; border-radius: 2px;")
            status_layout.addWidget(indicator)
            self.indicators.append(indicator)
        
        c_layout.addWidget(self.status_bar)
        
        # Start animations
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate_indicators)
        self.animation_timer.start(500)
        
    def update_alert_level(self, level: str):
        """React to system-wide alert level changes."""
        if level == "RED":
            self.container.setStyleSheet("background: #110000; border: 2px solid #D80000;")
            self.h_elb.setStyleSheet(f"background-color: #D80000; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
            self.title_bar.setStyleSheet("background-color: #CC0000; border-radius: 4px;")
            self.sb_main.setStyleSheet("background-color: #D80000; border-radius: 4px; border-bottom-left-radius: 90px;")
            self.footer.setStyleSheet("background-color: #D80000; border-bottom-right-radius: 40px; border-top-right-radius: 4px;")
            self.info_lbl.setStyleSheet(f"color: #D80000; {get_lcars_font_style(28, 'normal')}")
        else:
            self.container.setStyleSheet("background: black; border: 2px solid #111;")
            self.h_elb.setStyleSheet(f"background-color: #4BBEBF; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
            self.title_bar.setStyleSheet("background-color: #99FFFF; border-radius: 4px;")
            self.sb_main.setStyleSheet("background-color: #2A7193; border-radius: 4px; border-bottom-left-radius: 90px;")
            self.footer.setStyleSheet("background-color: #2A7193; border-bottom-right-radius: 40px; border-top-right-radius: 4px;")
            self.info_lbl.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(28, 'normal')}")

    def _animate_indicators(self):
        """Animate status indicators"""
        colors = ["#4BBEBF", "#FFCC33", "#FF6B6B", "#99FFFF", "#FFFFFF"]
        
        for i, indicator in enumerate(self.indicators):
            phase = (self.node_phase + i) % len(colors)
            indicator.setStyleSheet(f"background-color: {colors[phase]}; border-radius: 2px;")
        
        self.node_phase = (self.node_phase + 1) % len(colors)
        
        # Also animate selected faction button
        if hasattr(self, 'selected_faction') and self.selected_faction in self.faction_buttons:
            btn = self.faction_buttons[self.selected_faction]
            current_style = btn.styleSheet()
            if "border: 2px solid white" in current_style:
                # Remove white border
                new_style = current_style.replace("border: 2px solid white;", "border: 2px solid #FFD700;")
            else:
                # Add white border
                new_style = current_style.replace("border: 2px solid #FFD700;", "border: 2px solid white;")
            btn.setStyleSheet(new_style)

    def _on_faction_selected(self, name):
        get_sound_manager().play("acknowledge")
        self.selected_faction = name
        stardate = datetime.datetime.now().strftime("%Y.%m.%d")
        self.info_lbl.setText(f"STARDATE: {stardate} // {name} SECTOR")
        self.status_lbl.setText(f"FACTION SELECTED: {name} // INITIATING INTERFACE")
        
        # Highlight selected button
        for faction, btn in self.faction_buttons.items():
            if faction == name:
                btn.setStyleSheet(btn.styleSheet().replace("border: 2px solid #FFD700;", "border: 2px solid white;"))
            else:
                btn.setStyleSheet(btn.styleSheet().replace("border: 2px solid white;", "border: 2px solid #FFD700;"))
        
        # Emit selection signal after delay
        QTimer.singleShot(1500, lambda: self.selected.emit(name, "25th"))
        # self.stack.setCurrentIndex(1) # Keep on Faction page to show off the change, or move? 
        # User wants "authentic interface", usually implies staying to see the change or immediate transition? 
        # Let's keep existing logic but maybe delay transition or just transition.
        # Actually user complaining about "where buttons?" implies they want to see the UI change.
        # Let's transition to Era selection as before, but the BG/Style will be updated.
        self.stack.setCurrentIndex(1)

    def apply_faction_style(self, faction_name):
        """Apply authentic geometry and colors based on faction."""
        f = faction_name.upper()
        
        # DEFAULT / FEDERATION
        # Rounded corners, Blue/Orange/Beige, Standard Font
        radius_elb = "40px"
        radius_sb = "90px"
        radius_footer = "40px"
        radius_title = "4px"
        
        col_elb = "#4BBEBF"
        col_sb = "#2A7193"
        col_footer = "#2A7193"
        col_title = "#99FFFF"
        col_text = "#FFCC33"
        
        if f == "KLINGON":
            # Angular, Red/Metal, Aggressive
            radius_elb = "0px"
            radius_sb = "0px"
            radius_footer = "0px"
            radius_title = "0px"
            
            col_elb = "#D80000"
            col_sb = "#990000"
            col_footer = "#990000"
            col_title = "#CC0000"
            col_text = "#FF0000"
            
        elif f == "ROMULAN":
            # Boxy but slight curves, Green/Grey
            radius_elb = "10px"
            radius_sb = "20px"
            radius_footer = "10px"
            radius_title = "2px"
            
            col_elb = "#006633"
            col_sb = "#004422"
            col_footer = "#004422"
            col_title = "#339966"
            col_text = "#66FF99"

        elif f == "CARDASSIAN":
            # Industrial, Beveled look (simulated with borders later?), Brown/Orange
            radius_elb = "2px" # Almost sharp
            radius_sb = "15px"
            radius_footer = "5px"
            radius_title = "0px"
            
            col_elb = "#CC9966"
            col_sb = "#996633"
            col_footer = "#996633"
            col_title = "#FFCC66"
            col_text = "#FF9900"

        # Apply Styles
        self.h_elb.setStyleSheet(f"background-color: {col_elb}; border-top-left-radius: {radius_elb}; border-bottom-left-radius: 4px;")
        self.sb_main.setStyleSheet(f"background-color: {col_sb}; border-radius: 4px; border-bottom-left-radius: {radius_sb};")
        self.footer.setStyleSheet(f"background-color: {col_footer}; border-bottom-right-radius: {radius_footer}; border-top-right-radius: 4px;")
        self.title_bar.setStyleSheet(f"background-color: {col_title}; border-radius: {radius_title};")
        self.info_lbl.setStyleSheet(f"color: {col_text}; {get_lcars_font_style(28, 'normal')}")

        # Update Nodes colors slightly to match theme
        if f == "KLINGON":
            node_col = "#FF3333" 
            node_rad = "0px"
        elif f == "ROMULAN":
            node_col = "#33CC66"
            node_rad = "2px"
        elif f == "CARDASSIAN":
            node_col = "#FFCC33"
            node_rad = "4px"
        else:
            node_col = "#3366CC"
            node_rad = "8px"

        for n in self.nodes:
            n.setStyleSheet(f"background-color: {node_col}; border-radius: {node_rad};")

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Main Dialog Container (Open Geometry - No Border)
        self.container = QFrame()
        self.container.setFixedSize(1024, 700)
        self.container.setStyleSheet("background: black;") # Removed border: 2px solid #111
        
        # USE GRID LAYOUT FOR PERFECT ALIGNMENT
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(4, 4, 4, 4)
        self.grid.setSpacing(6)
        
        # --- COLUMNS SETUP ---
        # Col 0: Sidebar/Elbow (Fixed 220px)
        self.grid.setColumnMinimumWidth(0, 220)
        self.grid.setColumnStretch(0, 0)
        # Col 1: Content (Stretch)
        self.grid.setColumnStretch(1, 1)
        # Col 2: Cap (Small)
        self.grid.setColumnMinimumWidth(2, 80)
        self.grid.setColumnStretch(2, 0)

        # --- ROW 0: HEADER ---
        # 0,0: Header Block (Industrial)
        self.h_elb = QFrame()
        self.h_elb.setFixedSize(220, 60)
        self.h_elb.setStyleSheet("background-color: #4BBEBF; border-radius: 4px;")
        self.grid.addWidget(self.h_elb, 0, 0)
        
        # 0,1: Title Bar
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(60)
        self.title_bar.setStyleSheet("background-color: #99FFFF; border-radius: 4px;")
        # No inner layout needed if just label, but keeping it for structure
        tb_lay = QHBoxLayout(self.title_bar)
        tb_lay.setContentsMargins(25, 0, 0, 0)
        hdr_txt = QLabel("◢ SYSTEM ACCESS // TEMPORAL ALIGNMENT")
        hdr_txt.setStyleSheet(f"color: black; {get_lcars_font_style(24, 'normal')}")
        tb_lay.addWidget(hdr_txt)
        self.grid.addWidget(self.title_bar, 0, 1, alignment=Qt.AlignmentFlag.AlignTop)
        
        # 0,2: Cap
        self.h_cap = QFrame()
        self.h_cap.setFixedSize(80, 60)
        self.h_cap.setStyleSheet("background-color: #9EA5BA; border-top-right-radius: 30px; border-bottom-right-radius: 4px;")
        self.grid.addWidget(self.h_cap, 0, 2, alignment=Qt.AlignmentFlag.AlignTop)

        # --- ROW 1: MID CONTENT ---
        # 1,0: Sidebar Container
        sidebar_container = QWidget()
        sidebar_container.setFixedWidth(220)
        sb_lay = QVBoxLayout(sidebar_container)
        sb_lay.setContentsMargins(0, 0, 0, 0)
        sb_lay.setSpacing(6)
        
        self.sb_main = QFrame()
        self.sb_main.setFixedSize(220, 360)
        # Style set by apply_faction_style
        sb_lay.addWidget(self.sb_main)
        
        sb_lay.addStretch()
        
        # Animated Nodes
        self.nodes = []
        for _ in range(5):
            n = QFrame()
            n.setFixedSize(220, 18)
            # Style set by apply_faction_style
            sb_lay.addWidget(n)
            self.nodes.append(n)
            
        # RED ALERT Button
        self.alert_btn = LCARSButton("RED ALERT", "#D80000", era=self.era, shape="rect", auto_cycle=False)
        self.alert_btn.setFixedSize(220, 60)
        self.alert_btn.clicked.connect(self.alert_triggered.emit)
        sb_lay.addWidget(self.alert_btn)
        
        self.grid.addWidget(sidebar_container, 1, 0)
        
        # 1,1 - 1,2: DECK (Spanning cols 1 and 2)
        deck = QVBoxLayout()
        deck.setContentsMargins(40, 20, 20, 20)
        deck.setSpacing(20)
        
        # Stardate Header Row
        info_row = QHBoxLayout()
        info_row.addStretch()
        stardate = datetime.datetime.now().strftime("%Y.%m.%d")
        self.info_lbl = QLabel(f"STARDATE: {stardate} // {self.faction}")
        self.info_lbl.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(28, 'normal')}")
        info_row.addWidget(self.info_lbl)
        deck.addLayout(info_row)
        
        self.stack = QStackedWidget()
        
        # Faction Grid
        f_page = QWidget()
        f_grid = QGridLayout(f_page)
        f_grid.setSpacing(30)
        
        f_list = [
            ("FEDERATION", "#556699"), ("KLINGON", "#990000"),
            ("ROMULAN", "#006633"), ("CARDASSIAN", "#CC9966")
        ]
        for i, (name, color) in enumerate(f_list):
            btn = LCARSButton(name, color, era=self.era, shape="rect", auto_cycle=True)
            btn.setFixedSize(280, 140)
            btn.clicked.connect(lambda ch, n=name: self._on_faction_selected(n))
            f_grid.addWidget(btn, i // 2, i % 2)
        self.stack.addWidget(f_page)
        
        self.stack.addWidget(f_page)
        
        # Era Grid (Full 7 Eras - Symmetric Layout)
        e_page = QWidget()
        e_layout = QVBoxLayout(e_page)
        e_layout.setContentsMargins(0, 0, 0, 0)
        e_layout.setSpacing(20)

        # Title
        era_title = QLabel("SELECT TEMPORAL PERIOD")
        era_title.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(22, 'normal')}")
        era_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e_layout.addStretch()
        e_layout.addWidget(era_title)

        e_grid = QGridLayout()
        e_grid.setSpacing(20)
        e_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        all_eras = ["22nd", "23rd", "23st", "24th", "24st", "25th"]
        # First 6 eras (2 columns x 3 rows)
        row, col = 0, 0
        for era in all_eras:
            eb = LCARSButton(era.upper(), "#2A7193", era=self.era, shape="rect", auto_cycle=True)
            eb.setFixedSize(220, 70)
            eb.clicked.connect(lambda ch, e=era: self.selected.emit(self.faction, e))
            e_grid.addWidget(eb, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # 7th Era (29th) - Centered / Spanning
        e29 = LCARSButton("29TH", "#5A4A85", era=self.era, shape="rect", auto_cycle=True)
        e29.setFixedSize(460, 70) # Double width + spacing
        e29.clicked.connect(lambda: self.selected.emit(self.faction, "29th"))
        e_grid.addWidget(e29, row, 0, 1, 2)
        
        e_layout.addLayout(e_grid)
        
        # Back Button (Distinct Command Bar)
        back_btn = LCARSButton("CANCEL SELECTION", "#CC6633", era=self.era, shape="rect", auto_cycle=False)
        back_btn.setFixedSize(220, 50)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        
        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(back_btn)
        button_row.addStretch()
        e_layout.addLayout(button_row)
        
        e_layout.addStretch()
        self.stack.addWidget(e_page)
        
        deck.addWidget(self.stack)
        deck.addStretch()
        
        # RE-ADD DECK TO GRID
        self.grid.addLayout(deck, 1, 1, 1, 2)

        # --- ROW 2: FOOTER ---
        # 2,0: Spacer/Empty
        
        # 2,1 - 2,2: Footer Bar
        self.footer = QFrame()
        self.footer.setFixedHeight(40)
        self.footer.setStyleSheet("background-color: #2A7193; border-bottom-right-radius: 40px; border-top-right-radius: 4px;")
        self.grid.addWidget(self.footer, 2, 1, 1, 2)

        # Center in Viewport
        self.layout.addStretch()
        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(self.container)
        h_box.addStretch()
        self.layout.addLayout(h_box)
        self.layout.addStretch()
        
        self.apply_faction_style(self.faction)

    def _on_faction_selected(self, name):
        get_sound_manager().play("acknowledge")
        self.faction = name
        stardate = datetime.datetime.now().strftime("%Y.%m.%d")
        self.info_lbl.setText(f"STARDATE: {stardate} // {self.faction} SECTOR")
        self.stack.setCurrentIndex(1)

class GreetingView(QWidget):
    finished = pyqtSignal()
    def __init__(self, faction=None):
        super().__init__()
        l = QVBoxLayout(self)
        self.lbl = QLabel("ACCESS GRANTED\nWELCOME")
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setStyleSheet(f"color: #4BBEBF; {get_lcars_font_style(32, 'normal')}")
        l.addWidget(self.lbl)
        QTimer.singleShot(2000, self.finished.emit)

class LoginView(QWidget):
    """Authentic LCARS Authorization Protocol screen."""
    finished = pyqtSignal()

    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__()
        self.era = era
        self.faction = faction
        from lcars.themes.lcars_palette import LCARSColorGenerator
        self.color_gen = LCARSColorGenerator(era)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Main Dialog Container
        self.container = QFrame()
        self.container.setFixedSize(800, 450)
        self.container.setStyleSheet("background: black;")
        c_lay = QVBoxLayout(self.container)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(4)
        
        # --- HEADER ---
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.h_elb = QFrame()
        self.h_elb.setFixedSize(140, 50)
        # Style set by apply_faction_style
        header.addWidget(self.h_elb)
        
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(50)
        # Style set by apply_faction_style
        tb_lay = QHBoxLayout(self.title_bar)
        tb_lay.setContentsMargins(20, 0, 0, 0)
        hdr_txt = QLabel("◢ AUTHORIZATION PROTOCOL - SECURE ACCESS")
        hdr_txt.setStyleSheet(f"color: black; {get_lcars_font_style(16, 'normal')}")
        tb_lay.addWidget(hdr_txt)
        header.addWidget(self.title_bar, 1)
        
        self.h_cap = QFrame()
        self.h_cap.setFixedSize(30, 50)
        self.h_cap.setStyleSheet("background-color: #9EA5BA; border-top-right-radius: 15px; border-bottom-right-radius: 4px;")
        header.addWidget(self.h_cap)
        c_lay.addLayout(header)

        # --- MID AREA ---
        mid = QHBoxLayout()
        mid.setSpacing(10)
        
        # Left Sidebar (blocky)
        sidebar = QVBoxLayout()
        sidebar.setSpacing(4)
        self.sb_block = QFrame()
        self.sb_block.setFixedSize(140, 200)
        # Style set by apply_faction_style
        sidebar.addWidget(self.sb_block)
        sidebar.addStretch()
        mid.addLayout(sidebar)
        
        # Main content area
        content = QVBoxLayout()
        content.setContentsMargins(30, 20, 30, 20)
        content.setSpacing(15)
        
        self.status_lbl = QLabel("PROTOCOL :: IDENTIFYING NEURAL PATTERN...")
        # Style set by apply_faction_style
        content.addWidget(self.status_lbl)
        
        self.progress_bar = ScanningBar("#4BBEBF", self)
        self.progress_bar.setFixedHeight(25)
        content.addWidget(self.progress_bar)
        
        content.addStretch()
        
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.auth_btn = LCARSButton("AUTHORIZE", "#3366CC", shape="rect", auto_cycle=True)
        self.auth_btn.setFixedSize(160, 45)
        self.auth_btn.clicked.connect(self.start_auth)
        btn_box.addWidget(self.auth_btn)
        content.addLayout(btn_box)
        
        mid.addLayout(content, 1)
        c_lay.addLayout(mid, 1)

        # --- FOOTER ---
        self.footer = QFrame()
        self.footer.setFixedHeight(20)
        # Style set by apply_faction_style
        c_lay.addWidget(self.footer)

        # Centering
        self.layout.addStretch()
        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(self.container)
        h_box.addStretch()
        self.layout.addLayout(h_box)
        self.layout.addStretch()
        
        self.apply_faction_style(self.faction)

    def start_auth(self):
        get_sound_manager().play("acknowledge")
        self.auth_btn.setEnabled(False)
        self.status_lbl.setText("SCANNING BIOMETRICS... [MATCH CONFIRMED]")
        QTimer.singleShot(1500, self.finish_auth)

    def finish_auth(self):
        get_sound_manager().play("ready")
        self.finished.emit()
