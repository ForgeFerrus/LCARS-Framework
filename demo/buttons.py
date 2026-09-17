# ◤ LCARS BUTTONS DEMO 🖖
# Один екземпляр кожного виду/типу кнопки, передається прямо в PADD.
# СТАНДАРТ: Titanium (Zero-Imports, Single LCARS Entry, Native Launch).
from lcars.base.type import LCARS

def ButtonsInterface():
    # Отримання системних сутностей через єдине ядро LCARS
    PADD = LCARS.Retrieve("Base.Interface.PADD")
    Button = LCARS.Retrieve("Base.Component.Button")
    Elbow = LCARS.Retrieve("Base.Component.Elbow")
    Theme = LCARS.Retrieve("Base.Default.SystemTheme")
    Power = LCARS.Retrieve("System.Power.Control")

    Horizontal = LCARS.Retrieve(LCARS.Horizontal)
    Vertical = LCARS.Retrieve(LCARS.Vertical)
    Widget = LCARS.Retrieve(LCARS.Display)
    Timer = LCARS.Retrieve("Base.Interface.Timer")

    Padd = PADD(Title="LCARS BUTTON CATALOG", Width=1100, Height=720)
    Row = Horizontal()
    Row.setContentsMargins(16, 16, 16, 16)
    Row.setSpacing(12)

    # ── Колонка 1: Всі форми ─────────────────────────────────────────
    Col1 = Vertical()
    Col1.setSpacing(8)

    for Text, Form, Direction in [
        ("RECT",          Button.Rect,     0),
        ("PILL",          Button.Pill,     0),
        ("SOFT",          Button.Soft,     0),
        ("PILLHALF →",    Button.PillHalf, 0),
        ("PILLHALF ←",    Button.PillHalf, 180),
        ("PILLHALF ↓",    Button.PillHalf, 90),
        ("PILLHALF ↑",    Button.PillHalf, 270),
        ("SOFTHALF →",    Button.SoftHalf, 0),
        ("SOFTHALF ←",    Button.SoftHalf, 180),
    ]:
        B = Button(Text=Text, Form=Form, Direction=Direction, Width=200, Height=40, FontSize=14)
        Col1.addWidget(B.widget)

    Col1.addStretch()
    Row.addLayout(Col1)

    # ── Колонка 2: Стани ─────────────────────────────────────────────
    Col2 = Vertical()
    Col2.setSpacing(8)

    for Text, State, Sensory in [
        ("NORMAL",    "normal",   True),
        ("DISABLED",  "disabled", False),
        ("ALERT RED", "alert",    True),
        ("YELLOW",    "yellow",   True),
    ]:
        B = Button(Text=Text, Form=Button.Pill, State=State, Sensory=Sensory, Width=200, Height=40, FontSize=14)
        Col2.addWidget(B.widget)

    BSplit = Button(Text="SPLIT MODE", Form=Button.Rect, Number="47-001", SplitMode=True, Width=200, Height=40, FontSize=14)
    Col2.addWidget(BSplit.widget)

    BDark = Button(Text="DARK CYCLE", Form=Button.PillHalf, Direction=0, Number="SEC-01", DarkCycle=True, IsWakeupTrigger=True, Width=200, Height=40, FontSize=14)
    Col2.addWidget(BDark.widget)

    Col2.addStretch()
    Row.addLayout(Col2)

    # ── Колонка 3: Дії (Alert + Power) ───────────────────────────────
    Col3 = Vertical()
    Col3.setSpacing(8)

    BAlert = Button(Text="RED ALERT", Form=Button.Pill, State="alert", Sound="alert_red", Width=200, Height=40, FontSize=14)
    if Theme and hasattr(Theme, "SetSystemState"):
        BAlert.Clicked.Connect(lambda: Theme.SetSystemState("Red"))
    Col3.addWidget(BAlert.widget)

    BYellow = Button(Text="YELLOW ALERT", Form=Button.PillHalf, Direction=180, State="yellow", Sound="alert_yellow", Width=200, Height=40, FontSize=14)
    if Theme and hasattr(Theme, "SetSystemState"):
        BYellow.Clicked.Connect(lambda: Theme.SetSystemState("Yellow"))
    Col3.addWidget(BYellow.widget)

    BNormal = Button(Text="CONDITION GREEN", Form=Button.Pill, State="normal", Sound="acknowledge", Width=200, Height=40, FontSize=14)
    if Theme and hasattr(Theme, "SetSystemState"):
        BNormal.Clicked.Connect(lambda: Theme.SetSystemState("Normal"))
    Col3.addWidget(BNormal.widget)

    BPower = Button(Text="GRID POWER", Form=Button.Pill, Sound="acknowledge", IsWakeupTrigger=True, Width=200, Height=40, FontSize=14)
    if Power:
        BPower.Clicked.Connect(lambda: Power.PowerOff() if Power.State != 0 else Power.PowerOn())
    Col3.addWidget(BPower.widget)

    BLock = Button(Text="STASIS LOCK", Form=Button.PillHalf, Direction=0, Sound="alert_yellow", IsWakeupTrigger=True, DarkCycle=True, Width=200, Height=40, FontSize=14)
    if Power:
        BLock.Clicked.Connect(lambda: Power.Unlock() if Power.Locked else Power.Lock())
    Col3.addWidget(BLock.widget)

    BElbow = Elbow(Direction="top-left", Text="NAV DECK", Number="01-NAV", Width=200, Height=64, Thickness=24, Radius=20)
    Col3.addWidget(BElbow.widget)

    Col3.addStretch()
    Row.addLayout(Col3)

    # Монтуємо у PADD
    Container = Widget()
    Container.setLayout(Row)
    Padd.Add(Container)
    Padd.show()

    return Padd

    def Launch(EntryPoint, *args, **kwargs):
    AppClass = LCARS.Retrieve("Base.Interface.Application")
    App = AppClass.instance() if AppClass and hasattr(AppClass, "instance") else None
    if App is None and AppClass:
        SysModule = __import__("sys")
        App = AppClass(getattr(SysModule, "argv", []))

    Result = EntryPoint(*args, **kwargs) if callable(EntryPoint) else EntryPoint

    if App and hasattr(App, "exec"):
        return App.exec()
    return Result

# Власний фірмовий системний запуск програми зорельота:
LCARS.Launch(ButtonsInterface)