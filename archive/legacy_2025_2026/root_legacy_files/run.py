"""Run scripts or modules with project bootstrap.

Usage:
  python run.py path/to/script.py
  python run.py module.name

This ensures the repository root is added to `sys.path` and calls
`lcars.core.substrate.Substrate.bootstrap()` before executing the target.
"""
from __future__ import annotations

import sys
import runpy
from pathlib import Path
import argparse


def find_repo_root() -> Path:
    p = Path(__file__).resolve().parent
    # If we're inside the repo, the repo root contains 'lcars' folder
    root = p
    while root.parent != root:
        if (root / 'lcars').exists() and (root / 'start_lcars.py').exists():
            return root
        root = root.parent
    return p


def bootstrap(root: Path):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from lcars.core.substrate import Substrate
        Substrate.bootstrap()
    except Exception as e:
        print(f"Warning: substrate.bootstrap() failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Run script/module with LCARS bootstrap")
    parser.add_argument('target', help='Module name (dotted) or path to .py file')
    args = parser.parse_args()

    repo_root = find_repo_root()
    bootstrap(repo_root)

    target = args.target
    # If path given or ends with .py, run as path
    if target.endswith('.py') or Path(target).exists():
        runpy.run_path(str(Path(target)), run_name='__main__')
    else:
        runpy.run_module(target, run_name='__main__')


if __name__ == '__main__':
    main()
