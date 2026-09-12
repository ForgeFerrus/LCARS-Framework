# LCARS FRAMEWORK Головний десктопний екран LCARS.
#
# Побудовано тільки з готових LCARS-елементів:
# component.py  -> LCARSButton, LCARSBar, LCARSElbow, LCARSLabel, LCARSIndicator
# interface.py  -> Screen, Segment, Panel, Padd, Header, DataBlock, StatBar, StatusLine
# animation.py  -> Warp, DataStream, DiagnosticGrid
# Workbench / Nova тут не імпортуються. Вони мають запускатися окремим модулем,
# коли будуть приведені до актуального LCARS API.
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from typing import Any

from lcars.base.type import LCARS
from lcars.base.default import Palette, RandomButtonColor, FontStyle
from lcars.base.component import LCARSButton, LCARSBar, LCARSElbow, LCARSLabel, LCARSIndicator, Primitive
from lcars.base.interface import Screen, Segment, Panel, PADD, Header, DataBlock, StatBar, StatusLine
from lcars.base.animation import Warp, DataStream, DiagnosticGrid, ScanningBar
from lcars.core.signal import Transmission
from lcars.ui.panels.access import SystemAccess

class LCARSDesktop(Screen):
    def __init__(self, parent=None):
        super().__init__(Parent=parent)
        self.LockRequested = Transmission()
        
        self.Pages = {}
        self.NavButtons = {}
        self.Mode = "MENU"

        self.ClockTimer = None
        self.TopStatus = None
        self.Chamber = None

        self.widget.setObjectName("DesktopRoot")
        self.widget.setStyleSheet("#DesktopRoot { background-color: #000000; border: none; }")
        self.Root = self

        self.Build()
        self.StartClock()
        self.Select(self.Mode)

    # ─────────────────────────────────────────────────────────────
    # BUILD
    # ─────────────────────────────────────────────────────────────

    def Build(self):
        ContentWidget = self.Items["Content"].widget
        RootLayout = LCARS.Horizontal(ContentWidget)
        RootLayout.setContentsMargins(18, 18, 18, 18)
        RootLayout.setSpacing(10)

        self.LeftColumn = Segment(Parent=ContentWidget)
        self.LeftColumn.widget.setFixedWidth(220)
        self.LeftLayout = LCARS.Vertical(self.LeftColumn.widget)
        self.LeftLayout.setContentsMargins(0, 0, 0, 0)
        self.LeftLayout.setSpacing(7)
        RootLayout.addWidget(self.LeftColumn.widget)

        self.RightColumn = Segment(Parent=ContentWidget)
        self.RightLayout = LCARS.Vertical(self.RightColumn.widget)
        self.RightLayout.setContentsMargins(0, 0, 0, 0)
        self.RightLayout.setSpacing(7)
        RootLayout.addWidget(self.RightColumn.widget, 1)

        self.BuildLeftNavigation()
        self.BuildRightShell()
        self.BuildPages()
        self.Select("BRIDGE")

    def BuildLeftNavigation(self):
        TopElbow = LCARSElbow(
            Direction="top-left",
            Color=RandomButtonColor("accent", "DesktopTopElbow"),
            Parent=self.LeftColumn.widget
        )
        TopElbow.widget.setFixedHeight(85)
        self.LeftLayout.addWidget(TopElbow.widget)

        Items = [
            ("WORKSPACE", self.ShowWorkspace),
            ("BRIDGE", self.ShowBridge),
            ("SYSTEM", self.ShowSystem),
            ("SUPPORT", self.ShowSupport),
            ("MENU", self.ShowMenu),
            ("CONSOLE", self.ShowConsole),
            ("ENGINE", self.ShowEngineering),
            ("SCIENCE", self.ShowScience),
            ("AGENT", self.ShowAgent),
            ("DESIGNER", self.ShowDesigner),
            ("COMMANDER", self.ShowCommander),
            ("IDE", self.ShowIDE),
            ("LOCK", self.RequestLock),
        ]

        for Index, (Name, Callback) in enumerate(Items):
            BtnColor = Palette.Buttons[Index % len(Palette.Buttons)]
            Btn = LCARSButton(
                Text=Name,
                Type="soft-left",
                Color=BtnColor,
                Parent=self.LeftColumn.widget
            )
            Btn.Clicked.Connect(Callback)
            self.NavButtons[Name] = Btn
            self.LeftLayout.addWidget(Btn.widget)

        self.LeftLayout.addStretch(1)

        BottomElbow = LCARSElbow(
            Direction="bottom-left",
            Color=RandomButtonColor("accent", "DesktopBottomElbow"),
            Parent=self.LeftColumn.widget
        )
        BottomElbow.widget.setFixedHeight(61)
        self.LeftLayout.addWidget(BottomElbow.widget)

    def BuildRightShell(self):
        self.BuildHeader()
        self.BuildChamber()
        self.BuildFooter()

    def BuildHeader(self):
        TopRow = Segment(Parent=self.RightColumn.widget)
        TopLayout = LCARS.Horizontal(TopRow.widget)
        TopLayout.setContentsMargins(0, 0, 0, 0)
        TopLayout.setSpacing(7)

        self.TopStatus = LCARSIndicator(
            Text="LCARS PRIMARY OPERATING SYSTEM // STARTING",
            Type="rect-left",
            Color=Palette.Buttons[1],
            Parent=TopRow.widget,
            FontSize=15,
        )
        self.TopStatus.widget.setFixedHeight(52)
        TopLayout.addWidget(self.TopStatus.widget, 1)

        Accent = LCARSBar(
            Type="rect",
            Color=Palette.Buttons[2],
            Parent=TopRow.widget,
            Width=72,
            Height=52
        )
        Accent.widget.setFixedWidth(72)
        Accent.widget.setFixedHeight(52)
        TopLayout.addWidget(Accent.widget)

        self.RightLayout.addWidget(TopRow.widget)

        SecondRow = Segment(Parent=self.RightColumn.widget)
        SecondLayout = LCARS.Horizontal(SecondRow.widget)
        SecondLayout.setContentsMargins(0, 0, 0, 0)
        SecondLayout.setSpacing(7)

        self.ModeStatus = LCARSIndicator(
            Text="MODE // BRIDGE",
            Type="rect-left",
            Color=Palette.Buttons[3],
            Parent=SecondRow.widget,
            FontSize=12,
        )
        self.ModeStatus.widget.setFixedHeight(26)
        SecondLayout.addWidget(self.ModeStatus.widget, 1)

        Scan = LCARSBar(
            Type="scanning",
            Color=Palette.Buttons[4],
            Parent=SecondRow.widget,
            Height=26
        )
        Scan.widget.setFixedWidth(180)
        Scan.widget.setFixedHeight(26)
        SecondLayout.addWidget(Scan.widget)

        self.RightLayout.addWidget(SecondRow.widget)

    def BuildChamber(self):
        self.Chamber = LCARS.Chamber(self.RightColumn.widget)
        self.Chamber.setStyleSheet("background-color: #000000; border: none;")
        PolicyCls = LCARS.Policy
        Expand = getattr(PolicyCls, "Expanding", getattr(getattr(PolicyCls, "Policy", PolicyCls), "Expanding", None))
        if Expand is not None:
            self.Chamber.setSizePolicy(Expand, Expand)
        self.RightLayout.addWidget(self.Chamber, 1)

    def BuildFooter(self):
        FooterOne = Segment(Parent=self.RightColumn.widget)
        FooterOneLayout = LCARS.Horizontal(FooterOne.widget)
        FooterOneLayout.setContentsMargins(0, 0, 0, 0)
        FooterOneLayout.setSpacing(7)

        # Додаємо кілька DataBlock-ів для відображення системного статусу
        Stats = [
            ("CORE TEMP", "47.2 °C", Palette.Buttons[0]),
            ("POWER DRAW", "12.4 GW", Palette.Buttons[1]),
            ("SUBSPACE", "NOMINAL", Palette.Buttons[2]),
            ("SHIELD", "STANDBY", Palette.Buttons[3]),
            ("SENSORS", "ACTIVE", Palette.Buttons[4]),
        ]

        for Label, Value, Color in Stats:
            Block = DataBlock(LabelText=Label, ValueText=Value, Color=Color, Parent=FooterOne.widget)
            FooterOneLayout.addWidget(Block.widget, 1)

        self.RightLayout.addWidget(FooterOne.widget)

        FooterTwo = Segment(Parent=self.RightColumn.widget)
        FooterTwoLayout = LCARS.Horizontal(FooterTwo.widget)
        FooterTwoLayout.setContentsMargins(0, 0, 0, 0)
        FooterTwoLayout.setSpacing(7)

        self.FooterStatus = LCARSIndicator(
            Text="CORE DESKTOP ONLINE",
            Type="rect-left",
            Color=Palette.Buttons[0],
            Parent=FooterTwo.widget,
            FontSize=12
        )
        self.FooterStatus.widget.setFixedHeight(30)
        FooterTwoLayout.addWidget(self.FooterStatus.widget, 1)

        EndCap = LCARSBar(
            Type="rect",
            Color=Palette.Buttons[2],
            Parent=FooterTwo.widget,
            Width=120,
            Height=30
        )
        EndCap.widget.setFixedWidth(120)
        EndCap.widget.setFixedHeight(30)
        FooterTwoLayout.addWidget(EndCap.widget)

        self.RightLayout.addWidget(FooterTwo.widget)

    # ─────────────────────────────────────────────────────────────
    # PAGES
    # ─────────────────────────────────────────────────────────────

    def BuildPages(self):
        self.Builders = {
            "WORKSPACE": self.CreateWorkspacePage,
            "BRIDGE": self.CreateBridgePage,
            "SYSTEM": self.CreateSystemPage,
            "SUPPORT": self.CreateSupportPage,
            "MENU": self.CreateMenuPage,
            "CONSOLE": self.CreateConsolePage,
            "ENGINE": self.CreateEngineeringPage,
            "SCIENCE": self.CreateSciencePage,
            "DESIGNER": self.CreateDesignerPage,
            "IDE": self.CreateIDEPage,
        }

        self.Pages = {}

    def Page(self):
        Page = Segment(Parent=self.Chamber)
        Page.widget.setStyleSheet("background-color: #000000; border: none;")
        Layout = LCARS.Vertical(Page.widget)
        Layout.setContentsMargins(0, 0, 0, 0)
        Layout.setSpacing(12)
        Page.Layout = Layout
        return Page

    def CreateFallbackPage(self, Name, Error):
        Page = self.Page()
        Page.Layout.addWidget(Header(f"{Name} OFFLINE", Parent=Page.widget).widget)

        Fault = DataBlock(
            LabelText="MODULE ISOLATED",
            ValueText=str(Error)[:220],
            Color=Palette.RedAlert[0],
            Parent=Page.widget
        )
        Page.Layout.addWidget(Fault.widget)
        Page.Layout.addStretch()
        return Page

    def CreateBridgePage(self):
        Page = self.Page()
        Body = Segment(Parent=Page.widget)
        BodyLayout = LCARS.Horizontal(Body.widget)
        BodyLayout.setContentsMargins(0, 0, 0, 0)
        BodyLayout.setSpacing(16)
        Page.Layout.addWidget(Body.widget, 1)

        Stars = Warp(
            Parent=Body.widget,
            Color="#D9E8FF",
            Width=900,
            Height=520,
            StarCount=170,
            Running=True
        )
        Stars.widget.setMinimumSize(620, 380)
        BodyLayout.addWidget(Stars.widget, 1)

        Side = Segment(Parent=Body.widget)
        SideLayout = LCARS.Vertical(Side.widget)
        SideLayout.setContentsMargins(0, 0, 0, 0)
        SideLayout.setSpacing(10)
        BodyLayout.addWidget(Side.widget)

        Stream = DataStream(
            Parent=Side.widget,
            Color=Palette.Buttons[1],
            Width=320,
            Height=220,
            Running=True
        )
        Stream.widget.setFixedSize(320, 220)
        SideLayout.addWidget(Stream.widget)

        SideLayout.addWidget(DataBlock("LOCATION", "SOL SYSTEM", Color=Palette.Buttons[2], Parent=Side.widget).widget)
        SideLayout.addWidget(DataBlock("STATUS", "ALL SYSTEMS NOMINAL", Color=Palette.Buttons[3], Parent=Side.widget).widget)
        SideLayout.addWidget(DataBlock("CREW", "ACTIVE", Color=Palette.Buttons[4], Parent=Side.widget).widget)
        SideLayout.addStretch()

        Controls = Segment(Parent=Page.widget)
        ControlsLayout = LCARS.Horizontal(Controls.widget)
        ControlsLayout.setContentsMargins(0, 0, 0, 0)
        ControlsLayout.setSpacing(10)
        Page.Layout.addWidget(Controls.widget)

        BtnImpulse = LCARSButton("IMPULSE", Type="pill", Color=Palette.Buttons[0], Parent=Controls.widget, Width=160, Height=44)
        BtnWarp = LCARSButton("WARP", Type="pill", Color=Palette.Buttons[1], Parent=Controls.widget, Width=160, Height=44)
        BtnImpulse.Clicked.Connect(lambda: Stars.SetWarpSpeed(False))
        BtnWarp.Clicked.Connect(lambda: Stars.SetWarpSpeed(True))
        ControlsLayout.addWidget(BtnImpulse.widget)
        ControlsLayout.addWidget(BtnWarp.widget)
        ControlsLayout.addStretch()       
        return Page


    def CreateSystemPage(self):
        # Titanium Bridge Migration: import importlib.util
        if importlib.util.find_spec("lcars.ui.panels.access") is not None and importlib.util.find_spec("psutil") is not None:
            Page = self.Page()
            Page.Layout.addWidget(Header("SYSTEM", Parent=Page.widget).widget)
            from lcars.ui.panels.access import SystemAccess
            SystemPanel = SystemAccess(DesktopNodeRef=self)
            if hasattr(SystemPanel, "widget"):
                Page.Layout.addWidget(SystemPanel.widget, 1)
            else:
                Page.Layout.addWidget(SystemPanel, 1)
        else:
            Page = self.CreateFallbackPage("SYSTEM", "access panel or psutil dependency not found")
        return Page

    def CreateMenuPage(self):
        Page = self.Page()
        Page.Layout.addWidget(Header("APPLICATIONS", Parent=Page.widget).widget)

        Grid = Segment(Parent=Page.widget)
        GridLayout = LCARS.Horizontal(Grid.widget)
        GridLayout.setContentsMargins(16, 16, 16, 16)
        GridLayout.setSpacing(24)
        Page.Layout.addWidget(Grid.widget, 1)

        Col1 = LCARS.Vertical()
        Col1.setSpacing(16)
        GridLayout.addLayout(Col1)

        Col2 = LCARS.Vertical()
        Col2.setSpacing(16)
        GridLayout.addLayout(Col2)

        Apps1 = [
            ("ENGINEERING", self.ShowEngineering),
            ("SCIENCE", self.ShowScience),
            ("TERMINAL", self.ShowConsole),
            ("AGENT", self.ShowAgent),
        ]
        Apps2 = [
            ("SYSTEM ACCESS", self.ShowSystem),
            ("DESIGNER", self.ShowDesigner),
            ("COMMUNICATIONS", None),
            ("DATABASE", None),
        ]

        for AppList, ColLayout in [(Apps1, Col1), (Apps2, Col2)]:
            for i, (Name, Handler) in enumerate(AppList):
                Btn = LCARSButton(
                    Text=Name,
                    Type="rect-left",
                    Color=Palette.Buttons[i % len(Palette.Buttons)],
                    Parent=Grid.widget,
                    Height=70,
                    FontSize=18
                )
                if Handler:
                    Btn.Clicked.Connect(Handler)
                ColLayout.addWidget(Btn.widget)
            ColLayout.addStretch()

        return Page

    def CreateConsolePage(self):
        Page = self.Page()
        Page.Layout.addWidget(Header("ONBOARD COMPUTER", Parent=Page.widget).widget)

        from lcars.service.console import LCARSConsole
        from lcars.base.component import SetStyle

        self.BoardConsole = LCARSConsole()

        # Вихідна зона
        OutputRow = Segment(Parent=Page.widget)
        OutputLayout = LCARS.Vertical(OutputRow.widget)
        OutputLayout.setContentsMargins(0, 0, 0, 0)
        OutputLayout.setSpacing(6)
        Page.Layout.addWidget(OutputRow.widget, 1)

        self.ConsoleOutput = LCARS.Terminal(OutputRow.widget)
        self.ConsoleOutput.setReadOnly(True)
        SetStyle(self.ConsoleOutput,
            "background-color: #040810; color: #99CCFF; border: none; "
            "font-family: 'LCARS', Consolas, monospace; font-size: 18px; "
            "padding: 16px; line-height: 1.5;"
        )
        OutputLayout.addWidget(self.ConsoleOutput, 1)

        # Рядок вводу
        InputRow = Segment(Parent=Page.widget)
        InputRowLayout = LCARS.Horizontal(InputRow.widget)
        InputRowLayout.setContentsMargins(0, 0, 0, 0)
        InputRowLayout.setSpacing(8)
        Page.Layout.addWidget(InputRow.widget)

        self.ConsoleInput = LCARS.Input(InputRow.widget)
        SetStyle(self.ConsoleInput,
            "background-color: #060C18; color: #FFFFFF; border: none; "
            "border-bottom: 2px solid #336699; font-family: 'LCARS', Consolas, monospace; "
            "font-size: 18px; padding: 10px 16px;"
        )
        self.ConsoleInput.setPlaceholderText("ENTER DIRECTIVE...")
        InputRowLayout.addWidget(self.ConsoleInput, 1)

        ExecBtn = LCARSButton("EXECUTE", Type="soft-right", Color=Palette.Buttons[1],
                              Parent=InputRow.widget, Width=160, Height=44)
        ExecBtn.Clicked.Connect(self.OnConsoleExecute)
        InputRowLayout.addWidget(ExecBtn.widget)

        self.ConsoleInput.returnPressed.connect(self.OnConsoleExecute)

        # Кнопки швидкого доступу
        QuickRow = Segment(Parent=Page.widget)
        QuickLayout = LCARS.Horizontal(QuickRow.widget)
        QuickLayout.setContentsMargins(0, 4, 0, 0)
        QuickLayout.setSpacing(8)
        Page.Layout.addWidget(QuickRow.widget)

        Shortcuts = [
            ("STATUS",    "status"),
            ("HELP",      "help"),
            ("DIAG",      "diag"),
            ("GIT LOG",   "git log --oneline -8"),
            ("CHECK",     "check lcars"),
            ("SAFEGUARD", "diag"),
        ]
        for Idx, (Label, Cmd) in enumerate(Shortcuts):
            Btn = LCARSButton(Label, Type="pill", Color=Palette.Buttons[Idx % len(Palette.Buttons)],
                              Parent=QuickRow.widget, Height=36, FontSize=15)
            Btn.Clicked.Connect(lambda C=Cmd: self.RunConsoleCommand(C))
            QuickLayout.addWidget(Btn.widget)
        QuickLayout.addStretch()

        # Автоаналіз при першому відкритті
        LCARS.Timer.singleShot(400, self.RunComputerAnalysis)
        return Page

    def RunConsoleCommand(self, Text):
        if not hasattr(self, "BoardConsole") or not hasattr(self, "ConsoleOutput"):
            return
        self.ConsoleLog(f"LCARS> {Text}")
        self.BoardConsole.Execute(Text, self.ConsoleLog)

    def OnConsoleExecute(self, Packet=None):
        if not hasattr(self, "ConsoleInput") or not hasattr(self, "BoardConsole"):
            return
        Text = self.ConsoleInput.text().strip()
        if not Text:
            return
        self.ConsoleInput.clear()
        self.ConsoleLog(f"LCARS> {Text}")
        if Text.lower() in ("clear", "cls"):
            if hasattr(self.ConsoleOutput, "clear"):
                self.ConsoleOutput.clear()
            return
        self.BoardConsole.Execute(Text, self.ConsoleLog)

    def ConsoleLog(self, Message):
        if not hasattr(self, "ConsoleOutput"):
            return
        if hasattr(self.ConsoleOutput, "append"):
            self.ConsoleOutput.append(str(Message))
            return
        if hasattr(self.ConsoleOutput, "setPlainText"):
            Current = self.ConsoleOutput.toPlainText() if hasattr(self.ConsoleOutput, "toPlainText") else ""
            self.ConsoleOutput.setPlainText(Current + "\n" + str(Message))

    def RunComputerAnalysis(self):
        # Titanium Bridge Migration: import importlib.util
        from lcars.base.info import getVersion
        self.ConsoleLog("=" * 56)
        self.ConsoleLog("  LCARS ONBOARD COMPUTER — SYSTEM ANALYSIS")
        self.ConsoleLog("=" * 56)
        self.ConsoleLog(f"  VERSION  : LCARS {getVersion()}")
        self.ConsoleLog(f"  PLATFORM : {sys.platform}")
        self.ConsoleLog("")
        self.ConsoleLog("  DIRECTIVES:")
        self.ConsoleLog("    status       — system status")
        self.ConsoleLog("    diag         — full diagnostics")
        self.ConsoleLog("    help         — command reference")
        self.ConsoleLog("    git log      — repository log")
        self.ConsoleLog("    check <path> — compile check")
        self.ConsoleLog("    run <path>   — execute file")
        self.ConsoleLog("    mode git     — switch to git mode")
        self.ConsoleLog("    mode python  — switch to python mode")
        self.ConsoleLog("")
        self.ConsoleLog("  SAFEGUARD SCAN:")
        Modules = [
            ("lcars.base.desktop",        "DESKTOP CORE"),
            ("lcars.base.component",      "COMPONENT LAYER"),
            ("lcars.system.emergency",    "EMERGENCY CORE"),
            ("lcars.service.console",     "CONSOLE SERVICE"),
            ("lcars.ui.panels.access",    "SYSTEM ACCESS PANEL"),
            ("lcars.ui.panels.engineering","ENGINEERING PANEL"),
            ("psutil",                    "SYSTEM METRICS (psutil)"),
        ]
        Faults = []
        for ModName, Label in Modules:
            Found = importlib.util.find_spec(ModName) is not None
            Status = "OK  " if Found else "FAIL"
            self.ConsoleLog(f"    [{Status}] {Label}")
            if not Found:
                Faults.append(Label)
        self.ConsoleLog("")
        if Faults:
            self.ConsoleLog("  RECOMMENDATIONS:")
            for F in Faults:
                self.ConsoleLog(f"    WARNING: {F} NOT FOUND — CHECK INSTALLATION")
            self.ConsoleLog("    RUN: diag — for full fault report")
        else:
            self.ConsoleLog("  ALL MODULES NOMINAL. SYSTEM LIFE SUPPORT: ACTIVE.")
        self.ConsoleLog("=" * 56)


    def CreateEngineeringPage(self):
        # Titanium Bridge Migration: import importlib.util
        if importlib.util.find_spec("lcars.ui.panels.engineering") is not None:
            Page = self.Page()
            from lcars.ui.panels.engineering import EngineeringPanel
            EngPanel = EngineeringPanel(DesktopNodeRef=self, ParentNode=Page)
            if hasattr(EngPanel, "widget"):
                Page.Layout.addWidget(EngPanel.widget, 1)
            else:
                Page.Layout.addWidget(EngPanel, 1)
        else:
            Page = self.CreateFallbackPage("ENGINEERING", "engineering panel not found")
        return Page

    def CreateSciencePage(self):
        Page = self.Page()
        Page.Layout.addWidget(Header("SCIENCE", Parent=Page.widget).widget)

        Row = Segment(Parent=Page.widget)
        RowLayout = LCARS.Horizontal(Row.widget)
        RowLayout.setContentsMargins(0, 0, 0, 0)
        RowLayout.setSpacing(16)
        Page.Layout.addWidget(Row.widget, 1)

        Stream = DataStream(
            Parent=Row.widget,
            Color=Palette.Buttons[2],
            Width=520,
            Height=420,
            Lines=[
                "PARTICLE TRACE 47-A",
                "GEANT4 SIMULATION BUS",
                "DETECTOR ARRAY STANDBY",
                "QUANTUM CORE RESERVED",
                "SENSOR MATRIX ONLINE",
                "ANALYTIC PIPELINE READY",
            ],
            Running=True
        )
        RowLayout.addWidget(Stream.widget, 1)

        Side = Segment(Parent=Row.widget)
        SideLayout = LCARS.Vertical(Side.widget)
        SideLayout.setContentsMargins(0, 0, 0, 0)
        SideLayout.setSpacing(10)
        RowLayout.addWidget(Side.widget)

        SideLayout.addWidget(DataBlock("SENSORS", "PASSIVE", Color=Palette.Buttons[0], Parent=Side.widget).widget)
        SideLayout.addWidget(DataBlock("SIMULATION", "IDLE", Color=Palette.Buttons[1], Parent=Side.widget).widget)
        SideLayout.addWidget(DataBlock("QUANTUM", "RESERVED", Color=Palette.Buttons[2], Parent=Side.widget).widget)
        SideLayout.addStretch()

        return Page



    def CreateDesignerPage(self):
        Page = self.Page()
        # Titanium Bridge Migration: import importlib.util
        if importlib.util.find_spec("programs.constructor") is not None and importlib.util.find_spec("lcars.app.designer") is not None:
            from programs.constructor import ConstructorObject
            from lcars.app.designer import Designer
            DesignerView = Designer(Parent=Page.widget)
            if hasattr(DesignerView, "widget"):
                Page.Layout.addWidget(DesignerView.widget, 1)
            else:
                Page.Layout.addWidget(DesignerView, 1)
        else:
            Page = self.CreateFallbackPage("DESIGNER", "designer components not found")
        return Page

    def CreateIDEPage(self):
        Page = self.Page()
        if True:
            from lcars.ui.panels.ide import TitaniumIDE
            from lcars.base.register import REGISTRY
            
            # Отримуємо BoardComputer
            bc = REGISTRY.Get("BoardComputer")
            
            # Створюємо IDE
            IDEView = TitaniumIDE(Parent=Page.widget, BoardComputer=bc)
            if hasattr(IDEView, "widget"):
                Page.Layout.addWidget(IDEView.widget, 1)
            else:
                Page.Layout.addWidget(IDEView, 1)
        if False: # Removed except block
            Page = self.CreateFallbackPage("IDE", f"IDE initialization failed: {e}")
        return Page

    def CreateSupportPage(self):
        Page = self.Page()
        # Titanium Bridge Migration: import importlib.util
        if importlib.util.find_spec("lcars.tools.health") is not None:
            from lcars.tools.health import SystemSupportPanel
            SupportView = SystemSupportPanel(Parent=Page.widget)
            if hasattr(SupportView, "widget"):
                Page.Layout.addWidget(SupportView.widget, 1)
            else:
                Page.Layout.addWidget(SupportView, 1)
        else:
            Page = self.CreateFallbackPage("SUPPORT", "health module not found")
        return Page

    def CreateWorkspacePage(self):
        Page = self.Page()
        # Titanium Bridge Migration: import importlib.util
        if importlib.util.find_spec("programs.nova.app") is not None:
            from programs.nova.app import BuildNova
            NovaWorkspace = BuildNova(Parent=Page.widget)
            if hasattr(NovaWorkspace, "widget"):
                Page.Layout.addWidget(NovaWorkspace.widget, 1)
            else:
                Page.Layout.addWidget(NovaWorkspace, 1)
        else:
            Page = self.CreateFallbackPage("WORKSPACE", "Nova workspace app not found")
        return Page

    # ─────────────────────────────────────────────────────────────
    # NAVIGATION
    # ─────────────────────────────────────────────────────────────

    def Select(self, PageName: str):
        if PageName not in self.Pages and PageName in self.Builders:
            if True:
                Page = self.Builders[PageName]()
            if False:
                Page = self.CreateFallbackPage(PageName, f"module error: {e}")
            self.Pages[PageName] = Page
            self.Chamber.addWidget(Page.widget)

        if PageName not in self.Pages:
            return

        Page = self.Pages[PageName]
        self.Chamber.setCurrentWidget(Page.widget)
        self.Mode = PageName

        if self.TopStatus:
            self.TopStatus.SetText(f"LCARS PRIMARY OPERATING SYSTEM // {PageName}")

        if self.ModeStatus:
            self.ModeStatus.SetText(f"MODE // {PageName}")

        if self.FooterStatus:
            self.FooterStatus.SetText(f"ACTIVE PANEL // {PageName}")

        for Name, Button in self.NavButtons.items():
            if Name == "LOCK":
                continue
            Button.SetState("selected" if Name == PageName else "normal")

    def ShowWorkspace(self):
        self.Select("WORKSPACE")

    def ShowBridge(self):
        self.Select("BRIDGE")

    def ShowSystem(self):
        self.Select("SYSTEM")

    def ShowSupport(self):
        self.Select("SUPPORT")

    def ShowMenu(self):
        self.Select("MENU")

    def ShowConsole(self):
        self.Select("CONSOLE")

    def ShowEngineering(self):
        self.Select("ENGINE")

    def ShowScience(self):
        self.Select("SCIENCE")

    def ShowAgent(self):
        self.Select("AGENT")

    def ShowDesigner(self):
        self.Select("DESIGNER")

    def ShowCommander(self):
        self.Select("COMMANDER")

    def ShowIDE(self):
        if True:
            from lcars.ui.panels.ide import TitaniumIDE
            from lcars.base.register import REGISTRY
            
            # Отримуємо BoardComputer з реєстру
            bc = REGISTRY.Get("BoardComputer")
            
            # Створюємо IDE як окреме вікно
            ide = TitaniumIDE(Parent=self.widget, BoardComputer=bc)
            ide.widget.setWindowTitle("TITANIUM IDE - LCARS Development Environment")
            ide.widget.show()
            
            self.Select("IDE")
        if False: # Removed except block
            print(f"[DESKTOP] Failed to launch IDE: {e}")
            # Fallback - просто покажемо повідомлення
            self.Select("IDE")

    def RequestLock(self):
        self.LockRequested.Emit()

    # ─────────────────────────────────────────────────────────────
    # CLOCK
    # ─────────────────────────────────────────────────────────────

    def StartClock(self):
        self.ClockTimer = LCARS.Timer(self.widget)
        self.ClockTimer.setInterval(1000)
        self.ClockTimer.timeout.connect(self.UpdateClock)
        self.ClockTimer.start()

    def UpdateClock(self):
        DTV = LCARS.System.DateTime
        if DTV and hasattr(DTV, "now"):
            Now = DTV.now()
            if hasattr(Now, "strftime"):
                ClockText = Now.strftime("%H:%M:%S")
            else:
                ClockText = "00:00:00"
        else:
            ClockText = "00:00:00"
        if self.TopStatus:
            self.TopStatus.SetText(f"LCARS PRIMARY OPERATING SYSTEM // {self.Mode} // {ClockText}")

    def Show(self):
        FramelessFlag = getattr(LCARS, "Frameless", None)
        if FramelessFlag is not None and hasattr(self.widget, "setWindowFlag"):
            self.widget.setWindowFlag(FramelessFlag, True)
        if hasattr(self.widget, "showFullScreen"):
            self.widget.showFullScreen()
        elif hasattr(self.widget, "showMaximized"):
            self.widget.showMaximized()
        else:
            self.widget.show()


def Build(Display=None):
    return LCARSDesktop(Display)


def Run(Args=None):
    HostSys = LCARS.Import("sys")
    ArgsList = HostSys.argv if HostSys and hasattr(HostSys, "argv") else []
    App = LCARS.Application.instance() or LCARS.Application(ArgsList)
    if App is None:
        return 1

    try:
        Shell = Build(None)
        if hasattr(Shell, "Show"):
            Shell.Show()
        elif hasattr(Shell, "widget"):
            Shell.widget.show()
        elif hasattr(Shell, "show"):
            Shell.show()
        return App.exec()
    except Exception as e:
        try:
            from lcars.ui.screen.emergency import EmergencyScreen
            Em = EmergencyScreen()
            if hasattr(Em, "SetErrorContext"):
                Em.SetErrorContext({"error": str(e), "stage": "DESKTOP RUN"})
            if hasattr(Em, "widget"):
                Em.widget.show()
            return App.exec()
        except Exception:
            return 1

if __name__ == "__main__":
    HostSys = LCARS.Import("sys")
    ExitCode = Run()
    if HostSys and hasattr(HostSys, "exit"):
        HostSys.exit(ExitCode)
