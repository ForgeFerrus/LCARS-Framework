# LCARS NETWORK MODULE
# Об'єднане ядро мережі: транспорт (TCP/HTTP), фаєрвол, клієнтські запити, async.

from __future__ import annotations
from typing import Any, Callable, Dict, List, Set
import re

from lcars.base.type import LCARS, SystemComponent
from lcars.base.info import getVersion
from lcars.service.bridge import Bridge


IP = re.compile(r"^[0-9a-fA-F:./\[\]]+$")
HEX = set("0123456789abcdefABCDEF")
IPV4 = set("0123456789.")

def IsValidIpPattern(Value: str) -> bool:
    if not Value:
        return False
    Clean = Value.strip()
    if Clean.startswith("["):
        Clean = Clean.lstrip("[").rstrip("]")
    if "/" in Clean:
        Base, Prefix = Clean.rsplit("/", 1)
        if not Prefix.isdigit():
            return False
        Clean = Base
    return bool(IP.match(Clean))


class FirewallRule(LCARS):
    def __init__(self, Action: str, Pattern: str):
        super().__init__()
        self.Action = str(Action).upper()
        self.Pattern = str(Pattern).strip()
        self.Network = None
        self.Port = None
        self.WildcardPort = False
        self.Parse()

    def Parse(self):
        Part = self.Pattern
        if ":" in Part and not Part.startswith("["):
            HostPart, PortPart = Part.rsplit(":", 1)
            if PortPart == "*":
                self.WildcardPort = True
                Part = HostPart
            elif PortPart.isdigit():
                self.Port = int(PortPart)
                Part = HostPart
        if Part:
            if IsValidIpPattern(Part):
                IpModule = LCARS.Import("ipaddress")
                if IpModule:
                    Result = getattr(IpModule, "ip_network", None)
                    if callable(Result):
                        self.Network = Result(Part, strict=False)

    def Match(self, Address: str, Port: int | None = None) -> bool:
        Host = str(Address or "").strip().lower()
        if not Host:
            return False
        if self.Port is not None and Port is not None and self.Port != Port:
            return False
        if self.Network is not None:
            IpModule = LCARS.Import("ipaddress")
            if IpModule:
                IpFn = getattr(IpModule, "ip_address", None)
                if callable(IpFn) and IsValidIpPattern(Host):
                    Addr = IpFn(Host)
                    if Addr in self.Network:
                        return True
        HostClean = Host
        if Host.startswith("["):
            HostClean = Host.split("]")[0].lstrip("[")
        elif Host.count(":") > 1:
            pass
        else:
            HostClean = Host.split(":", 1)[0] if ":" in Host else Host
        PatternClean = self.Pattern
        if ":" in PatternClean and not PatternClean.startswith("["):
            PatternClean = PatternClean.rsplit(":", 1)[0]
        elif PatternClean.startswith("["):
            PatternClean = PatternClean.split("]")[0].lstrip("[")
        PatternLower = PatternClean.lower()
        return HostClean == PatternLower or HostClean.endswith("." + PatternLower)

    def ToDict(self) -> dict:
        PortVal = "*" if self.WildcardPort else self.Port
        return {"Action": self.Action, "Pattern": self.Pattern, "Port": PortVal}


class FirewallPolicy(SystemComponent):
    def __init__(self, SystemId: str = "ServerFirewall"):
        super().__init__(SystemId=SystemId)
        self.Enabled = True
        self.AllowLocal = True
        self.Allowlist: Set[str] = set()
        self.Denylist: Set[str] = set()
        self.Rules: List[FirewallRule] = []
        self.MaxConnections = 64
        self.ConnectionCount = 0
        LockFn = Bridge.Load("System.Thread.Lock")
        self.Lock = LockFn() if callable(LockFn) else None

    def Acquire(self):
        if self.Lock:
            AcquireFn = getattr(self.Lock, "acquire", None)
            if callable(AcquireFn):
                AcquireFn()

    def Release(self):
        if self.Lock:
            ReleaseFn = getattr(self.Lock, "release", None)
            if callable(ReleaseFn):
                ReleaseFn()

    def AddRule(self, Action: str, Pattern: str) -> bool:
        CleanPattern = str(Pattern).strip()
        if not CleanPattern:
            return False
        if Action not in ("ALLOW", "DENY"):
            return False
        self.Acquire()
        self.Rules.append(FirewallRule(Action, CleanPattern))
        self.Release()
        return True

    def RemoveRule(self, Pattern: str) -> bool:
        CleanPattern = str(Pattern).strip()
        self.Acquire()
        Before = len(self.Rules)
        self.Rules = [R for R in self.Rules if R.Pattern != CleanPattern]
        Removed = len(self.Rules) < Before
        self.Release()
        return Removed

    def Allow(self, Address: str) -> bool:
        Clean = str(Address).strip()
        if not Clean:
            return False
        self.Acquire()
        self.Allowlist.add(Clean)
        self.Release()
        return True

    def Deny(self, Address: str) -> bool:
        Clean = str(Address).strip()
        if not Clean:
            return False
        self.Acquire()
        self.Denylist.add(Clean)
        self.Release()
        return True

    def RemoveAllow(self, Address: str) -> bool:
        Clean = str(Address).strip()
        self.Acquire()
        Found = Clean in self.Allowlist
        if Found:
            self.Allowlist.remove(Clean)
        self.Release()
        return Found

    def RemoveDeny(self, Address: str) -> bool:
        Clean = str(Address).strip()
        self.Acquire()
        Found = Clean in self.Denylist
        if Found:
            self.Denylist.remove(Clean)
        self.Release()
        return Found

    def ValidateAddress(self, Address: str) -> bool:
        Clean = str(Address).strip()
        if not Clean:
            return False
        if IsValidIpPattern(Clean):
            IpModule = LCARS.Import("ipaddress")
            if IpModule:
                IpFn = getattr(IpModule, "ip_address", None)
                if callable(IpFn):
                    if IsValidIpPattern(Clean):
                        IpFn(Clean)
                        return True
        if "." in Clean or ":" in Clean:
            return len(Clean) > 0 and all(C.isalnum() or C in ".-:" for C in Clean)
        return False

    def ParseHost(self, Address: str) -> str:
        Host = str(Address or "").strip()
        if Host.startswith("["):
            return Host.split("]")[0].lstrip("[")
        if Host.count(":") == 1:
            return Host.split(":")[0]
        if Host.count(":") > 1:
            return Host
        return Host

    def IsAllowed(self, Address: str, Port: int | None = None) -> bool:
        HostBase = self.ParseHost(Address)
        if not self.Enabled:
            return True
        for Rule in self.Rules:
            if Rule.Match(Address, Port):
                return Rule.Action == "ALLOW"
        if HostBase in self.Denylist:
            return False
        if self.AllowLocal and HostBase in ("127.0.0.1", "::1", "localhost"):
            return True
        if self.Allowlist:
            return HostBase in self.Allowlist
        return True

    def IncrementConnections(self) -> bool:
        self.Acquire()
        if self.ConnectionCount >= self.MaxConnections:
            self.Release()
            return False
        self.ConnectionCount += 1
        self.Release()
        return True

    def DecrementConnections(self) -> None:
        self.Acquire()
        if self.ConnectionCount > 0:
            self.ConnectionCount -= 1
        self.Release()

    def GetStatus(self) -> dict:
        self.Acquire()
        Count = self.ConnectionCount
        self.Release()
        return {
            "Enabled": self.Enabled,
            "AllowLocal": self.AllowLocal,
            "Allowlist": sorted(self.Allowlist),
            "Denylist": sorted(self.Denylist),
            "Rules": [R.ToDict() for R in self.Rules],
            "MaxConnections": self.MaxConnections,
            "ConnectionCount": Count,
        }


class ServerSignature(LCARS):
    def __init__(self, Name: str, Host: str, Port: int, Protocol: str = "TCP"):
        super().__init__()
        self.Name = str(Name)
        self.Host = str(Host)
        self.Port = int(Port)
        self.Protocol = str(Protocol).upper()
        self.Version = "1.0"
        self.Identifier = f"{self.Protocol}://{self.Host}:{self.Port}/{self.Name}"

    def ToDict(self) -> dict:
        return {
            "Name": self.Name, "Host": self.Host, "Port": self.Port,
            "Protocol": self.Protocol, "Version": self.Version, "Identifier": self.Identifier,
        }


class Server(SystemComponent):
    def __init__(self, Name: str, Host: str = "127.0.0.1", Port: int = 0,
                 Protocol: str = "TCP", Firewall: FirewallPolicy | None = None):
        super().__init__(SystemId=f"Server.{Name}")
        self.Name = str(Name)
        self.Host = str(Host)
        self.Port = int(Port)
        self.Protocol = str(Protocol).upper()
        self.Signature = ServerSignature(self.Name, self.Host, self.Port, self.Protocol)
        self.Firewall = Firewall or FirewallPolicy()
        self.Socket = None
        self.Running = False
        self.SSLContext = None

    def Start(self) -> bool:
        self.Running = True
        return True

    def Stop(self) -> bool:
        self.Running = False
        return True

    def Health(self) -> bool:
        return self.Running

    def GetStatus(self) -> dict:
        return {
            "Name": self.Name, "Host": self.Host, "Port": self.Port,
            "Protocol": self.Protocol, "Running": self.Running,
            "Connections": self.Firewall.ConnectionCount,
            "SSL": self.SSLContext is not None,
            "Signature": self.Signature.ToDict(), "Firewall": self.Firewall.GetStatus(),
        }


class TcpServer(Server):
    def __init__(self, Name: str, Host: str = "127.0.0.1", Port: int = 0,
                 Firewall: FirewallPolicy | None = None,
                 Handler: Callable | None = None,
                 SSLContext=None, Backlog: int = 128):
        super().__init__(Name, Host, Port, "TCP", Firewall)
        self.Handler = Handler
        self.Thread = None
        self.Backlog = Backlog
        self.SSLContext = SSLContext

    def Start(self) -> bool:
        SocketType = Bridge.Load("System.Network.Socket")
        Family = Bridge.Load("System.Network.IPv4")
        Stream = Bridge.Load("System.Network.TCP")
        ThreadType = Bridge.Load("System.Thread")
        SocketModule = Bridge.Load("System.Network")
        if not callable(SocketType):
            return False
        if Family is None:
            return False
        if Stream is None:
            return False
        if not callable(ThreadType):
            return False
        if SocketModule is None:
            return False
        self.Socket = SocketType(Family, Stream)
        SolSock = getattr(SocketModule, "SOL_SOCKET", None)
        SoReuse = getattr(SocketModule, "SO_REUSEADDR", None)
        if SolSock is not None and SoReuse is not None:
            self.Socket.setsockopt(SolSock, SoReuse, 1)
        if self.SSLContext is not None:
            WrapFn = getattr(self.SSLContext, "wrap_socket", None)
            if callable(WrapFn):
                self.Socket = WrapFn(self.Socket, server_side=True)
        self.Socket.bind((self.Host, self.Port))
        self.Socket.listen(self.Backlog)
        self.Port = int(self.Socket.getsockname()[1])
        self.Signature = ServerSignature(self.Name, self.Host, self.Port, self.Protocol)
        self.Running = True
        self.Thread = ThreadType(target=self.Serve, daemon=True, name=f"LCARS-{self.Name}")
        self.Thread.start()
        return True

    def Serve(self) -> None:
        while self.Running:
            if not self.Running:
                break
            SelfSocket = self.Socket
            if SelfSocket is None:
                break
            SelfSocket.settimeout(1.0)
            AcceptResult = None
            AcceptFn = getattr(SelfSocket, "accept", None)
            if callable(AcceptFn):
                AcceptResult = AcceptFn()
            if AcceptResult is None:
                continue
            Connection, Address = AcceptResult
            AddressText = str(Address[0]) if isinstance(Address, tuple) else str(Address)
            AddressPort = int(Address[1]) if isinstance(Address, tuple) and len(Address) > 1 else None
            if not self.Firewall.IsAllowed(AddressText, AddressPort):
                CloseFn = getattr(Connection, "close", None)
                if callable(CloseFn):
                    CloseFn()
                continue
            if not self.Firewall.IncrementConnections():
                CloseFn = getattr(Connection, "close", None)
                if callable(CloseFn):
                    CloseFn()
                continue
            Worker = Bridge.Load("System.Thread")
            if callable(Worker):
                Worker(target=self.HandleConnection, args=(Connection, Address), daemon=True).start()
            else:
                self.HandleConnection(Connection, Address)

    def HandleConnection(self, Connection, Address) -> None:
        if callable(self.Handler):
            self.Handler(Connection, Address, self)
        else:
            CloseFn = getattr(Connection, "close", None)
            if callable(CloseFn):
                CloseFn()
        self.Firewall.DecrementConnections()

    def Stop(self) -> bool:
        self.Running = False
        if self.Socket:
            SocketType = Bridge.Load("System.Network.Socket")
            Family = Bridge.Load("System.Network.IPv4")
            Stream = Bridge.Load("System.Network.TCP")
            if callable(SocketType) and Family is not None and Stream is not None:
                Wake = SocketType(Family, Stream)
                Wake.settimeout(2.0)
                Wake.connect((self.Host, self.Port))
                Wake.close()
            CloseFn = getattr(self.Socket, "close", None)
            if callable(CloseFn):
                CloseFn()
        self.Socket = None
        return True


class HttpServer(TcpServer):
    ReasonPhrases = {
        200: "OK", 201: "Created", 204: "No Content",
        301: "Moved Permanently", 304: "Not Modified",
        400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
        404: "Not Found", 405: "Method Not Allowed", 413: "Payload Too Large",
        429: "Too Many Requests", 500: "Internal Server Error",
        502: "Bad Gateway", 503: "Service Unavailable",
    }

    def __init__(self, Name: str, Host: str = "127.0.0.1", Port: int = 0,
                 Firewall: FirewallPolicy | None = None,
                 Router: Callable | None = None,
                 SSLContext=None, Backlog: int = 128,
                 KeepAlive: bool = False):
        super().__init__(Name, Host, Port, Firewall, SSLContext=SSLContext, Backlog=Backlog)
        self.Protocol = "HTTP"
        self.Router = Router
        self.KeepAlive = KeepAlive
        self.Signature = ServerSignature(self.Name, self.Host, self.Port, self.Protocol)

    def HandleConnection(self, Connection, Address) -> None:
        Connection.settimeout(30.0)
        try:
            self.HandleRequestLoop(Connection, Address)
        finally:
            self.Firewall.DecrementConnections()

    def HandleRequestLoop(self, Connection, Address) -> None:
        KeepGoing = True
        while KeepGoing:
            RequestData = self.ReadRequest(Connection)
            if not RequestData:
                Response = self.MakeResponse(400, "text/plain", "BAD REQUEST")
                SendFn = getattr(Connection, "sendall", None)
                if callable(SendFn):
                    SendFn(Response)
                break
            Header, Body = (RequestData.split("\r\n\r\n", 1) + [""])[:2]
            Lines = Header.splitlines()
            if not Lines:
                Response = self.MakeResponse(400, "text/plain", "BAD REQUEST")
                SendFn = getattr(Connection, "sendall", None)
                if callable(SendFn):
                    SendFn(Response)
                break
            Parts = Lines[0].split(" ")
            Method = Parts[0] if Parts else "GET"
            Path = Parts[1] if len(Parts) > 1 else "/"
            ConnectionHeader = ""
            for Line in Lines[1:]:
                if Line.lower().startswith("connection:"):
                    ConnectionHeader = Line.split(":", 1)[1].strip().lower()
                    break
            if callable(self.Router):
                Response = self.Router(Method, Path, Body, self)
            else:
                Response = self.MakeResponse(404, "text/plain", "LCARS SERVER ROUTE NOT FOUND")
            if Response is None:
                Response = self.MakeResponse(500, "text/plain", "LCARS SERVER ROUTE RETURNED NONE")
            SendFn = getattr(Connection, "sendall", None)
            if callable(SendFn):
                SendFn(Response)
            if self.KeepAlive and ConnectionHeader != "close":
                KeepGoing = True
            else:
                KeepGoing = False
        CloseFn = getattr(Connection, "close", None)
        if callable(CloseFn):
            CloseFn()

    def ReadRequest(self, Connection) -> str:
        Chunks = []
        Total = 0
        MaxSize = 262144
        while Total < MaxSize:
            Chunk = None
            RecvFn = getattr(Connection, "recv", None)
            if callable(RecvFn):
                Chunk = RecvFn(min(65536, MaxSize - Total))
            if not Chunk:
                break
            Chunks.append(Chunk)
            Total += len(Chunk)
            Data = b"".join(Chunks).decode("utf-8", errors="replace")
            if "\r\n\r\n" in Data:
                HeaderPart = Data.split("\r\n\r\n", 1)[0]
                ContentLength = 0
                for Line in HeaderPart.splitlines():
                    if Line.lower().startswith("content-length:"):
                        CLStr = Line.split(":", 1)[1].strip()
                        if CLStr.isdigit():
                            ContentLength = int(CLStr)
                        break
                BodyReceived = len(Data) - len(HeaderPart) - 4
                while BodyReceived < ContentLength and Total < MaxSize:
                    Chunk = None
                    if callable(RecvFn):
                        Chunk = RecvFn(min(65536, ContentLength - BodyReceived))
                    if not Chunk:
                        break
                    Chunks.append(Chunk)
                    Total += len(Chunk)
                    BodyReceived += len(Chunk)
                break
        return b"".join(Chunks).decode("utf-8", errors="replace")

    def MakeResponse(self, Code: int, ContentType: str, Body: str,
                     ExtraHeaders: dict | None = None) -> bytes:
        Data = str(Body).encode("utf-8")
        Reason = self.ReasonPhrases.get(Code, "UNKNOWN")
        Headers = (
            f"HTTP/1.1 {Code} {Reason}\r\n"
            f"Content-Type: {ContentType}\r\n"
            f"Content-Length: {len(Data)}\r\n"
        )
        if self.KeepAlive:
            Headers += "Connection: keep-alive\r\n"
        else:
            Headers += "Connection: close\r\n"
        if ExtraHeaders:
            for Key, Val in ExtraHeaders.items():
                Headers += f"{Key}: {Val}\r\n"
        Headers += "\r\n"
        return Headers.encode("utf-8") + Data


class AsyncTcpServer(Server):
    def __init__(self, Name: str, Host: str = "127.0.0.1", Port: int = 0,
                 Firewall: FirewallPolicy | None = None,
                 Handler: Callable | None = None,
                 SSLContext=None, Backlog: int = 128):
        super().__init__(Name, Host, Port, "TCP", Firewall)
        self.Handler = Handler
        self.Thread = None
        self.Backlog = Backlog
        self.SSLContext = SSLContext
        self.Loop = None

    def Start(self) -> bool:
        AsyncioModule = LCARS.Import("asyncio")
        if AsyncioModule is None:
            return False
        NewLoopFn = getattr(AsyncioModule, "new_event_loop", None)
        if not callable(NewLoopFn):
            return False
        self.Loop = NewLoopFn()
        self.Running = True
        ThreadType = Bridge.Load("System.Thread")
        if callable(ThreadType):
            self.Thread = ThreadType(target=self.RunLoop, daemon=True, name=f"LCARS-Async-{self.Name}")
            self.Thread.start()
        return True

    def RunLoop(self):
        AsyncioModule = LCARS.Import("asyncio")
        if AsyncioModule:
            SetLoopFn = getattr(AsyncioModule, "set_event_loop", None)
            if callable(SetLoopFn):
                SetLoopFn(self.Loop)
            RunFn = getattr(self.Loop, "run_until_complete", None)
            if callable(RunFn):
                RunFn(self.AcceptLoop())
        self.Running = False

    async def AcceptLoop(self):
        AsyncioModule = LCARS.Import("asyncio")
        StartServerFn = getattr(AsyncioModule, "start_server", None)
        if not callable(StartServerFn):
            return
        Kwargs = {}
        if self.SSLContext is not None:
            Kwargs["ssl"] = self.SSLContext
        ServerObj = await StartServerFn(
            self.HandleClient, self.Host, self.Port, **Kwargs
        )
        Sockets = getattr(ServerObj, "sockets", [])
        if Sockets:
            self.Port = Sockets[0].getsockname()[1]
        self.Signature = ServerSignature(self.Name, self.Host, self.Port, self.Protocol)
        ServeForeverFn = getattr(ServerObj, "serve_forever", None)
        if callable(ServeForeverFn):
            await ServeForeverFn()

    async def HandleClient(self, Reader, Writer):
        ReadFn = getattr(Reader, "read", None)
        if callable(ReadFn):
            Data = await ReadFn(65536)
        else:
            Data = None
        if Data:
            Address = Writer.get_extra_info("peername")
            AddressText = str(Address[0]) if isinstance(Address, tuple) else str(Address)
            AddressPort = int(Address[1]) if isinstance(Address, tuple) and len(Address) > 1 else None
            if self.Firewall.IsAllowed(AddressText, AddressPort):
                if self.Firewall.IncrementConnections():
                    if callable(self.Handler):
                        AsyncioModule = LCARS.Import("asyncio")
                        IsCoroFn = getattr(AsyncioModule, "iscoroutinefunction", None)
                        if callable(IsCoroFn) and IsCoroFn(self.Handler):
                            await self.Handler(Reader, Writer, self)
                        else:
                            self.Handler(Reader, Writer, self)
                    self.Firewall.DecrementConnections()
        CloseFn = getattr(Writer, "close", None)
        if callable(CloseFn):
            CloseFn()
        WaitClosedFn = getattr(Writer, "wait_closed", None)
        if callable(WaitClosedFn):
            await WaitClosedFn()

    def Stop(self) -> bool:
        self.Running = False
        if self.Loop:
            IsRunningFn = getattr(self.Loop, "is_running", None)
            if callable(IsRunningFn) and IsRunningFn():
                AsyncioModule = LCARS.Import("asyncio")
                if AsyncioModule:
                    RunCoroFn = getattr(AsyncioModule, "run_coroutine_threadsafe", None)
                    if callable(RunCoroFn):
                        RunCoroFn(self.AsyncStop(), self.Loop)
        return True

    async def AsyncStop(self):
        AsyncioModule = LCARS.Import("asyncio")
        if AsyncioModule:
            AllTasksFn = getattr(AsyncioModule, "all_tasks", None)
            CurrentTaskFn = getattr(AsyncioModule, "current_task", None)
            if callable(AllTasksFn) and callable(CurrentTaskFn):
                CurrentTask = CurrentTaskFn(self.Loop)
                for Task in AllTasksFn(self.Loop):
                    if Task is not CurrentTask:
                        CancelFn = getattr(Task, "cancel", None)
                        if callable(CancelFn):
                            CancelFn()
        StopFn = getattr(self.Loop, "stop", None)
        if callable(StopFn):
            StopFn()


class AsyncHttpServer(AsyncTcpServer):
    ReasonPhrases = HttpServer.ReasonPhrases

    def __init__(self, Name: str, Host: str = "127.0.0.1", Port: int = 0,
                 Firewall: FirewallPolicy | None = None,
                 Router: Callable | None = None,
                 SSLContext=None, Backlog: int = 128):
        super().__init__(Name, Host, Port, Firewall, SSLContext=SSLContext, Backlog=Backlog)
        self.Protocol = "HTTP"
        self.Router = Router
        self.Signature = ServerSignature(self.Name, self.Host, self.Port, self.Protocol)

    async def HandleClient(self, Reader, Writer):
        AsyncioModule = LCARS.Import("asyncio")
        WaitFn = getattr(AsyncioModule, "wait_for", None)
        ReadFn = getattr(Reader, "read", None)
        if not callable(WaitFn) or not callable(ReadFn):
            return
        try:
            Data = await WaitFn(ReadFn(262144), timeout=30.0)
        except Exception:
            Data = None
        if not Data:
            CloseFn = getattr(Writer, "close", None)
            if callable(CloseFn):
                CloseFn()
            WaitClosedFn = getattr(Writer, "wait_closed", None)
            if callable(WaitClosedFn):
                await WaitClosedFn()
            return
        RequestData = Data.decode("utf-8", errors="replace")
        Header, Body = (RequestData.split("\r\n\r\n", 1) + [""])[:2]
        Lines = Header.splitlines()
        if not Lines:
            CloseFn = getattr(Writer, "close", None)
            if callable(CloseFn):
                CloseFn()
            WaitClosedFn = getattr(Writer, "wait_closed", None)
            if callable(WaitClosedFn):
                await WaitClosedFn()
            return
        Parts = Lines[0].split(" ")
        Method = Parts[0] if Parts else "GET"
        Path = Parts[1] if len(Parts) > 1 else "/"
        if callable(self.Router):
            IsCoroFn = getattr(AsyncioModule, "iscoroutinefunction", None)
            if callable(IsCoroFn) and IsCoroFn(self.Router):
                Response = await self.Router(Method, Path, Body, self)
            else:
                Response = self.Router(Method, Path, Body, self)
        else:
            Response = self.MakeResponse(404, "text/plain", "LCARS SERVER ROUTE NOT FOUND")
        if Response is None:
            Response = self.MakeResponse(500, "text/plain", "LCARS SERVER ROUTE RETURNED NONE")
        WriteFn = getattr(Writer, "write", None)
        if callable(WriteFn):
            WriteFn(Response)
        DrainFn = getattr(Writer, "drain", None)
        if callable(DrainFn):
            await DrainFn()
        CloseFn = getattr(Writer, "close", None)
        if callable(CloseFn):
            CloseFn()
        WaitClosedFn = getattr(Writer, "wait_closed", None)
        if callable(WaitClosedFn):
            await WaitClosedFn()

    def MakeResponse(self, Code: int, ContentType: str, Body: str,
                     ExtraHeaders: dict | None = None) -> bytes:
        Data = str(Body).encode("utf-8")
        Reason = self.ReasonPhrases.get(Code, "UNKNOWN")
        Headers = (
            f"HTTP/1.1 {Code} {Reason}\r\n"
            f"Content-Type: {ContentType}\r\n"
            f"Content-Length: {len(Data)}\r\n"
            "Connection: close\r\n"
        )
        if ExtraHeaders:
            for Key, Val in ExtraHeaders.items():
                Headers += f"{Key}: {Val}\r\n"
        Headers += "\r\n"
        return Headers.encode("utf-8") + Data


class ServerRegistry(LCARS):
    def __init__(self):
        super().__init__()
        self.Servers: Dict[str, Server] = {}
        LockFn = Bridge.Load("System.Thread.Lock")
        self.Lock = LockFn() if callable(LockFn) else None

    def Acquire(self):
        if self.Lock:
            AcquireFn = getattr(self.Lock, "acquire", None)
            if callable(AcquireFn):
                AcquireFn()

    def Release(self):
        if self.Lock:
            ReleaseFn = getattr(self.Lock, "release", None)
            if callable(ReleaseFn):
                ReleaseFn()

    def Register(self, ServerObject: Server) -> Server:
        self.Acquire()
        self.Servers[ServerObject.Name] = ServerObject
        self.Release()
        return ServerObject

    def Unregister(self, Name: str) -> bool:
        self.Acquire()
        Found = Name in self.Servers
        if Found:
            del self.Servers[Name]
        self.Release()
        return Found

    def Get(self, Name: str) -> Server | None:
        self.Acquire()
        Result = self.Servers.get(str(Name))
        self.Release()
        return Result

    def StartAll(self) -> dict:
        self.Acquire()
        Items = list(self.Servers.items())
        self.Release()
        Result = {}
        for Name, ServerObject in Items:
            Result[Name] = ServerObject.Start()
        return Result

    def StopAll(self) -> dict:
        self.Acquire()
        Items = list(self.Servers.items())
        self.Release()
        Result = {}
        for Name, ServerObject in Items:
            Result[Name] = ServerObject.Stop()
        return Result

    def GetStatus(self) -> dict:
        self.Acquire()
        Items = list(self.Servers.items())
        self.Release()
        return {Name: ServerObject.GetStatus() for Name, ServerObject in Items}


class NetworkManager(SystemComponent):
    DefaultAllowlist: Set[str] = {
        "api.github.com",
        "api.groq.com",
        "api.mistral.ai",
        "api.experientiallabs.ai",
        "openrouter.ai",
        "api.telegram.org",
        "graph.facebook.com",
        "chatapi.viber.com",
        "api.open-meteo.com",
        "geocoding-api.open-meteo.com",
        "ip-api.com",
        "httpbin.org",
        "lcars.local",
        "starfleet.command",
    }

    def __init__(self):
        super().__init__()
        self.Enabled = True
        self.Allowlist: Set[str] = set(self.DefaultAllowlist)
        self.DefaultTimeout = 60
        self.MaxTimeout = 180
        self.MaxRetries = 2
        self.RetryDelay = 0.5
        self.SSLVerify = True
        self.SSLCertPath = None
        self.UseSession = True
        self.Subsystem = "network"
        self.Version = getVersion()
        self.Session = None

    def GetSession(self):
        if self.UseSession and self.Session is not None:
            return self.Session
        Requests = Bridge.Load("Bridge.Network.Requests")
        if Requests:
            SessionFn = getattr(Requests, "Session", None)
            if callable(SessionFn):
                self.Session = SessionFn()
                return self.Session
        return None

    def IsHostAllowed(self, Url: str) -> bool:
        UrlParse = getattr(LCARS.System.URL, "urlparse", None)
        if not callable(UrlParse):
            return False
        Parsed = UrlParse(Url)
        Host = str(getattr(Parsed, "hostname", "") or "").lower()
        if not Host:
            return False
        if Host in ("localhost", "127.0.0.1", "::1"):
            return True
        return any(Host == Domain or Host.endswith("." + Domain) for Domain in self.Allowlist)

    def AddToAllowlist(self, Domain: str) -> bool:
        CleanDomain = str(Domain or "").lower().strip()
        if not CleanDomain:
            return False
        self.Allowlist.add(CleanDomain)
        return True

    def RemoveFromAllowlist(self, Domain: str) -> bool:
        CleanDomain = str(Domain or "").lower().strip()
        if CleanDomain not in self.Allowlist:
            return False
        self.Allowlist.remove(CleanDomain)
        return True

    def GetAllowlist(self) -> List[str]:
        return sorted(list(self.Allowlist))

    def SetEnabled(self, Status: bool):
        self.Enabled = bool(Status)

    def IsEnabled(self) -> bool:
        return self.Enabled

    def CalculateBackoff(self, Attempt: int) -> float:
        return min(self.RetryDelay * (2 ** Attempt), 5.0)

    def ValidateUrl(self, Url: str) -> tuple[bool, str]:
        if not Url:
            return False, "URL_EMPTY"
        if not str(Url).startswith(("http://", "https://")):
            return False, "URL_INVALID_SCHEME"
        if not self.IsHostAllowed(Url):
            return False, "HOST_BLOCKED"
        if not self.Enabled:
            return False, "NETWORK_DISABLED"
        return True, "OK"

    def PerformRequest(self, RequestFn, Method: str, Url: str, Headers: dict,
                       Payload: Any, Timeout: int) -> dict:
        Response = RequestFn(
            Method, Url,
            headers=Headers, json=Payload,
            timeout=Timeout,
        )
        Status = int(getattr(Response, "status_code", 0) or 0)
        Success = bool(getattr(Response, "ok", False))
        Body = str(getattr(Response, "text", "") or "")
        ResponseHeaders = dict(getattr(Response, "headers", {}) or {})
        return {
            "Status": Status, "Success": Success, "Body": Body,
            "Headers": ResponseHeaders,
        }

    def PerformSessionRequest(self, Session, Method: str, Url: str, Headers: dict,
                              Payload: Any, Timeout: int, Verify: bool, Cert) -> dict:
        Response = Session.request(
            Method, Url,
            headers=Headers, json=Payload,
            timeout=Timeout, verify=Verify, cert=Cert,
        )
        Status = int(getattr(Response, "status_code", 0) or 0)
        Success = bool(getattr(Response, "ok", False))
        Body = str(getattr(Response, "text", "") or "")
        ResponseHeaders = dict(getattr(Response, "headers", {}) or {})
        return {
            "Status": Status, "Success": Success, "Body": Body,
            "Headers": ResponseHeaders,
        }

    def Request(self, Url: str, Method: str = "GET", Headers: dict | None = None,
                Payload: Any = None, Timeout: int = 60) -> dict:
        Valid, Message = self.ValidateUrl(Url)
        if not Valid:
            return {"Status": 403 if Message == "HOST_BLOCKED" else 0, "Success": False, "Body": Message}

        Requests = Bridge.Load("Bridge.Network.Requests")
        RequestFn = getattr(Requests, "request", None) if Requests else None
        if not callable(RequestFn):
            return {"Status": 0, "Success": False, "Body": "HTTP ENGINE UNAVAILABLE"}

        SafeTimeout = max(1, min(int(Timeout or self.DefaultTimeout), self.MaxTimeout))
        RequestHeaders = dict(Headers or {})
        RequestHeaders.setdefault("User-Agent", "LCARS-Titanium/4.0")
        LastResult = {"Status": 0, "Success": False, "Body": "HTTP REQUEST FAILED", "Headers": {}}

        for Attempt in range(self.MaxRetries + 1):
            Session = self.GetSession()
            if Session and hasattr(Session, "request"):
                LastResult = self.PerformSessionRequest(
                    Session, str(Method or "GET").upper(), Url,
                    RequestHeaders, Payload, SafeTimeout, self.SSLVerify, self.SSLCertPath,
                )
            else:
                LastResult = self.PerformRequest(
                    RequestFn, str(Method or "GET").upper(), Url,
                    RequestHeaders, Payload, SafeTimeout,
                )
            LastResult["Attempts"] = Attempt + 1
            Status = LastResult.get("Status", 0)
            Success = LastResult.get("Success", False)
            if Success or Status < 500:
                return LastResult
            if Attempt < self.MaxRetries:
                TimeModule = LCARS.Import("time")
                SleepFn = getattr(TimeModule, "sleep", None) if TimeModule else None
                if callable(SleepFn):
                    SleepFn(self.CalculateBackoff(Attempt))
        return LastResult

    def Ping(self, Url: str) -> bool:
        return bool(self.Request(Url, "HEAD").get("Success"))

    def FetchUrl(self, Url: str) -> tuple[bool, str]:
        Result = self.Request(Url, "GET")
        return bool(Result.get("Success")), str(Result.get("Body", ""))

    def RequestJson(self, Url: str, Method: str = "GET", Headers: dict | None = None,
                    Payload: Any = None, Timeout: int = 60) -> tuple[bool, Any]:
        Result = self.Request(Url, Method, Headers, Payload, Timeout)
        if not Result.get("Success"):
            return False, Result
        JsonModule = getattr(LCARS.System, "Json", None)
        if not JsonModule:
            JsonModule = LCARS.Import("json")
        LoadsFn = getattr(JsonModule, "loads", None) if JsonModule else None
        if not callable(LoadsFn):
            return False, {"Status": 0, "Success": False, "Body": "JSON ENGINE UNAVAILABLE"}
        return True, LoadsFn(Result.get("Body", ""))

    def GetConfig(self) -> Dict[str, Any]:
        return {
            "enabled": self.Enabled,
            "allowlist": self.GetAllowlist(),
            "default_timeout": self.DefaultTimeout,
            "max_timeout": self.MaxTimeout,
            "max_retries": self.MaxRetries,
            "retry_delay": self.RetryDelay,
            "ssl_verify": self.SSLVerify,
            "use_session": self.UseSession,
        }

    def GetStatus(self) -> Dict[str, Any]:
        return {
            "Name": self.Subsystem, "Enabled": self.Enabled,
            "AllowlistCount": len(self.Allowlist),
            "DefaultTimeout": self.DefaultTimeout, "MaxTimeout": self.MaxTimeout,
            "MaxRetries": self.MaxRetries, "SSLVerify": self.SSLVerify,
            "SessionActive": self.Session is not None,
        }

    def Health(self) -> bool:
        return self.Enabled

    def LoadConfig(self, Config: Dict[str, Any]):
        self.Enabled = bool(Config.get("enabled", True))
        self.DefaultTimeout = int(Config.get("default_timeout", self.DefaultTimeout))
        self.MaxTimeout = int(Config.get("max_timeout", self.MaxTimeout))
        self.MaxRetries = max(0, int(Config.get("max_retries", self.MaxRetries)))
        self.RetryDelay = max(0.0, float(Config.get("retry_delay", self.RetryDelay)))
        self.SSLVerify = bool(Config.get("ssl_verify", True))
        self.UseSession = bool(Config.get("use_session", True))
        AllowlistData = Config.get("allowlist", [])
        if AllowlistData is not None:
            self.Allowlist = set(AllowlistData) if AllowlistData else set(self.DefaultAllowlist)


class Async(NetworkManager):
    def __init__(self):
        super().__init__()
        self.AsyncClient = None

    async def GetAsyncClient(self):
        if self.AsyncClient is not None:
            IsClosedFn = getattr(self.AsyncClient, "is_closed", None)
            IsClosed = IsClosedFn() if callable(IsClosedFn) else False
            if not IsClosed:
                return self.AsyncClient
        HttpxModule = LCARS.Import("httpx")
        if HttpxModule:
            ClientFn = getattr(HttpxModule, "AsyncClient", None)
            if callable(ClientFn):
                self.AsyncClient = await ClientFn(verify=self.SSLVerify)
                return self.AsyncClient
        return None

    async def AsyncRequest(self, Url: str, Method: str = "GET", Headers: dict | None = None,
                           Payload: Any = None, Timeout: int = 60) -> dict:
        Valid, Message = self.ValidateUrl(Url)
        if not Valid:
            return {"Status": 403 if Message == "HOST_BLOCKED" else 0, "Success": False, "Body": Message}
        Client = await self.GetAsyncClient()
        if Client is None:
            return {"Status": 0, "Success": False, "Body": "ASYNC ENGINE UNAVAILABLE"}
        SafeTimeout = max(1, min(int(Timeout or self.DefaultTimeout), self.MaxTimeout))
        RequestHeaders = dict(Headers or {})
        RequestHeaders.setdefault("User-Agent", "LCARS-Titanium/4.0")
        LastResult = {"Status": 0, "Success": False, "Body": "HTTP REQUEST FAILED", "Headers": {}}
        ClientRequestFn = getattr(Client, "request", None)
        for Attempt in range(self.MaxRetries + 1):
            if callable(ClientRequestFn):
                Response = await ClientRequestFn(
                    str(Method or "GET").upper(), Url,
                    headers=RequestHeaders, json=Payload, timeout=SafeTimeout,
                )
                Status = int(getattr(Response, "status_code", 0) or 0)
                Success = 200 <= Status < 400
                Body = str(getattr(Response, "text", "") or "")
                ResponseHeaders = dict(getattr(Response, "headers", {}) or {})
                LastResult = {
                    "Status": Status, "Success": Success, "Body": Body,
                    "Headers": ResponseHeaders, "Attempts": Attempt + 1,
                }
                if Success or Status < 500:
                    return LastResult
            if Attempt < self.MaxRetries:
                AsyncioModule = LCARS.Import("asyncio")
                SleepFn = getattr(AsyncioModule, "sleep", None) if AsyncioModule else None
                if callable(SleepFn):
                    await SleepFn(self.CalculateBackoff(Attempt))
        return LastResult

    async def AsyncFetchUrl(self, Url: str) -> tuple[bool, str]:
        Result = await self.AsyncRequest(Url, "GET")
        return bool(Result.get("Success")), str(Result.get("Body", ""))

    async def AsyncRequestJson(self, Url: str, Method: str = "GET", Headers: dict | None = None,
                               Payload: Any = None, Timeout: int = 60) -> tuple[bool, Any]:
        Result = await self.AsyncRequest(Url, Method, Headers, Payload, Timeout)
        if not Result.get("Success"):
            return False, Result
        JsonModule = LCARS.Import("json")
        if not JsonModule:
            JsonModule = getattr(LCARS.System, "Json", None)
        LoadsFn = getattr(JsonModule, "loads", None) if JsonModule else None
        if not callable(LoadsFn):
            return False, {"Status": 0, "Success": False, "Body": "JSON ENGINE UNAVAILABLE"}
        return True, LoadsFn(Result.get("Body", ""))

    async def Close(self):
        if self.AsyncClient:
            CloseFn = getattr(self.AsyncClient, "aclose", None)
            if callable(CloseFn):
                await CloseFn()
        self.AsyncClient = None

Net = NetworkManager
AsyncNet = Async

__all__ = [
    "FirewallRule", "FirewallPolicy",
    "ServerSignature", "Server", "TcpServer", "HttpServer",
    "AsyncTcpServer", "AsyncHttpServer",
    "ServerRegistry",
    "NetworkManager", "AsyncNetworkManager",
    "Net", "AsyncNet",
]
