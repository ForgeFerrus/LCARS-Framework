# ◤ LCARS OPTICAL DATA NETWORK & TRANSPORT ARCHITECTURE 🖖
# Фундаментальна квантово-оптична топологія та транспортна магістраль зорельота.
# СТАНДАРТ: Titanium (Zero-Except, Zero-Underscores, Strict PascalCase, Pure LCARS Base).
# ---------------------------------------------------------------------------------------
# Titanium Bridge Migration: 
from typing import Any, Callable, List, Dict, Optional
from lcars.base.info import Version, Passport
from lcars.base.type import Directive, SystemComponent, LCARS

# Квантово-оптичний потік передачі даних LCARS (Двосторонній імпульс / Пакет)
class Transmission(Directive):
    def __init__(self, *Types, Id: Optional[str] = None):
        ActualId = Id
        if ActualId is None and len(Types) == 1 and isinstance(Types[0], str):
            ActualId = Types[0]
        super().__init__(ActualId)
        self.Id = ActualId
        self.Channel: Optional[str] = ActualId
        self.TypeArgs = Types
        self.Protocol = "Optical"
        self.State = "Idle"
        self.Source = "System"
        self.Target = None
        self.Route = []
        self.Data: Any = None
        self.Response: Any = None
        self.Flags: Dict[str, Any] = {}
        self.Priority = 0
        self.Timestamp = 0.0

    def Complete(self) -> Transmission:
        self.State = "Completed"
        return self

    def Cancel(self) -> Transmission:
        self.State = "Cancelled"
        return self

    def Emit(self, *Args, **Flags) -> Any:
        Path = self.Channel or f"Transmission.{id(self)}"
        return ODN.Transmit(Path, Data=Args[0] if len(Args) == 1 else (Args if Args else None), **Flags)

    def Connect(self, Receiver: Callable) -> Transmission:
        Path = self.Channel or f"Transmission.{id(self)}"
        ODN.Connect(Path, Receiver)
        return self

    def Disconnect(self, Receiver: Callable) -> Transmission:
        Path = self.Channel or f"Transmission.{id(self)}"
        ODN.Disconnect(Path, Receiver)
        return self

# Optical Transport Network (OTN) — Фізичний транспортний рушій перенесення імпульсів
class OpticalTransportNetwork(SystemComponent):
    def __init__(self):
        super().__init__(SystemId="OTN")
        self.Version = Version.Release
        self.Mode = "Optical"

    def SetMode(self, ModeName: str) -> OpticalTransportNetwork:
        self.Mode = "Quantum" if str(ModeName).lower() == "quantum" else "Optical"
        return self

    def OpticalMode(self) -> OpticalTransportNetwork:
        return self.SetMode("Optical")

    def QuantumMode(self) -> OpticalTransportNetwork:
        return self.SetMode("Quantum")

    # Фізичне перенесення та двостороння доставка (Команда -> Відповідь) без затримок (Zero-Except)
    def Transport(self, Packet: Transmission, Receivers: List[Callable]) -> Transmission:
        Packet.Protocol = self.Mode
        Packet.State = "Completed"

        for Receiver in list(Receivers):
            if not callable(Receiver):
                continue

            # Чисте розгалудження за сигнатурою виклику без try/except
            CodeObj = getattr(Receiver, "__code__", None)
            ClosureFunc = getattr(Receiver, "__wrapped__", None)
            if CodeObj is None and ClosureFunc and hasattr(ClosureFunc, "__code__"):
                CodeObj = ClosureFunc.__code__

            ArgCount = getattr(CodeObj, "co_argcount", 1) if CodeObj else 1
            HasVarArgs = bool(getattr(CodeObj, "co_flags", 0) & 0x04) if CodeObj else False

            # Bound method: co_argcount включає self → відніміємо 1 щоб отримати кількість реальних аргументів
            if hasattr(Receiver, "__self__"):
                ArgCount = max(0, ArgCount - 1)

            if ArgCount > 0 or HasVarArgs:
                Result = Receiver(Packet)
            else:
                Result = Receiver()

            if Result is not None:
                Packet.Response = Result

        return Packet

# Optical Data Network (ODN) — Матриця топології, кондуїтів та маршрутизації зорельота
class OpticalDataNetwork(SystemComponent):
    def __init__(self):
        super().__init__(SystemId="ODN")
        self.Version = Version.Release
        self.Transport = OpticalTransportNetwork()
        self.Receivers: Dict[str, List[Callable]] = {}
        self.Channels: Dict[str, Transmission] = {}
        self.Routes: Dict[str, List[Any]] = {}
        self.BlackBox = None

    def Channel(self, Path: str) -> Transmission:
        Stream = self.Channels.get(Path)
        if Stream is None:
            Stream = Transmission(Id=Path)
            Stream.State = "Online"
            self.Channels[Path] = Stream

            if self.BlackBox is None:
                from lcars.engineering.isolinear import BlackBox
                self.BlackBox = BlackBox()

            if self.BlackBox is not None and hasattr(self.BlackBox, "RegisterChannel"):
                self.BlackBox.RegisterChannel(Path)
        return Stream

    def Exists(self, Path: str) -> bool:
        return Path in self.Channels

    # Комутація приймача (термінала/вузла) до каналу шини
    def Connect(self, Path: str, Receiver: Callable) -> None:
        if Path not in self.Receivers:
            self.Receivers[Path] = []
        if callable(Receiver) and Receiver not in self.Receivers[Path]:
            self.Receivers[Path].append(Receiver)

    # Відключення приймача від каналу шини
    def Disconnect(self, Path: str, Receiver: Callable) -> None:
        if Path in self.Receivers and Receiver in self.Receivers[Path]:
            self.Receivers[Path].remove(Receiver)

    # Миттєва двостороння передача імпульсу у канал (Команда -> Відповідь)
    def Transmit(self, Path: str, Data: Any = None, Source: Optional[str] = None, Target: Optional[str] = None, **Flags) -> Transmission:
        Packet = self.Channel(Path)
        Packet.Data = Data
        Packet.Response = None
        Packet.Flags = dict(Flags)
        TimeSubsystem = LCARS.System.Time
        Packet.Timestamp = TimeSubsystem.time() if hasattr(TimeSubsystem, "time") else 0.0
        if Source:
            Packet.Source = Source
        if Target:
            Packet.Target = Target

        ChannelReceivers = self.Receivers.get(Path, [])
        return self.Transport.Transport(Packet, ChannelReceivers)

    def RegisterRoute(self, Path: str, *RouteSteps) -> List[Any]:
        self.Routes[Path] = list(RouteSteps)
        return self.Routes[Path]

    def Route(self, SignalObj: Transmission) -> Transmission:
        SignalObj.Route = self.Routes.get(SignalObj.Channel, [])
        return SignalObj

    def Dispatch(self, Path: str, *Args, Mode: str = "Optical", **Flags) -> Transmission:
        self.Transport.SetMode(Mode)
        return self.Transmit(Path, Data=Args, **Flags)

    def Broadcast(self, *Args, **Flags) -> List[Transmission]:
        Results = []
        for ConduitPath in list(self.Channels.keys()):
            Results.append(self.Transmit(ConduitPath, Data=Args, **Flags))
        return Results

    def Multicast(self, Paths: List[str], *Args, **Flags) -> List[Transmission]:
        Results = []
        for ConduitPath in Paths:
            Results.append(self.Transmit(ConduitPath, Data=Args, **Flags))
        return Results

    def Purge(self, Path: str) -> None:
        if Path in self.Receivers:
            del self.Receivers[Path]
        if Path in self.Channels:
            self.Channels[Path].Cancel()
            del self.Channels[Path]

    # Системні аліаси відправки
    Emit = Transmit
    emit = Transmit
    Listen = Connect
    listen = Connect

# Канонічні інстанси та аліаси зорельота
Signal = Transmission
OTN = OpticalTransportNetwork()
ODN = OpticalDataNetwork()

__all__ = [
    "Signal",
    "Transmission",
    "OpticalTransportNetwork",
    "OpticalDataNetwork",
    "OTN",
    "ODN",
]

