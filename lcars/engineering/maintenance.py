# LCARS engineering maintenance layer.
# Тут живе тільки обслуговування інженерного відсіку:
# - логи
# - структура робочого простору
# - резервні копії інженерних даних
# - відновлення інженерного стану
# - базові аварійні прапори для інженерії
# Системний emergency-режим, підтримка, оновлення й загальна діагностика
# залишаються в `lcars.system.emergency`.

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

from lcars.base.type import SystemComponent
from lcars.base.version import getVersion
from lcars.core.signal import Transmission
from lcars.core.matrix import SystemMatrix
from lcars.base.type import LCARS
from lcars.core.service import Service
from lcars.engineering.telemetry import emit_telemetry
from lcars.modules.storage import ListChipFiles

__version__ = getVersion()


class LogMaintenance:
    # Обрізка дуже великих логів, щоб інженерний відсік не забивався сміттям.
    MaxLogSize = 5 * 1024 * 1024

    def rotateLogs(self, WorkRoot: Path) -> dict[str, Any]:
        LogDir = WorkRoot / "logs"
        FreedBytes = 0

        if LogDir.exists():
            for LogFile in LogDir.glob("*.log"):
                if LogFile.is_file():
                    Size = LogFile.stat().st_size
                    if Size > self.MaxLogSize:
                        FreedBytes += Size
                        LogFile.write_text("")

        return {"Task": "LogRotation", "FreedBytes": FreedBytes}


class StructureMaintenance:
    # Перевірка базових папок інженерного середовища.
    RequiredFolders = ["logs", "database", "config", "archive", "plugins"]

    def verify(self, WorkRoot: Path) -> tuple[bool, list[str]]:
        MissingFolders: list[str] = []
        for Folder in self.RequiredFolders:
            FolderPath = WorkRoot / Folder
            if not FolderPath.exists():
                MissingFolders.append(Folder)
                FolderPath.mkdir(parents=True, exist_ok=True)
        return (len(MissingFolders) == 0, MissingFolders)


class DatabaseMaintenance:
    # Допоміжні операції для бази даних і chip-файлів.
    def defragment(self, DBManager: Any | None) -> int:
        Count = 0
        if DBManager and hasattr(DBManager, "Chips"):
            for _ChipId in getattr(DBManager, "Chips", {}):
                Count += 1
        return Count

    def backupChipFiles(self, WorkRoot: Path) -> int:
        ArchiveDir = WorkRoot / "archive" / "auto_backups"
        ArchiveDir.mkdir(parents=True, exist_ok=True)

        Count = 0
        for DBFile in ListChipFiles():
            if DBFile.exists() and DBFile.is_file():
                BackupPath = ArchiveDir / f"{DBFile.stem}.db.backup"
                BackupPath.write_bytes(DBFile.read_bytes())
                Count += 1
        return Count


class RecoveryMaintenance:
    # Загальний стан відновлення та аварійного режиму інженерного шару.
    def __init__(self) -> None:
        self.BackupStore = deque(maxlen=10)
        self.EmergencyState: dict[str, Any] = {
            "active": False,
            "level": 0,
            "affected_systems": [],
        }
        self.IsEmergency = False

    def createBackup(self, WorkRoot: Path) -> dict[str, Any]:
        State = {
            "workspace": str(WorkRoot),
            "emergency": self.EmergencyState.copy(),
            "timestamp": 0,
        }
        self.BackupStore.append(State)
        return State

    def restoreBackup(self, Index: int = -1) -> bool:
        if not self.BackupStore:
            return False
        if Index < -len(self.BackupStore) or Index >= len(self.BackupStore):
            return False

        State = self.BackupStore[Index]
        self.EmergencyState = State.get(
            "emergency",
            {"active": False, "level": 0, "affected_systems": []},
        )
        self.IsEmergency = bool(self.EmergencyState.get("active", False))
        return True

    def getBackupList(self) -> list[dict[str, Any]]:
        return list(self.BackupStore)

    def triggerEmergency(self, Level: int, Systems: list[str]) -> None:
        self.IsEmergency = True
        self.EmergencyState["active"] = True
        self.EmergencyState["level"] = Level
        self.EmergencyState["affected_systems"] = list(Systems)

    def clearEmergency(self) -> None:
        self.IsEmergency = False
        self.EmergencyState["active"] = False
        self.EmergencyState["level"] = 0
        self.EmergencyState["affected_systems"] = []

    def getEmergencyStatus(self) -> dict[str, Any]:
        return {
            "IsEmergency": self.IsEmergency,
            "EmergencyState": self.EmergencyState,
            "BackupCount": len(self.BackupStore),
        }


class StructuralIntegrity(Service):
    # Стан корпуса і пошкодження в межах інженерної підтримки.
    # Цей вузол живе тут, бо він залежить від обслуговування, ремонту і аварійного сигналу.
    def __init__(self):
        super().__init__(Id="structural")
        self.Name = "structural"
        self.HullMatrix = SystemMatrix([10, 5, 20], Id="ShipHull")
        self.InitializeHull()

    def InitializeHull(self):
        for X in range(10):
            for Y in range(5):
                for Z in range(20):
                    self.HullMatrix.SetData(X, Y, Z, 100.0)

    def OnStart(self) -> None:
        pass

    def OnStop(self) -> None:
        pass

    def ApplyDamage(self, X: int, Y: int, Z: int, Amount: float):
        Current = self.HullMatrix.GetData(X, Y, Z, default=100.0)
        NewIntegrity = max(0.0, Current - Amount)
        self.HullMatrix.SetData(X, Y, Z, NewIntegrity)

        if NewIntegrity < 20.0:
            LCARS.ODN.send("Alert.SetLevel", Level="RED")
            LCARS.ODN.send("System.Broadcast", Message=f"CRITICAL HULL BREACH AT SECTOR {X}-{Y}-{Z}")

    def Repair(self, X: int, Y: int, Z: int, Amount: float):
        Current = self.HullMatrix.GetData(X, Y, Z, default=0.0)
        NewIntegrity = min(100.0, Current + Amount)
        self.HullMatrix.SetData(X, Y, Z, NewIntegrity)

    def GetStatus(self):
        return {
            "name": self.Name,
            "status": "online",
            "hullIntegrity": self.HullMatrix.GetData(0, 0, 0, default=100.0),
            "matrix": self.HullMatrix,
        }


class MaintenanceProtocol(SystemComponent, RecoveryMaintenance):
    # Головний інженерний контролер maintenance.
    MaintenanceStarted = Transmission(str)
    MaintenanceCompleted = Transmission(str)
    OptimizationReport = Transmission(dict)
    EmergencyAlert = Transmission(str)
    AutoFixApplied = Transmission(str)
    RecoveryComplete = Transmission(str)
    VitalSignsWarning = Transmission(str)
    EnvironmentStabilized = Transmission()
    CheckCompleted = Transmission(int)

    def __init__(self, WorkDir: str | None = None):
        SystemComponent.__init__(self)
        RecoveryMaintenance.__init__(self)

        self.WorkRoot = Path(WorkDir) if WorkDir else Path(__file__).resolve().parents[2]

        self.StructureHelper = StructureMaintenance()
        self.LogHelper = LogMaintenance()
        self.DatabaseHelper = DatabaseMaintenance()

        # Набір простих виправлень без зайвих обгорток.
        self.FixPatterns = {
            "missing_dir": self.fixMissingDir,
            "empty_config": self.fixEmptyConfig,
            "corrupted_log": self.fixCorruptedLog,
            "missing_file": self.fixMissingFile,
        }

        self.LastScanData: dict[str, Any] = {}

    # Рівень 1: чистка та ротація логів.
    def runLevel1(self) -> dict[str, Any]:
        self.MaintenanceStarted.Emit("Level 1")
        Result = self.LogHelper.rotateLogs(self.WorkRoot)
        self.OptimizationReport.Emit(Result)
        self.MaintenanceCompleted.Emit("Level 1")
        return Result

    # Рівень 2: технічне обслуговування бази та chip-даних.
    def runLevel2(self, DBManager: Any | None = None) -> dict[str, Any]:
        self.MaintenanceStarted.Emit("Level 2")
        Processed = self.DatabaseHelper.defragment(DBManager)
        Result = {"Task": "Defragmentation", "ChipsProcessed": Processed}
        self.OptimizationReport.Emit(Result)
        self.MaintenanceCompleted.Emit("Level 2")
        return Result

    # Рівень 3: перевірка інженерної структури робочого простору.
    def runLevel3(self) -> dict[str, Any]:
        self.MaintenanceStarted.Emit("Level 3")
        AllValid, MissingCritical = self.StructureHelper.verify(self.WorkRoot)
        Result = {
            "Task": "StructureVerify",
            "Reconstructed": MissingCritical,
            "Status": "NOMINAL" if AllValid else "RECONSTRUCTED",
        }
        self.OptimizationReport.Emit(Result)
        self.MaintenanceCompleted.Emit("Level 3")
        return Result

    # Рівень 4: резервне копіювання інженерних даних.
    def backupCoreSystems(self) -> dict[str, Any]:
        self.MaintenanceStarted.Emit("Level 4")
        Count = self.DatabaseHelper.backupChipFiles(self.WorkRoot)
        Result = {"Task": "Backup", "FilesCopied": Count}
        self.OptimizationReport.Emit(Result)
        self.MaintenanceCompleted.Emit("Level 4")
        return Result

    # Просте виправлення за відомим типом проблеми.
    def autofix(self, Issue: str, Context: dict | None = None) -> bool:
        Context = Context or {}
        Fixer = self.FixPatterns.get(Issue)
        if not Fixer:
            return False

        Result = Fixer(Context)
        if Result:
            self.AutoFixApplied.Emit(f"Fixed: {Issue}")
            emit_telemetry("Maintenance", f"AutoFix applied: {Issue}")
        return Result

    # Створює відсутню директорію.
    def fixMissingDir(self, Context: dict) -> bool:
        Target = Context.get("path")
        if Target:
            Path(Target).mkdir(parents=True, exist_ok=True)
            return True
        return False

    # Відновлює порожній конфіг до базового стану.
    def fixEmptyConfig(self, Context: dict) -> bool:
        Target = Context.get("path")
        if Target:
            Path(Target).write_text("{}")
            return True
        return False

    # Очищає зіпсований лог-файл.
    def fixCorruptedLog(self, Context: dict) -> bool:
        Target = Context.get("path")
        if Target:
            Path(Target).write_text("")
            return True
        return False

    # Створює відсутній файл із переданим вмістом.
    def fixMissingFile(self, Context: dict) -> bool:
        Target = Context.get("path")
        Content = Context.get("content", "")
        if Target:
            Path(Target).write_text(str(Content))
            return True
        return False

    # Швидка перевірка структури.
    def verifyStructure(self) -> bool:
        AllValid, _MissingCritical = self.StructureHelper.verify(self.WorkRoot)
        self.CheckCompleted.Emit(0 if AllValid else 1)
        return AllValid

    # Поточний стан інженерного maintenance.
    def getStatus(self) -> dict[str, Any]:
        AllValid, MissingCritical = self.StructureHelper.verify(self.WorkRoot)
        return {
            "StructureValid": AllValid,
            "MissingCritical": MissingCritical,
            "IsEmergency": self.IsEmergency,
            "EmergencyState": self.EmergencyState,
            "BackupCount": len(self.BackupStore),
            "Workspace": str(self.WorkRoot),
        }

    # Зберігає аварійний знімок інженерного стану.
    def createBackup(self) -> dict[str, Any]:
        return super().createBackup(self.WorkRoot)

    # Відкат до попереднього знімка.
    def restoreBackup(self, Index: int = -1) -> bool:
        Result = super().restoreBackup(Index)
        if Result:
            self.RecoveryComplete.Emit(f"Restored to state {Index}")
            emit_telemetry("Maintenance", f"Recovery complete: backup {Index}")
        return Result

    # Вмикає інженерний аварійний прапор.
    def triggerEmergency(self, Level: int, Systems: list[str]) -> None:
        super().triggerEmergency(Level, Systems)
        self.EmergencyAlert.Emit(f"EMERGENCY LEVEL {Level}")
        emit_telemetry("Maintenance", f"Emergency triggered: Level {Level}, Systems: {Systems}")

    # Скидає інженерний аварійний прапор.
    def clearEmergency(self) -> None:
        super().clearEmergency()
        emit_telemetry("Maintenance", "Emergency cleared")


# Тут лишається тільки інженерний протокол обслуговування.
# Системне аварійне відновлення, підтримка й життєзабезпечення живуть окремо у `lcars.system.emergency`.
LifeSupportSystem = MaintenanceProtocol
