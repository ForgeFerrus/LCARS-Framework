# ◤ LCARS COMPONENT LIBRARY — PADD FORM FACTOR
# Демонстрація всіх компонентів фреймворку на PADD

from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel
from lcars.base.component import (
    LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
)
from lcars.base.animation import TextDecode, Reveal, Stagger, Blink
from lcars.modules.sound import ActiveAudio


def ComponentShowcase():
    Padd = PADD(Title="LCARS COMPONENT LIBRARY", Width=480, Height=720)
    Padd.SetVertical(10, 10, 10, 10, Spacing=6)

    # ── HEADER ──────────────────────────────────────────────────────────────
    Padd.Add(LCARSElbow(Corner="top-left", Text="LCARS", Number="COMP-LIB",
                        Width=200, Height=56, Thickness=22, Radius=16))

    # ── BUTTON FORMS ────────────────────────────────────────────────────────
    Padd.Add(LCARSLabel(Text="BUTTON FORMS", FontSize=12))

    AllBtns = []
    for Txt, Num, Fm, Dr in [
        ("RECT",        "01", LCARSButton.RectType,     0),
        ("PILL",        "02", LCARSButton.PillType,     0),
        ("SOFT",        "03", LCARSButton.SoftType,     0),
        ("PILL-HALF E", "04", LCARSButton.PillHalfType, 0),
        ("PILL-HALF W", "05", LCARSButton.PillHalfType, 180),
    ]:
        B = LCARSButton(Text=Txt, Number=Num, SwapMode=True, Form=Fm, Direction=Dr,
                        Width=440, Height=36, Sound="click")
        AllBtns.append(B)
        Padd.Add(B)

    Padd.Add(LCARSBar(Height=3))

    # ── BUTTON STATES ───────────────────────────────────────────────────────
    Padd.Add(LCARSLabel(Text="BUTTON STATES", FontSize=12))

    for Txt, St in [("NORMAL", LCARSButton.NORMAL), ("DISABLED", LCARSButton.DISABLED),
                     ("YELLOW", LCARSButton.YELLOW), ("ALERT", LCARSButton.ALERT)]:
        B = LCARSButton(Text=Txt, State=St, Width=440, Height=36, Sound="click")
        AllBtns.append(B)
        Padd.Add(B)

    Padd.Add(LCARSBar(Height=3))

    # ── INDICATORS ──────────────────────────────────────────────────────────
    Padd.Add(LCARSLabel(Text="INDICATORS", FontSize=12))

    IndRow = Panel()
    IndRow.SetHorizontal(0, 0, 0, 0, Spacing=6)
    IndRow.Add(LCARSIndicator(Form=LCARSIndicator.RectType, Width=140, Height=28))
    IndRow.Add(LCARSIndicator(Form=LCARSIndicator.SoftType, Width=140, Height=28))
    IndRow.Add(LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=140, Height=28))
    Padd.Add(IndRow)

    Padd.Add(LCARSBar(Height=3))

    # ── BARS ────────────────────────────────────────────────────────────────
    Padd.Add(LCARSLabel(Text="BARS", FontSize=12))
    Padd.Add(LCARSBar(Form=LCARSBar.RectType, Width=440, Height=14))
    Padd.Add(LCARSBar(Form=LCARSBar.PillHalfType, Width=440, Height=14))
    Padd.Add(LCARSBar(Form=LCARSBar.SoftType, Width=440, Height=14))

    Padd.Add(LCARSBar(Height=3))

    # ── ELBOWS ──────────────────────────────────────────────────────────────
    Padd.Add(LCARSLabel(Text="ELBOWS", FontSize=12))

    ElbowRow = Panel()
    ElbowRow.SetHorizontal(0, 0, 0, 0, Spacing=8)
    for Corner, Txt in [("top-left","TL"), ("top-right","TR"), ("bottom-left","BL"), ("bottom-right","BR")]:
        ElbowRow.Add(LCARSElbow(Corner=Corner, Text=Txt, Width=100, Height=50,
                                Thickness=18, Radius=14))
    ElbowRow.AddStretch()
    Padd.Add(ElbowRow)

    Padd.Add(LCARSBar(Height=3))

    # ── DEMO STATUS ─────────────────────────────────────────────────────────
    DemoStatus = LCARSLabel(Text="COMPONENT LIBRARY", FontSize=16,
                            Align="center", Height=32)
    Padd.Add(DemoStatus)

    ScanBar = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=440, Height=8)
    Padd.Add(ScanBar)
    Blink(Target=ScanBar, Period=0.7, Loop=True).Start()

    # ── FOOTER ──────────────────────────────────────────────────────────────
    Padd.Add(LCARSElbow(Corner="bottom-right", Text="DECK-47", Number="47-LC",
                        Width=200, Height=48, Thickness=20, Radius=16))

    # ── SHOW + ANIM ─────────────────────────────────────────────────────────
    Padd.Show()

    Cascade = Stagger()
    for B in AllBtns:
        R = Reveal(); R.StartReveal(Target=B, Period=0.2, Direction="Left"); Cascade.Add(R)
    Cascade.Play(DelayMs=25)

    TextDecode().Decode(Target=DemoStatus, Text="LCARS TITANIUM v0.3", Period=1.4)

    return Padd


LCARS.Launch(ComponentShowcase)
