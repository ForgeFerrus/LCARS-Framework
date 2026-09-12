"""Standalone Geant4 control application based on LCARS Framework."""

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication

# import local program modules
def run():
    from .workstation import Geant4Workstation
    app = QApplication(sys.argv)
    w = Geant4Workstation()
    w.resize(1024, 768)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
