# ◤ LCARS ENGINEERING :: MASTER SYSTEM & CHIP ARCHITECT 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/architect.py
# ОПИС: Головне Конструкторське Бюро ізолінійних чіпів та системної топології LCARS.
#       Повний інженерний арсенал:
#       1. Спеціалізовані архетипи чіпів (Database, Service, Interface, Subsystem, Science).
#       2. Проєктування та синтез маніфестів (ConstructChip / ConstructFromArchetype).
#       3. Автоматичний підбір вільних слотів у секторах (GetNextAvailableNumber).
#       4. Збереження маніфестів на диск у форматі YAML (SaveChipToDisk).
#       5. Автоматичне розгортання SQLite баз даних чіпів (ScaffoldChipDatabase).
#       6. Топологія 12 категорій оптичної шини даних ODN (GetBusTopology).
#       7. Інспектор заповнення секторів матриці (InspectSectorMatrix).
#       8. Аудит графа залежностей та навантаження шини (AuditDependencyGraph).
#       9. Генерація майстер-креслення всієї системи (ExportSystemMasterBlueprint).
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import SystemComponent, LCARS
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN

# Стандартні архітектурні профілі системи (25-те століття)
class SystemProfile(LCARS):
    # Основні класи 25-го століття (Primary 25th Century)
    Odyssey = "ODYSSEY"
    Titan = "TITAN"

    # Спадкові опції 24-го століття (24th Century Legacy Options)
    Sovereign = "SOVEREIGN"
    Galaxy = "GALAXY"
    Defiant = "DEFIANT"
    Intrepid = "INTREPID"

    # Аліаси сумісності
    Workstation = Odyssey
    HeavyStation = Titan
    MobilePADD = Defiant
    Scientific = Intrepid

ShipClass = SystemProfile

# Архітектурні архетипи ізолінійних чіпів
class ChipArchetype(LCARS):
    Database = "Database"
    Service = "Service"
    Interface = "Interface"
    Subsystem = "Subsystem"
    Science = "Science"

# Головне Конструкторське Бюро чіпів та системної топології
class EngineeringArchitect(SystemComponent):
    Instance = None

    # Архітектурні профілі навантаження шини даних
    Profiles = {
        SystemProfile.Odyssey: {
            "ProfileName": "Odyssey Class Dreadnought (25th Century Flagship)",
            "Era": "25th",
            "MaxBusThroughput": 8500.0,
            "TargetArrays": 16,
            "ShieldGenerators": 18,
        },
        SystemProfile.Titan: {
            "ProfileName": "Titan Class Multi-Mission Cruiser (25th Century)",
            "Era": "25th",
            "MaxBusThroughput": 7200.0,
            "TargetArrays": 14,
            "ShieldGenerators": 16,
        },
        SystemProfile.Sovereign: {
            "ProfileName": "Sovereign Heavy Cruiser Profile",
            "Era": "24th",
            "MaxBusThroughput": 6000.0,
            "TargetArrays": 12,
            "ShieldGenerators": 14,
        },
        SystemProfile.Galaxy: {
            "ProfileName": "Galaxy Explorer Profile",
            "Era": "24th",
            "MaxBusThroughput": 4500.0,
            "TargetArrays": 11,
            "ShieldGenerators": 10,
        },
        SystemProfile.Defiant: {
            "ProfileName": "Defiant Tactical Escort Profile",
            "Era": "24th",
            "MaxBusThroughput": 5200.0,
            "TargetArrays": 4,
            "ShieldGenerators": 8,
        },
        SystemProfile.Intrepid: {
            "ProfileName": "Intrepid Science Profile",
            "Era": "24th",
            "MaxBusThroughput": 3800.0,
            "TargetArrays": 8,
            "ShieldGenerators": 10,
        },
    }

    # Канонічна топологія 12 категорій оптичної шини даних ODN
    BusTopology = {
        "01": {"Category": "Core", "Name": "Primary Core and Master System", "Bus": "ODN-01"},
        "02": {"Category": "Engineering", "Name": "Propulsion and Power Systems", "Bus": "ODN-02"},
        "03": {"Category": "Tactical", "Name": "Deflector and Tactical Shields", "Bus": "ODN-03"},
        "04": {"Category": "Navigation", "Name": "Stardate and Navigation Sensors", "Bus": "ODN-04"},
        "05": {"Category": "Science", "Name": "Physics Sensors and Geant4 Engine", "Bus": "ODN-05"},
        "06": {"Category": "Communication", "Name": "SubspaceLink and Voice Comlink", "Bus": "ODN-06"},
        "07": {"Category": "Interface", "Name": "LCARS PADD and UI Matrix", "Bus": "ODN-07"},
        "08": {"Category": "Security", "Name": "Authorization and Access Protocols", "Bus": "ODN-08"},
        "09": {"Category": "LifeSupport", "Name": "Environmental Monitoring Grid", "Bus": "ODN-09"},
        "10": {"Category": "Library", "Name": "Archival Knowledge Base", "Bus": "ODN-10"},
        "11": {"Category": "Maintenance", "Name": "Diagnostic and AutoRepair", "Bus": "ODN-11"},
        "12": {"Category": "External", "Name": "Subspace Transceiver Relays", "Bus": "ODN-12"},
    }

    def __init__(self, CurrentProfile: str = SystemProfile.Odyssey):
        super().__init__()
        self.CurrentClass = CurrentProfile
        self.ActiveProfile = self.Profiles.get(CurrentProfile, self.Profiles[SystemProfile.Odyssey])
        self.Version = VersionInfo.GetVersion()
        PathModule = LCARS.System.Path
        self.ChipsRoot = PathModule("lcars/engineering/chips")
        self.DataRoot = PathModule("lcars/data")

    @classmethod
    def GetInstance(cls, CurrentProfile: str = SystemProfile.Odyssey) -> EngineeringArchitect:
        if cls.Instance is None:
            cls.Instance = EngineeringArchitect(CurrentProfile=CurrentProfile)
        return cls.Instance

    # Зміна системного профілю
    def ConfigureClass(self, NewProfile: str) -> dict:
        ProfileKey = str(NewProfile or "").upper().strip()
        if ProfileKey in self.Profiles:
            self.CurrentClass = ProfileKey
            self.ActiveProfile = self.Profiles[ProfileKey]
            ODN.Transmit("Engineering.Architect.ProfileConfigured", Profile=ProfileKey)
            return dict(self.ActiveProfile)
        return dict(self.ActiveProfile)

    # Автоматичний пошук наступного вільного номера чіпа в секторі
    def GetNextAvailableNumber(self, Sector: str) -> str:
        SectorStr = f"{int(Sector):02d}" if str(Sector).isdigit() else str(Sector)
        SectorDir = self.ChipsRoot / SectorStr
        if not SectorDir.exists():
            return "0001"

        UsedNumbers = set()
        for FilePath in SectorDir.glob("*.yaml"):
            FileName = FilePath.stem
            if "-" in FileName:
                Parts = FileName.split("-")
                if len(Parts) == 2 and Parts[1].isdigit():
                    UsedNumbers.add(int(Parts[1]))

        Candidate = 1
        while Candidate in UsedNumbers:
            Candidate += 1
        return f"{Candidate:04d}"

    # Проєктування та синтез маніфесту ізолінійного чіпа
    def ConstructChip(self, Sector: str, ChipNumber: str | None = None, Name: str = "LCARS Generic Chip",
                      Role: str = "generic", ChipType: str = "database",
                      BlueLevel: int = 3, GreenLevel: int = 4,
                      Entrypoint: str = "", DatabaseFile: str = "",
                      ConfigParams: dict | None = None,
                      Dependencies: list[str] | None = None) -> dict:
        SectorStr = f"{int(Sector):02d}" if str(Sector).isdigit() else str(Sector)
        NumberStr = ChipNumber if ChipNumber else self.GetNextAvailableNumber(SectorStr)
        NumberStr = f"{int(NumberStr):04d}" if str(NumberStr).isdigit() else str(NumberStr)
        ChipId = f"{SectorStr}-{NumberStr}"
        BusName = f"ODN-{SectorStr}"

        Manifest = {
            "Metadata": {
                "Id": ChipId,
                "Name": Name,
                "Version": self.Version,
                "Faction": "Federation",
                "Type": ChipType.lower(),
                "Category": SectorStr,
                "Number": NumberStr,
            },
            "Specs": {
                "Capacity": 2000,
                "ColorCode": "#99CCFF",
                "SecurityLevel": max(1, min(10, int(BlueLevel + GreenLevel))),
                "Priority": max(1, min(5, int(BlueLevel))),
                "Bus": BusName,
            },
            "Entrypoints": {
                "Main": Entrypoint or f"lcars.modules.{Role.lower()}:Initialize{Role}",
            },
            "Paths": {
                "DatabaseFile": DatabaseFile or f"lcars/data/{SectorStr}/{ChipId}-{Role.lower()}.db",
                "Tables": ["Records", "Logs", "Status"],
            },
            "Config": ConfigParams or {
                "Active": True,
                "AutoSync": True,
            },
            "Dependencies": Dependencies or ["core.alpha", "engineering.isolinear"],
        }
        ODN.Transmit("Engineering.Architect.ChipConstructed", ChipId=ChipId, Role=Role)
        return Manifest

    # Синтез чіпа за спеціалізованим архетипом
    def ConstructFromArchetype(self, Archetype: str, Sector: str, Name: str, Role: str,
                               ChipNumber: str | None = None, CustomConfig: dict | None = None) -> dict:
        ArchUpper = str(Archetype or "").capitalize()
        NumStr = ChipNumber or self.GetNextAvailableNumber(Sector)
        SectorStr = f"{int(Sector):02d}" if str(Sector).isdigit() else str(Sector)

        if ArchUpper == ChipArchetype.Database:
            Cfg = {"Engine": "SQLite", "JournalMode": "WAL", "CacheSizeKb": 4096}
            if CustomConfig:
                Cfg.update(CustomConfig)
            return self.ConstructChip(Sector=SectorStr, ChipNumber=NumStr, Name=Name, Role=Role,
                                      ChipType="database", BlueLevel=3, GreenLevel=3, ConfigParams=Cfg)

        elif ArchUpper == ChipArchetype.Service:
            Cfg = {"TcpPort": 8000 + int(SectorStr), "MaxConnections": 64, "KeepAliveSec": 60}
            if CustomConfig:
                Cfg.update(CustomConfig)
            return self.ConstructChip(Sector=SectorStr, ChipNumber=NumStr, Name=Name, Role=Role,
                                      ChipType="service", BlueLevel=4, GreenLevel=4, ConfigParams=Cfg)

        elif ArchUpper == ChipArchetype.Interface:
            Cfg = {"LayoutStandard": "Titanium", "GridDensity": 5, "Palette": "Standard"}
            if CustomConfig:
                Cfg.update(CustomConfig)
            return self.ConstructChip(Sector=SectorStr, ChipNumber=NumStr, Name=Name, Role=Role,
                                      ChipType="interface", BlueLevel=2, GreenLevel=3, ConfigParams=Cfg)

        elif ArchUpper == ChipArchetype.Subsystem:
            Cfg = {"SubsystemId": f"Subsystem.{Role}", "AutoOnline": True, "DiagnosticsInterval": 30}
            if CustomConfig:
                Cfg.update(CustomConfig)
            return self.ConstructChip(Sector=SectorStr, ChipNumber=NumStr, Name=Name, Role=Role,
                                      ChipType="subsystem", BlueLevel=5, GreenLevel=5, ConfigParams=Cfg)

        elif ArchUpper == ChipArchetype.Science:
            Cfg = {"PhysicsEngine": "Geant4", "Precision": "Double", "ComputeThreads": 4}
            if CustomConfig:
                Cfg.update(CustomConfig)
            return self.ConstructChip(Sector=SectorStr, ChipNumber=NumStr, Name=Name, Role=Role,
                                      ChipType="science", BlueLevel=4, GreenLevel=5, ConfigParams=Cfg)

        return self.ConstructChip(Sector=SectorStr, ChipNumber=NumStr, Name=Name, Role=Role, ConfigParams=CustomConfig)

    # Збереження згенерованого маніфесту у файл YAML на диску
    def SaveChipToDisk(self, Manifest: dict, Overwrite: bool = False) -> dict:
        Meta = Manifest.get("Metadata", {})
        ChipId = Meta.get("Id")
        Category = Meta.get("Category", "01")
        if not ChipId:
            return {"Status": "Error", "Message": "Manifest missing Id"}

        TargetDir = self.ChipsRoot / Category
        TargetDir.mkdir(parents=True, exist_ok=True)
        TargetFile = TargetDir / f"{ChipId}.yaml"

        if TargetFile.exists() and not Overwrite:
            return {"Status": "FileExists", "FilePath": str(TargetFile).replace("\\", "/")}

        YamlMod = LCARS.Import("yaml")
        if YamlMod and hasattr(YamlMod, "dump"):
            YamlContent = YamlMod.dump(Manifest, sort_keys=False, default_flow_style=False, allow_unicode=True)
            TargetFile.write_text(YamlContent, encoding="utf-8")
        else:
            # Чистий автономний генератор YAML без зовнішніх бібліотек
            Lines = []
            for Section, Data in Manifest.items():
                Lines.append(f"{Section}:")
                if isinstance(Data, dict):
                    for K, V in Data.items():
                        if isinstance(V, list):
                            Lines.append(f"  {K}:")
                            for Item in V:
                                Lines.append(f"    - {Item}")
                        elif isinstance(V, dict):
                            Lines.append(f"  {K}:")
                            for SubK, SubV in V.items():
                                Lines.append(f"    {SubK}: {SubV}")
                        else:
                            Lines.append(f"  {K}: {V}")
                elif isinstance(Data, list):
                    for Item in Data:
                        Lines.append(f"  - {Item}")
            TargetFile.write_text("\n".join(Lines) + "\n", encoding="utf-8")

        ODN.Transmit("Engineering.Architect.ChipPersisted", ChipId=ChipId, Path=str(TargetFile))
        return {
            "Status": "Success",
            "ChipId": ChipId,
            "FilePath": str(TargetFile).replace("\\", "/"),
        }

    # Автоматичне розгортання бази даних чіпа
    def ScaffoldChipDatabase(self, Manifest: dict) -> dict:
        Paths = Manifest.get("Paths", {})
        DbFileStr = Paths.get("DatabaseFile", "")
        Tables = Paths.get("Tables", ["Records", "Logs", "Status"])
        if not DbFileStr:
            return {"Status": "Skipped", "Message": "No database path declared"}

        PathModule = LCARS.System.Path
        DbPath = PathModule(DbFileStr)
        DbPath.parent.mkdir(parents=True, exist_ok=True)

        SqliteMod = LCARS.Import("sqlite3")
        if SqliteMod and hasattr(SqliteMod, "connect"):
            Conn = SqliteMod.connect(str(DbPath))
            Cur = Conn.cursor()
            for TableName in Tables:
                Cur.execute(f"CREATE TABLE IF NOT EXISTS {TableName} (Id INTEGER PRIMARY KEY AUTOINCREMENT, Key TEXT, Value TEXT, Timestamp REAL)")
            Conn.commit()
            Conn.close()

        ODN.Transmit("Engineering.Architect.DatabaseScaffolded", Database=str(DbPath))
        return {
            "Status": "DatabaseScaffolded",
            "DatabasePath": str(DbPath).replace("\\", "/"),
            "TablesCreated": Tables,
        }

    # Валідація схеми маніфесту чіпа на відповідність канону
    def ValidateChipBlueprint(self, Manifest: dict) -> dict:
        Errors = []
        RequiredSections = ["Metadata", "Specs", "Entrypoints", "Paths", "Config", "Dependencies"]
        for Section in RequiredSections:
            if Section not in Manifest:
                Errors.append(f"MissingRequiredSection:{Section}")

        Meta = Manifest.get("Metadata", {})
        if not Meta.get("Id"):
            Errors.append("MissingMetadataId")
        if not Meta.get("Name"):
            Errors.append("MissingMetadataName")

        return {
            "Valid": len(Errors) == 0,
            "Errors": Errors,
            "ChipId": Meta.get("Id", "Unknown"),
        }

    # Інспектор заповнення сектору чіпів
    def InspectSectorMatrix(self, Sector: str) -> dict:
        SectorStr = f"{int(Sector):02d}" if str(Sector).isdigit() else str(Sector)
        SectorDir = self.ChipsRoot / SectorStr
        ChipsInfo = []
        if SectorDir.exists():
            for FilePath in sorted(SectorDir.glob("*.yaml")):
                ChipsInfo.append({
                    "FileName": FilePath.name,
                    "ChipId": FilePath.stem,
                    "SizeBytes": FilePath.stat().st_size,
                })

        BusMeta = self.BusTopology.get(SectorStr, {"Category": "Unknown", "Name": "Unknown", "Bus": f"ODN-{SectorStr}"})
        return {
            "Sector": SectorStr,
            "Category": BusMeta["Category"],
            "Bus": BusMeta["Bus"],
            "InstalledChipsCount": len(ChipsInfo),
            "InstalledChips": ChipsInfo,
            "NextAvailableSlot": self.GetNextAvailableNumber(SectorStr),
        }

    # Отримання топології шини ODN
    def GetBusTopology(self) -> dict:
        return dict(self.BusTopology)

    # Аудит графа залежностей між чіпами
    def AuditDependencyGraph(self, LoadedChips: dict) -> dict:
        AllIds = set(LoadedChips.keys())
        Unresolved = {}
        for ChipId, ChipObj in LoadedChips.items():
            Deps = getattr(ChipObj, "Dependencies", []) or []
            Missing = [D for D in Deps if D not in AllIds and not D.startswith("core.")]
            if Missing:
                Unresolved[ChipId] = Missing
        return {
            "TotalChips": len(LoadedChips),
            "UnresolvedCount": len(Unresolved),
            "UnresolvedDependencies": Unresolved,
            "Status": "OPTIMAL" if not Unresolved else "MissingDependencies",
        }

    # Аудит навантаження розподілу потужностей
    def AuditPowerGrid(self, Allocations: dict) -> dict:
        TotalRequested = sum(float(V) for V in Allocations.values())
        MaxAllowed = float(self.ActiveProfile["MaxBusThroughput"])
        Ratio = TotalRequested / MaxAllowed if MaxAllowed > 0 else 1.0

        Status = "OPTIMAL"
        WarningMsg = None
        if Ratio > 1.0:
            Status = "OverloadCritical"
            WarningMsg = f"Allocations {TotalRequested:.1f} exceed capacity {MaxAllowed:.1f}"
        elif Ratio > 0.85:
            Status = "HighStrain"
            WarningMsg = f"Near peak capacity {Ratio * 100.0:.1f}%"

        Audit = {
            "Profile": self.CurrentClass,
            "Capacity": MaxAllowed,
            "Allocated": TotalRequested,
            "LoadRatio": round(Ratio, 4),
            "Status": Status,
            "Warning": WarningMsg,
        }
        ODN.Transmit("Engineering.Architect.PowerGridAudited", Audit=Audit)
        return Audit

    # Аудит цілісності оптичної мережі ODN
    def AuditOpticalNetwork(self, LoadedChipsCount: int = 42) -> dict:
        TargetArrays = self.ActiveProfile["TargetArrays"]
        Status = "HEALTHY"
        if LoadedChipsCount == 0:
            Status = "OfflineNoChips"
        elif LoadedChipsCount < TargetArrays:
            Status = "SuboptimalSparseChips"

        return {
            "Profile": self.CurrentClass,
            "TargetArrays": TargetArrays,
            "MountedChips": LoadedChipsCount,
            "NetworkStatus": Status,
        }

    # Генерація повного майстер-креслення всієї системи
    def ExportSystemMasterBlueprint(self) -> dict:
        SectorReports = {Sec: self.InspectSectorMatrix(Sec) for Sec in sorted(self.BusTopology.keys())}
        TotalInstalled = sum(Report["InstalledChipsCount"] for Report in SectorReports.values())

        return {
            "FrameworkVersion": self.Version,
            "SystemProfile": self.CurrentClass,
            "BusTopologyCategories": len(self.BusTopology),
            "TotalInstalledChips": TotalInstalled,
            "Sectors": SectorReports,
            "Timestamp": LCARS.System.Time.time() if hasattr(LCARS.System, "Time") else 0.0,
        }

# Аліаси сумісності
GenerateChipManifest = EngineeringArchitect.GetInstance().ConstructChip
Architect = EngineeringArchitect.GetInstance
ARCHITECT = EngineeringArchitect.GetInstance()
IsolinearArchitect = EngineeringArchitect