"""
Demo launcher for LCARS Communication Panel UI
"""
from PyQt6.QtWidgets import QApplication
from lcars.ui.views.comm_panel import CommPanel
# Titanium Bridge Migration: import sys

def main():
    app = QApplication(sys.argv)
    panel = CommPanel()
    panel.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
