# [TITAN OPS] Linguistic Matrix - Integration Entry Point

import sys
from pathlib import Path
from lcars.ui.internal import Application, MessageBox, Qt

# Ensure path is correct
proj_root = Path(__file__).resolve().parents[3]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from lcars.themes.palette import LCARSEra
from programs.learning.app import LinguisticApp

class LinguisticMatrixLCARS:
    # LCARS Integrated Linguistic Matrix Application

    def __init__(self, era=LCARSEra.LCARS_25TH):
        self.era = era
        self.window = None
    
    def initialize(self):
        # Initialize the application within LCARS framework
        # We use the new, high-fidelity app.py version
        self.window = LinguisticApp()
        return True
    
    def show(self):
        if self.window:
            self.window.showFullScreen()
            return True
        return False

    def cleanup(self):
        if self.window:
            self.window.close()

def run_linguistic_matrix_lcars(era=LCARSEra.LCARS_25TH):
    qt_app = QApplication.instance() or QApplication(sys.argv)
    
    lmatrix_app = LinguisticMatrixLCARS(era)
    if not lmatrix_app.initialize():
        return 1
    
    lmatrix_app.show()
    return qt_app.exec()

if __name__ == "__main__":
    sys.exit(run_linguistic_matrix_lcars())
