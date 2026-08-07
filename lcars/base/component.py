# LCARS Базові компоненти LCARS.
# Тут тільки нижній шар. Клас має розрізняти свій тип всередині:
# кнопка розуміє свою форму, індикатор розуміє режим напису або статусу,
# лікоть розуміє напрям, бар розуміє режим смуги, Primitive розуміє фігуру.
# Готові елементи і повні панелі збираються у lcars/base/interface.py.

from typing import Any, Dict, Optional

from lcars.base.default import (
    ContrastColor, CycleNormal, DefaultFontFamily, DefaultFontWeight,
    FrameRadius, FrameThick, FrameThin, MinFontSize,
    Palette, FontStyle, Take,
    RandomButtonColor, SetStyle, SetName, Widget, Normalize, NormalizeFontWeight,
    PickColor, ResolvePaletteGroup,
)
def ButtonMetrics(Width: int, Height: int, ButtonType: str = "rect") -> Dict[str, int]:
    W = max(24, int(Width))
    H = max(18, int(Height))
    R = max(4, min(H // 2, W // 4))
    Gap = max(4, H // 7)
    Cap = max(H, min(W // 3, H + H // 3))
    Rail = max(6, H // 5)
    Stripe = max(5, H // 8)
    Pad = max(8, H // 4)
    return {
        "width": W,
        "height": H,
        "radius": R,
        "gap": Gap,
        "cap": Cap,
        "rail": Rail,
        "stripe": Stripe,
        "pad": Pad,
    }

def AdaptiveTextSize(Text: str, Width: int, Height: int, BaseSize: int) -> int:
    TextValue = str(Text or "").strip()
    W = max(1, int(Width))
    H = max(1, int(Height))
    Base = max(MinFontSize, int(BaseSize or MinFontSize))
    HeightSize = max(MinFontSize, int(H * 0.46))
    if not TextValue:
        return min(max(Base, HeightSize), 72)
    WidthSize = int(W / max(1, len(TextValue)) * 1.45)
    return max(MinFontSize, min(HeightSize, WidthSize, 72))

def SoftRadius(Width: int, Height: int) -> int:
    W = max(1, int(Width))
    H = max(1, int(Height))
    # A modern soft-rounded rectangle (not a pill), using a smaller max radius
    return max(4, min(H // 4, W // 8, 12))

# Функція для отримання повного набору стилю кнопки з урахуванням типу, циклів та випадковості
def ResolveButtonStyle(ButtonType: str = "rect", Seed: Optional[Any] = None, Overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    Key = Normalize(ButtonType)
    Base = ButtonStyles.get(Key, ButtonStyles["rect"]).copy()
    Base["type"] = Key
    Base["shape"] = Normalize(Base.get("shape", Key))
    if not Base.get("color"):
        Base["color"] = RandomButtonColor(Base.get("colorGroup", "buttons"), Seed or Key)
        Base["generatedColor"] = True
    else:
        Base["generatedColor"] = False
    if not Base.get("capColor"):
        CapGroup = Base.get("capGroup", Base.get("colorGroup", "buttons"))
        Base["capColor"] = RandomButtonColor(CapGroup, f"{Seed or Key}.cap")
    if not Base.get("accentColor"):
        Accent = Base.get("accent")
        if Accent:
            Base["accentColor"] = Accent
        else:
            AccentGroup = Base.get("accentGroup", "accent")
            Base["accentColor"] = RandomButtonColor(AccentGroup, f"{Seed or Key}.accent")
    if Overrides:
        for Name, Value in Overrides.items():
            if Value is not None:
                Base[Name] = Value
    return Base

from lcars.base.graphic import Graphic
from lcars.base.type import LCARS
# Базовий клас для всіх компонентів LCARS (кнопки, індикатори, лікоті, бари, примітиви)
# Базовий графічний клас для всіх компонентів LCARS
class Component(Graphic):
    def __init__(self, Parent=None, **Args):
        # Отримуємо базові параметри
        ParentVal = Args.get("parent", Args.get("Parent", Parent))
        ColorVal = Args.get("color", Args.get("Color", Args.get("ColorHexStr", None)))
        TextVal = Args.get("text", Args.get("Text", ""))
        TypeVal = Args.get("type", Args.get("Type", ""))
        ShapeVal = Args.get("shape", Args.get("Shape", ""))
        
        # Визначаємо тип компонента
        CompType = Args.get("ComponentType", Args.get("componentType", None))
        if not CompType:
            if "direction" in Args or "Direction" in Args:
                CompType = "elbow"
            elif ShapeVal or "shape" in Args or "Shape" in Args:
                CompType = "primitive"
            elif "blink" in Args or "Blink" in Args or "status" in Args or "Status" in Args or Normalize(TypeVal) in ["label", "status", "alert", "value", "title", "console"]:
                CompType = "indicator"
            elif Normalize(TypeVal) in ["bar", "divider", "scanning"]:
                CompType = "bar"
            elif "widgetType" in Args or "WidgetType" in Args:
                CompType = "container"
            else:
                CompType = "button"
                
        self.CompType = Normalize(CompType)
        
        # Визначаємо базовий клас віджета
        if self.CompType == "button":
            WidgetClass = Args.get("widgetType", Args.get("WidgetType", None)) or LCARS.Segment
        elif self.CompType in ["indicator", "label"]:
            WidgetClass = LCARS.Label
        else:
            WidgetClass = Args.get("widgetType", Args.get("WidgetType", None)) or LCARS.Segment
            
        # Видаляємо дубльовані аргументи перед викликом super().__init__
        Args.pop("parent", None)
        Args.pop("Parent", None)
        Args.pop("widgetType", None)
        Args.pop("WidgetType", None)
        Args.pop("ComponentType", None)
        Args.pop("componentType", None)
        
        super().__init__(
            Parent=ParentVal,
            WidgetType=WidgetClass,
            **Args,
        )
        
        self.Elements = []
        self.Layout = None
        self.Style = {}
        
        # Ініціалізуємо логіку конкретного типу
        if self.CompType == "button":
            self.InitButton(**Args)
        elif self.CompType == "indicator":
            self.InitIndicator(**Args)
        elif self.CompType == "label":
            self.InitLabel(**Args)
        elif self.CompType == "elbow":
            self.InitElbow(**Args)
        elif self.CompType == "bar":
            self.InitBar(**Args)
        elif self.CompType == "primitive":
            self.InitPrimitive(**Args)
    # =========================================================================
    # КОНТЕЙНЕР
    # =========================================================================
    def AddElement(self, Element):
        if Element not in self.Elements:
            self.Elements.append(Element)
            if hasattr(Element, "Parent"):
                Element.Parent = self

    def RemoveElement(self, Element):
        if Element in self.Elements:
            self.Elements.remove(Element)
            if hasattr(Element, "Parent"):
                Element.Parent = None

    def GetElements(self):
        if getattr(self, "CompType", None) == "button":
            return [self, self.Label]
        return self.Elements.copy()

    def SetLayout(self, Layout):
        self.Layout = Layout

    def Build(self):
        if not self.Layout:
            return
        Add = getattr(self.Layout, "addWidget", None)
        if not Add:
            return
        for Element in self.Elements:
            Add(Element.widget)

    def Clear(self):
        for Element in self.Elements:
            if hasattr(Element, "Parent"):
                Element.Parent = None
        self.Elements.clear()
    # =========================================================================
    # КНОПКА (BUTTON)
    # =========================================================================
    def InitButton(self, **Args):
        Text = Args.get("text", Args.get("Text", ""))
        Color = Args.get("color", Args.get("Color", Args.get("ColorHexStr", None)))
        Type = Args.get("type", Args.get("Type", "rect"))
        Sound = Args.get("sound", Args.get("Sound", None))
        State = Args.get("state", Args.get("State", "normal"))
        Active = Args.get("active", Args.get("Active", Args.get("enabled", Args.get("Enabled", True))))
        Prefix = Args.get("prefix", Args.get("Prefix", ""))
        Suffix = Args.get("suffix", Args.get("Suffix", ""))
        Animated = Args.get("animated", Args.get("Animated", True))
        Cycle = Args.get("cycle", Args.get("Cycle", None))
        CycleRate = Args.get("cycleRate", Args.get("CycleRate", int(CycleNormal * 1000)))
        ColorGroup = Args.get("colorGroup", Args.get("ColorGroup", "buttons"))
        StyleOverrides = {
            "color": Color,
            "sound": Sound,
            "fontSize": Args.get("fontSize", Args.get("FontSize", None)),
            "fontFamily": Args.get("fontFamily", Args.get("FontFamily", None)),
            "weight": Args.get("weight", Args.get("Weight", Args.get("fontWeight", Args.get("FontWeight", None)))),
            "capColor": Args.get("capColor", Args.get("CapColor", None)),
            "accentColor": Args.get("accentColor", Args.get("AccentColor", None)),
            "gap": Args.get("gap", Args.get("Gap", None)),
        }
        self.ButtonStyle = ResolveButtonStyle(Type, Args.get("seed", Args.get("Seed", Text or Type)), StyleOverrides)
        
        self.Type = self.ButtonStyle.get("type", Normalize(Type) or "rect")
        self.Shape = self.ButtonStyle.get("shape", self.Type)
        self.RawText = str(Text or "")
        self.Prefix = str(Prefix or "")
        self.Suffix = str(Suffix or "")
        self.ExplicitColor = Color is not None
        self.GeneratedColor = not self.ExplicitColor and bool(self.ButtonStyle.get("generatedColor", False))
        self.BaseColor = Color if self.ExplicitColor else None
        self.ColorGroup = str(self.ButtonStyle.get("colorGroup", ColorGroup or "buttons"))
        self.CapGroup = str(self.ButtonStyle.get("capGroup", self.ColorGroup))
        self.AccentGroup = str(self.ButtonStyle.get("accentGroup", "accent"))
        self.ColorSeed = Args.get("seed", Args.get("Seed", self.RawText or self.Type))
        self.ColorPhase = 0
        self.Color = self.ButtonStyle.get("color", self.ResolveButtonColor())
        self.State = Normalize(State) or "normal"
        self.Active = bool(Active)
        self.Animated = bool(Animated)
        StaticTypes = ["alert", "warning", "terminate", "abort", "disabled"]
        self.Cycle = bool(Cycle) if Cycle is not None else (self.GeneratedColor and Normalize(Type) not in StaticTypes)
        self.Pressed = False
        self.Weight = NormalizeFontWeight(self.ButtonStyle.get("weight", DefaultFontWeight))
        self.FontFamily = self.ButtonStyle.get("fontFamily", DefaultFontFamily)
        self.FontSize = self.ButtonStyle.get("fontSize", self.FontSize)
        self.Label = LCARSLabel(self.RawText, self.Prefix, self.Suffix, self.FontFamily, self.FontSize, self.Weight)
        self.Text = self.Label.GetText()
        self.Sound = self.ButtonStyle.get("sound") or self.DefaultSound()
        self.CapColor = self.ButtonStyle.get("capColor", self.Color)
        self.AccentColor = self.ButtonStyle.get("accentColor", Palette.Buttons[2])
        self.Gap = int(self.ButtonStyle.get("gap", 8))
        self.Number = str(Args.get("number", Args.get("Number", Args.get("value", Args.get("Value", "47")))))
        self.Characteristics = {
            "Color": self.Color,
            "Font": {"Family": self.FontFamily, "Size": self.FontSize, "Weight": self.Weight},
            "Sound": self.Sound,
        }

        from lcars.core.signal import Transmission
        self.Clicked = Transmission()
        self.Toggled = Transmission()

        self.ApplyText()
        if hasattr(self.widget, "setMinimumHeight"):
            self.widget.setMinimumHeight(52)
        if hasattr(self.widget, "setMinimumWidth"):
            self.widget.setMinimumWidth(100)
        if hasattr(self.widget, "setSizePolicy"):
            Policy = LCARS.Policy
            if Policy:
                self.widget.setSizePolicy(Policy.Expanding, Policy.Expanding)
        if hasattr(self.widget, "setEnabled"):
            self.widget.setEnabled(self.Active)

        HandCursor = LCARS.CursorHand
        if HandCursor is not None and hasattr(self.widget, "setCursor"):
            self.widget.setCursor(HandCursor)

        self.Connect()
        self.ApplyStyle()
        if self.Cycle:
            self.ConnectColorCycle(CycleRate)

    @property
    def clicked(self):
        return self.Clicked

    @property
    def toggled(self):
        return self.Toggled

    def DefaultSound(self):
        Text = self.Text.upper()
        if self.Color in Palette.RedAlert or Text in ["RED ALERT", "CRITICAL", "TERMINATE"]:
            return "alert_red"
        if self.Color in Palette.YellowAlert or Text in ["YELLOW ALERT", "CAUTION"]:
            return "alert_yellow"
        if Text in ["ABORT", "CANCEL"]:
            return "click"
        return "acknowledge"

    def ResolveButtonColor(self):
        if self.BaseColor:
            return self.BaseColor
        return RandomButtonColor(self.ColorGroup, self.ColorSeed)

    def Connect(self):
        if not self.Active:
            return
        Click = getattr(self.widget, "clicked", None)
        Toggle = getattr(self.widget, "toggled", None)
        Pressed = getattr(self.widget, "pressed", None)
        Released = getattr(self.widget, "released", None)
        if Click and hasattr(Click, "connect"):
            Click.connect(self.OnClicked)
        else:
            self.widget.mousePressEvent = lambda Event: self.OnPressed()
            self.widget.mouseReleaseEvent = lambda Event: self.OnReleaseClick()
        if Toggle and hasattr(Toggle, "connect"):
            Toggle.connect(lambda: self.Toggled.Emit())
        if Pressed and hasattr(Pressed, "connect"):
            Pressed.connect(self.OnPressed)
        if Released and hasattr(Released, "connect"):
            Released.connect(self.OnReleased)

    def ConnectColorCycle(self, CycleRate):
        Timer = LCARS.Timer
        if not Timer:
            self.Cycle = False
            return
        self.ColorTimer = Timer(self.widget)
        Timeout = getattr(self.ColorTimer, "timeout", None)
        Connect = getattr(Timeout, "connect", None)
        Start = getattr(self.ColorTimer, "start", None)
        if not Connect or not Start:
            self.Cycle = False
            return
        Connect(self.StepColor)
        Start(int(CycleRate))

    def StepColor(self):
        if not self.BaseColor:
            PaletteGroup = ResolvePaletteGroup(self.ColorGroup)
            if PaletteGroup:
                Offset = hash(str(self.ColorSeed)) % len(PaletteGroup)
                self.ColorPhase = (self.ColorPhase + 1) % len(PaletteGroup)
                self.Color = PaletteGroup[(Offset + self.ColorPhase) % len(PaletteGroup)]
            CapPalette = ResolvePaletteGroup(getattr(self, "CapGroup", self.ColorGroup))
            if CapPalette:
                CapOffset = hash(f"{self.ColorSeed}.cap") % len(CapPalette)
                self.CapColor = CapPalette[(CapOffset + self.ColorPhase) % len(CapPalette)]
            AccentPalette = ResolvePaletteGroup(getattr(self, "AccentGroup", "accent"))
            if AccentPalette:
                AccentOffset = hash(f"{self.ColorSeed}.accent") % len(AccentPalette)
                self.AccentColor = AccentPalette[(AccentOffset + self.ColorPhase) % len(AccentPalette)]
            self.ApplyStyle()

    def OnPressed(self):
        if not self.Active:
            return
        self.Pressed = True
        if self.Animated:
            self.ApplyStyle()
        self.OnClicked() # Emit instantly on touch/press for zero-delay responsiveness

    def OnReleased(self):
        if not self.Active:
            return
        self.Pressed = False
        if self.Animated:
            self.ApplyStyle()

    def OnReleaseClick(self):
        self.OnReleased()
        # self.OnClicked() moved to OnPressed for instant response

    def PlaySound(self, Name):
        if not Name or Name == "none":
            return
        from lcars.base.default import AudioEnabled
        if not AudioEnabled:
            return
        from lcars.modules.sound import GetSound
        Manager = GetSound()
        if Manager is not None and hasattr(Manager, "play"):
            Played = Manager.play(Name)
            if Played:
                return
        if LCARS.Platform:
            import winsound
            winsound.MessageBeep()

    def OnClicked(self):
        if not getattr(self, "Active", True):
            return
        sound = getattr(self, "Sound", None)
        if sound:
            self.PlaySound(sound)
        if hasattr(self, "Clicked"):
            self.Clicked.Emit()

    def mousePressEvent(self, Event):
        self.OnClicked()

    def BuildText(self):
        Label = getattr(self, "Label", None)
        if Label:
            return Label.GetText()
        Parts = []
        if self.Prefix:
            Parts.append(self.Prefix)
        if self.RawText:
            Parts.append(self.RawText)
        if self.Suffix:
            Parts.append(self.Suffix)
        return " ".join(Parts)

    def ApplyText(self):
        self.Text = self.BuildText()
        if hasattr(self.widget, "setText"):
            self.widget.setText(self.Text.upper())

    def SetText(self, Text):
        if self.CompType == "button":
            self.Label.SetText(Text)
            self.RawText = self.Label.Text
            self.ApplyText()
            self.Update()
        elif self.CompType == "indicator":
            self.Text = str(Text)
            if hasattr(self.widget, "setText"):
                self.widget.setText("")
            self.Update()
        else:
            self.Text = str(Text)
            self.Update()

    def SetColor(self, Color):
        self.BaseColor = Color
        self.Color = self.ResolveButtonColor()
        if isinstance(getattr(self, "Characteristics", None), dict):
            self.Characteristics["Color"] = self.Color
        if self.CompType in ["button", "indicator", "label"]:
            self.ApplyStyle()
        else:
            self.Update()

    def SetType(self, Type):
        if self.CompType == "button":
            self.ButtonStyle = ResolveButtonStyle(Type, self.ColorSeed, None)
            self.Type = self.ButtonStyle.get("type", Normalize(Type) or "rect")
            self.Shape = self.ButtonStyle.get("shape", self.Type)
            self.GeneratedColor = bool(self.ButtonStyle.get("generatedColor", False))
            self.BaseColor = None if self.GeneratedColor else self.ButtonStyle.get("color")
            self.ColorGroup = str(self.ButtonStyle.get("colorGroup", self.ColorGroup))
            self.CapGroup = str(self.ButtonStyle.get("capGroup", self.ColorGroup))
            self.AccentGroup = str(self.ButtonStyle.get("accentGroup", "accent"))
            self.Color = self.ButtonStyle.get("color", self.ResolveButtonColor())
            self.Sound = self.ButtonStyle.get("sound") or self.DefaultSound()
            self.Weight = NormalizeFontWeight(self.ButtonStyle.get("weight", self.Weight))
            self.FontFamily = self.ButtonStyle.get("fontFamily", self.FontFamily)
            self.FontSize = self.ButtonStyle.get("fontSize", self.FontSize)
            self.Label.SetFont(self.FontFamily, self.FontSize, self.Weight)
            self.CapColor = self.ButtonStyle.get("capColor", self.Color)
            self.AccentColor = self.ButtonStyle.get("accentColor", self.AccentColor)
            self.Gap = int(self.ButtonStyle.get("gap", self.Gap))
            self.Characteristics = {
                "Color": self.Color,
                "Font": {"Family": self.FontFamily, "Size": self.FontSize, "Weight": self.Weight},
                "Sound": self.Sound,
            }
            self.ApplyStyle()
        elif self.CompType == "indicator":
            TypeKey = Normalize(Type) or "rect-left"
            if TypeKey in ["rect-left", "rect-right", "pill-left", "pill-right", "soft-left", "soft-right"]:
                self.Shape = TypeKey
            else:
                self.Type = TypeKey
            self.Update()
        elif self.CompType == "bar":
            self.Type = Normalize(Type) or "rect"
            self.Update()

    def SetState(self, State):
        self.State = Normalize(State) or "normal"
        if self.CompType == "button":
            self.ApplyStyle()

    def SetActive(self, Active):
        self.Active = bool(Active)
        if hasattr(self.widget, "setEnabled"):
            self.widget.setEnabled(self.Active)
        if self.CompType == "button":
            self.ApplyStyle()

    def ApplyStyle(self):
        if self.CompType == "button":
            self.ApplyButtonStyle()
        elif self.CompType == "indicator":
            self.Update()
        elif self.CompType == "label":
            self.ApplyLabelStyle()

    def ApplyButtonStyle(self):
        SetName(self.widget, "LCARSButton")
        SetStyle(self.widget, "#LCARSButton { background-color: transparent; border: none; }")
        self.Update()

    def ButtonColor(self):
        ColorValue = self.Color
        if self.Type in ["warning"] or self.State in ["warning", "yellow"]:
            ColorValue = Palette.YellowAlert[0]
        elif self.Type in ["alert", "terminate"] or self.State in ["critical", "red", "alert"]:
            ColorValue = Palette.RedAlert[0]
        elif self.Type in ["disabled"] or self.State in ["disabled", "inactive", "off"] or not self.Active:
            ColorValue = "#333333"
        elif self.Pressed:
            ColorValue = "#FFFFFF"
        return PickColor(ColorValue)

    def DrawLeftCap(self, X, Y, Width, Height, Color):
        Radius = max(2, Height // 2)
        self.DrawCircle(X + Radius, Y + Radius, Radius, Color)
        self.DrawRect(X + Radius, Y, max(0, Width - Radius), Height, Color)

    def DrawRightCap(self, X, Y, Width, Height, Color):
        Radius = max(2, Height // 2)
        self.DrawRect(X, Y, max(0, Width - Radius), Height, Color)
        self.DrawCircle(X + Width - Radius, Y + Radius, Radius, Color)

    def DrawSoftLeft(self, X, Y, Width, Height, Color):
        Radius = SoftRadius(Width, Height)
        self.DrawRoundedRect(X, Y, Width, Height, Radius, Radius, Color)
        self.DrawRect(X + Width - Radius, Y, Radius, Height, Color)

    def DrawSoftRight(self, X, Y, Width, Height, Color):
        Radius = SoftRadius(Width, Height)
        self.DrawRoundedRect(X, Y, Width, Height, Radius, Radius, Color)
        self.DrawRect(X, Y, Radius, Height, Color)

    def DrawTopCap(self, X, Y, Width, Height, Color):
        Radius = max(2, Width // 2)
        self.DrawCircle(X + Radius, Y + Radius, Radius, Color)
        self.DrawRect(X, Y + Radius, Width, max(0, Height - Radius), Color)

    def DrawBottomCap(self, X, Y, Width, Height, Color):
        Radius = max(2, Width // 2)
        self.DrawRect(X, Y, Width, max(0, Height - Radius), Color)
        self.DrawCircle(X + Radius, Y + Height - Radius, Radius, Color)

    def RenderButton(self):
        self.ClearCommands()
        WidthValue = self.widget.width() if hasattr(self.widget, "width") else int(self.Width)
        HeightValue = self.widget.height() if hasattr(self.widget, "height") else int(self.Height)
        MetricsValue = ButtonMetrics(WidthValue, HeightValue, self.Type)
        WidthValue = MetricsValue["width"]
        HeightValue = MetricsValue["height"]
        ColorValue = self.ButtonColor()
        Radius = MetricsValue["radius"]
        Kind = Normalize(getattr(self, "Shape", self.Type))
        TextColor = "#777777" if not self.Active else ContrastColor(ColorValue)
        AccentColor = self.AccentColor
        CapColor = self.CapColor or ColorValue
        Gap = max(MetricsValue["gap"], int(self.Gap))
        Cap = MetricsValue["cap"]
        Rail = MetricsValue["rail"]
        Stripe = MetricsValue["stripe"]
        Pad = MetricsValue["pad"]
        IndicatorW = max(18, min(HeightValue // 2, WidthValue // 6))
        TextX = Pad
        TextY = 0
        TextW = WidthValue - Pad * 2
        TextH = HeightValue

        if Kind in ["rect", "block"]:
            self.DrawRect(0, 0, WidthValue, HeightValue, ColorValue)
        elif Kind == "soft":
            RadiusValue = SoftRadius(WidthValue, HeightValue)
            self.DrawRoundedRect(0, 0, WidthValue, HeightValue, RadiusValue, RadiusValue, ColorValue)
        elif Kind in ["rect-ind-left", "rect-indicator-left"]:
            BodyX = IndicatorW + Gap
            BodyW = WidthValue - BodyX
            self.DrawRect(0, 0, IndicatorW, HeightValue, AccentColor)
            self.DrawRect(BodyX, 0, BodyW, HeightValue, ColorValue)
            TextX = BodyX + Pad
            TextW = BodyW - Pad * 2
        elif Kind in ["rect-ind-right", "rect-indicator-right"]:
            BodyW = WidthValue - IndicatorW - Gap
            self.DrawRect(0, 0, BodyW, HeightValue, ColorValue)
            self.DrawRect(BodyW + Gap, 0, IndicatorW, HeightValue, AccentColor)
            TextX = Pad
            TextW = BodyW - Pad * 2
        elif Kind in ["soft-ind-left", "soft-indicator-left"]:
            BodyX = IndicatorW + Gap
            BodyW = WidthValue - BodyX
            RadiusValue = SoftRadius(BodyW, HeightValue)
            self.DrawRect(0, 0, IndicatorW, HeightValue, AccentColor)
            self.DrawRoundedRect(BodyX, 0, BodyW, HeightValue, RadiusValue, RadiusValue, ColorValue)
            TextX = BodyX + Pad
            TextW = BodyW - Pad * 2
        elif Kind in ["soft-ind-right", "soft-indicator-right"]:
            BodyW = WidthValue - IndicatorW - Gap
            RadiusValue = SoftRadius(BodyW, HeightValue)
            self.DrawRoundedRect(0, 0, BodyW, HeightValue, RadiusValue, RadiusValue, ColorValue)
            self.DrawRect(BodyW + Gap, 0, IndicatorW, HeightValue, AccentColor)
            TextX = Pad
            TextW = BodyW - Pad * 2
        elif Kind in ["selected-code", "selected-indicator"]:
            NumberW = max(54, HeightValue)
            BodyW = max(80, WidthValue - IndicatorW - NumberW - Gap * 2)
            self.DrawRect(0, 0, IndicatorW, HeightValue, "#FFFFFF")
            self.DrawPill(IndicatorW + Gap, 0, BodyW, HeightValue, ColorValue)
            self.DrawRect(IndicatorW + Gap + BodyW + Gap, 0, NumberW, HeightValue, CapColor)
            self.DrawText(self.Number, IndicatorW + Gap + BodyW + Gap, 0, NumberW, HeightValue, self.FontSize, "center", ContrastColor(CapColor), self.FontFamily)
            TextX = IndicatorW + Gap + Pad
            TextW = BodyW - Pad * 2
        elif Kind == "pill":
            self.DrawPill(0, 0, WidthValue, HeightValue, ColorValue)
        elif Kind in ["left", "round-left", "cap-left"]:
            self.DrawLeftCap(0, 0, WidthValue, HeightValue, ColorValue)
            TextX = Radius + Pad // 2
            TextW = WidthValue - Radius - Pad
        elif Kind in ["right", "round-right", "cap-right"]:
            self.DrawRightCap(0, 0, WidthValue, HeightValue, ColorValue)
            TextX = Pad
            TextW = WidthValue - Radius - Pad
        elif Kind in ["pill-left", "half-pill-left"]:
            self.DrawLeftCap(0, 0, WidthValue, HeightValue, ColorValue)
            TextX = Radius + Pad // 2
            TextW = WidthValue - Radius - Pad
        elif Kind in ["pill-right", "half-pill-right"]:
            self.DrawRightCap(0, 0, WidthValue, HeightValue, ColorValue)
            TextX = Pad
            TextW = WidthValue - Radius - Pad
        elif Kind in ["soft-left", "half-soft-left"]:
            self.DrawSoftLeft(0, 0, WidthValue, HeightValue, ColorValue)
            TextX = Pad
            TextW = WidthValue - Pad * 2
        elif Kind in ["soft-right", "half-soft-right"]:
            self.DrawSoftRight(0, 0, WidthValue, HeightValue, ColorValue)
            TextX = Pad
            TextW = WidthValue - Pad * 2
        elif Kind in ["top", "round-top", "cap-top"]:
            self.DrawTopCap(0, 0, WidthValue, HeightValue, ColorValue)
            TextX = Pad
            TextY = Radius + Pad // 2
            TextW = WidthValue - Pad * 2
            TextH = HeightValue - Radius - Pad
        elif Kind in ["bottom", "round-bottom", "cap-bottom"]:
            self.DrawBottomCap(0, 0, WidthValue, HeightValue, ColorValue)
            TextX = Pad
            TextW = WidthValue - Pad * 2
            TextH = HeightValue - Radius - Pad
        elif Kind in ["tab-left", "block-left"]:
            self.DrawLeftCap(0, 0, Cap, HeightValue, CapColor)
            self.DrawRect(Cap + Gap, 0, WidthValue - Cap - Gap, HeightValue, ColorValue)
            TextX = Cap + Gap + Pad
            TextW = WidthValue - Cap - Gap - Pad * 2
        elif Kind in ["tab-right", "block-right"]:
            self.DrawRect(0, 0, WidthValue - Cap - Gap, HeightValue, ColorValue)
            self.DrawRightCap(WidthValue - Cap, 0, Cap, HeightValue, CapColor)
            TextX = Pad
            TextW = WidthValue - Cap - Gap - Pad * 2
        elif Kind in ["split", "segmented"]:
            Half = max(1, (WidthValue - Gap) // 2)
            self.DrawRect(0, 0, Half, HeightValue, ColorValue)
            self.DrawRect(Half + Gap, 0, WidthValue - Half - Gap, HeightValue, AccentColor)
            TextX = Pad
            TextW = WidthValue - Pad * 2
        elif Kind in ["code", "access-code"]:
            CapW = max(38, HeightValue)
            self.DrawRect(0, HeightValue // 2 - Rail // 2, WidthValue - CapW - Gap, Rail, ColorValue)
            self.DrawRect(WidthValue - CapW - Gap, 0, Gap, HeightValue, AccentColor)
            self.DrawRightCap(WidthValue - CapW, 0, CapW, HeightValue, CapColor)
            TextX = Pad
            TextW = WidthValue - CapW - Gap - Pad * 2
        elif Kind in ["authorize", "confirm"]:
            CapW = max(42, HeightValue)
            self.DrawRect(0, 0, WidthValue - CapW - Gap, HeightValue, ColorValue)
            self.DrawRect(WidthValue - CapW - Gap, 0, Gap, HeightValue, "#000000")
            self.DrawRightCap(WidthValue - CapW, 0, CapW, HeightValue, AccentColor)
            TextX = Pad
            TextW = WidthValue - CapW - Gap - Pad * 2
        elif Kind in ["status", "long"]:
            self.DrawPill(0, HeightValue // 2 - Rail // 2, WidthValue, Rail, ColorValue)
            self.DrawRect(0, 0, Stripe, HeightValue, AccentColor)
            TextX = Stripe + Pad
            TextW = WidthValue - Stripe - Pad * 2
        elif Kind in ["indicator", "value", "number"]:
            self.DrawRect(0, HeightValue // 2 - Rail // 2, WidthValue, Rail, AccentColor)
            self.DrawRect(0, 0, Stripe, HeightValue, ColorValue)
            self.DrawRect(WidthValue - Stripe, 0, Stripe, HeightValue, CapColor)
            TextX = Stripe + Pad
            TextW = WidthValue - Stripe * 2 - Pad * 2
        elif Kind in ["stack", "tile"]:
            self.DrawRect(0, 0, WidthValue, HeightValue, ColorValue)
            self.DrawRect(0, 0, Stripe, HeightValue, AccentColor)
            self.DrawRect(WidthValue - Stripe, 0, Stripe, HeightValue, CapColor)
            TextX = Stripe + Pad
            TextW = WidthValue - Stripe * 2 - Pad * 2
        else:
            self.DrawRect(0, 0, WidthValue, HeightValue, ColorValue)
        if self.Type in ["selected"] or self.State in ["selected", "active"]:
            self.DrawRect(0, 0, Stripe, HeightValue, "#FFFFFF")

        Align = "center"
        TextW = max(10, TextW)
        self.Label.SetFont(self.FontFamily, self.FontSize, self.Weight)
        self.Label.SetColor(TextColor)
        self.Label.SetAlign(Align)
        if getattr(self, "ManualLabelBounds", False):
            TextX, TextY, TextW, TextH = getattr(self.Label, "Bounds", (TextX, TextY, TextW, TextH))
        else:
            self.Label.SetBounds(TextX, TextY, TextW, TextH)
        if not getattr(self, "SuppressLabel", False):
            self.Label.Draw(self, TextX, TextY, TextW, TextH)

    # =========================================================================
    # ІНДИКАТОР / ЛЕЙБЛ (INDICATOR / LABEL)
    # =========================================================================
    def InitLabel(self, **Args):
        Text = Args.get("text", Args.get("Text", ""))
        Prefix = Args.get("prefix", Args.get("Prefix", ""))
        Suffix = Args.get("suffix", Args.get("Suffix", ""))
        Color = Args.get("color", Args.get("Color", Args.get("ColorHexStr", None)))
        Align = Args.get("align", Args.get("Align", "center"))
        FontFamily = Args.get("fontFamily", Args.get("FontFamily", DefaultFontFamily))
        FontSize = Args.get("fontSize", Args.get("FontSize", self.FontSize))
        Weight = Args.get("weight", Args.get("Weight", Args.get("fontWeight", Args.get("FontWeight", "normal"))))
        Mode = Args.get("mode", Args.get("Mode", "label"))

        self.Type = Normalize(Mode) or "label"
        self.Status = "normal"
        self.Value = None
        self.Text = str(Text)
        self.Prefix = str(Prefix or "")
        self.Suffix = str(Suffix or "")
        self.Color = Color or "#FFFFFF"
        self.FontFamily = str(FontFamily or DefaultFontFamily)
        self.FontSize = int(FontSize or self.FontSize)
        self.Weight = NormalizeFontWeight(Weight)
        self.Align = str(Align or "center")
        self.Blink = False
        self.BlinkState = True
        self.Bounds = (0, 0, self.Width, self.Height)
        self.ApplyText()
        self.ApplyStyle()

    def InitIndicator(self, **Args):
        Text = Args.get("text", Args.get("Text", ""))
        Color = Args.get("color", Args.get("Color", Args.get("ColorHexStr", None)))
        Type = Args.get("type", Args.get("Type", "label"))
        Shape = Args.get("shape", Args.get("Shape", None))
        Status = Args.get("status", Args.get("Status", Args.get("state", Args.get("State", "normal"))))
        Value = Args.get("value", Args.get("Value", None))
        Blink = Args.get("blink", Args.get("Blink", False))
        BlinkRate = Args.get("blinkRate", Args.get("BlinkRate", 650))
        
        TypeKey = Normalize(Type) or "label"
        ShapeTypes = ["rect-left", "rect-right", "pill-left", "pill-right", "soft-left", "soft-right"]
        self.Shape = Normalize(Shape) or (TypeKey if TypeKey in ShapeTypes else "rect")
        self.Type = TypeKey if TypeKey not in ShapeTypes else self.Shape
        self.Status = Normalize(Status) or "normal"
        self.Value = Value
        self.Text = str(Value if Value is not None else Text)
        self.Color = Color or self.StatusColor()
        self.AccentColor = RandomButtonColor("buttons", f"{self.Shape}.pulse")
        self.Blink = bool(Blink)
        self.BlinkState = True
        self.PulsePhase = 0
        self.FontFamily = Args.get("fontFamily", Args.get("FontFamily", DefaultFontFamily))
        self.FontSize = int(Args.get("fontSize", Args.get("FontSize", self.FontSize)))
        self.Weight = NormalizeFontWeight(Args.get("weight", Args.get("Weight", Args.get("fontWeight", Args.get("FontWeight", DefaultFontWeight)))))

        if hasattr(self.widget, "setText"):
            self.widget.setText("")
        self.widget.paintEvent = self.paintEvent
        SetStyle(self.widget, "background-color: transparent; border: none;")
        if self.Blink:
            self.ConnectBlink(BlinkRate)

        self.Update()

    def SetValue(self, Value):
        self.Value = Value
        self.SetText(Value)

    def SetStatus(self, Status):
        self.Status = Normalize(Status) or "normal"
        self.Color = self.StatusColor()
        self.ApplyStyle()

    def StatusColor(self):
        if self.Status in ["ok", "online", "ready", "normal"]:
            return Palette.Buttons[2]
        if self.Status in ["warn", "warning", "yellow"]:
            return Palette.YellowAlert[0]
        if self.Status in ["error", "critical", "red", "alert"]:
            return Palette.RedAlert[0]
        if self.Status in ["off", "offline", "disabled"]:
            return "#333333"
        return PickColor(None, self.Text)

    def ConnectBlink(self, BlinkRate):
        Timer = LCARS.Chronometer
        if not Timer:
            self.Blink = False
            return

        self.BlinkTimer = Timer(self.widget)
        Timeout = getattr(self.BlinkTimer, "timeout", None)
        Connect = getattr(Timeout, "connect", None)
        Start = getattr(self.BlinkTimer, "start", None)

        if not Connect or not Start:
            self.Blink = False
            return

        Connect(self.ToggleBlink)
        Start(BlinkRate)

    def ToggleBlink(self):
        self.BlinkState = not self.BlinkState
        self.PulsePhase = (self.PulsePhase + 1) % 4
        self.Update()

    def IndicatorColor(self):
        if not self.BlinkState:
            return "#1A1A1A"
        if self.PulsePhase in [1, 2]:
            return self.Color
        return self.AccentColor if hasattr(self, "AccentColor") else RandomButtonColor("buttons", self.Shape)

    def RenderIndicator(self):
        self.ClearCommands()
        WidthValue = self.widget.width() if hasattr(self.widget, "width") else int(self.Width)
        HeightValue = self.widget.height() if hasattr(self.widget, "height") else int(self.Height)
        ColorValue = self.IndicatorColor()
        Shape = Normalize(getattr(self, "Shape", "rect-left")) or "rect-left"
        if Shape == "rect-left":
            self.DrawRect(0, 0, WidthValue, HeightValue, ColorValue)
        elif Shape == "rect-right":
            self.DrawRect(0, 0, WidthValue, HeightValue, ColorValue)
        elif Shape == "pill-left":
            self.DrawLeftCap(0, 0, WidthValue, HeightValue, ColorValue)
        elif Shape == "pill-right":
            self.DrawRightCap(0, 0, WidthValue, HeightValue, ColorValue)
        elif Shape == "soft-left":
            self.DrawSoftLeft(0, 0, WidthValue, HeightValue, ColorValue)
        elif Shape == "soft-right":
            self.DrawSoftRight(0, 0, WidthValue, HeightValue, ColorValue)
        if str(getattr(self, "Text", "") or "").strip():
            TextColor = ContrastColor(ColorValue)
            Size = AdaptiveTextSize(self.Text.upper(), WidthValue, HeightValue, self.FontSize)
            self.DrawText(self.Text.upper(), 0, 0, WidthValue, HeightValue, Size, "center", TextColor, self.FontFamily)

    def ApplyIndicatorStyle(self):
        ColorValue = self.Color if self.BlinkState else "#1A1A1A"
        Background = ColorValue
        Border = ""
        Padding = "2px 14px"
        Radius = "0px"
        WidthValue = self.widget.width() if hasattr(self.widget, "width") else int(self.Width)
        HeightValue = self.widget.height() if hasattr(self.widget, "height") else int(self.Height)
        Shape = Normalize(getattr(self, "Shape", "rect")) or "rect"

        if Shape == "pill":
            Radius = f"{max(2, HeightValue // 2)}px"
        elif Shape == "pill-left":
            R = max(2, HeightValue // 2)
            Radius = f"{R}px 0px 0px {R}px"
        elif Shape == "pill-right":
            R = max(2, HeightValue // 2)
            Radius = f"0px {R}px {R}px 0px"
        elif Shape == "soft":
            Radius = f"{max(4, min(HeightValue // 4, WidthValue // 10))}px"
        elif Shape == "soft-left":
            R = max(4, min(HeightValue // 4, WidthValue // 10))
            Radius = f"{R}px 0px 0px {R}px"
        elif Shape == "soft-right":
            R = max(4, min(HeightValue // 4, WidthValue // 10))
            Radius = f"0px {R}px {R}px 0px"

        if self.Type == "status":
            ColorValue = ContrastColor(ColorValue)
            Padding = "4px 14px"
        elif self.Type == "console":
            Background = "#020202"
            Padding = "15px"
        elif self.Type == "alert":
            Background = ColorValue
            ColorValue = ContrastColor(ColorValue)
        elif self.Type == "value":
            Padding = "2px 0px"
        elif self.Type == "title":
            Padding = "4px 0px"
            ColorValue = self.Color

        SetName(self.widget, "LCARSIndicator")
        SetStyle(
            self.widget,
            "#LCARSIndicator { "
            f"background-color: {Background}; color: {ColorValue}; "
            f"{FontStyle(AdaptiveTextSize(self.Text, WidthValue, HeightValue, self.FontSize), self.Weight)} {Border} padding: {Padding}; "
            f"font-family: '{getattr(self, 'FontFamily', DefaultFontFamily)}', 'Segoe UI', Arial; "
            f"text-align: {getattr(self, 'Align', 'center')}; "
            "text-transform: uppercase; letter-spacing: 0px; "
            f"border-radius: {Radius}; "
            "}",
        )

    def ApplyLabelStyle(self):
        WidthValue = self.widget.width() if hasattr(self.widget, "width") else int(self.Width)
        HeightValue = self.widget.height() if hasattr(self.widget, "height") else int(self.Height)
        ColorValue = getattr(self, "Color", "#ffffff") or "#ffffff"
        TextValue = str(getattr(self, "Text", "") or "")
        SetName(self.widget, "LCARSLabel")
        SetStyle(
            self.widget,
            "#LCARSLabel { "
            "background-color: transparent; border: none; "
            f"color: {ColorValue}; "
            f"{FontStyle(AdaptiveTextSize(TextValue, WidthValue, HeightValue, self.FontSize), self.Weight)} "
            f"font-family: '{getattr(self, 'FontFamily', DefaultFontFamily)}', 'Segoe UI', Arial; "
            f"text-align: {getattr(self, 'Align', 'center')}; "
            "text-transform: uppercase; letter-spacing: 0px; padding: 0px; "
            "}",
        )

    # =========================================================================
    # ЛІКОТЬ (ELBOW)
    # =========================================================================
    def InitElbow(self, **Args):
        Direction = Args.get("direction", Args.get("Direction", "top-left"))
        Text = Args.get("text", Args.get("Text", ""))
        Color = Args.get("color", Args.get("Color", Args.get("ColorHexStr", None)))
        Mode = Args.get("mode", Args.get("Mode", Args.get("FrameMode", Args.get("frameMode", "vertical-thick"))))
        Thick = Args.get("thick", Args.get("Thick", FrameThick))
        Thin = Args.get("thin", Args.get("Thin", FrameThin))
        Radius = Args.get("radius", Args.get("Radius", FrameRadius))
        
        self.Direction = Normalize(Direction) or "top-left"
        self.FrameMode = Normalize(Mode) or "vertical-thick"
        self.FrameThick = max(2, int(Thick))
        self.FrameThin = max(2, int(Thin))
        self.Radius = max(self.FrameThick, int(Radius))
        self.Text = str(Text)
        self.Color = PickColor(Color, self.Direction)
        
        if hasattr(self.widget, "setMinimumSize"):
            self.widget.setMinimumSize(120, 60)
        if hasattr(self.widget, "PaintCallback"):
            self.widget.PaintCallback = self.paintEvent
        else:
            self.widget.paintEvent = self.paintEvent

    def SetDirection(self, Direction):
        self.Direction = Normalize(Direction) or "top-left"
        self.Update()

    def SetFrameMode(self, Mode):
        self.FrameMode = Normalize(Mode) or "vertical-thick"
        self.Update()

    def ElbowThickness(self):
        if self.FrameMode in ["horizontal-thick", "thin-to-thick"]:
            return self.FrameThick, self.FrameThin
        return self.FrameThin, self.FrameThick

    def RenderElbow(self):
        self.ClearCommands()
        WidthValue = self.widget.width() if hasattr(self.widget, "width") else self.Width
        HeightValue = self.widget.height() if hasattr(self.widget, "height") else self.Height
        ThickH, ThickV = self.ElbowThickness()
        self.DrawElbow(
            0,
            0,
            WidthValue,
            HeightValue,
            ThickH,
            ThickV,
            self.Radius,
            self.Direction,
            self.Color,
        )
        if self.Text:
            TextColor = ContrastColor(self.Color)
            if self.Direction == "top-left":
                self.DrawText(self.Text.upper(), self.Radius + ThickV + 8, 0, max(20, WidthValue - self.Radius - ThickV - 12), ThickH, 9, "left", TextColor)
            elif self.Direction == "top-right":
                self.DrawText(self.Text.upper(), 8, 0, max(20, WidthValue - self.Radius - ThickV - 12), ThickH, 9, "right", TextColor)
            elif self.Direction == "bottom-left":
                self.DrawText(self.Text.upper(), self.Radius + ThickV + 8, HeightValue - ThickH, max(20, WidthValue - self.Radius - ThickV - 12), ThickH, 9, "left", TextColor)
            elif self.Direction == "bottom-right":
                self.DrawText(self.Text.upper(), 8, HeightValue - ThickH, max(20, WidthValue - self.Radius - ThickV - 12), ThickH, 9, "right", TextColor)

    # =========================================================================
    # БАР / СМУГА (BAR)
    # =========================================================================
    def InitBar(self, **Args):
        Text = Args.get("text", Args.get("Text", ""))
        Color = Args.get("color", Args.get("Color", Args.get("ColorHexStr", None)))
        Type = Args.get("type", Args.get("Type", "bar"))
        Height = Args.get("height", Args.get("Height", 10))
        Animated = Args.get("animated", Args.get("Animated", True))
        Speed = Args.get("speed", Args.get("Speed", 80))
        
        self.Type = Normalize(Type) or "bar"
        self.Height = int(Height)
        self.Text = str(Text)
        self.Color = PickColor(Color, self.Text or self.Type)
        self.Animated = bool(Animated)
        self.Speed = int(Speed)
        self.Phase = 0
        
        if hasattr(self.widget, "setFixedHeight"):
            self.widget.setFixedHeight(self.Height)
        if hasattr(self.widget, "PaintCallback"):
            self.widget.PaintCallback = self.paintEvent
        else:
            self.widget.paintEvent = self.paintEvent
        SetStyle(self.widget, "background-color: transparent; border: none;")
        if self.Type == "scanning" and self.Animated:
            self.ConnectAnimation()

    def ConnectAnimation(self):
        Timer = LCARS.Timer
        if not Timer:
            self.Animated = False
            return
        self.AnimationTimer = Timer(self.widget)
        Timeout = getattr(self.AnimationTimer, "timeout", None)
        Connect = getattr(Timeout, "connect", None)
        Start = getattr(self.AnimationTimer, "start", None)
        if not Connect or not Start:
            self.Animated = False
            return
        Connect(self.StepAnimation)
        Start(self.Speed)

    def StepAnimation(self):
        self.Phase = (self.Phase + 4) % 240
        self.Update()

    def RenderBar(self):
        self.ClearCommands()
        WidthValue = self.widget.width() if hasattr(self.widget, "width") else self.Width
        HeightValue = self.widget.height() if hasattr(self.widget, "height") else self.Height

        if self.Type == "scanning":
            SegmentWidth = 22
            GapValue = 6
            X = -(self.Phase % (SegmentWidth + GapValue))
            while X < WidthValue:
                self.DrawRect(X, 0, SegmentWidth, HeightValue, self.Color)
                X += SegmentWidth + GapValue
        elif self.Type == "divider":
            self.DrawRect(0, HeightValue // 2, WidthValue, max(1, HeightValue // 3), self.Color)
        elif self.Type in ["pill", "bar-pill"]:
            self.DrawPill(0, 0, WidthValue, HeightValue, self.Color)
        elif self.Type in ["soft", "bar-soft"]:
            Radius = max(4, min(HeightValue // 4, WidthValue // 10))
            self.DrawRoundedRect(0, 0, WidthValue, HeightValue, Radius, Radius, self.Color)
        elif self.Type in ["rect", "bar"]:
            self.DrawRect(0, 0, WidthValue, HeightValue, self.Color)
        elif self.Text:
            TextWidth = max(80, len(self.Text) * 10 + 24)
            SegmentWidth = max(0, (WidthValue - TextWidth) // 2)
            self.DrawRect(0, 0, SegmentWidth, HeightValue, self.Color)
            self.DrawText(self.Text.upper(), SegmentWidth, 0, TextWidth, HeightValue, 10, "center", self.Color)
            self.DrawRect(SegmentWidth + TextWidth, 0, SegmentWidth, HeightValue, self.Color)
        else:
            self.DrawRect(0, 0, WidthValue, HeightValue, self.Color)

    # =========================================================================
    # ПРИМІТИВ (PRIMITIVE / VECTOR SHAPE)
    # =========================================================================
    def InitPrimitive(self, **Args):
        Shape = Args.get("shape", Args.get("Shape", "surface"))
        Text = Args.get("text", Args.get("Text", ""))
        Color = Args.get("color", Args.get("Color", Args.get("ColorHexStr", None)))
        Points = Args.get("points", Args.get("Points", None))
        Align = Args.get("align", Args.get("Align", Args.get("alignment", Args.get("Alignment", "center"))))
        Thickness = Args.get("thickness", Args.get("Thickness", 4))
        Radius = Args.get("radius", Args.get("Radius", None))
        
        self.Shape = Normalize(Shape) or "surface"
        self.Points = Points or []
        self.Color = PickColor(Color, self.Shape)
        self.Orientation = Args.get("orientation", Args.get("Orientation", "h"))
        self.Text = str(Text)
        self.Align = Normalize(Align) or "center"
        self.LineThickness = int(Thickness)
        if Radius is not None:
            self.Radius = int(Radius)

    def SetShape(self, Shape):
        self.Shape = Normalize(Shape) or "surface"
        self.Update()

    def SetPoints(self, Points):
        self.Points = Points or []
        self.Update()

    def RenderPrimitive(self):
        self.ClearCommands()
        WidthValue = self.widget.width() if hasattr(self.widget, "width") else self.Width
        HeightValue = self.widget.height() if hasattr(self.widget, "height") else self.Height

        if self.Shape in ["surface", "rect", "square"]:
            self.DrawRect(0, 0, WidthValue, HeightValue, self.Color)
            self.DrawTextIfNeeded(WidthValue, HeightValue)
        elif self.Shape == "pill":
            self.DrawPill(0, 0, WidthValue, HeightValue, self.Color)
            self.DrawTextIfNeeded(WidthValue, HeightValue)
        elif self.Shape in ["text", "symbol"]:
            self.DrawTextIfNeeded(WidthValue, HeightValue, self.Color)
        elif self.Shape == "structure":
            self.DrawStructure(WidthValue, HeightValue)
        elif self.Shape == "access-panel":
            self.DrawAccessPanel(WidthValue, HeightValue)
        elif self.Shape == "circle":
            self.DrawCircle(WidthValue // 2, HeightValue // 2, min(WidthValue, HeightValue) // 2, self.Color)
            self.DrawTextIfNeeded(WidthValue, HeightValue)
        elif self.Shape == "ellipse":
            self.DrawEllipse(0, 0, WidthValue, HeightValue, self.Color)
            self.DrawTextIfNeeded(WidthValue, HeightValue)
        elif self.Shape == "triangle":
            self.DrawPolygon([(WidthValue / 2, 0), (WidthValue, HeightValue), (0, HeightValue)], self.Color)
        elif self.Shape == "trapezoid":
            Offset = WidthValue * 0.25
            self.DrawPolygon([(Offset, 0), (WidthValue - Offset, 0), (WidthValue, HeightValue), (0, HeightValue)], self.Color)
        elif self.Shape == "diamond":
            self.DrawPolygon(
                [(WidthValue / 2, 0), (WidthValue, HeightValue / 2), (WidthValue / 2, HeightValue), (0, HeightValue / 2)],
                self.Color,
            )
        elif self.Shape == "hexagon":
            Cut = WidthValue * 0.18
            self.DrawPolygon(
                [(Cut, 0), (WidthValue - Cut, 0), (WidthValue, HeightValue / 2), (WidthValue - Cut, HeightValue), (Cut, HeightValue), (0, HeightValue / 2)],
                self.Color,
            )
        elif self.Shape == "star":
            self.DrawPolygon(
                [
                    (WidthValue / 2, 0),
                    (WidthValue * 0.6, HeightValue * 0.4),
                    (WidthValue, HeightValue / 2),
                    (WidthValue * 0.6, HeightValue * 0.6),
                    (WidthValue / 2, HeightValue),
                    (WidthValue * 0.4, HeightValue * 0.6),
                    (0, HeightValue / 2),
                    (WidthValue * 0.4, HeightValue * 0.4),
                ],
                self.Color,
            )
        elif self.Shape == "polygon" and self.Points:
            self.DrawPolygon(self.Points, self.Color)
        elif self.Shape == "polyline" and self.Points:
            self.DrawPolyline()
        elif self.Shape == "line":
            if str(self.Orientation).lower().startswith("h"):
                self.DrawLine(0, HeightValue // 2, WidthValue, HeightValue // 2, self.LineThickness, self.Color)
            else:
                self.DrawLine(WidthValue // 2, 0, WidthValue // 2, HeightValue, self.LineThickness, self.Color)

    def DrawTextIfNeeded(self, WidthValue, HeightValue, Color="#FFFFFF"):
        if self.Text:
            Size = AdaptiveTextSize(self.Text.upper(), WidthValue, HeightValue, self.FontSize)
            self.DrawText(self.Text.upper(), 0, 0, WidthValue, HeightValue, Size, self.Align, Color, DefaultFontFamily)

    def DrawStructure(self, WidthValue, HeightValue):
        if str(self.Orientation).lower().startswith("v"):
            self.DrawRect(0, 0, 30, HeightValue, self.Color)
        else:
            self.DrawRect(0, 0, WidthValue, 15, self.Color)
        self.DrawTextIfNeeded(WidthValue, HeightValue)

    def DrawPolyline(self):
        Index = 0
        Last = len(self.Points) - 1
        while Index < Last:
            X1, Y1 = self.Points[Index]
            X2, Y2 = self.Points[Index + 1]
            self.DrawLine(X1, Y1, X2, Y2, self.LineThickness, self.Color)
            Index += 1

    def DrawAccessPanel(self, WidthValue, HeightValue):
        self.DrawRect(0, 0, WidthValue, HeightValue, "#000000")
        self.DrawRect(0, 0, WidthValue, 60, "#FF9900")
        self.DrawText(self.Text or "STARFLEET ACCESS", 150, 0, 300, 60, 20, "center", "#000000")
        self.DrawText("ACCESS", 10, 0, 120, 60, 18, "center", "#000000")

    # =========================================================================
    # РЕНДЕРИНГ (GRAPHIC HOOKS)
    # =========================================================================
    def render(self):
        if self.CompType == "button":
            self.RenderButton()
        elif self.CompType == "indicator":
            self.RenderIndicator()
        elif self.CompType == "elbow":
            self.RenderElbow()
        elif self.CompType == "bar":
            self.RenderBar()
        elif self.CompType == "primitive":
            self.RenderPrimitive()

# Універсальний компонент тексту. Об'єднує всі типи елементів інтерфейсу.
# Псевдоніми та класи для збереження зворотної сумісності
# Універсальний компонент для створення різноманітних типів кнопок та інтерактивних елементів.
class LCARSLabel(Component):
    def __init__(
        self,
        Text="",
        Prefix="",
        Suffix="",
        FontFamily=None,
        FontSize=None,
        Weight=None,
        Color=None,
        Align="center",
        Parent=None,
        **Args,
    ):
        Args.setdefault("Text", Text)
        Args.setdefault("Prefix", Prefix)
        Args.setdefault("Suffix", Suffix)
        Args.setdefault("Align", Align)
        if FontFamily is not None:
            Args.setdefault("FontFamily", FontFamily)
        if FontSize is not None:
            Args.setdefault("FontSize", FontSize)
        if Weight is not None:
            Args.setdefault("Weight", Weight)
        if Color is not None:
            Args.setdefault("Color", Color)
        Args["ComponentType"] = "label"
        super().__init__(Parent=Parent, **Args)

    def GetText(self):
        Parts = []
        Prefix = getattr(self, "Prefix", "")
        Text = getattr(self, "Text", "")
        Suffix = getattr(self, "Suffix", "")
        if Prefix:
            Parts.append(Prefix)
        if Text:
            Parts.append(Text)
        if Suffix:
            Parts.append(Suffix)
        return " ".join(Parts)

    def Upper(self):
        return self.GetText().upper()

    def SetAffixes(self, Prefix="", Suffix=""):
        self.Prefix = str(Prefix or "")
        self.Suffix = str(Suffix or "")
        self.ApplyText()

    def SetText(self, Text):
        self.Text = str(Text or "")
        self.ApplyText()
        self.ApplyStyle()

    def SetColor(self, Color):
        self.Color = Color or "#FFFFFF"
        self.ApplyStyle()

    def SetFont(self, FontFamily=None, FontSize=None, Weight=None):
        if FontFamily:
            self.FontFamily = str(FontFamily)
        if FontSize:
            self.FontSize = int(FontSize)
        if Weight:
            self.Weight = NormalizeFontWeight(Weight)
        self.ApplyStyle()

    def SetAlign(self, Align):
        self.Align = str(Align or "center")
        self.ApplyStyle()

    def SetBounds(self, X, Y, Width, Height):
        self.Bounds = (int(X), int(Y), int(Width), int(Height))
        if hasattr(self.widget, "setGeometry"):
            self.widget.setGeometry(*self.Bounds)

    def Draw(self, GraphicObject, X, Y, Width, Height, Color=None, Align=None):
        Size = AdaptiveTextSize(self.Upper(), Width, Height, self.FontSize)
        GraphicObject.DrawText(
            self.Upper(),
            X,
            Y,
            Width,
            Height,
            Size,
            Align or self.Align,
            Color or self.Color or "#FFFFFF",
            self.FontFamily,
        )

    def GetElements(self):
        return []

    def ApplyText(self):
        if hasattr(self.widget, "setText"):
            self.widget.setText(self.Upper())


class LCARSButton(Component):
    RECT = "rect"
    PILL = "pill"
    SOFT = "soft"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

    def __init__(self, *Values, Parent=None, **Args):
        if Values:
            if isinstance(Values[0], str):
                Args.setdefault("Text", Values[0])
                if len(Values) > 1:
                    Args.setdefault("Color", Values[1])
                if len(Values) > 2:
                    Parent = Values[2]
            else:
                Parent = Values[0]
        Args["ComponentType"] = "button"
        super().__init__(Parent=Parent, **Args)
    
    # Визначення стилів кнопок за типами (з можливістю випадковості та переоприділення)
ButtonStyles = {
    "block": {
        "shape": "rect",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "rect": {
        "shape": "rect",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "soft": {
        "shape": "soft",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "rect-ind-left": {
        "shape": "rect-ind-left",
        "colorGroup": "buttons",
        "accentGroup": "panel",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "rect-ind-right": {
        "shape": "rect-ind-right",
        "colorGroup": "buttons",
        "accentGroup": "panel",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "soft-ind-left": {
        "shape": "soft-ind-left",
        "colorGroup": "buttons",
        "accentGroup": "panel",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "soft-ind-right": {
        "shape": "soft-ind-right",
        "colorGroup": "buttons",
        "accentGroup": "panel",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "pill": {
        "shape": "pill",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "pill-left": {
        "shape": "pill-left",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "pill-right": {
        "shape": "pill-right",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "soft-left": {
        "shape": "soft-left",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "soft-right": {
        "shape": "soft-right",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "left": {
        "shape": "left",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "right": {
        "shape": "right",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "top": {
        "shape": "top",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "bottom": {
        "shape": "bottom",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "cap-left": {
        "shape": "cap-left",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "cap-right": {
        "shape": "cap-right",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "cap-top": {
        "shape": "cap-top",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "cap-bottom": {
        "shape": "cap-bottom",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "tab-left": {
        "shape": "tab-left",
        "colorGroup": "buttons",
        "capGroup": "panel",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 10,
    },
    "tab-right": {
        "shape": "tab-right",
        "colorGroup": "buttons",
        "capGroup": "panel",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 10,
    },
    "segmented": {
        "shape": "segmented",
        "colorGroup": "buttons",
        "accentGroup": "panel",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 10,
    },
    "access-code": {
        "shape": "access-code",
        "colorGroup": "accent",
        "capGroup": "panel",
        "accent": Palette.RedAlert[0],
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "access",
        "gap": 10,
    },
    "code": {
        "shape": "access-code",
        "colorGroup": "accent",
        "capGroup": "panel",
        "accent": Palette.RedAlert[0],
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "access",
        "gap": 10,
    },
    "authorize": {
        "shape": "authorize",
        "colorGroup": "panel",
        "accentGroup": "accent",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 10,
    },
    "confirm": {
        "shape": "authorize",
        "colorGroup": "panel",
        "accentGroup": "accent",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 10,
    },
    "long": {
        "shape": "long",
        "colorGroup": "accent",
        "accentGroup": "panel",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "status": {
        "shape": "status",
        "colorGroup": "accent",
        "accentGroup": "panel",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "stack": {
        "shape": "stack",
        "colorGroup": "buttons",
        "capGroup": "panel",
        "accentGroup": "accent",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "indicator": {
        "shape": "indicator",
        "colorGroup": "buttons",
        "accentGroup": "accent",
        "capGroup": "panel",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "number": {
        "shape": "number",
        "colorGroup": "accent",
        "accentGroup": "panel",
        "capGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "cycle": {
        "shape": "pill",
        "colorGroup": "buttons",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "selected": {
        "shape": "selected-code",
        "colorGroup": "buttons",
        "capGroup": "accent",
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "acknowledge",
        "gap": 8,
    },
    "terminate": {
        "shape": "pill",
        "color": Palette.RedAlert[0],
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "alert_red",
        "gap": 8,
    },
    "abort": {
        "shape": "right",
        "color": Palette.YellowAlert[1],
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "click",
        "gap": 8,
    },
    "alert": {
        "shape": "pill",
        "color": Palette.RedAlert[0],
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "alert_red",
        "gap": 8,
    },
    "warning": {
        "shape": "pill",
        "color": Palette.YellowAlert[0],
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "alert_yellow",
        "gap": 8,
    },
    "disabled": {
        "shape": "pill",
        "color": Palette.Neutral[1],
        "fontFamily": DefaultFontFamily,
        "fontSize": 18,
        "weight": DefaultFontWeight,
        "sound": "none",
        "gap": 8,
    },
}

# Компонент для створення різноманітних типів індикаторів, статусів та лейблів.
class LCARSIndicator(Component):
    def __init__(self, *Values, Parent=None, **Args):
        if Values:
            if isinstance(Values[0], str):
                Args.setdefault("Text", Values[0])
                if len(Values) > 1:
                    Args.setdefault("Color", Values[1])
                if len(Values) > 2:
                    Parent = Values[2]
            else:
                Parent = Values[0]
        Args["ComponentType"] = "indicator"
        super().__init__(Parent=Parent, **Args)

# Компонент для створення різноманітних типів ліктів та кутових з'єднань.
class LCARSElbow(Component):
    def __init__(self, *Values, Parent=None, **Args):
        if Values:
            if isinstance(Values[0], str):
                Args.setdefault("Direction", Values[0])
                if len(Values) > 1:
                    Args.setdefault("Color", Values[1])
                if len(Values) > 2:
                    Parent = Values[2]
            else:
                Parent = Values[0]
        Args["ComponentType"] = "elbow"
        super().__init__(Parent=Parent, **Args)

# компонент для створення різноманітних типів смуг, роздільників та декоративних елементів.
class LCARSBar(Component):
    def __init__(self, *Values, Parent=None, **Args):
        if Values:
            if isinstance(Values[0], str):
                Args.setdefault("Type", Values[0])
                if len(Values) > 1:
                    Args.setdefault("Color", Values[1])
                if len(Values) > 2:
                    Parent = Values[2]
            else:
                Parent = Values[0]
        Args["ComponentType"] = "bar"
        super().__init__(Parent=Parent, **Args)

# Універсальний примітив для створення векторних форм та нестандартних елементів інтерфейсу.
class Primitive(Component):
    def __init__(self, *Values, Parent=None, **Args):
        if Values:
            if isinstance(Values[0], str):
                Args.setdefault("Shape", Values[0])
                if len(Values) > 1:
                    Args.setdefault("Color", Values[1])
                if len(Values) > 2:
                    Parent = Values[2]
            else:
                Parent = Values[0]
        Args["ComponentType"] = "primitive"
        super().__init__(Parent=Parent, **Args)

# Keep the legacy module alias so old imports still resolve to this file.
LCARS.Sys.modules["lcars.base.components"] = LCARS.Sys.modules[__name__]

# DataBlock is a ready-made info tile. It should stay on top of the generic
# component layer so we do not pull Segment back into this module.
class DataBlock(Component):
    def __init__(self, Title, Value, Color, Parent=None):
        super().__init__(
            Parent=Parent,
            ComponentType="container",
            WidgetType=LCARS.Segment,
            Text=Title,
            Color=Color,
        )
        self.widget.setStyleSheet(f"background-color: rgba(0, 0, 0, 0.5); border: 2px solid {Color};")
        self.widget.setMinimumHeight(60)

        Layout = LCARS.Vertical(self.widget)
        Layout.setContentsMargins(10, 5, 10, 5)
        Layout.setSpacing(2)

        self.TitleLabel = LCARSLabel(Text=Title, Color=Color, FontSize=12, Parent=self.widget)
        self.ValueLabel = LCARSLabel(Text=str(Value), Color="#FFFFFF", FontSize=18, Weight="bold", Parent=self.widget)

        Layout.addWidget(self.TitleLabel.widget)
        Layout.addWidget(self.ValueLabel.widget)

    def SetText(self, Value):
        self.ValueLabel.SetText(str(Value))

class PillButton(LCARSButton):
    def __init__(self, *Args, **KWArgs):
        KWArgs.setdefault("Type", "pill")
        super().__init__(*Args, **KWArgs)

__all__ = [
    "Graphic", "Component", "Primitive",
    "LCARSLabel", "PillButton", "LCARSButton", "LCARSElbow",
    "LCARSIndicator", "LCARSBar", "DataBlock"
]

