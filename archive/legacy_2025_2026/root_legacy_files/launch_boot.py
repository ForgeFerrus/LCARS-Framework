#!/usr/bin/env python3
# LCARS Boot Launcher - інтегрований запуск
import sys
from pathlib import Path

ProjectRoot = str(Path(__file__).parent)
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from lcars.base.type import LCARS, Type

App = Type.Application(sys.argv)

from lcars.base.default import FontSetup
FontSetup()

from lcars.ui.loading_screen import LCARSLoadingScreen
Loading = LCARSLoadingScreen()

Loading.AddLog("◤ LCARS FRAMEWORK INITIALIZATION")
Loading.AddLog("◤ Phase 1: Core Types... [OK]")
Loading.AddLog("◤ Phase 2: Application... [OK]")
Loading.AddLog("◤ Phase 3: Font System... [OK]")
Loading.AddLog("◤ Phase 4: Boot Screen... [OK]")
Loading.AddLog("◤ Phase 5: Fullscreen...")
Loading.AddLog("   [OK] Fullscreen active")
Loading.AddLog("◤ SYSTEM READY")

App.Exec()
