from __future__ import annotations

from typing import Any, Dict, Optional, cast

from lcars.base.type import SystemComponent
from lcars.core.signal import ODN
from lcars.engineering.isolinear import IsolinearBank, IsolinearChip


# Трансівер тримає двонапрямний оптичний зв'язок і передає кадри через сокет.
class OpticalTransceiver:
    def __init__(self, NodeId: str, Socket: Optional["OpticalSocket"] = None):
        self.NodeId = NodeId
        self.Socket = Socket
        self.Mode = "BIDIRECTIONAL"
        self.State = "IDLE"
        self.LastFrame: Dict[str, Any] = {}
        self.InputRate = 0
        self.OutputRate = 0

    # Підключаємо сокет до трансівера.
    def Attach(self, Socket: "OpticalSocket") -> None:
        self.Socket = Socket
        self.State = "LINKED"

    # Відключаємо сокет від трансівера.
    def Detach(self) -> None:
        self.Socket = None
        self.State = "IDLE"

    # Передаємо кадр через сокет.
    def Transmit(self, SignalName: str, Payload: Any) -> Dict[str, Any]:
        Frame = {
            "node": self.NodeId,
            "kind": "transceiver",
            "signal": SignalName,
            "payload": Payload,
            "mode": self.Mode,
        }
        self.LastFrame = Frame
        self.OutputRate += 1
        self.State = "ACTIVE"
        if self.Socket is not None:
            self.Socket.Route(f"Optical.{SignalName}", Frame)
        ODN.send("Optical.Transceiver", Frame)
        return Frame

    # Отримуємо кадр від зовнішнього джерела.
    def Receive(self, Frame: Dict[str, Any]) -> Dict[str, Any]:
        self.LastFrame = Frame
        self.InputRate += 1
        self.State = "RECEIVING"
        ODN.send("Optical.Transceiver.Receive", Frame)
        return Frame

    # Повертаємо поточний стан трансівера.
    def GetStatus(self) -> Dict[str, Any]:
        return {
            "NodeId": self.NodeId,
            "Kind": "Transceiver",
            "State": self.State,
            "Mode": self.Mode,
            "HasSocket": self.Socket is not None,
            "InputRate": self.InputRate,
            "OutputRate": self.OutputRate,
            "LastFrame": self.LastFrame,
        }


# Мультиплексор збирає кілька каналів у спільний потік і віддає злитий кадр.
class OpticalMultiplexer:
    def __init__(self, NodeId: str, Socket: Optional["OpticalSocket"] = None):
        self.NodeId = NodeId
        self.Socket = Socket
        self.State = "IDLE"
        self.ActiveChannel: Optional[str] = None
        self.Channels: Dict[str, list[Any]] = {}
        self.LastFrame: Dict[str, Any] = {}

    # Підключаємо сокет до мультиплексора.
    def Attach(self, Socket: "OpticalSocket") -> None:
        self.Socket = Socket
        self.State = "LINKED"

    # Додаємо новий канал до мультиплексора.
    def AddChannel(self, ChannelName: str) -> None:
        if ChannelName not in self.Channels:
            self.Channels[ChannelName] = []

    # Додаємо дані в канал та передаємо кадр.
    def Push(self, ChannelName: str, Payload: Any) -> Dict[str, Any]:
        self.AddChannel(ChannelName)
        self.Channels[ChannelName].append(Payload)
        self.ActiveChannel = ChannelName
        self.State = "MIXING"
        Frame = {
            "node": self.NodeId,
            "kind": "multiplexer",
            "channel": ChannelName,
            "payload": Payload,
            "channels": list(self.Channels.keys()),
        }
        self.LastFrame = Frame
        if self.Socket is not None:
            self.Socket.Route("Optical.Mux", Frame)
        ODN.send("Optical.Multiplexer", Frame)
        return Frame

    # Зливаємо всі канали в один пакет.
    def Merge(self) -> Dict[str, Any]:
        Packets = []
        for ChannelName in self.Channels:
            Packets.extend(self.Channels[ChannelName])
        Frame = {
            "node": self.NodeId,
            "kind": "multiplexer",
            "active": self.ActiveChannel,
            "packets": Packets,
        }
        self.LastFrame = Frame
        self.State = "READY"
        ODN.send("Optical.Multiplexer.Merge", Frame)
        return Frame

    # Повертаємо поточний стан мультиплексора.
    def GetStatus(self) -> Dict[str, Any]:
        return {
            "NodeId": self.NodeId,
            "Kind": "Multiplexer",
            "State": self.State,
            "ActiveChannel": self.ActiveChannel,
            "ChannelCount": len(self.Channels),
            "HasSocket": self.Socket is not None,
            "LastFrame": self.LastFrame,
        }


# Повторювач підсилює або повторює кадр без зміни маршруту.
class OpticalRepeater:
    def __init__(self, NodeId: str, Socket: Optional["OpticalSocket"] = None):
        self.NodeId = NodeId
        self.Socket = Socket
        self.State = "IDLE"
        self.Gain = 1.0
        self.Delay = 0.0
        self.LastFrame: Dict[str, Any] = {}

    # Підключаємо сокет до повторювача.
    def Attach(self, Socket: "OpticalSocket") -> None:
        self.Socket = Socket
        self.State = "LINKED"

    # Повторюємо або підсилюємо кадр.
    def Repeat(self, SignalName: str, Payload: Any) -> Dict[str, Any]:
        Frame = {
            "node": self.NodeId,
            "kind": "repeater",
            "signal": SignalName,
            "payload": Payload,
            "gain": self.Gain,
            "delay": self.Delay,
        }
        self.LastFrame = Frame
        self.State = "REPEATING"
        if self.Socket is not None:
            self.Socket.Route(f"Optical.{SignalName}", Frame)
        ODN.send("Optical.Repeater", Frame)
        return Frame

    # Повертаємо поточний стан повторювача.
    def GetStatus(self) -> Dict[str, Any]:
        return {
            "NodeId": self.NodeId,
            "Kind": "Repeater",
            "State": self.State,
            "Gain": self.Gain,
            "Delay": self.Delay,
            "HasSocket": self.Socket is not None,
            "LastFrame": self.LastFrame,
        }


# Перемикач керує маршрутами між портами оптичної мережі.
class OpticalSwitch:
    def __init__(self, NodeId: str):
        self.NodeId = NodeId
        self.State = "IDLE"
        self.Ports: Dict[str, OpticalSocket] = {}
        self.Routes: Dict[str, str] = {}
        self.ActiveRoute: Optional[tuple[str, str]] = None
        self.LastFrame: Dict[str, Any] = {}

    # Підключаємо сокет до порту перемикача.
    def AttachPort(self, PortName: str, Socket: "OpticalSocket") -> None:
        self.Ports[PortName] = Socket
        self.State = "LINKED"

    # Мапимо маршрут між портами.
    def MapRoute(self, InputPort: str, OutputPort: str) -> None:
        self.Routes[InputPort] = OutputPort

    # Маршрутизуємо кадр через перемикач.
    def Route(self, InputPort: str, SignalName: str, Payload: Any) -> Dict[str, Any]:
        OutputPort = self.Routes.get(InputPort)
        Frame = {
            "node": self.NodeId,
            "kind": "switch",
            "input": InputPort,
            "output": OutputPort,
            "signal": SignalName,
            "payload": Payload,
        }
        self.LastFrame = Frame
        if OutputPort is not None and OutputPort in self.Ports:
            self.Ports[OutputPort].Route(f"Optical.{SignalName}", Frame)
            self.ActiveRoute = (InputPort, OutputPort)
            self.State = "ROUTED"
        else:
            self.ActiveRoute = None
            self.State = "BLOCKED"
        ODN.send("Optical.Switch", Frame)
        return Frame

    # Повертаємо поточний стан перемикача.
    def GetStatus(self) -> Dict[str, Any]:
        return {
            "NodeId": self.NodeId,
            "Kind": "Switch",
            "State": self.State,
            "PortCount": len(self.Ports),
            "RouteCount": len(self.Routes),
            "ActiveRoute": self.ActiveRoute,
            "LastFrame": self.LastFrame,
        }


# Окрема точка підключення для чіпа або вузла оптичної мережі.
class OpticalSocket:
    def __init__(self, SocketId: str, Priority: int = 5):
        self.SocketId = SocketId
        self.Priority = Priority
        self.ConnectedChip: Optional[IsolinearChip] = None
        self.ConnectedChipId: Optional[str] = None
        self.LinkState = "OPEN"
        self.LinkHealth = 100.0
        self.ChannelState = "IDLE"

    # Вставляємо чіп у сокет.
    def Insert(self, Chip: Any) -> bool:
        if isinstance(Chip, IsolinearChip):
            self.ConnectedChip = Chip
            self.ConnectedChipId = Chip.id
            self.LinkState = "BOUND"
            self.ChannelState = "ACTIVE" if getattr(Chip, "Connected", False) else "READY"
            self.LinkHealth = 100.0
            return True

        if isinstance(Chip, str):
            self.ConnectedChip = None
            self.ConnectedChipId = Chip
            self.LinkState = "BOUND"
            self.ChannelState = "READY"
            self.LinkHealth = 100.0
            return True

        return False

    # Виймаємо чіп із сокета.
    def Eject(self) -> None:
        self.ConnectedChip = None
        self.ConnectedChipId = None
        self.LinkState = "OPEN"
        self.ChannelState = "IDLE"
        self.LinkHealth = 100.0

    # Маршрутизуємо сигнал через сокет.
    def Route(self, SignalName: str, Payload: Any) -> Dict[str, Any]:
        Packet = {
            "socket": self.SocketId,
            "chip": self.ConnectedChipId,
            "signal": SignalName,
            "payload": Payload,
            "priority": self.Priority,
        }
        ODN.send("Optical.Route", Packet)
        return Packet

    # Повертаємо поточний стан сокета.
    def GetStatus(self) -> dict[str, Any]:
        return {
            "SocketId": self.SocketId,
            "Priority": self.Priority,
            "ConnectedChipId": self.ConnectedChipId,
            "LinkState": self.LinkState,
            "LinkHealth": self.LinkHealth,
            "ChannelState": self.ChannelState,
        }


# Єдина оптична шина для вузлів, сокетів і маршрутизації сигналів.
class SocketArray(SystemComponent):
    def __init__(self, ArrayId: str = "main"):
        super().__init__()
        self.ArrayId = ArrayId
        self.Sockets: Dict[str, OpticalSocket] = {}
        self.Nodes: Dict[str, Any] = {}
        self.ChipBindings: Dict[str, str] = {}
        self.NetworkState = "OFFLINE"
        self.LastPacket: Dict[str, Any] = {}

    # Додаємо новий сокет до масиву.
    def AddSocket(self, SocketId: str, Priority: int = 5) -> OpticalSocket:
        Socket = OpticalSocket(SocketId, Priority)
        self.Sockets[SocketId] = Socket
        return Socket

    # Повертаємо сокет за ідентифікатором.
    def GetSocket(self, SocketId: str) -> Optional[OpticalSocket]:
        return self.Sockets.get(SocketId)

    # Знаходимо чіп у банку за ідентифікатором.
    def ResolveChip(self, Bank: Any, ChipId: str) -> Any | None:
        Chips = getattr(Bank, "Chips", None)
        if isinstance(Chips, dict):
            return Chips.get(ChipId)
        return None

    # Видаляємо сокет з масиву.
    def RemoveSocket(self, SocketId: str) -> bool:
        if SocketId not in self.Sockets:
            return False

        Socket = self.Sockets[SocketId]
        if Socket.ConnectedChipId is not None and Socket.ConnectedChipId in self.ChipBindings:
            del self.ChipBindings[Socket.ConnectedChipId]

        del self.Sockets[SocketId]
        return True

    # Реєструємо вузол у масиві.
    def RegisterNode(self, NodeId: str, Node: Any) -> Any:
        self.Nodes[NodeId] = Node
        return Node

    # Повертаємо вузол за ідентифікатором.
    def GetNode(self, NodeId: str) -> Any | None:
        return self.Nodes.get(NodeId)

    # Прив'язуємо чіп до сокета.
    def BindChip(self, Bank: IsolinearBank, ChipId: str, SocketId: str) -> bool:
        Socket = self.GetSocket(SocketId)
        if Socket is None:
            return False

        Chip = self.ResolveChip(Bank, ChipId)
        if Chip is None:
            return False

        if not Socket.Insert(Chip):
            return False

        self.ChipBindings[ChipId] = SocketId
        return True

    # Відв'язуємо чіп від сокета.
    def UnbindChip(self, ChipId: str) -> bool:
        SocketId = self.ChipBindings.get(ChipId)
        if SocketId is None:
            return False

        Socket = self.GetSocket(SocketId)
        if Socket is not None:
            Socket.Eject()

        del self.ChipBindings[ChipId]
        return True

    # Синхронізуємо чіпи з банку в масив сокетів.
    def SyncBank(self, Bank: IsolinearBank) -> int:
        Count = 0
        if not hasattr(Bank, "Chips"):
            return 0

        for ChipId in Bank.Chips:
            if ChipId in self.ChipBindings:
                continue
            Socket = self.FindFreeSocket()
            if Socket is None:
                break
            if self.BindChip(Bank, ChipId, Socket.SocketId):
                Count += 1
        return Count

    # Знаходимо вільний сокет з найнижчим пріоритетом.
    def FindFreeSocket(self) -> Optional[OpticalSocket]:
        for Socket in sorted(self.Sockets.values(), key=lambda Item: Item.Priority):
            if Socket.ConnectedChipId is None:
                return Socket
        return None

    # Маршрутизуємо сигнал через масив сокетів.
    def RouteSignal(self, SignalName: str, Payload: Any, SocketId: str | None = None) -> Dict[str, Any]:
        Socket = self.GetSocket(SocketId) if SocketId else self.FindFreeSocket()
        if Socket is None:
            Packet: Dict[str, Any] = {
                "array": self.ArrayId,
                "state": "NO_SOCKET",
                "signal": SignalName,
                "payload": Payload,
            }
            self.LastPacket = Packet
            return Packet

        Packet = Socket.Route(SignalName, Payload)
        Packet["array"] = self.ArrayId
        self.LastPacket = Packet
        self.NetworkState = "ONLINE"
        return Packet

    # Маршрутизуємо сигнал до вузла за ідентифікатором.
    def RouteNode(self, NodeId: str, SignalName: str, Payload: Any) -> Dict[str, Any]:
        Node = self.GetNode(NodeId)
        if Node is None:
            Packet: Dict[str, Any] = {
                "array": self.ArrayId,
                "state": "NO_NODE",
                "node": NodeId,
                "signal": SignalName,
                "payload": Payload,
            }
            self.LastPacket = Packet
            return Packet

        Transmit = getattr(Node, "Transmit", None)
        if callable(Transmit):
            Packet = cast(Dict[str, Any], Transmit(SignalName, Payload))
            self.LastPacket = Packet
            self.NetworkState = "ONLINE"
            return Packet

        Repeat = getattr(Node, "Repeat", None)
        if callable(Repeat):
            Packet = cast(Dict[str, Any], Repeat(SignalName, Payload))
            self.LastPacket = Packet
            self.NetworkState = "ONLINE"
            return Packet

        Push = getattr(Node, "Push", None)
        if callable(Push):
            Packet = cast(Dict[str, Any], Push(SignalName, Payload))
            self.LastPacket = Packet
            self.NetworkState = "ONLINE"
            return Packet

        Route = getattr(Node, "Route", None)
        if callable(Route):
            Packet = cast(Dict[str, Any], Route(SignalName, Payload))
            self.LastPacket = Packet
            self.NetworkState = "ONLINE"
            return Packet

        Packet: Dict[str, Any] = {
            "array": self.ArrayId,
            "state": "UNSUPPORTED_NODE",
            "node": NodeId,
            "signal": SignalName,
            "payload": Payload,
        }
        self.LastPacket = Packet
        return Packet

    # Повертаємо повний стан масиву.
    def GetStatus(self) -> dict[str, Any]:
        return {
            "ArrayId": self.ArrayId,
            "NetworkState": self.NetworkState,
            "SocketCount": len(self.Sockets),
            "NodeCount": len(self.Nodes),
            "BoundCount": len(self.ChipBindings),
            "Sockets": {SocketId: Socket.GetStatus() for SocketId, Socket in self.Sockets.items()},
            "Nodes": {NodeId: Node.GetStatus() if hasattr(Node, "GetStatus") else str(Node) for NodeId, Node in self.Nodes.items()},
            "ChipBindings": dict(self.ChipBindings),
            "LastPacket": self.LastPacket,
        }


IsolinearSocket = OpticalSocket
SocketArrayInstance = SocketArray("main")


# Повертаємо екземпляр масиву сокетів.
def GetSocketArray(ArrayId: str = "main") -> SocketArray:
    if ArrayId == "main":
        return SocketArrayInstance
    return SocketArray(ArrayId)


# Ініціалізуємо оптичну мережу з базовими сокетами та вузлами.
def InitializeOpticalNetwork() -> SocketArray:
    Array = GetSocketArray("main")
    if not Array.Sockets:
        Array.AddSocket("core.alpha", 1)
        Array.AddSocket("core.beta", 1)
        Array.AddSocket("agent.primary", 3)
        Array.AddSocket("storage.main", 5)
        Array.AddSocket("backup.aux", 7)
        Array.AddSocket("detector.geant4", 9)
        Array.AddSocket("nova.ide", 9)
        Array.AddSocket("theme.dynamic", 10)

    if not Array.Nodes:
        Transceiver = Array.RegisterNode("core.transceiver", OpticalTransceiver("core.transceiver"))
        Multiplexer = Array.RegisterNode("core.multiplexer", OpticalMultiplexer("core.multiplexer"))
        Repeater = Array.RegisterNode("core.repeater", OpticalRepeater("core.repeater"))
        Switch = Array.RegisterNode("core.switch", OpticalSwitch("core.switch"))

        SocketAlpha = Array.GetSocket("core.alpha")
        SocketBeta = Array.GetSocket("core.beta")
        AgentSocket = Array.GetSocket("agent.primary")
        BackupSocket = Array.GetSocket("backup.aux")

        if SocketAlpha is not None:
            Transceiver.Attach(SocketAlpha)
            Switch.AttachPort("input.core", SocketAlpha)
        if SocketBeta is not None:
            Switch.AttachPort("output.core", SocketBeta)
        if AgentSocket is not None:
            Multiplexer.Attach(AgentSocket)
        if BackupSocket is not None:
            Repeater.Attach(BackupSocket)

        Switch.MapRoute("input.core", "output.core")
        Array.RegisterNode("agent.multiplexer", Multiplexer)
        Array.RegisterNode("backup.repeater", Repeater)
        Array.RegisterNode("core.router", Switch)
    return Array


__all__ = [
    "OpticalTransceiver",
    "OpticalMultiplexer",
    "OpticalRepeater",
    "OpticalSwitch",
    "OpticalSocket",
    "SocketArray",
    "IsolinearSocket",
    "SocketArrayInstance",
    "GetSocketArray",
    "InitializeOpticalNetwork",
]
