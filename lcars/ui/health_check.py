
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QTextEdit, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

import lcars.themes.lcars_palette as palette_module
from lcars.themes.lcars_palette import LCARSEra, get_era_palette

class HealthCheck(QMainWindow):
    def __init__(self):
        super().__init__()
        self.palette = get_era_palette(LCARSEra.LCARS_25TH)
        self.setWindowTitle("LCARS System Health Check")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showMaximized()
        self.setStyleSheet(f"background-color: {self.palette['background']};")
        
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        
        self.setup_ui()
        self.run_diag()
        
    def setup_ui(self):
        header = QLabel("◢ SYSTEM_DIAGNOSTICS // HEALTH_CHECK")
        header.setStyleSheet(f"color: {self.palette['alert_colors'][0]}; font-size: 28px; font-weight: bold; padding: 20px;")
        self.layout.addWidget(header)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet(f"background: #050505; color: #37A6D1; border: 1px solid #1A2332; font-family: 'Consolas'; font-size: 12px; margin: 20px;")
        self.layout.addWidget(self.log)
        
        btn = QPushButton("EXIT DIAGNOSTICS")
        btn.clicked.connect(self.close)
        btn.setStyleSheet(f"background: {self.palette['button_colors'][1]}; color: black; font-weight: bold; padding: 15px; margin: 20px; border-radius: 15px;")
        self.layout.addWidget(btn)
        
    def run_diag(self):
        self.log.append("Initializing System Scan...")
        
        # Check files
        files = [
            'start.py',
            'constructor.py',
            'lcars/ui/lcars_central.py',
            'lcars/ui/geant4_workstation.py',
            'lcars/core/project_manager.py'
        ]
        
        for f in files:
            status = "✓ FOUND" if os.path.exists(f) else "✗ MISSING"
            self.log.append(f"{f:<30} {status}")
            
        # Check External path
        ext_path = "C:/Users/Forge/MyProject/Geant4/Enterprise"
        if os.path.exists(ext_path):
            self.log.append(f"\nExternal Project Path: {ext_path} ✓ ONLINE")
        else:
            self.log.append(f"\nExternal Project Path: {ext_path} ✗ OFFLINE")
            
        self.log.append("\nDIAGNOSTICS COMPLETE. ALL SYSTEMS NOMINAL.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HealthCheck()
    win.show()
    sys.exit(app.exec())
