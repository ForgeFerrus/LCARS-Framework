import json
import os
from pathlib import Path

history_root = Path(r"c:\Users\Forge\AppData\Roaming\Code\User\History")
core_FILES = []
for history_dir in sorted(history_root.iterdir()):
    entries_path = history_dir / "entries.json"
    if not entries_path.is_file():
        continue
    try:
        data = json.loads(entries_path.read_text(encoding="utf-8"))
    except Exception:
        continue
    resource = data.get("resource", "")
    if "LCARS-Framework/lcars/core/" not in resource and "LCARS-Framework\\lcars\\core\\" not in resource:
        continue
    for entry in data.get("entries", []):
        idname = entry.get("id")
        if not idname:
            continue
        core_FILES.append((resource, history_dir.name, idname))
print(f"found {len(core_FILES)} snapshots")
missing = [item for item in core_FILES if not (Path(history_root) / item[1] / item[2]).is_file()]
print(f"missing {len(missing)}")
for item in missing[:20]:
    print(item)
