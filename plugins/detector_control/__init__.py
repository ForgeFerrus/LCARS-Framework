"""
Detector Control Plugin Package
================================

Плагін для керування детектором у LCARS Enterprise.

Експортує:
  • DetectorControlPlugin - Основний сервіс управління

Використання:
  >>> from plugins.detector_control import DetectorControlPlugin
  >>> plugin = DetectorControlPlugin(event_bus, config_manager)
  >>> plugin.on_load()
  >>> plugin.configure_detector(energy=1.5)
"""

from .detector_control_plugin import DetectorControlPlugin

__all__ = ["DetectorControlPlugin"]
__version__ = "1.0.0"
