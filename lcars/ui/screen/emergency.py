from __future__ import annotations

import sys
import textwrap
from pathlib import Path
from importlib.util import find_spec

ProjectRoot = Path(__file__).resolve().parents[3]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from lcars.base.component import DataBlock, LCARSBar, LCARSButton, LCARSElbow, LCARSLabel
from lcars.base.default import Palette
from lcars.base.interface import Screen, Segment
from lcars.base.type import LCARS
from lcars.core.signal import ODN
from lcars.system import emergency as EmergencySystem

# Аварійний екран живе тут.
# У цьому файлі тільки візуальний шар і поведінка екрана.
# Логіка запуску та маршрутизація залишаються в lcars.system.emergency.


 # Аварійний екран лишається візуальним шаром.
 # Низинні операції з ремонту, відновлення й діагностики живуть у `lcars.system.emergency`.


class EmergencyMode(Screen):
    def __init__(self, Parent=None, Context=None):
        self.Context = Context or {}
        self.BoardComputer = None
        self.LogLines = []
        self.MaxLines = 140
        self.StageIndex = 0
        self.StageNames = ["CORE", "ODN", "BIOS", "KERNEL", "SYSTEM"]
        self.LeftButtons = {}
        self.VisibleLayers = []
        self.KernelAuditCache = {}
        super().__init__(Parent=Parent)
        self.widget.setStyleSheet("background-color: #000000; border: none;")
        self.ApplyContext(self.Context)
        self.ShowBootState()

    # Головний каркас: верхня смуга, три зони, нижній статус.
    def BuildInterface(self):
        Root = LCARS.Vertical(self.widget)
        Root.setContentsMargins(18, 18, 18, 18)
        Root.setSpacing(10)

        self.Header = Segment(Parent=self.widget)
        HeaderLayout = LCARS.Horizontal(self.Header.widget)
        HeaderLayout.setContentsMargins(0, 0, 0, 0)
        HeaderLayout.setSpacing(8)

        self.HeaderCap = LCARSElbow(Direction="top-left", Color=Palette.Buttons[0], Parent=self.Header.widget)
        self.HeaderCap.widget.setFixedSize(92, 42)
        HeaderLayout.addWidget(self.HeaderCap.widget)

        self.HeaderTitle = LCARSLabel(
            Text="LCARS EMERGENCY MATRIX",
            Color=Palette.Buttons[2],
            FontSize=22,
            Parent=self.Header.widget,
        )
        self.HeaderTitle.widget.setStyleSheet("background-color: transparent; border: none;")
        HeaderLayout.addWidget(self.HeaderTitle.widget, 1)

        self.HeaderRoute = LCARSLabel(
            Text="ROUTE: EMERGENCY",
            Color=Palette.Background,
            FontSize=14,
            Parent=self.Header.widget,
        )
        self.HeaderRoute.widget.setFixedHeight(42)
        self.HeaderRoute.widget.setStyleSheet(
            "background-color: " + Palette.Buttons[0] + "; color: #000000; padding: 8px 14px;"
        )
        HeaderLayout.addWidget(self.HeaderRoute.widget)

        self.HeaderMode = LCARSLabel(
            Text="OVERRIDE ACTIVE",
            Color=Palette.Background,
            FontSize=14,
            Parent=self.Header.widget,
        )
        self.HeaderMode.widget.setFixedHeight(42)
        self.HeaderMode.widget.setStyleSheet(
            "background-color: " + Palette.RedAlert[0] + "; color: #000000; padding: 8px 14px;"
        )
        HeaderLayout.addWidget(self.HeaderMode.widget)
        Root.addWidget(self.Header.widget)

        self.StageStrip = Segment(Parent=self.widget)
        StageLayout = LCARS.Horizontal(self.StageStrip.widget)
        StageLayout.setContentsMargins(0, 0, 0, 0)
        StageLayout.setSpacing(10)
        self.StageChips = []
        for Index, Name in enumerate(self.StageNames):
            Chip = LCARSLabel(Text=Name, Color=Palette.Panels[2], FontSize=15, Parent=self.StageStrip.widget)
            Chip.widget.setFixedHeight(34)
            Chip.widget.setStyleSheet(
                "background-color: #000000; color: "
                + Palette.Panels[2]
                + "; border: 1px solid "
                + Palette.Panels[Index % len(Palette.Panels)]
                + "; border-radius: 16px; padding: 6px 12px;"
            )
            self.StageChips.append(Chip)
            StageLayout.addWidget(Chip.widget)
        StageLayout.addStretch(1)
        self.StageBar = LCARSBar(Type="scanning", Color=Palette.Panels[2], Parent=self.StageStrip.widget, Height=10)
        self.StageBar.widget.setMinimumHeight(10)
        self.StageBar.widget.setStyleSheet("background-color: transparent; border: none;")
        StageLayout.addWidget(self.StageBar.widget)
        Root.addWidget(self.StageStrip.widget)

        Body = LCARS.Horizontal(self.widget)
        Body.setSpacing(12)
        Root.addLayout(Body, 1)

        self.LeftRail = Segment(Parent=self.widget)
        self.LeftRail.widget.setFixedWidth(250)
        LeftLayout = LCARS.Vertical(self.LeftRail.widget)
        LeftLayout.setContentsMargins(0, 0, 0, 0)
        LeftLayout.setSpacing(8)

        self.LeftTop = LCARSElbow(Direction="top-left", Color=Palette.RedAlert[0], Parent=self.LeftRail.widget)
        self.LeftTop.widget.setFixedHeight(84)
        LeftLayout.addWidget(self.LeftTop.widget)

        self.LeftButtons = {}
        ActionSet = [
            ("AUTO FIX", self.RunAutoFix, Palette.Buttons[0]),
            ("RECOVERY", self.RunRecovery, Palette.Buttons[1]),
            ("LIFE SUPPORT", self.RunLifeSupport, Palette.Buttons[2]),
            ("KERNEL", self.RunKernelAudit, Palette.Panels[0]),
            ("SERVICES", self.RunServiceAudit, Palette.Panels[1]),
            ("PROCESSES", self.RunProcessAudit, Palette.Panels[2]),
            ("MODULES", self.RunModuleAudit, Palette.Buttons[4]),
            ("AI", self.RunAIAudit, Palette.Buttons[5]),
            ("BIOS", self.LaunchBios, Palette.Buttons[3]),
            ("ACCESS", self.LaunchAccess, Palette.Buttons[4]),
            ("DESKTOP", self.LaunchDesktop, Palette.Buttons[5]),
            ("REBOOT", self.RebootSystem, Palette.YellowAlert[1]),
            ("POWER", self.PowerDown, Palette.RedAlert[0]),
        ]
        for Text, Handler, Color in ActionSet:
            Button = LCARSButton(Text=Text, Type="soft-right", Color=Color, Parent=self.LeftRail.widget)
            if hasattr(Button, "Clicked"):
                Button.Clicked.Connect(Handler)
            else:
                Button.widget.clicked.connect(Handler)
            LeftLayout.addWidget(Button.widget)
            self.LeftButtons[Text] = Button

        LeftLayout.addSpacing(10)
        LeftLayout.addWidget(
            DataBlock("SYSTEM VITALITY", "EMERGENCY", Palette.RedAlert[1], Parent=self.LeftRail.widget).widget
        )
        LeftLayout.addWidget(
            DataBlock("BOARD COMPUTER", "OFFLINE", Palette.Buttons[2], Parent=self.LeftRail.widget).widget
        )
        LeftLayout.addStretch(1)

        self.LeftBottom = LCARSElbow(Direction="bottom-left", Color=Palette.RedAlert[0], Parent=self.LeftRail.widget)
        self.LeftBottom.widget.setFixedHeight(61)
        LeftLayout.addWidget(self.LeftBottom.widget)
        Body.addWidget(self.LeftRail.widget)

        self.CenterRail = Segment(Parent=self.widget)
        CenterLayout = LCARS.Vertical(self.CenterRail.widget)
        CenterLayout.setContentsMargins(0, 0, 0, 0)
        CenterLayout.setSpacing(8)

        self.CenterHeader = LCARSLabel(
            Text="EMERGENCY CONSOLE / BOOT LOG",
            Color=Palette.Buttons[2],
            FontSize=18,
            Parent=self.CenterRail.widget,
        )
        self.CenterHeader.widget.setStyleSheet("background-color: transparent; border: none;")
        CenterLayout.addWidget(self.CenterHeader.widget)

        self.LogArea = self.BuildLogArea(self.CenterRail.widget)
        CenterLayout.addWidget(self.LogArea, 1)
        Body.addWidget(self.CenterRail.widget, 1)

        self.RightRail = Segment(Parent=self.widget)
        self.RightRail.widget.setFixedWidth(340)
        RightLayout = LCARS.Vertical(self.RightRail.widget)
        RightLayout.setContentsMargins(0, 0, 0, 0)
        RightLayout.setSpacing(8)

        self.RightHeader = LCARSLabel(
            Text="BOARD COMPUTER TERMINAL",
            Color=Palette.Panels[2],
            FontSize=18,
            Parent=self.RightRail.widget,
        )
        self.RightHeader.widget.setStyleSheet("background-color: transparent; border: none;")
        RightLayout.addWidget(self.RightHeader.widget)

        self.BoardCard = self.BuildBoardCard(self.RightRail.widget)
        RightLayout.addWidget(self.BoardCard, 1)
        Body.addWidget(self.RightRail.widget)

        self.Footer = Segment(Parent=self.widget)
        FooterLayout = LCARS.Horizontal(self.Footer.widget)
        FooterLayout.setContentsMargins(0, 0, 0, 0)
        FooterLayout.setSpacing(8)

        self.FooterStatus = LCARSLabel(
            Text="EMERGENCY OVERRIDE READY",
            Color=Palette.Buttons[2],
            FontSize=14,
            Parent=self.Footer.widget,
        )
        self.FooterStatus.widget.setFixedHeight(30)
        self.FooterStatus.widget.setStyleSheet("background-color: transparent; border: none;")
        FooterLayout.addWidget(self.FooterStatus.widget, 1)

        self.FooterBar = LCARSBar(Type="rect", Color=Palette.RedAlert[1], Parent=self.Footer.widget, Width=120, Height=30)
        self.FooterBar.widget.setFixedWidth(120)
        self.FooterBar.widget.setFixedHeight(30)
        FooterLayout.addWidget(self.FooterBar.widget)
        Root.addWidget(self.Footer.widget)

        self.WriteLine("EMERGENCY MODE READY.")
        self.WriteLine("LEFT ACTIONS ARE AVAILABLE.")
        self.WriteLine("TYPE HELP IN THE TERMINAL FOR COMMANDS.")

    # Логова зона має бути тихою і читабельною.
    def BuildLogArea(self, Parent):
        Box = Segment(Parent=Parent)
        Box.widget.setStyleSheet("background-color: #050505; border: 1px solid #245b8f;")
        Layout = LCARS.Vertical(Box.widget)
        Layout.setContentsMargins(12, 12, 12, 12)
        Layout.setSpacing(6)

        Header = LCARSLabel(Text="SYSTEM LOG KERNEL", Color=Palette.Buttons[1], FontSize=13, Parent=Box.widget)
        Header.widget.setStyleSheet("background-color: transparent; border: none;")
        Layout.addWidget(Header.widget)

        self.ConsoleWidget = LCARS.Terminal(Box.widget)
        self.ConsoleWidget.setReadOnly(True)
        self.ConsoleWidget.setStyleSheet(
            "background-color: #000000; color: #6FC2FF; border: none; "
            "font-family: 'Consolas', monospace; font-size: 14px;"
        )
        Layout.addWidget(self.ConsoleWidget, 1)
        return Box.widget

    # Правий блок з терміналом борту.
    def BuildBoardCard(self, Parent):
        Box = Segment(Parent=Parent)
        Box.widget.setStyleSheet("background-color: #050505; border: 1px solid #245b8f;")
        Layout = LCARS.Vertical(Box.widget)
        Layout.setContentsMargins(12, 12, 12, 12)
        Layout.setSpacing(8)

        self.BoardStatus = LCARSLabel(
            Text="BOARD COMPUTER: OFFLINE",
            Color=Palette.RedAlert[1],
            FontSize=14,
            Parent=Box.widget,
        )
        self.BoardStatus.widget.setStyleSheet("background-color: transparent; border: none;")
        Layout.addWidget(self.BoardStatus.widget)

        self.TerminalFeed = LCARSLabel(
            Text="AWAITING INPUT",
            Color=Palette.Buttons[2],
            FontSize=14,
            Parent=Box.widget,
        )
        self.TerminalFeed.widget.setStyleSheet(
            "background-color: #000000; color: #FFB347; border: none; "
            "font-family: 'Consolas', monospace; font-size: 13px;"
        )
        Layout.addWidget(self.TerminalFeed.widget)

        self.CommandInput = LCARS.Input(Box.widget)
        self.CommandInput.setStyleSheet(
            "background-color: #111111; color: #FFFFFF; border: 1px solid #FF9900; "
            "font-family: 'Consolas', monospace; font-size: 16px; padding: 6px;"
        )
        if hasattr(self.CommandInput, "setPlaceholderText"):
            self.CommandInput.setPlaceholderText("TYPE COMMAND HERE...")
        if hasattr(self.CommandInput, "returnPressed"):
            self.CommandInput.returnPressed.connect(self.ExecuteCurrent)
        Layout.addWidget(self.CommandInput)

        self.BoardSummary = LCARSLabel(Text="", Color=Palette.Panels[2], FontSize=13, Parent=Box.widget)
        self.BoardSummary.widget.setStyleSheet("background-color: transparent; border: none;")
        Layout.addWidget(self.BoardSummary.widget, 1)

        self.BoardDetails = LCARSLabel(Text="", Color=Palette.Buttons[2], FontSize=12, Parent=Box.widget)
        self.BoardDetails.widget.setStyleSheet(
            "background-color: #000000; color: #6FC2FF; border: none; "
            "font-family: 'Consolas', monospace; font-size: 12px;"
        )
        Layout.addWidget(self.BoardDetails.widget, 1)

        return Box.widget

    # Поступове відкриття екрану робить аварійку живою, а не плоскою.
    def showEvent(self, event):
        if hasattr(self, "RevealTimer"):
            return
        self.RevealStep = 0
        self.HideLayer(self.LeftRail)
        self.HideLayer(self.RightRail)
        self.HideLayer(self.Footer)
        self.RevealTimer = LCARS.Timer(self.widget)
        self.RevealTimer.setSingleShot(False)
        self.RevealTimer.setInterval(90)
        self.RevealTimer.timeout.connect(self.RevealNextLayer)
        self.RevealTimer.start(90)

    def HideLayer(self, Layer):
        if Layer is None:
            return
        Surface = getattr(Layer, "widget", Layer)
        if hasattr(Surface, "hide"):
            Surface.hide()

    def ShowLayer(self, Layer):
        if Layer is None:
            return
        Surface = getattr(Layer, "widget", Layer)
        if hasattr(Surface, "show"):
            Surface.show()

    def RevealNextLayer(self):
        if self.RevealStep == 0:
            self.ShowLayer(self.LeftRail)
            self.WriteLine("LEFT ACTION RAIL ONLINE.")
        elif self.RevealStep == 1:
            self.ShowLayer(self.RightRail)
            self.WriteLine("BOARD TERMINAL LINK CHECKED.")
        elif self.RevealStep == 2:
            self.ShowLayer(self.Footer)
            self.WriteLine("FOOTER STATUS ONLINE.")
            if hasattr(self, "RevealTimer"):
                self.RevealTimer.stop()
        self.RevealStep += 1

    def ApplyContext(self, Context):
        Payload = Context or {}
        Error = str(Payload.get("error", "MANUAL EMERGENCY BOOT"))
        Stage = str(Payload.get("stage", "MANUAL"))
        Details = Payload.get("details", "")

        self.HeaderTitle.SetText("LCARS EMERGENCY // " + Error)
        self.HeaderRoute.SetText("ROUTE: " + Stage.upper())
        self.FooterStatus.SetText("EMERGENCY OVERRIDE GRANTED")

        self.WriteLine("!!! EMERGENCY ROUTE ACTIVE !!!")
        self.WriteLine("STAGE: " + Stage.upper())
        self.WriteLine("ERROR: " + Error)
        if Details:
            self.WriteLine("DETAILS:")
            for Line in str(Details).splitlines():
                self.WriteLine("  " + Line)

        self.WriteLine("")
        self.WriteLine("SYSTEM WILL WAIT FOR A COMMAND OR A ROUTE SWITCH.")

    def WriteLine(self, Text):
        Line = str(Text)
        self.LogLines.append(Line)
        if len(self.LogLines) > self.MaxLines:
            self.LogLines = self.LogLines[-self.MaxLines :]
        if hasattr(self.ConsoleWidget, "setPlainText"):
            self.ConsoleWidget.setPlainText("\n".join(self.LogLines))
        elif hasattr(self.ConsoleWidget, "setText"):
            self.ConsoleWidget.setText("\n".join(self.LogLines))
        elif hasattr(self.ConsoleWidget, "append"):
            self.ConsoleWidget.append(Line)

    def WriteBlock(self, Prefix, Text):
        self.WriteLine("")
        self.WriteLine("[" + str(Prefix) + "]")
        for Line in str(Text).splitlines():
            Wrapped = textwrap.wrap(Line, width=88) or [""]
            for Chunk in Wrapped:
                self.WriteLine("  " + Chunk)

    def GetBoardComputer(self):
        if self.BoardComputer is None:
            self.BoardComputer = EmergencySystem.GetBoardComputer()
        return self.BoardComputer

    def UpdateBoardState(self):
        BoardComputer = self.GetBoardComputer()
        if BoardComputer is None:
            self.BoardStatus.SetText("BOARD COMPUTER: OFFLINE")
            self.TerminalFeed.SetText("NO BOARD COMPUTER FOUND")
            self.BoardSummary.SetText("MANUAL CONTROL ONLY")
            self.BoardDetails.SetText("SYSTEM LOG AND ROUTES STILL AVAILABLE")
            return

        self.BoardStatus.SetText("BOARD COMPUTER: ONLINE")
        Summary = EmergencySystem.GetBoardSummary()
        SummaryText = "BOARD COMPUTER READY"
        if isinstance(Summary, dict) and Summary:
            SummaryText = "\n".join([str(Key).upper() + ": " + str(Value) for Key, Value in Summary.items()])
        self.BoardSummary.SetText(SummaryText)
        self.TerminalFeed.SetText("READY FOR DIRECT COMMANDS")

        Details = []
        Snapshot = EmergencySystem.BuildEmergencySnapshot(self.Context)
        KernelState = Snapshot.get("kernel", {}) if isinstance(Snapshot, dict) else {}
        if isinstance(KernelState, dict) and KernelState:
            Details.append("BOARD STATE")
            Details.append("  PHASE: " + str(KernelState.get("Phase", "UNKNOWN")))
            Services = KernelState.get("Services", {})
            if isinstance(Services, dict):
                Details.append("  SERVICES: " + ", ".join(Services.get("Registered", [])))
                Details.append("  ALERT: " + str(Services.get("Health", {})))

        CoreState = EmergencySystem.GetCoreDiagnostics()
        if isinstance(CoreState, dict) and CoreState:
            Details.append("")
            Details.append("CORE DIAGNOSTICS")
            Details.append("  UPTIME: " + str(CoreState.get("uptime", "n/a")))
            Details.append("  NEXUS: " + str(CoreState.get("nexus", "unknown")))

        AIState = EmergencySystem.GetAIStatus()
        if isinstance(AIState, dict) and AIState:
            Details.append("")
            Details.append("AI CLUSTER")
            Details.append("  ACTIVE: " + str(AIState.get("active", "none")))
            Details.append("  READY: " + str(AIState.get("is_ai", False)))
            Details.append("  INITIALIZED: " + str(AIState.get("initialized", False)))

        self.BoardDetails.SetText("\n".join(Details) if Details else "NO EXTRA BOARD DETAILS")

    def RefreshKernelAudit(self):
        from lcars.core.kernel import Kernel

        KernelNode = Kernel()
        KernelStatus = KernelNode.Status()
        self.KernelAuditCache = KernelStatus if isinstance(KernelStatus, dict) else {}
        return self.KernelAuditCache

    def ShowKernelAudit(self):
        Status = self.RefreshKernelAudit()
        if not Status:
            self.WriteLine("KERNEL AUDIT UNAVAILABLE.")
            return

        self.WriteLine("KERNEL AUDIT:")
        self.WriteLine("  PHASE: " + str(Status.get("Phase", "UNKNOWN")))
        self.WriteLine("  ENV: " + str(Status.get("Env", {})))
        Services = Status.get("Services", {})
        if isinstance(Services, dict):
            self.WriteLine("  SERVICES:")
            self.WriteLine("    REGISTERED: " + ", ".join(Services.get("Registered", [])))
            self.WriteLine("    HEALTH: " + str(Services.get("Health", {})))
        self.WriteLine("  MODULES: " + ", ".join(Status.get("Modules", [])))
        Processes = Status.get("Processes", [])
        self.WriteLine("  PROCESSES: " + str(len(Processes)))
        for Item in Processes[:10]:
            if isinstance(Item, dict):
                self.WriteLine("    " + str(Item.get("Pid", "?")) + " | " + str(Item.get("App", "?")) + " | " + str(Item.get("Title", "?")))
        self.UpdateBoardState()

    def RunKernelAudit(self):
        self.WriteLine("REQUESTING KERNEL AUDIT...")
        self.ShowKernelAudit()

    def RunServiceAudit(self):
        self.WriteLine("REQUESTING SERVICE HEALTH...")
        Health = EmergencySystem.GetServiceHealth()
        if isinstance(Health, dict) and Health:
            self.WriteBlock("SERVICE HEALTH", Health)
        else:
            self.WriteLine("SERVICE HEALTH UNAVAILABLE.")
        self.UpdateBoardState()

    def RunProcessAudit(self):
        self.WriteLine("REQUESTING PROCESS TABLE...")
        Processes = EmergencySystem.RunProcessAudit()
        self.WriteLine("PROCESSES:")
        for Item in Processes[:20]:
            if isinstance(Item, dict):
                self.WriteLine(
                    "  PID "
                    + str(Item.get("Pid", "?"))
                    + " | "
                    + str(Item.get("App", "?"))
                    + " | "
                    + str(Item.get("Title", "?"))
                )
        self.UpdateBoardState()

    def RunModuleAudit(self):
        self.WriteLine("REQUESTING MODULE INVENTORY...")
        Modules = EmergencySystem.RunModuleAudit()
        self.WriteLine("MODULES:")
        for Name in Modules:
            self.WriteLine("  " + str(Name))
        self.UpdateBoardState()

    def RunAIAudit(self):
        self.WriteLine("REQUESTING AI CLUSTER STATUS...")
        AIState = EmergencySystem.GetAIStatus()
        if not isinstance(AIState, dict) or not AIState:
            self.WriteLine("AI ROUTE UNAVAILABLE.")
            return
        self.WriteBlock("AI STATUS", AIState)
        self.UpdateBoardState()

    def ShowBoardSummary(self):
        Summary = EmergencySystem.GetBoardSummary()
        if not isinstance(Summary, dict) or not Summary:
            self.WriteLine("BOARD COMPUTER OFFLINE. MANUAL CONTROL ACTIVE.")
            self.UpdateBoardState()
            return

        self.WriteLine("BOARD COMPUTER STATUS:")
        for Key, Value in Summary.items():
            self.WriteLine("  " + str(Key).upper() + ": " + str(Value))
        self.UpdateBoardState()

    def ExecuteCurrent(self):
        if not hasattr(self.CommandInput, "text"):
            return
        Text = str(self.CommandInput.text()).strip()
        if not Text:
            return
        if hasattr(self.CommandInput, "clear"):
            self.CommandInput.clear()
        self.WriteLine("LCARS> " + Text)
        self.RunCommand(Text)

    def RunCommand(self, Text):
        Command = str(Text).strip()
        Lower = Command.lower()

        if Lower in ("clear", "cls"):
            self.LogLines = []
            if hasattr(self.ConsoleWidget, "clear"):
                self.ConsoleWidget.clear()
            self.WriteLine("CONSOLE CLEARED.")
            return

        if Lower == "help":
            self.WriteLine("AVAILABLE COMMANDS:")
            self.WriteLine("  status      - show board summary")
            self.WriteLine("  kernel      - show kernel audit")
            self.WriteLine("  services    - show service health")
            self.WriteLine("  processes   - show process table")
            self.WriteLine("  modules     - show loaded modules")
            self.WriteLine("  ai          - show AI cluster status")
            self.WriteLine("  diagnostics - run board diagnostics")
            self.WriteLine("  autofix     - request auto repair")
            self.WriteLine("  recovery    - request recovery")
            self.WriteLine("  lifesupport - request life support check")
            self.WriteLine("  desktop     - open desktop")
            self.WriteLine("  access      - open access")
            self.WriteLine("  bios        - open BIOS")
            self.WriteLine("  reboot      - reboot system")
            self.WriteLine("  power       - power down")
            self.WriteLine("  clear       - clear console")
            return

        if Lower == "status":
            self.ShowBoardSummary()
            return

        if Lower == "kernel":
            self.RunKernelAudit()
            return

        if Lower == "services":
            self.RunServiceAudit()
            return

        if Lower == "processes":
            self.RunProcessAudit()
            return

        if Lower == "modules":
            self.RunModuleAudit()
            return

        if Lower == "ai":
            self.RunAIAudit()
            return

        if Lower == "diagnostics":
            self.RunDiagnostics()
            return

        if Lower == "autofix":
            self.RunAutoFix()
            return

        if Lower == "recovery":
            self.RunRecovery()
            return

        if Lower == "lifesupport":
            self.RunLifeSupport()
            return

        if Lower == "desktop":
            self.LaunchDesktop()
            return

        if Lower == "access":
            self.LaunchAccess()
            return

        if Lower == "bios":
            self.LaunchBios()
            return

        if Lower == "reboot":
            self.RebootSystem()
            return

        if Lower == "power":
            self.PowerDown()
            return

        Result = EmergencySystem.QueryBoardComputer(Command)
        if isinstance(Result, dict):
            if str(Result.get("status", "")) == "ok":
                self.WriteBlock("AI RESPONSE", Result.get("response", ""))
            else:
                self.WriteLine(str(Result.get("response", "NO RESPONSE")))
            self.UpdateBoardState()
            return

        self.WriteLine("BOARD COMPUTER DOES NOT SUPPORT DIRECT AI QUERIES.")
        self.UpdateBoardState()

    def RunDiagnostics(self):
        self.WriteLine("RUNNING EMERGENCY DIAGNOSTICS...")
        Result = EmergencySystem.PerformDiagnostics()
        if isinstance(Result, dict) and Result:
            self.WriteBlock("DIAGNOSTIC RESULT", Result)
        else:
            self.WriteLine("NO DEDICATED DIAGNOSTIC METHOD FOUND.")
        self.UpdateBoardState()

    def RunAutoFix(self):
        self.WriteLine("REQUESTING AUTO FIX...")
        Result = EmergencySystem.PerformAutofix(self.Context)
        if Result is not None:
            self.WriteBlock("AUTO FIX", Result)
        else:
            self.WriteLine("AUTO FIX ROUTE IS NOT AVAILABLE.")
        self.UpdateBoardState()

    def RunRecovery(self):
        self.WriteLine("REQUESTING RECOVERY MODE...")
        Result = EmergencySystem.PerformRecovery()
        if Result is not None:
            self.WriteBlock("RECOVERY", Result)
        else:
            self.WriteLine("RECOVERY ROUTE IS NOT AVAILABLE.")
        self.UpdateBoardState()

    def RunLifeSupport(self):
        self.WriteLine("REQUESTING LIFE SUPPORT CHECK...")
        Result = EmergencySystem.RunLifeSupportCheck()
        if Result is not None:
            self.WriteBlock("LIFE SUPPORT", Result)
        else:
            self.WriteLine("LIFE SUPPORT ROUTE IS NOT AVAILABLE.")
        self.UpdateBoardState()

    def LaunchBios(self):
        self.WriteLine("BIOS ROUTE REQUESTED.")
        ODN.Emit("System.Phase.Bios")

    def LaunchAccess(self):
        self.WriteLine("ACCESS ROUTE REQUESTED.")
        ODN.Emit("System.Phase.Access")

    def LaunchDesktop(self):
        self.WriteLine("DESKTOP ROUTE REQUESTED.")
        ODN.Emit("System.Phase.Desktop")

    def RebootSystem(self):
        self.WriteLine("SYSTEM REBOOT REQUESTED.")
        ODN.Emit("System.Command.Reboot")

    def PowerDown(self):
        self.WriteLine("POWER DOWN REQUESTED.")
        ODN.Emit("System.Command.PowerDown")

    def ShowBootState(self):
        self.UpdateBoardState()

    def SetErrorContext(self, Context):
        self.Context = Context or {}
        Error = str(self.Context.get("error", "UNKNOWN ERROR"))
        Stage = str(self.Context.get("stage", "UNKNOWN"))
        Details = self.Context.get("details", "")

        self.HeaderMode.SetText("FAULT: " + Error)
        self.FooterStatus.SetText("EMERGENCY OVERRIDE GRANTED")
        self.WriteLine("!!! EMERGENCY ROUTE ACTIVE !!!")
        self.WriteLine("STAGE: " + Stage)
        self.WriteLine("ERROR: " + Error)
        if Details:
            self.WriteLine("DETAILS:")
            for Line in str(Details).splitlines():
                self.WriteLine("  " + Line)
        self.WriteLine("")
        self.WriteLine("BOARD COMPUTER CAN BE PROBED FROM THE TERMINAL.")
        self.UpdateBoardState()

    def SetErrorContext(self, Context):
        self.SetErrorContext(Context)

EmergencyScreen = EmergencyMode
