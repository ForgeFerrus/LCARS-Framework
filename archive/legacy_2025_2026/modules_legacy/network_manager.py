
# Titanium Bridge Migration: import sqlite3
# Titanium Bridge Migration: import uuid
import time
from urllib.parse import urlparse
# Titanium Bridge Migration: import requests
from lcars.base.type import SystemComponent, Signal
from lcars.engineering.telemetry import emit_telemetry

class NetworkManager(SystemComponent):
    # Централізоване керування мережевими операціями.
    _instance = None
    network_status_changed = Signal(bool)
    request_logged = Signal(dict)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_network()
        return cls._instance

    def _init_network(self):
        from lcars.modules.config_manager import config_manager
        self.enabled = bool(config_manager.get('network', 'enabled', True))
        self.require_confirmation = bool(config_manager.get('network', 'require_confirmation', False))
        self.allowlist = config_manager.get('network', 'allowlist', ["localhost", "127.0.0.1"])
        self.db_path = "lcars_data/network_comm.db"
        self._init_schema()
        emit_telemetry("Network", "PROCESS: SUBSPACE_LINK_READY. Security protocols active.")

    def _init_schema(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS network_logs (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                url TEXT,
                status_code INTEGER,
                success INTEGER,
                note TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS allowlist (
                domain TEXT PRIMARY KEY,
                added_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def is_allowed(self, url: str) -> bool:
        host = (urlparse(url).hostname or "").lower()
        if not host:
            return False
        if host in ("localhost", "127.0.0.1"):
            return True
        for domain in self.allowlist:
            if host == domain or host.endswith("." + domain):
                return True
        return False

    def subspace_request(self, url: str, timeout: int = 15) -> str:
        if not self.enabled:
            return "◤ SUBSPACE ERROR: NETWORK_OFFLINE"
        if not self.is_allowed(url):
            self._log_request(url, 403, False, "BLOCKED: Domain not in allowlist")
            return "◤ SUBSPACE ERROR: PROTOCOL_VOID (Domain Blocked)"
            
            resp = requests.get(url, timeout=timeout)
            status = resp.status_code
            success = resp.ok
            text = resp.text[:2048]
            self._log_request(url, status, success, "")
            if not success:
                return f"◤ SUBSPACE ERROR: HTTP {status}"
            return f"◤ SUBSPACE DOWNLINK SUCCESS [{status}]: {url}\n{text}"

    def _log_request(self, url: str, status: int, success: bool, note: str = ""):
        req_id = str(uuid.uuid4())
        ts = time.strftime('%Y-%m-%dT%H:%M:%S')
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO network_logs (id, timestamp, url, status_code, success, note) VALUES (?, ?, ?, ?, ?, ?)",
            (req_id, ts, url, status, 1 if success else 0, note)
        )
        conn.commit()
        conn.close()
        emit_telemetry("Network", f"EVENT: Request {status} to {url[:30]}...")
        self.request_logged.emit({
            "id": req_id,
            "timestamp": ts,
            "url": url,
            "status_code": status,
            "success": success,
            "note": note
        })

    def set_enabled(self, status: bool):
        self.enabled = status
        self.network_status_changed.emit(status)

network_manager = NetworkManager()
get_network = lambda: network_manager
