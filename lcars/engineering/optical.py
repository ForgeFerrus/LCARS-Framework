# ◤ LCARS ENGINEERING :: ISOLINEAR OPTICAL SUBSTRATE & CONDUITS 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/optical.py
# ОПИС: Фізичне оптичне середовище передачі та обробки даних зорельота.
#       Моделює кристалічні ізолінійні стрижні (IsolinearRod), світлопроводи (OpticalConduit),
#       оптичні спектральні хвилі та фотонні розгалужувачі магістралі ODN.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import SystemComponent, LCARS
from lcars.core.signal import ODN
from lcars.engineering.isolinear import IsolinearChip, ChipStatus

# Спектральні лінії оптичного носія (довжини хвиль у нанометрах)
class OpticalSpectrum(LCARS):
    Blue450 = 450.0
    Cyan490 = 490.0
    Green532 = 532.0
    Amber590 = 590.0
    Red650 = 650.0

# Стан оптичного каналу
class ConduitStatus(LCARS):
    ALIGNING = "ALIGNING"
    TRANSMITTING = "TRANSMITTING"
    ATTENUATED = "ATTENUATED"
    FAULT = "FAULT"

# Фізичний світловод шини ODN (Optical Conduit)
class OpticalConduit(LCARS):
    def __init__(self, ConduitId: str = "ODN-C01", LengthMeters: float = 12.5,
                 CoreIndex: float = 1.48, MaxBandwidthTbps: float = 100.0):
        super().__init__()
        self.ConduitId = ConduitId
        self.LengthMeters = float(LengthMeters)
        self.CoreIndex = float(CoreIndex)
        self.MaxBandwidthTbps = float(MaxBandwidthTbps)
        self.Status = ConduitStatus.ALIGNING
        self.AttenuationDb = 0.02
        self.ActivePhotons = 0
        self.LatencyNs = (self.LengthMeters * self.CoreIndex / 300000000.0) * 1000000000.0

    # Пропуск світлового пакету по світловоду
    def TransmitPhotons(self, PacketSizeBits: int, WavelengthNm: float = OpticalSpectrum.Blue450) -> dict:
        self.Status = ConduitStatus.TRANSMITTING
        self.ActivePhotons += PacketSizeBits
        ThroughputRatio = min(1.0, float(PacketSizeBits) / (self.MaxBandwidthTbps * 1000000000000.0))

        Result = {
            "ConduitId": self.ConduitId,
            "LatencyNs": round(self.LatencyNs, 3),
            "WavelengthNm": WavelengthNm,
            "PacketBits": PacketSizeBits,
            "AttenuationLossDb": round(self.LengthMeters * self.AttenuationDb, 4),
            "Status": self.Status,
        }
        ODN.Transmit("Engineering.Optical.ConduitPulsed", Conduit=self.ConduitId, Latency=Result["LatencyNs"])
        return Result

    def GetStatus(self) -> dict:
        return {
            "ConduitId": self.ConduitId,
            "LengthMeters": self.LengthMeters,
            "LatencyNs": round(self.LatencyNs, 3),
            "BandwidthTbps": self.MaxBandwidthTbps,
            "Status": self.Status,
            "TotalPhotonsHandled": self.ActivePhotons,
        }

# Оптичний розгалужувач / спліттер світлового променя
class OpticalCoupler(LCARS):
    def __init__(self, CouplerId: str = "COUPLER-01", SplitRatio: float = 0.5):
        super().__init__()
        self.CouplerId = CouplerId
        self.SplitRatio = float(SplitRatio)
        self.Ports = {}

    def RouteBeam(self, InputConduit: OpticalConduit, TargetConduits: list) -> bool:
        if not TargetConduits:
            return False
        for Conduit in TargetConduits:
            self.Ports[Conduit.ConduitId] = Conduit
        ODN.Transmit("Engineering.Optical.BeamCoupled", Coupler=self.CouplerId, Targets=len(TargetConduits))
        return True

# Оптичний ізолінійний стрижень (циліндричний процесорний кристал)
class IsolinearRod(LCARS):
    def __init__(self, RodId: str = "ROD-0001", TargetChip: IsolinearChip | None = None,
                 ResonanceGhz: float = 4.75, OpticalChannel: float = OpticalSpectrum.Blue450):
        super().__init__()
        self.RodId = RodId
        self.TargetChip = TargetChip
        self.ResonanceGhz = float(ResonanceGhz)
        self.OpticalChannel = float(OpticalChannel)
        self.Status = "ACTIVE" if TargetChip else "STANDBY"
        self.Buffer = {}
        self.OperationsCount = 0

    # Прив'язка стрижня до плоского чіпа пам'яті
    def MountChip(self, Chip: IsolinearChip) -> bool:
        self.TargetChip = Chip
        self.Status = "ACTIVE"
        ODN.Transmit("Engineering.Optical.RodMounted", Rod=self.RodId, ChipId=Chip.Id)
        return True

    # Оптичне виконання запиту через кристал
    def Process(self, Query: str, Params: tuple = ()):
        self.OperationsCount += 1
        if self.TargetChip is None:
            return []
        return self.TargetChip.ExecuteQuery(Query, Params)

    # Ін'єкція квантово-оптичного патерна в кристал (для телепортації, сенсорів, чорної скриньки)
    def InjectPattern(self, PatternId: str, PatternData: any) -> bool:
        self.Buffer[PatternId] = PatternData
        self.OperationsCount += 1

        if self.TargetChip and hasattr(self.TargetChip, "Data"):
            self.TargetChip.Data[PatternId] = PatternData

        ODN.Transmit("Engineering.Optical.PatternInjected", Rod=self.RodId, PatternId=PatternId)
        return True

    # Вилучення патерна з оптичного кристала
    def ExtractPattern(self, PatternId: str) -> any:
        self.OperationsCount += 1
        if PatternId in self.Buffer:
            return self.Buffer[PatternId]
        if self.TargetChip and hasattr(self.TargetChip, "Data"):
            return self.TargetChip.Data.get(PatternId)
        return None

    # Очищення буфера патернів
    def FlushPattern(self, PatternId: str) -> bool:
        Removed = self.Buffer.pop(PatternId, None)
        if self.TargetChip and hasattr(self.TargetChip, "Data"):
            self.TargetChip.Data.pop(PatternId, None)
        return Removed is not None

    def GetStatus(self) -> dict:
        return {
            "RodId": self.RodId,
            "Status": self.Status,
            "ResonanceGhz": self.ResonanceGhz,
            "ChannelWavelength": self.OpticalChannel,
            "TargetChip": self.TargetChip.Id if self.TargetChip else None,
            "BufferedPatterns": len(self.Buffer),
            "OperationsCount": self.OperationsCount,
        }

# Кристалічний субстрат комутації між банками чіпів
class OpticalSubstrate(LCARS):
    def __init__(self, ArrayId: str = "SUBSTRATE-00"):
        super().__init__()
        self.ArrayId = ArrayId
        self.Rods: dict = {}
        self.Conduits: dict = {}
        self.Couplers: dict = {}
        self.InitializeTopology()

    # Створення базової оптичної топології субстрату
    def InitializeTopology(self) -> None:
        for Index in range(4):
            CId = f"CONDUIT-{self.ArrayId}-{Index:02d}"
            self.Conduits[CId] = OpticalConduit(ConduitId=CId, LengthMeters=10.0 + Index * 5.0)

    # Додавання оптичного стрижня в субстрат
    def RegisterRod(self, Rod: IsolinearRod) -> None:
        self.Rods[Rod.RodId] = Rod

    # Маршрутизація оптичного імпульсу через субстрат
    def RoutePulse(self, SourceRodId: str, TargetConduitId: str, PacketBits: int) -> dict:
        Rod = self.Rods.get(SourceRodId)
        Conduit = self.Conduits.get(TargetConduitId)
        if not Conduit:
            return {"Status": "FAILED_NO_CONDUIT"}

        Wavelength = Rod.OpticalChannel if Rod else OpticalSpectrum.Blue450
        return Conduit.TransmitPhotons(PacketBits, Wavelength)

    def GetStatus(self) -> dict:
        return {
            "ArrayId": self.ArrayId,
            "RodsCount": len(self.Rods),
            "ConduitsCount": len(self.Conduits),
            "CouplersCount": len(self.Couplers),
        }

# Головне фізичне розширення оптичної мережі зорельота
class OpticalNetwork(SystemComponent):
    Instance = None

    def __init__(self):
        super().__init__()
        self.Substrates: dict = {}
        self.Rods: dict = {}
        self.Conduits: dict = {}
        self.Couplers: dict = {}
        self.DefaultConduit = OpticalConduit(ConduitId="ODN-MAIN-SPINE", LengthMeters=45.0, MaxBandwidthTbps=500.0)
        self.Conduits["ODN-MAIN-SPINE"] = self.DefaultConduit
        self.InitializeSubstrates()

    @classmethod
    def GetInstance(cls) -> OpticalNetwork:
        if cls.Instance is None:
            cls.Instance = OpticalNetwork()
        return cls.Instance

    # Ініціалізація оптичних субстратів по основних секціях
    def InitializeSubstrates(self) -> None:
        for ArrayIdx in range(11):
            SubId = f"SUB-{ArrayIdx:02d}"
            self.Substrates[SubId] = OpticalSubstrate(ArrayId=SubId)

    # Створення та монтування оптичного стрижня
    def CreateRod(self, RodId: str, TargetChip: IsolinearChip | None = None,
                  WavelengthNm: float = OpticalSpectrum.Blue450) -> IsolinearRod:
        Rod = IsolinearRod(RodId=RodId, TargetChip=TargetChip, OpticalChannel=WavelengthNm)
        self.Rods[RodId] = Rod
        Sector = TargetChip.Array if TargetChip else "00"
        SubId = f"SUB-{Sector}" if f"SUB-{Sector}" in self.Substrates else "SUB-00"
        self.Substrates[SubId].RegisterRod(Rod)
        return Rod

    def GetRod(self, RodId: str) -> IsolinearRod | None:
        return self.Rods.get(RodId)

    # Пульсація оптичної магістралі
    def PulseSpine(self, PacketBits: int = 1048576) -> dict:
        return self.DefaultConduit.TransmitPhotons(PacketBits, OpticalSpectrum.Blue450)

    # Звіт про стан оптичної мережі
    def GetStatus(self) -> dict:
        return {
            "SpineConduit": self.DefaultConduit.GetStatus(),
            "TotalSubstrates": len(self.Substrates),
            "TotalRods": len(self.Rods),
            "TotalConduits": len(self.Conduits),
            "CarrierSpectrums": [
                OpticalSpectrum.Blue450,
                OpticalSpectrum.Cyan490,
                OpticalSpectrum.Green532,
                OpticalSpectrum.Amber590,
                OpticalSpectrum.Red650,
            ],
        }
