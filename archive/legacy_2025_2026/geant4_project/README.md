# Geant4 Project Workspace

This folder isolates Geant4-specific assets from the LCARS framework. Use it to keep all simulation code, configs, and outputs together.

## Layout
- `src/` — Geant4 application sources, macros, CMakeLists (if used).
- `config/` — runtime configs, environment setups, geometry/material definitions.
- `data/` — input datasets, geometry files, cross-section data (do not commit large binaries unless needed).
- `build/` — local build/output artifacts (PyInstaller, CMake, or Geant4 build trees).
- `scripts/` — utility scripts for setup, runs, and packaging.
- `docs/` — notes, runbooks, and experiment logs.
- `logs/` — runtime logs and job outputs.

## Notes
- LCARS integration hooks live in the framework under `lcars/core/` (e.g., `geant4_build.py`, `geant4_wrapper.py`). Keep those in place; only project-specific payloads should live here.
- If you move an existing Geant4 project (ENX*/NCC-*), drop the project folder inside `data/` or `src/` and update any paths referenced by LCARS UI panels.
- Prefer relative paths from this folder when wiring run/build commands to avoid scattering absolute paths.
