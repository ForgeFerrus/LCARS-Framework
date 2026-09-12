# Titanium Bridge Migration: from typing import Dict, List, Optional, Callable, Any
# Titanium Bridge Migration: from dataclasses import dataclass, field
from lcars.base.type import Matrix, Directive
from lcars.base.signal import Signal
# Titanium Bridge Migration: from enum import Enum
import time

class SensorType(Enum):
    OPTICAL = "optical"
    SUBSPACE = "subspace"
    TACHYON = "tachyon"
    GRAVIMETRIC = "gravimetric"
    THERMAL = "thermal"
    MAGNETIC = "magnetic"

@dataclass
class SensorReading:
    sensorId: str
    sensorType: SensorType
    value: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def toDict(self) -> Dict:
        return {
            "sensorId": self.sensorId,
            "sensorType": self.sensorType.value,
            "value": self.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

class SensorSubsystem:
    def __init__(self):
        self.sensors: Dict[str, Dict] = {}
        self.readings: List[SensorReading] = []
        self.listeners: List[Callable] = []
        self.activeScans: Dict[str, Any] = {}
        
    def registerSensor(self, sensorId: str, sensorType: SensorType, metadata: Dict = None) -> bool:
        # Реєстрація сенсора
        self.sensors[sensorId] = {
            "type": sensorType,
            "metadata": metadata or {},
            "status": "active"
        }
        return True
        
    def readSensor(self, sensorId: str, value: float, metadata: Dict = None) -> bool:
        # Зчитування показань
        if sensorId not in self.sensors:
            return False
        reading = SensorReading(
            sensorId=sensorId,
            sensorType=self.sensors[sensorId]["type"],
            value=value,
            metadata=metadata or {}
        )
        self.readings.append(reading)
        self.notify("sensorReading", reading)
        return True
        
    def startScan(self, scanId: str, sensorTypes: List[SensorType], rangeKm: float) -> bool:
        # Почати сканування
        self.activeScans[scanId] = {
            "types": sensorTypes,
            "range": rangeKm,
            "started": time.time(),
            "status": "scanning"
        }
        return True
        
    def stopScan(self, scanId: str) -> bool:
        # Зупинити сканування
        if scanId not in self.activeScans:
            return False
        self.activeScans[scanId]["status"] = "complete"
        return True
        
    def getReadings(self, sensorType: SensorType = None, limit: int = 100) -> List[SensorReading]:
        # Отримати показання
        filtered = self.readings
        if sensorType:
            filtered = [r for r in filtered if r.sensorType == sensorType]
        return filtered[-limit:]
        
    def getActiveSensors(self) -> List[str]:
        # Активні сенсори
        return [sid for sid, data in self.sensors.items() if data.get("status") == "active"]
        
    def calibrateSensor(self, sensorId: str, calibrationData: Dict) -> bool:
        # Калібрування
        if sensorId not in self.sensors:
            return False
        self.sensors[sensorId]["calibration"] = calibrationData
        return True
        
    def addListener(self, callback: Callable):
        # Додати слухача
        self.listeners.append(callback)
        
    def notify(self, event: str, reading: SensorReading):
        # Сповістити слухачів
        for listener in self.listeners:
            if callable(listener):
                listener(event, reading)
                
    def getStats(self) -> Dict[str, Any]:
        # Статистика
        return {
            "totalSensors": len(self.sensors),
            "activeSensors": len(self.getActiveSensors()),
            "totalReadings": len(self.readings),
            "activeScans": len(self.activeScans)
        }

sensorSubsystem: Optional[SensorSubsystem] = None

# --- СЕНСОРИ СИСТЕМИ ---

class CPUSensor(Sensor):
    # Сенсор завантаження CPU
    # У спрощеній версії повертає емульовані дані

    def ReadLogic(self) -> float:
        # Емульоване значення для демонстрації
        # В реальній системі тут читання з Kernel.State
        return 15.0


class MemorySensor(Sensor):
    # Сенсор використання памяті

    def ReadLogic(self) -> float:
        # Емульоване значення
        return 45.0


class NetworkSensor(Sensor):
    # Сенсор мережевого трафіку

    def ReadLogic(self) -> float:
        # Емульоване значення в MB
        return 2.5

# --- ІНЖЕНЕРНІ СЕНСОРИ ---

class IntegritySensor(Sensor):
    # Сенсор цілісності корпусу

    def ReadLogic(self) -> float:
        # Значення цілісності від 0 до 100
        return 99.8

class SensorArray(SystemComponent):
    # Масив сенсорів (Sensor Array Module)

    # Сигнал потоку даних: словник з показаннями
    DataStream = Signal(dict)

    def __init__(self, Name: str = "Main Sensor Array"):
        super().__init__()
        self.Name = Name
        self.Sensors: list[Sensor] = []
        self.SetupStandardGrid()

    def SetupStandardGrid(self) -> None:
        # Стандартний набір сенсорів
        self.AddSensor(CPUSensor("CPU_LOAD", "System"))
        self.AddSensor(MemorySensor("MEM_LOAD", "System"))
        self.AddSensor(IntegritySensor("HULL_INTEGRITY", "Engineering"))

    def AddSensor(self, SensorInstance: Sensor) -> None:
        # Додавання сенсора до масиву
        self.Sensors.append(SensorInstance)

    def PollGrid(self) -> dict[str, Any]:
        # Опитування всіх сенсорів
        Matrix = {}
        for S in self.Sensors:
            Matrix[S.Name] = S.Read()
        self.DataStream.Emit(Matrix)
        return Matrix

    def GetStatus(self) -> dict[str, Any]:
        # Отримання статусу масиву сенсорів
        return {
            "Name": self.Name,
            "SensorCount": len(self.Sensors),
            "LastPoll": self.PollGrid(),
        }

    SensorSystem = SensorArray
# Глобальний екземпляр    
def getSensorSubsystem() -> SensorSubsystem:
    global sensorSubsystem
    if sensorSubsystem is None:
        sensorSubsystem = SensorSubsystem()
    return sensorSubsystem
