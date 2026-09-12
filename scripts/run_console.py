"""Run the full-screen ConsoleView (UI) reliably.

Usage:
    python scripts/run_console.py
"""
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if __name__ == "__main__":
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        from lcars.ui.views.console import ConsoleView
        v = ConsoleView(event_bus=None)
        v.setWindowTitle("LCARS Console (demo)")
        v.resize(1000, 700)
        v.show()
        sys.exit(app.exec())
    except Exception as e:
        print("Failed to launch ConsoleView:\n", e)
        raise
