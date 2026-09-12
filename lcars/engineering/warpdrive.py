# ◤ TITANIUM STARFLEET WARP DRIVE, PROPULSION & WARP CORE SUITE 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/warpdrive.py
# ОПИС: Повний канонічний інженерний комплекс надсвітлового та субсвітлового руху.
#       Об'єднує всі фізичні вузли та інструментарій зорельота:
#       1. Математику Кокрана (CochraneCalculator): напруженість поля, швидкість у c,
#          коефіцієнт стиснення метрики простору та енергетичні витрати.
#       2. Магнітні звужувачі (MagneticConstrictor): 12 сегментів фокусування антиматерії.
#       3. Артикуляційну раму дилітію (DilithiumArticulation): кут нахилу, резонанс 42 Гц.
#       4. Інжектори суміші (MatterAntimatterInjector): мікроімпульси калібрування 1:1.
#       5. Мережу плазмових реле (PlasmaRelayGrid): 8 реле EPS та аварійні клапани скидання.
#       6. Фазування варп-котушок (WarpCoilPhasing): 36 котушок, кути фаз 0-360 deg, перистальтична хвиля.
#       7. Фізичне варп-ядро (WarpCore): реактор, піропатрони катапультування ядра, геометрія Geant4.
#       8. Субсвітло та маневри (ImpulseDrive, ThrusterSystem).
#       9. Електроплазмову шину (EPSConduit) та Головний контролер (WarpDrive).
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================
from __future__ import annotations
from lcars.base.type import SystemComponent, LCARS
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN, Transmission

# ─── 1. МАТЕМАТИЧНИЙ МОДУЛЬ КОКРАНА (COCHRANE CALCULATOR) ─────────────────────
class CochraneCalculator(LCARS):
    @classmethod
    def CalculateSpeed(cls, WarpFactor: float) -> float:
        Factor = max(0.0, min(9.99, float(WarpFactor)))
        if Factor == 0.0:
            return 0.0
        if Factor < 9.0:
            return round(Factor ** (10.0 / 3.0), 3)
        Exponent = (10.0 / 3.0) + ((Factor - 9.0) * 2.8)
        return round(Factor ** Exponent, 3)

    @classmethod
    def CalculateCochranes(cls, WarpFactor: float) -> float:
        return cls.CalculateSpeed(WarpFactor)

    @classmethod
    def CalculateCompression(cls, WarpFactor: float) -> float:
        Cochranes = cls.CalculateCochranes(WarpFactor)
        return round(1.0 + (Cochranes * 0.085), 3)

    @classmethod
    def CalculatePowerMw(cls, WarpFactor: float) -> float:
        Factor = max(0.0, min(9.99, float(WarpFactor)))
        if Factor == 0.0:
            return 50.0
        return round(120.0 * (Factor ** 1.85), 1)

# ─── 2. МАГНІТНІ ЗВУЖУВАЧІ АНТИМАТЕРІЇ (MAGNETIC CONSTRICTOR) ─────────────────
class MagneticConstrictor(SystemComponent):
    def __init__(self, SegmentCount: int = 12):
        super().__init__()
        self.SegmentCount = int(SegmentCount)
        self.ConfinementLevel = 99.998
        self.MagneticFieldTesla = 48.5
        self.ConstrictorSegments: list[float] = [100.0 for i in range(self.SegmentCount)]
        self.StreamAligned = True

    def AdjustConfinement(self, TargetPercent: float) -> float:
        self.ConfinementLevel = max(80.0, min(100.0, float(TargetPercent)))
        self.MagneticFieldTesla = (self.ConfinementLevel / 100.0) * 48.5
        ODN.Transmit("Engineering.Constrictor.Adjusted", Confinement=self.ConfinementLevel)
        return self.ConfinementLevel

    def GetStatus(self) -> dict:
        return {
            "SegmentCount": self.SegmentCount,
            "ConfinementLevel": round(self.ConfinementLevel, 4),
            "MagneticFieldTesla": round(self.MagneticFieldTesla, 2),
            "StreamAligned": self.StreamAligned,
        }

# ─── 3. АРТИКУЛЯЦІЙНА РАМА ДИЛІТІЮ (DILITHIUM ARTICULATION) ───────────────────
class DilithiumArticulation(SystemComponent):
    def __init__(self):
        super().__init__()
        self.TiltAngleDeg = 22.5
        self.ResonanceFreqHz = 42.0
        self.CrystalIntegrity = 100.0
        self.LatticeSaturation = 0.15

    def SetTiltAngle(self, AngleDeg: float) -> float:
        self.TiltAngleDeg = max(0.0, min(45.0, float(AngleDeg)))
        ODN.Transmit("Engineering.Dilithium.Tilted", Angle=self.TiltAngleDeg)
        return self.TiltAngleDeg

    def TuneResonance(self, TargetFreqHz: float = 42.0) -> float:
        self.ResonanceFreqHz = float(TargetFreqHz)
        self.CrystalIntegrity = max(0.0, min(100.0, self.CrystalIntegrity - 0.0001))
        ODN.Transmit("Engineering.Dilithium.ResonanceTuned", Frequency=self.ResonanceFreqHz)
        return self.ResonanceFreqHz

    def GetStatus(self) -> dict:
        return {
            "TiltAngleDeg": round(self.TiltAngleDeg, 2),
            "ResonanceFreqHz": round(self.ResonanceFreqHz, 2),
            "CrystalIntegrity": round(self.CrystalIntegrity, 3),
            "LatticeSaturation": round(self.LatticeSaturation, 3),
        }

# ─── 4. ІНЖЕКТОРИ СУМІШІ (MATTER-ANTIMATTER INJECTOR) ──────────────────────────
class MatterAntimatterInjector(SystemComponent):
    def __init__(self):
        super().__init__()
        self.DeuteriumPulseNs = 12.5
        self.AntihydrogenPulseNs = 12.5
        self.Ratio = 1.000
        self.InjectionRateKgs = 0.0

    def CalibrateRatio(self, TargetRatio: float = 1.000) -> float:
        self.Ratio = max(0.95, min(1.05, float(TargetRatio)))
        ODN.Transmit("Engineering.Injector.RatioCalibrated", Ratio=self.Ratio)
        return self.Ratio

    def Inject(self, Throttle: float) -> float:
        Fraction = max(0.0, min(1.0, float(Throttle)))
        self.InjectionRateKgs = round(Fraction * 4.25, 3)
        return self.InjectionRateKgs

    def GetStatus(self) -> dict:
        return {
            "Ratio": round(self.Ratio, 4),
            "DeuteriumPulseNs": self.DeuteriumPulseNs,
            "AntihydrogenPulseNs": self.AntihydrogenPulseNs,
            "InjectionRateKgs": self.InjectionRateKgs,
        }

# ─── 5. ПЛАЗМОВІ РЕЛЕ ТА EPS (PLASMA RELAY GRID) ──────────────────────────────
class PlasmaRelay(LCARS):
    def __init__(self, RelayId: str, Channel: str, CapacityMw: float = 2400.0):
        super().__init__()
        self.RelayId = RelayId
        self.Channel = Channel
        self.CapacityMw = float(CapacityMw)
        self.CurrentPressureKpa = 101.3
        self.FlowRateKgs = 0.0
        self.DumpValveOpen = False
        self.Status = "NOMINAL"

    def SetFlow(self, FlowRate: float) -> None:
        self.FlowRateKgs = max(0.0, float(FlowRate))
        self.CurrentPressureKpa = 101.3 + (self.FlowRateKgs * 0.8)
        if self.CurrentPressureKpa > 200.0:
            self.Status = "OVERPRESSURE"
        else:
            self.Status = "NOMINAL"

    def OpenDumpValve(self) -> None:
        self.DumpValveOpen = True
        self.CurrentPressureKpa = 0.0
        self.FlowRateKgs = 0.0
        self.Status = "VENTING"

    def CloseDumpValve(self) -> None:
        self.DumpValveOpen = False
        self.CurrentPressureKpa = 101.3
        self.Status = "NOMINAL"

    def GetStatus(self) -> dict:
        return {
            "RelayId": self.RelayId,
            "Channel": self.Channel,
            "CapacityMw": self.CapacityMw,
            "CurrentPressureKpa": round(self.CurrentPressureKpa, 1),
            "FlowRateKgs": round(self.FlowRateKgs, 2),
            "DumpValveOpen": self.DumpValveOpen,
            "Status": self.Status,
        }

class PlasmaRelayGrid(SystemComponent):
    def __init__(self):
        super().__init__()
        self.Relays: dict[str, PlasmaRelay] = {
            "PortPrimary": PlasmaRelay("EPS-RELAY-PORT-PRIMARY", "PortPrimary", 2400.0),
            "PortSecondary": PlasmaRelay("EPS-RELAY-PORT-SECONDARY", "PortSecondary", 1800.0),
            "PortDump": PlasmaRelay("EPS-RELAY-PORT-DUMP", "PortEmergencyVent", 3200.0),
            "PortInjector": PlasmaRelay("EPS-RELAY-PORT-INJECTOR", "PortPlasmaInjector", 1500.0),
            "StbdPrimary": PlasmaRelay("EPS-RELAY-STBD-PRIMARY", "StarboardPrimary", 2400.0),
            "StbdSecondary": PlasmaRelay("EPS-RELAY-STBD-SECONDARY", "StarboardSecondary", 1800.0),
            "StbdDump": PlasmaRelay("EPS-RELAY-STBD-DUMP", "StarboardEmergencyVent", 3200.0),
            "StbdInjector": PlasmaRelay("EPS-RELAY-STBD-INJECTOR", "StarboardPlasmaInjector", 1500.0),
        }

    def BalanceFlow(self, PortTargetKgs: float, StbdTargetKgs: float) -> None:
        self.Relays["PortPrimary"].SetFlow(PortTargetKgs)
        self.Relays["PortInjector"].SetFlow(PortTargetKgs * 0.8)
        self.Relays["StbdPrimary"].SetFlow(StbdTargetKgs)
        self.Relays["StbdInjector"].SetFlow(StbdTargetKgs * 0.8)
        ODN.Transmit("Engineering.EPS.Balanced", Port=PortTargetKgs, Starboard=StbdTargetKgs)

    def EmergencyDump(self) -> None:
        self.Relays["PortDump"].OpenDumpValve()
        self.Relays["StbdDump"].OpenDumpValve()
        ODN.Transmit("Engineering.EPS.EmergencyDumpEngaged", Status="VentingToSpace")

    def ResetDumpValves(self) -> None:
        self.Relays["PortDump"].CloseDumpValve()
        self.Relays["StbdDump"].CloseDumpValve()

    def GetStatus(self) -> dict:
        return {Name: R.GetStatus() for Name, R in self.Relays.items()}

# ─── 6. ФАЗУВАННЯ ВАРП-КОТУШОК (WARP COIL PHASING) ────────────────────────────
class WarpCoilPhasing(SystemComponent):
    def __init__(self, CoilsPerNacelle: int = 18):
        super().__init__()
        self.CoilsPerNacelle = int(CoilsPerNacelle)
        self.TotalCoils = self.CoilsPerNacelle * 2
        self.BasePhaseAngleDeg = 0.0
        self.SequenceDelayNs = 2.75
        self.CoilFrequenciesGhz = 42.5
        self.WaveSynchronized = True

    def SetPhaseAngle(self, AngleDeg: float) -> float:
        self.BasePhaseAngleDeg = float(AngleDeg) % 360.0
        ODN.Transmit("Engineering.Coils.PhaseAdjusted", Angle=self.BasePhaseAngleDeg)
        return self.BasePhaseAngleDeg

    def GeneratePeristalticSequence(self, WarpFactor: float) -> list[dict]:
        Wave = []
        for i in range(1, self.CoilsPerNacelle + 1):
            Offset = round((i - 1) * (360.0 / self.CoilsPerNacelle) + self.BasePhaseAngleDeg, 2) % 360.0
            Delay = round(i * self.SequenceDelayNs, 3)
            Wave.append({
                "CoilIndex": i,
                "PhaseOffsetDeg": Offset,
                "FiringDelayNs": Delay,
                "Confinement": 0.9998,
            })
        return Wave

    def GetStatus(self) -> dict:
        return {
            "TotalCoils": self.TotalCoils,
            "CoilsPerNacelle": self.CoilsPerNacelle,
            "BasePhaseAngleDeg": round(self.BasePhaseAngleDeg, 2),
            "SequenceDelayNs": self.SequenceDelayNs,
            "CoilFrequenciesGhz": self.CoilFrequenciesGhz,
            "WaveSynchronized": self.WaveSynchronized,
        }

# ─── 7. ЕЛЕКТРОПЛАЗМОВИЙ РОЗПОДІЛ (EPS CONDUIT) ───────────────────────────────
class EPSConduit(SystemComponent):
    def __init__(self, Capacity: float = 1500.0):
        super().__init__()
        self.Capacity = float(Capacity)
        self.Load = 0.0
        self.Status = "NOMINAL"
        self.PowerChannel = Transmission(float, float)

    def AdjustLoad(self, Amount: float) -> None:
        self.Load = max(0.0, min(self.Capacity * 1.5, self.Load + Amount))
        if self.Load > self.Capacity * 1.2:
            self.Status = "CRITICAL"
        elif self.Load > self.Capacity:
            self.Status = "OVERLOAD"
        else:
            self.Status = "NOMINAL"

        ODN.Transmit("Engineering.EPS.LoadAdjusted", Load=self.Load, Status=self.Status)
        self.PowerChannel.Emit(self.Load, self.Capacity)

    def GetStatus(self) -> dict:
        PercentVal = (self.Load / self.Capacity) * 100.0 if self.Capacity > 0.0 else 0.0
        return {
            "Load": self.Load,
            "Capacity": self.Capacity,
            "Status": self.Status,
            "LoadPercent": round(PercentVal, 2),
        }

# ─── 8. МАНЕВРОВІ СОПЛА ОРІЄНТАЦІЇ (THRUSTER SYSTEM / RCS) ────────────────────
class ThrusterSystem(SystemComponent):
    def __init__(self):
        super().__init__()
        self.FuelLevel = 100.0
        self.Active = True
        self.Orientation = {"Pitch": 0.0, "Yaw": 0.0, "Roll": 0.0}
        self.ThrusterChannel = Transmission(str, float)

    def Fire(self, Axis: str, Intensity: float) -> bool:
        if not self.Active or self.FuelLevel <= 0.0:
            return False

        FuelCost = float(Intensity) * 0.1
        self.FuelLevel = max(0.0, self.FuelLevel - FuelCost)
        Current = self.Orientation.get(Axis, 0.0)
        self.Orientation[Axis] = (Current + float(Intensity)) % 360.0

        ODN.Transmit("Engineering.Thrusters.Fired", Axis=Axis, Intensity=Intensity)
        self.ThrusterChannel.Emit(Axis, Intensity)
        return True

    def GetStatus(self) -> dict:
        return {
            "Active": self.Active,
            "FuelLevel": round(self.FuelLevel, 2),
            "Orientation": self.Orientation.copy(),
        }

# ─── 9. ІМПУЛЬСНИЙ СУБСВІТЛОВИЙ РУШІЙ (IMPULSE DRIVE) ──────────────────────────
class ImpulseDrive(SystemComponent):
    def __init__(self):
        super().__init__()
        self.Active = True
        self.ImpulseSpeed = 0.0
        self.DeuteriumLevel = 100.0
        self.FusionReactorTempK = 850.0
        self.ThrustVector = 100.0

    def SetImpulse(self, Fraction: float) -> bool:
        if not self.Active:
            return False

        TargetSpeed = max(0.0, min(1.0, float(Fraction)))
        self.ImpulseSpeed = TargetSpeed
        self.FusionReactorTempK = 850.0 + (TargetSpeed * 350.0)
        ODN.Transmit("Engineering.Impulse.SpeedChanged", Speed=self.ImpulseSpeed)
        return True

    def GetStatus(self) -> dict:
        return {
            "Active": self.Active,
            "ImpulseSpeed": self.ImpulseSpeed,
            "DeuteriumLevel": self.DeuteriumLevel,
            "FusionReactorTempK": round(self.FusionReactorTempK, 1),
            "ThrustVector": self.ThrustVector,
        }

# ─── 10. ФІЗИЧНЕ ВАРП-ЯДРО (WARP CORE REACTOR) ────────────────────────────────
class WarpCore(SystemComponent):
    def __init__(self):
        super().__init__()
        self.Constrictor = MagneticConstrictor()
        self.Dilithium = DilithiumArticulation()
        self.Injector = MatterAntimatterInjector()
        self.Relays = PlasmaRelayGrid()
        self.WarpFactor = 0.0
        self.CoreStability = 100.0
        self.PlasmaFlow = 0.0
        self.ContainmentField = 100.0
        self.CoreEjected = False
        self.StructuralNodes: list = []

    @property
    def ResonanceFreq(self) -> float:
        return self.Dilithium.ResonanceFreqHz

    @property
    def DilithiumIntegrity(self) -> float:
        return self.Dilithium.CrystalIntegrity

    @property
    def MatterAntimatterRatio(self) -> float:
        return self.Injector.Ratio

    def SetWarpFactor(self, Factor: float) -> bool:
        if self.CoreEjected:
            return False

        TargetFactor = max(0.0, min(9.99, float(Factor)))
        self.WarpFactor = TargetFactor
        self.PlasmaFlow = round(TargetFactor * 10.0, 1) if TargetFactor > 0.0 else 0.0
        Throttle = TargetFactor / 9.99
        self.Injector.Inject(Throttle)

        FlowKgs = self.PlasmaFlow * 0.425
        self.Relays.BalanceFlow(FlowKgs, FlowKgs)

        ODN.Transmit("Engineering.WarpCore.FactorChanged", WarpFactor=self.WarpFactor, PlasmaFlow=self.PlasmaFlow)
        return True

    def EjectCore(self) -> bool:
        self.CoreEjected = True
        self.WarpFactor = 0.0
        self.PlasmaFlow = 0.0
        self.CoreStability = 0.0
        self.Relays.EmergencyDump()
        ODN.Transmit("Engineering.WarpCore.Ejected", Status="CoreEjectedToSpace")
        return True

    def InjectWarpMatrix(self, Nodes: list) -> None:
        if not Nodes:
            return
        self.StructuralNodes = Nodes

    def GenerateWarpField(self) -> str:
        if self.CoreEjected or not self.StructuralNodes:
            return ""

        Instructions = []
        for Node in self.StructuralNodes:
            Name = Node.get("Name", "UnknownZone")
            Shape = Node.get("Type", "box")
            Instructions.append(f"/lcars/geom/add {Shape} {Name}")
        return chr(10).join(Instructions)

    def GetStatus(self) -> dict:
        return {
            "WarpFactor": self.WarpFactor,
            "CoreStability": self.CoreStability,
            "PlasmaFlow": self.PlasmaFlow,
            "ResonanceFreq": self.ResonanceFreq,
            "DilithiumIntegrity": self.DilithiumIntegrity,
            "MatterAntimatterRatio": self.MatterAntimatterRatio,
            "ContainmentField": self.ContainmentField,
            "CoreEjected": self.CoreEjected,
            "Constrictor": self.Constrictor.GetStatus(),
            "Dilithium": self.Dilithium.GetStatus(),
            "Injector": self.Injector.GetStatus(),
            "Relays": self.Relays.GetStatus(),
            "StructuralNodesCount": len(self.StructuralNodes),
        }

# ─── 11. ГОЛОВНИЙ РУШІЙНИЙ КОМПЛЕКС (WARP DRIVE) ──────────────────────────────
class WarpDrive(SystemComponent):
    Instance = None

    StatusChanged = Transmission(str)
    WarpFactorChanged = Transmission(float)
    FlightTelemetry = Transmission(dict)
    RelayTriggered = Transmission(str, str)

    def __init__(self):
        super().__init__()
        self.Core = WarpCore()
        self.Coils = WarpCoilPhasing()
        self.Impulse = ImpulseDrive()
        self.Thrusters = ThrusterSystem()
        self.EPS = EPSConduit(Capacity=1500.0)
        self.Mode = "STANDBY"
        self.Version = VersionInfo.GetVersion()

    @classmethod
    def GetInstance(cls) -> WarpDrive:
        if cls.Instance is None:
            cls.Instance = WarpDrive()
        return cls.Instance

    @property
    def WarpFactor(self) -> float:
        return self.Core.WarpFactor

    @property
    def CoreStability(self) -> float:
        return self.Core.CoreStability

    @property
    def PlasmaFlow(self) -> float:
        return self.Core.PlasmaFlow

    @property
    def ResonanceFreq(self) -> float:
        return self.Core.ResonanceFreq

    @property
    def DilithiumIntegrity(self) -> float:
        return self.Core.DilithiumIntegrity

    def SetMode(self, ModeName: str) -> None:
        Normalized = ModeName.upper()

        if Normalized == "IMPULSE":
            self.Mode = "IMPULSE"
            self.Core.SetWarpFactor(0.0)
            if self.Impulse.ImpulseSpeed <= 0.0:
                self.Impulse.SetImpulse(0.5)
            self.EPS.AdjustLoad(150.0)

        elif Normalized == "WARP":
            self.Mode = "WARP"
            if self.Core.WarpFactor <= 0.0:
                self.Core.SetWarpFactor(1.0)
            self.Impulse.SetImpulse(0.0)
            self.EPS.AdjustLoad(450.0)

        elif Normalized == "AUTODESTRUCT":
            self.Mode = "AUTODESTRUCT"
            self.Core.CoreStability = 0.0
            self.Core.PlasmaFlow = 0.0

        else:
            self.Mode = "STANDBY"
            self.Core.SetWarpFactor(0.0)
            self.Impulse.SetImpulse(0.0)
            self.EPS.AdjustLoad(-200.0)

        ODN.Transmit("Engineering.WarpDrive.ModeChanged", Mode=self.Mode, WarpFactor=self.WarpFactor)
        self.StatusChanged.Emit(self.Mode)

    def SetWarpFactor(self, Factor: float) -> bool:
        Success = self.Core.SetWarpFactor(Factor)
        if Success:
            TargetFactor = float(Factor)
            if TargetFactor > 0.0:
                if self.Mode != "WARP":
                    self.Mode = "WARP"
                    self.Impulse.SetImpulse(0.0)
                PowerMw = CochraneCalculator.CalculatePowerMw(TargetFactor)
                self.EPS.AdjustLoad(PowerMw * 0.25)
                self.Coils.SetPhaseAngle(TargetFactor * 36.0)
            else:
                self.Mode = "STANDBY"
                self.EPS.AdjustLoad(-200.0)

            self.WarpFactorChanged.Emit(self.WarpFactor)
            self.StatusChanged.Emit(self.Mode)
            ODN.Transmit("Engineering.WarpDrive.FactorChanged", WarpFactor=self.WarpFactor)
        return Success

    def SetImpulse(self, Fraction: float) -> bool:
        Success = self.Impulse.SetImpulse(Fraction)
        if Success:
            if Fraction > 0.0:
                self.Mode = "IMPULSE"
                self.Core.SetWarpFactor(0.0)
                self.EPS.AdjustLoad(150.0)
            else:
                self.Mode = "STANDBY"
            self.StatusChanged.Emit(self.Mode)
        return Success

    def InjectWarpMatrix(self, Nodes: list) -> None:
        self.Core.InjectWarpMatrix(Nodes)

    def GenerateWarpField(self) -> str:
        return self.Core.GenerateWarpField()

    def GetStatus(self) -> dict:
        CurrentWarp = self.Core.WarpFactor
        SpeedC = CochraneCalculator.CalculateSpeed(CurrentWarp)
        Compression = CochraneCalculator.CalculateCompression(CurrentWarp)
        PowerMw = CochraneCalculator.CalculatePowerMw(CurrentWarp)

        Data = {
            "Mode": self.Mode,
            "WarpFactor": CurrentWarp,
            "VelocityC": SpeedC,
            "SubspaceCompression": Compression,
            "PowerDemandMw": PowerMw,
            "CoreStability": self.Core.CoreStability,
            "PlasmaFlow": self.Core.PlasmaFlow,
            "Resonance": self.Core.ResonanceFreq,
            "Dilithium": self.Core.DilithiumIntegrity,
            "Core": self.Core.GetStatus(),
            "Coils": self.Coils.GetStatus(),
            "Impulse": self.Impulse.GetStatus(),
            "Thrusters": self.Thrusters.GetStatus(),
            "EPS": self.EPS.GetStatus(),
            "Version": self.Version,
        }
        self.FlightTelemetry.Emit(Data)
        return Data

# ─── 12. КАНОНІЧНІ ТОЧКИ ВХОДУ ─────────────────────────────────────────────────
WarpDriveCore = WarpDrive.GetInstance
WarpCoreReactor = WarpCore
WarpPhasing = WarpCoilPhasing
WARPDRIVE = WarpDrive.GetInstance()
