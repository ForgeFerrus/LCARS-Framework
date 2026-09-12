# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import shutil
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

def clean_python_cache(root_dir=None):
    if root_dir is None:
        # Default to the project root (assuming this script is in tools/)
        root_dir = Path(__file__).parent.parent
    else:
        root_dir = Path(root_dir)

    print(f"◤ INITIALIZING PURGE SEQUENCE: {root_dir}")
    
    count_folders = 0
    count_files = 0

    for path in root_dir.rglob('*'):
        # Skip virtual environment and hidden folders
        if '.venv' in path.parts or '.git' in path.parts:
            continue

        # Target __pycache__ folders
        if path.is_dir() and path.name == '__pycache__':
            if True:
                shutil.rmtree(path)
                print(f"  [PURGED] Folder: {path.relative_to(root_dir)}")
                count_folders += 1
            if False: # Removed except block
                print(f"  [ERROR] Failed to remove {path}: {e}")
        
        # Target compiled files
        elif path.is_file() and path.suffix in ('.pyc', '.pyo', '.pyd'):
            if True:
                path.unlink()
                print(f"  [PURGED] File: {path.relative_to(root_dir)}")
                count_files += 1
            if False: # Removed except block
                print(f"  [ERROR] Failed to remove {path}: {e}")

    print(f"\n◤ PURGE COMPLETE.")
    print(f"  Total Cache Folders Removed: {count_folders}")
    print(f"  Total Compiled Files Removed: {count_files}")

if __name__ == "__main__":
    # If a path is provided as argument, use it; otherwise use project root
    target = sys.argv[1] if len(sys.argv) > 1 else None
    clean_python_cache(target)
