
import sys
import psutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QFrame, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QFont

import lcars.themes.lcars_palette as palette_module
from lcars.themes.lcars_palette import LCARSEra, get_era_palette

class LcarsProgressBar(QProgressBar):
    def __init__(self, color="#37A6D1", parent=None):
        super().__init__(parent)
        self.color = color
        self.setTextVisible(False)
        self.setHeight = 25
        self.setStyleSheet(f"""
            QProgressBar {{
                background-color: #050505;
                border: 1px solid #1A2332;
                border-radius: 12px;
                height: 25px;
            }}
            QProgressBar::chunk {{
                background-color: {self.color};
                border-radius: 10px;
            }}
        """)

class SystemMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.palette = get_era_palette(LCARSEra.LCARS_25TH)
        self.setWindowTitle("LCARS System Monitor")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showMaximized()
        self.setStyleSheet(f"background-color: {self.palette['background']};")
        
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.setup_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)
        
    def setup_ui(self):
        # Header
        header = QHBoxLayout()
        header.setSpacing(0)
        
        title = QLabel("◢ SYSTEM MONITORING // NODE_01")
        title.setStyleSheet(f"color: {self.palette['button_colors'][0]}; font-size: 24px; font-weight: bold; font-family: 'Swis721 BT';")
        header.addWidget(title)
        header.addStretch()
        
        exit_btn = QPushButton("✕")
        exit_btn.setFixedSize(40, 40)
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet(f"background: {self.palette['alert_colors'][0]}; color: black; border-radius: 20px; font-weight: bold;")
        header.addWidget(exit_btn)
        
        self.layout.addLayout(header)
        
        # Stats Grid
        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)
        
        self.cpu_bar = self.add_stat("CPU USAGE", 0, self.palette['button_colors'][1])
        self.mem_bar = self.add_stat("MEMORY USAGE", 1, self.palette['button_colors'][2])
        self.disk_bar = self.add_stat("DISK SPACE", 2, self.palette['button_colors'][3])
        
        self.layout.addStretch()
        
    def add_stat(self, name, row, color):
        lbl = QLabel(name)
        lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
        self.grid.addWidget(lbl, row * 2, 0)
        
        bar = LcarsProgressBar(color)
        self.grid.addWidget(bar, row * 2 + 1, 0)
        
        val_lbl = QLabel("0%")
        val_lbl.setStyleSheet(f"color: {color}; font-size: 14px;")
        self.grid.addWidget(val_lbl, row * 2 + 1, 1)
        
        return (bar, val_lbl)
        
    def update_stats(self):
        cpu = psutil.cpu_percent()
        self.cpu_bar[0].setValue(int(cpu))
        self.cpu_bar[1].setText(f"{cpu}%")
        
        mem = psutil.virtual_memory().percent
        self.mem_bar[0].setValue(int(mem))
        self.mem_bar[1].setText(f"{mem}%")
        
        disk = psutil.disk_usage('/').percent
        self.disk_bar[0].setValue(int(disk))
        self.disk_bar[1].setText(f"{disk}%")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    from PyQt6.QtWidgets import QPushButton, QGridLayout
    win = SystemMonitor()
    win.show()
    sys.exit(app.exec())
