"""
Program wrapper for the LCARS Terminal.
- Exposes a simple `launch` function used by the Programs launcher and other UI
  entry points to start the Terminal as a standalone program/window.
- Keeps the UI class (`LCARSTerminal`) implemented under `lcars.ui.tools.terminal`.

Usage:
    from lcars.programs.terminal import launch
    win = launch(parent=some_widget)

The function returns the QMainWindow instance so callers can keep a reference.
"""
from __future__ import annotations
import sys
from typing import Optional
from PyQt6.QtWidgets import QApplication, QMainWindow
from lcars.themes.lcars_palette import LCARSEra

try:
    from lcars.ui.tools.terminal import LCARSTerminal
except Exception:
    # Safe fallback for import-time failures in UI-less environments
    LCARSTerminal = None


def _ensure_qapp():
    if QApplication.instance() is None:
        return QApplication(sys.argv)
    return QApplication.instance()


def launch(parent: Optional[object] = None, era: Optional[LCARSEra] = None, faction: Optional[str] = None) -> Optional[QMainWindow]:
    """Launch the Terminal program as a separate window.

    Returns the created QMainWindow or None if UI class is unavailable.
    """
    if LCARSTerminal is None:
        return None

    app = _ensure_qapp()
    win = QMainWindow(parent)
    win.setWindowTitle("LCARS :: TERMINAL")
    term = LCARSTerminal(parent=win, era=era or LCARSEra.LCARS_25TH, faction=faction)
    win.setCentralWidget(term)
    win.resize(920, 520)
    win.show()
    try:
        win.raise_()
        win.activateWindow()
    except Exception:
        pass
    return win


if __name__ == "__main__":
    app = _ensure_qapp()
    launch()
    sys.exit(app.exec())
