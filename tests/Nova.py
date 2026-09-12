# ◤ TITANIUM LCARS :: NOVA SUITE 🖖
# =============================================================================
# ФАЙЛ: tests/Nova.py
# ПРИЗНАЧЕННЯ: Комплексна верифікація робочого простору Nova та QVAC адаптера.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase).
# =============================================================================

from lcars.base.type import LCARS

SysModule = LCARS.Import("sys")
if hasattr(SysModule.stdout, "reconfigure"):
    SysModule.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(SysModule.stderr, "reconfigure"):
    SysModule.stderr.reconfigure(encoding="utf-8", errors="replace")


class NovaSuite:
    def VerifyWorkbenchShell(self):
        BaseApp = LCARS.Application
        App = BaseApp.instance() if hasattr(BaseApp, "instance") else None
        if App is None and callable(BaseApp):
            App = BaseApp([])
        NovaModule = LCARS.Import("programs.Nova.ide")
        PanelInstance = NovaModule.NovaPanel()
        assert getattr(PanelInstance, "ThemeName", "") == "LCARS"
        assert getattr(PanelInstance, "LayoutMode", "") == "command-console"
        assert hasattr(PanelInstance, "Sidebar")
        assert hasattr(PanelInstance, "RightPane")
        assert hasattr(PanelInstance, "PreviewPane")
        assert hasattr(PanelInstance, "SdkPanel")

    def VerifyScriptResolution(self):
        PathHelper = LCARS.Import("pathlib").Path
        AdapterModule = LCARS.Import("programs.Nova.sdk.adapter")
        AdapterInstance = AdapterModule.NovaAdapter.__new__(AdapterModule.NovaAdapter)
        ServerScript = PathHelper(AdapterInstance.ResolveServerScript())
        CliScript = PathHelper(AdapterInstance.ResolveCliScript())
        assert ServerScript.name == "network.py"
        assert CliScript.name == "cli.mjs"
        assert ServerScript.exists()
        assert CliScript.exists()

    def VerifyActionDispatch(self):
        AdapterModule = LCARS.Import("programs.Nova.sdk.adapter")
        AdapterInstance = AdapterModule.NovaAdapter()
        HealthResult = AdapterInstance.ExecuteAction("health")
        assert isinstance(HealthResult, dict)
        assert "result" in HealthResult
        HealthPayload = HealthResult["result"]
        assert isinstance(HealthPayload, dict)
        assert HealthPayload.get("name") == "nova"
        assert HealthPayload.get("transport") == "http"

        ForgetResult = AdapterInstance.ExecuteAction("forget")
        assert isinstance(ForgetResult, dict)
        assert ForgetResult.get("result") == "Memory cleared"

    def VerifyDiagnosticsTool(self):
        JsonHelper = LCARS.Import("json")
        AdapterModule = LCARS.Import("programs.Nova.sdk.adapter")
        AdapterInstance = AdapterModule.NovaAdapter()
        ToolResult = AdapterInstance.ExecuteTool("GetSystemStatus", {})
        assert isinstance(ToolResult, str)
        ParsedResult = JsonHelper.loads(ToolResult)
        assert isinstance(ParsedResult, dict)
        assert ParsedResult.get("State") == "NOMINAL"
        assert "NCC-74205" in ParsedResult.get("Ship", "")

    def VerifyConsoleExecution(self):
        PathHelper = LCARS.Import("pathlib").Path
        ConsoleModule = LCARS.Import("lcars.service.console")
        ConsoleInstance = ConsoleModule.LCARSConsole()
        TempPath = PathHelper("probe.py")
        TempPath.write_text("print('NOVA_PROBE_ONLINE')\n", encoding="utf-8")
        ConsoleOutput = ConsoleInstance.RunCommand(f"run {TempPath}")
        if TempPath.exists():
            TempPath.unlink()
        assert "NOVA_PROBE_ONLINE" in ConsoleOutput
        assert "LCARS PYTHON: EXIT 0" in ConsoleOutput

    def VerifyComputerInterface(self):
        BaseApp = LCARS.Application
        App = BaseApp.instance() if hasattr(BaseApp, "instance") else None
        if App is None and callable(BaseApp):
            App = BaseApp([])
        ComputerModule = LCARS.Import("lcars.core.computer")
        ComputerInstance = ComputerModule.BoardComputer.GetInstance()
        ComputerInstance.InitializeSystem()
        ComputerInstance.LaunchInterface("NOVA", Show=False)
        assert "NOVA" in ComputerInstance.ActiveInterfaces
        InterfaceData = ComputerInstance.ActiveInterfaces["NOVA"]
        assert InterfaceData.get("Status") == "ACTIVE"
        assert InterfaceData.get("Screen") is not None

    def VerifyReplicatorAndSynthesis(self):
        BaseApp = LCARS.Application
        App = BaseApp.instance() if hasattr(BaseApp, "instance") else None
        if App is None and callable(BaseApp):
            App = BaseApp([])
        ReplicatorModule = LCARS.Import("lcars.service.replicator")
        assert ReplicatorModule is not None
        Replicator = ReplicatorModule.LCARSReplicator.GetInstance()
        assert Replicator is not None
        assert "Primary" in Replicator.ActivePalette
        assert "Background" in Replicator.ActivePalette
        assert "EditorBg" in Replicator.ActivePalette
        assert "TerminalFg" in Replicator.ActivePalette
        assert len(Replicator.RegisteredPrimitives) > 0
        assert len(Replicator.RegisteredComponents) > 0

        ComputerModule = LCARS.Import("lcars.core.computer")
        Computer = ComputerModule.BoardComputer.GetInstance()
        Station = Computer.Synthesize("nova")
        assert Station is not None
        assert "NOVA" in Station.windowTitle()

    @classmethod
    def RunAll(cls):
        PrintFn = print
        PrintFn("=" * 76)
        PrintFn("◤ RUNNING TITANIUM NOVA SUITE 🖖")
        PrintFn("============================================================================")
        SuiteInstance = cls()
        SuiteInstance.VerifyWorkbenchShell()
        PrintFn("  ✓ [1/7] NovaPanel LCARS Shell Workbench: VERIFIED")
        SuiteInstance.VerifyScriptResolution()
        PrintFn("  ✓ [2/7] Canonical Network Gateway and QVAC CLI resolution: VERIFIED")
        SuiteInstance.VerifyActionDispatch()
        PrintFn("  ✓ [3/7] NovaAdapter Action Dispatch (health, forget): VERIFIED")
        SuiteInstance.VerifyDiagnosticsTool()
        PrintFn("  ✓ [4/7] NovaAdapter Core Diagnostics Tool: VERIFIED")
        SuiteInstance.VerifyConsoleExecution()
        PrintFn("  ✓ [5/7] LCARS Console Execution: VERIFIED")
        SuiteInstance.VerifyComputerInterface()
        PrintFn("  ✓ [6/7] BoardComputer LaunchInterface('NOVA'): VERIFIED")
        SuiteInstance.VerifyReplicatorAndSynthesis()
        PrintFn("  ✓ [7/7] LCARSReplicator Service & Synthesis: VERIFIED")
        PrintFn("============================================================================")
        PrintFn("◤ ALL 7 NOVA SUITE CHECKS COMPLETED // NOMINAL 🖖")
        PrintFn("============================================================================")



ArgvList = getattr(SysModule, "argv", [])
IsPytestActive = any("pytest" in ArgItem for ArgItem in ArgvList)
if not IsPytestActive:
    NovaSuite.RunAll()
