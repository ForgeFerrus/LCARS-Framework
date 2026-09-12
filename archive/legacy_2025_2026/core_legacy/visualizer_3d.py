"""
3D Visualization using Vispy - GPU-accelerated rendering
Renders particle trajectories, detector geometry, and spectra in 3D
Оптимізовано для Geant4 симуляцій та великих датасетів
"""

import numpy as np
from vispy import scene, color
from vispy.scene import visuals
import pandas as pd
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import List, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class Particle3DTrajectory:
    """Represents a single particle trajectory in 3D space"""
    
    def __init__(self, particle_id: int, particle_type: str, positions: np.ndarray, 
                 energy_keV: float, color_rgb: Tuple[float, float, float] = None,
                 track_id: int = None, parent_id: int = None):
        """
        Parameters:
        - particle_id: Unique identifier
        - particle_type: 'gamma', 'electron', 'neutron', etc.
        - positions: (N, 3) array of x,y,z coordinates
        - energy_keV: Particle energy in keV
        - color_rgb: RGB color (0-1 scale)
        - track_id: Track number in simulation
        - parent_id: Parent particle ID (for decay chains)
        """
        self.particle_id = particle_id
        self.particle_type = particle_type
        self.positions = np.asarray(positions, dtype=np.float32)
        self.energy_keV = energy_keV
        self.track_id = track_id
        self.parent_id = parent_id
        self.length = self._calculate_path_length()
        
        # Auto-assign color based on particle type if not provided
        if color_rgb is None:
            self.color_rgb = self._get_color_by_type(particle_type)
        else:
            self.color_rgb = color_rgb
    
    def _calculate_path_length(self) -> float:
        """Calculate total path length"""
        if len(self.positions) < 2:
            return 0.0
        diffs = np.diff(self.positions, axis=0)
        distances = np.sqrt(np.sum(diffs**2, axis=1))
        return np.sum(distances)
    
    @staticmethod
    def _get_color_by_type(particle_type: str) -> Tuple[float, float, float]:
        """Assign color by particle type"""
        colors = {
            'gamma': (0.0, 1.0, 1.0),      # Cyan - photons
            'electron': (1.0, 0.5, 0.0),   # Orange - electrons
            'positron': (1.0, 0.0, 1.0),   # Magenta - positrons
            'neutron': (0.5, 1.0, 0.5),    # Light green - neutrons
            'proton': (1.0, 0.0, 0.0),     # Red - protons
            'alpha': (1.0, 1.0, 0.0),      # Yellow - alphas
            'antineutrino': (0.5, 0.5, 1.0), # Light blue - neutrinos
        }
        return colors.get(particle_type, (0.5, 0.5, 0.5))  # Gray default


class DetectorGeometry:
    """Represents detector geometry in 3D"""
    
    def __init__(self, shape: str = 'cylinder', dimensions: Tuple[float, float, float] = None):
        """
        Parameters:
        - shape: 'cylinder', 'box', 'sphere'
        - dimensions: (radius/width, height/length, thickness) in mm
        """
        self.shape = shape
        self.dimensions = dimensions or (10.0, 20.0, 1.0)
    
    def get_visual(self) -> visuals.Mesh:
        """Generate Vispy visual for detector"""
        if self.shape == 'cylinder':
            mesh = visuals.Mesh(vertices=self._cylinder_vertices(), 
                               faces=self._cylinder_faces(),
                               color=(0.2, 0.6, 0.8, 0.3))  # Semi-transparent blue
            return mesh
        elif self.shape == 'box':
            mesh = visuals.Box(width=self.dimensions[0], 
                             height=self.dimensions[1],
                             depth=self.dimensions[2],
                             color=(0.2, 0.6, 0.8, 0.3))
            return mesh
        return None
    
    @staticmethod
    def _cylinder_vertices() -> np.ndarray:
        """Generate cylinder vertices"""
        theta = np.linspace(0, 2*np.pi, 32, endpoint=False)
        x = np.cos(theta)
        y = np.sin(theta)
        z_bottom = np.zeros_like(theta)
        z_top = np.ones_like(theta)
        
        vertices = np.vstack([
            np.column_stack([x, y, z_bottom]),
            np.column_stack([x, y, z_top]),
            [[0, 0, 0], [0, 0, 1]]  # Center points
        ])
        return vertices
    
    @staticmethod
    def _cylinder_faces() -> np.ndarray:
        """Generate cylinder face indices"""
        n = 32
        faces = []
        
        # Side faces
        for i in range(n):
            next_i = (i + 1) % n
            faces.append([i, next_i, n + next_i])
            faces.append([i, n + next_i, n + i])
        
        return np.array(faces)


class Spectrum3DVisualizer:
    """3D visualization of gamma-ray spectrum"""
    
    def __init__(self, spectrum_data: dict):
        """
        Parameters:
        - spectrum_data: dict with energy_keV and counts
        """
        self.spectrum_data = spectrum_data
        self.vertices = self._generate_spectrum_mesh()
    
    def _generate_spectrum_mesh(self) -> np.ndarray:
        """Convert spectrum data to 3D surface"""
        energies = list(self.spectrum_data.keys())
        counts = list(self.spectrum_data.values())
        
        # Create grid for spectrum surface
        n_energy = len(energies)
        x = np.array(energies)
        y = np.zeros_like(x)
        z = np.array(counts)
        
        # Normalize for visualization
        x_norm = x / max(x) if max(x) > 0 else x
        z_norm = z / max(z) if max(z) > 0 else z
        
        vertices = np.column_stack([x_norm, y, z_norm])
        return vertices


class Vispy3DCanvas:
    """Main 3D visualization canvas using Vispy
    
    Оптимізовано для:
    - Великих датасетів (10,000+ траєкторій)
    - Швидкого рендерингу GPU
    - Інтеграції з Geant4 результатами
    """
    
    def __init__(self, parent=None, background_color=(0.02, 0.05, 0.1)):
        """
        Initialize 3D canvas
        
        Parameters:
        - parent: PyQt parent widget (optional)
        - background_color: RGB tuple (0-1 scale)
        """
        self.canvas = scene.SceneCanvas(
            keys='interactive',
            show=False,
            bgcolor=background_color,
            size=(800, 600)
        )
        
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.cameras.TurntableCamera(fov=60)
        
        self.trajectories: List[Particle3DTrajectory] = []
        self.trajectory_cache: Dict[str, List[Particle3DTrajectory]] = {}
        self.detector: Optional[DetectorGeometry] = None
        
        # Visualization elements
        self.trajectory_lines = []
        self.trajectory_visuals = {}  # Grouped by particle type
        self.detector_visual = None
        self.spectrum_visual = None
        
        # Performance tracking
        self.frame_count = 0
        self.max_trajectories_display = 1000  # GPU limit
        self.current_filter = None
        
        # Add axis helper
        self._add_axis()
        
        logger.info("Vispy3DCanvas інізаліхозовано")
    
    def _add_axis(self):
        """Add XYZ axis visualization"""
        axis_length = 30
        
        # X axis (red)
        x_line = visuals.Line(
            pos=np.array([[0, 0, 0], [axis_length, 0, 0]], dtype=np.float32),
            color='red', width=2
        )
        self.view.add(x_line)
        
        # Y axis (green)
        y_line = visuals.Line(
            pos=np.array([[0, 0, 0], [0, axis_length, 0]], dtype=np.float32),
            color='green', width=2
        )
        self.view.add(y_line)
        
        # Z axis (blue)
        z_line = visuals.Line(
            pos=np.array([[0, 0, 0], [0, 0, axis_length]], dtype=np.float32),
            color='blue', width=2
        )
        self.view.add(z_line)
    
    def add_trajectory(self, trajectory: Particle3DTrajectory):
        """Add particle trajectory to visualization"""
        if len(trajectory.positions) < 2:
            return
        
        # Grouped visualization by particle type for efficiency
        particle_type = trajectory.particle_type
        
        if particle_type not in self.trajectory_visuals:
            self.trajectory_visuals[particle_type] = []
        
        # Create line visual
        line = visuals.Line(
            pos=trajectory.positions,
            color=trajectory.color_rgb,
            width=1.5,
            connect='segments'
        )
        self.view.add(line)
        
        self.trajectories.append(trajectory)
        self.trajectory_visuals[particle_type].append(line)
        
        if len(self.trajectories) % 100 == 0:
            logger.debug(f"Завантажено {len(self.trajectories)} траєкторій")
    
    def add_batch_trajectories(self, trajectories: List[Particle3DTrajectory], 
                               progress_callback=None):
        """Add multiple trajectories efficiently with progress tracking"""
        for i, traj in enumerate(trajectories):
            self.add_trajectory(traj)
            if progress_callback and i % 100 == 0:
                progress_callback(i, len(trajectories))
        
        logger.info(f"Пакетно завантажено {len(trajectories)} траєкторій")
    
    def filter_by_particle_type(self, particle_type: str):
        """Show only trajectories of specific type"""
        # Clear all trajectory visuals
        for visuals_list in self.trajectory_visuals.values():
            for visual in visuals_list:
                visual.parent = None
        
        # Re-add only selected type
        if particle_type in self.trajectory_visuals:
            for visual in self.trajectory_visuals[particle_type]:
                self.view.add(visual)
        
        self.current_filter = particle_type
        logger.info(f"Фільтр за типом: {particle_type}")
    
    def filter_by_energy_range(self, min_energy_keV: float, max_energy_keV: float):
        """Show only trajectories within energy range"""
        filtered = [t for t in self.trajectories 
                   if min_energy_keV <= t.energy_keV <= max_energy_keV]
        
        # Clear and rebuild
        for visual in self.trajectory_lines:
            visual.parent = None
        self.trajectory_lines.clear()
        self.trajectory_visuals.clear()
        
        for traj in filtered:
            self.add_trajectory(traj)
        
        logger.info(f"Фільтр за енергією: {min_energy_keV}-{max_energy_keV} keV. " +
                   f"Відображено {len(filtered)} траєкторій")
    
    def get_statistics(self) -> Dict[str, any]:
        """Get visualization statistics"""
        stats = {
            'total_trajectories': len(self.trajectories),
            'particle_types': {},
            'energy_range': None,
            'average_path_length': 0.0
        }
        
        if self.trajectories:
            for traj in self.trajectories:
                ptype = traj.particle_type
                stats['particle_types'][ptype] = stats['particle_types'].get(ptype, 0) + 1
            
            energies = [t.energy_keV for t in self.trajectories]
            stats['energy_range'] = (min(energies), max(energies))
            
            path_lengths = [t.length for t in self.trajectories]
            stats['average_path_length'] = np.mean(path_lengths)
        
        return stats
    
    def add_detector(self, detector: DetectorGeometry):
        """Add detector geometry to visualization"""
        self.detector = detector
        visual = detector.get_visual()
        if visual:
            self.view.add(visual)
            self.detector_visual = visual
    
    def add_spectrum_3d(self, spectrum_data: dict):
        """Add 3D spectrum visualization"""
        visualizer = Spectrum3DVisualizer(spectrum_data)
        
        # Create line series for spectrum peaks
        vertices = visualizer.vertices
        if len(vertices) > 1:
            spectrum_line = visuals.Line(
                pos=vertices,
                color=(0.0, 1.0, 0.5),  # Cyan-green
                width=2
            )
            self.view.add(spectrum_line)
            self.spectrum_visual = spectrum_line
    
    def load_csv_trajectories(self, csv_file: Path, limit: int = None):
        """Load particle trajectories from CSV file (Geant4 output)
        
        Expected CSV columns:
        - particle_id or track_id
        - x, y, z (coordinates)
        - particle_type or pdgid
        - energy_keV or ke
        - parent_id (optional, for decay chains)
        """
        if True:
            logger.info(f"Завантаження траєкторій з {csv_file}")
            df = pd.read_csv(csv_file)
            
            # Auto-detect column names (common variants)
            particle_id_col = 'particle_id' if 'particle_id' in df.columns else 'track_id'
            particle_type_col = 'particle_type' if 'particle_type' in df.columns else 'pdgid'
            energy_col = 'energy_keV' if 'energy_keV' in df.columns else 'ke'
            
            trajectory_count = 0
            
            if particle_id_col in df.columns:
                for i, (particle_id, group) in enumerate(df.groupby(particle_id_col)):
                    if limit and i >= limit:
                        break
                    
                    positions = group[['x', 'y', 'z']].values
                    particle_type = str(group[particle_type_col].iloc[0])
                    energy = float(group[energy_col].iloc[0]) if energy_col in group.columns else 0
                    
                    parent_id = int(group['parent_id'].iloc[0]) if 'parent_id' in group.columns else None
                    track_id = i
                    
                    trajectory = Particle3DTrajectory(
                        particle_id=int(particle_id),
                        particle_type=particle_type,
                        positions=positions,
                        energy_keV=energy,
                        track_id=track_id,
                        parent_id=parent_id
                    )
                    self.add_trajectory(trajectory)
                    trajectory_count += 1
            
            logger.info(f"Успішно завантажено {trajectory_count} траєкторій")
            
        if False: # Removed except block
            logger.error(f"Помилка при завантаженні траєкторій: {e}")
    
    def reset_view(self):
        """Reset camera to default view"""
        self.view.camera.set_range()
        logger.debug("Камера скинута на стандартний вигляд")
    
    def get_canvas(self):
        """Return the Vispy canvas for embedding in PyQt"""
        return self.canvas
    
    def show(self):
        """Show the canvas"""
        self.canvas.show()


# Example usage functions
def demo_simple_trajectory():
    """Demo: simple trajectory visualization"""
    canvas = Vispy3DCanvas()
    
    # Create a simple electron trajectory
    positions = np.array([
        [0, 0, 0],
        [5, 2, 3],
        [10, 5, 8],
        [15, 3, 12]
    ])
    
    trajectory = Particle3DTrajectory(
        particle_id=1,
        particle_type='electron',
        positions=positions,
        energy_keV=50.0
    )
    
    canvas.add_trajectory(trajectory)
    
    # Add detector
    detector = DetectorGeometry(shape='cylinder', dimensions=(10, 20, 1))
    canvas.add_detector(detector)
    
    return canvas


def demo_spectrum_3d():
    """Demo: 3D spectrum visualization"""
    canvas = Vispy3DCanvas()
    
    # Create sample spectrum
    spectrum = {
        100: 500,
        200: 1200,
        300: 800,
        400: 600,
        500: 400,
    }
    
    canvas.add_spectrum_3d(spectrum)
    return canvas
