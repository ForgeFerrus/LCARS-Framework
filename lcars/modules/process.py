# ◤ LCARS PROCESS & RUNTIME MODULE // TITANIUM ARCHITECTURE 🖖
# =============================================================================
# ФАЙЛ: lcars/modules/process.py
# ОПИС: Модуль керування процесами, додатками та зовнішніми системними потоками.
#       Містить контракти для запуску віконних додатків (Application, ProcessTable),
#       а також повноцінний менеджер зовнішніх системних процесів (ProcessManager)
#       з підтримкою політики автоматичного перезапуску, відстеження потоків вводу/виводу
#       та інтеграції з оточенням операційної системи.
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure LCARS Classes).
# =============================================================================

from __future__ import annotations
# Titanium Bridge Migration: from typing import Any, Callable, Dict, List, Optional
from lcars.base.type import Process as LCARSProcess, LCARS

# ═════════════════════════════════════════════════════════════════════
# 1. APPLICATION & UI PROCESS CONTRACTS
# ═════════════════════════════════════════════════════════════════════
# Базовий контракт віконного додатку LCARS.
class Application(LCARS):
    AppId: str = "unnamed"
    Title: str = "LCARS Application"
    Icon: str = ""
    Category: str = "general"

    # Викликається середовищем виконання при старті
    def OnLaunch(self, HostRef: Any) -> None:
        self.Host = HostRef

    # Фабрика створення головного графічного віджета
    def CreateUI(self) -> Any:
        return None

    # Викликається при отриманні додатком фокусу
    def OnFocus(self) -> None:
        pass

    # Викликається при згортанні/мінімізації
    def OnMinimize(self) -> None:
        pass

    # Викликається при закритті додатку
    def OnClose(self) -> None:
        pass

# Запис активного процесу додатку з власним PID.
class ProcessEntry(LCARS):
    Counter = 0
    CounterLock = LCARS.System.Threading.Lock()

    def __init__(self, App: Application):
        super().__init__()
        with ProcessEntry.CounterLock:
            ProcessEntry.Counter += 1
            self.Pid = ProcessEntry.Counter
        self.App = App
        self.Started = LCARS.System.Time.DateTime.now()
        self.Widget = None

# Таблиця активних додатків та інтерфейсних процесів.
class ProcessTable(LCARS):
    def __init__(self):
        super().__init__()
        self.Table: Dict[int, ProcessEntry] = {}

    # Зареєструвати новий процес додатка
    def Add(self, App: Application) -> ProcessEntry:
        Entry = ProcessEntry(App)
        self.Table[Entry.Pid] = Entry
        return Entry

    # Отримати процес за PID
    def Get(self, Pid: int) -> Optional[ProcessEntry]:
        return self.Table.get(Pid)

    # Знайти процес за його AppId
    def Find(self, AppId: str) -> Optional[ProcessEntry]:
        for Entry in self.Table.values():
            if Entry.App.AppId == AppId:
                return Entry
        return None

    # Видалити процес за PID
    def Remove(self, Pid: int) -> Optional[ProcessEntry]:
        return self.Table.pop(Pid, None)

    # Список усіх активних процесів
    def All(self) -> List[ProcessEntry]:
        return list(self.Table.values())

    # Кількість активних процесів
    def Count(self) -> int:
        return len(self.Table)

    # Зупинити та закрити всі запущені додатки
    def KillAll(self) -> None:
        for Entry in list(self.Table.values()):
            Entry.App.OnClose()
        self.Table.clear()

# ═════════════════════════════════════════════════════════════════════
# 2. SYSTEM PROCESS MANAGER (SUBPROCESS ENGINE)
# ═════════════════════════════════════════════════════════════════════
# Менеджер зовнішніх процесів операційної системи та фонових воркерів.
class ProcessManager(LCARSProcess):
    def __init__(self, ProjectRoot: str = "."):
        super().__init__("ProcessManager")
        self.Name = "ProcessManager"
        self.Command = ""
        self.ProjectRoot = str(ProjectRoot)
        self.Processes: Dict[str, Any] = {}
        self.RestartPolicies: Dict[str, Any] = {}
        self.LastCommand: Dict[str, Any] = {}
        self.OutputCallbacks: List[Callable] = []
        self.FinishedCallbacks: List[Callable] = []
        self.StartedCallbacks: List[Callable] = []

    # Підписка на отримання тексту з виводу процесу
    def OnOutput(self, CallbackFunc: Callable) -> None:
        self.OutputCallbacks.append(CallbackFunc)

    # Підписка на подію завершення процесу
    def OnFinished(self, CallbackFunc: Callable) -> None:
        self.FinishedCallbacks.append(CallbackFunc)

    # Підписка на подію запуску процесу
    def OnStarted(self, CallbackFunc: Callable) -> None:
        self.StartedCallbacks.append(CallbackFunc)

    # Запуск зовнішнього процесу Python/Shell у робочій директорії
    def Start(self, NameStr: str, FullPath: str, ArgsList: Optional[List[str]] = None) -> bool:
        if NameStr in self.Processes:
            Proc = self.Processes[NameStr]
            if Proc and hasattr(Proc, "poll") and Proc.poll() is None:
                return False

        Sys = LCARS.System.Core
        SysPath = Sys.path if (Sys and hasattr(Sys, "path")) else []
        EnvPaths = [self.ProjectRoot] + SysPath
        IsWin = (Sys.platform == "win32") if (Sys and hasattr(Sys, "platform")) else True
        PythonPath = ";".join(EnvPaths) if IsWin else ":".join(EnvPaths)

        SysExecutable = Sys.executable if (Sys and hasattr(Sys, "executable")) else "python"
        CmdArgs = [SysExecutable, FullPath]
        if ArgsList:
            CmdArgs += ArgsList

        Os = LCARS.System.Environment
        Env = Os.copy() if hasattr(Os, "copy") else {}
        Env["PYTHONPATH"] = PythonPath

        Subprocess = LCARS.System.Subprocess
        if not Subprocess:
            return False

        ProcessObj = Subprocess.Popen(
            CmdArgs,
            stdout=Subprocess.PIPE,
            stderr=Subprocess.PIPE,
            env=Env,
            cwd=self.ProjectRoot,
            text=True,
        )
        self.Processes[NameStr] = ProcessObj
        self.LastCommand[NameStr] = (FullPath, ArgsList or [])

        for Cb in self.StartedCallbacks:
            if callable(Cb):
                Cb(NameStr)
        return True

    # Читання доступного буфера виводу процесу
    def Read(self, NameStr: str) -> str:
        Proc = self.Processes.get(NameStr)
        if Proc is None or (hasattr(Proc, "poll") and Proc.poll() is not None):
            return ""

        DataStr = ""
        if hasattr(Proc, "stdout") and Proc.stdout and not getattr(Proc.stdout, "closed", False):
            Chunk = Proc.stdout.read(1024)
            if Chunk:
                DataStr = Chunk

        for Cb in self.OutputCallbacks:
            if callable(Cb):
                Cb(NameStr, DataStr)
        return DataStr

    # Перевірка статусу процесу та автоматичний перезапуск за політикою
    def Check(self, NameStr: str) -> bool:
        Proc = self.Processes.get(NameStr)
        if Proc is None:
            return True

        ReturnCode = Proc.poll() if hasattr(Proc, "poll") else None
        if ReturnCode is not None:
            self.Processes.pop(NameStr, None)
            for Cb in self.FinishedCallbacks:
                if callable(Cb):
                    Cb(NameStr)

            Policy = self.RestartPolicies.get(NameStr)
            if Policy and isinstance(Policy, dict):
                Retries = Policy.get("retries", 0)
                Count = Policy.get("count", 0)
                if Count < Retries:
                    Policy["count"] = Count + 1
                    Delay = Policy.get("delayMs", 1000)
                    Threading = LCARS.System.Threading
                    if Threading and hasattr(Threading, "Timer"):
                        Threading.Timer(Delay / 1000.0, lambda: self.Restart(NameStr, Policy)).start()
            return True
        return False

    # Зупинка процесу за назвою
    def Stop(self, NameStr: str) -> bool:
        Proc = self.Processes.get(NameStr)
        if Proc and hasattr(Proc, "poll") and Proc.poll() is None:
            if hasattr(Proc, "terminate"):
                Proc.terminate()
            return True
        return False

    # Зупинка всіх активних процесів
    def StopAll(self) -> None:
        for NameStr, Proc in list(self.Processes.items()):
            if Proc and hasattr(Proc, "poll") and Proc.poll() is None:
                if hasattr(Proc, "terminate"):
                    Proc.terminate()

    # Встановлення політики автоматичного перезапуску в разі збою
    def SetRestart(self, NameStr: str, Retries: int = 0, DelayMs: int = 1000) -> None:
        self.RestartPolicies[NameStr] = {"retries": int(Retries), "delayMs": int(DelayMs), "count": 0}

    # Перезапуск процесу за збереженою командою
    def Restart(self, NameStr: str, Policy: dict) -> None:
        if self.Running(NameStr):
            return
        if NameStr in self.LastCommand:
            FullPath, ArgsList = self.LastCommand[NameStr]
            self.Start(NameStr, FullPath, ArgsList=ArgsList)

    # Перевірка чи процес виконується в даний момент
    def Running(self, NameStr: str) -> bool:
        Proc = self.Processes.get(NameStr)
        return bool(Proc is not None and hasattr(Proc, "poll") and Proc.poll() is None)

    # Список імен усіх запущених процесів
    def List(self) -> List[str]:
        return list(self.Processes.keys())

# ═════════════════════════════════════════════════════════════════════
# 3. RUNTIME KERNEL & APPLICATION ACCESS GATEWAY
# ═════════════════════════════════════════════════════════════════════
# Системний шлюз доступу до екземпляра Qt Application та ядра ОС.
class KernelAccess(LCARS):
    # Отримати поточний активний екземпляр Qt Application
    @staticmethod
    def ExistingApplication() -> Any:
        return LCARS.Application.instance() if hasattr(LCARS, "Application") and hasattr(LCARS.Application, "instance") else None

    # Створити або отримати екземпляр Application для запуску графічної підсистеми
    @staticmethod
    def CreateApplication(ArgvList: Any = None) -> Any:
        if ArgvList is None:
            ArgvList = LCARS.System.Core.argv if (hasattr(LCARS.System, "Core") and hasattr(LCARS.System.Core, "argv")) else []
        App = KernelAccess.ExistingApplication()
        if App is None and hasattr(LCARS, "Application"):
            App = LCARS.Application(ArgvList)
        return App

    # Отримати глобальний синглтон ядра Kernel
    @staticmethod
    def GetKernel() -> Any:
        from lcars.core.kernel import Kernel
        return Kernel.GetInstance()

    # Отримати системну шину подій ядра
    @staticmethod
    def GetEventBus() -> Any:
        from lcars.core.kernel import Kernel
        return Kernel.GetInstance().Events

ExistingApplication = KernelAccess.ExistingApplication
CreateApplication = KernelAccess.CreateApplication

__all__ = [
    "Application",
    "ProcessEntry",
    "ProcessTable",
    "ProcessManager",
    "KernelAccess",
    "ExistingApplication",
    "CreateApplication",
]
