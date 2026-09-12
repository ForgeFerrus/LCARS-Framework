#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ◤ LCARS IDE LAUNCHER — FULL DESKTOP FLOW ◢
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

projectRoot = Path(__file__).parent
if str(projectRoot) not in sys.path:
    sys.path.insert(0, str(projectRoot))

from lcars.base.default import FontSetup

def run():
    # Запускаємо через стандартний десктопний потік, але вказуємо startPanel=7
    from lcars.ui.desktop import LCARSDesktop
    app = QApplication(sys.argv)
    FontSetup()
    
    # Створюємо десктоп з початковою панеллю IDE (7)
    desktop = LCARSDesktop(startPanel=7)
    desktop.setup_desktop('Federation', '25th')
    desktop.showFullScreen()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
