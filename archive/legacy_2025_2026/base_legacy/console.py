# LCARS FRAMEWORK v1.0.0-ALPHA
# Термінальна Консоль LCARS (LCARSConsole)
# ОПИС: Центральний інтерфейс командного рядка бортового комп'ютера. Обробляє внутрішні
#        команди LCARS, системний shell (PowerShell/Bash), компіляцію скриптів .lcars,
#        та виконання Python програм. Архітектура Zero-Except - помилки пропагуються вгору.
# ФУНКЦІЇ:
#   - Execute: Головний обробник вхідних команд
#   - ExecuteShell: Асинхронне виконання системних команд
#   - ExecuteCompile: Компіляція LCARS Script (.lcars) в Python
#   - ExecuteRun: Виконання Python скриптів
#   - ExecuteHelp/Status/Alert/Mode/Diag: Внутрішні команди управління
#   - ExecuteBrowser: Запуск веб-браузера
#   - ExecuteExit: Коректне завершення термінала
#   - Stop: Аварійна зупинка активного процесу
# ПІДКЛЮЧЕННЯ: Компілятор LCARS Script (lcars/system/compiler) через Isolinear
# ВЕРСІЯ: v1.0.0-ALPHA — повноцінний термінал з підтримкою власної мови LCARS

from __future__ import annotations
from typing import Any, Callable, Dict, Optional

from lcars.base.type import Directive

class LCARSConsole:
    def __init__(self, BoardComputer: Optional[Any] = None, **Kwargs):
        self.ComputerRef = BoardComputer or Kwargs.get('BoardComputer')
        self.CurrentProcess = None
        self.IsProcessActive = False
        self.CommandRegistry = {
            'help':    self.ExecuteHelp,
            'status':  self.ExecuteStatus,
            'alert':   self.ExecuteAlert,
            'mode':    self.ExecuteMode,
            'diag':    self.ExecuteDiagnostics,
            'compile': self.ExecuteCompile,
            'run':     self.ExecuteRun,
            'stop':    self.ExecuteStop,
            'browser': self.ExecuteBrowser,
            'exit':    self.ExecuteExit,
        }

    def Execute(self, InputText: str, OutputCallback: Callable[[str], None]):
        InputText = (InputText or "").strip()
        if not InputText:
            return
        Segments = InputText.split()
        Command = Segments[0].lower()
        Args = Segments[1:]
        if Command in self.CommandRegistry:
            self.CommandRegistry[Command](Args, OutputCallback)
            return
        self.ExecuteShell(InputText, OutputCallback)

    def ExecuteShell(self, Command: str, Callback: Callable[[str], None]):
        if self.IsProcessActive:
            Callback('◤ ERROR: SYSTEM BUSY')
            return

        def Run():
            self.IsProcessActive = True
            IsWin = (Directive.System.platform == "win32")
            Shell = 'powershell' if IsWin else '/bin/bash'
            Flag = '-Command' if IsWin else '-c'
            self.CurrentProcess = Directive.Terminal.Popen(
                [Shell, Flag, Command],
                stdout=Directive.Terminal.PIPE,
                stderr=Directive.Terminal.STDOUT,
                text=True, bufsize=1
            )
            Stdout = self.CurrentProcess.stdout
            if Stdout is not None:
                for Line in Stdout:
                    if Line:
                        Callback(Line.rstrip('\n'))
            self.CurrentProcess.wait()
            self.IsProcessActive = False
            self.CurrentProcess = None

        Directive.Process.Thread(target=Run, daemon=True).start()

    def ExecuteHelp(self, Args, Callback):
        Commands = ', '.join(sorted(self.CommandRegistry.keys()))
        Callback(f'◤ LCARS COMMANDS: {Commands}')
        Callback('◤ SHELL: ANY OTHER TEXT EXECUTES IN SYSTEM SHELL.')

    def ExecuteStatus(self, Args, Callback):
        if not self.ComputerRef:
            Callback('◤ STATUS: NO BOARD COMPUTER LINKED.')
            return
        Status = self.ComputerRef.GetSystemSummary()
        Callback(self.FormatReport("STATUS", Status))

    def ExecuteAlert(self, Args, Callback):
        if not self.ComputerRef or not Args:
            Callback('◤ ALERT ERROR: CORE UNLINKED OR MISSING PARAMETER.')
            return
        Level = Args[0].upper()
        self.ComputerRef.SetAlertLevel(Level)
        Callback(f'◤ ALERT SYSTEM: CONDITION {Level} APPLIED.')

    def ExecuteMode(self, Args, Callback):
        if not self.ComputerRef or not hasattr(self.ComputerRef, 'CycleAlertMode'):
            Callback('◤ ERROR: MODE CYCLE NOT SUPPORTED BY ACTIVE CORE.')
            return
        self.ComputerRef.CycleAlertMode()
        Callback('◤ MODE: ALERT CONDITION CYCLED.')

    def ExecuteDiagnostics(self, Args, Callback):
        if not self.ComputerRef or not hasattr(self.ComputerRef, 'GetSystemMetrics'):
            Callback('◤ DIAG ERROR: CORE MODULE INACCESSIBLE.')
            return
        Data = self.ComputerRef.GetSystemMetrics()
        Callback(self.FormatReport("DIAGNOSTICS", Data))

    def ExecuteCompile(self, Args, Callback):
        if not Args:
            Callback('◤ COMPILE ERROR: MISSING PATH PARAMETER.')
            return
        from lcars.system.compiler import UniversalCompiler
        Compiler = UniversalCompiler()
        Result = Compiler.compile_path(Directive.PathDrive(Args[0]))
        Callback(self.FormatReport("COMPILATION", {
            'IsolinearID': getattr(Result, 'IsolinearID', 'UNKNOWN'),
            'CompilationStatus': 'SUCCESSFUL'
        }))

    def ExecuteBrowser(self, Args, Callback):
        Callback('◤ BROWSER: UPLINK INITIATED // WEB ENGINE ACTIVE.')

    def ExecuteRun(self, Args, Callback):
        if not Args:
            Callback('◤ RUN ERROR: MISSING FILEPATH. USAGE: run <filepath> [args]')
            return
        Target = Args[0]
        Extra = Args[1:]
        if Target.lower().endswith('.py'):
            Cmd = [Directive.System.executable, Target] + Extra if hasattr(Directive.System, 'executable') else ['python', Target] + Extra
        else:
            Cmd = [Target] + Extra
        Callback(f'◤ RUN: EXECUTING {Cmd}')
        import subprocess
        with subprocess.Popen(Cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as P:
            self.CurrentProcess = P
            self.IsProcessActive = True
            if P.stdout is not None:
                for Line in P.stdout:
                    Callback(Line.rstrip('\n'))
            P.wait()
            self.IsProcessActive = False
            self.CurrentProcess = None
            Callback(f'◤ RUN: EXIT CODE {P.returncode}')

    def ExecuteStop(self, Args, Callback):
        if self.Stop():
            Callback('◤ STOP: NOMINAL // PROCESS TERMINATED.')
        else:
            Callback('◤ STOP: NO ACTIVE PROCESS DETECTED.')

    def Stop(self) -> bool:
        if self.CurrentProcess and self.IsProcessActive:
            self.CurrentProcess.kill()
            return True
        return False

    def ExecuteExit(self, Args, Callback):
        if self.Stop():
            Callback('◤ EXIT: NOMINAL // PROCESS TERMINATED.')
        else:
            Callback('◤ EXIT: NO ACTIVE PROCESS DETECTED.')
        Callback('◤ EXIT: TERMINAL SHUTDOWN INITIATED.')
        Directive.System.exit(0)
        return

    def FormatReport(self, Label: str, Data: Dict[str, Any]) -> str:
        Header = f"◤ {Label} REPORT // LCARS"
        Body = '\n'.join(f'  {K.upper()}: {V}' for K, V in (Data or {}).items())
        return f'{Header}\n{Body}'

ConsoleBackend = LCARSConsole
ConsoleBase = LCARSConsole

__all__ = ["LCARSConsole", "ConsoleBackend", "ConsoleBase"]

