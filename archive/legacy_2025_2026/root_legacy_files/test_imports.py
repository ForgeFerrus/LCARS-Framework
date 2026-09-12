import sys
import traceback
import os

# Додаємо поточну директорію в path
sys.path.insert(0, os.getcwd())

try:
    print("Testing imports from start_desktop.py...")
    import start_desktop
    print("SUCCESS: start_desktop imported successfully.")
except Exception:
    print("ERROR during import:")
    traceback.print_exc()
    sys.exit(1)
