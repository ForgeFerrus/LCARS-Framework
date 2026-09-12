from __future__ import annotations
import time
# Titanium Bridge Migration: from dataclasses import dataclass, field
# Titanium Bridge Migration: from typing import List, Optional
from lcars.modules.library import database_manager
from lcars.engineering.telemetry import emit_telemetry

@dataclass
class Call:
    id: Optional[int] = None
    caller: str = ""
    callee: str = ""
    timestamp: float = field(default_factory=lambda: time.time())
    duration: Optional[float] = None
    status: Optional[str] = None  # started, ended, missed

class CallSubsystem:
    def __init__(self):
        self.matrix = database_manager
        self._init_storage()

    def _init_storage(self):
        sql = """
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caller TEXT NOT NULL,
            callee TEXT NOT NULL,
            timestamp REAL NOT NULL,
            duration REAL,
            status TEXT
        )
        """
        self.matrix.execute_global("comm", sql)
        emit_telemetry("COMM", "PROCESS: STORAGE_READY. Call matrix set.")

    def start_call(self, caller: str, callee: str) -> int:
        sql = "INSERT INTO calls (caller, callee, timestamp, status) VALUES (?,?,?,?)"
        params = (caller, callee, time.time(), "started")
        row_id = self.matrix.execute_global("comm", sql, params)
        emit_telemetry("COMM", f"CALL_STARTED: {row_id} {caller} -> {callee}")
        return row_id

    def end_call(self, call_id: int, duration: float):
        sql = "UPDATE calls SET duration = ?, status = ? WHERE id = ?"
        self.matrix.execute_global("comm", sql, (duration, "ended", call_id))
        emit_telemetry("COMM", f"CALL_ENDED: {call_id} duration {duration}s")

    def get_calls(self, participant: str) -> List[Call]:
        sql = """
        SELECT id, caller, callee, timestamp, duration, status FROM calls
        WHERE caller = ? OR callee = ? ORDER BY timestamp DESC
        """
        rows = self.matrix.execute_global("comm", sql, (participant, participant))
        return [Call(*row) for row in rows]

# Глобальний екземпляр системи дзвінків
call_system = CallSubsystem()
