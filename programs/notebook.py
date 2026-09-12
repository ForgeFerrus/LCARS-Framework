"""Simple Notes / Notebook program stub"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit
import sys

class NotebookApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Notebook")
        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)
        self.resize(600, 400)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = NotebookApp()
    win.show()
    sys.exit(app.exec())