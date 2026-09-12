from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional

from .core import PCARSCentral


class PCARSOSystem:
    """Facade for the PCARS operating system layer."""

    def __init__(self, config_path: Path | None = None):
        self.ConfigPath = config_path or Path(__file__).resolve().parent / "config.json"
        self.Central = PCARSCentral(self.ConfigPath)
        self.IsOnline = False

    def Start(self, default_era: Optional[str] = None) -> None:
        self.Central.Boot()
        if default_era:
            self.Central.SelectEra(default_era)
        self.IsOnline = True

    def Stop(self) -> None:
        self.Central.ShutdownSequence()
        self.IsOnline = False

    def Execute(self, command: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.Central.ExecuteCommand(command, payload)

    def Status(self) -> Dict[str, Any]:
        return self.Central.GetStatus()

    def SelectEra(self, era_key: str) -> Dict[str, Any]:
        result = self.Central.SelectEra(era_key)
        if "era" in result and "key" not in result:
            result["key"] = result["era"]
        return result

    def Feature(self, feature_name: str, payload: Optional[Any] = None) -> Dict[str, Any]:
        return self.Central.Feature(feature_name, payload)

    def RegisterSubsystem(self, name: str, service: object) -> None:
        self.Central.RegisterSubsystem(name, service)

    def GetSubsystem(self, name: str) -> object | None:
        return self.Central.GetSubsystem(name)

    def EnsureDefaultConfig(self, default_era: str = "CARS_22") -> None:
        self.Central.Config.Load()
        if self.Central.Config.Get("default_era") is None:
            self.Central.Config.Set("default_era", default_era)
            self.Central.Config.Save()
