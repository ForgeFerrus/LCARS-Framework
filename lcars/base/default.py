# LCARS FRAMEWORK TITANIUM DEFAULT — Базові візуальні константи та палітра (Канон)
# ОПИС: Модуль визначає колірну схему LCARS, графічну тему SystemTheme та системні часові цикли.
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from copy import deepcopy
from lcars.base.type import LCARS
from lcars.base.info import Version

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

    @classmethod
    def AsDict(cls) -> dict:
        return {
            "fontFamily": cls.FontFamily,
            "fontWeight": cls.FontWeight,
            "minFontSize": cls.FontSize,
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
    Disabled = ["#606060", "#333333"]
    Dark = ["#000000"]

    Normal = Buttons
    Alert = Red
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


# Профіль системної теми — єдиний головний клас візуальних і LCARS.
# Містить системну конфігурацію, базовий стиль, палітру,
# типографіку та алгоритми динамічного оформлення.
class SystemTheme(LCARS):
    Name = "LCARS Master Theme"
    ThemeId = "lcars.master"
    ThemeVersion = Version.Release
    Description = "Canonical 25th Century Theme"
    # Базова системна конфігурація.
    # Містить початкові значення, з яких створюються екземпляри теми
    # та до яких система повертається під час Reset().
    DefaultConfig = {
        "audioEnabled": AudioEnabled,
        "systemScale": SystemScale,
        "systemState": SystemState,
        "minFontSize": MinFontSize,
    }
    # Базовий візуальний стиль теми.
    # Є єдиним джерелом початкових параметрів оформлення,
    # з якого створюється поточний Style екземпляра SystemTheme.
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

    # Створення екземпляра системної теми з переданою конфігурацією
    # або з повним набором системних значень за замовчуванням.
    def __init__(self, Config: dict | None = None):
        super().__init__()
        self.Config = self.__class__.ApplyConfig(
            Config or self.__class__.BuildDefaultConfig()
        )
        self.Style = deepcopy(self.__class__.DefaultStyle)

    # Створює незалежну копію базової конфігурації теми.
    # Повертає default-значення, не змінюючи сам шаблон DefaultConfig.
    @classmethod
    def BuildDefaultConfig(cls) -> dict:
        return deepcopy(cls.DefaultConfig)

    # Застосовує передану конфігурацію до глобальних системних параметрів.
    # Відсутні параметри залишаються на значеннях системного default.
    # Метод також нормалізує типи отриманих значень.
    @classmethod
    def ApplyConfig(cls, Config: dict | None = None) -> dict:
        global AudioEnabled, SystemScale, SystemState, MinFontSize

        Current = cls.BuildDefaultConfig()

        if isinstance(Config, dict):
            Current.update(Config)

        AudioEnabled = bool(
            Current.get("audioEnabled", AudioEnabled)
        )

        SystemScale = float(
            Current.get("systemScale", SystemScale)
        )

        SystemState = str(
            Current.get("systemState", SystemState)
        )

        MinFontSize = int(
            Current.get("minFontSize", MinFontSize)
        )

        return Current

    # Застосовує нову конфігурацію до поточного екземпляра теми
    # та відновлює базовий стиль із системного шаблону DefaultStyle.
    def Apply(self, Config: dict | None = None) -> dict:
        self.Config = self.__class__.ApplyConfig(
            Config or self.Config
        )
        self.Style = deepcopy(self.__class__.DefaultStyle)
        return deepcopy(self.Config)

    # Повністю повертає тему до системних значень за замовчуванням,
    # повторно застосовуючи DefaultConfig до глобального стану системи
    # та відновлюючи початковий DefaultStyle.
    def Reset(self) -> dict:
        self.Config = self.__class__.BuildDefaultConfig()
        self.Config = self.__class__.ApplyConfig(self.Config)
        self.Style = deepcopy(self.__class__.DefaultStyle)
        return deepcopy(self.Config)

    # Визначає палітру, яка відповідає заданій групі або поточному
    # системному стану. Цей метод є внутрішнім механізмом DynamicColor()
    # і не виконує сам цикл зміни кольору.
    @staticmethod
    def ResolvePaletteGroup(Group: str = "buttons") -> list:
        Key = (Group or "buttons").lower()
        State = (SystemState or "Normal").lower()

        if Key in ["disabled", "neutral", "inactive"]:
            return Palette.Disabled

        if Key in ["dark", "stasis", "black", "off"]:
            return Palette.Dark

        if Key in ["red", "alert", "critical"]:
            return Palette.Red

        if Key in ["yellow", "warning", "caution"]:
            return Palette.Yellow

        # Якщо група не визначена, повертає палітру відповідно до поточного стану системи.
        if State in ["dark", "stasis", "black", "off"]:
            return Palette.Dark

        if State in ["red", "alert", "critical"]:
            return Palette.Red

        if State in ["yellow", "warning", "caution"]:
            return Palette.Yellow

        return Palette.Buttons

    # Головний універсальний алгоритм динамічного кольору системної теми.
    # Визначає палітру, системний цикл та поточний колір.
    # Кожна зміна кольору отримує новий випадковий інтервал:
    # Normal = 4–8 секунд, Yellow = 3–6 секунд, Red = 1–2 секунди, Dark/Stasis = 5–10 секунд.
    # Алгоритм не прив'язаний до кнопок і може використовуватися
    # будь-яким системним візуальним компонентом.
    @staticmethod
    def DynamicColor(Group: str = "buttons", Dynamic: bool = True, Key: str = "") -> str:
        ColorList = SystemTheme.ResolvePaletteGroup(Group)

        if not ColorList or not isinstance(ColorList, (list, tuple)):
            return Palette.Buttons[0] if Palette.Buttons else "#336699"

        State = (SystemState or "Normal").lower()
        GroupKey = str(Group or "buttons").lower()

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

        Time = LCARS.System.Time
        Random = getattr(LCARS.System, "Random", None)

        if not Time or not Random:
            return ColorList[0]

        Now = Time.time()

        StateData = getattr(SystemTheme, "DynamicColors", None)
        if StateData is None:
            StateData = {}
            SystemTheme.DynamicColors = StateData

        # Унікальний ключ для кожного компонента — незалежний стан циклу
        EntryKey = (GroupKey + "." + Key) if Key else GroupKey

        GroupState = StateData.get(EntryKey)

        # Перший запуск — рандомний старт і рандомний колір
        if GroupState is None:
            StartIndex = Random.randint(0, len(ColorList) - 1)
            StartOffset = Random.uniform(0.0, Cycle * 2.0)
            GroupState = {
                "index": StartIndex,
                "next": Now + StartOffset,
            }
            StateData[EntryKey] = GroupState
            return ColorList[StartIndex]

        # Час ще не настав
        if Now < GroupState["next"]:
            return ColorList[GroupState["index"] % len(ColorList)]

        # Рандомний наступний колір і рандомний інтервал
        GroupState["index"] = Random.randint(0, len(ColorList) - 1)
        GroupState["next"] = Now + Random.uniform(Cycle, Cycle * 2.0)

        return ColorList[GroupState["index"] % len(ColorList)]

    @classmethod
    def SetSystemState(cls, State: str) -> None:
        """Встановлює системний стан і скидає цикли DynamicColor.
        Використовуйте замість прямого присвоєння LCARS.System.State
        щоб SystemState в default.py і цикли кольорів синхронізувалися."""
        global SystemState
        SystemState = str(State or "Normal")
        # Скидаємо всі цикли — вони перестартують з нових таймінгів нового стану
        cls.DynamicColors.clear()


    @staticmethod
    # Контрастність кольору
    def ContrastColor(Hex: str) -> str:
        H = Hex.lstrip("#")
        if len(H) == 3:
            H = "".join([c * 2 for c in H])
        if len(H) < 6:
            return "#FFFFFF"
        R, G, B = int(H[0:2], 16), int(H[2:4], 16), int(H[4:6], 16)
        Brightness = (R * 299 + G * 587 + B * 114) / 1000
        return "#FFFFFF" if Brightness < 128 else "#000000"

    @staticmethod
    # Яскравість кольору 
    def BrightenColor(Hex: str, Factor: float = 1.35) -> str:
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

    @staticmethod
    def FontStyle(Size: int = 16, Weight: str = "normal") -> str:
        if not SystemTheme.FontInitialized:
            SystemTheme.FontSetup()
        Effective = max(MinFontSize, int(Size))
        ScaledSize = int(Effective * SystemScale)
        WeightValue = str(Weight or "").lower().replace("_", "-").strip()
        if WeightValue in ["light", "300", "200", "thin", "normal"]:
            NormalizedWeight = "normal"
        else:
            NormalizedWeight = DefaultFontWeight
        return f"font-size: {ScaledSize}pt; font-family: {DefaultFontFamily}; font-weight: {NormalizedWeight};"

    @staticmethod
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
            FontsDir / "7fonts.ru_FEC___.TTF",
        ]
        if hasattr(FontManager, "addApplicationFont"):
            for DefaultFontPath in PreferredFonts:
                if not DefaultFontPath.exists():
                    continue
                FontId = FontManager.addApplicationFont(str(DefaultFontPath))
                if FontId != -1 and hasattr(FontManager, "applicationFontFamilies"):
                    FamiliesFn = getattr(FontManager, "applicationFontFamilies")
                    FontFamily = FamiliesFn(FontId) if callable(FamiliesFn) else getattr(FontManager, "applicationFontFamilies", None)
                    if isinstance(FontFamily, (list, tuple)) and len(FontFamily) > 0:
                        DefaultFontFamily = str(FontFamily[0])
                        SystemStyle.FontFamily = DefaultFontFamily
                        SystemTheme.FontInitialized = True
                        return
                    elif isinstance(FontFamily, str) and FontFamily:
                        DefaultFontFamily = str(FontFamily)
                        SystemStyle.FontFamily = DefaultFontFamily
                        SystemTheme.FontInitialized = True
                        return
        if not FontsDir.exists():
            return
        for FontFile in list(FontsDir.glob("*.ttf")) + list(FontsDir.glob("*.otf")):
            if hasattr(FontManager, "load"):
                FontManager.load(str(FontFile))
            elif hasattr(FontManager, "addApplicationFont"):
                FontManager.addApplicationFont(str(FontFile))
        SystemTheme.FontInitialized = True

    @staticmethod
    def SetDisplayFlag(TargetWidget: any, Flag: any, Enabled: bool = True) -> None:
        Setter = getattr(TargetWidget, "setWindowFlag", None)
        if Setter and callable(Setter):
            Setter(Flag, Enabled)

DefaultStyle: dict = SystemTheme.DefaultStyle
DefaultSystemConfig: dict = SystemTheme.DefaultConfig

SystemThemeInfo: dict = {
    "name": SystemTheme.Name,
    "theme": SystemTheme.ThemeId,
    "version": SystemTheme.ThemeVersion,
    "description": SystemTheme.Description,
}

BaselineTheme: dict = {
    "meta": deepcopy(SystemThemeInfo),
    "style": deepcopy(SystemTheme.DefaultStyle),
    "config": SystemTheme.BuildDefaultConfig(),
}

DefaultConfig = SystemTheme.BuildDefaultConfig
ApplySystemConfig = SystemTheme.ApplyConfig
ResolvePaletteGroup = SystemTheme.ResolvePaletteGroup
RandomButtonColor = SystemTheme.DynamicColor
ContrastColor = SystemTheme.ContrastColor
FontStyle = SystemTheme.FontStyle
SetDisplayFlag = SystemTheme.SetDisplayFlag
