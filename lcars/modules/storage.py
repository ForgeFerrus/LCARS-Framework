# LCARS ISOLINEAR STORAGE & CHIP MANAGER
# ОПИС: Модуль доступу до ізолінійних баз даних та маніфестів чіпів (.yaml / .db).
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.service.bridge import Bridge

# Базовий адаптер сховища в пам'яті
class StorageAdapter(LCARS):
    def __init__(self):
        super().__init__()
        self.Store: dict = {}

    def Save(self, Key: str, Value: any) -> None:
        self.Store[Key] = Value

    def Load(self, Key: str) -> any:
        return self.Store.get(Key)

# Менеджер та парсер ізолінійних чіпів
class ChipStorageManager(LCARS):
    SingletonInstance: "ChipStorageManager" | None = None

    def __new__(cls, *Args: any, **Kwargs: any) -> "ChipStorageManager":
        if cls.SingletonInstance is None:
            cls.SingletonInstance = super().__new__(cls)
        return cls.SingletonInstance

    def __init__(self):
        super().__init__()
        Path = Bridge().Load("System.Path")
        if Path:
            self.ProjectRoot = Path(__file__).resolve().parents[2]
            DataDir = self.ProjectRoot / "lcars" / "data"
            DbDir = self.ProjectRoot / "lcars" / "database"
            self.ChipRoot = DataDir if DataDir.exists() else DbDir
            self.ChipManifestRoot = self.ProjectRoot / "lcars" / "engineering" / "chips"
        else:
            self.ProjectRoot = None
            self.ChipRoot = None
            self.ChipManifestRoot = None

    def NormalizeName(self, Name: str) -> str:
        Clean = []
        LastDash = False
        for Char in str(Name).strip().strip('"').strip("'").lower():
            if Char.isalnum():
                Clean.append(Char)
                LastDash = False
            elif not LastDash:
                Clean.append("-")
                LastDash = True
        Text = "".join(Clean).strip("-")
        return Text or "chip"

    def ChipSector(self, ChipId: str) -> str:
        Re = Bridge().Load("System.Re")
        if Re:
            Match = Re.match(r"^(\d{2})-", str(ChipId))
            if Match:
                return Match.group(1)
        return self.NormalizeName(ChipId).split("-", 1)[0]

    def ChipIdFromPath(self, PathRef: any) -> str:
        Stem = str(getattr(PathRef, "stem", PathRef))
        Re = Bridge().Load("System.Re")
        if Re:
            Match = Re.match(r"^(\d{2}-\d{4})", Stem)
            if Match:
                return Match.group(1)
        Parts = Stem.split("-", 2)
        if len(Parts) >= 2 and Parts[0].isdigit() and Parts[1].isdigit():
            return Parts[0] + "-" + Parts[1]
        return Stem

    def ManifestPath(self, ChipId: str) -> any:
        if not self.ChipManifestRoot:
            return None
        return self.ChipManifestRoot / self.ChipSector(ChipId) / (str(ChipId) + ".yaml")

    def ReadManifest(self, ChipId: str) -> dict:
        PathRef = self.ManifestPath(ChipId)
        if PathRef is None or not PathRef.exists():
            return {}
        Yaml = Bridge().Load("System.Yaml")
        if Yaml is None:
            # Спроба зчитати як базовий текстовий маніфест
            Content = PathRef.read_text(encoding="utf-8", errors="replace")
            return {"raw": Content}
        Data = Yaml.safe_load(PathRef.read_text(encoding="utf-8", errors="replace")) if hasattr(Yaml, "safe_load") else {}
        return Data if isinstance(Data, dict) else {}

    def ChipName(self, ChipId: str) -> str:
        Manifest = self.ReadManifest(ChipId)
        Metadata = Manifest.get("metadata", {}) if isinstance(Manifest, dict) else {}
        Name = Metadata.get("name") if isinstance(Metadata, dict) else None
        return str(Name) if Name else "LCARS Chip " + str(ChipId)

    def ChipFileName(self, ChipId: str) -> str:
        return str(ChipId) + "-" + self.NormalizeName(self.ChipName(ChipId)) + ".db"

    def ChipPath(self, ChipId: str) -> any:
        if not self.ChipRoot:
            return None
        return self.ChipRoot / self.ChipSector(ChipId) / self.ChipFileName(ChipId)

    def ListChipFiles(self) -> list:
        if not self.ChipRoot or not self.ChipRoot.exists():
            return []
        Files = list(self.ChipRoot.glob("*.db"))
        Files.extend(self.ChipRoot.glob("*/*.db"))
        return sorted(Files)

    def ChipRecord(self, PathRef: any) -> dict:
        ChipId = self.ChipIdFromPath(PathRef)
        Manifest = self.ReadManifest(ChipId)
        Metadata = Manifest.get("metadata", {}) if isinstance(Manifest, dict) else {}
        Tags = Manifest.get("tags", []) if isinstance(Manifest, dict) else []
        if not isinstance(Metadata, dict):
            Metadata = {}
        if not isinstance(Tags, list):
            Tags = []
        Stem = str(getattr(PathRef, "stem", PathRef))
        Name = Metadata.get("name") or Stem
        Keys = [
            ChipId,
            Stem,
            Name,
            Metadata.get("id", ""),
            Metadata.get("type", ""),
            Metadata.get("category", ""),
        ]
        Keys.extend(Tags)
        return {
            "ChipId": ChipId,
            "Name": str(Name),
            "Path": PathRef,
            "Sector": self.ChipSector(ChipId),
            "Metadata": Metadata,
            "Tags": Tags,
            "Keys": [self.NormalizeName(Key) for Key in Keys if Key],
        }

    def ListChips(self) -> list:
        return [self.ChipRecord(PathRef) for PathRef in self.ListChipFiles()]

    def FindChip(self, Query: str) -> dict | None:
        Wanted = self.NormalizeName(Query)
        BestRecord = None
        BestScore = 0
        for Record in self.ListChips():
            Metadata = Record.get("Metadata", {})
            ChipId = self.NormalizeName(Record["ChipId"])
            Name = self.NormalizeName(Record["Name"])
            PathStem = self.NormalizeName(str(getattr(Record["Path"], "stem", Record["Path"])))
            MetadataId = self.NormalizeName(Metadata.get("id", "")) if isinstance(Metadata, dict) else ""
            Tags = [self.NormalizeName(Tag) for Tag in Record.get("Tags", [])]
            Score = 0
            if Wanted == ChipId:
                Score = 100
            elif Wanted == Name:
                Score = 95
            elif Wanted == MetadataId:
                Score = 90
            elif Wanted == PathStem:
                Score = 85
            elif Wanted in Name:
                Score = 80
            elif Wanted in MetadataId:
                Score = 75
            elif Wanted in Tags:
                Score = 60
            elif all(Token in Name for Token in Wanted.split("-")):
                Score = 55
            elif any(Wanted in Key for Key in Record["Keys"]):
                Score = 45
            if Score > BestScore:
                BestScore = Score
                BestRecord = Record
        return BestRecord

    def ResolveChipPath(self, Query: str) -> any:
        Record = self.FindChip(Query)
        if Record:
            return Record["Path"]
        Text = str(Query)
        Re = Bridge().Load("System.Re")
        if Re and Re.match(r"^\d{2}-\d{4}$", Text):
            PathRef = self.ChipPath(Text)
            if PathRef:
                PathRef.parent.mkdir(parents=True, exist_ok=True)
                return PathRef
        if self.ChipRoot:
            PathRef = self.ChipRoot / "99" / ("99-9999-" + self.NormalizeName(Text) + ".db")
            PathRef.parent.mkdir(parents=True, exist_ok=True)
            return PathRef
        return None

# Читач баз даних ізолінійного чіпа
class DatabaseReader(LCARS):
    def __init__(self, Chip: str):
        super().__init__()
        self.Chip = Chip
        self.Path = ChipStorageAccess.GetManager().ResolveChipPath(Chip)

    def Tables(self) -> list:
        if not self.Path or not self.Path.exists():
            return []
        Sqlite = Bridge().Load("System.Sqlite")
        if not Sqlite:
            return []
        Connection = Sqlite.connect(str(self.Path))
        Cursor = Connection.cursor()
        Cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        Rows = Cursor.fetchall()
        Connection.close()
        return [Row[0] for Row in Rows]

    def Columns(self, Table: str) -> list:
        if not self.Path or not self.Path.exists():
            return []
        Sqlite = Bridge().Load("System.Sqlite")
        if not Sqlite:
            return []
        Connection = Sqlite.connect(str(self.Path))
        Cursor = Connection.cursor()
        Cursor.execute("PRAGMA table_info(" + str(Table) + ")")
        Rows = Cursor.fetchall()
        Connection.close()
        return [Row[1] for Row in Rows]

    def Rows(self, Table: str, Limit: int = 50) -> list:
        if not self.Path or not self.Path.exists():
            return []
        Columns = self.Columns(Table)
        Sqlite = Bridge().Load("System.Sqlite")
        if not Sqlite:
            return []
        Connection = Sqlite.connect(str(self.Path))
        Cursor = Connection.cursor()
        Cursor.execute("SELECT * FROM " + str(Table) + " LIMIT ?", (Limit,))
        Rows = Cursor.fetchall()
        Connection.close()
        return [dict(zip(Columns, Row)) for Row in Rows]

    def Snapshot(self, Limit: int = 20) -> dict:
        Tables = self.Tables()
        return {
            "Chip": self.Chip,
            "Path": str(self.Path) if self.Path else "",
            "Tables": Tables,
            "Data": {Table: self.Rows(Table, Limit) for Table in Tables},
        }

# Екранний буфер для відображення даних бази даних чіпа
class DatabaseScreenBuffer(LCARS):
    def __init__(self, Chip: str = "ODN Black Box", Limit: int = 12):
        super().__init__()
        self.Chip = Chip
        self.Limit = Limit
        self.Lines: list = []
        self.Refresh()

    def Refresh(self) -> list:
        Snapshot = ChipStorageAccess.ReadChip(self.Chip, self.Limit)
        Lines = [
            "DATABASE CHIP :: " + str(self.Chip),
            "PATH :: " + Snapshot.get("Path", ""),
        ]
        for Table in Snapshot.get("Tables", []):
            Lines.append("TABLE :: " + Table)
            Rows = Snapshot.get("Data", {}).get(Table, [])
            if not Rows:
                Lines.append("  EMPTY")
            for Row in Rows:
                Cells = []
                for Key, Value in Row.items():
                    Cells.append(str(Key).upper() + "=" + str(Value))
                Lines.append("  " + " | ".join(Cells))
        self.Lines = Lines
        return self.Lines

    def Text(self) -> str:
        return "\n".join(self.Lines)

# Клас доступу до сховища ізолінійних чіпів
class ChipStorageAccess:
    ManagerInstance = None

    @classmethod
    def GetManager(cls) -> ChipStorageManager:
        if cls.ManagerInstance is None:
            cls.ManagerInstance = ChipStorageManager()
        return cls.ManagerInstance

    @staticmethod
    def ReadManifest(ChipId: str) -> dict:
        return ChipStorageAccess.GetManager().ReadManifest(ChipId)

    @staticmethod
    def ListChips() -> list:
        return ChipStorageAccess.GetManager().ListChips()

    @staticmethod
    def FindChip(Query: str) -> dict | None:
        return ChipStorageAccess.GetManager().FindChip(Query)

    @staticmethod
    def ResolveChipPath(Query: str) -> any:
        return ChipStorageAccess.GetManager().ResolveChipPath(Query)

    @staticmethod
    def ReadChip(Chip: str, Limit: int = 20) -> dict:
        return DatabaseReader(Chip).Snapshot(Limit)

    @staticmethod
    def ChipScreenLines(Chip: str, Limit: int = 12) -> list:
        Buffer = DatabaseScreenBuffer(Chip, Limit)
        return Buffer.Lines

    @staticmethod
    def ChipName(ChipId: str) -> str:
        Manifest = ChipStorageAccess.ReadManifest(ChipId)
        return Manifest.get("Name", ChipId)

# Сумісні псевдоніми
ReadManifest = ChipStorageAccess.ReadManifest
ListChips = ChipStorageAccess.ListChips
FindChip = ChipStorageAccess.FindChip
ResolveChipPath = ChipStorageAccess.ResolveChipPath
ChipPath = ChipStorageAccess.ResolveChipPath
ReadChip = ChipStorageAccess.ReadChip
ChipScreenLines = ChipStorageAccess.ChipScreenLines
ChipName = ChipStorageAccess.ChipName
ListChipFiles = ChipStorageAccess.ListChips

__all__ = [
    "StorageAdapter",
    "ChipStorageManager",
    "DatabaseReader",
    "DatabaseScreenBuffer",
    "ChipStorageAccess",
    "ReadManifest",
    "ListChips",
    "ListChipFiles",
    "FindChip",
    "ResolveChipPath",
    "ChipPath",
    "ReadChip",
    "ChipScreenLines",
    "ChipName",
]
