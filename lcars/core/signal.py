# LCARS Optical Data Network (ODN) — ізолінійна мережа
# ОПИС: Єдина мережа сигналів, протоколів і директив для бортового комп'ютера.
# ─────────────────────────────────────────────────────────────────────────────
from typing import Any
from lcars.base.version import getVersion
from lcars.base.type import Directive, SystemComponent

# Transmission — безперервний потік даних, сигналів, директив
class Transmission(Directive):
    def __init__(self, *Types, Id=None):
        super().__init__(Id)
        self.Id = Id
        self.TypeArgs = Types
        # службова інформація
        self.Protocol = None
        self.Timestamp = None
        self.State = "Idle"
        # маршрут
        self.Source = None
        self.Target = None
        self.Route = None
        # дані
        self.Data: Any
        self.Flags = {}
        # ідентифікація
        self.Channel = None
        # пріоритет
        self.Priority = 0
        # походження
        self.Owner = None
        # результат виконання
        self.Result = None
        # помилка
        self.Error = None

    # Позначити виконання як завершене
    def Complete(self):
        self.State = "Completed"
        return self

    # Скасувати виконання
    def Cancel(self):
        self.State = "Cancelled"
        return self

    # Випустити результат у цей сигнал. Встановлює дані та завершений стан.
    def Emit(self, Data=None, **Kwargs):
        self.Data = Data if Data is not None else Kwargs
        self.State = "Completed"
        for Callback in getattr(self, "_listeners", []):
            Callback(self)
        return self

    # Підключити зворотний виклик до сигналу
    def Connect(self, Callback):
        if not hasattr(self, "_listeners"):
            self._listeners = []
        self._listeners.append(Callback)
        return self

# Optical Transport Line — статичний транспортний канал
class OTN(SystemComponent):
    # Ініціалізувати оптичний транспортний вузол
    def __init__(self):
        super().__init__(Id="OTN")
        self.Version = getVersion()
        self.State = "Online"

    # Передати сигнал через оптичну лінію
    def Transmit(self, Signal):
        Signal.Protocol = "Optical"
        return Signal

# Optical Data Network -- Ізолінійна мережа LCARS
# Призначення:
#   - єдина мережа передачі;
#   - логічні канали;
#   - маршрутизація сигналів;
#   - резолюція каналів.
class ODN(SystemComponent):
    # Ініціалізувати мережу Optical Data Network
    def __init__(self):
        super().__init__(Id="ODN")
        self.Version = getVersion()
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
        # Протоколи
        self.Protocols = {}
        # Маршрути
        self.Routes = {}
        from lcars.engineering.isolinear import BlackBox
        self.BlackBox = BlackBox()
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

# Observer — спрощений сигнал для зворотного виклику підписників.
# Використовується в Firmware та WarpDrive для сповіщення про зміни стану.
class Observer:
    # Конструктор: приймає типи аргументів (необов'язково)
    def __init__(self, *ArgTypes):
        self.ArgTypes = ArgTypes
        self.Subscribers = []

    # Підписати функцію на отримання сповіщень
    def Subscribe(self, Callback):
        self.Subscribers.append(Callback)

    # Відправити дані всім підписникам
    def Update(self, *Args):
        for Callback in self.Subscribers:
            Callback(*Args)

# Singleton інстанси.
# ODN — синглтон (інстанс), а не клас: весь код викликає ODN.Emit(...),
# ODN.Channel(...).Connect(...) тощо як методи мережі, тому модуль експортує інстанс.
ODNInstance = ODN()
ODN = ODNInstance
OpticalDataNetwork = ODN
OpticalTransportLine = OTN
Signal = Transmission

__all__ = ["ODN", "OTN", "Transmission", "Signal", "Observer"]
