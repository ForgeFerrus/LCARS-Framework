#!/usr/bin/env python3
"""
Merge programs/english_learning into programs/learning safely.
Creates backups for conflicting files under programs/learning/merged_backups.
"""
from pathlib import Path
import filecmp
import shutil
import sys
import argparse

root = Path(__file__).resolve().parent.parent

parser = argparse.ArgumentParser(description='Merge two folders under the project root')
parser.add_argument('--src', default='programs/english_learning', help='source relative path from project root')
parser.add_argument('--dst', default='programs/learning', help='destination relative path from project root')
args = parser.parse_args()

src = root / args.src
dst = root / args.dst
backup_root = dst / 'merged_backups'

moved = []
skipped = []
conflicts = []
errors = []

if not src.exists():
    print(f"Source not found: {src}")
    sys.exit(1)

dst.mkdir(parents=True, exist_ok=True)
backup_root.mkdir(parents=True, exist_ok=True)

for p in src.rglob('*'):
    if p.is_dir():
        continue
    rel = p.relative_to(src)
    target = dst / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        if not target.exists():
            shutil.move(str(p), str(target))
            moved.append(str(rel))
        else:
            same = False
            try:
                same = filecmp.cmp(str(p), str(target), shallow=False)
            except Exception:
                same = False
            if same:
                try:
                    p.unlink()
                    skipped.append(str(rel))
                except Exception as e:
                    errors.append((str(rel), f"unlink error: {e}"))
            else:
                backup_path = backup_root / rel
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(p), str(backup_path))
                try:
                    p.unlink()
                except Exception as e:
                    errors.append((str(rel), f"unlink after backup error: {e}"))
                conflicts.append((str(rel), str(target), str(backup_path)))
    except Exception as e:
        errors.append((str(rel), str(e)))

# remove empty directories under src
for d in sorted([d for d in src.rglob('*') if d.is_dir()], key=lambda x: -len(str(x))):
    try:
        d.rmdir()
    except Exception:
        pass

print("Merge complete.")
print(f"Moved files: {len(moved)}")
for i in moved:
    print("MOVED", i)
print(f"Skipped identical files (removed from source): {len(skipped)}")
for s in skipped:
    print("SKIPPED", s)
print(f"Conflicts (backed up from source): {len(conflicts)}")
for rel, t, b in conflicts:
    print("CONFLICT", rel, "->", t, "backup->", b)
if errors:
    print(f"Errors: {len(errors)}")
    for rel, e in errors:
        print("ERROR", rel, e)
print("Backups stored under:", backup_root)
print("Source directory processed; empty subdirs removed where possible.")
