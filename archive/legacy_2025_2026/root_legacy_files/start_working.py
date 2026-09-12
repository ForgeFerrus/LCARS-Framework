#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LCARS Framework - Simple Working Boot Sequence
Проста послідовність: Boot -> Lock -> Start Menu
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

class SimpleBootScreen(QWidget):
    loading_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Loading text
        self.loading_label = QLabel("LCARS SYSTEM LOADING...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #FFCC66;
                font-family: 'Arial', sans-serif;
                font-size: 24px;
                font-weight: bold;
                text-transform: uppercase;
            }
        """)
        
        layout.addWidget(self.loading_label)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #000000;")
        
        # Full screen
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        
        # Auto-transition after 3 seconds
        QTimer.singleShot(3000, self.finish_loading)
        
    def finish_loading(self):
        print("✓ Loading finished")
        self.loading_finished.emit()
        self.close()

class SimpleLockScreen(QWidget):
    login_successful = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("◤ LCARS ACCESS TERMINAL ◢")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #FFCC66;
                font-family: 'Arial', sans-serif;
                font-size: 20px;
                font-weight: bold;
                text-transform: uppercase;
                margin-bottom: 30px;
            }
        """)
        
        # Access button
        self.access_button = QPushButton("ACCESS")
        self.access_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9966;
                color: #000000;
                font-size: 16px;
                font-weight: bold;
                padding: 15px 30px;
                border: none;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #FFAA55;
            }
        """)
        self.access_button.clicked.connect(self.on_access_clicked)
        
        # Instructions
        instructions = QLabel("Press ENTER or click ACCESS to continue")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-family: 'Arial', sans-serif;
                font-size: 14px;
                margin-top: 20px;
            }
        """)
        
        layout.addWidget(title)
        layout.addWidget(self.access_button)
        layout.addWidget(instructions)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #000000;")
        
        # Full screen
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        
        # Set focus to button
        self.access_button.setFocus()
        
    def on_access_clicked(self):
        print("✓ Access granted")
        self.login_successful.emit()
        self.close()

class SimpleStartMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("◤ LCARS MAIN MENU ◢")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #FFCC66;
                font-family: 'Arial', sans-serif;
                font-size: 18px;
                font-weight: bold;
                text-transform: uppercase;
                margin-bottom: 20px;
            }
        """)
        
        # Menu buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(5)
        
        menu_items = [
            ("DASHBOARD", "#FF9966"),
            ("SYSTEMS", "#99CCFF"),
            ("TOOLS", "#FFCC66"),
            ("SETTINGS", "#3366CC"),
            ("EXIT", "#FF6666")
        ]
        
        for text, color in menu_items:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: #000000;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px 20px;
                    border: none;
                    text-transform: uppercase;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    background-color: #FFAA55;
                }}
            """)
            btn.setMinimumHeight(40)
            buttons_layout.addWidget(btn)
        
        layout.addWidget(title)
        layout.addWidget(buttons_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #000000;")
        
        # Full screen
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()

class LCARSWindowManager:
    def __init__(self, skip_boot=False):
        from PyQt6.QtWidgets import QStackedWidget
        
        self.stack = QStackedWidget()
        
        # Create screens
        self.boot = SimpleBootScreen()
        self.lock = SimpleLockScreen()
        self.desktop = SimpleStartMenu()
        
        # Connect signals
        self.boot.loading_finished.connect(self.show_lock_screen)
        self.lock.login_successful.connect(self.show_start_menu)
        
        # Add widgets to stack
        self.stack.addWidget(self.boot)
        self.stack.addWidget(self.lock)
        self.stack.addWidget(self.desktop)
        
        # Configure stack
        self.stack.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.stack.setWindowState(Qt.WindowState.WindowFullScreen)
        
        if skip_boot:
            self.show_start_menu()
        else:
            self.stack.setCurrentWidget(self.boot)
            
        self.stack.show()

def main():
    """Simple LCARS boot sequence"""
    print("◤ LCARS TITANIUM v44.20 ◢")
    print("1. SYSTEM INITIALIZING...")
    print("✓ Core systems ready")
    print("2. LOADING INTERFACE...")
    
    app = QApplication(sys.argv)
    window_manager = LCARSWindowManager(skip_boot=False)
    
    print("✓ LCARS System Ready")
    window_manager.show_stack()
    
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n◤ SYSTEM SHUTDOWN ◢")
        sys.exit(0)
