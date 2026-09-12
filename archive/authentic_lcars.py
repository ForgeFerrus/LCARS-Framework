"""
Authentic LCARS System - Star Trek Style with Real Theme Integration
"""
import sys
from pathlib import Path

# Fallback LCARS Color Palette (used only if theme system fails)
LCARS_COLORS = {
    "primary_orange": "#FF9900",
    "primary_cyan": "#00CC99", 
    "primary_blue": "#3366CC",
    "secondary_cyan": "#99FFFF",
    "secondary_orange": "#FFCC33",
    "secondary_blue": "#4BBEBF",
    "alert_red": "#FF3333",
    "alert_yellow": "#FFFF00",
    "text_black": "#000000",
    "text_white": "#FFFFFF",
    "background_black": "#000000",
    "panel_gray": "#333333"
}
# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (QApplication, QDialog, QMainWindow, QWidget, 
                            QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                            QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QScreen
import logging
logger = logging.getLogger(__name__)
# Import real theme system (optional)
try:
    from lcars.themes.theme import FactionEra, get_faction_palette
    THEME_AVAILABLE = True
    print("✓ Real theme system loaded successfully")
except Exception as e:
    print(f"⚠ Theme system not available: {e}")
    THEME_AVAILABLE = False

# Provide a safe fallback for get_faction_palette when theme is unavailable
if not THEME_AVAILABLE:
    def get_faction_palette(faction_era):
        return {}

# Minimal fallback factory for FactionEra so module can be imported
if not THEME_AVAILABLE:
    class _FallbackEra:
        def __init__(self, name):
            self.name = name
        def __repr__(self):
            return f"<FactionEra {self.name}>"

    class _EraFactory:
        def __getattr__(self, name):
            return _FallbackEra(name)

    FactionEra = _EraFactory()



def get_real_palette(faction_era=None):
    """Get real palette from theme system or fallback"""
    if faction_era is None:
        faction_era = FactionEra.STARFLEET_25TH

    if LCARS_COLORS:
        try:
            palette = get_faction_palette(faction_era)
            # If palette is a method, call it
            if callable(palette):
                palette = palette()
            # Ensure palette is a dict before using .get()
            if isinstance(palette, dict):
                colors = palette.get('button_colors', [])
                if colors:
                    return {
                        "primary_orange": colors[0],
                        "primary_cyan": colors[1] if len(colors) > 1 else colors[0],
                        "primary_blue": colors[2] if len(colors) > 2 else colors[0],
                        "secondary_cyan": colors[3] if len(colors) > 3 else colors[0],
                        "secondary_orange": colors[4] if len(colors) > 4 else colors[0],
                        "secondary_blue": colors[5] if len(colors) > 5 else colors[0],
                        "alert_red": "#FF3333",
                        "alert_yellow": "#FFFF00",
                        "text_black": "#000000",
                        "text_white": "#FFFFFF",
                        "background_black": "#000000",
                        "panel_gray": "#333333",
                        "button_colors": colors
                    }
            else:
                logger.warning("Palette returned is not a dict: %s", type(palette))
        except Exception as e:
            logger.exception("Unhandled exception while getting palette: %s", e)
            print(f"⚠ Error getting palette: {e}")
    
    # Fallback to hardcoded colors
    return {
        "primary_orange": LCARS_COLORS["primary_orange"],
        "primary_cyan": LCARS_COLORS["primary_cyan"],
        "primary_blue": LCARS_COLORS["primary_blue"],
        "secondary_cyan": LCARS_COLORS["secondary_cyan"],
        "secondary_orange": LCARS_COLORS["secondary_orange"],
        "secondary_blue": LCARS_COLORS["secondary_blue"],
        "alert_red": LCARS_COLORS["alert_red"],
        "alert_yellow": LCARS_COLORS["alert_yellow"],
        "text_black": LCARS_COLORS["text_black"],
        "text_white": LCARS_COLORS["text_white"],
        "background_black": LCARS_COLORS["background_black"],
        "panel_gray": LCARS_COLORS["panel_gray"],
        "button_colors": [LCARS_COLORS["primary_orange"], LCARS_COLORS["primary_cyan"]]
    }

class LCARSElbow(QFrame):
    """Authentic LCARS elbow corner piece with real theme support"""
    def __init__(self, orientation="tl", faction_era=None, color=None, size=(180, 70)):
        super().__init__()
        self.setFixedSize(size[0], size[1])
        
        # Get real palette if color not specified
        if faction_era is None:
            faction_era = FactionEra.STARFLEET_25TH

        if color is None:
            palette = get_real_palette(faction_era)
            color = palette["primary_orange"]
        
        border_radius = ""
        if orientation == "tl":  # top-left
            border_radius = "border-top-left-radius: 50px; border-bottom-left-radius: 4px;"
        elif orientation == "tr":  # top-right  
            border_radius = "border-top-right-radius: 35px; border-bottom-right-radius: 4px;"
        elif orientation == "bl":  # bottom-left
            border_radius = "border-bottom-left-radius: 40px; border-top-left-radius: 6px;"
        elif orientation == "br":  # bottom-right
            border_radius = "border-bottom-right-radius: 40px; border-top-right-radius: 6px;"
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                {border_radius}
            }}
        """)

class LCARSButton(QPushButton):
    """Authentic LCARS button with algorithmic faction-specific styling"""
    def __init__(self, text, faction_era=None, color=None, size=(200, 50), text_color=None):
        super().__init__(text)
        self.setFixedSize(size[0], size[1])
        
        # Use algorithmic styling if faction_era provided
        if faction_era and LCARS_COLORS:
            self.apply_faction_style(text, faction_era, size)
        else:
            # Fallback to manual color
            if color is None:
                color = LCARS_COLORS["primary_cyan"]
            if text_color is None:
                text_color = "#000000"
            self.apply_manual_style(text, color, text_color)
    
    def apply_faction_style(self, text, faction_era, size):
        """Apply algorithmic faction-specific styling"""
        palette = get_real_palette(faction_era)
        colors = palette.get('button_colors', [])
        
        if not colors:
            self.apply_manual_style(text, LCARS_COLORS["primary_cyan"], "#000000")
            return
        
        faction_name = faction_era.name.split('_')[0]
        main_color = colors[0]
        
        # Algorithmic text color based on faction and background
        if faction_name == "STARFLEET":
            text_color = "#000000"  # Dark text on light colors
        elif faction_name == "KLINGON":
            text_color = "#FFFFFF"  # White text on dark colors
        elif faction_name == "ROMULAN":
            text_color = "#FFFFFF"  # White text on green
        elif faction_name == "CARDASSIAN":
            text_color = "#000000"  # Dark text on brown
        else:
            text_color = "#FFFFFF"
        
        # Algorithmic styling based on faction
        if faction_name == "STARFLEET":
            # Starfleet: Clean, rounded, professional
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {main_color};
                    color: {text_color};
                    border: 2px solid {main_color};
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: 'Arial', sans-serif;
                    text-transform: uppercase;
                    padding: 8px;
                }}
                QPushButton:hover {{
                    background-color: #FFFFFF;
                    color: {main_color};
                    border: 2px solid #FFFFFF;
                }}
                QPushButton:pressed {{
                    background-color: {colors[1] if len(colors) > 1 else main_color};
                    color: {text_color};
                }}
            """)
        
        elif faction_name == "KLINGON":
            # Klingon: Sharp, aggressive, angular
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {main_color};
                    color: {text_color};
                    border: 3px solid {colors[1] if len(colors) > 1 else main_color};
                    border-radius: 2px;
                    font-size: 14px;
                    font-weight: 900;
                    font-family: 'Arial Black', sans-serif;
                    text-transform: uppercase;
                    padding: 6px;
                }}
                QPushButton:hover {{
                    background-color: {colors[1] if len(colors) > 1 else main_color};
                    color: #FFFFFF;
                    border: 3px solid #FFFFFF;
                }}
                QPushButton:pressed {{
                    background-color: {colors[2] if len(colors) > 2 else main_color};
                    color: #FFFFFF;
                }}
            """)
        
        elif faction_name == "ROMULAN":
            # Romulan: Elegant, curved, sophisticated
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {main_color};
                    color: {text_color};
                    border: 2px solid {colors[2] if len(colors) > 2 else main_color};
                    border-radius: 12px;
                    font-size: 15px;
                    font-weight: bold;
                    font-family: 'Georgia', serif;
                    font-style: italic;
                    text-transform: uppercase;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: {colors[1] if len(colors) > 1 else main_color};
                    color: #FFFFFF;
                    border: 2px solid {colors[1] if len(colors) > 1 else main_color};
                }}
                QPushButton:pressed {{
                    background-color: {colors[2] if len(colors) > 2 else main_color};
                    color: #FFFFFF;
                }}
            """)
        
        elif faction_name == "CARDASSIAN":
            # Cardassian: Technical, hexagonal, structured
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {main_color};
                    color: {text_color};
                    border: 2px solid {colors[1] if len(colors) > 1 else main_color};
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                    font-family: 'Courier New', monospace;
                    text-transform: uppercase;
                    padding: 7px;
                }}
                QPushButton:hover {{
                    background-color: {colors[2] if len(colors) > 2 else main_color};
                    color: {text_color};
                    border: 2px solid {colors[2] if len(colors) > 2 else main_color};
                }}
                QPushButton:pressed {{
                    background-color: {colors[1] if len(colors) > 1 else main_color};
                    color: #000000;
                }}
            """)
        
        else:
            self.apply_manual_style(text, main_color, text_color)
    
    def apply_manual_style(self, text, color, text_color):
        """Apply manual color styling (fallback)"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: none;
                font-size: 16px;
                font-weight: bold;
                text-transform: uppercase;
                border-radius: 4px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: #FFFFFF;
                color: {color};
            }}
            QPushButton:pressed {{
                background-color: #666666;
                color: #FFFFFF;
            }}
        """)

class LCARSPanel(QFrame):
    """LCARS panel with rounded corners"""
    def __init__(self, color=LCARS_COLORS["secondary_blue"], height=70):
        super().__init__()
        self.setFixedHeight(height)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                border-radius: 4px;
            }}
        """)

class LCARSLabel(QLabel):
    """LCARS text label with proper styling"""
    def __init__(self, text, color=LCARS_COLORS["text_white"], size=16, text_color=None):
        super().__init__(text)
        actual_color = text_color or color
        self.setStyleSheet(f"""
            QLabel {{
                color: {actual_color};
                font-size: {size}px;
                font-weight: bold;
                text-transform: uppercase;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class LCARSLauncher(QDialog):
    """Authentic LCARS launcher dialog with real theme integration"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS System Access")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(100, 100, 1200, 800)
        
        # Center on screen
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)
        
        # Initialize with real theme
        self.current_faction_era = FactionEra.STARFLEET_25TH
        self.selected_faction = "FEDERATION"
        self.selected_era = "25th"
        self._selection = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Clear any existing layout to avoid duplicate layout warnings
        if self.layout():
            for i in reversed(range(self.layout().count())):
                item = self.layout().itemAt(i)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)

        # Get real palette for current faction/era
        palette = get_real_palette(self.current_faction_era)
        
        # Full screen background with faction color
        self.setStyleSheet(f"""
            LCARSLauncher {{
                background-color: {palette['background_black']};
                background-image: none;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 {palette['background_black']}, stop: 1 {palette['panel_gray']});
            }}
        """)
        
        existing_layout = self.layout()
        if existing_layout is None:
            main_layout = QVBoxLayout(self)
        else:
            main_layout = existing_layout
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)
        
        # === HEADER SECTION ===
        header_layout = QHBoxLayout()
        header_layout.setSpacing(4)
        
        # Left elbow with real theme
        elbow_left = LCARSElbow("tl", self.current_faction_era, None, (200, 70))
        header_layout.addWidget(elbow_left)
        
        # Main title panel with real theme
        title_panel = LCARSPanel(palette["secondary_cyan"], 70)
        title_layout = QHBoxLayout(title_panel)
        faction_name = self.current_faction_era.name.replace('_', ' ').title()
        title_label = LCARSLabel(f"{faction_name} - SYSTEM ACCESS", size=28, text_color="#000000")
        title_layout.addWidget(title_label)
        header_layout.addWidget(title_panel, 1)
        
        # Right cap with real theme
        right_cap = LCARSElbow("tr", self.current_faction_era, None, (60, 70))
        header_layout.addWidget(right_cap)
        
        main_layout.addLayout(header_layout)
        
        # === MAIN CONTENT AREA ===
        content_layout = QHBoxLayout()
        content_layout.setSpacing(4)
        
        # === LEFT SIDEBAR ===
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(4)
        
        # Main sidebar panel with real theme
        main_sidebar = QFrame()
        main_sidebar.setFixedWidth(200)
        main_sidebar.setStyleSheet(f"background-color: {palette['secondary_blue']}; border-bottom-left-radius: 80px; border-top-left-radius: 4px;")
        sidebar_layout.addWidget(main_sidebar, 1)
        
        # Status indicator buttons with real theme
        status_colors = [
            palette["secondary_cyan"],
            palette["secondary_orange"], 
            palette["primary_blue"],
            palette["primary_cyan"],
            palette["alert_red"],
            palette["alert_yellow"]
        ]
        
        for i, color in enumerate(status_colors):
            btn = LCARSButton(f"NODE {i+1:02d}", self.current_faction_era, color, (200, 40), None)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch(1)
        
        # Bottom elbow with real theme
        bottom_elbow = LCARSElbow("bl", self.current_faction_era, None, (200, 60))
        sidebar_layout.addWidget(bottom_elbow)
        
        content_layout.addLayout(sidebar_layout)
        
        # === CENTER SELECTION AREA ===
        center_area = QVBoxLayout()
        center_area.setSpacing(20)
        center_area.setContentsMargins(40, 20, 40, 20)
        
        # Faction selection section with real theme
        faction_header = LCARSPanel(palette["secondary_cyan"], 60)
        faction_layout = QHBoxLayout(faction_header)
        faction_title = LCARSLabel("SELECT FACTION ALIGNMENT", size=24, text_color="#000000")
        faction_layout.addWidget(faction_title)
        center_area.addWidget(faction_header)
        
        # Faction buttons with REAL palettes
        faction_grid = QGridLayout()
        faction_grid.setSpacing(20)
        
        if LCARS_COLORS:
            # Real faction options with theme system
            faction_options = [
                ("FEDERATION", FactionEra.STARFLEET_25TH),
                ("KLINGON", FactionEra.KLINGON_24TH),
                ("ROMULAN", FactionEra.ROMULAN_24TH),
                ("CARDASSIAN", FactionEra.CARDASSIAN_24TH)
            ]
            
            for i, (name, faction_era) in enumerate(faction_options):
                # Get real palette for this faction
                faction_palette = get_faction_palette(faction_era)
                colors = faction_palette.get('button_colors', [])
                main_color = colors[0] if colors else '#4BBEBF'
                
                # Create simple button with real palette color
                btn = QPushButton(name)
                btn.setFixedSize(250, 80)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {main_color};
                        color: {'black' if name == 'FEDERATION' else 'white'};
                        border: 2px solid {main_color};
                        border-radius: 8px;
                        font-size: 18px;
                        font-weight: bold;
                        text-transform: uppercase;
                    }}
                    QPushButton:hover {{
                        background-color: white;
                        color: {main_color};
                        border: 2px solid white;
                    }}
                """)
                btn.clicked.connect(lambda checked, f=name, fe=faction_era: self.select_faction(f, fe))
                faction_grid.addWidget(btn, i // 2, i % 2)
                
                # Show palette info
                info = QLabel(f"{len(colors)} colors from theme.py")
                info.setStyleSheet(f"color: {main_color}; font-size: 12px;")
                info.setAlignment(Qt.AlignmentFlag.AlignCenter)
                faction_grid.addWidget(info, i // 2 + 1, i % 2)
        else:
            # Fallback
            btn = QPushButton("THEME SYSTEM UNAVAILABLE")
            btn.setEnabled(False)
            faction_grid.addWidget(btn)
        
        center_area.addLayout(faction_grid)
        
        # Era selection section with real theme
        era_header = LCARSPanel(palette["secondary_cyan"], 60)
        era_layout = QHBoxLayout(era_header)
        era_title = LCARSLabel("SELECT TEMPORAL ERA", size=24, text_color="#000000")
        era_layout.addWidget(era_title)
        center_area.addWidget(era_header)
        
        # Era buttons with real theme
        era_grid = QHBoxLayout()
        era_grid.setSpacing(20)
        
        eras = [
            ("22ND", LCARS_COLORS["primary_blue"], "#000000"),
            ("23RD", LCARS_COLORS["secondary_blue"], "#000000"),
            ("24TH", LCARS_COLORS["secondary_cyan"], "#000000"),
            ("25TH", LCARS_COLORS["secondary_orange"], "#000000"),
            ("29TH", LCARS_COLORS["alert_yellow"], "#000000")
        ]
        
        for era, color, text_color in eras:
            btn = LCARSButton(era, self.current_faction_era, color, (180, 80), text_color)
            btn.clicked.connect(lambda checked, e=era: self.select_era(e))
            era_grid.addWidget(btn)
        
        center_area.addLayout(era_grid)
        center_area.addStretch()
        
        content_layout.addLayout(center_area, 1)
        main_layout.addLayout(content_layout)
        
        # === BOTTOM NAVIGATION BAR ===
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(200, 8, 8, 8)
        nav_layout.setSpacing(15)
        
        # Back button (initially hidden)
        self.back_btn = LCARSButton("RETURN", None, LCARS_COLORS["alert_red"], (200, 56), None)
        self.back_btn.setVisible(False)
        nav_layout.addWidget(self.back_btn)
        
        # Status display
        self.status_label = LCARSLabel("SYSTEM READY - MAKE SELECTION", LCARS_COLORS["secondary_cyan"], 16)
        nav_layout.addWidget(self.status_label, 1)
        
        main_layout.addLayout(nav_layout)
        
        # === FOOTER ===
        footer = QFrame()
        footer.setFixedHeight(40)
        footer.setStyleSheet(f"""
            QFrame {{
                background-color: {LCARS_COLORS['primary_orange']};
                border-bottom-right-radius: 40px;
                border-top-right-radius: 4px;
                margin-left: 200px;
            }}
        """)
        main_layout.addWidget(footer)
        
    def select_faction(self, faction_name, faction_era=None):
        """Handle faction selection with real theme integration"""
        self.selected_faction = faction_name
        
        if faction_era and THEME_AVAILABLE:
            # Update current faction era and refresh UI
            self.current_faction_era = faction_era
            self.status_label.setText(f"FACTION: {faction_name} - REAL THEME LOADED")
            
            # Refresh UI with new theme
            self.refresh_ui_with_theme()
        else:
            self.status_label.setText(f"FACTION: {faction_name} - SELECT ERA")
    
    def refresh_ui_with_theme(self):
        """Refresh UI with current faction theme"""
        # Clear current layout and rebuild with new theme
        layout = self.layout()
        if layout:
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)

        # Rebuild UI with new theme
        self.setup_ui()
    
    def select_era(self, era):
        self.selected_era = era
        self._selection = (self.selected_faction, self.selected_era, 0)

        # Start simulated loading sequence
        self._load_progress = 0
        self.status_label.setText(f"LOADING {self.selected_faction} {era} — {self._load_progress}%")

        # Show cancel/back button during load
        if hasattr(self, 'back_btn'):
            self.back_btn.setVisible(True)
            self.back_btn.clicked.disconnect()
            self.back_btn.clicked.connect(self.cancel_loading)

        self._load_timer = QTimer(self)
        self._load_timer.setInterval(250)
        self._load_timer.timeout.connect(self._update_loading)
        self._load_timer.start()

    def _update_loading(self):
        # Increment and update status
        self._load_progress += 8
        if self._load_progress > 100:
            self._load_progress = 100

        self.status_label.setText(f"LOADING {self.selected_faction} {self.selected_era} — {self._load_progress}%")

        if self._load_progress >= 100:
            # stop timer and accept dialog
            if hasattr(self, '_load_timer'):
                self._load_timer.stop()
            if hasattr(self, 'back_btn'):
                self.back_btn.setVisible(False)
            QTimer.singleShot(300, self.accept)

    def cancel_loading(self):
        # Cancel loading and reset status
        if hasattr(self, '_load_timer'):
            self._load_timer.stop()
        self.status_label.setText("SYSTEM READY - MAKE SELECTION")
        if hasattr(self, 'back_btn'):
            self.back_btn.setVisible(False)
        
    def get_selection(self):
        return self._selection

class LCARSDesktop(QMainWindow):
    """Authentic LCARS desktop interface with real faction themes"""
    def __init__(self, faction, era):
        super().__init__()
        self.faction = faction
        self.era = era
        
        self.setWindowTitle(f"LCARS Desktop - {faction} {era}")
        self.setGeometry(50, 50, 1600, 1000)
        
        # Get real faction era
        faction_era_map = {
            ("FEDERATION", "22ND"): FactionEra.STARFLEET_22ND,
            ("FEDERATION", "23RD"): FactionEra.STARFLEET_23RD,
            ("FEDERATION", "24TH"): FactionEra.STARFLEET_24TH,
            ("FEDERATION", "25TH"): FactionEra.STARFLEET_25TH,
            ("FEDERATION", "29TH"): FactionEra.STARFLEET_29TH,
            ("KLINGON", "22ND"): FactionEra.KLINGON_22ND,
            ("KLINGON", "23RD"): FactionEra.KLINGON_23RD,
            ("KLINGON", "24TH"): FactionEra.KLINGON_24TH,
            ("KLINGON", "25TH"): FactionEra.KLINGON_25TH,
            ("ROMULAN", "22ND"): FactionEra.ROMULAN_22ND,
            ("ROMULAN", "23RD"): FactionEra.ROMULAN_23RD,
            ("ROMULAN", "24TH"): FactionEra.ROMULAN_24TH,
            ("ROMULAN", "25TH"): FactionEra.ROMULAN_25TH,
            ("CARDASSIAN", "22ND"): FactionEra.CARDASSIAN_22ND,
            ("CARDASSIAN", "23RD"): FactionEra.CARDASSIAN_23RD,
            ("CARDASSIAN", "24TH"): FactionEra.CARDASSIAN_24TH,
            ("CARDASSIAN", "25TH"): FactionEra.CARDASSIAN_25TH,
        }
        
        self.faction_era = faction_era_map.get((faction, era), FactionEra.STARFLEET_25TH)
        
        # Get real palette for this faction
        self.palette = get_real_palette(self.faction_era)
        
        # Apply faction-specific background
        self.setStyleSheet(f"background-color: {self.palette['background_black']};")
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Faction-specific interface design
        if self.faction == "KLINGON":
            self.setup_klingon_interface(main_layout)
        elif self.faction == "ROMULAN":
            self.setup_romulan_interface(main_layout)
        elif self.faction == "CARDASSIAN":
            self.setup_cardassian_interface(main_layout)
        else:  # FEDERATION
            self.setup_federation_interface(main_layout)

    def setup_klingon_interface(self, main_layout):
        """Authentic Klingon LCARS interface with sharp angles and red colors"""
        colors = self.palette.get('button_colors', ['#FF0000', '#CC0000', '#990000', '#660000', '#330000', '#000000'])

        # Top header with Klingon LCARS style
        top_layout = QHBoxLayout()
        top_layout.setSpacing(0)

        # Left sharp elbow
        left_elbow = QFrame()
        left_elbow.setFixedSize(200, 70)
        left_elbow.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[0]};
                border: none;
                border-bottom-left-radius: 2px;
            }}
        """)
        top_layout.addWidget(left_elbow)

        # Main title panel
        title_panel = QFrame()
        title_panel.setFixedHeight(70)
        title_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[1]};
                border: none;
            }}
        """)
        title_layout = QHBoxLayout(title_panel)
        title_label = QLabel("KLINGON EMPIRE COMMAND")
        title_label.setStyleSheet(f"""
            color: white;
            font-size: 24px;
            font-weight: 900;
            font-family: 'Arial Black';
            text-transform: uppercase;
        """)
        title_layout.addWidget(title_label)
        top_layout.addWidget(title_panel, 1)

        # Right sharp cap
        right_cap = QFrame()
        right_cap.setFixedSize(80, 70)
        right_cap.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[2]};
                border: none;
                border-bottom-right-radius: 2px;
            }}
        """)
        top_layout.addWidget(right_cap)

        main_layout.addLayout(top_layout)

        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(4)

        # Left control panel with Klingon LCARS design
        left_panel = QVBoxLayout()
        left_panel.setSpacing(4)

        # Status display panel
        status_panel = QFrame()
        status_panel.setFixedHeight(100)
        status_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[3]};
                border: 2px solid {colors[0]};
                border-radius: 2px;
            }}
        """)
        status_layout = QVBoxLayout(status_panel)
        status_title = QLabel("SYSTEM STATUS")
        status_title.setStyleSheet(f"""
            color: white;
            font-size: 16px;
            font-weight: 900;
            font-family: 'Arial Black';
        """)
        status_layout.addWidget(status_title)

        status_text = QLabel("ALL SYSTEMS OPERATIONAL")
        status_text.setStyleSheet(f"""
            color: {colors[4]};
            font-size: 14px;
            font-weight: bold;
        """)
        status_layout.addWidget(status_text)
        left_panel.addWidget(status_panel)

        # Klingon control buttons
        controls = [
            ("WEAPONS", colors[0]),
            ("SHIELDS", colors[1]),
            ("TACTICAL", colors[2]),
            ("CLOAK", colors[3]),
            ("ENGINEERING", colors[4]),
            ("COMMUNICATIONS", colors[5])
        ]

        for control, color in controls:
            btn = QPushButton(control)
            btn.setFixedHeight(50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: 2px solid {colors[(controls.index((control, color)) + 1) % len(colors)]};
                    border-radius: 2px;
                    font-family: 'Arial Black';
                    font-weight: 900;
                    font-size: 12px;
                    text-transform: uppercase;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {color};
                    border: 2px solid white;
                }}
            """)
            left_panel.addWidget(btn)

        left_panel.addStretch(1)

        # Bottom sharp elbow
        bottom_elbow = QFrame()
        bottom_elbow.setFixedSize(200, 60)
        bottom_elbow.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[0]};
                border: none;
                border-top-left-radius: 2px;
            }}
        """)
        left_panel.addWidget(bottom_elbow)

        content_layout.addLayout(left_panel)

        # Center display area
        center_display = QFrame()
        center_display.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border: 2px solid {colors[2]};
                border-radius: 2px;
            }}
        """)
        center_layout = QVBoxLayout(center_display)

        # Main viewer
        viewer = QFrame()
        viewer.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 1px solid {colors[3]};
                border-radius: 2px;
            }}
        """)
        viewer.setFixedHeight(400)
        center_layout.addWidget(viewer, 1)

        # Data display
        data_text = QLabel("KLINGON EMPIRE - TACTICAL DISPLAY")
        data_text.setStyleSheet(f"""
            color: {colors[4]};
            font-size: 18px;
            font-weight: bold;
            font-family: 'Arial Black';
        """)
        data_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(data_text)

        content_layout.addWidget(center_display, 1)

        # Right panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(4)

        # Alert panel
        alert_panel = QFrame()
        alert_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[5]};
                border: 2px solid {colors[0]};
                border-radius: 2px;
            }}
        """)
        alert_layout = QVBoxLayout(alert_panel)
        alert_title = QLabel("ALERT STATUS")
        alert_title.setStyleSheet(f"""
            color: white;
            font-size: 14px;
            font-weight: 900;
            font-family: 'Arial Black';
        """)
        alert_layout.addWidget(alert_title)

        alert_status = QLabel("GREEN - ALL CLEAR")
        alert_status.setStyleSheet(f"""
            color: #00FF00;
            font-size: 12px;
            font-weight: bold;
        """)
        alert_layout.addWidget(alert_status)
        right_panel.addWidget(alert_panel)

        right_panel.addStretch(1)

        content_layout.addLayout(right_panel)

        main_layout.addLayout(content_layout, 1)

    def setup_romulan_interface(self, main_layout):
        """Authentic Romulan LCARS interface with elegant curves and green colors"""
        colors = self.palette.get('button_colors', ['#00FF00', '#00CC00', '#009900', '#006600', '#003300', '#001100'])
        
        # Top header with Romulan LCARS style - elegant curves
        top_layout = QHBoxLayout()
        top_layout.setSpacing(0)
        
        # Left curved elbow
        left_elbow = QFrame()
        left_elbow.setFixedSize(200, 70)
        left_elbow.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[0]};
                border: none;
                border-bottom-left-radius: 15px;
            }}
        """)
        top_layout.addWidget(left_elbow)
        
        # Main title panel
        title_panel = QFrame()
        title_panel.setFixedHeight(70)
        title_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors[1]}, stop:0.5 {colors[2]}, stop:1 {colors[1]});
                border: none;
            }}
        """)
        title_layout = QHBoxLayout(title_panel)
        title_label = QLabel("ROMULAN STAR EMPIRE")
        title_label.setStyleSheet(f"""
            color: white;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Georgia';
            font-style: italic;
            text-transform: uppercase;
        """)
        title_layout.addWidget(title_label)
        top_layout.addWidget(title_panel, 1)
        
        # Right curved cap
        right_cap = QFrame()
        right_cap.setFixedSize(80, 70)
        right_cap.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[3]};
                border: none;
                border-bottom-right-radius: 12px;
            }}
        """)
        top_layout.addWidget(right_cap)
        
        main_layout.addLayout(top_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(6)
        
        # Left control panel with Romulan LCARS design
        left_panel = QVBoxLayout()
        left_panel.setSpacing(6)
        
        # Elegant status display
        status_panel = QFrame()
        status_panel.setFixedHeight(100)
        status_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors[2]}, stop:1 {colors[3]});
                border: 2px solid {colors[0]};
                border-radius: 12px;
            }}
        """)
        status_layout = QVBoxLayout(status_panel)
        status_title = QLabel("EMPIRE STATUS")
        status_title.setStyleSheet(f"""
            color: white;
            font-size: 16px;
            font-weight: bold;
            font-family: 'Georgia';
            font-style: italic;
        """)
        status_layout.addWidget(status_title)
        
        status_text = QLabel("CLOAKING SYSTEMS ACTIVE")
        status_text.setStyleSheet(f"""
            color: {colors[4]};
            font-size: 14px;
            font-weight: bold;
            font-family: 'Georgia';
        """)
        status_layout.addWidget(status_text)
        left_panel.addWidget(status_panel)
        
        # Romulan control buttons
        controls = [
            ("CLOAK", colors[0]),
            ("DECOY", colors[1]), 
            ("WARBIRD", colors[2]),
            ("SCIENCE", colors[3]),
            ("TAL SHIAR", colors[4]),
            ("SENATE", colors[5])
        ]
        
        for control, color in controls:
            btn = QPushButton(control)
            btn.setFixedHeight(50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color}, stop:0.7 {colors[(controls.index((control, color)) + 1) % len(colors)]});
                    color: white;
                    border: 2px solid {colors[(controls.index((control, color)) + 2) % len(colors)]};
                    border-radius: 12px;
                    font-family: 'Georgia';
                    font-style: italic;
                    font-weight: bold;
                    font-size: 12px;
                    text-transform: uppercase;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 white, stop:1 {colors[(controls.index((control, color)) + 1) % len(colors)]});
                    color: {color};
                    border: 2px solid white;
                }}
            """)
            left_panel.addWidget(btn)
        
        left_panel.addStretch(1)
        
        # Bottom curved elbow
        bottom_elbow = QFrame()
        bottom_elbow.setFixedSize(200, 60)
        bottom_elbow.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[0]};
                border: none;
                border-top-left-radius: 15px;
            }}
        """)
        left_panel.addWidget(bottom_elbow)
        
        content_layout.addLayout(left_panel)
        
        # Center display area
        center_display = QFrame()
        center_display.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #000000, stop:1 {colors[2]});
                border: 2px solid {colors[3]};
                border-radius: 12px;
            }}
        """)
        center_layout = QVBoxLayout(center_display)
        
        # Main viewer
        viewer = QFrame()
        viewer.setStyleSheet(f"""
            QFrame {{
                background-color: #0A0A0A;
                border: 1px solid {colors[4]};
                border-radius: 8px;
            }}
        """)
        viewer.setFixedHeight(400)
        center_layout.addWidget(viewer, 1)
        
        # Data display
        data_text = QLabel("ROMULAN EMPIRE - STEALTH OPERATIONS")
        data_text.setStyleSheet(f"""
            color: {colors[4]};
            font-size: 18px;
            font-weight: bold;
            font-family: 'Georgia';
            font-style: italic;
        """)
        data_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(data_text)
        
        content_layout.addWidget(center_display, 1)
        
        # Right panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(6)
        
        # Intelligence panel
        intel_panel = QFrame()
        intel_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors[5]}, stop:1 {colors[0]});
                border: 2px solid {colors[3]};
                border-radius: 12px;
            }}
        """)
        intel_layout = QVBoxLayout(intel_panel)
        intel_title = QLabel("TAL SHIAR INTEL")
        intel_title.setStyleSheet(f"""
            color: white;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Georgia';
            font-style: italic;
        """)
        intel_layout.addWidget(intel_title)
        
        intel_status = QLabel("CLASSIFIED - LEVEL ALPHA")
        intel_status.setStyleSheet(f"""
            color: #00FF00;
            font-size: 12px;
            font-weight: bold;
            font-family: 'Georgia';
        """)
        intel_layout.addWidget(intel_status)
        right_panel.addWidget(intel_panel)
        
        right_panel.addStretch(1)
        
        content_layout.addLayout(right_panel)
        
        main_layout.addLayout(content_layout, 1)

    def setup_cardassian_interface(self, main_layout):
        """Authentic Cardassian LCARS interface with hexagonal patterns and brown colors"""
        colors = self.palette.get('button_colors', ['#8B4513', '#A0522D', '#CD853F', '#DEB887', '#F4A460', '#D2691E'])
        
        # Top header with Cardassian LCARS style - technical hexagonal
        top_layout = QHBoxLayout()
        top_layout.setSpacing(0)
        
        # Left technical elbow
        left_elbow = QFrame()
        left_elbow.setFixedSize(200, 70)
        left_elbow.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[0]};
                border: none;
                border-bottom-left-radius: 6px;
                border-bottom: 3px solid {colors[1]};
                border-left: 3px solid {colors[1]};
            }}
        """)
        top_layout.addWidget(left_elbow)
        
        # Main title panel
        title_panel = QFrame()
        title_panel.setFixedHeight(70)
        title_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors[1]}, stop:0.3 {colors[2]}, stop:0.6 {colors[3]}, stop:1 {colors[1]});
                border: none;
                border-bottom: 2px solid {colors[2]};
            }}
        """)
        title_layout = QHBoxLayout(title_panel)
        title_label = QLabel("CARDASSIAN UNION")
        title_label.setStyleSheet(f"""
            color: black;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Courier New';
            text-transform: uppercase;
        """)
        title_layout.addWidget(title_label)
        top_layout.addWidget(title_panel, 1)
        
        # Right technical cap
        right_cap = QFrame()
        right_cap.setFixedSize(80, 70)
        right_cap.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[3]};
                border: none;
                border-bottom-right-radius: 6px;
                border-bottom: 3px solid {colors[2]};
                border-right: 3px solid {colors[2]};
            }}
        """)
        top_layout.addWidget(right_cap)
        
        main_layout.addLayout(top_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(4)
        
        # Left control panel with Cardassian LCARS design
        left_panel = QVBoxLayout()
        left_panel.setSpacing(4)
        
        # Technical status display
        status_panel = QFrame()
        status_panel.setFixedHeight(100)
        status_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors[2]}, stop:1 {colors[3]});
                border: 2px solid {colors[0]};
                border-radius: 6px;
            }}
        """)
        status_layout = QVBoxLayout(status_panel)
        status_title = QLabel("UNION STATUS")
        status_title.setStyleSheet(f"""
            color: black;
            font-size: 16px;
            font-weight: bold;
            font-family: 'Courier New';
        """)
        status_layout.addWidget(status_title)
        
        status_text = QLabel("OBSIDIAN ORDER ONLINE")
        status_text.setStyleSheet(f"""
            color: {colors[4]};
            font-size: 14px;
            font-weight: bold;
            font-family: 'Courier New';
        """)
        status_layout.addWidget(status_text)
        left_panel.addWidget(status_panel)
        
        # Cardassian control buttons
        controls = [
            ("ORDER", colors[0]),
            ("GUL", colors[1]), 
            ("DETAPA", colors[2]),
            ("SCIENCE", colors[3]),
            ("MILITARY", colors[4]),
            ("OBSIDIAN", colors[5])
        ]
        
        for control, color in controls:
            btn = QPushButton(control)
            btn.setFixedHeight(50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color}, stop:0.5 {colors[(controls.index((control, color)) + 1) % len(colors)]}, stop:1 {color});
                    color: black;
                    border: 2px solid {colors[(controls.index((control, color)) + 2) % len(colors)]};
                    border-radius: 6px;
                    font-family: 'Courier New';
                    font-weight: bold;
                    font-size: 12px;
                    text-transform: uppercase;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 white, stop:0.5 {colors[(controls.index((control, color)) + 1) % len(colors)]}, stop:1 white);
                    color: black;
                    border: 2px solid {colors[(controls.index((control, color)) + 2) % len(colors)]};
                }}
            """)
            left_panel.addWidget(btn)
        
        left_panel.addStretch(1)
        
        # Bottom technical elbow
        bottom_elbow = QFrame()
        bottom_elbow.setFixedSize(200, 60)
        bottom_elbow.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[0]};
                border: none;
                border-top-left-radius: 6px;
                border-top: 3px solid {colors[1]};
                border-left: 3px solid {colors[1]};
            }}
        """)
        left_panel.addWidget(bottom_elbow)
        
        content_layout.addLayout(left_panel)
        
        # Center display area
        center_display = QFrame()
        center_display.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #000000, stop:1 {colors[2]});
                border: 2px solid {colors[3]};
                border-radius: 6px;
            }}
        """)
        center_layout = QVBoxLayout(center_display)
        
        # Main viewer
        viewer = QFrame()
        viewer.setStyleSheet(f"""
            QFrame {{
                background-color: #0A0A0A;
                border: 1px solid {colors[4]};
                border-radius: 4px;
            }}
        """)
        viewer.setFixedHeight(400)
        center_layout.addWidget(viewer, 1)
        
        # Data display
        data_text = QLabel("CARDASSIAN UNION - CENTRAL COMMAND")
        data_text.setStyleSheet(f"""
            color: {colors[4]};
            font-size: 18px;
            font-weight: bold;
            font-family: 'Courier New';
        """)
        data_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(data_text)
        
        content_layout.addWidget(center_display, 1)
        
        # Right panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(4)
        
        # Order panel
        order_panel = QFrame()
        order_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors[5]}, stop:1 {colors[0]});
                border: 2px solid {colors[3]};
                border-radius: 6px;
            }}
        """)
        order_layout = QVBoxLayout(order_panel)
        order_title = QLabel("OBSIDIAN ORDER")
        order_title.setStyleSheet(f"""
            color: black;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Courier New';
        """)
        order_layout.addWidget(order_title)
        
        order_status = QLabel("CLASSIFIED - LEVEL DELTA")
        order_status.setStyleSheet(f"""
            color: #FF6600;
            font-size: 12px;
            font-weight: bold;
            font-family: 'Courier New';
        """)
        order_layout.addWidget(order_status)
        right_panel.addWidget(order_panel)
        
        right_panel.addStretch(1)
        
        content_layout.addLayout(right_panel)
        
        main_layout.addLayout(content_layout, 1)

    def setup_federation_interface(self, main_layout):
        """Authentic Federation LCARS interface with clean rounded design"""
        colors = self.palette.get('button_colors', [])
        
        # Top header with Federation LCARS style - clean rounded
        top_layout = QHBoxLayout()
        top_layout.setSpacing(0)
        
        # Left rounded elbow
        left_elbow = QFrame()
        left_elbow.setFixedSize(200, 70)
        left_elbow.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[0]};
                border: none;
                border-bottom-left-radius: 50px;
            }}
        """)
        top_layout.addWidget(left_elbow)
        
        # Main title panel
        title_panel = QFrame()
        title_panel.setFixedHeight(70)
        title_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors[1]}, stop:0.5 {colors[2]}, stop:1 {colors[1]});
                border: none;
            }}
        """)
        title_layout = QHBoxLayout(title_panel)
        title_label = QLabel("UNITED FEDERATION")
        title_label.setStyleSheet(f"""
            color: black;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Arial';
            text-transform: uppercase;
        """)
        title_layout.addWidget(title_label)
        top_layout.addWidget(title_panel, 1)
        
        # Right rounded cap
        right_cap = QFrame()
        right_cap.setFixedSize(80, 70)
        right_cap.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[3]};
                border: none;
                border-bottom-right-radius: 35px;
            }}
        """)
        top_layout.addWidget(right_cap)
        
        main_layout.addLayout(top_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(4)
        
        # Left control panel with Federation LCARS design
        left_panel = QVBoxLayout()
        left_panel.setSpacing(4)
        
        # Clean status display
        status_panel = QFrame()
        status_panel.setFixedHeight(100)
        status_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors[2]}, stop:1 {colors[3]});
                border: 2px solid {colors[0]};
                border-radius: 10px;
            }}
        """)
        status_layout = QVBoxLayout(status_panel)
        status_title = QLabel("FEDERATION STATUS")
        status_title.setStyleSheet(f"""
            color: black;
            font-size: 16px;
            font-weight: bold;
            font-family: 'Arial';
        """)
        status_layout.addWidget(status_title)
        
        status_text = QLabel("STARFLEET SYSTEMS ONLINE")
        status_text.setStyleSheet(f"""
            color: {colors[4]};
            font-size: 14px;
            font-weight: bold;
            font-family: 'Arial';
        """)
        status_layout.addWidget(status_text)
        left_panel.addWidget(status_panel)
        
        # Federation control buttons
        controls = [
            ("COMMAND", colors[0]),
            ("SCIENCE", colors[1]), 
            ("TACTICAL", colors[2]),
            ("ENGINEERING", colors[3]),
            ("MEDICAL", colors[4]),
            ("DIPLOMACY", colors[5])
        ]
        
        for control, color in controls:
            btn = QPushButton(control)
            btn.setFixedHeight(50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color}, stop:0.7 {colors[(controls.index((control, color)) + 1) % len(colors)]});
                    color: black;
                    border: 2px solid {colors[(controls.index((control, color)) + 2) % len(colors)]};
                    border-radius: 8px;
                    font-family: 'Arial';
                    font-weight: bold;
                    font-size: 12px;
                    text-transform: uppercase;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 white, stop:0.7 {colors[(controls.index((control, color)) + 1) % len(colors)]});
                    color: {color};
                    border: 2px solid white;
                }}
            """)
            left_panel.addWidget(btn)
        
        left_panel.addStretch(1)
        
        # Bottom rounded elbow
        bottom_elbow = QFrame()
        bottom_elbow.setFixedSize(200, 60)
        bottom_elbow.setStyleSheet(f"""
            QFrame {{
                background-color: {colors[0]};
                border: none;
                border-top-left-radius: 40px;
            }}
        """)
        left_panel.addWidget(bottom_elbow)
        
        content_layout.addLayout(left_panel)
        
        # Center display area
        center_display = QFrame()
        center_display.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #000000, stop:1 {colors[2]});
                border: 2px solid {colors[3]};
                border-radius: 10px;
            }}
        """)
        center_layout = QVBoxLayout(center_display)
        
        # Main viewer
        viewer = QFrame()
        viewer.setStyleSheet(f"""
            QFrame {{
                background-color: #0A0A0A;
                border: 1px solid {colors[4]};
                border-radius: 8px;
            }}
        """)
        viewer.setFixedHeight(400)
        center_layout.addWidget(viewer, 1)
        
        # Data display
        data_text = QLabel("UNITED FEDERATION - STARFLEET COMMAND")
        data_text.setStyleSheet(f"""
            color: {colors[4]};
            font-size: 18px;
            font-weight: bold;
            font-family: 'Arial';
        """)
        data_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(data_text)
        
        content_layout.addWidget(center_display, 1)
        
        # Right panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(4)
        
        # Federation panel
        fed_panel = QFrame()
        fed_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors[5]}, stop:1 {colors[0]});
                border: 2px solid {colors[3]};
                border-radius: 10px;
            }}
        """)
        fed_layout = QVBoxLayout(fed_panel)
        fed_title = QLabel("STARFLEET STATUS")
        fed_title.setStyleSheet(f"""
            color: black;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Arial';
        """)
        fed_layout.addWidget(fed_title)
        
        fed_status = QLabel("ALL SYSTEMS NOMINAL")
        fed_status.setStyleSheet(f"""
            color: #00FF00;
            font-size: 12px;
            font-weight: bold;
            font-family: 'Arial';
        """)
        fed_layout.addWidget(fed_status)
        right_panel.addWidget(fed_panel)
        
        right_panel.addStretch(1)
        
        content_layout.addLayout(right_panel)
        
        main_layout.addLayout(content_layout, 1)

        # (clean up) ensure center_display is used as part of the main layout
        center_display.addStretch()
        main_layout.addWidget(center_display)
        
        # === BOTTOM STATUS BAR ===
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(4)
        
        # Left status
        left_status = LCARSElbow("bl", LCARS_COLORS["primary_orange"], (300, 50))
        bottom_bar.addWidget(left_status)
        
        # Center status
        center_status = LCARSPanel(LCARS_COLORS["secondary_cyan"], 50)
        center_layout = QHBoxLayout(center_status)
        status_text = LCARSLabel(f"STARDATE: 58432.7 - {self.faction} {self.era} SYSTEM READY", size=18, text_color="#000000")
        center_layout.addWidget(status_text)
        bottom_bar.addWidget(center_status, 1)
        
        # Right status
        right_status = LCARSElbow("br", LCARS_COLORS["primary_blue"], (150, 50))
        bottom_bar.addWidget(right_status)
        
        main_layout.addLayout(bottom_bar)

def main():
    print("=== AUTHENTIC LCARS SYSTEM INITIALIZATION ===")
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    # Show launcher
    launcher = LCARSLauncher()
    launcher.show()

    if launcher.exec() == QDialog.DialogCode.Accepted:
        selection = launcher.get_selection()
        if selection:
            faction, era, _ = selection
            print(f"Launching LCARS Desktop: {faction} {era}")

            desktop = LCARSDesktop(faction, era)
            desktop.show()

            print("LCARS System Fully Operational")
            app.exec()
    else:
        print("System initialization cancelled")

if __name__ == "__main__":
    main()
