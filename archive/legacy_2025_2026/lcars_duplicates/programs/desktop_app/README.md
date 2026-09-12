# LCARS Standalone Desktop App

This is a minimal self-contained application built from the LCARS Framework.
All of the code required to run the app lives under this directory, so you
can copy or distribute the entire folder without needing the rest of the
framework.

## Features

* Scan for Geant4 projects in the current working directory (and a hard-\
coded Enterprise path).
* Display a simple system monitor with CPU/memory/network stats.
* Play some basic LCARS sounds via the embedded `SoundManager`.

## Running

From the workspace root, execute:

```bash
python -m lcars.programs.desktop_app.main
```

Requirements: PyQt6, psutil (and optionally vispy if you want sound support).


## Structure

```
lcars/programs/desktop_app/
  main.py            # application entry point
  modules/           # copies of needed utility modules
    project_manager.py
    system_monitor.py
    sound_manager.py
  ui/                # (none yet)
```

Each module is a straight copy of its sibling in `lcars/modules` with no
external imports, so the program can run standalone.
