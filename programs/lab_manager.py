"""Laboratory management stub"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
import sys

from .lcars_style import apply_lcars_style

class LabManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        apply_lcars_style(self)
        self.setWindowTitle("LCARS Laboratory")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("Lab module (stub)"))
        self.resize(400, 300)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LabManagerApp()
    win.show()
    sys.exit(app.exec())
