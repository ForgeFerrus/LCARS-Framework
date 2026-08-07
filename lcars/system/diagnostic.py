
# Діагностична підсистема LCARS
# Ізолінійний чіп: 00-0009
# Відповідає за збір даних з сенсорів системи

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from lcars.base.type import SystemComponent
from lcars.core.signal import Transmission
from lcars.system.odn import scanner
from time import time

# Запис показань сенсора
@dataclass
class SensorReading:
    name: str
    value: Any
    timestamp: float = field(default_factory=time)

# Базовий клас сенсора системи
# Наслідується для створення специфічних сенсорів (температура, навантаження тощо)
class Sensor(SystemComponent):
    # Конструктор сенсора
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        # Сигнал при новому показанні
        self.readingReceived = Transmission()
    
    # Читає поточне значення сенсора
    # Підкласи повинні перевизначити цей метод
    def read(self) -> SensorReading:
        reading = SensorReading(self.name, None)
        self.readingReceived.emit(reading)
        return reading

# Центральна діагностична система на чіпі 00-0009
# Керує сенсорами та зберігає історію показань
class DiagnosticSystem(SystemComponent):

    # Конструктор діагностичної системи
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
    
    # Реєструє сенсор в системі
    def register(self, sensor: Sensor) -> None:
        self.sensors[sensor.name] = sensor
        self.sensorRegistered.emit({"sensor": sensor.name})
    
    # Видаляє сенсор з системи
    def unregister(self, name: str) -> bool:
        if name in self.sensors:
            del self.sensors[name]
            return True
        return False
    
    # Читає показання конкретного сенсора
    def read(self, name: str) -> Optional[SensorReading]:
        sensor = self.sensors.get(name)
        if sensor:
            reading = sensor.read()
            self.history.append(reading)
            self.readingAdded.emit(reading)
            return reading
        return None
    
    # Читає всі сенсори та повертає словник показань
    def readAll(self) -> dict[str, SensorReading]:
        results: dict[str, SensorReading] = {}
        for name, sensor in self.sensors.items():
            reading = sensor.read()
            results[name] = reading
            self.history.append(reading)
            self.readingAdded.emit(reading)
        self.systemChecked.emit({"count": len(results)})
        return results
    
    # Підписується на всі події діагностики
    def subscribe(self, callback: Callable) -> None:
        self.callbacks.append(callback)
    
    # Відписується від подій
    def unsubscribe(self, callback: Callable) -> bool:
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            return True
        return False
    
    # Повертає історію показань сенсора (останні limit записів)
    def getHistory(self, name: str, limit: int = 100) -> list[SensorReading]:
        return [h for h in self.history if h.name == name][-limit:]
    
    # Очищує історію (всю або для конкретного сенсора)
    def clearHistory(self, name: Optional[str] = None) -> int:
        if name is None:
            count = len(self.history)
            self.history.clear()
            return count
        else:
            originalLen = len(self.history)
            self.history = [h for h in self.history if h.name != name]
            return originalLen - len(self.history)
    
    # Повертає список імен зареєстрованих сенсорів
    def getSensorList(self) -> list[str]:
        return list(self.sensors.keys())
    
    # Перевіряє чи сенсор зареєстрований
    def isSensorAvailable(self, name: str) -> bool:
        return name in self.sensors
    
    # Запускає повну діагностику системи
    # Збирає телеметрію, мережу, процеси та покази сенсорів
    def runFullDiagnostic(self) -> dict:
        results = {}
        # Збір апаратної телеметрії
        telemetry = scanner.GetHardwareTelemetry()
        results["telemetry"] = telemetry
        # Збір даних мережевого вводу-виводу
        network = scanner.GetNetworkIO()
        results["network"] = network
        # Збір матриці процесів (обмеження 10 записів)
        processes = scanner.GetProcessMatrix(10)
        results["processes"] = processes
        # Збір показань усіх сенсорів
        results["sensor_readings"] = self.readAll()
        return results
    
    # Запускає швидку перевірку системи
    # Перевіряє навантаження CPU, пам'ять та температуру
    def runQuickCheck(self) -> dict:
        # Отримання поточної апаратної телеметрії
        telemetry = scanner.GetHardwareTelemetry()
        status = "NOMINAL"
        issues = []
        # Перевірка навантаження процесора
        if telemetry["CpuLoad"] > 80:
            issues.append("HIGH_CPU")
            status = "WARNING"
        # Перевірка використання пам'яті
        if telemetry["MemPercent"] > 85:
            issues.append("HIGH_MEMORY")
            status = "WARNING"
        # Перевірка температури ядра
        if telemetry["TempCore"] > 70:
            issues.append("HIGH_TEMP")
            status = "WARNING"
        # Якщо є два або більше проблемних показників — статус критичний
        if len(issues) >= 2:
            status = "CRITICAL"
        return {
            "status": status,
            "issues": issues,
            "telemetry": telemetry
        }

__all__ = ["DiagnosticSystem", "Sensor", "SensorReading", "DiagnosticChip"]

DiagnosticChip = None

# Ініціалізує діагностичну систему на чіпі 00-0009
def initializeDiagnostic(chip) -> DiagnosticSystem:
    global DiagnosticChip
    DiagnosticChip = chip
    system = DiagnosticSystem()
    return system
