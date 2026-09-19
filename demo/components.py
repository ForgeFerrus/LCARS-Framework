# ◤ LCARS COMPONENT LIBRARY SHOWCASE
# Демонстрація всіх компонентів фреймворку: кнопки, індикатори, балки, лікті, анімації

from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel, Header, Footer
from lcars.base.component import (
    LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
)
from lcars.base.animation import TextDecode, Reveal, Stagger, Blink
from lcars.base.default import Palette, SystemTheme
from lcars.modules.sound import ActiveAudio


def ComponentShowcase():
    Padd = PADD(Title="LCARS COMPONENT LIBRARY", Width=1320, Height=820)
    Padd.SetVertical(10, 10, 10, 10, Spacing=8)

    TopBar = Panel(Spectrum=Palette.Buttons[2])
    TopBar.SetHorizontal(8, 0, 0, 0, Spacing=12)
    TopBar.Add(LCARSElbow(Corner="top-left", Text="LCARS", Width=120, Height=48, Thickness=18, Radius=16, Spectrum=Palette.Buttons[2]))
    TopBar.Add(LCARSLabel(Text="COMPONENT LIBRARY // TITANIUM STANDARD", FontSize=18, Spectrum=Palette.Background))
    Padd.Add(TopBar)

    Body = Panel(Spectrum=Palette.Background)
    Body.SetHorizontal(0, 0, 0, 0, Spacing=14)

    # ─── ЛІВА: КНОПКИ ─────────────────────────────────────────────────────
    Left = Panel(Spectrum=Palette.Background)
    Left.SetVertical(0, 0, 0, 0, Spacing=6)

    Left.Add(LCARSElbow(Corner="top-left", Text="BUTTONS", Number="01-BTN",
                        Width=260, Height=64, Thickness=24, Radius=18, Spectrum=Palette.Buttons[1]))

    Left.Add(LCARSLabel(Text="FORMS", FontSize=12, Spectrum=Palette.Buttons[0]))

    AllBtns = []

    FormData = [
        ("RECT",       "01", LCARSButton.RectType,     0),
        ("PILL",       "02", LCARSButton.PillType,     0),
        ("SOFT",       "03", LCARSButton.SoftType,     0),
        ("PILL-HALF E","04", LCARSButton.PillHalfType, 0),
        ("PILL-HALF W","05", LCARSButton.PillHalfType, 180),
        ("SOFT-HALF E","06", LCARSButton.SoftHalfType, 0),
        ("SOFT-HALF W","07", LCARSButton.SoftHalfType, 180),
    ]

    for Txt, Num, Fm, Dr in FormData:
        B = LCARSButton(Text=Txt, Number=Num, SwapMode=True, Form=Fm, Direction=Dr,
                        Width=260, Height=38, Sound="click",
                        Handler=lambda t=Txt: ActiveAudio.play("click"))
        AllBtns.append(B)
        Left.Add(B)

    Left.Add(LCARSBar(Height=3, Spectrum=Palette.Buttons[2]))
    Left.Add(LCARSLabel(Text="STATES", FontSize=12, Spectrum=Palette.Buttons[0]))

    StateData = [
        ("NORMAL",  LCARSButton.NORMAL,  Palette.Buttons[2]),
        ("DISABLED",LCARSButton.DISABLED,Palette.Disabled[0]),
        ("YELLOW",  LCARSButton.YELLOW,  Palette.YellowAlert[0]),
        ("ALERT",   LCARSButton.ALERT,   Palette.RedAlert[0]),
    ]

    for Txt, St, Col in StateData:
        B = LCARSButton(Text=Txt, State=St, Width=260, Height=38, Sound="click",
                        Handler=lambda s=St: SystemTheme.SetSystemState(s.replace("YellowAlert","Yellow").replace("RedAlert","Red").replace("Normal","Normal")))
        AllBtns.append(B)
        Left.Add(B)

    Left.AddStretch(1)

    IndRow = Panel(Spectrum=Palette.Background)
    IndRow.SetHorizontal(0, 0, 0, 0, Spacing=4)
    for Fm in [LCARSIndicator.RectType, LCARSIndicator.SoftType, LCARSIndicator.PillHalf]:
        IndRow.Add(LCARSIndicator(Form=Fm, Width=82, Height=26, Spectrum=Palette.Buttons[2]))
    Left.Add(IndRow)

    Left.Add(LCARSElbow(Corner="bottom-left", Text="DECK-47", Number="47-LC",
                        Width=260, Height=52, Thickness=22, Radius=18, Spectrum=Palette.Buttons[0]))
    Body.Add(Left)

    # ─── ЦЕНТР: БАЛКИ + ЛІКТІ + ДЕМО ─────────────────────────────────────
    Center = Panel(Spectrum=Palette.Background)
    Center.SetVertical(0, 0, 0, 0, Spacing=8)

    Center.Add(LCARSLabel(Text="STRUCTURAL ELEMENTS", FontSize=16, Spectrum=Palette.Buttons[0]))

    ElbowRow = Panel(Spectrum=Palette.Background)
    ElbowRow.SetHorizontal(0, 0, 0, 0, Spacing=10)
    for Corner, Txt in [("top-left","TL"), ("top-right","TR"), ("bottom-left","BL"), ("bottom-right","BR")]:
        ElbowRow.Add(LCARSElbow(Corner=Corner, Text=Txt, Width=200, Height=70,
                                Thickness=20, Radius=16, Spectrum=Palette.Buttons[1]))
    ElbowRow.AddStretch()
    Center.Add(ElbowRow)

    Center.Add(LCARSLabel(Text="BARS", FontSize=12, Spectrum=Palette.Buttons[0]))

    BarCol = Panel(Spectrum=Palette.Background)
    BarCol.SetVertical(0, 0, 0, 0, Spacing=6)
    BarCol.Add(LCARSBar(Form=LCARSBar.RectType, Width=500, Height=16, Spectrum=Palette.Buttons[2]))
    BarCol.Add(LCARSBar(Form=LCARSBar.PillHalfType, Width=500, Height=16, Spectrum=Palette.Buttons[0]))
    BarCol.Add(LCARSBar(Form=LCARSBar.SoftType, Width=500, Height=16, Spectrum=Palette.Buttons[1]))
    Center.Add(BarCol)

    Center.Add(LCARSBar(Height=3, Spectrum=Palette.Buttons[3]))

    Center.Add(LCARSLabel(Text="INTERACTIVE DEMO", FontSize=12, Spectrum=Palette.Buttons[0]))

    DemoCard = Panel(Spectrum=Palette.Background)
    DemoCard.SetVertical(8, 10, 8, 10, Spacing=6)

    DemoStatus = LCARSLabel(Text="TOUCH ANY BUTTON TO ENGAGE", FontSize=16,
                            Align="center", Height=32, Spectrum=Palette.Buttons[2])
    DemoCard.Add(DemoStatus)

    ActionRow = Panel(Spectrum=Palette.Background)
    ActionRow.SetHorizontal(0, 0, 0, 0, Spacing=8)

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

    ActionRow.Add(LCARSButton(Text="RED ALERT", Form=LCARSButton.PillType, State="alert",
                              Width=180, Height=44, Sound="alertred", Handler=OnRed))
    ActionRow.Add(LCARSButton(Text="YELLOW", Form=LCARSButton.PillType, State="yellow",
                              Width=180, Height=44, Sound="alertyellow", Handler=OnYellow))
    ActionRow.Add(LCARSButton(Text="GREEN", Form=LCARSButton.PillType, State="normal",
                              Width=180, Height=44, Sound="ack", Handler=OnGreen))
    DemoCard.Add(ActionRow)

    ScanBar = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=500, Height=12, Spectrum=Palette.Buttons[2])
    DemoCard.Add(ScanBar)
    Blink(Target=ScanBar, Period=0.7, Loop=True).Start()

    Center.Add(DemoCard, 1)
    Center.AddStretch(1)
    Body.Add(Center, 1)

    # ─── ПРАВА: ІНДИКАТОРИ + ТЕЛЕМЕТРІЯ ───────────────────────────────────
    Right = Panel(Spectrum=Palette.Background)
    Right.SetVertical(0, 0, 0, 0, Spacing=6)

    Right.Add(LCARSElbow(Corner="top-right", Text="TELEMETRY", Number="02-TLM",
                         Width=260, Height=54, Thickness=22, Radius=18, Spectrum=Palette.Buttons[3]))

    Right.Add(LCARSLabel(Text="INDICATORS (BLINK)", FontSize=12, Spectrum=Palette.Buttons[0]))

    Indicators = []
    IndColors = ["#00CC66", Palette.Buttons[2], Palette.Buttons[4], Palette.RedAlert[0], Palette.YellowAlert[0]]
    IndForms = [LCARSIndicator.RectType, LCARSIndicator.SoftType, LCARSIndicator.PillHalf,
                LCARSIndicator.RectType, LCARSIndicator.SoftType]

    for i in range(5):
        Ind = LCARSIndicator(Form=IndForms[i], Width=260, Height=20, Spectrum=IndColors[i])
        Indicators.append(Ind)
        Right.Add(Ind)
        Blink(Target=Ind, Period=0.4 + i * 0.2, Loop=True).Start()

    Right.Add(LCARSBar(Height=3, Spectrum=Palette.Disabled[1]))

    Right.Add(LCARSLabel(Text="DYNAMIC LABELS", FontSize=12, Spectrum=Palette.Buttons[0]))

    DynLabel = LCARSLabel(Text="DYNAMIC COLOR CYCLING", FontSize=14, Height=28, Spectrum=Palette.Buttons[2])
    Right.Add(DynLabel)
    Blink(Target=DynLabel, Period=1.2, Loop=True,
          ActiveColor=Palette.Buttons[4], OffColor=Palette.Buttons[0]).Start()

    Right.Add(LCARSBar(Height=3, Spectrum=Palette.Disabled[1]))

    Right.Add(LCARSLabel(Text="BARS GALLERY", FontSize=12, Spectrum=Palette.Buttons[0]))

    PaletteColors = Palette.Buttons[:6]
    for i, Col in enumerate(PaletteColors):
        Right.Add(LCARSBar(Form=LCARSBar.RectType, Width=260, Height=12, Spectrum=Col))

    Right.AddStretch(1)

    Right.Add(LCARSElbow(Corner="bottom-right", Text="STARFLEET", Number="SF-47",
                         Width=260, Height=52, Thickness=22, Radius=18, Spectrum=Palette.Buttons[4]))

    Body.Add(Right)

    Padd.Add(Body, 1)
    BotBar = Panel(Spectrum=Palette.Buttons[0])
    BotBar.SetHorizontal(0, 0, 8, 0, Spacing=12)
    BotBar.Add(LCARSLabel(Text="LCARS TITANIUM v0.3 // ALL COMPONENTS OPERATIONAL", FontSize=12, Spectrum=Palette.Background))
    BotBar.Add(LCARSElbow(Corner="bottom-right", Text="EXIT", Width=120, Height=48, Thickness=18, Radius=16, Spectrum=Palette.Buttons[0]))
    Padd.Add(BotBar)

    # ── SHOW + ANIM ────────────────────────────────────────────────────────
    Padd.Show()

    Cascade = Stagger()
    for B in AllBtns:
        R = Reveal(); R.StartReveal(Target=B, Period=0.2, Direction="Left"); Cascade.Add(R)
    Cascade.Play(DelayMs=25)

    TextDecode().Decode(Target=DemoStatus, Text="LCARS COMPONENT LIBRARY READY", Period=1.4)

    return Padd


LCARS.Launch(ComponentShowcase)
