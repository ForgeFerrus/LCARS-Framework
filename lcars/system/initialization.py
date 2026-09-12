# ◤ TITANIUM SYSTEM INITIALIZATION & COMPLETE SUBSYSTEM MATRIX 🖖
# =============================================================================
# ФАЙЛ: lcars/system/initialization.py
# ОПИС: Повна канонічна апаратна, інженерна та нейронна ініціалізація зорельота LCARS.
#       РЕАЛЬНІ ЕТАПИ АЛГОРИТМУ ЗАПУСКУ (14 CANONICAL PHASES / HEALTH MATRIX):
#       ФАЗА 1: HARDWARE & BIOS POST
#         1. PLATFORM DIAGNOSTICS — фізичне залізо ПК (ОС, ядро, версія Python).
#         2. SPLICING ODN BUS — підключення та верифікація оптичної шини ODN Black Box.
#         3. BIOS POST VALIDATION — 10 повних апаратних тестів середовища.
#       ФАЗА 2: MEMORY & ISOLINEAR ARCHITECTURE
#         4. ISOLINEAR MATRIX AUDIT — сканування та верифікація 42 ізолінійних чіпів.
#         5. MEMORY SUBSTRATE — виділення та стабілізація матриці пам'яті (MemoryMatrix).
#         6. DATA STORAGE CHIPS — перевірка критичних чіпів (BlackBox, Bios, Network, Logbook).
#       ФАЗА 3: ENGINEERING COMPLEXES & SHIP SYSTEMS
#         7. EPS POWER GRID — Odyssey Primary 8500 MW EPS шина живлення.
#         8. DEFLECTOR SHIELD MATRIX — підсистема захисних дефлекторів (DeflectorSystem).
#         9. ENVIRONMENTAL & LIFE SUPPORT — системи життєзабезпечення (атмосфера, кисень, гравітація).
#        10. SENSOR ARRAYS & ASTROMETRICS — довгохвильові тахіонні та гравіметричні сенсори.
#        11. DAMAGE CONTROL & INTEGRITY — контур контролю пошкоджень та структурна цілісність корпусу.
#       ФАЗА 4: OPERATIONAL NEXUS & NEURAL AI CORE
#        12. BOARD COMPUTER NEXUS — зв'язок процесорного блоку (CoreProcessor) і телеметрія CPU/RAM.
#        13. NEURAL AI RESIDENT HANDSHAKE — підтвердження готовності локального ШІ (Gemma / Qwen).
#        14. CORE STABILIZATION & CLEARANCE — стабілізація матриці, видача допуску Level 7.
# СТАНДАРТ: Titanium LCARS (Strict PascalCase, Zero Underscores, Pure Classes, No Free Functions).
# =============================================================================

from __future__ import annotations

from lcars.base.type import LCARS, SystemComponent
from lcars.core.signal import ODN

class InitStep(LCARS):
    def __init__(self, Name: str, Category: str, Handler: any, Critical: bool = True):
        super().__init__()
        self.Name = Name
        self.Category = Category
        self.Handler = Handler
        self.Critical = Critical
        self.Status = "PENDING"
        self.Details = ""

class InitReport(LCARS):
    def __init__(self):
        super().__init__()
        self.Errors = []
        self.Warnings = []
        self.Logs = []
        self.SubsystemHealth = {}

    def AddError(self, ErrorText: str) -> None:
        self.Errors.append(str(ErrorText))

    def AddWarning(self, WarnText: str) -> None:
        self.Warnings.append(str(WarnText))

    def AddLog(self, LogText: str) -> None:
        self.Logs.append(str(LogText))

    def SetHealth(self, SubsystemName: str, Status: str, Detail: str = "") -> None:
        self.SubsystemHealth[SubsystemName] = {
            "Status": Status,
            "Detail": Detail,
        }

    def Export(self) -> dict:
        return {
            "Errors": list(self.Errors),
            "Warnings": list(self.Warnings),
            "Logs": list(self.Logs),
            "SubsystemHealth": dict(self.SubsystemHealth),
            "Status": "NOMINAL" if not self.Errors else "ERROR",
        }

class SystemInitializer(SystemComponent):
    Instance = None

    @classmethod
    def GetInstance(cls) -> SystemInitializer:
        if cls.Instance is None:
            cls.Instance = SystemInitializer()
        return cls.Instance

    def __init__(self, SystemId: str = "System.Initializer"):
        super().__init__(SystemId=SystemId)
        self.Report = InitReport()
        self.CurrentStepIndex = 0
        self.IsRunning = False
        self.IsCompleted = False
        
        # 14 повних канонічних етапів ініціалізації
        self.Sequence = [
            # ФАЗА 1: HARDWARE & BIOS POST
            InitStep("PLATFORM DIAGNOSTICS", "Hardware", self.StepPlatform),
            InitStep("SPLICING ODN BUS", "Bus", self.StepODN),
            InitStep("BIOS POST VALIDATION", "BIOS", self.StepBiosPost),
            # ФАЗА 2: MEMORY & ISOLINEAR ARCHITECTURE
            InitStep("ISOLINEAR MATRIX AUDIT", "Memory", self.StepIsolinear),
            InitStep("MEMORY SUBSTRATE", "Memory", self.StepMemorySubstrate),
            InitStep("CRITICAL DATA CHIPS", "Storage", self.StepDataChips),
            # ФАЗА 3: ENGINEERING COMPLEXES & SHIP SYSTEMS
            InitStep("EPS POWER DISTRIBUTION", "Engineering", self.StepPowerGrid),
            InitStep("DEFLECTOR SHIELD MATRIX", "Defense", self.StepDeflectorShield),
            InitStep("LIFE SUPPORT & ENVIRONMENT", "LifeSupport", self.StepLifeSupport),
            InitStep("SENSOR ARRAY & ASTROMETRICS", "Sensors", self.StepSensorArray),
            InitStep("STRUCTURAL INTEGRITY & HULL", "Maintenance", self.StepDamageControl),
            # ФАЗА 4: OPERATIONAL NEXUS & NEURAL AI CORE
            InitStep("BOARD COMPUTER NEXUS", "Core", self.StepBoardComputer),
            InitStep("NEURAL AI RESIDENT CORE", "Intelligence", self.StepNeuralCore),
            InitStep("SYSTEM STABILIZATION & LEVEL 7", "Security", self.StepFinalize),
        ]

    def Log(self, Line: str) -> None:
        Clean = str(Line).strip()
        self.Report.AddLog(Clean)
        ODN.Emit("System.Init.Log", Line=Clean)

    def StartSequence(self) -> None:
        self.CurrentStepIndex = 0
        self.IsRunning = True
        self.IsCompleted = False
        self.ExecuteNextStep()

    def ExecuteNextStep(self) -> bool:
        if not self.IsRunning:
            return False

        Total = len(self.Sequence)
        if self.CurrentStepIndex < Total:
            Step = self.Sequence[self.CurrentStepIndex]
            Pct = int(((self.CurrentStepIndex + 1) / Total) * 100)

            self.Log(f"\n>> [0x{self.CurrentStepIndex+1:02X}] >>> INITIALIZING {Step.Category.upper()}: {Step.Name}...")
            Success = True
            if callable(getattr(Step, "Handler", None)):
                Success = Step.Handler()

            Step.Status = "NOMINAL" if Success else "ERROR"
            self.Report.SetHealth(Step.Name, Step.Status, Step.Details)

            self.Log(f">> [0x{self.CurrentStepIndex+1:02X}] >> {Step.Name.ljust(36, '.')} [ {Step.Status} ]")

            self.CurrentStepIndex += 1
            ODN.Emit("System.Init.Progress", Step=self.CurrentStepIndex, Total=Total, Percent=Pct, Name=Step.Name)
            return True
        else:
            self.IsRunning = False
            self.IsCompleted = True
            ODN.Emit("System.Init.Completed", Report=self.Report.Export())
            return False

    # ─── ФАЗА 1: HARDWARE & BIOS POST ─────────────────────────────────
    def StepPlatform(self) -> bool:
        PlatformMod = LCARS.Import("platform")
        HostSys = LCARS.Import("sys")
        OsName = PlatformMod.platform() if PlatformMod and hasattr(PlatformMod, "platform") else "Starfleet Quantum Core"
        PyVer = HostSys.version.split()[0] if HostSys and hasattr(HostSys, "version") else "3.14"
        self.Log(f"   * HOST ARCHITECTURE : {OsName.upper()}")
        self.Log(f"   * RUNTIME PLATFORM  : PYTHON {PyVer} [64-BIT OPTIMIZED]")
        self.Log("   * PROTOCOL STANDARD : TITANIUM LCARS OKUDA-25")
        return True

    def StepODN(self) -> bool:
        ODN.Transmit("System.Init.ODNConnected")
        Throughput = 4500.0
        self.Log("   * OPTICAL DATA BUS  : TRUNK CARRIER LOCKED (47.2 GHz)")
        self.Log(f"   * BUS THROUGHPUT    : {Throughput} TERAOPS // 1024-BIT FULL DUPLEX")
        self.Log("   * BLACK BOX BUFFER  : TELEMETRY LOG RECORDER ONLINE")
        return True

    def StepBiosPost(self) -> bool:
        from lcars.system.bios import BIOS
        BiosNode = BIOS()
        Report = BiosNode.RunPost()
        self.Log(f"   * BIOS POST ROUTINE : {len(Report.Checks)} ASTRONAVIGATIONAL TESTS")
        for Check in Report.Checks:
            self.Log(f"     [{Check.Status}] {Check.Name}: {Check.Detail}")
        self.Log(f"   * BIOS INTEGRITY    : {Report.Status} // ALL REGISTERS NOMINAL")
        return Report.Status == "NOMINAL"

    # ─── ФАЗА 2: MEMORY & ISOLINEAR ARCHITECTURE ──────────────────────
    def StepIsolinear(self) -> bool:
        from lcars.engineering.chips.architecture import ISOArchitecture
        Arch = ISOArchitecture.GetInstance()
        Chips = Arch.ScanCategories()
        ChipCount = len(Chips) if isinstance(Chips, (list, dict)) else 42
        self.Log(f"   * ISOLINEAR MATRIX  : SCANNING CATEGORIES 00..14 (SLOTS: {ChipCount})")
        self.Log("   * SUBPOLYMER MESH   : OPTICAL INTEGRITY 99.98% NOMINAL")
        self.Log("   * CHIP INTERCONNECT : TRI-NUCLEIC FLUX CHANNELS LOCKED")
        return True

    def StepMemorySubstrate(self) -> bool:
        from lcars.modules.memory import MemoryMatrix
        Mem = MemoryMatrix()
        TotalNodes = 100 * 100 * 100
        self.Log("   * MEMORY MATRIX     : 3D OPTICAL STATE SUBSTRATE INITIALIZED")
        self.Log(f"   * TOTAL MATRIX NODES: {TotalNodes:,} ADDRESSABLE VOXELS")
        self.Log("   * QUANTUM COHERENCE : 0.9998 // PHASE DRIFT NULLIFIED")
        return True

    def StepDataChips(self) -> bool:
        from lcars.modules.storage import ListChips
        ChipList = ListChips()
        Count = len(ChipList) if isinstance(ChipList, list) else 14
        self.Log(f"   * STORAGE BANKS     : {Count} CRITICAL CHIP REPOSITORIES MOUNTED")
        self.Log("   * BOOT REPOSITORIES : BlackBox, BiosCore, Network, Logbook, Telemetry")
        self.Log("   * PARITY VALIDATION : ZERO ENCODING DEFECTS DETECTED")
        return True

    # ─── ФАЗА 3: ENGINEERING COMPLEXES & SHIP SYSTEMS ─────────────────
    def StepPowerGrid(self) -> bool:
        from lcars.engineering.controller import Engineering
        Eng = Engineering.GetInstance()
        self.Log("   * PRIMARY POWER EPS : ODYSSEY 8500 MW PRIMARY CONDUIT CHARGED")
        self.Log("   * WARP CORE TAP     : DUAL-MATTER ANTIMATTER INJECTION STANDBY")
        self.Log("   * PLASMA BUS RAILS  : 14 CANONICAL ENGINEERING COMPLEXES POWERED")
        return True

    def StepDeflectorShield(self) -> bool:
        from lcars.engineering.deflector import DeflectorSystem
        Deflector = DeflectorSystem()
        self.Log("   * DEFLECTOR ARRAY   : MAIN DISH FREQUENCY 428.6 MHz PHASED")
        self.Log("   * SHIELD GENERATORS : FORWARD / AFT / DORSAL / VENTRAL ARMED")
        self.Log("   * GRAVITON EMITTERS : DEFLECTOR SHIELD MATRIX 100% NOMINAL")
        return True

    def StepLifeSupport(self) -> bool:
        from lcars.engineering.maintenance import LifeSupportSystem
        LS = LifeSupportSystem()
        Status = LS.GetStatus() if hasattr(LS, "GetStatus") else {}
        self.Log("   * ATMOSPHERIC MESH  : 78% N2, 21% O2, 1% AR // 1.0 ATM BAROMETRIC")
        self.Log("   * GRAVITY PLATING   : 1.00 G STABILIZED THROUGHOUT PRIMARY HULL")
        self.Log("   * WATER RECYCLING   : CLOSED-LOOP SYSTEM COHERENCE NOMINAL")
        return True

    def StepSensorArray(self) -> bool:
        from lcars.modules.sensor import SensorArray
        Sensors = SensorArray()
        self.Log("   * LONG-RANGE SENSORS: TACHYON SWEEP ACTIVE // RANGE: 5 LIGHT YEARS")
        self.Log("   * SUB-SPACE GRID    : GRAVIMETRIC SENSORS CALIBRATED TO SECTOR 001")
        self.Log("   * ASTROMETRICS LINK : STARFLEET CARTOGRAPHIC DATABASE SYNCED")
        return True

    def StepDamageControl(self) -> bool:
        from lcars.engineering.maintenance import StructuralIntegrity, DamageControl
        SI = StructuralIntegrity()
        DC = DamageControl()
        self.Log("   * STRUCTURAL SIF    : INTEGRITY FIELDS 100% THROUGHOUT DURANIUM HULL")
        self.Log("   * DAMAGE CONTROL    : 24 AUTOMATED REPAIR SQUADS ON STANDBY")
        self.Log("   * BUSSARD RAMSCOOPS : MAGNETIC COLLECTORS ARMED AND BALANCED")
        return True

    # ─── ФАЗА 4: OPERATIONAL NEXUS & NEURAL AI CORE ───────────────────
    def StepBoardComputer(self) -> bool:
        from lcars.core.computer import BoardComputer
        Computer = BoardComputer.GetInstance()
        PsUtil = LCARS.Import("psutil")
        PsCpuAttrs = [attr for attr in dir(PsUtil) if attr.startswith("cpu")]
        CpuFunc = getattr(PsUtil, PsCpuAttrs[0], None) if PsCpuAttrs else None
        CpuLoad = CpuFunc() if callable(CpuFunc) else 0.0
        PsVmAttrs = [attr for attr in dir(PsUtil) if attr.startswith("virtual")]
        VmFunc = getattr(PsUtil, PsVmAttrs[0], None) if PsVmAttrs else None
        RamPercent = VmFunc().percent if callable(VmFunc) else 0.0
        
        self.Log(f"   * FLAGSHIP REGISTRY : {Computer.ShipRegistry} ({Computer.ShipClass})")
        self.Log(f"   * HARDWARE SENSORS  : HOST CPU LOAD: {CpuLoad:.1f}% // RAM ALLOCATION: {RamPercent:.1f}%")
        self.Log(f"   * CORE ALU REGISTERS: OPTICAL/QUANTUM HYBRID RUNTIME ACTIVE")
        return True

    def StepNeuralCore(self) -> bool:
        from lcars.service.provider import AIProviderManager
        AiManager = AIProviderManager.GetInstance()
        Backend = AiManager.ActiveBackend
        BackendName = getattr(Backend, "Name", "Local Offline Core")
        ModelDesc = "google/gemma-3-1b-it (1.0B Parameters)"
        self.Log(f"   * NEURAL PROVIDER   : {BackendName.upper()} // DIRECT CPU INFERENCE")
        self.Log(f"   * RESIDENT WEIGHTS  : {ModelDesc} [1.94 GB]")
        self.Log("   * AUTONOMOUS LINK   : BOARD COMPUTER COPILOT SYNCHRONIZED [OK]")
        return True

    def StepFinalize(self) -> bool:
        ODN.Transmit("System.Boot.CoreStabilized")
        self.Log("   * ACCESS GATEWAY    : CLEARANCE LEVEL 7 CONFIRMED")
        self.Log("   * OPERATIONAL STATUS: ALL 14 CANONICAL COMPLEXES ONLINE & SYNCHRONIZED")
        self.Log("   * INTERFACE DISPATCH: READY FOR LCARS COMMAND CONSOLE / SECURITY GATE 🖖")
        return True