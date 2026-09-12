# ◤ LCARS ENGINEERING :: ISOLINEAR CHIP & STRATUM ARCHITECTURE 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/chips/architecture.py
# ОПИС: Головна суверенна архітектура ізолінійних чіпів (00..10) та інженерного шару.
#       Керує 11 категоріями оптичних чіпів зорельота, шинами ODN (ODN-00..ODN-10),
#       монтуванням у слоти, оперативним каталогом чіпів та виконанням entrypoints.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import SystemComponent, LCARS
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN

# Категорія ізолінійного чіпа
class ChipCategory(LCARS):
    def __init__(self, Code: str, Name: str, Bus: str, SecurityLevel: int, TargetPath: str, Description: str):
        super().__init__()
        self.Code = Code
        self.Name = Name
        self.Bus = Bus
        self.SecurityLevel = SecurityLevel
        self.TargetPath = TargetPath
        self.Description = Description

# Оптичний слот стійки ODN
class ChipSlot(SystemComponent):
    def __init__(self, CategoryCode: str, SlotNumber: int):
        super().__init__()
        self.CategoryCode = CategoryCode
        self.SlotNumber = SlotNumber
        self.MountedChipId = None
        self.IsOccupied = False
        self.Status = "EMPTY"

    def Mount(self, ChipId: str) -> None:
        self.MountedChipId = ChipId
        self.IsOccupied = True
        self.Status = "ONLINE"

    def Unmount(self) -> None:
        self.MountedChipId = None
        self.IsOccupied = False
        self.Status = "EMPTY"

# Головна ІСО-архітектура оптичних чіпів зорельота
class ISOArchitecture(SystemComponent):
    Instance = None

    Categories = {
        "00": ChipCategory("00", "System Kernel", "ODN-00", 10, "lcars/core/", "Ядро системи, бутстрап та системний контроль"),
        "01": ChipCategory("01", "Base Framework", "ODN-01", 9, "lcars/base/", "Базові типи, протоколи та геометрія LCARS"),
        "02": ChipCategory("02", "Engineering", "ODN-02", 7, "lcars/engineering/", "Фізичні підсистеми інженерного відсіку"),
        "03": ChipCategory("03", "Data Management", "ODN-03", 6, "lcars/modules/", "Бази даних та керування оперативною пам'яттю"),
        "04": ChipCategory("04", "AI ML Systems", "ODN-04", 8, "lcars/modules/", "Синтетичний інтелект та лінгвістичні матриці"),
        "05": ChipCategory("05", "Security Clearance", "ODN-05", 9, "lcars/system/", "Протоколи безпеки, блокування та рівні допуску"),
        "06": ChipCategory("06", "Communication", "ODN-06", 5, "lcars/service/", "Підпросторовий зв'язок та комунікаційні протоколи"),
        "07": ChipCategory("07", "Interface UI", "ODN-07", 4, "lcars/ui/", "Графічні консолі, PADD-панелі та InterfaceEditor"),
        "08": ChipCategory("08", "Storage Systems", "ODN-08", 5, "lcars/data/", "Файлові адаптери та носії сховищ"),
        "09": ChipCategory("09", "Simulation", "ODN-09", 6, "lcars/engineering/laboratory.py", "Фізичні симуляції часток та Geant4"),
        "10": ChipCategory("10", "Sensor Telemetry", "ODN-10", 6, "lcars/engineering/telemetry.py", "Сенсорна та телеметрична сітка корабля"),
    }

    def __init__(self):
        super().__init__()
        self.Catalog = {}
        self.Slots = {}
        self.ActiveBuses = {}
        self.InitializeSlots()
        self.ScanCategories()

    @classmethod
    def GetInstance(cls) -> ISOArchitecture:
        if cls.Instance is None:
            cls.Instance = ISOArchitecture()
        return cls.Instance

    def InitializeSlots(self) -> None:
        for CatCode in self.Categories:
            self.Slots[CatCode] = [ChipSlot(CatCode, SlotIndex) for SlotIndex in range(100)]
            self.ActiveBuses[CatCode] = self.Categories[CatCode].Bus

    def ScanCategories(self) -> dict:
        Yaml = LCARS.Storage.Yaml
        NewCatalog = {}
        for CatCode in self.Categories:
            NewCatalog[CatCode] = {}
            CatDir = LCARS.System.Path(f"lcars/engineering/chips/{CatCode}")
            if not CatDir.exists():
                continue
            for ManifestPath in CatDir.glob("*.yaml"):
                Text = ManifestPath.read_text(encoding="utf-8", errors="replace")
                Parsed = Yaml.safe_load(Text) if Yaml and hasattr(Yaml, "safe_load") else {}
                Meta = Parsed.get("Metadata") or Parsed.get("metadata") or {}
                ChipId = Meta.get("Id") or Meta.get("id") or Parsed.get("Id") or Parsed.get("id") or ManifestPath.stem
                ChipName = Meta.get("Name") or Meta.get("name", "Unknown Chip")
                Entrypoints = Parsed.get("Entrypoints") or Parsed.get("entrypoints") or {}
                Entry = Entrypoints.get("Main") or Entrypoints.get("main", "None")
                Paths = Parsed.get("Paths") or Parsed.get("paths") or {}
                Specs = Parsed.get("Specs") or Parsed.get("specs") or {}
                Database = Paths.get("DatabaseFile") or Paths.get("database_file", "")
                NewCatalog[CatCode][ChipId] = {
                    "Id": ChipId,
                    "Name": ChipName,
                    "Category": CatCode,
                    "FilePath": str(ManifestPath).replace("\\", "/"),
                    "Entrypoint": Entry,
                    "Status": "ONLINE",
                    "Specs": Specs,
                    "Paths": Paths,
                    "Database": Database,
                }
        self.Catalog = NewCatalog
        return self.Catalog

    def GetCategoryChips(self, CategoryCode: str) -> list[dict]:
        CatData = self.Catalog.get(CategoryCode, {})
        return list(CatData.values())

    def ResolveChip(self, ChipId: str) -> dict | None:
        for CatCode, Chips in self.Catalog.items():
            if ChipId in Chips:
                return Chips[ChipId]
        return None

    def MountChip(self, ChipId: str, SlotNumber: int | None = None) -> bool:
        Resolved = self.ResolveChip(ChipId)
        if not Resolved:
            return False
        CatCode = Resolved["Category"]
        CatSlots = self.Slots.get(CatCode, [])
        BusName = Resolved['Specs'].get('Bus') or Resolved['Specs'].get('bus', 'ODN-00')
        if SlotNumber is not None and 0 <= SlotNumber < len(CatSlots):
            TargetSlot = CatSlots[SlotNumber]
            TargetSlot.Mount(ChipId)
            ODN.Transmit(f"ODN.{BusName}.Mounted", ChipId=ChipId)
            return True
        for Slot in CatSlots:
            if not Slot.IsOccupied:
                Slot.Mount(ChipId)
                ODN.Transmit(f"ODN.{BusName}.Mounted", ChipId=ChipId)
                return True
        return False

    def UnmountChip(self, ChipId: str) -> bool:
        for CatCode, CatSlots in self.Slots.items():
            for Slot in CatSlots:
                if Slot.MountedChipId == ChipId:
                    Slot.Unmount()
                    ODN.Transmit("ODN.Chip.Unmounted", ChipId=ChipId)
                    return True
        return False

    def ExecuteEntrypoint(self, ChipId: str) -> any:
        Resolved = self.ResolveChip(ChipId)
        if not Resolved:
            return None
        Entry = Resolved.get("Entrypoint")
        ModulePath, AttrName = Entry.split(":")
        from lcars.service.bridge import Bridge
        ImportFunc = Bridge().Load("System.Module.Import")
        LoadedModule = ImportFunc(ModulePath)
        TargetClassOrFunc = getattr(LoadedModule, AttrName, None)
        return TargetClassOrFunc

# Канонічні точки доступу до ІСО-архітектури чіпів
ISOArchitectureCore = ISOArchitecture.GetInstance
ISO = ISOArchitecture.GetInstance()
IsolinearChipArchitecture = ISOArchitecture
ChipArchitecture = ISOArchitecture.GetInstance
ARCHITECTURE = ISOArchitecture.GetInstance()
