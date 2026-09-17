# =============================================================================
# ФУНДАМЕНТАЛЬНА КВАНТОВО-ОПТИЧНА СИГНАЛЬНА ТА ТРАНСПОРТНА АРХІТЕКТУРА ЗОРЕЛЬОТА
# =============================================================================
# ОПИС: Єдина мережа сигналів, протоколів і директив для бортового комп'ютера.
# ПРИЗНАЧЕННЯ МОДУЛЯ:
#   1. Transmission (Клієнтський сигнал / Фотонний потік):
#      Одиниця передачі даних, директив чи подій у системі LCARS. Є фотонним
#      променем (Payload), що курсує оптичними хвилеводами зв'язку.
#
#   2. OpticalTransportLine (OTN — Фізична транспортна лінія):
#      Фізичний транспортний рушій зорельота. Проводить світловий промінь
#      через хвилеводи, підсилювачі та забезпечує детекцію сенсорами (Zero-Except).
#
#   3. ODN (Optical Data Network — Єдина оптична мережа зорельота):
#      Глобальна матриця комутації та топології каналів зорельота. Керує
#      кондуїтами (Conduits), підключенням терміналів (Connect/Disconnect)
#      та маршрутизацією широкомовних (Broadcast) і адресних передач.
# =============================================================================
from typing import Any, Callable, List, Dict, Optional
from lcars.base.info import Version, Passport
from lcars.base.type import SystemComponent, LCARS
# =============================================================================
# 1. TRANSMISSION — ПОТІК ПЕРЕДАЧІ ДАНИХ ТА СИГНАЛІВ LCARS
# Фізичний промінь у кондуїті ODN: класичний лазерний або квантовий режим.
# =============================================================================
class Transmission(SystemComponent):
    TypeName = "LCARSTransmission"
    Type = "Transmission"

    # Системний режим роботи комп'ютера зорельота
    Mode: str = "Optical"               # "Optical" (ізолінійний лазерний режим) або "Quantum" (квантовий режим)
    Wavelength: float = 1550.0          # Довжина хвилі (нм) / спектральний канал
    Intensity: float = 1.0              # Інтенсивність світлового потоку (0.0 - 1.0)
    Coherence: float = 1.0              # Квантова когерентність
    EntangledWith: Optional[str] = None # Адреса парного заплутаного вузла

    # Топологія та адресація в кондуїтах
    Channel: Optional[str] = None       # Оптичний кондуїт / хвилевід
    Source: str = "System"              # Джерело випромінювання (лазер / емітер)
    Target: Optional[str] = None        # Вузол детекції (фотоелемент / сенсор)
    Route: List[str] = []               # Оптичні реле та призми проходження (Hops)

    # Фотонне навантаження (хвиля / сигнал / дані)
    Photons: Any = None                 # Самі фотони (Payload / директива / значення)
    Data: Any = None                    # Канонічний аліас до Photons
    Response: Any = None                # Зворотний стан або результат вимірювання
    Flags: Dict[str, Any] = {}          # Модуляційні прапорці
    State: str = "Idle"                 # Стан: Idle, Streaming, Detected, Collapsed, Absorbed, Cancelled, Failed
    Timestamp: float = 0.0              # Зоряний час пуску променя

    # Завантаження та модуляція фотонного потоку в потрібному системному режимі
    def Modulate(self, Photons: Any = None, Mode: str = "Optical", Source: Optional[str] = None, Target: Optional[str] = None, Wavelength: float = 1550.0, **Flags) -> "Transmission":
        self.Photons = Photons
        self.Data = Photons
        self.Mode = "Quantum" if (Mode).capitalize().startswith("Quant") else "Optical"
        self.Wavelength = float(Wavelength)
        self.Intensity = 1.0
        self.Coherence = 1.0
        if Source:
            self.Source = Source
        if Target:
            self.Target = Target
        if Flags:
            self.Flags = dict(Flags)
        self.State = "Idle"
        return self

    Load = Modulate

    # Проходження через оптичне реле
    def Relay(self, Node: str) -> "Transmission":
        self.Route.append(Node)
        return self

    Hop = Relay

    # Заплутування квантового потоку з іншим вузлом
    def Entangle(self, Node: str) -> "Transmission":
        self.Mode = "Quantum"
        self.EntangledWith = Node
        return self

    # Детекція фотонного потоку сенсором / приймачем залежно від режиму системи
    def Detect(self, Sensor: Callable) -> Any:
        Cargo = self.Photons if self.Photons is not None else self.Data
        if self.Mode == "Quantum":
            self.State = "Collapsed"
            self.Coherence = 0.0
        else:
            self.State = "Detected"

        Result = Sensor(Cargo)
        if Result is not None:
            self.Response = Result
        return Result

    Deliver = Detect

    # Згасання або поглинання променя
    def Absorb(self, Reason: Any = None) -> "Transmission":
        self.Intensity = 0.0
        self.Response = Reason
        self.State = "Absorbed"
        return self

    # Фіксація успішної доставки / детекції
    def Complete(self, ResponseData: Any = None) -> "Transmission":
        if ResponseData is not None:
            self.Response = ResponseData
        self.State = "Detected" if self.Mode == "Optical" else "Collapsed"
        return self

    # Скасування передачі
    def Cancel(self) -> "Transmission":
        self.State = "Cancelled"
        return self

    Cancelled = Cancel

    # Фіксація збою під час передачі
    def Fail(self, Reason: Any = None) -> "Transmission":
        self.Response = Reason
        self.State = "Failed"
        return self

    # Отримання детектованого значення
    def Value(self) -> Any:
        return self.Response if self.Response is not None else (self.Photons if self.Photons is not None else self.Data)

    Result = Value

    # Перевірки фізичного стану
    def IsDetected(self) -> bool:
        return self.State in ("Detected", "Collapsed")

    def IsAbsorbed(self) -> bool:
        return self.State == "Absorbed" or self.Intensity <= 0.0

    def IsStreaming(self) -> bool:
        return self.State in ("Idle", "Streaming")

    # Підключення приймача до кондуїту цього сигналу через ODN
    def Connect(self, Callback: Callable) -> "Transmission":
        if self.Channel:
            ODN.Connect(self.Channel, Callback)
        return self

    # Відключення приймача від кондуїту
    def Disconnect(self, Callback: Callable) -> "Transmission":
        if self.Channel:
            ODN.Disconnect(self.Channel, Callback)
        return self


# =============================================================================
# 2. OPTICAL TRANSPORT LINE (OTN) — ФІЗИЧНА ОПТИЧНА ТРАНСПОРТНА ЛІНІЯ
# =============================================================================
class OpticalTransportLine(SystemComponent):
    TypeName = "LCARSOpticalTransportLine"
    Type = "OTN"
    Version = Version.Release

    DefaultWavelength: float = 1550.0   # Робоча довжина хвилі лазерів (нм)
    AttenuationPerHop: float = 0.05     # Втрата інтенсивності променя на вузол (5%)
    ActiveBeams: int = 0                # Кількість активних променів у магістралі
    MultiplexedChannels: Dict[float, List[Transmission]] = {}

    # Оптичне підсилення та регенерація імпульсу (повторювач)
    def Amplify(self, Beam: Transmission) -> Transmission:
        Beam.Intensity = 1.0
        if Beam.Mode == "Quantum":
            Beam.Coherence = 1.0
        return Beam

    # Мультиплексування (WDM)
    def Multiplex(self, Beam: Transmission) -> Transmission:
        LambdaKey = round(Beam.Wavelength, 1)
        if not self.MultiplexedChannels:
            self.MultiplexedChannels = {}
        if LambdaKey not in self.MultiplexedChannels:
            self.MultiplexedChannels[LambdaKey] = []
        self.MultiplexedChannels[LambdaKey].append(Beam)
        return Beam

    # Демультиплексування
    def Demultiplex(self, Wavelength: float) -> List[Transmission]:
        LambdaKey = round(Wavelength, 1)
        if not self.MultiplexedChannels:
            return []
        return self.MultiplexedChannels.pop(LambdaKey, [])

    # Перемикання на резервний оптичний контур
    def ProtectionSwitch(self, Beam: Transmission, AlternateConduit: str) -> Transmission:
        Beam.Relay(f"Bypass.{AlternateConduit}")
        return self.Amplify(Beam)

    # Повне фізичне транспортування фотонного променя по лінії
    def Transport(self, Beam: Transmission, Sensors: Optional[List[Callable]] = None) -> Transmission:
        self.ActiveBeams += 1
        Beam.State = "Streaming"

        # Врахування згасання світла по довжині маршруту
        HopsCount = len(Beam.Route)
        Beam.Intensity = max(0.0, Beam.Intensity - (HopsCount * self.AttenuationPerHop))

        if Beam.Intensity <= 0.0:
            Beam.Absorb("SIGNAL_ATTENUATED")
            self.ActiveBeams = max(0, self.ActiveBeams - 1)
            return Beam

        TargetSensors = list(Sensors or [])
        LastDetection = None

        if Beam.Mode == "Quantum":
            for Sensor in TargetSensors:
                if not callable(Sensor):
                    continue
                LastDetection = Beam.Detect(Sensor)
                break
        else:
            for Sensor in TargetSensors:
                if not callable(Sensor):
                    continue
                Detection = Beam.Detect(Sensor)
                if Detection is not None:
                    LastDetection = Detection

        if LastDetection is not None:
            Beam.Response = LastDetection

        self.ActiveBeams = max(0, self.ActiveBeams - 1)
        return Beam


# =============================================================================
# 3. OPTICAL DATA NETWORK (ODN) — ЦЕНТРАЛЬНА МАТРИЦЯ КОМУТАЦІЇ ТА ТОПОЛОГІЇ
# =============================================================================
class OpticalDataNetwork(SystemComponent):
    TypeName = "LCARSOpticalDataNetwork"
    Type = "ODN"
    Version = Version.Release

    Conduits: Dict[str, Transmission] = {}      # Реєстр оптичних кондуїтів (каналів)
    Receivers: Dict[str, List[Callable]] = {}   # Комутаційні списки підключених сенсорів/терміналів
    Routes: Dict[str, List[str]] = {}           # Маршрутні таблиці проходження через палуби (Hops)
    TransportEngine: Optional[OpticalTransportLine] = None

    def EnsureTransport(self) -> OpticalTransportLine:
        if self.TransportEngine is None:
            self.TransportEngine = OpticalTransportLine()
        return self.TransportEngine

    def Channel(self, ConduitPath: str) -> Transmission:
        Stream = self.Conduits.get(ConduitPath)
        if Stream is None:
            Stream = Transmission()
            Stream.Channel = ConduitPath
            Stream.State = "Online"
            self.Conduits[ConduitPath] = Stream
        return Stream

    def Exists(self, ConduitPath: str) -> bool:
        return ConduitPath in self.Conduits

    def Online(self, ConduitPath: str) -> Transmission:
        Stream = self.Channel(ConduitPath)
        Stream.State = "Online"
        return Stream

    def Offline(self, ConduitPath: str) -> Transmission:
        Stream = self.Channel(ConduitPath)
        Stream.State = "Offline"
        return Stream

    def StatusChannel(self, ConduitPath: str) -> str:
        return self.Channel(ConduitPath).State

    def Connect(self, ConduitPath: str, Callback: Callable) -> None:
        if ConduitPath not in self.Receivers:
            self.Receivers[ConduitPath] = []
        if callable(Callback) and Callback not in self.Receivers[ConduitPath]:
            self.Receivers[ConduitPath].append(Callback)

    Listen = Connect
    Subscribe = Connect

    def Disconnect(self, ConduitPath: str, Callback: Callable) -> None:
        if ConduitPath in self.Receivers and Callback in self.Receivers[ConduitPath]:
            self.Receivers[ConduitPath].remove(Callback)

    Mute = Disconnect
    Unsubscribe = Disconnect

    def RegisterRoute(self, ConduitPath: str, *HopNodes: str) -> List[str]:
        self.Routes[ConduitPath] = list(HopNodes)
        return self.Routes[ConduitPath]

    def Route(self, Beam: Transmission) -> Transmission:
        if Beam.Channel and Beam.Channel in self.Routes:
            Beam.Route = list(self.Routes[Beam.Channel])
        return Beam

    def Transmit(self, ConduitPath: str, Data: Any = None, Source: Optional[str] = None, Target: Optional[str] = None, Mode: str = "Optical", **Flags) -> Transmission:
        Beam = self.Channel(ConduitPath)
        Beam.Modulate(Photons=Data, Mode=Mode, Source=Source, Target=Target, **Flags)

        TimeSubsystem = getattr(LCARS.System, "Time", None)
        Beam.Timestamp = TimeSubsystem.time() if TimeSubsystem and hasattr(TimeSubsystem, "time") else 0.0

        Beam = self.Route(Beam)

        Engine = self.EnsureTransport()
        Sensors = self.Receivers.get(ConduitPath, [])
        return Engine.Transport(Beam, Sensors)

    Send = Transmit
    Dispatch = Transmit

    def Broadcast(self, *Args, **Flags) -> List[Transmission]:
        Results = []
        for Path in list(self.Conduits.keys()):
            Results.append(self.Transmit(Path, Data=Args, **Flags))
        return Results

    def Multicast(self, ConduitsList: List[str], *Args, **Flags) -> List[Transmission]:
        Results = []
        for Path in ConduitsList:
            Results.append(self.Transmit(Path, Data=Args, **Flags))
        return Results

    def Purge(self, ConduitPath: str) -> None:
        if ConduitPath in self.Receivers:
            del self.Receivers[ConduitPath]
        if ConduitPath in self.Conduits:
            self.Conduits[ConduitPath].Absorb("PURGED")
            del self.Conduits[ConduitPath]

    def Shutdown(self) -> None:
        self.Conduits.clear()
        self.Receivers.clear()
        self.Routes.clear()


# =============================================================================
# 4. КАНОНІЧНІ СИНГЛТОНИ ТА АЛІАСИ ЗОРЕЛЬОТА
# =============================================================================
# Будь-який сигнал у зорельоті LCARS — це фотонний потік Transmission
Signal = Transmission
OpticalTransportNetwork = OpticalTransportLine

# Класи (для типізації)
ODNClass = OpticalDataNetwork
OTNClass = OpticalTransportLine

# Глобальні робочі інстанси-синглтони зорельота
OTN: OpticalTransportLine = OpticalTransportLine()
ODN: OpticalDataNetwork = OpticalDataNetwork()

LCARS.All = ["ODN", "OTN", "Transmission", "Signal"]
