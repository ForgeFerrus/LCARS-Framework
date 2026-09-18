# ◤ LCARS PADD — SECURITY ACCESS PANEL
# Функціональний планшет офіцера з клавіатурою, анімаціями та системою авторизації.
# Код доступу: 4721 | Макс. спроб: 3 | Lockout після 3-х невдач.
# ─────────────────────────────────────────────────────────────────────────────
from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel, Header, Footer
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
from lcars.base.animation import TextDecode, Typewriter, Reveal, Stagger
from lcars.base.default import Palette, SystemTheme
from lcars.modules.sound import ActiveAudio

AUTH_CODE = "4721"
MAX_CODE = 8


def PaddAccessInterface():
    # ═══════════════════════════════════════════════════════════════════════
    # PADD
    # ═══════════════════════════════════════════════════════════════════════
    Padd = PADD(Title="LCARS PADD // SECURITY ACCESS TERMINAL", Width=1100, Height=720)
    Padd.SetVertical(10, 10, 10, 10, Spacing=8)

    # ═══════════════════════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════════════════════
    TopHeader = Header(Title="SECURITY ACCESS TERMINAL // AUTHORIZATION REQUIRED", Spectrum=Palette.Buttons[2])
    Padd.Add(TopHeader)

    # ═══════════════════════════════════════════════════════════════════════
    # BODY — три колонки
    # ═══════════════════════════════════════════════════════════════════════
    Body = Panel(Spectrum=Palette.Background)
    Body.SetHorizontal(0, 0, 0, 0, Spacing=12)

    # ─── ЛІВА: навігація ──────────────────────────────────────────────────
    LeftCol = Panel(Spectrum=Palette.Background)
    LeftCol.SetVertical(0, 0, 0, 0, Spacing=6)

    ElbowNav = LCARSElbow(Direction="top-left", Text="SECURITY", Number="01-SEC",
                          Width=210, Height=56, Spectrum=Palette.Buttons[1])
    LeftCol.Add(ElbowNav)

    NavBtns = []
    for Txt, Clr in [("ACCESS LOG", Palette.Buttons[2]), ("USER MATRIX", Palette.Buttons[0]),
                     ("CLEARANCE", Palette.Buttons[1]), ("AUDIT TRAIL", Palette.Buttons[3])]:
        B = LCARSButton(Text=Txt, Form=LCARSButton.PillHalfType, Direction=0,
                        Width=210, Height=36, FontSize=12, Spectrum=Clr)
        NavBtns.append(B)
        LeftCol.Add(B)

    LockBtn = LCARSButton(Text="LOCKOUT", Form=LCARSButton.PillHalfType, Direction=0,
                          Width=210, Height=36, FontSize=12, Spectrum=Palette.Disabled[0], State="disabled")
    LeftCol.Add(LockBtn)

    LeftCol.AddStretch()

    SysIndicator = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=210, Height=16,
                                  Spectrum=Palette.Buttons[2])
    LeftCol.Add(SysIndicator)

    Body.Add(LeftCol)

    # ─── ЦЕНТР: дисплей + клавіатура ─────────────────────────────────────
    CenterCol = Panel(Spectrum=Palette.Background)
    CenterCol.SetVertical(0, 0, 0, 0, Spacing=8)

    # --- Дисплей ---
    DisplayCard = Panel(Spectrum=Palette.Background)
    DisplayCard.SetVertical(12, 10, 12, 10, Spacing=4)

    DisplayTitle = LCARSLabel(Text="ENTER ACCESS CODE", FontSize=13, Spectrum=Palette.Buttons[2],
                              Width=480, Height=24)
    DisplayCard.Add(DisplayTitle)

    CodeDisplay = LCARSLabel(Text="_", FontSize=36, Align="center", Spectrum=Palette.Buttons[4],
                             Width=480, Height=56)
    DisplayCard.Add(CodeDisplay)

    StatusMsg = LCARSLabel(Text="AWAITING INPUT...", FontSize=11, Align="center",
                           Spectrum=Palette.Buttons[2], Width=480, Height=22)
    DisplayCard.Add(StatusMsg)

    CenterCol.Add(DisplayCard)

    # Розділювач
    CenterCol.Add(LCARSBar(Form=LCARSBar.RectType, Height=3, Spectrum=Palette.Buttons[2]))

    # --- Клавіатура ---
    KeypadPanel = Panel(Spectrum=Palette.Background)
    KeypadPanel.SetVertical(0, 0, 0, 0, Spacing=5)

    # Стан
    State = {"code": "", "auth": False, "attempts": 0}

    KeypadBtns = []

    def UpdateDisplay():
        c = State["code"]
        CodeDisplay.SetText("*" * len(c) if c else "_")
        if State["auth"]:
            StatusMsg.SetText("ACCESS GRANTED // WELCOME, COMMANDER")
            StatusMsg.Spectrum = "#00CC66"
            SysIndicator.Spectrum = "#00CC66"
        elif State["attempts"] >= 3:
            StatusMsg.SetText("LOCKOUT ENGAGED // CONTACT STARFLEET COMMAND")
            StatusMsg.Spectrum = Palette.RedAlert[0]
            SysIndicator.Spectrum = Palette.RedAlert[0]
        elif State["attempts"] > 0:
            rem = 3 - State["attempts"]
            StatusMsg.SetText(f"ACCESS DENIED // {rem} ATTEMPTS REMAINING")
            StatusMsg.Spectrum = Palette.RedAlert[0]
            SysIndicator.Spectrum = Palette.RedAlert[0]
        else:
            StatusMsg.SetText(f"CODE LENGTH: {len(c)}/{MAX_CODE}")
            StatusMsg.Spectrum = Palette.Buttons[2]
            SysIndicator.Spectrum = Palette.Buttons[2]

    def OnDigit(d):
        if State["auth"] or State["attempts"] >= 3:
            ActiveAudio.play("denied")
            return
        if len(State["code"]) >= MAX_CODE:
            ActiveAudio.play("denied")
            return
        State["code"] += d
        ActiveAudio.play("click")
        UpdateDisplay()

    def OnClear():
        ActiveAudio.play("click")
        State["code"] = ""
        State["auth"] = False
        State["attempts"] = 0
        UpdateDisplay()

    def OnBackspace():
        if State["auth"]:
            ActiveAudio.play("denied")
            return
        if State["code"]:
            State["code"] = State["code"][:-1]
            ActiveAudio.play("click")
            UpdateDisplay()

    def OnEnter():
        if State["auth"] or not State["code"]:
            ActiveAudio.play("denied")
            return
        if State["code"] == AUTH_CODE:
            State["auth"] = True
            ActiveAudio.play("acknowledge")
            UpdateDisplay()
        else:
            State["attempts"] += 1
            ActiveAudio.play("denied")
            State["code"] = ""
            UpdateDisplay()

    # Ряд 1: 1 2 3
    R1 = Panel(Spectrum=Palette.Background)
    R1.SetHorizontal(0, 0, 0, 0, Spacing=6)
    for d, c in [("1", Palette.Buttons[2]), ("2", Palette.Buttons[0]), ("3", Palette.Buttons[1])]:
        B = LCARSButton(Text=d, Form=LCARSButton.RectType, Width=155, Height=54, FontSize=22, Spectrum=c)
        B.Clicked.Connect(lambda digit=d: OnDigit(digit))
        KeypadBtns.append(B)
        R1.Add(B)
    KeypadPanel.Add(R1)

    # Ряд 2: 4 5 6
    R2 = Panel(Spectrum=Palette.Background)
    R2.SetHorizontal(0, 0, 0, 0, Spacing=6)
    for d, c in [("4", Palette.Buttons[0]), ("5", Palette.Buttons[1]), ("6", Palette.Buttons[2])]:
        B = LCARSButton(Text=d, Form=LCARSButton.RectType, Width=155, Height=54, FontSize=22, Spectrum=c)
        B.Clicked.Connect(lambda digit=d: OnDigit(digit))
        KeypadBtns.append(B)
        R2.Add(B)
    KeypadPanel.Add(R2)

    # Ряд 3: 7 8 9
    R3 = Panel(Spectrum=Palette.Background)
    R3.SetHorizontal(0, 0, 0, 0, Spacing=6)
    for d, c in [("7", Palette.Buttons[1]), ("8", Palette.Buttons[2]), ("9", Palette.Buttons[0])]:
        B = LCARSButton(Text=d, Form=LCARSButton.RectType, Width=155, Height=54, FontSize=22, Spectrum=c)
        B.Clicked.Connect(lambda digit=d: OnDigit(digit))
        KeypadBtns.append(B)
        R3.Add(B)
    KeypadPanel.Add(R3)

    # Ряд 4: CLR 0 BSP
    R4 = Panel(Spectrum=Palette.Background)
    R4.SetHorizontal(0, 0, 0, 0, Spacing=6)

    BtnClr = LCARSButton(Text="CLR", Form=LCARSButton.SoftHalfType, Direction=180,
                         Width=155, Height=54, FontSize=15, Spectrum=Palette.Buttons[3])
    BtnClr.Clicked.Connect(OnClear)
    KeypadBtns.append(BtnClr)
    R4.Add(BtnClr)

    Btn0 = LCARSButton(Text="0", Form=LCARSButton.RectType,
                       Width=155, Height=54, FontSize=22, Spectrum=Palette.Buttons[4])
    Btn0.Clicked.Connect(lambda: OnDigit("0"))
    KeypadBtns.append(Btn0)
    R4.Add(Btn0)

    BtnBsp = LCARSButton(Text="BSP", Form=LCARSButton.SoftHalfType, Direction=0,
                         Width=155, Height=54, FontSize=15, Spectrum=Palette.Buttons[5])
    BtnBsp.Clicked.Connect(OnBackspace)
    KeypadBtns.append(BtnBsp)
    R4.Add(BtnBsp)

    KeypadPanel.Add(R4)
    CenterCol.Add(KeypadPanel, 1)

    # Ряд дій
    ActionRow = Panel(Spectrum=Palette.Background)
    ActionRow.SetHorizontal(0, 0, 0, 0, Spacing=10)

    BtnAbort = LCARSButton(Text="ABORT", Form=LCARSButton.PillHalfType, Direction=180,
                           Width=180, Height=44, FontSize=14, Spectrum=Palette.Buttons[3])
    BtnAbort.Clicked.Connect(OnClear)
    KeypadBtns.append(BtnAbort)
    ActionRow.Add(BtnAbort)

    ActionRow.AddStretch()

    BtnConfirm = LCARSButton(Text="CONFIRM", Form=LCARSButton.PillHalfType, Direction=0,
                             Width=180, Height=44, FontSize=14, Spectrum=Palette.Buttons[4])
    BtnConfirm.Clicked.Connect(OnEnter)
    KeypadBtns.append(BtnConfirm)
    ActionRow.Add(BtnConfirm)

    CenterCol.Add(ActionRow)
    CenterCol.AddStretch()
    Body.Add(CenterCol, 1)

    # ─── ПРАВА: телеметрія + тривога ──────────────────────────────────────
    RightCol = Panel(Spectrum=Palette.Background)
    RightCol.SetVertical(0, 0, 0, 0, Spacing=6)

    RightCol.Add(LCARSLabel(Text="SYSTEM TELEMETRY", FontSize=11, Spectrum=Palette.Buttons[0]))

    IndRow = Panel(Spectrum=Palette.Background)
    IndRow.SetHorizontal(0, 0, 0, 0, Spacing=4)
    IndRow.Add(LCARSIndicator(Form=LCARSIndicator.RectType, Width=65, Height=24, Spectrum="#00CC66"))
    IndRow.Add(LCARSIndicator(Form=LCARSIndicator.SoftType, Width=65, Height=24, Spectrum=Palette.Buttons[2]))
    IndRow.Add(LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=65, Height=24, Spectrum=Palette.Disabled[0]))
    RightCol.Add(IndRow)

    RightCol.Add(LCARSLabel(Text="PWR: ONLINE",  FontSize=10, Spectrum="#00CC66"))
    RightCol.Add(LCARSLabel(Text="NET: STABLE",  FontSize=10, Spectrum=Palette.Buttons[2]))
    RightCol.Add(LCARSLabel(Text="SEC: STANDBY", FontSize=10, Spectrum=Palette.Disabled[0]))

    RightCol.Add(LCARSBar(Form=LCARSBar.RectType, Height=2, Spectrum=Palette.Disabled[1]))

    RightCol.Add(LCARSLabel(Text="ALERT DIRECTIVES", FontSize=11, Spectrum=Palette.Buttons[0]))

    BRed = LCARSButton(Text="RED ALERT", Form=LCARSButton.PillType,
                       Width=210, Height=38, FontSize=13, Spectrum=Palette.RedAlert[0])
    BRed.Clicked.Connect(lambda: SystemTheme.SetSystemState("Red"))
    RightCol.Add(BRed)

    BYel = LCARSButton(Text="YELLOW ALERT", Form=LCARSButton.PillType,
                       Width=210, Height=38, FontSize=13, Spectrum=Palette.YellowAlert[0])
    BYel.Clicked.Connect(lambda: SystemTheme.SetSystemState("Yellow"))
    RightCol.Add(BYel)

    BGrn = LCARSButton(Text="CONDITION GREEN", Form=LCARSButton.PillType,
                       Width=210, Height=38, FontSize=13, Spectrum=Palette.Buttons[0])
    BGrn.Clicked.Connect(lambda: SystemTheme.SetSystemState("Normal"))
    RightCol.Add(BGrn)

    BReset = LCARSButton(Text="RESET CONSOLE", Form=LCARSButton.SoftType,
                         Width=210, Height=36, FontSize=12, Spectrum=Palette.Buttons[3])
    BReset.Clicked.Connect(OnClear)
    RightCol.Add(BReset)

    RightCol.AddStretch()
    Body.Add(RightCol)

    Padd.Add(Body, 1)

    # ═══════════════════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════════════════
    BottomFoot = Footer(Title="PADD SECURITY v5.1 // ISOLINEAR OPTICAL INTERFACE ACTIVE",
                        Spectrum=Palette.Buttons[0])
    Padd.Add(BottomFoot)

    # ═══════════════════════════════════════════════════════════════════════
    # SHOW + ANIMATIONS
    # ═══════════════════════════════════════════════════════════════════════
    Padd.Show()

    # Каскадне розгортання кнопок
    Cascade = Stagger()
    for Btn in KeypadBtns:
        R = Reveal()
        R.StartReveal(Target=Btn, Period=0.25, Direction="Left")
        Cascade.Add(R)
    Cascade.Play(DelayMs=30)

    # Декодування статусу
    Decoder = TextDecode()
    Decoder.Decode(Target=StatusMsg, Text="SYSTEM READY // ENTER ACCESS CODE TO PROCEED", Period=1.4)

    return Padd


LCARS.Launch(PaddAccessInterface)
