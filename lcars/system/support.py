# ◤ TITANIUM SYSTEM SUPPORT & SHIP INTEGRITY WATCHDOG // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/system/support.py
# ОПИС: Головна служба системної підтримки (System Support) та забезпечення
#       живучості ядра LCARS. Об'єднує контроль цілісності структури, автоматичний
#       ремонт конфігів (AutoFix), створення точок відновлення (Backups),
#       моніторинг пам'яті (Vital Signs) та перехоплення критичних аварій (Core Dump Hook).
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
from collections import deque

from lcars.base.type import SystemComponent, LCARS, Directive
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN, Transmission

# Операційні рівні стану системної підтримки
class SupportStatus(LCARS):
    OPTIMAL = "OPTIMAL"
    STABLE = "STABLE"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"

# Головний сервіс системної підтримки зорельота
class SystemSupport(SystemComponent):
    Instance = None

    # Оптичні сигнали шини зв'язку ODN
    VitalSignsWarning = Transmission(str, dict)
    SystemStabilized = Transmission(str)
    IntegrityBreach = Transmission(str)
    AutoFixApplied = Transmission(str)
    RecoveryCompleted = Transmission(str)
    CriticalFailure = Transmission(str)
    SupportPulse = Transmission(dict)

    def __init__(self, WorkspaceRoot: any = None):
        super().__init__()
        self.WorkspaceRoot = Directive.PathDrive(WorkspaceRoot) if WorkspaceRoot else Directive.PathDrive(__file__).resolve().parents[2]
        self.Status = SupportStatus.OPTIMAL
        self.Version = VersionInfo.GetVersion()
        self.WatchdogActive = True
        self.CrashLogPath = self.WorkspaceRoot / "logs" / "CrashDump.log"
        self.BackupStore = deque(maxlen=10)
        self.HealthLog: list[dict] = []
        self.RepairedItems: list[str] = []

        # Каталог шаблонів автофіксу
        self.FixPatterns = {
            "MissingDirectory": self.FixMissingDirectory,
            "EmptyConfiguration": self.FixEmptyConfiguration,
            "CorruptedLog": self.FixCorruptedLog,
        }
        # Активація перехоплювача аварій
        self.HookCoreDump()

    @classmethod
    def GetInstance(cls, WorkspaceRoot: any = None) -> SystemSupport:
        if cls.Instance is None:
            cls.Instance = SystemSupport(WorkspaceRoot)
        return cls.Instance

    # ─── 1. МОНІТОРИНГ ЖИТТЄВИХ ПОКАЗНИКІВ ЯДРА (VITAL SIGNS) ─────────────────
    def InspectVitalSigns(self) -> dict:
        MemoryModule = LCARS.System.Memory
        GcCount = MemoryModule.get_count() if MemoryModule and hasattr(MemoryModule, "get_count") else (0, 0, 0)
        GcObjectsCount = len(MemoryModule.get_objects()) if MemoryModule and hasattr(MemoryModule, "get_objects") else 0

        TimeModule = LCARS.System.Time
        CurrentTimestamp = TimeModule.time() if TimeModule and hasattr(TimeModule, "time") else 0.0

        VitalReport = {
            "Status": self.Status,
            "Timestamp": CurrentTimestamp,
            "MemoryObjectsCount": GcObjectsCount,
            "GarbageCollectorCycles": GcCount,
            "WatchdogActive": self.WatchdogActive,
            "RepairedItemsCount": len(self.RepairedItems),
            "Version": self.Version,
        }

        if GcObjectsCount > 500000:
            self.Status = SupportStatus.DEGRADED
            self.VitalSignsWarning.Emit("High object retention in memory core", VitalReport)
            self.PerformMemoryPurge()
        else:
            self.Status = SupportStatus.OPTIMAL

        self.HealthLog.append(VitalReport)
        if len(self.HealthLog) > 100:
            self.HealthLog.pop(0)

        self.SupportPulse.Emit(VitalReport)
        return VitalReport

    def PerformMemoryPurge(self) -> int:
        MemoryModule = LCARS.System.Memory
        Collected = MemoryModule.collect() if MemoryModule and hasattr(MemoryModule, "collect") else 0
        self.SystemStabilized.Emit(f"Memory core purged: {Collected} residual objects cleared")
        ODN.Transmit("System.Support.MemoryStabilized", ClearedCount=Collected)
        return Collected

    # ─── 2. ПЕРЕВІРКА СТРУКТУРИ ТА АВТОФІКС (HULL & STRUCTURE) ────────────────

    def VerifyStructure(self) -> bool:
        CriticalSections = ["config", "database", "logs", "plugins", "archive", "lcars/data"]
        AllIntact = True
        for Section in CriticalSections:
            TargetDir = self.WorkspaceRoot / Section
            if not TargetDir.exists():
                AllIntact = False
                TargetDir.mkdir(parents=True, exist_ok=True)
                Message = f"Reconstructed missing section: {Section}"
                self.IntegrityBreach.Emit(Message)
                self.AutoFixApplied.Emit(Message)
                self.RepairedItems.append(Section)
                ODN.Transmit("System.Support.StructureRepaired", Section=Section)
        return AllIntact

    def VerifyAndRepairConfiguration(self) -> bool:
        ConfigPath = self.WorkspaceRoot / "config" / "config.json"
        ExamplePath = self.WorkspaceRoot / "config" / "config.example.json"

        if not ConfigPath.exists():
            self.IntegrityBreach.Emit("config.json missing")
            return self.RestoreFromBackup(ExamplePath, ConfigPath)

        Content = ConfigPath.read_text(encoding="utf-8", errors="replace").strip()
        if not Content or not Content.startswith("{") or not Content.endswith("}"):
            self.IntegrityBreach.Emit("config.json corrupted")
            return self.RestoreFromBackup(ExamplePath, ConfigPath)

        return True

    def FixMissingDirectory(self, TargetPath: any) -> bool:
        PathItem = Directive.PathDrive(TargetPath)
        if PathItem:
            PathItem.mkdir(parents=True, exist_ok=True)
            self.AutoFixApplied.Emit(f"Directory recreated: {PathItem.name}")
            return True
        return False

    def FixEmptyConfiguration(self, TargetPath: any) -> bool:
        PathItem = Directive.PathDrive(TargetPath)
        if PathItem:
            PathItem.write_text("{}", encoding="utf-8")
            self.AutoFixApplied.Emit(f"Empty configuration initialized: {PathItem.name}")
            return True
        return False

    def FixCorruptedLog(self, TargetPath: any) -> bool:
        PathItem = Directive.PathDrive(TargetPath)
        if PathItem and PathItem.exists():
            PathItem.write_text("", encoding="utf-8")
            self.AutoFixApplied.Emit(f"Log sanitized: {PathItem.name}")
            return True
        return False

    def PurgeAnomalies(self) -> int:
        TargetDirectories = [
            self.WorkspaceRoot / "database",
            self.WorkspaceRoot / "lcars" / "data",
        ]
        PurgedCount = 0
        for TargetDir in TargetDirectories:
            if not TargetDir.exists():
                continue
            for FileItem in TargetDir.glob("*"):
                FileName = FileItem.name
                if FileName.endswith(".db-journal") or FileName.endswith(".tmp") or FileName.endswith(".phantom"):
                    FileItem.unlink(missing_ok=True)
                    PurgedCount += 1
                    ODN.Transmit("System.Support.AnomalyPurged", File=FileName)
        return PurgedCount

    # ─── 3. СИСТЕМА ТОЧОК ВІДНОВЛЕННЯ (BACKUP & RESTORE) ───────────────────────

    def CreateBackup(self) -> dict:
        TimeModule = LCARS.System.Time
        CurrentTimestamp = TimeModule.time() if TimeModule and hasattr(TimeModule, "time") else 0.0
        BackupRecord = {
            "Timestamp": CurrentTimestamp,
            "Workspace": str(self.WorkspaceRoot),
            "Status": self.Status,
            "RepairedItems": list(self.RepairedItems),
        }
        self.BackupStore.append(BackupRecord)
        return BackupRecord

    def RestoreBackup(self, Index: int = -1) -> bool:
        if not self.BackupStore:
            return False
        SelectedRecord = self.BackupStore[Index]
        self.Status = SelectedRecord.get("Status", SupportStatus.OPTIMAL)
        self.RecoveryCompleted.Emit(f"Restored to checkpoint {Index}")
        ODN.Transmit("System.Support.BackupRestored", Index=Index)
        return True

    def RestoreFromBackup(self, SourcePath: any, DestinationPath: any) -> bool:
        Src = Directive.PathDrive(SourcePath)
        Dst = Directive.PathDrive(DestinationPath)
        if not Src.exists():
            ErrorMessage = f"Backup source {Src} not found"
            self.CriticalFailure.Emit(ErrorMessage)
            ODN.Transmit("System.Support.BackupFailed", Source=str(Src))
            return False
        Dst.parent.mkdir(parents=True, exist_ok=True)
        Content = Src.read_text(encoding="utf-8", errors="replace")
        Dst.write_text(Content, encoding="utf-8")
        self.RecoveryCompleted.Emit(f"Restored {Dst.name} from backup")
        ODN.Transmit("System.Support.FileRestored", Destination=str(Dst))
        return True

    def GetBackupList(self) -> list[dict]:
        return list(self.BackupStore)

    # ─── 4. ПЕРЕХОПЛЕННЯ АВАРІЙ ТА ЗАХИСТ ЯДРА (CORE DUMP HOOK) ────────────────

    def HookCoreDump(self) -> None:
        Sys = LCARS.System.Core

        def SystemExceptionHandler(ExcType: any, ExcValue: any, ExcTraceback: any):
            TracebackModule = LCARS.System.Traceback
            ErrorLines = TracebackModule.format_exception(ExcType, ExcValue, ExcTraceback) if TracebackModule else [str(ExcValue)]
            ErrorMessage = "".join(ErrorLines)

            self.CrashLogPath.parent.mkdir(parents=True, exist_ok=True)
            Time = LCARS.System.Time
            Timestamp = Time.strftime("%Y-%m-%d %H:%M:%S") if Time else "0000-00-00"
            DumpRecord = f"\n--- CORE DUMP INTERCEPT [{Timestamp}] ---\n{ErrorMessage}\n"

            with open(str(self.CrashLogPath), "a", encoding="utf-8") as LogFile:
                LogFile.write(DumpRecord)

            self.CriticalFailure.Emit(f"Core dump intercepted: {ExcType.__name__}")
            ODN.Transmit("System.Support.CoreDumpIntercepted", Error=str(ExcValue))

        if Sys and hasattr(Sys, "excepthook"):
            Sys.excepthook = SystemExceptionHandler

    # ─── 5. ПОВНИЙ ЗВІТ СИСТЕМНОЇ ПІДТРИМКИ ───────────────────────────────────

    def GetStatus(self) -> dict:
        return {
            "SupportStatus": self.Status,
            "WatchdogActive": self.WatchdogActive,
            "HealthReportsCount": len(self.HealthLog),
            "RepairedItemsCount": len(self.RepairedItems),
            "BackupsAvailable": len(self.BackupStore),
            "Version": self.Version,
        }

# Експорт сервісу підтримки
Support = SystemSupport.GetInstance
SUPPORT = SystemSupport.GetInstance()
