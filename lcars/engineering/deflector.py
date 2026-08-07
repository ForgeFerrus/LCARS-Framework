# LCARS Engineering Deflector
# Призначення: низинна корабельна захисна система інженерної секції.
# Тут живуть дефлектор, щитова решітка, секторне екранування,
# структурне поле, радіаційний захист і журнал ударів по захисту.
# Avast і Advanced мають користуватися цим вузлом, але не замінювати його.

from typing import Any

from lcars.base.type import SystemComponent
from lcars.core.signal import Transmission


# Основний інженерний вузол дефлектора й щитової решітки.
class DeflectorSystem(SystemComponent):
    ShieldStatusUpdated = Transmission(dict)
    ThreatDetected = Transmission(dict)
    SectorScanned = Transmission(dict)
    ImpactRegistered = Transmission(dict)
    ScreenUpdated = Transmission(dict)
    StructuralFieldUpdated = Transmission(dict)

    def __init__(self):
        super().__init__()
        self.Mode = "STANDBY"
        self.ShieldLevel = 0.0
        self.ShieldStatus = "OFFLINE"
        self.SecurityPolicy = "PASSIVE"
        self.SensorsActive = False
        self.ThreatCount = 0
        self.BlockedThreats = 0
        self.LastScanData: dict[str, Any] = {}
        self.LastThreat: dict[str, Any] = {}
        self.LastImpact: dict[str, Any] = {}
        self.ImpactLog: list[dict[str, Any]] = []
        self.ShieldGrid = self.CreateShieldGrid()
        self.RadiationScreening = self.CreateScreening("RADIATION", 0.0)
        self.ElectromagneticScreening = self.CreateScreening("ELECTROMAGNETIC", 0.0)
        self.PlasmaScreening = self.CreateScreening("PLASMA", 0.0)
        self.StructuralField = {
            "Status": "STANDBY",
            "Integrity": 100.0,
            "Reinforcement": 0.0,
            "Stress": 0.0,
        }
        self.ThreatSignatures = [
            "eval(",
            "exec(",
            "System.Process",
            "subprocess",
            "pickle.loads",
            "marshal.loads",
            "base64.b64decode",
        ]

    # Створює початкову карту секторів щитової решітки.
    def CreateShieldGrid(self) -> dict[str, dict[str, Any]]:
        Grid: dict[str, dict[str, Any]] = {}
        for Sector in ["FORWARD", "AFT", "PORT", "STARBOARD", "DORSAL", "VENTRAL"]:
            Grid[Sector] = {
                "Status": "OFFLINE",
                "Power": 0.0,
                "Integrity": 100.0,
                "Load": 0.0,
                "Hits": 0,
            }
        return Grid

    # Створює один тип технічного екранування.
    def CreateScreening(self, Kind: str, Level: float) -> dict[str, Any]:
        return {
            "Kind": Kind,
            "Status": "OFFLINE",
            "Level": self.ClampLevel(Level),
            "Load": 0.0,
        }

    # Переводить дефлектор у базовий навігаційний режим.
    def ActivateNavigationField(self) -> dict[str, Any]:
        self.Mode = "NAVIGATION"
        self.ShieldStatus = "NAVIGATION"
        self.SecurityPolicy = "PASSIVE"
        self.SensorsActive = True
        self.ShieldLevel = 35.0
        self.DistributeShieldPower(35.0)
        self.SetRadiationScreening(35.0)
        self.SetElectromagneticScreening(25.0)
        self.SetStructuralField(20.0)
        self.BroadcastShieldStatus()
        return self.GetStatus()

    # Піднімає захисне поле до заданої потужності.
    def RaiseShields(self, Level: float = 100.0, Policy: str = "ACTIVE") -> dict[str, Any]:
        self.Mode = "DEFENSE"
        self.ShieldStatus = "ONLINE"
        self.SecurityPolicy = Policy
        self.SensorsActive = True
        self.ShieldLevel = self.ClampLevel(Level)
        self.DistributeShieldPower(self.ShieldLevel)
        self.SetRadiationScreening(self.ShieldLevel)
        self.SetElectromagneticScreening(self.ShieldLevel)
        self.SetPlasmaScreening(self.ShieldLevel * 0.8)
        self.SetStructuralField(self.ShieldLevel * 0.7)
        self.BroadcastShieldStatus()
        return self.GetStatus()

    # Опускає щити, але лишає систему готовою до повторного підняття.
    def LowerShields(self) -> dict[str, Any]:
        self.Mode = "STANDBY"
        self.ShieldStatus = "STANDBY"
        self.SecurityPolicy = "PASSIVE"
        self.ShieldLevel = 0.0
        self.DistributeShieldPower(0.0)
        self.SetRadiationScreening(0.0)
        self.SetElectromagneticScreening(0.0)
        self.SetPlasmaScreening(0.0)
        self.SetStructuralField(0.0)
        self.BroadcastShieldStatus()
        return self.GetStatus()

    # Переводить дефлектор у аварійний максимум без залежності від UI.
    def EmergencyShieldMode(self) -> dict[str, Any]:
        self.Mode = "EMERGENCY"
        self.ShieldStatus = "MAXIMUM"
        self.SecurityPolicy = "EMERGENCY"
        self.SensorsActive = True
        self.ShieldLevel = 100.0
        self.DistributeShieldPower(100.0)
        self.SetRadiationScreening(100.0)
        self.SetElectromagneticScreening(100.0)
        self.SetPlasmaScreening(100.0)
        self.SetStructuralField(95.0)
        self.BroadcastShieldStatus()
        return self.GetStatus()

    # Синхронізує дефлектор із рівнем тривоги системи.
    def SyncPolicy(self, AlertLevel: str) -> dict[str, Any]:
        Level = AlertLevel.upper()

        if Level == "RED":
            return self.EmergencyShieldMode()

        if Level == "YELLOW":
            return self.RaiseShields(85.0, "ACTIVE")

        if Level == "GREEN":
            return self.ActivateNavigationField()

        return self.LowerShields()

    # Рівномірно розподіляє потужність по всій щитовій решітці.
    def DistributeShieldPower(self, Level: float) -> dict[str, dict[str, Any]]:
        Power = self.ClampLevel(Level)
        for SectorData in self.ShieldGrid.values():
            SectorData["Power"] = Power
            SectorData["Status"] = "ONLINE" if Power > 0 else "OFFLINE"
            SectorData["Load"] = Power * (100.0 - float(SectorData["Integrity"])) / 100.0
        return self.ShieldGrid

    # Перерозподіляє енергію на один сектор щитів.
    def RedistributeShieldPower(self, Sector: str, Level: float) -> dict[str, Any]:
        SectorName = Sector.upper()
        if SectorName not in self.ShieldGrid:
            return {"Updated": False, "Reason": "UNKNOWN SECTOR", "Sector": SectorName}

        Power = self.ClampLevel(Level)
        self.ShieldGrid[SectorName]["Power"] = Power
        self.ShieldGrid[SectorName]["Status"] = "ONLINE" if Power > 0 else "OFFLINE"
        self.RefreshGlobalShieldLevel()
        self.BroadcastShieldStatus()
        return {"Updated": True, "Sector": SectorName, "Power": Power}

    # Реєструє удар по сектору щитів і зменшує його цілісність.
    def RegisterImpact(self, Sector: str, Force: float, Kind: str = "KINETIC") -> dict[str, Any]:
        SectorName = Sector.upper()
        if SectorName not in self.ShieldGrid:
            SectorName = "FORWARD"

        ImpactForce = self.ClampLevel(Force)
        SectorData = self.ShieldGrid[SectorName]
        CurrentIntegrity = float(SectorData["Integrity"])
        ShieldPower = float(SectorData["Power"])
        Damage = max(0.0, ImpactForce - ShieldPower * 0.45)
        SectorData["Integrity"] = self.ClampLevel(CurrentIntegrity - Damage)
        SectorData["Load"] = self.ClampLevel(float(SectorData["Load"]) + ImpactForce)
        SectorData["Hits"] = int(SectorData["Hits"]) + 1

        if float(SectorData["Integrity"]) <= 0.0:
            SectorData["Status"] = "BREACHED"
        elif float(SectorData["Integrity"]) < 35.0:
            SectorData["Status"] = "CRITICAL"
        elif ShieldPower > 0.0:
            SectorData["Status"] = "ONLINE"

        self.LastImpact = {
            "Sector": SectorName,
            "Force": ImpactForce,
            "Kind": Kind,
            "Damage": Damage,
            "SectorStatus": SectorData["Status"],
            "SectorIntegrity": SectorData["Integrity"],
        }
        self.ImpactLog.append(self.LastImpact)
        self.RefreshGlobalShieldLevel()
        self.ImpactRegistered.Emit(self.LastImpact)
        self.BroadcastShieldStatus()
        return self.LastImpact

    # Ремонтує один сектор щитів на задану величину.
    def RepairShieldSegment(self, Sector: str, Amount: float = 25.0) -> dict[str, Any]:
        SectorName = Sector.upper()
        if SectorName not in self.ShieldGrid:
            return {"Repaired": False, "Reason": "UNKNOWN SECTOR", "Sector": SectorName}

        Segment = self.ShieldGrid[SectorName]
        Segment["Integrity"] = self.ClampLevel(float(Segment["Integrity"]) + Amount)
        Segment["Load"] = self.ClampLevel(float(Segment["Load"]) - Amount)

        if float(Segment["Power"]) > 0.0:
            Segment["Status"] = "ONLINE"
        else:
            Segment["Status"] = "OFFLINE"

        self.RefreshGlobalShieldLevel()
        self.BroadcastShieldStatus()
        return {"Repaired": True, "Sector": SectorName, "Integrity": Segment["Integrity"]}

    # Відновлює всі сектори щитової решітки.
    def RepairShieldGrid(self, Amount: float = 15.0) -> dict[str, Any]:
        Report: dict[str, Any] = {}
        for Sector in self.ShieldGrid:
            Report[Sector] = self.RepairShieldSegment(Sector, Amount)
        return Report

    # Вмикає або змінює рівень радіаційного екранування.
    def SetRadiationScreening(self, Level: float) -> dict[str, Any]:
        self.RadiationScreening = self.UpdateScreening(self.RadiationScreening, Level)
        self.ScreenUpdated.Emit(self.RadiationScreening)
        return self.RadiationScreening

    # Вмикає або змінює рівень електромагнітного екранування.
    def SetElectromagneticScreening(self, Level: float) -> dict[str, Any]:
        self.ElectromagneticScreening = self.UpdateScreening(self.ElectromagneticScreening, Level)
        self.ScreenUpdated.Emit(self.ElectromagneticScreening)
        return self.ElectromagneticScreening

    # Вмикає або змінює рівень плазмового екранування.
    def SetPlasmaScreening(self, Level: float) -> dict[str, Any]:
        self.PlasmaScreening = self.UpdateScreening(self.PlasmaScreening, Level)
        self.ScreenUpdated.Emit(self.PlasmaScreening)
        return self.PlasmaScreening

    # Оновлює один блок екранування.
    def UpdateScreening(self, Screening: dict[str, Any], Level: float) -> dict[str, Any]:
        Screening["Level"] = self.ClampLevel(Level)
        Screening["Status"] = "ONLINE" if float(Screening["Level"]) > 0.0 else "OFFLINE"
        Screening["Load"] = self.ClampLevel(float(Screening["Level"]) * 0.35)
        return Screening

    # Налаштовує поле структурної цілісності.
    def SetStructuralField(self, Level: float) -> dict[str, Any]:
        Reinforcement = self.ClampLevel(Level)
        self.StructuralField["Status"] = "ONLINE" if Reinforcement > 0.0 else "STANDBY"
        self.StructuralField["Reinforcement"] = Reinforcement
        self.StructuralField["Stress"] = self.ClampLevel(100.0 - Reinforcement)
        self.StructuralFieldUpdated.Emit(self.StructuralField)
        return self.StructuralField

    # Сканує сектор і повертає кількість знайдених програмних загроз.
    def ScanSector(self, Sector: str, FileContents: dict[str, str]) -> int:
        self.SensorsActive = True
        Threats: list[dict[str, str]] = []

        for Filename, Content in FileContents.items():
            if Filename.endswith(".py"):
                for Signature in self.ThreatSignatures:
                    if Signature in Content:
                        Threat = {
                            "Sector": Sector,
                            "Filename": Filename,
                            "Signature": Signature,
                        }
                        Threats.append(Threat)
                        self.RegisterThreat(Threat)

        self.LastScanData = {
            "Sector": Sector,
            "FilesScanned": len(FileContents),
            "Threats": Threats,
            "ThreatCount": len(Threats),
        }
        self.SectorScanned.Emit(self.LastScanData)
        return len(Threats)

    # Реєструє одну загрозу й передає її в канал дефлектора.
    def RegisterThreat(self, Threat: dict[str, Any]) -> None:
        self.ThreatCount += 1
        self.LastThreat = Threat
        self.ThreatDetected.Emit(Threat)

    # Вважає загрозу заблокованою дефлекторним полем.
    def DeflectThreat(self, Threat: dict[str, Any]) -> dict[str, Any]:
        self.BlockedThreats += 1
        self.LastThreat = Threat
        Impact = {
            "Sector": str(Threat.get("Sector", "FORWARD")),
            "Force": 15.0,
            "Kind": "SOFTWARE",
        }
        self.RegisterImpact(Impact["Sector"], Impact["Force"], Impact["Kind"])
        return {
            "Blocked": True,
            "BlockedThreats": self.BlockedThreats,
            "Threat": Threat,
            "ShieldLevel": self.ShieldLevel,
        }

    # Заряджає щити до максимуму без зміни поточного режиму.
    def RechargeShields(self) -> dict[str, Any]:
        self.ShieldLevel = 100.0
        self.ShieldStatus = "ONLINE"
        self.DistributeShieldPower(100.0)
        self.BroadcastShieldStatus()
        return self.GetStatus()

    # Оновлює загальний рівень щитів як середнє по секторах.
    def RefreshGlobalShieldLevel(self) -> float:
        Total = 0.0
        Count = 0
        for SectorData in self.ShieldGrid.values():
            Total += float(SectorData["Power"]) * float(SectorData["Integrity"]) / 100.0
            Count += 1

        if Count == 0:
            self.ShieldLevel = 0.0
        else:
            self.ShieldLevel = self.ClampLevel(Total / Count)

        if self.ShieldLevel <= 0.0:
            self.ShieldStatus = "OFFLINE"
        elif self.ShieldLevel < 35.0:
            self.ShieldStatus = "CRITICAL"
        elif self.Mode == "EMERGENCY":
            self.ShieldStatus = "MAXIMUM"
        else:
            self.ShieldStatus = "ONLINE"

        return self.ShieldLevel

    # Передає поточний стан щитів у сигнал.
    def BroadcastShieldStatus(self) -> None:
        self.ShieldStatusUpdated.Emit(self.GetStatus())

    # Обмежує значення в межах 0-100.
    def ClampLevel(self, Level: float) -> float:
        if Level < 0.0:
            return 0.0
        if Level > 100.0:
            return 100.0
        return Level

    # Повертає стан щитової решітки окремо від решти дефлектора.
    def GetShieldGridStatus(self) -> dict[str, Any]:
        return {
            "GlobalLevel": self.ShieldLevel,
            "Status": self.ShieldStatus,
            "Sectors": self.ShieldGrid,
            "LastImpact": self.LastImpact,
        }

    # Повертає стан усіх типів екранування.
    def GetScreeningStatus(self) -> dict[str, Any]:
        return {
            "Radiation": self.RadiationScreening,
            "Electromagnetic": self.ElectromagneticScreening,
            "Plasma": self.PlasmaScreening,
            "StructuralField": self.StructuralField,
        }

    # Повертає повний стан дефлектора для контролера, колектора й UI.
    def GetStatus(self) -> dict[str, Any]:
        return {
            "Mode": self.Mode,
            "ShieldLevel": self.ShieldLevel,
            "ShieldStatus": self.ShieldStatus,
            "SecurityPolicy": self.SecurityPolicy,
            "SensorsActive": self.SensorsActive,
            "ThreatCount": self.ThreatCount,
            "BlockedThreats": self.BlockedThreats,
            "ShieldGrid": self.ShieldGrid,
            "Screening": self.GetScreeningStatus(),
            "LastScan": self.LastScanData,
            "LastThreat": self.LastThreat,
            "LastImpact": self.LastImpact,
            "ImpactLog": self.ImpactLog[-20:],
        }
