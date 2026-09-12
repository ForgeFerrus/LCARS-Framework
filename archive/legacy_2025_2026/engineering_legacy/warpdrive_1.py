# LCARS PROPULSION SYSTEM - ENGINEERING LAYER
# ПРИЗНАЧЕННЯ: Керування імпульсними та варп-двигунами
# СТАНДАРТ: Titanium Master (No-Except, No-OS, No-JSON)

from __future__ import annotations
# Titanium Bridge Migration: from typing import Any

from lcars.base.type import SystemComponent
from lcars.base.signal import Signal, Transmission, ODN

# Electro-Plasma System (EPS). Розподіл енергії між системами.
class EPSConduit(SystemComponent):
    def __init__(self, Capacity: float = 1000.0):
        super().__init__()
        self.Capacity = Capacity
        self.Load = 0.0
        self.Status = "NOMINAL"
        # Канал оновлення потужності
        self.PowerChannel = Transmission(float, float)

    def AdjustLoad(self, Amount: float) -> None:
        # Зміна навантаження з перевіркою лімітів
        self.Load = max(0.0, min(self.Capacity * 1.5, self.Load + Amount))

        if self.Load > self.Capacity * 1.2:
            self.Status = "CRITICAL"
        elif self.Load > self.Capacity:
            self.Status = "OVERLOAD"
        else:
            self.Status = "NOMINAL"

        # Emit через ODN канал Engineering
        ODN.Emit("Systems.Engineering", {"EPS": self.GetStatus()})
        self.PowerChannel.Emit(self.Load, self.Capacity)

    def GetStatus(self) -> dict[str, Any]:
        return {
            "Load": self.Load,
            "Capacity": self.Capacity,
            "Status": self.Status,
            "Percent": (self.Load / self.Capacity) * 100 if self.Capacity > 0 else 0,
        }

# Reaction Control System (RCS). Маневрові двигуни орієнтації.
class ThrusterSystem(SystemComponent):
    def __init__(self):
        super().__init__()
        self.FuelLevel = 100.0
        self.Active = True
        self.Orientation = {"Pitch": 0.0, "Yaw": 0.0, "Roll": 0.0}
        self.ThrusterChannel = Transmission(str, float)

    def Fire(self, Axis: str, Intensity: float) -> bool:
        # Запуск маневрового двигуна
        if not self.Active or self.FuelLevel <= 0:
            return False

        FuelCost = Intensity * 0.1
        self.FuelLevel = max(0.0, self.FuelLevel - FuelCost)
        Current = self.Orientation.get(Axis, 0.0)
        self.Orientation[Axis] = (Current + Intensity) % 360

        # Emit через ODN
        ODN.Emit("Systems.ImpulseEngines", {"Axis": Axis, "Intensity": Intensity})
        self.ThrusterChannel.Emit(Axis, Intensity)
        return True

    def GetStatus(self) -> dict[str, Any]:
        return {
            "Fuel": self.FuelLevel,
            "Active": self.Active,
            "Orientation": self.Orientation,
        }

# Головна рушійна установка (Impulse / Warp Core).
class WarpDrive(SystemComponent):
    # Сигнал зміни режиму: новий режим
    StatusChanged = Signal(str)

    def __init__(self):
        super().__init__()
        # Поточний режим: standby, impulse, warp, autodestruct
        self.mode = "standby"
        # Варп-фактор від 0.0 до 9.9
        self.WarpFactor = 0.0
        # Стабільність ядра від 0 до 100
        self.CoreStability = 100.0
        # Потік плазми в відсотках
        self.PlasmaFlow = 0.0
        self.ResonanceFreq = 42.0
        self.DilithiumIntegrity = 100.0
        self.StructuralNodes = []

        # Підсистеми
        self.EPS = EPSConduit(Capacity=1200.0)
        self.Thrusters = ThrusterSystem()

        # Параметри матерії та резонансу
        self.ResonanceFreq = 42.0
        self.DilithiumIntegrity = 100.0

    def SetMode(self, Mode: str) -> None:
        # Встановлення режиму роботи двигуна
        # impulse — маневрування, warp — FTL швидкість, standby — очікування
        ModeStr = Mode.upper()

        if ModeStr == "IMPULSE":
            self.mode = "impulse"
            self.WarpFactor = 0.0
            self.PlasmaFlow = 25.0
            self.EPS.AdjustLoad(100.0)

        elif ModeStr == "WARP":
            self.mode = "warp"
            self.PlasmaFlow = 100.0
            self.EPS.AdjustLoad(400.0)

        elif ModeStr == "AUTODESTRUCT":
            self.mode = "autodestruct"
            self.CoreStability = 0.0
            self.PlasmaFlow = 0.0

        else:
            # STANDBY або будь-який інший варіант
            self.mode = "standby"
            self.WarpFactor = 0.0
            self.PlasmaFlow = 5.0
            self.EPS.AdjustLoad(-200.0)

        # Emit через ODN канали
        ODN.Emit("Systems.WarpDrive", {"Mode": self.mode, "WarpFactor": self.WarpFactor})
        ODN.Emit("Updates.Status", {"System": "WarpDrive", "Mode": self.mode})
        self.StatusChannel.Emit(self.mode)

    def SetWarpFactor(self, Factor: float) -> bool:
        # Встановлення варп-фактора від 0.0 до 9.9
        # Автоматично перемикає в режим warp якщо Factor > 0
        if not (0.0 <= Factor <= 9.9):
            return False

        self.WarpFactor = Factor
        if Factor > 0:
            if self.mode != "warp":
                self.SetMode("warp")
        else:
            self.SetMode("standby")

        ODN.Emit("Systems.WarpDrive", {"WarpFactor": self.WarpFactor})
        return True

    def GetStatus(self) -> dict[str, Any]:
        # Отримання повного статусу двигуна
        return {
            "Mode": self.mode,
            "WarpFactor": self.WarpFactor,
            "CoreStability": self.CoreStability,
            "PlasmaFlow": self.PlasmaFlow,
            "Resonance": self.ResonanceFreq,
            "Dilithium": self.DilithiumIntegrity,
            "EPS": self.EPS.GetStatus(),
            "Thrusters": self.Thrusters.GetStatus(),
        }

    def InjectWarpMatrix(self, Nodes: list) -> None:
        # Ін'єкція вузлів геометрії для передачі в Geant4
        if self.mode != "warp":
            return
        if not Nodes:
            return
        self.StructuralNodes = Nodes

    def GenerateWarpField(self) -> str:
        # Генерація команд геометрії для Geant4
        if self.mode != "warp":
            return ""
        if not self.StructuralNodes:
            return ""
        Instructions = []
        for N in self.StructuralNodes:
            Name = N.get("Name", "UnknownZone")
            Shape = N.get("Type", "box")
            Instructions.append(f"/lcars/geom/add {Shape} {Name}")
        return "\n".join(Instructions)

# Експорт класів
DriveModule = WarpDrive
PropulsionSystem = WarpDrive
