"""Astronavigation stub"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
import sys

from .lcars_style import apply_lcars_style

class AstroNavApp(QMainWindow):
    def __init__(self):
        super().__init__()
        apply_lcars_style(self)
        self.setWindowTitle("LCARS Astronavigation")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("Star charting module (stub)"))
        self.resize(450, 350)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AstroNavApp()
    win.show()
    sys.exit(app.exec())
