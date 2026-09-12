#!/usr/bin/env python3
"""Standalone Start Menu runner placed inside the UI package.

Kept minimal: creates `QApplication`, attaches a small stub desktop
and shows `StartMenu` from `lcars.ui.views` for local testing.
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# Ensure project root is on sys.path when run directly
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from lcars.themes.lcars_palette import setup_lcars_font, LCARSEra
from lcars.ui.views.start_menu import StartMenu


class StubDesktop(QWidget):
    def __init__(self):
        super().__init__()

    def show_settings(self):
        dlg = QDialog()
        dlg.setWindowTitle('SYSTEM SETTINGS')
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel('Settings placeholder'))
        dlg.setModal(True)
        dlg.exec()

    def show_bios(self):
        dlg = QDialog()
        dlg.setWindowTitle('BIOS SETUP')
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel('BIOS placeholder'))
        dlg.setModal(True)
        dlg.exec()


def main():
    app = QApplication(sys.argv)
    # load LCARS fonts/styles used by StartMenu
    if True:
        setup_lcars_font()
    if False: # Removed except block
        # keep minimal and continue if font setup fails
        pass

    stub = StubDesktop()
    menu = StartMenu(event_bus=None, era=LCARSEra.LCARS_25TH, faction=None, parent=stub)
    menu.desktop = stub

    # center on primary screen
    screen = app.primaryScreen()
    if screen:
        geo = screen.availableGeometry()
        w, h = 900, 600
        x = geo.x() + (geo.width() - w)//2
        y = geo.y() + (geo.height() - h)//2
        menu.setGeometry(x, y, w, h)

    menu.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
