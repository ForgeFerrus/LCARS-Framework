# LCARS FRAMEWORK -- Main Desktop Screen
# Titanium Standard: PascalCase, no underscore in identifiers, no Qt imports,
# no .widget access, no QHBoxLayout/QVBoxLayout, no docstrings.
# All string literals in ASCII/Latin only.

import importlib.util

from lcars.base.type import LCARS
from lcars.base.default import Palette, RandomButtonColor
from lcars.base.component import LCARSButton, LCARSBar, LCARSElbow, LCARSLabel, LCARSIndicator
from lcars.base.interface import Screen, Panel
from lcars.base.animation import Warp, DataStream, DiagnosticGrid
from lcars.core.signal import Transmission


# =============================================================================
# LCARS DESKTOP -- primary operational surface
# =============================================================================

class LCARSDesktop(Screen):

    LockRequested = Transmission()

    def Initialize(self, Parent=None):
        super().Initialize(Parent=Parent)
        self.Pages = {}
        self.NavItems = {}
        self.ActivePage = ""
        self.ClockTimer = None
        self.StatusBar = None
        self.ModeLabel = None
        self.FooterStatus = None
        self.BoardConsole = None
        self.ConsoleOutput = None
        self.ConsoleInput = None
        self.Build()
        self.StartClock()
        self.Select("BRIDGE")

    # -------------------------------------------------------------------------
    # BUILD
    # -------------------------------------------------------------------------

    def Build(self):
        self.SetHorizontal(18, 18, 18, 18, Spacing=10)

        self.LeftColumn = Panel()
        self.LeftColumn.SetVertical(0, 0, 0, 0, Spacing=7)
        self.Add(self.LeftColumn)

        self.RightColumn = Panel()
        self.RightColumn.SetVertical(0, 0, 0, 0, Spacing=7)
        self.Add(self.RightColumn, 1)

        self.BuildLeftNavigation()
        self.BuildRightShell()

    def BuildLeftNavigation(self):
        self.LeftColumn.Add(LCARSElbow(
            Corner="top-left",
            Color=RandomButtonColor("accent", "DesktopTopElbow"),
            Height=85
        ))

        NavMap = [
            ("WORKSPACE",  "WORKSPACE",   self.ShowWorkspace),
            ("BRIDGE",     "BRIDGE",      self.ShowBridge),
            ("SYSTEM",     "SYSTEM",      self.ShowSystem),
            ("SUPPORT",    "SUPPORT",     self.ShowSupport),
            ("MENU",       "MENU",        self.ShowMenu),
            ("CONSOLE",    "CONSOLE",     self.ShowConsole),
            ("ENGINE",     "ENGINEERING", self.ShowEngineering),
            ("SCIENCE",    "SCIENCE",     self.ShowScience),
            ("AGENT",      "AGENT",       self.ShowAgent),
            ("DESIGNER",   "DESIGNER",    self.ShowDesigner),
            ("COMMANDER",  "COMMANDER",   self.ShowCommander),
            ("IDE",        "IDE",         self.ShowIDE),
            ("LOCK",       "LOCK",        self.RequestLock),
        ]

        for Index, (Key, Label, Handler) in enumerate(NavMap):
            BtnColor = Palette.Buttons[Index % len(Palette.Buttons)]
            Btn = LCARSButton(
                Text=Label,
                Form=LCARSButton.SoftLeftType,
                Color=BtnColor,
                Height=36,
                FontSize=16,
                Handler=Handler
            )
            self.NavItems[Key] = Btn
            self.LeftColumn.Add(Btn)

        self.LeftColumn.AddStretch(1)

        self.LeftColumn.Add(LCARSElbow(
            Corner="bottom-left",
            Color=RandomButtonColor("accent", "DesktopBottomElbow"),
            Height=61
        ))

    def BuildRightShell(self):
        self.BuildHeader()
        self.BuildChamber()
        self.BuildFooter()

    def BuildHeader(self):
        TopRow = Panel()
        TopRow.SetHorizontal(0, 0, 0, 0, Spacing=7)

        self.StatusBar = LCARSIndicator(
            Text="LCARS PRIMARY OPERATING SYSTEM // STARTING",
            Form=LCARSIndicator.RectLeftType,
            Color=Palette.Buttons[1],
            FontSize=18,
            Height=52
        )
        TopRow.Add(self.StatusBar, 1)
        TopRow.Add(LCARSBar(
            Form=LCARSBar.RectType,
            Color=Palette.Buttons[2],
            Width=72,
            Height=52
        ))
        self.RightColumn.Add(TopRow)

        SecondRow = Panel()
        SecondRow.SetHorizontal(0, 0, 0, 0, Spacing=7)

        self.ModeLabel = LCARSIndicator(
            Text="MODE // BRIDGE",
            Form=LCARSIndicator.RectLeftType,
            Color=Palette.Buttons[3],
            FontSize=16,
            Height=26
        )
        SecondRow.Add(self.ModeLabel, 1)
        SecondRow.Add(LCARSBar(
            Form=LCARSBar.PillHalfType,
            Color=Palette.Buttons[4],
            Width=180,
            Height=26
        ))
        self.RightColumn.Add(SecondRow)

    def BuildChamber(self):
        # Central content chamber -- pages are added dynamically on first navigation
        self.Chamber = Panel()
        self.Chamber.SetVertical(0, 0, 0, 0, Spacing=0)
        self.RightColumn.Add(self.Chamber, 1)

    def BuildFooter(self):
        FooterOne = Panel()
        FooterOne.SetHorizontal(0, 0, 0, 0, Spacing=7)

        Stats = [
            ("CORE TEMP",  "47.2 C",  Palette.Buttons[0]),
            ("POWER DRAW", "12.4 GW", Palette.Buttons[1]),
            ("SUBSPACE",   "NOMINAL", Palette.Buttons[2]),
            ("SHIELD",     "STANDBY", Palette.Buttons[3]),
            ("SENSORS",    "ACTIVE",  Palette.Buttons[4]),
        ]

        for Label, Value, Color in Stats:
            Block = Panel()
            Block.SetVertical(0, 0, 0, 0, Spacing=2)
            Block.Add(LCARSLabel(Text=Label, FontSize=16, Height=20, Color=Color))
            Block.Add(LCARSLabel(Text=Value, FontSize=18, Height=24, Color=Color))
            FooterOne.Add(Block, 1)

        self.RightColumn.Add(FooterOne)

        FooterTwo = Panel()
        FooterTwo.SetHorizontal(0, 0, 0, 0, Spacing=7)

        self.FooterStatus = LCARSIndicator(
            Text="CORE DESKTOP ONLINE",
            Form=LCARSIndicator.RectLeftType,
            Color=Palette.Buttons[0],
            FontSize=16,
            Height=30
        )
        FooterTwo.Add(self.FooterStatus, 1)
        FooterTwo.Add(LCARSBar(
            Form=LCARSBar.RectType,
            Color=Palette.Buttons[2],
            Width=120,
            Height=30
        ))
        self.RightColumn.Add(FooterTwo)

    # -------------------------------------------------------------------------
    # PAGES -- lazy construction on first navigation
    # -------------------------------------------------------------------------

    def MakePage(self):
        # Returns a fresh vertical panel sized to fill the chamber
        Page = Panel()
        Page.SetVertical(0, 0, 0, 0, Spacing=12)
        return Page

    def CreateBridgePage(self):
        Page = self.MakePage()

        Body = Panel()
        Body.SetHorizontal(0, 0, 0, 0, Spacing=16)
        Page.Add(Body, 1)

        Stars = Warp(
            Color="#D9E8FF",
            Width=900,
            Height=520,
            StarCount=170,
            Running=True
        )
        Body.Add(Stars, 1)

        Side = Panel()
        Side.SetVertical(0, 0, 0, 0, Spacing=10)
        Body.Add(Side)

        Stream = DataStream(
            Color=Palette.Buttons[1],
            Width=320,
            Height=220,
            Running=True
        )
        Side.Add(Stream)
        Side.Add(LCARSLabel(Text="LOCATION: SOL SYSTEM",        FontSize=16, Height=28))
        Side.Add(LCARSLabel(Text="STATUS: ALL SYSTEMS NOMINAL",  FontSize=16, Height=28))
        Side.Add(LCARSLabel(Text="CREW: ACTIVE",                 FontSize=16, Height=28))
        Side.AddStretch(1)

        Controls = Panel()
        Controls.SetHorizontal(0, 0, 0, 0, Spacing=10)
        Page.Add(Controls)

        Controls.Add(LCARSButton(
            Text="IMPULSE",
            Form=LCARSButton.PillType,
            Color=Palette.Buttons[0],
            Width=160,
            Height=44,
            FontSize=18,
            Handler=lambda: Stars.SetWarpSpeed(False)
        ))
        Controls.Add(LCARSButton(
            Text="WARP",
            Form=LCARSButton.PillType,
            Color=Palette.Buttons[1],
            Width=160,
            Height=44,
            FontSize=18,
            Handler=lambda: Stars.SetWarpSpeed(True)
        ))
        Controls.AddStretch(1)

        return Page

    def CreateSystemPage(self):
        if (importlib.util.find_spec("lcars.ui.panels.access") is not None
                and importlib.util.find_spec("psutil") is not None):
            Page = self.MakePage()
            from lcars.ui.panels.access import SystemAccess
            SystemPanel = SystemAccess()
            Page.Add(SystemPanel, 1)
        else:
            Page = self.CreateFallbackPage("SYSTEM", "access panel or psutil dependency not found")
        return Page

    def CreateMenuPage(self):
        Page = self.MakePage()

        Grid = Panel()
        Grid.SetHorizontal(16, 16, 16, 16, Spacing=24)
        Page.Add(Grid, 1)

        Col1 = Panel()
        Col1.SetVertical(0, 0, 0, 0, Spacing=16)
        Col2 = Panel()
        Col2.SetVertical(0, 0, 0, 0, Spacing=16)

        Apps1 = [
            ("ENGINEERING",   self.ShowEngineering),
            ("SCIENCE",       self.ShowScience),
            ("TERMINAL",      self.ShowConsole),
            ("AGENT",         self.ShowAgent),
        ]
        Apps2 = [
            ("SYSTEM ACCESS", self.ShowSystem),
            ("DESIGNER",      self.ShowDesigner),
            ("COMMUNICATIONS", None),
            ("DATABASE",      None),
        ]

        for Index, (Name, Handler) in enumerate(Apps1):
            Col1.Add(LCARSButton(
                Text=Name,
                Form=LCARSButton.RectLeftType,
                Color=Palette.Buttons[Index % len(Palette.Buttons)],
                Height=70,
                FontSize=20,
                Handler=Handler
            ))
        Col1.AddStretch(1)

        for Index, (Name, Handler) in enumerate(Apps2):
            Col2.Add(LCARSButton(
                Text=Name,
                Form=LCARSButton.RectLeftType,
                Color=Palette.Buttons[Index % len(Palette.Buttons)],
                Height=70,
                FontSize=20,
                Handler=Handler
            ))
        Col2.AddStretch(1)

        Grid.Add(Col1, 1)
        Grid.Add(Col2, 1)
        return Page

    def CreateConsolePage(self):
        Page = self.MakePage()
        Page.Add(LCARSLabel(Text="ONBOARD COMPUTER", FontSize=22, Height=36))

        from lcars.service.console import LCARSConsole
        self.BoardConsole = LCARSConsole()

        # Output area
        OutputRow = Panel()
        OutputRow.SetVertical(0, 0, 0, 0, Spacing=6)
        Page.Add(OutputRow, 1)

        self.ConsoleOutput = LCARS.Terminal()
        if hasattr(self.ConsoleOutput, "SetReadOnly"):
            self.ConsoleOutput.SetReadOnly(True)
        OutputRow.Add(self.ConsoleOutput, 1)

        # Input row
        InputRow = Panel()
        InputRow.SetHorizontal(0, 0, 0, 0, Spacing=8)
        Page.Add(InputRow)

        self.ConsoleInput = LCARS.Input()
        if hasattr(self.ConsoleInput, "SetPlaceholder"):
            self.ConsoleInput.SetPlaceholder("ENTER DIRECTIVE...")
        InputRow.Add(self.ConsoleInput, 1)

        ExecBtn = LCARSButton(
            Text="EXECUTE",
            Form=LCARSButton.SoftRightType,
            Color=Palette.Buttons[1],
            Width=160,
            Height=44,
            FontSize=16,
            Handler=self.OnConsoleExecute
        )
        InputRow.Add(ExecBtn)

        # Quick-access shortcuts
        QuickRow = Panel()
        QuickRow.SetHorizontal(0, 4, 0, 0, Spacing=8)
        Page.Add(QuickRow)

        Shortcuts = [
            ("STATUS",    "status"),
            ("HELP",      "help"),
            ("DIAG",      "diag"),
            ("GIT LOG",   "git log --oneline -8"),
            ("CHECK",     "check lcars"),
            ("SAFEGUARD", "diag"),
        ]
        for Index, (Label, Cmd) in enumerate(Shortcuts):
            QuickRow.Add(LCARSButton(
                Text=Label,
                Form=LCARSButton.PillType,
                Color=Palette.Buttons[Index % len(Palette.Buttons)],
                Height=36,
                FontSize=16,
                Handler=lambda C=Cmd: self.RunConsoleCommand(C)
            ))
        QuickRow.AddStretch(1)

        # Boot analysis on first open
        BootTimer = LCARS.Retrieve("Base.Core.Timer")
        if BootTimer and hasattr(BootTimer, "singleShot"):
            BootTimer.singleShot(400, self.RunComputerAnalysis)

        return Page

    def CreateEngineeringPage(self):
        if importlib.util.find_spec("lcars.ui.panels.engineering") is not None:
            Page = self.MakePage()
            from lcars.ui.panels.engineering import EngineeringPanel
            EngPanel = EngineeringPanel()
            Page.Add(EngPanel, 1)
        else:
            Page = self.CreateFallbackPage("ENGINEERING", "engineering panel not found")
        return Page

    def CreateSciencePage(self):
        Page = self.MakePage()

        Row = Panel()
        Row.SetHorizontal(0, 0, 0, 0, Spacing=16)
        Page.Add(Row, 1)

        Stream = DataStream(
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
        Row.Add(Stream, 1)

        Side = Panel()
        Side.SetVertical(0, 0, 0, 0, Spacing=10)
        Row.Add(Side)

        Side.Add(LCARSLabel(Text="SENSORS: PASSIVE",    FontSize=16, Height=28))
        Side.Add(LCARSLabel(Text="SIMULATION: IDLE",    FontSize=16, Height=28))
        Side.Add(LCARSLabel(Text="QUANTUM: RESERVED",   FontSize=16, Height=28))
        Side.AddStretch(1)

        return Page

    def CreateDesignerPage(self):
        Page = self.MakePage()
        try:
            from programs.constructor import TitaniumArchitectEngine
            DesignerView = TitaniumArchitectEngine()
            Page.Add(DesignerView, 1)
        except Exception as Err:
            Page = self.CreateFallbackPage("DESIGNER", "Constructor error: " + str(Err))
        return Page

    def CreateIDEPage(self):
        Page = self.MakePage()
        try:
            from lcars.ui.panels.ide import TitaniumIDE
            from lcars.base.register import REGISTRY
            Computer = REGISTRY.Get("BoardComputer")
            IDEView = TitaniumIDE(BoardComputer=Computer)
            Page.Add(IDEView, 1)
        except Exception as Err:
            Page = self.CreateFallbackPage("IDE", "IDE initialization failed: " + str(Err))
        return Page

    def CreateSupportPage(self):
        if importlib.util.find_spec("lcars.tools.health") is not None:
            Page = self.MakePage()
            from lcars.tools.health import SystemSupportPanel
            SupportView = SystemSupportPanel()
            Page.Add(SupportView, 1)
        else:
            Page = self.CreateFallbackPage("SUPPORT", "health module not found")
        return Page

    def CreateWorkspacePage(self):
        if importlib.util.find_spec("programs.nova.app") is not None:
            Page = self.MakePage()
            from programs.nova.app import BuildNova
            NovaWorkspace = BuildNova()
            Page.Add(NovaWorkspace, 1)
        else:
            Page = self.CreateFallbackPage("WORKSPACE", "Nova workspace app not found")
        return Page

    def CreateAgentPage(self):
        Page = self.MakePage()
        Page.Add(LCARSLabel(Text="AUTONOMOUS AGENT", FontSize=24, Align="center", Height=60))
        return Page

    def CreateCommanderPage(self):
        Page = self.MakePage()
        Page.Add(LCARSLabel(Text="COMMANDER", FontSize=24, Align="center", Height=60))
        return Page

    def CreateFallbackPage(self, Name, Error):
        Page = self.MakePage()
        Page.Add(LCARSLabel(Text=Name + " OFFLINE", FontSize=22, Height=36))
        Page.Add(LCARSLabel(
            Text="MODULE ISOLATED: " + str(Error)[:220],
            FontSize=16,
            Color=Palette.RedAlert[0],
            Height=48
        ))
        Page.AddStretch(1)
        return Page

    # -------------------------------------------------------------------------
    # NAVIGATION -- lazy page construction
    # -------------------------------------------------------------------------

    Builders = {}

    def RegisterBuilders(self):
        self.Builders = {
            "WORKSPACE": self.CreateWorkspacePage,
            "BRIDGE":    self.CreateBridgePage,
            "SYSTEM":    self.CreateSystemPage,
            "SUPPORT":   self.CreateSupportPage,
            "MENU":      self.CreateMenuPage,
            "CONSOLE":   self.CreateConsolePage,
            "ENGINE":    self.CreateEngineeringPage,
            "SCIENCE":   self.CreateSciencePage,
            "AGENT":     self.CreateAgentPage,
            "DESIGNER":  self.CreateDesignerPage,
            "COMMANDER": self.CreateCommanderPage,
            "IDE":       self.CreateIDEPage,
        }

    def Select(self, Key):
        if not self.Builders:
            self.RegisterBuilders()

        # Build page on first navigation
        if Key not in self.Pages and Key in self.Builders:
            try:
                Page = self.Builders[Key]()
            except Exception as Err:
                Page = self.CreateFallbackPage(Key, str(Err))
            self.Pages[Key] = Page
            self.Chamber.Add(Page)

        if Key not in self.Pages:
            return

        # Show selected, hide all others
        for PageKey, Page in self.Pages.items():
            if PageKey == Key:
                Page.show()
            else:
                Page.hide()

        self.ActivePage = Key

        if self.StatusBar:
            self.StatusBar.SetText("LCARS PRIMARY OPERATING SYSTEM // " + Key)
        if self.ModeLabel:
            self.ModeLabel.SetText("MODE // " + Key)
        if self.FooterStatus:
            self.FooterStatus.SetText("ACTIVE PANEL // " + Key)

        # Update nav button states
        for NavKey, Btn in self.NavItems.items():
            if NavKey == "LOCK":
                continue
            if hasattr(Btn, "SetState"):
                Btn.SetState("selected" if NavKey == Key else "normal")

    # -------------------------------------------------------------------------
    # CONSOLE OPERATIONS
    # -------------------------------------------------------------------------

    def RunConsoleCommand(self, Text):
        self.ConsoleLog("LCARS> " + Text)
        if self.BoardConsole:
            self.BoardConsole.Execute(Text, self.ConsoleLog)

    def OnConsoleExecute(self):
        if self.ConsoleInput is None or self.BoardConsole is None:
            return
        Text = ""
        if hasattr(self.ConsoleInput, "GetText"):
            Text = self.ConsoleInput.GetText().strip()
        elif hasattr(self.ConsoleInput, "text"):
            Text = self.ConsoleInput.text().strip()
        if not Text:
            return
        if hasattr(self.ConsoleInput, "Clear"):
            self.ConsoleInput.Clear()
        elif hasattr(self.ConsoleInput, "clear"):
            self.ConsoleInput.clear()
        self.ConsoleLog("LCARS> " + Text)
        if Text.lower() in ("clear", "cls"):
            if self.ConsoleOutput and hasattr(self.ConsoleOutput, "Clear"):
                self.ConsoleOutput.Clear()
            elif self.ConsoleOutput and hasattr(self.ConsoleOutput, "clear"):
                self.ConsoleOutput.clear()
            return
        self.BoardConsole.Execute(Text, self.ConsoleLog)

    def ConsoleLog(self, Message):
        if self.ConsoleOutput is None:
            return
        if hasattr(self.ConsoleOutput, "Append"):
            self.ConsoleOutput.Append(str(Message))
        elif hasattr(self.ConsoleOutput, "append"):
            self.ConsoleOutput.append(str(Message))

    def RunComputerAnalysis(self):
        from lcars.base.version import GetVersion
        Sep = "=" * 56
        self.ConsoleLog(Sep)
        self.ConsoleLog("  LCARS ONBOARD COMPUTER -- SYSTEM ANALYSIS")
        self.ConsoleLog(Sep)
        self.ConsoleLog("  VERSION  : LCARS " + str(GetVersion()))
        self.ConsoleLog("")
        self.ConsoleLog("  DIRECTIVES:")
        self.ConsoleLog("    status       -- system status")
        self.ConsoleLog("    diag         -- full diagnostics")
        self.ConsoleLog("    help         -- command reference")
        self.ConsoleLog("    git log      -- repository log")
        self.ConsoleLog("    check <path> -- compile check")
        self.ConsoleLog("    run <path>   -- execute file")
        self.ConsoleLog("")
        self.ConsoleLog("  SAFEGUARD SCAN:")

        Modules = [
            ("lcars.base.desktop",          "DESKTOP CORE"),
            ("lcars.base.component",        "COMPONENT LAYER"),
            ("lcars.system.emergency",      "EMERGENCY CORE"),
            ("lcars.service.console",       "CONSOLE SERVICE"),
            ("lcars.ui.panels.access",      "SYSTEM ACCESS PANEL"),
            ("lcars.ui.panels.engineering", "ENGINEERING PANEL"),
            ("psutil",                      "SYSTEM METRICS (psutil)"),
        ]

        Faults = []
        for ModName, ModLabel in Modules:
            Found = importlib.util.find_spec(ModName) is not None
            Status = "OK  " if Found else "FAIL"
            self.ConsoleLog("    [" + Status + "] " + ModLabel)
            if not Found:
                Faults.append(ModLabel)

        self.ConsoleLog("")
        if Faults:
            self.ConsoleLog("  RECOMMENDATIONS:")
            for Fault in Faults:
                self.ConsoleLog("    WARNING: " + Fault + " NOT FOUND -- CHECK INSTALLATION")
            self.ConsoleLog("    RUN: diag -- for full fault report")
        else:
            self.ConsoleLog("  ALL MODULES NOMINAL. SYSTEM LIFE SUPPORT: ACTIVE.")
        self.ConsoleLog(Sep)

    # -------------------------------------------------------------------------
    # CLOCK
    # -------------------------------------------------------------------------

    def StartClock(self):
        TimerClass = LCARS.Retrieve("Base.Core.Timer")
        if TimerClass is None:
            return
        self.ClockTimer = TimerClass()
        if hasattr(self.ClockTimer, "timeout"):
            self.ClockTimer.timeout.connect(self.UpdateClock)
        if hasattr(self.ClockTimer, "start"):
            self.ClockTimer.start(1000)

    def UpdateClock(self):
        TimeModule = LCARS.Retrieve("System.Core.Datetime")
        if TimeModule and hasattr(TimeModule, "now"):
            ClockText = TimeModule.now().strftime("%H:%M:%S")
        else:
            ClockText = ""
        if self.StatusBar and ClockText:
            self.StatusBar.SetText(
                "LCARS PRIMARY OPERATING SYSTEM // " + self.ActivePage + " // " + ClockText
            )

    # -------------------------------------------------------------------------
    # NAVIGATION HANDLERS
    # -------------------------------------------------------------------------

    def ShowWorkspace(self):  self.Select("WORKSPACE")
    def ShowBridge(self):     self.Select("BRIDGE")
    def ShowSystem(self):     self.Select("SYSTEM")
    def ShowSupport(self):    self.Select("SUPPORT")
    def ShowMenu(self):       self.Select("MENU")
    def ShowConsole(self):    self.Select("CONSOLE")
    def ShowEngineering(self): self.Select("ENGINE")
    def ShowScience(self):    self.Select("SCIENCE")
    def ShowAgent(self):      self.Select("AGENT")
    def ShowDesigner(self):   self.Select("DESIGNER")
    def ShowCommander(self):  self.Select("COMMANDER")
    def ShowIDE(self):        self.Select("IDE")
    def RequestLock(self):    self.LockRequested.Emit()


def Build(Parent=None):
    return LCARSDesktop(Parent=Parent)
