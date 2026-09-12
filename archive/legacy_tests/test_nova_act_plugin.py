# ◤ TITANIUM LCARS :: NOVA SYSTEM & ACT PLUGIN TEST SUITE 🖖
# =============================================================================
# ФАЙЛ: tests/test_nova_act_plugin.py
# ПРИЗНАЧЕННЯ: Повне тестування середовища Nova IDE, NovaAdapter та інтеграції з бортовим комп'ютером.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase).
# =============================================================================

from lcars.base.type import LCARS

SysModule = LCARS.Import("sys")
if hasattr(SysModule.stdout, "reconfigure"):
    SysModule.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(SysModule.stderr, "reconfigure"):
    SysModule.stderr.reconfigure(encoding="utf-8", errors="replace")


class TestNovaSystem:
    def TestNovaPanelIsLcarsShell(self):
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

    def TestNovaAdapterScriptsResolution(self):
        Path = LCARS.Import("pathlib").Path
        AdapterModule = LCARS.Import("programs.Nova.sdk.adapter")
        AdapterInstance = AdapterModule.NovaAdapter.__new__(AdapterModule.NovaAdapter)
        ServerScript = Path(AdapterInstance.ResolveServerScript())
        CliScript = Path(AdapterInstance.ResolveCliScript())
        assert ServerScript.name == "server.mjs"
        assert CliScript.name == "cli.mjs"
        assert ServerScript.exists()
        assert CliScript.exists()

    def TestNovaExecuteAction(self):
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

    def TestNovaExecuteTool(self):
        Json = LCARS.Import("json")
        AdapterModule = LCARS.Import("programs.Nova.sdk.adapter")
        AdapterInstance = AdapterModule.NovaAdapter()
        ToolResult = AdapterInstance.ExecuteTool("GetSystemStatus", {})
        assert isinstance(ToolResult, str)
        ParsedResult = Json.loads(ToolResult)
        assert isinstance(ParsedResult, dict)
        assert ParsedResult.get("State") == "NOMINAL"
        assert "NCC-74205" in ParsedResult.get("Ship", "")

    def TestNovaBoardComputerIntegration(self):
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

    @classmethod
    def RunAllTests(cls):
        PrintFn = print
        PrintFn("=" * 76)
        PrintFn("◤ RUNNING TITANIUM NOVA SYSTEM & ACT PLUGIN TEST SUITE 🖖")
        PrintFn("============================================================================")
        TestInstance = cls()
        TestInstance.TestNovaPanelIsLcarsShell()
        PrintFn("  ✓ [1/5] NovaPanel LCARS Shell Workbench: PASSED")
        TestInstance.TestNovaAdapterScriptsResolution()
        PrintFn("  ✓ [2/5] NovaAdapter QVAC Script Resolution (server.mjs, cli.mjs): PASSED")
        TestInstance.TestNovaExecuteAction()
        PrintFn("  ✓ [3/5] NovaAdapter ExecuteAction (health, forget): PASSED")
        TestInstance.TestNovaExecuteTool()
        PrintFn("  ✓ [4/5] NovaAdapter ExecuteTool (GetSystemStatus): PASSED")
        TestInstance.TestNovaBoardComputerIntegration()
        PrintFn("  ✓ [5/5] BoardComputer LaunchInterface('NOVA'): PASSED")
        PrintFn("============================================================================")
        PrintFn("◤ ALL 5 NOVA SYSTEM TESTS PASSED SUCCESSFULLY // OPERATIONAL 🖖")
        PrintFn("============================================================================")


SysModule = LCARS.Import("sys")
ArgvList = getattr(SysModule, "argv", [])
IsPytestActive = any("pytest" in ArgItem for ArgItem in ArgvList)
if not IsPytestActive:
    TestNovaSystem.RunAllTests()


