# LCARS system runtime.
# Призначення: виконує AST у контрольованому контексті борта й агентів.
# Runtime не створює окремої мережі: події й команди йдуть через переданий ODN,
# а режим OPTICAL/QUANTUM змінює лише обчислювальний контекст.

# Titanium Bridge Migration: from dataclasses import dataclass, field
# Titanium Bridge Migration: from typing import Any, Callable, Dict, List, Optional

from lcars.base.type import LCARS, Namespace
from .lexer import Lexer
from .parser import ASTNode, NodeType, Parser

class StateItem(str):
    @property
    def name(self) -> str:
        return self
    @property
    def value(self) -> str:
        return self

class SystemTimeNamespace(metaclass=Namespace):
    NamespacePath = "System.Time"

class RuntimeMode(LCARS):
    OPTICAL = StateItem("OPTICAL")
    NORMAL = StateItem("OPTICAL")
    QUANTUM = StateItem("QUANTUM")


@dataclass
class RuntimeError:
    message: str
    line: int = 0
    column: int = 0

    def __str__(self) -> str:
        Location = "" if self.line <= 0 else " " + str(self.line) + ":" + str(self.column)
        return "RUNTIME" + Location + " " + self.message


@dataclass
class SimulationResult:
    name: str
    status: str
    start_time: Any
    end_time: Optional[Any] = None
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class ExecutionStats:
    total_simulations: int = 0
    completed_simulations: int = 0
    failed_simulations: int = 0
    total_execution_time: float = 0.0


@dataclass
class RuntimeResult:
    success: bool
    value: Any = None
    errors: List[str] = field(default_factory=list)
    mode: str = RuntimeMode.OPTICAL.value


@dataclass
class RuntimeFunction:
    parameters: List[str]
    body: ASTNode
    runtime: "LCARSRuntime"

    def Call(self, Values: List[Any]) -> Any:
        Previous = self.runtime.Variables.copy()
        for Index, Name in enumerate(self.parameters):
            self.runtime.Variables[Name] = Values[Index] if Index < len(Values) else None
        Flow = self.runtime.ExecuteNode(self.body)
        self.runtime.Variables = Previous
        return Flow.value


class LCARSRuntime:
    # Усі скриптові виклики проходять через цей контекст, що дає агентам один
    # спосіб читати стан і посилати сигнал незалежно від режиму борта.
    def __init__(self, event_bus=None, ODNNode=None, Kernel=None, Mode: RuntimeMode = RuntimeMode.OPTICAL):
        self.EventBus = event_bus
        self.ODN = ODNNode
        if self.ODN is None:
            from lcars.core.signal import ODNInstance
            self.ODN = ODNInstance
        self.Kernel = Kernel
        self.Mode = Mode
        self.Simulations: Dict[str, Any] = {}
        self.Detectors: Dict[str, Any] = {}
        self.Analyzers: Dict[str, Any] = {}
        self.Functions: Dict[str, Any] = {}
        self.Variables: Dict[str, Any] = {}
        self.ExecutionStats = ExecutionStats()
        self.CurrentSimulation: Optional[str] = None
        self.SimulationResults: List[SimulationResult] = []
        self.IsRunning = False
        self.StartTime: Optional[Any] = None
        self.LastResult = RuntimeResult(True, mode=self.Mode.value)
        self.PhysicsConstants = {
            "c": 299792458,
            "e": 1.602176634e-19,
            "m_e": 9.1093837015e-31,
            "m_p": 1.67262192369e-27,
            "h": 6.62607015e-34,
            "k_B": 1.380649e-23,
            "NA": 6.02214076e23,
        }
        self.InitializeEnvironment()

    def InitializeEnvironment(self) -> None:
        self.Variables.update(self.PhysicsConstants)
        self.Variables.update({"pi": LCARS.System.Math.pi, "euler": LCARS.System.Math.e, "tau": LCARS.System.Math.tau})
        self.Functions.update({
            "log": self.LcarsLog,
            "emit": self.LcarsEmit,
            "export": self.LcarsExport,
            "len": len,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "str": str,
            "int": int,
            "float": float,
            "sqrt": LCARS.System.Math.sqrt,
            "sin": LCARS.System.Math.sin,
            "cos": LCARS.System.Math.cos,
            "tan": LCARS.System.Math.tan,
            "range": range,
            # Час / дата (через існуючий ChronometerSubsystem)
            "time": self.SysTime,
            "stardate": self.SysStardate,
            "earthDate": self.SysEarthDate,
            # Файлова система (через Kernel.Service("file"))
            "read": self.SysRead,
            "write": self.SysWrite,
            "list": self.SysList,
            "exists": self.SysExists,
            "delete": self.SysDelete,
            # Процеси (через Kernel.ProcessStart)
            "spawn": self.SysSpawn,
            "kill": self.SysKill,
            # Таймер / затримка
            "wait": self.SysWait,
            "sleep": self.SysWait,
            # Мережа (через Kernel.Service("network"))
            "http": self.SysHttp,
        })

    def SetMode(self, Mode: RuntimeMode) -> RuntimeMode:
        self.Mode = Mode
        self.LastResult.mode = Mode.value
        self.Publish("Runtime.ModeChanged", {"mode": Mode.value})
        return self.Mode

    def Publish(self, Channel: str, Data: Dict[str, Any]) -> None:
        # ODN має бути єдиним каналом; EventBus лишається тільки legacy fallback.
        if self.ODN is not None and hasattr(self.ODN, "Emit"):
            self.ODN.Emit(Channel, Data)
            return
        if self.EventBus is not None and hasattr(self.EventBus, "emit"):
            self.EventBus.emit(Channel, Data)

    def CompileSource(self, Source: str) -> Optional[ASTNode]:
        Lex = Lexer(Source)
        Tokens = Lex.tokenize()
        if Lex.Error is not None:
            self.LastResult = RuntimeResult(False, errors=[str(Lex.Error)], mode=self.Mode.value)
            return None
        Tree = Parser(Tokens)
        Ast = Tree.parse()
        if Tree.Errors:
            self.LastResult = RuntimeResult(False, errors=[str(Item) for Item in Tree.Errors], mode=self.Mode.value)
            return None
        return Ast

    def ExecuteSource(self, Source: str, ScriptName: str = "Main") -> RuntimeResult:
        Ast = self.CompileSource(Source)
        if Ast is None:
            return self.LastResult
        self.IsRunning = True
        self.StartTime = LCARS.System.DateTime.now(SystemTimeNamespace.TimeZone.utc)
        Flow = self.ExecuteNode(Ast)
        self.IsRunning = False
        Errors = [] if Flow.error is None else [str(Flow.error)]
        self.LastResult = RuntimeResult(Flow.error is None, Flow.value, Errors, self.Mode.value)
        self.Publish("Runtime.Completed", {"script": ScriptName, "success": self.LastResult.success, "mode": self.Mode.value})
        return self.LastResult

    def ExecuteScript(self, ScriptPath: str) -> bool:
        Target = LCARS.System.Path(ScriptPath)
        if not Target.exists():
            self.LastResult = RuntimeResult(False, errors=["script file not found: " + str(Target)], mode=self.Mode.value)
            return False
        Result = self.ExecuteSource(Target.read_text(encoding="utf-8"), Target.name)
        return Result.success

    def CompileScript(self, ScriptPath: str) -> str:
        from .compiler import PythonCompiler
        Target = LCARS.System.Path(ScriptPath)
        if not Target.exists():
            self.LastResult = RuntimeResult(False, errors=["script file not found: " + str(Target)], mode=self.Mode.value)
            return ""
        Ast = self.CompileSource(Target.read_text(encoding="utf-8"))
        return "" if Ast is None else PythonCompiler().compile(Ast)

    def ExecuteCompiledScript(self, CompiledPath: str) -> bool:
        # Python-артефакт є результатом компіляції, але не входом безпечного
        # runtime. Повторне виконання завжди має йти з вихідного .lcars AST.
        self.LastResult = RuntimeResult(False, errors=["compiled artifact requires source AST"], mode=self.Mode.value)
        return False

    def ExecuteNode(self, Node: ASTNode) -> "Flow":
        if Node.type == NodeType.PROGRAM or Node.type == NodeType.BLOCK:
            Result = Flow()
            for Child in Node.children:
                Result = self.ExecuteNode(Child)
                if Result.returned or Result.error is not None:
                    return Result
            return Result
        if Node.type in (NodeType.FUNCTION_DECLARATION, NodeType.PROCEDURE_DECLARATION):
            Parameters = [Child.value for Child in Node.children if Child.type == NodeType.IDENTIFIER]
            Body = next((Child for Child in Node.children if Child.type == NodeType.BLOCK), ASTNode(NodeType.BLOCK))
            self.Functions[str(Node.value)] = RuntimeFunction(Parameters, Body, self)
            return Flow()
        if Node.type in (NodeType.SIMULATION_DECLARATION, NodeType.DETECTOR_DECLARATION, NodeType.ANALYZER_DECLARATION, NodeType.VISUALIZE_DECLARATION, NodeType.PLUGIN_DECLARATION):
            return self.ExecuteNode(next((Child for Child in Node.children if Child.type == NodeType.BLOCK), ASTNode(NodeType.BLOCK)))
        if Node.type == NodeType.EVENT_HANDLER:
            return Flow()
        if Node.type in (NodeType.VARIABLE_DECLARATION, NodeType.ASSIGNMENT):
            self.Variables[str(Node.value)] = self.Evaluate(Node.children[0]) if Node.children else None
            return Flow(self.Variables[str(Node.value)])
        if Node.type == NodeType.EXPRESSION_STATEMENT:
            return Flow(self.Evaluate(Node.children[0]) if Node.children else None)
        if Node.type == NodeType.RETURN_STATEMENT:
            return Flow(self.Evaluate(Node.children[0]) if Node.children else None, returned=True)
        if Node.type == NodeType.IF_STATEMENT:
            Branch = Node.children[1] if self.Evaluate(Node.children[0]) else (Node.children[2] if len(Node.children) > 2 else ASTNode(NodeType.BLOCK))
            return self.ExecuteNode(Branch)
        if Node.type == NodeType.WHILE_STATEMENT:
            Count = 0
            while self.Evaluate(Node.children[0]) and Count < 10000:
                Result = self.ExecuteNode(Node.children[1])
                if Result.returned or Result.error is not None:
                    return Result
                Count += 1
            return Flow()
        if Node.type == NodeType.FOR_STATEMENT:
            IteratorName = Node.value.get("iterator", "i")
            Collection = self.Evaluate(Node.children[0])
            Body = Node.children[1]
            self.Variables[IteratorName] = None
            Count = 0
            Result = Flow()
            for Item in (Collection if hasattr(Collection, '__iter__') else []):
                self.Variables[IteratorName] = Item
                Result = self.ExecuteNode(Body)
                if Result.returned or Result.error is not None:
                    break
                Count += 1
                if Count >= 10000:
                    break
            return Result
        if Node.type == NodeType.FOREACH_STATEMENT:
            IteratorName = Node.value.get("iterator", "item")
            Collection = self.Evaluate(Node.children[0])
            Body = Node.children[1]
            self.Variables[IteratorName] = None
            Count = 0
            Result = Flow()
            for Item in (Collection if hasattr(Collection, '__iter__') else []):
                self.Variables[IteratorName] = Item
                Result = self.ExecuteNode(Body)
                if Result.returned or Result.error is not None:
                    break
                Count += 1
                if Count >= 10000:
                    break
            return Result
        if Node.type == NodeType.IMPORT_STATEMENT:
            ModuleName = str(Node.value)
            if ModuleName in LCARS.System.Core.modules:
                self.Variables[ModuleName] = LCARS.System.Core.modules[ModuleName]
            else:
                self.Variables[ModuleName] = ModuleName
            return Flow()
        if Node.type == NodeType.EXPORT_STATEMENT:
            Value = self.Evaluate(Node.children[0]) if Node.children else None
            return Flow(Value)
        if Node.type == NodeType.LOG_STATEMENT:
            Args = [self.Evaluate(Child) for Child in Node.children]
            return Flow(self.LcarsLog(*Args))
        if Node.type == NodeType.EMIT_STATEMENT:
            Channel = self.Evaluate(Node.children[0]) if len(Node.children) > 0 else ""
            Data = self.Evaluate(Node.children[1]) if len(Node.children) > 1 else {}
            return Flow(self.LcarsEmit(str(Channel), Data if isinstance(Data, dict) else {"value": Data}))
        return Flow()

    def Evaluate(self, Node: ASTNode) -> Any:
        if Node.type == NodeType.LITERAL:
            return self.ConvertLiteral(Node.value)
        if Node.type == NodeType.IDENTIFIER:
            if Node.value in self.Variables:
                return self.Variables[Node.value]
            return self.Functions.get(Node.value)
        if Node.type == NodeType.ARRAY_LITERAL:
            return [self.Evaluate(Item) for Item in Node.children]
        if Node.type == NodeType.OBJECT_LITERAL:
            return {str(Item.value): self.Evaluate(Item.children[0]) for Item in Node.children}
        if Node.type == NodeType.MEMBER_EXPRESSION:
            Target = self.Evaluate(Node.children[0])
            Key = self.Evaluate(Node.children[1])
            if Node.value == "[]" and isinstance(Target, (list, tuple, dict)):
                return Target[Key]
            if isinstance(Target, dict):
                return Target.get(Key)
            return getattr(Target, str(Key), None)
        if Node.type == NodeType.CALL_EXPRESSION:
            Function = self.Evaluate(Node.children[0])
            Values = [self.Evaluate(Item) for Item in Node.children[1:]]
            if isinstance(Function, RuntimeFunction):
                return Function.Call(Values)
            if callable(Function):
                return Function(*Values)
            return None
        if Node.type == NodeType.UNARY_EXPRESSION:
            Value = self.Evaluate(Node.children[0])
            return (not Value) if str(Node.value).lower() == "not" else (-Value if Node.value == "-" else Value)
        if Node.type == NodeType.BINARY_EXPRESSION:
            Left = self.Evaluate(Node.children[0])
            Right = self.Evaluate(Node.children[1])
            return self.ApplyOperator(str(Node.value), Left, Right)
        return None

    def ApplyOperator(self, Operator: str, Left: Any, Right: Any) -> Any:
        Operations = {
            "+": lambda: Left + Right, "-": lambda: Left - Right,
            "*": lambda: Left * Right, "/": lambda: Left / Right,
            "%": lambda: Left % Right, "^": lambda: Left ** Right,
            "==": lambda: Left == Right, "!=": lambda: Left != Right,
            "<": lambda: Left < Right, "<=": lambda: Left <= Right,
            ">": lambda: Left > Right, ">=": lambda: Left >= Right,
            "and": lambda: bool(Left and Right), "or": lambda: bool(Left or Right),
        }
        Action = Operations.get(Operator.lower())
        return Action() if Action is not None else None

    def ConvertLiteral(self, Value: Any) -> Any:
        if not isinstance(Value, str):
            return Value
        Text = Value.strip()
        if Text == "":
            return ""
        if Text.isdigit() or (Text.startswith("-") and Text[1:].isdigit()):
            return int(Text)
        if Text.count(".") == 1 and all(Item.isdigit() for Item in Text.split(".")):
            return float(Text)
        return Value

    def RegisterSimulation(self, Name: str, SimulationClass: type) -> None:
        self.Simulations[Name] = SimulationClass

    def RegisterDetector(self, Name: str, DetectorClass: type) -> None:
        self.Detectors[Name] = DetectorClass

    def RegisterAnalyzer(self, Name: str, AnalyzerClass: type) -> None:
        self.Analyzers[Name] = AnalyzerClass

    def RegisterFunction(self, Name: str, Function: Callable) -> None:
        self.Functions[Name] = Function

    def RunSimulation(self, Name: str, **Params: Any) -> SimulationResult:
        Started = LCARS.System.DateTime.now(SystemTimeNamespace.TimeZone.utc)
        Result = SimulationResult(Name, "error", Started, error="simulation not found")
        if Name in self.Simulations:
            Instance = self.Simulations[Name]()
            for Key, Value in Params.items():
                if hasattr(Instance, Key):
                    setattr(Instance, Key, Value)
            Data = Instance.run() if hasattr(Instance, "run") else {}
            Result.status = "completed"
            Result.data = Data if isinstance(Data, dict) else {"value": Data}
            self.ExecutionStats.completed_simulations += 1
        else:
            self.ExecutionStats.failed_simulations += 1
        Result.end_time = LCARS.System.DateTime.now(SystemTimeNamespace.TimeZone.utc)
        self.ExecutionStats.total_simulations += 1
        self.ExecutionStats.total_execution_time += (Result.end_time - Result.start_time).total_seconds()
        self.SimulationResults.append(Result)
        return Result

    def GetSimulationStatus(self, Name: str) -> Optional[str]:
        Items = self.GetSimulationResults(Name)
        return Items[-1].status if Items else None

    def GetSimulationResults(self, Name: Optional[str] = None) -> List[SimulationResult]:
        return [Item for Item in self.SimulationResults if Name is None or Item.name == Name]

    def GetExecutionStats(self) -> ExecutionStats:
        return self.ExecutionStats

    def ResetStats(self) -> None:
        self.ExecutionStats = ExecutionStats()
        self.SimulationResults.clear()

    def LcarsLog(self, *Args: Any) -> str:
        Message = " ".join(str(Item) for Item in Args)
        self.Publish("Runtime.Log", {"message": Message, "mode": self.Mode.value})
        return Message

    def LcarsEmit(self, Channel: str, Data: Optional[Dict[str, Any]] = None) -> bool:
        self.Publish(str(Channel), Data or {})
        return True

    def LcarsExport(self, Filename: str, Data: Any = None) -> bool:
        Target = LCARS.System.Path(Filename)
        Payload = Data if Data is not None else {}
        Target.write_text(LCARS.System.Serialization.dumps(Payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        return True

    # Час / дата — через існуючий ChronometerSubsystem
    def SysTime(self, Format: str = "%Y-%m-%d %H:%M:%S") -> str:
        from lcars.tools.chronometer import ChronometerSubsystem
        return ChronometerSubsystem.GetNow(Format)

    def SysStardate(self) -> float:
        from lcars.tools.chronometer import ChronometerSubsystem
        return ChronometerSubsystem.GetStardate()

    def SysEarthDate(self) -> str:
        from lcars.tools.chronometer import ChronometerSubsystem
        return ChronometerSubsystem.GetEarthDate()

    # Файлова система — через Kernel.Service("file")
    def SysRead(self, PathStr: str) -> str:
        if self.Kernel is None:
            return ""
        FileSvc = self.Kernel.Service("file")
        if FileSvc and hasattr(FileSvc, "Read"):
            return FileSvc.Read(PathStr)
        return ""

    def SysWrite(self, PathStr: str, Data: Any) -> bool:
        if self.Kernel is None:
            return False
        FileSvc = self.Kernel.Service("file")
        if FileSvc and hasattr(FileSvc, "Write"):
            return FileSvc.Write(PathStr, Data)
        return False

    def SysList(self, PathStr: str) -> List[str]:
        if self.Kernel is None:
            return []
        FileSvc = self.Kernel.Service("file")
        if FileSvc and hasattr(FileSvc, "List"):
            return FileSvc.List(PathStr)
        return []

    def SysExists(self, PathStr: str) -> bool:
        if self.Kernel is None:
            return False
        FileSvc = self.Kernel.Service("file")
        if FileSvc and hasattr(FileSvc, "Exists"):
            return FileSvc.Exists(PathStr)
        return False

    def SysDelete(self, PathStr: str) -> bool:
        if self.Kernel is None:
            return False
        FileSvc = self.Kernel.Service("file")
        if FileSvc and hasattr(FileSvc, "Delete"):
            return FileSvc.Delete(PathStr)
        return False

    # Процеси — через Kernel.ProcStart
    def SysSpawn(self, Command: str, Args: List[str] = None) -> bool:
        if self.Kernel is None:
            return False
        Name = "user_" + str(int(LCARS.System.DateTime.now(SystemTimeNamespace.TimeZone.utc).timestamp()))
        return self.Kernel.ProcStart(Name, Command, Args)

    def SysKill(self, Name: str) -> bool:
        if self.Kernel is None:
            return False
        return self.Kernel.ProcStop(Name)

    # Таймер / затримка
    def SysWait(self, Milliseconds: float) -> None:
        import time
        time.sleep(Milliseconds / 1000.0)

    # Мережа — через Kernel.Service("network")
    def SysHttp(self, Url: str) -> Dict[str, Any]:
        if self.Kernel is None:
            return {"error": "no kernel"}
        NetSvc = self.Kernel.Service("network")
        if NetSvc and hasattr(NetSvc, "SubspaceRequest"):
            Result = NetSvc.SubspaceRequest(Url)
            return {"result": Result}
        return {"error": "no network service"}


@dataclass
class Flow:
    value: Any = None
    returned: bool = False
    error: Optional[RuntimeError] = None


runtime = LCARSRuntime()


__all__ = ["RuntimeMode", "RuntimeError", "SimulationResult", "ExecutionStats", "RuntimeResult", "LCARSRuntime", "runtime"]
