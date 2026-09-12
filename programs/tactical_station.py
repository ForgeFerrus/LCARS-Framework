from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from lcars.engineering.connector import engineering_core
from lcars.ui.base.widgets import LCARSButton

class TacticalStation(QWidget):
    """
    Тактична станція. 
    Управляє щитами (Deflector) та безпекою мережі.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.title = QLabel("TACTICAL STATION // INTERNAL SECURITY")
        self.title.setStyleSheet("color: #CC2222; font-family: 'LCARS'; font-size: 28px; font-weight: bold;")
        self.layout.addWidget(self.title)

        self.status_lbl = QLabel("DEFLECTOR SHIELDS: OFFLINE")
        self.status_lbl.setStyleSheet("color: #FF9900; font-size: 20px;")
        self.layout.addWidget(self.status_lbl)

        # Контроль щитів
        self.btn_layout = QHBoxLayout()
        self.raise_shields_btn = LCARSButton("RAISE SHIELDS")
        self.lower_shields_btn = LCARSButton("LOWER SHIELDS")
        
        self.btn_layout.addWidget(self.raise_shields_btn)
        self.btn_layout.addWidget(self.lower_shields_btn)
        self.layout.addLayout(self.btn_layout)

        self.raise_shields_btn.clicked.connect(self.engage_deflector)
        self.lower_shields_btn.clicked.connect(self.disable_deflector)
        
        self.layout.addStretch()

        self._deflector = engineering_core.get_subsystem("deflector")

    def engage_deflector(self):
        self.status_lbl.setText("DEFLECTOR SHIELDS: MAXIMUM YIELD")
        self.status_lbl.setStyleSheet("color: #99FF99; font-size: 20px;")
        if self._deflector:
            self._deflector.shield_status = "MAXIMUM"
            # Сигнал піде по логах

    def disable_deflector(self):
        self.status_lbl.setText("DEFLECTOR SHIELDS: STANDBY")
        self.status_lbl.setStyleSheet("color: #FF9900; font-size: 20px;")
        if self._deflector:
            self._deflector.shield_status = "STANDBY"
