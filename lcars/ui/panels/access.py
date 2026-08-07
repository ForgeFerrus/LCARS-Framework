# Панель системного доступу LCARS.
# Це не окремий системний лаунчер і не зовнішній пульт. Панель працює як частина
# бортового інтерфейсу: показує стан ядра, живу телеметрію, доступні маршрути
# та відправляє команди в ODN, щоб їх обробляли системні служби LCARS.
# Небезпечні дії тут не виконуються напряму. Кнопка тільки ставить команду в
# чергу й показує її в журналі, а реальне виконання має проходити через сервіс
# команд або аварійний контур.

import sys
import time
from datetime import datetime
from pathlib import Path

import psutil

ProjectRoot = str(Path(__file__).resolve().parents[3])
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from lcars.base.default import Palette
from lcars.base.type import LCARS
from lcars.base.component import LCARSBar, LCARSButton, LCARSLabel, LCARSElbow, Primitive
from lcars.base.interface import Segment, Panel
from lcars.base.animation import DiagnosticGrid
from lcars.core.signal import ODN


# Збирає коротку телеметрію без запуску зовнішніх програм.
# Панель оновлює ці значення таймером і не блокує головний інтерфейс.
def ReadTelemetry():
    Memory = psutil.virtual_memory()
    Disk = psutil.disk_usage(str(Path.cwd().anchor or Path.cwd()))
    Uptime = int(time.time() - psutil.boot_time())
    return {
        "CORE": f"{psutil.cpu_percent(interval=0.0):.0f}%",
        "MEMORY": f"{Memory.percent:.0f}%",
        "STORAGE": f"{Disk.percent:.0f}%",
        "UPTIME": f"{Uptime // 3600}H {(Uptime % 3600) // 60}M",
    }


# Малий допоміжний стиль для LCARS-карток.
# Він тримає форму панелей однаковою без локальних випадкових кольорів.
def StyleCard(Widget, BorderColor, FillColor=None, Radius=20):
    Fill = FillColor or Palette.Background
    Widget.setStyleSheet(
        "background-color: "
        + Fill
        + "; border: 1px solid "
        + BorderColor
        + "; border-radius: "
        + str(Radius)
        + "px;"
    )


# Панель доступу збирає керування сесією, стан системи й журнал команд.
# Вона не дублює desktop, а дає системний вузол для діагностики й переходів.
class SystemAccess(Segment):
    def __init__(self, DesktopNodeRef=None, ParentNode=None):
        super().__init__(Parent=ParentNode)
        self.DesktopNode = DesktopNodeRef
        self.TelemetryLabels = {}
        self.CommandLog = []
        self.PendingCommand = ""
        self.widget.setStyleSheet("background-color: " + Palette.Background + "; border: none;")
        self.Build()
        self.StartTimers()

    # Створює головну структуру: верхній статус, ліві команди, центр телеметрії,
    # правий журнал і нижню лінію стану.
    def Build(self):
        Root = self.Vertical(14, 14, 14, 14, 10)

        self.BuildHeader(Root)

        Body = Segment(Parent=self.widget)
        BodyLayout = LCARS.Horizontal(Body.widget)
        BodyLayout.setContentsMargins(0, 0, 0, 0)
        BodyLayout.setSpacing(14)

        self.BuildCommandRail(Body, BodyLayout)
        self.BuildTelemetryCore(Body, BodyLayout)
        self.BuildSystemJournal(Body, BodyLayout)

        Root.addWidget(Body.widget, 1)
        self.BuildFooter(Root)

        self.AddLog("ACCESS NODE ONLINE")
        self.AddLog("ODN COMMAND ROUTE READY")
        self.AddLog("DIRECT SYSTEM ACTIONS ARE QUEUED THROUGH LCARS")

    # Верхня LCARS-лінія задає контекст панелі і показує активний маршрут.
    def BuildHeader(self, Root):
        Header = Segment(Parent=self.widget)
        Layout = LCARS.Horizontal(Header.widget)
        Layout.setContentsMargins(0, 0, 0, 0)
        Layout.setSpacing(8)

        Elbow = LCARSElbow(Direction="top-left", Color=Palette.Panels[0], Parent=Header.widget)
        Elbow.widget.setFixedSize(120, 58)
        Layout.addWidget(Elbow.widget)

        TitleBar = LCARSBar(Type="rect", Color=Palette.Panels[2], Height=58, Parent=Header.widget)
        TitleLayout = LCARS.Horizontal(TitleBar.widget)
        TitleLayout.setContentsMargins(18, 0, 18, 0)
        self.Title = LCARSLabel(
            Text="SYSTEM ACCESS / COMMAND CONTROL",
            Color=Palette.Background,
            FontSize=20,
            Parent=TitleBar.widget,
        )
        TitleLayout.addWidget(self.Title.widget)
        TitleLayout.addStretch(1)
        Layout.addWidget(TitleBar.widget, 1)

        StatusCap = LCARSBar(Type="rect-right", Color=Palette.YellowAlert[1], Width=96, Height=58, Parent=Header.widget)
        Layout.addWidget(StatusCap.widget)
        Root.addWidget(Header.widget)

    # Лівий рейл містить тільки маршрути і запити. Він не запускає ОС-команди
    # напряму, щоб LCARS лишався єдиним середовищем керування.
    def BuildCommandRail(self, Body, BodyLayout):
        Rail = Panel(Parent=Body.widget)
        Rail.widget.setMinimumWidth(260)
        Rail.widget.setMaximumWidth(300)
        StyleCard(Rail.widget, Palette.Panels[0], Palette.Background, 24)
        Layout = Rail.Vertical(14, 14, 14, 14, 8)

        Label = LCARSLabel(Text="COMMAND ROUTES", Color=Palette.Panels[2], FontSize=20, Parent=Rail.widget)
        Label.widget.setStyleSheet("background-color: transparent; border: none;")
        Layout.addWidget(Label.widget)

        Commands = [
            ("LOCK", "lock", Palette.Panels[0]),
            ("SWITCH USER", "switch-user", Palette.Panels[1]),
            ("BIOS / UEFI", "bios", Palette.YellowAlert[2]),
            ("DIAGNOSTICS", "diagnostics", Palette.Panels[2]),
            ("RESTART REQUEST", "restart", Palette.YellowAlert[1]),
            ("SHUTDOWN REQUEST", "shutdown", Palette.RedAlert[0]),
        ]

        for Text, Command, Color in Commands:
            Button = LCARSButton(Text=Text, Type="soft-left", Color=Color, Parent=Rail.widget)
            Button.widget.setFixedHeight(46)
            Button.clicked.connect(lambda Checked=False, Current=Command: self.QueueCommand(Current))
            Layout.addWidget(Button.widget)

        Layout.addStretch(1)
        BodyLayout.addWidget(Rail.widget)
        self.CommandRail = Rail

    # Центральна зона показує живий стан системи, щоб панель була діагностичною,
    # а не просто набором кнопок.
    def BuildTelemetryCore(self, Body, BodyLayout):
        Core = Panel(Parent=Body.widget)
        StyleCard(Core.widget, Palette.Panels[1], Palette.Background, 24)
        Layout = Core.Vertical(16, 16, 16, 16, 12)

        Top = Segment(Parent=Core.widget)
        TopLayout = LCARS.Horizontal(Top.widget)
        TopLayout.setContentsMargins(0, 0, 0, 0)
        TopLayout.setSpacing(10)

        Pulse = Primitive(Shape="circle", Color=Palette.Panels[2], Parent=Top.widget)
        Pulse.widget.setFixedSize(38, 38)
        TopLayout.addWidget(Pulse.widget)

        self.CoreTitle = LCARSLabel(Text="BOARD COMPUTER LINK", Color=Palette.Panels[2], FontSize=26, Parent=Top.widget)
        self.CoreTitle.widget.setStyleSheet("background-color: transparent; border: none;")
        TopLayout.addWidget(self.CoreTitle.widget)
        TopLayout.addStretch(1)
        Layout.addWidget(Top.widget)

        Grid = Segment(Parent=Core.widget)
        GridLayout = LCARS.Horizontal(Grid.widget)
        GridLayout.setContentsMargins(0, 0, 0, 0)
        GridLayout.setSpacing(10)

        for Name, Color in [
            ("CORE", Palette.Panels[0]),
            ("MEMORY", Palette.Panels[1]),
            ("STORAGE", Palette.YellowAlert[2]),
            ("UPTIME", Palette.YellowAlert[1]),
        ]:
            Tile = Panel(Parent=Grid.widget)
            StyleCard(Tile.widget, Color, Palette.Background, 18)
            TileLayout = Tile.Vertical(10, 10, 10, 10, 4)
            NameLabel = LCARSLabel(Text=Name, Color=Color, FontSize=13, Parent=Tile.widget)
            NameLabel.widget.setStyleSheet("background-color: transparent; border: none;")
            ValueLabel = LCARSLabel(Text="--", Color=Palette.Panels[2], FontSize=24, Parent=Tile.widget)
            ValueLabel.widget.setStyleSheet("background-color: transparent; border: none;")
            TileLayout.addWidget(NameLabel.widget)
            TileLayout.addWidget(ValueLabel.widget)
            GridLayout.addWidget(Tile.widget, 1)
            self.TelemetryLabels[Name] = ValueLabel

        Layout.addWidget(Grid.widget)

        Scan = DiagnosticGrid(Parent=Core.widget, Color=Palette.Panels[1])
        Scan.widget.setMinimumHeight(180)
        Layout.addWidget(Scan.widget, 1)

        BodyLayout.addWidget(Core.widget, 1)
        self.TelemetryCore = Core

    # Правий журнал показує, що саме запитано і через який системний маршрут.
    # Це робить панель прозорою для діагностики.
    def BuildSystemJournal(self, Body, BodyLayout):
        Journal = Panel(Parent=Body.widget)
        Journal.widget.setMinimumWidth(310)
        Journal.widget.setMaximumWidth(380)
        StyleCard(Journal.widget, Palette.Panels[0], Palette.Background, 24)
        Layout = Journal.Vertical(14, 14, 14, 14, 8)

        Title = LCARSLabel(Text="ODN COMMAND JOURNAL", Color=Palette.Panels[2], FontSize=20, Parent=Journal.widget)
        Title.widget.setStyleSheet("background-color: transparent; border: none;")
        Layout.addWidget(Title.widget)

        self.RouteStatus = LCARSLabel(Text="ROUTE: ACCESS", Color=Palette.YellowAlert[2], FontSize=14, Parent=Journal.widget)
        self.RouteStatus.widget.setStyleSheet("background-color: transparent; border: none;")
        Layout.addWidget(self.RouteStatus.widget)

        self.JournalText = LCARS.TextEdit(Journal.widget)
        self.JournalText.setReadOnly(True)
        self.JournalText.setStyleSheet(
            "background-color: "
            + Palette.Background
            + "; color: "
            + Palette.Panels[2]
            + "; border: 1px solid "
            + Palette.Neutral[1]
            + "; border-radius: 14px; padding: 10px; font-family: 'LCARS', Consolas, monospace; font-size: 14px;"
        )
        Layout.addWidget(self.JournalText, 1)

        BodyLayout.addWidget(Journal.widget)
        self.SystemJournal = Journal

    # Нижня лінія показує час, активний вузол і останню команду.
    def BuildFooter(self, Root):
        Footer = Segment(Parent=self.widget)
        Layout = LCARS.Horizontal(Footer.widget)
        Layout.setContentsMargins(0, 0, 0, 0)
        Layout.setSpacing(8)

        self.ClockLabel = LCARSLabel(Text="STARDATE: --", Color=Palette.Background, FontSize=12, Parent=Footer.widget)
        ClockBar = LCARSBar(Type="rect-left", Color=Palette.Panels[1], Height=34, Parent=Footer.widget)
        ClockLayout = LCARS.Horizontal(ClockBar.widget)
        ClockLayout.setContentsMargins(16, 0, 16, 0)
        ClockLayout.addWidget(self.ClockLabel.widget)
        Layout.addWidget(ClockBar.widget, 1)

        self.CommandState = LCARSLabel(Text="COMMAND QUEUE: IDLE", Color=Palette.Background, FontSize=12, Parent=Footer.widget)
        StateBar = LCARSBar(Type="rect-right", Color=Palette.YellowAlert[2], Width=360, Height=34, Parent=Footer.widget)
        StateLayout = LCARS.Horizontal(StateBar.widget)
        StateLayout.setContentsMargins(16, 0, 16, 0)
        StateLayout.addWidget(self.CommandState.widget)
        Layout.addWidget(StateBar.widget)

        Root.addWidget(Footer.widget)

    # Таймери оновлюють живі дані без ручного перемальовування екрана.
    def StartTimers(self):
        self.TelemetryTimer = LCARS.Timer(self.widget)
        self.TelemetryTimer.timeout.connect(self.UpdateTelemetry)
        self.TelemetryTimer.start(2000)

        self.ClockTimer = LCARS.Timer(self.widget)
        self.ClockTimer.timeout.connect(self.UpdateClock)
        self.ClockTimer.start(1000)

        self.UpdateTelemetry()
        self.UpdateClock()

    # Записує команду в журнал і передає її через ODN.
    # Реальне виконання має робити сервіс команд, не панель інтерфейсу.
    def QueueCommand(self, Command):
        self.PendingCommand = str(Command).upper()
        self.CommandState.SetText("COMMAND QUEUE: " + self.PendingCommand)
        self.AddLog("REQUEST: " + self.PendingCommand)
        ODN.Emit("System.Command.Request", {"source": "SystemAccess", "command": Command})

        if Command == "bios":
            ODN.Emit("System.Phase.Bios")
        if Command == "diagnostics":
            ODN.Emit("System.Diagnostics.Request", {"source": "SystemAccess"})
        if Command == "lock":
            ODN.Emit("System.Phase.Access")

    # Оновлює показники ядра, пам'яті, диска й часу роботи.
    def UpdateTelemetry(self):
        Telemetry = ReadTelemetry()
        for Name, Value in Telemetry.items():
            Label = self.TelemetryLabels.get(Name)
            if Label is not None:
                Label.SetText(Value)

    # Оновлює системний час у нижній LCARS-лінії.
    def UpdateClock(self):
        Now = datetime.now()
        self.ClockLabel.SetText("STARDATE: " + Now.strftime("%Y.%m.%d") + " / " + Now.strftime("%H:%M:%S"))

    # Додає рядок у журнал і тримає його коротким, щоб екран не перетворювався
    # на нескінченний дамп.
    def AddLog(self, Message):
        Stamp = datetime.now().strftime("%H:%M:%S")
        self.CommandLog.append("[" + Stamp + "] " + str(Message))
        self.CommandLog = self.CommandLog[-18:]
        self.JournalText.setPlainText("\n".join(self.CommandLog))
