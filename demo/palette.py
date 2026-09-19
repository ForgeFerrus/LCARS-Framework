# LCARS MINIMAL DEMO — PALETTE SHOWCASE
# СТАНДАРТ: Titanium

from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel
from lcars.base.component import LCARSButton, LCARSElbow, LCARSBar, LCARSLabel, LCARSIndicator
from lcars.base.default import Palette


def MinimalPaletteDemo():
    Padd = PADD(Title="LCARS MINIMAL DEMO - PALETTE SHOWCASE", Width=1000, Height=760)
    Padd.SetVertical(10, 10, 10, 10, Spacing=8)

    # Header
    Padd.Add(LCARSElbow(Corner="top-left", Text="LCARS", Number="PAL-01",
                        Width=220, Height=60, Thickness=22, Radius=18))

    Header = LCARSLabel(Text="LCARS FRAMEWORK - COMBINED MINIMAL DEMO", FontSize=26, Bold=True)
    Padd.Add(Header)

    Padd.Add(LCARSBar(Height=10))

    # Top elbows
    ElbowRow = Panel()
    ElbowRow.SetHorizontal(0, 0, 0, 0, Spacing=0)
    ElbowRow.Add(LCARSElbow(Corner="top-left", Width=200, Height=60))
    ElbowRow.AddStretch(1)
    ElbowRow.Add(LCARSElbow(Corner="top-right", Width=200, Height=60))
    Padd.Add(ElbowRow)

    Padd.Add(LCARSBar(Height=20))

    # Faction buttons (2x2 Grid)
    Factions = ["STARFLEET", "KLINGON", "ROMULAN", "CARDASSIAN"]

    GridWrapper = Panel()
    GridWrapper.SetVertical(0, 0, 0, 0, Spacing=20)

    for I in range(0, len(Factions), 2):
        Row = Panel()
        Row.SetHorizontal(0, 0, 0, 0, Spacing=30)
        Row.AddStretch(1)
        for J in range(2):
            if I + J < len(Factions):
                Name = Factions[I + J]
                Col = Panel()
                Col.SetVertical(0, 0, 0, 0, Spacing=4)
                Btn = LCARSButton(Text=Name, Number=str(I + J + 1).zfill(2),
                                  SwapMode=True, Form=LCARSButton.RectType,
                                  Width=260, Height=110, Sound="click")
                Desc = LCARSLabel(Text=Name + " - 8 COLORS", FontSize=16)
                Col.Add(Btn)
                Col.Add(Desc)
                Row.Add(Col)
        Row.AddStretch(1)
        GridWrapper.Add(Row)

    Padd.Add(GridWrapper)

    Padd.Add(LCARSBar(Height=30))

    # Era label
    Padd.Add(LCARSLabel(Text="LCARS 25TH ERA SAMPLE PALETTE", FontSize=18, Bold=True))

    # Palette samples
    PalRow = Panel()
    PalRow.SetHorizontal(0, 0, 0, 0, Spacing=10)
    for Idx in range(8):
        Swatch = LCARSButton(Text="", Number=str(Idx + 1).zfill(2),
                             SwapMode=True, Form=LCARSButton.RectType,
                             Width=90, Height=60, Sound="click")
        PalRow.Add(Swatch)
    PalRow.AddStretch(1)
    Padd.Add(PalRow)

    Padd.Add(LCARSBar(Height=20))

    # Scanning bars
    Padd.Add(LCARSBar(Height=14, Sensory=True))
    Padd.AddStretch(1)

    # Footer
    FooterRow = Panel()
    FooterRow.SetHorizontal(0, 0, 0, 0, Spacing=15)
    FooterRow.Add(LCARSButton(Text="SYSTEM DEMO", Form=LCARSButton.RectType,
                              Width=160, Height=44, Sound="click"))
    FooterRow.Add(LCARSButton(Text="PALETTE SHOWCASE", Form=LCARSButton.RectType,
                              Width=180, Height=44, Sound="click"))
    FooterRow.Add(LCARSButton(Text="CLOSE", Form=LCARSButton.RectType,
                              Width=120, Height=44, Sound="click",
                              Handler=lambda: Padd.Close()))
    FooterRow.AddStretch(1)
    Padd.Add(FooterRow)

    # Footer elbow
    Padd.Add(LCARSElbow(Corner="bottom-right", Text="DECK", Number="47-MN",
                        Width=200, Height=48, Thickness=20, Radius=16))

    Padd.Show()
    return Padd


LCARS.Launch(MinimalPaletteDemo)