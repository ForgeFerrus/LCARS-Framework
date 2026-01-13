import os
import sys
import subprocess
from pathlib import Path

# Ensure UTF-8 output to handle Unicode characters in scripts
sys.stdout.reconfigure(encoding='utf-8')

# Base directory for the archive
base_dir = Path(r"c:\Users\Forge\MyProject\LCARS-Framework\archive")
# Collect all .py files recursively, excluding this diagnostic script
prototypes = [p.relative_to(base_dir).as_posix() for p in base_dir.rglob('*.py') if p.name != Path(__file__).name]

print(f"Checking {len(prototypes)} Python files in {base_dir}...")

# Prepare environment for subprocesses to enforce UTF-8 encoding
env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"

for proto in prototypes:
    file_path = base_dir / proto
    if not file_path.exists():
        print(f"[MISSING] {proto}")
        continue
    
    # Run py_compile for syntax check
    try:
        subprocess.check_output([sys.executable, "-m", "py_compile", str(file_path)], stderr=subprocess.STDOUT, env=env)
        print(f"[OK] {proto} - Syntax and basic imports are fine")
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] {proto} - Compile error:")
        print(e.output.decode('utf-8', errors='replace'))

print("\nDetailed Execution Check (first 2 seconds check):")
for proto in prototypes:
    file_path = base_dir / proto
    # Try to execute and check if it gets past the imports
    try:
        proc = subprocess.Popen([sys.executable, str(file_path)], cwd=base_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        try:
            # Wait a bit for it to crash due to import/name errors
            stdout, stderr = proc.communicate(timeout=2)
            if proc.returncode != 0:
                print(f"[FAIL] {proto} - Execution error:")
                print(stderr)
            else:
                print(f"[OK?] {proto} - Process exited with 0 (maybe prompt/check mode?)")
        except subprocess.TimeoutExpired:
            proc.kill()
            print(f"[LIVE] {proto} - Seems to run (timed out without crash)")
    except Exception as e:
        print(f"[ERROR] {proto} - {str(e)}")
