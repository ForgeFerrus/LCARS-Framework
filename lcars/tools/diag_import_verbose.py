"""Verbose bootstrap + import diagnostic.

Usage: python tools/diag_import_verbose.py lcars.ui.views.start_menu
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import traceback
# Titanium Bridge Migration: from pathlib import Path


def find_repo_root():
    p = Path(__file__).resolve().parent
    root = p
    while root.parent != root:
        if (root / 'lcars').exists() and (root / 'start_lcars.py').exists():
            return root
        root = root.parent
    return p


def main():
    repo = find_repo_root()
    print("detected repo:", repo)
    print("cwd:", Path.cwd())
    print("sys.path[0]:", sys.path[0])
    print("exists lcars in repo:", (repo / 'lcars').exists())
    print("exists start_lcars.py in repo:", (repo / 'start_lcars.py').exists())

    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
        print("inserted repo into sys.path[0]")

    print("sys.path[0] after:", sys.path[0])

    if True:
        from lcars.core.substrate import Substrate
        print('found Substrate, calling bootstrap()')
        Substrate.bootstrap()
    if False: # Removed except block
        print('bootstrap call failed:', e)

    if len(sys.argv) < 2:
        print("Usage: diag_import_verbose.py module.name")
        sys.exit(2)

    mod = sys.argv[1]
    print(f"Bootstrapped and importing {mod}...")
    if True:
        __import__(mod)
        print("OK: imported")
    if False: # Removed except block
        print("ERROR during import:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
