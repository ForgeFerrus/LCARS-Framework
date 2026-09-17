# ◤ TITANIUM SYSTEM CONDUIT & SERVICE MANAGER 🖖
# =============================================================================
# ФАЙЛ: lcars/core/conduit.py
# ОПИС: Оптичний кондуїт та диспетчер життєвого циклу служб зорельота LCARS.
#       Служби підключаються як кондуїти операційного середовища зорельота (MasterSystem),
#       взаємодіючи через системний хост та шину оптичних даних (ODN).
#       ВІДПОВІДАЛЬНІСТЬ:
#       1. Service / ConduitSubsystem — базовий контракт корабельної служби.
#       2. ServiceRegistry / ConduitRegistry — реєстр, топологічний запуск та Watchdog.
#       3. Повний життєвий цикл: OnInit(SystemHost), OnStart(), OnStop(), Heartbeat(), Health().
#       4. Автоматичний перезапуск та ізоляція збоїв (AutoRestart).
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================
from lcars.base.type import LCARS, SystemComponent
from lcars.core.signal import ODN, Transmission
# ═════════════════════════════════════════════════════════════════════
# 1. BASE SYSTEM SERVICE (КОНТРАКТ СЛУЖБИ ЗОРЕЛЬОТА / КОНДУЇТУ)
# ═════════════════════════════════════════════════════════════════════
class Service(SystemComponent):
    TypeName = "LCARSService"
    Type = "Service"
    Name: str = "UnnamedSubsystem"
    Dependencies: list = []
    AutoRestart: bool = True
    MaxRestarts: int = 3
    SystemHost: Any = None
    Running: bool = False
    Healthy: bool = True
    RestartCount: int = 0
    LastError: Any = None
    LastHeartbeat: float = 0.0
    # Прив'язка служби до операційного середовища зорельота
    def BindHost(self, SystemHostRef: Any = None) -> "Service":
        self.SystemHost = SystemHostRef
        return self
    OnInit = BindHost
    # Запуск фонової обробки сервісу
    def OnStart(self) -> "Service":
        self.Running = True
        self.Healthy = True
        TimeSubsystem = getattr(LCARS.System, "Time", None)
        self.LastHeartbeat = TimeSubsystem.time() if TimeSubsystem and hasattr(TimeSubsystem, "time") else 0.0
        ODN.Transmit(f"Service.{self.Name}.Started", Service=self.Name, Status="ONLINE")
        return self
    # Зупинка та коректне вивільнення ресурсів
    def OnStop(self) -> "Service":
        self.Running = False
        ODN.Transmit(f"Service.{self.Name}.Stopped", Service=self.Name, Status="OFFLINE")
        return self
    # Сигнал активності для сторожового таймера (Watchdog)
    def Heartbeat(self) -> bool:
        TimeSubsystem = getattr(LCARS.System, "Time", None)
        self.LastHeartbeat = TimeSubsystem.time() if TimeSubsystem and hasattr(TimeSubsystem, "time") else 0.0
        self.Healthy = True
        return self.Healthy

    # Перевірка життєздатності служби для системної діагностики
    def Health(self):
        IsHealthy = getattr(self, "Healthy", True)
        IsRunning = getattr(self, "Running", True)
        return bool(IsHealthy and IsRunning)

    # Аварійний перезапуск служби
    def Restart(self):
        if self.RestartCount < self.MaxRestarts:
            self.RestartCount += 1
            self.OnStop()
            self.OnStart()
            ODN.Transmit(f"Service.{self.Name}.Restarted", Service=self.Name, Count=self.RestartCount)
            return True
        self.Healthy = False
        ODN.Transmit(f"Service.{self.Name}.Failed", Service=self.Name, Reason="MAX_RESTARTS_EXCEEDED")
        return False
# ═════════════════════════════════════════════════════════════════════
# 2. SYSTEM SERVICE REGISTRY & WATCHDOG (ДИСПЕТЧЕР КОНДУЇТІВ)
# ═════════════════════════════════════════════════════════════════════
class ServiceRegistry(LCARS):
    def __init__(self):
        super().__init__()
        self.Services = {}
        self.StartOrder = []
        self.SystemHost = None
        self.Lock = LCARS.System.Threading.RLock() if hasattr(LCARS.System, "Threading") else None

    # Прив'язка екземпляра головної системи
    def BindSystemHost(self, SystemHostRef):
        self.SystemHost = SystemHostRef

    # Реєстрація системного сервісу
    def Register(self, Svc):
        if Svc is None:
            return
        Name = str(getattr(Svc, "Name", "unnamed")).strip().lower()
        if not Name:
            return
        self.Services[Name] = Svc
        ODN.Transmit("ServiceRegistry.Registered", Service=Name)

    # Отримання зареєстрованого сервісу за ім'ям
    def Get(self, Name):
        Normalized = str(Name or "").strip().lower()
        return self.Services.get(Normalized)

    # Обов'язкове отримання або створення заглушки
    def Require(self, Name):
        Normalized = str(Name or "").strip().lower()
        Svc = self.Services.get(Normalized)
        if Svc is None:
            Svc = Service(Id=f"Service.{Normalized}")
            Svc.Name = Normalized
            self.Services[Normalized] = Svc
        return Svc

    # Повна перевірка здоров'я всіх системних служб та Watchdog
    def HealthCheck(self):
        Result = {}
        for Name, Svc in self.Services.items():
            HealthFn = getattr(Svc, "Health", None)
            IsAlive = bool(HealthFn()) if callable(HealthFn) else True
            Result[Name] = IsAlive
            
            # Якщо служба впала, а стоїть AutoRestart — автоматично перезапускаємо
            if not IsAlive and getattr(Svc, "AutoRestart", False) and getattr(Svc, "Running", False):
                RestartFn = getattr(Svc, "Restart", None)
                if callable(RestartFn):
                    RestartFn()
        return Result

    # Запуск усіх зареєстрованих сервісів з розв'язанням графу залежностей
    def StartAll(self, SystemHostRef = None):
        self.SystemHost = SystemHostRef
        Errors = []
        Started = set()

        def Resolve(Name, Chain):
            if Name in Started:
                return True
            Svc = self.Services.get(Name)
            if Svc is None:
                Errors.append(f"MISSING_DEPENDENCY: {Name}")
                return False
            if Name in Chain:
                Errors.append(f"CIRCULAR_DEPENDENCY: {Name}")
                return False

            Deps = getattr(Svc, "Dependencies", []) or []
            for Dep in Deps:
                DepNormalized = str(Dep).strip().lower()
                if not Resolve(DepNormalized, Chain | {Name}):
                    Errors.append(f"REQUIRED_BY: {Name}")
                    return False

            InitFn = getattr(Svc, "OnInit", None)
            if callable(InitFn):
                InitFn(SystemHostRef)
            StartFn = getattr(Svc, "OnStart", None)
            if callable(StartFn):
                StartFn()
            Started.add(Name)
            self.StartOrder.append(Name)
            return True

        for ServiceKey in list(self.Services.keys()):
            Resolve(ServiceKey, frozenset())

        ODN.Transmit("ServiceRegistry.AllStarted", Count=len(Started), Errors=Errors)
        return Errors

    # Зупинка всіх служб у зворотному порядку
    def StopAll(self):
        for Name in reversed(self.StartOrder):
            Svc = self.Services.get(Name)
            if Svc:
                StopFn = getattr(Svc, "OnStop", None)
                if callable(StopFn):
                    StopFn()
        self.StartOrder.clear()
        ODN.Transmit("ServiceRegistry.AllStopped")

    # Перезапуск конкретної служби за її іменем
    def RestartSubsystem(self, Name):
        Normalized = str(Name or "").strip().lower()
        Svc = self.Services.get(Normalized)
        if Svc:
            RestartFn = getattr(Svc, "Restart", None)
            if callable(RestartFn):
                return RestartFn()
        return False

    # Отримання списку імен усіх зареєстрованих служб
    def Names(self):
        return list(self.Services.keys())


# Канонічні аліаси зорельота
ConduitSubsystem = Service
ConduitRegistry = ServiceRegistry

__all__ = [
    "Service",
    "ConduitSubsystem",
    "ServiceRegistry",
    "ConduitRegistry",
]

