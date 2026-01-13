"""
Geant4 Simulation Control Component
Bridges LCARS UI with Geant4 C++/Python Physics Core
"""
from PyQt6.QtWidgets import QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QWidget, QVBoxLayout
from pathlib import Path
from lcars.core.geant4_wrapper import Simulation, Particle, ParticleType

class Geant4Simulation(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # The parent is the Workstation, which already has the layout and UI setup
        # This component now only handles the logic injection and specialized controls

    def inject_controls(self, layout):
        """Inject specialized Geant4 controls into the workstation's left panel"""
        # (This logic is now largely integrated into Geant4Workstation for better 25th-century UI)
        # But we keep this for specific physics-heavy configuration
        pass

    def get_simulation_config(self):
        """Extract configuration from UI for the wrapper"""
        energy = float(self.parent.params["ENERGY (MeV)"].text())
        particle_name = "NEUTRON" # Default or from UI
        
        return {
            "energy": energy,
            "particle": particle_name,
            "events": int(self.parent.params["EVENTS"].text() or 1000)
        }

    def prepare_run(self, project_path):
        """Prepare the simulation environment (macros, configs)"""
        cfg = self.get_simulation_config()
        sim = Simulation(name="LCARS_SIM", project_path=project_path)
        
        # Configure based on UI
        sim.num_events = cfg["events"]
        # Generate macro file
        macro_content = f"/gun/energy {cfg['energy']} MeV\n/run/beamOn {cfg['events']}\n"
        macro_path = project_path / "run.mac"
        
        with open(macro_path, "w") as f:
            f.write(macro_content)
            
        return macro_path