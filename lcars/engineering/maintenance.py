# ◤ TITANIUM ENGINEERING MAINTENANCE, LIFE SUPPORT & DAMAGE CONTROL 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/maintenance.py
# ОПИС: Єдиний консолідований комплекс технічного обслуговування, життєзабезпечення
#       та аварійного контролю живучості зорельота.
#       Об'єднує в єдину інженерну систему:
#       1. Життєзабезпечення: атмосфера (кисень, тиск, скрубери CO2), клімат палуб, гравітація, рециркуляція.
#       2. Боротьба за живучість: аварійна ізоляція перебірок, силові поля, пожежогасіння, ремонтні бригади.
#       3. Аварійний ремонт: герметизація пробоїн корпусу, відновлення конфігурацій, ліквідація збоїв.
#       4. Регламентне обслуговування: ротація логів, дефрагментація та бекапи баз даних, точки відновлення.
#       5. 3D-матриця міцності корпусу (StructuralIntegrity SystemMatrix).
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================
from __future__ import annotations
from collections import deque
from lcars.base.type import SystemComponent, LCARS, Directive
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN, Transmission
from lcars.core.matrix import SystemMatrix
from lcars.core.conduit import Service
from lcars.modules.storage import ListChipFiles
# ═════════════════════════════════════════════════════════════════════════════
# 1. СИСТЕМА ЖИТТЄЗАБЕЗПЕЧЕННЯ ТА ЕКОЛОГІЧНОГО КОНТРОЛЮ (LIFE SUPPORT)
# ═════════════════════════════════════════════════════════════════════════════
class AtmosphericSystem(LCARS):
    def __init__(self):
        super().__init__()
        self.OxygenPercent = 20.9
        self.NitrogenPercent = 78.08
        self.CarbonDioxidePercent = 0.04
        self.PressureKpa = 101.325
        self.ScrubberEfficiency = 99.8
        self.ReserveTanksPercent = 100.0

    def RegulateAtmosphere(self, OxygenTarget: float = 20.9, PressureTarget: float = 101.325) -> None:
        self.OxygenPercent = max(0.0, min(100.0, float(OxygenTarget)))
        self.PressureKpa = max(0.0, min(200.0, float(PressureTarget)))
        self.CarbonDioxidePercent = 0.04 if self.ScrubberEfficiency > 90.0 else 0.85

    def GetStatus(self) -> dict:
        IsBreathable = (18.5 <= self.OxygenPercent <= 23.5) and (80.0 <= self.PressureKpa <= 110.0)
        return {
            "OxygenPercent": round(self.OxygenPercent, 2),
            "NitrogenPercent": round(self.NitrogenPercent, 2),
            "CarbonDioxidePercent": round(self.CarbonDioxidePercent, 3),
            "PressureKpa": round(self.PressureKpa, 3),
            "ScrubberEfficiency": round(self.ScrubberEfficiency, 1),
            "ReserveTanksPercent": round(self.ReserveTanksPercent, 1),
            "IsBreathable": IsBreathable,
            "Status": "NOMINAL" if IsBreathable else "HAZARD",
        }

class EnvironmentalControl(LCARS):
    def __init__(self):
        super().__init__()
        self.DeckTemperatureC = 21.5
        self.RelativeHumidityPercent = 45.0
        self.ArtificialGravityG = 1.0
        self.InertialDampenersPercent = 100.0
        self.AirCirculationRateM3S = 450.0

    def SetDeckTemperature(self, TargetC: float) -> float:
        self.DeckTemperatureC = max(15.0, min(30.0, float(TargetC)))
        return self.DeckTemperatureC

    def SetGravity(self, ValueG: float) -> float:
        self.ArtificialGravityG = max(0.0, min(2.0, float(ValueG)))
        return self.ArtificialGravityG

    def GetStatus(self) -> dict:
        return {
            "DeckTemperatureC": round(self.DeckTemperatureC, 1),
            "RelativeHumidityPercent": round(self.RelativeHumidityPercent, 1),
            "ArtificialGravityG": round(self.ArtificialGravityG, 2),
            "InertialDampenersPercent": round(self.InertialDampenersPercent, 1),
            "AirCirculationRateM3S": self.AirCirculationRateM3S,
        }

class WaterRecyclingSystem(LCARS):
    def __init__(self):
        super().__init__()
        self.PotableWaterLiters = 85000.0
        self.RecyclerEfficiencyPercent = 99.4
        self.BioFilterStatus = "CLEAN"
        self.DailyConsumptionLiters = 1200.0

    def GetStatus(self) -> dict:
        return {
            "PotableWaterLiters": self.PotableWaterLiters,
            "RecyclerEfficiencyPercent": self.RecyclerEfficiencyPercent,
            "BioFilterStatus": self.BioFilterStatus,
        }

class LifeSupportSystem(SystemComponent):
    Instance = None

    AtmosphereAlert = Transmission(str, dict)
    LifeSupportEmergency = Transmission(str)
    DeckStabilized = Transmission(int)

    def __init__(self):
        super().__init__()
        self.Atmosphere = AtmosphericSystem()
        self.Climate = EnvironmentalControl()
        self.Hydraulics = WaterRecyclingSystem()
        self.ActiveQuarantineDecks: list[int] = []
        self.Version = VersionInfo.GetVersion()

    @classmethod
    def GetInstance(cls) -> LifeSupportSystem:
        if cls.Instance is None:
            cls.Instance = LifeSupportSystem()
        return cls.Instance

    @property
    def OxygenLevelPercent(self) -> float:
        return self.Atmosphere.OxygenPercent

    @property
    def AtmosphericPressureKpa(self) -> float:
        return self.Atmosphere.PressureKpa

    @property
    def DeckTemperatureC(self) -> float:
        return self.Climate.DeckTemperatureC

    def IsAtmosphereBreathable(self) -> bool:
        return self.Atmosphere.GetStatus()["IsBreathable"]

    def SealDeck(self, DeckNumber: int) -> bool:
        TargetDeck = int(DeckNumber)
        if TargetDeck not in self.ActiveQuarantineDecks:
            self.ActiveQuarantineDecks.append(TargetDeck)
            self.LifeSupportEmergency.Emit(f"Deck {TargetDeck} sealed under emergency containment.")
            ODN.Transmit("Engineering.LifeSupport.DeckSealed", Deck=TargetDeck)
            return True
        return False

    def UnsealDeck(self, DeckNumber: int) -> bool:
        TargetDeck = int(DeckNumber)
        if TargetDeck in self.ActiveQuarantineDecks:
            self.ActiveQuarantineDecks.remove(TargetDeck)
            self.DeckStabilized.Emit(TargetDeck)
            ODN.Transmit("Engineering.LifeSupport.DeckUnsealed", Deck=TargetDeck)
            return True
        return False

    def EmergencyOxygenFlush(self, DeckNumber: int | None = None) -> None:
        self.Atmosphere.OxygenPercent = 22.0
        self.Atmosphere.PressureKpa = 101.325
        self.AtmosphereAlert.Emit("OxygenFlush", self.Atmosphere.GetStatus())
        ODN.Transmit("Engineering.LifeSupport.OxygenFlushed", Deck=DeckNumber)

    def GetStatus(self) -> dict:
        Atmo = self.Atmosphere.GetStatus()
        Climate = self.Climate.GetStatus()
        Water = self.Hydraulics.GetStatus()
        IsEmergency = not Atmo["IsBreathable"] or len(self.ActiveQuarantineDecks) > 0

        return {
            "Status": "EMERGENCY" if IsEmergency else "NOMINAL",
            "IsCritical": not Atmo["IsBreathable"],
            "IsEmergency": IsEmergency,
            "Atmosphere": Atmo,
            "Climate": Climate,
            "Water": Water,
            "QuarantinedDecks": list(self.ActiveQuarantineDecks),
            "OxygenLevelPercent": Atmo["OxygenPercent"],
            "CarbonDioxidePercent": Atmo["CarbonDioxidePercent"],
            "AtmosphericPressureKpa": Atmo["PressureKpa"],
            "LifeSupportDeckTempC": Climate["DeckTemperatureC"],
            "Version": self.Version,
        }

# ═════════════════════════════════════════════════════════════════════════════
# 2. АВАРІЙНИЙ КОНТРОЛЬ (DAMAGE CONTROL)
# ═════════════════════════════════════════════════════════════════════════════
class DamageSeverity(LCARS):
    NOMINAL = "NOMINAL"
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"

class DamageControl(SystemComponent):
    Instance = None

    DamageReported = Transmission(str, str)
    BulkheadSealed = Transmission(str)
    HazardNeutralized = Transmission(str)
    TeamsDispatched = Transmission(str, int)

    def __init__(self):
        super().__init__()
        self.Severity = DamageSeverity.NOMINAL
        self.SealedCompartments: list[str] = []
        self.ActiveHazards: list[str] = []
        self.ActiveRepairTeams = 0
        self.ForceFieldsActive = False
        self.Version = VersionInfo.GetVersion()

    @classmethod
    def GetInstance(cls) -> DamageControl:
        if cls.Instance is None:
            cls.Instance = DamageControl()
        return cls.Instance

    def SealCompartment(self, CompartmentId: str) -> bool:
        Compartment = str(CompartmentId)
        if Compartment not in self.SealedCompartments:
            self.SealedCompartments.append(Compartment)
            self.BulkheadSealed.Emit(Compartment)
            ODN.Transmit("Engineering.DamageControl.CompartmentSealed", Compartment=Compartment)
            return True
        return False

    def UnsealCompartment(self, CompartmentId: str) -> bool:
        Compartment = str(CompartmentId)
        if Compartment in self.SealedCompartments:
            self.SealedCompartments.remove(Compartment)
            ODN.Transmit("Engineering.DamageControl.CompartmentUnsealed", Compartment=Compartment)
            return True
        return False

    def SuppressHazard(self, HazardLocation: str) -> bool:
        Location = str(HazardLocation)
        if Location in self.ActiveHazards:
            self.ActiveHazards.remove(Location)
            self.HazardNeutralized.Emit(Location)
            ODN.Transmit("Engineering.DamageControl.HazardSuppressed", Location=Location)
            return True
        return False

    def ReportHazard(self, HazardLocation: str, SeverityLevel: str = DamageSeverity.MODERATE) -> None:
        Location = str(HazardLocation)
        if Location not in self.ActiveHazards:
            self.ActiveHazards.append(Location)
        self.Severity = SeverityLevel
        self.DamageReported.Emit(Location, SeverityLevel)
        ODN.Transmit("Engineering.DamageControl.HazardReported", Location=Location, Severity=SeverityLevel)

    def DispatchRepairTeams(self, TargetSector: str, TeamCount: int = 1) -> int:
        self.ActiveRepairTeams += int(TeamCount)
        self.TeamsDispatched.Emit(str(TargetSector), self.ActiveRepairTeams)
        ODN.Transmit("Engineering.DamageControl.TeamsDispatched", Sector=TargetSector, Teams=TeamCount)
        return self.ActiveRepairTeams

    def RecallRepairTeams(self) -> None:
        self.ActiveRepairTeams = 0
        ODN.Transmit("Engineering.DamageControl.TeamsRecalled", Status="Standby")

    def EngageEmergencyForceFields(self) -> None:
        self.ForceFieldsActive = True
        ODN.Transmit("Engineering.DamageControl.ForceFieldsEngaged", Status="ACTIVE")

    def DisengageEmergencyForceFields(self) -> None:
        self.ForceFieldsActive = False
        ODN.Transmit("Engineering.DamageControl.ForceFieldsDisengaged", Status="OFFLINE")

    def GetStatus(self) -> dict:
        return {
            "Severity": self.Severity,
            "SealedCompartmentsCount": len(self.SealedCompartments),
            "SealedCompartments": list(self.SealedCompartments),
            "ActiveHazardsCount": len(self.ActiveHazards),
            "ActiveHazards": list(self.ActiveHazards),
            "ActiveRepairTeams": self.ActiveRepairTeams,
            "ForceFieldsActive": self.ForceFieldsActive,
            "Version": self.Version,
        }

# ═════════════════════════════════════════════════════════════════════════════
# 3. АВАРІЙНИЙ РЕМОНТ ТА ЦІЛІСНІСТЬ КОРПУСУ (REPAIR SUBSYSTEM)
# ═════════════════════════════════════════════════════════════════════════════
class RepairSystem(SystemComponent):
    Instance = None

    IntegrityBreach = Transmission(str)
    RepairCompleted = Transmission(str)
    CriticalFailure = Transmission(str)

    def __init__(self, SystemId: str = "Engineering.Repair", WorkspaceRoot: any = None):
        super().__init__(SystemId=SystemId)
        self.SystemId = SystemId
        self.Active = True
        self.WorkspaceRoot = Directive.PathDrive(WorkspaceRoot) if WorkspaceRoot else Directive.PathDrive(__file__).resolve().parents[2]
        self.ActiveBreaches: list[str] = []
        self.RepairedSections: list[str] = []
        self.SealedCompartments: list[str] = []
        self.Status = "NOMINAL"
        self.Version = VersionInfo.GetVersion()

    @classmethod
    def GetInstance(cls, WorkspaceRoot: any = None) -> RepairSystem:
        if cls.Instance is None:
            cls.Instance = RepairSystem(WorkspaceRoot=WorkspaceRoot)
        return cls.Instance

    def VerifyHullIntegrity(self) -> bool:
        CriticalSections = ["config", "data", "lcars", "plugins"]
        AllValid = True

        for Section in CriticalSections:
            SectionPath = self.WorkspaceRoot / Section
            if not SectionPath.exists():
                AllValid = False
                self.ActiveBreaches.append(Section)
                self.IntegrityBreach.Emit(f"Missing section: {Section}")
                SectionPath.mkdir(parents=True, exist_ok=True)
                self.RepairedSections.append(Section)
                self.RepairCompleted.Emit(f"Reconstructed directory: {Section}")
                ODN.Transmit("Engineering.Repair.HullBreachSealed", Section=Section)

        self.Status = "RepairsActive" if not AllValid else "NOMINAL"
        return AllValid

    def VerifyAndRepairConfig(self) -> bool:
        ConfigPath = self.WorkspaceRoot / "config" / "config.json"
        ExamplePath = self.WorkspaceRoot / "config" / "config.example.json"

        if not ConfigPath.exists():
            if ExamplePath.exists():
                ConfigPath.write_text(ExamplePath.read_text(encoding="utf-8"), encoding="utf-8")
                self.RepairCompleted.Emit("Restored config.json from example template.")
                return True
            ConfigPath.write_text("{}", encoding="utf-8")
            self.RepairCompleted.Emit("Initialized empty config.json.")
            return True
        return True

    def SealCompartment(self, CompartmentId: str) -> bool:
        if CompartmentId not in self.SealedCompartments:
            self.SealedCompartments.append(CompartmentId)
            ODN.Transmit("Engineering.Repair.CompartmentSealed", Compartment=CompartmentId)
            return True
        return False

    def PurgeAnomalies(self) -> int:
        TargetDirs = [self.WorkspaceRoot / "database", self.WorkspaceRoot / "lcars" / "data"]
        Purged = 0
        for TargetDir in TargetDirs:
            if not TargetDir.exists():
                continue
            for Item in TargetDir.glob("*"):
                Name = Item.name
                if Name.endswith(".tmp") or Name.endswith(".journal") or Name.endswith(".bak"):
                    Item.unlink(missing_ok=True)
                    Purged += 1
        return Purged

    def GetStatus(self) -> dict:
        return {
            "Status": self.Status,
            "ActiveBreachesCount": len(self.ActiveBreaches),
            "ActiveBreaches": list(self.ActiveBreaches),
            "RepairedSections": list(self.RepairedSections),
            "SealedCompartments": list(self.SealedCompartments),
            "Version": self.Version,
        }

# ═════════════════════════════════════════════════════════════════════════════
# 4. СЛУЖБИ ТЕХНІЧНОГО ОБСЛУГОВУВАННЯ ТА ЛОГІВ (MAINTENANCE HELPERS)
# ═════════════════════════════════════════════════════════════════════════════
class LogMaintenance(LCARS):
    MaxLogSize = 5 * 1024 * 1024

    def rotateLogs(self, WorkRoot: any) -> dict:
        LogDir = Directive.PathDrive(WorkRoot) / "logs"
        FreedBytes = 0
        if LogDir.exists():
            for LogFile in LogDir.glob("*.log"):
                if LogFile.is_file():
                    Size = LogFile.stat().st_size
                    if Size > self.MaxLogSize:
                        FreedBytes += Size
                        LogFile.write_text("", encoding="utf-8")
        return {"Task": "LogRotation", "FreedBytes": FreedBytes}

class StructureMaintenance(LCARS):
    RequiredFolders = ["logs", "database", "config", "archive", "plugins"]

    def verify(self, WorkRoot: any) -> tuple[bool, list[str]]:
        MissingFolders: list[str] = []
        Root = Directive.PathDrive(WorkRoot)
        for Folder in self.RequiredFolders:
            FolderPath = Root / Folder
            if not FolderPath.exists():
                MissingFolders.append(Folder)
                FolderPath.mkdir(parents=True, exist_ok=True)
        return (len(MissingFolders) == 0, MissingFolders)

class DatabaseMaintenance(LCARS):
    def defragment(self, DBManager: any | None) -> int:
        Count = 0
        if DBManager and hasattr(DBManager, "Chips"):
            for ChipId in getattr(DBManager, "Chips", {}):
                Count += 1
        return Count

    def backupChipFiles(self, WorkRoot: any) -> int:
        ArchiveDir = Directive.PathDrive(WorkRoot) / "archive" / "Backups"
        ArchiveDir.mkdir(parents=True, exist_ok=True)
        Count = 0
        for Item in ListChipFiles():
            PathRef = Item.get("Path") if isinstance(Item, dict) else Item
            FileObj = Directive.PathDrive(PathRef) if PathRef else None
            if FileObj and FileObj.exists() and FileObj.is_file():
                BackupPath = ArchiveDir / f"{FileObj.stem}.db.backup"
                BackupPath.write_bytes(FileObj.read_bytes())
                Count += 1
        return Count

class RecoveryMaintenance(LCARS):
    def __init__(self) -> None:
        super().__init__()
        self.BackupStore = deque(maxlen=10)
        self.EmergencyState: dict = {
            "active": False,
            "level": 0,
            "AffectedSystems": [],
        }
        self.IsEmergency = False

    def createBackup(self, WorkRoot: any) -> dict:
        State = {
            "workspace": str(WorkRoot),
            "emergency": self.EmergencyState.copy(),
            "timestamp": 0,
        }
        self.BackupStore.append(State)
        return State

    def restoreBackup(self, Index: int = -1) -> bool:
        if not self.BackupStore:
            return False
        if Index < -len(self.BackupStore) or Index >= len(self.BackupStore):
            return False
        State = self.BackupStore[Index]
        self.EmergencyState = State.get("emergency", {"active": False, "level": 0, "AffectedSystems": []})
        self.IsEmergency = bool(self.EmergencyState.get("active", False))
        return True

    def getBackupList(self) -> list[dict]:
        return list(self.BackupStore)

    def triggerEmergency(self, Level: int, Systems: list[str]) -> None:
        self.IsEmergency = True
        self.EmergencyState["active"] = True
        self.EmergencyState["level"] = Level
        self.EmergencyState["AffectedSystems"] = list(Systems)

    def clearEmergency(self) -> None:
        self.IsEmergency = False
        self.EmergencyState["active"] = False
        self.EmergencyState["level"] = 0
        self.EmergencyState["AffectedSystems"] = []

    def getEmergencyStatus(self) -> dict:
        return {
            "IsEmergency": self.IsEmergency,
            "EmergencyState": self.EmergencyState,
            "BackupCount": len(self.BackupStore),
        }

class StructuralIntegrity(Service):
    def __init__(self):
        super().__init__(Id="structural")
        self.Name = "structural"
        self.HullMatrix = SystemMatrix([10, 5, 20], Id="ShipHull")
        self.InitializeHull()

    def InitializeHull(self):
        for X in range(10):
            for Y in range(5):
                for Z in range(20):
                    self.HullMatrix.SetData(X, Y, Z, 100.0)

    def OnStart(self) -> None:
        pass

    def OnStop(self) -> None:
        pass

    def ApplyDamage(self, X: int, Y: int, Z: int, Amount: float):
        Current = self.HullMatrix.GetData(X, Y, Z, default=100.0)
        NewIntegrity = max(0.0, Current - Amount)
        self.HullMatrix.SetData(X, Y, Z, NewIntegrity)
        if NewIntegrity < 20.0:
            ODN.Transmit("Alert.SetLevel", Level="RED")
            ODN.Transmit("System.Broadcast", Message=f"CRITICAL HULL BREACH AT SECTOR {X}-{Y}-{Z}")

    def Repair(self, X: int, Y: int, Z: int, Amount: float):
        Current = self.HullMatrix.GetData(X, Y, Z, default=0.0)
        NewIntegrity = min(100.0, Current + Amount)
        self.HullMatrix.SetData(X, Y, Z, NewIntegrity)

    def GetStatus(self):
        return {
            "name": self.Name,
            "status": "online",
            "hullIntegrity": self.HullMatrix.GetData(0, 0, 0, default=100.0),
            "matrix": self.HullMatrix,
        }

# ═════════════════════════════════════════════════════════════════════════════
# 5. ГОЛОВНИЙ ОБ'ЄДНАНИЙ ПРОТОКОЛ ОБСЛУГОВУВАННЯ (MAINTENANCE PROTOCOL)
# ═════════════════════════════════════════════════════════════════════════════
class MaintenanceProtocol(SystemComponent, RecoveryMaintenance):
    Instance = None

    MaintenanceStarted = Transmission(str)
    MaintenanceCompleted = Transmission(str)
    OptimizationReport = Transmission(dict)
    EmergencyAlert = Transmission(str)
    AutoFixApplied = Transmission(str)
    RecoveryComplete = Transmission(str)

    def __init__(self, WorkspaceRoot: any = None):
        SystemComponent.__init__(self)
        RecoveryMaintenance.__init__(self)

        self.WorkspaceRoot = Directive.PathDrive(WorkspaceRoot) if WorkspaceRoot else Directive.PathDrive(__file__).resolve().parents[2]
        self.LogHelper = LogMaintenance()
        self.StructureHelper = StructureMaintenance()
        self.DatabaseHelper = DatabaseMaintenance()
        self.Structural = StructuralIntegrity()

        # Інтегровані служби життєзабезпечення, пошкоджень та ремонту
        self.LifeSupport = LifeSupportSystem.GetInstance()
        self.DamageControl = DamageControl.GetInstance()
        self.Repair = RepairSystem.GetInstance(self.WorkspaceRoot)

        self.LastCycleReport: dict = {}
        self.Version = VersionInfo.GetVersion()

    @classmethod
    def GetInstance(cls, WorkspaceRoot: any = None) -> MaintenanceProtocol:
        if cls.Instance is None:
            cls.Instance = MaintenanceProtocol(WorkspaceRoot)
        return cls.Instance

    def RunMaintenanceCycle(self, DBManager: any | None = None) -> dict:
        self.MaintenanceStarted.Emit("Starting comprehensive maintenance cycle")
        ODN.Transmit("Engineering.Maintenance.Started", WorkDir=str(self.WorkspaceRoot))

        Ok, Missing = self.StructureHelper.verify(self.WorkspaceRoot)
        LogResult = self.LogHelper.rotateLogs(self.WorkspaceRoot)
        DefragCount = self.DatabaseHelper.defragment(DBManager)
        BackupCount = self.DatabaseHelper.backupChipFiles(self.WorkspaceRoot)
        Purged = self.Repair.PurgeAnomalies()

        # Перевірка життєзабезпечення
        AtmoBreathable = self.LifeSupport.IsAtmosphereBreathable()

        Report = {
            "StructureValid": Ok,
            "MissingFolders": Missing,
            "LogFreedBytes": LogResult.get("FreedBytes", 0),
            "DatabaseDefragmentedChips": DefragCount,
            "ChipBackupsCreated": BackupCount,
            "AnomaliesPurged": Purged,
            "LifeSupportBreathable": AtmoBreathable,
            "DamageSeverity": self.DamageControl.Severity,
            "Status": "COMPLETED",
        }

        self.LastCycleReport = Report
        self.OptimizationReport.Emit(Report)
        self.MaintenanceCompleted.Emit("Comprehensive maintenance cycle completed successfully.")
        ODN.Transmit("Engineering.Maintenance.Completed", **Report)
        return Report

    def VerifyStructure(self) -> bool:
        Ok, Missing = self.StructureHelper.verify(self.WorkspaceRoot)
        return Ok

    def RotateLogs(self) -> dict:
        return self.LogHelper.rotateLogs(self.WorkspaceRoot)

    def DefragmentDatabase(self, DBManager: any | None = None) -> int:
        return self.DatabaseHelper.defragment(DBManager)

    def GetStatus(self) -> dict:
        return {
            "WorkspaceRoot": str(self.WorkspaceRoot),
            "LastCycleReport": self.LastCycleReport,
            "StructuralIntegrity": self.Structural.GetStatus(),
            "LifeSupport": self.LifeSupport.GetStatus(),
            "DamageControl": self.DamageControl.GetStatus(),
            "Repair": self.Repair.GetStatus(),
            "EmergencyStatus": self.getEmergencyStatus(),
            "Version": self.Version,
        }

# ═════════════════════════════════════════════════════════════════════════════
# 6. КАНОНІЧНІ ТОЧКИ ВХОДУ ТА ЕКСПОРТИ
# ═════════════════════════════════════════════════════════════════════════════
LifeSupportCore = LifeSupportSystem.GetInstance
DamageControlCore = DamageControl.GetInstance
RepairSystemCore = RepairSystem.GetInstance
MaintenanceProtocolCore = MaintenanceProtocol.GetInstance

LIFESUPPORT = LifeSupportSystem.GetInstance()
DAMAGECONTROL = DamageControl.GetInstance()
MAINTENANCE = MaintenanceProtocol.GetInstance()
