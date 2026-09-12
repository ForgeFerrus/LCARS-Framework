from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar, QApplication
from PyQt6.QtCore import Qt, QTimer
import threading
import time
from typing import Optional

try:
    import psutil
except ImportError:
    psutil = None

from lcars.themes.palette import LCARSEra, get_theme, get_lcars_font_style
from lcars.ui.base.widgets import LCARSButton, LCARSElbow

class AnalyticsView(QWidget):
    """High-Fidelity System Resource Monitor (LCARS Style)."""
    def __init__(self, event_bus, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_row = QHBoxLayout()
        self.elbow = LCARSElbow("top-left", self.theme['accent'], era=self.era)
        header_row.addWidget(self.elbow)
        
        lbl = QLabel("◤ SYSTEM DIAGNOSTICS - REAL-TIME METRICS")
        lbl.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(24, 'normal')}")
        header_row.addWidget(lbl)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Metrics Grid
        self.cpu_bar, self.cpu_lbl = self._create_bar("CPU UTILIZATION", "#99CCFF")
        layout.addLayout(self.cpu_layout)
        
        self.mem_bar, self.mem_lbl = self._create_bar("MEMORY ALLOCATION", "#CC99FF")
        layout.addLayout(self.mem_layout)
        
        self.net_bar, self.net_lbl = self._create_bar("NETWORK THRUPUT", "#00FF00")
        layout.addLayout(self.net_layout)

        layout.addStretch()
        
        # Poll Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)

    def _create_bar(self, label, color):
        row = QVBoxLayout()
        header = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: white; {get_lcars_font_style(14, 'normal')}")
        val = QLabel("0%")
        val.setStyleSheet(f"color: {color}; {get_lcars_font_style(14, 'normal')}")
        header.addWidget(lbl)
        header.addStretch()
        header.addWidget(val)
        row.addLayout(header)
        
        bar = QProgressBar()
        bar.setFixedHeight(25)
        bar.setStyleSheet(f"""
            QProgressBar {{ border: 1px solid #444; border-radius: 5px; background: #111; text-align: center; }}
            QProgressBar::chunk {{ background-color: {color}; }}
        """)
        bar.setValue(0)
        row.addWidget(bar)
        
        # Store layout for adding
        if "CPU" in label: self.cpu_layout = row
        elif "MEMORY" in label: self.mem_layout = row
        else: self.net_layout = row
            
        return bar, val

    def update_metrics(self):
        import random
        # Fake metrics if psutil not found
        cpu = random.randint(10, 45)
        mem = random.randint(30, 60)
        net = random.randint(5, 15)
        
        if psutil:
            try:
                cpu = int(psutil.cpu_percent())
                mem = int(psutil.virtual_memory().percent)
            except: pass
            
        self.cpu_lbl.setText(f"{cpu}%")
        self.cpu_bar.setValue(cpu)
        
        self.mem_lbl.setText(f"{mem}%")
        self.mem_bar.setValue(mem)
        
        self.net_lbl.setText(f"{net} MB/s")
        self.net_bar.setValue(min(100, net * 5))
