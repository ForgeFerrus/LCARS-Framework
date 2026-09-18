# LCARS FRAMEWORK — PADD ACCESS PANEL v2
# Функціональний планшет офіцера з клавіатурою, анімаціями та системою авторизації.
# Сценарій:
# 1. PADD завантажується з каскадною анімацією розгортання (Stagger + Reveal).
# 2. Термінальний друк (Typewriter) інформує про готовність системи.
# 3. Користувач вводить код безпеки через функціональну клавіатуру (0-9).
# 4. Введення супроводжується анімацією натискання кнопок та блиманням індикатора.
# 5. Підтвердження коду активує повідомлення про успішну/невдалу авторизацію.
import sys
import os

Root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if Root not in sys.path:
    sys.path.insert(0, Root)

from lcars.base.type import LCARS
from lcars.base.default import Palette, SystemTheme
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator, LCARSBar
from lcars.base.interface import PADD, Panel, Header, Footer
from lcars.base.animation import TextDecode, Typewriter, Reveal, Stagger

# ============================================================================
# КОНСТАНТИ ДОДАТКУ
# ============================================================================
AUTH_CODE = "4721"
MAX_CODE_LENGTH = 8

# Кольори для різних станів індикатора
COLOR_READY = Palette.Buttons[2]
COLOR_ACTIVE = Palette.Buttons[4]
COLOR_SUCCESS = "#00CC66"
COLOR_ERROR = Palette.RedAlert[0]
COLOR_DISABLED = Palette.Disabled[0]

def Run():
    AppClass = LCARS.Retrieve("Base.Interface.Application")
    app = AppClass.instance() if AppClass and hasattr(AppClass, "instance") else None
    if app is None and AppClass:
        app = AppClass(sys.argv)

    # ========================================================================
    # 1. СТВОРЕННЯ ПЛАНШЕТА PADD
    # ========================================================================
    Padd = PADD(Title="LCARS PADD // STARFLEET SECURITY ACCESS", Width=1080, Height=720)
    Padd.SetVertical(8, 8, 8, 8, Spacing=6)

    # ========================================================================
    # 2. ШАПКА ПЛАНШЕТА
    # ========================================================================
    TopHeader = Header(Title="SECURITY ACCESS TERMINAL // AUTHORIZATION REQUIRED", Spectrum=Palette.Buttons[2])
    Padd.Add(TopHeader)

    # ========================================================================
    # 3. ОСНОВНЕ ТІЛО ПЛАНШЕТА
    # ========================================================================
    Body = Panel(Spectrum=Palette.Background)
    Body.SetHorizontal(0, 0, 0, 0, Spacing=12)

    # ─── ЛІВА КОЛОНКА: НАВІГАЦІЯ ТА СИСТЕМНІ ФУНКЦІЇ ───
    LeftCol = Panel(Spectrum=Palette.Background)
    LeftCol.SetVertical(0, 0, 0, 0, Spacing=6)

    ElbowNav = LCARSElbow(Direction="top-left", Text="SECURITY", Number="01-SEC", Width=200, Height=56, Spectrum=Palette.Buttons[1])
    LeftCol.Add(ElbowNav)

    NavButtons = []
    for Text, Color in [
        ("ACCESS LOG", Palette.Buttons[2]),
        ("USER MATRIX", Palette.Buttons[0]),
        ("Clearance", Palette.Buttons[1]),
        ("Audit Trail", Palette.Buttons[3]),
        ("LOCKOUT", COLOR_DISABLED),
    ]:
        Btn = LCARSButton(Text=Text, Form=LCARSButton.PillHalfType, Direction=0, Width=200, Height=36, FontSize=12, Spectrum=Color)
        NavButtons.append(Btn)
        LeftCol.Add(Btn)

    LeftCol.AddStretch()

    # Індикатор статусу системи
    StatusRow = Panel(Spectrum=Palette.Background)
    StatusRow.SetHorizontal(0, 0, 0, 0, Spacing=6)

    SystemIndicator = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=200, Height=20, Spectrum=COLOR_READY)
    StatusRow.Add(SystemIndicator)
    LeftCol.Add(StatusRow)

    Body.Add(LeftCol)

    # ─── ЦЕНТРАЛЬНА ЗОНА: ДИСПЛЕЙ КОДУ ТА КЛАВІАТУРА ───
    CenterCol = Panel(Spectrum=Palette.Background)
    CenterCol.SetVertical(0, 0, 0, 0, Spacing=10)

    # Дисплей введеного коду
    DisplayPanel = Panel(Spectrum=Palette.Background)
    DisplayPanel.SetVertical(0, 0, 0, 0, Spacing=4)

    DisplayTitle = LCARSLabel(Text="ENTER ACCESS CODE", FontSize=14, Spectrum=Palette.Buttons[2], Width=500, Height=28)
    DisplayPanel.Add(DisplayTitle)

    CodeDisplay = LCARSLabel(Text="_", FontSize=32, Align="center", Width=500, Height=56, Spectrum=COLOR_ACTIVE)
    DisplayPanel.Add(CodeDisplay)

    StatusMessage = LCARSLabel(Text="AWAITING INPUT...", FontSize=12, Align="center", Width=500, Height=22, Spectrum=COLOR_READY)
    DisplayPanel.Add(StatusMessage)

    CenterCol.Add(DisplayPanel)

    # Розділювач
    Divider = LCARSBar(Form=LCARSBar.PillHalfType, Direction=0, Width=500, Height=4, Spectrum=Palette.Buttons[2])
    CenterCol.Add(Divider)

    # ─── КЛАВІАТУРА (3x4 матриця + ряд функцій) ───
    KeypadGrid = Panel(Spectrum=Palette.Background)
    KeypadGrid.SetVertical(0, 0, 0, 0, Spacing=6)

    # Стан введення коду
    CodeState = {"code": "", "authenticated": False, "attempts": 0}

    # Внутрішня функція оновлення дисплея
    def UpdateDisplay():
        CurrentCode = CodeState["code"]
        if not CurrentCode:
            CodeDisplay.SetText("_")
        else:
            Masked = "*" * len(CurrentCode)
            CodeDisplay.SetText(Masked)

        if CodeState["authenticated"]:
            StatusMessage.SetText("ACCESS GRANTED")
            StatusMessage.Spectrum = COLOR_SUCCESS
            SystemIndicator.Spectrum = COLOR_SUCCESS
        elif CodeState["attempts"] > 0 and not CodeState["authenticated"]:
            Remaining = 3 - CodeState["attempts"]
            if Remaining > 0:
                StatusMessage.SetText(f"ACCESS DENIED // {Remaining} ATTEMPTS REMAINING")
            else:
                StatusMessage.SetText("LOCKOUT ENGAGED // CONTACT STARFLEET COMMAND")
            StatusMessage.Spectrum = COLOR_ERROR
            SystemIndicator.Spectrum = COLOR_ERROR
        else:
            StatusMessage.SetText(f"CODE LENGTH: {len(CurrentCode)}/{MAX_CODE_LENGTH}")
            StatusMessage.Spectrum = COLOR_READY
            SystemIndicator.Spectrum = COLOR_READY

    # Функція натискання цифри
    def OnDigitPress(Digit):
        if CodeState["authenticated"]:
            return
        if CodeState["attempts"] >= 3:
            return
        if len(CodeState["code"]) >= MAX_CODE_LENGTH:
            return
        CodeState["code"] += str(Digit)
        UpdateDisplay()

    # Функція очищення
    def OnClear():
        CodeState["code"] = ""
        CodeState["authenticated"] = False
        CodeState["attempts"] = 0
        UpdateDisplay()

    # Функція стирання останнього символу
    def OnBackspace():
        if CodeState["authenticated"]:
            return
        if CodeState["code"]:
            CodeState["code"] = CodeState["code"][:-1]
            UpdateDisplay()

    # Функція підтвердження
    def OnEnter():
        if CodeState["authenticated"]:
            return
        if not CodeState["code"]:
            return
        if CodeState["code"] == AUTH_CODE:
            CodeState["authenticated"] = True
            UpdateDisplay()
            OnAccessGranted()
        else:
            CodeState["attempts"] += 1
            if CodeState["attempts"] >= 3:
                StatusMessage.SetText("LOCKOUT ENGAGED // CONTACT STARFLEET COMMAND")
            UpdateDisplay()
            OnAccessDenied()

    def OnAccessGranted():
        SystemIndicator.Spectrum = COLOR_SUCCESS
        SystemIndicator.Refresh()

    def OnAccessDenied():
        CodeState["code"] = ""
        UpdateDisplay()

    # Ряд 1: 1 2 3
    Row1 = Panel(Spectrum=Palette.Background)
    Row1.SetHorizontal(0, 0, 0, 0, Spacing=6)
    KeypadBtns = []
    for Digit in ["1", "2", "3"]:
        Btn = LCARSButton(
            Text=Digit, Form=LCARSButton.RectType, Width=150, Height=52, FontSize=20,
            Spectrum=Palette.Buttons[2]
        )
        Btn.DigitValue = Digit
        Btn.Clicked.Connect(lambda d=Digit: OnDigitPress(d))
        KeypadBtns.append(Btn)
        Row1.Add(Btn)
    KeypadGrid.Add(Row1)

    # Ряд 2: 4 5 6
    Row2 = Panel(Spectrum=Palette.Background)
    Row2.SetHorizontal(0, 0, 0, 0, Spacing=6)
    for Digit in ["4", "5", "6"]:
        Btn = LCARSButton(
            Text=Digit, Form=LCARSButton.RectType, Width=150, Height=52, FontSize=20,
            Spectrum=Palette.Buttons[0]
        )
        Btn.Clicked.Connect(lambda d=Digit: OnDigitPress(d))
        KeypadBtns.append(Btn)
        Row2.Add(Btn)
    KeypadGrid.Add(Row2)

    # Ряд 3: 7 8 9
    Row3 = Panel(Spectrum=Palette.Background)
    Row3.SetHorizontal(0, 0, 0, 0, Spacing=6)
    for Digit in ["7", "8", "9"]:
        Btn = LCARSButton(
            Text=Digit, Form=LCARSButton.RectType, Width=150, Height=52, FontSize=20,
            Spectrum=Palette.Buttons[1]
        )
        Btn.Clicked.Connect(lambda d=Digit: OnDigitPress(d))
        KeypadBtns.append(Btn)
        Row3.Add(Btn)
    KeypadGrid.Add(Row3)

    # Ряд 4: CLR 0 BSP
    Row4 = Panel(Spectrum=Palette.Background)
    Row4.SetHorizontal(0, 0, 0, 0, Spacing=6)

    BtnClear = LCARSButton(
        Text="CLR", Form=LCARSButton.SoftHalfType, Direction=180, Width=150, Height=52, FontSize=16,
        Spectrum=Palette.Buttons[3]
    )
    BtnClear.Clicked.Connect(OnClear)
    KeypadBtns.append(BtnClear)
    Row4.Add(BtnClear)

    BtnZero = LCARSButton(
        Text="0", Form=LCARSButton.RectType, Width=150, Height=52, FontSize=20,
        Spectrum=Palette.Buttons[4]
    )
    BtnZero.Clicked.Connect(lambda: OnDigitPress("0"))
    KeypadBtns.append(BtnZero)
    Row4.Add(BtnZero)

    BtnBack = LCARSButton(
        Text="BSP", Form=LCARSButton.SoftHalfType, Direction=0, Width=150, Height=52, FontSize=16,
        Spectrum=Palette.Buttons[5]
    )
    BtnBack.Clicked.Connect(OnBackspace)
    KeypadBtns.append(BtnBack)
    Row4.Add(BtnBack)

    KeypadGrid.Add(Row4)

    CenterCol.Add(KeypadGrid)

    # Ряд дій під клавіатурою
    ActionRow = Panel(Spectrum=Palette.Background)
    ActionRow.SetHorizontal(0, 0, 0, 0, Spacing=8)

    BtnAbort = LCARSButton(
        Text="ABORT", Form=LCARSButton.PillHalfType, Direction=180, Width=180, Height=40, FontSize=14,
        Spectrum=Palette.Buttons[3]
    )
    BtnAbort.Clicked.Connect(OnClear)
    ActionRow.Add(BtnAbort)

    ActionRow.AddStretch()

    BtnConfirm = LCARSButton(
        Text="CONFIRM", Form=LCARSButton.PillHalfType, Direction=0, Width=180, Height=40, FontSize=14,
        Spectrum=Palette.Buttons[4]
    )
    BtnConfirm.Clicked.Connect(OnEnter)
    ActionRow.Add(BtnConfirm)

    CenterCol.Add(ActionRow)
    CenterCol.AddStretch()
    Body.Add(CenterCol, 1)

    # ─── ПРАВА КОЛОНКА: ТЕЛЕМЕТРІЯ ТА ТРИВОГА ───
    RightCol = Panel(Spectrum=Palette.Background)
    RightCol.SetVertical(0, 0, 0, 0, Spacing=6)

    LblTelemetry = LCARSLabel(Text="SYSTEM TELEMETRY", FontSize=12, Spectrum=Palette.Buttons[0])
    RightCol.Add(LblTelemetry)

    # Індикатори статусу
    IndRow1 = Panel(Spectrum=Palette.Background)
    IndRow1.SetHorizontal(0, 0, 0, 0, Spacing=4)
    IndPower = LCARSIndicator(Form=LCARSIndicator.RectType, Width=60, Height=28, Spectrum=COLOR_SUCCESS)
    IndNetwork = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=60, Height=28, Spectrum=COLOR_READY)
    IndSecurity = LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=60, Height=28, Spectrum=COLOR_DISABLED)
    IndRow1.Add(IndPower)
    IndRow1.Add(IndNetwork)
    IndRow1.Add(IndSecurity)
    RightCol.Add(IndRow1)

    LblPower = LCARSLabel(Text="PWR: ONLINE", FontSize=11, Spectrum=Palette.Buttons[2])
    RightCol.Add(LblPower)
    LblNet = LCARSLabel(Text="NET: STABLE", FontSize=11, Spectrum=Palette.Buttons[0])
    RightCol.Add(LblNet)
    LblSec = LCARSLabel(Text="SEC: STANDBY", FontSize=11, Spectrum=COLOR_DISABLED)
    RightCol.Add(LblSec)

    # Кнопки тривоги
    LblAlert = LCARSLabel(Text="ALERT DIRECTIVES", FontSize=12, Spectrum=Palette.Buttons[0])
    RightCol.Add(LblAlert)

    BRed = LCARSButton(
        Text="RED ALERT", Form=LCARSButton.PillType, Width=200, Height=38, FontSize=13,
        Spectrum=Palette.RedAlert[0]
    )
    BRed.Clicked.Connect(lambda: SystemTheme.SetSystemState("Red"))
    RightCol.Add(BRed)

    BYellow = LCARSButton(
        Text="YELLOW ALERT", Form=LCARSButton.PillType, Width=200, Height=38, FontSize=13,
        Spectrum=Palette.YellowAlert[0]
    )
    BYellow.Clicked.Connect(lambda: SystemTheme.SetSystemState("Yellow"))
    RightCol.Add(BYellow)

    BGreen = LCARSButton(
        Text="CONDITION GREEN", Form=LCARSButton.PillType, Width=200, Height=38, FontSize=13,
        Spectrum=Palette.Buttons[0]
    )
    BGreen.Clicked.Connect(lambda: SystemTheme.SetSystemState("Normal"))
    RightCol.Add(BGreen)

    BReset = LCARSButton(
        Text="RESET CONSOLE", Form=LCARSButton.SoftType, Width=200, Height=36, FontSize=12,
        Spectrum=Palette.Buttons[3]
    )
    BReset.Clicked.Connect(OnClear)
    RightCol.Add(BReset)

    RightCol.AddStretch()
    Body.Add(RightCol)

    Padd.Add(Body, 1)

    # ========================================================================
    # 4. ПІДВАЛ ПЛАНШЕТА
    # ========================================================================
    BottomFoot = Footer(Title="PADD SECURITY v5.1 // ISOLINEAR OPTICAL INTERFACE ACTIVE", Spectrum=Palette.Buttons[0])
    Padd.Add(BottomFoot)

    # ========================================================================
    # 5. АНІМАЦІЙНИЙ КОНВЕЄР ІНІЦІАЛІЗАЦІЇ
    # ========================================================================
    Decoder = TextDecode()
    Writer = Typewriter()
    CascadeReveal = Stagger()

    # Каскадне розгортання кнопок клавіатури
    for Btn in KeypadBtns:
        Revealer = Reveal()
        Revealer.StartReveal(Target=Btn, Period=0.25, Direction="Left")
        CascadeReveal.Add(Revealer)

    # Каскадне розгортання навігаційних кнопок
    for Btn in NavButtons:
        Revealer = Reveal()
        Revealer.StartReveal(Target=Btn, Period=0.20, Direction="Right")
        CascadeReveal.Add(Revealer)

    # Запуск каскадної анімації при показі PADD
    def OnPaddReady():
        CascadeReveal.Play(DelayMs=35)

    # Декодування статусного повідомлення при старті
    def StartInitialization():
        Decoder.Decode(
            Target=StatusMessage,
            Text="SYSTEM READY // ENTER ACCESS CODE TO PROCEED",
            Period=1.5,
            OnFinish=OnPaddReady
        )

    # ========================================================================
    # 6. ПОКАЗ ПЛАНШЕТА ТА ЗАПУСК
    # ========================================================================
    Padd.Show()

    # Запускаємо анімацію ініціалізації
    StartInitialization()

    if app and hasattr(app, "exec"):
        sys.exit(app.exec())

if __name__ == "__main__":
    Run()
