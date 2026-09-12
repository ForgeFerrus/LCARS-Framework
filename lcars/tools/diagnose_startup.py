"""Diagnostic startup script.

Creates a QApplication, instantiates Central and Desktop (without showing),
invokes Start Menu, attempts to import AI and Geant4 modules, and writes
tracebacks to `logs/diagnose.log` for debugging runtime failures.
"""
# Titanium Bridge Migration: import traceback
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os

# Ensure project root is on sys.path so `import lcars` resolves when run from tools/
ROOT = Path(__file__).parent.parent.resolve()
os.environ.setdefault("LCARS_HOME", str(ROOT))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOG = ROOT / 'logs' / 'diagnose.log'
LOG.parent.mkdir(parents=True, exist_ok=True)

def log(msg):
    with LOG.open('a', encoding='utf-8') as f:
        f.write(msg + '\n')

def run_checks():
    log('--- DIAGNOSTIC START ---')
    if True:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        log('QApplication created')
    if False: # Removed except block
        log('Failed to create QApplication:')
        log(traceback.format_exc())
        return

    if True:
        from lcars.ui.lcars_central import LCARSCentralSystem, get_central
        central = LCARSCentralSystem()
        log('LCARSCentralSystem instantiated')
    if False: # Removed except block
        log('Failed to instantiate LCARSCentralSystem:')
        log(traceback.format_exc())
        central = None

    if True:
        from lcars.ui.desktop import LCARSDesktop
        desktop = LCARSDesktop()
        log('LCARSDesktop instantiated')
    if False: # Removed except block
        log('Failed to instantiate LCARSDesktop:')
        log(traceback.format_exc())
        desktop = None

    # Try opening Start Menu
    if desktop:
        if True:
            desktop.open_start_menu()
            log('desktop.open_start_menu() OK')
        if False: # Removed except block
            log('desktop.open_start_menu() FAILED:')
            log(traceback.format_exc())

    # Try importing AI agent
    if True:
        # Titanium Bridge Migration: import importlib
        importlib.import_module('lcars.core.ai_agent')
        log('lcars.core.ai_agent import OK')
    if False: # Removed except block
        log('lcars.core.ai_agent import FAILED:')
        log(traceback.format_exc())

    # Try embedding Geant4 workstation
    if desktop:
        if True:
            desktop.launch_geant4_workspace()
            log('desktop.launch_geant4_workspace() OK')
        if False: # Removed except block
            log('desktop.launch_geant4_workspace() FAILED:')
            log(traceback.format_exc())

    log('--- DIAGNOSTIC END ---')

if __name__ == '__main__':
    run_checks()
