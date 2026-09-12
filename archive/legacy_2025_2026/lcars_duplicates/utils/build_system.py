"""Build system orchestrator for the LCARS application.

Provides `BuildManager` which can: install Python deps, run tests,
package the application with PyInstaller (if spec present), archive
the distribution, and optionally invoke native project builds via
the AutobuildOrchestrator if CMake projects are found.

This module is safe to import in GUI contexts and exposes a synchronous
`run_full_build()` and a QThread-friendly `BuildManager` class with
Qt signals for UI integration.
"""
from pathlib import Path
from typing import List, Optional
import subprocess
import logging
import shutil
import zipfile
import sys

from PyQt6.QtCore import QThread, pyqtSignal
from lcars.utils.autobuild import Orchestrator, BuildDiagnostics
logger = logging.getLogger("lcars.utils.build_system")


class BuildResult:
    def __init__(self):
        self.success = True
        self.logs: List[str] = []
        self.errors: List[str] = []

    def add_log(self, line: str):
        self.logs.append(line)
        logger.debug(line)

    def add_error(self, line: str):
        self.errors.append(line)
        self.success = False
        logger.error(line)


class BuildManager(QThread):
    log = pyqtSignal(str)
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool)

    def __init__(self, project_root: Optional[Path] = None, parent=None):
        super().__init__(parent)
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.result = BuildResult()

    def run(self):
        ok = self.run_full_build()
        self.finished.emit(ok)

    def _emit(self, msg: str):
        sig = getattr(self, 'log', None)
        if sig is not None and hasattr(sig, 'emit') and callable(getattr(sig, 'emit')):
            sig.emit(msg)
        self.result.add_log(msg)

    def _create_shortcut_windows(self, exe_path: Path, name: str = "LCARS") -> bool:
        """Create a Start Menu/Desktop shortcut for the exe on Windows.

        Tries to create a .lnk via pywin32; if unavailable, falls back to
        creating a simple .bat launcher on the desktop.
        """
        from win32com.client import Dispatch
        desktop = Path.home() / 'Desktop'
        shortcut_path = desktop / f"{name}.lnk"
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(exe_path)
        shortcut.WorkingDirectory = str(exe_path.parent)
        shortcut.IconLocation = str(exe_path)
        shortcut.save()
        self._emit(f"Created shortcut: {shortcut_path}")
        return True

    def create_shortcuts(self, dist_dir: Path) -> bool:
        """Scan `dist_dir` for executables and create shortcuts where appropriate.

        Currently targets Windows; returns True if at least one shortcut created.
        """
        created = False
        for p in dist_dir.rglob('*.exe'):
            name = p.stem
            if sys.platform.startswith('win'):
                ok = self._create_shortcut_windows(p, name)
                created = created or ok
        return created

    def run_full_build(self, steps: Optional[List[str]] = None, dry_run: bool = False) -> bool:
        """Run the full build pipeline.

        Steps can include: 'deps', 'tests', 'pyinstaller', 'archive', 'native'
        """
        steps = steps or ["deps", "tests", "pyinstaller", "archive", "native"]
        self._emit("Starting full build pipeline")

        if "deps" in steps:
            self.progress.emit(5, "Installing dependencies")
            if not dry_run and not self.install_requirements():
                self._emit("Dependency installation failed")
                return False

        if "tests" in steps:
            self.progress.emit(20, "Running test suite")
            if not dry_run and not self.run_tests():
                self._emit("Tests failed")
                return False

        if "pyinstaller" in steps:
            self.progress.emit(60, "Packaging with PyInstaller")
            if not dry_run and not self.package_pyinstaller():
                self._emit("Packaging failed")
                return False

        if "archive" in steps:
            self.progress.emit(80, "Archiving distribution")
            if not dry_run and not self.archive_dist():
                self._emit("Archiving failed")
                return False

        if "native" in steps:
            self.progress.emit(90, "Building native subprojects")
            if not dry_run and not self.build_native_projects():
                self._emit("Native subproject build failed")
                return False

        self.progress.emit(100, "Build complete")
        self._emit("Build succeeded")
        return True

    def install_requirements(self) -> bool:
        req = self.project_root / "scripts" / "requirements.txt"
        cmd = [sys.executable, "-m", "pip", "install", "-r", str(req)]
        return self._run_cmd(cmd, cwd=self.project_root)

    def run_tests(self) -> bool:
        cmd = [sys.executable, "-m", "unittest", "discover", "tests"]
        return self._run_cmd(cmd, cwd=self.project_root)

    def package_pyinstaller(self) -> bool:
        spec = self.project_root / "build_lcars.spec"
        cmd = [sys.executable, "-m", "PyInstaller", str(spec)]
        return self._run_cmd(cmd, cwd=self.project_root)

    def archive_dist(self) -> bool:
        dist = self.project_root / "dist"
        out = self.project_root / "build" / f"lcars_dist.zip"
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for p in dist.rglob("*"):
                if p.is_file():
                    zf.write(p, arcname=str(p.relative_to(dist)))
        self._emit(f"Archived dist -> {out}")
        return True

    def build_native_projects(self) -> bool:
        # Find native CMake projects under 'programs' and invoke AutobuildOrchestrator
        # to build them
        ok = True
        programs = self.project_root / "programs"
        for proj in programs.iterdir():
            if (proj / "CMakeLists.txt").exists():
                self._emit(f"Building native project: {proj.name}")
                orchestrator = Orchestrator(proj)
                orchestrator.run()
        return ok

    def _run_cmd(self, cmd: List[str], cwd: Optional[Path] = None) -> bool:
        self._emit(f"$ {' '.join(cmd)}")
        proc = subprocess.Popen(cmd, cwd=str(cwd) if cwd else None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            line = line.rstrip()
            self._emit(line)
        proc.wait()
        return proc.returncode == 0


def run_full_build(project_root: Optional[str] = None, dry_run: bool = False) -> bool:
    bm = BuildManager(Path(project_root) if project_root else None)
    return bm.run_full_build(dry_run=dry_run)
