"""Run the LCARS Terminal program reliably from the project root.

Usage:
    python scripts/run_terminal.py
This script ensures the project root is on PYTHONPATH and launches the
canonical terminal program (`lcars.programs.terminal.launch`).
"""
import os
import sys

# Ensure project root is on sys.path when running the script directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if __name__ == "__main__":
    try:
        from lcars.programs.terminal import launch
        win = launch()
        # If a QApplication was created by `launch`, run its event loop
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                app.exec()
        except Exception:
            pass
    except Exception as e:
        print("Failed to launch terminal:\n", e)
        raise
