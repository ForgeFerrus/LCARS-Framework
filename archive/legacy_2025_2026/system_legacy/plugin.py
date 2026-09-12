# ◤ TITANIUM PLUGIN SYSTEM — v44.20 🖖
# LCARS Framework :: EXTENSION_SUBSTRATE // MODULAR_NODE // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Система плагінів та розширення функціоналу LCARS Titanium.
# ФУНКЦІЇ: Динамічне завантаження ізолінійних модулів через YAML-дескриптори.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
# Titanium Bridge Migration: import importlib
# Titanium Bridge Migration: import importlib.util
# Titanium Bridge Migration: import yaml
import logging
# Titanium Bridge Migration: from dataclasses import dataclass, field
from abc import ABC, abstractmethod
# Titanium Bridge Migration: from typing import Any, Optional, Union, Dict, List, Callable, Type

# Імпорт базових типів Titanium Master
from lcars.base.type import LCARS, Directive, PathDrive

# Налаштування системного логера Titanium
SystemLogger = logging.getLogger(__name__)

# БАЗОВИЙ КЛАС ДЛЯ ВСІХ ПЛАГІНІВ (TITANIUM PLUGIN BASE)
@dataclass
class LCARSPluginMetadata:
    Name: str
    Version: str
    Author: str
    Description: str
    Dependencies: List[str] = field(default_factory=list)
    Id: str = ""
    Entrypoint: str = ""


class LCARSPlugin(ABC):
    # Метадані плагіна Titanium (Plugin Metadata)

    def __init__(
        self,
        metadata: Optional[LCARSPluginMetadata] = None,
        MetadataNode: Optional[LCARSPluginMetadata] = None,
    ):
        if metadata is None:
            metadata = MetadataNode
        if metadata is None:
            metadata = LCARSPluginMetadata(
                Name="Unknown",
                Version="0.0.1",
                Author="Anonymous",
                Description=""
            )
        self.metadata: LCARSPluginMetadata = metadata
        self.IsLoaded = False
        self.IsEnabled = False
        self.ExportMap = {}

    # Завантаження логіки плагіна (OnLoad)
    @abstractmethod
    def OnLoad(self) -> bool:
        pass

    # Вивантаження плагіна (OnUnload)
    @abstractmethod
    def OnUnload(self) -> bool:
        pass

    # Старт системних служб плагіна
    def OnStartup(self):
        pass

    # Зупинка системних служб плагіна
    def OnShutdown(self):
        pass

    # Експорт функціоналу (Export)
    def Export(self, NameKey: str, ValueNode: Any):
        self.ExportMap[NameKey] = ValueNode

    # Отримання експортованих значень (GetExport)
    def GetExport(self, NameKey: str) -> Optional[Any]:
        return self.ExportMap.get(NameKey)

# РЕЄСТР АКТИВНИХ ПЛАГІНІВ (PLUGIN REGISTRY)
class PluginRegistry:
    def __init__(self):
        self.ActivePluginsMap: Dict[str, LCARSPlugin] = {}

    def RegisterPlugin(self, PluginIdStr: str, PluginInstance: LCARSPlugin):
        if PluginIdStr in self.ActivePluginsMap:
            SystemLogger.warning(f"◤ PLUGIN REGISTRY: ID {PluginIdStr} ALREADY ACTIVE.")
            return
        self.ActivePluginsMap[PluginIdStr] = PluginInstance
        SystemLogger.info(f"✓ {PluginIdStr}: MODULE CONNECTED TO KERNEL MATRIX.")

    def UnregisterPlugin(self, PluginIdStr: str):
        if PluginIdStr in self.ActivePluginsMap:
            del self.ActivePluginsMap[PluginIdStr]

    def GetPlugin(self, PluginIdStr: str) -> Optional[LCARSPlugin]:
        return self.ActivePluginsMap.get(PluginIdStr)

# МЕНЕДЖЕР ПЛАГІНІВ (TITANIUM PLUGIN MANAGER)
class PluginManager:
    # Координатор пошуку та інтеграції зовнішніх модулів.
    def __init__(self, NexusRef: Any = None):
        # Визначення кореня через PathDrive (No OS)
        RootPathNode = NexusRef.ProjectRoot if hasattr(NexusRef, 'ProjectRoot') else "."
        self.PluginsDirectory = PathDrive(RootPathNode) / "plugins"
        self.RegistryNode = PluginRegistry()
        self.LoadedModulesCache = {}

    # Масове завантаження плагінів (LoadPlugins)
    def LoadPlugins(self):
        return self.LoadAllDetectedPlugins()

    # Пошук YAML дескрипторів (DiscoverPlugins)
    def DiscoverPlugins(self) -> List[Any]:
        if not self.PluginsDirectory.exists():
            return []
        return list(self.PluginsDirectory.glob("*.yaml"))
    
    # Верифікація шляху модуля Titanium
    def VerifyModuleNodePath(self, ModuleNameStr: str) -> bool:
        PathNodesArray = ModuleNameStr.split('.')
        CurrentPath = ""
        for Node in PathNodesArray:
            CurrentPath = f"{CurrentPath}.{Node}" if CurrentPath else Node
            if not importlib.util.find_spec(CurrentPath):
                return False
        return True

    # Завантаження окремого плагіна (LoadPluginNode)
    def LoadPluginNode(self, DescriptorPath: Any) -> bool:
        with open(DescriptorPath, 'r', encoding='utf-8') as FileNode:
            DataMap = yaml.safe_load(FileNode)
            
        if not isinstance(DataMap, dict):
            return False
            
        PluginIdStr = DataMap.get('id')
        EntrypointStr = DataMap.get('entrypoint')
        
        if not PluginIdStr or not EntrypointStr:
            return False
            
        if ":" in EntrypointStr:
            ModuleNameStr, AttrNameStr = EntrypointStr.split(":", 1)
        else:
            ModuleNameStr, AttrNameStr = EntrypointStr, "setup"
            
        # Валідація модульної структури Titanium
        if not self.VerifyModuleNodePath(ModuleNameStr):
            SystemLogger.debug(f"◤ PLUGIN MANAGER: NODE {ModuleNameStr} NOT FOUND.")
            return False
            
        ModuleInstance = importlib.import_module(ModuleNameStr)
        self.LoadedModulesCache[PluginIdStr] = ModuleInstance
        TargetNode = getattr(ModuleInstance, AttrNameStr, None)
        
        if not TargetNode:
            return False
            
        # Створення метаданих плагіна Titanium
        MetadataNode = LCARSPluginMetadata(
            Name=DataMap.get('name', 'Unknown'),
            Version=str(DataMap.get('version', '0.0.1')),
            Author=DataMap.get('author', 'Anonymous'),
            Description=DataMap.get('description', ''),
            Id=PluginIdStr,
            Entrypoint=EntrypointStr,
            Dependencies=DataMap.get('dependencies', [])
        )
        
        PluginInstance = None
        if isinstance(TargetNode, type) and issubclass(TargetNode, LCARSPlugin):
            PluginInstance = TargetNode(MetadataNode=MetadataNode)
        elif callable(TargetNode):
            # Підтримка адаптерів функціонального типу
            PluginInstance = TargetNode(Directive, DataMap.get('config_schema', {}))
            if not isinstance(PluginInstance, LCARSPlugin):
                # Обгортка Titanium для функціональних компонентів
                class FunctionalPluginAdapter(LCARSPlugin):
                    def OnLoad(self): return True
                    def OnUnload(self): return True
                BackendLink = PluginInstance
                PluginInstance = FunctionalPluginAdapter(MetadataNode=MetadataNode)
                PluginInstance.Export("BackendLink", BackendLink)

        if PluginInstance:
            if PluginInstance.OnLoad():
                self.RegistryNode.RegisterPlugin(PluginIdStr, PluginInstance)
                PluginInstance.IsEnabled = True
                return True
        return False

    # Масове завантаження всіх компонентів (LoadAllDetectedPlugins)
    def LoadAllDetectedPlugins(self) -> int:
        DescriptorList = self.DiscoverPlugins()
        CountVal = 0
        for PathNode in DescriptorList:
            # Ігнорування службових файлів конфігурації
            if PathNode.name.startswith('_'):
                continue
            if self.LoadPluginNode(PathNode):
                CountVal += 1
        return CountVal

# ЕКСПОРТ СИСТЕМИ ПЛАГІНІВ
__all__ = ["LCARSPlugin", "PluginManager", "PluginRegistry"]
