# ◤ TITANIUM SYSTEM LCARS SCRIPT INTERPRETER // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/system/interpreter.py
# ОПИС: Канонічний інтерпретатор та рантайм-рушій мови LCARS Script (.lcars).
#       Виконує синтаксичне дерево (AST) у пам'яті, підтримує області видимості
#       (Environment), функції, цикли, структури даних, симуляції Geant4
#       та системні інструкції з передачею телеметрії по шині ODN.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import SystemComponent, LCARS, Directive
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN, Transmission
from lcars.system.parser import Parser, ASTNode, NodeType
from lcars.system.lexer import Lexer

# Сигнал повернення значення з функції
class ReturnSignal(Exception):
    def __init__(self, Value: any = None):
        self.Value = Value

# Область видимості змінних та функцій
class Environment(LCARS):
    def __init__(self, Enclosing: Environment | None = None):
        super().__init__()
        self.Values: dict[str, any] = {}
        self.Enclosing = Enclosing

    def Define(self, Name: str, Value: any) -> None:
        self.Values[Name] = Value

    def Get(self, Name: str) -> any:
        if Name in self.Values:
            return self.Values[Name]
        if self.Enclosing:
            return self.Enclosing.Get(Name)
        return None

    def Assign(self, Name: str, Value: any) -> bool:
        if Name in self.Values:
            self.Values[Name] = Value
            return True
        if self.Enclosing:
            return self.Enclosing.Assign(Name, Value)
        self.Values[Name] = Value
        return True

    def Has(self, Name: str) -> bool:
        if Name in self.Values:
            return True
        if self.Enclosing:
            return self.Enclosing.Has(Name)
        return False

# Сценарій-функція користувача
class ScriptFunction(LCARS):
    def __init__(self, DeclarationNode: ASTNode, Closure: Environment):
        super().__init__()
        self.DeclarationNode = DeclarationNode
        self.Closure = Closure
        self.Name = str(DeclarationNode.Value)
        self.Parameters = [Child.Value for Child in DeclarationNode.Children if Child.Type == NodeType.IDENTIFIER]
        self.Body = [Child for Child in DeclarationNode.Children if Child.Type == NodeType.BLOCK]

    def Call(self, InterpreterInstance: Interpreter, Arguments: list[any]) -> any:
        CallEnvironment = Environment(self.Closure)
        for Index, ParamName in enumerate(self.Parameters):
            ArgValue = Arguments[Index] if Index < len(Arguments) else None
            CallEnvironment.Define(ParamName, ArgValue)

        SavedEnvironment = InterpreterInstance.CurrentEnvironment
        InterpreterInstance.CurrentEnvironment = CallEnvironment
        Result = None

        try:
            for BlockNode in self.Body:
                InterpreterInstance.Execute(BlockNode)
        except ReturnSignal as Signal:
            Result = Signal.Value
        finally:
            InterpreterInstance.CurrentEnvironment = SavedEnvironment

        return Result

# Головний інтерпретатор LCARS Script
class Interpreter(SystemComponent):
    Instance = None

    # Оптичні сигнали шини ODN
    ScriptExecuted = Transmission(str, dict)
    ScriptError = Transmission(str, str)
    OutputLogged = Transmission(str)
    SimulationRegistered = Transmission(str, dict)

    def __init__(self):
        super().__init__()
        self.Globals = Environment()
        self.CurrentEnvironment = self.Globals
        self.Simulations: dict[str, dict] = {}
        self.Detectors: dict[str, dict] = {}
        self.Analyzers: dict[str, dict] = {}
        self.Plugins: dict[str, dict] = {}
        self.Version = VersionInfo.GetVersion()
        self.RegisterBuiltins()

    @classmethod
    def GetInstance(cls) -> Interpreter:
        if cls.Instance is None:
            cls.Instance = Interpreter()
        return cls.Instance

    # ─── 1. ВБУДОВАНІ ФУНКЦІЇ ТА КОНСТАНТИ ─────────────────────────────────────

    def RegisterBuiltins(self) -> None:
        def BuiltinLog(*Args: any) -> str:
            Message = " ".join(str(A) for A in Args)
            self.OutputLogged.Emit(Message)
            ODN.Transmit("LCARS.Script.Log", Message=Message)
            return Message

        def BuiltinEmit(EventName: str, EventData: any = None) -> bool:
            Payload = EventData if isinstance(EventData, dict) else {"Data": EventData}
            ODN.Transmit(str(EventName), **Payload)
            return True

        def BuiltinExport(FilePath: str, Data: any) -> bool:
            JsonModule = LCARS.Storage.Json
            TargetFile = Directive.PathDrive(FilePath)
            TargetFile.parent.mkdir(parents=True, exist_ok=True)
            Content = JsonModule.dumps(Data, indent=2) if JsonModule else str(Data)
            TargetFile.write_text(Content, encoding="utf-8")
            ODN.Transmit("LCARS.Script.Exported", FilePath=str(TargetFile))
            return True

        def BuiltinLen(Item: any) -> int:
            if hasattr(Item, "__len__"):
                return len(Item)
            return 0

        def BuiltinSqrt(Value: float | int) -> float:
            return float(Value) ** 0.5

        def BuiltinAbs(Value: float | int) -> float:
            return abs(float(Value))

        def BuiltinRound(Value: float | int, Decimals: int = 0) -> float:
            return round(float(Value), int(Decimals))

        # Функції
        self.Globals.Define("log", BuiltinLog)
        self.Globals.Define("emit", BuiltinEmit)
        self.Globals.Define("export", BuiltinExport)
        self.Globals.Define("len", BuiltinLen)
        self.Globals.Define("sqrt", BuiltinSqrt)
        self.Globals.Define("abs", BuiltinAbs)
        self.Globals.Define("round", BuiltinRound)

        # Фізичні та математичні константи Зоряного Флоту
        self.Globals.Define("PI", 3.141592653589793)
        self.Globals.Define("E", 2.718281828459045)
        self.Globals.Define("LIGHTSPEED", 299792458)
        self.Globals.Define("WARPFACTORMAX", 9.99)

    # ─── 2. ГОЛОВНИЙ ДИСПЕТЧЕР ВИКОНАННЯ AST ──────────────────────────────────

    def Execute(self, Node: ASTNode) -> any:
        if not Node:
            return None

        Type = Node.Type

        # Програма та блоки
        if Type == NodeType.PROGRAM or Type == NodeType.BLOCK:
            Result = None
            for Child in Node.Children:
                Result = self.Execute(Child)
            return Result

        # Декларації змінних
        if Type == NodeType.VARIABLE_DECLARATION:
            Value = self.Execute(Node.Children[0]) if Node.Children else None
            self.CurrentEnvironment.Define(str(Node.Value), Value)
            return Value

        # Присвоєння
        if Type == NodeType.ASSIGNMENT:
            TargetNode = Node.Children[0]
            Value = self.Execute(Node.Children[1])
            if TargetNode.Type == NodeType.IDENTIFIER:
                self.CurrentEnvironment.Assign(str(TargetNode.Value), Value)
            elif TargetNode.Type == NodeType.MEMBER_EXPRESSION:
                Container = self.Execute(TargetNode.Children[0])
                Prop = TargetNode.Children[1].Value if len(TargetNode.Children) > 1 else None
                if isinstance(Container, dict) and Prop is not None:
                    Container[Prop] = Value
                elif isinstance(Container, list) and isinstance(Prop, int) and 0 <= Prop < len(Container):
                    Container[Prop] = Value
            return Value

        # Функції та процедури
        if Type == NodeType.FUNCTION_DECLARATION or Type == NodeType.PROCEDURE_DECLARATION:
            Func = ScriptFunction(Node, self.CurrentEnvironment)
            self.CurrentEnvironment.Define(str(Node.Value), Func)
            return Func

        # Повернення значення
        if Type == NodeType.RETURN_STATEMENT:
            Value = self.Execute(Node.Children[0]) if Node.Children else None
            raise ReturnSignal(Value)

        # Розгалуження IF / ELSE
        if Type == NodeType.IF_STATEMENT:
            Condition = self.Execute(Node.Children[0])
            if Condition:
                return self.Execute(Node.Children[1])
            elif len(Node.Children) > 2:
                return self.Execute(Node.Children[2])
            return None

        # Цикли
        if Type == NodeType.WHILE_STATEMENT:
            CondNode = Node.Children[0]
            BodyNode = Node.Children[1]
            LastResult = None
            while self.Execute(CondNode):
                LastResult = self.Execute(BodyNode)
            return LastResult

        if Type == NodeType.FOR_STATEMENT:
            InitNode = Node.Children[0] if len(Node.Children) > 0 else None
            CondNode = Node.Children[1] if len(Node.Children) > 1 else None
            StepNode = Node.Children[2] if len(Node.Children) > 2 else None
            BodyNode = Node.Children[3] if len(Node.Children) > 3 else None
            if InitNode:
                self.Execute(InitNode)
            LastResult = None
            while CondNode is None or self.Execute(CondNode):
                if BodyNode:
                    LastResult = self.Execute(BodyNode)
                if StepNode:
                    self.Execute(StepNode)
            return LastResult

        if Type == NodeType.FOREACH_STATEMENT:
            VarName = str(Node.Value)
            Collection = self.Execute(Node.Children[0])
            BodyNode = Node.Children[1]
            LastResult = None
            if hasattr(Collection, "__iter__"):
                for Item in Collection:
                    self.CurrentEnvironment.Define(VarName, Item)
                    LastResult = self.Execute(BodyNode)
            return LastResult

        # Інструкція-вираз
        if Type == NodeType.EXPRESSION_STATEMENT:
            return self.Execute(Node.Children[0]) if Node.Children else None

        # Бінарні операції
        if Type == NodeType.BINARY_EXPRESSION:
            return self.EvaluateBinary(Node)

        # Унарні операції
        if Type == NodeType.UNARY_EXPRESSION:
            Operand = self.Execute(Node.Children[0])
            Operator = str(Node.Value)
            if Operator == "-":
                return -Operand
            if Operator == "not":
                return not Operand
            return Operand

        # Виклик функції
        if Type == NodeType.CALL_EXPRESSION:
            Callee = self.Execute(Node.Children[0])
            Args = [self.Execute(Child) for Child in Node.Children[1:]]
            if callable(Callee):
                return Callee(*Args)
            if isinstance(Callee, ScriptFunction):
                return Callee.Call(self, Args)
            return None

        # Звернення до властивостей / елементів
        if Type == NodeType.MEMBER_EXPRESSION:
            Container = self.Execute(Node.Children[0])
            Prop = Node.Children[1].Value if len(Node.Children) > 1 else None
            if isinstance(Container, dict) and Prop in Container:
                return Container[Prop]
            if isinstance(Container, list) and isinstance(Prop, int) and 0 <= Prop < len(Container):
                return Container[Prop]
            return getattr(Container, str(Prop), None)

        # Літерали та ідентифікатори
        if Type == NodeType.LITERAL:
            return Node.Value

        if Type == NodeType.IDENTIFIER:
            return self.CurrentEnvironment.Get(str(Node.Value))

        if Type == NodeType.ARRAY_LITERAL:
            return [self.Execute(Child) for Child in Node.Children]

        if Type == NodeType.OBJECT_LITERAL:
            ObjectResult = {}
            for PropNode in Node.Children:
                Key = str(PropNode.Value)
                Val = self.Execute(PropNode.Children[0]) if PropNode.Children else None
                ObjectResult[Key] = Val
            return ObjectResult

        # Спеціальні блоки LCARS (Симуляції, Детектори, Аналізатори)
        if Type in {NodeType.SIMULATION_DECLARATION, NodeType.DETECTOR_DECLARATION,
                    NodeType.ANALYZER_DECLARATION, NodeType.VISUALIZE_DECLARATION, NodeType.PLUGIN_DECLARATION}:
            return self.RegisterDeclaration(Node)

        return None

    # ─── 3. ОБЧИСЛЕННЯ БІНАРНИХ ОПЕРАЦІЙ ──────────────────────────────────────

    def EvaluateBinary(self, Node: ASTNode) -> any:
        Left = self.Execute(Node.Children[0])
        Right = self.Execute(Node.Children[1])
        Op = str(Node.Value)

        if Op == "+":
            return Left + Right
        if Op == "-":
            return Left - Right
        if Op == "*":
            return Left * Right
        if Op == "/":
            return Left / Right if Right != 0 else 0
        if Op == "%":
            return Left % Right if Right != 0 else 0
        if Op == "^":
            return Left ** Right
        if Op == "==":
            return Left == Right
        if Op == "!=":
            return Left != Right
        if Op == "<":
            return Left < Right
        if Op == "<=":
            return Left <= Right
        if Op == ">":
            return Left > Right
        if Op == ">=":
            return Left >= Right
        if Op == "and":
            return Left and Right
        if Op == "or":
            return Left or Right
        return None

    # ─── 4. РЕЄСТРАЦІЯ СПЕЦІАЛЬНИХ ДЕКЛАРАЦІЙ LCARS ────────────────────────────

    def RegisterDeclaration(self, Node: ASTNode) -> dict:
        Name = str(Node.Value)
        Type = Node.Type
        Descriptor = {
            "Name": Name,
            "Type": Type,
            "ChildrenCount": len(Node.Children),
            "Line": Node.Line,
        }

        if Type == NodeType.SIMULATION_DECLARATION:
            self.Simulations[Name] = Descriptor
            self.SimulationRegistered.Emit(Name, Descriptor)
            ODN.Transmit("LCARS.Simulation.Registered", Name=Name)
        elif Type == NodeType.DETECTOR_DECLARATION:
            self.Detectors[Name] = Descriptor
        elif Type == NodeType.ANALYZER_DECLARATION:
            self.Analyzers[Name] = Descriptor
        elif Type == NodeType.PLUGIN_DECLARATION:
            self.Plugins[Name] = Descriptor

        return Descriptor

    # ─── 5. ПУБЛІЧНІ МЕТОДИ ВИКОНАННЯ ─────────────────────────────────────────

    def Interpret(self, AstTree: ASTNode) -> any:
        return self.Execute(AstTree)

    def ExecuteSource(self, SourceCode: str) -> any:
        LexerInstance = Lexer(SourceCode)
        Tokens = LexerInstance.Tokenize()
        ParserInstance = Parser(Tokens)
        AstTree = ParserInstance.Parse()
        Result = self.Execute(AstTree)
        self.ScriptExecuted.Emit("DirectSource", {"Result": str(Result)})
        return Result

    def ExecuteFile(self, FilePath: any) -> any:
        PathItem = Directive.PathDrive(FilePath)
        if not PathItem.exists():
            ErrorMessage = f"Script file not found: {PathItem}"
            self.ScriptError.Emit(str(PathItem), ErrorMessage)
            return None
        SourceText = PathItem.read_text(encoding="utf-8", errors="replace")
        return self.ExecuteSource(SourceText)

    def Reset(self) -> None:
        self.Globals = Environment()
        self.CurrentEnvironment = self.Globals
        self.Simulations.clear()
        self.Detectors.clear()
        self.Analyzers.clear()
        self.Plugins.clear()
        self.RegisterBuiltins()

# Експорт інтерпретатора
InterpreterCore = Interpreter.GetInstance
INTERPRETER = Interpreter.GetInstance()
