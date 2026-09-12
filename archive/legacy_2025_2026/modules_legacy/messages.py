from __future__ import annotations
import time
# Titanium Bridge Migration: from dataclasses import dataclass, field
# Titanium Bridge Migration: from typing import List, Optional
from lcars.modules.library import database_manager
from lcars.engineering.telemetry import emit_telemetry

@dataclass
class Message:
    id: Optional[int] = None
    sender: str = ""
    recipient: str = ""
    timestamp: float = field(default_factory=lambda: time.time())
    content: str = ""
    status: Optional[str] = None  # sent, delivered, read

class MessageSubsystem:
    def __init__(self):
        self.matrix = database_manager
        self._init_storage()

    def _init_storage(self):
        sql = """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            timestamp REAL NOT NULL,
            content TEXT NOT NULL,
            status TEXT
        )
        """
        self.matrix.execute_global("comm", sql)
        emit_telemetry("COMM", "PROCESS: STORAGE_READY. Message matrix set.")

    def send_message(self, sender: str, recipient: str, content: str) -> int:
        sql = "INSERT INTO messages (sender, recipient, timestamp, content, status) VALUES (?,?,?,?,?)"
        params = (sender, recipient, time.time(), content, "sent")
        row_id = self.matrix.execute_global("comm", sql, params)
        emit_telemetry("COMM", f"MESSAGE_SENT: {row_id} from {sender} to {recipient}")
        return row_id

    def get_messages(self, participant: str) -> List[Message]:
        sql = """
        SELECT id, sender, recipient, timestamp, content, status FROM messages
        WHERE sender = ? OR recipient = ? ORDER BY timestamp DESC
        """
        rows = self.matrix.execute_global("comm", sql, (participant, participant))
        return [Message(*row) for row in rows]

    def update_status(self, message_id: int, status: str):
        sql = "UPDATE messages SET status = ? WHERE id = ?"
        self.matrix.execute_global("comm", sql, (status, message_id))
        emit_telemetry("COMM", f"MESSAGE_STATUS: {message_id} set to {status}")

# Глобальний екземпляр системи повідомлень
message_system = MessageSubsystem()
