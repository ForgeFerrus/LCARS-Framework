"""
LCARS Computer Memory — Persistent Storage for Board Computer
═══════════════════════════════════════════════════════════════
Зберігає:
  - Сесії роботи (коли запускався, скільки працював)
  - Історію діалогів (команди + відповіді)
  - Контекст розмови (для безперервності між перезапусками)
  - Системні примітки та закладки
═══════════════════════════════════════════════════════════════
"""

import sqlite3
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("lcars.computer_memory")

DB_VERSION = 1

class ComputerMemory:
    """
    Persistent memory for the LCARS Board Computer.
    Uses SQLite stored in database/computer_memory.db
    """

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path(__file__).resolve().parents[2] / "database" / "computer_memory.db"
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._conn: Optional[sqlite3.Connection] = None
        self._session_id: Optional[str] = None
        self._connect()
        self._init_schema()
        self._start_session()
        if self._session_id:
            logger.info(f"◤ COMPUTER MEMORY: ACTIVE | SESSION {self._session_id[:8]}")
        else:
            logger.info("◤ COMPUTER MEMORY: ACTIVE | SESSION N/A")

    # ──────────────────────────────────────────────────────
    #  CONNECTION
    # ──────────────────────────────────────────────────────

    def _connect(self):
        """Open connection to SQLite DB."""
        try:
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        except Exception as e:
            logger.error(f"MEMORY DB ERROR: {e}")
            self._conn = None

# ...existing code...
