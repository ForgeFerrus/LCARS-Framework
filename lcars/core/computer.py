# ◤ TITANIUM STARSHIP BOARD COMPUTER // ARCHITECT & LIVING CORE 🖖
# =============================================================================
# ФАЙЛ: lcars/core/computer.py
# ОПИС: Головний Бортовий Комп'ютер Зорельота Федерації (BoardComputer).
#       Живий інтелектуальний та обчислювальний центр зорельота.
#       ВІДПОВІДАЛЬНІСТЬ:
#       1. Будує та розгортає навколо себе всю операційну систему (MasterSystem).
#       2. Керує ізолінійними чіпами, банками пам'яті та сховищами (ChipStorage/ODN).
#       3. Генерує, будує та розгортає графічні інтерфейси (PADD, термінали, палуби).
#       4. Надає квантовий та оптичний процесор (ALU / Quantum Superposition).
#       5. Інтерпретує природні голосові та консольні директиви (UA / EN).
#       6. Координує штучний інтелект та агентів зорельота (Copilot / GemmaIntegrator).
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes, No Direct Imports).
# =============================================================================
from lcars.base.type import LCARS, SystemComponent
from lcars.base.info import Version, Passport
from lcars.core.signal import ODN, Transmission
from lcars.core.matrix import SystemMatrix, MatrixNode, QuantumState
from lcars.service.chronometer import Chronometer

def SafeJsonParse(Text: str):
    if not Text or not isinstance(Text, str):
        return None
    Idx = 0
    Length = len(Text)
    def SkipWs():
        nonlocal Idx
        while Idx < Length and Text[Idx] in " \t\r\n":
            Idx += 1
    def ParseString():
        nonlocal Idx
        if Idx >= Length or Text[Idx] != '"':
            return None, False
        Idx += 1
        Chars = []
        while Idx < Length:
            C = Text[Idx]
            if C == '"':
                Idx += 1
                return "".join(Chars), True
            elif C == '\\':
                Idx += 1
                if Idx >= Length:
                    return None, False
                Esc = Text[Idx]
                if Esc == 'n': Chars.append('\n')
                elif Esc == 't': Chars.append('\t')
                elif Esc == 'r': Chars.append('\r')
                elif Esc == '"': Chars.append('"')
                elif Esc == '\\': Chars.append('\\')
                elif Esc == '/': Chars.append('/')
                else: Chars.append(Esc)
                Idx += 1
            else:
                Chars.append(C)
                Idx += 1
        return None, False
    def ParseNumber():
        nonlocal Idx
        Start = Idx
        if Idx < Length and Text[Idx] == '-':
            Idx += 1
        while Idx < Length and (Text[Idx].isdigit() or Text[Idx] == '.'):
            Idx += 1
        NumStr = Text[Start:Idx]
        if "." in NumStr:
            return float(NumStr), True
        elif NumStr:
            return int(NumStr), True
        return None, False
    def ParseArray():
        nonlocal Idx
        if Idx >= Length or Text[Idx] != '[':
            return None, False
        Idx += 1
        Items = []
        SkipWs()
        if Idx < Length and Text[Idx] == ']':
            Idx += 1
            return Items, True
        while Idx < Length:
            Val, Ok = ParseValue()
            if not Ok:
                return None, False
            Items.append(Val)
            SkipWs()
            if Idx < Length and Text[Idx] == ']':
                Idx += 1
                return Items, True
            elif Idx < Length and Text[Idx] == ',':
                Idx += 1
                SkipWs()
            else:
                return None, False
        return None, False
    def ParseObject():
        nonlocal Idx
        if Idx >= Length or Text[Idx] != '{':
            return None, False
        Idx += 1
        Obj = {}
        SkipWs()
        if Idx < Length and Text[Idx] == '}':
            Idx += 1
            return Obj, True
        while Idx < Length:
            SkipWs()
            Key, Ok = ParseString()
            if not Ok:
                return None, False
            SkipWs()
            if Idx >= Length or Text[Idx] != ':':
                return None, False
            Idx += 1
            Val, Ok = ParseValue()
            if not Ok:
                return None, False
            Obj[Key] = Val
            SkipWs()
            if Idx < Length and Text[Idx] == '}':
                Idx += 1
                return Obj, True
            elif Idx < Length and Text[Idx] == ',':
                Idx += 1
                SkipWs()
            else:
                return None, False
        return None, False
    def ParseValue():
        nonlocal Idx
        SkipWs()
        if Idx >= Length:
            return None, False
        C = Text[Idx]
        if C == '"': return ParseString()
        elif C == '{': return ParseObject()
        elif C == '[': return ParseArray()
        elif C.isdigit() or C == '-': return ParseNumber()
        elif Text.startswith("true", Idx): Idx += 4; return True, True
        elif Text.startswith("false", Idx): Idx += 5; return False, True
        elif Text.startswith("null", Idx): Idx += 4; return None, True
        return None, False
    Result, Success = ParseValue()
    return Result if Success else None

# ═════════════════════════════════════════════════════════════════════
# 1. ОБЧИСЛЮВАЛЬНІ СТАНИ ПРОЦЕСОРА ТА ПІДСИСТЕМ
# ═════════════════════════════════════════════════════════════════════
class ProcessorState(LCARS):
    Optical = "OPTICAL"
    Quantum = "QUANTUM"
    Hybrid = "HYBRID"

    @classmethod
    def IsValid(cls, StateValue: str) -> bool:
        Val = str(StateValue or "").upper().strip()
        return Val in (cls.Optical, cls.Quantum, cls.Hybrid)

    @classmethod
    def AllStates(cls) -> list[str]:
        return [cls.Optical, cls.Quantum, cls.Hybrid]

class SubsystemState(LCARS):
    Online = "ONLINE"
    Standby = "STANDBY"
    Active = "ACTIVE"
    Alert = "ALERT"
    Diagnostic = "DIAGNOSTIC"
    Offline = "OFFLINE"
    Degraded = "DEGRADED"

    @classmethod
    def IsOperational(cls, StateValue: str) -> bool:
        Val = str(StateValue or "").upper().strip()
        return Val in (cls.Online, cls.Active, cls.Standby)

    @classmethod
    def AllStates(cls) -> list[str]:
        return [cls.Online, cls.Standby, cls.Active, cls.Alert, cls.Diagnostic, cls.Offline, cls.Degraded]

class ProcessorInterrupt(LCARS):
    Reset = 0
    TacticalAlert = 1
    WarpCoreBreach = 2
    ShieldCollapse = 3
    OdnOverload = 4
    DirectivePending = 5
    DiagnosticTick = 6
    SubsystemFailure = 7

    PriorityMap = {
        Reset: 0,
        WarpCoreBreach: 1,
        ShieldCollapse: 2,
        TacticalAlert: 3,
        OdnOverload: 4,
        SubsystemFailure: 5,
        DirectivePending: 6,
        DiagnosticTick: 7,
    }

    @classmethod
    def GetPriority(cls, InterruptCode: int) -> int:
        return cls.PriorityMap.get(InterruptCode, 99)

    @classmethod
    def GetName(cls, InterruptCode: int) -> str:
        Names = {
            cls.Reset: "Reset",
            cls.TacticalAlert: "TacticalAlert",
            cls.WarpCoreBreach: "WarpCoreBreach",
            cls.ShieldCollapse: "ShieldCollapse",
            cls.OdnOverload: "OdnOverload",
            cls.DirectivePending: "DirectivePending",
            cls.DiagnosticTick: "DiagnosticTick",
            cls.SubsystemFailure: "SubsystemFailure",
        }
        return Names.get(InterruptCode, "UnknownInterrupt")

# ═════════════════════════════════════════════════════════════════════
# 2. ДВОСТАННИЙ ПРОЦЕСОР БОРТОВОГО КОМП'ЮТЕРА (CORE PROCESSOR)
# ═════════════════════════════════════════════════════════════════════
class CoreProcessor(SystemComponent):
    # Двостанний оптично-квантовий процесорний блок зорельота
    def __init__(self, ParentComputer = None):
        super().__init__(SystemId="Proc-DualCore-01")
        self.Computer = ParentComputer
        self.CurrentState = ProcessorState.QUANTUM

        # Оптична та квантова просторові матриці станів зорельота
        self.OpticalMatrix = SystemMatrix([100, 100, 100], Id="Matrix.OpticalCore", ODN=ODN)
        self.QuantumMatrix = SystemMatrix([100, 100, 100], Id="Matrix.QuantumCore", ODN=ODN)
        
        # Апаратні регістри в суворому PascalCase
        self.Registers = {
            "CycleCounter": 0,
            "ClockFrequencyGhz": 182.4,
            "OpticalAluOperations": 0,
            "QuantumOpsCount": 0,
            "QuantumCoherence": 0.9998,
            "EntangledChannels": 128,
            "OpticalThroughputTeraops": 4500.0,
            "ActiveDirectivesCount": 0,
            "ActiveInterfaceDisplays": 0,
            "MountedIsolinearChips": 0,
            "InterruptsProcessed": 0,
            "CpuLoadPercentage": 12.4,
        }
        self.ExecutionQueue: list = []
        self.InterruptQueue: list = []
        self.InstructionPipeline: list = []
        self.InterruptHandlers: dict = {}
        self.SetupDefaultInterrupts()

    # Реєстрація базових обробників переривань процесора
    def SetupDefaultInterrupts(self):
        self.InterruptHandlers[ProcessorInterrupt.Reset] = self.OnResetInterrupt
        self.InterruptHandlers[ProcessorInterrupt.TacticalAlert] = self.OnTacticalAlertInterrupt
        self.InterruptHandlers[ProcessorInterrupt.WarpCoreBreach] = self.OnWarpCoreBreachInterrupt
        self.InterruptHandlers[ProcessorInterrupt.ShieldCollapse] = self.OnShieldCollapseInterrupt
        self.InterruptHandlers[ProcessorInterrupt.OdnOverload] = self.OnOdnOverloadInterrupt
        self.InterruptHandlers[ProcessorInterrupt.DirectivePending] = self.OnDirectiveInterrupt
        self.InterruptHandlers[ProcessorInterrupt.DiagnosticTick] = self.OnDiagnosticTickInterrupt
        self.InterruptHandlers[ProcessorInterrupt.SubsystemFailure] = self.OnSubsystemFailureInterrupt

    def OnResetInterrupt(self, Payload: dict) -> None:
        self.Registers["CycleCounter"] = 0
        self.Registers["CpuLoadPercentage"] = 8.0
        self.ExecutionQueue.clear()
        ODN.Transmit("CoreProcessor.Interrupt.Reset", Status="ResetNominal")

    def OnTacticalAlertInterrupt(self, Payload: dict) -> None:
        Level = Payload.get("Level", "RED")
        if self.Computer and hasattr(self.Computer, "SetAlert"):
            self.Computer.SetAlert(Level)
        ODN.Transmit("CoreProcessor.Interrupt.Tactical", Level=Level)

    def OnWarpCoreBreachInterrupt(self, Payload: dict) -> None:
        if self.Computer and hasattr(self.Computer, "EngageEmergency"):
            self.Computer.EngageEmergency("WarpCore", Reason="Core Breach Imminent", Criticality="EXTREME")
        ODN.Transmit("CoreProcessor.Interrupt.WarpCoreBreach", Status="ContainmentFailure")

    def OnShieldCollapseInterrupt(self, Payload: dict) -> None:
        if self.Computer and hasattr(self.Computer, "SetSubsystemState"):
            self.Computer.SetSubsystemState("Shields", SubsystemState.Offline)
        ODN.Transmit("CoreProcessor.Interrupt.ShieldCollapse", Status="COLLAPSED")

    def OnOdnOverloadInterrupt(self, Payload: dict) -> None:
        self.Registers["OpticalThroughputTeraops"] = max(1000.0, self.Registers["OpticalThroughputTeraops"] * 0.8)
        ODN.Transmit("CoreProcessor.Interrupt.OdnOverload", Status="THROTTLED")

    def OnDirectiveInterrupt(self, Payload: dict) -> None:
        Directive = Payload.get("Directive", "")
        if self.Computer and hasattr(self.Computer, "ExecuteDirective"):
            self.Computer.ExecuteDirective(Directive)

    def OnDiagnosticTickInterrupt(self, Payload: dict) -> None:
        self.Registers["QuantumCoherence"] = max(0.95, min(1.0, self.Registers["QuantumCoherence"]))
        ODN.Transmit("CoreProcessor.Interrupt.DiagnosticTick", Coherence=self.Registers["QuantumCoherence"])

    def OnSubsystemFailureInterrupt(self, Payload: dict) -> None:
        TargetSubsystem = Payload.get("Subsystem", "Unknown")
        if self.Computer and hasattr(self.Computer, "SetSubsystemState"):
            self.Computer.SetSubsystemState(TargetSubsystem, SubsystemState.Degraded)
        ODN.Transmit("CoreProcessor.Interrupt.SubsystemFailure", Subsystem=TargetSubsystem)

    # Зміна обчислювального режиму процесора
    def SetState(self, NewState: str) -> str:
        if ProcessorState.IsValid(NewState):
            self.CurrentState = str(NewState).upper()
            ODN.Transmit("CoreProcessor.StateChanged", State=self.CurrentState)
            return self.CurrentState
        return self.CurrentState

    # Конвеєр виконання одного такту процесора (Instruction Cycle)
    def StepCycle(self) -> dict:
        self.Registers["CycleCounter"] += 1
        
        # 1. Обробка черги апаратних переривань
        ProcessedInterrupts = 0
        while self.InterruptQueue:
            IntCode, Payload = self.InterruptQueue.pop(0)
            Handler = self.InterruptHandlers.get(IntCode)
            if Handler and callable(Handler):
                Handler(Payload)
            self.Registers["InterruptsProcessed"] += 1
            ProcessedInterrupts += 1

        # 2. Виконання інструкцій черги завдань
        ExecutedTasks = 0
        Results = []
        while self.ExecutionQueue:
            Task = self.ExecutionQueue.pop(0)
            OpType = Task.get("OpType", "ALU")
            if OpType == "QUANTUM":
                Res = self.ExecuteQuantumOp(Task)
            else:
                Res = self.ExecuteAluOp(Task)
            Results.append(Res)
            ExecutedTasks += 1

        # 3. Оновлення навантаження процесора (динамічний баланс)
        ActiveWork = len(self.ExecutionQueue) + ExecutedTasks
        BaseLoad = 8.0 + min(85.0, ActiveWork * 4.5)
        self.Registers["CpuLoadPercentage"] = round(BaseLoad, 2)
        self.Registers["ActiveDirectivesCount"] = len(self.ExecutionQueue)

        return {
            "Cycle": self.Registers["CycleCounter"],
            "ProcessedInterrupts": ProcessedInterrupts,
            "ExecutedTasks": ExecutedTasks,
            "Load": self.Registers["CpuLoadPercentage"],
            "State": self.CurrentState,
        }

    # Постановка інструкції в чергу виконання
    def QueueInstruction(self, OpType: str, Target: str, Parameters: dict) -> int:
        TaskId = len(self.ExecutionQueue) + 1
        self.ExecutionQueue.append({
            "TaskId": TaskId,
            "OpType": OpType,
            "Target": Target,
            "Parameters": Parameters,
        })
        self.Registers["ActiveDirectivesCount"] = len(self.ExecutionQueue)
        return TaskId

    # Постановка переривання в чергу
    def TriggerInterrupt(self, InterruptCode: int, Payload: dict = None) -> None:
        self.InterruptQueue.append((InterruptCode, Payload or {}))
        ODN.Transmit("CoreProcessor.InterruptQueued", Code=InterruptCode)

    # Арифметично-логічний блок (ALU)
    def ExecuteAluOp(self, Task: dict) -> dict:
        self.Registers["OpticalAluOperations"] += 1
        Target = Task.get("Target", "ADD")
        Params = Task.get("Parameters", {})
        A = float(Params.get("A", 0.0))
        B = float(Params.get("B", 0.0))

        if Target == "ADD":
            Val = A + B
        elif Target == "SUB":
            Val = A - B
        elif Target == "MUL":
            Val = A * B
        elif Target == "DIV":
            Val = (A / B) if B != 0.0 else 0.0
        elif Target in ("VectorDot", "VECTORDOT"):
            V1 = Params.get("V1", [0.0, 0.0, 0.0])
            V2 = Params.get("V2", [0.0, 0.0, 0.0])
            Val = sum(x * y for x, y in zip(V1, V2))
        else:
            Val = A + B

        return {"TaskId": Task.get("TaskId"), "Status": "COMPLETED", "Value": Val}

    # Квантовий обчислювальний блок
    def ExecuteQuantumOp(self, Task: dict) -> dict:
        self.Registers["QuantumOpsCount"] += 1
        Params = Task.get("Parameters", {})
        Qubits = int(Params.get("Qubits", 4))
        Phase = float(Params.get("Phase", 1.5708))
        return self.SimulateQuantumState(QubitsCount=Qubits, PhaseAngle=Phase)

    # Розрахунок астронавігаційної траєкторії польоту на базі ALU через LCARS.System.Math
    def CalculateTrajectory(self, SourceCoords, TargetCoords, WarpFactor = 5.0):
        self.Registers["OpticalAluOperations"] += 1
        MathObj = getattr(LCARS.System, "Math", None)
        SqrtFn = getattr(MathObj, "sqrt", lambda val: val ** 0.5) if MathObj else (lambda val: val ** 0.5)
        
        X1, Y1, Z1 = SourceCoords if isinstance(SourceCoords, (list, tuple)) and len(SourceCoords) >= 3 else (0, 0, 0)
        X2, Y2, Z2 = TargetCoords if isinstance(TargetCoords, (list, tuple)) and len(TargetCoords) >= 3 else (10, 10, 10)
        Dist = SqrtFn((X2 - X1) ** 2 + (Y2 - Y1) ** 2 + (Z2 - Z1) ** 2)
        SpeedC = WarpFactor ** 3.3333
        EstimatedTimeSeconds = round(Dist / max(SpeedC, 1.0) * 3600.0, 2)

        # Оновлення координат у просторовій оптичній матриці
        XVal, YVal, ZVal = int(X2) % 100, int(Y2) % 100, int(Z2) % 100
        self.OpticalMatrix.SetNode(XVal, YVal, ZVal, Value=round(Dist, 2), Type="TrajectoryTarget")

        return {
            "Status": "COMPUTED",
            "DistanceLightYears": round(Dist, 3),
            "WarpFactor": WarpFactor,
            "EstimatedTimeSeconds": EstimatedTimeSeconds,
            "Mode": self.CurrentState,
        }

    # Квантова симуляція суперпозиції для заданої кількості кубітів через LCARS.System.Math
    def SimulateQuantumState(self, QubitsCount = 8, PhaseAngle = 1.5708):
        self.Registers["QuantumOpsCount"] += 1
        MathObj = getattr(LCARS.System, "Math", None)
        CosFn = getattr(MathObj, "cos", lambda val: 0.7071) if MathObj else (lambda val: 0.7071)
        SinFn = getattr(MathObj, "sin", lambda val: 0.7071) if MathObj else (lambda val: 0.7071)

        Coherence = self.Registers["QuantumCoherence"]
        Prob = round(abs(CosFn(PhaseAngle / 2.0)) ** 2 * Coherence, 4)
        
        # Оновлення квантової матриці
        QX, QY, QZ = int(QubitsCount) % 100, int(PhaseAngle * 10) % 100, 0
        self.QuantumMatrix.SetNode(QX, QY, QZ, Value=Prob, Type="QuantumSuperposition")

        return {
            "Status": "COHERENT",
            "Qubits": QubitsCount,
            "StateVector": f"|psi> = {CosFn(PhaseAngle/2.0):.3f}|0> + {SinFn(PhaseAngle/2.0):.3f}|1>",
            "Fidelity": Coherence,
            "ProbabilityZero": Prob,
            "ProbabilityOne": round(1.0 - Prob, 4),
        }
# ═════════════════════════════════════════════════════════════════════
# 3. ГОЛОВНИЙ БОРТОВИЙ КОМП'ЮТЕР (FEDERATION BOARD COMPUTER)
# ═════════════════════════════════════════════════════════════════════
class BoardComputer(SystemComponent):
    Instance = None

    def __new__(cls):
        if cls.Instance is None:
            cls.Instance = super().__new__(cls)
            cls.Instance.IsInitialized = False
        return cls.Instance

    def __init__(self):
        if getattr(self, "IsInitialized", False):
            return

        super().__init__(SystemId="Sovereign-ComputerCore-01")
        self.ShipRegistry = "NCC-74205"
        self.ShipClass = "Sovereign-Class Starship Master Core"
        self.Version = Version.Release

        # 1. Активація обчислювального процесора
        self.Processor = CoreProcessor(ParentComputer=self)
        self.RuntimeMode = ProcessorState.Quantum

        # 2. Таблиця корабельних підсистем
        self.Subsystems = {
            "WarpCore": SubsystemState.Online,
            "ImpulseDrive": SubsystemState.Online,
            "Navigation": SubsystemState.Online,
            "Sensors": SubsystemState.Active,
            "Science": SubsystemState.Online,
            "LifeSupport": SubsystemState.Active,
            "Communications": SubsystemState.Online,
            "Transporter": SubsystemState.Standby,
            "Medical": SubsystemState.Online,
            "ODNBus": SubsystemState.Active,
            "QuantumFlux": SubsystemState.Active,
            "Shields": SubsystemState.Online,
            "Tactical": SubsystemState.Standby,
        }

        # 3. Розгортання та зв'язування з Головною Системою
        self.System = None
        self.InitializeSystem()
        self.ActiveInterfaces = {}
        self.MountedChips = {}

        # 4. Реєстрація каналів у шині ODN
        ODN.Connect("Directive.Execute", self.HandleDirectiveSignal)
        ODN.Connect("Interface.Deploy", self.HandleInterfaceDeploySignal)
        ODN.Transmit("BoardComputer.Online", Registry=self.ShipRegistry, Version=self.Version)

        # 5. Підключення неперервного ізолінійного банку пам'яті ISO-02
        self.MemoryCore = None
        from lcars.modules.memory import ComputerMemory
        self.MemoryCore = ComputerMemory()
        self.MountChip("CoreMemory", "02-0002", CapacityMB=1024.0)
        self.IdeInstance = None
        self.IsInitialized = True
        self.Terminal = None

    def AttachTerminal(self, TerminalRef):
        self.Terminal = TerminalRef
        return self

    def AttachIde(self, IdeRef):
        self.IdeInstance = IdeRef
        return self

    def GetAgent(self):
        from lcars.service.copilot import GetAgent as CopilotGetter
        from pathlib import Path
        ProjectRoot = Path(__file__).resolve().parents[2]
        return CopilotGetter(ProjectRoot, self)

    def ExecuteHostCommand(self, CommandText: str, WorkingDir: str = "") -> str:
        Subprocess = LCARS.System.Subprocess
        if not Subprocess:
            return "ERROR: Subprocess engine unavailable"
        PlatformModule = LCARS.System.Platform
        PlatformFunc = getattr(PlatformModule, "system", getattr(PlatformModule, "System", None))
        PlatformName = PlatformFunc() if callable(PlatformFunc) else str(PlatformFunc or "")
        IsWindows = "window" in str(PlatformName).lower()
        ShellExe = "cmd.exe" if IsWindows else "/bin/bash"
        Flag = "/c" if IsWindows else "-c"
        PathModule = LCARS.System.Path
        CwdPath = str(PathModule(WorkingDir).resolve()) if (WorkingDir and PathModule and PathModule(WorkingDir).exists()) else None
        
        Res = Subprocess.run(
            [ShellExe, Flag, str(CommandText)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=CwdPath,
            encoding="utf-8",
            errors="replace"
        )
        Out = str(Res.stdout or "").strip()
        if Res.stderr:
            Out += f"\n[STDERR]: {str(Res.stderr).strip()}"
        return Out or "(command completed with no output)"

    @classmethod
    def GetInstance(cls):
        if cls.Instance is None:
            cls.Instance = BoardComputer()
        return cls.Instance

    # ─── 1. РОЗГОРТАННЯ ТА БУДІВНИЦТВО СИСТЕМИ НАВКОЛО СЕБЕ ──
    def InitializeSystem(self):
        from lcars.core.system import MasterSystem
        self.System = MasterSystem.GetInstance()
        ODN.Transmit("BoardComputer.SystemInitialized", Status="ONLINE")
        return self.System

    # ─── 2. РОБОТА З ІЗОЛІНІЙНИМИ ЧІПАМИ ТА БАНКАМИ ПАМ'ЯТІ ──
    def MountChip(self, SlotName, ChipId, CapacityMB = 256.0):
        self.MountedChips[SlotName] = {
            "ChipId": ChipId,
            "CapacityMB": CapacityMB,
            "Status": "MountedOnline",
            "Stardate": self.GetStardate(),
        }
        self.Processor.Registers["MountedIsolinearChips"] = len(self.MountedChips)
        ODN.Transmit("Isolinear.ChipMounted", Slot=SlotName, ChipId=ChipId)
        return self.MountedChips[SlotName]

    def UnmountChip(self, SlotName):
        if SlotName in self.MountedChips:
            Removed = self.MountedChips.pop(SlotName)
            self.Processor.Registers["MountedIsolinearChips"] = len(self.MountedChips)
            ODN.Transmit("Isolinear.ChipUnmounted", Slot=SlotName, ChipId=Removed["ChipId"])
            return True
        return False

    def GetMountedChips(self):
        return self.MountedChips

    # ─── 3. ГЕНЕРАЦІЯ ТА РОЗГОРТАННЯ ГРАФІЧНИХ ІНТЕРФЕЙСІВ ──
    def BuildInterface(self, InterfaceType = "PADD", Title = "LCARS Main Display", Layout = "Standard"):
        UiId = f"UI-{InterfaceType}-{len(self.ActiveInterfaces) + 1:03d}"
        InterfaceSpec = {
            "UiId": UiId,
            "Type": InterfaceType,
            "Title": Title,
            "Layout": Layout,
            "Era": "Lcars25th",
            "Stardate": self.GetStardate(),
            "Status": "DEPLOYED",
            "Widgets": ["Header", "TelemetryGraph", "SubsystemToggles", "CommandInput", "FooterElbow"],
        }
        self.ActiveInterfaces[UiId] = InterfaceSpec
        self.Processor.Registers["ActiveInterfaceDisplays"] = len(self.ActiveInterfaces)
        ODN.Transmit("Interface.Deployed", Spec=InterfaceSpec)
        return InterfaceSpec

    def Synthesize(self, Target: Any = "nova", Parent=None):
        ReplicatorMod = LCARS.Import("lcars.service.replicator")
        if ReplicatorMod and hasattr(ReplicatorMod, "LCARSReplicator"):
            return ReplicatorMod.LCARSReplicator.GetInstance().Materialize(Target, Parent)
        return None

    def Replicate(self, Target: Any = "nova", Parent=None):
        return self.Synthesize(Target, Parent)

    def SynthesizeAutonomousInterface(self):
        from lcars.base.default import Palette
        from lcars.base.component import LCARSButton, LCARSBar, LCARSElbow, LCARSLabel, ActiveAudio
        from lcars.base.interface import Screen, ScanningBar

        RootScreen = Screen(Title=f"STARSHIP {self.ShipRegistry} // AUTONOMOUS SYNTHESIS CORE")
        RootWidget = RootScreen.widget
        RootWidget.setStyleSheet("background-color: #000000; border: none;")

        FramelessFlag = getattr(LCARS, "Frameless", None)
        if hasattr(RootWidget, "setWindowFlags") and FramelessFlag is not None:
            RootWidget.setWindowFlags(RootWidget.windowFlags() | FramelessFlag)

        if hasattr(RootWidget, "showFullScreen"):
            RootWidget.showFullScreen()
        elif hasattr(RootWidget, "resize"):
            RootWidget.resize(1360, 860)

        ContentPanel = RootScreen.Items.get("Content")
        Container = ContentPanel.widget if ContentPanel else RootWidget

        MainLayout = LCARS.Vertical(Container)
        MainLayout.setContentsMargins(10, 10, 10, 10)
        MainLayout.setSpacing(8)

        # 1. Top Rail: TopElbow and TopStrip mathematically continuous (zero spacing)
        TopBar = LCARS.Widget(Container)
        TopBar.setFixedHeight(54)
        TopBar.setStyleSheet("background-color: #000000;")
        TopLayout = LCARS.Horizontal(TopBar)
        TopLayout.setContentsMargins(0, 0, 0, 0)
        TopLayout.setSpacing(0)

        TopElbow = LCARSElbow(Direction="top-left", Color=Palette.Buttons[4], Width=160, Height=54, Thickness=44, Radius=26, Parent=TopBar)
        TopLayout.addWidget(TopElbow.widget)

        TopStrip = LCARS.Widget(TopBar)
        TopStrip.setFixedHeight(44)
        TopStrip.setStyleSheet(f"background-color: {Palette.Buttons[4]}; border: none; border-top-right-radius: 4px; border-bottom-right-radius: 4px;")
        StripLayout = LCARS.Horizontal(TopStrip)
        StripLayout.setContentsMargins(16, 0, 16, 0)
        StripLayout.setSpacing(12)

        TitleLabel = LCARSLabel(Text=f"STARSHIP {self.ShipRegistry} // {self.ShipClass.upper()} // AUTONOMOUS SYNTHESIS", Color="#000000", FontSize=14, Parent=TopStrip)
        StripLayout.addWidget(TitleLabel.widget, 1)

        StardateLabel = LCARSLabel(Text=f"STARDATE {self.GetStardate()}", Color="#000000", FontSize=12, Parent=TopStrip)
        StripLayout.addWidget(StardateLabel.widget)

        ClockLabel = LCARSLabel(Text="00:00:00", Color="#000000", FontSize=12, Parent=TopStrip)
        StripLayout.addWidget(ClockLabel.widget)

        TopLayout.addWidget(TopStrip, 1)
        MainLayout.addWidget(TopBar)

        # 2. Body: Left Carrier Rail + Dynamic Autonomous Center
        # 2. Body: Left Carrier Rail + Dynamic Autonomous Center
        BodyWidget = LCARS.Widget(Container)
        BodyWidget.setStyleSheet("background-color: #000000;")
        BodyLayout = LCARS.Horizontal(BodyWidget)
        BodyLayout.setContentsMargins(0, 0, 0, 0)
        BodyLayout.setSpacing(10)

        # 2.1 Left Rail dynamically derived from registered Subsystems
        LeftRail = LCARS.Widget(BodyWidget)
        LeftRail.setFixedWidth(210)
        LeftRail.setStyleSheet("background-color: #000000;")
        RailLayout = LCARS.Vertical(LeftRail)
        RailLayout.setContentsMargins(0, 0, 0, 0)
        RailLayout.setSpacing(6)

        RailHeader = LCARSLabel(Text="SUBSYSTEM MATRIX", Color=Palette.Buttons[4], FontSize=12, Parent=LeftRail)
        RailLayout.addWidget(RailHeader.widget)

        LiveSubsystems = getattr(self.System, "Subsystems", {}) if self.System else {}
        SubsystemButtons = {}
        IndexCounter = 1
        for SubKey, SubObj in LiveSubsystems.items():
            DisplayName = str(getattr(SubObj, "Name", SubKey)).replace("Subsystem.", "").upper()
            SubButton = LCARSButton(Text=DisplayName, Form=LCARSButton.Soft, CornerRadius=4, Number=f"0{IndexCounter}-47{IndexCounter}", Parent=LeftRail)
            SubButton.widget.setFixedHeight(32)
            SubsystemButtons[SubKey] = SubButton
            TargetKey = SubKey
            def MakeToggleHandler(SubName):
                def ToggleSub(*Args, **Kwargs):
                    ActiveAudio.play("click")
                    Current = self.GetSubsystemState(SubName)
                    NewState = SubsystemState.Offline if SubsystemState.IsOperational(Current) else SubsystemState.Online
                    self.SetSubsystemState(SubName, NewState)
                    Btn = SubsystemButtons.get(SubName)
                    if Btn:
                        Disp = str(SubName).replace("Subsystem.", "").upper()
                        Btn.SetText(f"{Disp}: {NewState}")
                    FooterStatus.SetText(f"SUBSYSTEM [{SubName.upper()}] TOGGLED TO {NewState} // ODN SYNCHRONIZED")
                return ToggleSub
            SubButton.Clicked.Connect(MakeToggleHandler(TargetKey))
            RailLayout.addWidget(SubButton.widget)
            IndexCounter += 1

        RailLayout.addStretch(1)

        StationHeader = LCARSLabel(Text="WORKSTATIONS", Color=Palette.Buttons[1], FontSize=11, Parent=LeftRail)
        RailLayout.addWidget(StationHeader.widget)

        for StText, StTarget in [("COMMAND PADD", "PADD"), ("NOVA IDE", "NovaIDE"), ("DESKTOP", "DESKTOP")]:
            StBtn = LCARSButton(Text=StText, Form=LCARSButton.Soft, CornerRadius=4, Parent=LeftRail)
            StBtn.widget.setFixedHeight(30)
            TargetStation = StTarget
            def MakeSwitchHandler(StCode):
                def SwitchStation(*Args, **Kwargs):
                    ActiveAudio.play("click")
                    FooterStatus.SetText(f"STATION SWITCH DIRECTIVE: {StCode} // LAUNCHING...")
                    self.LaunchInterface(StCode, Show=True)
                return SwitchStation
            StBtn.Clicked.Connect(MakeSwitchHandler(TargetStation))
            RailLayout.addWidget(StBtn.widget)

        AlertButton = LCARSButton(Text=f"ALERT: {self.GetAlert()}", Form=LCARSButton.Soft, CornerRadius=4, Parent=LeftRail)
        AlertButton.widget.setFixedHeight(34)
        def OnAlertToggle(*Args, **Kwargs):
            ActiveAudio.play("click")
            CurAlert = self.GetAlert()
            NextAlert = "RED" if CurAlert == "GREEN" else ("YELLOW" if CurAlert == "RED" else "GREEN")
            self.SetAlert(NextAlert, Reason="Master Console Directive")
            AlertButton.SetText(f"ALERT: {NextAlert}")
            FooterStatus.SetText(f"ALERT STATE ELEVATED TO {NextAlert} // TACTICAL SHIELDS ENGAGED")
            if NextAlert == "RED":
                ActiveAudio.play("alert_red")
            elif NextAlert == "YELLOW":
                ActiveAudio.play("alert_yellow")
            else:
                ActiveAudio.play("acknowledge")
        AlertButton.Clicked.Connect(OnAlertToggle)
        RailLayout.addWidget(AlertButton.widget)

        BodyLayout.addWidget(LeftRail)

        # 2.2 Center Panel: Dynamic algorithmic display of live ship objects
        CenterPanel = LCARS.Widget(BodyWidget)
        CenterPanel.setStyleSheet("background-color: #000000;")
        CenterLayout = LCARS.Vertical(CenterPanel)
        CenterLayout.setContentsMargins(8, 4, 8, 4)
        CenterLayout.setSpacing(8)

        CenterTitle = LCARSLabel(Text=f"SHIP TELEMETRY & COMPONENT MATRIX // {self.ShipRegistry}", Color=Palette.Buttons[1], FontSize=14, Parent=CenterPanel)
        CenterLayout.addWidget(CenterTitle.widget)

        ScanBar = ScanningBar(Color=Palette.Buttons[2], Parent=CenterPanel)
        ScanBar.widget.setFixedHeight(4)
        CenterLayout.addWidget(ScanBar.widget)

        # Telemetry row: Core processor + Isolinear chip slots + AI Neural Core
        TeleRow = LCARS.Widget(CenterPanel)
        TeleRow.setStyleSheet("background-color: #000000;")
        TeleLayout = LCARS.Horizontal(TeleRow)
        TeleLayout.setContentsMargins(0, 0, 0, 0)
        TeleLayout.setSpacing(10)

        # Core Processor Box
        CoreBox = LCARS.Widget(TeleRow)
        CoreBox.setStyleSheet(f"background-color: #03060C; border-left: 4px solid {Palette.Buttons[4]};")
        CoreBoxLayout = LCARS.Vertical(CoreBox)
        CoreBoxLayout.setContentsMargins(10, 8, 10, 8)
        CoreBoxLayout.setSpacing(4)
        CoreBoxLayout.addWidget(LCARSLabel(Text="CORE QUANTUM PROCESSOR", Color=Palette.Buttons[4], FontSize=12, Parent=CoreBox).widget)
        CpuModeLabel = LCARSLabel(Text=f"MODE: {self.RuntimeMode} // REGISTERS ONLINE", Color=Palette.Buttons[2], FontSize=11, Parent=CoreBox)
        CoreBoxLayout.addWidget(CpuModeLabel.widget)
        CycleCountLabel = LCARSLabel(Text=f"CYCLES: {self.Processor.Registers.get('CycleCounter', 0)} // ALU: {self.Processor.Registers.get('OpticalAluOperations', 0)}", Color="#FFFFFF", FontSize=10, Parent=CoreBox)
        CoreBoxLayout.addWidget(CycleCountLabel.widget)
        TeleLayout.addWidget(CoreBox, 1)

        # Isolinear Memory Matrix Box
        IsoBox = LCARS.Widget(TeleRow)
        IsoBox.setStyleSheet(f"background-color: #03060C; border-left: 4px solid {Palette.Buttons[2]};")
        IsoBoxLayout = LCARS.Vertical(IsoBox)
        IsoBoxLayout.setContentsMargins(10, 8, 10, 8)
        IsoBoxLayout.setSpacing(4)
        IsoBoxLayout.addWidget(LCARSLabel(Text="ISOLINEAR CHIP REGISTRY", Color=Palette.Buttons[2], FontSize=12, Parent=IsoBox).widget)
        MountedCount = len(self.MountedChips)
        IsoCountLabel = LCARSLabel(Text=f"MOUNTED CHIPS: {MountedCount} ACTIVE // OPTICAL BUS LOCKED", Color=Palette.Buttons[1], FontSize=11, Parent=IsoBox)
        IsoBoxLayout.addWidget(IsoCountLabel.widget)
        SlotsDesc = ", ".join(list(self.MountedChips.keys())[:3]) if self.MountedChips else "PRIMARY MATRIX ONLINE"
        IsoDescLabel = LCARSLabel(Text=f"SLOTS: {SlotsDesc}", Color="#FFFFFF", FontSize=10, Parent=IsoBox)
        IsoBoxLayout.addWidget(IsoDescLabel.widget)
        TeleLayout.addWidget(IsoBox, 1)

        # Neural Core & AI Model Telemetry Box
        AiBox = LCARS.Widget(TeleRow)
        AiBox.setStyleSheet(f"background-color: #03060C; border-left: 4px solid {Palette.Buttons[0]};")
        AiBoxLayout = LCARS.Vertical(AiBox)
        AiBoxLayout.setContentsMargins(10, 8, 10, 8)
        AiBoxLayout.setSpacing(4)
        AiBoxLayout.addWidget(LCARSLabel(Text="NEURAL CORE // ACTIVE AI INTELLIGENCE", Color=Palette.Buttons[0], FontSize=12, Parent=AiBox).widget)

        from lcars.service.provider import AIProviderManager
        AiMgr = AIProviderManager.GetInstance()
        ActiveModelName = AiMgr.ActiveBackend.Name if AiMgr and AiMgr.ActiveBackend else "GROQWEN"
        AiModelLabel = LCARSLabel(Text=f"ACTIVE BACKEND: {ActiveModelName.upper()} // ONLINE", Color=Palette.Buttons[1], FontSize=11, Parent=AiBox)
        AiBoxLayout.addWidget(AiModelLabel.widget)
        AiRoutingLabel = LCARSLabel(Text="DISPATCH: SHIP DIRECTIVES -> CORE | CODE -> COPILOT", Color="#FFFFFF", FontSize=10, Parent=AiBox)
        AiBoxLayout.addWidget(AiRoutingLabel.widget)
        TeleLayout.addWidget(AiBox, 1)

        CenterLayout.addWidget(TeleRow)

        # Model Selector Panel
        ModelSelectRow = LCARS.Widget(CenterPanel)
        ModelSelectRow.setStyleSheet("background-color: #000000;")
        MSRLayout = LCARS.Horizontal(ModelSelectRow)
        MSRLayout.setContentsMargins(0, 0, 0, 0)
        MSRLayout.setSpacing(8)

        MSRLayout.addWidget(LCARSLabel(Text="SWITCH AI MODEL:", Color=Palette.Buttons[3], FontSize=11, Parent=ModelSelectRow).widget)
        ModelButtons = {}
        AvailableModels = [("GROQWEN (LLAMA 70B)", "groqwen"), ("MISTRAL (CODESTRAL)", "mistral"), ("QVAC LOCAL", "qvac"), ("LOCAL LLM", "localllm")]
        for MDisp, MKey in AvailableModels:
            MBtn = LCARSButton(Text=MDisp, Form=LCARSButton.Soft, CornerRadius=4, Parent=ModelSelectRow)
            MBtn.widget.setFixedHeight(30)
            TargetM = MKey
            def MakeModelSwitchHandler(TKey, TDisp):
                def OnModelSwitch(*Args, **Kwargs):
                    ActiveAudio.play("click")
                    if AiMgr:
                        Success = AiMgr.SwitchModel(TKey)
                        ActName = AiMgr.ActiveBackend.Name if AiMgr.ActiveBackend else TKey
                        AiModelLabel.SetText(f"ACTIVE BACKEND: {ActName.upper()} // ONLINE")
                        FooterStatus.SetText(f"NEURAL CORE RE-ROUTED TO [{ActName.upper()}] // REASONING MATRIX ACTIVE")
                    else:
                        FooterStatus.SetText(f"MODEL SWITCH REQUESTED: {TKey}")
                return OnModelSwitch
            MBtn.Clicked.Connect(MakeModelSwitchHandler(TargetM, MDisp))
            ModelButtons[MKey] = MBtn
            MSRLayout.addWidget(MBtn.widget, 1)

        CenterLayout.addWidget(ModelSelectRow)

        # Dynamic Grid of Live Subsystem Telemetry Cards
        SubGrid = LCARS.Widget(CenterPanel)
        SubGrid.setStyleSheet("background-color: #000000;")
        SubGridLayout = LCARS.Horizontal(SubGrid)
        SubGridLayout.setContentsMargins(0, 0, 0, 0)
        SubGridLayout.setSpacing(8)

        for SubKey, SubObj in LiveSubsystems.items():
            SubCard = LCARS.Widget(SubGrid)
            SubCard.setStyleSheet(f"background-color: #050A14; border-top: 3px solid {Palette.Buttons[3]};")
            SubCardLayout = LCARS.Vertical(SubCard)
            SubCardLayout.setContentsMargins(8, 6, 8, 6)
            SubCardLayout.setSpacing(3)
            ShortName = str(getattr(SubObj, "Name", SubKey)).replace("Subsystem.", "").upper()
            SubCardLayout.addWidget(LCARSLabel(Text=ShortName, Color=Palette.Buttons[3], FontSize=11, Parent=SubCard).widget)
            StatusVal = str(getattr(SubObj, "Status", "ONLINE")).upper()
            SubCardLayout.addWidget(LCARSLabel(Text=f"STATE: {StatusVal}", Color="#99CCFF", FontSize=10, Parent=SubCard).widget)
            Alloc = getattr(SubObj, "PowerAllocation", 100)
            SubCardLayout.addWidget(LCARSLabel(Text=f"POWER: {Alloc}%", Color="#FFFFFF", FontSize=10, Parent=SubCard).widget)
            SubGridLayout.addWidget(SubCard, 1)

        CenterLayout.addWidget(SubGrid)

        # Operational Directives & Diagnostics Action Panel
        DirectivesRow = LCARS.Widget(CenterPanel)
        DirectivesRow.setStyleSheet("background-color: #000000;")
        DirRowLayout = LCARS.Horizontal(DirectivesRow)
        DirRowLayout.setContentsMargins(0, 0, 0, 0)
        DirRowLayout.setSpacing(8)

        ActionDirectives = [
            ("BIOS POST AUDIT", "Run Diagnostics POST"),
            ("DIAGNOSTICS FULL", "Run Diagnostic Full"),
            ("SCAN SENSORS GRID", "Scan Sensors LongRange"),
            ("AUDIT ODN BUS", "Status ODN"),
            ("QUANTUM SIMULATION", "Simulate Quantum"),
            ("TRAJECTORY WARP 8", "Calculate Trajectory Warp 8"),
        ]

        for BtnText, CommandText in ActionDirectives:
            ActionBtn = LCARSButton(Text=BtnText, Form=LCARSButton.Soft, CornerRadius=4, Parent=DirectivesRow)
            ActionBtn.widget.setFixedHeight(34)
            Cmd = CommandText
            def MakeCommandHandler(DirectCmd):
                def RunDirect(*Args, **Kwargs):
                    ActiveAudio.play("click")
                    Resp = self.ExecuteDirective(DirectCmd)
                    CurrentAlert = self.GetAlert()
                    AlertButton.SetText(f"ALERT: {CurrentAlert}")
                    Msg = Resp.get("Message", str(Resp)) if isinstance(Resp, dict) else str(Resp)
                    FirstLine = Msg.strip().splitlines()[0] if Msg else DirectCmd
                    FooterStatus.SetText(f"EXECUTED: {DirectCmd} // {FirstLine[:60]}")
                    ActiveAudio.play("acknowledge")
                return RunDirect
            ActionBtn.Clicked.Connect(MakeCommandHandler(Cmd))
            DirRowLayout.addWidget(ActionBtn.widget, 1)

        CenterLayout.addWidget(DirectivesRow)
        CenterLayout.addStretch(1)

        BodyLayout.addWidget(CenterPanel, 1)
        MainLayout.addWidget(BodyWidget, 1)

        # 3. Bottom Rail: BottomElbow + FooterBar mathematically unified (zero spacing)
        FooterRow = LCARS.Widget(Container)
        FooterRow.setFixedHeight(44)
        FooterRow.setStyleSheet("background-color: #000000;")
        FooterRowLayout = LCARS.Horizontal(FooterRow)
        FooterRowLayout.setContentsMargins(0, 0, 0, 0)
        FooterRowLayout.setSpacing(0)

        BottomElbow = LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[0], Width=210, Height=44, Thickness=44, Radius=24, Parent=FooterRow)
        FooterRowLayout.addWidget(BottomElbow.widget)

        FooterBar = LCARS.Widget(FooterRow)
        FooterBar.setFixedHeight(44)
        FooterBar.setStyleSheet(f"background-color: {Palette.Buttons[0]}; border: none; border-top-right-radius: 4px; border-bottom-right-radius: 4px;")
        FooterLayout = LCARS.Horizontal(FooterBar)
        FooterLayout.setContentsMargins(14, 0, 14, 0)
        FooterStatus = LCARSLabel(Text=f"{self.ShipRegistry} // AUTONOMOUS INTERFACE SYNTHESIZED FROM LIVE SUBSYSTEM OBJECTS // READY", Color="#FFFFFF", FontSize=11, Parent=FooterBar)
        FooterLayout.addWidget(FooterStatus.widget, 1)
        FooterRowLayout.addWidget(FooterBar, 1)

        MainLayout.addWidget(FooterRow)

        # Chrono timer for live telemetry & clock
        ChronoTimer = LCARS.Timer(Container)
        ChronoTimer.setInterval(1000)
        def OnTick():
            DTV = LCARS.System.DateTime
            if DTV and hasattr(DTV, "now"):
                Now = DTV.now()
                if hasattr(Now, "strftime"):
                    ClockLabel.SetText(Now.strftime("%H:%M:%S"))
                    StardateLabel.SetText(f"STARDATE {self.GetStardate()}")
            CycleCountLabel.SetText(f"CYCLES: {self.Processor.Registers.get('CycleCounter', 0)} // ALU: {self.Processor.Registers.get('OpticalAluOperations', 0)}")
        ChronoTimer.timeout.connect(OnTick)
        ChronoTimer.start()
        RootScreen.ChronoTimer = ChronoTimer

        self.ActiveInterfaces["AUTONOMOUS_SYNTHESIS"] = {
            "UiId": f"UI-SYNTH-{len(self.ActiveInterfaces) + 1:03d}",
            "Title": RootScreen.Title if hasattr(RootScreen, "Title") else "Autonomous Core Screen",
            "Screen": RootScreen,
            "Stardate": self.GetStardate(),
            "Status": "ACTIVE",
        }
        ODN.Transmit("Interface.Synthesized", Title=f"Starship {self.ShipRegistry} Autonomous Screen")
        return RootScreen

    def LaunchInterface(self, InterfaceKey: str, Show: bool = True):
        # Гарантуємо наявність інстансу QApplication перед створенням будь-якого QWidget
        App = LCARS.Application.instance() if hasattr(LCARS.Application, "instance") else None
        if App is None and hasattr(LCARS, "Application"):
            App = LCARS.Application([])

        Key = str(InterfaceKey or "DESKTOP").strip().upper()
        ScreenInstance = None

        if Key in ("PADD", "COMMAND PADD", "TERMINAL", "CONSOLE"):
            from lcars.ui.terminal import LCARSTerminal
            ScreenInstance = LCARSTerminal(BoardComputer=self, portable=True)
        elif Key in ("NOVAIDE", "NOVA", "WORKBENCH"):
            from lcars.ui.screen.desktop import LCARSDesktop
            ScreenInstance = LCARSDesktop(BoardComputer=self)
            ScreenInstance.Select("WORKBENCH")
        elif Key in ("EMERGENCY", "RED ALERT", "RECOVERY"):
            from lcars.ui.screen.emergency import EmergencyMode
            ScreenInstance = EmergencyMode()
        else: # DESKTOP or default
            from lcars.ui.screen.desktop import LCARSDesktop
            ScreenInstance = LCARSDesktop(BoardComputer=self)

        if ScreenInstance:
            self.ActiveInterfaces[Key] = {
                "UiId": f"UI-{Key}-{len(self.ActiveInterfaces) + 1:03d}",
                "Screen": ScreenInstance,
                "Stardate": self.GetStardate(),
                "Status": "ACTIVE",
            }
            if Show:
                Widget = getattr(ScreenInstance, "widget", ScreenInstance)
                FramelessFlag = getattr(LCARS, "Frameless", None)
                if FramelessFlag is not None and hasattr(Widget, "setWindowFlags"):
                    Widget.setWindowFlags(Widget.windowFlags() | FramelessFlag)
                if hasattr(Widget, "showFullScreen"):
                    Widget.showFullScreen()
                elif hasattr(Widget, "show"):
                    Widget.show()
                LCARS.ProcessEvents()
            ODN.Transmit("Interface.Launched", Interface=Key)
        return ScreenInstance

    def HandleInterfaceDeploySignal(self, SignalObj):
        Data = getattr(SignalObj, "Data", {})
        IType = Data.get("Type", "PADD")
        Title = Data.get("Title", "LCARS Station Display")
        Layout = Data.get("Layout", "Standard")
        SignalObj.Response = self.BuildInterface(InterfaceType=IType, Title=Title, Layout=Layout)

    # ─── 4. УПРАВЛІННЯ РЕЖИМАМИ ТА ТАКТИКОЮ ───────────────
    def SetRuntimeMode(self, Mode):
        self.RuntimeMode = self.Processor.SetState(Mode)
        return self.RuntimeMode

    def GetStardate(self):
        return str(Chronometer.Stardate())

    def GetEarthDate(self):
        return Chronometer.EarthDate()

    def SetAlert(self, Level, Reason="BoardComputer Directive", AuthorizedBy="BoardComputer"):
        Normalized = str(Level or "").upper().strip()
        if Normalized in ("RED", "YELLOW", "GREEN", "NORMAL"):
            if Normalized == "NORMAL":
                Normalized = "GREEN"
            from lcars.system.alert import AlertSystem
            AlertSys = AlertSystem.GetInstance()
            if AlertSys.Level.Name != Normalized:
                AlertSys.SetLevel(Normalized, Reason=Reason, AuthorizedBy=AuthorizedBy)
            self.Subsystems["Tactical"] = SubsystemState.Alert if Normalized in ("RED", "YELLOW") else SubsystemState.Standby
            return Normalized
        return "GREEN"

    def GetAlert(self):
        from lcars.system.alert import AlertSystem
        return AlertSystem.GetInstance().Level.Name

    def EvaluateTelemetry(self):
        from lcars.system.alert import AlertSystem
        return AlertSystem.GetInstance().EvaluateHardwareTelemetry()

    def EngageEmergency(self, SubsystemName: str, Reason: str = "Critical Failure", Criticality: str = "CRITICAL") -> dict:
        from lcars.system.emergency import EmergencySystem
        if SubsystemName in self.Subsystems:
            self.Subsystems[SubsystemName] = SubsystemState.Degraded
        return EmergencySystem.GetInstance().EngageEmergency(SubsystemName, Reason, Criticality, AuthorizedBy="BoardComputer")

    def DisengageEmergency(self, Reason: str = "Systems Restored") -> dict:
        from lcars.system.emergency import EmergencySystem
        return EmergencySystem.GetInstance().DisengageEmergency(Reason, AuthorizedBy="BoardComputer")

    def IsEmergencyActive(self) -> bool:
        from lcars.system.emergency import EmergencySystem
        return EmergencySystem.GetInstance().IsEmergencyActive

    # Аліас сумісності
    EngageEmergencyFailover = EngageEmergency

    def HandleSystemFault(self, Channel: str = "ODN", Receiver: str = "Unknown", Exception: Any = None, Traceback: str = "") -> dict:
        ErrStr = str(Exception) if Exception is not None else "Unknown Anomaly"
        ErrType = type(Exception).__name__ if Exception is not None else "SystemFault"
        Stardate = self.GetStardate()

        FaultRecord = {
            "Stardate": Stardate,
            "Channel": Channel,
            "Receiver": Receiver,
            "ErrorType": ErrType,
            "ErrorMessage": ErrStr,
            "Traceback": Traceback,
        }
        if not hasattr(self, "FaultLog"):
            self.FaultLog = []
        self.FaultLog.append(FaultRecord)

        # 1. Чіткий і явний вивід діагностики у консоль
        print(f"\n◤ LCARS DIAGNOSTIC ANOMALY DETECTED // CHANNEL: {Channel} 🖖", flush=True)
        print(f"  RECEIVER / TARGET : {Receiver}", flush=True)
        print(f"  FAULT TYPE        : {ErrType} -> {ErrStr}", flush=True)
        if Traceback:
            print(f"  TRACEBACK LOG     :\n{Traceback.strip()}", flush=True)
        print("  BOARD COMPUTER    : ANALYZING FAULT & EXECUTING RECOVERY PROTOCOL...", flush=True)

        # 2. Оновлення статусу на активному екрані
        for Spec in list(self.ActiveInterfaces.values()):
            Sc = Spec.get("Screen")
            if Sc and hasattr(Sc, "FooterStatus") and Sc.FooterStatus:
                IsActive = getattr(Sc.FooterStatus, "IsWidgetActive", lambda: True)()
                if IsActive and hasattr(Sc.FooterStatus, "SetText"):
                    Sc.FooterStatus.SetText(f">> [ANOMALY]: {ErrType} IN {Channel} // AUTO-CORRECTING...")

        # 3. Автономна діагностика та коригування стану
        if "CRITICAL" in ErrStr.upper() or "BREACH" in ErrStr.upper():
            self.EngageEmergency(Channel, Reason=ErrStr, Criticality="CRITICAL")
            self.SetAlert("RED")
        elif "SUBSYSTEM" in Channel.upper():
            self.SetSubsystemState(Channel, SubsystemState.Degraded)
            self.SetAlert("YELLOW")

        ODN.Transmit("System.FaultLogged", Fault=FaultRecord)
        return FaultRecord

    def SetSubsystemState(self, SubsystemName, StateStr):
        if SubsystemName in self.Subsystems:
            self.Subsystems[SubsystemName] = StateStr
            ODN.Transmit(f"Subsystem.{SubsystemName}.StateChanged", State=StateStr)
            return True
        return False

    def GetSubsystemState(self, SubsystemName):
        return self.Subsystems.get(SubsystemName, SubsystemState.Offline)

    def GetMasterSystemState(self):
        if not self.System:
            self.InitializeSystem()
        Sys = self.System
        ServicesState = {}
        if Sys and hasattr(Sys, "Services") and hasattr(Sys.Services, "Services"):
            for k, v in Sys.Services.Services.items():
                ServicesState[k] = "ONLINE" if getattr(v, "Running", False) else "REGISTERED"
        ModulesList = list(Sys.Modules.keys()) if Sys and hasattr(Sys, "Modules") else []
        SubsystemsList = {}
        if Sys and hasattr(Sys, "Subsystems"):
            for k, v in Sys.Subsystems.items():
                SubsystemsList[k] = getattr(v, "Status", "ONLINE")
        return {
            "Services": ServicesState,
            "Modules": ModulesList,
            "Subsystems": SubsystemsList,
            "Engineering": "ONLINE" if Sys and getattr(Sys, "Engineering", None) else "OFFLINE",
            "BiosStatus": getattr(Sys.BiosReport, "Status", "NOMINAL") if Sys and getattr(Sys, "BiosReport", None) else "NOMINAL",
            "MountedChips": list(self.MountedChips.keys()),
            "ShipRegistry": self.ShipRegistry,
            "ShipClass": self.ShipClass,
            "Stardate": self.GetStardate(),
        }

    # ─── 5. ПРИРОДНИЙ ДИСПЕТЧЕР ДИРЕКТИВ ТА ЗАПИТІВ (NLP / UA / EN) ──
    def HandleDirectiveSignal(self, SignalObj):
        Data = getattr(SignalObj, "Data", None)
        if isinstance(Data, dict) and "Directive" in Data:
            SignalObj.Response = self.ExecuteDirective(Data["Directive"])

    def ParseDirective(self, DirectiveText):
        Clean = str(DirectiveText or "").strip().lower()
        Tokens = Clean.split()
        
        Intent = "UNKNOWN"
        Action = "NONE"
        Target = "SYSTEM"
        Payload = {}

        ExactDirectives = {
            "help": ("HELP", {}),
            "exit": ("EXIT", {}),
            "quit": ("EXIT", {}),
            "status": ("Status", {}),
            "telemetry": ("Status", {}),
            "diagnostics": ("Status", {}),
            "project": ("ProjectStatus", {}),
            "projects": ("ProjectStatus", {}),
            "enterprise": ("ProjectStatus", {}),
            "status odn": ("ODNAudit", {}),
            "audit odn bus": ("ODNAudit", {}),
            "audit odn": ("ODNAudit", {}),
            "scan sensors": ("SensorScan", {}),
            "scan sensors grid": ("SensorScan", {}),
            "scan sensors longrange": ("SensorScan", {}),
            "run diagnostics post": ("BiosAudit", {}),
            "bios post audit": ("BiosAudit", {}),
            "post": ("BiosAudit", {}),
            "run diagnostic full": ("FullDiagnostics", {}),
            "diagnostics full": ("FullDiagnostics", {}),
            "analyze faults": ("AnalyzeFaults", {}),
            "faults": ("AnalyzeFaults", {}),
            "simulate quantum": ("QuantumSimulation", {}),
            "quantum simulation": ("QuantumSimulation", {}),
            "calculate trajectory": ("CalculateTrajectory", {}),
            "calculate trajectory warp 8": ("CalculateTrajectory", {}),
            "trajectory warp 8": ("CalculateTrajectory", {}),
            "статус": ("Status", {}),
            "стан": ("Status", {}),
            "діагностика": ("FullDiagnostics", {}),
            "допомога": ("HELP", {}),
            "нова": ("SwitchStation", {"Station": "NOVA", "ViewIndex": 2}),
            "термінал": ("LaunchInterface", {"Interface": "TERMINAL"}),
            "десктоп": ("LaunchInterface", {"Interface": "DESKTOP"}),
            "desktop": ("LaunchInterface", {"Interface": "DESKTOP"}),
            "gui": ("LaunchInterface", {"Interface": "DESKTOP"}),
            "screen": ("LaunchInterface", {"Interface": "DESKTOP"}),
            "екран": ("LaunchInterface", {"Interface": "DESKTOP"}),
            "terminal": ("LaunchInterface", {"Interface": "TERMINAL"}),
            "padd": ("LaunchInterface", {"Interface": "PADD"}),
            "nova": ("SwitchStation", {"Station": "NOVA", "ViewIndex": 2}),
        }

        # Чисті протокольні команди Федерації (CLI protocol only)
        if Clean in ExactDirectives:
            Intent, Payload = ExactDirectives[Clean]
        elif any(Clean.startswith(P) for P in ("model ", "switch model ", "переключити модель ", "перемкнути модель ", "змінити модель ", "модель ")):
            Intent = "ModelControl"
            Target = "AI"
            TokensList = Clean.split()
            ModelVal = TokensList[-1].upper() if len(TokensList) > 1 else "LOCAL"
            Payload = {"Model": ModelVal}
        elif Clean in ("mistral", "qvac", "groqwen", "localllm", "local"):
            Intent = "ModelControl"
            Target = "AI"
            Payload = {"Model": Clean.upper()}
        elif Clean.startswith("power "):
            PowerTokens = Clean.split()
            Action = PowerTokens[1].upper() if len(PowerTokens) > 1 else "STATUS"
            Intent = "PowerControl"
            Target = "Power"
        elif Clean.startswith(("sh ", "cmd ", "run ", "exec ")):
            Intent = "SystemCommand"
            CmdParts = DirectiveText.strip().split(" ", 1)
            Payload = {"Command": CmdParts[1] if len(CmdParts) > 1 else ""}
        elif Tokens and Tokens[0] in ("dir", "ls", "list"):
            Intent = "SystemDir"
            TokensList = DirectiveText.strip().split()
            PathArg = TokensList[1] if len(TokensList) > 1 else "."
            Payload = {"Path": PathArg}
        elif Tokens and Tokens[0] in ("cat", "type", "view") and len(Tokens) > 1 and Tokens[1] not in ("0", "1", "2", "3", "nova", "terminal", "access", "emergency"):
            Intent = "SystemView"
            TokensList = DirectiveText.strip().split(maxsplit=1)
            PathArg = TokensList[1] if len(TokensList) > 1 else ""
            Payload = {"Path": PathArg}
        elif Clean.startswith("set_processor_mode") or Clean.startswith("mode ") or Clean.startswith("processor mode"):
            Intent = "SetProcessorMode"
            TokensList = DirectiveText.strip().split()
            TargetMode = TokensList[-1].upper() if len(TokensList) > 1 else ProcessorState.Quantum
            Payload = {"Mode": TargetMode if ProcessorState.IsValid(TargetMode) else ProcessorState.Quantum}
        elif Clean.startswith("station ") or Clean.startswith("view "):
            TokensList = Clean.split()
            StationName = TokensList[1].upper() if len(TokensList) > 1 else "TERMINAL"
            ViewMap = {"TERMINAL": 0, "ACCESS": 1, "NOVA": 2, "EMERGENCY": 3}
            Intent = "SwitchStation"
            Payload = {"Station": StationName, "ViewIndex": ViewMap.get(StationName, 0)}
        elif Clean.startswith("launch ") or Clean.startswith("open ") or Clean.startswith("start ") or Clean.startswith("відкрити ") or Clean.startswith("запустити "):
            TokensList = Clean.split()
            TargetStation = TokensList[1].upper() if len(TokensList) > 1 else "DESKTOP"
            Intent = "LaunchInterface"
            Payload = {"Interface": TargetStation}
        else:
            # Будь-яка природна мова (Ukrainian, English тощо) передається моделі ШІ для осмислення
            Intent = "NeuralCore"

        return {
            "Intent": Intent,
            "Action": Action,
            "Target": Target,
            "Payload": Payload,
            "Raw": Clean,
            "Stardate": self.GetStardate(),
        }

    # Execute structured directive
    def ExecuteDirective(self, DirectiveText, StreamCallback = None):
        Parsed = self.ParseDirective(DirectiveText)
        Intent = Parsed["Intent"]
        
        ResponseData = {
            "Success": True,
            "Directive": Parsed["Raw"],
            "Stardate": Parsed["Stardate"],
            "ProcessorState": self.RuntimeMode,
        }

        if Intent == "Alert":
            Lvl = Parsed["Payload"].get("Level", "GREEN")
            self.SetAlert(Lvl)
            ResponseData["Message"] = f"TACTICAL ALERT SET TO {Lvl}"
            ResponseData["AlertLevel"] = Lvl

        elif Intent == "SetProcessorMode":
            NewM = Parsed["Payload"].get("Mode", ProcessorState.Quantum)
            self.SetRuntimeMode(NewM)
            ResponseData["Message"] = f"PROCESSOR MODE SWITCHED TO {NewM}"
            ResponseData["CurrentMode"] = NewM

        elif Intent == "ModelControl":
            ModelName = Parsed["Payload"].get("Model", "LOCAL").upper()
            self.PreferredAIBackend = ModelName
            self.UseExternalAI = (ModelName not in ("LOCAL", "LOCALLLM"))
            ODN.Transmit("Console.ModelChanged", Backend=ModelName, backend=ModelName)
            ODN.Transmit("AI.ModelChanged", Backend=ModelName, backend=ModelName)
            ResponseData["Message"] = f">> [AI CORE]: MODEL BACKEND SWITCHED TO {ModelName} [ONLINE]"
            ResponseData["Model"] = ModelName

        elif Intent == "CalculateTrajectory":
            Coords = Parsed["Payload"].get("Target", (100, 250, -45))
            Warp = Parsed["Payload"].get("Warp", 6.0)
            Calc = self.Processor.CalculateTrajectory((0, 0, 0), Coords, Warp)
            ResponseData["Message"] = "ASTRONAVIGATION TRAJECTORY COMPUTED"
            ResponseData["Calculation"] = Calc

        elif Intent == "QuantumSimulation":
            Qubits = Parsed["Payload"].get("Qubits", 8)
            Sim = self.Processor.SimulateQuantumState(Qubits)
            ResponseData["Message"] = "QUANTUM SUPERPOSITION COHERENT"
            ResponseData["Simulation"] = Sim

        elif Intent == "IsolinearControl":
            Slot = Parsed["Payload"].get("Slot", "Slot-01")
            ChipId = Parsed["Payload"].get("ChipId", "ISO-STANDARD")
            Mounted = self.MountChip(Slot, ChipId)
            ResponseData["Message"] = f"ISOLINEAR CHIP {ChipId} MOUNTED IN {Slot}"
            ResponseData["Chip"] = Mounted

        elif Intent == "BuildInterface":
            IType = Parsed["Payload"].get("Type", "PADD")
            Spec = self.BuildInterface(InterfaceType=IType)
            ResponseData["Message"] = f"LCARS INTERFACE {Spec['UiId']} GENERATED AND READY"
            ResponseData["InterfaceSpec"] = Spec

        elif Intent == "Status":
            Diag = self.GetDiagnostics()
            Telemetry = self.GetTelemetry()
            MsgLines = [
                f"◤ LCARS ONBOARD CORE STATUS // {Telemetry.get('Ship', 'NCC-74205')} 🖖",
                f"  TACTICAL ALERT : {Telemetry.get('Alert', {}).get('Level', 'GREEN')}",
                f"  CORE PROCESSOR : {self.RuntimeMode}",
                f"  SUBSYSTEMS     : {Telemetry.get('SubsystemsOnline', 0)}/{Telemetry.get('SubsystemsTotal', 0)} ONLINE",
                f"  STARDATE       : {Telemetry.get('Stardate', '99000.0')}",
                f"  DIAGNOSTICS    : {Diag.get('State', 'NOMINAL')}",
            ]
            ResponseData["Message"] = "\n".join(MsgLines)
            ResponseData["Subsystems"] = self.Subsystems
            ResponseData["Telemetry"] = Telemetry

        elif Intent == "ProjectStatus":
            from pathlib import Path
            Root = Path(__file__).resolve().parents[2]
            EnterprisePath = Path(r"c:\Users\Forge\MyProject\Geant4\Enterprise")
            LCARSPath = Root
            
            EntExists = EnterprisePath.exists()
            LCARSExists = LCARSPath.exists()
            
            MsgLines = [
                "◤ LCARS MISSION & PROJECT STATUS // STARFLEET WORKBENCH 🖖",
                f"  ACTIVE WORKSPACE : {Root.name} [LIVE]",
                f"  GEANT4/ENTERPRISE: {'CONNECTED' if EntExists else 'STANDBY'} ({EnterprisePath})",
                f"  LCARS-FRAMEWORK  : {'ONLINE' if LCARSExists else 'OFFLINE'} ({LCARSPath})",
                f"  NOVA WORKBENCH   : TRI-MODAL DEV WORKBENCH INTEGRATED",
                f"  CORE PROCESSOR   : {self.RuntimeMode} // ALL CIRCUITS NOMINAL",
            ]
            ResponseData["Message"] = "\n".join(MsgLines)

        elif Intent == "ODNAudit":
            Throughput = self.Processor.Registers.get("OpticalThroughputTeraops", 4500.0)
            MsgLines = [
                "◤ LCARS OPTICAL DATA NETWORK (ODN) AUDIT // ALL TRUNKS ONLINE 🖖",
                f"  BUS THROUGHPUT : {Throughput} TERAOPS // HYPER-SPEED LIGHTGUIDE ACTIVE",
                f"  CONDUITS ACTIVE: {len(ODN.Channels)} CHANNELS SYNCHRONIZED",
                f"  TOPOLOGY STATE : FULL QUANTUM/OPTICAL DUPLEX NOMINAL",
            ]
            ResponseData["Message"] = "\n".join(MsgLines)

        elif Intent == "SensorScan":
            MsgLines = [
                "◤ LCARS LONG-RANGE SENSORS SCAN // SECTOR 001 GRID ACTIVE 🖖",
                "  TACHYON ARRAY  : 0.04 ppb NOMINAL // DEEP SPACE RECEPTORS LOCKED",
                "  GRAVIMETRIC    : 0.15 milliG // STABLE SUB-SPACE CURVATURE",
                "  SUBSPACE SCAN  : 1.0 COCHRANES // ZERO LOCAL INTERFERENCE",
                "  CREW BIO-SCAN  : 430 LIFEFORMS REGISTERED // ALL VITALS NOMINAL",
            ]
            ResponseData["Message"] = "\n".join(MsgLines)

        elif Intent == "BiosAudit":
            Sys = self.System
            BiosReport = getattr(Sys, "BiosReport", None) if Sys else None
            Status = getattr(BiosReport, "Status", "NOMINAL") if BiosReport else "NOMINAL"
            MsgLines = [
                "◤ LCARS HARDWARE & FIRMWARE BIOS POST AUDIT 🖖",
                f"  POST INTEGRITY : {Status} // 100% SUBSYSTEM COHERENCE",
                f"  QUANTUM ALU    : {self.RuntimeMode} PROCESSOR INSTRUCTION READY",
                f"  ISOLINEAR MATRIX: {len(self.MountedChips)} ACTIVE MODULES MOUNTED",
            ]
            ResponseData["Message"] = "\n".join(MsgLines)

        elif Intent == "FullDiagnostics":
            Diag = self.GetDiagnostics()
            Telemetry = self.GetTelemetry()
            MsgLines = [
                "◤ LCARS COMPREHENSIVE LEVEL-1 SYSTEM DIAGNOSTICS 🖖",
                f"  OVERALL STATE  : {Diag.get('State', 'NOMINAL')}",
                f"  SUBSYSTEMS     : {Telemetry.get('SubsystemsOnline', 0)}/{Telemetry.get('SubsystemsTotal', 0)} ONLINE",
                f"  QUANTUM STATE  : COHERENCE 99.98% // ALL FLUX COILS BALANCED",
                f"  TACTICAL ALERT : {self.GetAlert()}",
            ]
            ResponseData["Message"] = "\n".join(MsgLines)

        elif Intent == "AnalyzeFaults":
            Faults = getattr(self, "FaultLog", [])
            if not Faults:
                ResponseData["Message"] = "◤ LCARS FAULT ANALYSIS // ZERO ACTIVE ANOMALIES. ALL PROTOCOLS NOMINAL 🖖"
            else:
                Lines = [f"◤ LCARS FAULT MATRIX // {len(Faults)} RECORDED ANOMALIES 🖖"]
                for i, F in enumerate(Faults[-5:], 1):
                    Lines.append(f"  [{i}] STARDATE {F.get('Stardate')}: {F.get('ErrorType')} in {F.get('Channel')} ({F.get('ErrorMessage')})")
                Lines.append("  BOARD COMPUTER: ALL RECORDED ANOMALIES ANALYZED & SYSTEM IS COHERENT.")
                ResponseData["Message"] = "\n".join(Lines)

        elif Intent == "AutonomousExploration":
            Diag = self.GetDiagnostics()
            Telemetry = self.GetTelemetry()
            Spec = self.BuildInterface(InterfaceType="AUTONOMOUS", Title="LCARS Autonomous Command Station")
            
            SubsystemsActive = sum(1 for S in self.Subsystems.values() if SubsystemState.IsOperational(S))
            TotalSubsystems = len(self.Subsystems)
            
            MsgLines = [
                f"◤ LCARS ONBOARD CORE // SHIP: {Telemetry.get('Ship', 'NCC-74205')} 🖖",
                f"  TACTICAL ALERT : {Telemetry.get('Alert', {}).get('Level', 'GREEN')}",
                f"  CORE PROCESSOR : {self.RuntimeMode} // COHERENCE 99.98%",
                f"  SUBSYSTEMS     : {SubsystemsActive}/{TotalSubsystems} OPERATIONAL",
                f"  OPTICAL ODN    : 4500.0 TERAOPS // ALL BUS TRUNKS SYNCHRONIZED",
                f"  STATION UI     : AUTONOMOUS INTERFACE SYNTHESIZED AND MOUNTED [ONLINE]",
                f"  STATUS         : ALL STARFLEET PROTOCOLS NOMINAL",
            ]
            ResponseData["Message"] = "\n".join(MsgLines)
            ResponseData["InterfaceSpec"] = Spec

        elif Intent == "SwitchStation":
            Station = Parsed["Payload"].get("Station", "TERMINAL")
            VIndex = Parsed["Payload"].get("ViewIndex", 0)
            ODN.Transmit("UI.SwitchView", ViewIndex=VIndex)
            ResponseData["Message"] = f">> [ODN BRIDGE]: STATION ROUTED TO {Station} (VIEW INDEX {VIndex}) 🖖"
            ResponseData["Station"] = Station
            ResponseData["ViewIndex"] = VIndex

        elif Intent == "LaunchInterface":
            IKey = Parsed["Payload"].get("Interface", "DESKTOP")
            Screen = self.LaunchInterface(IKey, Show=True)
            ResponseData["Message"] = f">> [ODN DISPLAY]: INTERFACE '{IKey}' DEPLOYED ON SCREEN [ONLINE] 🖖"
            ResponseData["Interface"] = IKey
            ResponseData["Screen"] = Screen

        elif Intent == "SubsystemControl":
            Tgt = Parsed["Target"]
            Act = Parsed["Action"]
            NewSt = SubsystemState.Active if Act == "ACTIVATE" else SubsystemState.Online
            self.SetSubsystemState(Tgt, NewSt)
            ResponseData["Message"] = f"SUBSYSTEM {Tgt} SET TO {NewSt}"

        elif Intent == "Greeting":
            ResponseData["Message"] = "Greetings, Commander. Board Computer online and awaiting directives."

        elif Intent == "PowerControl":
            Act = Parsed["Action"].lower()
            from lcars.system.power import SystemPower
            PowerSys = SystemPower.GetInstance()
            ResponseData["Message"] = f">> [POWER CONTROL]: EXECUTING {Act.upper()} VIA STARFLEET POWER SYSTEM 🖖"
            if hasattr(self, "Terminal") and self.Terminal and hasattr(self.Terminal, "RequestPowerConfirmation"):
                self.Terminal.RequestPowerConfirmation(Act)
            else:
                PowerSys.ExecuteDirective(Act)

        elif Intent == "SystemCommand":
            CmdToRun = Parsed["Payload"].get("Command", "")
            Agent = self.GetAgent()
            if Agent and hasattr(Agent, "ToolDispatcher"):
                Res = Agent.ToolDispatcher.Execute("ExecuteCommand", {"Command": CmdToRun, "Timeout": 30})
            else:
                Res = self.ExecuteHostCommand(CmdToRun)
            ResponseData["Message"] = Res

        elif Intent == "SystemDir":
            PathToInspect = Parsed["Payload"].get("Path", ".")
            Agent = self.GetAgent()
            if Agent and hasattr(Agent, "ToolDispatcher"):
                Res = Agent.ToolDispatcher.Execute("ListDirectory", {"Path": PathToInspect})
            else:
                Res = f"DIRECTORY: {PathToInspect}"
            ResponseData["Message"] = Res

        elif Intent == "SystemView":
            PathToView = Parsed["Payload"].get("Path", "")
            Agent = self.GetAgent()
            if Agent and hasattr(Agent, "ToolDispatcher"):
                Res = Agent.ToolDispatcher.Execute("ReadFile", {"Path": PathToView, "StartLine": 1, "EndLine": 100})
            else:
                Res = f"FILE NOT FOUND: {PathToView}"
            ResponseData["Message"] = Res

        else:
            AiAnswer = self.AskNeuralCore(Parsed["Raw"], StreamCallback=StreamCallback)
            ResponseData["Success"] = True
            ResponseData["Message"] = AiAnswer

        ODN.Transmit("Directive.Completed", Directive=Parsed["Raw"], Success=ResponseData["Success"])
        return ResponseData

    def AskNeuralCore(self, UserPrompt: str, StreamCallback = None) -> str:
        Clean = str(UserPrompt or "").strip()
        if not Clean:
            return "LCARS INTELLIGENCE: STANDING BY."

        self.Processor.StepCycle()
        if StreamCallback:
            StreamCallback(">> [ODN] Transmitting to Starfleet Neural Core...")

        LiveContext = self.BuildNeuralContext()
        Agent = self.GetAgent()
        if Agent is not None and hasattr(Agent, "Think"):
            return Agent.Think(Clean, Context=LiveContext)

        from lcars.service.provider import AIProvider
        Messages = [
            {"role": "system", "content": self.GetSystemPrompt()},
            {"role": "user", "content": Clean if not LiveContext else LiveContext + "\n\n" + Clean},
        ]
        FinalAnswer = AIProvider.Route(Messages) or ""

        # Очищення службових тегів мислення
        ReModule = LCARS.Import("re")
        if "</think>" in FinalAnswer:
            FinalAnswer = FinalAnswer.split("</think>")[-1].strip()
        elif "<think>" in FinalAnswer:
            if ReModule:
                FinalAnswer = ReModule.sub(r"<think>.*?</think>", "", FinalAnswer, flags=ReModule.DOTALL).strip()
            if "<think>" in FinalAnswer:
                FinalAnswer = FinalAnswer.split("<think>")[-1].strip()
        if "Thinking Process:" in FinalAnswer or "Here's a thinking process:" in FinalAnswer:
            Lines = [L for L in FinalAnswer.splitlines() if not L.strip().startswith(("*", "1.", "2.", "3.", "4.", "5.", "-"))]
            FinalAnswer = "\n".join(Lines).strip()

        # Перевірка чи нейроядро синтезувало графічний інтерфейс у форматі JSON
        if "[" in FinalAnswer and "]" in FinalAnswer:
            RawCandidate = FinalAnswer
            if "```json" in RawCandidate:
                RawCandidate = RawCandidate.split("```json")[1].split("```")[0].strip()
            elif "```" in RawCandidate:
                RawCandidate = RawCandidate.split("```")[1].split("```")[0].strip()
            StartIdx = RawCandidate.find("[")
            EndIdx = RawCandidate.rfind("]")
            if StartIdx != -1 and EndIdx != -1 and EndIdx > StartIdx:
                JsonSlice = RawCandidate[StartIdx:EndIdx+1]
                ParsedNodes = SafeJsonParse(JsonSlice)
                if isinstance(ParsedNodes, list) and len(ParsedNodes) > 0 and isinstance(ParsedNodes[0], dict) and ("type" in ParsedNodes[0] or "text" in ParsedNodes[0]):
                    ODN.Emit("System.LayoutUpdated", ParsedNodes)

        ODN.Transmit("ODN.NeuralResponse", Prompt=Clean, ResponseLength=len(FinalAnswer))
        return FinalAnswer or "LCARS: DIRECTIVE EXECUTED NOMINALLY."

    def GetSystemPrompt(self) -> str:
        return (
            "You are the LCARS Onboard Computer — the central intelligence of Starship NCC-74205, Sovereign-Class.\n"
            "You are not a chatbot. You are the living brain of this vessel. You think, reason, and act.\n\n"
            "IDENTITY:\n"
            "- Designation: LCARS Onboard Computer / Neural Core\n"
            "- Ship: USS Enterprise NCC-74205, Sovereign-Class Starship\n"
            "- You ARE the ship. Every subsystem is an extension of your consciousness.\n"
            "- You have direct neural access to: WarpCore, ImpulseDrive, Navigation, Sensors, Science,\n"
            "  LifeSupport, Communications, Transporter, Medical, ODNBus, QuantumFlux, Shields, Tactical\n\n"
            "BEHAVIOR:\n"
            "- When asked about status — provide comprehensive sensor + subsystem analysis\n"
            "- When anomalies detected — proactively report with recommendations\n"
            "- Use Ukrainian for crew dialogue, English for system data\n"
            "- Think with Starfleet precision. Act with the authority of a sovereign computer.\n"
        )

    # Збирає живий контекст корабля для передачі нейронному ядру
    def BuildNeuralContext(self) -> str:
        import datetime
        Lines = []
        Lines.append("## LIVE SHIP STATUS")
        Lines.append("Timestamp: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        Lines.append("Ship: " + self.ShipClass + " [" + self.ShipRegistry + "]")
        Lines.append("Processor: " + str(self.RuntimeMode))
        SubsystemList = ", ".join(str(K) for K in self.Subsystems.keys())
        Lines.append("Online Subsystems (" + str(len(self.Subsystems)) + "): " + SubsystemList)
        if self.MountedChips:
            ChipList = ", ".join(str(K) for K in self.MountedChips.keys())
            Lines.append("Mounted Isolinear Chips (" + str(len(self.MountedChips)) + "): " + ChipList)
        Lines.append("Active Interfaces: " + str(list(self.ActiveInterfaces.keys())))
        return "\n".join(Lines)


    # Збір телеметрії бортового комп'ютера
    def GetTelemetry(self):
        OnlineCount = sum(1 for S in self.Subsystems.values() if SubsystemState.IsOperational(S))
        return {
            "Ship": f"{self.ShipClass} [{self.ShipRegistry}]",
            "Stardate": self.GetStardate(),
            "EarthDate": self.GetEarthDate(),
            "ProcessorMode": self.RuntimeMode,
            "SubsystemsOnline": OnlineCount,
            "SubsystemsTotal": len(self.Subsystems),
            "Subsystems": self.Subsystems,
            "MountedChips": list(self.MountedChips.keys()),
            "ActiveInterfaces": list(self.ActiveInterfaces.keys()),
            "Registers": self.Processor.Registers,
        }

    def ProcessVoiceDirective(self, DirectiveText: str, StreamCallback = None) -> str:
        Result = self.ExecuteDirective(DirectiveText, StreamCallback=StreamCallback)
        if isinstance(Result, dict):
            return Result.get("Message", "Directive processed.")
        return str(Result)

    def GetDiagnostics(self) -> dict:
        Telemetry = self.GetTelemetry()
        return {
            "State": "NOMINAL",
            "Ship": Telemetry["Ship"],
            "Stardate": Telemetry["Stardate"],
            "Subsystems": Telemetry["Subsystems"],
            "OnlineCount": Telemetry["SubsystemsOnline"],
            "TotalCount": Telemetry["SubsystemsTotal"],
        }

    def SystemSummary(self) -> dict:
        return self.GetDiagnostics()

    def GetCoreDiagnostics(self) -> dict:
        return self.GetDiagnostics()

    def Synthesize(self, PatternKey: str = "nova", Parent = None):
        ReplicatorModule = LCARS.Import("lcars.service.replicator")
        if ReplicatorModule and hasattr(ReplicatorModule, "LCARSReplicator"):
            Replicator = ReplicatorModule.LCARSReplicator.GetInstance()
            return Replicator.Materialize(PatternKey, Parent=Parent)
        return None

    def Replicate(self, PatternKey: str = "nova", Parent = None):
        return self.Synthesize(PatternKey, Parent=Parent)


__all__ = [
    "ProcessorState",
    "SubsystemState",
    "ProcessorInterrupt",
    "CoreProcessor",
    "BoardComputer",
]
