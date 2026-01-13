"""
Geant4 Build System - Automated CMake/Make pipeline for LCARS Science Workstation
"""
import subprocess
import os
import threading
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

class BuildWorker(QObject):
    """Handles asynchronous build and run processes for Geant4 projects"""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)
    
    def __init__(self, project_path, action="build"):
        super().__init__()
        self.project_path = Path(project_path)
        self.action = action
        self.process = None

    def run(self):
        """Execute the build or run action"""
        if self.action == "build":
            self.build_project()
        elif self.action == "run":
            self.run_project()

    def build_project(self):
        """Standard Geant4 build: cmake .. && make"""
        build_dir = self.project_path / "build"
        if not build_dir.exists():
            build_dir.mkdir()
        
        self.output_signal.emit(f"◢ INITIALIZING BUILD IN {build_dir}")
        
        # 1. CMake Configuration
        cmd_cmake = ["cmake", ".."]
        if os.name == "nt": # Windows specific
             cmd_cmake = ["cmake", "..", "-G", "Visual Studio 17 2022"]
             
        success = self.execute_command(cmd_cmake, build_dir)
        if not success:
            self.finished_signal.emit(1)
            return

        # 2. Build Execution
        cmd_build = ["cmake", "--build", "."]
        success = self.execute_command(cmd_build, build_dir)
        
        self.finished_signal.emit(0 if success else 1)

    def run_project(self, executable_path=None):
        """Execute the Geant4 binary"""
        if not executable_path:
            # Attempt to find executable
            for exe in self.project_path.glob("build/**/*"):
                if exe.is_file() and os.access(exe, os.X_OK):
                    executable_path = exe
                    break
        
        if not executable_path or not executable_path.exists():
            self.output_signal.emit("◣ ERROR: EXECUTABLE NOT FOUND")
            self.finished_signal.emit(1)
            return

        self.output_signal.emit(f"◢ EXECUTING: {executable_path.name}")
        success = self.execute_command([str(executable_path)], self.project_path)
        self.finished_signal.emit(0 if success else 1)

    def execute_command(self, cmd, cwd):
        """Execute a shell command and pipe output to the UI"""
        try:
            self.process = subprocess.Popen(
                cmd, 
                cwd=cwd, 
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
            self.output_signal.emit(f"◣ PROCESS CRASHED: {str(e)}")
            return False

    def terminate(self):
        """Safely terminate the running process"""
        if self.process:
            self.process.terminate()
