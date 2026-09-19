# ◤ PLUGIN CHIP MANAGER 🖖
# =============================================================================
# ФАЙЛ: lcars/modules/integrator.py
# ОПИС: Конвертація YAML плагінів в ізолінійні чіпи та управління ними.
#       Потік: YAML → DetectFaction → CalculateCapacity → Create Chip → Insert to Slot
# СТАНДАРТ: Titanium LCARS (Zero-Except, Strict PascalCase, Pure Classes).
# =============================================================================

from typing import Any, Optional, Dict, List
from pathlib import Path
from lcars.base.type import LCARS
from lcars.modules.library import ChipStatus, IsolinearChip, IsolinearBank


class IsolinearModule:
    def __init__(self, ModuleId: str, ParentChip: Any):
        self.ModuleId = ModuleId
        self.ParentChip = ParentChip
        self.Active = False
        self.EntryPoint: Optional[str] = None
        self.Instance: Any = None

    def Load(self, EntryPoint: str) -> bool:
        self.EntryPoint = EntryPoint
        if not EntryPoint:
            return False
        if ':' not in EntryPoint:
            return False
        EntryModule, EntryFunc = EntryPoint.split(':')
        Parts = EntryModule.split('.')
        Module = __import__(EntryModule, fromlist=[Parts[-1]] if Parts else [])
        InitFunc = getattr(Module, EntryFunc)
        self.Instance = InitFunc()
        return True

    def Activate(self) -> bool:
        if not self.ParentChip.Connected:
            return False
        if self.Instance is None:
            return False
        self.Active = True
        return True

    def Deactivate(self):
        self.Active = False


class ChipManager(IsolinearBank):
    def LoadFromYaml(self, YamlPath: Any) -> Optional[IsolinearChip]:
        PathRef = LCARS.Directive.Path(YamlPath)
        if not PathRef.exists():
            return None
        if not PathRef.is_file():
            return None
        FileContent = PathRef.read_text(encoding='utf-8')
        if FileContent is None:
            return None

        import yaml
        Data = yaml.safe_load(FileContent)
        if Data is None:
            return None
        if not isinstance(Data, dict):
            return None

        Metadata = Data.get('metadata', {})
        if 'id' not in Metadata:
            return None
        if 'name' not in Metadata:
            return None
        if 'version' not in Metadata:
            return None

        Faction = self.DetectFaction(Data)
        Specs = Data.get('specs', {})
        Capacity = Specs.get('capacity', 100)
        ColorCode = Specs.get('color_code', self.GetFactionColor(Faction))
        SecurityLevel = Specs.get('security_level', 1)

        RawId = Metadata['id']
        CleanId = RawId.replace('plugins.', '')
        Chip = self.AddChip(CleanId, Faction)

        Chip.Name = Metadata['name']
        Chip.Version = Metadata['version']
        Chip.Capacity = Capacity
        Chip.ColorCode = ColorCode
        Chip.SecurityLevel = SecurityLevel
        Chip.EntryPoints = Data.get('entrypoints', {})
        Chip.Config = Data.get('config', {})
        Chip.Dependencies = Data.get('dependencies', [])
        Chip.Paths = Data.get('paths', {})
        Chip.Interfaces = Data.get('interfaces', [])
        Chip.Tags = Data.get('tags', [])

        return Chip

    def LoadAllFromCategory(self, CategoryPath: Path) -> int:
        if not CategoryPath.exists():
            return 0
        if not CategoryPath.is_dir():
            return 0
        LoadedCount = 0
        for YamlFile in CategoryPath.glob('*.yaml'):
            Chip = self.LoadFromYaml(YamlFile)
            if Chip is not None:
                LoadedCount += 1
        return LoadedCount

    def DetectFaction(self, Data: Dict) -> str:
        Tags = Data.get('tags', [])
        Metadata = Data.get('metadata', {})
        NameLower = Metadata.get('name', '').lower()
        FactionKeywords = {
            'federation': 'Federation',
            'klingon': 'Klingon',
            'romulan': 'Romulan',
            'cardassian': 'Cardassian',
        }
        for Tag in Tags:
            TagLower = str(Tag).lower()
            if TagLower in FactionKeywords:
                return FactionKeywords[TagLower]
        for Keyword, FactionName in FactionKeywords.items():
            if Keyword in NameLower:
                return FactionName
        return 'Federation'

    def GetFactionColor(self, Faction: str) -> str:
        FactionColors = {
            'Federation': '#FF9900',
            'Klingon': '#CC0000',
            'Romulan': '#33CC33',
            'Cardassian': '#996600',
        }
        return FactionColors.get(Faction, '#99CCFF')

    def AutoInsertChips(self, Controller: Any) -> int:
        ActivatedCount = 0
        for ChipId, Chip in self.Chips.items():
            HasEntry = len(Chip.EntryPoints) > 0 if hasattr(Chip, 'EntryPoints') else False
            if HasEntry:
                Success = Controller.ActivateChip(ChipId)
                if Success:
                    ActivatedCount += 1
        return ActivatedCount


ManagerRef: Optional[ChipManager] = None

def GetManager() -> ChipManager:
    global ManagerRef
    if ManagerRef is None:
        ManagerRef = ChipManager()
    return ManagerRef


def Version() -> str:
    from lcars.base.info import getVersion
    return getVersion()


ComponentIntegrator = ChipManager

__all__ = [
    'IsolinearModule', 'ChipManager', 'ComponentIntegrator', 'GetManager'
]
