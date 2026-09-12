# ◤ TITANIUM SYSTEM PASSPORT & SPECIFICATION 🖖
# =============================================================================
# ФАЙЛ: lcars/base/info.py
# ОПИС: Єдиний канонічний паспорт та специфікація системи LCARS Framework.
#       Містить глобальну версію, метадані та делегує обчислення часу хронометру.
# СТАНДАРТ: Titanium (Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================
from __future__ import annotations
import sys
from typing import Any, Dict

# Офіційна глобальна версія проекту (встановлюється розробником)
class Version:
    Release = "0.3.0-alpha"
    Status = "Operational"
    Build = "2026.08.28"
    Title = "LCARS Framework"
    System = "Library Computer Access/Retrieval System"
    Specification = "Starfleet Cybernetics Division Directive 24.5"
    Architecture = "Titanium Master Architecture"
    Design = "Michael Okuda 24th Century Canonical Vector Design"
    Platform = "Quantum Core / Optical Transport Network (OTN)"

    @classmethod
    # Делегуємо отримання астрономічного часу спеціалізованому системному хронометру
    def GetStardate(cls) -> str:
        from lcars.service.chronometer import StardateCalculator
        return str(StardateCalculator.Stardate())

    @classmethod
    def GetEarthDate(cls) -> str:
        from lcars.service.chronometer import StardateCalculator
        return StardateCalculator.EarthDate()

    @classmethod
    def GetVersion(cls) -> str:
        return cls.Release

    @classmethod
    def GetMetadata(cls) -> Dict[str, Any]:
        return cls.Passport()

    # Повний паспорт системи
    @classmethod
    def Passport(cls) -> Dict[str, Any]:
        return {
            "title": cls.Title,
            "release": cls.Release,
            "version": cls.Release,
            "build": cls.Build,
            "status": cls.Status,
            "stardate": cls.GetStardate(),
            "earth_date": cls.GetEarthDate(),
            "system": cls.System,
            "specification": cls.Specification,
            "architecture": cls.Architecture,
            "design": cls.Design,
            "platform": cls.Platform,
            "runtime": f"Python {sys.version.split()[0]} on {sys.platform}",
        }

    def __str__(self):
        return f"{self.Title} v{self.Release} [Stardate {self.GetStardate()}]"

# Канонічні аліаси для зворотної сумісності
Passport = Version
VersionInfo = Version
SystemInfo = Version
getVersion = Version.GetVersion
getMetadata = Version.GetMetadata
__all__ = [
    "Version",
    "Passport",
    "VersionInfo",
    "SystemInfo",
    "getVersion",
    "getMetadata",
]
