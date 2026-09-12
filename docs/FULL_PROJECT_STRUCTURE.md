LCARS — Full Project Structure and Implementation Plan

This file supplements `PROJECT_STRUCTURE.md` with a concrete, actionable tree, priorities, and an implementation roadmap. Use it as the authoritative plan for the recovery and next development sprints.

Legend:
- Exists — file/directory already in repo
- MISSING — recommended file not present
- Priority: (H) High, (M) Medium, (L) Low

ROOT (H)
- start.py (Exists) — launcher
- requirements.txt (Exists)
- README.md (Exists) — update from current snapshot
- .gitignore (MISSING) (H)
- LICENSE (MISSING) (M)
- pyproject.toml / setup.py (MISSING) (M)

lcars/ (H)
- __init__.py (Exists)
- launcher.py (MISSING) (H)
- lcars_system.py (MISSING) (H)
- lcars_data/ (Exists)

lcars/core/ (H)
- __init__.py (Exists)
- project_manager.py (Exists)
- task_executor.py (Exists)
- config_manager.py (Exists)
- event_bus.py (Exists)
- storage_adapter.py (MISSING) (H)
- tricoder.py (MISSING) (M)
- db/
  - schema.sql (MISSING) (M)
  - adapter_sqlite.py (MISSING) (M)

lcars/ui/ (H)
- __init__.py (Exists)
- desktop.py (Exists)
- lock_screen.py (Exists)
- start_menu.py (Exists)
- main_window.py (MISSING) (H)
- devworkbench/
  - __init__.py (Exists)
  - editor.py (MISSING) (M)
  - preview.py (MISSING) (M)
  - terminal_panel.py (MISSING) (M)
  - workbench_layout.py (MISSING) (M)

lcars/ui/widgets/ (H)
- __init__.py (Exists)
- common.py (Exists)
- operations.py (Exists)
- analytics.py (Exists)
- terminal.py (Exists)
- file_manager.py (MISSING) (H)
- settings.py (MISSING) (M)
- maps_widget.py (MISSING) (L)
- physics_widget.py (MISSING) (L)
- chemistry_widget.py (MISSING) (L)
- astronomy_widget.py (MISSING) (L)
- navigation_widget.py (MISSING) (L)
- comms_widget.py (MISSING) (M)

lcars/themes/ (M)
- __init__.py (Exists)
- lcars_palette.py (Exists)
- theme_presets.yaml (MISSING) (M)
- resources/fonts/ — ensure fonts available (Exists?)

lcars/modules/ (H)
- __init__.py (Exists)
- lock_screen.py (Exists)
- start_menu.py (modules variant) (Exists)

lcars/onboard/ (M)
- __init__.py (Exists)
- agent.py (MISSING) (M)
- agent_cli.py (MISSING) (M)
- agent_service.py (MISSING) (M)

lcars/storage/ (M)
- __init__.py (Exists)
- tricoder.py (MISSING) (M)
- object_store.py (MISSING) (M)

platform/ (L)
- bios/ (MISSING) — README, bios-profiles/, tools/
- uefi/ (MISSING) — README, uefi-profiles/, scripts/, keys/

specs/, hw/, fpga/, rtl/ (L) — optional hardware artifacts

data/ (H)
- projects/ (Exists)
- archive/ (Exists)
- backups/ (MISSING) (M)

resources/ (H)
- lcars_assets/ (Exists)
- fonts/ (Exists?) — check and add fallbacks

docs/ (H)
- desktop_ui_plan.md (Exists)
- desktop_file_structure.md (Exists)
- PROJECT_PLAN.md (Exists)
- FULL_PROJECT_STRUCTURE.md (this file)
- ARCHITECTURE.md (MISSING) (H)
- DEVELOPER_GUIDE.md (MISSING) (H)
- README_UI.md (MISSING) (M)

tests/ (H)
- __init__.py (MISSING) (H)
- test_project_manager.py (MISSING) (H)
- test_task_executor.py (MISSING) (H)
- test_tricoder.py (MISSING) (M)
- e2e/test_edit_preview_flow.py (MISSING) (M)

scripts/ (M)
- repair_missing.py (MISSING) (H)
- build_release.py (MISSING) (M)
- generate_assets_index.py (MISSING) (M)

tools/ (M)
- validate_configs.py (MISSING) (M)
- generate_thumbs.py (MISSING) (M)

plugins/ (M)
- detector_control/ (Exists)
- template_plugin/ (MISSING) (M)

lcars/security/ (H)
- secrets.example.env (Exists)
- vault/ (Exists) — instructions only

logs/ (H)
- audit.log (MISSING) (H)
- recovery.log (MISSING) (H)
- .gitkeep (MISSING) (H)

ci/ infra (M)
- .github/workflows/ci.yml (MISSING) (M)
- docker/ (MISSING) (M)


Implementation Roadmap (detailed actions)

Phase 0 — Audit & Safety (complete)
- Consolidate docs (`PROJECT_PLAN.md`, `PROJECT_STRUCTURE.md`, `FULL_PROJECT_STRUCTURE.md`)
- Mark prohibited features (already in docs)

Phase 1 — Recovery Sprint (H)
Goal: Boot desktop to Mission Hub with minimal failures.
Tasks:
- Create minimal placeholders for: `lcars/ui/widgets/file_manager.py`, `lcars/ui/main_window.py`, `lcars/devworkbench/editor.py`, `lcars/onboard/agent.py`, `.gitignore`, `logs/.gitkeep`.
- Run `python start.py`, capture import/runtime errors, fix smallest issues (resilient imports, font fallbacks).
Deliverable: `start.py` boots to Lock → Desktop (placeholders visible if modules missing).

Phase 2 — Core Services (H→M)
Goal: Stable project & task execution pipeline.
Tasks:
- Implement `storage_adapter.py` (local SQLite adapter) and register in bootstrap.
- Implement basic `tricoder.py` to encode artifacts with hashes and store metadata.
- Add unit tests for `ProjectManager` and `TaskExecutor`.
Deliverable: Build/run of a sample project via `OperationsWidget` with logs.

Phase 3 — Developer Workbench PoC (M)
Goal: Live edit → preview flow.
Tasks:
- Editor UI + preview subprocess with IPC; hot-reload minimal widget.
- Terminal integration to run `TaskExecutor` tasks from workbench.
Deliverable: Demo where editing a small widget updates preview.

Phase 4 — Projects & Journal (M)
Goal: Persistent project DB and journal.
Tasks:
- DB schema, Journal API, Archive/restore flows.
- UI: Dashboard & timeline.
Deliverable: Create/Archive/Restore a sample project with logs and journal entries.

Phase 5 — Security & Ops (M)
Goal: Signing, secrets guidance, operational scripts.
Tasks:
- Add `ARCHITECTURE.md` and `DEVELOPER_GUIDE.md`.
- Add sample scripts for BIOS/UEFI workflows (docs + templates).
Deliverable: Documentation + signing pipeline example.

Phase 6 — Tests, CI & HW (M→L)
Goal: CI for code and RTL sim.
Tasks:
- Add GitHub Actions for tests and linting.
- Add RTL simulation CI job if hardware files exist.
Deliverable: Passing CI and test coverage baseline.

Next steps — pick an action
- Reply `create top` — I will scaffold the high-priority placeholders and run `start.py` to capture errors.
- Reply `create all` — I will scaffold all missing placeholders (long operation).
- Or specify exact files to create (comma-separated). 

Notes & constraints
- I will not commit secrets or private keys. `vault/` remains instructions-only.
- Placeholder files are minimal, safe stubs intended to let the app start; they will be replaced by full implementations later.

