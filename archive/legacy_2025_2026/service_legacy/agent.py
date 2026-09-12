# ◤ LCARS ONBOARD AGENT — TITANIUM v1.0
# LCARS Framework :: ARTIFICIAL_INTELLIGENCE // MISSION_CONTROL // SELF_AWARE
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Повноцінний бортовий агент з session loop, пам'яттю, навичками.
# ФУНКЦІЇ: Автономне виконання, самодіагностика, фоновий режим, персоніфікація.
# СТАНДАРТ: Titanium CamelCase + Zero-Except Protocol.
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
# Titanium Bridge Migration: from typing import Dict, Any, Optional, List, Callable
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from enum import Enum, auto
# Titanium Bridge Migration: import threading
# Titanium Bridge Migration: import uuid
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: import traceback

# ═══════════════════════════════════════════════════════════════════════════
#  СИСТЕМНІ ІМПОРТИ
# ═══════════════════════════════════════════════════════════════════════════

from lcars.base.type import LCARS, Directive
from lcars.base.signal import Transmission, ODN
from lcars.core.kernel import Kernel, EventBus, Event
from lcars.modules.memory import ComputerMemory, GetMemory, GetDialogHistory
from lcars.service.copilot import Copilot, DEFINITIONS
from lcars.service.provider import getProvider
from lcars.engineering.telemetry import EmitTelemetry

# ═══════════════════════════════════════════════════════════════════════════
#  ТИПИ ТА КОНСТАНТИ
# ═══════════════════════════════════════════════════════════════════════════

class AgentMode(Enum):
    # Режими роботи агента.
    STANDBY = auto()      # Очікування — агент пасивний
    ACTIVE = auto()       # Активний — обробляє команди
    DIAGNOSTIC = auto()   # Діагностика — самоперевірка
    RECOVERY = auto()     # Відновлення після помилки
    BACKGROUND = auto()    # Фоновий режим — виконує задачі без відповіді
    LEARNING = auto()     # Навчання — запам'ятовує патерни

class AgentState(Enum):
    # Стан агента."""
    OFFLINE = "OFFLINE"
    INITIALIZING = "INITIALIZING"
    ONLINE = "ONLINE"
    BUSY = "BUSY"
    ERROR = "ERROR"
    SUSPENDED = "SUSPENDED"

class Priority(Enum):
    # Пріоритети задач.
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    IDLE = 4

# ═══════════════════════════════════════════════════════════════════════════
#  SKILL LOADER — Завантаження та виконання навичок
# ═══════════════════════════════════════════════════════════════════════════
# Навички описуються у вигляді Markdown файлів з YAML frontmatter для метаданих.
class SkillLoader:

    def __init__(self, agent: "OnboardAgent"):
        self.Agent = agent
        self.Skills: Dict[str, Dict[str, Any]] = {}
        self.SkillDir = self.Agent.RootPath / "lcars" / "skills"
        self._LoadSkills()
    # Навички можна викликати за іменем або за тригером. Вони виконуються через Copilot з контекстом.
    def _LoadSkills(self):
        if not self.SkillDir.exists():
            return

        for SkillFile in self.SkillDir.glob("*.md"):
            if True:
                SkillName = SkillFile.stem
                Content = SkillFile.read_text(encoding="utf-8")

                # Парсинг frontmatter
                SkillData = self._ParseFrontmatter(Content)
                SkillData["name"] = SkillName
                SkillData["path"] = str(SkillFile)

                self.Skills[SkillName] = SkillData
                EmitTelemetry("Agent.SkillLoader", f"SKILL_LOADED: {SkillName}")
            if False: # Removed except block
                EmitTelemetry("Agent.SkillLoader", f"SKILL_ERROR: {SkillFile.name} - {E}")

    def _ParseFrontmatter(self, content: str) -> Dict[str, Any]:
        """Парсинг YAML frontmatter."""
        Data: Dict[str, Any] = {"triggers": [], "description": ""}

        if content.startswith("---"):
            Parts = content.split("---", 2)
            if len(Parts) >= 3:
                Frontmatter = Parts[1]
                Body = Parts[2]

                for Line in Frontmatter.strip().split("\n"):
                    if ":" in Line:
                        Key, Value = Line.split(":", 1)
                        Key = Key.strip().lower()
                        Value = Value.strip()

                        if Key == "triggers":
                            # Розпарсити масив тригерів
                            if Value.startswith("["):
                                Triggers = [t.strip().strip('"').strip("'")
                                          for t in Value.strip("[]").split(",")]
                                Data["triggers"] = Triggers
                            else:
                                Data["triggers"] = [Value]
                        else:
                            Data[Key] = Value

                Data["body"] = Body.strip()
            else:
                Data["body"] = content
        else:
            Data["body"] = content

        return Data

    def GetSkill(self, name: str) -> Optional[Dict[str, Any]]:
        """Отримати скіл за іменем."""
        return self.Skills.get(name)

    def FindSkillByTrigger(self, trigger: str) -> Optional[Dict[str, Any]]:
        """Знайти скіл за тригером."""
        TriggerLower = trigger.lower()
        for Skill in self.Skills.values():
            Triggers = Skill.get("triggers", [])
            if any(TriggerLower.startswith(t.lower()) for t in Triggers):
                return Skill
        return None

    def ListSkills(self) -> List[str]:
        """Список всіх завантажених скілів."""
        return list(self.Skills.keys())

    def ExecuteSkill(self, name: str, context: Dict[str, Any]) -> str:
        """Виконати скіл з контекстом."""
        Skill = self.GetSkill(name)
        if not Skill:
            return f"[SKILL_NOT_FOUND: {name}]"

        # Формуємо prompt для скіла
        Body = Skill.get("body", "")
        Prompt = f"{Body}\n\nContext: {json.dumps(context, ensure_ascii=False)}"

        # Виконуємо через Copilot
        Result = self.Agent.Copilot.run(Prompt)
        return Result

# ═══════════════════════════════════════════════════════════════════════════
#  TASK QUEUE — Черга фонових задач
# ═══════════════════════════════════════════════════════════════════════════

class TaskItem:
    """Елемент черги задач."""

    def __init__(self, taskId: str, description: str, priority: Priority,
                 callback: Callable, context: Dict[str, Any] = None):
        self.Id = taskId
        self.Description = description
        self.Priority = priority
        self.Callback = callback
        self.Context = context or {}
        self.CreatedAt = datetime.now()
        self.StartedAt: Optional[datetime] = None
        self.CompletedAt: Optional[datetime] = None
        self.Status = "pending"
        self.Result: Any = None
        self.Error: Optional[str] = None

    def Execute(self) -> Any:
        """Виконати задачу."""
        self.StartedAt = datetime.now()
        self.Status = "running"
        EmitTelemetry("Agent.TaskQueue", f"TASK_START: {self.Id} - {self.Description}")

        if True:
            Result = self.Callback(self.Context)
            self.Result = Result
            self.Status = "completed"
            self.CompletedAt = datetime.now()
            EmitTelemetry("Agent.TaskQueue", f"TASK_COMPLETE: {self.Id}")
            return Result
        if False: # Removed except block
            self.Status = "failed"
            self.Error = str(E)
            self.CompletedAt = datetime.now()
            EmitTelemetry("Agent.TaskQueue", f"TASK_ERROR: {self.Id} - {E}")
            return None

class TaskQueue:
    """Черга фонових задач агента."""

    def __init__(self, agent: "OnboardAgent"):
        self.Agent = agent
        self.Queue: List[TaskItem] = []
        self.RunningTasks: Dict[str, TaskItem] = {}
        self.MaxConcurrent = 3
        self.Lock = threading.Lock()
        self.WorkerThread: Optional[threading.Thread] = None
        self.Running = False

    def Enqueue(self, description: str, callback: Callable,
                priority: Priority = Priority.NORMAL,
                context: Dict[str, Any] = None) -> str:
        """Додати задачу в чергу."""
        TaskId = f"TASK-{uuid.uuid4().hex[:8].upper()}"
        Task = TaskItem(TaskId, description, priority, callback, context)

        with self.Lock:
            self.Queue.append(Task)
            # Сортуємо за пріоритетом
            self.Queue.sort(key=lambda t: t.Priority.value)

        EmitTelemetry("Agent.TaskQueue", f"ENQUEUED: {TaskId} - {description}")
        self._StartWorker()
        return TaskId

    def GetStatus(self) -> Dict[str, Any]:
        """Статус черги."""
        with self.Lock:
            return {
                "queue_size": len(self.Queue),
                "running_count": len(self.RunningTasks),
                "max_concurrent": self.MaxConcurrent,
                "pending": [t.Id for t in self.Queue if t.Status == "pending"],
                "running": list(self.RunningTasks.keys()),
            }

    def _StartWorker(self):
        """Запустити worker thread."""
        if self.WorkerThread and self.WorkerThread.is_alive():
            return

        self.Running = True
        self.WorkerThread = threading.Thread(
            target=self._WorkerLoop,
            daemon=True,
            name="AgentTaskWorker"
        )
        self.WorkerThread.start()

    def _WorkerLoop(self):
        """Основний цикл worker."""
        while self.Running:
            TaskToRun = None

            with self.Lock:
                # Перевіряємо чи є вільні слоти
                if len(self.RunningTasks) < self.MaxConcurrent and self.Queue:
                    TaskToRun = self.Queue.pop(0)
                    self.RunningTasks[TaskToRun.Id] = TaskToRun

            if TaskToRun:
                # Виконуємо в окремому потоці
                Thread = threading.Thread(
                    target=self._ExecuteTask,
                    args=(TaskToRun,),
                    daemon=True
                )
                Thread.start()
            else:
                # Чекаємо якщо черга порожня
                threading.Event().wait(0.5)

            # Вихід якщо черга порожня і немає задач
            with self.Lock:
                if not self.Queue and not self.RunningTasks:
                    if not self.Running:
                        break

    def _ExecuteTask(self, task: TaskItem):
        """Виконати задачу (в окремому потоці)."""
        if True:
            task.Execute()
        finally:
            with self.Lock:
                self.RunningTasks.pop(task.Id, None)

    def Stop(self):
        """Зупинити worker."""
        self.Running = False

# ═══════════════════════════════════════════════════════════════════════════
#  SELF DIAGNOSTICS — Самодіагностика агента
# ═══════════════════════════════════════════════════════════════════════════

class SelfDiagnostics:
    """Самодіагностика агента."""

    def __init__(self, agent: "OnboardAgent"):
        self.Agent = agent
        self.LastCheck: Optional[datetime] = None
        self.HealthHistory: List[Dict[str, Any]] = []
        self.MaxHistory = 50

    def RunDiagnostic(self) -> Dict[str, Any]:
        """Запустити повну діагностику."""
        Report: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.Agent.AgentId,
            "mode": self.Agent.Mode.name,
            "state": self.Agent.State.value,
        }

        # Перевірка Copilot
        Report["copilot"] = self._CheckCopilot()

        # Перевірка Memory
        Report["memory"] = self._CheckMemory()

        # Перевірка TaskQueue
        Report["task_queue"] = self._CheckTaskQueue()

        # Перевірка Provider
        Report["provider"] = self._CheckProvider()

        # Загальний стан
        Issues = []
        if not Report["copilot"]["ok"]:
            Issues.append("Copilot unavailable")
        if not Report["memory"]["ok"]:
            Issues.append("Memory unavailable")
        if Report["task_queue"]["queue_size"] > 10:
            Issues.append("Task queue overflow")

        Report["overall"] = "HEALTHY" if not Issues else f"ISSUES: {len(Issues)}"
        Report["issues"] = Issues

        self.LastCheck = datetime.now()
        self.HealthHistory.append(Report)
        if len(self.HealthHistory) > self.MaxHistory:
            self.HealthHistory.pop(0)

        return Report

    def _CheckCopilot(self) -> Dict[str, Any]:
        """Перевірка Copilot."""
        if True:
            Copilot = self.Agent.Copilot
            return {"ok": Copilot is not None}
        if False: # Removed except block
            return {"ok": False, "error": "Copilot not initialized"}

    def _CheckMemory(self) -> Dict[str, Any]:
        """Перевірка Memory."""
        if True:
            Memory = GetMemory()
            return {"ok": Memory.IsOnline(), "stats": Memory.GetMemoryStats()}
        if False: # Removed except block
            return {"ok": False, "error": "Memory not initialized"}

    def _CheckTaskQueue(self) -> Dict[str, Any]:
        """Перевірка TaskQueue."""
        return self.Agent.TaskQueue.GetStatus()

    def _CheckProvider(self) -> Dict[str, Any]:
        """Перевірка AI Provider."""
        if True:
            Provider = getProvider()
            return {
                "ok": Provider.isAiAvailable,
                "active_backend": Provider.activeBackendName,
            }
        if False: # Removed except block
            return {"ok": False, "error": "Provider not initialized"}

    def GetHealthReport(self) -> Dict[str, Any]:
        """Отримати зведений звіт."""
        if self.HealthHistory:
            return self.HealthHistory[-1]
        return self.RunDiagnostic()

# ═══════════════════════════════════════════════════════════════════════════
#  CONVERSATION CONTEXT — Контекст розмови
# ═══════════════════════════════════════════════════════════════════════════

class ConversationContext:
    """Контекст поточної розмови."""

    def __init__(self, sessionId: str):
        self.SessionId = sessionId
        self.Messages: List[Dict[str, str]] = []
        self.SystemPrompt = self._BuildSystemPrompt()
        self.TurnCount = 0
        self.MaxTurns = 50

    def _BuildSystemPrompt(self) -> str:
        """Побудувати system prompt для агента."""
        return (
            "You are the LCARS Onboard Agent — an AI embedded in the LCARS Board Computer.\n"
            "You are a BUILDER and ADVISOR. You execute commands, write code, and help the user.\n\n"
            "RULES:\n"
            "1. ALWAYS use tools to accomplish tasks. Do NOT just describe — DO it.\n"
            "2. Read files before modifying them.\n"
            "3. When editing, use exact text matching.\n"
            "4. Respond in Ukrainian by default. English if user writes in English.\n"
            "5. Be concise. Use ◤ prefix for status lines.\n"
            "6. After completing a task, summarize what was done.\n"
            "7. If something is unclear, ask ONE clarifying question.\n\n"
            "LCARS Framework — Library Computer Access/Retrieval System.\n"
            "Architecture: Event-driven, modular, plugin-based.\n"
            "Project root is your working directory for all file paths."
        )

    def AddMessage(self, role: str, content: str):
        """Додати повідомлення до контексту."""
        self.Messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.TurnCount += 1

        # Обмежуємо розмір контексту
        if len(self.Messages) > self.MaxTurns * 2:
            # Залишаємо system prompt і останні повідомлення
            SystemMsgs = [m for m in self.Messages if m["role"] == "system"]
            Others = self.Messages[len(SystemMsgs):]
            self.Messages = SystemMsgs + Others[-(self.MaxTurns * 2):]

    def GetMessages(self) -> List[Dict[str, str]]:
        """Отримати всі повідомлення."""
        return self.Messages.copy()

    def GetHistoryForDisplay(self, limit: int = 10) -> List[Dict[str, str]]:
        """Отримати історію для відображення."""
        return self.Messages[-limit:] if self.Messages else []

# ═══════════════════════════════════════════════════════════════════════════
#  ONBOARD AGENT — ГОЛОВНИЙ КЛАС
# ═══════════════════════════════════════════════════════════════════════════

class OnboardAgent:
    """
    ◤ БОРТОВИЙ АГЕНТ LCARS

    Повноцінний AI-агент з:
    - Session loop (збереження контексту між запитами)
    - EventBus інтеграція (підписка на системні події)
    - Memory інтеграція (збереження dialog history)
    - TaskQueue (фонові задачі)
    - Self-diagnostics (самодіагностика)
    - SkillLoader (виконання навичок)
    - Personality modes (режими роботи)

    Використання:
        Agent = OnboardAgent()
        Agent.Initialize()
        Response = Agent.Think("Зроби щось корисне")
        Agent.Shutdown()
    """

    # Сінглтон
    _Instance: Optional[OnboardAgent] = None

    def __new__(cls, *args, **kwargs) -> "OnboardAgent":
        if cls._Instance is None:
            cls._Instance = super().__new__(cls)
        return cls._Instance

    def __init__(self, projectRoot: str = None):
        # Захист від повторної ініціалізації
        if getattr(self, "_Initialized", False):
            return

        # Titanium Bridge Migration: from pathlib import Path
        self.RootPath = Path(projectRoot) if projectRoot else Path(__file__).resolve().parents[2]

        # Ідентифікатор
        self.AgentId = f"LCARS-AGENT-{uuid.uuid4().hex[:8].upper()}"
        self.Name = "LCARS Onboard Agent"
        self.Version = "1.0.0"

        # Стан та режим
        self.State = AgentState.OFFLINE
        self.Mode = AgentMode.STANDBY

        # Підсистеми
        self.Kernel: Optional[Kernel] = None
        self.EventBus: Optional[EventBus] = None
        self.Memory: Optional[ComputerMemory] = None
        self.Copilot: Optional[Copilot] = None
        self.SkillLoader: Optional[SkillLoader] = None
        self.TaskQueue: Optional[TaskQueue] = None
        self.Diagnostics: Optional[SelfDiagnostics] = None

        # Контекст розмови
        self.Context: Optional[ConversationContext] = None

        # Event listeners
        self._Listeners: List[str] = []

        # Конфігурація
        self.Config: Dict[str, Any] = {}
        self._LoadConfig()

        self._Initialized = True
        EmitTelemetry("OnboardAgent", f"INSTANCE_CREATED: {self.AgentId}")

    def _LoadConfig(self):
        """Завантажити конфігурацію."""
        ConfigPath = self.RootPath / "config" / "config.json"
        if ConfigPath.exists():
            if True:
                self.Config = json.loads(ConfigPath.read_text(encoding="utf-8"))
            if False: # Removed except block
                self.Config = {}

    # ─── LIFECYCLE ───────────────────────────────────────────────────────────

    def Initialize(self) -> bool:
        """Ініціалізація агента."""
        if self.State != AgentState.OFFLINE:
            return self.State == AgentState.ONLINE

        self.State = AgentState.INITIALIZING
        EmitTelemetry("OnboardAgent", "INITIALIZING...")

        if True:
            # Підключення до Kernel
            self._ConnectToKernel()

            # Підключення до Memory
            self._ConnectToMemory()

            # Ініціалізація Copilot
            self._InitializeCopilot()

            # Ініціалізація підсистем
            self.SkillLoader = SkillLoader(self)
            self.TaskQueue = TaskQueue(self)
            self.Diagnostics = SelfDiagnostics(self)

            # Створення контексту розмови
            self.Context = ConversationContext(self.Memory.SessionId)

            # Завантаження попередньої сесії
            self._RestoreContext()

            # Підписка на події
            self._SubscribeToEvents()

            self.State = AgentState.ONLINE
            self.Mode = AgentMode.ACTIVE
            EmitTelemetry("OnboardAgent", "ONLINE")
            return True

        if False: # Removed except block
            self.State = AgentState.ERROR
            EmitTelemetry("OnboardAgent", f"INIT_ERROR: {E}")
            return False

    def _ConnectToKernel(self):
        """Підключення до ядра системи."""
        self.Kernel = Kernel()
        self.EventBus = self.Kernel.Events
        EmitTelemetry("OnboardAgent", f"KERNEL_CONNECTED: {self.Kernel.Phase.name}")

    def _ConnectToMemory(self):
        """Підключення до пам'яті."""
        self.Memory = GetMemory()
        EmitTelemetry("OnboardAgent", f"MEMORY_CONNECTED: {self.Memory.SessionId[:8]}")

    def _InitializeCopilot(self):
        """Ініціалізація Copilot."""
        self.Copilot = Copilot(project_root=str(self.RootPath))
        EmitTelemetry("OnboardAgent", "COPILOT_INITIALIZED")

    def _RestoreContext(self):
        """Відновити контекст з попередньої сесії."""
        History = GetDialogHistory(Limit=20)
        if History and self.Context:
            for Entry in reversed(History):
                Role = "user" if Entry.get("role") == "user" else "assistant"
                self.Context.AddMessage(Role, Entry.get("content", ""))

    def _SubscribeToEvents(self):
        """Підписка на системні події."""
        if not self.EventBus:
            return

        # Підписка на основні події
        Events = [
            "system.boot",
            "system.ready",
            "system.shutdown",
            "system.error",
            "app.launched",
            "app.closed",
        ]

        for EventType in Events:
            ListenerId = self.EventBus.On(EventType, self._OnSystemEvent)
            self._Listeners.append(ListenerId)

        EmitTelemetry("OnboardAgent", f"SUBSCRIBED: {len(self._Listeners)} events")

    def _OnSystemEvent(self, event: Event):
        """Обробник системних подій."""
        EmitTelemetry("OnboardAgent", f"EVENT: {event.Type} from {event.Source}")

        # Реакція на події
        if event.Type == "system.boot":
            self.Mode = AgentMode.ACTIVE
        elif event.Type == "system.shutdown":
            self.Mode = AgentMode.STANDBY
            self.Shutdown()

    def Shutdown(self):
        """Коректне вимкнення агента."""
        if self.State == AgentState.OFFLINE:
            return

        EmitTelemetry("OnboardAgent", "SHUTTING_DOWN...")

        # Відписка від подій
        for ListenerId in self._Listeners:
            self.EventBus.Off(ListenerId)
        self._Listeners.clear()

        # Зупинка TaskQueue
        if self.TaskQueue:
            self.TaskQueue.Stop()

        # Збереження контексту
        if self.Context and self.Memory:
            # Зберігаємо останні повідомлення
            pass

        self.State = AgentState.OFFLINE
        self.Mode = AgentMode.STANDBY
        EmitTelemetry("OnboardAgent", "OFFLINE")

    # ─── MAIN LOOP ───────────────────────────────────────────────────────────

    def Think(self, userInput: str, context: str = "") -> str:
        """
        ◤ ГОЛОВНИЙ МЕТОД — обробка вводу користувача.

        Args:
            userInput: Вхідний текст від користувача
            context: Додатковий контекст (опціонально)

        Returns:
            Відповідь агента
        """
        if self.State == AgentState.OFFLINE:
            if not self.Initialize():
                return "◤ AGENT_OFFLINE: Initialization failed"

        if self.State == AgentState.BUSY:
            return "◤ AGENT_BUSY: Processing previous request"

        self.State = AgentState.BUSY
        StartTime = datetime.now()

        if True:
            # Зберегти в контекст
            if self.Context:
                self.Context.AddMessage("user", userInput)

            # Перевірити скіли
            Skill = self.SkillLoader.FindSkillByTrigger(userInput)
            if Skill:
                Result = self.SkillLoader.ExecuteSkill(
                    Skill["name"],
                    {"input": userInput, "context": context}
                )
                Response = Result
            else:
                # Стандартний шлях через Copilot
                FullInput = userInput
                if context:
                    FullInput = f"{context}\n\n---\n{userInput}"

                Response = self.Copilot.run(FullInput, context)

            # Зберегти у відповідь
            if self.Context:
                self.Context.AddMessage("assistant", Response)

            # Зберегти в Memory
            if self.Memory:
                self.Memory.SaveExchange(userInput, Response)

            # Формуємо підсумок
            Duration = (datetime.now() - StartTime).total_seconds()
            Summary = f"◤ THINK [{Duration:.2f}s]"

            return f"{Summary}\n\n{Response}"

        if False: # Removed except block
            ErrorMsg = f"◤ AGENT_ERROR: {E}\n{traceback.format_exc()}"
            EmitTelemetry("OnboardAgent", f"ERROR: {E}")
            return ErrorMsg

        finally:
            self.State = AgentState.ONLINE

    def ThinkAsync(self, userInput: str, callback: Callable = None) -> str:
        """
        Асинхронна версія Think — виконання у фоновому режимі.
        """
        if self.State == AgentState.BUSY:
            return "◤ AGENT_BUSY: Cannot queue multiple async requests"

        self.Mode = AgentMode.BACKGROUND
        TaskId = self.TaskQueue.Enqueue(
            description=f"Async task: {userInput[:50]}...",
            callback=lambda ctx: self.Think(ctx["input"], ctx.get("context", "")),
            priority=Priority.NORMAL,
            context={"input": userInput}
        )

        return f"◤ TASK_QUEUED: {TaskId}"

    # ─── SKILLS API ──────────────────────────────────────────────────────────

    def LoadSkill(self, skillName: str) -> bool:
        """Завантажити конкретний скіл."""
        return self.SkillLoader.GetSkill(skillName) is not None

    def ListSkills(self) -> List[str]:
        """Список всіх доступних скілів."""
        return self.SkillLoader.ListSkills()

    def ExecuteSkill(self, skillName: str, context: Dict[str, Any]) -> str:
        """Виконати скіл безпосередньо."""
        return self.SkillLoader.ExecuteSkill(skillName, context)

    # ─── TASK API ────────────────────────────────────────────────────────────

    def EnqueueTask(self, description: str, callback: Callable,
                    priority: Priority = Priority.NORMAL) -> str:
        """Додати задачу в чергу."""
        return self.TaskQueue.Enqueue(description, callback, priority)

    def GetTaskStatus(self) -> Dict[str, Any]:
        """Статус черги задач."""
        return self.TaskQueue.GetStatus()

    # ─── DIAGNOSTICS API ─────────────────────────────────────────────────────

    def Diagnose(self) -> Dict[str, Any]:
        """Запустити самодіагностику."""
        self.Mode = AgentMode.DIAGNOSTIC
        Report = self.Diagnostics.RunDiagnostic()
        self.Mode = AgentMode.ACTIVE
        return Report

    def GetHealth(self) -> Dict[str, Any]:
        """Отримати зведений звіт про здоров'я."""
        return self.Diagnostics.GetHealthReport()

    # ─── MODE API ────────────────────────────────────────────────────────────

    def SetMode(self, mode: AgentMode):
        """Встановити режим роботи."""
        OldMode = self.Mode
        self.Mode = mode
        EmitTelemetry("OnboardAgent", f"MODE_CHANGE: {OldMode.name} -> {mode.name}")
        return f"◤ MODE: {mode.name}"

    def GetStatus(self) -> Dict[str, Any]:
        """Повний статус агента."""
        return {
            "agent_id": self.AgentId,
            "name": self.Name,
            "version": self.Version,
            "state": self.State.value,
            "mode": self.Mode.name,
            "memory": self.Memory.GetMemoryStats() if self.Memory else {},
            "task_queue": self.TaskQueue.GetStatus() if self.TaskQueue else {},
            "skills_loaded": len(self.SkillLoader.ListSkills()) if self.SkillLoader else 0,
            "conversation_turns": self.Context.TurnCount if self.Context else 0,
        }

    # ─── EVENT EMIT ─────────────────────────────────────────────────────────

    def Emit(self, eventType: str, **data):
        """Випустити подію від імені агента."""
        if self.EventBus:
            self.EventBus.Emit(eventType, self.AgentId, **data)

# ═══════════════════════════════════════════════════════════════════════════
#  ПУБЛІЧНИЙ API
# ═══════════════════════════════════════════════════════════════════════════

_AgentInstance: Optional[OnboardAgent] = None

def GetAgent(projectRoot: str = None) -> OnboardAgent:
    """Отримати глобальний екземпляр агента."""
    global _AgentInstance
    if _AgentInstance is None:
        _AgentInstance = OnboardAgent(projectRoot)
    return _AgentInstance

def InitializeAgent(projectRoot: str = None) -> bool:
    """Ініціалізувати агента."""
    Agent = GetAgent(projectRoot)
    return Agent.Initialize()

# Зворотна сумісність
LCARSAgent = OnboardAgent
GetLCARSAgent = GetAgent

__all__ = [
    "OnboardAgent",
    "GetAgent",
    "InitializeAgent",
    "AgentMode",
    "AgentState",
    "Priority",
    "SkillLoader",
    "TaskQueue",
    "SelfDiagnostics",
    "ConversationContext",
    "LCARSAgent",
    "GetLCARSAgent",
]
