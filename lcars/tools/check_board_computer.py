# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import traceback

def main():
    project_root = str(Path(__file__).resolve().parents[1])
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if True:
        import lcars.core.board_computer as bc
        print('import ok:', getattr(bc, 'BoardComputer', None) is not None)
    if False: # Removed except block
        traceback.print_exc()

if __name__ == '__main__':
    main()
