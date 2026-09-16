# ◤ LCARS ENGINEERING :: ISOLINEAR OPTICAL NETWORK 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/isolinear.py
# ОПИС: Апаратне технічне ядро ізолінійної оптичної мережі зорельота.
#       Керує оптичними чіпами (00..10), стійками (IsolinearBank),
#       чорною скринькою ODN (BlackBox) та тривимірною оптичною матрицею пам'яті.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import LCARS, Directive
from lcars.core.conduit import Service
from lcars.modules.storage import ChipPath, ResolveChipPath

# Стан чіпа в ізолінійній мережі
class ChipStatus(LCARS):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    FAULT = "FAULT"

class ChipSlot(LCARS):
    def __init__(self, SlotId: any):
        super().__init__()
        self.SlotId = SlotId
        self.ActiveChip = None

class ChipChannel(LCARS):
    def __init__(self, ChannelId: any):
        super().__init__()
        self.ChannelId = ChannelId
        self.Active = True

class NetworkChannel(LCARS):
    def __init__(self, ChannelId: any):
        super().__init__()
        self.ChannelId = ChannelId
        self.Speed = 1000

class IsolinearChip(LCARS):
    def __init__(
        self,
        Id: str = "00-0000",
        Array: str = "00",
        Metadata: dict | None = None,
        Faction: str = "federation",
        Status: str = ChipStatus.OFFLINE,
        MemoryUsage: int = 0,
        CpuUsage: int = 0,
        Data: dict | None = None,
        FilePath: any = None,
        Connection: any = None,
        Connected: bool = False,
        *Args: any,
        **Kwargs: any,
    ):
        super().__init__()
        self.Id = Id if Id != "00-0000" else Kwargs.get("id", Id)
        self.Array = Array if Array != "00" else Kwargs.get("array", Array)
        Meta = Metadata if Metadata is not None else Kwargs.get("metadata", {})
        self.Metadata = dict(Meta or {})
        self.Faction = Faction
        self.Status = Status
        self.MemoryUsage = MemoryUsage
        self.CpuUsage = CpuUsage
        self.Data = dict(Data or {})
        self.FilePath = FilePath
        self.Connection = Connection
        self.Connected = Connected

    # Підключення локальної бази даних чіпа
    def Connect(self) -> bool:
        if self.FilePath is None:
            return False
        if self.Connection is not None:
            self.Connected = True
            return True
        PathMod = LCARS.Import("pathlib")
        PathObj = PathMod.Path(self.FilePath) if PathMod and not hasattr(self.FilePath, "parent") else self.FilePath
        if hasattr(PathObj, "parent"):
            PathObj.parent.mkdir(parents=True, exist_ok=True)
        Sqlite = LCARS.Import("sqlite3")
        if Sqlite and hasattr(Sqlite, "connect"):
            DatabasePath = str(PathObj)
            Threading = LCARS.System.Thread
            if Threading and hasattr(Threading, "Local"):
                ThreadLocal = Threading.Local()
                if not hasattr(ThreadLocal, "Connection"):
                    ThreadLocal.Connection = Sqlite.connect(DatabasePath)
                self.Connection = ThreadLocal.Connection
            else:
                self.Connection = Sqlite.connect(DatabasePath)
            self.Connected = True
            return True
        return False

    # Відключення локальної бази даних чіпа
    def Disconnect(self) -> None:
        if self.Connection is not None:
            self.Connection.close()
            self.Connection = None
        self.Connected = False

    # Виконання SQL-запиту у файлі чіпа
    def ExecuteQuery(self, Query: str, Params=None):
        if not self.Connected:
            self.Connect()
        if self.Connection is None:
            return False if not Query.strip().upper().startswith("SELECT") else []

        Cursor = self.Connection.cursor()
        if Params is not None:
            Cursor.execute(Query, Params)
        else:
            Cursor.execute(Query)

        if Query.strip().upper().startswith("SELECT"):
            return Cursor.fetchall()

        self.Connection.commit()
        return True

    # Повернення технічного стану чіпа
    def GetStatus(self) -> dict:
        return {
            "ChipId": self.Id,
            "Array": self.Array,
            "Status": self.Status,
            "Faction": self.Faction,
            "Connected": self.Connected,
            "Path": str(self.FilePath) if self.FilePath else "",
        }

# Банк чіпів для базової роботи з ізолінійною пам'яттю
class IsolinearBank:
    def __init__(self, DBDirectory: str = "database"):
        self.DBDirectory = Directive.PathDrive(DBDirectory)
        self.Chips = {}
        self.Channels = {}
        self.Networks = {}
        self.Slots = {}

    # Додавання чіпа в банк
    def AddChip(self, ChipId: str, Faction: str = "federation") -> IsolinearChip:
        PathRef = ResolveChipPath(str(ChipId))
        Chip = IsolinearChip(
            Id=ChipId,
            Array="LEGACY",
            Metadata={"Faction": Faction},
            Faction=Faction,
            FilePath=PathRef,
        )
        self.Chips[ChipId] = Chip
        return Chip

    # Монтування чіпа в стійку
    def Mount(self, ChipId: str, FilePath: any = None, Faction: str = "federation") -> IsolinearChip:
        if ChipId in self.Chips:
            return self.Chips[ChipId]
        PathRef = Directive.PathDrive(FilePath) if FilePath else ResolveChipPath(str(ChipId))
        Chip = IsolinearChip(
            Id=ChipId,
            Array="MOUNTED",
            Metadata={"Faction": Faction},
            Faction=Faction,
            FilePath=PathRef,
        )
        self.Chips[ChipId] = Chip
        return Chip

    # Отримання чіпа за ідентифікатором
    def GetChip(self, ChipId: str) -> IsolinearChip | None:
        return self.Chips.get(ChipId)

    # Завантаження наявних чіпів з директорії бази
    def LoadBanks(self, Faction: str = "federation") -> None:
        if not self.DBDirectory.exists():
            self.DBDirectory.mkdir(parents=True, exist_ok=True)
        for ChipFile in self.DBDirectory.glob("**/*.db"):
            Parts = ChipFile.stem.split("-", 2)
            ChipId = Parts[0] + "-" + Parts[1] if len(Parts) > 1 else ChipFile.stem
            if ChipId not in self.Chips:
                self.AddChip(ChipId, Faction)

    # Діагностичний стан банку чіпів
    def ClusterStatus(self) -> dict:
        return {
            "Directory": str(self.DBDirectory),
            "ChipCount": len(self.Chips),
            "ChipIds": list(self.Chips.keys()),
            "ChannelCount": len(self.Channels),
            "NetworkCount": len(self.Networks),
            "SlotCount": len(self.Slots),
        }

# Легкий модуль, прив'язаний до батьківського чіпа
class IsolinearModule:
    def __init__(self, ModuleId: str, ParentChip: IsolinearChip):
        self.ModuleId = ModuleId
        self.ParentChip = ParentChip

# Чорна скринька ODN: реєстратор сигналів, каналів і технічних подій
class BlackBox(IsolinearChip):
    def __init__(
        self,
        Id: str = "00-0004",
        Array: str = "00",
        Metadata: dict | None = None,
        FilePath: any = None,
    ):
        Meta = dict(Metadata or {})
        Meta.setdefault("Name", "ODN Black Box")
        Meta.setdefault("Type", "DATABASE")
        Meta.setdefault("Role", "ODN_TRANSMISSION_RECORDER")
        super().__init__(
            Id=Id,
            Array=Array,
            Metadata=Meta,
            Status=ChipStatus.OFFLINE,
            FilePath=ResolveChipPath(FilePath) if FilePath else ResolveChipPath("00-0004"),
        )
        self.ChipName = "ODN Black Box"
        self.Prepare()

    # Створення таблиць ідентичності чіпа та журналу подій
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
        Now = LCARS.System.Time.Now()
        Cursor.execute(
            "INSERT OR IGNORE INTO ChipIdentity (ChipId, ChipName, Sector, Role, Created) VALUES (?, ?, ?, ?, ?)",
            (self.Id, self.ChipName, self.Array, "ODN_TRANSMISSION_RECORDER", Now),
        )
        Conn.commit()

    # Пакування даних в JSON для запису
    def Pack(self, Value: any) -> str:
        Json = LCARS.Storage.JSON
        return Json.dumps(Value, ensure_ascii=False, default=str) if Json else str(Value)
    # Реєстрація каналу в чорній скриньці
    def RegisterChannel(self, Name: str) -> None:
        Stamp = LCARS.System.Time.Now()
        if not self.Connect():
            return
        Threading = LCARS.System.Thread
        if Threading and hasattr(Threading, "Local"):
            ThreadLocal = Threading.Local()
            if not hasattr(ThreadLocal, "Connection"):
                PathMod = LCARS.Import("pathlib")
                PathObj = PathMod.Path(self.FilePath) if PathMod and not hasattr(self.FilePath, "parent") else self.FilePath
                Sqlite = LCARS.Import("sqlite3")
                if Sqlite and hasattr(Sqlite, "connect"):
                    ThreadLocal.Connection = Sqlite.connect(str(PathObj))
            Conn = ThreadLocal.Connection
        else:
            Conn = self.Connection
        if Conn is None:
            return
        Cursor = Conn.cursor()
        Cursor.execute(
            "INSERT OR IGNORE INTO ODNChannel (Name, Created, LastStamp) VALUES (?, ?, ?)",
            (Name, Stamp, Stamp),
        )
        Conn.commit()

    # Фіксація події в чорній скриньці
    def Record(self, Channel: str, GroupName: str | None, SignalName: str | None, Args: tuple, Kwargs: dict) -> None:
        if not self.Connect():
            return
        Conn = self.Connection
        if Conn is None:
            return

        Stamp = LCARS.System.Time.Now()
        Cursor = Conn.cursor()
        Cursor.execute(
            "INSERT INTO ODNLog (Stamp, Channel, GroupName, SignalName, Args, Kwargs) VALUES (?, ?, ?, ?, ?, ?)",
            (
                Stamp,
                Channel,
                GroupName,
                SignalName,
                self.Pack(Args),
                self.Pack(Kwargs),
            ),
        )
        Conn.commit()

    # Підрахунок кількості записів у журналі
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

    # Стан чорної скриньки
    def GetStatus(self) -> dict:
        return {
            "ChipId": self.Id,
            "ChipName": self.ChipName,
            "Path": str(self.FilePath),
            "Entries": self.Count(),
        }

# Головний сервіс ізолінійної оптичної мережі
class IsolinearCore(Service):
    def __init__(self):
        super().__init__()
        self.Name = "Isolinear"
        from lcars.core.matrix import SystemMatrix

        self.StorageMatrix = SystemMatrix([11, 100, 10], Id="IsolinearStorage")
        self.Chips = {}
        self.RootPath = Directive.PathDrive("lcars/engineering/chips")
        self.DbData = {f"{Index:02d}": {} for Index in range(11)}

    # Завантаження карти та чіпів в пам'ять
    def OnStart(self) -> None:
        self.ScanChips()

    # Зупинка та скидання стану
    def OnStop(self) -> None:
        pass

    def ScanChips(self):
        if not self.RootPath.exists():
            self.RootPath.mkdir(parents=True, exist_ok=True)
            return

        for ArrayDir in self.RootPath.iterdir():
            if ArrayDir.is_dir():
                ArrayName = ArrayDir.name
                for ChipFile in ArrayDir.glob("*.yaml"):
                    self.LoadChip(ChipFile, ArrayName)

    # Завантаження одного YAML-чіпа та розміщення в матриці
    def LoadChip(self, FilePath: any, ArrayName: str = "00"):
        from lcars.base.info import VersionInfo
        if isinstance(FilePath, str):
            Candidate = LCARS.System.Path(FilePath)
            if not Candidate.exists():
                Candidate = LCARS.System.Path(f"lcars/engineering/chips/{ArrayName}/{FilePath}.yaml")
            FilePath = Candidate

        Yaml = LCARS.Storage.YAML
        if Yaml is None or not hasattr(Yaml, "safe_load"):
            Metadata = {}
        else:
            Content = FilePath.read_text(encoding="utf-8", errors="replace")
            Metadata = Yaml.safe_load(Content) or {}

        ChipId = (
            Metadata.get("ChipId")
            or Metadata.get("Id")
            or (Metadata.get("Metadata", {}).get("Id") if isinstance(Metadata.get("Metadata"), dict) else None)
            or Metadata.get("id")
            or (Metadata.get("metadata", {}).get("id") if isinstance(Metadata.get("metadata"), dict) else None)
            or FilePath.stem
        )

        if ArrayName not in self.DbData:
            self.DbData[ArrayName] = {}
        if ChipId not in self.DbData[ArrayName]:
            self.DbData[ArrayName][ChipId] = {"Installed": True, "Settings": {}}

        ChipData = self.DbData[ArrayName][ChipId]
        ChipDbPath = ChipPath(ChipId)

        Chip = IsolinearChip(
            Id=ChipId,
            Array=ArrayName,
            Metadata=Metadata,
            Status=ChipStatus.ONLINE,
            Data=ChipData,
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
        return Chip

    # Отримання чіпа з ядра мережі
    def GetChip(self, ChipId: str) -> IsolinearChip | None:
        return self.Chips.get(ChipId)

    # Стан масиву для діагностики
    def GetChipStatus(self, ArrayPattern: str) -> list:
        Result = []
        ArrayIndex = int(ArrayPattern) if ArrayPattern.isdigit() else 0

        for Col in range(100):
            for Row in range(10):
                Node = self.StorageMatrix.GetNode(ArrayIndex, Col, Row)
                if Node and Node.value:
                    Chip = Node.value
                    Result.append(
                        {
                            "Id": Chip.Id,
                            "Type": Chip.Metadata.get("type", "UNKNOWN"),
                            "Blue": Chip.Metadata.get("blue_level", 2),
                            "Green": Chip.Metadata.get("green_level", 3),
                        }
                    )

        while len(Result) < 4:
            Result.append({"Id": "EMPTY", "Type": "SLOT", "Blue": 0, "Green": 0})
        return Result

    # Загальний стан ізолінійного ядра
    def GetStatus(self) -> dict:
        return {
            "Name": self.Name,
            "Chips": len(self.Chips),
            "RootPath": str(self.RootPath),
            "DbPath": str(self.DbPath),
        }

    # Діагностичний статус кластера чіпів
    def ClusterStatus(self) -> dict:
        return {
            "TotalMounted": len(self.Chips),
            "Status": "MOUNTED_ONLINE",
            "RootPath": str(self.RootPath),
            "DbPath": str(self.DbPath),
        }
