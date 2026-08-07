from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from lcars.base.type import LCARS
from lcars.core.kernel import CreateApplication, ExistingApplication, Kernel, SystemState

# Аварійний рівень системи.
# Тут немає візуальної логіки. Файл тільки:
# - бере активний застосунок;
# - тримає низинні аварійні операції;
# - дає стартувати ручний або автоматичний аварійний режим.

_MaintenanceNode = None
_OpticalNode = None


def GetApplication():
    App = ExistingApplication()
    if App is None:
        App = CreateApplication(sys.argv)
    return App


def LoadEmergencyScreen(Context=None):
    from lcars.ui.screen.emergency import EmergencyMode

    return EmergencyMode(Context=Context)


def GetKernel():
    return Kernel()


def GetMasterSystem():
    from lcars.core.system import ActiveSystem
    return ActiveSystem()


def GetBoardComputer():
    from lcars.service.onboard import Computer
    return Computer()


def GetMaintenanceSystem():
    global _MaintenanceNode
    if _MaintenanceNode is not None:
        return _MaintenanceNode
    from lcars.engineering.maintenance import MaintenanceProtocol
    _MaintenanceNode = MaintenanceProtocol(str(ProjectRoot))
    return _MaintenanceNode


def GetOpticalNetwork():
    global _OpticalNode
    if _OpticalNode is not None:
        return _OpticalNode
    from lcars.engineering.optical import InitializeOpticalNetwork

    _OpticalNode = InitializeOpticalNetwork()
    if hasattr(LCARS, "Set"):
        LCARS.Set("Optical", _OpticalNode)
    return _OpticalNode


def GetServiceHealth():
    KernelNode = GetKernel()
    Services = getattr(KernelNode, "Services", None)
    if Services is None or not hasattr(Services, "HealthCheck"):
        return {}
    Health = Services.HealthCheck()
    return Health if isinstance(Health, dict) else {}


def GetProcessSnapshot():
    KernelNode = GetKernel()
    Status = KernelNode.Status() if hasattr(KernelNode, "Status") else {}
    Processes = Status.get("Processes", []) if isinstance(Status, dict) else []
    return Processes if isinstance(Processes, list) else []


def GetModuleSnapshot():
    KernelNode = GetKernel()
    if hasattr(KernelNode, "ModuleNames"):
        Names = KernelNode.ModuleNames()
        return Names if isinstance(Names, list) else []
    return []


def GetAIStatus():
    BoardComputer = GetBoardComputer()
    if BoardComputer is None or not hasattr(BoardComputer, "getAI"):
        return {}

    AI = BoardComputer.getAI()
    if AI is None or not hasattr(AI, "getStatus"):
        return {}

    Status = AI.getStatus()
    return Status if isinstance(Status, dict) else {}


def GetBoardSummary():
    BoardComputer = GetBoardComputer()
    if BoardComputer is None or not hasattr(BoardComputer, "SystemSummary"):
        return {}
    Summary = BoardComputer.SystemSummary()
    return Summary if isinstance(Summary, dict) else {}


def GetCoreDiagnostics():
    BoardComputer = GetBoardComputer()
    if BoardComputer is None or not hasattr(BoardComputer, "GetCoreDiagnostics"):
        return {}
    Diagnostics = BoardComputer.GetCoreDiagnostics()
    return Diagnostics if isinstance(Diagnostics, dict) else {}


def GetMaintenanceStatus():
    Maintenance = GetMaintenanceSystem()
    if Maintenance is None:
        return {}

    if hasattr(Maintenance, "getStatus"):
        Status = Maintenance.getStatus()
        return Status if isinstance(Status, dict) else {}

    if hasattr(Maintenance, "GetStatus"):
        Status = Maintenance.GetStatus()
        return Status if isinstance(Status, dict) else {}

    if hasattr(Maintenance, "getEmergencyStatus"):
        Status = Maintenance.getEmergencyStatus()
        return Status if isinstance(Status, dict) else {}

    return {}


def GetOpticalStatus():
    Optical = GetOpticalNetwork()
    if Optical is None:
        return {}

    if hasattr(Optical, "GetStatus"):
        Status = Optical.GetStatus()
        return Status if isinstance(Status, dict) else {}

    return {}


def BuildEmergencySnapshot(Context=None):
    KernelNode = GetKernel()
    Master = GetMasterSystem()
    Snapshot = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "context": Context or {},
        "kernel": KernelNode.Status() if hasattr(KernelNode, "Status") else {},
        "services": GetServiceHealth(),
        "processes": GetProcessSnapshot(),
        "modules": GetModuleSnapshot(),
        "board": GetBoardSummary(),
        "maintenance": GetMaintenanceStatus(),
        "optical": GetOpticalStatus(),
        "ai": GetAIStatus(),
        "diagnostics": GetCoreDiagnostics(),
    }
    if Master is not None and hasattr(Master, "DiagnosticsReport"):
        Snapshot["master"] = Master.DiagnosticsReport()
    return Snapshot


def EmitEmergencyLine(Sink, Text):
    Line = str(Text)
    if Sink is None:
        return
    if callable(Sink):
        Sink(Line)
        return
    if hasattr(Sink, "append"):
        Sink.append(Line)
        return
    if hasattr(Sink, "setText"):
        Current = ""
        if hasattr(Sink, "text"):
            Current = str(Sink.text())
        if Current:
            Sink.setText(Current + "\n" + Line)
        else:
            Sink.setText(Line)
        return
    if hasattr(Sink, "setPlainText"):
        Current = ""
        if hasattr(Sink, "toPlainText"):
            Current = str(Sink.toPlainText())
        if Current:
            Sink.setPlainText(Current + "\n" + Line)
        else:
            Sink.setPlainText(Line)


def EmitEmergencyBlock(Sink, Title, Payload):
    EmitEmergencyLine(Sink, "")
    EmitEmergencyLine(Sink, "[" + str(Title) + "]")
    if isinstance(Payload, dict):
        for Key, Value in Payload.items():
            EmitEmergencyLine(Sink, "  " + str(Key).upper() + ": " + str(Value))
        return
    if isinstance(Payload, list):
        for Item in Payload:
            EmitEmergencyLine(Sink, "  " + str(Item))
        return
    for Line in str(Payload).splitlines():
        EmitEmergencyLine(Sink, "  " + Line)


def GetBackupManager():
    KernelNode = GetKernel()
    Services = getattr(KernelNode, "Services", None)
    if Services is None or not hasattr(Services, "Get"):
        return None

    PluginService = Services.Get("plugin")
    if PluginService is None:
        return None

    Backup = getattr(PluginService, "Backup", None)
    if Backup is not None:
        return Backup

    Manager = getattr(PluginService, "Manager", None)
    if Manager is not None and hasattr(PluginService, "RegisterBackup"):
        return Manager

    return None


def GetBackupCatalog():
    BackupManager = GetBackupManager()
    if BackupManager is None or not hasattr(BackupManager, "ListBackups"):
        return []
    Catalog = BackupManager.ListBackups()
    return Catalog if isinstance(Catalog, list) else []


def RunServiceRepair():
    KernelNode = GetKernel()
    Services = getattr(KernelNode, "Services", None)
    Result = {
        "repaired": [],
        "skipped": [],
        "health": {},
    }
    if Services is None or not hasattr(Services, "HealthCheck"):
        return Result

    Health = Services.HealthCheck()
    Result["health"] = Health if isinstance(Health, dict) else {}
    if not isinstance(Health, dict):
        return Result

    for Name, Healthy in Health.items():
        if Healthy:
            Result["skipped"].append(Name)
            continue
        ServiceNode = Services.Get(Name) if hasattr(Services, "Get") else None
        if ServiceNode is None:
            continue
        if hasattr(ServiceNode, "Init") and hasattr(KernelNode, "Boot"):
            ServiceNode.Init(KernelNode)
        if hasattr(ServiceNode, "Start"):
            ServiceNode.Start()
            Result["repaired"].append(Name)

    return Result


def RunProcessAudit():
    Processes = GetProcessSnapshot()
    Audit = []
    for Item in Processes:
        if isinstance(Item, dict):
            Audit.append(
                {
                    "Pid": Item.get("Pid", "?"),
                    "App": Item.get("App", "?"),
                    "Title": Item.get("Title", "?"),
                }
            )
    return Audit


def RunModuleAudit():
    return GetModuleSnapshot()


def RunLifeSupportCheck():
    Board = GetBoardSummary()
    Core = GetCoreDiagnostics()
    Services = GetServiceHealth()
    Maintenance = GetMaintenanceStatus()
    Optical = GetOpticalStatus()
    Status = "NOMINAL"
    Issues: List[str] = []

    if isinstance(Core, dict):
        Alerts = Core.get("alerts", {})
        if isinstance(Alerts, dict) and str(Alerts.get("state", "UNKNOWN")) not in ("NORMAL", "GREEN"):
            Issues.append("ALERT_STATE_NON_NORMAL")
            Status = "WARNING"

    if isinstance(Services, dict):
        for Name, Healthy in Services.items():
            if not Healthy:
                Issues.append("SERVICE_" + str(Name).upper())
                Status = "CRITICAL" if len(Issues) > 1 else "WARNING"

    if isinstance(Maintenance, dict) and Maintenance:
        if not bool(Maintenance.get("StructureValid", True)):
            Issues.append("MAINTENANCE_STRUCTURE")
            Status = "WARNING" if Status == "NOMINAL" else Status
        if bool(Maintenance.get("IsEmergency", False)):
            Issues.append("MAINTENANCE_EMERGENCY")
            Status = "CRITICAL"

    if isinstance(Optical, dict) and Optical:
        if str(Optical.get("NetworkState", "OFFLINE")).upper() != "ONLINE" and int(Optical.get("NodeCount", 0)) > 0:
            Issues.append("OPTICAL_LINK_DEGRADED")
            Status = "WARNING" if Status == "NOMINAL" else Status

    if isinstance(Board, dict) and Board:
        if str(Board.get("alert", "")).upper().find("CONDITION") >= 0:
            pass

    return {
        "status": Status,
        "issues": Issues,
        "board": Board,
        "core": Core,
        "services": Services,
        "maintenance": Maintenance,
        "optical": Optical,
        "ai": GetAIStatus(),
    }


def RunEmergencyDiagnostics():
    Snapshot = BuildEmergencySnapshot()
    Snapshot["life_support"] = RunLifeSupportCheck()
    Snapshot["service_repair"] = RunServiceRepair()
    Snapshot["maintenance"] = GetMaintenanceStatus()
    Snapshot["optical"] = GetOpticalStatus()
    Snapshot["backups"] = GetBackupCatalog()
    return Snapshot


def RunSystemSupport():
    return {
        "diagnostics": RunEmergencyDiagnostics(),
        "life_support": RunLifeSupportCheck(),
        "service_repair": RunServiceRepair(),
        "maintenance": GetMaintenanceStatus(),
        "optical": GetOpticalStatus(),
        "backups": GetBackupCatalog(),
    }


def RunSystemUpdate():
    KernelNode = GetKernel()
    Status = KernelNode.Status() if hasattr(KernelNode, "Status") else {}
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "kernel": Status,
        "services": GetServiceHealth(),
        "modules": GetModuleSnapshot(),
        "processes": GetProcessSnapshot(),
        "board": GetBoardSummary(),
        "ai": GetAIStatus(),
    }


def RunEmergencyBackup(Source=None, Name=None, ToDatabase=True):
    BackupManager = GetBackupManager()
    SourcePath = Path(Source) if Source is not None else Path(ProjectRoot)
    BackupName = Name or ("emergency_" + datetime.now().strftime("%Y%m%d_%H%M%S"))

    if BackupManager is not None and hasattr(BackupManager, "CreateBackup") and SourcePath.exists():
        Result = BackupManager.CreateBackup(str(SourcePath), BackupName, toDb=bool(ToDatabase))
        if isinstance(Result, dict):
            return Result

    BackupRoot = ProjectRoot / "data" / "emergency_backups"
    BackupRoot.mkdir(parents=True, exist_ok=True)
    TargetPath = BackupRoot / (BackupName + ".json")
    TargetPath.write_text(
        json.dumps(BuildEmergencySnapshot({"source": str(SourcePath)}), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return {
        "name": BackupName,
        "path": str(TargetPath),
        "db": False,
        "mode": "snapshot",
    }


def RestoreEmergencyBackup(BackupName, Destination, FromDb=False):
    BackupManager = GetBackupManager()
    if BackupManager is None or not hasattr(BackupManager, "Restore"):
        return None
    if not BackupName or not Destination:
        return None

    if not FromDb:
        SourcePath = Path(ProjectRoot) / str(BackupName)
        if not SourcePath.exists():
            return None

    Result = BackupManager.Restore(str(BackupName), str(Destination), fromDb=bool(FromDb))
    return Result


def RunEmergencyRecovery(Snapshot=None, Destination=None, FromDb=False):
    if isinstance(Snapshot, dict):
        return Snapshot

    if Snapshot is not None:
        SnapshotPath = Path(Snapshot)
        if SnapshotPath.exists():
            Data = SnapshotPath.read_text(encoding="utf-8")
            return json.loads(Data)

    if Snapshot and Destination:
        Restored = RestoreEmergencyBackup(Snapshot, Destination, FromDb=FromDb)
        if Restored is not None:
            return {
                "restored": Restored,
                "backups": GetBackupCatalog(),
            }

    return {
        "plan": "manual-recovery",
        "snapshot": BuildEmergencySnapshot(),
        "backups": GetBackupCatalog(),
    }


def RunEmergencyAutofix(Context=None):
    KernelNode = GetKernel()
    BoardComputer = GetBoardComputer()
    Maintenance = GetMaintenanceSystem()
    Report = {
        "booted": False,
        "services": {},
        "life_support": {},
        "maintenance": {},
        "optical": {},
        "backup": None,
        "board": {},
    }

    if hasattr(KernelNode, "Phase") and KernelNode.Phase in (SystemState.OFF, SystemState.ERROR):
        if hasattr(KernelNode, "Boot"):
            Report["booted"] = bool(KernelNode.Boot())

    Report["services"] = RunServiceRepair()
    Report["life_support"] = RunLifeSupportCheck()
    if Maintenance is not None and hasattr(Maintenance, "getStatus"):
        Report["maintenance"] = Maintenance.getStatus()
        if hasattr(Maintenance, "verifyStructure"):
            Maintenance.verifyStructure()
        if hasattr(Maintenance, "backupCoreSystems"):
            Maintenance.backupCoreSystems()
    Report["optical"] = GetOpticalStatus()
    Report["board"] = GetBoardSummary()

    if BoardComputer is not None and hasattr(BoardComputer, "SetAlertLevel"):
        if Report["life_support"].get("status") == "CRITICAL":
            BoardComputer.SetAlertLevel("RED")
        elif Report["life_support"].get("status") == "WARNING":
            BoardComputer.SetAlertLevel("YELLOW")
        else:
            BoardComputer.SetAlertLevel("GREEN")

    Report["backup"] = RunEmergencyBackup(Source=ProjectRoot, Name="autofix_snapshot", ToDatabase=False)
    return Report


def RunEmergencyNexusStabilization():
    KernelNode = GetKernel()
    Status = KernelNode.Status() if hasattr(KernelNode, "Status") else {}
    Services = GetServiceHealth()
    return {
        "kernel": Status,
        "services": Services,
        "modules": GetModuleSnapshot(),
        "processes": GetProcessSnapshot(),
        "ai": GetAIStatus(),
    }


def PerformAutofix(ErrorContext=None, Sink=None):
    Context = ErrorContext or {}
    EmitEmergencyLine(Sink, "EMERGENCY AUTO FIX STARTED")
    if Context:
        EmitEmergencyBlock(Sink, "CONTEXT", Context)

    Report = RunEmergencyAutofix(Context)
    EmitEmergencyBlock(Sink, "AUTO FIX RESULT", Report)
    return Report


def PerformRecovery(Snapshot=None, Destination=None, FromDb=False):
    Report = RunEmergencyRecovery(Snapshot, Destination=Destination, FromDb=FromDb)
    return Report


def PerformBackup(Source=None, Name=None, ToDatabase=True):
    return RunEmergencyBackup(Source=Source, Name=Name, ToDatabase=ToDatabase)


def PerformDiagnostics():
    return RunEmergencyDiagnostics()


def QueryBoardComputer(Command):
    BoardComputer = GetBoardComputer()
    if BoardComputer is None:
        return {"status": "offline", "response": "BOARD COMPUTER OFFLINE"}
    if hasattr(BoardComputer, "askAI"):
        return {
            "status": "ok",
            "response": BoardComputer.askAI(str(Command)),
        }
    return {
        "status": "unsupported",
        "response": "BOARD COMPUTER DOES NOT SUPPORT DIRECT QUERIES",
    }


def PresentScreen(ScreenObject):
    App = GetApplication()
    if App is None:
        return 1

    Surface = getattr(ScreenObject, "widget", ScreenObject)

    if hasattr(Surface, "showFullScreen"):
        Surface.showFullScreen()
    elif hasattr(Surface, "showMaximized"):
        Surface.showMaximized()
    elif hasattr(Surface, "show"):
        Surface.show()

    if hasattr(App, "processEvents"):
        App.processEvents()
    if hasattr(App, "exec"):
        return App.exec()
    return 0


def StartEmergencyMode(Context=None):
    ScreenObject = LoadEmergencyScreen(Context)
    return ScreenObject


def RunEmergencyMode(Context=None):
    ScreenObject = StartEmergencyMode(Context)
    return PresentScreen(ScreenObject)


if __name__ == "__main__":
    raise SystemExit(RunEmergencyMode())
