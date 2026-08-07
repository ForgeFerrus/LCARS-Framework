# LCARS COLLECTOR - ENGINEERING LAYER
# Призначення: зібрати й звести дані з інженерної, модульної та системної частин
# Стан: один агрегатор даних для борту, без зайвих проміжних оболонок

from __future__ import annotations

from typing import Any, Callable

from lcars.base.type import SystemComponent
from lcars.core.signal import Transmission


class CollectorCore(SystemComponent):
    # Збирає всі доступні зрізи в один спільний стан
    # Ініціалізація ядра колектора.
    def __init__(self):
        super().__init__()
        self.Updated = Transmission(dict)
        self.Last: dict[str, Any] = {}
        self.EngineeringNode = None
        self.ModuleNode = None
        self.SystemNode = None

    def AttachEngineering(self, Sensors) -> bool:
        # Підключення до інженерного вузла
        self.EngineeringNode = Sensors

        Stream = getattr(Sensors, "DataStream", None)
        if Stream and hasattr(Stream, "Connect"):
            Stream.Connect(self.OnEngineeringData)
            return True

        return False

    def AttachModules(self, Sensors) -> bool:
        # Підключення до модульного вузла
        self.ModuleNode = Sensors

        Stream = getattr(Sensors, "FrameworkUpdated", None)
        if Stream and hasattr(Stream, "Connect"):
            Stream.Connect(self.OnModuleData)
            return True

        Stream = getattr(Sensors, "EngineeringUpdated", None)
        if Stream and hasattr(Stream, "Connect"):
            Stream.Connect(self.OnModuleData)
            return True

        Stream = getattr(Sensors, "SensorReadingReceived", None)
        if Stream and hasattr(Stream, "Connect"):
            Stream.Connect(self.OnModuleData)
            return True

        return False

    def AttachSystem(self, Node) -> bool:
        # Підключення до системної матриці
        self.SystemNode = Node

        Stream = getattr(Node, "FrameworkUpdated", None)
        if Stream and hasattr(Stream, "Connect"):
            Stream.Connect(self.OnSystemData)
            return True

        Stream = getattr(Node, "EngineeringUpdated", None)
        if Stream and hasattr(Stream, "Connect"):
            Stream.Connect(self.OnSystemData)
            return True

        return False

    def ConnectMetrics(self, Listener: Callable[[dict], None]) -> None:
        # Підписка на зведені метрики
        self.Updated.Connect(Listener)

    def DisconnectMetrics(self, Listener: Callable[[dict], None]) -> None:
        # Відписка від зведених метрик
        self.Updated.Disconnect(Listener)

    def OnEngineeringData(self, Data: dict[str, Any]) -> None:
        # Нормалізуємо інженерні дані до компактної форми
        self.Last["Eng"] = self.NormalizeEngineering(Data)
        self.Updated.Emit(self.GetAll())

    def OnModuleData(self, Data: dict[str, Any]) -> None:
        # Зберігаємо модульний шар як єдиний зріз
        self.Last["Mod"] = Data if isinstance(Data, dict) else {}
        self.Updated.Emit(self.GetAll())

    def OnSystemData(self, Data: dict[str, Any]) -> None:
        # Зберігаємо системний шар як окремий зріз
        self.Last["Sys"] = Data if isinstance(Data, dict) else {}
        self.Updated.Emit(self.GetAll())

    def PollEngineering(self) -> dict[str, Any]:
        # Активне опитування інженерного вузла
        Node = self.EngineeringNode
        if not Node:
            return {}

        if hasattr(Node, "PollGrid") and callable(Node.PollGrid):
            Result = Node.PollGrid()
            return Result if isinstance(Result, dict) else {}

        if hasattr(Node, "GetStatus") and callable(Node.GetStatus):
            Result = Node.GetStatus()
            return Result if isinstance(Result, dict) else {}

        if hasattr(Node, "GetAllSensors") and callable(Node.GetAllSensors):
            Sensors = Node.GetAllSensors()
            SensorList: list[Any] = []
            if isinstance(Sensors, list):
                SensorList = Sensors
            elif isinstance(Sensors, tuple):
                SensorList = list(Sensors)
            else:
                return {}

            return {
                "Sensors": [
                    Sensor.ToDict() if hasattr(Sensor, "ToDict") else Sensor
                    for Sensor in SensorList
                ]
            }

        return {}

    def PollModules(self) -> dict[str, Any]:
        # Активне опитування модульного вузла
        Node = self.ModuleNode
        if not Node:
            return {}

        if hasattr(Node, "GetCurrentData") and callable(Node.GetCurrentData):
            Result = Node.GetCurrentData()
            return Result if isinstance(Result, dict) else {}

        if hasattr(Node, "GetStats") and callable(Node.GetStats):
            Result = Node.GetStats()
            return Result if isinstance(Result, dict) else {}

        return {}

    def PollSystem(self) -> dict[str, Any]:
        # Активне опитування системного вузла
        Node = self.SystemNode
        if not Node:
            return {}

        if hasattr(Node, "GetCurrentData") and callable(Node.GetCurrentData):
            Result = Node.GetCurrentData()
            return Result if isinstance(Result, dict) else {}

        if hasattr(Node, "GetStats") and callable(Node.GetStats):
            Result = Node.GetStats()
            return Result if isinstance(Result, dict) else {}

        if hasattr(Node, "GetAll") and callable(Node.GetAll):
            Result = Node.GetAll()
            return Result if isinstance(Result, dict) else {}

        return {}

    def PollAll(self) -> dict[str, Any]:
        # Оновлюємо всі шари й одразу формуємо знімок
        EngData = self.PollEngineering()
        ModData = self.PollModules()
        SysData = self.PollSystem()

        if EngData:
            self.Last["Eng"] = self.NormalizeEngineering(EngData)
        if ModData:
            self.Last["Mod"] = ModData
        if SysData:
            self.Last["Sys"] = SysData

        return self.GetAll()

    def Status(self) -> str:
        # Беремо найгірший стан із доступних шарів
        Eng = self.Last.get("Eng", {})
        Sys = self.Last.get("Sys", {})

        CPU = max(
            self.PickNumber(Eng, ["CPU", "CPU_LOAD", "system_load"]),
            self.PickNumber(Sys, ["CPU", "CPU_LOAD", "system_load"]),
        )
        Mem = max(
            self.PickNumber(Eng, ["Mem", "MEM_LOAD", "memory_usage"]),
            self.PickNumber(Sys, ["Mem", "MEM_LOAD", "memory_usage"]),
        )

        if CPU > 90 or Mem > 90:
            return "CRITICAL"
        if CPU > 70 or Mem > 75:
            return "WARNING"
        return "NOMINAL"

    def Get(self) -> dict[str, Any]:
        # Зворотний сумісний виклик
        return self.GetAll()

    def GetAll(self) -> dict[str, Any]:
        # Єдина точка доступу для бортового комп’ютера
        print("STATUS =", self.Status)
        print("TYPE =", type(self.Status))
        Snapshot = {
            "Status": self.Status,
            "Eng": self.Last.get("Eng", {}),
            "Mod": self.Last.get("Mod", {}),
        }
        if self.Last.get("Sys"):
            Snapshot["Sys"] = self.Last.get("Sys", {})
        return Snapshot

    def GetStats(self) -> dict[str, Any]:
        # Власна статистика колектора
        return {
            "has_engineering": self.EngineeringNode is not None,
            "has_modules": self.ModuleNode is not None,
            "has_system": self.SystemNode is not None,
            "status": self.Status,
            "sections": len([Key for Key in ("Eng", "Mod", "Sys") if self.Last.get(Key)]),
        }

    def NormalizeEngineering(self, Data: dict[str, Any]) -> dict[str, Any]:
        # Переходимо до спрощених ключів, незалежно від того, хто подав дані
        if not isinstance(Data, dict):
            return {}

        if "CPU" in Data or "Mem" in Data or "Hull" in Data:
            return {
                "CPU": self.SafeNumber(Data.get("CPU")),
                "Mem": self.SafeNumber(Data.get("Mem")),
                "Hull": self.SafeNumber(Data.get("Hull", 100)),
            }

        if "CPU_LOAD" in Data or "MEM_LOAD" in Data or "HULL_INTEGRITY" in Data:
            CpuNode = Data.get("CPU_LOAD", {})
            MemNode = Data.get("MEM_LOAD", {})
            HullNode = Data.get("HULL_INTEGRITY", {})
            return {
                "CPU": self.PickReadingValue(CpuNode),
                "Mem": self.PickReadingValue(MemNode),
                "Hull": self.PickReadingValue(HullNode, fallback=100),
            }

        if "system_load" in Data or "memory_usage" in Data:
            return {
                "CPU": self.SafeNumber(Data.get("system_load")),
                "Mem": self.SafeNumber(Data.get("memory_usage")),
                "Hull": self.SafeNumber(Data.get("shield_status", 100)),
            }

        return Data

    # Витягуємо числове значення з вузла або повертаємо запасне.
    def PickReadingValue(self, Node: Any, fallback: float = 0.0) -> float:
        if isinstance(Node, dict):
            Value = Node.get("value", fallback)
            return self.SafeNumber(Value, fallback)
        return self.SafeNumber(Node, fallback)

    # Шукаємо перше числове значення за списком ключів.
    def PickNumber(self, Data: dict[str, Any], Keys: list[str]) -> float:
        for Key in Keys:
            Value = Data.get(Key)
            if isinstance(Value, dict):
                Value = Value.get("value")
            if isinstance(Value, (int, float)):
                return float(Value)
            if isinstance(Value, str) and Value.replace(".", "", 1).isdigit():
                return float(Value)
        return 0.0

    # Безпечно перетворюємо значення на число.
    def SafeNumber(self, Value: Any, fallback: float = 0.0) -> float:
        if isinstance(Value, (int, float)):
            return float(Value)
        if isinstance(Value, str) and Value.replace(".", "", 1).isdigit():
            return float(Value)
        return float(fallback)


CollectorInstance = CollectorCore()
__all__ = [
    "CollectorCore",
    "CollectorInstance",
]
