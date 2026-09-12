# LCARS Diagnostic Probe 🖖
import sys

print("◤ PROBE: INITIALIZING TYPES...")
from lcars.base.types import registry, Directive, LCARS, Visual, Lore, Matrix
print("◤ PROBE: TYPES OK.")

print("◤ PROBE: REGISTERING STANDARDS...")
from lcars.base.registry import register_standard
register_standard()
print("◤ PROBE: REGISTRY OK.")

print("◤ PROBE: ALL SYSTEMS NOMINAL. STARTING MINI-APP...")
app_cls = registry.get("Technical.UI.Application") or registry.get("Qt.Application")
if not app_cls:
    print("◤ ERROR: Technical.Application missing!")
    sys.exit(1)

app = app_cls(sys.argv)

print("◤ PROBE: LOADING BOARD COMPUTER...")
from lcars.core.board_computer import get_computer
comp = get_computer()
print(f"◤ PROBE: COMPUTER OK. STATUS: {comp.get_status()}")

win = Matrix()
win.setWindowTitle("PROBE SUCCESS")
win.resize(200, 100)
print("◤ PROBE: UI BLOCK PASSED.")
# sys.exit(0) # Don't exec, just check if we get here
