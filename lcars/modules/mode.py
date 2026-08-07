# LCARS SYSTEM MODES - MODULES LAYER
# ПРИЗНАЧЕННЯ: Режими роботи системи LCARS
# СТАНДАРТ: Titanium Master (Enum + State Helpers)
# КЕРУВАННЯ: EngineeringController (engineering/controller.py)
from __future__ import annotations
from enum import Enum, auto
from typing import Optional
from lcars.base.version import getVersion

__version__ = getVersion()

class SystemMode(Enum):
    # Режими роботи системи LCARS
    # Визначають доступні функції та обмеження інтерфейсу

    # --- Основні режими ---
    NORMAL = auto()           # Нормальний режим — сталий стан (повернення після тривоги)
    OPERATIONAL = auto()      # Робочий режим — стандартна робота системи
    EDIT = auto()             # Режим редагування — модифікація UI елементів

    # --- Режими тривоги ---
    YELLOW_ALERT = auto()     # Жовта тривога — підвищена увага
    RED_ALERT = auto()        # Червона тривога — критична ситуація

    # --- Бойові режими ---
    BATTLE = auto()           # Бойовий режим — повна бойова готовність

    # --- Наукові режими ---
    SCIENCE = auto()          # Науковий режим — енергія на сенсори

    # --- Критичні режими ---
    AUTODESTRUCT = auto()     # Автознищення — підготовка до самознищення

    # --- Сервісні режими ---
    DIAGNOSTIC = auto()       # Діагностика — перевірка систем
    MAINTENANCE = auto()      # Технічне обслуговування

class ModeState:
    # Стан режиму системи
    # Зберігає поточний режим та дозволені операції

    def __init__(self):
        self.Current = SystemMode.OPERATIONAL
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

    def __init__(self):
        self.State = ModeState()
        self.BaselineMode = SystemMode.NORMAL

    def GetMode(self) -> SystemMode:
        # Отримання поточного режиму
        return self.State.Current

    def SetMode(self, Mode: SystemMode, Alert=None) -> None:
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

    def EnterEditMode(self) -> None:
        # Вхід в режим редагування UI
        self.State.SetMode(SystemMode.EDIT)

    def ExitEditMode(self, Alert=None) -> None:
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

    def IsEditMode(self) -> bool:
        # Перевірка чи активний режим редагування
        return self.State.IsEditMode()

    def OnAlertChanged(self, AlertLevel: str) -> None:
        # Обробка зміни рівня тривоги від AlertSystem
        AlertMap = {
            "GREEN": SystemMode.NORMAL,
            "YELLOW": SystemMode.YELLOW_ALERT,
            "RED": SystemMode.RED_ALERT,
        }
        if AlertLevel in AlertMap:
            self.State.SetMode(AlertMap[AlertLevel])

    def ActivateBattleMode(self, Alert=None) -> None:
        # Активація бойового режиму
        self.SetMode(SystemMode.BATTLE, Alert)

    def ActivateScienceMode(self, Alert=None) -> None:
        # Активація наукового режиму
        self.SetMode(SystemMode.SCIENCE, Alert)

    def InitiateAutodestruct(self, Alert=None) -> None:
        # Ініціація автознищення
        self.SetMode(SystemMode.AUTODESTRUCT, Alert)

# Фабрична функція для створення стану
CreateModeState = ModeState


__all__ = [
    "SystemMode",
    "ModeState",
    "ModeManager",
]
