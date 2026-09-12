"""Standalone LCARS desktop application package.

This program lives entirely in its own directory (`lcars/programs/desktop_app`)
and includes copies of the necessary modules so that it can be shipped as a
single folder without relying on the rest of the framework.

Run with:
    python -m lcars.programs.desktop_app.main

"""
import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit,
    QSplitter, QLabel
)
from PyQt6.QtCore import Qt

# import local modules
from .modules.project_manager import ProjectManager
from .modules.system_monitor import SystemMonitor
from .modules.sound_manager import get_sound_manager

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Standalone App")
        self.resize(800, 600)

        # central splitter: left buttons, right workspace
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        left_layout = QVBoxLayout(left)

        btn_scan = QPushButton("Scan Projects")
        btn_scan.clicked.connect(self.scan_projects)
        left_layout.addWidget(btn_scan)

        btn_monitor = QPushButton("System Monitor")
        btn_monitor.clicked.connect(self.show_monitor)
        left_layout.addWidget(btn_monitor)

        btn_sound = QPushButton("Play Click")
        btn_sound.clicked.connect(lambda: get_sound_manager().play("click"))
        left_layout.addWidget(btn_sound)

        left_layout.addStretch()
        splitter.addWidget(left)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        splitter.addWidget(self.output)

        self.setCentralWidget(splitter)

        self.pm = ProjectManager(root_path=Path("."))

    def scan_projects(self):
        names = self.pm.get_project_names()
        if names:
            self.output.setText("\n".join(names))
        else:
            self.output.setText("<no projects found>")

    def show_monitor(self):
        self.monitor = SystemMonitor(self)
        self.monitor.show()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
