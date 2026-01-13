# Copilot Instructions for LCARS Framework

## Project Overview
- **LCARS Framework** is a modular, event-driven Python system for managing and analyzing Geant4 projects, with a PyQt6 GUI and plugin architecture.
- Major components: `lcars/core/` (core logic), `plugins/` (extensible features), `lcars/ui/` (UI), `config/` (settings), `themes/` (appearance), `tests/` (test suites).
- Key files: `launcher.py` (entry point), `lcars_system.py` (main app logic), `examples.py` (usage patterns), `PHASE_1_COMPLETE.py` (project summary).

## Architecture & Data Flow
- **Event-driven:** Central `event_bus` enables decoupled communication between plugins and core.
- **Plugin system:** Plugins are discovered in `plugins/`, each with `__init__.py`, `plugin.yaml`, and main logic file. See `plugins/detector_control/` for a template.
- **Project discovery:** `ProjectManager` scans for Geant4 projects (folders matching `ENX*` or `NCC-*`), analyzes structure, and exposes metadata to UI.
- **Task execution:** `TaskExecutor` runs external processes (e.g., Geant4 jobs) asynchronously, streaming output to the UI.
- **Configuration:** Managed via `config_manager.py`, supports JSON/YAML, schema validation, and hot-reload.

## Developer Workflows
- **Build executable:** Use `build_lcars.spec.txt` with PyInstaller. Example: `pyinstaller build_lcars.spec` (see comments in the spec file for data/resource inclusion).
- **Run tests:** Place tests in `tests/`. Run all with `python -m unittest discover tests`.
- **Debugging:** Use standalone runs of core modules (e.g., `python lcars/core/plugin_system.py`) for targeted testing.
- **Add plugin:**
  1. Create a folder in `plugins/`.
  2. Add `__init__.py`, `plugin.yaml`, and your logic file.
  3. Register events and communicate via the event bus.
- **Add UI tab:** Edit `lcars_system.py` to add a setup method and navigation button. Style with LCARS color palette.

## Conventions & Patterns
- **Event bus:** Use for all cross-component communication. Prefer events over direct calls.
- **Config:** Access via `ConfigManager`; do not hardcode paths or settings.
- **Testing:** Each core module is independently testable; integration tests in `tests/test_integration_phase1.py`.
- **Data:** Project data and executables are auto-discovered; avoid hardcoded project lists.
- **Docs:** See `docs/ARCHITECTURE.md`, `docs/DEVELOPER_GUIDE.md`, and `examples.py` for patterns and usage.

## External Dependencies
- **Geant4** (external simulation engine; must be installed separately)
- **PyQt6**, **NumPy**, **Pandas**, **Matplotlib** (Python packages; see `requirements.txt`)

## Examples
- See `examples.py` for programmatic usage: environment setup, project discovery, task execution.
- Example plugin: `plugins/detector_control/`

---
For more, see: `docs/ARCHITECTURE.md`, `docs/DEVELOPER_GUIDE.md`, `PHASE_1_COMPLETE.py`, and the `tests/` directory.
