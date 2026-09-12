"""
LCARS Desktop - Official High-Quality Interface
Era: Federation/Klingon/Romulan Dynamic Support
"""

# Titanium Bridge Migration: import sys
import logging
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QColor

# Add project root to sys.path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import lcars
from lcars.themes.lcars_palette import (
    LCARSEra, FactionEra, get_theme, get_random_button_color,
    get_lcars_font_style, setup_lcars_font
)

logger = logging.getLogger("lcars.ui.desktop")

class LCARSButton(QPushButton):
    """Standard LCARS 'Brick' button: 220x60, themed radii and colors."""
    def __init__(self, text, color=None, era=LCARSEra.LCARS_25TH, faction=None, shape="rect", parent=None):
        super().__init__(text, parent)
        self.era = era
        self.faction = faction
        self.shape = shape
        self.theme = get_theme(era, faction)
        self.current_color = color or get_random_button_color(self.era, self.faction)
        
        # Standard brick size
        self.setFixedSize(220, 60)
        self.apply_style()
        
        # Atmospheric slow color cycling
        if not color:
            self.color_timer = QTimer(self)
            self.color_timer.timeout.connect(self._cycle_color)
            self.color_timer.start(7000 + (hash(text) % 5000))

    def _cycle_color(self):
        self.current_color = get_random_button_color(self.era, self.faction)
        self.apply_style()

    def apply_style(self):
        radius = self.theme['radius']
        if self.shape == "left":
            radius_style = f"border-top-left-radius: {radius}; border-bottom-left-radius: {radius}; border-top-right-radius: 2px; border-bottom-right-radius: 2px;"
        elif self.shape == "right":
            radius_style = f"border-top-right-radius: {radius}; border-bottom-right-radius: {radius}; border-top-left-radius: 2px; border-bottom-left-radius: 2px;"
        else:
            radius_style = f"border-radius: {radius};"

        font_style = get_lcars_font_style(16, 'bold')
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                color: #000000;
                border: none;
                {radius_style}
                {font_style}
                text-align: right;
                padding-right: 20px;
                text-transform: uppercase;
            }}
            QPushButton:hover {{ background-color: #FFFFFF; }}
            QPushButton:pressed {{ background-color: #AAAAAA; }}
        """)

class LCARSElbow(QFrame):
    """The iconic LCARS 'Elbow' (G-shaped connector)."""
    def __init__(self, direction="top-left", era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        self.theme = get_theme(era, faction)
        self.direction = direction
        self.current_color = get_random_button_color(era, faction)
        self.apply_style()

    def apply_style(self):
        radius = self.theme['elbow']
        if self.direction == "top-left":
            style = f"border-top-left-radius: {radius};"
        elif self.direction == "bottom-left":
            style = f"border-bottom-left-radius: {radius};"
        elif self.direction == "top-right":
            style = f"border-top-right-radius: {radius};"
        elif self.direction == "bottom-right":
            style = f"border-bottom-right-radius: {radius};"
        else:
            style = "border-radius: 2px;"

        self.setStyleSheet(f"background-color: {self.current_color}; {style} border: none;")

class LCARSDesktop(QMainWindow):
    """Main LCARS Desktop Interface."""
    def __init__(self, era_key: str = "25th", faction_key: str = "federation"):
        super().__init__()
        self.system = lcars.get_system()
        
        # Parse Era/Faction
        era_map = {
            "22nd": LCARSEra.COMS_22ND, "23rd": LCARSEra.PCARS_23RD, "23st": LCARSEra.PCARS_23ST,
            "24th": LCARSEra.LCARS_24TH, "24st": LCARSEra.LCARS_24ST, "25th": LCARSEra.LCARS_25TH, 
            "29th": LCARSEra.TCARS_29TH
        }
        self.era = era_map.get(era_key.lower(), LCARSEra.LCARS_25TH)
        
        faction_map = {
            "federation": None, "klingon": FactionEra.KLINGON, 
            "romulan": FactionEra.ROMULAN, "cardassian": FactionEra.CARDASSIAN
        }
        self.faction = faction_map.get(faction_key.lower())
        self.theme = get_theme(self.era, self.faction)

        # UI Setup
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setStyleSheet(f"background-color: {self.theme['bg']};")
        
        setup_lcars_font()
        self.init_ui()
        
        # System timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # 1. HEADER (Elbow + Title + Cap)
        header = QHBoxLayout()
        header.setSpacing(5)
        
        self.header_elbow = LCARSElbow("top-left", self.era, self.faction)
        self.header_elbow.setFixedSize(220, 90)
        header.addWidget(self.header_elbow)

        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(60)
        self.title_bar.setStyleSheet(f"background-color: {self.theme['accent']}; border-radius: 2px;")
        t_layout = QHBoxLayout(self.title_bar)
        
        faction_name = "FEDERATION" if not self.faction else self.faction.name
        self.lbl_title = QLabel(f"COMMAND INTERFACE / {faction_name} / {self.era.value}")
        self.lbl_title.setStyleSheet(f"color: black; {get_lcars_font_style(20, 'bold')}")
        t_layout.addWidget(self.lbl_title)
        t_layout.addStretch()
        
        self.lbl_clock = QLabel("--:--:--")
        self.lbl_clock.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'bold')}")
        t_layout.addWidget(self.lbl_clock)
        
        header.addWidget(self.title_bar, 1)
        
        self.header_cap = QFrame()
        self.header_cap.setFixedSize(150, 60)
        self.header_cap.setStyleSheet(f"background-color: {get_random_button_color(self.era, self.faction)}; border-top-right-radius: {self.theme['radius']};")
        header.addWidget(self.header_cap)
        
        layout.addLayout(header)

        # 2. MIDDLE (Sidebar + Stack)
        middle = QHBoxLayout()
        middle.setSpacing(5)

        sidebar = QVBoxLayout()
        sidebar.setSpacing(5)
        
        # Sidebar filler elbow
        side_connector = QFrame()
        side_connector.setFixedSize(220, 30)
        side_connector.setStyleSheet(f"background-color: {self.header_elbow.current_color}; border-bottom-left-radius: {self.theme['radius']};")
        sidebar.addWidget(side_connector)

        nav = [
            ("SENSORS", self.show_sensors),
            ("PROJECTS", self.show_projects),
            ("ENGINE", self.show_engine),
            ("TERMINAL", self.show_terminal),
            ("SYSTEM", self.show_system)
        ]
        
        for text, func in nav:
            btn = LCARSButton(text, era=self.era, faction=self.faction, shape="left")
            btn.clicked.connect(func)
            sidebar.addWidget(btn)

        sidebar.addStretch()
        
        off_btn = LCARSButton("OFF", "#CC0000", era=self.era, faction=self.faction, shape="left")
        off_btn.clicked.connect(self.close)
        sidebar.addWidget(off_btn)
        
        middle.addLayout(sidebar)

        # Content area
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"border-top: 2px solid {self.theme['border']}; border-left: 2px solid {self.theme['border']}; background: black;")
        
        self.dashboard = self._create_dashboard()
        self.stack.addWidget(self.dashboard)
        
        middle.addWidget(self.stack, 1)
        layout.addLayout(middle, 1)

        # 3. FOOTER
        footer = QHBoxLayout()
        footer.setSpacing(5)
        
        f_left = LCARSElbow("bottom-left", self.era, self.faction)
        f_left.setFixedSize(220, 60)
        footer.addWidget(f_left)

        f_mid = QFrame()
        f_mid.setFixedHeight(40)
        f_mid.setStyleSheet(f"background-color: {get_random_button_color(self.era, self.faction)};")
        footer.addWidget(f_mid, 1)
        
        f_right = QFrame()
        f_right.setFixedSize(150, 40)
        f_right.setStyleSheet(f"background-color: {get_random_button_color(self.era, self.faction)}; border-bottom-right-radius: {self.theme['radius']};")
        footer.addWidget(f_right)
        
        layout.addLayout(footer)

    def _create_dashboard(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("◢ MISSION CONTROL HUB")
        title.setStyleSheet(f"color: {get_random_button_color(self.era, self.faction)}; {get_lcars_font_style(32, 'bold')}")
        l.addWidget(title)
        
        grid = QGridLayout()
        grid.setSpacing(15)
        
        stats = [
            ("SHIELDS", "ACTIVE (100%)"), ("SENSORS", "NOMINAL"), ("POWER", "STABLE"),
            ("DATABANK", "CONNECTED"), ("GEANT4", "READY"), ("SYSTEM", "OPTIMAL")
        ]
        
        for i, (k, v) in enumerate(stats):
            f = QFrame()
            f.setStyleSheet(f"background: #111; border-left: 10px solid {get_random_button_color(self.era, self.faction)}; padding: 10px;")
            fl = QVBoxLayout(f)
            kl = QLabel(k); kl.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(14, 'bold')}")
            vl = QLabel(v); vl.setStyleSheet(f"color: white; {get_lcars_font_style(18, 'normal')}")
            fl.addWidget(kl); fl.addWidget(vl)
            grid.addWidget(f, i // 3, i % 3)
            
        l.addLayout(grid)
        l.addStretch()
        
        log = QLabel("◢ SYSTEM LOG: BOOT SEQUENCE COMPLETE. ALL MODULES OPERATIONAL.\n◢ STARBASE CONNECTION ESTABLISHED.")
        log.setStyleSheet(f"color: #00FF00; background: #050505; padding: 20px; {get_lcars_font_style(14, 'normal')}")
        l.addWidget(log)
        
        return w

    def update_clock(self):
        self.lbl_clock.setText(datetime.now().strftime("%H:%M:%S"))

    def show_sensors(self):
        if not hasattr(self, 'sensors_view'):
            from lcars.ui.views.analytics import AnalyticsView
            self.sensors_view = AnalyticsView()
            self.stack.addWidget(self.sensors_view)
        self.stack.setCurrentWidget(self.sensors_view)

    def show_projects(self):
        from lcars.ui.views.project_explorer import ProjectExplorerWidget
        if not hasattr(self, 'projects_view'):
            self.projects_view = ProjectExplorerWidget(self.system.project_manager, era=self.era)
            self.stack.addWidget(self.projects_view)
        self.stack.setCurrentWidget(self.projects_view)

    def show_engine(self):
        from lcars.ui.views.operations import OperationsView
        if not hasattr(self, 'ops_view'):
            self.ops_view = OperationsView()
            self.stack.addWidget(self.ops_view)
        self.stack.setCurrentWidget(self.ops_view)

    def show_terminal(self):
        from lcars.ui.views.terminal import TerminalView
        if not hasattr(self, 'term_view'):
            self.term_view = TerminalView()
            self.stack.addWidget(self.term_view)
        self.stack.setCurrentWidget(self.term_view)

    def show_system(self):
        self.stack.setCurrentIndex(0)

def main():
    app = QApplication(sys.argv)
    # Simple check for args
    era = "25th"
    faction = "Federation"
    for i, arg in enumerate(sys.argv):
        if arg == "--era" and i+1 < len(sys.argv): era = sys.argv[i+1]
        if arg == "--faction" and i+1 < len(sys.argv): faction = sys.argv[i+1]
        
    window = LCARSDesktop(era, faction)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
