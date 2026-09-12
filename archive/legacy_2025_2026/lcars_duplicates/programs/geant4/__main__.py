"""Entry point for the Geant4 workstation program.

This file is executed when running ``python -m lcars.programs.geant4``
and simply creates the QApplication and shows the main widget.  It
does not expose the word ``main`` anywhere in the command line.
"""

import sys
from PyQt6.QtWidgets import QApplication

from .launcher import run

# simply delegate to launcher module which handles sizing

if __name__ == "__main__":
    run()
