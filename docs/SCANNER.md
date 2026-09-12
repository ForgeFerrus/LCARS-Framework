# Scanner Subsystem (LCARS)

Overview
--------
This repository now includes a unified Scanner Subsystem located in
`lcars/system/scanner_system.py`. It provides a small `BaseScanner`
abstraction and a `ScannerRegistry` used to register and discover
scanner implementations.

Built-in adapters
-----------------
- `lcars.system.scanner_adapters.odn_adapter` — exposes the existing
  `lcars.system.odn.scanner` telemetry as the `odn` scanner.
- `lcars.system.scanner_adapters.media_adapter` — scans common media
  folders and reports audio/video files as `media_scanner`.
- `lcars.system.scanner_adapters.wifi_adapter` — a conservative,
  non-privileged Wi‑Fi scanner stub (`wifi_scanner`).

Program and UI integration
--------------------------
- `programs/scanner/engine.py` provides `ScannerEngine` used by UI
  components (for example `lcars.ui.widgets.scanner.ScannerWidget`).
- `programs/scanner.py` is a small CLI to list and run registered
  scanners:

```bash
python programs/scanner.py --list
python programs/scanner.py --scan odn --json
```

Developer notes
---------------
- Adapters register themselves at import time. Import
  `lcars.system.scanner_adapters` to ensure built-ins are loaded.
- To add a new scanner implement `BaseScanner` and register it with
  `ScannerRegistry.register(name, instance)` (or use
  `register_scanner()` decorator in `scanner_system.py`).

Cleaning strategy
-----------------
We intentionally created adapters that centralise scanning logic. The
original per-program scanner files remain as compatibility wrappers.
If you want, I can replace or remove old entry scripts (for example
`programs/wifi_scanner.py`) once you confirm it's safe to do so.
