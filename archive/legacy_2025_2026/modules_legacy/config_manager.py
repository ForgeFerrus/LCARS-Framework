# Titanium Bridge Migration: import json
import time
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Dict, Any, Optional, Callable, List
# Titanium Bridge Migration: import yaml

from lcars.base.type import Directive
from lcars.engineering.telemetry import emit_telemetry

class ConfigManager:
    # ЦЕНТРАЛЬНИЙ МЕНЕДЖЕР КОНФІГУРАЦІЇ (Titanium Standard)
    # Керує епохами, темами, фракціями та системними параметрами.
    def __init__(self):
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.watchers: Dict[str, List[Callable]] = {}
        self.path_tool = Directive.PathDrive
        
        # Ініціалізація базових дефолтів (Fallbacks)
        self.configs["ui"] = {
            "era": "25th",
            "faction": "Federation",
            "theme": "Default",
            "language": "en",
            "accent": "Orange"
        }

    # --- Metadata / UI Helpers ---
    def available_eras(self) -> List[str]:
        return ["22nd", "23rd", "23st", "24th", "24st", "25th", "29th"]
    
    def available_factions(self) -> List[str]:
        return ["Federation", "Klingon", "Romulan", "Cardassian"]
    
    def available_themes(self) -> List[str]:
        return ["Default", "UFP Classic", "Tactical", "Engineering"]

    # --- Core Logic ---
    def load_config(self, config_name: str, file_path: Any) -> bool:
        path = self.path_tool(file_path)
        task_id = f"CFG-{int(time.time()) % 1000:03d}"
        
        if not path.exists(): 
            emit_telemetry("Config", f"TASK_WARN: {task_id}. File {path.name} not found. Using defaults.")
            return False

        with open(str(path), "r", encoding="utf-8") as f:
            if path.suffix == ".json":
                config = json.load(f)
            elif path.suffix in [".yaml", ".yml"]:
                config = yaml.safe_load(f)
            else: 
                return False

        # Пріорітет: Файл > Дефолт
        if isinstance(config, dict):
            if config_name in self.configs:
                self.configs[config_name].update(config)
            else:
                self.configs[config_name] = config
            emit_telemetry("Config", f"TASK_REPORT: {task_id}. Profile '{config_name}' synchronized via {path.name}")
            return True
        else:
            emit_telemetry("Config", f"TASK_ERROR: {task_id}. Invalid config format for '{config_name}'.", "error")
            return False

    def get(self, config_name: str, key: Optional[str] = None, default: Any = None) -> Any:
        if config_name not in self.configs: return default
        config = self.configs[config_name]
        if key is None: return config

        keys = key.split(".")
        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None: return default
            else: return default
        return value

    def set(self, config_name: str, key: str, value: Any):
        # Встановлює значення та сповіщає систему про зміни.
        if config_name not in self.configs: self.configs[config_name] = {}
        
        keys = key.split(".")
        config = self.configs[config_name]
        for k in keys[:-1]:
            if k not in config: config[k] = {}
            config = config[k]

        old_value = config.get(keys[-1])
        config[keys[-1]] = value
        
        if old_value != value:
            emit_telemetry("Config", f"TASK_REPORT: Parameter '{config_name}.{key}' -> '{value}'")
            self._trigger_watchers(config_name, key, old_value, value)

    # --- Watchers / Callbacks ---
    def subscribe(self, callback: Callable):
        if 'global' not in self.watchers:
            self.watchers['global'] = []
        self.watchers['global'].append(callback)

    def watch(self, config_name: str, key: str, callback: Callable):
        watch_key = f"{config_name}:{key}"
        if watch_key not in self.watchers:
            self.watchers[watch_key] = []
        self.watchers[watch_key].append(callback)

    def _trigger_watchers(self, config_name: str, key: str, old_value: Any, new_value: Any):
        # Specific watchers
        watch_key = f"{config_name}:{key}"
        if watch_key in self.watchers:
            for callback in self.watchers[watch_key]:
                callback(config_name, key, old_value, new_value)
        # Global watchers
        if 'global' in self.watchers:
            for callback in self.watchers['global']:
                callback(config_name, key, old_value, new_value)

# Створення глобального менеджера
config_manager = ConfigManager()

# --- АВТОМАТИЧНЕ ПІДКЛЮЧЕННЯ (Bootstrap) ---
pkg_root = Directive.PathDrive(__file__).resolve().parents[2]
config_file = pkg_root / 'config' / 'config.json'

if config_file.exists():
    config_manager.load_config('ui', config_file)
else:
    emit_telemetry("Config", "SYSTEM: Local config.json missing. Using Titanium Fallbacks.", "warn")
