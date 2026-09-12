# LCARS Panel Diagnostic Probe 🖖
import sys, os

# Initialize Base Types first
from lcars.base.types import registry, Directive, ODN, Visual, Lore, Isolinear, Matrix
from lcars.base.registry import register_standard
register_standard()

panels = [
    ("COMM", "lcars.ui.panels.comm", "CommPanel"),
    ("DATABASE", "lcars.ui.panels.database", "DatabasePanel"),
    ("SCIENCE", "lcars.ui.panels.science", "SciencePanel"),
    ("NAVIGATION", "lcars.ui.panels.navigation", "NavigationPanel"),
    ("TACTICAL", "lcars.ui.panels.tactical", "TacticalPanel"),
]

print("◤ PROBE: STARTING PANEL SCAN...")
for name, mod_path, cls_name in panels:
    try:
        print(f"◤ SCANNING: {name} ({mod_path})...")
        mod = __import__(mod_path, fromlist=[cls_name])
        cls = getattr(mod, cls_name)
        # Attempt to instantiate (without App context, might fail but we check for Imports)
        print(f"◤ SUCCESS: {name} LOADED.")
    except Exception as e:
        print(f"◤ ERROR: {name} FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

print("◤ PROBE: SCAN COMPLETE.")
