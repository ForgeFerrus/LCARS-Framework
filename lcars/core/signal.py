# LCARS Optical Data Network (ODN) — ізолінійна мережа
# ОПИС: Єдина мережа сигналів, протоколів і директив для бортового комп'ютера.
# ─────────────────────────────────────────────────────────────────────────────
from typing import Any, Callable, List, Dict, Optional
from lcars.base.info import Version, Passport
from lcars.base.type import Directive, SystemComponent, LCARS

# Квантово-оптичний потік передачі даних LCARS (Двосторонній імпульс / Пакет)
class Transmission(Directive):
    TypeName = "LCARSTransmission"
    Type = "Transmission"
    State = "Idle"
    Source = "System"
    Channel: Optional[str] = None
    TypeArgs: tuple = ()
    Protocols = None
    Target = None
    Route: list = []
    Data: Any = None
    Response: Any = None
    Flags: Dict[str, Any] = {}
    Priority = 0
    Timestamp = 0.0

    # Доставка сигналу до вузла-приймача
    def Deliver(self, Receiver: Callable) -> Any:
        self.State = "Delivered"
        Result = Receiver(self)
        if Result is not None:
            self.Response = Result
        return Result

    # Позначення виконання успішно завершеним
    def Complete(self, ResponseData: Any = None) -> "Transmission":
        if ResponseData is not None:
            self.Response = ResponseData
        self.State = "Completed"
        return self

    # Скасувати виконання
    def Cancelled(self) -> "Transmission":
        self.State = "Cancelled"
        return self

    # Фіксація збою під час передачі в кондуїті   
    def Fail(self, Reason: Any = None) -> "Transmission":
        self.Response = Reason
        self.State = "Failed"
        return self
        
    # Випустити результат у цей сигнал. Встановлює дані та завершений стан.
    def Transmit(self, *Args, Channel: Optional[str] = None, **Flags) -> Any:
        Path = Channel or Flags.pop("Channel", None) or self.Channel or f"Transmission.{id(self)}"
        Payload = Args[0] if len(Args) == 1 else (Args if Args else None)
        return ODN.Transmit(Path, Data=Payload, **Flags)
# =============================================================================
# OTN (OPTICAL TRANSPORT LINE) — статичний транспортний канал
# Оптоволоконна лінія передачі світлового імпульсу зорельота.
# =============================================================================
class OpticalTransportLine(SystemComponent):
    TypeName = "OpticalTransportLine"
    Type = "OTN"
    Version = Version.Release
    # Фізичні параметри середовища
    Mode: str = "Optical"           # "Optical" (ізолінійне волокно) або "Quantum" (субпросторовий тунель)
    Bandwidth: int = 1000000        # Пропускна здатність (Квадів/сек)
    Latency: float = 0.0            # Затримка лінії (мілісекунди)
    ActivePipes: int = 0            # Лічильник активних імпульсів у магістралі

    # Передати сигнал через оптичну лінію
    def Transmit(self, Packet: Transmission, Receivers: Optional[List[Callable]] = None) -> Transmission:
        self.ActivePipes += 1
        Packet.Protocol = self.Protocol
        Packet.State = "Transmitting"
        TargetList = list(Receivers or [])
        LastResponse = None
        for Receiver in TargetList:
            if not callable(Receiver):
                continue
            Response = Packet.Deliver(Receiver)
            if Response is not None:
                LastResponse = Response
        Packet.Response = LastResponse
        Packet.State = "Completed"
        self.ActivePipes = max(0, self.ActivePipes - 1)
        return Packet

# Optical Data Network -- Ізолінійна мережа LCARS
# Призначення:
#   - єдина мережа передачі;
#   - логічні канали;
#   - маршрутизація сигналів;
#   - резолюція каналів.
class ODN(SystemComponent):
    
    self.OTN = OTN()
        # Класична ізолінійна мережа
        # Квантова мережа
        self.Quantum = {}
        self.Network = {
            "Optical": {},
            "Quantum": {}
        }
        # Активний режим
        self.Mode = "Optical"
    
        def SetMode(self, ModeName: str) -> OpticalTransportNetwork:
            self.Mode = "Quantum" if (ModeName).lower() == "quantum" else "Optical"
            # Протоколи
            self.Protocols = {}
            # Маршрути
            self.Routes = {}
            self._BlackBox = None
        # ------------------------------------------------------------------
        # Отримати поточну мережу за активним режимом
        def Current(self):
            return self.Network[self.Mode]

        # Переключити на оптичний режим
        def OpticalMode(self):
            self.Mode = "Optical"
            return self

        # Переключити на квантовий режим
        def QuantumMode(self):
            self.Mode = "Quantum"
            return self

        # Канали
        # Отримати або створити канал за шляхом
        def Channel(self, Path):
            Network = self.Current()
            Channel = Network.get(Path)
            if Channel is None:
                Channel = Transmission()
                Channel.Channel = Path
                Channel.State = "Online"
                Network[Path] = Channel
                self.BlackBox.RegisterChannel(Path)
            return Channel

        # Перевірити існування каналу
        def Exists(self, Path):
            return Path in self.Current()

        # Активувати канал
        def Online(self, Path):
            Channel = self.Channel(Path)
            Channel.State = "Online"
            return Channel

        # Деактивувати канал
        def Offline(self, Path):
            Channel = self.Channel(Path)
            Channel.State = "Offline"
            return Channel

        # Отримати статус каналу
        def Status(self, Path):
            return self.Channel(Path).State

        # Випустити сигнал у канал з даними та прапорцями.
        # Після публікації викликає всіх підписників каналу.
        def Emit(self, Path, Data=None, **Kwargs):
            Signal = self.Channel(Path)
            Signal.Data = Data if Data is not None else Kwargs
            Signal.Flags = dict(Kwargs)
            Signal.State = "Completed"
            Signal.Channel = Path
            # Сповіщаємо підписників каналу
            for Callback in getattr(Signal, "_listeners", []):
                Callback(Signal)
            # Bridge до EventBus ядра — єдина шина подій системи.
            if hasattr(self, "EventBus") and self.EventBus is not None:
                if not str(Path).startswith("EventBus."):
                    self.EventBus.Emit(Path, "ODN", Data=Data)
            return Signal
    
        def Connect(self, Receiver: Callable, Channel: Optional[str] = None) -> "Transmission":
            Path = Channel or self.Channel or f"Transmission.{id(self)}"
            ODN.Connect(Path, Receiver)
            return self

        def Disconnect(self, Receiver: Callable, Channel: Optional[str] = None) -> "Transmission":
            Path = Channel or self.Channel or f"Transmission.{id(self)}"
            ODN.Disconnect(Path, Receiver)
            return self

    # ------------------------------------------------------------------
    # Маршрути
    # ------------------------------------------------------------------
    # Зареєструвати маршрут для шляху
    def RegisterRoute(self, Path, *Route):
        self.Routes[Path] = list(Route)
        return self.Routes[Path]

    # Маршрутизувати сигнал відповідно до зареєстрованого шляху
    def Route(self, Signal):
        Signal.Route = self.Routes.get(
            Signal.Channel, []
        )
        return Signal
    # ------------------------------------------------------------------
    # Передача
    # ------------------------------------------------------------------
    # Надіслати дані по вказаному каналу з вибором транспорту
    def Dispatch(self, Path, *Args, Mode="Optical", **Kwargs):
        Signal = self.Channel(Path)
        Signal.Data = Args
        Signal.Flags = Kwargs
        Signal = self.Route(Signal)
        if Mode == "Optical":
            return self.OTN.Transmit(Signal)
        if Mode == "Quantum":
            return self.OTN.Transmit(Signal)
        raise ValueError(f"Unknown transport: {Mode}")

    # Розіслати дані на всі активні канали
    def Broadcast(self, *Args, **Kwargs):
        Signals = []
        for Path in self.Current():
            Signals.append(
                self.Dispatch(
                    Path,
                    *Args,
                    **Kwargs
                )
            )
        return Signals

    # Розіслати дані на вказані канали
    def Multicast(self, Paths, *Args, **Kwargs):
        Signals = []
        for Path in Paths:
            Signals.append(
                self.Dispatch(
                    Path,
                    *Args,
                    **Kwargs
                )
            )
        return Signals

    # Надіслати дані у канал. Аліас Dispatch для матриці та системних вузлів.
    def Send(self, Path, *Args, **Kwargs):
        return self.Dispatch(Path, *Args, **Kwargs)

# Singleton інстанси.
# ODN — синглтон (інстанс), а не клас: весь код викликає ODN.Emit(...),
# ODN.Channel(...).Connect(...) тощо як методи мережі, тому модуль експортує інстанс.
OpticalDataNetwork = ODNClass = ODN
OpticalTransportLine = OTNClass = OTN
ODN = ODNClass()
OTN = OTNClass()
Signal = Transmission

__all__ = ["ODN", "OTN", "Transmission", "Signal", "ODNClass", "OTNClass"]
