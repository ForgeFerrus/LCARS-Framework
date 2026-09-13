# ◤ TITANIUM SYSTEM CONFIGURATION MANAGER // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/system/config.py
# ОПИС: Центральний менеджер конфігурації LCARS Framework (ConfigManager).
#       Зберігання та управління конфігураціями UI, тем, ер, фракцій і підсистем.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Strict PascalCase, Pure Classes).
# =============================================================================

from lcars.base.type import LCARS, SystemComponent
from lcars.base.info import Version


from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class ConfigSchema:
    name: str = ""
    Name: str = ""
    required_keys: List[str] = field(default_factory=list)
    optional_keys: List[str] = field(default_factory=list)
    type_hints: Dict[str, Any] = field(default_factory=dict)
    defaults: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.Name and self.name:
            self.Name = self.name
        if not self.name and self.Name:
            self.name = self.Name

class ConfigManager(SystemComponent):
    SystemVersion = Version.Release
    Instance = None

    def __init__(self, SystemId="ConfigManager"):
        super().__init__(SystemId=SystemId)
        self.Version = Version.Release
        self.Passport = Version.Passport()
        self.Configs = {}
        self.Schemas = {}
        self.Watchers = {}
        self.PathTool = LCARS.System.Path

        # Базові налаштування за замовчуванням
        self.Configs["ui"] = {
            "era": "25th",
            "faction": "Federation",
            "theme": "Default",
            "language": "uk",
            "accent": "Orange"
        }

    @classmethod
    def GetInstance(cls):
        if cls.Instance is None:
            cls.Instance = ConfigManager()
        return cls.Instance

    def Eras(self):
        return ["22nd", "23rd", "23st", "24th", "24st", "25th", "29th", "32nd"]

    def Factions(self):
        return ["Federation", "Klingon", "Romulan", "Cardassian", "Ferengi"]

    def Themes(self):
        return ["Default", "UFP Classic", "Tactical", "Engineering", "Titan", "Klingon"]

    def RegisterSchema(self, Schema: ConfigSchema) -> None:
        SchemaName = Schema.Name or Schema.name
        self.Schemas[SchemaName] = Schema
        if SchemaName not in self.Configs and Schema.defaults:
            self.Configs[SchemaName] = dict(Schema.defaults)

    register_schema = RegisterSchema

    def Load(self, NameKey, Filepath):
        PathObj = self.PathTool(Filepath)
        if not PathObj.exists():
            return False

        ConfigData = None
        Suffix = str(PathObj.suffix).lower()
        if Suffix == ".json":
            JsonModule = LCARS.Import("json")
            with open(str(PathObj), "r", encoding="utf-8") as F:
                ConfigData = JsonModule.load(F)
        elif Suffix in [".yaml", ".yml"]:
            YamlModule = LCARS.Yaml
            with open(str(PathObj), "r", encoding="utf-8") as F:
                ConfigData = YamlModule.safe_load(F)
        else:
            return False

        if isinstance(ConfigData, dict):
            if NameKey in self.Configs:
                self.Configs[NameKey].update(ConfigData)
            else:
                self.Configs[NameKey] = ConfigData
            return True
        return False

    load_config = Load

    def Get(self, NameKey, PropertyKey=None, DefaultValue=None):
        if NameKey not in self.Configs:
            return DefaultValue
        TargetConfig = self.Configs[NameKey]
        if PropertyKey is None:
            return TargetConfig
        KeysList = str(PropertyKey).split(".")
        CurrentVal = TargetConfig
        for K in KeysList:
            if isinstance(CurrentVal, dict):
                CurrentVal = CurrentVal.get(K)
                if CurrentVal is None:
                    return DefaultValue
            else:
                return DefaultValue
        return CurrentVal

    get = Get

    def Set(self, NameKey, PropertyKey, Value):
        if NameKey not in self.Configs:
            self.Configs[NameKey] = {}
        KeysList = str(PropertyKey).split(".")
        TargetConfig = self.Configs[NameKey]
        for K in KeysList[:-1]:
            if K not in TargetConfig:
                TargetConfig[K] = {}
            TargetConfig = TargetConfig[K]
        OldValue = TargetConfig.get(KeysList[-1])
        TargetConfig[KeysList[-1]] = Value
        if OldValue != Value:
            self.Trigger(NameKey, PropertyKey, OldValue, Value)

    set = Set

    def Subscribe(self, Callback):
        if "global" not in self.Watchers:
            self.Watchers["global"] = []
        self.Watchers["global"].append(Callback)

    def Watch(self, NameKey, PropertyKey, Callback):
        WatchKeyStr = f"{NameKey}:{PropertyKey}"
        if WatchKeyStr not in self.Watchers:
            self.Watchers[WatchKeyStr] = []
        self.Watchers[WatchKeyStr].append(Callback)

    watch = Watch

    def PrintConfig(self, NameKey: str) -> None:
        cfg = self.Get(NameKey)
        if isinstance(cfg, dict):
            for k, v in cfg.items():
                print(f"    {k}: {v}")
        else:
            print(f"    {NameKey}: {cfg}")

    print_config = PrintConfig

    def Trigger(self, NameKey, PropertyKey, OldValue, NewValue):
        WatchKeyStr = f"{NameKey}:{PropertyKey}"
        if WatchKeyStr in self.Watchers:
            for Cb in self.Watchers[WatchKeyStr]:
                if callable(Cb):
                    Cb(NameKey, PropertyKey, OldValue, NewValue)
        if "global" in self.Watchers:
            for Cb in self.Watchers["global"]:
                if callable(Cb):
                    Cb(NameKey, PropertyKey, OldValue, NewValue)

# Глобальний екземпляр конфігурації
ConfigInstance = ConfigManager.GetInstance()

# Спроба завантажити базовий конфіг проєкту
PkgRoot = LCARS.System.Path(__file__).resolve().parents[2]
ConfigFile = PkgRoot / "config" / "config.json"
if ConfigFile.exists():
    ConfigInstance.Load("ui", ConfigFile)

Config = ConfigManager

__all__ = ["ConfigSchema", "ConfigManager", "Config", "ConfigInstance"]
