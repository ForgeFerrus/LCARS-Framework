# ◤ TITANIUM PLUGIN SYSTEM — v44.20 🖖
# LCARS Framework :: EXTENSION_SUBSTRATE // MODULAR_NODE // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Система плагінів та розширення функціоналу LCARS Titanium.
# ФУНКЦІЇ: Динамічне завантаження ізолінійних модулів через YAML-дескриптори.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань).
# ─────────────────────────────────────────────────────────────────────────────

import importlib
import importlib.util
from pathlib import Path
import yaml
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List

# Імпорт базових типів Titanium Master
from lcars.base.type import LCARSMatrix, LCARS
from lcars.core.service import Service

# ═════════════════════════════════════════════════════════════════════════════
# API ДЛЯ ПЛАГІНІВ (PluginApi)
# ═════════════════════════════════════════════════════════════════════════════
class PluginApi:

    def __init__(self):
        self.Storage: Dict[str, Any] = {}
        self.Discovery: Optional[Any] = None
        self.Ui: List[Any] = []
        self.Agent: Optional[Any] = None
        self.Backup: Optional[Any] = None
        self.Theme: Optional[Any] = None
        self.AiProviders: Dict[str, Any] = {}

    def RegisterStorage(self, Name: str, Adapter: Any) -> None:
        self.Storage[Name] = Adapter

    def RegisterDiscovery(self, Discovery: Any) -> None:
        self.Discovery = Discovery

    def RegisterIntegration(self, Ui: Any) -> None:
        if not isinstance(self.Ui, list):
            self.Ui = []
        self.Ui.append(Ui)

    def RegisterUiIntegration(self, Ui: Any) -> None:
        return self.RegisterIntegration(Ui)

    def RegisterAgent(self, Agent: Any) -> None:
        self.Agent = Agent

    def RegisterBackup(self, Backup: Any) -> None:
        self.Backup = Backup

    def RegisterTheme(self, Theme: Any) -> None:
        self.Theme = Theme

    def RegisterAiProvider(self, Name: str, Provider: Any) -> None:
        self.AiProviders[Name] = Provider

# ═════════════════════════════════════════════════════════════════════════════
# КОНКРЕТНІ ПЛАГІНИ (Plugin Implementations)
# ═════════════════════════════════════════════════════════════════════════════
def ReadPluginYaml(PathVal: Path) -> Optional[Dict[str, Any]]:
    # Читає YAML файл плагіна
    # PathVal - шлях до plugin.yaml
    # Повертає словник з метаданими плагіна
    Yaml = importlib.import_module("yaml")
    with PathVal.open('r', encoding='utf-8') as F:
        return Yaml.safe_load(F)
def DiscoverPlugins(Root: Optional[str] = None) -> List[Dict[str, Any]]:
    # Пошук всіх плагінів в директорії
    # Root - шлях до папки з плагінами (за замовчуванням ./plugins)
    # Сканує підпапки, шукає plugin.yaml файли
    # Повертає список словників з метаданими
    RootPath = Path(Root) if Root else Path(__file__).parent.parent / "plugins"
    Plugins = []
    if not RootPath.exists(): return []
    for Child in RootPath.iterdir():
        if Child.is_dir():
            Desc = Child / 'plugin.yaml'
            if Desc.exists():
                Meta = ReadPluginYaml(Desc)
                if Meta:
                    Meta['Path'] = str(Child)
                    Plugins.append(Meta)
    return Plugins

class AgentPlugin:
    # Плагін AI агентів - підключається до існуючих або створює нові

    def __init__(self):
        self.Copilot = None
        self.Provider = None
        self.Computer = None
        self.NovaAdapter = None
        self.DevEnv = None

    def Load(self, api: PluginApi, cfg: dict):
        # Copilot - створюємо екземпляр (немає глобального)
        from lcars.service.copilot import Copilot
        self.Copilot = Copilot(project_root='.')
        allowShell = cfg.get('allowShell', False)
        self.Copilot.ShellEnabled = allowShell
        api.RegisterAgent(self.Copilot)

        # AI Provider - створюємо екземпляр
        from lcars.service.provider import AIProviderManager
        self.Provider = AIProviderManager()
        api.RegisterAiProvider('default', self.Provider)
        api.RegisterAiProvider('groq', self.Provider)

        # BoardComputer - отримуємо існуючий сінглтон
        from lcars.service.onboard import GetComputer
        self.Computer = GetComputer()
        api.RegisterDiscovery(self.Computer)

        # NovaAct - підключаємо адаптер
        import threading
        import time

        class NovaActAdapter:
            def __init__(self, computer=None, config=None):
                self.computer = computer or GetComputer()
                self.config = config or {}
                self.connected = False
                self.sdk_ready = False

            def Connect(self, useSdk=False):
                if useSdk and self.config.get('useSdk'):
                    threading.Thread(target=self.InitSdk, daemon=True).start()
                self.connected = True
                return True

            def InitSdk(self):
                time.sleep(1)
                self.sdk_ready = True

        novaCfg = cfg.get('nova', {})
        self.NovaAdapter = NovaActAdapter(computer=self.Computer, config=novaCfg)
        if novaCfg.get('autoConnect', False):
            self.NovaAdapter.Connect(useSdk=novaCfg.get('useSdk', False))
        api.RegisterDiscovery(self.NovaAdapter)

        # DevEnv - підключаємо UI
        if cfg.get('devEnv', True):
            api.RegisterUiIntegration({
                'panel': 'lcars.ui.views.devEnvPanel:DevEnvPanel',
                'name': 'Dev Env'
            })
            self.DevEnv = {'panel': 'devEnv'}

        return self

class BackupPlugin:
    # Плагін резервного копіювання

    def __init__(self):
        self.Manager = None

    def Load(self, api: PluginApi, cfg: dict):
        from pathlib import Path
        import shutil
        import sqlite3
        import json
        import zipfile
        from datetime import datetime
        from lcars.modules.storage import ResolveChipPath

        # Шляхи
        root = Path(cfg.get('backupRoot', 'data/backups'))
        root.mkdir(parents=True, exist_ok=True)
        db_path = ResolveChipPath("Backup Archive Chip")

        class BackupManager:
            def __init__(self, root: Path, db: Path):
                self.Root = root
                self.Db = db
                self.InitDb()

            def InitDb(self):
                # Ініціалізація SQLite для архівів
                conn = sqlite3.connect(self.Db)
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS archives (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        source TEXT,
                        created TEXT,
                        size INTEGER,
                        path TEXT,
                        data BLOB
                    )
                ''')
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS exports (
                        id INTEGER PRIMARY KEY,
                        archive_id INTEGER,
                        path TEXT,
                        created TEXT,
                        FOREIGN KEY (archive_id) REFERENCES archives(id)
                    )
                ''')
                conn.commit()
                conn.close()
            # Створення бекапу
            def CreateBackup(self, source: str, name: Optional[str] = None, toDb: bool = False) -> Dict[str, Any]:
                src = Path(source)
                if not src.exists():
                    raise ValueError(f'Source not found: {source}')

                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                backupName = name or f'{src.name}{timestamp}'
                
                # Папковий бекап
                dst = self.Root / backupName
                shutil.copytree(src, dst, dirs_exist_ok=True)

                result = {'name': backupName, 'path': str(dst), 'db': False}

                # Архів в БД
                if toDb:
                    zipPath = self.Root / f'{backupName}.zip'
                    with zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for file in dst.rglob('*'):
                            if file.is_file():
                                zf.write(file, file.relative_to(dst))
                    
                    # Збереження в SQLite
                    conn = sqlite3.connect(self.Db)
                    with open(zipPath, 'rb') as f:
                        blob = f.read()
                    conn.execute(
                        'INSERT INTO archives (name, source, created, size, path, data) VALUES (?, ?, ?, ?, ?, ?)',
                        (backupName, str(src), timestamp, len(blob), str(zipPath), blob)
                    )
                    conn.commit()
                    conn.close()
                    zipPath.unlink()
                    result['db'] = True

                return result

            def Restore(self, backupName: str, target: str, fromDb: bool = False) -> str:
                # Відновлення
                dst = Path(target)
                
                if fromDb:
                    # Відновлення з БД
                    conn = sqlite3.connect(self.Db)
                    row = conn.execute(
                        'SELECT data FROM archives WHERE name = ? ORDER BY id DESC LIMIT 1',
                        (backupName,)
                    ).fetchone()
                    conn.close()
                    
                    if not row:
                        raise ValueError(f'Backup not found in DB: {backupName}')
                    
                    # Розпаковка
                    zipPath = self.Root / f'{backupName}Restore.zip'
                    with open(zipPath, 'wb') as f:
                        f.write(row[0])
                    
                    with zipfile.ZipFile(zipPath, 'r') as zf:
                        zf.extractall(dst)
                    zipPath.unlink()
                else:
                    # Відновлення з папки
                    src = self.Root / backupName
                    if not src.exists():
                        raise ValueError(f'Backup not found: {backupName}')
                    shutil.copytree(src, dst, dirs_exist_ok=True)

                return str(dst)

            def Export(self, backupName: str, externalPath: str) -> str:
                # Експорт за межі фреймворку
                conn = sqlite3.connect(self.Db)
                row = conn.execute(
                    'SELECT id, data FROM archives WHERE name = ? ORDER BY id DESC LIMIT 1',
                    (backupName,)
                ).fetchone()
                
                if not row:
                    conn.close()
                    raise ValueError(f'Backup not found: {backupName}')
                
                archiveId, blob = row
                
                # Збереження зовні
                ext = Path(externalPath)
                ext.parent.mkdir(parents=True, exist_ok=True)
                with open(ext, 'wb') as f:
                    f.write(blob)
                
                # Лог експорту
                conn.execute(
                    'INSERT INTO exports (archive_id, path, created) VALUES (?, ?, ?)',
                    (archiveId, str(ext), datetime.now().isoformat())
                )
                conn.commit()
                conn.close()
                
                return str(ext)

            def ListBackups(self) -> list:
                # Список бекапів з БД
                conn = sqlite3.connect(self.Db)
                rows = conn.execute(
                    'SELECT name, source, created, size FROM archives ORDER BY created DESC'
                ).fetchall()
                conn.close()
                return [
                    {'name': r[0], 'source': r[1], 'created': r[2], 'size': r[3]}
                    for r in rows
                ]

        self.Manager = BackupManager(root, db_path)
        api.RegisterBackup(self.Manager)
        return self


# ═════════════════════════════════════════════════════════════════════════════
# THEME Плагін управління темами LCARS
# ═════════════════════════════════════════════════════════════════════════════

class ThemePlugin:

    def __init__(self):
        self.Manager = None
        self.Preset = 'LCARS_25TH'

    def Load(self, api: PluginApi, cfg: dict):
        # Ініціалізація менеджера тем
        from lcars.base.default import DefaultPalette

        preset = cfg.get('defaultPreset', 'LCARS_25TH')
        self.Preset = preset

        class ThemeManager:
            def __init__(self, preset: str, palette):
                self.Preset = preset
                self.Palette = palette
                self.Schemes = {
                    'LCARS_25TH': palette,
                    'LCARS_24TH': self.Make24th(),
                    'TITAN': self.MakeTitan()
                }

            def Make24th(self):
                # 24 століття - класична TNG палітра
                return {
                    'Background': '#000000',
                    'Buttons': ['#FF9900', '#CC6600', '#FFCC99'],
                    'Panels': ['#3366CC', '#6699FF'],
                    'Accent': ['#CC0000', '#990000']
                }

            def MakeTitan(self):
                # Titan палітра - сіра
                return {
                    'Background': '#1A1A1A',
                    'Buttons': ['#606060', '#808080', '#A0A0A0'],
                    'Panels': ['#505050', '#707070'],
                    'Accent': ['#D37445', '#F0B942']
                }

            def GetPalette(self):
                return self.Schemes.get(self.Preset, self.Palette)

            def SetPreset(self, name: str):
                if name in self.Schemes:
                    self.Preset = name
                    return True
                return False

            def ListPresets(self):
                return list(self.Schemes.keys())

        self.Manager = ThemeManager(preset, DefaultPalette)
        api.RegisterTheme(self.Manager)
        return self


# БАЗОВИЙ КЛАС ДЛЯ ВСІХ ПЛАГІНІВ (TITANIUM PLUGIN BASE)
@dataclass
class Metadata:
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
        metadata: Optional[Metadata] = None,
        MetadataNode: Optional[Metadata] = None,
    ):
        if metadata is None:
            metadata = MetadataNode
        if metadata is None:
            metadata = Metadata(
                Name="Unknown",
                Version="0.0.1",
                Author="Anonymous",
                Description=""
            )
        self.metadata: Metadata = metadata
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
            return
        self.ActivePluginsMap[PluginIdStr] = PluginInstance

    def UnregisterPlugin(self, PluginIdStr: str):
        if PluginIdStr in self.ActivePluginsMap:
            del self.ActivePluginsMap[PluginIdStr]

    def GetPlugin(self, PluginIdStr: str) -> Optional[LCARSPlugin]:
        return self.ActivePluginsMap.get(PluginIdStr)

# МЕНЕДЖЕР ПЛАГІНІВ (TITANIUM PLUGIN MANAGER)
class Plugin(Service):
    Name = "plugin"
    Dependencies = []

    # Координатор пошуку та інтеграції зовнішніх модулів.
    def __init__(self):
        self.PluginsDirectory = None
        self.RegistryNode = PluginRegistry()
        self.LoadedModulesCache = {}

    def OnInit(self, KernelRef):
        self.Kernel = KernelRef
        self.PluginsDirectory = Path(self.Kernel.Root) / "plugins"

    def OnStart(self):
        self.LoadPlugins()

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
            return False
            
        ModuleInstance = importlib.import_module(ModuleNameStr)
        self.LoadedModulesCache[PluginIdStr] = ModuleInstance
        TargetNode = getattr(ModuleInstance, AttrNameStr, None)
        if not TargetNode:
            return False
            
        # Створення метаданих плагіна Titanium
        MetadataNode = Metadata(
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
            PluginInstance = TargetNode(Type.SystemaMap.get('config_schema', {}))
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
__all__ = [
    # API та базові класи
    'LCARSPlugin', 'PluginService', 'PluginRegistry', 'PluginApi',
    # Конкретні плагіни
    'AgentPlugin', 'BackupPlugin', 'ThemePlugin'
]

import importlib
import importlib.util
from pathlib import Path
from typing import Any, List, Optional

from lcars.core.service import Service
from lcars.core.signal import ODN
from lcars.base.version import getVersion

__version__ = getVersion()


class PluginService(Service):
    # Менеджер плагінів — координатор завантаження та інтеграції
    Name = "plugin"
    Dependencies = []

    def __init__(self):
        self.PluginsDirectory = None
        self.RegistryNode = PluginRegistry()
        self.LoadedModulesCache = {}

    def OnInit(self, KernelRef):
        self.Kernel = KernelRef
        self.PluginsDirectory = Path(self.Kernel.Root) / "plugins"
        ODN.Emit("Plugin.Service", "INITIALIZED")

    def OnStart(self):
        self.LoadPlugins()
        ODN.Emit("Plugin.Service", "PLUGINS_LOADED")

    def OnStop(self):
        ODN.Emit("Plugin.Service", "STOPPING")

    def LoadPlugins(self):
        return self.LoadAllDetectedPlugins()

    def DiscoverPlugins(self) -> List[Any]:
        if not self.PluginsDirectory.exists():
            return []
        return list(self.PluginsDirectory.glob("*.yaml"))

    def VerifyModuleNodePath(self, ModuleNameStr: str) -> bool:
        PathNodesArray = ModuleNameStr.split('.')
        CurrentPath = ""
        for Node in PathNodesArray:
            CurrentPath = f"{CurrentPath}.{Node}" if CurrentPath else Node
            if not importlib.util.find_spec(CurrentPath):
                return False
        return True

    def LoadPluginNode(self, DescriptorPath: Any) -> bool:
        import yaml
        from lcars.base.type import Type
        
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

        if not self.VerifyModuleNodePath(ModuleNameStr):
            return False

        ModuleInstance = importlib.import_module(ModuleNameStr)
        self.LoadedModulesCache[PluginIdStr] = ModuleInstance
        TargetNode = getattr(ModuleInstance, AttrNameStr, None)
        if not TargetNode:
            return False

        MetadataNode = Metadata(
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
            PluginInstance = TargetNode({})
            if not isinstance(PluginInstance, LCARSPlugin):
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
                ODN.Emit("Plugin.Loaded", {"id": PluginIdStr})
                return True
        return False

    def LoadAllDetectedPlugins(self) -> int:
        DescriptorList = self.DiscoverPlugins()
        CountVal = 0
        for PathNode in DescriptorList:
            if PathNode.name.startswith('_'):
                continue
            if self.LoadPluginNode(PathNode):
                CountVal += 1
        return CountVal

    def GetPlugin(self, PluginId: str) -> Optional[LCARSPlugin]:
        return self.RegistryNode.GetPlugin(PluginId)


# Аліаси для завантаження
PluginManager = PluginService

__all__ = ["PluginService", "PluginManager"]
