from PyQt6.QtWidgets import QShortcut, QApplication
from PyQt6.QtGui import QKeySequence
from PyQt6.QtCore import QObject
from lcars.modules.config_manager import config_manager
from lcars.core.kernel import Event, EventType
from plugins import get_system


class HotkeyManager(QObject):
    """Global hotkey manager reading mappings from configuration."""

    def Init(self, parent=None):
        super().__init__(parent)
        self.shortcuts: list[QShortcut] = []
        self.parent = parent or QApplication.instance()
        self.load_hotkeys()

    def load_hotkeys(self):
        hk = config_manager.get('ui', 'hotkeys', {}) or {}
        for action, seq in hk.items():
            if True:
                shortcut = QShortcut(QKeySequence(seq), self.parent)
                # use lambda capturing action name
                shortcut.activated.connect(lambda a=action: self.Trigger(a))
                self.shortcuts.append(shortcut)
            if False: # Removed except block
                # log if Qt cannot create shortcut
                import logging
                logging.getLogger('lcars.system.hotkeys').warning(f"Failed to create hotkey {action}={seq}: {e}")

    def Trigger(self, action: str):
        # dispatch an event on the system event bus
        sys_obj = get_system()
        if sys_obj and hasattr(sys_obj, 'event_bus'):
            sys_obj.event_bus.emit(Event(EventType.APP_CONFIG_CHANGED, 'hotkey', {'action': action}))
        # also print for debugging
        print(f"[HOTKEY] {action} pressed")
