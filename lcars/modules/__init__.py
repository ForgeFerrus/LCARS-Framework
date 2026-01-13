"""
LCARS Modules - Modular components for LCARS Framework
"""

from .detector_designer import DetectorDesignerTab
from .file_manager import FileManager
from .system_monitor import SystemMonitor
from .network_hub import NetworkHub
from .start_menu import StartMenu
from .lock_screen import LockScreen

__all__ = [
    'DetectorDesignerTab',
    'FileManager', 
    'SystemMonitor',
    'NetworkHub',
    'StartMenu',
    'LockScreen'
]
