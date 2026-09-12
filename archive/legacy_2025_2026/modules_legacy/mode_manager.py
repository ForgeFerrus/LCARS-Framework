# Titanium Bridge Migration: from typing import Optional, Any, Dict, List

# LCARS MODE MANAGER (TITANIUM STANDARD)
# Менеджер системних режимів та станів готовності.
# Базується на DEFAULT_PALETTE з base/defaults.py.

from lcars.base.type import SystemComponent, Directive, Matrix, Chassis
# Titanium Bridge Migration: from enum import Enum
from lcars.base.default import ( TitanPalette, ActivePalette, AlertPalette, SetupFont
)
from lcars.engineering.telemetry import emit_telemetry

class MissionMode(Enum):
    CRUISE = "CRUISE"               # Крейсерський політ (Baseline)
    NORMAL = "NORMAL"               # Звичайний політ (Condition Green)
    YELLOW_ALERT = "YELLOW_ALERT"   # Посилена готовність
    RED_ALERT = "RED_ALERT"         # Бойова тривога
    CONSTRUCTION = "CONSTRUCTION"   # Режим інженерного редагування (Edit Mode)
    DIAGNOSTIC = "DIAGNOSTIC"       # Рівень 1-5 діагностика
    SILENT_RUNNING = "SILENT"       # Режим маскування
    
SystemMode = MissionMode
    
class ModeManager(SystemComponent):
    # Центральний контролер станів системи.
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        self._mode = MissionMode.CRUISE
        self._active_editor = None
        emit_telemetry("ModeManager", "PROCESS: OPERATIONAL. Baseline established.")

    def set_mode(self, mode: MissionMode, target: Optional[Matrix] = None):
        # Перемикання глобального режиму місії.
        if self._mode == mode: return

        prev_mode = self._mode
        self._mode = mode
        
        # 1. Синхронізація з Системою Тривог (Alert System)
        self._sync_alert_level(mode)
        
        # 2. Активація специфічних підсистем (Construction/Edit)
        if mode == MissionMode.CONSTRUCTION:
            self._engage_construction_tools(target)
        elif prev_mode == MissionMode.CONSTRUCTION:
            self._disengage_construction_tools()
            
        # 3. Трансляція стану
        emit_telemetry("ModeManager", f"EVENT: Mode transition: {prev_mode} -> {mode}")
        
        # 4. Оновлення тем через Event Bus (UI Sync)
        from lcars.core import Event, EventType, get_event_bus
        get_event_bus().emit(Event(
            EventType.UI_COMPONENT_UPDATED, 
            source="mode_manager", 
            data={"action": "mode_changed", "mode": mode.value}
        ))

    def _sync_alert_level(self, mode: MissionMode):
        # Приведення AlertSystem до стану режиму місії.
        from lcars.system.alert import get_alert_system, AlertLevel
        alert = get_alert_system()
        
        mapping = {
            MissionMode.CRUISE: AlertLevel.GREEN,
            MissionMode.NORMAL: AlertLevel.GREEN,
            MissionMode.YELLOW_ALERT: AlertLevel.YELLOW,
            MissionMode.RED_ALERT: AlertLevel.RED,
            MissionMode.SILENT_RUNNING: AlertLevel.YELLOW
        }
        
        if mode in mapping:
            alert.set_level(mapping[mode])

    def _engage_construction_tools(self, target: Optional[Matrix]):
        # Активація інженерного редактора (VisualEditor).
        from lcars.engineering.editor import VisualEditor
        if not target:
            target = Chassis.Nexus.instance().activeWindow() if Chassis.Nexus.instance() else None
            
        if target:
            self._active_editor = VisualEditor(target)
            self._active_editor.enabled = True
            emit_telemetry("ModeManager", f"TASK_REPORT: Construction matrix active on {target.__class__.__name__}")

    def _disengage_construction_tools(self):
        # Деактивація інструментів редагування.
        if self._active_editor:
            self._active_editor.enabled = False
            self._active_editor.deleteLater()
            self._active_editor = None
            emit_telemetry("ModeManager", "TASK_REPORT: Construction matrix collapsed.")

    @property
    def current_mode(self) -> MissionMode:
        return self._mode

# Singleton API
mode_manager = ModeManager()
get_mode_manager = lambda: mode_manager
