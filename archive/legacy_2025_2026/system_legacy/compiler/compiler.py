# LCARS FRAMEWORK v1.0.0-ALPHA
# Універсальний Компілятор LCARS (LCARS Universal Compiler)
# ОПИС: Центральний модуль компіляції для LCARS Script (.lcars) та системних скриптів.
#        Перетворює декларативний синтаксис LCARS в виконуваний Python код через
#        повний стек: Лексер → Парсер (AST) → Компілятор → Рантайм.
# АРХІТЕКТУРА:
#   - BaseCompiler: Абстрактний базовий клас для всіх компіляторів
#   - LCARSScriptCompiler: Компілятор .lcars файлів через Lexer/Parser/AST
#   - ShellScriptCompiler: Обгортка для .cmd/.bat/.ps1/.sh скриптів
#   - PythonCompiler: Генерація Python коду з AST дерева
#   - IsolinearArtifactStore: Каталог артефактів (ізолінійний кеш)
#   - IsolinearCompiler: Головний координатор вибору компілятора
# ФУНКЦІЇ:
#   - compile_path: Визначення типу файлу та делегування відповідному компілятору
#   - LCARSScriptCompiler.compile: Токенізація → Парсинг → Компіляція AST
#   - IsolinearArtifactStore.record: Реєстрація артефакту в ізолінійному каталозі
# ЗАЛЕЖНОСТІ: lexer.py (Tokenizer), parser.py (AST), runtime.py (Execution Engine)
# ВЕРСІЯ: v1.0.0-ALPHA — повноцінний компілятор з підтримкою ізолінійних чіпів

from __future__ import annotations
import hashlib
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: import shutil
# Titanium Bridge Migration: from dataclasses import dataclass, field
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Dict, List, Optional
from .parser import NodeType, ASTNode

# Центральний "бортовий" комп'ютер LCARS.
class CompileError(Exception):
	pass
# Налаштування компіляції.
@dataclass
class CompileOptions:
	output_dir: Path = Path("scripts/compiled")
	write_manifest: bool = True
	write_wrapper: bool = True
	copy_source: bool = True
	record_isolinear: bool = True

# Результат компіляції одного файлу.
@dataclass
class CompilationResult:
	kind: str
	source_path: Path
	output_path: Optional[Path] = None
	manifest_path: Optional[Path] = None
	wrapper_path: Optional[Path] = None
	isolinear_id: Optional[str] = None
	metadata: Dict[str, str] = field(default_factory=dict)

# Каталізатор артефактів, що імітує "ізолінійний" запис.
class IsolinearArtifactStore:

	def __init__(self, base_dir: Path = Path("lcars/data/isolinear_cache")):
		self.base_dir = base_dir
		self.index_path = self.base_dir / "isolinear_index.json"

	def record(self, result: CompilationResult) -> str:
		self.base_dir.mkdir(parents=True, exist_ok=True)
		index = self._load_index()

		timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
		hash_value = result.metadata.get("hash", "unknown")
		artifact_id = f"{result.kind}-{timestamp}-{hash_value[:12]}"

		entry = {
			"id": artifact_id,
			"kind": result.kind,
			"source": str(result.source_path),
			"output": str(result.output_path) if result.output_path else None,
			"manifest": str(result.manifest_path) if result.manifest_path else None,
			"wrapper": str(result.wrapper_path) if result.wrapper_path else None,
			"created_at": datetime.utcnow().isoformat() + "Z",
			"hash": hash_value,
		}
		index.append(entry)
		self._write_index(index)
		return artifact_id

	def _load_index(self) -> List[Dict[str, str]]:
		return json.loads(self.index_path.read_text(encoding="utf-8"))

	def _write_index(self, index: List[Dict[str, str]]) -> None:
		self.index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

# Базовий компілятор для всіх компіляторів.
class BaseCompiler:
	kind: str = "base"
	extensions: List[str] = []

	def supports(self, path: Path) -> bool:
		return path.suffix.lower() in self.extensions

	def compile(self, path: Path, options: CompileOptions) -> CompilationResult:
		raise NotImplementedError

# 
class LCARSScriptCompiler(BaseCompiler):

	kind = "lcars"
	extensions = [".lcars"]

	def compile(self, path: Path, options: CompileOptions) -> CompilationResult:
		output_dir = Path(options.output_dir)
		output_dir.mkdir(parents=True, exist_ok=True)

		from .lexer import Lexer
		from .parser import Parser

		source = path.read_text(encoding="utf-8")
		lexer = Lexer(source)
		tokens = lexer.tokenize()
		parser = Parser(tokens)
		ast = parser.parse()

		python_code = PythonCompiler().compile(ast)

		output_path = output_dir / f"{path.stem}_compiled.py"
		output_path.write_text(python_code, encoding="utf-8")

		manifest_path = None
		if options.write_manifest:
			manifest_path = output_dir / f"{path.stem}.lcarc.json"
			manifest = {
				"kind": self.kind,
				"source": str(path),
				"entry": str(output_path),
				"created_at": datetime.utcnow().isoformat() + "Z",
				"hash": _hash_text(source),
			}
			manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

		return CompilationResult(
			kind=self.kind,
			source_path=path,
			output_path=output_path,
			manifest_path=manifest_path,
			metadata={"hash": _hash_text(source)},
		)

# Універсальний компілятор, який вибирає конкретний компілятор на основі розширення файлу.
class CommandCompiler(BaseCompiler):

	kind = "command"
	extensions: List[str] = []
	shell_command: List[str] = []

	def compile(self, path: Path, options: CompileOptions) -> CompilationResult:
		output_dir = Path(options.output_dir)
		output_dir.mkdir(parents=True, exist_ok=True)

		entry_path = path
		if options.copy_source:
			entry_path = output_dir / path.name
			shutil.copy2(path, entry_path)

		wrapper_path = None
		if options.write_wrapper:
			wrapper_path = output_dir / f"{path.stem}_{self.kind}_runner.py"
			wrapper_path.write_text(
				_build_wrapper(self.shell_command, entry_path),
				encoding="utf-8",
			)

		manifest_path = None
		if options.write_manifest:
			manifest_path = output_dir / f"{path.stem}.{self.kind}.lcarc.json"
			manifest = {
				"kind": self.kind,
				"source": str(path),
				"entry": str(entry_path),
				"command": self.shell_command + [str(entry_path)],
				"created_at": datetime.utcnow().isoformat() + "Z",
				"hash": _hash_file(path),
			}
			manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

		return CompilationResult(
			kind=self.kind,
			source_path=path,
			output_path=entry_path,
			manifest_path=manifest_path,
			wrapper_path=wrapper_path,
			metadata={"hash": _hash_file(path)},
		)

# Специфічні компілятори для різних типів скриптів.
class CmdCompiler(CommandCompiler):

	kind = "cmd"
	extensions = [".cmd", ".bat"]
	shell_command = ["cmd.exe", "/c"]

# Увага: для PowerShell потрібно переконатися, що ExecutionPolicy дозволяє запуск скриптів, інакше wrapper може не працювати. Можливо, знадобиться додаткове налаштування або інструкції для користувача.
class PowerShellCompiler(CommandCompiler):

	kind = "powershell"
	extensions = [".ps1"]
	shell_command = ["powershell", "-ExecutionPolicy", "Bypass", "-File"]

# Для Bash-скриптів (WSL або Git Bash) може знадобитися додаткове налаштування шляху до bash.exe на Windows, або використання стандартного /bin/bash на Unix-системах. Wrapper також може потребувати адаптації для різних середовищ.
class BashCompiler(CommandCompiler):

	kind = "bash"
	extensions = [".sh"]
	shell_command = ["bash"]

# Утиліти Фасад для компіляції різних типів скриптів
# IsolinearCompiler — ізолінійний компілятор (alias для UniversalCompiler для зворотної сумісності)
IsolinearCompiler = UniversalCompiler


class UniversalCompiler:
	# Універсальний компілятор LCARS — вибирає відповідний компілятор за розширенням файлу
	# та інтегрується з бортовим комп'ютером через Nexus шину
	def __init__(
		self,
		options: Optional[CompileOptions] = None,
		store: Optional[IsolinearArtifactStore] = None,
	):
		self.options = options or CompileOptions()
		self.store = store or IsolinearArtifactStore()
		# Бортовий комп'ютер отримуємо через Nexus/Registry singleton
		self.board_computer = None
		if True:
			from lcars.base.register import REGISTRY
			self.board_computer = REGISTRY.Get("System.BoardComputer") or REGISTRY.Get("BoardComputer")
		if False: # Removed except block
			pass
		self.compilers: List[BaseCompiler] = [
			LCARSScriptCompiler(),
			CmdCompiler(),
			PowerShellCompiler(),
			BashCompiler(),
		]

	def compile_path(self, path: Path) -> CompilationResult:
		compiler = self._find_compiler(path)
		result = compiler.compile(path, self.options)

		if self.options.record_isolinear:
			result.isolinear_id = self.store.record(result)

		# Передати керування/контроль бортовому комп'ютеру без файлових перевірок.
		if self.board_computer:
			payload = {
				"kind": result.kind,
				"source": str(result.source_path),
				"output": str(result.output_path) if result.output_path else None,
				"manifest": str(result.manifest_path) if result.manifest_path else None,
				"wrapper": str(result.wrapper_path) if result.wrapper_path else None,
				"isolinear_id": result.isolinear_id,
			}
			nexus = getattr(self.board_computer.kernel, "nexus", None)
			if nexus is not None and hasattr(nexus, "set"):
				nexus.set("compiler:last_result", payload)

		return result

	def _find_compiler(self, path: Path) -> BaseCompiler:
		for compiler in self.compilers:
			if compiler.supports(path):
				return compiler
		raise CompileError(f"No compiler registered for: {path.suffix}")

# Допоміжні функції Компілятор AST LCARS Script у Python код
class PythonCompiler:

	def __init__(self) -> None:
		self.lines: List[str] = []
		self.indent = 0

	def compile(self, ast: ASTNode) -> str:
		self.lines = ["# Generated by LCARS PythonCompiler"]
		self.indent = 0
		self._compile_node(ast)
		return "\n".join(self.lines) + "\n"

	def _emit(self, line: str) -> None:
		self.lines.append("    " * self.indent + line)

	def _compile_node(self, node: ASTNode) -> None:
		if node.type == NodeType.PROGRAM:
			for child in node.children:
				self._compile_statement(child)
			return
		self._compile_statement(node)

	def _compile_statement(self, node: ASTNode) -> None:
		t = node.type

		if t == NodeType.BLOCK:
			self._compile_block(node)
		elif t == NodeType.VARIABLE_DECLARATION:
			value = self._compile_expression(node.children[0])
			self._emit(f"{node.value} = {value}")
		elif t == NodeType.ASSIGNMENT:
			self._compile_assignment(node)
		elif t == NodeType.RETURN_STATEMENT:
			if node.children:
				self._emit(f"return {self._compile_expression(node.children[0])}")
			else:
				self._emit("return")
		elif t == NodeType.IF_STATEMENT:
			condition = self._compile_expression(node.children[0])
			self._emit(f"if {condition}:")
			self._compile_block(node.children[1])
			if len(node.children) > 2:
				self._emit("else:")
				self._compile_block(node.children[2])
		elif t == NodeType.FOR_STATEMENT:
			var_name = node.value
			start = self._compile_expression(node.children[0])
			end = self._compile_expression(node.children[1])
			self._emit(f"for {var_name} in range({start}, {end} + 1):")
			self._compile_block(node.children[2])
		elif t == NodeType.WHILE_STATEMENT:
			condition = self._compile_expression(node.children[0])
			self._emit(f"while {condition}:")
			self._compile_block(node.children[1])
		elif t == NodeType.FOREACH_STATEMENT:
			var_name = node.value
			collection = self._compile_expression(node.children[0])
			self._emit(f"for {var_name} in {collection}:")
			self._compile_block(node.children[1])
		elif t == NodeType.EXPRESSION_STATEMENT:
			self._emit(self._compile_expression(node.children[0]))
		elif t == NodeType.FUNCTION_DECLARATION:
			self._compile_function(node)
		elif t == NodeType.PROCEDURE_DECLARATION:
			self._compile_procedure(node)
		elif t == NodeType.SIMULATION_DECLARATION:
			self._compile_simulation(node)
		elif t == NodeType.DETECTOR_DECLARATION:
			self._compile_simple_class(node, "Detector", "register_detector")
		elif t == NodeType.ANALYZER_DECLARATION:
			self._compile_simple_class(node, "Analyzer", "register_analyzer")
		elif t == NodeType.VISUALIZE_DECLARATION:
			self._compile_named_function(node, prefix="visualize")
		elif t == NodeType.PLUGIN_DECLARATION:
			self._compile_named_function(node, prefix="plugin")
		else:
			self._emit(self._compile_expression(node))

	def _compile_block(self, block: ASTNode) -> None:
		self.indent += 1
		if not block.children:
			self._emit("pass")
		else:
			for stmt in block.children:
				self._compile_statement(stmt)
		self.indent -= 1

	def _compile_assignment(self, node: ASTNode) -> None:
		if node.value is not None and len(node.children) == 1:
			target = node.value
			value = self._compile_expression(node.children[0])
		else:
			target = self._compile_expression(node.children[0])
			value = self._compile_expression(node.children[1])
		self._emit(f"{target} = {value}")

	def _compile_function(self, node: ASTNode) -> None:
		name = node.value
		body = node.children[-1]
		params = node.children[:-1]
		if params and self._looks_like_return_type(params[-1]):
			params = params[:-1]
		param_names = [p.value for p in params]
		self._emit(f"def {name}({', '.join(param_names)}):")
		self._compile_block(body)
		self._emit(
			f"if 'lcars_runtime' in globals(): lcars_runtime.register_function({repr(name)}, {name})"
		)

	def _compile_procedure(self, node: ASTNode) -> None:
		name = node.value
		body = node.children[-1]
		params = node.children[:-1]
		param_names = [p.value for p in params]
		self._emit(f"def {name}({', '.join(param_names)}):")
		self._compile_block(body)
		self._emit(
			f"if 'lcars_runtime' in globals(): lcars_runtime.register_function({repr(name)}, {name})"
		)

	def _compile_named_function(self, node: ASTNode, prefix: str) -> None:
		func_name = f"{prefix}_{node.value}"
		body = node.children[-1] if node.children else ASTNode(NodeType.BLOCK)
		self._emit(f"def {func_name}():")
		self._compile_block(body)
		self._emit(
			f"if 'lcars_runtime' in globals(): lcars_runtime.register_function({repr(node.value)}, {func_name})"
		)

	def _compile_simulation(self, node: ASTNode) -> None:
		class_name = f"Simulation_{node.value}"
		self._emit(f"class {class_name}:")
		self.indent += 1

		init_nodes = [c for c in node.children if c.type != NodeType.EVENT_HANDLER]
		handlers = [c for c in node.children if c.type == NodeType.EVENT_HANDLER]

		self._emit("def __init__(self):")
		self.indent += 1
		self._emit("self.runtime = globals().get('lcars_runtime')")

		for stmt in init_nodes:
			if stmt.type == NodeType.ASSIGNMENT and stmt.value and len(stmt.children) == 1:
				value = self._compile_expression(stmt.children[0])
				self._emit(f"self.{stmt.value} = {value}")
			else:
				self._compile_statement(stmt)

		if not init_nodes:
			self._emit("pass")

		self.indent -= 1

		start_handler = None
		for handler in handlers:
			event_name = str(handler.value).lower()
			if event_name == "start":
				start_handler = handler
			else:
				self._compile_event_handler(handler)

		self._emit("def run(self):")
		self.indent += 1
		if start_handler:
			self._compile_block(start_handler.children[-1])
		else:
			self._emit("pass")
		self.indent -= 1

		self.indent -= 1
		self._emit(
			f"if 'lcars_runtime' in globals(): lcars_runtime.register_simulation({repr(node.value)}, {class_name})"
		)

	def _compile_event_handler(self, node: ASTNode) -> None:
		event_name = str(node.value).lower()
		params = node.children[:-1] if node.children else []
		body = node.children[-1] if node.children else ASTNode(NodeType.BLOCK)
		param_names = []
		for idx, param in enumerate(params):
			if param.type == NodeType.IDENTIFIER:
				param_names.append(param.value)
			else:
				param_names.append(f"param_{idx}")
		self._emit(f"def on_{event_name}(self, {', '.join(param_names)}):")
		self._compile_block(body)

	def _compile_simple_class(self, node: ASTNode, prefix: str, register_method: str) -> None:
		class_name = f"{prefix}_{node.value}"
		self._emit(f"class {class_name}:")
		self.indent += 1
		self._emit("def __init__(self):")
		self._compile_block(ASTNode(NodeType.BLOCK, children=node.children))
		self.indent -= 1
		self._emit(
			f"if 'lcars_runtime' in globals(): lcars_runtime.{register_method}({repr(node.value)}, {class_name})"
		)

	def _compile_expression(self, node: ASTNode) -> str:
		t = node.type
		if t == NodeType.LITERAL:
			return _format_literal(node.value)
		if t == NodeType.IDENTIFIER:
			return node.value
		if t == NodeType.BINARY_EXPRESSION:
			left = self._compile_expression(node.children[0])
			right = self._compile_expression(node.children[1])
			op = "**" if node.value == "^" else node.value
			return f"({left} {op} {right})"
		if t == NodeType.UNARY_EXPRESSION:
			operand = self._compile_expression(node.children[0])
			op = "not" if node.value == "not" else node.value
			return f"({op} {operand})" if op == "not" else f"({op}{operand})"
		if t == NodeType.CALL_EXPRESSION:
			callee = self._compile_expression(node.children[0])
			args = ", ".join(self._compile_expression(a) for a in node.children[1:])
			return f"{callee}({args})"
		if t == NodeType.MEMBER_EXPRESSION:
			target = self._compile_expression(node.children[0])
			if node.value == ".":
				member = self._compile_expression(node.children[1])
				return f"{target}.{member}"
			if node.value == "[]":
				index = self._compile_expression(node.children[1])
				return f"{target}[{index}]"
		if t == NodeType.ARRAY_LITERAL:
			elements = ", ".join(self._compile_expression(e) for e in node.children)
			return f"[{elements}]"
		if t == NodeType.OBJECT_LITERAL:
			props = []
			for prop in node.children:
				key = prop.value
				value = self._compile_expression(prop.children[0])
				props.append(f"{repr(key)}: {value}")
			return "{" + ", ".join(props) + "}"
		return "None"

	def _looks_like_return_type(self, node: ASTNode) -> bool:
		if node.type != NodeType.IDENTIFIER:
			return False
		return node.value in {
			"int",
			"float",
			"string",
			"bool",
			"number",
			"list",
			"dict",
			"void",
			"any",
		}

def _hash_file(path: Path) -> str:
	return _hash_text(path.read_text(encoding="utf-8"))


def _hash_text(text: str) -> str:
	return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _build_wrapper(shell_command: List[str], entry_path: Path) -> str:
	cmd_list = shell_command + [str(entry_path)]
	return "\n".join(
		[
			"import subprocess",
			"import sys",
			f"cmd = {repr(cmd_list)} + sys.argv[1:]",
			"sys.exit(subprocess.call(cmd))",
		]
	)

def _format_literal(value) -> str:
	if value is None:
		return "None"
	if isinstance(value, bool):
		return "True" if value else "False"
	if isinstance(value, str):
		if _looks_like_number(value):
			return value
		return repr(value)
	return repr(value)

def _looks_like_number(value: str) -> bool:
	text = value.strip()
	if not text:
		return False
	if text[0] in "+-":
		text = text[1:]
	if not text:
		return False
	parts = text.split(".")
	if len(parts) > 2:
		return False
	return all(part.isdigit() for part in parts)
