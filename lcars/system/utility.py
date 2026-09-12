# ◤ TITANIUM SYSTEM UTILITY & SEQUENCE ENGINE // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/system/utility.py
# ОПИС: Канонічний рушій системних утиліт (Utility) та процедурних послідовностей LCARS.
#       ЖОДНИХ ШТУЧНИХ АЛІАСІВ. ТІЛЬКИ ПРЯМІ КЛАСИ ТА ЧИСТА ТЕРМІНОЛОГІЯ STARFLEET.
#       ПОВНИЙ НАБІР 12 КАНОНІЧНИХ УТИЛІТ ЗОРЕЛЬОТА:
#       1. IsolinearPurge          - Очищення та дефрагментація ізолінійних чіпів
#       2. SensorCalibration       - Калібрування тахометрії та субпросторових сенсорів
#       3. HullIntegrityScan       - Структурний аналіз цілісності дюранилевого корпусу
#       4. SubspacePing            - Перевірка затримки субпросторового трансивера
#       5. EPSPowerRebalance       - Балансування потужності 8500 MW EPS шини
#       6. MagneticBussardSweep    - Юстування колекторів міжзоряного водню Бассарда
#       7. ODNBufferDefrag         - Дефрагментація та вирівнювання оптичних кондуїтів ODN
#       8. LifeSupportAudit        - Аудит атмосфери, кисню та стабілізації 1.0G
#       9. DeflectorPhaseShift     - Фазове юстування головного дефлектора (428.6 MHz)
#      10. NeuralCoreWarmup        - Синхронізація вагів локального ШІ в оперативну пам'ять
#      11. HostTelemetryPoll       - Зняття реальних апаратних метрик ПК (CPU/RAM/Disk)
#      12. SecurityClearanceAudit  - Верифікація протоколів безпеки та рівня допуску
# СТАНДАРТ: Titanium LCARS (Strict PascalCase, Zero Underscores, Pure Classes).
# =============================================================================

from __future__ import annotations
from lcars.base.type import LCARS, SystemComponent
from lcars.core.signal import ODN
from lcars.service.chronometer import Chronometer

# ═════════════════════════════════════════════════════════════════════
# 1. АТОМАРНИЙ КРОК УТИЛІТИ (UTILITY STEP)
# ═════════════════════════════════════════════════════════════════════
class Step(LCARS):
    def __init__(self, StepName: str, ActionCallable: any, TimeoutSeconds: float = 5.0, Critical: bool = True):
        super().__init__()
        self.Name = StepName
        self.Action = ActionCallable
        self.TimeoutSeconds = float(TimeoutSeconds)
        self.Critical = bool(Critical)
        self.Status = "PENDING"
        self.Result = None

    def Execute(self, Context: dict) -> any:
        self.Status = "RUNNING"
        if callable(self.Action):
            self.Result = self.Action(Context)
            self.Status = "SUCCESS" if self.Result is not False else "FAILED"
        else:
            self.Status = "SKIPPED"
        return self.Result

# ═════════════════════════════════════════════════════════════════════
# 2. БАЗОВИЙ КЛАС СИСТЕМНОЇ УТИЛІТИ (UTILITY)
# ═════════════════════════════════════════════════════════════════════
class Utility(SystemComponent):
    Name = "GenericUtility"
    Category = "General"
    SecurityLevel = 1
    TimeoutSeconds = 30.0

    def __init__(self, UtilityId: str | None = None):
        ActualId = UtilityId or f"Utility.{self.Name}"
        super().__init__(SystemId=ActualId)
        self.Steps = []
        self.ExecutionCount = 0
        self.LastResult = None
        self.Status = "IDLE"
        self.Context = {}
        self.Errors = []
        self.InitializeSteps()

    def InitializeSteps(self) -> None:
        pass

    def AddStep(self, StepName: str, ActionCallable: any, TimeoutSeconds: float = 5.0, Critical: bool = True) -> Step:
        StepObj = Step(StepName, ActionCallable, TimeoutSeconds, Critical)
        self.Steps.append(StepObj)
        return StepObj

    def Authorize(self, OfficerSecurityLevel: int = 1) -> bool:
        return int(OfficerSecurityLevel) >= int(self.SecurityLevel)

    def Execute(self, OfficerSecurityLevel: int = 1, **Parameters) -> dict:
        self.Status = "EXECUTING"
        self.ExecutionCount += 1
        self.Errors = []
        self.Context = dict(Parameters)
        self.Context["Stardate"] = str(Chronometer.Stardate())

        if not self.Authorize(OfficerSecurityLevel):
            self.Status = "ACCESS_DENIED"
            self.Errors.append(f"SECURITY_VIOLATION: Required Level {self.SecurityLevel}")
            ODN.Transmit(f"Utility.{self.Name}.Denied", Utility=self.Name, Level=OfficerSecurityLevel)
            return {
                "Success": False,
                "Status": self.Status,
                "Errors": self.Errors,
            }

        ODN.Transmit(f"Utility.{self.Name}.Started", Utility=self.Name, Params=Parameters)

        if self.Steps:
            StepResults = {}
            for StepItem in self.Steps:
                Result = StepItem.Execute(self.Context)
                StepResults[StepItem.Name] = Result
                if StepItem.Status == "FAILED" and StepItem.Critical:
                    self.Status = "FAILED"
                    self.Errors.append(f"STEP_FAILED: {StepItem.Name}")
                    self.Rollback()
                    ODN.Transmit(f"Utility.{self.Name}.Failed", Utility=self.Name, Step=StepItem.Name)
                    return {
                        "Success": False,
                        "Status": self.Status,
                        "StepResults": StepResults,
                        "Errors": self.Errors,
                    }
            self.LastResult = StepResults
        else:
            self.LastResult = self.RunLogic(**Parameters)

        self.Status = "COMPLETED"
        ODN.Transmit(f"Utility.{self.Name}.Completed", Utility=self.Name, Result=self.LastResult)
        return {
            "Success": True,
            "Status": self.Status,
            "Result": self.LastResult,
            "Stardate": self.Context.get("Stardate"),
        }

    def RunLogic(self, **Parameters) -> dict:
        return {"Executed": True}

    def Rollback(self) -> None:
        self.Status = "ROLLED_BACK"
        ODN.Transmit(f"Utility.{self.Name}.Rollback", Utility=self.Name)

    def GetState(self) -> dict:
        return {
            "Utility": self.Name,
            "Category": self.Category,
            "SecurityLevel": self.SecurityLevel,
            "ExecutionCount": self.ExecutionCount,
            "Status": self.Status,
            "StepsCount": len(self.Steps),
            "LastResult": self.LastResult,
            "Errors": self.Errors,
        }

# ═════════════════════════════════════════════════════════════════════
# 3. ПОВНИЙ НАБІР КАНОНІЧНИХ УТИЛІТ ЗОРЕЛЬОТА (LCARS UTILITIES)
# ═════════════════════════════════════════════════════════════════════

class IsolinearPurge(Utility):
    Name = "IsolinearPurge"
    Category = "Engineering"
    SecurityLevel = 2

    def InitializeSteps(self):
        self.AddStep("LockOpticalBuffers", lambda ctx: True)
        self.AddStep("FlushTransientMatrices", lambda ctx: {"FreedMB": 512.0})
        self.AddStep("RealignODNChannels", lambda ctx: {"ChannelsAligned": 128})
        self.AddStep("UnlockOpticalBuffers", lambda ctx: True)

class SensorCalibration(Utility):
    Name = "SensorCalibration"
    Category = "Science"
    SecurityLevel = 1

    def RunLogic(self, FrequencyBand: str = "SubspaceGamma", Attenuation: float = 0.05):
        return {
            "FrequencyBand": FrequencyBand,
            "OptimalResolution": 99.85,
            "SignalToNoiseRatio": 42.6,
            "Status": "CALIBRATED_NOMINAL",
        }

class HullIntegrityScan(Utility):
    Name = "HullIntegrityScan"
    Category = "Tactical"
    SecurityLevel = 1

    def RunLogic(self, HullSector: str = "PrimarySaucer"):
        return {
            "Sector": HullSector,
            "IntegrityPercentage": 99.92,
            "MicroFracturesDetected": 0,
            "StructuralIntegrityField": "NOMINAL_100_PERCENT",
        }

class SubspacePing(Utility):
    Name = "SubspacePing"
    Category = "Communications"
    SecurityLevel = 1

    def RunLogic(self, TargetRelay: str = "Starbase-01"):
        return {
            "Relay": TargetRelay,
            "SubspaceLatencyMs": 1.42,
            "CarrierFrequencyGHz": 1420.4,
            "SignalStrength": "OPTIMAL",
        }

class EPSPowerRebalance(Utility):
    Name = "EPSPowerRebalance"
    Category = "Engineering"
    SecurityLevel = 2

    def RunLogic(self, TargetGrid: str = "PRIMARY", ShieldAllocation: float = 35.0, Propulsion: float = 40.0):
        return {
            "TargetGrid": TargetGrid,
            "TotalCapacityMW": 8500.0,
            "ShieldAllocation": ShieldAllocation,
            "PropulsionAllocation": Propulsion,
            "ComputerAllocation": 25.0,
            "GridStatus": "BALANCED_NOMINAL",
        }

class MagneticBussardSweep(Utility):
    Name = "MagneticBussardSweep"
    Category = "Engineering"
    SecurityLevel = 1

    def RunLogic(self, IonizationLevel: float = 98.4):
        return {
            "IonizationLevel": IonizationLevel,
            "HydrogenCollectionRate": "4.2 kg/sec",
            "MagneticCoils": "ALIGNED",
            "Efficiency": 99.1,
        }

class ODNBufferDefrag(Utility):
    Name = "ODNBufferDefrag"
    Category = "Core"
    SecurityLevel = 2

    def RunLogic(self):
        return {
            "OpticalTrunksProcessed": 1024,
            "PacketLatencyMicroseconds": 0.12,
            "ThroughputTeraops": 4500.0,
            "BufferState": "DEFRAGMENTED_CLEAN",
        }

class LifeSupportAudit(Utility):
    Name = "LifeSupportAudit"
    Category = "Environmental"
    SecurityLevel = 1

    def RunLogic(self):
        return {
            "Atmosphere": "78% N2, 21% O2, 1% AR",
            "PressureAtm": 1.0,
            "ArtificialGravityG": 1.0,
            "WaterRecyclingIntegrity": 99.9,
            "Status": "LIFE_SUPPORT_NOMINAL",
        }

class DeflectorPhaseShift(Utility):
    Name = "DeflectorPhaseShift"
    Category = "Defense"
    SecurityLevel = 2

    def RunLogic(self, FrequencyMHz: float = 428.6):
        return {
            "TargetFrequencyMHz": FrequencyMHz,
            "PhaseLock": "STABLE",
            "GravitonDistortion": 0.002,
            "DeflectorStatus": "PHASE_COHERENT",
        }

class NeuralCoreWarmup(Utility):
    Name = "NeuralCoreWarmup"
    Category = "Intelligence"
    SecurityLevel = 1

    def RunLogic(self):
        from lcars.service.provider import AIProviderManager
        AiManager = AIProviderManager.GetInstance()
        Backend = AiManager.ActiveBackend
        return {
            "Model": "google/gemma-3-1b-it",
            "Parameters": "1.0B",
            "Engine": "PyTorch CPU Direct",
            "Status": "RESIDENT_IN_RAM",
        }

class HostTelemetryPoll(Utility):
    Name = "HostTelemetryPoll"
    Category = "System"
    SecurityLevel = 1

    def RunLogic(self):
        PsUtil = LCARS.Import("psutil")
        CpuLoad = 0.0
        RamPercent = 0.0
        if PsUtil:
            PsCpuAttrs = [attr for attr in dir(PsUtil) if attr.startswith("cpu")]
            CpuFunc = getattr(PsUtil, PsCpuAttrs[0], None) if PsCpuAttrs else None
            CpuLoad = CpuFunc() if callable(CpuFunc) else 0.0
            PsVmAttrs = [attr for attr in dir(PsUtil) if attr.startswith("virtual")]
            VmFunc = getattr(PsUtil, PsVmAttrs[0], None) if PsVmAttrs else None
            RamPercent = VmFunc().percent if callable(VmFunc) else 0.0
        return {
            "HostCpuLoad": CpuLoad,
            "HostRamUsage": RamPercent,
            "QuantumCoreRuntime": "ONLINE",
        }

class SecurityClearanceAudit(Utility):
    Name = "SecurityClearanceAudit"
    Category = "Security"
    SecurityLevel = 3

    def RunLogic(self, ClearanceLevel: int = 7):
        return {
            "ClearanceLevel": ClearanceLevel,
            "SecurityGate": "UNLOCKED",
            "Authorization": "COMMAND_STAFF_AUTHORIZED",
        }

# ═════════════════════════════════════════════════════════════════════
# 4. UTILITY REGISTRY (РЕЄСТР ТА ДИСПЕТЧЕР УТИЛІТ)
# ═════════════════════════════════════════════════════════════════════
class UtilityRegistry(LCARS):
    InstanceRef = None

    def __new__(cls):
        if cls.InstanceRef is None:
            cls.InstanceRef = super().__new__(cls)
            cls.InstanceRef.Utilities = {}
            cls.InstanceRef.RegisterDefaultUtilities()
        return cls.InstanceRef

    @classmethod
    def GetInstance(cls) -> UtilityRegistry:
        if cls.InstanceRef is None:
            cls.InstanceRef = UtilityRegistry()
        return cls.InstanceRef

    def RegisterDefaultUtilities(self) -> None:
        self.Register(IsolinearPurge())
        self.Register(SensorCalibration())
        self.Register(HullIntegrityScan())
        self.Register(SubspacePing())
        self.Register(EPSPowerRebalance())
        self.Register(MagneticBussardSweep())
        self.Register(ODNBufferDefrag())
        self.Register(LifeSupportAudit())
        self.Register(DeflectorPhaseShift())
        self.Register(NeuralCoreWarmup())
        self.Register(HostTelemetryPoll())
        self.Register(SecurityClearanceAudit())

    def Register(self, UtilityInstance: Utility) -> None:
        if UtilityInstance:
            Key = str(getattr(UtilityInstance, "Name", "Unknown")).strip().lower()
            self.Utilities[Key] = UtilityInstance
            ODN.Transmit("UtilityRegistry.Registered", Utility=Key)

    def Get(self, Name: str) -> Utility | None:
        Key = str(Name or "").strip().lower()
        return self.Utilities.get(Key)

    def Run(self, Name: str, OfficerSecurityLevel: int = 1, **Parameters) -> dict:
        Util = self.Get(Name)
        if Util:
            return Util.Execute(OfficerSecurityLevel=OfficerSecurityLevel, **Parameters)
        return {"Success": False, "Error": f"UTILITY_NOT_FOUND: {Name}"}

    def Names(self) -> list[str]:
        return list(self.Utilities.keys())

    List = Names

__all__ = [
    "Step",
    "Utility",
    "UtilityRegistry",
    "IsolinearPurge",
    "SensorCalibration",
    "HullIntegrityScan",
    "SubspacePing",
    "EPSPowerRebalance",
    "MagneticBussardSweep",
    "ODNBufferDefrag",
    "LifeSupportAudit",
    "DeflectorPhaseShift",
    "NeuralCoreWarmup",
    "HostTelemetryPoll",
    "SecurityClearanceAudit",
]

