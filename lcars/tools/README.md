System Utilities (tools)

This folder contains embeddable UI widgets and a small `Dispatcher` app to host them for system-level utilities.

Quick start

Activate the venv then run the dispatcher:

```powershell
& .venv\Scripts\Activate.ps1
python tools\system_utilities.py
```

Included widgets (examples):
- Control Panel — service control and logs
- Calculator — keypad + safe evaluator + history
- Character Table — glyph reference, copy to clipboard
- On-Screen Keyboard — inserts into focused input
- Engineering Calculator — KE and momentum calculations

Config is persisted to `config/config.json` and managed by `tools/config_manager.py`.

If you want me to integrate the Dispatcher into the main launcher UI, say so and I will add an integration PR.
