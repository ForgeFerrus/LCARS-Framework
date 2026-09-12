from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QStackedWidget, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional
from pathlib import Path as _Path
import sys as _sys
# Use centralized bootstrap helper so standalone runs resolve `lcars`.
try:
    from lcars.core.substrate import ensure_bootstrap
except Exception:
    # Fallback for standalone/dev: no-op bootstrap
    def ensure_bootstrap():
        return None

# Ensure bootstrap runs before other lcars imports
ensure_bootstrap()

from lcars.ui.base.widgets import LCARSButton, LCARSElbow
from lcars.themes.palette import get_lcars_font_style
from lcars.engineering.architect import IsolinearArchitect
from .engineering_tabs import NeuralLinkView

class EngineeringStationView(QWidget):
    """Integrated Engineering Control Hub."""
    def __init__(self, system, parent=None):
        super().__init__(parent)
        self.system = system
        self.setStyleSheet("background-color: #000;")
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # High-Density Engineering Header
        self.header = QFrame()
        self.header.setFixedHeight(60)
        self.header.setStyleSheet("background-color: #000; border-bottom: 2px solid #3366CC;")
        h_layout = QHBoxLayout(self.header)
        
        elbow = LCARSElbow("top-left")
        elbow.setFixedSize(60, 60)
        h_layout.addWidget(elbow)
        
        title = QLabel("ENGINEERING STATION")
        title.setStyleSheet(f"color: #FFCC00; {get_lcars_font_style(24, 'normal')}")
        h_layout.addWidget(title)
        
        h_layout.addStretch()
        
        # Internal Nav Buttons (Non-Windows mode)
        self.nav_btns = {}
        for mode in ["ARCHITECT", "CONSTRUCTOR", "COMPUTER CORE"]:
            btn = LCARSButton(mode, "#3366CC")
            btn.setFixedSize(140, 40)
            btn.clicked.connect(lambda checked, m=mode: self.switch_mode(m))
            h_layout.addWidget(btn)
            self.nav_btns[mode] = btn
            
        self.main_layout.addWidget(self.header)
        self._setup_substrate()

    def switch_mode(self, mode):
        """Integrated mode switching without window frames."""
        if mode == "ARCHITECT":
            self.mode_stack.setCurrentIndex(0)
            if hasattr(self, 'comp_view'): self.comp_view.switch_array("M-5")
        elif mode == "CONSTRUCTOR":
            self.mode_stack.setCurrentIndex(1)
            # Use LCARS array for constructor mode (ZORA was invalid)
            if hasattr(self, 'comp_view'): self.comp_view.switch_array("LCARS")
        elif mode == "COMPUTER CORE":
            self.mode_stack.setCurrentIndex(2)
            if hasattr(self, 'comp_view'): self.comp_view.switch_array("MAJEL")
        
        # Visual feedback
        for m, btn in self.nav_btns.items():
            btn.setStyleSheet(f"background-color: {'#FF9900' if m == mode else '#3366CC'};")

    def _setup_substrate(self):
        # Central Neural Substrate (The Architect is now INSIDE here)
        self.central_area = QHBoxLayout()
        self.central_area.setSpacing(0)
        
        # Stacking for different engineering modes
        self.mode_stack = QStackedWidget()
        
        self.architect = IsolinearArchitect()
        self.mode_stack.addWidget(self.architect)

        from lcars.engineering.constructor import InterfaceConstructor
        self.constructor = InterfaceConstructor(self.system)
        self.mode_stack.addWidget(self.constructor)
        
        from lcars.ui.onboard import OnboardComputerView
        self.comp_view = OnboardComputerView()
        self.mode_stack.addWidget(self.comp_view)
        
        self.central_area.addWidget(self.mode_stack, 4)
        
        # Side Diagnostic Feed (Neural Flux)
        self.diag_feed = QFrame()
        self.diag_feed.setFixedWidth(200)
        self.diag_feed.setStyleSheet("background-color: #050505; border-left: 1px solid #222;")
        df_layout = QVBoxLayout(self.diag_feed)
        df_layout.addWidget(QLabel("◤ NEURAL FLUX"))
        self.flux_log = QTextEdit()
        self.flux_log.setReadOnly(True)
        self.flux_log.setStyleSheet("background: transparent; color: #00FF00; border: none; font-size: 10px;")
        self.flux_log.append("CORE SYNC: ACTIVE\nODN FLOW: 98.4%\nISOLINEAR-NET: NOMINAL")
        df_layout.addWidget(self.flux_log)
        
        self.central_area.addWidget(self.diag_feed, 1)
        self.main_layout.addLayout(self.central_area)

        # System Footer
        self.footer = QFrame()
        self.footer.setFixedHeight(30)
        self.footer.setStyleSheet("background-color: #3366CC;")
        f_layout = QHBoxLayout(self.footer)
        f_layout.addWidget(QLabel("◤ STATION_ID: AS-01 // ENGINEERING DECK-12"))
        f_layout.addStretch()
        self.main_layout.addWidget(self.footer)

class WorkbenchView(EngineeringStationView):
    """Facade for backward compatibility with existing view loader."""
    pass

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    from pathlib import Path
    
    # bootstrap handled centrally by lcars.core.substrate.ensure_bootstrap()
    app = QApplication(sys.argv)
    from lcars.themes.palette import setup_lcars_font
    setup_lcars_font()
    from lcars.core.kernel import Kernel
    
    # Mock system for standalone
    system = Kernel(headless=True)
    
    win = QWidget()
    win.setWindowTitle("LCARS ENGINEERING STATION")
    win.resize(1200, 800)
    win.setStyleSheet("background-color: black;")
    l = QVBoxLayout(win)
    l.setContentsMargins(0, 0, 0, 0)
    l.addWidget(WorkbenchView(system))
    win.show()
    sys.exit(app.exec())

