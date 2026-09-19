# LCARS FULLSCREEN SECURITY ACCESS TERMINAL
# Standard: Titanium (Zero-Except, Zero Underscores, Strict PascalCase)

from lcars.base.type import LCARS
from lcars.base.interface import Screen, Panel, Header, Footer
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
from lcars.base.animation import TextDecode, Reveal, Stagger, Blink
from lcars.base.default import SystemTheme
from lcars.modules.sound import ActiveAudio

AuthCode = "4721"

def SecurityAccessInterface():
    MainScreen = Screen(Title="LCARS FULLSCREEN SECURITY TERMINAL")
    MainScreen.SetVertical(10, 14, 10, 14, Spacing=8)

    # 1. ВЕРХНІЙ ТАКТИЧНИЙ РЯД
    TopBar = Panel()
    TopBar.SetHorizontal(0, 0, 0, 0, Spacing=8)

    TopElbow = LCARSElbow(Corner="top-left", Text="SECURITY", Number="SEC-47", Width=220, Height=54, Thickness=22, Radius=18)
    TopBar.Add(TopElbow)

    TopLabel = LCARSLabel(Text="SECURITY CLEARANCE TERMINAL // AUTHORIZATION REQUIRED", FontSize=20, Align="left", Height=36)
    TopBar.Add(TopLabel, 1)

    BtnExit = LCARSButton(Text="EXIT FULLSCREEN", Form=LCARSButton.PillHalf, Direction=0, Width=180, Height=36, Sound="click")
    TopBar.Add(BtnExit)

    MainScreen.Add(TopBar)

    # 2. ГОЛОВНИЙ ТРИКОЛОНКОВИЙ БЛОК
    Body = Panel()
    Body.SetHorizontal(0, 0, 0, 0, Spacing=14)

    # ─── ЛІВА КОЛОНКА: НАВІГАЦІЯ ТА АУДИТ ───
    Left = Panel()
    Left.SetVertical(0, 0, 0, 0, Spacing=6)

    LeftElbow = LCARSElbow(Corner="top-left", Text="ACCESS DECK", Number="01-ACC", Width=230, Height=54, Thickness=22, Radius=18)
    Left.Add(LeftElbow)

    for NavTitle in ["ACCESS LOG", "USER MATRIX", "CLEARANCE", "AUDIT TRAIL"]:
        BNav = LCARSButton(
            Text=NavTitle,
            Form=LCARSButton.PillHalfType,
            Direction=0,
            Width=230,
            Height=38,
            Sound="click"
        )
        Left.Add(BNav)

    BLockout = LCARSButton(
        Text="LOCKOUT",
        Form=LCARSButton.PillHalfType,
        Direction=0,
        Width=230,
        Height=38,
        State="disabled"
    )
    Left.Add(BLockout)
    Left.AddStretch(1)

    LeftInd = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=230, Height=22)
    Left.Add(LeftInd)
    Body.Add(Left)

    # ─── ЦЕНТРАЛЬНА КОЛОНКА: КЛАВІАТУРА ТА ДИСПЛЕЙ ───
    Center = Panel()
    Center.SetVertical(0, 0, 0, 0, Spacing=8)

    DisplayCard = Panel()
    DisplayCard.SetVertical(10, 12, 10, 12, Spacing=4)

    PromptMsg = LCARSLabel(Text="ENTER AUTHORIZATION CODE", Height=26)
    DisplayCard.Add(PromptMsg)

    CodeDisplay = LCARSLabel(Text="*", FontSize=36, Align="center", Height=56)
    DisplayCard.Add(CodeDisplay)

    StatusMsg = LCARSLabel(Text="AWAITING INPUT...", Align="center", Height=26)
    DisplayCard.Add(StatusMsg)

    Center.Add(DisplayCard)

    DividerBar = LCARSBar(Height=3)
    Center.Add(DividerBar)

    StateStore = {"Code": "", "Passed": False, "Attempts": 0}
    KeypadBtns = []

    def UpdateDisplay():
        CurCode = StateStore["Code"]
        CodeDisplay.SetText("*" * len(CurCode) if CurCode else "EMPTY")
        if StateStore["Passed"]:
            StatusMsg.SetText("ACCESS GRANTED // COMMAND CONSOLE OPEN")
        elif StateStore["Attempts"] >= 3:
            StatusMsg.SetText("LOCKOUT // CONTACT STARFLEET COMMAND")
        elif StateStore["Attempts"] > 0:
            Remain = 3 - StateStore["Attempts"]
            StatusMsg.SetText(f"DENIED // {Remain} ATTEMPTS REMAINING")
        else:
            StatusMsg.SetText(f"BUFFER: {len(CurCode)} / 8 DIGITS")

    def AddDigit(DigitChar):
        if StateStore["Passed"] or StateStore["Attempts"] >= 3 or len(StateStore["Code"]) >= 8:
            ActiveAudio.play("denied")
            return
        StateStore["Code"] += DigitChar
        ActiveAudio.play("click")
        UpdateDisplay()

    def ClearCode():
        ActiveAudio.play("click")
        StateStore["Code"] = ""
        StateStore["Passed"] = False
        StateStore["Attempts"] = 0
        UpdateDisplay()

    def BackspaceCode():
        if StateStore["Passed"]:
            ActiveAudio.play("denied")
            return
        if StateStore["Code"]:
            StateStore["Code"] = StateStore["Code"][:-1]
            ActiveAudio.play("click")
            UpdateDisplay()

    def SubmitCode():
        if StateStore["Passed"] or not StateStore["Code"]:
            ActiveAudio.play("denied")
            return
        if StateStore["Code"] == AuthCode:
            StateStore["Passed"] = True
            ActiveAudio.play("ack")
            UpdateDisplay()
        else:
            StateStore["Attempts"] += 1
            ActiveAudio.play("denied")
            StateStore["Code"] = ""
            UpdateDisplay()

    KeypadPanel = Panel()
    KeypadPanel.SetVertical(0, 0, 0, 0, Spacing=6)

    NumRows = [
        ("1", "2", "3"),
        ("4", "5", "6"),
        ("7", "8", "9")
    ]

    for RowTuple in NumRows:
        RowPanel = Panel()
        RowPanel.SetHorizontal(0, 0, 0, 0, Spacing=6)
        for DigitStr in RowTuple:
            BNum = LCARSButton(
                Text=DigitStr,
                Form=LCARSButton.RectType,
                Width=160,
                Height=52,
                FontSize=24,
                Sound="click"
            )
            BNum.Clicked.Connect(lambda D=DigitStr: AddDigit(D))
            KeypadBtns.append(BNum)
            RowPanel.Add(BNum)
        KeypadPanel.Add(RowPanel)

    BottomKeyRow = Panel()
    BottomKeyRow.SetHorizontal(0, 0, 0, 0, Spacing=6)

    BtnClr = LCARSButton(
        Text="CLR",
        Form=LCARSButton.SoftHalfType,
        Direction=180,
        Width=160,
        Height=52,
        Sound="click"
    )
    BtnClr.Clicked.Connect(ClearCode)
    KeypadBtns.append(BtnClr)
    BottomKeyRow.Add(BtnClr)

    BtnZero = LCARSButton(
        Text="0",
        Form=LCARSButton.RectType,
        Width=160,
        Height=52,
        FontSize=24,
        Sound="click"
    )
    BtnZero.Clicked.Connect(lambda: AddDigit("0"))
    KeypadBtns.append(BtnZero)
    BottomKeyRow.Add(BtnZero)

    BtnBsp = LCARSButton(
        Text="BSP",
        Form=LCARSButton.SoftHalfType,
        Direction=0,
        Width=160,
        Height=52,
        Sound="click"
    )
    BtnBsp.Clicked.Connect(BackspaceCode)
    KeypadBtns.append(BtnBsp)
    BottomKeyRow.Add(BtnBsp)

    KeypadPanel.Add(BottomKeyRow)
    Center.Add(KeypadPanel, 1)

    ActionRow = Panel()
    ActionRow.SetHorizontal(0, 0, 0, 0, Spacing=10)

    BtnAbort = LCARSButton(
        Text="ABORT",
        Form=LCARSButton.PillHalfType,
        Direction=180,
        Width=190,
        Height=46,
        Sound="click"
    )
    BtnAbort.Clicked.Connect(ClearCode)
    KeypadBtns.append(BtnAbort)
    ActionRow.Add(BtnAbort)
    ActionRow.AddStretch(1)

    BtnConfirm = LCARSButton(
        Text="CONFIRM",
        Form=LCARSButton.PillHalfType,
        Direction=0,
        Width=190,
        Height=46,
        Sound="ack"
    )
    BtnConfirm.Clicked.Connect(SubmitCode)
    KeypadBtns.append(BtnConfirm)
    ActionRow.Add(BtnConfirm)

    Center.Add(ActionRow)
    Center.AddStretch(1)
    Body.Add(Center, 1)

    # ─── ПРАВА КОЛОНКА: ДИРЕКТИВИ ТА ТЕЛЕМЕТРІЯ ───
    Right = Panel()
    Right.SetVertical(0, 0, 0, 0, Spacing=6)

    LblTelemetry = LCARSLabel(Text="SECURITY TELEMETRY", Height=24)
    Right.Add(LblTelemetry)

    IndicatorRow = Panel()
    IndicatorRow.SetHorizontal(0, 0, 0, 0, Spacing=4)
    IndPwr = LCARSIndicator(Form=LCARSIndicator.RectType, Width=72, Height=26)
    IndNet = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=72, Height=26)
    IndSec = LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=72, Height=26)
    IndicatorRow.Add(IndPwr)
    IndicatorRow.Add(IndNet)
    IndicatorRow.Add(IndSec)
    Right.Add(IndicatorRow)

    LblPwr = LCARSLabel(Text="POWER GRID: ONLINE", Height=22)
    LblNet = LCARSLabel(Text="ODN NETWORK: STABLE", Height=22)
    LblSec = LCARSLabel(Text="SECURITY BUS: ACTIVE", Height=22)
    Right.Add(LblPwr)
    Right.Add(LblNet)
    Right.Add(LblSec)

    RightBar = LCARSBar(Height=3)
    Right.Add(RightBar)

    LblAlertDirectives = LCARSLabel(Text="ALERT DIRECTIVES", Height=24)
    Right.Add(LblAlertDirectives)

    # Червона та жовта тривоги передаються у стані alert і yellow зі своїми динамічними циклами
    BtnRed = LCARSButton(
        Text="RED ALERT",
        Form=LCARSButton.PillType,
        Width=230,
        Height=40,
        State="alert",
        Sound="alertred"
    )
    def SetRedState():
        SystemTheme.SetSystemState("Red")
        StatusMsg.SetText("RED ALERT ACTIVATED")
    BtnRed.Clicked.Connect(SetRedState)
    Right.Add(BtnRed)

    BtnYellow = LCARSButton(
        Text="YELLOW ALERT",
        Form=LCARSButton.PillType,
        Width=230,
        Height=40,
        State="yellow",
        Sound="alertyellow"
    )
    def SetYellowState():
        SystemTheme.SetSystemState("Yellow")
        StatusMsg.SetText("YELLOW ALERT ACTIVATED")
    BtnYellow.Clicked.Connect(SetYellowState)
    Right.Add(BtnYellow)

    BtnGreen = LCARSButton(
        Text="CONDITION GREEN",
        Form=LCARSButton.PillType,
        Width=230,
        Height=40,
        State="normal",
        Sound="ack"
    )
    def SetGreenState():
        SystemTheme.SetSystemState("Normal")
        StatusMsg.SetText("CONDITION GREEN RESTORED")
    BtnGreen.Clicked.Connect(SetGreenState)
    Right.Add(BtnGreen)

    BtnReset = LCARSButton(
        Text="RESET CONSOLE",
        Form=LCARSButton.SoftType,
        Width=230,
        Height=38,
        Sound="click"
    )
    BtnReset.Clicked.Connect(ClearCode)
    Right.Add(BtnReset)

    Right.AddStretch(1)
    Body.Add(Right)

    MainScreen.Add(Body, 1)

    # 3. ПІДВАЛ ЕКРАНА
    FootBar = Panel()
    FootBar.SetHorizontal(0, 0, 0, 0, Spacing=8)

    FootLabel = LCARSLabel(Text="LCARS SECURITY SYSTEM v5.1 // BIOMETRIC & CODE CONDUIT OPERATIONAL", Height=32)
    FootBar.Add(FootLabel, 1)

    MainScreen.Add(FootBar)

    # 4. ДІЇ ТА АНІМАЦІЯ
    def ExitTerminal():
        HostSurface = MainScreen.GetSurface()
        if hasattr(HostSurface, "close"):
            HostSurface.close()

    BtnExit.Clicked.Connect(ExitTerminal)

    Cascade = Stagger()
    for BKey in KeypadBtns:
        Rev = Reveal()
        Rev.StartReveal(Target=BKey, Period=0.25, Direction="Left")
        Cascade.Add(Rev)
    Cascade.Play(DelayMs=30)

    Decoder = TextDecode()
    Decoder.Decode(Target=StatusMsg, Text="ENTER 4-DIGIT SECURITY PIN", Period=1.2)

    Blink(Target=IndPwr, Period=0.6, Loop=True).Start()
    Blink(Target=IndNet, Period=0.8, Loop=True).Start()
    Blink(Target=IndSec, Period=1.0, Loop=True).Start()

    MainScreen.Show()
    return MainScreen

LCARS.Launch(SecurityAccessInterface)
