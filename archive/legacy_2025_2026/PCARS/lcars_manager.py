# Central LCARS manager for PCARS.

from pathlib import Path
from typing import Any, Optional

from .core import PCARSCentral


class LcarsManager:
    def __init__(self, configPath: Path) -> None:
        self.Core = PCARSCentral(configPath)

    def Boot(self) -> None:
        self.Core.Boot()

    def Shutdown(self) -> None:
        self.Core.ShutdownSequence()

    def GetStatus(self) -> dict[str, Any]:
        return self.Core.GetStatus()

    def RegisterSubsystem(self, name: str, service: object) -> None:
        self.Core.RegisterSubsystem(name, service)

    def GetSubsystem(self, name: str) -> Optional[object]:
        return self.Core.GetSubsystem(name)

    def SelectEra(self, eraKey: str) -> dict[str, Any]:
        return self.Core.SelectEra(eraKey)

    def Feature(self, featureName: str, payload: Any | None = None) -> dict[str, Any]:
        return self.Core.Feature(featureName, payload)

    def ExecuteCommand(self, command: str, payload: Any | None = None) -> dict[str, Any]:
        return self.Core.ExecuteCommand(command, payload)
