
# Діагностична підсистема LCARS
# Ізолінійний чіп: 00-0009
# Відповідає за збір даних з сенсорів системи

# Titanium Bridge Migration: from dataclasses import dataclass, field
# Titanium Bridge Migration: from typing import Any, Callable, Optional
from lcars.base.type import SystemComponent
from lcars.core.signal import Transmission
from time import time

@dataclass
class SensorReading:
    # Запис показань сенсора
    name: str
    value: Any
    timestamp: float = field(default_factory=time)

# Базовий клас сенсора системи
# Наслідується для створення специфічних сенсорів (температура, навантаження тощо)
class Sensor(SystemComponent):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        # Сигнал при новому показанні
        self.readingReceived = Transmission()
    
    def read(self) -> SensorReading:
        # Читає поточне значення сенсора
        # Підкласи повинні перевизначити цей метод
        reading = SensorReading(self.name, None)
        self.readingReceived.emit(reading)
        return reading

# Центральна діагностична система на чіпі 00-0009
# Керує сенсорами та зберігає історію показань
class DiagnosticSystem(SystemComponent):

    def __init__(self):
        super().__init__()
        # Сенсори за іменем
        self.sensors: dict[str, Sensor] = {}
        # Історія показань
        self.history: list[SensorReading] = []
        # Підписники на події
        self.callbacks: list[Callable] = []
        # Сигнали
        self.sensorRegistered = Transmission()
        self.readingAdded = Transmission()
        self.systemChecked = Transmission()
    
    def register(self, sensor: Sensor) -> None:
        # Реєструє сенсор в системі
        self.sensors[sensor.name] = sensor
        self.sensorRegistered.emit({"sensor": sensor.name})
    
    def unregister(self, name: str) -> bool:
        # Видаляє сенсор з системи
        if name in self.sensors:
            del self.sensors[name]
            return True
        return False
    
    def read(self, name: str) -> Optional[SensorReading]:
        # Читає показання конкретного сенсора
        sensor = self.sensors.get(name)
        if sensor:
            reading = sensor.read()
            self.history.append(reading)
            self.readingAdded.emit(reading)
            return reading
        return None
    
    def readAll(self) -> dict[str, SensorReading]:
        # Читає всі сенсори та повертає словник показань
        results: dict[str, SensorReading] = {}
        for name, sensor in self.sensors.items():
            reading = sensor.read()
            results[name] = reading
            self.history.append(reading)
            self.readingAdded.emit(reading)
        self.systemChecked.emit({"count": len(results)})
        return results
    
    def subscribe(self, callback: Callable) -> None:
        # Підписується на всі події діагностики
        self.callbacks.append(callback)
    
    def unsubscribe(self, callback: Callable) -> bool:
        # Відписується від подій
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            return True
        return False
    
    def getHistory(self, name: str, limit: int = 100) -> list[SensorReading]:
        # Повертає історію показань сенсора (останні limit записів)
        return [h for h in self.history if h.name == name][-limit:]
    
    def clearHistory(self, name: Optional[str] = None) -> int:
        # Очищує історію (всю або для конкретного сенсора)
        if name is None:
            count = len(self.history)
            self.history.clear()
            return count
        else:
            originalLen = len(self.history)
            self.history = [h for h in self.history if h.name != name]
            return originalLen - len(self.history)
    
    def getSensorList(self) -> list[str]:
        # Повертає список імен зареєстрованих сенсорів
        return list(self.sensors.keys())
    
    def isSensorAvailable(self, name: str) -> bool:
        # Перевіряє чи сенсор зареєстрований
        return name in self.sensors
    
    def runFullDiagnostic(self) -> dict:
        from lcars.engineering.odn.scanner import scanner
        results = {}
        telemetry = scanner.GetHardwareTelemetry()
        results["telemetry"] = telemetry
        network = scanner.GetNetworkIO()
        results["network"] = network
        processes = scanner.GetProcessMatrix(10)
        results["processes"] = processes
        results["sensor_readings"] = self.readAll()
        return results
    
    def runQuickCheck(self) -> dict:
        from lcars.engineering.odn.scanner import scanner
        telemetry = scanner.GetHardwareTelemetry()
        status = "NOMINAL"
        issues = []
        if telemetry["CpuLoad"] > 80:
            issues.append("HIGH_CPU")
            status = "WARNING"
        if telemetry["MemPercent"] > 85:
            issues.append("HIGH_MEMORY")
            status = "WARNING"
        if telemetry["TempCore"] > 70:
            issues.append("HIGH_TEMP")
            status = "WARNING"
        if len(issues) >= 2:
            status = "CRITICAL"
        return {
            "status": status,
            "issues": issues,
            "telemetry": telemetry
        }

__all__ = ["DiagnosticSystem", "Sensor", "SensorReading", "DiagnosticChip"]

DiagnosticChip = None

def initializeDiagnostic(chip) -> DiagnosticSystem:
    # Ініціалізує діагностичну систему на чіпі 00-0009
    global DiagnosticChip
    DiagnosticChip = chip
    system = DiagnosticSystem()
    return system
