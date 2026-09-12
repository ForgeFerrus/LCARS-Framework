#!/usr/bin/env python3
"""
Test script to demonstrate PCARS22Panel_Simple standalone
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt

# Add project root to path
sys.path.insert(0, '.')

from lcars.themes.eras.PCARS22Panel_Simple import PCARS22Panel


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCARS22Panel Simple Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create panel
        self.panel = PCARS22Panel(parent=self)
        self.setCentralWidget(self.panel)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
