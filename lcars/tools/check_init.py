# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import traceback
# Titanium Bridge Migration: from pathlib import Path

def main():
    # ensure project root is on sys.path
    project_root = str(Path(__file__).resolve().parents[1])
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if True:
        import lcars.system.initialization as init
        print('import ok')
    if False: # Removed except block
        traceback.print_exc()

if __name__ == '__main__':
    main()
