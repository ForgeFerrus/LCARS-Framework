# ◤ LCARS ENGINEERING :: GEANT4 DETECTOR BUILDER 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/detector.py
# ОПИС: Апаратний конструктор геометрії детекторів частинок та радіації зорельота.
#       Підготовляє геометричні параметри сцинтиляторів, коліматорів та захисних екранів
#       для передачі та моделювання фізичних взаємодій у Geant4 Enterprise.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import SystemComponent, LCARS
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN, Transmission

# Матеріали для детектора частинок Geant4
class MaterialType(LCARS):
    Cobalt59 = "Cobalt-59"
    Lead = "Lead"
    Tungsten = "Tungsten"
    Aluminum = "Aluminum"
    Copper = "Copper"
    Silicon = "Silicon"
    Gadolinium = "Gadolinium"
    Water = "Water"
    Air = "Air"

# Збирач геометрії детекторів для зв'язку з Geant4
class DetectorBuilder(SystemComponent):
    Instance = None
    GeometryReady = Transmission(dict)
    TransferStatus = Transmission(str, str)

    def __init__(self):
        super().__init__()
        self.Parts = {
            "crystal": None,
            "shield": None,
            "collimator": None,
        }
        self.Connector = None
        self.IsReady = False
        self.Version = VersionInfo.GetVersion()

    @classmethod
    def GetInstance(cls) -> DetectorBuilder:
        if cls.Instance is None:
            cls.Instance = DetectorBuilder()
        return cls.Instance

    # Додавання сцинтиляційного кристала детектора
    def AddCrystal(self, Name: str, Material: str = MaterialType.Cobalt59,
                   RadiusCm: float = 2.5, HeightCm: float = 5.0) -> None:
        MatStr = str(getattr(Material, "value", Material))
        self.Parts["crystal"] = {
            "Type": "crystal",
            "Name": Name,
            "Material": MatStr,
            "RadiusCm": float(RadiusCm),
            "HeightCm": float(HeightCm),
        }
        ODN.Transmit("Engineering.Detector.CrystalConfigured", Name=Name, Material=MatStr)

    # Додавання радіаційного екрана / щита
    def AddShield(self, Name: str, Material: str = MaterialType.Lead,
                  DimensionsCm: tuple = (10.0, 10.0, 10.0)) -> None:
        MatStr = str(getattr(Material, "value", Material))
        self.Parts["shield"] = {
            "Type": "shield",
            "Name": Name,
            "Material": MatStr,
            "DimensionsCm": tuple(float(D) for D in DimensionsCm),
        }
        ODN.Transmit("Engineering.Detector.ShieldConfigured", Name=Name, Material=MatStr)

    # Додавання коліматора
    def AddCollimator(self, Name: str, Material: str = MaterialType.Tungsten,
                      InnerRadiusCm: float = 0.5, OuterRadiusCm: float = 2.0) -> None:
        MatStr = str(getattr(Material, "value", Material))
        self.Parts["collimator"] = {
            "Type": "collimator",
            "Name": Name,
            "Material": MatStr,
            "InnerRadiusCm": float(InnerRadiusCm),
            "OuterRadiusCm": float(OuterRadiusCm),
        }
        ODN.Transmit("Engineering.Detector.CollimatorConfigured", Name=Name, Material=MatStr)

    # Підключення каналу передачі до Geant4
    def AttachConnector(self, Connector: any) -> None:
        self.Connector = Connector

    # Збірка геометрії у формат для Geant4
    def BuildGeometry(self) -> dict:
        Time = LCARS.System.Time
        Timestamp = Time.time() if Time and hasattr(Time, "time") else 0.0

        Geometry = {
            "Detector": dict(self.Parts),
            "Timestamp": Timestamp,
            "Version": self.Version,
        }
        self.IsReady = True
        self.GeometryReady.Emit(Geometry)
        ODN.Transmit("Engineering.Detector.GeometryBuilt", HasCrystal=bool(self.Parts["crystal"]))
        return Geometry

    # Передача геометрії в Geant4
    def SendToGeant4(self) -> bool:
        if not self.IsReady:
            self.TransferStatus.Emit("ERROR", "Geometry not built")
            return False
        if not self.Connector:
            self.TransferStatus.Emit("ERROR", "No connector attached")
            return False

        Geometry = self.BuildGeometry()
        self.TransferStatus.Emit("SENDING", "Transferring to Geant4")
        if hasattr(self.Connector, "Send") and callable(self.Connector.Send):
            return bool(self.Connector.Send(Geometry))
        return True

    # Звіт про стан збирача детекторів
    def GetStatus(self) -> dict:
        return {
            "Parts": dict(self.Parts),
            "IsReady": self.IsReady,
            "Connected": self.Connector is not None,
            "Version": self.Version,
        }
