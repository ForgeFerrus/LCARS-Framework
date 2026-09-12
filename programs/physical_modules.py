"""Physical modules stub (sensors, actuators, etc.)"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
import sys

from .lcars_style import apply_lcars_style

class PhysicalModulesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        apply_lcars_style(self)
        self.setWindowTitle("LCARS Physical Modules")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("Physical modules interface (stub)"))
        self.resize(400, 300)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PhysicalModulesApp()
    win.show()
    sys.exit(app.exec())
