# LCARS Framework :: Build System v1.0.0
# Єдина система побудови проєктів
# Автор: LCARS Development Team
# Ліцензія: MIT

__version__ = "1.0.0"
__author__ = "LCARS Development Team"
__license__ = "MIT"

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from lcars.base.version import getVersion

version = getVersion()
print(f"LCARS Build System v{version}")


class BuildResult:
    # Результат збірки
    def __init__(self):
        self.success = True
        self.logs: List[str] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.build_time = 0.0
        self.artifacts: List[str] = []

    def add_log(self, message: str):
        self.logs.append(message)

    def add_error(self, message: str):
        self.errors.append(message)
        self.success = False

    def add_warning(self, message: str):
        self.warnings.append(message)

    def add_artifact(self, path: str):
        self.artifacts.append(path)

    def get_summary(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'build_time': self.build_time,
            'total_logs': len(self.logs),
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'artifacts': self.artifacts
        }


class DependencyManager:
    # Менеджер залежностей
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.requirements_files = [
            'requirements.txt',
            'requirements-dev.txt',
            'pyproject.toml',
            'setup.py',
            'Pipfile'
        ]

    def install_dependencies(self, result: BuildResult) -> bool:
        # Встановити залежності
        result.add_log("Installing dependencies...")
        
        for req_file in self.requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                result.add_log(f"Found {req_file}")
                
                if req_file == 'requirements.txt' or req_file == 'requirements-dev.txt':
                    cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(req_path)]
                elif req_file == 'pyproject.toml':
                    cmd = [sys.executable, '-m', 'pip', 'install', '-e', '.']
                elif req_file == 'setup.py':
                    cmd = [sys.executable, 'setup.py', 'install']
                elif req_file == 'Pipfile':
                    cmd = ['pipenv', 'install']
                else:
                    continue
                
                success = self._run_command(cmd, result)
                if not success:
                    return False
        
        result.add_log("Dependencies installed successfully")
        return True

    def _run_command(self, cmd: List[str], result: BuildResult) -> bool:
        # Виконати команду
        try:
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if stdout:
                for line in stdout.strip().split('\n'):
                    result.add_log(line)
            
            if stderr:
                for line in stderr.strip().split('\n'):
                    if 'error' in line.lower() or 'failed' in line.lower():
                        result.add_error(line)
                    elif 'warning' in line.lower():
                        result.add_warning(line)
                    else:
                        result.add_log(line)
            
            return process.returncode == 0
        except Exception as e:
            result.add_error(f"Command failed: {e}")
            return False


class TestRunner:
    # Запуск тестів
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dirs = ['tests', 'test', 'testsuite']

    def run_tests(self, result: BuildResult) -> bool:
        # Запустити тести
        result.add_log("Running tests...")
        
        test_dir = self._find_test_directory()
        if not test_dir:
            result.add_warning("No test directory found")
            return True
        
        # Спробувати різні тестові фреймворки
        test_commands = [
            [sys.executable, '-m', 'pytest', str(test_dir), '-v'],
            [sys.executable, '-m', 'unittest', 'discover', str(test_dir)],
            [sys.executable, '-m', 'unittest', str(test_dir)]
        ]
        
        for cmd in test_commands:
            if self._command_exists(cmd[1]):
                success = self._run_command(cmd, result)
                if success:
                    result.add_log("Tests completed successfully")
                    return True
                else:
                    result.add_warning(f"Test command failed: {' '.join(cmd)}")
        
        result.add_warning("Could not run tests")
        return True

    def _find_test_directory(self) -> Optional[Path]:
        for test_dir in self.test_dirs:
            path = self.project_root / test_dir
            if path.exists() and path.is_dir():
                return path
        return None

    def _command_exists(self, cmd: str) -> bool:
        return shutil.which(cmd) is not None

    def _run_command(self, cmd: List[str], result: BuildResult) -> bool:
        try:
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if stdout:
                for line in stdout.strip().split('\n'):
                    if 'FAILED' in line or 'ERROR' in line:
                        result.add_error(line)
                    else:
                        result.add_log(line)
            
            if stderr:
                for line in stderr.strip().split('\n'):
                    result.add_error(line)
            
            return process.returncode == 0
        except Exception as e:
            result.add_error(f"Test command failed: {e}")
            return False


class Packager:
    # Пакування проєкту
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.build_dir = project_root / 'build'
        self.dist_dir = project_root / 'dist'

    def package_project(self, result: BuildResult) -> bool:
        # Запакувати проєкт
        result.add_log("Packaging project...")
        
        # Створити директорії
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
        # Спробувати PyInstaller
        spec_file = self.project_root / 'project.spec'
        if spec_file.exists():
            return self._package_with_pyinstaller(spec_file, result)
        
        # Спробувати стандартне пакування
        return self._package_standard(result)

    def _package_with_pyinstaller(self, spec_file: Path, result: BuildResult) -> bool:
        # Пакування з PyInstaller
        cmd = [sys.executable, '-m', 'PyInstaller', str(spec_file)]
        
        success = self._run_command(cmd, result)
        if success:
            # Знайти артефакти
            for item in self.dist_dir.iterdir():
                if item.is_file():
                    result.add_artifact(str(item))
                elif item.is_dir():
                    result.add_artifact(str(item))
        
        return success

    def _package_standard(self, result: BuildResult) -> bool:
        # Стандартне пакування
        # Створити zip архів вихідного коду
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"source_{timestamp}.zip"
        archive_path = self.dist_dir / archive_name
        
        success = self._create_source_archive(archive_path, result)
        if success:
            result.add_artifact(str(archive_path))
        
        return success

    def _create_source_archive(self, archive_path: Path, result: BuildResult) -> bool:
        # Створити архів вихідного коду
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in self.project_root.rglob('*'):
                    if file_path.is_file():
                        # Пропустити build та dist директорії
                        if 'build' in str(file_path) or 'dist' in str(file_path):
                            continue
                        
                        arcname = file_path.relative_to(self.project_root)
                        zf.write(file_path, arcname)
            
            result.add_log(f"Source archive created: {archive_path}")
            return True
        except Exception as e:
            result.add_error(f"Failed to create source archive: {e}")
            return False

    def _run_command(self, cmd: List[str], result: BuildResult) -> bool:
        try:
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if stdout:
                for line in stdout.strip().split('\n'):
                    result.add_log(line)
            
            if stderr:
                for line in stderr.strip().split('\n'):
                    if 'error' in line.lower():
                        result.add_error(line)
                    else:
                        result.add_log(line)
            
            return process.returncode == 0
        except Exception as e:
            result.add_error(f"Packaging command failed: {e}")
            return False


class Archiver:
    # Архіватор для створення бекапів та дистрибутивів
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.archive_dir = project_root / 'archives'

    def create_version_archive(self, version: str, result: BuildResult) -> str:
        # Створити архів з версією
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"lcars_v{version}_{timestamp}.zip"
        archive_path = self.archive_dir / archive_name
        
        result.add_log(f"Creating version archive: {archive_name}")
        
        success = self._create_full_archive(archive_path, result)
        if success:
            result.add_artifact(str(archive_path))
            return str(archive_path)
        
        return ""

    def create_backup_archive(self, result: BuildResult) -> str:
        # Створити бекап
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"backup_{timestamp}.zip"
        archive_path = self.archive_dir / archive_name
        
        result.add_log(f"Creating backup: {archive_name}")
        
        success = self._create_full_archive(archive_path, result)
        if success:
            result.add_artifact(str(archive_path))
            return str(archive_path)
        
        return ""

    def create_dist_archive(self, dist_dir: Path, version: str, result: BuildResult) -> str:
        # Створити архів дистрибутива
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"lcars_dist_v{version}_{timestamp}.zip"
        archive_path = self.archive_dir / archive_name
        
        result.add_log(f"Creating distribution archive: {archive_name}")
        
        success = self._create_dist_archive(dist_dir, archive_path, result)
        if success:
            result.add_artifact(str(archive_path))
            return str(archive_path)
        
        return ""

    def _create_full_archive(self, archive_path: Path, result: BuildResult) -> bool:
        # Створити повний архів проєкту
        try:
            self.archive_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in self.project_root.rglob('*'):
                    if file_path.is_file():
                        # Пропустити архіви та тимчасові файли
                        if (file_path.suffix in ['.zip', '.tar', '.gz'] or
                            'archives' in str(file_path) or
                            '__pycache__' in str(file_path) or
                            file_path.name.endswith('.pyc')):
                            continue
                        
                        arcname = file_path.relative_to(self.project_root)
                        zf.write(file_path, arcname)
            
            result.add_log(f"Archive created: {archive_path}")
            return True
        except Exception as e:
            result.add_error(f"Failed to create archive: {e}")
            return False

    def _create_dist_archive(self, dist_dir: Path, archive_path: Path, result: BuildResult) -> bool:
        # Створити архів дистрибутива
        try:
            self.archive_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in dist_dir.rglob('*'):
                    arcname = file_path.relative_to(dist_dir)
                    zf.write(file_path, arcname)
            
            result.add_log(f"Distribution archive created: {archive_path}")
            return True
        except Exception as e:
            result.add_error(f"Failed to create distribution archive: {e}")
            return False


class BuildManager:
    # Основний менеджер збірки
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.result = BuildResult()
        
        self.dependency_manager = DependencyManager(self.project_root)
        self.test_runner = TestRunner(self.project_root)
        self.packager = Packager(self.project_root)
        self.archiver = Archiver(self.project_root)

    def run_full_build(self, version: str = None) -> BuildResult:
        # Повна збірка проєкту
        start_time = datetime.now()
        
        self.result.add_log(f"Starting full build for: {self.project_root}")
        
        # 1. Встановити залежності
        if not self.dependency_manager.install_dependencies(self.result):
            self.result.add_error("Dependency installation failed")
            return self.result
        
        # 2. Запустити тести
        if not self.test_runner.run_tests(self.result):
            self.result.add_warning("Tests failed or not available")
        
        # 3. Запакувати проєкт
        if not self.packager.package_project(self.result):
            self.result.add_error("Packaging failed")
            return self.result
        
        # 4. Створити архів
        if version:
            archive_path = self.archiver.create_version_archive(version, self.result)
            if archive_path:
                self.result.add_log(f"Version archive: {archive_path}")
        else:
            archive_path = self.archiver.create_backup_archive(self.result)
            if archive_path:
                self.result.add_log(f"Backup archive: {archive_path}")
        
        # Обчислити час збірки
        end_time = datetime.now()
        self.result.build_time = (end_time - start_time).total_seconds()
        
        if self.result.success:
            self.result.add_log(f"Build completed successfully in {self.result.build_time:.2f}s")
        else:
            self.result.add_error(f"Build failed after {self.result.build_time:.2f}s")
        
        return self.result

    def run_quick_build(self) -> BuildResult:
        # Швидка збірка (без тестів)
        start_time = datetime.now()
        
        self.result.add_log(f"Starting quick build for: {self.project_root}")
        
        # 1. Запакувати проєкт
        if not self.packager.package_project(self.result):
            self.result.add_error("Packaging failed")
            return self.result
        
        # 2. Створити бекап
        archive_path = self.archiver.create_backup_archive(self.result)
        if archive_path:
            self.result.add_log(f"Backup archive: {archive_path}")
        
        # Обчислити час збірки
        end_time = datetime.now()
        self.result.build_time = (end_time - start_time).total_seconds()
        
        if self.result.success:
            self.result.add_log(f"Quick build completed in {self.result.build_time:.2f}s")
        else:
            self.result.add_error(f"Quick build failed after {self.result.build_time:.2f}s")
        
        return self.result

    def clean_build(self) -> BuildResult:
        # Очистка збірки
        self.result.add_log("Cleaning build directories...")
        
        # Видалити build та dist
        build_dir = self.project_root / 'build'
        dist_dir = self.project_root / 'dist'
        
        if build_dir.exists():
            shutil.rmtree(build_dir)
            self.result.add_log("Removed build directory")
        
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
            self.result.add_log("Removed dist directory")
        
        # Очистити __pycache__
        for cache_dir in self.project_root.rglob('__pycache__'):
            shutil.rmtree(cache_dir)
            self.result.add_log(f"Removed cache directory: {cache_dir}")
        
        self.result.add_log("Build cleanup completed")
        return self.result


# Швидкі функції
def build_project(project_root: str = None, version: str = None) -> BuildResult:
    manager = BuildManager(Path(project_root) if project_root else None)
    return manager.run_full_build(version)

def quick_build(project_root: str = None) -> BuildResult:
    manager = BuildManager(Path(project_root) if project_root else None)
    return manager.run_quick_build()

def clean_project(project_root: str = None) -> BuildResult:
    manager = BuildManager(Path(project_root) if project_root else None)
    return manager.clean_build()

def create_archive(project_root: str = None, version: str = "1.0") -> str:
    manager = BuildManager(Path(project_root) if project_root else None)
    result = BuildResult()
    return manager.archiver.create_version_archive(version, result)


# Константи
BUILD_STEPS = ['dependencies', 'tests', 'packaging', 'archiving']
SUPPORTED_FORMATS = ['zip', 'tar', 'gz']
DEFAULT_BUILD_DIR = 'build'
DEFAULT_DIST_DIR = 'dist'
DEFAULT_ARCHIVE_DIR = 'archives'
