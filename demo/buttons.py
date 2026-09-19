# LCARS FULLSCREEN TACTICAL INTERFACE & BUTTON CATALOG
# Standard: Titanium (Zero-Except, Pure PascalCase, Zero Underscores)

from lcars.base.type import LCARS
from lcars.base.interface import Screen, Panel
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
from lcars.base.animation import DataStream
from lcars.base.default import SystemTheme
from lcars.system.power import PowerControl

def ButtonsInterface():
    MainScreen = Screen(Title="LCARS FULLSCREEN TACTICAL TERMINAL")
    MainScreen.SetVertical(10, 14, 10, 14, Spacing=8)

    # 1. ВЕРХНІЙ ГОРИЗОНТ: ШАПКА З НАВІГАЦІЄЮ ТА СТАТУСОМ
    TopBar = Panel()
    TopBar.SetHorizontal(0, 0, 0, 0, Spacing=8)

    TopElbow = LCARSElbow(
        Corner="top-left",
        Text="LCARS 47",
        Number="SEC-TAC",
        Width=240,
        Height=54,
        Thickness=22,
        Radius=18
    )
    TopBar.Add(TopElbow)

    TopTitle = LCARSLabel(
        Text="STARFLEET TACTICAL INTERFACE // CANONICAL BUTTON MATRIX",
        FontSize=20,
        Align="left",
        Height=36
    )
    TopBar.Add(TopTitle, 1)

    BtnExit = LCARSButton(
        Text="EXIT FULLSCREEN",
        Form=LCARSButton.PillHalf,
        Direction=0,
        Width=190,
        Height=36,
        Sound="click"
    )
    TopBar.Add(BtnExit)

    MainScreen.Add(TopBar)

    # 2. ГОЛОВНА ТРИКОЛОНКОВА РОБОЧА СЦЕНА
    WorkArea = Panel()
    WorkArea.SetHorizontal(0, 0, 0, 0, Spacing=14)

    # ─── КОЛОНКА 1: КАНОНІЧНІ ФОРМИ КНОПОК ───
    Col1 = Panel()
    Col1.SetVertical(0, 0, 0, 0, Spacing=6)

    LblForms = LCARSLabel(Text="CANONICAL FORMS", Height=24)
    Col1.Add(LblForms)

    FormButtons = []
    FormData = [
        ("RECT BUTTON",    "01-RCT", LCARSButton.RectType,     0),
        ("PILL CAPSULE",   "02-PIL", LCARSButton.PillType,     0),
        ("SOFT CHAMFER",   "03-SFT", LCARSButton.SoftType,     0),
        ("PILL-HALF EAST", "04-PHE", LCARSButton.PillHalfType, 0),
        ("PILL-HALF WEST", "05-PHW", LCARSButton.PillHalfType, 180),
        ("SOFT-HALF EAST", "06-SHE", LCARSButton.SoftHalfType, 0),
        ("SOFT-HALF WEST", "07-SHW", LCARSButton.SoftHalfType, 180),
    ]

    for TextVal, NumVal, FormVal, DirVal in FormData:
        B = LCARSButton(
            Text=TextVal,
            Number=NumVal,
            SwapMode=True,
            Form=FormVal,
            Direction=DirVal,
            Width=240,
            Height=40,
            Sound="click"
        )
        FormButtons.append(B)
        Col1.Add(B)

    Col1.Add(LCARSBar(Height=3))

    Col1Ind = Panel()
    Col1Ind.SetHorizontal(0, 0, 0, 0, Spacing=6)
    Col1Ind.Add(LCARSIndicator(Form=LCARSIndicator.RectType, Width=76, Height=26))
    Col1Ind.Add(LCARSIndicator(Form=LCARSIndicator.SoftType, Width=76, Height=26))
    Col1Ind.Add(LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=76, Height=26))
    Col1.Add(Col1Ind)

    Col1.AddStretch(1)
    WorkArea.Add(Col1)

    # ─── КОЛОНКА 2: ЦЕНТРАЛЬНА ТЕЛЕМЕТРІЯ ТА СТАТУС ───
    Col2 = Panel()
    Col2.SetVertical(0, 0, 0, 0, Spacing=6)

    LblReadout = LCARSLabel(Text="SYSTEM READOUT & TELEMETRY", Height=24)
    Col2.Add(LblReadout)

    MonitorCard = Panel()
    MonitorCard.SetVertical(8, 10, 8, 10, Spacing=4)

    SysStateLabel = LCARSLabel(
        Text="CONDITION GREEN // ALL SUBSYSTEMS NOMINAL",
        FontSize=20,
        Align="left",
        Height=32
    )
    MonitorCard.Add(SysStateLabel)

    SelectionLabel = LCARSLabel(
        Text="TOUCH ANY BUTTON TO ENGAGE ODN TELEMETRY",
        Align="left",
        Height=24
    )
    MonitorCard.Add(SelectionLabel)

    TelemetryLine = LCARSLabel(
        Text="ODN OPTICAL CARRIER ONLINE // EPS MATRIX SYNCHRONIZED",
        Align="left",
        Height=24
    )
    MonitorCard.Add(TelemetryLine)

    Col2.Add(MonitorCard)

    StreamTitle = LCARSLabel(Text="TACTICAL DATASTREAM", Height=22)
    Col2.Add(StreamTitle)

    TelemetryStream = DataStream(
        Width=460,
        Height=140,
        Rows=5
    )
    TelemetryStream.Lines = [
        "ISOLINEAR OPTICAL BUS // VERIFYING",
        "EPS POWER COUPLING // SYNCHRONIZING",
        "ODN SUBSURFACE CARRIER // OPERATIONAL",
        "LCARS 47-ALPHA CORE // HANDSHAKE READY",
        "TACTICAL INTERFACE MATRIX // ONLINE",
    ]
    Col2.Add(TelemetryStream)

    LblIndicators = LCARSLabel(Text="OPTICAL PULSE INDICATORS", Height=22)
    Col2.Add(LblIndicators)

    CenterInd = Panel()
    CenterInd.SetHorizontal(0, 0, 0, 0, Spacing=6)
    CenterInd.Add(LCARSIndicator(Form=LCARSIndicator.RectType, Width=146, Height=30))
    CenterInd.Add(LCARSIndicator(Form=LCARSIndicator.SoftType, Width=146, Height=30))
    CenterInd.Add(LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=146, Height=30))
    Col2.Add(CenterInd)

    Col2.AddStretch(1)
    WorkArea.Add(Col2, 1)

    # ─── КОЛОНКА 3: ОПЕРАЦІЙНІ ДИРЕКТИВИ ТА КЕРУВАННЯ ───
    Col3 = Panel()
    Col3.SetVertical(0, 0, 0, 0, Spacing=6)

    LblDirectives = LCARSLabel(Text="TACTICAL DIRECTIVES", Height=24)
    Col3.Add(LblDirectives)

    def SelectReport(TitleStr, CodeStr, DetailStr=""):
        SelectionLabel.SetText(f"ENGAGED: {TitleStr} [{CodeStr}]")
        if DetailStr:
            TelemetryLine.SetText(DetailStr)

    for TextVal, NumVal, FormVal, DirVal in FormData:
        def MakeHandler(T=TextVal, N=NumVal, D=DirVal):
            return lambda: SelectReport(T, N, f"FORM TOPOLOGY PROCESSED // DIRECTION: {D} DEG")
        BtnNode = Col1.Items.get(str(id(FormButtons[len(Col3.Items)]))) if False else None

    for Idx, BtnObj in enumerate(FormButtons):
        TName, CNum, _, CDir = FormData[Idx]
        BtnObj.Clicked.Connect(lambda T=TName, C=CNum, D=CDir: SelectReport(T, C, f"GEOMETRY SYNTHESIZED // DIR: {D} DEG"))

    # Кнопки тривоги одразу у своїх станах з власними динамічними циклами
    BtnRed = LCARSButton(
        Text="RED ALERT",
        Number="01-RED",
        SwapMode=True,
        Form=LCARSButton.Pill,
        State="alert",
        Sound="alertred",
        Width=240,
        Height=40
    )
    def EngageRed():
        SystemTheme.SetSystemState("Red")
        MainScreen.SetState("Red")
        SysStateLabel.SetText("RED ALERT // TACTICAL SHIELDS ENGAGED")
        SelectReport("RED ALERT", "TACTICAL-01", "ALL CONDUITS REDIRECTED TO DEFENSIVE SYSTEMS")
    BtnRed.Clicked.Connect(EngageRed)
    Col3.Add(BtnRed)

    BtnYellow = LCARSButton(
        Text="YELLOW ALERT",
        Number="02-YEL",
        SwapMode=True,
        Form=LCARSButton.PillHalf,
        Direction=180,
        State="yellow",
        Sound="alertyellow",
        Width=240,
        Height=40
    )
    def EngageYellow():
        SystemTheme.SetSystemState("Yellow")
        MainScreen.SetState("Yellow")
        SysStateLabel.SetText("YELLOW ALERT // SENSORS ON HIGH READINESS")
        SelectReport("YELLOW ALERT", "TACTICAL-02", "VERIFYING EPS COUPLINGS & WARP STATUS")
    BtnYellow.Clicked.Connect(EngageYellow)
    Col3.Add(BtnYellow)

    BtnGreen = LCARSButton(
        Text="CONDITION GREEN",
        Number="03-GRN",
        SwapMode=True,
        Form=LCARSButton.Pill,
        State="normal",
        Sound="ack",
        Width=240,
        Height=40
    )
    def EngageGreen():
        SystemTheme.SetSystemState("Normal")
        MainScreen.SetState("Normal")
        SysStateLabel.SetText("CONDITION GREEN // ALL SUBSYSTEMS NOMINAL")
        SelectReport("CONDITION GREEN", "TACTICAL-03", "STANDARD ISOLINEAR CRUISE MATRIX RESTORED")
    BtnGreen.Clicked.Connect(EngageGreen)
    Col3.Add(BtnGreen)

    BtnPower = LCARSButton(
        Text="GRID POWER",
        Number="04-PWR",
        SwapMode=True,
        Form=LCARSButton.Pill,
        Sound="ack",
        IsWakeupTrigger=True,
        Width=240,
        Height=40
    )
    def TogglePowerGrid():
        if PowerControl.State != 0:
            PowerControl.PowerOff()
            MainScreen.SetPower(False)
            BtnPower.Power = True
            BtnPower.Refresh()
            SysStateLabel.SetText("POWER OFFLINE // EPS GRID DE-ENERGIZED")
            SelectReport("GRID POWER", "EPS-000", "PRIMARY EPS BUSES SHUT DOWN // MATRIX DARK")
        else:
            PowerControl.PowerOn()
            MainScreen.SetPower(True)
            SysStateLabel.SetText("POWER ONLINE // ALL CIRCUITS ENERGIZED")
            SelectReport("GRID POWER", "EPS-100", "PRIMARY EPS COUPLINGS SYNCHRONIZED")
    BtnPower.Clicked.Connect(TogglePowerGrid)
    Col3.Add(BtnPower)

    BtnLock = LCARSButton(
        Text="STASIS LOCK",
        Number="05-LCK",
        SwapMode=True,
        Form=LCARSButton.PillHalf,
        Direction=0,
        Sound="ack",
        IsWakeupTrigger=True,
        DarkCycle=True,
        Width=240,
        Height=40
    )
    def ToggleStasis():
        if PowerControl.Locked:
            PowerControl.Unlock()
            SelectReport("STASIS LOCK", "UNLOCKED", "TOUCH SENSORS RESPONSIVE // INPUT ALLOWED")
        else:
            PowerControl.Lock()
            SelectReport("STASIS LOCK", "LOCKED", "CONSOLE INPUT BLOCKED // STASIS ACTIVE")
    BtnLock.Clicked.Connect(ToggleStasis)
    Col3.Add(BtnLock)

    BtnSplit = LCARSButton(
        Text="SPLIT SYS",
        Number="47-SPL",
        SplitMode=True,
        Form=LCARSButton.RectType,
        Width=240,
        Height=40,
        Sound="click"
    )
    BtnSplit.Clicked.Connect(lambda: SelectReport("SPLIT MODE", "47-SPL", "DUAL CHANNEL MATRIX ENGAGED"))
    Col3.Add(BtnSplit)

    BtnDark = LCARSButton(
        Text="DARK CYCLE",
        Number="SEC-01",
        Form=LCARSButton.SoftType,
        DarkCycle=True,
        IsWakeupTrigger=True,
        Width=240,
        Height=40,
        Sound="click"
    )
    BtnDark.Clicked.Connect(lambda: SelectReport("DARK CYCLE", "SEC-01", "NIGHT ROTATION ACTIVE"))
    Col3.Add(BtnDark)

    Col3.AddStretch(1)
    WorkArea.Add(Col3)

    MainScreen.Add(WorkArea, 1)

    # 3. НИЖНІЙ ГОРИЗОНТ: ПІДВАЛ ІЗ ПАНЕЛЛЮ ДІЙ
    BottomBar = Panel()
    BottomBar.SetHorizontal(0, 0, 0, 0, Spacing=8)

    FootLabel = LCARSLabel(
        Text="LCARS TACTICAL MATRIX ACTIVE // EPS GRID SYNCHRONIZED // PULSE ENGINE NOMINAL",
        Height=32
    )
    BottomBar.Add(FootLabel, 1)

    BtnResetAll = LCARSButton(
        Text="RESET CONSOLE",
        Form=LCARSButton.PillHalf,
        Direction=180,
        Width=180,
        Height=34,
        Sound="click"
    )
    def ResetConsole():
        SystemTheme.SetSystemState("Normal")
        MainScreen.SetState("Normal")
        if PowerControl.State == 0:
            PowerControl.PowerOn()
            MainScreen.SetPower(True)
        if PowerControl.Locked:
            PowerControl.Unlock()
        SysStateLabel.SetText("CONDITION GREEN // ALL SUBSYSTEMS NOMINAL")
        SelectReport("CONSOLE RESET", "NOMINAL", "DEFAULT ISOLINEAR PARAMETERS RESTORED")
    BtnResetAll.Clicked.Connect(ResetConsole)
    BottomBar.Add(BtnResetAll)

    BtnDataStream = LCARSButton(
        Text="STREAM RUN",
        Form=LCARSButton.PillHalf,
        Direction=0,
        Width=180,
        Height=34,
        Sound="ack"
    )
    BtnDataStream.Clicked.Connect(lambda: TelemetryStream.Start(Speed=0.03))
    BottomBar.Add(BtnDataStream)

    MainScreen.Add(BottomBar)

    def ExitTerminal():
        HostSurface = MainScreen.GetSurface()
        if hasattr(HostSurface, "close"):
            HostSurface.close()

    BtnExit.Clicked.Connect(ExitTerminal)

    TelemetryStream.Start(Speed=0.04)

    MainScreen.Show()
    return MainScreen

LCARS.Launch(ButtonsInterface)