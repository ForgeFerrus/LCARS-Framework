# LCARS DETECTOR BUILDER - ENGINEERING LAYER
# Призначення: зібрати геометрію детектора, зберегти його параметри і віддати їх у симулятор Geant4.
# Тут немає UI і немає окремого контролера. Це інженерний вузол, який тримає структуру детектора і його стан.

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from lcars.base.type import SystemComponent
from lcars.core.signal import Transmission


class MaterialEnum(Enum):
    # Матеріали, які вже можна використовувати в конфігурації детектора.
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
    # Інженерний збирач детектора.
    # Він не малює інтерфейс і не грається в програмний рівень.
    # Його завдання: зібрати частини, підготувати геометрію і передати її далі.

    GeometryReady = Transmission(dict)
    TransferStatus = Transmission(str, str)

    # Ініціалізуємо детектор з базовими порожніми частинами та станом.
    def __init__(self):
        super().__init__()
        self.Parts: dict[str, Any] = {"crystal": None, "shield": None, "collimator": None}
        self.Connector = None
        self.Geometry: dict[str, Any] = {}
        self.LastScanData: dict[str, Any] = {}
        self.EnergyWindow = {"Min": 0.0, "Max": 10000.0}
        self.Sensitivity = 1.0
        self.IsReady = False
        self.Status = "IDLE"

    # Додаємо кристал як окремий інженерний вузол геометрії.
    def AddCrystal(self, Name: str, Material: MaterialEnum, Radius: float, Height: float) -> None:
        self.Parts["crystal"] = {
            "Type": "crystal",
            "Name": Name,
            "Material": Material.value if isinstance(Material, MaterialEnum) else str(Material),
            "RadiusCm": float(Radius),
            "HeightCm": float(Height),
        }

    # Додаємо захист детектора.
    def AddShield(self, Name: str, Material: MaterialEnum, Dimensions: tuple[float, float, float]) -> None:
        self.Parts["shield"] = {
            "Type": "shield",
            "Name": Name,
            "Material": Material.value if isinstance(Material, MaterialEnum) else str(Material),
            "DimensionsCm": tuple(float(Value) for Value in Dimensions),
        }

    # Додаємо коліматор.
    def AddCollimator(self, Name: str, Material: MaterialEnum, InnerRadius: float, OuterRadius: float) -> None:
        self.Parts["collimator"] = {
            "Type": "collimator",
            "Name": Name,
            "Material": Material.value if isinstance(Material, MaterialEnum) else str(Material),
            "InnerRadiusCm": float(InnerRadius),
            "OuterRadiusCm": float(OuterRadius),
        }

    # Підключаємо канал передачі до Geant4 або до будь-якого іншого вузла симуляції.
    def AttachConnector(self, Connector) -> None:
        self.Connector = Connector

    # Поточна позначка часу для конфігурації.
    def Stamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Збираємо фінальну геометрію детектора.
    def BuildGeometry(self) -> dict[str, Any]:
        Geometry = {
            "Detector": {Key: Value for Key, Value in self.Parts.items() if Value is not None},
            "Timestamp": self.Stamp(),
            "Version": "1.0",
            "Ready": True,
        }
        self.Geometry = Geometry
        self.IsReady = True
        self.Status = "READY"
        self.GeometryReady.Emit(Geometry)
        return Geometry

    # Передаємо геометрію далі, якщо є до кого підключитися.
    def SendToGeant4(self) -> bool:
        if not self.Geometry:
            self.BuildGeometry()

        if self.Connector is None:
            self.TransferStatus.Emit("ERROR", "Connector missing")
            self.Status = "OFFLINE"
            return False

        # Спроба знайти метод Send, якщо немає — шукаємо Transmit як запасний варіант.
        Send = getattr(self.Connector, "Send", None)
        if not callable(Send):
            Send = getattr(self.Connector, "Transmit", None)
        if not callable(Send):
            self.TransferStatus.Emit("ERROR", "Connector cannot send geometry")
            self.Status = "OFFLINE"
            return False

        self.TransferStatus.Emit("SENDING", "Geometry transfer started")
        Result = Send(self.Geometry)
        self.TransferStatus.Emit("SENT" if Result else "FAILED", "Geometry transfer finished")
        return bool(Result)

    # Короткий технічний стан вузла.
    def GetStatus(self) -> dict[str, Any]:
        return {
            "Status": self.Status,
            "IsReady": self.IsReady,
            "HasConnector": self.Connector is not None,
            "Parts": {Key: Value for Key, Value in self.Parts.items() if Value is not None},
            "EnergyWindow": self.EnergyWindow,
            "Sensitivity": self.Sensitivity,
        }

    # Приймаємо результати симуляції назад у вузол.
    def ReceiveData(self, Data: dict[str, Any]) -> None:
        if not isinstance(Data, dict):
            return

        if "Hits" in Data:
            self.LastScanData["Hits"] = Data["Hits"]
        if "Energy" in Data:
            self.LastScanData["Energy"] = Data["Energy"]
        self.Status = "UPDATED"
        self.TransferStatus.Emit("RECEIVED", "Simulation data received")

    # Налаштування енергетичного вікна.
    def SetEnergyWindow(self, MinEnergy: float, MaxEnergy: float) -> dict[str, Any]:
        self.EnergyWindow = {"Min": float(MinEnergy), "Max": float(MaxEnergy)}
        return {
            "Status": "CONFIGURED",
            "EnergyWindow": self.EnergyWindow,
            "Message": f"Energy window set: {MinEnergy} - {MaxEnergy} keV",
        }

    # Налаштування чутливості.
    def SetSensitivity(self, Level: float) -> dict[str, Any]:
        self.Sensitivity = max(0.0, min(1.0, float(Level)))
        return {
            "Status": "CONFIGURED",
            "Sensitivity": self.Sensitivity,
            "Message": f"Sensitivity set to {self.Sensitivity:.2%}",
        }

    # Скидаємо вузол у чистий стан.
    def Reset(self) -> dict[str, Any]:
        self.Parts = {"crystal": None, "shield": None, "collimator": None}
        self.Geometry = {}
        self.LastScanData = {}
        self.EnergyWindow = {"Min": 0.0, "Max": 10000.0}
        self.Sensitivity = 1.0
        self.IsReady = False
        self.Status = "IDLE"
        return {"Status": "RESET", "Message": "Detector reset to initial state"}

    # Початкова ініціалізація вузла.
    def Initialize(self) -> dict[str, Any]:
        self.Reset()
        self.Status = "INITIALIZED"
        self.IsReady = True
        return {"Status": "INITIALIZED", "Message": "Detector ready for operation"}

    # Віддаємо повну конфігурацію вузла назовні.
    def ExportConfiguration(self) -> dict[str, Any]:
        if not self.Geometry:
            self.BuildGeometry()
        return {
            "Parts": self.Geometry.get("Detector", {}),
            "EnergyWindow": self.EnergyWindow,
            "Sensitivity": self.Sensitivity,
            "Timestamp": self.Geometry.get("Timestamp", self.Stamp()),
        }
