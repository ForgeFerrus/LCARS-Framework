"""Minimal desktop launcher that opens StartMenu via a desktop window.

Run from repo root:
    python tools/launch_via_desktop.py

Adds the repo root to PYTHONPATH when running to resolve `lcars` imports.
"""
# Titanium Bridge Migration: import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

from lcars.ui.views.start_menu import StartMenu


def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("LCARS Minimal Desktop")
    win.setGeometry(100, 100, 800, 600)

    central = QWidget()
    layout = QVBoxLayout(central)
    btn = QPushButton("SYSTEM ACCESS")
    btn.setFixedHeight(60)
    layout.addWidget(btn)
    win.setCentralWidget(central)

    def open_menu():
        menu = StartMenu(None, parent=win)
        menu.show_menu(floating=True)

    btn.clicked.connect(open_menu)

    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
