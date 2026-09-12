# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import shutil
# Titanium Bridge Migration: import traceback
from PyQt6.QtCore import QObject, pyqtSignal
from lcars.engineering.telemetry import emit_telemetry

class DamageControl(QObject):
    # Система боротьби за живучість (Автофікс).
    # Забезпечує цілісність файлової структури, відновлює конфігурації
    # та перехоплює критичні збої (краші), уникаючи вильоту на робочий стіл.

    integrity_breach = pyqtSignal(str)   # Сигнал про виявлення пошкоджень
    repair_completed = pyqtSignal(str)   # Сигнал про успішне відновлення
    critical_failure = pyqtSignal(str)   # Сигнал про невідворотний збій

    def __init__(self, workspace_root: str):
        super().__init__()
        self.workspace_root = workspace_root
        self._hook_core_dump()
        emit_telemetry("DamageControl", "System online. Monitoring structural integrity.")

    def verify_hull_integrity(self):
        # Перевіряє наявність ключових директорій. Якщо вони зникли — відтворює їх.
        critical_sections = ["config", "database", "logs", "plugins", "archive"]
        for section in critical_sections:
            path = os.path.join(self.workspace_root, section)
            if not os.path.exists(path):
                self.integrity_breach.emit(f"Missing section: {section}")
                os.makedirs(path, exist_ok=True)
                emit_telemetry("DamageControl", f"Reconstructed missing directory: {section}", "warn")
                self.repair_completed.emit(section)

    def verify_and_repair_config(self):
        # Перевіряє config.json. Якщо файл порожній або структурно невірний, відновлює з config.example.json.
        config_path = os.path.join(self.workspace_root, "config", "config.json")
        example_path = os.path.join(self.workspace_root, "config", "config.example.json")

        if not os.path.exists(config_path):
            self.integrity_breach.emit("config.json missing")
            self._restore_from_backup(example_path, config_path)
            return

        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Просте розгалуження (if/else) замість виключень для перевірки структури
        if not content or not content.startswith("{") or not content.endswith("}"):
            self.integrity_breach.emit("config.json corrupted")
            self._restore_from_backup(example_path, config_path)

    def purge_anomalies(self):
        # Очищення системи від тимчасових та сміттєвих файлів
        db_path = os.path.join(self.workspace_root, "database")
        if not os.path.exists(db_path):
            return

        for filename in os.listdir(db_path):
            if filename.endswith(".db-journal") or filename.endswith(".tmp"):
                filepath = os.path.join(db_path, filename)
                os.remove(filepath)
                emit_telemetry("DamageControl", f"Purged phantom file: {filename}")

    def _restore_from_backup(self, source: str, destination: str):
        # Виконує фізичне відновлення файлу
        if os.path.exists(source):
            shutil.copy2(source, destination)
            emit_telemetry("DamageControl", f"Restored {destination} from backup.")
            self.repair_completed.emit("Configuration restored")
        else:
            msg = f"Fatal error: Backup source {source} not found."
            emit_telemetry("DamageControl", msg, "critical")
            self.critical_failure.emit(msg)

    def _hook_core_dump(self):
        # Замінює стандартний обробник помилок Python на системний сигнал LCARS
        def exception_handler(exc_type, exc_value, exc_tb):
            error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            emit_telemetry("CORE DUMP", f"Unhandled Exception:\n{error_msg}", "critical")
            
            dump_file = os.path.join(self.workspace_root, "crash_log.txt")
            with open(dump_file, "a", encoding="utf-8") as f:
                f.write(f"\n--- CORE DUMP ---\n{error_msg}\n")
                
            self.critical_failure.emit("System destabilized. See crash_log.txt.")

        sys.excepthook = exception_handler
