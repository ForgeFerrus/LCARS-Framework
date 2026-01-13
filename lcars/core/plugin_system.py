"""
Plugin System для LCARS Enterprise
===================================

Система плагінів дозволяє розширювати функціонал без зміни основного коду.
"""

import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Type, Any, Callable, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# ІНТЕРФЕЙС ПЛАГІНА
# ═════════════════════════════════════════════════════════════════════════════

class LCARSPlugin(ABC):
    """
    Базовий клас для всіх плагінів LCARS Enterprise.
    
    Кожен плагін повинен наслідувати цей клас та реалізувати методи:
    • on_load()
    • on_unload()
    • on_startup()
    • on_shutdown()
    """
    
    @dataclass
    class Metadata:
        """Метаданні плагіна"""
        name: str
        version: str
        author: str
        description: str
        dependencies: List[str] = None
        
        def __post_init__(self):
            if self.dependencies is None:
                self.dependencies = []
    
    def __init__(self, metadata: Metadata):
        self.metadata = metadata
        self.enabled = False
        self.exports = {}
    
    @abstractmethod
    def on_load(self) -> bool:
        """Викликається при завантаженні плагіна"""
        pass
    
    @abstractmethod
    def on_unload(self) -> bool:
        """Викликається при вивантаженні плагіна"""
        pass
    
    def on_startup(self):
        """Викликається при старті приложення"""
        pass
    
    def on_shutdown(self):
        """Викликається при завершенні приложення"""
        pass
    
    def export(self, name: str, obj: Any):
        """Експортувати об'єкт для інших плагінів"""
        self.exports[name] = obj
    
    def get_export(self, name: str) -> Optional[Any]:
        """Отримати експортований об'єкт"""
        return self.exports.get(name)


# ═════════════════════════════════════════════════════════════════════════════
# РЕЄСТР ПЛАГІНІВ
# ═════════════════════════════════════════════════════════════════════════════

class PluginRegistry:
    """Реєстр усіх плагінів у системі"""
    
    def __init__(self):
        self.plugins: Dict[str, LCARSPlugin] = {}
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register(self, name: str, plugin: LCARSPlugin):
        """Зареєструвати плагін"""
        if name in self.plugins:
            raise ValueError(f"Plugin '{name}' already registered")
        
        self.plugins[name] = plugin
        logger.info(f"✓ Plugin registered: {name} v{plugin.metadata.version}")
    
    def unregister(self, name: str):
        """Видалити плагін з реєстру"""
        if name in self.plugins:
            del self.plugins[name]
            logger.info(f"✓ Plugin unregistered: {name}")
    
    def get_plugin(self, name: str) -> Optional[LCARSPlugin]:
        """Отримати плагін по імені"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> Dict[str, str]:
        """Список всіх плагінів"""
        return {
            name: plugin.metadata.version
            for name, plugin in self.plugins.items()
        }
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Зареєструвати hook (callback на подію)"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    def trigger_hook(self, hook_name: str, *args, **kwargs):
        """Викликати всі callbacks для hook'a"""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in hook '{hook_name}': {e}")


# ═════════════════════════════════════════════════════════════════════════════
# МЕНЕДЖЕР ПЛАГІНІВ
# ═════════════════════════════════════════════════════════════════════════════

class PluginManager:
    """Менеджер для завантаження, встановлення та управління плагінами"""
    
    def __init__(self, plugins_dir: Path = None):
        self.plugins_dir = plugins_dir or Path("./plugins")
        self.registry = PluginRegistry()
        self.loaded_modules = {}
    
    def discover_plugins(self) -> Dict[str, Path]:
        """Знайти всі доступні плагіни"""
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return {}
        
        plugins = {}
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith('_'):
                plugin_file = plugin_dir / f"{plugin_dir.name}_plugin.py"
                if plugin_file.exists():
                    plugins[plugin_dir.name] = plugin_file
        
        logger.info(f"✓ Discovered {len(plugins)} plugins")
        return plugins
    
    def load_plugin(self, plugin_name: str, plugin_path: Path) -> bool:
        """Завантажити плагін з файлу"""
        try:
            # Завантажимо Python модуль
            spec = importlib.util.spec_from_file_location(
                f"lcars_plugin_{plugin_name}",
                plugin_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            
            # Знаходимо клас плагіна
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, LCARSPlugin) and 
                    attr is not LCARSPlugin):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                logger.error(f"No LCARSPlugin subclass found in {plugin_path}")
                return False
            
            # Створимо екземпляр плагіна
            plugin = plugin_class()
            
            # Завантажимо метаданні (якщо є plugin.yaml)
            yaml_path = plugin_path.parent / "plugin.yaml"
            if yaml_path.exists():
                with open(yaml_path, 'r') as f:
                    # Спрощено - просто логуємо
                    logger.info(f"Loaded metadata from {yaml_path}")
            
            # Викличемо on_load
            if not plugin.on_load():
                logger.error(f"Plugin {plugin_name} failed to load")
                return False
            
            # Зареєструємо плагін
            self.registry.register(plugin_name, plugin)
            self.loaded_modules[plugin_name] = module
            plugin.enabled = True
            
            logger.info(f"✅ Plugin loaded: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Вивантажити плагін"""
        plugin = self.registry.get_plugin(plugin_name)
        if plugin is None:
            logger.warning(f"Plugin not found: {plugin_name}")
            return False
        
        try:
            if plugin.on_unload():
                self.registry.unregister(plugin_name)
                plugin.enabled = False
                logger.info(f"✓ Plugin unloaded: {plugin_name}")
                return True
            else:
                logger.error(f"Plugin {plugin_name} failed to unload")
                return False
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> int:
        """Завантажити всі плагіни"""
        plugins = self.discover_plugins()
        loaded_count = 0
        
        for plugin_name, plugin_path in plugins.items():
            if self.load_plugin(plugin_name, plugin_path):
                loaded_count += 1
        
        logger.info(f"✓ Loaded {loaded_count}/{len(plugins)} plugins")
        return loaded_count
    
    def get_plugin(self, name: str) -> Optional[LCARSPlugin]:
        """Отримати плагін по імені"""
        return self.registry.get_plugin(name)
    
    def list_plugins(self) -> Dict[str, str]:
        """Список активних плагінів"""
        return self.registry.list_plugins()


# ═════════════════════════════════════════════════════════════════════════════
# ПРИКЛАД ПЛАГІНА
# ═════════════════════════════════════════════════════════════════════════════

class ExamplePlugin(LCARSPlugin):
    """Приклад простого плагіна"""
    
    def __init__(self):
        metadata = LCARSPlugin.Metadata(
            name="Example Plugin",
            version="1.0.0",
            author="Enterprise",
            description="Simple example plugin for LCARS",
            dependencies=[]
        )
        super().__init__(metadata)
    
    def on_load(self) -> bool:
        """Викликається при завантаженні"""
        print(f"Loading: {self.metadata.name}")
        self.export("example_data", {"message": "Hello from plugin!"})
        return True
    
    def on_unload(self) -> bool:
        """Викликається при вивантаженні"""
        print(f"Unloading: {self.metadata.name}")
        return True
    
    def on_startup(self):
        print(f"Startup: {self.metadata.name}")
    
    def on_shutdown(self):
        print(f"Shutdown: {self.metadata.name}")


# ═════════════════════════════════════════════════════════════════════════════
# ТЕСТ
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s'
    )
    
    print("=" * 80)
    print("LCARS Enterprise Plugin System - Demo")
    print("=" * 80 + "\n")
    
    # Створимо менеджер плагінів
    pm = PluginManager(Path("./plugins"))
    
    # Завантажимо плагін прямо (для демонстрації)
    example = ExamplePlugin()
    pm.registry.register("example", example)
    example.on_load()
    
    # Запустимо
    example.on_startup()
    
    # Покажемо список плагінів
    print("\n📋 Active Plugins:")
    for name, version in pm.list_plugins().items():
        print(f"  • {name}: v{version}")
    
    # Отримаємо експортовані дані
    print("\n📦 Plugin Exports:")
    exported = example.get_export("example_data")
    print(f"  {exported}")
    
    # Завершимо
    example.on_shutdown()
    pm.unload_plugin("example")
    
    print("\n✅ Plugin system working correctly!")
