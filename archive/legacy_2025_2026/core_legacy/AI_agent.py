
# LCARS Development Agent — AI Coding Assistant
# Агент розробки вбудований в бортовий комп'ютер.
# Має доступ до файлової системи, shell, аналізу коду.
# Використовує Ollama (tool-calling) для прийняття рішень.
# Потік роботи: Користувач → Запит → LLM → [Tool Call] → Результат → LLM → Відповідь
#                                   ↑_____↓  (цикл до завершення)
# Titanium Bridge Migration: import json
import logging
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import re
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: import traceback
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Any, Callable, Dict, List, Optional, Tuple

MAX_AGENT_ITERATIONS = 12
logger = logging.getLogger("lcars.Copilot")
# ──────────────────────────────────────────────────────
#  TOOL DEFINITIONS (for Ollama tool-calling)
# ──────────────────────────────────────────────────────
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file in the project. Returns file text. Use for understanding existing code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to project root (e.g. 'lcars/core/kernel.py')"
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Start line number (1-based). Optional, defaults to 1."
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "End line number (1-based). Optional, defaults to end of file."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create a new file or completely overwrite an existing file. Use for creating new modules.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to project root"
                    },
                    "content": {
                        "type": "string",
                        "description": "Complete file content to write"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace a specific text fragment in an existing file. Use for modifying code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to project root"
                    },
                    "old_text": {
                        "type": "string",
                        "description": "Exact text to find and replace (must match exactly)"
                    },
                    "new_text": {
                        "type": "string",
                        "description": "New text to replace old_text with"
                    }
                },
                "required": ["path", "old_text", "new_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and folders in a directory. Use to explore project structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path relative to project root. Use '.' for root."
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If true, list recursively (max 3 levels deep). Default false."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_text",
            "description": "Search for a text pattern across project files. Returns matching lines with file paths.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Text or regex pattern to search for"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Glob pattern to filter files, e.g. '*.py'. Default '*.py'"
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a shell command (PowerShell on Windows). Use for running scripts, tests, pip install etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds. Default 15."
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_info",
            "description": "Get summary of project structure, key files and architecture. Use at the start to understand the codebase.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_browser",
            "description": "Open the internal LCARS browser to a given URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type":"string"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "network_request",
            "description": "Perform HTTP GET and return response text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type":"string"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "nova_list_devices",
            "description": "List available actuators and devices managed by the Nova Act SDK.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "nova_get_telemetry",
            "description": "Retrieve the latest telemetry (voltage, temperature, rx_packets) from the Nova Act adapter.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "nova_execute_action",
            "description": "Execute a specific action on a Nova Act device (e.g., 'move', 'toggle', 'calibrate').",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "The name of the action to perform."
                    },
                    "params": {
                        "type": "object",
                        "description": "Optional parameters for the action."
                    }
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ui_builder",
            "description": "Spawn a floating LCARS UI panel with specific components. Use to create diagnostic, control, or status widgets for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the floating panel (e.g. '◤ TRANSDUCER CONTROL')"
                    },
                    "components": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "enum": ["button", "label", "stat", "data"]},
                                "label": {"type": "string"},
                                "value": {"type": "string"},
                                "color": {"type": "string", "description": "CSS color or hex"}
                            }
                        }
                    }
                },
                "required": ["title", "components"]
            }
        }
    },
]

# ──────────────────────────────────────────────────────
#  SYSTEM PROMPT
# ──────────────────────────────────────────────────────

COPILOT_SYSTEM_PROMPT = """You are the LCARS Copilot — an AI coding assistant embedded in the LCARS Board Computer.

YOU ARE A BUILDER. You write, read, and modify code. You execute commands. You create real things.

RULES:
1. ALWAYS use tools to accomplish tasks. Do NOT just describe what to do — DO it.
2. Read files before modifying them to understand context.
3. When editing files, use edit_file with exact matching text.
4. When creating new files, use write_file.
5. After making changes, verify with read_file or execute_command.
6. Respond in Ukrainian by default. Switch to English if user writes in English.
7. Be concise. Use ◤ prefix for status lines.
8. If you need to understand the project, call get_project_info first.
9. Maximum focus: do what the user asks, nothing more.
10. When done, summarize what you did in a brief report.

PROJECT CONTEXT:
- Framework: LCARS (Library Computer Access/Retrieval System)
- Language: Python 3.11, PyQt6
- Architecture: Event-driven, plugin system, modular core
- Root: The project root is the working directory for all file paths
- Key dirs: lcars/core/, lcars/ui/, lcars/modules/, plugins/, config/
"""

# ──────────────────────────────────────────────────────
#  TOOL EXECUTOR
# ──────────────────────────────────────────────────────
# УКР: Цей клас виконує інструменти, які викликає агент. Він має доступ до файлової системи проєкту, може виконувати shell-команди та інші дії. Всі інструменти повинні бути викликані через метод `execute`, який є єдиним публічним інтерфейсом для виконання дій агента.
class ToolExecutor:
    """Executes agent tools against the real filesystem."""

    def __init__(self, project_root: Path, allow_host_access: bool = False, host_whitelist: Optional[List[str]] = None):
        """Initialize ToolExecutor.

        allow_host_access: opt‑in flag — when True the executor will allow
        resolving absolute paths outside project_root (use with caution).
        host_whitelist: optional list of absolute paths that are always allowed.
        """
        self.project_root = Path(project_root).resolve()
        self._changes_log: List[str] = []
        self.allow_host_access = bool(allow_host_access)
        # Normalize whitelist to resolved Paths
        self.host_whitelist = [Path(p).resolve() for p in (host_whitelist or [])]
    # У цьому журналі зберігаються всі зміни, які агент зробив через write_file або edit_file, щоб потім можна було підсумувати їх у звіті.
    @property
    def changes(self) -> List[str]:
        return self._changes_log
    # Метод `execute` приймає назву інструменту та аргументи, знаходить відповідний метод і виконує його. Якщо інструмент невідомий або виникає помилка, повертається повідомлення про помилку.
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a named tool and return result as string.

        УКР: Викликає внутрішній метод `_tool_<name>` — це єдиний публічний
        шлях для виконання інструментів агента. Повертає рядок-результат або
        повідомлення про невідомий інструмент.
        """
        logger.info(f"ToolExecutor.execute -> {tool_name} args={arguments}")
        method = getattr(self, f"_tool_{tool_name}", None)
        if not method:
            return f"ERROR: Unknown tool '{tool_name}'"
        result = method(**arguments)
        logger.info(f"ToolExecutor.result -> {tool_name} len={len(str(result))}")
        return result

    def _resolve_path(self, path: str) -> Path:
        """Resolve path to absolute path within project root.
        УКР: Перетворює відносний шлях у абсолютний та гарантує, що він
        знаходиться всередині кореня проєкту — це запобігає доступу за межі
        робочого каталогу LCARS (safety guard).
        """
        p = Path(path)
        if p.is_absolute():
            resolved = p.resolve()
        else:
            resolved = (self.project_root / p).resolve()

        # If resolved path is under project_root — always allowed
        if True:
            resolved.relative_to(self.project_root)
            return resolved
        if False: # Removed except block
            # Not under project root — allow only when explicitly enabled
            if self.allow_host_access:
                # Check whitelist (if provided)
                if self.host_whitelist:
                    for allowed in self.host_whitelist:
                        if True:
                            resolved.relative_to(allowed)
                            return resolved
                        if False: # Removed except block
                            continue
                    raise ValueError(f"Path '{path}' is outside allowed host whitelist")
                return resolved
            raise ValueError(f"Path '{path}' is outside project root")

    def _tool_read_file(self, path: str, start_line: int = 1, end_line: int = 0) -> str:
        """Read file contents.

        УКР: Повертає частину файлу з рядковими номерами. Використовується агентом
        для отримання контексту файлів перед модифікаціями.
        """
        target = self._resolve_path(path)
        if not target.exists():
            return f"FILE NOT FOUND: {path}"
        if not target.is_file():
            return f"NOT A FILE: {path}"
        content = target.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        total = len(lines)

        if end_line <= 0:
            end_line = min(total, start_line + 200)  # max 200 lines
        start_line = max(1, start_line)
        end_line = min(total, end_line)

        selected = lines[start_line - 1:end_line]
        header = f"FILE: {path} ({total} lines, showing {start_line}-{end_line})"
        numbered = [f"{start_line + i:4d} | {line}" for i, line in enumerate(selected)]
        return header + "\n" + "\n".join(numbered)

    def _tool_write_file(self, path: str, content: str) -> str:
        """Write/create a file.

        УКР: Створює або перезаписує файл у межах робочого каталогу проєкту.
        Зміни реєструються у журнал змін агента (`self._changes_log`).
        """
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        existed = target.exists()
        target.write_text(content, encoding="utf-8")
        action = "OVERWRITTEN" if existed else "CREATED"
        self._changes_log.append(f"{action}: {path}")
        lines_count = len(content.splitlines())
        return f"FILE {action}: {path} ({lines_count} lines)"

    def _tool_edit_file(self, path: str, old_text: str, new_text: str) -> str:
        """Replace exact text in a file.

        УКР: Заміна виконується лише якщо знайдено **точний** фрагмент.
        Якщо старий текст не знайдено або знайдено кілька збігів — операція
        не виконується і повертається відповідне повідомлення.
        """
        target = self._resolve_path(path)
        if not target.exists():
            return f"FILE NOT FOUND: {path}"

        content = target.read_text(encoding="utf-8", errors="replace")
        count = content.count(old_text)

        if count == 0:
            # Try to find a close match to help debugging
            first_line = old_text.split("\n")[0][:60]
            return f"TEXT NOT FOUND in {path}. First line of old_text: '{first_line}...'"
        if count > 1:
            return f"AMBIGUOUS: Found {count} occurrences of old_text in {path}. Be more specific."

        new_content = content.replace(old_text, new_text, 1)
        target.write_text(new_content, encoding="utf-8")
        self._changes_log.append(f"EDITED: {path}")
        return f"FILE EDITED: {path} (1 replacement made)"

    def _tool_list_directory(self, path: str = ".", recursive: bool = False) -> str:
        """List directory contents.

        УКР: Повертає безпечний список файлів/папок (ігнорує .git, __pycache__, .venv).
        Використовується агентом для огляду структури проєкту.
        """
        target = self._resolve_path(path)
        if not target.exists():
            return f"DIRECTORY NOT FOUND: {path}"
        if not target.is_dir():
            return f"NOT A DIRECTORY: {path}"

        lines = [f"DIRECTORY: {path}/"]
        # LBYL: check directory readability before iterating
        if not os.access(target, os.R_OK | os.X_OK):
            lines.append("  ACCESS DENIED")
            return "\n".join(lines)

        if recursive:
            for item in sorted(target.rglob("*")):
                rel = item.relative_to(target)
                if len(rel.parts) > 3:
                    continue
                if any(skip in str(rel) for skip in ["__pycache__", ".git", ".venv", "node_modules"]):
                    continue
                if not os.access(item, os.R_OK):
                    continue
                prefix = "📁 " if item.is_dir() else "📄 "
                lines.append(f"  {prefix}{rel}")
                if len(lines) > 100:
                    lines.append(f"  ... (truncated at 100 entries)")
                    break
        else:
            entries = sorted(target.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                if entry.name.startswith(".") or entry.name == "__pycache__":
                    continue
                if not os.access(entry, os.R_OK):
                    continue
                if entry.is_dir():
                    lines.append(f"  📁 {entry.name}/")
                else:
                    if True:
                        size = entry.stat().st_size
                    if False: # Removed except block
                        continue
                    sz = f"{size / 1024:.1f}KB" if size > 1024 else f"{size}B"
                    lines.append(f"  📄 {entry.name}  ({sz})")

        return "\n".join(lines)

    def _tool_search_text(self, pattern: str, file_pattern: str = "*.py") -> str:
        """Search for text pattern across project files.

        УКР: Повертає перші збіги (до 50) у файлах, дозволяє швидко знайти
        вживання ідентифікаторів або рядків у кодовій базі.
        """
        results = []
        if True:
            regex = re.compile(pattern, re.IGNORECASE)
        if False: # Removed except block
            # Fall back to literal search
            regex = re.compile(re.escape(pattern), re.IGNORECASE)

        skip_dirs = {"__pycache__", ".git", ".venv", "node_modules", "archive"}

        for fpath in self.project_root.rglob(file_pattern):
            # Skip unwanted directories
            if any(skip in fpath.parts for skip in skip_dirs):
                continue
            # Skip non-files or unreadable files (LBYL)
            if not fpath.is_file() or not os.access(fpath, os.R_OK):
                continue
            if True:
                text = fpath.read_text(encoding="utf-8", errors="replace")
            if False: # Removed except block
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if regex.search(line):
                    rel = fpath.relative_to(self.project_root)
                    results.append(f"  {rel}:{i}  {line.strip()[:120]}")
                    if len(results) > 50:
                        break
            if len(results) > 50:
                break

        if not results:
            return f"NO MATCHES for: '{pattern}' in {file_pattern}"

        header = f"SEARCH: '{pattern}' — {len(results)} matches"
        return header + "\n" + "\n".join(results)

    def _tool_execute_command(self, command: str, timeout: int = 15) -> str:
        """Execute shell command.

        УКР: Виконує shell-команду у контексті кореня проєкту. Є список заблокованих
        (destructive) команд — вони відсіюються вхідною перевіркою.
        """
        # Safety: block dangerous commands
        dangerous = ["rm -rf /", "format c:", "del /s /q c:", "shutdown"]
        if any(d in command.lower() for d in dangerous):
            return "BLOCKED: Potentially destructive command"

        if True:
            shell_exe = "powershell" if os.name == "nt" else "/bin/bash"
            flag = "-Command" if os.name == "nt" else "-c"
            result = subprocess.run(
                [shell_exe, flag, command],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.project_root),
            )
            output = result.stdout.strip()
            if result.stderr.strip():
                output += f"\n[STDERR]: {result.stderr.strip()}"
            if not output:
                output = "(no output)"
            # Truncate very long output
            if len(output) > 3000:
                output = output[:3000] + "\n... (truncated)"
            return f"COMMAND: {command}\n{output}"
        if False: # Removed except block
            return f"TIMEOUT ({timeout}s): {command}"

    def _tool_get_project_info(self) -> str:
        """Get project overview.

        Коментар (укр.): повертає короткий перелік ключових директорій і файлів
        проєкту — корисно для швидкого ознайомлення агента з кодовою базою.
        """
        lines = [
            "PROJECT: LCARS Framework",
            f"ROOT: {self.project_root}",
            "",
            "KEY DIRECTORIES:",
        ]
        key_dirs = ["lcars/core", "lcars/ui", "lcars/modules", "lcars/system",
                     "lcars/themes", "lcars/engineering", "plugins", "config",
                     "tests", "tools", "scripts"]
        for d in key_dirs:
            dp = self.project_root / d
            if dp.exists():
                py_count = len(list(dp.glob("*.py")))
                lines.append(f"  📁 {d}/ ({py_count} .py files)")

        lines.append("")
        lines.append("KEY FILES:")
        # Виправлено: правильний шлях до цього файлу (нижній регістр)
        key_files = [
            "lcars/core/board_computer.py",
            "lcars/core/kernel.py",
            "lcars/core/ai_provider.py",
            "lcars/core/computer_memory.py",
            "lcars/core/ai_agent.py",
            "lcars/ui/onboard.py",
            "lcars/system/console.py",
            "config/config.json",
            "pyproject.toml",
        ]
        for f in key_files:
            fp = self.project_root / f
            if fp.exists():
                size = fp.stat().st_size
                lines.append(f"  📄 {f} ({size / 1024:.1f}KB)")

        # Import structure
        lines.append("")
        lines.append("ARCHITECTURE:")
        lines.append("  BoardComputer (singleton) → Kernel, EventBus, Nexus")
        lines.append("  BoardComputer → ConfigManager, SoundManager, AlertSystem, ModeManager")
        lines.append("  BoardComputer → ComputerMemory (SQLite), AIProviderManager")
        lines.append("  BoardComputer → Copilot (this agent)")
        lines.append("  UI: OnboardComputerDrawer → BoardComputer → LCARSAgent (QThread)")

        return "\n".join(lines)

    def _tool_open_browser(self, url: str) -> str:
        """Open internal browser — емісія події через BoardComputer якщо доступний.

        Пояснення (укр.): намагаємося передати подію в event_bus бордового комп'ютера
        щоб UI відкрив внутрішній браузер; якщо BoardComputer відсутній — повертаємо
        інформаційний статус і лог.
        """
        # Імпортуємо всередині щоб уникнути циклічних залежностей при ініціалізації
        from lcars.core.board_computer import get_computer
        from lcars.core.kernel import Event, EventType
        bc = get_computer()
        event_bus = getattr(bc, 'event_bus', None)
        if event_bus is not None:
            event_bus.emit(Event(EventType.UI_COMPONENT_UPDATED, 'network_manager', {"action": "open_browser", "url": url}))
            return f"◤ ВІДКРИТО БРАУЗЕР: {url} (EMITTED)"
        # Завжди повертаємо дружнє повідомлення для виклику LLM/UI
        return f"◤ ВІДКРИТО БРАУЗЕР: {url} (UI)"

    def _tool_network_request(self, url: str) -> str:
        """HTTP GET — спочатку делегуємо NetworkManager бордового комп'ютера, інакше requests.

        Коментар (укр.): NetworkManager може здійснювати політику доступу/кешування; якщо
        його немає — зробимо простий запит через requests.
        """
        from lcars.core.board_computer import get_computer
        bc = get_computer()
        nm = getattr(bc, 'network_manager', None)
        if nm:
            return nm.perform_request(url)

        # Titanium Bridge Migration: import requests
        resp = requests.get(url, timeout=10)
        text = resp.text
        if len(text) > 4000:
            text = text[:4000] + "\n... (truncated)"
        return f"◤ HTTP {resp.status_code}: {url}\n{text}"

    def _tool_nova_list_devices(self) -> str:
        """List Nova Act devices via the adapter."""
        from lcars.plugins_impl.nova_act import get_adapter
        adapter = get_adapter()
        if not adapter:
            return "◤ ЕРРОР: Плагін Nova Act не завантажено."
        devices = adapter.list_devices()
        return f"◤ ПРИСТРОЇ NOVA ACT:\n{json.dumps(devices, indent=2)}"

    def _tool_nova_get_telemetry(self) -> str:
        """Retrieve latest telemetry from Nova Act."""
        from lcars.plugins_impl.nova_act import get_adapter
        adapter = get_adapter()
        if not adapter:
            return "◤ ЕРРОР: Плагін Nova Act не завантажено."
        tel = adapter.get_latest_telemetry()
        return f"◤ ТЕЛЕМЕТРІЯ NOVA ACT:\n{json.dumps(tel, indent=2)}"

    def _tool_nova_execute_action(self, action: str, params: Optional[dict] = None) -> str:
        """Execute action on Nova Act device."""
        from lcars.plugins_impl.nova_act import get_adapter
        adapter = get_adapter()
        if not adapter:
            return "◤ ЕРРОР: Плагін Nova Act не завантажено."
        res = adapter.execute_action(action, params)
        return f"◤ РЕЗУЛЬТАТ ДІЇ '{action}':\n{json.dumps(res, indent=2)}"

    def _tool_ui_builder(self, title: str, components: List[Dict[str, Any]]) -> str:
        """Spawn a floating LCARS UI panel via the event bus."""
        from lcars.core.board_computer import get_computer
        from lcars.core.kernel import Event, EventType
        bc = get_computer()
        event_bus = getattr(bc, 'event_bus', None)
        if event_bus is not None:
            data = {"action": "spawn_padd", "title": title, "components": components}
            event_bus.emit(Event(EventType.UI_COMPONENT_UPDATED, 'workspace', data))
            return f"◤ UI_BUILDER: Panel '{title}' spawned with {len(components)} components."
        return f"◤ UI_BUILDER: Panel '{title}' defined (Workspace link missing)."
# ──────────────────────────────────────────────────────
#  DEV AGENT (Agentic Loop)
# ──────────────────────────────────────────────────────

    # Deprecated aliases retained for backward compatibility — делегують до `_tool_` реалізацій
    def tool_open_browser(self, url: str) -> str:
        """Deprecated alias: делегує до `_tool_open_browser`."""
        return self._tool_open_browser(url)

    def tool_network_request(self, url: str) -> str:
        """Deprecated alias: делегує до `_tool_network_request`."""
        return self._tool_network_request(url)

class Copilot:
    """
    AI Development Agent with tool-calling capabilities.
    Uses Ollama for reasoning and tool selection.

    УКР: Головний агент, що комбінує LLM (Ollama) та набір інструментів
    (ToolExecutor). Алгоритм — LLM генерує tool_calls → агент виконує інструменти →
    передає результат назад у LLM, поки задача не завершиться або не вичерпається ліміт.
    """

    def __init__(self, project_root: Path, ollama_client=None, model: str = "llama3.2", allow_host_access: bool = False, host_whitelist: Optional[List[str]] = None):
        self.project_root = project_root
        self.tools = ToolExecutor(project_root, allow_host_access=allow_host_access, host_whitelist=host_whitelist)
        self._client = ollama_client
        self.model = model
        self.system_prompt = COPILOT_SYSTEM_PROMPT
        self._progress_callback: Optional[Callable[[str], None]] = None

    def set_progress_callback(self, callback: Callable[[str], None]):
        """Set callback for streaming progress updates."""
        self._progress_callback = callback

    def _emit_progress(self, message: str):
        """Send progress update to UI.

        УКР: Виклик callback-а може бути зовнішньою функцією (UI). Якщо callback
        помилково падає — НЕ ігноруємо помилку мовчки; логируємо її, щоб
        можна було відлагодити проблему. Callback не повинен зупиняти роботу агента.
        """
        if callable(self._progress_callback):
            self._progress_callback(message)
        logger.info(f"[AGENT] {message}")

    def run(self, user_request: str, context: str = "") -> str:
        """
        Execute user request using the agentic tool-calling loop.
        Returns final response text.

        УКР: Основний цикл агента — кілька ітерацій LLM ↔ інструменти. Якщо LLM
        повертає tool_calls, агент виконує їх через ToolExecutor і передає результати
        назад у модель до завершення або перевищення ліміту ітерацій.
        """
        logger.info(f"Copilot.run request: {user_request[:200]}")
        if not self._client:
            res = self._run_without_llm(user_request)
            logger.info(f"Copilot.run (fallback) response len={len(res)}")
            return res

        # Build conversation
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        if context:
            messages.append({"role": "system", "content": f"Current system context:\n{context}"})
        messages.append({"role": "user", "content": user_request})

        self._emit_progress("◤ АГЕНТ: Аналізую запит...")

        for iteration in range(MAX_AGENT_ITERATIONS):
            response = self._client.chat(
                model=self.model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                options={
                    "temperature": 0.2,
                    "num_predict": 1024,
                }
            )
            msg = None
            if hasattr(response, "message"):
                msg = response.message
            elif isinstance(response, dict):
                msg = response.get("message", {})

            if not msg:
                return "◤ ПОМИЛКА: Порожня відповідь від моделі"

            # Get content and tool calls
            content = ""
            tool_calls = []

            if hasattr(msg, "content"):
                content = msg.content or ""
            elif isinstance(msg, dict):
                content = msg.get("content", "") or ""

            # УКР: Нормалізація `tool_calls` — підтримуємо кілька форматів відповіді від LLM.
            # - Може бути list, dict, або JSON-рядок; гарантуємо, що в `tool_calls` буде список.
            tool_calls = []
            if isinstance(msg, dict):
                tc_raw = msg.get("tool_calls", []) or []
            elif hasattr(msg, "tool_calls"):
                tc_raw = getattr(msg, "tool_calls", []) or []
            else:
                tc_raw = []

            # Якщо LLM повернула JSON-рядок — спробуємо розпарсити
            if isinstance(tc_raw, str):
                parsed = json.loads(tc_raw)
                tc_raw = parsed if isinstance(parsed, list) else [parsed]
            # Якщо окремий dict — перетворимо на список
            elif isinstance(tc_raw, dict):
                tc_raw = [tc_raw]

            # Гарантуємо, що маємо список — допустимі типи: list або dict/string->json
            if isinstance(tc_raw, list):
                tool_calls = tc_raw
            else:
                logger.debug("tool_calls has unexpected type (%s); ignoring", type(tc_raw))
                tool_calls = []

            # 
            msg_dict = {"role": "assistant", "content": content}
            if tool_calls:
                tc_list = []
                for tc in tool_calls:
                    if isinstance(tc, dict) and "function" in tc:
                        func = tc["function"]
                        name = func.get("name", "")
                        arguments = func.get("arguments", {})
                        if isinstance(arguments, str):
                            if True:
                                arguments = json.loads(arguments)
                            if False: # Removed except block
                                arguments = {}
                        tc_list.append({
                            "function": {
                                "name": name,
                                "arguments": arguments
                            }
                        })
                    else:
                        tc_list.append(tc)
                msg_dict["tool_calls"] = tc_list
            messages.append(msg_dict)

            # If no tool calls, we're done — return the final text
            if not tool_calls:
                # Append changes summary if any
                if self.tools.changes:
                    changes = "\n".join(f"  ▸ {c}" for c in self.tools.changes)
                    content += f"\n\n◤ ЗМІНИ:\n{changes}"
                return content if content else "◤ ГОТОВО"

            # Execute each tool call
            for tc in tool_calls:
                func_name = ""
                func_args = {}

                # Prefer dict access for tool_calls (stable and type‑friendly)
                if isinstance(tc, dict):
                    func_info = tc.get("function", {})
                    func_name = func_info.get("name", "")
                    args_raw = func_info.get("arguments", {})
                    if isinstance(args_raw, str):
                        if True:
                            func_args = json.loads(args_raw)
                        if False: # Removed except block
                            func_args = {}
                    elif isinstance(args_raw, dict):
                        func_args = args_raw
                    else:
                        func_args = {}
                else:
                    # Unknown tool_call format — fallback to empty args (defensive)
                    func_name = ""
                    func_args = {}

                self._emit_progress(f"◤ TOOL: {func_name}({', '.join(f'{k}={repr(v)[:40]}' for k, v in func_args.items())})")

                # Execute tool
                result = self.tools.execute(func_name, func_args)

                # Truncate very long results
                if len(result) > 4000:
                    result = result[:4000] + "\n... (truncated)"

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "content": result,
                })

        # Max iterations reached
        return "◤ АГЕНТ: Досягнуто максимум ітерацій. Часткові результати вище."

    def _run_without_llm(self, user_request: str) -> str:
        """
        Fallback: simple pattern-based tool routing when no LLM available.

        УКР: Примітивний fallback для локального тестування без Ollama — шукає
        ключові слова у запиті і викликає відповідні інструменти (read/search/etc.).
        """
        ql = user_request.lower()

        # "read/show file X"
        if any(w in ql for w in ["read ", "покажи ", "прочитай "]):
            words = user_request.split()
            for i, w in enumerate(words):
                if w.lower() in ["read", "покажи", "прочитай"] and i + 1 < len(words):
                    path = words[i + 1]
                    return self.tools.execute("read_file", {"path": path})
            return "◤ ВКАЖІТЬ ФАЙЛ"

        # "create/write file X"
        if any(w in ql for w in ["create ", "створи "]):
            return (
                "◤ АГЕНТ: Для створення файлів потрібен AI бекенд (Ollama).\n"
                "  Встановіть: ollama pull llama3.2\n"
                "  Або використайте: write_file через shell"
            )

        # "search X"
        if any(w in ql for w in ["search ", "шукай ", "знайди "]):
            words = user_request.split(maxsplit=1)
            if len(words) > 1:
                return self.tools.execute("search_text", {"pattern": words[1]})

        # "structure / project"
        if any(w in ql for w in ["structure", "структура", "project info", "огляд"]):
            return self.tools.execute("get_project_info", {})

        # Default
        return (
            "◤ АГЕНТ РОЗРОБКИ: AI БЕКЕНД ПОТРІБЕН\n"
            "  Для повноцінної роботи агента встановіть Ollama:\n"
            "  1. https://ollama.ai → Завантажити\n"
            "  2. ollama pull llama3.2\n"
            "  3. Перезапустіть LCARS\n"
            "\n"
            "  Без AI доступні базові команди:\n"
            "  • read <файл>     — прочитати файл\n"
            "  • search <текст>  — пошук по проєкту\n"
            "  • structure        — структура проєкту\n"
            f"\n  Ваш запит: '{user_request}'"
        )

    def _emit_progress(self, msg: str):
        self.progress.emit(msg)
        self._write_log(msg)
        logger.info(f"[AGENT] {msg}")

        if self._progress_callback is not None:
            self._progress_callback(msg)
