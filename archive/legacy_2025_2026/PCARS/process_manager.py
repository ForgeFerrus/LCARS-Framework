# Process manager for PCARS.

import subprocess
from pathlib import Path
from typing import Optional


class ProcessManager:
    def __init__(self) -> None:
        self.Process: Optional[subprocess.Popen] = None

    def Start(self, command: list[str], cwd: Optional[Path] = None) -> None:
        self.Process = subprocess.Popen(
            command,
            cwd=str(cwd) if cwd is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def Stop(self) -> bool:
        if self.Process is not None and self.Process.poll() is None:
            self.Process.terminate()
            self.Process.wait(timeout=5)
            return True
        return False

    def IsRunning(self) -> bool:
        return self.Process is not None and self.Process.poll() is None
