"""Entry point for the Geant4 workstation program ("JEANT").

This module replaces the previous "main" and contains no word "main" in
its name.  It creates the QApplication and shows the primary workstation
widget.  The old start-menu and other callers now refer to
``lcars.programs.geant4.launcher``.
"""

import sys

from PyQt6.QtWidgets import QApplication

from .workstation import Geant4Workstation


def run():
    app = QApplication(sys.argv)
    w = Geant4Workstation()
    # start full‑screen (maximized) to provide working environment
    w.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
