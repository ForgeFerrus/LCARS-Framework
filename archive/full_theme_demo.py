"""
Full LCARS Theme Demo - Complete demonstration of all canonical faction and era themes
Based on authentic Star Trek LCARS interface color palettes
Запуск: python full_theme_demo.py
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QFrame, QTabWidget, QTextEdit,
    QGroupBox, QGridLayout, QScrollArea, QLineEdit, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QPen

# Import centralized theme system
try:
    from lcars.themes.lcars_palette import get_palette_by_name
    THEME_SYSTEM_AVAILABLE = True
except ImportError:
    THEME_SYSTEM_AVAILABLE = False

# Import existing UI components if available
try:
    from lcars.ui.elements import LCARSRect, LCARSCircle, LCARSButton
    UI_COMPONENTS_AVAILABLE = True
except ImportError:
    UI_COMPONENTS_AVAILABLE = False

# Fallback components only if UI components not available
if not UI_COMPONENTS_AVAILABLE:
    class LCARSRect(QWidget):
        def __init__(self, color="#BFC2C4", border_color="#FFF", border=4, parent=None):
            super().__init__(parent)
            self.color = color
            self.border_color = border_color
            self.border = border
            self.setStyleSheet("background: transparent;")
        def paintEvent(self, a0):
            w, h = self.width(), self.height()
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setPen(QPen(QColor(self.border_color), self.border))
            painter.setBrush(QColor(self.color))
            painter.drawRect(self.border//2, self.border//2, w-self.border, h-self.border)

import os

# Ensure the project root and lcars/ui are in the Python path
project_root = Path(__file__).resolve().parents[2]
lcars_ui_dir = Path(__file__).resolve().parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(lcars_ui_dir) not in sys.path:
    sys.path.insert(0, str(lcars_ui_dir))

# Simplify sys.path handling to avoid conflicts
sys.path = list(dict.fromkeys(sys.path))  # Remove duplicates
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class FullThemeDemo(QMainWindow):
    """Complete LCARS theme demonstration with all factions and eras"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Complete Theme Demonstration")
        self.setGeometry(100, 100, 1400, 900)
        
        # Remove window decorations - frameless window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Set black background immediately - NO WHITE SCREEN
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
        
        # Initialize theme system
        self.current_theme = None
        
        # Setup UI
        self.setup_ui()
        
        # Apply initial theme after UI is ready
        QTimer.singleShot(100, self.apply_25th_century_theme)
        
        # Start time update
        self.update_time()
        
    def setup_ui(self):
        """Setup the complete demo interface"""
        # Set fullscreen
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.showFullScreen()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        
        # Left control panel
        self.create_control_panel(main_layout)
        
        # Main content area
        self.create_main_content(main_layout)
        
        # Initialize login_menu and main_menu in setup_ui
        self.login_menu = QFrame()
        self.main_menu = QFrame()
        self.login_menu.hide()
        self.main_menu.hide()

        # Default to Federation 25th century (after widgets are created)
        # self.apply_25th_century_theme()  # Don't call here - widgets not ready yet
        
    def create_control_panel(self, parent_layout):
        """Create left control panel with theme selection"""
        control_frame = QFrame()
        control_frame.setObjectName("control_panel")
        control_frame.setFixedWidth(280)
        
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(15)
        
        # Panel title
        panel_title = QLabel("THEME CONTROL")
        panel_title.setObjectName("panel_title")
        panel_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(panel_title)
        
        # Time display
        self.time_label = QLabel()
        self.time_label.setObjectName("time_display")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(self.time_label)
        
        # Theme selection
        theme_group = QGroupBox("SELECT THEME")
        theme_group.setObjectName("theme_group")
        theme_layout = QVBoxLayout(theme_group)
        
        # Faction selector - ALL REAL FACTIONS
        theme_layout.addWidget(QLabel("Faction:"))
        self.faction_combo = QComboBox()
        self.faction_combo.setObjectName("faction_selector")
        self.faction_combo.addItems([
            "Starfleet",
            "Klingon Empire", 
            "Romulan Star Empire",
            "Cardassian Union"
        ])
        self.faction_combo.currentTextChanged.connect(self.apply_25th_century_theme)
        theme_layout.addWidget(self.faction_combo)
        
        # Era selector - ALL REAL ERAS
        theme_layout.addWidget(QLabel("Era:"))
        self.era_combo = QComboBox()
        self.era_combo.setObjectName("era_selector")
        self.era_combo.addItems([
            "Pre-Federation (2150s)",
            "22nd Century (PCARS)",
            "Early 23rd Century (PCARS)",
            "Mid 23rd Century (TOS)",
            "Late 23rd Century (TMP)",
            "Early 24th Century (TNG)",
            "Mid 24th Century (DS9)",
            "Late 24th Century (VOY)",
            "25th Century (PIC)",
            "29th Century (TCARS)",
            "Alternate Timeline",
            "Mirror Universe"
        ])
        self.era_combo.currentTextChanged.connect(self.apply_25th_century_theme)
        theme_layout.addWidget(self.era_combo)
        
        # Ship selector - REAL SHIPS
        theme_layout.addWidget(QLabel("Ship:"))
        self.ship_combo = QComboBox()
        self.ship_combo.setObjectName("ship_selector")
        self.ship_combo.addItems([
            "Enterprise NX-01",
            "USS Enterprise NCC-1701",
            "USS Enterprise NCC-1701-A", 
            "USS Enterprise NCC-1701-B",
            "USS Enterprise NCC-1701-C",
            "USS Enterprise NCC-1701-D",
            "USS Enterprise NCC-1701-E",
            "USS Voyager NCC-74656",
            "USS Defiant NX-74205",
            "IKS Bortas",
            "IKS Rotarran",
            "IRW Valdore",
        ])
        self.ship_combo.currentTextChanged.connect(self.apply_25th_century_theme)
        theme_layout.addWidget(self.ship_combo)
        
        control_layout.addWidget(theme_group)
        
        # Quick theme buttons
        quick_group = QGroupBox("QUICK SELECT")
        quick_group.setObjectName("quick_group")
        quick_layout = QVBoxLayout(quick_group)

        # Quick themes: use friendly keys ("faction_era") for compatibility
        quick_themes = [
            ("Federation TNG", "federation_24th"),
            ("Federation TOS", "federation_23rd"),
            ("Federation TMP", "federation_23rd"),
            ("Enterprise NX-01", "federation_22nd"),
            ("Titan Era", "federation_25th"),
            ("TCARS", "federation_29th")
        ]
        
        self.quick_buttons = []
        for text, faction_era in quick_themes:
            btn = QPushButton(text)
            btn.setObjectName("quick_button")
            btn.clicked.connect(lambda checked, fe=faction_era: self.apply_theme(fe))
            quick_layout.addWidget(btn)
            self.quick_buttons.append(btn)
            
        control_layout.addWidget(quick_group)
        
        # Status display
        status_group = QGroupBox("CURRENT THEME")
        status_group.setObjectName("status_group")
        status_layout = QVBoxLayout(status_group)
        
        self.theme_info = QTextEdit()
        self.theme_info.setObjectName("theme_info")
        self.theme_info.setMaximumHeight(150)
        self.theme_info.setReadOnly(True)
        status_layout.addWidget(self.theme_info)
        
        control_layout.addWidget(status_group)
        
        # Add login button
        login_button = QPushButton("SYSTEM")
        login_button.setObjectName("login_button")
        login_button.setText("SYSTEM LOGIN")
        login_button.clicked.connect(self.launch_lcars_system)
        control_layout.addWidget(login_button)

        # Add logout button
        logout_button = QPushButton("EXIT")
        logout_button.setObjectName("logout_button")
        logout_button.setText("EXIT PROGRAM")
        logout_button.clicked.connect(self.close)
        control_layout.addWidget(logout_button)
        
        # Initialize era options
        # self.apply_25th_century_theme()  # Don't call here - widgets not ready yet
        
    def create_main_content(self, parent_layout):
        """Create main content area with examples"""
        content_frame = QFrame()
        content_frame.setObjectName("main_content")
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(20)
        
        # Main title
        self.main_title = QLabel("LCARS INTERFACE DEMONSTRATION")
        self.main_title.setObjectName("main_title")
        self.main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.main_title)
        
        # Tabbed interface
        self.tabs = QTabWidget()
        self.tabs.setObjectName("demo_tabs")

        # Tab 1: UI Elements
        self.create_ui_elements_tab()

        # Tab 2: Color Palette
        self.create_color_palette_tab()

        # Tab 3: LCARS Console
        self.create_lcars_console_tab()

        # Tab 4: Universal Editor
        # self.create_lcars_editor_tab()  # Disabled for now

        content_layout.addWidget(self.tabs)
        parent_layout.addWidget(content_frame)
        
        # Apply initial theme after all widgets are created
        self.apply_25th_century_theme()

            
                        
    def create_ui_elements_tab(self):
        """Create AUTHENTIC LCARS UI elements with faction-specific components"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Title
        title = QLabel("LCARS FACTION COMPONENTS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Federation Components Section
        fed_group = QGroupBox("FEDERATION LCARS COMPONENTS")
        fed_layout = QVBoxLayout(fed_group)
        
        # Federation Command Interface
        fed_command_row = QHBoxLayout()
        fed_command_label = QLabel("COMMAND INTERFACE:")
        fed_command_label.setStyleSheet("font-weight: bold; color: #FFCC00;")
        fed_command_row.addWidget(fed_command_label)
        
        # Federation LCARS buttons with authentic styling
        fed_btn1 = QPushButton("01 COMMAND")
        fed_btn1.setMinimumSize(100, 50)
        fed_btn1.clicked.connect(lambda: print("Federation Command clicked"))
        fed_command_row.addWidget(fed_btn1)
        
        fed_btn2 = QPushButton("02 TACTICAL")
        fed_btn2.setMinimumSize(100, 50)
        fed_btn2.clicked.connect(lambda: print("Federation Tactical clicked"))
        fed_command_row.addWidget(fed_btn2)
        
        fed_btn3 = QPushButton("03 SCIENCE")
        fed_btn3.setMinimumSize(100, 50)
        fed_btn3.clicked.connect(lambda: print("Federation Science clicked"))
        fed_command_row.addWidget(fed_btn3)
        
        fed_layout.addLayout(fed_command_row)
        
        # Federation Operations
        fed_ops_row = QHBoxLayout()
        fed_ops_label = QLabel("OPERATIONS:")
        fed_ops_label.setStyleSheet("font-weight: bold; color: #FFCC00;")
        fed_ops_row.addWidget(fed_ops_label)
        
        fed_btn4 = QPushButton("04 WARP")
        fed_btn4.setMinimumSize(100, 50)
        fed_btn4.clicked.connect(lambda: print("Federation Warp clicked"))
        fed_ops_row.addWidget(fed_btn4)
        
        fed_btn5 = QPushButton("05 SHIELDS")
        fed_btn5.setMinimumSize(100, 50)
        fed_btn5.clicked.connect(lambda: print("Federation Shields clicked"))
        fed_ops_row.addWidget(fed_btn5)
        
        fed_btn6 = QPushButton("06 PHASERS")
        fed_btn6.setMinimumSize(100, 50)
        fed_btn6.clicked.connect(lambda: print("Federation Phasers clicked"))
        fed_ops_row.addWidget(fed_btn6)
        
        fed_layout.addLayout(fed_ops_row)
        
        layout.addWidget(fed_group)
        
        # Klingon Empire Components Section
        klingon_group = QGroupBox("KLINGON EMPIRE COMPONENTS")
        klingon_layout = QVBoxLayout(klingon_group)
        
        # Klingon Battle Interface
        klingon_battle_row = QHBoxLayout()
        klingon_battle_label = QLabel("BATTLE INTERFACE:")
        klingon_battle_label.setStyleSheet("font-weight: bold; color: #CC0000;")
        klingon_battle_row.addWidget(klingon_battle_label)
        
        # Klingon buttons with authentic styling
        klingon_btn1 = LCARSButton("01", "WEAPONS")
        klingon_btn1.era = LCARSEra.PCARS_23RD
        klingon_btn1.apply_theme()
        klingon_btn1.setStyleSheet("background-color: #8B0000; color: #FFCC00; border: 2px solid #CC0000;")
        klingon_btn1.setMinimumSize(100, 50)
        klingon_btn1.clicked.connect(lambda: print("Klingon Weapons clicked"))
        klingon_battle_row.addWidget(klingon_btn1)
        
        klingon_btn2 = LCARSButton("02", "CLOAK")
        klingon_btn2.era = LCARSEra.PCARS_23RD
        klingon_btn2.apply_theme()
        klingon_btn2.setStyleSheet("background-color: #8B0000; color: #FFCC00; border: 2px solid #CC0000;")
        klingon_btn2.setMinimumSize(100, 50)
        klingon_btn2.clicked.connect(lambda: print("Klingon Cloak clicked"))
        klingon_battle_row.addWidget(klingon_btn2)
        
        klingon_btn3 = LCARSButton("03", "TARGET")
        klingon_btn3.era = LCARSEra.PCARS_23RD
        klingon_btn3.apply_theme()
        klingon_btn3.setStyleSheet("background-color: #8B0000; color: #FFCC00; border: 2px solid #CC0000;")
        klingon_btn3.setMinimumSize(100, 50)
        klingon_btn3.clicked.connect(lambda: print("Klingon Target clicked"))
        klingon_battle_row.addWidget(klingon_btn3)
        
        klingon_layout.addLayout(klingon_battle_row)
        
        layout.addWidget(klingon_group)
        
        # Add stretch
        layout.addStretch()
        
        self.tabs.addTab(tab, "ELEMENTS")
        
    
    def create_color_palette_tab(self):
        """Create color palette demonstration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Color grid
        colors_group = QGroupBox("THEME COLOR PALETTE")
        colors_group.setObjectName("colors_group")
        colors_layout = QGridLayout(colors_group)
        
        self.color_swatches = {}
        color_labels = [
            "Primary", "Secondary", "Accent",
            "Background", "Panel", "Frame", 
            "Text", "Border", "Hover",
            "Warning", "Success", "Error"
        ]
        
        for i, label in enumerate(color_labels):
            row = i // 4
            col = i % 4
            
            # Color swatch
            swatch = QFrame()
            swatch.setFixedSize(80, 50)
            swatch.setObjectName(f"swatch_{label.lower()}")
            
            # Label
            label_widget = QLabel(label)
            label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_widget.setObjectName("color_label")
            
            # Container
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.addWidget(swatch)
            container_layout.addWidget(label_widget)
            container_layout.setSpacing(5)
            
            colors_layout.addWidget(container, row, col)
            self.color_swatches[label.lower()] = swatch
            
        layout.addWidget(colors_group)
        
        # Color codes
        codes_group = QGroupBox("HEX COLOR CODES")
        codes_group.setObjectName("codes_group")
        codes_layout = QVBoxLayout(codes_group)
        
        self.color_codes_display = QTextEdit()
        self.color_codes_display.setObjectName("color_codes")
        self.color_codes_display.setReadOnly(True)
        codes_layout.addWidget(self.color_codes_display)
        
        layout.addWidget(codes_group)
        
        # Era and Ship Class Palettes
        palette_group = QGroupBox("PALETTE PRESETS")
        palette_group.setObjectName("palette_group")
        palette_layout = QVBoxLayout(palette_group)
        
        # Display current palette colors
        self.current_palette_display = QFrame()
        self.current_palette_display.setFixedHeight(80)
        self.current_palette_layout = QHBoxLayout(self.current_palette_display)
        self.current_palette_layout.setContentsMargins(10, 5, 10, 5)
        self.current_palette_layout.setSpacing(5)
        palette_layout.addWidget(QLabel("Current Era Palette:"))
        palette_layout.addWidget(self.current_palette_display)
        
        # General Era Palettes
        self.general_palette_btn = QPushButton("LOAD ERA PALETTE")
        self.general_palette_btn.setObjectName("general_palette_btn")
        self.general_palette_btn.clicked.connect(self.load_general_palette)
        palette_layout.addWidget(self.general_palette_btn)
        
        # Ship Class Palettes
        self.ship_class_palette_btn = QPushButton("LOAD SHIP CLASS PALETTE")
        self.ship_class_palette_btn.setObjectName("ship_class_palette_btn")
        self.ship_class_palette_btn.clicked.connect(self.load_ship_class_palette)
        palette_layout.addWidget(self.ship_class_palette_btn)
        
        layout.addWidget(palette_group)
        
        self.tabs.addTab(tab, "COLORS")
        
        # Initialize palette display
        self.update_palette_display()
        
    def create_lcars_console_tab(self):
        """Create LCARS console demonstration tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Left side panel
        left_panel = QFrame()
        left_panel.setObjectName("lcars_left")
        left_panel.setFixedWidth(200)
        left_layout = QVBoxLayout(left_panel)
        
        # Status indicators
        status_items = [
            ("SYS", "ONLINE"),
            ("PWR", "NOMINAL"), 
            ("SEC", "GREEN"),
            ("NAV", "READY"),
            ("COM", "ACTIVE")
        ]
        
        for label, status in status_items:
            item_frame = QFrame()
            item_frame.setObjectName("status_item")
            item_layout = QHBoxLayout(item_frame)
            
            label_widget = QLabel(label)
            label_widget.setObjectName("status_label")
            status_widget = QLabel(status)
            status_widget.setObjectName("status_value")
            
            item_layout.addWidget(label_widget)
            item_layout.addWidget(status_widget)
            
            left_layout.addWidget(item_frame)
            
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # Main display
        main_display = QFrame()
        main_display.setObjectName("main_display")
        display_layout = QVBoxLayout(main_display)
        
        # Display title
        display_title = QLabel("MAIN VIEWER")
        display_title.setObjectName("display_title")
        display_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display_layout.addWidget(display_title)
        
        # Console output
        self.console_output = QTextEdit()
        self.console_output.setObjectName("console_output")
        self.console_output.setReadOnly(True)
        display_layout.addWidget(self.console_output)
        
        layout.addWidget(main_display)
        
        self.tabs.addTab(tab, "CONSOLE")
        
            
    def update_time(self):
        """Update time display"""
        # Guard: only update if time_label exists and is not deleted
        if not hasattr(self, 'time_label') or self.time_label is None:
            return
        try:
            _ = self.time_label.objectName()
        except RuntimeError:
            return
        current_time = datetime.now()
        stardate = 2400 + (current_time.year - 2000) * 100 + current_time.timetuple().tm_yday
        time_text = f"{current_time.strftime('%H:%M:%S')}\nSD {stardate:.1f}"
        self.time_label.setText(time_text)

    def show_login_menu(self):
        """Show the login menu, hide main menu"""
        self.login_menu.show()
        self.main_menu.hide()

    def handle_logout(self):
        """Handle user logout, show main menu"""
        self.login_menu.hide()
        self.main_menu.show()

    def transition_to_system_menu(self):
        """Handle system login"""
        print("Transitioning to system menu.")
        self.main_menu.show()
        self.login_menu.hide()

    # Define method to launch LCARS system
    def launch_lcars_system(self):
        # System integration stub (not implemented)
        # try:
        #     from lcars_system import initialize_lcars_main_window
        # except ImportError:
        #     from lcars.lcars_system import initialize_lcars_main_window
        # initialize_lcars_main_window()
        self.close()
    def load_general_palette(self):
        """Load and apply the general era palette"""
        # Guard: only use combo if exists and not deleted
        try:
            faction = self.faction_combo.currentText().lower()
            era_text = self.era_combo.currentText()
        except (AttributeError, RuntimeError):
            return
        # Map era text to era code
        era_mapping = {
            "22nd Century": "22nd",
            "23rd Century": "23rd", 
            "24th Century": "24th",
            "25th Century": "25th",
            "29th Century": "29th",
            "Dominion War": "dominion"
        }
        era = era_mapping.get(era_text, "24th")
        # Build key and apply theme directly; fallback to federation_24th
        faction_era_key = f"{faction}_{era}"
        self.apply_theme(faction_era_key if faction_era_key else 'federation_24th')

    def load_ship_class_palette(self):
        """Load and apply the ship class palette"""
        try:
            ship_name = self.ship_combo.currentText()
        except (AttributeError, RuntimeError):
            return
        # Map ship names to themes
        ship_theme_mapping = {
            "Enterprise NX-01 (NX-01)": "federation_22nd",
            "USS Enterprise (NCC-1701)": "federation_23rd",
            "USS Voyager (NCC-74656)": "federation_24th",
            "USS Defiant (NX-74205)": "federation_24th",
            "USS Enterprise-E (NCC-1701-E) - Sovereign Class": "federation_24th",
            "USS Sovereign (NCC-73811)": "federation_25th"
        }
        faction_era = ship_theme_mapping.get(ship_name, "federation_24th")
        self.apply_theme(faction_era)

    def apply_25th_century_theme(self):
        """Apply theme based on current faction and era selections"""
        # Guard: do not run if combo boxes are missing or deleted
        if not (hasattr(self, 'faction_combo') and hasattr(self, 'era_combo')):
            return
        # PyQt: check if C++ object is deleted
        try:
            _ = self.faction_combo.objectName()
            _ = self.era_combo.objectName()
        except RuntimeError:
            return
            
        # Get selected faction and era
        faction = self.faction_combo.currentText().lower()
        era_text = self.era_combo.currentText()
        
        # Map era text to era values - COMPREHENSIVE MAPPING
        era_mapping = {
            "pre-federation (2150s)": "22nd",
            "22nd century (pcars)": "22nd",
            "early 23rd century (pcars)": "23rd",
            "mid 23rd century (tos)": "23rd",
            "late 23rd century (tmp)": "23rd",
            "early 24th century (tng)": "24th",
            "mid 24th century (ds9)": "24th",
            "late 24th century (voy)": "24th",
            "25th century (pic)": "25th",
            "29th century (tcars)": "29th",
            "alternate timeline": "24th",
            "mirror universe": "24th"
        }
        
        # Get era key
        era_key = "24th"  # default
        for display, key in era_mapping.items():
            if display.lower() in era_text.lower():
                era_key = key
                break
        
        # Apply theme using centralized palette system
        if THEME_SYSTEM_AVAILABLE:
            try:
                colors = get_palette_by_name(era_key)
                
                # Faction-specific color adjustments
                if "klingon" in faction:
                    # Klingon red/orange theme
                    bg_color = colors.get('background', '#1A0000')
                    primary_color = colors.get('button_colors', ['#CC0000'])[0] if colors.get('button_colors') else '#CC0000'
                    accent_color = '#FF6600'
                    text_color = '#FFCC00'
                elif "romulan" in faction:
                    # Romulan green theme
                    bg_color = colors.get('background', '#001A00')
                    primary_color = colors.get('button_colors', ['#00CC00'])[0] if colors.get('button_colors') else '#00CC00'
                    accent_color = '#00FF99'
                    text_color = '#FFFFFF'
                elif "cardassian" in faction:
                    # Cardassian orange/brown theme
                    bg_color = colors.get('background', '#1A0A00')
                    primary_color = colors.get('button_colors', ['#CC6600'])[0] if colors.get('button_colors') else '#CC6600'
                    accent_color = '#FFCC66'
                    text_color = '#FFFF00'
                else:
                    # Starfleet default
                    bg_color = colors.get('background', '#000000')
                    primary_color = colors.get('button_colors', ['#FFCC00'])[0] if colors.get('button_colors') else '#FFCC00'
                    accent_color = colors.get('button_colors', ['#FFCC00'])[1] if colors.get('button_colors') and len(colors.get('button_colors')) > 1 else '#FF9900'
                    text_color = '#FFFFFF'
                
                # Apply comprehensive LCARS styling
                main_style = f"""
                QMainWindow {{
                    background-color: {bg_color};
                    color: {text_color};
                    font-family: 'Eurostile', 'Segoe UI', Arial, sans-serif;
                }}
                QWidget {{
                    background-color: {bg_color};
                    color: {text_color};
                }}
                QFrame {{
                    background-color: {bg_color};
                    border: none;
                }}
                QGroupBox {{
                    background-color: {colors.get('panel_color', bg_color)};
                    border: 2px solid {primary_color};
                    border-radius: 8px;
                    margin: 10px;
                    padding: 15px;
                    font-weight: bold;
                    color: {text_color};
                }}
                QGroupBox::title {{
                    color: {primary_color};
                    font-weight: bold;
                    padding: 5px;
                }}
                QComboBox {{
                    background-color: {colors.get('panel_color', bg_color)};
                    color: {text_color};
                    border: 2px solid {primary_color};
                    border-radius: 4px;
                    padding: 5px;
                    font-weight: bold;
                }}
                QPushButton {{
                    background-color: {primary_color};
                    color: {bg_color};
                    border: 2px solid {primary_color};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {accent_color};
                    color: {bg_color};
                }}
                QPushButton:pressed {{
                    background-color: {colors.get('panel_color', bg_color)};
                    color: {primary_color};
                }}
                QLabel {{
                    color: {text_color};
                    font-weight: bold;
                    background: transparent;
                }}
                QTextEdit {{
                    background-color: {colors.get('panel_color', bg_color)};
                    color: {text_color};
                    border: 1px solid {primary_color};
                    border-radius: 4px;
                }}
                QTabWidget::pane {{
                    border: 2px solid {primary_color};
                    background-color: {colors.get('panel_color', bg_color)};
                }}
                QTabBar::tab {{
                    background-color: {colors.get('panel_color', bg_color)};
                    color: {text_color};
                    border: 2px solid {primary_color};
                    padding: 8px 16px;
                    margin: 2px;
                    border-radius: 6px;
                    font-weight: bold;
                }}
                QTabBar::tab:selected {{
                    background-color: {primary_color};
                    color: {bg_color};
                }}
                QTabBar::tab:hover {{
                    background-color: {accent_color};
                    color: {bg_color};
                }}
                """
                
                self.setStyleSheet(main_style)
                
                # Update displays
                self.update_color_swatches()
                self.update_theme_info()
                
                print(f"Theme applied: {faction.title()} {era_key}")
                
            except Exception as e:
                print(f"Error applying theme: {e}")
                # Fallback to basic black theme
                self.setStyleSheet("QMainWindow { background-color: #000000; color: #FFFFFF; }")
        else:
            # Fallback theme
            self.setStyleSheet("QMainWindow { background-color: #000000; color: #FFFFFF; }")
                    
        # Map faction to theme system
        faction_mapping = {
            "federation": "federation",
            "klingon empire": "klingon",
            "romulan star empire": "romulan",
            "cardassian union": "cardassian",
            "dominion": "dominion",
            "borg collective": "borg",
            "ferengi alliance": "ferengi",
            "vulcan high command": "vulcan",
            "andorian empire": "andorian",
            "tellarite caliphate": "tellarite"
        }
        
        era = era_mapping.get(era_text.lower(), "24th")
        faction_key = faction_mapping.get(faction.lower(), "federation")
        
        # Get theme based on faction and era
        try:
            self.current_theme = get_faction_era_theme(faction_key, era)
        except Exception:
            # Fallback to federation 24th
            self.current_theme = get_theme_by_name('federation', '24th')
        
        # Apply the theme to interface
        self.apply_current_theme()
        
        # Update palette display
        self.update_palette_display()
        
        # Force immediate update of all widgets
        self.update()
        if hasattr(self, 'tabs'):
            self.tabs.update()
        
        # Update LCARS buttons with new colors
        self.update_lcars_buttons_colors()
        
        print(f"Theme applied: {faction_key} {era}")
        
    def apply_current_theme(self):
        """Apply current theme using centralized palette system"""
        if not THEME_SYSTEM_AVAILABLE:
            return
            
        # Get current faction and era
        faction = self.faction_combo.currentText().lower()
        era_text = self.era_combo.currentText().lower()
        
        # Map era to palette key
        era_mapping = {
            "22nd": "22nd",
            "23rd": "23rd", 
            "24th": "24th",
            "25th": "25th",
            "29th": "29th"
        }
        
        palette_key = "24th"  # default
        for key, value in era_mapping.items():
            if key in era_text:
                palette_key = value
                break
        
        # Get colors from centralized system
        try:
            colors = get_palette_by_name(palette_key)
            
            # Apply LCARS styling with faction-specific colors
            main_style = f"""
            QMainWindow {{
                background-color: {colors.get('background', '#000000')};
                color: {colors.get('text', '#FFFFFF')};
            }}
            QWidget {{
                background-color: {colors.get('background', '#000000')};
                color: {colors.get('text', '#FFFFFF')};
            }}
            QGroupBox {{
                background-color: {colors.get('panel_color', colors.get('background', '#000000'))};
                border: 2px solid {colors.get('button_colors', ['#FFCC00'])[0] if colors.get('button_colors') else '#FFCC00'};
                color: {colors.get('text', '#FFFFFF')};
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {colors.get('button_colors', ['#FFCC00'])[0] if colors.get('button_colors') else '#FFCC00'};
                color: {colors.get('text', '#000000')};
                border: 2px solid {colors.get('button_colors', ['#FFCC00'])[0] if colors.get('button_colors') else '#FFCC00'};
                font-weight: bold;
            }}
            QComboBox {{
                background-color: {colors.get('panel_color', colors.get('background', '#000000'))};
                color: {colors.get('text', '#FFFFFF')};
                border: 2px solid {colors.get('button_colors', ['#FFCC00'])[0] if colors.get('button_colors') else '#FFCC00'};
            }}
            QLabel {{
                color: {colors.get('text', '#FFFFFF')};
                background: transparent;
            }}
            """
            
            self.setStyleSheet(main_style)
            
        except Exception as e:
            print(f"Error applying theme: {e}")
        
        self.update_color_swatches()
        
        # Force immediate repaint of all widgets
        self.repaint()
        if hasattr(self, 'tabs'):
            self.tabs.repaint()

    def update_color_swatches(self):
        """Update color swatches directly from centralized palette"""
        if not THEME_SYSTEM_AVAILABLE:
            return
            
        # Get current era
        era_text = self.era_combo.currentText().lower()
        
        # Map era to palette key
        era_mapping = {
            "22nd": "22nd",
            "23rd": "23rd", 
            "24th": "24th",
            "25th": "25th",
            "29th": "29th"
        }
        
        palette_key = "24th"  # default
        for key, value in era_mapping.items():
            if key in era_text:
                palette_key = value
                break
        
        # Get colors directly from centralized system
        try:
            colors = get_palette_by_name(palette_key)
            
            # Update existing color swatches with palette colors
            if hasattr(self, 'color_swatches'):
                # Show all colors from palette directly
                for color_name, color_value in colors.items():
                    if color_name in self.color_swatches:
                        self.color_swatches[color_name].setStyleSheet(f"background-color: {color_value}; border: 1px solid #333;")
                
                # Update color codes display
                if hasattr(self, 'color_codes_display') and self.color_codes_display is not None:
                    color_codes = "\n".join([f"{name.upper()}: {color}" for name, color in colors.items()])
                    self.color_codes_display.setPlainText(color_codes)
                    
        except Exception as e:
            print(f"Error updating color swatches: {e}")
        
        # Update LCARS buttons in elements tab
        if hasattr(self, 'tabs') and self.tabs is not None:
            elements_tab_index = -1
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == "ELEMENTS":
                    elements_tab_index = i
                    break
            
            if elements_tab_index >= 0:
                elements_tab = self.tabs.widget(elements_tab_index)
                if elements_tab:
                    # Find all LCARS buttons and update their colors
                    for child in elements_tab.findChildren(LCARSButton):
                        # Update button era based on current selection
                        current_era_text = self.era_combo.currentText().lower() if hasattr(self, 'era_combo') else "24th century (lcars)"
                        era_mapping = {
                            "22nd century (pcars)": LCARSEra.PCARS_22ND,
                            "23rd century (pcars)": LCARSEra.PCARS_23RD,
                            "23rd century (tmp)": LCARSEra.PCARS_23ST,
                            "24th century (lcars)": LCARSEra.LCARS_24TH,
                            "25th century (lcars)": LCARSEra.LCARS_25TH,
                            "29th century (tcars)": LCARSEra.TCARS_29TH
                        }
                        new_era = era_mapping.get(current_era_text, LCARSEra.LCARS_24TH)
                        child.era = new_era
                        child.apply_theme()
    
    def update_palette_display(self):
        """Update palette display using centralized theme system"""
        if not THEME_SYSTEM_AVAILABLE:
            return
            
        # Get current faction and era
        faction = self.faction_combo.currentText().lower()
        era_text = self.era_combo.currentText().lower()
        
        # Map era to palette key
        era_mapping = {
            "22nd": "22nd",
            "23rd": "23rd", 
            "24th": "24th",
            "25th": "25th",
            "29th": "29th"
        }
        
        palette_key = "24th"  # default
        for key, value in era_mapping.items():
            if key in era_text:
                palette_key = value
                break
        
        # Get colors from centralized system
        try:
            colors = get_palette_by_name(palette_key)
            
            # Clear existing palette display
            if hasattr(self, 'current_palette_layout'):
                for i in reversed(range(self.current_palette_layout.count())):
                    child = self.current_palette_layout.itemAt(i).widget()
                    if child:
                        child.setParent(None)
            
            # Display colors from palette
            if hasattr(self, 'current_palette_layout'):
                # Show button colors from centralized palette
                button_colors = colors.get('button_colors', [])
                
                for i, color in enumerate(button_colors[:8]):  # Show first 8 colors
                    container = QWidget()
                    container_layout = QVBoxLayout(container)
                    container_layout.setSpacing(2)
                    
                    # Color swatch
                    swatch = QFrame()
                    swatch.setFixedSize(35, 35)
                    swatch.setStyleSheet(f"background-color: {color}; border: 2px solid #333;")
                    swatch.setToolTip(f"Color {i+1}: {color}")
                    container_layout.addWidget(swatch)
                    
                    # Color index
                    label = QLabel(f"COL{i+1}")
                    label.setObjectName("color_label")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setStyleSheet("color: #FFFFFF; font-size: 8px; background: transparent;")
                    container_layout.addWidget(label)
                    
                    self.current_palette_layout.addWidget(container)
                
                self.current_palette_layout.addStretch()
                
        except Exception as e:
            print(f"Error updating palette display: {e}")
    
    def update_lcars_buttons_colors(self):
        """Update all LCARS buttons with faction-specific theme colors"""
        if not hasattr(self, 'tabs') or not self.current_theme:
            return
            
        # Find elements tab
        elements_tab_index = -1
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "ELEMENTS":
                elements_tab_index = i
                break
        
        if elements_tab_index >= 0:
            elements_tab = self.tabs.widget(elements_tab_index)
            if elements_tab:
                # Get current faction for styling
                faction = self.faction_combo.currentText().lower()
                
                # Update all LCARS buttons with faction-specific styling
                for child in elements_tab.findChildren(LCARSButton):
                    # Apply current theme colors
                    if hasattr(child, 'apply_theme'):
                        child.apply_theme()
                    
                    # Apply faction-specific styling using centralized theme system
                    if THEME_SYSTEM_AVAILABLE:
                        try:
                            # Get colors from centralized theme system
                            if "klingon" in faction:
                                colors = get_palette_by_name("24th")  # Klingon uses 24th colors
                                child.setStyleSheet(f"background-color: {colors.get('button_colors', ['#8B0000'])[0]}; color: #FFCC00; border: 2px solid #CC0000;")
                            elif "romulan" in faction:
                                colors = get_palette_by_name("24th")  # Romulan uses 24th colors  
                                child.setStyleSheet(f"background-color: {colors.get('button_colors', ['#00FF99'])[0]}; color: #FFFFFF; border: 2px solid #00CC00;")
                            elif "cardassian" in faction:
                                colors = get_palette_by_name("24th")  # Cardassian uses 24th colors
                                child.setStyleSheet(f"background-color: {colors.get('button_colors', ['#8B4513'])[0]}; color: #FFFF00; border: 2px solid #886644;")
                            # Federation uses default theme colors
                        except Exception:
                            pass  # Fallback to default styling
                    
                    child.update()
                    
                    # Update button labels based on faction
                    if hasattr(child, 'setText'):
                        if "klingon" in faction:
                            if "COMMAND" in child.text():
                                child.setText("BATTLE")
                            elif "TACTICAL" in child.text():
                                child.setText("HONOR")
                            elif "SCIENCE" in child.text():
                                child.setText("WARFARE")
                        elif "romulan" in faction:
                            if "COMMAND" in child.text():
                                child.setText("TAL SHIA")
                            elif "TACTICAL" in child.text():
                                child.setText("STEALTH")
                            elif "SCIENCE" in child.text():
                                child.setText("INTEL")
                        elif "borg" in faction:
                            if "COMMAND" in child.text():
                                child.setText("ASSIMILATE")
                            elif "TACTICAL" in child.text():
                                child.setText("ADAPT")
                            elif "SCIENCE" in child.text():
                                child.setText("ANALYZE")
                        elif "cardassian" in faction:
                            if "COMMAND" in child.text():
                                child.setText("ORDER")
                            elif "TACTICAL" in child.text():
                                child.setText("SECURITY")
                            elif "SCIENCE" in child.text():
                                child.setText("INTEL")
                        elif "dominion" in faction:
                            if "COMMAND" in child.text():
                                child.setText("FOUNDERS")
                            elif "TACTICAL" in child.text():
                                child.setText("JEM'HADAR")
                            elif "SCIENCE" in child.text():
                                child.setText("VORTA")
                        elif "ferengi" in faction:
                            if "COMMAND" in child.text():
                                child.setText("PROFIT")
                            elif "TACTICAL" in child.text():
                                child.setText("RULES")
                            elif "SCIENCE" in child.text():
                                child.setText("COMMERCE")
                    
                    child.update()
    
    def load_general_palette(self):
        """Load general era palette"""
        # Get current era selection
        era_text = self.era_combo.currentText()
        era_mapping = {
            "22nd century (pcars)": "22nd",
            "23rd century (pcars)": "23rd",
            "23rd century (tmp)": "23rd",
            "24th century (lcars)": "24th",
            "25th century (lcars)": "25th",
            "29th century (tcars)": "29th"
        }
        
        era = era_mapping.get(era_text.lower(), "24th")
        
        # Apply theme based on era
        try:
            self.current_theme = get_faction_era_theme('federation', era)
            self.apply_current_theme()
            self.update_palette_display()
        except Exception as e:
            print(f"Error loading general palette: {e}")
    
    def load_ship_class_palette(self):
        """Load ship class specific palette"""
        # Get current ship selection
        ship_name = self.ship_combo.currentText()
        
        # Ship specific theme mapping
        ship_theme_mapping = {
            "USS Enterprise (NCC-1701)": "federation_23rd",
            "USS Enterprise-A (NCC-1701-A)": "federation_23rd",
            "USS Enterprise-D (NCC-1701-D)": "federation_24th",
            "USS Enterprise-E (NCC-1701-E)": "federation_24th",
            "USS Voyager (NCC-74656)": "federation_24th",
            "USS Defiant (NX-74205)": "federation_24th",
            "USS Enterprise-E (NCC-1701-E) - Sovereign Class": "federation_25th",
            "USS Sovereign (NCC-73811)": "federation_25th"
        }
        
        faction_era = ship_theme_mapping.get(ship_name, "federation_24th")
        
        try:
            self.current_theme = get_theme_by_name('federation', faction_era.split('_')[1])
            self.apply_current_theme()
            self.update_palette_display()
        except Exception as e:
            print(f"Error loading ship class palette: {e}")


def main():
    """Run the complete theme demonstration"""
    app = QApplication(sys.argv)
    app.setApplicationName("LCARS Full Theme Demo")
    
    demo = FullThemeDemo()
    demo.show()
    
    print("🎨 LCARS Complete Theme Demonstration")
    print("🖖 Canonical Star Trek interface colors")
    print("📊 All factions and eras available")
    print("🚀 Select themes to see authentic LCARS styling")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
# запуск full_theme_demo.py
