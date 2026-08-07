from __future__ import annotations
import importlib
import inspect
from typing import Any, Optional, Dict, List, Callable
from collections import defaultdict

from lcars.base.type import LCARS, Directive, SystemComponent
from lcars.base.version import getVersion
from lcars.base.register import registry


class Proxy:
    # Мостовий проксі для завантаження та кешування модулів з реєстру
    def __init__(self, register, bridge):
        # Ініціалізація проксі з реєстром та батьківським мостом
        self.Register = register
        self.Bridge = bridge
        self.Runtime: Dict[str, Any] = {}

    def Resolve(self, key: str) -> tuple:
        # Пошук запису в реєстрі за ключем
        entry = self.Register.Resolve(key)
        if entry is None:
            raise KeyError(f"Registry: '{key}' not found.")
        return entry

    def Load(self, key: str) -> Any:
        # Завантаження модуля з кешу або реєстру
        if key in self.Runtime:
            return self.Runtime[key]

        entry = self.Resolve(key)
        if not isinstance(entry, tuple) or len(entry) != 2:
            return entry

        module_path, attribute = entry
        # Імпорт модуля з перевіркою наявності import_module
        if hasattr(importlib, 'import_module'):
            module = importlib.import_module(module_path)
        else:
            return None

        if attribute:
            result = getattr(module, attribute, None)
        else:
            result = module

        # Автоматичний виклик функцій без обов'язкових аргументів
        if callable(result) and not isinstance(result, type):
            if hasattr(result, '__code__') and result.__code__.co_argcount == 0:
                result = result()

        self.Runtime[key] = result
        return result

    def Reload(self, key: str) -> Any:
        # Перезавантаження модуля з видаленням з кешу
        self.Runtime.pop(key, None)
        return self.Load(key)

    def __getitem__(self, key: str) -> Any:
        # Доступ до завантаженого модуля за ключем
        return self.Load(key)

    def __contains__(self, key: str) -> bool:
        # Перевірка наявності ключа в кеші
        return key in self.Runtime


class Link:
    # Посилання на цільовий об'єкт з підтримкою перезавантаження
    def __init__(self, key: str, target: Any):
        # Ініціалізація посилання з ключем та ціллю
        self.Key = key
        self.Target = target
        self.Name = getattr(target, "__name__", str(target))
        self.Module = getattr(target, "__module__", "")

    def Reload(self) -> Any:
        # Перезавантаження цільового об'єкта з модуля
        module_path, attribute = self.Key, ""
        if "." in self.Key:
            parts = self.Key.rsplit(".", 1)
            module_path = parts[0]
            attribute = parts[1] if len(parts) > 1 else ""
        # Імпорт модуля з перевіркою наявності import_module
        if hasattr(importlib, 'import_module'):
            module = importlib.import_module(module_path)
        else:
            return None
        if attribute:
            self.Target = getattr(module, attribute)
        else:
            self.Target = module
        return self.Target

    def __call__(self, *args, **kwargs):
        # Виклик цільового об'єкта з аргументами
        return self.Target(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        # Делегування атрибутів цільовому об'єкту
        return getattr(self.Target, name)


class SubspaceBridge:
    # Підміст мосту з префіксом простору імен
    def __init__(self, prefix: str, bridge: "Bridge"):
        # Ініціалізація підмосту з префіксом та батьківським мостом
        self.Prefix = prefix
        self.Bridge = bridge

    def Load(self, key: str) -> Any:
        # Завантаження через батьківський міст з префіксом
        return self.Bridge.Load(f"{self.Prefix}.{key}")

    def Route(self, key: str) -> Any:
        # Маршрутизація запиту через Load
        return self.Load(key)

    def Connect(self, path: str, slot: Callable) -> Callable:
        # Підключення слоту через батьківський міст
        return self.Bridge.Connect(f"{self.Prefix}.{path}", slot)

    def Disconnect(self, path: str, slot: Callable) -> Callable:
        # Відключення слоту через батьківський міст
        return self.Bridge.Disconnect(f"{self.Prefix}.{path}", slot)


class Bridge(SystemComponent):
    # Головний компонент мосту LCARS для маршрутизації та завантаження
    def __init__(self):
        # Ініціалізація мосту з базовими параметрами
        super().__init__(Id="Bridge")
        self.Version = getVersion()
        self.Name = "LCARS Bridge"
        self.Status = "Offline"
        self.Proxy: Optional[Proxy] = None

    def Initialize(self) -> bool:
        # Ініціалізація проксі та активація мосту
        self.Proxy = Proxy(register=registry, bridge=self)
        self.Status = "Online"
        return True

    @staticmethod
    def Connect(Name: str) -> Any:
        """Load one external bridge entry by name, and nothing else."""
        Key = str(Name or "").strip()
        if not Key:
            return None
        if not Key.lower().startswith("bridge."):
            Key = "Bridge." + Key
        RealKey = Key if Key in registry.Mapping else registry.Keys.get(Key.lower())
        if RealKey is None:
            return None
        Rule = registry.Mapping[RealKey]
        Module, Attribute = Rule if isinstance(Rule, tuple) else (Rule, None)
        if not isinstance(Module, str):
            return None
        try:
            module = importlib.import_module(Module)
        except (ImportError, ModuleNotFoundError, ValueError):
            return None
        if not Attribute:
            return module
        result = module
        for Part in str(Attribute).split("."):
            result = getattr(result, Part, None)
            if result is None:
                return None
        return result

    def Load(self, key: str) -> Any:
        # Завантаження через проксі з автоматичною ініціалізацією
        if self.Proxy is None:
            self.Initialize()
        return self.Proxy.Load(key)

    def Reload(self, key: str) -> Any:
        # Перезавантаження через проксі з автоматичною ініціалізацією
        if self.Proxy is None:
            self.Initialize()
        return self.Proxy.Reload(key)

    def Route(self, key: str) -> Any:
        # Маршрутизація запиту через Load
        return self.Load(key)

    def Subspace(self, prefix: str) -> SubspaceBridge:
        # Створення підмосту з вказаним префіксом
        return SubspaceBridge(prefix, self)

    def ActiveChannels(self) -> dict:
        # Отримання інформації про активні канали
        return {
            "Status": self.Status,
            "Version": str(self.Version),
            "Runtime": len(self.Proxy.Runtime) if self.Proxy else 0,
        }

    def Clear(self):
        # Очищення кешу рантайму
        if self.Proxy:
            self.Proxy.Runtime.clear()
        return self


__all__ = ["Bridge", "Proxy", "Link", "SubspaceBridge"]
