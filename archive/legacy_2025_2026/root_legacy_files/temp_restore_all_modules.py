import json
import os
from pathlib import Path

workspace_root = Path(r"c:\Users\Forge\MyProject\LCARS-Framework")
history_root = Path(r"c:\Users\Forge\AppData\Roaming\Code\User\History")
prefixes = [
    "LCARS-Framework/plugins/",
    "LCARS-Framework/programs/",
    "LCARS-Framework/scripts/",
    "LCARS-Framework/tools/",
    "LCARS-Framework/lcars/",
    "LCARS-Framework/config/",
    "LCARS-Framework/resources/",
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
    if not any(prefix in resource for prefix in prefixes):
        continue
    for entry in data.get("entries", []):
        idname = entry.get("id")
        ts = entry.get("timestamp", 0)
        if not idname:
            continue
        # Normalize file URI to relative workspace path
        resource_path = resource
        if resource_path.startswith("file:///"):
            resource_path = resource_path[len("file:///"):]
        resource_path = resource_path.replace("/", os.sep)
        if resource_path.startswith("c%3A"):
            resource_path = resource_path.replace("c%3A", "c:")
        if resource_path.startswith("c:"):
            resource_path = resource_path[2:]
        idx = resource_path.find("LCARS-Framework")
        if idx >= 0:
            rel_path = resource_path[idx + len("LCARS-Framework"):]
        else:
            continue
        rel_path = rel_path.lstrip(os.sep)
        if not rel_path:
            continue
        rel_path_norm = rel_path.replace(os.sep, '/')
        if any(rel_path_norm.startswith(prefix[len("LCARS-Framework/"):]) for prefix in prefixes):
            if rel_path not in latest or latest[rel_path][0] < ts:
                latest[rel_path] = (ts, history_dir, idname)

restored = []
for rel_path, (ts, history_dir, idname) in sorted(latest.items()):
    src = history_dir / idname
    if not src.is_file():
        print(f"MISSING SNAPSHOT: {src}")
        continue
    dest = workspace_root / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    restored.append(rel_path)

print(f"Restored {len(restored)} files")
for path in restored[:200]:
    print(path)
if len(restored) > 200:
    print(f"...and {len(restored)-200} more files")
