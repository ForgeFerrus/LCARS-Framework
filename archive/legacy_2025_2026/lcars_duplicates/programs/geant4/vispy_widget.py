"""3D visualization widget used by Geant4Workstation.

Moved from lcars/modules since it is currently only consumed by the
Geant4 program.  The original module has been deprecated and will simply
raise an informative error if imported.

This file wraps :class:`Vispy3DCanvas` from the engineering/vision_tools
package and exposes a PyQt6 widget with a few convenience controls.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
import numpy as np
import logging

# depend on shared 3D primitives in engineering package
from lcars.engineering.vision_tools import Vispy3DCanvas, Particle3DTrajectory

logger = logging.getLogger(__name__)


class Vispy3DWidget(QWidget):
    """PyQt6 widget containing Vispy 3D visualization for Geant4 program."""

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
        layout.addWidget(self.canvas.canvas.native if self.canvas.canvas else QLabel("Vispy unavailable"), 1)

        # Control panel
        control_layout = QHBoxLayout()

        # Buttons
        self.btn_reset = QPushButton("Reset View")
        self.btn_reset.clicked.connect(self.canvas.reset_view if hasattr(self.canvas, 'reset_view') else lambda: None)
        self.btn_reset.setFont(QFont('Arial', 9))
        control_layout.addWidget(self.btn_reset)

        self.btn_load = QPushButton("Load CSV")
        self.btn_load.clicked.connect(self.load_trajectories_dialog)
        self.btn_load.setFont(QFont('Arial', 9))
        control_layout.addWidget(self.btn_load)

        # Info label
        self.info_label = QLabel("Ready")
        self.info_label.setFont(QFont('Arial', 9))
        self.info_label.setStyleSheet("color: #00FFFF;")
        control_layout.addWidget(self.info_label)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        self.setLayout(layout)

    def load_trajectories_dialog(self):
        """Show file dialog and load selected CSV."""
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
        """Load trajectories from a CSV file and update the canvas."""
        try:
            if hasattr(self.canvas, 'load_csv_trajectories'):
                self.canvas.load_csv_trajectories(csv_file, limit=limit)
                count = len(getattr(self.canvas, 'trajectories', []))
                self.info_label.setText(f"Loaded {count} trajectories from {csv_file.name}")
                self.trajectory_loaded.emit(count)
            else:
                self.info_label.setText("Visualizer backend missing")
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            self.info_label.setText(f"Error: {e}")

    def add_trajectory_direct(self, positions: np.ndarray, particle_type: str = 'electron',
                             energy_keV: float = 0):
        """Add trajectory directly (from code, not CSV)"""
        trajectory = Particle3DTrajectory(
            p_id=len(getattr(self.canvas, 'trajectories', [])),
            p_type=particle_type,
            pos=positions
        )
        if hasattr(self.canvas, 'add_trajectory'):
            self.canvas.add_trajectory(trajectory)
        self.info_label.setText(f"Added {particle_type} trajectory ({energy_keV} keV)")

    def clear(self):
        """Clear all visualizations (re-create canvas)."""
        if hasattr(self.canvas, 'clear'):
            self.canvas.clear()
        self.info_label.setText("Cleared")


# helper for creating tab is no longer necessary; workstation will
# instantiate Vispy3DWidget directly
