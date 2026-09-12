import json
import os
from pathlib import Path

workspace_root = Path(r"c:\Users\Forge\MyProject\LCARS-Framework")
history_root = Path(r"c:\Users\Forge\AppData\Roaming\Code\User\History")

files_to_restore = [
    "programs/learning/__init__.py",
    "programs/learning/__main__.py",
    "programs/learning/_run_compile_learning.py",
    "programs/learning/_smoke_test.py",
    "programs/learning/app.py",
    "programs/learning/apps/linguistic_matrix.py",
    "programs/learning/diag.py",
    "programs/learning/exams/A1.py",
    "programs/learning/exams/A2.py",
    "programs/learning/exams/B1.py",
    "programs/learning/exams/B2.py",
    "programs/learning/exams/C1.py",
    "programs/learning/exams/C2.py",
    "programs/learning/exams/__init__.py",
    "programs/learning/exams/modules.py",
    "programs/learning/grammar_data.py",
    "programs/learning/import_cefr.py",
    "programs/learning/interface.py",
    "programs/learning/klingon.py",
    "programs/learning/launcher.py",
    "programs/learning/learningEngine.py",
    "programs/learning/learning_engine.py",
    "programs/learning/learning_modules.py",
    "programs/learning/load_isochip.py",
    "programs/learning/logic.py",
    "programs/learning/modules.py",
    "programs/learning/progress.py",
    "programs/learning/seed/__init__.py",
    "programs/learning/seed/buildB1Chip.py",
    "programs/learning/seed/content.py",
    "programs/learning/seed/dictionary.py",
    "programs/learning/seed/exam.py",
    "programs/learning/seed/importLicensedLexicon.py",
    "programs/learning/seed/import_cefr.py",
    "programs/learning/seed/init_db.py",
    "programs/learning/seed/seed_chip_exam_pack.py",
    "programs/learning/seed/vocabulary.py",
    "programs/learning/seed_chip_exam_pack.py",
    "programs/learning/seed_new.py",
    "programs/learning/seed_vocab.py",
    "programs/learning/seed_vocab_full.py",
    "programs/learning/tracker.py",
    "programs/learning/ui/base_panel.py",
    "programs/learning/ui/dashboard.py",
    "programs/learning/ui/dictionary.py",
    "programs/learning/ui/exercises.py",
    "programs/learning/ui/grammar.py",
    "programs/learning/ui/interface.py",
    "programs/learning/ui/onboard.py",
    "programs/learning/ui/prepositions.py",
    "programs/learning/ui/progress.py",
    "programs/learning/ui/settings.py",
    "programs/learning/ui/tenses.py",
    "programs/learning/ui/widgetsExtra.py",
    "programs/learning/ui/widgets_extra.py",
    "programs/learning/ui/writing.py",
    "programs/learning/vocabulary.py",
]

# Build latest snapshot map
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
    resource_norm = resource
    if resource_norm.startswith("file:///"):
        resource_norm = resource_norm[len("file:///"):]
    resource_norm = resource_norm.replace("/", os.sep)
    if resource_norm.startswith("c%3A"):
        resource_norm = resource_norm.replace("c%3A", "c:")
    if resource_norm.startswith("c:"):
        resource_norm = resource_norm[2:]
    if "LCARS-Framework" not in resource_norm:
        continue
    rel_path = resource_norm.split("LCARS-Framework", 1)[1].lstrip(os.sep)
    rel_path = rel_path.replace(os.sep, "/")
    if rel_path not in files_to_restore:
        continue
    for entry in data.get("entries", []):
        idname = entry.get("id")
        ts = entry.get("timestamp", 0)
        if not idname:
            continue
        existing = latest.get(rel_path)
        if existing is None or existing[0] < ts:
            latest[rel_path] = (ts, history_dir, idname)

restored = []
missing = []
for rel_path in files_to_restore:
    info = latest.get(rel_path)
    dest = workspace_root / rel_path
    if info is None:
        missing.append(rel_path)
        continue
    ts, history_dir, idname = info
    src = history_dir / idname
    if not src.is_file():
        missing.append(rel_path)
        continue
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    restored.append(rel_path)

print(f"Restored {len(restored)} files")
for path in restored:
    print(path)
if missing:
    print(f"Missing {len(missing)} files")
    for path in missing:
        print(path)
