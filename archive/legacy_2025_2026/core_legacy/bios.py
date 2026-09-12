#!/usr/bin/env python3
# LCARS BIOS - Аварійний режим та ініціалізація системи

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# Додаємо шлях до проекту
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QTextEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class LCARSEmergencyMode(QWidget):
    # Аварійний режим LCARS
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #000000;")
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("background-color: #FF3333;")
        header_layout = QHBoxLayout(header)
        
        title = QLabel("LCARS EMERGENCY MODE")
        title.setStyleSheet("color: #000000; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        layout.addWidget(header)
        
        # Console
        self.console = QTextEdit()
        self.console.setStyleSheet("""
            background-color: #000000; 
            color: #FF3333; 
            font-family: 'Courier New'; 
            font-size: 14px;
            border: 2px solid #FF3333;
        """)
        self.console.setReadOnly(True)
        layout.addWidget(self.console)
        
        # Footer
        footer = QFrame()
        footer.setFixedHeight(40)
        footer.setStyleSheet("background-color: #FF3333;")
        footer_layout = QHBoxLayout(footer)
        
        footer_label = QLabel("STARFLEET EMERGENCY SYSTEM")
        footer_label.setStyleSheet("color: #000000; font-size: 14px;")
        footer_layout.addWidget(footer_label)
        
        layout.addWidget(footer)
        
        # Запускаємо ініціалізацію
        self.start_initialization()
        
    def start_initialization(self):
        # Ініціалізація системи в аварійному режимі
        self.console.append("=== LCARS EMERGENCY BOOT ===")
        self.console.append("Initializing critical systems...")
        
        QTimer.singleShot(1000, self.step1)
        
    def step1(self):
        self.console.append("✓ Core systems loaded")
        QTimer.singleShot(1000, self.step2)
        
    def step2(self):
        self.console.append("✓ Emergency protocols active")
        QTimer.singleShot(1000, self.step3)
        
    def step3(self):
        self.console.append("✓ System ready for recovery")
        self.console.append("\nPress any key to continue...")

def run_emergency_mode():
    # Запуск аварійного режиму
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    emergency = LCARSEmergencyMode()
    emergency.showFullScreen()
    
    return app.exec()
