#!/usr/bin/env python3
# LCARS DESKTOP LAUNCHER
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from lcars.base.desktop import LCARSDesktop
from lcars.base.default import FontSetup

if __name__ == "__main__":
    app = QApplication(sys.argv)
    FontSetup()
    
    # Створюємо LCARS десктоп напряму
    desktop = LCARSDesktop()
    desktop.show()
    
    # Максимізуємо вікно
    desktop.setWindowState(Qt.WindowState.WindowMaximized)
    
    sys.exit(app.exec())
