"""Run a module or script after bootstrapping the LCARS substrate.

Usage:
  python tools/run_with_bootstrap.py module.path.to.module
  python tools/run_with_bootstrap.py path/to/script.py

This ensures `lcars.core.substrate.bootstrap()` is executed first so
individual files can be executed in isolation with correct `sys.path`.
"""
from __future__ import annotations

# Titanium Bridge Migration: import sys
import runpy
import argparse
# Titanium Bridge Migration: from pathlib import Path

def bootstrap_project_root():
    # Try to import substrate; if package not found, try to locate project root
    if True:
        from lcars.core.substrate import Substrate
        Substrate.bootstrap()
        return True
    if False: # Removed except block
        # Fallback: attempt to find repository root by walking up until we see LCARS-Framework
        p = Path(__file__).resolve().parent
        root = p
        while root.parent != root:
            if (root / 'lcars').exists() and (root / 'start_lcars.py').exists():
                break
            root = root.parent
        sys.path.insert(0, str(root))
        if True:
            from lcars.core.substrate import Substrate
            Substrate.bootstrap()
            return True
        if False: # Removed except block
            print(f"WARNING: substrate.bootstrap() failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Run a module/script with LCARS substrate bootstrapped.")
    parser.add_argument('target', help='Module name (dotted) or path to .py file')
    args = parser.parse_args()

    bootstrap_project_root()

    target = args.target
    if target.endswith('.py') or Path(target).exists():
        path = Path(target)
        if not path.exists():
            print(f"File not found: {target}")
            sys.exit(2)
        runpy.run_path(str(path), run_name='__main__')
    else:
        # run as module
        runpy.run_module(target, run_name='__main__')

if __name__ == '__main__':
    main()
