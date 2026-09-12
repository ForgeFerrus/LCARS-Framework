# ◤ TITANIUM LCARS INTERACTIVE DESIGNER & COMPONENT CONSTRUCTOR 🖖
# ОПИС: Інтерактивний дизайнер та конструктор фізичних об'єктів LCARS за категоріями з режимом Edit Mode.
# СТАНДАРТ: Titanium (Zero-Except, Zero-Underscores, Strict PascalCase, Pure LCARS Classes).
# ФУНКЦІОНАЛ: 
#   1. Бібліотека за категоріями (Buttons, Directional Caps, L-Frames, Indicators, Composites, Alerts).
#   2. Інтерактивне полотно (Canvas) із вибором та фокусом активного елемента.
#   3. Edit Mode / Конструктор: регулювання ширини (W-/W+), висоти (H-/H+), зміна форми, стану, дублювання та видалення.
#   4. Паспорт об'єкта та генерація коду конструктора в реальному часі.

from __future__ import annotations

from lcars.base.type import LCARS
from lcars.base.interface import PADD
from lcars.base.component import (
    LCARSButton, LCARSLabel, LCARSElbow, LCARSBar,
    LCARSIndicator, LCARSDataBlock
)


class DesignerWorkbench:
    def __init__(self, Title="LCARS INTERACTIVE DESIGNER // COMPONENT CONSTRUCTOR", Width=1420, Height=890):
        self.App = LCARS.Application.instance()
        if self.App is None:
            Argv = getattr(LCARS.System.Core, "argv", []) if hasattr(LCARS.System, "Core") else []
            self.App = LCARS.Application(Argv)

        self.Padd = PADD(Title=Title, Width=Width, Height=Height)
        self.CanvasItems = []
        self.ActiveItem = None
        self.ActiveIndex = 0
        self.CurrentCategory = "BUTTONS"

        self.Build()

        # Автоматичний таймер динамічного циклу кольорів LCARS (1.8с)
        self.Timer = LCARS.Timer()
        self.Timer.setInterval(1800)
        self.Timer.timeout.connect(self.OnCycleTick)
        self.Timer.start()

    def OnCycleTick(self):
        if hasattr(self.Padd, "update"):
            self.Padd.update()
        if hasattr(self.Padd, "widget") and hasattr(self.Padd.widget, "update"):
            self.Padd.widget.update()

    def Build(self):
        MainContainer = LCARS.Widget()
        MainLayout = LCARS.Horizontal(MainContainer)
        MainLayout.setContentsMargins(12, 12, 12, 12)
        MainLayout.setSpacing(16)

        # ─────────────────────────────────────────────────────────────────────
        # 1. ЛІВА ПАНЕЛЬ: БІБЛІОТЕКА КАТЕГОРІЙ ТА ШВИДКИЙ КОНСТРУКТОР
        # ─────────────────────────────────────────────────────────────────────
        SidebarContainer = LCARS.Widget()
        SidebarLayout = LCARS.Vertical(SidebarContainer)
        SidebarLayout.setContentsMargins(0, 0, 0, 0)
        SidebarLayout.setSpacing(6)

        SidebarHeader = LCARSLabel(Text="OBJECT CATEGORIES", FontSize=13)
        SidebarLayout.addWidget(SidebarHeader.widget)

        Categories = [
            ("CANONICAL BUTTONS", "01-BTN", self.LoadButtonsCategory),
            ("DIRECTIONAL CAPS", "02-CAP", self.LoadCapsCategory),
            ("L-FRAME ELBOWS", "03-ELB", self.LoadElbowsCategory),
            ("STATUS INDICATORS", "04-IND", self.LoadIndicatorsCategory),
            ("COMPOSITE ASSEMBLIES", "05-CMP", self.LoadCompositesCategory),
            ("SYSTEM ALERTS", "06-ALT", self.LoadAlertsCategory),
        ]

        for Text, Number, Callback in Categories:
            CategoryBtn = LCARSButton(Text=Text, Form=LCARSButton.PillHalf, Direction=180, Number=Number, Height=38, FontSize=13)
            # Підключаємо сигнал натискання через сигнал або кастомний хук
            CategoryBtn.OnClickAction = Callback
            SidebarLayout.addWidget(CategoryBtn.widget)

        SidebarLayout.addSpacing(14)
        AddHeader = LCARSLabel(Text="SPAWN NEW OBJECT", FontSize=12)
        SidebarLayout.addWidget(AddHeader.widget)

        SpawnGridWidget = LCARS.Widget()
        SpawnGrid = LCARS.Grid(SpawnGridWidget)
        SpawnGrid.setContentsMargins(0, 0, 0, 0)
        SpawnGrid.setHorizontalSpacing(4)
        SpawnGrid.setVerticalSpacing(4)

        SpawnPill = LCARSButton(Text="+ PILL", Form=LCARSButton.Pill, Number="ADD", Height=34, FontSize=11)
        SpawnPill.OnClickAction = lambda: self.SpawnObject("PILL")
        SpawnRect = LCARSButton(Text="+ RECT", Form=LCARSButton.Rect, Number="ADD", Height=34, FontSize=11)
        SpawnRect.OnClickAction = lambda: self.SpawnObject("RECT")
        SpawnSoft = LCARSButton(Text="+ SOFT", Form=LCARSButton.Soft, Number="ADD", Height=34, FontSize=11)
        SpawnSoft.OnClickAction = lambda: self.SpawnObject("SOFT")
        SpawnElbow = LCARSButton(Text="+ ELBOW", Form=LCARSButton.PillHalf, Direction=0, Number="ADD", Height=34, FontSize=11)
        SpawnElbow.OnClickAction = lambda: self.SpawnObject("ELBOW")

        SpawnGrid.addWidget(SpawnPill.widget, 0, 0)
        SpawnGrid.addWidget(SpawnRect.widget, 0, 1)
        SpawnGrid.addWidget(SpawnSoft.widget, 1, 0)
        SpawnGrid.addWidget(SpawnElbow.widget, 1, 1)
        SidebarLayout.addWidget(SpawnGridWidget)

        SidebarLayout.addStretch()

        CountLabel = LCARSLabel(Text="ODN MATRIX // ONLINE", FontSize=10)
        SidebarLayout.addWidget(CountLabel.widget)
        MainLayout.addWidget(SidebarContainer, 1)

        # ─────────────────────────────────────────────────────────────────────
        # 2. ЦЕНТРАЛЬНЕ ПОЛОТНО (INTERACTIVE LIVE CANVAS)
        # ─────────────────────────────────────────────────────────────────────
        self.CanvasContainer = LCARS.Widget()
        self.CanvasLayout = LCARS.Vertical(self.CanvasContainer)
        self.CanvasLayout.setContentsMargins(0, 0, 0, 0)
        self.CanvasLayout.setSpacing(10)

        # Рамковий заголовок полотна
        TopFrameRow = LCARS.Widget()
        TopFrameLayout = LCARS.Horizontal(TopFrameRow)
        TopFrameLayout.setContentsMargins(0, 0, 0, 0)
        TopFrameLayout.setSpacing(8)

        self.CanvasHeaderLabel = LCARSLabel(Text="CANVAS // CATEGORY: CANONICAL BUTTONS", FontSize=14)
        TopBar = LCARSBar(Height=14, Width=320)
        TopElbow = LCARSElbow(Direction="top-right", Text="ACTIVE ODN", Number="47-CANV", Width=220, Height=36, Thickness=16, Radius=16)

        TopFrameLayout.addWidget(self.CanvasHeaderLabel.widget)
        TopFrameLayout.addWidget(TopBar.widget, 1)
        TopFrameLayout.addWidget(TopElbow.widget)
        self.CanvasLayout.addWidget(TopFrameRow)

        # Зона монтування об'єктів полотна
        self.CanvasContentWidget = LCARS.Widget()
        self.CanvasContentLayout = LCARS.Vertical(self.CanvasContentWidget)
        self.CanvasContentLayout.setContentsMargins(0, 4, 0, 4)
        self.CanvasContentLayout.setSpacing(10)
        self.CanvasLayout.addWidget(self.CanvasContentWidget, 1)

        MainLayout.addWidget(self.CanvasContainer, 3)

        # ─────────────────────────────────────────────────────────────────────
        # 3. ПРАВА ПАНЕЛЬ: EDIT MODE ТА КОНСТРУКТОР ВЛАСТИВОСТЕЙ
        # ─────────────────────────────────────────────────────────────────────
        InspectorContainer = LCARS.Widget()
        InspectorLayout = LCARS.Vertical(InspectorContainer)
        InspectorLayout.setContentsMargins(0, 0, 0, 0)
        InspectorLayout.setSpacing(8)

        InspectorHeader = LCARSLabel(Text="OBJECT INSPECTOR // PASSPORT", FontSize=13)
        InspectorLayout.addWidget(InspectorHeader.widget)

        self.PassportBlock = LCARSDataBlock(
            Title="PROPERTIES // ODN TELEMETRY",
            Data={
                "CLASS": "LCARSButton",
                "FORM": "PILL // WARP",
                "LABEL": "WARP ENGAGE",
                "CODE": "47-1001",
                "STATE": "NORMAL",
                "WIDTH": "175 PX",
                "HEIGHT": "40 PX"
            },
            Width=270,
            Height=150,
            FontSize=12
        )
        InspectorLayout.addWidget(self.PassportBlock.widget)

        InspectorLayout.addSpacing(6)
        EditModeHeader = LCARSLabel(Text="EDIT MODE // TRANSFORM MATRIX", FontSize=12)
        InspectorLayout.addWidget(EditModeHeader.widget)

        # Регулятор ширини: W- / W+
        WidthRow = LCARS.Widget()
        WidthRowLayout = LCARS.Horizontal(WidthRow)
        WidthRowLayout.setContentsMargins(0, 0, 0, 0)
        WidthRowLayout.setSpacing(4)
        BtnWidthMinus = LCARSButton(Text="[ W - ]", Form=LCARSButton.SoftHalf, Direction=180, Number="W-", Height=34, FontSize=12)
        BtnWidthMinus.OnClickAction = lambda: self.AdjustActiveDimensions(DeltaW=-15, DeltaH=0)
        BtnWidthPlus = LCARSButton(Text="[ W + ]", Form=LCARSButton.SoftHalf, Direction=0, Number="W+", Height=34, FontSize=12)
        BtnWidthPlus.OnClickAction = lambda: self.AdjustActiveDimensions(DeltaW=15, DeltaH=0)
        WidthRowLayout.addWidget(BtnWidthMinus.widget, 1)
        WidthRowLayout.addWidget(BtnWidthPlus.widget, 1)
        InspectorLayout.addWidget(WidthRow)

        # Регулятор висоти: H- / H+
        HeightRow = LCARS.Widget()
        HeightRowLayout = LCARS.Horizontal(HeightRow)
        HeightRowLayout.setContentsMargins(0, 0, 0, 0)
        HeightRowLayout.setSpacing(4)
        BtnHeightMinus = LCARSButton(Text="[ H - ]", Form=LCARSButton.SoftHalf, Direction=180, Number="H-", Height=34, FontSize=12)
        BtnHeightMinus.OnClickAction = lambda: self.AdjustActiveDimensions(DeltaW=0, DeltaH=-4)
        BtnHeightPlus = LCARSButton(Text="[ H + ]", Form=LCARSButton.SoftHalf, Direction=0, Number="H+", Height=34, FontSize=12)
        BtnHeightPlus.OnClickAction = lambda: self.AdjustActiveDimensions(DeltaW=0, DeltaH=4)
        HeightRowLayout.addWidget(BtnHeightMinus.widget, 1)
        HeightRowLayout.addWidget(BtnHeightPlus.widget, 1)
        InspectorLayout.addWidget(HeightRow)

        # Перемикачі форми та стану
        TransformRow = LCARS.Widget()
        TransformRowLayout = LCARS.Horizontal(TransformRow)
        TransformRowLayout.setContentsMargins(0, 0, 0, 0)
        TransformRowLayout.setSpacing(4)
        BtnCycleForm = LCARSButton(Text="FORM CYCLE", Form=LCARSButton.Rect, Number="FORM", Height=34, FontSize=11)
        BtnCycleForm.OnClickAction = self.CycleActiveForm
        BtnCycleState = LCARSButton(Text="STATE CYCLE", Form=LCARSButton.Rect, Number="STATE", Height=34, FontSize=11)
        BtnCycleState.OnClickAction = self.CycleActiveState
        TransformRowLayout.addWidget(BtnCycleForm.widget, 1)
        TransformRowLayout.addWidget(BtnCycleState.widget, 1)
        InspectorLayout.addWidget(TransformRow)

        # Дії над об'єктом: Duplicate / Delete
        ActionRow = LCARS.Widget()
        ActionRowLayout = LCARS.Horizontal(ActionRow)
        ActionRowLayout.setContentsMargins(0, 0, 0, 0)
        ActionRowLayout.setSpacing(4)
        BtnDuplicate = LCARSButton(Text="DUPLICATE", Form=LCARSButton.PillHalf, Direction=180, Number="COPY", Height=34, FontSize=11)
        BtnDuplicate.OnClickAction = self.DuplicateActive
        BtnDelete = LCARSButton(Text="DELETE", Form=LCARSButton.PillHalf, Direction=0, Number="DEL", State=LCARSButton.ALERT, Height=34, FontSize=11)
        BtnDelete.OnClickAction = self.DeleteActive
        ActionRowLayout.addWidget(BtnDuplicate.widget, 1)
        ActionRowLayout.addWidget(BtnDelete.widget, 1)
        InspectorLayout.addWidget(ActionRow)

        InspectorLayout.addSpacing(6)
        CodeHeader = LCARSLabel(Text="CONSTRUCTOR CODE PREVIEW", FontSize=12)
        InspectorLayout.addWidget(CodeHeader.widget)

        self.ConstructorCodeBlock = LCARSDataBlock(
            Title="PYTHON CONSTRUCTOR CALL",
            Data={
                "CALL": "LCARSButton(Text='WARP ENGAGE',",
                "PARAMS": "Form=LCARSButton.Pill, W=175, H=40)",
                "STATE": "State=LCARSButton.NORMAL"
            },
            Width=270,
            Height=95,
            FontSize=11
        )
        InspectorLayout.addWidget(self.ConstructorCodeBlock.widget)

        InspectorLayout.addStretch()

        ResetBtn = LCARSButton(Text="RESET TO BASELINE", Form=LCARSButton.Pill, Number="RST-00", State=LCARSButton.ALERT, Height=38, FontSize=13)
        ResetBtn.OnClickAction = self.LoadButtonsCategory
        InspectorLayout.addWidget(ResetBtn.widget)

        MainLayout.addWidget(InspectorContainer, 1)

        # Монтуємо у PADD
        self.Padd.Add(MainContainer)

        # Завантажуємо базову категорію кнопок за замовчуванням
        self.LoadButtonsCategory()

    # ─────────────────────────────────────────────────────────────────────────
    # МЕТОДИ КЕРУВАННЯ КАТЕГОРІЯМИ ПОЛОТНА
    # ─────────────────────────────────────────────────────────────────────────
    def ClearCanvasContent(self):
        self.CanvasItems.clear()
        if hasattr(self.CanvasContentLayout, "count"):
            while self.CanvasContentLayout.count() > 0:
                Item = self.CanvasContentLayout.takeAt(0)
                W = getattr(Item, "widget", lambda: None)() if callable(getattr(Item, "widget", None)) else getattr(Item, "widget", None)
                if W and hasattr(W, "deleteLater"):
                    W.deleteLater()

    def SelectItem(self, Item: any):
        self.ActiveItem = Item
        self.UpdateInspectorPassport()

    def UpdateInspectorPassport(self):
        if not self.ActiveItem:
            return
        ClassName = self.ActiveItem.__class__.__name__
        FormVal = getattr(self.ActiveItem, "Form", "Standard")
        FormName = "RECT" if FormVal == LCARSButton.Rect else ("PILL" if FormVal == LCARSButton.Pill else ("SOFT" if FormVal == LCARSButton.Soft else ("PILL-HALF" if FormVal == LCARSButton.PillHalf else ("SOFT-HALF" if FormVal == LCARSButton.SoftHalf else str(FormVal)))))
        TextVal = str(getattr(self.ActiveItem, "Text", "") or "—")
        NumVal = str(getattr(self.ActiveItem, "Number", "") or "—")
        StateVal = str(getattr(self.ActiveItem, "State", "normal")).upper()
        W = self.ActiveItem.widget.width() if getattr(self.ActiveItem, "widget", None) else getattr(self.ActiveItem, "Width", 175)
        H = self.ActiveItem.widget.height() if getattr(self.ActiveItem, "widget", None) else getattr(self.ActiveItem, "Height", 40)

        self.PassportBlock.SetData({
            "CLASS": ClassName,
            "FORM": FormName,
            "LABEL": TextVal,
            "CODE": NumVal,
            "STATE": StateVal,
            "WIDTH": f"{W} PX",
            "HEIGHT": f"{H} PX"
        })

        self.ConstructorCodeBlock.SetData({
            "CALL": f"{ClassName}(Text='{TextVal}',",
            "PARAMS": f"Form={FormName}, W={W}, H={H})",
            "STATE": f"State=LCARSButton.{StateVal}"
        })

    def LoadButtonsCategory(self):
        self.CurrentCategory = "BUTTONS"
        self.ClearCanvasContent()
        self.CanvasHeaderLabel.SetText("CANVAS // CATEGORY: CANONICAL BASE BUTTONS")

        RowOne = LCARS.Widget()
        R1Layout = LCARS.Horizontal(RowOne)
        R1Layout.setContentsMargins(0, 0, 0, 0)
        R1Layout.setSpacing(8)
        b1 = LCARSButton(Text="SYSTEM RECT", Form=LCARSButton.Rect, Number="01-4402", Height=40, FontSize=13)
        b2 = LCARSButton(Text="WARP PILL", Form=LCARSButton.Pill, Number="02-1088", Height=40, FontSize=13)
        b3 = LCARSButton(Text="IMPULSE SOFT", Form=LCARSButton.Soft, Number="03-7740", Height=40, FontSize=13)
        b4 = LCARSButton(Text="ANGLE CUT", Form=LCARSButton.SoftHalf, Direction=180, Number="04-9912", Height=40, FontSize=13)
        for b in [b1, b2, b3, b4]:
            self.BindItemSelection(b)
            R1Layout.addWidget(b.widget, 1)
        self.CanvasContentLayout.addWidget(RowOne)

        RowTwo = LCARS.Widget()
        R2Layout = LCARS.Horizontal(RowTwo)
        R2Layout.setContentsMargins(0, 0, 0, 0)
        R2Layout.setSpacing(8)
        b5 = LCARSButton(Text="COMMUNICATION", Form=LCARSButton.Pill, Number="05-9921", Height=40, FontSize=13)
        b6 = LCARSButton(Text="TRANSPORTER", Form=LCARSButton.Rect, Number="06-3310", Height=40, FontSize=13)
        b7 = LCARSButton(Text="DEFLECTOR", Form=LCARSButton.Soft, Number="07-4480", Height=40, FontSize=13)
        b8 = LCARSButton(Text="SUBSPACE ODN", Form=LCARSButton.SoftHalf, Direction=0, Number="08-1120", Height=40, FontSize=13)
        for b in [b5, b6, b7, b8]:
            self.BindItemSelection(b)
            R2Layout.addWidget(b.widget, 1)
        self.CanvasContentLayout.addWidget(RowTwo)

        self.CanvasContentLayout.addStretch()
        self.SelectItem(b1)

    def LoadCapsCategory(self):
        self.CurrentCategory = "CAPS"
        self.ClearCanvasContent()
        self.CanvasHeaderLabel.SetText("CANVAS // CATEGORY: DIRECTIONAL CAPS (4 QUADRANTS)")

        RowOne = LCARS.Widget()
        R1Layout = LCARS.Horizontal(RowOne)
        R1Layout.setContentsMargins(0, 0, 0, 0)
        R1Layout.setSpacing(8)
        c1 = LCARSButton(Text="CAP EAST 0", Form=LCARSButton.PillHalf, Direction=0, Number="01-E00", Height=40, FontSize=13)
        c2 = LCARSButton(Text="CAP SOUTH 90", Form=LCARSButton.PillHalf, Direction=90, Number="02-S90", Height=40, FontSize=13)
        c3 = LCARSButton(Text="CAP WEST 180", Form=LCARSButton.PillHalf, Direction=180, Number="03-W18", Height=40, FontSize=13)
        c4 = LCARSButton(Text="CAP NORTH 270", Form=LCARSButton.PillHalf, Direction=270, Number="04-N27", Height=40, FontSize=13)
        for c in [c1, c2, c3, c4]:
            self.BindItemSelection(c)
            R1Layout.addWidget(c.widget, 1)
        self.CanvasContentLayout.addWidget(RowOne)

        RowTwo = LCARS.Widget()
        R2Layout = LCARS.Horizontal(RowTwo)
        R2Layout.setContentsMargins(0, 0, 0, 0)
        R2Layout.setSpacing(8)
        s1 = LCARSButton(Text="SOFT EAST 0", Form=LCARSButton.SoftHalf, Direction=0, Number="05-SE0", Height=40, FontSize=13)
        s2 = LCARSButton(Text="SOFT SOUTH 90", Form=LCARSButton.SoftHalf, Direction=90, Number="06-SS9", Height=40, FontSize=13)
        s3 = LCARSButton(Text="SOFT WEST 180", Form=LCARSButton.SoftHalf, Direction=180, Number="07-SW1", Height=40, FontSize=13)
        s4 = LCARSButton(Text="SOFT NORTH 270", Form=LCARSButton.SoftHalf, Direction=270, Number="08-SN2", Height=40, FontSize=13)
        for s in [s1, s2, s3, s4]:
            self.BindItemSelection(s)
            R2Layout.addWidget(s.widget, 1)
        self.CanvasContentLayout.addWidget(RowTwo)

        self.CanvasContentLayout.addStretch()
        self.SelectItem(c1)

    def LoadElbowsCategory(self):
        self.CurrentCategory = "ELBOWS"
        self.ClearCanvasContent()
        self.CanvasHeaderLabel.SetText("CANVAS // CATEGORY: L-FRAME ELBOW STRUCTURES")

        RowOne = LCARS.Widget()
        R1Layout = LCARS.Horizontal(RowOne)
        R1Layout.setContentsMargins(0, 0, 0, 0)
        R1Layout.setSpacing(12)
        e1 = LCARSElbow(Direction="top-left", Text="PRIMARY BRIDGE", Number="01-TL", Width=320, Height=60, Thickness=24, Radius=20)
        e2 = LCARSElbow(Direction="top-right", Text="ASTROMETRICS", Number="02-TR", Width=320, Height=60, Thickness=24, Radius=20)
        for e in [e1, e2]:
            self.BindItemSelection(e)
            R1Layout.addWidget(e.widget, 1)
        self.CanvasContentLayout.addWidget(RowOne)

        RowTwo = LCARS.Widget()
        R2Layout = LCARS.Horizontal(RowTwo)
        R2Layout.setContentsMargins(0, 0, 0, 0)
        R2Layout.setSpacing(12)
        e3 = LCARSElbow(Direction="bottom-left", Text="MAIN ENGINEERING", Number="03-BL", Width=320, Height=60, Thickness=24, Radius=20)
        e4 = LCARSElbow(Direction="bottom-right", Text="WARP REACTION", Number="04-BR", Width=320, Height=60, Thickness=24, Radius=20)
        for e in [e3, e4]:
            self.BindItemSelection(e)
            R2Layout.addWidget(e.widget, 1)
        self.CanvasContentLayout.addWidget(RowTwo)

        self.CanvasContentLayout.addStretch()
        self.SelectItem(e1)

    def LoadIndicatorsCategory(self):
        self.CurrentCategory = "INDICATORS"
        self.ClearCanvasContent()
        self.CanvasHeaderLabel.SetText("CANVAS // CATEGORY: STATUS & SENSORY INDICATORS")

        RowOne = LCARS.Widget()
        R1Layout = LCARS.Horizontal(RowOne)
        R1Layout.setContentsMargins(0, 0, 0, 0)
        R1Layout.setSpacing(8)
        i1 = LCARSIndicator(IndicatorType=LCARSIndicator.Pill, Height=40, Width=140)
        i2 = LCARSIndicator(IndicatorType=LCARSIndicator.Rect, Height=40, Width=140)
        i3 = LCARSIndicator(IndicatorType=LCARSIndicator.PillHalf, Direction=180, Height=40, Width=140)
        i4 = LCARSIndicator(IndicatorType=LCARSIndicator.PillHalf, Direction=0, Height=40, Width=140)
        for i in [i1, i2, i3, i4]:
            self.BindItemSelection(i)
            R1Layout.addWidget(i.widget, 1)
        self.CanvasContentLayout.addWidget(RowOne)

        BarRow = LCARS.Widget()
        BLayout = LCARS.Horizontal(BarRow)
        BLayout.setContentsMargins(0, 0, 0, 0)
        BLayout.setSpacing(8)
        bar1 = LCARSBar(Height=16, Width=300)
        bar2 = LCARSBar(Height=16, Width=300)
        for b in [bar1, bar2]:
            self.BindItemSelection(b)
            BLayout.addWidget(b.widget, 1)
        self.CanvasContentLayout.addWidget(BarRow)

        DataBlockItem = LCARSDataBlock(
            Title="SUBSYSTEM SENSOR ARRAY",
            Data={
                "TACHYON EMITTER": "NOMINAL",
                "GRAVITON BEARING": "OPTIMAL",
                "PLASMA DRIFT": "0.002 PERCENT"
            },
            Width=620,
            Height=90
        )
        self.BindItemSelection(DataBlockItem)
        self.CanvasContentLayout.addWidget(DataBlockItem.widget)

        self.CanvasContentLayout.addStretch()
        self.SelectItem(i1)

    def LoadCompositesCategory(self):
        self.CurrentCategory = "COMPOSITES"
        self.ClearCanvasContent()
        self.CanvasHeaderLabel.SetText("CANVAS // CATEGORY: COMPOSITE ASSEMBLIES & STRIPS")

        # Двоетапна пара авторизації
        DualRow = LCARS.Widget()
        DualLayout = LCARS.Horizontal(DualRow)
        DualLayout.setContentsMargins(0, 0, 0, 0)
        DualLayout.setSpacing(4)
        arm = LCARSButton(Text="ARM / AUTHORIZE", Form=LCARSButton.PillHalf, Direction=180, Number="99-ARM", State=LCARSButton.YELLOW, Height=40, FontSize=13)
        exec_btn = LCARSButton(Text="EXECUTE SEQUENCE", Form=LCARSButton.PillHalf, Direction=0, Number="99-EXEC", State=LCARSButton.ALERT, Height=40, FontSize=13)
        for b in [arm, exec_btn]:
            self.BindItemSelection(b)
            DualLayout.addWidget(b.widget, 1)
        self.CanvasContentLayout.addWidget(DualRow)

        # Тріада регулювання
        StepRow = LCARS.Widget()
        StepLayout = LCARS.Horizontal(StepRow)
        StepLayout.setContentsMargins(0, 0, 0, 0)
        StepLayout.setSpacing(3)
        dec_btn = LCARSButton(Text="[-] DEC", Form=LCARSButton.SoftHalf, Direction=180, Number="DEC-01", Height=40, FontSize=13)
        val_btn = LCARSButton(Text="WARP 9.975", Form=LCARSButton.Rect, Number="V-4700", Height=40, FontSize=13)
        inc_btn = LCARSButton(Text="[+] INC", Form=LCARSButton.SoftHalf, Direction=0, Number="INC-02", Height=40, FontSize=13)
        for b in [dec_btn, val_btn, inc_btn]:
            self.BindItemSelection(b)
            StepLayout.addWidget(b.widget, 1)
        self.CanvasContentLayout.addWidget(StepRow)

        # Смуга клавіатури
        KeypadRow = LCARS.Widget()
        KeypadLayout = LCARS.Horizontal(KeypadRow)
        KeypadLayout.setContentsMargins(0, 0, 0, 0)
        KeypadLayout.setSpacing(3)
        k1 = LCARSButton(Text="1", Form=LCARSButton.PillHalf, Direction=180, Number="01", Height=38, FontSize=14)
        k2 = LCARSButton(Text="2", Form=LCARSButton.Rect, Number="02", Height=38, FontSize=14)
        k3 = LCARSButton(Text="3", Form=LCARSButton.Rect, Number="03", Height=38, FontSize=14)
        k4 = LCARSButton(Text="4", Form=LCARSButton.Rect, Number="04", Height=38, FontSize=14)
        k5 = LCARSButton(Text="5", Form=LCARSButton.PillHalf, Direction=0, Number="05", Height=38, FontSize=14)
        for k in [k1, k2, k3, k4, k5]:
            self.BindItemSelection(k)
            KeypadLayout.addWidget(k.widget, 1)
        self.CanvasContentLayout.addWidget(KeypadRow)

        self.CanvasContentLayout.addStretch()
        self.SelectItem(arm)

    def LoadAlertsCategory(self):
        self.CurrentCategory = "ALERTS"
        self.ClearCanvasContent()
        self.CanvasHeaderLabel.SetText("CANVAS // CATEGORY: SYSTEM ALERT PALETTES")

        RowOne = LCARS.Widget()
        R1Layout = LCARS.Horizontal(RowOne)
        R1Layout.setContentsMargins(0, 0, 0, 0)
        R1Layout.setSpacing(8)
        a1 = LCARSButton(Text="CONDITION GREEN", Form=LCARSButton.Pill, Number="47-0101", State=LCARSButton.NORMAL, Height=42, FontSize=14)
        a2 = LCARSButton(Text="YELLOW ALERT", Form=LCARSButton.PillHalf, Direction=180, Number="47-0102", State=LCARSButton.YELLOW, Height=42, FontSize=14)
        a3 = LCARSButton(Text="RED ALERT", Form=LCARSButton.Pill, Number="47-0103", State=LCARSButton.ALERT, Height=42, FontSize=14)
        a4 = LCARSButton(Text="WARP CORE EJECT", Form=LCARSButton.Soft, Number="47-0104", State=LCARSButton.ALERT, Height=42, FontSize=14)
        for a in [a1, a2, a3, a4]:
            self.BindItemSelection(a)
            R1Layout.addWidget(a.widget, 1)
        self.CanvasContentLayout.addWidget(RowOne)

        RowTwo = LCARS.Widget()
        R2Layout = LCARS.Horizontal(RowTwo)
        R2Layout.setContentsMargins(0, 0, 0, 0)
        R2Layout.setSpacing(8)
        d1 = LCARSButton(Text="OFFLINE DECK 1", Form=LCARSButton.Rect, Number="00-0001", State=LCARSButton.DISABLED, Sensory=False, Height=42, FontSize=14)
        d2 = LCARSButton(Text="OFFLINE DECK 2", Form=LCARSButton.PillHalf, Direction=0, Number="00-0002", State=LCARSButton.DISABLED, Sensory=False, Height=42, FontSize=14)
        for d in [d1, d2]:
            if hasattr(d.widget, "setEnabled"):
                d.widget.setEnabled(False)
            self.BindItemSelection(d)
            R2Layout.addWidget(d.widget, 1)
        self.CanvasContentLayout.addWidget(RowTwo)

        self.CanvasContentLayout.addStretch()
        self.SelectItem(a1)

    # ─────────────────────────────────────────────────────────────────────────
    # EDIT MODE / КОНСТРУКТОР ТРАНСФОРМАЦІЇ
    # ─────────────────────────────────────────────────────────────────────────
    def BindItemSelection(self, Item: any):
        self.CanvasItems.append(Item)
        OriginalClick = getattr(Item, "OnClick", None)

        def InterceptClick():
            self.SelectItem(Item)
            if callable(OriginalClick):
                OriginalClick()
            Action = getattr(Item, "OnClickAction", None)
            if callable(Action):
                Action()

        Item.OnClick = InterceptClick

    def AdjustActiveDimensions(self, DeltaW: int, DeltaH: int):
        if not self.ActiveItem or not getattr(self.ActiveItem, "widget", None):
            return
        W = self.ActiveItem.widget
        CurrentW = W.width()
        CurrentH = W.height()
        NewW = max(60, CurrentW + DeltaW)
        NewH = max(24, CurrentH + DeltaH)
        W.setFixedSize(NewW, NewH)
        self.ActiveItem.Width = NewW
        self.ActiveItem.Height = NewH
        if hasattr(self.ActiveItem, "Update"):
            self.ActiveItem.Update()
        self.UpdateInspectorPassport()

    def CycleActiveForm(self):
        if not self.ActiveItem or not hasattr(self.ActiveItem, "Form"):
            return
        Current = getattr(self.ActiveItem, "Form", LCARSButton.Rect)
        Forms = [LCARSButton.Rect, LCARSButton.Pill, LCARSButton.Soft, LCARSButton.PillHalf, LCARSButton.SoftHalf]
        Idx = Forms.index(Current) if Current in Forms else 0
        NextForm = Forms[(Idx + 1) % len(Forms)]
        self.ActiveItem.Form = NextForm
        if hasattr(self.ActiveItem, "Update"):
            self.ActiveItem.Update()
        self.UpdateInspectorPassport()

    def CycleActiveState(self):
        if not self.ActiveItem or not hasattr(self.ActiveItem, "State"):
            return
        Current = getattr(self.ActiveItem, "State", LCARSButton.NORMAL)
        States = [LCARSButton.NORMAL, LCARSButton.YELLOW, LCARSButton.ALERT, LCARSButton.DISABLED]
        Idx = States.index(Current) if Current in States else 0
        NextState = States[(Idx + 1) % len(States)]
        self.ActiveItem.SetState(NextState)
        self.UpdateInspectorPassport()

    def DuplicateActive(self):
        if not self.ActiveItem:
            return
        Text = getattr(self.ActiveItem, "Text", "COPY")
        Number = f"CP-{len(self.CanvasItems)+1:02d}"
        Form = getattr(self.ActiveItem, "Form", LCARSButton.Pill)
        Direction = getattr(self.ActiveItem, "Direction", 0)
        NewBtn = LCARSButton(Text=Text, Form=Form, Direction=Direction, Number=Number, Height=40, FontSize=13)
        self.BindItemSelection(NewBtn)
        self.CanvasContentLayout.insertWidget(0, NewBtn.widget)
        self.SelectItem(NewBtn)

    def DeleteActive(self):
        if not self.ActiveItem or not getattr(self.ActiveItem, "widget", None):
            return
        W = self.ActiveItem.widget
        if self.ActiveItem in self.CanvasItems:
            self.CanvasItems.remove(self.ActiveItem)
        if hasattr(W, "deleteLater"):
            W.deleteLater()
        self.ActiveItem = self.CanvasItems[0] if self.CanvasItems else None
        self.UpdateInspectorPassport()

    def SpawnObject(self, ObjectType: str):
        Num = f"SP-{len(self.CanvasItems)+1:02d}"
        if ObjectType == "PILL":
            NewObj = LCARSButton(Text="SPAWNED PILL", Form=LCARSButton.Pill, Number=Num, Height=40, FontSize=13)
        elif ObjectType == "RECT":
            NewObj = LCARSButton(Text="SPAWNED RECT", Form=LCARSButton.Rect, Number=Num, Height=40, FontSize=13)
        elif ObjectType == "SOFT":
            NewObj = LCARSButton(Text="SPAWNED SOFT", Form=LCARSButton.Soft, Number=Num, Height=40, FontSize=13)
        elif ObjectType == "ELBOW":
            NewObj = LCARSElbow(Direction="top-left", Text="SPAWNED ELBOW", Number=Num, Width=320, Height=55, Thickness=22, Radius=18)
        else:
            NewObj = LCARSButton(Text="SPAWNED", Form=LCARSButton.Rect, Number=Num, Height=40, FontSize=13)

        self.BindItemSelection(NewObj)
        self.CanvasContentLayout.insertWidget(0, NewObj.widget)
        self.SelectItem(NewObj)

    def Run(self):
        self.Padd.show()
        return self.App.exec()


if __name__ == "__main__":
    Designer = DesignerWorkbench()
    Designer.Run()
