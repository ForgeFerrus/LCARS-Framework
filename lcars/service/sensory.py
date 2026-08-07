# ◤ TITANIUM SENSORY SYSTEM
# LCARS Framework :: SENSOR_GRID // ENV_SCANNER // SENSOR_CONTROL // NO_Q PROTOCOL
# ОПИС: Повноцінна сенсорна система з керуванням та агрегацією даних.
# СТАНДАРТ: Titanium CamelCase, Zero-Except.

from lcars.base.type import LCARS
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import time
import psutil

from lcars.base.type import SystemComponent, Directive, LCARSTypes
from lcars.core.signal import ODN, Signal

from lcars.base.version import getVersion
from .logbook import WriteEntry, LogCategory

__version__ = getVersion()

# ◤ ТИПИ СЕНСОРІВ ДЛЯ СИСТЕМИ КЕРУВАННЯ
class SensorCategory(Enum):
    OPTICAL = "optical"
    SUBSPACE = "subspace"
    TACHYON = "tachyon"
    GRAVIMETRIC = "gravimetric"
    THERMAL = "thermal"
    MAGNETIC = "magnetic"
    SYSTEM = "system"
    ENGINEERING = "engineering"

# ◤ ПОКАЗАННЯ СЕНСОРА
@dataclass
class SensorData:
    SensorId: str
    Category: SensorCategory
    Value: float
    Timestamp: float = field(default_factory=time.time)
    Metadata: Dict[str, Any] = field(default_factory=dict)
    
    def ToDict(self) -> Dict:
        return {
            "sensor_id": self.SensorId,
            "category": self.Category.value,
            "value": self.Value,
            "timestamp": self.Timestamp,
            "metadata": self.Metadata
        }

# ◤ ОПИС СЕНСОРА В СИСТЕМІ
@dataclass
class SensorInfo:
    SensorId: str
    Name: str
    Category: SensorCategory
    Status: str = "active"
    Calibration: Dict[str, Any] = field(default_factory=dict)
    LastReading: Optional[SensorData] = None

# ◤ ГОЛОВНА СЕНСОРНА СИСТЕМА
class SensorySystem(SystemComponent):
    # Сигнали
    EnvironmentUpdated = Signal(dict)
    EngineeringUpdated = Signal(dict)
    FrameworkUpdated = Signal(dict)
    SensorReadingReceived = Signal(SensorData)
    
    def __init__(self, Parent=None):
        super().__init__()
        self.Parent = Parent
        
        # Реєстр сенсорів
        self.Sensors: Dict[str, SensorInfo] = {}
        self.Readings: List[SensorData] = []
        self.Listeners: List[Callable] = []
        self.ActiveScans: Dict[str, Any] = {}
        
        # Таймер автосканування
        TimerClass = LCARS.Timer
        if TimerClass and TimerClass is not object:
            self.UpdateTimer = TimerClass()
            self.UpdateTimer.timeout.connect(self.ScanAllSensors)
            self.UpdateTimer.start(5000)
        
        ODN.Emit("Telemetry.Event", "Sensory", "TASK: SYSTEM_READY. Sensor grid online.")
    
    # ◤ РЕЄСТРАЦІЯ ТА КЕРУВАННЯ СЕНСОРАМИ
    
    # Реєстрація нового сенсора в системі
    def RegisterSensor(self, SensorId: str, Name: str, Category: SensorCategory, 
                       Metadata: Dict = None) -> bool:
        self.Sensors[SensorId] = SensorInfo(
            SensorId=SensorId,
            Name=Name,
            Category=Category,
            Metadata=Metadata or {}
        )
        ODN.Emit("Telemetry.Event", "Sensory", f"SENSOR_REGISTERED: {SensorId}")
        return True
    
    # Видалення сенсора з системи
    def UnregisterSensor(self, SensorId: str) -> bool:
        if SensorId in self.Sensors:
            del self.Sensors[SensorId]
            ODN.Emit("Telemetry.Event", "Sensory", f"SENSOR_UNREGISTERED: {SensorId}")
            return True
        return False
    
    # Активація сенсора за ідентифікатором
    def ActivateSensor(self, SensorId: str) -> bool:
        if SensorId in self.Sensors:
            self.Sensors[SensorId].Status = "active"
            ODN.Emit("Telemetry.Event", "Sensory", f"SENSOR_ACTIVE: {SensorId}")
            return True
        return False
    
    # Деактивація сенсора за ідентифікатором
    def DeactivateSensor(self, SensorId: str) -> bool:
        if SensorId in self.Sensors:
            self.Sensors[SensorId].Status = "inactive"
            ODN.Emit("Telemetry.Event", "Sensory", f"SENSOR_INACTIVE: {SensorId}")
            return True
        return False
    
    # Калібрування сенсора новими даними
    def CalibrateSensor(self, SensorId: str, CalibrationData: Dict) -> bool:
        if SensorId not in self.Sensors:
            return False
        self.Sensors[SensorId].Calibration = CalibrationData
        ODN.Emit("Telemetry.Event", "Sensory", f"SENSOR_CALIBRATED: {SensorId}")
        return True
    
    # Отримання статусу конкретного сенсора
    def GetSensorStatus(self, SensorId: str) -> Optional[SensorInfo]:
        return self.Sensors.get(SensorId)
    
    # Список всіх зареєстрованих сенсорів
    def GetAllSensors(self) -> List[SensorInfo]:
        return list(self.Sensors.values())
    
    # Список активних сенсорів
    def GetActiveSensors(self) -> List[str]:
        return [S.SensorId for S in self.Sensors.values() if S.Status == "active"]
    
    # ◤ ЧИТАННЯ ТА ОБРОБКА ДАНИХ
    
    # Подача показань від сенсора в систему
    def SubmitReading(self, SensorId: str, Value: float, Metadata: Dict = None) -> bool:
        if SensorId not in self.Sensors:
            return False
        
        Reading = SensorData(
            SensorId=SensorId,
            Category=self.Sensors[SensorId].Category,
            Value=Value,
            Metadata=Metadata or {}
        )
        
        self.Readings.append(Reading)
        self.Sensors[SensorId].LastReading = Reading
        
        # Сповіщення слухачів
        self.SensorReadingReceived.Emit(Reading)
        for Listener in self.Listeners:
            if callable(Listener):
                Listener("reading", Reading)
        
        return True
    
    # Отримання показань з фільтрацією за сенсором та лімітом
    def GetReadings(self, SensorId: str = None, Limit: int = 100) -> List[SensorData]:
        Filtered = self.Readings
        if SensorId:
            Filtered = [R for R in Filtered if R.SensorId == SensorId]
        return Filtered[-Limit:]
    
    # Очищення показань за ідентифікатором сенсора
    def ClearReadings(self, SensorId: str = None) -> int:
        if SensorId:
            Count = len([R for R in self.Readings if R.SensorId == SensorId])
            self.Readings = [R for R in self.Readings if R.SensorId != SensorId]
            return Count
        else:
            Count = len(self.Readings)
            self.Readings.clear()
            return Count
    
    # Додавання слухача подій сенсорної системи
    def AddListener(self, Callback: Callable):
        self.Listeners.append(Callback)
    
    # Видалення слухача подій
    def RemoveListener(self, Callback: Callable):
        if Callback in self.Listeners:
            self.Listeners.remove(Callback)
    
    # ◤ СКАНУВАННЯ
    
    # Початок сканування з вказаними категоріями та діапазоном
    def StartScan(self, ScanId: str, Categories: List[SensorCategory], Range: float) -> bool:
        self.ActiveScans[ScanId] = {
            "categories": [C.value for C in Categories],
            "range": Range,
            "started": time.time(),
            "status": "scanning"
        }
        ODN.Emit("Telemetry.Event", "Sensory", f"SCAN_STARTED: {ScanId}")
        return True
    
    # Зупинка сканування за ідентифікатором
    def StopScan(self, ScanId: str) -> bool:
        if ScanId not in self.ActiveScans:
            return False
        self.ActiveScans[ScanId]["status"] = "complete"
        ODN.Emit("Telemetry.Event", "Sensory", f"SCAN_COMPLETE: {ScanId}")
        return True
    
    # Отримання статусу сканування
    def GetScanStatus(self, ScanId: str) -> Optional[Dict]:
        return self.ActiveScans.get(ScanId)
    
    # ◤ АГРЕГАЦІЯ СИСТЕМНИХ ДАНИХ (psutil)
    
    # Головне сканування всіх системних сенсорів
    def ScanAllSensors(self):
        TaskId = f"SC-{int(time.time() * 1000) % 10000:04d}"
        
        EnvData = self.GetEnvMatrix()
        self.EnvironmentUpdated.Emit(EnvData)
        
        EngData = self.GetEngMatrix()
        self.EngineeringUpdated.Emit(EngData)
        
        FrameData = self.GetFrameworkMatrix()
        self.FrameworkUpdated.Emit(FrameData)
        
        # Телеметрія
        Metrics = {**EnvData, **EngData, **FrameData}
        ODN.Emit("Telemetry.Metrics", "Sensory", str(Metrics))
        
        # Попередження про перевантаження
        if EngData.get('system_load', 0) > 90:
            ODN.Emit("Telemetry.Warn", "Sensory", f"TASK_WARN: {TaskId}. Core Overload: {EngData['system_load']}%")
            WriteEntry(f"Core overload detected: {EngData['system_load']}%", LogCategory.SYSTEM_LOG)
        
        return Metrics
    
    # Матриця середовища (температура, живлення, EPS)
    def GetEnvMatrix(self) -> Dict:
        Temp = 0
        TempSensors = psutil.sensors_temperatures()
        if TempSensors and 'coretemp' in TempSensors:
            Temp = TempSensors['coretemp'][0].current
        
        Battery = psutil.sensors_battery()
        Power = Battery.percent if Battery else 100
        EpsFlow = round(Power * 0.95, 1)
        
        return {
            "core_temp": Temp,
            "power_level": Power,
            "eps_flow": EpsFlow,
            "platform": Directive.System.platform() if hasattr(Directive.System, "platform") else "LCARS",
            "status": "STABLE"
        }
    
    # Інженерна матриця (CPU, пам'ять, процеси)
    def GetEngMatrix(self) -> Dict:
        Mem = psutil.virtual_memory()
        return {
            "system_load": psutil.cpu_percent(),
            "memory_usage": Mem.percent,
            "ram_allocated_mb": round(Mem.used / (1024**2), 1),
            "active_processes": len(psutil.pids()),
            "eps_status": "NOMINAL",
            "shield_status": "NONE"
        }
    
    # Матриця фреймворку (мережа, інтегріті, uptime)
    def GetFrameworkMatrix(self) -> Dict:
        NetStatus = "OFFLINE"
        if hasattr(Directive, "Network") and Directive.Network.is_online():
            NetStatus = "CONNECTED"
        return {
            "integrity_index": 100,
            "uptime_sec": int(time.time()),
            "network_link": NetStatus,
            "subspace_band": "Standard"
        }
    
    # Агрегація всіх даних з матриць
    def GetCurrentData(self) -> Dict:
        return {
            **self.GetEnvMatrix(),
            **self.GetEngMatrix(),
            **self.GetFrameworkMatrix()
        }
    
    # Статистика сенсорної системи
    def GetStats(self) -> Dict[str, Any]:
        return {
            "total_sensors": len(self.Sensors),
            "active_sensors": len(self.GetActiveSensors()),
            "total_readings": len(self.Readings),
            "active_scans": len([S for S in self.ActiveScans.values() if S.get("status") == "scanning"])
        }

# Глобальний екземпляр
Sensory = SensorySystem()

__all__ = [
    "SensorCategory",
    "SensorData",
    "SensorInfo",
    "SensorySystem",
    "Sensory"
]
