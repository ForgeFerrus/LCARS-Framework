# LCARS FRAMEWORK TITANIUM DEFAULT — Базові візуальні константи та палітра (Канон)
# ОПИС: Модуль визначає колірну схему LCARS, графічну тему SystemTheme та системні часові цикли.
# ----------------------------------------------------------------------------------------------------------------------------------
from lcars.base.type import LCARS, Type
from lcars.base.info import Version

# Канонічні типи LCARS для анотацій
Mapping = Type.Mapping
List = Type.List
String = Type.String
Integer = Type.Integer
Float = Type.Float
Boolean = Type.Boolean
Any = Type.Any

# Системні налаштування
AudioEnabled = True
SystemScale = 1.0
SystemState = "Normal"
MinFontSize = 16

# Базовий профіль стилю системи
class SystemStyle(LCARS):
    FontFamily = "LCARS"
    FontWeight = "normal"
    FontSize = 18

    def AsDict() -> Mapping:
        return {
            "fontFamily": SystemStyle.FontFamily,
            "fontWeight": SystemStyle.FontWeight,
            "minFontSize": SystemStyle.FontSize,
        }

# Визначення палітри LCARS (Канон: 3 системні режими + відключений стан)
class Palette(LCARS):
    Background = "#000000"
    Buttons = [
        "#336699", "#6699CC", "#99CCFF",
        "#D37445", "#F0B942", "#BA985D",
        "#7D8736", "#50571A", "#606060"
    ]
    Yellow = [ "#F0B942", "#FFB732",  "#BA985D", "#CC8800", "#FFFFFF", 
                "#D37445", "#CC7700", "#996600"]
    Red = ["#CC0000", "#990000", "#E63946", "#CC3300", 
           "#800000", "#B30000","#660000", "#FFFFFF"]
    Disabled = ["#313131", "#333333", "#000000"]
    YellowAlert = Yellow
    RedAlert = Red
    Alert = Red
    Normal = Buttons
    Neutral = Disabled

# Визначення констант
DefaultBackground = Palette.Background
DefaultFontFamily = SystemStyle.FontFamily
DefaultFontWeight = SystemStyle.FontWeight
FrameThick = 40
FrameThin = 20
FrameRadius = 34
CycleNormal = 4.0
CycleYellow = 3.0
CycleRed = 1.0
CycleDark = 5.0
# -----------------------------------------------------------------------------
# ЧИСТІ ФУНКЦІЇ ДИНАМІЧНОЇ ТЕМИ
# -----------------------------------------------------------------------------
# Копіювання даних
def CopyData(Target: Any) -> Any:
    CopyMod = LCARS.System.Copy
    DeepFunc = getattr(CopyMod, "deepcopy", None)
    return DeepFunc(Target) if callable(DeepFunc) else Target

# Конфігурація
def DefaultConfig() -> Mapping:
    return {
        "audioEnabled": AudioEnabled,
        "systemScale": SystemScale,
        "systemState": SystemState,
        "minFontSize": MinFontSize,
    }

# Застосування конфігурації
def ApplyConfig(Config: Mapping | None = None) -> Mapping:
    global AudioEnabled, SystemScale, SystemState, MinFontSize
    Current = DefaultConfig()
    if isinstance(Config, dict):
        Current.update(Config)
    AudioEnabled = Boolean(Current.get("audioEnabled", AudioEnabled))
    SystemScale = Float(Current.get("systemScale", SystemScale))
    SystemState = String(Current.get("systemState", SystemState))
    MinFontSize = Integer(Current.get("minFontSize", MinFontSize))
    return Current
# Визначення палітри 
def ResolvePaletteGroup(Group: String = "buttons") -> List:
    Key = (Group or "buttons").lower()
    State = (SystemState or "Normal").lower()
    if Key in ["disabled", "neutral", "inactive", "stasis", "standby", "void", "off", "sleep"]:
        return Palette.Disabled
    if Key in ["red", "alert", "critical"]:
        return Palette.Red
    if Key in ["yellow", "warning", "caution"]:
        return Palette.Yellow
    if State in ["red", "alert", "critical"]:
        return Palette.Red
    if State in ["yellow", "warning", "caution"]:
        return Palette.Yellow
    return Palette.Buttons
# Отримання динамічного кольору
def DynamicColor(Group: String = "buttons", Dynamic: Boolean = True, Key: String = "") -> String:
    ColorList = ResolvePaletteGroup(Group)
    if not ColorList or not isinstance(ColorList, (list, tuple)):
        return Palette.Buttons[0] if Palette.Buttons else "#336699"
    State = (SystemState or "Normal").lower()
    GroupKey = (Group or "buttons").lower()
    if State in ["dark", "stasis", "black", "off"] or GroupKey in ["dark", "stasis", "black", "off"]:
        Cycle = CycleDark
    elif State in ["red", "alert", "critical"] or GroupKey in ["red", "alert", "critical"]:
        Cycle = CycleRed
    elif State in ["yellow", "warning", "caution"] or GroupKey in ["yellow", "warning", "caution"]:
        Cycle = CycleYellow
    else:
        Cycle = CycleNormal
    if not Dynamic:
        return ColorList[0]
    Random = getattr(LCARS.System, "Random", None)
    if not Random:
        return ColorList[0]
    # Канонічний хронометр: вузол System.Time.Now (epoch-секунди, float)
    NowNode = LCARS.Retrieve("System.Time.Now")
    Now = NowNode() if callable(NowNode) else 0.0
    StateData = SystemTheme.DynamicColors
    EntryKey = (GroupKey + "." + Key) if Key else GroupKey
    GroupState = StateData.get(EntryKey)
    if GroupState is None:
        StartIndex = Random.randint(0, len(ColorList) - 1) if hasattr(Random, "randint") else 0
        StartOffset = Random.uniform(0.0, Cycle * 2.0) if hasattr(Random, "uniform") else 0.0
        GroupState = {
            "index": StartIndex,
            "next": Now + StartOffset,
        }
        StateData[EntryKey] = GroupState
        return ColorList[StartIndex]
    if Now < GroupState["next"]:
        return ColorList[GroupState["index"] % len(ColorList)]
    GroupState["index"] = Random.randint(0, len(ColorList) - 1) if hasattr(Random, "randint") else 0
    GroupState["next"] = Now + (Random.uniform(Cycle, Cycle * 2.0) if hasattr(Random, "uniform") else Cycle)
    return ColorList[GroupState["index"] % len(ColorList)]

# Встановлення системного стану
def SetSystemState(State: String) -> None:
    global SystemState
    SystemState = (State or "Normal")
    SystemTheme.DynamicColors.clear()
    ODNNode = LCARS.Retrieve("Core.ODN")
    if ODNNode and hasattr(ODNNode, "Transmit"):
        ODNNode.Transmit("UI.AlertChanged", State=SystemState)

    from lcars.modules.sound import ActiveAudio
    LowState = SystemState.lower()
    if LowState in ("red", "alert", "critical"):
        ActiveAudio.StartAlertLoop("red")
    elif LowState in ("yellow", "warning", "caution"):
        ActiveAudio.StartAlertLoop("yellow")
    elif LowState in ("normal", "green"):
        ActiveAudio.StopAlertLoop()
        ActiveAudio.PlayAudioClip("ack")
    else:
        ActiveAudio.StopAlertLoop()
# Отримання контрасту
def ContrastColor(Hex: String) -> String:
    H = Hex.lstrip("#")
    if len(H) == 3:
        H = "".join([c * 2 for c in H])
    if len(H) < 6:
        return "#FFFFFF"
    R, G, B = int(H[0:2], 16), int(H[2:4], 16), int(H[4:6], 16)
    Brightness = (R * 299 + G * 587 + B * 114) / 1000
    return "#FFFFFF" if Brightness < 128 else "#000000"
# Збільшення яскравості кольору
def BrightenColor(Hex: String, Factor: Float = 1.35) -> String:
    H = Hex.lstrip("#")
    if len(H) == 3:
        H = "".join([c * 2 for c in H])
    if len(H) < 6:
        return Hex
    R, G, B = int(H[0:2], 16), int(H[2:4], 16), int(H[4:6], 16)
    R = min(255, int(R * Factor))
    G = min(255, int(G * Factor))
    B = min(255, int(B * Factor))
    return f"#{R:02X}{G:02X}{B:02X}"
# Ініціалізація шрифтів
def FontSetup() -> None:
    global DefaultFontFamily
    if SystemTheme.FontInitialized:
        return
    FontManager = getattr(LCARS, "FontDatabase", None)
    if not FontManager:
        return
    Path = LCARS.System.Path
    if not Path:
        return
    BaseDir = Path(__file__).resolve().parents[2]
    FontsDir = BaseDir / "lcars" / "fonts"
    PreferredFonts = [
        FontsDir / "lcars.ttf",
        FontsDir / "Roddenberry.ttf",
    ]
    if hasattr(FontManager, "addApplicationFont"):
        for DefaultFontPath in PreferredFonts:
            if not DefaultFontPath.exists():
                continue
            FontId = FontManager.addApplicationFont(String(DefaultFontPath))
            if FontId != -1 and hasattr(FontManager, "applicationFontFamilies"):
                FamiliesFn = getattr(FontManager, "applicationFontFamilies")
                FontFamily = FamiliesFn(FontId) if callable(FamiliesFn) else getattr(FontManager, "applicationFontFamilies", None)
                if isinstance(FontFamily, (list, tuple)) and len(FontFamily) > 0:
                    DefaultFontFamily = (FontFamily[0])
                    SystemStyle.FontFamily = DefaultFontFamily
                    SystemTheme.FontInitialized = True
                    return
                elif isinstance(FontFamily, String) and FontFamily:
                    DefaultFontFamily = (FontFamily)
                    SystemStyle.FontFamily = DefaultFontFamily
                    SystemTheme.FontInitialized = True
                    return
    if not FontsDir.exists():
        return
    for FontFile in list(FontsDir.glob("*.ttf")) + list(FontsDir.glob("*.otf")):
        if hasattr(FontManager, "load"):
            FontManager.load(String(FontFile))
        elif hasattr(FontManager, "addApplicationFont"):
            FontManager.addApplicationFont(String(FontFile))
    SystemTheme.FontInitialized = True
def SetDisplayFlag(TargetWidget: Any, Flag: Any, Enabled: Boolean = True) -> None:
    Setter = getattr(TargetWidget, "setWindowFlag", None)
    if Setter and callable(Setter):
        Setter(Flag, Enabled)
# =============================================================================
# ГОЛОВНИЙ КЛАС СИСТЕМНОЇ ТЕМИ LCARS
# Профіль системної теми — єдиний головний клас візуальних і LCARS.
# Містить системну конфігурацію, базовий стиль, палітру,
# типографіку та алгоритми динамічного оформлення.
class SystemTheme(LCARS):
    Name = "LCARS Master Theme"
    ThemeId = "lcars.master"
    ThemeVersion = Version.Release
    Description = "Canonical 25th Century Theme"

    DefaultConfig = {
        "audioEnabled": AudioEnabled,
        "systemScale": SystemScale,
        "systemState": SystemState,
        "minFontSize": MinFontSize,
    }

    DefaultStyle = {
        "fontFamily": SystemStyle.FontFamily,
        "fontWeight": SystemStyle.FontWeight,
        "fontSize": SystemStyle.FontSize,
        "background": Palette.Background,
        "palette": {
            "buttons": Palette.Buttons,
            "yellow": Palette.Yellow,
            "red": Palette.Red,
            "disabled": Palette.Disabled,
        },
    }
    FontInitialized = False
    DynamicColors = {}
    # Системні операції теми
    DefaultConfig = DefaultConfig
    PaletteGroup = ResolvePaletteGroup
    DynamicColor = DynamicColor
    SetSystemState = SetSystemState
    ContrastColor = ContrastColor
    BrightenColor = BrightenColor
    FontSetup = FontSetup
    SetDisplayFlag = SetDisplayFlag
    # Застосування нової конфігурації
    def Apply(self, Config: Mapping | None = None) -> Mapping:
        TargetConfig = Config if Config else getattr(self, "Config", {})
        self.Config = ApplyConfig(TargetConfig)
        self.Style = dict(SystemTheme.DefaultStyle)
        return dict(self.Config)

    def Reset(self) -> Mapping:
        self.Config = ApplyConfig(DefaultConfig())
        self.Style = dict(SystemTheme.DefaultStyle)
        return dict(self.Config)

# Системні аліаси для зворотної сумісності
DefaultStyle = SystemTheme.DefaultStyle
DefaultSystemConfig = SystemTheme.DefaultConfig
DefaultPalette = Palette
SystemConfig = ApplyConfig
RandomButtonColor = DynamicColor

def FontStyle(Size: int = 16, Weight: str = "normal", Family: str = "LCARS") -> str:
    return f"font-family: '{Family}', 'Swiss 911 Ultra Compressed', sans-serif; font-size: {int(Size)}px; font-weight: {Weight};"

DefaultRadius = 4
ContrastColor = SystemTheme.ContrastColor