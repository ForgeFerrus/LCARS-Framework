# Titanium Bridge Migration: import os, sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if root not in sys.path:
    sys.path.insert(0, root)
"""
LCARS Faction Selection Interface
Initial screen for choosing allegiance/theme.
Redesigned for 25th Century Aesthetics.
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QFrame,
    QSizePolicy,
    QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal

from lcars.themes.palette import get_lcars_font_style
# УКР: використовуємо канонічний LCARS віджет 'LCARSElbow' для декоративного ліктя/елемента UI
from lcars.ui.base.widgets import LCARSElbow

class FactionSelector(QWidget):
    """
    Modern Faction Selection Screen.
    Displays available factions with high-fidelity LCARS styling.
    """

    factionSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")
        self.setup_ui()

    def setup_ui(self):
        # Master Layout: Horizontal (Left Bar + Main Content)
        master_layout = QHBoxLayout(self)
        master_layout.setContentsMargins(20, 20, 20, 20)
        master_layout.setSpacing(10)

        # --- LEFT SIDEBAR (The distinct LCARS curve) ---
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(5)

        # Top Elbow (Curve)
        # 25th Century Color: #37A6D1 (Blue) or #FF9900 (Orange) for Command
        
        # Vertical Bar connecting downward
        self.v_bar = QFrame()
        self.v_bar.setMinimumWidth(150)
        self.v_bar.setStyleSheet("background-color: #FF9900; border: none;")
        self.v_bar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sidebar_layout.addWidget(self.v_bar)

        # Bottom decorative block
        self.bottom_block = QFrame()
        self.bottom_block.setMinimumSize(150, 60)
        self.bottom_block.setStyleSheet("background-color: #CC6600; border: none;")
        sidebar_layout.addWidget(self.bottom_block)

        master_layout.addLayout(sidebar_layout)

        # --- MAIN CONTENT AREA ---
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 0, 0, 0)

        # Header Text (Aligned with Elbow)
        header_text = QLabel("SYSTEM ACCESS AUTHORIZATION")
        header_text.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(42, 'normal')} text-transform: uppercase; letter-spacing: 2px;")
        header_text.setMinimumHeight(80)  # Match elbow height
        header_text.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        content_layout.addWidget(header_text)

        # Top Separator Line
        line = QFrame()
        line.setMinimumHeight(5)
        line.setStyleSheet("background-color: #FF9900;")
        content_layout.addWidget(line)

        content_layout.addStretch(1)

        # Grid of Factions
        grid = QGridLayout()
        grid.setSpacing(30)

        # Faction Definitions: (Name, ID, Color)
        factions = [
            ("UNITED FEDERATION\nOF PLANETS", "federation", "#37A6D1"),  # Blue
            ("KLINGON EMPIRE", "klingon", "#CE392B"),  # Red
            ("ROMULAN STAR EMPIRE", "romulan", "#45D090"),  # Green
            ("CARDASSIAN UNION", "cardassian", "#EACD53"),  # Gold
            ("TERRAN EMPIRE", "terran", "#8B0000"),  # Dark Red
            ("BORG COLLECTIVE", "borg", "#555555"),  # Grey
        ]

        row, col = 0, 0
        for name, fid, color in factions:
            btn = self.create_faction_button(name, fid, color)
            grid.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        content_layout.addLayout(grid)
        content_layout.addStretch(2)

        master_layout.addLayout(content_layout)

    def create_faction_button(self, name, fid, color):
        """Creates a large, styled button for faction selection"""
        btn = QPushButton(name)
        btn.setMinimumHeight(120)
        # Styling: Big rect with rounded corners on one side? Or just blocky.
        # LCARS buttons are typically rounded lozenges.
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: black;
                font-family: 'Arial';
                font-size: 18px;
                font-weight: normal;
                border: none;
                border-radius: 60px; /* Fully rounded ends */
                padding: 20px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: white; 
                /* Lighter version of color would be better, but white is standard LCARS interaction */
            }}
            QPushButton:pressed {{
                background-color: #FF9900;
            }}
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.factionSelected.emit(fid))

        # Add a "Shadow" or "Connector" look if desired, but clean is better.
        return btn


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = FactionSelector()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())
