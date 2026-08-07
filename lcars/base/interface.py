# LCARS FRAMEWORK
# Готові елементи інтерфейсу LCARS.
# У component.py лежить база. Тут лежать готові складені об'єкти.
# Назви без LCARS, бо цей модуль уже є частиною LCARS.
from __future__ import annotations
from typing import Any
from lcars.base.component import (
    Component,
    LCARSBar,
    LCARSButton,
    LCARSElbow,
    LCARSIndicator,
    LCARSLabel,
    Primitive,
    SetStyle,
    Take,
    Widget,
    Normalize,
)
from lcars.base.default import DefaultBackground, Palette, SetDisplayFlag
from lcars.base.type import LCARS
from lcars.core.signal import ODN
from lcars.base.version import getVersion
Version = getVersion()
# =====================================================================
# ЕЛЕМЕНТИ ІНТЕРФЕЙСУ — готові компоненти для швидкого створення інтерфейсу
# Базовий клас Element — спадкоємець Component, що надає контейнерну логіку
class Element(Component):
    # Пошук цільового вкладеного атрибуту за списком назв з обмеженням глибини
    def ResolveTarget(self, Item, NameList, Depth=0):
        if Item is None or Depth > 4:
            return None

        for Name in NameList:
            if not hasattr(Item, Name):
                continue

            Target = getattr(Item, Name)
            if Target is None or callable(Target):
                continue
            if Target is Item:
                continue

            # Рекурсивний пошук глибшого вкладеного елементу
            Nested = self.ResolveTarget(Target, NameList, Depth + 1)
            if Nested is not None:
                return Nested
            return Target

        return None

    # Отримання Widget-цілі з елементу або його Layout
    def WidgetTarget(self, Item):
        Target = self.ResolveTarget(Item, ("widget", "Widget"))
        if Target is not None:
            return Target
        Layout = self.ResolveTarget(Item, ("layout", "Layout"))
        if Layout is not None:
            return Layout
        return Item

    # Отримання Layout-цілі з елементу або вкладеного Widget
    def LayoutTarget(self, Item):
        Target = self.ResolveTarget(Item, ("layout", "Layout"))
        if Target is not None:
            return Target
        Target = self.ResolveTarget(Item, ("widget", "Widget"))
        if Target is not None:
            Inner = self.ResolveTarget(Target, ("layout", "Layout"))
            if Inner is not None:
                return Inner
        return Item

    # Ініціалізація Element з типом, батьком, кольором та додатковими аргументами
    def __init__(self, Type="panel", Parent=None, Color=None, **Args):
        Type = Take(Args, ["type", "Type"], Type)
        Parent = Take(Args, ["parent", "Parent"], Parent)
        Color = Take(Args, ["color", "Color", "ColorHexStr"], Color)
        Mode = Take(Args, ["mode", "Mode"], "")
        Frame = LCARS.Panel
        if Normalize(Type) in ["padd", "screen", "segment"]:
            Frame = LCARS.Segment

        Args["ComponentType"] = "container"
        Args["WidgetType"] = Frame
        super().__init__(Parent=Parent, Color=Color or DefaultBackground, **Args)
        self.Type = Normalize(Type) or "panel"
        self.Mode = Normalize(Mode)
        self.Color = Color or DefaultBackground
        self.Items = {}
        self.Value = Take(Args, ["value", "Value"], "")
        self.LabelText = Take(Args, ["label", "Label", "labelText", "LabelText"], "")
        self.Title = Take(Args, ["title", "Title"], "")
        self.ActionText = Take(Args, ["action", "Action", "actionText", "ActionText"], "")
        self.OnConfirm = Take(Args, ["onConfirm", "OnConfirm"], None)
        self.Owner = Take(Args, ["owner", "Owner"], None)
        self.BuildInterface()

    # Побудова інтерфейсу відповідно до типу елементу
    def BuildInterface(self):
        if self.Type == "padd":
            self.BuildPadd()
        elif self.Type == "screen":
            self.BuildScreen()
        elif self.Type == "segment":
            self.BuildSegment()
        elif self.Type == "header":
            self.BuildHeader()
        elif self.Type == "footer":
            self.BuildFooter()
        elif self.Type == "sidebar":
            self.BuildSidebar()
        elif self.Type == "menu":
            self.BuildMenu()
        elif self.Type == "toolbar":
            self.BuildToolbar()
        elif self.Type == "statusline":
            self.BuildStatusLine()
        elif self.Type == "datablock":
            self.BuildDataBlock()
        elif self.Type == "statbar":
            self.BuildStatBar()
        elif self.Type == "scanningbar":
            self.BuildScanningBar()
        elif self.Type == "overlay":
            self.BuildOverlay()
        elif self.Type == "stasis":
            self.BuildStasis()
        else:
            self.BuildPanel()

    # Створення вертикального layout з відступами та інтервалом
    def Vertical(self, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        VBox: Any = LCARS.Vertical
        GetLayout = getattr(self.widget, "layout", None)
        Layout = GetLayout() if GetLayout else None
        if not Layout:
            Layout = VBox()
            SetLayout = getattr(self.widget, "setLayout", None)
            if SetLayout:
                SetLayout(Layout)
        Layout.setContentsMargins(Left, Top, Right, Bottom)
        Layout.setSpacing(Spacing)
        self.Layout = Layout
        return Layout

    # Створення горизонтального layout з відступами та інтервалом
    def Horizontal(self, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        HBox: Any = LCARS.Horizontal
        GetLayout = getattr(self.widget, "layout", None)
        Layout = GetLayout() if GetLayout else None
        if not Layout:
            Layout = HBox()
            SetLayout = getattr(self.widget, "setLayout", None)
            if SetLayout:
                SetLayout(Layout)
        Layout.setContentsMargins(Left, Top, Right, Bottom)
        Layout.setSpacing(Spacing)
        self.Layout = Layout
        return Layout

    # Альтернативний виклик Vertical
    def LayoutV(self, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        return self.Vertical(Left, Top, Right, Bottom, Spacing)

    # Альтернативний виклик Horizontal
    def LayoutH(self, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        return self.Horizontal(Left, Top, Right, Bottom, Spacing)

    # Додавання віджету до layout з опціональним розтягуванням
    def Add(self, Layout, Element, Stretch=None):
        AddWidget = getattr(Layout, "addWidget", None)
        if not AddWidget:
            return
        Target = self.WidgetTarget(Element)
        if Stretch is None:
            AddWidget(Target)
        else:
            AddWidget(Target, Stretch)

    # Додавання вкладеного layout до батьківського layout
    def AddLayout(self, Layout, ChildLayout):
        AddLayout = getattr(Layout, "addLayout", None)
        if AddLayout:
            Target = self.LayoutTarget(ChildLayout)
            AddLayout(Target)

    # Додавання розтягу до layout
    def AddStretch(self, Layout):
        AddStretch = getattr(Layout, "addStretch", None)
        if AddStretch:
            AddStretch()

    # Очищення всіх дочірніх елементів layout з видаленням віджетів
    def Clear(self, Layout=None):
        if Layout is None:
            Layout = getattr(self.widget, "layout", lambda: None)()
            
        if not Layout:
            return
            
        Count = getattr(Layout, "count", lambda: 0)
        TakeAt = getattr(Layout, "takeAt", None)
        
        if TakeAt:
            while Count():
                Item = TakeAt(0)
                if Item:
                    WidgetRef = getattr(Item, "widget", lambda: None)()
                    if WidgetRef and hasattr(WidgetRef, "deleteLater"):
                        WidgetRef.deleteLater()
                    ChildLayout = getattr(Item, "layout", lambda: None)()
                    if ChildLayout:
                        self.Clear(ChildLayout)

    # Побудова базової панелі з чорним фоном
    def BuildPanel(self):
        SetStyle(self.widget, "background-color: #000000; border: none;")

    # Побудова прозорого сегменту без фону
    def BuildSegment(self):
        SetStyle(self.widget, "background-color: transparent; border: none;")

    # Побудова екрану: повний або внутрішній режим з Content-контейнером
    def BuildScreen(self):
        if self.Mode == "inner":
            SetStyle(self.widget, "background-color: #050505;")
            self.Vertical(8, 8, 8, 8, 6)
        else:
            self.Mode = "full"
            SetStyle(self.widget, "background-color: #000000; border: none;")
            if hasattr(self.widget, "setState"):
                self.widget.setState(LCARS.Frameless, True)
            self.Vertical(0, 0, 0, 0, 0)

        self.Items["Content"] = Panel(Parent=self.widget)
        self.Add(self.Layout, self.Items["Content"], 1)

    # Побудова PADD — портативного екрану-носія з внутрішнім шаром
    def BuildPadd(self):
        self.Mode = self.Mode or "portable"
        SetStyle(self.widget, "background-color: #000000; border: none;")
        self.PaddFullscreen = False
        self.PaddSavedGeometry = None
        if hasattr(self.widget, "setMinimumSize"):
            self.widget.setMinimumSize(320, 220)
        if hasattr(self.widget, "setSizePolicy"):
            Policy = LCARS.Policy
            if Policy:
                self.widget.setSizePolicy(Policy.Expanding, Policy.Expanding)

        # Padd сам є екраном-носієм; Content це внутрішній шар для інтерфейсу.
        Layout = self.Vertical(0, 0, 0, 0, 0)
        self.Items["Content"] = Element(Type="segment", Parent=self.widget)
        self.Items["Content"].Vertical(0, 0, 0, 0, 0)
        self.Items["Body"] = self.Items["Content"]
        self.Items["Body"].Items["Content"] = self.Items["Content"]
        if hasattr(self.Items["Content"].widget, "setSizePolicy"):
            Policy = LCARS.Policy
            if Policy:
                self.Items["Content"].widget.setSizePolicy(Policy.Expanding, Policy.Expanding)
        self.Add(Layout, self.Items["Content"], 1)

    # Побудова верхньої панелі з elbow, заголовком та смугою
    def BuildHeader(self):
        SetStyle(self.widget, "background-color: #000000; border: none;")
        Layout = self.Horizontal(0, 0, 0, 0, 8) 
        self.Items["Elbow"] = LCARSElbow(Direction="top-left", Color=Palette.Buttons[0], Text=self.Title, Parent=self.widget)
        self.Items["Title"] = LCARSIndicator(Text=self.Title, Type="title", Color=Palette.Buttons[2], Parent=self.widget)
        self.Items["Bar"] = LCARSBar(Type="bar", Height=10, Color=Palette.Buttons[1], Parent=self.widget)
        self.Add(Layout, self.Items["Elbow"])
        self.Add(Layout, self.Items["Title"], 1)
        self.Add(Layout, self.Items["Bar"])

    # Побудова нижньої панелі з смугою, статусом та elbow
    def BuildFooter(self):
        SetStyle(self.widget, "background-color: #000000; border: none;")
        Layout = self.Horizontal(0, 0, 0, 0, 8)
        self.Items["Bar"] = LCARSBar(Type="divider", Height=8, Color=Palette.Buttons[1], Parent=self.widget)
        self.Items["Status"] = LCARSIndicator(Text=self.Title or "READY", Type="status", Status="ready", Parent=self.widget)
        self.Items["Elbow"] = LCARSElbow(Direction="bottom-right", Color=Palette.Buttons[0], Parent=self.widget)
        self.Add(Layout, self.Items["Bar"], 1)
        self.Add(Layout, self.Items["Status"])
        self.Add(Layout, self.Items["Elbow"])

    # Побудова бічної панелі з верхнім/нижнім elbow та направляючою
    def BuildSidebar(self):
        SetStyle(self.widget, "background-color: #000000; border: none;")
        Layout = self.Vertical(0, 0, 0, 0, 6)
        self.Items["Top"] = LCARSElbow(Direction="top-left", Color=Palette.Buttons[0], Parent=self.widget)
        self.Items["Rail"] = Primitive(Shape="rect", Color=Palette.Buttons[1], Parent=self.widget)
        self.Items["Bottom"] = LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[2], Parent=self.widget)
        self.Add(Layout, self.Items["Top"])
        self.Add(Layout, self.Items["Rail"], 1)
        self.Add(Layout, self.Items["Bottom"])

    # Побудова вертикального меню з кнопками зі списку міток
    def BuildMenu(self):
        SetStyle(self.widget, "background-color: #000000; border: none;")
        Layout = self.LayoutV(0, 0, 0, 0, 6)
        Labels = self.Value if isinstance(self.Value, list) else ["SYSTEM", "PROGRAMS", "SETTINGS", "DIAGNOSTICS"]
        Index = 0
        for Lbl in Labels:
            Button = LCARSButton(Text=Lbl, Type="right", Color=Palette.Buttons[Index % len(Palette.Buttons)], Parent=self.widget)
            self.Items[f"Button{Index}"] = Button
            self.Add(Layout, Button)
            Index += 1
        self.AddStretch(Layout)

    # Побудова горизонтальної панелі інструментів з кнопками
    def BuildToolbar(self):
        SetStyle(self.widget, "background-color: #000000; border: none;")
        Layout = self.LayoutH(0, 0, 0, 0, 6)
        Labels = self.Value if isinstance(self.Value, list) else ["BACK", "HOME", "NEXT"]
        Index = 0
        for Lbl in Labels:
            Button = LCARSButton(Text=Lbl, Type="pill", Color=Palette.Buttons[Index % len(Palette.Buttons)], Parent=self.widget)
            self.Items[f"Tool{Index}"] = Button
            self.Add(Layout, Button)
            Index += 1
        self.AddStretch(Layout)

    # Побудова смуги статусу з індикатором та роздільником
    def BuildStatusLine(self):
        SetStyle(self.widget, "background-color: #000000; border: none;")
        Layout = self.LayoutH(0, 0, 0, 0, 8)
        self.Items["Status"] = LCARSIndicator(Text=self.Value or "READY", Type="status", Status="ready", Parent=self.widget)
        self.Items["Bar"] = LCARSBar(Type="divider", Height=4, Color=Palette.Accent[1], Parent=self.widget)
        self.Add(Layout, self.Items["Status"])
        self.Add(Layout, self.Items["Bar"], 1)

    # Побудова блоку даних з заголовком та значенням
    def BuildDataBlock(self):
        SetStyle(self.widget, "background: #080808;")
        Layout = self.LayoutV(12, 4, 8, 4, 0)
        self.Items["Label"] = LCARSIndicator(Text=self.LabelText, Type="title", Color=self.Color or Palette.Accent[1], Parent=self.widget)
        self.Items["Value"] = LCARSIndicator(Text=self.Value, Type="value", Color="#FFFFFF", Parent=self.widget)
        self.Add(Layout, self.Items["Label"])
        self.Add(Layout, self.Items["Value"])

    # Побудова смуги статистики з прогрес-баром та міткою
    def BuildStatBar(self):
        SetStyle(self.widget, "background-color: transparent; border: none;")
        Layout = self.LayoutH(0, 0, 0, 0, 10)
        MaxValue = 100
        Value = int(self.Value or 0)
        self.Items["Marker"] = Primitive(Shape="rect", Color=self.Color or Palette.Buttons[1], Parent=self.widget)
        self.Items["Label"] = LCARSIndicator(Text=self.Label, Type="label", Color=self.Color or Palette.Buttons[1], Parent=self.widget)
        Progress = LCARS.Progress
        if Progress:
            self.Items["Progress"] = Progress(self.widget)
        else:
            self.Items["Progress"] = LCARSBar(Type="bar", Height=12, Color=self.Color or Palette.Buttons[1], Parent=self.widget)
        if hasattr(self.Items["Progress"], "setObjectName"):
            self.Items["Progress"].setObjectName("LCARSProgress")
        if hasattr(self.Items["Progress"], "setTextVisible"):
            self.Items["Progress"].setTextVisible(False)
        if hasattr(self.Items["Progress"], "setRange"):
            self.Items["Progress"].setRange(0, MaxValue)
        if hasattr(self.Items["Progress"], "setValue"):
            self.Items["Progress"].setValue(Value)
        SetStyle(
            self.Items["Progress"],
            "#LCARSProgress { background: #111111; border: none; border-radius: 6px; }"
            f"#LCARSProgress::chunk {{ background: {self.Color or Palette.Buttons[1]}; border-radius: 5px; }}",
        )
        self.Add(Layout, self.Items["Marker"])
        self.Add(Layout, self.Items["Label"])
        self.Add(Layout, self.Items["Progress"], 1)

    # Побудова анімованої смуги сканування
    def BuildScanningBar(self):
        self.Phase = 0
        self.Scan = LCARSBar(Type="scanning", Height=15, Color=self.Color or Palette.Buttons[1], Parent=self.widget)
        SetStyle(self.widget, "background-color: transparent; border: none;")
        Layout = self.LayoutV(0, 0, 0, 0, 0)
        self.Add(Layout, self.Scan)

    # Побудова оверлею підтвердження дії з кнопками AUTHORIZE та ABORT
    def BuildOverlay(self):
        SetStyle(self.widget, "background-color: rgba(0, 0, 0, 240);")
        Layout = self.LayoutV(40, 40, 40, 40, 12)
        self.Items["Title"] = LCARSIndicator("SECURITY CLEARANCE AUTHORIZATION", Type="alert", Color=Palette.RedAlert[0], Parent=self.widget)
        self.Items["Message"] = LCARSIndicator(f"CRITICAL ACTION: {self.ActionText.upper()}", Type="label", Color=Palette.Panels[2], Parent=self.widget)
        self.Items["Confirm"] = LCARSButton("AUTHORIZE", Color=Palette.RedAlert[0], Type="pill", Parent=self.widget)
        self.Items["Cancel"] = LCARSButton("ABORT", Color="#555555", Type="pill", Parent=self.widget)
        self.Items["Confirm"].clicked.Connect(self.Accept)
        self.Items["Cancel"].clicked.Connect(self.Cleanup)
        ButtonLayout = self.Horizontal(0, 0, 0, 0)
        ButtonLayout.setSpacing(10)
        self.Add(Layout, self.Items["Title"])
        self.Add(Layout, self.Items["Message"])
        self.AddStretch(Layout)
        self.Add(ButtonLayout, self.Items["Confirm"])
        self.Add(ButtonLayout, self.Items["Cancel"])
        self.AddLayout(Layout, ButtonLayout)

    # Побудова екрану стазису з повідомленням про зупинку системи
    def BuildStasis(self):
        SetStyle(self.widget, "background-color: #000000; border: none;")
        Layout = self.LayoutV(0, 0, 0, 0, 0)
        self.Items["Label"] = LCARSIndicator("SYSTEM IN STASIS", Type="title", Color=Palette.Buttons[0], Parent=self.widget)
        self.Add(Layout, self.Items["Label"])
        self.widget.mousePressEvent = self.mousePressEvent

    # Встановлення значення та оновлення відповідних елементів
    def SetValue(self, Value):
        self.Value = Value
        Item = self.Items.get("Value")
        if Item and hasattr(Item, "SetValue"):
            Item.SetValue(Value)
        Progress = self.Items.get("Progress")
        if Progress and hasattr(Progress, "setValue"):
            Progress.setValue(int(Value))

    # Встановлення мітки та оновлення тексту Label-елементу
    def SetLabel(self, Label):
        self.Label = str(Label)
        Item = self.Items.get("Label")
        if Item and hasattr(Item, "SetText"):
            Item.SetText(Label)

    # Прийняття дії з викликом OnConfirm та очищенням
    def Accept(self):
        if self.OnConfirm:
            self.OnConfirm()
        self.Cleanup()

    # Видалення віджету з викликом deleteLater
    def Cleanup(self):
        Delete = getattr(self.widget, "deleteLater", None)
        if Delete:
            Delete()

    # Обробник натискання миші для пробудження власника
    def mousePressEvent(self, Event):
        WakeUp = getattr(self.Owner, "WakeUp", None)
        if WakeUp:
            WakeUp()

# РЕЄСТРАЦІЯ КЛАСІВ ІНТЕРФЕЙСУ В LCARS
# Padd — це спеціальний тип панелі з верхньою і нижньою смугами, який можна використовувати для створення виділених областей інтерфейсу.
class PADD(Element):
    # Ініціалізація PADD з розмірами, мінімальними обмеженнями та портативністю
    def __init__(self, Parent=None, **Args):
        Width = Take(Args, ["width", "Width"], 920)
        Height = Take(Args, ["height", "Height"], 580)
        MinWidth = Take(Args, ["minWidth", "MinWidth"], 520)
        MinHeight = Take(Args, ["minHeight", "MinHeight"], 340)
        Portable = Take(Args, ["portable", "Portable"], Parent is None)
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
        super().__init__(Type="padd", Parent=Parent, **Args)
        self.ConfigurePadd()

    # Налаштування базових розмірів, хука resize та portable-режиму PADD
    def ConfigurePadd(self):
        # Налаштовуємо базові розміри PADD
        Host = self.widget
        if hasattr(Host, "setMinimumSize"):
            Host.setMinimumSize(self.PaddMinWidth, self.PaddMinHeight)
        if hasattr(Host, "setMaximumSize"):
            Host.setMaximumSize(16777215, 16777215)
        if hasattr(Host, "resize"):
            Host.resize(self.PaddStartWidth, self.PaddStartHeight)

        # Зберігаємо оригінальний resizeEvent для подальшого виклику
        OriginalResize = getattr(Host, "resizeEvent", None)
        PaddSelf = self

        # Обгортаємо resizeEvent для виклику адаптації контенту при зміні розміру
        def PaddResizeHook(Event):
            PaddSelf.OnPaddResize(Event)
            if OriginalResize:
                OriginalResize(Event)
        Host.resizeEvent = PaddResizeHook

        # Якщо Padd без батьківського елементу — робимо його безрамковим вікном
        if self.PaddPortable:
            from PyQt6.QtCore import Qt
            SetFrameless = getattr(Host, "setWindowFlag", None)
            if SetFrameless:
                SetFrameless(Qt.WindowType.FramelessWindowHint, True)
            SetTranslucent = getattr(Host, "setAttribute", None)
            if SetTranslucent:
                SetTranslucent(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            if hasattr(Host, "setSizePolicy"):
                Policy = LCARS.Policy
                if Policy:
                    Host.setSizePolicy(Policy.Expanding, Policy.Expanding)
            # Увімкнення перетягування та resize для portable PADD
            self.EnablePortablePadd(Host)

    # Поточні розміри PADD (оновлюється при resize)
    PaddCurrentWidth = 0
    PaddCurrentHeight = 0

    # Показати PADD на екрані
    def show(self):
        Host = self.widget
        if Host and hasattr(Host, "show"):
            Host.show()

    # Обробник зміни розміру PADD — оновлює відступи та spacing контенту
    def OnPaddResize(self, Event):
        Host = self.widget
        if not Host:
            return
        # Отримуємо поточні розміри вікна
        W = Host.width() if hasattr(Host, "width") else 0
        H = Host.height() if hasattr(Host, "height") else 0
        if W < 1 or H < 1:
            return

        # Адаптивні відступи: зменшуємо при малих розмірах, збільшуємо при великих
        Margin = max(4, min(20, W // 50, H // 50))
        Spacing = max(2, min(8, Margin // 2))

        # Оновлюємо відступи внутрішнього контенту
        Content = self.Items.get("Content")
        if Content is not None:
            ContentLayout = getattr(Content, "Layout", None)
            if ContentLayout and hasattr(ContentLayout, "setContentsMargins"):
                ContentLayout.setContentsMargins(Margin, Margin, Margin, Margin)
                ContentLayout.setSpacing(Spacing)

        # Зберігаємо розміри для використання підкласами
        self.PaddCurrentWidth = W
        self.PaddCurrentHeight = H

    # Увімкнення перетягування та зміни розміру для portable PADD
    def EnablePortablePadd(self, Host=None):
        Targets = [
        Host,
        self.Items.get("Body"),
        ]

        for Target in Targets:
            TargetWidget = self.WidgetTarget(Target)

            if TargetWidget is None:
                continue

            TargetWidget.mousePressEvent = self.PaddPress
            TargetWidget.mouseMoveEvent = self.PaddMove
            TargetWidget.mouseReleaseEvent = self.PaddRelease

    # Отримання глобальних координат події (сумісність з різними API)
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

    # Отримання локальних координат події (сумісність з різними API)
    def EventLocal(self, Event):
        Method = getattr(Event, "position", None)
        if Method:
            Point = Method()
            Convert = getattr(Point, "toPoint", None)
            if Convert:
                Point = Convert()
            return int(Point.x()), int(Point.y())
        Method = getattr(Event, "pos", None)
        if Method:
            Point = Method()
            return int(Point.x()), int(Point.y())
        return 0, 0

    # Обробник натискання миші — визначення позиції та типу дії (move/resize)
    def PaddPress(self, Event):
        Host = self.widget
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
        self.PaddOffset = (GX - self.PaddStartRect[0], GY - self.PaddStartRect[1])
        self.PaddAction = self.PaddEdgeAction(LX, LY)
        Accept = getattr(Event, "accept", None)
        if Accept:
            Accept()

    # Обробник руху миші — виконання move або resize з обмеженнями мінімального розміру
    def PaddMove(self, Event):
        if not self.PaddAction:
            return
        Host = self.widget
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

        # Обмеження мінімальних розмірів при зміні розміру
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
        Accept = getattr(Event, "accept", None)
        if Accept:
            Accept()

    # Обробник відпускання миші — скидання поточної дії
    def PaddRelease(self, Event):
        self.PaddAction = ""
        Accept = getattr(Event, "accept", None)
        if Accept:
            Accept()

    # Перемикання між повноекранним та звичайним режимом PADD
    def ToggleFullscreen(self):
        Host = self.widget
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

    # Визначення типу дії за позицією миші відносно країв вікна
    def PaddEdgeAction(self, X, Y):
        Host = self.widget
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

# Screen — це основний контейнер для інтерфейсу, який зазвичай займає весь простір і містить інші елементи. 
class Screen(Element):
    # Ініціалізація Screen з батьківським елементом та додатковими аргументами
    def __init__(self, Parent=None, **Args):
        super().__init__(Type="screen", Parent=Parent, **Args)

# Panel — це базовий контейнер для групування елементів. Він має просту чорну заливку і може містити інші елементи.
class Panel(Element):
    # Ініціалізація Panel з батьківським елементом та додатковими аргументами
    def __init__(self, Parent=None, **Args):
        super().__init__(Type="panel", Parent=Parent, **Args)

# Register Panel in LCARS namespace for backwards compatibility
from lcars.base.type import LCARS
LCARS.Panel = Panel

# Segment — це прозорий контейнер, який можна використовувати для створення розділів або сегментів інтерфейсу. Він не має фону і може містити інші елементи.
class Segment(Element):
    # Ініціалізація Segment з батьківським елементом та додатковими аргументами
    def __init__(self, Parent=None, **Args):
        super().__init__(Type="segment", Parent=Parent, **Args)

# Register Segment in LCARS namespace for backwards compatibility
from lcars.base.type import LCARS
LCARS.Segment = Segment

# Інші елементи інтерфейсу, такі як Header, Footer, Sidebar, Menu, Toolbar, StatusLine, DataBlock, StatBar, ScanningBar, Confirmation та Stasis, також реалізовані як підкласи Element з відповідними стилями та компонентами.
class Header(Element):
    # Ініціалізація Header з заголовком та батьківським елементом
    def __init__(self, Title="", Parent=None, **Args):
        super().__init__(Type="header", Parent=Parent, Title=Title, **Args)

# Footer — це нижня панель, яка зазвичай містить статусну інформацію або інші елементи. Вона має чорний фон і може містити індикатор статусу та інші компоненти.
class Footer(Element):
    # Ініціалізація Footer з заголовком та батьківським елементом
    def __init__(self, Title="", Parent=None, **Args):
        super().__init__(Type="footer", Parent=Parent, Title=Title, **Args)

# Sidebar — це вертикальна панель з лівого боку, яка може містити навігаційні елементи або інші компоненти. Вона має чорний фон і акцентні кольори для верхньої та нижньої частин.
class Sidebar(Element):
    # Ініціалізація Sidebar з батьківським елементом та додатковими аргументами
    def __init__(self, Parent=None, **Args):
        super().__init__(Type="sidebar", Parent=Parent, **Args)

# Menu — це вертикальний список кнопок, який можна використовувати для створення меню навігації або вибору. Він має чорний фон і кольорові кнопки.
class Menu(Element):
    # Ініціалізація Menu зі списком пунктів та батьківським елементом
    def __init__(self, Items=None, Parent=None, **Args):
        super().__init__(Type="menu", Parent=Parent, Value=Items or [], **Args)

# Toolbar — це горизонтальна панель з кнопками, яка зазвичай розташовується вгорі або внизу екрану. Вона має чорний фон і кольорові кнопки для навігації або виконання дій.
class Toolbar(Element):
    # Ініціалізація Toolbar зі списком пунктів та батьківським елементом
    def __init__(self, Items=None, Parent=None, **Args):
        super().__init__(Type="toolbar", Parent=Parent, Value=Items or [], **Args)

# StatusLine — це горизонтальна панель, яка зазвичай розташовується внизу екрану і містить статусну інформацію. Вона має чорний фон і індикатор статусу.
class StatusLine(Element):
    # Ініціалізація StatusLine з текстом статусу та батьківським елементом
    def __init__(self, Text="READY", Parent=None, **Args):
        super().__init__(Type="statusline", Parent=Parent, Value=Text, **Args)

# DataBlock — це спеціальний елемент, який відображає заголовок і значення. Він має темний фон і акцентну ліву смугу.
class DataBlock(Element):
    # Ініціалізація DataBlock з міткою, значенням, батьком та кольором
    def __init__(self, LabelText="", ValueText="", Parent=None, Color=None, **Args):
        super().__init__(Type="datablock", Parent=Parent, Color=Color, Label=LabelText, Value=ValueText, **Args)

# StatBar — це горизонтальна смуга, яка відображає прогрес або рівень. Вона має прозорий фон і кольорову індикаторну смугу, яка заповнюється відповідно до значення.
class StatBar(Element):
    # Ініціалізація StatBar з міткою, значенням, батьком та кольором
    def __init__(self, LabelText="", Value=0, Parent=None, Color=None, **Args):
        super().__init__(Type="statbar", Parent=Parent, Color=Color, Label=LabelText, Value=Value, **Args)

# ScanningBar — це анімована смуга, яка створює ефект сканування. Вона має прозорий фон і кольорову смугу, яка рухається зліва направо.
class ScanningBar(Element):
    # Ініціалізація ScanningBar з кольором та батьківським елементом
    def __init__(self, ColorVal=None, Parent=None, **Args):
        ColorVal = Take(Args, ["color", "Color", "ColorHexStr"], ColorVal)
        super().__init__(Type="scanningbar", Parent=Parent, Color=ColorVal, **Args)

# Confirmation — це елемент, який відображає підтвердження дії перед її виконанням. Він має прозорий фон і кольорові кнопки.
class Confirmation(Element):
    # Ініціалізація Confirmation з текстом дії, обробником підтвердження та батьком
    def __init__(self, ActionText="", OnConfirm=None, Parent=None, **Args):
        super().__init__(Type="overlay", Parent=Parent, ActionText=ActionText, OnConfirm=OnConfirm, **Args)

# Stasis — це спеціальний елемент, який відображає повідомлення про те, що система знаходиться в стані стазису. Він має чорний фон і великий заголовок.
class Stasis(Element):
    # Ініціалізація Stasis з власником та батьківським елементом
    def __init__(self, Owner=None, Parent=None, **Args):
        super().__init__(Type="stasis", Parent=Parent, Owner=Owner, **Args)

# Аліаси для зворотної сумісності
LCARSPadd = PADD
Padd = PADD
LCARSPanel = Panel
LCARSMenu = Menu

# LCARSProgramPanel — аліас Segment з підтримкою accent_color та title (Titanium-сумісність)
# Backward-compat base for panels that use BuildUi(layout) pattern.
# Previously was in lcars.modules.ui_manager.
class LCARSProgramPanel(Segment):
    # Ініціалізація LCARSProgramPanel з заголовком, кольором accent та посиланнями на вузли
    def __init__(self, title="", accent_color=None, DesktopNodeRef=None, ParentNode=None, *args, **kwargs):
        super().__init__(Parent=ParentNode or kwargs.pop("parent", None), **kwargs)
        self.title = title
        self.accent_color = accent_color or "#FF9900"
        self.DesktopNode = DesktopNodeRef

        RootLayout = self.Vertical(0, 0, 0, 0, 0)
        self.BuildUi(RootLayout)

    # Переозначення у підкласах для заповнення панелі елементами
    # Override in subclasses to populate the panel.
    def BuildUi(self, layout):
        pass

# LCARSContour — backward-compat alias for Segment (used in library.py)
LCARSContour = Segment

# Backward-compatible names used by older panels and learning screens.
Dialog = "Interface.Dialog"
MessageBox = "Interface.Dialog.Message"
Splitter = "Interface.Splitter"
TextCursor = "Visual.TextCursor"
RadioButton = "Interface.Button.Radio"
ProgressBar = "Interface.Progress"
LineEdit = "Interface.Input"
Widget = "Interface.Widget"
Frame = "Interface.Frame"
Label = "Interface.Label"
GridLayout = "Interface.Layout.Grid"
ScrollArea = "Interface.Scroll"
ListWidget = "Interface.Select.List"
ListWidgetItem = "Interface.Select.ListItem"
PushButton = LCARSButton

# Група кнопок для керування станом вибору
class ButtonGroup:
    # Ініціалізація порожньої групи кнопок
    def __init__(self):
        self._buttons_list = []

    # Додавання кнопки до групи
    def AddButton(self, button):
        self._buttons_list.append(button)

    addButton = AddButton

    # Отримання списку всіх кнопок у групі
    def Buttons(self):
        return list(self._buttons_list)

    buttons = Buttons

    # Пошук поточної вибраної кнопки серед групи
    def CheckedButton(self):
        for button in self._buttons_list:
            if hasattr(button, "isChecked") and button.isChecked():
                return button
        return self._buttons_list[0] if self._buttons_list else None

    checkedButton = CheckedButton

__all__ = [
    "Element",
    "Panel",
    "Screen",
    "Segment",
    "Header",
    "Footer",
    "Sidebar",
    "Menu",
    "Toolbar",
    "StatusLine",
    "DataBlock",
    "StatBar",
    "ScanningBar",
    "Confirmation",
    "Stasis",
    "LCARSLabel",
    "PADD",
    "LCARSPadd",
    "LCARSPanel",
    "Padd",
    "LCARSProgramPanel",
    "LCARSContour",
]
