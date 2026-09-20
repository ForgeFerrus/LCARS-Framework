# LCARS FRAMEWORK 
# Готові елементи та канонічні композиції LCARS (Michael Okuda Standard).
# У component.py лежать фізичні примітиви. Тут лежить віртуальний контейнер/оркестратор Element
# та канонічні складені об'єкти інтерфейсу зорельота за векторними кресленнями CorelDRAW.

from typing import Any, Optional, Dict, List, Union, Tuple
from lcars.base.component import Component
from lcars.base.graphic import Visual, Emitter
from lcars.base.default import DefaultBackground, Palette
from lcars.base.type import LCARS, SystemComponent, Namespace
from lcars.base.display import LCARSNativeViewport

WidgetClass = LCARS.Retrieve("Base.Interface.Widget")
if WidgetClass is None or not callable(WidgetClass):
    QtWidgetsMod = LCARS.Import("PyQt6.QtWidgets")
    WidgetClass = getattr(QtWidgetsMod, "QWidget", object) if QtWidgetsMod else object

if WidgetClass is not object:
    class SurfaceViewportMeta(type(WidgetClass), Namespace):
        pass

    class SurfaceViewport(WidgetClass, metaclass=SurfaceViewportMeta):
        """Канонічний в'юпорт поверхні LCARS."""
        SurfaceObj = None

        def __init__(self, SurfaceObj=None, Parent=None):
            super().__init__(Parent)
            self.SurfaceObj = SurfaceObj
            if SurfaceObj and hasattr(SurfaceObj, "Optics") and SurfaceObj.Optics:
                W = getattr(SurfaceObj.Optics, "Width", 800)
                H = getattr(SurfaceObj.Optics, "Height", 600)
                if hasattr(self, "resize"):
                    self.resize(int(W), int(H))

        def paintEvent(self, Event):
            if self.SurfaceObj and hasattr(self.SurfaceObj, "OpticalDispersion"):
                self.SurfaceObj.OpticalDispersion(Event)

        def resizeEvent(self, Event):
            if self.SurfaceObj and hasattr(self.SurfaceObj, "Rescale"):
                self.SurfaceObj.Rescale(Event)

        def mousePressEvent(self, Event):
            if self.SurfaceObj and hasattr(self.SurfaceObj, "TouchContact"):
                self.SurfaceObj.TouchContact(Event)

        def mouseReleaseEvent(self, Event):
            if self.SurfaceObj and hasattr(self.SurfaceObj, "TouchRelease"):
                self.SurfaceObj.TouchRelease(Event)

        def mouseMoveEvent(self, Event):
            if self.SurfaceObj and hasattr(self.SurfaceObj, "TouchMovement"):
                self.SurfaceObj.TouchMovement(Event)
else:
    class SurfaceViewport(LCARS):
        """Канонічний в'юпорт поверхні LCARS."""
        SurfaceObj = None

        def __init__(self, SurfaceObj=None, Parent=None):
            self.SurfaceObj = SurfaceObj

# =============================================================================
# СЕНСОРНА ОПТИЧНА ПОВЕРХНЯ LCARS (SURFACE / PANEL)
# Чистий векторний вузол LCARS (SystemComponent) без наслідування від QWidget
# =============================================================================
class Surface(SystemComponent):
    TypeName = "LCARSSurface"
    Optics = None
    Layers = []
    PulseTimer = None
    Viewport = None

    def Initialize(self, Optics=None, Parent=None, **kwargs):
        if getattr(self, "Initialized", False):
            return self
        super().Initialize(Parent=Parent, **kwargs)
        self.Optics = Optics
        self.Layers = kwargs.get("Layers", [])
        if self.Optics is not None:
            OpticsHeight = getattr(self.Optics, "Height", None)
            OpticsWidth = getattr(self.Optics, "Width", None)
            OpticsType = str(getattr(self.Optics, "Type", "")).lower()
            IsRigid = not getattr(self.Optics, "Flexible", False) or OpticsType in ("button", "indicator", "elbow", "label", "bar", "text")
            if OpticsHeight is not None and IsRigid:
                self.setFixedHeight(int(OpticsHeight))
            if OpticsWidth is not None and OpticsType in ("button", "indicator", "elbow"):
                self.setFixedWidth(int(OpticsWidth))
        return self

    def GetViewport(self):
        if self.Viewport is None:
            self.Viewport = SurfaceViewport(SurfaceObj=self)
        return self.Viewport

    def width(self):
        if self.Viewport is not None:
            return self.Viewport.width()
        return int(getattr(self, "Width", 800))

    def height(self):
        if self.Viewport is not None:
            return self.Viewport.height()
        return int(getattr(self, "Height", 600))

    def setFixedWidth(self, Width):
        if self.Optics:
            self.Optics.Width = Width
        self.Width = Width
        if self.Viewport is not None and hasattr(self.Viewport, "setFixedWidth"):
            self.Viewport.setFixedWidth(int(Width))
        return self

    def setFixedHeight(self, Height):
        if self.Optics:
            self.Optics.Height = Height
        self.Height = Height
        if self.Viewport is not None and hasattr(self.Viewport, "setFixedHeight"):
            self.Viewport.setFixedHeight(int(Height))
        return self

    def update(self):
        if self.Viewport is not None and hasattr(self.Viewport, "update"):
            self.Viewport.update()
        return self

    def show(self):
        self.GetViewport().show()
        return self

    def showFullScreen(self):
        self.GetViewport().showFullScreen()
        return self

    def hide(self):
        if self.Viewport is not None and hasattr(self.Viewport, "hide"):
            self.Viewport.hide()
        return self

    def windowFlags(self):
        return self.GetViewport().windowFlags()

    def setWindowFlags(self, Flags):
        return self.GetViewport().setWindowFlags(Flags)

    def setStyleSheet(self, Sheet):
        return self.GetViewport().setStyleSheet(Sheet)

    def isVisible(self):
        if self.Viewport is not None:
            return self.Viewport.isVisible()
        return True

    def SetOptics(self, Value):
        self.Optics = Value
        return self
    Visual = None
    Graphic = None

    # Пульсація стану поверхні
    def Pulse(self, Event=None):
        if not self.Optics:
            return
        if not self.isVisible():
            return
        self.update()

    # Рекомендований розмір поверхні для систем компонування
    def PreferredSize(self):
        Node = self.Optics
        W = int(getattr(Node, "Width", 100) if Node is not None else 100)
        H = int(getattr(Node, "Height", 30) if Node is not None else 30)
        W = max(10, min(16384, W))
        H = max(10, min(16384, H))
        SizeClass = LCARS.Retrieve("Base.Geometry.Size.Int")
        return SizeClass(W, H) if SizeClass and callable(SizeClass) else None

    # Просторове вирівнювання сенсорного поля
    def AlignContent(self, Flag):
        if hasattr(self.Optics, "Align"):
            self.Optics.Align = "center" if "Center" in str(Flag) else ("right" if "Right" in str(Flag) else "left")
        self.update()
        return self

    # Зміна фізичної геометрії сенсорного скла
    def Rescale(self, Event=None):
        if self.Optics is not None:
            self.Optics.Width = self.width()
            self.Optics.Height = self.height()
            if hasattr(self.Optics, "Synthesize") and callable(self.Optics.Synthesize):
                self.Optics.Synthesize()
            elif hasattr(self.Optics, "Generate") and callable(self.Optics.Generate):
                self.Optics.Generate()

    # Цикл оптичного світіння (прояв фотонного поля на поверхні)
    def OpticalDispersion(self, Event=None):
        if self.Optics is None:
            return
        TargetDevice = self.GetViewport()
        CurrentW = TargetDevice.width()
        CurrentH = TargetDevice.height()
        if getattr(self.Optics, "Width", 0) != CurrentW or getattr(self.Optics, "Height", 0) != CurrentH:
            self.Optics.Width = CurrentW
            self.Optics.Height = CurrentH
            if hasattr(self.Optics, "Synthesize") and callable(self.Optics.Synthesize):
                self.Optics.Synthesize()
        ProjectorInstance = Emitter()
        if ProjectorInstance.Activate(TargetDevice):
            ProjectorInstance.Project(self.Optics)
            ProjectorInstance.Deactivate()
    # Сенсорний контакт (натискання на скло)
    def TouchContact(self, Event):
        ButtonValue = getattr(Event, "button", lambda: 1)()
        IsLeftButton = (
            ButtonValue == 1 or
            "Left" in str(ButtonValue) or
            ButtonValue == getattr(getattr(LCARS, "Protocol", None), "LeftButton", 1)
        )
        HandledByOptics = False
        if IsLeftButton and self.Optics is not None:
            IsTactile = getattr(self.Optics, "Tactile", False) or getattr(self.Optics, "IsWakeupTrigger", False)
            TargetEngage = getattr(self.Optics, "Engage", getattr(self.Optics, "Trigger", None))
            if IsTactile and callable(TargetEngage):
                TargetEngage()
                HandledByOptics = True
            if hasattr(self, "isVisible") and self.isVisible():
                self.update()

        if not HandledByOptics:
            WindowHost = self.window()
            PaddCtrl = getattr(WindowHost, "PaddController", None)
            if PaddCtrl is not None and hasattr(PaddCtrl, "PaddPress"):
                PaddCtrl.PaddPress(Event)
                return

        ParentMousePress = getattr(super(), "TouchContact", None)
        if callable(ParentMousePress):
            ParentMousePress(Event)
    # Розрив сенсорного контакту (відпускання скла)
    def TouchRelease(self, Event):
        if self.Optics is not None:
            TargetDisengage = getattr(self.Optics, "Disengage", getattr(self.Optics, "Release", None))
            if callable(TargetDisengage):
                TargetDisengage()
            if hasattr(self, "isVisible") and self.isVisible():
                self.update()

        WindowHost = self.window()
        PaddCtrl = getattr(WindowHost, "PaddController", None)
        if PaddCtrl is not None and hasattr(PaddCtrl, "PaddRelease"):
            PaddCtrl.PaddRelease(Event)

        ParentMouseRelease = getattr(super(), "TouchRelease", None)
        if callable(ParentMouseRelease):
            ParentMouseRelease(Event)
    # Переміщення вказівника (сенсорний рух)
    def TouchMovement(self, Event):
        WindowHost = self.window()
        PaddCtrl = getattr(WindowHost, "PaddController", None)
        if PaddCtrl is not None and hasattr(PaddCtrl, "PaddMove"):
            PaddCtrl.PaddMove(Event)
        ParentMouseMove = getattr(super(), "mouseMoveEvent", None)
        if callable(ParentMouseMove):
            ParentMouseMove(Event)
    # Датчик наближення (фокус при наведенні курсора або руки)
    def FocusDetection(self, Event):
        if self.Optics is not None:
            TargetFocus = getattr(self.Optics, "Focus", getattr(self.Optics, "Hover", None))
            if callable(TargetFocus):
                TargetFocus(True)
            self.update()
        ParentEnter = getattr(super(), "FocusDetection", None)
        if callable(ParentEnter):
            ParentEnter(Event)
    # Вихід із зони наближення
    def Leave(self, Event):
        if self.Optics is not None:
            TargetFocus = getattr(self.Optics, "Focus", getattr(self.Optics, "Hover", None))
            if callable(TargetFocus):
                TargetFocus(False)
            self.update()
        ParentLeave = getattr(super(), "leaveEvent", None)
        if callable(ParentLeave):
            ParentLeave(Event)
    # Прив'язка системних подій до графічних методів
    paintEvent = OpticalDispersion
    resizeEvent = Rescale
    enterEvent = FocusDetection
    leaveEvent = Leave
    mousePressEvent = TouchContact
    mouseReleaseEvent = TouchRelease
    mouseMoveEvent = TouchMovement
    timerEvent = Pulse
    sizeHint = PreferredSize
    minimumSizeHint = PreferredSize
# =====================================================================
# ЕЛЕМЕНТИ ІНТЕРФЕЙСУ — семантичні оркестратори та композиційні вузли
# Базовий клас Element — віртуальна конструкція, що координує фізичні поверхні
# =====================================================================
class Element(Component):
    TypeName = "LCARSElement"
    Type = "Element"
    ElementType = "Composite"
    # Склад та просторове розміщення
    Items: Dict[str, Component] = {}
    Spacing = 6.0       # Фірмовий зазор Окуди між компонентами
    Orientation = "horizontal"  # horizontal або vertical
    Visible = True
    SurfaceHost = None
    Tactile = False
    Interactive = False

    def show(self):
        self.Visible = True
        if self.SurfaceHost and hasattr(self.SurfaceHost, "show"):
            self.SurfaceHost.show()
        return self

    def hide(self):
        self.Visible = False
        if self.SurfaceHost and hasattr(self.SurfaceHost, "hide"):
            self.SurfaceHost.hide()
        return self

    def isVisible(self):
        return bool(self.Visible)

    def GetSurface(self):
        if self.SurfaceHost is None:
            SurfaceClass = LCARS.Retrieve("Base.Interface.Surface") or Surface
            ParentRef = getattr(self, "Parent", None)
            ParentSurface = getattr(ParentRef, "SurfaceHost", None)
            if ParentSurface is None and ParentRef is not None:
                GetParentSurface = getattr(ParentRef, "GetSurface", None)
                if callable(GetParentSurface):
                    ParentSurface = GetParentSurface()
                else:
                    ParentSurface = ParentRef
            self.SurfaceHost = SurfaceClass(ParentSurface) if ParentSurface is not None else SurfaceClass()
            if hasattr(self.SurfaceHost, "Initialize"):
                self.SurfaceHost.Initialize(Optics=self, Parent=ParentSurface)
        return self.SurfaceHost

    def Surface(self):
        return self.GetSurface()

    def Show(self):
        Host = self.GetSurface()
        if hasattr(Host, "show"):
            Host.show()
        return self

    show = Show

    def ShowFullScreen(self):
        Host = self.GetSurface()
        if hasattr(Host, "showFullScreen"):
            Host.showFullScreen()
        elif hasattr(Host, "show"):
            Host.show()
        return self

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

    def SetState(self, State, Visited=None):
        if Visited is None:
            Visited = set()
        ObjId = id(self)
        if ObjId in Visited:
            return self
        Visited.add(ObjId)

        self.State = str(State or "Normal")
        for Child in list(self.Items.values()):
            if hasattr(Child, "SetState") and callable(Child.SetState):
                try:
                    Child.SetState(State, Visited)
                except TypeError:
                    Child.SetState(State)
            else:
                Child.State = self.State
                if hasattr(Child, "Refresh"):
                    Child.Refresh()
        self.Refresh()
        return self

    def SetPower(self, PowerVal: bool, Visited=None):
        if Visited is None:
            Visited = set()
        ObjId = id(self)
        if ObjId in Visited:
            return self
        Visited.add(ObjId)

        self.Power = bool(PowerVal)
        for Child in list(self.Items.values()):
            if hasattr(Child, "SetPower") and callable(Child.SetPower):
                try:
                    Child.SetPower(PowerVal, Visited)
                except TypeError:
                    Child.SetPower(PowerVal)
            else:
                Child.Power = self.Power
                Child.Tactile = self.Power and not getattr(Child, "Locked", False)
                if hasattr(Child, "Refresh"):
                    Child.Refresh()
        self.Refresh()
        return self

    # Додає новий компонент або лейаут у композицію
    def Add(self, *Arguments):
        if not Arguments:
            return self

        if self.Layout is None:
            Host = self.GetSurface()
            if hasattr(Host, "layout") and Host.layout() is not None:
                self.Layout = Host.layout()
            else:
                self.SetVertical(0, 0, 0, 0, 0)

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

        from lcars.base.component import Component
        if isinstance(Item, Component):
            ChildKey = str(getattr(Item, "Name", "") or id(Item))
            self.Items[ChildKey] = Item
            Item.Parent = self

        TargetSurface = getattr(Item, "SurfaceHost", None)
        if TargetSurface is None:
            GetItemSurface = getattr(Item, "GetSurface", None)
            if callable(GetItemSurface):
                TargetSurface = GetItemSurface()
            else:
                from lcars.base.component import Component
                if isinstance(Item, Component):
                    SurfaceClass = LCARS.Retrieve("Base.Interface.Surface") or Surface
                    TargetSurface = SurfaceClass()
                    if hasattr(TargetSurface, "Initialize"):
                        TargetSurface.Initialize(Optics=Item)
                    Item.SurfaceHost = TargetSurface
                    Item.Parent = self
                else:
                    TargetSurface = Item

        if hasattr(TargetLayout, "addWidget") and (not hasattr(Item, "addWidget") or TargetSurface is not Item):
            IsQtLayout = hasattr(TargetLayout, "count") and hasattr(TargetLayout, "indexOf")
            IsQtWidget = hasattr(TargetSurface, "inherits") or type(TargetSurface).__name__ in ("QWidget", "Display")
            if not IsQtLayout or IsQtWidget:
                if Stretch is None:
                    TargetLayout.addWidget(TargetSurface)
                else:
                    TargetLayout.addWidget(TargetSurface, int(Stretch))
            if hasattr(TargetSurface, "show"):
                TargetSurface.show()
        elif hasattr(TargetLayout, "addLayout"):
            SubLayout = getattr(Item, "Layout", Item)
            TargetLayout.addLayout(SubLayout)
        return self
    # 
    def SetVertical(self, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        LayoutClass = LCARS.Retrieve("Base.Interface.Layout.Vertical")
        if LayoutClass and callable(LayoutClass):
            Host = self.GetSurface()
            self.Layout = LayoutClass()
            if hasattr(Host, "setLayout"):
                Host.setLayout(self.Layout)
            if hasattr(self.Layout, "setContentsMargins"):
                self.Layout.setContentsMargins(Left, Top, Right, Bottom)
            if hasattr(self.Layout, "setSpacing"):
                self.Layout.setSpacing(Spacing)
        return self.Layout
    # 
    def SetHorizontal(self, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        LayoutClass = LCARS.Retrieve("Base.Interface.Layout.Horizontal")
        if LayoutClass and callable(LayoutClass):
            Host = self.GetSurface()
            self.Layout = LayoutClass()
            if hasattr(Host, "setLayout"):
                Host.setLayout(self.Layout)
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
    def Synthesize(self, Visited=None):
        if Visited is None:
            Visited = set()
        ObjId = id(self)
        if ObjId in Visited:
            return self
        Visited.add(ObjId)

        CurX = 0.0
        CurY = 0.0
        TotalW = 0.0
        TotalH = 0.0
        for Node in list(self.Items.values()):
            import math
            if not hasattr(Node, "Width") or not hasattr(Node, "Height"):
                continue
            Node.X = int(CurX)
            Node.Y = int(CurY)
            NW = float(getattr(Node, "Width", 0) or 0)
            NH = float(getattr(Node, "Height", 0) or 0)
            if math.isnan(NW) or math.isinf(NW) or NW > 16384.0:
                NW = 100.0
            if math.isnan(NH) or math.isinf(NH) or NH > 16384.0:
                NH = 30.0

            SafeX = max(0.0, min(16384.0, CurX))
            SafeY = max(0.0, min(16384.0, CurY))
            if math.isnan(SafeX) or math.isinf(SafeX):
                SafeX = 0.0
            if math.isnan(SafeY) or math.isinf(SafeY):
                SafeY = 0.0

            Node.X = int(SafeX)
            Node.Y = int(SafeY)
            if hasattr(Node, "Synthesize") and callable(Node.Synthesize):
                try:
                    Node.Synthesize(Visited)
                except TypeError:
                    Node.Synthesize()
            if self.Orientation == "horizontal":
                CurX += float(Node.Width) + self.Spacing
                CurX += NW + self.Spacing
                TotalW = CurX
                TotalH = max(TotalH, float(Node.Height))
                TotalH = max(TotalH, NH)
            else:
                CurY += float(Node.Height) + self.Spacing
                CurY += NH + self.Spacing
                TotalH = CurY
                TotalW = max(TotalW, float(Node.Width))
                TotalW = max(TotalW, NW)
        if self.Items:
            self.Width = int(TotalW)
            self.Height = int(TotalH)
            self.Width = int(max(10.0, min(16384.0, TotalW)))
            self.Height = int(max(10.0, min(16384.0, TotalH)))
        return self
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

    def Show(self):
        Host = self.GetSurface()
        if hasattr(Host, "setWindowFlags"):
            FramelessFlag = LCARS.Retrieve(getattr(LCARS, "Frameless", None))
            CurFlags = Host.windowFlags()
            if CurFlags is not None and FramelessFlag is not None and not isinstance(FramelessFlag, str):
                Host.setWindowFlags(CurFlags | FramelessFlag)
        if hasattr(Host, "setStyleSheet"):
            Host.setStyleSheet("background-color: #000000;")
        if hasattr(Host, "showFullScreen"):
            Host.showFullScreen()
        elif hasattr(Host, "show"):
            Host.show()
        return self

    show = Show

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
    Width = 20
    Height = 80
    MinWidth = 20
    MinHeight = 40
    PaddMinWidth = 20
    PaddMinHeight = 40
    Portable = True
    PaddAction = ""
    PaddStartGlobal = (0, 0)
    PaddStartRect = (0, 0, 0, 0)
    PaddOffset = (0, 0)
    # Все наслідується чисто і без помилок сигнатури!
    def ConfigurePadd(self):
        Host = self.GetSurface()
        if Host is not None:
            Host.PaddController = self
        if hasattr(Host, "setMinimumSize"):
            Host.setMinimumSize(self.MinWidth, self.MinHeight)

        # Обмежити розмір PADD доступною площею екрану (90%)
        PaddW = self.Width
        PaddH = self.Height
        App = LCARS.Application.instance() if hasattr(LCARS, "Application") else None
        if App and hasattr(App, "primaryScreen"):
            ScreenRef = App.primaryScreen()
            if ScreenRef and hasattr(ScreenRef, "availableGeometry"):
                Avail = ScreenRef.availableGeometry()
                MaxW = int(Avail.width() * 0.9)
                MaxH = int(Avail.height() * 0.9)
                if PaddW > MaxW:
                    PaddW = MaxW
                if PaddH > MaxH:
                    PaddH = MaxH

        if hasattr(Host, "resize"):
            Host.resize(self.Width, self.Height)
            Host.resize(PaddW, PaddH)

        OriginalResize = getattr(Host, "resizeEvent", None)
        PaddSelf = self

        def PaddResizeHook(Event):
            PaddSelf.AdaptPaddGeometry(Event)
            if OriginalResize:
                OriginalResize(Event)
        Host.resizeEvent = PaddResizeHook

        FramelessFlag = LCARS.Retrieve(getattr(LCARS, "Frameless", None))
        CurFlags = Host.windowFlags()
        if hasattr(Host, "setWindowFlags") and CurFlags is not None and FramelessFlag is not None and not isinstance(FramelessFlag, str):
            Host.setWindowFlags(CurFlags | FramelessFlag)
        if hasattr(Host, "setStyleSheet"):
            Host.setStyleSheet("background-color: #000000;")
        if hasattr(Host, "setSizePolicy"):
            Policy = getattr(LCARS, "Policy", None)
            if Policy and hasattr(Policy, "Preferred"):
                Host.setSizePolicy(Policy.Preferred, Policy.Preferred)

        # Центрувати PADD на екрані
        if App and hasattr(App, "primaryScreen"):
            ScreenRef = App.primaryScreen()
            if ScreenRef and hasattr(ScreenRef, "availableGeometry") and hasattr(Host, "move"):
                Avail = ScreenRef.availableGeometry()
                CenterX = Avail.x() + (Avail.width() - PaddW) // 2
                CenterY = Avail.y() + (Avail.height() - PaddH) // 2
                Host.move(CenterX, CenterY)

        self.EnablePortablePadd(Host)

    def Show(self):
        self.ConfigurePadd()
        Host = self.GetSurface()
        if hasattr(Host, "show"):
            Host.show()
        return self

    show = Show

    def AdaptPaddGeometry(self, Event):
        Host = self.GetSurface()
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
            if Target is None:
                continue
            TargetSurface = getattr(Target, "SurfaceHost", None)
            if TargetSurface is None:
                GetTargetSurface = getattr(Target, "GetSurface", None)
                if callable(GetTargetSurface):
                    TargetSurface = GetTargetSurface()
                else:
                    TargetSurface = Target
            if TargetSurface is None:
                continue
            TargetSurface.mousePressEvent = self.PaddPress
            TargetSurface.mouseMoveEvent = self.PaddMove
            TargetSurface.mouseReleaseEvent = self.PaddRelease

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

    def PaddPress(self, *Args, **Kwargs):
        Event = None
        if len(Args) >= 1 and not isinstance(Args[0], (int, float)):
            Event = Args[0]

        Host = self.GetSurface()
        if not Host:
            return None

        GX, GY = (0, 0)
        if Event is not None:
            GX, GY = self.EventGlobal(Event)
            self.PaddStartGlobal = (GX, GY)
        if hasattr(Host, "geometry"):
            Geom = Host.geometry()
            self.PaddStartRect = (Geom.x(), Geom.y(), Geom.width(), Geom.height())

        # Локальні координати всередині головного скла PADD
        HX = GX - self.PaddStartRect[0]
        HY = GY - self.PaddStartRect[1]

        Margin = 16
        W = Host.width() if hasattr(Host, "width") else 0
        H = Host.height() if hasattr(Host, "height") else 0
        
        Action = ""
        if HY < Margin: Action += "top"
        elif HY > H - Margin: Action += "bottom"
        
        if HX < Margin: Action += "left"
        elif HX > W - Margin: Action += "right"
        self.PaddAction = Action or "move"

        if Event is not None and hasattr(Event, "accept"):
            Event.accept()
        return None

    def PaddMove(self, Event):
        if not self.PaddAction:
            return
        Host = self.GetSurface()
        if not Host:
            return
        GX, GY = self.EventGlobal(Event)
        X, Y, W, H = self.PaddStartRect
        DX = GX - self.PaddStartGlobal[0]
        DY = GY - self.PaddStartGlobal[1]

        if self.PaddAction == "move":
            Host.move(X + DX, Y + DY)
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

    def PaddEdgeAction(self, X, Y):
        Host = self.GetSurface()
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
Segment = Element
StatusLine = StatBar
HeaderFrame = Header
FrameBracket = Bracket
AccessCode = AccessPanel
Access = AccessPanel

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
