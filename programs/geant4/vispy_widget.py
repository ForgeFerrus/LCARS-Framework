# ============================================================================
# Vispy 3D Visualizer — Високоточна 3D візуалізація Geant4
# ============================================================================

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
import numpy as np
import logging

from lcars.themes.palette import get_theme, LCARSEra, get_lcars_font_style
from lcars.base.interface import LCARSButton, DataBlock, ScanningBar
from .vision_tools import Vispy3DCanvas, Particle3DTrajectory

logger = logging.getLogger(__name__)

class Vispy3DWidget(QWidget):
    """
    Професійний 3D візуалізатор для Geant4.
    Відображає геометрію детектора та траєкторії частинок у реальному часі.
    """
    
    trajectory_loaded = pyqtSignal(int)

    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        
        # Створення 3D полотна
        self.canvas_container = Vispy3DCanvas()
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(5)

        # TOP CONTROL TRAY
        tray = QHBoxLayout()
        self.info = QLabel("◤ HOLOGRAPHIC GRID: CALIBRATED")
        self.info.setStyleSheet(f"color: #00FFFF; {get_lcars_font_style(12, 'bold')}")
        tray.addWidget(self.info)
        tray.addStretch()
        
        btn_reset = LCARSButton("RESET VIEW", self.theme['palette'][4], era=self.era, shape="rect")
        btn_reset.setFixedWidth(120)
        btn_reset.clicked.connect(self.reset_view)
        tray.addWidget(btn_reset)
        
        btn_clear = LCARSButton("PURGE DATA", self.theme['alerts'][0], era=self.era, shape="rect")
        btn_clear.setFixedWidth(120)
        btn_clear.clicked.connect(self.clear)
        tray.addWidget(btn_clear)
        
        vbox.addLayout(tray)

        # VISPY CANVAS
        if self.canvas_container.canvas:
            self.viewer = self.canvas_container.canvas.native
            vbox.addWidget(self.viewer, 1)
        else:
            fallback = QFrame()
            fallback.setStyleSheet("background: #050505; border: 2px dashed #333;")
            fl = QVBoxLayout(fallback)
            fl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fl.addWidget(QLabel("3D ENGINE OFFLINE\nCHECK GPU ACCELERATION"))
            vbox.addWidget(fallback, 1)

        # BOTTOM STATUS
        self.status = DataBlock("ENGINE STATUS", "NOMINAL", self.theme['palette'][1], parent=self)
        vbox.addWidget(self.status)

    def update_geometry(self, config):
        """Оновлює 3D модель детектора на основі конфігурації."""
        if not self.canvas_container.canvas: return
        
        self.canvas_container.clear()
        
        radius = config.get('radius', 2.0)
        height = config.get('height', 5.0)
        mat = config.get('material', 'Lead')
        
        # Draw Crystal (Cylinder proxy)
        self.canvas_container.add_cylinder("Crystal", radius=radius, height=height, 
                                        color=(0.3, 0.6, 1.0, 0.4))
        
        # Draw Shield (Box proxy)
        self.canvas_container.add_box("Shield", size=(radius*4, height+2, radius*4),
                                    color=(0.5, 0.5, 0.5, 0.2))
        
        self.info.setText(f"◤ GEOMETRY UPDATED: {mat.upper()} CORE")

    def add_mock_trajectories(self, count=10):
        """Генерує випадкові траєкторії для демонстрації."""
        if not self.canvas_container.canvas: return
        
        for _ in range(count):
            n_points = 50
            pos = np.zeros((n_points, 3), dtype=np.float32)
            # Simple scattering path
            pos[:, 2] = np.linspace(-10, 10, n_points)
            pos[:, 0] = np.random.normal(0, 1, n_points).cumsum() * 0.2
            pos[:, 1] = np.random.normal(0, 1, n_points).cumsum() * 0.2
            
            traj = Particle3DTrajectory(p_id=0, p_type="muon", pos=pos)
            self.canvas_container.add_trajectory(traj)
            
        self.info.setText(f"◤ SIMULATION DATA: {count} TRACKS ACTIVE")

    def reset_view(self):
        if hasattr(self.canvas_container.view, 'camera'):
            self.canvas_container.view.camera.set_range()

    def clear(self):
        self.canvas_container.clear()
        self.info.setText("◤ DATA CORE PURGED")

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    w = Vispy3DWidget()
    w.resize(800, 600)
    w.show()
    w.update_geometry({'radius': 3.0, 'height': 8.0})
    w.add_mock_trajectories(5)
    sys.exit(app.exec())
