# ◤ LCARS QUANTUM MICROKERNEL // PURE HARDWARE PRISTINE KERNEL 🖖
# =============================================================================
# ФАЙЛ: lcars/core/kernel.py
# ОПИС: Чисте низькорівневе апаратне мікроядро зорельота (Quantum Microkernel).
#       ВІДПОВІДАЛЬНІСТЬ (ВИКЛЮЧНО АПАРАТНИЙ РІВЕНЬ):
#       1. Event / EventBus — квантова шина системних сигналів та подій.
#       2. Nexus — міждоменний маршрутизатор каналів та оптичних кондуїтів.
#       3. SystemMatrix — просторова 3D-матриця топології заліза (100x100x100).
#       4. ProcessTable / ProcessManager — облік та диспетчеризація процесів.
#       5. BootSequence — перший фізичний запуск: оживляє BoardComputer,
#          який розгортає MasterSystem.
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
from lcars.base.info import getVersion
from lcars.base.type import LCARS, SystemComponent
from lcars.base.register import registry
from lcars.core.signal import ODN, Transmission
from lcars.core.matrix import SystemMatrix
from lcars.modules.process import Application, ProcessEntry, ProcessTable, ProcessManager
from lcars.system.software import SystemState

ROOT = LCARS.System.Path(__file__).resolve().parents[2] if hasattr(LCARS.System, "Path") else None
# ═════════════════════════════════════════════════════════════════════
# 1. QUANTUM EVENT SYSTEM (КВАНТОВА ШИНА СИСТЕМНИХ ПОДІЙ)
# ═════════════════════════════════════════════════════════════════════
class Event(LCARS):
    # Окремий квантовий імпульс-подія зі штампом часу, джерелом та корисним навантаженням
    def __init__(self, Type, Source, Data = None, Time = None, Id = None):
        super().__init__()
        self.Type = Type
        self.Source = Source
        self.Data = Data or {}
        DateTimeMod = getattr(LCARS.System, "Time", None)
        self.Time = Time if Time is not None else (DateTimeMod.DateTime.now().timestamp() if (DateTimeMod and hasattr(DateTimeMod, "DateTime")) else 0.0)
        UuidMod = getattr(LCARS.System, "Uuid", None)
        GeneratedId = "0"
        if UuidMod and hasattr(UuidMod, "uuid4"):
            Obj = UuidMod.uuid4()
            GeneratedId = getattr(Obj, "hex", str(Obj))[:12]
        else:
            import uuid
            GeneratedId = uuid.uuid4().hex[:12]
        self.Id = Id if Id is not None else GeneratedId
# Центральна квантова шина підписок та розподілу подій між підсистемами
class EventBus(LCARS):
    def __init__(self):
        super().__init__()
        self.Listeners = {}
        self.History = []
        self.Lock = LCARS.System.Threading.Lock() if hasattr(LCARS.System, "Threading") else None
        self.MaxHistory = 2000
        self.ListenerCounter = 0

    # Генерація унікального текстового ідентифікатора для підписки
    def NextId(self):
        self.ListenerCounter += 1
        return f"L{self.ListenerCounter:04d}"

    # Підписка на подію за типом із пріоритетом та фільтром джерела
    def On(self, EventTypeStr, CallbackFunc, Priority = 0, SourceFilter = None):
        ListenerId = self.NextId()
        Entry = (ListenerId, CallbackFunc, Priority, SourceFilter)
        self.Listeners.setdefault(EventTypeStr, []).append(Entry)
        self.Listeners[EventTypeStr].sort(key=lambda item: item[2], reverse=True)
        return ListenerId

    # Відписка від події за отриманим ідентифікатором
    def Off(self, ListenerId):
        for EventTypeStr, ListenerList in self.Listeners.items():
            for Index, Entry in enumerate(ListenerList):
                if Entry[0] == ListenerId:
                    del ListenerList[Index]
                    return True
        return False

    # Трансляція події всім підписникам та відправка копії в шину ODN
    def Emit(self, EventTypeStr, Source = "kernel", **Data):
        Ev = Event(Type=EventTypeStr, Source=Source, Data=Data)
        Handled = 0
        ODN.Transmit(f"EventBus.{EventTypeStr}", Data=Data, Source=Source)

        self.History.append(Ev)
        if len(self.History) > self.MaxHistory:
            self.History = self.History[-self.MaxHistory // 2:]

        Targets = []
        Targets.extend(self.Listeners.get(EventTypeStr, []))
        Targets.extend(self.Listeners.get("*", []))

        for ListenerId, CallbackFunc, Priority, SourceFilter in Targets:
            if SourceFilter and Ev.Source != SourceFilter:
                continue
            if callable(CallbackFunc):
                CallbackFunc(Ev)
                Handled += 1
        return Handled

    # Отримання списку останніх подій з можливістю фільтрації за типом
    def GetHistory(self, EventTypeFilter = None, Limit = 50):
        Source = self.History
        if EventTypeFilter:
            Source = [E for E in Source if E.Type == EventTypeFilter]
        return list(Source[-Limit:])

    # Повне очищення списку слухачів та історії
    def Clear(self):
        self.Listeners.clear()
        self.History.clear()
        self.ListenerCounter = 0
# ═════════════════════════════════════════════════════════════════════
# 2. NEXUS (МІЖДОМЕННИЙ МАРШРУТИЗАТОР)
# ═════════════════════════════════════════════════════════════════════
class Nexus(LCARS):
    # Маршрутизатор прямого обміну даними між внутрішніми доменами ядра
    def __init__(self, Bus = None):
        super().__init__()
        self.Bus = Bus
        self.Channels = {}
        self.Streams = {}

    # Прив'язка шини подій для реєстраційних сповіщень
    def BindBus(self, Bus):
        self.Bus = Bus

    # Реєстрація каналу компонента в таблиці маршрутизації
    def Register(self, Name, Component):
        self.Channels[Name] = Component
        if self.Bus:
            self.Bus.Emit("nexus.registered", "Nexus", Channel=Name)

    # Отримання зареєстрованого компонента за його системним іменем
    def ResolveChannel(self, Name):
        return self.Channels.get(Name)

    # Канонічний аліас пошуку каналу
    Get = ResolveChannel

    # Створення або отримання прямого потоку Transmission за шляхом
    def Stream(self, Path):
        if Path not in self.Streams:
            self.Streams[Path] = Transmission(Id=f"nexus_{Path}")
        return self.Streams[Path]

    # Маршрутизація корисного навантаження у вказаний канал
    def Route(self, TargetChannel, Payload, Source = "unknown"):
        Comp = self.ResolveChannel(TargetChannel)
        if Comp:
            Handler = getattr(Comp, "HandleNexus", None) or getattr(Comp, "Receive", None)
            if callable(Handler):
                return Handler(Payload, Source=Source)
        if self.Bus:
            self.Bus.Emit(f"nexus.routed.{TargetChannel}", Source, Payload=Payload)
        return None

    # Видалення каналу з таблиці маршрутизатора
    def Unregister(self, Name):
        if Name in self.Channels:
            del self.Channels[Name]
            if self.Bus:
                self.Bus.Emit("nexus.unregistered", "Nexus", Channel=Name)
            return True
        return False
# ═════════════════════════════════════════════════════════════════════
# 3. KERNEL (ЧИСТЕ АПАРАТНЕ МІКРОЯДРО ЗОРЕЛЬОТА)
# ═════════════════════════════════════════════════════════════════════
class Kernel(LCARS):
    Instance = None
    Ready = False

    def __new__(cls):
        if cls.Instance is None:
            Inst = super().__new__(cls)
            Inst.Ready = False
            cls.Instance = Inst
        return cls.Instance

    # Ініціалізація апаратних примітивів мікроядра
    def __init__(self):
        if self.Ready:
            return

        self.Root = ROOT
        self.Phase = SystemState.OFF

        # 1. Квантова шина подій мікроядра
        self.Events = EventBus()

        # 2. Міждоменний маршрутизатор каналів
        self.Nexus = Nexus(self.Events)

        # 3. Просторова 3D-матриця топології заліза
        self.Matrix = SystemMatrix(
            Dimensions=[100, 100, 100],
            Id="Core.Matrix",
            Registry=registry,
            ODN=ODN,
            Nexus=self.Nexus,
        )
        self.Matrix.RegisterWithNexus("Core.Matrix")

        # 4. Підсистема диспетчеризації процесів
        self.Processes = ProcessTable()
        self.ProcessManager = ProcessManager(str(self.Root))
        self.Env = {}

        # 5. Посилання на Комп'ютер та Систему
        self.Computer = None
        self.System = None

        self.Ready = True
        registry.Register("Core.Kernel", "lcars.core.kernel", "Kernel")
        registry.Register("Core.Matrix", "lcars.core.matrix", "SystemMatrix")

    # Отримання синглтона мікроядра
    @classmethod
    def GetInstance(cls):
        return cls()

    # Початковий апаратний старт зорельота (Bootstrap)
    def Boot(self):
        self.SetPhase(SystemState.BOOTING)
        self.Events.Emit("kernel.boot.start", "kernel")

        # 1. Ядро запускає Бортовий Комп'ютер
        from lcars.core.computer import BoardComputer
        self.Computer = BoardComputer.GetInstance()
        self.Nexus.Register("Core.Computer", self.Computer)

        # 2. Бортовий Комп'ютер ініціалізує та розгортає Головну Систему
        from lcars.core.system import MasterSystem
        self.System = MasterSystem.GetInstance()
        self.Nexus.Register("Core.System", self.System)

        self.SetPhase(SystemState.RUNNING)
        self.Events.Emit("kernel.ready", "kernel", Phase=self.Phase.Name)

        # 3. Агент ініціалізується та запускає startup діагностику
        Agent = self.Computer.GetAgent()
        if Agent and hasattr(Agent, "Startup"):
            StartupReport = Agent.Startup()
            self.Events.Emit("agent.ready", "kernel", Report=StartupReport)
        else:
            self.Events.Emit("agent.init.skip", "kernel")

        return True

    # Зміна поточної фази завантаження чи функціонування мікроядра
    def SetPhase(self, NewPhase):
        Old = self.Phase
        self.Phase = NewPhase
        self.Events.Emit("kernel.phase.changed", "kernel", Previous=Old.name if hasattr(Old, "name") else str(Old), Current=NewPhase.name if hasattr(NewPhase, "name") else str(NewPhase))
        return self.Phase

    # Повне та безпечне вимкнення процесів ядра
    def Shutdown(self):
        if self.Phase in (SystemState.OFF, SystemState.SHUTTING_DOWN):
            return

        Prev = self.Phase
        self.Phase = SystemState.SHUTTING_DOWN
        self.Events.Emit("kernel.shutdown", "kernel", Previous=Prev.name if hasattr(Prev, "name") else str(Prev))

        # Зупинка всіх активних процесів
        if self.Processes.Count():
            self.Processes.KillAll()

        self.ProcessManager.StopAll()

        self.Phase = SystemState.OFF
        self.Events.Emit("kernel.off", "kernel")

    # ─── УПРАВЛІННЯ ПРОЦЕСАМИ (PROCESS ENGINE) ───────────
    # Реєстрація та взяття під контроль графічного застосунку зорельота
    def RegisterProcess(self, App):
        App.State = "running"
        self.Processes.Register(App)
        Entry = self.Processes.GetByApp(App.AppId)
        Pid = Entry.Pid if Entry else -1
        self.Events.Emit("process.started", "kernel", Pid=Pid, App=App.AppId, Title=App.Title)
        return Pid

    # Завершення процесу застосунку з відповідним кодом виходу
    def TerminateProcess(self, App, ExitCode = 0):
        Entry = self.Processes.GetByApp(App.AppId)
        if Entry:
            self.Processes.Unregister(Entry.Pid)
            self.Events.Emit("process.exited", "kernel", Pid=Entry.Pid, App=App.AppId, Code=ExitCode)
        App.State = "stopped"

    # Запуск зовнішнього системного скрипта чи програми
    def LaunchScript(self, PathStr, *Args):
        return self.ProcessManager.LaunchScript(PathStr, list(Args))

    # ─── АПАРАТНИЙ СТАН ТА СТАТИСТИКА ────────────────────
    def Status(self):
        return {
            "Phase": self.Phase.name if hasattr(self.Phase, "name") else str(self.Phase),
            "Env": self.Env,
            "Matrix": {
                "Dimensions": self.Matrix.Dimensions,
                "NodesCount": len(self.Matrix.Nodes),
                "Domains": list(self.Matrix.Domains.keys()),
            },
            "ProcessesCount": self.Processes.Count(),
            "Processes": [
                {"Pid": E.Pid, "App": E.App.AppId, "Title": E.App.Title}
                for E in self.Processes.All()
            ],
        }

    # Повне скидання стану мікроядра для перезапуску або тестів
    @classmethod
    def Reset(cls):
        if cls.Instance and cls.Instance.Phase != SystemState.OFF:
            cls.Instance.Shutdown()
        cls.Instance = None
        ProcessEntry.Counter = 0

    # Текстове представлення об'єкта мікроядра
    def __repr__(self):
        AppN = self.Processes.Count()
        NodesN = len(self.Matrix.Nodes)
        PhaseName = self.Phase.name if hasattr(self.Phase, "name") else str(self.Phase)
        return f"<Kernel Phase={PhaseName} Apps={AppN} MatrixNodes={NodesN}>"

__all__ = [
    "SystemState",
    "Event",
    "EventBus",
    "Nexus",
    "Kernel",
]
