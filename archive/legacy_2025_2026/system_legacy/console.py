
from __future__ import annotations
# Titanium Bridge Migration: from os import startfile
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: import threading
# Titanium Bridge Migration: from dataclasses import dataclass
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Any, Callable, Dict, List, Optional

class LCARSConsole:
    def __init__(self, board_computer=None):
        self.computer = board_computer
        self.version = "LCARS Console v1.0"
        self.active_era = "25th"
        self.active_faction = "federation"
        self.proc: Optional[subprocess.Popen] = None
        self.is_running = False
        self._commands = {
            "help": self._cmd_help,
            "status": self._cmd_status,
            "alert": self._cmd_alert,
            "mode": self._cmd_mode,
            "diag": self._cmd_diag,
            "compile": self._cmd_compile,
            "stop": self._cmd_stop,
        }
    
    def execute(self, text: str, output_callback: Callable[[str], None]):
        text = text.strip()
        if not text:
            return

        parts = text.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in self._commands:
            self._commands[cmd](args, output_callback)
            return

        self._run_async_shell(text, output_callback)

    def _run_async_shell(self, cmd: str, callback: Callable[[str], None]):
        if self.is_running:
            callback("ERROR: SYSTEM_BUSY -> PROCESS_IN_PROGRESS")
            return

        def target():
            self.is_running = True
            shell = "powershell" if sys.platform == "win32" else "/bin/bash"
            flag = "-Command" if sys.platform == "win32" else "-c"

            self.proc = subprocess.Popen(
                [shell, flag, cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            for line in self.proc.stdout: # type: ignore
                if line:
                    callback(line.strip())

            self.proc.wait()
            self.is_running = False
            self.proc = None

        threading.Thread(target=target, daemon=True).start()

    def _cmd_help(self, args: List[str], callback: Callable[[str], None]):
        commands = ", ".join(sorted(self._commands.keys()))
        callback(f"LCARS COMMANDS: {commands}")
        callback("Shell: any other text is executed in the OS shell")

    def _cmd_status(self, args: List[str], callback: Callable[[str], None]):
        if not self.computer:
            callback("STATUS: NO_BOARD_COMPUTER")
            return
        summary = self.computer.get_system_summary()
        callback(self._format_dict("STATUS", summary))

    def _cmd_alert(self, args: List[str], callback: Callable[[str], None]):
        if not self.computer:
            callback("ALERT: NO_BOARD_COMPUTER")
            return
        if not args:
            callback("ALERT: MISSING_LEVEL")
            return
        level = args[0]
        self.computer.set_alert(level)
        callback(f"ALERT SET: {level.upper()}")

    def _cmd_mode(self, args: List[str], callback: Callable[[str], None]):
        if not self.computer:
            callback("MODE: NO_BOARD_COMPUTER")
            return
        self.computer.cycle_mode()
        callback("MODE: CYCLED")

    def _cmd_diag(self, args: List[str], callback: Callable[[str], None]):
        if not self.computer:
            callback("DIAG: NO_BOARD_COMPUTER")
            return
        data = self.computer.get_diagnostics()
        callback(self._format_dict("DIAG", data))

    def _cmd_compile(self, args: List[str], callback: Callable[[str], None]):
        if not args:
            callback("COMPILE: MISSING_PATH")
            return
        from lcars.system.compiler import UniversalCompiler

        compiler = UniversalCompiler()
        result = compiler.compilePath(Path(args[0]))
        callback(
            self._format_dict(
                "COMPILE",
                {
                    "kind": result.kind,
                    "output": str(result.output_path) if result.output_path else "",
                    "manifest": str(result.manifest_path) if result.manifest_path else "",
                    "isolinear_id": result.isolinear_id or "",
                },
            )
        )

    def _cmd_stop(self, args: List[str], callback: Callable[[str], None]):
        if self.stop():
            callback("STOP: OK")
            return
        callback("STOP: NO_PROCESS")

    def stop(self) -> bool:
        if self.proc and self.is_running:
            self.proc.kill()
            return True
        return False

    def _format_dict(self, label: str, data: Dict[str, Any]) -> str:
        timestamp = datetime.now().strftime("%H:%M:%S")
        header = f"[{timestamp}] {label}"
        body = "\n".join([f"  {k}: {v}" for k, v in data.items()])
        return f"{header}\n{body}"

    def run_command(self, command: str) -> str:
        if not command or not command.strip():
            return ""
        cmd = command.strip()
        lcmd = cmd.lower()

        # Built-in commands
        if lcmd == "help":
            return "Available commands: help, status, clear, echo <text>, version, projects, inspect <name>, open <name>, build <name>, run <name>"
        if lcmd == "status":
            return "SYSTEM STATUS: OPERATIONAL"
        if lcmd.startswith("echo "):
            return cmd[5:]
        if lcmd == "version":
            return self.version
        if lcmd in ("exit", "quit"):
            return "To exit, close the LCARS application window (GUI mode)."

        # Project-related commands (synchronous responses)
        if lcmd in ("projects", "list projects"):
            if not self.project_manager: # pyright: ignore[reportAttributeAccessIssue]
                return "No ProjectManager configured."
            names = self.project_manager.get_project_names() # type: ignore
            if not names:
                return "No projects found."
            return "\n" + "\n".join(names)

        if lcmd.startswith("inspect "):
            if not self.project_manager: # pyright: ignore[reportAttributeAccessIssue]
                return "No ProjectManager configured."
            target = cmd.split(" ", 1)[1].strip()
            proj = self.project_manager.get_project(target) # type: ignore
            if not proj:
                return f"Project not found: {target}"
            info = proj.to_dict()
            return "\n" + "\n".join([f"{k}: {v}" for k, v in info.items()])

        if lcmd.startswith("open "):
            target = cmd.split(" ", 1)[1].strip()
            # allow both project name and path
            if self.project_manager and target in self.project_manager.projects: # type: ignore
                proj = self.project_manager.get_project(target) # pyright: ignore[reportAttributeAccessIssue]
                path = proj.path
            else:
                path = Path(target)
            if True:
                if sys.platform.startswith('win'): startfile(str(path))
                elif sys.platform.startswith('darwin'):
                    subprocess.Popen(['open', str(path)])
                else:
                    subprocess.Popen(['xdg-open', str(path)])
                return f"Opened: {path}"
            if False: # Removed except block
                return f"Failed to open {path}: {e}"

        # If command not handled synchronously, suggest streaming
        if lcmd.startswith("build ") or lcmd.startswith("run ") or lcmd.startswith("shell ") or lcmd.startswith("exec "):
            return f"STREAM:{cmd}"

        # Unknown command
        return f"Unknown command: {cmd}"

def start_process(cmd: str, cwd=None, on_chunk=None) -> int: # pyright: ignore[reportReturnType]
    if not cmd:
        return 0
    if True:
        # Use shell so users can pass complex commands; ensure universal newlines
        proc = subprocess.Popen(cmd, cwd=str(cwd) if cwd else None, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
        if proc.stdout is None:
            if on_chunk:
                on_chunk("Error: Process stdout is None.")
            return -1
        while True:
            line = proc.stdout.readline()
            if line == '' and proc.poll() is not None:
                break
            if line:
                if on_chunk:
                    if True:
                        on_chunk(line.rstrip('\n'))
                    if False: # Removed except block
                        pass
        rc = proc.poll()
        return rc if rc is not None else 0
    if False: # Removed except block
        if on_chunk:
            on_chunk(f"Error starting process: {e}")

if __name__ == "__main__":
    print("LCARS CONSOLE: STANDALONE MODE")
    console = LCARSConsole()
    print(console.version)
    while True:
        line = input("LCARS> ")
        if line.lower() in ["exit", "terminate"]:
            break
        console.execute(line, print)
