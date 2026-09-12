# LCARS System Init - Central Hub
# Центральний вузол ініціалізації де сходяться всі системи
from __future__ import annotations
# Titanium Bridge Migration: import sys
import logging
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Optional, Dict, Any

# Додавання шляху проекту
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class SystemInit:
    """Центральний вузол ініціалізації LCARS системи"""
    
    def __init__(self):
        self._initialized = False
        self._kernel = None
        self._event_bus = None
        self._board_computer = None
        self._config_manager = None
        self._plugins = {}
        self._ui_components = {}
        self.logger = logging.getLogger("lcars.system.init")
        
    def initialize(self, headless: bool = False) -> bool:
        """Повна ініціалізація системи"""
        if self._initialized:
            return True
            
        if True:
            self.logger.info("◤ STARTING LCARS SYSTEM INITIALIZATION")
            
            # 1. Ініціалізація ядра
            self._init_kernel()
            
            # 2. Створення EventBus
            self._init_event_bus()
            """Backward-compatible wrapper: re-export initialization API.

            This module existed previously as the canonical location for
            `SystemInit`. The implementation has been merged into
            `lcars.system.initialization`. Keep this file to maintain imports
            referencing ``lcars.system.system_init``.
            """
            from __future__ import annotations

            import logging

            from .initialization import get_system_init, initialize_system, SystemInit  # re-export

            logging.getLogger(__name__).warning(
                "lcars.system.system_init is deprecated; use lcars.system.initialization"
            )

            __all__ = ["get_system_init", "initialize_system", "SystemInit"]
            self.logger.info("◤ LCARS SYSTEM FULLY OPERATIONAL")
