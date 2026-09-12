# ◤ TITANIUM SENSORY SYSTEM & SCIENTIFIC SENSOR ARRAY // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/modules/sensor.py
# ОПИС: Головний сенсорний комплекс зорельота (Sensory Array). Керує науковими,
#       тактичними та внутрішніми сенсорами корабля: тахіонними, гравіметричними,
#       субпросторовими, біологічними, оптичними, магнітними та термальними.
#       Передає результати сканування секторів по шині ODN-10.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import SystemComponent, LCARS, Directive
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN, Transmission

# Типи фізичних сенсорів зорельота
class SensorType(LCARS):
    OPTICAL = "OPTICAL"
    TACHYON = "TACHYON"
    GRAVIMETRIC = "GRAVIMETRIC"
    SUBSPACE = "SUBSPACE"
    THERMAL = "THERMAL"
    MAGNETIC = "MAGNETIC"
    RADIATION = "RADIATION"
    BIOLOGICAL = "BIOLOGICAL"
    STRUCTURAL = "STRUCTURAL"

# Знімок показання окремого сенсора
class SensorReading(LCARS):
    def __init__(self, SensorId: str, Category: str, Value: float, Unit: str,
                 IsSafe: bool = True, Status: str = "NOMINAL", Metadata: dict | None = None):
        super().__init__()
        self.SensorId = SensorId
        self.Category = Category
        self.Value = float(Value)
        self.Unit = Unit
        self.IsSafe = bool(IsSafe)
        self.Status = Status
        self.Metadata = Metadata or {}
        TimeModule = LCARS.System.Time
        self.Timestamp = TimeModule.time() if TimeModule and hasattr(TimeModule, "time") else 0.0

    def ToDict(self) -> dict:
        return {
            "SensorId": self.SensorId,
            "Category": self.Category,
            "Value": self.Value,
            "Unit": self.Unit,
            "IsSafe": self.IsSafe,
            "Status": self.Status,
            "Timestamp": self.Timestamp,
            "Metadata": self.Metadata,
        }

# Базовий клас фізичного сенсора корабля
class Sensor(SystemComponent):
    def __init__(self, Name: str, Category: str = SensorType.OPTICAL, Unit: str = "",
                 MinSafe: float = 0.0, MaxSafe: float = 1000.0):
        super().__init__()
        self.Name = Name
        self.Category = Category
        self.Unit = Unit
        self.MinSafe = float(MinSafe)
        self.MaxSafe = float(MaxSafe)
        self.Active = True
        self.LastReading: SensorReading | None = None

    def Read(self) -> SensorReading:
        if not self.Active:
            return SensorReading(self.Name, self.Category, 0.0, self.Unit, False, "OFFLINE")

        Value = self.ReadLogic()
        IsSafe = (self.MinSafe <= Value <= self.MaxSafe)
        Status = "NOMINAL" if IsSafe else "WarningThresholdExceeded"

        Reading = SensorReading(
            SensorId=self.Name,
            Category=self.Category,
            Value=Value,
            Unit=self.Unit,
            IsSafe=IsSafe,
            Status=Status,
        )
        self.LastReading = Reading
        return Reading

    def ReadLogic(self) -> float:
        return 0.0

# ─── СПЕЦІАЛІЗОВАНІ СЕНСОРИ ЗОРЕЛЬОТА ──────────────────────────────────────────

# Тахіонний сенсор (виявлення замаскованих об'єктів та варп-слідів)
class TachyonSensor(Sensor):
    def __init__(self, Name: str = "TachyonScanner"):
        super().__init__(Name, SensorType.TACHYON, Unit="ppb", MinSafe=0.0, MaxSafe=10.0)

    def ReadLogic(self) -> float:
        return 0.04

# Гравіметричний сенсор (просторові аномалії та викривлення гравітації)
class GravimetricSensor(Sensor):
    def __init__(self, Name: str = "GravimetricDistortion"):
        super().__init__(Name, SensorType.GRAVIMETRIC, Unit="milliG", MinSafe=-50.0, MaxSafe=50.0)

    def ReadLogic(self) -> float:
        return 0.15

# Субпросторовий сенсор (коливання підпросторового континууму)
class SubspaceSensor(Sensor):
    def __init__(self, Name: str = "SubspaceTransceiver"):
        super().__init__(Name, SensorType.SUBSPACE, Unit="Cochranes", MinSafe=0.0, MaxSafe=100.0)

    def ReadLogic(self) -> float:
        return 1.0

# Біосенсор (детекція життєвих форм та чисельності екіпажу)
class BioSensor(Sensor):
    def __init__(self, Name: str = "InternalBioScanner"):
        super().__init__(Name, SensorType.BIOLOGICAL, Unit="Lifeforms", MinSafe=1.0, MaxSafe=1200.0)

    def ReadLogic(self) -> float:
        return 430.0

# Термальний сенсор (температурний баланс систем)
class ThermalSensor(Sensor):
    def __init__(self, Name: str = "CoreThermalSensor"):
        super().__init__(Name, SensorType.THERMAL, Unit="K", MinSafe=250.0, MaxSafe=2400.0)

    def ReadLogic(self) -> float:
        return 310.5

# Магнітний сенсор (напруженість захисних полів)
class MagneticSensor(Sensor):
    def __init__(self, Name: str = "DeflectorMagneticFlux"):
        super().__init__(Name, SensorType.MAGNETIC, Unit="Tesla", MinSafe=0.0, MaxSafe=500.0)

    def ReadLogic(self) -> float:
        return 45.2

# Радіаційний сенсор (космічне та реакторне випромінювання)
class RadiationSensor(Sensor):
    def __init__(self, Name: str = "RadiationDetector"):
        super().__init__(Name, SensorType.RADIATION, Unit="mSv/h", MinSafe=0.0, MaxSafe=5.0)

    def ReadLogic(self) -> float:
        return 0.08

# Структурний сенсор (механічне напруження перебірок корпусу)
class StructuralSensor(Sensor):
    def __init__(self, Name: str = "HullStressSensor"):
        super().__init__(Name, SensorType.STRUCTURAL, Unit="MicroStrain", MinSafe=0.0, MaxSafe=800.0)

    def ReadLogic(self) -> float:
        return 22.0

# ─── ГОЛОВНИЙ СЕНСОРНИЙ МАСИВ ЗОРЕЛЬОТА (SENSOR ARRAY) ─────────────────────────

class SensorArray(SystemComponent):
    Instance = None

    # Оптичні сигнали шини ODN-10
    ScanCompleted = Transmission(dict)
    AnomalyDetected = Transmission(str, dict)
    SensorMounted = Transmission(str)

    def __init__(self, Name: str = "Main Primary Sensory Array"):
        super().__init__()
        self.Name = Name
        self.Sensors: dict[str, Sensor] = {}
        self.Version = VersionInfo.GetVersion()
        self.SetupStandardSensoryGrid()

    @classmethod
    def GetInstance(cls) -> SensorArray:
        if cls.Instance is None:
            cls.Instance = SensorArray()
        return cls.Instance

    def SetupStandardSensoryGrid(self) -> None:
        self.MountSensor(TachyonSensor("LongRangeTachyon"))
        self.MountSensor(GravimetricSensor("GravimetricArray"))
        self.MountSensor(SubspaceSensor("SubspaceReceptor"))
        self.MountSensor(BioSensor("CrewBioScanner"))
        self.MountSensor(ThermalSensor("SystemThermal"))
        self.MountSensor(MagneticSensor("MagneticFlux"))
        self.MountSensor(RadiationSensor("RadiationMonitor"))
        self.MountSensor(StructuralSensor("HullIntegrityStress"))

    def MountSensor(self, SensorInstance: Sensor) -> None:
        self.Sensors[SensorInstance.Name] = SensorInstance
        self.SensorMounted.Emit(SensorInstance.Name)
        ODN.Transmit("ODN.Sensors.Mounted", SensorName=SensorInstance.Name, Category=SensorInstance.Category)

    def UnmountSensor(self, SensorName: str) -> bool:
        if SensorName in self.Sensors:
            del self.Sensors[SensorName]
            ODN.Transmit("ODN.Sensors.Unmounted", SensorName=SensorName)
            return True
        return False

    def GetSensor(self, Name: str) -> Sensor | None:
        return self.Sensors.get(Name)

    def ScanGrid(self) -> dict:
        SensoryData = {}
        WarningCount = 0

        for Name, SensorObj in self.Sensors.items():
            Reading = SensorObj.Read()
            SensoryData[Name] = Reading.ToDict()
            if not Reading.IsSafe:
                WarningCount += 1
                self.AnomalyDetected.Emit(Name, SensoryData[Name])
                ODN.Transmit("ODN.Sensors.Anomaly", Sensor=Name, Value=Reading.Value)

        self.ScanCompleted.Emit(SensoryData)
        ODN.Transmit("ODN.Sensors.ScanPulse", ActiveSensors=len(self.Sensors), Warnings=WarningCount)
        return SensoryData

    ReadAll = ScanGrid

    def GetSensorySnapshot(self) -> dict:
        return {
            "ArrayName": self.Name,
            "TotalSensorsCount": len(self.Sensors),
            "SensorsList": list(self.Sensors.keys()),
            "Version": self.Version,
        }

# Експорт контролера сенсорів
SensorArrayController = SensorArray.GetInstance
SensorGrid = SensorArray.GetInstance
SENSORARRAY = SensorArray.GetInstance()
