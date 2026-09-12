# ◤ TITANIUM LCARS :: DESKTOP SUITE 🖖
# =============================================================================
# ФАЙЛ: tests/Desktop.py
# ПРИЗНАЧЕННЯ: Комплексна верифікація LCARS Mission Control Desktop,
#              провайдера OpenRouter, станцій сайдбару та ODN шини.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase).
# =============================================================================

from lcars.base.type import LCARS

SysModule = LCARS.Import("sys")
if hasattr(SysModule.stdout, "reconfigure"):
    SysModule.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(SysModule.stderr, "reconfigure"):
    SysModule.stderr.reconfigure(encoding="utf-8", errors="replace")


class DesktopSuite:
    def VerifyOpenRouterProvider(self):
        ProviderModule = LCARS.Import("lcars.service.provider")
        assert hasattr(ProviderModule, "OpenRouterProvider")
        OpenRouterCls = ProviderModule.OpenRouterProvider
        Instance = OpenRouterCls()
        assert Instance.Name == "openrouter"
        assert Instance.BaseUrl == "https://openrouter.ai/api/v1"
        assert len(Instance.GetAvailableModels()) >= 4
        assert "anthropic/claude-3.5-sonnet" in Instance.GetAvailableModels()

        AiManager = ProviderModule.AIProviderManager.GetInstance()
        assert AiManager is not None
        FoundOpenRouter = any(B.Name == "openrouter" for B in AiManager.Backends)
        assert FoundOpenRouter is True

        Switched = AiManager.SwitchModel("openrouter")
        assert Switched is True
        assert AiManager.ActiveBackend.Name == "openrouter"

    def VerifyDesktopStationsAndNavigation(self):
        BaseApp = LCARS.Application
        App = BaseApp.instance() if hasattr(BaseApp, "instance") else None
        if App is None and callable(BaseApp):
            App = BaseApp([])

        ComputerModule = LCARS.Import("lcars.core.computer")
        DesktopModule = LCARS.Import("lcars.ui.screen.desktop")
        BoardInstance = ComputerModule.BoardComputer.GetInstance()
        BoardInstance.InitializeSystem()

        DesktopInstance = DesktopModule.LCARSDesktop(BoardComputer=BoardInstance)
        assert DesktopInstance is not None
        assert DesktopInstance.widget is not None
        assert DesktopInstance.GatewayPort in (3055, 3688)
        assert DesktopInstance.ProcessorMode == "QUANTUM"

        # Перевірка логування
        InitialLogCount = len(DesktopInstance.LogsList)
        DesktopInstance.Log(">> Test ODN Carrier Transmission")
        assert len(DesktopInstance.LogsList) == InitialLogCount + 1

        # Перевірка станцій
        DesktopInstance.Select("STATUS")
        assert DesktopInstance.ActivePage == "STATUS"
        assert DesktopInstance.DaemonLogBox is not None

        DesktopInstance.Select("AGENTS")
        assert DesktopInstance.ActivePage == "AGENTS"

        DesktopInstance.Select("PROVIDERS")
        assert DesktopInstance.ActivePage == "PROVIDERS"

        DesktopInstance.Select("PROJECTS")
        assert DesktopInstance.ActivePage == "PROJECTS"
        assert DesktopInstance.ProjectOutputBox is not None

        DesktopInstance.Select("COCKPIT")
        assert DesktopInstance.ActivePage == "COCKPIT"
        assert DesktopInstance.CockpitResponseBox is not None

        # Перемикання режиму процесора
        DesktopInstance.ToggleProcessorMode()
        assert DesktopInstance.ProcessorMode == "OPTICAL"
        DesktopInstance.ToggleProcessorMode()
        assert DesktopInstance.ProcessorMode == "QUANTUM"

        DesktopInstance.widget.close()

    def VerifyZeroExceptIntegrity(self):
        PathHelper = LCARS.Import("pathlib").Path
        ProjectRoot = PathHelper(__file__).resolve().parents[1]
        DesktopFile = ProjectRoot / "lcars" / "ui" / "screen" / "desktop.py"

        DesktopLines = [LineItem for LineItem in DesktopFile.read_text(encoding="utf-8").splitlines() if LineItem.strip().startswith("except ")]
        assert len(DesktopLines) == 0

    @classmethod
    def RunAll(cls):
        PrintFn = print
        PrintFn("=" * 76)
        PrintFn("◤ RUNNING TITANIUM DESKTOP SUITE 🖖")
        PrintFn("============================================================================")
        SuiteInstance = cls()
        SuiteInstance.VerifyOpenRouterProvider()
        PrintFn("  ✓ [1/3] OpenRouter Provider Registration: VERIFIED")
        SuiteInstance.VerifyDesktopStationsAndNavigation()
        PrintFn("  ✓ [2/3] Desktop Stations & Navigation: VERIFIED")
        SuiteInstance.VerifyZeroExceptIntegrity()
        PrintFn("  ✓ [3/3] Zero-Except Architectural Integrity: VERIFIED")
        PrintFn("============================================================================")
        PrintFn("◤ ALL 3 DESKTOP SUITE CHECKS COMPLETED // NOMINAL 🖖")
        PrintFn("============================================================================")


ArgvList = getattr(SysModule, "argv", [])
IsPytestActive = any("pytest" in ArgItem for ArgItem in ArgvList)
if not IsPytestActive:
    DesktopSuite.RunAll()

