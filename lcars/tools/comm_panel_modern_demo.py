"""
Demo launcher for Modern LCARS Communication Panel UI
"""
from PyQt6.QtWidgets import QApplication
from lcars.ui.views.comm_panel_modern import CommPanelModern
# Titanium Bridge Migration: import sys

def main():
    app = QApplication(sys.argv)
    panel = CommPanelModern()
    panel.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
