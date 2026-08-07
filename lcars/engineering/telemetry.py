# ◤ TITANIUM TELEMETRY HUB
# LCARS Framework :: TELEMETRY // METRICS // NO_Q PROTOCOL
# ОПИС: Централізоване логування та збір системних метрик.
# СТАНДАРТ: Titanium CamelCase, Zero-Except.
# ─────────────────────────────────────────────────────────────────────────────
from datetime import datetime
from lcars.base.version import getVersion
from lcars.core.signal import ODN
__version__ = getVersion()

def EmitTelemetry(source: str, message: str, level: str = "info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # ASCII-safe prefix for Windows CP1251
    prefix_map = {
        "info": "[INFO]",
        "warning": "[WARN]",
        "error": "[ERROR]",
        "success": "[OK]"
    }
    prefix = prefix_map.get(level.lower(), "[LOG]")
    
    log_line = f">> MISSION LOGS: [{timestamp}] {source.upper()} {prefix}: {message}"
    
    # Remove Unicode special chars for Windows compatibility
    safe_line = log_line.replace("\u25e4", ">").replace("\u25e5", "v").replace("\u26a0", "!")

    print(safe_line)

    TelemetryMap = {
        "timestamp": timestamp,
        "source": source,
        "level": level.lower(),
        "message": message,
        "line": safe_line,
    }
    ODN.Emit("Telemetry.Event", TelemetryMap)

# База телеметрії для зберігання та передачі метрик.
class TelemetryDatabase:
    def __init__(self):
        self.callbacks = []
    # Реєстрація зворотного виклику для отримання телеметрії.
    def RegisterTelemetryCallback(self, cb):
        self.callbacks.append(cb)

TelemetryDb = TelemetryDatabase()

def GetTelemetryDatabase():
    return TelemetryDb

# Зворотна сумісність
emit_telemetry = EmitTelemetry

__all__ = ["EmitTelemetry", "GetTelemetryDatabase", "emit_telemetry"]
