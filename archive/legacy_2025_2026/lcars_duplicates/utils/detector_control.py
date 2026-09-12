"""Compatibility shim for detector control.

This module prefers the program-scoped implementation under
`programs.Geant4.detector_control`. If that module is not importable,
provides a minimal fallback implementation so imports don't break.
"""

from typing import Optional

try:
    from programs.Geant4.detector_control import DetectorControlPlugin, setup  # type: ignore
    __all__ = ["DetectorControlPlugin", "setup"]
except Exception:
    import logging

    logger = logging.getLogger(__name__)

    class DetectorControlPlugin:
        def __init__(self, event_bus: Optional[object] = None, config_manager: Optional[object] = None):
            self.event_bus = event_bus
            self.config_manager = config_manager
            self.state = {"power": "off", "energy": 0.0}
            self.listener_ids = []

        def on_load(self) -> bool:
            return True

        def on_unload(self) -> bool:
            self.listener_ids.clear()
            return True

    def setup(plugin_api, config=None):
        plugin = DetectorControlPlugin()
        if hasattr(plugin_api, 'register_plugin'):
            plugin_api.register_plugin(plugin)
        return plugin

    __all__ = ["DetectorControlPlugin", "setup"]
