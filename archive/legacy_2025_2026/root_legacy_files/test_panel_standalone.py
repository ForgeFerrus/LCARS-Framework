#!/usr/bin/env python3
"""
Test PCARSPanel standalone with debug
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt
sys.path.insert(0, '.')

from lcars.themes.eras.PCARSPanel import PCARS22Panel


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCARS22Panel Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Add background to see if window shows
        self.setStyleSheet("background: #000;")
        
        self.panel = PCARS22Panel(parent=self)
        self.setCentralWidget(self.panel)
        
        # Add test label to verify window is visible
        self.test_label = QLabel("TEST WINDOW VISIBLE", self)
        self.test_label.setStyleSheet("color: red; font-size: 24px; padding: 20px;")
        self.test_label.setGeometry(50, 50, 300, 50)
        
        self.panel.show()
        print("Panel created and shown")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    print("Window shown")
    sys.exit(app.exec())
