# ◤ TITANIUM LCARS :: TERMINAL SUITE 🖖
# =============================================================================
# ФАЙЛ: tests/Terminal.py
# ПРИЗНАЧЕННЯ: Комплексна верифікація терміналу, комп'ютера, підсистем та шини ODN.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase).
# =============================================================================

from lcars.base.type import LCARS

SysModule = LCARS.Import("sys")
if hasattr(SysModule.stdout, "reconfigure"):
    SysModule.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(SysModule.stderr, "reconfigure"):
    SysModule.stderr.reconfigure(encoding="utf-8", errors="replace")


class TerminalSuite:
    def VerifyMasterSystemBoot(self):
        SystemModule = LCARS.Import("lcars.core.system")
        SystemInstance = SystemModule.MasterSystem.GetInstance()
        assert SystemInstance is not None
        assert hasattr(SystemInstance, "Services")
        assert hasattr(SystemInstance, "Modules")
        assert len(SystemInstance.Services.Services) >= 8
        assert len(SystemInstance.Modules) >= 15

    def VerifyBoardComputerSingleton(self):
        ComputerModule = LCARS.Import("lcars.core.computer")
        BoardPrimary = ComputerModule.BoardComputer.GetInstance()
        BoardSecondary = ComputerModule.BoardComputer.GetInstance()
        assert BoardPrimary is BoardSecondary
        BoardPrimary.InitializeSystem()
        assert BoardPrimary.ShipRegistry == "NCC-74205"
        assert "Sovereign" in BoardPrimary.ShipClass
        assert len(BoardPrimary.Subsystems) == 13

    def VerifySubsystemMatrixAndStates(self):
        ComputerModule = LCARS.Import("lcars.core.computer")
        BoardInstance = ComputerModule.BoardComputer.GetInstance()
        SubsystemState = ComputerModule.SubsystemState
        BoardInstance.InitializeSystem()
        WarpState = BoardInstance.GetSubsystemState("WarpCore")
        assert SubsystemState.IsOperational(WarpState)

        BoardInstance.SetSubsystemState("WarpCore", SubsystemState.Offline)
        assert BoardInstance.GetSubsystemState("WarpCore") == SubsystemState.Offline
        BoardInstance.SetSubsystemState("WarpCore", SubsystemState.Online)
        assert BoardInstance.GetSubsystemState("WarpCore") == SubsystemState.Online

    def VerifyODNSignalBus(self):
        SignalModule = LCARS.Import("lcars.core.signal")
        ODNBus = SignalModule.ODN
        ZeroFired = [False]
        OneFired = [False]
        PacketContent = [{}]

        def ZeroCallback():
            ZeroFired[0] = True

        def OneCallback(PacketItem):
            OneFired[0] = True
            PacketContent[0] = getattr(PacketItem, "Flags", {})

        ODNBus.Connect("Ship.ZeroArgChannel", ZeroCallback)
        ODNBus.Connect("Ship.OneArgChannel", OneCallback)

        ODNBus.Transmit("Ship.ZeroArgChannel")
        ODNBus.Transmit("Ship.OneArgChannel", Payload="ActiveTransmission", Value=1701)

        assert ZeroFired[0]
        assert OneFired[0]
        assert PacketContent[0].get("Value") == 1701

        ODNBus.Disconnect("Ship.ZeroArgChannel", ZeroCallback)
        ODNBus.Disconnect("Ship.OneArgChannel", OneCallback)

    def VerifyConsoleDirectives(self):
        ComputerModule = LCARS.Import("lcars.core.computer")
        ConsoleModule = LCARS.Import("lcars.service.console")
        BoardInstance = ComputerModule.BoardComputer.GetInstance()
        BoardInstance.InitializeSystem()
        ConsoleInstance = ConsoleModule.LCARSConsole(BoardComputer=BoardInstance)

        DirectivesList = [
            "status",
            "Run Diagnostics POST",
            "Run Diagnostic Full",
            "Status ODN",
            "Scan Sensors LongRange",
        ]

        for DirectiveItem in DirectivesList:
            OutputsList = []
            ConsoleInstance.Execute(DirectiveItem, lambda OutputLine: OutputsList.append(OutputLine))
            assert len(OutputsList) > 0
            CombinedOutput = " ".join(OutputsList)
            assert "ERROR" not in CombinedOutput.upper() or "[OK]" in CombinedOutput or "ONLINE" in CombinedOutput or "NOMINAL" in CombinedOutput

    def VerifyTerminalInterface(self):
        BaseApp = LCARS.Application
        App = BaseApp.instance() if hasattr(BaseApp, "instance") else None
        if App is None and callable(BaseApp):
            App = BaseApp([])

        ComputerModule = LCARS.Import("lcars.core.computer")
        TerminalModule = LCARS.Import("lcars.ui.terminal")
        BoardInstance = ComputerModule.BoardComputer.GetInstance()
        BoardInstance.InitializeSystem()

        TerminalInstance = TerminalModule.LCARSTerminal(BoardComputer=BoardInstance, portable=True)
        assert TerminalInstance is not None
        assert TerminalInstance.widget is not None
        assert hasattr(TerminalInstance, "Output")
        assert hasattr(TerminalInstance, "BoardComputer")

        TerminalInstance.TriggerEmergency("Simulated ODN Phase Disruption")
        assert TerminalInstance.IsEmergency is True

        TerminalInstance.close()

    def VerifyZeroExceptIntegrity(self):
        PathHelper = LCARS.Import("pathlib").Path
        ProjectRoot = PathHelper(__file__).resolve().parents[1]
        TerminalFile = ProjectRoot / "terminal.py"
        ComputerFile = ProjectRoot / "lcars" / "core" / "computer.py"

        TerminalLines = [LineItem for LineItem in TerminalFile.read_text(encoding="utf-8").splitlines() if LineItem.strip().startswith("except ")]
        ComputerLines = [LineItem for LineItem in ComputerFile.read_text(encoding="utf-8").splitlines() if LineItem.strip().startswith("except ")]

        assert len(TerminalLines) == 0
        assert len(ComputerLines) == 0

    @classmethod
    def RunAll(cls):
        PrintFn = print
        PrintFn("=" * 76)
        PrintFn("◤ RUNNING TITANIUM TERMINAL SUITE 🖖")
        PrintFn("============================================================================")
        SuiteInstance = cls()
        SuiteInstance.VerifyMasterSystemBoot()
        PrintFn("  ✓ [1/7] MasterSystem Boot: VERIFIED")
        SuiteInstance.VerifyBoardComputerSingleton()
        PrintFn("  ✓ [2/7] BoardComputer Singleton & Identity: VERIFIED")
        SuiteInstance.VerifySubsystemMatrixAndStates()
        PrintFn("  ✓ [3/7] Subsystem Matrix & State Toggles: VERIFIED")
        SuiteInstance.VerifyODNSignalBus()
        PrintFn("  ✓ [4/7] ODN Signal Bus (Zero-Except): VERIFIED")
        SuiteInstance.VerifyConsoleDirectives()
        PrintFn("  ✓ [5/7] LCARS Console Directives Execution: VERIFIED")
        SuiteInstance.VerifyTerminalInterface()
        PrintFn("  ✓ [6/7] Terminal UI & Emergency Intercept: VERIFIED")
        SuiteInstance.VerifyZeroExceptIntegrity()
        PrintFn("  ✓ [7/7] Zero-Except Architectural Integrity: VERIFIED")
        PrintFn("============================================================================")
        PrintFn("◤ ALL 7 TERMINAL SUITE CHECKS COMPLETED // NOMINAL 🖖")
        PrintFn("============================================================================")


ArgvList = getattr(SysModule, "argv", [])
IsPytestActive = any("pytest" in ArgItem for ArgItem in ArgvList)
if not IsPytestActive:
    TerminalSuite.RunAll()

