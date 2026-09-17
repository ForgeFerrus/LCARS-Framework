# ◤ LCARS BUTTONS DEMO 🖖
# Один екземпляр кожного виду/типу кнопки, виводиться прямо на скло PADD.
# СТАНДАРТ: Titanium (Pure LCARS Surface Rendering).
from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel
from lcars.base.component import LCARSButton, LCARSElbow
from lcars.base.default import SystemTheme, Palette
from lcars.system.power import PowerControl


def ButtonsInterface():
    Padd = PADD(Title="LCARS BUTTON CATALOG", Width=1100, Height=720)

    # Головна горизонтальна панель скла
    Row = Panel(Spectrum=Palette.Background)
    Row.SetHorizontal(16, 16, 16, 16, Spacing=12)

    # ── Колонка 1: Всі форми ─────────────────────────────────────────
    Col1 = Panel(Spectrum=Palette.Background)
    Col1.SetVertical(0, 0, 0, 0, Spacing=8)

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
        Col1.Add(B)

    Col1.AddStretch()
    Row.Add(Col1)

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
    Row.Add(Col2)

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
    Row.Add(Col3)

    # Виводимо панель на скло планшета PADD
    Padd.Add(Row, 1)
    Padd.Show()

    return Padd


# Запуск через канонічне ядро LCARS:
LCARS.Launch(ButtonsInterface)