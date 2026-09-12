# ◤ TITANIUM TELEMETRY GRID & SYSTEM METRICS // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/telemetry.py
# ОПИС: Централізована телеметрична служба інженерного відсіку.
#       Зчитує системні метрики хост-системи (SystemMetrics), агрегує дані від
#       головного сенсорного масиву корабля (lcars.modules.sensor.SensorArray)
#       та фізичних інженерних підсистем (WarpCore, Deflector, LifeSupport, Repair).
#       Транслює зведений щосекундний пульс по оптичній шині ODN-10.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import SystemComponent, LCARS
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN, Transmission
from lcars.modules.sensor import SensorArray, ThermalSensor, MagneticSensor, StructuralSensor

# ─── 1. АДАПТЕР СИСТЕМНИХ МЕТРИК ХОСТА (SYSTEM METRICS) ───────────────────────

class SystemMetrics(SystemComponent):
    Instance = None

    def __init__(self):
        super().__init__()
        self.LastReadings: dict = {}

    @classmethod
    def GetInstance(cls) -> SystemMetrics:
        if cls.Instance is None:
            cls.Instance = SystemMetrics()
        return cls.Instance

    def GetCpuUsage(self) -> float:
        Psutil = getattr(LCARS.System, "Psutil", None)
        if Psutil and hasattr(Psutil, "cpu_percent"):
            Val = Psutil.cpu_percent(interval=None)
            if isinstance(Val, (int, float)):
                return float(Val)
        return 12.0

    def GetMemoryUsage(self) -> float:
        Psutil = getattr(LCARS.System, "Psutil", None)
        if Psutil and hasattr(Psutil, "virtual_memory"):
            Vm = Psutil.virtual_memory()
            Percent = getattr(Vm, "percent", None)
            if isinstance(Percent, (int, float)):
                return float(Percent)
        return 42.0

    def GetDiskUsage(self) -> float:
        Psutil = getattr(LCARS.System, "Psutil", None)
        if Psutil and hasattr(Psutil, "disk_usage"):
            Du = Psutil.disk_usage("C:\\")
            Percent = getattr(Du, "percent", None)
            if isinstance(Percent, (int, float)):
                return float(Percent)
        return 35.0

    def GetNetworkFlow(self) -> dict:
        Psutil = getattr(LCARS.System, "Psutil", None)
        SentMb = 0.0
        RecvMb = 0.0
        if Psutil and hasattr(Psutil, "net_io_counters"):
            Net = Psutil.net_io_counters()
            Sent = getattr(Net, "bytes_sent", None)
            Recv = getattr(Net, "bytes_recv", None)
            if isinstance(Sent, (int, float)) and isinstance(Recv, (int, float)):
                SentMb = round(Sent / (1024 * 1024), 2)
                RecvMb = round(Recv / (1024 * 1024), 2)
        return {"SentMb": SentMb, "RecvMb": RecvMb}

    def GetUptime(self) -> int:
        Psutil = getattr(LCARS.System, "Psutil", None)
        if Psutil and hasattr(Psutil, "boot_time"):
            Boot = Psutil.boot_time()
            if isinstance(Boot, (int, float)):
                Time = LCARS.System.Time
                Now = Time.time() if Time and hasattr(Time, "time") else 0.0
                return int(Now - Boot)
        return 3600

    def GetAllMetrics(self) -> dict:
        Time = LCARS.System.Time
        Now = Time.time() if Time and hasattr(Time, "time") else 0.0
        self.LastReadings = {
            "CpuPercent": self.GetCpuUsage(),
            "MemoryPercent": self.GetMemoryUsage(),
            "DiskPercent": self.GetDiskUsage(),
            "NetworkFlow": self.GetNetworkFlow(),
            "UptimeSeconds": self.GetUptime(),
            "Timestamp": Now,
        }
        return self.LastReadings

# ─── 2. АДАПТЕР ЗВЕДЕННЯ ТЕЛЕМЕТРІЇ (SENSORY ADAPTER) ─────────────────────────

class SensoryAdapter(LCARS):
    def __init__(self):
        super().__init__()
        self.Array = SensorArray.GetInstance()
        self.Metrics = SystemMetrics.GetInstance()
        self.LastPulseTime = 0.0

    def ReadSubsystemsTelemetry(self, Subsystems: dict | None = None) -> dict:
        Data = {
            "WarpCoreTempK": 300.0,
            "WarpFactor": 0.0,
            "MatterAntimatterRatio": 1.0,
            "ShieldLevelPercent": 0.0,
            "ShieldStatus": "OFFLINE",
            "OxygenLevelPercent": 20.9,
            "CarbonDioxidePercent": 0.04,
            "AtmosphericPressureKpa": 101.325,
            "LifeSupportDeckTempC": 21.5,
            "HullIntegrityPercent": 100.0,
            "ActiveHullBreaches": 0,
            "MountedIsolinearChips": 0,
            "OpticalConduitLatencyNs": 222.0,
        }

        if not Subsystems or not isinstance(Subsystems, dict):
            return Data

        # 1. Дані Варп-рушія
        Warp = Subsystems.get("WarpDrive")
        if Warp is not None:
            Factor = float(getattr(Warp, "WarpFactor", 0.0))
            Data["WarpFactor"] = Factor
            Data["WarpCoreTempK"] = round(300.0 + (Factor * 220.0), 1)
            Data["MatterAntimatterRatio"] = 1.0 if Factor < 9.0 else 1.05

        # 2. Дані Дефлектора та щитів
        Deflector = Subsystems.get("Deflector")
        if Deflector is not None:
            Data["ShieldLevelPercent"] = float(getattr(Deflector, "ShieldLevel", 0.0))
            Data["ShieldStatus"] = str(getattr(Deflector, "ShieldStatus", "ONLINE"))

        # 3. Дані Життєзабезпечення
        Life = Subsystems.get("LifeSupport")
        if Life is not None:
            Data["OxygenLevelPercent"] = float(getattr(Life, "OxygenLevelPercent", 20.9))
            Data["CarbonDioxidePercent"] = float(getattr(Life.Atmosphere, "CarbonDioxidePercent", 0.04)) if hasattr(Life, "Atmosphere") else 0.04
            Data["AtmosphericPressureKpa"] = float(getattr(Life, "AtmosphericPressureKpa", 101.325))
            Data["LifeSupportDeckTempC"] = float(getattr(Life, "DeckTemperatureC", 21.5))

        # 4. Дані Ремонтної служби корпусу
        Repair = Subsystems.get("Repair")
        if Repair is not None:
            Breaches = getattr(Repair, "Breaches", [])
            Data["ActiveHullBreaches"] = len(Breaches)
            Data["HullIntegrityPercent"] = max(0.0, 100.0 - (len(Breaches) * 15.0))

        # 5. Дані Ізолінійної матриці
        Isolinear = Subsystems.get("Isolinear")
        if Isolinear is not None and hasattr(Isolinear, "Bank"):
            Bank = Isolinear.Bank
            if Bank and hasattr(Bank, "Chips"):
                Data["MountedIsolinearChips"] = len(Bank.Chips)

        # 6. Дані Оптичного середовища
        Optical = Subsystems.get("Optical")
        if Optical is not None and hasattr(Optical, "DefaultConduit"):
            Conduit = Optical.DefaultConduit
            if Conduit and hasattr(Conduit, "LatencyNs"):
                Data["OpticalConduitLatencyNs"] = round(Conduit.LatencyNs, 3)

        return Data

    def ScanAllSensors(self, Subsystems: dict | None = None) -> dict:
        Time = LCARS.System.Time
        self.LastPulseTime = Time.time() if Time and hasattr(Time, "time") else 0.0

        SubData = self.ReadSubsystemsTelemetry(Subsystems)
        HostMetrics = self.Metrics.GetAllMetrics()
        SensorReadings = self.Array.ScanGrid()

        return {
            "Timestamp": self.LastPulseTime,
            **SubData,
            "HostCpuPercent": HostMetrics["CpuPercent"],
            "HostMemoryPercent": HostMetrics["MemoryPercent"],
            "HostDiskPercent": HostMetrics["DiskPercent"],
            "HostNetSentMb": HostMetrics["NetworkFlow"]["SentMb"],
            "HostNetRecvMb": HostMetrics["NetworkFlow"]["RecvMb"],
            "HostUptimeSeconds": HostMetrics["UptimeSeconds"],
            "PhysicalSensors": SensorReadings,
        }

# ─── 3. ГОЛОВНА ТЕЛЕМЕТРИЧНА СІТКА (TELEMETRY GRID) ───────────────────────────

class TelemetryGrid(SystemComponent):
    Instance = None

    # Оптичні сигнали шини ODN-10
    StreamEvent = Transmission(str, str, str)
    PulseBroadcast = Transmission(dict)

    def __init__(self):
        super().__init__()
        self.Sensory = SensoryAdapter()
        self.SubsystemsRef: dict = {}
        self.Listeners: list = []
        self.Version = VersionInfo.GetVersion()

    @classmethod
    def GetInstance(cls) -> TelemetryGrid:
        if cls.Instance is None:
            cls.Instance = TelemetryGrid()
        return cls.Instance

    def AttachSubsystems(self, Subsystems: dict) -> None:
        self.SubsystemsRef = Subsystems
        if "WarpDrive" in Subsystems:
            self.Sensory.Array.MountSensor(ThermalSensor("WarpCoreThermal"))
        if "Deflector" in Subsystems:
            self.Sensory.Array.MountSensor(MagneticSensor("DeflectorFlux"))
        if "Repair" in Subsystems:
            self.Sensory.Array.MountSensor(StructuralSensor("HullMicrostrain"))

    def GetCurrentData(self) -> dict:
        return self.Sensory.ScanAllSensors(self.SubsystemsRef)

    def Sensor(self) -> dict:
        return self.GetCurrentData()

    def EmitPulse(self) -> dict:
        Data = self.GetCurrentData()
        self.PulseBroadcast.Emit(Data)
        ODN.Transmit("Engineering.Telemetry.Pulse", Cpu=Data.get("HostCpuPercent"), WarpFactor=Data.get("WarpFactor"))
        return Data

    def AddListener(self, CallbackFunc: any) -> None:
        if CallbackFunc not in self.Listeners:
            self.Listeners.append(CallbackFunc)

    def RemoveListener(self, CallbackFunc: any) -> None:
        if CallbackFunc in self.Listeners:
            self.Listeners.remove(CallbackFunc)

    def Emit(self, Source: str, Message: str, Level: str = "info") -> None:
        self.StreamEvent.Emit(Source, Level, Message)
        for Listener in self.Listeners:
            if callable(Listener):
                Listener(Source, Message, Level)
        ODN.Transmit("Engineering.Telemetry.Event", Source=Source, Message=Message, Level=Level)

    def GetStatus(self) -> dict:
        Latest = self.GetCurrentData()
        return {
            "SubsystemsAttached": len(self.SubsystemsRef),
            "SensorsCount": len(self.Sensory.Array.Sensors),
            "ListenersCount": len(self.Listeners),
            "Version": self.Version,
            "LatestSnapshot": Latest,
        }

# ─── 4. КАНОНІЧНИЙ ЕКСПОРТ ТЕЛЕМЕТРІЇ ──────────────────────────────────────────

GetTelemetryGrid = TelemetryGrid.GetInstance

def EmitTelemetry(Source: str, Message: str, Level: str = "info") -> None:
    TelemetryGrid.GetInstance().Emit(Source, Message, Level)

TELEMETRYGRID = TelemetryGrid.GetInstance()
