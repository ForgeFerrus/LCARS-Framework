# BOARD COMPUTER CORE
# Центральний бортовий вузол LCARS.
#
# Цей модуль тримає:
# - системні метрики;
# - стан тривоги;
# - канали Compiler -> Console -> Terminal;
# - локальний AI fallback;
# - сумісні обгортки для старого коду.
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from lcars.base.type import LCARS, SystemComponent
from lcars.core.kernel import EventBus
from lcars.core.signal import Transmission
from lcars.engineering.collector import CollectorInstance
from lcars.engineering.telemetry import EmitTelemetry
from lcars.modules.net import NetworkManager
from lcars.service.provider import AIProviderManager
from lcars.system.alert import AlertSystem

Copilot = None
ComputerInstance = None


# Бортовий комп'ютер є системним компонентом з повним стеком каналів
class BoardComputer(SystemComponent):
    def __init__(self, ParentNode=None):
        super().__init__(ParentNode)
        self.name = "BoardComputer"
        self.version = "4.0"
        self.Version = self.version
        self.StartTimeNode = datetime.now()
        self.EventBusNodeRef = EventBus()
        self.AlertSystemNodeRef = AlertSystem()
        self.AlertSystemNodeRef.Init(self.EventBusNodeRef)
        self.SystemMetricsMap: Dict[str, Any] = {}
        self.MetricsSignal = Transmission("MetricsUpdate")
        self.aiProvider = None
        self.aiInitialized = False
        self.UseExternalAI = False
        self.PreferredAIBackend = "LOCAL"
        self.agent = None
        self.isolinearBank = None
        self.actionCenter = None
        self.autopilot = None
        self.subsystems: Dict[str, Any] = {}
        self.Compiler = None
        self.ConsoleService = None
        self.Terminal = None
        self.ActiveApplicationsMap: Dict[str, Any] = {}
        self.CurrentAppID: Optional[str] = None
        self.MainViewportNode: Optional[Any] = None
        self.Desktop: Optional[Any] = None
        self.Network = NetworkManager()
        self.Network.AddToAllowlist("google.com")
        self.Network.AddToAllowlist("startpage.com")
        if not self.SystemMetricsMap:
            self.SystemMetricsMap = CollectorInstance.GetAll()
        EmitTelemetry("BoardComputer", "TASK: COMMAND CORE INITIALIZED. Event Bus & Alert System linked.")

    # Оновлює внутрішню карту метрик з переданих даних
    def UpdateIncomingMetrics(self, DataMap: dict):
        self.SystemMetricsMap = dict(DataMap or {})

    # Повертає поточні метрики бортового комп'ютера
    def SystemMetrics(self) -> dict:
        MetricsNode = self.SystemMetricsMap or CollectorInstance.GetAll()
        return MetricsNode if isinstance(MetricsNode, dict) else {}

    # Отримання системних метрик через адаптер
    def GetSystemMetrics(self):
        return self.SystemMetrics()

    # Будує мінімальний словник layout-вузлів для PADD/desktop контейнера
    def BuildInterfaceLayout(self, ParentMatrix: Any) -> dict:
        Chassis = getattr(LCARS, "Chassis", None)
        Visual = getattr(LCARS, "Visual", None)
        if Chassis is None or Visual is None:
            return {"Error": "CHASSIS_OR_VISUAL_OFFLINE"}
        LayoutConfigMap = {}
        MainLayoutNode = Chassis.Vertical(ParentMatrix)
        MainLayoutNode.setContentsMargins(0, 0, 0, 0)
        HeaderFrameNode = LCARS.Panel(Parent=ParentMatrix)
        HeaderFrameNode.setFixedHeight(60)
        HeaderLayoutNode = Chassis.Horizontal(HeaderFrameNode)
        TitleLabelNode = Visual.Label("LCARS COMMAND INTERFACE // BOARD COMPUTER", parent=HeaderFrameNode)
        HeaderLayoutNode.addWidget(TitleLabelNode)
        BodyFrameNode = LCARS.Panel(Parent=ParentMatrix)
        BodyLayoutNode = Chassis.Horizontal(BodyFrameNode)
        SidebarFrameNode = LCARS.Panel(Parent=BodyFrameNode)
        SidebarFrameNode.setMinimumWidth(180)
        SidebarLayoutNode = Chassis.Vertical(SidebarFrameNode)
        ViewportFrameNode = LCARS.Panel(Parent=BodyFrameNode)
        BodyLayoutNode.addWidget(SidebarFrameNode)
        BodyLayoutNode.addWidget(ViewportFrameNode, 1)
        MainLayoutNode.addWidget(HeaderFrameNode)
        MainLayoutNode.addWidget(BodyFrameNode, 1)
        LayoutConfigMap.update({
            "MainLayout": MainLayoutNode,
            "HeaderFrame": HeaderFrameNode,
            "SidebarFrame": SidebarFrameNode,
            "SidebarLayout": SidebarLayoutNode,
            "ViewportFrame": ViewportFrameNode,
            "BodyFrame": BodyFrameNode,
            "TitleLabel": TitleLabelNode,
        })
        return LayoutConfigMap

    # Повертає зведення по стану борту
    def SystemSummary(self) -> dict:
        MetricsArray = self.SystemMetrics()
        UptimeDeltaNode = datetime.now() - self.StartTimeNode
        alert_level = getattr(self.AlertSystemNodeRef, "TacticalLevel", None)
        if alert_level is not None and hasattr(alert_level, "name"):
            alert_level = alert_level.name
        else:
            alert_level = "NORMAL"
        return {
            "uptime": str(UptimeDeltaNode).split(".")[0],
            "alert": f"CONDITION {alert_level}",
            "cpu": f"{MetricsArray.get('load', 0)}%",
            "mem": f"{MetricsArray.get('memory', 0)}%",
            "odn_status": "ONLINE",
        }

    # Отримання зведення по стану борту
    def GetSystemSummary(self):
        return self.SystemSummary()

    # Встановлення рівня тривоги
    def SetAlertLevel(self, TargetLevelNode: str | int):
        self.AlertSystemNodeRef.SetAlertLevel(TargetLevelNode)

    # Отримання поточного стану тривоги
    def GetAlertState(self) -> dict:
        level = getattr(self.AlertSystemNodeRef, "TacticalLevel", None)
        return {
            "state": level.name if level is not None else "UNKNOWN",
            "code": getattr(level, "value", None),
        }

    # Отримання діагностичних даних ядра
    def GetCoreDiagnostics(self) -> dict:
        return {
            "metrics": self.SystemMetrics(),
            "uptime": self.SystemSummary().get("uptime", "0:00:00"),
            "alerts": self.GetAlertState(),
            "nexus": "connected" if self.EventBusNodeRef else "disconnected",
        }

    # Збір стандартного ланцюга ядра (Compiler -> Console -> Terminal)
    def AssembleChannels(self, InitAI: bool = False):
        if self.ConsoleService is not None and self.Compiler is not None and self.Terminal is not None:
            return self
        from lcars.system.compiler import UniversalCompiler
        from lcars.service.console import LCARSConsole, ConsoleTerminal
        self.Compiler = UniversalCompiler()
        self.Compiler.board_computer = self
        self.ConsoleService = LCARSConsole(BoardComputer=self, Compiler=self.Compiler)
        self.Terminal = ConsoleTerminal(self.ConsoleService)
        if InitAI:
            self.InitializeAIProvider()
        return self

    # Дає терміналу вже створений бортовий контекст
    def AttachTerminal(self, TerminalNode) -> bool:
        if TerminalNode is None:
            return False
        self.Terminal = TerminalNode
        if getattr(TerminalNode, "BoardComputer", None) is not self:
            TerminalNode.BoardComputer = self
        if getattr(TerminalNode, "Console", None) is None and self.ConsoleService is not None:
            TerminalNode.Console = self.ConsoleService
        return True

    # Передає команду в центральну консоль
    def ProcessCommand(self, CommandStr: str) -> str:
        if self.ConsoleService is None:
            self.AssembleChannels(InitAI=False)
        Lines = []
        self.ConsoleService.Execute(CommandStr, Lines.append)
        return "\n".join(Lines) if Lines else "\u25e7 ERROR: VOID_INPUT"

    # Ініціалізація AI-провайдера
    def InitializeAIProvider(self):
        if self.aiProvider is None:
            self.aiProvider = AIProviderManager()
            self.aiProvider.initialize()
            self.aiInitialized = getattr(self.aiProvider, "activeBackend", None) is not None

    # Отримання AI-провайдера з lazy-ініціалізацією
    def GetAI(self):
        if self.aiProvider is None:
            self.InitializeAIProvider()
        return self.aiProvider

    getAI = GetAI

    # Повертає живого Copilot-агента для мислення і tool-based виконання
    def GetAgent(self):
        if self.agent is None:
            from lcars.service.copilot import Copilot
            self.agent = Copilot(projectRoot=str(Path(__file__).resolve().parents[2]), boardComputer=self)
            self.agent.initialize()
        return self.agent

    getAgent = GetAgent

    # Перевірка чи є відповідь провайдера fallback-повідомленням
    def IsProviderFallback(self, response: str) -> bool:
        Text = str(response).strip().lower()
        Markers = ("[ai:", "[mistral", "[localllm", "[gemma", "[groq", "[model ", "provider offline")
        return not Text or Text.startswith(Markers)

    # Локальна інтелектуальна відповідь без зовнішнього AI
    def LocalIntelligence(self, prompt: str) -> str:
        Text = str(prompt or "").strip().lower()
        Console = self.ConsoleService
        Mode = getattr(Console, "ActiveMode", "OPTICAL") if Console is not None else "OPTICAL"
        if any(Item in Text for Item in ("status", "стан", "diagnostic", "діагностик")):
            Summary = self.SystemSummary()
            return (
                "BOARD INTELLIGENCE: ACTIVE\n"
                "CORE: ONLINE\n"
                f"ODN: {str(Summary.get('odn_status', 'ONLINE')).upper()}\n"
                f"MODE: {str(Mode).upper()}\n"
                f"ALERT: {str(Summary.get('alert', 'GREEN')).upper()}"
            )
        if "quantum" in Text or "квант" in Text:
            return "BOARD INTELLIGENCE: QUANTUM CHANNEL READY. Use MODE QUANTUM to switch runtime state."
        if "optical" in Text or "normal" in Text or "звичай" in Text:
            return "BOARD INTELLIGENCE: OPTICAL CHANNEL READY. Use MODE OPTICAL to switch runtime state."
        if "help" in Text or "допом" in Text or "команд" in Text:
            return "BOARD INTELLIGENCE: STATUS | MODE OPTICAL | MODE QUANTUM | COMPILE | RUN | HELP"
        if "who are you" in Text or "хто ти" in Text:
            return "I AM THE LCARS BOARD COMPUTER. CORE, ODN, RUNTIME AND TERMINAL ARE LINKED."
        return "BOARD INTELLIGENCE: REQUEST RECEIVED. CORE IS ONLINE; use STATUS for diagnostics or HELP for available directives."

    # Запит до AI з використанням провайдера або локальної відповіді
    def AskAI(self, prompt: str, context: str = "") -> str:
        if not self.UseExternalAI:
            if self.agent is None:
                self.GetAgent()
            if self.agent is not None:
                response = self.agent.run(prompt, role="commander")
                if response:
                    return response
            return self.LocalIntelligence(prompt)
        provider = self.GetAI()
        if provider is None:
            return self.LocalIntelligence(prompt)
        response = provider.ask(prompt, context)
        if response and not self.IsProviderFallback(response):
            return response
        return self.LocalIntelligence(prompt)

    askAI = AskAI

    # Отримання повного статусу системи
    def GetSystemStatus(self) -> dict:
        ac = self.GetActionCenter()
        ai = self.GetAI()
        bank = self.GetIsolinearBank()
        tasks = ac.getStats() if ac is not None and hasattr(ac, "getStats") else {}
        return {
            "name": self.name,
            "version": self.version,
            "ai_available": bool(ai and getattr(ai, "activeBackend", None) is not None),
            "database_chips": len(getattr(bank, "Chips", [])) if bank else 0,
            "tasks": tasks,
            "subsystems": list(self.subsystems.keys()),
            "mode": getattr(self.ConsoleService, "ActiveMode", "OPTICAL") if self.ConsoleService else "OPTICAL",
        }

    getSystemStatus = GetSystemStatus

    # Отримання ізолінійного банку даних
    def GetIsolinearBank(self):
        if self.isolinearBank is None:
            from lcars.modules.library import IsolinearBank
            self.isolinearBank = IsolinearBank("database")
            self.isolinearBank.LoadBanks("federation")
        return self.isolinearBank

    getIsolinearBank = GetIsolinearBank

    # Отримання центру дій (Action Center)
    def GetActionCenter(self):
        if self.actionCenter is None:
            from lcars.engineering.controller import getEngineeringController
            self.actionCenter = getEngineeringController()
        return self.actionCenter

    getActionCenter = GetActionCenter

    # Створення інженерного завдання
    def CreateEngineeringTask(self, taskId: str, title: str, description: str, priority: str = "MEDIUM", assignedTo: str = None) -> dict:
        ac = self.GetActionCenter()
        if ac is None:
            return {"error": "Action Center is offline"}
        from lcars.engineering.controller import TaskPriority
        prio = getattr(TaskPriority, priority.upper(), TaskPriority.MEDIUM)
        task = ac.createTask(taskId, title, description, prio, assignedTo)
        return task.toDict()

    createEngineeringTask = CreateEngineeringTask

    # Активація autopilot-режиму з Copilot-агентом
    def EnableAutopilot(self) -> str:
        if self.autopilot is None:
            global Copilot
            if Copilot is None:
                from lcars.service.copilot import Copilot as CopilotClass
                Copilot = CopilotClass
            project_root = Path(__file__).resolve().parents[2]
            self.autopilot = Copilot(projectRoot=project_root)
            EmitTelemetry("Autopilot", "AUTOPILOT ENGINE ONLINE AND LINKED TO BOARD COMPUTER.")
            return "\u25e7 AUTOPILOT ENABLED"
        return "\u25e7 AUTOPILOT ALREADY ONLINE"

    enableAutopilot = EnableAutopilot

    # Запуск інтерактивного терміналу з виводом статусу
    def RunTerminal(self, InitAI: bool = True):
        self.AssembleChannels(InitAI=InitAI)
        print("=" * 70)
        print("LCARS ONBOARD — BOARD COMPUTER")
        print("=" * 70)
        print("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("CHANNELS: COMPILER -> CONSOLE -> TERMINAL -> ONBOARD")
        print("[OK] Compiler: " + type(self.Compiler).__name__)
        print("[OK] Console:  " + self.ConsoleService.Version)
        print("[OK] Terminal: " + self.Terminal.Name)
        print("[OK] Onboard:  BoardComputer v" + str(self.version))
        AiStatus = "ONLINE" if self.aiInitialized else "OFFLINE"
        print("[" + AiStatus + "] AI Provider")
        print()
        print("READY — HELP | EXIT  //  THINK: ai <prompt>")
        print("=" * 70)
        print()
        while True:
            Mode = self.ConsoleService.ActiveMode.upper()
            Cmd = input("LCARS[" + Mode + "]> ").strip()
            if not Cmd:
                continue
            if Cmd.upper() in ("EXIT", "QUIT"):
                print("[SHUTDOWN] Onboard session end")
                break
            Lines = []
            self.Terminal.Execute(Cmd, Lines.append)
            if Lines:
                for Line in Lines:
                    print(Line)
            else:
                print("[INFO] No output")
            print()
        print("[DONE]")


# Отримання або створення singleton-екземпляра BoardComputer
def Computer() -> BoardComputer:
    global ComputerInstance
    if ComputerInstance is None:
        ComputerInstance = BoardComputer()
    return ComputerInstance


GetComputer = Computer


# Обгортка-синглтон для BoardComputer
class OnboardComputer:
    def __new__(cls):
        return Computer()

    # Отримання шини подій бортового комп'ютера
    @staticmethod
    def EventBus():
        return Computer().EventBusNodeRef

    # Отримання системи тривог бортового комп'ютера
    @staticmethod
    def AlertSystem():
        return Computer().AlertSystemNodeRef

    # Отримання шини подій через BoardComputer
    @staticmethod
    def GetEventBus():
        return BoardComputer.EventBus()

    # Отримання системи тривог через BoardComputer
    @staticmethod
    def GetAlertSystem():
        return BoardComputer.AlertSystem()

    GetComputer = Computer

    # Отримання AI-провайдера
    @staticmethod
    def GetAI():
        return Computer().GetAI()

    getAI = GetAI

    # Запит до AI
    @staticmethod
    def AskAI(prompt: str, context: str = "") -> str:
        return Computer().AskAI(prompt, context)

    askAI = AskAI

    # Отримання статусу системи
    @staticmethod
    def GetSystemStatus() -> dict:
        return Computer().GetSystemStatus()

    getSystemStatus = GetSystemStatus
