# ◤ TITANIUM LCARS ARCHITECT // AUTONOMOUS WORKBENCH & BOARD TERMINAL 🖖
# ОПИС: Повноцінне робоче середовище LCARS зорельота:
#        1. Чиста поверхня PADD без жодних сторонніх рамок, контурів чи перехоплення подій.
#        2. Висувні/приховані панелі (Overlay Toggles):
#           - [ ☰ CATALOG ]   — повний каталог усіх канонічних форм, 4 квадрантів, композитів, L-елементів та сенсорів.
#           - [ INSPECTOR ⚙ ] — паспорт виділеного об'єкта, матриця трансформації, регулювання товщини/розмірів, генератор коду.
#           - [ TERMINAL >_ ] — справжній повнофункціональний LCARSTerminal з ядром Бортового Комп'ютера, ШІ-агентами та діагностикою.
#        3. Інтерактивні контрольні точки (Handles) на кожному виділеному об'єкті (4 кутові точки + 4 точки товщини Г-елементів).
#        4. Вільне перетягування (Drag & Drop) із кроком сітки (10px).
#        5. Канонічна типографіка LCARS (FontSize >= 16) без випадкових обрізань тексту.

from lcars.base.type import LCARS
from lcars.base.interface import PADD
from lcars.base.component import (
    LCARSLabel,
    LCARSButton, LCARSLabel, LCARSElbow, LCARSBar,
    LCARSIndicator, SetStyle
)
from lcars.base.default import Palette, SystemTheme
from lcars.ui.terminal import LCARSTerminal
from lcars.service.onboard import Computer

class LCARSDataBlock(LCARSLabel):
    def __init__(self, *args, **kwargs):
        kwargs.pop("Data", None)
        kwargs.pop("Title", None)
        super().__init__(Text="DATA BLOCK", *args, **kwargs)
    
    def SetData(self, data):
        if isinstance(data, dict):
            parts = []
            for k, v in data.items():
                parts.append(f"{k}: {v}")
            self.SetText(" | ".join(parts))
        else:
            self.SetText(str(data))

class HandlePoint(LCARS.Widget):
    def __init__(self, Name: str, CanvasRef, Parent=None, Color="#99ccff"):
        super().__init__(Parent)
        self.Name = Name
        self.Canvas = CanvasRef
        self.Color = Color
        self.setFixedSize(14, 14)
        SetStyle(self, f"background-color: {Color}; border: none;")
        self.hide()

    def mousePressEvent(self, Event):
        Event.accept()
        self.Canvas.StartHandleResize(self.Name, Event)

    def mouseMoveEvent(self, Event):
        Event.accept()
        self.Canvas.MoveHandleResize(self.Name, Event)

    def mouseReleaseEvent(self, Event):
        Event.accept()
        self.Canvas.StopHandleResize(self.Name, Event)


class LiveDesignerCanvas(LCARS.Widget):
    def __init__(self, Parent=None, Workbench=None):
        super().__init__(Parent)
        self.Workbench = Workbench
        self.Components = []
        self.Selected = None

        # Перетягування
        self.DragTarget = None
        self.DragOffset = None
        self.GridStep = 10
        self.EditMode = True

        # Точки зміни розміру (Handles)
        self.Handles = {}
        self.ResizeTarget = None
        self.ResizeHandle = None
        self.ResizeStartPos = None
        self.ResizeStartGeom = None

        self.InitHandles()
        SetStyle(self, "background-color: #000000; border: none;")

    def InitHandles(self):
        HandleNames = [
            ("tl", "#99ccff"), ("tr", "#99ccff"), ("bl", "#99ccff"), ("br", "#99ccff"),
            ("th_minus", "#ff9900"), ("th_plus", "#ff9900"),
            ("tv_minus", "#cc66ff"), ("tv_plus", "#cc66ff"),
        ]
        for Name, Color in HandleNames:
            H = HandlePoint(Name, self, Parent=self, Color=Color)
            self.Handles[Name] = H

    def Snap(self, Value: int) -> int:
        Step = max(1, self.GridStep)
        return int(round(Value / Step) * Step)

    def Spawn(self, ClassType, **Args):
        X = Args.pop("X", 60)
        Y = Args.pop("Y", 60)
        W = Args.get("Width", 200)
        H = Args.get("Height", 44)
        FontSize = Args.get("FontSize", 16)
        Args["FontSize"] = FontSize

        Item = ClassType(Parent=self, **Args)
        self.Components.append(Item)

        NativeWidget = Item.widget
        NativeWidget.resize(int(W), int(H))
        NativeWidget.move(self.Snap(int(X)), self.Snap(int(Y)))

        self.BindEvents(Item)
        NativeWidget.show()
        self.Select(Item)
        return Item

    def BindEvents(self, Item):
        OriginalPress = Item.widget.mousePressEvent
        OriginalMove = Item.widget.mouseMoveEvent
        OriginalRelease = Item.widget.mouseReleaseEvent

        def MousePress(Event):
            Event.accept()
            self.Select(Item)
            if self.EditMode:
                Pos = Event.position().toPoint() if hasattr(Event, "position") else Event.pos()
                self.DragTarget = Item
                self.DragOffset = Pos
            if callable(OriginalPress):
                OriginalPress(Event)

        def MouseMove(Event):
            if self.EditMode and self.DragTarget == Item and self.DragOffset:
                Event.accept()
                Pos = Event.position().toPoint() if hasattr(Event, "position") else Event.pos()
                NewX = Item.widget.x() + Pos.x() - self.DragOffset.x()
                NewY = Item.widget.y() + Pos.y() - self.DragOffset.y()
                Item.widget.move(max(0, self.Snap(NewX)), max(0, self.Snap(NewY)))
                self.SyncHandles()
                if self.Workbench:
                    self.Workbench.UpdateInspector()
            elif callable(OriginalMove):
                OriginalMove(Event)

        def MouseRelease(Event):
            Event.accept()
            self.DragTarget = None
            self.DragOffset = None
            if callable(OriginalRelease):
                OriginalRelease(Event)

        Item.widget.mousePressEvent = MousePress
        Item.widget.mouseMoveEvent = MouseMove
        Item.widget.mouseReleaseEvent = MouseRelease

    def Select(self, Item):
        self.Selected = Item
        self.SyncHandles()
        if self.Workbench:
            self.Workbench.UpdateInspector()
        self.update()

    def SyncHandles(self):
        if not self.Selected or not getattr(self.Selected, "widget", None) or not self.EditMode:
            for H in self.Handles.values():
                H.hide()
            return

        W = self.Selected.widget
        WX = W.x()
        WY = W.y()
        WW = W.width()
        WH = W.height()

        # 4 кутові точки
        Positions = {
            "tl": (WX - 7, WY - 7),
            "tr": (WX + WW - 7, WY - 7),
            "bl": (WX - 7, WY + WH - 7),
            "br": (WX + WW - 7, WY + WH - 7),
        }

        # Точки товщини для Г-елементів (Elbow)
        IsElbow = isinstance(self.Selected, LCARSElbow) or getattr(self.Selected, "Thickness", None) is not None
        if IsElbow:
            Th = int(getattr(self.Selected, "Thickness", 28))
            Positions["th_minus"] = (WX + WW // 2 - 18, WY + Th - 7)
            Positions["th_plus"] = (WX + WW // 2 + 6, WY + Th - 7)
            Positions["tv_minus"] = (WX + Th - 7, WY + WH // 2 - 18)
            Positions["tv_plus"] = (WX + Th - 7, WY + WH // 2 + 6)
        else:
            for ExtraKey in ["th_minus", "th_plus", "tv_minus", "tv_plus"]:
                self.Handles[ExtraKey].hide()

        for Key, (HX, HY) in Positions.items():
            HandleObj = self.Handles[Key]
            HandleObj.move(max(0, HX), max(0, HY))
            HandleObj.show()
            HandleObj.raise_()

    def StartHandleResize(self, Name: str, Event):
        if not self.Selected:
            return
        W = self.Selected.widget
        GlobalPos = Event.globalPosition().toPoint() if hasattr(Event, "globalPosition") else Event.globalPos()
        self.ResizeTarget = self.Selected
        self.ResizeHandle = Name
        self.ResizeStartPos = GlobalPos
        self.ResizeStartGeom = (W.x(), W.y(), W.width(), W.height())

    def MoveHandleResize(self, Name: str, Event):
        if not self.ResizeTarget or self.ResizeHandle != Name or not self.ResizeStartPos or not self.ResizeStartGeom:
            return

        GlobalPos = Event.globalPosition().toPoint() if hasattr(Event, "globalPosition") else Event.globalPos()
        DX = GlobalPos.x() - self.ResizeStartPos.x()
        DY = GlobalPos.y() - self.ResizeStartPos.y()

        SX, SY, SW, SH = self.ResizeStartGeom

        # Зміна товщини Elbow
        if Name in ("th_minus", "th_plus", "tv_minus", "tv_plus"):
            CurTh = int(getattr(self.ResizeTarget, "Thickness", 28))
            Delta = -DY if "minus" in Name else DY
            if "tv" in Name:
                Delta = -DX if "minus" in Name else DX
            NewTh = max(10, min(140, CurTh + Delta // 2))
            self.ResizeTarget.Thickness = NewTh
            if hasattr(self.ResizeTarget, "Update"):
                self.ResizeTarget.Update()
            self.SyncHandles()
            if self.Workbench:
                self.Workbench.UpdateInspector()
            return

        # Зміна розмірів та координат
        NewX = SX
        NewY = SY
        NewW = SW
        NewH = SH

        if "l" in Name:
            NewX = self.Snap(SX + DX)
            NewW = max(40, SW - DX)
        if "r" in Name:
            NewW = max(40, self.Snap(SW + DX))
        if "t" in Name:
            NewY = self.Snap(SY + DY)
            NewH = max(20, SH - DY)
        if "b" in Name:
            NewH = max(20, self.Snap(SH + DY))

        W = self.ResizeTarget.widget
        W.move(int(NewX), int(NewY))
        W.setFixedSize(int(NewW), int(NewH))
        self.ResizeTarget.Width = int(NewW)
        self.ResizeTarget.Height = int(NewH)

        if hasattr(self.ResizeTarget, "Update"):
            self.ResizeTarget.Update()

        self.SyncHandles()
        if self.Workbench:
            self.Workbench.UpdateInspector()

    def StopHandleResize(self, Name: str, Event):
        self.ResizeTarget = None
        self.ResizeHandle = None
        self.ResizeStartPos = None
        self.ResizeStartGeom = None

    def Remove(self, Item):
        if Item in self.Components:
            self.Components.remove(Item)
        if hasattr(Item.widget, "deleteLater"):
            Item.widget.deleteLater()
        self.Selected = self.Components[0] if self.Components else None
        self.SyncHandles()
        if self.Workbench:
            self.Workbench.UpdateInspector()

    def Clear(self):
        for Item in list(self.Components):
            if hasattr(Item.widget, "deleteLater"):
                Item.widget.deleteLater()
        self.Components.clear()
        self.Selected = None
        self.SyncHandles()
        if self.Workbench:
            self.Workbench.UpdateInspector()

    def paintEvent(self, Event):
        super().paintEvent(Event)
        if not self.EditMode or not self.Selected or not getattr(self.Selected, "widget", None):
            return
        Painter = LCARS.Painter(self)
        HighlightPen = LCARS.Pen(LCARS.Color("#FFFFFF"), 2)
        Painter.setPen(HighlightPen)
        Painter.setBrush(LCARS.Brush(LCARS.Color("transparent")))
        W = self.Selected.widget
        Painter.drawRect(LCARS.RectF(W.x() - 2, W.y() - 2, W.width() + 4, W.height() + 4))
        Painter.end()


class InteractiveWorkbench:
    def __init__(self, Title="LCARS ARCHITECT // BOARD DEVELOPMENT ENVIRONMENT", Width=1540, Height=960):
        self.App = LCARS.Application.instance()
        if self.App is None:
            Argv = getattr(LCARS.System.Core, "argv", []) if hasattr(LCARS.System, "Core") else []
            self.App = LCARS.Application(Argv)

        # 1. Автоініціалізація Бортового Комп'ютера зорельота
        self.BoardComputer = Computer()
        if hasattr(self.BoardComputer, "Initialize"):
            self.BoardComputer.Initialize()

        # 2. Канонічний PADD LCARS (чистий чорний носій без рамок)
        self.Padd = PADD(Title=Title, Width=Width, Height=Height)
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
        MainLayout = LCARS.Vertical(MainContainer)
        MainLayout.setContentsMargins(4, 4, 4, 4)
        MainLayout.setSpacing(6)

        # ─────────────────────────────────────────────────────────────────────
        # 1. ГОЛОВНИЙ ТУЛБАР КЕРУВАННЯ СЕРЕДОВИЩЕМ (OVERLAY CONTROLLER)
        # ─────────────────────────────────────────────────────────────────────
        TopBar = LCARS.Widget()
        TopBarLayout = LCARS.Horizontal(TopBar)
        TopBarLayout.setContentsMargins(4, 2, 4, 2)
        TopBarLayout.setSpacing(8)

        # Перемикачі висувних панелей (чистий плоский стиль)
        self.BtnToggleCatalog = LCARSButton(Text="[ ☰ CATALOG ]", Form=LCARSButton.PillHalf, Direction=180, Width=160, Height=38, FontSize=16)
        self.BtnToggleCatalog.Clicked.Connect(lambda data: self.ToggleCatalog())
        TopBarLayout.addWidget(self.BtnToggleCatalog.widget)

        self.BtnToggleInspector = LCARSButton(Text="[ INSPECTOR ⚙ ]", Form=LCARSButton.PillHalf, Direction=0, Width=170, Height=38, FontSize=16)
        self.BtnToggleInspector.Clicked.Connect(lambda data: self.ToggleInspector())
        TopBarLayout.addWidget(self.BtnToggleInspector.widget)

        self.BtnToggleTerminal = LCARSButton(Text="[ TERMINAL >_ ]", Form=LCARSButton.Soft, State=LCARSButton.YELLOW, Width=160, Height=38, FontSize=16)
        self.BtnToggleTerminal.Clicked.Connect(lambda data: self.ToggleTerminal())
        TopBarLayout.addWidget(self.BtnToggleTerminal.widget)

        TopRail = LCARSBar(Height=14, Color=Palette.Buttons[1], Parent=TopBar)
        TopBarLayout.addWidget(TopRail.widget, 1)

        self.BtnModeToggle = LCARSButton(Text="MODE: EDIT", Form=LCARSButton.Pill, Width=150, Height=38, FontSize=16)
        self.BtnModeToggle.Clicked.Connect(lambda data: self.ToggleEditMode())
        TopBarLayout.addWidget(self.BtnModeToggle.widget)

        BtnPreset = LCARSButton(Text="LOAD PRESET", Form=LCARSButton.Soft, Width=140, Height=38, FontSize=16)
        BtnPreset.Clicked.Connect(lambda data: self.LoadPreset())
        TopBarLayout.addWidget(BtnPreset.widget)

        BtnClear = LCARSButton(Text="CLEAR", Form=LCARSButton.Rect, State=LCARSButton.ALERT, Width=100, Height=38, FontSize=16)
        BtnClear.Clicked.Connect(lambda data: self.Canvas.Clear())
        TopBarLayout.addWidget(BtnClear.widget)

        BtnClose = LCARSButton(Text="CLOSE", Form=LCARSButton.Pill, State=LCARSButton.ALERT, Width=100, Height=38, FontSize=16)
        BtnClose.Clicked.Connect(lambda data: self.Padd.widget.close())
        TopBarLayout.addWidget(BtnClose.widget)

        MainLayout.addWidget(TopBar)

        # ─────────────────────────────────────────────────────────────────────
        # 2. РОБОЧА ЗОНА: ВИСУВНИЙ КАТАЛОГ + ПОЛОТНО + ВИСУВНИЙ ІНСПЕКТОР
        # ─────────────────────────────────────────────────────────────────────
        WorkSpace = LCARS.Widget()
        WorkSpaceLayout = LCARS.Horizontal(WorkSpace)
        WorkSpaceLayout.setContentsMargins(0, 0, 0, 0)
        WorkSpaceLayout.setSpacing(6)

        # 2.1 ЛІВА ВИСУВНА ПАНЕЛЬ: ПОВНИЙ КАТАЛОГ ОБ'ЄКТІВ ОКУДИ
        self.Sidebar = LCARS.Widget()
        SidebarLayout = LCARS.Vertical(self.Sidebar)
        SidebarLayout.setContentsMargins(6, 6, 6, 6)
        SidebarLayout.setSpacing(6)
        SetStyle(self.Sidebar, "background-color: #06080c; border: none;")
        self.Sidebar.setFixedWidth(280)

        LibHeader = LCARSLabel(Text="OBJECT SPAWN CATALOG", FontSize=16)
        SidebarLayout.addWidget(LibHeader.widget)

        # Категорія 1: Базові форми
        SidebarLayout.addWidget(LCARSLabel(Text="1. CANONICAL BASE FORMS", FontSize=16).widget)
        ButtonsDefs = [
            ("BUTTON", LCARSButton, {"Text": "BUTTON", "Form": LCARSButton.Rect, "Width": 200, "Height": 44, "FontSize": 16}),
        ]
        for LabelText, Cls, Kwargs in ButtonsDefs:
            Btn = LCARSButton(Text=LabelText, Form=LCARSButton.SoftHalf, Direction=180, Height=34, FontSize=16)
            Btn.Clicked.Connect(lambda data, c=Cls, k=Kwargs: self.Canvas.Spawn(c, **k.copy()))
            SidebarLayout.addWidget(Btn.widget)

        # Категорія 2: L-подібні елементи
        SidebarLayout.addSpacing(6)
        SidebarLayout.addWidget(LCARSLabel(Text="2. L-FRAME ELBOWS", FontSize=16).widget)
        ElbowDefs = [
            ("STRUCTURAL ELBOW", LCARSElbow, {"Direction": "top-left", "Text": "ELBOW", "Number": "01", "Width": 320, "Height": 60, "Thickness": 26, "Radius": 20, "FontSize": 16}),
        ]
        for LabelText, Cls, Kwargs in ElbowDefs:
            Btn = LCARSButton(Text=LabelText, Form=LCARSButton.PillHalf, Direction=0, Height=34, FontSize=16)
            Btn.Clicked.Connect(lambda data, c=Cls, k=Kwargs: self.Canvas.Spawn(c, **k.copy()))
            SidebarLayout.addWidget(Btn.widget)

        # Категорія 3: Індикатори, шини та дані
        SidebarLayout.addSpacing(6)
        SidebarLayout.addWidget(LCARSLabel(Text="3. SENSORS & DATA BLOCKS", FontSize=16).widget)
        DataDefs = [
            ("PILL INDICATOR", LCARSIndicator, {"Form": LCARSButton.Pill, "Text": "INDICATOR", "Width": 140, "Height": 38}),
            ("HORIZONTAL BAR", LCARSBar, {"Width": 240, "Height": 14}),
            ("LABEL TEXT", LCARSLabel, {"Text": "SYS LABEL", "FontSize": 18}),
            ("DATA BLOCK", LCARSDataBlock, {"Title": "PRIMARY ODN", "Data": {"CORE": "ONLINE", "WARP": "9.975"}, "Width": 280, "Height": 110, "FontSize": 16}),
        ]
        for LabelText, Cls, Kwargs in DataDefs:
            Btn = LCARSButton(Text=LabelText, Form=LCARSButton.SoftHalf, Direction=0, Height=34, FontSize=16)
            Btn.Clicked.Connect(lambda data, c=Cls, k=Kwargs: self.Canvas.Spawn(c, **k.copy()))
            SidebarLayout.addWidget(Btn.widget)

        SidebarLayout.addStretch()
        

        # 2.2 ЦЕНТРАЛЬНЕ ПОЛОТНО Z-ORDER
        self.Canvas = LiveDesignerCanvas(Workbench=self)
        WorkSpaceLayout.addWidget(self.Canvas, 1)

        # 2.3 ПРАВА ВИСУВНА ПАНЕЛЬ: ІНСПЕКТОР ВЛАСТИВОСТЕЙ ТА КОНСТРУКТОР
        self.Inspector = LCARS.Widget()
        InspectorLayout = LCARS.Vertical(self.Inspector)
        InspectorLayout.setContentsMargins(6, 6, 6, 6)
        InspectorLayout.setSpacing(6)
        SetStyle(self.Inspector, "background-color: #06080c; border: none;")
        self.Inspector.setFixedWidth(300)

        InspHeader = LCARSLabel(Text="OBJECT INSPECTOR // PASSPORT", FontSize=16)
        InspectorLayout.addWidget(InspHeader.widget)

        self.PassportBlock = LCARSDataBlock(
            Title="PROPERTIES // PASSPORT",
            Data={
                "CLASS": "NONE",
                "LABEL": "NONE",
                "CODE": "NONE",
                "STATE": "NORMAL",
                "WIDTH": "0 PX",
                "HEIGHT": "0 PX",
                "THICK": "—",
                "POS (X, Y)": "0, 0"
            },
            Width=286,
            Height=170,
            FontSize=16
        )
        InspectorLayout.addWidget(self.PassportBlock.widget)

        EditHeader = LCARSLabel(Text="TRANSFORM MATRIX", FontSize=16)
        InspectorLayout.addWidget(EditHeader.widget)

        # Стрілки
        MoveRow = LCARS.Widget()
        MoveRowLayout = LCARS.Horizontal(MoveRow)
        MoveRowLayout.setContentsMargins(0, 0, 0, 0)
        MoveRowLayout.setSpacing(2)
        BtnMoveLeft = LCARSButton(Text="◄", Form=LCARSButton.SoftHalf, Direction=180, Height=36, FontSize=16)
        BtnMoveLeft.Clicked.Connect(lambda data: self.MoveActive(-10, 0))
        BtnMoveUp = LCARSButton(Text="▲", Form=LCARSButton.Rect, Height=36, FontSize=16)
        BtnMoveUp.Clicked.Connect(lambda data: self.MoveActive(0, -10))
        BtnMoveDown = LCARSButton(Text="▼", Form=LCARSButton.Rect, Height=36, FontSize=16)
        BtnMoveDown.Clicked.Connect(lambda data: self.MoveActive(0, 10))
        BtnMoveRight = LCARSButton(Text="►", Form=LCARSButton.SoftHalf, Direction=0, Height=36, FontSize=16)
        BtnMoveRight.Clicked.Connect(lambda data: self.MoveActive(10, 0))
        MoveRowLayout.addWidget(BtnMoveLeft.widget, 1)
        MoveRowLayout.addWidget(BtnMoveUp.widget, 1)
        MoveRowLayout.addWidget(BtnMoveDown.widget, 1)
        MoveRowLayout.addWidget(BtnMoveRight.widget, 1)
        InspectorLayout.addWidget(MoveRow)

        # Розміри
        SizeRow = LCARS.Widget()
        SizeRowLayout = LCARS.Horizontal(SizeRow)
        SizeRowLayout.setContentsMargins(0, 0, 0, 0)
        SizeRowLayout.setSpacing(3)
        BtnWMinus = LCARSButton(Text="W-", Form=LCARSButton.SoftHalf, Direction=180, Height=36, FontSize=16)
        BtnWMinus.Clicked.Connect(lambda data: self.ResizeActive(-15, 0))
        BtnWPlus = LCARSButton(Text="W+", Form=LCARSButton.SoftHalf, Direction=0, Height=36, FontSize=16)
        BtnWPlus.Clicked.Connect(lambda data: self.ResizeActive(15, 0))
        BtnHMinus = LCARSButton(Text="H-", Form=LCARSButton.SoftHalf, Direction=180, Height=36, FontSize=16)
        BtnHMinus.Clicked.Connect(lambda data: self.ResizeActive(0, -6))
        BtnHPlus = LCARSButton(Text="H+", Form=LCARSButton.SoftHalf, Direction=0, Height=36, FontSize=16)
        BtnHPlus.Clicked.Connect(lambda data: self.ResizeActive(0, 6))
        SizeRowLayout.addWidget(BtnWMinus.widget, 1)
        SizeRowLayout.addWidget(BtnWPlus.widget, 1)
        SizeRowLayout.addWidget(BtnHMinus.widget, 1)
        SizeRowLayout.addWidget(BtnHPlus.widget, 1)
        InspectorLayout.addWidget(SizeRow)

        # Товщина Elbow
        ThickRow = LCARS.Widget()
        ThickRowLayout = LCARS.Horizontal(ThickRow)
        ThickRowLayout.setContentsMargins(0, 0, 0, 0)
        ThickRowLayout.setSpacing(3)
        BtnThickMinus = LCARSButton(Text="TH-", Form=LCARSButton.SoftHalf, Direction=180, Height=36, FontSize=16)
        BtnThickMinus.Clicked.Connect(lambda data: self.AdjustThickness(-4))
        BtnThickPlus = LCARSButton(Text="TH+", Form=LCARSButton.SoftHalf, Direction=0, Height=36, FontSize=16)
        BtnThickPlus.Clicked.Connect(lambda data: self.AdjustThickness(4))
        ThickRowLayout.addWidget(BtnThickMinus.widget, 1)
        ThickRowLayout.addWidget(BtnThickPlus.widget, 1)
        InspectorLayout.addWidget(ThickRow)
        
        RadRow = LCARS.Widget()
        RadRowLayout = LCARS.Horizontal(RadRow)
        RadRowLayout.setContentsMargins(0, 0, 0, 0)
        RadRowLayout.setSpacing(3)
        BtnRadMinus = LCARSButton(Text="RAD-", Form=LCARSButton.SoftHalf, Direction=180, Height=36, FontSize=16)
        BtnRadMinus.Clicked.Connect(lambda data: self.AdjustRadius(-4))
        BtnRadPlus = LCARSButton(Text="RAD+", Form=LCARSButton.SoftHalf, Direction=0, Height=36, FontSize=16)
        BtnRadPlus.Clicked.Connect(lambda data: self.AdjustRadius(4))
        RadRowLayout.addWidget(BtnRadMinus.widget, 1)
        RadRowLayout.addWidget(BtnRadPlus.widget, 1)
        InspectorLayout.addWidget(RadRow)

        # Форма та стан
        CycleRow = LCARS.Widget()
        CycleRowLayout = LCARS.Horizontal(CycleRow)
        CycleRowLayout.setContentsMargins(0, 0, 0, 0)
        CycleRowLayout.setSpacing(3)
        BtnFormCycle = LCARSButton(Text="FORM", Form=LCARSButton.Rect, Height=36, FontSize=16)
        BtnFormCycle.Clicked.Connect(lambda data: self.CycleFormActive())
        BtnStateCycle = LCARSButton(Text="STATE", Form=LCARSButton.Rect, Height=36, FontSize=16)
        BtnStateCycle.Clicked.Connect(lambda data: self.CycleStateActive())
        CycleRowLayout.addWidget(BtnFormCycle.widget, 1)
        CycleRowLayout.addWidget(BtnStateCycle.widget, 1)
        InspectorLayout.addWidget(CycleRow)
        
        # TEXT EDIT
        InspectorLayout.addSpacing(6)
        InspectorLayout.addWidget(LCARSLabel(Text="COMPONENT TEXT", FontSize=16).widget)
        
        TextEditRow = LCARS.Widget()
        TextEditLayout = LCARS.Horizontal(TextEditRow)
        TextEditLayout.setContentsMargins(0, 0, 0, 0)
        TextEditLayout.setSpacing(3)
        
        self.TextInput = LCARS.LineEdit()
        self.TextInput.setStyleSheet("background: #222; color: #fc9; font-size: 16px; border: 1px solid #fc9; border-radius: 4px; padding: 4px;")
        
        BtnApplyText = LCARSButton(Text="SET", Form=LCARSButton.SoftHalf, Direction=0, Width=60, Height=32, FontSize=16)
        BtnApplyText.Clicked.Connect(lambda data: self.ApplyText())
        
        TextEditLayout.addWidget(self.TextInput, 1)
        TextEditLayout.addWidget(BtnApplyText.widget)
        
        InspectorLayout.addWidget(TextEditRow)


        # Клон і видалення
        ActionRow = LCARS.Widget()
        ActionRowLayout = LCARS.Horizontal(ActionRow)
        ActionRowLayout.setContentsMargins(0, 0, 0, 0)
        ActionRowLayout.setSpacing(3)
        BtnDuplicate = LCARSButton(Text="COPY", Form=LCARSButton.PillHalf, Direction=180, Height=36, FontSize=16)
        BtnDuplicate.Clicked.Connect(lambda data: self.DuplicateActive())
        BtnDelete = LCARSButton(Text="DELETE", Form=LCARSButton.PillHalf, Direction=0, State=LCARSButton.ALERT, Height=36, FontSize=16)
        BtnDelete.Clicked.Connect(lambda data: self.Canvas.Remove(self.Canvas.Selected))
        ActionRowLayout.addWidget(BtnDuplicate.widget, 1)
        ActionRowLayout.addWidget(BtnDelete.widget, 1)
        InspectorLayout.addWidget(ActionRow)

        # Генератор коду
        self.CodeBlock = LCARSDataBlock(
            Title="PYTHON CODE GENERATOR",
            Data={
                "CALL": "# SELECT OBJECT",
                "PARAMS": "# TO GENERATE CODE",
                "STATE": ""
            },
            Width=286,
            Height=110,
            FontSize=16
        )
        InspectorLayout.addWidget(self.CodeBlock.widget)

        InspectorLayout.addStretch()
        WorkSpaceLayout.addWidget(self.Inspector)

        MainLayout.addWidget(WorkSpace, 1)

        # ─────────────────────────────────────────────────────────────────────
        # 3. НИЖНІЙ СПРАВЖНІЙ ТЕРМІНАЛ БОРТОВОГО КОМП'ЮТЕРА (LCARSTerminal)
        # ─────────────────────────────────────────────────────────────────────
        self.TerminalHost = LCARS.Widget()
        TerminalHostLayout = LCARS.Vertical(self.TerminalHost)
        TerminalHostLayout.setContentsMargins(0, 0, 0, 0)
        TerminalHostLayout.setSpacing(0)
        self.TerminalHost.setFixedHeight(270)
        SetStyle(self.TerminalHost, "background-color: #000000; border: none;")

        # Вбудований повнофункціональний LCARSTerminal
        self.TerminalInstance = LCARSTerminal(
            ParentNode=self.TerminalHost,
            BoardComputer=self.BoardComputer,
            Decorated=False
        )
        TerminalHostLayout.addWidget(self.TerminalInstance.widget)
        MainLayout.addWidget(self.TerminalHost)

        # Додаємо весь робочий стіл у PADD
        self.Padd.Add(MainContainer)

        # Стартова схема
        self.LoadPreset()

    # ─────────────────────────────────────────────────────────────────────────
    # ПЕРЕМИКАННЯ ВИСУВНИХ ПАНЕЛЕЙ (OVERLAY SLIDERS)
    # ─────────────────────────────────────────────────────────────────────────
    def ToggleCatalog(self):
        IsHidden = self.Sidebar.isHidden()
        self.Sidebar.setVisible(IsHidden)
        if hasattr(self.TerminalInstance, "OnCommandOutput"):
            self.TerminalInstance.OnCommandOutput(f"LCARS: Catalog Panel {'OPENED' if IsHidden else 'HIDDEN'}")

    def ToggleInspector(self):
        IsHidden = self.Inspector.isHidden()
        self.Inspector.setVisible(IsHidden)
        if hasattr(self.TerminalInstance, "OnCommandOutput"):
            self.TerminalInstance.OnCommandOutput(f"LCARS: Inspector Panel {'OPENED' if IsHidden else 'HIDDEN'}")

    def ToggleTerminal(self):
        IsHidden = self.TerminalHost.isHidden()
        self.TerminalHost.setVisible(IsHidden)

    def ToggleEditMode(self):
        self.Canvas.EditMode = not self.Canvas.EditMode
        StatusText = "EDIT (HANDLES ON)" if self.Canvas.EditMode else "VIEW (HANDLES OFF)"
        self.BtnModeToggle.SetText(f"MODE: {'EDIT' if self.Canvas.EditMode else 'VIEW'}")
        self.Canvas.SyncHandles()
        self.Canvas.update()

    def LoadPreset(self):
        self.Canvas.Clear()
        e1 = self.Canvas.Spawn(LCARSElbow, Direction="top-left", Text="NAVIGATION DECK", Number="01-NAV", Width=340, Height=60, Thickness=26, Radius=20, FontSize=16, X=40, Y=30)
        b1 = self.Canvas.Spawn(LCARSBar, Width=360, Height=16, X=390, Y=30)
        btn1 = self.Canvas.Spawn(LCARSButton, Text="WARP ENGAGE", Form=LCARSButton.Pill, Number="47-1001", Width=200, Height=44, FontSize=16, X=40, Y=110)
        btn2 = self.Canvas.Spawn(LCARSButton, Text="IMPULSE", Form=LCARSButton.Soft, Number="47-1002", Width=200, Height=44, FontSize=16, X=250, Y=110)
        btn3 = self.Canvas.Spawn(LCARSButton, Text="SUBSPACE ODN", Form=LCARSButton.Rect, Number="47-1003", Width=200, Height=44, FontSize=16, X=460, Y=110)
        arm = self.Canvas.Spawn(LCARSButton, Text="ARM / AUTH", Form=LCARSButton.PillHalf, Direction=180, Number="99-ARM", State=LCARSButton.YELLOW, Width=180, Height=44, FontSize=16, X=40, Y=170)
        exec_btn = self.Canvas.Spawn(LCARSButton, Text="EXECUTE", Form=LCARSButton.PillHalf, Direction=0, Number="99-EXEC", State=LCARSButton.ALERT, Width=180, Height=44, FontSize=16, X=224, Y=170)
        data = self.Canvas.Spawn(LCARSDataBlock, Title="PRIMARY ODN STATUS", Data={"CORE": "ONLINE", "WARP": "9.975"}, Width=364, Height=110, FontSize=16, X=40, Y=230)
        self.Canvas.Select(e1)

    def UpdateInspector(self):
        Item = self.Canvas.Selected
        if not Item or not getattr(Item, "widget", None):
            self.PassportBlock.SetData({
                "CLASS": "NONE",
                "LABEL": "NONE",
                "CODE": "NONE",
                "STATE": "NORMAL",
                "WIDTH": "0 PX",
                "HEIGHT": "0 PX",
                "THICK": "—",
                "POS (X, Y)": "0, 0"
            })
            self.CodeBlock.SetData({
                "CALL": "# SELECT OBJECT",
                "PARAMS": "# TO GENERATE CODE",
                "STATE": ""
            })
            return

        W = Item.widget
        ClassName = Item.__class__.__name__
        FormVal = getattr(Item, "Form", "RECT")
        FormName = "RECT" if FormVal == LCARSButton.Rect else ("PILL" if FormVal == LCARSButton.Pill else ("SOFT" if FormVal == LCARSButton.Soft else ("PILL-HALF" if FormVal == LCARSButton.PillHalf else ("SOFT-HALF" if FormVal == LCARSButton.SoftHalf else str(FormVal)))))
        TextVal = str(getattr(Item, "Text", "") or "—")
        NumVal = str(getattr(Item, "Number", "") or "—")
        StateVal = str(getattr(Item, "State", "normal")).upper()
        ThickVal = f"{getattr(Item, 'Thickness', '—')} PX" if hasattr(Item, "Thickness") else "—"
        PosX = W.x()
        PosY = W.y()
        WidthVal = W.width()
        HeightVal = W.height()

        if hasattr(self, "TextInput"):
            self.TextInput.setText(TextVal)
            
        self.PassportBlock.SetData({
            "CLASS": ClassName,
            "FORM": FormName,
            "LABEL": TextVal,
            "CODE": NumVal,
            "STATE": StateVal,
            "WIDTH": f"{WidthVal} PX",
            "HEIGHT": f"{HeightVal} PX",
            "THICK": ThickVal,
            "POS (X, Y)": f"{PosX}, {PosY}"
        })

        if isinstance(Item, LCARSElbow):
            self.CodeBlock.SetData({
                "CALL": f"LCARSElbow(Text='{TextVal}',",
                "PARAMS": f"W={WidthVal}, H={HeightVal}, Thickness={getattr(Item, 'Thickness', 26)},",
                "STATE": f"Direction='{getattr(Item, 'Direction', 'top-left')}', FontSize=16)"
            })
        else:
            self.CodeBlock.SetData({
                "CALL": f"{ClassName}(Text='{TextVal}',",
                "PARAMS": f"Form={FormName}, W={WidthVal}, H={HeightVal},",
                "STATE": f"State=LCARSButton.{StateVal}, FontSize=16)"
            })

    def MoveActive(self, DX: int, DY: int):
        Item = self.Canvas.Selected
        if not Item or not getattr(Item, "widget", None):
            return
        W = Item.widget
        W.move(max(0, self.Canvas.Snap(W.x() + DX)), max(0, self.Canvas.Snap(W.y() + DY)))
        self.Canvas.SyncHandles()
        self.UpdateInspector()
        self.Canvas.update()

    def ResizeActive(self, DW: int, DH: int):
        Item = self.Canvas.Selected
        if not Item or not getattr(Item, "widget", None):
            return
        W = Item.widget
        NewW = max(40, W.width() + DW)
        NewH = max(20, W.height() + DH)
        W.setFixedSize(NewW, NewH)
        Item.Width = NewW
        Item.Height = NewH
        if hasattr(Item, "Update"):
            Item.Update()
        self.Canvas.SyncHandles()
        self.UpdateInspector()
        self.Canvas.update()

    def AdjustThickness(self, Delta: int):
        Item = self.Canvas.Selected
        if not Item or not hasattr(Item, "Thickness"):
            return
        CurTh = int(getattr(Item, "Thickness", 26))
        Item.Thickness = max(10, min(140, CurTh + Delta))
        if hasattr(Item, "Update"):
            Item.Update()
        self.Canvas.SyncHandles()
        self.UpdateInspector()
        self.Canvas.update()

    def ApplyText(self):
        Item = self.Canvas.Selected
        if not Item: return
        new_text = self.TextInput.text()
        if hasattr(Item, "Text"):
            Item.Text = new_text
            Item.SetText(new_text)
        self.UpdateInspector()
        self.Canvas.update()

    def CycleDirectionActive(self):
        Item = self.Canvas.Selected
        if not Item:
            return
        if hasattr(Item, "Direction"):
            if isinstance(Item.Direction, str):
                dirs = ["top-left", "top-right", "bottom-right", "bottom-left"]
                try:
                    idx = dirs.index(str(Item.Direction).lower())
                except:
                    idx = 0
                Item.Direction = dirs[(idx + 1) % len(dirs)]
            else:
                Item.Direction = (int(Item.Direction) + 90) % 360
            self.UpdateInspector()
            self.Canvas.update()

    def CycleFormActive(self):
        Item = self.Canvas.Selected
        if not Item or not hasattr(Item, "Form"):
            return
        Forms = [LCARSButton.Rect, LCARSButton.Pill, LCARSButton.Soft, LCARSButton.PillHalf, LCARSButton.SoftHalf]
        Current = getattr(Item, "Form", LCARSButton.Rect)
        Idx = Forms.index(Current) if Current in Forms else 0
        Item.Form = Forms[(Idx + 1) % len(Forms)]
        if hasattr(Item, "Update"):
            Item.Update()
        self.UpdateInspector()
        self.Canvas.update()

    def CycleStateActive(self):
        Item = self.Canvas.Selected
        if not Item or not hasattr(Item, "State"):
            return
        States = [LCARSButton.NORMAL, LCARSButton.YELLOW, LCARSButton.ALERT, LCARSButton.DISABLED]
        Current = getattr(Item, "State", LCARSButton.NORMAL)
        Idx = States.index(Current) if Current in States else 0
        Item.SetState(States[(Idx + 1) % len(States)])
        self.UpdateInspector()
        self.Canvas.update()

    def DuplicateActive(self):
        Item = self.Canvas.Selected
        if not Item or not getattr(Item, "widget", None):
            return
        ClassType = Item.__class__
        W = Item.widget
        NewItem = self.Canvas.Spawn(
            ClassType,
            Text=getattr(Item, "Text", "COPY"),
            Form=getattr(Item, "Form", LCARSButton.Pill),
            Direction=getattr(Item, "Direction", 0),
            Number=f"CP-{len(self.Canvas.Components):02d}",
            State=getattr(Item, "State", LCARSButton.NORMAL),
            Thickness=getattr(Item, "Thickness", 26),
            FontSize=16,
            Width=W.width(),
            Height=W.height(),
            X=W.x() + 20,
            Y=W.y() + 20
        )
        self.Canvas.Select(NewItem)

    def Run(self):
        self.Padd.show()
        return self.App.exec()


def RunDesigner():
    Designer = InteractiveWorkbench()
    return Designer.Run()

LCARS.Launch(RunDesigner)
