# LCARS FRAMEWORK — PADD BUTTONS CATALOG 🖖
# Демонстрація всіх канонічних форм і станів кнопок через інтерфейс PADD.
import sys
import os

# Канонічний бутстрап шляху: корінь проєкту — для запуску з будь-якої теки
Root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if Root not in sys.path:
    sys.path.insert(0, Root)

from lcars.base.type import LCARS
from lcars.base.default import Palette, SystemTheme
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSIndicator
from lcars.base.interface import PADD, Panel, Header, Footer

def Run():
    AppClass = LCARS.Retrieve("Base.Interface.Application")
    app = AppClass.instance() if AppClass and hasattr(AppClass, "instance") else None
    if app is None and AppClass:
        app = AppClass(sys.argv)

    # 1. Створюємо планшет офіцера PADD
    Padd = PADD(Title="LCARS PADD // STARFLEET TACTICAL", Width=1180, Height=760)
    Padd.SetVertical(8, 8, 8, 8, Spacing=6)

    # 2. Шапка планшета
    TopHeader = Header(Title="PERSONAL ACCESS DISPLAY DEVICE // STARFLEET COMMAND", Spectrum=Palette.Buttons[2])
    Padd.Add(TopHeader)

    # 3. Основне горизонтальне тіло планшета
    Body = Panel(Spectrum=Palette.Background)
    Body.SetHorizontal(0, 0, 0, 0, Spacing=10)

    # ─── ЛІВА КОЛОНКА: СИЛОВИЙ КАРКАС ТА РЕЖИМИ ───
    LeftCol = Panel(Spectrum=Palette.Background)
    LeftCol.SetVertical(0, 0, 0, 0, Spacing=6)

    ElbowNav = LCARSElbow(Direction="top-left", Text="TACTICAL", Number="01-TAC", Width=210, Height=60, Spectrum=Palette.Buttons[1])
    LeftCol.Add(ElbowNav)

    for Text, State, Color in [
        ("NAV MATRIX", "normal", Palette.Buttons[2]),
        ("SENSOR GRID", "normal", Palette.Buttons[0]),
        ("SHIELD ARRAY", "normal", Palette.Buttons[1]),
        ("WARP DRIVE", "normal", Palette.Buttons[3]),
        ("STASIS FIELD", "disabled", Palette.Disabled[0]),
    ]:
        Btn = LCARSButton(Text=Text, Form=LCARSButton.PillHalfType, Direction=0, Width=210, Height=38, FontSize=13, Spectrum=Color, State=State)
        LeftCol.Add(Btn)

    LeftCol.AddStretch()
    Body.Add(LeftCol)

    # ─── ЦЕНТРАЛЬНА ЗОНА: КАТАЛОГ УСІХ ФОРМ КНОПОК ───
    CenterCol = Panel(Spectrum=Palette.Background)
    CenterCol.SetVertical(0, 0, 0, 0, Spacing=6)

    LblForms = LCARSLabel(Text="CANONICAL BUTTON GEOMETRIES (OKUDA VECTOR)", FontSize=12, Spectrum=Palette.Buttons[2])
    CenterCol.Add(LblForms)

    GridForms = Panel(Spectrum=Palette.Background)
    GridForms.SetHorizontal(0, 0, 0, 0, Spacing=8)

    # Підколонка 1: Базові форми
    Sub1 = Panel(Spectrum=Palette.Background)
    Sub1.SetVertical(0, 0, 0, 0, Spacing=6)
    for Text, FormVal, DirVal in [
        ("RECT BUTTON", LCARSButton.RectType, 0),
        ("PILL CAPSULE", LCARSButton.PillType, 0),
        ("SOFT CHAMFER", LCARSButton.SoftType, 0),
        ("PILL-HALF EAST", LCARSButton.PillHalfType, 0),
        ("PILL-HALF WEST", LCARSButton.PillHalfType, 180),
        ("SOFT-HALF EAST", LCARSButton.SoftHalfType, 0),
        ("SOFT-HALF WEST", LCARSButton.SoftHalfType, 180),
    ]:
        B = LCARSButton(Text=Text, Form=FormVal, Direction=DirVal, Width=220, Height=36, FontSize=12, Spectrum=Palette.Buttons[2])
        Sub1.Add(B)
    GridForms.Add(Sub1)

    # Підколонка 2: Розщеплені кнопки та індикатори
    Sub2 = Panel(Spectrum=Palette.Background)
    Sub2.SetVertical(0, 0, 0, 0, Spacing=6)

    BSplit1 = LCARSButton(Text="SPLIT SYS", Number="47-A", SplitMode=True, Form=LCARSButton.RectType, Width=220, Height=36, FontSize=12, Spectrum=Palette.Buttons[0])
    Sub2.Add(BSplit1)

    BSplit2 = LCARSButton(Text="AUX EPS", Number="99-B", SplitMode=True, Form=LCARSButton.SoftType, Width=220, Height=36, FontSize=12, Spectrum=Palette.Buttons[1])
    Sub2.Add(BSplit2)

    # Світлові індикатори
    LblInd = LCARSLabel(Text="STATUS INDICATORS", FontSize=11, Spectrum=Palette.Buttons[0])
    Sub2.Add(LblInd)

    IndRow = Panel(Spectrum=Palette.Background)
    IndRow.SetHorizontal(0, 0, 0, 0, Spacing=6)
    Ind1 = LCARSIndicator(Form=LCARSIndicator.RectType, Width=65, Height=32, Spectrum=Palette.Buttons[2])
    Ind2 = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=65, Height=32, Spectrum=Palette.Buttons[0])
    Ind3 = LCARSIndicator(Form=LCARSIndicator.PillHalf, Width=65, Height=32, Spectrum=Palette.Buttons[1])
    IndRow.Add(Ind1)
    IndRow.Add(Ind2)
    IndRow.Add(Ind3)
    Sub2.Add(IndRow)

    GridForms.Add(Sub2)
    CenterCol.Add(GridForms)
    CenterCol.AddStretch()
    Body.Add(CenterCol, 1)

    # ─── ПРАВА КОЛОНКА: СИСТЕМНІ ДІЇ ТА ТРИВОГА ───
    RightCol = Panel(Spectrum=Palette.Background)
    RightCol.SetVertical(0, 0, 0, 0, Spacing=6)

    LblAlert = LCARSLabel(Text="ALERT DIRECTIVES", FontSize=12, Spectrum=Palette.Buttons[0])
    RightCol.Add(LblAlert)

    BRed = LCARSButton(Text="RED ALERT", Form=LCARSButton.PillType, Width=210, Height=40, FontSize=13, Spectrum=Palette.RedAlert[0])
    BRed.Clicked.Connect(lambda: SystemTheme.SetSystemState("Red"))
    RightCol.Add(BRed)

    BYellow = LCARSButton(Text="YELLOW ALERT", Form=LCARSButton.PillType, Width=210, Height=40, FontSize=13, Spectrum=Palette.YellowAlert[0])
    BYellow.Clicked.Connect(lambda: SystemTheme.SetSystemState("Yellow"))
    RightCol.Add(BYellow)

    BGreen = LCARSButton(Text="CONDITION GREEN", Form=LCARSButton.PillType, Width=210, Height=40, FontSize=13, Spectrum=Palette.Buttons[0])
    BGreen.Clicked.Connect(lambda: SystemTheme.SetSystemState("Normal"))
    RightCol.Add(BGreen)

    BReset = LCARSButton(Text="RESET CONSOLE", Form=LCARSButton.SoftType, Width=210, Height=36, FontSize=12, Spectrum=Palette.Buttons[3])
    RightCol.Add(BReset)

    RightCol.AddStretch()
    Body.Add(RightCol)

    Padd.Add(Body, 1)

    # 4. Підвал планшета
    BottomFoot = Footer(Title="PADD HARDWARE v4.7 // ISOLINEAR OPTICAL INTERFACE ACTIVE", Spectrum=Palette.Buttons[0])
    Padd.Add(BottomFoot)

    # Показуємо планшет
    Padd.Show()

    if app and hasattr(app, "exec"):
        sys.exit(app.exec())

if __name__ == "__main__":
    Run()
