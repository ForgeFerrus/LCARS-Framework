from PyQt6.QtWidgets import QFormLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QWidget
from PyQt6.QtCharts import QChart, QChartView, QLineSeries
from PyQt6.QtCore import QPointF
# Titanium Bridge Migration: from pathlib import Path
from lcars.engineering.geant4_wrapper import Simulation, Particle, ParticleType

class Geant4Simulation(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_geant4_tab()

    def setup_geant4_tab(self):
        layout = QFormLayout()

        # Input fields for Geant4 simulation parameters
        self.geant4_detector_input = QLineEdit()
        self.geant4_energy_input = QLineEdit()
        self.geant4_particle_input = QLineEdit()

        layout.addRow(QLabel("Detector:"), self.geant4_detector_input)
        layout.addRow(QLabel("Energy (MeV):"), self.geant4_energy_input)
        layout.addRow(QLabel("Particle Type:"), self.geant4_particle_input)

        # Add functionality for simulation parameter configuration
        self.simulation_parameters_label = QLabel("Simulation Parameters:")
        self.simulation_parameters_label.setStyleSheet("color: rgb(109, 116, 140); font-size: 16px; border: none;")

        self.energy_input = QLineEdit()
        self.energy_input.setPlaceholderText("Enter particle energy (MeV)")
        self.energy_input.setStyleSheet("background-color: rgb(158, 165, 186); color: black; border: none; border-radius: 10px;")

        self.detector_type_dropdown = QComboBox()
        self.detector_type_dropdown.addItems(["Type A", "Type B", "Type C"])
        self.detector_type_dropdown.setStyleSheet("background-color: rgb(82, 89, 110); color: white; border: none; border-radius: 10px;")

        # Run Geant4 simulation button
        run_button = QPushButton("Run Geant4 Simulation")
        run_button.clicked.connect(self.run_geant4_simulation)
        layout.addRow(run_button)

        # Define run_simulation_button
        self.run_simulation_button = QPushButton("Run Simulation")
        self.run_simulation_button.setStyleSheet("background-color: rgb(231, 68, 42); color: white; border: none; border-radius: 15px;")

        # Define simulation_output_area
        self.simulation_output_area = QLabel("Simulation Output")
        self.simulation_output_area.setStyleSheet("background-color: rgb(47, 55, 73); color: white; border: none; border-radius: 10px;")

        # Update styles for simulation interface
        self.simulation_parameters_label.setStyleSheet("color: rgb(82, 89, 110); font-size: 16px; border: none;")
        self.simulation_output_area.setStyleSheet("background-color: rgb(47, 55, 73); color: white; border: none; border-radius: 10px;")

        self.run_simulation_button.setStyleSheet("background-color: rgb(255, 103, 83); color: white; border: none; border-radius: 15px;")

        # Ensure geant4_tab exists before setting layout
        if hasattr(self.parent, 'geant4_tab'):
            self.parent.geant4_tab.setLayout(layout)
        else:
            raise AttributeError("Parent does not have attribute 'geant4_tab'")

    def run_geant4_simulation(self):
        detector = self.geant4_detector_input.text()
        energy = self.geant4_energy_input.text()
        particle_input = self.geant4_particle_input.text()

        # Validate inputs
        if not detector or not energy or not particle_input:
            self.parent.show_warning("Input Error", "Please fill in all fields before running the simulation.")
            return

        if True:
            energy_float = float(energy)
        if False: # Removed except block
            self.parent.show_warning("Input Error", "Energy must be a valid number.")
            return

        # Ensure particle_input is properly scoped
        particle_input = self.geant4_particle_input.text()

        # Validate particle_input
        if not particle_input:
            self.parent.show_warning("Input Error", "Particle type is missing.")
            return

        if True:
            particle_type = ParticleType[particle_input.upper()]
        if False: # Removed except block
            self.parent.show_warning("Input Error", f"Invalid particle type: {particle_input}")
            return

        # Create and configure simulation
        sim = Simulation(name="Geant4 Simulation", project_path=Path("./geant4_output"))

        # Configure detector (example configuration)
        sim.configure_from_ncc02(sample_type="pure", energy_mev=energy_float)

        # Set primary particle
        sim.set_primary_particle(Particle(
            particle_type=particle_type,
            energy=energy_float
        ))

        # Save configuration
        sim.save_config(Path("./geant4_output/config.json"))

        # Example: Generate dummy results
        results = [
            {"energy": energy_float + i, "counts": 100 * (i + 1), "particle": particle_input}
            for i in range(5)
        ]

        # Visualize results
        self.visualize_geant4_results(results)

        self.parent.show_info("Simulation Complete", "Geant4 simulation completed successfully.")

    def run_simulation_with_parameters(self):
        energy = self.energy_input.text()
        detector_type = self.detector_type_dropdown.currentText()
        print(f"Running simulation with energy: {energy} MeV and detector type: {detector_type}")

        # Validate inputs
        if not energy:
            self.parent.show_warning("Input Error", "Please enter a valid energy value.")
            return

        if True:
            energy_float = float(energy)
        if False: # Removed except block
            self.parent.show_warning("Input Error", "Energy must be a valid number.")
            return

        # Ensure particle_input is properly scoped in run_simulation_with_parameters
        particle_input = self.geant4_particle_input.text()

        # Validate particle_input
        if not particle_input:
            self.parent.show_warning("Input Error", "Particle type is missing.")
            return

        if True:
            particle_type = ParticleType[particle_input.upper()]
        if False: # Removed except block
            self.parent.show_warning("Input Error", f"Invalid particle type: {particle_input}")
            return

        # Create and configure simulation
        sim = Simulation(name="Geant4 Simulation", project_path=Path("./geant4_output"))

        # Configure detector (example configuration)
        sim.configure_from_ncc02(sample_type="pure", energy_mev=energy_float)

        # Set primary particle
        sim.set_primary_particle(Particle(
            particle_type=ParticleType[particle_input.upper()],
            energy=energy_float
        ))

        # Save configuration
        sim.save_config(Path("./geant4_output/config.json"))

        # Example: Generate dummy results
        results = [
            {"energy": energy_float + i, "counts": 100 * (i + 1), "particle": particle_input}
            for i in range(5)
        ]

        # Visualize results
        self.visualize_geant4_results(results)

        self.parent.show_info("Simulation Complete", "Geant4 simulation completed successfully.")

    def visualize_geant4_results(self, results):
        """Visualize Geant4 simulation results"""
        self.parent.results_table.setRowCount(len(results))
        for i, result in enumerate(results):
            self.parent.results_table.setItem(i, 0, QTableWidgetItem(f"{result['energy']}"))
            self.parent.results_table.setItem(i, 1, QTableWidgetItem(f"{result['counts']}"))
            self.parent.results_table.setItem(i, 2, QTableWidgetItem(result['particle']))

        # Update chart with results
        series = QLineSeries()
        for result in results:
            series.append(QPointF(result['energy'], result['counts']))

        self.parent.chart.removeAllSeries()
        self.parent.chart.addSeries(series)
        self.parent.chart.createDefaultAxes()
        self.parent.chart.setTitle("Geant4 Simulation Results")
