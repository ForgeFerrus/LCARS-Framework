# ◤ LCARS ENGINEERING :: CENTRAL DATA & CORE COLLECTOR 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/collector.py
# ОПИС: Централізований Інженерний Колектор зорельота.
#       Поєднує два взаємопов'язані аспекти:
#       1. Фізичний збір:
#          - BussardCollector (колектор Бассарда для збору міжзоряного водню/дейтерію)
#          - CorePlasmaTap (відбір високоенергетичної плазми з варп-ядра для EPS)
#       2. Системний збір телеметрії:
#          - Агрегація метрик варп-ядра (WarpDrive), дефлектора (DeflectorShield),
#            життєзабезпечення (LifeSupport), сенсорної сітки (TelemetryGrid)
#            та ізолінійних чіпів (IsolinearBank).
#          - Обчислення інтегрального здоров'я корабля (NOMINAL / WARNING / CRITICAL).
#          - Трансляція зведеного пульсу через Transmission та ODN.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================
from __future__ import annotations
# Titanium Bridge Migration: from typing import Any, Callable
from lcars.base.type import SystemComponent, LCARS
from lcars.core.signal import Transmission, ODN
# =============================================================================
# 1. ФІЗИЧНІ КОЛЕКТОРИ (BUSSARD RAMSCOOP ТА CORE PLASMA TAP)
# =============================================================================
# Колектор Бассарда (Bussard Ramscoop).
# Встановлений на передніх закінченнях варп-гондол для всмоктування
# міжзоряного водню, дейтерію та плазми для поповнення паливних баків.
class BussardCollector(SystemComponent):
    def __init__(self, SystemId: str = "Engineering.Collector.Bussard"):
        super().__init__(SystemId=SystemId)
        self.Active = True
        self.MagneticFieldStrength = 100.0
        self.IntakeRateKgS = 0.48
        self.Efficiency = 94.5
        self.DeuteriumTankLevel = 85.0
        self.ParticleFilterStatus = "CLEAN"

    # Регулювання інтенсивності всмоктування газу
    def SetIntake(self, RateKgS: float) -> float:
        self.IntakeRateKgS = max(0.0, float(RateKgS))
        return self.IntakeRateKgS

    # Регулювання потужності магнітного поля конуса
    def SetMagneticField(self, Percent: float) -> float:
        self.MagneticFieldStrength = max(0.0, min(100.0, float(Percent)))
        self.Efficiency = 94.5 * (self.MagneticFieldStrength / 100.0)
        return self.MagneticFieldStrength

    # Продувка колектора від накопичених космічних мікрочасток
    def Purge(self) -> str:
        self.ParticleFilterStatus = "PURGED_OPTIMAL"
        return self.ParticleFilterStatus

    def GetStatus(self) -> dict:
        return {
            "Active": self.Active,
            "MagneticField": self.MagneticFieldStrength,
            "IntakeRateKgS": self.IntakeRateKgS,
            "Efficiency": round(self.Efficiency, 2),
            "DeuteriumTank": self.DeuteriumTankLevel,
            "FilterStatus": self.ParticleFilterStatus,
        }
# Колектор відбору електроплазми варп-ядра (Core Plasma Tap).
# Відбирає високоенергетичну плазму безпосередньо з реактора антиматерії
# та розподіляє її по магістралях електроплазмової системи (EPS).
class CorePlasmaTap(SystemComponent):
    def __init__(self, SystemId: str = "Engineering.Collector.PlasmaTap"):
        super().__init__(SystemId=SystemId)
        self.Active = True
        self.TappingRateMwf = 1250.0
        self.ManifoldPressure = 98.6
        self.PlasmaCoolantLevel = 100.0
        self.PlasmaInjectorSync = 99.8

    # Регулювання потоку відбору плазми
    def RegulateFlow(self, TargetMwf: float) -> float:
        self.TappingRateMwf = max(0.0, float(TargetMwf))
        return self.TappingRateMwf

    # Аварійне перекриття відбору плазми від ядра
    def EmergencyScram(self) -> str:
        self.Active = False
        self.TappingRateMwf = 0.0
        self.ManifoldPressure = 0.0
        return "PLASMA_TAP_ISOLATED"

    def GetStatus(self) -> dict:
        return {
            "Active": self.Active,
            "FlowRateMwf": self.TappingRateMwf,
            "ManifoldPressure": self.ManifoldPressure,
            "CoolantLevel": self.PlasmaCoolantLevel,
            "InjectorSync": self.PlasmaInjectorSync,
        }
# =============================================================================
# 2. ГОЛОВНИЙ ІНЖЕНЕРНИЙ КОЛЕКТОР (ENGINEERING CENTRAL COLLECTOR)
# =============================================================================
# Головний інженерний агрегатор зорельота.
# Збирає фізичні та програмні метрики всіх систем корабля в єдину картину.
class CollectorCore(SystemComponent):
    PulseSignal = Transmission(dict)
    AlertSignal = Transmission(str, str)

    def __init__(self, SystemId: str = "Engineering.Collector"):
        super().__init__(SystemId=SystemId)
        self.CollectorId = SystemId

        # Фізичні вузли збору
        self.Bussard = BussardCollector()
        self.PlasmaTap = CorePlasmaTap()

        # Підключені корабельні вузли
        self.EngineeringNode = None
        self.WarpNode = None
        self.DeflectorNode = None
        self.LifeSupportNode = None
        self.TelemetryNode = None
        self.IsolinearNode = None
        self.SystemNode = None

        # Останній збережений зріз метрик
        self.LastSnapshot = {}

    # Автоматичне підключення інженерних вузлів із переданого словника
    def AutoAttach(self, Nodes: dict) -> int:
        Count = 0
        if not isinstance(Nodes, dict):
            return 0

        if "WarpDrive" in Nodes or "warp" in Nodes:
            self.WarpNode = Nodes.get("WarpDrive") or Nodes.get("warp")
            Count += 1

        if "Deflector" in Nodes or "deflector" in Nodes:
            self.DeflectorNode = Nodes.get("Deflector") or Nodes.get("deflector")
            Count += 1

        if "Maintenance" in Nodes or "maintenance" in Nodes:
            self.LifeSupportNode = Nodes.get("Maintenance") or Nodes.get("maintenance")
            Count += 1
        elif "LifeSupport" in Nodes or "life_support" in Nodes:
            self.LifeSupportNode = Nodes.get("LifeSupport") or Nodes.get("life_support")
            Count += 1

        if "Telemetry" in Nodes or "telemetry" in Nodes:
            self.TelemetryNode = Nodes.get("Telemetry") or Nodes.get("telemetry")
            Count += 1

        if "Isolinear" in Nodes or "isolinear" in Nodes:
            self.IsolinearNode = Nodes.get("Isolinear") or Nodes.get("isolinear")
            Count += 1

        self.EngineeringNode = Nodes
        return Count

    def AttachEngineering(self, SensorsNode) -> bool:
        self.EngineeringNode = SensorsNode
        return True

    def AttachModules(self, ModulesNode) -> bool:
        self.TelemetryNode = ModulesNode
        return True

    def AttachSystem(self, MasterNode) -> bool:
        self.SystemNode = MasterNode
        return True

    # Опитування варп-ядра, плазми та EPS
    def PollWarpCore(self) -> dict:
        Node = self.WarpNode
        if not Node and isinstance(self.EngineeringNode, dict):
            Node = self.EngineeringNode.get("WarpDrive")

        if Node and hasattr(Node, "GetStatus"):
            Status = Node.GetStatus()
            if isinstance(Status, dict):
                return Status

        return {
            "CoreStability": 100.0,
            "PlasmaFlow": 0.0,
            "WarpFactor": 0.0,
            "Dilithium": 100.0,
            "Status": "STANDBY",
        }

    # Опитування щитів, дефлектора та тактичних загроз
    def PollShields(self) -> dict:
        Node = self.DeflectorNode
        if not Node and isinstance(self.EngineeringNode, dict):
            Node = self.EngineeringNode.get("Deflector")

        if Node and hasattr(Node, "GetStatus"):
            Status = Node.GetStatus()
            if isinstance(Status, dict):
                return Status

        return {
            "ShieldLevel": 100.0,
            "ShieldStatus": "ONLINE",
            "ThreatCount": 0,
        }

    # Опитування життєзабезпечення та цілісності структури
    def PollLifeSupport(self) -> dict:
        Node = self.LifeSupportNode
        if not Node and isinstance(self.EngineeringNode, dict):
            Node = self.EngineeringNode.get("Maintenance") or self.EngineeringNode.get("Repair")

        if Node and hasattr(Node, "GetStatus"):
            Status = Node.GetStatus()
            if isinstance(Status, dict):
                return Status

        return {
            "StructureValid": True,
            "IsCritical": False,
            "IsEmergency": False,
        }

    # Опитування сенсорної сітки та апаратних ресурсів
    def PollSensory(self) -> dict:
        Node = self.TelemetryNode
        if not Node and isinstance(self.EngineeringNode, dict):
            Node = self.EngineeringNode.get("Telemetry")

        if Node:
            if hasattr(Node, "Sensor") and callable(Node.Sensor):
                Data = Node.Sensor()
                if isinstance(Data, dict):
                    return Data
            if hasattr(Node, "Metrics") and callable(Node.Metrics):
                Data = Node.Metrics()
                if isinstance(Data, dict):
                    return Data

        return {
            "SystemLoad": 15.0,
            "MemoryUsage": 42.0,
            "CoreTemp": 300.0,
            "IsolinearIntegrity": 100.0,
        }

    # Опитування ізолінійної мережі чіпів
    def PollIsolinear(self) -> dict:
        Node = self.IsolinearNode
        if not Node and isinstance(self.EngineeringNode, dict):
            Node = self.EngineeringNode.get("Isolinear")

        if Node:
            if hasattr(Node, "ClusterStatus") and callable(Node.ClusterStatus):
                Status = Node.ClusterStatus()
                if isinstance(Status, dict):
                    return Status
            if hasattr(Node, "Chips"):
                ChipsDict = getattr(Node, "Chips", {})
                return {
                    "TotalMounted": len(ChipsDict),
                    "Status": "MOUNTED_ONLINE",
                }

        return {
            "TotalMounted": 32,
            "Status": "NOMINAL",
        }
    # Комплексна оцінка інтегрального здоров'я зорельота
    # NOMINAL  - зелений (усі життєві показники в нормі)
    # WARNING  - жовтий (зниження ефективності, перевантаження або загрози)
    # CRITICAL - червоний (пробій щита, аварія життєзабезпечення, критичний перегрів)
    def CalculateHealth(self) -> str:
        Warp = self.PollWarpCore()
        Shields = self.PollShields()
        Life = self.PollLifeSupport()
        Sensors = self.PollSensory()

        # 1. Перевірка критичних станів
        if Life.get("IsEmergency") or Life.get("IsCritical"):
            return "CRITICAL"

        CoreStability = float(Warp.get("CoreStability", 100.0))
        if CoreStability < 30.0:
            return "CRITICAL"

        ShieldLevel = float(Shields.get("ShieldLevel", 100.0))
        ThreatCount = int(Shields.get("ThreatCount", 0))
        if ShieldLevel == 0.0 and ThreatCount > 0:
            return "CRITICAL"

        SystemLoad = float(Sensors.get("SystemLoad", Sensors.get("CPU", 0.0)))
        if SystemLoad > 92.0:
            return "CRITICAL"

        # 2. Перевірка попереджувальних станів
        if CoreStability < 75.0 or ShieldLevel < 60.0 or ThreatCount > 0:
            return "WARNING"

        MemoryUsage = float(Sensors.get("MemoryUsage", Sensors.get("Mem", 0.0)))
        if SystemLoad > 70.0 or MemoryUsage > 75.0:
            return "WARNING"

        if not Life.get("StructureValid", True):
            return "WARNING"

        return "NOMINAL"

    # Властивість інтегрального здоров'я корабля
    @property
    def HealthStatus(self) -> str:
        return self.CalculateHealth()

    # Знімає повний комплексний знімок інженерного відсіку
    def PollAll(self) -> dict:
        WarpData = self.PollWarpCore()
        ShieldData = self.PollShields()
        LifeData = self.PollLifeSupport()
        SensoryData = self.PollSensory()
        IsolinearData = self.PollIsolinear()
        BussardData = self.Bussard.GetStatus()
        PlasmaData = self.PlasmaTap.GetStatus()

        Health = self.CalculateHealth()

        DateTimeModule = getattr(LCARS.System, "DateTime", None)
        Timestamp = DateTimeModule.now().timestamp() if (DateTimeModule and hasattr(DateTimeModule, "now")) else 0.0

        Snapshot = {
            "CollectorId": self.CollectorId,
            "Timestamp": Timestamp,
            "HealthStatus": Health,
            "Bussard": BussardData,
            "PlasmaTap": PlasmaData,
            "WarpCore": WarpData,
            "Shields": ShieldData,
            "LifeSupport": LifeData,
            "Sensory": SensoryData,
            "Isolinear": IsolinearData,
            "Eng": {
                "CPU": SensoryData.get("SystemLoad", 15.0),
                "Mem": SensoryData.get("MemoryUsage", 42.0),
                "Hull": 100.0 if LifeData.get("StructureValid", True) else 80.0,
            },
            "Status": Health,
        }

        self.LastSnapshot = Snapshot

        # Трансляція через локальний сигнал та глобальну ODN
        self.PulseSignal.Emit(Snapshot)
        ODN.Transmit("Engineering.Collector.Pulse", Health=Health, Load=SensoryData.get("SystemLoad", 15.0))

        if Health == "CRITICAL":
            self.AlertSignal.Emit("CRITICAL_ALERT", "Collector detected vessel critical threshold")
            ODN.Transmit("Engineering.Alert.Critical", Reason="Collector anomaly threshold")

        return Snapshot

    # Повертає актуальний або щойно зібраний знімок
    def GetAll(self) -> dict:
        if not self.LastSnapshot:
            return self.PollAll()
        return dict(self.LastSnapshot)

    # Статус самого колектора для SystemComponent сумісності
    def GetStatus(self) -> dict:
        return {
            "SystemId": self.CollectorId,
            "CollectorReady": True,
            "HealthStatus": self.HealthStatus,
            "BussardActive": self.Bussard.Active,
            "PlasmaTapActive": self.PlasmaTap.Active,
            "AttachedNodes": {
                "Warp": self.WarpNode is not None,
                "Shields": self.DeflectorNode is not None,
                "LifeSupport": self.LifeSupportNode is not None,
                "Telemetry": self.TelemetryNode is not None,
                "Isolinear": self.IsolinearNode is not None,
            }
        }

    # Підписка слухача на зведені метрики
    def ConnectMetrics(self, Listener) -> None:
        if callable(Listener):
            self.PulseSignal.Connect(Listener)

    # Відписка слухача від зведених метрик
    def DisconnectMetrics(self, Listener) -> None:
        if callable(Listener):
            self.PulseSignal.Disconnect(Listener)
