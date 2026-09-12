# ◤ LCARS DEFENSE PERIMETER & DEFLECTOR SHIELD ENGINE 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/deflector.py
# ОПИС: Головний дефлекторний щит, мережа силових екранів та автономний кіберзахист.
#       Містить об'єктні типи екранів (ShieldScreen), сітку щитів (ShieldGrid),
#       фізику поглинання урону (AbsorbDamage), частотну модуляцію
#       та активний сигнатурний сканер файлових систем.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
# Titanium Bridge Migration: from typing import Any

from lcars.base.type import SystemComponent, Directive, LCARS
from lcars.core.signal import Transmission, ODN

# Типи захисних екранів та силових полів зорельота
class ShieldType(LCARS):
    TACTICAL = "TACTICAL"
    NAVIGATIONAL = "NAVIGATIONAL"
    FORCEFIELD = "FORCEFIELD"
    METAPHASIC = "METAPHASIC"
    REGENERATIVE = "REGENERATIVE"

# Окремий силовий екран / емітер сектора
class ShieldScreen(LCARS):
    def __init__(self, Quadrant: str, ScreenType: str = ShieldType.TACTICAL, FrequencyMhz: float = 257.4):
        super().__init__()
        self.Quadrant = Quadrant
        self.ScreenType = ScreenType
        self.Active = True
        self.EnergyLevel = 0.0
        self.Integrity = 100.0
        self.FrequencyMhz = float(FrequencyMhz)
        self.Modulation = 0.0

    # Підйом силового екрана
    def Raise(self) -> bool:
        self.Active = True
        if self.EnergyLevel == 0.0:
            self.EnergyLevel = 100.0
        return self.Active

    # Опускання силового екрана
    def Drop(self) -> bool:
        self.Active = False
        self.EnergyLevel = 0.0
        return self.Active

    # Перезарядка енергії екрана
    def Recharge(self, Amount: float = 100.0) -> float:
        self.EnergyLevel = max(0.0, min(100.0, float(Amount)))
        self.Active = True
        return self.EnergyLevel

    # Поглинання урону / навантаження силовим полем
    def AbsorbDamage(self, ImpactPower: float) -> dict:
        if not self.Active or self.EnergyLevel <= 0.0:
            HullDamage = float(ImpactPower)
            return {"Absorbed": 0.0, "Bleedthrough": HullDamage, "EnergyRemaining": 0.0, "Integrity": self.Integrity}

        Absorbed = min(self.EnergyLevel, float(ImpactPower))
        self.EnergyLevel -= Absorbed
        Bleedthrough = max(0.0, float(ImpactPower) - Absorbed)

        if Bleedthrough > 0.0:
            Erosion = Bleedthrough * 0.25
            self.Integrity = max(0.0, self.Integrity - Erosion)

        if self.EnergyLevel == 0.0:
            self.Active = False

        return {
            "Absorbed": Absorbed,
            "Bleedthrough": Bleedthrough,
            "EnergyRemaining": self.EnergyLevel,
            "Integrity": self.Integrity,
        }

    # Зміна несучої частоти екрана (модуляція)
    def Modulate(self, DeltaMhz: float) -> float:
        self.Modulation += float(DeltaMhz)
        self.FrequencyMhz = round(257.4 + self.Modulation, 2)
        return self.FrequencyMhz

    # Отримання стану окремого екрана
    def GetStatus(self) -> dict:
        return {
            "Quadrant": self.Quadrant,
            "Type": self.ScreenType,
            "Active": self.Active,
            "Energy": round(self.EnergyLevel, 1),
            "Integrity": round(self.Integrity, 1),
            "FrequencyMhz": self.FrequencyMhz,
        }

# Координатор усіх силових екранів зорельота (Сітка щитів)
class ShieldGrid(LCARS):
    def __init__(self):
        super().__init__()
        self.Screens = {
            "Forward": ShieldScreen("Forward", ShieldType.TACTICAL),
            "Aft": ShieldScreen("Aft", ShieldType.TACTICAL),
            "Port": ShieldScreen("Port", ShieldType.TACTICAL),
            "Starboard": ShieldScreen("Starboard", ShieldType.TACTICAL),
            "Navigational": ShieldScreen("Navigational", ShieldType.NAVIGATIONAL),
        }

    # Середній рівень енергії всіх бойових щитів
    def GetTotalEnergy(self) -> float:
        CombatScreens = [S for K, S in self.Screens.items() if K != "Navigational"]
        Total = sum(S.EnergyLevel for S in CombatScreens)
        return round(Total / len(CombatScreens), 1)

    # Середня структурна цілісність емітерів
    def GetAverageIntegrity(self) -> float:
        CombatScreens = [S for K, S in self.Screens.items() if K != "Navigational"]
        Total = sum(S.Integrity for S in CombatScreens)
        return round(Total / len(CombatScreens), 1)

    # Підйом усіх щитів зорельота
    def RaiseAll(self) -> None:
        for Screen in self.Screens.values():
            Screen.Raise()

    # Опускання всіх щитів
    def DropAll(self) -> None:
        for Screen in self.Screens.values():
            Screen.Drop()

    # Повна перезарядка всіх екранів до заданого рівня
    def RechargeAll(self, Level: float = 100.0) -> None:
        for Screen in self.Screens.values():
            Screen.Recharge(Level)

    # Встановлення рівня заряду для окремого квадранта
    def SetQuadrant(self, QuadrantName: str, Level: float) -> bool:
        Screen = self.Screens.get(QuadrantName)
        if Screen:
            Screen.Recharge(Level)
            return True
        return False

    # Поглинання урону в конкретний сектор
    def AbsorbSectorImpact(self, QuadrantName: str, Power: float) -> dict:
        Screen = self.Screens.get(QuadrantName)
        if Screen:
            return Screen.AbsorbDamage(Power)
        return {"Absorbed": 0.0, "Bleedthrough": float(Power), "EnergyRemaining": 0.0, "Integrity": 0.0}

    # Гармонійна модуляція частоти для всієї сітки
    def ModulateAll(self, DeltaMhz: float) -> float:
        Freq = 257.4
        for Screen in self.Screens.values():
            Freq = Screen.Modulate(DeltaMhz)
        return Freq

    # Словник статусів для сумісності з UI та тактичною консоллю
    def GetStatus(self) -> dict:
        return {K: S.GetStatus() for K, S in self.Screens.items()}

# Головна система дефлекторних щитів та кіберзахисту
class DeflectorSystem(SystemComponent):
    ShieldStatusUpdated = Transmission(tuple)
    ThreatDetected = Transmission(dict)
    SectorScanned = Transmission(str, dict)
    ScanProgress = Transmission(int, int)
    ScanCompleted = Transmission(dict)

    def __init__(self, SystemId: str = "Engineering.Deflector"):
        super().__init__(SystemId=SystemId)
        self.SystemId = SystemId

        # Вбудована координаційна сітка екранів
        self.Grid = ShieldGrid()
        self.ShieldStatus = "ONLINE"
        self.ThreatCount = 0
        self.SecurityPolicy = "STANDARD"

        # Базові сигнатури загроз для кібер-сканера
        self.ThreatSignatures = [
            "eval(",
            "exec(",
            "os.system(",
            "subprocess.",
            "__import__",
            "shutil.rmtree(",
        ]

        self.SensorsActive = True
        self.LastScanData = {}
        self.QuarantineList = []
        self.WorkspaceRoot = Directive.PathDrive(__file__).resolve().parents[2]

    # Рівень бойових щитів (динамічно з сітки екранів)
    @property
    def ShieldLevel(self) -> float:
        return self.Grid.GetTotalEnergy()

    @ShieldLevel.setter
    def ShieldLevel(self, Value: float):
        self.Grid.RechargeAll(float(Value))

    # Секторні квадранти (динамічно з окремих екранів)
    @property
    def Quadrants(self) -> dict:
        return {
            "Forward": self.Grid.Screens["Forward"].EnergyLevel,
            "Aft": self.Grid.Screens["Aft"].EnergyLevel,
            "Port": self.Grid.Screens["Port"].EnergyLevel,
            "Starboard": self.Grid.Screens["Starboard"].EnergyLevel,
        }

    # Несуча частота дефлектора
    @property
    def FrequencyMhz(self) -> float:
        return self.Grid.Screens["Forward"].FrequencyMhz

    # Синхронізація політики безпеки з рівнем тривоги
    def SyncPolicy(self, AlertLevel: str) -> None:
        Level = AlertLevel.upper()
        if Level == "RED":
            self.SecurityPolicy = "STRATIFIED"
            self.RechargeShields()
        elif Level == "YELLOW":
            self.SecurityPolicy = "ACTIVE"
            self.SetAllQuadrants(85.0)
        else:
            self.SecurityPolicy = "PASSIVE"
            self.SetAllQuadrants(50.0)

        self.ShieldStatusUpdated.Emit((self.ShieldLevel, self.SecurityPolicy))
        ODN.Transmit("Engineering.Deflector.PolicySynced", Level=Level, ShieldLevel=self.ShieldLevel)

    # Встановлення рівня для всіх бойових секторів
    def SetAllQuadrants(self, Level: float) -> None:
        self.Grid.RechargeAll(float(Level))
        self.ShieldStatusUpdated.Emit((self.ShieldLevel, self.SecurityPolicy))

    # Перезарядка щитів до 100%
    def RechargeShields(self) -> None:
        self.Grid.RechargeAll(100.0)
        self.ShieldStatus = "ONLINE"
        self.ShieldStatusUpdated.Emit((self.ShieldLevel, self.SecurityPolicy))
        ODN.Transmit("Engineering.Deflector.ShieldsRecharged", Level=100.0)

    # Встановлення рівня окремого сектора
    def SetQuadrant(self, QuadrantName: str, Level: float) -> bool:
        Success = self.Grid.SetQuadrant(QuadrantName, Level)
        if Success:
            self.ShieldStatusUpdated.Emit((self.ShieldLevel, self.SecurityPolicy))
        return Success

    # Модуляція частоти щитів
    def ModulateFrequency(self, DeltaMhz: float) -> float:
        NewFreq = self.Grid.ModulateAll(DeltaMhz)
        ODN.Transmit("Engineering.Deflector.FrequencyModulated", FrequencyMhz=NewFreq)
        return NewFreq

    # Сканування коду в пам'яті перед виконанням (Sandbox Shield)
    def ScanBuffer(self, CodeContent: str, SourceName: str = "Buffer") -> list:
        Detected = []
        if not isinstance(CodeContent, str):
            return Detected

        for Sig in self.ThreatSignatures:
            if Sig in CodeContent:
                ThreatInfo = {
                    "Source": SourceName,
                    "Signature": Sig,
                    "Level": "CRITICAL" if Sig in ("eval(", "exec(") else "HIGH",
                }
                Detected.append(ThreatInfo)
                self.ThreatCount += 1
                self.TriggerThreatAlarm(SourceName, Sig)

        return Detected

    # Автономне сканування одного файлу
    def ScanFile(self, FilePathItem) -> list:
        Detected = []
        Target = Directive.PathDrive(FilePathItem)
        if not Target.exists() or not Target.is_file():
            return Detected

        if not str(Target).endswith(".py"):
            return Detected

        Content = Target.read_text(encoding="utf-8")
        Detected = self.ScanBuffer(Content, str(Target.name))
        return Detected

    # Автономне сканування директорії (повний обхід каталогу)
    def ScanDirectory(self, DirectoryTarget: any = None) -> dict:
        BaseDir = Directive.PathDrive(DirectoryTarget) if DirectoryTarget else (self.WorkspaceRoot / "plugin")
        if not BaseDir.exists():
            return {"ScannedFiles": 0, "ThreatsFound": 0, "Threats": []}

        FileList = [P for P in BaseDir.rglob("*.py") if P.is_file()]
        TotalFiles = len(FileList)
        AllThreats = []

        for Index, FilePathItem in enumerate(FileList):
            Threats = self.ScanFile(FilePathItem)
            if Threats:
                AllThreats.extend(Threats)
            self.ScanProgress.Emit(Index + 1, TotalFiles)

        Report = {
            "Directory": str(BaseDir),
            "ScannedFiles": TotalFiles,
            "ThreatsFound": len(AllThreats),
            "Threats": AllThreats,
            "Status": "CLEAN" if len(AllThreats) == 0 else "THREATS_DETECTED",
        }

        self.LastScanData = Report
        self.SectorScanned.Emit(str(BaseDir.name), Report)
        self.ScanCompleted.Emit(Report)
        ODN.Transmit("Engineering.Deflector.ScanCompleted", Threats=len(AllThreats))

        return Report

    # Зворотна сумісність: сканування переданого словника або директорії
    def ScanSector(self, Sector: str, FileContents: dict = None) -> int:
        if FileContents and isinstance(FileContents, dict):
            ThreatCount = 0
            for Filename, Content in FileContents.items():
                Threats = self.ScanBuffer(Content, Filename)
                ThreatCount += len(Threats)
            return ThreatCount

        Report = self.ScanDirectory(Sector)
        return Report.get("ThreatsFound", 0)

    # Ізоляція підозрілого файлу в карантин
    def IsolateThreat(self, FilePathItem: any) -> bool:
        Target = Directive.PathDrive(FilePathItem)
        if not Target.exists():
            return False

        QuarantineDir = self.WorkspaceRoot / "archive" / "quarantine"
        QuarantineDir.mkdir(parents=True, exist_ok=True)
        DestPath = QuarantineDir / f"{Target.name}.quarantined"
        Target.rename(DestPath)

        self.QuarantineList.append(str(DestPath))
        ODN.Transmit("Engineering.Deflector.ThreatIsolated", Original=str(Target), Quarantined=str(DestPath))
        return True

    # Активація тривоги при виявленні загрози
    def TriggerThreatAlarm(self, Filename: str, Signature: str) -> None:
        Payload = {"Filename": Filename, "Signature": Signature}
        self.ThreatDetected.Emit(Payload)
        ODN.Transmit("Engineering.Deflector.ThreatDetected", Threat=Payload)

    # Отримання повного статусу системи дефлектора та сітки екранів
    def GetStatus(self) -> dict:
        return {
            "SystemId": self.SystemId,
            "ShieldLevel": self.ShieldLevel,
            "ShieldStatus": self.ShieldStatus,
            "Quadrants": self.Quadrants,
            "FrequencyMhz": self.FrequencyMhz,
            "ThreatCount": self.ThreatCount,
            "SecurityPolicy": self.SecurityPolicy,
            "SensorsActive": self.SensorsActive,
            "QuarantineCount": len(self.QuarantineList),
            "Screens": self.Grid.GetStatus(),
            "LastScan": self.LastScanData,
        }
