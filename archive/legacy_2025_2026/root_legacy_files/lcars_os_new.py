"""
LCARS Operating System - Main Entry Point
Використовує lock_screen.py з boot sequence та всіма опціями
"""

import sys
from pathlib import Path

project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    """Launch LCARS OS"""
    from PyQt6.QtWidgets import QApplication
    from lcars.ui.lock_screen import LCARSLockScreen
    
    app = QApplication(sys.argv)
    
    # Start LCARS OS with lock screen (includes boot sequence)
    lcars_os = LCARSLockScreen()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()