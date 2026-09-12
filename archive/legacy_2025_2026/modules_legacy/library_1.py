# LCARS LIBRARY & ISOLINEAR CORE (TITANIUM STANDARD)
# Центральний архів та ядро керування ізолінійними накопичувачами.
# "Бібліотека" — це точка входу до всіх знань зорельота.
# Titanium Bridge Migration: from typing import List, Dict, Optional, Tuple, Any, Union
from lcars.base.type import Directive, SystemComponent
from lcars.engineering.telemetry import emit_telemetry
from lcars.engineering.isolinear_optical import IsolinearRod

# ── 1. ОПТИЧНА МЕРЕЖА ДАНИХ (ODN - OPTICAL DATA NETWORK) ──

class ODN(SystemComponent):
    # ПІДСИСТЕМА ПЕРЕДАЧІ ТА ОБРОБКИ ДАНИХ. Керує банками чипів та стрижнями.
    _instance = None
    _init_done = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._bank = None
        return cls._instance

    def get_bank(self):
        # Отримання власного IsolinearBank.
        if self._bank is None:
            from lcars.engineering.architecture import ARCHITECTURE
            self._bank = ARCHITECTURE.isolinear_bank

            # Виконуємо ініціалізацію один раз
            if not self._init_done:
                self._init_done = True
                self._init_chassis()
        return self._bank

    def _init_chassis(self):
        # Ініціалізація та монтування стандартних чипів за протоколом
        emit_telemetry("Database", "PROCESS: CORE_BOOT. Accessing Isolinear Rack...")
        
        mounts = {
            "core": "iso_chip_01_core.db",
            "memory": "iso_chip_02_memory.db",
            "linguistics": "iso_chip_03_linguistics.db",
            "telemetry": "iso_chip_04_telemetry.db",
            "copilot": "iso_chip_05_copilot.db",
            "english": "iso_chip_06_english.db",
            "archives": "iso_chip_07_archives.db",
            "comm": "iso_chip_08_comm.db"
        }
        
        for name, filename in mounts.items():
            self.get_bank().mount(name, filename)
        
        # Створення таблиці архівів
        sql = "CREATE TABLE IF NOT EXISTS archives (id INTEGER PRIMARY KEY AUTOINCREMENT, item_class TEXT NOT NULL, tag TEXT, data TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        self.execute_global("archives", sql)
        emit_telemetry("Database", "PROCESS_COMPLETE: ISOLINEAR_STORAGE_READY.")

    def register_chip(self, name: str, filename: str):
        # Реєстрація нового вузла в системній стійці.
        self.get_bank().mount(name, filename)

    def get_status(self) -> List[Dict[str, Any]]:
        # Отримання статусу працездатності чипів для інженерії.
        status = self.get_bank().get_rack_status()
        for item in status: item["type"] = "ISO_NODE"
        return status

    def execute_global(self, chip_name: str, query: str, params: tuple = ()) -> Union[list, bool]:
        # Виконання команди через оптичний процесор (Rod).
        rod = self.get_bank().get_rod(chip_name)
        if not rod: return []
        return rod.process(query, params)

    def get_chip(self, chip_name: str):
        # Повертає об'єкт IsolinearChip для доступу до шляху бази даних.
        rod = self.get_bank().get_rod(chip_name)
        if rod is None:
            return None
        return rod.chip

    def archive_record(self, item_class: str, data: str, tag: Optional[str] = None) -> bool:
        # Додавання запису до центрального архіву.
        query = "INSERT INTO archives (item_class, tag, data) VALUES (?, ?, ?)"
        tag_val = tag if tag is not None else ""
        result = self.execute_global("archives", query, (item_class, tag_val, data))
        return isinstance(result, bool) and result is True

    def index_system_files(self, start_dir: Optional[str] = None):
        # Сканування та індексація системних файлів зорельота.
        root = str(start_dir) if start_dir is not None else str(Directive.PathDrive(__file__).resolve().parents[2])
        scan_map = {
            "CORE": ["lcars/core/*designer.py", "lcars/system/*designer.py"],
            "UI": ["lcars/ui/*designer.py", "lcars/qml/*.qml"],
            "APPS": ["programs/**/*designer.py"],
            "TECH": ["lcars/engineering/*designer.py"]
        }
        
        # Використовуємо Path через Directive для глибокого сканування
        # Titanium Bridge Migration: from pathlib import Path
        root_path = Path(root)
        
        for data_class, patterns in scan_map.items():
            for pattern in patterns:
                for file_path in root_path.glob(pattern):
                    rel_path = file_path.relative_to(root_path)
                    self.archive_record(data_class, str(rel_path), file_path.suffix.lstrip('.').upper())

# ── 2. БІБЛІОТЕЧНИЙ СЕРВІС (Knowledge Access) ──

class Library(SystemComponent):
    # Менеджер локальної бібліотеки та архівних секторів.
    
    _SECTOR_MAP = {
        "DOCUMENTS": ["federation", "science"],
        "IMAGES": ["federation"],
        "MEDIA": ["sports"],
        "EDUCATION": ["education"],
        "FEDERATION": ["federation"],
        "SPORTS": ["sports"],
        "SCIENCE": ["science"],
    }

    def __init__(self, base_path: Optional[str] = None):
        super().__init__()
        self.Path = Directive.PathDrive
        self.root = self.Path(base_path or "lcars/data/archives").resolve()

    def get_sectors(self) -> List[str]:
        return ["DOCUMENTS", "IMAGES", "MEDIA", "EDUCATION"]

    def list_files(self, sector: str) -> List[Dict[str, Any]]:
        # Повернути список записів секції (Core Index -> Disk Fallback).
        task_id = f"LIB-{Directive.Chronon.now().microsecond % 1000:03d}"
        
        # 1. Спроба через Core Index
        odn_hub = get_odn()
        query = "SELECT tag, data FROM archives WHERE item_class = ?"
        db_results = odn_hub.execute_global("archives", query, (sector.upper(),))
        if isinstance(db_results, list):
            return [{"name": r[0], "path": r[1], "type": "DATA_CHIP"} for r in db_results]
        
        # 2. Fallback до файлової системи
        records = []
        if sector.upper() == "EDUCATION":
            records.append({"name": "English Learning", "type": "APP", "path": "english_learning"})
            
        folders = self._SECTOR_MAP.get(sector.upper(), [sector.lower().replace(" ", "_")])
        for folder in folders:
            path = self.root / folder
            if not path.exists(): continue
            
            for entry in path.iterdir():
                if entry.is_file():
                    ext = entry.suffix.lower()
                    ftype = "TEXT"
                    if ext in [".png", ".jpg", ".jpeg"]: ftype = "IMAGE"
                    elif ext in [".mp4", ".mkv"]: ftype = "VIDEO"
                    
                    records.append({
                        "name": entry.name,
                        "type": ftype,
                        "size": f"{entry.stat().st_size / 1024:.1f} KB",
                        "path": str(entry)
                    })
        
        emit_telemetry("Library", f"TASK_REPORT: {task_id}. Records listed for {sector}.")
        return records

# Синглтони та аліаси
library = Library()

# Ліниве отримання ODN (щоб уникнути циклічних імпортів при ініціалізації)
_odn_instance: Optional[ODN] = None
def get_odn() -> ODN:
    global _odn_instance
    if _odn_instance is None:
        _odn_instance = ODN()
    return _odn_instance

def get_database_manager() -> ODN:
    # Псевдонім для сумісності з інженерними модулями.
    return get_odn()

# Аліаси
odn = get_odn()
database_manager = odn

# Сумісність
get_library = lambda: library
LinguisticDatabase = ODN

__all__ = ["ODN", "odn", "database_manager", "Library", "library", "get_odn", "get_database_manager", "get_library", "LinguisticDatabase"]
