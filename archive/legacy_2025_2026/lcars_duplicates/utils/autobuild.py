"""
Autobuild utility — relocated build orchestrator implementation.

Provides `Orchestrator` and `BuildDiagnostics` dataclass. This
module is intended as a utilities implementation; use the `lcars.core`
shim for backwards compatibility if other modules import the old path.
"""
import subprocess
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import logging

logger = logging.getLogger("lcars.utils.autobuild")


@dataclass
class BuildDiagnostics:
    """Diagnostic information from build process"""
    success: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    build_time: float = 0.0


class Orchestrator(QThread):
    """
    Intelligent build system that:
    - Auto-detects CMake projects
    - Validates dependencies
    - Builds with optimal settings
    - Diagnoses errors with simple heuristics
    """
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, str)  # percentage, status
    finished_signal = pyqtSignal(BuildDiagnostics)

    def __init__(self, project_path: Path):
        super().__init__()
        self.project_path = Path(project_path)
        self.process = None
        self.diagnostics = BuildDiagnostics(success=False, errors=[], warnings=[], suggestions=[])

    def run(self):
        """Main autonomous build pipeline"""
        self.log_signal.emit("═══ AUTONOMOUS BUILD SYSTEM INITIATED ═══")

        if not self.check_environment():
            self.finished_signal.emit(self.diagnostics)
            return

        cmake_file = self.find_cmake_file()
        if not cmake_file:
            self.diagnostics.errors.append("No CMakeLists.txt found")
            self.diagnostics.suggestions.append("Create CMakeLists.txt in project root")
            self.finished_signal.emit(self.diagnostics)
            return

        build_dir = self.setup_build_directory()

        if not self.configure_cmake(build_dir):
            self.analyze_cmake_errors()
            self.finished_signal.emit(self.diagnostics)
            return

        if not self.compile_project(build_dir):
            self.analyze_build_errors()
            self.finished_signal.emit(self.diagnostics)
            return

        self.diagnostics.success = True
        self.log_signal.emit("═══ BUILD COMPLETED SUCCESSFULLY ═══")
        self.finished_signal.emit(self.diagnostics)

    def check_environment(self) -> bool:
        self.progress_signal.emit(10, "Checking environment")
        required_tools = {"cmake": "CMake build system", "git": "Version control"}
        missing = []
        for tool, description in required_tools.items():
            if not self.is_tool_available(tool):
                missing.append(f"{tool} ({description})")
        if missing:
            self.diagnostics.errors.append(f"Missing tools: {', '.join(missing)}")
            self.diagnostics.suggestions.append("Install missing tools via package manager")
            self.log_signal.emit(f"◣ ERROR: Missing required tools")
            return False
        self.log_signal.emit("✓ Environment check passed")
        return True

    def is_tool_available(self, tool: str) -> bool:
        if tool == "cmake":
            subprocess.run([tool, "--version"], capture_output=True, timeout=5)
            return True
        if tool == "git":
            subprocess.run([tool, "--version"], capture_output=True, timeout=5)
            return True
        if (subprocess.SubprocessError, FileNotFoundError):
            return False

    def find_cmake_file(self) -> Optional[Path]:
        self.progress_signal.emit(20, "Analyzing project structure")
        cmake_file = self.project_path / "CMakeLists.txt"
        if cmake_file.exists():
            self.log_signal.emit(f"✓ Found CMakeLists.txt")
            return cmake_file
        for cmake in self.project_path.rglob("CMakeLists.txt"):
            self.log_signal.emit(f"✓ Found CMakeLists.txt in {cmake.parent.name}")
            return cmake
        return None

    def setup_build_directory(self) -> Path:
        self.progress_signal.emit(30, "Setting up build directory")
        build_dir = self.project_path / "build"
        build_dir.mkdir(exist_ok=True)
        self.log_signal.emit(f"✓ Build directory: {build_dir}")
        return build_dir

    def configure_cmake(self, build_dir: Path) -> bool:
        self.progress_signal.emit(40, "Configuring CMake")
        cmd = ["cmake", ".."]
        if os.name == "nt":
            cmd.extend(["-G", "Visual Studio 17 2022"])
        self.log_signal.emit(f"◢ Running: {' '.join(cmd)}")
        return self.execute_command(cmd, build_dir)

    def compile_project(self, build_dir: Path) -> bool:
        self.progress_signal.emit(60, "Compiling project")
        cmd = ["cmake", "--build", ".", "--config", "Release"]
        self.log_signal.emit(f"◢ Building in Release mode")
        return self.execute_command(cmd, build_dir)

    def execute_command(self, cmd: List[str], cwd: Path) -> bool:
        try:
            self.process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=False)
            if self.process.stdout:
                for line in self.process.stdout:
                    line = line.strip()
                    if line:
                        self.log_signal.emit(line)
                        if "error" in line.lower():
                            self.diagnostics.errors.append(line)
                        elif "warning" in line.lower():
                            self.diagnostics.warnings.append(line)
            self.process.wait()
            return self.process.returncode == 0
        except Exception as e:
            self.diagnostics.errors.append(str(e))
            self.log_signal.emit(f"◣ EXCEPTION: {str(e)}")
            return False

    def analyze_cmake_errors(self):
        if not self.diagnostics.errors:
            return
        for error in self.diagnostics.errors:
            if "Could not find" in error:
                package = re.search(r"Could not find (\w+)", error)
                if package:
                    self.diagnostics.suggestions.append(f"Install {package.group(1)} library")
            elif "CMAKE_CXX_COMPILER" in error:
                self.diagnostics.suggestions.append("Install C++ compiler (MSVC, GCC, or Clang)")

    def analyze_build_errors(self):
        if not self.diagnostics.errors:
            return
        for error in self.diagnostics.errors:
            if "undefined reference" in error.lower():
                self.diagnostics.suggestions.append("Check library linking in CMakeLists.txt")
            elif "no such file" in error.lower():
                self.diagnostics.suggestions.append("Verify include paths and file locations")

    def terminate(self):
        if self.process:
            self.process.terminate()
            self.log_signal.emit("◣ BUILD TERMINATED BY USER")
