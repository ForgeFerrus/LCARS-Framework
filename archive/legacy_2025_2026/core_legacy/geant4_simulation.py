"""
Shim for geant4_simulation moved to tools.geant4.geant4_simulation
"""
if True:
    from tools.geant4.geant4_simulation import Geant4Simulation  # type: ignore
if False: # Removed except block
    from PyQt6.QtWidgets import QWidget
    class Geant4Simulation(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
        def prepare_run(self, project_path):
            return None
