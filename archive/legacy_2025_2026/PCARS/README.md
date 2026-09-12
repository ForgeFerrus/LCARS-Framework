# PCARS Package

PCARS is a separate LCARS core package built as a timeline-aware central system. It is designed to model the evolution of command architecture across eras:

- `CARS_22` — early 22nd century command shell
- `PCARS_23` — 23rd century adaptive service layer
- `LCARS_24_25` — 24th/25th century graphical LCARS orchestrator
- `TKARS_29_30` — 29th/30th century temporal command architecture

## Core concepts

- `PCARSCentral` manages services, configuration, the process manager, UI bridge, and era timeline.
- `EraTimeline` loads registered eras and keeps the active era.
- `BaseEra` defines the era contract and feature execution.

## Usage

```python
from PCARS import PCARSCentral
from pathlib import Path

central = PCARSCentral(Path("PCARS/config.json"))
central.boot()
central.select_era("CARS_22")
print(central.feature("command_console"))
```
