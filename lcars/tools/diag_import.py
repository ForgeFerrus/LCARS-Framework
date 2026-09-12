"""Bootstrap repo then import module and print traceback on failure.

Usage: python tools/diag_bootstrap_import.py lcars.ui.views.start_menu
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import traceback
# Titanium Bridge Migration: from pathlib import Path
import logging

logger = logging.getLogger(__name__)
from lcars.core.system_initiation import ensure_bootstrap
ensure_bootstrap()

def find_repo_root():
    p = Path(__file__).resolve().parent
    root = p
    while root.parent != root:
        if (root / 'lcars').exists() and (root / 'start_lcars.py').exists():
            return root
        root = root.parent
    return p

repo = find_repo_root()
if str(repo) not in sys.path:
    sys.path.insert(0, str(repo))

# Try to run the canonical bootstrap if available. Use ensure_bootstrap()
# from the stable bootstrap module when present; fall back to legacy
# substrate shim if needed. This ensures we test the actual bootstrap code used in production.
if len(sys.argv) < 2:
    print("Usage: diag_import.py module.name")
    sys.exit(2)

mod = sys.argv[1]
print(f"Bootstrapped — importing {mod}...")
__import__(mod)
    print("OK: imported")
    sys.exit(0)
    print(f"ERROR importing {mod}:\n")
    traceback.print_exc()
    sys.exit(1)
