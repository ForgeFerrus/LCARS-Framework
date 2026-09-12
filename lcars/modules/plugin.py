# ◤ LCARS PLUGIN MODULE 🖖
# =============================================================================
# ФАЙЛ: lcars/modules/plugin.py
# ОПИС: Модуль плагінів LCARS Framework.
#       Базові класи, реєстр, конкретні плагіни, менеджер виявлення та завантаження.
#       ВІДПОВІДАЛЬНІСТЬ:
#       1. Metadata / LCARSPlugin — контракт та метадані будь-якого плагіна.
#       2. PluginRegistry — реєстр активних плагінів.
#       3. ExtensionApi — API для реєстрації плагінних компонентів.
#       4. AgentPlugin / BackupPlugin / ThemePlugin — конкретні реалізації.
#       5. PluginManager — менеджер виявлення YAML-дескрипторів і завантаження.
# СТАНДАРТ: Titanium LCARS (Zero-Except, Strict PascalCase, Pure Classes).
# =============================================================================

import importlib
import importlib.util
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List

from lcars.base.type import SystemComponent
from lcars.base.info import getVersion

__version__ = getVersion()


# ═════════════════════════════════════════════════════════════════════════════
# 1. МЕТАДАНІ ПЛАГІНА
# ═════════════════════════════════════════════════════════════════════════════
@dataclass
class Metadata:
    Name: str
    Version: str
    Author: str
    Description: str
    Dependencies: List[str] = field(default_factory=list)
    Id: str = ""
    Entrypoint: str = ""


# ═════════════════════════════════════════════════════════════════════════════
# 2. БАЗОВИЙ КЛАС ПЛАГІНА
# ═════════════════════════════════════════════════════════════════════════════
class LCARSPlugin(ABC):
    def __init__(self, metadata: Optional[Metadata] = None, MetadataNode: Optional[Metadata] = None):
        if metadata is None:
            metadata = MetadataNode
        if metadata is None:
            metadata = Metadata(Name="Unknown", Version="0.0.1", Author="Anonymous", Description="")
        self.metadata: Metadata = metadata
        self.IsLoaded = False
        self.IsEnabled = False
        self.ExportMap: Dict[str, Any] = {}

    @abstractmethod
    def OnLoad(self) -> bool:
        pass

    @abstractmethod
    def OnUnload(self) -> bool:
        pass

    def OnStartup(self):
        pass

    def OnShutdown(self):
        pass

    def Export(self, NameKey: str, ValueNode: Any):
        self.ExportMap[NameKey] = ValueNode

    def GetExport(self, NameKey: str) -> Optional[Any]:
        return self.ExportMap.get(NameKey)


# ═════════════════════════════════════════════════════════════════════════════
# 3. API ДЛЯ ПЛАГІНІВ
# ═════════════════════════════════════════════════════════════════════════════
class ExtensionApi:
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
# 4. РЕЄСТР АКТИВНИХ ПЛАГІНІВ
# ═════════════════════════════════════════════════════════════════════════════
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

    def ListPlugins(self) -> List[str]:
        return list(self.ActivePluginsMap.keys())


# ═════════════════════════════════════════════════════════════════════════════
# 5. YAML УТИЛІТИ
# ═════════════════════════════════════════════════════════════════════════════
def ReadPluginYaml(PathVal: Path) -> Optional[Dict[str, Any]]:
    Yaml = importlib.import_module("yaml")
    with PathVal.open('r', encoding='utf-8') as F:
        return Yaml.safe_load(F)


def DiscoverPlugins(Root: Optional[str] = None) -> List[Dict[str, Any]]:
    RootPath = Path(Root) if Root else Path(__file__).parent.parent / "plugins"
    Plugins = []
    if not RootPath.exists():
        return []
    for Child in RootPath.iterdir():
        if Child.is_dir():
            Desc = Child / 'plugin.yaml'
            if Desc.exists():
                Meta = ReadPluginYaml(Desc)
                if Meta:
                    Meta['Path'] = str(Child)
                    Plugins.append(Meta)
    return Plugins


# ═════════════════════════════════════════════════════════════════════════════
# 6. КОНКРЕТНІ ПЛАГІНИ
# ═════════════════════════════════════════════════════════════════════════════

class AgentPlugin(LCARSPlugin):
    def __init__(self, metadata: Optional[Metadata] = None, MetadataNode: Optional[Metadata] = None):
        super().__init__(metadata, MetadataNode)
        self.Copilot = None
        self.Provider = None
        self.Computer = None
        self.NovaAdapter = None
        self.DevEnv = None

    def OnLoad(self) -> bool:
        return True

    def OnUnload(self) -> bool:
        return True

    def Load(self, api, cfg: dict):
        from lcars.service.copilot import Copilot
        self.Copilot = Copilot(project_root='.')
        AllowShell = cfg.get('allowShell', False)
        self.Copilot.ShellEnabled = AllowShell
        api.RegisterAgent(self.Copilot)

        from lcars.service.provider import AIProviderManager
        self.Provider = AIProviderManager()
        api.RegisterAiProvider('default', self.Provider)
        api.RegisterAiProvider('groq', self.Provider)

        from lcars.service.onboard import GetComputer
        self.Computer = GetComputer()
        api.RegisterDiscovery(self.Computer)

        self.NovaAdapter = NovaActAdapter(self.Computer, cfg.get('nova', {}))
        if cfg.get('nova', {}).get('autoConnect', False):
            self.NovaAdapter.Connect(useSdk=cfg.get('nova', {}).get('useSdk', False))
        api.RegisterDiscovery(self.NovaAdapter)

        if cfg.get('devEnv', True):
            api.RegisterUiIntegration({'panel': 'lcars.ui.views.devEnvPanel:DevEnvPanel', 'name': 'Dev Env'})
            self.DevEnv = {'panel': 'devEnv'}

        return self


class BackupPlugin(LCARSPlugin):
    def __init__(self, metadata: Optional[Metadata] = None, MetadataNode: Optional[Metadata] = None):
        super().__init__(metadata, MetadataNode)
        self.Manager = None

    def OnLoad(self) -> bool:
        return True

    def OnUnload(self) -> bool:
        return True

    def Load(self, api, cfg: dict):
        Root = Path(cfg.get('backupRoot', 'data/backups'))
        Root.mkdir(parents=True, exist_ok=True)
        DbPath = Root / 'backups.db'
        self.Manager = BackupManager(Root, DbPath)
        api.RegisterBackup(self.Manager)
        return self


class ThemePlugin(LCARSPlugin):
    def __init__(self, metadata: Optional[Metadata] = None, MetadataNode: Optional[Metadata] = None):
        super().__init__(metadata, MetadataNode)
        self.Manager = None
        self.Preset = 'LCARS_25TH'

    def OnLoad(self) -> bool:
        return True

    def OnUnload(self) -> bool:
        return True

    def Load(self, api, cfg: dict):
        from lcars.base.default import DefaultPalette
        Preset = cfg.get('defaultPreset', 'LCARS_25TH')
        self.Preset = Preset
        self.Manager = ThemeManager(Preset, DefaultPalette)
        api.RegisterTheme(self.Manager)
        return self


# ═════════════════════════════════════════════════════════════════════════════
# 7. ДОПОМОЖНІ КЛАСИ ДЛЯ ПЛАГІНІВ
# ═════════════════════════════════════════════════════════════════════════════

class NovaActAdapter:
    def __init__(self, computer=None, config=None):
        self.computer = computer
        self.config = config or {}
        self.connected = False
        self.sdk_ready = False

    def Connect(self, useSdk=False):
        if useSdk and self.config.get('useSdk'):
            import threading
            threading.Thread(target=self.InitSdk, daemon=True).start()
        self.connected = True
        return True

    def InitSdk(self):
        import time
        time.sleep(1)
        self.sdk_ready = True


class BackupManager:
    def __init__(self, root: Path, db: Path):
        self.Root = root
        self.Db = db
        self.InitDb()

    def InitDb(self):
        import sqlite3
        Conn = sqlite3.connect(self.Db)
        Conn.execute('''CREATE TABLE IF NOT EXISTS archives (
            id INTEGER PRIMARY KEY, name TEXT, source TEXT, created TEXT,
            size INTEGER, path TEXT, data BLOB)''')
        Conn.execute('''CREATE TABLE IF NOT EXISTS exports (
            id INTEGER PRIMARY KEY, archive_id INTEGER, path TEXT,
            created TEXT, FOREIGN KEY (archive_id) REFERENCES archives(id))''')
        Conn.commit()
        Conn.close()

    def CreateBackup(self, source: str, name=None, toDb: bool = False):
        import zipfile, shutil, sqlite3
        from datetime import datetime
        Src = Path(source)
        if not Src.exists():
            return {"error": f"Source not found: {source}"}
        Timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        BackupName = name or f'{Src.name}{Timestamp}'
        Dst = self.Root / BackupName
        shutil.copytree(Src, Dst, dirs_exist_ok=True)
        Result = {'name': BackupName, 'path': str(Dst), 'db': False}
        if toDb:
            ZipPath = self.Root / f'{BackupName}.zip'
            with zipfile.ZipFile(ZipPath, 'w', zipfile.ZIP_DEFLATED) as Zf:
                for FileItem in Dst.rglob('*'):
                    if FileItem.is_file():
                        Zf.write(FileItem, FileItem.relative_to(Dst))
            Conn = sqlite3.connect(self.Db)
            with open(ZipPath, 'rb') as F:
                Blob = F.read()
            Conn.execute('INSERT INTO archives (name, source, created, size, path, data) VALUES (?, ?, ?, ?, ?, ?)',
                         (BackupName, str(Src), Timestamp, len(Blob), str(ZipPath), Blob))
            Conn.commit()
            Conn.close()
            ZipPath.unlink()
            Result['db'] = True
        return Result

    def Restore(self, backupName: str, target: str, fromDb: bool = False):
        import shutil, sqlite3, zipfile
        Dst = Path(target)
        if fromDb:
            Conn = sqlite3.connect(self.Db)
            Row = Conn.execute('SELECT data FROM archives WHERE name = ? ORDER BY id DESC LIMIT 1', (backupName,)).fetchone()
            Conn.close()
            if not Row:
                return f"Backup not found in DB: {backupName}"
            ZipPath = self.Root / f'{backupName}Restore.zip'
            with open(ZipPath, 'wb') as F:
                F.write(Row[0])
            with zipfile.ZipFile(ZipPath, 'r') as Zf:
                Zf.extractall(Dst)
            ZipPath.unlink()
        else:
            Src = self.Root / backupName
            if not Src.exists():
                return f"Backup not found: {backupName}"
            shutil.copytree(Src, Dst, dirs_exist_ok=True)
        return str(Dst)

    def Export(self, backupName: str, externalPath: str):
        import sqlite3
        Conn = sqlite3.connect(self.Db)
        Row = Conn.execute('SELECT id, data FROM archives WHERE name = ? ORDER BY id DESC LIMIT 1', (backupName,)).fetchone()
        if not Row:
            Conn.close()
            return f"Backup not found: {backupName}"
        ArchiveId, Blob = Row
        Ext = Path(externalPath)
        Ext.parent.mkdir(parents=True, exist_ok=True)
        with open(Ext, 'wb') as F:
            F.write(Blob)
        from datetime import datetime
        Conn.execute('INSERT INTO exports (archive_id, path, created) VALUES (?, ?, ?)',
                     (ArchiveId, str(Ext), datetime.now().isoformat()))
        Conn.commit()
        Conn.close()
        return str(Ext)

    def ListBackups(self):
        import sqlite3
        Conn = sqlite3.connect(self.Db)
        Rows = Conn.execute('SELECT name, source, created, size FROM archives ORDER BY created DESC').fetchall()
        Conn.close()
        return [{'name': R[0], 'source': R[1], 'created': R[2], 'size': R[3]} for R in Rows]


class ThemeManager:
    def __init__(self, preset: str, palette):
        self.Preset = preset
        self.Palette = palette
        self.Schemes = {'LCARS_25TH': palette, 'LCARS_24TH': self.Make24th(), 'TITAN': self.MakeTitan()}

    def Make24th(self):
        return {'Background': '#000000', 'Buttons': ['#FF9900', '#CC6600', '#FFCC99'],
                'Panels': ['#3366CC', '#6699FF'], 'Accent': ['#CC0000', '#990000']}

    def MakeTitan(self):
        return {'Background': '#1A1A1A', 'Buttons': ['#606060', '#808080', '#A0A0A0'],
                'Panels': ['#505050', '#707070'], 'Accent': ['#D37445', '#F0B942']}

    def GetPalette(self):
        return self.Schemes.get(self.Preset, self.Palette)

    def SetPreset(self, name: str) -> bool:
        if name in self.Schemes:
            self.Preset = name
            return True
        return False

    def ListPresets(self):
        return list(self.Schemes.keys())


# ═════════════════════════════════════════════════════════════════════════════
# 8. МЕНЕДЖЕР ПЛАГІНІВ
# ═════════════════════════════════════════════════════════════════════════════
class PluginManager:
    def __init__(self, PluginsRoot: Optional[Path] = None):
        self.PluginsDirectory = PluginsRoot
        self.RegistryNode = PluginRegistry()
        self.Api = ExtensionApi()
        self.LoadedModulesCache: Dict[str, Any] = {}

    def SetRoot(self, Root: Path):
        self.PluginsDirectory = Root

    def DiscoverPlugins(self) -> List[Path]:
        if not self.PluginsDirectory or not self.PluginsDirectory.exists():
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

    def LoadPluginNode(self, DescriptorPath: Path) -> bool:
        Yaml = importlib.import_module("yaml")
        with open(DescriptorPath, 'r', encoding='utf-8') as FileNode:
            DataMap = Yaml.safe_load(FileNode)
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
            Name=DataMap.get('name', 'Unknown'), Version=str(DataMap.get('version', '0.0.1')),
            Author=DataMap.get('author', 'Anonymous'), Description=DataMap.get('description', ''),
            Id=PluginIdStr, Entrypoint=EntrypointStr, Dependencies=DataMap.get('dependencies', []))
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

    def ListPlugins(self) -> List[str]:
        return self.RegistryNode.ListPlugins()


# ═════════════════════════════════════════════════════════════════════════════
# ЕКСПОРТ МОДУЛЯ
# ═════════════════════════════════════════════════════════════════════════════
__all__ = [
    'Metadata', 'LCARSPlugin', 'ExtensionApi', 'PluginRegistry',
    'PluginManager', 'AgentPlugin', 'BackupPlugin', 'ThemePlugin',
    'ReadPluginYaml', 'DiscoverPlugins',
]
