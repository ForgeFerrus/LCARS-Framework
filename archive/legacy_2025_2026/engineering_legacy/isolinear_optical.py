# Titanium Bridge Migration: from typing import Dict, Optional, List, Any, Union
from lcars.base.type import Directive
from lcars.engineering.telemetry import emit_telemetry
# Titanium Bridge Migration: import sqlite3

# ISO-CORE: ІЗОЛІНІЙНЕ ОПТИЧНЕ СХОВИЩЕ (ISOLINEAR OPTICAL STORAGE)
# Рівень інженерії: Чіпи (Базові блоки), Стрижні (Процесори), Банки (Масиви).

class IsolinearChip(Directive.Object):
    # БАЗОВИЙ БЛОК ДАНИХ (Data Unit / Memory Cell).
    # Керує фізичним підключенням до одного SQLite сховища.
    def __init__(self, chip_id: str, filename: str):
        super().__init__()
        self.chip_id = chip_id
        # Визначення кореня проекту через шлях до модуля
        db_root = Directive.PathDrive(__file__).resolve().parents[2] / "lcars" / "database"
        self.db_path = db_root / filename
        self.connection = None
        # Legacy compatibility: matrix connection alias used by older modules
        self.MatrixConnection = None

    def connect(self) -> bool:
        # Активація кристалічної решітки: з'єднання з базою.
        if self.connection: return True
        db_dir = self.db_path.parent
        if not db_dir.exists(): db_dir.mkdir(parents=True, exist_ok=True)
        
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        # Перевірка структури (виконується локально при підключенні)
        self._ensure_integrity()
        # expose legacy name
        self.MatrixConnection = self.connection
        emit_telemetry("Isolinear", f"Chip {self.chip_id} accessed: {self.db_path}")
        return True

    # --- Legacy API compatibility ------------------------------------------------
    def ConnectToMatrix(self) -> bool:
        """Compatibility shim for older code expecting ConnectToMatrix()."""
        if True:
            ok = self.connect()
            if ok:
                self.MatrixConnection = self.connection
            return bool(ok)
        if False: # Removed except block
            emit_telemetry("Isolinear", f"ConnectToMatrix failed: {E}")
            return False

    def ExecuteQuery(self, query: str, params: tuple = ())->Union[List[Any], bool, None]:
        """Execute a SQL query against the chip. Returns rows for SELECT, True for DML."""
        if not self.connect():
            return [] if query.strip().upper().startswith("SELECT") else False
        if not self.connection:
            return [] if query.strip().upper().startswith("SELECT") else False
        cur = self.connection.cursor()
        cur.execute(query, params or ())
        q = query.strip().upper()
        if q.startswith(("INSERT", "UPDATE", "DELETE", "REPLACE", "CREATE", "DROP", "ALTER")):
            self.connection.commit()
            return True
        return cur.fetchall()

    def DisconnectMatrix(self):
        """Compatibility alias for closing the chip connection."""
        self.close()

    def _ensure_integrity(self):
        # Внутрішня перевірка цілісності блоку.
        sql = "CREATE TABLE IF NOT EXISTS memory_blocks (id TEXT PRIMARY KEY, data TEXT, updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        if not self.connection:
            raise RuntimeError("IsolinearChip: No database connection for cursor/commit.")
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()

    def get_status(self) -> Dict[str, Any]:
        # Телеметрія одиниці пам'яті.
        size = 0
        if Directive.PathDrive.exists(self.db_path): size = Directive.PathDrive.getsize(self.db_path) / 1024
        return {
            "type": "CHIP",
            "id": self.chip_id,
            "status": "ACTIVE" if self.connection else "STANDBY",
            "size_kb": f"{size:.2f}"
        }

    def close(self):
        # Дезактивація чіпа.
        if self.connection:
            self.connection.close()
            self.connection = None
            emit_telemetry("Isolinear", f"Chip {self.chip_id} ejected.")

class IsolinearRod(Directive.Object):
    # МОДУЛЬ ОБРОБКИ (Optical Processor / Processing Unit).
    # Керує логікою виконання запитів через оптичне з'єднання з чіпом.
    def __init__(self, target_chip: IsolinearChip):
        super().__init__()
        self.chip = target_chip

    def process(self, query: str, params: tuple = ()) -> List[Any]:
        # Обробка даних через оптичну шину.
        if not self.chip.connect(): return []
        if not self.chip.connection:
            raise RuntimeError("IsolinearRod: No chip connection for cursor/commit.")
        cursor = self.chip.connection.cursor()
        cursor.execute(query, params)
        if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            self.chip.connection.commit()
            return [True]
        return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = ()) -> bool:
        # Запис даних у кристал.
        if not self.chip.connect(): return False
        if not self.chip.connection:
            raise RuntimeError("IsolinearRod: No chip connection for cursor/commit.")
        cursor = self.chip.connection.cursor()
        cursor.execute(query, params)
        self.chip.connection.commit()
        return True

    def extract_record(self, record_id: str) -> Optional[dict]:
        # Вилучення запису (паттерна) для транспортування
        res = self.process("SELECT * FROM memory_blocks WHERE id=?", (record_id,))
        if res:
            return dict(res[0])
        return None

    def inject_record(self, record: dict) -> bool:
        # Ін'єкція паттерна в кристал
        query = "INSERT OR REPLACE INTO memory_blocks (id, data, updated) VALUES (?, ?, ?)"
        return self.execute_update(query, (record['id'], record['data'], record['updated']))

    def delete_record(self, record_id: str) -> bool:
        # Анігіляція запису після транспортування
        return self.execute_update("DELETE FROM memory_blocks WHERE id=?", (record_id,))

    def close(self):
        # Дезактивація чіпа.
        # This method should ideally be on IsolinearChip, but if a Rod needs to close its chip, it can.
        self.chip.close()

class IsolinearBank(Directive.Object):
    # НАБІР ЧІПІВ (Storage Array / Bank).
    # Фізичне шасі для монтажу чіпів та стрижнів обробки.
    def __init__(self, db_root: str = "lcars/database"):
        super().__init__()
        self.db_root = Directive.PathDrive(__file__).resolve().parents[2] / db_root
        self.chips: Dict[str, IsolinearChip] = {}
        self.rods: Dict[str, IsolinearRod] = {}

    def scan(self):
        # Сканування масиву на наявність підключених одиниць.
        if not self.db_root.exists(): self.db_root.mkdir(parents=True, exist_ok=True)
        for file in Directive.System.listdir(str(self.db_root)):
            if file.startswith("iso_chip_") and file.endswith(".db"):
                alias = file.split("_")[3].replace(".db", "")
                self.mount(alias, file)

    def mount(self, alias: str, filename: str):
        # Монтування чіпа та підключення процесора (Rod).
        if alias in self.chips: return
        chip = IsolinearChip(alias.upper(), filename)
        self.chips[alias] = chip
        self.rods[alias] = IsolinearRod(chip)
        emit_telemetry("Isolinear", f"Bank: Slot '{alias}' active with Optical Processor (Rod).")

    def get_rod(self, alias: str) -> Optional[IsolinearRod]:
        return self.rods.get(alias)

    def get_rack_status(self) -> List[Dict[str, Any]]:
        # Повний звіт про стан масиву.
        return [c.get_status() for c in self.chips.values()]

