#!/usr/bin/env python3
"""Compile all Python files under a folder and optionally run _smoke_test.py if present."""
from pathlib import Path
import py_compile
import sys
import subprocess

root = Path(__file__).resolve().parent.parent
learning = root / 'programs' / 'learning'

errors = []
compiled = 0
if not learning.exists():
    print("Learning folder not found:", learning)
    sys.exit(2)

for p in sorted(learning.rglob('*.py')):
    try:
        py_compile.compile(str(p), doraise=True)
        compiled += 1
    except py_compile.PyCompileError as e:
        errors.append((str(p), str(e)))

print(f"Compiled: {compiled} files")
print(f"Errors: {len(errors)}")
for f, e in errors:
    print('ERROR', f)
    print(e)

# run smoke test if exists
smoke = learning / '_smoke_test.py'
if smoke.exists():
    print('\nRunning smoke test:')
    try:
        res = subprocess.run([sys.executable, str(smoke)], check=False, capture_output=True, text=True)
        print('returncode=', res.returncode)
        print('--- stdout ---')
        print(res.stdout)
        print('--- stderr ---')
        print(res.stderr)
    except Exception as e:
        print('Smoke test failed to run:', e)

if errors:
    sys.exit(1)
else:
    print('No compile errors detected.')
    sys.exit(0)
