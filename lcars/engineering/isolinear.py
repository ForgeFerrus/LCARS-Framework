# LCARS ISOLINEAR NETWORK
# Призначення: технічне ядро ізолінійної мережі, чіпів, чорної скриньки та YAML-карт.
# Тут живе інженерний рівень. UI, програми і запускалки мають бути в інших секціях.

import json
import logging
import sqlite3
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from time import time
from typing import Any, Dict, List, Optional

if find_spec("yaml") is not None:
    import yaml
else:
    yaml = None

from lcars.core.service import Service
from lcars.modules.storage import ChipPath, ResolveChipPath

log = logging.getLogger("Isolinear")


class ChipStatus:
    # Стан чіпа в ізолінійній мережі.
    ONLINE = "online"
    OFFLINE = "offline"
    FAULT = "fault"


class ChipSlot:
    # Простий слот для чіпа.
    def __init__(self, SlotId):
        self.SlotId = SlotId
        self.ActiveChip = None


class ChipChannel:
    # Канал, через який чіп підключається до мережі.
    def __init__(self, ChannelId):
        self.ChannelId = ChannelId
        self.Active = True


class NetworkChannel:
    # Лінія передачі з базовою швидкістю.
    def __init__(self, ChannelId):
        self.ChannelId = ChannelId
        self.Speed = 1000


@dataclass(init=False)
class IsolinearChip:
    id: str
    array: str
    metadata: Dict
    Faction: str
    status: str
    memory_usage: int
    cpu_usage: int
    data: Dict
    FilePath: Optional[Path]
    Connection: Any
    Connected: bool

    # Створюємо чіп і зберігаємо сумісність зі старим позиційним викликом.
    def __init__(
        self,
        id: str,
        array: str,
        metadata: Any = None,
        Faction: str = "federation",
        status: str = "OFFLINE",
        memory_usage: int = 0,
        cpu_usage: int = 0,
        data: Optional[Dict] = None,
        FilePath: Optional[Path] = None,
        Connection: Any = None,
        Connected: bool = False,
    ):
        if isinstance(metadata, dict):
            Meta = dict(metadata)
        else:
            Meta = {}
            if metadata is not None and Faction == "federation":
                Faction = str(metadata)

        self.id = id
        self.array = array
        self.metadata = Meta
        self.Faction = Faction
        self.status = status
        self.memory_usage = memory_usage
        self.cpu_usage = cpu_usage
        self.data = dict(data or {})
        self.FilePath = FilePath
        self.Connection = Connection
        self.Connected = Connected

    # Підключаємо локальну базу чіпа.
    def Connect(self) -> bool:
        if self.FilePath is None:
            return False
        self.FilePath.parent.mkdir(parents=True, exist_ok=True)
        self.Connection = sqlite3.connect(str(self.FilePath))
        self.Connected = True
        return True

    # Відключаємо локальну базу чіпа.
    def Disconnect(self) -> None:
        if self.Connection is not None:
            self.Connection.close()
            self.Connection = None
        self.Connected = False

    # Виконуємо SQL-запит у файлі чіпа.
    def ExecuteQuery(self, Query: str, Params=None) -> bool:
        if not self.Connected:
            self.Connect()
        if self.Connection is None:
            return False

        Cursor = self.Connection.cursor()
        if Params is not None:
            Cursor.execute(Query, Params)
        else:
            Cursor.execute(Query)
        self.Connection.commit()
        return True

    # Повертаємо технічний стан чіпа.
    def GetStatus(self) -> dict[str, Any]:
        return {
            "ChipId": self.id,
            "Array": self.array,
            "Status": self.status,
            "Faction": self.Faction,
            "Connected": self.Connected,
            "Path": str(self.FilePath) if self.FilePath else "",
        }


# Банк чіпів для базової роботи з ізолінійною пам'яттю.
class IsolinearBank:
    # Приймаємо старі аргументи, але використовуємо лише директорію бази.
    def __init__(self, DBDirectory: str = "database", *Args: Any, **Kwargs: Any):
        self.DBDirectory = Path(DBDirectory)
        self.Chips: Dict[str, IsolinearChip] = {}
        self.Channels: Dict[str, ChipChannel] = {}
        self.Networks: Dict[str, NetworkChannel] = {}
        self.Slots: Dict[str, ChipSlot] = {}

    # Додаємо чіп у банк.
    def AddChip(self, ChipId, Faction="federation"):
        PathRef = ResolveChipPath(str(ChipId))
        Chip = IsolinearChip(
            id=ChipId,
            array="LEGACY",
            metadata={"faction": Faction},
            Faction=Faction,
            FilePath=PathRef,
        )
        self.Chips[ChipId] = Chip
        return Chip

    # Повертаємо чіп за ідентифікатором.
    def GetChip(self, ChipId):
        return self.Chips.get(ChipId)

    # Завантажуємо існуючі чіпи з директорії бази.
    def LoadBanks(self, Faction: str = "federation") -> None:
        if not self.DBDirectory.exists():
            self.DBDirectory.mkdir(parents=True, exist_ok=True)
        for ChipFile in self.DBDirectory.glob("**/*.db"):
            Parts = ChipFile.stem.split("-", 2)
            ChipId = Parts[0] + "-" + Parts[1] if len(Parts) > 1 else ChipFile.stem
            if ChipId not in self.Chips:
                self.AddChip(ChipId, Faction)

    # Повертаємо короткий діагностичний стан банку.
    def ClusterStatus(self) -> Dict[str, Any]:
        return {
            "Directory": str(self.DBDirectory),
            "ChipCount": len(self.Chips),
            "ChipIds": list(self.Chips.keys()),
            "ChannelCount": len(self.Channels),
            "NetworkCount": len(self.Networks),
            "SlotCount": len(self.Slots),
        }


# Легкий модуль, прив'язаний до батьківського чіпа.
class IsolinearModule:
    # Тут лише зв'язок з основним чіпом.
    def __init__(self, ModuleId, ParentChip):
        self.ModuleId = ModuleId
        self.ParentChip = ParentChip


# Чорна скринька ODN: журнал сигналів, каналів і технічних подій.
class BlackBox(IsolinearChip):
    # Готуємо чорну скриньку до запису.
    def __init__(
        self,
        id: str = "01-0004",
        array: str = "01",
        metadata: Optional[Dict] = None,
        FilePath: str | Path | None = None,
    ):
        Meta = dict(metadata or {})
        Meta.setdefault("name", "ODN Black Box")
        Meta.setdefault("type", "database")
        Meta.setdefault("role", "ODN_TRANSMISSION_RECORDER")
        super().__init__(
            id=id,
            array=array,
            metadata=Meta,
            status="OFFLINE",
            data={},
            FilePath=Path(FilePath) if FilePath else Path("lcars/database/01/01-0004-odn-black-box.db"),
        )
        self.ChipName = "ODN Black Box"
        self.Prepare()

    # Створюємо таблиці ідентичності чіпа та журналу подій.
    def Prepare(self) -> None:
        if not self.Connect():
            return

        Conn = self.Connection
        if Conn is None:
            return

        Cursor = Conn.cursor()
        Cursor.execute(
            "CREATE TABLE IF NOT EXISTS ChipIdentity ("
            "ChipId TEXT PRIMARY KEY,"
            "ChipName TEXT NOT NULL,"
            "Sector TEXT NOT NULL,"
            "Role TEXT NOT NULL,"
            "Created REAL NOT NULL"
            ")"
        )
        Cursor.execute(
            "CREATE TABLE IF NOT EXISTS ODNLog ("
            "Id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "Stamp REAL NOT NULL,"
            "Channel TEXT NOT NULL,"
            "GroupName TEXT,"
            "SignalName TEXT,"
            "Args TEXT,"
            "Kwargs TEXT"
            ")"
        )
        Cursor.execute(
            "CREATE TABLE IF NOT EXISTS ODNChannel ("
            "Name TEXT PRIMARY KEY,"
            "Created REAL NOT NULL,"
            "LastStamp REAL"
            ")"
        )
        Cursor.execute(
            "INSERT OR IGNORE INTO ChipIdentity (ChipId, ChipName, Sector, Role, Created) VALUES (?, ?, ?, ?, ?)",
            (self.id, self.ChipName, self.array, "ODN_TRANSMISSION_RECORDER", time()),
        )
        Conn.commit()

    # Перетворюємо дані в JSON для запису.
    def Pack(self, Value: Any) -> str:
        return json.dumps(Value, ensure_ascii=False, default=str)

    # Реєструємо канал у чорній скриньці.
    def RegisterChannel(self, Name: str) -> None:
        Stamp = time()
        if not self.Connect():
            return
        Conn = self.Connection
        if Conn is None:
            return
        Cursor = Conn.cursor()
        Cursor.execute(
            "INSERT OR IGNORE INTO ODNChannel (Name, Created, LastStamp) VALUES (?, ?, ?)",
            (Name, Stamp, Stamp),
        )
        Conn.commit()

    # Записуємо одну подію в чорну скриньку.
    def Record(self, Channel: str, GroupName: str | None, SignalName: str | None, Args: tuple, Kwargs: dict) -> None:
        if not self.Connect():
            return
        Conn = self.Connection
        if Conn is None:
            return

        Cursor = Conn.cursor()
        Cursor.execute(
            "INSERT INTO ODNLog (Stamp, Channel, GroupName, SignalName, Args, Kwargs) VALUES (?, ?, ?, ?, ?, ?)",
            (
                time(),
                Channel,
                GroupName,
                SignalName,
                self.Pack(Args),
                self.Pack(Kwargs),
            ),
        )
        Conn.commit()

    # Рахуємо кількість записів у журналі.
    def Count(self) -> int:
        if not self.Connect():
            return 0
        Conn = self.Connection
        if Conn is None:
            return 0
        Cursor = Conn.cursor()
        Cursor.execute("SELECT COUNT(*) FROM ODNLog")
        Row = Cursor.fetchone()
        return int(Row[0]) if Row else 0

    # Повертаємо компактний стан чорної скриньки.
    def GetStatus(self) -> Dict[str, Any]:
        return {
            "ChipId": self.id,
            "ChipName": self.ChipName,
            "Path": str(self.FilePath),
            "Entries": self.Count(),
        }


# Головний сервіс ізолінійної мережі.
class IsolinearCore(Service):
    # Створюємо ядро мережі та карту для розміщення чіпів.
    def __init__(self):
        super().__init__()
        self.Name = "isolinear"
        from lcars.core.matrix import SystemMatrix

        self.StorageMatrix = SystemMatrix([11, 100, 10], Id="IsolinearStorage")
        self.Chips: Dict[str, IsolinearChip] = {}
        self.RootPath = Path("lcars/engineering/chips")
        self.DbPath = Path("lcars/engineering/chips_db.json")
        self.DbData: Dict[str, Dict[str, Any]] = {}

    # Запускаємо завантаження карти та чіпів.
    def OnStart(self) -> None:
        log.info("Initializing Isolinear Optical Data Network...")
        self.LoadDatabase()
        self.ScanChips()

    # Зберігаємо карту перед зупинкою.
    def OnStop(self) -> None:
        self.SaveDatabase()
        log.info("Isolinear Optical Data Network offline.")

    # Завантажуємо карту чіпів з JSON.
    def LoadDatabase(self):
        if self.DbPath.exists():
            with open(self.DbPath, "r", encoding="utf-8") as File:
                self.DbData = json.load(File)
        else:
            self.InitEmptyDatabase()

    # Створюємо порожню карту для нової бази.
    def InitEmptyDatabase(self):
        self.DbData = {f"{Index:02d}": {} for Index in range(11)}
        self.SaveDatabase()

    # Зберігаємо карту чіпів назад у JSON.
    def SaveDatabase(self):
        self.DbPath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.DbPath, "w", encoding="utf-8") as File:
            json.dump(self.DbData, File, indent=2)

    # Скануємо YAML-чіпи всередині інженерної секції.
    def ScanChips(self):
        if not self.RootPath.exists():
            self.RootPath.mkdir(parents=True, exist_ok=True)
            return

        for ArrayDir in self.RootPath.iterdir():
            if ArrayDir.is_dir():
                ArrayName = ArrayDir.name
                for ChipFile in ArrayDir.glob("*.yaml"):
                    self.LoadChip(ChipFile, ArrayName)

    # Завантажуємо один YAML-чіп і ставимо його в карту масиву.
    def LoadChip(self, FilePath: Path, ArrayName: str):
        from lcars.base.version import getVersion

        # YAML є опційним: ядро має стартувати навіть без цього пакета.
        if yaml is None:
            Metadata = {}
        else:
            with open(FilePath, "r", encoding="utf-8") as File:
                Metadata = yaml.safe_load(File) or {}

        Metadata["version"] = getVersion()
        ChipId = Metadata.get("chip_id") or Metadata.get("id") or FilePath.stem

        if ArrayName not in self.DbData:
            self.DbData[ArrayName] = {}
        if ChipId not in self.DbData[ArrayName]:
            self.DbData[ArrayName][ChipId] = {"installed": True, "settings": {}}

        ChipData = self.DbData[ArrayName][ChipId]
        ChipDbPath = ChipPath(ChipId)

        Chip = IsolinearChip(
            id=ChipId,
            array=ArrayName,
            metadata=Metadata,
            status="ONLINE",
            data=ChipData,
            FilePath=ChipDbPath,
        )
        self.Chips[ChipId] = Chip

        ArrayIndex = int(ArrayName) if ArrayName.isdigit() else 0
        Placed = False
        for Col in range(100):
            for Row in range(10):
                if not self.StorageMatrix.HasData(ArrayIndex, Col, Row):
                    self.StorageMatrix.SetData(ArrayIndex, Col, Row, Chip, Metadata)
                    Placed = True
                    break
            if Placed:
                break

        log.debug(
            "Loaded Isolinear Chip: %s [%s] v%s",
            ChipId,
            Metadata.get("name", "Unknown"),
            Metadata["version"],
        )

    # Повертаємо чіп із ядра мережі.
    def GetChip(self, ChipId: str) -> Optional[IsolinearChip]:
        return self.Chips.get(ChipId)

    # Повертаємо компактний стан масиву для діагностики.
    def GetChipStatus(self, ArrayPattern: str) -> List[Dict]:
        Result: List[Dict] = []
        ArrayIndex = int(ArrayPattern) if ArrayPattern.isdigit() else 0

        for Col in range(100):
            for Row in range(10):
                Node = self.StorageMatrix.GetNode(ArrayIndex, Col, Row)
                if Node and Node.value:
                    Chip = Node.value
                    Result.append(
                        {
                            "id": Chip.id,
                            "type": Chip.metadata.get("type", "UNKNOWN"),
                            "blue": Chip.metadata.get("blue_level", 2),
                            "green": Chip.metadata.get("green_level", 3),
                        }
                    )

        while len(Result) < 4:
            Result.append({"id": "EMPTY", "type": "SLOT", "blue": 0, "green": 0})
        return Result

    # Повертаємо загальний стан ізолінійного ядра.
    def GetStatus(self) -> Dict[str, Any]:
        return {
            "Name": self.Name,
            "Chips": len(self.Chips),
            "RootPath": str(self.RootPath),
            "DbPath": str(self.DbPath),
        }


__all__ = [
    "ChipStatus",
    "ChipSlot",
    "ChipChannel",
    "NetworkChannel",
    "IsolinearChip",
    "IsolinearBank",
    "IsolinearModule",
    "BlackBox",
    "IsolinearCore",
]
