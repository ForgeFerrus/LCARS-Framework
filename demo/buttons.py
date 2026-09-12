# ◤ LCARS BUTTONS DEMO 🖖
# Один екземпляр кожного виду/типу кнопки, передається прямо в PADD.

from __future__ import annotations

from lcars.base.type import LCARS
from lcars.base.interface import PADD
from lcars.base.component import LCARSButton, LCARSElbow
from lcars.base.default import SystemTheme
from lcars.system.power import PowerControl


def Run():
    App = LCARS.Application.instance() or LCARS.Application([])

    Padd = PADD(Title="LCARS BUTTON CATALOG", Width=1100, Height=720)

    Row = LCARS.Horizontal()
    Row.setContentsMargins(16, 16, 16, 16)
    Row.setSpacing(12)

    # ── Колонка 1: Всі форми ─────────────────────────────────────────
    Col1 = LCARS.Vertical()
    Col1.setSpacing(8)

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
        B = LCARSButton(Text=Text, Form=Form, Direction=Direction,
                        Width=200, Height=40, FontSize=14)
        Col1.addWidget(B.widget)

    Col1.addStretch()
    Row.addLayout(Col1)

    # ── Колонка 2: Стани ─────────────────────────────────────────────
    Col2 = LCARS.Vertical()
    Col2.setSpacing(8)

    for Text, State, Sensory in [
        ("NORMAL",    "normal",   True),
        ("DISABLED",  "disabled", False),
        ("ALERT RED", "alert",    True),
        ("YELLOW",    "yellow",   True),
    ]:
        B = LCARSButton(Text=Text, Form=LCARSButton.Pill,
                        State=State, Sensory=Sensory,
                        Width=200, Height=40, FontSize=14)
        Col2.addWidget(B.widget)

    BSplit = LCARSButton(Text="SPLIT MODE", Form=LCARSButton.Rect,
                         Number="47-001", SplitMode=True,
                         Width=200, Height=40, FontSize=14)
    Col2.addWidget(BSplit.widget)

    BDark = LCARSButton(Text="DARK CYCLE", Form=LCARSButton.PillHalf,
                        Direction=0, Number="SEC-01",
                        DarkCycle=True, IsWakeupTrigger=True,
                        Width=200, Height=40, FontSize=14)
    Col2.addWidget(BDark.widget)

    Col2.addStretch()
    Row.addLayout(Col2)

    # ── Колонка 3: Дії (Alert + Power) ───────────────────────────────
    Col3 = LCARS.Vertical()
    Col3.setSpacing(8)

    BAlert = LCARSButton(Text="RED ALERT", Form=LCARSButton.Pill,
                         State="alert", Sound="alert_red",
                         Width=200, Height=40, FontSize=14)
    BAlert.Clicked.Connect(lambda: SystemTheme.SetSystemState("Red"))
    Col3.addWidget(BAlert.widget)

    BYellow = LCARSButton(Text="YELLOW ALERT", Form=LCARSButton.PillHalf,
                          Direction=180, State="yellow", Sound="alert_yellow",
                          Width=200, Height=40, FontSize=14)
    BYellow.Clicked.Connect(lambda: SystemTheme.SetSystemState("Yellow"))
    Col3.addWidget(BYellow.widget)

    BNormal = LCARSButton(Text="CONDITION GREEN", Form=LCARSButton.Pill,
                          State="normal", Sound="acknowledge",
                          Width=200, Height=40, FontSize=14)
    BNormal.Clicked.Connect(lambda: SystemTheme.SetSystemState("Normal"))
    Col3.addWidget(BNormal.widget)

    BPower = LCARSButton(Text="GRID POWER", Form=LCARSButton.Pill,
                         Sound="acknowledge", IsWakeupTrigger=True,
                         Width=200, Height=40, FontSize=14)
    BPower.Clicked.Connect(
        lambda: PowerControl.PowerOff() if PowerControl.State != 0 else PowerControl.PowerOn()
    )
    Col3.addWidget(BPower.widget)

    BLock = LCARSButton(Text="STASIS LOCK", Form=LCARSButton.PillHalf,
                        Direction=0, Sound="alert_yellow",
                        IsWakeupTrigger=True, DarkCycle=True,
                        Width=200, Height=40, FontSize=14)
    BLock.Clicked.Connect(
        lambda: PowerControl.Unlock() if PowerControl.Locked else PowerControl.Lock()
    )
    Col3.addWidget(BLock.widget)

    # LCARSElbow
    BElbow = LCARSElbow(Direction="top-left", Text="NAV DECK",
                        Number="01-NAV", Width=200, Height=64,
                        Thickness=24, Radius=20)
    Col3.addWidget(BElbow.widget)

    Col3.addStretch()
    Row.addLayout(Col3)

    # Монтуємо
    Container = LCARS.Widget()
    Container.setLayout(Row)
    Padd.Add(Container)
    Padd.show()

    # Цикл перемалювання для DynamicColor
    Timer = LCARS.Timer()
    Timer.setInterval(1800)
    Timer.timeout.connect(Padd.Widget.update)
    Timer.start()

    return App.exec()


if __name__ == "__main__":
    Run()
