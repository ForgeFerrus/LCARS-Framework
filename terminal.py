
# ◤ TITANIUM LCARS :: MASTER SYSTEM BOOTSTRAP 🖖
# =============================================================================
# ФАЙЛ: terminal.py
# ПРИЗНАЧЕННЯ: Єдина точка запуску LCARS Board Computer.
#
# terminal.py НЕ реалізує систему.
# Він лише:
#   1. готує процес;
#   2. запускає BoardComputer;
#   3. встановлює аварійні перехоплювачі;
#   4. обирає CLI або графічний PADD;
#   5. передає керування відповідному інтерфейсу.
#
# =============================================================================

from lcars.base.type import LCARS
from lcars.core.computer import BoardComputer
from lcars.service.console import LCARSConsole


def GetSystemModule():
    return LCARS.Import("sys")


def ConfigureProcess():
    SysModule = GetSystemModule()

    if SysModule is None:
        return None

    if hasattr(SysModule.stdout, "reconfigure"):
        SysModule.stdout.reconfigure(encoding="utf-8")

    if hasattr(SysModule.stdin, "reconfigure"):
        SysModule.stdin.reconfigure(encoding="utf-8")

    return SysModule


def GetArguments(SysModule):
    if SysModule is None or not hasattr(SysModule, "argv"):
        return []

    return SysModule.argv[1:]


def GetDirectCommand(ArgList):
    if "--cmd" in ArgList:
        Index = ArgList.index("--cmd")
        if Index + 1 < len(ArgList):
            return ArgList[Index + 1]

    if "-e" in ArgList:
        Index = ArgList.index("-e")
        if Index + 1 < len(ArgList):
            return ArgList[Index + 1]

    CommandArgs = [Arg for Arg in ArgList if not Arg.startswith("-")]

    if CommandArgs:
        return " ".join(CommandArgs)

    return None


def IsCliMode(ArgList):
    return (
        "--cli" in ArgList
        or "-cli" in ArgList
        or "-c" in ArgList
    )


def IsDesktopMode(ArgList):
    return (
        "--desktop" in ArgList
        or "-desktop" in ArgList
        or "-d" in ArgList
    )


def IsGuiMode(ArgList):
    return not IsCliMode(ArgList)


def InstallEmergencyHooks(SysModule):
    if SysModule is None:
        return

    def EmergencyCatcher(ExcType, ExcValue, ExcTraceback):
        TracebackModule = LCARS.Import("traceback")

        if TracebackModule and hasattr(TracebackModule, "print_exception"):
            TracebackModule.print_exception(
                ExcType,
                ExcValue,
                ExcTraceback
            )

        ErrName = getattr(ExcType, "__name__", "SystemFault")
        ErrText = f"{ErrName}: {ExcValue}"

        print(
            f"\n◤ SYSTEM ANOMALY LOGGED 🖖 // {ErrText}\n",
            flush=True
        )

        from lcars.core.signal import ODN
        ODN.Transmit("System.SystemFault", Error=ErrText)

    SysModule.excepthook = EmergencyCatcher

    ThreadingModule = LCARS.Import("threading")

    if ThreadingModule is None or not hasattr(
        ThreadingModule,
        "excepthook"
    ):
        return

    def ThreadEmergencyCatcher(Args):
        TracebackModule = LCARS.Import("traceback")

        if TracebackModule and hasattr(TracebackModule, "print_exception"):
            TracebackModule.print_exception(
                Args.exc_type,
                Args.exc_value,
                Args.exc_traceback
            )

        ThreadName = getattr(
            Args.thread,
            "name",
            "SubspaceWorker"
        )

        ErrName = getattr(
            Args.exc_type,
            "__name__",
            "ThreadFault"
        )

        ErrText = (
            f"Thread [{ThreadName}] - "
            f"{ErrName}: {Args.exc_value}"
        )

        print(
            f"\n◤ THREAD ANOMALY LOGGED 🖖 // {ErrText}\n",
            flush=True
        )

        from lcars.core.signal import ODN
        ODN.Transmit(
            "System.ThreadFault",
            Error=ErrText
        )

    ThreadingModule.excepthook = ThreadEmergencyCatcher


def BootBoardComputer():
    print(
        ">> [PHASE 1/3] BOOTING ONBOARD QUANTUM INTELLIGENCE CORE...",
        flush=True
    )

    Board = BoardComputer.GetInstance()

    print(
        f"   ✓ SHIP REGISTRY : "
        f"{getattr(Board, 'ShipRegistry', 'UNKNOWN')} "
        f"[{getattr(Board, 'ShipClass', 'UNKNOWN')}]",
        flush=True
    )

    print(
        f"   ✓ RUNTIME MODE  : "
        f"{getattr(Board, 'RuntimeMode', 'UNKNOWN')} "
        f"PROCESSOR ONLINE",
        flush=True
    )

    Subsystems = getattr(Board, "Subsystems", {})

    print(
        f"   ✓ SUBSYSTEMS    : "
        f"{len(Subsystems)} CHANNELS NOMINAL",
        flush=True
    )

    return Board


def RunDirectCommand(Board, CommandText):
    Console = LCARSConsole(BoardComputer=Board)

    print(
        f">> [DIRECTIVE INITIATED]: {CommandText}",
        flush=True
    )

    Console.Execute(
        CommandText,
        lambda Line: print(Line, flush=True)
    )


def RunCli(Board, SysModule):
    Console = LCARSConsole(BoardComputer=Board)

    print("=" * 76, flush=True)
    print(
        "◤ STARFLEET ODN CARRIER INITIALIZATION // "
        "BOARD COMPUTER ONLINE 🖖",
        flush=True
    )
    print("=" * 76, flush=True)

    print(
        ">> TERMINAL SUBSPACE CONDUIT ESTABLISHED.",
        flush=True
    )
    print(
        "  Type 'help' for command matrix, 'status', "
        "'diag', or natural directives.",
        flush=True
    )
    print(
        "  Type 'exit' or 'quit' to terminate subspace link.",
        flush=True
    )

    while True:
        if SysModule and hasattr(SysModule.stdout, "write"):
            SysModule.stdout.write("LCARS: ")
            SysModule.stdout.flush()

        RawLine = (
            SysModule.stdin.readline()
            if SysModule and hasattr(SysModule.stdin, "readline")
            else ""
        )

        if not RawLine:
            break

        CommandInput = RawLine.strip()

        if not CommandInput:
            continue

        if CommandInput.lower() in (
            "exit",
            "quit",
            "shutdown"
        ):
            print(
                ">> Terminating subspace link. "
                "Board Computer standing by.",
                flush=True
            )
            break

        Console.Execute(
            CommandInput,
            lambda Line: print(Line, flush=True)
        )


def RunGui(Board, ArgList, SysModule):
    Application = getattr(LCARS, "Application", None)

    if Application is None:
        print(
            "◤ GRAPHICAL APPLICATION CORE UNAVAILABLE.",
            flush=True
        )
        RunCli(Board, SysModule)
        return

    App = Application.instance()

    if App is None:
        App = Application(ArgList)

    if IsDesktopMode(ArgList):
        print(
            ">> [PHASE 2/3] "
            "INITIALIZING MISSION CONTROL DESKTOP...",
            flush=True
        )

        from lcars.ui.screen.desktop import LCARSDesktop

        ActiveWindow = LCARSDesktop(
            BoardComputer=Board
        )

    else:
        print(
            ">> [PHASE 2/3] "
            "INITIALIZING LCARS PADD TERMINAL...",
            flush=True
        )

        from lcars.ui.terminal import LCARSTerminal

        ActiveWindow = LCARSTerminal(
            BoardComputer=Board,
            portable=True
        )

    print(
        ">> [PHASE 3/3] LCARS INTERFACE ACTIVE.",
        flush=True
    )

    ActiveWindow.show()

    if hasattr(App, "exec"):
        return App.exec()

    if hasattr(App, "exec_"):
        return App.exec_()

    return 0


def RunBootstrap():
    SysModule = ConfigureProcess()
    ArgList = GetArguments(SysModule)

    InstallEmergencyHooks(SysModule)

    DirectCommand = GetDirectCommand(ArgList)

    Board = BootBoardComputer()

    if DirectCommand:
        RunDirectCommand(Board, DirectCommand)
        return 0

    if IsGuiMode(ArgList):
        return RunGui(
            Board,
            ArgList,
            SysModule
        )

    RunCli(
        Board,
        SysModule
    )

    return 0


def RunSystemSelfTest():
    print("=" * 76, flush=True)
    print(
        "◤ LCARS BOARD COMPUTER SELF-TEST 🖖",
        flush=True
    )
    print("=" * 76, flush=True)

    print(
        ">> [TEST 1/4] BOARD COMPUTER BOOT...",
        flush=True
    )

    Board = BoardComputer.GetInstance()

    assert Board is not None
    assert len(getattr(Board, "Subsystems", {})) > 0

    print("   ✓ BOARD COMPUTER: ONLINE", flush=True)

    print(
        ">> [TEST 2/4] SUBSYSTEM STATE...",
        flush=True
    )

    from lcars.core.computer import SubsystemState

    WarpState = Board.GetSubsystemState("WarpCore")

    assert SubsystemState.IsOperational(WarpState)

    print(
        f"   ✓ WARP CORE: {WarpState}",
        flush=True
    )

    print(
        ">> [TEST 3/4] ODN TRANSMISSION...",
        flush=True
    )

    from lcars.core.signal import ODN

    ZeroArgFired = [False]
    OneArgFired = [False]

    def ZeroArgHandler():
        ZeroArgFired[0] = True

    def OneArgHandler(Packet):
        OneArgFired[0] = True

    ODN.Connect(
        "Test.ZeroArgChannel",
        ZeroArgHandler
    )

    ODN.Connect(
        "Test.OneArgChannel",
        OneArgHandler
    )

    ODN.Transmit(
        "Test.ZeroArgChannel"
    )

    ODN.Transmit(
        "Test.OneArgChannel",
        Payload="Active"
    )

    assert ZeroArgFired[0]
    assert OneArgFired[0]

    ODN.Disconnect(
        "Test.ZeroArgChannel",
        ZeroArgHandler
    )

    ODN.Disconnect(
        "Test.OneArgChannel",
        OneArgHandler
    )

    print(
        "   ✓ ODN: ONLINE",
        flush=True
    )

    print(
        ">> [TEST 4/4] LCARS CONSOLE...",
        flush=True
    )

    Console = LCARSConsole(
        BoardComputer=Board
    )

    OutputLines = []

    Console.Execute(
        "status",
        lambda Line: OutputLines.append(Line)
    )

    assert OutputLines

    print(
        "   ✓ CONSOLE: ONLINE",
        flush=True
    )

    print("=" * 76, flush=True)
    print(
        "◤ ALL CORE SELF-TESTS PASSED 🖖",
        flush=True
    )
    print("=" * 76, flush=True)

RunBootstrap()

if __name__ == "__main__":
    RunSystemSelfTest()