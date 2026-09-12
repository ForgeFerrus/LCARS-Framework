import json
import os
from pathlib import Path

workspace_root = Path(r"c:\Users\Forge\MyProject\LCARS-Framework")
history_root = Path(r"c:\Users\Forge\AppData\Roaming\Code\User\History")

core_resources = {}
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
        ts = entry.get("timestamp", 0)
        if not idname:
            continue
        if resource.startswith("file:///"):
            resource_path = resource[len("file:///"):]
        else:
            resource_path = resource
        resource_path = resource_path.replace("/", os.sep)
        if resource_path.startswith("c%3A"):
            resource_path = resource_path.replace("c%3A", "c:")
        if resource_path.startswith("c:"):
            resource_path = resource_path[2:]
        idx = resource_path.find("LCARS-Framework")
        if idx >= 0:
            rel_path = resource_path[idx + len("LCARS-Framework"):]
        else:
            rel_path = resource_path
        rel_path = rel_path.lstrip("\\/")
        if not rel_path:
            continue
        # Choose latest timestamp per resource
        existing = core_resources.get(rel_path)
        if existing is None or existing[0] < ts:
            core_resources[rel_path] = (ts, history_dir, idname)

restored = []
for rel_path, (ts, history_dir, idname) in sorted(core_resources.items()):
    src = history_dir / idname
    if not src.is_file():
        print(f"ERROR: missing snapshot file {src}")
        continue
    dest = workspace_root / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    restored.append(rel_path)

# Ensure boot and odn packages exist for Python imports if needed
for extra_pkg in [workspace_root / "lcars" / "core" / "boot", workspace_root / "lcars" / "core" / "odn"]:
    if extra_pkg.exists() and extra_pkg.is_dir():
        init_file = extra_pkg / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Package initializer\n", encoding="utf-8")
            restored.append(str(init_file.relative_to(workspace_root)))

print(f"Restored {len(restored)} files under {workspace_root}")
for path in restored:
    print(path)
