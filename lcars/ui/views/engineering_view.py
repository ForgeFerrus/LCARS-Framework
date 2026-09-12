from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from lcars.themes.palette import get_theme, LCARSEra
from lcars.ui.base.authentic import LCARSComplexElbow, WarpCoreStatus
from lcars.ui.base.widgets import LCARSElbow, LCARSButton # Mix in standard widgets where appropriate

class EngineeringView(QWidget):
    """
    High-fidelity Engineering View mimicking the 24th Century layout.
    Features: Warp Core Status, Impulse Engines, and complex LCARS elbow layouts.
    Strict Colors: Uses get_theme(LCARS_24TH) palette exclusively.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")
        
        # --- PALETTE SETUP ---
        # Rigorous adherence to LCARS 25th Century Palette (TNG/VOY)
        self.era = LCARSEra.LCARS_25TH
        self.theme = get_theme(self.era)
        # TNG Engineering Colors:
        # Heavily uses Gold/Tan (#FFCC66, #FF9900) for structural
        # Red (#CD6363) for alerts/heavy systems
        # Blue/Periwinkle (#9999FF, #99CCFF) for sensor/readout systems
        self.palette = self.theme.get("button_colors", ["#FF9900", "#CC6666", "#99CCFF"])

        # Mapping indices to functions
        self.col_primary = self.palette[1]  # Orange/Gold (Main Structure)
        self.col_secondary = self.palette[8] if len(self.palette) > 8 else "#99CCFF" # Light Blue (Scanners/Field)
        self.col_tertiary = self.palette[0] # Tan/Beige (Backgrounds/Minor)
        self.col_heavy = self.palette[6] if len(self.palette) > 6 else "#CC0000" # Red (Impulse/Power)
        self.col_header = self.palette[4] if len(self.palette) > 4 else "#FFCC00" # Yellow
        
        # Main Layout: 3 Columns
        # Left: Systems Monitor (Impulse / Life Support)
        # Center: Warp Core
        # Right: Engineering Readouts
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # --- LEFT COLUMN ---
        col_left = QVBoxLayout()
        col_left.setSpacing(5)
        
        # Impulse Status Panel (Top Left) - Heavy System -> RED/RUST
        impulse_panel = self.create_system_panel("IMPULSE PROPULSION", self.col_heavy, "top-left")
        col_left.addWidget(impulse_panel)
        
        # Life Support Panel (Bottom Left) - Critical -> TERTIARY/TAN
        life_support = self.create_system_panel("LIFE SUPPORT", self.col_tertiary, "bottom-left")
        col_left.addWidget(life_support)
        
        layout.addLayout(col_left, 1) # Stretch factor 1
        
        # --- CENTER COLUMN (WARP CORE) ---
        col_center = QVBoxLayout()
        col_center.setSpacing(0)
        
        # Header for Warp Core
        header = QLabel("MATTER / ANTIMATTER REACTION ASSEMBLY")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"color: {self.col_primary}; font-family: Impact; font-size: 24px; letter-spacing: 2px;")
        col_center.addWidget(header)
        
        # The Core Widget
        self.core = WarpCoreStatus(era=self.era)
        col_center.addWidget(self.core, 1) # Make it expand
        
        layout.addLayout(col_center, 2) # Stretch factor 2 (wider)
        
        # --- RIGHT COLUMN ---
        col_right = QVBoxLayout()
        col_right.setSpacing(5)
        
        # Warp Field Coils (Top Right) - Field/Sensor -> BLUE
        warp_coils = self.create_system_panel("WARP FIELD COILS", self.col_secondary, "top-right")
        col_right.addWidget(warp_coils)
        
        # Dilithium Chamber (Bottom Right) - Power -> PRIMARY/GOLD
        dilithium = self.create_system_panel("DILITHIUM CHAMBER", self.col_primary, "bottom-right")
        col_right.addWidget(dilithium)
        
        layout.addLayout(col_right, 1)

        # Animation Loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animations)
        self.timer.start(50)

    def create_system_panel(self, title, color, corner):
        """Creates a panel framed by complex elbows."""
        container = QFrame()
        # No background on container, we draw valid LCARS shapes
        
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(2)
        
        # Create an elbow frame
        elbow = LCARSComplexElbow(
            color=color,
            direction=corner,
            radius=60,
            thickness=25,
            arm_h=200,
            arm_v=150,
            text=title,
            text_color="black",
            era=self.era
        )
        
        # Determine alignment
        if "top" in corner:
            vbox.addWidget(elbow)
            vbox.addStretch()
            # Add some dummy data blocks below
            for i in range(3):
                lbl = QLabel(f"SYS-40{i}   ONLINE")
                lbl.setStyleSheet(f"color: {color}; font-family: Arial; font-size: 14px; margin-left: 30px;")
                vbox.addWidget(lbl)
        else:
            vbox.addStretch()
            # Add some dummy data blocks above
            for i in range(3):
                lbl = QLabel(f"AUX-90{i}   STANDBY")
                lbl.setStyleSheet(f"color: {color}; font-family: Arial; font-size: 14px; margin-left: 30px;")
                vbox.addWidget(lbl)
            vbox.addWidget(elbow)

        return container

    def update_animations(self):
        # Update warp core
        self.core.timer_val += 1
        self.core.update()
