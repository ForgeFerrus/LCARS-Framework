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
# =============================================================================
# TOOLBAR — ГОРИЗОНТАЛЬНА ПАНЕЛЬ ШВИДКИХ ДІЙ ТА ІНСТРУМЕНТІВ LCARS
# Ряд функціональних кнопок та статус-маркерів
# =============================================================================
class Toolbar(Element):
    TypeName = "Toolbar"
    Type = "Toolbar"

    # Варіації панелі
    Compact = 1
    Divided = 2
    Aligned = 3

    Height = 36
    Spacing = 6

    def Compose(self, *Objects, Align="left"):
        self.Clear()
        LayoutRef = self.SetHorizontal(0, 0, 0, 0, Spacing=self.Spacing)

        # Якщо вирівнювання праворуч — пружина на початку
        if Align == "right":
            self.AddStretch(LayoutRef, 1)

        for Obj in Objects:
            # Якщо передано число — це пружина (розрив між групами кнопок)
            if isinstance(Obj, int):
                self.AddStretch(LayoutRef, Obj)
            else:
                self.Add(Obj)

        # Якщо вирівнювання ліворуч — пружина в кінці (притискає кнопки вліво)
        if Align == "left":
            self.AddStretch(LayoutRef, 1)
        return self
# =============================================================================
# STATBAR — ГОРИЗОНТАЛЬНА ШКАЛА СТАТУСУ ТА ТЕЛЕМЕТРІЇ LCARS
# Відображає назву, динамічну смугу рівня та цифрове значення
# =============================================================================
class StatBar(Element):
    TypeName = "StatBar"
    Type = "StatBar"

    # Варіації шкали
    Linear = 1
    Segmented = 2
    Minimal = 3

    Form = Linear
    Height = 24
    Value = 0.0         # 0.0 - 100.0 %
    Title = ""

    def Compose(self, Label=None, Bar=None, ValueLabel=None, Indicator=None):
        self.Clear()
        self.SetHorizontal(0, 0, 0, 0, Spacing=6)

        # 1. Назва параметра зліва
        if Label is not None:
            self.Add(Label)

        # 2. Основна динамічна балка (заповнює всю вільну ширину)
        if Bar is not None:
            self.Add(Bar, 1)

        # 3. Числове значення (відсотки/одиниці)
        if ValueLabel is not None:
            self.Add(ValueLabel)

        # 4. Кінцевий маркер-заглушка справа
        if Indicator is not None:
            self.Add(Indicator)

        return self

    def SetValue(self, Value: float):
        self.Value = max(0.0, min(100.0, float(Value)))
        # Оновлюємо стан залежно від порогу аварійності
        if self.Value >= 90.0:
            self.State = self.ALERT
        elif self.Value >= 75.0:
            self.State = self.YELLOW
        else:
            self.State = self.NORMAL
            
        self.Refresh()
        return self
# =============================================================================
# SCANNINGBAR — ДИНАМІЧНИЙ СКАНЕР СЕНСОРІВ ТА БІГУНОК ІМПУЛЬСІВ
# Анімована смуга сканування для діагностичних та наукових панелей
# =============================================================================
class ScanningBar(Element):
    TypeName = "ScanningBar"
    Type = "ScanningBar"

    # Варіації анімації
    Oscillating = 1     # Маятниковий бігунок
    Progressive = 2     # Односторонній прохід
    DualPulse = 3       # Зустрічні імпульси

    Form = Oscillating
    Height = 24
    Active = True
    Position = 0.0      # Поточна фаза (0.0 - 1.0)
    Direction = 1       # 1 = праворуч, -1 = ліворуч
    Speed = 1.0         # Швидкість сканування

    def Compose(self, Rail=None, Label=None, StatusCap=None):
        self.Clear()
        self.SetHorizontal(0, 0, 0, 0, Spacing=6)

        if Label is not None:
            self.Add(Label)

        if Rail is not None:
            # Напрямна балка сканера займає весь простір
            self.Add(Rail, 1)

        if StatusCap is not None:
            self.Add(StatusCap)

        return self

    # Крок анімації скануючого імпульсу (викликається квантовим таймером)
    def StepScan(self, Delta=0.05):
        if not self.Active or not self.Power:
            return self

        # Маятниковий режим
        if self.Form == self.Oscillating:
            self.Position += Delta * self.Speed * self.Direction
            if self.Position >= 1.0:
                self.Position = 1.0
                self.Direction = -1
            elif self.Position <= 0.0:
                self.Position = 0.0
                self.Direction = 1
        # Односторонній режим
        else:
            self.Position = (self.Position + Delta * self.Speed) % 1.0

        self.Refresh()
        return self

    def SetScanning(self, Active: bool):
        self.Active = (Active)
        self.Refresh()
        return self 
# =============================================================================
# PANEL — КОНСОЛЬНА ОПЕРАЦІЙНА ПАНЕЛЬ ВІДСІКУ LCARS
# Базова робоча плита для розміщення кнопок, моніторів та схем
# =============================================================================
class Panel(Element):
    TypeName = "Panel"
    Type = "Panel"

    # Варіації панелі
    GridButton = 1            # Матрична панель кнопок
    Framed = 2          # Панель із рамкою/ліктями
    Card = 3            # Окрема інформаційна картка
    Segment = 4         # Розділена на секції панель

    Form = Framed
    Title = ""
    Code = "PANEL-01"

    def Compose(self, HeaderElement=None, ContentElement=None, ControlsElement=None):
        self.Clear()
        MainLayout = self.SetVertical(6, 6, 6, 6, Spacing=6)

        # 1. Шапка або рамка панелі
        if HeaderElement is not None:
            self.Add(HeaderElement)

        # 2. Робоча зона (контент / схема)
        if ContentElement is not None:
            self.Add(ContentElement, 1)  # займає основний простір

        # 3. Нижні органи управління (кнопки/тулбар)
        if ControlsElement is not None:
            self.Add(ControlsElement)
        return self
# =============================================================================
# ACCESSPANEL — ПАНЕЛЬ ДОСТУПУ ТА ПІДТВЕРДЖЕННЯ БЕЗПЕКИ LCARS
# Чисте компонування готових органів авторизації та підтвердження
# =============================================================================
class AccessPanel(Element):
    TypeName = "AccessPanel"
    Type = "AccessPanel"

    # Варіації панелі
    Confirmation = 1        # Просте підтвердження (Запит + Скасування + Підтвердження)
    Authorization = 2       # Введення коду безпеки (Запит + Дисплей коду + Дії)
    Override = 3            # Подвійне підтвердження

    Form = Confirmation

    def Compose(self, Prompt=None, CodeDisplay=None, AbortButton=None, ConfirmButton=None, Keypad=None):
        self.Clear()
        self.SetVertical(8, 8, 8, 8, Spacing=8)

        # 1. Текст запиту чи попередження
        if Prompt is not None:
            self.Add(Prompt)

        # 2. Дисплей введеного коду (якщо режим авторизації)
        if CodeDisplay is not None:
            self.Add(CodeDisplay)

        # 3. Сенсорна панель клавіатури (якщо є)
        if Keypad is not None:
            self.Add(Keypad, 1)

        # 4. Ряд кнопок дій: [ AbortButton | <stretch> | ConfirmButton ]
        if AbortButton is not None or ConfirmButton is not None:
            ActionRow = Element()
            ActionRow.SetHorizontal(0, 0, 0, 0, Spacing=8)

            if AbortButton is not None:
                ActionRow.Add(AbortButton)

            ActionRow.AddStretch()

            if ConfirmButton is not None:
                ActionRow.Add(ConfirmButton)

            self.Add(ActionRow)
        return self
# =============================================================================
# SCREEN — ГОЛОВНИЙ ЕЛЕМЕНТ ЕКРАНА LCARS
# Простий базовий контейнер сцени на весь екран
# =============================================================================
class Screen(Element):
    TypeName = "Screen"
    Type = "Screen"

    def Compose(self, Top=None, Center=None, Bottom=None):
        self.Clear()
        self.SetVertical(0, 0, 0, 0, Spacing=6)

        # 1. Верхній ярус (шапка)
        if Top is not None:
            self.Add(Top)

        # 2. Центральна сцена (займає весь вільний простір)
        if Center is not None:
            self.Add(Center, 1)

        # 3. Нижній ярус (підвал)
        if Bottom is not None:
            self.Add(Bottom)

        return self
# =============================================================================
# FRAME — КОНТУРНА РАМА ВІДСІКУ ТА РОБОЧОЇ ЗОНИ LCARS
# Обмежує зону вмісту несучим каркасом Окуди. Варіації: Full, Header, Footer
# =============================================================================
class Frame(Element):
    TypeName = "Frame"
    Type = "Frame"

    # Варіації рами
    Full = 1        # Повна замкнена рама (4 кути)
    HeaderFrame = 2 # П-подібна рама зверху
    FooterFrame = 3 # U-подібна рама знизу

    Form = Full

    def Compose(self, TopBar=None, LeftPillar=None, Content=None, RightPillar=None, BottomBar=None):
        self.Clear()
        MainLayout = self.SetVertical(0, 0, 0, 0, Spacing=6)

        # 1. Верхня поперечина рами
        if TopBar is not None:
            self.Add(TopBar)

        # 2. Центральний ярус: [ LeftPillar | Content | RightPillar ]
        CenterRow = Element()
        CenterRow.SetHorizontal(0, 0, 0, 0, Spacing=6)

        if LeftPillar is not None:
            CenterRow.Add(LeftPillar)

        if Content is not None:
            CenterRow.Add(Content, 1)  # Вміст розтягується на всю ширину і висоту!

        if RightPillar is not None:
            CenterRow.Add(RightPillar)

        self.Add(CenterRow, 1)  # Центральний ярус заповнює висоту рами

        # 3. Нижня поперечина рами
        if BottomBar is not None:
            self.Add(BottomBar)

        return self
# =============================================================================
# PADD — ПЕРСОНАЛЬНИЙ ДОСТУПОВИЙ ДИСПЛЕЙ (ПЛАНШЕТ ОФІЦЕРА ЗОРЕЛЬОТА)
# Портативний автономний термінал із перетягуванням та масштабуванням
# =============================================================================
class PADD(Element):
    Type = "PADD"
    Type = "PADD"
    Width = 920
    Height = 580
    MinWidth = 320
    MinHeight = 240
    Portable = True
    PaddAction = ""
    PaddStartGlobal = (0, 0)
    PaddStartRect = (0, 0, 0, 0)
    PaddOffset = (0, 0)
    # Все наслідується чисто і без помилок сигнатури!
    def ConfigurePadd(self):
        Host = self.Widget
        if hasattr(Host, "setMinimumSize"):
            Host.setMinimumSize(self.MinWidth, self.MinHeight)
        if hasattr(Host, "resize"):
            Host.resize(self.Width, self.Height)

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

    def PaddPress(self, LX, LY):
        Margin = 8
        Host = self.Widget
        W = Host.width()
        H = Host.height()
        
        Action = ""
        if LY < Margin: Action += "top"
        elif LY > H - Margin: Action += "bottom"
        
        if LX < Margin: Action += "left"
        elif LX > W - Margin: Action += "right"
        return Action or "move"

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
# ЕКСПОРТНІ СИНОНІМИ ТА СИМВОЛИ
# =====================================================================
LCARS.All = [
    "Element",
    "PADD",
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
    "Bracket",
    "FrameBracket",
    "DataBlock",
    "StatBar",
    "ScanningBar",
    "ButtonGroup",
    "ProgramPanel",
]
