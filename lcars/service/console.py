# LCARS terminal console.
# Призначення: приймає текст від терміналу, розбирає його на системну
# директиву/скрипт/запит агента і повертає рядки назад одним каналом.
# Console не запускає довільні процеси та не має власної шини: сигнали йдуть
# через ODN, а обчислення делегуються LCARSRuntime.

from lcars.base.type import LCARS, SystemComponent
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN
from lcars.system.environment import SystemEnvironment, SessionEnvironment
from lcars.system.command import Command
from lcars.system.compiler import UniversalCompiler
from lcars.service.bridge import Bridge

# Транспортний адаптер між людиною/агентом і Command Core
class LCARSConsole(SystemComponent):
    def __init__(self, BoardComputer=None, Compiler=None, Shell=None):
        self.Computer = BoardComputer
        if Compiler is not None:
            self.Compiler = Compiler
        else:
            if True:
                self.Compiler = UniversalCompiler()
            if False: # Removed except block
                self.Compiler = None
        self.Shell = Shell
        self.CommandNode: Optional[Command] = None
        from lcars.service.bridge import Bridge
        if isinstance(getattr(self.Computer, "Bridge", None), Bridge):
            self.BridgeNode = self.Computer.Bridge
        else:
            self.BridgeNode = Bridge()
            if hasattr(self.BridgeNode, "Initialize") and callable(self.BridgeNode.Initialize):
                self.BridgeNode.Initialize()
        self.Version = "LCARS " + VersionInfo.Release
        self.ProjectRoot = LCARS.System.Path(__file__).resolve().parents[2]
        self.Runtime = SystemEnvironment
        self.Cwd = LCARS.System.Path(SystemEnvironment.getWorkingDirectory())
        
        # Використовуємо ізольоване середовище для цієї консолі
        self.Session = SessionEnvironment()
        self.Session.State["LCARS_PROJECT_ROOT"] = str(self.ProjectRoot)
        
        self.ActiveMode = "NORMAL"
        self.PreferredAIBackend = "LOCAL"
        self.BridgeNamespaces = {
            "AI", "SDK", "CLI", "IDE", "DATABASE", "CLOUD", "NETWORK", "STORAGE",
            "QUANTUM", "SCIENCE", "PHYSICS", "ENGINEERING", "SECURITY",
            "OPTIMIZATION", "ANALYTICS", "SIMULATION", "RENDERING", "XR", "SCENE",
        }
        self.Running = True
        self.Environment = self.BuildEnvironment()
        self.ShellCommands = {
            "tasklist", "dir", "ls", "pwd", "ping", "ipconfig", "netstat",
            "whoami", "powershell", "pwsh", "cmd", "python", "py", "pip",
            "pip3", "git", "npm", "npx", "node", "codex", "opencode", "uv",
            "poetry", "cargo", "go", "bash", "sh", "devin", "gemini", "agy",
            "antigravity", "code",
        }
        self.PowerShellPrefixes = (
            "get-", "set-", "new-", "remove-", "start-", "stop-", "invoke-",
            "test-", "clear-", "copy-", "move-", "import-", "export-",
            "select-", "where-", "foreach-", "measure-", "format-", "add-",
        )
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
            "bridge": self.BridgeCommand,
            "connect": self.BridgeCommand,
            "catalog": self.BridgeCatalog,
            "diag": self.Diagnostics,
            "directive": self.Directive,
            "lcars": self.Help,
            "compile": self.Compile,
            "build": self.Compile,
            "run": self.Run,
            "source": self.Run,
            "python": self.RunPython,
            "py": self.RunPython,
            "ai": self.AICommand,
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
        if hasattr(ODN, "Transmit"):
            ODN.Transmit(Channel, Data)

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
        if any(ord(char) > 127 for char in Clean) or self.LooksLikeGreeting(Clean) or self.LooksLikeThought(Clean):
            Output(self.LocalIntelligence(Clean, StreamCallback=Output))
            return
        if Name in self.ShellCommands and self.TryShellCommand(Clean, Output):
            return
        if self.TryBridgeCommand(Clean, Output):
            return
        if self.HandlePath(Clean, Output):
            return
        if self.LooksLikeShell(Clean) and self.TryShellCommand(Clean, Output):
            return
        # Делегування природних та інженерних директив Бортовому Комп'ютеру
        Output(self.LocalIntelligence(Clean, StreamCallback=Output))

    # Запуск Python-файлу через системний інтерпретатор
    def RunPython(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        if not Args:
            Output("LCARS PYTHON: target path required")
            return
        if Args[0].startswith("-"):
            InlineValue = " ".join(Args[1:]).strip()
            if InlineValue.startswith(("'", '"')) and InlineValue.endswith(InlineValue[0]):
                InlineValue = InlineValue[1:-1]
            Arguments = [Args[0]]
            if InlineValue:
                Arguments.append(InlineValue)
            ReturnCode, Lines = self.RunProcess(self.PythonExecutable(), Arguments, Cwd=self.Cwd)
            Output("LCARS PYTHON: COMPLETED" if ReturnCode == 0 else "LCARS PYTHON: FAILED")
            for Line in Lines:
                Output(Line)
            Output(f"LCARS PYTHON: EXIT {int(ReturnCode)}")
            return
        Target = self.ResolvePath(Args[0])
        if not Target.exists() or not Target.is_file():
            Output("LCARS PYTHON: source not found in filesystem")
            return
        if Target.suffix.lower() != ".py":
            Output("LCARS PYTHON: only .py source accepted")
            return
        ReturnCode, Lines = self.RunProcess(self.PythonExecutable(), [str(Target)], Cwd=Target.parent)
        Output("LCARS PYTHON: COMPLETED" if ReturnCode == 0 else "LCARS PYTHON: FAILED")
        for Line in Lines:
            Output(Line)
        Output(f"LCARS PYTHON: EXIT {int(ReturnCode)}")

    # Запуск OpenCode AI в терміналі
    def AICommand(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Prompt = " ".join(Args).strip() if Args else ""
        if not Prompt:
            Output("LCARS AI: usage — AI <prompt>")
            Output("Example: AI як створити клас в Python?")
            Output("Modes: AI <text> — simple query")
            Output("       AI --chat — interactive mode")
            return
        Output(f"LCARS AI: Processing...")
        Output(f"Query: {Prompt}")
        Output("─" * 50)
        # Використовуємо AIProviderManager для відповіді
        ImportResult = LCARS.Import("lcars.service.provider")
        if ImportResult:
            AIProviderManager = getattr(ImportResult, "AIProviderManager", None)
            if AIProviderManager:
                Manager = AIProviderManager.GetInstance()
                Messages = [{"role": "user", "content": Prompt}]
                Response = Manager.Route(Messages)
                if Response:
                    Output(Response)
                else:
                    Output("LCARS AI: no response from provider")
            else:
                Output("LCARS AI: AIProviderManager not found")
        else:
            Output("LCARS AI: provider module not loaded")
        Output("─" * 50)

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
        First = Parts[0].lower()
        if First in self.ShellCommands:
            return True
        if self.LooksLikePowerShell(Text):
            return True
        if any(Item in {"|", ">", "<", ">>", "&&", "||", ";"} for Item in Parts):
            return True
        if any(First.endswith(Suffix) for Suffix in (".exe", ".cmd", ".bat", ".ps1", ".py", ".pyw", ".sh")):
            return True
        if "\\" in Parts[0] or "/" in Parts[0] or ":" in Parts[0]:
            return True
        return False

    # Перевірка на PowerShell-рядок або cmdlet
    def LooksLikePowerShell(self, Text: str) -> bool:
        Clean = (Text or "").strip()
        if not Clean:
            return False
        First = Clean.split()[0]
        Lower = First.lower()
        if First.startswith("$") or First.startswith("@") or First.startswith("&"):
            return True
        if any(Lower.startswith(Prefix) for Prefix in self.PowerShellPrefixes):
            return True
        if "." in First and First.startswith("$"):
            return True
        if First in {"irm", "iex", "gci", "gsv", "gps", "ls", "dir", "pwd"}:
            return True
        return False

    # Перевірка на коротке привітання або дружній ввід
    def LooksLikeGreeting(self, Text: str) -> bool:
        Clean = (Text or "").strip().lower()
        if not Clean:
            return False
        Greetings = {
            "hi", "hello", "hey", "greetings", "вітаю", "привіт", "здрастуй",
            "доброго", "добрий", "salut", "hola",
        }
        if Clean in Greetings:
            return True
        First = Clean.split()[0]
        return First in Greetings

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
        Output("MODES: NORMAL / QUANTUM")
        Output("MODE ALIAS: NORMAL = OPTICAL")
        Output("DIRECTIVES: STATUS VERSION BIOS ALERT MODE COMPILE RUN PWD LS HELP")
        Output("BRIDGE: BRIDGE <name> | CONNECT <name> | CATALOG [prefix]")
        Output("BRIDGE STATE: STATUS <name> | INFO <name> | INSPECT <name>")
        Output("AUTO: FILE PATHS ROUTE BY EXTENSION | UNKNOWN TEXT GOES TO AI OR BRIDGE")
        Output("AGENT INTERFACE: AI <prompt>")

    # Вивід поточного статусу системи
    def Status(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Result = self.Command().Execute("STATUS")
        Result["Data"]["Mode"] = self.ActiveMode
        Result["Data"]["AI"] = self.PreferredAIBackend
        self.EmitResult(Output, Result)

    # Вивід інформації про версію LCARS
    def VersionInfo(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Output(f"[OK] {self.Version}")

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
            self.ActiveMode = "NORMAL"
            if self.Computer is not None and hasattr(self.Computer, "SetRuntimeMode"):
                self.Computer.SetRuntimeMode("OPTICAL")
        elif Value == "QUANTUM":
            self.ActiveMode = "QUANTUM"
            if self.Computer is not None and hasattr(self.Computer, "SetRuntimeMode"):
                self.Computer.SetRuntimeMode("QUANTUM")
        else:
            Output("LCARS: UNKNOWN MODE — " + Value)
            return
        self.Emit("Console.ModeChanged", {"mode": self.ActiveMode})
        Output("MODE: " + self.ActiveMode)

    # Керування AI-бекендом (LOCAL/LOCALLLM/MISTRAL/GROQWEN/QVAC)
    def Model(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        if not Args:
            Output("MODEL: " + self.PreferredAIBackend)
            return
        CleanTokens = [Token.strip().upper() for Token in Args if Token.lower() not in ("на", "to", "model", "модель", "бекенд", "backend")]
        Value = CleanTokens[-1] if CleanTokens else Args[0].strip().upper()
        if Value in ("LOCAL", "LOCALLLM"):
            self.PreferredAIBackend = "LOCAL"
        else:
            self.PreferredAIBackend = Value
        from lcars.service.provider import AIProvider
        BackendName = "localllm" if self.PreferredAIBackend == "LOCAL" else self.PreferredAIBackend.lower()
        ProviderSwitched = AIProvider.SwitchModel(BackendName)
        if self.Computer is not None:
            setattr(self.Computer, "UseExternalAI", self.PreferredAIBackend != "LOCAL")
            setattr(self.Computer, "PreferredAIBackend", self.PreferredAIBackend)
        self.Emit("Console.ModelChanged", {"backend": self.PreferredAIBackend, "Backend": self.PreferredAIBackend})
        self.Emit("AI.ModelChanged", {"backend": self.PreferredAIBackend, "Backend": self.PreferredAIBackend})
        State = "ONLINE" if ProviderSwitched else "UNAVAILABLE"
        Output(f">> [AI CORE]: MODEL BACKEND SWITCHED TO {self.PreferredAIBackend} [{State}]")



    # Вивід списку доступних режимів
    def ModesInfo(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Output("MODES: NORMAL, QUANTUM")
        Output("NORMAL = OPTICAL")

    # Каталог bridge-цілей
    def BridgeCatalog(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Prefix = " ".join(Args).strip()
        if Prefix:
            LowerPrefix = Prefix.lower()
            if LowerPrefix.startswith("bridge "):
                Prefix = "Bridge." + Prefix[7:].strip().replace(" ", ".")
            elif not LowerPrefix.startswith("bridge."):
                Prefix = "Bridge." + Prefix.replace(" ", ".")
        Keys = self.BridgeNode.Catalog(Prefix or "")
        if not Keys:
            Output("BRIDGE CATALOG: EMPTY")
            return
        if Prefix:
            Output("BRIDGE CATALOG: " + Prefix)
            for Key in Keys:
                Output(Key)
            return
        Families = {}
        for Key in Keys:
            Parts = Key.split(".")
            Family = ".".join(Parts[:3]) if len(Parts) >= 3 else Key
            Families[Family] = Families.get(Family, 0) + 1
        Output("BRIDGE CATALOG: " + str(len(Keys)) + " ENTRIES")
        for Family in sorted(Families):
            Output(Family + " // " + str(Families[Family]))

    # Підключення до bridge-цілі
    def BridgeCommand(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        if not Args:
            self.BridgeCatalog([], Output, Text)
            return
        Head = Args[0].lower()
        if Head in ("help", "list", "catalog", "show"):
            self.BridgeCatalog(Args[1:], Output, Text)
            return
        if Head in ("status", "info", "inspect"):
            self.BridgeStatus(Args[1:], Output, Text)
            return
        if Head in ("connect", "link", "use"):
            Args = Args[1:]
        Target = " ".join(Args).strip()
        if not Target:
            self.BridgeCatalog([], Output, Text)
            return
        if Target.upper() in self.BridgeNamespaces:
            self.BridgeCatalog([Target], Output, Text)
            return
        Resolved = self.BridgeNode.Connect(Target)
        if Resolved is None:
            self.BridgeStatus([Target], Output, Text)
            return
        self.DescribeBridgeConnection(Target, Resolved, Output)

    # Автоматичний bridge-роутер для коротких введень
    def TryBridgeCommand(self, Text: str, Output: Callable[[str], None]) -> bool:
        Clean = (Text or "").strip()
        if not Clean:
            return False
        Parts = Clean.split()
        if not Parts:
            return False
        Head = Parts[0].lower()
        if Head in ("bridge", "connect"):
            self.BridgeCommand(Parts[1:], Output, Clean)
            return True
        if len(Parts) == 1 and not any(Char in Clean for Char in ("\\", "/", ":")):
            Resolved = self.BridgeNode.Connect(Clean)
            if Resolved is None:
                return False
            self.DescribeBridgeConnection(Clean, Resolved, Output)
            return True
        return False

    # Людиночитна відповідь на bridge-підключення
    def DescribeBridgeConnection(self, Name: str, Target: Any, Output: Callable[[str], None]) -> None:
        Label = getattr(Target, "__name__", Target.__class__.__name__)
        ModuleName = getattr(Target, "__module__", "")
        if ModuleName and ModuleName != "builtins" and ModuleName != "__main__":
            Output("BRIDGE: CONNECTED -> " + ModuleName + "." + Label)
        else:
            Output("BRIDGE: CONNECTED -> " + Label)
        FileName = getattr(Target, "__file__", "")
        if FileName:
            Output("BRIDGE SOURCE: " + str(FileName))

    # Вивід поточного стану bridge-запису
    def BridgeStatus(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Target = " ".join(Args).strip()
        if not Target:
            self.BridgeCatalog([], Output, Text)
            return
        Located = self.BridgeNode.Locate(Target)
        if not Located:
            Output("BRIDGE: NOT REGISTERED — " + Target)
            return
        for Item in Located:
            Key = str(Item.get("Key", Target))
            State = str(Item.get("State", "UNKNOWN"))
            ModuleName = Item.get("Module")
            AttributeTarget = Item.get("Attribute")
            if State == "ONLINE":
                Output("BRIDGE: ONLINE — " + Key)
                if ModuleName:
                    Output("MODULE: " + str(ModuleName))
                if AttributeTarget:
                    Output("ATTRIBUTE: " + str(AttributeTarget))
                continue
            if State == "NAMESPACE":
                Output("BRIDGE: NAMESPACE — " + Key)
                continue
            if State == "OFFLINE":
                Output("BRIDGE: REGISTERED BUT OFFLINE — " + Key)
                if ModuleName:
                    Output("MODULE: " + str(ModuleName))
                if AttributeTarget:
                    Output("ATTRIBUTE: " + str(AttributeTarget))
                continue
            Output("BRIDGE: REGISTERED — " + Key)

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
        if Target.is_dir():
            self.ListDirectory([str(Target)], Output, Text)
            return
        if Target.suffix.lower() in (".py", ".pyw"):
            self.RunPython([str(Target)], Output, Text)
            return
        if Target.suffix.lower() == ".lcars":
            Output("LCARS RUN: .lcars execution requires program runtime (not available in system console)")
            return
        if self.Compiler.findCompiler(Target) is not None:
            Result = self.Compiler.compilePath(Target)
            self.EmitResult(Output, {
                "Command": "RUN",
                "Success": Result.success,
                "Message": "COMPILED" if Result.success else Result.error,
                "Data": {"Kind": Result.kind, "Output": str(Result.output_path or ""), "Isolinear": Result.isolinear_id or ""},
            })
            return
        Output("LCARS RUN: no runtime available for this file type")

    # Запит до AI-агента або розгортання інтерактивної сесії Copilot
    def Agent(self, Args: List[str], Output: Callable[[str], None], TriggerName: str = "copilot") -> None:
        Prompt = " ".join(Args).strip()
        
        # 1. Якщо виклик "copilot" або "agent" без аргументів — розгортаємо інтерактивного агента
        if not Prompt or Prompt.lower() in ("copilot", "agent", "ai", "status"):
            if self.Computer is not None and hasattr(self.Computer, "GetAgent"):
                Agent = self.Computer.GetAgent()
                Diagnostic = Agent.Diagnostics.RunDiagnostic() if hasattr(Agent, "Diagnostics") else {}
                Output("◤ LCARS COPILOT // ONBOARD AGENT ONLINE 🖖")
                Output("======================================================================")
                Output(f">> AGENT ID   : {getattr(Agent, 'AgentId', 'LCARS-COPILOT-01')}")
                Output(f">> STATUS     : {getattr(Agent, 'State', 'ONLINE').value if hasattr(getattr(Agent, 'State', None), 'value') else 'ONLINE'}")
                Output(f">> BACKEND    : GEMINI CLI / LOCAL CORE [READY]")
                Output(f">> MEMORY     : {len(getattr(Agent.Memory, 'Messages', [])) if hasattr(Agent, 'Memory') else 0} ACTIVE TURNS")
                Output(f">> SKILLS     : {len(Agent.ListSkills()) if hasattr(Agent, 'ListSkills') else 'ALL'} MODULES LOADED")
                Output("----------------------------------------------------------------------")
                Output(">> READY. Enter 'copilot <request>' or type your instruction directly.")
                Output("======================================================================")
                return
            Output("◤ LCARS COPILOT ACTIVE: Ready for instructions. Usage: copilot <prompt>")
            return

        # 2. Якщо задано промпт — надсилаємо в Copilot / Board Computer
        if self.Computer is not None and hasattr(self.Computer, "GetAgent"):
            Agent = self.Computer.GetAgent()
            if Agent is not None and hasattr(Agent, "Think"):
                Result = Agent.Think(Prompt)
                Output(str(Result))
                return

        if self.Computer is not None and hasattr(self.Computer, "AskAI"):
            Output(str(self.Computer.AskAI(Prompt)))
            return

        if self.Computer is not None and hasattr(self.Computer, "askAI"):
            Output(str(self.Computer.askAI(Prompt)))
            return

        if self.Computer is not None:
            Output(str(self.Computer.LocalIntelligence(Prompt)) if hasattr(self.Computer, "LocalIntelligence") else "LCARS AI: provider not linked to board computer")
            return
        Output("LCARS AI: provider not linked to board computer")

    # Зміна поточного робочого каталогу
    def ChangeDirectory(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        if not Args:
            Output(str(self.Session.Cwd))
            return
        if self.Session.ChangeDirectory(Args[0]):
            Output(str(self.Session.Cwd))
            return
        Output("LCARS: path not found — " + str(Args[0]))

    # Вивід поточного робочого каталогу
    def PrintWorkingDirectory(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Output(str(self.Session.Cwd))

    # Вивід вмісту директорії
    def ListDirectory(self, Args: List[str], Output: Callable[[str], None], Text: str = "") -> None:
        Target = self.Session.ResolvePath(Args[0]) if Args else self.Session.Cwd
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

    # Локальна відповідь без зовнішнього AI-провайдера
    def LocalIntelligence(self, Text: str, StreamCallback = None) -> str:
        Clean = (Text or "").strip()
        if self.Computer and hasattr(self.Computer, "ProcessVoiceDirective"):
            return self.Computer.ProcessVoiceDirective(Clean, StreamCallback=StreamCallback)
        from lcars.core.computer import BoardComputer
        return BoardComputer.GetInstance().ProcessVoiceDirective(Clean, StreamCallback=StreamCallback)

    # Розв'язування шляху відносно поточного каталогу
    def ResolvePath(self, Value: str) -> Any:
        return self.Session.ResolvePath(Value)

    # Побудова середовища для shell-процесів і CLI-інструментів
    def BuildEnvironment(self) -> Dict[str, str]:
        Environment = self.Session.Export()
        Paths: List[str] = []
        Candidates = [
            self.ProjectRoot,
            self.ProjectRoot / ".venv" / "Scripts",
            self.ProjectRoot / ".venv" / "bin",
            LCARS.System.Path.cwd(),
        ]
        AppData = SystemEnvironment.get("APPDATA", "")
        if AppData:
            Candidates.append(LCARS.System.Path(AppData) / "npm")
        LocalAppData = SystemEnvironment.get("LOCALAPPDATA", "")
        if LocalAppData:
            Candidates.append(LCARS.System.Path(LocalAppData) / "devin" / "cli" / "bin")
        for Candidate in Candidates:
            if Candidate.exists():
                Text = str(Candidate)
                if Text not in Paths:
                    Paths.append(Text)
        CurrentPath = Environment.get("PATH", "")
        if CurrentPath:
            Paths.append(CurrentPath)
        Environment["PATH"] = ";".join(Paths)
        Environment["LCARS_PROJECT_ROOT"] = str(self.ProjectRoot)
        return Environment

    # Повертає шлях до Python з поточного LCARS-оточення
    def PythonExecutable(self) -> str:
        Candidate = self.ProjectRoot / ".venv" / "Scripts" / "python.exe"
        if Candidate.exists():
            return str(Candidate)
        return "python"

    # Виконує ввід як шлях до файлу або директорії
    def HandlePath(self, Text: str, Output: Callable[[str], None]) -> bool:
        Target = self.ResolvePath(Text)
        if not Target.exists():
            return False
        if Target.is_dir():
            self.ListDirectory([str(Target)], Output, Text)
            return True
        if Target.suffix.lower() in (".py", ".pyw"):
            self.RunPython([str(Target)], Output, Text)
            return True
        if Target.suffix.lower() == ".lcars":
            self.Run([str(Target)], Output, Text)
            return True
        if self.Compiler.findCompiler(Target) is not None:
            self.Compile([str(Target)], Output, Text)
            return True
        Output("LCARS: no compiler registered for " + str(Target.name))
        return True

    # Спроба виконати команду як shell/CLI програму
    def TryShellCommand(self, Text: str, Output: Callable[[str], None]) -> bool:
        Clean = (Text or "").strip()
        Lower = Clean.lower()

        # Інтерактивні CLI програми, які потребують повноцінного термінала (ConPTY/TTY)
        InteractivePrograms = {
            "devin", "gemini", "agy", "opencode", "copilot", "codex",
            "aider", "claude", "ollama", "pwsh", "powershell", "cmd",
        }

        Tokens = Clean.split()
        HeadCmd = Tokens[0].lower() if Tokens else ""
        if HeadCmd in InteractivePrograms:
            Output(f">> [SYSTEM]: Launching interactive agent in external PTY terminal: {HeadCmd}")
            Arguments = Tokens[1:]
            ReturnCode = self.RunInteractiveProcess(HeadCmd, Arguments, Cwd=self.Session.Cwd, Output=Output)
            if ReturnCode == 0:
                Output(f">> [SYSTEM]: Interactive session for '{HeadCmd}' started successfully [OK]")
            else:
                Output(f">> [SYSTEM]: Failed to start interactive session for '{HeadCmd}'")
            return True

        CommandSpec = self.BuildShellCommand(Text)
        if CommandSpec is None:
            return False
        Program, Arguments = CommandSpec
        ReturnCode, Lines = self.RunProcess(Program, Arguments, Cwd=self.Session.Cwd)
        for Line in Lines:
            Output(Line)
        if ReturnCode != 0 and (Program.lower().endswith("opencode") or "opencode" in Text.lower()):
            Output("LCARS: OPENCODE IS AN INTERACTIVE CLI AND MAY REQUIRE A REAL TERMINAL SESSION.")
        if ReturnCode != 0:
            BridgeProbe = self.BridgeNode.Locate(Text)
            if BridgeProbe:
                for Item in BridgeProbe:
                    State = str(Item.get("State", "UNKNOWN"))
                    Key = str(Item.get("Key", Text))
                    if State == "OFFLINE":
                        Output("BRIDGE: REGISTERED BUT OFFLINE — " + Key)
                    elif State == "NAMESPACE":
                        Output("BRIDGE: NAMESPACE — " + Key)
                    elif State == "ONLINE":
                        Output("BRIDGE: ONLINE — " + Key)
        return True

    # Конструює правильну оболонку для CLI або PowerShell-виразу
    def BuildShellCommand(self, Text: str):
        Clean = (Text or "").strip()
        if not Clean:
            return None
        if self.LooksLikePowerShell(Clean):
            Shell = "powershell" if SystemEnvironment.get("COMSPEC", "") else "powershell"
            return Shell, ["-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", Clean]
        if SystemEnvironment.get("COMSPEC", ""):
            return "cmd", ["/d", "/s", "/c", Clean]
        return "bash", ["-lc", Clean]

    # Запуск інтерактивної програми з термінальним інтерфейсом
    def RunInteractiveProcess(self, Program: str, Arguments: List[str], Cwd=None, Output: Callable[[str], None] = None) -> int:
        CleanArgs = [str(arg) for arg in Arguments]
        FullCmd = " ".join([str(Program)] + CleanArgs)
        SubprocessMod = LCARS.Import("subprocess")
        if not SubprocessMod:
            return 1
        WorkDir = str(Cwd) if Cwd else str(self.Session.Cwd)

        IsWindows = bool(SystemEnvironment.get("COMSPEC", ""))
        if IsWindows:
            CreationFlags = getattr(SubprocessMod, "CREATE_NEW_CONSOLE", 0x00000010)
            StartCmd = ["cmd.exe", "/k", FullCmd]
            SubprocessMod.Popen(StartCmd, cwd=WorkDir, creationflags=CreationFlags)
            return 0
        SubprocessMod.Popen(["x-terminal-emulator", "-e", FullCmd], cwd=WorkDir)
        return 0

    # Запуск процесу через LCARS.Core.Process
    def RunProcess(self, Program: str, Arguments: List[str], Cwd=None):
        Process = LCARS.Core.Process()
        if hasattr(Process, "setProgram"):
            Process.setProgram(str(Program))
        if hasattr(Process, "setArguments"):
            Process.setArguments([str(Item) for Item in Arguments])
        if Cwd is not None and hasattr(Process, "setWorkingDirectory"):
            Process.setWorkingDirectory(str(Cwd))
        if hasattr(Process, "setProcessChannelMode") and hasattr(LCARS.Core.Process, "ProcessChannelMode"):
            Process.setProcessChannelMode(LCARS.Core.Process.ProcessChannelMode.MergedChannels)
        if hasattr(Process, "setEnvironment"):
            Process.setEnvironment([f"{Key}={Value}" for Key, Value in self.Environment.items()])
        if hasattr(Process, "start"):
            Process.start()
        if hasattr(Process, "waitForStarted"):
            Process.waitForStarted()
        if hasattr(Process, "waitForFinished"):
            Process.waitForFinished()
        Encoding = LCARS.System.Locale.getpreferredencoding(False)
        RawOutput = b""
        if hasattr(Process, "readAllStandardOutput"):
            RawOutput += bytes(Process.readAllStandardOutput())
        # If MergedChannels is not used, read standard error separately
        HasMerged = hasattr(LCARS.Core.Process, "ProcessChannelMode") and hasattr(Process, "processChannelMode") and Process.processChannelMode() == LCARS.Core.Process.ProcessChannelMode.MergedChannels
        if not HasMerged and hasattr(Process, "readAllStandardError"):
            StandardError = bytes(Process.readAllStandardError())
            if StandardError:
                if RawOutput:
                    RawOutput += b"\n"
                RawOutput += StandardError
        Text = RawOutput.decode(Encoding, errors="replace") if RawOutput else ""
        Lines = [Line.rstrip() for Line in Text.replace("\r\n", "\n").split("\n") if Line.rstrip()]
        ReturnCode = int(Process.exitCode()) if hasattr(Process, "exitCode") else 0
        return ReturnCode, Lines

    # Форматування та вивід результату виконання команди
    def EmitResult(self, Output: Callable[[str], None], Result: Dict[str, Any]) -> None:
        Message = str(Result.get("Message", ""))
        Prefix = "OK" if Result.get("Success") else "ERROR"
        # ASCII-вивід сумісний із бортовим терміналом без вимоги до кодування.
        Output("[" + Prefix + "] " + Message)
        Data = Result.get("Data", {})
        if Data:
            Output(str(Data))

# Запуск зовнішнього процесу з перехопленням виводу — через клас, не через standalone функцію
class ProcessLauncher:
    @staticmethod
    def StartProcess(CommandText: str, Cwd: Any = None, OnChunk: Any = None) -> int:
        if not CommandText:
            return 0
        Program = "cmd" if SystemEnvironment.get("COMSPEC", "") else "bash"
        Arguments = ["/d", "/s", "/c", CommandText] if Program == "cmd" else ["-lc", CommandText]
        Console = LCARSConsole()
        ReturnCode, Lines = Console.RunProcess(Program, Arguments, Cwd=Cwd)
        if OnChunk:
            for Line in Lines:
                OnChunk(Line)
        return int(ReturnCode)


__all__ = ["LCARSConsole"]
