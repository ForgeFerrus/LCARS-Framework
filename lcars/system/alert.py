
from enum import IntEnum
from lcars.base.version import getVersion

def getSystemVersion() -> str:
    # Функція: Отримання версії системи
    # Призначення: Делегує до центральної версії в base.version
    # Повертає: Рядок версії
    return getVersion()

class AlertLevel(IntEnum):
    # Рівні системної тривоги
    GREEN = 0
    YELLOW = 1
    RED = 2

class AlertSystem:
    # Центральна система тривог LCARS
    # Керує рівнями тривоги та інтегрується з Controller

    def Init(self, EventBus=None, Controller=None):
        # Ініціалізація системи тривог з параметрами EventBus та Controller
        # EventBus використовується для відправки сигналів про зміну рівня тривоги
        # Controller використовується для застосування візуальних змін рівня тривоги
        self.EventBus = EventBus
        self.Controller = Controller
        # Початковий рівень тривоги завжди GREEN (0) - нормальний стан
        self.Level = AlertLevel.GREEN

    def SetLevel(self, Level: AlertLevel) -> None:
        # Перевіряємо чи переданий рівень є валідним enum AlertLevel
        # І чи це новий рівень відмінний від поточного
        if isinstance(Level, AlertLevel) and self.Level != Level:
            # Присвоюємо новий рівень тривоги в поле Level
            self.Level = Level
            # Якщо є Controller - викликаємо ApplyLevel для застосування візуальних змін
            if self.Controller:
                self.Controller.ApplyLevel(Level)
            # Якщо є EventBus - відправляємо сигнал CHANGED з іменем рівня
            if self.EventBus:
                self.EventBus.emit("CHANGED", level=Level.name)

    def CycleLevel(self) -> AlertLevel:
        # Циклічне перемикання рівня тривоги
        # Якщо поточний GREEN (0) -> перемикаємо на YELLOW (1)
        # Якщо поточний YELLOW (1) -> перемикаємо на RED (2)
        # Якщо поточний RED (2) -> повертаємось на GREEN (0)
        Target = AlertLevel.YELLOW if self.Level == AlertLevel.GREEN else (
            AlertLevel.RED if self.Level == AlertLevel.YELLOW else AlertLevel.GREEN)
        # Викликаємо SetLevel для застосування нового рівня
        self.SetLevel(Target)
        # Повертаємо новий рівень тривоги
        return Target

    def RaiseLevel(self) -> None:
        # Підвищення рівня тривоги на один щабель
        # Перевіряємо чи поточний рівень не RED (максимальний)
        if self.Level != AlertLevel.RED:
            # Викликаємо CycleLevel для підвищення рівня
            self.CycleLevel()

    def LowerLevel(self) -> None:
        # Зниження рівня тривоги на один щабель
        # Якщо поточний RED (2) -> перемикаємо на YELLOW (1)
        if self.Level == AlertLevel.RED:
            self.SetLevel(AlertLevel.YELLOW)
        # Якщо поточний YELLOW (1) -> перемикаємо на GREEN (0)
        elif self.Level == AlertLevel.YELLOW:
            self.SetLevel(AlertLevel.GREEN)

    def IsLevel(self, Level: AlertLevel) -> bool:
        # Перевірка чи поточний рівень тривоги відповідає переданому
        # Повертає True якщо рівні співпадають
        return self.Level == Level

    def IsAlert(self) -> bool:
        # Перевірка чи активна тривога (рівень не GREEN)
        # Повертає True якщо рівень тривоги YELLOW або RED
        return self.Level != AlertLevel.GREEN

    PublicExports = ["AlertLevel", "AlertSystem", "getSystemVersion"]

    def SetLevel(self, Level):
        """Backward-compat wrapper for SetLevel (tactical.py uses lowercase)."""
        self.SetLevel(Level)

    def SetAlertLevel(self, TargetLevelNode):
        LevelMap = {
            "GREEN": AlertLevel.GREEN,
            "YELLOW": AlertLevel.YELLOW,
            "RED": AlertLevel.RED,
            "0": AlertLevel.GREEN,
            "1": AlertLevel.YELLOW,
            "2": AlertLevel.RED,
        }
        Level = LevelMap.get(str(TargetLevelNode).upper(), AlertLevel.GREEN)
        self.SetLevel(Level)


# ActiveAlerts — pre-initialized singleton for panels that just need a reference
class ActiveInstance(AlertSystem):
    def __init__(self):
        self.EventBus = None
        self.Controller = None
        self.Level = AlertLevel.GREEN
ActiveAlerts = ActiveInstance()