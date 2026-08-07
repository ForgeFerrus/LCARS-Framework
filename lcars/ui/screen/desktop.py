# Головний десктоп LCARS.
# Канонічний вигляд: периферійні пояси, матові блоки, великий шрифт.
# Ліва навігація перемикає робочі панелі, кожна оперує реальними модулями.
# Без docstring і без try/except — тільки короткі коментарі.

import sys
from pathlib import Path
from datetime import datetime

ProjectRoot = Path(__file__).resolve().parents[3]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from lcars.base.type import LCARS
from lcars.base.default import Palette
from lcars.base.component import LCARSButton, LCARSBar, LCARSLabel, LCARSIndicator, LCARSElbow
from lcars.base.interface import Screen, Segment, Panel, DataBlock, Header
from lcars.core.signal import ODN
from lcars.core.kernel import Kernel


# Застосувати явний великий шрифт до текстового елемента (обхід адаптивного).
def BigText(Element, Size=18, Color=None):
    Widget = Element.widget if hasattr(Element, "widget") else Element
    Current = Widget.styleSheet() if hasattr(Widget, "styleSheet") else ""
    Extra = "font-size: " + str(Size) + "pt; font-family: 'LCARS', 'Segoe UI', sans-serif; font-weight: bold;"
    if Color:
        Extra += " color: " + Color + ";"
    Widget.setStyleSheet(Current + " " + Extra)
    return Element


class LCARSDesktop(Screen):
    def __init__(self, parent=None):
        super().__init__(Parent=parent)
        self.Pages = {}
        self.NavButtons = {}
        self.ActivePage = "ENGINEERING"
        self.ClockTimer = None
        self.TickerTimer = None
        self.LiveLog = []
        self.CurrentLanguage = "ENG"
        self.CurrentMode = "NOMINAL"
        self.TickerPhase = 0
        self.KernelRef = Kernel()

        self.widget.setObjectName("DesktopRoot")
        self.widget.setStyleSheet("#DesktopRoot { background-color: #000000; border: none; }")

        self.Build()
        self.StartClock()
        self.StartTicker()
        self.SubscribeEvents()
        self.Select("GREETING")

    # ──────────────────────────────────────────────── КАРКАС
    def Build(self):
        Content = self.Items["Content"].widget
        Root = LCARS.Horizontal(Content)
        Root.setContentsMargins(0, 0, 0, 0)
        Root.setSpacing(10)

        self.LeftColumn = Segment(Parent=Content)
        self.LeftColumn.widget.setFixedWidth(260)
        self.LeftColumn.widget.setStyleSheet("background-color: #000000; border: none;")
        self.LeftLayout = LCARS.Vertical(self.LeftColumn.widget)
        self.LeftLayout.setContentsMargins(0, 0, 0, 0)
        self.LeftLayout.setSpacing(6)
        Root.addWidget(self.LeftColumn.widget)

        self.RightColumn = Segment(Parent=Content)
        self.RightColumn.widget.setStyleSheet("background-color: #000000; border: none;")
        self.RightLayout = LCARS.Vertical(self.RightColumn.widget)
        self.RightLayout.setContentsMargins(0, 0, 0, 0)
        self.RightLayout.setSpacing(10)
        Root.addWidget(self.RightColumn.widget, 1)

        self.BuildNav()
        self.BuildHeader()
        self.BuildChamber()
        self.BuildFooter()

    # Ліва навігація — LCARS elbows та кнопки
    def BuildNav(self):
        # Top elbow
        TopElbow = LCARSElbow(Direction="top-left", Color=Palette.Buttons[0], Parent=self.LeftColumn.widget)
        TopElbow.widget.setFixedSize(260, 56)
        self.LeftLayout.addWidget(TopElbow.widget)

        Items = [
            ("ENGINEERING", lambda: self.Select("ENGINEERING")),
            ("BRIDGE", lambda: self.Select("BRIDGE")),
            ("SCIENCE", lambda: self.Select("SCIENCE")),
            ("NAVIGATION", lambda: self.Select("NAVIGATION")),
            ("TACTICAL", lambda: self.Select("TACTICAL")),
            ("COMM", lambda: self.Select("COMM")),
            ("LIBRARY", lambda: self.Select("LIBRARY")),
            ("STORAGE", lambda: self.Select("STORAGE")),
            ("MEMORY", lambda: self.Select("MEMORY")),
            ("PROGRAMS", lambda: self.Select("PROGRAMS")),
            ("SETTINGS", lambda: self.Select("SETTINGS")),
            ("DATABASE", lambda: self.Select("DATABASE")),
            ("MEDICAL", lambda: self.Select("MEDICAL")),
            ("COMPUTER", lambda: self.Select("COMPUTER")),
            ("MODE", self.ToggleMode),
            ("LANG", self.ToggleLanguage),
            ("NETWORK", lambda: ODN.Emit("System.Phase.Hub")),
            ("LOCK", self.RequestLock),
            ("EMERGENCY", lambda: ODN.Emit("System.Phase.Emergency")),
        ]
        Greeting = LCARSButton(Text="GREETING", Type="pill", Color=Palette.Buttons[4], Parent=self.LeftColumn.widget)
        Greeting.widget.setFixedHeight(48)
        Greeting.Clicked.Connect(lambda: self.Select("GREETING"))
        self.NavButtons["GREETING"] = Greeting
        self.LeftLayout.insertWidget(1, Greeting.widget)

        Propulsion = LCARSButton(Text="PROPULSION", Type="pill", Color=Palette.Buttons[1], Parent=self.LeftColumn.widget)
        Propulsion.widget.setFixedHeight(48)
        Propulsion.Clicked.Connect(lambda: self.Select("PROPULSION"))
        self.NavButtons["PROPULSION"] = Propulsion
        self.LeftLayout.insertWidget(15, Propulsion.widget)
        
        for Index, (Name, Callback) in enumerate(Items):
            Color = Palette.Buttons[Index % len(Palette.Buttons)]
            if Name == "EMERGENCY":
                Color = Palette.RedAlert[0]
            Btn = LCARSButton(Text=Name, Type="pill", Color=Color, Parent=self.LeftColumn.widget)
            Btn.widget.setFixedHeight(48)
            Btn.Clicked.Connect(Callback)
            self.NavButtons[Name] = Btn
            self.LeftLayout.addWidget(Btn.widget)
            
        self.LeftLayout.addStretch(1)

        BotElbow = LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[2], Parent=self.LeftColumn.widget)
        BotElbow.widget.setFixedSize(260, 46)
        self.LeftLayout.addWidget(BotElbow.widget)

    def BuildHeader(self):
        Bar = LCARSBar(Type="rect", Color=Palette.Buttons[1], Height=56, Parent=self.RightColumn.widget)
        Bar.widget.setStyleSheet("background-color: " + Palette.Buttons[1] + "; border: none;")
        Layout = LCARS.Horizontal(Bar.widget)
        Layout.setContentsMargins(16, 0, 16, 0)
        Layout.setSpacing(12)
        self.TopStatus = LCARSLabel(Text="LCARS TITAN V9.0", Color=Palette.Background, FontSize=26, Parent=Bar.widget)
        BigText(self.TopStatus, 26, Palette.Background)
        Layout.addWidget(self.TopStatus.widget, 1)
        self.ModeStatus = LCARSLabel(Text="ENGINEERING", Color=Palette.Background, FontSize=20, Parent=Bar.widget)
        BigText(self.ModeStatus, 20, Palette.Background)
        Layout.addWidget(self.ModeStatus.widget)
        self.RightLayout.addWidget(Bar.widget)

    def BuildChamber(self):
        self.Chamber = LCARS.Chamber(self.RightColumn.widget)
        self.Chamber.setStyleSheet("background-color: #000000; border: none;")
        self.Chamber.setSizePolicy(LCARS.Policy.Policy.Expanding, LCARS.Policy.Policy.Expanding)
        self.RightLayout.addWidget(self.Chamber, 1)

    def BuildFooter(self):
        Bar = LCARSBar(Type="rect", Color=Palette.Buttons[2], Height=46, Parent=self.RightColumn.widget)
        Bar.widget.setStyleSheet("background-color: " + Palette.Buttons[2] + "; border: none;")
        Layout = LCARS.Horizontal(Bar.widget)
        Layout.setContentsMargins(12, 0, 12, 0)
        Layout.setSpacing(10)
        self.FooterStatus = LCARSLabel(Text="CORE DESKTOP ONLINE", Color=Palette.Background, FontSize=16, Parent=Bar.widget)
        BigText(self.FooterStatus, 16, Palette.Background)
        Layout.addWidget(self.FooterStatus.widget, 1)
        self.Ticker = LCARSLabel(Text="", Color=Palette.Background, FontSize=14, Parent=Bar.widget)
        BigText(self.Ticker, 14, Palette.Background)
        Layout.addWidget(self.Ticker.widget, 2)
        self.RightLayout.addWidget(Bar.widget)

    # ──────────────────────────────────────────────── ПІДКЛЮЧЕННЯ ПАНЕЛЕЙ
    def LoadPage(self, Name):
        if Name == "GREETING":
            return self.PageGreeting()
        if Name == "PROPULSION":
            return self.PagePropulsion()
        from lcars.ui.panels.workbench import (
            SciencePanel, NavigationPanel, TacticalPanel, CommPanel,
            LibraryPanel, StoragePanel, ProgramsPanel, SettingsPanel,
            DatabasePanel, MedicalPanel,
        )
        if Name == "ENGINEERING":
            from lcars.ui.panels.engineering import EngineeringPanel
            return EngineeringPanel(DesktopNodeRef=self.KernelRef, ParentNode=self.Chamber)
        if Name == "SCIENCE":
            return SciencePanel(self.KernelRef, self.Chamber)
        if Name == "NAVIGATION":
            return NavigationPanel(self.KernelRef, self.Chamber)
        if Name == "TACTICAL":
            return TacticalPanel(self.KernelRef, self.Chamber)
        if Name == "COMM":
            return CommPanel(self.KernelRef, self.Chamber)
        if Name == "LIBRARY":
            return LibraryPanel(self.KernelRef, self.Chamber)
        if Name == "STORAGE":
            return StoragePanel(self.KernelRef, self.Chamber)
        if Name == "MEMORY":
            return self.PageMemory()
        if Name == "PROGRAMS":
            return ProgramsPanel(self.KernelRef, self.Chamber)
        if Name == "SETTINGS":
            return SettingsPanel(self.KernelRef, self.Chamber)
        if Name == "DATABASE":
            return DatabasePanel(self.KernelRef, self.Chamber)
        if Name == "MEDICAL":
            return MedicalPanel(self.KernelRef, self.Chamber)
        if Name == "COMPUTER":
            return self.PageComputer()
        if Name == "BRIDGE":
            return self.PageBridge()
        return self.PageBridge()

    def Select(self, Name):
        self.ActivePage = Name
        if Name not in self.Pages:
            self.Pages[Name] = self.LoadPage(Name)
            self.Chamber.addWidget(self.Pages[Name].widget)
        for Key, Page in self.Pages.items():
            if Key == Name:
                Page.widget.show()
            else:
                Page.widget.hide()
        self.ModeStatus.SetText(Name)
        self.RefreshClockStats()

    # ──────────────────────────────────────────────── СПРОЩЕНІ СТОРІНКИ
    def PageGreeting(self):
        Page = Segment(Parent=self.Chamber)
        Page.widget.setStyleSheet("background-color: #000000; border: none;")
        Layout = LCARS.Vertical(Page.widget)
        Layout.setContentsMargins(0, 0, 0, 0)
        Layout.setSpacing(20)
        Layout.setAlignment(LCARS.Protocol.AlignmentFlag.AlignCenter if hasattr(LCARS.Protocol, "AlignmentFlag") else 0)
        Title = LCARSLabel(Text="LCARS TITAN V9.0", Color=Palette.Buttons[1], FontSize=44, Parent=Page.widget)
        BigText(Title, 44, Palette.Buttons[1])
        Layout.addWidget(Title.widget)
        Sub = LCARSLabel(Text="БОРТОВИЙ КОМП'ЮТЕР ОНЛАЙН", Color=Palette.Buttons[2], FontSize=26, Parent=Page.widget)
        BigText(Sub, 26, Palette.Buttons[2])
        Layout.addWidget(Sub.widget)
        Welcome = LCARSLabel(Text="ВІТАЄМО, COMMANDER", Color=Palette.Panels[2], FontSize=22, Parent=Page.widget)
        BigText(Welcome, 22, Palette.Panels[2])
        Layout.addWidget(Welcome.widget)
        Hint = LCARSLabel(Text="ОБЕРІТЬ РОЗДІЛ ЗЛІВА", Color=Palette.Buttons[3], FontSize=16, Parent=Page.widget)
        BigText(Hint, 16, Palette.Buttons[3])
        Layout.addWidget(Hint.widget)
        Layout.addStretch(1)
        self.GreetTimer = LCARS.Timer(Page.widget)
        self.GreetTimer.setSingleShot(True)
        self.GreetTimer.setInterval(3500)
        self.GreetTimer.timeout.connect(lambda: self.Select("BRIDGE"))
        self.GreetTimer.start()
        return Page

    def PagePropulsion(self):
        Page = Segment(Parent=self.Chamber)
        Page.widget.setStyleSheet("background-color: #000000; border: none;")
        Layout = LCARS.Vertical(Page.widget)
        Layout.setContentsMargins(12, 12, 12, 12)
        Layout.setSpacing(14)
        Title = LCARSLabel(Text="PROPULSION // DRIVE MODE", Color=Palette.Buttons[2], FontSize=24, Parent=Page.widget)
        BigText(Title, 24, Palette.Buttons[2])
        Layout.addWidget(Title.widget)

        self.DriveMode = "IMPULSE"
        self.DriveLabel = LCARSLabel(Text="РЕЖИМ: ІМПУЛЬС", Color=Palette.Buttons[0], FontSize=28, Parent=Page.widget)
        BigText(self.DriveLabel, 28, Palette.Buttons[0])
        Layout.addWidget(self.DriveLabel.widget)

        Controls = Segment(Parent=Page.widget)
        CtrLayout = LCARS.Horizontal(Controls.widget)
        CtrLayout.setContentsMargins(0, 0, 0, 0)
        CtrLayout.setSpacing(12)
        Impulse = LCARSButton(Text="ІМПУЛЬС", Type="pill", Color=Palette.Buttons[1], Parent=Controls.widget)
        Impulse.widget.setFixedSize(240, 60)
        Impulse.widget.setStyleSheet("background-color: " + Palette.Buttons[1] + "; color: #000000; border: none; border-radius: 6px; font-size: 18pt; font-weight: bold;")
        Impulse.Clicked.Connect(lambda: self.SetDrive("IMPULSE", "ІМПУЛЬС"))
        CtrLayout.addWidget(Impulse.widget)
        Warp = LCARSButton(Text="ВАРП", Type="pill", Color=Palette.Buttons[3], Parent=Controls.widget)
        Warp.widget.setFixedSize(240, 60)
        Warp.widget.setStyleSheet("background-color: " + Palette.Buttons[3] + "; color: #000000; border: none; border-radius: 6px; font-size: 18pt; font-weight: bold;")
        Warp.Clicked.Connect(lambda: self.SetDrive("WARP", "ВАРП"))
        CtrLayout.addWidget(Warp.widget)
        CtrLayout.addStretch(1)
        Layout.addWidget(Controls.widget)

        self.DriveOut = LCARS.Terminal(Page.widget)
        self.DriveOut.setReadOnly(True)
        self.DriveOut.setStyleSheet("background-color: " + Palette.Panels[1] + "; color: #000000; border: none; font-family: 'LCARS', Consolas, monospace; font-size: 15pt; padding: 14px;")
        self.DriveOut.setPlainText("ВИВІД НА ЕКРАН:\n> DRIVE MODE: IMPULSE\n> THRUST: NOMINAL\n> READY")
        Layout.addWidget(self.DriveOut, 1)
        return Page

    def SetDrive(self, Mode, Label):
        self.DriveMode = Mode
        self.DriveLabel.SetText("РЕЖИМ: " + Label)
        self.DriveOut.setPlainText("ВИВІД НА ЕКРАН:\n> DRIVE MODE: " + Mode + "\n> THRUST: NOMINAL\n> READY")

    def PageBridge(self):
        Page = Segment(Parent=self.Chamber)
        Page.widget.setStyleSheet("background-color: #000000; border: none;")
        Layout = LCARS.Vertical(Page.widget)
        Layout.setContentsMargins(12, 12, 12, 12)
        Layout.setSpacing(12)
        Title = LCARSLabel(Text="BRIDGE OPERATIONS", Color=Palette.Buttons[2], FontSize=24, Parent=Page.widget)
        BigText(Title, 24, Palette.Buttons[2])
        Layout.addWidget(Title.widget)
        Grid = Segment(Parent=Page.widget)
        GridLayout = LCARS.Horizontal(Grid.widget)
        GridLayout.setContentsMargins(0, 0, 0, 0)
        GridLayout.setSpacing(10)
        self.BridgeBlocks = {}
        for Label, Color in [("CPU", Palette.Buttons[0]), ("MEMORY", Palette.Buttons[1]), ("UPTIME", Palette.Buttons[2]), ("PROCESSES", Palette.Buttons[3])]:
            Block = DataBlock(LabelText=Label, ValueText="SCAN...", Color=Color, Parent=Grid.widget)
            Block.widget.setFixedHeight(90)
            GridLayout.addWidget(Block.widget, 1)
            self.BridgeBlocks[Label] = Block
        Layout.addWidget(Grid.widget)
        self.RefreshMetrics()
        Layout.addStretch(1)
        return Page

    def PageMemory(self):
        Page = Segment(Parent=self.Chamber)
        Page.widget.setStyleSheet("background-color: #000000; border: none;")
        Layout = LCARS.Vertical(Page.widget)
        Layout.setContentsMargins(12, 12, 12, 12)
        Layout.setSpacing(12)
        Title = LCARSLabel(Text="ISOLINEAR MEMORY", Color=Palette.Buttons[2], FontSize=24, Parent=Page.widget)
        BigText(Title, 24, Palette.Buttons[2])
        Layout.addWidget(Title.widget)
        Grid = Segment(Parent=Page.widget)
        GridLayout = LCARS.Horizontal(Grid.widget)
        GridLayout.setContentsMargins(0, 0, 0, 0)
        GridLayout.setSpacing(10)
        self.MemBlocks = {}
        for Label, Color in [("CHIPS", Palette.Buttons[0]), ("SESSIONS", Palette.Buttons[1]), ("DIALOGS", Palette.Buttons[2]), ("CONTEXTS", Palette.Buttons[3])]:
            Block = DataBlock(LabelText=Label, ValueText="--", Color=Color, Parent=Grid.widget)
            Block.widget.setFixedHeight(90)
            GridLayout.addWidget(Block.widget, 1)
            self.MemBlocks[Label] = Block
        Layout.addWidget(Grid.widget)
        self.RefreshMemory()
        Layout.addStretch(1)
        return Page

    def PageComputer(self):
        Page = Segment(Parent=self.Chamber)
        Page.widget.setStyleSheet("background-color: #000000; border: none;")
        Layout = LCARS.Vertical(Page.widget)
        Layout.setContentsMargins(12, 12, 12, 12)
        Layout.setSpacing(12)
        Title = LCARSLabel(Text="COMPUTER // TITAN", Color=Palette.Buttons[2], FontSize=24, Parent=Page.widget)
        BigText(Title, 24, Palette.Buttons[2])
        Layout.addWidget(Title.widget)
        Query = Segment(Parent=Page.widget)
        QueryLayout = LCARS.Horizontal(Query.widget)
        QueryLayout.setContentsMargins(0, 0, 0, 0)
        QueryLayout.setSpacing(8)
        self.ComputerInput = LCARS.Input()
        self.ComputerInput.setParent(Query.widget)
        self.ComputerInput.setStyleSheet("background-color: #000000; color: " + Palette.Panels[2] + "; border: 2px solid " + Palette.Panels[1] + "; font-size: 16pt; padding: 10px;")
        self.ComputerInput.setPlaceholderText("ЗАПИТ ДО КОМП'ЮТЕРА...")
        QueryLayout.addWidget(self.ComputerInput, 1)
        AskBtn = LCARSButton(Text="ЗАПИТАТИ", Type="pill", Color=Palette.Buttons[2], Parent=Query.widget)
        AskBtn.widget.setFixedSize(200, 52)
        AskBtn.widget.setStyleSheet("background-color: " + Palette.Buttons[2] + "; color: #000000; border: none; border-radius: 6px; font-size: 16pt; font-weight: bold;")
        AskBtn.Clicked.Connect(self.AskComputer)
        QueryLayout.addWidget(AskBtn.widget)
        Layout.addWidget(Query.widget)
        self.ComputerOutput = LCARS.Terminal(Page.widget)
        self.ComputerOutput.setReadOnly(True)
        self.ComputerOutput.setStyleSheet("background-color: #000000; color: " + Palette.Panels[2] + "; border: 2px solid " + Palette.Panels[1] + "; font-family: 'LCARS', Consolas, monospace; font-size: 15pt; padding: 14px;")
        self.ComputerOutput.setPlainText("КОМП'ЮТЕР TITAN ГОТОВИЙ. ВВЕДІТЬ ЗАПИТ.\n> _")
        Layout.addWidget(self.ComputerOutput, 1)
        return Page

    def AskComputer(self):
        Text = self.ComputerInput.text()
        Text = str(Text).strip()
        if not Text:
            return
        self.ComputerOutput.append("\n> " + Text)
        self.ComputerInput.clear()
        Copilot = self.KernelRef.Module("copilot")
        Computer = Copilot.getAI()
        Result = Computer.askAI(Text)
        Reply = str(Result) if Result else "[БЕЗ ВІДПОВІДІ]"
        self.ComputerOutput.append(Reply)

    # ──────────────────────────────────────────────── ЖИВІ ДАНІ
    def RefreshMetrics(self):
        from lcars.service.metric import SystemMetrics
        Metrics = SystemMetrics()
        CPU = Metrics.GetCPUUsage()
        RAM = Metrics.GetMemoryUsage()
        Up = Metrics.GetUptime()
        Status = Metrics.GetStatus()
        Procs = Status.get("processes", 0) if isinstance(Status, dict) else 0
        if "CPU" in self.BridgeBlocks:
            self.BridgeBlocks["CPU"].SetValue(str(CPU) + "%")
            self.BridgeBlocks["MEMORY"].SetValue(str(RAM) + "%")
            self.BridgeBlocks["UPTIME"].SetValue(self.FmtUptime(Up))
            self.BridgeBlocks["PROCESSES"].SetValue(str(Procs))

    def FmtUptime(self, Seconds):
        Seconds = int(Seconds)
        H = Seconds // 3600
        M = (Seconds % 3600) // 60
        return f"{H}h{M:02d}m"

    def RefreshMemory(self):
        Mem = self.KernelRef.Module("memory")
        Stats = Mem.GetMemoryStats()
        if "CHIPS" in self.MemBlocks:
            self.MemBlocks["CHIPS"].SetValue(str(Stats.get("chips", "--")))
            self.MemBlocks["SESSIONS"].SetValue(str(Stats.get("sessions", "--")))
            self.MemBlocks["DIALOGS"].SetValue(str(Stats.get("dialogs", "--")))
            self.MemBlocks["CONTEXTS"].SetValue(str(Stats.get("contexts", "--")))

    def RefreshClockStats(self):
        if self.ActivePage == "BRIDGE":
            self.RefreshMetrics()
        if self.ActivePage == "MEMORY":
            self.RefreshMemory()

    # ──────────────────────────────────────────────── ПОДІЇ
    def SubscribeEvents(self):
        ODN.Channel("Telemetry.Event").Connect(self.OnTelemetry)

    def OnTelemetry(self, Payload):
        if isinstance(Payload, dict):
            Source = str(Payload.get("source", "TELEMETRY")).upper()
            Level = str(Payload.get("level", "INFO")).upper()
            Message = str(Payload.get("message", ""))
            Line = ">> " + Source + " [" + Level + "]: " + Message
        else:
            Line = str(Payload)
        self.LiveLog.append(Line)
        if len(self.LiveLog) > 400:
            self.LiveLog = self.LiveLog[-400:]

    # ──────────────────────────────────────────────── РЕЖИМИ
    def ToggleMode(self):
        modes = ["NOMINAL", "YELLOW ALERT", "RED ALERT"]
        idx = modes.index(self.CurrentMode)
        self.CurrentMode = modes[(idx + 1) % len(modes)]
        self.TopStatus.SetText("STATUS: " + self.CurrentMode)
        if self.CurrentMode == "RED ALERT":
            ODN.Emit("System.Phase.Emergency")

    def ToggleLanguage(self):
        langs = ["ENG", "UKR"]
        idx = langs.index(self.CurrentLanguage)
        self.CurrentLanguage = langs[(idx + 1) % len(langs)]
        if self.CurrentLanguage == "UKR":
            self.TopStatus.SetText("СИСТЕМА ЛКАРС")
            for K in self.NavButtons:
                self.NavButtons[K].SetText(self.UkrName(K))
        else:
            self.TopStatus.SetText("LCARS TITAN V9.0")
            for K in self.NavButtons:
                self.NavButtons[K].SetText(K)

    def UkrName(self, K):
        M = {"ENGINEERING": "ІНЖЕНЕРІЯ", "BRIDGE": "МІСТОК", "SCIENCE": "НАУКА", "NAVIGATION": "НАВІГАЦІЯ", "TACTICAL": "ТАКТИКА", "COMM": "ЗВ'ЯЗОК", "LIBRARY": "БІБЛІОТЕКА", "STORAGE": "СХОВИЩЕ", "MEMORY": "ПАМ'ЯТЬ", "PROGRAMS": "ПРОГРАМИ", "SETTINGS": "НАЛАШТУВАННЯ", "DATABASE": "БАЗА", "MEDICAL": "МЕДИЦИНА", "COMPUTER": "КОМП'ЮТЕР", "MODE": "РЕЖИМ", "LANG": "МОВА", "NETWORK": "МЕРЕЖА", "LOCK": "БЛОК", "EMERGENCY": "ТРИВОГА"}
        return M.get(K, K)

    def RequestLock(self):
        ODN.Emit("System.Phase.Lock")

    # ──────────────────────────────────────────────── ГОДИННИК І БІЖУЧИЙ РЯДОК
    def StartClock(self):
        self.ClockTimer = LCARS.Timer(self.widget)
        self.ClockTimer.setInterval(1000)
        self.ClockTimer.timeout.connect(self.TickClock)
        self.ClockTimer.start()

    def TickClock(self):
        Now = datetime.now().strftime("%H:%M:%S")
        if self.CurrentLanguage == "UKR":
            self.FooterStatus.SetText("РОБОЧИЙ СТІЛ // " + Now)
        else:
            self.FooterStatus.SetText("CORE DESKTOP ONLINE // " + Now)

    def StartTicker(self):
        self.TickerTimer = LCARS.Timer(self.widget)
        self.TickerTimer.setInterval(120)
        self.TickerTimer.timeout.connect(self.TickTicker)
        self.TickerTimer.start()

    def TickTicker(self):
        Messages = [
            "ODN LINK STABLE",
            "KERNEL: " + self.KernelRef.Phase.name,
            "TITAN AI ONLINE",
            "ISOLINEAR BANK NOMINAL",
            "SENSOR GRID ACTIVE",
        ]
        Scroll = "   ◆   ".join(Messages)
        self.TickerPhase = (self.TickerPhase + 1) % len(Scroll)
        self.Ticker.SetText(Scroll[self.TickerPhase:] + Scroll[:self.TickerPhase])
