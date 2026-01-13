LCARS devtools UI Designer (prototype)

Purpose
- Lightweight in-repo UI designer to prototype LCARS-style screens on a black canvas.
- Allows adding basic widgets, moving them, editing properties, saving/loading JSON layouts, and generating a Python scaffold.

How to run
- Activate your project's virtualenv (the one with PyQt6 installed):

  PowerShell:
    & 'C:\Users\Forge\MyProject\Geant4\Enterprise\.venv\Scripts\Activate.ps1'
    python devtools\ui_designer.py

  CMD:
    C:\> C:\Users\Forge\MyProject\Geant4\Enterprise\.venv\Scripts\activate.bat
    C:\> python devtools\ui_designer.py

- You can pass a saved layout to open on startup:
    python devtools\ui_designer.py path\to\layout.json

Requirements
- PyQt6 must be installed in the active virtualenv.

Notes
- This is an MVP; it is intentionally small and easy to extend.
- Generated Python is a scaffold — you still need to wire signals and integrate it into your application.
- Next improvements planned: grid/snap, property types, signal wiring UI, undo/redo, tests.
