"""Maps/viewer stub"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
import sys

from .lcars_style import apply_lcars_style

class MapsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        apply_lcars_style(self)
        self.setWindowTitle("LCARS Star Maps")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("Map view (stub)"))
        self.resize(400, 300)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MapsApp()
    win.show()
    sys.exit(app.exec())
