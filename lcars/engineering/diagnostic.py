# ◤ LCARS ENGINEERING :: DIAGNOSTIC ENGINE & STARFLEET PROBES 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/diagnostic.py
# ОПИС: Система багаторівневої діагностики інженерного обладнання зорельота.
#       Реалізує 5 канонічних рівнів діагностики Зоряного Флоту (Level 1..5),
#       проби перевірки підсистем (SubsystemProbe) та оцінку допусків (HealthStatus).
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import SystemComponent, LCARS
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN

# 5 рівнів діагностики Зоряного Флоту
class DiagnosticLevel(LCARS):
    Level1 = 1  # Тотальна діагностика всіх систем зорельота
    Level2 = 2  # Глибока перевірка варп-каверни, гармонік і плазми
    Level3 = 3  # Аналіз підсистем (сенсори, зв'язок, життєзабезпечення)
    Level4 = 4  # Фонова перевірка цілісності конфігурацій та баз
    Level5 = 5  # Автоматичний пасивний моніторинг телеметрії

# Оцінка стану здоров'я вузла
class HealthStatus(LCARS):
    def __init__(self, Status: str = "NOMINAL", Message: str = "Operating within tolerances", Code: int = 200):
        super().__init__()
        self.Status = Status  # NOMINAL, MARGINAL, CRITICAL, SKIPPED
        self.Message = Message
        self.Code = Code

    def ToDict(self) -> dict:
        return {
            "Status": self.Status,
            "Message": self.Message,
            "Code": self.Code,
        }

# Діагностична проба для окремої підсистеми
class SubsystemProbe(LCARS):
    def __init__(self, SubsystemName: str, MinLevel: int = DiagnosticLevel.Level5, TargetNode: any = None):
        super().__init__()
        self.SubsystemName = SubsystemName
        self.MinLevel = MinLevel
        self.TargetNode = TargetNode

    # Запуск перевірки на вказаному рівні
    def Check(self, Level: int) -> HealthStatus:
        if Level > self.MinLevel:
            return HealthStatus("SKIPPED", f"Probe requires Level {self.MinLevel} or higher (current: Level {Level})", 200)
        return self.RunLogic(Level)

    # Логіка тестування відповідно до глибини діагностики
    def RunLogic(self, Level: int) -> HealthStatus:
        Node = self.TargetNode
        if Node is None:
            return HealthStatus("NOMINAL", f"{self.SubsystemName}: Simulated standard pass", 200)

        # Перевірка наявності статусу вузла
        if hasattr(Node, "Status") and getattr(Node, "Status") == "FAULT":
            return HealthStatus("CRITICAL", f"{self.SubsystemName}: Hardware fault reported", 500)

        if Level == DiagnosticLevel.Level1:
            # Тотальний стрес-тест
            return HealthStatus("NOMINAL", f"{self.SubsystemName}: Full-spectrum stress test passed at 100%", 200)
        elif Level == DiagnosticLevel.Level2:
            return HealthStatus("NOMINAL", f"{self.SubsystemName}: Deep harmonic tolerance nominal", 200)
        elif Level == DiagnosticLevel.Level3:
            return HealthStatus("NOMINAL", f"{self.SubsystemName}: Subsystem impedance nominal", 200)
        elif Level == DiagnosticLevel.Level4:
            return HealthStatus("NOMINAL", f"{self.SubsystemName}: Checksum verified", 200)
        else:
            return HealthStatus("NOMINAL", f"{self.SubsystemName}: Passive telemetry stream active", 200)

# Головний діагностичний процесор інженерії
class DiagnosticSuite(SystemComponent):
    Instance = None

    def __init__(self):
        super().__init__()
        self.Probes: dict = {}
        self.LastReport: dict = {}
        self.Version = VersionInfo.GetVersion()
        self.InitializeProbes()

    @classmethod
    def GetInstance(cls) -> DiagnosticSuite:
        if cls.Instance is None:
            cls.Instance = DiagnosticSuite()
        return cls.Instance

    # Ініціалізація стандартних інженерних проб
    def InitializeProbes(self) -> None:
        self.RegisterProbe(SubsystemProbe("EPS-GRID", DiagnosticLevel.Level5))
        self.RegisterProbe(SubsystemProbe("WARP-CORE", DiagnosticLevel.Level2))
        self.RegisterProbe(SubsystemProbe("DEFLECTOR-HARMONICS", DiagnosticLevel.Level3))
        self.RegisterProbe(SubsystemProbe("LIFE-SUPPORT-ATMOSPHERE", DiagnosticLevel.Level4))
        self.RegisterProbe(SubsystemProbe("ISOLINEAR-MATRIX", DiagnosticLevel.Level4))
        self.RegisterProbe(SubsystemProbe("OPTICAL-SPINE", DiagnosticLevel.Level3))
        self.RegisterProbe(SubsystemProbe("QUANTUM-SUBSTRATE", DiagnosticLevel.Level2))
        self.RegisterProbe(SubsystemProbe("HULL-INTEGRITY", DiagnosticLevel.Level1))

    # Реєстрація кастомної проби для реального вузла
    def RegisterProbe(self, Probe: SubsystemProbe) -> None:
        self.Probes[Probe.SubsystemName] = Probe

    # Запуск діагностики заданого рівня (1..5)
    def RunDiagnostic(self, Level: int = DiagnosticLevel.Level5) -> dict:
        ActualLevel = max(1, min(5, int(Level)))
        Results = {}
        OverallStatus = "NOMINAL"

        Time = LCARS.System.Time
        StartTimestamp = Time.time() if Time and hasattr(Time, "time") else 0.0

        for Name, Probe in self.Probes.items():
            Health = Probe.Check(ActualLevel)
            Results[Name] = Health.ToDict()
            if Health.Status == "CRITICAL":
                OverallStatus = "CRITICAL"
            elif Health.Status == "MARGINAL" and OverallStatus != "CRITICAL":
                OverallStatus = "MARGINAL"

        EndTimestamp = Time.time() if Time and hasattr(Time, "time") else 0.0
        DurationMs = round((EndTimestamp - StartTimestamp) * 1000.0, 3)

        Report = {
            "DiagnosticLevel": ActualLevel,
            "OverallStatus": OverallStatus,
            "TotalProbes": len(self.Probes),
            "DurationMs": DurationMs,
            "Results": Results,
        }
        self.LastReport = Report

        ODN.Transmit("Engineering.Diagnostic.Completed", Level=ActualLevel, Status=OverallStatus)
        return Report

    # Отримання останнього звіту
    def GetStatus(self) -> dict:
        return {
            "ProbesCount": len(self.Probes),
            "LastDiagnosticLevel": self.LastReport.get("DiagnosticLevel", 5),
            "LastOverallStatus": self.LastReport.get("OverallStatus", "UNTESTED"),
            "Version": self.Version,
        }
