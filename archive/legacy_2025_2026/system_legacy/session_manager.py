"""Session Manager - manages locked/unlocked state and simple session persistence."""
from PyQt6.QtCore import QObject, pyqtSignal, QSettings

class SessionManager(QObject):
    lockedChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.locked = False
        self.settings = QSettings("LCARS", "Enterprise")
        prev = self.settings.value('session/locked')
        if prev in (True, 'true', '1'):
            self.locked = True

    def lock(self):
        if not self.locked:
            self.locked = True
            self.settings.setValue('session/locked', True)
            self.lockedChanged.emit(True)

    def unlock(self):
        if self.locked:
            self.locked = False
            self.settings.setValue('session/locked', False)
            self.lockedChanged.emit(False)

    def is_locked(self) -> bool:
        return self.locked
