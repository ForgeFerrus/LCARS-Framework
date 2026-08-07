# LCARS FRAMEWORK v0.1.0-alpha
# ◤ TITANIUM DEFAULT — Базові візуальні константи та палітра (Канон)
# ОПИС: Модуль визначає колірну схему LCARS та системні часові цикли.
# ─────────────────────────────────────────────────────────────────────────────
from typing import List, Any, Optional
from lcars.base.type import LCARS

# СИСТЕМНІ НАЛАШТУВАННЯ
AudioEnabled = True
SystemScale = 1.0
SystemState = "Normal"
MinFontSize = 14

# ВИЗНАЧЕННЯ ПАЛІТРИ LCARS (Канон)
class Palette:
    Background  = "#000000"
    Buttons = [
        "#336699", "#6699CC", "#99CCFF",
        "#D37445", "#F0B942", "#BA985D",
        "#7D8736", "#50571A", "#606060"
    ]
    Neutral = ["#606060", "#333333"]
    Panels = ["#336699", "#6699CC", "#99CCFF"]
    Accent = ["#50571A", "#BA985D", "#7D8736"]
    Green = ["#50571A", "#7D8736", "#BA985D"]
    RedAlert = ["#990000", "#CC6600", "#E63946", "#CC0000"]
    YellowAlert = ["#FF9900", "#D37445", "#F0B942", "#BA985D"]

TitanPalette = Palette

ALERT_RED = "#CC0000"
DefaultBackground = Palette.Background
DefaultFontFamily = "LCARS"
DefaultFontWeight = "normal"
FrameThick = 40
FrameThin = 20
FrameRadius = 34

CycleNormal = 5.0
CycleYellow = 3.0
CycleRed = 2.0

def ResolvePaletteGroup(Group: str = "buttons") -> List[str]:
    Key = (Group or "buttons").lower()
    State = (SystemState or "Normal").lower()
    if Key in ["neutral", "disabled", "inactive", "off"]:
        return Palette.Neutral
    if Key in ["accent", "confirm", "confirmation"]:
        return Palette.Accent
    if Key in ["red", "alert", "critical"]:
        return Palette.RedAlert
    if Key in ["yellow", "warning", "caution"]:
        return Palette.YellowAlert
    if Key == "green":
        return Palette.Green
    if Key in ["button", "buttons", "normal"]:
        if State in ["red", "alert", "critical"]:
            return Palette.RedAlert
        if State in ["yellow", "warning", "caution"]:
            return Palette.YellowAlert
        if State == "green":
            return Palette.Green
    if Key in ["panel", "panels"]:
        return Palette.Panels
    return Palette.Buttons

def RandomButtonColor(Group: str = "buttons", Seed: Optional[Any] = None) -> str:
    Palette = ResolvePaletteGroup(Group)
    if not Palette: return "#FFFFFF"

    T = CycleNormal
    if SystemState == "Yellow": T = CycleYellow
    if SystemState == "Red": T = CycleRed

    Phase = int(LCARS.TimeMod.time() / T)

    if Seed is not None and Seed != "":
        Offset = hash(str(Seed)) % len(Palette)
    else:
        Offset = LCARS.RandomInteger(0, len(Palette) - 1)

    return Palette[(Phase + Offset) % len(Palette)]

def ContrastColor(Hex: str) -> str:
    H = Hex.lstrip('#')
    if len(H) == 3: H = ''.join([c*2 for c in H])
    R, G, B = int(H[0:2], 16), int(H[2:4], 16), int(H[4:6], 16)
    Brightness = (R * 299 + G * 587 + B * 114) / 1000
    return '#FFFFFF' if Brightness < 128 else '#000000'

def NormalizeFontWeight(Weight: Any = None) -> str:
    Value = Normalize(Weight)
    if Value in ["bold", "700", "800", "900", "heavy", "black"]:
        return "bold"
    if Value in ["light", "300", "200", "thin", "normal"]:
        return "normal" if Value == "normal" else "light"
    return DefaultFontWeight

def FontStyle(Size: int = 16, Weight: str = "normal") -> str:
    Effective = max(MinFontSize, int(Size))
    ScaledSize = int(Effective * SystemScale)
    NormalizedWeight = NormalizeFontWeight(Weight)
    return f"font-size: {ScaledSize}pt; font-family: {DefaultFontFamily}; font-weight: {NormalizedWeight};"

def FontSetup():
    FontManager = LCARS.Font.Database
    if FontManager:
        BaseDir = LCARS.PathLib(__file__).resolve().parents[2]
        FontDirs = [
            BaseDir / "assets" / "fonts",
            BaseDir / "resources" / "fonts",
        ]
        for FontDir in FontDirs:
            if FontDir.exists():
                for FontFile in FontDir.glob("*.ttf"):
                    if hasattr(FontManager, 'load'):
                        FontManager.load(str(FontFile))
                    elif hasattr(FontManager, 'addApplicationFont'):
                        FontManager.addApplicationFont(str(FontFile))
                for FontFile in FontDir.glob("*.otf"):
                    if hasattr(FontManager, 'load'):
                        FontManager.load(str(FontFile))
                    elif hasattr(FontManager, 'addApplicationFont'):
                        FontManager.addApplicationFont(str(FontFile))

def Take(Args, Names, Default=None):
    for Name in Names:
        if Name in Args:
            return Args.pop(Name)
    return Default

def SetStyle(Widget, Style):
    Setter = getattr(Widget, "setStyleSheet", None)
    if Setter:
        Setter(Style)

def SetName(Widget, Name):
    Setter = getattr(Widget, "setObjectName", None)
    if Setter:
        Setter(Name)

def Widget(Element):
    WidgetVal = getattr(Element, "widget", Element)
    if callable(WidgetVal):
        return Element
    return WidgetVal

def Normalize(Value):
    return str(Value or "").lower().replace("_", "-").strip()

def PickColor(Color, Seed=""):
    if not Color:
        return RandomButtonColor("buttons", Seed)
    if str(Color).startswith("#"):
        return Color
    return RandomButtonColor(str(Color), Seed)

def SetDisplayFlag(Widget, Flag, Enabled=True):
    Setter = getattr(Widget, "set" + "Win" + "dowFlag", None)
    if Setter:
        Setter(Flag, Enabled)

class SystemTheme:
    def __init__(self):
        self.Name = "System"
        self.Palette = {}

__all__ = [
    "Palette", "TitanPalette", "ALERT_RED", "AudioEnabled",
    "DefaultFontFamily", "DefaultFontWeight", "FrameThick", "FrameThin", "FrameRadius",
    "MinFontSize", "RandomButtonColor", "ContrastColor", "FontStyle",
    "CycleNormal", "CycleYellow", "CycleRed", "FontSetup",
    "Take", "SetStyle", "SetName", "Widget", "Normalize", "PickColor",
    "ResolvePaletteGroup", "NormalizeFontWeight", "SetDisplayFlag",
    "DefaultBackground", "SystemTheme"
]
