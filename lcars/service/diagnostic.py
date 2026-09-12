# ◤ LCARS DIAGNOSTIC SUBSYSTEM — SERVICE LAYER 🖖
# =============================================================================
# ФАЙЛ: lcars/service/diagnostic.py
# ОПИС: Діагностична служба зорельота LCARS (DiagnosticEngine).
#       Глибока перевірка вузлів, аналіз допусків та виконання діагностичних протоколів.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Strict PascalCase, Pure Classes).
# =============================================================================

from lcars.base.type import LCARS, SystemComponent
from lcars.core.conduit import Service
from lcars.core.signal import Transmission, ODN
from lcars.base.info import getVersion

__version__ = getVersion()

class DiagnosticLevel(LCARS):
    LEVEL_5 = 5  # Автоматичний моніторинг
    LEVEL_4 = 4  # Фонова перевірка
    LEVEL_3 = 3  # Аналіз підсистем
    LEVEL_2 = 2  # Глибока перевірка
    LEVEL_1 = 1  # Тотальна діагностика

@LCARS.DataClass
class HealthStatus(LCARS):
    # Статус здоров'я підсистеми
    Status: str = "NOMINAL"  # NOMINAL, MARGINAL, CRITICAL, SKIPPED
    Message: str = "Optimal state"
    Code: int = 200

    def __post_init__(self):
        super().__init__(Id=f"HealthStatus.{self.Status}")

class SubsystemProbe(LCARS):
    # Проба для перевірки підсистеми

    def __init__(self, Name: str, Level: int = DiagnosticLevel.LEVEL_5):
        super().__init__(Id=f"Probe.{Name}")
        self.Name = Name
        self.MinLevel = Level

    def Check(self, Level: int) -> HealthStatus:
        # Перевірка проби на вказаному рівні
        if Level > self.MinLevel:
            return HealthStatus(Status="SKIPPED", Message=f"Level {Level} restricted", Code=200)
        return self.RunLogic(Level)

    def RunLogic(self, Level: int) -> HealthStatus:
        # Логіка перевірки — перевизначається в нащадках
        return HealthStatus(Status="NOMINAL", Message="Optimal state", Code=200)

class Diagnostic(Service):
    # Головний діагностичний процесор зорельота
    Name = "diagnostic"
    Dependencies = []

    # Сигнал завершення діагностики: список результатів
    DiagnosticComplete = Transmission(list)

    def __init__(self):
        super().__init__(Id="Service.Diagnostic")
        self.Probes = []
        self.InitProbes()

    def InitProbes(self) -> None:
        # Ініціалізація стандартних проб
        self.Probes.append(SubsystemProbe("EPS", DiagnosticLevel.LEVEL_5))
        self.Probes.append(SubsystemProbe("CORE", DiagnosticLevel.LEVEL_5))
        self.Probes.append(SubsystemProbe("WARP", DiagnosticLevel.LEVEL_3))

    def RunProtocol(self, LevelNum: int = 3) -> list:
        # Запуск діагностичного протоколу
        Results = []
        for Probe in self.Probes:
            Res = Probe.Check(LevelNum)
            if Res.Status != "SKIPPED":
                Results.append((Probe.Name, Res))

        self.DiagnosticComplete.Emit(Results)
        ODN.Transmit("Diagnostic.Completed", ProtocolLevel=LevelNum, ProbeCount=len(Results))
        return Results

    def GetStatus(self) -> dict:
        # Отримання статусу діагностичного двигуна
        return {
            "ProbeCount": len(self.Probes),
            "Probes": [P.Name for P in self.Probes],
        }

# Експорт та аліаси
SystemDiagnostic = Diagnostic
DiagnosticEngine = Diagnostic

__all__ = [
    "DiagnosticLevel",
    "HealthStatus",
    "SubsystemProbe",
    "Diagnostic",
    "SystemDiagnostic",
    "DiagnosticEngine",
]
