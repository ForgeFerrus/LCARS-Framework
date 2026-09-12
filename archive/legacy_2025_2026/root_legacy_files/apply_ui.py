import os

components_code = """from __future__ import annotations
import math
from typing import TYPE_CHECKING, Any
from lcars.base.register import registry as Registry
from lcars.base.types import Primitives, Directive, Matrix
from lcars.base.defaults import DefaultPalette, RandomButtonColor, FontStyle, ContrastColor

class SystemComponent(Matrix):
    clicked = getattr(Directive, "Signal", type("MockSignal", (), {"emit": lambda *a: None, "connect": lambda *a: None}))()
    
    def __init__(self, Parent=None):
        super().__init__(Parent)
        self.ActiveColor = RandomButtonColor()
        self.Hover = False
        self.Children = []
        self.Active = True

    def AddChild(self, Child):
        if Child not in self.Children:
            self.Children.append(Child)
            getattr(Child, "setParent", lambda p: setattr(Child, "Parent", p))(self)
            
    def RemoveChild(self, Child):
        if Child in self.Children:
            self.Children.remove(Child)
            getattr(Child, "setParent", lambda p: setattr(Child, "Parent", p))(None)
            
    def Activate(self):
        self.Active = True
        getattr(self, "update", lambda: None)()
        
    def Deactivate(self):
        self.Active = False
        getattr(self, "update", lambda: None)()

    def enterEvent(self, Event):
        self.Hover = True
        getattr(self, "update", lambda: None)()
        
    def leaveEvent(self, Event):
        self.Hover = False
        getattr(self, "update", lambda: None)()
        
    def mousePressEvent(self, Event):
        if hasattr(self, "clicked") and hasattr(self.clicked, "emit"):
            self.clicked.emit()
            getattr(self, "update", lambda: None)()

class LCARSLabel(SystemComponent):
    def __init__(self, Text="", Parent=None, FontSize=14, Color="white", Weight="normal", AlignType=None, **Kwargs):
        super().__init__(Parent)
        Align = getattr(Directive, "Align", None)
        AlignType = AlignType or (Align.Left if hasattr(Align, "Left") else 0x0001)
        getattr(self, "setStyleSheet", lambda s: None)(f"color: {Color}; {FontStyle(FontSize, Weight)} background: transparent;")
        getattr(self, "setAlignment", lambda a: None)(AlignType)
        getattr(self, "setText", lambda t: None)(Text)

class LCARSButtonBase(SystemComponent):
    def __init__(self, Text="", Color=None, Parent=None, **Kwargs):
        super().__init__(Parent)
        self.Text = Text
        self.ActiveColor = Color if Color and Color != "none" else RandomButtonColor()
        self.Radius = Kwargs.get("radius", 20)
        getattr(self, "setFixedHeight", lambda h: None)(Kwargs.get("height", 45))
        
        Protocol = getattr(Directive, "Protocol", None)
        if Protocol and hasattr(Protocol, "CursorShape"):  
            getattr(self, "setCursor", lambda c: None)(Protocol.CursorShape.PointingHandCursor)

    def _setup_painter(self):
        PainterClass = getattr(Primitives, "Painter", object)
        if not PainterClass or PainterClass == object: return None, None, None, None
        P = PainterClass(self)
        P.setRenderHint(getattr(Primitives, "Antialiasing", object))
        
        TargetColor = self.ActiveColor
        if getattr(self, "Hover", False):
            TargetColor = ContrastColor(self.ActiveColor)
            if TargetColor == self.ActiveColor: TargetColor = "#ffffff"
            
        P.setBrush(getattr(Primitives, "Brush", object)(getattr(Primitives, "Color", object)(TargetColor)))
        P.setPen(getattr(Primitives, "Pen", object)(getattr(Primitives, "Color", object)(0,0,0,0)))
        
        W, H = getattr(self, "width", lambda: 0)(), getattr(self, "height", lambda: 0)()
        return P, W, H, getattr(Primitives, "Path", object)()

    def _draw_text(self, P, W, H, OffsetX=0, AlignOverride=None):
        P.setPen(getattr(Primitives, "Pen", object)(getattr(Primitives, "Color", object)(ContrastColor(self.ActiveColor))))
        P.setFont(getattr(Primitives, "Font", object)("LCARS", 14, 75))
        Align = getattr(Directive, "Align", None)
        AlignVal = AlignOverride if AlignOverride is not None else getattr(Align, "Center", 0x0004 | 0x0080)
        RectF = getattr(Primitives, "RectF", object)
        if RectF and RectF != object:
            P.drawText(RectF(OffsetX, 0, W - OffsetX, H), AlignVal, self.Text.upper())

class LCARSRectButton(LCARSButtonBase):
    def paintEvent(self, Event):
        P, W, H, Path = self._setup_painter()
        if not P: return
        RectF = getattr(Primitives, "RectF", object)
        Path.addRect(RectF(0, 0, W, H))
        P.drawPath(Path)
        self._draw_text(P, W, H)

class LCARSRoundedButton(LCARSButtonBase):
    def paintEvent(self, Event):
        P, W, H, Path = self._setup_painter()
        if not P: return
        RectF = getattr(Primitives, "RectF", object)
        R = H / 2
        Path.addRoundedRect(RectF(0, 0, W, H), R, R)
        P.drawPath(Path)
        self._draw_text(P, W, H)

class LCARSHalfRoundedButton(LCARSButtonBase):
    def __init__(self, Text="", Side="left", Color=None, Parent=None, **Kwargs):
        super().__init__(Text, Color, Parent, **Kwargs)
        self.Side = Side

    def paintEvent(self, Event):
        P, W, H, Path = self._setup_painter()
        if not P: return
        RectF = getattr(Primitives, "RectF", object)
        R = H / 2
        Path.addRoundedRect(RectF(0, 0, W, H), R, R)
        if self.Side == "left":
            Path.addRect(RectF(R, 0, W - R, H))
        else:
            Path.addRect(RectF(0, 0, W - R, H))
        P.drawPath(Path)
        
        Align = getattr(Directive, "Align", None)
        self._draw_text(P, W, H, AlignOverride=getattr(Align, "Right", 0x0002) if self.Side == "left" else getattr(Align, "Left", 0x0001))

class LCARSCroppedButton(LCARSButtonBase):
    def __init__(self, Text="", Side="left", Color=None, Parent=None, **Kwargs):
        super().__init__(Text, Color, Parent, **Kwargs)
        self.Side = Side
        
    def paintEvent(self, Event):
        P, W, H, Path = self._setup_painter()
        if not P: return
        RectF = getattr(Primitives, "RectF", object)
        R = H / 2
        Crop = 10
        Path.addRoundedRect(RectF(0, 0, W, H), R, R)
        if self.Side == "left":
            Path.addRect(RectF(R, 0, W - R, H))
            Path.addRect(RectF(0, 0, Crop, H))
        else:
            Path.addRect(RectF(0, 0, W - R, H))
            Path.addRect(RectF(W - Crop, 0, Crop, H))
        P.drawPath(Path)
        self._draw_text(P, W, H)

class LCARSIndicatorButton(LCARSButtonBase):
    def __init__(self, Text="", Side="left", IndicatorColor="#FF9900", Color=None, Parent=None, **Kwargs):
        super().__init__(Text, Color, Parent, **Kwargs)
        self.Side = Side
        self.IndicatorColor = IndicatorColor

    def paintEvent(self, Event):
        P, W, H, Path = self._setup_painter()
        if not P: return
        RectF = getattr(Primitives, "RectF", object)
        ColorClass = getattr(Primitives, "Color", object)
        BrushClass = getattr(Primitives, "Brush", object)
        
        IndW = 15
        Gap = 5
        R = H / 2
        BodyPath = getattr(Primitives, "Path", object)()
        
        if self.Side == "left":
            BodyPath.addRect(RectF(IndW + Gap, 0, W - IndW - Gap - R, H))
            BodyPath.addRoundedRect(RectF(IndW + Gap, 0, W - IndW - Gap, H), R, R)
        else:
            BodyPath.addRoundedRect(RectF(0, 0, W - IndW - Gap, H), R, R)
            BodyPath.addRect(RectF(R, 0, W - IndW - Gap - R, H))
        P.drawPath(BodyPath)
        
        P.setBrush(BrushClass(ColorClass(self.IndicatorColor)))
        if self.Side == "left":
            P.drawRect(RectF(0, 0, IndW, H))
            self._draw_text(P, W, H, OffsetX=IndW+Gap)
        else:
            P.drawRect(RectF(W - IndW, 0, IndW, H))
            self._draw_text(P, W - IndW - Gap, H)

class LCARSSplitButton(LCARSButtonBase):
    def __init__(self, Text="", Prefix="47", Color=None, Parent=None, **Kwargs):
        super().__init__(Text, Color, Parent, **Kwargs)
        self.Prefix = Prefix
        
    def paintEvent(self, Event):
        P, W, H, Path = self._setup_painter()
        if not P: return
        RectF = getattr(Primitives, "RectF", object)
        R = H / 2
        SplitW = 40
        Gap = 5
        
        Path1 = getattr(Primitives, "Path", object)()
        Path1.addRoundedRect(RectF(0, 0, SplitW, H), R, R)
        Path1.addRect(RectF(R, 0, SplitW - R, H))
        P.drawPath(Path1)
        
        Path2 = getattr(Primitives, "Path", object)()
        Path2.addRoundedRect(RectF(SplitW + Gap, 0, W - SplitW - Gap, H), R, R)
        Path2.addRect(RectF(SplitW + Gap, 0, W - SplitW - Gap - R, H))
        P.drawPath(Path2)
        
        P.setPen(getattr(Primitives, "Pen", object)(getattr(Primitives, "Color", object)(ContrastColor(self.ActiveColor))))
        P.setFont(getattr(Primitives, "Font", object)("LCARS", 12, 75))
        Align = getattr(Directive, "Align", None)
        AlignCenter = getattr(Align, "Center", 0x0004 | 0x0080)
        P.drawText(RectF(0, 0, SplitW, H), AlignCenter, self.Prefix)
        P.drawText(RectF(SplitW + Gap, 0, W - SplitW - Gap, H), AlignCenter, self.Text.upper())

class LCARSElbow(SystemComponent):
    def __init__(self, Direction="top-left", Color=None, Thickness=40, Radius=80, Parent=None, **Kwargs):
        super().__init__(Parent)
        self.Direction, self.Thickness, self.Radius = Direction, Thickness, Radius
        self.ActiveColor = Color or RandomButtonColor()
        getattr(self, "setMinimumSize", lambda w, h: None)(Radius, Radius)

    def paintEvent(self, Event):
        PainterClass = getattr(Primitives, "Painter", object)
        if not PainterClass or PainterClass == object: return
        P = PainterClass(self)
        W, H, R, T = self.width(), self.height(), self.Radius, self.Thickness
        P.setRenderHint(getattr(Primitives, "Antialiasing", object))
        P.setBrush(getattr(Primitives, "Brush", object)(getattr(Primitives, "Color", object)(self.ActiveColor)))
        P.setPen(getattr(Primitives, "Pen", object)(getattr(Primitives, "Color", object)(0,0,0,0)))
        Path = getattr(Primitives, "Path", object)()
        RectF = getattr(Primitives, "RectF", object)
        if "top-left" in self.Direction:
            Path.moveTo(0, H)
            Path.lineTo(0, R)
            Path.arcTo(RectF(0, 0, R*2, R*2), 180, -90)
            Path.lineTo(W, 0)
            Path.lineTo(W, T)
            Path.lineTo(R, T)
            Path.arcTo(RectF(T, T, (R-T)*2, (R-T)*2), 90, 90)
            Path.lineTo(T, H)
        elif "bottom-left" in self.Direction:
            Path.moveTo(W, H)
            Path.lineTo(R, H)
            Path.arcTo(RectF(0, H-R*2, R*2, R*2), -90, -90)
            Path.lineTo(0, 0)
            Path.lineTo(T, 0)
            Path.lineTo(T, H-R)
            Path.arcTo(RectF(T, H-R*2+T, (R-T)*2, (R-T)*2), 180, 90)
            Path.lineTo(W, H-T)
        P.drawPath(Path)

class LCARSBar(SystemComponent):
    def __init__(self, Color=None, Parent=None, **Kwargs):
        super().__init__(Parent)
        self.ActiveColor = Color or RandomButtonColor()
        self.Thickness = Kwargs.get("thickness", 15)
        getattr(self, "setFixedHeight", lambda h: None)(self.Thickness)

    def paintEvent(self, Event):
        PainterClass = getattr(Primitives, "Painter", object)
        if not PainterClass or PainterClass == object: return
        P = PainterClass(self)
        P.setRenderHint(getattr(Primitives, "Antialiasing", object))
        P.setBrush(getattr(Primitives, "Brush", object)(getattr(Primitives, "Color", object)(self.ActiveColor)))
        P.setPen(getattr(Primitives, "Pen", object)(getattr(Primitives, "Color", object)(0,0,0,0)))
        RectF = getattr(Primitives, "RectF", object)
        if hasattr(P, "drawRect") and RectF != object:
            P.drawRect(RectF(0, 0, self.width(), self.height()))

class LCARSDoubleBar(SystemComponent):
    def __init__(self, Color1=None, Color2=None, Parent=None, **Kwargs):
        super().__init__(Parent)
        self.Color1 = Color1 or RandomButtonColor()
        self.Color2 = Color2 or RandomButtonColor()
        getattr(self, "setFixedHeight", lambda h: None)(Kwargs.get("height", 35))

    def paintEvent(self, Event):
        PainterClass = getattr(Primitives, "Painter", object)
        if not PainterClass or PainterClass == object: return
        P = PainterClass(self)
        P.setRenderHint(getattr(Primitives, "Antialiasing", object))
        BrushC = getattr(Primitives, "Brush", object)
        ColorC = getattr(Primitives, "Color", object)
        RectF = getattr(Primitives, "RectF", object)
        P.setPen(getattr(Primitives, "Pen", object)(ColorC(0,0,0,0)))
        
        W, H = self.width(), self.height()
        LineH = (H - 5) / 2
        
        if hasattr(P, "drawRect") and RectF != object:
            P.setBrush(BrushC(ColorC(self.Color1)))
            P.drawRect(RectF(0, 0, W, LineH))
            
            P.setBrush(BrushC(ColorC(self.Color2)))
            P.drawRect(RectF(0, LineH + 5, W, LineH))

class LCARSIndicatorBar(SystemComponent):
    def __init__(self, Side="right", Color=None, IndicatorColor=None, Parent=None, **Kwargs):
        super().__init__(Parent)
        self.Side = Side
        self.ActiveColor = Color or RandomButtonColor()
        self.IndicatorColor = IndicatorColor or RandomButtonColor()
        getattr(self, "setFixedHeight", lambda h: None)(Kwargs.get("height", 20))

    def paintEvent(self, Event):
        PainterClass = getattr(Primitives, "Painter", object)
        if not PainterClass or PainterClass == object: return
        P = PainterClass(self)
        P.setRenderHint(getattr(Primitives, "Antialiasing", object))
        BrushC = getattr(Primitives, "Brush", object)
        ColorC = getattr(Primitives, "Color", object)
        RectF = getattr(Primitives, "RectF", object)
        P.setPen(getattr(Primitives, "Pen", object)(ColorC(0,0,0,0)))
        
        W, H = self.width(), self.height()
        IndW = 30
        Gap = 5
        
        if hasattr(P, "drawRect") and RectF != object:
            if self.Side == "right":
                P.setBrush(BrushC(ColorC(self.ActiveColor)))
                P.drawRect(RectF(0, H/4, W - IndW - Gap, H/2))
                P.setBrush(BrushC(ColorC(self.IndicatorColor)))
                P.drawRect(RectF(W - IndW, 0, IndW, H))
            else:
                P.setBrush(BrushC(ColorC(self.IndicatorColor)))
                P.drawRect(RectF(0, 0, IndW, H))
                P.setBrush(BrushC(ColorC(self.ActiveColor)))
                P.drawRect(RectF(IndW + Gap, H/4, W - IndW - Gap, H/2))

__all__ = [
    "SystemComponent", "LCARSLabel", "LCARSButtonBase", "LCARSRectButton", "LCARSRoundedButton",
    "LCARSHalfRoundedButton", "LCARSCroppedButton", "LCARSIndicatorButton", "LCARSSplitButton",
    "LCARSElbow", "LCARSBar", "LCARSDoubleBar", "LCARSIndicatorBar"
]
"""

animations_code = """from __future__ import annotations
import math
from lcars.base.types import Primitives
from lcars.base.components import SystemComponent
from lcars.base.defaults import RandomButtonColor

class LCARSScanningBar(SystemComponent):
    def __init__(self, Color=None, Parent=None, **Kwargs):
        super().__init__(Parent)
        self.ActiveColor = Color or RandomButtonColor()
        getattr(self, "setFixedHeight", lambda h: None)(15)
        self.ScanPhase = 0.0
        TimerClass = getattr(Primitives, "Timer", object)
        if TimerClass and TimerClass != object:
            self.Timer = TimerClass(self)
            if hasattr(self.Timer, "timeout"):
                self.Timer.timeout.connect(self.update)
                self.Timer.start(50)

    def paintEvent(self, Event):
        PainterClass = getattr(Primitives, "Painter", object)
        if not PainterClass or PainterClass == object: return
        P = PainterClass(self)
        P.setRenderHint(getattr(Primitives, "Antialiasing", object))
        W, H = self.width(), self.height()
        ColorClass = getattr(Primitives, "Color", object)
        for i in range(0, W, 20):
            Op = int(100 + 155 * abs(math.sin(self.ScanPhase + i/W)))
            C = ColorClass(self.ActiveColor)
            C.setAlpha(Op)
            P.setBrush(getattr(Primitives, "Brush", object)(C))
            P.setPen(getattr(Primitives, "Pen", object)(ColorClass(0,0,0,0)))
            if hasattr(P, "drawRect"):
                P.drawRect(i, 0, 15, H)
        self.ScanPhase += 0.05

class LCARSLoader(SystemComponent):
    def __init__(self, Color=None, Parent=None, **Kwargs):
        super().__init__(Parent)
        self.ActiveColor = Color or RandomButtonColor()
        getattr(self, "setFixedSize", lambda w, h: None)(40, 40)
        self.Angle = 0
        TimerClass = getattr(Primitives, "Timer", object)
        if TimerClass and TimerClass != object:
            self.Timer = TimerClass(self)
            if hasattr(self.Timer, "timeout"):
                self.Timer.timeout.connect(self.update)
                self.Timer.start(30)

    def paintEvent(self, Event):
        PainterClass = getattr(Primitives, "Painter", object)
        if not PainterClass or PainterClass == object: return
        P = PainterClass(self)
        P.setRenderHint(getattr(Primitives, "Antialiasing", object))
        W, H = self.width(), self.height()
        P.translate(W/2, H/2)
        P.rotate(self.Angle)
        
        ColorClass = getattr(Primitives, "Color", object)
        PenClass = getattr(Primitives, "Pen", object)
        C = ColorClass(self.ActiveColor)
        Pen = PenClass(C)
        Pen.setWidth(4)
        P.setPen(Pen)
        P.setBrush(getattr(Primitives, "Brush", object)(ColorClass(0,0,0,0)))
        
        RectF = getattr(Primitives, "RectF", object)
        if hasattr(P, "drawArc") and RectF != object:
            P.drawArc(RectF(-W/2+4, -H/2+4, W-8, H-8), 0, 270 * 16)
        
        self.Angle = (self.Angle + 10) % 360

__all__ = ["LCARSScanningBar", "LCARSLoader"]
"""

interface_code = """from __future__ import annotations
from lcars.base.types import Directive, ODN, Primitives, Matrix
from lcars.base.components import *
from lcars.base.animations import *

# ALIASES FOR HIGH LEVEL INTERFACE
Frame = SystemComponent
Label = LCARSLabel
Button = LCARSRoundedButton
RectButton = LCARSRectButton
HalfButton = LCARSHalfRoundedButton
CroppedButton = LCARSCroppedButton
IndicatorButton = LCARSIndicatorButton
SplitButton = LCARSSplitButton
Elbow = LCARSElbow
Bar = LCARSBar
DoubleBar = LCARSDoubleBar
IndicatorBar = LCARSIndicatorBar
ScanningBar = LCARSScanningBar
Loader = LCARSLoader

class LCARSPadd(SystemComponent):
    def __init__(self, Title="TITANIUM PADD", Color=None, Parent=None, **Kwargs):
        super().__init__(Parent)
        getattr(self, "setWindowFlags", lambda flag: None)(0x00000800)
        self.AccentColor = Color or "#336699"
        self.Title = Title
        
        WidgetC = getattr(Directive, "Widget", Matrix)
        if WidgetC:
            self.Viewport = WidgetC(self)
            VBoxC = getattr(Primitives, "VBoxLayout", None)
            if VBoxC and VBoxC != object:
                self.Layout = VBoxC(self.Viewport)
                getattr(self.Layout, "setContentsMargins", lambda *a: None)(0, 0, 0, 0)
        getattr(self, "setMinimumSize", lambda *a: None)(300, 200)

    def paintEvent(self, Event):
        if getattr(self, "parent", lambda: None)(): return
        PainterClass = getattr(Primitives, "Painter", None)
        if not PainterClass or PainterClass == object: return
        P = PainterClass(self)
        P.setRenderHint(getattr(Primitives, "Antialiasing", None))
        W, H, Th, Rl = getattr(self, "width", lambda: 0)(), getattr(self, "height", lambda: 0)(), 30, 45
        P.setBrush(getattr(Primitives, "Brush", None)(getattr(Primitives, "Color", None)(self.AccentColor)))
        P.setPen(getattr(Primitives, "Pen", None)(getattr(Primitives, "Color", None)(0,0,0,0)))
        
        Path = getattr(Primitives, "Path", None)()
        RectF = getattr(Primitives, "RectF", None)
        if Path and RectF:
            Path.moveTo(W, 0)
            Path.lineTo(Rl, 0)
            Path.arcTo(RectF(0, 0, Rl*2, Rl*2), 90, 90)
            Path.lineTo(0, H - Rl)
            Path.arcTo(RectF(0, H - Rl*2, Rl*2, Rl*2), 180, 90)
            Path.lineTo(W, H)
            Path.lineTo(W, H - Th)
            Path.lineTo(Rl, H - Th)
            Path.arcTo(RectF(Th, H - Rl*2 + Th, (Rl-Th)*2, (Rl-Th)*2), 270, -90)
            Path.lineTo(Th, Rl)
            Path.arcTo(RectF(Th, Th, (Rl-Th)*2, (Rl-Th)*2), 180, -90)
            Path.lineTo(W, Th)
            Path.lineTo(W, 0)
            P.drawPath(Path)
        
        if self.Title and RectF:
            P.setPen(getattr(Primitives, "Pen", None)(getattr(Primitives, "Color", None)("black")))
            P.setFont(getattr(Primitives, "Font", None)("LCARS", 13, 75))
            Align = getattr(Directive, "Align", None)
            P.drawText(RectF(Rl + 10, 0, W - Rl - 20, Th), getattr(Align, "VCenter", 0x0080), self.Title.upper())

    def resizeEvent(self, Event):
        if hasattr(self, "Viewport"):
            Th = 30
            self.Viewport.setGeometry(Th + 10, Th + 10, getattr(self, "width", lambda: 0)() - Th - 20, getattr(self, "height", lambda: 0)() - (Th * 2) - 20)
        if hasattr(super(), "resizeEvent"): super().resizeEvent(Event)

LCARSPanel = LCARSPadd
ScreenFrame = LCARSPadd
Panel = LCARSPanel

class LCARSScreen(LCARSPadd):
    def __init__(self, Title="LCARS MAINFRAME", Color=None, Parent=None, **Kwargs):
        super().__init__(Title, Color, Parent, **Kwargs)
        WindowState = getattr(Directive, "WindowState", None)
        if WindowState and hasattr(WindowState, "WindowFullScreen"):
            getattr(self, "setWindowState", lambda flag: None)(WindowState.WindowFullScreen)

class LCARSInterface(SystemComponent):
    def __init__(self, Title="LCARS INTERFACE", Parent=None):
        super().__init__(Parent)
        self.Title = Title
        self.Padd = LCARSPadd(Title=self.Title, Parent=self)
        
    def Build(self):
        raise NotImplementedError("Build() must be implemented in the child interface class.")

__all__ = [
    "SystemComponent", "LCARSRectButton", "LCARSRoundedButton", "LCARSHalfRoundedButton",
    "LCARSCroppedButton", "LCARSIndicatorButton", "LCARSSplitButton", "LCARSElbow",
    "LCARSBar", "LCARSDoubleBar", "LCARSIndicatorBar", "LCARSLabel", 
    "LCARSScanningBar", "LCARSLoader", "LCARSPadd", "LCARSPanel", "ScreenFrame", "Panel", 
    "Frame", "Label", "Button", "RectButton", "HalfButton", "CroppedButton", 
    "IndicatorButton", "SplitButton", "Elbow", "Bar", "DoubleBar", "IndicatorBar", 
    "ScanningBar", "Loader", "LCARSScreen", "LCARSInterface"
]
"""

with open("lcars/base/components.py", "w", encoding="utf-8") as f:
    f.write(components_code)
    
with open("lcars/base/animations.py", "w", encoding="utf-8") as f:
    f.write(animations_code)
    
with open("lcars/base/interface.py", "w", encoding="utf-8") as f:
    f.write(interface_code)
