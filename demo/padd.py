# ◤ LCARS PADD — SECURITY ACCESS TERMINAL
# Код: 4721 | Макс спроб: 3 | Стандарт: Titanium

from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
from lcars.base.animation import TextDecode, Reveal, Stagger, Blink
from lcars.base.default import Palette, SystemTheme
from lcars.modules.sound import ActiveAudio

AuthCode = "4721"

def PaddAccessInterface():
    Padd = PADD(Title="LCARS PADD // SECURITY ACCESS TERMINAL", Width=320, Height=480)
    Padd.SetVertical(6, 6, 6, 6, Spacing=6)

    Padd.Add(LCARSElbow(Corner="top-left", Text="SECURITY", Number="SEC-47",
                        Width=180, Height=44, Thickness=18, Radius=14))

    Padd.Add(LCARSLabel(Text="ENTER AUTHORIZATION CODE", FontSize=12))

    CodeDisplay = LCARSLabel(Text="*", FontSize=36, Align="center", Height=50)
    Padd.Add(CodeDisplay)

    StatusMsg = LCARSLabel(Text="AWAITING INPUT...", Align="center", Height=24)
    Padd.Add(StatusMsg)

    Padd.Add(LCARSBar(Height=3))

    S = {"code": "", "ok": False, "tries": 0}
    KeypadBtns = []

    def UpdateDisplay():
        c = S["code"]
        CodeDisplay.SetText("*" * len(c) if c else "EMPTY")
        if S["ok"]:
            StatusMsg.SetText("ACCESS GRANTED")
            StatusMsg.Spectrum = "#00CC66"
        elif S["tries"] >= 3:
            StatusMsg.SetText("LOCKOUT")
            StatusMsg.Spectrum = Palette.RedAlert[0]
        elif S["tries"] > 0:
            StatusMsg.SetText(f"DENIED // {3 - S['tries']} LEFT")
            StatusMsg.Spectrum = Palette.RedAlert[0]
        else:
            StatusMsg.SetText(f"BUFFER: {len(c)} / 8")

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

    for RowTuple in [("1","2","3"), ("4","5","6"), ("7","8","9")]:
        RowPanel = Panel()
        RowPanel.SetHorizontal(0, 0, 0, 0, Spacing=4)
        for D in RowTuple:
            B = LCARSButton(Text=D, Form=LCARSButton.RectType, Width=96, Height=44,
                            FontSize=20, Sound="click", Handler=lambda d=D: AddDigit(d))
            KeypadBtns.append(B)
            RowPanel.Add(B)
        Padd.Add(RowPanel)

    BottomRow = Panel()
    BottomRow.SetHorizontal(0, 0, 0, 0, Spacing=4)
    bc = LCARSButton(Text="CLR", Form=LCARSButton.SoftHalfType, Direction=180,
                     Width=96, Height=44, Sound="click", Handler=ClearCode)
    KeypadBtns.append(bc); BottomRow.Add(bc)
    b0 = LCARSButton(Text="0", Form=LCARSButton.RectType, Width=96, Height=44,
                     FontSize=20, Sound="click", Handler=lambda: AddDigit("0"))
    KeypadBtns.append(b0); BottomRow.Add(b0)
    bb = LCARSButton(Text="BSP", Form=LCARSButton.SoftHalfType, Direction=0,
                     Width=96, Height=44, Sound="click", Handler=BackspaceCode)
    KeypadBtns.append(bb); BottomRow.Add(bb)
    Padd.Add(BottomRow)

    ActionRow = Panel()
    ActionRow.SetHorizontal(0, 0, 0, 0, Spacing=6)
    ba = LCARSButton(Text="ABORT", Form=LCARSButton.PillHalfType, Direction=180,
                     Width=140, Height=40, Sound="click", Handler=ClearCode)
    KeypadBtns.append(ba); ActionRow.Add(ba)
    bk = LCARSButton(Text="CONFIRM", Form=LCARSButton.PillHalfType, Direction=0,
                     Width=140, Height=40, Sound="ack", Handler=SubmitCode)
    KeypadBtns.append(bk); ActionRow.Add(bk)
    Padd.Add(ActionRow)

    Padd.Add(LCARSBar(Height=3))

    IndRow = Panel()
    IndRow.SetHorizontal(0, 0, 0, 0, Spacing=4)
    IndPwr = LCARSIndicator(Form=LCARSIndicator.RectType, Width=96, Height=20)
    IndNet = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=96, Height=20)
    IndSec = LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=96, Height=20)
    IndRow.Add(IndPwr); IndRow.Add(IndNet); IndRow.Add(IndSec)
    Padd.Add(IndRow)

    Padd.Add(LCARSElbow(Corner="bottom-right", Text="DECK-47", Number="47-LC",
                        Width=180, Height=40, Thickness=16, Radius=14))

    Padd.Show()

    Cascade = Stagger()
    for B in KeypadBtns:
        R = Reveal(); R.StartReveal(Target=B, Period=0.25, Direction="Left"); Cascade.Add(R)
    Cascade.Play(DelayMs=30)

    TextDecode().Decode(Target=StatusMsg, Text="ENTER 4-DIGIT PIN", Period=1.2)

    Blink(Target=IndPwr, Period=0.6, Loop=True).Start()
    Blink(Target=IndNet, Period=0.8, Loop=True).Start()
    Blink(Target=IndSec, Period=1.0, Loop=True).Start()

    return Padd


LCARS.Launch(PaddAccessInterface)
