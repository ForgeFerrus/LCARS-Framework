# Process manager for lcars core operating system.

# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Optional


class ProcessManager:
    def __init__(self) -> None:
        self.current_process: Optional[subprocess.Popen] = None

    def start(self, command: list[str], cwd: Optional[Path] = None) -> Optional[subprocess.Popen]:
        self.current_process = subprocess.Popen(
            command,
            cwd=str(cwd) if cwd is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return self.current_process

    def stop(self) -> bool:
        if self.current_process is not None and self.current_process.poll() is None:
            self.current_process.terminate()
            self.current_process.wait(timeout=5)
            return True
        return False

    def is_running(self) -> bool:
        return self.current_process is not None and self.current_process.poll() is None
