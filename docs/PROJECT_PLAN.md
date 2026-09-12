**LCARS — Project Plan & Full File Tree (summary)**

Це зведений план робіт та повне дерево проєкту у читабельному вигляді. Використовуйте цей документ як робочий план: редагуйте статуси в `PROJECT_STRUCTURE.md`, потім я створю плейсхолдери або відновлю файли за вказівками.

**Plan — Phases (high level)**
- Phase 0 — Audit & Safety: review all docs, confirm prohibited features, add `RECOVERY_LOG.md`.
- Phase 1 — Recovery & Boot: create minimal placeholders for missing UI modules (StartMenu, FileManager), run `start.py`, fix import/runtime failures, remove temporary shims once originals restored.
- Phase 2 — Core Services: finalize `ProjectManager`, `TaskExecutor`, `storage_adapter`, `tricoder` and storage APIs.
- Phase 3 — Developer Workbench: implement `devworkbench` PoC (editor, preview subprocess + IPC, terminal panel), constructor → code export flow.
- Phase 4 — Projects & Archival: project DB (SQLite), object store, archive lifecycle, backups, retention.
- Phase 5 — Security & Ops: keys, signing, Vault integration, RBAC, audit trail, recovery playbooks.
- Phase 6 — Tests & CI: unit tests, e2e smoke tests, RTL sim CI for isoline hardware, release builds.

For each phase: create tasks, add tests, and run `start.py` at end of phase to verify runtime stability.

**Key documentation to review / consolidate**
- `docs/desktop_ui_plan.md` (Exists) — UI design & flow.
- `docs/desktop_file_structure.md` (Exists) — proposed file skeleton.
- `docs/PROJECT_PLAN.md` (this file) — consolidated plan and tree.
- `archive/GLOBAL_PLAN.md` (Exists) — higher-level strategy.
- Missing but recommended: `docs/ARCHITECTURE.md`, `docs/DEVELOPER_GUIDE.md`, `docs/README_UI.md`, `docs/INSTALLATION.md`.

**Full Project Tree (annotated)**
- start.py (Exists) — launcher
- requirements.txt (Exists)
- README.md (MISSING)
- PROJECT_STRUCTURE.md (Exists)

lcars/
- __init__.py (Exists)
- launcher.py (MISSING)
- lcars_system.py (MISSING)
- lcars_data/ (Exists)

lcars/core/
- __init__.py (Exists)
- project_manager.py (Exists)
- task_executor.py (Exists)
- storage_adapter.py (MISSING)
- tricoder.py (MISSING)
- session_manager.py (Exists)
- process_supervisor.py (Exists)

lcars/ui/
- __init__.py (Exists)
- desktop.py (Exists)
- lock_screen.py (Exists)
- start_menu.py (Exists)
- devworkbench/
  - __init__.py (Exists)
  - editor.py (MISSING)
  - preview.py (MISSING)
  - terminal_panel.py (MISSING)
  - workbench_layout.py (MISSING)

lcars/ui/widgets/
- __init__.py (Exists)
- operations.py (Exists)
- analytics.py (Exists)
- terminal.py (Exists)
- file_manager.py (MISSING)
- settings.py (MISSING)
- maps_widget.py (MISSING)
- physics_widget.py (MISSING)
- chemistry_widget.py (MISSING)
- astronomy_widget.py (MISSING)
- navigation_widget.py (MISSING)
- comms_widget.py (MISSING)

lcars/themes/
- __init__.py (Exists)
- lcars_palette.py (Exists)
- theme_presets.yaml (MISSING)

lcars/modules/
- __init__.py (Exists)
- lock_screen.py (Exists)

lcars/onboard/
- __init__.py (Exists)
- agent.py (MISSING)
- agent_cli.py (MISSING)
- agent_service.py (MISSING)

lcars/storage/
- __init__.py (Exists)
- tricoder.py (MISSING)
- object_store.py (MISSING)

platform/
- bios/ (MISSING)
- uefi/ (MISSING)

specs/, hw/, fpga/, rtl/ (MISSING or partially present as notes)

data/
- projects/ (Exists)
- archive/ (Exists)
- backups/ (MISSING)

resources/
- lcars_assets/ (Exists — many images, fonts)

docs/
- desktop_ui_plan.md (Exists)
- desktop_file_structure.md (Exists)
- PROJECT_PLAN.md (this file)
- ARCHITECTURE.md (MISSING)
- DEVELOPER_GUIDE.md (MISSING)
- README_UI.md (MISSING)

tests/
- test_project_manager.py (MISSING)
- test_task_executor.py (MISSING)
- test_tricoder.py (MISSING)
- e2e/test_edit_preview_flow.py (MISSING)

scripts/
- repair_missing.py (MISSING)
- build_release.py (MISSING)
- generate_assets_index.py (MISSING)

tools/
- validate_configs.py (MISSING)
- generate_thumbs.py (MISSING)

plugins/
- detector_control/ (Exists)
- template_plugin/ (MISSING template)

lcars/security/
- secrets.example.env (Exists)
- vault/ (Exists, instructions only)

logs/
- audit.log (MISSING)
- recovery.log (MISSING)
- .gitkeep (MISSING)

repo root recommended
- .gitignore (MISSING)
- LICENSE (MISSING)
- pyproject.toml or setup.py (MISSING)

---

**Next suggested immediate actions (pick one)**
- `top` — create top-priority placeholders (`.gitignore`, `pyproject.toml`, `LICENSE`, `logs/.gitkeep`, `lcars/ui/widgets/file_manager.py`, `lcars/ui/devworkbench/editor.py`, `docs/README_UI.md`) and then run `start.py`.
- `all` — create placeholders for all MISSING entries in the tree (longer, but gives a complete skeleton).
- Or list specific files you want created now (comma-separated).

If you want, I will now create the `top` set and then run `start.py` to capture the remaining runtime errors. Reply with `top`, `all`, or a comma-separated list of file paths.
