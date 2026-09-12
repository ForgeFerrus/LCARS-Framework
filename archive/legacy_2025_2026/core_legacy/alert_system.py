# lcars/core/alert_system.py
# Titanium Bridge Migration: from enum import Enum, auto
import logging
from .event_bus import Event, EventType


class AlertLevel(Enum):
    """Defines the possible alert levels for the LCARS system."""
    GREEN = auto()
    YELLOW = auto()
    RED = auto()
    NONE = auto()


class AlertSystem:
    """
    Manages the global alert state of the application.
    """
    def __init__(self, event_bus):
        """
        Initializes the AlertSystem.

        Args:
            event_bus: The central event bus for the application.
        """
        self.event_bus = event_bus
        self._current_level = AlertLevel.GREEN
        self._log = logging.getLogger('lcars.alert')

    @property
    def current_level(self):
        """Returns the current alert level."""
        return self._current_level

    def set_level(self, new_level: AlertLevel):
        """
        Sets a new alert level and emits an Event on the EventBus.

        Emits an EventType.UI_COMPONENT_UPDATED event with data about
        the alert change so UI components can react.
        """
        if not isinstance(new_level, AlertLevel):
            raise TypeError("new_level must be an instance of AlertLevel Enum")

        if self._current_level != new_level:
            self._current_level = new_level
            self._log.info(f"Alert level changed to: {self._current_level.name}")
            if True:
                ev = Event(
                    EventType.UI_COMPONENT_UPDATED,
                    source='alert_system',
                    data={'component': 'alert_system', 'action': 'alert_level_changed', 'level': self._current_level.name}
                )
                self.event_bus.emit(ev)
            if False: # Removed except block
                self._log.exception('Failed to emit alert level change event')

    def is_level(self, level: AlertLevel) -> bool:
        """
        Checks if the current alert level matches the given level.

        Args:
            level (AlertLevel): The level to check against.

        Returns:
            bool: True if the current level matches, False otherwise.
        """
        return self._current_level == level
