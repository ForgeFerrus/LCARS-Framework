# ◤ LCARS BUTTONS & PADD INITIALIZATION DEMO 🖖
# СТАНДАРТ: Titanium (Pure LCARS Surface Rendering).
# Сценарій:
# 1. PADD запускається у стані очікування (STANDBY) із кнопкою ініціалізації.
# 2. Натискання кнопки активує квантове декодування (TextDecode) та потік телеметрії (DataStream).
# 3. Термінальний посимвольний друк (Typewriter) підтверджує готовність матриці.
# 4. Каскадне розгортання (Stagger + Reveal) переводить PADD у повний каталог кнопок LCARS.
from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel, Header, Footer
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator
from lcars.base.animation import TextDecode, Typewriter, DataStream, Reveal, Stagger
from lcars.base.default import SystemTheme, Palette
from lcars.system.power import PowerControl

def ButtonsInterface():
    Padd = PADD(Title="LCARS INTERFACE & BUTTON CATALOG", Width=1180, Height=760)
    Padd.SetVertical(10, 10, 10, 10, Spacing=8)

    # 1. Верхня та нижня консольні смуги планшета
    TopHeader = Header(Title="LCARS 47 // STARFLEET TACTICAL INTERFACE", Spectrum=Palette.Buttons[2])
    Padd.Add(TopHeader)

    # 2. Центральна робоча область (контейнер для перемикання екранів)
    WorkArea = Panel(Spectrum=Palette.Background)
    WorkArea.SetVertical(0, 0, 0, 0, Spacing=0)

    # =========================================================================
    # ЕКРАН 1: СТАН ОЧІКУВАННЯ ТА ІНІЦІАЛІЗАЦІЯ (BOOT / STANDBY)
    # =========================================================================
    BootScreen = Panel(Spectrum=Palette.Background)
    BootScreen.SetVertical(20, 20, 20, 20, Spacing=16)

    StatusLabel = LCARSLabel(
        Text="STANDBY MODE // PADD OFFLINE",
        FontSize=20,
        Align="center",
        Width=800,
        Height=36,
        Spectrum=Palette.Buttons[1]
    )
    BootScreen.Add(StatusLabel)

    PromptLabel = LCARSLabel(
        Text="PRESS INITIALIZE TO ENGAGE LCARS INTERFACE MATRIX",
        FontSize=16,
        Align="center",
        Width=800,
        Height=26,
        Spectrum=Palette.Disabled[1]
    )
    BootScreen.Add(PromptLabel)

    # Центрована панель для фірмової кнопки запуску
    ButtonRow = Panel(Spectrum=Palette.Background)
    ButtonRow.SetHorizontal(0, 0, 0, 0, Spacing=0)
    ButtonRow.AddStretch(1)

    StartButton = LCARSButton(
        Text="INITIALIZE SYSTEM",
        Form=LCARSButton.Pill,
        Width=360,
        Height=48,
        FontSize=16,
        Sound="acknowledge",
        Spectrum=Palette.Buttons[4]
    )
    ButtonRow.Add(StartButton)
    ButtonRow.AddStretch(1)
    BootScreen.Add(ButtonRow)

    # Потік діагностики та телеметрії ODN
    TelemetryStream = DataStream(
        Width=800,
        Height=180,
        Rows=6,
        FontSize=16,
        Spectrum=Palette.Buttons[2],
        Accent=Palette.Buttons[0]
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
    # ЕКРАН 2: ПОВНИЙ КАТАЛОГ УСІХ ФОРМ, СТАНІВ І ТИПІВ КНОПОК LCARS
    # =========================================================================
    CatalogScreen = Panel(Spectrum=Palette.Background)
    CatalogScreen.SetHorizontal(0, 0, 0, 0, Spacing=12)

    # ─── КОЛОНКА 1: ФОРМИ ОКУДИ (PILL, RECT, SOFT, HALF) ───
    Col1 = Panel(Spectrum=Palette.Background)
    Col1.SetVertical(0, 0, 0, 0, Spacing=6)

    LblForms = LCARSLabel(Text="CANONICAL BUTTON FORMS", FontSize=12, Spectrum=Palette.Buttons[2])
    Col1.Add(LblForms)

    FormButtons = []
    for Text, Num, FormVal, DirVal in [
        ("RECT BUTTON",      "01-RCT", LCARSButton.RectType,     0),
        ("PILL CAPSULE",     "02-PIL", LCARSButton.PillType,     0),
        ("SOFT CHAMFER",     "03-SFT", LCARSButton.SoftType,     0),
        ("PILL-HALF EAST",   "04-PHE", LCARSButton.PillHalfType, 0),
        ("PILL-HALF WEST",   "05-PHW", LCARSButton.PillHalfType, 180),
        ("SOFT-HALF EAST",   "06-SHE", LCARSButton.SoftHalfType, 0),
        ("SOFT-HALF WEST",   "07-SHW", LCARSButton.SoftHalfType, 180),
    ]:
        B = LCARSButton(Text=Text, Number=Num, SwapMode=True, Form=FormVal, Direction=DirVal, Width=210, Height=36, FontSize=16, Spectrum=Palette.Buttons[2])
        FormButtons.append(B)
        Col1.Add(B)

    Col1.AddStretch(1)
    CatalogScreen.Add(Col1)

    # ─── КОЛОНКА 2: СТАНИ, РЕЖИМИ ТА ІНДИКАТОРИ ───
    Col2 = Panel(Spectrum=Palette.Background)
    Col2.SetVertical(0, 0, 0, 0, Spacing=6)

    LblStates = LCARSLabel(Text="OPERATIONAL STATES", FontSize=16, Spectrum=Palette.Buttons[1])
    Col2.Add(LblStates)

    for Text, Num, State, Sensory, Color in [
        ("NORMAL MATRIX",  "10-NRM", "normal",   True,  Palette.Buttons[1]),
        ("STANDBY OFF",    "11-OFF", "disabled", False, Palette.Disabled[0]),
        ("WARNING YELLOW", "12-WRN", "yellow",   True,  Palette.YellowAlert[0]),
        ("CRITICAL ALERT", "13-ALT", "alert",    True,  Palette.RedAlert[0]),
    ]:
        B = LCARSButton(Text=Text, Number=Num, SwapMode=True, Form=LCARSButton.Pill, State=State, Sensory=Sensory, Spectrum=Color, Width=210, Height=36, FontSize=16)
        Col2.Add(B)

    BSplit1 = LCARSButton(Text="SPLIT SYS", Number="47-SPL", SplitMode=True, Form=LCARSButton.RectType, Width=210, Height=36, FontSize=16, Spectrum=Palette.Buttons[0])
    Col2.Add(BSplit1)

    BDark = LCARSButton(Text="DARK CYCLE", Form=LCARSButton.PillHalf, Direction=0, Number="SEC-01", DarkCycle=True, IsWakeupTrigger=True, Width=210, Height=36, FontSize=16, Spectrum=Palette.Buttons[3])
    Col2.Add(BDark)

    LblInd = LCARSLabel(Text="OPTICAL INDICATORS", FontSize=11, Spectrum=Palette.Buttons[0])
    Col2.Add(LblInd)

    IndRow = Panel(Spectrum=Palette.Background)
    IndRow.SetHorizontal(0, 0, 0, 0, Spacing=6)
    Ind1 = LCARSIndicator(Form=LCARSIndicator.RectType, Width=65, Height=32, Spectrum=Palette.Buttons[2])
    Ind2 = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=65, Height=32, Spectrum=Palette.Buttons[0])
    Ind3 = LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=65, Height=32, Spectrum=Palette.Buttons[1])
    IndRow.Add(Ind1)
    IndRow.Add(Ind2)
    IndRow.Add(Ind3)
    Col2.Add(IndRow)

    Col2.AddStretch(1)
    CatalogScreen.Add(Col2)

    # ─── КОЛОНКА 3: ДИРЕКТИВИ ТРИВОГИ, ЖИВЛЕННЯ ТА ЛІКОТЬ ───
    Col3 = Panel(Spectrum=Palette.Background)
    Col3.SetVertical(0, 0, 0, 0, Spacing=6)

    LblAlert = LCARSLabel(Text="TACTICAL DIRECTIVES", FontSize=16, Spectrum=Palette.Buttons[0])
    Col3.Add(LblAlert)

    BRed = LCARSButton(Text="RED ALERT", Number="01-RED", SwapMode=True, Form=LCARSButton.Pill, State="alert", Sound="alert_red", Spectrum=Palette.RedAlert[0], Width=210, Height=38, FontSize=16)
    BRed.Clicked.Connect(lambda: SystemTheme.SetSystemState("Red"))
    Col3.Add(BRed)

    BYellow = LCARSButton(Text="YELLOW ALERT", Number="02-YEL", SwapMode=True, Form=LCARSButton.PillHalf, Direction=180, State="yellow", Sound="alert_yellow", Spectrum=Palette.YellowAlert[0], Width=210, Height=38, FontSize=16)
    BYellow.Clicked.Connect(lambda: SystemTheme.SetSystemState("Yellow"))
    Col3.Add(BYellow)

    BGreen = LCARSButton(Text="CONDITION GREEN", Number="03-GRN", SwapMode=True, Form=LCARSButton.Pill, State="normal", Sound="acknowledge", Spectrum=Palette.Buttons[0], Width=210, Height=38, FontSize=16)
    BGreen.Clicked.Connect(lambda: SystemTheme.SetSystemState("Normal"))
    Col3.Add(BGreen)

    BPower = LCARSButton(Text="GRID POWER", Number="04-PWR", SwapMode=True, Form=LCARSButton.Pill, Sound="acknowledge", IsWakeupTrigger=True, Spectrum=Palette.Buttons[3], Width=210, Height=36, FontSize=16)
    BPower.Clicked.Connect(lambda: PowerControl.PowerOff() if PowerControl.State != 0 else PowerControl.PowerOn())
    Col3.Add(BPower)

    BLock = LCARSButton(Text="STASIS LOCK", Number="05-LCK", SwapMode=True, Form=LCARSButton.PillHalf, Direction=0, Sound="alert_yellow", IsWakeupTrigger=True, DarkCycle=True, Spectrum=Palette.Buttons[5], Width=210, Height=36, FontSize=16)
    BLock.Clicked.Connect(lambda: PowerControl.Unlock() if PowerControl.Locked else PowerControl.Lock())
    Col3.Add(BLock)

    BElbow = LCARSElbow(Corner="top-left", Text="NAV DECK", Number="01-NAV", Width=210, Height=60, Thickness=24, Radius=20, Spectrum=Palette.Buttons[1])
    Col3.Add(BElbow)

    Col3.AddStretch(1)
    CatalogScreen.Add(Col3)

    # Додаємо екрани до робочої області (за замовчуванням показуємо Каталог для повної готовності)
    WorkArea.Add(CatalogScreen, 1)
    WorkArea.Add(BootScreen, 1)

    BootSurface = BootScreen.GetSurface()
    CatalogSurface = CatalogScreen.GetSurface()

    # Початковий стан: Каталог активний одразу для миттєвої перевірки всіх кнопок
    if hasattr(BootSurface, "hide"):
        BootSurface.hide()
    if hasattr(CatalogSurface, "show"):
        CatalogSurface.show()

    Padd.Add(WorkArea, 1)

    # 3. Підвал планшета із швидкими перемикачами режиму
    BottomFoot = Footer(Spectrum=Palette.Buttons[0])
    BottomFoot.SetHorizontal(0, 0, 0, 0, Spacing=8)

    FootLabel = LCARSLabel(Text="PADD v4.7 // ISOLINEAR OPTICAL INTERFACE ACTIVE", FontSize=12, Spectrum=Palette.Buttons[0])
    BottomFoot.Add(FootLabel, 1)

    BtnShowStandby = LCARSButton(Text="STANDBY MODE", Form=LCARSButton.PillHalf, Direction=180, Width=160, Height=28, FontSize=16, Spectrum=Palette.Buttons[3])
    BtnShowCatalog = LCARSButton(Text="FULL CATALOG", Form=LCARSButton.PillHalf, Direction=0, Width=160, Height=28, FontSize=16, Spectrum=Palette.Buttons[2])

    BottomFoot.Add(BtnShowStandby)
    BottomFoot.Add(BtnShowCatalog)

    Padd.Add(BottomFoot)

    # =========================================================================
    # АНІМАЦІЙНИЙ КОНВЕЄР ІНІЦІАЛІЗАЦІЇ ТА ПЕРЕХОДУ
    # =========================================================================
    Decoder = TextDecode()
    Writer = Typewriter()
    Cascade = Stagger()

    def OpenCatalog():
        if hasattr(BootSurface, "hide"):
            BootSurface.hide()
        if hasattr(CatalogSurface, "show"):
            CatalogSurface.show()

        # Каскадне розгортання кнопок каталогу (Stagger + Reveal)
        for Btn in FormButtons:
            Revealer = Reveal()
            Revealer.StartReveal(Target=Btn, Period=0.35, Direction="Left")
            Cascade.Add(Revealer)

        Cascade.Play(DelayMs=45)

    def OpenStandby():
        if hasattr(CatalogSurface, "hide"):
            CatalogSurface.hide()
        if hasattr(BootSurface, "show"):
            BootSurface.show()
        StartButton.Tactile = True
        StartButton.Refresh()

    BtnShowStandby.Clicked.Connect(OpenStandby)
    BtnShowCatalog.Clicked.Connect(OpenCatalog)

    def PrintReadyPrompt():
        Writer.Write(
            Target=PromptLabel,
            Text="SYSTEM READY // ENGAGING LCARS INTERFACE MATRIX...",
            Period=1.1,
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

    Padd.Show()
    return Padd

# Запуск через канонічне ядро LCARS:
LCARS.Launch(ButtonsInterface)