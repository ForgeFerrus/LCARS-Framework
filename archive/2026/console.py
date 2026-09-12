"""
LCARS System Console - Neural Logic Interface.
Bridge between physical OS commands and Isolinear Core logic.
Supports cross-era command protocols and multi-faction intelligence arrays.
"""
import sys
import os
import subprocess
import threading
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import logging
logger = logging.getLogger(__name__)

class LCARSConsole:
    """Central processing unit for command-line interaction."""
    def __init__(self, board_computer=None):
        self.computer = board_computer
        self.active_era = "25th"
        self.active_faction = "federation"
        self._proc: Optional[subprocess.Popen] = None
        self.is_running = False

    def execute(self, text: str, output_callback: Callable[[str], None]):
        """Main entry point for command execution. Handles routing and threading."""
        text = text.strip()
        if not text:
            return

        # 1. Check for LCARS Core Commands
        if self.computer and text.lower().split()[0] in self.computer.system_commands:
            cmd_parts = text.lower().split()
            cmd = cmd_parts[0]
            # Simple param parsing: just first arg for now
            params = {"project_name": cmd_parts[1]} if len(cmd_parts) > 1 else {}
            
            result = self.computer.execute_command(cmd, params)
            output_callback(self._format_lcars_result(result))
            return

        # 2. OS Shell Execution (Asynchronous)
        self._run_async_shell(text, output_callback)

    def _run_async_shell(self, cmd: str, callback: Callable[[str], None]):
        """Executes shell commands in a background thread and streams output."""
        if self.is_running:
            callback("◤ ERROR: SYSTEM_BUSY -> PROCESS_IN_PROGRESS")
            return

        def target():
            self.is_running = True
            try:
                shell = "powershell" if os.name == 'nt' else "/bin/bash"
                flag = "-Command" if os.name == 'nt' else "-c"
                
                self._proc = subprocess.Popen(
                    [shell, flag, cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                for line in self._proc.stdout:
                    if line:
                        callback(line.strip())
                
                self._proc.wait()
            except Exception as e:
                logger.exception("Unhandled exception in %s", __file__)
                raise

                callback(f"◤ ERROR: SHELL_FATAL -> {str(e)}")
            finally:
                self.is_running = False
                self._proc = None

        threading.Thread(target=target, daemon=True).start()

    def _format_lcars_result(self, data: Dict[str, Any]) -> str:
        """Formats BoardComputer output into LCARS-standard telemetry."""
        status = data.get("status", "UNKNOWN")
        cmd = data.get("command", "NONE")
        res = data.get("result", "")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        header = f"◤ [{timestamp}] LCARS_CMD::{cmd.upper()} -> STATUS::{status.upper()}"
        
        if isinstance(res, dict):
            body = "\n".join([f"  {k.upper()}: {v}" for k, v in res.items()])
        else:
            body = f"  DATA: {res}"
            
        return f"{header}\n{body}"

if __name__ == "__main__":
    # Internal boot for standalone console mode
    print("◤ NEURAL CONSOLE INITIALIZED")
    print("◤ SYSTEM CORE LINKED | LCARS 25th | FACTION: UFP")
    
    console = LCARSConsole()
    while True:
        try:
            line = input("LCARS> ")
            if line.lower() in ["exit", "terminate"]: break
            print(console.process_input(line))
        except KeyboardInterrupt:
            break
