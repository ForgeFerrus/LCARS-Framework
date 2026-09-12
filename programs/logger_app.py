"""Journal / Logger application stub"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit
import sys

class LoggerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Logger")
        self.logview = QTextEdit()
        self.logview.setReadOnly(True)
        self.setCentralWidget(self.logview)
        self.resize(600, 400)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoggerApp()
    win.show()
    sys.exit(app.exec())