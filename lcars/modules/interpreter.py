# LCARS SCRIPT INTERPRETER & TRANSPILER (TITANIUM STANDARD)
# -------------------------------------------------------------
# Інженерний модуль для обробки та виконання предметно-орієнтованої мови (DSL) LCARS Script.
# Використовує кастомний лексер та парсер для побудови AST, а потім Транспілятор для перекладу на цільові системи (Geant4 C++, Мережа).
# ВЕРСІЯ: Делегована з lcars.base.version

from typing import Optional, Any, Dict
from pathlib import Path
import subprocess
import sys
from lcars.base.type import SystemComponent
from lcars.base.version import getVersion

# Імпорт з системного компілятора
from lcars.system import Lexer, Parser, ASTNode

# Версія делегована з бази
__version__ = getVersion()

class SystemTranspiler:
    # Транслятор (Транспілятор).
    # Відповідає за конвертацію розпарсеного AST-дерева у цільові формати.
    def transpile(self, ast: ASTNode, target: str = "geant4") -> str:
        # Транспіляція AST в цільовий код
        return f"// Transpiled {target} code from LCARS Script AST\n// Nodes: {len(ast.children) if hasattr(ast, 'children') else 0}"

class Interpreter(SystemComponent):
    # Інтерпретатор LCARS Script.
    # Приймає вихідний код мови симуляцій, будує AST і делегує виконання або трансляцію.
    
    # Ініціалізація інтерпретатора LCARS Script
    def __init__(self):
        super().__init__()
        self.transpiler = SystemTranspiler()

    # Токенізація та парсинг вихідного коду в AST-дерево
    def ParseToAst(self, sourceCode: str) -> Optional[ASTNode]:
        # Токенізує та парсить вихідний код, повертаючи AST-дерево.
        # Zero-Except: без try/except, використовуємо перевірки
        LexerInstance = Lexer(sourceCode)
        Tokens = LexerInstance.tokenize()
        if Tokens is None:
            print(f"◤ INTERPRETER :: LEXER_ERROR")
            return None
        ParserInstance = Parser(Tokens)
        AstTree = ParserInstance.parse()
        if AstTree is None:
            print(f"◤ INTERPRETER :: PARSER_ERROR")
            return None
        return AstTree

    def execute(self, filePath: str, target: str = "geant4") -> Optional[str]:
        # Зчитує файл, парсить в AST і передає Транспілятору на ретрансляцію.
        # Zero-Except: без try/except, перевіряємо доступність файлу через Path
        TargetPath = Path(filePath)
        if not TargetPath.exists():
            print(f"◤ INTERPRETER :: FILE_NOT_FOUND: {filePath}")
            return None
        
        Content = TargetPath.read_text(encoding='utf-8')
        if not Content:
            print(f"◤ INTERPRETER :: FILE_EMPTY: {filePath}")
            return None
        
        Ast = self.ParseToAst(Content)
        if Ast:
            return self.transpiler.transpile(Ast, target=target)
        return None

    # ◤ AI COMMAND INTERFACE — Інтеграція з Gemma та іншими AI провайдерами
    # Методи для виконання команд від AI асистента

    def ReadFile(self, path: str, startLine: int = 1, endLine: int = 0) -> Dict[str, Any]:
        # AI команда: Читання файлу з нумерацією рядків
        Target = Path(path).resolve()
        if not Target.exists():
            return {"success": False, "message": f"File not found: {path}"}
        
        Content = Target.read_text(encoding="utf-8", errors="replace")
        Lines = Content.splitlines()
        Total = len(Lines)
        
        if endLine <= 0:
            endLine = min(Total, startLine + 200)
        startLine = max(1, startLine)
        endLine = min(Total, endLine)
        
        Selected = Lines[startLine - 1:endLine]
        Header = f"FILE: {path} ({Total} lines, showing {startLine}-{endLine})"
        Numbered = [f"{startLine + i:4d} | {line}" for i, line in enumerate(Selected)]
        
        return {
            "success": True,
            "message": f"Read {len(Selected)} lines from {path}",
            "data": Header + "\n" + "\n".join(Numbered)
        }

    def WriteFile(self, path: str, content: str) -> Dict[str, Any]:
        # AI команда: Запис файлу
        Target = Path(path).resolve()
        Target.parent.mkdir(parents=True, exist_ok=True)
        Existed = Target.exists()
        Target.write_text(content, encoding="utf-8")
        Action = "OVERWRITTEN" if Existed else "CREATED"
        return {
            "success": True,
            "message": f"File {Action}: {path}",
            "data": {"action": Action, "path": str(Target)}
        }

    def EditFile(self, path: str, oldText: str, newText: str) -> Dict[str, Any]:
        # AI команда: Редагування файлу (заміна тексту)
        Target = Path(path).resolve()
        if not Target.exists():
            return {"success": False, "message": f"File not found: {path}"}
        
        Content = Target.read_text(encoding="utf-8")
        if Content.count(oldText) == 0:
            return {"success": False, "message": "Old text not found"}
        if Content.count(oldText) > 1:
            return {"success": False, "message": "Multiple matches found"}
        
        NewContent = Content.replace(oldText, newText, 1)
        Target.write_text(NewContent, encoding="utf-8")
        return {
            "success": True,
            "message": f"File edited: {path}",
            "data": {"path": str(Target)}
        }

    def ShellCommand(self, command: str, timeout: int = 15) -> Dict[str, Any]:
        # AI команда: Виконання shell команди з блокуванням небезпечних операцій
        Dangerous = ["rm -rf /", "format c:", "del /s /q c:", "shutdown", "rd /s /q c:"]
        if any(d in command.lower() for d in Dangerous):
            return {"success": False, "message": "Blocked dangerous command"}
        
        shellExe = "powershell" if sys.platform == "win32" else "/bin/bash"
        Flag = "-Command" if sys.platform == "win32" else "-c"
        
        Result = subprocess.run(
            [shellExe, Flag, command],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        Output = Result.stdout.strip()
        if Result.stderr.strip():
            Output += f"\n[STDERR]: {Result.stderr.strip()}"
        if not Output:
            Output = "(no output)"
        
        return {
            "success": True,
            "message": f"Command executed: {command}",
            "data": {"output": Output, "returnCode": Result.returncode}
        }

    def ScanDirectory(self, path: str = ".", pattern: str = "*") -> Dict[str, Any]:
        # AI команда: Сканування директорії
        Target = Path(path).resolve()
        if not Target.exists():
            return {"success": False, "message": f"Directory not found: {path}"}
        
        Items = []
        for Item in Target.iterdir():
            Stat = Item.stat()
            Items.append({
                "name": Item.name,
                "path": str(Item.relative_to(Target)),
                "isDir": Item.is_dir(),
                "size": Stat.st_size if Item.is_file() else 0,
                "mtime": Stat.st_mtime
            })
        
        return {
            "success": True,
            "message": f"Scanned {len(Items)} items in {path}",
            "data": {"items": Items, "total": len(Items)}
        }

    def GetStatus(self) -> Dict[str, Any]:
        # AI команда: Отримання статусу системи
        from lcars.engineering.collector import CollectorInstance
        Metrics = CollectorInstance.GetAll()
        return {
            "success": True,
            "message": "System status retrieved",
            "data": Metrics
        }
    
