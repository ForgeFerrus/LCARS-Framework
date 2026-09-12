# ◤ LCARS ENGINEERING :: HARDWARE & TASK CONTROLLER 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/controller.py
# ОПИС: Центральний суверенний контролер інженерного відсіку (Subsystem.Engineering).
#       Оперативно керує всіма фізичними підсистемами зорельота в рантаймі:
#       реакція на тривоги (AlertLevel), бойові/дослідницькі режими (SystemMode),
#       перерозподіл енергії EPS та диспетчеризація завдань екіпажу.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import SystemComponent, LCARS
from lcars.base.info import VersionInfo
from lcars.system.alert import AlertLevel
from lcars.core.signal import ODN
from lcars.core.system import Subsystem

from lcars.engineering.collector import CollectorCore
from lcars.engineering.isolinear import IsolinearCore
from lcars.engineering.telemetry import TelemetryGrid
from lcars.engineering.warpdrive import WarpDrive
from lcars.engineering.deflector import DeflectorSystem
from lcars.engineering.maintenance import MaintenanceProtocol, LifeSupportSystem, DamageControl, RepairSystem
from lcars.engineering.laboratory import EngineeringLaboratory
from lcars.engineering.optical import OpticalNetwork
from lcars.service.diagnostic import Diagnostic, DiagnosticLevel
from lcars.engineering.detector import DetectorBuilder
from lcars.engineering.architect import EngineeringArchitect
from lcars.engineering.chips.architecture import IsolinearChipArchitecture

# Стан виконання інженерної задачі
class StateItem(str):
    @property
    def Name(self) -> str:
        return self

    @property
    def Value(self) -> str:
        return self

class PriorityItem(int):
    @property
    def Name(self) -> str:
        Mapping = {1: "CRITICAL", 2: "HIGH", 3: "MEDIUM", 4: "LOW"}
        return Mapping.get(self, "UNKNOWN")

    @property
    def Value(self) -> int:
        return self

# Пріоритет інженерної задачі
class TaskPriority(LCARS):
    CRITICAL = PriorityItem(1)
    HIGH = PriorityItem(2)
    MEDIUM = PriorityItem(3)
    LOW = PriorityItem(4)

# Статус виконання інженерної задачі
class TaskStatus(LCARS):
    PENDING = StateItem("Pending")
    InProgress = StateItem("InProgress")
    COMPLETED = StateItem("Completed")
    FAILED = StateItem("Failed")
    CANCELLED = StateItem("Cancelled")

# Режими роботи інженерних систем
class SystemMode(LCARS):
    CRUISE = "CRUISE"
    BATTLE = "BATTLE"
    TACTICAL = "TACTICAL"
    SCIENCE = "SCIENCE"
    STEALTH = "STEALTH"
    DIAGNOSTIC = "DIAGNOSTIC"
    DOCKED = "DOCKED"

# Одна інженерна задача
class EngineeringTask(LCARS):
    def __init__(self, TaskId: str, Title: str, Description: str = "", Priority: any = TaskPriority.MEDIUM,
                 StatusVal: any = TaskStatus.PENDING, AssignedTo: str | None = None,
                 CreatedAt: float = 0.0, StartedAt: float | None = None, CompletedAt: float | None = None,
                 Metadata: dict | None = None, Dependencies: list | None = None):
        super().__init__()
        self.Id = TaskId
        self.Title = Title
        self.Description = Description
        self.Priority = Priority
        self.Status = StatusVal
        self.AssignedTo = AssignedTo
        Now = LCARS.System.Time.time()
        self.CreatedAt = CreatedAt if CreatedAt > 0.0 else Now
        self.StartedAt = StartedAt
        self.CompletedAt = CompletedAt
        self.Metadata = Metadata or {}
        self.Dependencies = Dependencies or []

    def ToDict(self) -> dict:
        PriorityName = self.Priority.Name if hasattr(self.Priority, "Name") else str(self.Priority)
        PriorityVal = self.Priority.Value if hasattr(self.Priority, "Value") else int(self.Priority)
        StatusVal = self.Status.Value if hasattr(self.Status, "Value") else str(self.Status)
        return {
            "Id": self.Id,
            "Title": self.Title,
            "Description": self.Description,
            "Priority": PriorityName,
            "PriorityValue": PriorityVal,
            "Status": StatusVal,
            "AssignedTo": self.AssignedTo,
            "CreatedAt": self.CreatedAt,
            "StartedAt": self.StartedAt,
            "CompletedAt": self.CompletedAt,
            "Metadata": self.Metadata,
            "Dependencies": self.Dependencies,
        }

# ─── ГОЛОВНЕ ВИЗНАЧЕННЯ ІНЖЕНЕРНОЇ (MAIN ENGINEERING) ─────────────────────────
class Engineering(Subsystem):
    Instance = None

    def __init__(self, Kernel: any = None, WorkDir: str | None = None,
                 Deflector: any = None, Drive: any = None, Repair: any = None,
                 Collector: any = None, Maintenance: any = None, Isolinear: any = None,
                 EventBus: any = None, *Args: any, **Kwargs: any):
        super().__init__(SubsystemId="Subsystem.Engineering", ParentSystem=Kernel)
        self.Name = "Engineering"
        self.Category = "Engineering"
        self.Kernel = Kernel
        self.WorkDir = WorkDir
        self.EventBus = EventBus
        self.Version = VersionInfo.GetVersion()

        # Фізичні підсистеми інженерного відсіку
        self.Collector = Collector or CollectorCore()
        self.Isolinear = Isolinear or IsolinearCore()
        self.Optical = OpticalNetwork.GetInstance()
        self.Detector = DetectorBuilder.GetInstance()
        self.Telemetry = TelemetryGrid.GetInstance()
        self.WarpDrive = Drive or WarpDrive.GetInstance()
        self.Deflector = Deflector or DeflectorSystem()
        self.Repair = Repair or (RepairSystem(WorkspaceRoot=WorkDir) if WorkDir else RepairSystem())
        self.LifeSupport = LifeSupportSystem.GetInstance()
        self.DamageControl = DamageControl.GetInstance()
        self.Laboratory = EngineeringLaboratory.GetInstance()
        self.Maintenance = Maintenance or (MaintenanceProtocol(WorkDir) if WorkDir else MaintenanceProtocol())
        self.Architect = EngineeringArchitect.GetInstance()
        self.Chips = IsolinearChipArchitecture.GetInstance()

        # Реєстр обладнання відсіку
        self.Subsystems: dict = {
            "Collector": self.Collector,
            "Isolinear": self.Isolinear,
            "Optical": self.Optical,
            "Detector": self.Detector,
            "Telemetry": self.Telemetry,
            "WarpDrive": self.WarpDrive,
            "Deflector": self.Deflector,
            "LifeSupport": self.LifeSupport,
            "DamageControl": self.DamageControl,
            "Repair": self.Repair,
            "Laboratory": self.Laboratory,
            "Maintenance": self.Maintenance,
            "Architect": self.Architect,
            "Chips": self.Chips,
        }

        # Підключення шини вимірювальних приладів та сенсорного масиву до всіх вузлів
        self.Collector.AutoAttach(self.Subsystems)
        self.Telemetry.AttachSubsystems(self.Subsystems)

        self.CurrentAlertLevel = AlertLevel.GREEN
        self.CurrentMode = SystemMode.CRUISE
        self.PowerAllocations = {
            "Deflector": 100.0,
            "WarpDrive": 100.0,
            "LifeSupport": 100.0,
            "Maintenance": 100.0,
            "Sensors": 100.0,
            "Auxiliary": 50.0,
        }

        self.Tasks: dict = {}
        self.TaskHistory: list = []
        self.Listeners: list = []
        self.TaskHandlers: dict = {}
        self.ActiveTaskId: str | None = None

    @classmethod
    def GetInstance(cls, Kernel: any = None, WorkDir: str | None = None) -> Engineering:
        if cls.Instance is None:
            cls.Instance = Engineering(Kernel=Kernel, WorkDir=WorkDir)
        return cls.Instance

    # Ініціалізація інженерного відсіку
    def Initialize(self) -> bool:
        self.Isolinear.OnStart()
        self.ApplyAlertLevel(AlertLevel.GREEN)
        self.ApplySystemMode(SystemMode.CRUISE)
        ODN.Transmit("Engineering.Controller.Initialized", SubsystemCount=len(self.Subsystems))
        return True

    # Реакція фізичних підсистем на рівень бойової тривоги
    def ApplyAlertLevel(self, Level: any) -> dict:
        LevelStr = str(getattr(Level, "Name", Level) or "").upper()
        if hasattr(Level, "value"):
            LevelStr = str(Level.value).upper()
        self.CurrentAlertLevel = LevelStr

        Reactions = {}

        if LevelStr == "RED":
            if hasattr(self.Deflector, "RechargeShields"):
                self.Deflector.RechargeShields()
                Reactions["Deflector"] = "ShieldsMaximum100Percent"
            elif hasattr(self.Deflector, "SetAllQuadrants"):
                self.Deflector.SetAllQuadrants(100.0)
                Reactions["Deflector"] = "Shields100Percent"

            if hasattr(self.WarpDrive, "SetWarpFactor"):
                self.WarpDrive.SetWarpFactor(0.0)
                Reactions["WarpDrive"] = "TacticalImpulseStandby"

            if hasattr(self.Repair, "ScanCompartments"):
                Breaches = self.Repair.ScanCompartments()
                Reactions["Repair"] = f"HullCheckActiveBreaches{len(Breaches)}"

            self.PowerAllocations["Deflector"] = 150.0
            self.PowerAllocations["WarpDrive"] = 120.0
            self.PowerAllocations["Auxiliary"] = 20.0

        elif LevelStr == "YELLOW":
            if hasattr(self.Deflector, "SetAllQuadrants"):
                self.Deflector.SetAllQuadrants(50.0)
                Reactions["Deflector"] = "ShieldsStandby50Percent"

            if hasattr(self.WarpDrive, "SetWarpFactor"):
                self.WarpDrive.SetWarpFactor(1.0)
                Reactions["WarpDrive"] = "WarpFactor1Ready"

            self.PowerAllocations["Deflector"] = 80.0
            self.PowerAllocations["WarpDrive"] = 100.0

        else:
            if hasattr(self.Deflector, "SetAllQuadrants"):
                self.Deflector.SetAllQuadrants(20.0)
                Reactions["Deflector"] = "NavigationalDeflectorOnly"

            if hasattr(self.WarpDrive, "SetWarpFactor"):
                self.WarpDrive.SetWarpFactor(5.0)
                Reactions["WarpDrive"] = "CruiseWarpFactor5"

            self.PowerAllocations["Deflector"] = 50.0
            self.PowerAllocations["WarpDrive"] = 100.0
            self.PowerAllocations["Auxiliary"] = 50.0

        ODN.Transmit("Engineering.Controller.AlertApplied", Level=LevelStr, Reactions=Reactions)
        return Reactions

    SetAlertLevel = ApplyAlertLevel

    # Застосування тактичного або дослідницького режиму
    def ApplySystemMode(self, Mode: str) -> dict:
        ModeStr = str(Mode or "").upper()
        self.CurrentMode = ModeStr
        Profile = {}

        if ModeStr == SystemMode.BATTLE:
            self.ApplyAlertLevel(AlertLevel.RED)
            Profile["Status"] = "BattleStations"
        elif ModeStr == SystemMode.TACTICAL:
            self.ApplyAlertLevel(AlertLevel.YELLOW)
            Profile["Status"] = "TacticalReadiness"
        elif ModeStr == SystemMode.STEALTH:
            if hasattr(self.Deflector, "SetAllQuadrants"):
                self.Deflector.SetAllQuadrants(0.0)
            Profile["Status"] = "SilentRunningEmissionsMinimized"
        elif ModeStr == SystemMode.SCIENCE:
            Profile["Status"] = "SensorGridPeakResolution"
        else:
            self.ApplyAlertLevel(AlertLevel.GREEN)
            Profile["Status"] = "StandardCruise"

        ODN.Transmit("Engineering.Controller.ModeApplied", Mode=ModeStr, Profile=Profile)
        return Profile

    SetSystemMode = ApplySystemMode

    # Перерозподіл потужності EPS
    def BalancePower(self, SubsystemName: str, AmountMw: float) -> bool:
        if SubsystemName in self.PowerAllocations:
            self.PowerAllocations[SubsystemName] = float(AmountMw)
            ODN.Transmit("Engineering.Controller.PowerBalanced", Subsystem=SubsystemName, PowerMw=AmountMw)
            return True
        return False

    # Запуск 5-рівневої діагностики через системну службу Diagnostic
    def RunDiagnostic(self, Level: int = 5) -> list:
        DiagService = Diagnostic()
        return DiagService.RunProtocol(Level)

    # Доступ до конкретної підсистеми
    def GetSubsystem(self, Name: str) -> any:
        return self.Subsystems.get(Name)

    # Диспетчеризація інженерних задач
    def CreateTask(self, TaskId: str, Title: str, Description: str = "",
                   Priority: any = TaskPriority.MEDIUM, AssignedTo: str | None = None,
                   Metadata: dict | None = None, Dependencies: list | None = None) -> EngineeringTask:
        Task = EngineeringTask(
            TaskId=TaskId,
            Title=Title,
            Description=Description,
            Priority=Priority,
            AssignedTo=AssignedTo,
            Metadata=Metadata,
            Dependencies=Dependencies
        )
        self.Tasks[TaskId] = Task
        self.Notify("TaskCreated", Task)
        return Task

    def StartTask(self, TaskId: str) -> bool:
        Task = self.Tasks.get(TaskId)
        if Task is None or Task.Status != TaskStatus.PENDING:
            return False
        Now = LCARS.System.Time.time()
        Task.Status = TaskStatus.InProgress
        Task.StartedAt = Now
        self.ActiveTaskId = TaskId
        self.Notify("TaskStarted", Task)
        Handler = self.TaskHandlers.get(TaskId)
        if callable(Handler):
            Handler(Task)
        return True

    def CompleteTask(self, TaskId: str, ResultMetadata: dict | None = None) -> bool:
        Task = self.Tasks.get(TaskId)
        if Task is None or Task.Status != TaskStatus.InProgress:
            return False
        Now = LCARS.System.Time.time()
        Task.Status = TaskStatus.COMPLETED
        Task.CompletedAt = Now
        if ResultMetadata:
            Task.Metadata.update(ResultMetadata)
        if self.ActiveTaskId == TaskId:
            self.ActiveTaskId = None
        self.TaskHistory.append(Task)
        self.Notify("TaskCompleted", Task)
        return True

    def FailTask(self, TaskId: str, ReasonStr: str = "") -> bool:
        Task = self.Tasks.get(TaskId)
        if Task is None:
            return False
        Now = LCARS.System.Time.time()
        Task.Status = TaskStatus.FAILED
        Task.CompletedAt = Now
        Task.Metadata["FailureReason"] = ReasonStr
        if self.ActiveTaskId == TaskId:
            self.ActiveTaskId = None
        self.TaskHistory.append(Task)
        self.Notify("TaskFailed", Task)
        return True

    def CancelTask(self, TaskId: str) -> bool:
        Task = self.Tasks.get(TaskId)
        if Task is None:
            return False
        Task.Status = TaskStatus.CANCELLED
        if self.ActiveTaskId == TaskId:
            self.ActiveTaskId = None
        self.TaskHistory.append(Task)
        self.Notify("TaskCancelled", Task)
        return True

    def GetTask(self, TaskId: str) -> EngineeringTask | None:
        return self.Tasks.get(TaskId)

    def GetActiveTask(self) -> EngineeringTask | None:
        if self.ActiveTaskId:
            return self.Tasks.get(self.ActiveTaskId)
        return None

    def GetPendingTasks(self) -> list:
        return [T for T in self.Tasks.values() if T.Status == TaskStatus.PENDING]

    def GetTasksByPriority(self, PriorityVal: any) -> list:
        return [T for T in self.Tasks.values() if T.Priority == PriorityVal]

    def GetAllTasks(self) -> list:
        return list(self.Tasks.values())

    def GetHistory(self) -> list:
        return list(self.TaskHistory)

    def RegisterHandler(self, TaskId: str, HandlerFunc: any) -> None:
        self.TaskHandlers[TaskId] = HandlerFunc

    def AddListener(self, CallbackFunc: any) -> None:
        self.Listeners.append(CallbackFunc)

    def RemoveListener(self, CallbackFunc: any) -> None:
        if CallbackFunc in self.Listeners:
            self.Listeners.remove(CallbackFunc)

    def Notify(self, EventName: str, Task: EngineeringTask) -> None:
        for Listener in self.Listeners:
            if callable(Listener):
                Listener(EventName, Task)

    def GetStatus(self) -> dict:
        Total = len(self.Tasks)
        Pending = len([T for T in self.Tasks.values() if T.Status == TaskStatus.PENDING])
        InProgress = len([T for T in self.Tasks.values() if T.Status == TaskStatus.InProgress])
        Completed = len([T for T in self.Tasks.values() if T.Status == TaskStatus.COMPLETED])
        Failed = len([T for T in self.Tasks.values() if T.Status == TaskStatus.FAILED])
        return {
            "Subsystem": self.Name,
            "Status": self.Status,
            "Version": self.Version,
            "ShipClass": self.Architect.CurrentClass,
            "SubsystemsCount": len(self.Subsystems),
            "TotalChipsCount": sum(len(Chips) for Chips in self.Chips.Catalog.values()),
            "CurrentAlert": self.CurrentAlertLevel,
            "CurrentMode": self.CurrentMode,
            "PowerAllocations": self.PowerAllocations,
            "ActiveTaskId": self.ActiveTaskId,
            "PendingTasks": Pending,
            "CompletedTasks": Completed,
            "TelemetryPulse": self.Collector.PollAll(),
        }

    def ConfigureShipClass(self, NewClass: str) -> dict:
        return self.Architect.ConfigureClass(NewClass)

    def AuditPowerGrid(self) -> dict:
        return self.Architect.AuditPowerGrid(self.PowerAllocations)

    def AuditOpticalNetwork(self) -> dict:
        LoadedChipsCount = sum(len(Chips) for Chips in self.Chips.Catalog.values())
        return self.Architect.AuditOpticalNetwork(LoadedChipsCount)

    def GetChipMatrixStatus(self) -> dict:
        return {
            "TotalChipsCount": sum(len(Chips) for Chips in self.Chips.Catalog.values()),
            "Categories": list(self.Chips.Categories.keys()),
            "Slots": len(self.Chips.Slots),
        }

    def keys(self):
        return self.Subsystems.keys()

    def values(self):
        return self.Subsystems.values()

    def items(self):
        return self.Subsystems.items()

    def __getitem__(self, Key: str) -> any:
        return self.Subsystems.get(Key)

    def get(self, Key: str, Default: any = None) -> any:
        return self.Subsystems.get(Key, Default)

# Керує вузлами ізолінійного банку
class ISOController(LCARS):
    def __init__(self, Bank: any):
        super().__init__()
        self.Bank = Bank
        self.ActiveChips = {}
        self.DisabledChips = {}
        self.LastError: str | None = None

    def ActivateChip(self, ChipId: str) -> bool:
        Chip = self.Bank.GetChip(ChipId)
        if Chip is None:
            self.LastError = f"Chip {ChipId} not found"
            return False
        Success = Chip.Connect()
        if Success:
            self.ActiveChips[ChipId] = Chip
            self.DisabledChips.pop(ChipId, None)
            return True
        self.LastError = f"Failed to connect chip {ChipId}"
        return False

    def DeactivateChip(self, ChipId: str) -> bool:
        Chip = self.ActiveChips.get(ChipId)
        if Chip is None:
            return False
        Chip.Disconnect()
        self.DisabledChips[ChipId] = Chip
        self.ActiveChips.pop(ChipId, None)
        return True

    def DetachChip(self, ChipId: str) -> bool:
        Chip = self.ActiveChips.get(ChipId)
        if Chip is None:
            return False
        Chip.Disconnect()
        self.ActiveChips.pop(ChipId, None)
        return True

    def GetChipStatus(self, ChipId: str) -> dict | None:
        Chip = self.Bank.GetChip(ChipId)
        if Chip is not None:
            return Chip.GetStatus()
        return None

    def GetSystemStatus(self) -> dict:
        return {
            "ActiveCount": len(self.ActiveChips),
            "DisabledCount": len(self.DisabledChips),
            "ActiveIds": list(self.ActiveChips.keys()),
            "DisabledIds": list(self.DisabledChips.keys()),
            "LastError": self.LastError,
            "Version": VersionInfo.GetVersion(),
        }

class EngineeringAccess(LCARS):
    ControllerInstance = None

    @classmethod
    def GetEngineeringController(cls) -> Engineering:
        if cls.ControllerInstance is None:
            cls.ControllerInstance = Engineering.GetInstance()
        return cls.ControllerInstance

# Канонічні точки доступу до Інженерної
EngineeringCore = Engineering.GetInstance
EngineeringController = Engineering
ENGINEERING = Engineering.GetInstance()
GetEngineeringController = EngineeringAccess.GetEngineeringController
