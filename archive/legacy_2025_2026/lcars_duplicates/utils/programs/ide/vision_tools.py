"""
LCARS Substrate - AI, Vision, Perception
Об'єднаний модуль для AI комп'ютерного зору та 3D візуалізації
"""

import logging
import os
import random
from typing import Optional, Dict, Any

logger = logging.getLogger("lcars.substrate")

# ============================================================================
# VISION & PERCEPTION
# ============================================================================

try:
    import numpy as np
    from PIL import Image

    VISION_AVAILABLE = True
except ImportError:
    np = None
    Image = None
    VISION_AVAILABLE = False
    logger.warning("Vision libraries (numpy/PIL) not available")


class VisionHelper:
    """Helper class for vision and AI operations"""
    
    def __init__(self):
        self.ai_provider = None
        self.ui_analyzer = None
    
    def analyze_image(self, image_path):
        """Analyze image for UI elements"""
        if self.ui_analyzer:
            return self.ui_analyzer.analyze(image_path)
        return None
    
    def ask_ai(self, prompt):
        """Ask AI provider"""
        if self.ai_provider:
            return self.ai_provider.ask(prompt)
        return "AI not available"


class UIAnalyzer:
    """Аналізує зображення для визначення позицій UI елементів"""

    @staticmethod
    def analyze_background(image_path: str) -> Dict[str, Any]:
        """Аналізує зображення і повертає позиції UI регіонів"""
        if not VISION_AVAILABLE:
            logger.warning("Vision not available")
            return {}

        try:
            im = Image.open(image_path).convert("RGB")
            w, h = im.size

            # Спрощений аналіз
            return {
                "image_size": [w, h],
                "faction_buttons": [
                    {"x": 10, "y": 100 + i * 100, "w": 90, "h": 80} for i in range(4)
                ],
                "info_screen": {
                    "x": w // 2 - 300,
                    "y": h // 2 - 175,
                    "w": 600,
                    "h": 350,
                },
            }
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            logger.error(f"Failed to analyze {image_path}: {e}")
            return {}


# ============================================================================
# 3D VISUALIZATION
# ============================================================================


class Particle3DTrajectory:
    """Траєкторія частинки для 3D візуалізації"""

    def __init__(self, p_id: int, p_type: str, pos: Any):
        self.p_id = p_id
        self.p_type = p_type
        self.pos = pos


class Vispy3DCanvas:
    """3D візуалізатор на базі Vispy"""

    def __init__(self, background=(0.02, 0.05, 0.1)):
        try:
            from vispy import scene
            from vispy.scene import visuals

            self.canvas = scene.SceneCanvas(
                keys="interactive", bgcolor=background, size=(800, 600)
            )
            self.view = self.canvas.central_widget.add_view()
            self.view.camera = 'turntable' # Proper 3D camera
            
            self.geometry = []
            self.trajectories = []
            
            logger.info("3D Visualizer: GPU acceleration active")
        except ImportError:
            logger.warning("Vispy not available - 3D visualization disabled")
            self.canvas = None

    def add_box(self, name, size=(10, 10, 10), color=(0.5, 0.5, 0.5, 0.3)):
        """Adds a 3D box to the scene."""
        if not self.canvas: return
        from vispy.scene import visuals
        box = visuals.Box(width=size[0], height=size[1], depth=size[2], 
                         color=color, edge_color='white', parent=self.view.scene)
        self.geometry.append(box)
        return box

    def add_cylinder(self, name, radius=5, height=10, color=(0.7, 0.4, 0.1, 0.3)):
        """Adds a 3D cylinder to the scene."""
        if not self.canvas: return
        from vispy.scene import visuals
        # Vispy doesn't have a direct 'Cylinder' in scene.visuals as easily as Box,
        # but we can use Tube or Mesh. For simplicity, let's use a Box fallback or custom mesh.
        cyl = visuals.Box(width=radius*2, height=height, depth=radius*2,
                         color=color, edge_color='cyan', parent=self.view.scene)
        self.geometry.append(cyl)
        return cyl

    def add_trajectory(self, trajectory):
        """Adds a particle trajectory (LinePlot) to the scene."""
        if not self.canvas: return
        from vispy.scene import visuals
        line = visuals.Line(pos=trajectory.pos, color='red', parent=self.view.scene)
        self.trajectories.append(line)

    def clear(self):
        """Clears all objects from the scene."""
        for obj in self.geometry + self.trajectories:
            obj.parent = None
        self.geometry = []
        self.trajectories = []

    def show(self):
        if self.canvas:
            self.canvas.show()
