# LCARS COMPONENT & READY PHYSICAL OBJECTS (MICHAEL OKUDA VECTOR STANDARD)
# ОПИС: Сенсорне ядро (Component) та готові фізичні класи LCARS за кресленнями CorelDraw/StarTrek.
# ПРИНЦИП: Усі форми кнопок, ліктів, шин та індикаторів будуються за строгими параметрами пропорцій Окуди.
# ─────────────────────────────────────────────────────────────────────────────
# Titanium Bridge Migration: 
from typing import Any, Optional
from lcars.base.type import LCARS
from lcars.base.graphic import Graphic, Primitive, SetStyle
from lcars.base.default import (
    Palette, RandomButtonColor, DefaultFontFamily, SystemTheme
)
from lcars.core.signal import Transmission, ODN
from lcars.modules.sound import ActiveAudio
from lcars.system.alert import GetAlertSystem, AlertLevel
from lcars.base.register import registry
# =============================================================================
# 1. COMPONENT — БАЗОВИЙ СЕНСОРНИй об'єкт
class Component(Graphic):
    Type = "component"
    Form = "default"
    State = "normal"
    Default = {}
    Algorithm = ("Mount", "Refresh", "Alert", "Purge")

    NORMAL = "normal"
    DISABLED = "disabled"
    YELLOW = "yellow"
    ALERT = "alert"

    Sensitivity = "normal"
    SensorActive = False
    Transmission = None
    Channel = None

    @staticmethod
    def Normalize(Value: Any) -> str:
        if Value is None:
            return ""
        return str(Value).strip().lower()

    @staticmethod
    def Take(Source: dict, Keys: list, Default: Any = None) -> Any:
        if not isinstance(Source, dict):
            return Default
        for Key in Keys:
            if Key in Source:
                return Source[Key]
        return Default

    @staticmethod
    def ValidateIndex(Index: str) -> bool:
        if not Index:
            return True
        Re = getattr(LCARS.System, "Regex", None) or getattr(LCARS.System, "Re", None)
        if Re and hasattr(Re, "match"):
            # Підтримує як складові чіп-коди (47-01, SEC-09), так і чисті номери/індекси (01, 47, 1071)
            return bool(Re.match(r"^[A-Za-z0-9]{1,8}([-:][A-Za-z0-9]{1,8})*$", str(Index).strip()))
        return True

    @classmethod
    def NormalizeDirection(cls, Direction: Any) -> int:
        if isinstance(Direction, (int, float)):
            return int(Direction) % 360
        DirStr = cls.Normalize(Direction)
        if DirStr in ("right", "east", "0", "0deg"):
            return 0
        elif DirStr in ("bottom", "down", "south", "90", "90deg"):
            return 90
        elif DirStr in ("left", "west", "180", "180deg"):
            return 180
        elif DirStr in ("top", "up", "north", "270", "270deg"):
            return 270
        return 0

    def __init__(
        self,
        parent=None,
        Form=None,
        Properties=None,
        State=None,
        Transmission=None,
        Channel=None,
        Name=None,
        Number=None,
        Code=None,
        Direction=0,
        Sensory=True,
        Id=None,
        **Args):
        super().__init__(
            parent=parent,
            **Args
        )

        self.Id = (
            Id
            or f"{self.Type.capitalize()}_{id(self)}"
        )

        self.Form = (
            Form
            if Form is not None
            else type(self).Form
        )

        self.Properties = dict(
            Properties or {}
        )

        self.State = (
            State
            if State is not None
            else type(self).State
        )

        self.Transmission = Transmission

        self.Channel = (
            str(Channel)
            if Channel
            else f"{self.Type}.{id(self)}"
        )

        self.Name = Name

        Num = (
            str(Number)
            if Number
            else ""
        )

        if Num and not self.ValidateIndex(Num):
            Num = ""

        self.Number = Num
        self.Code = Code
        self.Direction = self.NormalizeDirection(Direction)
        self.Sensory = bool(Sensory)

        self.Algorithm = tuple(
            type(self).Algorithm
        )

        self.Power = kwargs.get("Power", True) if "kwargs" in locals() else Args.get("Power", True)
        self.Locked = kwargs.get("Locked", False) if "kwargs" in locals() else Args.get("Locked", False)
        self.IsWakeupTrigger = bool(kwargs.get("IsWakeupTrigger", False) if "kwargs" in locals() else Args.get("IsWakeupTrigger", False))
        self.DarkCycle = bool(kwargs.get("DarkCycle", False) if "kwargs" in locals() else Args.get("DarkCycle", False))

        ODN.Listen(
            "UI.AlertChanged",
            self.UpdateAlert
        )

        ODN.Listen(
            "UI.PaletteChanged",
            self.UpdateAlert
        )

        ODN.Listen(
            "UI.Power",
            self.UpdatePower
        )

        ODN.Listen(
            "UI.SecurityLock",
            self.UpdateSecurityLock
        )

    def UpdateAlert(self, SignalObj=None, **kw):
        Level = None
        if hasattr(SignalObj, "Flags"):
            Level = SignalObj.Flags.get("Level")
        elif "Level" in kw:
            Level = kw["Level"]
        elif SignalObj is not None and hasattr(SignalObj, "Data"):
            Level = SignalObj.Data
        W = getattr(self, "Widget", None)
        if W is not None and hasattr(W, "repaint"):
            W.repaint()
        return self

    def UpdatePower(self, SignalObj=None, **kw):
        PowerVal = True
        if hasattr(SignalObj, "Flags") and "Power" in SignalObj.Flags:
            PowerVal = bool(SignalObj.Flags["Power"])
        elif "Power" in kw:
            PowerVal = bool(kw["Power"])
        elif SignalObj is not None and hasattr(SignalObj, "Data") and isinstance(SignalObj.Data, bool):
            PowerVal = SignalObj.Data
        self.Power = PowerVal
        self.Sensory = bool(PowerVal and not getattr(self, "Locked", False))
        W = getattr(self, "Widget", None)
        if W is not None and hasattr(W, "repaint"):
            W.repaint()
        return self

    def UpdateSecurityLock(self, SignalObj=None, **kw):
        LockVal = False
        if hasattr(SignalObj, "Flags") and "Locked" in SignalObj.Flags:
            LockVal = bool(SignalObj.Flags["Locked"])
        elif "Locked" in kw:
            LockVal = bool(kw["Locked"])
        elif "Action" in kw:
            LockVal = str(kw["Action"]).upper() == "LOCK"
        self.Locked = LockVal
        self.Sensory = bool(getattr(self, "Power", True) and not LockVal)
        W = getattr(self, "Widget", None)
        if W is not None and hasattr(W, "repaint"):
            W.repaint()
        return self

    def PowerOn(self):
        return self.Activate(Sensory=not getattr(self, "Locked", False))

    def PowerOff(self):
        return self.Deactivate()

    def Lock(self):
        self.Locked = True
        # При блокуванні кнопки блокування/розблокування зберігають сенсорику
        if not getattr(self, "IsWakeupTrigger", False):
            self.Sensory = False
        W = getattr(self, "Widget", None)
        if W is not None and hasattr(W, "repaint"):
            W.repaint()
        return self

    def Unlock(self):
        self.Locked = False
        self.Sensory = bool(getattr(self, "Power", True))
        W = getattr(self, "Widget", None)
        if W is not None and hasattr(W, "repaint"):
            W.repaint()
        return self

    def Activate(self, Sensory: bool = True):
        self.Power = True
        self.Sensory = bool(Sensory)
        W = getattr(self, "Widget", None)
        if W is not None and hasattr(W, "repaint"):
            W.repaint()
        return self

    def Deactivate(self):
        self.Power = False
        self.Sensory = False
        W = getattr(self, "Widget", None)
        if W is not None and hasattr(W, "repaint"):
            W.repaint()
        return self

    def InductTransmission(self, Transmission):
        self.Transmission = Transmission
        return self

    def ActivateSensor(self):
        self.SensorActive = True
        return self

    def DeactivateSensor(self):
        self.SensorActive = False
        return self

    def SetSensitivity(self, Level):
        self.Sensitivity = str(Level)
        return self

    def SenseTransmit(self, Data):
        if self.SensorActive and self.Transmission:
            return self.Transmission.Emit(Data)
        return None

    def SenseReceive(self, Listener):
        if self.SensorActive and self.Transmission:
            self.Transmission.Connect(Listener)
        return self

    def Connect(self, Listener):
        return self.Clicked.Connect(Listener)

    def SetProperty(self, Name, Value):
        self.Properties[str(Name)] = Value
        return self

    def GetProperty(self, Name, Default=None):
        return self.Properties.get(str(Name), Default)

    def GetNumber(self) -> str:
        return str(getattr(self, "Number", "") or "")

    def SetNumber(self, Number: str):
        Num = str(Number).strip()
        if self.ValidateIndex(Num):
            self.Number = Num
            self.Update()
        return self

    def GetColor(self) -> str:
        StateStr = str(getattr(self, "State", "normal") or "normal").lower()
        if not getattr(self, "Power", True) or StateStr in ("off", "dark", "black"):
            return SystemTheme.DynamicColor("dark", Dynamic=False)

        # Якщо елемент в режимі періодичного затемнення (DarkCycle / Stealth / Lock)
        if getattr(self, "DarkCycle", False):
            # Періодично зникає (стає чорним кольором фону на деякий час)
            from lcars.base.default import CycleDark, CycleNormal
            Time = LCARS.System.Time
            if Time:
                Now = Time.time()
                # Вимкнений (чорний) 5.0с, нормальний (видимий) 4.0с (сумарний період 9.0с)
                Period = CycleDark + CycleNormal
                PhaseInCycle = Now % Period
                if PhaseInCycle < CycleDark:
                    return "#000000"

        if StateStr in ("disabled", "inactive") or not getattr(self, "Sensory", True):
            return SystemTheme.DynamicColor("disabled", Dynamic=False)
        if StateStr in ("alert", "red", "critical", "emergency"):
            return SystemTheme.DynamicColor("red", Dynamic=True, Key=str(id(self)))
        if StateStr in ("yellow", "warning", "caution", "standby"):
            return SystemTheme.DynamicColor("yellow", Dynamic=True, Key=str(id(self)))

        ExplicitColor = getattr(self, "Color", None)
        if ExplicitColor:
            return ExplicitColor

        return SystemTheme.DynamicColor("buttons", Dynamic=True, Key=str(id(self)))

    def SetColor(self, Color):
        self.Color = Color
        self.Update()
        return self

    def GetState(self) -> str:
        return str(getattr(self, "State", "normal") or "normal")

    def SetState(self, State: str):
        self.State = str(State or "normal").lower()
        if hasattr(self, "Update"):
            self.Update()
        return self

    def GetText(self) -> str:
        return str(getattr(self, "Text", "") or "")

    def SetText(self, Text):
        self.Text = str(Text)
        self.Update()
        return self

    def GetForm(self):
        return getattr(self, "Form", None)

    def SetFontSize(self, Size):
        self.FontSize = int(Size)
        self.Update()
        return self
    # Адаптивний розмір шрифту залежно від розміру компонента
    def GetAdaptiveFontSize(self, Width, Height, BaseSize=None):
        Base = int(BaseSize or self.FontSize or 16)
        if Width < 60 or Height < 20:
            return max(8, Base - 6)
        elif Width < 100 or Height < 28:
            return max(10, Base - 4)
        elif Width < 140 or Height < 36:
            return max(12, Base - 2)
        return Base

    # Розрахунок внутрішньої геометрії — перевизначається підкласами
    def CalculateLayout(self, Width, Height):
        return {"x": 0, "y": 0, "w": Width, "h": Height}

    # Алгоритмічний життєвий цикл базового компонента LCARS (чисті системні команди)
    def Mount(self):
        self.Update()
        return self

    def Refresh(self):
        self.Update()
        return self

    def Alert(self, Level=None):
        if hasattr(self, "UpdateAlert"):
            self.UpdateAlert(Data=Level)
        return self

    def Purge(self):
        if hasattr(self, "Destroy"):
            self.Destroy()
        return self

    # Диспетчер алгоритмів LCARS: викликає зареєстрований алгоритм за іменем
    def Dispatch(self, AlgorithmName: str, *args, **kwargs):
        CleanName = str(AlgorithmName or "").strip()
        if hasattr(self, "Algorithms") and isinstance(self.Algorithms, dict):
            alg = self.Algorithms.get(CleanName)
            if callable(alg):
                return alg(*args, **kwargs)

        alg = getattr(self, CleanName, None)
        if callable(alg):
            return alg(*args, **kwargs)
        return None

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_") or name == "widget":
            raise AttributeError(name)
        WidgetRef = getattr(self, "widget", None)
        if WidgetRef is not None and WidgetRef is not self and hasattr(WidgetRef, name):
            return getattr(WidgetRef, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
# =============================================================================
# 2. INTERACTABLE COMPONENT — БАЗОВИЙ ТИП КОМПОНЕНТІВ ДЛЯ ВЗАЄМОДІЇ
class Interactable(Component):
    Interactive = True
    Sensory = True

    # Повертає ODN-маршрут конкретної інтерактивної події.
    def InteractionPath(self, Event):
        ComponentId = getattr(self, "Id", id(self))
        return f"Component.{ComponentId}.{Event}"

    # Підключає слухача до події натискання компонента.
    def Connect(self, Listener):
        ODN.Connect(self.InteractionPath("Clicked"), Listener)
        return self

    # Відключає слухача від події натискання компонента.
    def Disconnect(self, Listener):
        ODN.Disconnect(self.InteractionPath("Clicked"), Listener)
        return self

    # Передає дані через подію натискання компонента.
    def TransmitClick(self, Data):
        return ODN.Transmit(
            self.InteractionPath("Clicked"),
            Data
        )

    # Передає дані через подію відпускання компонента.
    def TransmitRelease(self, Data):
        return ODN.Transmit(
            self.InteractionPath("Released"),
            Data
        )

    # Передає дані через подію наведення компонента.
    def TransmitHover(self, Data):
        return ODN.Transmit(
            self.InteractionPath("Hovered"),
            Data
        )

    # Квантові канали шини ODN для інтерактивних подій
    @property
    def Clicked(self) -> Transmission:
        return ODN.Channel(self.InteractionPath("Clicked"))

    @property
    def Released(self) -> Transmission:
        return ODN.Channel(self.InteractionPath("Released"))

    @property
    def Hovered(self) -> Transmission:
        return ODN.Channel(self.InteractionPath("Hovered"))

    # Канонічні аліаси під дієслова дій
    Engaged = Clicked
    Focused = Hovered
# =============================================================================
# 2. ГОТОВІ ФІЗИЧНІ ОБ'ЄКТИ LCARS ЗА КРЕСЛЕННЯМИ ОКУДИ
# =============================================================================
class LCARSButton(Interactable):
    Type = "button"
    Rect = 1
    Pill = 2
    Soft = 3
    PillHalf = 4
    SoftHalf = 5
    Elbow = 6

    DISABLED = 0
    ACTIVE = 1
    CONFIRM = 2
    YELLOW = 3
    ALERT = 4

    Algorithm = ("Engage", "Release", "Focus", "Modulate")

    def __init__(self, Text="", parent=None, Form=None, Color=None, Direction=0,
                 Number=None, Width=140, Height=36, FontSize=16, Sound="click",
                 SwapMode=True, CornerRadius=None, Handler=None, Action=None,
                 Key=None, State=1, Category="GENERAL", **Args):
        if not isinstance(Text, str) and Text is not None and parent is None:
            parent = Text
            Text = str(Args.pop("Text", "") or "")
        elif isinstance(Text, str) and not Text and "Text" in Args:
            Text = str(Args.pop("Text", "") or "")

        if isinstance(parent, str) and (parent.startswith("#") or parent.startswith("rgb")):
            Color = parent
            parent = Args.pop("Parent", None) or Args.pop("parent", None)
        elif "Parent" in Args and parent is None:
            parent = Args.pop("Parent")

        TypeStr = str(Args.pop("Type", "")).lower()
        if Form is None and TypeStr and TypeStr != "button":
            if "pill" in TypeStr:
                Form = LCARSButton.Pill
            elif "cut-left" in TypeStr or "left" in TypeStr:
                Form = LCARSButton.PillHalf
                Direction = 180
            elif "cut-right" in TypeStr or "right" in TypeStr:
                Form = LCARSButton.PillHalf
                Direction = 0
            elif "top" in TypeStr:
                Form = LCARSButton.PillHalf
                Direction = 270
            elif "bottom" in TypeStr:
                Form = LCARSButton.PillHalf
                Direction = 90
            elif "cut" in TypeStr or "soft" in TypeStr:
                Form = LCARSButton.Soft
            elif "elbow" in TypeStr:
                Form = LCARSButton.Elbow
            else:
                Form = LCARSButton.Soft
        elif Form is None:
            Form = LCARSButton.Soft

        if Number is None:
            CatCodes = {
                "SYS": "01", "BRIDGE": "00", "COMMAND": "01", "CORE": "02",
                "SCI": "03", "SENSOR": "03", "MED": "04", "BIO": "04",
                "TAC": "05", "DEF": "05", "SHIELD": "05", "ENG": "07",
                "WARP": "07", "POWER": "07", "NAV": "08", "ASTRO": "08",
                "SEC": "10", "LOCK": "10", "ACCESS": "10", "COMM": "12",
                "STORE": "14", "CHIP": "14", "DATA": "14", "SET": "16",
                "WORK": "47", "PROG": "47", "IDE": "47", "APP": "47",
                "ALERT": "99", "EMERG": "99"
            }
            Prefix = "47"
            UpperText = str(Text or "").upper()
            for K, Code in CatCodes.items():
                if K in UpperText:
                    Prefix = Code
                    break
            HashSuffix = (abs(hash(UpperText or str(id(self)))) % 900) + 100
            Number = f"{Prefix}-{HashSuffix}"

        Sensory = bool(Args.pop("Sensory", Args.pop("sensory", True)))
        super().__init__(parent=parent, Form=Form, Text=Text, Color=Color,
                         Direction=Direction, Number=Number, Width=Width,
                         Height=Height, FontSize=FontSize, Sensory=Sensory, **Args)
        self.Key = str(Key or Text or f"BTN_{id(self)}").upper()
        self.Category = str(Category or "GENERAL")
        self.Handler = Handler or Action or Args.pop("Callback", None) or Args.pop("callback", None)
        self.Sound = Sound
        self.SwapMode = SwapMode
        self.CornerRadius = CornerRadius
        self.State = State if State is not None else LCARSButton.ACTIVE

        # Алгоритмічний життєвий цикл кнопки (чисті системні дії)
        self.Algorithms = {
            "Engage": self.Engage,
            "Release": self.Release,
            "Focus": self.Focus,
            "Modulate": self.Modulate,
        }

    # Канонічні алгоритми кнопки LCARS: Engage, Release, Focus, Modulate
    def Engage(self):
        # Якщо кнопка є тригером пробудження (IsWakeupTrigger), вона спрацьовує завжди
        IsTrigger = getattr(self, "IsWakeupTrigger", False)
        if not IsTrigger and not getattr(self, "Sensory", True):
            return self

        if not IsTrigger and (self.State == LCARSButton.DISABLED or str(self.State).lower() in (
            "disabled",
            "off",
            "inactive"
        )):
            return self

        self.IsPressed = True
        self.Update()

        SoundName = self.Sound or "click"

        if self.State == LCARSButton.ALERT:
            SoundName = "alert"
        elif self.State == LCARSButton.CONFIRM:
            SoundName = "beep"

        ActiveAudio.play(SoundName)

        ODN.Transmit(
            "UI.ButtonClicked",
            Key=self.Key,
            Number=self.Number,
            Text=self.Text,
            State=self.State
        )

        self.TransmitClick(self)

        if callable(self.Handler):
            self.Handler()
        return self

    def Release(self):
        if not getattr(self, "Sensory", True):
            return self

        self.IsPressed = False
        self.Update()
        self.TransmitRelease(self)
        return self

    def Focus(self, Entering: bool):
        if not getattr(self, "Sensory", True):
            return self

        self.IsHovered = bool(Entering)
        self.Update()

        self.TransmitHover(
            {
                "event": "hover",
                "entering": bool(Entering),
                "id": self.Id,
                "key": self.Key
            }
        )
        return self

    def Modulate(self, NewState: int | str, NewText: str = None, NewColor: str = None):
        self.State = NewState
        if NewText is not None:
            self.Text = str(NewText)
        if NewColor is not None:
            self.Color = NewColor

        ActiveColor = self.GetColor()
        self.Update()
        ODN.Transmit("UI.ButtonStateChanged", Key=self.Key, State=self.State, Text=self.Text, Color=ActiveColor)
        return self

    SetState = Modulate

    def Paint(self, painter, rect):
        W = float(rect.width())
        H = float(rect.height())

        FillColor = LCARS.Color(self.GetColor())
        StateVal = self.State
        StateStr = str(StateVal or "normal").lower()
        Widget = getattr(self, "Widget", None)
        IsDisabled = (StateVal == LCARSButton.DISABLED) or StateStr in ("disabled", "off", "inactive") or (Widget is not None and hasattr(Widget, "isEnabled") and not Widget.isEnabled()) or not getattr(self, "Sensory", True)

        if IsDisabled:
            FillColor = LCARS.Color(Palette.Disabled[0])
        elif getattr(self, "IsPressed", False):
            FillColor = LCARS.Color("#FFFFFF")

        painter.setBrush(LCARS.Brush(FillColor))
        painter.setPen(LCARS.Pen(LCARS.Color("transparent")))
        Path = LCARS.PainterPath()
        FormVal = self.Form
        Dir = self.Direction

        if FormVal == self.Rect:
            Path.addRect(0, 0, W, H)
        elif FormVal == self.Pill:
            Rad = min(W, H) / 2.0
            Path.addRoundedRect(LCARS.RectF(0, 0, W, H), Rad, Rad)
        elif FormVal == self.Soft:
            Rad = float(self.CornerRadius or 6.0)
            Path.addRoundedRect(LCARS.RectF(0, 0, W, H), Rad, Rad)
        elif FormVal == self.PillHalf:
            D = str(Dir).lower()
            Rad = H / 2.0
            if D in ("0", "right", "east", 0):
                Path.moveTo(0, 0)
                Path.lineTo(max(0.0, W - Rad), 0)
                Path.arcTo(max(0.0, W - 2 * Rad), 0, 2 * Rad, H, 90, -180)
                Path.lineTo(0, H)
                Path.closeSubpath()
            elif D in ("180", "left", "west", 180):
                Path.moveTo(W, 0)
                Path.lineTo(Rad, 0)
                Path.arcTo(0, 0, 2 * Rad, H, 90, 180)
                Path.lineTo(W, H)
                Path.closeSubpath()
            elif D in ("90", "bottom", "south", 90):
                Rad = min(H * 0.5, W * 0.25, 14.0)
                Path.moveTo(0, 0)
                Path.lineTo(W, 0)
                Path.lineTo(W, H - Rad)
                Path.arcTo(W - 2 * Rad, H - 2 * Rad, 2 * Rad, 2 * Rad, 0, -90)
                Path.lineTo(Rad, H)
                Path.arcTo(0, H - 2 * Rad, 2 * Rad, 2 * Rad, 270, -90)
                Path.closeSubpath()
            elif D in ("270", "top", "north", 270):
                Rad = min(H * 0.5, W * 0.25, 14.0)
                Path.moveTo(0, H)
                Path.lineTo(0, Rad)
                Path.arcTo(0, 0, 2 * Rad, 2 * Rad, 180, -90)
                Path.lineTo(W - Rad, 0)
                Path.arcTo(W - 2 * Rad, 0, 2 * Rad, 2 * Rad, 90, -90)
                Path.lineTo(W, H)
                Path.closeSubpath()
        elif FormVal == self.SoftHalf:
            Rad = float(self.CornerRadius or min(8.0, H * 0.25, W * 0.25))
            D = str(Dir).lower()
            if D in ("0", "right", "east", 0):
                Path.moveTo(0, 0)
                Path.lineTo(W - Rad, 0)
                Path.arcTo(W - 2 * Rad, 0, 2 * Rad, 2 * Rad, 90, -90)
                Path.lineTo(W, H - Rad)
                Path.arcTo(W - 2 * Rad, H - 2 * Rad, 2 * Rad, 2 * Rad, 0, -90)
                Path.lineTo(0, H)
                Path.closeSubpath()
            elif D in ("180", "left", "west", 180):
                Path.moveTo(W, 0)
                Path.lineTo(Rad, 0)
                Path.arcTo(0, 0, 2 * Rad, 2 * Rad, 90, 90)
                Path.lineTo(0, H - Rad)
                Path.arcTo(0, H - 2 * Rad, 2 * Rad, 2 * Rad, 180, 90)
                Path.lineTo(W, H)
                Path.closeSubpath()
            else:
                Path.addRect(0, 0, W, H)
        elif FormVal == self.Elbow:
            Th = float(getattr(self, "Thickness", 24))
            Rad = float(getattr(self, "Radius", 32))
            Path = Primitive.CreateElbowPath(0, 0, W, H, Th, Rad, str(Dir))
        else:
            Path.addRect(0, 0, W, H)

        painter.drawPath(Path)

        # Якщо кнопка в темній фазі циклу (зливається з чорним полімером матриці) — текст не випромінюється
        IsDarkFill = str(FillColor.name() if hasattr(FillColor, "name") else FillColor).lower() in ("#000000", "#000")
        if IsDarkFill:
            return

        DisplayText = str(self.Text or "")
        Num = str(self.Number or "")

        if DisplayText or Num:
            FontSize = int(self.FontSize or max(16, min(22, int(H * 0.48))))
            Font = LCARS.Font(DefaultFontFamily or "LCARS", FontSize)
            painter.setFont(Font)
            if IsDisabled:
                painter.setPen(LCARS.Pen(LCARS.Color(Palette.Disabled[1] if len(Palette.Disabled) > 1 else "#333333")))
            else:
                painter.setPen(LCARS.Pen(LCARS.Color("#000000")))

            DirStr = str(Dir).lower()
            LeftPad = 10.0
            RightPad = 10.0
            if FormVal in (self.Pill, self.PillHalf):
                if DirStr in ("180", "left", "west", 180):
                    LeftPad = max(18.0, H * 0.45)
                    RightPad = 10.0
                elif DirStr in ("0", "right", "east", 0):
                    LeftPad = 10.0
                    RightPad = max(18.0, H * 0.45)
                else:
                    LeftPad = max(16.0, H * 0.35)
                    RightPad = max(16.0, H * 0.35)

            PadY = 2.0
            IsHovered = getattr(self, "IsHovered", False) or getattr(self, "IsPressed", False)
            SplitMode = bool(getattr(self, "SplitMode", False))
            SwapMode = bool(getattr(self, "SwapMode", False))

            if SplitMode and DisplayText and Num and W >= 180:
                NumBox = LCARS.RectF(LeftPad, PadY, 60.0, max(10.0, H - 2 * PadY))
                TextBox = LCARS.RectF(LeftPad + 62.0, PadY, max(10.0, W - LeftPad - RightPad - 62.0), max(10.0, H - 2 * PadY))
                ChipFont = LCARS.Font(DefaultFontFamily or "LCARS", max(12, FontSize - 2))
                painter.setFont(ChipFont)
                painter.drawText(NumBox, int(LCARS.AlignLeft | LCARS.AlignVCenter), Num)
                painter.setFont(Font)
                painter.drawText(TextBox, int(LCARS.AlignRight | LCARS.AlignVCenter), DisplayText.upper())
            else:
                if SwapMode and Num and DisplayText:
                    TargetStr = DisplayText if IsHovered else Num
                else:
                    TargetStr = DisplayText or Num

                if TargetStr:
                    RectBox = LCARS.RectF(LeftPad, PadY, max(10.0, W - LeftPad - RightPad), max(10.0, H - 2 * PadY))
                    if W < 140 or getattr(self, "Align", "") == "center":
                        AlignVal = LCARS.AlignCenter
                    elif DirStr in ("180", "left", "west", 180):
                        AlignVal = LCARS.AlignRight
                    elif DirStr in ("0", "right", "east", 0):
                        AlignVal = LCARS.AlignLeft
                    else:
                        AlignVal = LCARS.AlignRight
                    painter.drawText(RectBox, int(AlignVal | LCARS.AlignVCenter), TargetStr.upper())

# Індикатор LCARS — тонка сигнальна версія готової кнопки.
class LCARSIndicator(LCARSButton):
    Type = "indicator"
    Rect = LCARSButton.Rect
    PillHalf = LCARSButton.PillHalf
    SoftHalf = LCARSButton.SoftHalf

    Algorithm = ("Pulse", "Signal", "Alert", "Stop")
    def __init__(
        self,
        Text="",
        parent=None,
        Form=None,
        Color=None,
        Direction=0,
        Width=60,
        Height=10,
        BlinkInterval=0,
        State=LCARSButton.ACTIVE,
        **Args):
        
        Args["Number"] = Args.get("Number", "")
        Args["SwapMode"] = Args.get("SwapMode", False)
        super().__init__(
            Text=Text,
            parent=parent,
            Form=Form,
            Color=Color,
            Direction=Direction,
            Width=Width,
            Height=Height,
            State=State,
            **Args
        )
        self.BlinkPhase = True
        self.BlinkTimer = None

        if BlinkInterval and int(BlinkInterval) > 0:
            self.StartBlinking(BlinkInterval)

    # Запускає цикл блимання індикатора.
    def StartBlinking(self, IntervalMs=500):
        self.BlinkPhase = True

        if self.BlinkTimer is None:
            self.BlinkTimer = LCARS.Timer()
            self.BlinkTimer.timeout.connect(self.BlinkTick)

        self.BlinkTimer.setInterval(int(IntervalMs))
        self.BlinkTimer.start()

    # Зупиняє цикл блимання.
    def StopBlinking(self):
        self.BlinkPhase = True

        if self.BlinkTimer is not None:
            self.BlinkTimer.stop()

        Widget = getattr(self, "Widget", None)

        if Widget is not None and hasattr(Widget, "repaint"):
            Widget.repaint()

    # Чисті алгоритмічні методи LCARS
    def Pulse(self, IntervalMs=500):
        self.StartBlinking(IntervalMs)
        return self

    def Stop(self):
        self.StopBlinking()
        return self

    def Signal(self, Phase=None):
        if Phase is None:
            self.BlinkTick()
        else:
            self.BlinkPhase = bool(Phase)
            Widget = getattr(self, "Widget", None)
            if Widget is not None and hasattr(Widget, "repaint"):
                Widget.repaint()
        return self

    # Перемикає фазу сигналу.
    def BlinkTick(self):
        self.BlinkPhase = not self.BlinkPhase

        Widget = getattr(self, "Widget", None)

        if Widget is not None and hasattr(Widget, "repaint"):
            Widget.repaint()

    # Встановлює цикл блимання відповідно до системного стану.
    def Alert(self, Level=None, **kw):
        if hasattr(Level, "Flags"):
            Level = Level.Flags.get("Level")
        elif "Level" in kw:
            Level = kw["Level"]
        elif Level is not None and hasattr(Level, "Data"):
            Level = Level.Data

        LevelStr = str(Level or "GREEN").upper()

        if LevelStr in ("RED", "TACTICAL", "COMBAT", "BATTLE"):
            self.StartBlinking(200)
        elif LevelStr in ("YELLOW", "CAUTION", "STANDBY"):
            self.StartBlinking(500)
        else:
            self.StartBlinking(1200)
        return self

    OnAlertChanged = Alert

    # Малює ту саму кнопку, але без тексту та з фазою сигналу.
    def Paint(self, painter, rect):
        if not self.BlinkPhase:
            OriginalColor = getattr(self, "Color", None)
            self.Color = "#1A1A1A"
            super().Paint(painter, rect)
            self.Color = OriginalColor
        else:
            super().Paint(painter, rect)

class LCARSBar(Component):
    # Смуга LCARS: Rect (прямокутник), Pill (pill-form), Soft (скруглений)
    Type = "bar"
    Rect = 1
    Pill = 2
    Soft = 3

    def __init__(self, *args, **Args):
        Parent = None
        Color = None
        Height = 10
        Width = 100
        BarType = None
        Sensory = True

        if len(args) == 1:
            if isinstance(args[0], (int, float)):
                Height = int(args[0])
            elif isinstance(args[0], str):
                Color = args[0]
            else:
                Parent = args[0]
        elif len(args) >= 2:
            Parent = args[0]
            Color = args[1]

        Parent = Args.pop("Parent", Args.pop("parent", Parent))
        Color = Args.pop("Color", Args.pop("color", Color))
        Height = Args.pop("Height", Args.pop("height", Height))
        Width = Args.pop("Width", Args.pop("width", Width))
        BarType = Args.pop("BarType", Args.pop("barType", Args.pop("Type", None)))
        Sensory = Args.pop("Sensory", Args.pop("sensory", Sensory))

        if BarType is None:
            TypeStr = str(Args.pop("Type", "")).lower()
            if "pill" in TypeStr:
                BarType = LCARSBar.Pill
            elif "soft" in TypeStr:
                BarType = LCARSBar.Soft
            else:
                BarType = LCARSBar.Rect

        super().__init__(parent=Parent, Color=Color, Height=Height, Width=Width, Sensory=Sensory, **Args)
        self.BarType = BarType

    def Paint(self, painter, rect):
        # Рендеринг смуги: Rect, Pill, Soft
        W = float(rect.width())
        H = float(rect.height())
        FillColor = LCARS.Color(self.GetColor())
        painter.setBrush(LCARS.Brush(FillColor))
        painter.setPen(LCARS.Pen(LCARS.Color("transparent")))

        if self.BarType == self.Pill:
            Rad = min(W, H) / 2.0
            painter.drawRoundedRect(LCARS.RectF(0, 0, W, H), Rad, Rad)
        elif self.BarType == self.Soft:
            Rad = float(min(H * 0.4, 6.0))
            painter.drawRoundedRect(LCARS.RectF(0, 0, W, H), Rad, Rad)
        else:
            painter.fillRect(rect, FillColor)

# Текстовий компонент LCARS із підтримкою візуальних станів.
class LCARSLabel(Component):
    Type = "label"

    def __init__(self, *args, **Args):
        Parent = None
        Text = ""
        Color = None
        FontSize = 16
        Height = 26
        Sensory = False
        Intensity = 1.0
        Opacity = 1.0
        Visible = True
        Blink = False
        Pulse = False
        Animation = None
        AnimationSpeed = 1.0

        if len(args) == 1:
            if isinstance(args[0], str):
                Text = args[0]
            else:
                Parent = args[0]

        elif len(args) >= 2:
            if isinstance(args[0], str):
                Text = args[0]

                if isinstance(args[1], (int, float)):
                    FontSize = int(args[1])
                elif isinstance(args[1], str):
                    Color = args[1]
                else:
                    Parent = args[1]

            else:
                Parent = args[0]
                Text = str(args[1])

        Parent = Args.pop(
            "Parent",
            Args.pop("parent", Parent)
        )

        Text = Args.pop(
            "Text",
            Args.pop("text", Text)
        )

        Color = Args.pop(
            "Color",
            Args.pop("color", Color)
        )

        FontSize = Args.pop(
            "FontSize",
            Args.pop("fontSize", FontSize)
        )

        Height = Args.pop(
            "Height",
            Args.pop("height", Height)
        )

        Sensory = Args.pop(
            "Sensory",
            Args.pop("sensory", Sensory)
        )

        Intensity = Args.pop(
            "Intensity",
            Args.pop("intensity", Intensity)
        )

        Opacity = Args.pop(
            "Opacity",
            Args.pop("opacity", Opacity)
        )

        Visible = Args.pop(
            "Visible",
            Args.pop("visible", Visible)
        )

        Blink = Args.pop(
            "Blink",
            Args.pop("blink", Blink)
        )

        Pulse = Args.pop(
            "Pulse",
            Args.pop("pulse", Pulse)
        )

        Animation = Args.pop(
            "Animation",
            Args.pop("animation", Animation)
        )

        AnimationSpeed = Args.pop(
            "AnimationSpeed",
            Args.pop("animationSpeed", AnimationSpeed)
        )

        super().__init__(
            parent=Parent,
            Text=Text,
            Color=Color,
            FontSize=FontSize,
            Height=Height,
            Sensory=Sensory,
            **Args
        )

        self.Intensity = float(Intensity)
        self.Opacity = float(Opacity)
        self.Visible = bool(Visible)
        self.Blink = bool(Blink)
        self.Pulse = bool(Pulse)
        self.Animation = Animation
        self.AnimationSpeed = float(AnimationSpeed)

    # Малювання тексту з урахуванням поточного візуального стану.
    def Paint(self, painter, rect):
        if not self.Visible or not self.Text:
            return

        W = float(rect.width())
        H = float(rect.height())

        FontSize = self.GetAdaptiveFontSize(
            W,
            H,
            self.FontSize or 14
        )

        Font = LCARS.Font(
            DefaultFontFamily or "LCARS",
            FontSize
        )

        painter.setFont(Font)

        Color = LCARS.Color(
            self.GetColor()
        )

        painter.setPen(
            LCARS.Pen(Color)
        )

        AlignVal = (
            LCARS.AlignLeft |
            LCARS.AlignVCenter
            if hasattr(LCARS, "AlignLeft")
            else 0
        )

        painter.drawText(
            LCARS.RectF(0, 0, W, H),
            int(AlignVal),
            str(self.Text).upper()
        )

# LCARS Elbow — кутовий компонент зі статичним або динамічним режимом.
class LCARSElbow(Component):
    Type = "elbow"
    TopLeft = "top-left"
    TopRight = "top-right"
    BottomLeft = "bottom-left"
    BottomRight = "bottom-right"

    def __init__(self, *args, **Args):
        Parent = None
        Direction = "top-left"
        Color = None
        Text = ""
        Number = ""
        Thickness = 40
        Radius = 60
        Width = 260
        Height = 110
        FontSize = 16
        Sensory = True

        Dynamic = False
        Animation = None
        AnimationSpeed = 1.0
        Blink = False
        Pulse = False
        Cycle = None

        for Arg in args:
            if isinstance(Arg, str):
                if (
                    Arg.startswith("#")
                    or len(Arg) == 7
                    or Arg.startswith("rgb")
                ):
                    Color = Arg

                elif any(
                    D in Arg.lower()
                    for D in (
                        "top",
                        "bottom",
                        "left",
                        "right",
                        "east",
                        "west",
                        "north",
                        "south"
                    )
                ):
                    Direction = Arg

                elif not Text:
                    Text = Arg

            elif Arg is not None and not isinstance(
                Arg,
                (int, float, bool)
            ):
                Parent = Arg

        Parent = Args.pop(
            "Parent",
            Args.pop("parent", Parent)
        )

        Direction = Args.pop(
            "Direction",
            Args.pop("direction", Direction)
        )

        Color = Args.pop(
            "Color",
            Args.pop("color", Color)
        )

        Text = Args.pop(
            "Text",
            Args.pop("text", Text)
        )

        Number = Args.pop(
            "Number",
            Args.pop("number", Number)
        )

        Thickness = Args.pop(
            "Thickness",
            Args.pop("thickness", Thickness)
        )

        Radius = Args.pop(
            "Radius",
            Args.pop("radius", Radius)
        )

        Width = Args.pop(
            "Width",
            Args.pop("width", Width)
        )

        Height = Args.pop(
            "Height",
            Args.pop("height", Height)
        )

        FontSize = Args.pop(
            "FontSize",
            Args.pop("fontSize", FontSize)
        )

        Sensory = Args.pop(
            "Sensory",
            Args.pop("sensory", Sensory)
        )

        Dynamic = Args.pop(
            "Dynamic",
            Args.pop("dynamic", Dynamic)
        )

        Animation = Args.pop(
            "Animation",
            Args.pop("animation", Animation)
        )

        AnimationSpeed = Args.pop(
            "AnimationSpeed",
            Args.pop("animationSpeed", AnimationSpeed)
        )

        Blink = Args.pop(
            "Blink",
            Args.pop("blink", Blink)
        )

        Pulse = Args.pop(
            "Pulse",
            Args.pop("pulse", Pulse)
        )

        Cycle = Args.pop(
            "Cycle",
            Args.pop("cycle", Cycle)
        )

        super().__init__(
            parent=Parent,
            Form=LCARSButton.Elbow,
            Direction=Direction,
            Color=Color,
            Text=Text,
            Number=Number,
            Thickness=Thickness,
            Radius=Radius,
            Width=Width,
            Height=Height,
            FontSize=FontSize,
            Sensory=Sensory,
            **Args
        )

        self.Thickness = float(Thickness)
        self.Radius = float(Radius)

        self.Dynamic = bool(Dynamic)
        self.Animation = Animation
        self.AnimationSpeed = float(AnimationSpeed)
        self.Blink = bool(Blink)
        self.Pulse = bool(Pulse)
        self.Cycle = Cycle

    # Вмикає динамічний режим Elbow.
    def SetDynamic(
        self,
        Dynamic=True,
        Animation=None,
        Cycle=None,
        Speed=None
    ):
        self.Dynamic = bool(Dynamic)

        if Animation is not None:
            self.Animation = Animation

        if Cycle is not None:
            self.Cycle = Cycle

        if Speed is not None:
            self.AnimationSpeed = float(Speed)

        self.Update()
        return self

    # Вимикає динамічний режим Elbow.
    def StopDynamic(self):
        self.Dynamic = False
        self.Blink = False
        self.Pulse = False
        self.Cycle = None
        self.Update()
        return self

    # Встановлює режим реакції Elbow на стан.
    def SetState(self, State):
        StateValue = str(State or "normal").lower()

        self.State = StateValue

        if StateValue in (
            "disabled",
            "off",
            "inactive"
        ):
            self.StopDynamic()

        elif StateValue in (
            "yellow",
            "warning",
            "caution",
            "standby"
        ):
            self.SetDynamic(
                True,
                Cycle="yellow"
            )

        elif StateValue in (
            "alert",
            "red",
            "emergency",
            "critical"
        ):
            self.SetDynamic(
                True,
                Cycle="alert"
            )

        else:
            self.StopDynamic()

        self.Update()
        return self

    # Змінює геометричні параметри Elbow.
    def SetDimensions(
        self,
        Thickness,
        Radius
    ):
        self.Thickness = float(Thickness)
        self.Radius = float(Radius)
        self.Update()
        return self

    # Малює поточний стан Elbow.
    def Paint(self, painter, rect):
        W = float(rect.width())
        H = float(rect.height())

        Th = float(
            self.Thickness or 40
        )

        Rad = float(
            self.Radius or 60
        )

        Direction = str(
            self.Direction
        ).lower()

        FillColor = LCARS.Color(
            self.GetColor()
        )

        painter.setBrush(
            LCARS.Brush(FillColor)
        )

        painter.setPen(
            LCARS.Pen(
                LCARS.Color("transparent")
            )
        )

        Path = Primitive.CreateElbowPath(
            0,
            0,
            W,
            H,
            Th,
            Rad,
            Direction
        )

        painter.drawPath(Path)

        DisplayText = str(
            self.Text or self.Number or ""
        )

        if not DisplayText:
            return

        Font = LCARS.Font(
            DefaultFontFamily or "LCARS",
            int(self.FontSize or 16)
        )

        painter.setFont(Font)

        painter.setPen(
            LCARS.Pen(
                LCARS.Color("#000000")
            )
        )

        PadY = max(
            2.0,
            Th * 0.12
        )

        HRail = min(
            Th,
            H - 20.0
        )

        WPillar = max(
            HRail * 2.5,
            min(W * 0.35, 120.0)
        )

        if (
            "top-left" in Direction
            or Direction == "tl"
        ):
            FreeLeft = WPillar + 12.0
            FreeWidth = max(20.0, W - FreeLeft - 12.0)
            TextRect = LCARS.RectF(FreeLeft, 0.0, FreeWidth, HRail)
            AlignVal = LCARS.AlignRight | LCARS.AlignVCenter

        elif (
            "bottom-left" in Direction
            or Direction == "bl"
        ):
            FreeLeft = WPillar + 12.0
            FreeWidth = max(20.0, W - FreeLeft - 12.0)
            TextRect = LCARS.RectF(FreeLeft, H - HRail, FreeWidth, HRail)
            AlignVal = LCARS.AlignRight | LCARS.AlignVCenter

        elif (
            "top-right" in Direction
            or Direction == "tr"
        ):
            FreeWidth = max(20.0, W - WPillar - 24.0)
            TextRect = LCARS.RectF(12.0, 0.0, FreeWidth, HRail)
            AlignVal = LCARS.AlignLeft | LCARS.AlignVCenter

        else:
            FreeWidth = max(20.0, W - WPillar - 24.0)
            TextRect = LCARS.RectF(12.0, H - HRail, FreeWidth, HRail)
            AlignVal = LCARS.AlignLeft | LCARS.AlignVCenter

        painter.drawText(
            TextRect,
            int(AlignVal),
            DisplayText.upper()
        )

# =============================================================================
# РЕЄСТРАЦІЯ КОМПОНЕНТІВ LCARS
# =============================================================================
# 1. Рівень Модуля (канонічні аліаси)
Bar = LCARSBar
Label = LCARSLabel
Elbow = LCARSElbow
Button = LCARSButton
Indicator = LCARSIndicator
Normalize = Component.Normalize
Take = Component.Take
ValidateIndex = Component.ValidateIndex

# 2. Рівень Класу Component (простір імен для Component.Button, Component.Bar тощо)
Component.Bar = LCARSBar
Component.Label = LCARSLabel
Component.Elbow = LCARSElbow
Component.Button = LCARSButton
Component.Indicator = LCARSIndicator
Component.LCARSBar = LCARSBar
Component.LCARSLabel = LCARSLabel
Component.LCARSElbow = LCARSElbow
Component.LCARSButton = LCARSButton
Component.LCARSIndicator = LCARSIndicator

# 3. Рівень Системного Реєстру (ODN / Proxy resolution)
registry.Register("LCARS.Component.Button", "lcars.base.component", "LCARSButton")
registry.Register("LCARS.Component.Indicator", "lcars.base.component", "LCARSIndicator")
registry.Register("LCARS.Component.Bar", "lcars.base.component", "LCARSBar")
registry.Register("LCARS.Component.Label", "lcars.base.component", "LCARSLabel")
registry.Register("LCARS.Component.Elbow", "lcars.base.component", "LCARSElbow")

__all__ = [
    "Component",
    "Interactable",
    "Graphic",
    "Normalize",
    "Take",
    "LCARSButton",
    "Button",
    "LCARSElbow",
    "Elbow",
    "LCARSIndicator",
    "Indicator",
    "LCARSBar",
    "Bar",
    "LCARSLabel",
    "Label",
    "SetStyle",
]


