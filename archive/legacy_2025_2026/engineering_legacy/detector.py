# LCARS DETECTOR BUILDER - ENGINEERING LAYER
# ПРИЗНАЧЕННЯ: Підготовка та передача геометрії детекторів до Geant4
# СТАНДАРТ: Titanium Master (No-OS, No-JSON)

from __future__ import annotations
# Titanium Bridge Migration: from enum import Enum, auto
# Titanium Bridge Migration: from typing import Any

from lcars.base.type import SystemComponent, Directive
from core.signal import Transmission


class MaterialEnum(Enum):
    # Матеріали для детекторів Geant4
    COBALT_59 = "Cobalt-59"
    LEAD = "Lead"
    TUNGSTEN = "Tungsten"
    ALUMINUM = "Aluminum"
    COPPER = "Copper"
    SILICON = "Silicon"
    GADOLINIUM = "Gadolinium"
    WATER = "Water"
    AIR = "Air"


class DetectorBuilder(SystemComponent):
    # Збирач геометрії детекторів для Geant4
    # Підготовляє геометрію та передає через канал зв'язку

    # Сигнал готовності геометрії: дані детектора
    GeometryReady = Transmission(dict)
    # Сигнал статусу передачі: статус, повідомлення
    TransferStatus = Transmission(str, str)

    def __init__(self):
        super().__init__()
        self.Parts: dict[str, Any] = {"crystal": None, "shield": None, "collimator": None}
        self.Connector = None  # NetworkConnector для зв'язку з Geant4
        self.IsReady = False

    def AddCrystal(self, Name: str, Material: MaterialEnum, Radius: float, Height: float) -> None:
        # Додавання кристала детектора
        self.Parts["crystal"] = {
            "Type": "crystal",
            "Name": Name,
            "Material": Material.value if isinstance(Material, MaterialEnum) else str(Material),
            "RadiusCm": float(Radius),
            "HeightCm": float(Height),
        }

    def AddShield(self, Name: str, Material: MaterialEnum, Dimensions: tuple[float, float, float]) -> None:
        # Додавання щита детектора
        self.Parts["shield"] = {
            "Type": "shield",
            "Name": Name,
            "Material": Material.value if isinstance(Material, MaterialEnum) else str(Material),
            "DimensionsCm": tuple(float(D) for D in Dimensions),
        }

    def AddCollimator(self, Name: str, Material: MaterialEnum, InnerRadius: float, OuterRadius: float) -> None:
        # Додавання коліматора
        self.Parts["collimator"] = {
            "Type": "collimator",
            "Name": Name,
            "Material": Material.value if isinstance(Material, MaterialEnum) else str(Material),
            "InnerRadiusCm": float(InnerRadius),
            "OuterRadiusCm": float(OuterRadius),
        }

    def AttachConnector(self, Connector) -> None:
        # Підключення каналу зв'язку з Geant4
        self.Connector = Connector

    def BuildGeometry(self) -> dict[str, Any]:
        # Підготовка геометрії до передачі
        Geometry = {
            "Detector": self.Parts,
            "Timestamp": Directive.Chronometer.Now(),
            "Version": "1.0",
        }
        self.IsReady = True
        self.GeometryReady.Emit(Geometry)
        return Geometry

    def SendToGeant4(self) -> bool:
        # Передача геометрії в Geant4 через канал зв'язку
        if not self.IsReady:
            self.TransferStatus.Emit("ERROR", "Geometry not built")
            return False
        if not self.Connector:
            self.TransferStatus.Emit("ERROR", "No connector attached")
            return False
        Geometry = self.BuildGeometry()
        self.TransferStatus.Emit("SENDING", "Transferring to Geant4")
        return self.Connector.Send(Geometry)

    def GetStatus(self) -> dict[str, Any]:
        # Отримання статусу будівельника
        return {
            "Parts": self.Parts,
            "IsReady": self.IsReady,
            "HasConnector": self.Connector is not None,
        }

    # === Керування детектором (з detector_control.py) ===

    def Control(self, Command: str, Params: dict | None = None) -> dict[str, Any]:
        # Універсальний метод керування детектором
        # Команда: POWER_ON, POWER_OFF, CONFIGURE, MONITOR, CALIBRATE
        Params = Params or {}

        if Command == "POWER_ON":
            return {"Status": "ON", "Energy": 100.0, "Message": "Detector powered on"}

        elif Command == "POWER_OFF":
            return {"Status": "OFF", "Energy": 0.0, "Message": "Detector powered off"}

        elif Command == "CONFIGURE":
            # Конфігурація параметрів
            return {"Status": "CONFIGURED", "Params": Params, "Message": "Configuration applied"}

        elif Command == "MONITOR":
            # Моніторинг стану
            return {
                "Status": "MONITORING",
                "Power": "on",
                "Energy": 100.0,
                "Temperature": 25.0,
                "DataRate": 0.0,
            }

        elif Command == "CALIBRATE":
            # Калібрування
            return {"Status": "CALIBRATED", "Message": "Calibration completed"}

        else:
            return {"Status": "ERROR", "Message": f"Unknown command: {Command}"}

    def PowerOn(self) -> dict[str, Any]:
        # Увімкнення живлення
        return self.Control("POWER_ON")

    def PowerOff(self) -> dict[str, Any]:
        # Вимкнення живлення
        return self.Control("POWER_OFF")

    def Monitor(self) -> dict[str, Any]:
        # Отримання моніторингу
        return self.Control("MONITOR")

    def Calibrate(self) -> dict[str, Any]:
        # Калібрування детектора
        return self.Control("CALIBRATE")

    # === Розширений функціонал ===

    def ReceiveData(self, Data: dict[str, Any]) -> None:
        # Отримання даних з Geant4 після симуляції
        # Зберігаємо результати симуляції
        if "Hits" in Data:
            self.LastScanData["Hits"] = Data["Hits"]
        if "Energy" in Data:
            self.LastScanData["Energy"] = Data["Energy"]
        self.TransferStatus.Emit("RECEIVED", "Data from Geant4 received")

    def SetEnergyWindow(self, MinEnergy: float, MaxEnergy: float) -> dict[str, Any]:
        # Налаштування енергетичного вікна
        self.EnergyWindow = {"Min": MinEnergy, "Max": MaxEnergy}
        return {
            "Status": "CONFIGURED",
            "EnergyWindow": self.EnergyWindow,
            "Message": f"Energy window set: {MinEnergy} - {MaxEnergy} keV",
        }

    def SetSensitivity(self, Level: float) -> dict[str, Any]:
        # Налаштування чутливості (0.0 - 1.0)
        self.Sensitivity = max(0.0, min(1.0, Level))
        return {
            "Status": "CONFIGURED",
            "Sensitivity": self.Sensitivity,
            "Message": f"Sensitivity set to {self.Sensitivity:.2%}",
        }

    def Reset(self) -> dict[str, Any]:
        # Скидання детектора до початкового стану
        self.IsReady = False
        self.LastScanData = {}
        self.EnergyWindow = {"Min": 0.0, "Max": 10000.0}
        self.Sensitivity = 1.0
        return {"Status": "RESET", "Message": "Detector reset to initial state"}

    def Initialize(self) -> dict[str, Any]:
        # Ініціалізація детектора
        self.Reset()
        self.IsReady = True
        return {"Status": "INITIALIZED", "Message": "Detector ready for operation"}

    def ExportConfiguration(self) -> dict[str, Any]:
        # Експорт конфігурації
        return {
            "Parts": self.Parts,
            "EnergyWindow": getattr(self, "EnergyWindow", {"Min": 0.0, "Max": 10000.0}),
            "Sensitivity": getattr(self, "Sensitivity", 1.0),
            "Timestamp": Directive.Chronometer.Now(),
        }
