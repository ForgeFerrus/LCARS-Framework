# ◤ LCARS ENGINEERING :: UNIVERSAL SCIENCE & TESTING LABORATORY 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/laboratory.py
# ОПИС: Багатопрофільна науково-інженерна лабораторія зорельота.
#       Забезпечує дослідження в галузях: фізика частинок (Geant4), матеріалознавство
#       (тританій/дураній), хімія каталізаторів, ксенобіологія та субпросторові квантові поля.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import SystemComponent, LCARS
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN, Transmission

# Наукові галузі лабораторії зорельота
class ScienceDomain(LCARS):
    PHYSICS = "PHYSICS"
    MATERIALS = "MATERIALS"
    CHEMISTRY = "CHEMISTRY"
    BIOLOGY = "BIOLOGY"
    SUBSPACE = "SUBSPACE"

# Статус лабораторного експерименту
class ExperimentStatus(LCARS):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# Лабораторний дослідницький зразок
class LabSample(LCARS):
    def __init__(self, SampleId: str, Name: str, Domain: str = ScienceDomain.MATERIALS,
                 Origin: str = "EXTERNAL", Composition: dict | None = None):
        super().__init__()
        self.SampleId = SampleId
        self.Name = Name
        self.Domain = str(Domain).upper()
        self.Origin = Origin
        self.Composition = Composition or {}
        self.Analyzed = False
        self.Integrity = 100.0

    def ToDict(self) -> dict:
        return {
            "SampleId": self.SampleId,
            "Name": self.Name,
            "Domain": self.Domain,
            "Origin": self.Origin,
            "Composition": self.Composition,
            "Analyzed": self.Analyzed,
            "Integrity": self.Integrity,
        }

# Науковий експеримент або симуляція
class LabExperiment(LCARS):
    def __init__(self, ExperimentId: str, Title: str, Domain: str = ScienceDomain.PHYSICS,
                 Parameters: dict | None = None):
        super().__init__()
        self.ExperimentId = ExperimentId
        self.Title = Title
        self.Domain = str(Domain).upper()
        self.Parameters = Parameters or {}
        self.Status = ExperimentStatus.PENDING
        self.Results = {}
        Time = LCARS.System.Time
        self.CreatedAt = Time.time() if Time and hasattr(Time, "time") else 0.0
        self.CompletedAt = 0.0

    def Complete(self, Results: dict) -> None:
        self.Status = ExperimentStatus.COMPLETED
        self.Results = Results
        Time = LCARS.System.Time
        self.CompletedAt = Time.time() if Time and hasattr(Time, "time") else 0.0

    def ToDict(self) -> dict:
        return {
            "ExperimentId": self.ExperimentId,
            "Title": self.Title,
            "Domain": self.Domain,
            "Parameters": self.Parameters,
            "Status": self.Status,
            "Results": self.Results,
            "CreatedAt": self.CreatedAt,
            "CompletedAt": self.CompletedAt,
        }

# Головна багатопрофільна лабораторія інженерії
class EngineeringLaboratory(SystemComponent):
    Instance = None
    ExperimentCompleted = Transmission(str, dict)
    SampleAnalyzed = Transmission(str, dict)

    def __init__(self):
        super().__init__()
        self.Experiments: dict = {}
        self.Samples: dict = {}
        self.ActiveChambers = {
            ScienceDomain.PHYSICS: "Particle Deceleration Chamber",
            ScienceDomain.MATERIALS: "Spectro-Analysis Anvil",
            ScienceDomain.CHEMISTRY: "Catalytic Synthesis Unit",
            ScienceDomain.BIOLOGY: "Stasis Bio-Isolation Cell",
            ScienceDomain.SUBSPACE: "Subspace Qubit Resonator",
        }
        self.Version = VersionInfo.GetVersion()

    @classmethod
    def GetInstance(cls) -> EngineeringLaboratory:
        if cls.Instance is None:
            cls.Instance = EngineeringLaboratory()
        return cls.Instance

    # Створення нового експерименту в обраній науковій галузі
    def CreateExperiment(self, ExperimentId: str, Title: str,
                         Domain: str = ScienceDomain.PHYSICS,
                         Parameters: dict | None = None) -> LabExperiment:
        Exp = LabExperiment(ExperimentId=ExperimentId, Title=Title, Domain=Domain, Parameters=Parameters)
        self.Experiments[ExperimentId] = Exp
        ODN.Transmit("Engineering.Laboratory.ExperimentCreated", Id=ExperimentId, Domain=Domain)
        return Exp

    # Реєстрація та спектральний аналіз зразка
    def AnalyzeSample(self, SampleId: str, Name: str, Domain: str = ScienceDomain.MATERIALS,
                      Composition: dict | None = None, Origin: str = "DEEP-SPACE") -> dict:
        Sample = LabSample(SampleId=SampleId, Name=Name, Domain=Domain, Origin=Origin, Composition=Composition)
        Sample.Analyzed = True

        AnalysisReport = {
            "SampleId": SampleId,
            "Name": Name,
            "Domain": Sample.Domain,
            "Chamber": self.ActiveChambers.get(Sample.Domain, "General Crucible"),
            "StructuralDensity": 98.7,
            "SpectrometryPurity": 99.4,
            "HazardLevel": "ZERO",
            "Composition": Sample.Composition,
        }

        self.Samples[SampleId] = Sample
        self.SampleAnalyzed.Emit(SampleId, AnalysisReport)
        ODN.Transmit("Engineering.Laboratory.SampleAnalyzed", SampleId=SampleId, Domain=Sample.Domain)
        return AnalysisReport

    # Запуск комп'ютерного моделювання фізичного або квантового процесу
    def RunSimulation(self, ExperimentId: str, Steps: int = 100) -> dict:
        Exp = self.Experiments.get(ExperimentId)
        if Exp is None:
            Exp = self.CreateExperiment(ExperimentId, f"Auto-Simulation-{ExperimentId}", ScienceDomain.PHYSICS)

        Exp.Status = ExperimentStatus.RUNNING
        Domain = Exp.Domain

        SimResults = {
            "SimulationSteps": Steps,
            "Domain": Domain,
            "ConvergenceRate": 0.998,
            "StabilityIndex": 1.0,
            "AnomaliesDetected": 0,
        }

        if Domain == ScienceDomain.PHYSICS:
            SimResults["ScatteringCrossSection"] = "0.42 barns"
            SimResults["Geant4LinkStatus"] = "SYNCHRONIZED"
        elif Domain == ScienceDomain.MATERIALS:
            SimResults["TensileYieldMpa"] = 1250.0
            SimResults["ThermalToleranceKelvin"] = 3400.0
        elif Domain == ScienceDomain.BIOLOGY:
            SimResults["CellularViability"] = 0.96
            SimResults["PathogenRisk"] = "BENIGN"
        elif Domain == ScienceDomain.SUBSPACE:
            SimResults["ResonanceFrequencyThz"] = 47.3
            SimResults["CoherenceTimeMs"] = 120.0

        Exp.Complete(SimResults)
        self.ExperimentCompleted.Emit(ExperimentId, SimResults)
        ODN.Transmit("Engineering.Laboratory.SimulationFinished", Id=ExperimentId)
        return SimResults

    # Звіт про стан лабораторії
    def GetStatus(self) -> dict:
        return {
            "ActiveChambers": len(self.ActiveChambers),
            "TotalExperiments": len(self.Experiments),
            "TotalSamples": len(self.Samples),
            "DomainsSupported": list(self.ActiveChambers.keys()),
            "Version": self.Version,
        }

# Канонічний виклик лабораторії
Laboratory = EngineeringLaboratory.GetInstance
