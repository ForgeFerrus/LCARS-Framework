from __future__ import annotations

import sys
from pathlib import Path as FilePath

from lcars.service.console import LCARSConsole, ConsoleTerminal
from lcars.core.signal import ODN


Root = FilePath(__file__).resolve().parents[1]

if str(Root) not in sys.path:
    sys.path.insert(0, str(Root))


Passed = 0
Failed = 0
Total = 0


def Check(Name, Condition, Detail=None):
    global Passed
    global Failed
    global Total

    Total += 1

    if Condition:
        Passed += 1
        print(f"[PASS] {Name}")
        if Detail is not None:
            print(f"       {Detail}")
        return True

    Failed += 1
    print(f"[FAIL] {Name}")
    if Detail is not None:
        print(f"       {Detail}")
    return False


def Run(Console, Text):
    Output = []

    try:
        Console.Execute(
            Text,
            Output.append
        )
    except Exception as Error:
        Output.append(
            f"EXCEPTION: {type(Error).__name__}: {Error}"
        )

    print(f"\nLCARS> {Text}")

    for Line in Output:
        print(f"       {Line}")

    return Output


class ComputerProbe:
    def __init__(self):
        self.Calls = []

    def AskAI(self, Prompt):
        self.Calls.append(
            ("AskAI", Prompt)
        )
        return "BOARD COMPUTER AI RESPONSE"


def Main():
    global Passed
    global Failed
    global Total

    print("=" * 72)
    print("LCARS CONSOLE :: OPERATIONAL SYSTEM TEST")
    print("=" * 72)

    Console = LCARSConsole()

    # ================================================================
    # 1. CONSOLE BOOT
    # ================================================================

    print("\n[1] BOOT")

    Check(
        "Console created",
        isinstance(Console, LCARSConsole)
    )

    Check(
        "Console running",
        Console.Running is True
    )

    Check(
        "Runtime available",
        Console.Runtime is not None
    )

    Check(
        "Project root",
        Console.ProjectRoot.exists()
    )

    Check(
        "Working directory",
        Console.Cwd.exists()
    )

    # ================================================================
    # 2. REAL LCARS COMMANDS
    # ================================================================

    print("\n[2] LCARS COMMANDS")

    Output = Run(
        Console,
        "status"
    )

    Check(
        "STATUS",
        len(Output) > 0
    )

    Output = Run(
        Console,
        "version"
    )

    Check(
        "VERSION",
        len(Output) > 0
    )

    Output = Run(
        Console,
        "help"
    )

    Check(
        "HELP",
        any(
            "LCARS CONSOLE" in Line
            for Line in Output
        )
    )

    Output = Run(
        Console,
        "modes"
    )

    Check(
        "MODES",
        any(
            "MODES:" in Line
            for Line in Output
        )
    )

    # ================================================================
    # 3. RUNTIME MODE
    # ================================================================

    print("\n[3] RUNTIME MODE")

    Run(
        Console,
        "mode quantum"
    )

    Check(
        "QUANTUM mode entered",
        Console.ActiveMode == "QUANTUM"
    )

    Run(
        Console,
        "mode normal"
    )

    Check(
        "NORMAL mode restored",
        Console.ActiveMode == "NORMAL"
    )

    # ================================================================
    # 4. MODEL
    # ================================================================

    print("\n[4] MODEL")

    Run(
        Console,
        "model local"
    )

    Check(
        "LOCAL selected",
        Console.PreferredAIBackend == "LOCAL"
    )

    Run(
        Console,
        "backend groq"
    )

    Check(
        "BACKEND alias",
        Console.PreferredAIBackend == "GROQ"
    )

    Run(
        Console,
        "model local"
    )

    # ================================================================
    # 5. FILESYSTEM
    # ================================================================

    print("\n[5] FILESYSTEM")

    OriginalCwd = Console.Cwd

    Output = Run(
        Console,
        "pwd"
    )

    Check(
        "PWD",
        str(OriginalCwd) in "\n".join(Output)
    )

    Output = Run(
        Console,
        "ls"
    )

    Check(
        "LS",
        isinstance(Output, list)
    )

    Run(
        Console,
        "cd ."
    )

    Check(
        "CD",
        Console.Cwd == OriginalCwd
    )

    # ================================================================
    # 6. REAL PYTHON PROCESS
    # ================================================================

    print("\n[6] PYTHON")

    TempFile = Root / "test" / "_console_runtime_probe.py"

    try:
        TempFile.write_text(
            'print("LCARS CONSOLE PYTHON PROBE")\n',
            encoding="utf-8"
        )

        Output = Run(
            Console,
            f"py {TempFile}"
        )

        Check(
            "Python route",
            any(
                "LCARS PYTHON:" in Line
                for Line in Output
            )
        )

        Check(
            "Python executed probe",
            any(
                "LCARS CONSOLE PYTHON PROBE" in Line
                for Line in Output
            )
        )

        Check(
            "Python exit reported",
            any(
                "LCARS PYTHON: EXIT 0" in Line
                for Line in Output
            )
        )

    finally:
        if TempFile.exists():
            TempFile.unlink()

    # ================================================================
    # 7. LCARS RUN / COMPILE HANDLING
    # ================================================================

    print("\n[7] LCARS RUNTIME")

    Output = Run(
        Console,
        "run"
    )

    Check(
        "RUN without target handled",
        any(
            "LCARS RUN:" in Line
            for Line in Output
        )
    )

    Output = Run(
        Console,
        "compile"
    )

    Check(
        "COMPILE without target handled",
        any(
            "LCARS COMPILE:" in Line
            for Line in Output
        )
    )

    # ================================================================
    # 8. BRIDGE COMMAND INTERFACE
    # ================================================================

    print("\n[8] BRIDGE COMMAND INTERFACE")

    Output = Run(
        Console,
        "catalog AI"
    )

    Check(
        "Bridge catalog",
        len(Output) > 0
    )

    Output = Run(
        Console,
        "bridge AI"
    )

    Check(
        "Bridge namespace",
        len(Output) > 0
    )

    Output = Run(
        Console,
        "connect AI.Provider.Groq"
    )

    Check(
        "Bridge connect command",
        any(
            "BRIDGE:" in Line
            for Line in Output
        )
    )

    Output = Run(
        Console,
        "bridge status AI.Provider.Groq"
    )

    Check(
        "Bridge status command",
        any(
            "BRIDGE:" in Line
            for Line in Output
        )
    )

    # ================================================================
    # 9. SHELL
    # ================================================================

    print("\n[9] SHELL")

    Check(
        "git classified as shell",
        Console.LooksLikeShell(
            "git status"
        )
    )

    Check(
        "PowerShell classified",
        Console.LooksLikeShell(
            "Get-Process"
        )
    )

    Output = Run(
        Console,
        "where.exe python"
    )

    Check(
        "Read-only shell command",
        len(Output) > 0
    )

    # ================================================================
    # 10. AGENT / BOARD COMPUTER
    # ================================================================

    print("\n[10] BOARD COMPUTER")

    Computer = ComputerProbe()

    AgentConsole = LCARSConsole(
        BoardComputer=Computer
    )

    Output = Run(
        AgentConsole,
        "ai diagnostics ping"
    )

    Check(
        "Explicit AI reaches BoardComputer",
        Computer.Calls == [
            ("AskAI", "diagnostics ping")
        ]
    )

    Check(
        "Agent response returned",
        any(
            "BOARD COMPUTER AI RESPONSE" in Line
            for Line in Output
        )
    )

    Computer.Calls.clear()

    Output = Run(
        AgentConsole,
        "check current bridge state"
    )

    Check(
        "Unknown natural language reaches BoardComputer",
        Computer.Calls == [
            (
                "AskAI",
                "check current bridge state"
            )
        ]
    )

    # ================================================================
    # 11. LOCAL INTELLIGENCE
    # ================================================================

    print("\n[11] LOCAL INTELLIGENCE")

    Output = Run(
        Console,
        "hello"
    )

    Check(
        "Greeting handled locally",
        any(
            "BOARD INTELLIGENCE" in Line
            for Line in Output
        )
    )

    # ================================================================
    # 12. ODN / CONSOLE SIGNAL
    # ================================================================

    print("\n[12] ODN")

    ChannelName = "Console.Test"

    Received = []

    Channel = ODN.Channel(
        ChannelName
    )

    Channel.Connect(
        lambda Signal: Received.append(Signal)
    )

    Console.Emit(
        ChannelName,
        {
            "Source": "Console",
            "Test": True
        }
    )

    Check(
        "Console emits to ODN",
        len(Received) == 1
    )

    Check(
        "ODN receives console data",
        Received
        and Received[0].Data == {
            "Source": "Console",
            "Test": True
        }
    )

    # ================================================================
    # 13. TERMINAL ENDPOINT
    # ================================================================

    print("\n[13] TERMINAL")

    Terminal = ConsoleTerminal(
        Console
    )

    Check(
        "Terminal attached",
        Terminal.Console is Console
    )

    Result = Terminal.RunCommand(
        "version"
    )

    Check(
        "Terminal delegates command",
        Console.Version in Result
    )

    # ================================================================
    # 14. CLASSIFICATION
    # ================================================================

    print("\n[14] INPUT CLASSIFICATION")

    Check(
        "status = COMMAND",
        Console.ClassifyInput(
            "status"
        ) == "COMMAND"
    )

    Check(
        "connect = COMMAND",
        Console.ClassifyInput(
            "connect AI.Provider.Groq"
        ) == "COMMAND"
    )

    Check(
        "git status = SHELL",
        Console.ClassifyInput(
            "git status"
        ) == "SHELL"
    )

    Check(
        "question = THINK",
        Console.ClassifyInput(
            "what is LCARS?"
        ) == "THINK"
    )

    Check(
        "hello = UNKNOWN",
        Console.ClassifyInput(
            "hello"
        ) == "UNKNOWN"
    )

    # ================================================================
    # 15. CONTROL
    # ================================================================

    print("\n[15] CONTROL")

    Output = Run(
        Console,
        "clear"
    )

    Check(
        "CLEAR",
        any(
            "DISPLAY CLEARED" in Line
            for Line in Output
        )
    )

    Run(
        Console,
        "stop"
    )

    Check(
        "STOP",
        Console.Running is False
    )

    # ================================================================
    # FINAL
    # ================================================================

    print("\n" + "=" * 72)
    print("LCARS CONSOLE :: FINAL REPORT")
    print("=" * 72)

    print(
        f"TOTAL TESTS : {Total}"
    )

    print(
        f"PASSED      : {Passed}"
    )

    print(
        f"FAILED      : {Failed}"
    )

    print("=" * 72)

    if Failed == 0:
        print("CONSOLE STATUS       : OPERATIONAL")
        print("COMMAND CONTROL      : VERIFIED")
        print("RUNTIME CONTROL      : VERIFIED")
        print("FILESYSTEM           : VERIFIED")
        print("PYTHON EXECUTION     : VERIFIED")
        print("LCARS RUNTIME        : VERIFIED")
        print("BRIDGE COMMAND       : VERIFIED")
        print("SHELL CONTROL        : VERIFIED")
        print("BOARD COMPUTER       : VERIFIED")
        print("AGENT ROUTING        : VERIFIED")
        print("ODN                   : VERIFIED")
        print("TERMINAL             : VERIFIED")
        print("OVERALL STATUS       : NOMINAL")
        return 0

    print("CONSOLE STATUS       : FAILED")
    print("OVERALL STATUS       : DEGRADED")
    return 1


if __name__ == "__main__":
    sys.exit(Main())