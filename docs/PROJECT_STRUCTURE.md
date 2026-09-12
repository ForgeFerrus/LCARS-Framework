# LCARS — повна структура проєкту (читабельна версія)

Цей файл — зручна, людино‑читабельна версія структури проєкту. Вона містить три колонки: шлях, статус (Exists / MISSING) і короткий опис. Відкрийте файл і помічайте, що потрібно створити або відновити.

Legend:
- **Exists** — файл або папка вже присутні у репозиторії.
- **MISSING** — рекомендований файл/шаблон відсутній; можна створити як плейсхолдер.

Top-level files
- PROJECT: `start_lcars.py` — Exists — точка входу для LCARS launcher
- PROJECT: `requirements.txt` — Exists — список залежностей
- PROJECT: `README.md` — MISSING — основний README (рекомендую створити)

Package: `lcars/`
- `lcars/__init__.py` — Exists — пакет
- `lcars/launcher.py` — MISSING — допоміжні функції запуску
- `lcars/lcars_system.py` — MISSING — головна логіка додатку
- `lcars/lcars_data/` — Exists — ресурсні дані

`lcars/core/`
- `project_manager.py` — Exists — керування проєктами
- `task_executor.py` — Exists — виконання команд і потоків
- `storage_adapter.py` — MISSING — абстракція збереження
- `tricoder.py` — MISSING — encoder/decoder артефактів

`lcars/ui/`
- `desktop.py` — Exists — головний UI shell
- `lock_screen.py` — Exists
- `start_menu.py` — Exists
- `devworkbench/` — Exists
	- `editor.py` — MISSING
	- `preview.py` — MISSING
	- `terminal_panel.py` — MISSING
	- `workbench_layout.py` — MISSING

`lcars/ui/widgets/`
- **UI-specific elements** (buttons, frames, mini‑panels etc.) and a few
  convenience wrappers.  These are *not* full applications but building
  blocks that other panels and views can embed.  `common.py` lives here as
  a compatibility facade of frequently used widgets.
- `operations.py` — Exists
- `analytics.py` — Exists
- `terminal.py` — Exists
- `file_manager.py` — MISSING
- `settings.py` — MISSING
- `maps_widget.py` — MISSING
- `physics_widget.py` — MISSING
- `chemistry_widget.py` — MISSING
- `astronomy_widget.py` — MISSING
- `navigation_widget.py` — MISSING
- `comms_widget.py` — MISSING


## Key Directories Explained

To help orient yourself, here is a high‑level map of the main folders:

- `lcars/` – top‑level Python package containing all code. Treat it as the
  namespace root.

- `lcars/core/` – pure logic, managers and services with **no GUI
  dependencies**.  This is where business rules, task execution, project
  management, and other headless components live.

- `lcars/modules/` – reusable subsystems that may be used by both UI and
  non‑UI code (e.g. contact_db, diagnostics, network_manager).  They
  usually expose simple classes without Qt imports.

- `lcars/ui/` – everything visual. Within it:
  * `panels/` – full‑screen panels used by the central desktop (bridge,
    navigation, communications, etc.).  These are the main UI modes.
  * `views/` – smaller views or popup dialogs (start menu, system access,
    engineering view, diagnostics view).  They are often embedded inside
    panels or launched standalone.
  * `widgets/` – elementary widgets and helpers (buttons, elbows, logs).
    Utility code like `common.py` sits here as a convenience, not as a
    standalone application.
  * `tools/` – ad‑hoc GUI utilities for developers (like the diagnostic
    scanner, health check).  These are not part of the user-facing
    desktop but help during development.

- `programs/` – lightweight standalone applications that can be launched
  from the LCARS launcher or run by themselves.  They are mostly simple
  PyQt6 scripts (not part of the core package) and use the `programs/`
  helper `lcars_style.py` to apply theme.

- `docs/` – documentation. `PROJECT_STRUCTURE.md` (this file) is the
  master list. Other docs explain architecture, UI plans, and developer
  guides.

- `tests/` – unit and visual tests. Use `python -m unittest` to run them.

- `tools/` – command‑line utilities for maintenance and analysis (code
  scanner, builder scripts).

- `plugins/` – extensible plugins. Each plugin lives in its own folder
  with a manifest and logic.  The system loads them dynamically.

- `resources/`, `data/`, `archive/` – static assets, sample projects, and
  historical data; not code.

By following this map you can quickly tell whether a file is part of the
UI, a backend module, or just a development helper.

`lcars/themes/`
- `lcars_palette.py` — Exists
- `theme_presets.yaml` — MISSING

`lcars/modules/`
- `lock_screen.py` — Exists (shim/wrapper)

`lcars/onboard/`
- `agent.py` — MISSING — local agent API & attestation
- `agent_cli.py` — MISSING
- `agent_service.py` — MISSING

`lcars/storage/`
- `tricoder.py` — MISSING
- `object_store.py` — MISSING

`platform/`
- `bios/` — MISSING (profiles, tools)
- `uefi/` — MISSING (profiles, tools)

`specs/`, `hw/`, `fpga/`, `rtl/` — optional hardware design directories (MISSING)

`data/`
- `projects/` — Exists — per-project folders
- `archive/` — Exists
- `backups/` — MISSING

`resources/`
- `lcars_assets/` — Exists — wallpapers, icons, fonts (many files present)

`docs/`
- `desktop_ui_plan.md` — Exists
- `desktop_file_structure.md` — Exists
- `README_UI.md` — MISSING — short UI guide (recommended)
- `ARCHITECTURE.md` — MISSING
- `DEVELOPER_GUIDE.md` — MISSING

`tests/`
- `test_project_manager.py` — MISSING
- `test_task_executor.py` — MISSING
- `test_tricoder.py` — MISSING
- `e2e/test_edit_preview_flow.py` — MISSING

`scripts/`
- `repair_missing.py` — MISSING
- `build_release.py` — MISSING
- `generate_assets_index.py` — MISSING

`tools/`
- `configs.py` — MISSING
- `generate_thumbs.py` — MISSING

`plugins/`
- `<plugin_name>/` — template
	- `__init__.py` — MISSING
	- `plugin.yaml` — MISSING

`lcars/security/`
- `secrets.example.env` — Exists
- `vault/` — Exists (instructions only — DO NOT COMMIT KEYS)

`logs/`
- `audit.log` — MISSING
- `recovery.log` — MISSING
- `.gitkeep` — MISSING (recommended)

Other recommended files at repo root
- `.gitignore` — MISSING
- `LICENSE` — MISSING
- `pyproject.toml` or `setup.py` — MISSING

---

