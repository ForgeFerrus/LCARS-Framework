import os
import sys
from pathlib import Path

root_dir = str(Path(__file__).resolve().parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from lcars.base.type import LCARS
from lcars.base.default import SetDisplayFlag
from lcars.ui.terminal import LCARSTerminal


def run():
    Application = None
    try:
        Application = LCARS.Application
    except Exception:
        Application = None

    if Application is None:
        print("LCARS application carrier is not available.")
        return 1

    try:
        from PyQt6.QtWidgets import QApplication
        App = QApplication.instance() or QApplication(sys.argv)
    except Exception:
        App = None

    Window = LCARSTerminal(Parent=None, lite=False)

    Host = Window.widget
    if Host is not None:
        try:
            from PyQt6.QtCore import Qt
            SetDisplayFlag(Host, Qt.WindowType.FramelessWindowHint, True)
        except Exception:
            pass
        if hasattr(Host, "resize"):
            Host.resize(1280, 820)
        if hasattr(Host, "show"):
            Host.show()

    if App is not None and hasattr(App, "exec"):
        return App.exec()
    return 0


if __name__ == "__main__":
    sys.exit(run())
