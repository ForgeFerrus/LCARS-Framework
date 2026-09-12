# ◤ LCARS SENTINEL SERVICE — GUARDIAN DAEMON
# Автономний фоновий сервіс нагляду, очищення кешу та аудиту стандартів.
# Працює автономно в ядрі без потреби ручного запуску зовнішніх скриптів.
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.core.service import Service
from lcars.service.bridge import Bridge
from lcars.engineering.telemetry import EmitTelemetry

class SentinelSubsystem(Service):
    Name = "Sentinel"

    def __init__(self, Id: str | None = None):
        super().__init__(Id=Id or "svc_sentinel")
        self.PollInterval = 1.0
        self.RunningFlag = False
        self.WorkerThread = None
        self.IgnoredDirectories = {".git", ".venv", ".idea", ".vscode", "node_modules", "archive", "data"}
        self.BannedModules = {
            "os", "sys", "json", "pathlib", "subprocess", "shutil", "typing",
            "dataclasses", "enum", "sqlite3", "yaml", "importlib", "threading",
            "requests", "math", "re", "textwrap", "traceback", "inspect", "socket", "uuid", "datetime"
        }

    def OnInit(self, KernelRef: any) -> None:
        super().OnInit(KernelRef)
        self.PurgeAllCaches()

    def OnStart(self) -> None:
        self.RunningFlag = True
        self.IsRunning = True
        Threading = Bridge().Load("System.Threading")
        if Threading and hasattr(Threading, "Thread"):
            self.WorkerThread = Threading.Thread(target=self.GuardianLoop, daemon=True)
            self.WorkerThread.start()
            EmitTelemetry("Sentinel", "SENTINEL GUARDIAN DAEMON ONLINE")

    def OnStop(self) -> None:
        self.RunningFlag = False
        self.IsRunning = False
        EmitTelemetry("Sentinel", "SENTINEL GUARDIAN DAEMON STOPPED")

    def GetProjectRoot(self) -> any:
        Path = Bridge().Load("System.Path")
        if Path:
            return Path(__file__).resolve().parents[2]
        return None

    def FindCacheDirs(self, RootNode: any) -> list:
        CacheDirs = []
        if not RootNode or not RootNode.exists() or not RootNode.is_dir():
            return CacheDirs

        Path = Bridge().Load("System.Path")
        Os = Bridge().Load("System.Os")
        if not Path or not Os:
            return CacheDirs

        for DirPath, DirNames, _ in Os.walk(str(RootNode)):
            PathSegments = Path(DirPath).parts
            if any(IgnoredItem in PathSegments for IgnoredItem in self.IgnoredDirectories):
                continue

            for ItemName in list(DirNames):
                if ItemName in ("__pycache__", ".pytest_cache", ".cache"):
                    TargetDirectory = Path(DirPath) / ItemName
                    if TargetDirectory.exists() and TargetDirectory.is_dir():
                        CacheDirs.append(TargetDirectory)
                    DirNames.remove(ItemName)

        return CacheDirs

    def PurgeCacheDir(self, TargetDir: any) -> str | None:
        if not TargetDir or not TargetDir.exists() or not TargetDir.is_dir():
            return None

        DirPathString = str(TargetDir)
        Shutil = Bridge().Load("System.Shutil")
        if Shutil and hasattr(Shutil, "rmtree"):
            Shutil.rmtree(DirPathString, ignore_errors=True)

        if TargetDir.exists():
            Subprocess = Bridge().Load("System.Subprocess")
            if Subprocess and hasattr(Subprocess, "run"):
                Subprocess.run(f'rmdir /s /q "{DirPathString}"', shell=True, capture_output=True)

        if not TargetDir.exists():
            return DirPathString

        return None

    def PurgeOrphanPyc(self, RootNode: any) -> int:
        DeletedCount = 0
        if not RootNode or not RootNode.exists() or not RootNode.is_dir():
            return 0

        Path = Bridge().Load("System.Path")
        Os = Bridge().Load("System.Os")
        if not Path or not Os:
            return 0

        for DirPath, _, FileNames in Os.walk(str(RootNode)):
            PathSegments = Path(DirPath).parts
            if any(IgnoredItem in PathSegments for IgnoredItem in self.IgnoredDirectories):
                continue

            for FileName in FileNames:
                if FileName.endswith(".pyc") or FileName.endswith(".pyo"):
                    TargetFile = Path(DirPath) / FileName
                    if TargetFile.exists() and TargetFile.is_file():
                        TargetFile.unlink()
                        if not TargetFile.exists():
                            DeletedCount += 1

        return DeletedCount

    def PurgeAllCaches(self) -> list:
        PurgedRecords = []
        Root = self.GetProjectRoot()
        if not Root:
            return PurgedRecords

        for CacheDirItem in self.FindCacheDirs(Root):
            PurgeResult = self.PurgeCacheDir(CacheDirItem)
            if PurgeResult is not None:
                PurgedRecords.append(PurgeResult)

        OrphanPycCount = self.PurgeOrphanPyc(Root)
        if OrphanPycCount > 0:
            PurgedRecords.append(f"{OrphanPycCount} pyc files")

        return PurgedRecords

    def GuardianLoop(self) -> None:
        Time = Bridge().Load("System.Time")
        CycleCounter = 0
        while self.RunningFlag:
            Purged = self.PurgeAllCaches()
            if Purged:
                for Item in Purged:
                    EmitTelemetry("Sentinel", f"AUTO PURGED: {Item}")

            CycleCounter += 1
            if CycleCounter >= 10:
                CycleCounter = 0
                self.AuditSourceFiles()

            if Time and hasattr(Time, "sleep"):
                Time.sleep(self.PollInterval)

    def AuditSourceFiles(self) -> None:
        Root = self.GetProjectRoot()
        if not Root:
            return

        LcarsDir = Root / "lcars"
        if not LcarsDir.exists():
            return

        for PyFile in LcarsDir.rglob("*.py"):
            if PyFile.name == "bridge.py":
                continue
            Content = PyFile.read_text(encoding="utf-8", errors="ignore")
            Lines = Content.splitlines()
            for LineIndex, LineText in enumerate(Lines, start=1):
                Stripped = LineText.strip()
                if Stripped.startswith("import ") or Stripped.startswith("from "):
                    for Mod in self.BannedModules:
                        if f"import {Mod}" in Stripped or f"from {Mod}" in Stripped:
                            EmitTelemetry("SentinelAudit", f"DIRECT IMPORT VIOLATION in {PyFile.name}:L{LineIndex} -> {Mod}")
                if Stripped.startswith("try:") or Stripped.startswith("except"):
                    EmitTelemetry("SentinelAudit", f"TRY EXCEPT VIOLATION in {PyFile.name}:L{LineIndex}")

class SentinelAccess(LCARS):
    SentinelInstance = None

    @classmethod
    def GetSentinel(cls) -> SentinelSubsystem:
        if cls.SentinelInstance is None:
            cls.SentinelInstance = SentinelSubsystem()
        return cls.SentinelInstance

    @classmethod
    def PurgeNow(cls) -> list:
        return cls.GetSentinel().PurgeAllCaches()

    @classmethod
    def StartDaemon(cls) -> None:
        cls.GetSentinel().OnStart()

    @classmethod
    def StopDaemon(cls) -> None:
        cls.GetSentinel().OnStop()

GetSentinel = SentinelAccess.GetSentinel
PurgeNow = SentinelAccess.PurgeNow
StartDaemon = SentinelAccess.StartDaemon
StopDaemon = SentinelAccess.StopDaemon

__all__ = [
    "SentinelSubsystem",
    "SentinelAccess",
    "GetSentinel",
    "PurgeNow",
    "StartDaemon",
    "StopDaemon",
]

