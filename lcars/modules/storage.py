
from __future__ import annotations

import re
import sqlite3
from importlib.util import find_spec
from pathlib import Path
from typing import Protocol, Any, Optional, Dict, List

if find_spec("yaml") is not None:
    import yaml
else:
    yaml = None


# Протокол адаптера сховища для зберігання та завантаження даних
class StorageAdapterProtocol(Protocol):
    def save(self, key: str, value: Any) -> None: ...
    def load(self, key: str) -> Optional[Any]: ...


# Базовий адаптер сховища на словнику
class StorageAdapter:
    # Ініціалізація адаптера сховища
    def __init__(self):
        self.Store = {}

    # Збереження значення за ключем
    def save(self, key: str, value: Any) -> None:
        self.Store[key] = value

    # Завантаження значення за ключем
    def load(self, key: str) -> Optional[Any]:
        return self.Store.get(key)


ProjectRoot = Path(__file__).resolve().parents[2]
ChipRoot = ProjectRoot / "lcars" / "database"
ChipManifestRoot = ProjectRoot / "lcars" / "engineering" / "chips"


# Нормалізація імені чіпа для пошуку
def NormalizeName(Name: str) -> str:
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


# Визначення сектору чіпа за його ID
def ChipSector(ChipId: str) -> str:
    Match = re.match(r"^(\d{2})-", str(ChipId))
    if Match:
        return Match.group(1)
    return NormalizeName(ChipId).split("-", 1)[0]


# Витягування ID чіпа з шляху до файлу
def ChipIdFromPath(PathRef: Path) -> str:
    Match = re.match(r"^(\d{2}-\d{4})", PathRef.stem)
    if Match:
        return Match.group(1)
    Parts = PathRef.stem.split("-", 2)
    if len(Parts) >= 2 and Parts[0].isdigit() and Parts[1].isdigit():
        return Parts[0] + "-" + Parts[1]
    return PathRef.stem


# Формування шляху до маніфесту чіпа
def ManifestPath(ChipId: str) -> Path:
    return ChipManifestRoot / ChipSector(ChipId) / (str(ChipId) + ".yaml")


# Зчитування маніфесту чіпа з YAML файлу
def ReadManifest(ChipId: str) -> Dict[str, Any]:
    PathRef = ManifestPath(ChipId)
    if not PathRef.exists():
        return {}
    # YAML manifests are optional so the storage layer can still boot cleanly.
    if yaml is None:
        return {}
    Data = yaml.safe_load(PathRef.read_text(encoding="utf-8"))
    return Data if isinstance(Data, dict) else {}


# Отримання назви чіпа з маніфесту
def ChipName(ChipId: str) -> str:
    Manifest = ReadManifest(ChipId)
    Metadata = Manifest.get("metadata", {})
    Name = Metadata.get("name") if isinstance(Metadata, dict) else None
    return str(Name) if Name else "LCARS Chip " + str(ChipId)


# Формування імені файлу чіпа
def ChipFileName(ChipId: str) -> str:
    return str(ChipId) + "-" + NormalizeName(ChipName(ChipId)) + ".db"


# Формування повного шляху до файлу чіпа
def ChipPath(ChipId: str) -> Path:
    return ChipRoot / ChipSector(ChipId) / ChipFileName(ChipId)


# Отримання списку всіх файлів чіпів на диску
def ListChipFiles() -> List[Path]:
    Files = list(ChipRoot.glob("*.db"))
    Files.extend(ChipRoot.glob("*/*.db"))
    return sorted(Files)


# Побудова запису чіпа з маніфесту та шляху
def ChipRecord(PathRef: Path) -> Dict[str, Any]:
    ChipId = ChipIdFromPath(PathRef)
    Manifest = ReadManifest(ChipId)
    Metadata = Manifest.get("metadata", {})
    Tags = Manifest.get("tags", [])
    if not isinstance(Metadata, dict):
        Metadata = {}
    if not isinstance(Tags, list):
        Tags = []
    Name = Metadata.get("name") or PathRef.stem
    Keys = [
        ChipId,
        PathRef.stem,
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
        "Sector": ChipSector(ChipId),
        "Metadata": Metadata,
        "Tags": Tags,
        "Keys": [NormalizeName(Key) for Key in Keys if Key],
    }


# Отримання списку всіх чіпів з маніфестами
def ListChips() -> List[Dict[str, Any]]:
    return [ChipRecord(PathRef) for PathRef in ListChipFiles()]


# Пошук чіпа за запитом зі скорингом релевантності
def FindChip(Query: str) -> Dict[str, Any] | None:
    Wanted = NormalizeName(Query)
    BestRecord = None
    BestScore = 0
    for Record in ListChips():
        Metadata = Record.get("Metadata", {})
        ChipId = NormalizeName(Record["ChipId"])
        Name = NormalizeName(Record["Name"])
        PathStem = NormalizeName(Record["Path"].stem)
        MetadataId = NormalizeName(Metadata.get("id", "")) if isinstance(Metadata, dict) else ""
        Tags = [NormalizeName(Tag) for Tag in Record.get("Tags", [])]
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


# Розв'язування шляху до чіпа за запитом або створення нового
def ResolveChipPath(Query: str) -> Path:
    Record = FindChip(Query)
    if Record:
        return Record["Path"]
    Text = str(Query)
    if re.match(r"^\d{2}-\d{4}$", Text):
        PathRef = ChipPath(Text)
        PathRef.parent.mkdir(parents=True, exist_ok=True)
        return PathRef
    PathRef = ChipRoot / "99" / ("99-9999-" + NormalizeName(Text) + ".db")
    PathRef.parent.mkdir(parents=True, exist_ok=True)
    return PathRef


# Розв'язування шляху за назвою чіпа
def NamedChipPath(Name: str) -> Path:
    return ResolveChipPath(Name)


# Читання даних з бази даних чіпа
class DatabaseReader:
    # Ініціалізація читача бази даних чіпа
    def __init__(self, Chip: str):
        self.Chip = Chip
        self.Path = ResolveChipPath(Chip)

    # Отримання списку таблиць у базі даних
    def Tables(self) -> List[str]:
        Connection = sqlite3.connect(str(self.Path))
        Cursor = Connection.cursor()
        Cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        Rows = Cursor.fetchall()
        Connection.close()
        return [Row[0] for Row in Rows]

    # Отримання стовпців таблиці
    def Columns(self, Table: str) -> List[str]:
        Connection = sqlite3.connect(str(self.Path))
        Cursor = Connection.cursor()
        Cursor.execute("PRAGMA table_info(" + Table + ")")
        Rows = Cursor.fetchall()
        Connection.close()
        return [Row[1] for Row in Rows]

    # Отримання рядків з таблиці
    def Rows(self, Table: str, Limit: int = 50) -> List[Dict[str, Any]]:
        Columns = self.Columns(Table)
        Connection = sqlite3.connect(str(self.Path))
        Cursor = Connection.cursor()
        Cursor.execute("SELECT * FROM " + Table + " LIMIT ?", (Limit,))
        Rows = Cursor.fetchall()
        Connection.close()
        return [dict(zip(Columns, Row)) for Row in Rows]

    # Зняття повного знімка бази даних чіпа
    def Snapshot(self, Limit: int = 20) -> Dict[str, Any]:
        Tables = self.Tables()
        return {
            "Chip": self.Chip,
            "Path": str(self.Path),
            "Tables": Tables,
            "Data": {Table: self.Rows(Table, Limit) for Table in Tables},
        }


# Зчитування даних чіпа у вигляді знімка
def ReadChip(Chip: str, Limit: int = 20) -> Dict[str, Any]:
    return DatabaseReader(Chip).Snapshot(Limit)


# Формування рядків для відображення даних чіпа на екрані
def ChipScreenLines(Chip: str, Limit: int = 12) -> List[str]:
    Snapshot = ReadChip(Chip, Limit)
    Lines = [
        "DATABASE CHIP :: " + str(Chip),
        "PATH :: " + Snapshot["Path"],
    ]
    for Table in Snapshot["Tables"]:
        Lines.append("TABLE :: " + Table)
        Rows = Snapshot["Data"].get(Table, [])
        if not Rows:
            Lines.append("  EMPTY")
        for Row in Rows:
            Cells = []
            for Key, Value in Row.items():
                Cells.append(str(Key).upper() + "=" + str(Value))
            Lines.append("  " + " | ".join(Cells))
    return Lines


# Екранний буфер для відображення даних бази даних чіпа
class DatabaseScreenBuffer:
    # Ініціалізація екранного буфера
    def __init__(self, Chip: str = "ODN Black Box", Limit: int = 12):
        self.Chip = Chip
        self.Limit = Limit
        self.Lines: List[str] = []
        self.Refresh()

    # Оновлення вмісту буфера
    def Refresh(self) -> List[str]:
        self.Lines = ChipScreenLines(self.Chip, self.Limit)
        return self.Lines

    # Отримання текстового подання буфера
    def Text(self) -> str:
        return "\n".join(self.Lines)
