# LCARS FULLSCREEN INTERFACE & CANONICAL BUTTON CATALOG
# Standard: Titanium (Pure LCARS Surface Rendering)

from lcars.base.type import LCARS
from lcars.base.interface import Screen, Panel, Header, Footer
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
from lcars.base.animation import TextDecode, Typewriter, DataStream, Reveal, Stagger
from lcars.base.default import SystemTheme
from lcars.system.power import PowerControl

def ButtonsInterface():
    MainScreen = Screen(Title="LCARS FULLSCREEN INTERFACE // BUTTON MATRIX")
    MainScreen.SetVertical(10, 14, 10, 14, Spacing=8)

    # 1. ВЕРХНЯ КОНСОЛЬНА СМУГА З НАВІГАЦІЄЮ ТА ВИХОДОМ
    TopBar = Panel()
    TopBar.SetHorizontal(0, 0, 0, 0, Spacing=8)

    TopElbow = LCARSElbow(Corner="top-left", Text="LCARS 47", Number="SEC-TAC", Width=220, Height=54, Thickness=22, Radius=18)
    TopBar.Add(TopElbow)

    TopTitle = LCARSLabel(Text="STARFLEET TACTICAL INTERFACE // CANONICAL BUTTON MATRIX", FontSize=20, Align="left", Height=36)
    TopBar.Add(TopTitle, 1)

    BtnExit = LCARSButton(Text="EXIT FULLSCREEN", Form=LCARSButton.PillHalf, Direction=0, Width=180, Height=36, Sound="click")
    TopBar.Add(BtnExit)

    MainScreen.Add(TopBar)

    # 2. ЦЕНТРАЛЬНИЙ РОБОЧИЙ ПРОСТІР
    WorkArea = Panel()
    WorkArea.SetVertical(0, 0, 0, 0, Spacing=0)

    # =========================================================================
    # ЕКРАН 1: СТАН ОЧІКУВАННЯ ТА ІНІЦІАЛІЗАЦІЯ (STANDBY / BOOT)
    # =========================================================================
    BootScreen = Panel()
    BootScreen.SetVertical(20, 20, 20, 20, Spacing=16)

    StatusLabel = LCARSLabel(
        Text="STANDBY MODE // SYSTEM OFFLINE",
        FontSize=24,
        Align="center",
        Width=900,
        Height=40
    )
    BootScreen.Add(StatusLabel)

    PromptLabel = LCARSLabel(
        Text="PRESS INITIALIZE TO ENGAGE LCARS INTERFACE MATRIX",
        Align="center",
        Width=900,
        Height=28
    )
    BootScreen.Add(PromptLabel)

    ButtonRow = Panel()
    ButtonRow.SetHorizontal(0, 0, 0, 0, Spacing=0)
    ButtonRow.AddStretch(1)

    StartButton = LCARSButton(
        Text="INITIALIZE SYSTEM",
        Form=LCARSButton.Pill,
        Width=380,
        Height=52,
        Sound="ack"
    )
    ButtonRow.Add(StartButton)
    ButtonRow.AddStretch(1)
    BootScreen.Add(ButtonRow)

    TelemetryStream = DataStream(
        Width=900,
        Height=180,
        Rows=6
    )
    TelemetryStream.Lines = [
        "ISOLINEAR OPTICAL BUS // VERIFYING",
        "EPS POWER COUPLING // SYNCHRONIZING",
        "ODN SUBSURFACE CARRIER // INITIALIZING",
        "LCARS 47-ALPHA CORE // HANDSHAKE READY",
        "TACTICAL INTERFACE MATRIX // STANDBY",
    ]
    BootScreen.Add(TelemetryStream)
    BootScreen.AddStretch(1)

    # =========================================================================
    # ЕКРАН 2: ПОВНИЙ КАТАЛОГ УСІХ ФОРМ, СТАНІВ І ДИРЕКТИВ LCARS
    # =========================================================================
    CatalogScreen = Panel()
    CatalogScreen.SetHorizontal(0, 0, 0, 0, Spacing=14)

    # ─── КОЛОНКА 1: КАНОНІЧНІ ФОРМИ КНОПОК ───
    Col1 = Panel()
    Col1.SetVertical(0, 0, 0, 0, Spacing=6)

    LblForms = LCARSLabel(Text="CANONICAL BUTTON FORMS", Height=24)
    Col1.Add(LblForms)

    ReadoutCard = Panel()
    ReadoutCard.SetVertical(8, 8, 8, 8, Spacing=4)
    ReadoutTitle = LCARSLabel(Text="ACTIVE SELECTION", Height=20)
    ReadoutVal = LCARSLabel(Text="NO SELECTION // READY", Height=24)
    ReadoutCard.Add(ReadoutTitle)
    ReadoutCard.Add(ReadoutVal)

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

    def SelectForm(Name, Code):
        ReadoutVal.SetText(f"{Name} [{Code}]")

    for Text, Num, FormVal, DirVal in FormData:
        B = LCARSButton(
            Text=Text,
            Number=Num,
            SwapMode=True,
            Form=FormVal,
            Direction=DirVal,
            Width=230,
            Height=38,
            Sound="click"
        )
        B.Clicked.Connect(lambda N=Text, C=Num: SelectForm(N, C))
        FormButtons.append(B)
        Col1.Add(B)

    Col1.AddStretch(1)
    CatalogScreen.Add(Col1)

    # ─── КОЛОНКА 2: ОПЕРАЦІЙНІ СТАНИ ТА ІНДИКАТОРИ ───
    Col2 = Panel()
    Col2.SetVertical(0, 0, 0, 0, Spacing=6)

    LblStates = LCARSLabel(Text="OPERATIONAL STATES", Height=24)
    Col2.Add(LblStates)

    StateButtons = []
    StateDefs = [
        ("NORMAL MATRIX",  "10-NRM", "normal",   True),
        ("STANDBY OFF",    "11-OFF", "disabled", False),
        ("WARNING YELLOW", "12-WRN", "yellow",   True),
        ("CRITICAL ALERT", "13-ALT", "alert",    True),
    ]

    for Text, Num, StateVal, SensoryVal in StateDefs:
        BState = LCARSButton(
            Text=Text,
            Number=Num,
            SwapMode=True,
            Form=LCARSButton.Pill,
            State=StateVal,
            Sensory=SensoryVal,
            Width=230,
            Height=38,
            Sound="click"
        )
        BState.Clicked.Connect(lambda N=Text, S=StateVal: SelectForm(N, S.upper()))
        StateButtons.append(BState)
        Col2.Add(BState)

    BSplit = LCARSButton(
        Text="SPLIT SYS",
        Number="47-SPL",
        SplitMode=True,
        Form=LCARSButton.RectType,
        Width=230,
        Height=38,
        Sound="click"
    )
    BSplit.Clicked.Connect(lambda: SelectForm("SPLIT MODE ENGAGED", "47-SPL"))
    Col2.Add(BSplit)

    BDark = LCARSButton(
        Text="DARK CYCLE",
        Form=LCARSButton.PillHalf,
        Direction=0,
        Number="SEC-01",
        DarkCycle=True,
        IsWakeupTrigger=True,
        Width=230,
        Height=38,
        Sound="click"
    )
    BDark.Clicked.Connect(lambda: SelectForm("DARK CYCLE ACTIVE", "SEC-01"))
    Col2.Add(BDark)

    LblInd = LCARSLabel(Text="OPTICAL INDICATORS", Height=24)
    Col2.Add(LblInd)

    IndRow = Panel()
    IndRow.SetHorizontal(0, 0, 0, 0, Spacing=6)
    Ind1 = LCARSIndicator(Form=LCARSIndicator.RectType, Width=72, Height=32)
    Ind2 = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=72, Height=32)
    Ind3 = LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=72, Height=32)
    IndRow.Add(Ind1)
    IndRow.Add(Ind2)
    IndRow.Add(Ind3)
    Col2.Add(IndRow)

    Col2.AddStretch(1)
    CatalogScreen.Add(Col2)

    # ─── КОЛОНКА 3: ТАКТИЧНІ ДИРЕКТИВИ ТА КЕРУВАННЯ ───
    Col3 = Panel()
    Col3.SetVertical(0, 0, 0, 0, Spacing=6)

    LblAlert = LCARSLabel(Text="TACTICAL DIRECTIVES", Height=24)
    Col3.Add(LblAlert)

    # Червона та жовта тривоги передаються одразу в стані alert і yellow зі своїми динамічними циклами
    BRed = LCARSButton(
        Text="RED ALERT",
        Number="01-RED",
        SwapMode=True,
        Form=LCARSButton.Pill,
        State="alert",
        Sound="alertred",
        Width=230,
        Height=40
    )
    def TriggerRed():
        SystemTheme.SetSystemState("Red")
        SelectForm("RED ALERT CONDITION ENGAGED", "TACTICAL")
    BRed.Clicked.Connect(TriggerRed)
    Col3.Add(BRed)

    BYellow = LCARSButton(
        Text="YELLOW ALERT",
        Number="02-YEL",
        SwapMode=True,
        Form=LCARSButton.PillHalf,
        Direction=180,
        State="yellow",
        Sound="alertyellow",
        Width=230,
        Height=40
    )
    def TriggerYellow():
        SystemTheme.SetSystemState("Yellow")
        SelectForm("YELLOW ALERT CONDITION ENGAGED", "CAUTION")
    BYellow.Clicked.Connect(TriggerYellow)
    Col3.Add(BYellow)

    BGreen = LCARSButton(
        Text="CONDITION GREEN",
        Number="03-GRN",
        SwapMode=True,
        Form=LCARSButton.Pill,
        State="normal",
        Sound="ack",
        Width=230,
        Height=40
    )
    def TriggerGreen():
        SystemTheme.SetSystemState("Normal")
        SelectForm("CONDITION GREEN // SYSTEMS NOMINAL", "ALL-CLEAR")
    BGreen.Clicked.Connect(TriggerGreen)
    Col3.Add(BGreen)

    BPower = LCARSButton(
        Text="GRID POWER",
        Number="04-PWR",
        SwapMode=True,
        Form=LCARSButton.Pill,
        Sound="ack",
        IsWakeupTrigger=True,
        Width=230,
        Height=38
    )
    def TogglePower():
        if PowerControl.State == 0:
            PowerControl.PowerOn()
            SelectForm("GRID POWER RESTORED", "EPS-100")
        else:
            PowerControl.PowerOff()
            SelectForm("GRID POWER OFFLINE", "EPS-000")
    BPower.Clicked.Connect(TogglePower)
    Col3.Add(BPower)

    BLock = LCARSButton(
        Text="STASIS LOCK",
        Number="05-LCK",
        SwapMode=True,
        Form=LCARSButton.PillHalf,
        Direction=0,
        Sound="ack",
        IsWakeupTrigger=True,
        DarkCycle=True,
        Width=230,
        Height=38
    )
    def ToggleLock():
        if PowerControl.Locked:
            PowerControl.Unlock()
            SelectForm("STASIS LOCK RELEASED", "UNLOCKED")
        else:
            PowerControl.Lock()
            SelectForm("STASIS LOCK ENGAGED", "LOCKED")
    BLock.Clicked.Connect(ToggleLock)
    Col3.Add(BLock)

    BElbow = LCARSElbow(Corner="top-left", Text="NAV DECK", Number="01-NAV", Width=230, Height=60, Thickness=24, Radius=20)
    Col3.Add(BElbow)

    Col3.Add(ReadoutCard)
    Col3.AddStretch(1)
    CatalogScreen.Add(Col3)

    # Додаємо екрани до робочої області
    WorkArea.Add(CatalogScreen, 1)
    WorkArea.Add(BootScreen, 1)

    BootSurface = BootScreen.GetSurface()
    CatalogSurface = CatalogScreen.GetSurface()

    # За замовчуванням активний екран каталогу
    if hasattr(BootSurface, "hide"):
        BootSurface.hide()
    if hasattr(CatalogSurface, "show"):
        CatalogSurface.show()

    MainScreen.Add(WorkArea, 1)

    # 3. ПІДВАЛ ЕКРАНА З РЕЖИМАМИ ТА ТЕЛЕМЕТРІЄЮ
    BottomBar = Panel()
    BottomBar.SetHorizontal(0, 0, 0, 0, Spacing=8)

    FootLabel = LCARSLabel(Text="LCARS FULLSCREEN MATRIX ACTIVE // ISOLINEAR OPTICAL BUS NOMINAL", Height=32)
    BottomBar.Add(FootLabel, 1)

    BtnShowStandby = LCARSButton(Text="STANDBY MODE", Form=LCARSButton.PillHalf, Direction=180, Width=180, Height=34, Sound="click")
    BtnShowCatalog = LCARSButton(Text="FULL CATALOG", Form=LCARSButton.PillHalf, Direction=0, Width=180, Height=34, Sound="click")

    BottomBar.Add(BtnShowStandby)
    BottomBar.Add(BtnShowCatalog)

    MainScreen.Add(BottomBar)

    # 4. АНІМАЦІЙНИЙ КОНВЕЄР
    Decoder = TextDecode()
    Writer = Typewriter()
    Cascade = Stagger()

    def OpenCatalog():
        if hasattr(BootSurface, "hide"):
            BootSurface.hide()
        if hasattr(CatalogSurface, "show"):
            CatalogSurface.show()

        for Btn in FormButtons:
            Revealer = Reveal()
            Revealer.StartReveal(Target=Btn, Period=0.35, Direction="Left")
            Cascade.Add(Revealer)

        Cascade.Play(DelayMs=40)

    def OpenStandby():
        if hasattr(CatalogSurface, "hide"):
            CatalogSurface.hide()
        if hasattr(BootScreen.GetSurface(), "show"):
            BootScreen.GetSurface().show()
        StartButton.Tactile = True
        StartButton.Refresh()

    BtnShowStandby.Clicked.Connect(OpenStandby)
    BtnShowCatalog.Clicked.Connect(OpenCatalog)

    def ExitTerminal():
        HostSurface = MainScreen.GetSurface()
        if hasattr(HostSurface, "close"):
            HostSurface.close()

    BtnExit.Clicked.Connect(ExitTerminal)

    def PrintReadyPrompt():
        Writer.Write(
            Target=PromptLabel,
            Text="SYSTEM READY // ENGAGING LCARS INTERFACE MATRIX...",
            Period=1.0,
            OnFinish=OpenCatalog
        )

    def StartInitialization():
        StartButton.Tactile = False
        StartButton.Refresh()
        TelemetryStream.Start(Speed=0.03)

        Decoder.Decode(
            Target=StatusLabel,
            Text="AUTHORIZATION ACCEPTED // DECRYPTING ODN NODES",
            Period=1.0,
            OnFinish=PrintReadyPrompt
        )

    StartButton.Clicked.Connect(StartInitialization)

    MainScreen.Show()
    return MainScreen

LCARS.Launch(ButtonsInterface)