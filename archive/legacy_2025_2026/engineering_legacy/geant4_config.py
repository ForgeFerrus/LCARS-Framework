# LCARS GEANT4 CONFIGURATION
# ПРИЗНАЧЕННЯ: Конфігурація шляхів та інтеграція з Geant4
# СТАНДАРТ: Titanium Master

from __future__ import annotations
# Titanium Bridge Migration: from typing import Any


class Geant4Config:
    # Конфігурація Geant4 для LCARS
    # Шляхи до встановленого Geant4 та датасетів

    def __init__(self):
        # Основні шляхи до встановленого Geant4
        self.InstallPath = "C:/Users/Forge/MyProject/Geant4/program_files"
        self.BinPath = "C:/Users/Forge/MyProject/Geant4/program_files/bin"
        self.LibPath = "C:/Users/Forge/MyProject/Geant4/program_files/lib"
        self.IncludePath = "C:/Users/Forge/MyProject/Geant4/program_files/include/Geant4"
        self.DataPath = "C:/Users/Forge/MyProject/Geant4/program_files/share/Geant4/data"
        self.ExamplesPath = "C:/Users/Forge/MyProject/Geant4/program_files/share/Geant4/examples"

        # Датасети Geant4
        self.Datasets = {
            "G4NDL": "4.7.1",
            "G4EMLOW": "8.6.1",
            "PhotonEvaporation": "6.1",
            "RadioactiveDecay": "6.1.2",
            "G4PARTICLEXS": "4.1",
            "G4PII": "1.3",
            "RealSurface": "2.2",
            "G4SAIDDATA": "2.0",
            "G4ABLA": "3.3",
            "G4INCL": "1.2",
            "G4ENSDFSTATE": "3.0",
            "G4CHANNELING": "1.0",
        }

        # Налаштування збірки
        self.Compiler = "MSVC 19.44"
        self.CMakeFlags = [
            "-DGEANT4_INSTALL_DATA=OFF",
            "-DGEANT4_USE_GDML=ON",
            "-DGEANT4_USE_OPENGL_X11=OFF",
        ]

    def GetDatasetPath(self, Name: str) -> str | None:
        # Отримання шляху до датасету
        if Name in self.Datasets:
            return f"{self.DataPath}/{Name}/{self.Datasets[Name]}"
        return None

    def ValidateInstallation(self) -> dict[str, Any]:
        # Перевірка встановлення Geant4
        return {
            "InstallPath": self.InstallPath,
            "DataPath": self.DataPath,
            "BuildPath": self.BuildPath,
            "DatasetsMissing": list(self.Datasets.keys()),  # Треба перевірити наявність
        }


# Синглтон конфігурації
Config = Geant4Config()


__all__ = ["Geant4Config", "Config"] 
