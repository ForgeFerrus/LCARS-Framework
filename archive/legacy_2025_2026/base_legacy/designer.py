# LCARS FRAMEWORK v1.0.0-GOLD
# ◤ TITANIUM CONSTRUCTOR — середовище проектування UI + точка запуску (No-Q)
# Об'єднано: колишні designer (полотно, сайдбар, експорт) та boot-шар вікна.
# ─────────────────────────────────────────────────────────────────────────────

import sys
from typing import Any, List, Optional, Tuple, Type, Union
from lcars.base.type import Matrix, Directive, LCARS
Primitives = LCARS
from lcars.base.register import registry
from lcars.base.graphic import Graphic

# ==============================================================================
# INTERNAL GRAPHIC DRAWING WIDGETS (для дизайнера)
# ==============================================================================
class DesignSegment(LCARS.Segment):
    def __init__(self, parent=None, owner=None):
        super().__init__(parent)
        self.owner = owner
        
    def paintEvent(self, event):
        if self.owner and hasattr(self.owner, "paintEvent"):
            self.owner.paintEvent(event)
        else:
            super().paintEvent(event)

class DesignPanel(LCARS.Panel):
    def __init__(self, parent=None, owner=None):
        super().__init__(parent)
        self.owner = owner

    def paintEvent(self, event):
        if self.owner and hasattr(self.owner, "paintEvent"):
            self.owner.paintEvent(event)
        else:
            super().paintEvent(event)

# ==============================================================================
# DESIGNER BASE CLASS — базовий клас для дизайнера з утилітами
# ==============================================================================
class DesignerGraphic(Graphic):
    # Базовий клас для дизайнерських компонентів з дизайн-утилітами
    def __getattr__(self, name):
        if hasattr(self.widget, name):
            return getattr(self.widget, name)
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")
    
    def CreateLayout(self, layoutType="VBox", margins=None, spacing=None):
        if layoutType == "VBox":
            LayoutClass = registry.Get("Layout.VBox")
        elif layoutType == "HBox":
            LayoutClass = registry.Get("Layout.HBox")
        elif layoutType == "HMatrix":
            LayoutClass = LCARS.HMatrix
        elif layoutType == "VMatrix":
            LayoutClass = LCARS.VMatrix
        else:
            LayoutClass = registry.Get(f"Layout.{layoutType}")
        
        layout = LayoutClass(self)
        
        if margins:
            layout.setContentsMargins(*margins)
        else:
            layout.setContentsMargins(14, 14, 14, 14)
            
        if spacing:
            layout.setSpacing(spacing)
        else:
            layout.setSpacing(10)
        
        return layout
    
    def CreateLabel(self, text, color=None, fontSize=10):
        from lcars.base.component import LCARSLabel
        from lcars.base.default import Palette
        lbl = LCARSLabel(text.upper(), Parent=self)
        if color is None:
            color = Palette.Panels[2]
        lbl.setStyleSheet(
            f"color: {color}; font-size: {fontSize}pt;"
            " font-family: 'LCARS'; font-weight: bold;"
            " letter-spacing: 1.5px; background: transparent;"
        )
        return lbl
    
    def CreateSeparator(self, height=3, color=None):
        from lcars.base.component import LCARSBar
        from lcars.base.default import Palette
        if color is None:
            color = Palette.Buttons[2]
        sep = LCARSBar(Height=height, Parent=self)
        sep.IsTool = True
        return sep
    
    def AddLabel(self, text, color=None, fontSize=10, layout=None):
        lbl = self.CreateLabel(text, color, fontSize)
        if layout is None and hasattr(self, 'Layout'):
            layout = self.Layout
        if layout:
            layout.addWidget(lbl)
        return lbl
    
    def AddSeparator(self, height=3, color=None, layout=None):
        sep = self.CreateSeparator(height, color)
        if layout is None and hasattr(self, 'Layout'):
            layout = self.Layout
        if layout:
            layout.addWidget(sep)
        return sep
    
    def CreateSpinBox(self, minVal=0, maxVal=3000):
        SpinCls = LCARS.Input
        spin = SpinCls()
        spin.setRange(minVal, maxVal)
        spin.setStyleSheet(
            "background: #1a1a2e; color: #fff; border: 1px solid #336699; "
            "padding: 2px; border-radius: 4px;"
        )
        return spin
    
    def CreateButton(self, text, color=None, width=68, height=28):
        from lcars.base.component import LCARSButton
        btn = LCARSButton(text, Parent=self)
        btn.setFixedSize(width, height)
        btn.widget.setStyleSheet("font-size: 8pt;")
        return btn

# ==============================================================================
# INFO PAD — Панель інформації та редагування властивостей
# ==============================================================================
class InfoPad(DesignerGraphic):
    # ◤ ПАНЕЛЬ ІНФОРМАЦІЇ ТА РЕДАГУВАННЯ — повний функціонал ◢
    PAD_WIDTH = 260
    def __init__(self, Parent=None):
        from lcars.base.component import LCARSLabel, LCARSBar, LCARSButton
        super().__init__(Parent)
        self.IsTool = True
        self._block_signals = False
        self.setFixedWidth(self.PAD_WIDTH)
        self.setStyleSheet("background-color: #000000;")

        self.Layout = self.CreateLayout("VBox")

        self.TitleLbl = self.AddLabel("◤ PROPERTIES", fontSize=12)
        self.TitleLbl.IsTool = True
        self.AddSeparator(height=3)
        self.AddLabel("TYPE:")
        self.TypeValue = self.AddLabel("NONE")

        # 1. Текст
        self.Layout.addWidget(self.AddLabel("TEXT:"))
        InputCls = LCARS.Input
        self.TextEdit = InputCls(self.widget)
        self.TextEdit.setStyleSheet(
            "background: #1a1a2e; color: #fff; border: 1px solid #336699; "
            "font-family: 'LCARS'; font-size: 10pt; padding: 4px; border-radius: 4px;"
        )
        self.TextEdit.textChanged.connect(self.OnTextChanged)
        self.Layout.addWidget(self.TextEdit)

        # 2. Координати (X, Y)
        self.Layout.addWidget(self.AddLabel("POSITION (X,Y):"))
        PosRow = LCARS.HMatrix()
        
        self.SpinX = self.CreateSpinBox(0, 3000)
        self.SpinX.valueChanged.connect(lambda _: self.OnPositionChanged())
        
        self.SpinY = self.CreateSpinBox(0, 3000)
        self.SpinY.valueChanged.connect(lambda _: self.OnPositionChanged())
        
        PosRow.addWidget(self.SpinX)
        PosRow.addWidget(self.SpinY)
        self.Layout.addLayout(PosRow)

        # 3. Розміри (W, H)
        self.Layout.addWidget(self.AddLabel("SIZE (W,H):"))
        SizeRow = LCARS.HMatrix()
        
        self.SpinW = self.CreateSpinBox(10, 2000)
        self.SpinW.valueChanged.connect(lambda _: self.OnSizeChanged())
        
        self.SpinH = self.CreateSpinBox(10, 2000)
        self.SpinH.valueChanged.connect(lambda _: self.OnSizeChanged())
        
        SizeRow.addWidget(self.SpinW)
        SizeRow.addWidget(self.SpinH)
        self.Layout.addLayout(SizeRow)

        # 4. Фракції кольорів
        self.Layout.addWidget(self.AddLabel("FACTIONS:"))
        FacRow = LCARS.HMatrix()
        
        self.BtnFed = self.CreateButton("FED")
        self.BtnFed.Clicked.connect(lambda: self.ApplyColor("#3366FF"))
        
        self.BtnKli = self.CreateButton("KLI")
        self.BtnKli.Clicked.connect(lambda: self.ApplyColor("#FF3300"))
        
        self.BtnRom = self.CreateButton("ROM")
        self.BtnRom.Clicked.connect(lambda: self.ApplyColor("#00FF88"))
        
        FacRow.addWidget(self.BtnFed.widget)
        FacRow.addWidget(self.BtnKli.widget)
        FacRow.addWidget(self.BtnRom.widget)
        self.Layout.addLayout(FacRow)

        # 5. Палітра
        self.Layout.addWidget(self.AddLabel("PALETTE:"))
        PalRow = LCARS.HMatrix()
        
        self.BtnOra = self.CreateButton("AMB")
        self.BtnOra.Clicked.connect(lambda: self.ApplyColor("#FF9900"))
        
        self.BtnGld = self.CreateButton("GLD")
        self.BtnGld.Clicked.connect(lambda: self.ApplyColor("#F0B942"))
        
        self.BtnSil = self.CreateButton("SLV")
        self.BtnSil.Clicked.connect(lambda: self.ApplyColor("#BA985D"))
        
        # 6. Element Type (only visible for primitives with ElementType)
        self.TypeValLabel = LCARSLabel("ELEMENT TYPE:", Parent=self)
        self.SpinTypeVal = SpinCls()
        self.SpinTypeVal.setRange(1000, 4000)
        self.SpinTypeVal.setStyleSheet("background: #1a1a2e; color: #fff; border: 1px solid #336699; padding: 2px; border-radius: 4px;")
        self.SpinTypeVal.valueChanged.connect(lambda _: self.OnTypeValChanged())
        self.Layout.addWidget(self.TypeValLabel)
        self.Layout.addWidget(self.SpinTypeVal)
        self.TypeValLabel.hide()
        self.SpinTypeVal.hide()

        self.Layout.addStretch()
        
        self.DeleteBtn = LCARSButton("DELETE", Parent=self)
        self.DeleteBtn.Clicked.connect(self.DeleteTarget)
        self.Layout.addWidget(self.DeleteBtn)
        
        self.hide()

    def Refresh(self):
        if getattr(self, "Target", None):
            self._block_signals = True
            self.SpinX.setValue(self.Target.x())
            self.SpinY.setValue(self.Target.y())
            self.SpinW.setValue(self.Target.width())
            self.SpinH.setValue(self.Target.height())
            if hasattr(self.Target, "ElementType"):
                self.SpinTypeVal.setValue(self.Target.ElementType)
            self._block_signals = False
            self.update()

    def ShowFor(self, Comp: Graphic):
        self.Target = Comp
        TypeName = Comp.__class__.__name__
        self.TypeValue.Text = TypeName
        self.TypeValue.update()
        
        self._block_signals = True
        self.SpinX.setValue(Comp.x())
        self.SpinY.setValue(Comp.y())
        self.SpinW.setValue(Comp.width())
        self.SpinH.setValue(Comp.height())
        
        Text = getattr(Comp, "Text", "")
        self.TextEdit.setText(Text)
        
        if hasattr(Comp, "ElementType"):
            self.TypeValLabel.show()
            self.SpinTypeVal.setValue(Comp.ElementType)
            self.SpinTypeVal.show()
        else:
            self.TypeValLabel.hide()
            self.SpinTypeVal.hide()
            
        self._block_signals = False
        
        self.show()

    def OnTextChanged(self, text):
        if getattr(self, "Target", None) and not self._block_signals:
            self.Target.Text = text
            if hasattr(self.Target, "setText"):
                self.Target.setText(text)
            elif hasattr(self.Target.widget, "setText"):
                self.Target.widget.setText(text)
            self.Target.update()

    def OnPositionChanged(self):
        if getattr(self, "Target", None) and not self._block_signals:
            self.Target.move(self.SpinX.value(), self.SpinY.value())
            self.Target.update()

    def OnSizeChanged(self):
        if getattr(self, "Target", None) and not self._block_signals:
            self.Target.resize(self.SpinW.value(), self.SpinH.value())
            self.Target.update()

    def ApplyColor(self, color_hex):
        if getattr(self, "Target", None):
            self.Target.Color = color_hex
            if hasattr(self.Target, "apply_style"):
                self.Target.apply_style()
            self.Target.update()

    def OnTypeValChanged(self):
        if getattr(self, "Target", None) and not self._block_signals:
            if hasattr(self.Target, "ElementType"):
                self.Target.ElementType = self.SpinTypeVal.value()
                self.Target.update()

    def DeleteTarget(self):
        if getattr(self, "Target", None):
            Canvas = self.parent().Canvas
            Canvas.RemoveComponent(self.Target)
            self.hide()

# ==============================================================================
# LCARSCanvas — Робоча область
# ==============================================================================
class LCARSCanvas(Graphic):
    def __init__(self, Parent=None, PAD=None):
        super().__init__(Parent)
        self.IsDesigner = True
        self.PAD = PAD
        self.Components: List[Graphic] = []
        self.SelectedStack: List[Graphic] = []
        self.MarqueeRect: Optional[Primitives.Rect] = None
        self.DragStart: Optional[Primitives.Point] = None
        self.ResizingComp: Optional[Graphic] = None
        self.setStyleSheet("background-color: #050510;")

    def Spawn(self, Class: Type[Graphic], **Kwargs) -> Graphic:
        Comp = Class(Parent=self, **Kwargs)
        # Не встановлюємо WindowFlags — компоненти працюють як віджети всередині Canvas
        self.Components.append(Comp)
        W, H = self.width(), self.height()
        Comp.move(max(50, W//2-60), max(50, H//2-20))
        Comp.show()
        self.SelectComponent(Comp)
        return Comp

    def SelectComponent(self, Comp: Graphic, Additive: bool = False):
        if not Additive: self.ClearSelection()
        if Comp not in self.SelectedStack:
            self.SelectedStack.append(Comp)
            Comp.Selected = True
            Comp.update()
        if len(self.SelectedStack) == 1 and self.PAD:
            self.PAD.ShowFor(Comp)
        elif self.PAD: self.PAD.hide()

    def ClearSelection(self):
        for C in self.SelectedStack:
            C.Selected = False
            C.update()
        self.SelectedStack.clear()
        if self.PAD: self.PAD.hide()
        self.update()

    def RemoveComponent(self, Comp: Graphic):
        if Comp in self.Components: self.Components.remove(Comp)
        if Comp in self.SelectedStack: self.SelectedStack.remove(Comp)
        Comp.hide()
        Comp.setParent(None)

    def ClearCanvas(self):
        for C in list(self.Components):
            C.hide(); C.setParent(None)
        self.Components.clear()
        self.ClearSelection()

    def paintEvent(self, Event: Any):
        super().paintEvent(Event)
        P = Primitives.Painter(self)
        W, H = self.width(), self.height()
        Major = Primitives.Pen(Primitives.Color("#1A1A2E"), 1)
        Minor = Primitives.Pen(Primitives.Color("#0A0A10"), 1)
        for x in range(0, W, 10):
            P.setPen(Major if x % 50 == 0 else Minor); P.drawLine(x, 0, x, H)
        for y in range(0, H, 10):
            P.setPen(Major if y % 50 == 0 else Minor); P.drawLine(0, y, W, y)
        if self.MarqueeRect:
            P.setPen(Primitives.Pen(Primitives.Color("#4466FF"), 1))
            P.setBrush(Primitives.Brush(Primitives.Color(68, 102, 255, 40)))
            P.drawRect(self.MarqueeRect)
        if len(self.SelectedStack) == 1:
            C = self.SelectedStack[0]
            P.setPen(Primitives.Pen(Primitives.Color("#00FFFF"), 2))
            P.setBrush(Primitives.Brush(Primitives.Color("#00FFFF")))
            P.drawRect(C.x() + C.width() - 8, C.y() + C.height() - 8, 8, 8)

    def mousePressEvent(self, Event: Any):
        RawMods = getattr(Event, "modifiers", lambda: 0)()
        if True:
            Modifiers = int(RawMods) if RawMods else 0
        if False: # Removed except block
            Modifiers = 0
        ShiftMod = int(getattr(Directive.Protocol, "ShiftModifier", 0x02000000))
        Shift = bool(Modifiers & ShiftMod)
        if len(self.SelectedStack) == 1:
            C = self.SelectedStack[0]
            Handle = Primitives.Rect(C.x() + C.width() - 15, C.y() + C.height() - 15, 15, 15)
            if Handle.contains(Event.pos()):
                self.ResizingComp = C; self.DragStart = Event.pos(); return
        if not self.ChildAt(Event.pos()):
            if not Shift: self.ClearSelection()
            self.DragStart = Event.pos()
            self.MarqueeRect = Primitives.Rect(self.DragStart, self.DragStart)
        super().mousePressEvent(Event)

    def mouseMoveEvent(self, Event: Any):
        if self.ResizingComp and self.DragStart:
            Delta = Event.pos() - self.DragStart
            NewW = max(30, self.ResizingComp.width() + Delta.x())
            NewH = max(20, self.ResizingComp.height() + Delta.y())
            self.ResizingComp.resize(round(NewW/10)*10, round(NewH/10)*10)
            self.DragStart = Event.pos()
            if self.PAD: self.PAD.Refresh()
            self.update(); return
        if self.MarqueeRect and self.DragStart:
            self.MarqueeRect = Primitives.Rect(self.DragStart, Event.pos()).normalized()
            self.update()
        super().mouseMoveEvent(Event)

    def mouseReleaseEvent(self, Event: Any):
        self.ResizingComp = None
        if self.MarqueeRect:
            for C in self.Components:
                if self.MarqueeRect.contains(C.geometry()): self.SelectComponent(C, True)
            self.MarqueeRect = None; self.DragStart = None; self.update()
        super().mouseReleaseEvent(Event)

    def ChildAt(self, Pos: Any) -> Optional[Graphic]:
        for C in reversed(self.Components):
            if C.geometry().contains(Pos): return C
        return None

    def HandleMultiDrag(self, Initiator: Graphic, Event: Any):
        if not Initiator.DragPos:
            return
        Cur = Initiator.mapToParent(Event.pos())
        Last = getattr(Initiator, "_DesignerLastParent", None)
        if Last is None:
            Initiator._DesignerLastParent = Cur
            return
        DX = int(Cur.x() - Last.x())
        DY = int(Cur.y() - Last.y())
        Initiator._DesignerLastParent = Cur
        if DX == 0 and DY == 0:
            return
        for C in self.SelectedStack:
            C.move(round((C.x() + DX) / 10) * 10, round((C.y() + DY) / 10) * 10)
            C.update()
        if self.PAD:
            self.PAD.Refresh()

    def Align(self, Mode: str):
        if len(self.SelectedStack) < 2: return
        if Mode == "Left":
            X = min(C.x() for C in self.SelectedStack)
            for C in self.SelectedStack: C.move(X, C.y())
        elif Mode == "Top":
            Y = min(C.y() for C in self.SelectedStack)
            for C in self.SelectedStack: C.move(C.x(), Y)
        self.update()

    def ExportLayout(self):
        Lines = [
            "def BuildUI(Parent):",
            "    from lcars.base.component import (",
            "        LCARSButton, LCARSLabel, LCARSElbow, LCARSBar, LCARSDataBlock,",
            "        LCARSStatBar, LCARSDivider, IndicatorButton, SplitButton,",
            "    )",
        ]
        for C in self.Components:
            Name = C.__class__.__name__
            if isinstance(C, LCARSButton):
                Lines.append(
                    f"    obj = {Name}(Text={getattr(C, 'Text', '')!r}, Parent=Parent, Type={getattr(C, 'Type', 'rounded')!r})"
                )
            elif isinstance(C, LCARSLabel):
                Lines.append(f"    obj = {Name}(Text={getattr(C, 'Text', '')!r}, Parent=Parent)")
            elif C.__class__.__name__ == "LCARSDataBlock":
                Lines.append(
                    f"    obj = {Name}(Label={getattr(C, 'Label', '')!r}, Value={getattr(C, 'Value', '')!r}, Parent=Parent)"
                )
            elif C.__class__.__name__ == "LCARSStatBar":
                Lines.append(
                    f"    obj = {Name}(Value={getattr(C, 'Value', 0)!r}, MaxValue={getattr(C, 'MaxValue', 100)!r}, Parent=Parent)"
                )
            else:
                Lines.append(f"    obj = {Name}(Parent=Parent)")
            Lines.append(f"    obj.setGeometry({C.x()}, {C.y()}, {C.width()}, {C.height()})")
        print("\n" + "=" * 40 + "\n" + "\n".join(Lines) + "\n" + "=" * 40)

# ==============================================================================
# SIDEBAR
# ==============================================================================
class SidebarPanel(Graphic):
    WIDTH = 240

    def __init__(self, Canvas: LCARSCanvas, Parent=None):
        from lcars.base.component import (
            LCARSLabel, LCARSBar, LCARSButton, IndicatorButton, SplitButton,
            LCARSDataBlock, LCARSStatBar, LCARSDivider, LCARSElbow
        )
        super().__init__(Parent)
        self.IsTool = True
        self.Canvas = Canvas
        self.setFixedWidth(self.WIDTH)
        self.setStyleSheet("background-color: #000000;")
        VBox = registry.Get("Layout.VBox")(self)
        VBox.setContentsMargins(10, 10, 10, 10); VBox.setSpacing(6)
        VBox.addWidget(LCARSLabel("◤ ARCHITECT TOOLS"))
        VBox.addWidget(LCARSBar(Height=3))

        # Кнопки палітри — стандарт LCARS (rounded); прямокутний тип лише як рідкісний «support»
        self.AddCategory(VBox, "◤ BUTTON TYPES", [
            ("ROUNDED", LCARSButton, {"Text": "ACTION"}),
            ("HALF CAP", LCARSButton, {"Text": "NAV", "Type": LCARSButton.HALF_LEFT}),
            ("CROPPED", LCARSButton, {"Text": "PANEL", "Type": LCARSButton.CROPPED}),
            ("INDICATOR", IndicatorButton, {"Text": "STATUS"}),
            ("SPLIT", SplitButton, {"Text": "MAIN", "Prefix": "01"}),
            ("RECT (support)", LCARSButton, {"Text": "BRACKET", "Type": LCARSButton.RECT}),
        ])
        self.AddCategory(VBox, "◤ DISPLAY", [
            ("LABEL", LCARSLabel, {"Text": "TITLE"}),
            ("DATA BLOCK", LCARSDataBlock, {"Label": "FIELD", "Value": "—"}),
            ("STAT BAR", LCARSStatBar, {"Value": 40, "MaxValue": 100}),
            ("DIVIDER", LCARSDivider, {"Text": "SECTION"}),
        ])
        self.AddCategory(VBox, "◤ GEOMETRY", [
            ("ELBOW", LCARSElbow, {}),
            ("BAR", LCARSBar, {"Height": 8}),
        ])
        from lcars.base.interface import LCARSPadd, LCARSScreen
        self.AddCategory(VBox, "◤ SHELL (рідко на полотні)", [
            ("PADD", LCARSPadd, {}),
            ("SCREEN", LCARSScreen, {}),
        ])
        self.AddCategory(VBox, "◤ CANVAS PRIMITIVES", [
            ("ACCESS PANEL", AccessPanel, {}),
            ("SWEPT STRUCTURE", Structure, {}),
            ("RAW SURFACE", Surface, {}),
            ("RAW SYMBOL", Symbol, {}),
        ])

        VBox.addStretch()
        VBox.addWidget(LCARSLabel("◤ ALIGNMENT"))
        H = registry.Get("Layout.HBox")()
        L = LCARSButton("LEFT", Parent=self)
        L.IsTool = True
        L.Clicked = lambda: self.Canvas.Align("Left")
        T = LCARSButton("TOP", Parent=self)
        T.IsTool = True
        T.Clicked = lambda: self.Canvas.Align("Top")
        H.addWidget(L)
        H.addWidget(T)
        VBox.addLayout(H)
        Exp = LCARSButton("EXPORT CODE", Parent=self)
        Exp.IsTool = True
        Exp.Clicked = self.Canvas.ExportLayout
        Clr = LCARSButton("CLEAR ALL", Parent=self)
        Clr.IsTool = True
        Clr.Clicked = self.Canvas.ClearCanvas
        VBox.addWidget(Exp)
        VBox.addWidget(Clr)

    PaletteEntry = Union[Tuple[str, Type[Graphic]], Tuple[str, Type[Graphic], dict[str, Any]]]

    def AddCategory(self, Layout: Any, Title: str, Items: List[PaletteEntry]) -> None:
        from lcars.base.component import LCARSButton, LCARSLabel
        Layout.addSpacing(5)
        Layout.addWidget(LCARSLabel(Title))
        for Entry in Items:
            if len(Entry) == 3:
                Name, Class, Kw = Entry[0], Entry[1], dict(Entry[2])
            else:
                Name, Class = Entry[0], Entry[1]
                Kw = {}
            B = LCARSButton(Name, Parent=self)
            B.IsTool = True
            B.Clicked = lambda _=None, C=Class, K=Kw: self.Canvas.Spawn(C, **K)
            Layout.addWidget(B)

    def _noop(self) -> None:
        pass

class LCARSDesigner(Graphic):
    def __init__(self, Parent=None):
        super().__init__(Parent)
        HBox = registry.Get("Layout.HBox")(self)
        HBox.setContentsMargins(0,0,0,0); HBox.setSpacing(0)
        self.PAD = InfoPad(self); self.Canvas = LCARSCanvas(self, self.PAD); self.Sidebar = SidebarPanel(self.Canvas, self)
        HBox.addWidget(self.Sidebar); HBox.addWidget(self.Canvas, 1); HBox.addWidget(self.PAD)


def BootConstructor() -> Matrix:
    # 1. Створюємо базову системну матрицю вікна
    Window = Matrix()
    
    # 2. Відключаємо рамки Windows, вказуємо стандартний фон (Titanium)
    Proto = Directive.Protocol
    WinType = getattr(Proto, "WindowType", Proto)
    Frameless = getattr(WinType, "FramelessWindowHint", 0x00000800)
    Window.setWindowFlags(Frameless)
    Window.setWindowTitle("LCARS TITANIUM — Engineering Constructor")
    Window.setStyleSheet("background-color: #000000; margin: 0; padding: 0;")
    
    # 3. Підключаємо HBox Layout, щоб дизайнер ідеально вписався у розміри
    HBoxClass = registry.Get("Layout.HBox")
    Layout = HBoxClass(Window)
    Layout.setContentsMargins(0, 0, 0, 0)
    Layout.setSpacing(0)

    # 4. Вмонтовуємо конструктор у вікно
    Designer = LCARSDesigner(Parent=Window)
    Layout.addWidget(Designer)

    # 5. Heartbeat — оновлює компоненти на Canvas, створюючи "живий" ефект
    TimerClass = registry.Get("Core.Timer")
    if TimerClass:
        Heartbeat = TimerClass()
        Heartbeat.timeout.connect(
            lambda: [C.update() for C in Designer.Canvas.Components] if hasattr(Designer, 'Canvas') else None
        )
        Heartbeat.start(400) # Оновлюється 2.5 рази на секунду
    return Window
    
__all__ = ["Graphic", "LCARSDesigner", "LCARSCanvas", "SidebarPanel", "InfoPad", 
"BootConstructor", "Surface", "Symbol", "Structure", "AccessPanel", "Rect", "Square", 
"Circle", "Triangle", "Trapezoid", "Diamond", "Star", "Line"]

if __name__ == "__main__":
    AppClass = registry.Get("UI.Application")
    if not AppClass:
        print("ENGINE ERROR: UI.Application not found.")
        sys.exit(1)
    App = AppClass(sys.argv)

    # Запускаємо та розгортаємо Конструктор
    MainWindow = BootConstructor()
    MainWindow.showMaximized()

    sys.exit(App.exec())
