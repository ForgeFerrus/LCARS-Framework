from __future__ import annotations
import logging
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Any, Dict, List, Optional

from lcars.core.kernel import GetKernel, SystemState, Event
from lcars.core.nexus import TaskExecutor
from lcars.core.process import Application
from lcars.core.service import Service

logger = logging.getLogger(__name__)


class OperatingSystemManager:
    """Lightweight LCARS operating system manager inside lcars.core."""

    def __init__(self, root_path: Optional[Path] = None):
        self.RootPath = root_path or Path(__file__).resolve().parents[2]
        self.Kernel = GetKernel()
        self.Bus = self.Kernel.Events
        self.Store = self.Kernel.State
        self.Services = self.Kernel.Services
        self.TaskExecutor = TaskExecutor(self.Bus)

        self.State = SystemState.OFF
        self.CommandHistory: List[str] = []
        self.StartupEvents: List[Event] = []

    def Boot(self) -> None:
        if self.State != SystemState.OFF:
            raise RuntimeError("Operating system already booted or in progress")

        self.SetState(SystemState.BOOTING)
        self.EmitEvent("os.booting", stage="boot")

        success = self.Kernel.Boot()
        if success:
            self.SetState(self.Kernel.Phase)
            self.EmitEvent("os.running", phase=self.Kernel.Phase.name)
        else:
            self.SetState(SystemState.ERROR)
            self.EmitEvent("os.error", phase=self.Kernel.Phase.name)

        logger.info("◤ LCARS OS: Boot sequence completed. State=%s", self.State.name)

    def Shutdown(self) -> None:
        if self.State in (SystemState.OFF, SystemState.SHUTTING_DOWN):
            return

        self.SetState(SystemState.SHUTTING_DOWN)
        self.EmitEvent("os.shutting_down")
        self.Kernel.Shutdown()
        self.SetState(SystemState.OFF)
        self.EmitEvent("os.off")
        logger.info("◤ LCARS OS: Shutdown complete.")

    def SetState(self, state: SystemState) -> None:
        old_state = self.State
        self.State = state
        self.EmitEvent("os.state_changed", old=old_state.name, new=state.name)

    def EmitEvent(self, event_type: str, **data: Any) -> Event:
        event = Event(Type=event_type, Source="OperatingSystemManager", Data=data)
        self.StartupEvents.append(event)
        self.Bus.Emit(event.Type, event.Source, **event.Data)
        return event

    def LaunchApplication(self, app: Application) -> int:
        pid = self.Kernel.Launch(app)
        self.EmitEvent("os.application_launched", app_id=app.AppId, pid=pid, title=app.Title)
        logger.info("◤ LCARS OS: Application launched: %s (PID %s)", app.AppId, pid)
        return pid

    def ExecuteCommand(self, command: str, cwd: Optional[Path] = None) -> None:
        if not command.strip():
            raise ValueError("Command cannot be empty")
        self.CommandHistory.append(command)
        self.EmitEvent("os.command_executed", command=command)
        self.TaskExecutor.ExecuteSystemCommand(command, str(cwd or self.RootPath))

    def Status(self) -> Dict[str, Any]:
        return {
            "state": self.State.name,
            "root_path": str(self.RootPath),
            "phase": self.Kernel.Phase.name,
            "services": self.Services.Names(),
            "commands": list(self.CommandHistory),
        }
