# ◤ TITANIUM SENSOR MODULE
# LCARS Framework :: SENSOR_TYPES // SENSOR_ARRAY // NO_Q PROTOCOL
# ПРИЗНАЧЕННЯ: Керування сенсорами та їх типами
# СТАНДАРТ: Titanium CamelCase, Zero-Except

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import time

from lcars.base.type import SystemComponent
from lcars.core.signal import Signal
from lcars.base.version import getVersion

__version__ = getVersion()

# ◤ ТИПИ СЕНСОРІВ
class SensorType(Enum):
    OPTICAL = "optical"
    SUBSPACE = "subspace"
    TACHYON = "tachyon"
    GRAVIMETRIC = "gravimetric"
    THERMAL = "thermal"
    MAGNETIC = "magnetic"

# ◤ ПОКАЗАННЯ СЕНСОРА
@dataclass
class SensorReading:
    sensorId: str
    sensorType: SensorType
    value: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def ToDict(self) -> Dict:
        return {
            "sensorId": self.sensorId,
            "sensorType": self.sensorType.value,
            "value": self.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

# ◤ БАЗОВИЙ КЛАС СЕНСОРА
class Sensor(SystemComponent):
    def __init__(self, Name: str, Category: str = "Generic"):
        super().__init__()
        self.Name = Name
        self.Category = Category
        self.Active = True
    
    def Read(self) -> Dict[str, Any]:
        Value = self.ReadLogic()
        return {
            "name": self.Name,
            "category": self.Category,
            "value": Value,
            "active": self.Active,
            "timestamp": time.time()
        }
    
    def ReadLogic(self) -> float:
        # Базова логіка - перевизначається в підкласах
        return 0.0

# ◤ СИСТЕМНІ СЕНСОРИ
class CPUSensor(Sensor):
    def ReadLogic(self) -> float:
        return 15.0

class MemorySensor(Sensor):
    def ReadLogic(self) -> float:
        return 45.0

class NetworkSensor(Sensor):
    def ReadLogic(self) -> float:
        return 2.5

# ◤ ІНЖЕНЕРНІ СЕНСОРИ
class IntegritySensor(Sensor):
    def ReadLogic(self) -> float:
        return 99.8

# ◤ МАСИВ СЕНСОРІВ
class SensorArray(SystemComponent):
    DataStream = Signal(dict)

    def __init__(self, Name: str = "Main Sensor Array"):
        super().__init__()
        self.Name = Name
        self.Sensors: List[Sensor] = []
        self.SetupStandardGrid()

    def SetupStandardGrid(self) -> None:
        self.AddSensor(CPUSensor("CPU_LOAD", "System"))
        self.AddSensor(MemorySensor("MEM_LOAD", "System"))
        self.AddSensor(IntegritySensor("HULL_INTEGRITY", "Engineering"))

    def AddSensor(self, SensorInstance: Sensor) -> None:
        self.Sensors.append(SensorInstance)

    def PollGrid(self) -> Dict[str, Any]:
        Matrix = {}
        for S in self.Sensors:
            Matrix[S.Name] = S.Read()
        self.DataStream.Emit(Matrix)
        return Matrix

    def GetStatus(self) -> Dict[str, Any]:
        return {
            "Name": self.Name,
            "SensorCount": len(self.Sensors),
            "LastPoll": self.PollGrid(),
        }

__all__ = [
    "SensorType",
    "SensorReading",
    "Sensor",
    "CPUSensor",
    "MemorySensor",
    "NetworkSensor",
    "IntegritySensor",
    "SensorArray"
]
