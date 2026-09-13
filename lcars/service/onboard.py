# ◤ LCARS ONBOARD INTELLIGENCE & DEPLOYMENT SYSTEM // TITANIUM ARCHITECTURE 🖖
# =============================================================================
# ФАЙЛ: lcars/service/onboard.py
# ОПИС: Служба розгортання та інтелектуального керування бортовим комп'ютером зорельота.
#       Забезпечує активацію та розгортання графічних станцій (PADD, чіпи 05-0000–05-0049),
#       пряму інтеграцію з мовним ядром комп'ютера (BoardComputer)
#       та виконання голосових і консольних директив командира.
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure LCARS Classes).
# =============================================================================
from __future__ import annotations
from lcars.core.computer import BoardComputer, SubsystemState, ProcessorState
from lcars.base.type import LCARS

from lcars.base.interface import PADD
from lcars.engineering.telemetry import EmitTelemetry

# Головна служба розгортання та інтелектуального керування бортом
class OnboardDeployment(LCARS):
    Name = "onboard"
    ActiveDeployment = None

    def __init__(self):
        super().__init__(Id="Service.Onboard")
        OnboardDeployment.ActiveDeployment = self
        self.ComputerCore = BoardComputer.GetInstance()
        self.PaddInstance: PADD | None = None
        self.ActiveChipId = "05-0000"
        self.App = None
        self.Authorized = False
        self.SecurityLevel = 4
        EmitTelemetry("OnboardDeployment", "ONBOARD INTELLIGENCE & DEPLOYMENT HOST INITIALIZED.")

    @classmethod
    def GetDeployment(cls) -> "OnboardDeployment":
        if cls.ActiveDeployment is None:
            cls.ActiveDeployment = OnboardDeployment()
        return cls.ActiveDeployment

    # Повна системна ініціалізація та послідовність завантаження
    def RunBootSequence(self) -> None:
        print("=" * 72)
        print("[*] LCARS SYSTEM BOOT SEQUENCE // STARFLEET COMMAND OS 5.0")
        print("=" * 72)
        print(f"SHIP REGISTRY: {self.ComputerCore.ShipRegistry} // {self.ComputerCore.ShipClass.upper()}")
        print(f"STARDATE: {self.ComputerCore.GetStardate()} | RUNTIME: {self.ComputerCore.RuntimeMode}")
        print("-" * 72)
        print(">> [1/4] OPTICAL SENSORY GRID & EPS CONDUITS ........... [ ONLINE ]")
        print(">> [2/4] QUANTUM FLUX MATRIX & SUPERPOSITION ........... [ 99.98% COHERENCE ]")
        print(">> [3/4] ISOLINEAR DATA CHIPS (05-0000 - 05-0049) ...... [ SYNCHRONIZED ]")
        print(f">> [4/4] COMMAND CLEARANCE LEVEL {self.SecurityLevel} .................. [ GRANTED ]")
        print("=" * 72)
        self.Authorized = True
        EmitTelemetry("OnboardDeployment", "BOOT SEQUENCE COMPLETED. COMMAND CLEARANCE GRANTED.")

    # Розгортання повноцінного графічного інтерфейсу терміналу зорельота
    def Deploy(self, ChipId: str = "05-0000", Title: str = "LCARS ONBOARD STATION // NCC-74205") -> None:
        self.RunBootSequence()
        self.ActiveChipId = str(ChipId)

        ApplicationType = LCARS.Application
        if ApplicationType and hasattr(ApplicationType, "instance"):
            self.App = ApplicationType.instance()
            if self.App is None:
                Sys = LCARS.System.Core
                ArgvList = getattr(Sys, "argv", []) if Sys else []
                self.App = ApplicationType(ArgvList)

        # FontSetup()

        self.PaddInstance = PADD(
            Title=Title,
            Width=1024,
            Height=768,
            Decorated=False,
        )

        self.PaddInstance.LoadChip(self.ActiveChipId)
        self.PaddInstance.Show()
        EmitTelemetry("OnboardDeployment", f"STATION DEPLOYED WITH CHIP {self.ActiveChipId}. FULL INTERFACE ACTIVE.")

    # Інтелектуальна обробка команд командира та динамічна перебудова екрану
    def Command(self, DirectiveText: str) -> str:
        Text = str(DirectiveText or "").strip()
        if not Text:
            return "LCARS INTELLIGENCE: STANDING BY."

        LowerText = Text.lower()

        # 1. Задачі розробки, роботи з файлами чи кодом делегуються Copilot (Builder Agent)
        CodeKeywords = ("файл", "директор", "код", "проект", "зроби", "напиши", "виправи", "зміни",
                        "readfile", "writefile", "editfile", "list", "search", "copilot", "agent")
        if any(kw in LowerText for kw in CodeKeywords):
            from lcars.service.copilot import GetAgent
            Agent = GetAgent(BoardComputer=self.ComputerCore)
            if Agent is not None:
                return Agent.Think(Text)

        # 2. Загальні системні директиви зорельота виконуються через BoardComputer
        Response = self.ComputerCore.ProcessVoiceDirective(Text)
        if isinstance(Response, dict):
            return Response.get("Message", str(Response))
        return str(Response)

    # Запуск головного циклу обробки подій
    def Run(self) -> int:
        if self.App and hasattr(self.App, "exec"):
            return self.App.exec()
        return 0

# Інтелектуальний сервісний адаптер
class OnboardSubsystem(LCARS):
    @staticmethod
    def DeployStation(ChipId: str = "05-0000"):
        Deployment = OnboardDeployment.GetDeployment()
        Deployment.Deploy(ChipId)
        return Deployment.Run()

    @staticmethod
    def Start(ChipId: str = "05-0000"):
        return OnboardSubsystem.DeployStation(ChipId)

    @staticmethod
    def Ask(PromptText: str) -> str:
        Deployment = OnboardDeployment.GetDeployment()
        return Deployment.Command(PromptText)

Computer = BoardComputer

__all__ = [
    "BoardComputer",
    "Computer",
    "SubsystemState",
    "ProcessorState",
    "OnboardDeployment",
    "OnboardSubsystem",
]

