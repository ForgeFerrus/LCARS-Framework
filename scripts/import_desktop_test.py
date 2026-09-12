import importlib, traceback, sys, os

# Ensure workspace root is on sys.path so `lcars` package is importable
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

print('PYTHON:', sys.executable)
print('SYS.PATH[0]=', sys.path[0])

try:
    importlib.import_module('lcars.ui.desktop')
    print('DESKTOP_IMPORT_OK')
except Exception:
    traceback.print_exc()
    sys.exit(1)
