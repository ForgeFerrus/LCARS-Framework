# LCARS FRAMEWORK
# Готові елементи та канонічні композиції LCARS (Michael Okuda Standard).
# У component.py лежать фізичні примітиви. Тут лежить віртуальний контейнер/оркестратор Element
# та канонічні складені об'єкти інтерфейсу зорельота за векторними кресленнями CorelDRAW.
from typing import Any, Optional, Dict, List, Union, Tuple

from lcars.base.component import (
    Component,
    LCARSBar,
    LCARSButton,
    LCARSElbow,
    LCARSIndicator,
    LCARSLabel,
)
from lcars.base.graphic import Visual, Emitter
from lcars.base.default import DefaultBackground, Palette
from lcars.base.type import LCARS
from lcars.core.signal import ODN
# =============================================================================
# 5. СЕНСОРНА ОПТИЧНА ПОВЕРХНЯ LCARS (SURFACE / PANEL / WIDGET)
Display: type = LCARS.Retrieve(LCARS.Display) or object
# =============================================================================
class Surface(Display):
    TypeName = "LCARSWidget"
    Optics = None
    Layers = []
    PulseTimer = None
    # Канонічна ініціалізація консольного скла
    Initialize = LCARS.Init
    def Initialize(self, Optics=None, Parent=None, **kwargs):
        if Display is not object:
            super().Initialize(Parent)
        self.Optics = Optics
        self.Layers = kwargs.get("Layers", [])
    # Калібрування фізичних параметрів скла
        if hasattr(self, "setMinimumSize"):
            self.setMinimumSize(1, 1)
        Policy = getattr(LCARS, "Policy", None)
        if hasattr(self, "setSizePolicy") and Policy is not None and hasattr(Policy, "Preferred"):
            self.setSizePolicy(Policy.Preferred, Policy.Preferred)
        CursorHand = getattr(LCARS, "CursorHand", None)
        if hasattr(self, "setCursor") and CursorHand is not None:
            self.setCursor(CursorHand)
        # Реєстрація квантового пульсара для динамічних станів
        if hasattr(self, "startTimer"):
            self.PulseTimer = self.startTimer(1000)
    # Пульсація стану поверхні
    def Pulse(self):
        if not self.Optics:
            return
        if not getattr(self.Optics, "Spectrum", getattr(self.Optics, "Color", None)):
            self.update()
    # Рекомендований розмір поверхні для систем компонування
    def PreferredSize(self):
        Node = self.Visual
        W = getattr(Node, "Width", 100) if Node is not None else 100
        H = getattr(Node, "Height", 30) if Node is not None else 30
        SizeClass = LCARS.Geometry.Size
        return SizeClass(max(10, W), max(10, H))
    # Просторове вирівнювання сенсорного поля
    def AlignContent(self, Flag):
        if hasattr(self.Visual, "Align"):
            self.Visual.Align = "center" if "Center" in str(Flag) else ("right" if "Right" in str(Flag) else "left")
        self.update()
        return self
    # Зміна фізичної геометрії сенсорного скла
    def Rescale(self, Event):
        if self.Visual is not None:
            self.Visual.Width = self.width()
            self.Visual.Height = self.height()
            if hasattr(self.Visual, "Synthesize"):
                self.Visual.Synthesize
            elif hasattr(self.Visual, "Generate"):
                self.Visual.Generate
        ParentResize = getattr(super(), "Rescale", None)
        if callable(ParentResize):
            ParentResize(Event)
    # Цикл оптичного світіння (прояв фотонного поля на поверхні)
    def OpticalDispersion(self, Event):
        # Малює свій Optics / Graphic
        if self.Visual is None:
            return
        # Синхронізація просторових меж
        CurrentW = self.width()
        CurrentH = self.height()
        if getattr(self.Visual, "Width", 0) != CurrentW or getattr(self.Visual, "Height", 0) != CurrentH:
            self.Visual.Width = CurrentW
            self.Visual.Height = CurrentH
            if hasattr(self.Visual, "Synthesize"):
                self.Visual.Synthesize
        # Випромінення через єдиний оптичний проєктор LCARS
        ProjectorInstance = Emitter()

        if ProjectorInstance.Activate(self):
            # Проєктор бере self.Visual і малює його на підкладці
            ProjectorInstance.Project(self.Visual)
            ProjectorInstance.Deactivate()
    # Сенсорний контакт (натискання на скло)
    def TouchContact(self, Event):
        ButtonValue = getattr(Event, "button", lambda: 1)()
        IsLeftButton = (
            ButtonValue == 1 or
            "Left" in str(ButtonValue) or
            ButtonValue == getattr(getattr(LCARS, "Protocol", None), "LeftButton", 1)
        )
        if IsLeftButton and self.Graphic is not None:
            TargetEngage = getattr(self.Graphic, "Engage", getattr(self.Graphic, "Trigger", None))
            if callable(TargetEngage):
                TargetEngage()
            if hasattr(self, "isVisible") and self.isVisible():
                self.update()
        ParentMousePress = getattr(super(), "TouchContact", None)
        if callable(ParentMousePress):
            ParentMousePress(Event)
    # Розрив сенсорного контакту (відпускання скла)
    def TouchRelease(self, Event):
        if self.Graphic is not None:
            TargetDisengage = getattr(self.Graphic, "Disengage", getattr(self.Graphic, "Release", None))
            if callable(TargetDisengage):
                TargetDisengage()
            if hasattr(self, "isVisible") and self.isVisible():
                self.update()
        ParentMouseRelease = getattr(super(), "TouchRelease", None)
        if callable(ParentMouseRelease):
            ParentMouseRelease(Event)
    # Датчик наближення (фокус при наведенні курсора або руки)
    def FocusDetection(self, Event):
        if self.Graphic is not None:
            TargetFocus = getattr(self.Graphic, "Focus", None)
            if callable(TargetFocus):
                TargetFocus(True)
            self.update()
        ParentEnter = getattr(super(), "FocusDetection", None)
        if callable(ParentEnter):
            ParentEnter(Event)
    # Вихід із зони наближення
    def Leave(self, Event):
        if self.Graphic is not None:
            TargetFocus = getattr(self.Graphic, "Focus", None)
            if callable(TargetFocus):
                TargetFocus(False)
            self.update()
        ParentLeave = getattr(super(), "leaveEvent", None)
        if callable(ParentLeave):
            ParentLeave(Event)
    # Прив'язка системних подій до графічних методів
    paintEvent = OpticalDispersion
    enterEvent = FocusDetection
    leaveEvent = Leave
    mousePressEvent = TouchContact
    mouseReleaseEvent = TouchRelease
# =====================================================================
# ЕЛЕМЕНТИ ІНТЕРФЕЙСУ — семантичні оркестратори та композиційні вузли
# Базовий клас Element — віртуальна конструкція, що координує фізичні віджети
# =====================================================================
class Element(Component):
    TypeName = "LCARSElement"
    Type = "Element"
    ElementType = "Composite"
    # Склад та просторове розміщення
    Items: Dict[str, Component] = {}
    Spacing = 6.0       # Фірмовий зазор Окуди між компонентами
    Orientation = "horizontal"  # horizontal або vertical
    Title = ""
    ActionText = ""
    # -------------------------------------------------------------------------
    # КОМПОЗИЦІЙНЕ КЕРУВАННЯ (ATTACH / DETACH)
    # -------------------------------------------------------------------------
    def Attach(self, Key: str, ComponentNode: Component):
        if ComponentNode is None:
            return self
        CleanKey = str(Key or getattr(ComponentNode, "Name", "") or id(ComponentNode))
        self.Items[CleanKey] = ComponentNode
        ComponentNode.Parent = self
        # Автоматична синхронізація енергетичного та тривожного стану
        ComponentNode.Power = self.Power
        ComponentNode.Locked = self.Locked
        ComponentNode.State = self.State
        self.Synthesize()
        self.Refresh()
        return self

    def Detach(self, Key: str):
        if Key in self.Items:
            Node = self.Items.pop(Key)
            if getattr(Node, "Parent", None) is self:
                Node.Parent = None
            self.Synthesize()
            self.Refresh()
        return self

    def Clear(self):
        for Node in self.Items.values():
            if getattr(Node, "Parent", None) is self:
                Node.Parent = None
        self.Items.clear()
        self.Synthesize()
        self.Refresh()
        return self
        
    def Item(self, Key: str) -> Component | None:
        return self.Items.get(Key)
    Item = LCARS.GetItem

    # Додає новий компонент або лейаут у композицію
    def Add(self, *Arguments):
        if not Arguments:
            return self

        if self.Layout is None:
            if hasattr(self.Widget, "layout") and self.Widget.layout() is not None:
                self.Layout = self.Widget.layout()
            else:
                self.Vertical(0, 0, 0, 0, 0)

        TargetLayout = self.Layout
        Item = Arguments[0]
        Stretch = None

        if len(Arguments) == 1:
            Item = Arguments[0]
        elif len(Arguments) == 2:
            if hasattr(Arguments[0], "addWidget") or hasattr(Arguments[0], "addLayout"):
                TargetLayout = Arguments[0]
                Item = Arguments[1]
            else:
                Item = Arguments[0]
                Stretch = Arguments[1]
        elif len(Arguments) >= 3:
            TargetLayout = Arguments[0]
            Item = Arguments[1]
            Stretch = Arguments[2]

        if Item is None or TargetLayout is None:
            return self

        TargetWidget = getattr(Item, "Widget", getattr(Item, "widget", Item))
        if hasattr(TargetLayout, "addWidget") and (not hasattr(Item, "addWidget") or TargetWidget is not Item):
            if Stretch is None:
                TargetLayout.addWidget(TargetWidget)
            else:
                TargetLayout.addWidget(TargetWidget, int(Stretch))
        elif hasattr(TargetLayout, "addLayout"):
            SubLayout = getattr(Item, "Layout", Item)
            TargetLayout.addLayout(SubLayout)
        return self
    # 
    def SetVertical(self, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        LayoutClass = LCARS.Retrieve("Base.Interface.Layout.Vertical")
        if LayoutClass and callable(LayoutClass):
            TargetWidget = getattr(self, "Widget", getattr(self, "widget", None))
            self.Layout = LayoutClass(TargetWidget)
            if hasattr(self.Layout, "setContentsMargins"):
                self.Layout.setContentsMargins(Left, Top, Right, Bottom)
            if hasattr(self.Layout, "setSpacing"):
                self.Layout.setSpacing(Spacing)
        return self.Layout
    # 
    def SetHorizontal(self, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        LayoutClass = LCARS.Retrieve("Base.Interface.Layout.Horizontal")
        if LayoutClass and callable(LayoutClass):
            TargetWidget = getattr(self, "Widget", getattr(self, "widget", None))
            self.Layout = LayoutClass(TargetWidget)
            if hasattr(self.Layout, "setContentsMargins"):
                self.Layout.setContentsMargins(Left, Top, Right, Bottom)
            if hasattr(self.Layout, "setSpacing"):
                self.Layout.setSpacing(Spacing)
        return self.Layout
    # Додає гнучку прокладку (стретч)
    def AddStretch(self, TargetLayout=None, Factor=1):
        LayoutObj = TargetLayout or self.Layout
        if LayoutObj is not None and hasattr(LayoutObj, "addStretch"):
            LayoutObj.addStretch(int(Factor))
        return self
    # -------------------------------------------------------------------------
    # СИНТЕЗ КОМПОЗИТНОГО ВУЗЛА (ПРОСТОРОВИЙ РОЗРАХУНОК)
    # Розставляє дочірні компоненти вздовж лінії або в блок
    # -------------------------------------------------------------------------
    def Synthesize(self):
        CurX = 0.0
        CurY = 0.0
        TotalW = 0.0
        TotalH = 0.0
        for Node in self.Items.values():
            if not hasattr(Node, "Width") or not hasattr(Node, "Height"):
                continue
            # Задаємо локальні координати компонента
            Node.X = int(CurX)
            Node.Y = int(CurY)
            if hasattr(Node, "Synthesize"):
                Node.Synthesize()
            if self.Orientation == "horizontal":
                CurX += float(Node.Width) + self.Spacing
                TotalW = CurX
                TotalH = max(TotalH, float(Node.Height))
            else:
                CurY += float(Node.Height) + self.Spacing
                TotalH = CurY
                TotalW = max(TotalW, float(Node.Width))
        # Оновлюємо габарити всього елемента
        if self.Items:
            self.Width = int(TotalW)
            self.Height = int(TotalH)
        return self.BuildInterface()

    def BuildInterface(self):
        TargetType = (self.Type).lower()
        if TargetType == "padd":
            return self.BuildPadd()
        elif TargetType == "screen":
            return self.BuildScreen()
        elif TargetType == "segment":
            return self.BuildSegment()
        elif TargetType in ("header", "headerframe"):
            return self.BuildHeader()
        elif TargetType == "footer":
            return self.BuildFooter()
        elif TargetType == "sidebar":
            return self.BuildSidebar()
        elif TargetType == "menu":
            return self.BuildMenu()
        elif TargetType == "toolbar":
            return self.BuildToolbar()
        elif TargetType == "statusline":
            return self.BuildStatusLine()
        elif TargetType == "datablock":
            return self.BuildDataBlock()
        elif TargetType == "statbar":
            return self.BuildStatBar()
        elif TargetType == "scanningbar":
            return self.BuildScanningBar()
        elif TargetType == "overlay":
            return self.BuildOverlay()
        elif TargetType == "stasis":
            return self.BuildStasis()
        elif TargetType in ("access", "accesscode"):
            return self.BuildAccess()
        elif TargetType in ("coupled", "coupledblock"):
            return self.BuildCoupled()
        elif TargetType in ("telemetry", "telemetryblock"):
            return self.BuildTelemetry()
        elif TargetType in ("bracket", "framebracket"):
            return self.BuildBracket()
        return self.BuildPanel()
# =============================================================================
# HEADER — ВЕРХНЯ КОМПОЗИЦІЯ / ШАПКА ПАНЕЛІ ТЕРМІНАЛА
# Підтримує всі варіації несучих арок Окуди
# =============================================================================
class Header(Element):
    TypeName = "Header"
    Type = "Header"

    # --- ВАРІАЦІЇ ФОРМИ ШАПКИ ---
    ElbowLeft = 1       # Класична: лікоть зліва, напис, шина, кінцевик справа
    ElbowRight = 2      # Дзеркальна: кінцевик зліва, шина, напис, лікоть справа
    DoubleElbow = 3     # Подвійна арка: лікті з обох боків
    PillCap = 4         # Без ліктя: пряма шина із закругленими краями

    # Варіації розміщення
    ElbowLeft = 1
    ElbowRight = 2
    DoubleElbow = 3
    PillCap = 4
    # Композиції арок
    def Compose(self, *Objects, Form=ElbowLeft):
        self.Clear()
        
        # 1. Якщо передали готові об'єкти списком — компонуємо їх по порядку
        if Objects:
            for Obj in Objects:
                # Якщо це балка (Bar) — даємо їй розтягнення Stretch=1
                if getattr(Obj, "Type", "") == "Bar" or "Bar" in type(Obj).__name__:
                    self.Add(Obj, 1)
                else:
                    self.Add(Obj)
            return self
        return self
# =============================================================================
# FOOTER — НИЖНЯ КОМПОЗИЦІЯ / ПІДВАЛ ПАНЕЛІ ТЕРМІНАЛА
# =============================================================================
# =============================================================================
# FOOTER — НИЖНЯ КОМПОЗИЦІЯ / ПІДВАЛ ТЕРМІНАЛА
# Універсальне компонування готових об'єктів нижнього горизонту
# =============================================================================
class Footer(Element):
    TypeName = "Footer"
    Type = "Footer"

    Height = 36
    Thickness = 16

    def Compose(self, *Objects):
        self.Clear()
        self.SetHorizontal(0, 0, 0, 0, Spacing=6)

        if Objects:
            for Obj in Objects:
                # Балка автоматично розтягується на всю ширину
                if getattr(Obj, "Type", "") == "Bar" or "Bar" in type(Obj).__name__:
                    self.Add(Obj, 1)
                else:
                    self.Add(Obj)
        return self
# =============================================================================
# SIDEBAR — ВЕРТИКАЛЬНА БІЧНА КОЛОНА НАВІГАЦІЇ
# Компонує кнопки, індикатори та розділювачі у вертикальний стек
# =============================================================================
class Sidebar(Element):
    TypeName = "Sidebar"
    Type = "Sidebar"

    Width = 160
    Spacing = 6

    def Compose(self, *Objects, Align="top"):
        self.Clear()
        # Встановлюємо вертикальний лейаут для бічної колони
        LayoutRef = self.SetVertical(0, 0, 0, 0, Spacing=self.Spacing)

        # Якщо вирівнювання знизу — додаємо пружину на початку
        if Align == "bottom":
            self.AddStretch(LayoutRef, 1)

        for Obj in Objects:
            # Якщо передано ціле число або рядок "stretch" — це пружина
            if isinstance(Obj, int):
                self.AddStretch(LayoutRef, Obj)
            else:
                self.Add(Obj)

        # За замовчуванням притискаємо все догори (додаємо пружину внизу)
        if Align == "top":
            self.AddStretch(LayoutRef, 1)
        return self
# =============================================================================
# BRACKET — СКОБА / РАМКА РОБОЧОГО ВІДСІКУ LCARS
# Обмежує зону даних або екрану. Варіації: OpenRight, OpenLeft, Box
# =============================================================================
class Bracket(Element):
    TypeName = "Bracket"
    Type = "Bracket"

    # --- ВАРІАЦІЇ СКОБИ ---
    OpenRight = 1       # С-подібна скоба зліва (відкрита праворуч)
    OpenLeft = 2        # С-подібна скоба справа (відкрита ліворуч)
    Box = 3             # Повна замкнена рамка

    Form = OpenRight
    Thickness = 18
    Radius = 24

    def Compose(self, TopElbow=None, Pillar=None, BottomElbow=None, Content=None):
        self.Clear()
        # Встановлюємо горизонтальний лейаут: [Колона-скоба | Вміст]
        MainLayout = self.SetHorizontal(0, 0, 0, 0, Spacing=8)

        # 1. Створюємо бічну С-подібну колону
        SidebarCol = Element()
        ColLayout = SidebarCol.SetVertical(0, 0, 0, 0, Spacing=4)

        if TopElbow is not None:
            SidebarCol.Add(TopElbow)

        if Pillar is not None:
            # Центральна колона розтягується на всю висоту вмісту
            SidebarCol.Add(Pillar, 1)

        if BottomElbow is not None:
            SidebarCol.Add(BottomElbow)

        # Розміщуємо залежно від орієнтації OpenRight чи OpenLeft
        if self.Form == self.OpenLeft:
            if Content is not None:
                self.Add(Content, 1)
            self.Add(SidebarCol)
        else:  # OpenRight (за замовчуванням)
            self.Add(SidebarCol)
            if Content is not None:
                self.Add(Content, 1)

        return self
# =============================================================================
# DATABLOCK — ІНФОРМАЦІЙНИЙ БЛОК ДАНИХ ТА ТЕЛЕМЕТРІЇ
# Відображає назву, значення або пари ключ-значення
# =============================================================================
class DataBlock(Element):
    TypeName = "DataBlock"
    Type = "DataBlock"

    # --- ВАРІАЦІЇ БЛОКУ ---
    Titled = 1          # Заголовок зверху, значення знизу
    KeyValue = 2        # Список параметрів (ключ : значення)
    Coupled = 3         # Здвоєний блок (параметри + дія/кнопка)

    Form = Titled
    Width = 200
    Height = 64

    def Compose(self, Title=None, Value=None, Action=None):
        self.Clear()

        # 1. ТИПОВИЙ БЛОК: ЗАГОЛОВОК ЗВЕРХУ, ЗНАЧЕННЯ ЗНИЗУ
        if self.Form == self.Titled:
            self.SetVertical(4, 4, 4, 4, Spacing=2)
            if Title is not None:
                self.Add(Title)
            if Value is not None:
                self.Add(Value, 1)

        # 2. ЗДВОЄНИЙ БЛОК: ДАНІ ЗЛІВА, КНОПКА ДІЇ СПРАВА
        elif self.Form == self.Coupled:
            self.SetHorizontal(4, 4, 4, 4, Spacing=6)
            
            # Ліва частина (дані)
            DataCol = Element()
            DataCol.SetVertical(0, 0, 0, 0, Spacing=2)
            if Title is not None:
                DataCol.Add(Title)
            if Value is not None:
                DataCol.Add(Value, 1)
            self.Add(DataCol, 1)

            # Права частина (дія/кнопка)
            if Action is not None:
                self.Add(Action)

        # 3. СПИСОК ПАРАМЕТРІВ (KEY-VALUE)
        else:
            self.SetVertical(4, 4, 4, 4, Spacing=4)
            if Title is not None:
                self.Add(Title)
            if Value is not None:
                self.Add(Value)
        return self
                
    def BuildMenu(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.SetVertical(0, 0, 0, 0, 6)
        Labels = self.Value if isinstance(getattr(self, "Value", None), list) else ["SYSTEM", "PROGRAMS", "SETTINGS", "DIAGNOSTICS"]
        Index = 0
        for ItemText in Labels:
            ColorHex = Palette.Buttons[Index % len(Palette.Buttons)]
            Btn = LCARSButton(
                Text=ItemText,
                Form=LCARSButton.SoftHalf,
                Direction=0,
                Color=ColorHex,
                Parent=self.Widget
            )
            self.Items[f"Button{Index}"] = Btn
            self.Add(LayoutRef, Btn)
            Index += 1
        self.AddStretch(LayoutRef)
        return self

    def BuildToolbar(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 6)
        Labels = self.Value if isinstance(getattr(self, "Value", None), list) else ["BACK", "HOME", "NEXT"]
        Index = 0
        for ItemText in Labels:
            ColorHex = Palette.Buttons[Index % len(Palette.Buttons)]
            Btn = LCARSButton(
                Text=ItemText,
                Form=LCARSButton.Pill,
                Color=ColorHex,
                Parent=self.Widget
            )
            self.Items[f"Tool{Index}"] = Btn
            self.Add(LayoutRef, Btn)
            Index += 1
        self.AddStretch(LayoutRef)
        return self

    def BuildStatusLine(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 8)
        StatusText = getattr(self, "Value", None) or "READY"
        self.Items["Status"] = LCARSIndicator(
            Text=StatusText,
            Type="status",
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Items["Bar"] = LCARSBar(
            Type="divider",
            Height=4,
            Color=Palette.Buttons[1],
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Status"])
        self.Add(LayoutRef, self.Items["Bar"], 1)
        return self

    def BuildDataBlock(self):
        ColorHex = self.Color or Palette.Buttons[1]
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet(f"background-color: #060608; border-left: 4px solid {ColorHex}; border-radius: 4px;")
        LayoutRef = self.Vertical(8, 8, 8, 8, 4)
        
        RawLabel = getattr(self, "LabelText", None) or getattr(self, "Label", "")
        if isinstance(RawLabel, str):
            LabelStr = RawLabel.upper()
        elif hasattr(RawLabel, "Text"):
            LabelStr = str(RawLabel.Text).upper()
        else:
            LabelStr = "DATA"

        RawValue = getattr(self, "ValueText", None) or getattr(self, "Value", "")
        if isinstance(RawValue, (str, int, float)):
            ValueStr = str(RawValue).upper()
        else:
            ValueStr = "--"

        self.Items["Label"] = LCARSLabel(
            Text=LabelStr,
            Color=ColorHex,
            FontSize=13,
            Parent=self.Widget
        )
        self.Items["Value"] = LCARSLabel(
            Text=ValueStr,
            Color="#FFFFFF",
            FontSize=15,
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Label"])
        self.Add(LayoutRef, self.Items["Value"])
        return self

    def BuildStatBar(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: transparent; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 10)
        MaxValue = 100
        Val = int(getattr(self, "Value", 0) or 0)
        LabelStr = str(getattr(self, "LabelText", "") or getattr(self, "Label", "") or "")
        ColorHex = self.Color or Palette.Buttons[1]

        self.Items["Label"] = LCARSIndicator(
            Text=LabelStr,
            Type="label",
            Color=ColorHex,
            Parent=self.Widget
        )
        ProgressClass = getattr(LCARS, "Progress", None)
        if ProgressClass:
            ProgressBarWidget = ProgressClass(self.Widget)
        else:
            ProgressBarWidget = LCARSBar(
                Type="bar",
                Height=12,
                Color=ColorHex,
                Parent=self.Widget
            )
        self.Items["Progress"] = ProgressBarWidget
        if hasattr(ProgressBarWidget, "setObjectName"):
            ProgressBarWidget.setObjectName("LCARSProgress")
        if hasattr(ProgressBarWidget, "setTextVisible"):
            ProgressBarWidget.setTextVisible(False)
        if hasattr(ProgressBarWidget, "setRange"):
            ProgressBarWidget.setRange(0, MaxValue)
        if hasattr(ProgressBarWidget, "setValue"):
            ProgressBarWidget.setValue(Val)
        SetStyle(
            ProgressBarWidget,
            "#LCARSProgress { background: #111111; border: none; border-radius: 6px; }"
            f"#LCARSProgress::chunk {{ background: {ColorHex}; border-radius: 5px; }}",
        )
        self.Add(LayoutRef, self.Items["Label"])
        self.Add(LayoutRef, ProgressBarWidget, 1)
        return self

    def BuildScanningBar(self):
        self.Phase = 0
        ColorHex = self.Color or Palette.Buttons[1]
        self.Scan = LCARSBar(
            Type="scanning",
            Height=15,
            Color=ColorHex,
            Parent=self.Widget
        )
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: transparent; border: none;")
        LayoutRef = self.Vertical(0, 0, 0, 0, 0)
        self.Add(LayoutRef, self.Scan)
        return self

    def BuildOverlay(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: rgba(0, 0, 0, 240);")
        LayoutRef = self.Vertical(40, 40, 40, 40, 12)
        ActionDesc = str(self.ActionText or "").upper()
        self.Items["Title"] = LCARSIndicator(
            "SECURITY CLEARANCE AUTHORIZATION",
            Type="alert",
            Color=Palette.Red[0],
            Parent=self.Widget
        )
        self.Items["Message"] = LCARSIndicator(
            f"CRITICAL ACTION: {ActionDesc}",
            Type="label",
            Color=Palette.Buttons[2],
            Parent=self.Widget
        )
        self.Items["Confirm"] = LCARSButton(
            "AUTHORIZE",
            Color=Palette.Red[0],
            Form=LCARSButton.Pill,
            Parent=self.Widget
        )
        self.Items["Cancel"] = LCARSButton(
            "ABORT",
            Color=Palette.Disabled[0],
            Form=LCARSButton.Pill,
            Parent=self.Widget
        )
        self.Items["Confirm"].Clicked.Connect(self.AuthorizeAction)
        self.Items["Cancel"].Clicked.Connect(self.Cleanup)

        ButtonLayout = self.Horizontal(0, 0, 0, 0, 10)
        self.Add(LayoutRef, self.Items["Title"])
        self.Add(LayoutRef, self.Items["Message"])
        self.AddStretch(LayoutRef)
        self.Add(ButtonLayout, self.Items["Confirm"])
        self.Add(ButtonLayout, self.Items["Cancel"])
        self.AddLayout(LayoutRef, ButtonLayout)
        return self

    def BuildStasis(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Vertical(0, 0, 0, 0, 0)
        self.Items["Label"] = LCARSIndicator(
            "SYSTEM IN STASIS",
            Type="title",
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Label"])
        self.Widget.mousePressEvent = self.TriggerWakeup
        return self

    # Канонічний блок доступу за кресленням CorelDRAW:
    # AccentBar + Label("ACCESS CODE") + Mask("**********") + StatusButton("AUTHORIZED")
    def BuildAccess(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 6)
        TitleText = getattr(self, "Title", "") or "ACCESS CODE"
        MaskCode = getattr(self, "Code", "") or getattr(self, "Value", "") or "**********"
        StatusText = getattr(self, "StatusText", "") or "AUTHORIZED"

        self.Items["Bar"] = LCARSBar(
            Width=8,
            Height=34,
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Items["Title"] = LCARSLabel(
            Text=TitleText,
            Color=Palette.Buttons[2],
            FontSize=14,
            Parent=self.Widget
        )
        self.Items["Mask"] = LCARSLabel(
            Text=MaskCode,
            Color="#FFFFFF",
            FontSize=15,
            Parent=self.Widget
        )
        self.Items["Button"] = LCARSButton(
            Text=StatusText,
            Form=LCARSButton.SoftHalf,
            Direction=0,
            Color=Palette.Buttons[1],
            Height=34,
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Bar"])
        self.Add(LayoutRef, self.Items["Title"])
        self.Add(LayoutRef, self.Items["Mask"])
        self.AddStretch(LayoutRef)
        self.Add(LayoutRef, self.Items["Button"])
        return self

    # Канонічний спарений блок за кресленням CorelDRAW:
    # Button + вузький SuffixBar (зазор 2–4px)
    def BuildCoupled(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: transparent; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 3)
        BtnText = getattr(self, "Text", "") or getattr(self, "Title", "") or "COUPLED"
        BtnNum = getattr(self, "Number", "") or "01"
        BtnForm = getattr(self, "Form", LCARSButton.SoftHalf)
        BtnDir = getattr(self, "Direction", 0)

        self.Items["Button"] = LCARSButton(
            Text=BtnText,
            Number=BtnNum,
            Form=BtnForm,
            Direction=BtnDir,
            Height=getattr(self, "Height", 36),
            Color=self.Color or Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Items["Bar"] = LCARSBar(
            Width=12,
            Height=getattr(self, "Height", 36),
            Color=Palette.Buttons[1],
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Button"], 1)
        self.Add(LayoutRef, self.Items["Bar"])
        return self

    # Канонічний блок телеметрії за кресленням CorelDRAW:
    # Placard + NumberLabel("07") + Terminator
    def BuildTelemetry(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: transparent; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 6)
        TelemetryVal = str(getattr(self, "Value", "") or getattr(self, "Number", "") or "07")
        BadgeText = str(getattr(self, "Badge", "") or getattr(self, "Title", "") or "SEC")

        self.Items["Badge"] = LCARSIndicator(
            Text=BadgeText,
            IndicatorType=LCARSIndicator.PillHalf,
            Direction=180,
            Width=32,
            Height=34,
            Color=Palette.Buttons[2],
            Parent=self.Widget
        )
        self.Items["Number"] = LCARSLabel(
            Text=TelemetryVal,
            FontSize=22,
            Width=52,
            Color="#FFFFFF",
            Parent=self.Widget
        )
        self.Items["Bar"] = LCARSBar(
            Height=12,
            Color=Palette.Buttons[1],
            Parent=self.Widget
        )
        self.Items["Terminator"] = LCARSIndicator(
            IndicatorType=LCARSIndicator.PillHalf,
            Direction=0,
            Width=20,
            Height=34,
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Badge"])
        self.Add(LayoutRef, self.Items["Number"])
        self.Add(LayoutRef, self.Items["Bar"], 1)
        self.Add(LayoutRef, self.Items["Terminator"])
        return self

    # Канонічний каркасний кутник за кресленням CorelDRAW:
    # Elbow + Shelf + SpineRail
    def BuildBracket(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Vertical(0, 0, 0, 0, 4)
        TopRow = Segment(Parent=self.Widget)
        TopRowLayout = TopRow.Horizontal(0, 0, 0, 0, 4)

        self.Items["Elbow"] = LCARSElbow(
            Direction="top-left",
            Width=getattr(self, "Width", 320),
            Height=getattr(self, "Height", 64),
            Thickness=getattr(self, "Thickness", 24),
            Color=self.Color or Palette.Buttons[0],
            Parent=TopRow.Widget
        )
        self.Items["Shelf"] = LCARSBar(
            Height=getattr(self, "Thickness", 24),
            Color=Palette.Buttons[1],
            Parent=TopRow.Widget
        )
        TopRow.Add(TopRowLayout, self.Items["Elbow"])
        TopRow.Add(TopRowLayout, self.Items["Shelf"], 1)

        self.Items["Spine"] = LCARSBar(
            Width=getattr(self, "Thickness", 24),
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Add(LayoutRef, TopRow)
        self.Add(LayoutRef, self.Items["Spine"], 1)
        return self

    def SetValue(self, Value):
        self.Value = Value
        ValueItem = self.Items.get("Value")
        if ValueItem and hasattr(ValueItem, "SetValue"):
            ValueItem.SetValue(Value)
        elif ValueItem and hasattr(ValueItem, "SetText"):
            ValueItem.SetText(str(Value))
        Progress = self.Items.get("Progress")
        if Progress and hasattr(Progress, "setValue"):
            Progress.setValue(int(Value))
        return self

    def SetLabel(self, Label):
        self.Label = str(Label)
        LabelItem = self.Items.get("Label")
        if LabelItem and hasattr(LabelItem, "SetText"):
            LabelItem.SetText(str(Label))
        return self

    def AuthorizeAction(self):
        if self.ConfirmCallback:
            self.ConfirmCallback()
        self.Cleanup()

    def Cleanup(self):
        DeleteMethod = getattr(self.Widget, "deleteLater", None)
        if DeleteMethod:
            DeleteMethod()

    def TriggerWakeup(self, Event):
        WakeUpMethod = getattr(self.Owner, "WakeUp", None)
        if WakeUpMethod:
            WakeUpMethod()

    def SetFixedSize(self, *Args):
        if self.Widget and hasattr(self.Widget, "setFixedSize"):
            self.Widget.setFixedSize(*Args)
        return self

    def SetFixedWidth(self, Width: int):
        if self.Widget and hasattr(self.Widget, "setFixedWidth"):
            self.Widget.setFixedWidth(int(Width))
        return self

    def SetFixedHeight(self, Height: int):
        if self.Widget and hasattr(self.Widget, "setFixedHeight"):
            self.Widget.setFixedHeight(int(Height))
        return self

    def SetVisible(self, VisibleState: bool):
        if self.Widget and hasattr(self.Widget, "setVisible"):
            self.Widget.setVisible(bool(VisibleState))
        self.Visible = bool(VisibleState)
        return self

    def IsVisible(self) -> bool:
        if self.Widget and hasattr(self.Widget, "isVisible"):
            return self.Widget.isVisible()
        return getattr(self, "Visible", True)

    setFixedSize = SetFixedSize
    setFixedWidth = SetFixedWidth
    setFixedHeight = SetFixedHeight
    setVisible = SetVisible
    isVisible = IsVisible

# Побудова канонічної шапки консолі
    def Header(self, TargetWidget, Title="", **kwargs):
        self.Row(TargetWidget, 0, 0, 0, 0, 8)
        self.Items["Elbow"] = Topology(Parent=TargetWidget, Type=Topology.Elbow, Corner="top-left", Spectrum=Palette.Buttons[0])
        self.Items["Title"] = Topology(Parent=TargetWidget, Type=Topology.Text, Designation=Title, Spectrum=Palette.Buttons[2])
        self.Items["Bar"] = Topology(Parent=TargetWidget, Type=Topology.Bar, Spectrum=Palette.Buttons[1])
        return self.Items
    # Побудова канонічного підвалу консолі
    def Footer(self, TargetWidget, Status="READY", **kwargs):
        self.Row(TargetWidget, 0, 0, 0, 0, 8)
        self.Items["Bar"] = Topology(Parent=TargetWidget, Type=Topology.Bar, Spectrum=Palette.Buttons[1])
        self.Items["Status"] = Topology(Parent=TargetWidget, Type=Topology.Text, Designation=Status, Spectrum=Palette.Buttons[0])
        self.Items["Elbow"] = Topology(Parent=TargetWidget, Type=Topology.Elbow, Corner="bottom-right", Spectrum=Palette.Buttons[2])
        return self.Items
    # Побудова канонічної бічної панелі консолі
    def Sidebar(self, TargetWidget, **kwargs):
        self.Column(TargetWidget, 0, 0, 0, 0, 6)
        self.Items["Top"] = Topology(Parent=TargetWidget, Type=Topology.Elbow, Corner="top-left", Spectrum=Palette.Buttons[0])
        self.Items["Rail"] = Topology(Parent=TargetWidget, Type=Topology.Column, Spectrum=Palette.Buttons[1])
        self.Items["Bottom"] = Topology(Parent=TargetWidget, Type=Topology.Elbow, Corner="bottom-left", Spectrum=Palette.Buttons[2])
        return self.Items

# =====================================================================
# PADD — Повнофункціональний екранний термінал зорельота
# =====================================================================
class PADD(Element):
    Type = "PADD"

    def __init__(self, Parent=None, **Args):
        Width = self.Take(Args, ["Width", "width"], 920)
        Height = self.Take(Args, ["Height", "height"], 580)
        MinWidth = self.Take(Args, ["MinWidth", "minWidth"], 1)
        MinHeight = self.Take(Args, ["MinHeight", "minHeight"], 1)
        Portable = self.Take(Args, ["Portable", "portable"], Parent is None)

        super().__init__(
            Parent=Parent,
            **Args
        )

        self.PaddStartWidth = int(Width)
        self.PaddStartHeight = int(Height)
        self.PaddMinWidth = int(MinWidth)
        self.PaddMinHeight = int(MinHeight)
        self.PaddPortable = bool(Portable)

        self.PaddAction = ""
        self.PaddStartGlobal = (0, 0)
        self.PaddStartRect = (0, 0, 0, 0)
        self.PaddOffset = (0, 0)

        self.PaddCurrentWidth = int(Width)
        self.PaddCurrentHeight = int(Height)

        self.PaddFullscreen = False
        self.PaddSavedGeometry = None

        self.Builder = LCARSBuilder(self)
        self.ConfigurePadd()
        self.Build()

    @property
    def Content(self):
        return self.Items.get("Content")

    def Add(self, *Arguments):
        ContentItem = self.Items.get("Content")
        if ContentItem is not None and ContentItem is not self:
            return ContentItem.Add(*Arguments)
        return super().Add(*Arguments)

    def ConfigurePadd(self):
        Host = self.Widget
        if hasattr(Host, "setMinimumSize"):
            Host.setMinimumSize(self.PaddMinWidth, self.PaddMinHeight)
        if hasattr(Host, "setMaximumSize"):
            Host.setMaximumSize(16777215, 16777215)
        if hasattr(Host, "resize"):
            Host.resize(self.PaddStartWidth, self.PaddStartHeight)

        OriginalResize = getattr(Host, "resizeEvent", None)
        PaddSelf = self

        def PaddResizeHook(Event):
            PaddSelf.AdaptPaddGeometry(Event)
            if OriginalResize:
                OriginalResize(Event)
        Host.resizeEvent = PaddResizeHook

        if self.PaddPortable:
            FramelessFlag = getattr(LCARS, "Frameless", None)
            if hasattr(Host, "setWindowFlags") and FramelessFlag is not None:
                Host.setWindowFlags(Host.windowFlags() | FramelessFlag)
            if hasattr(Host, "setStyleSheet"):
                Host.setStyleSheet(f"background-color: #000000; color: {Palette.Buttons[0]};")
            if hasattr(Host, "setSizePolicy"):
                Policy = getattr(LCARS, "Policy", None)
                if Policy:
                    Host.setSizePolicy(Policy.Expanding, Policy.Expanding)
            self.EnablePortablePadd(Host)

    def AdaptPaddGeometry(self, Event):
        Host = self.Widget
        if not Host:
            return
        W = Host.width() if hasattr(Host, "width") else 0
        H = Host.height() if hasattr(Host, "height") else 0
        if W < 1 or H < 1:
            return

        Margin = max(4, min(20, W // 50, H // 50))
        Spacing = max(2, min(8, Margin // 2))

        ContentItem = self.Items.get("Content")
        if ContentItem is not None:
            ContentLayout = getattr(ContentItem, "Layout", None)
            if ContentLayout and hasattr(ContentLayout, "setContentsMargins"):
                ContentLayout.setContentsMargins(Margin, Margin, Margin, Margin)
                ContentLayout.setSpacing(Spacing)

        self.PaddCurrentWidth = W
        self.PaddCurrentHeight = H

    OnPaddResize = AdaptPaddGeometry

    def EnablePortablePadd(self, Host=None):
        Targets = [
            Host,
            self.Items.get("Body"),
        ]
        for Target in Targets:
            TargetWidget = getattr(Target, "Widget", getattr(Target, "widget", Target))
            if TargetWidget is None:
                continue
            TargetWidget.mousePressEvent = self.PaddPress
            TargetWidget.mouseMoveEvent = self.PaddMove
            TargetWidget.mouseReleaseEvent = self.PaddRelease

    def EventGlobal(self, Event):
        Method = getattr(Event, "globalPosition", None)
        if Method:
            Point = Method()
            Convert = getattr(Point, "toPoint", None)
            if Convert:
                Point = Convert()
            return int(Point.x()), int(Point.y())
        Method = getattr(Event, "globalPos", None)
        if Method:
            Point = Method()
            return int(Point.x()), int(Point.y())
        return 0, 0

    def PaddPress(self, Event):
        Host = self.Widget
        GX, GY = self.EventGlobal(Event)
        self.PaddStartGlobal = (GX, GY)
        self.PaddStartRect = (
            int(Host.x()),
            int(Host.y()),
            int(Host.width()),
            int(Host.height()),
        )
        LX = GX - self.PaddStartRect[0]
        LY = GY - self.PaddStartRect[1]
        self.PaddOffset = (LX, LY)
        self.PaddAction = self.PaddEdgeAction(LX, LY)
        AcceptMethod = getattr(Event, "accept", None)
        if AcceptMethod:
            AcceptMethod()

    def PaddMove(self, Event):
        if not self.PaddAction:
            return
        Host = self.Widget
        if not Host:
            return
        GX, GY = self.EventGlobal(Event)
        X, Y, W, H = self.PaddStartRect
        DX = GX - self.PaddStartGlobal[0]
        DY = GY - self.PaddStartGlobal[1]

        if self.PaddAction == "move":
            Host.move(GX - self.PaddOffset[0], GY - self.PaddOffset[1])
            return

        NewX = X
        NewY = Y
        NewW = W
        NewH = H
        if "left" in self.PaddAction:
            NewX = X + DX
            NewW = W - DX
        if "right" in self.PaddAction:
            NewW = W + DX
        if "top" in self.PaddAction:
            NewY = Y + DY
            NewH = H - DY
        if "bottom" in self.PaddAction:
            NewH = H + DY

        if NewW < self.PaddMinWidth:
            if "left" in self.PaddAction:
                NewX -= self.PaddMinWidth - NewW
            NewW = self.PaddMinWidth
        if NewH < self.PaddMinHeight:
            if "top" in self.PaddAction:
                NewY -= self.PaddMinHeight - NewH
            NewH = self.PaddMinHeight

        Host.move(NewX, NewY)
        Host.resize(NewW, NewH)
        AcceptMethod = getattr(Event, "accept", None)
        if AcceptMethod:
            AcceptMethod()

    def PaddRelease(self, Event):
        self.PaddAction = ""
        AcceptMethod = getattr(Event, "accept", None)
        if AcceptMethod:
            AcceptMethod()

    def ToggleFullscreen(self):
        Host = self.Widget
        if not Host:
            return
        if not self.PaddFullscreen:
            Geometry = getattr(Host, "geometry", None)
            if Geometry:
                self.PaddSavedGeometry = Geometry()
            ShowFull = getattr(Host, "showFullScreen", None)
            if ShowFull:
                ShowFull()
            self.PaddFullscreen = True
            return
        ShowNormal = getattr(Host, "showNormal", None)
        if ShowNormal:
            ShowNormal()
        if self.PaddSavedGeometry is not None and hasattr(Host, "setGeometry"):
            Host.setGeometry(self.PaddSavedGeometry)
        self.PaddFullscreen = False

    def PaddEdgeAction(self, X, Y):
        Host = self.Widget
        Edge = 28
        Width = int(Host.width())
        Height = int(Host.height())
        Left = X <= Edge
        Right = X >= Width - Edge
        Top = Y <= Edge
        Bottom = Y >= Height - Edge
        Parts = []
        if Top:
            Parts.append("top")
        if Bottom:
            Parts.append("bottom")
        if Left:
            Parts.append("left")
        if Right:
            Parts.append("right")
        if Parts:
            return "-".join(Parts)
        return "move"


# =====================================================================
# ПІДКЛАСИ ТА СЕМАНТИЧНІ ТИПИ ЕЛЕМЕНТІВ
# =====================================================================
class Screen(Element):
    Type = "screen"

    def __init__(self, Parent=None, **Args):
        super().__init__(Parent=Parent, **Args)
        Host = self.Widget
        # Канонічний термінал зорельота: без рамок Windows OS
        if Parent is None and Host is not None:
            FramelessFlag = getattr(LCARS, "Frameless", None)
            if hasattr(Host, "setWindowFlags") and FramelessFlag is not None:
                Host.setWindowFlags(Host.windowFlags() | FramelessFlag)
            if hasattr(Host, "setStyleSheet"):
                Host.setStyleSheet("background-color: #000000; border: none; color: #FFFFFF;")
            if hasattr(Host, "setAttribute") and hasattr(LCARS, "Protocol"):
                AlignObj = getattr(LCARS.Protocol, "Align", None)
                WidgetAttr = getattr(AlignObj, "WidgetAttribute", None)
                if WidgetAttr and hasattr(WidgetAttr, "WA_TranslucentBackground"):
                    pass
        self.Build()

Display = Screen


class Panel(Element):
    Type = "panel"


class Segment(Element):
    Type = "segment"


class Header(Element):
    Type = "header"

    def __init__(self, Title="", Parent=None, **Args):
        super().__init__(Type="header", Parent=Parent, Title=Title, **Args)
        self.Build()

HeaderFrame = Header


class Footer(Element):
    Type = "footer"

    def __init__(self, Title="", Parent=None, **Args):
        super().__init__(Type="footer", Parent=Parent, Title=Title, **Args)
        self.Build()


class Sidebar(Element):
    Type = "sidebar"

    def __init__(self, Parent=None, **Args):
        super().__init__(Type="sidebar", Parent=Parent, **Args)
        self.Build()


class Menu(Element):
    Type = "menu"

    def __init__(self, Items=None, Parent=None, **Args):
        super().__init__(Type="menu", Parent=Parent, Value=Items or [], **Args)
        self.Build()


class Toolbar(Element):
    Type = "toolbar"

    def __init__(self, Items=None, Parent=None, **Args):
        super().__init__(Type="toolbar", Parent=Parent, Value=Items or [], **Args)
        self.Build()


class StatusLine(Element):
    Type = "statusline"

    def __init__(self, Text="READY", Parent=None, **Args):
        super().__init__(Type="statusline", Parent=Parent, Value=Text, **Args)
        self.Build()


class Confirmation(Element):
    Type = "overlay"

    def __init__(self, ActionText="", OnConfirm=None, Parent=None, **Args):
        super().__init__(
            Type="overlay",
            Parent=Parent,
            ActionText=ActionText,
            ConfirmCallback=OnConfirm,
            **Args
        )
        self.Build()


class Stasis(Element):
    Type = "stasis"

    def __init__(self, Owner=None, Parent=None, **Args):
        super().__init__(Type="stasis", Parent=Parent, Owner=Owner, **Args)
        self.Build()


class AccessCode(Element):
    Type = "access"

    def __init__(self, Title="ACCESS CODE", Code="**********", Status="AUTHORIZED", Parent=None, **Args):
        super().__init__(
            Type="access",
            Parent=Parent,
            Title=Title,
            Code=Code,
            StatusText=Status,
            **Args
        )
        self.Build()

Access = AccessCode


class CoupledBlock(Element):
    Type = "coupled"

    def __init__(self, Text="", Number="", Form=None, Direction=0, Height=36, Parent=None, **Args):
        super().__init__(
            Type="coupled",
            Parent=Parent,
            Text=Text,
            Number=Number,
            Form=Form or LCARSButton.SoftHalf,
            Direction=Direction,
            Height=Height,
            **Args
        )
        self.Build()

Coupled = CoupledBlock


class TelemetryBlock(Element):
    Type = "telemetry"

    def __init__(self, Number="07", Badge="SEC", Parent=None, **Args):
        super().__init__(
            Type="telemetry",
            Parent=Parent,
            Number=Number,
            Badge=Badge,
            **Args
        )
        self.Build()

Telemetry = TelemetryBlock


class FrameBracket(Element):
    Type = "bracket"

    def __init__(self, Width=320, Height=64, Thickness=24, Parent=None, **Args):
        super().__init__(
            Type="bracket",
            Parent=Parent,
            Width=Width,
            Height=Height,
            Thickness=Thickness,
            **Args
        )
        self.Build()

Bracket = FrameBracket


class DataBlock(Element):
    Type = "datablock"

    def __init__(self, *Arguments, **Args):
        LabelText = Args.pop("Label", Args.pop("label", Args.pop("LabelText", Args.pop("labelText", ""))))
        ValueText = Args.pop("Value", Args.pop("value", Args.pop("ValueText", Args.pop("valueText", ""))))
        Parent = Args.pop("Parent", Args.pop("parent", None))
        Color = Args.pop("Color", Args.pop("color", None))

        if len(Arguments) >= 1:
            LabelText = Arguments[0]
        if len(Arguments) >= 2:
            ValueText = Arguments[1]
        if len(Arguments) >= 3:
            if isinstance(Arguments[2], str):
                Color = Arguments[2]
            else:
                Parent = Arguments[2]
        if len(Arguments) >= 4:
            if isinstance(Arguments[3], str):
                Color = Arguments[3]
            else:
                Parent = Arguments[3]

        super().__init__(
            Type="datablock",
            Parent=Parent,
            Color=Color,
            Label=LabelText,
            Value=ValueText,
            **Args
        )
        self.Build()


class StatBar(Element):
    Type = "statbar"

    def __init__(self, *Arguments, **Args):
        LabelText = Args.pop("Label", Args.pop("label", Args.pop("LabelText", Args.pop("labelText", ""))))
        Value = Args.pop("Value", Args.pop("value", 0))
        Parent = Args.pop("Parent", Args.pop("parent", None))
        Color = Args.pop("Color", Args.pop("color", None))

        if len(Arguments) >= 1:
            LabelText = Arguments[0]
        if len(Arguments) >= 2:
            if isinstance(Arguments[1], str) and Arguments[1].startswith("#"):
                Color = Arguments[1]
            else:
                Value = Arguments[1]
        if len(Arguments) >= 3:
            if isinstance(Arguments[2], str) and Arguments[2].startswith("#"):
                Color = Arguments[2]
            else:
                Parent = Arguments[2]

        super().__init__(
            Type="statbar",
            Parent=Parent,
            Color=Color,
            Label=LabelText,
            Value=Value,
            **Args
        )
        self.Build()


class ScanningBar(Element):
    Type = "scanningbar"

    def __init__(self, *Arguments, **Args):
        ColorVal = Args.pop("Color", Args.pop("color", Args.pop("ColorVal", None)))
        Parent = Args.pop("Parent", Args.pop("parent", None))
        Speed = Args.pop("Speed", Args.pop("speed", 1.0))

        if len(Arguments) >= 1:
            if isinstance(Arguments[0], str):
                ColorVal = Arguments[0]
            else:
                Parent = Arguments[0]
        if len(Arguments) >= 2:
            if isinstance(Arguments[1], (int, float)):
                Speed = Arguments[1]
            elif isinstance(Arguments[1], str):
                ColorVal = Arguments[1]
            else:
                Parent = Arguments[1]

        super().__init__(
            Type="scanningbar",
            Parent=Parent,
            Color=ColorVal,
            Speed=Speed,
            **Args
        )
        self.Build()


class ButtonGroup:
    def __init__(self):
        self.ButtonsList = []

    def AddButton(self, button):
        self.ButtonsList.append(button)

    def Buttons(self):
        return list(self.ButtonsList)

    def CheckedButton(self):
        for ButtonObj in self.ButtonsList:
            if hasattr(ButtonObj, "isChecked") and ButtonObj.isChecked():
                return ButtonObj
        return self.ButtonsList[0] if self.ButtonsList else None


# =====================================================================
# CHIP INTERFACE BUILDER — Фабрика зчитування й побудови чіпів ODN
# =====================================================================
class ChipInterfaceBuilder:
    @classmethod
    def LocateChip(cls, ChipId: str) -> Optional[Path]:
        CleanId = str(ChipId).strip().replace(".yaml", "").replace(".yml", "")
        BaseDir = Path(__file__).resolve().parents[2]
        Cat = CleanId.split("-")[0] if "-" in CleanId else "05"
        Candidates = [
            BaseDir / "lcars" / "engineering" / "chips" / Cat / f"{CleanId}.yaml",
            BaseDir / "lcars" / "engineering" / "chips" / Cat / f"{CleanId[:7]}.yaml",
            BaseDir / "lcars" / "engineering" / "chips" / Cat / "05-0000.yaml",
        ]
        for Candidate in Candidates:
            if Candidate.exists():
                return Candidate
        return None

    @classmethod
    def LoadChipData(cls, ChipId: str) -> dict:
        ChipFile = cls.LocateChip(ChipId)
        if not ChipFile:
            return {}
        with open(ChipFile, "r", encoding="utf-8") as FileStream:
            Manifest = yaml.safe_load(FileStream) or {}

        DbConfig = Manifest.get("config", {}).get("database", {})
        DbRelPath = DbConfig.get("path", "")
        if DbRelPath:
            BaseDir = Path(__file__).resolve().parents[2]
            DbPath = BaseDir / DbRelPath
            if DbPath.exists():
                Conn = sqlite3.connect(str(DbPath))
                Cursor = Conn.cursor()
                Table = DbConfig.get("table", "ui_chip_images")
                ScreenName = DbConfig.get("screen", "master_catalog")
                Cursor.execute(
                    f"SELECT elements_json FROM {Table} WHERE chip_id=? OR screen_name=? LIMIT 1",
                    (str(ChipId), str(ScreenName))
                )
                Row = Cursor.fetchone()
                Conn.close()
                if Row and Row[0]:
                    Payload = json.loads(Row[0])
                    if "layout" not in Payload and "sections" in Payload:
                        return {"layout": Payload}
                    return Payload

        LayoutPayload = Manifest.get("layout", {})
        if LayoutPayload:
            return {"layout": LayoutPayload}
        return {}

    @classmethod
    def Build(cls, ChipId: str, ParentHost: Any = None, MasterPadd: Any = None):
        Data = cls.LoadChipData(ChipId)
        if not Data:
            return None
        LayoutConfig = Data.get("layout", {})
        RootPanel = Panel(Parent=ParentHost)
        RootLayout = RootPanel.Vertical(16, 14, 16, 14, 18)
        StatusLabelRef = [None]

        def HandleModeAction(ActionType):
            from lcars.system.alert import GetAlertSystem, AlertLevel
            import lcars.base.default as DefaultMod
            AlertSys = GetAlertSystem()
            if ActionType == "normal":
                DefaultMod.SystemState = "normal"
                if AlertSys:
                    AlertSys.SetLevel(AlertLevel.GREEN)
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("SYSTEM MODE: NORMAL // STANDARD STARFLEET OPERATIONAL PALETTE")
            elif ActionType == "yellow":
                DefaultMod.SystemState = "yellow"
                if AlertSys:
                    AlertSys.SetLevel(AlertLevel.YELLOW)
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("SYSTEM MODE: CONDITION YELLOW // ACTIVE SENSOR CAUTION")
            elif ActionType == "red":
                DefaultMod.SystemState = "red"
                if AlertSys:
                    AlertSys.SetLevel(AlertLevel.RED)
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("SYSTEM MODE: CONDITION RED // ALL STATIONS TO TACTICAL ALERT")
            elif ActionType == "auth":
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("AUTHORIZATION ACCEPTED // SECURITY CLEARANCE LEVEL 4")
                    StatusLabelRef[0].Update()
            elif ActionType == "standby":
                DefaultMod.SystemState = "disabled"
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("SYSTEM MODE: STANDBY // POWER CONSERVE PROTOCOL")
            if MasterPadd and hasattr(MasterPadd, "Widget") and MasterPadd.Widget:
                MasterPadd.Widget.update()

        Sections = LayoutConfig.get("sections", [])
        for SecData in Sections:
            SecPanel = Panel(Parent=RootPanel.Widget)
            SecVL = SecPanel.Vertical(0, 0, 0, 0, SecData.get("spacing", 8))

            if "header" in SecData:
                HdrData = SecData["header"]
                HdrLbl = LCARSLabel(
                    Text=HdrData.get("text", ""),
                    FontSize=HdrData.get("font_size", 18),
                    Parent=SecPanel.Widget,
                )
                SecPanel.Add(SecVL, HdrLbl)

            if "status_label" in SecData:
                StData = SecData["status_label"]
                StRow = Segment(Parent=SecPanel.Widget)
                StRL = StRow.Horizontal(0, 0, 0, 0, 6)
                StLbl = LCARSLabel(
                    Text=StData.get("text", ""),
                    FontSize=StData.get("font_size", 18),
                    Parent=StRow.Widget,
                )
                StatusLabelRef[0] = StLbl
                StRow.Add(StRL, StLbl)
                SecPanel.Add(SecVL, StRow)

            for RowData in SecData.get("rows", []):
                RowType = RowData.get("type", "segment")
                if RowType == "compound_stacks":
                    RowMain = Segment(Parent=SecPanel.Widget)
                    RML = RowMain.Horizontal(0, 0, 0, 0, 12)

                    LeftStack = Segment(Parent=RowMain.Widget)
                    LSL = LeftStack.Vertical(0, 0, 0, 0, 4)
                    for NumVal, NameVal, ChipCode in RowData.get("left_rows", []):
                        RowItem = Segment(Parent=LeftStack.Widget)
                        RL = RowItem.Horizontal(0, 0, 0, 0, 4)
                        Cap = LCARSIndicator(
                            IndicatorType=LCARSIndicator.PillHalf,
                            Direction=180,
                            Width=28,
                            Height=28,
                            Parent=RowItem.Widget
                        )
                        Bar = LCARSBar(Width=6, Height=28, Parent=RowItem.Widget)
                        NumLbl = LCARSLabel(Text=NumVal, FontSize=20, Width=48, Parent=RowItem.Widget)
                        Btn = LCARSButton(
                            Text=NameVal,
                            Number=ChipCode,
                            Form=LCARSButton.SoftHalf,
                            Direction=0,
                            Height=28,
                            Width=180,
                            FontSize=16,
                            Parent=RowItem.Widget
                        )
                        RowItem.Add(RL, Cap)
                        RowItem.Add(RL, Bar)
                        RowItem.Add(RL, NumLbl)
                        RowItem.Add(RL, Btn)
                        LeftStack.Add(LSL, RowItem)
                    RowMain.Add(RML, LeftStack)

                    RightStack = Segment(Parent=RowMain.Widget)
                    RSL = RightStack.Vertical(0, 0, 0, 0, 4)
                    for Subsys, BadgeVal, TelemetryVal, ChipCode in RowData.get("right_rows", []):
                        RowItem = Segment(Parent=RightStack.Widget)
                        RL = RowItem.Horizontal(0, 0, 0, 0, 4)
                        LBtn = LCARSButton(
                            Text=Subsys,
                            Number=ChipCode,
                            Form=LCARSButton.SoftHalf,
                            Direction=180,
                            Height=28,
                            Width=160,
                            FontSize=16,
                            Parent=RowItem.Widget
                        )
                        BadgeLbl = LCARSLabel(Text=BadgeVal, FontSize=20, Width=36, Parent=RowItem.Widget)
                        DataLbl = LCARSLabel(Text=TelemetryVal, FontSize=18, Width=140, Parent=RowItem.Widget)
                        CapR = LCARSIndicator(
                            IndicatorType=LCARSIndicator.PillHalf,
                            Direction=0,
                            Width=24,
                            Height=28,
                            Parent=RowItem.Widget
                        )
                        RowItem.Add(RL, LBtn)
                        RowItem.Add(RL, BadgeLbl)
                        RowItem.Add(RL, DataLbl)
                        RowItem.Add(RL, CapR)
                        RightStack.Add(RSL, RowItem)
                    RowMain.Add(RML, RightStack, 1)
                    SecPanel.Add(SecVL, RowMain)

                elif RowType == "bars_stack":
                    BarRow = Segment(Parent=SecPanel.Widget)
                    BRL = BarRow.Vertical(0, 0, 0, 0, 4)
                    for HVal in RowData.get("heights", [4, 8, 14, 22]):
                        Bar = LCARSBar(Height=HVal, Parent=BarRow.Widget)
                        BarRow.Add(BRL, Bar)
                    SecPanel.Add(SecVL, BarRow)

                else:
                    RowSeg = Segment(Parent=SecPanel.Widget)
                    RL = RowSeg.Horizontal(0, 0, 0, 0, RowData.get("spacing", 6))
                    for Item in RowData.get("items", []):
                        IType = Item.get("type", "button")
                        Flex = Item.get("flex", 0)
                        if IType == "button":
                            ActionKey = Item.get("action", "")
                            Btn = LCARSButton(
                                Text=Item.get("text", ""),
                                Number=Item.get("number", ""),
                                Form=Item.get("form", LCARSButton.Pill),
                                Height=Item.get("height", 38),
                                Width=Item.get("width", 0),
                                FontSize=Item.get("font_size", 16),
                                Parent=RowSeg.Widget,
                            )
                            if ActionKey:
                                def MakeHandler(Act):
                                    return lambda *a: HandleModeAction(Act)
                                Btn.Clicked.Connect(MakeHandler(ActionKey))
                            RowSeg.Add(RL, Btn, Flex)
                        elif IType == "elbow":
                            Elb = LCARSElbow(
                                Direction=Item.get("direction", "top-left"),
                                Text=Item.get("text", ""),
                                Number=Item.get("number", ""),
                                Width=Item.get("width", 480),
                                Height=Item.get("height", 80),
                                Thickness=Item.get("thickness", 24),
                                Radius=Item.get("radius", 36),
                                FontSize=Item.get("font_size", 18),
                                Parent=RowSeg.Widget,
                            )
                            RowSeg.Add(RL, Elb, Flex)
                        elif IType == "indicator":
                            IndMap = {
                                "pill": LCARSIndicator.Pill,
                                "pill_half": LCARSIndicator.PillHalf,
                                "bar": LCARSIndicator.Rect,
                                "rect": LCARSIndicator.Rect,
                            }
                            IndTypeEnum = IndMap.get(Item.get("indicator_type", "pill_half"), LCARSIndicator.PillHalf)
                            Ind = LCARSIndicator(
                                Text=Item.get("text", ""),
                                IndicatorType=IndTypeEnum,
                                Direction=Item.get("direction", 0),
                                Height=Item.get("height", 34),
                                Width=Item.get("width", 140),
                                FontSize=Item.get("font_size", 16),
                                Parent=RowSeg.Widget,
                            )
                            RowSeg.Add(RL, Ind, Flex)
                        elif IType == "datablock":
                            DB = DataBlock(
                                Item.get("title", ""),
                                Item.get("data", {}),
                                RowSeg.Widget,
                            )
                            RowSeg.Add(RL, DB, Flex)
                    SecPanel.Add(SecVL, RowSeg)

            RootPanel.Add(RootLayout, SecPanel)
        return RootPanel


# =====================================================================
# ЕКСПОРТНІ СИНОНІМИ ТА СИМВОЛИ
# =====================================================================
Button = LCARSButton
Label = LCARSLabel
Indicator = LCARSIndicator
Elbow = LCARSElbow
Bar = LCARSBar
Pill = LCARSButton
Frame = Panel
Padd = PADD
LCARSPadd = PADD
LCARSScreen = Screen
LCARSSegment = Segment
LCARSInput = LCARSButton
LCARSProgramPanel = Panel
LCARSWaveform = ScanningBar

__all__ = [
    "Element",
    "PADD",
    "Padd",
    "Screen",
    "Display",
    "Panel",
    "Segment",
    "Header",
    "HeaderFrame",
    "Footer",
    "Sidebar",
    "Menu",
    "Toolbar",
    "StatusLine",
    "Confirmation",
    "Stasis",
    "AccessCode",
    "Access",
    "CoupledBlock",
    "Coupled",
    "TelemetryBlock",
    "Telemetry",
    "Bracket",
    "FrameBracket",
    "DataBlock",
    "StatBar",
    "ScanningBar",
    "ButtonGroup",
    "ChipInterfaceBuilder",
    "Button",
    "Label",
    "Indicator",
    "Elbow",
    "Bar",
    "Pill",
    "Frame",
    "LCARSButton",
    "LCARSLabel",
    "LCARSIndicator",
    "LCARSElbow",
    "LCARSBar",
    "LCARSPadd",
    "LCARSScreen",
    "LCARSSegment",
    "LCARSInput",
    "LCARSProgramPanel",
    "LCARSWaveform",
    "Primitive",
    "SetStyle",
]
