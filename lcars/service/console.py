# LCARS terminal console.
# Призначення: приймає текст від терміналу, розбирає його на системну
# директиву/скрипт/запит агента і повертає рядки назад одним каналом.
# Console не запускає довільні процеси та не має власної шини: сигнали йдуть
# через ODN, а обчислення делегуються LCARSRuntime.

from pathlib import Path
import subprocess
from typing import Any, Callable, Dict, List, Optional

from lcars.base.version import getVersion
from lcars.core.signal import ODNInstance
from lcars.system.command import Command
from lcars.system.compiler import UniversalCompiler
from lcars.system.runtime import LCARSRuntime, RuntimeMode


# Транспортний адаптер між людиною/агентом і Command Core
class LCARSConsole:
    def __init__(self, BoardComputer=None, Compiler=None):
        self.Computer = BoardComputer
        self.Compiler = Compiler or UniversalCompiler()
        self.CommandNode: Optional[Command] = None
        self.Runtime = LCARSRuntime(ODNNode=ODNInstance)
        self.Version = "LCARS " + getVersion()
        self.ProjectRoot = Path(__file__).resolve().parents[2]
        self.Cwd = self.ProjectRoot
        self.ActiveMode = "OPTICAL"
        self.PreferredAIBackend = "LOCAL"
        self.AvailableModes = ("OPTICAL", "QUANTUM")
        self.Running = True
        self.ShellCommands = {"tasklist", "dir", "ls", "pwd", "ping", "ipconfig", "netstat", "whoami"}
        self.Commands = {
            "help": self.Help,
            "status": self.Status,
            "version": self.VersionInfo,
            "bios": self.Bios,
            "alert": self.Alert,
            "mode": self.Mode,
            "model": self.Model,
            "backend": self.Model,
            "modes": self.ModesInfo,
            "diag": self.Diagnostics,
            "directive": self.Directive,
            "lcars": self.Help,
            "compile": self.Compile,
            "build": self.Compile,
            "run": self.Run,
            "source": self.Run,
            "cd": self.ChangeDirectory,
            "pwd": self.PrintWorkingDirectory,
            "ls": self.ListDirectory,
            "dir": self.ListDirectory,
            "clear": self.Clear,
            "cls": self.Clear,
            "stop": self.StopCommand,
        }

    # Емісія події через ODN-шину
    def Emit(self, Channel: str, Data: Dict[str, Any]) -> None:
        if hasattr(ODNInstance, "Emit"):
            ODNInstance.Emit(Channel, Data)

    # Виконання введеного тексту: розбір на команду, директиву, агента
    def Execute(self, Text: str, Output: Callable[[str], None]) -> None:
        Clean = (Text or "").strip()
        if not Clean:
            return
        self.Emit("Console.Input", {"text": Clean, "mode": self.ActiveMode})
        Parts = Clean.split()
        Name = Parts[0].lower()
        Args = Parts[1:]
        Handler = self.Commands.get(Name)
        if Handler is not None:
            Handler(Args, Output, Clean)
            return
        if self.IsDirective(Name):
            self.EmitResult(Output, self.Command().Execute(Name, self.Params(Args)))
            return
        if Name in ("exit", "quit", "shutdown"):
            self.StopCommand(Args, Output, Clean)
            return
        if Name in ("ai", "ask", "think", "copilot"):
            self.Agent(Args, Output)
            return
        Target = self.ResolvePath(Clean)
        if Target.exists() and Target.suffix.lower() == ".lcars":
            self.Run([Clean], Output, Clean)
            return
        Output("LCARS: UNKNOWN DIRECTIVE — " + Name)
        Output("LCARS: AVAILABLE — HELP | STATUS | MODE QUANTUM | COMPILE <file.lcars> | RUN <file.lcars>")

    # Виконання тексту та повернення результату як рядка
    def RunCommand(self, Text: str) -> str:
        Lines: List[str] = []
        self.Execute(Text, Lines.append)
        return "\n".join(Lines)

    # Отримання або створення вузла Command
    def Command(self) -> Command:
        if self.CommandNode is None:
            self.CommandNode = Command()
        return self.CommandNode

    # Перевірка чи є ім'я системною директивою
    def IsDirective(self, Name: str) -> bool:
        return Name.upper() in self.Command().Directives

    # Побудова словника параметрів з аргументів команди
    def Params(self, Args: List[str]) -> Dict[str, Any]:
        if not Args:
            return {}
        Data: Dict[str, Any] = {}
        for Item in Args:
            if "=" in Item:
                Key, Value = Item.split("=", 1)
                Data[Key] = Value
        if Data:
            return Data
        return {"Value": Args[0], "Level": Args[0], "Args": Args}

    # Класифікація введеного тексту для агентів
    def ClassifyInput(self, Text: str) -> str:
        # Класифікація потрібна агентам до виконання: команда не маскується під
        # природну мову, а невідомий короткий ввід не запускається автоматично.
        Clean = (Text or "").strip()
        if not Clean:
            return "UNKNOWN"
        Name = Clean.split()[0].lower()
        if Name in self.Commands or self.IsDirective(Name) or Name in ("ai", "ask", "think", "copilot"):
            return "COMMAND"
        if self.LooksLikeShell(Clean):
            return "SHELL"
        if self.LooksLikeThought(Clean):
            return "THINK"
        return "UNKNOWN"

    # Перевірка чи схожий текст на shell-команду
    def LooksLikeShell(self, Text: str) -> bool:
        Parts = (Text or "").strip().split()
        if not Parts:
            return False
        if Parts[0].lower() in self.ShellCommands:
            return True
        return any(Item in {"|", ">", "<", ">>", "&&", "||", ";"} for Item in Parts)

    # Перевірка чи схожий текст на запит для мислення
    def LooksLikeThought(self, Text: str) -> bool:
        Lower = (Text or "").strip().lower()
        if len(Lower.split()) < 3 or self.LooksLikeShell(Lower):
            return False
        Openers = ("what ", "how ", "why ", "who ", "when ", "where ", "\u0449\u043e ", "\u044f\u043a ", "\u0447\u043e\u043c\u0443 ", "\u0445\u0442\u043e ", "\u0434\u0435 ", "\u043f\u043e\u044f\u0441\u043d\u0438 ")
        return "?" in Lower or Lower.startswith(Openers)

    # Вивід довідки про доступні команди
    def Help(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Output("LCARS CONSOLE // ISOLINEAR NETWORK INTERFACE")
        Output("CHANNEL: ODN / ISOLINEAR NETWORK")
        Output("PIPELINE: COMMAND -> CONSOLE -> TERMINAL -> ONBOARD")
        Output("MODES: " + ", ".join(self.AvailableModes))
        Output("DIRECTIVES: STATUS VERSION BIOS ALERT MODE COMPILE RUN PWD LS HELP")
        Output("AGENT INTERFACE: AI <prompt>")

    # Вивід поточного статусу системи
    def Status(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Result = self.Command().Execute("STATUS")
        Result["Data"]["Mode"] = self.ActiveMode
        Result["Data"]["AI"] = self.PreferredAIBackend
        Result["Data"]["Runtime"] = "READY" if not self.Runtime.IsRunning else "RUNNING"
        self.EmitResult(Output, Result)

    # Вивід інформації про версію LCARS
    def VersionInfo(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        self.EmitResult(Output, self.Command().Execute("VERSION"))

    # Вивід інформації про BIOS
    def Bios(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        self.EmitResult(Output, self.Command().Execute("BIOS"))

    # Вивід або встановлення рівня тривоги
    def Alert(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        self.EmitResult(Output, self.Command().Execute("ALERT", self.Params(Args)))

    # Керування режимом роботи системи (OPTICAL/QUANTUM)
    def Mode(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        if not Args:
            Output("MODE: " + self.ActiveMode)
            return
        Value = Args[0].upper()
        if Value in ("NORMAL", "OPTICAL"):
            self.ActiveMode = "OPTICAL"
            self.Runtime.SetMode(RuntimeMode.OPTICAL)
        elif Value == "QUANTUM":
            self.ActiveMode = "QUANTUM"
            self.Runtime.SetMode(RuntimeMode.QUANTUM)
        else:
            Output("LCARS: UNKNOWN MODE — " + Value)
            return
        self.Emit("Console.ModeChanged", {"mode": self.ActiveMode})
        Output("MODE: " + self.ActiveMode)

    # Керування AI-бекендом (LOCAL/LOCALLLM)
    def Model(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        if not Args:
            Output("MODEL: " + self.PreferredAIBackend)
            return
        Value = Args[0].strip().upper()
        if Value in ("LOCAL", "LOCALLLM"):
            self.PreferredAIBackend = "LOCAL"
        else:
            self.PreferredAIBackend = Value
        if self.Computer is not None:
            setattr(self.Computer, "UseExternalAI", self.PreferredAIBackend != "LOCAL")
            setattr(self.Computer, "PreferredAIBackend", self.PreferredAIBackend)
        self.Emit("Console.ModelChanged", {"backend": self.PreferredAIBackend})
        Output("MODEL: " + self.PreferredAIBackend)

    # Вивід списку доступних режимів
    def ModesInfo(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Output("MODES: " + ", ".join(self.AvailableModes))

    # Вивід результатів діагностики системи
    def Diagnostics(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Output("DIAGNOSTICS: NOMINAL")
        Output("SIGNAL: ODN / ISOLINEAR")
        Output("RUNTIME: " + self.ActiveMode)

    # Виконання або довідка по системних директивах
    def Directive(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        if not Args:
            self.EmitResult(Output, self.Command().Execute("HELP"))
            return
        self.EmitResult(Output, self.Command().Execute(Args[0], self.Params(Args[1:])))

    # Компіляція .lcars джерельного коду
    def Compile(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        if not Args:
            Output("LCARS COMPILE: target path required")
            return
        Result = self.Compiler.compilePath(self.ResolvePath(Args[0]))
        self.EmitResult(Output, {
            "Command": "COMPILE",
            "Success": Result.success,
            "Message": "COMPILED" if Result.success else Result.error,
            "Data": {"Kind": Result.kind, "Output": str(Result.output_path or ""), "Isolinear": Result.isolinear_id or ""},
        })

    # Запуск .lcars джерельного коду через Runtime
    def Run(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        if not Args:
            Output("LCARS RUN: target path required")
            return
        Target = self.ResolvePath(Args[0])
        if not Target.exists():
            Output("LCARS RUN: source not found in filesystem")
            return
        if Target.suffix.lower() != ".lcars":
            Output("LCARS RUN: only .lcars source accepted by Runtime")
            return
        Result = self.Runtime.ExecuteSource(Target.read_text(encoding="utf-8"), Target.name)
        Output("LCARS RUN: " + ("COMPLETED" if Result.success else "FAILED"))
        for Error in Result.errors:
            Output(Error)

    # Запит до AI-агента з промптом
    def Agent(self, Args: List[str], Output: Callable[[str], None]) -> None:
        Prompt = " ".join(Args).strip()
        if not Prompt:
            Output("LCARS AI: directive requires prompt")
            return
        if self.Computer is not None and hasattr(self.Computer, "Ask"):
            Output(str(self.Computer.Ask(Prompt)))
            return
        # BoardComputer має legacy-метод askAI; підключаємо його як lazy link,
        # щоб провайдер не завантажувався під час звичайного старту терміналу.
        if self.Computer is not None and hasattr(self.Computer, "askAI"):
            Output(str(self.Computer.askAI(Prompt)))
            return
        Output("LCARS AI: provider not linked to board computer")

    # Зміна поточного робочого каталогу
    def ChangeDirectory(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        if not Args:
            Output(str(self.Cwd))
            return
        Target = self.ResolvePath(Args[0])
        if Target.exists() and Target.is_dir():
            self.Cwd = Target
            Output(str(self.Cwd))
            return
        Output("LCARS: path not found — " + str(Target))

    # Вивід поточного робочого каталогу
    def PrintWorkingDirectory(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Output(str(self.Cwd))

    # Вивід вмісту директорії
    def ListDirectory(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Target = self.ResolvePath(Args[0]) if Args else self.Cwd
        if not Target.exists() or not Target.is_dir():
            Output("LCARS: path not found — " + str(Target))
            return
        for Item in sorted(Target.iterdir(), key=lambda Value: Value.name.lower()):
            Output(Item.name + ("/" if Item.is_dir() else ""))

    # Очищення виводу терміналу
    def Clear(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Output("LCARS: DISPLAY CLEARED")

    # Зупинка поточної сесії
    def StopCommand(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        self.Running = False
        self.Command().Execute("SHUTDOWN")
        Output("LCARS: SESSION TERMINATION REQUESTED")

    # Розв'язування шляху відносно поточного каталогу
    def ResolvePath(self, Value: str) -> Path:
        Target = Path(Value)
        return Target if Target.is_absolute() else (self.Cwd / Target).resolve()

    # Форматування та вивід результату виконання команди
    def EmitResult(self, Output: Callable[[str], None], Result: Dict[str, Any]) -> None:
        Message = str(Result.get("Message", ""))
        Prefix = "OK" if Result.get("Success") else "ERROR"
        # ASCII-вивід сумісний із бортовим терміналом без вимоги до кодування.
        Output("[" + Prefix + "] " + Message)
        Data = Result.get("Data", {})
        if Data:
            Output(str(Data))

# Термінал — тонкий endpoint; у ньому немає другої системи команд.
class ConsoleTerminal:
    def __init__(self, Console: LCARSConsole):
        self.Console = Console
        self.Name = "LCARS Isolinear Terminal"

    # Виконання тексту через пов'язану консоль
    def Execute(self, Text: str, Output: Callable[[str], None]) -> None:
        self.Console.Execute(Text, Output)

    # Виконання тексту та повернення результату як рядка
    def RunCommand(self, Text: str) -> str:
        return self.Console.RunCommand(Text)

# Запуск зовнішнього процесу з перехопленням виводу
def StartProcess(CommandText: str, Cwd=None, OnChunk=None) -> int:
    if not CommandText:
        return 0
    Proc = subprocess.Popen(
        CommandText,
        cwd=str(Cwd) if Cwd else None,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    if Proc.stdout is not None:
        for Line in Proc.stdout:
            if OnChunk:
                OnChunk(Line.rstrip())
    Proc.wait()
    return int(Proc.returncode)

if __name__ == "__main__":
    Console = LCARSConsole()
    print(Console.Version)
    while True:
        Line = input("LCARS> ")
        if Line.lower() in ("exit", "terminate"):
            break
        Console.Execute(Line, print)

__all__ = ["LCARSConsole", "ConsoleTerminal", "StartProcess"]
