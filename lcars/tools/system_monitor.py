import psutil
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer
from lcars.themes.palette import LCARSEra
from lcars.base.interface import StatBar

class SystemMonitorView(QWidget):
    # Високоточний монітор системних ресурсів (стиль LCARS).
    # Переміщено з Geant4 Analytics у загальні Tools за запитом архітектури.
    def __init__(self, theme, accent, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.accent = accent
        self.era = era
        self.faction = faction
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setSpacing(10)
        p = self.theme.get("palette", ["#3366CC"] * 10)
        self.cpu_bar = StatBar("CPU LOAD", p[0], faction=self.faction, parent=self)
        self.mem_bar = StatBar("MEMORY", p[1], faction=self.faction, parent=self)
        vbox.addWidget(self.cpu_bar)
        vbox.addWidget(self.mem_bar)
        vbox.addStretch()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)

    def update_metrics(self):
        self.cpu_bar.setValue(int(psutil.cpu_percent()))
        self.mem_bar.setValue(int(psutil.virtual_memory().percent))
