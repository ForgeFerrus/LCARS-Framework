"""
Geant4 simulation controls (tools copy)
"""
from PyQt6.QtWidgets import QWidget
from pathlib import Path
from tools.geant4.geant4_wrapper import Simulation


class Geant4Simulation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def prepare_run(self, project_path):
        cfg = {"energy": 0.0, "events": 1000}
        sim = Simulation(name="LCARS_SIM", project_path=Path(project_path))
        sim.num_events = cfg["events"]
        macro_content = f"/gun/energy {cfg['energy']} MeV\n/run/beamOn {cfg['events']}\n"
        macro_path = Path(project_path) / "run.mac"
        macro_path.parent.mkdir(parents=True, exist_ok=True)
        with open(macro_path, "w", encoding="utf-8") as f:
            f.write(macro_content)
        return macro_path
