# ◤ TITANIUM MASTER SYSTEM & SUBSYSTEM // COMPLETE SHIP OS COORDINATOR 🖖
# =============================================================================
# ФАЙЛ: lcars/core/system.py
# ОПИС: Головна Майстер-Система LCARS Framework (MasterSystem) та Subsystem.
#       Операційне середовище та координатор зорельота.
#       ВІДПОВІДАЛЬНІСТЬ:
#       1. Subsystem — фундаментальний базовий клас для всіх підсистем Системи
#          (аналогічно як Subprocess у Process).
#       2. MasterSystem — координує BIOS POST, конфігурації, модулі та інженерію.
#       3. Підключає інженерний колектор, ізолінійні чіпи та сенсорну сітку.
#       4. Надає консоль та інтерфейс управління екіпажу.
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================
from lcars.base.type import LCARS, SystemComponent
from lcars.base.info import Version, Passport
from lcars.core.signal import ODN, Transmission
from lcars.core.conduit import ServiceRegistry, Service
from lcars.service.chronometer import Chronometer
from lcars.system.config import Config
# ═════════════════════════════════════════════════════════════════════
# 1. SUBSYSTEM (КАНОНІЧНИЙ КЛАС ПІДСИСТЕМИ ВСЕРЕДИНІ СИСТЕМИ)
# ═════════════════════════════════════════════════════════════════════
class Subsystem(SystemComponent):
    # Базовий клас підсистеми системи (аналог як Subprocess для Process)
    Name = "GenericSubsystem"
    Category = "General"

    def __init__(self, SubsystemId = None, ParentSystem = None):
        ActualId = SubsystemId or f"Subsystem.{self.Name}"
        super().__init__(SystemId=ActualId)
        self.System = ParentSystem
        self.Active = True
        self.PowerAllocation = 100.0
        self.Status = "ONLINE"

    # Прив'язка до батьківської Системи
    def BindSystem(self, SystemRef):
        self.System = SystemRef

    # Зміна рівня виділення потужності підсистемі
    def SetPower(self, Percent):
        self.PowerAllocation = max(0.0, min(100.0, float(Percent)))
        ODN.Transmit(f"Subsystem.{self.Name}.PowerChanged", Power=self.PowerAllocation)
        return self.PowerAllocation

    # Активація / деактивація підсистеми
    def SetActive(self, IsActive):
        self.Active = bool(IsActive)
        self.Status = "ONLINE" if self.Active else "OFFLINE"
        ODN.Transmit(f"Subsystem.{self.Name}.StateChanged", Status=self.Status)
        return self.Active

    # Звіт про стан підсистеми
    def GetState(self):
        return {
            "Subsystem": self.Name,
            "Category": self.Category,
            "Active": self.Active,
            "PowerAllocation": self.PowerAllocation,
            "Status": self.Status,
        }
# ═════════════════════════════════════════════════════════════════════
# 2. MASTER SYSTEM (ГОЛОВНЕ ОПЕРАЦІЙНЕ СЕРЕДОВИЩЕ ЗОРЕЛЬОТА)
# ═════════════════════════════════════════════════════════════════════
class MasterSystem(SystemComponent):
    InstanceRef = None

    def __new__(cls, *args, **kwargs):
        if cls.InstanceRef is None:
            cls.InstanceRef = super().__new__(cls)
            cls.InstanceRef.IsInitialized = False
        return cls.InstanceRef

    def __init__(self, SysArgs = None):
        if getattr(self, "IsInitialized", False):
            return

        super().__init__(SystemId="MasterSystem-MasterNode")
        self.Args = SysArgs or []
        self.Root = LCARS.System.Path(__file__).resolve().parents[2] if hasattr(LCARS.System, "Path") else None
        self.ErrorList = []
        self.BiosReport = None

        # 1. Реєстри модулів, служб та підсистем Матриці LCARS
        self.Services = ServiceRegistry()
        self.Subsystems = {}
        self.Modules = {}
        self.Engineering = {}

        # 2. Повний життєвий цикл розгортання Матриці (System Bootstrap)
        self.Boot()

        self.IsInitialized = True
        ODN.Transmit("MasterSystem.Online", Version=Version.Release, Status="ONLINE")

    @classmethod
    def GetInstance(cls):
        if cls.InstanceRef is None:
            cls.InstanceRef = MasterSystem()
        return cls.InstanceRef

    # ─── ЖИТТЄВИЙ ЦИКЛ ЗАВАНТАЖЕННЯ ───────────────────────
    def Boot(self):
        # 1. BIOS POST апаратна діагностика
        if not self.RunBiosChecks():
            ODN.Transmit("MasterSystem.Boot.Error", Phase="BIOS")
            return False

        # 2. Завантаження системних конфігурацій
        self.LoadSystemConfig()

        # 3. Повна інсталяція служб, модулів, підсистем та інженерних вузлів
        self.InstallFoundation()

        # 4. Запуск сервісів через ServiceRegistry
        Errors = self.Services.StartAll(self)
        if Errors:
            ODN.Transmit("MasterSystem.Degraded", Errors=Errors)
        else:
            ODN.Transmit("MasterSystem.Ready")

        return True

    def RunBiosChecks(self):
        from lcars.system.bios import BIOS
        self.BiosSystem = BIOS()
        Report = self.BiosSystem.RunPost()
        self.BiosReport = Report
        
        Status = getattr(Report, "Status", "ONLINE")
        if Status in ("FAIL", "ERROR", "CRITICAL"):
            self.AddError(f"BIOS_POST_FAILED: {Status}")
            return False
        return True

    def LoadSystemConfig(self):
        self.ConfigSystem = Config()
        return self.ConfigSystem

    def InstallFoundation(self):
        # 1. Підключення 7 канонічних служб
        from lcars.modules.net import Net
        from lcars.service.network import NetworkSubsystem
        from lcars.service.extension import ExtensionSubsystem
        from lcars.service.astrometrics import AstrometricsSubsystem
        from lcars.service.communicator import SubspaceVoiceGateway
        from lcars.service.onboard import OnboardDeployment
        from lcars.service.diagnostic import DiagnosticEngine
        from lcars.service.chronometer import StardateCalculator
        from lcars.service.scanner import Scanner

        NetworkModule = Net()
        self.Services.Register(NetworkSubsystem(NetworkModule))
        self.Services.Register(ExtensionSubsystem())
        self.Services.Register(AstrometricsSubsystem())
        self.Services.Register(SubspaceVoiceGateway())
        self.Services.Register(OnboardDeployment())
        self.Services.Register(DiagnosticEngine())
        self.Services.Register(StardateCalculator())
        self.Services.Register(Scanner())

        # 2. Підключення 12 канонічних модулів
        from lcars.modules.memory import MemoryMatrix
        from lcars.modules.sound import SoundManager
        from lcars.modules.mode import Mode
        from lcars.modules.process import ProcessManager
        from lcars.modules.storage import ChipStorageManager
        from lcars.modules.project import ProjectManager
        from lcars.modules.monitor import SystemMonitor
        from lcars.modules.sensor import SensorArray
        from lcars.modules.sensory import SensorySystem
        from lcars.modules.security import SecuritySystem
        from lcars.modules.library import LibraryArchive
        from lcars.modules.integrator import ComponentIntegrator
        from lcars.modules.plugin import PluginManager as PluginModule, AgentPlugin
        from lcars.modules.protocol import ProtocolManager

        self.Modules = {
            "memory": MemoryMatrix(),
            "sound": SoundManager(),
            "mode": Mode(),
            "net": NetworkModule,
            "process": ProcessManager(),
            "storage": ChipStorageManager(),
            "project": ProjectManager(),
            "monitor": SystemMonitor(),
            "sensor": SensorArray(),
            "sensory": SensorySystem(),
            "security": SecuritySystem(),
            "library": LibraryArchive(),
            "integrator": ComponentIntegrator(),
            "plugin": PluginModule(),
            "copilot": AgentPlugin(),
            "protocol": ProtocolManager.GetInstance(),
        }

        # 3. Підключення суверенної Інженерної зорельота
        from lcars.engineering.controller import Engineering, EngineeringController

        self.Engineering = Engineering.GetInstance(Kernel=self)
        self.EngineeringController = self.Engineering

        # 4. Реєстрація фундаментальних підсистем зорельота (Subsystems)
        from lcars.modules.comm import CommSubsystem
        self.Communication = CommSubsystem.GetInstance()

        self.RegisterSubsystem(self.Engineering)
        self.RegisterSubsystem(self.Communication)
        self.RegisterSubsystem(Subsystem(SubsystemId="Subsystem.Tactical", ParentSystem=self))
        self.RegisterSubsystem(Subsystem(SubsystemId="Subsystem.Navigation", ParentSystem=self))
        self.RegisterSubsystem(Subsystem(SubsystemId="Subsystem.Environmental", ParentSystem=self))

        # Прямі посилання для швидкого доступу
        self.SoundManager = self.Modules.get("sound")
        self.ModeManager = self.Modules.get("mode")
        self.NetworkManager = self.Modules.get("net")
        self.MemorySubstrate = self.Modules.get("memory")
        self.CopilotNode = self.Modules.get("copilot")
        self.StorageManager = self.Modules.get("storage")
        self.PluginManager = self.Services.Get("extension")
        self.AlertSubsystem = self.Services.Get("alert")

    def RegisterSubsystem(self, SubsystemInstance):
        if SubsystemInstance:
            SubsystemInstance.BindSystem(self)
            Name = str(getattr(SubsystemInstance, "SystemId", getattr(SubsystemInstance, "Name", "Unknown"))).lower()
            self.Subsystems[Name] = SubsystemInstance
            ODN.Transmit("MasterSystem.SubsystemRegistered", Subsystem=Name)

    def GetSubsystem(self, Name):
        Normalized = str(Name or "").lower().strip()
        return self.Subsystems.get(Normalized) or self.Subsystems.get(f"subsystem.{Normalized}")

    def Module(self, Name):
        return self.Modules.get(Name)

    def Service(self, Name):
        return self.Services.Require(Name)

    def Shutdown(self):
        if len(self.Services.Names()):
            self.Services.StopAll()
        ODN.Transmit("MasterSystem.Shutdown")

    # ─── КЕРУВАННЯ ТАКТИЧНИМ СТАНОМ ТА ТРИВОГОЮ ───────────
    @property
    def Alert(self):
        from lcars.system.alert import AlertSystem
        return AlertSystem.GetInstance()

    def SetAlert(self, Level, Reason = "MasterSystem Directive"):
        from lcars.system.alert import AlertSystem
        return AlertSystem.GetInstance().SetLevel(Level, Reason=Reason)

    def GetAlert(self):
        from lcars.system.alert import AlertSystem
        return AlertSystem.GetInstance().GetState()

    # ─── КЕРУВАННЯ ТА ДІАГНОСТИКА ────────────────────────
    def GetStardate(self):
        return str(Chronometer.Stardate())

    def GetEarthDate(self):
        return Chronometer.EarthDate()

    def ExecuteDirective(self, DirectiveText):
        from lcars.core.computer import BoardComputer
        Computer = BoardComputer.GetInstance()
        return Computer.ExecuteDirective(DirectiveText)

    def RunDiagnostics(self):
        return {
            "Version": Version.Release,
            "Stardate": self.GetStardate(),
            "ServicesHealth": self.Services.HealthCheck(),
            "ActiveModules": list(self.Modules.keys()),
            "EngineeringNodes": list(self.Engineering.keys()),
            "ActiveSubsystems": list(self.Subsystems.keys()),
            "BiosStatus": getattr(self.BiosReport, "Status", "ONLINE") if self.BiosReport else "UNKNOWN",
            "Errors": self.ErrorList,
        }

    def AddError(self, ErrorMessage):
        self.ErrorList.append(str(ErrorMessage))
        ODN.Transmit("MasterSystem.Error", Error=str(ErrorMessage))

# Системні аліаси зорельота
ActiveSystem = MasterSystem.GetInstance
System = MasterSystem.GetInstance
__all__ = [
    "Subsystem",
    "MasterSystem",
    "ActiveSystem",
    "System",
]
