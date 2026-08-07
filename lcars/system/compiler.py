# LCARS FRAMEWORK :: COMPILER // SYSTEM // UNIVERSAL TRANSPORT
# Призначення: компіляція джерельних файлів у переносимі артефакти.
# Базовий клас Compiler наслідується від LCARS та містить увесь інструментарій:
# хешування, запис, маніфести, ізолінійний індекс.
# Підкласи лише визначають розширення та спосіб обробки вмісту.

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

from lcars.base.type import LCARS
from .lexer import Lexer
from .parser import ASTNode, NodeType, Parser


# =====================================================================
# ДОПОМІЖНІ СТРУКТУРИ ДАНИХ
# =====================================================================

@dataclass
class CompileError:
    # CompileError — результат діагностики компіляції, а не exception.
    # Використовується для звітування про помилки без переривання потоку.
    message: str
    source: str = ""

    def __str__(self) -> str:
        return self.message


@dataclass
class CompileOptions:
    # CompileOptions — налаштування компіляції: куди писати, що створювати.
    output_dir: Path = Path("scripts/compiled")
    write_manifest: bool = True
    write_wrapper: bool = True
    copy_source: bool = True
    record_isolinear: bool = True


@dataclass
class CompilationResult:
    # CompilationResult — результат компіляції одного файлу.
    # Містить шляхи до вихідних файлів, статус, хеш та isolinear ID.
    kind: str
    source_path: Path
    output_path: Optional[Path] = None
    manifest_path: Optional[Path] = None
    wrapper_path: Optional[Path] = None
    isolinear_id: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)
    success: bool = True
    error: str = ""

    @property
    def isolinearId(self) -> Optional[str]:
        return self.isolinear_id


# =====================================================================
# БАЗОВИЙ КЛАС COMPILER — НАСЛІДУЄТЬСЯ ВІД LCARS
# =====================================================================

class Compiler(LCARS):
    # Compiler — базовий клас для всіх компіляторів артефактів.
    # Наслідується від LCARS та містить хешування, читання/запис файлів,
    # маніфести, ізолінійний індекс. Підкласи визначають extensions та Compile().

    kind = "base"
    extensions: Sequence[str] = ()

    # ---- Хешування ----

    @staticmethod
    def HashText(Text: str) -> str:
        # Повертає SHA-256 хеш рядка.
        return hashlib.sha256(Text.encode("utf-8")).hexdigest()

    @staticmethod
    def HashFile(PathValue: Path) -> str:
        # Повертає SHA-256 хеш вмісту файлу.
        return hashlib.sha256(PathValue.read_bytes()).hexdigest()

    # ---- Робота з файлами ----

    @staticmethod
    def LoadSource(PathValue: Path) -> Optional[str]:
        # Завантажує текстовий вміст файлу. Повертає None якщо файл не існує.
        if not PathValue.exists():
            return None
        return PathValue.read_text(encoding="utf-8")

    @staticmethod
    def WriteOutput(PathValue: Path, Content: str) -> None:
        # Записує текстовий вміст у файл, створюючи директорії якщо потрібно.
        PathValue.parent.mkdir(parents=True, exist_ok=True)
        PathValue.write_text(Content, encoding="utf-8")

    @staticmethod
    def WriteManifest(PathValue: Path, Data: Dict) -> None:
        # Записує JSON-маніфест артефакту.
        PathValue.parent.mkdir(parents=True, exist_ok=True)
        PathValue.write_text(json.dumps(Data, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---- Ізолінійний індекс ----

    @staticmethod
    def LoadIndex(IndexPath: Path) -> List[Dict[str, str]]:
        # Завантажує JSON-індекс артефактів. Повертає порожній список якщо файл не існує.
        if not IndexPath.exists():
            return []
        Text = IndexPath.read_text(encoding="utf-8").strip()
        if not Text:
            return []
        Value = json.loads(Text)
        return Value if isinstance(Value, list) else []

    @staticmethod
    def WriteIndex(IndexPath: Path, Index: List[Dict[str, str]]) -> None:
        # Записує JSON-індекс артефактів.
        IndexPath.parent.mkdir(parents=True, exist_ok=True)
        IndexPath.write_text(json.dumps(Index, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def RecordArtifact(Result: CompilationResult, StoreDir: Path) -> str:
        # Записує артефакт в ізолінійний індекс та повертає його ID.
        # Формат ID: {kind}-{timestamp}-{hash[:12]}
        if not Result.success:
            return ""
        IndexPath = StoreDir / "isolinear_index.json"
        Digest = Result.metadata.get("hash", "unknown")[:12]
        Stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        ArtifactId = Result.kind + "-" + Stamp + "-" + Digest
        Index = Compiler.LoadIndex(IndexPath)
        Index.append({
            "id": ArtifactId,
            "kind": Result.kind,
            "source": str(Result.source_path),
            "output": str(Result.output_path) if Result.output_path else "",
            "manifest": str(Result.manifest_path) if Result.manifest_path else "",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "hash": Result.metadata.get("hash", ""),
        })
        Compiler.WriteIndex(IndexPath, Index)
        return ArtifactId

    # ---- Базові методи компіляції ----

    def Supports(self, PathValue: Path) -> bool:
        # Перевіряє, чи підтримує даний клас це розширення файлу.
        return PathValue.suffix.lower() in self.extensions

    def Compile(self, PathValue: Path, Options: CompileOptions) -> CompilationResult:
        # Віртуальний метод компіляції. Підкласи мають перевизначити.
        return CompilationResult(self.kind, PathValue, success=False, error="compiler is not implemented")


# =====================================================================
# КОМАНДНІ ФАЙЛИ — БАЗОВИЙ ДЛЯ .cmd, .bat, .ps1, .sh, .py
# =====================================================================

class Command(Compiler):
    # Command — базовий клас для командних файлів.
    # Копіює файли як артефакти або описує їх для Terminal Link.

    kind = "command"
    extensions: Sequence[str] = ()
    shell_command: Sequence[str] = ()

    def Compile(self, PathValue: Path, Options: CompileOptions) -> CompilationResult:
        # Копіює файл до output_dir та створює маніфест.
        if not PathValue.exists():
            return CompilationResult(self.kind, PathValue, success=False, error="source file not found")
        OutputDir = Path(Options.output_dir)
        OutputDir.mkdir(parents=True, exist_ok=True)
        Entry = OutputDir / PathValue.name if Options.copy_source else PathValue
        if Options.copy_source:
            Entry.write_bytes(PathValue.read_bytes())
        Digest = Compiler.HashFile(PathValue)
        ManifestPath = None
        if Options.write_manifest:
            ManifestPath = OutputDir / (PathValue.stem + "." + self.kind + ".lcarc.json")
            Compiler.WriteManifest(ManifestPath, {
                "kind": self.kind,
                "source": str(PathValue),
                "entry": str(Entry),
                "hash": Digest,
                "transport": "terminal-link",
            })
        return CompilationResult(self.kind, PathValue, Entry, ManifestPath, metadata={"hash": Digest})


# =====================================================================
# КОМАНДНІ ФАЙЛИ — КОНКРЕТНІ ТИПИ
# =====================================================================

class Cmd(Command):
    # Cmd — обробка .cmd та .bat файлів Windows.

    kind = "cmd"
    extensions = (".cmd", ".bat")


class PowerShell(Command):
    # PowerShell — обробка .ps1 файлів PowerShell.

    kind = "powershell"
    extensions = (".ps1",)


class Bash(Command):
    # Bash — обробка .sh файлів Bash.

    kind = "bash"
    extensions = (".sh",)


class PythonScript(Command):
    # PythonScript — обробка .py та .pyw файлів Python.

    kind = "python"
    extensions = (".py", ".pyw")


# =====================================================================
# ДАНОВІ ФАЙЛИ — .json, .yaml, .toml, .txt, .md, .xml
# =====================================================================

class Data(Compiler):
    # Data — базовий клас для данових файлів.
    # Копіює файли як артефакти без трансформації.

    kind = "data"
    extensions = (".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".txt", ".md", ".xml")

    def Compile(self, PathValue: Path, Options: CompileOptions) -> CompilationResult:
        # Копіює файл та створює маніфест.
        if not PathValue.exists():
            return CompilationResult(self.kind, PathValue, success=False, error="source file not found")
        OutputDir = Path(Options.output_dir)
        OutputDir.mkdir(parents=True, exist_ok=True)
        Entry = OutputDir / PathValue.name if Options.copy_source else PathValue
        if Options.copy_source:
            Entry.write_bytes(PathValue.read_bytes())
        Digest = Compiler.HashFile(PathValue)
        ManifestPath = None
        if Options.write_manifest:
            ManifestPath = OutputDir / (PathValue.stem + ".data.lcarc.json")
            Compiler.WriteManifest(ManifestPath, {
                "kind": self.kind,
                "source": str(PathValue),
                "entry": str(Entry),
                "hash": Digest,
            })
        return CompilationResult(self.kind, PathValue, Entry, ManifestPath, metadata={"hash": Digest})


# =====================================================================
# РЕСУРСНІ ФАЙЛИ — ВСЕ ЩО НЕ ПІДТРИМУЄТЬСЯ ІНШИМИ
# =====================================================================

class Resource(Compiler):
    # Resource — базовий клас для ресурсних файлів.
    # Підтримує будь-який файл що не належить до інших категорій.

    kind = "resource"
    extensions: Sequence[str] = ()

    def Supports(self, PathValue: Path) -> bool:
        # Ресурс підтримує будь-який існуючий файл.
        return PathValue.is_file()

    def Compile(self, PathValue: Path, Options: CompileOptions) -> CompilationResult:
        # Копіює файл та створює маніфест.
        if not PathValue.exists():
            return CompilationResult(self.kind, PathValue, success=False, error="source file not found")
        OutputDir = Path(Options.output_dir)
        OutputDir.mkdir(parents=True, exist_ok=True)
        Entry = OutputDir / PathValue.name if Options.copy_source else PathValue
        if Options.copy_source:
            Entry.write_bytes(PathValue.read_bytes())
        Digest = Compiler.HashFile(PathValue)
        ManifestPath = None
        if Options.write_manifest:
            ManifestPath = OutputDir / (PathValue.stem + ".resource.lcarc.json")
            Compiler.WriteManifest(ManifestPath, {
                "kind": self.kind,
                "source": str(PathValue),
                "entry": str(Entry),
                "hash": Digest,
            })
        return CompilationResult(self.kind, PathValue, Entry, ManifestPath, metadata={"hash": Digest})


# =====================================================================
# LCARS SCRIPT — КОМПІЛЯЦІЯ .lcars ФАЙЛІВ ЧЕРЕЗ LEXER → PARSER → AST
# =====================================================================

class Script(Compiler):
    # Script — компіляція .lcars файлів через повний конвейер:
    # Lexer → Tokenize → Parser → AST → PythonEmitter → Python файл.

    kind = "lcars"
    extensions = (".lcars",)

    def Compile(self, PathValue: Path, Options: CompileOptions) -> CompilationResult:
        # Повний конвейер компіляції .lcars файлу в Python.
        Source = Compiler.LoadSource(PathValue)
        if Source is None:
            return CompilationResult(self.kind, PathValue, success=False, error="source file not found")

        # Крок 1: Лексичний аналіз
        Lex = Lexer(Source)
        Tokens = Lex.tokenize()
        if Lex.Error is not None:
            return CompilationResult(self.kind, PathValue, success=False, error=str(Lex.Error))

        # Крок 2: Синтаксичний аналіз (побудова AST)
        Tree = Parser(Tokens)
        Ast = Tree.parse()
        if Tree.Errors:
            return CompilationResult(self.kind, PathValue, success=False, error="; ".join(str(Item) for Item in Tree.Errors))

        # Крок 3: Генерація Python коду з AST
        OutputDir = Path(Options.output_dir)
        OutputDir.mkdir(parents=True, exist_ok=True)
        Digest = Compiler.HashText(Source)
        OutputPath = OutputDir / (PathValue.stem + "_compiled.py")
        Emitter = PythonEmitter()
        Compiler.WriteOutput(OutputPath, Emitter.Compile(Ast))

        # Крок 4: Запис маніфесту
        ManifestPath = None
        if Options.write_manifest:
            ManifestPath = OutputDir / (PathValue.stem + ".lcarc.json")
            Compiler.WriteManifest(ManifestPath, {
                "kind": self.kind,
                "source": str(PathValue),
                "entry": str(OutputPath),
                "hash": Digest,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        return CompilationResult(self.kind, PathValue, OutputPath, ManifestPath, metadata={"hash": Digest})


# =====================================================================
# ГЕНЕРАТОР PYTHON — ПЕРЕТВОРЕННЯ AST У PYTHON КОД
# =====================================================================

class PythonEmitter:
    # PythonEmitter — генерує читабельний Python-артефакт з AST.
    # Не виконує код під час компіляції — виконання делегується LCARSRuntime.

    def __init__(self) -> None:
        self.lines: List[str] = []
        self.indent = 0

    def Emit(self, Line: str) -> None:
        # Додає рядок з урахуванням поточного відступу.
        self.lines.append("    " * self.indent + Line)

    def Compile(self, Ast: ASTNode) -> str:
        # Генерує Python код з AST дерева.
        self.lines = ["# Generated by LCARS compiler", "# Execution is delegated to LCARSRuntime."]
        self.indent = 0
        self.CompileNode(Ast)
        if len(self.lines) == 2:
            self.Emit("pass")
        return "\n".join(self.lines) + "\n"

    # Аліас для зворотної сумісності (старий код викликає .compile())
    compile = Compile

    def CompileNode(self, Node: ASTNode) -> None:
        # Компілює окремий вузол AST.
        if Node.type == NodeType.PROGRAM:
            for Child in Node.children:
                self.CompileStatement(Child)
            return
        self.CompileStatement(Node)

    def CompileStatement(self, Node: ASTNode) -> None:
        # Компілює оператор (присвоєння, if, while, def тощо).
        if Node.type in (NodeType.VARIABLE_DECLARATION, NodeType.ASSIGNMENT):
            Value = self.CompileExpression(Node.children[0]) if Node.children else "None"
            self.Emit(str(Node.value) + " = " + Value)
            return
        if Node.type == NodeType.EXPRESSION_STATEMENT:
            self.Emit(self.CompileExpression(Node.children[0]) if Node.children else "None")
            return
        if Node.type == NodeType.RETURN_STATEMENT:
            self.Emit("return " + (self.CompileExpression(Node.children[0]) if Node.children else "None"))
            return
        if Node.type == NodeType.BLOCK:
            for Child in Node.children:
                self.CompileStatement(Child)
            return
        if Node.type == NodeType.IF_STATEMENT:
            self.Emit("if " + self.CompileExpression(Node.children[0]) + ":")
            self.indent += 1
            self.CompileStatement(Node.children[1])
            self.indent -= 1
            if len(Node.children) > 2:
                self.Emit("else:")
                self.indent += 1
                self.CompileStatement(Node.children[2])
                self.indent -= 1
            return
        if Node.type == NodeType.WHILE_STATEMENT:
            self.Emit("while " + self.CompileExpression(Node.children[0]) + ":")
            self.indent += 1
            self.CompileStatement(Node.children[1])
            self.indent -= 1
            return
        if Node.type == NodeType.FOR_STATEMENT:
            IteratorName = Node.value.get("iterator", "i") if isinstance(Node.value, dict) else str(Node.value)
            Collection = self.CompileExpression(Node.children[0])
            self.Emit("for " + IteratorName + " in " + Collection + ":")
            self.indent += 1
            self.CompileStatement(Node.children[1])
            self.indent -= 1
            return
        if Node.type == NodeType.FOREACH_STATEMENT:
            IteratorName = Node.value.get("iterator", "item") if isinstance(Node.value, dict) else str(Node.value)
            Collection = self.CompileExpression(Node.children[0])
            self.Emit("for " + IteratorName + " in " + Collection + ":")
            self.indent += 1
            self.CompileStatement(Node.children[1])
            self.indent -= 1
            return
        if Node.type == NodeType.IMPORT_STATEMENT:
            ModuleName = str(Node.value)
            self.Emit("import " + ModuleName)
            return
        if Node.type == NodeType.EXPORT_STATEMENT:
            Value = self.CompileExpression(Node.children[0]) if Node.children else "None"
            self.Emit("export_result = " + Value)
            return
        if Node.type == NodeType.LOG_STATEMENT:
            Args = ", ".join(self.CompileExpression(Child) for Child in Node.children)
            self.Emit("print(" + Args + ")")
            return
        if Node.type == NodeType.EMIT_STATEMENT:
            Channel = self.CompileExpression(Node.children[0]) if len(Node.children) > 0 else '""'
            Data = self.CompileExpression(Node.children[1]) if len(Node.children) > 1 else "{}"
            self.Emit("emit_event(" + Channel + ", " + Data + ")")
            return
        if Node.type in (NodeType.FUNCTION_DECLARATION, NodeType.PROCEDURE_DECLARATION):
            Parameters = [Child.value for Child in Node.children if Child.type == NodeType.IDENTIFIER]
            Body = next((Child for Child in Node.children if Child.type == NodeType.BLOCK), ASTNode(NodeType.BLOCK))
            self.Emit("def " + str(Node.value) + "(" + ", ".join(Parameters) + "):")
            self.indent += 1
            self.CompileStatement(Body)
            self.indent -= 1
            return
        if Node.type in (
            NodeType.SIMULATION_DECLARATION, NodeType.DETECTOR_DECLARATION,
            NodeType.ANALYZER_DECLARATION, NodeType.VISUALIZE_DECLARATION,
            NodeType.PLUGIN_DECLARATION, NodeType.EVENT_HANDLER,
        ):
            for Child in Node.children:
                self.CompileStatement(Child)

    def CompileExpression(self, Node: ASTNode) -> str:
        # Компілює вираз (літерал, ідентифікатор, виклик, член тощо).
        if Node.type == NodeType.LITERAL:
            return repr(Node.value)
        if Node.type == NodeType.IDENTIFIER:
            return str(Node.value)
        if Node.type == NodeType.BINARY_EXPRESSION:
            Operator = "**" if Node.value == "^" else ("and" if str(Node.value).lower() == "and" else ("or" if str(Node.value).lower() == "or" else str(Node.value)))
            return "(" + self.CompileExpression(Node.children[0]) + " " + Operator + " " + self.CompileExpression(Node.children[1]) + ")"
        if Node.type == NodeType.UNARY_EXPRESSION:
            Operator = "not " if str(Node.value).lower() == "not" else str(Node.value)
            return "(" + Operator + self.CompileExpression(Node.children[0]) + ")"
        if Node.type == NodeType.CALL_EXPRESSION:
            return self.CompileExpression(Node.children[0]) + "(" + ", ".join(self.CompileExpression(Item) for Item in Node.children[1:]) + ")"
        if Node.type == NodeType.MEMBER_EXPRESSION:
            Left = self.CompileExpression(Node.children[0])
            Right = self.CompileExpression(Node.children[1])
            return Left + ("[" + Right + "]" if Node.value == "[]" else "." + Right)
        if Node.type == NodeType.ARRAY_LITERAL:
            return "[" + ", ".join(self.CompileExpression(Item) for Item in Node.children) + "]"
        if Node.type == NodeType.OBJECT_LITERAL:
            return "{" + ", ".join(repr(Item.value) + ": " + self.CompileExpression(Item.children[0]) for Item in Node.children) + "}"
        return "None"


# =====================================================================
# СХОВИЩЕ АРТЕФАКТІВ — ІЗОЛІНІЙНИЙ ІНДЕКС
# =====================================================================

class Store:
    # Store — сховище артефактів в ізолінійному кеші.
    # Не дублює мережевий канал — лише локальний JSON-індекс.

    def __init__(self, base_dir: Path = Path("lcars/data/iso-cache")):
        self.base_dir = Path(base_dir)
        self.index_path = self.base_dir / "index.json"

    def LoadIndex(self) -> List[Dict[str, str]]:
        # Завантажує поточний індекс артефактів.
        return Compiler.LoadIndex(self.index_path)

    def WriteIndex(self, Index: List[Dict[str, str]]) -> None:
        # Записує оновлений індекс артефактів.
        Compiler.WriteIndex(self.index_path, Index)

    def Record(self, Result: CompilationResult) -> str:
        # Записує артефакт в індекс та повертає його ID.
        if not Result.success:
            return ""
        Digest = Result.metadata.get("hash", "unknown")[:12]
        Stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        ArtifactId = Result.kind + "-" + Stamp + "-" + Digest
        Index = self.LoadIndex()
        Index.append({
            "id": ArtifactId,
            "kind": Result.kind,
            "source": str(Result.source_path),
            "output": str(Result.output_path) if Result.output_path else "",
            "manifest": str(Result.manifest_path) if Result.manifest_path else "",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "hash": Result.metadata.get("hash", ""),
        })
        self.WriteIndex(Index)
        return ArtifactId

    # Аліас для зворотної сумісності (старий код викликає .record())
    record = Record


# =====================================================================
# УНІВЕРСАЛЬНИЙ ФАСАД — ОБИРАЄ КЛАС ЗА РОШИРЕННЯМ
# =====================================================================

class Universal(Compiler):
    # Universal — фасад, який бачать Console, Onboard і агенти.
    # Обирає відповідний підклас Compiler за розширенням файлу.

    def __init__(self, options: Optional[CompileOptions] = None, store: Optional[Store] = None):
        self.options = options or CompileOptions()
        self.store = store or Store()
        self.board_computer = None
        self.compilers: List[Compiler] = [
            Script(),
            PythonScript(),
            Cmd(),
            PowerShell(),
            Bash(),
            Data(),
            Resource(),
        ]

    def FindCompiler(self, PathValue: Union[Path, str]) -> Optional[Compiler]:
        # Знаходить компілятор за розширенням файлу.
        Target = Path(PathValue)
        for Item in self.compilers:
            if Item.Supports(Target):
                return Item
        return None

    def CompilePath(self, PathValue: Union[Path, str]) -> CompilationResult:
        # Компілює файл: знаходить компілятор, виконує, записує в індекс.
        Target = Path(PathValue)
        CompilerInstance = self.FindCompiler(Target)
        if CompilerInstance is None:
            return CompilationResult("unknown", Target, success=False, error="no compiler registered")
        Result = CompilerInstance.Compile(Target, self.options)
        if Result.success and self.options.record_isolinear:
            Result.isolinear_id = self.store.Record(Result)
        if self.board_computer is not None and hasattr(self.board_computer, "PublishSignal"):
            self.board_computer.PublishSignal("Compiler.Completed", {
                "success": Result.success, "kind": Result.kind, "source": str(Result.source_path),
            })
        return Result

    # Аліаси для зворотної сумісності
    compile_path = CompilePath
    compilePath = CompilePath
    find_compiler = FindCompiler
    findCompiler = FindCompiler


# =====================================================================
# АЛІАСИ ДЛЯ ЗВОРОТНОЇ СУМІСНОСТІ
# =====================================================================

# Старі назви що використовуються в інших модулях
BaseCompiler = Compiler
LCARSCompiler = Script
CommandCompiler = Command
CmdCompiler = Cmd
PowerShellCompiler = PowerShell
BashCompiler = Bash
PythonScriptFileCompiler = PythonScript
DataFileCompiler = Data
ResourceFileCompiler = Resource
UniversalCompiler = Universal
PythonCompiler = PythonEmitter
IsolinearArtifactStore = Store
IsolinearCompiler = Universal


# =====================================================================
# ЕКСПОРТИ
# =====================================================================

__all__ = [
    "CompileError", "CompileOptions", "CompilationResult",
    "Compiler", "Command", "Cmd", "PowerShell", "Bash", "PythonScript",
    "Data", "Resource", "Script",
    "PythonEmitter", "Store", "Universal",
    "BaseCompiler", "LCARSCompiler", "CommandCompiler", "CmdCompiler",
    "PowerShellCompiler", "BashCompiler", "PythonScriptFileCompiler",
    "DataFileCompiler", "ResourceFileCompiler",
    "UniversalCompiler", "PythonCompiler", "IsolinearArtifactStore",
    "IsolinearCompiler",
]
