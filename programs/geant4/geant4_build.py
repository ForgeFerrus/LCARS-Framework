"""
Geant4 Build System (tools copy)
"""
import subprocess
import os
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

class BuildWorker(QObject):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)

    def __init__(self, project_path, action="build"):
        super().__init__()
        self.project_path = Path(project_path)
        self.action = action
        self.process = None

    def run(self):
        if self.action == "build":
            self.build_project()
        elif self.action == "run":
            self.run_project()

    def build_project(self):
        build_dir = self.project_path / "build"
        if not build_dir.exists():
            build_dir.mkdir(parents=True, exist_ok=True)

        self.output_signal.emit(f"◢ INITIALIZING BUILD IN {build_dir}")
        cmd_cmake = ["cmake", ".."]
        if os.name == "nt":
            cmd_cmake = ["cmake", "..", "-G", "Visual Studio 17 2022"]

        success = self.execute_command(cmd_cmake, build_dir)
        if not success:
            self.finished_signal.emit(1)
            return

        cmd_build = ["cmake", "--build", "."]
        success = self.execute_command(cmd_build, build_dir)
        self.finished_signal.emit(0 if success else 1)

    def run_project(self, executable_path=None):
        if not executable_path:
            for exe in self.project_path.glob("build/**/*"):
                if exe.is_file() and os.access(exe, os.X_OK):
                    executable_path = exe
                    break

        if not executable_path or not Path(executable_path).exists():
            self.output_signal.emit("◣ ERROR: EXECUTABLE NOT FOUND")
            self.finished_signal.emit(1)
            return

        self.output_signal.emit(f"◢ EXECUTING: {Path(executable_path).name}")
        success = self.execute_command([str(executable_path)], self.project_path)
        self.finished_signal.emit(0 if success else 1)

    def execute_command(self, cmd, cwd):
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True
            )
            for line in self.process.stdout:
                self.output_signal.emit(line.strip())
            self.process.wait()
            return self.process.returncode == 0
        except Exception as e:
            self.output_signal.emit(f"◣ PROCESS CRASHED: {e}")
            return False

    def terminate(self):
        if self.process:
            try:
                self.process.terminate()
            except Exception as e:
                pass
