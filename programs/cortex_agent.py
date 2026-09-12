"""Standalone runner for the CortexAgent widget"""
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys

from lcars.ui.widgets.cortex_agent import CortexAgentWidget

class CortexAgentApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Cortex Agent")
        self.agent = CortexAgentWidget()
        self.setCentralWidget(self.agent)
        self.resize(600, 400)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CortexAgentApp()
    win.show()
    sys.exit(app.exec())
