"""Launch helper: show the LCARS Start Menu widget.

Run from repository root:
    python tools/launch_start_menu.py

Note: Requires PyQt6 and project dependencies installed.
"""
# Titanium Bridge Migration: import sys

from PyQt6.QtWidgets import QApplication

from lcars.ui.views.start_menu import StartMenu


def main():
    app = QApplication(sys.argv)
    # Minimal launch: no desktop parent, use defaults
    menu = StartMenu()
    menu.show_menu(floating=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
