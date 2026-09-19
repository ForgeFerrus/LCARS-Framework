# ◤ LCARS COMPONENT LIBRARY — PADD
# Демонстрація компонентів фреймворку на маленькому PADD

from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel
from lcars.base.component import (
    LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
)
from lcars.base.animation import TextDecode, Reveal, Stagger, Blink
from lcars.modules.sound import ActiveAudio

def ComponentShowcase():
    Padd = PADD(Title="LCARS COMPONENT LIBRARY", Width=320, Height=480)
    Padd.SetVertical(6, 6, 6, 6, Spacing=4)

    Padd.Add(LCARSElbow(Corner="top-left", Text="LCARS", Number="COMP-LIB",
                        Width=180, Height=44, Thickness=18, Radius=14))

    AllBtns = []

    Padd.Add(LCARSLabel(Text="BUTTON FORMS", FontSize=10))
    for Txt, Num, Fm, Dr in [
        ("RECT",    "01", LCARSButton.RectType,     0),
        ("PILL",    "02", LCARSButton.PillType,     0),
        ("SOFT",    "03", LCARSButton.SoftType,     0),
        ("HALF-E",  "04", LCARSButton.PillHalfType, 0),
        ("HALF-W",  "05", LCARSButton.PillHalfType, 180),
    ]:
        B = LCARSButton(Text=Txt, Number=Num, SwapMode=True, Form=Fm, Direction=Dr,
                        Width=280, Height=32, Sound="click")
        AllBtns.append(B)
        Padd.Add(B)

    Padd.Add(LCARSBar(Height=2))
    Padd.Add(LCARSLabel(Text="STATES", FontSize=10))

    for Txt, St in [("NORMAL", LCARSButton.NORMAL), ("DISABLED", LCARSButton.DISABLED),
                     ("YELLOW", LCARSButton.YELLOW), ("ALERT", LCARSButton.ALERT)]:
        B = LCARSButton(Text=Txt, State=St, Width=280, Height=32, Sound="click")
        AllBtns.append(B)
        Padd.Add(B)

    Padd.Add(LCARSBar(Height=2))
    Padd.Add(LCARSLabel(Text="INDICATORS", FontSize=10))

    IndRow = Panel()
    IndRow.SetHorizontal(0, 0, 0, 0, Spacing=4)
    IndRow.Add(LCARSIndicator(Form=LCARSIndicator.RectType, Width=88, Height=22))
    IndRow.Add(LCARSIndicator(Form=LCARSIndicator.SoftType, Width=88, Height=22))
    IndRow.Add(LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=88, Height=22))
    Padd.Add(IndRow)

    Padd.Add(LCARSBar(Height=2))
    Padd.Add(LCARSLabel(Text="BARS", FontSize=10))
    Padd.Add(LCARSBar(Form=LCARSBar.RectType, Width=280, Height=10))
    Padd.Add(LCARSBar(Form=LCARSBar.PillHalfType, Width=280, Height=10))
    Padd.Add(LCARSBar(Form=LCARSBar.SoftType, Width=280, Height=10))

    Padd.Add(LCARSBar(Height=2))

    ScanBar = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=280, Height=6)
    Padd.Add(ScanBar)
    Blink(Target=ScanBar, Period=0.7, Loop=True).Start()

    Padd.Add(LCARSElbow(Corner="bottom-right", Text="DECK-47", Number="47-LC",
                        Width=180, Height=40, Thickness=16, Radius=14))

    Padd.Show()

    Cascade = Stagger()
    for B in AllBtns:
        R = Reveal(); R.StartReveal(Target=B, Period=0.2, Direction="Left"); Cascade.Add(R)
    Cascade.Play(DelayMs=25)
    return Padd

LCARS.Launch(ComponentShowcase)
