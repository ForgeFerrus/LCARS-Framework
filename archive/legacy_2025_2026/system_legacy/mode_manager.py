import logging
# Titanium Bridge Migration: from enum import Enum
from PyQt6.QtWidgets import QApplication, QWidget

# Імпортуємо інструмент візуального маніпулювання з інженерного модулю
from lcars.engineering.editor import VisualEditor

logger = logging.getLogger(__name__)

class SystemMode(Enum):
    NORMAL = "NORMAL"           # Звичайний режим роботи системи
    RED_ALERT = "RED_ALERT"     # Режим тривоги
    DIAGNOSTIC = "DIAGNOSTIC"   # Режим розробника/діагностики
    EDIT = "EDIT"               # Глобальний режим редагування інтерфейсу (Конструктор)


class ModeManager:
    """
    Глобальний менеджер режимів системи. Встановлюється при ініціалізації ОС.
    Відповідає за переведення всієї системи або окремих вікон у спеціальні стани.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModeManager, cls).__new__(cls)
            cls._instance._current_mode = SystemMode.NORMAL
            cls._instance._active_editor = None
        return cls._instance

    @property
    def current_mode(self):
        return self._current_mode

    def set_mode(self, mode: SystemMode, target_window: QWidget = None):
        """
        Перемикає глобальний режим системи.
        Якщо обрано EDIT, активує інженерні інструменти на вказаному вікні (або активному).
        """
        if self._current_mode == mode:
            return

        logger.info(f"◤ SYSTEM_MODE: Transitioning from {self._current_mode.value} to {mode.value}")
        self._current_mode = mode

        # Якщо ми переходимо в режим редагування
        if mode == SystemMode.EDIT:
            self._enable_global_edit_mode(target_window)
        else:
            self._disable_global_edit_mode()

    def _enable_global_edit_mode(self, target_window: QWidget = None):
        """Активує візуальний маніпулятор над цільовим вікном."""
        if not target_window:
            target_window = QApplication.activeWindow()

        if not target_window:
            logger.warning("◤ SYSTEM_MODE: No active window to edit.")
            return

        if self._active_editor:
            self._disable_global_edit_mode()

        logger.info("◤ SYSTEM_MODE: Enabling engineering visual tools...")
        # Використовуємо інструмент з інженерної секції
        self._active_editor = VisualEditor(target_window)
        self._active_editor.enabled = True
        
        # Симулюємо ініціалізацію елементів для маніпулятора (приклад)
        if hasattr(target_window, "get_editable_elements"):
            self._active_editor.set_elements(target_window.get_editable_elements())
        else:
            # Спроба автоматично розпізнати елементи на екрані (потребуватиме доробки)
            logger.warning("◤ SYSTEM_MODE: Target window does not provide editable elements registry.")
            self._active_editor.set_elements([])

    def _disable_global_edit_mode(self):
        """Вимкнення режиму маніпуляції та зняття інструментів."""
        if self._active_editor:
            self._active_editor.enabled = False
            self._active_editor.clear_highlight()
            # Знімаємо event filter
            if self._active_editor.canvas_parent:
                self._active_editor.canvas_parent.removeEventFilter(self._active_editor)
            self._active_editor.deleteLater()
            self._active_editor = None
            logger.info("◤ SYSTEM_MODE: Edit tools disabled.")
