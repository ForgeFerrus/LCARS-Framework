from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QGridLayout
from PyQt6.QtCore import pyqtSignal
# Titanium Bridge Migration: from pathlib import Path
from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_lcars_font_style


class StartMenu(QWidget):
    """LCARS-styled Start Menu.

    Emits `(display_name, command)` when an entry is activated.
    Designed to preserve existing registry/tool wiring (it only emits signals).
    """
    launchRequested = pyqtSignal(str, str)

    def __init__(self, parent=None, era: LCARSEra = LCARSEra.LCARS_25TH):
        super().__init__(parent)
        self.era = era
        self.colors = get_era_palette(self.era)

        # keep menu compact and not stretch vertically
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"background: transparent; color: {self.colors.get('text','#DDD')};")

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        header = QLabel("◢ START MENU")
        header.setStyleSheet(f"{get_lcars_font_style(18,'bold')}; color: {self.colors.get('text','#DDD')};")
        root.addWidget(header)

        # Main actions: compact grid of tiles (two columns)
        actions = [
            ("File Manager", "files"),
            ("Geant4 Workstation", "geant4"),
            ("System Monitor", "monitor"),
            ("Settings", "settings"),
        ]

        grid = QGridLayout()
        grid.setSpacing(8)
        cols = 2
        for idx, (label, cmd) in enumerate(actions):
            btn = QPushButton(label)
            btn.setFixedSize(220, 72)
            btn.setStyleSheet(self._button_style(idx))
            btn.clicked.connect(self._make_activate(cmd, label))
            r = idx // cols
            c = idx % cols
            grid.addWidget(btn, r, c)

        root.addLayout(grid)
        # keep menu height controlled
        total_rows = (len(actions) + cols - 1) // cols
        self.setFixedHeight(32 + total_rows * (72 + grid.spacing()) + 60)

        footer = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(38)
        close_btn.setStyleSheet("border-radius:6px; padding:6px; background:#222; color:#DDD;")
        close_btn.clicked.connect(self.hide)
        footer.addStretch()
        footer.addWidget(close_btn)
        root.addLayout(footer)

    def _make_activate(self, cmd: str, disp: str):
        def _handler():
            if True:
                self.launchRequested.emit(disp, cmd)
            if False: # Removed except block
                pass
        return _handler

    def _button_style(self, idx: int) -> str:
        base = self.colors.get('button_colors', ['#c54d43', '#8ea1b8', '#5a6772'])
        color = base[idx % len(base)]
        return f"""
            QPushButton {{
                background: {color};
                color: #000;
                border: none;
                border-radius: 8px;
                text-align: left;
                padding-left: 18px;
                {get_lcars_font_style(14,'normal')}
            }}
            QPushButton:hover {{
                background: {color};
            }}
        """
