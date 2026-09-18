# ◤ LCARS PADD — SECURITY ACCESS PANEL
# Код: 4721 | Макс спроб: 3
from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel, Header, Footer
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
from lcars.base.animation import TextDecode, Typewriter, Reveal, Stagger
from lcars.base.default import Palette, SystemTheme
from lcars.modules.sound import ActiveAudio

AUTH_CODE = "4721"

def PaddAccessInterface():
    Padd = PADD(Title="LCARS PADD // SECURITY ACCESS", Width=1180, Height=760)
    Padd.SetVertical(10, 10, 10, 10, Spacing=8)

    Padd.Add(Header(Title="SECURITY ACCESS TERMINAL // AUTHORIZATION REQUIRED", Spectrum=Palette.Buttons[2]))

    # ═══ BODY ═══════════════════════════════════════════════════════════════
    Body = Panel(Spectrum=Palette.Background)
    Body.SetHorizontal(0, 0, 0, 0, Spacing=12)

    # ─── ЛІВА ──────────────────────────────────────────────────────────────
    Left = Panel(Spectrum=Palette.Background)
    Left.SetVertical(0, 0, 0, 0, Spacing=6)
    Left.Add(LCARSElbow(Direction="top-left", Text="SECURITY", Number="01-SEC",
                        Width=210, Height=56, Spectrum=Palette.Buttons[1]))
    for t, c in [("ACCESS LOG", Palette.Buttons[2]), ("USER MATRIX", Palette.Buttons[0]),
                 ("CLEARANCE", Palette.Buttons[1]), ("AUDIT TRAIL", Palette.Buttons[3])]:
        Left.Add(LCARSButton(Text=t, Form=LCARSButton.PillHalfType, Direction=0,
                             Width=210, Height=36, FontSize=12, Spectrum=c))
    Left.Add(LCARSButton(Text="LOCKOUT", Form=LCARSButton.PillHalfType, Direction=0,
                         Width=210, Height=36, FontSize=12, Spectrum=Palette.Disabled[0], State="disabled"))
    Left.AddStretch()
    Left.Add(LCARSIndicator(Form=LCARSIndicator.SoftType, Width=210, Height=16, Spectrum=Palette.Buttons[2]))
    Body.Add(Left)

    # ─── ЦЕНТР ─────────────────────────────────────────────────────────────
    Center = Panel(Spectrum=Palette.Background)
    Center.SetVertical(0, 0, 0, 0, Spacing=8)

    # Дисплей
    DisplayCard = Panel(Spectrum=Palette.Background)
    DisplayCard.SetVertical(12, 10, 12, 10, Spacing=4)
    DisplayCard.Add(LCARSLabel(Text="ENTER ACCESS CODE", FontSize=13, Spectrum=Palette.Buttons[2],
                               Width=500, Height=24))
    CodeDisplay = LCARSLabel(Text="_", FontSize=36, Align="center", Spectrum=Palette.Buttons[4],
                             Width=500, Height=56)
    DisplayCard.Add(CodeDisplay)
    StatusMsg = LCARSLabel(Text="AWAITING INPUT...", FontSize=11, Align="center",
                           Spectrum=Palette.Buttons[2], Width=500, Height=22)
    DisplayCard.Add(StatusMsg)
    Center.Add(DisplayCard)

    Center.Add(LCARSBar(Form=LCARSBar.RectType, Height=3, Spectrum=Palette.Buttons[2]))

    # Стан
    S = {"code": "", "ok": False, "tries": 0}
    KeypadBtns = []

    def Refresh():
        c = S["code"]
        CodeDisplay.SetText("*" * len(c) if c else "_")
        if S["ok"]:
            StatusMsg.SetText("ACCESS GRANTED // WELCOME, COMMANDER")
            StatusMsg.Spectrum = "#00CC66"
        elif S["tries"] >= 3:
            StatusMsg.SetText("LOCKOUT // CONTACT STARFLEET COMMAND")
            StatusMsg.Spectrum = Palette.RedAlert[0]
        elif S["tries"] > 0:
            StatusMsg.SetText(f"DENIED // {3 - S['tries']} ATTEMPTS LEFT")
            StatusMsg.Spectrum = Palette.RedAlert[0]
        else:
            StatusMsg.SetText(f"CODE LENGTH: {len(c)}/8")
            StatusMsg.Spectrum = Palette.Buttons[2]

    def Digit(d):
        if S["ok"] or S["tries"] >= 3 or len(S["code"]) >= 8:
            ActiveAudio.play("denied"); return
        S["code"] += d; ActiveAudio.play("click"); Refresh()

    def Clear():
        ActiveAudio.play("click"); S["code"] = ""; S["ok"] = False; S["tries"] = 0; Refresh()

    def Back():
        if S["ok"]: ActiveAudio.play("denied"); return
        if S["code"]: S["code"] = S["code"][:-1]; ActiveAudio.play("click"); Refresh()

    def Enter():
        if S["ok"] or not S["code"]: ActiveAudio.play("denied"); return
        if S["code"] == AUTH_CODE:
            S["ok"] = True; ActiveAudio.play("acknowledge"); Refresh()
        else:
            S["tries"] += 1; ActiveAudio.play("denied"); S["code"] = ""; Refresh()

    # Клавіатура
    KeypadPanel = Panel(Spectrum=Palette.Background)
    KeypadPanel.SetVertical(0, 0, 0, 0, Spacing=5)

    for row in [("1","2","3",Palette.Buttons[2],Palette.Buttons[0],Palette.Buttons[1]),
               ("4","5","6",Palette.Buttons[0],Palette.Buttons[1],Palette.Buttons[2]),
               ("7","8","9",Palette.Buttons[1],Palette.Buttons[2],Palette.Buttons[0])]:
        R = Panel(Spectrum=Palette.Background); R.SetHorizontal(0, 0, 0, 0, Spacing=6)
        for d, c in [(row[0],row[3]),(row[1],row[4]),(row[2],row[5])]:
            b = LCARSButton(Text=d, Form=LCARSButton.RectType, Width=155, Height=54, FontSize=22, Spectrum=c)
            b.Clicked.Connect(lambda digit=d: Digit(digit)); KeypadBtns.append(b); R.Add(b)
        KeypadPanel.Add(R)

    R4 = Panel(Spectrum=Palette.Background); R4.SetHorizontal(0, 0, 0, 0, Spacing=6)
    bc = LCARSButton(Text="CLR", Form=LCARSButton.SoftHalfType, Direction=180,
                     Width=155, Height=54, FontSize=15, Spectrum=Palette.Buttons[3])
    bc.Clicked.Connect(Clear); KeypadBtns.append(bc); R4.Add(bc)
    b0 = LCARSButton(Text="0", Form=LCARSButton.RectType, Width=155, Height=54, FontSize=22, Spectrum=Palette.Buttons[4])
    b0.Clicked.Connect(lambda: Digit("0")); KeypadBtns.append(b0); R4.Add(b0)
    bb = LCARSButton(Text="BSP", Form=LCARSButton.SoftHalfType, Direction=0,
                     Width=155, Height=54, FontSize=15, Spectrum=Palette.Buttons[5])
    bb.Clicked.Connect(Back); KeypadBtns.append(bb); R4.Add(bb)
    KeypadPanel.Add(R4)

    Center.Add(KeypadPanel, 1)

    ActRow = Panel(Spectrum=Palette.Background); ActRow.SetHorizontal(0, 0, 0, 0, Spacing=10)
    ba = LCARSButton(Text="ABORT", Form=LCARSButton.PillHalfType, Direction=180,
                     Width=180, Height=44, FontSize=14, Spectrum=Palette.Buttons[3])
    ba.Clicked.Connect(Clear); KeypadBtns.append(ba); ActRow.Add(ba)
    ActRow.AddStretch()
    bk = LCARSButton(Text="CONFIRM", Form=LCARSButton.PillHalfType, Direction=0,
                     Width=180, Height=44, FontSize=14, Spectrum=Palette.Buttons[4])
    bk.Clicked.Connect(Enter); KeypadBtns.append(bk); ActRow.Add(bk)
    Center.Add(ActRow)
    Center.AddStretch()
    Body.Add(Center, 1)

    # ─── ПРАВА ─────────────────────────────────────────────────────────────
    Right = Panel(Spectrum=Palette.Background)
    Right.SetVertical(0, 0, 0, 0, Spacing=6)
    Right.Add(LCARSLabel(Text="TELEMETRY", FontSize=11, Spectrum=Palette.Buttons[0]))
    IR = Panel(Spectrum=Palette.Background); IR.SetHorizontal(0, 0, 0, 0, Spacing=4)
    IR.Add(LCARSIndicator(Form=LCARSIndicator.RectType, Width=65, Height=24, Spectrum="#00CC66"))
    IR.Add(LCARSIndicator(Form=LCARSIndicator.SoftType, Width=65, Height=24, Spectrum=Palette.Buttons[2]))
    IR.Add(LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=65, Height=24, Spectrum=Palette.Disabled[0]))
    Right.Add(IR)
    Right.Add(LCARSLabel(Text="PWR: ONLINE",  FontSize=10, Spectrum="#00CC66"))
    Right.Add(LCARSLabel(Text="NET: STABLE",  FontSize=10, Spectrum=Palette.Buttons[2]))
    Right.Add(LCARSLabel(Text="SEC: STANDBY", FontSize=10, Spectrum=Palette.Disabled[0]))
    Right.Add(LCARSBar(Form=LCARSBar.RectType, Height=2, Spectrum=Palette.Disabled[1]))
    Right.Add(LCARSLabel(Text="ALERT DIRECTIVES", FontSize=11, Spectrum=Palette.Buttons[0]))
    br = LCARSButton(Text="RED ALERT", Form=LCARSButton.PillType, Width=210, Height=38, FontSize=13, Spectrum=Palette.RedAlert[0])
    br.Clicked.Connect(lambda: SystemTheme.SetSystemState("Red")); Right.Add(br)
    by = LCARSButton(Text="YELLOW ALERT", Form=LCARSButton.PillType, Width=210, Height=38, FontSize=13, Spectrum=Palette.YellowAlert[0])
    by.Clicked.Connect(lambda: SystemTheme.SetSystemState("Yellow")); Right.Add(by)
    bg = LCARSButton(Text="CONDITION GREEN", Form=LCARSButton.PillType, Width=210, Height=38, FontSize=13, Spectrum=Palette.Buttons[0])
    bg.Clicked.Connect(lambda: SystemTheme.SetSystemState("Normal")); Right.Add(bg)
    brst = LCARSButton(Text="RESET CONSOLE", Form=LCARSButton.SoftType, Width=210, Height=36, FontSize=12, Spectrum=Palette.Buttons[3])
    brst.Clicked.Connect(Clear); Right.Add(brst)
    Right.AddStretch()
    Body.Add(Right)

    Padd.Add(Body, 1)

    Padd.Add(Footer(Title="PADD SECURITY v5.1 // ISOLINEAR OPTICAL INTERFACE ACTIVE", Spectrum=Palette.Buttons[0]))

    # ═══ SHOW + ANIM ═══════════════════════════════════════════════════════
    Padd.Show()

    Cascade = Stagger()
    for b in KeypadBtns:
        r = Reveal(); r.StartReveal(Target=b, Period=0.25, Direction="Left"); Cascade.Add(r)
    Cascade.Play(DelayMs=30)

    TextDecode().Decode(Target=StatusMsg, Text="SYSTEM READY // ENTER ACCESS CODE TO PROCEED", Period=1.4)

    return Padd

LCARS.Launch(PaddAccessInterface)
