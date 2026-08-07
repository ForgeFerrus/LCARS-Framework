from __future__ import annotations

import importlib.util
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from lcars.base.register import registry
from lcars.core.signal import ODN, Transmission
from lcars.modules.storage import ListChips
from lcars.system.bios import BIOS
from lcars.system.software import BootTarget, Firmware


# LCARS стартує як послідовність окремих етапів. Спочатку реєстр і ядро,
# потім шина подій, чіпи, BIOS і лише після цього сервіси та система.
@dataclass
class InitStep:
    Name: str
    Handler: Callable[[], bool]
    Critical: bool = True
    Description: str = ""

# Клас для зберігання звіту про ініціалізацію системи... Збирає помилки, попередження та деталі кожного етапу
@dataclass
class InitReport:
    Status: str = "PENDING"
    Stage: str = "INIT"
    Errors: List[str] = field(default_factory=list)
    Warnings: List[str] = field(default_factory=list)
    Details: List[str] = field(default_factory=list)

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

# Єдиний системний ланцюг старту LCARS Виконує реальне підключення та підготовку системних модулів (без створення UI).
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
            "Interface.Application",
            "Interface.Widget",
            "Interface.Stacked",
            "Interface.Layout.VBox",
            "Interface.Layout.HBox",
            "Base.Timer",
            "Protocol",
        ]
        Missing = [Name for Name in Required if registry.Get(Name) is None]
        if Missing:
            self.Report.Errors.append("Registry sectors missing: " + ", ".join(Missing))
            return False
        self.Report.Details.append("[OK] REGISTER MAP")
        return True

    def CheckKernelModule(self) -> bool:
        if importlib.util.find_spec("lcars.core.kernel") is None:
            self.Report.Errors.append("Kernel module is not mapped.")
            return False
        from lcars.core.kernel import Kernel

        print(">> LCARS KERNEL WAKE: START")
        KernelNode = Kernel()
        KernelStarted = KernelNode.Boot()
        if not KernelStarted:
            self.Report.Errors.append("Kernel boot failed.")
            return False
        print(">> LCARS KERNEL WAKE: READY")
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
        if importlib.util.find_spec("lcars.system.security") is None:
            self.Report.Errors.append("Security module is not mapped.")
            return False
        from lcars.system.security import AuthManager

        self.Context["AuthManager"] = AuthManager()
        self.Context["ServiceChannelsReady"] = True
        ODN.Emit("Services.Prepare", {"Source": "SystemInitializer"})
        self.Report.Details.append("[OK] SERVICE CHANNELS CONNECTED")
        return True

    def CheckNetworkSubsystem(self) -> bool:
        if importlib.util.find_spec("lcars.modules.net") is None:
            self.Report.Errors.append("Network module is not mapped.")
            return False
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


class SystemInit(SystemInitializer):
    def initialize(self, headless: bool = False) -> bool:
        return self.Execute()

    def GetReport(self) -> Dict[str, Any]:
        return self.GetReport()


SystemInitNode: SystemInit | None = None


def GetSystemInit() -> SystemInit:
    global SystemInitNode
    if SystemInitNode is None:
        SystemInitNode = SystemInit(ProgressCallback=None)
    return SystemInitNode


def InitializeSystem(headless: bool = False) -> bool:
    return GetSystemInit().initialize(headless)


def InitializeSystem(ProgressCallback: Callable[[str, int], None] | None = None) -> bool:
    Initializer = SystemInitializer(ProgressCallback)
    return Initializer.Execute()


def CreateInitializer(ProgressCallback: Callable[[str, int], None] | None = None) -> SystemInitializer:
    return SystemInitializer(ProgressCallback)


class BootManager(threading.Thread):
    STAGES = ["INIT", "FIRMWARE", "KERNEL", "SERVICES", "UI", "READY"]

    def __init__(self, config=None):
        super().__init__()
        self.BootStageChanged = Transmission(str, dict)
        self.SystemReady = Transmission(dict)
        self.Config = config or {}
        self.CurrentStage = 0
        self.Target = self.Config.get("target", "desktop")
        self.SkipFirmware = self.Config.get("skip_firmware", False)
        self.Firmware = None
        ODN.EventBus.On("Firmware.BootSelected", self.OnFirmwareBootSelected)
        ODN.EventBus.On("BIOS.SaveAndExit", self.OnBiosExit)

    def run(self):
        self.RunSequence()

    def AdvanceStage(self, StageName: str):
        self.CurrentStage = self.STAGES.index(StageName) if StageName in self.STAGES else self.CurrentStage
        self.BootStageChanged.Emit(StageName, {"Stage": StageName})

    def RunSequence(self):
        Initializer = GetSystemInit()
        if not Initializer.Execute():
            ODN.Emit("System.Init.Failed", Initializer.GetReport())
            return
        if not self.SkipFirmware:
            self.AdvanceStage("FIRMWARE")
            self.LaunchFirmware()
            return
        self.LoadCoreChain()

    def LoadCoreChain(self):
        self.AdvanceStage("KERNEL")
        self.LoadKernel()
        self.AdvanceStage("SERVICES")
        self.StartServices()
        self.AdvanceStage("UI")
        self.LaunchUi()
        self.AdvanceStage("READY")
        self.SystemReady.Emit({"Stage": "READY"})

    def LaunchFirmware(self):
        self.LoadCoreChain()

    def LoadKernel(self):
        return True

    def StartServices(self):
        return True

    def LaunchUi(self):
        ODN.Emit("System.Phase.Desktop")
        return True

    def OnFirmwareBootSelected(self, *Args, **Kwargs):
        self.LoadCoreChain()

    def OnBiosExit(self, *Args, **Kwargs):
        self.SkipFirmware = True
        self.LoadCoreChain()


class LCARSBootloader(BootManager):
    pass
