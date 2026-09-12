"""
22nd Century System bundle: unified entrypoint and 22nd-only UI bindings.
"""

from pathlib import Path
import sys

from .launcher import launch_22nd

try:
    from .legacy.LCARS_22nd import NXConsole
except ImportError:
    NXConsole = None

__all__ = ["launch_22nd", "NXConsole"]


def run_nx_console():
    root = Path(__file__).resolve().parents[3]
    if NXConsole is None:
        raise ImportError("22nd legacy console is unavailable in this environment")
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = NXConsole(root)
    window.showFullScreen()
    return app.exec()
