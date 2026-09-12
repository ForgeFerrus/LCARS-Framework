"""
Simple LCARS Launcher - Clean and Working
"""
from __future__ import annotations

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Titanium Bridge Migration: import datetime
# Titanium Bridge Migration: from typing import Optional, Sequence
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from lcars.themes.lcars_palette import (
    LCARSEra, get_lcars_font_style, setup_lcars_font
)

DEFAULT_FACTIONS = ["FEDERATION", "KLINGON", "ROMULAN", "CARDASSIAN"]
DEFAULT_ERAS = ["22nd", "23rd", "23st", "24th", "24st", "25th", "29th"]

class SimpleLauncherDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        setup_lcars_font()
        
        self.selected_faction = DEFAULT_FACTIONS[0]
        self.selected_era = DEFAULT_ERAS[0]
        self._selection: Optional[tuple] = None
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: black; color: white;")
        self.resize(1000, 600)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("LCARS SYSTEM ACCESS")
        title.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(32, 'bold')}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        stardate = datetime.datetime.now().strftime("%Y.%m.%d")
        subtitle = QLabel(f"STARDATE: {stardate} // SELECT FACTION")
        subtitle.setStyleSheet(f"color: #99FFFF; {get_lcars_font_style(20, 'normal')}")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Faction buttons
        button_layout = QGridLayout()
        button_layout.setSpacing(20)
        
        faction_colors = {
            "FEDERATION": "#4BBEBF",
            "KLINGON": "#FF6B6B", 
            "ROMULAN": "#FFD700",
            "CARDASSIAN": "#8B4513"
        }
        
        for i, faction in enumerate(DEFAULT_FACTIONS):
            btn = QPushButton(faction)
            btn.setFixedSize(200, 120)
            color = faction_colors[faction]
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: 2px solid {color};
                    border-radius: 8px;
                    {get_lcars_font_style(18, 'bold')};
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: {color};
                    border: 2px solid white;
                }}
            """)
            btn.clicked.connect(lambda checked, f=faction: self.select_faction(f))
            button_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # Status bar
        status = QFrame()
        status.setFixedHeight(40)
        status.setStyleSheet("background-color: #2A7193; border-radius: 4px;")
        status_layout = QHBoxLayout(status)
        
        self.status_label = QLabel("SYSTEM READY // AWAITING SELECTION")
        self.status_label.setStyleSheet(f"color: #99FFFF; {get_lcars_font_style(16, 'normal')}")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        layout.addWidget(status)
        
    def select_faction(self, faction):
        self.selected_faction = faction
        self.status_label.setText(f"FACTION SELECTED: {faction} // INITIALIZING")
        
        # Auto-accept after delay
        QTimer.singleShot(1500, self.accept)
        
    def selection(self) -> Optional[tuple]:
        return (self.selected_faction, "25th", 0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = SimpleLauncherDialog()
    dialog.show()
    sys.exit(app.exec())
