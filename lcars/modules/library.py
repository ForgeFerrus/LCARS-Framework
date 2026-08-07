# ◤ LCARS LIBRARY MODULE — v1.0
# Призначення: Бібліотечний сервіс для роботи з файлами, архівними секторами та ізолінійними чіпами
# Опис: Повноцінний менеджер локальної бібліотеки з управлінням IsolinearBank
# ВЕРСІЯ: Делегована з lcars.base.version

from typing import List, Dict, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, field
import hashlib
import shutil

from lcars.base.type import Directive, SystemComponent
from lcars.base.version import getVersion
from lcars.modules.storage import ListChipFiles, ResolveChipPath
from lcars.engineering.isolinear import (
    IsolinearChip, ChipSlot, ChipChannel, NetworkChannel, ChipStatus
)

__version__ = getVersion()

# ◤ ISOLINEAR BANK — управління банком чіпів
class IsolinearBank(SystemComponent):
    # Керує масивом ізолінійних чипів з підтримкою каналів, мережі та слотів

    # Конструктор банку ізолінійних чипів
    def __init__(self, DBDirectory: str = "database"):
        super().__init__()
        self.DBDirectory = Path(DBDirectory)
        self.Chips: Dict[str, IsolinearChip] = {}
        self.Channels: Dict[str, ChipChannel] = {}
        self.Networks: Dict[str, NetworkChannel] = {}
        self.Slots: Dict[str, ChipSlot] = {}

    def LoadBanks(self, Faction: str = "federation") -> None:
        # Сканування директорії на наявність чипів
        if not self.DBDirectory.exists():
            self.DBDirectory.mkdir(parents=True, exist_ok=True)
        ChipFiles = ListChipFiles() if str(self.DBDirectory).replace("\\", "/") == "database" else sorted(self.DBDirectory.glob("**/*.db"))
        for ChipFile in ChipFiles:
            Parts = ChipFile.stem.split("-", 2)
            ChipId = Parts[0] + "-" + Parts[1] if len(Parts) > 1 else ChipFile.stem
            self.Chips[ChipId] = IsolinearChip(ChipId, str(ChipFile), Faction)

    def GetChip(self, ChipId: str) -> Optional[IsolinearChip]:
        # Отримання чипа за ID
        return self.Chips.get(ChipId)

    def AddChip(self, ChipId: str, Faction: str = "federation") -> IsolinearChip:
        # Додавання нового чипа
        FilePath = ResolveChipPath(ChipId)
        Chip = IsolinearChip(ChipId, str(FilePath), Faction)
        self.Chips[ChipId] = Chip
        return Chip

    def ClusterStatus(self) -> Dict[str, Any]:
        # Статус кластера чіпів
        return {
            "Directory": str(self.DBDirectory),
            "ChipCount": len(self.Chips),
            "ChipIds": list(self.Chips.keys()),
        }

# ◤ ISOLINEAR REGISTRY — реєстр чіпів
@dataclass
class RegistryEntry:
    # Запис в реєстрі відповідності
    ChipId: str
    LibraryPath: str
    ModuleName: str
    Active: bool = False
    Metadata: Dict[str, Any] = field(default_factory=dict)

class IsolinearRegistry:
    # Реєстр відповідності чіп-бібліотека-модуль

    # Конструктор реєстру чіпів
    def __init__(self):
        self.Entries: Dict[str, RegistryEntry] = {}
        self.Libraries: Dict[str, List[str]] = {}
        self.LastError: Optional[str] = None

    def Register(self, ChipId: str, LibraryPath: str, ModuleName: str, Metadata: Optional[Dict] = None):
        # Реєстрація нового чіпа з прив'язкою до бібліотеки
        Entry = RegistryEntry(
            ChipId=ChipId,
            LibraryPath=LibraryPath,
            ModuleName=ModuleName,
            Metadata=Metadata or {}
        )
        self.Entries[ChipId] = Entry
        if LibraryPath not in self.Libraries:
            self.Libraries[LibraryPath] = []
        self.Libraries[LibraryPath].append(ChipId)

# Синглтон Bank
BankRef: Optional[IsolinearBank] = None

# Отримання синглтону банку ізолінійних чипів
def GetIsolinearBank() -> IsolinearBank:
    global BankRef
    if BankRef is None:
        BankRef = IsolinearBank()
    return BankRef

class Library(SystemComponent):
    # Менеджер локальної бібліотеки та архівних секторів.
    # Інтегрується з IsolinearBank для індексації файлів в базі даних чіпів.

    SectorMap = {
        "DOCUMENTS": ["federation", "science"],
        "IMAGES": ["federation"],
        "MEDIA": ["sports"],
        "EDUCATION": ["education"],
        "FEDERATION": ["federation"],
        "SPORTS": ["sports"],
        "SCIENCE": ["science"],
    }

    TypeMap = {
        ".txt": "TEXT", ".md": "TEXT", ".pdf": "DOCUMENT",
        ".png": "IMAGE", ".jpg": "IMAGE", ".jpeg": "IMAGE", ".gif": "IMAGE",
        ".mp4": "VIDEO", ".mkv": "VIDEO", ".avi": "VIDEO",
        ".mp3": "AUDIO", ".wav": "AUDIO",
        ".py": "CODE", ".json": "DATA", ".yaml": "DATA", ".xml": "DATA"
    }

    # Конструктор менеджера бібліотеки
    def __init__(self, basePath: Optional[str] = None, bank: Optional[IsolinearBank] = None):
        super().__init__()
        from pathlib import Path
        self.Root = Path(basePath or "lcars/data/archives").resolve()
        self.Bank = bank or GetIsolinearBank()

    def GetSectors(self) -> List[str]:
        # Отримання списку доступних секторів
        return list(self.SectorMap.keys())

    def GetFileType(self, ext: str) -> str:
        # Визначення типу файлу за розширенням
        return self.TypeMap.get(ext.lower(), "UNKNOWN")

    def ScanFiles(self, sector: str) -> List[Dict[str, Any]]:
        # Сканування файлів сектора
        TaskId = f"LIB-{Directive.Chronon.now().microsecond % 1000:03d}"
        Records = []

        Folders = self.SectorMap.get(sector.upper(), [sector.lower().replace(" ", "_")])
        for Folder in Folders:
            FolderPath = self.Root / Folder
            if not FolderPath.exists():
                continue

            for Entry in FolderPath.iterdir():
                if Entry.is_file():
                    Stat = Entry.stat()
                    Ext = Entry.suffix.lower()
                    Records.append({
                        "name": Entry.name,
                        "type": self.GetFileType(Ext),
                        "size": Stat.st_size,
                        "sizeFormatted": f"{Stat.st_size / 1024:.1f} KB",
                        "path": str(Entry),
                        "relativePath": str(Entry.relative_to(self.Root)),
                        "modified": Stat.st_mtime,
                        "sector": sector.upper()
                    })

        print(f"◤ LIBRARY :: SCAN_COMPLETE: {TaskId}. Found {len(Records)} files in {sector}.")
        return Records

    def AddFile(self, sector: str, sourcePath: str, newName: Optional[str] = None) -> Dict[str, Any]:
        # Додавання файлу до бібліотеки
        Src = Path(sourcePath).resolve()
        if not Src.exists():
            return {"success": False, "error": "Source file not found"}

        Folders = self.SectorMap.get(sector.upper(), [sector.lower().replace(" ", "_")])
        TargetFolder = self.Root / Folders[0]
        TargetFolder.mkdir(parents=True, exist_ok=True)

        DestName = newName or Src.name
        DestPath = TargetFolder / DestName

        shutil.copy2(Src, DestPath)

        # Індексація в IsolinearBank
        self.IndexFile(sector, DestPath)

        return {"success": True, "path": str(DestPath), "name": DestName}

    def RemoveFile(self, filePath: str) -> Dict[str, Any]:
        # Видалення файлу з бібліотеки
        Target = Path(filePath).resolve()
        if not Target.exists():
            return {"success": False, "error": "File not found"}

        Target.unlink()
        return {"success": True, "message": f"Removed: {Target.name}"}

    def FindFiles(self, pattern: str, sector: Optional[str] = None) -> List[Dict[str, Any]]:
        # Пошук файлів за шаблоном
        Results = []
        Sectors = [sector.upper()] if sector else self.GetSectors()

        for Sec in Sectors:
            Files = self.ScanFiles(Sec)
            for File in Files:
                if pattern.lower() in File["name"].lower():
                    Results.append(File)

        return Results

    def GetFileInfo(self, filePath: str) -> Dict[str, Any]:
        # Отримання детальної інформації про файл
        Target = Path(filePath).resolve()
        if not Target.exists():
            return {"success": False, "error": "File not found"}

        Stat = Target.stat()
        Content = Target.read_bytes()
        Hash = hashlib.md5(Content).hexdigest()

        return {
            "success": True,
            "name": Target.name,
            "path": str(Target),
            "type": self.GetFileType(Target.suffix),
            "size": Stat.st_size,
            "sizeFormatted": f"{Stat.st_size / 1024:.1f} KB",
            "md5": Hash,
            "modified": Stat.st_mtime,
            "created": Stat.st_ctime
        }

    def IndexFile(self, sector: str, filePath: Path) -> bool:
        # Індексація файлу в IsolinearBank (archives чіп)
        Chip = self.Bank.GetChip("archives")
        if Chip is None:
            return False

        RelPath = str(filePath.relative_to(self.Root))
        Query = "INSERT OR REPLACE INTO archives (item_class, tag, data) VALUES (?, ?, ?)"
        return Chip.ExecuteQuery(Query, (sector.upper(), filePath.suffix.lstrip('.').upper(), RelPath)) is True

    def SyncWithBank(self) -> Dict[str, Any]:
        # Синхронізація всіх файлів з IsolinearBank
        TotalIndexed = 0
        for Sector in self.GetSectors():
            Files = self.ScanFiles(Sector)
            for File in Files:
                PathObj = Path(File["path"])
                if self.IndexFile(Sector, PathObj):
                    TotalIndexed += 1

        return {"success": True, "indexed": TotalIndexed}

    def ListFiles(self, sector: str) -> List[Dict[str, Any]]:
        # Сумісність: повертає список файлів сектора
        return self.ScanFiles(sector)

# Синглтони
LibraryInstance = Library()
BankRef = GetIsolinearBank()

def GetLibrary() -> Library:
    # Отримання синглтону бібліотеки
    return LibraryInstance

__all__ = [
    "Library", "LibraryInstance", "GetLibrary",
    "IsolinearBank", "IsolinearRegistry", "RegistryEntry", "GetIsolinearBank"
]
