"""
LCARS Faction Selection Interface
Initial screen for choosing allegiance/theme.
"""
import sys
from pathlib import Path

# Додаємо корінь проекту до шляху Python
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor, QFont

# Спроба імпортувати lcars_widgets з обробкою помилки
try:
    from lcars.ui.lcars_widgets import LcarsTile, LcarsElbow
    LCARS_WIDGETS_AVAILABLE = True
except ImportError:
    LCARS_WIDGETS_AVAILABLE = False
    # Створюємо прості заміни якщо lcars_widgets недоступні
    class LcarsTile(QFrame):
        def __init__(self, text, color, callback=None):
            super().__init__()
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border: none;
                    border-radius: 15px;
                }}
            """)
            layout = QVBoxLayout(self)
            label = QLabel(text)
            label.setStyleSheet("color: black; font-weight: bold; font-size: 16px;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            if callback:
                self.mousePressEvent = lambda e: callback()
    
    class LcarsElbow(QFrame):
        def __init__(self, color, direction="right", pos=None):
            super().__init__()
            self.setFixedSize(60, 60)
            self.color = color
            self.update_style(color, direction)

        def update_style(self, color, direction):
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border: none;
                    border-{direction}-radius: 30px;
                }}
            """)
            
        def set_color(self, color):
            # Handle QColor or string
            if hasattr(color, "name"):
                c = color.name()
            else:
                c = str(color)
            self.color = c
            # Assuming 'top-left' as default or parsing current style is hard.
            # We will just update background color which is enough for visual.
            # But update_style needs direction. We'll default to top-left if not stored.
            # Ideally store direction.
            self.setStyleSheet(f"background-color: {c}; border-top-left-radius: 30px;") 

class FactionSelector(QWidget):
    """Faction Selection Screen"""
    factionSelected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setup_ui()
        
    def setup_ui(self):
        # Background
        self.setStyleSheet("background-color: #000000;")
        
        # Main Horizontal Layout
        h_layout = QHBoxLayout(self)
        h_layout.setContentsMargins(20, 20, 20, 20)
        h_layout.setSpacing(10)
        
        # 1. Left Sidebar
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(5)
        
        # Elbow
        self.elbow = LcarsElbow("#FF9900", "top-left", (150, 80))
        sidebar_layout.addWidget(self.elbow)
        
        # Vertical Bar
        self.v_bar = QFrame()
        self.v_bar.setFixedWidth(40)
        self.v_bar.setStyleSheet("background-color: #FF9900; border-radius: 0px;")
        self.v_bar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sidebar_layout.addWidget(self.v_bar)
        
        # Bottom decorative block
        bottom_block = QFrame()
        bottom_block.setFixedSize(150, 60)
        bottom_block.setStyleSheet("background-color: #CC6600; border-radius: 0px; border-bottom-left-radius: 30px;")
        sidebar_layout.addWidget(bottom_block)
        
        h_layout.addLayout(sidebar_layout)
        
        # 2. Main Content Area
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header Bar
        self.header_bar = QFrame()
        self.header_bar.setFixedHeight(40)
        self.header_bar.setStyleSheet("background-color: #FF9900; border-top-right-radius: 20px;")
        
        # Header Title Layout inside the bar
        title_layout = QHBoxLayout(self.header_bar)
        title_layout.setContentsMargins(20, 0, 0, 0)
        self.title_label = QLabel("SYSTEM ACCESS AUTHORIZATION")
        self.title_label.setStyleSheet("color: black; font-family: 'Swis721 BT'; font-size: 24px; font-weight: 900; letter-spacing: 1px;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        
        content_layout.addWidget(self.header_bar)
        content_layout.addSpacing(40)
        
        # Content Stack (Factions vs Eras)
        from PyQt6.QtWidgets import QStackedWidget
        self.stack = QStackedWidget()
        
        # --- Page 1: Factions ---
        faction_page = QWidget()
        faction_grid = QGridLayout(faction_page)
        faction_grid.setSpacing(20)
        
        factions = [
            ("UNITED FEDERATION OF PLANETS", "Standard Operating Procedures\nStarfleet Command", "#FF9900", "federation"),
            ("KLINGON FLOTILLA", "Tactical Systems Protocol\nAuthorized General Martok", "#CC3333", "klingon"),
            ("ROMULAN STAR EMPIRE", "Restricted Access Only\nTal Shiar Clearance", "#33CC66", "romulan"),
            ("CARDASSIAN UNION", "Central Command Protocols\nObsidian Order Level 1", "#CC9900", "cardassian")
        ]
        
        for i, (name, desc, color_code, faction_id) in enumerate(factions):
            tile = LcarsTile(f"{name}\n{desc}")
            tile.set_color(QColor(color_code))
            tile.setFixedHeight(120) 
            tile.clicked.connect(lambda _, fid=faction_id, col=color_code: self.show_eras(fid, col))
            
            row = i // 2
            col = i % 2
            faction_grid.addWidget(tile, row, col)
            
        self.stack.addWidget(faction_page)
        self.faction_page = faction_page
        
        # --- Page 2: Eras (Dynamic) ---
        self.era_page = QWidget()
        self.era_grid = QGridLayout(self.era_page)
        self.era_grid.setSpacing(20)
        self.stack.addWidget(self.era_page)
        
        content_layout.addWidget(self.stack)
        content_layout.addStretch()
        
        # Footer
        self.footer = QLabel("AUTHORIZATION REQUIRED // SELECT AFFILIATION")
        self.footer.setStyleSheet("color: #FF9900; font-family: 'Swis721 BT'; font-size: 14px; letter-spacing: 4px; margin-right: 20px;")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        content_layout.addWidget(self.footer)
        
        h_layout.addLayout(content_layout)
        
    def show_eras(self, faction_id, color_code):
        """Transition to Era Selection"""
        self.current_faction = faction_id
        
        # Remove old buttons
        for i in reversed(range(self.era_grid.count())): 
            self.era_grid.itemAt(i).widget().setParent(None)
            
        # Update colors
        self.elbow.set_color(color_code)
        self.v_bar.setStyleSheet(f"background-color: {color_code}; border-radius: 0px;")
        self.header_bar.setStyleSheet(f"background-color: {color_code}; border-top-right-radius: 20px;")
        self.title_label.setText(f"SELECT TEMPORAL PERIOD // {faction_id.upper()}")
        self.footer.setStyleSheet(f"color: {color_code}; font-family: 'Swis721 BT'; font-size: 14px; letter-spacing: 4px; margin-right: 20px;")
        self.footer.setText("TEMPORAL SYNC REQUIRED")
        
        # Back Button
        back_tile = LcarsTile("RETURN\nInitialize Faction Select")
        back_tile.set_color(QColor("#999999"))
        back_tile.setFixedHeight(80)
        back_tile.clicked.connect(self.show_factions)
        self.era_grid.addWidget(back_tile, 0, 0, 1, 2)
        
        # Get Eras based on faction
        eras = self.get_eras_for_faction(faction_id)
        
        for i, (name, era_id) in enumerate(eras):
            tile = LcarsTile(name)
            tile.set_color(QColor(color_code))
            tile.setFixedHeight(100)
            tile.clicked.connect(lambda _, eid=era_id: self.emit_selection(self.current_faction, eid))
            
            row = (i // 2) + 1
            col = i % 2
            self.era_grid.addWidget(tile, row, col)
            
        self.stack.setCurrentWidget(self.era_page)
        
    def show_factions(self):
        """Return to Faction Selection"""
        self.stack.setCurrentWidget(self.faction_page)
        self.title_label.setText("SYSTEM ACCESS AUTHORIZATION")
        
        # Reset colors to default orange
        def_color = "#FF9900"
        self.elbow.set_color(def_color)
        self.v_bar.setStyleSheet(f"background-color: {def_color}; border-radius: 0px;")
        self.header_bar.setStyleSheet(f"background-color: {def_color}; border-top-right-radius: 20px;")
        self.footer.setStyleSheet(f"color: {def_color}; font-family: 'Swis721 BT'; font-size: 14px; letter-spacing: 4px; margin-right: 20px;")
        self.footer.setText("AUTHORIZATION REQUIRED // SELECT AFFILIATION")

    def get_eras_for_faction(self, faction_id):
        """Return available eras for the faction"""
        if faction_id == "federation":
            return [
                ("24TH CENTURY (TNG)\nAUTHENTIC SYSTEM CORE", "24th"),
                ("25TH CENTURY (PICARD)\nMODERN DASHBOARD", "25th"),
                ("29TH CENTURY (FUTURE)\nTEMPORAL PROTOCOLS", "29th")
            ]
        elif faction_id == "klingon":
            return [
                ("23RD CENTURY (TOS)\nImperial Defense Network", "23rd"),
                ("24TH CENTURY (TNG)\nHigh Council Access", "24th")
            ]
        elif faction_id == "romulan":
            return [
                ("24TH CENTURY\nTal Shiar Encrypted", "24th")
            ]
        elif faction_id == "cardassian":
            return [
                 ("UNION ERA (DS9)\nCentral Command", "24th")
            ]
        return []

        
    def emit_selection(self, faction_id, era_id):
        # Format: "federation_25th" or just "federation" if default
        # But per user request, we want complex handling. 
        # For compatibility with lcars_central.py user edits, we will emit constructed IDs
        
        if faction_id == "federation":
            if era_id == "25th":
                self.factionSelected.emit("federation_25th")
            else:
                self.factionSelected.emit("federation") # Default to 24th per user edit
        else:
            # Pass simple IDs for others for now, or construct complex ones if we update central
             self.factionSelected.emit(faction_id)
