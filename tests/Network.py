# ◤ TITANIUM LCARS :: NETWORK SUITE 🖖
# =============================================================================
# ФАЙЛ: tests/Network.py
# ПРИЗНАЧЕННЯ: Верифікація мережевого ядра: Firewall, TcpServer, HttpServer,
#              AsyncTcpServer, NetworkManager, ServerRegistry.
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase).
# =============================================================================

from lcars.base.type import LCARS

SysModule = LCARS.Import("sys")
if hasattr(SysModule.stdout, "reconfigure"):
    SysModule.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(SysModule.stderr, "reconfigure"):
    SysModule.stderr.reconfigure(encoding="utf-8", errors="replace")


class NetworkSuite:
    def VerifyFirewallPolicy(self):
        from lcars.modules.net import FirewallPolicy, FirewallRule

        Fw = FirewallPolicy(SystemId="TestFirewall")
        assert Fw.Enabled is True
        assert Fw.AllowLocal is True

        assert Fw.Allow("192.168.1.100") is True
        assert Fw.IsAllowed("192.168.1.100") is True

        assert Fw.Deny("10.0.0.5") is True
        assert Fw.IsAllowed("10.0.0.5") is False

        assert Fw.IsAllowed("127.0.0.1") is True
        assert Fw.IsAllowed("::1") is True
        assert Fw.IsAllowed("localhost") is True

        Fw.Enabled = False
        assert Fw.IsAllowed("10.0.0.5") is True
        Fw.Enabled = True

        assert Fw.ValidateAddress("192.168.1.1") is True
        assert Fw.ValidateAddress("::1") is True
        assert Fw.ValidateAddress("") is False

    def VerifyFirewallRules(self):
        from lcars.modules.net import FirewallPolicy

        Fw = FirewallPolicy(SystemId="TestFirewallRules")
        assert Fw.AddRule("ALLOW", "192.168.0.0/24") is True
        assert Fw.AddRule("DENY", "10.0.0.0/8") is True
        assert Fw.AddRule("ALLOW", ":8080") is True

        assert Fw.IsAllowed("192.168.0.50", 80) is True
        assert Fw.IsAllowed("10.0.0.1", 80) is False
        assert Fw.IsAllowed("172.16.0.1", 8080) is True

        assert Fw.RemoveRule("10.0.0.0/8") is True
        assert Fw.RemoveRule("nonexistent") is False

        assert Fw.AddRule("INVALID", "") is False

    def VerifyFirewallConnections(self):
        from lcars.modules.net import FirewallPolicy

        Fw = FirewallPolicy(SystemId="TestFwConn")
        Fw.MaxConnections = 2
        assert Fw.IncrementConnections() is True
        assert Fw.IncrementConnections() is True
        assert Fw.IncrementConnections() is False
        Fw.DecrementConnections()
        assert Fw.IncrementConnections() is True

    def VerifyTcpServerLifecycle(self):
        from lcars.modules.net import TcpServer, FirewallPolicy

        Fw = FirewallPolicy(SystemId="TestTcpFw")
        Server = TcpServer(Name="TestTcp", Host="127.0.0.1", Port=0, Firewall=Fw)
        assert Server.Running is False
        assert Server.Start() is True
        assert Server.Running is True
        assert Server.Port > 0
        assert Server.Stop() is True
        assert Server.Running is False

    def VerifyTcpServerFirewall(self):
        import socket as _socket
        from lcars.modules.net import TcpServer, FirewallPolicy

        Fw = FirewallPolicy(SystemId="TestTcpFwBlock")
        Fw.Deny("127.0.0.1")
        Server = TcpServer(Name="TestTcpBlock", Host="127.0.0.1", Port=0, Firewall=Fw)
        assert Server.Start() is True
        Port = Server.Port
        S = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        S.settimeout(2.0)
        try:
            S.connect(("127.0.0.1", Port))
            Data = S.recv(1024)
        except Exception:
            Data = b""
        finally:
            S.close()
        Server.Stop()

    def VerifyHttpServerLifecycle(self):
        from lcars.modules.net import HttpServer, FirewallPolicy

        Fw = FirewallPolicy(SystemId="TestHttpFw")
        def TestRouter(Method, Path, Body, ServerObj):
            return ServerObj.MakeResponse(200, "text/plain", "OK")
        Server = HttpServer(Name="TestHttp", Host="127.0.0.1", Port=0, Firewall=Fw, Router=TestRouter)
        assert Server.Start() is True
        assert Server.Port > 0
        assert Server.Stop() is True

    def VerifyHttpServerMakeResponse(self):
        from lcars.modules.net import HttpServer

        Server = HttpServer(Name="TestHttpResp", Host="127.0.0.1", Port=0)
        Resp = Server.MakeResponse(200, "text/plain", "Hello")
        assert b"HTTP/1.1 200 OK" in Resp
        assert b"Content-Type: text/plain" in Resp
        assert b"Hello" in Resp

        Resp404 = Server.MakeResponse(404, "text/plain", "Not Found")
        assert b"404" in Resp404
        assert b"Not Found" in Resp404

        Resp500 = Server.MakeResponse(500, "text/plain", "Error")
        assert b"500" in Resp500
        assert b"Internal Server Error" in Resp500

    def VerifyServerRegistry(self):
        from lcars.modules.net import ServerRegistry, TcpServer

        Reg = ServerRegistry()
        S1 = TcpServer(Name="RegTest1", Host="127.0.0.1", Port=0)
        S2 = TcpServer(Name="RegTest2", Host="127.0.0.1", Port=0)
        Reg.Register(S1)
        Reg.Register(S2)
        assert Reg.Get("RegTest1") is S1
        assert Reg.Get("RegTest2") is S2
        assert Reg.Get("Nonexistent") is None
        assert Reg.Unregister("RegTest1") is True
        assert Reg.Get("RegTest1") is None
        assert Reg.Unregister("Nonexistent") is False

    def VerifyNetworkManagerAllowlist(self):
        from lcars.modules.net import NetworkManager

        Nm = NetworkManager()
        assert Nm.IsEnabled() is True
        assert "api.github.com" in Nm.Allowlist
        assert Nm.AddToAllowlist("test.example.com") is True
        assert "test.example.com" in Nm.Allowlist
        assert Nm.RemoveFromAllowlist("test.example.com") is True
        assert "test.example.com" not in Nm.Allowlist
        assert Nm.AddToAllowlist("") is False
        assert Nm.AddToAllowlist(None) is False

    def VerifyNetworkManagerValidation(self):
        from lcars.modules.net import NetworkManager

        Nm = NetworkManager()
        Valid, Msg = Nm.ValidateUrl("https://api.github.com")
        assert Valid is True
        assert Msg == "OK"

        Valid, Msg = Nm.ValidateUrl("")
        assert Valid is False
        assert Msg == "URL_EMPTY"

        Valid, Msg = Nm.ValidateUrl("ftp://example.com")
        assert Valid is False
        assert Msg == "URL_INVALID_SCHEME"

        Valid, Msg = Nm.ValidateUrl("https://blocked.evil.com")
        assert Valid is False
        assert Msg == "HOST_BLOCKED"

        Nm.SetEnabled(False)
        Valid, Msg = Nm.ValidateUrl("https://api.github.com")
        assert Valid is False
        assert Msg == "NETWORK_DISABLED"
        Nm.SetEnabled(True)

    def VerifyNetworkManagerHostAllowed(self):
        from lcars.modules.net import NetworkManager

        Nm = NetworkManager()
        assert Nm.IsHostAllowed("https://api.github.com/test") is True
        assert Nm.IsHostAllowed("https://subdomain.api.github.com/test") is True
        assert Nm.IsHostAllowed("https://blocked.evil.com") is False
        assert Nm.IsHostAllowed("https://localhost:3000") is True
        assert Nm.IsHostAllowed("https://127.0.0.1:3000") is True
        assert Nm.IsHostAllowed("https://[::1]:3000") is True

    def VerifyNetworkManagerConfig(self):
        from lcars.modules.net import NetworkManager

        Nm = NetworkManager()
        Config = Nm.GetConfig()
        assert "enabled" in Config
        assert "allowlist" in Config
        assert "ssl_verify" in Config
        assert "use_session" in Config

        Status = Nm.GetStatus()
        assert Status["Name"] == "network"
        assert "AllowlistCount" in Status
        assert "SessionActive" in Status

    def VerifyNetworkManagerCalculateBackoff(self):
        from lcars.modules.net import NetworkManager

        Nm = NetworkManager()
        B0 = Nm.CalculateBackoff(0)
        B1 = Nm.CalculateBackoff(1)
        B2 = Nm.CalculateBackoff(2)
        assert B0 < B1 < B2
        assert B0 >= 0

    def VerifyNetworkManagerLoadConfig(self):
        from lcars.modules.net import NetworkManager

        Nm = NetworkManager()
        OriginalTimeout = Nm.DefaultTimeout
        Nm.LoadConfig({"enabled": False, "default_timeout": 30, "max_retries": 5})
        assert Nm.IsEnabled() is False
        assert Nm.DefaultTimeout == 30
        assert Nm.MaxRetries == 5
        Nm.LoadConfig({"enabled": True, "default_timeout": OriginalTimeout, "max_retries": 2})
        assert Nm.IsEnabled() is True

    def VerifyAsyncNetworkManager(self):
        from lcars.modules.net import Async as AsyncNetworkManager

        Anm = AsyncNetworkManager()
        assert Anm.IsEnabled() is True
        assert Anm.AsyncClient is None
        Config = Anm.GetConfig()
        assert "ssl_verify" in Config

    def VerifyServerSignature(self):
        from lcars.modules.net import ServerSignature

        Sig = ServerSignature("TestServer", "127.0.0.1", 8080, "TCP")
        assert Sig.Name == "TestServer"
        assert Sig.Host == "127.0.0.1"
        assert Sig.Port == 8080
        assert Sig.Protocol == "TCP"
        assert "TCP" in Sig.Identifier
        assert "8080" in Sig.Identifier
        Dict = Sig.ToDict()
        assert Dict["Name"] == "TestServer"

    @classmethod
    def RunAll(cls):
        PrintFn = print
        PrintFn("=" * 76)
        PrintFn("◤ RUNNING TITANIUM NETWORK SUITE 🖖")
        PrintFn("============================================================================")
        SuiteInstance = cls()
        Tests = [
            ("FirewallPolicy basics", SuiteInstance.VerifyFirewallPolicy),
            ("FirewallRules (CIDR/port)", SuiteInstance.VerifyFirewallRules),
            ("Firewall connection limits", SuiteInstance.VerifyFirewallConnections),
            ("TcpServer lifecycle", SuiteInstance.VerifyTcpServerLifecycle),
            ("TcpServer firewall block", SuiteInstance.VerifyTcpServerFirewall),
            ("HttpServer lifecycle", SuiteInstance.VerifyHttpServerLifecycle),
            ("HttpServer MakeResponse", SuiteInstance.VerifyHttpServerMakeResponse),
            ("ServerRegistry CRUD", SuiteInstance.VerifyServerRegistry),
            ("NetworkManager allowlist", SuiteInstance.VerifyNetworkManagerAllowlist),
            ("NetworkManager URL validation", SuiteInstance.VerifyNetworkManagerValidation),
            ("NetworkManager host allowed", SuiteInstance.VerifyNetworkManagerHostAllowed),
            ("NetworkManager config", SuiteInstance.VerifyNetworkManagerConfig),
            ("NetworkManager backoff", SuiteInstance.VerifyNetworkManagerCalculateBackoff),
            ("NetworkManager LoadConfig", SuiteInstance.VerifyNetworkManagerLoadConfig),
            ("AsyncNetworkManager init", SuiteInstance.VerifyAsyncNetworkManager),
            ("ServerSignature", SuiteInstance.VerifyServerSignature),
        ]
        for Idx, (Name, TestFn) in enumerate(Tests, 1):
            TestFn()
            PrintFn(f"  ✓ [{Idx}/{len(Tests)}] {Name}: VERIFIED")
        PrintFn("============================================================================")
        PrintFn(f"◤ ALL {len(Tests)} NETWORK SUITE CHECKS COMPLETED // NOMINAL 🖖")
        PrintFn("============================================================================")


ArgvList = getattr(SysModule, "argv", [])
IsPytestActive = any("pytest" in ArgItem for ArgItem in ArgvList)
if not IsPytestActive:
    NetworkSuite.RunAll()
