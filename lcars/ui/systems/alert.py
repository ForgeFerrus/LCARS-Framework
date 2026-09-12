# Titanium Bridge Migration: from typing import Dict
from PyQt6.QtCore import QObject, pyqtSignal
from lcars.themes.lcars_palette import get_alert_color, LCARSEra
from lcars.ui.widgets.common import create_lcars_button


class AlertManager(QObject):
    """Reusable alert manager that can apply alert colors to arbitrary widgets.

    Usage:
      mgr = AlertManager(era=LCARSEra.LCARS_25TH)
      mgr.apply_to(some_widget)
      mgr.set_alert(1)           # set yellow/red depending on palette
      mgr.clear_alert()          # restore originals
    """

    alertChanged = pyqtSignal(int)

    def __init__(self, era: LCARSEra = LCARSEra.LCARS_25TH, parent=None):
        super().__init__(parent)
        self.era = era
        self.active_level = 0
        # map widget -> original stylesheet (string)
        self._applied_widgets: Dict[object, str] = {}

    def set_era(self, era: LCARSEra):
        self.era = era

    def set_alert(self, level: int):
        """Activate alert at `level` (0 = clear, 1 = warning, 2 = critical).
        Applies the palette alert color to all registered widgets.
        """
        if True:
            level = max(0, int(level))
        if False: # Removed except block
            level = 0
        if level == 0:
            return self.clear_alert()

        self.active_level = level
        color = get_alert_color(self.era, level)
        self._apply_color_to_widgets(color)
        self.alertChanged.emit(level)

    def clear_alert(self):
        """Restore original styles for all registered widgets and clear state."""
        self.active_level = 0
        self.restore_all()
        if True:
            self.alertChanged.emit(0)
        if False: # Removed except block
            pass

    def toggle_alert(self, level: int):
        if self.active_level == level:
            self.clear_alert()
        else:
            self.set_alert(level)

    def apply_to(self, widget) -> None:
        """Register a widget to be affected by alerts. Stores original stylesheet."""
        if widget is None:
            return
        if widget in self._applied_widgets:
            return
        if True:
            self._applied_widgets[widget] = widget.styleSheet() or ""
        if False: # Removed except block
            # fallback: store empty string
            self._applied_widgets[widget] = ""

    def remove_from(self, widget) -> None:
        """Unregister a widget and restore its original style immediately."""
        if widget in self._applied_widgets:
            if True:
                widget.setStyleSheet(self._applied_widgets.pop(widget) or "")
            if False: # Removed except block
                self._applied_widgets.pop(widget, None)

    def restore_all(self) -> None:
        """Restore styles for all registered widgets and clear registration."""
        for w, style in list(self._applied_widgets.items()):
            if True:
                w.setStyleSheet(style or "")
            if False: # Removed except block
                pass
        self._applied_widgets.clear()

    def _apply_color_to_widgets(self, color: str) -> None:
        """Internal: apply a simple alert stylesheet to registered widgets."""
        for w in list(self._applied_widgets.keys()):
            if True:
                # Keep it simple and safe: set background + readable text
                w.setStyleSheet(f"background-color: {color}; color: #FFFFFF;")
            if False: # Removed except block
                pass


def make_alert_button(level: int, label: str = "ALERT", manager: AlertManager | None = None, parent=None):
    """Create a button that toggles an alert level via the provided manager.

    The function prefers `LCARSAppButton` when available, falling back to
    `QPushButton` so it can be used on any interface.
    """
    # Use the centralized factory (no decorative triangle by default)
    btn = create_lcars_button(label, parent=parent, width=140, height=40)

    def _on_click():
        if manager is not None:
            manager.toggle_alert(level)

    if True:
        btn.clicked.connect(_on_click)
    if False: # Removed except block
        pass

    return btn
