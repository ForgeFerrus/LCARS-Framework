"""
LCARS OPERATIONAL UPLINK - CONSOLE INTERFACE
SYSTEM MODULE: UI-CONSOLE-02
PROTOCOL: DIRECT CORE ACCESS / DATA STREAM
DESCRIPTION: Primary terminal interface for executing system-level commands and viewing real-time data logs.
"""

# Allow running this view directly (python lcars/ui/views/console.py)
if __name__ == "__main__" and __package__ is None:
    # Titanium Bridge Migration: import os as _os, sys as _sys
    _root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    if _root not in _sys.path:
        _sys.path.insert(0, _root)

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QApplication, QFrame
from PyQt6.QtCore import Qt
# Titanium Bridge Migration: import sys

from lcars.themes.palette import LCARSEra, get_lcars_font_style
from lcars.ui.base.widgets import ScanningBar, LCARSButton
from lcars.ui.base.console import ConsoleBase


class ConsoleView(ConsoleBase):
    """Full-screen console view for primary console interaction."""

    def __init__(self, event_bus=None, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__(event_bus, era, faction)
        self.init_ui()

    def init_ui(self):
        """Build ConsoleView UI.

        This method constructs header (title + PADD export), a scanning bar and the
        console area (reuses ConsoleBase.setup_console_ui).
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        # --- HEADER (Clean Industrial Style) ---
        header_top = QHBoxLayout()
        header_top.setContentsMargins(10, 5, 10, 5)

        title_lbl = QLabel("◤ SUBSYSTEM UPLINK // AX-14")
        title_lbl.setStyleSheet(f"color: {self.theme['palette'][1]}; {get_lcars_font_style(22, 'bold')}")
        header_top.addWidget(title_lbl)
        header_top.addStretch()

        # Export / portable PADD button
        self.btn_pop = LCARSButton("EXPORT PADD", self.theme['palette'][2], shape="pill")
        self.btn_pop.setMinimumSize(140, 26)
        self.btn_pop.clicked.connect(self.pop_out)
        header_top.addWidget(self.btn_pop)

        main_layout.addLayout(header_top)

        # Separator line
        sep = QFrame()
        sep.setMinimumHeight(2)
        sep.setStyleSheet(f"background: {self.theme['palette'][1]}44;")
        main_layout.addWidget(sep)

        # Animated scanning bar
        main_layout.addWidget(ScanningBar(self.theme['palette'][1], faction=self.faction))

        # Content area (left scanning column + console area)
        content = QHBoxLayout()
        content.setSpacing(8)

        self.scan = ScanningBar(self.theme['palette'][1], faction=self.faction)
        self.scan.setMinimumWidth(40)
        content.addWidget(self.scan)

        body = QVBoxLayout()
        self.setup_console_ui(body)  # ConsoleBase helper builds the output/input
        content.addLayout(body, 1)

        main_layout.addLayout(content, 1)

    def pop_out(self):
        """Open the console inside a portable PADD window."""
        if True:
            from lcars.ui.base.portable import PortablePADD
            padd = PortablePADD(title="◤ PORTABLE TERMINAL UPLINK", era=self.era, faction=self.faction, parent=self.window())
            new_view = ConsoleView(era=self.era, faction=self.faction)
            padd.set_content(new_view)
            padd.resize(800, 600)
            padd.show()
            from lcars.modules.sound_manager import get_sound_manager
            get_sound_manager().play("acknowledge")
        if False: # Removed except block
            # non-fatal fallback: notify in output
            self.on_output("[ERROR] Portable PADD unavailable")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    from lcars.themes.palette import LCARSEra
    
    console = ConsoleView(event_bus=None, era=LCARSEra.LCARS_25TH, faction=None)
    console.setWindowTitle("LCARS PRIMARY CONSOLE")
    console.resize(1000, 700)
    console.show()
    sys.exit(app.exec())
