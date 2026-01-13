"""
3D Visualization UI Widget for LCARS Framework
Integrates Vispy 3D canvas into PyQt6
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
import numpy as np

from lcars.core.visualizer_3d import Vispy3DCanvas, Particle3DTrajectory, DetectorGeometry


class Vispy3DWidget(QWidget):
    """PyQt6 widget containing Vispy 3D visualization"""
    
    trajectory_loaded = pyqtSignal(int)  # Emits number of trajectories
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create canvas
        self.canvas = Vispy3DCanvas(
            background_color=(0.02, 0.05, 0.1)  # Dark blue (LCARS style)
        )
        
        # Setup layout
        layout = QVBoxLayout()
        
        # Add canvas
        layout.addWidget(self.canvas.get_canvas().native, 1)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        # Buttons
        self.btn_reset = QPushButton("Reset View")
        self.btn_reset.clicked.connect(self.canvas.reset_view)
        self.btn_reset.setFont(QFont('Arial', 9))
        control_layout.addWidget(self.btn_reset)
        
        self.btn_load = QPushButton("Load CSV")
        self.btn_load.clicked.connect(self.load_trajectories_dialog)
        self.btn_load.setFont(QFont('Arial', 9))
        control_layout.addWidget(self.btn_load)
        
        self.btn_add_detector = QPushButton("Add Detector")
        self.btn_add_detector.clicked.connect(self.add_sample_detector)
        self.btn_add_detector.setFont(QFont('Arial', 9))
        control_layout.addWidget(self.btn_add_detector)
        
        # Info label
        self.info_label = QLabel("Ready")
        self.info_label.setFont(QFont('Arial', 9))
        self.info_label.setStyleSheet("color: #00FFFF;")
        control_layout.addWidget(self.info_label)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
    
    def load_trajectories_dialog(self):
        """Load trajectories from CSV file"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Trajectory CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.load_trajectories(Path(file_path))
    
    def load_trajectories(self, csv_file: Path, limit: int = 100):
        """Load trajectories from CSV"""
        try:
            self.canvas.load_csv_trajectories(csv_file, limit=limit)
            count = len(self.canvas.trajectories)
            self.info_label.setText(f"Loaded {count} trajectories from {csv_file.name}")
            self.trajectory_loaded.emit(count)
        except Exception as e:
            self.info_label.setText(f"Error: {str(e)}")
    
    def add_sample_detector(self):
        """Add sample detector geometry"""
        detector = DetectorGeometry(shape='cylinder', dimensions=(15, 30, 2))
        self.canvas.add_detector(detector)
        self.info_label.setText("Detector added: Cylinder (r=15mm, h=30mm)")
    
    def add_trajectory_direct(self, positions: np.ndarray, particle_type: str = 'electron', 
                             energy_keV: float = 0):
        """Add trajectory directly (from code, not CSV)"""
        trajectory = Particle3DTrajectory(
            particle_id=len(self.canvas.trajectories),
            particle_type=particle_type,
            positions=positions,
            energy_keV=energy_keV
        )
        self.canvas.add_trajectory(trajectory)
        self.info_label.setText(f"Added {particle_type} trajectory ({energy_keV} keV)")
    
    def add_spectrum(self, spectrum_dict: dict):
        """Add spectrum visualization"""
        self.canvas.add_spectrum_3d(spectrum_dict)
        self.info_label.setText(f"Spectrum added: {len(spectrum_dict)} points")
    
    def clear(self):
        """Clear all visualizations"""
        self.canvas.trajectories = []
        self.canvas.trajectory_lines = []
        self.canvas = Vispy3DCanvas(background_color=(0.02, 0.05, 0.1))
        self.info_label.setText("Cleared")


# Integration helper - add this to main_window.py

def create_3d_visualization_tab() -> QWidget:
    """Create a full 3D visualization tab for LCARS Framework"""
    
    widget = QWidget()
    layout = QVBoxLayout()
    
    # Title
    title = QLabel("3D VISUALIZATION")
    title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
    title.setStyleSheet("color: #00FFFF; letter-spacing: 2px;")
    layout.addWidget(title)
    
    # 3D Canvas
    canvas_widget = Vispy3DWidget()
    layout.addWidget(canvas_widget)
    
    widget.setLayout(layout)
    return widget


# Example for testing in main_window.py:
"""
# In LCARSMainWindow.__init__:
self.tab_3d = create_3d_visualization_tab()
self.tabs.addTab(self.tab_3d, "3D VISUALIZATION")
"""
