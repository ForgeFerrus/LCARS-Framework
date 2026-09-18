# LCARS FRAMEWORK TITANIUM COMPONENT (Базовий сенсорний вузол)
# ОПИС: Фундаментальний компонент інтерфейсу LCARS (Okuda Touch Standard).
# СТАНДАРТ: Titanium (Zero-Except, Pure PascalCase, Vector Surface Rendering).

from lcars.base.type import LCARS, Type
from lcars.base.graphic import Visual, Topology, Graphic, Primitive, SetStyle
from lcars.base.default import SystemTheme, Palette, DefaultBackground, DefaultFontFamily
from lcars.core.signal import ODN

Mapping = Type.Mapping
List = Type.List
String = Type.String
Integer = Type.Integer
Float = Type.Float
Boolean = Type.Boolean
Any = Type.Any

# -----------------------------------------------------------------------------
# ЧИСТІ УТИЛІТИ КОМПОНЕНТА
# -----------------------------------------------------------------------------

def NormalizeValue(Value):
    if Value is None:
        return ""
    return str(Value).strip().lower()

def ValidateIndex(Index):
    if not Index:
        return True
    Re = getattr(LCARS.System, "Regex", None) or getattr(LCARS.System, "Re", None)
    if Re and hasattr(Re, "match"):
        return bool(Re.match(r"^[A-Za-z0-9]{1,8}([-:][A-Za-z0-9]{1,8})*$", str(Index).strip()))
    return True

def NormalizeDirection(Direction):
    if isinstance(Direction, (int, float)):
        return int(Direction) % 360
    DirStr = str(Direction or "0").strip().lower()
    if DirStr in ("right", "east", "0", "0deg"): return 0
    if DirStr in ("bottom", "down", "south", "90", "90deg"): return 90
    if DirStr in ("left", "west", "180", "180deg"): return 180
    if DirStr in ("top", "up", "north", "270", "270deg"): return 270
    return str(Direction)
# =============================================================================
# ГОЛОВНИЙ КЛАС COMPONENT (СЕНСОРНИЙ ОПТИЧНИЙ ВУЗОЛ LCARS)
# Наслідує Visual (Graphic) -> SystemComponent -> LCARS.
# Це логічний вузол системи, з'єднаний через шину ODN.
# =============================================================================
class Component(Visual):
    TypeName = "LCARSComponent"
    Type = "Component"
    Form: int | str = 0
    # Сенсорний та енергетичний профіль вузла
    Power = True
    Locked = False
    Tactile = True
    Interactive = True
    SensorActive = False
    IsWakeupTrigger = False
    # Системні канали
    Channel = None
    Name = ""           # Системне ім'я для ODN
    Number = ""         # Індекс Окуди (01-NAV, 47-001)
    Text = ""           # Людський напис (ENGAGE)
    Designation = ""    # Поточне активне позначення (Text або Number)
    Title = ""          # Заголовок (для складених блоків)
    Subtext = ""        # Додатковий підпис (для SplitMode / Elbow)
    # Канонічні статуси вузла
    NORMAL = "Normal"
    DISABLED = "Disabled"
    YELLOW = "YellowAlert"
    ALERT = "RedAlert"
    STASIS = "Stasis"
    # -------------------------------------------------------------------------
    # ДИНАМІЧНИЙ СПЕКТР СВІТЛА ТА СТАНИ
    # -------------------------------------------------------------------------
    def GetState(self):
        return str(getattr(self, "State", "Normal") or "Normal")

    def SetState(self, State):
        self.State = str(State or "Normal")
        self.Refresh()
        return self

    def GetColor(self):
        StateStr = str(getattr(self, "State", "Normal") or "Normal").lower()
        if not self.Power or StateStr in ("off", "stasis", "black"):
            return Palette.Disabled[0]

        if StateStr in ("disabled", "inactive"):
            return Palette.Disabled[0]

        if getattr(self, "Interactive", True) and not self.Tactile:
            return Palette.Disabled[0]

        if StateStr in ("alert", "red", "critical", "emergency", "redalert"):
            return SystemTheme.DynamicColor("red", Dynamic=True, Key=str(id(self)))

        if StateStr in ("yellow", "warning", "caution", "yellowalert"):
            return SystemTheme.DynamicColor("yellow", Dynamic=True, Key=str(id(self)))

        ExplicitColor = getattr(self, "Spectrum", getattr(self, "Color", None))
        if ExplicitColor:
            return ExplicitColor
        return SystemTheme.DynamicColor("buttons", Dynamic=True, Key=str(id(self)))

    def SetName(self, Name: str):
        self.Name = (Name or "")
        return self

    def SetNumber(self, Number: str):
        NumStr = (Number or "").strip()
        if ValidateIndex(NumStr):
            self.Number = NumStr
            self.Refresh()
        return self

    def SetTitle(self, Title: str):
        self.Title = (Title or "")
        self.Refresh()
        return self
    # -------------------------------------------------------------------------
    # МОНТАЖ ТА СИСТЕМНА ШИНА ODN
    # -------------------------------------------------------------------------
    def Mount(self):
        ODN.Listen("UI.AlertChanged", self.UpdateAlert)
        ODN.Listen("UI.PaletteChanged", self.UpdateAlert)
        ODN.Listen("UI.Power", self.UpdatePower)
        ODN.Listen("UI.SecurityLock", self.UpdateSecurityLock)
        return self

    def Purge(self):
        ODN.Mute("UI.AlertChanged", self.UpdateAlert)
        ODN.Mute("UI.PaletteChanged", self.UpdateAlert)
        ODN.Mute("UI.Power", self.UpdatePower)
        ODN.Mute("UI.SecurityLock", self.UpdateSecurityLock)
        return self
    # Оновлення підключеної поверхні рендерингу (якщо вона існує)
    def Refresh(self):
        Target = getattr(self, "SurfaceHost", None)
        if Target is None and hasattr(self, "GetSurface") and callable(self.GetSurface):
            Target = self.GetSurface()
        if Target is None:
            Target = getattr(self, "Parent", None)
        if Target is not None and hasattr(Target, "update"):
            Target.update()
        return self
    Update = Refresh
    # Реакція на глобальні події ODN
    def UpdateAlert(self, SignalObj=None, **kwargs):
        self.Refresh()
        return self

    def UpdatePower(self, SignalObj=None, **kwargs):
        PowerVal = True
        if hasattr(SignalObj, "Flags") and "Power" in SignalObj.Flags:
            PowerVal = bool(SignalObj.Flags["Power"])
        elif "Power" in kwargs:
            PowerVal = bool(kwargs["Power"])
        elif SignalObj is not None and hasattr(SignalObj, "Data") and isinstance(SignalObj.Data, bool):
            PowerVal = SignalObj.Data
        self.Power = PowerVal
        self.Tactile = PowerVal and not self.Locked
        self.Refresh()
        return self

    def UpdateSecurityLock(self, SignalObj=None, **kwargs):
        LockVal = False
        if hasattr(SignalObj, "Flags") and "Locked" in SignalObj.Flags:
            LockVal = bool(SignalObj.Flags["Locked"])
        elif "Locked" in kwargs:
            LockVal = bool(kwargs["Locked"])
        elif "Action" in kwargs:
            LockVal = str(kwargs["Action"]).upper() == "LOCK"
        self.Locked = LockVal
        self.Tactile = self.Power and not LockVal
        self.Refresh()
        return self
    # -------------------------------------------------------------------------
    # КАНАЛИ ТА СИГНАЛИ ВЗАЄМОДІЇ (ODN CHANNELS)
    # -------------------------------------------------------------------------
    def InteractionPath(self, Event):
        return f"Component.{getattr(self, 'Id', id(self))}.{Event}"

    @property
    def Clicked(self):
        return ODN.Channel(self.InteractionPath("Clicked"))

    @property
    def Released(self):
        return ODN.Channel(self.InteractionPath("Released"))

    @property
    def Hovered(self):
        return ODN.Channel(self.InteractionPath("Hovered"))

    Engaged = Clicked
    Focused = Hovered
    # =============================================================================
    # МЕТОДИ ДЛЯ ПЕРЕДАЧІ СИГНАЛІВ (ODN TRANSPMITTERS)
    # Ці методи використовуються для відправки сигналів в мережу ODN.
    # =============================================================================
    def TransmitClick(self, Data=None):
        return ODN.Transmit(self.InteractionPath("Clicked"), Data)
    def TransmitRelease(self, Data=None):
        return ODN.Transmit(self.InteractionPath("Released"), Data)
    def TransmitHover(self, Data=None):
        return ODN.Transmit(self.InteractionPath("Hovered"), Data)
    # -------------------------------------------------------------------------
    # ЛОГІКА ТАКТИЛЬНОГО ВВОДУ (ВЕКТОРНИЙ КОНТАКТ)
    def TouchContact(self, Event=None):
        if not self.Interactive or not self.Tactile or not self.Power:
            return
        if hasattr(self, "Engage"):
            self.Engage()
        self.TransmitClick(Event)
        self.Refresh()
    
    def TouchRelease(self, Event=None):
        if not self.Interactive or not self.Tactile or not self.Power:
            return
        if hasattr(self, "Disengage"):
            self.Disengage()
        elif hasattr(self, "Release"):
            self.TransmitRelease(Event)
        self.Refresh()

    def FocusDetection(self, Entering: bool):
        if self.Interactive and self.Tactile and self.Power:
            if hasattr(self, "Focus"):
                self.Focus(Entering)
            self.TransmitHover(Entering)
            self.Refresh()

    # Диспетчер системних алгоритмів LCARS
    def Dispatch(self, AlgorithmName, *args, **kwargs):
        CleanName = str(AlgorithmName or "").strip()
        Handler = getattr(self, CleanName, None)
        if callable(Handler):
            return Handler(*args, **kwargs)
        return None
    
    def SecurityLock(self):
        self.Locked = True
        if not self.IsWakeupTrigger:
            self.Tactile = False
        self.Refresh()
        return self

    def SecurityUnlock(self):
        self.Locked = False
        self.Tactile = self.Power
        self.Refresh()
        return self
    # Синоніми для PowerControl та сумісності:
    Lock = SecurityLock
    Unlock = SecurityUnlock

    def PowerOn(self):
        self.Power = True
        self.Tactile = not self.Locked
        self.Refresh()
        return self

    def PowerOff(self):
        self.Power = False
        self.Tactile = False
        self.Refresh()
        return self

    # Канонічне отримання та створення оптичної поверхні сенсорного скла
    def GetSurface(self):
        if getattr(self, "SurfaceHost", None) is None:
            SurfaceClass = LCARS.Retrieve("Base.Interface.Surface")
            if SurfaceClass is not None and callable(SurfaceClass):
                self.SurfaceHost = SurfaceClass()
                if hasattr(self.SurfaceHost, "Initialize"):
                    self.SurfaceHost.Initialize(Optics=self)
        return getattr(self, "SurfaceHost", None)

    Surface = GetSurface

# Канонічний аліас для зворотної сумісності
Interactable = Component
# =============================================================================
# LCARSLABEL — СИСТЕМНИЙ ТЕКСТОВИЙ БЛОК LCARS (OKUDA TYPOGRAPHY)
# Відображає назви, титри та числові дані телеметрії.
# =============================================================================
class LCARSLabel(Component):
    TypeName = "LCARSLabel"
    Type = "Label"

    # Габарити текстового контейнера
    Width = 120
    Height = 24
    FontSize = 14
    Align = "left"          # left, right, center
    Uppercase = True        # Канон Окуди: весь текст у верхньому регістрі

    # Семантика
    Tactile = False
    Interactive = False
    SwapMode = False
    # -------------------------------------------------------------------------
    # СИНТЕЗ ГЕОМЕТРІЇ (ПЛОЩИНА ТЕКСТОВОГО ПОЛЯ)
    # -------------------------------------------------------------------------
    def Synthesize(self):
        # Текстовий блок сам по собі має прямокутний обмежувальний периметр (Bounding Box)
        W = float(self.Width)
        H = float(self.Height)
        self.Path = self.TraceRect(0, 0, W, H)
        self.Wavefront = None
        return self.Path
    # -------------------------------------------------------------------------
    # ТЕКСТОВІ МЕТОДИ ТА КАЛІБРУВАННЯ
    # -------------------------------------------------------------------------
    def SetText(self, Designation: str):
        TextVal = (Designation or "")
        if self.Uppercase:
            TextVal = TextVal.upper()
        self.Text = TextVal
        self.Designation = self.Text
        self.Refresh()
        return self

    def SetAlign(self, Align: str):
        self.Align = (Align or "left").lower()
        self.Refresh()
        return self

    def SetFontSize(self, Size: int):
        self.FontSize = (Size)
        self.Refresh()
        return self

    def GetDisplayText(self):
        TextVal = str(getattr(self, "Text", "") or getattr(self, "Designation", "") or "")
        return TextVal.upper() if self.Uppercase else TextVal
# =============================================================================
# LCARSBUTTON — ГОТОВИЙ ФІЗИЧНИЙ ОБ'ЄКТ КНОПКИ ЗА СТАНДАРТОМ ОКУДИ
# Наслідує Component. Повністю розкладається на примітиви.
# =============================================================================
class LCARSButton(Component):
    TypeName = "LCARSButton"
    Type = "Button"

    # --- ФОРМИ КНОПОК (Okuda Forms) ---
    RectType = 1        # Прямокутна (Standard Block)
    PillType = 2        # Пігулка (обидва кінці заокруглені)
    SoftType = 3        # Зрізані м'які кути (Soft Bevel)
    PillHalfType = 4    # Напівпігулка (круглий край з одного боку)
    SoftHalfType = 5    # Напівзріз (зріз лише з одного боку)
    ElbowType = 6       # Вигнута кутова кнопка-рамка

    # Канонічні аліаси форм
    Rect = RectType
    Pill = PillType
    Soft = SoftType
    PillHalf = PillHalfType
    SoftHalf = SoftHalfType
    Elbow = ElbowType

    # --- НАПРЯМКИ ЗРІЗУ/ЗАОКРУГЛЕННЯ (Direction) ---
    # 0 = праворуч, 180 = ліворуч, 90 = знизу, 270 = зверху
    East = 0
    West = 180
    South = 90
    North = 270

    # --- СТАНДАРТНІ ГАБАРИТИ ТА ПАРАМЕТРИ ОКУДИ ---
    Width = 140
    Height = 36
    FontSize = 14
    CornerRadius = 18.0  # Радіус пігулки (Height / 2)
    BevelSize = 6.0      # Розмір зрізу кута
    Sound = "click"
    
    # Режими роботи
    Form = 3          # За замовчуванням — класична пігулка
    Direction = 0
    SplitMode = False    # Розщеплення на дві зони (Текст + Номер)
    DarkCycle = False    # Чергове живлення
    SwapMode = True      # Заміна номера на команду при наведенні
    
    # Тактильні прапорці
    IsPressed = False
    IsHovered = False
    Handler = None
    Key = ""
    # -------------------------------------------------------------------------
    # ТАКТИЛЬНІ АЛГОРИТМИ ВЗАЄМОДІЇ
    # -------------------------------------------------------------------------
    def Engage(self):
        # Якщо живлення вимкнено і це не тригер запуску — клік ігнорується
        if not self.IsWakeupTrigger and (not self.Tactile or not self.Power):
            return self

        StateStr = (self.State or "").lower()
        if not self.IsWakeupTrigger and StateStr in ("disabled", "off", "inactive"):
            return self

        self.IsPressed = True
        self.Refresh()

        # Звуковий супровід
        AudioMod = getattr(LCARS.System, "Audio", None) or getattr(LCARS, "Audio", None)
        if AudioMod and hasattr(AudioMod, "Play"):
            AudioMod.Play(self.Sound or "click")

        # Системний імпульс по ODN
        ODN.Transmit(
            "UI.ButtonClicked",
            Key=self.Key,
            Number=self.Number,
            Text=self.Text,
            State=self.State
        )

        # Якщо призначено колбек — виконуємо
        if callable(self.Handler):
            self.Handler()

        return self

    def Disengage(self):
        if not self.Tactile and not self.IsWakeupTrigger:
            return self
        self.IsPressed = False
        self.Refresh()
        return self

    def Hover(self, Active: bool):
        if not self.Tactile and not self.IsWakeupTrigger:
            return self
        self.IsHovered = (Active)
        self.Refresh()
        return self
    # -------------------------------------------------------------------------
    # ЧИСТИЙ СИНТЕЗ ЧЕРЕЗ TOPOLOGY (БЕЗ ЗАЙВИХ ПРИМІТИВІВ)
    # Кнопка бере готову геометрію з топологічного ядра Okuda
    # -------------------------------------------------------------------------
    def Synthesize(self):
        W = float(self.Width)
        H = float(self.Height)
        R = float(getattr(self, "CornerRadius", 4.0))
        Dir = getattr(self, "Direction", 0)

        # 1. ПРЯМОКУТНИК (Rect)
        if self.Form == self.RectType:
            self.Path = self.TraceRect(0, 0, W, H)

        # 2. ПОВНА ПІГУЛКА (Pill)
        elif self.Form == self.PillType:
            self.Path = self.TraceCap(0, 0, W, H, Side="both")

        # 3. НАПІВПІГУЛКА (PillHalf)
        elif self.Form == self.PillHalfType:
            # 180 = заокруглення зліва, 0 = заокруглення справа
            SideName = "left" if Dir == 180 else "right"
            self.Path = self.TraceCap(0, 0, W, H, Side=SideName)

        # 4. М'ЯКІ ЗРІЗАНИЙ КУТИ (Soft / Rounded)
        elif self.Form in (self.SoftType, self.SoftHalfType):
            self.Path = self.TraceRounded(0, 0, W, H, Rx=R, Ry=R)

        # 5. Г-ПОДІБНИЙ КУТОВИЙ ЕЛЕМЕНТ (Elbow)
        elif self.Form == self.ElbowType:
            self.Path = self.TraceElbow(0, 0, W, H,
                                        Thickness=getattr(self, "Thickness", 24.0),
                                        Radius=getattr(self, "Radius", 20.0),
                                        Corner=getattr(self, "Corner", "top-left"))
        else:
            self.Path = self.TraceRect(0, 0, W, H)
        self.Wavefront = self.Path
        return self.Path
# =============================================================================
# LCARSINDICATOR — СВІТЛОВИЙ БЛОК-ІНДИКАТОР ПАНЕЛІ LCARS
# 3 типи геометрії (без повної таблетки): Rect, Soft, PillHalf
# =============================================================================
class LCARSIndicator(Component):
    TypeName = "LCARSIndicator"
    Type = "Indicator"

    # --- 3 ТИПИ ІНДИКАТОРА ---
    RectType = 1        # Прямокутний блок
    SoftType = 2        # Зрізані кути (фаски)
    PillHalf = 3    # Напівпігулка (напівтаблетка)

    # Стандартні компактні розміри кінцевика
    Width = 24
    Height = 36
    CornerRadius = 4.0
    Direction = 0       # 0 = праворуч (End), 180 = ліворуч (Start)
    # Винятки індикатора: чистий оптичний маркер без підписів
    Text = ""
    Number = ""
    Tactile = False
    Interactive = False
    SwapMode = False
    # Світловий стан
    Active = True
    Pulsing = True
    # -------------------------------------------------------------------------
    # СИНТЕЗ 3 ТИПІВ ГЕОМЕТРІЇ
    # -------------------------------------------------------------------------
    def Synthesize(self):
        W = float(self.Width)
        H = float(self.Height)
        R = float(getattr(self, "CornerRadius", 4.0))
        Dir = getattr(self, "Direction", 0)

        # 1. ПРЯМОКУТНИК
        if self.Form == self.RectType:
            self.Path = self.TraceRect(0, 0, W, H)

        # 2. ЗРІЗАНІ КУТИ (SOFT)
        elif self.Form == self.SoftType:
            self.Path = self.TraceRounded(0, 0, W, H, Rx=R, Ry=R)

        # 3. НАПІВПІГУЛКА (PILLHALF — заокруглений один край)
        elif self.Form == self.PillHalf:
            SideName = "left" if Dir == 180 else "right"
            self.Path = self.TraceCap(0, 0, W, H, Side=SideName)

        else:
            self.Path = self.TraceRect(0, 0, W, H)

        self.Wavefront = self.Path
        return self.Path
    # -------------------------------------------------------------------------
    # ОНОВЛЕННЯ ЗНАЧЕННЯ / ТЕЛЕМЕТРІЇ
    # -------------------------------------------------------------------------
    def DisplayText(self):
        return ""
        
    def SetValue(self, Value: float):
        self.Value = float(Value)
        if self.Value >= 90.0:
            self.State = self.ALERT
        elif self.Value >= 70.0:
            self.State = self.YELLOW
        else:
            self.State = self.NORMAL
        self.Refresh()
        return self

    def SetPulse(self, Active: bool):
        self.Pulsing = (Active)
        self.Refresh()
        return self
# =============================================================================
# LCARSBAR — ГОРИЗОНТАЛЬНА/ВЕРТИКАЛЬНА НЕСНА БАЛКА LCARS
# Каркасний рейсмус інтерфейсу. Форми: Rect, PillHalf, Soft, Segmented
# =============================================================================
class LCARSBar(Component):
    TypeName = "LCARSBar"
    Type = "Bar"

    # --- ФОРМИ БАЛКИ ---
    RectType = 1            # Суцільна прямокутна балка
    PillHalfType = 2        # Балка із заокругленим кінцем (Cap)
    SoftType = 3            # Балка зі зрізаним кутом (Soft)

    # Стандартні габарити балки
    Width = 300
    Height = 16         # Тонка стандартна товщина рельси (16-24px)
    Thickness = 16
    CornerRadius = 8.0  # Радіус для заокругленого краю
    Direction = 0       # 0 = заокруглення/зріз праворуч, 180 = ліворуч

    # Поведінка та семантика
    Tactile = False
    Interactive = False
    Align = "right"     # Текст на балці зазвичай вирівнюється по краю
    # -------------------------------------------------------------------------
    # СИНТЕЗ ЧИСТОЇ ГЕОМЕТРІЇ БАЛКИ
    # -------------------------------------------------------------------------
    def Synthesize(self):
        W = float(self.Width)
        H = float(self.Height)
        
        # Регулювання радіуса: береться CornerRadius або Radius
        R = float(getattr(self, "CornerRadius", getattr(self, "Radius", 4)))
        Rx = float(getattr(self, "RadiusX", R))
        Ry = float(getattr(self, "RadiusY", R))
        Dir = getattr(self, "Direction", 0)

        # 1. Повна напівпігулка (радіус = половині висоти балки H / 2)
        if self.Form == self.PillHalfType:
            SideName = "left" if Dir == 180 else "right"
            self.Path = self.TraceCap(0, 0, W, H, Side=SideName)

        # 2. Скруглені кути з керованим радіусом (Soft / Rounded)
        elif self.Form == self.SoftType:
            self.Path = self.TraceRounded(0, 0, W, H, Rx=Rx, Ry=Ry)

        # 3. Суцільний прямокутний рейсмус (Rect)
        else:
            self.Path = self.TraceRect(0, 0, W, H)

        self.Wavefront = self.Path
        return self.Path
    # -------------------------------------------------------------------------
    # МЕТОД РЕГУЛЮВАННЯ СКРУГЛЕННЯ
    # -------------------------------------------------------------------------
    def SetRadius(self, Radius: int, RadiusY: int | None = None):
        self.CornerRadius = Radius
        self.Radius = Radius
        self.RadiusX = Radius
        self.RadiusY = Radius if RadiusY is None else RadiusY
        self.Synthesize()
        self.Refresh()
        return self
# =============================================================================
# LCARSELBOW — КУТОВИЙ ЛІКОТЬ ТА НЕСУЧИЙ КАРКАС LCARS (OKUDA ELBOW)
# З'єднує вертикальну колону з горизонтальною шиною.
# =============================================================================
class LCARSElbow(Component):
    TypeName = "LCARSElbow"
    Type = "Elbow"

    # Кути вигину ліктя
    TopLeft = "top-left"
    BottomLeft = "bottom-left"
    TopRight = "top-right"
    BottomRight = "bottom-right"

    # Габарити несучого вузла
    Width = 240
    Height = 120
    Thickness = 24          # Товщина горизонтальної рейки
    Corner = TopLeft        # Положення кута за замовчуванням
    Radius = 24             # Зовнішній радіус скруглення кута
    PillarWidth = None      # Ширина колони (якщо None — розраховується автоматично)
    RailHeight = None       # Висота рейки (якщо None — береться Thickness)

    # Семантика ліктя
    Tactile = False         # Зазвичай каркас, але може бути сенсорним
    Interactive = False
    # -------------------------------------------------------------------------
    # СИНТЕЗ КУТОВОГО ВЕКТОРНОГО КОНТУРУ
    # -------------------------------------------------------------------------
    def Synthesize(self):
        W = float(self.Width)
        H = float(self.Height)
        Thick = float(getattr(self, "Thickness", 24))
        R = float(getattr(self, "Radius", 24))
        CornerName = str(getattr(self, "Corner", self.TopLeft)).lower()
        PillarW = float(self.PillarWidth) if self.PillarWidth is not None else None
        RailH = float(self.RailHeight) if self.RailHeight is not None else Thick

        # Викликаємо рідне трасування з Graphic
        self.Path = self.TraceElbow(
            0.0, 0.0, W, H,
            Thickness=Thick,
            Radius=R,
            Corner=CornerName,
            PillarWidth=PillarW,
            RailHeight=RailH
        )
        self.Wavefront = self.Path
        return self.Path
    # -------------------------------------------------------------------------
    # НАЛАШТУВАННЯ КУТА ТА ТОПОЛОГІЇ
    # -------------------------------------------------------------------------
    def SetCorner(self, Corner: str):
        self.Corner = (Corner).lower()
        self.Synthesize()
        self.Refresh()
        return self

    def SetDimensions(self, Thickness: int, PillarWidth: int | None = None, Radius: int | None = None):
        self.Thickness = (Thickness)
        if PillarWidth is not None:
            self.PillarWidth = (PillarWidth)
        if Radius is not None:
            self.Radius = (Radius)
        self.Synthesize()
        self.Refresh()
        return self

# =============================================================================
# РЕЄСТРАЦІЯ КОМПОНЕНТІВ LCARS
# =============================================================================
# 1. Рівень Модуля (канонічні аліаси)
Bar = LCARSBar
Label = LCARSLabel
Elbow = LCARSElbow
Button = LCARSButton
Indicator = LCARSIndicator
Normalize = NormalizeValue
Take = getattr(LCARS, "Take", lambda Collection, Count: Collection[:Count] if hasattr(Collection, "__getitem__") else Collection)
ValidateIndex = ValidateIndex

