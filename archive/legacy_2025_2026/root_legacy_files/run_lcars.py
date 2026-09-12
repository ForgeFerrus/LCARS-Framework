#!/usr/bin/env python3
# LCARS SYSTEM LAUNCHER

import sys
from pathlib import Path

projectRoot = Path(__file__).resolve().parent
if str(projectRoot) not in sys.path:
    sys.path.insert(0, str(projectRoot))

print("Starting LCARS System...")

# Запускаємо BIOS boot screen
try:
    from lcars.ui.screen.boot import run_bios
    print("Launching BIOS boot screen...")
    run_bios(auto_start=True, emergency_mode=False)
except Exception as e:
    print(f"Boot screen failed: {e}")
    print("Trying emergency mode...")
    try:
        from lcars.ui.screen.boot import run_bios
        run_bios(auto_start=False, emergency_mode=True)
    except Exception as e2:
        print(f"Emergency mode failed: {e2}")
        print("Starting minimal kernel...")
        from lcars.core.bootstrap import Start
        kernel = Start(Gui=False)
        print(f"Kernel started: {kernel}")
