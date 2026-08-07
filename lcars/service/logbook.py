# ◤ TITANIUM LOGBOOK SYSTEM — v44.20
# LCARS Framework :: SYSTEM_LOGS // SHIPS_HISTORY // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Управління журналами подій зорельота, зберігання в ізолінійних чіпах.
# ФУНКЦІЇ: Запис Капітанського логу, Операційного журналу та системних подій.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
from typing import List, Dict, Any, Optional, Union
from enum import Enum as PyEnum
from datetime import datetime
from lcars.base.type import SystemComponent, Directive
from lcars.engineering.isolinear import IsolinearChip
from lcars.modules.storage import ResolveChipPath
from pathlib import Path

# КАТЕГОРІЇ ЖУРНАЛІВ (TITANIUM LOG CATEGORIES)
class LogCategory(PyEnum):
    SHIPS_LOG      = "Ship's Log"
    CAPTAINS_LOG   = "Captain's Log"
    OPERATIONS_LOG = "Operations Log"
    SYSTEM_LOG     = "System Log"
    SECURITY_LOG   = "Security Log"
    MEDICAL_LOG    = "Medical Log"

# ГОЛОВНИЙ КЛАС ЛОГБУКУ (TITANIUM LOGBOOK)
class Logbook(SystemComponent):
    # Центральний координатор журналів подій Titanium.
    InstanceNode = None

    def __new__(cls):
        if cls.InstanceNode is None:
            cls.InstanceNode = super().__new__(cls)
            cls.InstanceNode.InitializeLogbook()
        return cls.InstanceNode

    # Ініціалізація логбуку зі створенням директорії та ізолінійного чіпу
    def InitializeLogbook(self):
        self.PathDriveNode = Path.cwd

        # Створення директорії логів Titanium
        self.LogsDirectoryNode = Path("logs")
        self.LogsDirectoryNode.mkdir(parents=True, exist_ok=True)

        # Ізолінійний чіп для Logbook (ISO-LOG)
        PathRef = ResolveChipPath("Logbook Archive Chip")
        ChipId = PathRef.stem.split("-", 2)[0] + "-" + PathRef.stem.split("-", 2)[1]
        self.LogChipNode = IsolinearChip(id=ChipId, array=ChipId.split("-", 1)[0], metadata={}, FilePath=PathRef)
        self.InitializeMemoryMatrix()

    # Ініціалізація SQL-структури в ізолінійній стійці
    def InitializeMemoryMatrix(self):
        # Перевірка з'єднання з ізолінійним чіпом
        if not self.LogChipNode.Connect():
            return

        MatrixConn = self.LogChipNode.Connection
        if MatrixConn:
            MatrixConn.execute('''CREATE TABLE IF NOT EXISTS logbook (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stardate REAL,
                EarthDate TEXT,
                category TEXT,
                message TEXT
            )''')
            MatrixConn.commit()

    # Запис події в матрицю Titanium та текстовий архів
    def RecordEntry(self, MessageStr: str, CategoryNode: LogCategory = LogCategory.SYSTEM_LOG):
        Now = datetime.now()
        StarDateVal = Now.timestamp()
        EarthDateStr = Now.isoformat(timespec="seconds")

        # Вивід у системну телеметрію Titanium
        print(f"LOGBOOK :: ENTRY ARCHIVED: {CategoryNode.value} -> {MessageStr[:50]}...")

        # 1. Запис в ізолінійний чіп (Matrix Storage)
        if self.LogChipNode.Connect():
            MatrixConn = self.LogChipNode.Connection
            if MatrixConn:
                MatrixConn.execute(
                    "INSERT INTO logbook (stardate, EarthDate, category, message) VALUES (?, ?, ?, ?)",
                    (StarDateVal, EarthDateStr, CategoryNode.value, MessageStr)
                )
                MatrixConn.commit()

        # 2. Запис у фізичний текстовий лог (Compliance Archive)
        if self.LogsDirectoryNode:
            LogFileNode = self.LogsDirectoryNode / f"{CategoryNode.name.lower()}.log"
            EntryLineStr = f"\u25e7 {StarDateVal:.2f} [{CategoryNode.value}] {MessageStr} (Earth: {EarthDateStr})\n"
            with open(str(LogFileNode), "a", encoding="utf-8") as F:
                F.write(EntryLineStr)

    # Читання останніх записів з матриці Titanium
    def FetchRecentEntries(self, LimitCount: int = 20) -> List[Dict[str, Any]]:
        # Перевірка з'єднання перед читанням
        if not self.LogChipNode.Connect():
            return []

        MatrixConn = self.LogChipNode.Connection
        if MatrixConn:
            CursorNode = MatrixConn.cursor()
            CursorNode.execute("SELECT stardate, EarthDate, category, message FROM logbook ORDER BY id DESC LIMIT ?", (LimitCount,))
            RowsArray = CursorNode.fetchall()
            return [
                {"stardate": r[0], "EarthDate": r[1], "category": r[2], "message": r[3]}
                for r in RowsArray
            ]
        return []

# ГОЛОВНІ ФУНКЦІЇ ДОСТУПУ (TITANIUM MASTER API)
LogbookInstance = None

# Отримання singleton-екземпляра логбуку
def GetLogbook() -> Logbook:
    global LogbookInstance
    if LogbookInstance is None:
        LogbookInstance = Logbook()
    return LogbookInstance

# Канонічний метод запису в логбук Titanium v44.20
def WriteEntry(MessageStr: str, CategoryNode: LogCategory = LogCategory.SYSTEM_LOG):
    GetLogbook().RecordEntry(MessageStr, CategoryNode)

# Зворотна сумісність (Legacy Aliases)
write_entry = WriteEntry

# Експорт вузлів Titanium
__all__ = ["LogCategory", "Logbook", "GetLogbook", "WriteEntry"]
