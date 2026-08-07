# ◤ lcars/system/config.py — System Configuration Manager v44.20
# Чіп: 00-0005

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
import yaml


class ConfigManager:
    def __init__(self):
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.watchers: Dict[str, List[Callable]] = {}
        self.pathTool = Path
        self.configs["ui"] = {
            "era": "25th",
            "faction": "Federation",
            "theme": "Default",
            "language": "en",
            "accent": "Orange"
        }

    def eras(self) -> List[str]:
        return ["22nd", "23rd", "23st", "24th", "24st", "25th", "29th"]

    def factions(self) -> List[str]:
        return ["Federation", "Klingon", "Romulan", "Cardassian"]

    def themes(self) -> List[str]:
        return ["Default", "UFP Classic", "Tactical", "Engineering"]

    def load(self, name: str, filepath: Any) -> bool:
        path = self.pathTool(filepath)
        if not path.exists():
            return False
        with open(str(path), "r", encoding="utf-8") as f:
            if path.suffix == ".json":
                config = json.load(f)
            elif path.suffix in [".yaml", ".yml"]:
                config = yaml.safe_load(f)
            else:
                return False
        if isinstance(config, dict):
            if name in self.configs:
                self.configs[name].update(config)
            else:
                self.configs[name] = config
            return True
        return False

    def get(self, name: str, key: Optional[str] = None, default: Any = None) -> Any:
        if name not in self.configs:
            return default
        config = self.configs[name]
        if key is None:
            return config
        keys = key.split(".")
        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    def set(self, name: str, key: str, value: Any):
        if name not in self.configs:
            self.configs[name] = {}
        keys = key.split(".")
        config = self.configs[name]
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        old = config.get(keys[-1])
        config[keys[-1]] = value
        if old != value:
            self.trigger(name, key, old, value)

    def subscribe(self, callback: Callable):
        if "global" not in self.watchers:
            self.watchers["global"] = []
        self.watchers["global"].append(callback)

    def watch(self, name: str, key: str, callback: Callable):
        watchkey = f"{name}:{key}"
        if watchkey not in self.watchers:
            self.watchers[watchkey] = []
        self.watchers[watchkey].append(callback)

    def trigger(self, name: str, key: str, old: Any, new: Any):
        watchkey = f"{name}:{key}"
        if watchkey in self.watchers:
            for cb in self.watchers[watchkey]:
                cb(name, key, old, new)
        if "global" in self.watchers:
            for cb in self.watchers["global"]:
                cb(name, key, old, new)


config = ConfigManager()

pkgroot = Path(__file__).resolve().parents[2]
configfile = pkgroot / "config" / "config.json"

if configfile.exists():
    config.load("ui", configfile)


__all__ = ["ConfigManager", "config"]
