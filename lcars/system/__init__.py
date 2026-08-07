# LCARS SYSTEM PACKAGE FACADE
# Призначення: один стабільний імпортний контракт для бортового комп'ютера,
# сервісів і агентів. Реалізація залишається розділеною по модулях, але старий
# код більше не мусить знати внутрішню структуру system-пакета.

from .lexer import Lexer, LexerError, Token, TokenType
from .parser import ASTNode, NodeType, Parser, ParserError
from .compiler import (
    # Базовий клас та структури даних
    LCARS,
    CompileError,
    CompileOptions,
    CompilationResult,
    # Підкласи компіляції
    Compiler,
    Command,
    Cmd,
    PowerShell,
    Bash,
    PythonScript,
    Data,
    Resource,
    Script,
    # Генератор та сховище
    PythonEmitter,
    Store,
    # Універсальний фасад
    Universal,
    # Аліаси для зворотної сумісності
    BaseCompiler,
    LCARSCompiler,
    CommandCompiler,
    CmdCompiler,
    PowerShellCompiler,
    BashCompiler,
    PythonScriptFileCompiler,
    DataFileCompiler,
    ResourceFileCompiler,
    UniversalCompiler,
    PythonCompiler,
    IsolinearArtifactStore,
    IsolinearCompiler,
)
from .runtime import (
    ExecutionStats,
    LCARSRuntime,
    RuntimeError,
    RuntimeMode,
    RuntimeResult,
    SimulationResult,
    runtime,
)

__all__ = [
    # Лексер та парсер
    "Lexer", "LexerError", "Token", "TokenType",
    "ASTNode", "NodeType", "Parser", "ParserError",
    # Базовий клас LCARS
    "LCARS",
    # Структури даних
    "CompileError", "CompileOptions", "CompilationResult",
    # Підкласи компіляції
    "Compiler", "Command", "Cmd", "PowerShell", "Bash", "PythonScript",
    "Data", "Resource", "Script",
    # Генератор та сховище
    "PythonEmitter", "Store",
    # Універсальний фасад
    "Universal",
    # Аліаси для зворотної сумісності
    "BaseCompiler", "LCARSCompiler", "CommandCompiler", "CmdCompiler",
    "PowerShellCompiler", "BashCompiler", "PythonScriptFileCompiler",
    "DataFileCompiler", "ResourceFileCompiler",
    "UniversalCompiler", "PythonCompiler", "IsolinearArtifactStore",
    "IsolinearCompiler",
    # Runtime
    "ExecutionStats", "LCARSRuntime", "RuntimeError", "RuntimeMode",
    "RuntimeResult", "SimulationResult", "runtime",
]
