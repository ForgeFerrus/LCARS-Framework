"""Wi-Fi scanner stub"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
import sys

from .lcars_style import apply_lcars_style

class WiFiScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        apply_lcars_style(self)
        self.setWindowTitle("LCARS Wi-Fi Scanner")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("Scanning networks... (stub)"))
        self.resize(300, 200)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WiFiScannerApp()
    win.show()
    sys.exit(app.exec())
