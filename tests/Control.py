# ◤ TITANIUM LCARS :: CONTROL SUITE 🖖
# =============================================================================
# ФАЙЛ: tests/Control.py
# ПРИЗНАЧЕННЯ: Комплексна верифікація автономного застосунку LCARS Control,
#              контролера фонового демона GatewayDaemon, 7 станцій робочого простору
#              та архітектурної цілісності за стандартом Titanium LCARS.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase).
# =============================================================================

from lcars.base.type import LCARS

SysModule = LCARS.Import("sys")
if hasattr(SysModule.stdout, "reconfigure"):
    SysModule.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(SysModule.stderr, "reconfigure"):
    SysModule.stderr.reconfigure(encoding="utf-8", errors="replace")


class ControlSuite:
    def VerifyDaemonLifecycle(self):
        DaemonModule = LCARS.Import("programs.Control.daemon")
        assert hasattr(DaemonModule, "GatewayDaemon")
        DaemonInstance = DaemonModule.GatewayDaemon.GetInstance()
        assert DaemonInstance is not None
        assert DaemonInstance.Port in (3055, 3688)

        Firewall = DaemonInstance.GetFirewallStatus()
        assert Firewall.get("Inbound") == "LOOPBACK_ONLY"
        assert Firewall.get("Outbound") == "ALLOWLIST"

        assert DaemonInstance.GetFormattedUptime() in ("—", "00:00:00")

    def VerifyControlAppInstantiation(self):
        BaseApp = LCARS.Application
        App = BaseApp.instance() if hasattr(BaseApp, "instance") else None
        if App is None and callable(BaseApp):
            App = BaseApp([])

        AppModule = LCARS.Import("programs.Control.app")
        assert hasattr(AppModule, "LCARSControlApp")
        AppInstance = AppModule.LCARSControlApp()
        assert AppInstance is not None
        assert AppInstance.Window is not None

        RequiredStations = ["Status", "Agent", "Channels", "Subscriptions", "Environment", "Dashboard", "Cockpit"]
        for StationKey in RequiredStations:
            assert StationKey in AppInstance.Views
            assert AppInstance.Views[StationKey].Widget is not None

        AppInstance.SelectStation("Dashboard")
        assert AppInstance.ActiveStation == "Dashboard"

        AppInstance.SelectStation("Cockpit")
        assert AppInstance.ActiveStation == "Cockpit"

        AppInstance.SelectStation("Status")
        assert AppInstance.ActiveStation == "Status"
        # Fullscreen & Window controls verification
        assert AppInstance.IsFullScreen is True
        assert AppInstance.WindowToggleBtn is not None
        assert AppInstance.ShutdownBtn is not None
        AppInstance.ToggleFullScreen()
        assert AppInstance.IsFullScreen is False
        AppInstance.ToggleFullScreen()
        assert AppInstance.IsFullScreen is True

        # Agent Station interactivity verification
        AgentStation = AppInstance.Views["Agent"]
        assert AgentStation is not None
        assert len(AgentStation.AgentsDirectory) >= 11

        AgentStation.SelectAgent("gemini")
        assert AgentStation.ActiveAgentKey == "gemini"

        AgentStation.SelectAgent("devin")
        assert AgentStation.ActiveAgentKey == "devin"

        AgentStation.SelectAgent("claude")
        assert AgentStation.ActiveAgentKey == "claude"

        AgentStation.SelectAgent("neuralcore")
        assert AgentStation.ActiveAgentKey == "neuralcore"

        AppInstance.close()

    def VerifyTitaniumIntegrity(self):
        PathHelper = LCARS.Import("pathlib").Path
        ProjectRoot = PathHelper(__file__).resolve().parents[1]
        ControlDir = ProjectRoot / "programs" / "Control"
        FilesToCheck = [
            ControlDir / "daemon.py",
            ControlDir / "views.py",
            ControlDir / "app.py",
            ProjectRoot / "control.py",
        ]

        for TargetPath in FilesToCheck:
            assert TargetPath.exists()
            FileText = TargetPath.read_text(encoding="utf-8")
            Lines = FileText.splitlines()
            ExceptLines = [L for L in Lines if L.strip().startswith("except ")]
            assert len(ExceptLines) == 0

    @classmethod
    def RunAll(cls):
        PrintFn = print
        PrintFn("=" * 76)
        PrintFn("◤ RUNNING TITANIUM CONTROL SUITE 🖖")
        PrintFn("============================================================================")
        SuiteInstance = cls()
        SuiteInstance.VerifyDaemonLifecycle()
        PrintFn("  ✓ [1/3] GatewayDaemon Controller & Resolution: VERIFIED")
        SuiteInstance.VerifyControlAppInstantiation()
        PrintFn("  ✓ [2/3] LCARSControlApp Stations & Navigation: VERIFIED")
        SuiteInstance.VerifyTitaniumIntegrity()
        PrintFn("  ✓ [3/3] Zero-Except Architectural Integrity: VERIFIED")
        PrintFn("============================================================================")
        PrintFn("◤ ALL 3 CONTROL SUITE CHECKS COMPLETED // NOMINAL 🖖")
        PrintFn("============================================================================")


ArgvList = getattr(SysModule, "argv", [])
IsPytestActive = any("pytest" in ArgItem for ArgItem in ArgvList)
if not IsPytestActive:
    ControlSuite.RunAll()
