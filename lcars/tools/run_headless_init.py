# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.system.initialization import initialize_system

if __name__ == '__main__':
    ok = initialize_system(headless=True)
    print('initialize_system returned:', ok)
