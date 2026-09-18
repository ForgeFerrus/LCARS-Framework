# ◤ LCARS BUTTONS & PADD INITIALIZATION DEMO 🖖
# СТАНДАРТ: Titanium (Pure LCARS Surface Rendering).
# Сценарій:
# 1. PADD запускається у стані очікування (STANDBY) із кнопкою ініціалізації.
# 2. Натискання кнопки активує квантове декодування (TextDecode) та потік телеметрії (DataStream).
# 3. Термінальний посимвольний друк (Typewriter) підтверджує готовність матриці.
# 4. Каскадне розгортання (Stagger + Reveal) розгортає повний каталог кнопок LCARS.
from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel
from lcars.base.animation import TextDecode, Typewriter, DataStream, Reveal, Stagger
from lcars.base.default import SystemTheme, Palette
from lcars.system.power import PowerControl
# =========================================================================
# 1. ЕКРАН ОЧІКУВАННЯ ТА ІНІЦІАЛІЗАЦІЇ
# =========================================================================
def ButtonsInterface():
    Padd = PADD(Title="LCARS INTERFACE & BUTTON CATALOG", Width=1100, Height=720)
    BootScreen = Panel(Spectrum=Palette.Background)
    BootScreen.SetVertical(24, 24, 24, 24, Spacing=14)
    BootScreen.AddStretch(1)
    # Статусний заголовок
    StatusLabel = LCARSLabel(
        Text="STANDBY MODE // PADD OFFLINE",
        FontSize=18,
        Align="center",
        Width=600,
        Height=36,
        Spectrum=Palette.Buttons[1]
    )
    BootScreen.Add(StatusLabel)
    # Підказка для офіцера
    PromptLabel = LCARSLabel(
        Text="PRESS INITIALIZE TO ENGAGE LCARS INTERFACE",
        FontSize=12,
        Align="center",
        Width=600,
        Height=24,
        Spectrum=Palette.Disabled[1]
    )
    BootScreen.Add(PromptLabel)
    # Кнопка запуску ініціалізації
    StartButton = LCARSButton(
        Text="INITIALIZE SYSTEM",
        Form=LCARSButton.Pill,
        Width=280,
        Height=46,
        FontSize=15,
        Sound="acknowledge"
    )
    BootScreen.Add(StartButton)
    # Потік діагностики та телеметрії ODN
    TelemetryStream = DataStream(
        Width=600,
        Height=110,
        Rows=5,
        FontSize=11,
        Spectrum=Palette.Buttons[2],
        Accent=Palette.Buttons[0]
    )
    TelemetryStream.Lines = [
        "ISOLINEAR OPTICAL BUS // VERIFYING",
        "EPS POWER COUPLING // SYNCHRONIZING",
        "ODN SUBSURFACE CARRIER // INITIALIZING",
        "LCARS 47-ALPHA CORE // HANDSHAKE READY",
    ]
    BootScreen.Add(TelemetryStream)
    BootScreen.AddStretch(1)
    # =========================================================================
    # 2. ГОЛОВНА РОБОЧА ПАНЕЛЬ КАТАЛОГУ КНОПОК
    # =========================================================================
    CatalogRow = Panel(Spectrum=Palette.Background)
    CatalogRow.SetHorizontal(16, 16, 16, 16, Spacing=12)

    # ── Колонка 1: Всі форми ─────────────────────────────────────────
    Col1 = Panel(Spectrum=Palette.Background)
    Col1.SetVertical(0, 0, 0, 0, Spacing=8)

    FormButtons = []
    for Text, Form, Direction in [
        ("RECT",          LCARSButton.Rect,     0),
        ("PILL",          LCARSButton.Pill,     0),
        ("SOFT",          LCARSButton.Soft,     0),
        ("PILLHALF →",    LCARSButton.PillHalf, 0),
        ("PILLHALF ←",    LCARSButton.PillHalf, 180),
        ("PILLHALF ↓",    LCARSButton.PillHalf, 90),
        ("PILLHALF ↑",    LCARSButton.PillHalf, 270),
        ("SOFTHALF →",    LCARSButton.SoftHalf, 0),
        ("SOFTHALF ←",    LCARSButton.SoftHalf, 180),
    ]:
        B = LCARSButton(Text=Text, Form=Form, Direction=Direction, Width=200, Height=40, FontSize=14)
        FormButtons.append(B)
        Col1.Add(B)

    Col1.AddStretch()
    CatalogRow.Add(Col1)

    # ── Колонка 2: Стани ─────────────────────────────────────────────
    Col2 = Panel(Spectrum=Palette.Background)
    Col2.SetVertical(0, 0, 0, 0, Spacing=8)

    for Text, State, Sensory in [
        ("NORMAL",    "normal",   True),
        ("DISABLED",  "disabled", False),
        ("ALERT RED", "alert",    True),
        ("YELLOW",    "yellow",   True),
    ]:
        B = LCARSButton(Text=Text, Form=LCARSButton.Pill, State=State, Sensory=Sensory, Width=200, Height=40, FontSize=14)
        Col2.Add(B)

    BSplit = LCARSButton(Text="SPLIT MODE", Form=LCARSButton.Rect, Number="47-001", SplitMode=True, Width=200, Height=40, FontSize=14)
    Col2.Add(BSplit)

    BDark = LCARSButton(Text="DARK CYCLE", Form=LCARSButton.PillHalf, Direction=0, Number="SEC-01", DarkCycle=True, IsWakeupTrigger=True, Width=200, Height=40, FontSize=14)
    Col2.Add(BDark)

    Col2.AddStretch()
    CatalogRow.Add(Col2)

    # ── Колонка 3: Дії (Alert + Power) ───────────────────────────────
    Col3 = Panel(Spectrum=Palette.Background)
    Col3.SetVertical(0, 0, 0, 0, Spacing=8)

    BAlert = LCARSButton(Text="RED ALERT", Form=LCARSButton.Pill, State="alert", Sound="alert_red", Width=200, Height=40, FontSize=14)
    BAlert.Clicked.Connect(lambda: SystemTheme.SetSystemState("Red"))
    Col3.Add(BAlert)

    BYellow = LCARSButton(Text="YELLOW ALERT", Form=LCARSButton.PillHalf, Direction=180, State="yellow", Sound="alert_yellow", Width=200, Height=40, FontSize=14)
    BYellow.Clicked.Connect(lambda: SystemTheme.SetSystemState("Yellow"))
    Col3.Add(BYellow)

    BNormal = LCARSButton(Text="CONDITION GREEN", Form=LCARSButton.Pill, State="normal", Sound="acknowledge", Width=200, Height=40, FontSize=14)
    BNormal.Clicked.Connect(lambda: SystemTheme.SetSystemState("Normal"))
    Col3.Add(BNormal)

    BPower = LCARSButton(Text="GRID POWER", Form=LCARSButton.Pill, Sound="acknowledge", IsWakeupTrigger=True, Width=200, Height=40, FontSize=14)
    BPower.Clicked.Connect(lambda: PowerControl.PowerOff() if PowerControl.State != 0 else PowerControl.PowerOn())
    Col3.Add(BPower)

    BLock = LCARSButton(Text="STASIS LOCK", Form=LCARSButton.PillHalf, Direction=0, Sound="alert_yellow", IsWakeupTrigger=True, DarkCycle=True, Width=200, Height=40, FontSize=14)
    BLock.Clicked.Connect(lambda: PowerControl.Unlock() if PowerControl.Locked else PowerControl.Lock())
    Col3.Add(BLock)

    BElbow = LCARSElbow(Direction="top-left", Text="NAV DECK", Number="01-NAV", Width=200, Height=64, Thickness=24, Radius=20)
    Col3.Add(BElbow)

    Col3.AddStretch()
    CatalogRow.Add(Col3)

    # Додаємо обидва екрани до PADD (BootScreen активний, CatalogRow приховано)
    Padd.Add(BootScreen, 1)
    Padd.Add(CatalogRow, 1)

    CatalogSurface = CatalogRow.GetSurface()
    if hasattr(CatalogSurface, "hide"):
        CatalogSurface.hide()

    # =========================================================================
    # 3. АНІМАЦІЙНИЙ КОНВЕЄР ІНІЦІАЛІЗАЦІЇ
    # =========================================================================
    Decoder = TextDecode()
    Writer = Typewriter()
    Cascade = Stagger()

    def OpenCatalog():
        BootSurface = BootScreen.GetSurface()
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

        # Фаза 1: квантове набігання/дешифрування
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