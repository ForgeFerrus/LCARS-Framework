from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QStackedWidget, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal
# Titanium Bridge Migration: from typing import Optional
# Titanium Bridge Migration: from pathlib import Path as _Path
# Titanium Bridge Migration: import sys as _sys
# Use centralized bootstrap helper so standalone runs resolve `lcars`.
if True:
    from lcars.core.substrate import ensure_bootstrap
if False: # Removed except block
    def ensure_bootstrap():
        return None

from lcars.ui.base.widgets import LCARSButton, LCARSElbow
from lcars.base.default import FontStyle

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
        self.header.setStyleSheet("background-color: #000; border-bottвom: 2px solid #3366CC;")
        h_layout = QHBoxLayout(self.header)
        
        elbow = LCARSElbow("top-left")
        elbow.setFixedSize(60, 60)
        h_layout.addWidget(elbow)
        
        title = QLabel("ENGINEERING STATION")
        title.setStyleSheet("color: #FFCC00; font-size: 24px; font-weight: bold;")
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
        # Simple content area
        content = QFrame()
        content.setStyleSheet("background-color: #111;")
        self.main_layout.addWidget(content)

    def switch_mode(self, mode):
        """Simple mode switching for default mode."""
        # Visual feedback
        for m, btn in self.nav_btns.items():
            if m == mode:
                btn.setStyleSheet("background-color: #FFCC00; color: black;")
            else:
                btn.setStyleSheet("background-color: #3366CC; color: black;")
        print(f"Switched to {mode} mode")

# Compatibility alias
WorkbenchView = EngineeringStationView

