# ◤ LCARS SUBSPACE VOICE COMMUNICATOR & ANDROID GATEWAY
# Бездротовий голосовий шлюз для зв'язку смартфона (Android Combadge) з бортовим комп'ютером.
# СТАНДАРТ: Titanium (Zero-Except, Zero Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.core.conduit import Service
from lcars.core.computer import BoardComputer
from lcars.engineering.telemetry import EmitTelemetry
from lcars.service.bridge import Bridge


class GatewayChannel(LCARS):
    def __init__(self, Gateway):
        super().__init__()
        self.Gateway = Gateway

    def Serve(self):
        Socket = self.Gateway.Socket
        SocketModule = Bridge.Load("System.Network")
        SelectModule = LCARS.Import("select")
        while self.Gateway.IsActive:
            Readable = SelectModule.select([Socket], [], [], 1.0) if SelectModule and hasattr(SelectModule, "select") else ([Socket], [], [])
            if not Readable[0]:
                continue
            AcceptResult = Socket.accept()
            if not AcceptResult:
                continue
            Connection, Address = AcceptResult
            if Connection is None:
                continue
            ThreadType = Bridge.Load("System.Thread")
            if callable(ThreadType):
                ThreadType(target=self.Handle, args=(Connection, Address), daemon=True).start()
            else:
                self.Handle(Connection, Address)

    def Handle(self, Connection, Address):
        Connection.settimeout(30.0)
        Data = self.ReadRequest(Connection)
        if not Data:
            Connection.sendall(self.Gateway.MakeResponse(400, "text/plain", "BAD REQUEST"))
            Connection.close()
            return
        Text = Data.decode("utf-8", errors="ignore")
        Header, Body = (Text.split("\r\n\r\n", 1) + [""])[:2]
        Parts = Header.splitlines()[0].split(" ") if Header else []
        Method = Parts[0] if Parts else "GET"
        Path = Parts[1] if len(Parts) > 1 else "/"
        Headers = {}
        for Line in Header.splitlines()[1:]:
            if ":" in Line:
                Key, Val = Line.split(":", 1)
                Headers[Key.strip().lower()] = Val.strip()
        ClientAddr = str(Address[0]) if isinstance(Address, tuple) else str(Address)
        if not self.Gateway.IsClientAllowed(ClientAddr):
            Connection.sendall(self.Gateway.MakeResponse(403, "application/json", '{"error":"FORBIDDEN"}'))
            Connection.close()
            return
        if self.Gateway.AuthToken and Method != "GET" and Path.startswith("/api/"):
            AuthHeader = Headers.get("authorization", "")
            if not AuthHeader.startswith("Bearer ") or AuthHeader[7:] != self.Gateway.AuthToken:
                Connection.sendall(self.Gateway.MakeResponse(401, "application/json", '{"error":"UNAUTHORIZED"}'))
                Connection.close()
                return
        if Method == "OPTIONS":
            Connection.sendall(self.Gateway.MakeCorsResponse())
            Connection.close()
            return
        Content = self.Gateway.Route(Method, Path, Body)
        Connection.sendall(Content)
        Connection.close()

    def ReadRequest(self, Connection) -> bytes:
        SocketModule = Bridge.Load("System.Network")
        SelectModule = LCARS.Import("select")
        Chunks = []
        Total = 0
        MaxSize = self.Gateway.MaxBodyBytes
        Connection.settimeout(30.0)
        while Total < MaxSize:
            if SelectModule and hasattr(SelectModule, "select"):
                Readable = SelectModule.select([Connection], [], [], 1.0)
                if not Readable[0]:
                    continue
            Chunk = Connection.recv(min(65536, MaxSize - Total))
            if not Chunk:
                break
            Chunks.append(Chunk)
            Total += len(Chunk)
            Data = b"".join(Chunks)
            if b"\r\n\r\n" in Data:
                HeaderPart = Data.split(b"\r\n\r\n", 1)[0]
                ContentLength = 0
                for Line in HeaderPart.split(b"\r\n"):
                    if Line.lower().startswith(b"content-length:"):
                        CLStr = Line.split(b":", 1)[1].strip()
                        if CLStr.isdigit():
                            ContentLength = int(CLStr)
                        break
                BodyReceived = len(Data) - len(HeaderPart) - 4
                while BodyReceived < ContentLength and Total < MaxSize:
                    if SelectModule and hasattr(SelectModule, "select"):
                        Readable = SelectModule.select([Connection], [], [], 1.0)
                        if not Readable[0]:
                            continue
                    Chunk = Connection.recv(min(65536, ContentLength - BodyReceived))
                    if not Chunk:
                        break
                    Chunks.append(Chunk)
                    Total += len(Chunk)
                    BodyReceived += len(Chunk)
                break
        return b"".join(Chunks)


class SubspaceVoiceGateway(Service):
    Name = "SubspaceVoiceGateway"

    def __init__(self, PortNumber: int = 8047, BindAddress: str = "127.0.0.1",
                 AuthToken: str | None = None, MaxBodyBytes: int = 262144):
        super().__init__(Id="SvcVoiceGateway")
        self.Port = PortNumber
        self.BindAddress = BindAddress
        self.AuthToken = AuthToken
        self.MaxBodyBytes = MaxBodyBytes
        self.Socket = None
        self.Channel = None
        self.ServerThread = None
        self.IsActive = False
        self.AllowedHosts = {"127.0.0.1", "::1", "localhost"}

    @classmethod
    def GetProxy(cls) -> any:
        from lcars.service.bridge import Proxy
        return Proxy.GetInstance()

    def IsClientAllowed(self, Address: str) -> bool:
        Host = str(Address).strip().lower()
        return Host in self.AllowedHosts

    def OnStart(self) -> None:
        self.IsActive = True
        self.IsRunning = True
        SocketModule = Bridge.Load("System.Socket")
        SocketType = getattr(SocketModule, "socket", None) if SocketModule else None
        if SocketType is None:
            self.IsActive = False
            self.IsRunning = False
            EmitTelemetry("VoiceGateway", "LCARS NETWORK SOCKET UNAVAILABLE")
            return
        self.Socket = SocketType(SocketModule.AF_INET, SocketModule.SOCK_STREAM)
        SolSock = getattr(SocketModule, "SOL_SOCKET", None)
        SoReuse = getattr(SocketModule, "SO_REUSEADDR", None)
        if SolSock is not None and SoReuse is not None:
            self.Socket.setsockopt(SolSock, SoReuse, 1)
        self.Socket.bind((self.BindAddress, self.Port))
        self.Socket.listen(16)
        self.Channel = GatewayChannel(self)
        ThreadType = Bridge.Load("System.Thread")
        if callable(ThreadType):
            self.ServerThread = ThreadType(target=self.Channel.Serve, daemon=True)
            self.ServerThread.start()
            EmitTelemetry("VoiceGateway", f"SUBSPACE VOICE GATEWAY ACTIVE ON {self.BindAddress}:{self.Port}")

    def OnStop(self) -> None:
        self.IsActive = False
        self.IsRunning = False
        if self.Socket:
            SocketModule = Bridge.Load("System.Socket")
            SocketType = getattr(SocketModule, "socket", None) if SocketModule else None
            if callable(SocketType):
                Wake = SocketType(SocketModule.AF_INET, SocketModule.SOCK_STREAM)
                Wake.settimeout(2.0)
                Wake.connect(("127.0.0.1", self.Port))
                Wake.close()
            CloseFn = getattr(self.Socket, "close", None)
            if callable(CloseFn):
                CloseFn()
        self.Socket = None
        EmitTelemetry("VoiceGateway", "SUBSPACE VOICE GATEWAY STOPPED")

    def MakeResponse(self, Code: int, ContentType: str, Body: str) -> bytes:
        Reason = "OK" if Code == 200 else "ERROR" if Code >= 400 else "INFO"
        Data = Body.encode("utf-8")
        Head = (
            f"HTTP/1.1 {Code} {Reason}\r\n"
            f"Content-Type: {ContentType}\r\n"
            f"Content-Length: {len(Data)}\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
            "Access-Control-Allow-Headers: Content-Type, Authorization\r\n"
            "Connection: close\r\n\r\n"
        )
        return Head.encode("utf-8") + Data

    def MakeCorsResponse(self) -> bytes:
        Head = (
            "HTTP/1.1 204 No Content\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
            "Access-Control-Allow-Headers: Content-Type, Authorization\r\n"
            "Access-Control-Max-Age: 86400\r\n"
            "Connection: close\r\n\r\n"
        )
        return Head.encode("utf-8")

    def Route(self, Method: str, Path: str, Body: str) -> bytes:
        if Method == "GET" and (Path in ("/", "/padd") or Path.startswith("/?")):
            return self.MakeResponse(200, "text/html; charset=utf-8", self.GetMobileHtml())
        if Method == "GET" and Path == "/manifest.json":
            ManifestFile = LCARS.System.Path("android/manifest.json")
            ExistsFn = getattr(ManifestFile, "exists", None)
            Content = ManifestFile.read_text(encoding="utf-8") if callable(ExistsFn) and ManifestFile.exists() else '{"name":"Starfleet LCARS PADD","short_name":"LCARS PADD","start_url":"/","display":"standalone","background_color":"#000000","theme_color":"#FF9900"}'
            return self.MakeResponse(200, "application/json; charset=utf-8", Content)
        if Method == "GET" and Path == "/icon.svg":
            IconFile = LCARS.System.Path("android/icon.svg")
            ExistsFn = getattr(IconFile, "exists", None)
            Content = IconFile.read_text(encoding="utf-8") if callable(ExistsFn) and IconFile.exists() else '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="#FF9900"/></svg>'
            return self.MakeResponse(200, "image/svg+xml", Content)
        if Method == "GET" and Path == "/service-worker.js":
            SwFile = LCARS.System.Path("android/service-worker.js")
            ExistsFn = getattr(SwFile, "exists", None)
            Content = SwFile.read_text(encoding="utf-8") if callable(ExistsFn) and SwFile.exists() else '// SW'
            return self.MakeResponse(200, "application/javascript", Content)
        if Method == "GET" and Path == "/api/status":
            return self.MakeResponse(200, "application/json; charset=utf-8", self.StatusPayload())
        if Method == "POST" and Path == "/api/voice":
            return self.MakeResponse(200, "application/json; charset=utf-8", self.VoicePayload(Body))
        if Method == "POST" and Path == "/api/alert":
            return self.MakeResponse(200, "application/json; charset=utf-8", self.AlertPayload(Body))
        if Method == "GET" and Path == "/api/comm/devices":
            from lcars.modules.comm import CommSubsystem
            Devices = CommSubsystem.GetInstance().SmartConnect.GetAllDevices()
            Json = self.JsonModule()
            return self.MakeResponse(200, "application/json; charset=utf-8", Json.dumps({"Devices": Devices}) if Json else "{}")
        if Method == "GET" and Path == "/api/comm/clipboard":
            from lcars.modules.comm import CommSubsystem
            Clip = CommSubsystem.GetInstance().SmartConnect.GetClipboard()
            Json = self.JsonModule()
            return self.MakeResponse(200, "application/json; charset=utf-8", Json.dumps(Clip) if Json else "{}")
        if Method == "POST" and Path == "/api/comm/clipboard":
            from lcars.modules.comm import CommSubsystem
            Json = self.JsonModule()
            Data = {}
            if Body and Json:
                Clean = Body.strip()
                if Clean.startswith("{") and Clean.endswith("}"):
                    Parsed = Json.loads(Clean)
                    if isinstance(Parsed, dict):
                        Data = Parsed
            Text = str(Data.get("Text", ""))
            CommSubsystem.GetInstance().SmartConnect.SetClipboard(Text, SourceDeviceId="LCARS 25th")
            return self.MakeResponse(200, "application/json; charset=utf-8", '{"Status": "Success"}')
        if Method == "POST" and Path == "/api/engineering/control":
            from lcars.modules.comm import CommSubsystem
            Json = self.JsonModule()
            Data = {}
            if Body and Json:
                Clean = Body.strip()
                if Clean.startswith("{") and Clean.endswith("}"):
                    Parsed = Json.loads(Clean)
                    if isinstance(Parsed, dict):
                        Data = Parsed
            Action = str(Data.get("Action", ""))
            Params = Data.get("Parameters", {})
            Result = CommSubsystem.GetInstance().SmartConnect.ExecuteCommand(Action, Params)
            return self.MakeResponse(200, "application/json; charset=utf-8", Json.dumps(Result) if Json else "{}")
        return self.MakeResponse(404, "text/plain; charset=utf-8", "LCARS CHANNEL: ROUTE NOT FOUND")

    def JsonModule(self):
        JsonMod = getattr(LCARS.Storage, "Json", None)
        if not JsonMod:
            JsonMod = getattr(LCARS.Storage, "JSON", None)
        if not JsonMod:
            JsonMod = Bridge.Load("System.Json")
        return JsonMod

    def StatusPayload(self) -> str:
        Comp = BoardComputer.GetInstance()
        AlertRaw = Comp.GetSubsystemState("Tactical")
        AlertState = getattr(AlertRaw, "value", getattr(AlertRaw, "name", str(AlertRaw)))
        if isinstance(AlertState, str):
            AlertState = AlertState.upper()
        from lcars.engineering.controller import Engineering
        Eng = Engineering.GetInstance()
        WarpFactor = Eng.WarpDrive.CurrentWarpFactor if hasattr(Eng.WarpDrive, "CurrentWarpFactor") else 0.0
        WarpStr = f"WARP {WarpFactor:.1f}" if WarpFactor > 0 else "WARP IMPULSE"
        ShieldsVal = f"{Eng.Deflector.ShieldGrid.GetAverageIntegrity():.0f}%" if hasattr(Eng.Deflector, "ShieldGrid") else "100%"
        Payload = {
            "ShipRegistry": Comp.ShipRegistry,
            "ShipClass": Comp.ShipClass,
            "RuntimeMode": str(Comp.RuntimeMode),
            "Stardate": str(Comp.GetStardate()),
            "AlertLevel": AlertState,
            "WarpCore": WarpStr,
            "Shields": ShieldsVal,
            "Sensors": "ACTIVE",
            "DeviceTarget": "LCARS 25th (Motorola)",
        }
        Json = self.JsonModule()
        return Json.dumps(Payload) if Json else "{}"

    def VoicePayload(self, Body: str) -> str:
        Json = self.JsonModule()
        if not Json:
            return "{}"
        Data = {}
        if Body and isinstance(Body, str):
            Clean = Body.strip()
            if Clean.startswith("{") and Clean.endswith("}"):
                Parsed = Json.loads(Clean)
                if isinstance(Parsed, dict):
                    Data = Parsed
        Text = str(Data.get("Text", "")).strip()
        Comp = BoardComputer.GetInstance()
        ExecFn = getattr(Comp, "ExecuteDirective", None)
        Res = ExecFn(Text) if callable(ExecFn) and Text else {"Message": "LCARS COMPUTER: DIRECTIVE PROCESSED."}
        ResponseText = Res.get("Message", "DIRECTIVE EXECUTED") if isinstance(Res, dict) else str(Res)
        EmitTelemetry("VoiceGateway", f"DIRECTIVE RECEIVED: '{Text}'")
        return Json.dumps({"InputDirective": Text, "ResponseText": ResponseText, "Stardate": str(Comp.GetStardate())})

    def AlertPayload(self, Body: str) -> str:
        Json = self.JsonModule()
        if not Json:
            return "{}"
        Data = {}
        if Body and isinstance(Body, str):
            Clean = Body.strip()
            if Clean.startswith("{") and Clean.endswith("}"):
                Parsed = Json.loads(Clean)
                if isinstance(Parsed, dict):
                    Data = Parsed
        Level = str(Data.get("Level", "NORMAL")).upper()
        Comp = BoardComputer.GetInstance()
        SetAlertFn = getattr(Comp, "SetAlert", None)
        if callable(SetAlertFn):
            SetAlertFn(Level)
        EmitTelemetry("VoiceGateway", f"TACTICAL ALERT CHANGED VIA MOBILE: {Level}")
        return Json.dumps({"Status": "SUCCESS", "AlertLevel": Level})

    @classmethod
    def GetLocalIp(cls) -> str:
        SocketModule = Bridge.Load("System.Network")
        SocketType = getattr(SocketModule, "socket", None) if SocketModule else None
        if callable(SocketType):
            S = SocketType(SocketModule.AF_INET, SocketModule.SOCK_DGRAM)
            SetTimeoutFn = getattr(S, "settimeout", None)
            if callable(SetTimeoutFn):
                SetTimeoutFn(2.0)
            ConnectFn = getattr(S, "connect", None)
            if callable(ConnectFn):
                ConnectFn(("8.8.8.8", 80))
            GetSockNameFn = getattr(S, "getsockname", None)
            LocalIp = GetSockNameFn()[0] if callable(GetSockNameFn) else "127.0.0.1"
            CloseFn = getattr(S, "close", None)
            if callable(CloseFn):
                CloseFn()
            return LocalIp
        return "127.0.0.1"

    @classmethod
    def GetMobileHtml(cls) -> str:
        PaddPath = LCARS.System.Path("android/index.html")
        ExistsFn = getattr(PaddPath, "exists", None)
        if callable(ExistsFn) and PaddPath.exists():
            return PaddPath.read_text(encoding="utf-8")
        return """<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>LCARS COMBADGE // FEDERATION COMMUNICATOR</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body {
            background-color: #000000;
            color: #FF9900;
            font-family: 'LCARS', 'Arial Black', -apple-system, sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            padding: 12px;
            overflow: hidden;
        }
        .Header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #FF9900;
            color: #000000;
            padding: 8px 16px;
            border-radius: 18px 18px 0 0;
            font-weight: 900;
            letter-spacing: 1px;
            font-size: 14px;
        }
        .SubHeader {
            background-color: #CC6699;
            color: #000000;
            padding: 4px 16px;
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 12px;
            border-radius: 0 0 12px 12px;
        }
        .TelemetryCard {
            background-color: #111111;
            border-left: 6px solid #3366CC;
            padding: 10px 14px;
            margin-bottom: 12px;
            border-radius: 4px;
            font-size: 12px;
            line-height: 1.5;
            color: #99CCFF;
        }
        .TelemetryVal { color: #FFFFFF; font-weight: bold; }
        .CombadgeContainer {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        .CombadgeButton {
            width: 140px;
            height: 190px;
            background: linear-gradient(135deg, #FFCC00 0%, #FF9900 60%, #CC6600 100%);
            border: none;
            border-radius: 70px 70px 50px 50px;
            box-shadow: 0 0 25px rgba(255, 153, 0, 0.4);
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #000000;
            font-weight: 900;
            font-size: 16px;
            transition: all 0.2s ease;
            position: relative;
        }
        .CombadgeButton:active, .CombadgeButton.Listening {
            transform: scale(0.95);
            box-shadow: 0 0 40px rgba(255, 51, 51, 0.8);
            background: linear-gradient(135deg, #FF6666 0%, #FF3333 60%, #990000 100%);
            color: #FFFFFF;
        }
        .CombadgeSymbol {
            font-size: 32px;
            margin-bottom: 6px;
        }
        .PulseWave {
            font-size: 11px;
            letter-spacing: 2px;
            margin-top: 10px;
            color: #FF9900;
            font-weight: bold;
            height: 18px;
        }
        .ResponseDisplay {
            background-color: #1A1A1A;
            border: 1px solid #FF9900;
            border-radius: 8px;
            padding: 12px;
            min-height: 90px;
            max-height: 130px;
            overflow-y: auto;
            color: #FFFFFF;
            font-size: 13px;
            line-height: 1.4;
            margin-bottom: 12px;
        }
        .ResponseTitle { color: #FF9900; font-size: 11px; font-weight: bold; margin-bottom: 4px; }
        .ActionGrid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 8px;
            margin-bottom: 8px;
        }
        .LcarsButton {
            background-color: #3366CC;
            color: #000000;
            border: none;
            padding: 12px 6px;
            font-weight: 900;
            font-size: 11px;
            border-radius: 12px;
            cursor: pointer;
            text-align: center;
        }
        .LcarsButton.Red { background-color: #FF3333; color: #FFFFFF; }
        .LcarsButton.Yellow { background-color: #FFCC00; color: #000000; }
        .LcarsButton.Green { background-color: #33CC66; color: #000000; }
        .LcarsButton:active { opacity: 0.7; }
        html, body { background: #000000; color: #FF9933; font-family: 'LCARS', Arial, sans-serif; font-weight: 400; }
        body { max-width: 720px; margin: 0 auto; padding: 16px; }
        .Header { background: #000000; color: #66CCFF; border-left: 42px solid #FF9933; border-bottom: 2px solid #FF9933; border-radius: 0; padding: 10px 14px; font-weight: 400; }
        .SubHeader { background: #CC6699; border-radius: 0; font-weight: 400; color: #000000; }
        .TelemetryCard, .ResponseDisplay { border-radius: 0; background: #050505; border: 1px solid #334455; border-left: 10px solid #3366CC; font-weight: 400; }
        .TelemetryVal, .ResponseTitle, .PulseWave { font-weight: 400; }
        .CombadgeContainer { min-height: 150px; }
        .CombadgeButton { width: min(82vw, 360px); height: 64px; border-radius: 0; background: #FF9933; box-shadow: none; color: #000000; font-weight: 400; letter-spacing: 1px; }
        .CombadgeButton:active, .CombadgeButton.Listening { transform: none; border-left: 22px solid #FF3333; background: #FF3333; box-shadow: none; }
        .CombadgeSymbol { display: none; }
        .ActionGrid { grid-template-columns: 1fr 1fr 1fr; gap: 4px; }
        .LcarsButton { border-radius: 0; padding: 12px 4px; font-weight: 400; }
        .CommandLine { display: flex; gap: 4px; margin-bottom: 10px; }
        .CommandInput { flex: 1; min-width: 0; background: #050505; color: #66CCFF; border: 1px solid #3366CC; border-left: 10px solid #3366CC; border-radius: 0; padding: 12px; font: 400 14px 'LCARS', Arial, sans-serif; }
        .CommandSend { background: #FF9933; color: #000000; border: 0; padding: 0 16px; font: 400 12px 'LCARS', Arial, sans-serif; }
    </style>
</head>
<body>
    <div class="Header">
        <span>LCARS COMMUNICATOR</span>
        <span id="StardateVal">74205.1</span>
    </div>
    <div class="SubHeader">
        <span id="ShipName">USS SOVEREIGN // NCC-74205</span>
    </div>

    <div class="TelemetryCard">
        <div>ALERT STATUS: <span class="TelemetryVal" id="AlertVal" style="color: #33CC66;">NORMAL</span></div>
        <div>WARP CORE: <span class="TelemetryVal" id="WarpVal">ONLINE</span> | SHIELDS: <span class="TelemetryVal" id="ShieldsVal">100%</span></div>
    </div>

    <div class="CombadgeContainer">
        <button class="CombadgeButton" id="CombadgeButton" onclick="ToggleVoice()">
            <div class="CombadgeSymbol">&#x25E4;</div>
            <div id="BtnText">TAP TO TALK</div>
        </button>
        <div class="PulseWave" id="StatusWave">SUBSPACE READY</div>
    </div>

    <div class="ResponseDisplay">
        <div class="ResponseTitle">BOARD COMPUTER RESPONSE:</div>
        <div id="ResponseText">Комп'ютер готовий до прийому голосових команд...</div>
    </div>

    <div class="CommandLine">
        <input class="CommandInput" id="DirectiveInput" placeholder="ВВЕДІТЬ НАКАЗ АБО ДИРЕКТИВУ...">
        <button class="CommandSend" onclick="SendManual()">TRANSMIT</button>
    </div>

    <div class="ActionGrid">
        <button class="LcarsButton Red" onclick="SetAlert('RED')">RED ALERT</button>
        <button class="LcarsButton Yellow" onclick="SetAlert('YELLOW')">YELLOW</button>
        <button class="LcarsButton Green" onclick="SetAlert('NORMAL')">NORMAL</button>
    </div>

    <div class="ActionGrid" style="margin-top: 6px;">
        <button class="LcarsButton" style="background-color: #99CCFF;" onclick="SendVoiceDirective('статус систем')">СТАТУС</button>
        <button class="LcarsButton" style="background-color: #FFCC00;" onclick="SendVoiceDirective('діагностика')">ДІАГНОСТИКА</button>
        <button class="LcarsButton" style="background-color: #CC6699;" onclick="SendVoiceDirective('підпростір')">ПІДПРОСТІР</button>
    </div>

    <div class="ActionGrid" style="margin-top: 6px;">
        <button class="LcarsButton" style="background-color: #3399FF; color: #FFFFFF;" onclick="SetWarp(1)">WARP 1</button>
        <button class="LcarsButton" style="background-color: #3399FF; color: #FFFFFF;" onclick="SetWarp(5)">WARP 5</button>
        <button class="LcarsButton" style="background-color: #3399FF; color: #FFFFFF;" onclick="SetWarp(9)">WARP 9</button>
    </div>

    <div class="CommandLine" style="margin-top: 6px;">
        <input class="CommandInput" id="ClipboardInput" placeholder="БУФЕР ОБМІНУ З ПК (SMART CONNECT)...">
        <button class="CommandSend" style="background-color: #CC6699;" onclick="SyncClipboard()">SYNC</button>
    </div>

    <script>
        let IsListening = false;
        let VoiceRecognition = null;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechClass = window.SpeechRecognition || window.webkitSpeechRecognition;
            VoiceRecognition = new SpeechClass();
            VoiceRecognition.continuous = false;
            VoiceRecognition.interimResults = false;
            VoiceRecognition.lang = 'uk-UA';

            VoiceRecognition.onstart = function() {
                IsListening = true;
                document.getElementById('CombadgeButton').classList.add('Listening');
                document.getElementById('BtnText').innerText = 'LISTENING...';
                document.getElementById('StatusWave').innerText = '>>> ПРИЙОМ ГОЛОСУ <<<';
                PlayBeep(880, 0.1);
            };

            VoiceRecognition.onresult = function(event) {
                const Transcript = event.results[0][0].transcript;
                document.getElementById('StatusWave').innerText = 'ПЕРЕДАЧА: ' + Transcript;
                SendVoiceDirective(Transcript);
            };

            VoiceRecognition.onerror = function(event) {
                document.getElementById('StatusWave').innerText = 'ПОМИЛКА: ' + event.error;
                ResetButton();
            };

            VoiceRecognition.onend = function() {
                ResetButton();
            };
        }

        function SpeakResponse(text) {
            if (!('speechSynthesis' in window)) return;
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'uk-UA';
            utterance.rate = 1.0;
            utterance.pitch = 1.05;
            window.speechSynthesis.speak(utterance);
        }

        function ToggleVoice() {
            if (!VoiceRecognition) {
                const ManualText = prompt("Введіть голосову директиву для комп'ютера:", "червона тривога");
                if (ManualText) SendVoiceDirective(ManualText);
                return;
            }
            if (IsListening) {
                VoiceRecognition.stop();
            } else {
                VoiceRecognition.start();
            }
        }

        function ResetButton() {
            IsListening = false;
            document.getElementById('CombadgeButton').classList.remove('Listening');
            document.getElementById('BtnText').innerText = 'TAP TO TALK';
            document.getElementById('StatusWave').innerText = 'SUBSPACE READY';
        }

        function SendVoiceDirective(TextStr) {
            PlayBeep(660, 0.08);
            fetch('/api/voice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ Text: TextStr })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('ResponseText').innerText = data.ResponseText;
                PlayBeep(440, 0.12);
                SpeakResponse(data.ResponseText);
                UpdateStatus();
            });
        }

        function SendManual() {
            const Field = document.getElementById('DirectiveInput');
            const Text = Field.value.trim();
            if (!Text) return;
            Field.value = '';
            SendVoiceDirective(Text);
        }

        function SetWarp(FactorVal) {
            PlayBeep(770, 0.1);
            fetch('/api/engineering/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ Action: 'WARP', Parameters: { Factor: FactorVal } })
            })
            .then(res => res.json())
            .then(data => {
                UpdateStatus();
                SpeakResponse('Варп фактор ' + FactorVal + ' активовано.');
            });
        }

        function SyncClipboard() {
            const Field = document.getElementById('ClipboardInput');
            const TextVal = Field.value.trim();
            if (TextVal) {
                fetch('/api/comm/clipboard', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ Text: TextVal })
                })
                .then(res => res.json())
                .then(data => {
                    PlayBeep(990, 0.08);
                    document.getElementById('StatusWave').innerText = 'БУФЕР СИНХРОНІЗОВАНО З ПК';
                });
            } else {
                fetch('/api/comm/clipboard')
                .then(res => res.json())
                .then(data => {
                    if (data.Content) {
                        Field.value = data.Content;
                        document.getElementById('StatusWave').innerText = 'ОТРИМАНО З БУФЕРА ПК';
                    }
                });
            }
        }

        function SetAlert(LevelStr) {
            PlayBeep(880, 0.1);
            fetch('/api/alert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ Level: LevelStr })
            })
            .then(res => res.json())
            .then(data => {
                UpdateStatus();
                if (LevelStr === 'RED') SpeakResponse('Увага. Червона тривога оголошена.');
                else if (LevelStr === 'YELLOW') SpeakResponse('Жовта тривога активована.');
                else SpeakResponse('Стан тривоги скасовано. Корабель у штатному режимі.');
            });
        }

        function UpdateStatus() {
            fetch('/api/status')
            .then(res => res.json())
            .then(data => {
                document.getElementById('StardateVal').innerText = data.Stardate;
                document.getElementById('ShipName').innerText = data.ShipRegistry + ' // ' + data.ShipClass;
                const AlertElement = document.getElementById('AlertVal');
                AlertElement.innerText = data.AlertLevel;
                if (data.AlertLevel === 'RED') AlertElement.style.color = '#FF3333';
                else if (data.AlertLevel === 'YELLOW') AlertElement.style.color = '#FFCC00';
                else AlertElement.style.color = '#33CC66';
                document.getElementById('WarpVal').innerText = data.WarpCore;
                document.getElementById('ShieldsVal').innerText = data.Shields;
            });
        }

        function PlayBeep(Frequency, Duration) {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            const Context = new AudioContextClass();
            const Osc = Context.createOscillator();
            Osc.type = 'sine';
            Osc.frequency.value = Frequency;
            Osc.connect(Context.destination);
            Osc.start();
            Osc.stop(Context.currentTime + Duration);
        }

        setInterval(UpdateStatus, 3000);
        UpdateStatus();
    </script>
</body>
</html>
"""


class CommunicatorAccess(LCARS):
    GatewayInstance = None

    @classmethod
    def GetCommunicator(cls, PortNumber: int = 8047, BindAddress: str = "127.0.0.1",
                        AuthToken: str | None = None) -> SubspaceVoiceGateway:
        if cls.GatewayInstance is None:
            cls.GatewayInstance = SubspaceVoiceGateway(PortNumber, BindAddress, AuthToken)
        return cls.GatewayInstance

    @classmethod
    def StartGateway(cls, PortNumber: int = 8047, BindAddress: str = "127.0.0.1",
                     AuthToken: str | None = None) -> None:
        Gateway = cls.GetCommunicator(PortNumber, BindAddress, AuthToken)
        if not Gateway.IsActive:
            Gateway.OnStart()

    @classmethod
    def StopGateway(cls) -> None:
        if cls.GatewayInstance and cls.GatewayInstance.IsActive:
            cls.GatewayInstance.OnStop()

GetCommunicator = CommunicatorAccess.GetCommunicator
StartGateway = CommunicatorAccess.StartGateway
StopGateway = CommunicatorAccess.StopGateway

def RunGateway(PortNumber: int = 8047, BindAddress: str = "127.0.0.1") -> None:
    Gateway = CommunicatorAccess.GetCommunicator(PortNumber, BindAddress)
    CommunicatorAccess.StartGateway(PortNumber, BindAddress)
    Gateway.ServerThread.join()

__all__ = [
    "SubspaceVoiceGateway",
    "CommunicatorAccess",
    "GetCommunicator",
    "StartGateway",
    "StopGateway",
    "RunGateway",
]
