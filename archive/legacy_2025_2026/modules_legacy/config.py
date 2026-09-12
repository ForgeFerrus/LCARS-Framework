"""
Config Manager ╨┤╨╗╤П LCARS Enterprise
====================================

╨б╨╕╤Б╤В╨╡╨╝╨░ ╨║╨╡╤А╤Г╨▓╨░╨╜╨╜╤П ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤Ф╤О: ╨╖╨░╨▓╨░╨╜╤В╨░╨╢╨╡╨╜╨╜╤П, ╨▓╨░╨╗╤Ц╨┤╨░╤Ж╤Ц╤П, ╨│╨░╤А╤П╤З╨╛╤Ч ╨┐╨╡╤А╨╡╨╖╨░╨▓╨░╨╜╤В╨░╨╢╨╡╨╜╨╜╤П.
"""

# Titanium Bridge Migration: import json
import logging
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Dict, Any, Optional, Union, Callable, List
# Titanium Bridge Migration: from dataclasses import dataclass, asdict
# Titanium Bridge Migration: import yaml

logger = logging.getLogger(__name__)


# тХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХР
# ╨Ъ╨Ю╨Э╨д╨Ж╨У╨г╨а╨Р╨ж╨Ж╨Щ╨Э╨Р ╨б╨е╨Х╨Ь╨Р
# тХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХР

@dataclass
class ConfigSchema:
    """╨б╤Е╨╡╨╝╨░ ╨┤╨╗╤П ╨▓╨░╨╗╤Ц╨┤╨░╤Ж╤Ц╤Ч ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤Ч"""
    
    name: str
    required_keys: List[str] = None
    optional_keys: List[str] = None
    type_hints: Dict[str, type] = None
    defaults: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.required_keys is None:
            self.required_keys = []
        if self.optional_keys is None:
            self.optional_keys = []
        if self.type_hints is None:
            self.type_hints = {}
        if self.defaults is None:
            self.defaults = {}
    
    def validate(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        ╨Т╨░╨╗╤Ц╨┤╤Г╨▓╨░╤В╨╕ ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤О.
        
        Returns:
            (valid, message)
        """
        # ╨Я╨╡╤А╨╡╨▓╤Ц╤А╨╕╨╝╨╛ ╨╛╨▒╨╛╨▓'╤П╨╖╨║╨╛╨▓╤Ц ╨║╨╗╤О╤З╤Ц
        for key in self.required_keys:
            if key not in config:
                return False, f"Missing required key: {key}"
        
        # ╨Я╨╡╤А╨╡╨▓╤Ц╤А╨╕╨╝╨╛ ╤В╨╕╨┐╨╕
        for key, expected_type in self.type_hints.items():
            if key in config:
                if not isinstance(config[key], expected_type):
                    return (
                        False,
                        f"Invalid type for '{key}': expected {expected_type.__name__}, "
                        f"got {type(config[key]).__name__}"
                    )
        
        return True, "Valid"


# тХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХР
# CONFIG MANAGER
# тХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХР

class ConfigManager:
    """
    ╨Ь╨╡╨╜╨╡╨┤╨╢╨╡╤А ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤Ч ╨┤╨╗╤П LCARS Enterprise.
    
    ╨д╤Г╨╜╨║╤Ж╤Ц╤Ч:
    тАв ╨Ч╨░╨▓╨░╨╜╤В╨░╨╢╨╡╨╜╨╜╤П ╨╖ JSON/YAML
    тАв ╨Т╨░╨╗╤Ц╨┤╨░╤Ж╤Ц╤П ╨┐╨╛ ╤Б╤Е╨╡╨╝╤Ц
    тАв ╨У╨░╤А╤П╤З╨░ ╨┐╨╡╤А╨╡╨╖╨░╨▓╨░╨╜╤В╨░╨╢╨╡╨╜╨╜ (hot-reload)
    тАв ╨б╨┐╨╛╤Б╤В╨╡╤А╨╡╨╢╨╡╨╜╨╜╤П ╨╖╨░ ╨╖╨╝╤Ц╨╜╨░╨╝╨╕
    тАв ╨Ъ╨╛╨╝╨┐╨╛╨╖╨╕╤Ж╤Ц╤П (env + default + user config)
    """
    
    def __init__(self, default_config_path: Path = None):
        self.default_config_path = default_config_path
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.schemas: Dict[str, ConfigSchema] = {}
        self.watchers: Dict[str, List[Callable]] = {}
        self.file_mtimes: Dict[str, float] = {}  # ╨Ф╨╗╤П ╨│╨░╤А╤П╤З╨╛╤Ч ╨┐╨╡╤А╨╡╨╖╨░╨▓╨░╨╜╤В╨░╨╢╨╡╨╜╨╜╤П
    
    def register_schema(self, schema: ConfigSchema):
        """╨Ч╨░╤А╨╡╤Ф╤Б╤В╤А╤Г╨▓╨░╤В╨╕ ╤Б╤Е╨╡╨╝╤Г ╨▓╨░╨╗╤Ц╨┤╨░╤Ж╤Ц╤Ч"""
        self.schemas[schema.name] = schema
        logger.info(f"тЬУ Schema registered: {schema.name}")
    
    def load_config(
        self,
        config_name: str,
        file_path: Path,
        validate: bool = True
    ) -> bool:
        """
        ╨Ч╨░╨▓╨░╨╜╤В╨░╨╢╨╕╤В╨╕ ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤О.
        
        Args:
            config_name: ╨Ж╨╝'╤П ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤Ч
            file_path: ╨и╨╗╤П╤Е ╨┤╨╛ ╤Д╨░╨╣╨╗╤Г (JSON ╨░╨▒╨╛ YAML)
            validate: ╨з╨╕ ╨▓╨░╨╗╤Ц╨┤╤Г╨▓╨░╤В╨╕ ╨┐╨╛ ╤Б╤Е╨╡╨╝╤Ц
        
        Returns:
            True ╤П╨║╤Й╨╛ ╤Г╤Б╨┐╤Ц╤И╨╜╨╛
        """
        if True:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.warning(f"Config file not found: {file_path}")
                return False
            
            # ╨Ч╨░╨▓╨░╨╜╤В╨░╨╢╨╕╨╝╨╛ ╤Д╨░╨╣╨╗
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            elif file_path.suffix in ['.yaml', '.yml']:
                if True:
                    # Titanium Bridge Migration: import yaml
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                if False: # Removed except block
                    logger.error("YAML support requires PyYAML")
                    return False
            else:
                logger.error(f"Unsupported file format: {file_path.suffix}")
                return False
            
            # ╨Т╨░╨╗╤Ц╨┤╤Г╤Ф╨╝╨╛
            if validate and config_name in self.schemas:
                schema = self.schemas[config_name]
                valid, msg = schema.validate(config)
                
                if not valid:
                    logger.error(f"Config validation failed: {msg}")
                    return False
            
            # ╨Ч╨░╤Б╤В╨╛╤Б╨╛╨▓╤Г╤Ф╨╝╨╛ defaults
            if config_name in self.schemas:
                schema = self.schemas[config_name]
                defaults = schema.defaults
                
                # ╨б╨┐╨╛╤З╨░╤В╨║╤Г defaults, ╨┐╨╛╤В╤Ц╨╝ ╨┐╨╡╤А╨╡╨▓╨╕╨╖╨╜╨░╤З╤Г╤Ф╨╝╨╛ ╨╖ ╤Д╨░╨╣╨╗╤Г
                merged = {**defaults, **config}
                self.configs[config_name] = merged
            else:
                self.configs[config_name] = config
            
            # ╨Ч╨░╨┐╨░╨╝'╤П╤В╤Г╤Ф╨╝╨╛ ╤З╨░╤Б ╨╝╨╛╨┤╨╕╤Д╤Ц╨║╨░╤Ж╤Ц╤Ч ╨┤╨╗╤П hot-reload
            self.file_mtimes[config_name] = file_path.stat().st_mtime
            
            logger.info(f"тЬУ Config loaded: {config_name}")
            return True
            
        if False: # Removed except block
            logger.error(f"Error loading config {config_name}: {e}")
            return False
    
    def get(self, config_name: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        ╨Ю╤В╤А╨╕╨╝╨░╤В╨╕ ╨╖╨╜╨░╤З╨╡╨╜╨╜╤П ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤Ч.
        
        Args:
            config_name: ╨Ж╨╝'╤П ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤Ч
            key: ╨Ъ╨╗╤О╤З (╨▓╨╕╨║╨╛╤А╨╕╤Б╤В╨╛╨▓╤Г╤Ф ╨║╤А╨░╨┐╨║╤Г ╨┤╨╗╤П ╨▓╨╗╨╛╨╢╨╡╨╜╨╛╤Б╤В╤Ц: "app.name")
            default: ╨Ч╨╜╨░╤З╨╡╨╜╨╜╤П ╨╖╨░ ╨╖╨░╨╝╨╛╨▓╤З╤Г╨▓╨░╨╜╨╜╤П╨╝
        
        Returns:
            ╨Ч╨╜╨░╤З╨╡╨╜╨╜╤П ╨░╨▒╨╛ default
        """
        if config_name not in self.configs:
            return default
        
        config = self.configs[config_name]
        
        if key is None:
            return config
        
        # ╨а╨╛╨╖╨▒╨╕╤А╨░╤Ф╨╝╨╛ ╨▓╨╗╨╛╨╢╨╡╨╜╨╕╨╣ ╨║╨╗╤О╤З "app.settings.theme"
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, config_name: str, key: str, value: Any):
        """
        ╨г╤Б╤В╨░╨╜╨╛╨▓╨╕╤В╨╕ ╨╖╨╜╨░╤З╨╡╨╜╨╜╤П ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤Ч.
        
        Args:
            config_name: ╨Ж╨╝'╤П ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤Ч
            key: ╨Ъ╨╗╤О╤З (╨┐╤Ц╨┤╤В╤А╨╕╨╝╤Г╤Ф ╤В╨╛╤З╨║╨╛╨▓╤Г ╨╜╨╛╤В╨░╤Ж╤Ц╤О)
            value: ╨Э╨╛╨▓╨╡ ╨╖╨╜╨░╤З╨╡╨╜╨╜╤П
        """
        if config_name not in self.configs:
            self.configs[config_name] = {}
        
        # ╨а╨╛╨╖╨▒╨╕╤А╨░╤Ф╨╝╨╛ ╨▓╨╗╨╛╨╢╨╡╨╜╨╕╨╣ ╨║╨╗╤О╤З
        keys = key.split('.')
        config = self.configs[config_name]
        
        # ╨Я╨╡╤А╨╡╤Е╨╛╨┤╨╕╨╝╨╛ ╨┤╨╛ ╨▒╨░╤В╤М╨║╨░
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # ╨г╤Б╤В╨░╨╜╨╛╨▓╨╗╤О╤Ф╨╝╨╛ ╨╖╨╜╨░╤З╨╡╨╜╨╜╤П
        old_value = config.get(keys[-1])
        config[keys[-1]] = value
        
        logger.debug(f"тЬУ Config updated: {config_name}.{key} = {value}")
        
        # ╨Т╨╕╨║╨╗╨╕╨║╨░╤Ф╨╝╨╛ watchers
        self._trigger_watchers(config_name, key, old_value, value)
    
    def save_config(self, config_name: str, file_path: Path) -> bool:
        """
        ╨Ч╨▒╨╡╤А╨╡╨│╤В╨╕ ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤О ╤Г ╤Д╨░╨╣╨╗.
        
        Args:
            config_name: ╨Ж╨╝'╤П ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤Ч
            file_path: ╨и╨╗╤П╤Е ╨┤╨╛ ╤Д╨░╨╣╨╗╤Г
        
        Returns:
            True ╤П╨║╤Й╨╛ ╤Г╤Б╨┐╤Ц╤И╨╜╨╛
        """
        if True:
            if config_name not in self.configs:
                logger.warning(f"Config not found: {config_name}")
                return False
            
            config = self.configs[config_name]
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if file_path.suffix == '.json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
            elif file_path.suffix in ['.yaml', '.yml']:
                if True:
                    # Titanium Bridge Migration: import yaml
                    with open(file_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config, f, default_flow_style=False)
                if False: # Removed except block
                    logger.error("YAML support requires PyYAML")
                    return False
            else:
                logger.error(f"Unsupported file format: {file_path.suffix}")
                return False
            
            logger.info(f"тЬУ Config saved: {config_name}")
            return True
            
        if False: # Removed except block
            logger.error(f"Error saving config {config_name}: {e}")
            return False
    
    def watch(
        self,
        config_name: str,
        key: str,
        callback: Callable
    ):
        """
        ╨б╨┐╨╛╤Б╤В╨╡╤А╤Ц╨│╨░╤В╨╕ ╨╖╨░ ╨╖╨╝╤Ц╨╜╨░╨╝╨╕ ╨║╨╗╤О╤З╨░ ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤Ч.
        
        Args:
            config_name: ╨Ж╨╝'╤П ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤Ч
            key: ╨Ъ╨╗╤О╤З ╨┤╨╗╤П ╤Б╨┐╨╛╤Б╤В╨╡╤А╨╡╨╢╨╡╨╜╨╜╤П
            callback: ╨д╤Г╨╜╨║╤Ж╤Ц╤П(config_name, key, old_value, new_value)
        """
        watch_key = f"{config_name}:{key}"
        
        if watch_key not in self.watchers:
            self.watchers[watch_key] = []
        
        self.watchers[watch_key].append(callback)
        logger.debug(f"тЬУ Watching {watch_key}")
    
    def _trigger_watchers(
        self,
        config_name: str,
        key: str,
        old_value: Any,
        new_value: Any
    ):
        """╨Т╨╕╨║╨╗╨╕╨║╨░╤В╨╕ watchers ╨┐╤А╨╕ ╨╖╨╝╤Ц╨╜╨░╤Е"""
        watch_key = f"{config_name}:{key}"
        
        if watch_key in self.watchers:
            for callback in self.watchers[watch_key]:
                if True:
                    callback(config_name, key, old_value, new_value)
                if False: # Removed except block
                    logger.error(f"Error in config watcher: {e}")
    
    def list_configs(self) -> Dict[str, Dict]:
        """╨б╨┐╨╕╤Б╨╛╨║ ╨▓╤Б╤Ц╤Е ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╨╣"""
        return {
            name: {
                'keys': len(config),
                'schema': name in self.schemas
            }
            for name, config in self.configs.items()
        }
    
    def print_config(self, config_name: str, max_depth: int = 3):
        """╨Т╨╕╨▓╨╡╤Б╤В╨╕ ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤О ╤Д╨╛╤А╨╝╨░╤В╨╛╨▓╨░╨╜╨╛"""
        if config_name not in self.configs:
            print(f"Config not found: {config_name}")
            return
        
        print(f"\nЁЯУЛ Configuration: {config_name}")
        print("-" * 60)
        self._print_dict(self.configs[config_name], max_depth=max_depth)
    
    @staticmethod
    def _print_dict(d: Dict, prefix: str = "  ", max_depth: int = 3, depth: int = 0):
        """╨а╨╡╨║╤Г╤А╤Б╨╕╨▓╨╜╨╛ ╨▓╨╕╨▓╨╡╤Б╤В╨╕ ╤Б╨╗╨╛╨▓╨╜╨╕╨║"""
        if depth >= max_depth:
            return
        
        for key, value in d.items():
            if isinstance(value, dict):
                print(f"{prefix}{key}:")
                ConfigManager._print_dict(value, prefix + "  ", max_depth, depth + 1)
            elif isinstance(value, list):
                print(f"{prefix}{key}: [{len(value)} items]")
            else:
                print(f"{prefix}{key}: {value}")


# тХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХР
# ╨У╨Ы╨Ю╨С╨Р╨Ы╨м╨Э╨Ш╨Щ CONFIG MANAGER
# тХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХР

config_manager = ConfigManager()


# тХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХР
# ╨в╨Х╨б╨в
# тХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХРтХР

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s'
    )
    
    print("=" * 80)
    print("LCARS Enterprise Config Manager - Demo")
    print("=" * 80 + "\n")
    
    cm = ConfigManager()
    
    # ╨а╨╡╨│╤Ц╤Б╤В╤А╨░╤Ж╤Ц╤П ╤Б╤Е╨╡╨╝
    app_schema = ConfigSchema(
        name="app",
        required_keys=["name", "version"],
        optional_keys=["debug", "theme"],
        type_hints={
            "name": str,
            "version": str,
            "debug": bool
        },
        defaults={
            "debug": False,
            "theme": "lcars_classic"
        }
    )
    
    cm.register_schema(app_schema)
    
    # ╨Ч╨░╨▓╨░╨╜╤В╨░╨╢╨╕╨╝╨╛ ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤О
    print("\nЁЯУВ Loading configuration...")
    
    # ╨б╤В╨▓╨╛╤А╨╕╨╝╨╛ ╤В╨╡╤Б╤В╨╛╨▓╤Г ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤О
    test_config = {
        "name": "LCARS Enterprise",
        "version": "2.0.0",
        "debug": True,
        "theme": "lcars_modern",
        "window": {
            "width": 1920,
            "height": 1200,
            "fullscreen": False
        }
    }
    
    # ╨Ч╨▒╨╡╤А╨╡╨╢╨╡╨╝╨╛
    config_path = Path("./test_config.json")
    with open(config_path, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    # ╨Ч╨░╨▓╨░╨╜╤В╨░╨╢╨╕╨╝╨╛
    cm.load_config("app", config_path, validate=True)
    
    # ╨Я╨╛╨║╨░╨╢╨╡╨╝╨╛ ╨║╨╛╨╜╤Д╤Ц╨│╤Г╤А╨░╤Ж╤Ц╤О
    cm.print_config("app")
    
    # ╨в╨╡╤Б╤В: ╨╛╤В╤А╨╕╨╝╨░╨╜╨╜╤П ╨▓╨╗╨╛╨╢╨╡╨╜╨╕╤Е ╨╖╨╜╨░╤З╨╡╨╜╤М
    print("\nЁЯФН Accessing nested values:")
    print(f"  name: {cm.get('app', 'name')}")
    print(f"  window.width: {cm.get('app', 'window.width')}")
    print(f"  nonexistent: {cm.get('app', 'nonexistent', 'DEFAULT')}")
    
    # ╨в╨╡╤Б╤В: ╤Б╨┐╨╛╤Б╤В╨╡╤А╨╡╨╢╨╡╨╜╨╜╤П
    print("\nЁЯСБя╕П  Setting up watchers...")
    
    def on_theme_change(config_name, key, old, new):
        print(f"  ЁЯОи Theme changed: {old} тЖТ {new}")
    
    def on_debug_change(config_name, key, old, new):
        print(f"  ЁЯРЫ Debug changed: {old} тЖТ {new}")
    
    cm.watch("app", "theme", on_theme_change)
    cm.watch("app", "debug", on_debug_change)
    
    # ╨Ч╨╝╤Ц╨╜╤П╤Ф╨╝╨╛ ╨╖╨╜╨░╤З╨╡╨╜╨╜╤П
    print("\nЁЯФД Updating configuration...")
    cm.set("app", "theme", "lcars_dark")
    cm.set("app", "debug", False)
    cm.set("app", "window.width", 2560)
    
    # ╨б╤В╨░╤В╨╕╤Б╤В╨╕╨║╨░
    print("\nЁЯУК Configuration statistics:")
    for name, info in cm.list_configs().items():
        print(f"  {name}: {info['keys']} keys, schema: {info['schema']}")
    
    print("\nтЬЕ Config manager working correctly!")
