# PCARS central core orchestration.

from __future__ import annotations
import threading
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .service_registry import ServiceRegistry
from .config_store import ConfigStore
from .process_manager import ProcessManager
from .ui_bridge import UIBridge
from .timeline import EraTimeline


class OSEventType(Enum):
    OS_STARTUP = "os:startup"
    OS_SHUTDOWN = "os:shutdown"
    OS_STATUS_REQUEST = "os:status_request"
    OS_STATUS_UPDATE = "os:status_update"
    ERA_CHANGED = "era:changed"
    FEATURE_EXECUTED = "feature:executed"
    CONFIG_CHANGED = "config:changed"
    COMMAND_RECEIVED = "command:received"


@dataclass
class OSEvent:
    event_type: OSEventType
    source: str
    payload: Dict[str, Any] = field(default_factory=dict)


class OSEventBus:
    _instance: Optional["OSEventBus"] = None

    def __new__(cls) -> "OSEventBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.listeners = {}
            cls._instance.history = []
        return cls._instance

    def subscribe(self, event_type: OSEventType, callback: Callable[[OSEvent], None]) -> None:
        self.listeners.setdefault(event_type, []).append(callback)

    def emit(self, event: OSEvent) -> None:
        self.history.append(event)
        for callback in list(self.listeners.get(event.event_type, [])):
            try:
                callback(event)
            except Exception:
                pass

    def GetHistory(self, eventType: Optional[OSEventType] = None) -> List[OSEvent]:
        if eventType is None:
            return list(self.history)
        return [evt for evt in self.history if evt.event_type == eventType]

    def ClearHistory(self) -> None:
        self.history.clear()


class OSNexus:
    def __init__(self, eventBus: OSEventBus) -> None:
        self.Memory: Dict[str, Any] = {}
        self.EventBus = eventBus

    def Set(self, key: str, value: Any) -> None:
        self.Memory[key] = value
        self.EventBus.emit(OSEvent(OSEventType.OS_STATUS_UPDATE, "nexus", {"key": key, "value": value}))

    def Get(self, key: str, default: Any = None) -> Any:
        return self.Memory.get(key, default)


class OSTaskExecutor:
    def __init__(self, eventBus: OSEventBus) -> None:
        self.EventBus = eventBus

    def RunTask(self, target: Callable[..., Any], *args: Any, **kwargs: Any) -> threading.Thread:
        thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread


class OSCommandCenter:
    def __init__(self, manager: "PCARSCentral") -> None:
        self.manager = manager

    def Execute(self, command: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        self.manager.EventBus.emit(OSEvent(OSEventType.COMMAND_RECEIVED, "command_center", {"command": command, "payload": payload}))

        if command == "status":
            return self.manager.GetStatus()

        if command == "boot":
            self.manager.BootSequence()
            return {"result": "booted"}

        if command == "shutdown":
            self.manager.ShutdownSequence()
            return {"result": "shutdown"}

        if command == "select_era":
            era_key = payload.get("era")
            if not era_key:
                return {"error": "missing_era_key"}
            return self.manager.SelectEra(era_key)

        if command == "feature":
            feature_name = payload.get("name")
            return self.manager.Feature(feature_name, payload.get("payload"))

        if command == "launch_program":
            program = payload.get("program")
            args = payload.get("args", [])
            if program:
                self.manager.process_manager.start([program] + args)
                return {"result": "launched", "program": program}
            return {"error": "missing_program"}

        if command == "config_get":
            key = payload.get("key")
            return {"value": self.manager.Config.Get(key, None)}

        if command == "config_set":
            key = payload.get("key")
            value = payload.get("value")
            if key is None:
                return {"error": "missing_key"}
            self.manager.Config.Set(key, value)
            self.manager.Config.Save()
            self.manager.EventBus.emit(OSEvent(OSEventType.CONFIG_CHANGED, "config", {"key": key, "value": value}))
            return {"result": "saved"}

        if command == "event_emit":
            event_type = payload.get("event_type")
            if not event_type:
                return {"error": "missing_event_type"}
            try:
                event_type_enum = OSEventType(event_type)
            except ValueError:
                return {"error": "invalid_event_type", "value": event_type}
            self.manager.EventBus.emit(OSEvent(event_type_enum, payload.get("source", "user"), payload.get("payload", {})))
            return {"result": "event_emitted"}

        return {"error": "unknown_command", "command": command}


class PCARSCentral:
    def __init__(self, configPath: Path) -> None:
        self.ConfigPath = configPath
        self.Config = ConfigStore(configPath)
        self.Services = ServiceRegistry()
        self.ProcessManager = ProcessManager()
        self.UIBridge = UIBridge()
        self.EventBus = OSEventBus()
        self.Nexus = OSNexus(self.EventBus)
        self.TaskExecutor = OSTaskExecutor(self.EventBus)
        self.CommandCenter = OSCommandCenter(self)
        self.Timeline = EraTimeline(self.Services)
        self.Status = "offline"
        self.ErrorLog: List[str] = []

    def Boot(self) -> None:
        self.Config.Load()
        self.Services.Register("config", self.Config)
        self.Services.Register("process", self.ProcessManager)
        self.Services.Register("ui", self.UIBridge)
        self.Services.Register("event_bus", self.EventBus)
        self.Services.Register("nexus", self.Nexus)
        self.Services.Register("task_executor", self.TaskExecutor)
        self.Services.Register("timeline", self.Timeline)
        self.Services.Register("command_center", self.CommandCenter)
        self.Timeline.LoadEras()

        defaultEra = self.Config.Get("default_era")
        if defaultEra:
            try:
                self.Timeline.SelectEra(defaultEra)
            except KeyError:
                self.ErrorLog.append(f"Unknown default era: {defaultEra}")

        self.Status = "online"
        self.EventBus.emit(OSEvent(OSEventType.OS_STARTUP, "pcars", {"status": self.Status}))

    def BootSequence(self) -> None:
        if self.Status != "online":
            self.Boot()
        self.EventBus.emit(OSEvent(OSEventType.OS_STARTUP, "pcars", {"phase": "boot_sequence"}))

    def ShutdownSequence(self) -> None:
        self.ProcessManager.Stop()
        self.Status = "offline"
        self.EventBus.emit(OSEvent(OSEventType.OS_SHUTDOWN, "pcars", {"status": self.Status}))

    def GetStatus(self) -> Dict[str, Any]:
        return {
            "status": self.Status,
            "default_era": self.Config.Get("default_era"),
            "active_era": self.Timeline.CurrentEraInfo(),
            "event_history": len(self.EventBus.history),
            "errors": list(self.ErrorLog),
        }

    def RegisterSubsystem(self, name: str, service: object) -> None:
        self.Services.Register(name, service)

    def GetSubsystem(self, name: str) -> object | None:
        return self.Services.Get(name)

    def SelectEra(self, era_key: str) -> Dict[str, Any]:
        result = self.Timeline.SelectEra(era_key)
        self.Nexus.Set("active_era", era_key)
        self.EventBus.emit(OSEvent(OSEventType.ERA_CHANGED, "pcars", {"era": era_key}))
        return result

    def Feature(self, feature_name: str, payload: Any | None = None) -> Dict[str, Any]:
        result = self.Timeline.ExecuteCurrentFeature(feature_name, payload)
        self.EventBus.emit(OSEvent(OSEventType.FEATURE_EXECUTED, "pcars", {"feature": feature_name, "result": result}))
        return result

    def ExecuteCommand(self, command: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.CommandCenter.Execute(command, payload)
