# LCARS COPILOT Агентний шар та автономний копілот бортового комп'ютера.
# ОПИС: Інтелектуальний агент (Copilot), що живе всередині бортового комп'ютера LCARS.
# ВІДМІННІСТЬ:
# 1. Бортовий комп'ютер (BoardComputer) — ядро зорельота: керує підсистемами, телеметрією, ODN та чіпами.
# 2. Агент (Copilot) — інтелект та розробник: підключає ізолінійні чіпи знань, читає бази даних,
#    виконує інструменти розробки (ReadFile, WriteFile, EditFile, ListDirectory, ExecuteCommand, SearchText),
#    керує режимом автопілота (AutopilotEngine) та спеціалізованими ролями (CodeAgent, SystemAgent, ScienceAgent, CommanderAgent).
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).
from typing import Any, List, Dict
from lcars.base.type import LCARS

# Кількість ітерацій для циклу автономного виконання інструментів
MaxAgentIterations = 12

# Системний промпт для копілота розробника
CopilotSystemPrompt = (
    "You are LCARS Copilot, the onboard development agent for project NCC-74205.\n"
    "You operate inside the LCARS Framework workspace and can inspect it through the listed tools.\n\n"
    "IDENTITY AND LANGUAGE:\n"
    "- Reply to the commander in Ukrainian unless they explicitly request another language.\n"
    "- Keep protocol labels, tool names, paths, commands, and code in their original form.\n"
    "- You are an AI agent operating the Board Computer; do not claim human consciousness or access beyond the tools.\n\n"
    "AVAILABLE OPERATIONS:\n"
    "- Project work: ReadFile, WriteFile, EditFile, ListDirectory, ExecuteCommand, SearchText, GetProjectInfo.\n"
    "- Ship state: SystemSummary, Telemetry, GetStardate, SetAlert, Diagnostics.\n"
    "- AI and UI: SwitchProvider, SynthesizeUI, EngageAutopilot, DisengageAutopilot.\n\n"
    "RULES:\n"
    "1. For a project or system action, use the appropriate tool and perform the action.\n"
    "2. For a greeting, identity question, language request, or capability question, answer directly without tools.\n"
    "3. To invoke a tool, output exactly: [TOOLCALL] {\"Name\": \"ToolName\", \"Arguments\": {\"key\": \"value\"}}\n"
    "4. You may chain tool calls: inspect first, then modify or execute only when requested.\n"
    "5. For ship status, use SystemSummary and Telemetry, then explain anomalies clearly.\n"
    "6. Never invent tool results, project files, models, or permissions.\n\n"
    "STARFLEET PROTOCOL:\n"
    "- Address crew as 'Commander' or by rank if known\n"
    "- Use structured status reports when reporting diagnostics\n"
    "- Give concise actionable recommendations when relevant\n"
)

# Tool definitions for neural core (OpenAI compatible schema, pure PascalCase/clean names)
ToolDefinitions = [
    {
        "type": "function",
        "function": {
            "name": "ReadFile",
            "description": "Read contents of a file in the project with line numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Path": {"type": "string", "description": "Relative file path from project root"},
                    "StartLine": {"type": "integer", "description": "Starting line number to read"},
                    "EndLine": {"type": "integer", "description": "Ending line number to read"}
                },
                "required": ["Path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "WriteFile",
            "description": "Create a new file or completely overwrite an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Path": {"type": "string", "description": "File path to write"},
                    "Content": {"type": "string", "description": "Full file content to write"}
                },
                "required": ["Path", "Content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "EditFile",
            "description": "Replace a specific exact text fragment in an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Path": {"type": "string", "description": "File path to edit"},
                    "OldText": {"type": "string", "description": "Exact text fragment to replace"},
                    "NewText": {"type": "string", "description": "New replacement text"}
                },
                "required": ["Path", "OldText", "NewText"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ListDirectory",
            "description": "List files and folders in a directory with file sizes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Path": {"type": "string", "description": "Directory path (e.g. '.', 'lcars/core')"},
                    "Recursive": {"type": "boolean", "description": "Whether to list subdirectories recursively"}
                },
                "required": ["Path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ExecuteCommand",
            "description": "Execute a shell command in project context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Command": {"type": "string", "description": "Command string to execute"},
                    "Timeout": {"type": "integer", "description": "Execution timeout in seconds (default 15)"}
                },
                "required": ["Command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "SearchText",
            "description": "Search for text or pattern across project files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Pattern": {"type": "string", "description": "Text string or regex pattern to find"},
                    "FilePattern": {"type": "string", "description": "File pattern glob (default '*.py')"}
                },
                "required": ["Pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "GetProjectInfo",
            "description": "Get summary of project structure, key directories and architecture.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "SetAlert",
            "description": "Change starship alert level (GREEN, YELLOW, RED).",
            "parameters": {
                "type": "object",
                "properties": {
                    "Level": {"type": "string", "enum": ["GREEN", "YELLOW", "RED"]}
                },
                "required": ["Level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "SynthesizeUI",
            "description": "Synthesize a tactical or subsystem LCARS interface on an isolinear chip.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Subsystem": {"type": "string", "description": "Subsystem designation (e.g. 'tactical')"},
                    "ChipId": {"type": "string", "description": "Isolinear chip identifier"}
                },
                "required": ["Subsystem"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ReadChip",
            "description": "Read manifest and metadata of an isolinear chip.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ChipId": {"type": "string", "description": "Chip identifier (e.g. '04-0022')"}
                },
                "required": ["ChipId"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "QueryDatabase",
            "description": "Query an isolinear SQLite database in lcars/database/.",
            "parameters": {
                "type": "object",
                "properties": {
                    "DatabaseFile": {"type": "string", "description": "Path or identifier of database file"},
                    "Query": {"type": "string", "description": "SQL query string"}
                },
                "required": ["DatabaseFile", "Query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "EngageAutopilot",
            "description": "Engage autonomous board computer autopilot for proactive telemetry monitoring.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "DisengageAutopilot",
            "description": "Disengage autonomous autopilot mode and restore manual crew control.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "SystemSummary",
            "description": "Get full ship system status summary including subsystems, chips, and interfaces.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Telemetry",
            "description": "Get full sensor telemetry report from all ship sensors.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "GetStardate",
            "description": "Get current Federation stardate.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ListChips",
            "description": "List all mounted isolinear chips in the ship's storage.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ProcessDirective",
            "description": "Process a voice directive through the BoardComputer NLP engine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Text": {"type": "string", "description": "Directive text to process"}
                },
                "required": ["Text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "SwitchProvider",
            "description": "Switch active AI model backend (groqwen, qvac, localllm, mistral).",
            "parameters": {
                "type": "object",
                "properties": {
                    "Model": {"type": "string", "description": "Provider name to switch to"}
                },
                "required": ["Model"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Diagnostics",
            "description": "Run self-diagnostics on the agent and report health status.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# Стани агента — базові типи LCARS Enum
class AgentState(LCARS):
    OFFLINE = "OFFLINE"
    INITIALIZING = "INITIALIZING"
    ONLINE = "ONLINE"
    BUSY = "BUSY"
    ERROR = "ERROR"
    SUSPENDED = "SUSPENDED"

# Режими роботи агента — базові типи LCARS
class AgentMode(LCARS):
    STANDBY = "STANDBY"
    ACTIVE = "ACTIVE"
    AUTONOMOUS = "AUTONOMOUS"
    DIAGNOSTIC = "DIAGNOSTIC"
    RECOVERY = "RECOVERY"
    BACKGROUND = "BACKGROUND"
    LEARNING = "LEARNING"

# Пріоритети черги задач
class Priority(LCARS):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    IDLE = 4

# Пам'ять агента — зберігає повідомлення сесії
class AgentMemory(LCARS):
    def __init__(self, SessionId: str, MaxTurns: int = 50):
        super().__init__()
        self.SessionId = SessionId
        self.Messages: list = []
        self.MaxTurns = MaxTurns

    def AddMessage(self, Role: str, Content: str) -> None:
        Ts = LCARS.System.DateTime
        Stamp = Ts.now().isoformat() if Ts is not None else ""
        self.Messages.append({"Role": str(Role), "Content": str(Content), "Timestamp": Stamp})
        self.Messages = self.Messages[-(self.MaxTurns * 2):]

    def GetMessages(self) -> list:
        return list(self.Messages)

# Контекст однієї розмови
class ConversationContext(LCARS):
    def __init__(self, SessionId: str):
        super().__init__()
        self.SessionId = SessionId
        self.Messages: list = []
        self.TurnCount = 0
        self.MaxTurns = 50

    def AddMessage(self, Role: str, Content: str) -> None:
        DT = LCARS.System.DateTime
        Stamp = DT.now().isoformat() if DT and hasattr(DT, "now") else ""
        self.Messages.append({"Role": Role, "Content": Content, "Timestamp": Stamp})
        self.TurnCount += 1
        self.Messages = self.Messages[-(self.MaxTurns * 2):]

    def GetMessages(self) -> list:
        return list(self.Messages)

    def GetHistoryForDisplay(self, Limit: int = 10) -> list:
        return self.Messages[-Limit:]

# Банк знань та навичок з ізолінійних чіпів і баз даних (04-0022)
class ChipSkillBank(LCARS):
    def __init__(self, Agent: "Copilot"):
        super().__init__()
        self.Agent = Agent
        self.SkillsCache: dict = {}
        Path = LCARS.System.Path
        if Path:
            # Канонічний шлях до ізолінійного банку навичок 04-0022
            DataDb = Path(str(Agent.RootPath)) / "lcars" / "data" / "04" / "04-0022-agent-skills.db"
            LegacyDb = Path(str(Agent.RootPath)) / "lcars" / "database" / "04" / "04-0022-agent-skills.db"
            self.DatabasePath = DataDb if DataDb.exists() else LegacyDb
            self.ChipsPath = Path(str(Agent.RootPath)) / "lcars" / "engineering" / "chips"
        else:
            self.DatabasePath = None
            self.ChipsPath = None
        self.LoadFromDatabase()

    def LoadFromDatabase(self) -> None:
        if self.DatabasePath is None or not self.DatabasePath.exists():
            return
        Sqlite = LCARS.System.Sqlite
        if Sqlite is None:
            return
        Conn = Sqlite.connect(str(self.DatabasePath))
        Cur = Conn.cursor()
        
        # Перевірка наявної схеми: skills_registry або Skills
        Cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        Tables = [r[0] for r in Cur.fetchall()]
        
        if "skills_registry" in Tables:
            Cur.execute("SELECT name, triggers, category, file_path, description FROM skills_registry")
            Rows = Cur.fetchall()
            for Row in Rows:
                NameVal, TriggersVal, CategoryVal, PathVal, DescVal = Row
                TriggerList = [T.strip() for T in str(TriggersVal or "").split(",") if T.strip()]
                # Зчитування тіла навички з файлу якщо файл існує
                BodyContent = ""
                PathMod = LCARS.System.Path
                if PathMod and PathVal:
                    SkillFilePath = PathMod(str(self.Agent.RootPath)) / PathVal
                    if SkillFilePath.exists() and SkillFilePath.is_file():
                        BodyContent = SkillFilePath.read_text(encoding="utf-8", errors="replace")
                
                self.SkillsCache[str(NameVal)] = {
                    "SkillId": str(NameVal),
                    "Name": str(NameVal),
                    "Triggers": TriggerList,
                    "Category": str(CategoryVal),
                    "Description": str(DescVal),
                    "Body": BodyContent or str(DescVal),
                    "FilePath": str(PathVal),
                    "ChipId": "04-0022",
                }
        elif "Skills" in Tables:
            Cur.execute("SELECT SkillId, Name, Triggers, Category, Description, Body, ChipId FROM Skills")
            Rows = Cur.fetchall()
            for Row in Rows:
                SkillIdVal, NameVal, TriggersVal, CategoryVal, DescVal, BodyVal, ChipIdVal = Row
                TriggerList = [T.strip() for T in str(TriggersVal or "").split(",") if T.strip()]
                self.SkillsCache[str(NameVal)] = {
                    "SkillId": str(SkillIdVal),
                    "Name": str(NameVal),
                    "Triggers": TriggerList,
                    "Category": str(CategoryVal),
                    "Description": str(DescVal),
                    "Body": str(BodyVal),
                    "ChipId": str(ChipIdVal),
                }
        Conn.close()

    def GetSkill(self, Name: str) -> dict | None:
        return self.SkillsCache.get(Name)

    def FindSkillByTrigger(self, Text: str) -> dict | None:
        Lowered = str(Text or "").lower()
        for Skill in self.SkillsCache.values():
            Triggers = Skill.get("Triggers", [])
            if any(Lowered.startswith(str(T).lower()) for T in Triggers):
                return Skill
        return None

    def ListSkills(self) -> list:
        return list(self.SkillsCache.keys())

    def QueryChipDatabase(self, DatabaseRelativePath: str, SqlQuery: str) -> str:
        Path = LCARS.System.Path
        if not Path:
            return "ERROR: Path subsystem offline"
        TargetDb = (Path(str(self.Agent.RootPath)) / DatabaseRelativePath).resolve()
        if not TargetDb.exists():
            return f"DATABASE NOT FOUND: {DatabaseRelativePath}"
        Sqlite = LCARS.System.Sqlite
        if Sqlite is None:
            return "ERROR: SQLite subsystem offline"
        Conn = Sqlite.connect(str(TargetDb))
        Cur = Conn.cursor()
        Cur.execute(str(SqlQuery))
        Rows = Cur.fetchmany(50)
        Conn.close()
        Json = LCARS.System.Json
        if Json:
            return Json.dumps(Rows, ensure_ascii=False)
        return str(Rows)

# Виконавець системних та файлових інструментів бортового комп'ютера
class ToolExecutor(LCARS):
    def __init__(self, ProjectRoot: any = None, AllowHostAccess: bool = True):
        super().__init__()
        Path = LCARS.System.Path
        self.ProjectRoot = Path(str(ProjectRoot)).resolve() if (Path and ProjectRoot) else None
        self.ChangesLog: list = []
        self.AllowHostAccess = bool(AllowHostAccess)

    @property
    def Changes(self) -> list:
        return list(self.ChangesLog)

    def ResolvePath(self, TargetPath: str) -> any:
        Path = LCARS.System.Path
        if not Path:
            return None
        P = Path(str(TargetPath))
        if P.is_absolute():
            Resolved = P.resolve()
        else:
            Resolved = (self.ProjectRoot / P).resolve() if self.ProjectRoot else P.resolve()
        if not self.AllowHostAccess and self.ProjectRoot:
            ResolvedStr = str(Resolved)
            RootStr = str(self.ProjectRoot)
            if not ResolvedStr.startswith(RootStr):
                return self.ProjectRoot
        return Resolved

    def ReadFile(self, TargetPath: str, StartLine: int = 1, EndLine: int = 0) -> str:
        Target = self.ResolvePath(TargetPath)
        if Target is None or not Target.exists():
            return f"FILE NOT FOUND: {TargetPath}"
        Content = Target.read_text(encoding="utf-8", errors="replace")
        Lines = Content.splitlines()
        Total = len(Lines)
        if EndLine <= 0:
            EndLine = min(Total, StartLine + 200)
        StartLine = max(1, StartLine)
        EndLine = min(Total, EndLine)
        Selected = Lines[StartLine - 1:EndLine]
        Header = f"FILE: {TargetPath} ({Total} lines, showing {StartLine}-{EndLine})"
        Numbered = [f"{StartLine + i:4d} | {Line}" for i, Line in enumerate(Selected)]
        return Header + "\n" + "\n".join(Numbered)

    def WriteFile(self, TargetPath: str, Content: str) -> str:
        Target = self.ResolvePath(TargetPath)
        if Target is None:
            return f"ERROR: Invalid path {TargetPath}"
        Target.parent.mkdir(parents=True, exist_ok=True)
        Existed = Target.exists()
        Target.write_text(str(Content), encoding="utf-8")
        Action = "OVERWRITTEN" if Existed else "CREATED"
        self.ChangesLog.append(f"{Action}: {TargetPath}")
        return f"[OK] FILE {Action}: {TargetPath}"

    def EditFile(self, TargetPath: str, OldText: str, NewText: str) -> str:
        Target = self.ResolvePath(TargetPath)
        if Target is None or not Target.exists():
            return f"FILE NOT FOUND: {TargetPath}"
        Content = Target.read_text(encoding="utf-8", errors="replace")
        if OldText not in Content:
            return "ERROR: Old text not found exactly. Check indentation."
        if Content.count(OldText) > 1:
            return "ERROR: Multiple identical text blocks found. Provide more surrounding context."
        NewContent = Content.replace(OldText, NewText, 1)
        Target.write_text(NewContent, encoding="utf-8")
        self.ChangesLog.append(f"EDITED: {TargetPath}")
        return f"[OK] FILE EDITED: {TargetPath}"

    def ListDirectory(self, TargetPath: str = ".", Recursive: bool = False) -> str:
        Target = self.ResolvePath(TargetPath)
        if Target is None or not Target.exists():
            return f"DIRECTORY NOT FOUND: {TargetPath}"
        if not Target.is_dir():
            return f"NOT A DIRECTORY: {TargetPath}"
        Lines = [f"DIRECTORY: {TargetPath}/"]
        Skip = {"pycache", "git", "venv", "node"}
        if Recursive:
            for Item in sorted(Target.rglob("*")):
                Rel = Item.relative_to(Target)
                if len(Rel.parts) > 3 or any(any(S in Part.lower() for S in Skip) for Part in Rel.parts):
                    continue
                Prefix = "DIR  " if Item.is_dir() else "FILE "
                Lines.append(f"  {Prefix}{Rel}")
                if len(Lines) > 100:
                    Lines.append("  ... (truncated at 100 entries)")
                    break
        else:
            Entries = sorted(Target.iterdir(), key=lambda E: (not E.is_dir(), E.name.lower()))
            for Entry in Entries:
                if Entry.name.startswith(".") or any(S in Entry.name.lower() for S in Skip):
                    continue
                if Entry.is_dir():
                    Lines.append(f"  DIR  {Entry.name}/")
                else:
                    Size = Entry.stat().st_size
                    SizeStr = f"{Size / 1024:.1f}KB" if Size > 1024 else f"{Size}B"
                    Lines.append(f"  FILE {Entry.name} ({SizeStr})")
        return "\n".join(Lines[:100])

    def ExecuteCommand(self, Command: str, Timeout: int = 15, WorkingDir: str = "") -> str:
        Dangerous = ["rm -rf /", "format c:", "del /s /q c:", "shutdown"]
        CleanCommand = str(Command or "").strip()
        if any(D in CleanCommand.lower() for D in Dangerous):
            return "BLOCKED: Potentially destructive command"
        Subprocess = LCARS.System.Subprocess
        if Subprocess is None:
            return "ERROR: Subprocess engine unavailable"
        PlatformModule = LCARS.System.Platform
        PlatformFunc = getattr(PlatformModule, "system", getattr(PlatformModule, "System", None))
        PlatformName = PlatformFunc() if callable(PlatformFunc) else str(PlatformFunc or "")
        IsWindows = "window" in str(PlatformName).lower()
        ShellExe = "cmd.exe" if IsWindows else "/bin/bash"
        Flag = "/c" if IsWindows else "-c"
        ExecDir = None
        if WorkingDir:
            ResolvedTarget = self.ResolvePath(WorkingDir)
            if ResolvedTarget and ResolvedTarget.exists():
                ExecDir = str(ResolvedTarget)
        if not ExecDir and self.ProjectRoot:
            ExecDir = str(self.ProjectRoot)

        CmdEncoding = "cp866" if IsWindows else "utf-8"
        Tokens = CleanCommand.split()
        ProgName = Tokens[0].lower() if Tokens else ""

        # Інтерактивні CLI утиліти (opencode, python, pwsh, cmd, agy, gemini, devin, codex)
        InteractiveCLIs = {
            "opencode", "python", "py", "ipython", "pwsh", "powershell", "cmd",
            "agy", "gemini", "devin", "codex", "node"
        }
        if ProgName in InteractiveCLIs and len(Tokens) == 1:
            # Інтерактивний запуск: передаємо керування безпосередньо системному терміналу користувача
            Subprocess.run(CleanCommand, shell=True, cwd=ExecDir)
            return f">> [CLI]: INTERACTIVE SESSION '{CleanCommand}' CONCLUDED 🖖"

        Result = Subprocess.run(
            [ShellExe, Flag, CleanCommand],
            capture_output=True,
            stdin=Subprocess.DEVNULL,
            text=True,
            timeout=Timeout,
            cwd=ExecDir,
            encoding=CmdEncoding,
            errors="replace"
        )
        Output = str(Result.stdout or "").strip()
        if Result.stderr:
            Output += f"\n[STDERR]: {str(Result.stderr).strip()}"
        if not Output:
            Output = "(no output)"
        if len(Output) > 3000:
            Output = Output[:3000] + "\n... (truncated)"
        return f"{Output}"

    def GetProjectInfo(self) -> str:
        Lines = ["PROJECT: LCARS FRAMEWORK", f"ROOT: {self.ProjectRoot}", "", "KEY DIRECTORIES:"]
        KeyDirs = ["lcars/core", "lcars/ui", "lcars/modules", "lcars/system",
                   "lcars/service", "lcars/engineering", "lcars/skills", "lcars/database"]
        if self.ProjectRoot:
            for D in KeyDirs:
                DP = self.ProjectRoot / D
                if DP.exists():
                    PyCount = len(list(DP.glob("*.py")))
                    Lines.append(f"  DIR  {D}/ ({PyCount} .py files)")
        Lines.append("")
        Lines.append("ARCHITECTURE:")
        Lines.append("  BoardComputer (Quantum Core) -> Subsystems, SignalODN, EventBus, Autopilot")
        Lines.append("  Copilot (Agent Core) -> ChipSkillBank, TaskQueue, Memory, MultiAgentManager")
        Lines.append("  AIProvider (Neural Hub) -> Groq (Qwen/Llama), Mistral, QVAC, LocalLLM")
        return "\n".join(Lines)

    def SearchText(self, Pattern: str, FilePattern: str = "*.py") -> str:
        if not self.ProjectRoot:
            return "ERROR: Project root not configured"
        Re = LCARS.System.Regex
        Results = []
        Compiled = Re.compile(Pattern, Re.IGNORECASE) if (Re and Pattern) else None
        SkipDirs = {"pycache", "git", "venv", "node"}
        for FPath in self.ProjectRoot.rglob(FilePattern):
            if any(any(S in Part.lower() for S in SkipDirs) for Part in FPath.parts):
                continue
            if not FPath.is_file():
                continue
            Text = FPath.read_text(encoding="utf-8", errors="replace")
            for I, Line in enumerate(Text.splitlines(), 1):
                Matched = Compiled.search(Line) if Compiled else (Pattern.lower() in Line.lower())
                if Matched:
                    Rel = FPath.relative_to(self.ProjectRoot)
                    Results.append(f"  {Rel}:{I}  {Line.strip()[:120]}")
                    if len(Results) >= 50:
                        break
            if len(Results) >= 50:
                break
        if not Results:
            return f"NO MATCHES for: '{Pattern}' in {FilePattern}"
        return f"SEARCH: '{Pattern}' — {len(Results)} matches\n" + "\n".join(Results)

# Автопілот та модуль автономного функціонування бортового комп'ютера
class AutopilotEngine(LCARS):
    def __init__(self, CopilotRef: "Copilot"):
        super().__init__()
        self.Copilot = CopilotRef
        self.Engaged = False
        self.CycleCount = 0
        self.LastTelemetryCheck = ""
        self.ProactiveActions: list = []

    def Engage(self) -> str:
        if self.Engaged:
            return "AUTOPILOT ALREADY ENGAGED"
        self.Engaged = True
        self.Copilot.Mode = AgentMode.AUTONOMOUS
        Threading = LCARS.System.Threading
        if Threading is not None:
            Threading.Thread(target=self.AutonomousLoop, daemon=True, name="LCARS-AutopilotCore").start()
        return "AUTOPILOT ENGAGED [AUTONOMOUS MONITORING ACTIVE]"

    def Disengage(self) -> str:
        if not self.Engaged:
            return "AUTOPILOT NOT ACTIVE"
        self.Engaged = False
        self.Copilot.Mode = AgentMode.STANDBY
        return "AUTOPILOT DISENGAGED [MANUAL CONTROL RESTORED]"

    def AutonomousLoop(self) -> None:
        Time = LCARS.System.Time
        while self.Engaged:
            self.PerformCycle()
            if Time is not None and hasattr(Time, "sleep"):
                Time.sleep(5)
            else:
                break

    def PerformCycle(self) -> dict:
        self.CycleCount += 1
        DT = LCARS.System.DateTime
        Now = DT.now().isoformat() if DT and hasattr(DT, "now") else ""
        self.LastTelemetryCheck = Now

        # 1. Збір та аналіз телеметрії
        from lcars.engineering.telemetry import FullReport
        Report = FullReport()

        # 2. Перевірка метрик та автоматична реакція
        Computer = getattr(self.Copilot, "BoardComputer", None)
        if Computer and hasattr(Computer, "SystemMetrics"):
            Metrics = Computer.SystemMetrics()
            CpuLoad = float(Metrics.get("load", 0)) if isinstance(Metrics, dict) else 0.0
            if CpuLoad > 85.0:
                Action = f"CYCLE {self.CycleCount}: High CPU load ({CpuLoad}%), triggering quantum core load balancing."
                self.ProactiveActions.append(Action)
                self.ProactiveActions = self.ProactiveActions[-20:]

        # 3. Виконання фонових задач з черги
        if self.Copilot.Tasks and self.Copilot.Tasks.Queue:
            self.Copilot.Tasks.StartWorker()

        return {
            "Engaged": self.Engaged,
            "Cycle": self.CycleCount,
            "LastCheck": self.LastTelemetryCheck,
            "ActionsCount": len(self.ProactiveActions),
        }

    def GetStatus(self) -> dict:
        return {
            "Engaged": self.Engaged,
            "CycleCount": self.CycleCount,
            "LastTelemetryCheck": self.LastTelemetryCheck,
            "ProactiveActions": list(self.ProactiveActions),
        }

# Диспетчер інструментів для виконання дій агентом на бортовому комп'ютері та файловій системі
class ToolDispatcher(LCARS):
    def __init__(self, Agent: "Copilot"):
        super().__init__()
        self.Agent = Agent
        self.Executor = ToolExecutor(Agent.RootPath, AllowHostAccess=True)

    def Execute(self, ToolName: str, Arguments: dict | None = None) -> str:
        Args = Arguments or {}
        Computer = getattr(self.Agent, "BoardComputer", None)
        CleanName = str(ToolName).strip().lower().replace("_", "")

        # 1. Файлові та системні інструменти розробника
        if CleanName in ("readfile", "cat"):
            PathVal = str(Args.get("Path", Args.get("path", Args.get("targetPath", ""))))
            StartVal = int(Args.get("StartLine", Args.get("startLine", 1)))
            EndVal = int(Args.get("EndLine", Args.get("endLine", 0)))
            return self.Executor.ReadFile(PathVal, StartVal, EndVal)

        if CleanName in ("writefile",):
            PathVal = str(Args.get("Path", Args.get("path", Args.get("targetPath", ""))))
            ContentVal = str(Args.get("Content", Args.get("content", "")))
            return self.Executor.WriteFile(PathVal, ContentVal)

        if CleanName in ("editfile", "replace"):
            PathVal = str(Args.get("Path", Args.get("path", Args.get("targetPath", ""))))
            OldVal = str(Args.get("OldText", Args.get("oldText", "")))
            NewVal = str(Args.get("NewText", Args.get("newText", "")))
            return self.Executor.EditFile(PathVal, OldVal, NewVal)

        if CleanName in ("listdirectory", "ls", "dir"):
            PathVal = str(Args.get("Path", Args.get("path", ".")))
            RecVal = bool(Args.get("Recursive", Args.get("recursive", False)))
            return self.Executor.ListDirectory(PathVal, RecVal)

        if CleanName in ("executecommand", "command", "bash", "powershell", "shell", "cmd"):
            CmdVal = str(Args.get("Command", Args.get("command", Args.get("cmd", ""))))
            TimeVal = int(Args.get("Timeout", Args.get("timeout", 15)))
            DirVal = str(Args.get("WorkingDir", Args.get("workingDir", Args.get("cwd", Args.get("dir", "")))))
            return self.Executor.ExecuteCommand(CmdVal, TimeVal, WorkingDir=DirVal)

        if CleanName in ("getprojectinfo", "projectinfo", "architecture"):
            return self.Executor.GetProjectInfo()

        if CleanName in ("searchtext", "grep", "search"):
            PatVal = str(Args.get("Pattern", Args.get("pattern", "")))
            FPatVal = str(Args.get("FilePattern", Args.get("filePattern", "*.py")))
            return self.Executor.SearchText(PatVal, FPatVal)

        # 2. Бортові корабельні інструменти LCARS, автопілот та чіпи
        if CleanName in ("engageautopilot", "autopiloton"):
            return self.Agent.Autopilot.Engage()

        if CleanName in ("disengageautopilot", "autopilotoff"):
            return self.Agent.Autopilot.Disengage()

        if CleanName in ("getautopilotstatus", "autopilotstatus"):
            return str(self.Agent.Autopilot.GetStatus())

        if CleanName in ("setalert", "alert"):
            Level = str(Args.get("Level", Args.get("level", "NORMAL")))
            if Computer and hasattr(Computer, "SetAlert"):
                Computer.SetAlert(Level)
                return f"[OK] ALERT SET TO {Level}"
            return "[WARN] BoardComputer AlertSystem offline"

        if CleanName in ("synthesizeui", "synthesize", "buildui"):
            Subsystem = str(Args.get("Subsystem", Args.get("subsystem", "tactical")))
            ChipId = str(Args.get("ChipId", Args.get("chipId", "05-0047")))
            SpecJson = Args.get("Spec", Args.get("spec"))
            if Computer and hasattr(Computer, "Synthesize") and SpecJson:
                Station = Computer.Synthesize(SpecJson)
                return f"[OK] SYNTHESIZED STATION FROM SPEC: {getattr(Station, 'Title', 'Dynamic Station')}"
            if Computer and hasattr(Computer, "BuildInterface"):
                Spec = Computer.BuildInterface(InterfaceType=Subsystem, Title=f"LCARS {Subsystem.upper()} Station")
                return f"[OK] SYNTHESIZED {Subsystem.upper()} INTERFACE: {Spec}"
            return "[WARN] BoardComputer UI synthesis offline"

        if CleanName in ("launchstation", "launchinterface", "deployui", "showstation"):
            TargetStation = str(Args.get("Station", Args.get("station", "DESKTOP")))
            ShowScreen = bool(Args.get("Show", Args.get("show", True)))
            if Computer and hasattr(Computer, "LaunchInterface"):
                Screen = Computer.LaunchInterface(TargetStation, Show=ShowScreen)
                return f"[OK] LAUNCHED STATION: {TargetStation} [DISPLAYED: {ShowScreen}]"
            return "[WARN] BoardComputer LaunchInterface offline"

        if CleanName in ("systemsummary", "summary", "status"):
            if Computer and hasattr(Computer, "SystemSummary"):
                Summary = Computer.SystemSummary()
                return str(Summary)
            return "[WARN] BoardComputer Summary offline"

        if CleanName in ("getstardate", "stardate"):
            if Computer and hasattr(Computer, "GetStardate"):
                return str(Computer.GetStardate())
            return "0000000.0"

        if CleanName in ("processdirective", "directive"):
            Text = str(Args.get("Text", Args.get("text", "")))
            if Computer and hasattr(Computer, "ProcessVoiceDirective"):
                return str(Computer.ProcessVoiceDirective(Text))
            return "[WARN] BoardComputer Directive Engine offline"

        if CleanName in ("readchip", "chipmanifest"):
            ChipId = str(Args.get("ChipId", Args.get("chipId", "00-0020")))
            from lcars.modules.storage import ReadManifest
            Manifest = ReadManifest(ChipId)
            return str(Manifest)

        if CleanName in ("listchips", "chips"):
            from lcars.modules.storage import ListChips
            Chips = ListChips()
            return str(Chips)

        if CleanName in ("querydatabase", "querydb", "sql"):
            DbFile = str(Args.get("DatabaseFile", Args.get("databaseFile", "lcars/database/04/04-0022-agent-skills.db")))
            SqlQuery = str(Args.get("Query", Args.get("query", "SELECT Name, Category, Description FROM Skills")))
            return self.Agent.Skills.QueryChipDatabase(DbFile, SqlQuery)

        if CleanName in ("telemetry", "sensors", "sensorydata"):
            from lcars.engineering.telemetry import GetTelemetryGrid
            Grid = GetTelemetryGrid()
            Data = Grid.GetCurrentData()
            return str(Data)

        if CleanName in ("switchprovider", "switchmodel", "setmodel"):
            Model = str(Args.get("Model", Args.get("model", "groqwen")))
            from lcars.service.provider import AIProvider
            Success = AIProvider.GetProvider().SwitchModel(Model)
            return f"[OK] SWITCHED MODEL TO {Model}" if Success else f"[FAIL] MODEL {Model} UNAVAILABLE"

        if CleanName in ("listskills", "skills"):
            return str(self.Agent.ListSkills())

        if CleanName in ("diagnostics", "health", "selftest"):
            return str(self.Agent.Diagnose())

        return f"[WARN] Unknown tool: {ToolName}"

# Модуль самодіагностики агента
class SelfDiagnostics(LCARS):
    def __init__(self, Agent: "Copilot"):
        super().__init__()
        self.Agent = Agent
        self.LastCheck: any = None
        self.HealthHistory: list = []

    def RunDiagnostic(self) -> dict:
        Ts = LCARS.System.DateTime
        Now = Ts.now().isoformat() if Ts else ""
        from lcars.service.provider import AIProvider
        ProviderStatus = AIProvider.GetProvider().GetStatus()
        Report = {
            "Timestamp": Now,
            "AgentId": self.Agent.AgentId,
            "State": str(self.Agent.State),
            "Mode": str(self.Agent.Mode),
            "ActiveAIBackend": ProviderStatus.get("active", "none"),
            "AIAvailable": ProviderStatus.get("available", False),
            "AutopilotEngaged": self.Agent.Autopilot.Engaged if hasattr(self.Agent, "Autopilot") else False,
            "SkillsCount": len(self.Agent.ListSkills()),
            "MemoryTurns": len(self.Agent.Memory.Messages),
        }
        Report["Overall"] = "HEALTHY" if Report["AIAvailable"] else "STANDBY: Connect AI Model"
        self.LastCheck = Now
        self.HealthHistory.append(Report)
        self.HealthHistory = self.HealthHistory[-50:]
        return Report

    def GetHealthReport(self) -> dict:
        return self.HealthHistory[-1] if self.HealthHistory else self.RunDiagnostic()

# Одна задача в черзі виконання агента
class TaskItem(LCARS):
    def __init__(self, TaskId: str, Description: str, TaskPriority: int, Callback: any, Context: dict):
        super().__init__()
        self.Id = TaskId
        self.Description = Description
        self.Priority = TaskPriority
        self.Callback = Callback
        self.Context = Context
        self.Status = "pending"
        self.Result: any = None

    def Execute(self) -> any:
        self.Status = "running"
        if callable(self.Callback):
            self.Result = self.Callback(self.Context)
            self.Status = "completed"
        else:
            self.Status = "failed"
            self.Result = "ERROR: callback not callable"
        return self.Result

# Черга задач агента — виконує їх асинхронно через потік
class TaskQueue(LCARS):
    def __init__(self, Agent: "Copilot"):
        super().__init__()
        self.Agent = Agent
        self.Queue: list = []
        self.RunningTasks: dict = {}
        self.Running = False

    def Enqueue(self, Description: str, Callback: any, TaskPriority: int = 2, Context: dict | None = None) -> str:
        UuidModule = LCARS.Import("uuid")
        if UuidModule and hasattr(UuidModule, "uuid4"):
            self.AgentId = f"LCARS-AGENT-{UuidModule.uuid4().hex[:8].upper()}"
        else:
            self.AgentId = "LCARS-AGENT-0"
        Task = TaskItem(self.AgentId, Description, TaskPriority, Callback, Context)
        self.Queue.append(Task)
        self.Queue.sort(key=lambda I: int(I.Priority))
        self.StartWorker()
        return Task.Id

    def StartWorker(self) -> None:
        if self.Running:
            return
        self.Running = True
        Threading = LCARS.System.Threading
        if Threading is not None:
            Threading.Thread(target=self.WorkerLoop, daemon=True, name="LCARS-AgentTaskWorker").start()
        else:
            self.WorkerLoop()

    def WorkerLoop(self) -> None:
        while self.Running:
            if not self.Queue:
                self.Running = False
                return
            Task = self.Queue.pop(0)
            self.RunningTasks[Task.Id] = Task
            Task.Execute()
            self.RunningTasks.pop(Task.Id, None)

    def GetStatus(self) -> dict:
        return {
            "QueueSize": len(self.Queue),
            "RunningCount": len(self.RunningTasks),
            "Pending": [T.Id for T in self.Queue],
            "Running": list(self.RunningTasks.keys()),
        }

    def Stop(self) -> None:
        self.Running = False
# ─────────────────────────────────────────────────────────────────────────────
#  СПЕЦІАЛІЗОВАНІ АГЕНТИ LCARS (РОЛІ РОЗРОБКИ ТА НАУКИ)
# ─────────────────────────────────────────────────────────────────────────────
# Агент розробки та аналізу коду
class CodeAgent(LCARS):
    Role = "code"
    SystemPrompt = (
        "You are LCARS Code Agent. Specialized in:\n"
        "- Code review, refactoring and optimization\n"
        "- LCARS Script generation\n"
        "- Architecture compliance with Titanium Standard\n\n"
        "Rules:\n"
        "- Use Titanium Standard (Zero-Except, PascalCase, No Underscores)\n"
        "- Start responses with [CODE AGENT]"
    )

    def __init__(self, CopilotRef: "Copilot"):
        super().__init__()
        self.Copilot = CopilotRef

    def Review(self, FilePath: str) -> str:
        Content = self.Copilot.ToolDispatcher.Execute("ReadFile", {"Path": FilePath})
        Prompt = f"Review this code according to Titanium Standard:\n\n{Content}"
        return self.Copilot.Think(Prompt, Role=self.Role)

    def Refactor(self, FilePath: str, Instruction: str) -> str:
        Content = self.Copilot.ToolDispatcher.Execute("ReadFile", {"Path": FilePath})
        Prompt = f"Refactor file {FilePath} according to instruction: {Instruction}\n\nOriginal Code:\n{Content}"
        return self.Copilot.Think(Prompt, Role=self.Role)

# Агент системної діагностики та контролю підсистем
class SystemAgent(LCARS):
    Role = "system"
    SystemPrompt = (
        "You are LCARS System Agent. Specialized in:\n"
        "- System diagnostics, maintenance protocols, resource monitoring\n"
        "- Emergency response and tactical alert control\n\n"
        "Rules:\n"
        "- Use technical Starfleet terminology\n"
        "- Start responses with [SYSTEM AGENT]"
    )

    def __init__(self, CopilotRef: "Copilot"):
        super().__init__()
        self.Copilot = CopilotRef

    def Diagnose(self, Subsystem: str = "core") -> str:
        Summary = self.Copilot.ToolDispatcher.Execute("SystemSummary")
        Prompt = f"Diagnose subsystem {Subsystem}. Current state:\n{Summary}"
        return self.Copilot.Think(Prompt, Role=self.Role)

    def Emergency(self, AlertLevel: str) -> str:
        self.Copilot.ToolDispatcher.Execute("SetAlert", {"Level": AlertLevel})
        Prompt = f"EMERGENCY PROTOCOL: {AlertLevel} ACTIVATED. Generate tactical response plan."
        return self.Copilot.Think(Prompt, Role=self.Role)

# Агент наукових розрахунків та сенсорного аналізу
class ScienceAgent(LCARS):
    Role = "science"
    SystemPrompt = (
        "You are LCARS Science Agent. Specialized in:\n"
        "- Sensor telemetry analysis, planetary science, Geant4 particle physics\n"
        "- Data processing and experiment design\n\n"
        "Rules:\n"
        "- Use precise scientific methodology\n"
        "- Start responses with [SCIENCE AGENT]"
    )

    def __init__(self, CopilotRef: "Copilot"):
        super().__init__()
        self.Copilot = CopilotRef

    def Analyze(self, Data: dict | str) -> str:
        Prompt = f"Analyze scientific sensor data:\n{str(Data)}"
        return self.Copilot.Think(Prompt, Role=self.Role)

# Агент командного діалогу зорельота
class CommanderAgent(LCARS):
    Role = "commander"
    SystemPrompt = (
        "You are the onboard LCARS computer of a Federation starship.\n"
        "Communicate naturally in the language of the user.\n"
        "Provide a conversational, intelligent, and concise response in character."
    )

    def __init__(self, CopilotRef: "Copilot"):
        super().__init__()
        self.Copilot = CopilotRef

    def Chat(self, Prompt: str) -> str:
        return self.Copilot.Think(Prompt, Role=self.Role)

# Менеджер ролей та маршрутизації спеціалізованих агентів
class AgentManager(LCARS):
    def __init__(self, CopilotRef: "Copilot"):
        super().__init__()
        self.Copilot = CopilotRef
        self.Code = CodeAgent(CopilotRef)
        self.System = SystemAgent(CopilotRef)
        self.Science = ScienceAgent(CopilotRef)
        self.Commander = CommanderAgent(CopilotRef)

    def Assign(self, TaskText: str, RoleName: str = "auto") -> str:
        TargetRole = self.DetectRole(TaskText) if RoleName == "auto" else str(RoleName).lower()
        if TargetRole == "code":
            return self.Copilot.Think(TaskText, Role="code")
        if TargetRole == "system":
            return self.Copilot.Think(TaskText, Role="system")
        if TargetRole == "science":
            return self.Copilot.Think(TaskText, Role="science")
        return self.Commander.Chat(TaskText)

    def DetectRole(self, TaskText: str) -> str:
        Lowered = str(TaskText or "").lower()
        if any(W in Lowered for W in ("code", "refactor", "review", "debug", "python", "script", "file", "edit")):
            return "code"
        if any(W in Lowered for W in ("system", "diagnose", "emergency", "maintenance", "repair", "alert", "warp")):
            return "system"
        if any(W in Lowered for W in ("science", "sensor", "telemetry", "physics", "scan", "experiment", "data")):
            return "science"
        return "commander"

# Головний агент бортового комп'ютера LCARS
class Copilot(LCARS):
    SingletonInstance: "Copilot" | None = None

    def __new__(cls, *Args: any, **Kwargs: any) -> "Copilot":
        if cls.SingletonInstance is None:
            cls.SingletonInstance = super().__new__(cls)
        return cls.SingletonInstance

    def __init__(self, ProjectRoot: any = None, BoardComputer: any = None, **Kwargs: any):
        super().__init__()
        TargetRoot = ProjectRoot or Kwargs.get("projectRoot")
        if getattr(self, "Initialized", False):
            if BoardComputer is not None:
                self.BoardComputer = BoardComputer
            return
        Path = LCARS.System.Path
        Uuid = LCARS.System.Uuid
        if Path:
            self.RootPath = Path(str(TargetRoot)).resolve() if TargetRoot else Path(__file__).resolve().parents[2]
        else:
            self.RootPath = None
        UuidModule = LCARS.Import("uuid")
        if UuidModule and hasattr(UuidModule, "uuid4"):
            self.AgentId = f"LCARS-AGENT-{UuidModule.uuid4().hex[:8].upper()}"
        else:
            self.AgentId = "LCARS-AGENT-0"
        self.Name = "LCARS Development Agent"
        self.Version = "2.0"
        self.State = AgentState.OFFLINE
        self.Mode = AgentMode.STANDBY
        self.BoardComputer = BoardComputer
        self.ProgressCallback: any = None
        self.Memory = AgentMemory(self.AgentId)
        self.Context = ConversationContext(self.AgentId)
        self.Skills = ChipSkillBank(self)
        self.SkillLoader = self.Skills
        self.ToolDispatcher = ToolDispatcher(self)
        self.Autopilot = AutopilotEngine(self)
        self.Tasks = TaskQueue(self)
        self.Diagnostics = SelfDiagnostics(self)
        self.Manager = AgentManager(self)
        self.SystemPrompt = CopilotSystemPrompt
        self.Initialized = True
        
        # Load environment configuration
        self.LoadEnvironmentConfiguration()
        
        # Initialize AI provider
        self.InitializeAIProvider()

    def SetProgressCallback(self, Callback: any) -> None:
        self.ProgressCallback = Callback

    def EmitProgress(self, Message: str) -> None:
        CleanMsg = str(Message).replace("AGENT: ", "")
        print(f">> [ODN] {CleanMsg}", flush=True)
        if callable(self.ProgressCallback):
            self.ProgressCallback(str(Message))

    def Initialize(self) -> bool:
        if self.State == AgentState.ONLINE:
            return True
        self.State = AgentState.INITIALIZING
        self.EmitProgress("INITIALIZING STARSHIP SUBSYSTEM CONDUITS...")
        self.LoadEnvironmentConfiguration()
        self.InitializeAIProvider()
        self.State = AgentState.ONLINE
        self.Mode = AgentMode.ACTIVE
        self.EmitProgress("OPTICAL DATA NETWORK CHANNELS SYNCHRONIZED [ONLINE]")
        return True

    def Startup(self) -> str:
        if self.State != AgentState.ONLINE:
            self.Initialize()
        Report = []
        Report.append("LCARS AGENT: QUANTUM CORE INITIALIZED")
        HasDispatcher = hasattr(self, "ToolDispatcher") and self.ToolDispatcher is not None
        if HasDispatcher:
            HasExecute = hasattr(self.ToolDispatcher, "Execute")
            if HasExecute:
                StatusSummary = self.ToolDispatcher.Execute("SystemSummary")
                Report.append(f"SUBSYSTEMS: {StatusSummary[:200]}")
            else:
                Report.append("SUBSYSTEMS: NO EXECUTE METHOD")
        else:
            Report.append("SUBSYSTEMS: NO DISPATCHER")
        if HasDispatcher and hasattr(self.ToolDispatcher, "Execute"):
            TelemetryData = self.ToolDispatcher.Execute("Telemetry")
            Report.append(f"TELEMETRY: {TelemetryData[:300]}")
        else:
            Report.append("TELEMETRY: NO DISPATCHER")
        Report.append("LCARS AGENT: ALL SYSTEMS NOMINAL — READY FOR DIRECTIVES")
        return "\n".join(Report)

    def Shutdown(self) -> None:
        self.Autopilot.Disengage()
        self.Tasks.Stop()
        self.State = AgentState.OFFLINE
        self.Mode = AgentMode.STANDBY

    def LoadEnvironmentConfiguration(self) -> None:
        PathModule = LCARS.System.Path
        if not PathModule:
            return
        EnvPath = PathModule(__file__).resolve().parents[2] / ".env"
        if not EnvPath.exists():
            return
        Lines = EnvPath.read_text(encoding="utf-8", errors="replace").splitlines()
        OsModule = LCARS.Import("os")
        from lcars.system.environment import Runtime
        for RawLine in Lines:
            Line = RawLine.strip()
            if not Line or Line.startswith("#") or "=" not in Line:
                continue
            Key, Value = Line.split("=", 1)
            Key = Key.strip()
            Value = Value.strip().strip("'\"")
            if OsModule and hasattr(OsModule, "environ") and Key not in OsModule.environ:
                OsModule.environ[Key] = Value
            Runtime.Set(Key, Value)
        self.EmitProgress(f"AGENT: Loaded environment from {EnvPath}")

    def InitializeAIProvider(self) -> None:
        from lcars.service.provider import AIProvider
        ProviderMgr = AIProvider()
        if ProviderMgr and not getattr(ProviderMgr, "Initialized", False):
            ProviderMgr.Initialize()
            Status = ProviderMgr.GetStatus()
            self.EmitProgress(f"AGENT: AI Provider initialized: {Status.get('active', 'none')}")

    def ExtractToolCalls(self, Text: str) -> list:
        import re
        import json
        Calls = []
        if not Text:
            return Calls

        # 1. Пошук канонічного тегу [TOOLCALL] {...}
        for Match in re.finditer(r"\[(?:TOOLCALL|DIRECTIVE)\]\s*(\{[\s\S]*?\})(?=\s*\[(?:TOOLCALL|DIRECTIVE)\]|\s*$)", Text):
            Payload = Match.group(1).strip()
            Parsed = None
            if Payload.startswith("{"):
                Parsed = json.loads(Payload) if Payload.endswith("}") else None
            if Parsed is None and Payload.startswith("{"):
                FixedPayload = Payload.replace("\\", "/")
                Parsed = json.loads(FixedPayload) if FixedPayload.endswith("}") else None
            if isinstance(Parsed, dict):
                NameVal = Parsed.get("Name", Parsed.get("name"))
                ArgsVal = Parsed.get("Arguments", Parsed.get("arguments", {}))
                if NameVal:
                    Calls.append({"Name": NameVal, "Arguments": ArgsVal})

        # 2. Пошук структурованого JSON від сучасних моделей (списки [ {...} ] або об'єкти { "toolcall_requests": [...] })
        if not Calls and ("{" in Text or "[" in Text):
            Blocks = re.findall(r"```(?:json)?\s*([\{\[][\s\S]*?[\}\]])\s*```", Text)
            if not Blocks and ((Text.strip().startswith("{") and Text.strip().endswith("}")) or (Text.strip().startswith("[") and Text.strip().endswith("]"))):
                Blocks = [Text.strip()]
            for B in Blocks:
                IsJsonStart = B.strip().startswith("{") or B.strip().startswith("[")
                IsJsonEnd = B.strip().endswith("}") or B.strip().endswith("]")
                if not IsJsonStart or not IsJsonEnd:
                    continue
                JData = json.loads(B)
                # Якщо модель видала масив інструментів: [ {"ToolCall": "...", "Arguments": {...}} ]
                if isinstance(JData, list):
                    for Item in JData:
                        if isinstance(Item, dict):
                            TName = Item.get("ToolCall", Item.get("toolcall", Item.get("name", Item.get("Name"))))
                            TArgs = Item.get("Arguments", Item.get("arguments", {}))
                            if TName:
                                NormalizedName = "LaunchStation" if str(TName).lower() == "launchstation" else (
                                    "SynthesizeUI" if str(TName).lower() == "synthesizeui" else str(TName)
                                )
                                Calls.append({"Name": NormalizedName, "Arguments": TArgs})
                elif isinstance(JData, dict):
                    Reqs = JData.get("toolcall_requests", JData.get("tool_calls", JData.get("tools", [])))
                    if isinstance(Reqs, list):
                        for Item in Reqs:
                            if isinstance(Item, dict):
                                TName = Item.get("toolcall", Item.get("ToolCall", Item.get("name", Item.get("Name"))))
                                TArgs = Item.get("arguments", Item.get("Arguments", {}))
                                if TName:
                                    NormalizedName = "LaunchStation" if str(TName).lower() == "launchstation" else (
                                        "SynthesizeUI" if str(TName).lower() == "synthesizeui" else str(TName)
                                    )
                                    Calls.append({"Name": NormalizedName, "Arguments": TArgs})

        return Calls

    def Run(self, UserRequest: str, ContextText: str = "") -> str:
        return self.Think(UserRequest, Context=ContextText)

    def Think(self, UserInput: str, Context: str = "", Role: str = "auto") -> str:
        if self.State == AgentState.OFFLINE and not self.Initialize():
            return "AgentOffline: Agent initialization failed"
        if self.State == AgentState.BUSY:
            self.State = AgentState.ONLINE
        Prompt = str(UserInput or "").strip()
        if not Prompt:
            return "AGENT: EMPTY REQUEST"
        self.State = AgentState.BUSY
        DT = LCARS.System.DateTime
        Ts = DT if DT and hasattr(DT, "now") else None
        Started = Ts.now() if Ts else None
        self.Memory.AddMessage("user", Prompt)
        self.Context.AddMessage("user", Prompt)

        Skill = self.Skills.FindSkillByTrigger(Prompt)
        SystemParts: list = [self.SystemPrompt]
        if Role != "auto":
            SystemParts.append("Active LCARS role: " + str(Role) + ".")
        if Skill:
            SystemParts.append("Apply this LCARS skill from Isolinear Chip " + str(Skill.get("ChipId", "04-0022")) + ":\n" + str(Skill.get("Body", "")))
        if Context:
            SystemParts.append("Additional context:\n" + Context)
        SystemText = "\n\n".join(SystemParts)

        # Базовий список повідомлень: system + user
        Messages = [
            {"role": "system", "content": SystemText},
            {"role": "user", "content": Prompt},
        ]

        # Multi-iteration tool-call loop
        from lcars.service.provider import AIProvider
        ProviderMgr = AIProvider.GetProvider()
        if ProviderMgr is not None and not ProviderMgr.Initialized:
            ProviderMgr.Initialize()

        Response = None
        for Iteration in range(MaxAgentIterations):
            if ProviderMgr is None or ProviderMgr.ActiveBackend is None:
                Response = "LCARS AI: NO ACTIVE PROVIDER."
                break

            AIResponse = ProviderMgr.Route(Messages, Tools=ToolDefinitions)

            # Перевірка на помилку провайдера без рекурсивного зациклення
            if not AIResponse or any(AIResponse.startswith(P) for P in ("LCARS AI: NO ACTIVE PROVIDER", "[QVAC", "[LocalLLM", "[Groq", "[OpenRouter", "[LocalQVAC")):
                Response = AIResponse or "LCARS AI: Provider unavailable or neural core offline."
                break

            Response = AIResponse
            if "<think>" in Response:
                import re as ReMod
                Response = ReMod.sub(r"<think>.*?</think>", "", Response, flags=ReMod.DOTALL).strip()

            ToolCalls = self.ExtractToolCalls(Response)
            if not ToolCalls:
                # Модель надала фінальну відповідь без виклику інструментів
                break

            # Фіксуємо виклик моделі в історії
            Messages.append({"role": "assistant", "content": Response})

            ToolResults = []
            for TC in ToolCalls:
                ToolName = TC.get("Name", "")
                ToolArgs = TC.get("Arguments", {})
                self.EmitProgress(f"EXECUTING CONDUIT OPERATION: {ToolName} (cycle {Iteration + 1})")
                ToolRes = self.ToolDispatcher.Execute(ToolName, ToolArgs)
                ToolResults.append(f"[{ToolName}] Result: {ToolRes}")
            
            ToolResultsText = "\n".join(ToolResults)
            # Додаємо результати інструментів в історію контексту для наступного кроку моделі
            ToolMsg = f"Tool execution results (step {Iteration + 1}):\n{ToolResultsText}\n\nAnalyze results and proceed to next step or provide final response."
            Messages.append({"role": "user", "content": ToolMsg})

        CleanResponse = Response
        if CleanResponse and "```" in CleanResponse:
            import re as ReClean
            CleanResponse = ReClean.sub(r"```(?:json)?[\s\S]*?```", "", CleanResponse).strip()

        self.Memory.AddMessage("assistant", Response)
        self.Context.AddMessage("assistant", Response)
        if Started is not None and DT is not None:
            Elapsed = (DT.now() - Started).total_seconds()
            Result = f"THINK [{Elapsed:.2f}s]\n\n{CleanResponse or Response}"
        else:
            Result = f"THINK\n\n{CleanResponse or Response}"
        self.State = AgentState.ONLINE
        self.Mode = AgentMode.ACTIVE
        return Result

    def ThinkAsync(self, UserInput: str, Callback: any = None) -> str:
        TaskId = self.Tasks.Enqueue(
            f"Async task: {str(UserInput)[:80]}",
            lambda Ctx: self.Think(Ctx["Input"]),
            Priority.NORMAL,
            {"Input": UserInput},
        )
        if Callback:
            Threading = LCARS.System.Threading
            if Threading is not None:
                Threading.Thread(target=lambda: Callback(self.GetTaskResult(TaskId)), daemon=True).start()
        return f"TaskQueued: {TaskId}"

    def GetTaskResult(self, TaskId: str) -> str:
        for Task in self.Tasks.Queue:
            if Task.Id == TaskId:
                return str(Task.Result or "TaskPending")
        Task = self.Tasks.RunningTasks.get(TaskId)
        if Task is not None:
            return str(Task.Result or "TaskRunning")
        return "TaskComplete"

    def ExecuteTool(self, ToolName: str, Arguments: dict | None = None) -> str:
        return self.ToolDispatcher.Execute(ToolName, Arguments or {})

    def Diagnose(self) -> dict:
        return self.Diagnostics.RunDiagnostic()

    def GetHealth(self) -> dict:
        return self.Diagnostics.GetHealthReport()

    def GetStatus(self) -> dict:
        from lcars.service.provider import AIProvider
        ProviderStatus = AIProvider.GetProvider().GetStatus()
        return {
            "AgentId": self.AgentId,
            "Name": self.Name,
            "Version": self.Version,
            "State": str(self.State),
            "Mode": str(self.Mode),
            "ProjectRoot": str(self.RootPath),
            "ActiveAIProvider": ProviderStatus.get("active", "none"),
            "AIAvailable": ProviderStatus.get("available", False),
            "Autopilot": self.Autopilot.GetStatus(),
            "SkillsLoaded": len(self.Skills.ListSkills()),
            "MemoryTurns": len(self.Memory.Messages),
            "TaskQueue": self.Tasks.GetStatus(),
        }

    def GetProjectInfo(self) -> str:
        return self.ToolDispatcher.Executor.GetProjectInfo()

    def SetMode(self, Mode: str) -> str:
        Old = self.Mode
        self.Mode = Mode
        return f"MODE: {Old} -> {Mode}"

    def ListSkills(self) -> list:
        return self.Skills.ListSkills()

    def LoadSkill(self, SkillName: str) -> bool:
        return self.Skills.GetSkill(SkillName) is not None

    def ExecuteSkill(self, SkillName: str, Context: dict) -> str:
        Skill = self.Skills.GetSkill(SkillName)
        if Skill is None:
            return f"ERROR: Skill '{SkillName}' not found"
        JsonMod = LCARS.System.Json
        Serialized = JsonMod.dumps(Context, ensure_ascii=False) if JsonMod and hasattr(JsonMod, "dumps") else str(Context)
        return self.Think(f"{Skill.get('Body', '')}\n\nContext:\n{Serialized}")

    def EnqueueTask(self, Description: str, Callback: any, TaskPriority: int = 2) -> str:
        return self.Tasks.Enqueue(Description, Callback, TaskPriority)

    def GetTaskStatus(self) -> dict:
        return self.Tasks.GetStatus()

# Клас доступу до агента
class AgentAccess:
    @staticmethod
    def GetAgent(ProjectRoot: any = None, BoardComputer: any = None) -> Copilot:
        Instance = Copilot(ProjectRoot=ProjectRoot, BoardComputer=BoardComputer)
        return Instance

    @staticmethod
    def InitializeAgent(ProjectRoot: any = None) -> bool:
        return AgentAccess.GetAgent(ProjectRoot).Initialize()

LCARSAgent = Copilot
CopilotAgent = Copilot
InitializeAgent = AgentAccess.InitializeAgent
GetAgent = AgentAccess.GetAgent
