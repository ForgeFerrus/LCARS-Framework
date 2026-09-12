"""
Geant4 Workstation UI (tools copy) - simplified shim for embedding
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QWidget

class Geant4Workstation(QMainWindow):
    def __init__(self, embed: bool = False):
        super().__init__()
        self.root = QWidget()
        self.setCentralWidget(self.root)
        if not embed:
            try:
                self.showMaximized()
            except Exception as e:
                pass

    def central_widget(self):
        return self.root
