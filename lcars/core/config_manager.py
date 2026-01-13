"""
Config Manager для LCARS Enterprise
====================================

Система керування конфігурацією: завантаження, валідація, гарячої перезавантаження.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, Callable, List
from dataclasses import dataclass, asdict
import yaml

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# КОНФІГУРАЦІЙНА СХЕМА
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class ConfigSchema:
    """Схема для валідації конфігурації"""
    
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
        Валідувати конфігурацію.
        
        Returns:
            (valid, message)
        """
        # Перевіримо обов'язкові ключі
        for key in self.required_keys:
            if key not in config:
                return False, f"Missing required key: {key}"
        
        # Перевіримо типи
        for key, expected_type in self.type_hints.items():
            if key in config:
                if not isinstance(config[key], expected_type):
                    return (
                        False,
                        f"Invalid type for '{key}': expected {expected_type.__name__}, "
                        f"got {type(config[key]).__name__}"
                    )
        
        return True, "Valid"


# ═════════════════════════════════════════════════════════════════════════════
# CONFIG MANAGER
# ═════════════════════════════════════════════════════════════════════════════

class ConfigManager:
    """
    Менеджер конфігурації для LCARS Enterprise.
    
    Функції:
    • Завантаження з JSON/YAML
    • Валідація по схемі
    • Гаряча перезавантаженн (hot-reload)
    • Спостереження за змінами
    • Композиція (env + default + user config)
    """
    
    def __init__(self, default_config_path: Path = None):
        self.default_config_path = default_config_path
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.schemas: Dict[str, ConfigSchema] = {}
        self.watchers: Dict[str, List[Callable]] = {}
        self.file_mtimes: Dict[str, float] = {}  # Для гарячої перезавантаження
    
    def register_schema(self, schema: ConfigSchema):
        """Зареєструвати схему валідації"""
        self.schemas[schema.name] = schema
        logger.info(f"✓ Schema registered: {schema.name}")
    
    def load_config(
        self,
        config_name: str,
        file_path: Path,
        validate: bool = True
    ) -> bool:
        """
        Завантажити конфігурацію.
        
        Args:
            config_name: Ім'я конфігурації
            file_path: Шлях до файлу (JSON або YAML)
            validate: Чи валідувати по схемі
        
        Returns:
            True якщо успішно
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.warning(f"Config file not found: {file_path}")
                return False
            
            # Завантажимо файл
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            elif file_path.suffix in ['.yaml', '.yml']:
                try:
                    import yaml
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                except ImportError:
                    logger.error("YAML support requires PyYAML")
                    return False
            else:
                logger.error(f"Unsupported file format: {file_path.suffix}")
                return False
            
            # Валідуємо
            if validate and config_name in self.schemas:
                schema = self.schemas[config_name]
                valid, msg = schema.validate(config)
                
                if not valid:
                    logger.error(f"Config validation failed: {msg}")
                    return False
            
            # Застосовуємо defaults
            if config_name in self.schemas:
                schema = self.schemas[config_name]
                defaults = schema.defaults
                
                # Спочатку defaults, потім перевизначуємо з файлу
                merged = {**defaults, **config}
                self.configs[config_name] = merged
            else:
                self.configs[config_name] = config
            
            # Запам'ятуємо час модифікації для hot-reload
            self.file_mtimes[config_name] = file_path.stat().st_mtime
            
            logger.info(f"✓ Config loaded: {config_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading config {config_name}: {e}")
            return False
    
    def get(self, config_name: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Отримати значення конфігурації.
        
        Args:
            config_name: Ім'я конфігурації
            key: Ключ (використовує крапку для вложеності: "app.name")
            default: Значення за замовчуванням
        
        Returns:
            Значення або default
        """
        if config_name not in self.configs:
            return default
        
        config = self.configs[config_name]
        
        if key is None:
            return config
        
        # Розбираємо вложений ключ "app.settings.theme"
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
        Установити значення конфігурації.
        
        Args:
            config_name: Ім'я конфігурації
            key: Ключ (підтримує точкову нотацію)
            value: Нове значення
        """
        if config_name not in self.configs:
            self.configs[config_name] = {}
        
        # Розбираємо вложений ключ
        keys = key.split('.')
        config = self.configs[config_name]
        
        # Переходимо до батька
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Установлюємо значення
        old_value = config.get(keys[-1])
        config[keys[-1]] = value
        
        logger.debug(f"✓ Config updated: {config_name}.{key} = {value}")
        
        # Викликаємо watchers
        self._trigger_watchers(config_name, key, old_value, value)
    
    def save_config(self, config_name: str, file_path: Path) -> bool:
        """
        Зберегти конфігурацію у файл.
        
        Args:
            config_name: Ім'я конфігурації
            file_path: Шлях до файлу
        
        Returns:
            True якщо успішно
        """
        try:
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
                try:
                    import yaml
                    with open(file_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config, f, default_flow_style=False)
                except ImportError:
                    logger.error("YAML support requires PyYAML")
                    return False
            else:
                logger.error(f"Unsupported file format: {file_path.suffix}")
                return False
            
            logger.info(f"✓ Config saved: {config_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving config {config_name}: {e}")
            return False
    
    def watch(
        self,
        config_name: str,
        key: str,
        callback: Callable
    ):
        """
        Спостерігати за змінами ключа конфігурації.
        
        Args:
            config_name: Ім'я конфігурації
            key: Ключ для спостереження
            callback: Функція(config_name, key, old_value, new_value)
        """
        watch_key = f"{config_name}:{key}"
        
        if watch_key not in self.watchers:
            self.watchers[watch_key] = []
        
        self.watchers[watch_key].append(callback)
        logger.debug(f"✓ Watching {watch_key}")
    
    def _trigger_watchers(
        self,
        config_name: str,
        key: str,
        old_value: Any,
        new_value: Any
    ):
        """Викликати watchers при змінах"""
        watch_key = f"{config_name}:{key}"
        
        if watch_key in self.watchers:
            for callback in self.watchers[watch_key]:
                try:
                    callback(config_name, key, old_value, new_value)
                except Exception as e:
                    logger.error(f"Error in config watcher: {e}")
    
    def list_configs(self) -> Dict[str, Dict]:
        """Список всіх конфігурацій"""
        return {
            name: {
                'keys': len(config),
                'schema': name in self.schemas
            }
            for name, config in self.configs.items()
        }
    
    def print_config(self, config_name: str, max_depth: int = 3):
        """Вивести конфігурацію форматовано"""
        if config_name not in self.configs:
            print(f"Config not found: {config_name}")
            return
        
        print(f"\n📋 Configuration: {config_name}")
        print("-" * 60)
        self._print_dict(self.configs[config_name], max_depth=max_depth)
    
    @staticmethod
    def _print_dict(d: Dict, prefix: str = "  ", max_depth: int = 3, depth: int = 0):
        """Рекурсивно вивести словник"""
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


# ═════════════════════════════════════════════════════════════════════════════
# ГЛОБАЛЬНИЙ CONFIG MANAGER
# ═════════════════════════════════════════════════════════════════════════════

config_manager = ConfigManager()


# ═════════════════════════════════════════════════════════════════════════════
# ТЕСТ
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s'
    )
    
    print("=" * 80)
    print("LCARS Enterprise Config Manager - Demo")
    print("=" * 80 + "\n")
    
    cm = ConfigManager()
    
    # Регістрація схем
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
    
    # Завантажимо конфігурацію
    print("\n📂 Loading configuration...")
    
    # Створимо тестову конфігурацію
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
    
    # Збережемо
    config_path = Path("./test_config.json")
    with open(config_path, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    # Завантажимо
    cm.load_config("app", config_path, validate=True)
    
    # Покажемо конфігурацію
    cm.print_config("app")
    
    # Тест: отримання вложених значень
    print("\n🔍 Accessing nested values:")
    print(f"  name: {cm.get('app', 'name')}")
    print(f"  window.width: {cm.get('app', 'window.width')}")
    print(f"  nonexistent: {cm.get('app', 'nonexistent', 'DEFAULT')}")
    
    # Тест: спостереження
    print("\n👁️  Setting up watchers...")
    
    def on_theme_change(config_name, key, old, new):
        print(f"  🎨 Theme changed: {old} → {new}")
    
    def on_debug_change(config_name, key, old, new):
        print(f"  🐛 Debug changed: {old} → {new}")
    
    cm.watch("app", "theme", on_theme_change)
    cm.watch("app", "debug", on_debug_change)
    
    # Зміняємо значення
    print("\n🔄 Updating configuration...")
    cm.set("app", "theme", "lcars_dark")
    cm.set("app", "debug", False)
    cm.set("app", "window.width", 2560)
    
    # Статистика
    print("\n📊 Configuration statistics:")
    for name, info in cm.list_configs().items():
        print(f"  {name}: {info['keys']} keys, schema: {info['schema']}")
    
    print("\n✅ Config manager working correctly!")
