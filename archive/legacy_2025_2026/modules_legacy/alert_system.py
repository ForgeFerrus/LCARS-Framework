# Titanium Bridge Migration: from enum import Enum, auto
from lcars.core.kernel import Event, EventType
from lcars.modules.mode_manager import SystemMode

# Інженерні підсистеми для прямого керування
from lcars.engineering.deflector import Deflector
from lcars.engineering.drive import WarpDrive
from lcars.engineering.damage_control import DamageControl

class AlertLevel(Enum):
    GREEN = auto()
    YELLOW = auto()
    RED = auto()
    BLUE = auto()   # Режим посадки / екологічної небезпеки
    BLACK = auto()  # Режим радіомовчання / критичної скритності

class AlertSystem:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self._current_level = AlertLevel.GREEN
        self._current_mode = SystemMode.NORMAL
        
        # Ініціалізація інженерних підсистем
        self.deflector = Deflector()
        self.drive = WarpDrive()
        # Assume path is current working directory for damage control
        # Titanium Bridge Migration: import os
        self.damage_control = DamageControl(os.getcwd())

    @property
    def current_level(self):
        return self._current_level

    @property
    def current_mode(self):
        return self._current_mode

    def set_alert(self, level: AlertLevel):
        self.set_level(level)

    def set_level(self, new_level):
        if isinstance(new_level, AlertLevel) and self._current_level != new_level:
            self._current_level = new_level

            # Пряма взаємодія з інженерними системами залежно від рівня
            if new_level == AlertLevel.RED:
                self.deflector.shield_level = 100
                self.drive.mode = "impulse" # Готовність до маневрів
                self.damage_control.verify_hull_integrity()
            elif new_level == AlertLevel.YELLOW:
                self.deflector.shield_level = 50
                self.drive.mode = "standby"
            elif new_level in (AlertLevel.GREEN, AlertLevel.BLUE):
                self.deflector.shield_level = 0
                self.drive.mode = "standby"
            elif new_level == AlertLevel.BLACK:
                self.deflector.shield_level = 0
                self.drive.mode = "standby"
                # Тут можна вимкнути мережеві випромінювання (stealth)

            ev = Event(
                EventType.UI_COMPONENT_UPDATED,
                source="alert_system",
                data={
                    "component": "alert_system",
                    "action": "alert_level_changed",
                    "level": self._current_level.name,
                },
            )
            self.event_bus.emit(ev)

        elif isinstance(new_level, SystemMode) and self._current_mode != new_level:
            self._current_mode = new_level
            
            if new_level == SystemMode.BATTLE:
                # Максимальне переведення всієї інженерії в бойовий стан
                self.deflector.shield_level = 200 # Overcharge
                self.drive.mode = "warp"
                
                self.event_bus.emit(Event(
                    EventType.SYSTEM_ALERT,
                    source="alert_system",
                    data={"action": "battle_mode", "level": "BATTLE"}
                ))
            elif new_level == SystemMode.TACTICAL:
                # Тактичний режим: сенсори на максимум, щити напоготові
                self.deflector.shield_level = 100
                self.drive.mode = "impulse"
                self.event_bus.emit(Event(EventType.SYSTEM_MODE_CHANGED, data={"mode": "TACTICAL"}))
                
            elif new_level == SystemMode.SCIENCE:
                # Науковий режим: енергія на сенсори
                self.deflector.shield_level = 20
                self.drive.mode = "standby"
                self.event_bus.emit(Event(EventType.SYSTEM_MODE_CHANGED, data={"mode": "SCIENCE"}))
                
            elif new_level == SystemMode.AUTODESTRUCT:
                # Вимикаємо всі захисти, готуємо ядро до руйнування
                self.deflector.shield_level = 0
                
                self.event_bus.emit(Event(
                    EventType.SYSTEM_ALERT,
                    source="alert_system",
                    data={"action": "autodestruct", "level": "AUTODESTRUCT"}
                ))

    def activate_battle_mode(self):
        self.set_level(SystemMode.BATTLE)

    def initiate_autodestruct(self):
        self.set_level(SystemMode.AUTODESTRUCT)

    def is_level(self, level: AlertLevel) -> bool:
        level_hierarchy = {
            AlertLevel.GREEN: 1,
            AlertLevel.YELLOW: 2,
            AlertLevel.RED: 3
        }
        return level_hierarchy.get(self._current_level, 0) == level_hierarchy.get(level, -1)
        
