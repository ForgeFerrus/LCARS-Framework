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
    MainScreen.SetHorizontal(14, 14, 14, 14, Spacing=14)

    # =========================================================================
    # ЛІВА КОЛОНА: РАМКА ОКУДИ ТА КАНОНІЧНІ ФОРМИ КНОПОК (260 px)
    # =========================================================================
    LeftCol = Panel()
    LeftCol.SetVertical(0, 0, 0, 0, Spacing=6)
    LeftCol.GetSurface().setFixedWidth(260)

    TopLeftElbow = LCARSElbow(
        Corner="top-left",
        Text="LCARS 47",
        Number="SEC-TAC",
        Width=260,
        Height=64,
        Thickness=24,
        Radius=18
    )
    LeftCol.Add(TopLeftElbow)

    LblForms = LCARSLabel(Text="CANONICAL FORMS", Height=24)
    LeftCol.Add(LblForms)

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
            Width=260,
            Height=38,
            Sound="click"
        )
        FormButtons.append(B)
        LeftCol.Add(B)

    LeftCol.Add(LCARSBar(Height=3))

    LeftIndRow = Panel()
    LeftIndRow.SetHorizontal(0, 0, 0, 0, Spacing=6)
    LeftIndRow.Add(LCARSIndicator(Form=LCARSIndicator.RectType, Width=82, Height=26))
    LeftIndRow.Add(LCARSIndicator(Form=LCARSIndicator.SoftType, Width=82, Height=26))
    LeftIndRow.Add(LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=82, Height=26))
    LeftCol.Add(LeftIndRow)

    BotLeftElbow = LCARSElbow(
        Corner="bottom-left",
        Text="STARFLEET",
        Number="DECK-47",
        Width=260,
        Height=52,
        Thickness=22,
        Radius=18
    )
    LeftCol.Add(BotLeftElbow)
    LeftCol.AddStretch(1)

    MainScreen.Add(LeftCol)

    # =========================================================================
    # ЦЕНТРАЛЬНИЙ ТАКТИЧНИЙ ДЕК: МОНІТОРИНГ, ТЕЛЕМЕТРІЯ ТА ПОТІК ДАНИХ (СТРЕТЧ)
    # =========================================================================
    CenterCol = Panel()
    CenterCol.SetVertical(0, 0, 0, 0, Spacing=8)

    # Верхня інформаційна лінія центру
    CenterTop = Panel()
    CenterTop.SetHorizontal(0, 0, 0, 0, Spacing=8)

    TopTitle = LCARSLabel(
        Text="STARFLEET TACTICAL INTERFACE // PRIMARY SENSOR MATRIX",
        FontSize=20,
        Align="left",
        Height=36
    )
    CenterTop.Add(TopTitle, 1)

    BtnExit = LCARSButton(
        Text="EXIT FULLSCREEN",
        Form=LCARSButton.PillHalf,
        Direction=0,
        Width=180,
        Height=36,
        Sound="click"
    )
    CenterTop.Add(BtnExit)

    CenterCol.Add(CenterTop)
    CenterCol.Add(LCARSBar(Height=4))

    # Центральна картка оперативного стану
    MonitorCard = Panel()
    MonitorCard.SetVertical(10, 14, 10, 14, Spacing=4)

    SysStateLabel = LCARSLabel(
        Text="CONDITION GREEN // ALL SUBSYSTEMS NOMINAL",
        FontSize=20,
        Align="left",
        Height=32
    )
    MonitorCard.Add(SysStateLabel)

    SelectionLabel = LCARSLabel(
        Text="TOUCH ANY SENSOR NODE TO ENGAGE TELEMETRY",
        Align="left",
        Height=24
    )
    MonitorCard.Add(SelectionLabel)

    TelemetryLine = LCARSLabel(
        Text="ODN OPTICAL DATA BUS ONLINE // WAVELENGTH: 1550 NM // EPS MATRIX SYNCHRONIZED",
        Align="left",
        Height=24
    )
    MonitorCard.Add(TelemetryLine)

    CenterCol.Add(MonitorCard)

    # Потік тактичної діагностики
    StreamHeader = LCARSLabel(Text="TACTICAL DATASTREAM // REALTIME ODN LOG", Height=24)
    CenterCol.Add(StreamHeader)

    TelemetryStream = DataStream(
        Width=600,
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
    CenterCol.Add(TelemetryStream)

    # Індикатори оптичних магістралей
    LblConduits = LCARSLabel(Text="PRIMARY OPTICAL CONDUITS", Height=24)
    CenterCol.Add(LblConduits)

    ConduitRow = Panel()
    ConduitRow.SetHorizontal(0, 0, 0, 0, Spacing=8)
    ConduitRow.Add(LCARSIndicator(Form=LCARSIndicator.RectType, Width=120, Height=28))
    ConduitRow.Add(LCARSIndicator(Form=LCARSIndicator.SoftType, Width=120, Height=28))
    ConduitRow.Add(LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=120, Height=28))
    ConduitRow.Add(LCARSIndicator(Form=LCARSIndicator.RectType, Width=120, Height=28))
    CenterCol.Add(ConduitRow)

    CenterCol.AddStretch(1)

    # Підвал центральної сцени
    CenterBottom = Panel()
    CenterBottom.SetHorizontal(0, 0, 0, 0, Spacing=8)

    FootLabel = LCARSLabel(
        Text="LCARS TACTICAL INTERFACE v4.7 // EPS GRID NOMINAL // SYSTEM ACTIVE",
        Height=34
    )
    CenterBottom.Add(FootLabel, 1)

    BtnResetAll = LCARSButton(
        Text="RESET CONSOLE",
        Form=LCARSButton.PillHalf,
        Direction=180,
        Width=160,
        Height=34,
        Sound="click"
    )
    CenterBottom.Add(BtnResetAll)

    BtnRunStream = LCARSButton(
        Text="CYCLE STREAM",
        Form=LCARSButton.PillHalf,
        Direction=0,
        Width=160,
        Height=34,
        Sound="ack"
    )
    CenterBottom.Add(BtnRunStream)

    CenterCol.Add(CenterBottom)

    MainScreen.Add(CenterCol, 1)

    # =========================================================================
    # ПРАВА КОЛОНА: ТАКТИЧНІ ДИРЕКТИВИ ТА ЕНЕРГОСИСТЕМА (260 px)
    # =========================================================================
    RightCol = Panel()
    RightCol.SetVertical(0, 0, 0, 0, Spacing=6)
    RightCol.GetSurface().setFixedWidth(260)

    TopRightElbow = LCARSElbow(
        Corner="top-right",
        Text="DIRECTIVES",
        Number="DIR-01",
        Width=260,
        Height=64,
        Thickness=24,
        Radius=18
    )
    RightCol.Add(TopRightElbow)

    LblDirectives = LCARSLabel(Text="TACTICAL DIRECTIVES", Height=24)
    RightCol.Add(LblDirectives)

    def SelectReport(TitleStr, CodeStr, DetailStr=""):
        SelectionLabel.SetText(f"ENGAGED: {TitleStr} [{CodeStr}]")
        if DetailStr:
            TelemetryLine.SetText(DetailStr)

    for Idx, BtnObj in enumerate(FormButtons):
        TName, CNum, _, CDir = FormData[Idx]
        BtnObj.Clicked.Connect(lambda T=TName, C=CNum, D=CDir: SelectReport(T, C, f"GEOMETRY SYNTHESIZED // DIRECTION: {D} DEG"))

    # Кнопки тривоги одразу у своїх станах з власними динамічними циклами
    BtnRed = LCARSButton(
        Text="RED ALERT",
        Number="01-RED",
        SwapMode=True,
        Form=LCARSButton.Pill,
        State="alert",
        Sound="alertred",
        Width=260,
        Height=40
    )
    def EngageRed():
        SystemTheme.SetSystemState("Red")
        MainScreen.SetState("Red")
        SysStateLabel.SetText("RED ALERT // TACTICAL SHIELDS ENGAGED")
        SelectReport("RED ALERT", "TACTICAL-01", "ALL CONDUITS REDIRECTED TO DEFENSIVE SYSTEMS")
    BtnRed.Clicked.Connect(EngageRed)
    RightCol.Add(BtnRed)

    BtnYellow = LCARSButton(
        Text="YELLOW ALERT",
        Number="02-YEL",
        SwapMode=True,
        Form=LCARSButton.PillHalf,
        Direction=180,
        State="yellow",
        Sound="alertyellow",
        Width=260,
        Height=40
    )
    def EngageYellow():
        SystemTheme.SetSystemState("Yellow")
        MainScreen.SetState("Yellow")
        SysStateLabel.SetText("YELLOW ALERT // SENSORS ON HIGH READINESS")
        SelectReport("YELLOW ALERT", "TACTICAL-02", "VERIFYING EPS COUPLINGS & WARP STATUS")
    BtnYellow.Clicked.Connect(EngageYellow)
    RightCol.Add(BtnYellow)

    BtnGreen = LCARSButton(
        Text="CONDITION GREEN",
        Number="03-GRN",
        SwapMode=True,
        Form=LCARSButton.Pill,
        State="normal",
        Sound="ack",
        Width=260,
        Height=40
    )
    def EngageGreen():
        SystemTheme.SetSystemState("Normal")
        MainScreen.SetState("Normal")
        SysStateLabel.SetText("CONDITION GREEN // ALL SUBSYSTEMS NOMINAL")
        SelectReport("CONDITION GREEN", "TACTICAL-03", "STANDARD ISOLINEAR CRUISE MATRIX RESTORED")
    BtnGreen.Clicked.Connect(EngageGreen)
    RightCol.Add(BtnGreen)

    PowerActive = {"Online": True}

    BtnPower = LCARSButton(
        Text="GRID POWER",
        Number="04-PWR",
        SwapMode=True,
        Form=LCARSButton.Pill,
        Sound="ack",
        IsWakeupTrigger=True,
        Width=260,
        Height=40
    )
    def TogglePowerGrid():
        if PowerControl.State != 0:
            PowerControl.PowerOff()
        if PowerActive["Online"]:
            PowerActive["Online"] = False
            MainScreen.SetPower(False)
            BtnPower.Power = True
            BtnPower.Tactile = True
            BtnPower.Refresh()
            SysStateLabel.SetText("POWER OFFLINE // EPS GRID DE-ENERGIZED")
            SelectReport("GRID POWER", "EPS-000", "PRIMARY EPS BUSES SHUT DOWN // MATRIX DARK")
            SysStateLabel.SetText("INTERFACE OFFLINE // DISPLAY MUTED")
            SelectReport("INTERFACE OFF", "PWR-OFF", "INTERFACE BLANKED // TOUCH AGAIN TO RESTORE")
        else:
            PowerControl.PowerOn()
            PowerActive["Online"] = True
            MainScreen.SetPower(True)
            SysStateLabel.SetText("POWER ONLINE // ALL CIRCUITS ENERGIZED")
            SelectReport("GRID POWER", "EPS-100", "PRIMARY EPS COUPLINGS SYNCHRONIZED")
            BtnPower.Power = True
            BtnPower.Tactile = True
            MainScreen.Refresh()
            SysStateLabel.SetText("CONDITION GREEN // ALL CIRCUITS ENERGIZED")
            SelectReport("INTERFACE ON", "PWR-ON", "INTERFACE ONLINE // ALL CIRCUITS RESTORED")
    BtnPower.Clicked.Connect(TogglePowerGrid)
    RightCol.Add(BtnPower)

    BtnLock = LCARSButton(
        Text="STASIS LOCK",
        Number="05-LCK",
        SwapMode=True,
        Form=LCARSButton.PillHalf,
        Direction=0,
        Sound="ack",
        IsWakeupTrigger=True,
        DarkCycle=True,
        Width=260,
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
    RightCol.Add(BtnLock)

    BtnSplit = LCARSButton(
        Text="SPLIT SYS",
        Number="47-SPL",
        SplitMode=True,
        Form=LCARSButton.RectType,
        Width=260,
        Height=40,
        Sound="click"
    )
    BtnSplit.Clicked.Connect(lambda: SelectReport("SPLIT MODE", "47-SPL", "DUAL CHANNEL MATRIX ENGAGED"))
    RightCol.Add(BtnSplit)

    BtnDark = LCARSButton(
        Text="DARK CYCLE",
        Number="SEC-01",
        Form=LCARSButton.SoftType,
        DarkCycle=True,
        IsWakeupTrigger=True,
        Width=260,
        Height=40,
        Sound="click"
    )
    BtnDark.Clicked.Connect(lambda: SelectReport("DARK CYCLE", "SEC-01", "NIGHT ROTATION ACTIVE"))
    RightCol.Add(BtnDark)

    RightCol.Add(LCARSBar(Height=3))

    BotRightElbow = LCARSElbow(
        Corner="bottom-right",
        Text="COMMAND",
        Number="CORE-01",
        Width=260,
        Height=52,
        Thickness=22,
        Radius=18
    )
    RightCol.Add(BotRightElbow)
    RightCol.AddStretch(1)

    MainScreen.Add(RightCol)

    # Обробники дій підвалу
    def ResetConsole():
        SystemTheme.SetSystemState("Normal")
        MainScreen.SetState("Normal")
        if PowerControl.State == 0:
            PowerControl.PowerOn()
            MainScreen.SetPower(True)
        PowerActive["Online"] = True
        MainScreen.SetPower(True)
        BtnPower.Power = True
        BtnPower.Tactile = True
        if PowerControl.Locked:
            PowerControl.Unlock()
        SysStateLabel.SetText("CONDITION GREEN // ALL SUBSYSTEMS NOMINAL")
        SelectReport("CONSOLE RESET", "NOMINAL", "DEFAULT ISOLINEAR PARAMETERS RESTORED")

    BtnResetAll.Clicked.Connect(ResetConsole)
    BtnRunStream.Clicked.Connect(lambda: TelemetryStream.Start(Speed=0.03))

    def ExitTerminal():
        HostSurface = MainScreen.GetSurface()
        if hasattr(HostSurface, "close"):
            HostSurface.close()

    BtnExit.Clicked.Connect(ExitTerminal)

    TelemetryStream.Start(Speed=0.04)

    MainScreen.Show()
    return MainScreen

LCARS.Launch(ButtonsInterface)