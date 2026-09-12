"""Generic network application container stub"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout, QWidget
import sys

class NetworkApps(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Network Apps")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.apps = QListWidget()
        layout.addWidget(self.apps)
        for name in ["Facebook", "Telegram", "Viber", "WhatsApp"]:
            self.apps.addItem(name)
        self.resize(300,400)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = NetworkApps()
    win.show()
    sys.exit(app.exec())