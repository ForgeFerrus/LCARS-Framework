# ◤ TITANIUM MEMORY MODULE — ISO-02
# LCARS Framework :: COMPUTER_MEMORY // DIALOG_HISTORY // CONTEXT_STORAGE
# ОПИС: Управління пам'яттю бортового комп'ютера через ізолінійний чіп ISO-02.
# ФУНКЦІЇ: Сесії, історія діалогів, контекст, закладки.
# СТАНДАРТ: Titanium CamelCase, Zero-Except, Isolinear Chip ISO-02.
# БАЗА ДАНИХ: 02.db (новий формат)

from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import uuid
import platform as Plat
from lcars.base.type import SystemComponent
from lcars.engineering.isolinear import IsolinearChip
from lcars.modules.storage import ResolveChipPath
from lcars.base.version import getVersion

DB_VERSION = 1
__version__ = getVersion()

class MemoryChip(IsolinearChip):
    # Ізолінійний чіп ISO-02 для зберігання пам'яті.

    def __init__(self):
        super().__init__(
            id="02-0001",
            array="02",
            metadata={"Name": "COMPUTER MEMORY", "Role": "SESSION STORAGE"},
            FilePath=ResolveChipPath("02-0001"),
        )
        self.InitializeSchema()

    def InitializeSchema(self):
        # Ініціалізація схеми бази даних пам'яті.
        if not self.Connect():
            return

        Conn = self.Connection
        if Conn:
            Cursor = Conn.cursor()
            Cursor.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    started_at TIMESTAMP NOT NULL,
                    ended_at TIMESTAMP,
                    hostname TEXT,
                    platform TEXT,
                    uptime_sec REAL DEFAULT 0,
                    notes TEXT
                );

                CREATE TABLE IF NOT EXISTS dialog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'computer')),
                    content TEXT NOT NULL,
                    command_type TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                );

                CREATE TABLE IF NOT EXISTS context (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                );

                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    tags TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_dialog_session ON dialog(session_id);
                CREATE INDEX IF NOT EXISTS idx_dialog_ts ON dialog(timestamp);
                CREATE INDEX IF NOT EXISTS idx_bookmarks_session ON bookmarks(session_id);
            """)
            Conn.commit()
            print(">> MEMORY_CHIP: SCHEMA_INITIALIZED")


class ComputerMemory(SystemComponent):
    # Управління пам'яттю бортового комп'ютера через ізолінійний чіп ISO-02.
    Name = "memory"

    def __init__(self):
        super().__init__()
        self.StorageChip = MemoryChip()
        self.SessionID: Optional[str] = None
        self.InitializeMemory()

    def InitializeMemory(self):
        # Ініціалізація пам'яті та старт сесії.
        self.StartSession()
        if self.SessionID:
            print(f">> COMPUTER_MEMORY: ACTIVE | SESSION {self.SessionID[:8]}")
        else:
            print(">> COMPUTER_MEMORY: ACTIVE | SESSION N/A")

    def StartSession(self):
        # Старт нової сесії.
        self.SessionID = str(uuid.uuid4())
        if self.StorageChip.Connect():
            Conn = self.StorageChip.Connection
            if Conn:
                Conn.execute(
                    "INSERT INTO sessions (id, started_at, hostname, platform) VALUES (?, ?, ?, ?)",
                    (self.SessionID, datetime.now().isoformat(), Plat.node(), Plat.system())
                )
                Conn.commit()

    def EndSession(self, UptimeSec: float = 0):
        # Завершення сесії.
        if self.StorageChip.Connect() and self.SessionID:
            Conn = self.StorageChip.Connection
            if Conn:
                Conn.execute(
                    "UPDATE sessions SET ended_at = ?, uptime_sec = ? WHERE id = ?",
                    (datetime.now().isoformat(), UptimeSec, self.SessionID)
                )
                Conn.commit()

    @property
    def SessionId(self) -> str:
        return self.SessionID or ""

    def GetSessionCount(self) -> int:
        # Кількість сесій.
        if not self.StorageChip.Connect():
            return 0
        Conn = self.StorageChip.Connection
        if Conn:
            Row = Conn.execute("SELECT COUNT(*) FROM sessions").fetchone()
            return Row[0] if Row else 0
        return 0

    def GetRecentSessions(self, Limit: int = 10) -> List[Dict[str, Any]]:
        # Останні сесії.
        if not self.StorageChip.Connect():
            return []
        Conn = self.StorageChip.Connection
        if Conn:
            Rows = Conn.execute(
                "SELECT * FROM sessions ORDER BY started_at DESC LIMIT ?", (Limit,)
            ).fetchall()
            return [dict(R) for R in Rows]
        return []

    def SaveExchange(self, UserQuery: str, ComputerResponse: str, CommandType: str = ""):
        # Збереження діалогу.
        if not self.StorageChip.Connect():
            return
        Conn = self.StorageChip.Connection
        if Conn:
            Now = datetime.now().isoformat()
            Conn.execute(
                "INSERT INTO dialog (session_id, timestamp, role, content, command_type) VALUES (?, ?, 'user', ?, ?)",
                (self.SessionID, Now, UserQuery, CommandType)
            )
            Conn.execute(
                "INSERT INTO dialog (session_id, timestamp, role, content, command_type) VALUES (?, ?, 'computer', ?, ?)",
                (self.SessionID, Now, ComputerResponse, CommandType)
            )
            Conn.commit()

    def GetDialogHistory(self, Limit: int = 50, SessionId: Optional[str] = None) -> List[Dict[str, Any]]:
        # Історія діалогу.
        if not self.StorageChip.Connect():
            return []
        Conn = self.StorageChip.Connection
        if Conn:
            Sid = SessionId or self.SessionID
            Rows = Conn.execute(
                "SELECT * FROM dialog WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (Sid, Limit)
            ).fetchall()
            return [dict(R) for R in reversed(Rows)]
        return []

    def GetAllDialogCount(self) -> int:
        # Загальна кількість діалогів.
        if not self.StorageChip.Connect():
            return 0
        Conn = self.StorageChip.Connection
        if Conn:
            Row = Conn.execute("SELECT COUNT(*) FROM dialog").fetchone()
            return Row[0] if Row else 0
        return 0

    def SearchDialog(self, Keyword: str, Limit: int = 20) -> List[Dict[str, Any]]:
        # Пошук в діалогах.
        if not self.StorageChip.Connect():
            return []
        Conn = self.StorageChip.Connection
        if Conn:
            Rows = Conn.execute(
                "SELECT * FROM dialog WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
                (f"%{Keyword}%", Limit)
            ).fetchall()
            return [dict(R) for R in Rows]
        return []

    def SetContext(self, Key: str, Value: Any):
        # Збереження контексту.
        if not self.StorageChip.Connect():
            return
        Conn = self.StorageChip.Connection
        if Conn:
            ValStr = json.dumps(Value, ensure_ascii=False) if not isinstance(Value, str) else Value
            Conn.execute(
                "INSERT OR REPLACE INTO context (key, value, updated_at) VALUES (?, ?, ?)",
                (Key, ValStr, datetime.now().isoformat())
            )
            Conn.commit()

    def GetContext(self, Key: str, Default: Any = None) -> Any:
        # Отримання контексту.
        if not self.StorageChip.Connect():
            return Default
        Conn = self.StorageChip.Connection
        if Conn:
            Row = Conn.execute("SELECT value FROM context WHERE key = ?", (Key,)).fetchone()
            if Row:
                Val = Row[0]
                if Val and Val[0] in ("{", "["):
                    return json.loads(Val)
                return Val
        return Default

    def GetAllContext(self) -> Dict[str, Any]:
        # Весь контекст.
        if not self.StorageChip.Connect():
            return {}
        Conn = self.StorageChip.Connection
        if Conn:
            Rows = Conn.execute("SELECT key, value FROM context").fetchall()
            Result = {}
            for R in Rows:
                Val = R[1]
                if Val and Val[0] in ("{", "["):
                    Result[R[0]] = json.loads(Val)
                else:
                    Result[R[0]] = Val
            return Result
        return {}

    def AddBookmark(self, Title: str, Content: str = "", Tags: str = ""):
        # Додавання закладки.
        if not self.StorageChip.Connect():
            return
        Conn = self.StorageChip.Connection
        if Conn:
            Conn.execute(
                "INSERT INTO bookmarks (session_id, timestamp, title, content, tags) VALUES (?, ?, ?, ?, ?)",
                (self.SessionID, datetime.now().isoformat(), Title, Content, Tags)
            )
            Conn.commit()

    def GetBookmarks(self, Limit: int = 20) -> List[Dict[str, Any]]:
        # Отримання закладок.
        if not self.StorageChip.Connect():
            return []
        Conn = self.StorageChip.Connection
        if Conn:
            Rows = Conn.execute(
                "SELECT * FROM bookmarks ORDER BY timestamp DESC LIMIT ?", (Limit,)
            ).fetchall()
            return [dict(R) for R in Rows]
        return []

    def IsOnline(self) -> bool:
        # Статус підключення.
        return self.StorageChip.Connected

    def GetMemoryStats(self) -> Dict[str, Any]:
        # Статистика пам'яті.
        if not self.StorageChip.Connect():
            return {"status": "OFFLINE"}
        Conn = self.StorageChip.Connection
        if Conn:
            Sessions = self.GetSessionCount()
            Dialogs = self.GetAllDialogCount()
            BookmarksCount = Conn.execute("SELECT COUNT(*) FROM bookmarks").fetchone()[0]
            ContextCount = Conn.execute("SELECT COUNT(*) FROM context").fetchone()[0]
            DBSize = self.StorageChip.FilePath.stat().st_size if self.StorageChip.FilePath.exists() else 0
            return {
                "status": "ONLINE",
                "db_path": str(self.StorageChip.FilePath),
                "db_size_kb": round(DBSize / 1024, 1),
                "sessions": Sessions,
                "dialog_entries": Dialogs,
                "bookmarks": BookmarksCount,
                "context_keys": ContextCount,
                "current_session": self.SessionID[:8] if self.SessionID else "N/A",
            }
        return {"status": "OFFLINE"}

    def Close(self):
        # Закриття з'єднання.
        self.StorageChip.Disconnect()

# Глобальний екземпляр
MemoryInstance: Optional[ComputerMemory] = None

def GetMemory() -> ComputerMemory:
    # Отримати екземпляр пам'яті.
    global MemoryInstance
    if MemoryInstance is None:
        MemoryInstance = ComputerMemory()
    return MemoryInstance


def SaveExchange(UserQuery: str, ComputerResponse: str, CommandType: str = ""):
    # Зберегти обмін.
    GetMemory().SaveExchange(UserQuery, ComputerResponse, CommandType)


def GetDialogHistory(Limit: int = 50, SessionId: Optional[str] = None) -> List[Dict[str, Any]]:
    # Отримати історію.
    return GetMemory().GetDialogHistory(Limit, SessionId)


def SetContext(Key: str, Value: Any):
    # Встановити контекст.
    GetMemory().SetContext(Key, Value)


def GetContext(Key: str, Default: Any = None) -> Any:
    # Отримати контекст.
    return GetMemory().GetContext(Key, Default)


# Зворотна сумісність для завантажувача
MemoryService = ComputerMemory

__all__ = ["ComputerMemory", "MemoryChip", "GetMemory", "SaveExchange", "GetDialogHistory", "SetContext", "GetContext", "MemoryService"]
