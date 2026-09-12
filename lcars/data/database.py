# ◤ TITANIUM LCARS DATABASE CORE // STARFLEET CANON 🖖
# ◤ TITANIUM LCARS DATABASE ENGINE // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/database/core.py
# ФАЙЛ: lcars/database/database.py
# ОПИС: Ядро бази даних LCARS (SQLite Engine & Model ORM).
#       Забезпечує потокобезпечне зберігання даних зорельота, виконання транзакцій,
#       автоматичне створення таблиць та реєстр ізолінійних оптичних чіпів.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
from contextlib import contextmanager
from lcars.base.type import LCARS
from lcars.base.info import Version
from lcars.service.chronometer import Chronometer

# ═════════════════════════════════════════════════════════════════════
# 1. ПОМИЛКИ БАЗИ ДАНИХ (DATABASE ERRORS)
# ═════════════════════════════════════════════════════════════════════
class DatabaseError(Exception, LCARS):
    # Базова помилка операцій з базою даних
    def __init__(self, Message: str = ""):
        super().__init__(f"DatabaseError: {Message}")
        self.Message = Message

class RecordNotFound(DatabaseError):
    # Запис не знайдено в таблиці
    def __init__(self, Message: str = "Record not found"):
        super().__init__(Message)

class ValidationError(DatabaseError):
    # Помилка перевірки цілісності даних
    def __init__(self, Message: str = "Data validation failed"):
        super().__init__(Message)

# ═════════════════════════════════════════════════════════════════════
# 2. РУШІЙ БАЗИ ДАНИХ LCARS (DATABASE ENGINE)
# ═════════════════════════════════════════════════════════════════════
class Database(LCARS):
    # Потокобезпечний реляційний рушій SQLite для підсистем LCARS
    SystemVersion = Version.Release

    def __init__(self, DbName: str = "system.db"):
        super().__init__(Id=f"Database.{DbName}")
        self.Version = Version.Release
        self.Passport = Version.Passport()

        PathModule = LCARS.System.Path
        DbDir = PathModule(__file__).resolve().parent if PathModule else None
        self.DbPath = (DbDir / DbName) if DbDir else None

        ThreadingModule = LCARS.Import("threading")
        self.LocalState = ThreadingModule.local() if ThreadingModule else None
        self.Lock = ThreadingModule.RLock() if ThreadingModule else None

    def GetConnection(self) -> any:
        # Отримання локального для потоку з'єднання з базою даних
        if not self.LocalState:
            return None
        if not hasattr(self.LocalState, "Conn") or self.LocalState.Conn is None:
            Sqlite = LCARS.Import("sqlite3")
            if Sqlite and self.DbPath:
                Conn = Sqlite.connect(str(self.DbPath), check_same_thread=False)
                Conn.row_factory = Sqlite.Row
                self.LocalState.Conn = Conn
        return getattr(self.LocalState, "Conn", None)

    @contextmanager
    def Transaction(self):
        # Менеджер контексту для атомарних транзакцій
        Conn = self.GetConnection()
        if self.Lock:
            self.Lock.acquire()
        try:
            yield Conn
            if Conn:
                Conn.commit()
        finally:
            if self.Lock:
                self.Lock.release()

    def Execute(self, Sql: str, Parameters: tuple = ()) -> any:
        # Виконання SQL запиту з параметрами
        if self.Lock:
            self.Lock.acquire()
        try:
            Conn = self.GetConnection()
            if Conn:
                return Conn.execute(Sql, Parameters)
            return None
        finally:
            if self.Lock:
                self.Lock.release()

    def FetchOne(self, Sql: str, Parameters: tuple = ()) -> dict | None:
        # Отримання одного рядка у вигляді словника
        if self.Lock:
            self.Lock.acquire()
        try:
            Cursor = self.Execute(Sql, Parameters)
            if Cursor:
                Row = Cursor.fetchone()
                return dict(Row) if Row else None
            return None
        finally:
            if self.Lock:
                self.Lock.release()

    def FetchAll(self, Sql: str, Parameters: tuple = ()) -> list[dict]:
        # Отримання всіх рядків у вигляді списку словників
        if self.Lock:
            self.Lock.acquire()
        try:
            Cursor = self.Execute(Sql, Parameters)
            if Cursor:
                Rows = Cursor.fetchall()
                return [dict(R) for R in Rows]
            return []
        finally:
            if self.Lock:
                self.Lock.release()

    def Insert(self, Table: str, Data: dict[str, any]) -> int:
        # Вставка запису та повернення його ID
        if not Data:
            return 0
        Columns = ", ".join(Data.keys())
        Placeholders = ", ".join("?" * len(Data))
        Sql = f"INSERT INTO {Table} ({Columns}) VALUES ({Placeholders})"
        with self.Transaction() as Conn:
            if Conn:
                Cursor = Conn.execute(Sql, tuple(Data.values()))
                return int(Cursor.lastrowid or 0)
        return 0

    def Upsert(self, Table: str, Data: dict[str, any], UniqueCols: list[str]) -> int:
        # Вставка або оновлення запису за унікальними полями
        if not Data:
            return 0
        Columns = ", ".join(Data.keys())
        Placeholders = ", ".join("?" * len(Data))
        Updates = ", ".join(f"{K}=excluded.{K}" for K in Data.keys() if K not in UniqueCols)
        ConflictTarget = ",".join(UniqueCols)
        Sql = f"INSERT INTO {Table} ({Columns}) VALUES ({Placeholders}) ON CONFLICT({ConflictTarget}) DO UPDATE SET {Updates}"
        with self.Transaction() as Conn:
            if Conn:
                Cursor = Conn.execute(Sql, tuple(Data.values()))
                return int(Cursor.lastrowid or Cursor.rowcount or 0)
        return 0

    def Update(self, Table: str, Data: dict[str, any], Where: str, Params: tuple = ()) -> int:
        # Оновлення записів, що відповідають умові
        if not Data:
            return 0
        SetClause = ", ".join(f"{K}=?" for K in Data.keys())
        Sql = f"UPDATE {Table} SET {SetClause} WHERE {Where}"
        with self.Transaction() as Conn:
            if Conn:
                Cursor = Conn.execute(Sql, tuple(Data.values()) + Params)
                return int(Cursor.rowcount or 0)
        return 0

    def Delete(self, Table: str, Where: str, Params: tuple = ()) -> int:
        # Видалення записів за умовою
        Sql = f"DELETE FROM {Table} WHERE {Where}"
        with self.Transaction() as Conn:
            if Conn:
                Cursor = Conn.execute(Sql, Params)
                return int(Cursor.rowcount or 0)
        return 0

    def TableExists(self, TableName: str) -> bool:
        # Перевірка наявності таблиці в базі даних
        Sql = "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?"
        return self.FetchOne(Sql, (TableName,)) is not None

    def CreateTable(self, TableName: str, SchemaSql: str) -> None:
        # Створення таблиці за схемою SQL
        with self.Transaction() as Conn:
            if Conn:
                Conn.execute(SchemaSql)

    # Аліаси сумісності зі старим кодом
    execute = Execute
    fetchone = FetchOne
    fetchall = FetchAll
    insert = Insert
    upsert = Upsert
    update = Update
    delete = Delete
    table_exists = TableExists
    create_table = CreateTable
    transaction = Transaction

# Сумісний аліас для старого коду
LCARSDatabase = Database

# ═════════════════════════════════════════════════════════════════════
# 3. БАЗОВА МОДЕЛЬ ТАБЛИЦІ (MODEL ORM)
# ═════════════════════════════════════════════════════════════════════
class Model(LCARS):
    # Базовий клас об'єктно-реляційної моделі (ORM)
    SystemVersion = Version.Release
    TableName: str = ""
    Schema: str = ""
    UniqueCols: list[str] = []

    # Аліаси для старого коду
    TABLE_NAME = TableName
    SCHEMA = Schema
    UNIQUE_COLS = UniqueCols

    def __init__(self, DbNode: Database | None = None):
        super().__init__(Id=f"Model.{self.TableName}")
        self.Db = DbNode or GetDatabase()
        self.EnsureTable()

    def EnsureTable(self) -> None:
        # Створення таблиці у разі її відсутності
        TName = self.TableName or getattr(self, "TABLE_NAME", "")
        TSchema = self.Schema or getattr(self, "SCHEMA", "")
        if TName and TSchema and not self.Db.TableExists(TName):
            self.Db.CreateTable(TName, TSchema)

    def Save(self, Data: dict[str, any]) -> int:
        # Збереження запису (вставка або upsert)
        TName = self.TableName or getattr(self, "TABLE_NAME", "")
        UCols = self.UniqueCols or getattr(self, "UNIQUE_COLS", [])
        if UCols:
            return self.Db.Upsert(TName, Data, UCols)
        return self.Db.Insert(TName, Data)

    def Get(self, RecordId: int | str) -> dict | None:
        # Отримання запису за його ID
        TName = self.TableName or getattr(self, "TABLE_NAME", "")
        return self.Db.FetchOne(f"SELECT * FROM {TName} WHERE id = ?", (RecordId,))

    def GetBy(self, **Kwargs: any) -> dict | None:
        # Пошук першого запису за значеннями колонок
        if not Kwargs:
            return None
        TName = self.TableName or getattr(self, "TABLE_NAME", "")
        WhereStr = " AND ".join(f"{K} = ?" for K in Kwargs.keys())
        return self.Db.FetchOne(f"SELECT * FROM {TName} WHERE {WhereStr}", tuple(Kwargs.values()))

    def Find(self, **Kwargs: any) -> list[dict]:
        # Пошук списку записів за критеріями
        if not Kwargs:
            return self.All()
        TName = self.TableName or getattr(self, "TABLE_NAME", "")
        WhereStr = " AND ".join(f"{K} = ?" for K in Kwargs.keys())
        return self.Db.FetchAll(f"SELECT * FROM {TName} WHERE {WhereStr}", tuple(Kwargs.values()))

    def All(self, Limit: int = 1000, OrderBy: str = "id DESC") -> list[dict]:
        # Отримання всіх записів таблиці
        TName = self.TableName or getattr(self, "TABLE_NAME", "")
        return self.Db.FetchAll(f"SELECT * FROM {TName} ORDER BY {OrderBy} LIMIT ?", (Limit,))

    def Delete(self, RecordId: int | str) -> bool:
        # Видалення запису за ID
        TName = self.TableName or getattr(self, "TABLE_NAME", "")
        Count = self.Db.Delete(TName, "id = ?", (RecordId,))
        return Count > 0

    def Count(self) -> int:
        # Підрахунок загальної кількості записів
        TName = self.TableName or getattr(self, "TABLE_NAME", "")
        Result = self.Db.FetchOne(f"SELECT COUNT(*) as count FROM {TName}")
        return Result["count"] if Result else 0

    # Аліаси сумісності
    save = Save
    get = Get
    get_by = GetBy
    find = Find
    all = All
    delete = Delete
    count = Count

# ═════════════════════════════════════════════════════════════════════
# 4. МОДЕЛЬ ІЗОЛІНІЙНИХ ЧІПІВ (ISOLINEAR CHIP REGISTRY)
# ═════════════════════════════════════════════════════════════════════
class IsolinearModel(Model):
    # Таблиця ізолінійних чіпів та скомпільованих артефактів
    TableName = "isolinear_chips"
    UniqueCols = ["id"]
    Schema = """
    CREATE TABLE IF NOT EXISTS isolinear_chips (
        id TEXT PRIMARY KEY,
        kind TEXT,
        source TEXT,
        output TEXT,
        manifest TEXT,
        wrapper TEXT,
        created_at TEXT,
        stardate TEXT,
        hash TEXT
    )
    """

class SubsystemStateModel(Model):
    # Модель станів підсистем ядра
    TableName = "subsystem_states"
    UniqueCols = ["id"]
    Schema = """
    CREATE TABLE IF NOT EXISTS subsystem_states (
        id TEXT PRIMARY KEY,
        subsystem TEXT NOT NULL,
        status TEXT NOT NULL,
        health REAL DEFAULT 1.0,
        stardate TEXT,
        metadata_json TEXT
    )
    """

class EngineeringTelemetryModel(Model):
    # Модель показників інженерної телеметрії
    TableName = "engineering_metrics"
    UniqueCols = ["id"]
    Schema = """
    CREATE TABLE IF NOT EXISTS engineering_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subsystem TEXT NOT NULL,
        parameter TEXT NOT NULL,
        value REAL NOT NULL,
        unit TEXT NOT NULL,
        stardate TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """

class MissionEventModel(Model):
    # Модель подій та місій хронометра
    TableName = "mission_events"
    UniqueCols = ["id"]
    Schema = """
    CREATE TABLE IF NOT EXISTS mission_events (
        id TEXT PRIMARY KEY,
        event_type TEXT NOT NULL,
        title TEXT NOT NULL,
        stardate REAL NOT NULL,
        earth_date TEXT NOT NULL,
        status TEXT NOT NULL,
        details TEXT
    )
    """

class StarshipRegistryModel(Model):
    # Модель флоту та зорельотів Федерації
    TableName = "starships"
    UniqueCols = ["registry"]
    Schema = """
    CREATE TABLE IF NOT EXISTS starships (
        registry TEXT PRIMARY KEY,
        name TEXT,
        ship_class TEXT,
        status TEXT,
        captain TEXT,
        max_warp REAL,
        crew_complement INTEGER
    )
    """

# Глобальний екземпляр бази даних
_GlobalDatabase: Database | None = None

def GetDatabase(DbName: str = "system.db") -> Database:
    # Отримання синглтона бази даних LCARS
    global _GlobalDatabase
    if _GlobalDatabase is None:
        _GlobalDatabase = Database(DbName)
    return _GlobalDatabase

# Аліас сумісності
get_db = GetDatabase

__all__ = [
    "DatabaseError",
    "RecordNotFound",
    "ValidationError",
    "Database",
    "LCARSDatabase",
    "Model",
    "IsolinearModel",
    "SubsystemStateModel",
    "EngineeringTelemetryModel",
    "MissionEventModel",
    "StarshipRegistryModel",
    "GetDatabase",
    "get_db",
]
