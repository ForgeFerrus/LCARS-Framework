# ◤ TITANIUM NETWORK SERVICE // TITANIUM OS ARCHITECTURE 🖖
# =============================================================================
# ФАЙЛ: lcars/service/network.py
# ОПИС: Централізоване керування мережевими операціями, зв'язком підпростору (Subspace Link)
#       та протоколами безпеки зорельота. Зберігає мережеві логи та список дозволених
#       доменів в ізолінійному чіпі ISO-NET.
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure LCARS Classes).
# =============================================================================
from __future__ import annotations
import threading
from typing import Set
from lcars.base.type import LCARS
from lcars.core.conduit import Service
from lcars.engineering.isolinear import IsolinearChip
from lcars.core.signal import ODN
from lcars.modules.storage import ResolveChipPath
from lcars.modules.net import NetworkManager, ServerRegistry, Server

# Сховище стану мережі та журналів (ISO-NET)
class NetworkStorage(IsolinearChip):
    def __init__(self):
        PathRef = ResolveChipPath("Network Operations Chip")
        StemStr = str(getattr(PathRef, "stem", PathRef))
        Parts = StemStr.split("-", 2)
        ChipId = Parts[0] + "-" + (Parts[1] if len(Parts) > 1 else "0000")
        super().__init__(Id=ChipId, Array=ChipId.split("-", 1)[0], Metadata={}, FilePath=PathRef)
        self.InitializeSchema()

    # Ініціалізація SQL-схеми для мережевих логів та allowlist
    def InitializeSchema(self) -> None:
        if not self.Connect():
            return
        Conn = self.Connection
        if Conn:
            Cursor = Conn.cursor()
            Cursor.executescript(
                "CREATE TABLE IF NOT EXISTS network_logs ("
                "id TEXT PRIMARY KEY, timestamp TEXT, url TEXT, "
                "status_code INTEGER, success INTEGER, note TEXT);"
                "CREATE TABLE IF NOT EXISTS allowlist ("
                "domain TEXT PRIMARY KEY, added_at TEXT);"
            )
            Conn.commit()

# Сервіс мережевих операцій та безпеки
class NetworkSubsystem(Service):
    Name = "network"
    InstanceRef = None

    def __init__(self, NetworkModule: NetworkManager | None = None):
        if NetworkSubsystem.InstanceRef is not None:
            raise RuntimeError("Use NetworkSubsystem.GetInstance()")
        super().__init__(Id="NetworkSubsystem")
        NetworkSubsystem.InstanceRef = self
        self.Module = NetworkModule or NetworkManager()
        self.StorageChip = NetworkStorage()
        self.ServerRegistry = ServerRegistry()
        self.DefaultTimeout = self.Module.DefaultTimeout
        self.MaxTimeout = self.Module.MaxTimeout
        self.Enabled = self.Module.Enabled
        self.GatewayHost = "127.0.0.1"
        self.GatewayPort = 3688
        self.GatewayServer = None
        self.GatewayThread = None
        self.GatewayStartedAt = None
        self.GatewayAudit = []
        self.AuditLock = threading.Lock()
        self.GatewayMaxBodyBytes = 262144
        self.GatewayRoutes = {"/health", "/generate", "/v1/chat/completions"}
        self.LoadAllowlist()

        RuntimeModule = LCARS.Import("lcars.system.environment").Runtime
        if RuntimeModule:
            self.GatewayHost = str(RuntimeModule.get("GATEWAY_HOST", "127.0.0.1"))
            RawPort = str(RuntimeModule.get("GATEWAY_PORT", "3688"))
            if RawPort.isdigit():
                self.GatewayPort = int(RawPort)

    InstanceLock = threading.Lock()

    @classmethod
    def GetInstance(cls):
        if cls.InstanceRef is not None and cls.InstanceRef.Running:
            return cls.InstanceRef
        with cls.InstanceLock:
            if cls.InstanceRef is not None and cls.InstanceRef.Running:
                return cls.InstanceRef
            cls.InstanceRef = None
            cls.InstanceRef = NetworkSubsystem()
            return cls.InstanceRef

    @property
    def Allowlist(self):
        return self.Module.Allowlist

    # Завантаження списку дозволених доменів з чіпа
    def LoadAllowlist(self) -> None:
        if not self.StorageChip.Connect():
            return
        Conn = self.StorageChip.Connection
        if Conn:
            Cursor = Conn.cursor()
            Cursor.execute("SELECT domain FROM allowlist")
            Rows = Cursor.fetchall()
            self.Module.Allowlist.update(Row[0] for Row in Rows)
        MissingDomains = self.Module.DefaultAllowlist.difference(self.Allowlist)
        if MissingDomains:
            self.Allowlist.update(MissingDomains)
            self.SaveAllowlist()

    # Збереження списку дозволених доменів на чіп
    def SaveAllowlist(self) -> None:
        if not self.StorageChip.Connect():
            return
        Conn = self.StorageChip.Connection
        if Conn:
            Cursor = Conn.cursor()
            DateTime = getattr(LCARS.System, "DateTime", None)
            NowStr = DateTime.now().isoformat() if DateTime and hasattr(DateTime, "now") else ""
            for Domain in self.Allowlist:
                Cursor.execute("INSERT OR IGNORE INTO allowlist (domain, added_at) VALUES (?, ?)", (Domain, NowStr))
            Conn.commit()

    # Додавання домену до списку дозволених
    def AddToAllowlist(self, Domain: str) -> None:
        self.Module.AddToAllowlist(Domain)
        self.SaveAllowlist()
        ODN.Transmit("Network.Allowlist", f"DOMAIN ADDED: {Domain}")

    # Видалення домену зі списку дозволених
    def RemoveFromAllowlist(self, Domain: str) -> bool:
        Result = self.Module.RemoveFromAllowlist(Domain)
        if Result:
            self.SaveAllowlist()
            ODN.Transmit("Network.Allowlist", f"DOMAIN REMOVED: {Domain}")
        return Result

    # Перевірка чи дозволено домен
    def IsAllowed(self, Url: str) -> bool:
        return self.Module.IsHostAllowed(Url)

    def Request(self, Url: str, Method: str = "GET", Headers: dict | None = None,
                Payload: any = None, Timeout: int = 60) -> dict:
        Result = self.Module.Request(Url, Method, Headers, Payload, Timeout)
        Status = int(Result.get("Status", 0) or 0)
        Success = bool(Result.get("Success"))
        self.LogRequest(Url, Status, Success, "")
        Result["Url"] = Url
        Result["Method"] = str(Method or "GET").upper()
        return Result

    def OnNetworkRequest(self, Packet) -> dict:
        Data = getattr(Packet, "Data", None)
        RequestData = Data if isinstance(Data, dict) else {}
        return self.Request(
            RequestData.get("Url", ""),
            RequestData.get("Method", "GET"),
            RequestData.get("Headers", {}),
            RequestData.get("Payload"),
            RequestData.get("Timeout", self.DefaultTimeout),
        )

    def OnStart(self):
        super().OnStart()
        ODN.Connect("Network.Request", self.OnNetworkRequest)
        ODN.Transmit("Network.Ready", Status="ONLINE")
        ODN.Transmit("Server.Ready", Status="ONLINE", Servers=self.ServerRegistry.GetStatus())

    def OnStop(self):
        self.StopGateway()
        self.ServerRegistry.StopAll()
        ODN.Disconnect("Network.Request", self.OnNetworkRequest)
        ODN.Transmit("Server.Stopped", Status="OFFLINE")
        super().OnStop()

    # ── Server Management (from ServerSubsystem) ──────────────────────────

    def RegisterServer(self, ServerObject: Server) -> Server:
        return self.ServerRegistry.Register(ServerObject)

    def UnregisterServer(self, Name: str) -> bool:
        return self.ServerRegistry.Unregister(Name)

    def StartServer(self, Name: str) -> bool:
        ServerObject = self.ServerRegistry.Get(Name)
        return bool(ServerObject and ServerObject.Start())

    def StopServer(self, Name: str) -> bool:
        ServerObject = self.ServerRegistry.Get(Name)
        return bool(ServerObject and ServerObject.Stop())

    def GetServerStatus(self) -> dict:
        return self.ServerRegistry.GetStatus()

    def ServersHealth(self) -> bool:
        return all(
            ServerObject.Health() or not ServerObject.Running
            for ServerObject in self.ServerRegistry.Servers.values()
        )

    def IsLoopbackHost(self, Host: str) -> bool:
        return str(Host).strip().lower() in ("127.0.0.1", "localhost", "::1")

    def IsGatewayClientAllowed(self, Address: str) -> bool:
        return self.IsLoopbackHost(Address)

    def RecordGatewayAudit(self, Method: str, Path: str, Status: int, Client: str) -> None:
        with self.AuditLock:
            DateTimeModule = LCARS.Import("datetime")
            DateTimeClass = getattr(DateTimeModule, "datetime", None) if DateTimeModule else None
            NowStr = DateTimeClass.now().isoformat(timespec="seconds") if DateTimeClass and hasattr(DateTimeClass, "now") else ""
            self.GatewayAudit.append({
                "Time": NowStr,
                "Method": str(Method), "Path": str(Path),
                "Status": int(Status), "Client": str(Client),
            })
            if len(self.GatewayAudit) > 128:
                self.GatewayAudit = self.GatewayAudit[-128:]

    def GetFirewallStatus(self) -> dict:
        return {
            "Outbound": "ALLOWLIST", "Inbound": "LOOPBACK_ONLY",
            "GatewayHost": self.GatewayHost, "GatewayPort": self.GatewayPort,
            "Routes": sorted(self.GatewayRoutes),
            "MaxBodyBytes": self.GatewayMaxBodyBytes,
            "AllowlistCount": len(self.Allowlist),
        }

    def IsGatewayActive(self) -> bool:
        return bool(self.GatewayServer and self.GatewayServer.Running)

    def GetGatewayStatus(self) -> dict:
        return {
            "Active": self.IsGatewayActive(), "Host": self.GatewayHost,
            "Port": self.GatewayPort, "Firewall": self.GetFirewallStatus(),
            "AuditEvents": len(self.GatewayAudit),
        }

    def BuildGatewayFirewall(self):
        from lcars.modules.net import FirewallPolicy
        Firewall = FirewallPolicy(SystemId="GatewayFirewall")
        Firewall.AllowLocal = True
        Firewall.Allow("127.0.0.1")
        Firewall.Allow("::1")
        Firewall.Allow("localhost")
        return Firewall

    def RouteGatewayRequest(self, Method: str, Path: str, Body: str, ServerObject):
        JsonModule = LCARS.Import("json")
        CleanMethod = str(Method).upper()
        if CleanMethod == "GET" and Path == "/health":
            self.RecordGatewayAudit(CleanMethod, Path, 200, "loopback")
            return ServerObject.MakeResponse(200, "application/json; charset=utf-8",
                JsonModule.dumps({"status": "ONLINE", "gateway": self.GetGatewayStatus()}, ensure_ascii=False))
        if CleanMethod != "POST" or Path not in self.GatewayRoutes or Path == "/health":
            self.RecordGatewayAudit(CleanMethod, Path, 404, "loopback")
            return ServerObject.MakeResponse(404, "application/json; charset=utf-8",
                JsonModule.dumps({"error": "GATEWAY_ROUTE_NOT_FOUND"}))
        BodyBytes = Body.encode("utf-8")
        if len(BodyBytes) < 1 or len(BodyBytes) > self.GatewayMaxBodyBytes:
            self.RecordGatewayAudit(CleanMethod, Path, 413, "loopback")
            return ServerObject.MakeResponse(413, "application/json; charset=utf-8",
                JsonModule.dumps({"error": "GATEWAY_BODY_REJECTED"}))
        if not Body.startswith("{") and not Body.startswith("["):
            self.RecordGatewayAudit(CleanMethod, Path, 400, "loopback")
            return ServerObject.MakeResponse(400, "application/json; charset=utf-8",
                JsonModule.dumps({"error": "INVALID_JSON"}))
        Payload = JsonModule.loads(Body)
        Messages = Payload.get("messages", []) if isinstance(Payload, dict) else []
        Reply = self.GenerateLocal(Messages)
        self.RecordGatewayAudit(CleanMethod, Path, 200, "loopback")
        if Path == "/v1/chat/completions":
            Model = str(Payload.get("model", "lcars-local")) if isinstance(Payload, dict) else "lcars-local"
            Response = {"object": "chat.completion", "model": Model,
                "choices": [{"index": 0, "message": {"role": "assistant", "content": Reply}, "finish_reason": "stop"}]}
            return ServerObject.MakeResponse(200, "application/json; charset=utf-8",
                JsonModule.dumps(Response, ensure_ascii=False))
        return ServerObject.MakeResponse(200, "application/json; charset=utf-8",
            JsonModule.dumps({"result": Reply}, ensure_ascii=False))

    def StartGateway(self) -> bool:
        if self.IsGatewayActive():
            return True
        if not self.IsLoopbackHost(self.GatewayHost):
            return False
        from lcars.modules.net import HttpServer
        TimeModule = LCARS.Import("time")
        self.GatewayServer = HttpServer(
            Name="LCARSLocalGateway", Host=self.GatewayHost, Port=self.GatewayPort,
            Firewall=self.BuildGatewayFirewall(), Router=self.RouteGatewayRequest,
        )
        if not self.GatewayServer.Start():
            self.GatewayServer = None
            return False
        self.GatewayPort = self.GatewayServer.Port
        self.GatewayStartedAt = TimeModule.time()
        ODN.Transmit("Network.Gateway", {"Status": "ONLINE", "Host": self.GatewayHost, "Port": self.GatewayPort})
        return True

    def StopGateway(self) -> bool:
        if self.GatewayServer:
            self.GatewayServer.Stop()
        self.GatewayServer = None
        self.GatewayThread = None
        self.GatewayStartedAt = None
        ODN.Transmit("Network.Gateway", {"Status": "OFFLINE"})
        return True

    def GenerateLocal(self, Messages: list) -> str:
        ProviderModule = LCARS.Import("lcars.service.provider")
        if not ProviderModule:
            return "[LCARS LOCAL GATEWAY: provider module unavailable]"
        LocalBackendFn = getattr(ProviderModule, "LocalLLM", None)
        if not callable(LocalBackendFn):
            return "[LCARS LOCAL GATEWAY: LocalLLM class not found]"
        LocalBackend = LocalBackendFn()
        CheckFn = getattr(LocalBackend, "CheckAvailable", None)
        if not callable(CheckFn) or not CheckFn():
            return "[LCARS LOCAL GATEWAY: local model is unavailable]"
        ChatFn = getattr(LocalBackend, "Chat", None)
        if not callable(ChatFn):
            return "[LCARS LOCAL GATEWAY: Chat method not found]"
        return str(ChatFn(Messages))

    # HTTP запит через subspace link з перевіркою безпеки
    def SubspaceRequest(self, Url: str, Timeout: int = 15) -> str:
        Result = self.Request(Url, "GET", Timeout=Timeout)
        if not Result.get("Success"):
            return f"◧ SUBSPACE ERROR: HTTP {Result.get('Status', 0)}"
        return f"◧ SUBSPACE DOWNLINK SUCCESS [{Result.get('Status', 0)}]: {Url}\n{str(Result.get('Body', ''))[:2048]}"

    # Логування мережевого запиту в ізолінійний чіп
    def LogRequest(self, Url: str, Status: int, Success: bool, Note: str = "") -> None:
        if not self.StorageChip.Connect():
            return
        Conn = self.StorageChip.Connection
        if Conn:
            Uuid = getattr(LCARS.System, "Uuid", None)
            DateTimeModule = LCARS.Import("datetime")
            DateTimeClass = getattr(DateTimeModule, "datetime", None) if DateTimeModule else None
            TimeModule = LCARS.System.Time
            ReqId = f"REQ-{int(TimeModule.time() * 1000000) if TimeModule and hasattr(TimeModule, 'time') else int(LCARS.System.Hash(str(Url + str(Status))))}"
            Ts = DateTimeClass.now().strftime("%Y-%m-%dT%H:%M:%S") if DateTimeClass and hasattr(DateTimeClass, "now") else ""
            Cursor = Conn.cursor()
            Cursor.execute(
                "INSERT OR REPLACE INTO network logs (id, timestamp, url, status_code, success, note) VALUES (?, ?, ?, ?, ?, ?)",
                (ReqId, Ts, Url, Status, 1 if Success else 0, Note)
            )
            Conn.commit()
            ODN.Transmit("Network.Service", f"REQUEST LOGGED: {Url[:30]}... | {Status}")

    # Встановлення статусу мережі (увімкнено/вимкнено)
    def SetEnabled(self, Status: bool) -> None:
        self.Module.SetEnabled(Status)
        self.Enabled = self.Module.Enabled
        ODN.Transmit("Network.Status", {"enabled": Status})

    # Перевірка здоров'я мережевого сервісу
    def Health(self) -> bool:
        return self.Module.IsEnabled() and self.StorageChip.Connected and self.ServersHealth()

    def GetStatus(self) -> dict:
        return {
            "Service": self.Name,
            "Running": self.Running,
            "Network": self.Module.GetStatus(),
            "Servers": self.ServerRegistry.GetStatus(),
            "Gateway": self.GetGatewayStatus(),
        }

# Alias for backward compatibility
ServerSubsystem = NetworkSubsystem

__all__ = ["NetworkSubsystem", "NetworkStorage", "ServerSubsystem"]
