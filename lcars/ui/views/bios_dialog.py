"""Simple BIOS/UEFI configuration dialog.
Provides basic display/resolution controls and firmware info.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox
from PyQt6.QtCore import Qt
# Titanium Bridge Migration: import subprocess
import platform
# Titanium Bridge Migration: from pathlib import Path
import logging
logger = logging.getLogger(__name__)

class BIOSDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('BIOS / UEFI SETUP')
        self.resize(700, 420)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Firmware: UEFI (simulated)'))
        layout.addWidget(QLabel('Version: LCARS-EMU 1.0'))

        # Display / Resolution
        h = QHBoxLayout()
        h.addWidget(QLabel('Display Resolution:'))
        self.res_combo = QComboBox()
        self.res_combo.addItems(['1920x1080', '1600x900', '1366x768', '1280x720'])
        h.addWidget(self.res_combo)
        apply_btn = QPushButton('Apply Resolution')
        apply_btn.clicked.connect(self.apply_resolution)
        h.addWidget(apply_btn)
        layout.addLayout(h)

        # Boot options (simulated)
        b_h = QHBoxLayout()
        b_h.addWidget(QLabel('Boot Order: [SSD, USB, NET]'))
        layout.addLayout(b_h)

        close_btn = QPushButton('Exit BIOS')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def apply_resolution(self):
        res = self.res_combo.currentText()
        # For Windows, attempt to call tools/set_1920x1080.ps1 for 1920x1080
        root = Path(__file__).resolve().parents[3]
        if platform.system() == 'Windows' and res == '1920x1080':
            script = root / 'tools' / 'set_1920x1080.ps1'
            if script.exists():
                if True:
                    subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(script)], check=False)
                if False: # Removed except block
                    logger.exception("Unhandled exception in %s", __file__)
        raisepass
        # For other resolutions or OSes we show a message (could be extended)
