"""Detector Control module moved under the Geant4 program.

Lightweight plugin-like class for detector management used by Geant4 tools.
"""
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DetectorControlPlugin:
    def __init__(self, event_bus: Optional[object] = None, config_manager: Optional[object] = None):
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.state = {"power": "off", "energy": 0.0}
        self.listener_ids = []

    def on_load(self) -> bool:
        # perform any startup initialization specific to detector control
        self._setup_event_listeners()
        self._load_configuration()
        self._export_api()
        return True

    def on_unload(self) -> bool:
        self.listener_ids.clear()
        return True

    def _setup_event_listeners(self):
        pass

    def _load_configuration(self):
        pass

    def _export_api(self):
        pass


def setup(plugin_api, config=None):
    plugin = DetectorControlPlugin()
    if hasattr(plugin_api, 'register_plugin'):
        plugin_api.register_plugin(plugin)
    return plugin
