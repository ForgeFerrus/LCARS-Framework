import json
import os
from pathlib import Path

workspace_root = Path(r"c:\Users\Forge\MyProject\LCARS-Framework")
history_root = Path(r"c:\Users\Forge\AppData\Roaming\Code\User\History")
include_prefixes = [
    "LCARS-Framework/data/",
    "LCARS-Framework/lcars/programs/english_learning/",
    "LCARS-Framework/lcars/modules/linguistic_matrix/",
    "LCARS-Framework/lcars/programs/linguistic_matrix/",
    "LCARS-Framework/programs/english_learning/",
    "LCARS-Framework/programs/learning/",
    "LCARS-Framework/lcars/modules/database_manager.py",
    "LCARS-Framework/lcars/modules/linguistic_matrix.py",
]

latest = {}
for history_dir in sorted(history_root.iterdir()):
    entries_path = history_dir / "entries.json"
    if not entries_path.is_file():
        continue
    try:
        data = json.loads(entries_path.read_text(encoding="utf-8"))
    except Exception:
        continue
    resource = data.get("resource", "")
    if not any(prefix in resource for prefix in include_prefixes):
        continue
    for entry in data.get("entries", []):
        idname = entry.get("id")
        ts = entry.get("timestamp", 0)
        if not idname:
            continue
        path = resource
        if path.startswith("file:///"):
            path = path[len("file:///"):]
        path = path.replace('/', os.sep)
        if path.startswith('c%3A'):
            path = path.replace('c%3A', 'c:')
        if path.startswith('c:'):
            path = path[2:]
        idx = path.find('LCARS-Framework')
        if idx < 0:
            continue
        rel = path[idx + len('LCARS-Framework'):].lstrip(os.sep)
        if not rel:
            continue
        rel_norm = rel.replace(os.sep, '/')
        if not any(rel_norm.startswith(prefix[len('LCARS-Framework/'):]) if prefix.endswith('/') else rel_norm == prefix[len('LCARS-Framework/'):]
                   for prefix in include_prefixes):
            continue
        if rel_norm not in latest or latest[rel_norm][0] < ts:
            latest[rel_norm] = (ts, history_dir, idname)

restored = []
for rel, (ts, history_dir, idname) in sorted(latest.items()):
    dest = workspace_root / rel.replace('/', os.sep)
    if dest.exists():
        continue
    src = history_dir / idname
    if not src.is_file():
        print(f"MISSING SNAPSHOT: {src}")
        continue
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    restored.append(rel)

print(f"Restored {len(restored)} missing files")
for path in restored:
    print(path)
