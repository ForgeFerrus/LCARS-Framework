#!/usr/bin/env python3
# LCARS Launcher - запуск System Access
import sys
from pathlib import Path

ProjectRoot = str(Path(__file__).parent)
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from lcars.base.type import Chassis
from lcars.base.default import FontSetup

App = Chassis.Application(sys.argv)
FontSetup()

from lcars.ui.panels.access import SystemAccess

Window = SystemAccess()
Window.Native.setFixedSize(800, 600)
Window.Show()

print("◤ LCARS System Access запущено")
sys.exit(App.exec())
