# LCARS SYSTEM MODES - MODULES LAYER
# ПРИЗНАЧЕННЯ: Режими роботи системи LCARS
# СТАНДАРТ: Titanium Master (Enum + State Helpers)
# КЕРУВАННЯ: EngineeringController (engineering/controller.py)
from lcars.base.type import LCARS
from lcars.base.info import Version

# Отримуємо чистий Enum з LCARS.System без сторонніх імпортів
EnumBase = getattr(LCARS.System, "Enum", None)
Enum = getattr(EnumBase, "Enum", object)
Auto = getattr(EnumBase, "auto", lambda: None)

class SystemMode(Enum):
    # Режими роботи системи LCARS
    # Визначають доступні функції та обмеження інтерфейсу

    # --- Основні режими ---
    NORMAL = Auto()           # Нормальний режим — сталий стан (повернення після тривоги)
    OPERATIONAL = Auto()      # Робочий режим — стандартна робота системи
    EDIT = Auto()             # Режим редагування — модифікація UI елементів

    # --- Стан блокування та очікування ---
    LOCKED = Auto()           # Консоль заблокована — сенсори відключені, потрібен код допуску
    STASIS = Auto()           # Режим очікування / стазис — пробудження по дотику

    # --- Режими тривоги ---
    YELLOW_ALERT = Auto()     # Жовта тривога — підвищена увага
    RED_ALERT = Auto()        # Червона тривога — критична ситуація

    # --- Бойові режими ---
    BATTLE = Auto()           # Бойовий режим — повна бойова готовність

    # --- Наукові режими ---
    SCIENCE = Auto()          # Науковий режим — енергія на сенсори

    # --- Критичні режими ---
    AUTODESTRUCT = Auto()     # Автознищення — підготовка до самознищення

    # --- Сервісні режими ---
    DIAGNOSTIC = Auto()       # Діагностика — перевірка систем
    MAINTENANCE = Auto()      # Технічне обслуговування

class ModeState:
    # Стан режиму системи
    # Зберігає поточний режим та дозволені операції

    def __init__(self):
        self.Current = SystemMode.OPERATIONAL
        self.Version = Version.Release
        self.Previous = None
        self.AllowedOperations = set()
        self.RestrictedOperations = set()
        self.UpdateAllowedOperations()

    def SetMode(self, Mode: SystemMode) -> None:
        # Зміна режиму системи
        self.Previous = self.Current
        self.Current = Mode
        self.UpdateAllowedOperations()

    def UpdateAllowedOperations(self) -> None:
        # Оновлення дозволених операцій залежно від режиму
        ModeOps = {
            SystemMode.NORMAL: {"view", "interact", "navigate"},
            SystemMode.OPERATIONAL: {"view", "interact", "navigate", "alert"},
            SystemMode.EDIT: {"view", "interact", "navigate", "edit", "move", "resize", "delete", "create"},
            SystemMode.LOCKED: {"view", "unlock"},
            SystemMode.STASIS: {"view", "wakeup"},
            SystemMode.YELLOW_ALERT: {"view", "interact", "navigate", "alert", "shield"},
            SystemMode.RED_ALERT: {"view", "interact", "alert", "shield", "weapons"},
            SystemMode.BATTLE: {"view", "interact", "alert", "shield", "weapons", "maneuver"},
            SystemMode.SCIENCE: {"view", "interact", "scan", "analyze", "record"},
            SystemMode.AUTODESTRUCT: {"view", "alert"},
            SystemMode.DIAGNOSTIC: {"view", "diagnose", "scan", "report"},
            SystemMode.MAINTENANCE: {"view", "repair", "replace", "calibrate"},
        }
        self.AllowedOperations = ModeOps.get(self.Current, set())

    def Can(self, Operation: str) -> bool:
        # Перевірка чи дозволена операція в поточному режимі
        return Operation in self.AllowedOperations

    def IsEditMode(self) -> bool:
        # Перевірка чи активний режим редагування
        return self.Current == SystemMode.EDIT

    def IsAlert(self) -> bool:
        # Перевірка чи активний режим тривоги
        return self.Current in (SystemMode.YELLOW_ALERT, SystemMode.RED_ALERT)

class ModeManager:
    # Центральний менеджер режимів системи
    # Приймає AlertSystem в методах для синхронізації
    InstanceRef = None

    @classmethod
    def GetInstance(cls) -> ModeManager:
        if cls.InstanceRef is None:
            cls.InstanceRef = ModeManager()
        return cls.InstanceRef

    def __init__(self):
        self.State = ModeState()
        self.BaselineMode = SystemMode.NORMAL

    @property
    def CurrentMode(self) -> SystemMode:
        return self.State.Current

    def GetMode(self) -> SystemMode:
        # Отримання поточного режиму
        return self.State.Current

    def SetMode(self, Mode: SystemMode, Alert=None):
        # Встановлення режиму з опціональним викликом Alert
        self.State.SetMode(Mode)

        # Синхронізація з AlertSystem якщо передано
        if Alert:
            from lcars.system.alert import AlertLevel
            if Mode == SystemMode.YELLOW_ALERT:
                Alert.SetLevel(AlertLevel.YELLOW)
            elif Mode == SystemMode.RED_ALERT:
                Alert.SetLevel(AlertLevel.RED)
            elif Mode == SystemMode.NORMAL:
                Alert.SetLevel(AlertLevel.GREEN)
        return self

    def EnterEditMode(self):
        # Вхід в режим редагування UI
        self.State.SetMode(SystemMode.EDIT)
        return self

    def ExitEditMode(self, Alert=None):
        # Вихід з режиму редагування
        IsAlert = Alert.IsAlert() if Alert else False
        if IsAlert:
            Level = Alert.Level
            from lcars.system.alert import AlertLevel
            if Level == AlertLevel.YELLOW:
                self.State.SetMode(SystemMode.YELLOW_ALERT)
            elif Level == AlertLevel.RED:
                self.State.SetMode(SystemMode.RED_ALERT)
        else:
            self.State.SetMode(self.BaselineMode)
        return self

    def IsEditMode(self) -> bool:
        # Перевірка чи активний режим редагування
        return self.State.IsEditMode()

    def UpdateAlert(self, AlertLevel: str):
        # Обробка зміни рівня тривоги від AlertSystem
        AlertMap = {
            "GREEN": SystemMode.NORMAL,
            "YELLOW": SystemMode.YELLOW_ALERT,
            "RED": SystemMode.RED_ALERT,
        }
        if AlertLevel in AlertMap:
            self.State.SetMode(AlertMap[AlertLevel])
        return self

    def ActivateBattleMode(self, Alert=None):
        # Активація бойового режиму
        self.SetMode(SystemMode.BATTLE, Alert)
        return self

    def ActivateScienceMode(self, Alert=None):
        # Активація наукового режиму
        self.SetMode(SystemMode.SCIENCE, Alert)
        return self

    def LockConsole(self):
        self.SetMode(SystemMode.LOCKED)
        return self

    def UnlockConsole(self):
        self.SetMode(self.BaselineMode)
        return self

    def EnterStasis(self):
        self.SetMode(SystemMode.STASIS)
        return self

    def ExitStasis(self):
        self.SetMode(self.BaselineMode)
        return self

    def IsLocked(self) -> bool:
        return self.State.Current == SystemMode.LOCKED

    def IsStasis(self) -> bool:
        return self.State.Current == SystemMode.STASIS

    def InitiateAutodestruct(self, Alert=None):
        # Ініціація автознищення
        self.SetMode(SystemMode.AUTODESTRUCT, Alert)
        return self

# Фабрична функція для створення стану
CreateModeState = ModeState
Mode = ModeManager

__all__ = [
    "SystemMode",
    "ModeState",
    "ModeManager",
    "Mode",
]
