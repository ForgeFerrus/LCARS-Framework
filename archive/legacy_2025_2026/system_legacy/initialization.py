from __future__ import annotations
from lcars.base.register import registry
from lcars.core.signal import ODN, Transmission
from lcars.modules.storage import ListChips
from lcars.system.bios import BIOS
from lcars.system.software import BootTarget, Firmware
from lcars.service.bridge import Bridge


# LCARS стартує як послідовність окремих етапів. Спочатку реєстр і ядро,
# потім шина подій, чіпи, BIOS і лише після цього сервіси та система.
class InitStep:
    def __init__(self, Name: str, Handler: Callable[[], bool], Critical: bool = True, Description: str = ""):
        self.Name = Name
        self.Handler = Handler
        self.Critical = Critical
        self.Description = Description


# Клас для зберігання звіту про ініціалізацію системи
# Збирає помилки, попередження та деталі кожного етапу
class InitReport:
    def __init__(self):
        self.Status: str = "PENDING"
        self.Stage: str = "INIT"
        self.Errors: List[str] = []
        self.Warnings: List[str] = []
        self.Details: List[str] = []

    def Ok(self) -> bool:
        return len(self.Errors) == 0

    def Export(self) -> Dict[str, Any]:
        return {
            "Status": self.Status,
            "Stage": self.Stage,
            "Errors": list(self.Errors),
            "Warnings": list(self.Warnings),
            "Details": list(self.Details),
            "Success": self.Ok(),
        }


# Єдиний системний ланцюг старту LCARS
# Виконує реальне підключення та підготовку системних модулів (без створення UI)
class SystemInitializer:
    StageChanged = Transmission(str, dict)
    Completed = Transmission(dict)
    Failed = Transmission(dict)

    def __init__(self, ProgressCallback: Callable[[str, int], None] | None = None):
        self.ProgressCallback = ProgressCallback
        self.Report = InitReport()
        self.Context: Dict[str, Any] = {}
        self.Sequence = [
            InitStep("REGISTER MAP", self.CheckRegistry, True, "Перевіряє базовий реєстр LCARS."),
            InitStep("KERNEL MAP", self.CheckKernelModule, True, "Піднімає ядро раніше за інші шари."),
            InitStep("ODN BUS", self.CheckODN, True, "Піднімає шину подій і телеметрії."),
            InitStep("ISOLINEAR CHIPS", self.CheckChips, True, "Перевіряє банк ізолінійних даних."),
            InitStep("BIOS POST", self.RunBiosPost, True, "Запускає системний POST BIOS."),
            InitStep("SERVICE CHANNELS", self.PrepareServiceChannels, False, "Готує канали сервісів."),
            InitStep("NETWORK UPLINK", self.CheckNetworkSubsystem, False, "Піднімає базовий мережевий модуль."),
            InitStep("SYSTEM READY", self.MarkReady, True, "Фіксує фінальний стан системи."),
        ]

    def Execute(self) -> bool:
        Count = len(self.Sequence)
        for Index, Step in enumerate(self.Sequence):
            self.Report.Stage = Step.Name
            Percent = int((Index / max(1, Count - 1)) * 100)
            self.DescribeStep(Step)
            self.EmitProgress(Step.Name, Percent)
            if not Step.Handler():
                if not self.Report.Errors:
                    self.Report.Errors.append("Initialization stopped at stage: " + Step.Name)
                self.Report.Status = "FAILED"
                Payload = self.Report.Export()
                ODN.Emit("System.Init.Failed", Payload)
                self.Failed.Emit(Payload)
                return False
        self.Report.Status = "OK"
        self.EmitProgress("READY", 100)
        Payload = self.Report.Export()
        ODN.Emit("System.Init.Ready", Payload)
        self.Completed.Emit(Payload)
        return True

    def Run(self, OnStage=None, OnFinish=None, OnFail=None) -> bool:
        if OnStage:
            self.ProgressCallback = lambda stage, percent: OnStage(stage, percent)
        if OnFinish:
            self.Completed.Connect(OnFinish)
        if OnFail:
            self.Failed.Connect(OnFail)
        return self.Execute()

    def DescribeStep(self, Step: InitStep) -> None:
        if Step.Description:
            self.Report.Details.append("[STAGE] " + Step.Name + " - " + Step.Description)

    def EmitProgress(self, Stage: str, Percent: int) -> None:
        Payload = {"Stage": Stage, "Progress": Percent}
        self.StageChanged.Emit(Stage, Payload)
        ODN.Emit("System.Init.Stage", Payload)
        if self.ProgressCallback:
            self.ProgressCallback(Stage, Percent)

    def CheckRegistry(self) -> bool:
        Required = [
            "Base.Interface.Application",
            "Base.Interface.Widget",
            "Base.Interface.Stack",
            "Base.Interface.Layout.Vertical",
            "Base.Interface.Layout.Horizontal",
            "Base.Core.Timer",
            "Base.Protocol",
        ]
        Missing = [Name for Name in Required if registry.Resolve(Name) is None]
        if Missing:
            self.Report.Errors.append("Registry sectors missing: " + ", ".join(Missing))
            return False
        self.Report.Details.append("[OK] REGISTER MAP")
        return True

    def CheckKernelModule(self) -> bool:
        # Перевіряємо наявність модуля ядра через Bridge замість importlib
        KernelSpec = Bridge().Load("Kernel.Module.Spec")
        if KernelSpec is None:
            from lcars.core.kernel import Kernel as KernelClass
            KernelSpec = KernelClass
        if KernelSpec is None:
            self.Report.Errors.append("Kernel module is not mapped.")
            return False
        from lcars.core.kernel import Kernel
        KernelNode = Kernel()
        KernelStarted = KernelNode.Boot()
        if not KernelStarted:
            self.Report.Errors.append("Kernel boot failed.")
            return False
        self.Report.Details.append("[OK] KERNEL LOADED AND RESPONDING")
        return True

    def CheckODN(self) -> bool:
        if not hasattr(ODN, "BlackBox"):
            self.Report.Errors.append("ODN BlackBox is offline.")
            return False
        self.Context["ODN"] = ODN.BlackBox.GetStatus()
        self.Report.Details.append("[OK] ODN BLACK BOX")
        return True

    def CheckChips(self) -> bool:
        Chips = ListChips()
        self.Context["Chips"] = Chips
        if not Chips:
            self.Report.Errors.append("Isolinear chip catalog is empty.")
            return False
        self.Report.Details.append("[OK] CHIPS " + str(len(Chips)))
        return True

    def RunBiosPost(self) -> bool:
        Bios = BIOS()
        Result = Bios.RunPost()
        self.Context["BIOS"] = Bios.ReportPayload(Result)
        self.Report.Details.extend(Result.Lines())
        for Check in Result.Checks:
            Message = Check.Name + (" :: " + Check.Detail if Check.Detail else "")
            if Check.Status != "OK":
                self.Report.Errors.append("BIOS POST failed: " + Message)
        return Result.Status == "NOMINAL"

    def PrepareServiceChannels(self) -> bool:
        from lcars.modules.security import AuthManager
        self.Context["AuthManager"] = AuthManager()
        self.Context["ServiceChannelsReady"] = True
        ODN.Emit("Services.Prepare", {"Source": "SystemInitializer"})
        self.Report.Details.append("[OK] SERVICE CHANNELS CONNECTED")
        return True

    def CheckNetworkSubsystem(self) -> bool:
        # Перевіряємо наявність мережевого модуля через Bridge
        NetworkSpec = Bridge().Load("Network.Module.Spec")
        if NetworkSpec is None:
            from lcars.modules.net import NetworkManager
        else:
            from lcars.modules.net import NetworkManager
        Node = NetworkManager()
        self.Context["NetworkManager"] = Node
        if hasattr(Node, "IsEnabled") and not Node.IsEnabled():
            self.Report.Errors.append("NetworkManager is disabled.")
            return False
        self.Report.Details.append("[OK] NETWORK UPLINK CONNECTED")
        return True

    def MarkReady(self) -> bool:
        registry.Register("System.Initializer", self)
        registry.Register("System.InitReport", self.Report.Export())
        self.Report.Details.append("[OK] SYSTEM READY")
        return True

    def GetReport(self) -> Dict[str, Any]:
        return self.Report.Export()


# Скорочений варіант SystemInitializer
class SystemInit(SystemInitializer):
    def initialize(self, Headless: bool = False) -> bool:
        return self.Execute()

    def GetReport(self) -> Dict[str, Any]:
        return self.Report.Export()


# Менеджер завантаження системи як окремий клас потоку через Bridge
class BootManager:
    STAGES = ["INIT", "FIRMWARE", "KERNEL", "SERVICES", "UI", "READY"]

    def __init__(self, Config: Any = None):
        self.BootStageChanged = Transmission(str, dict)
        self.SystemReady = Transmission(dict)
        self.Config = Config or {}
        self.CurrentStage = 0
        self.Target = self.Config.get("target", "desktop")
        self.SkipFirmware = self.Config.get("skip_firmware", False)
        self.FirmwareNode = None
        ODN.EventBus.On("Firmware.BootSelected", self.OnFirmwareBootSelected)
        ODN.EventBus.On("BIOS.SaveAndExit", self.OnBiosExit)

    def Start(self) -> None:
        # Запускаємо через Bridge замість threading.Thread
        Threading = Bridge().Load("System.Threading")
        if Threading is not None:
            Threading.Thread(target=self.RunSequence, daemon=True, name="LCARS-BootManager").start()
        else:
            self.RunSequence()

    def AdvanceStage(self, StageName: str) -> None:
        self.CurrentStage = self.STAGES.index(StageName) if StageName in self.STAGES else self.CurrentStage
        self.BootStageChanged.Emit(StageName, {"Stage": StageName})

    def RunSequence(self) -> None:
        Initializer = SystemInitAccess.GetSystemInit()
        if not Initializer.Execute():
            ODN.Emit("System.Init.Failed", Initializer.GetReport())
            return
        if not self.SkipFirmware:
            self.AdvanceStage("FIRMWARE")
            self.LaunchFirmware()
            return
        self.LoadCoreChain()

    def LoadCoreChain(self) -> None:
        self.AdvanceStage("KERNEL")
        self.LoadKernel()
        self.AdvanceStage("SERVICES")
        self.StartServices()
        self.AdvanceStage("UI")
        self.LaunchUi()
        self.AdvanceStage("READY")
        self.SystemReady.Emit({"Stage": "READY"})

    def LaunchFirmware(self) -> None:
        self.LoadCoreChain()

    def LoadKernel(self) -> bool:
        return True

    def StartServices(self) -> bool:
        return True

    def LaunchUi(self) -> bool:
        ODN.Emit("System.Phase.Desktop")
        return True

    def OnFirmwareBootSelected(self, *Args: Any, **Kwargs: Any) -> None:
        self.LoadCoreChain()

    def OnBiosExit(self, *Args: Any, **Kwargs: Any) -> None:
        self.SkipFirmware = True
        self.LoadCoreChain()


# Псевдонім BootManager
class LCARSBootloader(BootManager):
    pass


# Клас доступу до синглтону ініціалізатора (замість standalone функцій)
class SystemInitAccess:
    Node: SystemInit | None = None

    @classmethod
    def GetSystemInit(cls) -> SystemInit:
        if cls.Node is None:
            cls.Node = SystemInit(ProgressCallback=None)
        return cls.Node

    @staticmethod
    def CreateInitializer(ProgressCallback: Callable[[str, int], None] | None = None) -> SystemInitializer:
        return SystemInitializer(ProgressCallback)

    @staticmethod
    def InitializeSystem(ProgressCallback: Callable[[str, int], None] | None = None) -> bool:
        Initializer = SystemInitializer(ProgressCallback)
        return Initializer.Execute()


# Псевдоніми для зворотної сумісності
GetSystemInit = SystemInitAccess.GetSystemInit
CreateInitializer = SystemInitAccess.CreateInitializer
InitializeSystem = SystemInitAccess.InitializeSystem
