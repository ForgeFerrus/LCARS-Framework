# ◤ LCARS PADD — SECURITY ACCESS TERMINAL
# Код: 4721 | Макс спроб: 3 | Стандарт: Titanium

from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel, Header, Footer
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
from lcars.base.animation import TextDecode, Reveal, Stagger, Blink
from lcars.base.default import Palette, SystemTheme
from lcars.modules.sound import ActiveAudio

AuthCode = "4721"

def PaddAccessInterface():
    Padd = PADD(Title="LCARS PADD // SECURITY ACCESS TERMINAL", Width=180, Height=260)
    Padd.SetVertical(10, 10, 10, 10, Spacing=8)

    Padd.Add(Header(Title="SECURITY CLEARANCE TERMINAL // AUTHORIZATION REQUIRED", Spectrum=Palette.Buttons[2]))

    Body = Panel(Spectrum=Palette.Background)
    Body.SetHorizontal(0, 0, 0, 0, Spacing=12)

    # ─── ЛІВА: НАВІГАЦІЯ ──────────────────────────────────────────────────
    Left = Panel(Spectrum=Palette.Background)
    Left.SetVertical(0, 0, 0, 0, Spacing=6)
    Left.Add(LCARSElbow(Corner="top-left", Text="SECURITY", Number="SEC-47",
                        Width=230, Height=54, Thickness=22, Radius=18, Spectrum=Palette.Buttons[1]))
    for NavTitle in ["ACCESS LOG", "USER MATRIX", "CLEARANCE", "AUDIT TRAIL"]:
        Left.Add(LCARSButton(Text=NavTitle, Form=LCARSButton.PillHalfType, Direction=0,
                             Width=230, Height=38, Sound="click"))
    Left.Add(LCARSButton(Text="LOCKOUT", Form=LCARSButton.PillHalfType, Direction=0,
                         Width=230, Height=38, State="disabled"))
    Left.AddStretch(1)
    Left.Add(LCARSIndicator(Form=LCARSIndicator.SoftType, Width=230, Height=22, Spectrum=Palette.Buttons[2]))
    Body.Add(Left)

    # ─── ЦЕНТР: ДИСПЛЕЙ + КЛАВІАТУРА ─────────────────────────────────────
    Center = Panel(Spectrum=Palette.Background)
    Center.SetVertical(0, 0, 0, 0, Spacing=8)

    DisplayCard = Panel(Spectrum=Palette.Background)
    DisplayCard.SetVertical(10, 12, 10, 12, Spacing=4)
    DisplayCard.Add(LCARSLabel(Text="ENTER AUTHORIZATION CODE", Height=26, Spectrum=Palette.Buttons[2]))
    CodeDisplay = LCARSLabel(Text="*", FontSize=36, Align="center", Height=56, Spectrum=Palette.Buttons[4])
    DisplayCard.Add(CodeDisplay)
    StatusMsg = LCARSLabel(Text="AWAITING INPUT...", Align="center", Height=26, Spectrum=Palette.Buttons[2])
    DisplayCard.Add(StatusMsg)
    Center.Add(DisplayCard)

    Center.Add(LCARSBar(Height=3, Spectrum=Palette.Buttons[2]))

    S = {"code": "", "ok": False, "tries": 0}
    KeypadBtns = []

    def UpdateDisplay():
        c = S["code"]
        CodeDisplay.SetText("*" * len(c) if c else "EMPTY")
        if S["ok"]:
            StatusMsg.SetText("ACCESS GRANTED // COMMAND CONSOLE OPEN")
            StatusMsg.Spectrum = "#00CC66"
        elif S["tries"] >= 3:
            StatusMsg.SetText("LOCKOUT // CONTACT STARFLEET COMMAND")
            StatusMsg.Spectrum = Palette.RedAlert[0]
        elif S["tries"] > 0:
            StatusMsg.SetText(f"DENIED // {3 - S['tries']} ATTEMPTS REMAINING")
            StatusMsg.Spectrum = Palette.RedAlert[0]
        else:
            StatusMsg.SetText(f"BUFFER: {len(c)} / 8 DIGITS")
            StatusMsg.Spectrum = Palette.Buttons[2]

    def AddDigit(d):
        if S["ok"] or S["tries"] >= 3 or len(S["code"]) >= 8:
            ActiveAudio.play("denied"); return
        S["code"] += d; ActiveAudio.play("click"); UpdateDisplay()

    def ClearCode():
        ActiveAudio.play("click")
        S["code"] = ""; S["ok"] = False; S["tries"] = 0; UpdateDisplay()

    def BackspaceCode():
        if S["ok"]: ActiveAudio.play("denied"); return
        if S["code"]:
            S["code"] = S["code"][:-1]; ActiveAudio.play("click"); UpdateDisplay()

    def SubmitCode():
        if S["ok"] or not S["code"]:
            ActiveAudio.play("denied"); return
        if S["code"] == AuthCode:
            S["ok"] = True; ActiveAudio.play("ack"); UpdateDisplay()
        else:
            S["tries"] += 1; ActiveAudio.play("denied"); S["code"] = ""; UpdateDisplay()

    KeypadPanel = Panel(Spectrum=Palette.Background)
    KeypadPanel.SetVertical(0, 0, 0, 0, Spacing=6)

    for RowTuple in [("1","2","3"), ("4","5","6"), ("7","8","9")]:
        RowPanel = Panel(Spectrum=Palette.Background)
        RowPanel.SetHorizontal(0, 0, 0, 0, Spacing=6)
        for D in RowTuple:
            B = LCARSButton(Text=D, Form=LCARSButton.RectType, Width=160, Height=52,
                            FontSize=24, Sound="click",
                            Handler=lambda d=D: AddDigit(d))
            KeypadBtns.append(B)
            RowPanel.Add(B)
        KeypadPanel.Add(RowPanel)

    BottomRow = Panel(Spectrum=Palette.Background)
    BottomRow.SetHorizontal(0, 0, 0, 0, Spacing=6)
    bc = LCARSButton(Text="CLR", Form=LCARSButton.SoftHalfType, Direction=180,
                     Width=160, Height=52, Sound="click", Handler=ClearCode)
    KeypadBtns.append(bc); BottomRow.Add(bc)
    b0 = LCARSButton(Text="0", Form=LCARSButton.RectType, Width=160, Height=52,
                     FontSize=24, Sound="click", Handler=lambda: AddDigit("0"))
    KeypadBtns.append(b0); BottomRow.Add(b0)
    bb = LCARSButton(Text="BSP", Form=LCARSButton.SoftHalfType, Direction=0,
                     Width=160, Height=52, Sound="click", Handler=BackspaceCode)
    KeypadBtns.append(bb); BottomRow.Add(bb)
    KeypadPanel.Add(BottomRow)
    Center.Add(KeypadPanel, 1)

    ActionRow = Panel(Spectrum=Palette.Background)
    ActionRow.SetHorizontal(0, 0, 0, 0, Spacing=10)
    ba = LCARSButton(Text="ABORT", Form=LCARSButton.PillHalfType, Direction=180,
                     Width=190, Height=46, Sound="click", Handler=ClearCode)
    KeypadBtns.append(ba); ActionRow.Add(ba)
    ActionRow.AddStretch(1)
    bk = LCARSButton(Text="CONFIRM", Form=LCARSButton.PillHalfType, Direction=0,
                     Width=190, Height=46, Sound="ack", Handler=SubmitCode)
    KeypadBtns.append(bk); ActionRow.Add(bk)
    Center.Add(ActionRow)
    Center.AddStretch(1)
    Body.Add(Center, 1)

    # ─── ПРАВА: ТЕЛЕМЕТРІЯ + ТРИВОГА ──────────────────────────────────────
    Right = Panel(Spectrum=Palette.Background)
    Right.SetVertical(0, 0, 0, 0, Spacing=6)
    Right.Add(LCARSLabel(Text="SECURITY TELEMETRY", Height=24, Spectrum=Palette.Buttons[0]))

    IndRow = Panel(Spectrum=Palette.Background)
    IndRow.SetHorizontal(0, 0, 0, 0, Spacing=4)
    IndPwr = LCARSIndicator(Form=LCARSIndicator.RectType, Width=72, Height=26, Spectrum="#00CC66")
    IndNet = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=72, Height=26, Spectrum=Palette.Buttons[2])
    IndSec = LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=72, Height=26, Spectrum=Palette.Disabled[0])
    IndRow.Add(IndPwr); IndRow.Add(IndNet); IndRow.Add(IndSec)
    Right.Add(IndRow)

    Right.Add(LCARSLabel(Text="POWER GRID: ONLINE", Height=22, Spectrum="#00CC66"))
    Right.Add(LCARSLabel(Text="ODN NETWORK: STABLE", Height=22, Spectrum=Palette.Buttons[2]))
    Right.Add(LCARSLabel(Text="SECURITY BUS: ACTIVE", Height=22, Spectrum=Palette.Disabled[0]))
    Right.Add(LCARSBar(Height=3, Spectrum=Palette.Disabled[1]))
    Right.Add(LCARSLabel(Text="ALERT DIRECTIVES", Height=24, Spectrum=Palette.Buttons[0]))

    def SetRed():
        SystemTheme.SetSystemState("Red")
        IndPwr.Spectrum = Palette.RedAlert[0]; IndPwr.Refresh()
        IndNet.Spectrum = Palette.RedAlert[1]; IndNet.Refresh()
        IndSec.Spectrum = Palette.RedAlert[2]; IndSec.Refresh()
        StatusMsg.SetText("RED ALERT ACTIVATED"); StatusMsg.Spectrum = Palette.RedAlert[0]
        ActiveAudio.play("alertred")

    def SetYellow():
        SystemTheme.SetSystemState("Yellow")
        IndPwr.Spectrum = Palette.YellowAlert[0]; IndPwr.Refresh()
        IndNet.Spectrum = Palette.YellowAlert[1]; IndNet.Refresh()
        IndSec.Spectrum = Palette.YellowAlert[2]; IndSec.Refresh()
        StatusMsg.SetText("YELLOW ALERT ACTIVATED"); StatusMsg.Spectrum = Palette.YellowAlert[0]
        ActiveAudio.play("alertyellow")

    def SetGreen():
        SystemTheme.SetSystemState("Normal")
        IndPwr.Spectrum = "#00CC66"; IndPwr.Refresh()
        IndNet.Spectrum = Palette.Buttons[2]; IndNet.Refresh()
        IndSec.Spectrum = Palette.Disabled[0]; IndSec.Refresh()
        StatusMsg.SetText("CONDITION GREEN RESTORED"); StatusMsg.Spectrum = Palette.Buttons[0]
        ActiveAudio.play("ack")

    Right.Add(LCARSButton(Text="RED ALERT", Form=LCARSButton.PillType, Width=230, Height=40,
                          State="alert", Sound="alertred", Handler=SetRed))
    Right.Add(LCARSButton(Text="YELLOW ALERT", Form=LCARSButton.PillType, Width=230, Height=40,
                          State="yellow", Sound="alertyellow", Handler=SetYellow))
    Right.Add(LCARSButton(Text="CONDITION GREEN", Form=LCARSButton.PillType, Width=230, Height=40,
                          State="normal", Sound="ack", Handler=SetGreen))
    Right.Add(LCARSButton(Text="RESET CONSOLE", Form=LCARSButton.SoftType, Width=230, Height=38,
                          Sound="click", Handler=ClearCode))
    Right.AddStretch(1)
    Body.Add(Right)

    Padd.Add(Body, 1)
    Padd.Add(Footer(Title="LCARS SECURITY v5.1 // BIOMETRIC & CODE CONDUIT OPERATIONAL", Spectrum=Palette.Buttons[0]))

    # ── SHOW + ANIM ────────────────────────────────────────────────────────
    Padd.Show()

    Cascade = Stagger()
    for B in KeypadBtns:
        R = Reveal(); R.StartReveal(Target=B, Period=0.25, Direction="Left"); Cascade.Add(R)
    Cascade.Play(DelayMs=30)

    TextDecode().Decode(Target=StatusMsg, Text="ENTER 4-DIGIT SECURITY PIN", Period=1.2)

    Blink(Target=IndPwr, Period=0.6, Loop=True).Start()
    Blink(Target=IndNet, Period=0.8, Loop=True).Start()
    Blink(Target=IndSec, Period=1.0, Loop=True).Start()

    return Padd


LCARS.Launch(PaddAccessInterface)
