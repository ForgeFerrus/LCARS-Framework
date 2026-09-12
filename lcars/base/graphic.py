# LCARS FRAMEWORK UNIFIED GRAPHIC & TOPOLOGY ENGINE
# ОПИС: Канонічна векторна графіка та топологічний рендеринг LCARS (Michael Okuda Standard).
# ПРИНЦИП: Усі елементи інтерфейсу складаються з топологічних примітивів (Elbow, Bar, Cap, Column, Rect),
#         які рендерить системний клас Renderer без зайвого CSS та піксельних розривів.
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations
from lcars.base.type import LCARS, SystemComponent
from lcars.base.info import Version
from lcars.base.default import Palette, DefaultBackground, FrameThick, FrameThin, FrameRadius
from lcars.core.signal import ODN
# =============================================================================
# 1. МАТЕМАТИЧНІ КРИВІ МОДУЛЯЦІЇ (EASING)
# =============================================================================
class Easing:
    @staticmethod
    def Linear(Phase: float) -> float:
        return Phase

    @staticmethod
    def EaseIn(Phase: float) -> float:
        return Phase * Phase

    @staticmethod
    def EaseOut(Phase: float) -> float:
        return Phase * (2.0 - Phase)

    @staticmethod
    def EaseInOut(Phase: float) -> float:
        return 2.0 * Phase * Phase if Phase < 0.5 else -1.0 + (4.0 - 2.0 * Phase) * Phase

    @staticmethod
    def SineWave(Phase: float) -> float:
        Math = LCARS.System.Math
        SinFunc = getattr(Math, "sin", lambda x: 0.0) if Math else (lambda x: 0.0)
        PiVal = getattr(Math, "pi", 3.141592653589793) if Math else 3.141592653589793
        return (SinFunc(Phase * 2.0 * PiVal - PiVal / 2.0) + 1.0) / 2.0

    @staticmethod
    def PulseWave(Phase: float) -> float:
        return 1.0 if (Phase % 1.0) < 0.5 else 0.0
# =============================================================================
# 2. ГОЛОВНЕ БАЗОВЕ ЯДРО ГРАФІКИ (GRAPHIC)
# =============================================================================
class Graphic(SystemComponent):
    @staticmethod
    def Clamp(Value: float, Minimum: float, Maximum: float) -> float:
        return max(Minimum, min(Maximum, Value))

    @staticmethod
    def Lerp(Start: float, End: float, Progress: float) -> float:
        return Start + (End - Start) * Progress

    @staticmethod
    def HexToRgb(HexStr: str) -> Tuple[int, int, int]:
        if not isinstance(HexStr, str):
            return (217, 232, 255)
        HexClean = HexStr.lstrip('#')
        if len(HexClean) == 3:
            HexClean = ''.join([c * 2 for c in HexClean])
        if len(HexClean) != 6:
            return (217, 232, 255)
        return tuple(int(HexClean[i:i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def RgbToHex(Rgb: Tuple[int, int, int]) -> str:
        return f"#{int(Rgb[0]):02x}{int(Rgb[1]):02x}{int(Rgb[2]):02x}"

    @staticmethod
    def LerpColor(ColorA: str, ColorB: str, Progress: float) -> str:
        RgbA = Graphic.HexToRgb(ColorA)
        RgbB = Graphic.HexToRgb(ColorB)
        P = Graphic.Clamp(Progress, 0.0, 1.0)
        R = int(RgbA[0] + (RgbB[0] - RgbA[0]) * P)
        G = int(RgbA[1] + (RgbB[1] - RgbA[1]) * P)
        B = int(RgbA[2] + (RgbB[2] - RgbA[2]) * P)
        return Graphic.RgbToHex((R, G, B))

    def __init__(self, parent=None, widgetType=None, **kwargs):
        SystemId = kwargs.get("SystemId", kwargs.get("Id", f"{self.__class__.__name__}{id(self)}"))
        super().__init__(SystemId)
        self.Parent = parent if parent is not None else kwargs.get("Parent")
        self.Version = Version.Release
        self.X = kwargs.get("X", kwargs.get("x", 0))
        self.Y = kwargs.get("Y", kwargs.get("y", 0))
        self.Width = kwargs.get("Width", kwargs.get("width", 100))
        self.Height = kwargs.get("Height", kwargs.get("height", 30))
        self.Text = str(kwargs.get("Text", kwargs.get("text", "")))
        self.Color = kwargs.get("Color", kwargs.get("color", DefaultBackground))
        self.FontSize = kwargs.get("FontSize", kwargs.get("fontSize", 14))
        self.Thickness = kwargs.get("Thickness", FrameThick)
        self.Radius = kwargs.get("Radius", FrameRadius)
        self.Gap = kwargs.get("Gap", 6)
        self.Widget = None
        self.Primitives: List[Primitive] = []
        WidgetClass = widgetType or kwargs.get("WidgetType") or kwargs.get("widgetType")
        if WidgetClass is not None:
            self.AttachWidget(WidgetClass)

    @property
    def widget(self):
        if self.Widget is None:
            self.AttachWidget(GraphicWidget)
        return self.Widget

    @widget.setter
    def widget(self, value):
        self.Widget = value

    def AttachWidget(self, WidgetType):
        ParentWidget = self.Parent
        if ParentWidget is not None:
            PropWidget = getattr(ParentWidget, "Widget", None)
            if PropWidget is not None and not callable(PropWidget):
                ParentWidget = PropWidget
            else:
                PropWidget2 = getattr(ParentWidget, "widget", None)
                if PropWidget2 is not None and not callable(PropWidget2):
                    ParentWidget = PropWidget2

        if ParentWidget is not None:
            IsWidget = getattr(ParentWidget, "isWidgetType", None)
            if callable(IsWidget):
                if not IsWidget():
                    ParentWidget = None
            elif callable(ParentWidget):
                ParentWidget = None

        if WidgetType is GraphicWidget or (isinstance(WidgetType, type) and issubclass(WidgetType, LCARS.Widget)):
            self.Widget = WidgetType(self, ParentWidget) if WidgetType is GraphicWidget else (
                WidgetType(ParentWidget) if ParentWidget is not None else WidgetType()
            )
        elif WidgetType is not None and callable(WidgetType):
            if ParentWidget is not None:
                self.Widget = WidgetType(ParentWidget)
            else:
                self.Widget = WidgetType()
        else:
            self.Widget = None

        self.SetGeometry(self.X, self.Y, self.Width, self.Height)
        if self.Text:
            self.SetText(self.Text)
        if self.Color:
            self.SetBackgroundColor(self.Color)
        self.SetEnabled(self.Enabled)
        return self.Widget

    def SetPosition(self, X, Y):
        self.X = int(X)
        self.Y = int(Y)
        if not self.IsWidgetActive():
            self.Widget = None
            return self
        Move = getattr(self.Widget, "move", None)
        if callable(Move):
            Move(self.X, self.Y)
        return self

    def SetSize(self, Width, Height):
        self.Width = int(Width)
        self.Height = int(Height)
        if not self.IsWidgetActive():
            self.Widget = None
            return self
        Resize = getattr(self.Widget, "resize", None)
        if callable(Resize):
            Resize(self.Width, self.Height)
        return self

    def SetGeometry(self, X, Y, Width, Height):
        self.X = int(X)
        self.Y = int(Y)
        self.Width = int(Width)
        self.Height = int(Height)
        if not self.IsWidgetActive():
            self.Widget = None
            return self
        SetGeometry = getattr(self.Widget, "setGeometry", None)
        if callable(SetGeometry):
            SetGeometry(self.X, self.Y, self.Width, self.Height)
        return self

    def SetVisible(self, Visible):
        self.Visible = bool(Visible)
        if not self.IsWidgetActive():
            self.Widget = None
            return self
        Method = getattr(self.Widget, "setVisible", None)
        if callable(Method):
            Method(self.Visible)
        return self

    def SetEnabled(self, Enabled):
        self.Enabled = bool(Enabled)
        if not self.IsWidgetActive():
            self.Widget = None
            return self
        Method = getattr(self.Widget, "setEnabled", None)
        if callable(Method):
            Method(self.Enabled)
        return self

    def SetStyle(self, Style):
        if not self.IsWidgetActive():
            self.Widget = None
            return self
        Method = getattr(self.Widget, "setStyleSheet", None)
        if callable(Method):
            Method(str(Style))
        return self

    def SetBackgroundColor(self, Color):
        self.Color = Color
        return self.SetStyle(f"background-color: {Color};")

    def SetTextColor(self, Color):
        return self.SetStyle(f"color: {Color};")

    def SetFont(self, Family, Size, Weight="normal"):
        self.FontSize = int(Size)
        return self.SetStyle(f"font-family: {Family}; font-size: {self.FontSize}px; font-weight: {Weight};")

    def SetText(self, Text):
        self.Text = str(Text)
        if not self.IsWidgetActive():
            self.Widget = None
            return self
        Method = getattr(self.Widget, "setText", None)
        if callable(Method):
            Method(self.Text)
        return self

    def GetText(self):
        if not self.IsWidgetActive():
            self.Widget = None
            return self.Text
        Method = getattr(self.Widget, "text", None)
        if callable(Method):
            return Method()
        return self.Text

    def Update(self):
        if not self.IsWidgetActive():
            self.Widget = None
            return self
        Method = getattr(self.Widget, "update", None)
        if callable(Method):
            Method()
        return self

    def Repaint(self):
        if not self.IsWidgetActive():
            self.Widget = None
            return self
        Method = getattr(self.Widget, "repaint", None)
        if callable(Method):
            Method()
        return self

    def Show(self):
        return self.SetVisible(True)

    def Hide(self):
        return self.SetVisible(False)

    def Destroy(self):
        if self.IsWidgetActive():
            Method = getattr(self.Widget, "deleteLater", None)
            if callable(Method):
                Method()
            else:
                Method = getattr(self.Widget, "close", None)
                if callable(Method):
                    Method()
        self.Widget = None
        self.Parent = None
        return self

    def IsWidgetActive(self) -> bool:
        if self.Widget is None:
            return False
        SipMod = LCARS.Import("PyQt6.sip") or LCARS.Import("sip")
        if SipMod and hasattr(SipMod, "isdeleted"):
            if SipMod.isdeleted(self.Widget):
                return False
        return True
# =============================================================================
# 3. ВІДЖЕТ ВІЗУАЛІЗАЦІЇ LCARS (GRAPHIC WIDGET)
# =============================================================================
class GraphicWidget(LCARS.Widget):
    def __init__(self, GraphicInstance, ParentWidget=None):
        super().__init__(ParentWidget)
        self.Graphic = GraphicInstance
        WidthVal = max(10, int(getattr(GraphicInstance, "Width", 100)))
        HeightVal = max(10, int(getattr(GraphicInstance, "Height", 30)))
        self.setMinimumSize(1, 1)
        if hasattr(self, "setSizePolicy") and hasattr(LCARS, "Policy"):
            Pol = LCARS.Policy
            if Pol:
                self.setSizePolicy(Pol.Preferred, Pol.Preferred)
        if hasattr(self, "setCursor") and hasattr(LCARS, "CursorHand"):
            self.setCursor(LCARS.CursorHand)
        # Pulse: triggers DynamicColor algorithm automatically.
        # Only active when component has no explicit Color set.
        self.PulseTimerId = self.startTimer(1000)

    def timerEvent(self, Event):
        if not self.Graphic:
            return
        # Only repaint if color is algorithm-driven (no explicit Color locked)
        if not getattr(self.Graphic, "Color", None):
            self.update()

    def sizeHint(self):
        W = max(10, int(getattr(self.Graphic, "Width", 100))) if self.Graphic else 100
        H = max(10, int(getattr(self.Graphic, "Height", 30))) if self.Graphic else 30
        return LCARS.Size(W, H)

    def setAlignment(self, Flag):
        if hasattr(self.Graphic, "Align"):
            self.Graphic.Align = "center" if "Center" in str(Flag) else ("right" if "Right" in str(Flag) else "left")
        self.update()
        return self


    def resizeEvent(self, Event):
        if self.Graphic is not None:
            self.Graphic.Width = self.width()
            self.Graphic.Height = self.height()
            if hasattr(self.Graphic, "Generate") and callable(self.Graphic.Generate):
                self.Graphic.Generate()
        ParentResize = getattr(super(), "resizeEvent", None)
        if callable(ParentResize):
            ParentResize(Event)

    def paintEvent(self, Event):
        PainterInstance = LCARS.Painter(self)
        if hasattr(PainterInstance, "setRenderHint") and hasattr(PainterInstance, "RenderHint"):
            PainterInstance.setRenderHint(PainterInstance.RenderHint.Antialiasing, True)

        GraphicObj = self.Graphic
        IsTransparent = getattr(GraphicObj, "Transparent", False) or (GraphicObj is not None and getattr(GraphicObj, "Type", "") == "label")
        if not IsTransparent:
            PainterInstance.fillRect(self.rect(), LCARS.Color("#000000"))
        if GraphicObj is not None:
            CurrentW = self.width()
            CurrentH = self.height()
            if getattr(GraphicObj, "Width", 0) != CurrentW or getattr(GraphicObj, "Height", 0) != CurrentH:
                GraphicObj.Width = CurrentW
                GraphicObj.Height = CurrentH
                if hasattr(GraphicObj, "Generate") and callable(GraphicObj.Generate):
                    GraphicObj.Generate()

        RendererInstance = Renderer()
        RendererInstance.painter = PainterInstance

        if hasattr(GraphicObj, "Primitives") and GraphicObj.Primitives:
            for Prim in GraphicObj.Primitives:
                RendererInstance.Render(Prim)
        elif hasattr(GraphicObj, "Primitive") and GraphicObj.Primitive:
            RendererInstance.Render(GraphicObj.Primitive)
        elif hasattr(GraphicObj, "Paint") and callable(GraphicObj.Paint):
            GraphicObj.Paint(PainterInstance, self.rect())

        PainterInstance.end()

    def mousePressEvent(self, Event):

        ButtonValue = getattr(Event, "button", lambda: 1)()
        IsLeftButton = (
            ButtonValue == 1 or
            "Left" in str(ButtonValue) or
            ButtonValue == getattr(getattr(LCARS, "Protocol", None), "LeftButton", 1)
        )
        if IsLeftButton:
            TargetEngage = getattr(self.Graphic, "Engage", getattr(self.Graphic, "OnClick", None))
            if callable(TargetEngage):
                TargetEngage()
            if hasattr(self, "isVisible") and callable(self.isVisible) and self.isVisible():
                self.update()
        ParentMousePress = getattr(super(), "mousePressEvent", None)
        if callable(ParentMousePress):
            ParentMousePress(Event)

    def mouseReleaseEvent(self, Event):
        TargetRelease = getattr(self.Graphic, "Release", getattr(self.Graphic, "OnRelease", None))
        if callable(TargetRelease):
            TargetRelease()
        if hasattr(self, "isVisible") and callable(self.isVisible) and self.isVisible():
            self.update()
        ParentMouseRelease = getattr(super(), "mouseReleaseEvent", None)
        if callable(ParentMouseRelease):
            ParentMouseRelease(Event)

    def enterEvent(self, Event):
        TargetFocus = getattr(self.Graphic, "Focus", getattr(self.Graphic, "OnHover", None))
        if callable(TargetFocus):
            TargetFocus(True)
        self.update()
        ParentEnter = getattr(super(), "enterEvent", None)
        if callable(ParentEnter):
            ParentEnter(Event)

    def leaveEvent(self, Event):
        TargetFocus = getattr(self.Graphic, "Focus", getattr(self.Graphic, "OnHover", None))
        if callable(TargetFocus):
            TargetFocus(False)
        self.update()
        ParentLeave = getattr(super(), "leaveEvent", None)
        if callable(ParentLeave):
            ParentLeave(Event)
# =============================================================================
# 4. ТОПОЛОГІЧНІ ПРИМІТИВИ LCARS (PRIMITIVE)
# =============================================================================
class Primitive(Graphic):
    # Базові канонічні типи LCARS
    ELBOW = "elbow"
    BAR = "bar"
    CAP = "cap"
    COLUMN = "column"
    RECT = "rect"
    ROUNDED = "rounded"
    ROUNDED_RECT = "rounded"
    CIRCLE = "circle"
    LINE = "line"
    POINT = "point"
    POLYGON = "polygon"
    TEXT = "text"
    PATH = "path"
    ARC = "arc"
    IMAGE = "image"

    @staticmethod
    def CreateElbowPath(X: float, Y: float, Width: float, Height: float, Thickness: float, Radius: float, Corner: str = "top-left", PillarWidth: float = None, RailHeight: float = None):
        Path = LCARS.PainterPath()
        Corner = str(Corner).lower()

        H_rail = float(RailHeight or Thickness or min(28.0, Height * 0.35))
        W_pillar = float(PillarWidth or max(H_rail * 2.5, min(Width * 0.35, 120.0)))
        W_pillar = min(W_pillar, Width - 20.0)
        H_rail = min(H_rail, Height - 20.0)

        R_out = min(float(Radius or 32.0), min(W_pillar, Height) * 0.95)
        R_in = max(4.0, min(18.0, R_out * 0.5))

        if Corner in ("top-left", "tl"):
            Path.moveTo(X + R_out, Y)
            Path.lineTo(X + Width, Y)
            Path.lineTo(X + Width, Y + H_rail)
            Path.lineTo(X + W_pillar + R_in, Y + H_rail)
            Path.arcTo(X + W_pillar, Y + H_rail, R_in * 2, R_in * 2, 90, 90)
            Path.lineTo(X + W_pillar, Y + Height)
            Path.lineTo(X, Y + Height)
            Path.lineTo(X, Y + R_out)
            Path.arcTo(X, Y, R_out * 2, R_out * 2, 180, -90)
            Path.closeSubpath()
        elif Corner in ("bottom-left", "bl"):
            Path.moveTo(X, Y)
            Path.lineTo(X + W_pillar, Y)
            Path.lineTo(X + W_pillar, Y + Height - H_rail - R_in)
            Path.arcTo(X + W_pillar, Y + Height - H_rail - R_in * 2, R_in * 2, R_in * 2, 180, 90)
            Path.lineTo(X + Width, Y + Height - H_rail)
            Path.lineTo(X + Width, Y + Height)
            Path.lineTo(X + R_out, Y + Height)
            Path.arcTo(X, Y + Height - R_out * 2, R_out * 2, R_out * 2, 270, -90)
            Path.closeSubpath()
        elif Corner in ("top-right", "tr"):
            Path.moveTo(X, Y)
            Path.lineTo(X + Width - R_out, Y)
            Path.arcTo(X + Width - R_out * 2, Y, R_out * 2, R_out * 2, 90, -90)
            Path.lineTo(X + Width, Y + Height)
            Path.lineTo(X + Width - W_pillar, Y + Height)
            Path.lineTo(X + Width - W_pillar, Y + H_rail + R_in)
            Path.arcTo(X + Width - W_pillar - R_in * 2, Y + H_rail, R_in * 2, R_in * 2, 0, 90)
            Path.lineTo(X, Y + H_rail)
            Path.closeSubpath()
        else:
            Path.moveTo(X + Width - W_pillar, Y)
            Path.lineTo(X + Width, Y)
            Path.lineTo(X + Width, Y + Height - R_out)
            Path.arcTo(X + Width - R_out * 2, Y + Height - R_out * 2, R_out * 2, R_out * 2, 0, -90)
            Path.lineTo(X, Y + Height)
            Path.lineTo(X, Y + Height - H_rail)
            Path.lineTo(X + Width - W_pillar - R_in, Y + Height - H_rail)
            Path.arcTo(X + Width - W_pillar - R_in * 2, Y + Height - H_rail - R_in * 2, R_in * 2, R_in * 2, 270, 90)
            Path.closeSubpath()

        return Path

    @staticmethod
    def CreateCapPath(X: float, Y: float, Width: float, Height: float, Side: str = "left"):
        Path = LCARS.PainterPath()
        Side = str(Side).lower()
        if Side == "left":
            Radius = Height / 2.0
            Path.moveTo(X + Radius, Y)
            Path.lineTo(X + Width, Y)
            Path.lineTo(X + Width, Y + Height)
            Path.lineTo(X + Radius, Y + Height)
            Path.arcTo(X, Y, Height, Height, 270, -180)
            Path.closeSubpath()
        elif Side == "right":
            Radius = Height / 2.0
            Path.moveTo(X, Y)
            Path.lineTo(X + Width - Radius, Y)
            Path.arcTo(X + Width - Height, Y, Height, Height, 90, -180)
            Path.lineTo(X, Y + Height)
            Path.closeSubpath()
        else: # Both/Pill
            Radius = min(Width, Height) / 2.0
            Path.addRoundedRect(LCARS.RectF(float(X), float(Y), float(Width), float(Height)), float(Radius), float(Radius))
        return Path

    def __init__(self, parent=None, type="rect", **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.Type = type
        self.Points = kwargs.get("points", [])
        self.Path = kwargs.get("path", None)
        self.Side = kwargs.get("Side", kwargs.get("side", "left"))
        self.Corner = kwargs.get("Corner", kwargs.get("corner", "top-left"))
        self.RadiusX = kwargs.get("RadiusX", kwargs.get("rx", 4))
        self.RadiusY = kwargs.get("RadiusY", kwargs.get("ry", 4))
        self.LineWidth = kwargs.get("LineWidth", kwargs.get("width", 1))
        self.StartAngle = kwargs.get("StartAngle", 0)
        self.SpanAngle = kwargs.get("SpanAngle", 180)
        self.Image = kwargs.get("image", None)


# =============================================================================
# 5. ЄДИНИЙ ТОПОЛОГІЧНИЙ РЕНДЕРЕР LCARS (RENDERER)
# =============================================================================
class Renderer(Graphic):
    def __init__(self):
        self.painter = None
        self.device = None

    def Begin(self, device):
        self.device = device
        self.painter = LCARS.Painter(device) if hasattr(LCARS, "Painter") else None
        return self.painter is not None

    def End(self):
        if self.painter:
            self.painter.end()
            self.painter = None
            self.device = None
        return True

    def Render(self, primitive: Primitive):
        if not self.painter:
            return False

        PrimType = str(primitive.Type).lower()
        if PrimType == "elbow":
            return self.RenderElbow(primitive)
        elif PrimType == "cap":
            return self.RenderCap(primitive)
        elif PrimType in ("bar", "column", "rect"):
            return self.RenderRect(primitive)
        elif PrimType == "rounded":
            return self.RenderRoundedRect(primitive)
        elif PrimType == "circle":
            return self.RenderCircle(primitive)
        elif PrimType == "line":
            return self.RenderLine(primitive)
        elif PrimType == "point":
            return self.RenderPoint(primitive)
        elif PrimType == "polygon":
            return self.RenderPolygon(primitive)
        elif PrimType == "text":
            return self.RenderText(primitive)
        elif PrimType == "path":
            return self.RenderPath(primitive)
        elif PrimType == "arc":
            return self.RenderArc(primitive)
        elif PrimType == "image":
            return self.RenderImage(primitive)
        return False

    def RenderElbow(self, primitive: Primitive):
        Path = Primitive.CreateElbowPath(
            primitive.X, primitive.Y, primitive.Width, primitive.Height,
            primitive.Thickness, primitive.Radius, primitive.Corner
        )
        ColorObj = LCARS.Color(primitive.Color)
        self.painter.setBrush(LCARS.Brush(ColorObj))
        self.painter.setPen(LCARS.Pen(LCARS.Color("transparent")))
        self.painter.drawPath(Path)
        return True

    def RenderCap(self, primitive: Primitive):
        Path = Primitive.CreateCapPath(primitive.X, primitive.Y, primitive.Width, primitive.Height, primitive.Side)
        ColorObj = LCARS.Color(primitive.Color)
        self.painter.setBrush(LCARS.Brush(ColorObj))
        self.painter.setPen(LCARS.Pen(LCARS.Color("transparent")))
        self.painter.drawPath(Path)
        return True

    def RenderRect(self, primitive: Primitive):
        RectObj = LCARS.RectF(float(primitive.X), float(primitive.Y), float(primitive.Width), float(primitive.Height))
        ColorObj = LCARS.Color(primitive.Color)
        self.painter.fillRect(RectObj, ColorObj)
        return True

    def RenderRoundedRect(self, primitive: Primitive):
        RectObj = LCARS.RectF(float(primitive.X), float(primitive.Y), float(primitive.Width), float(primitive.Height))
        ColorObj = LCARS.Color(primitive.Color)
        self.painter.setBrush(LCARS.Brush(ColorObj))
        self.painter.setPen(LCARS.Pen(LCARS.Color("transparent")))
        self.painter.drawRoundedRect(RectObj, float(primitive.RadiusX), float(primitive.RadiusY))
        return True

    def RenderCircle(self, primitive: Primitive):
        Radius = float(min(primitive.Width, primitive.Height) / 2.0)
        Cx = float(primitive.X)
        Cy = float(primitive.Y)
        ColorObj = LCARS.Color(primitive.Color)
        self.painter.setBrush(LCARS.Brush(ColorObj))
        self.painter.setPen(LCARS.Pen(LCARS.Color("transparent")))
        self.painter.drawEllipse(LCARS.RectF(Cx - Radius, Cy - Radius, 2.0 * Radius, 2.0 * Radius))
        return True

    def RenderLine(self, primitive: Primitive):
        ColorObj = LCARS.Color(primitive.Color)
        self.painter.setPen(LCARS.Pen(ColorObj, float(primitive.LineWidth)))
        self.painter.drawLine(int(primitive.X), int(primitive.Y), int(primitive.X + primitive.Width), int(primitive.Y + primitive.Height))
        return True

    def RenderPoint(self, primitive: Primitive):
        ColorObj = LCARS.Color(primitive.Color)
        self.painter.setPen(LCARS.Pen(ColorObj))
        self.painter.drawPoint(int(primitive.X), int(primitive.Y))
        return True

    def RenderPolygon(self, primitive: Primitive):
        if not primitive.Points:
            return False
        ColorObj = LCARS.Color(primitive.Color)
        self.painter.setBrush(LCARS.Brush(ColorObj))
        self.painter.setPen(LCARS.Pen(LCARS.Color("transparent")))
        Poly = LCARS.PolygonF()
        for Pt in primitive.Points:
            Poly.append(LCARS.PointF(float(Pt[0]), float(Pt[1])))
        self.painter.drawPolygon(Poly)
        return True

    def RenderText(self, primitive: Primitive):
        RectObj = LCARS.RectF(float(primitive.X), float(primitive.Y), float(primitive.Width), float(primitive.Height))
        ColorObj = LCARS.Color(primitive.Color)
        self.painter.setFont(LCARS.Font("LCARS", int(primitive.FontSize)))
        self.painter.setPen(LCARS.Pen(ColorObj))
        self.painter.drawText(RectObj, int(LCARS.AlignCenter), str(primitive.Text))
        return True

    def RenderPath(self, primitive: Primitive):
        if not primitive.Path:
            return False
        ColorObj = LCARS.Color(primitive.Color)
        self.painter.setBrush(LCARS.Brush(ColorObj))
        self.painter.setPen(LCARS.Pen(LCARS.Color("transparent")))
        self.painter.drawPath(primitive.Path)
        return True

    def RenderArc(self, primitive: Primitive):
        RectObj = LCARS.RectF(float(primitive.X), float(primitive.Y), float(primitive.Width), float(primitive.Height))
        ColorObj = LCARS.Color(primitive.Color)
        self.painter.setPen(LCARS.Pen(ColorObj, float(primitive.LineWidth)))
        self.painter.drawArc(RectObj, int(primitive.StartAngle), int(primitive.SpanAngle))
        return True

    def RenderImage(self, primitive: Primitive):
        if not primitive.Image:
            return False
        PixmapObj = LCARS.Pixmap(primitive.Image)
        self.painter.drawPixmap(int(primitive.X), int(primitive.Y), PixmapObj)
        return True
# =============================================================================
# 6. БУДІВНИК ІНТЕРФЕЙСУ LCARS (LCARS BUILDER)
# =============================================================================
class LCARSBuilder(SystemComponent):
    def __init__(self, parent=None):
        self.Parent = parent
        self.Components = []
        self.Items = {}
        self.Layout = None

    def WidgetTarget(self, Item):
        Target = getattr(Item, "widget", Item)
        if callable(Target):
            return Item
        return Target

    def LayoutTarget(self, Item):
        Target = getattr(Item, "layout", Item)
        if callable(Target):
            return Item
        return Target

    def Vertical(self, widget, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        VBox = getattr(LCARS, "Vertical", None)
        if not VBox:
            return None
        GetLayout = getattr(widget, "layout", None)
        Layout = GetLayout() if GetLayout else None
        if not Layout:
            Layout = VBox()
            SetLayout = getattr(widget, "setLayout", None)
            if SetLayout:
                SetLayout(Layout)
        Layout.setContentsMargins(Left, Top, Right, Bottom)
        Layout.setSpacing(Spacing)
        self.Layout = Layout
        return Layout

    def Horizontal(self, widget, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        HBox = getattr(LCARS, "Horizontal", None)
        if not HBox:
            return None
        GetLayout = getattr(widget, "layout", None)
        Layout = GetLayout() if GetLayout else None
        if not Layout:
            Layout = HBox()
            SetLayout = getattr(widget, "setLayout", None)
            if SetLayout:
                SetLayout(Layout)
        Layout.setContentsMargins(Left, Top, Right, Bottom)
        Layout.setSpacing(Spacing)
        self.Layout = Layout
        return Layout

    def Add(self, Layout, Element, Stretch=None):
        AddWidget = getattr(Layout, "addWidget", None)
        if not AddWidget:
            return
        Target = self.WidgetTarget(Element)
        if Stretch is None:
            AddWidget(Target)
        else:
            AddWidget(Target, Stretch)

    def AddLayout(self, Layout, ChildLayout):
        AddLayout = getattr(Layout, "addLayout", None)
        if AddLayout:
            Target = self.LayoutTarget(ChildLayout)
            AddLayout(Target)

    def AddStretch(self, Layout):
        AddStretch = getattr(Layout, "addStretch", None)
        if AddStretch:
            AddStretch()

    def Clear(self, Layout=None):
        if Layout is None:
            Layout = getattr(self.Parent, "layout", lambda: None)()
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

    def BuildPanel(self, widget):
        if hasattr(widget, "setStyleSheet"):
            widget.setStyleSheet("background-color: #000000; border: none;")

    def BuildHeader(self, widget, title="", **kwargs):
        self.BuildPanel(widget)
        self.Horizontal(widget, 0, 0, 0, 0, 8)
        self.Items["Elbow"] = Primitive(Parent=widget, type=Primitive.ELBOW, Corner="top-left", Color=Palette.Buttons[0])
        self.Items["Title"] = Primitive(Parent=widget, type=Primitive.TEXT, Text=title, Color=Palette.Buttons[2])
        self.Items["Bar"] = Primitive(Parent=widget, type=Primitive.BAR, Color=Palette.Buttons[1])
        return self.Items

    def BuildFooter(self, widget, status="READY", **kwargs):
        self.BuildPanel(widget)
        self.Horizontal(widget, 0, 0, 0, 0, 8)
        self.Items["Bar"] = Primitive(Parent=widget, type=Primitive.BAR, Color=Palette.Buttons[1])
        self.Items["Status"] = Primitive(Parent=widget, type=Primitive.TEXT, Text=status, Color=Palette.Buttons[0])
        self.Items["Elbow"] = Primitive(Parent=widget, type=Primitive.ELBOW, Corner="bottom-right", Color=Palette.Buttons[2])
        return self.Items

    def BuildSidebar(self, widget, **kwargs):
        self.BuildPanel(widget)
        self.Vertical(widget, 0, 0, 0, 0, 6)
        self.Items["Top"] = Primitive(Parent=widget, type=Primitive.ELBOW, Corner="top-left", Color=Palette.Buttons[0])
        self.Items["Rail"] = Primitive(Parent=widget, type=Primitive.COLUMN, Color=Palette.Buttons[1])
        self.Items["Bottom"] = Primitive(Parent=widget, type=Primitive.ELBOW, Corner="bottom-left", Color=Palette.Buttons[2])
        return self.Items

    # Застосовує технічний стиль до графічного віджета.
def SetStyle(TargetWidget, Style):
    Setter = getattr(TargetWidget, "setStyleSheet", None)

    if callable(Setter):
        Setter(str(Style))

Builder = LCARSBuilder
__all__ = ["Easing", "Graphic", "GraphicWidget", "Primitive", "Renderer", "LCARSBuilder", "Builder", "SetStyle"]
