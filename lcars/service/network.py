# ◤ TITANIUM NETWORK SERVICE
# LCARS Framework :: SUBSPACE_LINK // NETWORK_OPS // SECURITY_PROTOCOLS
# ОПИС: Централізоване керування мережевими операціями та безпекою.
# ФУНКЦІЇ: HTTP запити, логування, allowlist, безпека.
# СТАНДАРТ: Titanium CamelCase, Zero-Except, Isolinear Chip.

from __future__ import annotations
import uuid
import time
from urllib.parse import urlparse
from typing import Optional, List
from pathlib import Path

from lcars.core.service import Service
from lcars.engineering.isolinear import IsolinearChip
from lcars.core.signal import ODN
from lcars.base.version import getVersion
from lcars.modules.storage import ResolveChipPath

# Ізолінійний чіп для мережевих логів (ISO-NET)
class NetworkChip(IsolinearChip):
    def __init__(self):
        PathRef = ResolveChipPath("Network Operations Chip")
        ChipId = PathRef.stem.split("-", 2)[0] + "-" + PathRef.stem.split("-", 2)[1]
        super().__init__(id=ChipId, array=ChipId.split("-", 1)[0], metadata={}, FilePath=PathRef)
        self.InitializeSchema()
        getVersion() 

    # Ініціалізація SQL-схеми для мережевих логів та allowlist
    def InitializeSchema(self):
        if not self.Connect():
            return

        Conn = self.Connection
        if Conn:
            Cursor = Conn.cursor()
            Cursor.executescript("""
                CREATE TABLE IF NOT EXISTS network_logs (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    url TEXT,
                    status_code INTEGER,
                    success INTEGER,
                    note TEXT
                );

                CREATE TABLE IF NOT EXISTS allowlist (
                    domain TEXT PRIMARY KEY,
                    added_at TEXT
                );
            """)
            Conn.commit()
            ODN.Emit("Network.Chip", "SCHEMA_INITIALIZED")


# Централізоване керування мережевими операціями та безпекою
class Network(Service):
    Name = "network"
    Dependencies: List[str] = ["config"]

    def __init__(self):
        self.Enabled = True
        self.RequireConfirmation = False
        self.Allowlist = ["localhost", "127.0.0.1"]
        self.StorageChip = NetworkChip()
        self.Kernel = None

    # Ініціалізація сервісу мережі з Kernel-посиланням
    def OnInit(self, KernelRef):
        self.Kernel = KernelRef
        self.Enabled = KernelRef.State.Get("config.network.enabled", True)
        self.RequireConfirmation = KernelRef.State.Get("config.network.require_confirmation", False)
        self.Allowlist = KernelRef.State.Get("config.network.allowlist", ["localhost", "127.0.0.1"])
        ODN.Emit("Network.Service", "INITIALIZED")

    # Запуск мережевого сервісу
    def OnStart(self):
        ODN.Emit("Network.Service", "SUBSPACE LINK READY. Security protocols active.")

    # Зупинка мережевого сервісу та відключення чіпу
    def OnStop(self):
        self.StorageChip.Disconnect()
        ODN.Emit("Network.Service", "SUBSPACE LINK TERMINATED")

    # Перевірка чи дозволений домен в allowlist
    def IsAllowed(self, Url: str) -> bool:
        Host = (urlparse(Url).hostname or "").lower()
        if not Host:
            return False
        if Host in ("localhost", "127.0.0.1"):
            return True
        for Domain in self.Allowlist:
            if Host == Domain or Host.endswith("." + Domain):
                return True
        return False

    # HTTP запит через subspace link з перевіркою безпеки
    def SubspaceRequest(self, Url: str, Timeout: int = 15) -> str:
        if not self.Enabled:
            return "\u25e7 SUBSPACE ERROR: NETWORK OFFLINE"
        if not self.IsAllowed(Url):
            self.LogRequest(Url, 403, False, "BLOCKED: Domain not in allowlist")
            return "\u25e7 SUBSPACE ERROR: PROTOCOL VOID (Domain Blocked)"

        # Zero-Except: без try/except, використовуємо умовні перевірки
        import requests
        Resp = requests.get(Url, timeout=Timeout)
        Status = Resp.status_code
        Success = Resp.ok
        Text = Resp.text[:2048]
        self.LogRequest(Url, Status, Success, "")
        if not Success:
            return f"\u25e7 SUBSPACE ERROR: HTTP {Status}"
        return f"\u25e7 SUBSPACE DOWNLINK SUCCESS [{Status}]: {Url}\n{Text}"

    # Логування мережевого запиту в ізолінійний чіп
    def LogRequest(self, Url: str, Status: int, Success: bool, Note: str = ""):
        # Перевірка з'єднання перед записом
        if not self.StorageChip.Connect():
            return

        Conn = self.StorageChip.Connection
        if Conn:
            ReqId = str(uuid.uuid4())
            Ts = time.strftime('%Y-%m-%dT%H:%M:%S')
            Conn.execute(
                "INSERT INTO network_logs (id, timestamp, url, status_code, success, note) VALUES (?, ?, ?, ?, ?, ?)",
                (ReqId, Ts, Url, Status, 1 if Success else 0, Note)
            )
            Conn.commit()
            ODN.Emit("Network.Service", f"REQUEST LOGGED: {Url[:30]}... | {Status}")

    # Встановлення статусу мережі (увімкнено/вимкнено)
    def SetEnabled(self, Status: bool):
        self.Enabled = Status
        ODN.Emit("Network.Status", {"enabled": Status})

    # Перевірка здоров'я мережевого сервісу
    def Health(self) -> bool:
        return self.Enabled and self.StorageChip.Connected

__all__ = ["NetworkService", "NetworkChip"]
