"""
LCARS Agent Launcher — ONBOARD AGENT v1.0
Запуск бортового комп'ютера з повним agent loop, пам'яттю та навичками.

Покласти цей файл у корінь LCARS-Framework поруч із lcars/

Запуск:
    python start_lcars_agent.py

Команди:
    help           - Показати допомогу
    agent <завдання> - Запустити агента (повний цикл)
    think <запит>   - Швидке запитання без збереження в контексті
    status         - Статус агента
    diagnose       - Запустити самодіагностику
    mode <режим>    - Встановити режим (ACTIVE, STANDBY, DIAGNOSTIC, BACKGROUND)
    skills         - Список завантажених навичок
    tasks          - Статус черги задач
    memory         - Статус пам'яті
    history [n]    - Історія діалогів (останні n записів)
    quit
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent

# ─── ІНТЕГРАЦІЯ З ONBOARD AGENT ────────────────────────────────────────────

def get_onboard_agent():
    """Отримати ініціалізований OnboardAgent."""
    from lcars.service.agent import GetAgent, InitializeAgent
    Agent = GetAgent(str(ROOT))
    if Agent.State.value == "OFFLINE":
        if not InitializeAgent(str(ROOT)):
            raise RuntimeError("Agent initialization failed")
    return Agent

# ═══════════════════════════════════════════════════════════════════════════
#  LOCAL TOOLS (для сумісності з Copilot)
# ═══════════════════════════════════════════════════════════════════════════

class LocalTools:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def safePath(self, path: str) -> Path:
        target = (self.root / path).resolve()
        target.relative_to(self.root)
        return target

    def files(self, path: str = ".") -> str:
        target = self.safePath(path)
        if not target.exists():
            return f"PATH NOT FOUND: {path}"
        if not target.is_dir():
            return f"NOT DIRECTORY: {path}"
        skip = {".git", ".venv", "__pycache__", "node_modules"}
        out = [f"DIRECTORY: {target}"]
        for item in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            if item.name in skip:
                continue
            mark = "[DIR] " if item.is_dir() else "[FILE]"
            out.append(f"{mark} {item.name}")
        return "\n".join(out)

    def read(self, path: str, start: int = 1, end: int = 160) -> str:
        target = self.safePath(path)
        if not target.exists():
            return f"FILE NOT FOUND: {path}"
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        start = max(1, int(start))
        end = min(len(lines), int(end))
        out = [f"FILE: {path} ({len(lines)} lines, showing {start}-{end})"]
        for number in range(start, end + 1):
            out.append(f"{number:4d} | {lines[number - 1]}")
        return "\n".join(out)

    def search(self, text: str) -> str:
        found = []
        skip = {".git", ".venv", "__pycache__", "node_modules"}
        for filePath in self.root.rglob("*.py"):
            if any(part in skip for part in filePath.parts):
                continue
            content = filePath.read_text(encoding="utf-8", errors="replace")
            for number, line in enumerate(content.splitlines(), 1):
                if text.lower() in line.lower():
                    found.append(f"{filePath.relative_to(self.root)}:{number}  {line.strip()}")
                    if len(found) >= 80:
                        return "\n".join(found)
        return "\n".join(found) if found else "NO MATCHES"

    def run(self, command: str) -> str:
        shell = "powershell" if os.name == "nt" else "/bin/bash"
        flag = "-Command" if os.name == "nt" else "-c"
        result = subprocess.run(
            [shell, flag, command],
            cwd=str(self.root),
            capture_output=True,
            text=True,
            timeout=60,
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        if err:
            out = (out + "\n" if out else "") + "ERROR:\n" + err
        return out or "NO OUTPUT"


class LCARSAgentRuntime:
    """Рантайм бортового агента з повним функціоналом."""

    def __init__(self):
        self.Agent = get_onboard_agent()
        self.Tools = LocalTools(ROOT)

    def agentInfo(self) -> str:
        """Інформація про агента."""
        Status = self.Agent.GetStatus()
        Lines = [
            "◤ ONBOARD AGENT STATUS",
            f"  ID:     {Status['agent_id']}",
            f"  State:  {Status['state']}",
            f"  Mode:   {Status['mode']}",
            f"  Skills: {Status['skills_loaded']}",
            f"  Turns:  {Status['conversation_turns']}",
        ]

        # Memory stats
        Memory = Status.get('memory', {})
        if Memory:
            Lines.append(f"  Memory: {Memory.get('sessions', 0)} sessions, {Memory.get('dialog_entries', 0)} dialogs")

        # Task queue
        Tasks = Status.get('task_queue', {})
        if Tasks:
            Lines.append(f"  Tasks:  {Tasks.get('running_count', 0)}/{Tasks.get('max_concurrent', 0)} running, {Tasks.get('queue_size', 0)} queued")

        return "\n".join(Lines)

    def execute(self, command: str) -> str:
        command = command.strip()
        low = command.lower()

        if not command:
            return ""

        # Допомога
        if low == "help":
            return self.help()

        # Інформація про агента
        if low in ("agent-info", "agent info"):
            return self.agentInfo()

        # Статус агента
        if low == "status":
            return self.agentInfo()

        # Діагностика
        if low == "diagnose":
            Report = self.Agent.Diagnose()
            import json
            return f"◤ DIAGNOSTIC REPORT\n{json.dumps(Report, indent=2, ensure_ascii=False)}"

        # Режим роботи
        if low.startswith("mode "):
            ModeName = command[5:].strip().upper()
            from lcars.service.agent import AgentMode
            try:
                Mode = AgentMode[ModeName]
                return self.Agent.SetMode(Mode)
            except KeyError:
                return f"◤ UNKNOWN MODE: {ModeName}. Available: ACTIVE, STANDBY, DIAGNOSTIC, RECOVERY, BACKGROUND, LEARNING"

        # Список навичок
        if low == "skills":
            Skills = self.Agent.ListSkills()
            return f"◤ LOADED SKILLS ({len(Skills)}):\n" + "\n".join(f"  - {s}" for s in Skills)

        # Статус задач
        if low == "tasks":
            Status = self.Agent.GetTaskStatus()
            import json
            return f"◤ TASK QUEUE:\n{json.dumps(Status, indent=2)}"

        # Статус пам'яті
        if low == "memory":
            from lcars.modules.memory import GetMemory
            Memory = GetMemory()
            Stats = Memory.GetMemoryStats()
            import json
            return f"◤ MEMORY:\n{json.dumps(Stats, indent=2, ensure_ascii=False)}"

        # Історія діалогів
        if low.startswith("history"):
            Parts = command.split()
            Limit = int(Parts[1]) if len(Parts) > 1 else 10
            from lcars.modules.memory import GetDialogHistory
            History = GetDialogHistory(Limit=Limit)
            if not History:
                return "◤ NO HISTORY"
            Lines = ["◤ DIALOG HISTORY:"]
            for Entry in History[-Limit:]:
                Role = "USER" if Entry.get("role") == "user" else "AGENT"
                Content = Entry.get("content", "")[:80]
                Lines.append(f"  [{Role}] {Content}...")
            return "\n".join(Lines)

        # Швидкий think (без agent prefix)
        if low.startswith("think "):
            Query = command[6:].strip()
            return self.Agent.Think(Query)

        # Agent команда (повний цикл з контекстом)
        if low.startswith("agent "):
            Task = command[6:].strip()
            return self.Agent.Think(Task)

        # Локальні команди
        if low == "files":
            return self.Tools.files(".")
        if low.startswith("files "):
            return self.Tools.files(command[6:].strip())
        if low.startswith("read "):
            Parts = command.split()
            if len(Parts) == 2:
                return self.Tools.read(Parts[1])
            if len(Parts) >= 4:
                return self.Tools.read(Parts[1], int(Parts[2]), int(Parts[3]))
            return "FORMAT: read path start end"
        if low.startswith("search "):
            return self.Tools.search(command[7:].strip())
        if low.startswith("run "):
            return self.Tools.run(command[4:].strip())

        # Ехо для невідомих команд
        return f"◤ UNKNOWN: {command}\nType 'help' for available commands."

    def help(self) -> str:
        return """
◤ LCARS ONBOARD AGENT v1.0

AGENT COMMANDS:
  agent <task>     Запустити агента з повним контекстом
  think <query>    Швидке запитання без збереження
  status           Статус агента
  diagnose         Запустити самодіагностику
  mode <MODE>      Встановити режим (ACTIVE, STANDBY, DIAGNOSTIC, BACKGROUND)
  skills           Список завантажених навичок
  tasks            Статус черги задач
  memory           Статус пам'яті
  history [n]      Історія діалогів (останні n записів)

FILE COMMANDS:
  files [path]     Список файлів
  read <path>      Читати файл
  search <text>    Пошук по файлах
  run <cmd>        Виконати команду shell

Exit:
  quit
""".strip()


def main():
    print("=" * 60)
    print("  LCARS ONBOARD AGENT v1.0 - TITANIUM CORE ONLINE")
    print("  Library Computer Access/Retrieval System")
    print("=" * 60)
    print("  Commands: help | agent <task> | think <query>")
    print("  File ops: files | read | search | run")
    print("  Agent:     status | diagnose | skills | tasks")
    print("=" * 60)
    print()

    try:
        runtime = LCARSAgentRuntime()
        print(f"Agent initialized: {runtime.Agent.AgentId}")
        print(f"Skills loaded: {len(runtime.Agent.ListSkills())}")
        print()
    except Exception as E:
        print(f"[!] Initialization error: {E}")
        print("Running in fallback mode...")
        print()

    while True:
        try:
            line = input("LCARS> ").strip()
        except KeyboardInterrupt:
            print("\n◤ SHUTTING DOWN...")
            break
        if line.lower() in ("quit", "exit"):
            print("◤ GOODBYE")
            break
        result = runtime.execute(line)
        if result:
            print(result)
            print()


if __name__ == "__main__":
    main()
