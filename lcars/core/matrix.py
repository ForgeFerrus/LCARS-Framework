# LCARS FRAMEWORK
# System Matrix
# Ядро просторового стану системи.
#
# Matrix є системним компонентом:
# - зберігає вузли;
# - тримає домени;
# - має локальні зв'язки між вузлами;
# - зберігає квантовий опис вузла;
# - інтегрується з Registry, ODN і Nexus;
# - не є транспортом і не створює канали.
from __future__ import annotations

import math
import re
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

from lcars.base.type import SystemComponent
from lcars.base.version import getVersion


# Квантовий стан вузла матриці.
@dataclass
class QuantumState:
    Amplitude: complex = 1 + 0j
    Phase: float = 0.0
    Probability: float = 1.0
    Measured: bool = False
    Entangled: List[Tuple[int, int, int]] = field(default_factory=list)


# Вузол системної матриці з координатами та станом.
@dataclass
class MatrixNode:
    X: int
    Y: int
    Z: int
    Value: Any = None
    State: str = "idle"
    Type: str = "Generic"
    Metadata: Dict[str, Any] = field(default_factory=dict)
    Links: List[Tuple[int, int, int]] = field(default_factory=list)
    Quantum: QuantumState = field(default_factory=QuantumState)


# Системна матриця є компонентом ядра, а не транспортом або симулятором.
class SystemMatrix(SystemComponent):
    # Ініціалізація матриці з розмірностями та залежностями.
    def __init__(
        self,
        Dimensions: Optional[List[int]] = None,
        Id: Optional[str] = None,
        Registry=None,
        ODN=None,
        Nexus=None,
        Parent=None,
    ):
        super().__init__(Id=Id or f"Matrix-{id(self)}")
        self.Parent = Parent
        self.Version = getVersion()
        self.Role = "Core.Matrix"
        self.Registry = Registry
        self.ODN = ODN
        self.Nexus = Nexus
        self.Dimensions = self.NormalizeDimensions(Dimensions or [100, 100, 100])
        self.Nodes: Dict[Tuple[int, int, int], MatrixNode] = {}
        self.Domains: Dict[str, "SystemMatrix"] = {}
        self.Metadata: Dict[str, Any] = {}
        self.Lock = threading.RLock()
        self.Status = "Running"

    # Нормалізація розмірностей до трьох додатних цілих чисел.
    @staticmethod
    def NormalizeDimensions(Dimensions: Iterable[int]) -> List[int]:
        Values = list(Dimensions)[:3]
        while len(Values) < 3:
            Values.append(1)
        return [max(1, int(Value)) for Value in Values]

    # Перетворення ключа на кортеж координат.
    @staticmethod
    def PositionFromKey(Key: Any) -> Optional[Tuple[int, int, int]]:
        if isinstance(Key, (tuple, list)) and len(Key) == 3:
            Values = tuple(Key)
            if all(isinstance(Value, int) for Value in Values):
                return Values  # type: ignore[return-value]
            return None
        if not isinstance(Key, str):
            return None
        Match = re.fullmatch(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", Key)
        if Match is None:
            return None
        return tuple(int(Value) for Value in Match.groups())  # type: ignore[return-value]

    # Забезпечення існування вузла за координатами.
    def EnsureNode(self, X: int, Y: int, Z: int) -> MatrixNode:
        Node = self.Nodes.get((X, Y, Z))
        if Node is None:
            Node = MatrixNode(X=X, Y=Y, Z=Z)
            self.Nodes[(X, Y, Z)] = Node
        return Node

    # Додавання вузла за ключем-координатою.
    def AddNode(
        self,
        Name: Any,
        Node: MatrixNode,
    ) -> MatrixNode:
        Position = self.PositionFromKey(Name)
        if Position is None:
            raise ValueError("Matrix node key must be a coordinate tuple or string.")
        with self.Lock:
            self.Nodes[Position] = Node
        return Node

    # Створення або заміна вузла за координатами.
    def SetNode(
        self,
        X: int,
        Y: int,
        Z: int,
        Value: Any = None,
        Type: str = "Generic",
        State: str = "active",
        Metadata: Optional[Dict[str, Any]] = None,
    ) -> MatrixNode:
        Node = MatrixNode(
            X=X,
            Y=Y,
            Z=Z,
            Value=Value,
            Type=Type,
            State=State,
            Metadata=dict(Metadata or {}),
        )
        with self.Lock:
            self.Nodes[(X, Y, Z)] = Node
        return Node

    # Отримання вузла за координатами.
    def GetNode(self, X: int, Y: int, Z: int) -> Optional[MatrixNode]:
        with self.Lock:
            return self.Nodes.get((X, Y, Z))

    # Видалення вузла за координатами.
    def RemoveNode(self, X: int, Y: int, Z: int) -> bool:
        with self.Lock:
            return self.Nodes.pop((X, Y, Z), None) is not None

    # Перевірка існування вузла за координатами.
    def HasNode(self, X: int, Y: int, Z: int) -> bool:
        with self.Lock:
            return (X, Y, Z) in self.Nodes

    # Зчитування значення вузла за координатами.
    def Read(self, X: int, Y: int, Z: int) -> Any:
        Node = self.GetNode(X, Y, Z)
        return None if Node is None else Node.Value

    # Запис значення у вузол за координатами.
    def Write(self, X: int, Y: int, Z: int, Value: Any) -> bool:
        with self.Lock:
            Node = self.EnsureNode(X, Y, Z)
            Node.Value = Value
        return True

    # Зв'язування двох вузлів.
    def LinkNodes(self, Source: Tuple[int, int, int], Target: Tuple[int, int, int]) -> bool:
        with self.Lock:
            Node = self.Nodes.get(Source)
            if Node is None:
                return False
            if Target not in Node.Links:
                Node.Links.append(Target)
            return True

    # Від'язування двох вузлів.
    def UnlinkNodes(self, Source: Tuple[int, int, int], Target: Tuple[int, int, int]) -> bool:
        with self.Lock:
            Node = self.Nodes.get(Source)
            if Node is None or Target not in Node.Links:
                return False
            Node.Links.remove(Target)
            return True

    # Отримання списку зв'язків вузла.
    def GetLinks(self, Position: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        with self.Lock:
            Node = self.Nodes.get(Position)
            return [] if Node is None else list(Node.Links)

    # Обчислення евклідової відстані між двома точками.
    def Distance(self, X1: int, Y1: int, Z1: int, X2: int, Y2: int, Z2: int) -> float:
        return math.sqrt((X2 - X1) ** 2 + (Y2 - Y1) ** 2 + (Z2 - Z1) ** 2)

    # Пошук сусідніх вузлів у радіусі.
    def Neighbors(self, X: int, Y: int, Z: int, Radius: int = 1) -> List[MatrixNode]:
        Result: List[MatrixNode] = []
        with self.Lock:
            for Position, Node in self.Nodes.items():
                if Position == (X, Y, Z):
                    continue
                if self.Distance(X, Y, Z, Position[0], Position[1], Position[2]) <= Radius:
                    Result.append(Node)
        return Result

    # Отримання меж матриці за координатами вузлів.
    def Bounds(self) -> Tuple[int, int, int, int, int, int]:
        with self.Lock:
            if not self.Nodes:
                return (0, 0, 0, 0, 0, 0)
            Xs = [Position[0] for Position in self.Nodes]
            Ys = [Position[1] for Position in self.Nodes]
            Zs = [Position[2] for Position in self.Nodes]
            return (min(Xs), min(Ys), min(Zs), max(Xs), max(Ys), max(Zs))

    # Додавання піддомену до матриці.
    def AddDomain(self, Name: str, Domain: "SystemMatrix") -> bool:
        with self.Lock:
            Domain.Parent = self
            self.Domains[Name] = Domain
        return True

    # Створення нового піддомену з вказаними розмірностями.
    def CreateDomain(self, Name: str, Dimensions: Optional[List[int]] = None) -> "SystemMatrix":
        Domain = SystemMatrix(
            Dimensions=Dimensions,
            Id=f"{self.Id}.{Name}",
            Registry=self.Registry,
            ODN=self.ODN,
            Nexus=self.Nexus,
            Parent=self,
        )
        self.AddDomain(Name, Domain)
        return Domain

    # Отримання піддомену за назвою.
    def GetDomain(self, Name: str) -> Optional["SystemMatrix"]:
        with self.Lock:
            return self.Domains.get(Name)

    # Видалення піддомену за назвою.
    def RemoveDomain(self, Name: str) -> bool:
        with self.Lock:
            Domain = self.Domains.pop(Name, None)
            if Domain is None:
                return False
            Domain.Parent = None
            return True

    # Формування ієрархічного опису матриці.
    def GetHierarchy(self) -> Dict[str, Any]:
        with self.Lock:
            return {
                "id": self.Id,
                "version": self.Version,
                "dimensions": list(self.Dimensions),
                "role": self.Role,
                "domains": {Name: Domain.GetHierarchy() for Name, Domain in self.Domains.items()},
                "nodes": len(self.Nodes),
            }

    # Підключення зворотного виклику до сигналу ODN.
    def ConnectSignal(self, Signal: str, Callback) -> bool:
        if self.ODN is None or not hasattr(self.ODN, "Subscribe"):
            return False
        self.ODN.EventBus.On(Signal, Callback)
        return True

    # Надсилання сигналу через ODN.
    def SendSignal(self, Signal: str, *Args, **Kwargs) -> bool:
        if self.ODN is None or not hasattr(self.ODN, "Send"):
            return False
        self.ODN.Emit(Signal, *Args, **Kwargs)
        return True

    # Реєстрація матриці в Nexus.
    def RegisterWithNexus(self, Name: str = "Matrix") -> bool:
        if self.Nexus is None or not hasattr(self.Nexus, "Register"):
            return False
        self.Nexus.Register(Name, self)
        return True

    # Встановлення квантового стану вузла.
    def SetQuantumState(
        self,
        X: int,
        Y: int,
        Z: int,
        Amplitude: complex,
        Phase: float = 0.0,
    ) -> QuantumState:
        Node = self.EnsureNode(X, Y, Z)
        Node.Quantum.Amplitude = Amplitude
        Node.Quantum.Phase = Phase
        Node.Quantum.Probability = abs(Amplitude) ** 2
        return Node.Quantum

    # Заплутування двох вузлів у квантовому стані.
    def Entangle(self, First: Tuple[int, int, int], Second: Tuple[int, int, int]) -> bool:
        with self.Lock:
            A = self.Nodes.get(First)
            B = self.Nodes.get(Second)
            if A is None or B is None:
                return False
            if Second not in A.Quantum.Entangled:
                A.Quantum.Entangled.append(Second)
            if First not in B.Quantum.Entangled:
                B.Quantum.Entangled.append(First)
            return True

    # Вимірювання квантового стану вузла.
    def MeasureQuantum(self, X: int, Y: int, Z: int) -> Optional[Dict[str, Any]]:
        Node = self.GetNode(X, Y, Z)
        if Node is None:
            return None
        Node.Quantum.Measured = True
        return {
            "Amplitude": Node.Quantum.Amplitude,
            "Phase": Node.Quantum.Phase,
            "Probability": Node.Quantum.Probability,
        }

    # Отримання квантового стану вузла.
    def GetQuantumState(self, X: int, Y: int, Z: int) -> Optional[QuantumState]:
        Node = self.GetNode(X, Y, Z)
        return None if Node is None else Node.Quantum

    # Створення підматриці як домену.
    def CreateSubMatrix(self, Name: str, Dimensions: Optional[List[int]] = None) -> "SystemMatrix":
        return self.CreateDomain(Name, Dimensions)

    # Витягування прямокутної області з матриці.
    def Extract(self, X1: int, Y1: int, Z1: int, X2: int, Y2: int, Z2: int) -> "SystemMatrix":
        Result = SystemMatrix(
            Dimensions=[X2 - X1 + 1, Y2 - Y1 + 1, Z2 - Z1 + 1],
            Id=f"{self.Id}.extract",
            Registry=self.Registry,
            ODN=self.ODN,
            Nexus=self.Nexus,
        )
        with self.Lock:
            for (X, Y, Z), Node in self.Nodes.items():
                if X1 <= X <= X2 and Y1 <= Y <= Y2 and Z1 <= Z <= Z2:
                    Result.SetNode(
                        X - X1,
                        Y - Y1,
                        Z - Z1,
                        Node.Value,
                        Node.Type,
                        Node.State,
                        dict(Node.Metadata),
                    )
                    Copy = Result.GetNode(X - X1, Y - Y1, Z - Z1)
                    if Copy is not None:
                        Copy.Links = list(Node.Links)
                        Copy.Quantum = QuantumState(
                            Amplitude=Node.Quantum.Amplitude,
                            Phase=Node.Quantum.Phase,
                            Probability=Node.Quantum.Probability,
                            Measured=Node.Quantum.Measured,
                            Entangled=list(Node.Quantum.Entangled),
                        )
        return Result

    # Вставка вузлів з іншої матриці зі зміщенням.
    def Insert(self, Matrix: "SystemMatrix", Offset: Tuple[int, int, int] = (0, 0, 0)) -> int:
        Ox, Oy, Oz = Offset
        Count = 0
        with self.Lock:
            for (X, Y, Z), Node in Matrix.Nodes.items():
                self.SetNode(
                    X + Ox,
                    Y + Oy,
                    Z + Oz,
                    Node.Value,
                    Node.Type,
                    Node.State,
                    dict(Node.Metadata),
                )
                Copy = self.GetNode(X + Ox, Y + Oy, Z + Oz)
                if Copy is not None:
                    Copy.Links = list(Node.Links)
                    Copy.Quantum = QuantumState(
                        Amplitude=Node.Quantum.Amplitude,
                        Phase=Node.Quantum.Phase,
                        Probability=Node.Quantum.Probability,
                        Measured=Node.Quantum.Measured,
                        Entangled=list(Node.Quantum.Entangled),
                    )
                Count += 1
        return Count

    # Встановлення стану вузла за координатами.
    def SetState(self, X: int, Y: int, Z: int, State: str) -> bool:
        Node = self.GetNode(X, Y, Z)
        if Node is None:
            return False
        Node.State = State
        return True

    # Отримання стану вузла за координатами.
    def GetState(self, X: int, Y: int, Z: int) -> Optional[str]:
        Node = self.GetNode(X, Y, Z)
        return None if Node is None else Node.State

    # Повернення кількості вузлів у матриці.
    def Size(self) -> int:
        with self.Lock:
            return len(self.Nodes)

    # Очищення всіх вузлів матриці.
    def Clear(self) -> None:
        with self.Lock:
            self.Nodes.clear()

    # Змінює межі матриці й прибирає вузли, що вийшли за них.
    def Resize(self, Dimensions: List[int]) -> None:
        with self.Lock:
            self.Dimensions = self.NormalizeDimensions(Dimensions)
            ToRemove = []
            for (X, Y, Z) in self.Nodes:
                if X < 0 or Y < 0 or Z < 0:
                    ToRemove.append((X, Y, Z))
                    continue
                if X >= self.Dimensions[0] or Y >= self.Dimensions[1] or Z >= self.Dimensions[2]:
                    ToRemove.append((X, Y, Z))
            for Position in ToRemove:
                self.Nodes.pop(Position, None)

    # Формує коротку технічну статистику для ядра й термінала.
    def Stats(self) -> Dict[str, Any]:
        return {
            "Id": self.Id,
            "Version": self.Version,
            "Role": self.Role,
            "Dimensions": list(self.Dimensions),
            "Nodes": self.Size(),
            "Domains": len(self.Domains),
            "Bounds": self.Bounds(),
        }

    # Знімає повний знімок вузлів, зв'язків і квантового шару.
    def Snapshot(self) -> Dict[str, Any]:
        with self.Lock:
            return {
                str(Position): {
                    "value": Node.Value,
                    "type": Node.Type,
                    "state": Node.State,
                    "metadata": dict(Node.Metadata),
                    "links": list(Node.Links),
                    "quantum": {
                        "amplitude": Node.Quantum.Amplitude,
                        "phase": Node.Quantum.Phase,
                        "probability": Node.Quantum.Probability,
                        "measured": Node.Quantum.Measured,
                        "entangled": list(Node.Quantum.Entangled),
                    },
                }
                for Position, Node in self.Nodes.items()
            }

    # Відновлює матрицю зі знімка без домислювання структури.
    def Restore(self, Snapshot: Dict[str, Any]) -> None:
        with self.Lock:
            self.Nodes.clear()
            for Position, Data in Snapshot.items():
                Coordinates = self.PositionFromKey(Position)
                if Coordinates is None or not isinstance(Data, dict):
                    continue
                X, Y, Z = Coordinates
                Node = self.SetNode(
                    X,
                    Y,
                    Z,
                    Data.get("value"),
                    Data.get("type", "Generic"),
                    Data.get("state", "idle"),
                    Data.get("metadata", {}),
                )
                Links = []
                for Link in Data.get("links", []):
                    LinkPos = self.PositionFromKey(Link)
                    if LinkPos is not None:
                        Links.append(LinkPos)
                Node.Links = Links
                Quantum = Data.get("quantum", {})
                if isinstance(Quantum, dict):
                    Node.Quantum.Amplitude = Quantum.get("amplitude", 1 + 0j)
                    Node.Quantum.Phase = Quantum.get("phase", 0.0)
                    Node.Quantum.Probability = Quantum.get("probability", abs(Node.Quantum.Amplitude) ** 2)
                    Node.Quantum.Measured = Quantum.get("measured", False)
                    Entangled = []
                    for Link in Quantum.get("entangled", []):
                        LinkPos = self.PositionFromKey(Link)
                        if LinkPos is not None:
                            Entangled.append(LinkPos)
                    Node.Quantum.Entangled = Entangled

    # Встановлення даних вузла (обгортка над SetNode).
    def SetData(self, X: int, Y: int, Z: int, Value: Any, Metadata=None) -> MatrixNode:
        return self.SetNode(X, Y, Z, Value=Value, Metadata=Metadata)

    # Отримання даних вузла зі значенням за замовчуванням.
    def GetData(self, X: int, Y: int, Z: int, default=None) -> Any:
        Value = self.Read(X, Y, Z)
        return default if Value is None else Value

    # Перевірка наявності даних у вузлі.
    def HasData(self, X: int, Y: int, Z: int) -> bool:
        return self.HasNode(X, Y, Z)

    # Отримання розміру матриці (обгортка над Size).
    def GetSize(self) -> int:
        return self.Size()

    # Формування діагностичного звіту ядра.
    def GetCoreDiagnostics(self) -> Dict[str, Any]:
        return {
            "matrix": self.Stats(),
            "domains": list(self.Domains.keys()),
            "status": self.Status,
        }


__all__ = ["QuantumState", "MatrixNode", "SystemMatrix"]
