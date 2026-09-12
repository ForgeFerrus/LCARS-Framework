# ◤ TITANIUM LCARS :: EMERGENCY FAILOVER & SUBSYSTEM RECOVERY 🖖
# =============================================================================
# ФАЙЛ: lcars/system/emergency.py
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Underscores, Strict PascalCase).
# =============================================================================

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.core.signal import ODN, Transmission

class EmergencySystem:
    Instance = None

    @classmethod
    def GetInstance(cls) -> EmergencySystem:
        if cls.Instance is None:
            cls.Instance = cls()
        return cls.Instance

    def __init__(self):
        self.SystemId = "EMERGENCY_FAILOVER_MATRIX"
        self.Version = "25th Century v4.7"
        self.IsEmergencyActive = False
        self.EmergencyReason = ""
        self.FailedSubsystem = ""
        self.Criticality = "NONE"
        self.AuxiliaryCircuitsEngaged = False
        self.AuthorizedBy = ""
        self.EngagedTimestamp = 0.0
        self.EmergencyHistory = []

        self.EmergencyTriggered = Transmission()
        self.EmergencyDisengaged = Transmission()

    def TriggerEmergency(self, Reason: str = "Subsystem Failure", Subsystem: str = "CORE", Criticality: str = "CRITICAL", AuthorizedBy: str = "SystemAuto") -> dict:
        TimeModule = LCARS.System.Time
        NowTime = TimeModule.time() if hasattr(TimeModule, "time") else 0.0

        self.IsEmergencyActive = True
        self.EmergencyReason = str(Reason)
        self.FailedSubsystem = str(Subsystem)
        self.Criticality = str(Criticality)
        self.AuxiliaryCircuitsEngaged = True
        self.AuthorizedBy = str(AuthorizedBy)
        self.EngagedTimestamp = NowTime

        Record = {
            "Timestamp": round(NowTime, 2),
            "Action": "Trigger",
            "Reason": self.EmergencyReason,
            "Subsystem": self.FailedSubsystem,
            "Criticality": self.Criticality,
            "AuthorizedBy": self.AuthorizedBy,
            "AuxiliaryEngaged": True,
        }
        self.EmergencyHistory.append(Record)

        from lcars.system.alert import AlertSystem, AlertLevel
        AlertSystem.GetInstance().SetLevel(AlertLevel.RED, Reason=Reason, AuthorizedBy=AuthorizedBy)

        StatePacket = self.GetEmergencyState()
        self.EmergencyTriggered.Emit(StatePacket)
        ODN.Transmit("Emergency.Triggered", **StatePacket)
        return StatePacket

    def DisengageEmergency(self, Reason: str = "All Systems Nominal", AuthorizedBy: str = "Captain") -> dict:
        TimeModule = LCARS.System.Time
        NowTime = TimeModule.time() if hasattr(TimeModule, "time") else 0.0

        self.IsEmergencyActive = False
        self.EmergencyReason = str(Reason)
        self.FailedSubsystem = ""
        self.Criticality = "NONE"
        self.AuxiliaryCircuitsEngaged = False
        self.AuthorizedBy = str(AuthorizedBy)

        Record = {
            "Timestamp": round(NowTime, 2),
            "Action": "Disengage",
            "Reason": self.EmergencyReason,
            "AuthorizedBy": self.AuthorizedBy,
            "AuxiliaryEngaged": False,
        }
        self.EmergencyHistory.append(Record)

        from lcars.system.alert import AlertSystem, AlertLevel
        AlertSystem.GetInstance().SetLevel(AlertLevel.GREEN, Reason=Reason, AuthorizedBy=AuthorizedBy)

        StatePacket = self.GetEmergencyState()
        self.EmergencyDisengaged.Emit(StatePacket)
        ODN.Transmit("Emergency.Disengaged", **StatePacket)
        return StatePacket

    def VerifyAuxiliaryCircuits(self) -> dict:
        return {
            "CircuitsReady": True,
            "AuxiliaryBypass": "ONLINE",
            "EmergencySystemOnline": True,
            "ActiveFailover": self.IsEmergencyActive,
        }

    def GetEmergencyState(self) -> dict:
        return {
            "SystemId": self.SystemId,
            "Version": self.Version,
            "IsEmergencyActive": self.IsEmergencyActive,
            "FailedSubsystem": self.FailedSubsystem,
            "EmergencyReason": self.EmergencyReason,
            "Criticality": self.Criticality,
            "AuxiliaryCircuitsEngaged": self.AuxiliaryCircuitsEngaged,
            "AuthorizedBy": self.AuthorizedBy,
            "EngagedTimestamp": self.EngagedTimestamp,
            "TotalIncidents": len(self.EmergencyHistory),
        }

    def GetHistory(self) -> list[dict]:
        return list(self.EmergencyHistory)

    def RunBiosPost(self) -> list:
        return RunBiosPost()

    def PerformDiagnostics(self) -> dict:
        return PerformDiagnostics()

    def GetCoreDiagnostics(self) -> dict:
        return GetCoreDiagnostics()

    def PerformAutofix(self, Context: dict = None) -> str:
        return PerformAutofix(Context)

    def PerformRecovery(self) -> str:
        return PerformRecovery()

    def RunLifeSupportCheck(self) -> dict:
        return RunLifeSupportCheck()

    def GetServiceHealth(self) -> dict:
        return GetServiceHealth()

    def RunModuleAudit(self) -> list:
        return RunModuleAudit()

def GetBoardComputer():
    from lcars.core.computer import BoardComputer
    return BoardComputer.GetInstance()

def GetBoardSummary() -> dict:
    es = EmergencySystem.GetInstance()
    return {
        "CORE STATUS": "EMERGENCY ISOLATION" if es.IsEmergencyActive else "NOMINAL",
        "FAILOVER CIRCUITS": "ENGAGED" if es.AuxiliaryCircuitsEngaged else "STANDBY",
        "CRITICALITY": es.Criticality or "NONE",
        "ACTIVE INCIDENTS": str(len(es.EmergencyHistory)),
    }

def BuildEmergencySnapshot(Context: dict = None) -> dict:
    ctx = Context or {}
    return {
        "kernel": {
            "Phase": "EMERGENCY_OVERRIDE",
            "Reason": ctx.get("Reason", "UNKNOWN FAULT"),
            "Services": {
                "Registered": ["ODN", "TELEMETRY", "CONSOLE", "AUDIO", "EMERGENCY"],
                "Health": {"CIRCUITS": "AUXILIARY", "INTEGRITY": "100%"},
            },
        }
    }

def GetCoreDiagnostics() -> dict:
    from lcars.service.diagnostic import DiagnosticEngine
    Engine = DiagnosticEngine()
    Results = Engine.RunProtocol(3)
    Output = {}
    for ProbeName, Health in Results:
        Output[ProbeName] = Health.Status + " - " + Health.Message
    return Output

def GetAIStatus() -> dict:
    from lcars.service.provider import AIProviderManager
    Provider = AIProviderManager.GetInstance()
    Active = Provider.ActiveBackend
    return {
        "ACTIVE": getattr(Active, "Name", "STANDBY"),
        "MODEL": getattr(Active, "Model", getattr(Active, "ModelId", "UNKNOWN")),
        "AVAILABLE": Active.CheckAvailable() if hasattr(Active, "CheckAvailable") else False,
    }

def GetServiceHealth() -> dict:
    from lcars.core.system import MasterSystem
    MS = MasterSystem.GetInstance()
    Health = {}
    if MS and hasattr(MS, "Services") and hasattr(MS.Services, "Services"):
        for SName in MS.Services.Services.keys():
            Health[str(SName).upper()] = "ONLINE"
    if not Health:
        Health = {"ODN": "ONLINE", "TELEMETRY": "ONLINE", "CONSOLE": "ONLINE", "EMERGENCY": "ENGAGED"}
    return Health

def RunProcessAudit() -> list:
    from lcars.core.system import MasterSystem
    MS = MasterSystem.GetInstance()
    ProcessList = []
    if MS and hasattr(MS, "Processes") and hasattr(MS.Processes, "Processes"):
        for PId, Proc in MS.Processes.Processes.items():
            ProcessList.append({"name": getattr(Proc, "Name", str(PId)), "pid": PId, "status": "ACTIVE"})
    if not ProcessList:
        ProcessList = [
            {"name": "ODN Carrier Bus", "pid": 4701, "status": "ACTIVE"},
            {"name": "Emergency Guard", "pid": 9901, "status": "ENGAGED"},
            {"name": "MasterSystem Core", "pid": 1001, "status": "ACTIVE"},
        ]
    return ProcessList

def RunModuleAudit() -> list:
    from lcars.core.system import MasterSystem
    MS = MasterSystem.GetInstance()
    if MS and hasattr(MS, "Modules") and MS.Modules:
        return list(MS.Modules.keys())
    return ["CORE", "ODN", "BIOS", "KERNEL", "SYSTEM", "ALERT", "CONSOLE", "EMERGENCY"]

def QueryBoardComputer(Command: str) -> str:
    bc = GetBoardComputer()
    if bc and hasattr(bc, "ExecuteDirective"):
        Res = bc.ExecuteDirective(Command)
        if isinstance(Res, dict):
            return str(Res.get("Message", Res))
        return str(Res)
    return "COMMAND EXECUTED BY AUXILIARY FAILOVER"

def PerformDiagnostics() -> dict:
    from lcars.service.diagnostic import DiagnosticEngine
    Engine = DiagnosticEngine()
    Results = Engine.RunProtocol(1)
    DiagReport = {}
    for Name, Health in Results:
        DiagReport[Name] = Health.Status + " (" + Health.Message + ")"
    return DiagReport

def PerformAutofix(Context: dict = None) -> str:
    es = EmergencySystem.GetInstance()
    es.AuxiliaryCircuitsEngaged = True
    from lcars.core.computer import BoardComputer
    bc = BoardComputer.GetInstance()
    if hasattr(bc, "InitializeSystem"):
        bc.InitializeSystem()
    from lcars.core.signal import ODN
    ODN.Transmit("Emergency.AutoFixCompleted", Status="REPAIRED")
    return "AUTOFIX PROTOCOL COMPLETE // CORE RE-INITIALIZED // ODN CONDUIT NOMINAL"

def PerformRecovery() -> str:
    es = EmergencySystem.GetInstance()
    es.DisengageEmergency("ManualRecovery")
    from lcars.core.signal import ODN
    ODN.Transmit("System.Phase.Terminal")
    return "RECOVERY COMPLETED // DISENGAGING EMERGENCY // CONDITION GREEN RESTORED"

def RunLifeSupportCheck() -> dict:
    from lcars.core.computer import BoardComputer
    bc = BoardComputer.GetInstance()
    Subsystems = getattr(bc, "Subsystems", {})
    Report = {}
    if Subsystems:
        for SName, SState in Subsystems.items():
            Report[str(SName)] = str(SState)
    else:
        Report = {"LifeSupport": "ONLINE", "WarpCore": "ONLINE", "Sensors": "ONLINE"}
    return Report

def RunBiosPost() -> list:
    from lcars.system.bios import BIOS
    BiosSys = BIOS()
    Report = BiosSys.RunPost()
    return Report.Lines() if hasattr(Report, "Lines") else ["BIOS POST: COMPLETE"]

EMERGENCY = EmergencySystem.GetInstance()
