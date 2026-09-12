# Configuration store for PCARS.

import json
from pathlib import Path
from typing import Any


class ConfigStore:
    def __init__(self, path: Path) -> None:
        self.Path = path
        self.Data: dict[str, Any] = {}

    def Load(self) -> None:
        if self.Path.exists():
            self.Data = json.loads(self.Path.read_text(encoding="utf-8"))
        else:
            self.Data = {}

    def Save(self) -> None:
        self.Path.parent.mkdir(parents=True, exist_ok=True)
        self.Path.write_text(json.dumps(self.Data, indent=2), encoding="utf-8")

    def Get(self, key: str, default: Any = None) -> Any:
        return self.Data.get(key, default)

    def Set(self, key: str, value: Any) -> None:
        self.Data[key] = value
