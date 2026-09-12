
# LCARS Development Agent — Копілот для розробки
# Цей файл містить логіку "Копілота" — інтелектуального агента, який живе всередині бортового комп'ютера.
# 
# В ЧОМУ РІЗНИЦЯ МІЖ КОМП'ЮТЕРОМ ТА АГЕНТОМ?
# 1. Бортовий комп'ютер (BoardComputer) — це сама система LCARS.
#    Він керує файлами, звуком, екранами та пам'яттю.
# 2. Агент (Copilot) — це "особистість" або "інтелект". 
#    Він не просто виконує команди, а може ДУМАТИ.
#    Наприклад: якщо ви скажете "виправ помилку", комп'ютер сам не зрозуміє, а Агент:
#    - Прочитає код (інструмент read_file)
#    - Знайде помилку (логіка AI)
#    - Виправить її (інструмент edit_file)
#    - Перевірить результат.

# Titanium Bridge Migration: import json
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import re
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: import traceback
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from typing import Any, Callable, Dict, List, Optional, Tuple
from lcars.base.type import LCARS, Directive
from lcars.system.board_computer import TitaniumBoardComputer
# Кількість спроб, які Агент може зробити для вирішення однієї задачі (щоб не зациклився).
MAX_AGENT_ITERATIONS = 12

# ──────────────────────────────────────────────────────
#  ОПИС ІНСТРУМЕНТІВ (Які "руки" має Агент)
# ──────────────────────────────────────────────────────
# Кожен інструмент тут — це функція, яку ШІ бачить і може викликати.

TOOL_DEFINITIONS = [
    {
        # read_file: Дозволяє Агенту читати ваші файли.
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file in the project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Шлях до файлу (відносно кореня)"},
                    "start_line": {"type": "integer", "description": "З якого рядка читати"},
                    "end_line": {"type": "integer", "description": "По який рядок читати"}
                },
                "required": ["path"]
            }
        }
    },
    {
        # write_file: Дозволяє Агенту створювати нові файли або перезаписувати старі.
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create a new file or completely overwrite an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Шлях до нового файлу"},
                    "content": {"type": "string", "description": "Весь текст, який треба записати"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        # edit_file: Найважливіший інструмент — Агент може міняти шматки коду.
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace a specific text fragment in an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Файл для редагування"},
                    "old_text": {"type": "string", "description": "Текст, який треба знайти (ТОЧНО)"},
                    "new_text": {"type": "string", "description": "Новий текст, на який замінити"}
                },
                "required": ["path", "old_text", "new_text"]
            }
        }
    },
    {
        # list_directory: Агент дивиться, які папки та файли є в проєкті.
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and folders in a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Папка (наприклад, '.', 'lcars/core')"},
                    "recursive": {"type": "boolean", "description": "Чи шукати вкладені папки"}
                },
                "required": ["path"]
            }
        }
    },
    {
        # execute_command: Команди в терміналі (PowerShell). Запустити тест, білд тощо.
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a shell command (PowerShell).",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Команда для виконання"},
                    "timeout": {"type": "integer", "description": "Скільки чекати секунд"}
                },
                "required": ["command"]
            }
        }
    },
    {
        # get_project_info: Швидкий звіт про структуру всього проєкту.
        "type": "function",
        "function": {
            "name": "get_project_info",
            "description": "Get summary of project structure.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        # ui_builder: Агент може сам намалювати і відкрити вам панель LCARS.
        "type": "function",
        "function": {
            "name": "ui_builder",
            "description": "Spawn a floating LCARS UI panel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Заголовок панелі"},
                    "components": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "enum": ["button", "label", "stat", "data"]},
                                "label": {"type": "string"},
                                "value": {"type": "string"},
                                "color": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["title", "components"]
            }
        }
    },
    {
        # search_text: Пошук тексту або regex по всіх файлах проєкту.
        "type": "function",
        "function": {
            "name": "search_text",
            "description": "Search for a text pattern across project files. Returns matching lines with file paths.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Text or regex pattern to search for"},
                    "file_pattern": {"type": "string", "description": "Glob pattern to filter files, e.g. '*.py'. Default '*.py'"}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        # open_browser: Відкриття внутрішнього браузера LCARS.
        "type": "function",
        "function": {
            "name": "open_browser",
            "description": "Open the internal LCARS browser to a given URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to open"}
                },
                "required": ["url"]
            }
        }
    },
    {
        # network_request: HTTP GET запит.
        "type": "function",
        "function": {
            "name": "network_request",
            "description": "Perform HTTP GET and return response text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"}
                },
                "required": ["url"]
            }
        }
    },
    {
        # nova_list_devices: Список пристроїв Nova Act.
        "type": "function",
        "function": {
            "name": "nova_list_devices",
            "description": "List available actuators and devices managed by the Nova Act SDK.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        # nova_get_telemetry: Телеметрія Nova Act.
        "type": "function",
        "function": {
            "name": "nova_get_telemetry",
            "description": "Retrieve the latest telemetry from the Nova Act adapter.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        # nova_execute_action: Виконати дію на пристрої Nova Act.
        "type": "function",
        "function": {
            "name": "nova_execute_action",
            "description": "Execute a specific action on a Nova Act device.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "The name of the action to perform"},
                    "params": {"type": "object", "description": "Optional parameters for the action"}
                },
                "required": ["action"]
            }
        }
    },
]
# Ці рядки пояснюють ШІ його роль та правила поведінки.

COPILOT_SYSTEM_PROMPT = (
    "You are the LCARS Copilot — an AI coding assistant embedded in the LCARS Board Computer.\n"
    "YOU ARE A BUILDER. You write, read, and modify code. You execute commands. You create real things.\n\n"
    "RULES:\n"
    "1. ALWAYS use tools to accomplish tasks. Do NOT just describe what to do — DO it.\n"
    "2. Read files before modifying them to understand context.\n"
    "3. When editing files, use edit_file with exact matching text.\n"
    "4. When creating new files, use write_file.\n"
    "5. After making changes, verify with read_file or execute_command.\n"
    "6. Respond in Ukrainian by default. Switch to English if user writes in English.\n"
    "7. Be concise. Use prefix for status lines.\n"
    "8. If you need to understand the project, call get_project_info first.\n"
    "9. Maximum focus: do what the user asks, nothing more.\n"
    "10. When done, summarize what you did in a brief report.\n\n"
    "PROJECT CONTEXT:\n"
    "- Framework: LCARS (Library Computer Access/Retrieval System)\n"
    "- Language: Python 3.11, PyQt6\n"
    "- Architecture: Event-driven, plugin system, modular core\n"
    "- Root: The project root is the working directory for all file paths\n"
    "- Key dirs: lcars/core/, lcars/ui/, lcars/modules/, plugins/, config/"
)

# ──────────────────────────────────────────────────────
#  TOOL EXECUTOR (Виконавець інструментів)
# ──────────────────────────────────────────────────────
# Цей клас — це "руки" Агента. Коли ШІ каже "хочу прочитати файл", цей клас іде на диск і читає його.

class ToolExecutor:
    # Клас, що виконує дії на файловій системі комп'ютера.

    def __init__(self, project_root: Any, allow_host_access: bool = False, host_whitelist: Optional[List[str]] = None):
        # Вказуємо корінь проєкту, щоб Агент не міг вийти за межі папки (для безпеки).
        self.project_root = Directive.PathDrive(project_root).resolve()
        self._changes_log: List[str] = [] # Журнал змін (що ми змінили)
        self.allow_host_access = bool(allow_host_access)
        self.host_whitelist = [Directive.PathDrive(p).resolve() for p in (host_whitelist or [])]

    @property
    def changes(self) -> List[str]:
        # Повертає список всіх змін, зроблених за час роботи.
        return self._changes_log

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        # Головний вхід: отримує назву інструмента та аргументи від ШІ.
        method = getattr(self, f"_tool_{tool_name}", None)
        if not method:
            return f"ERROR: Unknown tool '{tool_name}'"
        # Викликаємо відповідний метод (наприклад _tool_read_file)
        result = method(**arguments)
        return result

    def _resolve_path(self, path: str) -> Any:
        # Перетворює назву файлу (напр. 'main.py') на повний шлях на вашому диску.
        p = Directive.PathDrive(path)
        if p.is_absolute():
            resolved = p.resolve()
        else:
            resolved = (self.project_root / p).resolve()
        
        # Перевірка: чи не намагається Агент "зламати" систему, вийшовши з папки проєкту.
        if not self.allow_host_access:
            resolved.relative_to(self.project_root)
        return resolved

    def _tool_read_file(self, path: str, start_line: int = 1, end_line: int = 0) -> str:
        # Читання файлу. Ми додаємо номери рядків (1 | ...), щоб ШІ міг орієнтуватися.
        target = self._resolve_path(path)
        if not target.exists(): return f"FILE NOT FOUND: {path}"
        
        content = target.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        total = len(lines)

        # Обмеження на 200 рядків за раз, щоб ШІ не "перевантажився".
        if end_line <= 0: end_line = min(total, start_line + 200)
        start_line = max(1, start_line)
        end_line = min(total, end_line)

        selected = lines[start_line - 1:end_line]
        header = f"FILE: {path} ({total} lines, showing {start_line}-{end_line})"
        numbered = [f"{start_line + i:4d} | {line}" for i, line in enumerate(selected)]
        return header + "\n" + "\n".join(numbered)

    def _tool_write_file(self, path: str, content: str) -> str:
        # Створення або повний перезапис файлу.
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        existed = target.exists()
        target.write_text(content, encoding="utf-8")
        action = "OVERWRITTEN" if existed else "CREATED"
        self._changes_log.append(f"{action}: {path}")
        return f"◤ FILE {action}: {path}"

    def _tool_edit_file(self, path: str, old_text: str, new_text: str) -> str:
        # Розумна заміна шматка коду. ШІ має дати ТОЧНИЙ старий текст.
        target = self._resolve_path(path)
        if not target.exists(): return f"FILE NOT FOUND: {path}"

        content = target.read_text(encoding="utf-8")
        if content.count(old_text) == 0:
            return "ERROR: Old text not found exactly. Check indentation."
        if content.count(old_text) > 1:
            return "ERROR: Multiple identical text blocks found. Provide more context."

        new_content = content.replace(old_text, new_text, 1)
        target.write_text(new_content, encoding="utf-8")
        self._changes_log.append(f"EDITED: {path}")
        return f"◤ FILE EDITED: {path}"

    def _tool_list_directory(self, path: str = ".", recursive: bool = False) -> str:
        # Список файлів з розмірами. Ігноруємо службові папки.
        target = self._resolve_path(path)
        if not target.exists(): return f"DIRECTORY NOT FOUND: {path}"
        if not target.is_dir(): return f"NOT A DIRECTORY: {path}"
        
        lines = [f"DIRECTORY: {path}/"]
        if not os.access(target, os.R_OK | os.X_OK):
            lines.append("  ACCESS DENIED")
            return "\n".join(lines)

        skip = {"__pycache__", ".git", ".venv", "node_modules"}
        if recursive:
            for item in sorted(target.rglob("*")):
                rel = item.relative_to(target)
                if len(rel.parts) > 3: continue
                if any(s in rel.parts for s in skip): continue
                if not os.access(item, os.R_OK): continue
                prefix = "📁 " if item.is_dir() else "📄 "
                lines.append(f"  {prefix}{rel}")
                if len(lines) > 100:
                    lines.append("  ... (truncated at 100 entries)")
                    break
        else:
            entries = sorted(target.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                if entry.name.startswith(".") or entry.name in skip: continue
                if not os.access(entry, os.R_OK): continue
                if entry.is_dir():
                    lines.append(f"  📁 {entry.name}/")
                else:
                    size = entry.stat().st_size
                    sz = f"{size / 1024:.1f}KB" if size > 1024 else f"{size}B"
                    lines.append(f"  📄 {entry.name}  ({sz})")
        
        return "\n".join(lines[:100])

    def _tool_execute_command(self, command: str, timeout: int = 15) -> str:
        # Виконання команди в shell. Блокуємо небезпечні команди. Детектимо платформу.
        dangerous = ["rm -rf /", "format c:", "del /s /q c:", "shutdown"]
        if any(d in command.lower() for d in dangerous):
            return "BLOCKED: Potentially destructive command"

        shell_exe = "powershell" if os.name == "nt" else "/bin/bash"
        flag = "-Command" if os.name == "nt" else "-c"
        result = subprocess.run(
            [shell_exe, flag, command],
            capture_output=True, text=True, timeout=timeout, cwd=str(self.project_root)
        )
        output = result.stdout.strip()
        if result.stderr.strip():
            output += f"\n[STDERR]: {result.stderr.strip()}"
        if not output:
            output = "(no output)"
        if len(output) > 3000:
            output = output[:3000] + "\n... (truncated)"
        return f"COMMAND: {command}\n{output}"

    def _tool_get_project_info(self) -> str:
        # Детальний звіт про структуру проєкту з підрахунком .py файлів.
        lines = ["PROJECT: LCARS FRAMEWORK", f"ROOT: {self.project_root}", "", "KEY DIRECTORIES:"]
        key_dirs = ["lcars/core", "lcars/ui", "lcars/modules", "lcars/system",
                     "lcars/themes", "lcars/engineering", "plugins", "config",
                     "programs", "tools", "scripts"]
        for d in key_dirs:
            dp = self.project_root / d
            if dp.exists():
                py_count = len(list(dp.glob("*.py")))
                lines.append(f"  📁 {d}/ ({py_count} .py files)")

        lines.append("")
        lines.append("KEY FILES:")
        key_files = [
            "lcars/core/board_computer.py", "lcars/core/kernel.py",
            "lcars/core/copilot.py", "lcars/core/ai_provider.py",
            "lcars/core/computer_memory.py", "lcars/ui/onboard.py",
            "lcars/system/console.py", "config/config.json", "pyproject.toml",
        ]
        for f in key_files:
            fp = self.project_root / f
            if fp.exists():
                size = fp.stat().st_size
                lines.append(f"  📄 {f} ({size / 1024:.1f}KB)")

        lines.append("")
        lines.append("ARCHITECTURE:")
        lines.append("  BoardComputer (singleton) -> Kernel, EventBus, Store")
        lines.append("  BoardComputer -> ConfigManager, SoundManager, AlertSystem")
        lines.append("  BoardComputer -> ComputerMemory (SQLite), AIProviderManager")
        lines.append("  BoardComputer -> Copilot (this agent)")
        return "\n".join(lines)

    def _tool_ui_builder(self, title: str, components: List[Dict[str, Any]]) -> str:
        # Цей інструмент надсилає сигнал Бортовому Комп'ютеру створити нове вікно PADD.
        from lcars.system.board_computer import TitaniumBoardComputer
        from lcars.core.nexus import Event, EventType
        bc = TitaniumBoardComputer()
        if hasattr(bc, 'event_bus') and bc.event_bus:
            data = {"action": "spawn_padd", "title": title, "components": components}
            bc.event_bus.emit(Event(EventType.APP_CONFIG_CHANGED, 'workspace', data))
            return f"◤ UI PANEL '{title}' CREATED"
        return "ERROR: System bus unavailable."

    def _tool_search_text(self, pattern: str, file_pattern: str = "*.py") -> str:
        # Пошук тексту/regex по файлах проєкту. Повертає до 50 збігів.
        results = []
        compiled = re.compile(pattern, re.IGNORECASE) if self._is_valid_regex(pattern) else re.compile(re.escape(pattern), re.IGNORECASE)
        skip_dirs = {"__pycache__", ".git", ".venv", "node_modules", "archive"}

        for fpath in self.project_root.rglob(file_pattern):
            if any(skip in fpath.parts for skip in skip_dirs): continue
            if not fpath.is_file() or not os.access(fpath, os.R_OK): continue
            text = fpath.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(text.splitlines(), 1):
                if compiled.search(line):
                    rel = fpath.relative_to(self.project_root)
                    results.append(f"  {rel}:{i}  {line.strip()[:120]}")
                    if len(results) >= 50: break
            if len(results) >= 50: break

        if not results:
            return f"NO MATCHES for: '{pattern}' in {file_pattern}"
        return f"SEARCH: '{pattern}' — {len(results)} matches\n" + "\n".join(results)

    @staticmethod
    def _is_valid_regex(pattern: str) -> bool:
        # Перевірка чи рядок є валідним regex (без try/except — compile + match test).
        import sre_parse
        result = True
        # sre_parse.parse raises error for invalid patterns
        # Використовуємо re.compile з перехопленням через bool
        test = re.compile(pattern, re.IGNORECASE) if pattern else None
        return test is not None

    def _tool_open_browser(self, url: str) -> str:
        # Відкриття внутрішнього браузера через event bus BoardComputer.
        from lcars.system.board_computer import get_computer
        from lcars.core.kernel import Event, EventType
        bc = get_computer()
        event_bus = getattr(bc, 'event_bus', None)
        if event_bus is not None:
            event_bus.emit(Event(EventType.UI_COMPONENT_UPDATED, 'network_manager', {"action": "open_browser", "url": url}))
            return f"◤ BROWSER OPENED: {url}"
        return f"◤ BROWSER: {url} (UI offline)"

    def _tool_network_request(self, url: str) -> str:
        # HTTP GET — спочатку через NetworkManager, інакше requests.
        from lcars.system.board_computer import get_computer
        bc = get_computer()
        nm = getattr(bc, 'network_manager', None)
        if nm:
            return nm.perform_request(url)

        # Titanium Bridge Migration: import requests as http_lib
        resp = http_lib.get(url, timeout=10)
        text = resp.text
        if len(text) > 4000:
            text = text[:4000] + "\n... (truncated)"
        return f"◤ HTTP {resp.status_code}: {url}\n{text}"

    def _tool_nova_list_devices(self) -> str:
        # Список пристроїв Nova Act SDK.
        from lcars.plugins_impl.nova_act import get_adapter
        adapter = get_adapter()
        if not adapter:
            return "◤ ERROR: Nova Act plugin not loaded."
        devices = adapter.list_devices()
        return f"◤ NOVA ACT DEVICES:\n{json.dumps(devices, indent=2)}"

    def _tool_nova_get_telemetry(self) -> str:
        # Телеметрія з Nova Act.
        from lcars.plugins_impl.nova_act import get_adapter
        adapter = get_adapter()
        if not adapter:
            return "◤ ERROR: Nova Act plugin not loaded."
        tel = adapter.get_latest_telemetry()
        return f"◤ NOVA ACT TELEMETRY:\n{json.dumps(tel, indent=2)}"

    def _tool_nova_execute_action(self, action: str, params: Optional[dict] = None) -> str:
        # Виконання дії на пристрої Nova Act.
        from lcars.plugins_impl.nova_act import get_adapter
        adapter = get_adapter()
        if not adapter:
            return "◤ ERROR: Nova Act plugin not loaded."
        res = adapter.execute_action(action, params)
        return f"◤ NOVA ACTION '{action}':\n{json.dumps(res, indent=2)}"

# ──────────────────────────────────────────────────────
#  CLASS COPILOT (Agent Head)
# ──────────────────────────────────────────────────────
# Цей клас керує зв'язком з ШІ (напр. через Groq API) та обробляє цикл його "думок".

class Copilot:
    # Головний Агент розробки.

    def __init__(self, project_root: Any, ai_client=None, model: str = "qwen/qwen3-32b"):
        self.project_root = project_root
        self.tools = ToolExecutor(project_root)
        self.system_prompt = COPILOT_SYSTEM_PROMPT
        self._progress_callback: Optional[Callable[[str], None]] = None
        self.ShellEnabled: bool = False

    def _get_ai(self):
        # Отримання централізованого провайдера ШІ
        from lcars.system.board_computer import TitaniumBoardComputer
        return TitaniumBoardComputer().ai

    def set_progress_callback(self, callback: Callable[[str], None]):
        self._progress_callback = callback

    def _emit_progress(self, message: str):
        if callable(self._progress_callback): self._progress_callback(message)

    def _sanitize_output(self, text: str) -> str:
        # Ensure returned strings are safe to print in environments with limited encodings (e.g. CP1251).
        if not isinstance(text, str):
            text = str(text)
        return text.encode('ascii', errors='replace').decode('ascii')

    @staticmethod
    def _parse_simple_json_object(obj_text: str) -> Dict[str, str]:
        # Базовий парсер, що читає лише рядкові ключі та рядкові значення.
        out: Dict[str, str] = {}
        for m in re.finditer(r'"([^"\\]+)"\s*:\s*"([^"\\]*)"', obj_text):
            out[m.group(1)] = m.group(2)
        return out

    def _extract_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        # Парсинг простого синтаксису [TOOL_CALL] {"name": "read_file", "arguments": {...}}
        # Без використання try/except, щоб уникати неявних винятків.
        tool_calls: List[Dict[str, Any]] = []

        for match in re.finditer(r"\[TOOL_CALL\]\s*(\{.*?\})", text, re.DOTALL):
            payload = match.group(1)

            name_match = re.search(r'"name"\s*:\s*"([^"\\]+)"', payload)
            if not name_match:
                continue
            name = name_match.group(1)

            args: Dict[str, str] = {}
            args_match = re.search(r'"arguments"\s*:\s*(\{.*\})', payload, re.DOTALL)
            if args_match:
                args_text = args_match.group(1)
                args = Copilot._parse_simple_json_object(args_text)

            tool_calls.append({"name": name, "arguments": args})

        return tool_calls

    def run(self, user_request: str, context: str = "") -> str:
        # ЦЕЙ МЕТОД — СЕРЦЕ АГЕНТА. 
        ai = self._get_ai()
        # Ensure AI backend is initialized (may be lazy/async elsewhere)
        if not getattr(ai, '_initialized', False):
            ai.initialize()

        # Allow fallback backend to operate (so Copilot can still respond in limited mode).
        if not ai.is_ai_available and ai.active_backend_name != "fallback":
            return self._sanitize_output("◤ ERROR: AI Engine offline. Agent cannot think.")

        messages = [{"role": "system", "content": self.system_prompt}]
        if context:
            messages.append({"role": "system", "content": f"Context:\n{context}"})
        messages.append({"role": "user", "content": user_request})

        self._emit_progress("◤ AGENT: Analyzing request...")

        for iteration in range(MAX_AGENT_ITERATIONS):
            # Використовуємо уніфікований метод chat через провайдера
            response = ai.chat(messages, tools=TOOL_DEFINITIONS)

            # Fallback backend does not implement chat; use ask() instead.
            if response is None:
                return self._sanitize_output(ai.ask(user_request, context))

            msg = response.choices[0].message
            content = msg.content or ""
            tool_calls = getattr(msg, "tool_calls", None) or []

            messages.append(msg)  # Додаємо об'єкт повідомлення безпосередньо

            # 2. Якщо ШІ просто відповів (без інструментів) — значить він закінчив.
            if not tool_calls:
                # Try to parse tool calls from text (fallback mode / simple tool syntax)
                parsed = self._extract_tool_calls(content)
                if not parsed:
                    return self._sanitize_output(content)

                tool_results = []
                for tc in parsed:
                    func_name = tc.get("name")
                    if not isinstance(func_name, str):
                        continue
                    func_args = tc.get("arguments", {}) or {}
                    self._emit_progress(f"◤ EXECUTING (parsed): {func_name}")
                    result = self.tools.execute(func_name, func_args)

                    tool_results.append(f"[{func_name}] {result}")

                combined = content + "\n\n" + "\n".join(tool_results)
                return self._sanitize_output(combined)

            # 3. Якщо ШІ хоче використати інструменти — виконуємо їх один за одним.
            for tc in tool_calls:
                func_name = getattr(tc.function, "name", None)
                if not isinstance(func_name, str):
                    continue

                func_args: Dict[str, str] = {}
                if hasattr(tc.function, "arguments") and isinstance(tc.function.arguments, str):
                    func_args = Copilot._parse_simple_json_object(tc.function.arguments) # type: ignore

                self._emit_progress(f"◤ EXECUTING: {func_name}")
                
                # Реальне виконання інструмента через ToolExecutor
                result = self.tools.execute(func_name, func_args)
                
                # Передаємо результат назад ШІ, щоб він побачив, що сталось.
                messages.append({
                    "role": "tool",
                    "tool_call_id": getattr(tc, 'id', None), # type: ignore
                    "name": func_name,
                    "content": str(result)
                })

        return self._sanitize_output("◤ AGENT: I've made too many attempts and stopped for safety.")
