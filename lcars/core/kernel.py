
from __future__ import annotations

import sys
import uuid
import threading
import platform
from enum import Enum
from pathlib import Path
from datetime import datetime

from typing import Any, Callable, Dict, List, Optional, Sequence, Union
from dataclasses import dataclass, field

from .service import Service, ServiceRegistry
from .matrix import SystemMatrix
from lcars.base.type import LCARS
from lcars.base.register import registry
from lcars.core.signal import ODN, Transmission
from lcars.modules.process import ProcessManager
from lcars.base.version import getVersion

# Отримати існуючу програму LCARS
def ExistingApplication():
    return LCARS.Application.instance()

# Створити або отримати програму LCARS
def CreateApplication(argv=None):
    if argv is None:
        argv = sys.argv
    app = LCARS.Application.instance()
    if app is None:
        app = LCARS.Application(argv)
    return app

__version__ = getVersion()
ROOT = Path(__file__).resolve().parents[2]

# Стани системи LCARS — кожен крок життєвого циклу ядра
class SystemState(Enum):
    OFF           = 0   # Система вимкнена
    BOOTING       = 1   # Послідовність завантаження
    READY         = 2   # Ядро готове, сервіси стартують
    RUNNING       = 3   # Повністю операційний стан
    DEGRADED      = 4   # Працює з помилками
    SHUTTING_DOWN = 5   # Послідовність вимкнення
    ERROR         = 6   # Критична помилка

# Event - Незмінна подія що проходить через систему.
@dataclass(frozen=True)
class Event:
    Type: str
    Source: str
    Data: dict       = field(default_factory=dict)
    Time: float      = field(default_factory=lambda: datetime.now().timestamp())
    Id: str          = field(default_factory=lambda: uuid.uuid4().hex[:12])
# ═══════════════════════════════════════════════════════════

#  Слухач подій з пріоритетом
@dataclass
class EventListener:
    Id: str
    Callback: Callable
    EventTypes: List[str]
    Priority: int = 0
    SourceFilter: Optional[str] = None

    # Перевірити чи слухач має обробляти цю подію
    def ShouldHandle(self, Ev: Event) -> bool:
        # Фільтрація за джерелом якщо вказано
        if self.SourceFilter and Ev.Source != self.SourceFilter:
            return False
        return Ev.Type in self.EventTypes or "*" in self.EventTypes

    # Обробити подію викликом callback
    def Handle(self, Ev: Event) -> bool:
        if callable(self.Callback):
            self.Callback(Ev)
            return True
        return False

# ═════════════════════════════════════════════════════════════════════
# APPLICATION CONTRACT
# Програми LCARS, які запускає Kernel.Master().
class Application:
    AppId: str = "unnamed"
    Title: str = "LCARS Application"
    Icon: str = ""
    Category: str = "general"

    # Викликається при запуску програми ядром
    def OnLaunch(self, KernelRef: Kernel) -> None:
        self.Kernel = KernelRef

    # Створити інтерфейс програми
    def CreateUI(self) -> Any:
        return None

    # Викликається при отриманні фокусу
    def OnFocus(self) -> None:
        pass

    # Викликається при мінімізації
    def OnMinimize(self) -> None:
        pass

    # Викликається при закритті програми
    def OnClose(self) -> None:
        pass


# Запис процесу — один екземпляр на запущену програму
class ProcessEntry:
    Counter = 0
    CounterLock = threading.Lock()

    # Створити запис процесу з унікальним PID
    def __init__(self, App: Application):
        with ProcessEntry.CounterLock:
            ProcessEntry.Counter += 1
            self.Pid = ProcessEntry.Counter
        self.App = App
        self.Started = datetime.now()
        self.Widget = None


# Таблиця процесів — зберігає всі запущені програми
class ProcessTable:
    def __init__(self):
        self.Table: Dict[int, ProcessEntry] = {}

    # Додати програму до таблиці процесів
    def Add(self, App: Application) -> ProcessEntry:
        Entry = ProcessEntry(App)
        self.Table[Entry.Pid] = Entry
        return Entry

    # Отримати процес за PID
    def Get(self, Pid: int) -> Optional[ProcessEntry]:
        return self.Table.get(Pid)

    # Знайти процес за AppId
    def Find(self, AppId: str) -> Optional[ProcessEntry]:
        for Entry in self.Table.values():
            if Entry.App.AppId == AppId:
                return Entry
        return None

    # Видалити процес з таблиці
    def Remove(self, Pid: int) -> Optional[ProcessEntry]:
        return self.Table.pop(Pid, None)

    # Отримати всі процеси
    def All(self) -> List[ProcessEntry]:
        return list(self.Table.values())

    # Кількість активних процесів
    def Count(self) -> int:
        return len(self.Table)

    # Закрити всі програми
    def KillAll(self) -> None:
        for Entry in list(self.Table.values()):
            Entry.App.OnClose()
        self.Table.clear()

# Комунікаційна шина LCARS.
# Всі компоненти спілкуються через події, ніколи прямими викликами.
# Підтримує wildcard "*" для підписки на всі події.
class EventBus:
    def __init__(self):
        self.Listeners: Dict[str, List[EventListener]] = {}
        self.History: List[Event] = []
        self.Lock = threading.Lock()
        self.MaxHistory = 2000
        self.ListenerCounter = 0

    # Згенерувати унікальний ідентифікатор для слухача
    def NextId(self) -> str:
        self.ListenerCounter += 1
        return f"L{self.ListenerCounter:04d}"

    # Підписатися на тип події. "*" = всі події. Повертає ID для відписки.
    def On(self, EventType: str, Callback: Callable, Priority: int = 0,
           SourceFilter: Optional[str] = None) -> str:
        with self.Lock:
            Listener = EventListener(
                Id=self.NextId(),
                Callback=Callback,
                EventTypes=[EventType],
                Priority=Priority,
                SourceFilter=SourceFilter
            )
            self.Listeners.setdefault(EventType, []).append(Listener)
            # Сортуємо за пріоритетом (вищий = раніше)
            self.Listeners[EventType].sort(key=lambda L: L.Priority, reverse=True)
            # Підписано — повертаємо ідентифікатор
            return Listener.Id

    # Відписатися за ID слухача.
    def Off(self, ListenerId: str) -> bool:
        with self.Lock:
            for EventType, Listeners in self.Listeners.items():
                for i, L in enumerate(Listeners):
                    if L.Id == ListenerId:
                        Listeners.pop(i)
                        # Відписано
                        return True
            return False

    # Legacy: відписатися за callback (повільніше)
    def OffCallback(self, EventType: str, Callback: Callable) -> None:
        with self.Lock:
            Current = self.Listeners.get(EventType, [])
            self.Listeners[EventType] = [
                L for L in Current if L.Callback is not Callback
            ]

    # Випустити подію. Повертає кількість оброблених слухачів.
    def Emit(self, EventType: str, Source: str = "system", **Data) -> int:
        Ev = Event(Type=EventType, Source=Source, Data=Data)
        Handled = 0
        ODN.Emit(f"EventBus.{EventType}", Source=Source, Data=Data)

        with self.Lock:
            self.History.append(Ev)
            # Обрізаємо історію якщо перевищено максимальний розмір
            if len(self.History) > self.MaxHistory:
                self.History = self.History[-self.MaxHistory // 2:]

            # Збираємо всіх слухачів для цього типу + wildcard
            Targets: List[EventListener] = []
            Targets.extend(self.Listeners.get(EventType, []))
            Targets.extend(self.Listeners.get("*", []))

        for Listener in Targets:
            if Listener.ShouldHandle(Ev):
                if Listener.Handle(Ev):
                    Handled += 1

        # Подія оброблена
        return Handled

    # Emit з EventType enum
    def EmitTyped(self, EType: EventType, Source: str = "system", **Data) -> int:
        return self.Emit(EType.value, Source, **Data)

    # Отримати останні події. Можна фільтрувати за типом.
    def GetHistory(self, EventType: Optional[EventType] = None, Limit: int = 50) -> List[Event]:
        with self.Lock:
            Source = self.History
            if EventType:
                Source = [E for E in Source if E.Type == EventType]
            return list(Source[-Limit:])

    # Статистика по подіям
    def GetStats(self) -> Dict[str, int]:
        with self.Lock:
            Stats: Dict[str, int] = {}
            for Ev in self.History:
                Stats[Ev.Type] = Stats.get(Ev.Type, 0) + 1
            return Stats

    # Вивести статистику
    def PrintStats(self) -> None:
        Stats = self.GetStats()
        # Вивід статистики

    # Очистити всіх слухачів та історію.
    def Clear(self) -> None:
        with self.Lock:
            self.Listeners.clear()
            self.History.clear()
            self.ListenerCounter = 0

# ═══════════════════════════════════════════════════════════
#  NEXUS (Центральний вузол даних) - координатор потоків даних в системі.
# НЕ сховище, а маршрутизатор між джерелами даних.
# Кожен канал має свою логіку обробки.
class Nexus:
    def __init__(self):
        self.Bus: Optional[EventBus] = None
        self.Stream: Transmission = Transmission(object)
        self.ChannelName: str = "nexus"
        self.Channels: Dict[str, Any] = {}

    # Зареєструвати компонент в Nexus
    def Register(self, Name: str, Component: Any) -> None:
        # Реєстр Nexus зберігає системні вузли, а Stream лишається транспортом.
        self.Channels[Name] = Component
        if self.Bus:
            self.Bus.Emit("nexus.registered", "Nexus", Channel=Name)

    # Прив'язати обробник до каналу
    def RegisterChannel(self, Name: str, Handler: Callable) -> None:
        self.Stream.Connect(Handler, Channel=self.ChannelName)
        if self.Bus:
            self.Bus.Emit("nexus.bound", "Nexus", Channel=Name)

    # Маршрутизувати дані через канал
    def Route(self, Channel: str, Data: Any) -> Any:
        self.Stream.Emit(Data, Channel=self.ChannelName)
        if self.Bus:
            self.Bus.Emit("nexus.routed", "Nexus", Channel=Channel, Data=Data)
        return Data

    # Отримати компонент за назвою каналу
    def GetChannel(self, Name: str) -> Optional[Callable]:
        return self.Channels.get(Name)

# ═══════════════════════════════════════════════════════════
#  THE KERNEL
# ◤ ЯДРО LCARS
# Один екземпляр на процес. Це І Є операційна система.
# Все працює через цей єдиний об'єкт.
#
# Використання:
#   K = Kernel()             # Отримати синглтон
#   K.Register(MySvc)        # Зареєструвати сервіс
#   K.Boot()                 # Запустити систему
#   K.Launch(MyApp)          # Запустити програму
#   K.Shutdown()             # Вимкнути систему
#
# Структура:
#   Kernel
#    ├── Events     (EventBus)        — шина подій
#    ├── State      (Store)           — спільний стан
#    ├── Services   (ServiceRegistry) — реєстр сервісів
#    └── Processes  (ProcessTable)    — таблиця програм

class Kernel:
    Instance: Optional[Kernel] = None
    Ready: bool = False

    # Створення синглтону — один екземпляр на весь процес
    def __new__(cls) -> Kernel:
        if cls.Instance is None:
            Inst = super().__new__(cls)
            Inst.Ready = False
            cls.Instance = Inst
        return cls.Instance

    # Ініціалізація ядра — лише при першому створенні
    def __init__(self):
        if self.Ready:
            return

        # Ідентичність
        self.Root: Path = ROOT
        self.Phase: SystemState = SystemState.OFF

        # Підсистеми
        self.Events: EventBus = EventBus()
        self.Nexus: Nexus = Nexus()
        self.Nexus.Bus = self.Events
        # Одна шина подій: ODN ретранслює сигнали в EventBus ядра.
        if hasattr(ODN, "EventBus"):
            ODN.EventBus = self.Events
        self.State: StateVault = StateVault(self.Events)
        self.Services: ServiceRegistry = ServiceRegistry()
        self.Modules: Dict[str, Any] = {}
        self.Processes: ProcessTable = ProcessTable()
        self.ProcessManager: ProcessManager = ProcessManager(str(self.Root))
        # Матриця є станом ядра, тому отримує спільні транспорт і реєстр.
        self.Matrix: SystemMatrix = SystemMatrix(
            Registry=registry,
            ODN=ODN,
            Nexus=self.Nexus
        )
        self.Matrix.RegisterWithNexus("Core.Matrix")
        from lcars.modules.sound import SoundManager
        self.sounds = SoundManager()

        # Середовище (заповнюється при Boot)
        self.Env: Dict[str, Any] = {}

        self.Ready = True
        # Ядро ініціалізовано

    # ─── BOOT ─────────────────────────────────────────────
    # Послідовність завантаження системи.
    # Phase 1: BIOS — перевірка середовища
    # Phase 2: SERVICES — запуск зареєстрованих сервісів
    # Phase 3: ONLINE — система готова
    # Повертає True якщо успішно (RUNNING або DEGRADED).
    def Boot(self) -> bool:
        if self.Phase not in (SystemState.OFF, SystemState.ERROR):
            # A degraded kernel is still operational and is an accepted boot
            # result according to the contract documented above.
            return self.Phase in (SystemState.RUNNING, SystemState.DEGRADED)

        self.InstallFoundation()
        self.Phase = SystemState.BOOTING
        self.Events.Emit("system.boot", "kernel", Phase="start")

        # Phase 1: BIOS
        if not self.Bios():
            self.Phase = SystemState.ERROR
            self.Events.Emit("system.error", "kernel", Phase="bios")
            return False

        # Phase 2: Services
        self.Events.Emit("system.boot", "kernel", Phase="services")
        Errors = self.Services.StartAll(self)

        # Визначення фінального стану залежно від помилок
        if Errors:
            self.Phase = SystemState.DEGRADED
            self.Events.Emit("system.degraded", "kernel", Errors=Errors)
        else:
            self.Phase = SystemState.RUNNING

        self.Events.Emit("system.ready", "kernel", Phase=self.Phase.name)
        # Система онлайн
        return True

    # Phase 1: Перевірка середовища виконання.
    def Bios(self) -> bool:
        V = sys.version_info
        if V < (3, 8):
            # Перевірка версії Python не пройдена
            return False

        self.Env = {
            "Python": f"{V.major}.{V.minor}.{V.micro}",
            "Platform": platform.system(),
            "Machine": platform.machine(),
            "Root": str(self.Root),
        }

        self.Events.Emit("system.bios", "kernel", **self.Env)
        # BIOS завершено
        return True

    # ─── SHUTDOWN ─────────────────────────────────────────
    # Коректне вимкнення: програми → сервіси → вимкнено.
    def Shutdown(self) -> None:
        if self.Phase in (SystemState.OFF, SystemState.SHUTTING_DOWN):
            return

        Prev = self.Phase
        self.Phase = SystemState.SHUTTING_DOWN
        self.Events.Emit("system.shutdown", "kernel", Previous=Prev.name)

        # Послідовність вимкнення

        # Закрити всі програми
        AppCount = self.Processes.Count()
        if AppCount:
            # Закриття програм
            self.Processes.KillAll()

        # Зупинити зовнішні процеси
        self.ProcessManager.stopAll()

        # Зупинити всі сервіси
        SvcCount = len(self.Services.Names())
        if SvcCount:
            # Зупинка сервісів
            self.Services.StopAll()

        self.Phase = SystemState.OFF
        self.Events.Emit("system.off", "kernel")
        # Система вимкнена

    # ─── SERVICE API ──────────────────────────────────────
    # Зареєструвати сервіс. Має бути ДО Boot().
    def Register(self, Svc: Service) -> None:
        self.Services.Register(Svc)

    # Додати модуль до системи
    def AddModule(self, Name: str, Module: Any) -> None:
        self.Modules[Name] = Module

    # Отримати сервіс за іменем.
    def Service(self, Name: str) -> Service:
        return self.Services.Require(Name)

    # Отримати модуль за назвою
    def Module(self, Name: str) -> Any:
        return self.Modules.get(Name)

    # Отримати список назв модулів
    def ModuleNames(self) -> List[str]:
        return list(self.Modules.keys())

    # Встановити базові сервіси та модулі системи
    def InstallFoundation(self) -> None:
        from lcars.service.alert import AlertService
        from lcars.service.network import Network
        from lcars.service.plugin import PluginManager
        from lcars.service.copilot import Copilot
        from lcars.modules.memory import ComputerMemory
        from lcars.modules.sound import SoundManager
        from lcars.modules.mode import ModeManager
        from lcars.modules.net import NetworkManager

        # Реєстрація сервісів — кожен перевіряється на наявність
        if self.Services.Get("alert") is None:
            self.Register(AlertService())
        if self.Services.Get("network") is None:
            self.Register(Network())
        if self.Services.Get("plugin") is None:
            self.Register(PluginManager())
        if self.Services.Get("file") is None:
            from lcars.service.filesystem import FileService
            self.Register(FileService())
            
        from lcars.engineering.maintenance import StructuralIntegrity
        if self.Services.Get("structural") is None:
            self.Register(StructuralIntegrity())
            
        from lcars.engineering.isolinear import IsolinearCore
        if self.Services.Get("isolinear") is None:
            self.Register(IsolinearCore())
            
        from lcars.service.astrometrics import AstrometricsService
        if self.Services.Get("astrometrics") is None:
            self.Register(AstrometricsService())
            
        from lcars.service.holodeck import HolodeckCore
        if self.Services.Get("holodeck") is None:
            self.Register(HolodeckCore())

        # Реєстрація модулів — кожен перевіряється на наявність
        if "memory" not in self.Modules:
            self.AddModule("memory", ComputerMemory())
        if "sound" not in self.Modules:
            self.AddModule("sound", SoundManager())
        if "mode" not in self.Modules:
            self.AddModule("mode", ModeManager())
        if "net" not in self.Modules:
            self.AddModule("net", NetworkManager())
        if "copilot" not in self.Modules:
            self.AddModule("copilot", Copilot(projectRoot=str(self.Root)))

    # ─── APPLICATION API ──────────────────────────────────
    # Запустити програму. Повертає PID.
    # Якщо вже запущена — виводить на передній план.
    def Master(self, App: Application) -> int:
        Existing = self.Processes.Find(App.AppId)
        if Existing:
            Existing.App.OnFocus()
            return Existing.Pid

        Entry = self.Processes.Add(App)
        App.OnLaunch(self)
        Entry.Widget = App.CreateUI()
        self.Events.Emit("app.launched", "kernel",
                         AppId=App.AppId, Pid=Entry.Pid, Title=App.Title)
        # Програму запущено
        return Entry.Pid

    # Запустити зовнішній процес
    def ProcStart(self, Name: str, FullPath: str, Args: Optional[List[str]] = None) -> bool:
        return self.ProcessManager.Start(Name, FullPath, Args)

    # Зупинити зовнішній процес
    def ProcStop(self, Name: str) -> bool:
        return self.ProcessManager.Stop(Name)

    # Прочитати вивід процесу
    def ProcRead(self, Name: str) -> str:
        return self.ProcessManager.Read(Name)

    # Перевірити чи процес працює
    def ProcRun(self, Name: str) -> bool:
        return self.ProcessManager.Running(Name)

    # Отримати список запущених процесів
    def ProcList(self) -> List[str]:
        return self.ProcessManager.List()

    # Compatibility aliases
    StartProcess = ProcStart
    StopProcess = ProcStop
    ProcessOutput = ProcRead
    ProcessRunning = ProcRun
    ProcessList = ProcList

    # ─── EVENT SHORTCUTS ──────────────────────────────────
    # Випустити подію від ядра.
    # etype може бути Enum EventType, рядок, або None
    # Повертає кількість оброблених слухачів
    def Emit(self, etype: Union[EventType, str, None] = None, **Data) -> int:
        # Конвертація типу події в рядок для EventBus
        event_type_str = etype.value if isinstance(etype, Enum) else (etype or "*")
        
        return self.Events.Emit(event_type_str, "kernel", **Data)

    # Підписатися на системні події.
    # etype може бути Enum EventType, рядок "*", None, або Callable
    # Callback має бути callable (функція або метод)
    # Повертає ідентифікатор підписки або None якщо не вдалося
    def On(self, etype: Union[EventType, str, None, Callable] = None,
           Callback: Optional[Callable] = None,
           Priority: int = 0, SourceFilter: Optional[str] = None) -> Optional[str]:

        # Універсальна обробка аргументів: On(callback) коли перший аргумент це функція
        ActualCallback: Optional[Callable] = Callback
        ActualEventType: Union[EventType, str, None] = None

        if Callback is None and callable(etype):
            ActualCallback = etype  # type: ignore
            ActualEventType = "*"
        else:
            ActualEventType = etype  # type: ignore

        # Конвертація типу події в рядок для EventBus
        event_type_str = ActualEventType.value if isinstance(ActualEventType, Enum) else (ActualEventType or "*")

        # Перевірка що callback не None перед викликом EventBus.On
        if ActualCallback is None:
            return None

        return self.Events.On(event_type_str, ActualCallback, Priority, SourceFilter)

    # ─── DIAGNOSTICS ──────────────────────────────────────
    # Повний знімок стану системи.
    def Status(self) -> Dict[str, Any]:
        return {
            "Phase": self.Phase.name,
            "Env": self.Env,
            "Store": self.State.Keys(),
            "Services": {
                "Registered": self.Services.Names(),
                "Health": self.Services.HealthCheck(),
            },
            "Modules": self.ModuleNames(),
            "Processes": [
                {"Pid": E.Pid, "App": E.App.AppId, "Title": E.App.Title}
                for E in self.Processes.All()
            ],
        }

    # ─── TESTING ──────────────────────────────────────────
    # Знищити синглтон. Тільки для тестів.
    @classmethod
    def Reset(cls) -> None:
        if cls.Instance and cls.Instance.Phase != SystemState.OFF:
            cls.Instance.Shutdown()
        cls.Instance = None
        ProcessEntry.Counter = 0

    # Зв'язати з MasterSystem для зворотної сумісності
    def SetSystem(self, System) -> None:
        self.MasterSystem = System

    # Представлення ядра у вигляді рядка
    def __repr__(self) -> str:
        SvcN = len(self.Services.Names())
        ModN = len(self.Modules)
        AppN = self.Processes.Count()
        return f"<Kernel Phase={self.Phase.name} Services={SvcN} Modules={ModN} Apps={AppN}>"

# Сховище стану — просте сховище ключ-значення
# Генерує події при зміні даних через EventBus
class StateVault:
    # Просте сховище ключ-значення
    # Генерує події при зміні даних через EventBus

    def __init__(self, Bus: 'EventBus'):
        self.Bus = Bus
        self.Data: Dict[str, Any] = {}
        self.Lock = threading.Lock()

    # Встановити значення за ключем
    def Set(self, Key: str, Value: Any) -> None:
        with self.Lock:
            Old = self.Data.get(Key)
            self.Data[Key] = Value
        self.Bus.Emit("state.set", "StateVault", Key=Key, Value=Value, Old=Old)

    # Отримати значення за ключем
    def Get(self, Key: str, Default: Any = None) -> Any:
        with self.Lock:
            return self.Data.get(Key, Default)

    # Перевірити наявність ключа
    def Has(self, Key: str) -> bool:
        with self.Lock:
            return Key in self.Data

    # Видалити ключ зі сховища
    def Delete(self, Key: str) -> None:
        with self.Lock:
            self.Data.pop(Key, None)
        self.Bus.Emit("state.delete", "StateVault", Key=Key)

    # Отримати всі ключі
    def Keys(self) -> List[str]:
        with self.Lock:
            return list(self.Data.keys())

    # Зробити знімок всього стану
    def Snapshot(self) -> Dict[str, Any]:
        with self.Lock:
            return dict(self.Data)

    # Очистити сховище
    def Clear(self) -> None:
        with self.Lock:
            self.Data = {}
        self.Bus.Emit("state.clear", "StateVault")
    
# Ініціалізація шляхів при імпорті
# Типи подій системи LCARS — використовуються для підписки та випуску подій
class EventType(Enum):
    # Життєвий цикл
    APP_STARTUP = "app:startup"
    APP_SHUTDOWN = "app:shutdown"
    APP_CONFIG_CHANGED = "app:config_changed"

    # Плагіни
    PLUGIN_LOADED = "plugin:loaded"
    PLUGIN_UNLOADED = "plugin:unloaded"

    # UI
    UI_THEME_CHANGED = "ui:theme_changed"
    UI_COMPONENT_UPDATED = "ui:component_updated"

    # Системні (внутрішні)
    SYSTEM_BOOT = "system:boot"
    SYSTEM_READY = "system:ready"
    SYSTEM_DEGRADED = "system:degraded"
    SYSTEM_SHUTDOWN = "system:shutdown"
    STORE_CHANGED = "store:changed"
    STORE_DELETED = "store:deleted"

__all__ = [
    "SystemState",
    "Event",
    "EventListener",
    "EventBus",
    "Nexus",
    "Kernel",
    "StateVault",
    "EventType",
]
