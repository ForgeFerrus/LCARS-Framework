import sys
import traceback
import os

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

try:
    print("Testing LCARSDesktop import...")
    from lcars.ui.desktop import LCARSDesktop
    print("SUCCESS: LCARSDesktop imported.")
except Exception:
    print("ERROR:")
    traceback.print_exc()
    sys.exit(1)
