# ◤ LCARS COMPONENT LIBRARY SHOWCASE
# Демонстрація всіх компонентів фреймворку через Compose API

from lcars.base.type import LCARS
from lcars.base.interface import Screen, Panel, Frame
from lcars.base.component import (
    LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
)
from lcars.base.animation import TextDecode, Reveal, Stagger, Blink
from lcars.base.default import Palette, SystemTheme
from lcars.modules.sound import ActiveAudio


def ComponentShowcase():
    Screen_ = Screen(Title="LCARS COMPONENT LIBRARY")

    # ── HEADER ──────────────────────────────────────────────────────────────
    Header = LCARSElbow(Corner="top-left", Text="LCARS", Number="COMP-LIB",
                        Width=320, Height=72, Thickness=28, Radius=20, Spectrum=Palette.Buttons[2])

    # ── FOOTER ──────────────────────────────────────────────────────────────
    Footer = LCARSElbow(Corner="bottom-right", Text="STARFLEET", Number="SF-47",
                        Width=320, Height=56, Thickness=24, Radius=18, Spectrum=Palette.Buttons[0])

    # ── LEFT COLUMN: BUTTONS ────────────────────────────────────────────────
    LeftCol = Panel()
    LeftCol.SetVertical(0, 0, 0, 0, Spacing=6)
    LeftCol.GetSurface().setFixedWidth(280)

    LeftCol.Add(LCARSLabel(Text="BUTTON FORMS", FontSize=12, Spectrum=Palette.Buttons[0]))

    AllBtns = []
    FormData = [
        ("RECT",        "01", LCARSButton.RectType,     0),
        ("PILL",        "02", LCARSButton.PillType,     0),
        ("SOFT",        "03", LCARSButton.SoftType,     0),
        ("PILL-HALF E", "04", LCARSButton.PillHalfType, 0),
        ("PILL-HALF W", "05", LCARSButton.PillHalfType, 180),
        ("SOFT-HALF E", "06", LCARSButton.SoftHalfType, 0),
        ("SOFT-HALF W", "07", LCARSButton.SoftHalfType, 180),
    ]

    for Txt, Num, Fm, Dr in FormData:
        B = LCARSButton(Text=Txt, Number=Num, SwapMode=True, Form=Fm, Direction=Dr,
                        Width=280, Height=40, Sound="click")
        AllBtns.append(B)
        LeftCol.Add(B)

    LeftCol.Add(LCARSBar(Height=3, Spectrum=Palette.Buttons[2]))
    LeftCol.Add(LCARSLabel(Text="BUTTON STATES", FontSize=12, Spectrum=Palette.Buttons[0]))

    for Txt, St in [("NORMAL", LCARSButton.NORMAL), ("DISABLED", LCARSButton.DISABLED),
                     ("YELLOW", LCARSButton.YELLOW), ("ALERT", LCARSButton.ALERT)]:
        B = LCARSButton(Text=Txt, State=St, Width=280, Height=40, Sound="click")
        AllBtns.append(B)
        LeftCol.Add(B)

    LeftCol.AddStretch(1)

    IndRow = Panel()
    IndRow.SetHorizontal(0, 0, 0, 0, Spacing=6)
    IndRow.Add(LCARSIndicator(Form=LCARSIndicator.RectType, Width=88, Height=28, Spectrum=Palette.Buttons[2]))
    IndRow.Add(LCARSIndicator(Form=LCARSIndicator.SoftType, Width=88, Height=28, Spectrum=Palette.Buttons[0]))
    IndRow.Add(LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=88, Height=28, Spectrum=Palette.Buttons[1]))
    LeftCol.Add(IndRow)

    # ── CENTER: INTERACTIVE DEMO ────────────────────────────────────────────
    CenterCol = Panel()
    CenterCol.SetVertical(0, 0, 0, 0, Spacing=8)

    DemoStatus = LCARSLabel(Text="LCARS COMPONENT LIBRARY", FontSize=22,
                            Align="center", Height=40, Spectrum=Palette.Buttons[2])
    CenterCol.Add(DemoStatus)

    CenterCol.Add(LCARSBar(Height=4, Spectrum=Palette.Buttons[2]))

    CenterCol.Add(LCARSLabel(Text="SYSTEM STATE CONTROL", FontSize=14, Spectrum=Palette.Buttons[0]))

    ActionRow = Panel()
    ActionRow.SetHorizontal(0, 0, 0, 0, Spacing=12)

    def OnRed():
        SystemTheme.SetSystemState("Red")
        DemoStatus.SetText("RED ALERT // ALL STATIONS TO BATTLE")
        DemoStatus.Spectrum = Palette.RedAlert[0]
        ActiveAudio.play("alertred")

    def OnYellow():
        SystemTheme.SetSystemState("Yellow")
        DemoStatus.SetText("YELLOW ALERT // CAUTION ADVISED")
        DemoStatus.Spectrum = Palette.YellowAlert[0]
        ActiveAudio.play("alertyellow")

    def OnGreen():
        SystemTheme.SetSystemState("Normal")
        DemoStatus.SetText("CONDITION GREEN // ALL SYSTEMS NOMINAL")
        DemoStatus.Spectrum = Palette.Buttons[0]
        ActiveAudio.play("ack")

    ActionRow.Add(LCARSButton(Text="RED ALERT", Form=LCARSButton.PillType, State=LCARSButton.ALERT,
                              Width=200, Height=50, Sound="alertred", Handler=OnRed))
    ActionRow.Add(LCARSButton(Text="YELLOW", Form=LCARSButton.PillType, State=LCARSButton.YELLOW,
                              Width=200, Height=50, Sound="alertyellow", Handler=OnYellow))
    ActionRow.Add(LCARSButton(Text="GREEN", Form=LCARSButton.PillType, State=LCARSButton.NORMAL,
                              Width=200, Height=50, Sound="ack", Handler=OnGreen))
    CenterCol.Add(ActionRow)

    CenterCol.Add(LCARSBar(Height=3, Spectrum=Palette.Buttons[3]))

    CenterCol.Add(LCARSLabel(Text="BARS & STRUCTURAL ELEMENTS", FontSize=14, Spectrum=Palette.Buttons[0]))

    BarPanel = Panel()
    BarPanel.SetVertical(0, 0, 0, 0, Spacing=8)
    BarPanel.Add(LCARSBar(Form=LCARSBar.RectType, Height=18, Spectrum=Palette.Buttons[2]))
    BarPanel.Add(LCARSBar(Form=LCARSBar.PillHalfType, Height=18, Spectrum=Palette.Buttons[0]))
    BarPanel.Add(LCARSBar(Form=LCARSBar.SoftType, Height=18, Spectrum=Palette.Buttons[1]))
    CenterCol.Add(BarPanel)

    CenterCol.Add(LCARSLabel(Text="ELBOW VARIANTS", FontSize=14, Spectrum=Palette.Buttons[0]))

    ElbowRow = Panel()
    ElbowRow.SetHorizontal(0, 0, 0, 0, Spacing=10)
    for Corner, Txt in [("top-left","TL"), ("top-right","TR"), ("bottom-left","BL"), ("bottom-right","BR")]:
        ElbowRow.Add(LCARSElbow(Corner=Corner, Text=Txt, Width=180, Height=70,
                                Thickness=22, Radius=16, Spectrum=Palette.Buttons[1]))
    ElbowRow.AddStretch()
    CenterCol.Add(ElbowRow)

    CenterCol.AddStretch(1)

    ScanBar = LCARSIndicator(Form=LCARSIndicator.SoftType, Height=10, Spectrum=Palette.Buttons[2])
    CenterCol.Add(ScanBar)
    Blink(Target=ScanBar, Period=0.7, Loop=True).Start()

    # ── RIGHT COLUMN: INDICATORS + TELEMETRY ────────────────────────────────
    RightCol = Panel()
    RightCol.SetVertical(0, 0, 0, 0, Spacing=6)
    RightCol.GetSurface().setFixedWidth(280)

    RightCol.Add(LCARSLabel(Text="INDICATORS (BLINK)", FontSize=12, Spectrum=Palette.Buttons[0]))

    IndColors = ["#00CC66", Palette.Buttons[2], Palette.Buttons[4], Palette.RedAlert[0], Palette.YellowAlert[0]]
    IndForms = [LCARSIndicator.RectType, LCARSIndicator.SoftType, LCARSIndicator.PillHalf,
                LCARSIndicator.RectType, LCARSIndicator.SoftType]

    for i in range(5):
        Ind = LCARSIndicator(Form=IndForms[i], Width=280, Height=22, Spectrum=IndColors[i])
        RightCol.Add(Ind)
        Blink(Target=Ind, Period=0.4 + i * 0.2, Loop=True).Start()

    RightCol.Add(LCARSBar(Height=3, Spectrum=Palette.Disabled[1]))

    RightCol.Add(LCARSLabel(Text="DYNAMIC LABELS", FontSize=12, Spectrum=Palette.Buttons[0]))

    DynLabel = LCARSLabel(Text="COLOR CYCLING", FontSize=16, Height=32, Spectrum=Palette.Buttons[2])
    RightCol.Add(DynLabel)
    Blink(Target=DynLabel, Period=1.2, Loop=True,
          ActiveColor=Palette.Buttons[4], OffColor=Palette.Buttons[0]).Start()

    RightCol.Add(LCARSBar(Height=3, Spectrum=Palette.Disabled[1]))

    RightCol.Add(LCARSLabel(Text="PALETTE STRIP", FontSize=12, Spectrum=Palette.Buttons[0]))

    for Col in Palette.Buttons[:6]:
        RightCol.Add(LCARSBar(Form=LCARSBar.RectType, Width=280, Height=14, Spectrum=Col))

    RightCol.AddStretch(1)

    # ── ASSEMBLE VIA COMPOSE ────────────────────────────────────────────────
    CenterFrame = Frame()
    CenterFrame.Compose(TopBar=Header, LeftPillar=LeftCol, Content=CenterCol, RightPillar=RightCol, BottomBar=Footer)
    Screen_.Add(CenterFrame, 1)

    Screen_.Show()

    Cascade = Stagger()
    for B in AllBtns:
        R = Reveal(); R.StartReveal(Target=B, Period=0.2, Direction="Left"); Cascade.Add(R)
    Cascade.Play(DelayMs=25)

    TextDecode().Decode(Target=DemoStatus, Text="LCARS COMPONENT LIBRARY READY", Period=1.4)

    return Screen_


LCARS.Launch(ComponentShowcase)
